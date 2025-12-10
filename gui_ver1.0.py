import asyncio
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from playwright.async_api import async_playwright


FREEPIK_URL = "https://www.freepik.com/ai/image-generator"


async def run_freepik(clothes_dir: Path, models_dir: Path, prompt_text: str, log_cb):
  async with async_playwright() as p:
    chrome_path = Path(
      r"C:\Users\EKR\AppData\Local\Google\Chrome\User Data\Profile 2"
    )  # 필요 시 수정
    browser = await p.chromium.launch_persistent_context(
      user_data_dir=str(chrome_path),
      channel="chrome",
      headless=False,
      slow_mo=200
    )
    page = browser.pages[0] if browser.pages else await browser.new_page()

    await page.goto(FREEPIK_URL)
    log_cb("브라우저가 열렸습니다. Freepik에 로그인 후, 이 창으로 돌아와 진행해주세요.")
    input("터미널 창에서 Enter 키를 누르면 계속 진행합니다...")  # EXE에서는 콘솔이 없을 수 있음

    clothes_files = sorted(Path(clothes_dir).glob("*.*"))
    model_files = sorted(Path(models_dir).glob("*.*"))

    if not clothes_files or not model_files:
      log_cb("옷/모델 폴더에 이미지가 없습니다.")
      return

    pair_count = min(len(clothes_files), len(model_files)) // 2
    if pair_count == 0:
      log_cb("각 폴더에 최소 2장 이상의 이미지가 필요합니다.")
      return

    for i in range(pair_count):
      clothes_pair = clothes_files[i * 2 : (i + 1) * 2]
      model_pair = model_files[i * 2 : (i + 1) * 2]

      log_cb(f"[{i+1}] 세트 처리 중: " + ", ".join(f.name for f in clothes_pair + model_pair))

      upload_input = await page.wait_for_selector("input[type='file']", timeout=15000)
      files_to_upload = [str(f) for f in (clothes_pair + model_pair)]
      await upload_input.set_input_files(files_to_upload)

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
      await prompt_el.type(prompt_text)

      gen_btn = await page.wait_for_selector(
        'button[data-cy="generate-button"]', timeout=15000
      )
      for _ in range(20):
        disabled = await gen_btn.get_attribute("aria-disabled")
        if disabled != "true":
          break
        await asyncio.sleep(0.15)

      await gen_btn.click()
      log_cb(f"[{i+1}] Generate 클릭 완료, 결과 대기 중...")
      await asyncio.sleep(15)

    log_cb("모든 세트 처리 완료.")
    await browser.close()


def start_automation(clothes_path, models_path, prompt_text, log_cb):
  def runner():
    try:
      asyncio.run(run_freepik(Path(clothes_path), Path(models_path), prompt_text, log_cb))
    except Exception as e:
      log_cb(f"에러 발생: {e}")

  threading.Thread(target=runner, daemon=True).start()


def main():
  root = tk.Tk()
  root.title("Freepik Auto Generator")
  root.geometry("520x320")

  def choose_clothes():
    path = filedialog.askdirectory(title="옷 이미지 폴더 선택")
    if path:
      clothes_var.set(path)

  def choose_models():
    path = filedialog.askdirectory(title="모델 이미지 폴더 선택")
    if path:
      models_var.set(path)

  log_text = tk.Text(root, height=8, state="disabled")

  def log_cb(msg):
    log_text.configure(state="normal")
    log_text.insert("end", msg + "\n")
    log_text.see("end")
    log_text.configure(state="disabled")

  def on_start():
    clothes = clothes_var.get().strip()
    models = models_var.get().strip()
    prompt = prompt_entry.get("1.0", "end").strip()

    if not clothes or not models:
      messagebox.showerror("오류", "옷/모델 폴더를 모두 선택해주세요.")
      return
    if not prompt:
      messagebox.showerror("오류", "프롬프트 내용을 입력해주세요.")
      return

    log_cb("자동화를 시작합니다. 브라우저에서 로그인 후 터미널 창 안내에 따라 Enter를 눌러주세요.")
    start_automation(clothes, models, prompt, log_cb)

  clothes_var = tk.StringVar()
  models_var = tk.StringVar()

  tk.Label(root, text="옷 이미지 폴더:").pack(anchor="w", padx=10, pady=(10, 0))
  row1 = tk.Frame(root)
  row1.pack(fill="x", padx=10)
  tk.Entry(row1, textvariable=clothes_var).pack(side="left", fill="x", expand=True)
  tk.Button(row1, text="찾기", command=choose_clothes, width=8).pack(side="left", padx=(5, 0))

  tk.Label(root, text="모델 이미지 폴더:").pack(anchor="w", padx=10, pady=(8, 0))
  row2 = tk.Frame(root)
  row2.pack(fill="x", padx=10)
  tk.Entry(row2, textvariable=models_var).pack(side="left", fill="x", expand=True)
  tk.Button(row2, text="찾기", command=choose_models, width=8).pack(side="left", padx=(5, 0))

  tk.Label(root, text="프롬프트:").pack(anchor="w", padx=10, pady=(8, 0))
  prompt_entry = tk.Text(root, height=3)
  prompt_entry.insert(
    "1.0", "Please naturally composite the product from @img1 onto the model in @img2."
  )
  prompt_entry.pack(fill="both", padx=10)

  tk.Button(root, text="자동 생성 시작", command=on_start).pack(pady=8)

  tk.Label(root, text="로그:").pack(anchor="w", padx=10)
  log_text.pack(fill="both", padx=10, pady=(0, 10))

  root.mainloop()


if __name__ == "__main__":
  main()

