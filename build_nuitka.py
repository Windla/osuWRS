import os
import subprocess
import sys

def build_nuitka():
    print("="*40)
    print("osuWRS Nuitka 打包脚本")
    print("="*40)

    # 自动将 Nuitka 缓存目录设置为当前目录下的 .cache/nuitka 文件夹
    # 这样可以避免占用 C 盘空间，且所有依赖都保存在项目目录内
    cache_dir = os.path.join(os.getcwd(), ".cache", "nuitka")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    os.environ["NUITKA_CACHE_DIR"] = cache_dir
    print(f"已将 Nuitka 缓存目录设置为: {cache_dir}")

    try:
        import nuitka
        print("已检测到 Nuitka")
    except ImportError:
        print("未检测到 Nuitka，正在尝试安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka", "zstandard"])
            print("Nuitka 安装成功")
        except Exception as e:
            print(f"安装 Nuitka 失败: {e}")
            return

    # Nuitka 打包参数配置
    # --onefile: 生成单文件可执行程序
    # --standalone: 独立运行模式，包含所有必要运行库
    # --remove-output: 打包完成后自动删除临时生成的构建目录
    # --windows-console-mode=force: 强制程序运行时显示控制台窗口
    # --disable-plugin=tk-inter: 禁用不需要的 tkinter 插件以减小体积
    # --output-dir: 指定输出文件的目录
    # --output-filename: 指定生成的文件名
    cmd = [
        sys.executable,
        "-m", "nuitka",
        "--onefile",
        "--standalone",
        "--remove-output",
        "--windows-console-mode=force",
        "--disable-plugin=tk-inter",
        "--output-dir=dist",
        "--output-filename=osuWRS",
        "--assume-yes-for-downloads", # 自动同意可能需要的环境下载
        "--mingw64",                 # 强制使用 MinGW64 编译器
        "osuWRS.py"
    ]

    print(f"执行命令: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)

        # 编译成功后进行额外清理 (处理 Nuitka 在某些环境下残留的辅助目录)
        print("正在进行收尾清理...")
        import shutil
        build_dir = os.path.join("dist", "osuWRS.build")
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        dist_inner = os.path.join("dist", "osuWRS.dist")
        if os.path.exists(dist_inner):
            shutil.rmtree(dist_inner)

        print("\n" + "="*40)
        print("打包完成！")
        print(f"可执行文件位于: {os.path.join(os.getcwd(), 'dist', 'osuWRS.exe')}")
        print("="*40)
    except subprocess.CalledProcessError:
        print("\n打包过程中出错，请检查输出信息。")
    except Exception as e:
        print(f"\n发生未知错误: {e}")

if __name__ == "__main__":
    build_nuitka()
