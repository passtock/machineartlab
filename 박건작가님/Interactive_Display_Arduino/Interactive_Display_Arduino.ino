/*
 * ======================================================================================
 * [머신아트랩 - 박건 작가님 인터랙티브 아트 시스템]
 * 아두이노 IDE 업로드용 통합 코드 (Interactive_Display_Arduino.ino)
 * ======================================================================================
 * - 보드 설정: ESP32S3 Dev Module
 * - Flash Size: 16MB (128Mb)
 * - PSRAM: "OPI PSRAM"
 * - 필요한 라이브러리: 
 *    1. LovyanGFX
 *    2. TJpg_Decoder
 *    3. LedControl
 *    4. HX711
 * ======================================================================================
 */

#include <Arduino.h>
#include <FS.h>
#include <SD.h>
#include <SPI.h>
#include <LedControl.h>
#include "HX711.h"
#include <TJpg_Decoder.h>

#define LGFX_USE_V1
#include <LovyanGFX.hpp>

// ===================== [1. 확장 GPIO 핀 매핑] =====================
const int PIN_SEG_DIN = 17;
const int PIN_SEG_CLK = 18;
const int PIN_SEG_CS  = 19;
LedControl lc = LedControl(PIN_SEG_DIN, PIN_SEG_CLK, PIN_SEG_CS, 1);

const int PIN_LOADCELL_DOUT = 2;
const int PIN_LOADCELL_SCK  = 3;
HX711 scale;

const int PIN_BUZZER = 10;
const int PIN_SD_CS   = 5;

// ===================== [2. 디스플레이 드라이버] =====================
class LGFX_Custom : public lgfx::LGFX_Device {
  lgfx::Panel_RGB _panel_instance;
  lgfx::Bus_RGB   _bus_instance;
public:
  LGFX_Custom() {
    auto cfg = _bus_instance.config();
    cfg.panel = &_panel_instance;
    cfg.pin_d0 = GPIO_NUM_15; cfg.pin_d1 = GPIO_NUM_7; cfg.pin_d2 = GPIO_NUM_6; cfg.pin_d3 = GPIO_NUM_5;
    cfg.pin_d4 = GPIO_NUM_4; cfg.pin_d5 = GPIO_NUM_9; cfg.pin_d6 = GPIO_NUM_46; cfg.pin_d7 = GPIO_NUM_3;
    cfg.pin_d8 = GPIO_NUM_8; cfg.pin_d9 = GPIO_NUM_16; cfg.pin_d10 = GPIO_NUM_1; cfg.pin_d11 = GPIO_NUM_14;
    cfg.pin_d12 = GPIO_NUM_21; cfg.pin_d13 = GPIO_NUM_47; cfg.pin_d14 = GPIO_NUM_48; cfg.pin_d15 = GPIO_NUM_45;
    cfg.pin_henable = GPIO_NUM_41; cfg.pin_vsync = GPIO_NUM_40; cfg.pin_hsync = GPIO_NUM_39; cfg.pin_pclk = GPIO_NUM_42;
    cfg.freq_write = 16000000;
    cfg.hsync_polarity = 0; cfg.hsync_front_porch = 8; cfg.hsync_pulse_width = 4; cfg.hsync_back_porch = 8;
    cfg.vsync_polarity = 0; cfg.vsync_front_porch = 8; cfg.vsync_pulse_width = 4; cfg.vsync_back_porch = 8;
    cfg.pclk_active_neg = 1;
    _bus_instance.config(cfg);

    auto pcfg = _panel_instance.config();
    pcfg.memory_width = 800; pcfg.memory_height = 480; pcfg.panel_width = 800; pcfg.panel_height = 480;
    pcfg.offset_x = 0; pcfg.offset_y = 0;
    _panel_instance.config(pcfg);
    _panel_instance.setBus(&_bus_instance);
    setPanel(&_panel_instance);
  }
};
LGFX_Custom lcd;

// TJpg_Decoder 콜백
bool tjpgOutput(int16_t x, int16_t y, uint16_t w, uint16_h, uint16_t* bitmap) {
  if (y >= lcd.height()) return 0;
  lcd.pushImage(x, y, w, h, bitmap);
  return 1;
}

