@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================
echo Git 푸시 스크립트 (ver4.6)
echo ============================================

echo.
echo 1. 변경사항 추가...
git add freepik_auto_simple_ver4.6.* build_exe_ver4.6.bat

echo.
echo 2. 커밋...
git commit -m "ver4.6: 새 버전 시작"

echo.
echo 3. 푸시...
git push

echo.
echo 완료!
pause

