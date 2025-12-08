"""
Freepik 자동화 매크로
크롬 확장 프로그램의 팝업을 자동으로 조작하여 반복 작업 수행
"""
import pyautogui
import time
import os
from pathlib import Path

# pyautogui 안전 설정
pyautogui.FAILSAFE = True  # 마우스를 왼쪽 상단 모서리로 이동하면 중단
pyautogui.PAUSE = 0.5  # 각 동작 사이 0.5초 대기

# 확장 프로그램 팝업 위치 (화면 좌표, 사용자가 직접 조정 필요)
POPUP_X = 100  # 확장 아이콘 클릭 후 팝업이 뜨는 X 좌표
POPUP_Y = 200  # 확장 아이콘 클릭 후 팝업이 뜨는 Y 좌표

# 프롬프트 입력칸 위치 (팝업 내부)
PROMPT_INPUT_X = POPUP_X + 20
PROMPT_INPUT_Y = POPUP_Y + 80

# 버튼 위치
UPLOAD_BUTTON_X = POPUP_X + 130
UPLOAD_BUTTON_Y = POPUP_Y + 180

RUN_BUTTON_X = POPUP_X + 130
RUN_BUTTON_Y = POPUP_Y + 220

# 파일 경로 설정
CLOTHES_DIR = Path(r"D:\images\clothes")  # 옷 이미지 폴더
MODELS_DIR = Path(r"D:\images\models")    # 모델 이미지 폴더

PROMPT_TEXT = "Please naturally composite the product from @img1 onto the model in @img2."


def click_extension_icon():
    """크롬 확장 프로그램 아이콘 클릭"""
    # 확장 아이콘 위치 찾기 (화면 우측 상단)
    # 실제 위치는 사용자가 조정 필요
    icon_x = 1800  # 화면 너비에 따라 조정
    icon_y = 50
    
    pyautogui.click(icon_x, icon_y)
    time.sleep(0.5)
    print("확장 아이콘 클릭 완료")


def input_prompt():
    """팝업에서 프롬프트 입력"""
    pyautogui.click(PROMPT_INPUT_X, PROMPT_INPUT_Y)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")  # 전체 선택
    time.sleep(0.2)
    pyautogui.write(PROMPT_TEXT, interval=0.05)
    time.sleep(0.3)
    print("프롬프트 입력 완료")


def click_upload_button():
    """파일 업로드 버튼 클릭"""
    pyautogui.click(UPLOAD_BUTTON_X, UPLOAD_BUTTON_Y)
    time.sleep(1.0)  # 파일 선택 다이얼로그가 뜰 때까지 대기
    print("파일 업로드 버튼 클릭 완료")


def select_files_in_dialog(file_paths):
    """파일 선택 다이얼로그에서 파일 선택"""
    # 파일 경로를 클립보드에 복사하고 붙여넣기
    import pyperclip
    
    # 여러 파일 선택: Ctrl+A (모든 파일 선택) 또는 개별 파일 클릭
    # 여기서는 파일 경로 입력창에 직접 경로 입력하는 방식
    time.sleep(0.5)
    
    # 파일 경로 입력창 활성화 (보통 주소창)
    pyautogui.hotkey("ctrl", "l")  # 주소창으로 이동
    time.sleep(0.3)
    
    # 첫 번째 파일 경로 입력
    if file_paths:
        full_path = str(file_paths[0])
        pyperclip.copy(full_path)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1.0)
        print(f"파일 선택 완료: {full_path}")


def click_run_button():
    """Freepik에서 실행 버튼 클릭"""
    pyautogui.click(RUN_BUTTON_X, RUN_BUTTON_Y)
    time.sleep(1.0)
    print("실행 버튼 클릭 완료")


def wait_for_generation():
    """이미지 생성 완료 대기 (약 15-20초)"""
    print("이미지 생성 대기 중...")
    time.sleep(20)


def run_automation_cycle(clothes_files, model_files, pair_index):
    """한 번의 자동화 사이클 실행"""
    print(f"\n=== 세트 {pair_index + 1} 시작 ===")
    
    # 1. 확장 아이콘 클릭
    click_extension_icon()
    
    # 2. 프롬프트 입력
    input_prompt()
    
    # 3. 파일 업로드 버튼 클릭
    click_upload_button()
    
    # 4. 파일 선택 (옷 2개 + 모델 2개)
    pair_clothes = clothes_files[pair_index * 2 : (pair_index + 1) * 2]
    pair_models = model_files[pair_index * 2 : (pair_index + 1) * 2]
    all_files = pair_clothes + pair_models
    
    # 파일 선택 다이얼로그 처리
    # 주의: Windows 파일 선택 다이얼로그는 pyautogui로 직접 조작이 어려울 수 있음
    # 대안: 확장 프로그램에서 직접 파일 경로를 받아서 처리하도록 수정 필요
    # 여기서는 일단 파일 업로드 버튼만 클릭하고, 사용자가 수동으로 파일 선택하도록 안내
    
    print("파일 선택 다이얼로그가 열렸습니다. 수동으로 파일을 선택해주세요.")
    print(f"선택할 파일: {[f.name for f in all_files]}")
    input("파일 선택 완료 후 Enter를 눌러주세요...")
    
    # 5. 실행 버튼 클릭
    click_run_button()
    
    # 6. 생성 완료 대기
    wait_for_generation()
    
    print(f"=== 세트 {pair_index + 1} 완료 ===\n")


def main():
    """메인 실행 함수"""
    print("Freepik 자동화 매크로 시작")
    print("=" * 50)
    
    # 파일 목록 가져오기
    clothes_files = sorted(CLOTHES_DIR.glob("*.*"))
    model_files = sorted(MODELS_DIR.glob("*.*"))
    
    if not clothes_files or not model_files:
        print("옷/모델 폴더에 이미지가 없습니다.")
        return
    
    pair_count = min(len(clothes_files), len(model_files)) // 2
    if pair_count == 0:
        print("각 폴더에 최소 2장 이상의 이미지가 필요합니다.")
        return
    
    print(f"총 {pair_count}개 세트를 처리합니다.")
    print("\n주의: 매크로 실행 전에 다음을 확인하세요:")
    print("1. 크롬 브라우저가 열려 있고 Freepik에 로그인되어 있어야 합니다.")
    print("2. 확장 프로그램이 설치되어 있어야 합니다.")
    print("3. 팝업 좌표가 화면에 맞게 조정되어 있어야 합니다.")
    print("\n5초 후 시작합니다...")
    time.sleep(5)
    
    # 각 세트마다 반복
    for i in range(pair_count):
        try:
            run_automation_cycle(clothes_files, model_files, i)
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




