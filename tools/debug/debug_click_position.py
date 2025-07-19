"""
클릭 위치 디버깅 도구
"""
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
import os
from typing import Optional, Tuple


def find_game_window():
    """게임 윈도우 찾기"""
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


def capture_with_coordinates():
    """좌표 정보와 함께 캡처"""
    # 게임 윈도우 찾기
    window = find_game_window()
    if not window:
        print("게임 윈도우를 찾을 수 없습니다")
        return None
    
    print(f"게임 윈도우 정보:")
    print(f"  제목: {window.title}")
    print(f"  위치: ({window.left}, {window.top})")
    print(f"  크기: {window.width} x {window.height}")
    print(f"  활성화: {window.isActive}")
    
    # 윈도우 활성화
    if not window.isActive:
        print("게임 윈도우 활성화...")
        center_x = window.left + window.width // 2
        center_y = window.top + window.height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(2.0)
    
    # 게임 영역 캡처
    screenshot = pyautogui.screenshot(
        region=(window.left, window.top, window.width, window.height)
    )
    
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR), window


def find_cafe_button_with_debug(screenshot, window):
    """카페 버튼 찾기 (디버그 정보 포함)"""
    template_file = "assets/cafe_button.png"
    
    if not os.path.exists(template_file):
        print(f"템플릿 파일이 없습니다: {template_file}")
        return None
    
    # 템플릿 로드
    template = cv2.imread(template_file)
    if template is None:
        print(f"템플릿 로드 실패: {template_file}")
        return None
    
    print(f"템플릿 크기: {template.shape[1]} x {template.shape[0]}")
    
    # 그레이스케일 변환
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # 템플릿 매칭
    result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    print(f"매칭 결과:")
    print(f"  최대 신뢰도: {max_val:.3f}")
    print(f"  매칭 위치: {max_loc}")
    
    if max_val >= 0.6:
        template_h, template_w = gray_template.shape
        
        # 게임 윈도우 내 좌표
        game_x = max_loc[0] + template_w // 2
        game_y = max_loc[1] + template_h // 2
        
        # 화면 전체 좌표
        screen_x = window.left + game_x
        screen_y = window.top + game_y
        
        print(f"클릭 좌표:")
        print(f"  게임 내 좌표: ({game_x}, {game_y})")
        print(f"  화면 좌표: ({screen_x}, {screen_y})")
        
        return {
            'game_pos': (game_x, game_y),
            'screen_pos': (screen_x, screen_y),
            'confidence': max_val,
            'template_size': (template_w, template_h),
            'match_corner': max_loc
        }
    
    return None


