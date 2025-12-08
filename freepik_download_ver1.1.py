"""
Freepik 다운로드 기능 - ver1.1
체크박스 클릭 및 다운로드 버튼 클릭 기능
다운로드 파일을 지정 폴더에 저장
"""
import asyncio
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# 다운로드 폴더 설정
DOWNLOAD_DIR = Path(r"D:\private\코딩\커서\new\download")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def test_checkbox():
    """체크박스 클릭 테스트"""
    print("=" * 60)
    print("Freepik 체크박스 클릭 테스트")
    print("=" * 60)
    print("\n중요: 크롬을 디버깅 모드로 실행해야 합니다!")
    print("\n준비사항:")
    print("1. 크롬 디버깅 모드 실행 (fix_chrome_debug.bat)")
    print("2. Freepik에 로그인")
    print("3. 이미 생성된 이미지가 있는 페이지로 이동")
    print("\n준비되면 Enter를 누르세요...")
    input()
    
    async with async_playwright() as p:
        try:
            # 연결
            print("\n크롬 브라우저에 연결 중...")
            browser = None
            try:
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=30000)
                print("✓ 브라우저 연결 성공!")
            except Exception as e1:
                print(f"  IPv4 연결 실패: {e1}")
                print("  IPv6 localhost로 재시도 중...")
                try:
                    browser = await p.chromium.connect_over_cdp("http://localhost:9222", timeout=30000)
                    print("✓ 브라우저 연결 성공!")
                except Exception as e2:
                    print(f"  IPv6 연결도 실패: {e2}")
                    raise Exception("크롬 디버깅 모드에 연결할 수 없습니다.")
            
            # 페이지 찾기
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
                page = pages[0]
            
            if not page:
                page = await context.new_page()
            
            # 다운로드 이벤트 핸들러 설정 (여러 방법 시도)
            download_paths = []
            download_event_received = asyncio.Event()
            latest_download = None
            
            async def handle_download(download):
                """다운로드 파일을 지정 폴더로 저장"""
                nonlocal latest_download
                try:
                    latest_download = download
                    download_event_received.set()
                    
                    # 다운로드 파일명 가져오기
                    suggested_filename = download.suggested_filename
                    if not suggested_filename:
                        suggested_filename = f"download_{len(download_paths) + 1}.png"
                    
                    # 저장 경로 설정
                    save_path = DOWNLOAD_DIR / suggested_filename
                    
                    # 파일명 중복 방지
                    counter = 1
                    original_path = save_path
                    while save_path.exists():
                        stem = original_path.stem
                        suffix = original_path.suffix
                        save_path = DOWNLOAD_DIR / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    print(f"\n[다운로드] 파일 저장 중: {save_path.name}")
                    # download.saveAs()로 지정 폴더에 저장
                    await download.save_as(save_path)
                    download_paths.append(save_path)
                    print(f"✓ 다운로드 완료: {save_path}")
                except Exception as e:
                    print(f"⚠ 다운로드 이벤트 처리 중 오류: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 다운로드 이벤트 리스너 등록 (여러 방법 시도)
            print(f"다운로드 폴더: {DOWNLOAD_DIR}")
            
            # 방법 1: page.on("download") 사용
            try:
                page.on("download", handle_download)
                print("✓ 다운로드 이벤트 리스너 등록됨 (page.on)")
            except Exception as e:
                print(f"⚠ page.on 등록 실패: {e}")
            
            # 방법 2: context.on("page")로도 시도
            try:
                async def context_page_handler(new_page):
                    new_page.on("download", handle_download)
                context.on("page", context_page_handler)
                print("✓ 컨텍스트 페이지 핸들러 등록됨")
            except Exception as e:
                print(f"⚠ 컨텍스트 핸들러 등록 실패: {e}")
            
            # 방법 3: 모든 페이지에 핸들러 등록
            try:
                for p in pages:
                    try:
                        p.on("download", handle_download)
                        print(f"✓ 페이지 핸들러 등록됨: {p.url[:50]}")
                    except:
                        pass
            except Exception as e:
                print(f"⚠ 페이지 핸들러 등록 실패: {e}")
            
            print(f"현재 페이지: {page.url}")
            
            if "freepik.com" not in page.url:
                print("Freepik 페이지로 이동 중...")
                await page.goto("https://www.freepik.com/ai/image-generator")
                await asyncio.sleep(2)
                print("이미 생성된 이미지가 있는 페이지로 이동해주세요.")
                input("준비되면 Enter를 누르세요...")
            
            print("\n" + "=" * 60)
            print("체크박스 찾기 시작")
            print("=" * 60)
            
            # 방법 1: 이미지 항목 컨테이너 찾기
            print("\n[방법 1] 이미지 항목 컨테이너 찾기...")
            
            # div[id^='item-'] 요소 찾기 (생성된 이미지 항목)
            item_selectors = [
                "div[id^='item-']",
                "div[data-item]",
                "#tool-layout-main div.relative.w-full > div:first-child",
            ]
            
            item_container = None
            for selector in item_selectors:
                try:
                    item_container = await page.wait_for_selector(selector, timeout=3000, state="visible")
                    if item_container:
                        print(f"✓ 항목 컨테이너 찾음: {selector}")
                        break
                except:
                    continue
            
            if not item_container:
                print("✗ 이미지 항목 컨테이너를 찾을 수 없습니다.")
                print("\n페이지 구조 확인 중...")
                page_info = await page.evaluate("""
                    () => {
                        const main = document.querySelector('#tool-layout-main');
                        if (!main) return { error: 'tool-layout-main not found' };
                        
                        const items = main.querySelectorAll('div[id^="item-"]');
                        const relativeDivs = main.querySelectorAll('div.relative.w-full');
                        
                        return {
                            itemsCount: items.length,
                            relativeDivsCount: relativeDivs.length,
                            firstItemId: items.length > 0 ? items[0].id : null,
                            html: main.innerHTML.substring(0, 1000)
                        };
                    }
                """)
                print(f"페이지 정보: {page_info}")
                return
            
            # 방법 2: 체크박스 버튼 직접 찾기
            print("\n[방법 2] 체크박스 버튼 직접 찾기...")
            
            checkbox_selectors = [
                # 사용자 제공 셀렉터
                "#tool-layout-main > div > div.flex.flex-col.gap-2\\.5 > div.relative.w-full > div:nth-child(1) > div > div > div.border-surface-border-alpha-1.ml-auto.flex.items-center.gap-2.border-l.pl-2 > button",
                # 더 간단한 셀렉터
                "div.border-l.pl-2 > button",
                "div.ml-auto.flex.items-center.gap-2.border-l.pl-2 > button",
                # select-checkbox 클래스 사용
                "div.select-checkbox > button",
                # aria-pressed 속성 사용
                "button[aria-pressed]",
            ]
            
            checkbox_button = None
            for selector in checkbox_selectors:
                try:
                    checkbox_button = await page.wait_for_selector(selector, timeout=2000, state="visible")
                    if checkbox_button:
                        print(f"✓ 체크박스 버튼 찾음: {selector}")
                        break
                except:
                    continue
            
            # 방법 3: JavaScript로 찾기
            if not checkbox_button:
                print("\n[방법 3] JavaScript로 체크박스 찾기...")
                try:
                    checkbox_button = await page.evaluate_handle("""
                        () => {
                            // 1. select-checkbox 클래스 찾기
                            const selectCheckbox = document.querySelector('div.select-checkbox > button');
                            if (selectCheckbox) return selectCheckbox;
                            
                            // 2. border-l.pl-2 클래스를 가진 div 안의 button 찾기
                            const borderDivs = document.querySelectorAll('div.border-l.pl-2');
                            for (const div of borderDivs) {
                                const btn = div.querySelector('button');
                                if (btn) return btn;
                            }
                            
                            // 3. tool-layout-main 내부의 첫 번째 이미지 항목에서 찾기
                            const main = document.querySelector('#tool-layout-main');
                            if (main) {
                                const firstItem = main.querySelector('div[id^="item-"]');
                                if (firstItem) {
                                    const btn = firstItem.querySelector('div.border-l.pl-2 > button');
                                    if (btn) return btn;
                                    
                                    // 또는 모든 버튼 중에서
                                    const buttons = firstItem.querySelectorAll('button');
                                    for (const btn of buttons) {
                                        const parent = btn.closest('div.border-l.pl-2');
                                        if (parent) return btn;
                                    }
                                }
                            }
                            
                            return null;
                        }
                    """)
                    
                    if checkbox_button:
                        exists = await checkbox_button.evaluate("el => el !== null")
                        if exists:
                            print("✓ 체크박스 버튼 찾음 (JavaScript)")
                        else:
                            checkbox_button = None
                except Exception as e:
                    print(f"JavaScript 찾기 실패: {e}")
            
            if not checkbox_button:
                print("\n✗ 체크박스 버튼을 찾을 수 없습니다.")
                print("\n디버깅 정보:")
                debug_info = await page.evaluate("""
                    () => {
                        const main = document.querySelector('#tool-layout-main');
                        if (!main) return { error: 'main not found' };
                        
                        const buttons = main.querySelectorAll('button');
                        const buttonInfo = Array.from(buttons).slice(0, 10).map((btn, idx) => {
                            const parent = btn.parentElement;
                            return {
                                index: idx,
                                hasAriaPressed: btn.hasAttribute('aria-pressed'),
                                ariaPressed: btn.getAttribute('aria-pressed'),
                                parentClasses: parent ? parent.className : '',
                                hasSpan: btn.querySelector('span') !== null,
                                innerHTML: btn.innerHTML.substring(0, 150)
                            };
                        });
                        
                        return {
                            totalButtons: buttons.length,
                            buttonInfo: buttonInfo
                        };
                    }
                """)
                print(f"{debug_info}")
                return
            
            # 현재 상태 확인
            print("\n" + "=" * 60)
            print("체크박스 상태 확인")
            print("=" * 60)
            
            current_state = await checkbox_button.evaluate("""
                (btn) => {
                    const ariaPressed = btn.getAttribute('aria-pressed');
                    const span = btn.querySelector('span');
                    const hasBlueBg = span && (span.className.includes('bg-piki-blue-500') || span.className.includes('bg-piki-blue'));
                    const svg = span ? span.querySelector('svg') : null;
                    const use = svg ? svg.querySelector('use') : null;
                    const href = use ? (use.getAttribute('xlink:href') || use.getAttribute('href')) : '';
                    const hasCheckIcon = href === '#cdn-check';
                    
                    return {
                        ariaPressed: ariaPressed,
                        hasSpan: span !== null,
                        hasBlueBg: hasBlueBg,
                        hasCheckIcon: hasCheckIcon,
                        isChecked: ariaPressed === 'true' || hasBlueBg,
                        spanClasses: span ? span.className : null
                    };
                }
            """)
            
            print(f"현재 상태: {current_state}")
            
            if current_state.get('isChecked'):
                print("\n⚠ 이미 체크되어 있습니다.")
                print("체크 해제 후 다시 테스트하시겠습니까? (y/n)")
                response = input().strip().lower()
                if response == 'y':
                    print("체크 해제 중...")
                    await checkbox_button.click()
                    await asyncio.sleep(1.5)
                    print("✓ 체크 해제 완료")
                else:
                    print("테스트 종료")
                    return
            
            # 호버하여 체크박스가 보이도록
            print("\n" + "=" * 60)
            print("체크박스 클릭 시도")
            print("=" * 60)
            
            print("\n[1] 스크롤하여 요소가 보이도록...")
            await checkbox_button.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            
            print("[2] 마우스 호버...")
            await checkbox_button.hover()
            await asyncio.sleep(1.0)
            
            print("[3] 체크박스 클릭...")
            await checkbox_button.click()
            await asyncio.sleep(1.5)
            
            # 클릭 후 상태 확인
            print("\n[4] 클릭 후 상태 확인...")
            final_state = await checkbox_button.evaluate("""
                (btn) => {
                    const ariaPressed = btn.getAttribute('aria-pressed');
                    const span = btn.querySelector('span');
                    const hasBlueBg = span && (span.className.includes('bg-piki-blue-500') || span.className.includes('bg-piki-blue'));
                    const svg = span ? span.querySelector('svg') : null;
                    const use = svg ? svg.querySelector('use') : null;
                    const href = use ? (use.getAttribute('xlink:href') || use.getAttribute('href')) : '';
                    const hasCheckIcon = href === '#cdn-check';
                    
                    return {
                        ariaPressed: ariaPressed,
                        hasSpan: span !== null,
                        hasBlueBg: hasBlueBg,
                        hasCheckIcon: hasCheckIcon,
                        isChecked: ariaPressed === 'true' || hasBlueBg,
                        spanClasses: span ? span.className : null,
                        svgHTML: svg ? svg.innerHTML.substring(0, 200) : null
                    };
                }
            """)
            
            print(f"최종 상태: {final_state}")
            
            if final_state.get('isChecked'):
                print("\n" + "=" * 60)
                print("✓✓✓ 체크박스 클릭 성공! ✓✓✓")
                print("=" * 60)
                if final_state.get('hasBlueBg'):
                    print("✓ 파란 배경 (bg-piki-blue-500) 확인")
                if final_state.get('hasCheckIcon'):
                    print("✓ 체크 아이콘 (#cdn-check) 확인")
                if final_state.get('ariaPressed') == 'true':
                    print("✓ aria-pressed='true' 확인")
                
                # 다운로드 버튼 클릭
                print("\n" + "=" * 60)
                print("다운로드 버튼 찾기 및 클릭")
                print("=" * 60)
                
                download_button_selector = "body > div.pointer-events-none.fixed.bottom-0.right-0.z-30.flex.items-center.justify-center.duration-100.left-\\[384px\\].xl\\:left-\\[560px\\] > div > div.ml-auto.flex.gap-2 > div.flex > button"
                
                print("\n[1] 다운로드 버튼이 나타날 때까지 대기 중...")
                download_button = None
                
                # 버튼이 나타날 때까지 최대 5초 대기
                for i in range(10):
                    try:
                        download_button = await page.query_selector(download_button_selector)
                        if download_button:
                            # 버튼이 보이는지 확인
                            is_visible = await download_button.is_visible()
                            if is_visible:
                                print(f"✓ 다운로드 버튼 발견! (시도 {i+1}/10)")
                                break
                    except:
                        pass
                    
                    await asyncio.sleep(0.5)
                
                if not download_button:
                    # 대안 셀렉터 시도
                    print("\n[2] 대안 셀렉터로 찾기 시도...")
                    alternative_selectors = [
                        "div.fixed.bottom-0.right-0.z-30 button",
                        "div.fixed.bottom-0 button",
                        "button:has-text('Download')",
                        "button:has-text('다운로드')",
                    ]
                    
                    for alt_selector in alternative_selectors:
                        try:
                            download_button = await page.wait_for_selector(alt_selector, timeout=2000, state="visible")
                            if download_button:
                                print(f"✓ 다운로드 버튼 발견! (대안 셀렉터: {alt_selector})")
                                break
                        except:
                            continue
                
                if not download_button:
                    # JavaScript로 찾기
                    print("\n[3] JavaScript로 다운로드 버튼 찾기...")
                    try:
                        download_button = await page.evaluate_handle("""
                            () => {
                                // 고정된 하단 버튼 찾기
                                const fixedDivs = document.querySelectorAll('div.fixed.bottom-0.right-0');
                                for (const div of fixedDivs) {
                                    const button = div.querySelector('button');
                                    if (button && button.offsetParent !== null) {
                                        return button;
                                    }
                                }
                                
                                // z-30 클래스를 가진 고정 div 찾기
                                const z30Divs = document.querySelectorAll('div.z-30.fixed.bottom-0');
                                for (const div of z30Divs) {
                                    const button = div.querySelector('button');
                                    if (button && button.offsetParent !== null) {
                                        return button;
                                    }
                                }
                                
                                return null;
                            }
                        """)
                        
                        if download_button:
                            exists = await download_button.evaluate("el => el !== null && el.offsetParent !== null")
                            if exists:
                                print("✓ 다운로드 버튼 발견! (JavaScript)")
                            else:
                                download_button = None
                    except Exception as e:
                        print(f"JavaScript 찾기 실패: {e}")
                
                if download_button:
                    print("\n[4] 다운로드 버튼 클릭 중...")
                    try:
                        # 버튼이 보이도록 스크롤
                        await download_button.scroll_into_view_if_needed()
                        await asyncio.sleep(0.3)
                        
                        # 버튼 정보 확인
                        button_info = await download_button.evaluate("""
                            (btn) => {
                                return {
                                    text: btn.textContent.trim(),
                                    disabled: btn.disabled,
                                    visible: btn.offsetParent !== null,
                                    classes: btn.className
                                };
                            }
                        """)
                        print(f"버튼 정보: {button_info}")
                        
                        if button_info.get('disabled'):
                            print("⚠ 버튼이 비활성화되어 있습니다.")
                        else:
                            # 방법 3: CDP를 통한 다운로드 리스트 확인
                            print("\n[방법 3] CDP를 통한 다운로드 리스트 확인")
                            
                            # CDP 세션 가져오기
                            cdp_session = await context.new_cdp_session(page)
                            
                            # 다운로드 시작 전 다운로드 리스트 확인
                            print("다운로드 시작 전 상태 확인 중...")
                            initial_downloads = []
                            try:
                                # Browser.getDownloadPath 또는 다운로드 리스트 가져오기
                                # CDP를 통해 다운로드 이벤트 리스너 등록
                                await cdp_session.send("Browser.setDownloadBehavior", {
                                    "behavior": "allow",
                                    "downloadPath": str(DOWNLOAD_DIR)
                                })
                                print(f"✓ 다운로드 경로 설정: {DOWNLOAD_DIR}")
                            except Exception as e:
                                print(f"⚠ 다운로드 경로 설정 실패: {e}")
                            
                            # 다운로드 이벤트 리스너 설정
                            download_info = {}
                            
                            async def handle_cdp_download(event):
                                """CDP 다운로드 이벤트 처리"""
                                try:
                                    if event.get('method') == 'Browser.downloadProgress':
                                        params = event.get('params', {})
                                        guid = params.get('guid')
                                        state = params.get('state')
                                        
                                        if guid:
                                            if guid not in download_info:
                                                download_info[guid] = {}
                                            
                                            download_info[guid]['state'] = state
                                            
                                            if 'receivedBytes' in params:
                                                download_info[guid]['receivedBytes'] = params['receivedBytes']
                                            if 'totalBytes' in params:
                                                download_info[guid]['totalBytes'] = params['totalBytes']
                                            
                                            if state == 'completed':
                                                # 다운로드 완료
                                                if 'url' in params:
                                                    download_info[guid]['url'] = params['url']
                                                if 'suggestedFilename' in params:
                                                    download_info[guid]['filename'] = params['suggestedFilename']
                                                
                                                print(f"✓ 다운로드 완료 감지: {download_info[guid].get('filename', 'unknown')}")
                                
                                except Exception as e:
                                    print(f"CDP 이벤트 처리 오류: {e}")
                            
                            # CDP 이벤트 리스너 등록
                            cdp_session.on("Browser.downloadProgress", handle_cdp_download)
                            
                            # 버튼 클릭
                            await download_button.click()
                            await asyncio.sleep(0.5)
                            print("✓✓✓ 다운로드 버튼 클릭 성공! ✓✓✓")
                            print("\n다운로드 진행 상황을 모니터링 중...")
                            
                            # 다운로드 완료 대기
                            downloaded_file = None
                            for i in range(60):  # 최대 30초 대기
                                await asyncio.sleep(0.5)
                                
                                # 완료된 다운로드 확인
                                for guid, info in download_info.items():
                                    if info.get('state') == 'completed':
                                        downloaded_file = info
                                        break
                                
                                if downloaded_file:
                                    break
                                
                                # 진행 상황 출력
                                if i % 10 == 0 and download_info:
                                    for guid, info in download_info.items():
                                        state = info.get('state', 'unknown')
                                        received = info.get('receivedBytes', 0)
                                        total = info.get('totalBytes', 0)
                                        if total > 0:
                                            percent = (received / total) * 100
                                            print(f"  다운로드 진행: {percent:.1f}% ({received}/{total} bytes)")
                            
                            # 다운로드된 파일 처리
                            if downloaded_file:
                                filename = downloaded_file.get('filename', f"download_{len(download_paths) + 1}.png")
                                print(f"\n✓ 다운로드 완료: {filename}")
                                
                                # 파일 경로 찾기
                                # CDP를 통해 실제 파일 경로 가져오기 시도
                                try:
                                    # 다운로드 폴더에서 파일 찾기
                                    download_path = DOWNLOAD_DIR / filename
                                    
                                    # 파일이 없으면 Temp 폴더에서 찾기
                                    if not download_path.exists():
                                        temp_base = Path(tempfile.gettempdir())
                                        for item in temp_base.iterdir():
                                            if item.is_dir() and item.name.startswith("playwright-artifacts-"):
                                                for file_path in item.rglob(filename):
                                                    if file_path.is_file():
                                                        download_path = file_path
                                                        print(f"✓ 파일 발견: {download_path}")
                                                        break
                                                if download_path.exists():
                                                    break
                                    
                                    if download_path.exists():
                                        # 파일명 중복 방지
                                        save_path = DOWNLOAD_DIR / filename
                                        counter = 1
                                        original_path = save_path
                                        while save_path.exists() and save_path != download_path:
                                            stem = original_path.stem
                                            suffix = original_path.suffix
                                            save_path = DOWNLOAD_DIR / f"{stem}_{counter}{suffix}"
                                            counter += 1
                                        
                                        # 파일 복사 또는 이동
                                        if download_path != save_path:
                                            shutil.copy2(str(download_path), str(save_path))
                                            print(f"✓ 파일 복사 완료: {save_path.name}")
                                        else:
                                            print(f"✓ 파일이 이미 올바른 위치에 있습니다: {save_path}")
                                        
                                        print(f"\n✓✓✓ 다운로드 완료! ✓✓✓")
                                        print(f"저장 위치: {save_path}")
                                    else:
                                        print(f"\n⚠ 파일을 찾을 수 없습니다: {filename}")
                                        print(f"다운로드 폴더: {DOWNLOAD_DIR}")
                                
                                except Exception as e:
                                    print(f"\n✗ 파일 처리 중 오류: {e}")
                                    import traceback
                                    traceback.print_exc()
                            else:
                                print("\n⚠ 다운로드 완료를 감지하지 못했습니다.")
                                print(f"다운로드 폴더: {DOWNLOAD_DIR}")
                                print("브라우저의 다운로드 폴더를 확인해주세요.")
                            
                            await asyncio.sleep(1.0)
                    except Exception as e:
                        print(f"✗ 다운로드 버튼 클릭 실패: {e}")
                else:
                    print("\n✗ 다운로드 버튼을 찾을 수 없습니다.")
                    print("\n디버깅 정보:")
                    debug_info = await page.evaluate("""
                        () => {
                            const fixedDivs = document.querySelectorAll('div.fixed.bottom-0');
                            const buttonInfo = [];
                            
                            fixedDivs.forEach((div, idx) => {
                                const buttons = div.querySelectorAll('button');
                                buttons.forEach((btn, btnIdx) => {
                                    buttonInfo.push({
                                        divIndex: idx,
                                        buttonIndex: btnIdx,
                                        text: btn.textContent.trim(),
                                        visible: btn.offsetParent !== null,
                                        classes: btn.className,
                                        parentClasses: div.className
                                    });
                                });
                            });
                            
                            return {
                                fixedDivsCount: fixedDivs.length,
                                buttonInfo: buttonInfo
                            };
                        }
                    """)
                    print(f"{debug_info}")
            else:
                print("\n" + "=" * 60)
                print("✗ 체크박스 클릭 실패")
                print("=" * 60)
                print("\n브라우저에서 수동으로 확인해주세요.")
            
            print("\n브라우저를 닫지 마세요.")
            print("프로그램을 종료하려면 Enter를 누르세요...")
            input()
            
        except Exception as e:
            print(f"\n✗ 에러 발생: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_checkbox())

