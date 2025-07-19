"""
이미지 영역 도메인 모델
"""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ImageRegion:
    """
    버튼이나 UI 요소의 이미지 정보를 나타내는 도메인 모델
    """
    name: str  # 버튼 이름 (예: "cafe_button")
    image_path: str  # 이미지 파일 경로
    confidence: float = 0.8  # 이미지 매칭 신뢰도 (0.0 ~ 1.0)
    offset: Tuple[int, int] = (0, 0)  # 클릭 위치 오프셋 (x, y)
    
    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass 
class ClickPosition:
    """
    클릭할 위치 정보
    """
    x: int
    y: int
    confidence: float
    
    def apply_offset(self, offset_x: int, offset_y: int) -> 'ClickPosition':
        """오프셋을 적용한 새로운 클릭 위치 반환"""
        return ClickPosition(
            x=self.x + offset_x,
            y=self.y + offset_y, 
            confidence=self.confidence
        )


@dataclass
class MacroResult:
    """
    매크로 실행 결과
    """
    success: bool
    message: str
    clicked_positions: list[ClickPosition] = None
    
    def __post_init__(self):
        if self.clicked_positions is None:
            self.clicked_positions = []