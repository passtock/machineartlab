/*
 * ============================================================================
 * [손/손가락 10개 서보 모터 1:1 개별 제어 - 10개 푸시 버튼]
 * 
 * - 버튼 핀 연결 (내부 풀업 INPUT_PULLUP 사용 -> 별도 저항 불필요):
 *     1) 한 쪽 핀  -> GND (공통 그라운드)
 *     2) 다른 쪽 핀 -> 아두이노 아날로`그 입력 핀:
 *        - 왼손  5개 (SG1 ~ SG5)  : A0, A3, A4, A10, A11
 *        - 오른손 5개 (SD1 ~ SD5) : A5, A6, A7, A8,  A9
 *        * 버튼을 누르면 LOW(GND), 떼면 HIGH(5V)가 됩니다.
 * 
 * - 서보 모터 핀 연결:
 *     - 왼손  (SG1 ~ SG5)  : 디지털 2, 3, 4, 5, 6 번 핀
 *     - 오른손 (SD1 ~ SD5) : 디지털 7, 8, 9, 10, 11 번 핀
 * 
 * - 전원 릴레이/MOSFET 제어 핀:
 *     디지털 12 번 핀 (LOW = 전원 ON / HIGH = 전원 OFF)
 * 
 * - 실시간 각도 추종 방식 (Non-blocking):
 *     10개 손가락이 독립적으로 동작하며, 누르고 있는 버튼에 해당하는 손가락만
 *     실시간으로 '쥔 상태'로 이동하고 손을 떼면 즉시 '펴진 상태'로 부드럽게 복귀합니다.
 * ============================================================================
 */

#include <Arduino.h>
#include <Servo.h>

// ============================================================================
// 1. 핀 번호 설정
// ============================================================================
// 서보 모터 10개와 1:1 매칭되는 버튼 핀 번호 배열
// [0~4]: 왼손 (SG1 ~ SG5)
// [5~9]: 오른손 (SD1 ~ SD5)
// ※ 참고: 만약 왼손 배선 순서를 handv.0 기준(G1=A0, G2=A10, G3=A11, G4=A3, G5=A4)으로 하셨다면
//   왼손 배열 순서를 { A0, A10, A11, A3, A4 } 로 변경하시면 됩니다.
const int BUTTON_PINS[10] = {
  A0, A3, A4, A10, A11,   // 왼손: SG1, SG2, SG3, SG4, SG5
  A5, A6, A7, A8,  A9     // 오른손: SD1, SD2, SD3, SD4, SD5
};

// 버튼/서보 이름 (시리얼 모니터 확인용)
const char* FINGER_NAMES[10] = {
  "Left-1 (A0)", "Left-2 (A3)", "Left-3 (A4)", "Left-4 (A10)", "Left-5 (A11)",
  "Right-1 (A5)", "Right-2 (A6)", "Right-3 (A7)", "Right-4 (A8)", "Right-5 (A9)"
};

// 서보 모터 전원 제어 핀 (릴레이 또는 트랜지스터)
const int POWER_SERVO_PIN = 12;

// 서보 모터 10개에 연결된 아두이노 핀 번호 배열
const int SERVO_PINS[10] = {
  2,  3,  4,  5,  6,   // 왼손: SG1, SG2, SG3, SG4, SG5
  7,  8,  9,  10, 11   // 오른손: SD1, SD2, SD3, SD4, SD5
};

// ============================================================================
// 2. 서보 각도 및 동작 모드 설정
// ============================================================================
// [펴진 상태 (시작 각도 / 버튼을 뗐을 때)]
// 왼손: 0, 0, 0, 0, 0
// 오른손: 100, 100, 120, 100, 120
const int OPEN_ANGLES[10] = {
  0,   0,   0,   0,   0,     // 왼손 (SG1 ~ SG5)
  100, 100, 120, 100, 120    // 오른손 (SD1 ~ SD5) - 시작 각도
};

// [쥔 상태 (버튼을 눌렀을 때 목표 각도)]
// 왼손: 150, 150, 150, 150, 180
// 오른손: 0, 0, 0, 0, 0 (0으로 갈수록 쥐어짐)
const int CLOSE_ANGLES[10] = {
  150, 150, 150, 150, 180,   // 왼손 (SG1 ~ SG5)
  0,   0,   0,   0,   0      // 오른손 (SD1 ~ SD5) - 쥔 상태
};

/*
 * 동작 모드 선택:
 *   MODE 1 : 버튼을 누르면 실시간으로 쥐어지고, 떼면 실시간으로 펴짐 (기본값, 즉각 반응)
 *   MODE 2 : 버튼을 누를 때마다 해당 손가락의 [쥔 상태 <-> 펴진 상태] 토글 전환
 */
