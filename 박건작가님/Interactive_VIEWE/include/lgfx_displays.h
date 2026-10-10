#pragma once
/*
 * LovyanGFX 디스플레이 정의
 *  1) MainLCD : VIEWE 온보드 4.3" 800x480 RGB565 (ST7262)
 *  2) InfoLCD : 외장 2.8" 240x320 ST7789 (공유 SPI 버스)
 */
#include <SD.h>            // LovyanGFX의 drawJpgFile(SD, ...) 지원을 위해 먼저 include
#define LGFX_USE_V1
#include <LovyanGFX.hpp>
#include <lgfx/v1/platforms/esp32s3/Panel_RGB.hpp>
#include <lgfx/v1/platforms/esp32s3/Bus_RGB.hpp>
#include "pins.h"

// ======================================================================================
// 1) 메인 4.3" RGB 패널 — 핀/타이밍은 ESP32_Display_Panel의
//    BOARD_VIEWE_UEDX80480043E_WB_A 공식 설정값 그대로 사용
// ======================================================================================
class MainLCD : public lgfx::LGFX_Device {
  lgfx::Bus_RGB   _bus;
  lgfx::Panel_RGB _panel;
  lgfx::Light_PWM _light;

public:
  MainLCD() {
    {
      auto cfg = _panel.config();
      cfg.memory_width  = 800;
      cfg.memory_height = 480;
      cfg.panel_width   = 800;
      cfg.panel_height  = 480;
      _panel.config(cfg);
    }
    {
      auto cfg = _panel.config_detail();
      cfg.use_psram = 1;   // 프레임버퍼 768KB → PSRAM
      _panel.config_detail(cfg);
    }
    {
      auto cfg = _bus.config();
      cfg.panel = &_panel;
      cfg.pin_d0  = GPIO_NUM_8;   // B0
      cfg.pin_d1  = GPIO_NUM_3;   // B1
      cfg.pin_d2  = GPIO_NUM_46;  // B2
      cfg.pin_d3  = GPIO_NUM_9;   // B3
      cfg.pin_d4  = GPIO_NUM_1;   // B4
      cfg.pin_d5  = GPIO_NUM_5;   // G0
      cfg.pin_d6  = GPIO_NUM_6;   // G1
      cfg.pin_d7  = GPIO_NUM_7;   // G2
      cfg.pin_d8  = GPIO_NUM_15;  // G3
      cfg.pin_d9  = GPIO_NUM_16;  // G4
      cfg.pin_d10 = GPIO_NUM_4;   // G5
      cfg.pin_d11 = GPIO_NUM_45;  // R0
      cfg.pin_d12 = GPIO_NUM_48;  // R1
      cfg.pin_d13 = GPIO_NUM_47;  // R2
      cfg.pin_d14 = GPIO_NUM_21;  // R3
      cfg.pin_d15 = GPIO_NUM_14;  // R4

      cfg.pin_henable = GPIO_NUM_40;  // DE
      cfg.pin_vsync   = GPIO_NUM_41;
      cfg.pin_hsync   = GPIO_NUM_39;
      cfg.pin_pclk    = GPIO_NUM_42;
      cfg.freq_write  = 15000000;

      cfg.hsync_polarity    = 0;
      cfg.hsync_pulse_width = 1;
      cfg.hsync_back_porch  = 42;
      cfg.hsync_front_porch = 20;
      cfg.vsync_polarity    = 0;
      cfg.vsync_pulse_width = 10;
      cfg.vsync_back_porch  = 12;
      cfg.vsync_front_porch = 4;
      cfg.pclk_active_neg   = 1;
      cfg.de_idle_high      = 0;
      cfg.pclk_idle_high    = 0;
      _bus.config(cfg);
    }
    _panel.setBus(&_bus);
    {
      auto cfg = _light.config();
      cfg.pin_bl = PIN_MAIN_BL;
      _light.config(cfg);
    }
    _panel.light(&_light);
    setPanel(&_panel);
  }
};

// ======================================================================================
// 2) 2.8" ST7789 정보 LCD — SD카드·MAX7219와 SPI2 버스 공유
//    LovyanGFX가 Arduino 'SPI' 객체와 같은 버스를 쓰도록 자동 연동됨
// ======================================================================================
class InfoLCD : public lgfx::LGFX_Device {
  lgfx::Panel_ST7789 _panel;
  lgfx::Bus_SPI      _bus;

public:
  InfoLCD() {
    {
      auto cfg = _bus.config();
      cfg.spi_host    = SPI2_HOST;
      cfg.spi_mode    = 0;
      cfg.freq_write  = 27000000;   // 점퍼선 배선 고려해 40MHz 대신 27MHz
      cfg.freq_read   = 16000000;
      cfg.spi_3wire   = false;
      cfg.use_lock    = true;
      cfg.dma_channel = SPI_DMA_CH_AUTO;
      cfg.pin_sclk    = PIN_SPI_SCLK;
      cfg.pin_mosi    = PIN_SPI_MOSI;
      cfg.pin_miso    = PIN_SPI_MISO;   // SD카드가 읽기에 사용 (ST7789 SDO는 연결 안 함)
      cfg.pin_dc      = PIN_INFO_DC;
      _bus.config(cfg);
      _panel.setBus(&_bus);
    }
    {
      auto cfg = _panel.config();
      cfg.pin_cs        = PIN_INFO_CS;
      cfg.pin_rst       = PIN_INFO_RST;
      cfg.pin_busy      = -1;
      cfg.memory_width  = 240;
      cfg.memory_height = 320;
      cfg.panel_width   = 240;
      cfg.panel_height  = 320;
      cfg.offset_x      = 0;
      cfg.offset_y      = 0;
      cfg.readable      = false;
      cfg.invert        = true;    // IPS ST7789는 보통 반전 필요. 색이 반대로 나오면 false
      cfg.rgb_order     = false;   // 빨강/파랑이 바뀌어 보이면 true
      cfg.dlen_16bit    = false;
      cfg.bus_shared    = true;    // SD카드와 버스 공유
      _panel.config(cfg);
    }
    setPanel(&_panel);
  }
};
