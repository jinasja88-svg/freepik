@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 크롬 디버깅 모드 실행 (깨끗한 프로필)
echo ========================================
echo.

REM 모든 크롬 프로세스 종료
echo [1] 모든 크롬 프로세스 종료 중...
tasklist /FI "IMAGENAME eq chrome.exe" /NH 2>nul | find /I "chrome.exe" >nul
if !errorlevel! == 0 (
    echo 크롬 프로세스를 강제 종료합니다...
    taskkill /F /IM chrome.exe /T >nul 2>&1
    timeout /t 3 /nobreak >nul
    echo 완료.
) else (
    echo 크롬 프로세스가 없습니다.
)
echo.

REM 포트 9222 확인 및 정리
echo [2] 포트 9222 확인 중...
netstat -ano | findstr ":9222" >nul
if !errorlevel! == 0 (
    echo 포트 9222를 사용하는 프로세스를 종료합니다...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9222"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
    echo 완료.
) else (
    echo 포트 9222가 비어있습니다.
)
echo.

REM 크롬 경로 찾기
echo [3] 크롬 경로 확인 중...
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

echo [OK] 크롬 경로: !CHROME_PATH!
echo.

REM 임시 프로필 디렉토리 생성
set "TEMP_PROFILE=%TEMP%\chrome_debug_profile_%RANDOM%"
echo [4] 임시 프로필 디렉토리 생성: !TEMP_PROFILE!
if not exist "!TEMP_PROFILE!" mkdir "!TEMP_PROFILE!"
echo.

REM 크롬 실행
echo [5] 크롬을 디버깅 모드로 실행 중...
echo.
echo 실행 명령:
echo   "!CHROME_PATH!" --remote-debugging-port=9222 --user-data-dir="!TEMP_PROFILE!"
echo.
echo ========================================
echo 중요: 이 창을 닫지 마세요!
echo 크롬이 실행 중입니다.
echo ========================================
echo.
start "" "!CHROME_PATH!" --remote-debugging-port=9222 --user-data-dir="!TEMP_PROFILE!"

echo 크롬이 실행되었습니다.
echo 10초 대기 중... (크롬 초기화 및 디버깅 포트 열림 대기)
timeout /t 10 /nobreak >nul
echo.

REM 포트 확인
echo [6] 디버깅 포트 확인 중...
netstat -ano | findstr ":9222" >nul
if !errorlevel! == 0 (
    echo [OK] 포트 9222가 열려있습니다!
    netstat -ano | findstr ":9222"
    echo.
) else (
    echo [경고] 포트 9222가 아직 열리지 않았습니다.
    echo 5초 더 대기 중...
    timeout /t 5 /nobreak >nul
    netstat -ano | findstr ":9222" >nul
    if !errorlevel! == 0 (
        echo [OK] 포트 9222가 이제 열려있습니다!
    ) else (
        echo [오류] 포트 9222가 여전히 열리지 않았습니다!
        echo.
        echo 수동 확인:
        echo 1. 크롬 브라우저 주소창에 입력: http://127.0.0.1:9222/json
        echo 2. JSON 응답이 보이면 정상입니다.
        echo 3. 연결할 수 없으면 크롬이 디버깅 모드로 실행되지 않은 것입니다.
        echo.
    )
)
echo.

REM 연결 테스트
echo [7] 연결 테스트 중...
echo.
python quick_test_connection.py
if !errorlevel! == 0 (
    echo.
    echo ========================================
    echo 성공! 크롬이 디버깅 모드로 실행되었습니다.
    echo ========================================
    echo.
    echo 이제 다른 스크립트를 실행할 수 있습니다.
    echo 이 창을 닫지 마세요! (크롬이 종료됩니다)
    echo.
) else (
    echo.
    echo ========================================
    echo 연결 실패!
    echo ========================================
    echo.
    echo 수동 확인:
    echo 1. 크롬 브라우저 주소창에 입력: http://127.0.0.1:9222/json
    echo 2. JSON 응답이 보이면 정상입니다.
    echo 3. 연결할 수 없으면 check_chrome_running.bat를 실행하여 확인하세요.
    echo.
)

pause




