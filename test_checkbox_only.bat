@echo off
chcp 65001 >nul
echo ========================================
echo Freepik 체크박스 기능 테스트
echo ========================================
echo.
echo 중요: 먼저 Chrome을 디버깅 모드로 실행해야 합니다!
echo start_chrome_debug.bat 파일을 실행하세요.
echo.
echo 이미 생성된 이미지가 있는 페이지로 이동하세요.
echo.
pause

python test_checkbox_only.py

pause


