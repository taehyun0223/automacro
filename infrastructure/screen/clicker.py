"""
화면 클릭 처리 인프라스트럭처
"""
import pyautogui
import random
import time
from abc import ABC, abstractmethod
from typing import Optional

from domain.models.image_region import ClickPosition
import config


class Clicker(ABC):
    """클릭 처리 인터페이스"""
    
    @abstractmethod
    def click(self, position: ClickPosition) -> bool:
        """지정된 위치 클릭"""
        pass
    
    @abstractmethod
    def double_click(self, position: ClickPosition) -> bool:
        """지정된 위치 더블클릭"""
        pass


class PyAutoGuiScreenClicker(Clicker):
    """PyAutoGUI 기반 화면 클릭 구현체"""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    
    def _add_random_offset(self, position: ClickPosition) -> tuple[int, int]:
        """클릭 위치에 랜덤 오프셋 추가"""
        offset_range = config.CLICK_OFFSET_RANGE
        random_x = random.randint(-offset_range, offset_range)
        random_y = random.randint(-offset_range, offset_range)
        
        return (position.x + random_x, position.y + random_y)
    
    def _random_delay(self):
        """랜덤 지연"""
        delay = random.uniform(config.CLICK_DELAY_MIN, config.CLICK_DELAY_MAX)
        time.sleep(delay)
    
    def click(self, position: ClickPosition) -> bool:
        """단일 클릭 수행"""
        try:
            x, y = self._add_random_offset(position)
            
            if config.DEBUG_MODE:
                print(f"Clicking at ({x}, {y}) with confidence {position.confidence:.3f}")
            
            pyautogui.click(x, y)
            self._random_delay()
            
            return True
            
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Click error: {e}")
            return False
    
    def double_click(self, position: ClickPosition) -> bool:
        """더블클릭 수행"""
        try:
            x, y = self._add_random_offset(position)
            
            if config.DEBUG_MODE:
                print(f"Double clicking at ({x}, {y}) with confidence {position.confidence:.3f}")
            
            pyautogui.doubleClick(x, y)
            self._random_delay()
            
            return True
            
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Double click error: {e}")
            return False


class SafeClicker(Clicker):
    """안전한 클릭 처리 (화면 경계 검사 포함)"""
    
    def __init__(self, base_clicker: Clicker):
        self.base_clicker = base_clicker
        self.screen_width, self.screen_height = pyautogui.size()
    
    def _is_valid_position(self, position: ClickPosition) -> bool:
        """클릭 위치가 화면 범위 내인지 확인"""
        return (0 <= position.x < self.screen_width and 
                0 <= position.y < self.screen_height)
    
    def click(self, position: ClickPosition) -> bool:
        """안전한 단일 클릭"""
        if not self._is_valid_position(position):
            if config.DEBUG_MODE:
                print(f"Invalid click position: ({position.x}, {position.y})")
            return False
        
        return self.base_clicker.click(position)
    
    def double_click(self, position: ClickPosition) -> bool:
        """안전한 더블클릭"""
        if not self._is_valid_position(position):
            if config.DEBUG_MODE:
                print(f"Invalid double click position: ({position.x}, {position.y})")
            return False
        
        return self.base_clicker.double_click(position)