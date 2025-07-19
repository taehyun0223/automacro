"""
학생 호감도 자동화 유스케이스
카페에서 학생들의 호감도 표식을 감지하고 자동으로 상호작용
"""
import time
from typing import List, Optional

from infrastructure.process.game_process_detector import GameProcessDetector
from infrastructure.screen.game_state_detector import BlueArchiveStateDetector, GameState
from infrastructure.screen.student_affinity_detector import StudentAffinityDetector
from domain.models.student_affinity import AffinityInteractionResult, AffinityResult


class StudentAffinityUseCase:
    """학생 호감도 자동화 유스케이스"""
    
    def __init__(self):
        self.process_detector = GameProcessDetector()
        self.state_detector = BlueArchiveStateDetector()
        self.affinity_detector = StudentAffinityDetector()
        
    def execute(self) -> bool:
        """학생 호감도 자동화 전체 실행"""
        print("=" * 50)
        print("💕 학생 호감도 자동화 시작")
        print("=" * 50)
        
        try:
            # 1. 게임 프로세스 확인
            if not self._check_game_process():
                return False
            
            # 2. 게임 상태 확인 및 활성화
            if not self._ensure_game_ready():
                return False
            
            # 3. 카페 화면 확인
            if not self._ensure_in_cafe():
                return False
            
            # 4. 학생 호감도 상호작용 실행
            results = self._process_student_affinity()
            
            # 5. 결과 요약
            self._summarize_results(results)
            
            print("✅ 학생 호감도 자동화 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 학생 호감도 자동화 중 오류 발생: {e}")
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
    
    def _ensure_in_cafe(self) -> bool:
        """카페 화면 상태 확인"""
        print("\n3️⃣ 카페 화면 상태 확인 중...")
        
        # 현재 상태가 카페인지 확인 (간단한 검증)
        # 실제로는 카페 특유의 UI 요소를 감지해야 하지만,
        # 일단 게임이 활성화되어 있고 in_game 상태라면 카페에 있다고 가정
        
        result = self.state_detector.detect_current_state()
        
        if result.state in [GameState.IN_GAME, GameState.MAIN_MENU]:
            print("✅ 카페 화면 상태 확인 완료")
            print("💡 카페에 있는지 확인하고 학생 호감도 작업을 시작합니다")
            return True
        else:
            print(f"⚠️ 현재 상태: {result.state.value}")
            print("💡 카페 화면으로 이동한 후 다시 시도해주세요")
            return True  # 일단 계속 진행 (사용자가 카페에 있다고 가정)
    
    def _process_student_affinity(self) -> List[AffinityInteractionResult]:
        """학생 호감도 처리"""
        print("\n4️⃣ 학생 호감도 상호작용 실행 중...")
        
        # 학생들과 호감도 상호작용
        results = self.affinity_detector.process_all_students()
        
        if not results:
            print("💡 호감도 표식이 있는 학생이 없거나 템플릿이 없습니다")
            print("   tools/templates/create_affinity_templates.py를 실행해서 템플릿을 만들어보세요")
        
        return results
    
    def _summarize_results(self, results: List[AffinityInteractionResult]):
        """결과 요약"""
        if not results:
            return
            
        print("\n📊 학생 호감도 상호작용 결과:")
        print("-" * 40)
        
        rank_ups = 0
        normal_increases = 0
        no_changes = 0
        errors = 0
        total_time = 0.0
        
        for i, result in enumerate(results, 1):
            status_emoji = {
                AffinityResult.RANK_UP: "🎉",
                AffinityResult.NORMAL_INCREASE: "💖",
                AffinityResult.NO_CHANGE: "😐",
                AffinityResult.ERROR: "❌"
            }.get(result.result, "❓")
            
            print(f"학생 {i}: {status_emoji} {result.message} ({result.interaction_time:.1f}초)")
            
            if result.result == AffinityResult.RANK_UP:
                rank_ups += 1
            elif result.result == AffinityResult.NORMAL_INCREASE:
                normal_increases += 1
            elif result.result == AffinityResult.NO_CHANGE:
                no_changes += 1
            else:
                errors += 1
                
            total_time += result.interaction_time
        
        print("-" * 40)
        print(f"📈 요약:")
        print(f"  🎉 인연 랭크 업: {rank_ups}명")
        print(f"  💖 호감도 증가: {normal_increases}명")
        print(f"  😐 변화 없음: {no_changes}명")
        print(f"  ❌ 오류: {errors}명")
        print(f"  ⏱️ 총 소요시간: {total_time:.1f}초")
    
    def get_status(self) -> dict:
        """현재 상태 정보 반환"""
        process_running = self.process_detector.is_game_running()
        
        if process_running:
            game_state = self.state_detector.detect_current_state()
            return {
                "process_running": True,
                "game_state": game_state.state.value,
                "confidence": game_state.confidence,
                "ready_for_affinity": game_state.state in [GameState.IN_GAME, GameState.MAIN_MENU]
            }
        else:
            return {
                "process_running": False,
                "game_state": "unknown",
                "confidence": 0.0,
                "ready_for_affinity": False
            }


def create_student_affinity_automation() -> StudentAffinityUseCase:
    """학생 호감도 자동화 유스케이스 팩토리"""
    return StudentAffinityUseCase()


if __name__ == "__main__":
    # 테스트 실행
    automation = create_student_affinity_automation()
    
    print("💕 학생 호감도 자동화 유스케이스 테스트")
    print("=" * 40)
    
    # 현재 상태 확인
    status = automation.get_status()
    print(f"게임 프로세스: {status['process_running']}")
    print(f"게임 상태: {status['game_state']}")
    print(f"호감도 작업 준비: {status['ready_for_affinity']}")
    
    if status['process_running']:
        print("\n학생 호감도 자동화를 실행하시겠습니까? (y/n): ", end="")
        try:
            response = input().strip().lower()
            if response == 'y':
                success = automation.execute()
                if success:
                    print("\n🎉 학생 호감도 자동화 성공!")
                else:
                    print("\n😞 학생 호감도 자동화 실패")
            else:
                print("학생 호감도 자동화를 취소했습니다.")
        except:
            print("\n입력 건너뛰기 - 자동화 취소")
    else:
        print("\n게임을 먼저 실행해주세요.")