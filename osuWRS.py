#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import time
import glob
import win32api
import win32con
import configparser
from threading import Thread
# requests检测
try:
    import requests as req
except Exception as import_error:
    print(str(import_error) + "\n缺少requests模块, 请在终端中执行命令：pip3 install requests\n")
    time.sleep(10)
    exit(1)


# config 初始化
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
# config.ini 载入
osu_path = config['osu']['path']
QUICK_START = config['osu']['quickStart']
VERSION = config['osuWRS']['version']
OVERTIME = int(config['osuWRS']['overtime'])
debugMode = config['osuWRS']['debugMode']
check_set = config['set']['checkSet']
auto_set = config['set']['autoSet']
# 默认参数&全局变量
osuWRS_path = os.getcwd()  # 获取osuWRS工作目录
stop_threads = False  # 全局变量 virtual_key 线程运行&退出 | True: 不进行按键模拟
req_new = bytes()
os.environ['no_proxy'] = '*'  # 设置 no_proxy 环境变量 | 不使用代理


os.system("title osuWRS By Windla")
print("[!] osuWRS作者: B站 @-Windla-")
print("[!] osuWRS版本:", VERSION)
print("[!] 调试模式状态:", debugMode)


# 检测 seasonal backgrounds 的设置状态 -> Always
def setting_check():
    glob_cfg = glob.glob(osu_path + r'\osu!.*.cfg')
    if len(glob_cfg) == 1:
        osu_cfg = glob_cfg[0]  # 防止出现多账号 未测试

        # --- chatGPT 赞助支持() ---
        # 读取文本
        with open(osu_cfg, 'r', encoding='utf-8') as f:
            text = f.read()
        for or_key in ['Sometimes', 'Never']:
            key = r'SeasonalBackgrounds = ' + or_key
            if re.search(key, text):
                print(f"[!] 警告: 当前季节背景设置为 {or_key}")
                print(f"[!] 自动修改游戏内设置状态: {auto_set}")
                if auto_set == 'on':
                    text = re.sub(key, 'SeasonalBackgrounds = Always', text)
                    # 将修改后的文本写入新文件
                    with open(osu_cfg, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"[!] 提示: 季节背景已自动设置为 Always")
                else:
                    print("[!] 警告: 请自行修改 SeasonalBackgrounds = Always\n"
                          "[!] 提示: 可以选择在config.ini中\n"
                          "         将[set]的键值全修改为'on'即可实现自动修改")
                    time.sleep(10)
                    exit(1)
    else:
        print("[!] 提示: 可能存在多账号或无账号, 请自行检查osu!内设置\n"
              "         或者修改 config.ini [set]checkSet = off 以关闭检查"
              "[!] 匹配到的用户文件:", glob_cfg)


# 检测php数据更新
def php_update():
    global req_new
    req_error = 0  # 连接错误
    while True:
        try:
            print("[+] 状态: 正在连接osu!服务器")
            req_new = req.get("https://osu.ppy.sh/web/osu-getseasonal.php", timeout=OVERTIME).text.encode()  # ppy数据
            print("[+] 状态: 获取bg信息成功")
            break
        except req.exceptions.RequestException:
            req_error += 1
            print(f"[-] 连接osu!服务器超时, 次数: {req_error}")
            if req_error >= 10:
                print("请检查您的网络!")
                time.sleep(10)
                exit(1)
    try:
        with open('bg.php', 'r') as f:
            req_old = f.read().encode()
    except IOError:
        req_old = b''

    # 替换法允许的最多bg图数
    req_max = req_new.count(b',') + 1

    if req_new == req_old:
        req_code = 0
    else:
        req_code = 1

    return req_code, req_max


# bg刷新检测
def bg_num_get():
    num = len(glob.glob(bgPath + "\\*.jpg"))
    return num


# 按键模拟 | 弃用
def virtual_key_v1():
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


# 按键模拟 简化
def kb(key_list, key_time, sleep_time):  # 键值[列表] 按下时间 下次触发延迟
    for key in key_list:
        win32api.keybd_event(key, win32api.MapVirtualKey(key, 0), 0, 0)
    time.sleep(key_time)
    for key in key_list:
        win32api.keybd_event(key, win32api.MapVirtualKey(key, 0), win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(sleep_time)


# 按键模拟 基于重载skin方式
def virtual_key_v2():
    global stop_threads
    virtual_key_list = [0x11, 0x10, 0x12, 0x53]  # Ctrl+Shift+Alt+S
    while True:
        if stop_threads:
            break
        kb(virtual_key_list, 0.1, 0.8)


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
    os.system('md ' + osu_path + '\\Data\\bg_temp > nul')
    os.system('copy "' + osuWRS_path + '\\bg\\*.jpg" "' + osu_path + '\\Data\\bg_temp" > nul')

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
    global stop_threads, req_new
    print("[!] 提示: 请确保你的鼠标焦点位于osu!上, 不要移动!")
    while n != bg_num:
        n = bg_num_get()
        time.sleep(0.01)  # 越小消耗越大但越精准
        if i != n:
            print("[+] 进度: 已获取" + str(n) + "张服务器bg图")
            i = n
            e = 0  # 重置计数
        else:
            e += 1

        # 防呆措施
        if e >= 1000:  # 大约10s无进度
            # 声明退出virtual_key线程
            stop_threads = True
            # 腾空屏幕为显示log准备
            os.system("taskkill /F /IM osu!.exe > nul")
            with open("error.log", "w") as file:
                file.write('[Error] 请检查您的网络')
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
        file.write(req_new)
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

osuPath = osu_path + "\\osu!.exe"  # osu.exe 路径
bgPath = osu_path + "\\Data\\bg"  # bg文件夹 路径
bgTempPath = osu_path + "\\Data\\bg_temp"  # 跨驱动器的解决方案

# 配置检验
if not os.path.exists(osu_path + r'\Data'):
    print("[!] 错误: osu!路径配置有误,无法找到Data文件夹\n"
          "         请确保 [osu]path = xxx/osu! 路径有效")
    win32api.ShellExecute(0, 'open', osuWRS_path + r'\config.ini', '', '', 1)
    time.sleep(10)
    exit(1)

# 快速启动
if QUICK_START == 'on':
    win32api.ShellExecute(0, 'open', osuPath, '', '', 1)
# debugMode
if debugMode == 'on':
    bg_update()
# 基础判断
php_update, bg_max = php_update()
print(f"[!] bg可替换数量: {bg_max}张")
if bg_max < bg_num:
    print("[-] 错误: 替换bg数不应大于服务器所能提供的数量!")
    time.sleep(5)
    exit(1)

# 数据变化判断
if php_update == 0:  # seasonal background 更新后开始进行 bg更新
    print("[+] 状态: 无更新!")
    time.sleep(1)
    if QUICK_START != 1:
        win32api.ShellExecute(0, 'open', osuPath, '', '', 1)
else:
    # 杀死osu 当前启动的osu
    os.system("taskkill /F /IM osu!.exe > nul")
    # osu设置检测
    if check_set == 'on':
        print("[+] 状态: 正在检查游戏内设置")
        setting_check()
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
    thread_02 = Thread(target=virtual_key_v2)
    thread_01.start()
    # 给 bg_num = 1 的反应时间
    time.sleep(0.25)
    thread_02.start()
