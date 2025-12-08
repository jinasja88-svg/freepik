"""
Freepik 이미지 인식 기반 매크로
좌표 대신 버튼 이미지를 찾아서 클릭하는 방식
"""
import pyautogui
import time
import os
from pathlib import Path
import pyperclip

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# 이미지 파일 경로
IMAGES_DIR = Path(__file__).parent / "images"
EXTENSION_ICON_IMG = IMAGES_DIR / "extension_icon.png"
UPLOAD_BUTTON_IMG = IMAGES_DIR / "upload_button.png"
PROMPT_INPUT_IMG = IMAGES_DIR / "prompt_input.png"
RUN_BUTTON_IMG = IMAGES_DIR / "run_button.png"

# 설정
CLOTHES_DIR = Path(r"D:\private\코딩\커서\new\clothes")  # 옷 이미지 폴더
MODELS_DIR = Path(r"D:\private\코딩\커서\new\model")    # 모델 이미지 폴더
PROMPT_TEXT = "Please naturally composite the product from @img1 onto the model in @img2."


def find_and_click(image_path, confidence=0.8, timeout=5, description=""):
    """화면에서 이미지를 찾아서 클릭"""
    print(f"{description} 찾는 중... ({image_path.name})")
    
    # timeout을 직접 구현 (재시도 방식)
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            location = pyautogui.locateOnScreen(str(image_path), confidence=confidence)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center)
                print(f"✓ {description} 찾음 및 클릭 완료: {center}")
                time.sleep(0.5)
                return True
        except pyautogui.ImageNotFoundException:
            pass  # 계속 시도
        except Exception as e:
            print(f"✗ {description} 에러 발생: {e}")
            return False
        
        time.sleep(0.3)  # 0.3초마다 재시도
    
    print(f"✗ {description} 이미지를 찾을 수 없음: {image_path.name} (시간 초과)")
    return False


def click_extension_icon():
    """확장 아이콘 클릭 (이미지 인식)"""
    return find_and_click(EXTENSION_ICON_IMG, description="확장 아이콘")


def click_upload_button():
    """파일 업로드 버튼 클릭"""
    if find_and_click(UPLOAD_BUTTON_IMG, description="파일 업로드 버튼"):
        time.sleep(1.5)  # 파일 선택 다이얼로그가 뜰 때까지 대기
        return True
    return False


def select_files_in_dialog(file_paths):
    """파일 선택 다이얼로그에서 파일 선택"""
    print(f"파일 선택 다이얼로그 열림, 선택할 파일: {[f.name for f in file_paths]}")
    
    # Windows 파일 선택 다이얼로그 자동화
    time.sleep(0.5)
    
    if file_paths:
        # 첫 번째 파일의 폴더 경로로 이동
        folder_path = str(file_paths[0].parent)
        pyautogui.hotkey("alt", "d")  # 주소창 활성화
        time.sleep(0.3)
        pyperclip.copy(folder_path)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1.0)
        
        # 첫 번째 파일 선택
        pyautogui.hotkey("ctrl", "f")  # 검색
        time.sleep(0.3)
        pyperclip.copy(file_paths[0].name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        pyautogui.press("enter")
        time.sleep(0.5)
        pyautogui.press("enter")  # 파일 선택
        time.sleep(0.3)
        
        # 나머지 파일들도 선택 (Ctrl+클릭)
        for file_path in file_paths[1:]:
            pyautogui.hotkey("ctrl", "f")
            time.sleep(0.3)
            pyperclip.copy(file_path.name)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(0.5)
            pyautogui.hotkey("ctrl", "enter")  # Ctrl+Enter로 추가 선택
        
        # 열기 버튼 클릭
        time.sleep(0.5)
        pyautogui.press("enter")
        time.sleep(1.0)
        print("파일 선택 완료")
        return True
    return False


def input_prompt():
    """프롬프트 입력칸 찾아서 클릭하고 텍스트 입력"""
    if find_and_click(PROMPT_INPUT_IMG, description="프롬프트 입력칸"):
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "a")  # 전체 선택
        time.sleep(0.2)
        pyautogui.write(PROMPT_TEXT, interval=0.05)
        time.sleep(0.3)
        print("프롬프트 입력 완료")
        return True
    return False


def click_run_button():
    """실행 버튼 클릭"""
    return find_and_click(RUN_BUTTON_IMG, description="실행 버튼")


