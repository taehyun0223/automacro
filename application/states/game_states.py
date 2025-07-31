"""
블루아카이브 게임별 상태 구현
각 상태별 구체적인 동작과 전환 로직을 정의
"""

from domain.models.finite_state_machine import FSMState, StateAction, StateTransitionRule, StateTransitionTriggerType
from domain.models.game_states import ExtendedGameState
from domain.models.image_region import ImageRegion
import time
import logging


class IdleState(FSMState):
    """대기 상태 - 게임이 실행되지 않은 상태"""
    
    def on_enter(self):
        self.logger.info("🔄 IDLE 상태 진입 - 게임 실행 대기 중")
        
        # 게임 프로세스 감지 시 전환
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.CONDITION_MET,
            trigger_value="game_process_detected",
            target_state="LOADING",
            condition_check=lambda: self.context.process_detector.is_game_running()
        ))
        
        # 30초 대기 후 재확인
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.TIMEOUT,
            trigger_value="30",
            target_state="IDLE",  # 자기 자신으로 재전환 (재확인)
            priority=0
        ))
    
    def execute(self):
        # 주기적으로 게임 프로세스 확인
        if self.context.process_detector.is_game_running():
            self.logger.info("✅ 게임 프로세스 감지됨!")
            return "LOADING"
        
        self.logger.info("⏳ 게임 실행 대기중... (30초마다 확인)")
        time.sleep(5)
        return None
    
    def on_exit(self):
        self.logger.info("✅ 게임 프로세스 감지됨 - IDLE 상태 종료")


class LoadingState(FSMState):
    """로딩 상태 - 게임 로딩 화면 처리"""
    
    def on_enter(self):
        self.logger.info("⏳ LOADING 상태 진입 - 게임 로딩 대기")
        
        # 홈 화면 감지 시 전환
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.CONDITION_MET,
            trigger_value="home_screen_detected",
            target_state="IN_HOME",
            condition_check=self._is_home_screen_ready
        ))
        
        # 30초 타임아웃
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.TIMEOUT,
            trigger_value="30",
            target_state="ERROR",
            priority=0
        ))
    
    def _is_home_screen_ready(self) -> bool:
        """홈 화면 준비 상태 확인"""
        try:
            result = self.context.state_detector.detect_current_state()
            from infrastructure.screen.game_state_detector import GameState
            return result.state == GameState.MAIN_MENU and result.confidence > 0.7
        except Exception as e:
            self.logger.error(f"홈 화면 감지 오류: {e}")
            return False
    
    def execute(self):
        # 게임 상태 확인
        if self._is_home_screen_ready():
            self.logger.info("🏠 홈 화면 감지됨!")
            return "IN_HOME"
        
        self.logger.info("⏳ 로딩 중... 홈 화면 대기")
        time.sleep(2)
        return None
    
    def on_exit(self):
        self.logger.info("✅ 로딩 완료 - LOADING 상태 종료")


