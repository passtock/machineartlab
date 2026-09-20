/*
 * ======================================================================================
 * [머신아트랩 - 박건 작가님 인터랙티브 키트]
 * 1. 베이스 컨트롤러 코드 (Base Controller)
 * ======================================================================================
 * - 보드: 아두이노 우노(Uno) / 나노(Nano) / ESP32 기본 보드 공용
 * - 입력: 5kg 로드셀 + HX711 24비트 ADC 모듈 (손 올림 하중 감지)
 * - 출력 1: MAX7219 8자리 7세그먼트 디스플레이 ("띠리리리" 룰렛 롤링 애니메이션)
 * - 출력 2: 마그네틱 5핀 도크 트리거 핀 (교체형 ESP32 디스플레이로 사진 변경 신호 전송)
 * - 출력 3(선택): 패시브 부저 (띠리리리 사운드 효과음)
 * 
 * [라이브러리 요구사항]
 * 1. LedControl (by Eberhard Fahle) - 아두이노 라이브러리 매니저에서 설치
 * 2. HX711 (by Bogdan Necula) - 아두이노 라이브러리 매니저에서 설치
 * ======================================================================================
 */

#include <LedControl.h>
#include "HX711.h"

// ===================== [핀 설정] =====================
// 1. MAX7219 8자리 7세그먼트 (DIN, CLK, CS)
const int PIN_MAX7219_DIN = 12;
const int PIN_MAX7219_CLK = 11;
const int PIN_MAX7219_CS  = 10;
LedControl lc = LedControl(PIN_MAX7219_DIN, PIN_MAX7219_CLK, PIN_MAX7219_CS, 1);

// 2. HX711 로드셀 앰프 (DOUT, SCK)
const int PIN_HX711_DOUT = 3;
const int PIN_HX711_SCK  = 2;
HX711 scale;

// 3. 교체형 LCD 화면 모듈 트리거 신호선 (마그네틱 커넥터 Pin 3)
const int PIN_LCD_TRIGGER = 7;

// 4. 패시브 부저 (선택 연결: 미연결 시 소리만 안 남)
const int PIN_BUZZER = 8;

// ===================== [설정 파라미터] =====================
// 손 올림 감지 임계값 (캘리브레이션 전에는 raw 값 차이, 캘리브레이션 후에는 그램(g) 단위)
// 손을 올렸을 때의 변화량 임계치
const long WEIGHT_THRESHOLD = 8000; // raw 값 기준 (scale.read_average() 차이값) 또는 100g

// 시스템 상태 머신
enum SystemState {
  STATE_IDLE,         // 대기 상태 (손 올려지기를 기다림)
  STATE_TRIGGERED,    // 손 올림 감지 -> 띠리리리 롤링 & LCD 트리거 발송
  STATE_HOLD_RESULT,  // 최종 8자리 숫자 및 사진 고정 표시 중
  STATE_WAIT_RELEASE  // 손을 뗄 때까지 대기
};

SystemState currentState = STATE_IDLE;
long baselineWeight = 0;
unsigned long lastTriggerTime = 0;

void setup() {
  Serial.begin(115200);
  Serial.println(F("[SYSTEM] 박건 작가님 인터랙티브 시스템 베이스 시작"));

  // 1. 트리거 핀 초기화 (Active LOW 방식: 평상시 HIGH, 트리거 시 LOW 펄스)
  pinMode(PIN_LCD_TRIGGER, OUTPUT);
  digitalWrite(PIN_LCD_TRIGGER, HIGH);

  // 2. 부저 핀 초기화
  pinMode(PIN_BUZZER, OUTPUT);

  // 3. MAX7219 7세그먼트 초기화
  lc.shutdown(0, false);       // 절전 모드 해제
  lc.setIntensity(0, 8);       // 밝기 (0~15)
  lc.clearDisplay(0);          // 화면 초기화

  // 대기 표시 ("--------")
  for (int i = 0; i < 8; i++) {
    lc.setChar(0, i, '-', false);
  }

  // 4. 로드셀 HX711 초기화 및 영점(Tare) 측정
  scale.begin(PIN_HX711_DOUT, PIN_HX711_SCK);
  delay(500);

  Serial.println(F("[HX711] 영점(Tare) 보정 중... 원판에 손을 올리지 마세요."));
  if (scale.is_ready()) {
    baselineWeight = scale.read_average(10);
    Serial.print(F("[HX711] 영점 기준값 설정 완료: "));
    Serial.println(baselineWeight);
  } else {
    Serial.println(F("[HX711] 센서를 찾을 수 없습니다. 배선을 점검하세요."));
  }

  // 아날로그 미연결 핀으로 랜덤 시드 설정
  randomSeed(analogRead(A0) + analogRead(A1));

  // 시작 비프음
  tone(PIN_BUZZER, 1000, 100);
}

