"""
블루아카이브 일일퀘스트 매크로 메인 진입점
"""
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from domain.services.image_locator import OpenCVImageLocator
from infrastructure.screen.clicker import PyAutoGuiScreenClicker, SafeClicker
from infrastructure.input.keyboard_monitor import PynputKeyboardMonitor
from application.macros.cafe_reward_collector import CafeRewardCollector
from application.macros.daily_mission_claimer import DailyMissionClaimer
from application.usecases.macro_loop_usecase import BlueArchiveMacroLoopUseCase, SequentialMacroUseCase
import config


def setup_dependencies():
    """의존성 설정"""
    # 이미지 위치 탐지 서비스
    image_locator = OpenCVImageLocator()
    
    # 클릭 처리 (안전한 클릭 래퍼 사용)
    base_clicker = PyAutoGuiScreenClicker()
    clicker = SafeClicker(base_clicker)
    
    # 키보드 모니터링
    keyboard_monitor = PynputKeyboardMonitor()
    
    return image_locator, clicker, keyboard_monitor


def create_macros(image_locator, clicker):
    """매크로 인스턴스 생성"""
    # 개별 매크로들
    cafe_collector = CafeRewardCollector(image_locator, clicker)
    mission_claimer = DailyMissionClaimer(image_locator, clicker)
    
    return cafe_collector, mission_claimer


def check_assets():
    """에셋 파일 존재 확인"""
    missing_files = []
    
    for image_name, filename in config.IMAGES.items():
        filepath = f"{config.ASSETS_PATH}{filename}"
        if not os.path.exists(filepath):
            missing_files.append(filepath)
    
    if missing_files:
        print("⚠️  다음 이미지 파일들이 없습니다:")
        for file in missing_files:
            print(f"   - {file}")
        print("\\n📝 사용법:")
        print("1. 게임에서 해당 버튼들을 스크린샷으로 캡처")
        print("2. 캡처한 이미지들을 assets/ 폴더에 저장")
        print("3. 매크로 재실행")
        return False
    
    return True


def print_usage_info():
    """사용법 안내"""
    print("🎮 블루아카이브 일일퀘스트 매크로")
    print("="*50)
    print(f"🔧 설정된 화면 해상도: {config.SCREEN_RESOLUTION}")
    print(f"⏱️  매크로 루프 간격: {config.LOOP_DELAY}초")
    print(f"🛑 종료 키: {config.EXIT_KEY}")
    print(f"📁 이미지 경로: {config.ASSETS_PATH}")
    print("="*50)
    print("✅ 실행할 작업:")
    print("   1. 카페 보상 수령")
    print("   2. 일일 미션 수령")
    print("="*50)


def main():
    """메인 함수"""
    try:
        # 사용법 출력
        print_usage_info()
        
        # 에셋 파일 확인
        if not check_assets():
            return
        
        print("🔍 에셋 파일 확인 완료")
        
        # 의존성 설정
        image_locator, clicker, keyboard_monitor = setup_dependencies()
        
        # 매크로 생성
        cafe_collector, mission_claimer = create_macros(image_locator, clicker)
        
        # 매크로 루프 설정
        macro_loop = BlueArchiveMacroLoopUseCase(keyboard_monitor)
        
        # 순차 실행 매크로 (카페 -> 일일미션)
        sequential_macro = SequentialMacroUseCase([cafe_collector, mission_claimer])
        macro_loop.add_macro(sequential_macro)
        
        print("🚀 매크로 시작...")
        print(f"종료하려면 {config.EXIT_KEY}를 누르세요\\n")
        
        # 매크로 실행
        macro_loop.start()
        
    except KeyboardInterrupt:
        print("\\n❌ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\\n💥 오류 발생: {e}")
        if config.DEBUG_MODE:
            import traceback
            traceback.print_exc()
    finally:
        print("\\n👋 매크로 종료")


if __name__ == "__main__":
    main()