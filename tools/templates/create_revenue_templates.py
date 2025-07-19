"""
카페 수익 버튼 및 수령 버튼 템플릿 생성 도구
"""
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
import os


def capture_current_screen():
    """현재 게임 화면 캡처"""
    all_windows = gw.getAllWindows()
    game_window = None
    
    for window in all_windows:
        if window.title and "Blue Archive" in window.title:
            if "Visual Studio" not in window.title and "Code" not in window.title:
                game_window = window
                break
    
    if not game_window:
        print("게임 윈도우를 찾을 수 없습니다")
        return None, None
    
    # 윈도우 활성화
    if not game_window.isActive:
        center_x = game_window.left + game_window.width // 2
        center_y = game_window.top + game_window.height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(2.0)
    
    # 게임 화면 캡처
    screenshot = pyautogui.screenshot(
        region=(game_window.left, game_window.top, game_window.width, game_window.height)
    )
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    return screenshot_cv, game_window


def create_revenue_button_template():
    """카페 수익 버튼 템플릿 생성"""
    print("=== 카페 수익 버튼 템플릿 생성 ===")
    print("1. 카페 화면으로 이동하세요")
    print("2. '카페 수익' 버튼이 보이는지 확인하세요")
    print("3. 5초 후 화면을 캡처합니다")
    
    for i in range(5, 0, -1):
        print(f"{i}초...")
        time.sleep(1)
    
    screenshot, window = capture_current_screen()
    if screenshot is None:
        return
    
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    
    timestamp = time.strftime("%H%M%S")
    filename = f"screenshots/cafe_revenue_screen_{timestamp}.png"
    cv2.imwrite(filename, screenshot)
    
    print(f"카페 화면 저장: {filename}")
    print()
    print("다음 단계:")
    print("1. 위 이미지를 열어보세요")
    print("2. '카페 수익' 버튼 부분만 잘라내세요")
    print("3. 잘라낸 이미지를 'assets/cafe_revenue_button.png'로 저장하세요")


def create_collect_button_template():
    """수령 버튼 템플릿 생성"""
    print("=== 수령 버튼 템플릿 생성 ===")
    print("1. 카페 수익 버튼을 클릭해서 팝업을 띄우세요")
    print("2. '수령' 버튼이 보이는지 확인하세요")
    print("3. 5초 후 화면을 캡처합니다")
    
    for i in range(5, 0, -1):
        print(f"{i}초...")
        time.sleep(1)
    
    screenshot, window = capture_current_screen()
    if screenshot is None:
        return
    
    os.makedirs("screenshots", exist_ok=True)
    
    timestamp = time.strftime("%H%M%S")
    filename = f"screenshots/collect_popup_screen_{timestamp}.png"
    cv2.imwrite(filename, screenshot)
    
    print(f"팝업 화면 저장: {filename}")
    print()
    print("다음 단계:")
    print("1. 위 이미지를 열어보세요")
    print("2. '수령' 버튼 부분만 잘라내세요")
    print("3. 잘라낸 이미지를 'assets/collect_button.png'로 저장하세요")


def test_revenue_template():
    """카페 수익 버튼 템플릿 테스트"""
    template_path = "assets/cafe_revenue_button.png"
    if not os.path.exists(template_path):
        print(f"템플릿 파일이 없습니다: {template_path}")
        return
    
    screenshot, window = capture_current_screen()
    if screenshot is None:
        return
    
    template = cv2.imread(template_path)
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    print(f"카페 수익 버튼 매칭 결과:")
    print(f"  신뢰도: {max_val:.3f}")
    print(f"  위치: {max_loc}")
    
    if max_val >= 0.6:
        print("템플릿 매칭 성공!")
        template_h, template_w = gray_template.shape
        
        # 디버그 이미지 생성
        debug_img = screenshot.copy()
        cv2.rectangle(debug_img, max_loc, 
                      (max_loc[0] + template_w, max_loc[1] + template_h), 
                      (0, 255, 0), 3)
        
        center_x = max_loc[0] + template_w // 2
        center_y = max_loc[1] + template_h // 2
        cv2.circle(debug_img, (center_x, center_y), 10, (0, 0, 255), -1)
        
        timestamp = time.strftime("%H%M%S")
        debug_file = f"screenshots/revenue_template_test_{timestamp}.png"
        cv2.imwrite(debug_file, debug_img)
        print(f"디버그 이미지: {debug_file}")
    else:
        print("템플릿 매칭 실패 - 템플릿을 다시 만들어보세요")


def test_collect_template():
    """수령 버튼 템플릿 테스트"""
    template_path = "assets/collect_button.png"
    if not os.path.exists(template_path):
        print(f"템플릿 파일이 없습니다: {template_path}")
        return
    
    screenshot, window = capture_current_screen()
    if screenshot is None:
        return
    
    template = cv2.imread(template_path)
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    print(f"수령 버튼 매칭 결과:")
    print(f"  신뢰도: {max_val:.3f}")
    print(f"  위치: {max_loc}")
    
    if max_val >= 0.6:
        print("템플릿 매칭 성공!")
        template_h, template_w = gray_template.shape
        
        # 디버그 이미지 생성
        debug_img = screenshot.copy()
        cv2.rectangle(debug_img, max_loc, 
                      (max_loc[0] + template_w, max_loc[1] + template_h), 
                      (0, 255, 0), 3)
        
        center_x = max_loc[0] + template_w // 2
        center_y = max_loc[1] + template_h // 2
        cv2.circle(debug_img, (center_x, center_y), 10, (0, 0, 255), -1)
        
        timestamp = time.strftime("%H%M%S")
        debug_file = f"screenshots/collect_template_test_{timestamp}.png"
        cv2.imwrite(debug_file, debug_img)
        print(f"디버그 이미지: {debug_file}")
    else:
        print("템플릿 매칭 실패 - 템플릿을 다시 만들어보세요")


if __name__ == "__main__":
    print("=== 카페 수익 템플릿 생성 도구 ===")
    print("1. 카페 수익 버튼 템플릿 생성")
    print("2. 수령 버튼 템플릿 생성")
    print("3. 카페 수익 버튼 템플릿 테스트")
    print("4. 수령 버튼 템플릿 테스트")
    
    choice = input("선택 (1-4): ").strip()
    
    if choice == "1":
        create_revenue_button_template()
    elif choice == "2":
        create_collect_button_template()
    elif choice == "3":
        test_revenue_template()
    elif choice == "4":
        test_collect_template()
    else:
        print("잘못된 선택입니다")