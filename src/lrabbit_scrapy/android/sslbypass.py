import frida
import os
from threading import Thread


def start_frida_server():
    import os
    print("restart frida server")
    servername = "lrabbitarm64"
    port = "2333"
    server_path = input(f"please input frida_server path enter:/data/local/tmp/{servername}")
    if len(server_path) <= 3:
        server_path = f'/data/local/tmp/{servername}'
    killserver = "adb shell su -c killall -9 " + servername
    os.system(killserver)
    adbserver = "adb shell su -c " + server_path + " -l " + "0.0.0.0:" + port
    res = os.popen(adbserver)
    for i in res:
        print(i)


def sslbypass():
    phohe_ip = "192.168.1.97"
    t = Thread(target=start_frida_server, args=())
    t.start()
    cmd = f"frida-ps -H {phohe_ip}:2333 |grep -v xiaomi |grep -v tencent |grep -v miui"
    applciations = os.popen(cmd)
    app_dict = {}
    count = 0
    for i in applciations:
        count += 1
        app_dict[str(count)] = i.split()[-1]
    for k, v in app_dict.items():
        print(f'{k} : {v}')
    app_name = input("请输入对应的数字 eg 1 2\n")
    print(f'当前手机IP: {phohe_ip}')
    device = frida.get_device_manager().add_remote_device(f'{phohe_ip}:2333')
    packagename = app_dict[app_name]
    pid = device.spawn([packagename])
    device.resume(pid)
    device.attach(pid)


if __name__ == '__main__':
    sslbypass()
