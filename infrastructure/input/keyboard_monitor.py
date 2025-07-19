"""
키보드 입력 모니터링
"""
import threading
from abc import ABC, abstractmethod
from pynput import keyboard
import config


class KeyboardMonitor(ABC):
    """키보드 모니터링 인터페이스"""
    
    @abstractmethod
    def start_monitoring(self, exit_callback):
        """키보드 모니터링 시작"""
        pass
    
    @abstractmethod
    def stop_monitoring(self):
        """키보드 모니터링 중지"""
        pass


class PynputKeyboardMonitor(KeyboardMonitor):
    """Pynput 기반 키보드 모니터링 구현체"""
    
    def __init__(self):
        self.listener = None
        self.exit_callback = None
        self.is_monitoring = False
        
    def _parse_exit_key(self, exit_key_str: str):
        """종료 키 문자열을 파싱하여 키 조합 반환"""
        keys = exit_key_str.lower().split('+')
        parsed_keys = []
        
        for key in keys:
            key = key.strip()
            if key == 'ctrl':
                parsed_keys.append(keyboard.Key.ctrl_l)
            elif key == 'alt':
                parsed_keys.append(keyboard.Key.alt_l)
            elif key == 'shift':
                parsed_keys.append(keyboard.Key.shift_l)
            elif key == 'esc':
                parsed_keys.append(keyboard.Key.esc)
            elif len(key) == 1:
                parsed_keys.append(keyboard.KeyCode.from_char(key))
            else:
                # 기타 특수 키들
                try:
                    parsed_keys.append(getattr(keyboard.Key, key))
                except AttributeError:
                    parsed_keys.append(keyboard.KeyCode.from_char(key))
        
        return parsed_keys
    
    def _on_key_press(self, key):
        """키 입력 이벤트 처리"""
        if not self.is_monitoring:
            return
            
        try:
            # 현재 누른 키가 종료 키 조합에 포함되는지 확인
            exit_keys = self._parse_exit_key(config.EXIT_KEY)
            
            # 단일 키 확인
            if len(exit_keys) == 1 and key == exit_keys[0]:
                if config.DEBUG_MODE:
                    print(f"Exit key pressed: {config.EXIT_KEY}")
                self._trigger_exit()
                
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Key press error: {e}")
    
    def _on_key_combination(self, key):
        """키 조합 확인 (Ctrl+Q 등)"""
        exit_keys = self._parse_exit_key(config.EXIT_KEY)
        
        if len(exit_keys) > 1:
            # 복합키 조합 처리는 pynput의 GlobalHotKeys 사용
            pass
    
    def _trigger_exit(self):
        """종료 콜백 실행"""
        if self.exit_callback:
            self.exit_callback()
    
    def start_monitoring(self, exit_callback):
        """키보드 모니터링 시작"""
        self.exit_callback = exit_callback
        self.is_monitoring = True
        
        if config.DEBUG_MODE:
            print(f"키보드 모니터링 시작. 종료키: {config.EXIT_KEY}")
        
        # 복합키 조합 처리
        if '+' in config.EXIT_KEY:
            self._start_hotkey_monitoring()
        else:
            self._start_simple_key_monitoring()
    
    def _start_simple_key_monitoring(self):
        """단일 키 모니터링"""
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()
    
    def _start_hotkey_monitoring(self):
        """핫키 조합 모니터링"""
        try:
            # GlobalHotKeys 사용하여 키 조합 처리
            hotkeys = {config.EXIT_KEY: self._trigger_exit}
            self.listener = keyboard.GlobalHotKeys(hotkeys)
            self.listener.start()
            
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Hotkey monitoring error: {e}")
            # 폴백: 단순 키 모니터링
            self._start_simple_key_monitoring()
    
    def stop_monitoring(self):
        """키보드 모니터링 중지"""
        self.is_monitoring = False
        
        if self.listener:
            self.listener.stop()
            self.listener = None
            
        if config.DEBUG_MODE:
            print("키보드 모니터링 중지")