def draw_debug_image(screenshot, result, window):
    """디버그 이미지 생성"""
    if result is None:
        return
    
    debug_img = screenshot.copy()
    game_x, game_y = result['game_pos']
    template_w, template_h = result['template_size']
    corner_x, corner_y = result['match_corner']
    
    # 매칭된 영역 표시 (녹색 사각형)
    cv2.rectangle(debug_img, 
                  (corner_x, corner_y), 
                  (corner_x + template_w, corner_y + template_h), 
                  (0, 255, 0), 3)
    
    # 클릭 위치 표시 (빨간 점)
    cv2.circle(debug_img, (game_x, game_y), 10, (0, 0, 255), -1)
    
    # 좌표 텍스트 표시
    cv2.putText(debug_img, f"Click: ({game_x}, {game_y})", 
                (game_x + 15, game_y - 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    cv2.putText(debug_img, f"Confidence: {result['confidence']:.3f}", 
                (corner_x, corner_y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # 이미지 저장
    timestamp = time.strftime("%H%M%S")
    filename = f"screenshots/debug_click_{timestamp}.png"
    cv2.imwrite(filename, debug_img)
    
    print(f"디버그 이미지 저장: {filename}")
    print("이미지에서 녹색 사각형(매칭 영역)과 빨간 점(클릭 위치)을 확인하세요!")


def test_click_accuracy():
    """클릭 정확도 테스트"""
    print("=" * 60)
    print("🎯 클릭 위치 정확도 디버깅")
    print("=" * 60)
    
    os.makedirs("screenshots", exist_ok=True)
    
    # 1. 화면 캡처
    screenshot, window = capture_with_coordinates()
    if screenshot is None:
        return
    
    # 2. 카페 버튼 찾기
    result = find_cafe_button_with_debug(screenshot, window)
    if result is None:
        print("❌ 카페 버튼을 찾을 수 없습니다")
        return
    
    # 3. 디버그 이미지 생성
    draw_debug_image(screenshot, result, window)
    
    # 4. 실제 클릭 테스트
    print(f"\n🖱️ 실제 클릭 테스트")
    print("클릭하시겠습니까? (y/n): ", end="")
    response = input().strip().lower()
    
    if response == 'y':
        screen_x, screen_y = result['screen_pos']
        print(f"화면 좌표 ({screen_x}, {screen_y})를 클릭합니다...")
        
        # 마우스 위치 확인
        current_x, current_y = pyautogui.position()
        print(f"현재 마우스 위치: ({current_x}, {current_y})")
        
        # 클릭 실행
        pyautogui.click(screen_x, screen_y)
        
        # 클릭 후 마우스 위치 확인
        new_x, new_y = pyautogui.position()
        print(f"클릭 후 마우스 위치: ({new_x}, {new_y})")
        
        print("✅ 클릭 완료!")
    
    print("\n📋 결과 요약:")
    print(f"게임 윈도우: {window.left}, {window.top}, {window.width}x{window.height}")
    print(f"매칭 신뢰도: {result['confidence']:.3f}")
    print(f"템플릿 크기: {result['template_size']}")
    print(f"게임 내 클릭 위치: {result['game_pos']}")
    print(f"화면 클릭 위치: {result['screen_pos']}")


def compare_multiple_methods():
    """여러 방법 비교"""
    print("=" * 60)
    print("🔍 여러 캡처 방법 비교")
    print("=" * 60)
    
    window = find_game_window()
    if not window:
        return
    
    # 방법 1: pyautogui region
    screenshot1 = pyautogui.screenshot(
        region=(window.left, window.top, window.width, window.height)
    )
    screenshot1_cv = cv2.cvtColor(np.array(screenshot1), cv2.COLOR_RGB2BGR)
    
    # 방법 2: 전체 스크린샷 후 크롭
    full_screenshot = pyautogui.screenshot()
    full_cv = cv2.cvtColor(np.array(full_screenshot), cv2.COLOR_RGB2BGR)
    screenshot2_cv = full_cv[window.top:window.top+window.height, 
                            window.left:window.left+window.width]
    
    # 각각 저장
    timestamp = time.strftime("%H%M%S")
    cv2.imwrite(f"screenshots/method1_region_{timestamp}.png", screenshot1_cv)
    cv2.imwrite(f"screenshots/method2_crop_{timestamp}.png", screenshot2_cv)
    cv2.imwrite(f"screenshots/full_screen_{timestamp}.png", full_cv)
    
    print("3가지 방법으로 캡처한 이미지를 저장했습니다:")
    print(f"- method1_region_{timestamp}.png (pyautogui region)")
    print(f"- method2_crop_{timestamp}.png (전체 스크린샷 후 크롭)")
    print(f"- full_screen_{timestamp}.png (전체 스크린샷)")


if __name__ == "__main__":
    print("클릭 위치 디버깅 도구")
    print("1. 정확도 테스트")
    print("2. 캡처 방법 비교")
    print("선택하세요 (1-2): ", end="")
    
    choice = input().strip()
    
    if choice == '1':
        test_click_accuracy()
    elif choice == '2':
        compare_multiple_methods()
    else:
        print("잘못된 선택입니다.")