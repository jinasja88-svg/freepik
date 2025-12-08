"""
Freepik 자동화 - 사용자가 띄워놓은 크롬 창에서 작업
Playwright로 DOM 요소를 직접 찾아서 작업
"""
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import pyautogui
import pyperclip
import time

PROMPT_TEXT = "Please naturally composite the product from @img2 onto the model in @img1."

# 파일 경로 설정
MODEL_DIR = Path(r"D:\private\코딩\커서\new\model")
CLOTHES_DIR = Path(r"D:\private\코딩\커서\new\clothes")

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


async def connect_and_work():
    """크롬에 연결해서 작업"""
    print("=" * 50)
    print("Freepik 자동화 - 기존 크롬 연결")
    print("=" * 50)
    print("\n중요: 크롬을 디버깅 모드로 실행해야 합니다!")
    print("\n크롬 디버깅 모드 실행 방법:")
    print("1. 모든 크롬 창을 닫으세요")
    print("2. start_chrome_debug.bat 파일을 실행하세요")
    print("   (또는 수동으로 명령 실행)")
    print("3. 크롬이 열리면 Freepik에 로그인하세요")
    print("4. 이 프로그램을 실행하세요")
    print("\n준비되면 Enter를 누르세요...")
    input()
    
    async with async_playwright() as p:
        try:
            # 디버깅 포트로 연결
            print("\n크롬 브라우저에 연결 중...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("✓ 브라우저 연결 성공!")
            
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
            
            # 파일 업로드 함수
            async def upload_file(file_name, upload_button_selector, folder_path=None):
                """파일 업로드 함수"""
                print(f"\n=== 파일 업로드: {file_name} ===")
                if folder_path:
                    print(f"폴더: {folder_path}")
                
                # 파일 업로드 버튼 클릭
                print("파일 업로드 버튼 클릭 중...")
                try:
                    upload_btn = await page.wait_for_selector(upload_button_selector, timeout=10000)
                    print("✓ 파일 업로드 버튼 찾음")
                    await upload_btn.click()
                    print("✓ 파일 업로드 버튼 클릭 완료")
                    await asyncio.sleep(1.0)  # 모달 창이 뜰 때까지 대기
                except Exception as e:
                    print(f"✗ 파일 업로드 버튼 찾기 실패: {e}")
                    print("수동으로 파일 업로드 버튼을 클릭해주세요.")
                    input("파일 업로드 버튼 클릭 후 Enter를 누르세요...")
                
                # 모달 창 내 파일 선택 버튼 클릭
                print("모달 창 내 파일 선택 버튼 클릭 중...")
                modal_btn = None
                modal_button_selector = "body > div.fixed.inset-0.flex.justify-center.bg-neutral-900\\/80.py-8.backdrop-blur-sm.bg-black\\/70.items-center.z-\\[50\\] > div > div > div.flex.h-\\[80vh\\].flex-col.gap-0.md\\:flex-row.md\\:gap-3.lg\\:h-\\[550px\\] > div.flex.h-full.w-full.max-w-full.flex-col.overflow-hidden.md\\:max-w-\\[280px\\] > div.scroll-conversations.border-surface-border-alpha-2.scrollbar-thin.scrollbar-stable.scrollbar-thumb-neutral-200.dark\\:scrollbar-thumb-neutral-800.my-5.flex.h-full.w-full.flex-wrap.content-start.items-start.overflow-y-auto.\\!overflow-x-hidden.rounded-lg.border.border-dashed.p-2.transition-all.duration-100.ease-out.md\\:p-4.hover\\:bg-surface-1 > div > button"
                
                try:
                    modal_btn = await page.wait_for_selector(modal_button_selector, timeout=10000)
                    print("✓ 모달 창 내 버튼 찾음")
                except:
                    try:
                        modal_btn = await page.evaluate_handle("""
                            () => {
                                const modal = document.querySelector('div.fixed.inset-0.flex.justify-center');
                                if (!modal) return null;
                                const dashedDiv = modal.querySelector('div.border-dashed');
                                if (dashedDiv) {
                                    const btn = dashedDiv.querySelector('button');
                                    if (btn) return btn;
                                }
                                const scrollDiv = modal.querySelector('div.scroll-conversations');
                                if (scrollDiv) {
                                    const btn = scrollDiv.querySelector('button');
                                    if (btn) return btn;
                                }
                                const allButtons = modal.querySelectorAll('button');
                                if (allButtons.length > 0) return allButtons[0];
                                return null;
                            }
                        """)
                        if modal_btn and await modal_btn.evaluate("el => el !== null"):
                            print("✓ 모달 창 내 버튼 찾음 (JavaScript 기반)")
                        else:
                            modal_btn = None
                    except Exception as e:
                        print(f"JavaScript 기반 찾기 실패: {e}")
                        modal_btn = None
                
                if not modal_btn:
                    print("✗ 모달 창 내 버튼을 찾을 수 없습니다.")
                    input("모달 창 내 버튼 클릭 후 Enter를 누르세요...")
                else:
                    await modal_btn.click()
                    print("✓ 모달 창 내 버튼 클릭 완료")
                    await asyncio.sleep(2.0)
                    
                    # 파일 선택 다이얼로그에서 파일 선택
                    print("파일 선택 다이얼로그 대기 중...")
                    time.sleep(3.0)
                    
                    # 먼저 파일 선택 창 클릭 (포커스 확보)
                    print("파일 선택 창 클릭 중 (포커스 확보)...")
                    screen_width, screen_height = pyautogui.size()
                    pyautogui.click(screen_width // 2, screen_height // 2)
                    time.sleep(0.5)
                    
                    # 폴더 경로가 지정된 경우 해당 폴더로 이동
                    if folder_path:
                        print(f"폴더 경로로 이동 중: {folder_path}")
                        # 주소창에 포커스 (Alt+D) - 여러 번 시도
                        for i in range(3):
                            pyautogui.hotkey("alt", "d")
                            time.sleep(0.3)
                        
                        # 기존 경로 삭제
                        pyautogui.hotkey("ctrl", "a")
                        time.sleep(0.2)
                        pyautogui.press("backspace")
                        time.sleep(0.2)
                        
                        # 경로 입력
                        pyperclip.copy(str(folder_path))
                        pyautogui.hotkey("ctrl", "v")
                        time.sleep(0.5)
                        pyautogui.press("enter")
                        time.sleep(2.0)  # 폴더 이동 완료 대기 (더 길게)
                        
                        # 경로 이동 후 다시 파일 선택 창 클릭
                        print("경로 이동 후 파일 선택 창 클릭 중...")
                        pyautogui.click(screen_width // 2, screen_height // 2)
                        time.sleep(0.5)
                    
                    # 파일 이름 입력
                    print(f"파일 이름 입력 중: {file_name}")
                    pyautogui.typewrite(file_name, interval=0.1)
                    time.sleep(0.8)
                    
                    # Enter로 열기
                    print("Enter 키로 '열기' 버튼 클릭 중...")
                    pyautogui.press("enter")
                    time.sleep(2.0)
                    
                    print("✓ 파일 선택 및 열기 완료")
                    
                    # 모달 창 내 "올라가" 버튼 클릭
                    print("'올라가' 버튼 클릭 중...")
                    upload_confirm_selector = "body > div.fixed.inset-0.flex.justify-center.bg-neutral-900\\/80.py-8.backdrop-blur-sm.bg-black\\/70.items-center.z-\\[50\\] > div > div > div.flex.h-\\[80vh\\].flex-col.gap-0.md\\:flex-row.md\\:gap-3.lg\\:h-\\[550px\\] > div.flex.h-full.w-full.max-w-full.flex-col.overflow-hidden.md\\:max-w-\\[280px\\] > div.flex.justify-end.gap-2.py-2.pr-1 > button.flex.items-center.justify-center.gap-2.font-semibold.transition.duration-150.ease-in-out.disabled\\:cursor-not-allowed.disabled\\:opacity-50.disabled\\:aria-pressed\\:cursor-default.disabled\\:aria-pressed\\:opacity-100.outline-none.focus\\:outline-none.focus-visible\\:outline-none.active\\:outline-none.h-8.px-4.text-xs.bg-primary-0.text-primary-foreground-0.aria-pressed\\:bg-primary-2.hover\\:enabled\\:bg-primary-1.active\\:enabled\\:bg-primary-2.rounded-lg.sticky.bottom-0"
                    
                    try:
                        upload_confirm_btn = await page.wait_for_selector(upload_confirm_selector, timeout=10000)
                        print("✓ '올라가' 버튼 찾음")
                        await upload_confirm_btn.click()
                        print("✓ '올라가' 버튼 클릭 완료")
                        await asyncio.sleep(2.0)
                    except Exception as e:
                        print(f"✗ '올라가' 버튼 찾기 실패: {e}")
                        try:
                            upload_confirm_btn = await page.evaluate_handle("""
                                () => {
                                    const modal = document.querySelector('div.fixed.inset-0.flex.justify-center');
                                    if (!modal) return null;
                                    const buttons = modal.querySelectorAll('button');
                                    for (let btn of buttons) {
                                        const parent = btn.closest('div.flex.justify-end');
                                        if (parent && btn.textContent && (btn.textContent.includes('올') || btn.textContent.includes('Up'))) {
                                            return btn;
                                        }
                                    }
                                    for (let btn of buttons) {
                                        if (btn.classList.contains('bg-primary-0') || btn.className.includes('bg-primary-0')) {
                                            return btn;
                                        }
                                    }
                                    return null;
                                }
                            """)
                            if upload_confirm_btn and await upload_confirm_btn.evaluate("el => el !== null"):
                                print("✓ '올라가' 버튼 찾음 (JavaScript 기반)")
                                await upload_confirm_btn.click()
                                print("✓ '올라가' 버튼 클릭 완료")
                                await asyncio.sleep(2.0)
                            else:
                                raise Exception("버튼을 찾을 수 없음")
                        except Exception as e2:
                            print(f"JavaScript 기반 찾기도 실패: {e2}")
                            input("수동으로 '올라가' 버튼 클릭 후 Enter를 누르세요...")
                    
                    print(f"✓ {file_name} 업로드 완료")
            
            # 업로드된 파일 삭제 함수
            async def delete_uploaded_file(file_index):
                """업로드된 파일의 X 버튼 클릭하여 삭제
                file_index: 1 (첫 번째 파일) 또는 2 (두 번째 파일)
                """
                print(f"\n=== 업로드된 파일 삭제 ({file_index}번째 파일) ===")
                try:
                    # X 버튼 셀렉터 (file_index에 따라 nth-child 값 변경)
                    nth_child = 3 if file_index == 1 else 4
                    x_button_selector = f"#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child({nth_child}) > div > div > div > button"
                    
                    print(f"X 버튼 찾는 중... (nth-child({nth_child}))")
                    x_button = await page.wait_for_selector(x_button_selector, timeout=5000)
                    
                    if x_button:
                        print(f"✓ X 버튼 찾음 ({file_index}번째 파일)")
                        await x_button.click()
                        print(f"✓ X 버튼 클릭 완료 - {file_index}번째 파일 삭제됨")
                        await asyncio.sleep(1.0)
                    else:
                        print(f"✗ X 버튼을 찾을 수 없습니다 ({file_index}번째 파일).")
                        print("수동으로 X 버튼을 클릭해주세요.")
                        input(f"{file_index}번째 파일의 X 버튼 클릭 후 Enter를 누르세요...")
                except Exception as e:
                    print(f"파일 삭제 중 오류 발생 ({file_index}번째 파일): {e}")
                    print("수동으로 파일을 삭제해주세요.")
                    input(f"{file_index}번째 파일 삭제 후 Enter를 누르세요...")
            
            # 업로드 버튼 클릭 후 모달 창에서 X 버튼 클릭하여 삭제
            async def delete_uploaded_file_via_modal():
                """업로드 버튼을 클릭하고 모달 창에서 X 버튼 클릭하여 삭제"""
                print("\n=== 업로드된 파일 삭제 (모달 창 방식) ===")
                try:
                    # 업로드 버튼 클릭
                    upload_selector = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(3) > div > div > div > div.absolute.inset-0.flex.items-center.justify-center.rounded-lg"
                    print("업로드 버튼 클릭 중...")
                    upload_btn = await page.wait_for_selector(upload_selector, timeout=5000)
                    await upload_btn.click()
                    print("✓ 업로드 버튼 클릭 완료")
                    await asyncio.sleep(1.0)  # 모달 창이 뜰 때까지 대기
                    
                    # 모달 창 내 X 버튼 찾기
                    modal_x_button_selector = "body > div.fixed.inset-0.flex.justify-center.bg-neutral-900\\/80.py-8.backdrop-blur-sm.bg-black\\/70.items-center.z-\\[50\\] > div > div > div.flex.h-\\[80vh\\].flex-col.gap-0.md\\:flex-row.md\\:gap-3.lg\\:h-\\[550px\\] > div.flex.h-full.w-full.max-w-full.flex-col.overflow-hidden.md\\:max-w-\\[280px\\] > div.scroll-conversations.border-surface-border-alpha-2.scrollbar-thin.scrollbar-stable.scrollbar-thumb-neutral-200.dark\\:scrollbar-thumb-neutral-800.my-5.flex.h-full.w-full.flex-wrap.content-start.items-start.overflow-y-auto.\\!overflow-x-hidden.rounded-lg.border.border-dashed.p-2.transition-all.duration-100.ease-out.md\\:p-4.hover\\:bg-surface-1 > div > button"
                    
                    print("모달 창 내 X 버튼 찾는 중...")
                    modal_x_button = await page.wait_for_selector(modal_x_button_selector, timeout=5000)
                    
                    if modal_x_button:
                        print("✓ 모달 창 내 X 버튼 찾음")
                        await modal_x_button.click()
                        print("✓ 모달 창 내 X 버튼 클릭 완료 - 파일 삭제됨")
                        await asyncio.sleep(1.0)
                    else:
                        # JavaScript로 찾기 시도
                        try:
                            modal_x_button = await page.evaluate_handle("""
                                () => {
                                    const modal = document.querySelector('div.fixed.inset-0.flex.justify-center');
                                    if (!modal) return null;
                                    const dashedDiv = modal.querySelector('div.border-dashed');
                                    if (dashedDiv) {
                                        const btn = dashedDiv.querySelector('button');
                                        if (btn) return btn;
                                    }
                                    return null;
                                }
                            """)
                            if modal_x_button and await modal_x_button.evaluate("el => el !== null"):
                                print("✓ 모달 창 내 X 버튼 찾음 (JavaScript 기반)")
                                await modal_x_button.click()
                                print("✓ 모달 창 내 X 버튼 클릭 완료 - 파일 삭제됨")
                                await asyncio.sleep(1.0)
                            else:
                                raise Exception("X 버튼을 찾을 수 없음")
                        except Exception as e:
                            print(f"✗ 모달 창 내 X 버튼을 찾을 수 없습니다: {e}")
                            input("수동으로 모달 창 내 X 버튼 클릭 후 Enter를 누르세요...")
                except Exception as e:
                    print(f"파일 삭제 중 오류 발생: {e}")
                    print("수동으로 파일을 삭제해주세요.")
                    input("파일 삭제 후 Enter를 누르세요...")
            
            # 첫 번째 파일 업로드 (model 폴더의 1.png)
            upload_selector_1 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(3) > div > div > div > div.absolute.inset-0.flex.items-center.justify-center.rounded-lg"
            await upload_file("1.png", upload_selector_1, MODEL_DIR)
            
            # 두 번째 파일 업로드 (clothes 폴더의 1.png)
            upload_selector_2 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(4) > div > div > div > div.absolute.inset-0.flex.items-center.justify-center.rounded-lg"
            await upload_file("1.png", upload_selector_2, CLOTHES_DIR)
            
            await asyncio.sleep(1.0)  # 파일 업로드 완료 대기
            
            print("\n=== 2단계: 프롬프트 입력 ===")
            
            # 프롬프트 입력칸 찾기 (여러 방법 시도)
            prompt_el = None
            
            selectors = [
                "#imagePromptInput > div > div > div.relative.flex-1 > div > div.text-surface-foreground-0.w-full.flex-1.overflow-y-auto.whitespace-pre-wrap.text-sm.leading-relaxed.outline-none.transition-all.user-select-all.dynamic-prompt.scrollbar-thin.scrollbar-thumb-neutral-800.\\32 xl-legacy\\:max-h-96.relative.max-h-\\[46px\\].min-h-\\[103px\\].rounded.p-2.text-sm.focus-visible\\:outline-none.focus-visible\\:ring-0.md\\:max-h-52.xl\\:max-h-72.empty-prompt",
                "div.empty-prompt",
                "[contenteditable='true']",
                "div[contenteditable]"
            ]
            
            for selector in selectors:
                try:
                    prompt_el = await page.wait_for_selector(selector, timeout=3000)
                    print(f"✓ 프롬프트 입력칸 찾음: {selector[:50]}...")
                    break
                except:
                    continue
            
            if not prompt_el:
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
            print(f"입력된 프롬프트: {current_value[:50]}...")
            
            if PROMPT_TEXT[:20] in current_value:
                print("✓ 프롬프트 입력 완료")
            else:
                print("⚠ 경고: 프롬프트가 제대로 입력되지 않았을 수 있습니다.")
            
            print("\n=== 3단계: Generate 버튼 클릭 ===")
            
            # Generate 버튼 찾기
            gen_btn = None
            
            try:
                gen_btn = await page.wait_for_selector('button[data-cy="generate-button"]', timeout=5000)
                print("✓ Generate 버튼 찾음")
            except:
                # fallback: 텍스트로 찾기
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
                else:
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
            print("1분 10초 후 파일 삭제를 시작합니다...")
            
            # 1분 10초 대기
            await asyncio.sleep(70)  # 1분 10초 = 70초
            
            # 업로드된 파일 삭제 (2번)
            print("\n=== 4단계: 업로드된 파일 삭제 ===")
            
            # 첫 번째 삭제 버튼 클릭
            print("첫 번째 삭제 버튼 클릭 중...")
            delete_selector_1 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(3) > div > div > div > button"
            try:
                delete_btn_1 = await page.wait_for_selector(delete_selector_1, timeout=5000)
                await delete_btn_1.click()
                print("✓ 첫 번째 삭제 버튼 클릭 완료")
                await asyncio.sleep(1.0)
            except Exception as e:
                print(f"✗ 첫 번째 삭제 버튼 찾기 실패: {e}")
                input("수동으로 첫 번째 삭제 버튼 클릭 후 Enter를 누르세요...")
            
            # 두 번째 삭제 버튼 클릭
            print("두 번째 삭제 버튼 클릭 중...")
            delete_selector_2 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(3) > div > div > div > button"
            try:
                delete_btn_2 = await page.wait_for_selector(delete_selector_2, timeout=5000)
                await delete_btn_2.click()
                print("✓ 두 번째 삭제 버튼 클릭 완료")
                await asyncio.sleep(1.0)
            except Exception as e:
                print(f"✗ 두 번째 삭제 버튼 찾기 실패: {e}")
                input("수동으로 두 번째 삭제 버튼 클릭 후 Enter를 누르세요...")
            
            print("✓ 파일 삭제 완료!")
            print("브라우저를 닫지 마세요.")
            
            # 연결 유지
            print("\n프로그램을 종료하려면 Ctrl+C를 누르세요.")
            try:
                await asyncio.sleep(3600)
            except KeyboardInterrupt:
                print("\n프로그램 종료")
            
        except Exception as e:
            print(f"\n✗ 에러 발생: {e}")
            print("\n크롬이 디버깅 모드로 실행되었는지 확인하세요:")
            print("start_chrome_debug.bat 파일을 실행하세요")


if __name__ == "__main__":
    asyncio.run(connect_and_work())

