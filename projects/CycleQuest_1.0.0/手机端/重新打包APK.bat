@echo off
chcp 65001 >nul
set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
cd /d "%USERPROFILE%\AndroidStudioProjects\CycleQuestMobile"

echo 正在打包手机端 APK ...
call gradlew.bat assembleDebug
if errorlevel 1 (
  echo 打包失败，请检查上面的报错。
  pause
  exit /b 1
)

copy /Y "app\build\outputs\apk\debug\app-debug.apk" "%~dp0CycleQuestMobile.apk" >nul
echo.
echo 打包完成：%~dp0CycleQuestMobile.apk
pause
