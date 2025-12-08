"""
크롬 디버깅 모드 바로가기 생성
"""
import os
from pathlib import Path

# 현재 스크립트 위치
script_dir = Path(__file__).parent
bat_file = script_dir / "크롬_디버깅모드_실행.bat"

# 바로가기 생성
try:
    import win32com.client
    
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "크롬_디버깅모드.lnk"
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(bat_file)
    shortcut.WorkingDirectory = str(script_dir)
    shortcut.Description = "크롬을 디버깅 모드로 실행"
    shortcut.save()
    
    print(f"✓ 바로가기 생성 완료: {shortcut_path}")
    
except ImportError:
    print("win32com이 필요합니다. 설치 중...")
    os.system("pip install pywin32")
    print("\n다시 실행해주세요:")
    print("python create_shortcut.py")
except Exception as e:
    print(f"바로가기 생성 실패: {e}")
    print("\n수동으로 바로가기를 만드세요:")
    print(f"1. 바탕화면에서 우클릭 → 새로 만들기 → 바로가기")
    print(f"2. 대상: {bat_file}")
    print(f"3. 이름: 크롬_디버깅모드")


