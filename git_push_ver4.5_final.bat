@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================
echo Git 푸시 및 태그 생성 스크립트
echo ============================================

echo.
echo 1. 변경사항 추가...
git add .

echo.
echo 2. 커밋...
git commit -m "ver4.5_final: GUI 개선, 중지 기능 강화, 지정모드만 표시, 로그 창 추가"

echo.
echo 3. 푸시...
git push

echo.
echo 4. 태그 생성 (ver4.5_final)...
git tag ver4.5_final

echo.
echo 5. 태그 푸시...
git push origin ver4.5_final

echo.
echo 완료!
pause

