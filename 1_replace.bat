::作者主页:https://space.bilibili.com/358002685
::发布地址:https://github.com/Windla/OsuWRS


::读取config.ini
set /p osu_path=<".\config.ini"
::创建bg临时文件夹
md %osu_path%\Data\bg_temp

::复制待替换图片(使用通配符)(多张bg的准备)
::copy ".\bg\*.jpg" "%osu_path%\Data\bg_temp"
::复制待替换图片(不使用通配符)
copy ".\bg\bg.jpg" "%osu_path%\Data\bg_temp"

::进入osu路径
cd /d "%osu_path%"

::获取权限
echo y|cacls .\Data\bg /t /p everyone:f

::替换图片(仅单文件)(程序能跑就行了)
::@echo off & setlocal enabledelayedexpansion
setlocal enabledelayedexpansion
 for /r ".\Data\bg" %%a in (*.jpg) do (
  set filename=%%~na
   del /s /q ".\Data\bg\*.jpg"
   copy ".\Data\bg_temp\bg.jpg" ".\Data\bg\!filename!.jpg"
   del /s /q ".\Data\bg_temp\bg.jpg"
 )

::删除bg临时文件夹
rd /s /q ".\Data\bg_temp
::只读权限
echo y|cacls .\Data\bg /t /p everyone:r
