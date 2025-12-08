"""
Freepik 완전 자동화 프로그램 (확장 프로그램 없이)
Playwright로 모든 기능 직접 구현
"""
import asyncio
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading

from playwright.async_api import async_playwright

FREEPIK_URL = "https://www.freepik.com/ai/image-generator"

# 설정
CLOTHES_DIR = Path(r"D:\private\코딩\커서\new\clothes")
MODELS_DIR = Path(r"D:\private\코딩\커서\new\model")
PROMPT_TEXT = "Please naturally composite the product from @img1 onto the model in @img2."

# 크롬 프로필 경로 (구글 로그인된 프로필 사용)
CHROME_PROFILE_PATH = Path(r"C:\Users\EKR\AppData\Local\Google\Chrome\User Data\Profile 2")


async def run_freepik_automation(clothes_dir: Path, models_dir: Path, prompt_text: str, log_cb):
    """Freepik 자동화 실행"""
    async with async_playwright() as p:
        # 크롬 프로필 사용 (구글 로그인된 상태)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE_PATH),
            channel="chrome",
            headless=False,
            slow_mo=200
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        await page.goto(FREEPIK_URL)
        log_cb("Freepik 페이지 열림. 로그인되어 있는지 확인하세요.")
        await asyncio.sleep(2)
        
        # 파일 목록 가져오기
        clothes_files = sorted(clothes_dir.glob("*.*"))
        model_files = sorted(models_dir.glob("*.*"))
        
        if not clothes_files or not model_files:
            log_cb("옷/모델 폴더에 이미지가 없습니다.")
            return
        
        pair_count = min(len(clothes_files), len(model_files))
        
        if pair_count == 0:
            log_cb("각 폴더에 최소 1장 이상의 이미지가 필요합니다.")
            return
        
        log_cb(f"총 {pair_count}개 조합을 처리합니다.")
        
        for i in range(pair_count):
            clothes_file = clothes_files[i]
            model_file = model_files[i]
            
            log_cb(f"\n[{i+1}/{pair_count}] 처리 중: {clothes_file.name} + {model_file.name}")
            
            try:
                # 1. 파일 업로드
                log_cb("파일 업로드 중...")
                upload_input = await page.wait_for_selector("input[type='file']", timeout=10000)
                files_to_upload = [str(clothes_file), str(model_file)]
                await upload_input.set_input_files(files_to_upload)
                log_cb("파일 업로드 완료")
                await asyncio.sleep(1)
                
                # 2. 프롬프트 입력
                log_cb("프롬프트 입력 중...")
                prompt_selector = (
                    "#imagePromptInput > div > div > div.relative.flex-1 > div > "
                    "div.text-surface-foreground-0.w-full.flex-1.overflow-y-auto.whitespace-pre-wrap."
                    "text-sm.leading-relaxed.outline-none.transition-all.user-select-all.dynamic-prompt."
                    "scrollbar-thin.scrollbar-thumb-neutral-800.\\32 xl-legacy\\:max-h-96.relative."
                    "max-h-\\[46px\\].min-h-\\[103px\\].rounded.p-2.text-sm.focus-visible\\:outline-none."
                    "focus-visible\\:ring-0.md\\:max-h-52.xl\\:max-h-72.empty-prompt"
                )
                
                prompt_el = await page.wait_for_selector(prompt_selector, timeout=10000)
                await prompt_el.click()
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Delete")
                await prompt_el.type(prompt_text)
                log_cb("프롬프트 입력 완료")
                await asyncio.sleep(0.5)
                
                # 3. Generate 버튼 클릭
                log_cb("Generate 버튼 클릭 중...")
                gen_btn = await page.wait_for_selector('button[data-cy="generate-button"]', timeout=10000)
                
                # 버튼 활성화까지 대기
                for _ in range(20):
                    disabled = await gen_btn.get_attribute("aria-disabled")
                    if disabled != "true":
                        break
                    await asyncio.sleep(0.15)
                
                await gen_btn.click()
                log_cb("Generate 클릭 완료, 결과 대기 중...")
                
                # 4. 결과 완성 대기
                log_cb("이미지 생성 중... (최대 120초 대기)")
                max_wait = 120
                check_interval = 1
                elapsed = 0
                
                while elapsed < max_wait:
                    # "Generating..." 텍스트 확인
                    feed_container = await page.query_selector("#tool-layout-main > div > div.flex.flex-col.gap-2\\.5")
                    
                    if feed_container:
                        has_generating = await feed_container.evaluate("""
                            () => {
                                const spans = Array.from(document.querySelectorAll('span'));
                                return spans.some(span => span.textContent.includes('Generating...'));
                            }
                        """)
                        
                        if not has_generating:
                            # 생성 완료된 이미지 찾기
                            completed_item = await feed_container.evaluate("""
                                () => {
                                    const items = document.querySelectorAll("div[id^='item-']");
                                    for (let i = items.length - 1; i >= 0; i--) {
                                        const item = items[i];
                                        const hasGenerating = item.textContent.includes('Generating...');
                                        const hasImage = item.querySelector("img[id^='creation']");
                                        if (!hasGenerating && hasImage) {
                                            return item.id;
                                        }
                                    }
                                    return null;
                                }
                            """)
                            
                            if completed_item:
                                log_cb(f"이미지 생성 완료! (item: {completed_item})")
                                break
                    
                    await asyncio.sleep(check_interval)
                    elapsed += check_interval
                    
                    if elapsed % 10 == 0:
                        log_cb(f"생성 중... ({elapsed}초 경과)")
                
                if elapsed >= max_wait:
                    log_cb("경고: 생성 시간 초과 (120초)")
                    continue
                
                # 5. 체크박스 클릭
                log_cb("체크박스 클릭 중...")
                check_button_selector = (
                    "#tool-layout-main > div > div.flex.flex-col.gap-2\\.5 > div.relative.w-full > "
                    "div:nth-child(1) > div > div > div.border-surface-border-alpha-1.ml-auto.flex.items-center.gap-2.border-l.pl-2 > button > span"
                )
                
                check_button = await page.wait_for_selector(check_button_selector, timeout=5000)
                if check_button:
                    check_button_parent = await check_button.evaluate_handle("el => el.closest('button')")
                    is_checked = await check_button_parent.get_attribute("aria-pressed")
                    
                    if is_checked != "true":
                        await check_button_parent.click()
                        log_cb("체크박스 클릭 완료")
                    else:
                        log_cb("체크박스가 이미 체크되어 있음")
                    
                    await asyncio.sleep(1)
                    
                    # 6. 다운로드 버튼 클릭
                    log_cb("다운로드 버튼 클릭 중...")
                    download_button = await page.wait_for_selector(
                        "body > div.pointer-events-none.fixed.bottom-0.right-0.z-30.flex.items-center.justify-center.duration-100.left-\\[384px\\].xl\\:left-\\[560px\\] > div > div.ml-auto.flex.gap-2 > div.flex > button",
                        timeout=5000
                    )
                    
                    if download_button:
                        await download_button.click()
                        log_cb("다운로드 버튼 클릭 완료")
                        await asyncio.sleep(2)
                    else:
                        log_cb("경고: 다운로드 버튼을 찾을 수 없음")
                else:
                    log_cb("경고: 체크박스를 찾을 수 없음")
                
                log_cb(f"[{i+1}/{pair_count}] 완료!")
                
                # 다음 조합 전 대기
                if i < pair_count - 1:
                    log_cb("다음 조합까지 5초 대기...")
                    await asyncio.sleep(5)
                
            except Exception as e:
                log_cb(f"에러 발생: {e}")
                continue
        
        log_cb("\n모든 작업 완료!")
        await asyncio.sleep(3)
        await browser.close()


