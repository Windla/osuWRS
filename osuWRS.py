#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import glob
import requests
import win32api
import win32con
from threading import Thread

QUICK_START = 1  # 快速启动  0：关闭 1:开启 | 默认 0
OVERTIME = 5  # 连接ppy服务器超时时间 | 默认 5
VERSION = "2.2.2"  # 当前osuWRS版本号
osuWRS_path = os.getcwd()  # 获取osuWRS工作目录
stop_threads = False  # 全局变量 virtual_key 线程运行&退出 | True: 不进行按键模拟

os.system("title osuWRS By -Windla- (Bilibili)")
print("[!] osuWRS作者: B站 @-Windla-")
print("[!] osuWRS版本:", VERSION)


# bg刷新检测
def bg_num_get():
    num = len(glob.glob(bgPath + "\\*.jpg"))
    return num


# 按键模拟
def virtual_key():
    global stop_threads
    while True:
        # P * 3
        for i in range(3):
            if stop_threads:
                break
            win32api.keybd_event(80, 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(80, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.02)
        time.sleep(0.5)
        # ESC * 1
        if stop_threads:
            break
        win32api.keybd_event(0x1B, win32api.MapVirtualKey(0x1B, 0), 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(0x1B, win32api.MapVirtualKey(0x1B, 0), win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)


# 遍历更改bg文件名
def bg_rename(path, name):
    i = 1
    for file in os.listdir(path):
        os.rename(os.path.join(path, file), os.path.join(path, name + str(i)) + ".jpg")
        i += 1


# 检查待替换bg文件夹
def bg_check():
    i = 1
    while i != bg_num + 1:
        if not os.path.exists(osuWRS_path + "\\bg\\bg_" + str(i) + ".jpg"):
            print("[-] 状态: 重新初始化bg文件名 | bg_" + str(i) + "丢失")
            bg_rename(osuWRS_path + "\\bg", "pre_bg_")
            bg_rename(osuWRS_path + "\\bg", "bg_")
            break
        i += 1


# 解锁bg&删除旧bg
def bg_update():
    os.system('echo y|cacls ' + bgPath + ' /t /p everyone:f > nul')
    for bg_file in glob.glob(bgPath + "\\" + "*.jpg"):
        os.remove(bg_file)


# 锁定bg&替换新bg
def bg_replace():

    os.system('echo y|cacls ' + bgPath + ' /t /p everyone:f > nul')
    os.system('md ' + Path + '\\Data\\bg_temp > nul')
    os.system('copy "' + osuWRS_path + '\\bg\\*.jpg" "' + Path + '\\Data\\bg_temp" > nul')

    num = 1
    for osu_bg in glob.glob(bgPath + "\\" + "*.jpg"):
        os.remove(osu_bg)
        os.rename(bgTempPath + "\\bg_" + str(num) + ".jpg", osu_bg)
        if num == bg_num:
            break
        num += 1

    os.system('rd /s /q ' + bgTempPath + ' > nul')
    os.system('echo y|cacls ' + bgPath + ' /t /p everyone:r > nul')


#  多线程 | bg刷新检测&剩余的步骤
def thread_main():
    i = 0
    e = 0  # 错误计数
    n = bg_num_get()
    global stop_threads
    print("[!] 提示: 请确保你的鼠标焦点位于osu!上, 不要移动!")
    while n != bg_num:
        n = bg_num_get()
        time.sleep(0.01)  # 越小消耗越大但越精准
        if i != n:
            print("[+] 进度: 已获取" + str(n) + "张服务器bg图")
            i = n
            e = 0
        else:
            e += 1

        # 防呆措施
        if e >= 1000:  # 大约10s无进度
            # 声明退出virtual_key线程
            stop_threads = True
            # 腾空屏幕为显示log准备
            os.system("taskkill /F /IM osu!.exe > nul")
            with open("error.log", "w") as file:
                file.write('[Error] 不要超过ppy的服务器上限! 目前是最高' + str(n) + '张可替换的bg图 | 或者检查您的网络')
            win32api.ShellExecute(0, 'open', osuWRS_path + "\\bg", '', '', 1)
            time.sleep(2)
            win32api.ShellExecute(0, 'open', osuWRS_path + "\\error.log", '', '', 1)
            exit()
    # 声明退出virtual_key线程
    stop_threads = True
    time.sleep(0.01)
    # 杀死osu
    os.system("taskkill /F /IM osu!.exe > nul")
    # ------------------------------------------------------
    # 检查待替换bg
    bg_check()
    # 开始替换
    bg_replace()
    # 将新数据写入bg.php
    with open("bg.php", "wb") as file:
        file.write(ppyUrl)
    # 启动osu(替换成功后)
    print("[+] 状态: 更新成功!")
    time.sleep(1)
    win32api.ShellExecute(0, 'open', osuPath, '', '', 1)
    exit()


# ------------------------------初始化 | 配置文件读取---------------------------------
# bg文件夹 | bg数量识别
if not os.path.exists(osuWRS_path + "\\bg"):
    os.mkdir(osuWRS_path + "\\bg")
bg_num = len(glob.glob(osuWRS_path + "\\bg\\*.*"))
if bg_num == 0:
    print("[-] Error: 请在运行目录下的bg文件夹内放入待替换图片(只接受jpg/png格式 | 不建议超过10张)")
    time.sleep(5)
    exit()
print("[!] bg待替换数量:", bg_num, "张\n[!] 提示: 替换速度与bg替换数量负相关 | 不建议超过10张")
# config.ini
try:
    with open("config.ini", 'r') as f:
        Path = f.read()  # osu 路径
        f.close()
    if Path.find("Error") != -1 or Path.find("osu!") == -1:
        win32api.ShellExecute(0, 'open', osuWRS_path + "\\config.ini", '', '', 1)
        exit()
except FileNotFoundError:
    with open("config.ini", "w") as f:
        f.write('Error: 请将该行替换成你osu!根目录的绝对路径, 并重新打开osuWRS')
    win32api.ShellExecute(0, 'open', osuWRS_path + "\\config.ini", '', '', 1)
    exit()
osuPath = Path + "\\osu!.exe"  # osu.exe 路径
bgPath = Path + "\\Data\\bg"  # bg文件夹 路径
bgTempPath = Path + "\\Data\\bg_temp"  # 跨驱动器的解决方案

# 快速启动
if QUICK_START == 1:
    win32api.ShellExecute(0, 'open', osuPath, '', '', 1)

# 获取ppy数据&本地数据
while True:
    try:
        print("[+] 状态: 正在连接osu!服务器")
        ppyUrl = requests.get("https://osu.ppy.sh/web/osu-getseasonal.php", timeout=OVERTIME).text.encode()  # ppy数据
        print("[+] 状态: 获取bg信息成功")
        break
    except requests.exceptions.RequestException:
        print("[-] 连接osu!服务器超时")
while True:
    try:
        with open("bg.php", 'r') as f:
            ppyUrlOld = (f.read()).encode()
            f.close()
        break
    except FileNotFoundError:
        with open("bg.php", "w") as f:
            f.write('不要删除这个文件!')

# 数据变化判断
if ppyUrl != ppyUrlOld:  # seasonal background 更新后开始进行 bg更新
    # 杀死osu 当前启动的osu
    os.system("taskkill /F /IM osu!.exe > nul")
    # 删除旧图&开放权限
    bg_update()
    # 拉起osu
    win32api.ShellExecute(0, 'open', osuPath, '', '', 1)
    time.sleep(5)
    # 对osu启动的检测
    getnum = 0
    while getnum == 0:
        getnum = bg_num_get()
        time.sleep(0.1)
    print("[+] 进度: 成功启动osu!")
    time.sleep(3)

    # 尝试多进程以减少失误
    thread_01 = Thread(target=thread_main)
    thread_02 = Thread(target=virtual_key)
    thread_01.start()
    # 给 bg_num = 1 的反应时间
    time.sleep(0.25)
    thread_02.start()

else:
    print("[+] 状态: 无更新!")
    time.sleep(1)
    if QUICK_START != 1:
        win32api.ShellExecute(0, 'open', osuPath, '', '', 1)
