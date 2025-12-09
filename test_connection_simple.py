"""
간단한 연결 테스트 - 디버깅 모드가 제대로 작동하는지 확인
"""
import asyncio
from playwright.async_api import async_playwright


async def test_connection():
    print("=" * 50)
    print("크롬 디버깅 모드 연결 테스트")
    print("=" * 50)
    
    async with async_playwright() as p:
        try:
            print("\n1. 디버깅 포트에 연결 시도 중...")
            print("   IPv4 localhost (127.0.0.1:9222)로 시도...")
            
            browser = None
            try:
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                print("✓ 연결 성공! (IPv4)")
            except Exception as e1:
                print(f"   IPv4 연결 실패: {e1}")
                print("   IPv6 localhost로 재시도...")
                try:
                    browser = await p.chromium.connect_over_cdp("http://localhost:9222")
                    print("✓ 연결 성공! (IPv6)")
                except Exception as e2:
                    print(f"   IPv6 연결도 실패: {e2}")
                    raise e2
            
            if not browser:
                raise Exception("브라우저 연결 실패")
            
            print("\n2. 컨텍스트 확인 중...")
            contexts = browser.contexts
            print(f"   컨텍스트 수: {len(contexts)}")
            
            if contexts:
                context = contexts[0]
                pages = context.pages
                print(f"   페이지 수: {len(pages)}")
                
                print("\n3. 페이지 목록:")
                for i, page in enumerate(pages, 1):
                    print(f"   {i}. {page.url[:80]}")
                
                # Freepik 페이지 찾기
                freepik_pages = [p for p in pages if "freepik.com" in p.url]
                if freepik_pages:
                    print(f"\n✓ Freepik 페이지 발견: {len(freepik_pages)}개")
                else:
                    print("\n⚠ Freepik 페이지를 찾을 수 없습니다.")
                    print("   Freepik 페이지를 열어주세요.")
                
                print("\n✓✓✓ 연결 테스트 성공! ✓✓✓")
                print("   디버깅 모드가 정상적으로 작동 중입니다.")
            else:
                print("\n⚠ 컨텍스트가 없습니다.")
                print("   크롬에서 페이지를 열어주세요.")
            
            await browser.close()
            
        except Exception as e:
            print(f"\n✗ 연결 실패: {e}")
            print("\n문제 해결 방법:")
            print("1. 모든 크롬 창을 닫으세요")
            print("2. start_chrome_debug.bat 파일을 실행하세요")
            print("3. 크롬이 열리면 Freepik에 로그인하세요")
            print("4. 다시 이 스크립트를 실행하세요")


if __name__ == "__main__":
    asyncio.run(test_connection())
    print("\n계속하려면 Enter를 누르세요...")
    input()

