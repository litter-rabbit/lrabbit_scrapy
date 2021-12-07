import traceback
import os
from lrabbit_scrapy.common_utils.print_log_helper import LogUtils
from pathlib import Path
import subprocess


def start_frida_server(servername):
    server_path = f'/data/local/tmp/{servername}'
    killserver = "adb shell su -c killall -9 " + servername
    os.system(killserver)
    subprocess.Popen(
        ["adb", "shell", "su", "-c", server_path])


def sslbypass(server_name='15.0.0'):
    try:
        start_frida_server(server_name)
    except Exception as e:
        traceback.print_exc()
        LogUtils.log_error("please check frida-server name or this  path is in /data/local/tmp?")
        exit(0)
    current_parent_path = Path(__file__).parent
    frida_path = os.path.join(current_parent_path, 'sslpass.js')
    frida_hook_cmd = f"frida -FU -l {frida_path} --no-pause"
    os.system(frida_hook_cmd)
    subprocess.Popen(
        ["frida", "-FU", "-l", frida_path, "--no-pause"])


if __name__ == '__main__':
    sslbypass()
