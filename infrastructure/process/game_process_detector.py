import psutil
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class ProcessInfo:
    """게임 프로세스 정보"""
    pid: int
    name: str
    exe_path: str
    create_time: float
    memory_usage: int


class ProcessDetector(ABC):
    """프로세스 감지 인터페이스"""
    
    @abstractmethod
    def is_game_running(self) -> bool:
        """게임이 실행 중인지 확인"""
        pass
    
    @abstractmethod
    def get_game_processes(self) -> List[ProcessInfo]:
        """게임 프로세스 목록 반환"""
        pass
    
    @abstractmethod
    def wait_for_game(self, timeout: int = 60) -> bool:
        """게임 실행까지 대기"""
        pass


class GameProcessDetector(ProcessDetector):
    """블루아카이브 게임 프로세스 감지기"""
    
    def __init__(self, process_names: List[str] = None):
        """
        Args:
            process_names: 감지할 프로세스명 목록
        """
        self.process_names = process_names or [
            "BlueArchive.exe",
            "BlueArchiveClient.exe", 
            "BlueArchiveLauncher.exe",
            "Blue Archive.exe",
            "블루아카이브.exe"
        ]
        
    def is_game_running(self) -> bool:
        """게임이 실행 중인지 확인
        
        Returns:
            bool: 게임 실행 여부
        """
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name and self._is_game_process(proc_name):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            print(f"프로세스 확인 중 오류 발생: {e}")
            return False
    
    def get_game_processes(self) -> List[ProcessInfo]:
        """게임 프로세스 목록 반환
        
        Returns:
            List[ProcessInfo]: 발견된 게임 프로세스 정보 목록
        """
        game_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'memory_info']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name']
                    
                    if proc_name and self._is_game_process(proc_name):
                        memory_info = proc_info.get('memory_info')
                        memory_usage = 0
                        if memory_info:
                            try:
                                memory_usage = memory_info.rss if hasattr(memory_info, 'rss') else 0
                            except AttributeError:
                                memory_usage = 0
                        
                        process_info = ProcessInfo(
                            pid=proc_info['pid'],
                            name=proc_name,
                            exe_path=proc_info.get('exe', ''),
                            create_time=proc_info.get('create_time', 0),
                            memory_usage=memory_usage
                        )
                        game_processes.append(process_info)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"프로세스 정보 수집 중 오류 발생: {e}")
            
        return game_processes
    
    def wait_for_game(self, timeout: int = 60) -> bool:
        """게임 실행까지 대기
        
        Args:
            timeout: 대기 시간 (초)
            
        Returns:
            bool: 게임 실행 감지 성공 여부
        """
        start_time = time.time()
        
        print(f"게임 실행을 기다리는 중... (최대 {timeout}초)")
        
        while time.time() - start_time < timeout:
            if self.is_game_running():
                print("게임 실행 감지됨!")
                return True
            
            time.sleep(1)
            
        print(f"{timeout}초 동안 게임 실행이 감지되지 않았습니다.")
        return False
    
    def get_primary_game_process(self) -> Optional[ProcessInfo]:
        """주요 게임 프로세스 반환 (메모리 사용량 기준)
        
        Returns:
            Optional[ProcessInfo]: 주요 게임 프로세스 정보
        """
        processes = self.get_game_processes()
        
        if not processes:
            return None
            
        # 메모리 사용량이 가장 높은 프로세스를 주요 프로세스로 판단
        return max(processes, key=lambda p: p.memory_usage)
    
    def get_process_details(self) -> Dict[str, Any]:
        """게임 프로세스 상세 정보 반환
        
        Returns:
            Dict[str, Any]: 프로세스 상세 정보
        """
        processes = self.get_game_processes()
        
        if not processes:
            return {
                "running": False,
                "process_count": 0,
                "processes": [],
                "primary_process": None
            }
        
        primary = self.get_primary_game_process()
        
        return {
            "running": True,
            "process_count": len(processes),
            "processes": [
                {
                    "pid": p.pid,
                    "name": p.name,
                    "exe_path": p.exe_path,
                    "memory_mb": p.memory_usage // (1024 * 1024),
                    "create_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p.create_time))
                }
                for p in processes
            ],
            "primary_process": {
                "pid": primary.pid,
                "name": primary.name,
                "memory_mb": primary.memory_usage // (1024 * 1024)
            } if primary else None
        }
    
    def _is_game_process(self, process_name: str) -> bool:
        """프로세스명이 게임 프로세스인지 확인
        
        Args:
            process_name: 프로세스명
            
        Returns:
            bool: 게임 프로세스 여부
        """
        process_name_lower = process_name.lower()
        
        for game_name in self.process_names:
            if game_name.lower() in process_name_lower:
                return True
                
        return False


def create_game_detector() -> GameProcessDetector:
    """게임 프로세스 감지기 팩토리 함수
    
    Returns:
        GameProcessDetector: 게임 프로세스 감지기 인스턴스
    """
    return GameProcessDetector()


if __name__ == "__main__":
    # 테스트용 실행
    detector = create_game_detector()
    
    print("=== 블루아카이브 프로세스 감지 테스트 ===")
    print(f"게임 실행 중: {detector.is_game_running()}")
    
    processes = detector.get_game_processes()
    print(f"발견된 프로세스 수: {len(processes)}")
    
    for proc in processes:
        print(f"- PID: {proc.pid}, 이름: {proc.name}, 메모리: {proc.memory_usage // (1024 * 1024)}MB")
    
    details = detector.get_process_details()
    print(f"\n상세 정보:")
    print(f"실행 중: {details['running']}")
    print(f"프로세스 수: {details['process_count']}")
    
    if details['primary_process']:
        primary = details['primary_process']
        print(f"주요 프로세스: {primary['name']} (PID: {primary['pid']}, 메모리: {primary['memory_mb']}MB)")