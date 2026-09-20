/*
 * ======================================================================================
 * [머신아트랩 - 박건 작가님 인터랙티브 키트]
 * 3. ESP32 올인원 단일 보드 통합 코드 (All-in-One ESP32)
 * ======================================================================================
 * - 설명: 별도의 아두이노 베이스 보드 없이, ESP32 스마트 디스플레이 1개에 
 *        로드셀(HX711)과 8자리 세그먼트(MAX7219)를 모두 직결하여 단독 제어하는 초간결 구성
 * - 부품 직결 연결:
 *    1) HX711 (로드셀): DT, SCK -> ESP32 가용 GPIO
 *    2) MAX7219 (8자리 7세그먼트): DIN, CLK, CS -> ESP32 가용 GPIO
 *    3) 온보드 SD 카드 & LCD: 자체 화면 출력
 * 
 * [동작 흐름]
 * 1. 로드셀에 손을 올림 (> 100g 하중 감지)
 * 2. 세그먼트에 8자리 무작위 숫자 롤링 ("띠리리리" 슬롯머신 감속 애니메이션)
 * 3. 온보드 LCD 화면에 SD 카드의 무작위 사진 즉시 전환
 * 4. 손을 떼면 대기 모드로 복귀
 * ======================================================================================
 */

#include <Arduino.h>
#include <FS.h>
#include <SD.h>
#include <SPI.h>
#include <LedControl.h>
#include "HX711.h"

#define LGFX_USE_V1
#include <LovyanGFX.hpp>
#include <TJpg_Decoder.h>

// ===================== [ESP32 확장 GPIO 핀맵] =====================
// 1. MAX7219 8자리 7세그먼트 (DIN, CLK, CS)
const int PIN_MAX_DIN = 17;
const int PIN_MAX_CLK = 18;
const int PIN_MAX_CS  = 19;
LedControl lc = LedControl(PIN_MAX_DIN, PIN_MAX_CLK, PIN_MAX_CS, 1);

// 2. HX711 로드셀 앰프 (DOUT, SCK)
const int PIN_HX_DOUT = 21;
const int PIN_HX_SCK  = 22;
HX711 scale;

// 3. 온보드 MicroSD CS 핀
const int PIN_SD_CS   = 5;

// ===================== [디스플레이 드라이버] =====================
class LGFX : public lgfx::LGFX_Device {
public:
  LGFX() {
    // 사용하시는 디스플레이 보드 설정 매핑
  }
};
LGFX lcd;

// ===================== [전역 변수 및 파라미터] =====================
const long WEIGHT_THRESHOLD = 8000; // 손 올림 감지 임계치
long baselineWeight = 0;

const int MAX_IMAGES = 100;
String imageFiles[MAX_IMAGES];
int totalImageCount = 0;
int lastImageIndex = -1;

enum SystemState {
  STATE_IDLE,
  STATE_TRIGGERED,
  STATE_HOLD,
  STATE_WAIT_RELEASE
};
SystemState state = STATE_IDLE;
unsigned long triggerTimestamp = 0;

// TJpg_Decoder 콜백
bool tjpgCallback(int16_t x, int16_t y, uint16_t w, uint16_t h, uint16_t* bitmap) {
  if (y >= lcd.height()) return 0;
  lcd.pushImage(x, y, w, h, bitmap);
  return 1;
}

// ----------------------------------------------------
// SD 카드 이미지 스캔 및 무작위 사진 표시
// ----------------------------------------------------
void scanImages() {
  File dir = SD.open("/images");
  if (!dir || !dir.isDirectory()) return;

  totalImageCount = 0;
  File f = dir.openNextFile();
  while (f && totalImageCount < MAX_IMAGES) {
    if (!f.isDirectory()) {
      String name = f.name();
      if (name.endsWith(".jpg") || name.endsWith(".JPG")) {
        imageFiles[totalImageCount++] = String("/images/") + name;
      }
    }
    f = dir.openNextFile();
  }
}

void showRandomImage() {
  if (totalImageCount == 0) return;
  int idx = random(0, totalImageCount);
  if (totalImageCount > 1 && idx == lastImageIndex) {
    idx = (idx + 1) % totalImageCount;
  }
  lastImageIndex = idx;
  TJpgDec.drawSdJpg(0, 0, imageFiles[idx].c_str());
}

// ----------------------------------------------------
// "띠리리리" 룰렛 세그먼트 애니메이션
// ----------------------------------------------------
void playSegmentRoulette() {
  int targetNumbers[8];
  for (int i = 0; i < 8; i++) {
    targetNumbers[i] = random(0, 10);
  }

  // 30 프레임 동안 점점 속도가 느려지며 앞자리부터 멈춤
  for (int frame = 0; frame < 30; frame++) {
    int locked = frame / 4;
    if (locked > 8) locked = 8;

    for (int i = 0; i < 8; i++) {
      if (i < locked) {
        lc.setDigit(0, 7 - i, targetNumbers[i], false);
      } else {
        lc.setDigit(0, 7 - i, random(0, 10), false);
      }
    }
    delay(20 + (frame * 3));
  }

  // 최종 8자리 완성
  for (int i = 0; i < 8; i++) {
    lc.setDigit(0, 7 - i, targetNumbers[i], false);
  }
}

void setup() {
  Serial.begin(115200);

  // 1. 세그먼트 초기화
  lc.shutdown(0, false);
  lc.setIntensity(0, 8);
  lc.clearDisplay(0);
  for (int i = 0; i < 8; i++) lc.setChar(0, i, '-', false);

  // 2. LCD 및 디코더 초기화
  lcd.init();
  lcd.fillScreen(TFT_BLACK);
  TJpgDec.setJpgScale(1);
  TJpgDec.setSwapBytes(true);
  TJpgDec.setCallback(tjpgCallback);

  // 3. SD 카드 마운트 및 이미지 로드
  if (SD.begin(PIN_SD_CS)) {
    scanImages();
    showRandomImage();
  }

  // 4. 로드셀 초기화 및 영점 보정
  scale.begin(PIN_HX_DOUT, PIN_HX_SCK);
  delay(500);
  if (scale.is_ready()) {
    baselineWeight = scale.read_average(10);
  }
}

void loop() {
  switch (state) {
    case STATE_IDLE:
      if (scale.is_ready()) {
        long current = scale.read();
        if (abs(current - baselineWeight) > WEIGHT_THRESHOLD) {
          // 손 감지!
          state = STATE_TRIGGERED;
        }
      }
      break;

    case STATE_TRIGGERED:
      // 1) LCD 화면 무작위 사진 전환
      showRandomImage();

      // 2) 세그먼트 롤링 애니메이션
      playSegmentRoulette();

      triggerTimestamp = millis();
      state = STATE_HOLD;
      break;

    case STATE_HOLD:
      if (millis() - triggerTimestamp > 1500) {
        state = STATE_WAIT_RELEASE;
      }
      break;

    case STATE_WAIT_RELEASE:
      if (scale.is_ready()) {
        long current = scale.read_average(3);
        if (abs(current - baselineWeight) < (WEIGHT_THRESHOLD / 2)) {
          // 손 뗌 -> 대기 상태로 복귀
          for (int i = 0; i < 8; i++) lc.setChar(0, i, '-', false);
          delay(200);
          state = STATE_IDLE;
        }
      }
      break;
  }
  delay(10);
}
