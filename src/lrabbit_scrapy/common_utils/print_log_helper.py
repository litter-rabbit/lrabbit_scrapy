# -*- coding: utf-8 -*-
"""
@Time    : 2021/11/18 10:14
@Author  : lrabbit
@FileName: redis_helper.py
@Software: PyCharm
@Blog    : https://www.lrabbit.life
"""

import datetime
import os


class TermColor:
    ATTRIBUTES = dict(
        list(zip([
            'bold',
            'dark',
            '',
            'underline',
            'blink',
            '',
            'reverse',
            'concealed'
        ],
            list(range(1, 9))
        ))
    )
    del ATTRIBUTES['']

    HIGHLIGHTS = dict(
        list(zip([
            'on_grey',
            'on_red',
            'on_green',
            'on_yellow',
            'on_blue',
            'on_magenta',
            'on_cyan',
            'on_white'
        ],
            list(range(40, 48))
        ))
    )

    COLORS = dict(
        list(zip([
            'grey',
            'red',
            'green',
            'yellow',
            'blue',
            'magenta',
            'cyan',
            'white',
        ],
            list(range(30, 38))
        ))
    )

    RESET = '\033[0m'

    @staticmethod
    def colored(text, color=None, on_color=None, attrs=None):

        if os.getenv('ANSI_COLORS_DISABLED') is None:
            fmt_str = '\033[%dm%s'
            if color is not None:
                text = fmt_str % (TermColor.COLORS[color], text)

            if on_color is not None:
                text = fmt_str % (TermColor.HIGHLIGHTS[on_color], text)

            if attrs is not None:
                for attr in attrs:
                    text = fmt_str % (TermColor.ATTRIBUTES[attr], text)

            text += TermColor.RESET
        return text


class CommonUtils:

    def __init__(self):
        pass

    @staticmethod
    def fix_str_args(args):
        return list(map(lambda x: str(x).strip(), args))

    @staticmethod
    def get_format_time(for_mat='%Y-%m-%d %H:%M:%S'):
        return TermColor.colored(datetime.datetime.now().strftime(for_mat), 'yellow')

    @staticmethod
    def space_join_line_arg(*args):
        return ' '.join(args) + '\n'


class LogUtils:

    def __init__(self):
        pass

    @staticmethod
    def log_now_time_str():
        # fix buffer cache
        # sys.stdout.buffer.write()
        print(CommonUtils.get_format_time())

    @staticmethod
    def log_str(color_str, args):
        args = CommonUtils.fix_str_args(args)
        text = ' '.join(args)
        text = color_str + ' ' + text + '\n'
        # fix buffer cache
        # sys.stdout.buffer.write(text.encode('utf8'))
        print(text,end='')

    @staticmethod
    def log_info(*args):
        color_str = TermColor.colored('[*INFO*]', 'cyan')
        LogUtils.log_str(color_str, args)

    @staticmethod
    def log_running(*args):
        color_str = TermColor.colored('[*RUNNING*]', 'yellow')
        LogUtils.log_str(color_str, args)

    @staticmethod
    def log_finish(*args):
        color_str = TermColor.colored('[*FINISH*]', 'green')
        LogUtils.log_str(color_str, args)

    @staticmethod
    def log_error(*args):
        color_str = TermColor.colored('[*ERROR*]', 'red')
        LogUtils.log_str(color_str, args)

    @staticmethod
    def log_to_file(file_path, line):
        """

        :param file_path: log file path
        :param line: a str type
        :return:
        """
        with open(file_path, 'a', encoding='utf8') as f:
            line = CommonUtils.space_join_line_arg(LogUtils.get_format_time(), line)
            f.write(line)