def start_automation(clothes_path, models_path, prompt_text, log_cb):
    """자동화 시작 (별도 스레드)"""
    def runner():
        try:
            asyncio.run(run_freepik_automation(
                Path(clothes_path),
                Path(models_path),
                prompt_text,
                log_cb
            ))
        except Exception as e:
            log_cb(f"에러 발생: {e}")
    
    threading.Thread(target=runner, daemon=True).start()


def main():
    """GUI 메인 함수"""
    root = tk.Tk()
    root.title("Freepik 완전 자동화")
    root.geometry("600x500")
    
    # 폴더 선택
    clothes_var = tk.StringVar(value=str(CLOTHES_DIR))
    models_var = tk.StringVar(value=str(MODELS_DIR))
    
    def choose_clothes():
        path = filedialog.askdirectory(title="옷 이미지 폴더 선택", initialdir=str(CLOTHES_DIR))
        if path:
            clothes_var.set(path)
    
    def choose_models():
        path = filedialog.askdirectory(title="모델 이미지 폴더 선택", initialdir=str(MODELS_DIR))
        if path:
            models_var.set(path)
    
    # 로그 영역
    log_text = scrolledtext.ScrolledText(root, height=15, state="disabled", wrap=tk.WORD)
    
    def log_cb(msg):
        log_text.configure(state="normal")
        log_text.insert("end", msg + "\n")
        log_text.see("end")
        log_text.configure(state="disabled")
        root.update()
    
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
        
        log_cb("=" * 50)
        log_cb("Freepik 자동화 시작")
        log_cb("=" * 50)
        start_automation(clothes, models, prompt, log_cb)
    
    # UI 구성
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
    prompt_entry.insert("1.0", PROMPT_TEXT)
    prompt_entry.pack(fill="both", padx=10, expand=True)
    
    tk.Button(root, text="자동화 시작", command=on_start, bg="#4CAF50", fg="white", font=("", 12, "bold")).pack(pady=10)
    
    tk.Label(root, text="로그:").pack(anchor="w", padx=10)
    log_text.pack(fill="both", padx=10, pady=(0, 10), expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()


