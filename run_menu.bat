@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:menu
cls
echo ========================================
echo Freepik 자동화 도구 메뉴
echo ========================================
echo.
echo [1] 크롬 디버깅 모드 실행 및 연결 테스트
echo [2] Freepik 자동화 실행 (ver2.2)
echo [3] 다운로드 기능 테스트
echo [4] 체크박스 테스트
echo [5] 연결 상태 확인
echo [6] 종료
echo.
echo ========================================
set /p choice=선택하세요 (1-6): 

if "%choice%"=="1" goto start_chrome
if "%choice%"=="2" goto run_ver22
if "%choice%"=="3" goto test_download
if "%choice%"=="4" goto test_checkbox
if "%choice%"=="5" goto test_connection
if "%choice%"=="6" goto end

echo 잘못된 선택입니다. 다시 선택해주세요.
timeout /t 2 /nobreak >nul
goto menu

:start_chrome
cls
echo ========================================
echo 크롬 디버깅 모드 실행 및 연결 테스트
echo ========================================
echo.
call start_chrome_and_test.bat
goto menu

:run_ver22
cls
echo ========================================
echo Freepik 자동화 실행 (ver2.2)
echo ========================================
echo.
echo 중요: 먼저 크롬을 디버깅 모드로 실행해야 합니다!
echo 메뉴에서 [1]을 선택하여 크롬을 실행하세요.
echo.
pause
python freepik_auto_simple_ver2.2.py
pause
goto menu

:test_download
cls
echo ========================================
echo 다운로드 기능 테스트
echo ========================================
echo.
echo 중요: 먼저 크롬을 디버깅 모드로 실행해야 합니다!
echo 이미 생성된 이미지가 있는 페이지로 이동하세요.
echo.
pause
python test_download_only.py
pause
goto menu

:test_checkbox
cls
echo ========================================
echo 체크박스 테스트
echo ========================================
echo.
echo 중요: 먼저 크롬을 디버깅 모드로 실행해야 합니다!
echo 이미 생성된 이미지가 있는 페이지로 이동하세요.
echo.
pause
python test_checkbox_only.py
pause
goto menu

:test_connection
cls
echo ========================================
echo 연결 상태 확인
echo ========================================
echo.
python quick_test_connection.py
pause
goto menu

:end
echo.
echo 프로그램을 종료합니다.
timeout /t 1 /nobreak >nul
exit /b 0




