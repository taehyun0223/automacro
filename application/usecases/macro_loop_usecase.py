"""
매크로 루프 유스케이스
"""
import time
import threading
from typing import List, Callable
from abc import ABC, abstractmethod

from domain.models.image_region import MacroResult
from infrastructure.input.keyboard_monitor import KeyboardMonitor
import config


class MacroUseCase(ABC):
    """매크로 유스케이스 인터페이스"""
    
    @abstractmethod
    def execute(self) -> MacroResult:
        """매크로 실행"""
        pass


class BlueArchiveMacroLoopUseCase:
    """블루아카이브 매크로 루프 제어 유스케이스"""
    
    def __init__(self, keyboard_monitor: KeyboardMonitor):
        self.keyboard_monitor = keyboard_monitor
        self.macros: List[MacroUseCase] = []
        self.is_running = False
        self.should_exit = False
        
    def add_macro(self, macro: MacroUseCase):
        """매크로 추가"""
        self.macros.append(macro)
        
    def remove_macro(self, macro: MacroUseCase):
        """매크로 제거"""
        if macro in self.macros:
            self.macros.remove(macro)
    
    def clear_macros(self):
        """모든 매크로 제거"""
        self.macros.clear()
    
    def _on_exit_key_pressed(self):
        """종료 키 입력 시 호출되는 콜백"""
        if config.DEBUG_MODE:
            print("종료 키가 눌렸습니다. 매크로를 종료합니다...")
        self.should_exit = True
    
    def _execute_macro_cycle(self):
        """한 사이클의 매크로 실행"""
        if not self.macros:
            if config.DEBUG_MODE:
                print("실행할 매크로가 없습니다")
            return
        
        for i, macro in enumerate(self.macros):
            if self.should_exit:
                break
                
            try:
                if config.DEBUG_MODE:
                    print(f"매크로 {i+1}/{len(self.macros)} 실행 중...")
                
                result = macro.execute()
                
                if config.DEBUG_MODE:
                    status = "성공" if result.success else "실패"
                    print(f"매크로 {i+1} {status}: {result.message}")
                    
                # 매크로 간 대기
                if not self.should_exit and i < len(self.macros) - 1:
                    time.sleep(config.LOOP_DELAY)
                    
            except Exception as e:
                if config.DEBUG_MODE:
                    print(f"매크로 {i+1} 실행 중 오류: {e}")
                continue
    
    def start(self):
        """매크로 루프 시작"""
        if self.is_running:
            print("매크로가 이미 실행 중입니다")
            return
        
        if not self.macros:
            print("실행할 매크로가 없습니다")
            return
        
        self.is_running = True
        self.should_exit = False
        
        if config.DEBUG_MODE:
            print(f"매크로 루프 시작 (매크로 {len(self.macros)}개)")
            print(f"종료하려면 {config.EXIT_KEY}를 누르세요")
        
        # 키보드 모니터링 시작
        self.keyboard_monitor.start_monitoring(self._on_exit_key_pressed)
        
        try:
            while not self.should_exit:
                self._execute_macro_cycle()
                
                # 사이클 간 대기 (종료 신호 확인)
                if not self.should_exit:
                    for _ in range(int(config.LOOP_DELAY * 10)):
                        if self.should_exit:
                            break
                        time.sleep(0.1)
        
        except KeyboardInterrupt:
            if config.DEBUG_MODE:
                print("\\nCtrl+C로 매크로 종료")
        
        finally:
            self.stop()
    
    def stop(self):
        """매크로 루프 중지"""
        if not self.is_running:
            return
        
        self.should_exit = True
        self.is_running = False
        
        # 키보드 모니터링 중지
        self.keyboard_monitor.stop_monitoring()
        
        if config.DEBUG_MODE:
            print("매크로 루프 종료")
    
    def is_running_status(self) -> bool:
        """매크로 실행 상태 확인"""
        return self.is_running


class SequentialMacroUseCase:
    """여러 매크로를 순차적으로 실행하는 유스케이스"""
    
    def __init__(self, macros: List[MacroUseCase]):
        self.macros = macros
    
    def execute(self) -> MacroResult:
        """모든 매크로 순차 실행"""
        all_results = []
        all_clicked_positions = []
        
        for i, macro in enumerate(self.macros):
            try:
                result = macro.execute()
                all_results.append(result)
                all_clicked_positions.extend(result.clicked_positions)
                
                if config.DEBUG_MODE:
                    print(f"순차 매크로 {i+1}: {result.message}")
                
                # 매크로 간 짧은 대기
                if i < len(self.macros) - 1:
                    time.sleep(1.0)
                    
            except Exception as e:
                error_result = MacroResult(
                    success=False,
                    message=f"순차 매크로 {i+1} 실행 오류: {e}"
                )
                all_results.append(error_result)
        
        # 전체 결과 취합
        success_count = sum(1 for result in all_results if result.success)
        total_count = len(all_results)
        
        overall_success = success_count > 0
        overall_message = f"순차 매크로 완료: {success_count}/{total_count} 성공"
        
        return MacroResult(
            success=overall_success,
            message=overall_message,
            clicked_positions=all_clicked_positions
        )