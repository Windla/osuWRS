import os
import subprocess
import sys

def build():
    print("="*40)
    print("osuWRS PyInstaller 打包脚本")
    print("="*40)

    try:
        import PyInstaller
        print("已检测到 PyInstaller")
    except ImportError:
        print("未检测到 PyInstaller，正在尝试安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller 安装成功")
        except Exception as e:
            print(f"安装 PyInstaller 失败: {e}")
            return

    # PyInstaller 打包参数配置
    # --onefile: 将所有依赖打包成一个单独的 .exe 文件
    # --clean: 在打包前清理临时缓存
    # --name: 指定生成的可执行文件名
    # --distpath: 指定最终生成文件的存放目录
    # --workpath: 指定编译过程中的临时工作目录
    # --specpath: 指定 .spec 配置文件的存放目录
    cmd = [
        "pyinstaller",
        "--onefile",
        "--clean",
        "--name=osuWRS",
        "--distpath=dist",
        "--workpath=build",
        "--specpath=.",
        # 排除常见的大型但本项目未使用的库
        "--exclude-module=tkinter",
        "--exclude-module=unittest",
        "--exclude-module=pydoc",
        "--exclude-module=test",
        "osuWRS.py"
    ]

    print(f"执行打包命令: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        
        # 编译成功后，清理 PyInstaller 生成的辅助目录和文件
        print("正在清理临时构建文件...")
        import shutil
        if os.path.exists("build"):
            shutil.rmtree("build")
        if os.path.exists("osuWRS.spec"):
            os.remove("osuWRS.spec")
            
        print("\n" + "="*40)
        print("打包完成！")
        print(f"可执行文件位于: {os.path.join(os.getcwd(), 'dist', 'osuWRS.exe')}")
        print("="*40)
    except subprocess.CalledProcessError:
        print("\n打包过程中出错，请检查输出信息。")
    except Exception as e:
        print(f"\n发生未知错误: {e}")

if __name__ == "__main__":
    build()
