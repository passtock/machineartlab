/*
 * =================================================================================
 * 프로젝트: ESP32-S3 4.3인치 디스플레이 (8048S043 / 800x480 RGB) 테스트
 * 파일 경로: src/ESP32_Display_Test/ESP32_Display_Test.ino
 * 
 * [동작 설명]
 * - PC 아두이노 시리얼 모니터(115200 baud)에서:
 *   - 'u' 전송 시: 숫자 카운트 +1 증가 및 화면 위쪽(Up)으로 이동
 *   - 'd' 전송 시: 숫자 카운트 -1 감소 및 화면 아래쪽(Down)으로 이동
 *   - 'r' 전송 시: 0으로 초기화 및 정중앙 복귀
 * 
 * [⭐️ 아두이노 IDE 툴(Tools) 메뉴 필수 설정]
 * 1. Board: "ESP32S3 Dev Module"
 * 2. PSRAM: "OPI PSRAM"  <--- ⭐️⭐️⭐️ (매우 중요! 800x480 프레임버퍼용 필수)
 * 3. USB CDC On Boot: "Enabled" <--- ⭐️ (시리얼 모니터 통신 필수)
 * 4. Flash Size: "16MB (128Mb)"
 * 5. Partition Scheme: "16M Flash (3MB APP/9.9MB FATFS)"
 * 6. Upload Mode: "UART0 / Hardware CDC"
 * 
 * [필요 라이브러리 (Arduino IDE -> 라이브러리 관리자)]
 * - "GFX Library for Arduino" (Moon On Our Nation 저) v1.4.9 이상
 * =================================================================================
 */

#include <Arduino.h>
#include <Arduino_GFX_Library.h>

// =================================================================================
// [보드 선택] 자신이 가진 보드의 주석(#define)을 1개만 활성화하세요!
// 기본값: 가장 많이 쓰이는 Sunton ESP32-8048S043 (4.3인치 800x480 RGB 디스플레이)
// =================================================================================
#define BOARD_SUNTON_8048S043      // 4.3인치 800x480 (Sunton ESP32-S3)
// #define BOARD_SUNTON_8048S050   // 5.0인치 800x480 (Sunton ESP32-S3)
// #define BOARD_SUNTON_8048S070   // 7.0인치 800x480 (Sunton ESP32-S3)
// #define BOARD_LILYGO_T_DISPLAY_S3 // LilyGO T-Display-S3 (1.9인치 170x320)
// #define BOARD_GENERIC_SPI_ST7789 // 일반 SPI ST7789 디스플레이

// =================================================================================
// 디스플레이 객체 설정
// =================================================================================
#if defined(BOARD_SUNTON_8048S043) || defined(BOARD_SUNTON_8048S050) || defined(BOARD_SUNTON_8048S070)
  // Sunton 4.3" / 5.0" / 7.0" 800x480 RGB 인터페이스 핀맵
  #define TFT_BL 2 // 백라이트 제어 핀

  Arduino_ESP32RGBPanel *bus = new Arduino_ESP32RGBPanel(
      40 /* DE */, 41 /* VSYNC */, 39 /* HSYNC */, 42 /* PCLK */,
      45 /* R0 */, 48 /* R1 */, 47 /* R2 */, 21 /* R3 */, 14 /* R4 */,
      5  /* G0 */, 6  /* G1 */, 7  /* G2 */, 15 /* G3 */, 16 /* G4 */, 4 /* G5 */,
      8  /* B0 */, 3  /* B1 */, 46 /* B2 */, 9  /* B3 */, 1  /* B4 */,
      0 /* hsync_polarity */, 8 /* hsync_front_porch */, 4 /* hsync_pulse_width */, 8 /* hsync_back_porch */,
      0 /* vsync_polarity */, 8 /* vsync_front_porch */, 4 /* vsync_pulse_width */, 8 /* vsync_back_porch */
  );
  Arduino_RGB_Display *gfx = new Arduino_RGB_Display(
      800 /* width */, 480 /* height */, bus, 0 /* rotation */, true /* auto_flush */
  );

#elif defined(BOARD_LILYGO_T_DISPLAY_S3)
  #define TFT_BL 38
  Arduino_DataBus *bus = new Arduino_ESP32LCD8(
      7 /* DC */, 6 /* CS */, 8 /* WR */, 9 /* RD */,
      39 /* D0 */, 40 /* D1 */, 41 /* D2 */, 42 /* D3 */,
      45 /* D4 */, 46 /* D5 */, 47 /* D6 */, 48 /* D7 */
  );
  Arduino_GFX *gfx = new Arduino_ST7789(bus, 5 /* RST */, 0 /* rotation */, true /* IPS */, 170, 320);