class HomeState(FSMState):
    """홈 상태 - 메인 메뉴 화면"""
    
    def on_enter(self):
        self.logger.info("🏠 HOME 상태 진입 - 메인 메뉴에서 작업 수행")
        
        # 우선순위별 액션 설정
        self.add_action(StateAction(
            action_type="find_and_click_priority",
            target_resources=[
                "cafe_button.png",           # 최우선: 카페
                "daily_mission_button.png",  # 2순위: 일일 미션
                "event_notification.png",    # 3순위: 이벤트
                "shop_button.png"            # 4순위: 상점
            ],
            max_attempts=3,
            timeout=15.0
        ))
        
        # 카페 진입 감지
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.CONDITION_MET,
            trigger_value="cafe_screen_detected",
            target_state="IN_CAFE",
            condition_check=self._is_cafe_screen
        ))
        
        # 보상 팝업 감지 시 전환
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.IMAGE_DETECTED,
            trigger_value="reward_popup.png",
            target_state="REWARD_POPUP",
            priority=2  # 높은 우선순위
        ))
        
        # 60초 후 재시작 (무한 루프 방지)
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.TIMEOUT,
            trigger_value="60",
            target_state="IN_HOME",
            priority=0
        ))
    
    def _is_cafe_screen(self) -> bool:
        """카페 화면 진입 확인"""
        try:
            result = self.context.state_detector.detect_current_state()
            from infrastructure.screen.game_state_detector import GameState
            return result.state == GameState.CAFE and result.confidence > 0.6
        except Exception:
            return False
    
    def execute(self):
        # 홈 화면에서 우선순위별 액션 수행
        for action in self.actions:
            if action.action_type == "find_and_click_priority":
                for resource in action.target_resources:
                    try:
                        # 이미지 영역 생성
                        region = ImageRegion(
                            name=resource.replace('.png', ''),
                            image_path=f"assets/{resource}",
                            confidence=0.7
                        )
                        
                        location = self.context.image_locator.find_image(region)
                        if location:
                            self.logger.info(f"🎯 {resource} 발견 - 클릭 실행")
                            success = self.context.clicker.click(location)
                            if success:
                                self.context.shared_data["last_clicked"] = resource
                                self.context.shared_data["successful_actions"] = \
                                    self.context.shared_data.get("successful_actions", 0) + 1
                                time.sleep(3)  # 화면 전환 대기
                                return None  # 전환 규칙에서 처리
                            else:
                                self.context.shared_data["failed_actions"] = \
                                    self.context.shared_data.get("failed_actions", 0) + 1
                    except Exception as e:
                        self.logger.error(f"{resource} 처리 중 오류: {e}")
                
                # 아무것도 찾지 못한 경우
                self.logger.warning("⚠️ 홈 화면에서 액션 가능한 요소를 찾지 못함")
                time.sleep(3)
                return None
        
        return None
    
    def on_exit(self):
        last_clicked = self.context.shared_data.get("last_clicked", "unknown")
        self.logger.info(f"🚪 HOME 상태 종료 (마지막 클릭: {last_clicked})")


class CafeState(FSMState):
    """카페 상태 - 카페에서 보상 수집"""
    
    def on_enter(self):
        self.logger.info("☕ CAFE 상태 진입 - 카페 보상 수집 시작")
        
        # 카페 보상 수집 액션
        self.add_action(StateAction(
            action_type="collect_cafe_rewards",
            target_resources=[
                "cafe_reward.png",
                "collect_all_button.png", 
                "revenue_indicator.png"
            ],
            fallback_resources=[
                "cafe_student.png",  # 학생과 상호작용
                "cafe_furniture.png"  # 가구 배치
            ],
            max_attempts=5,
            timeout=30.0
        ))
        
        # 보상 팝업으로 전환
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.IMAGE_DETECTED,
            trigger_value="reward_collection_popup.png",
            target_state="REWARD_POPUP"
        ))
        
        # 60초 후 또는 할 일이 없으면 홈으로 복귀
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.TIMEOUT,
            trigger_value="60",
            target_state="IN_HOME",
            priority=0
        ))
        
        # 홈 버튼 감지시 즉시 복귀
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.IMAGE_DETECTED,
            trigger_value="home_button.png",
            target_state="IN_HOME",
            priority=1
        ))
    
    def execute(self):
        # 카페 보상 수집 로직
        rewards_collected = 0
        
        for attempt in range(5):  # 최대 5번 시도
            try:
                # 수집 가능한 보상 찾기
                reward_region = ImageRegion(
                    name="cafe_reward",
                    image_path="assets/cafe_reward.png",
                    confidence=0.6
                )
                
                reward_location = self.context.image_locator.find_image(reward_region)
                
                if reward_location:
                    self.logger.info(f"💰 카페 보상 발견 (시도 {attempt + 1}/5)")
                    success = self.context.clicker.click(reward_location)
                    if success:
                        rewards_collected += 1
                        self.context.shared_data["cafe_rewards_collected"] = rewards_collected
                        time.sleep(1.5)  # 수집 애니메이션 대기
                    else:
                        break
                else:
                    # 일괄 수집 버튼 찾기
                    collect_all_region = ImageRegion(
                        name="collect_all",
                        image_path="assets/collect_all_button.png",
                        confidence=0.7
                    )
                    
                    collect_all_location = self.context.image_locator.find_image(collect_all_region)
                    if collect_all_location:
                        self.logger.info("📦 일괄 수집 버튼 클릭")
                        self.context.clicker.click(collect_all_location)
                        time.sleep(2)
                        break
                    else:
                        self.logger.info("✅ 카페에서 수집할 보상이 없음")
                        break
            except Exception as e:
                self.logger.error(f"카페 보상 수집 중 오류: {e}")
                break
        
        if rewards_collected > 0:
            self.logger.info(f"🎉 카페 보상 {rewards_collected}개 수집 완료")
        
        # 추가 작업이 없으면 홈으로 복귀 준비
        time.sleep(2)
        return "IN_HOME"
    
    def on_exit(self):
        rewards = self.context.shared_data.get("cafe_rewards_collected", 0)
        self.logger.info(f"🚪 CAFE 상태 종료 (총 {rewards}개 보상 수집)")


