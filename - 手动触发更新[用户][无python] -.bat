::如果遇到更新失败,就运行这个脚本


::删除bg.php
del /s /q "bg.php"
::创建bg.php
type nul>bg.php
::触发更新
start "" "2_update.bat"

::打开osuWRS
start "" "osuWRS.exe"
