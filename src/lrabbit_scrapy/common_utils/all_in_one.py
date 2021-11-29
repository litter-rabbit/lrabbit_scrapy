# -*- coding: utf-8 -*-
"""
@Time    : 2021/11/18 10:22
@Author  : lrabbit
@FileName: all_in_one.py
@Software: PyCharm
@Blog    : https://www.lrabbit.life
"""
import os
import datetime
import csv
from lrabbit_scrapy.all_excepiton import ExceptionFileFieldNameError


def get_time_format_now(option=1):
    if option == 1:
        return datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class FileStore:

    def __init__(self, file_path: str, filed_name: list):
        self.file_path = file_path
        self.file_name = os.path.splitext(file_path)
        self.filed_name = filed_name

    def write(self, d: dict):
        """
        :param d: dict type
        :return:
        """
        if list(d.keys()) != self.filed_name:
            raise ExceptionFileFieldNameError()

        with open(self.file_path, 'a', encoding='utf8', newline='') as f:
            dict_write = csv.DictWriter(f, fieldnames=self.filed_name)
            dict_write.writerow(d)

    def write_many(self, rows: [dict]):
        if list(d.keys()) != self.filed_name:
            raise ExceptionFileFieldNameError()
        with open(self.file_path, 'a', encoding='utf8', newline='') as f:
            dict_write = csv.DictWriter(f, fieldnames=self.filed_name)
            dict_write.writerows(rows)


if __name__ == '__main__':
    blog_file = FileStore(r"D:\PythonWorkSpace\lrabbit_scrapy\test\blogPost.csv", ["title"])
    d = {"title": "1"}
    blog_file.write(d)
