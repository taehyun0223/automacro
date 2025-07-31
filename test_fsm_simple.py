"""
FSM 시스템 간단 테스트 스크립트
"""

import sys
from application.usecases.fsm_automation_usecase import FSMAutomationUseCase


def test_basic_functionality():
    """기본 기능 테스트"""
    print("=== FSM 기본 기능 테스트 ===")
    
    try:
        # FSM 인스턴스 생성
        automation = FSMAutomationUseCase()
        print("[OK] FSM 인스턴스 생성 성공")
        
        # 상태 등록 확인
        expected_states = ["IDLE", "LOADING", "IN_HOME", "IN_CAFE", "REWARD_POPUP", "ERROR"]
        registered_states = list(automation.fsm.states.keys())
        
        print(f"등록된 상태들: {registered_states}")
        
        missing = [s for s in expected_states if s not in registered_states]
        if missing:
            print(f"[FAIL] 누락된 상태: {missing}")
            return False
        
        print("[OK] 모든 상태가 정상 등록됨")
        
        # 컨텍스트 확인
        if automation.fsm_context.image_locator is None:
            print("[FAIL] image_locator가 없음")
            return False
        
        if automation.fsm_context.clicker is None:
            print("[FAIL] clicker가 없음")
            return False
            
        print("[OK] 모든 컴포넌트가 정상 주입됨")
        
        # 상태 확인 메소드 테스트
        status = automation.get_current_status()
        required_keys = ["fsm_running", "process_running", "game_state"]
        
        for key in required_keys:
            if key not in status:
                print(f"[FAIL] 상태 정보에 {key} 키가 없음")
                return False
        
        print("[OK] 상태 확인 메소드 정상 동작")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("FSM 시스템 테스트 시작")
    print("="*40)
    
    if test_basic_functionality():
        print("\n=== 테스트 결과 ===")
        print("[SUCCESS] 모든 기본 테스트 통과!")
        print("FSM 시스템이 정상적으로 구현되었습니다.")
        return True
    else:
        print("\n=== 테스트 결과 ===")
        print("[FAILED] 일부 테스트 실패")
        print("구현을 다시 확인해주세요.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)