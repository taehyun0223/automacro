# Epic Seven Shop Refresh Bot - 개발 설계서 (Claude Code 베이스)

## 📌 프로젝트 개요

Epic Seven(에픽세븐) 게임의 **Secret Shop** 자동 새로고침 매크로 봇.  
해당 봇은 일정 조건에 따라 상점을 자동으로 새로고침하고, 원하는 아이템이 등장할 경우 자동으로 구매 클릭을 수행합니다.

---

## 🧱 아키텍처 구조 (Clean Architecture 적용)

```
e7_macro/
├── domain/
│   ├── models/                  # 도메인 모델 정의 (이미지, 좌표 등)
│   └── services/                # 이미지 매칭 로직, 좌표 해석
├── application/
│   ├── usecases/                # 새로고침 루프 실행 및 종료 핸들링
│   └── macros/                  # 상점 새로고침 단일 동작 구현
├── infrastructure/
│   ├── screen/                  # PyAutoGUI/ADB 기반 클릭 처리
│   ├── input/                   # 키보드 종료 핫키 감지
│   └── adb/                     # (선택) ADB 백그라운드 클릭 기능
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
| 성능 최적화       | `mss` (선택적으로 스크린샷 속도 개선) |
| 랜덤 딜레이 및 좌표 | `random` 모듈 |

---

## 🔁 주요 유스케이스 흐름

1. `main.py`에서 설정 초기화 및 DI 구성
2. 상점 새로고침 버튼 이미지 탐색 (`OpenCVImageLocator`)
3. 버튼 위치 확인되면 클릭 (`ScreenClicker`)
4. 랜덤 딜레이 후 반복 수행
5. 종료 핫키(`q` 등) 감지되면 종료

---

## 📄 주요 클래스 설명

### `ImageRegion` (domain/models)
- 버튼 이미지 경로 및 임계값, 이름 등 저장

### `OpenCVImageLocator` (domain/services)
- 화면에서 버튼 이미지 위치를 탐색하여 좌표 반환

### `ShopRefresher` (application/macros)
- 버튼을 찾고 클릭하는 단일 동작만 담당 (SRP)

### `RefreshShopUseCase` (application/usecases)
- 반복 새로고침 루프 처리 및 종료 조건 감지

### `PyAutoGuiScreenClicker` (infrastructure/screen)
- pyautogui를 통한 화면 클릭 구현체

---

## ✅ 개발 우선순위

1. [x] 템플릿 이미지 캡처 및 저장
2. [x] `ImageLocator` 구현
3. [x] `Clicker` 구현
4. [x] `ShopRefresher` 단일 동작 구현
5. [x] 반복 루프 + 종료 핫키 감지

---

## 🚀 향후 개선 아이디어

- ADB 백그라운드 모드 전환
- 템플릿 이미지 자동 학습/추출
- OCR 기반 텍스트 매칭 강화
- GUI 인터페이스 추가 (PyQt or Tauri)