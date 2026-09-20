/*
 * ======================================================================================
 * [머신아트랩 - 박건 작가님 인터랙티브 아트 시스템]
 * ESP32 스마트 디스플레이 단독(All-in-One) 통합 제어 메인 펌웨어
 * ======================================================================================
 * - 하드웨어 구성:
 *    1. ESP32 스마트 디스플레이 (4.3" / 7.0" / 5.0" 등)
 *    2. 5kg 로드셀 + HX711 앰프 키트 (DT, SCK 직결)
 *    3. MAX7219 8자리 7세그먼트 모듈 (DIN, CLK, CS 직결)
 *    4. MicroSD 카드 (/images 폴더 내 무작위 사진)
 *    5. 패시브 부저 (선택 연결 - '띠리리리' 상승 효과음)
 * 
 * - 인터랙션 시나리오:
 *    1. 관람객이 로드셀 원판(100mm)에 손을 올림 (> 100g 하중 감지)
 *    2. 8자리 세그먼트에서 '띠리리리' 카지노 룰렛 감속 롤링 애니메이션 시작
 *    3. 디스플레이 화면에 SD 카드의 무작위 사진 즉시 고속 렌더링 (0.1~0.2초)
 *    4. 8자리 무작위 난수 확정 및 결과 화면 고정
 *    5. 손을 떼면 대기 상태('--------')로 자동 복귀
 * ======================================================================================
 */

#include <Arduino.h>
#include <FS.h>
#include <SD.h>
#include <SPI.h>
#include <LedControl.h>
#include "HX711.h"
#include <TJpg_Decoder.h>
#include "display_config.h"

// ======================================================================================
// [1. 하드웨어 확장 GPIO 핀 매핑]
// 사용하시는 디스플레이 보드 뒷면의 확장 커넥터(IO 포트) 핀 번호에 맞게 지정하세요.
// ======================================================================================

// MAX7219 8자리 7세그먼트 디스플레이 (DIN, CLK, CS)
const int PIN_SEG_DIN = 17;
const int PIN_SEG_CLK = 18;
const int PIN_SEG_CS  = 19;
LedControl lc = LedControl(PIN_SEG_DIN, PIN_SEG_CLK, PIN_SEG_CS, 1);

// HX711 24비트 로드셀 ADC 모듈 (DOUT, SCK)
const int PIN_LOADCELL_DOUT = 2;
const int PIN_LOADCELL_SCK  = 3;
HX711 scale;

// 선택 사항: 패시브 피에조 부저 (미연결 시 소리만 안 나고 정상 작동)
const int PIN_BUZZER = 10;

// 온보드 MicroSD 카드 CS 핀 (일반적인 스마트 디스플레이의 기본 SD CS)
const int PIN_SD_CS = 5;

// ======================================================================================
// [2. 디스플레이 및 그래픽 인스턴스]
// ======================================================================================
LGFX_Configured lcd;

// TJpg_Decoder 화면 고속 전송 콜백
bool tjpgOutput(int16_t x, int16_t y, uint16_t w, uint16_t h, uint16_t* bitmap) {
  if (y >= lcd.height()) return 0;
  lcd.pushImage(x, y, w, h, bitmap);
  return 1;
}

// ======================================================================================
// [3. 시스템 파라미터 및 상태 머신]
// ======================================================================================
const long WEIGHT_TRIGGER_THRESHOLD = 8000; // 손 올림 감지 임계치 (raw 값 차이)
long baselineWeight = 0;                     // 부팅 시 영점(Tare) 기준값

const int MAX_IMAGES = 120;
String imagePaths[MAX_IMAGES];
int totalImages = 0;
int lastImageIndex = -1;

enum SystemState {
  STATE_IDLE,          // 대기: 손 올려지기를 기다림
  STATE_TRIGGERED,     // 손 감지: 띠리리리 롤링 & 사진 전환 실행
  STATE_HOLD_RESULT,   // 결과 유지: 사진 및 숫자 화면 고정
  STATE_WAIT_RELEASE   // 손 뗌 감지: 손을 뗄 때까지 대기
};

SystemState currentState = STATE_IDLE;
unsigned long triggerTimestamp = 0;

