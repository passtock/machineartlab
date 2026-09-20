/*
 * ======================================================================================
 * [머신아트랩 - 변카카 작가님 인터랙티브 수조 키네틱 설치물]
 * 타입 A: 고토크 서보모터 + 풀리 와인더 방식 (Servo Pulley System)
 * ======================================================================================
 * - 특징: 
 *    1. 가장 조립이 간단하고 직관적인 구성 (부품 수 최소화)
 *    2. 관람객이 레버를 당기거나 밀면, 서보모터가 실을 감고 풀어 물체가 수조 안에서 상하 이동
 *    3. 물 속의 점성과 부력을 표현하는 '소프트웨어 물리 댐핑(EMA Smoothing)' 내장
 *       -> 사람이 거칠게 레버를 당겨도 물체는 물 속에서 우아하고 부드럽게 유영하듯 이동
 * 
 * - 하드웨어 배선:
 *    - 레버 입력: 아날로그 가변저항 / 레버 포텐셔미터 (A0)
 *    - 서보모터 제어: 메탈기어 서보 (예: MG996R / DS3218) 신호선 (D9)
 *    - 조명 연출(선택): 아날로그/PWM LED 스트립 (D6) - 수심에 따른 밝기 변화
 *    - 전원: 5V~6V 3A 독립 전원 (서보 전원용)
 * ======================================================================================
 */

#include <Arduino.h>
#include <Servo.h>

// ===================== [핀 정의] =====================
const int PIN_LEVER_INPUT = A0;   // 관람객 조작 레버 (0~5V 아날로그 분압)
const int PIN_SERVO_SIG   = 9;    // 고토크 서보모터 PWM 신호선
const int PIN_WATER_LED   = 6;    // 수조 조명 PWM 핀 (수심 연동 라이팅)

// ===================== [기계 및 모션 파라미터] =====================
// 서보 이동 각도 한계 (실이 감기는 풀리의 회전 한계)
const int SERVO_MIN_ANGLE = 15;   // 최저 수심 (물체가 바닥에 닿기 직전)
const int SERVO_MAX_ANGLE = 165;  // 최고 수심 (물체가 수면 위로 올라올 때)

// 레버 입력 가동 범위 (조작 레버의 최소/최대 아날로그 값)
const int LEVER_MIN_VAL = 50;
const int LEVER_MAX_VAL = 970;

// 물리 댐핑 계수 (물 속 저항 느낌 연출: 0.01 ~ 0.2)
// 값이 작을수록 물의 저항이 커져 묵직하고 부드럽게 천천히 따라옵니다.
const float WATER_VISCOSITY_FACTOR = 0.05f; 

Servo winchServo;

float filteredLeverPos = 0.0f; // 부드럽게 필터링된 현재 위치
float targetLeverPos   = 0.0f; // 관람객이 당긴 목표 위치

void setup() {
  Serial.begin(115200);
  Serial.println(F("[START] 변카카 작가님 수조 키네틱 서보 시스템 초기화"));

  pinMode(PIN_WATER_LED, OUTPUT);

  // 서보모터 연결 (초기 펄스 폭 500~2500us 메탈서보 표준)
  winchServo.attach(PIN_SERVO_SIG, 500, 2500);

  // 초기 위치를 현재 레버 위치로 설정
  int rawLever = analogRead(PIN_LEVER_INPUT);
  filteredLeverPos = map(rawLever, LEVER_MIN_VAL, LEVER_MAX_VAL, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
  filteredLeverPos = constrain(filteredLeverPos, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
  winchServo.write((int)filteredLeverPos);

  delay(500);
  Serial.println(F("[READY] 관람객 인터랙션 대기 중..."));
}

void loop() {
  // 1. 레버 입력 측정 (오버샘플링 노이즈 제거)
  long sum = 0;
  for (int i = 0; i < 5; i++) {
    sum += analogRead(PIN_LEVER_INPUT);
    delayMicroseconds(100);
  }
  int rawLever = sum / 5;

  // 2. 입력값을 서보 목표 각도로 매핑
  targetLeverPos = map(rawLever, LEVER_MIN_VAL, LEVER_MAX_VAL, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
  targetLeverPos = constrain(targetLeverPos, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);

  // 3. 물 속의 점성(Viscosity) 물리 시뮬레이션 (지수 이동 평균 댐핑)
  // 사람이 급격하게 레버를 당겨도 물체는 물의 저항을 받아 매끄럽게 가감속 추종
  filteredLeverPos += (targetLeverPos - filteredLeverPos) * WATER_VISCOSITY_FACTOR;

  // 4. 서보모터로 실 감기/풀기 명령
  int finalAngle = (int)(filteredLeverPos + 0.5f);
  winchServo.write(finalAngle);

  // 5. 수심에 따른 수조 조명 밝기 연출 (물체가 깊이 들어갈수록 은은해지는 심해 효과)
  int ledBrightness = map(finalAngle, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE, 60, 255);
  analogWrite(PIN_WATER_LED, ledBrightness);

  // 6. 시리얼 플로터/모니터 디버깅 출력
  static unsigned long lastLog = 0;
  if (millis() - lastLog > 50) {
    lastLog = millis();
    Serial.print(F("RawLever:"));
    Serial.print(rawLever);
    Serial.print(F(",Target:"));
    Serial.print(targetLeverPos);
    Serial.print(F(",FilteredAngle:"));
    Serial.println(finalAngle);
  }

  delay(15); // 약 60Hz 제어 루프
}
