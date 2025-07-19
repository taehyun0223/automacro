# 🎮 블루아카이브 일일퀘스트 매크로

블루아카이브 게임의 반복적인 일일 작업을 자동화하는 매크로입니다.

## ✨ 기능

- 🏪 **카페 자동화**: 카페 접근 및 수익 수령 자동화
- 💰 **카페 수익 수령**: 카페 수익 버튼 클릭 및 팝업 수령 처리
- 📋 **일일 미션 수령**: 완료된 일일 미션 보상을 자동으로 수령합니다
- ⌨️ **안전한 종료**: 설정된 키로 언제든 매크로를 중단할 수 있습니다
- 🎯 **이미지 인식**: OpenCV 기반 정확한 버튼 인식
- 🔍 **게임 상태 감지**: 실시간 게임 화면 상태 인식

## 📁 프로젝트 구조

```
blue_archive_macro/
├── domain/                     # 도메인 계층
│   ├── models/                 # 도메인 모델
│   │   └── image_region.py     # 이미지 영역 모델
│   └── services/               # 도메인 서비스
│       └── image_locator.py    # 이미지 검색 서비스
├── application/                # 애플리케이션 계층
│   ├── usecases/              # 유스케이스
│   │   ├── cafe_automation_usecase.py  # 카페 자동화
│   │   └── macro_loop_usecase.py       # 매크로 루프
│   └── macros/                # 매크로 구현체
│       ├── cafe_reward_collector.py    # 카페 보상 수집
│       └── daily_mission_claimer.py    # 일일 미션 클레임
├── infrastructure/             # 인프라스트럭처 계층
│   ├── screen/                # 화면 조작
│   │   ├── game_state_detector.py      # 게임 상태 감지
│   │   ├── cafe_revenue_detector.py    # 카페 수익 감지
│   │   └── clicker.py                  # 클릭 처리
│   ├── input/                 # 키보드 입력 처리
│   │   └── keyboard_monitor.py         # 키보드 모니터링
│   ├── process/               # 프로세스 관리
│   │   └── game_process_detector.py    # 게임 프로세스 감지
│   └── window/                # 윈도우 관리
│       └── window_manager.py           # 윈도우 관리자
├── assets/                    # 이미지 템플릿
│   ├── cafe_button.png        # 카페 버튼
│   ├── cafe_revenue_button.png # 카페 수익 버튼
│   ├── collect_button.png     # 수령 버튼
│   └── cafe_reward.png        # 카페 보상 아이콘
├── tools/                     # 개발 도구
│   ├── debug/                 # 디버깅 도구
│   └── templates/             # 템플릿 생성 도구
├── screenshots/               # 스크린샷 저장소
├── config.py                  # 설정 파일
├── main.py                    # 실행 진입점
├── TEST_GUIDE.md             # 테스트 가이드
└── requirements.txt           # 의존성
```

## 🛠️ 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 이미지 템플릿 준비

`assets/` 폴더에 다음 이미지들을 준비해주세요:

- `cafe_button.png` - 카페 버튼 (메인 메뉴)
- `cafe_revenue_button.png` - 카페 수익 버튼 (카페 내부)
- `collect_button.png` - 수령 버튼 (팝업)
- `cafe_reward.png` - 카페 보상 아이콘  
- `daily_mission_button.png` - 일일 미션 버튼
- `mission_claim_button.png` - 미션 수령 버튼
- `close_button.png` - 닫기 버튼

### 3. 설정 조정

`config.py`에서 다음 설정들을 조정할 수 있습니다:

- `SCREEN_RESOLUTION`: 화면 해상도
- `IMAGE_MATCH_CONFIDENCE`: 이미지 매칭 정확도 (0.0~1.0)
- `CLICK_DELAY_MIN/MAX`: 클릭 간격
- `EXIT_KEY`: 종료 키 (기본값: 'ctrl+q')

## 🚀 사용법

### 기본 실행
1. 블루아카이브 게임을 실행합니다
2. 매크로를 실행합니다:
   ```bash
   python main.py
   ```
3. 메뉴에서 원하는 기능을 선택합니다:
   - `1. 카페 접근`: 카페까지만 접근
   - `2. 카페 접근 + 수익 수령`: 카페 접근 후 수익 자동 수령
   - `3. 전체 매크로 루프`: 연속 실행
   - `4. 현재 상태 확인`: 게임 상태 점검

### 템플릿 생성 (최초 실행 시)
```bash
# 카페 수익 관련 템플릿 생성
python tools/templates/create_revenue_templates.py

# 수동 템플릿 생성 (문제 발생 시)
python tools/templates/manual_template_creator.py
```

### 디버깅 도구
```bash
# 클릭 위치 디버깅
python tools/debug/debug_click_position.py

# 간단한 클릭 테스트
python tools/debug/simple_debug_click.py
```

## ⚙️ 설정 옵션

### 기본 설정 (config.py)

```python
# 화면 설정
SCREEN_RESOLUTION = (1920, 1080)
IMAGE_MATCH_CONFIDENCE = 0.8

# 클릭 설정  
CLICK_DELAY_MIN = 0.5
CLICK_DELAY_MAX = 2.0
CLICK_OFFSET_RANGE = 5

# 실행 설정
LOOP_DELAY = 3.0
EXIT_KEY = 'ctrl+q'
```

## 🔧 개발자 정보

이 프로젝트는 Clean Architecture 패턴을 적용하여 개발되었습니다:

- **Domain Layer**: 비즈니스 로직과 도메인 모델
- **Application Layer**: 유스케이스와 매크로 구현
- **Infrastructure Layer**: 외부 의존성 (화면 조작, 키보드 등)

## ⚠️ 주의사항

- 게임 해상도는 1920x1080으로 고정해주세요
- 이미지 템플릿은 정확히 캡처해야 합니다
- 매크로 사용 시 게임 정책을 확인해주세요
- 안전을 위해 반드시 종료 키를 기억해두세요

## 🤝 기여

이슈나 개선사항이 있다면 언제든 제보해주세요!