@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Freepik 다운로드 ver1.1 실행
echo ========================================
echo.
python freepik_download_ver1.1.py
pause

