::作者主页:https://space.bilibili.com/358002685
::发布地址:https://github.com/Windla/OsuWRS


::读取config.ini
set /p osu_path=<".\config.ini"
::进入osu路径
cd /d "%osu_path%"

::只读权限
echo y|cacls .\Data\bg /t /p everyone:r