def run_single_cycle(clothes_file, model_file, cycle_num):
    """한 번의 자동화 사이클 실행"""
    print(f"\n=== 사이클 {cycle_num} 시작 ===")
    print(f"옷: {clothes_file.name}")
    print(f"모델: {model_file.name}")
    
    # 1. 확장 아이콘 클릭 (팝업 열기)
    if not click_extension_icon():
        print("확장 아이콘을 찾을 수 없습니다. 수동으로 클릭해주세요.")
        input("확장 아이콘 클릭 후 Enter를 눌러주세요...")
    
    time.sleep(0.5)  # 팝업이 열릴 때까지 대기
    
    # 2. 파일 업로드 버튼 클릭
    if not click_upload_button():
        print("파일 업로드 버튼을 찾을 수 없습니다.")
        return False
    
    # 3. 파일 선택 다이얼로그에서 파일 선택
    files_to_upload = [clothes_file, model_file]
    
    try:
        if not select_files_in_dialog(files_to_upload):
            print("자동 파일 선택 실패. 수동으로 파일을 선택해주세요.")
            input("파일 선택 완료 후 Enter를 눌러주세요...")
    except Exception as e:
        print(f"자동 파일 선택 실패: {e}")
        print("수동으로 파일을 선택해주세요.")
        input("파일 선택 완료 후 Enter를 눌러주세요...")
    
    # 4. 다시 확장 팝업 열기 (파일 선택 후)
    if not click_extension_icon():
        print("확장 아이콘을 찾을 수 없습니다. 수동으로 클릭해주세요.")
        input("확장 아이콘 클릭 후 Enter를 눌러주세요...")
    
    time.sleep(0.5)
    
    # 5. 프롬프트 입력
    if not input_prompt():
        print("프롬프트 입력칸을 찾을 수 없습니다.")
        return False
    
    # 6. 실행 버튼 클릭
    if not click_run_button():
        print("실행 버튼을 찾을 수 없습니다.")
        return False
    
    print(f"=== 사이클 {cycle_num} 완료 ===\n")
    return True


def main():
    """메인 실행 함수"""
    print("Freepik 이미지 인식 기반 매크로")
    print("=" * 50)
    
    # images 폴더 확인
    if not IMAGES_DIR.exists():
        IMAGES_DIR.mkdir()
        print(f"images 폴더를 생성했습니다.")
        print(f"\n다음 이미지들을 저장하세요:")
        print(f"  - {EXTENSION_ICON_IMG.name} (확장 아이콘 스크린샷)")
        print(f"  - {PROMPT_INPUT_IMG.name} (프롬프트 입력칸 스크린샷)")
        print(f"  - {UPLOAD_BUTTON_IMG.name} (파일 업로드 버튼 스크린샷)")
        print(f"  - {RUN_BUTTON_IMG.name} (실행 버튼 스크린샷)")
        print(f"\n스크린샷 찍는 방법:")
        print("  1. 각 요소를 화면에 표시")
        print("  2. Windows + Shift + S (스크린샷 도구)")
        print("  3. 해당 요소만 선택해서 캡처")
        print("  4. images 폴더에 저장")
        return
    
    # 이미지 파일 확인
    missing_images = []
    for img_path, name in [
        (EXTENSION_ICON_IMG, "확장 아이콘"),
        (UPLOAD_BUTTON_IMG, "파일 업로드 버튼"),
        (PROMPT_INPUT_IMG, "프롬프트 입력칸"),
        (RUN_BUTTON_IMG, "실행 버튼")
    ]:
        if not img_path.exists():
            missing_images.append(f"  - {img_path.name} ({name})")
    
    if missing_images:
        print("다음 이미지 파일이 없습니다:")
        for img in missing_images:
            print(img)
        print("\n스크린샷을 찍어서 images 폴더에 저장해주세요.")
        return
    
    # 파일 목록 가져오기
    clothes_files = sorted(CLOTHES_DIR.glob("*.*"))
    model_files = sorted(MODELS_DIR.glob("*.*"))
    
    if not clothes_files or not model_files:
        print("옷/모델 폴더에 이미지가 없습니다.")
        return
    
    pair_count = min(len(clothes_files), len(model_files))
    
    if pair_count == 0:
        print("각 폴더에 최소 1장 이상의 이미지가 필요합니다.")
        return
    
    print(f"총 {pair_count}개 조합을 처리합니다.")
    print("\n주의사항:")
    print("1. 크롬 브라우저가 열려 있고 Freepik에 로그인되어 있어야 합니다.")
    print("2. 확장 프로그램이 설치되어 있어야 합니다.")
    print("3. 이미지 파일이 images 폴더에 있어야 합니다.")
    print("\n5초 후 시작합니다...")
    time.sleep(5)
    
    # 각 조합마다 반복
    for i in range(pair_count):
        try:
            success = run_single_cycle(clothes_files[i], model_files[i], i + 1)
            
            if not success:
                print("사이클 실패. 계속 진행하려면 Enter를 누르세요...")
                input()
            
            # 다음 사이클 전 대기
            if i < pair_count - 1:
                print("다음 사이클까지 대기 중... (10초)")
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n사용자에 의해 중단되었습니다.")
            break
        except Exception as e:
            print(f"에러 발생: {e}")
            print("계속 진행하려면 Enter를 누르세요...")
            input()
    
    print("\n모든 작업 완료!")


if __name__ == "__main__":
    try:
        import pyperclip
    except ImportError:
        print("pyperclip 모듈이 필요합니다. 설치 중...")
        os.system("pip install pyperclip")
        import pyperclip
    
    main()

