@echo off
chcp 65001 > nul
cd /d "%~dp0"
pyinstaller freepik_auto_simple_ver4.5.spec --clean
pause

