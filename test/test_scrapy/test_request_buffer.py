from threading import Thread
from urllib import request
from lrabbit_spider.buffer.request_buffer import RequestsBuffer
from lrabbit_spider.network.request import Request
import time

request_buffer =  RequestsBuffer("test_request_buffer")

request_buffer.start()


while True:

    request_buffer.put_request(Request(url="https://www.baidu.com"))
    time.sleep(1)

 