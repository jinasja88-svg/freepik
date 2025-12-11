# GitHub 업로드 가이드

## 방법 1: GitHub 웹사이트에서 저장소 생성 후 업로드

### 1단계: GitHub에서 저장소 생성
1. https://github.com 에 로그인
2. 우측 상단의 "+" 버튼 클릭 → "New repository" 선택
3. 저장소 이름 입력 (예: `freepik-automation`)
4. Public 또는 Private 선택
5. "Create repository" 클릭

### 2단계: 원격 저장소 추가 및 푸시
저장소를 만든 후, 아래 명령어를 실행하세요:

```bash
# 원격 저장소 추가 (YOUR_USERNAME과 REPO_NAME을 실제 값으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 메인 브랜치 이름을 main으로 변경 (GitHub 기본값)
git branch -M main

# GitHub에 푸시
git push -u origin main
```

예시:
```bash
git remote add origin https://github.com/yourusername/freepik-automation.git
git branch -M main
git push -u origin main
```

## 방법 2: 저장소 이름을 알려주시면 자동으로 설정해드립니다

저장소 이름을 알려주시면 원격 저장소를 추가하고 푸시하는 명령어를 실행해드릴 수 있습니다.





