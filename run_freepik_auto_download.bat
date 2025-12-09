@echo off
chcp 65001 >nul
echo ========================================
echo Freepik 자동화 - Download 기능 포함
echo ========================================
echo.
echo 중요: 먼저 Chrome을 디버깅 모드로 실행해야 합니다!
echo start_chrome_debug.bat 파일을 실행하세요.
echo.
pause

python freepik_auto_simple_download.py

pause


