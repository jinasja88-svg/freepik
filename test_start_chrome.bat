@echo off
chcp 65001 >nul
echo ========================================
echo 크롬 경로 테스트
echo ========================================
echo.

echo [테스트 1] 표준 경로 확인...
set "TEST_PATH1=C:\Program Files\Google\Chrome\Application\chrome.exe"
if exist "%TEST_PATH1%" (
    echo [OK] %TEST_PATH1%
) else (
    echo [FAIL] %TEST_PATH1%
)

set "TEST_PATH2=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if exist "%TEST_PATH2%" (
    echo [OK] %TEST_PATH2%
) else (
    echo [FAIL] %TEST_PATH2%
)

echo.
echo [테스트 2] 사용자 프로필 경로 확인...
set "TEST_PATH3=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
if exist "%TEST_PATH3%" (
    echo [OK] %TEST_PATH3%
) else (
    echo [FAIL] %TEST_PATH3%
)

echo.
echo [테스트 3] where 명령으로 크롬 찾기...
where chrome.exe 2>nul
if %errorlevel% == 0 (
    echo [OK] chrome.exe를 PATH에서 찾았습니다.
) else (
    echo [FAIL] chrome.exe를 PATH에서 찾을 수 없습니다.
)

echo.
echo [테스트 4] 크롬 프로세스 확인...
tasklist /FI "IMAGENAME eq chrome.exe" 2>nul | find /I "chrome.exe" >nul
if %errorlevel% == 0 (
    echo [WARNING] 크롬 프로세스가 실행 중입니다!
    tasklist /FI "IMAGENAME eq chrome.exe"
) else (
    echo [OK] 크롬 프로세스 없음
)

echo.
echo [테스트 5] 포트 9222 확인...
netstat -ano | findstr :9222 >nul
if %errorlevel% == 0 (
    echo [WARNING] 포트 9222가 사용 중입니다!
    netstat -ano | findstr :9222
) else (
    echo [OK] 포트 9222 사용 가능
)

echo.
echo ========================================
echo 테스트 완료
echo ========================================
pause

