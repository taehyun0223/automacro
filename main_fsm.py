"""
블루아카이브 FSM 기반 자동화 매크로 메인 실행 파일
기존 시스템과 새로운 FSM 시스템을 모두 지원
"""

from infrastructure.input.keyboard_monitor import PynputKeyboardMonitor
from application.usecases.macro_loop_usecase import BlueArchiveMacroLoopUseCase
from application.usecases.cafe_automation_usecase import CafeAutomationUseCase
from application.usecases.fsm_automation_usecase import FSMAutomationUseCase
import sys


def show_menu():
    """메뉴 표시"""
    print("=" * 60)
    print("🎮 블루아카이브 자동화 매크로 (FSM Enhanced)")
    print("=" * 60)
    print("📚 기존 자동화:")
    print("1. 🏠 카페 자동화 (단일 실행)")
    print("2. 🔄 전체 매크로 루프 (연속 실행)")
    print()
    print("🧠 FSM 기반 자동화 (권장):")
    print("3. 🤖 FSM 자동화 - 스마트 모드 (30분)")
    print("4. ⚡ FSM 자동화 - 빠른 모드 (10분)")
    print("5. 🎯 FSM 자동화 - 카페 전용 모드")
    print()
    print("📊 정보 및 관리:")
    print("6. 📊 현재 상태 확인")
    print("7. 🔍 FSM 상태 확인")
    print("8. ❌ 종료")
    print("-" * 60)


def run_cafe_automation():
    """기존 카페 자동화 실행"""
    automation = CafeAutomationUseCase()
    
    print("\n🏠 기존 카페 자동화를 실행합니다...")
    success = automation.execute()
    
    if success:
        print("🎉 카페 자동화 완료!")
    else:
        print("😞 카페 자동화 실패")
    
    input("\nEnter를 눌러 메뉴로 돌아가세요...")


def run_full_macro():
    """기존 전체 매크로 루프 실행"""
    print("\n🔄 기존 전체 매크로 루프를 시작합니다...")
    print("Ctrl+Q로 언제든 종료할 수 있습니다.")
    
    try:
        keyboard_monitor = PynputKeyboardMonitor()
        macro_loop = BlueArchiveMacroLoopUseCase(keyboard_monitor)
        macro_loop.run()
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 매크로가 중단되었습니다.")


def run_fsm_automation_smart():
    """FSM 스마트 자동화 (30분)"""
    print("\n🤖 FSM 스마트 자동화 모드 (30분)")
    print("이 모드는 게임 상태를 지능적으로 감지하고 최적의 액션을 수행합니다.")
    print()
    
    automation = FSMAutomationUseCase()
    result = automation.start_automation("IDLE", max_runtime_minutes=30)
    
    print("\n" + "="*50)
    print("🎉 FSM 스마트 자동화 완료!")
    print(f"실행 시간: {result['execution_time_formatted']}")
    print(f"성공한 액션: {result['successful_actions']}개")
    if result['cafe_rewards_collected'] > 0:
        print(f"카페 보상: {result['cafe_rewards_collected']}개 수집")
    print("="*50)
    
    input("\nEnter를 눌러 메뉴로 돌아가세요...")


def run_fsm_automation_quick():
    """FSM 빠른 자동화 (10분)"""
    print("\n⚡ FSM 빠른 자동화 모드 (10분)")
    print("빠른 카페 보상 수집에 최적화된 모드입니다.")
    print()
    
    automation = FSMAutomationUseCase()
    result = automation.start_automation("IDLE", max_runtime_minutes=10)
    
    print("\n" + "="*50)
    print("⚡ FSM 빠른 자동화 완료!")
    print(f"실행 시간: {result['execution_time_formatted']}")
    print(f"성공한 액션: {result['successful_actions']}개")
    if result['cafe_rewards_collected'] > 0:
        print(f"카페 보상: {result['cafe_rewards_collected']}개 수집")
    print("="*50)
    
    input("\nEnter를 눌러 메뉴로 돌아가세요...")


