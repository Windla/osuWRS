::作者主页:https://space.bilibili.com/358002685
::发布地址:https://github.com/Windla/OsuWRS

::读取config.ini
set /p osu_path=<".\config.ini"
::复制待替换图片(使用通配符)
copy ".\*.jpg" "%osu_path%\Data\"
::进入osu路径
cd /d "%osu_path%"

::获取权限
echo y|cacls .\Data\bg /t /p everyone:f

::替换图片(仅单文件)
::@echo off & setlocal enabledelayedexpansion
setlocal enabledelayedexpansion
 for /r ".\Data\bg" %%a in (*.jpg) do (
  set filename=%%~na
   del /s /q ".\Data\bg\*.jpg"
   copy ".\Data\bg.jpg" ".\Data\bg\!filename!.jpg"
   del /s /q ".\Data\bg.jpg"
 )

::只读权限
echo y|cacls .\Data\bg /t /p everyone:r
