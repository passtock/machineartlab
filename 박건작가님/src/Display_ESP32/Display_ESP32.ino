/*
 * ======================================================================================
 * [머신아트랩 - 박건 작가님 인터랙티브 키트]
 * 2. 교체형 ESP32 스마트 디스플레이 모듈 코드 (Display ESP32)
 * ======================================================================================
 * - 대상 디스플레이: 
 *    - ESP32 4.3인치 스마트 TFT (800x480)
 *    - ESP32 7.0인치 스마트 IPS (800x480)
 *    - Waveshare ESP32-S3 5인치 / LILYGO 2.1인치 / Happy House 4인치 등
 * - 저장소: 온보드 MicroSD 카드 (FAT32 포맷, /images 폴더 내 jpg 사진들)
 * - 인터페이스: 마그네틱 5핀 도크 (5V, GND, Trigger 신호선)
 * - 동작:
 *    1. 부팅 시 SD 카드의 /images 폴더 내 모든 JPEG 사진 인덱싱
 *    2. 베이스 컨트롤러로부터 Trigger(LOW 펄스) 수신 시 무작위 사진 선택
 *    3. 화면에 초고속 디코딩 및 렌더링
 * 
 * [라이브러리 요구사항]
 * 1. LovyanGFX 또는 TFT_eSPI (화면 그래픽 드라이버)
 * 2. TJpg_Decoder (초고속 JPEG 하드웨어 디코더)
 * 3. SD 또는 SD_MMC (ESP32 내장 SD 라이브러리)
 * ======================================================================================
 */

#include <Arduino.h>
#include <FS.h>
#include <SD.h>
#include <SPI.h>

// 고속 디스플레이 라이브러리 (LovyanGFX 추천 - 모든 ESP32 화면 호환)
#define LGFX_USE_V1
#include <LovyanGFX.hpp>
#include <TJpg_Decoder.h>

// ===================== [하드웨어 핀 설정] =====================
// 마그네틱 커넥터 5핀 중 Trigger 입력 핀 (Base Controller의 신호 수신)
const int PIN_TRIGGER_INPUT = 4; // 각 ESP32 모듈의 가용 GPIO로 설정 (기본: GPIO 4)

// SD 카드 핀 (ESP32 일체형 모듈의 기본 온보드 슬롯 핀)
// 보통 VSPI/HSPI 또는 SD_MMC(1-bit/4-bit)를 사용합니다.
const int PIN_SD_CS = 5; 

// ===================== [LGFX 디스플레이 인스턴스] =====================
// 모듈 종류(4.3인치, 7.0인치, 5.0인치 등)에 맞는 설정을 활성화합니다.
class LGFX : public lgfx::LGFX_Device {
  lgfx::Panel_ST7701 _panel_instance; // 또는 Panel_RGB, Panel_ILI9488 등 모듈별 패널
  lgfx::Bus_RGB      _bus_instance;
public:
  LGFX() {
    // 사용하시는 ESP32 스마트 디스플레이 기종의 보드 프리셋이나 기본 초기화 적용
    // (대부분의 ESP32 스마트 디스플레이 완제품은 제조사 제공 lgfx_user.h 한 줄로 매핑 가능)
  }
};

LGFX lcd;

// ===================== [이미지 파일 관리] =====================
const int MAX_IMAGES = 100;
String imageFiles[MAX_IMAGES];
int totalImageCount = 0;
int lastImageIndex = -1;

// TJpg_Decoder 콜백 함수: 디코딩된 픽셀 블록을 LCD에 직접 고속 전송
bool tjpgOutputCallback(int16_t x, int16_t y, uint16_t w, uint16_t h, uint16_t* bitmap) {
  if (y >= lcd.height()) return 0;
  lcd.pushImage(x, y, w, h, bitmap);
  return 1;
}

