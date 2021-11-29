# -*- coding: utf-8 -*-
"""
@Time    : 2021/11/18 10:21
@Author  : lrabbit
@FileName: network_helper.py
@Software: PyCharm
@Blog    : https://www.lrabbit.life
"""

import urllib3
import requests
from lrabbit_scrapy.all_excepiton import Excepiton403, Exception404, Exception500

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequestSession:

    def __init__(self, proxies=None, timeout=15, headers=None):
        self.proxies = proxies
        self.timeout = timeout
        self.session = requests.session()
        self.session.headers = headers

    def send_request(self, method='GET', url=None, headers=None, data=None) -> requests.Response:

        if method == 'GET':
            res = self.session.get(url, proxies=self.proxies, verify=False, timeout=self.timeout)
        else:
            if isinstance(data, dict):
                res = self.session.post(url, json=data, proxies=self.proxies, headers=headers, verify=False,
                                        timeout=self.timeout)
            elif isinstance(data, str):
                res = self.session.get(url, data=data, proxies=self.proxies, headers=headers, verify=False,
                                       timeout=self.timeout)
            else:
                raise Exception("no data post")
        return self.deal_res(res)

    def download_file_by_url(self, out_file_path, url, headers=None):
        res = self.session.get(url=url, headers=headers, proxies=self.proxies, verify=False, stream=True,
                               )
        with open(out_file_path, 'wb') as f:
            for chunk in res.iter_content(1024):
                if chunk:
                    f.write(chunk)
        return out_file_path

    def deal_res(self, res):
        if res.status_code == 403:
            raise Excepiton403()
        elif res.status_code == 404:
            raise Exception404()
        elif res.status_code == 500:
            raise Exception500()
        return res


if __name__ == '__main__':
    session = RequestSession()
