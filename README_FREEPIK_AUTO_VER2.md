# Freepik 자동화 프로그램 - ver2.2

## 프로젝트 개요

Freepik AI 이미지 생성기를 자동화하는 Python 프로그램입니다. 
옷 이미지와 모델 이미지를 조합하여 자동으로 합성 이미지를 생성합니다.

## 주요 기능

- **이중 루프 구조**: clothes 폴더(8개) × model 폴더(8개) = 총 64번 작업
- **자동 파일 업로드**: Windows 파일 선택 다이얼로그 자동화
- **프롬프트 자동 입력**: 지정된 프롬프트 자동 입력
- **이미지 생성 대기**: 생성 완료까지 자동 대기
- **파일 자동 삭제**: 작업 완료 후 업로드된 파일 자동 삭제

## 파일 구조

### Python 스크립트
- `freepik_auto_simple_ver2.1.py` - 안정화된 버전 (삭제 버튼 개선)
- `freepik_auto_simple_ver2.2.py` - 현재 작업 중인 버전

### 실행 파일
- `run_freepik_auto.bat` - ver2.1 실행용
- `run_freepik_auto_ver2.2.bat` - ver2.2 실행용
- `start_chrome_debug.bat` - Chrome 디버깅 모드 실행용

### 폴더 구조
```
new/
├── model/          # 모델 이미지 폴더 (1.png ~ 8.png)
├── clothes/       # 옷 이미지 폴더 (1.png ~ 8.png)
└── [생성된 이미지들]
```

## 실행 방법

### 1. Chrome 디버깅 모드 실행
```bash
start_chrome_debug.bat
```
- 모든 Chrome 창을 먼저 닫아야 합니다
- Chrome이 디버깅 모드로 실행됩니다

### 2. Freepik 로그인
- 열린 Chrome 창에서 Freepik에 로그인합니다
- 이미지 생성 페이지로 이동합니다

### 3. 자동화 프로그램 실행
```bash
run_freepik_auto_ver2.2.bat
```
- 프로그램이 자동으로 작업을 시작합니다
- 총 64번의 작업이 순차적으로 실행됩니다

## 작업 흐름

### 각 작업마다 수행하는 단계

1. **파일 업로드**
   - model 폴더에서 이미지 업로드 (예: `1.png`)
   - clothes 폴더에서 이미지 업로드 (예: `1.png`)

2. **프롬프트 입력**
   - 기본 프롬프트: `"Please naturally composite the product from @img2 onto the model in @img1."`
   - 프롬프트 입력칸에 자동 입력

3. **Generate 버튼 클릭**
   - 버튼 활성화까지 대기 (최대 3초)
   - Generate 버튼 클릭

4. **생성 대기**
   - 이미지 생성 완료까지 1분 10초 대기

5. **파일 삭제**
   - 첫 번째 업로드 파일 삭제
   - 2초 대기
   - 두 번째 업로드 파일 삭제

6. **다음 작업으로 이동**
   - 마지막 작업이 아니면 2초 대기 후 다음 작업 시작

## 루프 구조

### 외부 루프: clothes 1~8
```
clothes 1.png → clothes 2.png → ... → clothes 8.png
```

### 내부 루프: model 1~8 (각 clothes마다)
```
model 1.png → model 2.png → ... → model 8.png
```

### 작업 순서 예시
- **1~8번**: model 1~8.png + clothes 1.png
- **9~16번**: model 1~8.png + clothes 2.png
- **17~24번**: model 1~8.png + clothes 3.png
- ...
- **57~64번**: model 1~8.png + clothes 8.png

## 기술 스택

- **Playwright**: 브라우저 자동화 및 DOM 조작
- **pyautogui**: Windows 파일 선택 다이얼로그 자동화
- **pyperclip**: 클립보드를 통한 경로 입력
- **asyncio**: 비동기 작업 처리

## 주요 기능 상세

### 파일 업로드 (`upload_file`)
1. 업로드 버튼 클릭
2. 모달 창 내 파일 선택 버튼 클릭
3. Windows 파일 선택 다이얼로그에서:
   - 폴더 경로 입력 (Alt+D → 경로 입력 → Enter)
   - 파일 이름 입력
   - Enter로 열기
4. 모달 창 내 "올라가" 버튼 클릭

### 파일 삭제
- 첫 번째 파일 삭제 후 2초 대기
- 두 번째 파일은 첫 번째 삭제 후 `nth-child(3)` 위치로 이동
- CSS 셀렉터와 JavaScript fallback 사용

### 에러 처리
- 각 단계에서 실패 시 JavaScript fallback 시도
- 최종 실패 시 수동 입력 대기

## 설정

### 프롬프트 텍스트
```python
PROMPT_TEXT = "Please naturally composite the product from @img2 onto the model in @img1."
```

### 폴더 경로
```python
MODEL_DIR = Path(r"D:\private\코딩\커서\new\model")
CLOTHES_DIR = Path(r"D:\private\코딩\커서\new\clothes")
```

### 대기 시간
- 파일 업로드 완료 대기: 1초
- Generate 버튼 활성화 대기: 최대 3초 (0.15초 간격)
- 이미지 생성 대기: 70초 (1분 10초)
- 첫 번째 삭제 후 대기: 2초
- 다음 작업 전 대기: 2초

## 버전 히스토리

### ver2.2 (현재)
- ver2.1에서 복사
- 추가 작업 예정

### ver2.1
- 삭제 버튼 개선
- 첫 번째 삭제 후 2초 대기 추가
- 두 번째 삭제 버튼 찾기 로직 개선 (nth-child(3) 위치로 이동 고려)
- JavaScript fallback 추가

### ver2.0
- 이중 루프 구조 구현
- 64번 작업 자동화

## 문제 해결

### Chrome 디버깅 모드 연결 실패
- 모든 Chrome 창을 닫고 `start_chrome_debug.bat` 실행
- 포트 9222가 사용 중인지 확인

### 파일 업로드 실패
- 파일 경로가 올바른지 확인
- 파일 이름이 정확한지 확인 (예: `1.png`, `2.png` 등)
- 파일 선택 다이얼로그가 포커스를 받았는지 확인

### 삭제 버튼 찾기 실패
- 첫 번째 파일 삭제 후 충분한 대기 시간 확보
- 수동으로 삭제 버튼 클릭 후 Enter 입력

## 주의사항

1. **Chrome 디버깅 모드 필수**: 프로그램 실행 전 반드시 Chrome을 디버깅 모드로 실행해야 합니다
2. **Freepik 로그인**: Chrome에서 미리 Freepik에 로그인해야 합니다
3. **파일 준비**: model과 clothes 폴더에 각각 1.png ~ 8.png 파일이 있어야 합니다
4. **인터넷 연결**: 안정적인 인터넷 연결이 필요합니다
5. **화면 해상도**: pyautogui 사용 시 화면 해상도 변경 시 문제가 발생할 수 있습니다

## 향후 개선 사항

- [ ] 이미지 생성 완료 감지 개선 (현재는 고정 대기 시간 사용)
- [ ] 생성된 이미지 자동 저장 기능
- [ ] 에러 발생 시 재시도 로직
- [ ] 진행 상황 로그 파일 저장
- [ ] GUI 인터페이스 추가

## 라이선스

개인 프로젝트

## 작성일

2025년 1월


