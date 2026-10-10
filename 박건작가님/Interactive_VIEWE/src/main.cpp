/*
 * ======================================================================================
 * [머신아트랩 - 박건 작가님 인터랙티브 아트 시스템]
 * VIEWE UEDX80480043E-WB-A/B 단독 통합 펌웨어
 * ======================================================================================
 * - 하드웨어:
 *    1. VIEWE 4.3" 800x480 ESP32-S3 보드 (온보드 RGB 화면 + MicroSD)
 *    2. 2.8" ST7789 240x320 정보 LCD   (공유 SPI)
 *    3. MAX7219 8자리 7세그먼트          (공유 SPI)
 *    4. 5kg 로드셀 + HX711               (GPIO17 / GPIO38)
 *    배선은 ../배선표_및_다이어그램.html 참고
 *
 * - 시나리오:
 *    대기   : 세그먼트 '--------', 메인 화면 대기 사진, 정보 LCD 실시간 하중 표시
 *    손 올림: 메인 화면 SD:/images 무작위 사진 + 세그먼트 '띠리리리' 감속 룰렛
 *    결과   : 8자리 숫자 확정, 정보 LCD에 번호·사진 이름 표시
 *    손 뗌  : 대기 상태로 복귀
 * ======================================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include "HX711.h"
#include "pins.h"
#include "lgfx_displays.h"
#include "max7219.h"

// ======================================================================================
// [1. 조정 파라미터]
// ======================================================================================
const long  TRIGGER_THRESHOLD  = 8000;  // 손 올림 판정 (HX711 raw 값 차이). 시리얼/정보LCD 값 보고 조정
const long  RELEASE_THRESHOLD  = 4000;  // 손 뗌 판정
const uint32_t HOLD_MIN_MS     = 1500;  // 결과 최소 유지 시간
const uint8_t  SEG_INTENSITY   = 8;     // MAX7219 밝기 0~15
const uint8_t  MAIN_BRIGHTNESS = 255;   // 4.3" 백라이트 0~255
const uint32_t SD_FREQ         = 20000000;

// ======================================================================================
// [2. 장치 인스턴스]
// ======================================================================================
MainLCD mainLcd;
InfoLCD infoLcd;
Max7219 seg(PIN_SEG_CS);
HX711   scale;

const int MAX_IMAGES = 200;
String imagePaths[MAX_IMAGES];
int  totalImages = 0;
int  lastImageIndex = -1;
bool sdOk = false;
bool hxOk = false;

long baseline = 0;     // 영점 (대기 중 천천히 추적)
long lastDiff = 0;
char lastNumber[9] = "--------";
String lastImageName = "-";

enum State { IDLE, TRIGGERED, HOLD_RESULT, WAIT_RELEASE };
State state = IDLE;
uint32_t triggerAt = 0;

// ======================================================================================
// [3. 부저 (선택)]
// ======================================================================================
void beep(int freq, int ms) {
  if (PIN_BUZZER >= 0) tone(PIN_BUZZER, freq, ms);
}

// ======================================================================================
// [4. 정보 LCD (2.8") 화면]
// ======================================================================================
const uint16_t C_BG     = 0x0841;
const uint16_t C_HEADER = 0x10A6;
const uint16_t C_ACCENT = 0x05FF;
const uint16_t C_DIM    = 0x8C71;

const char* stateName(State s) {
  switch (s) {
    case IDLE:         return "READY";
    case TRIGGERED:    return "ROLLING...";
    case HOLD_RESULT:  return "RESULT";
    case WAIT_RELEASE: return "RELEASE HAND";
  }
  return "";
}

void infoDrawFrame() {
  infoLcd.fillScreen(C_BG);
  infoLcd.fillRect(0, 0, 320, 34, C_HEADER);
  infoLcd.drawFastHLine(0, 34, 320, C_ACCENT);
  infoLcd.setTextDatum(textdatum_t::middle_left);
  infoLcd.setFont(&fonts::Font2);
  infoLcd.setTextColor(TFT_WHITE, C_HEADER);
  infoLcd.drawString("MACHINE ART LAB", 10, 17);
  infoLcd.setTextColor(C_DIM, C_BG);
  infoLcd.drawString("LOAD", 10, 92);
  infoLcd.drawString("NUMBER", 10, 132);
  infoLcd.drawString("IMAGE", 10, 212);
}

void infoDrawState() {
  infoLcd.setFont(&fonts::Font4);
  infoLcd.setTextDatum(textdatum_t::middle_left);
  uint16_t col = (state == IDLE) ? TFT_GREENYELLOW : (state == WAIT_RELEASE ? TFT_ORANGE : C_ACCENT);
  infoLcd.fillRect(0, 40, 320, 34, C_BG);
  infoLcd.setTextColor(col, C_BG);
  infoLcd.drawString(stateName(state), 10, 57);

  infoLcd.setFont(&fonts::Font2);
  infoLcd.setTextDatum(textdatum_t::middle_right);
  infoLcd.setTextColor(sdOk ? C_DIM : TFT_RED, C_BG);
  char buf[32];
  snprintf(buf, sizeof(buf), sdOk ? "SD %d img" : "SD ERROR", totalImages);
  infoLcd.drawString(buf, 310, 50);
  infoLcd.setTextColor(hxOk ? C_DIM : TFT_RED, C_BG);
  infoLcd.drawString(hxOk ? "HX711 OK" : "HX711 ERR", 310, 66);
}

void infoDrawLoad(long diff) {
  const int x = 60, y = 84, w = 250, h = 16;
  long full = TRIGGER_THRESHOLD * 2;
  int fill = (int)constrain(labs(diff) * w / full, 0L, (long)w);
  int mark = (int)(TRIGGER_THRESHOLD * w / full);
  uint16_t col = labs(diff) > TRIGGER_THRESHOLD ? TFT_ORANGE : C_ACCENT;
  infoLcd.startWrite();
  infoLcd.fillRect(x, y, fill, h, col);
  infoLcd.fillRect(x + fill, y, w - fill, h, C_HEADER);
  infoLcd.drawFastVLine(x + mark, y - 3, h + 6, TFT_WHITE);
  infoLcd.endWrite();

  infoLcd.setFont(&fonts::Font2);
  infoLcd.setTextDatum(textdatum_t::top_right);
  infoLcd.setTextColor(C_DIM, C_BG);
  char buf[24];
  snprintf(buf, sizeof(buf), "   raw %+ld", diff);
  infoLcd.drawString(buf, 310, 104);
}

void infoDrawNumber(const char* num, uint16_t col = TFT_WHITE) {
  infoLcd.fillRect(0, 142, 320, 56, C_BG);
  infoLcd.setFont(&fonts::Font7);   // 7세그먼트 스타일 폰트
  infoLcd.setTextDatum(textdatum_t::middle_center);
  infoLcd.setTextColor(col, C_BG);
  // Font7은 숫자/'-'/'.'/':'만 지원
  infoLcd.drawString(num, 160, 170);
}

void infoDrawImage() {
  infoLcd.fillRect(60, 202, 260, 22, C_BG);
  infoLcd.setFont(&fonts::Font2);
  infoLcd.setTextDatum(textdatum_t::middle_left);
  infoLcd.setTextColor(TFT_WHITE, C_BG);
  infoLcd.drawString(lastImageName.c_str(), 60, 212);
}

// ======================================================================================
// [5. SD 이미지 → 메인 4.3" 화면]
// ======================================================================================
void scanImages() {
  File dir = SD.open("/images");
  if (!dir || !dir.isDirectory()) {
    Serial.println(F("[SD] '/images' 폴더 없음"));
    return;
  }
  totalImages = 0;
  for (File f = dir.openNextFile(); f && totalImages < MAX_IMAGES; f = dir.openNextFile()) {
    if (f.isDirectory()) continue;
    String name = f.name();
    String lower = name;
    lower.toLowerCase();
    if (name.startsWith(".")) continue;             // macOS 숨김파일(._xxx.jpg) 제외
    if (lower.endsWith(".jpg") || lower.endsWith(".jpeg")) {
      imagePaths[totalImages++] = "/images/" + name;
    }
  }
  Serial.printf("[SD] 이미지 %d장 등록\n", totalImages);
}

void showMessage(const char* line1, const char* line2 = nullptr) {
  mainLcd.fillScreen(TFT_BLACK);
  mainLcd.setFont(&fonts::Font4);
  mainLcd.setTextDatum(textdatum_t::middle_center);
  mainLcd.setTextColor(TFT_WHITE);
  mainLcd.drawString(line1, 400, 220);
  if (line2) {
    mainLcd.setTextColor(TFT_RED);
    mainLcd.drawString(line2, 400, 260);
  }
}

void showRandomImage() {
  if (totalImages == 0) {
    showMessage("No JPEG in SD:/images/");
    lastImageName = "(none)";
    return;
  }
  int idx = random(totalImages);
  if (totalImages > 1 && idx == lastImageIndex) idx = (idx + 1) % totalImages;
  lastImageIndex = idx;

  const String& path = imagePaths[idx];
  uint32_t t0 = millis();
  mainLcd.fillScreen(TFT_BLACK);
  // 800x480보다 크거나 작으면 비율 유지해 화면에 맞춤 (scale 0 = auto fit)
  bool ok = mainLcd.drawJpgFile(SD, path.c_str(), 0, 0, 800, 480, 0, 0, 0.0f, 0.0f,
                                datum_t::middle_center);
  Serial.printf("[LCD] %s (%s, %lu ms)\n", path.c_str(), ok ? "OK" : "FAIL", millis() - t0);
  lastImageName = path.substring(8);   // "/images/" 제거
}

// ======================================================================================
// [6. 세그먼트 '띠리리리' 감속 룰렛]
// ======================================================================================
void playRoulette() {
  uint8_t finalDigits[8];
  for (int i = 0; i < 8; i++) finalDigits[i] = random(10);

  const int totalFrames = 36;
  char shown[9] = {0};
  for (int frame = 0; frame < totalFrames; frame++) {
    int locked = min(frame / 4, 8);   // 왼쪽부터 한 자리씩 고정
    for (int i = 0; i < 8; i++) {
      uint8_t d = (i < locked) ? finalDigits[i] : random(10);
      seg.setDigit(i, d);
      shown[i] = '0' + d;
    }
    if (frame % 3 == 0) infoDrawNumber(shown, C_DIM);
    beep(600 + frame * 50, 25);
    delay(25 + frame * 3);            // 점점 느려지는 감속감
  }

  for (int i = 0; i < 8; i++) {
    seg.setDigit(i, finalDigits[i]);
    lastNumber[i] = '0' + finalDigits[i];
  }
  lastNumber[8] = '\0';
  infoDrawNumber(lastNumber, TFT_GREENYELLOW);

  beep(2000, 150);
  delay(160);
  beep(2500, 300);
  Serial.printf("[SEG] 확정 번호: %s\n", lastNumber);
}

// ======================================================================================
// [7. 상태 전환]
// ======================================================================================
void setState(State s) {
  state = s;
  infoDrawState();
}

// ======================================================================================
// [8. setup]
// ======================================================================================
void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println(F("\n[SYSTEM] 박건 작가님 인터랙티브 시스템 (VIEWE 4.3\") 시작"));

  // 0) 공유 SPI 버스의 모든 CS를 먼저 HIGH로 → 초기화 중 오동작 방지
  pinMode(PIN_SD_CS,   OUTPUT); digitalWrite(PIN_SD_CS,   HIGH);
  pinMode(PIN_INFO_CS, OUTPUT); digitalWrite(PIN_INFO_CS, HIGH);
  pinMode(PIN_SEG_CS,  OUTPUT); digitalWrite(PIN_SEG_CS,  HIGH);
  pinMode(PIN_INFO_DC, OUTPUT);
  // HX711 SCK(GPIO38)를 LOW로 → HX711 동작 + GT911 터치칩 리셋 유지
  pinMode(PIN_HX_SCK,  OUTPUT); digitalWrite(PIN_HX_SCK,  LOW);

  // 1) 메인 4.3" 화면
  mainLcd.init();
  mainLcd.setBrightness(MAIN_BRIGHTNESS);
  showMessage("Interactive Art Lab - Booting...");

  // 2) 2.8" 정보 LCD (이 시점에 SPI2 버스와 Arduino SPI 객체가 함께 초기화됨)
  infoLcd.init();
  infoLcd.setRotation(1);   // 가로 320x240. 거꾸로면 3
  infoDrawFrame();

  // 3) MAX7219
  seg.begin(SEG_INTENSITY);
  seg.print("88888888");

  // 4) MicroSD (같은 SPI 버스, CS=10)
  sdOk = SD.begin(PIN_SD_CS, SPI, SD_FREQ);
  if (sdOk) {
    Serial.println(F("[SD] 마운트 성공"));
    scanImages();
  } else {
    Serial.println(F("[SD] 마운트 실패 (FAT32 포맷/카드 삽입 확인)"));
  }

  // 5) HX711 영점
  scale.begin(PIN_HX_DT, PIN_HX_SCK);
  uint32_t t0 = millis();
  while (!scale.is_ready() && millis() - t0 < 1500) delay(10);
  hxOk = scale.is_ready();
  if (hxOk) {
    baseline = scale.read_average(10);
    Serial.printf("[HX711] 영점: %ld\n", baseline);
  } else {
    Serial.println(F("[HX711] 응답 없음 (DT=17, SCK=38, 전원 확인)"));
  }

  randomSeed(esp_random());

  // 6) 대기 화면
  if (sdOk) showRandomImage(); else showMessage("Interactive Art Lab", "SD Card Error!");
  seg.print("--------");
  infoDrawNumber(lastNumber, C_DIM);
  infoDrawImage();
  setState(IDLE);
  beep(1200, 100);
}

// ======================================================================================
// [9. loop]
// ======================================================================================
void loop() {
  static uint32_t lastInfoDraw = 0;
  static uint32_t lastSegRefresh = 0;

  switch (state) {
    case IDLE:
      if (scale.is_ready()) {
        long v = scale.read();
        lastDiff = v - baseline;
        if (labs(lastDiff) > TRIGGER_THRESHOLD) {
          Serial.printf("[EVENT] 손 올림 감지 (diff %ld)\n", lastDiff);
          setState(TRIGGERED);
        } else if (labs(lastDiff) < RELEASE_THRESHOLD / 2) {
          baseline += (v - baseline) / 64;   // 온도 드리프트 천천히 추적
        }
      }
      break;

    case TRIGGERED:
      showRandomImage();
      infoDrawImage();
      playRoulette();
      triggerAt = millis();
      setState(HOLD_RESULT);
      break;

    case HOLD_RESULT:
      if (millis() - triggerAt > HOLD_MIN_MS) setState(WAIT_RELEASE);
      break;

    case WAIT_RELEASE:
      if (scale.is_ready()) {
        long v = scale.read();
        lastDiff = v - baseline;
        if (labs(lastDiff) < RELEASE_THRESHOLD) {
          Serial.println(F("[EVENT] 손 뗌 → 대기"));
          seg.print("--------");
          infoDrawNumber(lastNumber, C_DIM);
          delay(200);
          setState(IDLE);
        }
      }
      break;
  }

  // 정보 LCD 하중 바 갱신 (5Hz)
  if (millis() - lastInfoDraw > 200) {
    lastInfoDraw = millis();
    infoDrawLoad(lastDiff);
  }

  // MAX7219 설정 주기적 재기록 (BOOT 버튼/노이즈로 깨진 경우 자동 복구)
  if (state == IDLE && millis() - lastSegRefresh > 5000) {
    lastSegRefresh = millis();
    seg.refreshConfig(SEG_INTENSITY);
    seg.print("--------");
  }

  delay(5);
}