// ----------------------------------------------------
// MicroSD 카드의 /images 폴더 내 모든 JPEG 사진 목록 스캔
// ----------------------------------------------------
void scanImagesFromSD() {
  File dir = SD.open("/images");
  if (!dir || !dir.isDirectory()) {
    Serial.println(F("[SD] '/images' 폴더를 찾을 수 없습니다."));
    return;
  }

  totalImages = 0;
  File file = dir.openNextFile();
  while (file && totalImages < MAX_IMAGES) {
    if (!file.isDirectory()) {
      String name = file.name();
      if (name.endsWith(".jpg") || name.endsWith(".JPG") ||
          name.endsWith(".jpeg") || name.endsWith(".JPEG")) {
        imagePaths[totalImages] = String("/images/") + name;
        Serial.printf("[SD IMG #%d] %s\n", totalImages, imagePaths[totalImages].c_str());
        totalImages++;
      }
    }
    file = dir.openNextFile();
  }
  Serial.printf("[SD] 총 %d 개의 이미지 파일을 등록했습니다.\n", totalImages);
}

// ----------------------------------------------------
// 무작위 사진 한 장 화면에 초고속 출력 (0.1초 이내)
// ----------------------------------------------------
void displayRandomImage() {
  if (totalImages == 0) {
    lcd.fillScreen(TFT_BLACK);
    lcd.setTextColor(TFT_RED);
    lcd.setTextSize(2);
    lcd.setCursor(30, 30);
    lcd.println("No JPEG files in SD:/images/");
    return;
  }

  // 직전 사진과 겹치지 않게 무작위 선택
  int nextIdx = random(0, totalImages);
  if (totalImages > 1 && nextIdx == lastImageIndex) {
    nextIdx = (nextIdx + 1) % totalImages;
  }
  lastImageIndex = nextIdx;

  String path = imagePaths[nextIdx];
  Serial.printf("[LCD] 사진 출력: %s\n", path.c_str());

  unsigned long tStart = millis();
  TJpgDec.drawSdJpg(0, 0, path.c_str());
  unsigned long elapsed = millis() - tStart;
  Serial.printf("[LCD] 렌더링 완료! 소요 시간: %lu ms\n", elapsed);
}

// ----------------------------------------------------
// "띠리리리" 8자리 룰렛 감속 롤링 애니메이션
// - 전체 8자리가 빠르게 촤라라락 회전
// - 앞자리부터 차례로 탁! 탁! 탁! 고정되며 회전 속도가 서서히 느려짐
// - 부저에서 피치가 점점 상승하는 '띠리리리' 사운드 동기화
// ----------------------------------------------------
void playSegmentRoulette() {
  int finalNumbers[8];
  for (int i = 0; i < 8; i++) {
    finalNumbers[i] = random(0, 10); // 최종 확정될 난수 8자리
  }

  const int totalFrames = 30; // 전체 회전 프레임
  for (int frame = 0; frame < totalFrames; frame++) {
    int lockedDigits = frame / 4; // 시간이 지남에 따라 앞자리부터 차례로 고정
    if (lockedDigits > 8) lockedDigits = 8;

    for (int digit = 0; digit < 8; digit++) {
      if (digit < lockedDigits) {
        // 이미 멈춘 자리는 확정 번호 표시
        lc.setDigit(0, 7 - digit, finalNumbers[digit], false);
      } else {
        // 돌고 있는 자리는 계속 랜덤 숫자 롤링
        lc.setDigit(0, 7 - digit, random(0, 10), false);
      }
    }

    // 주파수가 점진적으로 상승하는 '띠리리리' 룰렛 사운드 (600Hz -> 2400Hz)
    int freq = 600 + (frame * 60);
    tone(PIN_BUZZER, freq, 25);

    // 프레임 딜레이를 점진적으로 늘려 서서히 멈추는 슬로우다운 감속감 부여
    delay(25 + (frame * 3));
  }

  // 8자리 모두 최종 번호로 확실하게 고정
  for (int i = 0; i < 8; i++) {
    lc.setDigit(0, 7 - i, finalNumbers[i], false);
  }

  // 최종 당첨/확정 "띵-!" 피날레 사운드
  tone(PIN_BUZZER, 2000, 150);
  delay(160);
  tone(PIN_BUZZER, 2500, 300);

  Serial.print(F("[SEGMENT] 최종 8자리 숫자 확정: "));
  for (int i = 0; i < 8; i++) Serial.print(finalNumbers[i]);
  Serial.println();
}