const int MOTION_MODE = 1;

// 부드러운 움직임 속도 조절 (각도 1도 변화 주기, 단위: ms)
// 값이 작을수록 빠르고, 클수록 천천히 부드럽게 움직입니다.
const int STEP_DELAY_MS = 15; 

// ============================================================================
// 전역 변수 및 서보 객체 선언
// ============================================================================
Servo servos[10];

// 현재 서보 각도를 기억하는 배열
int currentAngles[10];

// 10개 버튼 디바운스 처리용 변수 배열
int lastButtonReadings[10];
int stableButtonStates[10];
unsigned long lastDebounceTimes[10];
const unsigned long DEBOUNCE_DELAY = 30; // 30ms 디바운스 필터

// 마지막 서보 각도 스텝 업데이트 시각 (논블로킹 타이머)
unsigned long lastStepTime = 0;

// 모드 2(토글) 상태 플래그 배열
bool isToggledGrips[10];

// ============================================================================
// 초기화 함수 (setup)
// ============================================================================
void setup() {
  Serial.begin(9600);
  Serial.println(F("=== 10-Servo 10-Button Controller Initializing ==="));

  // 10개 버튼 핀을 내부 풀업 모드로 설정 (외장 저항 불필요)
  for (int i = 0; i < 10; i++) {
    pinMode(BUTTON_PINS[i], INPUT_PULLUP);
    lastButtonReadings[i] = HIGH;
    stableButtonStates[i] = HIGH;
    lastDebounceTimes[i] = 0;
    isToggledGrips[i] = false;
  }

  // 서보 전원 핀 초기화 (전원 활성화: LOW)
  pinMode(POWER_SERVO_PIN, OUTPUT);
  digitalWrite(POWER_SERVO_PIN, LOW);

  // 10개 서보 모터 attach 및 초기 위치(펴진 상태) 설정
  Serial.println(F("Moving to initial OPEN positions..."));
  for (int i = 0; i < 10; i++) {
    servos[i].attach(SERVO_PINS[i]);
    currentAngles[i] = OPEN_ANGLES[i];
    servos[i].write(currentAngles[i]);
    delay(50); // 서보 초기화 시 돌입 전류 분산
  }

  Serial.println(F("Ready! Press each button to grip individual finger."));
}

// ============================================================================
// 메인 루프 (loop) - 10개 버튼 및 10개 서보 실시간 독립 제어
// ============================================================================
void loop() {
  unsigned long currentMillis = millis();

  // 1. 10개 버튼 입력 읽기 및 디바운스 처리
  for (int i = 0; i < 10; i++) {
    int reading = digitalRead(BUTTON_PINS[i]);

    if (reading != lastButtonReadings[i]) {
      lastDebounceTimes[i] = currentMillis;
    }

    if ((currentMillis - lastDebounceTimes[i]) > DEBOUNCE_DELAY) {
      if (reading != stableButtonStates[i]) {
        stableButtonStates[i] = reading;

        // 버튼 상태 변경 이벤트 시리얼 출력
        if (stableButtonStates[i] == LOW) {
          Serial.print(F(">> [Button "));
          Serial.print(FINGER_NAMES[i]);
          Serial.println(F(" PRESSED] -> Gripping..."));
          if (MOTION_MODE == 2) {
            isToggledGrips[i] = !isToggledGrips[i];
          }
        } else {
          Serial.print(F(">> [Button "));
          Serial.print(FINGER_NAMES[i]);
          Serial.println(F(" RELEASED] -> Opening..."));
        }
      }
    }
    lastButtonReadings[i] = reading;
  }

  // 2. 논블로킹 서보 각도 실시간 갱신
  // 10개 손가락 각각의 목표 각도를 판별하여 1도씩 독립적으로 이동
  if (currentMillis - lastStepTime >= (unsigned long)STEP_DELAY_MS) {
    lastStepTime = currentMillis;

    for (int i = 0; i < 10; i++) {
      int targetAngle;
      if (MOTION_MODE == 1) {
        // MODE 1: 누르고 있으면 CLOSE(쥐기), 떼면 OPEN(펴기)
        targetAngle = (stableButtonStates[i] == LOW) ? CLOSE_ANGLES[i] : OPEN_ANGLES[i];
      } else {
        // MODE 2: 토글
        targetAngle = isToggledGrips[i] ? CLOSE_ANGLES[i] : OPEN_ANGLES[i];
      }

      if (currentAngles[i] < targetAngle) {
        currentAngles[i]++;
        servos[i].write(currentAngles[i]);
      } else if (currentAngles[i] > targetAngle) {
        currentAngles[i]--;
        servos[i].write(currentAngles[i]);
      }
    }
  }
}
