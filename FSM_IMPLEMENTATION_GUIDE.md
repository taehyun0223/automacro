# 🤖 FSM 자동화 시스템 구현 가이드

## 📋 개요

블루아카이브 자동화를 위한 지능형 유한 상태 머신(FSM) 시스템이 성공적으로 구현되었습니다. 이 시스템은 기존의 단순한 매크로 방식을 넘어서 게임 상태를 지능적으로 인식하고 최적의 액션을 수행하는 고급 자동화 시스템입니다.

## 🎯 주요 특징

### 🧠 지능형 상태 관리
- **이미지 기반 상태 전환**: `xxx.png` 감지 시 자동 상태 변경
- **우선순위 기반 액션**: 자원 발견 우선순위에 따른 액션 수행  
- **강력한 오류 처리**: 타임아웃, 대체 자원, 복구 메커니즘
- **실시간 모니터링**: 상태 변화, 성능 메트릭, 디버깅 정보

### ⚡ 성능 최적화
- **병렬 이미지 검색**: 여러 리소스 동시 탐지
- **스마트 캐싱**: 이미지 매칭 결과 캐시
- **적응형 신뢰도**: 상황별 다른 임계값 적용
- **메모리 효율성**: 불필요한 스크린샷 최소화

## 🚀 빠른 시작

### 1. FSM 자동화 실행
```bash
python main_fsm.py
```

### 2. 메뉴 옵션 선택
- **옵션 3**: 🤖 FSM 스마트 모드 (30분) - 권장
- **옵션 4**: ⚡ FSM 빠른 모드 (10분) - 빠른 테스트용
- **옵션 5**: 🎯 FSM 카페 전용 모드 - 카페 보상에만 집중

### 3. 자동화 실행 결과 확인
```
📊 자동화 실행 결과
==================================================
총 실행 시간: 15.2분
상태 전환 횟수: 23회
성공한 액션: 18개
실패한 액션: 2개
🎉 카페 보상 수집: 12개
⚡ 액션 효율성: 1.2회/분
✅ 성공률: 90.0%
```

## 🏗️ 시스템 아키텍처

### 핵심 컴포넌트

```
FSM 자동화 시스템
├── 🎯 FSM 프레임워크
│   ├── finite_state_machine.py (핵심 FSM 클래스)
│   └── game_states.py (상태 정의 및 전환 규칙)
├── 🎮 게임 상태 구현
│   └── application/states/game_states.py
├── 🤖 자동화 유스케이스
│   └── fsm_automation_usecase.py
└── 🖥️ 사용자 인터페이스
    └── main_fsm.py
```

### 상태 흐름도

```
[IDLE] 게임 미실행
   ↓ (게임 프로세스 감지)
[LOADING] 로딩 화면
   ↓ (홈 화면 감지)
[IN_HOME] 홈 화면
   ↓ (카페 버튼 클릭)
[IN_CAFE] 카페 화면
   ↓ (보상 수집)
[REWARD_POPUP] 보상 팝업
   ↓ (팝업 처리)
[IN_CAFE] 카페 화면
   ↓ (작업 완료)
[IN_HOME] 홈 화면
```

## 🔧 개발자 가이드

### FSM 상태 추가하기

1. **새 상태 정의**
```python
# domain/models/game_states.py
class ExtendedGameState(Enum):
    IN_SHOP = "in_shop"  # 새로운 상점 상태
```

2. **상태 구현**
```python
# application/states/game_states.py
class ShopState(FSMState):
    def on_enter(self):
        self.logger.info("🛒 SHOP 상태 진입")
        
    def execute(self):
        # 상점에서의 액션 로직
        return None
        
    def on_exit(self):
        self.logger.info("🚪 SHOP 상태 종료")
```

3. **상태 등록**
```python
# application/usecases/fsm_automation_usecase.py
def _register_states(self):
    # 기존 상태들...
    self.fsm.register_state("IN_SHOP", ShopState)
```

### 새로운 이미지 리소스 추가

1. **이미지 캡처**: 게임에서 해당 UI 요소 스크린샷
2. **파일 저장**: `assets/` 폴더에 PNG 형식으로 저장
3. **테스트**: FSM에서 해당 이미지 인식 테스트

```python
# 이미지 인식 테스트
region = ImageRegion(
    name="new_button",
    image_path="assets/new_button.png",
    confidence=0.7
)
result = image_locator.find_image(region)
```

## 🧪 테스트 및 검증

### 기본 테스트 실행
```bash
python test_fsm_simple.py
```

### 상태별 테스트
```python
# 특정 상태 테스트
automation = FSMAutomationUseCase()
automation.fsm.set_initial_state("IN_CAFE")
result = automation.start_automation("IN_CAFE", max_runtime_minutes=5)
```

### 디버깅 모드
```python
# 로깅 레벨 조정으로 상세 정보 확인
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📊 성능 모니터링

### 실시간 상태 확인
```bash
# FSM 시스템 상태 확인 (메뉴 옵션 7)
python main_fsm.py
```

### 메트릭 수집
- **상태 전환 횟수**: 시스템 활동성 지표
- **액션 성공률**: 이미지 인식 정확도
- **실행 효율성**: 분당 액션 수행 횟수
- **오류 복구율**: 시스템 안정성 지표

## 🔄 기존 시스템과의 통합

### 호환성
- ✅ 기존 `main.py` 완전 호환
- ✅ 기존 이미지 리소스 재사용
- ✅ 기존 설정 파일 유지

### 점진적 마이그레이션
1. **Phase 1**: FSM 시스템과 기존 시스템 병행 사용
2. **Phase 2**: FSM 시스템으로 주요 기능 이전
3. **Phase 3**: 기존 시스템 레거시 유지 및 FSM 주력 사용

## 🚨 문제 해결

### 일반적인 문제들

#### 이미지 인식 실패
```
해결 방법:
1. assets/ 폴더의 이미지 파일 확인
2. 게임 해상도 및 화면 배율 확인
3. confidence 임계값 조정 (0.6 ~ 0.8)
```

#### 상태 전환 실패
```
해결 방법:
1. 게임 상태 수동 확인
2. 로딩 시간 충분히 대기
3. 로그 파일에서 상세 오류 정보 확인
```

#### 성능 이슈
```
해결 방법:
1. 이미지 파일 크기 최적화
2. confidence 임계값 적정 수준 유지
3. 불필요한 스크린샷 캡처 비활성화
```

## 🔮 향후 개발 계획

### 단기 계획 (1-2주)
- [ ] 추가 게임 상태 (전투, 상점, 이벤트)
- [ ] 다중 해상도 지원
- [ ] 성능 프로파일링 및 최적화

### 중기 계획 (1-2개월)
- [ ] GUI 기반 설정 인터페이스
- [ ] 스케줄러 기능 (시간대별 자동화)
- [ ] 클라우드 기반 이미지 매칭

### 장기 계획 (3-6개월)
- [ ] 머신러닝 기반 패턴 학습
- [ ] 다른 게임에 대한 FSM 프레임워크 확장
- [ ] 커뮤니티 기반 이미지 리소스 공유

## 📝 라이선스 및 기여

이 FSM 자동화 시스템은 기존 프로젝트의 라이선스를 따르며, 커뮤니티 기여를 환영합니다.

### 기여 방법
1. 새로운 상태 구현
2. 이미지 리소스 기여
3. 버그 리포트 및 개선 제안
4. 문서 개선

---

🤖 **Generated with [Claude Code](https://claude.ai/code)**

**Co-Authored-By**: Claude <noreply@anthropic.com>