# Freepik 매크로 설정 가이드

## 좌표 설정 방법

### 1. 확장 아이콘 위치 찾기
1. 크롬 브라우저 열기
2. 확장 프로그램 아이콘 위치 확인 (주소창 옆)
3. 마우스를 아이콘 위에 올리고 위치 확인
4. `freepik_macro.py`에서 수정:
   ```python
   EXTENSION_ICON_X = 1800  # 실제 X 좌표
   EXTENSION_ICON_Y = 50    # 실제 Y 좌표
   ```

### 2. 팝업 내부 좌표 찾기
1. 확장 프로그램 아이콘 클릭 → 팝업 열기
2. 각 요소의 위치 확인:
   - 프롬프트 입력칸
   - 파일 업로드 버튼
   - 실행 버튼
3. Windows에서 좌표 확인:
   - AutoHotkey 사용: `ToolTip` 명령어
   - Python 사용: `pyautogui.position()` 함수
4. `freepik_macro.py`에서 수정:
   ```python
   POPUP_X = 100  # 팝업 왼쪽 상단 X
   POPUP_Y = 200  # 팝업 왼쪽 상단 Y
   PROMPT_INPUT_X = POPUP_X + 20
   PROMPT_INPUT_Y = POPUP_Y + 80
   UPLOAD_BUTTON_X = POPUP_X + 130
   UPLOAD_BUTTON_Y = POPUP_Y + 180
   RUN_BUTTON_X = POPUP_X + 130
   RUN_BUTTON_Y = POPUP_Y + 220
   ```

## 좌표 확인 스크립트

`test_coordinates.py` 파일을 만들어서 좌표를 확인할 수 있어요:

```python
import pyautogui
import time

print("마우스를 원하는 위치에 올리고 3초 후 좌표가 출력됩니다...")
time.sleep(3)
x, y = pyautogui.position()
print(f"X: {x}, Y: {y}")
```

## 사용 방법

1. 좌표 설정 완료
2. 폴더 경로 설정:
   ```python
   CLOTHES_DIR = Path(r"D:\images\clothes")
   MODELS_DIR = Path(r"D:\images\models")
   ```
3. 실행:
   ```bash
   python freepik_macro.py
   ```

## 주의사항

- 파일 선택 다이얼로그 자동화는 Windows 버전에 따라 다를 수 있어요
- 자동 선택이 실패하면 수동으로 파일을 선택해야 할 수 있어요
- 좌표는 화면 해상도에 따라 달라질 수 있어요


