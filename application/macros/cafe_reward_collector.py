"""
카페 보상 수령 매크로
"""
import time
from typing import Optional

from domain.models.image_region import ImageRegion, MacroResult
from domain.services.image_locator import ImageLocator
from infrastructure.screen.clicker import Clicker
import config


class CafeRewardCollector:
    """카페 보상 수령 매크로"""
    
    def __init__(self, image_locator: ImageLocator, clicker: Clicker):
        self.image_locator = image_locator
        self.clicker = clicker
        
        # 이미지 영역 정의
        self.cafe_button = ImageRegion(
            name="cafe_button",
            image_path=f"{config.ASSETS_PATH}{config.IMAGES['cafe_button']}",
            confidence=config.IMAGE_MATCH_CONFIDENCE
        )
        
        self.cafe_reward = ImageRegion(
            name="cafe_reward", 
            image_path=f"{config.ASSETS_PATH}{config.IMAGES['cafe_reward']}",
            confidence=config.IMAGE_MATCH_CONFIDENCE
        )
        
        self.close_button = ImageRegion(
            name="close_button",
            image_path=f"{config.ASSETS_PATH}{config.IMAGES['close_button']}",
            confidence=config.IMAGE_MATCH_CONFIDENCE
        )
    
    def execute(self) -> MacroResult:
        """카페 보상 수령 매크로 실행"""
        clicked_positions = []
        
        try:
            if config.DEBUG_MODE:
                print("카페 보상 수령 매크로 시작")
            
            # 1. 카페 버튼 찾기 및 클릭
            cafe_position = self.image_locator.find_image(self.cafe_button)
            if not cafe_position:
                return MacroResult(
                    success=False,
                    message="카페 버튼을 찾을 수 없습니다",
                    clicked_positions=clicked_positions
                )
            
            if not self.clicker.click(cafe_position):
                return MacroResult(
                    success=False,
                    message="카페 버튼 클릭 실패",
                    clicked_positions=clicked_positions
                )
            
            clicked_positions.append(cafe_position)
            time.sleep(2.0)  # 카페 화면 로딩 대기
            
            # 2. 보상 아이템 찾기 및 수령
            reward_collected = False
            retry_count = 0
            
            while retry_count < config.MAX_RETRY_COUNT:
                reward_position = self.image_locator.find_image(self.cafe_reward)
                
                if reward_position:
                    if self.clicker.click(reward_position):
                        clicked_positions.append(reward_position)
                        reward_collected = True
                        if config.DEBUG_MODE:
                            print("카페 보상 수령 완료")
                        time.sleep(1.0)
                    break
                
                retry_count += 1
                time.sleep(1.0)
            
            # 3. 카페 화면 닫기
            close_position = self.image_locator.find_image(self.close_button)
            if close_position:
                if self.clicker.click(close_position):
                    clicked_positions.append(close_position)
                    if config.DEBUG_MODE:
                        print("카페 화면 닫기 완료")
            
            success_message = "카페 보상 수령 완료" if reward_collected else "수령할 보상이 없습니다"
            
            return MacroResult(
                success=True,
                message=success_message,
                clicked_positions=clicked_positions
            )
            
        except Exception as e:
            error_message = f"카페 보상 수령 중 오류: {e}"
            if config.DEBUG_MODE:
                print(error_message)
            
            return MacroResult(
                success=False,
                message=error_message,
                clicked_positions=clicked_positions
            )