def run_fsm_cafe_only():
    """FSM 카페 전용 모드"""
    print("\n🎯 FSM 카페 전용 모드")
    print("카페 보상 수집에만 집중하는 모드입니다.")
    print()
    
    automation = FSMAutomationUseCase()
    
    # 카페 전용 설정 적용
    automation.fsm_context.config.update({
        "cafe_focus_mode": True,
        "skip_other_activities": True,
        "max_cafe_cycles": 3
    })
    
    # 게임이 실행 중이면 홈에서 시작, 아니면 IDLE에서 시작
    status = automation.get_current_status()
    initial_state = "IN_HOME" if status['process_running'] else "IDLE"
    
    result = automation.start_automation(initial_state, max_runtime_minutes=15)
    
    print("\n" + "="*50)
    print("🎯 FSM 카페 전용 자동화 완료!")
    print(f"실행 시간: {result['execution_time_formatted']}")
    if result['cafe_rewards_collected'] > 0:
        print(f"카페 보상: {result['cafe_rewards_collected']}개 수집")
    else:
        print("수집된 카페 보상이 없습니다.")
    print("="*50)
    
    input("\nEnter를 눌러 메뉴로 돌아가세요...")


def check_status():
    """기존 시스템 상태 확인"""
    automation = CafeAutomationUseCase()
    status = automation.get_status()
    
    print("\n📊 기존 시스템 상태:")
    print(f"게임 프로세스 실행: {'✅' if status['process_running'] else '❌'}")
    print(f"게임 상태: {status['game_state']}")
    print(f"신뢰도: {status['confidence']:.2f}")
    print(f"카페 자동화 준비: {'✅' if status['ready_for_cafe'] else '❌'}")
    
    input("\nEnter를 눌러 메뉴로 돌아가세요...")


def check_fsm_status():
    """FSM 시스템 상태 확인"""
    automation = FSMAutomationUseCase()
    status = automation.get_current_status()
    
    print("\n🔍 FSM 시스템 상태:")
    print("=" * 40)
    print(f"FSM 실행 중: {'✅' if status['fsm_running'] else '❌'}")
    print(f"현재 FSM 상태: {status['current_fsm_state'] or 'None'}")
    print(f"게임 프로세스: {'✅' if status['process_running'] else '❌'}")
    print(f"게임 상태: {status['game_state']}")
    print(f"게임 상태 신뢰도: {status['game_confidence']:.2f}")
    print(f"총 상태 전환 횟수: {status['total_transitions']}")
    
    if status['shared_data']:
        print("\n📈 세션 통계:")
        shared = status['shared_data']
        print(f"성공한 액션: {shared.get('successful_actions', 0)}개")
        print(f"실패한 액션: {shared.get('failed_actions', 0)}개")
        print(f"카페 보상 수집: {shared.get('cafe_rewards_collected', 0)}개")
        if shared.get('last_clicked'):
            print(f"마지막 클릭: {shared['last_clicked']}")
    
    input("\nEnter를 눌러 메뉴로 돌아가세요...")


def show_startup_info():
    """시작 정보 표시"""
    print("🔧 시작하기 전에 확인사항:")
    print("1. 블루아카이브 게임이 실행되어 있어야 합니다")
    print("2. assets/ 폴더에 필요한 이미지 파일들이 있어야 합니다")
    print("   - cafe_button.png (카페 버튼)")
    print("   - cafe_reward.png (카페 보상)")
    print("   - collect_all_button.png (일괄 수집 버튼)")
    print("3. 게임 화면이 보이는 상태여야 합니다")
    print()
    print("💡 권장사항:")
    print("- FSM 기반 자동화(옵션 3-5)를 사용하면 더 안정적이고 지능적인 자동화가 가능합니다")
    print("- 처음 사용하시는 경우 '빠른 모드(옵션 4)'를 추천합니다")
    print()


def main():
    """메인 실행 함수"""
    show_startup_info()
    
    while True:
        try:
            show_menu()
            choice = input("선택하세요 (1-8): ").strip()
            
            if choice == '1':
                run_cafe_automation()
            elif choice == '2':
                run_full_macro()
                break  # 매크로 루프 종료 후 프로그램 종료
            elif choice == '3':
                run_fsm_automation_smart()
            elif choice == '4':
                run_fsm_automation_quick()
            elif choice == '5':
                run_fsm_cafe_only()
            elif choice == '6':
                check_status()
            elif choice == '7':
                check_fsm_status()
            elif choice == '8':
                print("👋 프로그램을 종료합니다.")
                break
            else:
                print("❌ 잘못된 선택입니다. 1-8 중에서 선택해주세요.")
                input("Enter를 눌러 계속...")
                
        except KeyboardInterrupt:
            print("\n⏹️ 사용자에 의해 프로그램이 중단되었습니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류가 발생했습니다: {e}")
            print("디버깅을 위해 오류 세부사항:")
            import traceback
            traceback.print_exc()
            input("Enter를 눌러 계속...")


if __name__ == "__main__":
    main()