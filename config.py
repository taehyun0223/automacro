"""
블루아카이브 매크로 설정 파일
"""

# 화면 설정
SCREEN_RESOLUTION = (2560, 1440)
FULLSCREEN_CAPTURE = True

# 이미지 매칭 설정
IMAGE_MATCH_CONFIDENCE = 0.8
IMAGE_MATCH_GRAYSCALE = True

# 클릭 설정
CLICK_DELAY_MIN = 0.5  # 최소 클릭 간격 (초)
CLICK_DELAY_MAX = 2.0  # 최대 클릭 간격 (초)
CLICK_OFFSET_RANGE = 5  # 클릭 위치 랜덤 오프셋 범위 (픽셀)

# 매크로 실행 설정
LOOP_DELAY = 3.0  # 각 매크로 루프 간 대기 시간 (초)
MAX_RETRY_COUNT = 3  # 이미지 찾기 실패 시 재시도 횟수

# 종료 키 설정
EXIT_KEY = 'ctrl+q'  # 매크로 종료 키

# 에셋 경로
ASSETS_PATH = "assets/"

# 일일 퀘스트 관련 이미지 파일명
IMAGES = {
    "cafe_button": "cafe_button.png",
    "cafe_reward": "cafe_reward.png", 
    "daily_mission_button": "daily_mission_button.png",
    "mission_claim_button": "mission_claim_button.png",
    "close_button": "close_button.png"
}

# 디버그 설정
DEBUG_MODE = True
SAVE_SCREENSHOTS = False