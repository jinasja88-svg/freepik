@echo off
cd /d "%~dp0"
echo ========================================
echo Freepik 자동화 프로그램 실행 (ver2.2)
echo ========================================
echo.
echo 중요: 먼저 Chrome을 디버깅 모드로 실행해야 합니다!
echo.
echo 실행 순서:
echo 1. start_chrome_debug.bat 파일을 실행하세요
echo 2. Chrome에서 Freepik에 로그인하세요
echo 3. 이 파일을 실행하세요
echo.
pause
python freepik_auto_simple_ver2.2.py
pause


