@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Freepik 다운로드 ver1.1 실행
echo ========================================
echo.
echo 중요: 먼저 Chrome을 디버깅 모드로 실행해야 합니다!
echo.
echo 실행 순서:
echo 1. fix_chrome_debug.bat 실행 (크롬 디버깅 모드)
echo 2. Freepik에 로그인
echo 3. 이미 생성된 이미지가 있는 페이지로 이동
echo 4. 이 파일 실행
echo.
pause

echo.
echo Python 스크립트 실행 중...
echo.

python freepik_download_ver1.1.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo 오류 발생!
    echo ========================================
    echo.
    echo Python 스크립트 실행 중 오류가 발생했습니다.
    echo 위의 오류 메시지를 확인하세요.
    echo.
)

pause

