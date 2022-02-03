import logging
from logging.handlers import BaseRotatingHandler
import os
import sys
import lrabbit_spider.setting as setting
from better_exceptions import format_exception
import loguru

LOG_FORMAT = "%(threadName)s|%(asctime)s|%(filename)s|%(funcName)s|line:%(lineno)d|%(levelname)s| %(message)s"

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Retrieve context where the logging call occurred, this happens to be in the 6th frame upward
        logger_opt = loguru.logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

class RotatingFileHandler(BaseRotatingHandler):
    def __init__(
        self, filename, mode="a", max_bytes=0, backup_count=0, encoding=None, delay=0
    ):
        BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.placeholder = str(len(str(backup_count)))

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backup_count > 0:
            for i in range(self.backup_count - 1, 0, -1):
                sfn = ("%0" + self.placeholder + "d.") % i  # '%2d.'%i -> 02
                sfn = sfn.join(self.baseFilename.split("."))
                # sfn = "%d_%s" % (i, self.baseFilename)
                # dfn = "%d_%s" % (i + 1, self.baseFilename)
                dfn = ("%0" + self.placeholder + "d.") % (i + 1)
                dfn = dfn.join(self.baseFilename.split("."))
                if os.path.exists(sfn):
                    # print "%s -> %s" % (sfn, dfn)
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = (("%0" + self.placeholder + "d.") % 1).join(
                self.baseFilename.split(".")
            )
            if os.path.exists(dfn):
                os.remove(dfn)
            # Issue 18940: A file may not have been created if delay is True.
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record):

        if self.stream is None:  # delay was set...
            self.stream = self._open()
        if self.max_bytes > 0:  # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.max_bytes:
                return 1
        return 0            


def get_logger(

    name=None,
    path=None,
    log_level=None,
    is_write_to_console=None,
    is_write_to_file=None,
    color=None,
    mode=None,
    max_bytes=None,
    backup_count=None,
    encoding=None,
    is_print_default_exception=True
    
):
    name = name or  setting.LOG_NAME
    path = path or setting.LOG_PATH
    log_level = log_level or setting.LOG_LEVEL
    is_write_to_console = (is_write_to_console 
        if is_write_to_console is not None
        else setting.LOG_IS_WRITE_TO_CONSOLE
    )
    color = color if color is not None else setting.LOG_COLOR
    mode = mode or setting.LOG_MODE
    max_bytes = max_bytes or setting.LOG_MAX_BYTES
    backup_count = backup_count or setting.LOG_BACKUP_COUNT
    encoding = encoding or setting.LOG_ENCODING
    

    name = name.split(os.sep)[-1].split(".")[0]

    logger = logging.getLogger()
    logger.setLevel(log_level)
    formatter = logging.Formatter(LOG_FORMAT)
    if is_print_default_exception:
        formatter.formatException = lambda exce_info : format_exception(*exce_info)
    
    if is_write_to_console:
        if path and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        
        rf_handler = RotatingFileHandler(
            path,
            mode=mode,
            max_bytes=max_bytes,
            backup_count = backup_count,
            encoding = encoding
        )
        rf_handler.setFormatter(formatter)
        logger.addHandler(rf_handler)
    if color and is_write_to_console:
        loguru_handler =  InterceptHandler()
        loguru_handler.setFormatter(formatter)
        logger.addHandler(loguru_handler)
    elif is_write_to_console:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.stream=sys.stdout
        logger.addHandler(stream_handler)
    
    _handler_list = []
    _handler_name_list = []
    for _handler in logger.handlers:
        if str(_handler) not in _handler_name_list:
            _handler_name_list.append(str(_handler.name))
            _handler_list.append(_handler)
    logger.handlers = _handler_list

    return logger


STOP_LOGS = [
    # ES
    "urllib3.response",
    "urllib3.connection",
    "elasticsearch.trace",
    "requests.packages.urllib3.util",
    "requests.packages.urllib3.util.retry",
    "urllib3.util",
    "requests.packages.urllib3.response",
    "requests.packages.urllib3.contrib.pyopenssl",
    "requests.packages",
    "urllib3.util.retry",
    "requests.packages.urllib3.contrib",
    "requests.packages.urllib3.connectionpool",
    "requests.packages.urllib3.poolmanager",
    "urllib3.connectionpool",
    "requests.packages.urllib3.connection",
    "elasticsearch",
    "log_request_fail",
    # requests
    "requests",
    "selenium.webdriver.remote.remote_connection",
    "selenium.webdriver.remote",
    "selenium.webdriver",
    "selenium",
    # markdown
    "MARKDOWN",
    "build_extension",
    # newspaper
    "calculate_area",
    "largest_image_url",
    "newspaper.images",
    "newspaper",
    "Importing",
    "PIL",
]


for STOP_LOG in STOP_LOGS:
    log_level = eval("logging."+setting.OTHERS_LOG_LEVAL)
    logging.getLogger(STOP_LOG).setLevel(log_level)
        


class Log:
    log = None

    def __getattr__(self,name):
        if self.__class__.log is None:
            self.__class__.log = get_logger()
        return getattr(self.__class__.log,name)
    @property
    def debug(self):
        return self.__class__.log.debug
        pass
    
    @property
    def info(self):
        return self.__class__.log.info
        pass
        
    @property
    def warning(self):
        return self.__class__.log.warning
        pass
    
    @property
    def exception(self):
        return self.__class__.log.exception
        pass
    
    @property
    def error(self):
        return self.__class__.log.error
        pass
    @property
    def critical(self):
        return self.__class__.log.critical
        pass





log = Log() 