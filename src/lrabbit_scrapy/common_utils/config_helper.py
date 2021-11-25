# -*- coding: utf-8 -*-
"""
@Time    : 2021/11/18 10:27
@Author  : lrabbit
@FileName: config_helper.py
@Software: PyCharm
@Blog    : https://www.lrabbit.life
"""

from configparser import ConfigParser
import os


class MysqlConfigClass:
    MYSQL_USER = None
    MYSQL_PASSWORD = None
    MYSQL_DATABASE = None
    MYSQL_HOST = None
    MYSQL_PORT = 3306


class RedisConfigClass:
    REDIS_PASSWORD = None
    REDIS_DATABASE = None
    REDIS_HOST = None
    REDIS_PORT = 6379


def get_config(config_path=None, env='test'):
    """

     :param config_path:
     :return:
     """
    config = ConfigParser()
    if not config_path:
        pwd = os.path.dirname(__file__)
        config_path = os.path.join(pwd, 'crawl.ini')
    config.read(config_path)
    if os.getenv("ENV") == 'server':
        env = os.getenv("ENV")
    config = config[env]
    return config


def get_mysql_config(config_path, env='test') -> MysqlConfigClass:
    if not config_path:
        raise Exception("无效的文件路径")
    config = get_config(config_path, env)
    mysqlconfig = MysqlConfigClass()
    for k, v in config.items():
        setattr(mysqlconfig, k.upper(), v)
    return mysqlconfig


def get_redis_config(config_path, env='test') -> RedisConfigClass:
    if not config_path:
        raise Exception("无效的文件路径")
    config = get_config(config_path, env)
    redisconfig = RedisConfigClass()
    for k, v in config.items():
        setattr(redisconfig, k.upper(), v)
    return redisconfig


def get_config_path(config_path_env=None):
    if not config_path_env:
        config_path_env = "config_path"
    config_path = os.environ.get(config_path_env)
    if not config_path:
        raise Exception(f"请设置环境变量{config_path_env}为ini配置文件的绝对路径")
    return config_path
