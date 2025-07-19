import time
import pygetwindow as gw
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class WindowInfo:
    """윈도우 정보"""
    title: str
    handle: int
    x: int
    y: int
    width: int
    height: int
    is_active: bool
    is_minimized: bool
    is_maximized: bool


class WindowManager(ABC):
    """윈도우 관리 인터페이스"""
    
    @abstractmethod
    def find_game_window(self) -> Optional[WindowInfo]:
        """게임 윈도우 찾기"""
        pass
    
    @abstractmethod
    def activate_window(self, window_info: WindowInfo) -> bool:
        """윈도우 활성화"""
        pass
    
    @abstractmethod
    def resize_window(self, window_info: WindowInfo, width: int, height: int) -> bool:
        """윈도우 크기 조정"""
        pass


class GameWindowManager(WindowManager):
    """블루아카이브 게임 윈도우 관리자"""
    
    def __init__(self, window_titles: List[str] = None):
        """
        Args:
            window_titles: 감지할 윈도우 타이틀 패턴 목록
        """
        self.window_titles = window_titles or [
            "Blue Archive",
            "블루 아카이브", 
            "ブルーアーカイブ",
            "BlueArchive",
            "블루아카이브"
        ]
        
        # 제외할 윈도우 패턴들
        self.exclude_patterns = [
            "MINGW64",
            "cmd",
            "powershell", 
            "terminal",
            "Downloads",
            "BluearchiveAuto"
        ]
        
    def find_game_window(self) -> Optional[WindowInfo]:
        """게임 윈도우 찾기
        
        Returns:
            Optional[WindowInfo]: 발견된 게임 윈도우 정보
        """
        try:
            all_windows = gw.getAllWindows()
            
            for window in all_windows:
                if self._is_game_window(window.title):
                    return self._create_window_info(window)
                    
            return None
            
        except Exception as e:
            print(f"윈도우 검색 중 오류 발생: {e}")
            return None
    
    def find_all_game_windows(self) -> List[WindowInfo]:
        """모든 게임 윈도우 찾기
        
        Returns:
            List[WindowInfo]: 발견된 모든 게임 윈도우 정보
        """
        game_windows = []
        
        try:
            all_windows = gw.getAllWindows()
            
            for window in all_windows:
                if self._is_game_window(window.title):
                    window_info = self._create_window_info(window)
                    if window_info:
                        game_windows.append(window_info)
                        
        except Exception as e:
            print(f"윈도우 검색 중 오류 발생: {e}")
            
        return game_windows
    
    def activate_window(self, window_info: WindowInfo) -> bool:
        """윈도우 활성화
        
        Args:
            window_info: 활성화할 윈도우 정보
            
        Returns:
            bool: 활성화 성공 여부
        """
        try:
            # pygetwindow로 윈도우 객체 다시 찾기
            windows = gw.getWindowsWithTitle(window_info.title)
            
            if not windows:
                print(f"윈도우를 찾을 수 없음: {window_info.title}")
                return False
            
            target_window = windows[0]
            
            # 최소화된 경우 복원
            if window_info.is_minimized:
                try:
                    target_window.restore()
                    time.sleep(0.5)
                except Exception as restore_error:
                    print(f"윈도우 복원 중 오류 (무시): {restore_error}")
            
            # 윈도우 활성화 - 여러 방법 시도
            activation_success = False
            
            # 방법 1: pygetwindow activate
            try:
                target_window.activate()
                time.sleep(0.2)
                activation_success = True
            except Exception as activate_error:
                print(f"activate() 실패 (다른 방법 시도): {activate_error}")
            
            # 방법 2: 포커스 설정
            if not activation_success:
                try:
                    import win32gui
                    import win32con
                    
                    hwnd = target_window._hWnd if hasattr(target_window, '_hWnd') else None
                    if hwnd:
                        # 윈도우를 앞으로 가져오기
                        win32gui.SetForegroundWindow(hwnd)
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        activation_success = True
                        print("win32gui를 통한 활성화 성공")
                except ImportError:
                    print("win32gui를 사용할 수 없음")
                except Exception as win32_error:
                    print(f"win32gui 활성화 실패: {win32_error}")
            
            # 방법 3: 단순 클릭으로 활성화
            if not activation_success:
                try:
                    # 윈도우 중앙 클릭
                    center_x = window_info.x + window_info.width // 2
                    center_y = window_info.y + window_info.height // 2
                    
                    import pyautogui
                    pyautogui.click(center_x, center_y)
                    time.sleep(0.2)
                    activation_success = True
                    print("클릭을 통한 활성화 시도")
                except Exception as click_error:
                    print(f"클릭 활성화 실패: {click_error}")
            
            return activation_success
            
        except Exception as e:
            print(f"윈도우 활성화 중 치명적 오류: {e}")
            return False
    
    def resize_window(self, window_info: WindowInfo, width: int, height: int) -> bool:
        """윈도우 크기 조정
        
        Args:
            window_info: 크기를 조정할 윈도우 정보
            width: 새로운 너비
            height: 새로운 높이
            
        Returns:
            bool: 크기 조정 성공 여부
        """
        try:
            windows = gw.getWindowsWithTitle(window_info.title)
            
            if not windows:
                print(f"윈도우를 찾을 수 없음: {window_info.title}")
                return False
            
            target_window = windows[0]
            target_window.resizeTo(width, height)
            
            return True
            
        except Exception as e:
            print(f"윈도우 크기 조정 중 오류 발생: {e}")
            return False
    
    def move_window(self, window_info: WindowInfo, x: int, y: int) -> bool:
        """윈도우 위치 이동
        
        Args:
            window_info: 이동할 윈도우 정보
            x: 새로운 X 좌표
            y: 새로운 Y 좌표
            
        Returns:
            bool: 이동 성공 여부
        """
        try:
            windows = gw.getWindowsWithTitle(window_info.title)
            
            if not windows:
                print(f"윈도우를 찾을 수 없음: {window_info.title}")
                return False
            
            target_window = windows[0]
            target_window.moveTo(x, y)
            
            return True
            
        except Exception as e:
            print(f"윈도우 이동 중 오류 발생: {e}")
            return False
    
    def wait_for_window(self, timeout: int = 60) -> Optional[WindowInfo]:
        """게임 윈도우 나타날 때까지 대기
        
        Args:
            timeout: 대기 시간 (초)
            
        Returns:
            Optional[WindowInfo]: 발견된 윈도우 정보
        """
        start_time = time.time()
        
        print(f"게임 윈도우를 기다리는 중... (최대 {timeout}초)")
        
        while time.time() - start_time < timeout:
            window = self.find_game_window()
            if window:
                print(f"게임 윈도우 발견: {window.title}")
                return window
            
            time.sleep(1)
            
        print(f"{timeout}초 동안 게임 윈도우가 발견되지 않았습니다.")
        return None
    
    def ensure_window_ready(self, target_resolution: Tuple[int, int] = (1920, 1080)) -> Optional[WindowInfo]:
        """게임 윈도우를 매크로 실행 가능한 상태로 준비
        
        Args:
            target_resolution: 목표 해상도 (width, height)
            
        Returns:
            Optional[WindowInfo]: 준비된 윈도우 정보
        """
        window = self.find_game_window()
        
        if not window:
            print("게임 윈도우를 찾을 수 없습니다.")
            return None
        
        # 윈도우 활성화
        if not self.activate_window(window):
            print("윈도우 활성화에 실패했습니다.")
            return None
        
        # 해상도 조정
        target_width, target_height = target_resolution
        if window.width != target_width or window.height != target_height:
            print(f"윈도우 크기 조정: {window.width}x{window.height} -> {target_width}x{target_height}")
            if not self.resize_window(window, target_width, target_height):
                print("윈도우 크기 조정에 실패했습니다.")
                return None
        
        # 윈도우 정보 갱신
        updated_window = self.find_game_window()
        if updated_window:
            print(f"게임 윈도우 준비 완료: {updated_window.title} ({updated_window.width}x{updated_window.height})")
        
        return updated_window
    
    def get_window_details(self) -> Dict[str, Any]:
        """게임 윈도우 상세 정보 반환
        
        Returns:
            Dict[str, Any]: 윈도우 상세 정보
        """
        windows = self.find_all_game_windows()
        
        if not windows:
            return {
                "found": False,
                "window_count": 0,
                "windows": [],
                "active_window": None
            }
        
        # 활성 윈도우 찾기
        active_window = None
        for window in windows:
            if window.is_active:
                active_window = window
                break
        
        return {
            "found": True,
            "window_count": len(windows),
            "windows": [
                {
                    "title": w.title,
                    "handle": w.handle,
                    "position": f"{w.x}, {w.y}",
                    "size": f"{w.width}x{w.height}",
                    "active": w.is_active,
                    "minimized": w.is_minimized,
                    "maximized": w.is_maximized
                }
                for w in windows
            ],
            "active_window": {
                "title": active_window.title,
                "size": f"{active_window.width}x{active_window.height}",
                "position": f"{active_window.x}, {active_window.y}"
            } if active_window else None
        }
    
    def _is_game_window(self, window_title: str) -> bool:
        """윈도우 타이틀이 게임 윈도우인지 확인
        
        Args:
            window_title: 윈도우 타이틀
            
        Returns:
            bool: 게임 윈도우 여부
        """
        if not window_title or len(window_title.strip()) == 0:
            return False
        
        window_title_lower = window_title.lower()
        
        # 제외 패턴 확인
        for exclude_pattern in self.exclude_patterns:
            if exclude_pattern.lower() in window_title_lower:
                return False
        
        # 게임 타이틀 패턴 확인
        for title_pattern in self.window_titles:
            if title_pattern.lower() in window_title_lower:
                return True
                
        return False
    
    def _create_window_info(self, window) -> Optional[WindowInfo]:
        """pygetwindow 윈도우 객체를 WindowInfo로 변환
        
        Args:
            window: pygetwindow 윈도우 객체
            
        Returns:
            Optional[WindowInfo]: 변환된 윈도우 정보
        """
        try:
            return WindowInfo(
                title=window.title,
                handle=window._hWnd if hasattr(window, '_hWnd') else 0,
                x=window.left,
                y=window.top,
                width=window.width,
                height=window.height,
                is_active=window.isActive,
                is_minimized=window.isMinimized,
                is_maximized=window.isMaximized
            )
        except Exception as e:
            print(f"윈도우 정보 생성 중 오류: {e}")
            return None