void loop() {
  switch (currentState) {
    case STATE_IDLE:
      checkLoadCellTouch();
      break;

    case STATE_TRIGGERED:
      // 1) 교체형 LCD 화면 모듈에 즉시 트리거 펄스 전송
      sendLcdTrigger();
      
      // 2) 7세그먼트에 "띠리리리" 룰렛 슬롯머신 롤링 애니메이션 재생
      playRouletteAnimation();
      
      // 3) 결과 고정 상태로 전이
      currentState = STATE_HOLD_RESULT;
      lastTriggerTime = millis();
      break;

    case STATE_HOLD_RESULT:
      // 손을 떼었는지 확인 (일정 시간 유지 후)
      if (millis() - lastTriggerTime > 1500) {
        currentState = STATE_WAIT_RELEASE;
      }
      break;

    case STATE_WAIT_RELEASE:
      // 손을 떼었을 때 (무게가 다시 기준치 근처로 내려감)
      if (scale.is_ready()) {
        long currentWeight = scale.read_average(3);
        if (abs(currentWeight - baselineWeight) < (WEIGHT_THRESHOLD / 2)) {
          Serial.println(F("[STATE] 손 뗌 감지 -> 대기 모드로 복귀"));
          // 세그먼트 대기 모드로 복귀
          for (int i = 0; i < 8; i++) {
            lc.setChar(0, i, '-', false);
          }
          delay(300);
          currentState = STATE_IDLE;
        }
      }
      break;
  }
}

// ----------------------------------------------------
// 로드셀 손 올림 하중 감지 함수
// ----------------------------------------------------
void checkLoadCellTouch() {
  if (scale.is_ready()) {
    long current = scale.read();
    long diff = abs(current - baselineWeight);

    // 하중이 기준 임계값을 넘으면 손을 올린 것으로 판정
    if (diff > WEIGHT_THRESHOLD) {
      Serial.print(F("[TOUCH] 손 올림 감지! 감지 편차: "));
      Serial.println(diff);
      currentState = STATE_TRIGGERED;
    }
  }
}

// ----------------------------------------------------
// 교체형 LCD 화면에 전달하는 트리거 신호 (5핀 마그네틱 도크 Pin 3)
// ----------------------------------------------------
void sendLcdTrigger() {
  Serial.println(F("[TRIGGER] LCD 화면 모듈로 트리거 신호(LOW Pulse) 전송"));
  digitalWrite(PIN_LCD_TRIGGER, LOW);
  delay(30); // 30ms LOW 펄스
  digitalWrite(PIN_LCD_TRIGGER, HIGH);
}

// ----------------------------------------------------
// "띠리리리" 슬롯머신/룰렛 롤링 애니메이션
// - 8자리가 촤라라락 회전하다가 왼쪽 자리부터 순차적으로 감속하며 정지!
// - 피에조 부저에서 띠리리리 주파수가 빠르게 상승하며 연출 극대화
// ----------------------------------------------------
void playRouletteAnimation() {
  int finalNumbers[8];
  for (int i = 0; i < 8; i++) {
    finalNumbers[i] = random(0, 10); // 최종 확정될 8자리 난수 생성
  }

  // 롤링 애니메이션 루프:
  // 자리별로 멈추는 시점을 다르게 하여 카지노 룰렛 연출
  const int totalFrames = 30; // 전체 회전 프레임
  
  for (int frame = 0; frame < totalFrames; frame++) {
    int lockedDigits = frame / 4; // 시간이 지남에 따라 앞자리부터 차례로 고정 (0~7)
    if (lockedDigits > 8) lockedDigits = 8;

    // 자리수 렌더링
    for (int digit = 0; digit < 8; digit++) {
      if (digit < lockedDigits) {
        // 이미 멈춘 자리는 최종 확정 번호 출력
        lc.setDigit(0, 7 - digit, finalNumbers[digit], false);
      } else {
        // 아직 돌고 있는 자리는 계속 랜덤 숫자 롤링
        lc.setDigit(0, 7 - digit, random(0, 10), false);
      }
    }

    // "띠리리리" 사운드 주파수 점진 상승 (500Hz -> 2400Hz)
    int freq = 600 + (frame * 60);
    tone(PIN_BUZZER, freq, 25);

    // 회전 속도가 뒤로 갈수록 살짝 늘어지는 슬로우다운(감속) 느낌
    int frameDelay = 25 + (frame * 3);
    delay(frameDelay);
  }

  // 마지막 8자리 모두 최종 번호 고정
  for (int i = 0; i < 8; i++) {
    lc.setDigit(0, 7 - i, finalNumbers[i], false);
  }

  // 최종 당첨/확정 "띵-!" 피날레 사운드
  tone(PIN_BUZZER, 2000, 150);
  delay(160);
  tone(PIN_BUZZER, 2500, 300);

  Serial.print(F("[RESULT] 최종 확정 8자리 숫자: "));
  for (int i = 0; i < 8; i++) {
    Serial.print(finalNumbers[i]);
  }
  Serial.println();
}