class RewardPopupState(FSMState):
    """보상 팝업 상태 - 각종 보상 팝업 처리"""
    
    def on_enter(self):
        self.logger.info("🎁 REWARD_POPUP 상태 진입 - 보상 팝업 처리")
        
        # 보상 수집 액션
        self.add_action(StateAction(
            action_type="collect_popup_rewards",
            target_resources=[
                "collect_all_button.png",
                "collect_button.png",
                "confirm_button.png",
                "close_button.png"
            ],
            max_attempts=3,
            timeout=10.0
        ))
        
        # 팝업 종료 후 이전 상태로 복귀
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.IMAGE_NOT_FOUND,
            trigger_value="reward_popup.png",
            target_state="IN_CAFE",  # 기본적으로 카페로 복귀
            confidence_threshold=0.5
        ))
        
        # 15초 타임아웃
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.TIMEOUT,
            trigger_value="15",
            target_state="IN_CAFE",
            priority=0
        ))
    
    def execute(self):
        # 팝업의 보상 수집 처리
        for resource in ["collect_all_button.png", "collect_button.png", "confirm_button.png"]:
            try:
                region = ImageRegion(
                    name=resource.replace('.png', ''),
                    image_path=f"assets/{resource}",
                    confidence=0.7
                )
                
                location = self.context.image_locator.find_image(region)
                if location:
                    self.logger.info(f"🔘 {resource} 클릭")
                    self.context.clicker.click(location)
                    time.sleep(1.5)
                    return None  # 전환 조건에서 다음 상태 결정
            except Exception as e:
                self.logger.error(f"{resource} 처리 중 오류: {e}")
        
        # 닫기 버튼으로 팝업 종료
        try:
            close_region = ImageRegion(
                name="close_button",
                image_path="assets/close_button.png",
                confidence=0.7
            )
            
            close_location = self.context.image_locator.find_image(close_region)
            if close_location:
                self.logger.info("❌ 팝업 닫기")
                self.context.clicker.click(close_location)
                time.sleep(1)
        except Exception as e:
            self.logger.error(f"팝업 닫기 중 오류: {e}")
        
        return None
    
    def on_exit(self):
        self.logger.info("🚪 REWARD_POPUP 상태 종료")


class ErrorState(FSMState):
    """오류 상태 - 오류 발생 시 복구 처리"""
    
    def on_enter(self):
        self.logger.warning("❌ ERROR 상태 진입 - 오류 복구 시작")
        
        # 5초 후 IDLE로 복귀 (재시작)
        self.add_transition_rule(StateTransitionRule(
            trigger_type=StateTransitionTriggerType.TIMEOUT,
            trigger_value="5",
            target_state="IDLE"
        ))
    
    def execute(self):
        self.logger.warning("🔄 오류 복구 중... 5초 후 재시작")
        time.sleep(5)
        return "IDLE"
    
    def on_exit(self):
        self.logger.info("🔄 ERROR 상태 종료 - 시스템 재시작")