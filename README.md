# 🎮 블루아카이브 일일퀘스트 매크로 (현재 개발중, 미완)

블루아카이브 게임의 반복적인 일일 작업을 자동화하는 매크로입니다.

## ✨ 기능

- 🏪 **카페 보상 수령**: 카페에서 자동으로 보상을 수령합니다
- 📋 **일일 미션 수령**: 완료된 일일 미션 보상을 자동으로 수령합니다
- ⌨️ **안전한 종료**: 설정된 키로 언제든 매크로를 중단할 수 있습니다
- 🎯 **이미지 인식**: OpenCV 기반 정확한 버튼 인식

## 📁 프로젝트 구조

```
blue_archive_macro/
├── domain/                     # 도메인 계층
│   ├── models/                 # 도메인 모델
│   └── services/               # 도메인 서비스
├── application/                # 애플리케이션 계층
│   ├── usecases/              # 유스케이스
│   └── macros/                # 매크로 구현체
├── infrastructure/             # 인프라스트럭처 계층
│   ├── screen/                # 화면 조작
│   └── input/                 # 키보드 입력 처리
├── assets/                    # 이미지 템플릿
├── config.py                  # 설정 파일
├── main.py                    # 실행 진입점
└── requirements.txt           # 의존성
```

## 🛠️ 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 이미지 템플릿 준비

`assets/` 폴더에 다음 이미지들을 준비해주세요:

- `cafe_button.png` - 카페 버튼
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

1. 블루아카이브 게임을 실행합니다
2. 매크로를 실행합니다:
   ```bash
   python main.py
   ```
3. 설정된 종료 키(`Ctrl+Q`)를 눌러 매크로를 중단할 수 있습니다

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
