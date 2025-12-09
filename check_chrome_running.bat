@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 크롬 디버깅 모드 실행 확인
echo ========================================
echo.

echo [1] 크롬 프로세스 확인...
echo.
tasklist /FI "IMAGENAME eq chrome.exe" /NH 2>nul | find /I "chrome.exe" >nul
if !errorlevel! == 0 (
    echo [실행 중] 크롬 프로세스가 실행 중입니다.
    echo.
    echo 실행 중인 크롬 프로세스:
    tasklist /FI "IMAGENAME eq chrome.exe" /FO TABLE
    echo.
    
    echo [2] 크롬 프로세스의 명령줄 인자 확인...
    echo (--remote-debugging-port=9222가 있어야 합니다)
    echo.
    wmic process where "name='chrome.exe'" get commandline /format:list 2>nul | findstr /i "remote-debugging-port"
    if !errorlevel! == 0 (
        echo.
        echo [발견] 디버깅 포트 인자가 발견되었습니다!
    ) else (
        echo.
        echo [경고] 디버깅 포트 인자를 찾을 수 없습니다!
        echo 크롬이 일반 모드로 실행 중일 수 있습니다.
        echo.
        echo 해결 방법:
        echo 1. 모든 크롬 창을 완전히 닫으세요
        echo 2. 작업 관리자에서 chrome.exe 프로세스를 모두 종료하세요
        echo 3. fix_chrome_debug.bat를 다시 실행하세요
    )
) else (
    echo [중지됨] 크롬 프로세스가 실행 중이지 않습니다.
)

echo.
echo [3] 포트 9222 확인...
echo.
netstat -ano | findstr ":9222"
if !errorlevel! == 0 (
    echo.
    echo [열림] 포트 9222가 사용 중입니다.
) else (
    echo [닫힘] 포트 9222가 사용 중이지 않습니다!
    echo 크롬이 디버깅 모드로 실행되지 않았습니다.
)

echo.
echo [4] 브라우저에서 직접 확인하세요:
echo.
echo   1. 크롬 브라우저를 엽니다
echo   2. 주소창에 입력: http://127.0.0.1:9222/json
echo   3. JSON 응답이 보이면 정상입니다
echo   4. 연결할 수 없다면 디버깅 모드가 실행되지 않은 것입니다
echo.

pause

