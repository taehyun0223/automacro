"""
블루아카이브 일일퀘스트 매크로 메인 실행 파일
"""

from infrastructure.input.keyboard_monitor import PynputKeyboardMonitor
from application.usecases.macro_loop_usecase import BlueArchiveMacroLoopUseCase
from application.usecases.cafe_automation_usecase import CafeAutomationUseCase


def show_menu():
    """메뉴 표시"""
    print("=" * 50)
    print("🎮 블루아카이브 자동화 매크로")
    print("=" * 50)
    print("1. 🏠 카페 접근 (단일 실행)")
    print("2. 💰 카페 접근 + 수익 수령 (단일 실행)")
    print("3. 🔄 전체 매크로 루프 (연속 실행)")
    print("4. 📊 현재 상태 확인")
    print("5. ❌ 종료")
    print("-" * 50)


def run_cafe_automation():
    """카페 접근 자동화 실행"""
    automation = CafeAutomationUseCase(collect_revenue=False)
    
    print("\n🏠 카페 접근을 실행합니다...")
    success = automation.execute()
    
    if success:
        print("🎉 카페 접근 완료!")
    else:
        print("😞 카페 접근 실패")
    
    input("\nEnter를 눌러 메뉴로 돌아가세요...")


def run_cafe_with_revenue():
    """카페 접근 + 수익 수령 자동화 실행"""
    automation = CafeAutomationUseCase(collect_revenue=True)
    
    print("\n💰 카페 접근 + 수익 수령을 실행합니다...")
    print("⚠️ 카페 수익 및 수령 버튼 템플릿이 필요합니다")
    print("   없다면 create_revenue_templates.py를 먼저 실행하세요")
    
    success = automation.execute()
    
    if success:
        print("🎉 카페 자동화 완료!")
    else:
        print("😞 카페 자동화 실패")
    
    input("\nEnter를 눌러 메뉴로 돌아가세요...")


def run_full_macro():
    """전체 매크로 루프 실행"""
    print("\n🔄 전체 매크로 루프를 시작합니다...")
    print("Ctrl+Q로 언제든 종료할 수 있습니다.")
    
    try:
        keyboard_monitor = PynputKeyboardMonitor()
        macro_loop = BlueArchiveMacroLoopUseCase(keyboard_monitor)
        macro_loop.run()
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 매크로가 중단되었습니다.")


def check_status():
    """현재 상태 확인"""
    automation = CafeAutomationUseCase()
    status = automation.get_status()
    
    print("\n📊 현재 상태:")
    print(f"게임 프로세스 실행: {'✅' if status['process_running'] else '❌'}")
    print(f"게임 상태: {status['game_state']}")
    print(f"신뢰도: {status['confidence']:.2f}")
    print(f"카페 자동화 준비: {'✅' if status['ready_for_cafe'] else '❌'}")
    
    input("\nEnter를 눌러 메뉴로 돌아가세요...")


def main():
    """메인 실행 함수"""
    print("🔧 시작하기 전에 확인사항:")
    print("1. 블루아카이브 게임이 실행되어 있어야 합니다")
    print("2. assets/ 폴더에 필요한 이미지 파일들이 있어야 합니다")
    print("3. 게임 화면이 보이는 상태여야 합니다")
    print()
    
    while True:
        try:
            show_menu()
            choice = input("선택하세요 (1-5): ").strip()
            
            if choice == '1':
                run_cafe_automation()
            elif choice == '2':
                run_cafe_with_revenue()
            elif choice == '3':
                run_full_macro()
                break  # 매크로 루프 종료 후 프로그램 종료
            elif choice == '4':
                check_status()
            elif choice == '5':
                print("👋 프로그램을 종료합니다.")
                break
            else:
                print("❌ 잘못된 선택입니다. 1-5 중에서 선택해주세요.")
                input("Enter를 눌러 계속...")
                
        except KeyboardInterrupt:
            print("\n⏹️ 사용자에 의해 프로그램이 중단되었습니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류가 발생했습니다: {e}")
            input("Enter를 눌러 계속...")


if __name__ == "__main__":
    main()