@echo off
echo 크롬 디버깅 모드로 실행 중...
echo.
echo 주의: 모든 크롬 창을 먼저 닫아주세요!
echo.
pause

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

pause


