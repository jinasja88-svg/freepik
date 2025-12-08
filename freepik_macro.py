"""
Freepik 이미지 업로드 + 프롬프트 입력 매크로
확장 프로그램과 연동하여 자동화
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
# 확장 아이콘 위치 (크롬 주소창 옆)
EXTENSION_ICON_X = 1800
EXTENSION_ICON_Y = 50

# 팝업 내부 좌표 (팝업이 열린 후 기준)
POPUP_X = 100  # 팝업 왼쪽 상단 X
POPUP_Y = 200  # 팝업 왼쪽 상단 Y
PROMPT_INPUT_X = POPUP_X + 20
PROMPT_INPUT_Y = POPUP_Y + 80
UPLOAD_BUTTON_X = POPUP_X + 130
UPLOAD_BUTTON_Y = POPUP_Y + 180
RUN_BUTTON_X = POPUP_X + 130
RUN_BUTTON_Y = POPUP_Y + 220


def find_extension_icon():
    """확장 프로그램 아이콘 찾기 (이미지 인식 또는 좌표)"""
    # 방법 1: 좌표로 클릭
    pyautogui.click(EXTENSION_ICON_X, EXTENSION_ICON_Y)
    time.sleep(0.5)
    print("확장 아이콘 클릭 완료")
    return True


def click_upload_button():
    """파일 업로드 버튼 클릭"""
    pyautogui.click(UPLOAD_BUTTON_X, UPLOAD_BUTTON_Y)
    time.sleep(1.5)  # 파일 선택 다이얼로그가 뜰 때까지 대기
    print("파일 업로드 버튼 클릭 완료")


def select_files_in_dialog(file_paths):
    """파일 선택 다이얼로그에서 파일 선택"""
    print(f"파일 선택 다이얼로그 열림, 선택할 파일: {[f.name for f in file_paths]}")
    
    # Windows 파일 선택 다이얼로그 자동화
    # 주의: 이 부분은 Windows 버전과 설정에 따라 다를 수 있음
    
    time.sleep(0.5)
    
    # 방법 1: 주소창에 경로 입력
    # Alt+D로 주소창 활성화
    pyautogui.hotkey("alt", "d")
    time.sleep(0.3)
    
    # 첫 번째 파일의 폴더 경로 입력
    if file_paths:
        folder_path = str(file_paths[0].parent)
        pyperclip.copy(folder_path)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1.0)
        
        # 파일 선택 (Ctrl+클릭으로 여러 파일 선택)
        # 첫 번째 파일 클릭
        # 파일 이름을 입력해서 찾기
        pyautogui.hotkey("ctrl", "f")  # 검색
        time.sleep(0.3)
        pyperclip.copy(file_paths[0].name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        pyautogui.press("enter")
        time.sleep(0.5)
        
        # 첫 번째 파일 선택
        pyautogui.press("enter")
        time.sleep(0.3)
        
        # 나머지 파일들도 선택 (Ctrl+클릭 시뮬레이션)
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
    else:
        print("선택할 파일이 없습니다.")


def input_prompt():
    """프롬프트 입력"""
    # 확장 팝업이 열려있는 상태에서
    pyautogui.click(PROMPT_INPUT_X, PROMPT_INPUT_Y)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")  # 전체 선택
    time.sleep(0.2)
    pyautogui.write(PROMPT_TEXT, interval=0.05)
    time.sleep(0.3)
    print("프롬프트 입력 완료")


def click_run_button():
    """실행 버튼 클릭"""
    pyautogui.click(RUN_BUTTON_X, RUN_BUTTON_Y)
    time.sleep(1.0)
    print("실행 버튼 클릭 완료")


def run_single_cycle(clothes_file, model_file, cycle_num):
    """한 번의 자동화 사이클 실행"""
    print(f"\n=== 사이클 {cycle_num} 시작 ===")
    print(f"옷: {clothes_file.name}")
    print(f"모델: {model_file.name}")
    
    # 1. 확장 아이콘 클릭 (팝업 열기)
    find_extension_icon()
    time.sleep(0.5)  # 팝업이 열릴 때까지 대기
    
    # 2. 파일 업로드 버튼 클릭
    click_upload_button()
    
    # 3. 파일 선택 다이얼로그에서 파일 선택
    files_to_upload = [clothes_file, model_file]
    
    try:
        select_files_in_dialog(files_to_upload)
    except Exception as e:
        print(f"자동 파일 선택 실패: {e}")
        print("수동으로 파일을 선택해주세요.")
        input("파일 선택 완료 후 Enter를 눌러주세요...")
    
    # 4. 다시 확장 팝업 열기 (파일 선택 후)
    find_extension_icon()
    time.sleep(0.5)
    
    # 5. 프롬프트 입력
    input_prompt()
    
    # 6. 실행 버튼 클릭
    click_run_button()
    
    print(f"=== 사이클 {cycle_num} 완료 ===\n")


def main():
    """메인 실행 함수"""
    print("Freepik 이미지 업로드 + 프롬프트 입력 매크로")
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
            
            # 다음 사이클 전 대기 (이미지 생성 시간 고려)
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


