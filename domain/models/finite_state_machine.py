"""
고급 유한 상태 머신 (Finite State Machine) 구현
이미지 기반 상태 전환과 조건부 액션을 지원하는 게임 자동화 FSM
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Union
import time
import logging
from datetime import datetime, time as dt_time


class StateTransitionTriggerType(Enum):
    """상태 전환 트리거 타입"""
    IMAGE_DETECTED = "image_detected"        # 특정 이미지 감지됨
    IMAGE_NOT_FOUND = "image_not_found"      # 특정 이미지 찾을 수 없음  
    TIMEOUT = "timeout"                      # 시간 초과
    CONDITION_MET = "condition_met"          # 조건 충족
    USER_ACTION = "user_action"              # 사용자 액션
    ERROR_OCCURRED = "error_occurred"        # 오류 발생


@dataclass
class StateTransitionRule:
    """상태 전환 규칙"""
    trigger_type: StateTransitionTriggerType
    trigger_value: str                       # 이미지 파일명 또는 조건명
    target_state: str                        # 대상 상태명
    confidence_threshold: float = 0.7
    wait_time: float = 0.0                   # 전환 전 대기 시간
    condition_check: Optional[Callable[[], bool]] = None
    priority: int = 1                        # 높을수록 우선순위 높음


@dataclass  
class StateAction:
    """상태별 액션 정의"""
    action_type: str                         # "find_and_click", "wait", "scan", etc.
    target_resources: List[str] = field(default_factory=list)  # 찾을 리소스들
    fallback_resources: List[str] = field(default_factory=list)  # 대체 리소스들
    action_function: Optional[Callable] = None
    max_attempts: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FSMContext:
    """FSM 컨텍스트 (의존성 주입)"""
    image_locator: Any                       # OpenCVImageLocator 인스턴스
    clicker: Any                            # PyAutoGuiScreenClicker 인스턴스  
    state_detector: Any                     # BlueArchiveStateDetector 인스턴스
    process_detector: Any                   # GameProcessDetector 인스턴스
    config: Dict[str, Any] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)


class FSMState(ABC):
    """FSM 상태 추상 클래스"""
    
    def __init__(self, state_name: str, fsm_context: FSMContext):
        self.state_name = state_name
        self.context = fsm_context
        self.entry_time = time.time()
        self.actions: List[StateAction] = []
        self.transition_rules: List[StateTransitionRule] = []
        self.logger = logging.getLogger(f"FSM.{state_name}")
    
    @abstractmethod
    def on_enter(self) -> None:
        """상태 진입 시 실행"""
        pass
    
    @abstractmethod  
    def execute(self) -> Optional[str]:
        """상태 실행 로직, 다음 상태 반환 (None이면 현재 상태 유지)"""
        pass
    
    @abstractmethod
    def on_exit(self) -> None:
        """상태 종료 시 실행"""
        pass
    
    def add_transition_rule(self, rule: StateTransitionRule):
        """전환 규칙 추가"""
        self.transition_rules.append(rule)
        self.transition_rules.sort(key=lambda x: x.priority, reverse=True)
    
    def add_action(self, action: StateAction):
        """액션 추가"""
        self.actions.append(action)
    
    def check_transitions(self) -> Optional[str]:
        """전환 조건 확인"""
        for rule in self.transition_rules:
            if self._evaluate_transition_rule(rule):
                self.logger.info(f"전환 조건 충족: {rule.trigger_value} -> {rule.target_state}")
                if rule.wait_time > 0:
                    time.sleep(rule.wait_time)
                return rule.target_state
        return None
    
    def _evaluate_transition_rule(self, rule: StateTransitionRule) -> bool:
        """전환 규칙 평가"""
        try:
            if rule.trigger_type == StateTransitionTriggerType.IMAGE_DETECTED:
                from domain.models.image_region import ImageRegion
                region = ImageRegion(
                    name=rule.trigger_value,
                    image_path=f"assets/{rule.trigger_value}",
                    confidence=rule.confidence_threshold
                )
                result = self.context.image_locator.find_image(region)
                return result is not None
                
            elif rule.trigger_type == StateTransitionTriggerType.IMAGE_NOT_FOUND:
                from domain.models.image_region import ImageRegion
                region = ImageRegion(
                    name=rule.trigger_value,
                    image_path=f"assets/{rule.trigger_value}",
                    confidence=rule.confidence_threshold
                )
                result = self.context.image_locator.find_image(region)
                return result is None
                
            elif rule.trigger_type == StateTransitionTriggerType.TIMEOUT:
                return time.time() - self.entry_time > float(rule.trigger_value)
                
            elif rule.trigger_type == StateTransitionTriggerType.CONDITION_MET:
                return rule.condition_check() if rule.condition_check else False
                
        except Exception as e:
            self.logger.error(f"전환 규칙 평가 중 오류: {e}")
            return False
        
        return False


class GameStateMachine:
    """게임 상태 머신 메인 클래스"""
    
    def __init__(self, context: FSMContext):
        self.context = context
        self.current_state: Optional[FSMState] = None
        self.states: Dict[str, FSMState] = {}
        self.state_history: List[tuple] = []  # (state_name, timestamp, duration)
        self.is_running = False
        self.logger = logging.getLogger("GameStateMachine")
        
        # 성능 메트릭
        self.metrics = {
            "state_transitions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "total_runtime": 0.0
        }
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def register_state(self, state_name: str, state_class: type) -> None:
        """상태 등록"""
        state_instance = state_class(state_name, self.context)
        self.states[state_name] = state_instance
        self.logger.info(f"상태 등록: {state_name}")
    
    def set_initial_state(self, state_name: str) -> None:
        """초기 상태 설정"""
        if state_name in self.states:
            self.current_state = self.states[state_name]
            self.current_state.entry_time = time.time()
            self.current_state.on_enter()
            self.logger.info(f"초기 상태 설정: {state_name}")
        else:
            raise ValueError(f"상태를 찾을 수 없음: {state_name}")
    
    def transition_to(self, state_name: str) -> bool:
        """특정 상태로 전환"""
        if state_name not in self.states:
            self.logger.error(f"상태를 찾을 수 없음: {state_name}")
            return False
        
        if self.current_state:
            # 현재 상태 히스토리 기록
            duration = time.time() - self.current_state.entry_time
            self.state_history.append((
                self.current_state.state_name, 
                self.current_state.entry_time,
                duration
            ))
            
            self.current_state.on_exit()
        
        # 새 상태로 전환
        old_state = self.current_state.state_name if self.current_state else "None"
        self.current_state = self.states[state_name]
        self.current_state.entry_time = time.time()
        self.current_state.on_enter()
        
        self.metrics["state_transitions"] += 1
        self.logger.info(f"상태 전환: {old_state} -> {state_name}")
        return True
    
    def run(self, max_iterations: int = 1000) -> None:
        """FSM 실행"""
        if not self.current_state:
            raise RuntimeError("초기 상태가 설정되지 않음")
        
        self.is_running = True
        start_time = time.time()
        iteration = 0
        
        self.logger.info("FSM 실행 시작")
        
        try:
            while self.is_running and iteration < max_iterations:
                iteration += 1
                
                # 현재 상태 실행
                next_state = self.current_state.execute()
                
                # 전환 조건 확인 (상태 실행 결과 우선)
                if next_state:
                    transition_state = next_state
                else:
                    transition_state = self.current_state.check_transitions()
                
                # 상태 전환
                if transition_state and transition_state != self.current_state.state_name:
                    if not self.transition_to(transition_state):
                        self.logger.error(f"상태 전환 실패: {transition_state}")
                        break
                
                # 짧은 대기 (CPU 사용률 조절)
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("사용자에 의해 FSM 중단됨")
        except Exception as e:
            self.logger.error(f"FSM 실행 중 오류: {e}")
        finally:
            self.is_running = False
            self.metrics["total_runtime"] = time.time() - start_time
            self.logger.info(f"FSM 종료 (총 {iteration}회 반복, {self.metrics['total_runtime']:.2f}초)")
    
    def stop(self) -> None:
        """FSM 중단"""
        self.is_running = False
        self.logger.info("FSM 중단 요청됨")
    
    def get_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 반환"""
        return {
            **self.metrics,
            "current_state": self.current_state.state_name if self.current_state else None,
            "state_history_count": len(self.state_history),
            "average_state_duration": sum(h[2] for h in self.state_history) / len(self.state_history) if self.state_history else 0
        }
    
    def get_state_summary(self) -> Dict[str, Any]:
        """상태 요약 정보 반환"""
        return {
            "current_state": self.current_state.state_name if self.current_state else None,
            "running": self.is_running,
            "registered_states": list(self.states.keys()),
            "total_transitions": self.metrics["state_transitions"],
            "runtime": self.metrics["total_runtime"]
        }