// ===================== [3. 변수 및 상태 머신] =====================
const long WEIGHT_TRIGGER_THRESHOLD = 8000;
long baselineWeight = 0;
const int MAX_IMAGES = 120;
String imagePaths[MAX_IMAGES];
int totalImages = 0;
int lastImageIndex = -1;

enum SystemState { STATE_IDLE, STATE_TRIGGERED, STATE_HOLD, STATE_WAIT_RELEASE };
SystemState state = STATE_IDLE;
unsigned long triggerTime = 0;

void scanImagesFromSD() {
  File dir = SD.open("/images");
  if (!dir || !dir.isDirectory()) return;
  totalImages = 0;
  File file = dir.openNextFile();
  while (file && totalImages < MAX_IMAGES) {
    if (!file.isDirectory()) {
      String name = file.name();
      if (name.endsWith(".jpg") || name.endsWith(".JPG")) {
        imagePaths[totalImages++] = String("/images/") + name;
      }
    }
    file = dir.openNextFile();
  }
}

void displayRandomImage() {
  if (totalImages == 0) return;
  int nextIdx = random(0, totalImages);
  if (totalImages > 1 && nextIdx == lastImageIndex) nextIdx = (nextIdx + 1) % totalImages;
  lastImageIndex = nextIdx;
  TJpgDec.drawSdJpg(0, 0, imagePaths[nextIdx].c_str());
}

void playSegmentRoulette() {
  int finalNumbers[8];
  for (int i = 0; i < 8; i++) finalNumbers[i] = random(0, 10);

  for (int frame = 0; frame < 30; frame++) {
    int locked = frame / 4;
    if (locked > 8) locked = 8;
    for (int i = 0; i < 8; i++) {
      if (i < locked) lc.setDigit(0, 7 - i, finalNumbers[i], false);
      else lc.setDigit(0, 7 - i, random(0, 10), false);
    }
    tone(PIN_BUZZER, 600 + (frame * 60), 25);
    delay(25 + (frame * 3));
  }
  for (int i = 0; i < 8; i++) lc.setDigit(0, 7 - i, finalNumbers[i], false);
  tone(PIN_BUZZER, 2000, 150);
  delay(160);
  tone(PIN_BUZZER, 2500, 300);
}

void setSegmentIdle() {
  for (int i = 0; i < 8; i++) lc.setChar(0, i, '-', false);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_BUZZER, OUTPUT);

  lc.shutdown(0, false);
  lc.setIntensity(0, 9);
  lc.clearDisplay(0);
  setSegmentIdle();

  lcd.init();
  lcd.fillScreen(TFT_BLACK);
  TJpgDec.setJpgScale(1);
  TJpgDec.setSwapBytes(true);
  TJpgDec.setCallback(tjpgOutput);

  if (SD.begin(PIN_SD_CS)) {
    scanImagesFromSD();
    displayRandomImage();
  }

  scale.begin(PIN_LOADCELL_DOUT, PIN_LOADCELL_SCK);
  delay(300);
  if (scale.is_ready()) {
    baselineWeight = scale.read_average(10);
  }
}

void loop() {
  switch (state) {
    case STATE_IDLE:
      if (scale.is_ready()) {
        long current = scale.read();
        if (abs(current - baselineWeight) > WEIGHT_TRIGGER_THRESHOLD) {
          state = STATE_TRIGGERED;
        }
      }
      break;
    case STATE_TRIGGERED:
      displayRandomImage();
      playSegmentRoulette();
      triggerTime = millis();
      state = STATE_HOLD;
      break;
    case STATE_HOLD:
      if (millis() - triggerTime > 1500) state = STATE_WAIT_RELEASE;
      break;
    case STATE_WAIT_RELEASE:
      if (scale.is_ready()) {
        long current = scale.read_average(3);
        if (abs(current - baselineWeight) < (WEIGHT_TRIGGER_THRESHOLD / 2)) {
          setSegmentIdle();
          delay(200);
          state = STATE_IDLE;
        }
      }
      break;
  }
  delay(10);
}
