"""
게임 상태 감지 시스템
"""
import cv2
import numpy as np
import pyautogui
import time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from infrastructure.process.game_process_detector import GameProcessDetector
import pygetwindow as gw


class GameState(Enum):
    """게임 상태 열거형"""
    UNKNOWN = "unknown"
    LOADING = "loading"
    MAIN_MENU = "main_menu"
    IN_GAME = "in_game"
    CAFE = "cafe"
    BATTLE = "battle"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class StateDetectionResult:
    """상태 감지 결과"""
    state: GameState
    confidence: float
    detected_elements: List[str]
    screenshot_path: Optional[str] = None


class GameStateDetector(ABC):
    """게임 상태 감지 인터페이스"""
    
    @abstractmethod
    def detect_current_state(self) -> StateDetectionResult:
        """현재 게임 상태 감지"""
        pass
    
    @abstractmethod
    def wait_for_state(self, target_state: GameState, timeout: int = 30) -> bool:
        """특정 상태까지 대기"""
        pass


class BlueArchiveStateDetector(GameStateDetector):
    """블루아카이브 게임 상태 감지기"""
    
    def __init__(self):
        self.process_detector = GameProcessDetector()
        
        # 상태별 감지 패턴 (색상 기반)
        self.state_patterns = {
            GameState.LOADING: {
                "blue_ranges": [
                    ((100, 150, 0), (130, 255, 255)),  # 파란색 범위
                ],
                "white_ranges": [
                    ((0, 0, 200), (180, 30, 255)),     # 흰색 범위
                ],
                "required_percentage": 0.3  # 화면의 30% 이상 해당 색상
            },
            GameState.MAIN_MENU: {
                "ui_elements": ["buttons", "menu_items"],
                "color_variety": True,  # 다양한 색상이 있어야 함
                "required_percentage": 0.1
            },
            GameState.IN_GAME: {
                "ui_elements": ["health_bars", "buttons"],
                "color_variety": True,
                "required_percentage": 0.1
            }
        }
    
    def detect_current_state(self, save_screenshot: bool = False) -> StateDetectionResult:
        """현재 게임 상태 감지"""
        # 프로세스 확인
        if not self.process_detector.is_game_running():
            return StateDetectionResult(
                state=GameState.UNKNOWN,
                confidence=0.0,
                detected_elements=["no_process"]
            )
        
        # 윈도우 확인 및 활성화
        window = self._find_and_activate_game()
        if not window:
            return StateDetectionResult(
                state=GameState.UNKNOWN,
                confidence=0.0,
                detected_elements=["no_window"]
            )
        
        # 화면 캡처 및 분석
        try:
            screenshot = self._capture_screen()
            if screenshot is None:
                return StateDetectionResult(
                    state=GameState.UNKNOWN,
                    confidence=0.0,
                    detected_elements=["capture_failed"]
                )
            
            screenshot_path = None
            if save_screenshot:
                screenshot_path = self._save_screenshot(screenshot)
            
            # 각 상태별로 확인
            detection_results = []
            
            # 로딩 화면 확인
            loading_confidence = self._detect_loading_screen(screenshot)
            if loading_confidence > 0.7:
                detection_results.append((GameState.LOADING, loading_confidence))
            
            # 메인 메뉴 확인
            menu_confidence = self._detect_main_menu(screenshot)
            if menu_confidence > 0.5:
                detection_results.append((GameState.MAIN_MENU, menu_confidence))
            
            # 인게임 확인
            ingame_confidence = self._detect_in_game(screenshot)
            if ingame_confidence > 0.5:
                detection_results.append((GameState.IN_GAME, ingame_confidence))
            
            # 가장 높은 신뢰도의 상태 반환
            if detection_results:
                best_state, best_confidence = max(detection_results, key=lambda x: x[1])
                return StateDetectionResult(
                    state=best_state,
                    confidence=best_confidence,
                    detected_elements=[f"{best_state.value}_elements"],
                    screenshot_path=screenshot_path
                )
            else:
                return StateDetectionResult(
                    state=GameState.UNKNOWN,
                    confidence=0.0,
                    detected_elements=["no_match"],
                    screenshot_path=screenshot_path
                )
                
        except Exception as e:
            print(f"상태 감지 중 오류 발생: {e}")
            return StateDetectionResult(
                state=GameState.UNKNOWN,
                confidence=0.0,
                detected_elements=["error", str(e)]
            )
    
    def wait_for_state(self, target_state: GameState, timeout: int = 30) -> bool:
        """특정 상태까지 대기"""
        start_time = time.time()
        
        print(f"{target_state.value} 상태까지 대기 중... (최대 {timeout}초)")
        
        while time.time() - start_time < timeout:
            current_state = self.detect_current_state()
            
            if current_state.state == target_state:
                print(f"{target_state.value} 상태 감지 완료! (신뢰도: {current_state.confidence:.2f})")
                return True
            
            print(f"현재 상태: {current_state.state.value} (신뢰도: {current_state.confidence:.2f})")
            time.sleep(2)
        
        print(f"{timeout}초 동안 {target_state.value} 상태가 감지되지 않았습니다.")
        return False
    
    def get_detailed_analysis(self) -> Dict[str, any]:
        """상세한 게임 상태 분석"""
        result = self.detect_current_state()
        
        # 프로세스 정보
        process_info = self.process_detector.get_process_details()
        
        return {
            "game_state": {
                "current_state": result.state.value,
                "confidence": result.confidence,
                "detected_elements": result.detected_elements
            },
            "process_info": process_info,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _find_and_activate_game(self):
        """게임 찾기 및 활성화"""
        try:
            # 블루아카이브 윈도우 찾기
            all_windows = gw.getAllWindows()
            game_window = None
            
            for window in all_windows:
                if window.title and "Blue Archive" in window.title:
                    if "Visual Studio" not in window.title and "Code" not in window.title:
                        game_window = window
                        break
            
            if not game_window:
                print("게임 윈도우를 찾을 수 없습니다")
                return None
            
            print(f"게임 윈도우 발견: {game_window.title}")
            
            # 게임이 비활성화되어 있으면 클릭해서 활성화
            if not game_window.isActive:
                print("게임 윈도우 클릭해서 활성화...")
                center_x = game_window.left + game_window.width // 2
                center_y = game_window.top + game_window.height // 2
                
                pyautogui.click(center_x, center_y)
                time.sleep(2.0)  # 활성화 대기
                print("게임 활성화 완료")
            else:
                print("게임이 이미 활성화되어 있습니다")
            
            return game_window
            
        except Exception as e:
            print(f"게임 찾기/활성화 오류: {e}")
            return None
    
    def _capture_screen(self) -> Optional[np.ndarray]:
        """게임 윈도우 영역만 캡처"""
        try:
            # 게임 윈도우 다시 찾기 (최신 정보)
            all_windows = gw.getAllWindows()
            game_window = None
            
            for window in all_windows:
                if window.title and "Blue Archive" in window.title:
                    if "Visual Studio" not in window.title and "Code" not in window.title:
                        game_window = window
                        break
            
            if not game_window:
                print("게임 윈도우를 찾을 수 없어 전체 화면 캡처...")
                screenshot = pyautogui.screenshot()
                return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            print(f"게임 윈도우 영역 캡처: ({game_window.left}, {game_window.top}, {game_window.width}, {game_window.height})")
            
            # 게임 윈도우 영역만 캡처
            screenshot = pyautogui.screenshot(
                region=(game_window.left, game_window.top, game_window.width, game_window.height)
            )
            
            print("게임 윈도우 영역 캡처 완료!")
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
        except Exception as e:
            print(f"게임 윈도우 캡처 오류: {e}")
            print("전체 화면 캡처로 대체...")
            try:
                screenshot = pyautogui.screenshot()
                return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            except Exception as fallback_error:
                print(f"전체 화면 캡처도 실패: {fallback_error}")
                return None
    
    def _detect_loading_screen(self, screenshot: np.ndarray) -> float:
        """로딩 화면 감지 (파란색/흰색 위주)"""
        try:
            # HSV로 변환
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            
            # 파란색 영역 검출
            blue_mask1 = cv2.inRange(hsv, (100, 50, 50), (130, 255, 255))
            blue_mask2 = cv2.inRange(hsv, (110, 100, 100), (130, 255, 255))
            blue_mask = cv2.bitwise_or(blue_mask1, blue_mask2)
            
            # 흰색 영역 검출
            white_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
            
            # 전체 픽셀 수
            total_pixels = screenshot.shape[0] * screenshot.shape[1]
            
            # 파란색과 흰색 픽셀 비율
            blue_ratio = cv2.countNonZero(blue_mask) / total_pixels
            white_ratio = cv2.countNonZero(white_mask) / total_pixels
            
            # 로딩 화면은 주로 파란색과 흰색
            loading_confidence = (blue_ratio * 2 + white_ratio) / 3
            
            return min(loading_confidence * 2, 1.0)  # 최대 1.0으로 제한
            
        except Exception as e:
            print(f"로딩 화면 감지 오류: {e}")
            return 0.0
    
    def _detect_main_menu(self, screenshot: np.ndarray) -> float:
        """메인 메뉴 감지 (UI 요소 많음)"""
        try:
            # 그레이스케일로 변환
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # 가장자리 검출 (UI 요소들)
            edges = cv2.Canny(gray, 50, 150)
            
            # 윤곽선 검출
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 적당한 크기의 사각형 윤곽선 개수 (버튼들)
            button_like_contours = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 < area < 50000:  # 버튼 크기 범위
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 4:  # 버튼 비율
                        button_like_contours += 1
            
            # 색상 다양성 검사
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            color_variety = np.count_nonzero(hist) / 180
            
            # 메인 메뉴 신뢰도 계산
            button_score = min(button_like_contours / 10, 1.0)  # 10개 이상이면 1.0
            variety_score = min(color_variety * 2, 1.0)
            
            return (button_score + variety_score) / 2
            
        except Exception as e:
            print(f"메인 메뉴 감지 오류: {e}")
            return 0.0
    
    def _detect_in_game(self, screenshot: np.ndarray) -> float:
        """인게임 감지 (게임 플레이 화면)"""
        try:
            # 화면 하단의 UI 영역 확인
            height, width = screenshot.shape[:2]
            bottom_ui = screenshot[int(height * 0.8):, :]  # 하단 20%
            
            # 그레이스케일 변환
            gray_ui = cv2.cvtColor(bottom_ui, cv2.COLOR_BGR2GRAY)
            
            # UI 요소 감지
            edges = cv2.Canny(gray_ui, 30, 100)
            ui_density = cv2.countNonZero(edges) / (bottom_ui.shape[0] * bottom_ui.shape[1])
            
            # 전체 화면의 색상 복잡성
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            
            # 채도가 높은 영역 (게임 그래픽)
            saturation = hsv[:, :, 1]
            high_sat_ratio = np.count_nonzero(saturation > 100) / (height * width)
            
            # 인게임 신뢰도 계산
            ui_score = min(ui_density * 5, 1.0)
            graphics_score = min(high_sat_ratio * 3, 1.0)
            
            return (ui_score + graphics_score) / 2
            
        except Exception as e:
            print(f"인게임 감지 오류: {e}")
            return 0.0
    
    def _save_screenshot(self, screenshot: np.ndarray) -> str:
        """스크린샷 저장"""
        import os
        
        # screenshots 폴더 생성
        os.makedirs("screenshots", exist_ok=True)
        
        # 파일명 생성 (타임스탬프)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/game_state_{timestamp}.png"
        
        # 이미지 저장
        cv2.imwrite(filename, screenshot)
        print(f"스크린샷 저장: {filename}")
        
        return filename


def create_state_detector() -> BlueArchiveStateDetector:
    """게임 상태 감지기 팩토리 함수"""
    return BlueArchiveStateDetector()


if __name__ == "__main__":
    # 테스트용 실행
    detector = create_state_detector()
    
    print("=== 블루아카이브 게임 상태 감지 테스트 ===")
    
    # 현재 상태 감지 (스크린샷 저장)
    result = detector.detect_current_state(save_screenshot=True)
    print(f"현재 게임 상태: {result.state.value}")
    print(f"신뢰도: {result.confidence:.2f}")
    print(f"감지된 요소: {result.detected_elements}")
    if result.screenshot_path:
        print(f"스크린샷: {result.screenshot_path}")
    
    # 메인 메뉴 감지 상세 정보
    if result.state == GameState.MAIN_MENU:
        print(f"\n=== 메인 메뉴 감지 상세 정보 ===")
        print("감지 방식: UI 요소(버튼) 개수 + 색상 다양성")
        print("- Canny 엣지 검출로 버튼 모양의 윤곽선 찾기")
        print("- 1000~50000 픽셀 크기의 사각형 윤곽선 개수 측정")  
        print("- HSV 히스토그램으로 색상 다양성 계산")
        print("- 두 점수의 평균으로 메인 메뉴 신뢰도 결정")
    
    # 상세 분석
    analysis = detector.get_detailed_analysis()
    print(f"\n=== 상세 분석 ===")
    print(f"프로세스 실행 중: {analysis['process_info']['running']}")
    print(f"분석 시간: {analysis['timestamp']}")