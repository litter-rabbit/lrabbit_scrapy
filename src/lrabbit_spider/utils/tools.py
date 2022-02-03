import time

def delay_time(sleep_time=60):
    time.sleep(sleep_time)


class Singleton(object):
    def __init__(self,cls):
        self._cls = cls
        self._instance = {}
        
    def __call__(self,*args,**kwargs):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls(*args,**kwargs)
        return self._instance[self._cls]
    