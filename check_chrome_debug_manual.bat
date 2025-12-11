@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 크롬 디버깅 모드 수동 확인 도구
echo ========================================
echo.

echo [1] 크롬 프로세스 확인 중...
tasklist /FI "IMAGENAME eq chrome.exe" /NH 2>nul | find /I "chrome.exe" >nul
if !errorlevel! == 0 (
    echo [실행 중] 크롬 프로세스가 실행 중입니다.
    echo.
    tasklist /FI "IMAGENAME eq chrome.exe" /FO TABLE
    echo.
) else (
    echo [중지됨] 크롬 프로세스가 실행 중이지 않습니다.
    echo.
)

echo [2] 포트 9222 확인 중...
echo.
echo 방법 1: netstat 사용
netstat -ano | findstr ":9222"
if !errorlevel! == 0 (
    echo [열림] 포트 9222가 사용 중입니다.
) else (
    echo [닫힘] 포트 9222가 사용 중이지 않습니다.
)
echo.

echo 방법 2: curl 사용 (있는 경우)
curl -s http://127.0.0.1:9222/json 2>nul
if !errorlevel! == 0 (
    echo [열림] 포트 9222가 열려있고 응답합니다.
) else (
    echo [닫힘] 포트 9222에 연결할 수 없습니다.
)
echo.

echo [3] 크롬 경로 확인 중...
set "CHROME_PATH="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
    echo [발견] 크롬 경로: !CHROME_PATH!
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    echo [발견] 크롬 경로: !CHROME_PATH!
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
    echo [발견] 크롬 경로: !CHROME_PATH!
) else (
    echo [오류] 크롬을 찾을 수 없습니다!
)
echo.

echo [4] 수동 실행 테스트
echo.
if not "!CHROME_PATH!"=="" (
    echo 다음 명령어로 크롬을 수동으로 실행해보세요:
    echo.
    echo   "!CHROME_PATH!" --remote-debugging-port=9222
    echo.
    echo 수동 실행하시겠습니까? (Y/N)
    set /p MANUAL_TEST=
    if /i "!MANUAL_TEST!"=="Y" (
        echo.
        echo 크롬을 디버깅 모드로 실행합니다...
        echo 이 창을 닫지 마세요!
        echo.
        start "" "!CHROME_PATH!" --remote-debugging-port=9222
        timeout /t 3 /nobreak >nul
        echo.
        echo 크롬이 실행되었습니다.
        echo 브라우저에서 http://127.0.0.1:9222/json 을 열어보세요.
        echo JSON 응답이 보이면 디버깅 모드가 정상 작동 중입니다.
        echo.
        pause
    )
) else (
    echo 크롬 경로를 찾을 수 없어 수동 실행을 할 수 없습니다.
)
echo.

echo [5] 방화벽 확인
echo.
echo Windows 방화벽이 포트 9222를 차단하고 있는지 확인하세요.
echo.
echo 확인 방법:
echo   1. Windows 설정 ^> 네트워크 및 인터넷 ^> Windows 방화벽
echo   2. 고급 설정 ^> 인바운드 규칙 확인
echo.

echo ========================================
echo 진단 완료
echo ========================================
pause




