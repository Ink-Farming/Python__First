@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 正在打包 CycleQuest 2.0 ...
pyinstaller --noconfirm --clean --onefile --windowed --name CycleQuest ^
  --add-data "shell.html;." ^
  --add-data "app.html;." ^
  --add-data "report;report" ^
  server.py

if exist "dist\CycleQuest.exe" (
  echo.
  echo 打包完成：%cd%\dist\CycleQuest.exe
  echo 把它复制到上一级目录，覆盖旧 exe；不要覆盖 app_data.json。
) else (
  echo.
  echo 打包失败，请检查上面的报错。
)
pause
