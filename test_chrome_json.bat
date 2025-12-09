@echo off
chcp 65001 >nul
echo ========================================
echo 크롬 디버깅 포트 JSON 확인
echo ========================================
echo.
echo 브라우저에서 직접 확인하는 방법:
echo.
echo 1. 크롬 브라우저를 엽니다
echo 2. 주소창에 입력: http://127.0.0.1:9222/json
echo 3. JSON 응답이 보이면 정상입니다
echo.
echo PowerShell로 확인 시도 중...
echo.
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:9222/json' -TimeoutSec 3 -UseBasicParsing; Write-Host '[성공] JSON 응답 받음:'; Write-Host $response.Content.Substring(0, [Math]::Min(500, $response.Content.Length)) } catch { Write-Host '[실패] 연결할 수 없습니다:'; Write-Host $_.Exception.Message }"
echo.
pause

