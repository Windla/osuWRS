# -*- coding: utf-8 -*-
import os
import sys
import io

# 解决 Windows 终端中文乱码，必须在 logging 和其他输出之前
if sys.platform == 'win32':
    try:
        # 设置控制台代码页为 UTF-8
        os.system('chcp 65001 > nul')
        # 强制设置 stdout 和 stderr 编码为 utf-8
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)
    except:
        pass

import re
import time
import glob
import json
import hashlib
import logging
import configparser
import subprocess
import shutil
import webbrowser
import urllib.request
import ssl
from typing import List, Dict

# 日志配置：定义日志级别、格式和日期格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("osuWRS")

class OsuWRS:
    """osuWRS 主类，负责初始化配置、检查路径、同步背景及权限管理"""
    def __init__(self, config_path: str = 'config.ini'):
        self.version = '3.0.0'
        # 初始化阶段即确保配置文件的存在与加载
        self.ensure_config(config_path)
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')
        
        self.osu_path = self.config.get('osu', 'path', fallback=self.find_osu_path())
        self.quick_start = self.config.getboolean('osu', 'quickStart', fallback=True)
        self.overtime = self.config.getint('osuWRS', 'overtime', fallback=5)
        self.debug_mode = self.config.getboolean('osuWRS', 'debugMode', fallback=False)
        self.check_update_enabled = self.config.getboolean('osuWRS', 'checkUpdate', fallback=True)
        self.proxy_mode = self.config.get('osuWRS', 'proxy', fallback='off')
        self.check_set = self.config.getboolean('set', 'checkSet', fallback=False)
        self.auto_set = self.config.getboolean('set', 'autoSet', fallback=True)

        self.work_dir = os.getcwd()
        self.bg_dir = os.path.join(self.work_dir, 'bg')
        self.osu_exe = os.path.join(self.osu_path, 'osu!.exe')
        self.osu_data_bg = os.path.join(self.osu_path, 'Data', 'bg')
        
        # 确保本地存放自定义背景的目录存在
        if not os.path.exists(self.bg_dir):
            os.makedirs(self.bg_dir)
            
        # 代理环境配置
        if self.proxy_mode.lower() == 'off':
            os.environ['no_proxy'] = '*'
        elif self.proxy_mode.lower() == 'system':
            os.environ.pop('no_proxy', None)
            # 尝试通过环境变量实现系统代理
            for env_key in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
                if env_key in os.environ:
                     pass
        else:
            # 使用用户指定的具体代理地址
            os.environ.pop('no_proxy', None)
            os.environ['http_proxy'] = self.proxy_mode
            os.environ['https_proxy'] = self.proxy_mode

    def find_osu_path(self) -> str:
        """尝试自动寻找 osu! 安装路径，支持常见目录及注册表查询"""
        # 1. 尝试环境变量中的常见安装路径
        possible_paths = [
            os.path.join(os.environ.get('LocalAppData', ''), 'osu!'),
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'osu!'),
            os.path.join(os.environ.get('ProgramFiles', ''), 'osu!'),
        ]
        
        for path in possible_paths:
            if path and os.path.exists(os.path.join(path, 'osu!.exe')):
                return path
        
        # 2. 尝试通过 Windows 注册表获取安装关联路径
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"osu\DefaultIcon")
            val, _ = winreg.QueryValueEx(key, "")
            # 处理形如 "C:\path\to\osu!.exe,0" 的注册表值
            path = val.split(',')[0].strip('"')
            path = os.path.dirname(path)
            if os.path.exists(os.path.join(path, 'osu!.exe')):
                return path
        except Exception:
            pass
            
        return "" # 未找到路径则返回空

    def ensure_config(self, config_path: str):
        """检测并确保配置文件存在，若不存在则根据环境自动生成默认配置"""
        if os.path.exists(config_path):
            return

        logger.info(f"配置文件 {config_path} 不存在，正在生成默认配置...")
        osu_path = self.find_osu_path()
        
        content = f"""# 更新地址:  https://github.com/Windla/osuWRS
# 含有*标识的项目是必填项，其他根据自己需求修改即可

[osu]
# *osu!根目录
path = {osu_path}
# 快速启动 | on/off
quickStart = on

[osuWRS]
# 主程序当前版本号
version = {self.version}
# 连接ppy服务器超时时间 | 默认 5
overtime = 5
# 调试模式 请确保值为 'off' | on/off
debugMode = off
# 自动检查更新 | on/off
checkUpdate = on
# 代理设置 | off (直连), system (系统代理), 或指定地址(如 http://127.0.0.1:7890)
proxy = system

# 针对第一次打开, 配置成功后可全关 'off' (指[set]下的所有设置)
[set]
# 开启检测游戏内设置 | on/off
checkSet = on
# 自动修改游戏内设置 -> Always | on/off
autoSet = off
"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"已生成默认配置文件: {config_path}")
        except Exception as e:
            logger.error(f"生成配置文件失败: {e}")

    def check_config_settings(self):
        """检查并根据需要自动修改 osu! 游戏客户端的配置文件（.cfg），确保季节背景功能开启"""
        if not self.check_set:
            return

        cfgs = glob.glob(os.path.join(self.osu_path, 'osu!.*.cfg'))
        if not cfgs:
            logger.warning("未发现 osu! 用户配置文件，请确保路径正确。")
            return

        for cfg_path in cfgs:
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查 SeasonalBackgrounds 设置
                # 目标是 SeasonalBackgrounds = Always
                if 'SeasonalBackgrounds = Always' in content:
                    continue

                pattern = r'SeasonalBackgrounds\s*=\s*(Sometimes|Never)'
                if re.search(pattern, content):
                    logger.warning(f"发现设置项 SeasonalBackgrounds 不为 Always (文件: {os.path.basename(cfg_path)})")
                    if self.auto_set:
                        content = re.sub(pattern, 'SeasonalBackgrounds = Always', content)
                        with open(cfg_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info("已自动修改为 Always")
                    else:
                        logger.warning("请手动将游戏内季节背景设置为 Always，否则工具将无法正常工作。")
            except Exception as e:
                logger.error(f"处理配置文件 {cfg_path} 时出错: {e}")

    def set_title(self):
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(f"osuWRS")
        except:
            os.system(f"title osuWRS")
            
        print(f"""
 ██████╗ ███████╗██╗   ██╗██╗    ██╗██████╗ ███████╗
