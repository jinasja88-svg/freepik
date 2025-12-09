"""
Freepik 자동화 - Download 기능 추가 버전
ver2.2를 기반으로 이미지 생성 완료 감지 및 자동 다운로드 기능 추가
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
DOWNLOAD_DIR = Path(r"D:\private\코딩\커서\new\downloads")  # 다운로드 폴더

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


async def connect_and_work():
    """크롬에 연결해서 작업"""
    print("=" * 50)
    print("Freepik 자동화 - Download 기능 포함")
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
    
    # 다운로드 폴더 생성
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    print(f"\n다운로드 폴더: {DOWNLOAD_DIR}")
    
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
            
            # 파일 업로드 함수 (ver2.2와 동일)
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
            
            # 이미지 생성 완료 감지 및 다운로드 함수 (새로 추가)
            async def wait_for_image_completion_and_download(model_idx, clothes_idx):
                """이미지 생성 완료를 감지하고 다운로드"""
                print("\n=== 이미지 생성 완료 감지 및 다운로드 ===")
                
                max_wait_time = 120  # 최대 120초 대기
                check_interval = 2  # 2초마다 확인
                elapsed = 0
                
                while elapsed < max_wait_time:
                    try:
                        # 피드 컨테이너 찾기
                        feed_container = await page.query_selector("#tool-layout-main > div > div.flex.flex-col.gap-2\\.5")
                        
                        if feed_container:
                            # "Generating..." 텍스트 확인
                            has_generating = await feed_container.evaluate("""
                                () => {
                                    const spans = Array.from(document.querySelectorAll('span'));
                                    return spans.some(span => span.textContent.includes('Generating...') || span.textContent.includes('Getting ready...'));
                                }
                            """)
                            
                            if not has_generating:
                                # 생성 완료된 이미지 찾기
                                completed_item_id = await feed_container.evaluate("""
                                    () => {
                                        const items = document.querySelectorAll("div[id^='item-']");
                                        for (let i = items.length - 1; i >= 0; i--) {
                                            const item = items[i];
                                            const hasGenerating = item.textContent.includes('Generating...') || item.textContent.includes('Getting ready...');
                                            const hasImage = item.querySelector("img[id^='creation']") || item.querySelector("img");
                                            if (!hasGenerating && hasImage) {
                                                return item.id;
                                            }
                                        }
                                        return null;
                                    }
                                """)
                                
                                if completed_item_id:
                                    print(f"✓ 이미지 생성 완료 감지! (item: {completed_item_id})")
                                    
                                    # 체크박스 클릭
                                    await click_checkbox_and_download(model_idx, clothes_idx)
                                    return True
                    
                    except Exception as e:
                        print(f"감지 중 오류: {e}")
                    
                    await asyncio.sleep(check_interval)
                    elapsed += check_interval
                    
                    if elapsed % 10 == 0:
                        print(f"생성 대기 중... ({elapsed}초 경과)")
                
                print("⚠ 경고: 이미지 생성 완료를 감지하지 못했습니다. (최대 대기 시간 초과)")
                return False
            
            # 체크박스 클릭 및 다운로드 함수 (새로 추가)
            async def click_checkbox_and_download(model_idx, clothes_idx):
                """체크박스 클릭 후 다운로드 버튼 클릭"""
                print("\n=== 체크박스 클릭 및 다운로드 ===")
                
                try:
                    # 체크박스 버튼 찾기
                    checkbox_selector = "#tool-layout-main > div > div.flex.flex-col.gap-2\\.5 > div.relative.w-full > div:nth-child(1) > div > div > div.border-surface-border-alpha-1.ml-auto.flex.items-center.gap-2.border-l.pl-2 > button > span"
                    
                    checkbox_btn = None
                    try:
                        checkbox_btn = await page.wait_for_selector(checkbox_selector, timeout=5000)
                        print("✓ 체크박스 버튼 찾음")
                    except:
                        # JavaScript로 찾기 시도
                        checkbox_btn = await page.evaluate_handle("""
                            () => {
                                const container = document.querySelector('#tool-layout-main > div > div.flex.flex-col.gap-2\\.5');
                                if (!container) return null;
                                const buttons = container.querySelectorAll('button');
                                for (let btn of buttons) {
                                    const span = btn.querySelector('span');
                                    if (span && (span.textContent.includes('✓') || btn.getAttribute('aria-pressed'))) {
                                        return btn;
                                    }
                                }
                                return null;
                            }
                        """)
                        if checkbox_btn and await checkbox_btn.evaluate("el => el !== null"):
                            print("✓ 체크박스 버튼 찾음 (JavaScript 기반)")
                        else:
                            checkbox_btn = None
                    
                    if checkbox_btn:
                        # 체크 상태 확인
                        is_checked = await checkbox_btn.get_attribute("aria-pressed")
                        if is_checked != "true":
                            # 마우스 호버 (체크박스가 나타나도록)
                            await checkbox_btn.hover()
                            await asyncio.sleep(0.5)
                            
                            await checkbox_btn.click()
                            print("✓ 체크박스 클릭 완료")
                            await asyncio.sleep(1.0)
                        else:
                            print("✓ 체크박스가 이미 체크되어 있음")
                        
                        # 다운로드 버튼 클릭
                        print("다운로드 버튼 찾는 중...")
                        download_button_selector = "body > div.pointer-events-none.fixed.bottom-0.right-0.z-30.flex.items-center.justify-center.duration-100.left-\\[384px\\].xl\\:left-\\[560px\\] > div > div.ml-auto.flex.gap-2 > div.flex > button"
                        
                        download_btn = None
                        try:
                            download_btn = await page.wait_for_selector(download_button_selector, timeout=5000)
                            print("✓ 다운로드 버튼 찾음")
                        except:
                            # JavaScript로 찾기 시도
                            download_btn = await page.evaluate_handle("""
                                () => {
                                    const buttons = Array.from(document.querySelectorAll('button'));
                                    return buttons.find(btn => {
                                        const text = (btn.textContent || '').toLowerCase();
                                        return text.includes('download') || text.includes('다운로드');
                                    });
                                }
                            """)
                            if download_btn and await download_btn.evaluate("el => el !== null"):
                                print("✓ 다운로드 버튼 찾음 (JavaScript 기반)")
                            else:
                                download_btn = None
                        
                        if download_btn:
                            await download_btn.click()
                            print(f"✓ 다운로드 버튼 클릭 완료! (model_{model_idx}_clothes_{clothes_idx})")
                            await asyncio.sleep(2.0)  # 다운로드 시작 대기
                            return True
                        else:
                            print("✗ 다운로드 버튼을 찾을 수 없습니다.")
                            return False
                    else:
                        print("✗ 체크박스 버튼을 찾을 수 없습니다.")
                        return False
                        
                except Exception as e:
                    print(f"✗ 체크박스/다운로드 중 오류 발생: {e}")
                    return False
            
            # 업로드된 파일 삭제 함수 (ver2.2와 동일)
            async def delete_uploaded_file(file_index):
                """업로드된 파일의 X 버튼 클릭하여 삭제"""
                print(f"\n=== 업로드된 파일 삭제 ({file_index}번째 파일) ===")
                try:
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
            
            # 업로드 버튼 셀렉터
            upload_selector_1 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(3) > div > div > div > div.absolute.inset-0.flex.items-center.justify-center.rounded-lg"
            upload_selector_2 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(4) > div > div > div > div.absolute.inset-0.flex.items-center.justify-center.rounded-lg"
            
            # 삭제 버튼 셀렉터
            delete_selector_1 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(3) > div > div > div > button"
            delete_selector_2 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(4) > div > div > div > button"
            
            # 이중 루프 시작
            total_work = 0
            print("\n" + "=" * 60)
            print("이중 루프 자동화 시작! (Download 기능 포함)")
            print("외부 루프: clothes 1~8 (8번)")
            print("내부 루프: model 1~8 (8번)")
            print("총 작업 횟수: 64번")
            print("=" * 60)
            
            # 외부 루프: clothes 1~8
            for clothes_idx in range(1, 9):
                print(f"\n{'='*60}")
                print(f"외부 루프: clothes {clothes_idx}.png")
                print(f"{'='*60}")
                
                # 내부 루프: model 1~8
                for model_idx in range(1, 9):
                    total_work += 1
                    print(f"\n{'─'*60}")
                    print(f"작업 {total_work}/64: model {model_idx}.png + clothes {clothes_idx}.png")
                    print(f"{'─'*60}")
                    
                    # 1단계: 파일 업로드
                    print(f"\n=== 1단계: 파일 업로드 ===")
                    await upload_file(f"{model_idx}.png", upload_selector_1, MODEL_DIR)
                    await upload_file(f"{clothes_idx}.png", upload_selector_2, CLOTHES_DIR)
                    await asyncio.sleep(1.0)  # 파일 업로드 완료 대기
                    
                    # 2단계: 프롬프트 입력
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
                        print("다음 작업으로 넘어갑니다...")
                        continue
                    
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
                    
                    # 3단계: Generate 버튼 클릭
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
                            print("다음 작업으로 넘어갑니다...")
                            continue
                    
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
                    print("이미지 생성 완료를 감지하고 다운로드합니다...")
                    
                    # 4단계: 이미지 생성 완료 감지 및 다운로드 (새로 추가)
                    download_success = await wait_for_image_completion_and_download(model_idx, clothes_idx)
                    
                    if download_success:
                        print("✓ 이미지 다운로드 완료!")
                    else:
                        print("⚠ 경고: 이미지 다운로드에 실패했을 수 있습니다.")
                    
                    # 5단계: 업로드된 파일 삭제 (2번)
                    print("\n=== 5단계: 업로드된 파일 삭제 ===")
                    
                    # 첫 번째 삭제 버튼 클릭
                    print("첫 번째 삭제 버튼 클릭 중...")
                    try:
                        delete_btn_1 = await page.wait_for_selector(delete_selector_1, timeout=5000)
                        await delete_btn_1.click()
                        print("✓ 첫 번째 삭제 버튼 클릭 완료")
                    except Exception as e:
                        print(f"✗ 첫 번째 삭제 버튼 찾기 실패: {e}")
                        # JavaScript로 찾기 시도
                        try:
                            delete_btn_1 = await page.evaluate_handle("""
                                () => {
                                    const container = document.querySelector('#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3');
                                    if (!container) return null;
                                    const firstItem = container.querySelector('div:nth-child(3)');
                                    if (firstItem) {
                                        const btn = firstItem.querySelector('button.absolute.right-1.top-1');
                                        if (btn) return btn;
                                        const allBtns = firstItem.querySelectorAll('button');
                                        for (let btn of allBtns) {
                                            const svg = btn.querySelector('svg use[xlink\\:href="#cdn-cross-medium"]');
                                            if (svg) return btn;
                                        }
                                    }
                                    return null;
                                }
                            """)
                            if delete_btn_1 and await delete_btn_1.evaluate("el => el !== null"):
                                await delete_btn_1.click()
                                print("✓ 첫 번째 삭제 버튼 클릭 완료 (JavaScript 기반)")
                            else:
                                raise Exception("버튼을 찾을 수 없음")
                        except Exception as e2:
                            print(f"JavaScript 기반 찾기도 실패: {e2}")
                            print("수동으로 첫 번째 삭제 버튼 클릭 후 Enter를 누르세요...")
                            input()
                    
                    # 첫 번째 삭제 후 2초 대기
                    print("첫 번째 파일 삭제 완료. 2초 대기 중...")
                    await asyncio.sleep(2.0)
                    
                    # 두 번째 삭제 버튼 클릭
                    print("두 번째 삭제 버튼 클릭 중...")
                    try:
                        delete_selector_2_after = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(3) > div > div > div > button"
                        delete_btn_2 = await page.wait_for_selector(delete_selector_2_after, timeout=5000)
                        await delete_btn_2.click()
                        print("✓ 두 번째 삭제 버튼 클릭 완료")
                        await asyncio.sleep(1.0)
                    except Exception as e:
                        print(f"✗ 두 번째 삭제 버튼 찾기 실패: {e}")
                        # JavaScript로 찾기 시도
                        try:
                            delete_btn_2 = await page.evaluate_handle("""
                                () => {
                                    const container = document.querySelector('#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3');
                                    if (!container) return null;
                                    const secondItem = container.querySelector('div:nth-child(3)');
                                    if (secondItem) {
                                        const btn = secondItem.querySelector('button.absolute.right-1.top-1');
                                        if (btn) return btn;
                                        const allBtns = secondItem.querySelectorAll('button');
                                        for (let btn of allBtns) {
                                            if (btn.querySelector('svg use[xlink\\:href="#cdn-cross-medium"]')) {
                                                return btn;
                                            }
                                        }
                                    }
                                    const allDeleteBtns = container.querySelectorAll('button.absolute.right-1.top-1');
                                    if (allDeleteBtns.length > 0) {
                                        return allDeleteBtns[0];
                                    }
                                    return null;
                                }
                            """)
                            if delete_btn_2 and await delete_btn_2.evaluate("el => el !== null"):
                                await delete_btn_2.click()
                                print("✓ 두 번째 삭제 버튼 클릭 완료 (JavaScript 기반)")
                                await asyncio.sleep(1.0)
                            else:
                                raise Exception("버튼을 찾을 수 없음")
                        except Exception as e2:
                            print(f"JavaScript 기반 찾기도 실패: {e2}")
                            print("수동으로 두 번째 삭제 버튼 클릭 후 Enter를 누르세요...")
                            input()
                    
                    print(f"✓ 작업 {total_work}/64 완료!")
                    
                    # 다음 작업 전 대기 (마지막 작업이 아닌 경우)
                    if not (clothes_idx == 8 and model_idx == 8):
                        print("다음 작업을 위해 2초 대기 중...")
                        await asyncio.sleep(2.0)
            
            # 모든 작업 완료
            print("\n" + "=" * 60)
            print("모든 작업 완료!")
            print(f"총 {total_work}개의 작업을 완료했습니다.")
            print(f"다운로드 폴더: {DOWNLOAD_DIR}")
            print("=" * 60)
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


if __name__ == "__main__":
    asyncio.run(connect_and_work())


