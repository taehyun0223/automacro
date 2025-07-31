"""
FSM 기반 자동화 유스케이스 - 기존 시스템과 통합
기존의 CafeAutomationUseCase를 확장하여 FSM 기반 자동화를 제공
"""

from domain.models.finite_state_machine import GameStateMachine, FSMContext
from application.states.game_states import IdleState, LoadingState, HomeState, CafeState, RewardPopupState, ErrorState
from infrastructure.process.game_process_detector import GameProcessDetector
from infrastructure.screen.game_state_detector import BlueArchiveStateDetector
from domain.services.image_locator import OpenCVImageLocator
from infrastructure.screen.clicker import PyAutoGuiScreenClicker
import logging
import time
from typing import Optional, Dict, Any


class FSMAutomationUseCase:
    """FSM 기반 게임 자동화 유스케이스"""
    
    def __init__(self):
        # 기존 컴포넌트들 초기화
        self.process_detector = GameProcessDetector()
        self.state_detector = BlueArchiveStateDetector()
        self.image_locator = OpenCVImageLocator()
        self.clicker = PyAutoGuiScreenClicker()
        
        # FSM 컨텍스트 생성
        self.fsm_context = FSMContext(
            image_locator=self.image_locator,
            clicker=self.clicker,
            state_detector=self.state_detector,
            process_detector=self.process_detector,
            config={
                "max_cafe_attempts": 5,
                "reward_collection_timeout": 30,
                "auto_return_home": True,
                "max_runtime_minutes": 30,
                "enable_screenshots": True
            },
            shared_data={
                "cafe_rewards_collected": 0,
                "successful_actions": 0,
                "failed_actions": 0,
                "last_clicked": "",
                "session_start_time": time.time()
            }
        )
        
        # 로깅 설정
        self.logger = logging.getLogger("FSMAutomation")
        
        # FSM 초기화 및 상태 등록
        self.fsm = GameStateMachine(self.fsm_context)
        self._register_states()
        self.logger.setLevel(logging.INFO)
        
        # 콘솔 핸들러 추가 (없는 경우에만)
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _register_states(self):
        """상태들을 FSM에 등록"""
        self.fsm.register_state("IDLE", IdleState)
        self.fsm.register_state("LOADING", LoadingState)
        self.fsm.register_state("IN_HOME", HomeState)
        self.fsm.register_state("IN_CAFE", CafeState)
        self.fsm.register_state("REWARD_POPUP", RewardPopupState)
        self.fsm.register_state("ERROR", ErrorState)
        
        self.logger.info("모든 FSM 상태 등록 완료")
    
    def start_automation(self, initial_state: str = "IDLE", max_runtime_minutes: int = 30) -> Dict[str, Any]:
        """
        자동화 시작
        
        Args:
            initial_state: 시작 상태 (기본값: IDLE)
            max_runtime_minutes: 최대 실행 시간 (분)
            
        Returns:
            실행 결과 딕셔너리
        """
        print("🚀 FSM 기반 블루아카이브 자동화 시작")
        print("=" * 50)
        print(f"초기 상태: {initial_state}")
        print(f"최대 실행 시간: {max_runtime_minutes}분")
        print("Ctrl+C로 언제든 중단 가능합니다")
        print("=" * 50)
        
        start_time = time.time()
        max_iterations = max_runtime_minutes * 60 // 2  # 2초마다 1회 반복 가정
        
        try:
            self.fsm.set_initial_state(initial_state)
            
            # 런타임 제한을 위한 래퍼
            original_run = self.fsm.run
            def limited_run():
                iteration = 0
                while (self.fsm.is_running and 
                       iteration < max_iterations and 
                       time.time() - start_time < max_runtime_minutes * 60):
                    
                    # 현재 상태 실행
                    if self.fsm.current_state:
                        next_state = self.fsm.current_state.execute()
                        
                        # 전환 조건 확인
                        if next_state:
                            transition_state = next_state
                        else:
                            transition_state = self.fsm.current_state.check_transitions()
                        
                        # 상태 전환
                        if transition_state and transition_state != self.fsm.current_state.state_name:
                            if not self.fsm.transition_to(transition_state):
                                self.logger.error(f"상태 전환 실패: {transition_state}")
                                break
                    
                    iteration += 1
                    time.sleep(0.1)  # CPU 사용률 조절
                
                # 시간 제한으로 종료된 경우
                if time.time() - start_time >= max_runtime_minutes * 60:
                    self.logger.info(f"⏰ {max_runtime_minutes}분 시간 제한으로 자동화 종료")
            
            # 제한된 실행
            limited_run()
            
        except KeyboardInterrupt:
            print("\n⏹️ 사용자에 의해 자동화가 중단되었습니다")
        except Exception as e:
            print(f"❌ 자동화 중 오류 발생: {e}")
            self.logger.error(f"자동화 실행 오류: {e}")
        finally:
            self.fsm.stop()
            return self._get_execution_summary()
    
    def _get_execution_summary(self) -> Dict[str, Any]:
        """실행 결과 요약"""
        metrics = self.fsm.get_metrics()
        shared_data = self.fsm_context.shared_data
        
        execution_time = time.time() - shared_data.get("session_start_time", time.time())
        
        summary = {
            "execution_time_seconds": execution_time,
            "execution_time_formatted": f"{execution_time/60:.1f}분",
            "total_state_transitions": metrics["state_transitions"],
            "successful_actions": shared_data.get("successful_actions", 0),
            "failed_actions": shared_data.get("failed_actions", 0),
            "cafe_rewards_collected": shared_data.get("cafe_rewards_collected", 0),
            "final_state": metrics.get("current_state", "UNKNOWN"),
            "average_state_duration": metrics.get("average_state_duration", 0),
            "last_clicked_element": shared_data.get("last_clicked", "none")
        }
        
        self._print_summary(summary)
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]):
        """실행 결과 출력"""
        print("\n" + "=" * 50)
        print("📊 자동화 실행 결과")
        print("=" * 50)
        print(f"총 실행 시간: {summary['execution_time_formatted']}")
        print(f"상태 전환 횟수: {summary['total_state_transitions']}회")
        print(f"성공한 액션: {summary['successful_actions']}개")
        print(f"실패한 액션: {summary['failed_actions']}개")
        print(f"최종 상태: {summary['final_state']}")
        print(f"평균 상태 지속 시간: {summary['average_state_duration']:.1f}초")
        
        # 카페 보상 수집 결과
        if summary['cafe_rewards_collected'] > 0:
            print(f"🎉 카페 보상 수집: {summary['cafe_rewards_collected']}개")
            
        # 효율성 계산
        if summary['execution_time_seconds'] > 0:
            actions_per_minute = (summary['successful_actions'] * 60) / summary['execution_time_seconds']
            print(f"⚡ 액션 효율성: {actions_per_minute:.1f}회/분")
            
        # 성공률 계산
        total_actions = summary['successful_actions'] + summary['failed_actions']
        if total_actions > 0:
            success_rate = (summary['successful_actions'] / total_actions) * 100
            print(f"✅ 성공률: {success_rate:.1f}%")
    
    def get_current_status(self) -> Dict[str, Any]:
        """현재 상태 정보 반환"""
        fsm_summary = self.fsm.get_state_summary()
        process_running = self.process_detector.is_game_running()
        
        if process_running:
            game_state = self.state_detector.detect_current_state()
            return {
                "fsm_running": fsm_summary["running"],
                "current_fsm_state": fsm_summary["current_state"],
                "process_running": True,
                "game_state": game_state.state.value,
                "game_confidence": game_state.confidence,
                "total_transitions": fsm_summary["total_transitions"],
                "shared_data": dict(self.fsm_context.shared_data)
            }
        else:
            return {
                "fsm_running": fsm_summary["running"],
                "current_fsm_state": fsm_summary["current_state"],
                "process_running": False,
                "game_state": "unknown",
                "game_confidence": 0.0,
                "total_transitions": fsm_summary["total_transitions"],
                "shared_data": dict(self.fsm_context.shared_data)
            }
    
    def stop_automation(self):
        """자동화 중단"""
        self.logger.info("🛑 자동화 중단 요청됨")
        self.fsm.stop()
    
    def reset_automation(self):
        """자동화 상태 리셋"""
        self.logger.info("🔄 자동화 상태 리셋")
        self.fsm.stop()
        
        # 공유 데이터 리셋
        self.fsm_context.shared_data = {
            "cafe_rewards_collected": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "last_clicked": "",
            "session_start_time": time.time()
        }
        
        # 메트릭 리셋
        self.fsm.metrics = {
            "state_transitions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "total_runtime": 0.0
        }


