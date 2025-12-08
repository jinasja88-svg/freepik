"""
Freepik 간단 테스트: 프롬프트 입력 + Generate 버튼 클릭
"""
import asyncio
from playwright.async_api import async_playwright

FREEPIK_URL = "https://www.freepik.com/ai/image-generator"
PROMPT_TEXT = "Please naturally composite the product from @img1 onto the model in @img2."

# 크롬 프로필 경로 (구글 로그인된 프로필 사용)
CHROME_PROFILE_PATH = r"C:\Users\EKR\AppData\Local\Google\Chrome\User Data\Profile 2"


async def test_prompt_and_generate():
    """프롬프트 입력 + Generate 버튼 클릭 테스트"""
    async with async_playwright() as p:
        print("브라우저 시작 중...")
        
        # 크롬 프로필 사용 (구글 로그인된 상태)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_PROFILE_PATH,
            channel="chrome",
            headless=False,
            slow_mo=200
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        print("Freepik 페이지 열기...")
        await page.goto(FREEPIK_URL)
        await asyncio.sleep(2)  # 페이지 로드 대기
        
        print("\n=== 1단계: 프롬프트 입력 ===")
        
        # 프롬프트 입력칸 찾기
        prompt_selector = (
            "#imagePromptInput > div > div > div.relative.flex-1 > div > "
            "div.text-surface-foreground-0.w-full.flex-1.overflow-y-auto.whitespace-pre-wrap."
            "text-sm.leading-relaxed.outline-none.transition-all.user-select-all.dynamic-prompt."
            "scrollbar-thin.scrollbar-thumb-neutral-800.\\32 xl-legacy\\:max-h-96.relative."
            "max-h-\\[46px\\].min-h-\\[103px\\].rounded.p-2.text-sm.focus-visible\\:outline-none."
            "focus-visible\\:ring-0.md\\:max-h-52.xl\\:max-h-72.empty-prompt"
        )
        
        try:
            print("프롬프트 입력칸 찾는 중...")
            prompt_el = await page.wait_for_selector(prompt_selector, timeout=10000)
            print("✓ 프롬프트 입력칸 찾음")
            
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
            current_value = await prompt_el.evaluate("el => el.textContent || el.innerText || el.value")
            print(f"입력된 프롬프트 확인: {current_value[:50]}...")
            
            if PROMPT_TEXT not in current_value:
                print("⚠ 경고: 프롬프트가 제대로 입력되지 않았을 수 있습니다.")
            else:
                print("✓ 프롬프트 입력 완료")
                
        except Exception as e:
            print(f"✗ 프롬프트 입력 실패: {e}")
            print("프롬프트 입력칸을 찾을 수 없습니다.")
            return
        
        print("\n=== 2단계: Generate 버튼 클릭 ===")
        
        try:
            print("Generate 버튼 찾는 중...")
            gen_btn = await page.wait_for_selector('button[data-cy="generate-button"]', timeout=10000)
            print("✓ Generate 버튼 찾음")
            
            # 버튼 활성화까지 대기
            print("버튼 활성화 대기 중...")
            for i in range(20):
                disabled = await gen_btn.get_attribute("aria-disabled")
                if disabled != "true":
                    print(f"✓ 버튼 활성화됨 ({i * 0.15:.1f}초 후)")
                    break
                await asyncio.sleep(0.15)
            else:
                print("⚠ 경고: 버튼이 3초 후에도 활성화되지 않았지만 클릭 시도합니다.")
            
            # Generate 버튼 클릭
            await gen_btn.click()
            print("✓ Generate 버튼 클릭 완료!")
            print("\n이미지 생성이 시작되었습니다.")
            print("브라우저를 닫지 마세요. 생성이 완료될 때까지 기다려주세요.")
            
        except Exception as e:
            print(f"✗ Generate 버튼 클릭 실패: {e}")
            print("Generate 버튼을 찾을 수 없습니다.")
            return
        
        # 결과 확인을 위해 잠시 대기
        print("\n10초 후 브라우저를 닫습니다...")
        await asyncio.sleep(10)
        
        print("\n테스트 완료!")
        # 브라우저는 수동으로 닫으려면 주석 처리
        # await browser.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Freepik 프롬프트 입력 + Generate 테스트")
    print("=" * 50)
    print("\n주의사항:")
    print("1. 크롬 브라우저가 모두 닫혀 있어야 합니다.")
    print("2. Freepik에 로그인되어 있어야 합니다.")
    print("3. 크롬 프로필 경로가 맞는지 확인하세요.")
    print("\n5초 후 시작합니다...")
    print()
    
    asyncio.run(test_prompt_and_generate())