██╔═══██╗██╔════╝██║   ██║██║    ██║██╔══██╗██╔════╝
██║   ██║███████╗██║   ██║██║ █╗ ██║██████╔╝███████╗
██║   ██║╚════██║██║   ██║██║███╗██║██╔══██╗╚════██║
╚██████╔╝███████║╚██████╔╝╚███╔███╔╝██║  ██║███████║
 ╚═════╝ ╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝
                                    Version: {self.version}
        """)

    def check_update(self):
        """通过 GitHub API 检查是否有新版本 Release，并提示用户更新"""
        logger.info("正在检查更新...")
        api_url = "https://api.github.com/repos/Windla/osuWRS/releases/latest"
        
        # 创建一个不校验 SSL 证书的上下文（应对某些代理干扰）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            # 使用 API 获取最新版本信息
            req = urllib.request.Request(api_url)
            
            # 增加超时时间到 10s，应对握手慢的情况
            timeout = max(self.overtime, 10)
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            latest_tag = data['tag_name']
            latest_version = latest_tag.lstrip('v')
            
            # 版本号比较逻辑
            try:
                current_parts = [int(x) for x in self.version.split('.')]
                latest_parts = [int(x) for x in latest_version.split('.')]
            except ValueError:
                # 如果版本号格式不标准，简单字符串比较
                current_parts = self.version
                latest_parts = latest_version

            if latest_parts > current_parts:
                logger.info(f"发现新版本: {latest_tag} (当前: v{self.version})")
                print("\n" + "="*40)
                print(f"更新说明:\n{data['body']}")
                print("="*40 + "\n")
                
                logger.info(f"下载地址: {data['html_url']}")
                
                # 尝试询问用户
                try:
                    print("="*40)
                    choice = input("发现新版本，按回车键打开下载页面，或输入 n 跳过并继续运行: ").strip().lower()
                    if choice != 'n':
                        logger.info("正在打开下载页面...")
                        webbrowser.open(data['html_url'])
                    else:
                        logger.info("已跳过更新检查。")
                except Exception:
                    pass
            else:
                logger.info("当前已是最新版本。")
                
        except urllib.error.HTTPError as e:
            if e.code == 403:
                logger.warning("检查更新失败: GitHub API 访问频率受限 (403)。请稍后再试，或检查代理配置。")
            else:
                logger.warning(f"检查更新失败 (HTTP {e.code}): {e.reason}")
        except Exception as e:
            # 更新检查失败不应影响主程序运行
            logger.warning(f"检查更新失败: {e}")

    def check_osu_path(self):
        """检查 osu! 路径及其 Data 目录"""
        if not self.osu_path or not os.path.exists(self.osu_path):
            logger.error("未发现有效的 osu! 根目录。")
            logger.info("请打开 config.ini，在 [osu] 下方的 path = 后面填写你的 osu! 安装路径。")
            logger.info("例如: path = C:\\Users\\你的用户名\\AppData\\Local\\osu!")
            time.sleep(10)
            return False

        if not os.path.exists(self.osu_data_bg):
            # 尝试创建目录，如果 Data 存在但 bg 不存在
            data_dir = os.path.join(self.osu_path, 'Data')
            if os.path.exists(data_dir):
                os.makedirs(self.osu_data_bg, exist_ok=True)
                return True
            logger.error(f"无法找到 osu! Data 目录: {self.osu_data_bg}")
            logger.error("请检查 config.ini 中的 [osu]path 配置。")
            time.sleep(5)
            return False
        return True

    def get_seasonal_bgs(self) -> List[Dict[str, str]]:
        """从 osu! 官网 API 获取当前生效的季节性背景列表，并计算其 MD5 对应文件名"""
        api_url = "https://osu.ppy.sh/web/osu-getseasonal.php"
        headers = {'User-Agent': 'osu!'}
        
        try:
            logger.info("正在从 osu! 服务器同步背景信息...")
            
            # ssl_context = ssl.create_default_context()
            # ssl_context.check_hostname = False
            # ssl_context.verify_mode = ssl.CERT_NONE

            
            # req = urllib.request.Request(api_url, headers=headers)
            req = urllib.request.Request(api_url)
            timeout = max(self.overtime, 10)
            # with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()
                urls = json.loads(data)
            
            results = []
            for url in urls:
                md5_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
                file_name = f"online_background_{md5_hash}.jpg"
                results.append({
                    "url": url,
                    "filename": file_name
                })
            return results
        except Exception as e:
            logger.error(f"网络请求失败: {e}")
            return []

    def manage_permissions(self, lock=False):
        """管理 osu! Data/bg 目录的文件系统权限，通过 icacls 实现锁定/解锁"""
        # 使用 Windows icacls 命令修改权限
        # lock=True: 将目录设置为所有人只读 (R)，防止游戏运行时覆盖背景
        # lock=False: 将目录设置为所有人完全控制 (F)，允许脚本进行背景替换操作
        perm = 'R' if lock else 'F'
        # /grant:r 表示替换原有权限，/t 递归处理，/c 忽略错误继续，/q 安静模式
        cmd = f'icacls "{self.osu_data_bg}" /grant:r everyone:{perm} /t /c /q'
        try:
            subprocess.run(cmd, shell=True, capture_output=True)
        except Exception as e:
            logger.error(f"权限修改失败: {e}")

    def kill_osu(self):
        """关闭 osu! 以确保文件不被占用"""
        subprocess.run("taskkill /F /IM osu!.exe /T", shell=True, capture_output=True)

    def launch_osu(self):
        """启动 osu!"""
        if os.path.exists(self.osu_exe):
            try:
                # 尝试使用 win32api 如果存在 (为了更好的兼容性)
                import win32api
                win32api.ShellExecute(0, 'open', self.osu_exe, '', '', 1)
            except ImportError:
                # 否则使用标准库
                os.startfile(self.osu_exe)
        else:
            logger.error(f"找不到 osu!.exe: {self.osu_exe}")

    def run_replacement_cycle(self):
        """执行完整的替换周期：同步信息 -> 停止进程 -> 修改权限 -> 文件替换 -> 锁定权限 -> 启动游戏"""
        bgs = self.get_seasonal_bgs()
        if not bgs:
            logger.error("获取背景列表失败，请检查网络。")
            return

        # 检查本地待替换图片
        local_bgs = glob.glob(os.path.join(self.bg_dir, "*.*"))
        local_bgs = [f for f in local_bgs if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not local_bgs:
            logger.error(f"本地 bg/ 文件夹为空！请放入图片后再运行。")
            return

        # 判断是否需要更新
        # 兼容旧版本：清理 bg.php
        bg_php_path = os.path.join(self.work_dir, 'bg.php')
        if os.path.exists(bg_php_path):
            try:
                os.remove(bg_php_path)
            except:
                pass

        bg_cache_path = os.path.join(self.work_dir, 'bg.cache')
        current_filenames = [b['filename'] for b in bgs]
        
        needs_update = True
        if os.path.exists(bg_cache_path):
            try:
                with open(bg_cache_path, 'r', encoding='utf-8') as f:
                    cached_filenames = json.load(f)
                if cached_filenames == current_filenames and not self.debug_mode:
                    needs_update = False
            except Exception:
                needs_update = True
        
        if not needs_update:
            logger.info("背景列表未更新，无需操作。")
            if self.quick_start:
                self.launch_osu()
            return

        logger.info(f"检测到更新！服务器背景数: {len(bgs)}, 本地图片数: {len(local_bgs)}")
        
        # 1. 停止游戏
        self.kill_osu()
        time.sleep(0.5)

        # 2. 检查配置
        self.check_config_settings()

        # 3. 解锁权限
        self.manage_permissions(lock=False)

        # 3. 清理并替换
        # 先清理旧的
        old_files = glob.glob(os.path.join(self.osu_data_bg, "*.jpg"))
        for f in old_files:
            try: os.remove(f)
            except: pass

        # 写入新的
        for i, bg_info in enumerate(bgs):
            target_path = os.path.join(self.osu_data_bg, bg_info['filename'])
            source_path = local_bgs[i % len(local_bgs)]
            try:
                shutil.copy2(source_path, target_path)
                logger.info(f"已部署: {bg_info['filename']}")
            except Exception as e:
                logger.error(f"部署失败 {bg_info['filename']}: {e}")

        # 4. 锁定权限
        self.manage_permissions(lock=True)
        
        # 5. 保存状态
        try:
            with open(bg_cache_path, 'w', encoding='utf-8') as f:
                json.dump(current_filenames, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
            
        logger.info("替换完成，目录已锁定。")
        time.sleep(1)
        
        if self.quick_start:
            self.launch_osu()

    def run(self):
        self.set_title()
        
        # 启动时检查更新
        if self.check_update_enabled:
            self.check_update()
        
        if not self.check_osu_path():
            return
        
        try:
            self.run_replacement_cycle()
        except KeyboardInterrupt:
            logger.info("用户中断。")
        except Exception as e:
            logger.exception(f"运行时错误: {e}")
        
        logger.info("程序结束。")
        time.sleep(2)

if __name__ == "__main__":
    app = OsuWRS()
    app.run()
