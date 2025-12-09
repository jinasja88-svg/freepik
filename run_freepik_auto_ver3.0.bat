@echo off
cd /d "%~dp0"
echo ========================================
echo Freepik 자동화 프로그램 실행 (ver3.0)
echo ========================================
echo.
echo 중요: 먼저 Chrome을 디버깅 모드로 실행해야 합니다!
echo.
echo 실행 순서:
echo 1. start_chrome_debug.bat 파일을 실행하세요
echo 2. Chrome에서 Freepik에 로그인하세요
echo 3. 이 파일을 실행하세요
echo.
echo ver3.0 기능:
echo - 64번 자동화 작업 (model 1-8 x clothes 1-8)
echo - 이미지 생성 완료 자동 대기
echo - 자동 다운로드 (파일명: {날짜시간}_model{번호}_clothes{번호}.png)
echo.
pause
python freepik_auto_simple_ver3.0.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo 오류가 발생했습니다!
    echo ========================================
    pause
)
pause

