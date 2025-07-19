# 블루아카이브 PC 클라이언트 게임 감지 구현 가이드

## 1. 현재 상황 분석

### 문제점
- 현재 코드는 게임이 실행되어 있다고 가정하고 UI 요소만 찾음
- 실제 게임 프로세스나 윈도우 감지 로직 없음
- 게임이 실행되지 않았을 때 무한 대기하거나 오류 발생 가능

### 목표
블루아카이브 PC 클라이언트의 실행 상태를 감지하고 게임 윈도우를 관리하는 시스템 구축

## 2. 구현 단계

### Phase 1: 게임 프로세스 감지
1. **프로세스 감지 서비스 생성**
   ```
   infrastructure/process/
   ├── game_process_detector.py
   └── __init__.py
   ```

2. **구현 내용**
   - `psutil` 라이브러리를 사용해 실행 중인 프로세스 확인
   - 블루아카이브 관련 프로세스명 패턴 매칭
     - `BlueArchive.exe`
     - `BlueArchiveClient.exe`
     - `BlueArchiveLauncher.exe`
   - 프로세스 PID 및 실행 경로 정보 수집

### Phase 2: 윈도우 감지 및 관리
1. **윈도우 관리 서비스 생성**
   ```
   infrastructure/window/
   ├── window_manager.py
   └── __init__.py
   ```

2. **구현 내용**
   - `pygetwindow` 또는 `win32gui` 사용
   - 블루아카이브 윈도우 타이틀 패턴 매칭
     - "Blue Archive"
     - "블루 아카이브"
     - "ブルーアーカイブ"
   - 윈도우 상태 확인 (최소화/활성화/크기)
   - 윈도우 포커스 및 크기 조정 기능

### Phase 3: 게임 상태 감지
1. **게임 상태 감지 서비스 확장**
   ```
   domain/services/
   ├── game_state_detector.py
   └── game_detector.py (기존 image_locator 확장)
   ```

2. **구현 내용**
   - 로딩 화면 감지
   - 메인 메뉴 화면 감지
   - 인게임 상태 감지
   - 에러/팝업 화면 감지

### Phase 4: 통합 게임 감지 시스템
1. **게임 감지 유즈케이스 생성**
   ```
   application/usecases/
   └── game_detection_usecase.py
   ```

2. **구현 내용**
   - 프로세스 → 윈도우 → 게임상태 순차적 확인
   - 게임 실행 대기 로직
   - 게임 종료 감지 및 처리
   - 재시작 로직

## 3. 필요한 라이브러리 추가

### requirements.txt 업데이트 필요
```
psutil>=5.9.0          # 프로세스 감지
pygetwindow>=0.0.9     # 윈도우 관리
pywin32>=306           # Windows API (윈도우 조작)
```

## 4. 구현 순서

### Step 1: 프로세스 감지 구현
1. `GameProcessDetector` 클래스 생성
2. 블루아카이브 프로세스 패턴 정의
3. 프로세스 실행 상태 확인 메서드
4. 단위 테스트 작성

### Step 2: 윈도우 관리 구현
1. `WindowManager` 클래스 생성
2. 윈도우 찾기 및 상태 확인
3. 윈도우 포커스/크기 조정 기능
4. 단위 테스트 작성

### Step 3: 게임 상태 감지 확장
1. 기존 `OpenCVImageLocator` 확장
2. 게임 상태별 UI 패턴 정의
3. 상태 전환 로직 구현
4. 통합 테스트 작성

### Step 4: 유즈케이스 통합
1. `GameDetectionUseCase` 구현
2. 기존 매크로 시스템과 연동
3. 에러 처리 및 복구 로직
4. 전체 시스템 테스트

## 5. 설정 파일 업데이트

### config.py 추가 설정
```python
# 게임 감지 설정
GAME_PROCESS_NAMES = ["BlueArchive.exe", "BlueArchiveClient.exe"]
GAME_WINDOW_TITLES = ["Blue Archive", "블루 아카이브"]
GAME_DETECTION_TIMEOUT = 60  # 게임 감지 타임아웃 (초)
WINDOW_FOCUS_RETRY_COUNT = 3  # 윈도우 포커스 재시도 횟수

# 게임 상태 감지
LOADING_DETECTION_IMAGES = ["loading_screen.png"]
MAIN_MENU_DETECTION_IMAGES = ["main_menu_button.png"]
ERROR_DETECTION_IMAGES = ["error_popup.png", "maintenance_notice.png"]
```

## 6. 테스트 시나리오

### 게임 감지 테스트
1. **게임 미실행 상태**
   - 프로세스 감지 실패 확인
   - 적절한 대기/에러 메시지 출력

2. **게임 실행 중 상태**
   - 프로세스 감지 성공 확인
   - 윈도우 감지 및 포커스 확인
   - 게임 상태 정확히 판단

3. **게임 종료 감지**
   - 실행 중 게임 종료 시 감지
   - 매크로 안전 종료 처리

### 윈도우 관리 테스트
1. **윈도우 최소화 상태**
   - 윈도우 복원 기능 테스트
   - 포커스 설정 테스트

2. **해상도 변경 감지**
   - 윈도우 크기 변경 감지
   - 좌표 시스템 재조정

## 7. 예상되는 이슈 및 해결방안

### 이슈 1: 관리자 권한 필요
- **문제**: 윈도우 조작 시 권한 부족
- **해결**: 관리자 권한 요청 로직 추가

### 이슈 2: 다중 게임 인스턴스
- **문제**: 여러 게임 창이 열려있을 경우
- **해결**: 활성화된 윈도우 우선 선택 로직

### 이슈 3: 게임 업데이트로 인한 변화
- **문제**: UI 변경으로 인한 감지 실패
- **해결**: 다중 패턴 매칭 및 fallback 로직

## 8. 마이그레이션 계획

### 기존 코드 수정 최소화
1. 기존 `image_locator.py` 유지
2. 새로운 감지 시스템을 wrapper로 구현
3. 점진적 마이그레이션 가능하도록 설계

### 호환성 보장
1. 기존 매크로 동작 방식 유지
2. 새 기능은 옵션으로 제공
3. 설정으로 구/신 시스템 선택 가능

## 9. 다음 단계

1. **즉시 시작**: 프로세스 감지 구현
2. **1주차**: 윈도우 관리 구현
3. **2주차**: 게임 상태 감지 확장
4. **3주차**: 통합 및 테스트
5. **4주차**: 최적화 및 문서화

이 가이드를 따라 단계별로 구현하면 안정적인 블루아카이브 PC 클라이언트 감지 시스템을 구축할 수 있습니다.