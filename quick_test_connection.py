"""
빠른 연결 테스트 - IPv4/IPv6 모두 시도
"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        print("=" * 60)
        print("크롬 디버깅 모드 연결 테스트")
        print("=" * 60)
        print()
        
        browser = None
        
        # IPv4 먼저 시도 (타임아웃 증가)
        print("[1] IPv4 (127.0.0.1:9222) 연결 시도 중...")
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=30000)
            print("✓ IPv4 연결 성공!")
        except Exception as e1:
            print(f"✗ IPv4 연결 실패: {e1}")
            print()
            print("[2] IPv6 (localhost:9222) 연결 시도 중...")
            try:
                browser = await p.chromium.connect_over_cdp("http://localhost:9222", timeout=30000)
                print("✓ IPv6 연결 성공!")
            except Exception as e2:
                print(f"✗ IPv6 연결도 실패: {e2}")
                print()
                print("=" * 60)
                print("연결 실패!")
                print("=" * 60)
                print()
                print("확인 사항:")
                print("1. 크롬이 디버깅 모드로 실행되었는지 확인")
                print("   - start_chrome_debug.bat 실행")
                print("   - 또는 check_chrome_debug_manual.bat에서 수동 실행")
                print()
                print("2. 브라우저에서 직접 확인:")
                print("   http://127.0.0.1:9222/json")
                print("   (JSON 응답이 보이면 정상)")
                return
        
        if browser:
            print()
            print("=" * 60)
            print("연결 성공!")
            print("=" * 60)
            contexts = browser.contexts
            print(f"브라우저 컨텍스트 수: {len(contexts)}")
            if contexts:
                pages = contexts[0].pages
                print(f"열린 페이지 수: {len(pages)}")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test())