// ----------------------------------------------------
// SD 카드의 /images 디렉토리 탐색 및 파일 목록 로드
// ----------------------------------------------------
void scanImageDirectory() {
  File root = SD.open("/images");
  if (!root || !root.isDirectory()) {
    Serial.println(F("[SD] /images 폴더를 찾을 수 없습니다."));
    return;
  }

  totalImageCount = 0;
  File file = root.openNextFile();
  while (file && totalImageCount < MAX_IMAGES) {
    if (!file.isDirectory()) {
      String fileName = file.name();
      if (fileName.endsWith(".jpg") || fileName.endsWith(".JPG") ||
          fileName.endsWith(".jpeg") || fileName.endsWith(".JPEG")) {
        imageFiles[totalImageCount] = String("/images/") + fileName;
        Serial.print(F("[IMAGE FOUND] "));
        Serial.println(imageFiles[totalImageCount]);
        totalImageCount++;
      }
    }
    file = root.openNextFile();
  }
  Serial.printf("[SD] 총 %d 개의 이미지 파일을 로드했습니다.\n", totalImageCount);
}

// ----------------------------------------------------
// 무작위 사진 한 장 화면에 출력
// ----------------------------------------------------
void displayRandomImage() {
  if (totalImageCount == 0) {
    lcd.fillScreen(TFT_BLACK);
    lcd.setTextColor(TFT_RED);
    lcd.setTextSize(2);
    lcd.setCursor(20, 20);
    lcd.println("No images in /images!");
    return;
  }

  // 이전과 다른 무작위 사진 선택
  int nextIndex = random(0, totalImageCount);
  if (totalImageCount > 1 && nextIndex == lastImageIndex) {
    nextIndex = (nextIndex + 1) % totalImageCount;
  }
  lastImageIndex = nextIndex;

  String path = imageFiles[nextIndex];
  Serial.printf("[DISPLAY] 사진 로드 중: %s\n", path.c_str());

  // TJpg_Decoder로 화면 (0, 0) 좌표에 렌더링
  unsigned long t0 = millis();
  TJpgDec.drawSdJpg(0, 0, path.c_str());
  unsigned long elapsed = millis() - t0;

  Serial.printf("[DISPLAY] 렌더링 완료! 소요 시간: %lu ms\n", elapsed);
}

void setup() {
  Serial.begin(115200);
  Serial.println(F("[ESP32 DISPLAY] 인터랙티브 LCD 모듈 부팅"));

  // 1. 트리거 입력 핀 설정 (내부 풀업 활성화: 베이스에서 LOW 신호 수신)
  pinMode(PIN_TRIGGER_INPUT, INPUT_PULLUP);

  // 2. LCD 화면 초기화
  lcd.init();
  lcd.setRotation(0);
  lcd.fillScreen(TFT_BLACK);
  lcd.setTextColor(TFT_WHITE);
  lcd.setTextSize(2);
  lcd.setCursor(30, 30);
  lcd.println("Loading Machine Art Lab...");

  // 3. TJpg_Decoder 초기화
  TJpgDec.setJpgScale(1); // 1:1 원본 비율
  TJpgDec.setSwapBytes(true);
  TJpgDec.setCallback(tjpgOutputCallback);

  // 4. MicroSD 카드 초기화
  if (!SD.begin(PIN_SD_CS)) {
    Serial.println(F("[SD] SD 카드 마운트 실패!"));
    lcd.setCursor(30, 70);
    lcd.setTextColor(TFT_RED);
    lcd.println("SD Mount Failed!");
    return;
  }
  Serial.println(F("[SD] SD 카드 인식 성공"));

  // 5. 이미지 파일 스캔
  scanImageDirectory();

  // 최초 1회 첫 화면 이미지 표시
  displayRandomImage();
}

// 이전 트리거 핀 상태 저장
int lastTriggerState = HIGH;

void loop() {
  // 베이스 컨트롤러의 트리거 신호 감지 (Falling Edge: HIGH -> LOW)
  int currentTriggerState = digitalRead(PIN_TRIGGER_INPUT);

  if (lastTriggerState == HIGH && currentTriggerState == LOW) {
    Serial.println(F("[EVENT] 로드셀 터치 트리거 감지 -> 사진 무작위 전환!"));
    displayRandomImage();
    delay(150); // 디바운스
  }

  lastTriggerState = currentTriggerState;
  delay(10);
}
