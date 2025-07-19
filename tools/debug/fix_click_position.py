"""
클릭 위치 수정 및 보정
"""
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
import os


def get_window_client_area(window):
    """윈도우의 실제 클라이언트 영역 계산"""
    # Windows에서 윈도우 테두리 보정
    # 일반적으로 타이틀바 높이 30px, 테두리 8px 정도
    
    title_bar_height = 30
    border_width = 8
    
    client_left = window.left + border_width
    client_top = window.top + title_bar_height
    client_width = window.width - (border_width * 2)
    client_height = window.height - title_bar_height - border_width
    
    return client_left, client_top, client_width, client_height


def test_corrected_click():
    """보정된 클릭 테스트"""
    print("=== 보정된 클릭 위치 테스트 ===")
    
    # 게임 윈도우 찾기
    all_windows = gw.getAllWindows()
    game_window = None
    
    for window in all_windows:
        if window.title and "Blue Archive" in window.title:
            if "Visual Studio" not in window.title and "Code" not in window.title:
                game_window = window
                break
    
    if not game_window:
        print("게임 윈도우를 찾을 수 없습니다")
        return
    
    print(f"게임 윈도우 정보:")
    print(f"  제목: {game_window.title}")
    print(f"  원본 위치: ({game_window.left}, {game_window.top})")
    print(f"  원본 크기: {game_window.width} x {game_window.height}")
    
    # 클라이언트 영역 계산
    client_left, client_top, client_width, client_height = get_window_client_area(game_window)
    
    print(f"  보정된 위치: ({client_left}, {client_top})")
    print(f"  보정된 크기: {client_width} x {client_height}")
    
    # 윈도우 활성화
    if not game_window.isActive:
        print("게임 윈도우 활성화...")
        center_x = game_window.left + game_window.width // 2
        center_y = game_window.top + game_window.height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(2.0)
    
    # 방법 1: 원본 방법으로 캡처
    print("\n방법 1: 원본 윈도우 영역 캡처")
    screenshot1 = pyautogui.screenshot(
        region=(game_window.left, game_window.top, game_window.width, game_window.height)
    )
    screenshot1_cv = cv2.cvtColor(np.array(screenshot1), cv2.COLOR_RGB2BGR)
    
    # 방법 2: 보정된 클라이언트 영역 캡처
    print("방법 2: 보정된 클라이언트 영역 캡처")
    screenshot2 = pyautogui.screenshot(
        region=(client_left, client_top, client_width, client_height)
    )
    screenshot2_cv = cv2.cvtColor(np.array(screenshot2), cv2.COLOR_RGB2BGR)
    
    # 두 방법 모두 저장
    timestamp = time.strftime("%H%M%S")
    cv2.imwrite(f"screenshots/original_capture_{timestamp}.png", screenshot1_cv)
    cv2.imwrite(f"screenshots/corrected_capture_{timestamp}.png", screenshot2_cv)
    
    print(f"원본 캡처 저장: screenshots/original_capture_{timestamp}.png")
    print(f"보정 캡처 저장: screenshots/corrected_capture_{timestamp}.png")
    
    # 카페 버튼 매칭 (보정된 영역에서)
    template_file = "assets/cafe_button.png"
    if not os.path.exists(template_file):
        print(f"템플릿 파일이 없습니다: {template_file}")
        return
    
    template = cv2.imread(template_file)
    gray_screenshot = cv2.cvtColor(screenshot2_cv, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    print(f"\n카페 버튼 매칭 (보정된 영역):")
    print(f"  신뢰도: {max_val:.3f}")
    print(f"  매칭 위치: {max_loc}")
    
    if max_val >= 0.5:
        template_h, template_w = gray_template.shape
        
        # 보정된 좌표에서 클릭 위치 계산
        game_x = max_loc[0] + template_w // 2
        game_y = max_loc[1] + template_h // 2
        
        # 화면 절대 좌표
        screen_x = client_left + game_x
        screen_y = client_top + game_y
        
        print(f"클릭 위치:")
        print(f"  게임 내: ({game_x}, {game_y})")
        print(f"  화면: ({screen_x}, {screen_y})")
        
        # 디버그 이미지 생성
        debug_img = screenshot2_cv.copy()
        cv2.rectangle(debug_img, max_loc, 
                      (max_loc[0] + template_w, max_loc[1] + template_h), 
                      (0, 255, 0), 3)
        cv2.circle(debug_img, (game_x, game_y), 10, (0, 0, 255), -1)
        cv2.putText(debug_img, f"({game_x}, {game_y})", 
                    (game_x + 15, game_y - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.imwrite(f"screenshots/debug_corrected_{timestamp}.png", debug_img)
        print(f"보정된 디버그 이미지: screenshots/debug_corrected_{timestamp}.png")
        
        # 클릭 테스트
        print("3초 후 보정된 위치를 클릭합니다...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print(f"보정된 클릭 실행: ({screen_x}, {screen_y})")
        pyautogui.click(screen_x, screen_y)
        print("클릭 완료!")
        
        return True
    else:
        print("카페 버튼을 찾을 수 없습니다")
        return False


def manual_coordinate_test():
    """수동 좌표 테스트"""
    print("=== 수동 좌표 테스트 ===")
    print("마우스를 카페 버튼 위에 올리고 5초간 기다리세요...")
    
    time.sleep(5)
    
    mouse_x, mouse_y = pyautogui.position()
    print(f"현재 마우스 위치: ({mouse_x}, {mouse_y})")
    
    # 해당 위치 클릭 테스트
    print("해당 위치를 클릭하시겠습니까? (엔터를 누르면 클릭)")
    input()
    
    pyautogui.click(mouse_x, mouse_y)
    print("클릭 완료!")


if __name__ == "__main__":
    print("클릭 위치 수정 도구")
    print("1. 보정된 클릭 테스트")
    print("2. 수동 좌표 테스트")
    
    # 자동으로 보정된 클릭 테스트 실행
    test_corrected_click()