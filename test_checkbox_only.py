"""
Freepik 체크박스 기능 테스트 - 체크 표시만 테스트
"""
import asyncio
from playwright.async_api import async_playwright


async def test_checkbox():
    """체크박스 클릭 테스트"""
    print("=" * 50)
    print("Freepik 체크박스 기능 테스트")
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
            # 디버깅 포트로 연결 (IPv4 localhost 사용)
            print("\n크롬 브라우저에 연결 중...")
            print("  연결 URL: http://127.0.0.1:9222")
            
            browser = None
            connection_error = None
            
            # IPv4 localhost로 먼저 시도
            try:
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=30000)
                print("✓ 브라우저 연결 성공! (IPv4)")
            except Exception as e1:
                connection_error = e1
                print(f"  IPv4 연결 실패: {e1}")
                print("  IPv6 localhost로 재시도 중...")
                try:
                    browser = await p.chromium.connect_over_cdp("http://localhost:9222", timeout=30000)
                    print("✓ 브라우저 연결 성공! (IPv6)")
                except Exception as e2:
                    print(f"  IPv6 연결도 실패: {e2}")
                    print("\n✗ 연결 실패!")
                    print("\n문제 해결 방법:")
                    print("1. 크롬이 디버깅 모드로 실행되었는지 확인하세요")
                    print("   → start_chrome_debug.bat 파일을 실행했나요?")
                    print("2. 모든 크롬 창을 닫고 start_chrome_debug.bat를 다시 실행하세요")
                    print("3. 포트 9222가 사용 중인지 확인하세요")
                    raise e2
            
            if not browser:
                raise connection_error or Exception("브라우저 연결 실패")
            
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
            
            # 체크박스 클릭 함수
            async def click_checkbox():
                """체크박스 클릭하여 체크 표시"""
                print("\n=== 체크박스 클릭 테스트 ===")
                
                try:
                    # 체크 후 나타나는 span 셀렉터
                    checked_span_selector = "#tool-layout-main > div > div.flex.flex-col.gap-2\\.5 > div.relative.w-full > div:nth-child(1) > div > div > div.border-surface-border-alpha-1.ml-auto.flex.items-center.gap-2.border-l.pl-2 > button > span"
                    
                    # 버튼 셀렉터 (span의 부모)
                    checkbox_button_selector = "#tool-layout-main > div > div.flex.flex-col.gap-2\\.5 > div.relative.w-full > div:nth-child(1) > div > div > div.border-surface-border-alpha-1.ml-auto.flex.items-center.gap-2.border-l.pl-2 > button"
                    
                    print("체크박스 버튼 찾는 중...")
                    
                    # 먼저 체크 후 span이 이미 있는지 확인
                    checked_span_before = None
                    try:
                        checked_span_before = await page.query_selector(checked_span_selector)
                        if checked_span_before:
                            print("⚠ 체크 후 span이 이미 존재합니다. (이미 체크된 상태일 수 있음)")
                    except:
                        pass
                    
                    # 버튼 찾기 (여러 방법 시도)
                    checkbox_btn = None
                    
                    # 방법 1: CSS 셀렉터로 찾기
                    try:
                        checkbox_btn = await page.wait_for_selector(checkbox_button_selector, timeout=5000)
                        print("✓ 체크박스 버튼 찾음 (CSS 셀렉터)")
                    except Exception as e:
                        print(f"CSS 셀렉터로 찾기 실패: {e}")
                    
                    # 방법 2: JavaScript로 찾기 (border-l.pl-2)
                    if not checkbox_btn:
                        print("JavaScript로 찾는 중...")
                        try:
                            checkbox_btn = await page.evaluate_handle("""
                                () => {
                                    const container = document.querySelector('#tool-layout-main > div > div.flex.flex-col.gap-2\\.5');
                                    if (!container) return null;
                                    
                                    // border-l.pl-2 클래스를 가진 div 찾기
                                    const borderDiv = container.querySelector('div.border-l.pl-2');
                                    if (borderDiv) {
                                        const btn = borderDiv.querySelector('button');
                                        if (btn) return btn;
                                    }
                                    
                                    return null;
                                }
                            """)
                            
                            if checkbox_btn and await checkbox_btn.evaluate("el => el !== null"):
                                print("✓ 체크박스 버튼 찾음 (JavaScript 기반 - border-l.pl-2)")
                            else:
                                checkbox_btn = None
                        except Exception as e:
                            print(f"JavaScript 찾기 실패: {e}")
                    
                    # 방법 3: 더 넓은 범위로 찾기
                    if not checkbox_btn:
                        print("더 넓은 범위로 찾는 중...")
                        try:
                            checkbox_btn = await page.evaluate_handle("""
                                () => {
                                    // tool-layout-main 내부의 모든 버튼 찾기
                                    const container = document.querySelector('#tool-layout-main');
                                    if (!container) return null;
                                    
                                    // flex.flex-col.gap-2.5 컨테이너 찾기
                                    const flexContainer = container.querySelector('div.flex.flex-col.gap-2\\.5');
                                    if (!flexContainer) return null;
                                    
                                    // relative.w-full 내부 찾기
                                    const relativeDiv = flexContainer.querySelector('div.relative.w-full');
                                    if (!relativeDiv) return null;
                                    
                                    // 첫 번째 div:nth-child(1) 찾기
                                    const firstDiv = relativeDiv.querySelector('div:nth-child(1)');
                                    if (!firstDiv) return null;
                                    
                                    // border-l.pl-2를 가진 div 찾기
                                    const borderDivs = firstDiv.querySelectorAll('div.border-l.pl-2');
                                    for (const borderDiv of borderDivs) {
                                        const btn = borderDiv.querySelector('button');
                                        if (btn) return btn;
                                    }
                                    
                                    // 대안: 모든 버튼 중에서 체크박스처럼 보이는 것 찾기
                                    const allButtons = firstDiv.querySelectorAll('button');
                                    for (const btn of allButtons) {
                                        // span이 있고, border-l.pl-2를 가진 부모가 있는 버튼
                                        const parent = btn.closest('div.border-l.pl-2');
                                        if (parent) return btn;
                                    }
                                    
                                    return null;
                                }
                            """)
                            
                            if checkbox_btn and await checkbox_btn.evaluate("el => el !== null"):
                                print("✓ 체크박스 버튼 찾음 (JavaScript 기반 - 넓은 범위)")
                            else:
                                checkbox_btn = None
                        except Exception as e:
                            print(f"넓은 범위 찾기 실패: {e}")
                    
                    # 방법 4: 페이지 구조 출력하여 디버깅
                    if not checkbox_btn:
                        print("\n⚠ 버튼을 찾을 수 없습니다. 페이지 구조 확인 중...")
                        page_structure = await page.evaluate("""
                            () => {
                                const container = document.querySelector('#tool-layout-main > div > div.flex.flex-col.gap-2\\.5');
                                if (!container) return { error: 'container not found' };
                                
                                const relativeDiv = container.querySelector('div.relative.w-full');
                                if (!relativeDiv) return { error: 'relative div not found', containerHTML: container.innerHTML.substring(0, 500) };
                                
                                const firstDiv = relativeDiv.querySelector('div:nth-child(1)');
                                if (!firstDiv) return { error: 'first div not found', relativeHTML: relativeDiv.innerHTML.substring(0, 500) };
                                
                                const buttons = firstDiv.querySelectorAll('button');
                                const buttonInfo = Array.from(buttons).map((btn, idx) => {
                                    const parent = btn.parentElement;
                                    return {
                                        index: idx,
                                        hasSpan: btn.querySelector('span') !== null,
                                        parentClasses: parent ? parent.className : '',
                                        ariaPressed: btn.getAttribute('aria-pressed'),
                                        innerHTML: btn.innerHTML.substring(0, 200)
                                    };
                                });
                                
                                return {
                                    buttonsFound: buttons.length,
                                    buttonInfo: buttonInfo
                                };
                            }
                        """)
                        print(f"페이지 구조: {page_structure}")
                    
                    if not checkbox_btn:
                        print("✗ 체크박스 버튼을 찾을 수 없습니다.")
                        return False
                    
                    # 현재 상태 확인
                    is_checked_before = await checkbox_btn.get_attribute("aria-pressed")
                    print(f"클릭 전 체크 상태 (aria-pressed): {is_checked_before}")
                    
                    # 체크 후 span 존재 여부 확인 (bg-piki-blue-500 클래스 확인)
                    span_exists_before = await checkbox_btn.evaluate("""
                        (btn) => {
                            const span = btn.querySelector('span');
                            if (!span) return { exists: false };
                            
                            const spanClasses = span.className;
                            const hasBlueBg = spanClasses.includes('bg-piki-blue-500') || spanClasses.includes('bg-piki-blue');
                            
                            const svg = span.querySelector('svg');
                            if (!svg) return { exists: true, hasBlueBg: hasBlueBg, hasSvg: false };
                            
                            const use = svg.querySelector('use');
                            const href = use ? (use.getAttribute('xlink:href') || use.getAttribute('href')) : null;
                            const hasCheckIcon = href === '#cdn-check';
                            
                            const svgClasses = svg.className;
                            const hasOpacity100 = svgClasses.includes('opacity-100');
                            
                            return {
                                exists: true,
                                hasBlueBg: hasBlueBg,
                                hasSvg: true,
                                hasCheckIcon: hasCheckIcon,
                                hasOpacity100: hasOpacity100,
                                isChecked: hasBlueBg && hasCheckIcon
                            };
                        }
                    """)
                    print(f"클릭 전 체크 span 상태: {span_exists_before}")
                    
                    if (is_checked_before == "true" or span_exists_before.get('isChecked')):
                        print("✓ 이미 체크되어 있습니다.")
                        print("체크 해제 후 다시 테스트하시겠습니까? (y/n)")
                        response = input().strip().lower()
                        if response == 'y':
                            print("체크 해제 중...")
                            await checkbox_btn.click()
                            await asyncio.sleep(1.5)
                            # 해제 확인
                            is_unchecked = await checkbox_btn.evaluate("""
                                (btn) => {
                                    const span = btn.querySelector('span');
                                    if (!span) return true; // span이 없으면 해제된 것으로 간주
                                    const spanClasses = span.className;
                                    return !spanClasses.includes('bg-piki-blue-500') && !spanClasses.includes('bg-piki-blue');
                                }
                            """)
                            if is_unchecked:
                                print("✓ 체크 해제 완료")
                            else:
                                print("⚠ 체크 해제 확인 필요 (수동으로 확인해주세요)")
                        else:
                            return True
                    
                    # 버튼 정보 확인
                    btn_info = await checkbox_btn.evaluate("""
                        (btn) => {
                            const rect = btn.getBoundingClientRect();
                            return {
                                visible: rect.width > 0 && rect.height > 0,
                                display: window.getComputedStyle(btn).display,
                                opacity: window.getComputedStyle(btn).opacity,
                                pointerEvents: window.getComputedStyle(btn).pointerEvents,
                                disabled: btn.disabled,
                                ariaPressed: btn.getAttribute('aria-pressed'),
                                hasSpan: btn.querySelector('span') !== null
                            };
                        }
                    """)
                    print(f"\n버튼 정보: {btn_info}")
                    
                    if btn_info.get('disabled'):
                        print("⚠ 버튼이 비활성화되어 있습니다.")
                        return False
                    
                    # 마우스 호버 (체크박스가 나타나도록)
                    print("\n마우스 호버 중...")
                    try:
                        # 호버 전에 스크롤하여 요소가 보이도록
                        await checkbox_btn.scroll_into_view_if_needed()
                        await asyncio.sleep(0.3)
                        await checkbox_btn.hover()
                        await asyncio.sleep(0.8)  # 호버 후 더 긴 대기
                        print("✓ 호버 완료")
                    except Exception as e:
                        print(f"호버 실패: {e}")
                    
                    # 호버 후 span이 나타났는지 확인
                    span_after_hover = await checkbox_btn.evaluate("""
                        (btn) => {
                            const span = btn.querySelector('span');
                            if (!span) return { exists: false };
                            
                            const spanClasses = span.className;
                            const hasBlueBg = spanClasses.includes('bg-piki-blue-500') || spanClasses.includes('bg-piki-blue');
                            
                            return {
                                exists: true,
                                hasBlueBg: hasBlueBg,
                                classes: spanClasses
                            };
                        }
                    """)
                    print(f"호버 후 span 상태: {span_after_hover}")
                    
                    # 체크박스 클릭 (여러 방법 시도)
                    print("\n체크박스 클릭 중...")
                    click_success = False
                    
                    # 방법 1: 일반 클릭
                    try:
                        await checkbox_btn.click(timeout=3000)
                        await asyncio.sleep(1.0)
                        print("✓ 일반 클릭 완료")
                        click_success = True
                    except Exception as e:
                        print(f"일반 클릭 실패: {e}")
                    
                    # 방법 2: JavaScript 클릭
                    if not click_success:
                        try:
                            await checkbox_btn.evaluate("btn => btn.click()")
                            await asyncio.sleep(1.0)
                            print("✓ JavaScript 클릭 완료")
                            click_success = True
                        except Exception as e:
                            print(f"JavaScript 클릭 실패: {e}")
                    
                    # 방법 3: 마우스 이벤트 직접 발생
                    if not click_success:
                        try:
                            await checkbox_btn.evaluate("""
                                (btn) => {
                                    const event = new MouseEvent('click', {
                                        view: window,
                                        bubbles: true,
                                        cancelable: true
                                    });
                                    btn.dispatchEvent(event);
                                }
                            """)
                            await asyncio.sleep(1.0)
                            print("✓ 마우스 이벤트 클릭 완료")
                            click_success = True
                        except Exception as e:
                            print(f"마우스 이벤트 클릭 실패: {e}")
                    
                    # 방법 4: Force 클릭
                    if not click_success:
                        try:
                            await checkbox_btn.click(force=True)
                            await asyncio.sleep(1.0)
                            print("✓ Force 클릭 완료")
                            click_success = True
                        except Exception as e:
                            print(f"Force 클릭 실패: {e}")
                    
                    if not click_success:
                        print("✗ 모든 클릭 방법 실패")
                        return False
                    
                    # 클릭 후 상태 확인
                    is_checked_after = await checkbox_btn.get_attribute("aria-pressed")
                    print(f"\n클릭 후 체크 상태 (aria-pressed): {is_checked_after}")
                    
                    # 클릭 후 실제 체크 상태 확인 (bg-piki-blue-500 클래스)
                    actual_checked_after = await checkbox_btn.evaluate("""
                        (btn) => {
                            const span = btn.querySelector('span');
                            if (!span) return false;
                            const spanClasses = span.className;
                            return spanClasses.includes('bg-piki-blue-500') || spanClasses.includes('bg-piki-blue');
                        }
                    """)
                    print(f"클릭 후 실제 체크 상태 (파란 배경): {actual_checked_after}")
                    
                    # 체크 후 span이 나타났는지 확인 (여러 번 확인)
                    # 사용자 제공 HTML: <span class="flex size-4 items-center justify-center rounded bg-piki-blue-500 text-white">
                    span_appeared = False
                    for i in range(10):  # 더 많이 확인
                        await asyncio.sleep(0.5)
                        span_info = await checkbox_btn.evaluate("""
                            (btn) => {
                                // 버튼 내부의 span 찾기 (체크된 상태)
                                const span = btn.querySelector('span');
                                if (!span) return { exists: false, reason: 'span not found in button', buttonHTML: btn.innerHTML.substring(0, 300) };
                                
                                // span의 클래스 확인 (bg-piki-blue-500가 있으면 체크됨)
                                const spanClasses = span.className;
                                const hasBlueBg = spanClasses.includes('bg-piki-blue-500') || spanClasses.includes('bg-piki-blue');
                                const hasWhiteText = spanClasses.includes('text-white');
                                
                                // span의 직접 자식 SVG 찾기
                                const svg = span.querySelector('svg');
                                if (!svg) {
                                    return { 
                                        exists: true, 
                                        hasSvg: false, 
                                        spanClasses: spanClasses,
                                        innerHTML: span.innerHTML.substring(0, 200),
                                        reason: 'no svg in span'
                                    };
                                }
                                
                                // SVG의 use 요소 찾기
                                const use = svg.querySelector('use');
                                if (!use) {
                                    return { 
                                        exists: true, 
                                        hasSvg: true, 
                                        hasUse: false,
                                        spanClasses: spanClasses,
                                        reason: 'no use element'
                                    };
                                }
                                
                                // xlink:href 또는 href 속성 확인
                                const href = use.getAttribute('xlink:href') || use.getAttribute('href');
                                
                                // SVG의 스타일 확인
                                const svgStyle = window.getComputedStyle(svg);
                                const spanStyle = window.getComputedStyle(span);
                                
                                // SVG 클래스 확인 (opacity-100이 있으면 체크됨)
                                const svgClasses = svg.className;
                                const hasOpacity100 = svgClasses.includes('opacity-100');
                                
                                // 체크 아이콘 확인
                                const hasCheckIcon = href === '#cdn-check';
                                
                                // 체크된 상태인지 확인 (여러 조건)
                                const isChecked = hasBlueBg && hasCheckIcon && (hasOpacity100 || parseFloat(svgStyle.opacity) > 0.9);
                                
                                return {
                                    exists: true,
                                    hasSvg: true,
                                    hasUse: true,
                                    href: href,
                                    hasCheckIcon: hasCheckIcon,
                                    spanClasses: spanClasses,
                                    svgClasses: svgClasses,
                                    hasBlueBg: hasBlueBg,
                                    hasWhiteText: hasWhiteText,
                                    hasOpacity100: hasOpacity100,
                                    svgOpacity: svgStyle.opacity,
                                    svgDisplay: svgStyle.display,
                                    spanOpacity: spanStyle.opacity,
                                    spanDisplay: spanStyle.display,
                                    svgVisible: parseFloat(svgStyle.opacity) > 0 && svgStyle.display !== 'none',
                                    spanVisible: parseFloat(spanStyle.opacity) > 0 && spanStyle.display !== 'none',
                                    isChecked: isChecked,
                                    visible: isChecked && parseFloat(svgStyle.opacity) > 0 && svgStyle.display !== 'none' && parseFloat(spanStyle.opacity) > 0 && spanStyle.display !== 'none'
                                };
                            }
                        """)
                        
                        print(f"체크 span 확인 ({i+1}/10): {span_info}")
                        
                        # 여러 조건으로 확인
                        if span_info.get('exists'):
                            if span_info.get('isChecked'):
                                span_appeared = True
                                print(f"✓✓✓ 체크 표시 확인됨! (시도 {i+1}회) ✓✓✓")
                                print(f"  - 파란 배경: {span_info.get('hasBlueBg')}")
                                print(f"  - 체크 아이콘: {span_info.get('hasCheckIcon')}")
                                print(f"  - opacity-100: {span_info.get('hasOpacity100')}")
                                break
                            elif span_info.get('visible'):
                                span_appeared = True
                                print(f"✓ 체크 표시 확인됨! (시도 {i+1}회)")
                                break
                            elif span_info.get('hasCheckIcon'):
                                # 체크 아이콘이 있으면 일단 성공으로 간주
                                span_appeared = True
                                print(f"✓ 체크 아이콘 확인됨! (시도 {i+1}회, opacity는 낮을 수 있음)")
                                break
                            elif span_info.get('hasSvg'):
                                # SVG가 있으면 일단 성공으로 간주 (opacity 문제일 수 있음)
                                span_appeared = True
                                print(f"⚠ SVG 확인됨 (시도 {i+1}회, opacity 확인 필요)")
                                break
                    
                    # 최종 결과 확인
                    if actual_checked_after or span_appeared:
                        print("\n✓✓✓ 체크 표시 성공! ✓✓✓")
                        if actual_checked_after:
                            print("✓ 파란 배경 (bg-piki-blue-500) 확인")
                        if span_appeared:
                            print("✓ 체크 span 표시 확인")
                        if is_checked_after == "true":
                            print("✓ aria-pressed='true' 확인")
                        return True
                    elif is_checked_after == "true":
                        print("\n⚠ aria-pressed는 변경되었지만 체크 span이 보이지 않을 수 있습니다.")
                        print("✓ aria-pressed='true' 확인")
                        print("브라우저에서 수동으로 확인해주세요.")
                        return True
                    else:
                        print("\n✗ 체크 표시 실패")
                        print(f"aria-pressed: {is_checked_after}")
                        print(f"파란 배경: {actual_checked_after}")
                        print(f"span 표시: {span_appeared}")
                        
                        # 디버깅 정보 출력
                        final_state = await checkbox_btn.evaluate("""
                            (btn) => {
                                const span = btn.querySelector('span');
                                return {
                                    hasSpan: span !== null,
                                    spanClasses: span ? span.className : null,
                                    innerHTML: span ? span.innerHTML.substring(0, 300) : null
                                };
                            }
                        """)
                        print(f"\n최종 버튼 상태: {final_state}")
                        return False
                        
                except Exception as e:
                    print(f"✗ 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            # 테스트 실행
            success = await click_checkbox()
            
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
    asyncio.run(test_checkbox())

