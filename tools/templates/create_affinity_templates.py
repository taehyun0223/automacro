"""
학생 호감도 템플릿 생성 도구
호감도 표식 및 인연 랭크 업 팝업 템플릿 생성
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


def create_affinity_indicator_template():
    """호감도 표식 템플릿 생성"""
    print("=== 호감도 표식 템플릿 생성 ===")
    print("1. 카페 화면으로 이동하세요")
    print("2. 학생 위에 호감도 표식(하트, 말풍선 등)이 보이는지 확인하세요")
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
    filename = f"screenshots/affinity_indicator_screen_{timestamp}.png"
    cv2.imwrite(filename, screenshot)
    
    print(f"카페 화면 저장: {filename}")
    print()
    print("다음 단계:")
    print("1. 위 이미지를 열어보세요")
    print("2. 학생 위의 호감도 표식 부분만 잘라내세요")
    print("   - 하트 모양 표식")
    print("   - 말풍선 표식") 
    print("   - 느낌표 표식 등")
    print("3. 잘라낸 이미지를 'assets/affinity_indicator.png'로 저장하세요")
    print("   (크기: 약 30x30 ~ 50x50 픽셀 권장)")


def create_rank_up_template():
    """인연 랭크 업 팝업 템플릿 생성"""
    print("=== 인연 랭크 업 팝업 템플릿 생성 ===")
    print("1. 학생과 상호작용해서 인연 랭크 업을 발생시키세요")
    print("2. '인연 랭크 업!' 팝업이 나타나면 준비완료")
    print("3. 5초 후 화면을 캡처합니다")
    
    for i in range(5, 0, -1):
        print(f"{i}초...")
        time.sleep(1)
    
    screenshot, window = capture_current_screen()
    if screenshot is None:
        return
    
    os.makedirs("screenshots", exist_ok=True)
    
    timestamp = time.strftime("%H%M%S")
    filename = f"screenshots/rank_up_popup_screen_{timestamp}.png"
    cv2.imwrite(filename, screenshot)
    
    print(f"랭크 업 팝업 화면 저장: {filename}")
    print()
    print("다음 단계:")
    print("1. 위 이미지를 열어보세요")
    print("2. '인연 랭크 업!' 텍스트 부분만 잘라내세요")
    print("3. 잘라낸 이미지를 'assets/rank_up_popup.png'로 저장하세요")
    print("   (텍스트가 명확하게 보이도록 적당한 크기로 자르세요)")


def test_affinity_indicator_template():
    """호감도 표식 템플릿 테스트 (ROI + 히스토그램 평활화 적용)"""
    import os, time
    import cv2
    import numpy as np

    template_path = "assets/affinity_indicator.png"
    if not os.path.exists(template_path):
        print(f"템플릿 파일이 없습니다: {template_path}")
        return

    screenshot, window = capture_current_screen()
    if screenshot is None:
        print("스크린샷을 가져올 수 없습니다.")
        return

    # 원본→그레이스케일
    gray_full     = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(cv2.imread(template_path), cv2.COLOR_BGR2GRAY)
    template_h, template_w = gray_template.shape

    # 1) ROI로 관심 영역만 잘라내기 (예: 상단 우측 10%~50% 높이, 40%~100% 너비)
    h, w = gray_full.shape
    y1, y2 = int(h * 0.1), int(h * 0.5)
    x1, x2 = int(w * 0.4), w
    gray_roi = gray_full[y1:y2, x1:x2]

    # 2) 히스토그램 평활화
    gray_roi      = cv2.equalizeHist(gray_roi)
    gray_template = cv2.equalizeHist(gray_template)

    # 3) 템플릿 매칭 & 임계값
    threshold = 0.4
    result    = cv2.matchTemplate(gray_roi, gray_template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    matches = [(x, y, result[y, x]) for x, y in zip(*locations[::-1])]
    print(f"호감도 표식 매칭 결과: {len(matches)}개 발견")

    if not matches:
        print("템플릿 매칭 실패 - 템플릿을 다시 만들어보세요")
        return

    # 4) 디버그 이미지에 박스 표시 (ROI→전체 좌표 보정)
    debug_img = screenshot.copy()
    for i, (x, y, conf) in enumerate(matches, start=1):
        fx, fy = x + x1, y + y1
        cv2.rectangle(
            debug_img,
            (fx, fy),
            (fx + template_w, fy + template_h),
            (0, 255, 0), 2
        )
        cv2.putText(
            debug_img,
            f"{conf:.2f}",
            (fx, fy - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 255, 0), 1
        )
        print(f"  매칭 {i}: 위치=({fx}, {fy}), 신뢰도={conf:.3f}")

    # 5) 파일 저장
    os.makedirs("screenshots", exist_ok=True)
    timestamp = time.strftime("%H%M%S")
    debug_file = f"screenshots/affinity_indicator_test_{timestamp}.png"
    cv2.imwrite(debug_file, debug_img)
    print(f"디버그 이미지 저장: {debug_file}")



def test_rank_up_template():
    """인연 랭크 업 템플릿 테스트"""
    template_path = "assets/rank_up_popup.png"
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
    
    print(f"인연 랭크 업 팝업 매칭 결과:")
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
        
        timestamp = time.strftime("%H%M%S")
        debug_file = f"screenshots/rank_up_template_test_{timestamp}.png"
        cv2.imwrite(debug_file, debug_img)
        print(f"디버그 이미지: {debug_file}")
    else:
        print("템플릿 매칭 실패 - 템플릿을 다시 만들어보세요")


def detect_heart_animation():
    """하트 애니메이션 감지 테스트 (색상 기반)"""
    print("=== 하트 애니메이션 감지 테스트 ===")
    print("학생을 클릭한 직후 이 함수를 실행하세요")
    
    screenshot, window = capture_current_screen()
    if screenshot is None:
        return
    
    # HSV 색공간으로 변환
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
    
    heart_pixels = cv2.countNonZero(mask)
    print(f"하트 색상 픽셀 수: {heart_pixels}")
    
    if heart_pixels > 100:
        print("하트 애니메이션 감지됨!")
        
        # 하트 영역 표시
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        debug_img = screenshot.copy()
        cv2.drawContours(debug_img, contours, -1, (0, 255, 0), 2)
        
        timestamp = time.strftime("%H%M%S")
        debug_file = f"screenshots/heart_detection_{timestamp}.png"
        cv2.imwrite(debug_file, debug_img)
        print(f"하트 감지 디버그 이미지: {debug_file}")
    else:
        print("하트 애니메이션을 감지할 수 없습니다")


if __name__ == "__main__":
    print("=== 학생 호감도 템플릿 생성 도구 ===")
    print("1. 호감도 표식 템플릿 생성")
    print("2. 인연 랭크 업 팝업 템플릿 생성")
    print("3. 호감도 표식 템플릿 테스트")
    print("4. 인연 랭크 업 템플릿 테스트")
    print("5. 하트 애니메이션 감지 테스트")
    
    choice = input("선택 (1-5): ").strip()
    
    if choice == "1":
        create_affinity_indicator_template()
    elif choice == "2":
        create_rank_up_template()
    elif choice == "3":
        test_affinity_indicator_template()
    elif choice == "4":
        test_rank_up_template()
    elif choice == "5":
        detect_heart_animation()
    else:
        print("잘못된 선택입니다")