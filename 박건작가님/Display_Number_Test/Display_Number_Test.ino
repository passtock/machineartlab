/*
 * ======================================================================================
 * [머신아트랩 - 박건 작가님] 화면 및 8자리 세그먼트 숫자 출력 단독 테스트 펌웨어
 * ======================================================================================
 * - 목적:
 *    외부 센서(로드셀)나 MicroSD 카드 없이도,
 *    ESP32 화면(LCD)과 MAX7219 8자리 세그먼트에 숫자가 정상 출력되는지 즉시 검증
 * 
 * - 출력 내용:
 *    1. ESP32 온보드 LCD 화면 (800x480):
 *       - 화면 중앙에 커다란 8자리 디지털 숫자 표시 (네온 사이언)
 *       - 0.8초마다 8자리 무작위 난수 및 카운터 실시간 갱신
 *       - 헤더/푸터에 시스템 상태 표시
 *    2. MAX7219 8자리 7세그먼트 (DIN: 17, CLK: 18, CS: 19):
 *       - LCD 화면과 완벽히 동기화된 8자리 숫자 표시
 * ======================================================================================
 */

#include <Arduino.h>

#define LGFX_USE_V1
#include <LovyanGFX.hpp>
#include <lgfx_user/LGFX_ESP32S3_RGB_ESP32-8048S043.h>

static LGFX lcd;

// ===================== [1. 백라이트 및 MAX7219 핀 설정] =====================
const int PIN_LCD_BACKLIGHT = 2; // Sunton ESP32-8048S043 / 8048S070 백라이트 핀

// MAX7219 8자리 7세그먼트 핀
const int PIN_SEG_DIN = 17;
const int PIN_SEG_CLK = 18;
const int PIN_SEG_CS  = 19;

// MAX7219 레지스터 정의
#define MAX7219_REG_NOOP   0x00
#define MAX7219_REG_DIGIT0 0x01
#define MAX7219_REG_DECODE 0x09
#define MAX7219_REG_INTENS 0x0A
#define MAX7219_REG_SCAN   0x0B
#define MAX7219_REG_SHUT   0x0C
#define MAX7219_REG_TEST   0x0F

void max7219_send(byte reg, byte data) {
  digitalWrite(PIN_SEG_CS, LOW);
  shiftOut(PIN_SEG_DIN, PIN_SEG_CLK, MSBFIRST, reg);
  shiftOut(PIN_SEG_DIN, PIN_SEG_CLK, MSBFIRST, data);
  digitalWrite(PIN_SEG_CS, HIGH);
}

void max7219_init() {
  pinMode(PIN_SEG_DIN, OUTPUT);
  pinMode(PIN_SEG_CLK, OUTPUT);
  pinMode(PIN_SEG_CS,  OUTPUT);
  digitalWrite(PIN_SEG_CS, HIGH);

  max7219_send(MAX7219_REG_SHUT, 0x01);   // Normal Operation
  max7219_send(MAX7219_REG_DECODE, 0xFF); // 8자리 Code B 디코드 (0~9, -)
  max7219_send(MAX7219_REG_SCAN, 0x07);   // 8자리 스캔
  max7219_send(MAX7219_REG_INTENS, 0x08); // 밝기 중간
  max7219_send(MAX7219_REG_TEST, 0x00);   // 테스트 OFF
}

void max7219_setNumber(const char* numStr) {
  for (int i = 0; i < 8; i++) {
    char c = numStr[i];
    byte val = 0x0F;
    if (c >= '0' && c <= '9') val = c - '0';
    else if (c == '-') val = 0x0A;
    max7219_send(8 - i, val);
  }
}

// ===================== [2. 화면 갱신 함수] =====================
unsigned long lastUpdate = 0;

void updateDisplays(const char* numStr) {
  // 1. LCD 화면 렌더링
  lcd.startWrite();
  
  // 숫자 카드 박스 배경
  lcd.fillRoundRect(80, 150, 640, 160, 16, lcd.color565(15, 25, 45));
  lcd.drawRoundRect(80, 150, 640, 160, 16, lcd.color565(0, 200, 255));
  lcd.drawRoundRect(82, 152, 636, 156, 14, lcd.color565(0, 100, 180));

  // 커다란 8자리 네온 숫자 표시
  lcd.setTextColor(lcd.color565(0, 255, 200), lcd.color565(15, 25, 45));
  lcd.setTextSize(6);
  lcd.setTextDatum(textdatum_t::middle_center);
  lcd.drawString(numStr, 400, 230);

  // 하단 런타임 정보
  char subText[64];
  snprintf(subText, sizeof(subText), "Time: %lu s   |   Target Number: %s", millis() / 1000, numStr);
  lcd.setTextColor(lcd.color565(180, 180, 180), lcd.color565(10, 12, 20));
  lcd.setTextSize(2);
  lcd.drawString(subText, 400, 350);

  lcd.endWrite();

  // 2. MAX7219 8자리 세그먼트 전송
  max7219_setNumber(numStr);

  Serial.printf("[DISPLAY] Number: %s\n", numStr);
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println(F("\n=================================================="));
  Serial.println(F(" [Machine Art Lab] ESP32 Display & Segment Test   "));
  Serial.println(F("=================================================="));

  // 1. 백라이트 핀 강제 HIGH
  pinMode(PIN_LCD_BACKLIGHT, OUTPUT);
  digitalWrite(PIN_LCD_BACKLIGHT, HIGH);

  // 2. MAX7219 세그먼트 초기화
  max7219_init();
  max7219_setNumber("--------");

  // 3. LCD 화면 초기화
  lcd.init();
  lcd.setBrightness(255);
  lcd.fillScreen(lcd.color565(10, 12, 20)); // 다크 배경

  // 상단 헤더 배너
  lcd.fillRect(0, 0, 800, 80, lcd.color565(20, 30, 55));
  lcd.drawFastHLine(0, 80, 800, lcd.color565(0, 200, 255));
  
  lcd.setTextColor(TFT_WHITE, lcd.color565(20, 30, 55));
  lcd.setTextSize(3);
  lcd.setTextDatum(textdatum_t::middle_center);
  lcd.drawString("MACHINE ART LAB", 400, 30);

  lcd.setTextColor(lcd.color565(0, 200, 255), lcd.color565(20, 30, 55));
  lcd.setTextSize(2);
  lcd.drawString("INTERACTIVE NUMBER DISPLAY TEST", 400, 60);

  // 하단 핀 정보 안내
  lcd.setTextColor(lcd.color565(150, 170, 190), lcd.color565(10, 12, 20));
  lcd.setTextSize(2);
  lcd.drawString("ESP32 LCD Panel + MAX7219 8-Digit Segment", 400, 115);
  lcd.drawString("[ P17:DIN  P18:CLK  P19:CS  P2:Backlight ]", 400, 420);

  // 초기 88888888 1초간 표시
  updateDisplays("88888888");
  delay(1000);
}

void loop() {
  unsigned long now = millis();

  // 0.8초마다 8자리 무작위 난수 갱신
  if (now - lastUpdate >= 800) {
    lastUpdate = now;

    long rand1 = random(1000, 9999);
    long rand2 = random(1000, 9999);
    char buf[16];
    snprintf(buf, sizeof(buf), "%04ld%04ld", rand1, rand2);

    updateDisplays(buf);
  }

  delay(20);
}
