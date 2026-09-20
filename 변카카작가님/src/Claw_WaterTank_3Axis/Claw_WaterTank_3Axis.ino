/*
 * ======================================================================================
 * [머신아트랩 - 변카카 작가님 인터랙티브 인형뽑기 수조]
 * 옵션 2: 3축 (X-Y-Z) 완전한 갠트리 인형뽑기 시스템 (Full 3-Axis Claw Crane)
 * ======================================================================================
 * - 구성:
 *    1. X축 (좌우): 상단 갠트리 슬라이더 + NEMA 17 스텝모터
 *    2. Y축 (앞뒤): 수조 양측 듀얼 레일 + NEMA 17 스텝모터
 *    3. Z축 (상하 승강): 이동 캐리지 위 낚싯줄 윈치 릴 + NEMA 17 스텝모터
 *    4. 입력 인터페이스:
 *       - 2축 조이스틱 (X, Y축): 2차원 수조 평면 자유 이동
 *       - 수심 레버 (Z축): 물체의 잠김 깊이 실시간 조작
 *       - (또는 아케이드 드롭 버튼: 버튼 누르면 자동으로 내려갔다 올라오는 모드 지원)
 *    5. 안전 리밋: X-Min, Y-Min, Z-Max 리밋 스위치 3개
 * 
 * - 라이브러리: AccelStepper (라이브러리 매니저에서 설치)
 * ======================================================================================
 */

#include <Arduino.h>
#include <AccelStepper.h>

// ===================== [1. 핀 맵 (Arduino CNC Shield V3 표준)] =====================
// X축 (좌우)
const int PIN_X_STEP = 2;
const int PIN_X_DIR  = 5;

// Y축 (앞뒤)
const int PIN_Y_STEP = 3;
const int PIN_Y_DIR  = 6;

// Z축 (상하 윈치)
const int PIN_Z_STEP = 4;
const int PIN_Z_DIR  = 7;

// 모터 드라이버 공통 활성화 (LOW = ON)
const int PIN_ENABLE = 8;

// 리밋 스위치 핀 (X, Y, Z 원점)
const int PIN_LIMIT_X = 9;   // 좌측 한계
const int PIN_LIMIT_Y = 10;  // 전면 한계
const int PIN_LIMIT_Z = 11;  // 상단 한계 (실 전부 감김)

// 관람객 조작 입력 (아날로그 핀)
const int PIN_JOY_X = A0;  // 조이스틱 좌/우
const int PIN_JOY_Y = A1;  // 조이스틱 앞/뒤
const int PIN_LEVER_Z = A2; // 수심 조작 레버 (또는 드롭 버튼 A3)

// ===================== [2. 모터 인스턴스 및 가동 한계] =====================
AccelStepper stepperX(AccelStepper::DRIVER, PIN_X_STEP, PIN_X_DIR);
AccelStepper stepperY(AccelStepper::DRIVER, PIN_Y_STEP, PIN_Y_DIR);
AccelStepper stepperZ(AccelStepper::DRIVER, PIN_Z_STEP, PIN_Z_DIR);

// 수조 크기에 따른 최대 가동 스텝 수 (200스텝 * 16분주 = 3200스텝/회전)
const long MAX_X = 8000;  // 가로 (예: 50cm)
const long MAX_Y = 6000;  // 세로 (예: 35cm)
const long MAX_Z = 10000; // 깊이 (예: 40cm)

const int JOY_CENTER = 512;
const int JOY_DEADZONE = 70;

