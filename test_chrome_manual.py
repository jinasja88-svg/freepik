"""
크롬 디버깅 모드 연결 테스트 스크립트
"""
import asyncio
import sys
from playwright.async_api import async_playwright

async def test_chrome_connection():
    """크롬 디버깅 포트 연결 테스트"""
    
    print("=" * 60)
    print("크롬 디버깅 모드 연결 테스트")
    print("=" * 60)
    print()
    
    # 여러 URL 시도
    urls = [
        "http://127.0.0.1:9222",
        "http://localhost:9222",
        "http://[::1]:9222"
    ]
    
    connected = False
    
    for url in urls:
        print(f"[시도] {url} 연결 시도 중...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(url)
                print(f"✓ [성공] {url} 연결 성공!")
                print()
                
                # 브라우저 정보 출력
                contexts = browser.contexts
                print(f"브라우저 컨텍스트 수: {len(contexts)}")
                
                if contexts:
                    pages = contexts[0].pages
                    print(f"열린 페이지 수: {len(pages)}")
                    if pages:
                        print(f"첫 번째 페이지 URL: {pages[0].url}")
                
                await browser.close()
                connected = True
                break
                
        except Exception as e:
            print(f"✗ [실패] {url} 연결 실패: {e}")
            print()
    
    if not connected:
        print("=" * 60)
        print("연결 실패!")
        print("=" * 60)
        print()
        print("확인 사항:")
        print("1. 크롬이 디버깅 모드로 실행되었는지 확인")
        print("   - start_chrome_debug.bat 실행했는지 확인")
        print("   - 또는 수동 실행: chrome.exe --remote-debugging-port=9222")
        print()
        print("2. 포트 9222가 열려있는지 확인")
        print("   - 브라우저에서 http://127.0.0.1:9222/json 열어보기")
        print("   - JSON 응답이 보이면 정상")
        print()
        print("3. 방화벽 확인")
        print("   - Windows 방화벽이 포트 9222를 차단하지 않는지 확인")
        print()
        print("4. 크롬 프로세스 확인")
        print("   - 작업 관리자에서 chrome.exe 프로세스 확인")
        print("   - 명령줄에 --remote-debugging-port=9222 인자가 있는지 확인")
        print()
        sys.exit(1)
    else:
        print("=" * 60)
        print("연결 성공! 모든 것이 정상 작동 중입니다.")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_chrome_connection())




