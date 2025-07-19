"""
수동 템플릿 생성 도구
현재 게임 화면에서 카페 버튼 영역을 직접 지정
"""
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
import os


def capture_current_screen():
    """현재 게임 화면 캡처"""
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


def create_template_interactive():
    """대화형 템플릿 생성"""
    print("=== 카페 버튼 템플릿 생성 ===")
    print("1. 게임에서 카페 아이콘이 보이는 화면으로 이동하세요")
    print("2. 5초 후 화면을 캡처합니다")
    
    for i in range(5, 0, -1):
        print(f"{i}초...")
        time.sleep(1)
    
    # 화면 캡처
    screenshot, window = capture_current_screen()
    if screenshot is None:
        return
    
    # 현재 화면 저장
    os.makedirs("screenshots", exist_ok=True)
    timestamp = time.strftime("%H%M%S")
    current_file = f"screenshots/current_for_template_{timestamp}.png"
    cv2.imwrite(current_file, screenshot)
    
    print(f"현재 화면 저장: {current_file}")
    print()
    print("다음 단계:")
    print("1. 위 이미지를 열어보세요")
    print("2. 카페 아이콘 부분만 잘라내세요 (약 50x50 ~ 100x100 픽셀)")
    print("3. 잘라낸 이미지를 'assets/cafe_button_new.png'로 저장하세요")
    print("4. 아래 함수를 실행해서 테스트하세요")


def test_new_template():
    """새 템플릿 테스트"""
    print("=== 새 템플릿 테스트 ===")
    
    # 새 템플릿 파일 확인
    new_template = "assets/cafe_button_new.png"
    if not os.path.exists(new_template):
        print(f"새 템플릿 파일이 없습니다: {new_template}")
        print("먼저 create_template_interactive()를 실행하고 템플릿을 만드세요")
        return
    
    # 게임 화면 캡처
    screenshot, window = capture_current_screen()
    if screenshot is None:
        return
    
    # 새 템플릿으로 매칭
    template = cv2.imread(new_template)
    print(f"새 템플릿 크기: {template.shape[1]} x {template.shape[0]}")
    
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    print(f"매칭 결과:")
    print(f"  신뢰도: {max_val:.3f}")
    print(f"  매칭 위치: {max_loc}")
    
    if max_val >= 0.7:  # 높은 임계값 사용
        template_h, template_w = gray_template.shape
        
        # 클릭 위치 계산
        game_x = max_loc[0] + template_w // 2
        game_y = max_loc[1] + template_h // 2
        screen_x = window.left + game_x
        screen_y = window.top + game_y
        
        print(f"클릭 위치:")
        print(f"  게임 내: ({game_x}, {game_y})")
        print(f"  화면: ({screen_x}, {screen_y})")
        
        # 디버그 이미지 생성
        debug_img = screenshot.copy()
        cv2.rectangle(debug_img, max_loc, 
                      (max_loc[0] + template_w, max_loc[1] + template_h), 
                      (0, 255, 0), 3)
        cv2.circle(debug_img, (game_x, game_y), 10, (0, 0, 255), -1)
        cv2.putText(debug_img, f"({game_x}, {game_y})", 
                    (game_x + 15, game_y - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        timestamp = time.strftime("%H%M%S")
        debug_file = f"screenshots/new_template_test_{timestamp}.png"
        cv2.imwrite(debug_file, debug_img)
        print(f"디버그 이미지: {debug_file}")
        
        # 클릭 테스트
        print("새 템플릿으로 클릭 테스트를 하시겠습니까? (y/n): ", end="")
        try:
            response = input().strip().lower()
            if response == 'y':
                print("3초 후 클릭...")
                for i in range(3, 0, -1):
                    print(f"{i}...")
                    time.sleep(1)
                
                pyautogui.click(screen_x, screen_y)
                print("클릭 완료!")
                
                # 성공하면 원본 파일 교체
                print("새 템플릿이 잘 작동하나요? (y/n): ", end="")
                response2 = input().strip().lower()
                if response2 == 'y':
                    import shutil
                    shutil.copy(new_template, "assets/cafe_button.png")
                    print("새 템플릿을 cafe_button.png로 교체했습니다!")
        except:
            print("입력 건너뛰기")
        
    else:
        print("새 템플릿도 매칭되지 않습니다")
        print("템플릿 이미지를 다시 만들어보세요")


def quick_test():
    """빠른 테스트"""
    print("=== 빠른 카페 버튼 위치 확인 ===")
    
    # 현재 화면 캡처 및 저장
    screenshot, window = capture_current_screen()
    if screenshot is None:
        return
    
    timestamp = time.strftime("%H%M%S")
    filename = f"screenshots/quick_check_{timestamp}.png"
    cv2.imwrite(filename, screenshot)
    
    print(f"현재 게임 화면 저장: {filename}")
    print("이 이미지를 확인하고 카페 아이콘의 대략적인 위치를 파악하세요")
    
    # 화면 크기 정보
    print(f"게임 화면 크기: {screenshot.shape[1]} x {screenshot.shape[0]}")
    print("카페 아이콘이 보이는 위치를 확인하고 좌표를 알려주세요")


if __name__ == "__main__":
    print("템플릿 생성 도구")
    print("1. 현재 화면 빠른 확인")
    print("2. 새 템플릿 생성")
    print("3. 새 템플릿 테스트")
    
    # 자동으로 빠른 확인 실행
    quick_test()