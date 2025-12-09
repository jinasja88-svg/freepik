"""
Freepik 자동화 - GUI 버전
사용자가 띄워놓은 크롬 창에서 작업
Playwright로 DOM 요소를 직접 찾아서 작업
"""
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
from datetime import datetime
import pyautogui
import pyperclip
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import threading

DEFAULT_PROMPT = "Please naturally composite the product from @img2 onto the model in @img1."

# 파일 경로 설정
MODEL_DIR = Path(r"D:\private\코딩\커서\new\model")
CLOTHES_DIR = Path(r"D:\private\코딩\커서\new\clothes")
DOWNLOAD_DIR = Path(r"D:\private\코딩\커서\new\download")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

# 프롬프트 저장 파일 경로
PROMPTS_FILE = Path(__file__).parent / "prompts.json"

def load_prompts():
    """프롬프트 리스트 불러오기"""
    if PROMPTS_FILE.exists():
        try:
            with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
                return prompts
        except:
            pass
    # 기본 프롬프트 설정
    prompts = {
        "1": DEFAULT_PROMPT,
        "2": "",
        "3": "",
        "4": "",
        "5": "",
        "6": "",
        "7": "",
        "8": "",
        "9": "",
        "10": ""
    }
    save_prompts(prompts)
    return prompts

def save_prompts(prompts):
    """프롬프트 리스트 저장"""
    with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)

class FreepikGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Freepik 자동화 프로그램 - ver4.2_final")
        # 창 크기는 자동 조절되도록 설정 (초기값만 설정)
        self.root.geometry("1000x750")
        
        # 프롬프트 리스트 불러오기
        self.prompts = load_prompts()
        
        # 모드 변수
        self.mode = tk.StringVar(value="auto")
        
        # 자동모드 변수
        self.model_count = tk.IntVar(value=8)
        self.clothes_count = tk.IntVar(value=8)
        self.model_dir = Path(str(MODEL_DIR))  # 기본값은 MODEL_DIR
        self.clothes_dir = Path(str(CLOTHES_DIR))  # 기본값은 CLOTHES_DIR
        
        # 지정모드 변수
        self.model_files = []
        self.clothes_files = []
        
        # 다운로드 폴더 변수
        self.download_dir = Path(str(DOWNLOAD_DIR))  # 기본값은 DOWNLOAD_DIR
        
        # 프롬프트 변수 (1~10번)
        self.prompt_vars = {}
        self.prompt_modified = {}  # 수정 여부 추적
        self.selected_prompt_num = tk.IntVar(value=1)  # 선택된 프롬프트 번호
        self.prompt_text_widgets = {}  # 텍스트 위젯 저장
        self.prompt_status_labels = {}  # 상태 레이블 저장
        
        self.create_widgets()
        
    def create_widgets(self):
        # 제목
        title_label = tk.Label(self.root, text="Freepik 자동화 프로그램", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 모드 선택 프레임 (수평 배치)
        mode_frame = ttk.LabelFrame(self.root, text="작업 모드 선택", padding=10)
        mode_frame.pack(fill="x", padx=20, pady=10)
        
        mode_radio_frame = tk.Frame(mode_frame)
        mode_radio_frame.pack()
        
        ttk.Radiobutton(mode_radio_frame, text="자동모드 (파일 개수 지정)", variable=self.mode, 
                        value="auto", command=self.on_mode_change).pack(side="left", padx=20, pady=5)
        ttk.Radiobutton(mode_radio_frame, text="지정모드 (파일 직접 선택)", variable=self.mode, 
                        value="manual", command=self.on_mode_change).pack(side="left", padx=20, pady=5)
        
        # 자동모드와 지정모드를 좌우로 배치하는 컨테이너 프레임
        mode_settings_container = tk.Frame(self.root)
        mode_settings_container.pack(fill="x", padx=20, pady=10)
        
        # 자동모드 설정 프레임 (왼쪽)
        self.auto_frame = ttk.LabelFrame(mode_settings_container, text="자동모드 설정", padding=10)
        self.auto_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        auto_inner = tk.Frame(self.auto_frame)
        auto_inner.pack()
        
        # 모델 파일 개수 및 폴더 선택
        tk.Label(auto_inner, text="모델 파일 개수:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        model_spin = ttk.Spinbox(auto_inner, from_=1, to=100, textvariable=self.model_count, width=10)
        model_spin.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(auto_inner, text="폴더 선택", command=self.select_model_dir, width=12).grid(row=0, column=2, padx=5, pady=5)
        display_model_path = str(self.model_dir) if len(str(self.model_dir)) <= 40 else f"...{str(self.model_dir)[-37:]}"
        self.model_dir_label = tk.Label(auto_inner, text=f"폴더: {display_model_path}", fg="gray", wraplength=200)
        self.model_dir_label.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # 클로즈 파일 개수 및 폴더 선택
        tk.Label(auto_inner, text="클로즈 파일 개수:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        clothes_spin = ttk.Spinbox(auto_inner, from_=1, to=100, textvariable=self.clothes_count, width=10)
        clothes_spin.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(auto_inner, text="폴더 선택", command=self.select_clothes_dir, width=12).grid(row=1, column=2, padx=5, pady=5)
        display_clothes_path = str(self.clothes_dir) if len(str(self.clothes_dir)) <= 40 else f"...{str(self.clothes_dir)[-37:]}"
        self.clothes_dir_label = tk.Label(auto_inner, text=f"폴더: {display_clothes_path}", fg="gray", wraplength=200)
        self.clothes_dir_label.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # 지정모드 설정 프레임 (오른쪽)
        self.manual_frame = ttk.LabelFrame(mode_settings_container, text="지정모드 설정", padding=10)
        self.manual_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        manual_inner = tk.Frame(self.manual_frame)
        manual_inner.pack()
        
        tk.Button(manual_inner, text="모델 파일 선택", command=self.select_model_files, width=20).grid(row=0, column=0, padx=5, pady=5)
        self.model_files_label = tk.Label(manual_inner, text="선택된 파일: 없음", fg="gray")
        self.model_files_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Button(manual_inner, text="클로즈 파일 선택", command=self.select_clothes_files, width=20).grid(row=1, column=0, padx=5, pady=5)
        self.clothes_files_label = tk.Label(manual_inner, text="선택된 파일: 없음", fg="gray")
        self.clothes_files_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # 프롬프트 입력 프레임
        prompt_frame = ttk.LabelFrame(self.root, text="프롬프트 설정", padding=10)
        prompt_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 프롬프트 리스트 및 입력 영역
        prompt_list_frame = tk.Frame(prompt_frame)
        prompt_list_frame.pack(fill="both", expand=True, pady=5)
        
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(prompt_list_frame, height=250)
        scrollbar = ttk.Scrollbar(prompt_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 프롬프트 입력 영역 (1~10번)
        for i in range(1, 11):
            row_frame = tk.Frame(scrollable_frame)
            row_frame.pack(fill="x", padx=5, pady=3)
            
            # 라디오 버튼 (선택)
            ttk.Radiobutton(row_frame, text=str(i), variable=self.selected_prompt_num, 
                           value=i, command=lambda n=i: self.on_prompt_selected(n)).pack(side="left", padx=5)
            
            # 프롬프트 텍스트 입력창
            prompt_var = tk.StringVar()
            self.prompt_vars[i] = prompt_var
            self.prompt_modified[i] = False
            
            # 텍스트 입력창 (Entry 대신 Text 사용)
            text_widget = tk.Text(row_frame, height=2, wrap=tk.WORD, width=50)
            text_widget.pack(side="left", fill="x", expand=True, padx=5)
            saved_prompt = self.prompts.get(str(i), "")
            text_widget.insert("1.0", saved_prompt)
            text_widget.bind("<KeyRelease>", lambda e, n=i: self.on_prompt_modified(n))
            self.prompt_text_widgets[i] = text_widget
            
            # 저장 상태 표시 레이블 (초기값: 저장됨 또는 빈 상태)
            status_label = tk.Label(row_frame, text="", fg="green", width=10)
            status_label.pack(side="left", padx=5)
            self.prompt_status_labels[i] = status_label
            self.prompt_modified[i] = False  # 초기값은 수정 안됨
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 저장 버튼
        save_button_frame = tk.Frame(prompt_frame)
        save_button_frame.pack(fill="x", pady=10)
        tk.Button(save_button_frame, text="프롬프트 저장", command=self.save_all_prompts, 
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=15, height=2).pack()
        
        # 초기 선택
        self.on_prompt_selected(1)
        
        # 다운로드 폴더 설정 프레임
        download_frame = ttk.LabelFrame(self.root, text="다운로드 폴더 설정", padding=10)
        download_frame.pack(fill="x", padx=20, pady=10)
        
        download_inner = tk.Frame(download_frame)
        download_inner.pack()
        
        tk.Label(download_inner, text="다운로드 폴더:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        display_download_path = str(self.download_dir) if len(str(self.download_dir)) <= 50 else f"...{str(self.download_dir)[-47:]}"
        self.download_dir_label = tk.Label(download_inner, text=display_download_path, fg="gray", wraplength=400)
        self.download_dir_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        tk.Button(download_inner, text="폴더 선택", command=self.select_download_dir, width=12).grid(row=0, column=2, padx=5, pady=5)
        
        # 시작 버튼
        start_frame = tk.Frame(self.root)
        start_frame.pack(pady=20)
        
        self.start_button = tk.Button(start_frame, text="작업 시작", command=self.start_automation, 
                                      bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=20, height=2)
        self.start_button.pack()
        
        # 초기 모드 설정
        self.on_mode_change()
        
        # 창 크기 자동 조절 (모든 위젯이 보이도록)
        self.root.update_idletasks()
        self.adjust_window_size()
        
    def on_mode_change(self):
        """모드 변경 시 UI 업데이트"""
        if self.mode.get() == "auto":
            self.auto_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
            self.manual_frame.pack_forget()
        else:
            self.auto_frame.pack_forget()
            self.manual_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # 창 크기 재조절
        self.root.update_idletasks()
        self.adjust_window_size()
    
    def adjust_window_size(self):
        """창 크기를 자동으로 조절하여 모든 위젯이 보이도록"""
        self.root.update_idletasks()
        
        # 프롬프트 텍스트 입력창의 실제 너비를 기준으로 창 너비 계산
        if self.prompt_text_widgets:
            # 첫 번째 텍스트 위젯의 너비를 기준으로 계산
            first_widget = self.prompt_text_widgets[1]
            widget_width = first_widget.winfo_reqwidth()
            # 라디오 버튼 + 상태 레이블 + 패딩을 고려하여 약간의 여유 공간 추가
            min_width = widget_width + 200  # 여유 공간 (라디오 버튼, 상태 레이블, 패딩 등)
        else:
            # 기본값 (텍스트 입력창 width=50 기준)
            min_width = 700
        
        # 필요한 높이 계산
        height = self.root.winfo_reqheight()
        
        # 최소 높이 설정
        min_height = max(600, height)
        
        # 화면 크기 확인
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 화면 크기를 넘지 않도록 조절
        final_width = min(min_width, screen_width - 50)
        final_height = min(min_height, screen_height - 50)
        
        # 창 크기 설정
        self.root.geometry(f"{final_width}x{final_height}")
        
        # 창을 화면 중앙에 배치
        x = (screen_width - final_width) // 2
        y = (screen_height - final_height) // 2
        self.root.geometry(f"{final_width}x{final_height}+{x}+{y}")
    
    def select_model_dir(self):
        """자동모드: 모델 폴더 선택"""
        folder = filedialog.askdirectory(
            title="모델 폴더 선택",
            initialdir=str(self.model_dir)
        )
        if folder:
            self.model_dir = Path(folder)
            # 경로가 너무 길면 축약해서 표시
            display_path = str(self.model_dir) if len(str(self.model_dir)) <= 40 else f"...{str(self.model_dir)[-37:]}"
            self.model_dir_label.config(text=f"폴더: {display_path}", fg="black")
    
    def select_clothes_dir(self):
        """자동모드: 클로즈 폴더 선택"""
        folder = filedialog.askdirectory(
            title="클로즈 폴더 선택",
            initialdir=str(self.clothes_dir)
        )
        if folder:
            self.clothes_dir = Path(folder)
            # 경로가 너무 길면 축약해서 표시
            display_path = str(self.clothes_dir) if len(str(self.clothes_dir)) <= 40 else f"...{str(self.clothes_dir)[-37:]}"
            self.clothes_dir_label.config(text=f"폴더: {display_path}", fg="black")
    
    def select_model_files(self):
        """지정모드: 모델 파일 선택 (어떤 폴더든 선택 가능)"""
        files = filedialog.askopenfilenames(
            title="모델 파일 선택",
            filetypes=[("이미지 파일", "*.png *.jpg *.jpeg"), ("모든 파일", "*.*")]
        )
        if files:
            self.model_files = [Path(f) for f in files]
            file_names = ", ".join([f.name for f in self.model_files[:3]])
            if len(self.model_files) > 3:
                file_names += f" 외 {len(self.model_files) - 3}개"
            self.model_files_label.config(text=f"선택된 파일: {file_names}", fg="black")
    
    def select_clothes_files(self):
        """지정모드: 클로즈 파일 선택 (어떤 폴더든 선택 가능)"""
        files = filedialog.askopenfilenames(
            title="클로즈 파일 선택",
            filetypes=[("이미지 파일", "*.png *.jpg *.jpeg"), ("모든 파일", "*.*")]
        )
        if files:
            self.clothes_files = [Path(f) for f in files]
            file_names = ", ".join([f.name for f in self.clothes_files[:3]])
            if len(self.clothes_files) > 3:
                file_names += f" 외 {len(self.clothes_files) - 3}개"
            self.clothes_files_label.config(text=f"선택된 파일: {file_names}", fg="black")
    
    def select_download_dir(self):
        """다운로드 폴더 선택"""
        folder = filedialog.askdirectory(
            title="다운로드 폴더 선택",
            initialdir=str(self.download_dir)
        )
        if folder:
            self.download_dir = Path(folder)
            # 경로가 너무 길면 축약해서 표시
            display_path = str(self.download_dir) if len(str(self.download_dir)) <= 50 else f"...{str(self.download_dir)[-47:]}"
            self.download_dir_label.config(text=display_path, fg="black")
    
    def on_prompt_selected(self, num):
        """프롬프트 선택 시 호출"""
        # 선택된 프롬프트로 포커스 이동
        if num in self.prompt_text_widgets:
            self.prompt_text_widgets[num].focus_set()
    
    def on_prompt_modified(self, num):
        """프롬프트 수정 시 호출"""
        # 수정 표시
        self.prompt_modified[num] = True
        if num in self.prompt_status_labels:
            self.prompt_status_labels[num].config(text="저장 안됨", fg="red")
    
    def save_all_prompts(self):
        """모든 프롬프트 저장"""
        saved_count = 0
        for i in range(1, 11):
            if i in self.prompt_text_widgets:
                prompt_text = self.prompt_text_widgets[i].get("1.0", tk.END).strip()
                self.prompts[str(i)] = prompt_text
                # 저장 상태 업데이트
                self.prompt_modified[i] = False
                if i in self.prompt_status_labels:
                    self.prompt_status_labels[i].config(text="저장됨", fg="green")
                saved_count += 1
        
        save_prompts(self.prompts)
        messagebox.showinfo("저장 완료", f"모든 프롬프트가 저장되었습니다. ({saved_count}개)")
        
        # 2초 후 "저장됨" 표시 제거
        self.root.after(2000, self.clear_saved_status)
    
    def clear_saved_status(self):
        """저장 상태 표시 제거"""
        for i in range(1, 11):
            if i in self.prompt_status_labels and not self.prompt_modified[i]:
                self.prompt_status_labels[i].config(text="")
    
    def start_automation(self):
        """자동화 시작"""
        # 입력 검증
        if self.mode.get() == "manual":
            if not self.model_files or not self.clothes_files:
                messagebox.showerror("오류", "모델 파일과 클로즈 파일을 모두 선택해주세요.")
                return
        
        # 선택된 프롬프트 가져오기
        selected_num = self.selected_prompt_num.get()
        if selected_num in self.prompt_text_widgets:
            prompt_text = self.prompt_text_widgets[selected_num].get("1.0", tk.END).strip()
        else:
            prompt_text = ""
        
        if not prompt_text:
            messagebox.showerror("오류", "프롬프트를 입력해주세요.")
            return
        
        # 설정값 저장
        self.settings = {
            "mode": self.mode.get(),
            "prompt": prompt_text,
            "model_count": self.model_count.get() if self.mode.get() == "auto" else None,
            "clothes_count": self.clothes_count.get() if self.mode.get() == "auto" else None,
            "model_dir": str(self.model_dir) if self.mode.get() == "auto" else None,
            "clothes_dir": str(self.clothes_dir) if self.mode.get() == "auto" else None,
            "model_files": self.model_files if self.mode.get() == "manual" else None,
            "clothes_files": self.clothes_files if self.mode.get() == "manual" else None,
            "download_dir": str(self.download_dir)  # 다운로드 폴더
        }
        
        # GUI 닫기
        self.root.destroy()
        
        # 자동화 시작
        asyncio.run(connect_and_work(self.settings))


async def connect_and_work(settings):
    # 다운로드 폴더 설정
    download_dir = Path(settings.get("download_dir", str(DOWNLOAD_DIR)))
    download_dir.mkdir(parents=True, exist_ok=True)
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
    
    # 설정값 사용
    PROMPT_TEXT = settings["prompt"]
    mode = settings["mode"]
    
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
            
            # 파일 업로드 함수
            async def upload_file(file_name, upload_button_selector, folder_path=None):
                """파일 업로드 함수"""
                # 전체 파일 경로 생성
                if folder_path:
                    full_file_path = Path(folder_path) / file_name
                    # 실제 파일명 추출 (한글 포함)
                    actual_file_name = full_file_path.name
                    print(f"\n=== 파일 업로드: {actual_file_name} ===")
                    print(f"폴더: {folder_path}")
                    print(f"전체 경로: {full_file_path}")
                else:
                    actual_file_name = file_name
                    print(f"\n=== 파일 업로드: {actual_file_name} ===")
                
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
                    
                    # 1단계: 파일 선택 창 내부 클릭 (포커스 확보)
                    print("파일 선택 창 내부 클릭 중 (1단계)...")
                    screen_width, screen_height = pyautogui.size()
                    pyautogui.click(screen_width // 2, screen_height // 2)
                    time.sleep(0.5)
                    
                    # 2단계: 폴더 경로가 지정된 경우 해당 폴더로 이동
                    if folder_path:
                        print(f"폴더 경로로 이동 중 (2단계): {folder_path}")
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
                        time.sleep(2.0)  # 폴더 이동 완료 대기
                        
                        # 3단계: 경로 이동 후 다시 파일 선택 창 클릭
                        print("파일 선택 창 클릭 중 (3단계)...")
                        pyautogui.click(screen_width // 2, screen_height // 2)
                        time.sleep(0.5)
                    
                    # 4단계: Tab 키로 파일명 입력 창으로 이동
                    print("Tab 키로 파일명 입력 창으로 이동 중 (4단계)...")
                    pyautogui.press("tab")
                    time.sleep(0.5)
                    
                    # 5단계: 기존 파일명이 있다면 지우기
                    print("기존 파일명 지우는 중...")
                    pyautogui.hotkey("ctrl", "a")
                    time.sleep(0.2)
                    pyautogui.press("backspace")
                    time.sleep(0.3)
                    
                    # 6단계: 파일명을 클립보드에 복사 후 붙여넣기
                    print(f"파일명 복사 중 (5단계): {actual_file_name}")
                    pyperclip.copy(actual_file_name)
                    time.sleep(0.2)
                    print(f"파일명 붙여넣기 중: {actual_file_name}")
                    pyautogui.hotkey("ctrl", "v")
                    time.sleep(0.5)
                    
                    # 7단계: Enter로 파일 열기
                    print("Enter 키로 파일 열기 (6단계)...")
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
            
            # 업로드 버튼 셀렉터
            upload_selector_1 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(3) > div > div > div > div.absolute.inset-0.flex.items-center.justify-center.rounded-lg"
            upload_selector_2 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(4) > div > div > div > div.absolute.inset-0.flex.items-center.justify-center.rounded-lg"
            
            # 삭제 버튼 셀렉터
            delete_selector_1 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(3) > div > div > div > button"
            delete_selector_2 = "#left-column > div > div > div > div > div > div.flex.h-full.flex-col > div > aside > div:nth-child(2) > div > div.grid.gap-2.grid-cols-3 > div:nth-child(4) > div > div > div > button"
            
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
                    save_path = download_dir / suggested_filename
                    
                    # 파일명 중복 방지
                    counter = 1
                    original_path = save_path
                    while save_path.exists():
                        stem = original_path.stem
                        suffix = original_path.suffix
                        save_path = download_dir / f"{stem}_{counter}{suffix}"
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
            print(f"다운로드 폴더: {download_dir}")
            
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
            
            # 이미지 생성 완료 대기 함수
            async def wait_for_image_completion():
                """이미지 생성이 완료될 때까지 대기 (45초 고정 대기 후 확인)"""
                print("\n이미지 생성 중... (45초 대기)")
                print("45초 후 이미지 생성 완료를 확인합니다...")
                
                # 45초 고정 대기
                await asyncio.sleep(45)
                
                print("\n이미지 생성 완료 확인 중...")
                
                # 이미지 생성 완료 확인 (최대 30초 추가 대기)
                max_additional_wait = 30
                check_interval = 1.0
                checks = 0
                max_checks = int(max_additional_wait / check_interval)
                
                while checks < max_checks:
                    # "Generating..." 텍스트가 있는지 확인
                    generating_text = await page.evaluate("""
                        () => {
                            const text = document.body.innerText || document.body.textContent || '';
                            return text.includes('Generating') || text.includes('생성 중');
                        }
                    """)
                    
                    # 생성된 이미지 항목이 있는지 확인
                    has_image = await page.evaluate("""
                        () => {
                            const items = document.querySelectorAll('div[id^="item-"]');
                            if (items.length === 0) return false;
                            
                            // img 태그가 있는지 확인
                            const firstItem = items[0];
                            const img = firstItem.querySelector('img');
                            return img !== null && img.src && img.src.length > 0;
                        }
                    """)
                    
                    if not generating_text and has_image:
                        print(f"✓ 이미지 생성 완료! (총 {45 + checks * check_interval:.1f}초 소요)")
                        await asyncio.sleep(2.0)  # 이미지 완전 로드 대기
                        return True
                    
                    checks += 1
                    await asyncio.sleep(check_interval)
                
                # 타임아웃 시에도 계속 진행
                print(f"⚠ 이미지 생성 확인 타임아웃 (45초 + {max_additional_wait}초 경과), 계속 진행합니다.")
                await asyncio.sleep(2.0)  # 안전을 위한 추가 대기
                return False
            
            # 단일 작업 처리 함수
            async def process_single_task(page, settings, model_name, clothes_name, current_task, total_tasks, delete_selector_1):
                """단일 작업 처리 (프롬프트 입력, 생성, 다운로드, 삭제)"""
                PROMPT_TEXT = settings["prompt"]
                
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
                
                # 4단계: 이미지 생성 완료 대기
                print("\n=== 4단계: 이미지 생성 완료 대기 ===")
                await wait_for_image_completion()
                
                # 5단계: 다운로드
                print("\n=== 5단계: 이미지 다운로드 ===")
                download_success = await click_checkbox_and_download(model_name, clothes_name)
                if not download_success:
                    print("⚠ 다운로드 실패했지만 계속 진행합니다...")
                
                # 6단계: 업로드된 파일 삭제 (2번)
                print("\n=== 6단계: 업로드된 파일 삭제 ===")
                
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
                                    // 먼저 클래스로 찾기
                                    const btn = firstItem.querySelector('button.absolute.right-1.top-1');
                                    if (btn) return btn;
                                    // 또는 SVG 아이콘으로 찾기
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
                
                # 두 번째 삭제 버튼 클릭 (첫 번째 삭제 후 nth-child(3) 위치로 이동)
                print("두 번째 삭제 버튼 클릭 중...")
                try:
                    # 첫 번째 파일 삭제 후 두 번째 파일이 nth-child(3) 위치로 이동
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
                                // 첫 번째 파일 삭제 후 남은 파일 찾기
                                // nth-child(3) 위치의 파일 찾기
                                const secondItem = container.querySelector('div:nth-child(3)');
                                if (secondItem) {
                                    const btn = secondItem.querySelector('button.absolute.right-1.top-1');
                                    if (btn) return btn;
                                    // 또는 모든 버튼 중에서 찾기
                                    const allBtns = secondItem.querySelectorAll('button');
                                    for (let btn of allBtns) {
                                        if (btn.querySelector('svg use[xlink\\:href="#cdn-cross-medium"]')) {
                                            return btn;
                                        }
                                    }
                                }
                                // fallback: 모든 삭제 버튼 중 첫 번째
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
                
                print(f"✓ 작업 {current_task}/{total_tasks} 완료!")
                
                # 다음 작업 전 대기 (마지막 작업이 아닌 경우)
                if current_task < total_tasks:
                    print("다음 작업을 위해 2초 대기 중...")
                    await asyncio.sleep(2.0)
            
            # 단일 작업 처리 함수
            async def process_single_task(page, settings, model_name, clothes_name, current_task, total_tasks, delete_selector_1):
                """단일 작업 처리 (프롬프트 입력, 생성, 다운로드, 삭제)"""
                PROMPT_TEXT = settings["prompt"]
                
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
                
                # 4단계: 이미지 생성 완료 대기
                print("\n=== 4단계: 이미지 생성 완료 대기 ===")
                await wait_for_image_completion()
                
                # 5단계: 다운로드
                print("\n=== 5단계: 이미지 다운로드 ===")
                download_success = await click_checkbox_and_download(model_name, clothes_name)
                if not download_success:
                    print("⚠ 다운로드 실패했지만 계속 진행합니다...")
                
                # 6단계: 업로드된 파일 삭제 (2번)
                print("\n=== 6단계: 업로드된 파일 삭제 ===")
                
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
                                    // 먼저 클래스로 찾기
                                    const btn = firstItem.querySelector('button.absolute.right-1.top-1');
                                    if (btn) return btn;
                                    // 또는 SVG 아이콘으로 찾기
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
                
                # 두 번째 삭제 버튼 클릭 (첫 번째 삭제 후 nth-child(3) 위치로 이동)
                print("두 번째 삭제 버튼 클릭 중...")
                try:
                    # 첫 번째 파일 삭제 후 두 번째 파일이 nth-child(3) 위치로 이동
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
                                // 첫 번째 파일 삭제 후 남은 파일 찾기
                                // nth-child(3) 위치의 파일 찾기
                                const secondItem = container.querySelector('div:nth-child(3)');
                                if (secondItem) {
                                    const btn = secondItem.querySelector('button.absolute.right-1.top-1');
                                    if (btn) return btn;
                                    // 또는 모든 버튼 중에서 찾기
                                    const allBtns = secondItem.querySelectorAll('button');
                                    for (let btn of allBtns) {
                                        if (btn.querySelector('svg use[xlink\\:href="#cdn-cross-medium"]')) {
                                            return btn;
                                        }
                                    }
                                }
                                // fallback: 모든 삭제 버튼 중 첫 번째
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
                
                print(f"✓ 작업 {current_task}/{total_tasks} 완료!")
                
                # 다음 작업 전 대기 (마지막 작업이 아닌 경우)
                if current_task < total_tasks:
                    print("다음 작업을 위해 2초 대기 중...")
                    await asyncio.sleep(2.0)
            
            # 체크박스 클릭 및 다운로드 함수
            async def click_checkbox_and_download(model_idx, clothes_idx):
                """체크박스 클릭 후 다운로드 버튼 클릭"""
                print("\n=== 다운로드 시작 ===")
                
                # 방법 1: 이미지 항목 컨테이너 찾기
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
                
                # 방법 2: 체크박스 버튼 직접 찾기
                checkbox_selectors = [
                    "#tool-layout-main > div > div.flex.flex-col.gap-2\\.5 > div.relative.w-full > div:nth-child(1) > div > div > div.border-surface-border-alpha-1.ml-auto.flex.items-center.gap-2.border-l.pl-2 > button",
                    "div.border-l.pl-2 > button",
                    "div.ml-auto.flex.items-center.gap-2.border-l.pl-2 > button",
                    "div.select-checkbox > button",
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
                    print("✗ 체크박스 버튼을 찾을 수 없습니다.")
                    return False
                
                # 호버하여 체크박스가 보이도록
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
                print("[4] 클릭 후 상태 확인...")
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
                
                if not final_state.get('isChecked'):
                    print("⚠ 체크박스가 체크되지 않았습니다. 재시도 중...")
                    await checkbox_button.click()
                    await asyncio.sleep(1.5)
                    final_state = await checkbox_button.evaluate("""
                        (btn) => {
                            const ariaPressed = btn.getAttribute('aria-pressed');
                            const span = btn.querySelector('span');
                            const hasBlueBg = span && (span.className.includes('bg-piki-blue-500') || span.className.includes('bg-piki-blue'));
                            return ariaPressed === 'true' || hasBlueBg;
                        }
                    """)
                
                if not final_state.get('isChecked'):
                    print("✗ 체크박스 클릭 실패")
                    return False
                
                print("✓ 체크박스 클릭 성공!")
                
                # 다운로드 버튼 클릭
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
                            return False
                        else:
                            # 다운로드 버튼 클릭
                            print("\n[다운로드] 다운로드 버튼 클릭")
                            
                            # 다운로드 이벤트 대기 (최대 5초)
                            download_event_received.clear()
                            latest_download = None
                            
                            await download_button.click()
                            await asyncio.sleep(0.5)
                            print("✓ 다운로드 버튼 클릭 완료")
                            
                            # 다운로드 이벤트 대기
                            try:
                                await asyncio.wait_for(download_event_received.wait(), timeout=5.0)
                                if latest_download:
                                    print("✓ 다운로드 이벤트 감지됨")
                                    # handle_download는 이미 이벤트 리스너에서 자동 호출됨
                                    await asyncio.sleep(1.0)  # 파일 저장 완료 대기
                                    print("✓ 다운로드 완료!")
                                    return True
                                else:
                                    print("⚠ 다운로드 이벤트를 감지했지만 파일 정보가 없습니다.")
                                    return False
                            except asyncio.TimeoutError:
                                print("⚠ 다운로드 이벤트를 감지하지 못했습니다.")
                                print("브라우저의 다운로드 폴더를 확인하세요.")
                                return False
                    except Exception as e:
                        print(f"✗ 다운로드 버튼 클릭 실패: {e}")
                        return False
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
                    return False
            
            # 루프 시작
            total_work = 0
            
            if settings["mode"] == "auto":
                # 자동모드: 파일 개수 지정
                model_count = settings["model_count"]
                clothes_count = settings["clothes_count"]
                model_dir = Path(settings["model_dir"]) if settings["model_dir"] else MODEL_DIR
                clothes_dir = Path(settings["clothes_dir"]) if settings["clothes_dir"] else CLOTHES_DIR
                total_tasks = model_count * clothes_count
                
                print("\n" + "=" * 60)
                print("자동모드 - 이중 루프 자동화 시작!")
                print(f"모델 폴더: {model_dir}")
                print(f"클로즈 폴더: {clothes_dir}")
                print(f"외부 루프: clothes 1~{clothes_count} ({clothes_count}번)")
                print(f"내부 루프: model 1~{model_count} ({model_count}번)")
                print(f"총 작업 횟수: {total_tasks}번")
                print("=" * 60)
                
                # 외부 루프: clothes 1~clothes_count
                for clothes_idx in range(1, clothes_count + 1):
                    print(f"\n{'='*60}")
                    print(f"외부 루프: clothes {clothes_idx}.png")
                    print(f"{'='*60}")
                    
                    # 내부 루프: model 1~model_count
                    for model_idx in range(1, model_count + 1):
                        total_work += 1
                        print(f"\n{'─'*60}")
                        print(f"작업 {total_work}/{total_tasks}: model {model_idx}.png + clothes {clothes_idx}.png")
                        print(f"{'─'*60}")
                        
                        # 1단계: 파일 업로드
                        print(f"\n=== 1단계: 파일 업로드 ===")
                        await upload_file(f"{model_idx}.png", upload_selector_1, model_dir)
                        await upload_file(f"{clothes_idx}.png", upload_selector_2, clothes_dir)
                        await asyncio.sleep(1.0)  # 파일 업로드 완료 대기
                        
                        # 나머지 작업 수행
                        await process_single_task(page, settings, str(model_idx), str(clothes_idx), total_work, total_tasks, delete_selector_1)
                        
            else:
                # 지정모드: 선택한 파일들로 작업
                model_files = settings["model_files"]
                clothes_files = settings["clothes_files"]
                total_tasks = len(model_files) * len(clothes_files)
                
                print("\n" + "=" * 60)
                print("지정모드 - 선택한 파일로 자동화 시작!")
                print(f"모델 파일: {len(model_files)}개")
                print(f"클로즈 파일: {len(clothes_files)}개")
                print(f"총 작업 횟수: {total_tasks}번")
                print("=" * 60)
                
                # 외부 루프: clothes 파일들
                for clothes_file in clothes_files:
                    print(f"\n{'='*60}")
                    print(f"외부 루프: {clothes_file.name}")
                    print(f"{'='*60}")
                    
                    # 내부 루프: model 파일들
                    for model_file in model_files:
                        total_work += 1
                        print(f"\n{'─'*60}")
                        print(f"작업 {total_work}/{total_tasks}: {model_file.name} + {clothes_file.name}")
                        print(f"{'─'*60}")
                        
                        # 1단계: 파일 업로드 (지정모드는 전체 경로 사용)
                        print(f"\n=== 1단계: 파일 업로드 ===")
                        await upload_file(model_file.name, upload_selector_1, model_file.parent)
                        await upload_file(clothes_file.name, upload_selector_2, clothes_file.parent)
                        await asyncio.sleep(1.0)  # 파일 업로드 완료 대기
                        
                        # 나머지 작업 수행
                        await process_single_task(page, settings, model_file.stem, clothes_file.stem, total_work, total_tasks, delete_selector_1)
            
            # 모든 작업 완료
            print("\n" + "=" * 60)
            print("모든 작업 완료!")
            print(f"총 {total_work}개의 작업을 완료했습니다.")
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
    root = tk.Tk()
    app = FreepikGUI(root)
    root.mainloop()


