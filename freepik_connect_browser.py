"""
Freepik 자동화 - 이미 열려있는 크롬 브라우저에 연결
사용자가 직접 크롬을 띄워놓고 로그인한 상태에서 사용
"""
import asyncio
from playwright.async_api import async_playwright

FREEPIK_URL = "https://www.freepik.com/ai/image-generator"
PROMPT_TEXT = "Please naturally composite the product from @img1 onto the model in @img2."


async def connect_to_existing_browser():
    """이미 열려있는 크롬 브라우저에 연결"""
    async with async_playwright() as p:
        print("=" * 50)
        print("Freepik 자동화 - 기존 브라우저 연결")
        print("=" * 50)
        print("\n중요: 크롬 브라우저를 디버깅 모드로 실행해야 합니다!")
        print("\n크롬 디버깅 모드 실행 방법:")
        print("1. 모든 크롬 창을 닫으세요")
        print("2. 명령 프롬프트에서 다음 명령 실행:")
        print('   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
        print("3. 크롬이 열리면 Freepik에 로그인하세요")
        print("4. 이 프로그램을 실행하세요")
        print("\n준비되면 Enter를 누르세요...")
        input()
        
        try:
            # 디버깅 포트로 연결 (IPv4 우선)
            print("\n크롬 브라우저에 연결 중...")
            browser = None
            try:
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                print("✓ 브라우저 연결 성공! (IPv4)")
            except Exception as e1:
                print(f"  IPv4 연결 실패: {e1}")
                print("  IPv6 localhost로 재시도 중...")
                try:
                    browser = await p.chromium.connect_over_cdp("http://localhost:9222")
                    print("✓ 브라우저 연결 성공! (IPv6)")
                except Exception as e2:
                    print(f"  IPv6 연결도 실패: {e2}")
                    raise Exception("크롬 디버깅 모드에 연결할 수 없습니다. start_chrome_debug.bat를 실행했는지 확인하세요.")
            
            # 모든 페이지 가져오기
            contexts = browser.contexts
            if not contexts:
                print("✗ 연결된 컨텍스트가 없습니다.")
                return
            
            # 첫 번째 컨텍스트의 첫 번째 페이지 사용
            context = contexts[0]
            pages = context.pages
            if pages:
                page = pages[0]
            else:
                page = await context.new_page()
            
            print(f"현재 페이지 URL: {page.url}")
            
            # Freepik 페이지로 이동 (아직 안 열려있으면)
            if "freepik.com" not in page.url:
                print("Freepik 페이지로 이동 중...")
                await page.goto(FREEPIK_URL)
                await asyncio.sleep(2)
            
            print("\n=== 1단계: 프롬프트 입력 ===")
            
            # 프롬프트 입력칸 찾기 (여러 방법 시도)
            prompt_el = None
            
            # 방법 1: 정확한 셀렉터
            try:
                prompt_selector = (
                    "#imagePromptInput > div > div > div.relative.flex-1 > div > "
                    "div.text-surface-foreground-0.w-full.flex-1.overflow-y-auto.whitespace-pre-wrap."
                    "text-sm.leading-relaxed.outline-none.transition-all.user-select-all.dynamic-prompt."
                    "scrollbar-thin.scrollbar-thumb-neutral-800.\\32 xl-legacy\\:max-h-96.relative."
                    "max-h-\\[46px\\].min-h-\\[103px\\].rounded.p-2.text-sm.focus-visible\\:outline-none."
                    "focus-visible\\:ring-0.md\\:max-h-52.xl\\:max-h-72.empty-prompt"
                )
                prompt_el = await page.wait_for_selector(prompt_selector, timeout=5000)
                print("✓ 프롬프트 입력칸 찾음 (정확한 셀렉터)")
            except:
                # 방법 2: empty-prompt 클래스
                try:
                    prompt_el = await page.wait_for_selector("div.empty-prompt", timeout=5000)
                    print("✓ 프롬프트 입력칸 찾음 (empty-prompt 클래스)")
                except:
                    # 방법 3: contenteditable
                    try:
                        prompt_el = await page.wait_for_selector("[contenteditable='true']", timeout=5000)
                        print("✓ 프롬프트 입력칸 찾음 (contenteditable)")
                    except:
                        print("✗ 프롬프트 입력칸을 찾을 수 없습니다.")
                        print("페이지를 새로고침하거나 수동으로 확인해주세요.")
                        return
            
            # 프롬프트 입력
            await prompt_el.click()
            await asyncio.sleep(0.3)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Delete")
            await asyncio.sleep(0.2)
            
            print(f"프롬프트 입력 중: {PROMPT_TEXT}")
            await prompt_el.type(PROMPT_TEXT, delay=50)
            await asyncio.sleep(0.5)
            
            # 입력 확인
            current_value = await prompt_el.evaluate("""
                el => el.textContent || el.innerText || el.value || ''
            """)
            print(f"입력된 프롬프트 확인: {current_value[:50]}...")
            
            if PROMPT_TEXT[:20] in current_value:
                print("✓ 프롬프트 입력 완료")
            else:
                print("⚠ 경고: 프롬프트가 제대로 입력되지 않았을 수 있습니다.")
            
            print("\n=== 2단계: Generate 버튼 클릭 ===")
            
            # Generate 버튼 찾기
            gen_btn = None
            
            try:
                gen_btn = await page.wait_for_selector('button[data-cy="generate-button"]', timeout=5000)
                print("✓ Generate 버튼 찾음")
            except:
                # fallback: 텍스트로 찾기
                try:
                    gen_btn = await page.evaluate_handle("""
                        () => {
                            const buttons = Array.from(document.querySelectorAll('button'));
                            return buttons.find(btn => {
                                const text = (btn.textContent || '').toLowerCase();
                                return text.includes('generate') || text.includes('생성');
                            });
                        }
                    """)
                    if gen_btn:
                        print("✓ Generate 버튼 찾음 (텍스트 기반)")
                except:
                    print("✗ Generate 버튼을 찾을 수 없습니다.")
                    return
            
            # 버튼 활성화까지 대기
            print("버튼 활성화 대기 중...")
            for i in range(20):
                disabled = await gen_btn.get_attribute("aria-disabled")
                if disabled != "true":
                    print(f"✓ 버튼 활성화됨 ({i * 0.15:.1f}초 후)")
                    break
                await asyncio.sleep(0.15)
            
            # Generate 버튼 클릭
            await gen_btn.click()
            print("✓ Generate 버튼 클릭 완료!")
            print("\n이미지 생성이 시작되었습니다.")
            print("브라우저를 닫지 마세요.")
            
            # 연결 유지
            print("\n프로그램을 종료하려면 Ctrl+C를 누르세요.")
            print("(브라우저는 계속 열려있습니다)")
            
            try:
                await asyncio.sleep(3600)  # 1시간 대기 (또는 무한 대기)
            except KeyboardInterrupt:
                print("\n프로그램 종료")
            
        except Exception as e:
            print(f"\n✗ 에러 발생: {e}")
            print("\n크롬이 디버깅 모드로 실행되었는지 확인하세요:")
            print('"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')


if __name__ == "__main__":
    asyncio.run(connect_to_existing_browser())


