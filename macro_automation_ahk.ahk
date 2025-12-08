; AutoHotkey 스크립트: Freepik 자동화 매크로
; 크롬 확장 프로그램 팝업을 자동으로 조작

; 좌표 설정 (사용자가 화면에 맞게 조정 필요)
PopupX := 100
PopupY := 200
PromptInputX := PopupX + 20
PromptInputY := PopupY + 80
UploadButtonX := PopupX + 130
UploadButtonY := PopupY + 180
RunButtonX := PopupX + 130
RunButtonY := PopupY + 220
ExtensionIconX := 1800
ExtensionIconY := 50

; 프롬프트 텍스트
PromptText := "Please naturally composite the product from @img1 onto the model in @img2."

; 파일 경로 (사용자가 수정 필요)
ClothesDir := "D:\images\clothes"
ModelsDir := "D:\images\models"

; ============================================
; 함수: 확장 아이콘 클릭
; ============================================
ClickExtensionIcon() {
    global ExtensionIconX, ExtensionIconY
    Click, %ExtensionIconX%, %ExtensionIconY%
    Sleep, 500
    ToolTip, 확장 아이콘 클릭 완료
    Sleep, 500
    ToolTip
}

; ============================================
; 함수: 프롬프트 입력
; ============================================
InputPrompt() {
    global PromptInputX, PromptInputY, PromptText
    Click, %PromptInputX%, %PromptInputY%
    Sleep, 300
    Send, ^a  ; Ctrl+A (전체 선택)
    Sleep, 200
    SendRaw, %PromptText%
    Sleep, 300
    ToolTip, 프롬프트 입력 완료
    Sleep, 500
    ToolTip
}

; ============================================
; 함수: 파일 업로드 버튼 클릭
; ============================================
ClickUploadButton() {
    global UploadButtonX, UploadButtonY
    Click, %UploadButtonX%, %UploadButtonY%
    Sleep, 1000
    ToolTip, 파일 업로드 버튼 클릭 완료
    Sleep, 500
    ToolTip
}

; ============================================
; 함수: 실행 버튼 클릭
; ============================================
ClickRunButton() {
    global RunButtonX, RunButtonY
    Click, %RunButtonX%, %RunButtonY%
    Sleep, 1000
    ToolTip, 실행 버튼 클릭 완료
    Sleep, 500
    ToolTip
}

; ============================================
; 함수: 이미지 생성 대기
; ============================================
WaitForGeneration() {
    ToolTip, 이미지 생성 대기 중... (20초)
    Sleep, 20000
    ToolTip
}

; ============================================
; 메인 자동화 사이클
; ============================================
RunAutomationCycle() {
    ClickExtensionIcon()
    InputPrompt()
    ClickUploadButton()
    
    ; 파일 선택 다이얼로그는 수동 처리 필요
    MsgBox, 0, 파일 선택, 파일 선택 다이얼로그가 열렸습니다.`n파일을 선택한 후 OK를 누르세요.
    
    ClickRunButton()
    WaitForGeneration()
}

; ============================================
; 단축키: F1 = 한 번 실행
; ============================================
F1::
    RunAutomationCycle()
    return

; ============================================
; 단축키: F2 = 5번 반복 실행
; ============================================
F2::
    Loop, 5 {
        RunAutomationCycle()
        Sleep, 2000
    }
    MsgBox, 자동화 완료
    return

; ============================================
; 단축키: ESC = 종료
; ============================================
Esc::
    ExitApp
    return




