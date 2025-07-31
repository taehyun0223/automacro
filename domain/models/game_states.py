"""
확장된 게임 상태 정의
FSM에서 사용할 블루아카이브 게임의 모든 상태를 정의
"""

from enum import Enum
from typing import Dict, List


class ExtendedGameState(Enum):
    """확장된 게임 상태 열거형"""
    # System States
    IDLE = "idle"                    # 대기 상태 (게임 미실행)
    UNKNOWN = "unknown"              # 알 수 없는 상태
    ERROR = "error"                  # 오류 상태
    
    # Game Process States  
    LAUNCHING = "launching"          # 게임 시작 중
    LOADING = "loading"              # 로딩 화면
    MAINTENANCE = "maintenance"      # 점검 중
    
    # Main Game States
    IN_HOME = "in_home"             # 홈 화면 (메인 메뉴)
    IN_CAFE = "in_cafe"             # 카페 화면
    IN_MENU = "in_menu"             # 각종 메뉴 화면
    IN_BATTLE = "in_battle"         # 전투 화면
    IN_STORY = "in_story"           # 스토리 화면
    IN_SHOP = "in_shop"             # 상점 화면
    IN_INVENTORY = "in_inventory"   # 인벤토리 화면
    
    # Special States
    DIALOG_OPEN = "dialog_open"     # 다이얼로그 창 열림
    REWARD_POPUP = "reward_popup"   # 보상 팝업
    CONNECTION_ERROR = "conn_error" # 연결 오류


# 상태별 전환 규칙 매트릭스
TRANSITION_RULES = {
    ExtendedGameState.IDLE: {
        "game_window_detected.png": ExtendedGameState.LAUNCHING,
        "blue_archive_title.png": ExtendedGameState.LOADING
    },
    
    ExtendedGameState.LOADING: {
        "home_button.png": ExtendedGameState.IN_HOME,
        "maintenance_notice.png": ExtendedGameState.MAINTENANCE,
        "connection_error.png": ExtendedGameState.CONNECTION_ERROR,
        # 타임아웃 조건 (30초)
        "_timeout": ExtendedGameState.ERROR
    },
    
    ExtendedGameState.IN_HOME: {
        "cafe_button.png": ExtendedGameState.IN_CAFE,        # 카페 버튼 클릭 시
        "battle_button.png": ExtendedGameState.IN_BATTLE,    # 전투 버튼 클릭 시  
        "shop_button.png": ExtendedGameState.IN_SHOP,        # 상점 버튼 클릭 시
        "menu_button.png": ExtendedGameState.IN_MENU,        # 메뉴 버튼 클릭 시
        "reward_popup.png": ExtendedGameState.REWARD_POPUP,  # 보상 팝업 시
        "dialog_box.png": ExtendedGameState.DIALOG_OPEN      # 다이얼로그 시
    },
    
    ExtendedGameState.IN_CAFE: {
        "cafe_reward.png": ExtendedGameState.REWARD_POPUP,   # 카페 보상 발견 시
        "collect_all_button.png": ExtendedGameState.REWARD_POPUP,
        "home_button.png": ExtendedGameState.IN_HOME,        # 홈 버튼 클릭 시
        "back_button.png": ExtendedGameState.IN_HOME,        # 뒤로가기 시
        "_no_action_timeout": ExtendedGameState.IN_HOME      # 액션 없이 20초 경과
    },
    
    ExtendedGameState.REWARD_POPUP: {
        "collect_all_button.png": ExtendedGameState.IN_CAFE, # 일괄 수집 후
        "close_button.png": ExtendedGameState.IN_CAFE,       # 팝업 닫기 후
        "x_button.png": ExtendedGameState.IN_CAFE,           # X 버튼 클릭 후
        "_auto_collect_complete": ExtendedGameState.IN_CAFE  # 자동 수집 완료 후
    },
    
    ExtendedGameState.DIALOG_OPEN: {
        "confirm_button.png": ExtendedGameState.IN_HOME,     # 확인 버튼
        "cancel_button.png": ExtendedGameState.IN_HOME,      # 취소 버튼
        "close_dialog.png": ExtendedGameState.IN_HOME        # 다이얼로그 닫기
    }
}


