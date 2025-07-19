"""
이미지 위치 탐지 서비스
"""
import cv2
import numpy as np
import pyautogui
from abc import ABC, abstractmethod
from typing import Optional, List
from PIL import Image

from domain.models.image_region import ImageRegion, ClickPosition
import config


class ImageLocator(ABC):
    """이미지 위치 탐지 인터페이스"""
    
    @abstractmethod
    def find_image(self, image_region: ImageRegion) -> Optional[ClickPosition]:
        """이미지를 찾아 클릭 위치 반환"""
        pass
    
    @abstractmethod
    def find_all_images(self, image_region: ImageRegion) -> List[ClickPosition]:
        """모든 매칭되는 이미지 위치 반환"""
        pass


class OpenCVImageLocator(ImageLocator):
    """OpenCV 기반 이미지 위치 탐지 구현체"""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        
    def _capture_screen(self) -> np.ndarray:
        """화면 캡처"""
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def _load_template(self, image_path: str) -> np.ndarray:
        """템플릿 이미지 로드"""
        template = cv2.imread(image_path)
        if template is None:
            raise FileNotFoundError(f"Template image not found: {image_path}")
        return template
    
    def find_image(self, image_region: ImageRegion) -> Optional[ClickPosition]:
        """단일 이미지 위치 탐지"""
        try:
            screen = self._capture_screen()
            template = self._load_template(image_region.image_path)
            
            if config.IMAGE_MATCH_GRAYSCALE:
                screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= image_region.confidence:
                template_h, template_w = template.shape[:2]
                center_x = max_loc[0] + template_w // 2
                center_y = max_loc[1] + template_h // 2
                
                # 오프셋 적용
                center_x += image_region.offset[0]
                center_y += image_region.offset[1]
                
                return ClickPosition(x=center_x, y=center_y, confidence=max_val)
            
            return None
            
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Image search error for {image_region.name}: {e}")
            return None
    
    def find_all_images(self, image_region: ImageRegion) -> List[ClickPosition]:
        """모든 매칭되는 이미지 위치 탐지"""
        try:
            screen = self._capture_screen()
            template = self._load_template(image_region.image_path)
            
            if config.IMAGE_MATCH_GRAYSCALE:
                screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= image_region.confidence)
            
            positions = []
            template_h, template_w = template.shape[:2]
            
            for pt in zip(*locations[::-1]):
                center_x = pt[0] + template_w // 2
                center_y = pt[1] + template_h // 2
                
                # 오프셋 적용
                center_x += image_region.offset[0]
                center_y += image_region.offset[1]
                
                confidence = result[pt[1], pt[0]]
                positions.append(ClickPosition(x=center_x, y=center_y, confidence=confidence))
            
            return positions
            
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Multiple image search error for {image_region.name}: {e}")
            return []