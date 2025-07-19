"""
카페 수익 버튼 감지 및 팝업 처리
"""
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
import os


class CafeRevenueDetector:
    def __init__(self):
        self.revenue_button_template = "assets/cafe_revenue_button.png"
        self.collect_button_template = "assets/collect_button.png"
        self.confidence_threshold = 0.4
        
    def _find_game_window(self):
        """게임 윈도우 찾기"""
        all_windows = gw.getAllWindows()
        for window in all_windows:
            if window.title and "Blue Archive" in window.title:
                if "Visual Studio" not in window.title and "Code" not in window.title:
                    return window
        return None
    
    def _capture_game_screen(self):
        """게임 화면 캡처"""
        game_window = self._find_game_window()
        if not game_window:
            return None, None
            
        # 윈도우 활성화
        if not game_window.isActive:
            center_x = game_window.left + game_window.width // 2
            center_y = game_window.top + game_window.height // 2
            pyautogui.click(center_x, center_y)
            time.sleep(1.0)
        
        screenshot = pyautogui.screenshot(
            region=(game_window.left, game_window.top, game_window.width, game_window.height)
        )
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        return screenshot_cv, game_window
    
    def find_revenue_button(self):
        """카페 수익 버튼 찾기"""
        screenshot, window = self._capture_game_screen()
        if screenshot is None:
            return None
            
        if not os.path.exists(self.revenue_button_template):
            print(f"수익 버튼 템플릿이 없습니다: {self.revenue_button_template}")
            return None
            
        template = cv2.imread(self.revenue_button_template)
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= self.confidence_threshold:
            template_h, template_w = gray_template.shape
            center_x = max_loc[0] + template_w // 2
            center_y = max_loc[1] + template_h // 2
            screen_x = window.left + center_x
            screen_y = window.top + center_y
            
            return {
                'confidence': max_val,
                'position': (center_x, center_y),
                'screen_position': (screen_x, screen_y),
                'window': window
            }
        
        return None
    
    def click_revenue_button(self):
        """카페 수익 버튼 클릭"""
        button_info = self.find_revenue_button()
        if not button_info:
            print("카페 수익 버튼을 찾을 수 없습니다")
            return False
            
        screen_x, screen_y = button_info['screen_position']
        print(f"카페 수익 버튼 클릭: ({screen_x}, {screen_y})")
        
        pyautogui.click(screen_x, screen_y)
        time.sleep(2.0)  # 팝업이 뜰 시간 대기
        
        return True
    
    def find_collect_button(self):
        """수령 버튼 찾기 (팝업창에서)"""
        screenshot, window = self._capture_game_screen()
        if screenshot is None:
            return None
            
        if not os.path.exists(self.collect_button_template):
            print(f"수령 버튼 템플릿이 없습니다: {self.collect_button_template}")
            return None
            
        template = cv2.imread(self.collect_button_template)
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= self.confidence_threshold:
            template_h, template_w = gray_template.shape
            center_x = max_loc[0] + template_w // 2
            center_y = max_loc[1] + template_h // 2
            screen_x = window.left + center_x
            screen_y = window.top + center_y
            
            return {
                'confidence': max_val,
                'position': (center_x, center_y),
                'screen_position': (screen_x, screen_y),
                'window': window
            }
        
        return None
    
    def click_collect_button(self):
        """수령 버튼 클릭"""
        button_info = self.find_collect_button()
        if not button_info:
            print("수령 버튼을 찾을 수 없습니다")
            return False
            
        screen_x, screen_y = button_info['screen_position']
        print(f"수령 버튼 클릭: ({screen_x}, {screen_y})")
        
        pyautogui.click(screen_x, screen_y)
        time.sleep(1.5)  # 수령 후 대기
        
        return True
    
    def collect_cafe_revenue(self):
        """카페 수익 수령 전체 프로세스"""
        print("=== 카페 수익 수령 시작 ===")
        
        # 1. 카페 수익 버튼 클릭
        if not self.click_revenue_button():
            return False
            
        # 2. 수령 버튼 클릭 (팝업에서)
        if not self.click_collect_button():
            return False
            
        print("카페 수익 수령 완료!")
        return True
    
    def save_debug_screenshot(self, prefix="cafe_revenue_debug"):
        """디버그용 스크린샷 저장"""
        screenshot, window = self._capture_game_screen()
        if screenshot is None:
            return None
            
        os.makedirs("screenshots", exist_ok=True)
        timestamp = time.strftime("%H%M%S")
        filename = f"screenshots/{prefix}_{timestamp}.png"
        cv2.imwrite(filename, screenshot)
        
        print(f"디버그 스크린샷 저장: {filename}")
        return filename


if __name__ == "__main__":
    detector = CafeRevenueDetector()
    
    print("1. 현재 화면 저장")
    print("2. 카페 수익 버튼 찾기")
    print("3. 수령 버튼 찾기")
    print("4. 전체 수익 수령 실행")
    
    choice = input("선택 (1-4): ").strip()
    
    if choice == "1":
        detector.save_debug_screenshot()
    elif choice == "2":
        result = detector.find_revenue_button()
        if result:
            print(f"카페 수익 버튼 발견 - 신뢰도: {result['confidence']:.3f}")
        else:
            print("카페 수익 버튼을 찾을 수 없습니다")
    elif choice == "3":
        result = detector.find_collect_button()
        if result:
            print(f"수령 버튼 발견 - 신뢰도: {result['confidence']:.3f}")
        else:
            print("수령 버튼을 찾을 수 없습니다")
    elif choice == "4":
        detector.collect_cafe_revenue()