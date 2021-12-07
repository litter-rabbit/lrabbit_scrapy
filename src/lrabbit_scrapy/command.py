import os
from pathlib import Path
from lrabbit_scrapy.common_utils.print_log_helper import LogUtils
from lrabbit_scrapy.android.sslbypass import sslbypass

base_dir = Path(__file__).resolve().parent


def newspider(spider_name):
    copy_new_name_file(spider_name, f'{spider_name}.py', 'asy_crawl.py')
    copy_new_name_file(spider_name, f'{spider_name}.ini', 'config.py', is_config=True)
    LogUtils.log_finish('创建项目成功')


def new_template_spider(spider_name):
    copy_new_name_file(spider_name, f'{spider_name}.py', 'template_crawl.py')
    LogUtils.log_finish('创建项目成功')


def copy_new_name_file(spider_name, new_name, src_name, is_config=False):
    dst_path = os.path.abspath(os.getcwd())
    if not os.path.exists(os.path.join(dst_path, spider_name)):
        os.mkdir(os.path.join(dst_path, spider_name))
    dst_path = os.path.join(dst_path, spider_name)
    dst_file = os.path.join(dst_path, new_name)
    src_file = os.path.join(base_dir, src_name)
    if os.path.exists(dst_file):
        raise Exception(f'please remove your file {dst_file}')
    f2 = open(dst_file, 'a')
    with open(src_file, 'r') as f:
        for line in f.readlines():
            if is_config:
                line = line.replace("# ", "")
            f2.write(line)
    f2.close()


def run(*args):
    argv = args[0]
    if argv == 'new_scrapy':
        spider_name = args[1]
        print("opts", spider_name)
        new_template_spider(spider_name)
    elif argv == 'sslpass':
        sslbypass()
    elif argv == 'asy_new_scrapy':
        spider_name = args[1]
        print("opts", spider_name)
        newspider(spider_name)
    else:
        print("options: new_scarpy or sslpass or asy_new_scrapy ")


if __name__ == '__main__':
    import sys

    argv = sys.argv[1:]
    run(*argv)
