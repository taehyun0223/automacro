"""
게임 자동 활성화 후 캡처 (이모지 제거 버전)
"""
import pyautogui
import pygetwindow as gw
import time
import os


def find_game_window():
    """블루아카이브 윈도우 찾기"""
    try:
        all_windows = gw.getAllWindows()
        
        for window in all_windows:
            if window.title and "Blue Archive" in window.title:
                if "Visual Studio" not in window.title and "Code" not in window.title:
                    return window
        return None
    except Exception as e:
        print(f"윈도우 찾기 오류: {e}")
        return None


def activate_and_capture():
    """게임 활성화 후 캡처"""
    os.makedirs("screenshots", exist_ok=True)
    
    print("=== 게임 자동 활성화 + 캡처 ===")
    
    # 1. 게임 찾기
    print("1. 게임 윈도우 검색...")
    window = find_game_window()
    
    if not window:
        print("게임을 찾을 수 없습니다!")
        return None
    
    print(f"게임 발견: {window.title}")
    print(f"위치: ({window.left}, {window.top})")
    print(f"크기: {window.width} x {window.height}")
    print(f"활성화 상태: {window.isActive}")
    
    # 2. 게임이 비활성화되어 있으면 클릭해서 활성화
    if not window.isActive:
        print("2. 게임 윈도우 클릭해서 활성화...")
        
        # 윈도우 중앙 클릭
        center_x = window.left + window.width // 2
        center_y = window.top + window.height // 2
        
        print(f"클릭 위치: ({center_x}, {center_y})")
        pyautogui.click(center_x, center_y)
        
        print("활성화 대기 중...")
        time.sleep(3.0)  # 3초 대기
        
    else:
        print("2. 게임이 이미 활성화되어 있습니다.")
    
    # 3. 화면 캡처
    print("3. 화면 캡처 중...")
    timestamp = time.strftime("%H%M%S")
    
    try:
        screenshot = pyautogui.screenshot()
        filename = f"screenshots/auto_capture_{timestamp}.png"
        screenshot.save(filename)
        print(f"캡처 완료: {filename}")
        return filename
    except Exception as e:
        print(f"캡처 오류: {e}")
        return None


if __name__ == "__main__":
    print("게임 자동 활성화 테스트 시작!")
    print("3초 후 시작...")
    
    for i in range(3, 0, -1):
        print(f"{i}초...")
        time.sleep(1)
    
    result = activate_and_capture()
    
    if result:
        print(f"성공! {result} 파일을 확인하세요!")
    else:
        print("실패했습니다.")