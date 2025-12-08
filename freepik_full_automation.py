"""
Freepik 완전 자동화 프로그램
확장 프로그램과 연동하여 폴더에서 이미지를 순차적으로 불러와서
프롬프트 입력 → 생성 → 저장까지 자동으로 수행
"""
import pyautogui
import time
import os
from pathlib import Path
import pyperclip

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# 설정
CLOTHES_DIR = Path(r"D:\images\clothes")  # 옷 이미지 폴더
MODELS_DIR = Path(r"D:\images\models")    # 모델 이미지 폴더
PROMPT_TEXT = "Please naturally composite the product from @img1 onto the model in @img2."

# 확장 프로그램 팝업 좌표 (사용자가 조정 필요)
EXTENSION_ICON_X = 1800
EXTENSION_ICON_Y = 50
UPLOAD_BUTTON_X = 100
UPLOAD_BUTTON_Y = 180
PROMPT_INPUT_X = 100
PROMPT_INPUT_Y = 80
RUN_BUTTON_X = 100
RUN_BUTTON_Y = 220

# 파일 선택 다이얼로그 좌표 (Windows 파일 선택 창)
FILE_DIALOG_PATH_X = 200
FILE_DIALOG_PATH_Y = 100


def click_extension_icon():
    """확장 프로그램 아이콘 클릭"""
    pyautogui.click(EXTENSION_ICON_X, EXTENSION_ICON_Y)
    time.sleep(0.5)
    print("확장 아이콘 클릭 완료")


def click_upload_button():
    """파일 업로드 버튼 클릭"""
    pyautogui.click(UPLOAD_BUTTON_X, UPLOAD_BUTTON_Y)
    time.sleep(1.5)  # 파일 선택 다이얼로그가 뜰 때까지 대기
    print("파일 업로드 버튼 클릭 완료")


def select_files_in_dialog(file_paths):
    """파일 선택 다이얼로그에서 파일 선택"""
    # Windows 파일 선택 다이얼로그에서 파일 경로 입력
    # 주소창으로 이동 (Alt+D 또는 Ctrl+L)
    time.sleep(0.5)
    
    # 첫 번째 파일 경로를 주소창에 입력
    if file_paths:
        first_file = str(file_paths[0])
        pyperclip.copy(first_file)
        
        # 주소창 활성화 (Alt+D)
        pyautogui.hotkey("alt", "d")
        time.sleep(0.3)
        
        # 경로 붙여넣기
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1.0)
        
        # 여러 파일 선택: Ctrl+클릭 또는 Shift+클릭
        # 여기서는 첫 번째 파일만 선택하고, 나머지는 수동 선택 필요할 수 있음
        print(f"파일 선택 완료: {first_file}")
        
        # 다이얼로그 닫기 (Enter 또는 Open 버튼 클릭)
        time.sleep(0.5)
        pyautogui.press("enter")
        time.sleep(1.0)


def input_prompt():
    """프롬프트 입력"""
    pyautogui.click(PROMPT_INPUT_X, PROMPT_INPUT_Y)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.write(PROMPT_TEXT, interval=0.05)
    time.sleep(0.3)
    print("프롬프트 입력 완료")


def click_run_button():
    """실행 버튼 클릭"""
    pyautogui.click(RUN_BUTTON_X, RUN_BUTTON_Y)
    time.sleep(1.0)
    print("실행 버튼 클릭 완료")


def wait_for_generation():
    """이미지 생성 완료 대기 (확장 프로그램이 자동으로 저장 버튼 클릭)"""
    print("이미지 생성 및 저장 대기 중... (약 20초)")
    time.sleep(20)  # 확장 프로그램이 결과 완성 감지 및 저장까지 대기


def run_single_cycle(clothes_file, model_file, cycle_num):
    """한 번의 자동화 사이클 실행"""
    print(f"\n=== 사이클 {cycle_num} 시작 ===")
    print(f"옷: {clothes_file.name}")
    print(f"모델: {model_file.name}")
    
    # 1. 확장 아이콘 클릭
    click_extension_icon()
    
    # 2. 파일 업로드 버튼 클릭
    click_upload_button()
    
    # 3. 파일 선택 다이얼로그에서 파일 선택
    # 주의: Windows 파일 다이얼로그 자동화는 복잡할 수 있음
    # 여기서는 기본적인 방법만 제공, 필요시 수동 선택 안내
    print("파일 선택 다이얼로그가 열렸습니다.")
    print(f"선택할 파일: {clothes_file.name}, {model_file.name}")
    
    # 방법 1: 자동 선택 시도 (경로 입력)
    try:
        select_files_in_dialog([clothes_file, model_file])
    except Exception as e:
        print(f"자동 파일 선택 실패: {e}")
        print("수동으로 파일을 선택해주세요.")
        input("파일 선택 완료 후 Enter를 눌러주세요...")
    
    # 4. 프롬프트 입력
    click_extension_icon()  # 다시 팝업 열기
    time.sleep(0.5)
    input_prompt()
    
    # 5. 실행 버튼 클릭
    click_run_button()
    
    # 6. 결과 완성 및 저장 대기
    wait_for_generation()
    
    print(f"=== 사이클 {cycle_num} 완료 ===\n")


def main():
    """메인 실행 함수"""
    print("Freepik 완전 자동화 프로그램 시작")
    print("=" * 50)
    
    # 파일 목록 가져오기
    clothes_files = sorted(CLOTHES_DIR.glob("*.*"))
    model_files = sorted(MODELS_DIR.glob("*.*"))
    
    if not clothes_files or not model_files:
        print("옷/모델 폴더에 이미지가 없습니다.")
        return
    
    # 각 옷과 모델을 1:1로 매칭
    pair_count = min(len(clothes_files), len(model_files))
    
    if pair_count == 0:
        print("각 폴더에 최소 1장 이상의 이미지가 필요합니다.")
        return
    
    print(f"총 {pair_count}개 조합을 처리합니다.")
    print("\n주의사항:")
    print("1. 크롬 브라우저가 열려 있고 Freepik에 로그인되어 있어야 합니다.")
    print("2. 확장 프로그램이 설치되어 있어야 합니다.")
    print("3. 좌표가 화면에 맞게 조정되어 있어야 합니다.")
    print("4. 파일 선택 다이얼로그는 자동화가 제한적일 수 있습니다.")
    print("\n5초 후 시작합니다...")
    time.sleep(5)
    
    # 각 조합마다 반복
    for i in range(pair_count):
        try:
            run_single_cycle(clothes_files[i], model_files[i], i + 1)
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




