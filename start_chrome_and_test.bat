@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 크롬 디버깅 모드 실행 및 연결 테스트
echo ========================================
echo.

REM 크롬 경로 찾기
set "CHROME_PATH="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
)

if "!CHROME_PATH!"=="" (
    echo [오류] 크롬을 찾을 수 없습니다!
    pause
    exit /b 1
)

echo [1] 기존 크롬 프로세스 확인 중...
tasklist /FI "IMAGENAME eq chrome.exe" /NH 2>nul | find /I "chrome.exe" >nul
if !errorlevel! == 0 (
    echo [경고] 크롬이 이미 실행 중입니다.
    echo 모든 크롬 창을 닫고 다시 시도하세요.
    echo.
    echo 계속 진행하시겠습니까? (Y/N)
    set /p CONTINUE=
    if /i not "!CONTINUE!"=="Y" (
        exit /b 1
    )
)

echo.
echo [2] 크롬을 디버깅 모드로 실행 중...
echo 경로: !CHROME_PATH!
echo.
start "" "!CHROME_PATH!" --remote-debugging-port=9222

echo 크롬이 실행되었습니다.
echo 3초 대기 중... (크롬 초기화 대기)
timeout /t 3 /nobreak >nul

echo.
echo [3] 연결 테스트 중...
echo.

python quick_test_connection.py
if !errorlevel! == 0 (
    echo.
    echo ========================================
    echo 준비 완료!
    echo ========================================
    echo.
    echo 크롬이 디버깅 모드로 실행되었고 연결이 확인되었습니다.
    echo 이제 다른 스크립트를 실행할 수 있습니다.
    echo.
    echo 이 창을 닫지 마세요! (크롬이 종료됩니다)
    echo.
) else (
    echo.
    echo ========================================
    echo 연결 실패!
    echo ========================================
    echo.
    echo 크롬이 디버깅 모드로 실행되지 않았을 수 있습니다.
    echo 브라우저에서 http://127.0.0.1:9222/json 을 열어 확인하세요.
    echo.
)

pause




