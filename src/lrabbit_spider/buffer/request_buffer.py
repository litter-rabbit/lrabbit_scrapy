



from threading import Thread
from lrabbit_spider.utils.log import log
import lrabbit_spider.utils.tools as tools
import collections
import lrabbit_spider.setting as setting
from lrabbit_spider.network.request import Request
from lrabbit_spider.deque import Dedup
import  lrabbit_spider.constants as constants
from lrabbit_spider.db.redisdb import RedisDB


MAX_URL_COUNT=1000
class RequestsBuffer(Thread):
    dedup : Dedup= None

    def __init__(self,redis_key):
        if not hasattr(self,"_request_deque"):

            super(RequestsBuffer,self).__init__()
            self._thread_stop=False
            self._is_adding_to_db = False
            self._requests_deque = collections.deque()
            self._del_requests_deque = collections.deque()
            self._db = RedisDB()
            self._table_request = setting.TAB_REQUSETS.format(redis_key=redis_key)
            self.table_failed_request =setting.TAB_FAILED_REQUSETS
            if not self.__class__.dedup and setting.REQUEST_FILTER_ENABLE:
                self.__class__.dedup = Dedup(name=redis_key,to_md5=False,**setting.REQUEST_FILTER_SETTING)


    def run(self):
        self._thread_stop = False
        while not self._thread_stop:
            try:
                self.__add_request_to_db()
            except Exception as e:
                log.exception(e)
            tools.delay_time(1)

    def put_request(self,request):
        self._requests_deque.append(request)
        if self.get_requests_count() > MAX_URL_COUNT:
            self.flush()
        
        
        pass
    def put_del_request(self,request):
        self._del_requests_deque.append(request)


        pass
    def put_failed_request(self,request,table=None):
        try:
            request_dict = request.to_dict
            self._db.zadd(table or self.table_failed_request,request_dict,request.priority)
        except Exception as e:
            log.exception(e)

    def flush(self):
        try:
            self.__add_request_to_db()
        except Exception as e:
            log.exception(e)

    def get_requests_count(self):
        return len(self._requests_deque)
        pass
    def is_adding_to_db(self):
        return self._is_adding_to_db
        pass
    def __add_request_to_db(self):
        request_list = []
        prioritys = [] 
        callbacks = []

        while self._requests_deque:
            request:Request = self._requests_deque.popleft()
            self.is_adding_to_db = True
            if callable(request):
                callbacks.append(request)
            priority = request.fingerprint
            if (
                request.filter_repeat
                and setting.REQUEST_FILTER_ENABLE
                and not self.__class__.dedup.add(request.fingerprint)

            ):
                log.debug(constants.REQUEST_REPEAT+f"   URL = {request.url}")
                continue
            else:
                request_list.append(str(request.to_dict))
                prioritys.append(priority)
            if len(request_list)>MAX_URL_COUNT:
                self._db.zadd(self._table_request,request_list,prioritys)
                request_list = []
                prioritys = []
            
            if request_list:
                self._db.zadd(self._table_request,request_list,prioritys)

            for callback in callbacks:
                try:
                    callback()
                except Exception as e:
                    log.exception(e)
            if self._del_requests_deque:
                reqeust_done_list = []
                while self._del_requests_deque:
                    reqeust_done_list.append(self._del_requests_deque.popleft())
                reqeust_done_list = list(set(reqeust_done_list)-set(request_list))
                if reqeust_done_list:
                    self._db.zrem(self._table_request,reqeust_done_list)

            self._is_adding_to_db = False
                


            
                
