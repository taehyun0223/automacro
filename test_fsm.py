"""
FSM 시스템 테스트 스크립트
FSM 구현이 올바르게 동작하는지 기본적인 테스트 수행
"""

import sys
import time
from application.usecases.fsm_automation_usecase import FSMAutomationUseCase


def test_fsm_initialization():
    """FSM 초기화 테스트"""
    print("[TEST] FSM 초기화 테스트...")
    
    try:
        automation = FSMAutomationUseCase()
        print("[OK] FSM 초기화 성공")
        
        # 등록된 상태들 확인
        registered_states = list(automation.fsm.states.keys())
        print(f"등록된 상태들: {registered_states}")
        
        expected_states = ["IDLE", "LOADING", "IN_HOME", "IN_CAFE", "REWARD_POPUP", "ERROR"]
        missing_states = [state for state in expected_states if state not in registered_states]
        
        if missing_states:
            print(f"[FAIL] 누락된 상태들: {missing_states}")
            return False
        else:
            print("[OK] 모든 필요한 상태가 등록됨")
            return True
            
    except Exception as e:
        print(f"[FAIL] FSM 초기화 실패: {e}")
        return False


def test_state_transitions():
    """상태 전환 로직 테스트"""
    print("\n🔄 상태 전환 테스트...")
    
    try:
        automation = FSMAutomationUseCase()
        
        # IDLE 상태로 시작
        automation.fsm.set_initial_state("IDLE")
        current_state = automation.fsm.current_state
        
        if current_state and current_state.state_name == "IDLE":
            print("✅ 초기 상태 설정 성공: IDLE")
        else:
            print("❌ 초기 상태 설정 실패")
            return False
        
        # 상태 전환 테스트 (ERROR -> IDLE)
        print("ERROR 상태로 전환 테스트...")
        success = automation.fsm.transition_to("ERROR")
        
        if success and automation.fsm.current_state.state_name == "ERROR":
            print("✅ ERROR 상태 전환 성공")
        else:
            print("❌ ERROR 상태 전환 실패")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 상태 전환 테스트 실패: {e}")
        return False


def test_context_data():
    """컨텍스트 데이터 테스트"""
    print("\n📊 컨텍스트 데이터 테스트...")
    
    try:
        automation = FSMAutomationUseCase()
        
        # 공유 데이터 테스트
        automation.fsm_context.shared_data["test_key"] = "test_value"
        
        if automation.fsm_context.shared_data.get("test_key") == "test_value":
            print("✅ 공유 데이터 읽기/쓰기 성공")
        else:
            print("❌ 공유 데이터 읽기/쓰기 실패")
            return False
        
        # 설정 데이터 테스트
        config_keys = ["max_cafe_attempts", "reward_collection_timeout", "auto_return_home"]
        missing_config = [key for key in config_keys if key not in automation.fsm_context.config]
        
        if missing_config:
            print(f"❌ 누락된 설정: {missing_config}")
            return False
        else:
            print("✅ 모든 설정 키가 존재함")
        
        return True
        
    except Exception as e:
        print(f"❌ 컨텍스트 데이터 테스트 실패: {e}")
        return False


def test_component_integration():
    """컴포넌트 통합 테스트"""
    print("\n🔗 컴포넌트 통합 테스트...")
    
    try:
        automation = FSMAutomationUseCase()
        
        # 필요한 컴포넌트들이 모두 있는지 확인
        components = {
            "process_detector": automation.process_detector,
            "state_detector": automation.state_detector,
            "image_locator": automation.image_locator,
            "clicker": automation.clicker
        }
        
        for name, component in components.items():
            if component is None:
                print(f"❌ {name} 컴포넌트가 없음")
                return False
            else:
                print(f"✅ {name} 컴포넌트 존재")
        
        # FSM 컨텍스트에 모든 컴포넌트가 주입되었는지 확인
        context = automation.fsm_context
        if (context.process_detector and context.state_detector and 
            context.image_locator and context.clicker):
            print("✅ FSM 컨텍스트에 모든 컴포넌트 주입됨")
        else:
            print("❌ FSM 컨텍스트 의존성 주입 실패")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 컴포넌트 통합 테스트 실패: {e}")
        return False


def test_status_methods():
    """상태 확인 메소드 테스트"""
    print("\n📋 상태 확인 메소드 테스트...")
    
    try:
        automation = FSMAutomationUseCase()
        
        # get_current_status 테스트
        status = automation.get_current_status()
        required_keys = ["fsm_running", "current_fsm_state", "process_running", 
                        "game_state", "total_transitions", "shared_data"]
        
        missing_keys = [key for key in required_keys if key not in status]
        if missing_keys:
            print(f"❌ 상태 정보에 누락된 키: {missing_keys}")
            return False
        else:
            print("✅ 상태 정보 구조 정상")
        
        # FSM 메트릭 테스트
        metrics = automation.fsm.get_metrics()
        metric_keys = ["state_transitions", "successful_actions", "failed_actions", "total_runtime"]
        
        missing_metrics = [key for key in metric_keys if key not in metrics]
        if missing_metrics:
            print(f"❌ 메트릭에 누락된 키: {missing_metrics}")
            return False
        else:
            print("✅ FSM 메트릭 구조 정상")
        
        return True
        
    except Exception as e:
        print(f"❌ 상태 확인 메소드 테스트 실패: {e}")
        return False


def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 FSM 시스템 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("FSM 초기화", test_fsm_initialization),
        ("상태 전환", test_state_transitions),
        ("컨텍스트 데이터", test_context_data),
        ("컴포넌트 통합", test_component_integration),
        ("상태 확인 메소드", test_status_methods)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} 테스트 {'='*20}")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 테스트 통과")
            else:
                failed += 1
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
    
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")
    print(f"총 테스트: {passed + failed}개")
    
    if failed == 0:
        print("🎉 모든 테스트 통과! FSM 시스템이 정상적으로 구현되었습니다.")
        return True
    else:
        print(f"⚠️ {failed}개 테스트 실패. 구현을 다시 확인해주세요.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)