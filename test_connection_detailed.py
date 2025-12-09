"""
상세한 연결 테스트 - JSON 응답 확인 후 연결
"""
import asyncio
import sys
import json
from playwright.async_api import async_playwright

async def test():
    print("=" * 60)
    print("크롬 디버깅 모드 상세 연결 테스트")
    print("=" * 60)
    print()
    
    # 먼저 JSON 엔드포인트 확인
    print("[1] JSON 엔드포인트 확인 중...")
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=5) as response:
            json_data = json.loads(response.read().decode())
            print(f"✓ JSON 응답 받음: {len(json_data)}개 페이지/타겟 발견")
            if json_data:
                print(f"  첫 번째 타겟: {json_data[0].get('title', 'N/A')}")
                print(f"  WebSocket URL: {json_data[0].get('webSocketDebuggerUrl', 'N/A')}")
            print()
    except Exception as e:
        print(f"✗ JSON 엔드포인트 확인 실패: {e}")
        print("크롬이 디버깅 모드로 실행되지 않았을 수 있습니다.")
        return
    
    # Playwright 연결 시도
    print("[2] Playwright 연결 시도 중...")
    print()
    
    urls_to_try = [
        "http://127.0.0.1:9222",
        "http://localhost:9222",
    ]
    
    browser = None
    connected = False
    
    for url in urls_to_try:
        print(f"  시도: {url}")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(url, timeout=30000)
                print(f"  ✓ 연결 성공!")
                print()
                
                # 브라우저 정보
                contexts = browser.contexts
                print(f"브라우저 컨텍스트 수: {len(contexts)}")
                
                if contexts:
                    pages = contexts[0].pages
                    print(f"열린 페이지 수: {len(pages)}")
                    if pages:
                        for i, page in enumerate(pages):
                            print(f"  페이지 {i+1}: {page.url[:80]}")
                
                await browser.close()
                connected = True
                break
                
        except Exception as e:
            print(f"  ✗ 연결 실패: {type(e).__name__}: {e}")
            print()
    
    if connected:
        print("=" * 60)
        print("연결 성공! 모든 것이 정상 작동 중입니다.")
        print("=" * 60)
    else:
        print("=" * 60)
        print("연결 실패!")
        print("=" * 60)
        print()
        print("JSON은 받았지만 Playwright 연결이 실패했습니다.")
        print()
        print("가능한 원인:")
        print("1. 방화벽이나 보안 소프트웨어가 WebSocket 연결을 차단")
        print("2. Playwright 버전 문제")
        print("3. 네트워크 설정 문제")
        print()
        print("해결 방법:")
        print("1. 방화벽 설정 확인")
        print("2. Playwright 재설치: pip install --upgrade playwright")
        print("3. 다른 스크립트로 테스트해보기")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test())

