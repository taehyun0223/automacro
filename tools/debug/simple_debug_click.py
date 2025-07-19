"""
간단한 클릭 위치 디버깅
"""
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
import os


def debug_click_position():
    """클릭 위치 디버깅"""
    print("=== 클릭 위치 디버깅 ===")
    
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
    print(f"  위치: ({game_window.left}, {game_window.top})")
    print(f"  크기: {game_window.width} x {game_window.height}")
    print(f"  활성화: {game_window.isActive}")
    
    # 윈도우 활성화
    if not game_window.isActive:
        print("게임 윈도우 활성화...")
        center_x = game_window.left + game_window.width // 2
        center_y = game_window.top + game_window.height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(2.0)
    
    # 게임 화면 캡처
    print("게임 화면 캡처 중...")
    screenshot = pyautogui.screenshot(
        region=(game_window.left, game_window.top, game_window.width, game_window.height)
    )
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # 템플릿 매칭
    template_file = "assets/cafe_button.png"
    if not os.path.exists(template_file):
        print(f"템플릿 파일이 없습니다: {template_file}")
        return
    
    template = cv2.imread(template_file)
    print(f"템플릿 크기: {template.shape[1]} x {template.shape[0]}")
    
    # 그레이스케일 변환 및 매칭
    gray_screenshot = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    print(f"매칭 결과:")
    print(f"  신뢰도: {max_val:.3f}")
    print(f"  매칭 위치: {max_loc}")
    
    if max_val >= 0.5:
        template_h, template_w = gray_template.shape
        
        # 클릭 위치 계산
        game_x = max_loc[0] + template_w // 2
        game_y = max_loc[1] + template_h // 2
        screen_x = game_window.left + game_x
        screen_y = game_window.top + game_y
        
        print(f"클릭 위치:")
        print(f"  게임 내: ({game_x}, {game_y})")
        print(f"  화면: ({screen_x}, {screen_y})")
        
        # 디버그 이미지 생성
        debug_img = screenshot_cv.copy()
        
        # 매칭 영역 표시 (녹색 사각형)
        cv2.rectangle(debug_img, max_loc, 
                      (max_loc[0] + template_w, max_loc[1] + template_h), 
                      (0, 255, 0), 3)
        
        # 클릭 위치 표시 (빨간 원)
        cv2.circle(debug_img, (game_x, game_y), 10, (0, 0, 255), -1)
        
        # 좌표 텍스트
        cv2.putText(debug_img, f"({game_x}, {game_y})", 
                    (game_x + 15, game_y - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # 저장
        os.makedirs("screenshots", exist_ok=True)
        timestamp = time.strftime("%H%M%S")
        filename = f"screenshots/debug_click_{timestamp}.png"
        cv2.imwrite(filename, debug_img)
        
        print(f"디버그 이미지 저장: {filename}")
        print("녹색 사각형: 매칭된 영역")
        print("빨간 원: 클릭할 위치")
        
        # 실제 클릭 테스트 (3초 후)
        print("3초 후 실제 클릭을 실행합니다...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print(f"클릭 실행: ({screen_x}, {screen_y})")
        pyautogui.click(screen_x, screen_y)
        print("클릭 완료!")
        
    else:
        print("카페 버튼을 찾을 수 없습니다")
        # 현재 화면 저장
        timestamp = time.strftime("%H%M%S")
        filename = f"screenshots/no_match_{timestamp}.png"
        cv2.imwrite(filename, screenshot_cv)
        print(f"현재 화면 저장: {filename}")


if __name__ == "__main__":
    debug_click_position()