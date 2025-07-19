"""
카페 자동화 유스케이스
게임 인식 -> 활성화 -> 카페 아이콘 클릭 -> 카페 수익 수령의 전체 흐름
"""
import time
from typing import Optional

from infrastructure.process.game_process_detector import GameProcessDetector
from infrastructure.screen.game_state_detector import BlueArchiveStateDetector, GameState
from domain.services.image_locator import OpenCVImageLocator
from domain.models.image_region import ImageRegion
from infrastructure.screen.clicker import PyAutoGuiScreenClicker
from infrastructure.screen.cafe_revenue_detector import CafeRevenueDetector


class CafeAutomationUseCase:
    """카페 자동화 유스케이스"""
    
    def __init__(self, collect_revenue: bool = False):
        self.process_detector = GameProcessDetector()
        self.state_detector = BlueArchiveStateDetector()
        self.image_locator = OpenCVImageLocator()
        self.clicker = PyAutoGuiScreenClicker()
        self.revenue_detector = CafeRevenueDetector()
        self.collect_revenue = collect_revenue
        
        # 카페 버튼 이미지 영역 정의
        self.cafe_button_region = ImageRegion(
            name="cafe_button",
            image_path="assets/cafe_button.png",
            confidence=0.6,
            offset=(0, 0)
        )
    
    def execute(self) -> bool:
        """카페 자동화 전체 실행"""
        print("=" * 50)
        print("🏠 카페 자동화 시작")
        print("=" * 50)
        
        try:
            # 1. 게임 프로세스 확인
            if not self._check_game_process():
                return False
            
            # 2. 게임 상태 확인 및 활성화
            if not self._ensure_game_ready():
                return False
            
            # 3. 메인 메뉴 상태 확인
            if not self._wait_for_main_menu():
                return False
            
            # 4. 카페 아이콘 찾기 및 클릭
            if not self._click_cafe_button():
                return False
            
            # 5. 카페 수익 수령 (옵션)
            if self.collect_revenue:
                if not self._collect_cafe_revenue():
                    print("⚠️ 카페 수익 수령 실패, 하지만 카페 접근은 성공")
            
            print("✅ 카페 자동화 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 카페 자동화 중 오류 발생: {e}")
            return False
    
    def _check_game_process(self) -> bool:
        """게임 프로세스 확인"""
        print("\n1️⃣ 게임 프로세스 확인 중...")
        
        if not self.process_detector.is_game_running():
            print("❌ 블루아카이브 게임이 실행되지 않았습니다!")
            print("게임을 먼저 실행해주세요.")
            return False
        
        print("✅ 게임 프로세스 확인 완료")
        return True
    
    def _ensure_game_ready(self) -> bool:
        """게임 준비 상태 확인"""
        print("\n2️⃣ 게임 활성화 및 준비 상태 확인 중...")
        
        # 게임 상태 감지 (자동으로 활성화 포함)
        result = self.state_detector.detect_current_state(save_screenshot=True)
        
        if result.state == GameState.UNKNOWN:
            print("❌ 게임 상태를 확인할 수 없습니다")
            return False
        
        print(f"✅ 게임 상태: {result.state.value} (신뢰도: {result.confidence:.2f})")
        if result.screenshot_path:
            print(f"📸 스크린샷: {result.screenshot_path}")
        
        return True
    
    def _wait_for_main_menu(self, max_wait: int = 30) -> bool:
        """메인 메뉴 상태까지 대기"""
        print("\n3️⃣ 메인 메뉴 상태 대기 중...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            result = self.state_detector.detect_current_state()
            
            if result.state == GameState.MAIN_MENU:
                print(f"✅ 메인 메뉴 상태 확인 (신뢰도: {result.confidence:.2f})")
                return True
            elif result.state == GameState.LOADING:
                print("⏳ 로딩 중... 대기")
                time.sleep(2)
                continue
            else:
                print(f"⏳ 현재 상태: {result.state.value}, 메인 메뉴 대기 중...")
                time.sleep(3)
                continue
        
        print("❌ 메인 메뉴 상태 대기 시간 초과")
        return False
    
    def _click_cafe_button(self) -> bool:
        """카페 버튼 클릭"""
        print("\n4️⃣ 카페 버튼 찾기 및 클릭...")
        
        # 카페 버튼 찾기 (최대 3번 시도)
        for attempt in range(3):
            print(f"🔍 카페 버튼 검색 시도 {attempt + 1}/3...")
            
            click_position = self.image_locator.find_image(self.cafe_button_region)
            
            if click_position:
                print(f"✅ 카페 버튼 발견! (신뢰도: {click_position.confidence:.3f})")
                print(f"📍 클릭 위치: ({click_position.x}, {click_position.y})")
                
                # 카페 버튼 클릭
                success = self.clicker.click(click_position)
                
                if success:
                    print("✅ 카페 버튼 클릭 완료!")
                    time.sleep(2)  # 카페 로딩 대기
                    return True
                else:
                    print("❌ 카페 버튼 클릭 실패")
                    return False
            else:
                print(f"❌ 카페 버튼을 찾을 수 없습니다 (시도 {attempt + 1}/3)")
                if attempt < 2:
                    print("⏳ 2초 후 재시도...")
                    time.sleep(2)
        
        print("❌ 카페 버튼을 찾을 수 없습니다")
        print("💡 현재 화면을 확인하고 assets/cafe_button.png 이미지를 업데이트해보세요")
        
        # 현재 상태 저장 (디버깅용)
        self.state_detector.detect_current_state(save_screenshot=True)
        
        return False
    
    def _collect_cafe_revenue(self) -> bool:
        """카페 수익 수령"""
        print("\n5️⃣ 카페 수익 수령 중...")
        
        # 카페 화면 로딩 대기
        time.sleep(2)
        
        try:
            success = self.revenue_detector.collect_cafe_revenue()
            if success:
                print("✅ 카페 수익 수령 완료!")
                return True
            else:
                print("❌ 카페 수익 수령 실패")
                print("💡 템플릿 이미지가 없거나 버튼을 찾을 수 없습니다")
                print("   create_revenue_templates.py를 실행해서 템플릿을 만들어보세요")
                return False
                
        except Exception as e:
            print(f"❌ 카페 수익 수령 중 오류: {e}")
            return False
    
    def get_status(self) -> dict:
        """현재 상태 정보 반환"""
        process_running = self.process_detector.is_game_running()
        
        if process_running:
            game_state = self.state_detector.detect_current_state()
            return {
                "process_running": True,
                "game_state": game_state.state.value,
                "confidence": game_state.confidence,
                "ready_for_cafe": game_state.state == GameState.MAIN_MENU
            }
        else:
            return {
                "process_running": False,
                "game_state": "unknown",
                "confidence": 0.0,
                "ready_for_cafe": False
            }


def create_cafe_automation(collect_revenue: bool = False) -> CafeAutomationUseCase:
    """카페 자동화 유스케이스 팩토리"""
    return CafeAutomationUseCase(collect_revenue=collect_revenue)


if __name__ == "__main__":
    # 테스트 실행
    automation = create_cafe_automation()
    
    print("🏠 카페 자동화 유스케이스 테스트")
    print("=" * 40)
    
    # 현재 상태 확인
    status = automation.get_status()
    print(f"게임 프로세스: {status['process_running']}")
    print(f"게임 상태: {status['game_state']}")
    print(f"카페 준비: {status['ready_for_cafe']}")
    
    if status['process_running']:
        print("\n카페 자동화를 실행하시겠습니까? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            success = automation.execute()
            if success:
                print("\n🎉 카페 자동화 성공!")
            else:
                print("\n😞 카페 자동화 실패")
        else:
            print("카페 자동화를 취소했습니다.")
    else:
        print("\n게임을 먼저 실행해주세요.")