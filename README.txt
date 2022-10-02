作者主页:https://space.bilibili.com/358002685
发布地址:https://github.com/Windla/OsuWRS
教程地址:https://www.bilibili.com/video/BV1eq4y1g7sT  (这其实是旧教程)

使用前说明:
待替换数量不能超过服务器bg数量, 否则死循环!
最多不要超过25张(看运气)
如果想要一劳永逸,那就把 OsuWRS.exe/OsuWRS.py 当作osu!的启动器,osuWRS会自动检测ppy的更新

*使用方法:
1.将osu的绝对路径放入config.ini(见获取方法)
2.将待替换图片改为 bg.jpg 并放入bg目录下
  (可选,但是一定要jpg格式)
3.确保osu设置成下面这样子
  (Seasonal backgrounds - Always)
4.运行osuWRS.exe
  (如果有python环境,直接运行 osuWRS.py 也可以)


获取方法:
osu - 设置(Settings) - 打开osu!所在文件夹 - 复制地址栏 - 粘贴至config.ini


可以动的文件列表:
bg.jpg
config.ini


Q&A:
Q1:osu更新后,替换失效
A1:运行 osuWRS.exe 或者 - 手动触发更新 -.bat + osuWRS.exe

Q2:修改失败
A2:请查看config.ini是否只有一行,或者前后空格是否删除
   不要删除bg.php  如果删除了,请自行创建一个空文件


贡献者:
PercyDan
https://space.bilibili.com/306137911


使用到的语言:
python
cmd
