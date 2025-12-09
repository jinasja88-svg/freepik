@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 크롬 디버깅 모드로 실행
echo ========================================
echo.
echo 주의: 모든 크롬 창을 먼저 닫아주세요!
echo.
pause

echo.
echo [1/4] 크롬 경로 확인 중...

REM 여러 가능한 크롬 경로 확인
set "CHROME_PATH="
set CHROME_FOUND=0

set "TEST_PATH1=C:\Program Files\Google\Chrome\Application\chrome.exe"
if exist "!TEST_PATH1!" (
    set "CHROME_PATH=!TEST_PATH1!"
    set CHROME_FOUND=1
    echo [OK] 크롬 경로 발견: !CHROME_PATH!
    goto :found_chrome
)

set "TEST_PATH2=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if exist "!TEST_PATH2!" (
    set "CHROME_PATH=!TEST_PATH2!"
    set CHROME_FOUND=1
    echo [OK] 크롬 경로 발견: !CHROME_PATH!
    goto :found_chrome
)

REM 사용자 프로필 경로도 확인
set "TEST_PATH3=!LOCALAPPDATA!\Google\Chrome\Application\chrome.exe"
if exist "!TEST_PATH3!" (
    set "CHROME_PATH=!TEST_PATH3!"
    set CHROME_FOUND=1
    echo [OK] 크롬 경로 발견: !CHROME_PATH!
    goto :found_chrome
)

echo [ERROR] 크롬을 찾을 수 없습니다!
echo.
echo 다음 경로에서 크롬을 찾을 수 없습니다:
echo   - !TEST_PATH1!
echo   - !TEST_PATH2!
echo   - !TEST_PATH3!
echo.
echo 크롬이 설치되어 있는지 확인해주세요.
echo.
pause
exit /b 1

:found_chrome
if "!CHROME_PATH!"=="" (
    echo [ERROR] 크롬 경로가 설정되지 않았습니다!
    pause
    exit /b 1
)

echo [OK] 크롬 경로: !CHROME_PATH!
echo.
echo [2/4] 포트 9222 사용 확인 중...
REM 간단한 포트 확인 (curl 사용, 없으면 건너뜀)
curl -s http://127.0.0.1:9222/json >nul 2>&1
if !errorlevel! == 0 (
    echo [WARNING] 포트 9222가 이미 사용 중입니다!
    echo   다른 크롬 인스턴스가 실행 중일 수 있습니다.
    echo   작업 관리자에서 chrome.exe를 모두 종료해주세요.
    echo.
    echo 계속 진행하시겠습니까? (Y/N)
    set /p CONTINUE=
    if /i not "!CONTINUE!"=="Y" (
        echo 취소되었습니다.
        pause
        exit /b 1
    )
) else (
    echo [OK] 포트 9222 사용 가능 (또는 확인 불가)
)

echo.
echo [3/4] 기존 크롬 프로세스 확인 중...
REM tasklist 명령이 빠르게 실행되도록 간단한 방법 사용
tasklist /FI "IMAGENAME eq chrome.exe" /NH 2>nul | find /I "chrome.exe" >nul
if !errorlevel! == 0 (
    echo [WARNING] 크롬 프로세스가 실행 중입니다!
    echo   모든 크롬 창을 닫아주세요.
    echo.
    echo 계속 진행하시겠습니까? (Y/N)
    set /p CONTINUE=
    if /i not "!CONTINUE!"=="Y" (
        echo 취소되었습니다.
        pause
        exit /b 1
    )
) else (
    echo [OK] 크롬 프로세스 없음
)

echo.
echo [4/4] 크롬을 디버깅 모드로 실행합니다...
echo.
echo 실행 명령:
echo   "!CHROME_PATH!" --remote-debugging-port=9222
echo.
echo ========================================
echo 중요: 이 창을 닫지 마세요!
echo 크롬이 열리면 Freepik에 로그인하세요.
echo ========================================
echo.
pause

echo.
echo 크롬 실행 중...
echo 경로: !CHROME_PATH!
echo.
echo ========================================
echo 중요: 이 창을 닫지 마세요!
echo 크롬이 실행 중입니다.
echo ========================================
echo.
start "" "!CHROME_PATH!" --remote-debugging-port=9222

REM 크롬이 시작될 때까지 대기
timeout /t 3 /nobreak >nul

REM 연결 확인
echo 연결 확인 중...
python quick_test_connection.py >nul 2>&1
if !errorlevel! == 0 (
    echo [OK] 크롬 디버깅 모드 연결 성공!
    echo.
    echo 크롬이 정상적으로 실행되었습니다.
    echo 이 창을 닫으면 크롬도 종료됩니다.
    echo.
) else (
    echo [경고] 연결 확인 실패. 크롬이 아직 초기화 중일 수 있습니다.
    echo 브라우저에서 http://127.0.0.1:9222/json 을 열어 확인하세요.
    echo.
)

echo ========================================
echo 크롬이 실행 중입니다.
echo 이 창을 닫지 마세요!
echo ========================================
echo.
pause


