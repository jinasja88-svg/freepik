"""
Freepik 다운로드 기능 테스트 - 체크박스 클릭 후 다운로드만 테스트
이미 생성된 이미지가 있을 때 사용
"""
import asyncio
from playwright.async_api import async_playwright


async def test_download():
    """체크박스 클릭 및 다운로드 테스트"""
    print("=" * 50)
    print("Freepik 다운로드 기능 테스트")
    print("=" * 50)
    print("\n중요: 크롬을 디버깅 모드로 실행해야 합니다!")
    print("\n크롬 디버깅 모드 실행 방법:")
    print("1. 모든 크롬 창을 닫으세요")
    print("2. start_chrome_debug.bat 파일을 실행하세요")
    print("3. 크롬이 열리면 Freepik에 로그인하세요")
    print("4. 이미 생성된 이미지가 있는 페이지로 이동하세요")
    print("\n준비되면 Enter를 누르세요...")
    input()
    
    async with async_playwright() as p:
        try:
            # 디버깅 포트로 연결 (IPv4 우선)
            print("\n크롬 브라우저에 연결 중...")
            browser = None
            try:
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=30000)
                print("✓ 브라우저 연결 성공! (IPv4)")
            except Exception as e1:
                print(f"  IPv4 연결 실패: {e1}")
                print("  IPv6 localhost로 재시도 중...")
                try:
                    browser = await p.chromium.connect_over_cdp("http://localhost:9222", timeout=30000)
                    print("✓ 브라우저 연결 성공! (IPv6)")
                except Exception as e2:
                    print(f"  IPv6 연결도 실패: {e2}")
                    raise Exception("크롬 디버깅 모드에 연결할 수 없습니다. start_chrome_debug.bat를 실행했는지 확인하세요.")
            
            # 페이지 가져오기
            contexts = browser.contexts
            if not contexts:
                print("✗ 연결된 컨텍스트가 없습니다.")
                return
            
            context = contexts[0]
            pages = context.pages
            
            # Freepik 페이지 찾기
            page = None
            for p in pages:
                if "freepik.com" in p.url:
                    page = p
                    break
            
            if not page and pages:
                page = pages[0]  # 첫 번째 페이지 사용
            
            if not page:
                page = await context.new_page()
            
            print(f"현재 페이지: {page.url}")
            
            # Freepik 페이지로 이동 (필요시)
            if "freepik.com" not in page.url:
                print("Freepik 페이지로 이동 중...")
                await page.goto("https://www.freepik.com/ai/image-generator")
                await asyncio.sleep(2)
                print("이미 생성된 이미지가 있는 페이지로 이동해주세요.")
                input("준비되면 Enter를 누르세요...")
            
            # 체크박스 클릭 및 다운로드 함수
            async def click_checkbox_and_download():
                """체크박스 클릭 후 다운로드 버튼 클릭"""
                print("\n=== 체크박스 클릭 및 다운로드 테스트 ===")
                
                try:
                    # 체크박스 버튼 찾기
                    checkbox_selector = "#tool-layout-main > div > div.flex.flex-col.gap-2\\.5 > div.relative.w-full > div:nth-child(1) > div > div > div.border-surface-border-alpha-1.ml-auto.flex.items-center.gap-2.border-l.pl-2 > button > span"
                    
                    checkbox_btn = None
                    print("체크박스 버튼 찾는 중...")
                    try:
                        checkbox_btn = await page.wait_for_selector(checkbox_selector, timeout=5000)
                        print("✓ 체크박스 버튼 찾음 (CSS 셀렉터)")
                    except:
                        print("CSS 셀렉터로 찾기 실패. JavaScript로 찾는 중...")
                        # JavaScript로 찾기 시도
                        checkbox_btn = await page.evaluate_handle("""
                            () => {
                                const container = document.querySelector('#tool-layout-main > div > div.flex.flex-col.gap-2\\.5');
                                if (!container) {
                                    console.log('컨테이너를 찾을 수 없음');
                                    return null;
                                }
                                
                                // 방법 1: border-l.pl-2 클래스를 가진 div 내부의 button 찾기
                                const borderDiv = container.querySelector('div.border-l.pl-2');
                                if (borderDiv) {
                                    const btn = borderDiv.querySelector('button');
                                    if (btn) {
                                        console.log('방법 1로 체크박스 버튼 찾음');
                                        return btn;
                                    }
                                }
                                
                                // 방법 2: 모든 button 중에서 span을 가진 것 찾기
                                const buttons = container.querySelectorAll('button');
                                for (let btn of buttons) {
                                    const span = btn.querySelector('span');
                                    if (span) {
                                        console.log('방법 2로 체크박스 버튼 찾음');
                                        return btn;
                                    }
                                }
                                
                                // 방법 3: aria-pressed 속성을 가진 button 찾기
                                for (let btn of buttons) {
                                    if (btn.hasAttribute('aria-pressed')) {
                                        console.log('방법 3으로 체크박스 버튼 찾음');
                                        return btn;
                                    }
                                }
                                
                                console.log('체크박스 버튼을 찾을 수 없음');
                                return null;
                            }
                        """)
                        if checkbox_btn and await checkbox_btn.evaluate("el => el !== null"):
                            print("✓ 체크박스 버튼 찾음 (JavaScript 기반)")
                        else:
                            checkbox_btn = None
                    
                    if not checkbox_btn:
                        print("✗ 체크박스 버튼을 찾을 수 없습니다.")
                        print("\n디버깅 정보:")
                        # 페이지 구조 확인
                        structure = await page.evaluate("""
                            () => {
                                const container = document.querySelector('#tool-layout-main > div > div.flex.flex-col.gap-2\\.5');
                                if (!container) return '컨테이너를 찾을 수 없음';
                                
                                const buttons = container.querySelectorAll('button');
                                const info = [];
                                buttons.forEach((btn, idx) => {
                                    info.push({
                                        index: idx,
                                        hasSpan: !!btn.querySelector('span'),
                                        ariaPressed: btn.getAttribute('aria-pressed'),
                                        text: btn.textContent?.substring(0, 50),
                                        classes: btn.className
                                    });
                                });
                                return JSON.stringify(info, null, 2);
                            }
                        """)
                        print(f"페이지 구조:\n{structure}")
                        return False
                    
                    # 체크 상태 확인
                    is_checked = await checkbox_btn.get_attribute("aria-pressed")
                    print(f"현재 체크 상태: {is_checked}")
                    
                    if is_checked != "true":
                        print("체크박스가 체크되지 않음. 마우스 호버 후 클릭...")
                        # 마우스 호버 (체크박스가 나타나도록)
                        await checkbox_btn.hover()
                        await asyncio.sleep(0.5)
                        
                        await checkbox_btn.click()
                        print("✓ 체크박스 클릭 완료")
                        await asyncio.sleep(1.0)
                    else:
                        print("✓ 체크박스가 이미 체크되어 있음")
                    
                    # 다운로드 버튼 클릭
                    print("\n다운로드 버튼 찾는 중...")
                    download_button_selector = "body > div.pointer-events-none.fixed.bottom-0.right-0.z-30.flex.items-center.justify-center.duration-100.left-\\[384px\\].xl\\:left-\\[560px\\] > div > div.ml-auto.flex.gap-2 > div.flex > button"
                    
                    download_btn = None
                    try:
                        download_btn = await page.wait_for_selector(download_button_selector, timeout=5000)
                        print("✓ 다운로드 버튼 찾음 (CSS 셀렉터)")
                    except:
                        print("CSS 셀렉터로 찾기 실패. JavaScript로 찾는 중...")
                        # JavaScript로 찾기 시도
                        download_btn = await page.evaluate_handle("""
                            () => {
                                // 방법 1: fixed bottom-0 right-0 클래스를 가진 div 내부의 button 찾기
                                const fixedDiv = document.querySelector('div.fixed.bottom-0.right-0');
                                if (fixedDiv) {
                                    const buttons = fixedDiv.querySelectorAll('button');
                                    for (let btn of buttons) {
                                        const text = (btn.textContent || '').toLowerCase();
                                        if (text.includes('download') || text.includes('다운로드')) {
                                            return btn;
                                        }
                                    }
                                }
                                
                                // 방법 2: 모든 button 중에서 download 관련 텍스트 찾기
                                const allButtons = Array.from(document.querySelectorAll('button'));
                                return allButtons.find(btn => {
                                    const text = (btn.textContent || '').toLowerCase();
                                    return text.includes('download') || text.includes('다운로드');
                                });
                            }
                        """)
                        if download_btn and await download_btn.evaluate("el => el !== null"):
                            print("✓ 다운로드 버튼 찾음 (JavaScript 기반)")
                        else:
                            download_btn = None
                    
                    if not download_btn:
                        print("✗ 다운로드 버튼을 찾을 수 없습니다.")
                        print("\n디버깅 정보:")
                        # 페이지 구조 확인
                        structure = await page.evaluate("""
                            () => {
                                const fixedDiv = document.querySelector('div.fixed.bottom-0.right-0');
                                if (!fixedDiv) return '고정 div를 찾을 수 없음';
                                
                                const buttons = fixedDiv.querySelectorAll('button');
                                const info = [];
                                buttons.forEach((btn, idx) => {
                                    info.push({
                                        index: idx,
                                        text: btn.textContent?.substring(0, 50),
                                        classes: btn.className
                                    });
                                });
                                return JSON.stringify(info, null, 2);
                            }
                        """)
                        print(f"다운로드 버튼 영역 구조:\n{structure}")
                        return False
                    
                    print("다운로드 버튼 클릭 중...")
                    await download_btn.click()
                    print("✓ 다운로드 버튼 클릭 완료!")
                    await asyncio.sleep(2.0)  # 다운로드 시작 대기
                    
                    print("\n✓ 테스트 완료!")
                    print("브라우저의 다운로드 폴더를 확인하세요.")
                    return True
                        
                except Exception as e:
                    print(f"✗ 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            # 테스트 실행
            success = await click_checkbox_and_download()
            
            if success:
                print("\n" + "=" * 50)
                print("테스트 성공!")
                print("=" * 50)
            else:
                print("\n" + "=" * 50)
                print("테스트 실패!")
                print("=" * 50)
            
            print("\n브라우저를 닫지 마세요.")
            print("프로그램을 종료하려면 Ctrl+C를 누르세요.")
            try:
                await asyncio.sleep(3600)
            except KeyboardInterrupt:
                print("\n프로그램 종료")
            
        except Exception as e:
            print(f"\n✗ 에러 발생: {e}")
            print("\n크롬이 디버깅 모드로 실행되었는지 확인하세요:")
            print("start_chrome_debug.bat 파일을 실행하세요")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_download())