def create_fsm_automation() -> FSMAutomationUseCase:
    """FSM 자동화 유스케이스 팩토리"""
    return FSMAutomationUseCase()


if __name__ == "__main__":
    """FSM 자동화 실행"""
    automation = create_fsm_automation()
    
    print("🎮 블루아카이브 FSM 자동화")
    print("=" * 40)
    
    # 현재 상태 확인
    status = automation.get_current_status()
    print(f"게임 프로세스: {status['process_running']}")
    print(f"게임 상태: {status['game_state']}")
    print(f"FSM 실행 중: {status['fsm_running']}")
    
    if status['process_running']:
        print("\n🚀 FSM 자동화를 시작합니다...")
        print("Ctrl+C로 언제든 중단할 수 있습니다")
        
        # 자동화 실행 (30분 제한)
        result = automation.start_automation("IDLE", max_runtime_minutes=30)
        
        if result['successful_actions'] > 0:
            print(f"\n🎉 자동화 완료! 총 {result['successful_actions']}개 액션 성공")
        else:
            print("\n😞 성공한 액션이 없습니다. 게임 상태를 확인해주세요.")
    else:
        print("\n❌ 게임을 먼저 실행해주세요.")
        print("블루아카이브 게임이 실행되면 자동으로 감지됩니다.")