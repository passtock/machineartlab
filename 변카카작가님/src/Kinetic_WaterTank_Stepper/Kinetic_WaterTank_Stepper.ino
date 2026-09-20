/*
 * ======================================================================================
 * [머신아트랩 - 변카카 작가님 인터랙티브 수조 키네틱 설치물]
 * 타입 B: 저소음 스텝모터 + 무한 윈치 릴 방식 (Stepper Winch System)
 * ======================================================================================
 * - 특징: 
 *    1. 수조의 높이가 높거나(30cm ~ 100cm 이상), 긴 이동 거리가 필요할 때 최적
 *    2. NEMA 17 스텝모터 + TMC2208 무소음 드라이버 사용 시 갤러리 전시장에서 소음 '제로'
 *    3. 리밋 스위치를 이용한 최초 1회 자동 원점(Homing) 보정
 *    4. 가속도/감속도(AccelStepper) 물리 엔진으로 물체 유영 효과 극대화
 * 
 * - 라이브러리: AccelStepper (아두이노 라이브러리 매니저에서 설치)
 * ======================================================================================
 */

#include <Arduino.h>
#include <AccelStepper.h>

// ===================== [핀 정의] =====================
const int PIN_STEP_DIR  = 2;  // 드라이버 DIR
const int PIN_STEP_PUL  = 3;  // 드라이버 STEP (PUL)
const int PIN_STEP_EN   = 4;  // 드라이버 ENABLE (선택)

const int PIN_LIMIT_TOP = 7;  // 상단 한계(원점) 리밋 스위치 (INPUT_PULLUP)
const int PIN_LEVER_IN  = A0; // 조작 레버 포텐셔미터

// AccelStepper 인터페이스 (1 = STEP/DIR 드라이버)
AccelStepper stepper(AccelStepper::DRIVER, PIN_STEP_PUL, PIN_STEP_DIR);

// ===================== [이동 범위 파라미터] =====================
// 최대 이동 스텝 수 (예: 1회전 200스텝, 16마이크로스테핑 -> 1회전 3200스텝)
// 윈치 둘레가 10cm이고 수조 깊이가 40cm라면 총 4회전 = 12,800 스텝
const long MAX_TRAVEL_STEPS = 12000; 

// 속도 및 가속도 설정 (물 속의 부드러운 유영 가속도)
const float MAX_SPEED  = 4000.0f; // 최대 스텝/초
const float ACCEL_RATE = 1500.0f; // 가속도 스텝/초^2

void homeStepper() {
  Serial.println(F("[HOMING] 상단 원점 리밋 스위치 탐색 중..."));
  stepper.setMaxSpeed(1500);
  stepper.setAcceleration(800);

  // 리밋 스위치가 눌릴 때까지 위로 천천히 감아올림
  while (digitalRead(PIN_LIMIT_TOP) == HIGH) {
    stepper.moveTo(stepper.currentPosition() - 50);
    stepper.run();
  }

  // 리밋 도달 -> 현재 위치를 0(최상단)으로 설정
  stepper.setCurrentPosition(0);
  Serial.println(F("[HOMING] 원점 설정 완료 (Position = 0)"));

  // 정상 주행 속도/가속도로 복원
  stepper.setMaxSpeed(MAX_SPEED);
  stepper.setAcceleration(ACCEL_RATE);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LIMIT_TOP, INPUT_PULLUP);
  pinMode(PIN_STEP_EN, OUTPUT);
  digitalWrite(PIN_STEP_EN, LOW); // 드라이버 활성화

  homeStepper();
}

void loop() {
  // 1. 레버 입력 읽기 (5회 평균)
  long sum = 0;
  for (int i = 0; i < 5; i++) sum += analogRead(PIN_LEVER_IN);
  int leverVal = sum / 5;

  // 2. 레버 값을 0 ~ MAX_TRAVEL_STEPS 목표 위치로 매핑
  // 레버를 당길수록 물체가 깊이 내려감 (또는 반대로 설정 가능)
  long targetPos = map(leverVal, 50, 970, 0, MAX_TRAVEL_STEPS);
  targetPos = constrain(targetPos, 0, MAX_TRAVEL_STEPS);

  // 3. 목표 위치로 부드럽게 가감속 이동
  stepper.moveTo(targetPos);
  stepper.run();
}