#else // 기본 폴백: 일반 SPI 디스플레이
  #define TFT_BL 2
  Arduino_DataBus *bus = new Arduino_HWSPI(11 /* DC */, 10 /* CS */, 12 /* SCK */, 13 /* MOSI */, -1 /* MISO */);
  Arduino_GFX *gfx = new Arduino_ST7789(bus, 1 /* RST */, 0 /* rotation */, true /* IPS */, 240, 320);
#endif

// =================================================================================
// 전역 변수
// =================================================================================
int counter = 0;          // 표시할 숫자 값
int currentY = 0;          // 화면 상의 숫자 Y 좌표 위치
int screenW = 800;
int screenH = 480;

void drawInterface() {
  // 배경 전체 지우기 (진한 네이비 블랙)
  gfx->fillScreen(0x0810);

  // 상단 헤더 박스
  gfx->fillRect(0, 0, screenW, 50, 0x1925);
  gfx->setTextSize(2);
  gfx->setTextColor(0x07FF); // Cyan
  gfx->setCursor(20, 16);
  gfx->println("ESP32-S3 DISPLAY CONTROLLER TEST");

  // 안내 문구 (하단)
  gfx->fillRect(0, screenH - 45, screenW, 45, 0x10A2);
  gfx->setTextSize(2);
  gfx->setTextColor(0xFFE0); // Yellow
  gfx->setCursor(20, screenH - 30);
  gfx->println("Commands: Send 'u' to UP (+), 'd' to DOWN (-)");

  // 현재 숫자 다시 그리기
  drawNumber();
}

void drawNumber() {
  // 숫자 영역 부분 지우기 (잔상 제거용 사각형)
  gfx->fillRect(50, 60, screenW - 100, screenH - 120, 0x0810);

  // 중앙 그리드 가이드라인 (선택적 시각 효과)
  gfx->drawFastHLine(80, screenH / 2, screenW - 160, 0x2124);

  // 숫자 크기 및 폰트 설정
  gfx->setTextSize(6);

  // 숫자 값에 따른 색상 변화 (양수: 그린, 0: 화이트, 음수: 오렌지레드)
  if (counter > 0) {
    gfx->setTextColor(0x07E0); // Green
  } else if (counter < 0) {
    gfx->setTextColor(0xF980); // Orange-Red
  } else {
    gfx->setTextColor(0xFFFF); // White
  }

  // 숫자 텍스트 화면 중앙 정렬 계산
  char buf[32];
  sprintf(buf, "%d", counter);
  int textLen = strlen(buf);
  int approxCharWidth = 36; // TextSize 6 기준 대략 너비
  int startX = (screenW - (textLen * approxCharWidth)) / 2;

  gfx->setCursor(startX, currentY);
  gfx->print(buf);

  // 상태 보조 텍스트
  gfx->setTextSize(2);
  gfx->setTextColor(0x8410); // 회색
  gfx->setCursor(startX - 20, currentY + 60);
  gfx->printf("[ POS Y: %d px ]", currentY);
}

void setup() {
  // 1. 시리얼 통신 시작 (PC와 통신)
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\n========================================");
  Serial.println("  ESP32-S3 Display Test Starting...");
  Serial.println("========================================");

  // 2. 백라이트 핀 켜기
  #ifdef TFT_BL
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);
  #endif

  // 3. 디스플레이 초기화
  if (!gfx->begin()) {
    Serial.println("gfx->begin() FAILED!");
  } else {
    Serial.println("Display Initialized OK!");
  }

  screenW = gfx->width();
  screenH = gfx->height();
  currentY = (screenH / 2) - 25; // 초기 Y 좌표: 화면 세로 정중앙

  // 4. 초기 화면 그리기
  drawInterface();

  Serial.println("Ready! Type 'u' (Up) or 'd' (Down) in Serial Monitor and press Enter.");
}

void loop() {
  // 시리얼 입력 감지
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    // 줄바꿈 문자 무시
    if (cmd == '\r' || cmd == '\n' || cmd == ' ') {
      return;
    }

    if (cmd == 'u' || cmd == 'U') {
      counter++;
      currentY -= 20; // 숫자를 물리적으로 화면 위쪽으로 이동
      if (currentY < 70) currentY = 70; // 상단 헤더 침범 방지

      Serial.printf(">> [UP]   Counter = %d, PosY = %d\n", counter, currentY);
      drawNumber();
    } 
    else if (cmd == 'd' || cmd == 'D') {
      counter--;
      currentY += 20; // 숫자를 물리적으로 화면 아래쪽으로 이동
      if (currentY > screenH - 120) currentY = screenH - 120; // 하단 바 침범 방지

      Serial.printf(">> [DOWN] Counter = %d, PosY = %d\n", counter, currentY);
      drawNumber();
    } 
    else if (cmd == 'r' || cmd == 'R') {
      // 보너스: 리셋 기능
      counter = 0;
      currentY = (screenH / 2) - 25;
      Serial.println(">> [RESET] Reset to Center (0)");
      drawNumber();
    }
  }
}
