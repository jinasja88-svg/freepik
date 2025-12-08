"""
안정적인 Freepik 자동화 매크로 (이미지 인식 기반)
좌표 대신 화면에서 버튼 이미지를 찾아서 클릭하는 방식
"""
import pyautogui
import time
import os
from pathlib import Path

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# 확장 프로그램 팝업의 버튼 이미지 파일 경로
# 사용 전에 각 버튼의 스크린샷을 찍어서 images 폴더에 저장해야 함
IMAGES_DIR = Path(__file__).parent / "images"
EXTENSION_ICON_IMG = IMAGES_DIR / "extension_icon.png"
UPLOAD_BUTTON_IMG = IMAGES_DIR / "upload_button.png"
RUN_BUTTON_IMG = IMAGES_DIR / "run_button.png"
PROMPT_INPUT_IMG = IMAGES_DIR / "prompt_input.png"

PROMPT_TEXT = "Please naturally composite the product from @img1 onto the model in @img2."


def find_and_click(image_path, confidence=0.8, timeout=5):
    """화면에서 이미지를 찾아서 클릭"""
    try:
        location = pyautogui.locateOnScreen(str(image_path), confidence=confidence, timeout=timeout)
        if location:
            center = pyautogui.center(location)
            pyautogui.click(center)
            print(f"이미지 찾음 및 클릭: {image_path.name} at {center}")
            return True
        else:
            print(f"이미지를 찾을 수 없음: {image_path.name}")
            return False
    except pyautogui.ImageNotFoundException:
        print(f"이미지를 찾을 수 없음: {image_path.name}")
        return False
    except Exception as e:
        print(f"에러 발생: {e}")
        return False


def click_extension_icon():
    """확장 아이콘 클릭 (이미지 인식)"""
    if find_and_click(EXTENSION_ICON_IMG):
        time.sleep(0.5)
        return True
    return False


def input_prompt():
    """프롬프트 입력칸 찾아서 클릭하고 텍스트 입력"""
    if find_and_click(PROMPT_INPUT_IMG):
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        pyautogui.write(PROMPT_TEXT, interval=0.05)
        time.sleep(0.3)
        print("프롬프트 입력 완료")
        return True
    return False


def click_upload_button():
    """파일 업로드 버튼 클릭"""
    if find_and_click(UPLOAD_BUTTON_IMG):
        time.sleep(1.0)
        print("파일 업로드 버튼 클릭 완료")
        return True
    return False


def click_run_button():
    """실행 버튼 클릭"""
    if find_and_click(RUN_BUTTON_IMG):
        time.sleep(1.0)
        print("실행 버튼 클릭 완료")
        return True
    return False


def main():
    """메인 실행"""
    print("안정적인 Freepik 자동화 매크로 시작")
    print("=" * 50)
    
    # images 폴더 확인
    if not IMAGES_DIR.exists():
        IMAGES_DIR.mkdir()
        print(f"images 폴더를 생성했습니다. 다음 이미지들을 저장하세요:")
        print(f"  - extension_icon.png (확장 아이콘 스크린샷)")
        print(f"  - prompt_input.png (프롬프트 입력칸 스크린샷)")
        print(f"  - upload_button.png (파일 업로드 버튼 스크린샷)")
        print(f"  - run_button.png (실행 버튼 스크린샷)")
        return
    
    print("5초 후 시작합니다...")
    time.sleep(5)
    
    # 자동화 사이클
    click_extension_icon()
    input_prompt()
    click_upload_button()
    
    print("파일 선택 다이얼로그가 열렸습니다. 수동으로 파일을 선택해주세요.")
    input("파일 선택 완료 후 Enter를 눌러주세요...")
    
    click_run_button()
    
    print("자동화 완료!")


if __name__ == "__main__":
    main()




