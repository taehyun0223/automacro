"""
학생 호감도 감지 및 상호작용 처리
"""
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
import os
from typing import List, Optional, Tuple

from domain.models.student_affinity import (
    StudentPosition, AffinityResult, AffinityInteractionResult, 
    CafeAffinityArea
)


class StudentAffinityDetector:
    """학생 호감도 감지 및 처리"""
    
    def __init__(self):
        self.affinity_indicator_template = "assets/affinity_indicator.png"
        self.rank_up_template = "assets/rank_up_popup.png"
        self.confidence_threshold = 0.6
        self.max_students = 5
        
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
    
    def find_students_with_indicators(self) -> List[StudentPosition]:
        """호감도 표식이 있는 학생들 찾기"""
        screenshot, window = self._capture_game_screen()
        if screenshot is None:
            return []
            
        if not os.path.exists(self.affinity_indicator_template):
            print(f"호감도 표식 템플릿이 없습니다: {self.affinity_indicator_template}")
            return []
        
        students = []
        template = cv2.imread(self.affinity_indicator_template)
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # 템플릿 매칭
        result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
        
        # 여러 개의 매칭 결과 찾기
        locations = np.where(result >= self.confidence_threshold)
        template_h, template_w = gray_template.shape
        
        # 중복 제거를 위한 Non-Maximum Suppression
        matches = []
        for pt in zip(*locations[::-1]):
            matches.append([pt[0], pt[1], result[pt[1], pt[0]]])
        
        # 신뢰도 순으로 정렬
        matches = sorted(matches, key=lambda x: x[2], reverse=True)
        
        # 중복 제거 및 학생 위치 생성
        used_positions = []
        for match in matches:
            x, y, confidence = match
            
            # 너무 가까운 위치는 제외 (중복 방지)
            too_close = False
            for used_x, used_y in used_positions:
                if abs(x - used_x) < 50 and abs(y - used_y) < 50:
                    too_close = True
                    break
            
            if not too_close and len(students) < self.max_students:
                # 학생 클릭 위치는 표식 아래쪽 (학생 몸체 부분)
                student_x = x + template_w // 2
                student_y = y + template_h + 30  # 표식 아래 30픽셀 정도
                
                student_pos = StudentPosition(
                    x=student_x,
                    y=student_y,
                    confidence=confidence,
                    has_indicator=True
                )
                students.append(student_pos)
                used_positions.append((x, y))
        
        print(f"호감도 표식이 있는 학생 {len(students)}명 발견")
        return students
    
    def click_student(self, student: StudentPosition, window) -> bool:
        """학생 클릭"""
        screen_x = window.left + student.x
        screen_y = window.top + student.y
        
        print(f"학생 클릭: ({screen_x}, {screen_y})")
        pyautogui.click(screen_x, screen_y)
        time.sleep(1.5)  # 반응 대기
        
        return True
    
    def detect_affinity_result(self) -> AffinityResult:
        """호감도 증가 결과 감지"""
        screenshot, window = self._capture_game_screen()
        if screenshot is None:
            return AffinityResult.ERROR
        
        # 인연 랭크 업 팝업 확인
        if os.path.exists(self.rank_up_template):
            template = cv2.imread(self.rank_up_template)
            gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= self.confidence_threshold:
                print("인연 랭크 업 감지!")
                return AffinityResult.RANK_UP
        
        # 하트 표시 감지 (색상 기반)
        # 분홍색/빨간색 하트가 나타나는지 확인
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # 분홍색/빨간색 범위 (하트 색상)
        lower_pink = np.array([150, 50, 50])
        upper_pink = np.array([180, 255, 255])
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask_pink = cv2.inRange(hsv, lower_pink, upper_pink)
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask_pink + mask_red1 + mask_red2
        
        # 하트 모양의 픽셀이 일정 수 이상이면 호감도 증가로 판단
        heart_pixels = cv2.countNonZero(mask)
        if heart_pixels > 100:  # 임계값은 조정 가능
            print("호감도 증가 감지 (하트 표시)")
            return AffinityResult.NORMAL_INCREASE
        
        # 변화가 없는 경우
        return AffinityResult.NO_CHANGE
    
    def handle_rank_up_popup(self, window) -> bool:
        """인연 랭크 업 팝업 처리"""
        print("인연 랭크 업 팝업 처리 중...")
        
        # 화면 중앙 클릭
        center_x = window.left + window.width // 2
        center_y = window.top + window.height // 2
        screen_center_x = center_x
        screen_center_y = center_y
        
        print(f"화면 중앙 클릭: ({screen_center_x}, {screen_center_y})")
        pyautogui.click(screen_center_x, screen_center_y)
        time.sleep(2.0)  # 카페 화면 복귀 대기
        
        return True
    
    def interact_with_student(self, student: StudentPosition) -> AffinityInteractionResult:
        """학생과 호감도 상호작용"""
        window = self._find_game_window()
        if not window:
            return AffinityInteractionResult(
                student_position=student,
                result=AffinityResult.ERROR,
                message="게임 윈도우를 찾을 수 없음",
                interaction_time=0.0
            )
        
        start_time = time.time()
        
        # 1. 학생 클릭
        if not self.click_student(student, window):
            return AffinityInteractionResult(
                student_position=student,
                result=AffinityResult.ERROR,
                message="학생 클릭 실패",
                interaction_time=time.time() - start_time
            )
        
        # 2. 결과 확인
        affinity_result = self.detect_affinity_result()
        
        # 3. 랭크 업 팝업 처리
        if affinity_result == AffinityResult.RANK_UP:
            self.handle_rank_up_popup(window)
            message = "인연 랭크 업! 팝업 처리 완료"
        elif affinity_result == AffinityResult.NORMAL_INCREASE:
            message = "호감도 증가"
            time.sleep(1.0)  # 하트 애니메이션 대기
        elif affinity_result == AffinityResult.NO_CHANGE:
            message = "호감도 변화 없음"
        else:
            message = "결과 감지 실패"
        
        interaction_time = time.time() - start_time
        
        return AffinityInteractionResult(
            student_position=student,
            result=affinity_result,
            message=message,
            interaction_time=interaction_time
        )
    
    def process_all_students(self) -> List[AffinityInteractionResult]:
        """모든 호감도 표식이 있는 학생들과 상호작용"""
        print("=== 학생 호감도 상호작용 시작 ===")
        
        # 1. 호감도 표식이 있는 학생들 찾기
        students = self.find_students_with_indicators()
        
        if not students:
            print("호감도 표식이 있는 학생을 찾을 수 없습니다")
            return []
        
        results = []
        
        # 2. 각 학생과 상호작용
        for i, student in enumerate(students, 1):
            print(f"\n학생 {i}/{len(students)} 상호작용 중...")
            result = self.interact_with_student(student)
            results.append(result)
            
            print(f"결과: {result.message} (소요시간: {result.interaction_time:.1f}초)")
            
            # 다음 학생과의 간격
            if i < len(students):
                time.sleep(1.0)
        
        print(f"\n=== 학생 호감도 상호작용 완료 ({len(results)}명) ===")
        return results
    
    def save_debug_screenshot(self, prefix="student_affinity_debug"):
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
    detector = StudentAffinityDetector()
    
    print("학생 호감도 감지 시스템 테스트")
    print("1. 현재 화면 저장")
    print("2. 호감도 표식 학생 찾기")
    print("3. 모든 학생과 상호작용")
    
    choice = input("선택 (1-3): ").strip()
    
    if choice == "1":
        detector.save_debug_screenshot()
    elif choice == "2":
        students = detector.find_students_with_indicators()
        for i, student in enumerate(students, 1):
            print(f"학생 {i}: 위치=({student.x}, {student.y}), 신뢰도={student.confidence:.3f}")
    elif choice == "3":
        detector.process_all_students()