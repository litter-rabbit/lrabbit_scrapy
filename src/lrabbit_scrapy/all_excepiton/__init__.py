# -*- coding: utf-8 -*-
"""
@Time    : 2021/11/22 13:41
@Author  : lrabbit
@FileName: spider.py
@Software: PyCharm
@Blog    : https://www.lrabbit.life
"""


class Excepiton403(Exception):
    def __init__(self):
        self.__name = "exception403"


class Exception404(Exception):
    pass


class Exception500(Exception):
    pass


class ExceptionFileFieldNameError(Exception):
    pass


if __name__ == '__main__':
    print(type(Excepiton403()).__name__)
