import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Freepik AI 이미지 생성기 URL (필요하면 실제 사용하는 URL로 수정)
FREEPIK_URL = "https://www.freepik.com/ai/image-generator"

# TODO: 여기를 본인 폴더 경로로 바꾸세요.
CLOTHES_DIR = Path(r"D:\images\clothes")
MODELS_DIR = Path(r"D:\images\models")

# 기본 프롬프트 예시
PROMPT_TEMPLATE = "이 옷 사진과 이 모델 사진을 자연스럽게 합성해줘."


async def main():
  async with async_playwright() as p:
    browser = await p.chromium.launch(headless=False, slow_mo=200)
    context = await browser.new_context()
    page = await context.new_page()

    # 1) Freepik 접속
    await page.goto(FREEPIK_URL)
    print("Freepik에 로그인 안 되어 있으면 지금 로그인하고, 준비되면 Enter 누르세요.")
    input()

    # 2) 로컬 폴더에서 파일 2개씩 짝짓기
    clothes_files = sorted(CLOTHES_DIR.glob("*.*"))
    model_files = sorted(MODELS_DIR.glob("*.*"))

    if not clothes_files or not model_files:
      print("옷/모델 이미지 폴더에 파일이 없습니다. CLOTHES_DIR / MODELS_DIR 경로를 확인하세요.")
      return

    pair_count = min(len(clothes_files), len(model_files)) // 2
    if pair_count == 0:
      print("각 폴더에 최소 2개 이상의 이미지가 필요합니다.")
      return

    for i in range(pair_count):
      clothes_pair = clothes_files[i * 2 : (i + 1) * 2]
      model_pair = model_files[i * 2 : (i + 1) * 2]

      print(f"[{i+1}] 세트 처리 중:", [f.name for f in clothes_pair + model_pair])

      # 2-1) Freepik 업로드 input 찾기 (실제 구조에 맞게 selector 수정 필요)
      upload_input = await page.wait_for_selector("input[type='file']", timeout=15000)

      files_to_upload = [str(f) for f in (clothes_pair + model_pair)]
      await upload_input.set_input_files(files_to_upload)

      # 2-2) 프롬프트 입력 (우리가 확장에서 쓰던 셀렉터 사용)
      prompt_selector = (
        "#imagePromptInput > div > div > div.relative.flex-1 > div > "
        "div.text-surface-foreground-0.w-full.flex-1.overflow-y-auto.whitespace-pre-wrap."
        "text-sm.leading-relaxed.outline-none.transition-all.user-select-all.dynamic-prompt."
        "scrollbar-thin.scrollbar-thumb-neutral-800.\\32 xl-legacy\\:max-h-96.relative."
        "max-h-\\[46px\\].min-h-\\[103px\\].rounded.p-2.text-sm.focus-visible\\:outline-none."
        "focus-visible\\:ring-0.md\\:max-h-52.xl\\:max-h-72"
      )

      prompt_el = await page.wait_for_selector(prompt_selector, timeout=15000)
      await prompt_el.click()
      await page.keyboard.press("Control+A")
      await page.keyboard.press("Delete")
      await prompt_el.type(PROMPT_TEMPLATE)

      # 2-3) Generate 버튼 클릭 (data-cy="generate-button")
      gen_btn = await page.wait_for_selector(
        'button[data-cy="generate-button"]', timeout=15000
      )

      # 버튼 활성화까지 대기 (최대 2초)
      for _ in range(20):
        disabled = await gen_btn.get_attribute("aria-disabled")
        if disabled != "true":
          break
        await asyncio.sleep(0.15)

      await gen_btn.click()
      print(f"[{i+1}] Generate 클릭 완료, 결과 대기 중...")

      # 2-4) 결과가 나올 때까지 대기 (우선은 고정 시간 대기)
      await asyncio.sleep(15)

    print("모든 세트 처리 완료.")
    await browser.close()


if __name__ == "__main__":
  asyncio.run(main())







