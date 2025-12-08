"""
좌표 확인 스크립트
마우스를 원하는 위치에 올리고 좌표를 확인
"""
import pyautogui
import time

print("=" * 50)
print("좌표 확인 도구")
print("=" * 50)
print("\n사용 방법:")
print("1. 마우스를 확인하고 싶은 위치에 올리세요")
print("2. Enter 키를 누르면 해당 위치의 좌표가 출력됩니다")
print("3. 'q'를 입력하고 Enter를 누르면 종료됩니다")
print("\n시작합니다...\n")

while True:
    try:
        user_input = input("Enter 키를 눌러 현재 마우스 위치 확인 (q: 종료): ")
        
        if user_input.lower() == 'q':
            print("종료합니다.")
            break
        
        x, y = pyautogui.position()
        print(f"현재 마우스 위치: X={x}, Y={y}")
        print(f"코드에 사용: EXTENSION_ICON_X = {x}, EXTENSION_ICON_Y = {y}")
        print()
        
    except KeyboardInterrupt:
        print("\n종료합니다.")
        break


