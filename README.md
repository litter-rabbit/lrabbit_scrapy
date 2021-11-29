lrabbit_scrapy
=====

this is a small spider,you can easy running. When you often need to crawl a single site, you don't have to redo some
repeated code every time, using this small framework you can quickly crawl data into a file or database.


Installing
----------

    $ pip install lrabbit_scrapy

quick start
----------------

* create blog_spider.py

```python
from lrabbit_scrapy.spider import LrabbitSpider
from lrabbit_scrapy.common_utils.network_helper import RequestSession
from lrabbit_scrapy.common_utils.print_log_helper import LogUtils
from lrabbit_scrapy.common_utils.all_in_one import FileStore
import os
from lrabbit_scrapy.common_utils.mysql_helper import MysqlClient
from parsel import Selector


class Spider(LrabbitSpider):
    """
        spider_name : lrabbit blog spider
    """
    # unique spider name
    spider_name = "lrabbit_blog"
    # max thread worker numbers
    thread_mysql_open = True
    max_thread_num = 5
    # reset all task_list
    reset_task_config = True
    # open loop init_task_list
    loop_task_config = True
    # remove config option
    remove_confirm_config = True
    # config_path_name
    config_env_name = "config_path"
    # redis db_num
    redis_db_config = 0
    # debug log
    debug_config = False

    def __init__(self):
        super().__init__()
        self.session = RequestSession()
        self.proxy_session = RequestSession(proxies=None)
        csv_path = os.path.join(os.path.abspath(os.getcwd()), f"{self.spider_name}.csv")
        self.field_names = ['id', 'title', 'datetime']
        self.blog_file = FileStore(file_path=csv_path, filed_name=self.field_names)

    def worker(self, *args):
        task = args[0]
        # mysql_client: MysqlClient
        # if len(args) == 2:
        #     mysql_client = args[1]

        res = self.session.send_request(method='GET', url=f'http://www.lrabbit.life/post_detail/?id={task}')
        selector = Selector(res.text)
        title = selector.css(".detail-title h1::text").get()
        datetime = selector.css(".detail-info span::text").get()
        if title:
            post_data = {"id": task, "title": title, 'datetime': datetime}
            self.blog_file.write(post_data)
            # when you succes get content update redis stat
            self.update_stat_redis()
        LogUtils.log_finish(task)
     
    def init_task_list(self):
        # res = self.mysql_client.execute_query("select id from rookie limit 100 ")
        # return [item['id'] for item in res]
        return [i for i in range(100)]


if __name__ == '__main__':
    spider = Spider()
    spider.run()


```

* set config.ini and config env variable
    * create crawl.ini forexam this file path is /root/crawl.ini
    ```ini
  [server]
  mysql_user = root
  mysql_password = 123456
  mysql_database = test
  mysql_host = 192.168.1.1
  redis_user = lrabbit
  redis_host = 192.168.1.1
  redis_port = 6379
  redis_password = 123456

  [test]
  mysql_user = root
  mysql_password = 123456
  mysql_database = test
  mysql_host = 192.168.1.1
  redis_user = lrabbit
  redis_host = 192.168.1.1
  redis_port = 6379
  redis_password = 123456
  ```
    * set config env
        * windows power shell
        * $env:config_path = "/root/crawl.ini"
        * linux
        * export config_path="/root/crawl.ini"


* python3 blog_spider.py
* python3 blog_spider.py stat 
    * show task stat 

Links
-----

- author: https://www.lrabbit.life/

