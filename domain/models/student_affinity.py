"""
학생 호감도 도메인 모델
"""
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum


class AffinityResult(Enum):
    """호감도 증가 결과"""
    RANK_UP = "rank_up"          # 인연 랭크 업
    NORMAL_INCREASE = "normal"   # 일반 호감도 증가
    NO_CHANGE = "no_change"      # 변화 없음
    ERROR = "error"              # 오류 발생


@dataclass
class StudentPosition:
    """학생 위치 정보"""
    x: int                       # 화면 X 좌표
    y: int                       # 화면 Y 좌표
    confidence: float            # 감지 신뢰도
    has_indicator: bool          # 호감도 표식 여부
    student_id: Optional[str] = None  # 학생 식별자 (옵션)


@dataclass
class AffinityInteractionResult:
    """호감도 상호작용 결과"""
    student_position: StudentPosition
    result: AffinityResult
    message: str                 # 결과 메시지
    interaction_time: float      # 상호작용 소요 시간


class StudentAffinityRegion:
    """학생 호감도 영역 정의"""
    
    def __init__(self, name: str, template_path: str, confidence: float = 0.6):
        self.name = name
        self.template_path = template_path
        self.confidence = confidence
        
    def __repr__(self):
        return f"StudentAffinityRegion(name='{self.name}', confidence={self.confidence})"


class CafeAffinityArea:
    """카페 호감도 상호작용 영역"""
    
    # 카페 내 학생들이 위치할 수 있는 대략적인 영역들
    STUDENT_AREAS = [
        (100, 200, 300, 400),   # 왼쪽 상단 영역
        (400, 200, 600, 400),   # 중앙 상단 영역  
        (700, 200, 900, 400),   # 오른쪽 상단 영역
        (200, 500, 500, 700),   # 왼쪽 하단 영역
        (600, 500, 900, 700),   # 오른쪽 하단 영역
    ]
    
    @classmethod
    def get_search_areas(cls) -> list:
        """학생 검색 영역 반환"""
        return cls.STUDENT_AREAS.copy()