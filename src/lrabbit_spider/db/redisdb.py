

import lrabbit_spider.setting as setting
from redis.connection import Encoder as _Encoder
from redis.exceptions import ConnectionError, TimeoutError
from redis.exceptions import DataError
from redis.sentinel import Sentinel
from rediscluster import RedisCluster
from redis._compat import unicode,long,basestring

from lrabbit_spider.utils.log import log


import redis
class Encoder(_Encoder):
    def encode(self, value):
        "Return a bytestring or bytes-like representation of the value"
        if isinstance(value, (bytes, memoryview)):
            return value
        # elif isinstance(value, bool):
        #     # special case bool since it is a subclass of int
        #     raise DataError(
        #         "Invalid input of type: 'bool'. Convert to a "
        #         "bytes, string, int or float first."
        #     )
        elif isinstance(value, float):
            value = repr(value).encode()
        elif isinstance(value, (int, long)):
            # python 2 repr() on longs is '123L', so use str() instead
            value = str(value).encode()
        elif isinstance(value, (list, dict, tuple)):
            value = unicode(value)
        elif not isinstance(value, basestring):
            # a value we don't know how to deal with. throw an error
            typename = type(value).__name__
            raise DataError(
                "Invalid input of type: '%s'. Convert to a "
                "bytes, string, int or float first." % typename
            )
        if isinstance(value, unicode):
            value = value.encode(self.encoding, self.encoding_errors)
        return value


redis.connection.Encoder = Encoder
class RedisDB:
    def __init__(
        self,
        ip_ports=None,
        db=None,
        user_pass=None,
        url=None,
        decode_responses=True,
        service_name=None,
        max_connections=32,
        **kwargs,
    ):
        """
        redis的封装
        Args:
            ip_ports: ip:port 多个可写为列表或者逗号隔开 如 ip1:port1,ip2:port2 或 ["ip1:port1", "ip2:port2"]
            db:
            user_pass:
            url:
            decode_responses:
            service_name: 适用于redis哨兵模式
        """

        # 可能会改setting中的值，所以此处不能直接赋值为默认值，需要后加载赋值
        if ip_ports is None:
            ip_ports = setting.REDISDB_IP_PORTS
        if db is None:
            db = setting.REDISDB_DB
        if user_pass is None:
            user_pass = setting.REDISDB_USER_PASS
        if service_name is None:
            service_name = setting.REDISDB_SERVICE_NAME

        self._is_redis_cluster = False

        self.__redis = None
        self._url = url
        self._ip_ports = ip_ports
        self._db = db
        self._user_pass = user_pass
        self._decode_responses = decode_responses
        self._service_name = service_name
        self._max_connections = max_connections
        self._kwargs = kwargs
        self.get_connect()

    def get_connect(self):
        pass
    def __repr__(self):
        pass

    @property
    def _redis(self):
        pass
    @_redis.setter
    def _redis(self,val):
        pass


    @classmethod
    def from_url(cls,url):
        pass

    def sadd(self,table,values):
        pass

    def sget(self,table,count=1,is_pop=True):
        pass

    def srem(self,table,values):
        pass
    def sget_count(self,tables):
        pass

    def sdelete(slef,table):
        pass

    def sismember(self,table,key):
        pass

    def zadd(self,table,values,priority=0):
        pass
    def zget(self,table,count=1,is_pop=True):
        pass
    def zremrangebyscore(self,table,priority_min,priority_max):
        pass
    def zrangebysocre(selt,tale,priority_min,priority_mmax,count=None,is_pop=True):
        pass
    def zrangebyscore_increase_socre(self,table,priority_min,priority_max,icrease_score,count=None):
        pass
    def zrangebyscore_set_score(selfmtable,priority_min,priority_max,score,count=None):
        pass
    def zincrby(self,table,amount,value):
        pass

    def zget_count(self,table,priority_min=None,prioirty_max=None):
        pass

    def zrem(self,table,values):
        pass

    def zexiste(self,table,values):
        pass
    def lpush(self,table,values):
        pass

    def lpop(self,table,count=1):
        pass
    def rpoplpush(self,from_table,to_table=None):
        pass

    def lget_count(self,table):
        pass

    def lrem(self,table,value,num=0):
        pass
    def lrange(self,table,start=0,end=-1):
        pass

    def hset(self,table,value):
        pass

    def hset_batch(self,table,datas):
        pass

    def hincry(self,table,key,increment):
        pass

    def hget(self,table,key,is_pop=False):
        pass

    def hgetall(selfmtable):
        pss

    def hexistes(sefl,table,key):
        pass

    def hdel(self,table,*keys):
        pass

    def hget_count(self,table):
        pass

    def hkeys(self,table):
        pass

    def setbit(self,table,offset,values):
        pass

    def getbit(self,table,offsets):
        pass

    def bitcount(self,table):
        pass

    def strset(self,table,values,**kwargs):
        pass

    def str_incrby(self,table,values):
        pass

    def strget(self,table):
        pass

    def strlen(sefl,table):
        pass

    def getkeys(self,regex):
        pass

    def set_expire(self,key,seconds):
        pass

    def get_expire(self,key):
        pass

    def clear(sefl,table):
        pass

    def get_redis_obj(slef):
        pass

    def _reconenct(self):
        pass

    def __getattr__(self,name):
        pass

    

    





