# -*- coding: utf-8 -*-
"""
@Time    : 2021/11/18 11:41
@Author  : lrabbit
@FileName: spider.py
@Software: PyCharm
@Blog    : https://www.lrabbit.life
"""
import traceback
from lrabbit_scrapy.common_utils.mysql_helper import MysqlClient
from lrabbit_scrapy.common_utils.redis_helper import RedisClient
from threading import Thread
from lrabbit_scrapy.common_utils.all_in_one import get_time_format_now
from lrabbit_scrapy.common_utils.print_log_helper import LogUtils


class LrabbitSpider:

    def __init__(self):

        self._init_config()
        self.mysql_client = MysqlClient(config_path_env=self.config_env_name)
        self.redis_client = RedisClient(config_path_env=self.config_env_name, db=self.redis_db_config)
        spider_task_key = f'list:{self.__getattribute__("spider_name")}'
        self.spider_name = self.__getattribute__("spider_name")
        self.task_list_redis_key = spider_task_key
        self.success_count_all_key = f"success:count:{self.spider_name}"
        self.success_count_day_key = f"success:count:{self.spider_name}:{get_time_format_now()}"
        self.fail_count_all_key = f"fail:count:{self.spider_name}"
        self.fail_count_day_key = f"fail:count:{self.spider_name}:{get_time_format_now()}"
        self.thread_task_list = []
        self.task_list = []

    def _init_config(self):
        try:
            self.__getattribute__("thread_mysql_open")
        except:
            self.thread_mysql_open = False
        try:
            self.__getattribute__("max_thread_num")
        except:
            self.max_thread_num = 10
        try:
            self.__getattribute__("reset_task_config")
        except:
            self.reset_task_config = False
        try:
            self.__getattribute__("loop_task_config")
        except:
            self.loop_task_config = False
        try:
            self.__getattribute__("remove_confirm_config")
        except:
            self.remove_confirm_config = False
        try:
            self.__getattribute__("config_env_name")
        except:
            self.config_env_name = "config_path"
        try:
            self.__getattribute__("redis_db_config")
        except:
            self.redis_db_config = 0
        try:
            self.__getattribute__("debug_config")
        except:
            self.debug_config = True

    def _send_task_redis(self, task_list):
        for task in task_list:
            LogUtils.log_info("new task", task)
            self.redis_client.redis_executor.sadd(self.task_list_redis_key, task)

    def update_stat_redis(self):
        """
         success:count_all   success:count:spider_name
         success:count:day   success:count:spider_name:2021-11-11
        :return:
        """
        day = get_time_format_now()
        self.success_count_day_key = f"success:count:{self.spider_name}:{day}"
        self.redis_client.redis_executor.incr(self.success_count_all_key)
        self.redis_client.redis_executor.incr(self.success_count_day_key)

    def _init_task_list(self):

        if self.reset_task_config or not self.redis_client.redis_executor.exists(self.task_list_redis_key):

            LogUtils.log_info("init task list")
            generate_task_list_callback = self.__getattribute__("init_task_list")
            if self.redis_client.redis_executor.exists(self.task_list_redis_key):
                LogUtils.log_info("already exists", self.task_list_redis_key, "task list", "count",
                                  self.redis_client.redis_executor.scard(self.task_list_redis_key))
                try:
                    remove_confirm_config = self.__getattribute__("remove_confirm_config")
                    if not remove_confirm_config:
                        option = input("please input y to delete task list and add new task")
                        if option != 'y':
                            exit(-1)
                except AttributeError as e:
                    option = input("please input y to delete task list and add new task")
                    if option != 'y':
                        exit(-1)
                except Exception as e:
                    pass
                self.redis_client.redis_executor.delete(self.task_list_redis_key)

            generate_task_all = generate_task_list_callback()
            count = self.redis_client.redis_executor.scard(self.task_list_redis_key)
            if count >= 1:
                LogUtils.log_info("already init task")
                return
            if len(generate_task_all) < 10:
                for item in generate_task_all:
                    LogUtils.log_info("new task", item)
                    self.redis_client.redis_executor.sadd(self.task_list_redis_key, item)
            else:
                thread_num = 10
                step = len(generate_task_all) // thread_num
                send_thread_list = []
                for i in range(thread_num):
                    if i == thread_num - 1:
                        t = Thread(target=self._send_task_redis, args=(generate_task_all[i * step:],))
                    else:
                        t = Thread(target=self._send_task_redis, args=(generate_task_all[(i * step):(i + 1) * step],))
                    t.start()
                    send_thread_list.append(t)
                for t in send_thread_list:
                    t.join()
            LogUtils.log_finish("init task list success")

        task_count = self.redis_client.redis_executor.scard(self.task_list_redis_key)
        LogUtils.log_info("current task count", task_count)
        try:
            remove_confirm_config = self.__getattribute__("remove_confirm_config")
            if not remove_confirm_config:
                option = input("please input y to continue")
                if option != 'y':
                    exit(-1)
        except AttributeError as e:
            option = input("please input y to continue")
            if option != 'y':
                exit(-1)
        except Exception as e:
            pass

    def _run(self):
        self._init_task_list()
        try:
            worker_callback = self.__getattribute__("worker")
        except Exception as e:
            LogUtils.log_error("you not define worker function")
            exit(-1)

        def self_loop_call_back():
            while True:
                task = self.redis_client.redis_executor.spop(self.task_list_redis_key)
                if not task:
                    break
                try:
                    self.task_list.append(task)
                    if self.thread_mysql_open:
                        _mysql_client = MysqlClient(config_path_env=self.config_env_name)
                        worker_callback(task, _mysql_client)
                    else:
                        worker_callback(task)
                except Exception as e:
                    name_exception = type(e).__name__.lower()
                    if self.debug_config:
                        traceback.print_exc()
                    else:
                        LogUtils.log_error(task, name_exception, e.__getattribute__('args'))
                    self.redis_client.redis_executor.sadd(
                        f"list:error:count:{self.spider_name}:{name_exception}:{get_time_format_now()}",
                        task)
                    self.fail_count_day_key = f"fail:count:{self.spider_name}:{get_time_format_now()}"
                    self.redis_client.redis_executor.incr(self.fail_count_day_key)
                    self.redis_client.redis_executor.incr(self.fail_count_all_key)
                try:
                    self.task_list.remove(task)
                except Exception as e:
                    pass

        self.task_list = []
        self.process_list = []

        for _ in range(self.max_thread_num):
            t = Thread(target=self_loop_call_back, args=())
            t.start()
            self.process_list.append(t)
        for t in self.process_list:
            t.join()

    def _menu(self):
        import sys
        options = sys.argv[1:]
        if len(options) > 0:
            if options[0] == 'stat':
                LogUtils.log_info("remain t ask list", self.redis_client.redis_executor.scard(self.task_list_redis_key))
                print("\n")
                day = get_time_format_now()
                self.success_count_day_key = f"success:count:{self.spider_name}:{day}"
                LogUtils.log_finish("today success count",
                                    self.redis_client.redis_executor.get(self.success_count_day_key))
                LogUtils.log_error("today fail count", self.redis_client.redis_executor.get(self.fail_count_day_key))
                LogUtils.log_finish("all success count",
                                    self.redis_client.redis_executor.get(self.success_count_all_key))
                LogUtils.log_error("all fail count", self.redis_client.redis_executor.get(self.fail_count_all_key))
                print("\n")
                LogUtils.log_error("404 status_code count",
                                   self.redis_client.redis_executor.scard(
                                       f"list:error:count:{self.spider_name}:exception404:{get_time_format_now()}"))
                LogUtils.log_error("403 status_code count",
                                   self.redis_client.redis_executor.scard(
                                       f"list:error:count:{self.spider_name}:exception403:{get_time_format_now()}"))
                LogUtils.log_error("500 status_code count",
                                   self.redis_client.redis_executor.scard(
                                       f"list:error:count:{self.spider_name}:exception500:{get_time_format_now()}"))
            else:
                LogUtils.log_error(" you can add stat option ,check scrapy stat")
            exit(-1)

    def run(self):
        while True:
            self._menu()
            try:
                self._run()
                if self.loop_task_config:
                    continue
                break
            except KeyboardInterrupt as e:
                # when you keyboard break,need give this task back
                while True:
                    if len(self.task_list) == 0:
                        break
                    task = self.task_list.pop()
                    if not task:
                        break
                    self.redis_client.redis_executor.sadd(self.task_list_redis_key, task)
        LogUtils.log_now_time_str()
        LogUtils.log_finish("all finish")


if __name__ == '__main__':
    spider = LrabbitSpider()