// ----------------------------------------------------
// 세그먼트 대기 상태 표시 ("--------")
// ----------------------------------------------------
void setSegmentIdleDisplay() {
  for (int i = 0; i < 8; i++) {
    lc.setChar(0, i, '-', false);
  }
}

// ======================================================================================
// [4. Setup 초기화]
// ======================================================================================
void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println(F("\n============================================="));
  Serial.println(F("[SYSTEM] 박건 작가님 인터랙티브 아트 시스템 시작"));
  Serial.println(F("============================================="));

  // 1. 부저 핀 초기화
  pinMode(PIN_BUZZER, OUTPUT);

  // 2. MAX7219 7세그먼트 초기화
  lc.shutdown(0, false); // 절전 해제
  lc.setIntensity(0, 9); // 밝기 (0~15)
  lc.clearDisplay(0);
  setSegmentIdleDisplay();

  // 3. LCD 디스플레이 초기화
  lcd.init();
  lcd.setRotation(0);
  lcd.fillScreen(TFT_BLACK);
  lcd.setTextColor(TFT_WHITE);
  lcd.setTextSize(2);
  lcd.setCursor(30, 40);
  lcd.println("Interactive Art Lab Booting...");

  // 4. TJpg_Decoder 초기화
  TJpgDec.setJpgScale(1);
  TJpgDec.setSwapBytes(true);
  TJpgDec.setCallback(tjpgOutput);

  // 5. MicroSD 카드 초기화 및 사진 로드
  if (SD.begin(PIN_SD_CS)) {
    Serial.println(F("[SD] MicroSD 카드 마운트 성공"));
    scanImagesFromSD();
    displayRandomImage(); // 최초 대기 사진 한 장 출력
  } else {
    Serial.println(F("[SD] MicroSD 마운트 실패! (슬롯과 카드 FAT32 포맷 확인)"));
    lcd.setCursor(30, 80);
    lcd.setTextColor(TFT_RED);
    lcd.println("SD Card Error!");
  }

  // 6. 로드셀 HX711 초기화 및 영점(Tare) 측정
  scale.begin(PIN_LOADCELL_DOUT, PIN_LOADCELL_SCK);
  delay(300);
  if (scale.is_ready()) {
    baselineWeight = scale.read_average(10);
    Serial.printf("[LOADCELL] 영점 기준값 설정 완료: %ld\n", baselineWeight);
  } else {
    Serial.println(F("[LOADCELL] HX711 센서 응답 없음. 배선을 확인하세요."));
  }

  // 난수 시드 초기화
  randomSeed(micros());

  // 시작 알림음
  tone(PIN_BUZZER, 1200, 100);
}

// ======================================================================================
// [5. Main Loop]
// ======================================================================================
void loop() {
  switch (currentState) {
    case STATE_IDLE:
      // 로드셀 무게 감지 (손을 올렸는지 확인)
      if (scale.is_ready()) {
        long currentWeight = scale.read();
        long diff = abs(currentWeight - baselineWeight);

        if (diff > WEIGHT_TRIGGER_THRESHOLD) {
          Serial.printf("[EVENT] 손 올림 감지! (편차: %ld)\n", diff);
          currentState = STATE_TRIGGERED;
        }
      }
      break;

    case STATE_TRIGGERED:
      // 1) LCD 화면 무작위 사진 즉시 전환
      displayRandomImage();

      // 2) 7세그먼트 '띠리리리' 룰렛 감속 애니메이션 실행
      playSegmentRoulette();

      triggerTimestamp = millis();
      currentState = STATE_HOLD_RESULT;
      break;

    case STATE_HOLD_RESULT:
      // 최소 1.5초간 결과 유지 후 손 뗌 대기 상태로 전이
      if (millis() - triggerTimestamp > 1500) {
        currentState = STATE_WAIT_RELEASE;
      }
      break;

    case STATE_WAIT_RELEASE:
      // 손을 떼었는지 확인 (하중이 다시 기준값 근처로 내려감)
      if (scale.is_ready()) {
        long currentWeight = scale.read_average(3);
        if (abs(currentWeight - baselineWeight) < (WEIGHT_TRIGGER_THRESHOLD / 2)) {
          Serial.println(F("[EVENT] 손 뗌 감지 -> 대기 화면으로 복귀"));
          setSegmentIdleDisplay();
          delay(200);
          currentState = STATE_IDLE;
        }
      }
      break;
  }
  delay(10);
}
