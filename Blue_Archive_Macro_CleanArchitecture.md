# Blue Archive Macro Bot - 개발 설계서 (Claude Code 베이스)

## 📌 프로젝트 개요

블루아카이브(Blue Archive) 게임에서 반복적이고 수동적인 행동을 자동화하는 매크로 봇입니다.  
예: 카페 보상 수령, 인연 포인트 수령, 일일 미션 수령 등  
이미지 인식 기반으로 특정 UI 요소를 찾아 클릭하고, 일정 시간 간격으로 반복 수행합니다.

---

## 🧱 아키텍처 구조 (Clean Architecture 적용)

```
blue_archive_macro/
├── domain/
│   ├── models/                  # 도메인 모델 정의 (버튼, 이미지 위치 등)
│   └── services/                # 이미지 매칭 로직, 좌표 처리
├── application/
│   ├── usecases/                # 반복 실행 루프 및 종료 감지
│   └── macros/                  # 개별 동작 정의 (카페 수령 등)
├── infrastructure/
│   ├── screen/                  # pyautogui 기반 클릭 처리
│   ├── input/                   # 키보드 종료 핫키 감지
│   └── adb/                     # (선택) ADB 클릭 구현체
├── assets/                      # 템플릿 이미지 저장 경로
├── config.py                    # 설정값 (해상도, 딜레이 등)
└── main.py                      # 실행 진입점
```

---

## ⚙️ 기술 스택

| 기능             | 사용 도구 |
|------------------|-----------|
| 이미지 인식       | `opencv-python`, `pyautogui`, `Pillow` |
| 마우스 클릭       | `pyautogui` 또는 `adb` (선택) |
| 키보드 감지       | `pynput` |
| 성능 최적화       | `mss` (선택) |
| 랜덤 딜레이 및 좌표 | `random` 모듈 |

---

## 🧩 유스케이스 흐름

1. `main.py` 실행 시 config 로딩
2. 매크로 대상 버튼 이미지 인식 (`ImageLocator`)
3. 위치를 기준으로 클릭 수행 (`Clicker`)
4. 동작 후 랜덤 대기
5. 사용자가 정한 키 입력 시 루프 종료

---

## 🧩 예시 동작 모듈

### `CafeRewardCollector` (application/macros)
- 카페 버튼을 찾아 클릭
- 보상 아이콘을 탐색하여 클릭

### `DailyMissionClaimer`
- 일일 미션 창 확인 후 수령 버튼 반복 클릭

---

## 📄 주요 클래스 설명

### `ImageRegion` (domain/models)
- 버튼의 이미지 경로, 신뢰도, 이름을 저장

### `OpenCVImageLocator` (domain/services)
- 버튼 위치를 이미지 매칭을 통해 탐색

### `BlueArchiveMacroLoopUseCase` (application/usecases)
- 전체 반복 제어 및 종료 키 감지

### `PyAutoGuiScreenClicker` (infrastructure/screen)
- 실제 마우스 클릭 수행

---

## ✅ 개발 우선순위

1. [x] 버튼 이미지 캡처 및 저장
2. [x] 이미지 인식 기능 구현
3. [x] 클릭 기능 구현
4. [x] 반복 제어 + 종료 조건 구현
5. [ ] 각 기능 모듈별 분리 및 설정 옵션화

---

## 🚀 향후 개선 방향

- ADB 백그라운드 모드 전환
- OCR을 통한 텍스트 버튼 인식
- GUI 옵션 설정 화면 제공 (PyQt, Tauri 등)
- 사용자 행동 통계 기록 기능 추가

---

## 🔐 기타

- 실행 시 해상도 고정이 필요함 (예: 1920x1080)
- 이미지 파일은 `assets/`에 저장되며 이름은 기능에 따라 명명
- 반복 간격, 딜레이 등은 `config.py`에서 설정 가능