// ----------------------------------------------------
// 최초 부팅 시 3축 자동 원점 복귀 (Homing)
// ----------------------------------------------------
void perform3AxisHoming() {
  Serial.println(F("[HOMING] 3축 인형뽑기 크레인 원점 보정 시작..."));
  digitalWrite(PIN_ENABLE, LOW);

  // 1단계: Z축 (실 감개)을 먼저 최상단으로 감아 물체를 수면 위로 확보
  Serial.println(F("[HOMING] 1/3 Z축 상단 복귀..."));
  stepperZ.setMaxSpeed(1500);
  stepperZ.setAcceleration(800);
  while (digitalRead(PIN_LIMIT_Z) == HIGH) {
    stepperZ.moveTo(stepperZ.currentPosition() - 20);
    stepperZ.run();
  }
  stepperZ.setCurrentPosition(0);
  delay(150);

  // 2단계: X축 좌측 원점 복귀
  Serial.println(F("[HOMING] 2/3 X축 좌측 복귀..."));
  stepperX.setMaxSpeed(1500);
  stepperX.setAcceleration(800);
  while (digitalRead(PIN_LIMIT_X) == HIGH) {
    stepperX.moveTo(stepperX.currentPosition() - 20);
    stepperX.run();
  }
  stepperX.setCurrentPosition(0);
  delay(150);

  // 3단계: Y축 전면 원점 복귀
  Serial.println(F("[HOMING] 3/3 Y축 전면 복귀..."));
  stepperY.setMaxSpeed(1500);
  stepperY.setAcceleration(800);
  while (digitalRead(PIN_LIMIT_Y) == HIGH) {
    stepperY.moveTo(stepperY.currentPosition() - 20);
    stepperY.run();
  }
  stepperY.setCurrentPosition(0);
  delay(150);

  // 정상 전시 운용 속도 및 부드러운 가감속 설정
  stepperX.setMaxSpeed(2500);
  stepperX.setAcceleration(1200);

  stepperY.setMaxSpeed(2500);
  stepperY.setAcceleration(1200);

  stepperZ.setMaxSpeed(2000);
  stepperZ.setAcceleration(700); // 물 속 댐핑 느낌

  Serial.println(F("[HOMING] 3축 원점 설정 완료! 준비 완료."));
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_ENABLE, OUTPUT);
  pinMode(PIN_LIMIT_X, INPUT_PULLUP);
  pinMode(PIN_LIMIT_Y, INPUT_PULLUP);
  pinMode(PIN_LIMIT_Z, INPUT_PULLUP);

  perform3AxisHoming();
}

void loop() {
  // ----------------------------------------------------
  // 1. X축 & Y축 조이스틱 2차원 평면 이동
  // ----------------------------------------------------
  int rawX = analogRead(PIN_JOY_X);
  int rawY = analogRead(PIN_JOY_Y);

  int dx = rawX - JOY_CENTER;
  int dy = rawY - JOY_CENTER;

  // X축 속도 제어
  if (abs(dx) > JOY_DEADZONE) {
    float spdX = map(dx, -512, 512, -2200, 2200);
    if (stepperX.currentPosition() <= 0 && spdX < 0) spdX = 0;
    if (stepperX.currentPosition() >= MAX_X && spdX > 0) spdX = 0;
    stepperX.setSpeed(spdX);
    stepperX.runSpeed();
  } else {
    stepperX.setSpeed(0);
  }

  // Y축 속도 제어
  if (abs(dy) > JOY_DEADZONE) {
    float spdY = map(dy, -512, 512, -2200, 2200);
    if (stepperY.currentPosition() <= 0 && spdY < 0) spdY = 0;
    if (stepperY.currentPosition() >= MAX_Y && spdY > 0) spdY = 0;
    stepperY.setSpeed(spdY);
    stepperY.runSpeed();
  } else {
    stepperY.setSpeed(0);
  }

  // ----------------------------------------------------
  // 2. Z축 수심 레버 제어 (물체 잠김 깊이 추종)
  // ----------------------------------------------------
  int rawZ = analogRead(PIN_LEVER_Z);
  long targetZ = map(rawZ, 50, 970, 0, MAX_Z);
  targetZ = constrain(targetZ, 0, MAX_Z);

  stepperZ.moveTo(targetZ);
  stepperZ.run();
}
