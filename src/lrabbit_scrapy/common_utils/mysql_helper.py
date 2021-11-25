import time
import traceback
import pymysql.cursors
import pymysql
import queue
import threading
import logging
from lrabbit_scrapy.common_utils.config_helper import get_mysql_config, get_config_path


class MysqlClient(object):

    def __init__(self, database=None, config_path_env=None, env='test'):
        config_path = get_config_path(config_path_env)
        mysql_config = get_mysql_config(config_path, env)
        host = mysql_config.MYSQL_HOST
        if not database:
            database = mysql_config.MYSQL_DATABASE
        user = mysql_config.MYSQL_USER
        password = mysql_config.MYSQL_PASSWORD
        port = mysql_config.MYSQL_PORT
        max_idle_time = 7 * 3600
        connect_timeout = 10
        time_zone = "+0:00"
        charset = "utf8mb4"
        sql_mode = "TRADITIONAL"
        self.host = host
        self.database = database
        self.max_idle_time = float(max_idle_time)
        args = dict(use_unicode=True, charset=charset,
                    database=database,
                    init_command=('SET time_zone = "%s"' % time_zone),
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=connect_timeout, sql_mode=sql_mode)
        if user is not None:
            args["user"] = user
        if password is not None:
            args["passwd"] = password
        # We accept a path to a MySQL socket file or a host(:port) string
        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = 3306
        if port:
            args['port'] = port

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except Exception:
            logging.error("Cannot connect to MySQL on %s", self.host,
                          exc_info=True)

    def _ensure_connected(self):
        if (self._db is None or
                (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def __del__(self):
        self.close()

    def close(self):
        """Closes this database connection."""
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = pymysql.connect(**self._db_args)
        self._db.autocommit(True)

    def query(self, query, *parameters, **kwparameters):
        """Returns a row list for the given query and parameters."""
        cursor = self._cursor()
        try:
            cursor.execute(query, kwparameters or parameters)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def get(self, query, *parameters, **kwparameters):
        """Returns the (singular) row returned by the given query.
        """
        cursor = self._cursor()
        try:
            cursor.execute(query, kwparameters or parameters)
            return cursor.fetchone()
        finally:
            cursor.close()

    def execute(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the lastrowid from the query."""
        cursor = self._cursor()
        try:
            cursor.execute(query, kwparameters or parameters)
            return cursor.lastrowid
        except Exception as e:
            if e.args[0] == 1062:
                pass
            else:
                traceback.print_exc()
                raise e
        finally:
            cursor.close()

    insert = execute

    ## =============== high level method for table ===================

    def table_has(self, table_name, field, value):
        if isinstance(value, str):
            value = value.encode('utf8')
        sql = 'SELECT %s FROM %s WHERE %s="%s"' % (
            field,
            table_name,
            field,
            value)
        d = self.get(sql)
        return d

    def table_insert(self, table_name, item):
        '''item is a dict : key is mysql table field'''
        fields = list(item.keys())
        values = list(item.values())
        fieldstr = ','.join(fields)
        valstr = ','.join(['%s'] * len(item))
        for i in range(len(values)):
            if isinstance(values[i], str):
                values[i] = values[i].encode('utf8')
        sql = 'INSERT INTO %s (%s) VALUES(%s)' % (table_name, fieldstr, valstr)
        try:
            last_id = self.execute(sql, *values)
            return last_id
        except Exception as e:
            if e.args[0] == 1062:
                # just skip duplicated item
                pass
            else:
                traceback.print_exc()
                print('sql:', sql)
                print('item:')
                for i in range(len(fields)):
                    vs = str(values[i])
                    if len(vs) > 300:
                        print(fields[i], ' : ', len(vs), type(values[i]))
                    else:
                        print(fields[i], ' : ', vs, type(values[i]))
                raise e

    def table_update(self, table_name, updates,
                     field_where, value_where):
        '''updates is a dict of {field_update:value_update}'''
        upsets = []
        values = []
        for k, v in updates.items():
            s = '%s=%%s' % k
            upsets.append(s)
            values.append(v)
        upsets = ','.join(upsets)
        sql = 'UPDATE %s SET %s WHERE %s="%s"' % (
            table_name,
            upsets,
            field_where, value_where,
        )
        self.execute(sql, *(values))


logger = logging.Logger(name="mysql connect")


class Connection(pymysql.connections.Connection):
    _pool = None
    _reusable_expection = (pymysql.err.ProgrammingError, pymysql.err.IntegrityError, pymysql.err.NotSupportedError)

    def __init__(self, *args, **kwargs):
        pymysql.connections.Connection.__init__(self, *args, **kwargs)
        self.args = args
        self.kwargs = kwargs

    def __exit__(self, exc, value, traceback):

        pymysql.connections.Connection.__exit__(self, exc, value, traceback)
        if self._pool:
            if not exc or exc in self._reusable_expection:
                '''reusable connection'''
                self._pool.put_connection(self)
            else:
                '''no reusable connection, close it and create a new one then put it to the pool'''
                self._pool.put_connection(self._recreate(*self.args, **self.kwargs))
                self._pool = None
                try:
                    self.close()
                    logger.warning("Close not reusable connection from pool(%s) caused by %s", self._pool.name, value)
                except Exception:
                    pass

    def _recreate(self, *args, **kwargs):
        conn = Connection(*args, **kwargs)
        logger.debug('Create new connection due to pool(%s) lacking', self._pool.name)
        return conn

    def close(self):

        if self._pool:
            self._pool.put_connection(self)
        else:
            pymysql.connections.Connection.close(self)

    def execute_query(self, query, args=(), dictcursor=False, return_one=False, exec_many=False):

        with self:
            cur = self.cursor() if not dictcursor else self.cursor(pymysql.cursors.DictCursor)
            try:
                if exec_many:
                    cur.executemany(query, args)
                else:
                    cur.execute(query, args)
            except Exception:
                raise
            # if no record match the query, return () if return_one==False, else return None
            return cur.fetchone() if return_one else cur.fetchall()


class ConnectionPool:
    _HARD_LIMIT = 200
    _THREAD_LOCAL = threading.local()
    _THREAD_LOCAL.retry_counter = 0  # a counter used for debug get_connection() method

    def __init__(self, size=10, name=None, *args, **kwargs):
        self._pool = queue.Queue(self._HARD_LIMIT)
        self._size = size if 0 < size < self._HARD_LIMIT else self._HARD_LIMIT
        self.name = name if name else '-'.join(
            [kwargs.get('host', 'localhost'), str(kwargs.get('port', 3306)),
             kwargs.get('user', ''), kwargs.get('database', '')])
        for _ in range(self._size):
            conn = Connection(*args, **kwargs)
            conn._pool = self
            self._pool.put(conn)

    def get_connection(self, timeout=1, retry_num=1) -> Connection:
        """
        timeout: timeout of get a connection from pool, should be a int(0 means return or raise immediately)
        retry_num: how many times will retry to get a connection
        """
        try:
            conn = self._pool.get(timeout=timeout) if timeout > 0 else self._pool.get_nowait()
            logger.debug('Get connection from pool(%s)', self.name)
            return conn
        except queue.Empty:
            if not hasattr(self._THREAD_LOCAL, 'retry_counter'):
                self._THREAD_LOCAL.retry_counter = 0
            if retry_num > 0:
                self._THREAD_LOCAL.retry_counter += 1
                logger.debug('Retry get connection from pool(%s), the %d times', self.name,
                             self._THREAD_LOCAL.retry_counter)
                retry_num -= 1
                return self.get_connection(timeout, retry_num)
            else:
                total_times = self._THREAD_LOCAL.retry_counter + 1
                self._THREAD_LOCAL.retry_counter = 0
                raise GetConnectionFromPoolError("can't get connection from pool({}) within {}*{} second(s)".format(
                    self.name, timeout, total_times))

    def put_connection(self, conn):
        if not conn._pool:
            conn._pool = self
        conn.cursor().close()
        try:
            self._pool.put_nowait(conn)
            logger.debug("Put connection back to pool(%s)", self.name)
        except queue.Full:
            logger.warning("Put connection to pool(%s) error, pool is full, size:%d", self.name, self.size())

    def size(self):
        return self._pool.qsize()


class GetConnectionFromPoolError(Exception):
    """Exception related can't get connection from pool within timeout seconds."""


class MysqlConnectionPool:

    def __init__(self, database=None, config_path_env=None, env='test'):
        config_path = get_config_path(config_path_env)
        mysql_config = get_mysql_config(config_path, env)
        host = mysql_config.MYSQL_HOST
        if not database:
            database = mysql_config.MYSQL_DATABASE
        user = mysql_config.MYSQL_USER
        password = mysql_config.MYSQL_PASSWORD
        port = mysql_config.MYSQL_PORT
        max_idle_time = 7 * 3600
        connect_timeout = 10
        time_zone = "+0:00"
        charset = "utf8mb4"
        sql_mode = "TRADITIONAL"
        self.host = host
        self.database = database
        self.max_idle_time = float(max_idle_time)
        args = dict(use_unicode=True, charset=charset,
                    database=database,
                    init_command=('SET time_zone = "%s"' % time_zone),
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=connect_timeout, sql_mode=sql_mode)
        if user is not None:
            args["user"] = user
        if password is not None:
            args["passwd"] = password
        # We accept a path to a MySQL socket file or a host(:port) string
        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = 3306
        if port:
            args['port'] = port
        self._args = args
        self.pool = ConnectionPool(size=10, **self._args)

    def execute_query(self, sql):
        conn = self.pool.get_connection()
        with conn:
            res = conn.execute_query(sql)
            return res


if __name__ == '__main__':
    pass
