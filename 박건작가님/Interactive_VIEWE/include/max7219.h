#pragma once
/*
 * MAX7219 8자리 7세그먼트 — 하드웨어 SPI(공유 버스) 드라이버
 *  - LedControl 라이브러리는 shiftOut 비트뱅잉이라 SPI 버스 공유 시 충돌하므로 사용하지 않음
 *  - MAX7219는 LOAD(CS) 상승 에지에서만 데이터를 래치하므로, CS가 HIGH인 동안
 *    다른 장치(SD/ST7789) 트래픽이 지나가도 표시값은 바뀌지 않는다.
 */
#include <Arduino.h>
#include <SPI.h>

class Max7219 {
public:
  explicit Max7219(int csPin) : _cs(csPin) {}

  void begin(uint8_t intensity = 8) {
    pinMode(_cs, OUTPUT);
    digitalWrite(_cs, HIGH);
    write(0x0F, 0x00);        // Display test OFF
    write(0x0C, 0x01);        // Shutdown OFF (정상 동작)
    write(0x0B, 0x07);        // 8자리 스캔
    write(0x09, 0xFF);        // 8자리 모두 Code-B 디코드 (0~9, '-', 공백)
    setIntensity(intensity);
    clear();
  }

  void setIntensity(uint8_t v) { write(0x0A, v & 0x0F); }

  void clear() {
    for (uint8_t d = 1; d <= 8; d++) write(d, CODE_BLANK);
  }

  // pos: 0 = 맨 왼쪽 자리, 7 = 맨 오른쪽 자리
  void setDigit(uint8_t pos, uint8_t value, bool dp = false) {
    write(8 - pos, (value & 0x0F) | (dp ? 0x80 : 0x00));
  }

  // "12345678", "--------", "  1234  " 형태 문자열 (8글자)
  void print(const char* s) {
    for (uint8_t i = 0; i < 8; i++) {
      char c = s[i];
      uint8_t code = CODE_BLANK;
      if (c >= '0' && c <= '9') code = c - '0';
      else if (c == '-')        code = CODE_DASH;
      else if (c == '\0')       { for (; i < 8; i++) write(8 - i, CODE_BLANK); return; }
      write(8 - i, code);
    }
  }

  // 전원 노이즈·BOOT 버튼 등으로 설정이 깨졌을 때 복구용
  void refreshConfig(uint8_t intensity) {
    write(0x0F, 0x00);
    write(0x0C, 0x01);
    write(0x0B, 0x07);
    write(0x09, 0xFF);
    setIntensity(intensity);
  }

private:
  static constexpr uint8_t CODE_DASH  = 0x0A;
  static constexpr uint8_t CODE_BLANK = 0x0F;

  void write(uint8_t reg, uint8_t data) {
    SPI.beginTransaction(SPISettings(5000000, MSBFIRST, SPI_MODE0));
    digitalWrite(_cs, LOW);
    SPI.transfer(reg);
    SPI.transfer(data);
    digitalWrite(_cs, HIGH);   // 상승 에지에서 래치
    SPI.endTransaction();
  }

  int _cs;
};
