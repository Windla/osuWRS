#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import glob
import requests
import win32api
import win32con

quick_start = 1  # 0：关闭 1:开启 | 默认 0
overtime = 5  # 与ppy服务器连接的超时时间 | 默认 5
version = "2.1.1"  # 当前版本号
OsuWRS_path = os.getcwd()  # 获取OsuWRS工作目录

os.system("title OsuWRS By -Windla- (Bilibili)")
print("[!] OsuWRS作者: B站 @-Windla-")
print("[!] OsuWRS版本:", version)


# bg刷新检测
def get_bg_num():
    bg_num_get = len(glob.glob(bgPath + "\\*.jpg"))
    print("[+] 进度: 已获取" + str(bg_num_get) + "张服务器bg图")
    return bg_num_get


# 按键模拟 | bg刷新 | 多线程需要(暂时舍弃)
def virtual_key():
    # P*3
    for i in range(3):
        win32api.keybd_event(80, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(80, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
    time.sleep(0.25)
    # ESC*1
    win32api.keybd_event(0x1B, win32api.MapVirtualKey(0x1B, 0), 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(0x1B, win32api.MapVirtualKey(0x1B, 0), win32con.KEYEVENTF_KEYUP, 0)


# 遍历更改文件名
def rename(path, name):
    num = 1
    for file in os.listdir(path):
        os.rename(os.path.join(path, file), os.path.join(path, name + str(num)) + ".jpg")
        num += 1


# 检查待替换bg文件夹
def bg_check():
    num = 1
    while True:
        if not os.path.exists(OsuWRS_path + "\\bg\\bg_" + str(num) + ".jpg"):
            os.system('cls' if os.name == 'nt' else 'clear')
            print("[-] 状态: 重新初始化bg文件名 | bg_" + str(num) + "丢失")
            rename(OsuWRS_path + "\\bg", "pre_bg_")
            rename(OsuWRS_path + "\\bg", "bg_")
            break
        num += 1


def bg_update():
    os.system('echo y|cacls ' + bgPath + ' /t /p everyone:f')
    for bg_file in glob.glob(bgPath + "\\" + "*.jpg"):
        os.remove(bg_file)


def bg_replace():
    os.system('echo y|cacls ' + bgPath + ' /t /p everyone:f')
    os.system('md ' + Path + '\\Data\\bg_temp')
    os.system('copy "' + OsuWRS_path + '\\bg\\*.jpg" "' + Path + '\\Data\\bg_temp"')
    os.system('cls' if os.name == 'nt' else 'clear')

    num = 1
    for Osu_bg in glob.glob(bgPath + "\\" + "*.jpg"):
        os.remove(Osu_bg)
        os.rename(bgTempPath + "\\bg_" + str(num) + ".jpg", Osu_bg)
        if num == bg_num:
            break
        num += 1

    os.system('rd /s /q ' + bgTempPath)
    os.system('echo y|cacls ' + bgPath + ' /t /p everyone:r')


# ------------------------------初始化 | 配置文件读取---------------------------------
# bg文件夹 | bg数量识别
if not os.path.exists(OsuWRS_path + "\\bg"):
    os.mkdir(OsuWRS_path + "\\bg")
bg_num = len(glob.glob(OsuWRS_path + "\\bg\\*.*"))
if bg_num == 0:
    print("[-] Error: 请在运行目录下的bg文件夹内放入待替换图片(只接受jpg/png格式|只能一张)")
    time.sleep(5)
    exit()
print("[!] bg待替换数量:", bg_num, "张\n[!] 提示: 替换速度与bg替换数量负相关 | 不建议超过5张")
# config.ini
try:
    with open("config.ini", 'r') as f:
        Path = f.read()  # osu 路径
        f.close()
    if Path.find("Error") != -1 or Path.find("osu!") == -1:
        win32api.ShellExecute(0, 'open', OsuWRS_path + "\\config.ini", '', '', 1)
        exit()
except FileNotFoundError:
    with open("config.ini", "w") as f:
        f.write('Error: 请将该行替换成你osu!根目录的绝对路径, 并重新打开OsuWRS')
    win32api.ShellExecute(0, 'open', OsuWRS_path + "\\config.ini", '', '', 1)
    exit()
osuPath = Path + "\\osu!.exe"  # osu.exe 路径
bgPath = Path + "\\Data\\bg"  # bg文件夹 路径
bgTempPath = Path + "\\Data\\bg_temp"  # 跨驱动器的解决方案

# 快速启动
if quick_start == 1:
    win32api.ShellExecute(0, 'open', osuPath, '', '', 1)

# 获取ppy数据&本地数据
while True:
    try:
        print("[+] 状态: 正在连接osu服务器")
        ppyUrl = requests.get("https://osu.ppy.sh/web/osu-getseasonal.php", timeout=overtime).text.encode()  # ppy数据
        print("[+] 状态: 获取bg信息成功")
        break
    except requests.exceptions.RequestException:  # 蚌埠住了
        print("[-] 连接osu服务器超时")
while True:
    try:
        with open("bg.php", 'r') as f:  # 原数据
            ppyUrlOld = (f.read()).encode()
            f.close()
        break
    except FileNotFoundError:
        with open("bg.php", "w") as f:
            f.write('不要删除这个文件!')

# 数据变化判断
if ppyUrl != ppyUrlOld:  # seasonal background 更新后开始进行 bg更新
    # 杀死osu 当前启动的osu
    os.system("taskkill /F /IM osu!.exe")
    # 删除旧图&开放权限
    bg_update()
    # 拉起osu
    win32api.ShellExecute(0, 'open', osuPath, '', '', 1)
    time.sleep(3)
    # 已下载bg数量检测
    getnum = 0
    while getnum != 0:
        getnum = get_bg_num()
        time.sleep(0.2)
    time.sleep(3)
    while getnum != bg_num:
        virtual_key()
        getnum = get_bg_num()
    # 杀死osu
    os.system("taskkill /F /IM osu!.exe")
    # 检查待替换bg
    bg_check()
    # 开始替换
    bg_replace()
    # 将新数据写入bg.php
    with open("bg.php", "wb") as f:
        f.write(ppyUrl)
    # 启动osu(替换成功后)
    print("[+] 状态: 更新成功!")
    time.sleep(3)
    win32api.ShellExecute(0, 'open', osuPath, '', '', 1)
else:
    print("[+] 状态: 无更新!")
    time.sleep(3)
exit()
