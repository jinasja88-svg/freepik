@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 크롬 디버깅 모드 강제 재시작
echo ========================================
echo.

echo [1] 모든 크롬 프로세스 종료 중...
tasklist /FI "IMAGENAME eq chrome.exe" /NH 2>nul | find /I "chrome.exe" >nul
if !errorlevel! == 0 (
    echo 크롬 프로세스를 종료합니다...
    taskkill /F /IM chrome.exe /T >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo 완료.
) else (
    echo 크롬 프로세스가 없습니다.
)
echo.

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

echo [4] 크롬을 디버깅 모드로 실행 중...
echo.
echo 중요: 기존 크롬 프로세스와 충돌을 피하기 위해
echo 임시 사용자 프로필로 실행합니다.
echo.
set "TEMP_PROFILE=%TEMP%\chrome_debug_profile"
if not exist "!TEMP_PROFILE!" mkdir "!TEMP_PROFILE!"

echo 명령: "!CHROME_PATH!" --remote-debugging-port=9222 --user-data-dir="!TEMP_PROFILE!"
echo.
start "" "!CHROME_PATH!" --remote-debugging-port=9222 --user-data-dir="!TEMP_PROFILE!"

echo 크롬이 실행되었습니다.
echo 10초 대기 중... (크롬 초기화 및 디버깅 포트 열림 대기)
timeout /t 10 /nobreak >nul
echo.

echo [5] 디버깅 포트 확인 중...
echo.
netstat -ano | findstr ":9222" >nul
if !errorlevel! == 0 (
    echo [OK] 포트 9222가 열려있습니다.
    netstat -ano | findstr ":9222"
    echo.
) else (
    echo [경고] 포트 9222가 아직 열리지 않았습니다.
    echo 크롬이 완전히 초기화될 때까지 더 기다립니다...
    timeout /t 5 /nobreak >nul
    netstat -ano | findstr ":9222" >nul
    if !errorlevel! == 0 (
        echo [OK] 포트 9222가 이제 열려있습니다.
    ) else (
        echo [오류] 포트 9222가 여전히 열리지 않았습니다!
        echo.
        echo 크롬이 디버깅 모드로 실행되지 않았을 수 있습니다.
        echo.
        echo 수동 확인:
        echo 1. 크롬 브라우저 주소창에 입력: http://127.0.0.1:9222/json
        echo 2. JSON 응답이 보이면 정상, 연결할 수 없으면 디버깅 모드 미실행
        echo.
        pause
        exit /b 1
    )
)
echo.

echo [6] 연결 확인 중...
echo.
python quick_test_connection.py
if !errorlevel! == 0 (
    echo.
    echo ========================================
    echo 성공! 크롬이 디버깅 모드로 실행되었습니다.
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 연결 실패!
    echo ========================================
    echo.
    echo 수동 확인:
    echo 1. 크롬이 열렸는지 확인
    echo 2. 브라우저 주소창에 입력: http://127.0.0.1:9222/json
    echo 3. JSON 응답이 보이면 정상입니다.
    echo.
)

pause

