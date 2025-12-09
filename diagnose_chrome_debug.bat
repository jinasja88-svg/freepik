@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 크롬 디버깅 모드 진단 도구
echo ========================================
echo.

echo [1] 크롬 프로세스 확인 중...
echo.
tasklist /FI "IMAGENAME eq chrome.exe" /NH 2>nul | find /I "chrome.exe" >nul
if !errorlevel! == 0 (
    echo [실행 중] 크롬 프로세스가 실행 중입니다.
    echo.
    echo 실행 중인 크롬 프로세스 목록:
    tasklist /FI "IMAGENAME eq chrome.exe" /FO TABLE
    echo.
    
    echo [중요] 크롬 프로세스의 명령줄 인자 확인:
    echo (--remote-debugging-port=9222가 있어야 합니다)
    echo.
    wmic process where "name='chrome.exe'" get commandline 2>nul | findstr /i "debugging"
    if !errorlevel! == 0 (
        echo [발견] 디버깅 포트 인자가 발견되었습니다!
    ) else (
        echo [경고] 디버깅 포트 인자를 찾을 수 없습니다!
        echo 크롬이 일반 모드로 실행 중일 수 있습니다.
    )
    echo.
) else (
    echo [중지됨] 크롬 프로세스가 실행 중이지 않습니다.
    echo.
)

echo [2] 포트 9222 확인 중...
echo.
netstat -ano | findstr ":9222" >nul
if !errorlevel! == 0 (
    echo [열림] 포트 9222가 사용 중입니다:
    netstat -ano | findstr ":9222"
    echo.
) else (
    echo [닫힘] 포트 9222가 사용 중이지 않습니다!
    echo 크롬이 디버깅 모드로 실행되지 않았을 수 있습니다.
    echo.
)

echo [3] HTTP 연결 테스트 중...
echo.
echo 방법 1: curl 사용
curl -s http://127.0.0.1:9222/json 2>nul
if !errorlevel! == 0 (
    echo [성공] 포트 9222에 HTTP 연결 성공!
) else (
    echo [실패] 포트 9222에 HTTP 연결 실패!
)
echo.

echo 방법 2: PowerShell 사용
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:9222/json' -TimeoutSec 2 -UseBasicParsing; Write-Host '[성공] 포트 9222에 HTTP 연결 성공!' } catch { Write-Host '[실패] 포트 9222에 HTTP 연결 실패!' }" 2>nul
echo.

echo [4] 해결 방법
echo.
echo 만약 크롬이 디버깅 모드로 실행되지 않았다면:
echo.
echo 1. 모든 크롬 창을 완전히 닫으세요 (작업 관리자에서 chrome.exe 모두 종료)
echo 2. start_chrome_debug.bat 또는 start_chrome_and_test.bat 실행
echo 3. 또는 수동 실행:
echo    "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
echo.
echo 4. 크롬이 열리면 브라우저 주소창에 입력:
echo    http://127.0.0.1:9222/json
echo    (JSON 응답이 보이면 정상)
echo.

echo ========================================
echo 진단 완료
echo ========================================
pause

