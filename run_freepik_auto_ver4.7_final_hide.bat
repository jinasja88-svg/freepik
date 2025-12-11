@echo off
cd /d "%~dp0"
mode con: cols=70 lines=20
title Freepik 자동화 ver4.7_final_hide
echo ========================================
echo Freepik 자동화 프로그램 실행 (ver4.7_final_hide)
echo ========================================
echo.
echo 중요: 먼저 Chrome을 디버깅 모드로 실행해야 합니다!
echo.
echo 실행 순서:
echo 1. start_chrome_debug.bat 파일을 실행하세요
echo 2. Chrome에서 Freepik에 로그인하세요
echo 3. 크롬 창을 최소화하세요 (선택사항)
echo 4. 이 파일을 실행하세요
echo.
echo ver4.7_final_hide 기능:
echo - GUI 인터페이스 제공
echo - 지정모드: 파일 직접 선택하여 합성
echo - 프롬프트 입력 및 프롬프트 리스트 (1~10번 저장/불러오기)
echo - 이미지 생성 완료 자동 대기 (45초 고정 대기)
echo - 자동 다운로드 (지정 폴더에 저장)
echo - 백그라운드 파일 업로드 (파일 다이얼로그 없이)
echo.
pause
python freepik_auto_simple_ver4.7_final_hide.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo 오류가 발생했습니다!
    echo ========================================
    pause
)
pause