# 상태별 액션 정의
STATE_ACTIONS = {
    ExtendedGameState.IDLE: {
        "primary_action": "wait_for_game_launch",
        "resources_to_find": [],
        "fallback_actions": [
            {"condition": "game_not_found_30s", "action": "notify_user_launch_game"}
        ],
        "periodic_checks": ["check_game_process_every_5s"]
    },
    
    ExtendedGameState.LOADING: {
        "primary_action": "wait_for_load_complete", 
        "resources_to_find": ["home_button.png", "main_menu_indicator.png"],
        "fallback_actions": [
            {"condition": "loading_timeout_30s", "action": "restart_game_detection"},
            {"condition": "maintenance_detected", "action": "wait_maintenance_end"},
            {"condition": "error_popup_detected", "action": "handle_error_popup"}
        ],
        "periodic_checks": ["check_loading_progress_every_2s"]
    },
    
    ExtendedGameState.IN_HOME: {
        "primary_action": "scan_available_actions",
        "resources_to_find": [
            "cafe_button.png",           # 1순위: 카페 
            "daily_mission_button.png",  # 2순위: 일일 미션
            "event_button.png",          # 3순위: 이벤트
            "shop_button.png"            # 4순위: 상점
        ],
        "fallback_actions": [
            {"condition": "no_targets_found", "action": "take_screenshot_and_wait"},
            {"condition": "popup_detected", "action": "handle_popup"},
            {"condition": "reward_notification", "action": "collect_rewards"}
        ],
        "periodic_checks": ["scan_for_notifications_every_3s"],
        "priority_logic": "cafe_first_then_missions"
    },
    
    ExtendedGameState.IN_CAFE: {
        "primary_action": "collect_cafe_rewards",
        "resources_to_find": [
            "cafe_reward.png",           # 1순위: 수집 가능한 보상
            "collect_all_button.png",    # 2순위: 일괄 수집 버튼  
            "revenue_number.png",        # 3순위: 수익 확인
            "cafe_student_interaction.png" # 4순위: 학생 상호작용
        ],
        "fallback_actions": [
            {"condition": "no_rewards_available", "action": "check_cafe_upgrades"},
            {"condition": "cafe_full", "action": "expand_cafe_or_return_home"},
            {"condition": "student_interaction_available", "action": "interact_with_students"}
        ],
        "periodic_checks": ["check_reward_respawn_every_10s"],
        "auto_return_home": "after_all_actions_complete_or_60s"
    },
    
    ExtendedGameState.REWARD_POPUP: {
        "primary_action": "collect_all_rewards",
        "resources_to_find": [
            "collect_all_button.png",    # 1순위: 일괄 수집
            "collect_button.png",        # 2순위: 개별 수집
            "next_button.png",           # 3순위: 다음 보상
            "close_button.png"           # 4순위: 팝업 닫기  
        ],
        "fallback_actions": [
            {"condition": "collect_button_not_found", "action": "click_empty_space_to_close"},
            {"condition": "multiple_popups", "action": "handle_popup_sequence"},
            {"condition": "inventory_full", "action": "expand_inventory_or_skip"}
        ],
        "periodic_checks": ["check_popup_changes_every_1s"],
        "max_wait_time": 15
    },
    
    ExtendedGameState.DIALOG_OPEN: {
        "primary_action": "handle_dialog_appropriately", 
        "resources_to_find": [
            "confirm_button.png",        # 확인 버튼
            "cancel_button.png",         # 취소 버튼
            "yes_button.png",            # 예 버튼
            "no_button.png"              # 아니오 버튼
        ],
        "fallback_actions": [
            {"condition": "unknown_dialog", "action": "take_screenshot_and_default_confirm"},
            {"condition": "warning_dialog", "action": "carefully_choose_safe_option"},
            {"condition": "purchase_dialog", "action": "cancel_unless_intended"}
        ],
        "decision_logic": "analyze_dialog_content_for_safe_choice"
    },
    
    ExtendedGameState.ERROR: {
        "primary_action": "diagnose_and_recover",
        "resources_to_find": [
            "retry_button.png",
            "reconnect_button.png", 
            "home_button.png"
        ],
        "fallback_actions": [
            {"condition": "connection_error", "action": "wait_and_retry_connection"},
            {"condition": "game_crash", "action": "restart_game_detection"},
            {"condition": "unknown_error", "action": "notify_user_and_reset"}
        ],
        "recovery_sequence": ["wait_5s", "retry_detection", "escalate_if_persistent"]
    }
}


# 컨텍스트 기반 리소스 선택 로직
RESOURCE_SELECTION_LOGIC = {
    ExtendedGameState.IN_HOME: {
        "if_morning": ["morning_bonus.png", "daily_mission.png", "cafe_button.png"],
        "if_evening": ["cafe_button.png", "battle_button.png", "shop_button.png"],
        "if_event_active": ["event_banner.png", "limited_time.png", "cafe_button.png"],
        "default": ["cafe_button.png", "daily_mission.png", "shop_button.png"]
    },
    
    ExtendedGameState.IN_CAFE: {
        "if_rewards_available": ["cafe_reward.png", "collect_all_button.png"],
        "if_no_rewards": ["upgrade_cafe.png", "interact_student.png", "home_button.png"],
        "if_full_storage": ["expand_button.png", "sell_items.png", "home_button.png"]
    }
}


def get_state_priority_resources(state: ExtendedGameState, context: str = "default") -> List[str]:
    """상태와 컨텍스트에 따른 우선순위 리소스 반환"""
    if state in RESOURCE_SELECTION_LOGIC:
        logic = RESOURCE_SELECTION_LOGIC[state]
        return logic.get(context, logic.get("default", []))
    
    if state in STATE_ACTIONS:
        return STATE_ACTIONS[state].get("resources_to_find", [])
    
    return []


def get_state_transitions(state: ExtendedGameState) -> Dict[str, ExtendedGameState]:
    """상태의 전환 규칙 반환"""
    return TRANSITION_RULES.get(state, {})


def get_state_actions(state: ExtendedGameState) -> Dict[str, any]:
    """상태의 액션 정의 반환"""
    return STATE_ACTIONS.get(state, {})