"""
크롬 디버깅 모드 확인 스크립트
"""
import requests
import subprocess
import sys


def check_debug_port():
    """포트 9222가 열려있는지 확인"""
    print("=" * 50)
    print("크롬 디버깅 모드 확인")
    print("=" * 50)
    
    try:
        # localhost:9222/json에 요청 보내기
        print("\n1. 디버깅 포트 확인 중...")
        response = requests.get("http://localhost:9222/json", timeout=2)
        
        if response.status_code == 200:
            print("✓ 디버깅 포트 9222가 열려있습니다!")
            data = response.json()
            print(f"  - 연결된 페이지 수: {len(data)}")
            
            # Freepik 페이지 찾기
            freepik_pages = [p for p in data if "freepik.com" in p.get("url", "")]
            if freepik_pages:
                print(f"  - Freepik 페이지: {len(freepik_pages)}개 발견")
                for i, page in enumerate(freepik_pages[:3], 1):
                    print(f"    {i}. {page.get('url', 'N/A')[:80]}")
            else:
                print("  ⚠ Freepik 페이지를 찾을 수 없습니다.")
                print("     Freepik 페이지를 열어주세요.")
            
            return True
        else:
            print(f"✗ 디버깅 포트 응답 오류: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ 디버깅 포트 9222에 연결할 수 없습니다.")
        print("\n  → 크롬이 디버깅 모드로 실행되지 않았을 수 있습니다.")
        print("  → start_chrome_debug.bat 파일을 실행하세요.")
        return False
    except requests.exceptions.Timeout:
        print("✗ 디버깅 포트 응답 시간 초과")
        return False
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        return False


def check_chrome_process():
    """크롬 프로세스에 디버깅 옵션이 있는지 확인"""
    print("\n2. 크롬 프로세스 확인 중...")
    
    try:
        # Windows에서 크롬 프로세스 확인
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq chrome.exe', '/FO', 'CSV', '/V'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and 'chrome.exe' in result.stdout:
            print("✓ 크롬 프로세스가 실행 중입니다.")
            
            # wmic으로 더 자세한 정보 확인 (선택적)
            try:
                wmic_result = subprocess.run(
                    ['wmic', 'process', 'where', 'name="chrome.exe"', 'get', 'commandline'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if '--remote-debugging-port=9222' in wmic_result.stdout:
                    print("✓ 크롬이 디버깅 모드(--remote-debugging-port=9222)로 실행 중입니다!")
                    return True
                else:
                    print("⚠ 크롬이 디버깅 모드로 실행되지 않았을 수 있습니다.")
                    print("  → start_chrome_debug.bat 파일을 실행하세요.")
                    return False
            except Exception as e:
                print(f"  (프로세스 상세 정보 확인 실패: {e})")
                return False
        else:
            print("✗ 크롬 프로세스를 찾을 수 없습니다.")
            print("  → 크롬을 실행하세요.")
            return False
            
    except Exception as e:
        print(f"✗ 프로세스 확인 실패: {e}")
        return False


def test_playwright_connection():
    """Playwright로 연결 테스트"""
    print("\n3. Playwright 연결 테스트 중...")
    
    try:
        from playwright.async_api import async_playwright
        import asyncio
        
        async def test():
            try:
                playwright = await async_playwright().start()
                browser = None
                try:
                    browser = await playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
                    print("✓ Playwright로 연결 성공! (IPv4)")
                except Exception as e1:
                    print(f"  IPv4 연결 실패: {e1}")
                    print("  IPv6 localhost로 재시도 중...")
                    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
                    print("✓ Playwright로 연결 성공! (IPv6)")
                
                contexts = browser.contexts
                if contexts:
                    pages = contexts[0].pages
                    print(f"  - 컨텍스트 수: {len(contexts)}")
                    print(f"  - 페이지 수: {len(pages)}")
                    
                    freepik_pages = [p for p in pages if "freepik.com" in p.url]
                    if freepik_pages:
                        print(f"  - Freepik 페이지: {len(freepik_pages)}개 발견")
                    else:
                        print("  ⚠ Freepik 페이지를 찾을 수 없습니다.")
                else:
                    print("  ⚠ 연결된 컨텍스트가 없습니다.")
                
                await browser.close()
                await playwright.stop()
                return True
            except Exception as e:
                print(f"✗ Playwright 연결 실패: {e}")
                return False
        
        return asyncio.run(test())
        
    except ImportError:
        print("⚠ Playwright가 설치되지 않았습니다. (선택적 확인)")
        return None
    except Exception as e:
        print(f"✗ 테스트 실패: {e}")
        return False


if __name__ == "__main__":
    # requests 설치 확인
    try:
        import requests
    except ImportError:
        print("requests 모듈이 필요합니다.")
        print("설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    # 확인 실행
    port_ok = check_debug_port()
    process_ok = check_chrome_process()
    playwright_ok = test_playwright_connection()
    
    print("\n" + "=" * 50)
    print("확인 결과 요약")
    print("=" * 50)
    print(f"디버깅 포트: {'✓' if port_ok else '✗'}")
    print(f"크롬 프로세스: {'✓' if process_ok else '✗'}")
    if playwright_ok is not None:
        print(f"Playwright 연결: {'✓' if playwright_ok else '✗'}")
    
    if port_ok:
        print("\n✓ 크롬이 디버깅 모드로 정상 실행 중입니다!")
        print("  test_checkbox_only.bat를 실행할 수 있습니다.")
    else:
        print("\n✗ 크롬이 디버깅 모드로 실행되지 않았습니다.")
        print("  → start_chrome_debug.bat 파일을 실행하세요.")
        print("  → 모든 크롬 창을 닫고 다시 실행하세요.")
    
    print("\n계속하려면 Enter를 누르세요...")
    input()