def create_window_manager() -> GameWindowManager:
    """게임 윈도우 관리자 팩토리 함수
    
    Returns:
        GameWindowManager: 게임 윈도우 관리자 인스턴스
    """
    return GameWindowManager()


if __name__ == "__main__":
    # 테스트용 실행
    manager = create_window_manager()
    
    print("=== 블루아카이브 윈도우 관리 테스트 ===")
    
    # 윈도우 찾기
    window = manager.find_game_window()
    if window:
        print(f"게임 윈도우 발견: {window.title}")
        print(f"크기: {window.width}x{window.height}")
        print(f"위치: ({window.x}, {window.y})")
        print(f"활성화됨: {window.is_active}")
        print(f"최소화됨: {window.is_minimized}")
        
        # 윈도우 활성화 테스트
        print("\n윈도우 활성화 시도...")
        if manager.activate_window(window):
            print("윈도우 활성화 성공!")
        else:
            print("윈도우 활성화 실패!")
            
        # 윈도우 준비 테스트
        print("\n윈도우 준비 시도...")
        ready_window = manager.ensure_window_ready((1920, 1080))
        if ready_window:
            print("윈도우 준비 완료!")
        else:
            print("윈도우 준비 실패!")
    else:
        print("게임 윈도우를 찾을 수 없습니다.")
    
    # 상세 정보 출력
    details = manager.get_window_details()
    print(f"\n윈도우 상세 정보:")
    print(f"발견됨: {details['found']}")
    print(f"윈도우 수: {details['window_count']}")
    
    if details['active_window']:
        active = details['active_window']
        print(f"활성 윈도우: {active['title']} ({active['size']})")