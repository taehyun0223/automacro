"""
일일 미션 수령 매크로
"""
import time
from typing import List

from domain.models.image_region import ImageRegion, MacroResult, ClickPosition
from domain.services.image_locator import ImageLocator
from infrastructure.screen.clicker import Clicker
import config


class DailyMissionClaimer:
    """일일 미션 수령 매크로"""
    
    def __init__(self, image_locator: ImageLocator, clicker: Clicker):
        self.image_locator = image_locator
        self.clicker = clicker
        
        # 이미지 영역 정의
        self.mission_button = ImageRegion(
            name="daily_mission_button",
            image_path=f"{config.ASSETS_PATH}{config.IMAGES['daily_mission_button']}",
            confidence=config.IMAGE_MATCH_CONFIDENCE
        )
        
        self.claim_button = ImageRegion(
            name="mission_claim_button",
            image_path=f"{config.ASSETS_PATH}{config.IMAGES['mission_claim_button']}",
            confidence=config.IMAGE_MATCH_CONFIDENCE
        )
        
        self.close_button = ImageRegion(
            name="close_button",
            image_path=f"{config.ASSETS_PATH}{config.IMAGES['close_button']}",
            confidence=config.IMAGE_MATCH_CONFIDENCE
        )
    
    def execute(self) -> MacroResult:
        """일일 미션 수령 매크로 실행"""
        clicked_positions = []
        
        try:
            if config.DEBUG_MODE:
                print("일일 미션 수령 매크로 시작")
            
            # 1. 일일 미션 버튼 찾기 및 클릭
            mission_position = self.image_locator.find_image(self.mission_button)
            if not mission_position:
                return MacroResult(
                    success=False,
                    message="일일 미션 버튼을 찾을 수 없습니다",
                    clicked_positions=clicked_positions
                )
            
            if not self.clicker.click(mission_position):
                return MacroResult(
                    success=False,
                    message="일일 미션 버튼 클릭 실패",
                    clicked_positions=clicked_positions
                )
            
            clicked_positions.append(mission_position)
            time.sleep(3.0)  # 미션 화면 로딩 대기
            
            # 2. 모든 수령 가능한 미션 보상 클릭
            claimed_count = self._claim_all_rewards(clicked_positions)
            
            # 3. 미션 화면 닫기
            close_position = self.image_locator.find_image(self.close_button)
            if close_position:
                if self.clicker.click(close_position):
                    clicked_positions.append(close_position)
                    if config.DEBUG_MODE:
                        print("일일 미션 화면 닫기 완료")
            
            success_message = f"일일 미션 {claimed_count}개 수령 완료" if claimed_count > 0 else "수령할 미션이 없습니다"
            
            return MacroResult(
                success=True,
                message=success_message,
                clicked_positions=clicked_positions
            )
            
        except Exception as e:
            error_message = f"일일 미션 수령 중 오류: {e}"
            if config.DEBUG_MODE:
                print(error_message)
            
            return MacroResult(
                success=False,
                message=error_message,
                clicked_positions=clicked_positions
            )
    
    def _claim_all_rewards(self, clicked_positions: List[ClickPosition]) -> int:
        """모든 수령 가능한 보상 클릭"""
        claimed_count = 0
        max_claims = 10  # 무한 루프 방지
        
        for attempt in range(max_claims):
            # 수령 가능한 버튼들 찾기
            claim_positions = self.image_locator.find_all_images(self.claim_button)
            
            if not claim_positions:
                if config.DEBUG_MODE:
                    print(f"더 이상 수령할 미션이 없습니다 (시도: {attempt + 1})")
                break
            
            # 첫 번째 수령 버튼 클릭
            if self.clicker.click(claim_positions[0]):
                clicked_positions.append(claim_positions[0])
                claimed_count += 1
                
                if config.DEBUG_MODE:
                    print(f"미션 보상 수령 #{claimed_count}")
                
                time.sleep(1.5)  # 보상 수령 애니메이션 대기
            else:
                if config.DEBUG_MODE:
                    print("수령 버튼 클릭 실패")
                break
        
        return claimed_count