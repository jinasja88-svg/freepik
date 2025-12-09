@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo 크롬 연결 테스트 (상세 진단)
echo ========================================
echo.
echo JSON 응답을 받았다면 크롬 디버깅 모드는 정상입니다.
echo 이제 Playwright 연결을 테스트합니다.
echo.
pause
python test_connection_detailed.py
pause

