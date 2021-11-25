# -*- coding: utf-8 -*-
"""
@Time    : 2021/11/18 10:14
@Author  : lrabbit
@FileName: redis_helper.py
@Software: PyCharm
@Blog    : https://www.lrabbit.life
"""
import redis
from lrabbit_scrapy.common_utils.config_helper import get_redis_config, get_config_path


class RedisClient:

    def __init__(self, db=0, config_path_env=None, env='test'):
        config_path = get_config_path(config_path_env)
        redis_config = get_redis_config(config_path, env)
        self.redis_executor = redis.StrictRedis(host=redis_config.REDIS_HOST, port=redis_config.REDIS_PORT,
                                                password=redis_config.REDIS_PASSWORD,
                                                db=db,decode_responses=True)


if __name__ == '__main__':
    redis_client = RedisClient()
