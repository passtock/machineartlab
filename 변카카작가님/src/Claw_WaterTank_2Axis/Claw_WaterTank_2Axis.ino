/*
 * ======================================================================================
 * [머신아트랩 - 변카카 작가님 인터랙티브 인형뽑기 수조]
 * 옵션 1: 2축 (X-Z) 전면 크레인 갠트리 시스템 (2-Axis Claw Crane)
 * ======================================================================================
 * - 구성:
 *    1. X축 (좌우 이동): 수조 상단 단일 알루미늄 레일 + 타이밍 벨트 + NEMA 17 스텝모터
 *    2. Z축 (상하 승강): 이동 캐리지에 탑재된 낚싯줄 윈치 릴 + NEMA 17 스텝모터 (또는 서보)
 *    3. 입력 인터페이스:
 *       - 좌우 조작: 아케이드 조이스틱 좌/우 (또는 좌우 아날로그 레버)
 *       - 상하 조작: 상하 아날로그 레버 (또는 누름식 하강/상승 버튼)
 *    4. 안전 리밋: X축 좌측 원점 스위치, Z축 상단 원점 스위치
 * 
 * - 라이브러리: AccelStepper (라이브러리 매니저에서 설치)
 * ======================================================================================
 */

#include <Arduino.h>
#include <AccelStepper.h>

// ===================== [1. 핀 맵 정의 (CNC 쉴드 또는 개별 드라이버)] =====================
// X축 (좌우 슬라이더)
const int PIN_X_STEP = 2;
const int PIN_X_DIR  = 5;

// Z축 (상하 윈치 릴)
const int PIN_Z_STEP = 4;
const int PIN_Z_DIR  = 7;

// 공통 모터 드라이버 활성화 (LOW = 모터 켜짐, HIGH = 절전/손으로 밀림)
const int PIN_MOTORS_ENABLE = 8;

// 원점 복귀용 리밋 스위치 (INPUT_PULLUP: 평상시 HIGH, 눌리면 LOW)
const int PIN_LIMIT_X_MIN = 9;   // 좌측 한계점
const int PIN_LIMIT_Z_MAX = 10;  // 상단 최상층 한계점 (실이 다 감긴 상태)

// 조작 입력부
const int PIN_INPUT_X_JOYSTICK = A0;  // 좌우 조이스틱 (가운데 약 512)
const int PIN_INPUT_Z_LEVER    = A1;  // 상하 수심 조작 레버 (0~1023)

// ===================== [2. 모터 인스턴스 및 가동 한계] =====================
AccelStepper stepperX(AccelStepper::DRIVER, PIN_X_STEP, PIN_X_DIR);
AccelStepper stepperZ(AccelStepper::DRIVER, PIN_Z_STEP, PIN_Z_DIR);

// 기구 이동 한계 스텝 수 (실제 기구 규격에 맞게 캘리브레이션)
const long MAX_TRAVEL_X = 6000;  // 수조 가로폭 (예: 50cm)
const long MAX_TRAVEL_Z = 8000;  // 수조 깊이 수심 (예: 30cm)

// 조이스틱 데드존 (중립 위치 떨림 방지)
const int JOY_CENTER = 512;
const int JOY_DEADZONE = 60;

// ----------------------------------------------------
// 최초 부팅 시 자동 원점 복귀 (Homing Sequence)
// ----------------------------------------------------
void performHoming() {
  Serial.println(F("[HOMING] 2축 인형뽑기 원점 보정 시작..."));
  digitalWrite(PIN_MOTORS_ENABLE, LOW);

  // 1. Z축 먼저 최상단으로 감아올려 물체가 바닥이나 벽에 걸리지 않게 보호
  Serial.println(F("[HOMING] Z축 (수직 릴) 상단 복귀 중..."));
  stepperZ.setMaxSpeed(1500);
  stepperZ.setAcceleration(800);
  while (digitalRead(PIN_LIMIT_Z_MAX) == HIGH) {
    stepperZ.moveTo(stepperZ.currentPosition() - 20);
    stepperZ.run();
  }
  stepperZ.setCurrentPosition(0); // 수면 위 최상단 = 0
  delay(200);

  // 2. X축 좌측 원점으로 이동
  Serial.println(F("[HOMING] X축 (좌우 레일) 좌측 복귀 중..."));
  stepperX.setMaxSpeed(1500);
  stepperX.setAcceleration(800);
  while (digitalRead(PIN_LIMIT_X_MIN) == HIGH) {
    stepperX.moveTo(stepperX.currentPosition() - 20);
    stepperX.run();
  }
  stepperX.setCurrentPosition(0); // 맨 좌측 = 0
  delay(200);

  // 3. 정상 속도/가속도로 재설정 (부드러운 전시장 모션)
  stepperX.setMaxSpeed(2500);
  stepperX.setAcceleration(1200);

  stepperZ.setMaxSpeed(2000);
  stepperZ.setAcceleration(800); // 물 속 점성 느낌의 부드러운 가감속

  Serial.println(F("[HOMING] 원점 보정 완료! 관람객 조작 대기."));
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_MOTORS_ENABLE, OUTPUT);
  pinMode(PIN_LIMIT_X_MIN, INPUT_PULLUP);
  pinMode(PIN_LIMIT_Z_MAX, INPUT_PULLUP);

  performHoming();
}

void loop() {
  // ----------------------------------------------------
  // 1. X축 조이스틱 좌우 이동 제어 (속도 비례 제어)
  // ----------------------------------------------------
  int joyX = analogRead(PIN_INPUT_X_JOYSTICK);
  int deltaX = joyX - JOY_CENTER;

  if (abs(deltaX) > JOY_DEADZONE) {
    // 조이스틱을 미는 정도에 따라 속도 조절
    float speedX = map(deltaX, -512, 512, -2200, 2200);

    // 소프트웨어 소프트 리밋 (경계 넘김 방지)
    if (stepperX.currentPosition() <= 0 && speedX < 0) speedX = 0;
    if (stepperX.currentPosition() >= MAX_TRAVEL_X && speedX > 0) speedX = 0;

    stepperX.setSpeed(speedX);
    stepperX.runSpeed();
  } else {
    stepperX.setSpeed(0);
  }

  // ----------------------------------------------------
  // 2. Z축 레버 수심 상하 제어 (위치 절대 추종 + 가감속)
  // ----------------------------------------------------
  int rawLeverZ = analogRead(PIN_INPUT_Z_LEVER);
  // 레버를 당길수록 물체가 깊이 내려감 (0 ~ MAX_TRAVEL_Z)
  long targetZ = map(rawLeverZ, 50, 970, 0, MAX_TRAVEL_Z);
  targetZ = constrain(targetZ, 0, MAX_TRAVEL_Z);

  stepperZ.moveTo(targetZ);
  stepperZ.run();
}
