"""
크롬이 디버깅 모드로 실행되었는지 확인
"""
import requests
import subprocess
import sys


def check_debug_port():
    """포트 9222 확인"""
    print("=" * 60)
    print("크롬 디버깅 모드 확인")
    print("=" * 60)
    
    # IPv4로 먼저 시도
    urls = [
        "http://127.0.0.1:9222/json",
        "http://localhost:9222/json",
        "http://[::1]:9222/json"
    ]
    
    for url in urls:
        try:
            print(f"\n{url} 연결 시도 중...")
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                print(f"✓ 연결 성공! ({url})")
                data = response.json()
                print(f"  - 연결된 페이지 수: {len(data)}")
                
                if data:
                    print("\n  페이지 목록:")
                    for i, page in enumerate(data[:5], 1):
                        print(f"    {i}. {page.get('url', 'N/A')[:70]}")
                    
                    freepik_pages = [p for p in data if "freepik.com" in p.get("url", "")]
                    if freepik_pages:
                        print(f"\n  ✓ Freepik 페이지: {len(freepik_pages)}개 발견")
                    else:
                        print("\n  ⚠ Freepik 페이지를 찾을 수 없습니다.")
                
                return True
            else:
                print(f"  응답 코드: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ✗ 연결 실패")
        except requests.exceptions.Timeout:
            print(f"  ✗ 타임아웃")
        except Exception as e:
            print(f"  ✗ 오류: {e}")
    
    print("\n" + "=" * 60)
    print("✗ 디버깅 포트에 연결할 수 없습니다!")
    print("=" * 60)
    print("\n확인 사항:")
    print("1. 크롬이 실행 중인가요?")
    print("   → 작업 관리자에서 chrome.exe 확인")
    print("\n2. 크롬이 디버깅 모드로 실행되었나요?")
    print("   → start_chrome_debug.bat 파일을 실행했나요?")
    print("   → 일반 크롬 실행과 디버깅 모드 실행은 다릅니다!")
    print("\n3. 포트 9222가 사용 중인가요?")
    print("   → netstat -ano | findstr :9222")
    print("\n해결 방법:")
    print("1. 모든 크롬 창을 완전히 닫기 (작업 관리자에서 확인)")
    print("2. start_chrome_debug.bat 파일 실행")
    print("3. 크롬이 열리면 Freepik에 로그인")
    print("4. 다시 이 스크립트 실행")
    
    return False


def check_chrome_process():
    """크롬 프로세스 확인"""
    print("\n" + "=" * 60)
    print("크롬 프로세스 확인")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq chrome.exe'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if 'chrome.exe' in result.stdout:
            print("✓ 크롬 프로세스가 실행 중입니다.")
            
            # 프로세스 수 확인
            lines = [l for l in result.stdout.split('\n') if 'chrome.exe' in l]
            print(f"  크롬 프로세스 수: {len(lines)}개")
            
            # 디버깅 포트 옵션 확인
            try:
                wmic_result = subprocess.run(
                    ['wmic', 'process', 'where', 'name="chrome.exe"', 'get', 'commandline', '/format:list'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if '--remote-debugging-port=9222' in wmic_result.stdout:
                    print("  ✓ 디버깅 모드(--remote-debugging-port=9222) 확인됨!")
                    return True
                else:
                    print("  ✗ 디버깅 모드 옵션이 없습니다!")
                    print("  → 크롬이 일반 모드로 실행되었을 수 있습니다.")
                    print("  → start_chrome_debug.bat로 다시 실행하세요.")
                    return False
            except Exception as e:
                print(f"  (상세 정보 확인 실패: {e})")
                return False
        else:
            print("✗ 크롬 프로세스를 찾을 수 없습니다.")
            return False
            
    except Exception as e:
        print(f"✗ 프로세스 확인 실패: {e}")
        return False


if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("requests 모듈 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    port_ok = check_debug_port()
    process_ok = check_chrome_process()
    
    print("\n" + "=" * 60)
    print("결과 요약")
    print("=" * 60)
    print(f"디버깅 포트 연결: {'✓' if port_ok else '✗'}")
    print(f"크롬 프로세스 확인: {'✓' if process_ok else '✗'}")
    
    if port_ok and process_ok:
        print("\n✓✓✓ 모든 확인 완료! 디버깅 모드가 정상 작동 중입니다. ✓✓✓")
    else:
        print("\n✗ 문제가 발견되었습니다. 위의 해결 방법을 참고하세요.")
    
    print("\n계속하려면 Enter를 누르세요...")
    input()


