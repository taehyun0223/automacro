# Assets 폴더

FSM 자동화에 필요한 이미지 템플릿들을 저장하는 폴더입니다.

## 현재 있는 파일들
- `cafe_button.png` - 홈 화면의 카페 버튼
- `cafe_reward.png` - 카페의 수집 가능한 보상

## FSM 자동화를 위해 추가로 필요한 파일들

### 기본 UI 요소
- `home_button.png` - 홈으로 돌아가는 버튼
- `back_button.png` - 뒤로가기 버튼
- `close_button.png` - 팝업 닫기 버튼 (X 버튼)
- `confirm_button.png` - 확인 버튼
- `cancel_button.png` - 취소 버튼

### 보상 관련
- `collect_all_button.png` - 일괄 수집 버튼
- `collect_button.png` - 개별 수집 버튼
- `reward_popup.png` - 보상 팝업 화면
- `reward_collection_popup.png` - 보상 수집 팝업

### 메뉴 및 네비게이션
- `daily_mission_button.png` - 일일 미션 버튼
- `event_notification.png` - 이벤트 알림
- `shop_button.png` - 상점 버튼
- `battle_button.png` - 전투 버튼
- `menu_button.png` - 메뉴 버튼

### 다이얼로그 및 팝업
- `dialog_box.png` - 일반 다이얼로그 창
- `yes_button.png` - 예 버튼
- `no_button.png` - 아니오 버튼
- `x_button.png` - X 닫기 버튼

### 오류 및 상태
- `connection_error.png` - 연결 오류 화면
- `maintenance_notice.png` - 점검 공지
- `retry_button.png` - 재시도 버튼
- `reconnect_button.png` - 재연결 버튼

## 이미지 캡처 가이드

### 캡처 방법
1. 게임을 실행하고 해당 UI 요소가 화면에 표시된 상태로 만듭니다
2. 스크린샷을 찍거나 `manual_template_creator.py`를 사용합니다
3. 이미지 편집 프로그램에서 해당 버튼/요소만 잘라냅니다
4. PNG 형식으로 저장합니다

### 캡처 팁
- 버튼의 경우 텍스트와 배경을 포함하여 캡처하세요
- 너무 크게 캡처하지 말고 버튼 영역만 정확히 캡처하세요
- 이미지가 흐리지 않도록 선명하게 캡처하세요
- 다양한 상황(밝기, 상태)에서도 인식될 수 있도록 대표적인 상태에서 캡처하세요

### 파일명 규칙
- 소문자와 언더스코어 사용 (예: `cafe_button.png`)
- 명확하고 설명적인 이름 사용
- `.png` 확장자 사용

## 테스트 방법

캡처한 이미지가 잘 동작하는지 테스트하려면:

```python
from domain.services.image_locator import OpenCVImageLocator
from domain.models.image_region import ImageRegion

locator = OpenCVImageLocator()
region = ImageRegion(
    name="test_button",
    image_path="assets/your_image.png",
    confidence=0.7
)

result = locator.find_image(region)
if result:
    print(f"이미지 발견: ({result.x}, {result.y}), 신뢰도: {result.confidence}")
else:
    print("이미지를 찾을 수 없습니다")
```