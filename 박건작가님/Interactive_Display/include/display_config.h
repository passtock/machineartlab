#pragma once
#include <Arduino.h>

#define LGFX_USE_V1
#include <LovyanGFX.hpp>

/*
 * ======================================================================================
 * [디스플레이 패널 설정]
 * 사용하시는 디스플레이 기종에 맞춰 아래의 define 중 하나를 활성화(주석 해제)하세요.
 * ======================================================================================
 */
#define DISPLAY_SUNTON_43_OR_70_INCH    // ESP32-8048S043 (4.3인치) 또는 ESP32-8048S070 (7.0인치) 800x480
// #define DISPLAY_WAVESHARE_ESP32S3_50 // Waveshare ESP32-S3 5.0인치 (800x480)
// #define DISPLAY_LILYGO_TRGB_21       // LILYGO T-RGB 2.1인치 (480x480)
// #define DISPLAY_HAPPY_HOUSE_40       // Happy House 4.0인치 (480x480)

class LGFX_Configured : public lgfx::LGFX_Device {
#if defined(DISPLAY_SUNTON_43_OR_70_INCH)
  lgfx::Panel_RGB _panel_instance;
  lgfx::Bus_RGB   _bus_instance;

public:
  LGFX_Configured() {
    {
      auto cfg = _bus_instance.config();
      cfg.panel = &_panel_instance;
      cfg.pin_d0  = GPIO_NUM_15;
      cfg.pin_d1  = GPIO_NUM_7;
      cfg.pin_d2  = GPIO_NUM_6;
      cfg.pin_d3  = GPIO_NUM_5;
      cfg.pin_d4  = GPIO_NUM_4;
      cfg.pin_d5  = GPIO_NUM_9;
      cfg.pin_d6  = GPIO_NUM_46;
      cfg.pin_d7  = GPIO_NUM_3;
      cfg.pin_d8  = GPIO_NUM_8;
      cfg.pin_d9  = GPIO_NUM_16;
      cfg.pin_d10 = GPIO_NUM_1;
      cfg.pin_d11 = GPIO_NUM_14;
      cfg.pin_d12 = GPIO_NUM_21;
      cfg.pin_d13 = GPIO_NUM_47;
      cfg.pin_d14 = GPIO_NUM_48;
      cfg.pin_d15 = GPIO_NUM_45;

      cfg.pin_henable = GPIO_NUM_41;
      cfg.pin_vsync   = GPIO_NUM_40;
      cfg.pin_hsync   = GPIO_NUM_39;
      cfg.pin_pclk    = GPIO_NUM_42;
      cfg.freq_write  = 16000000;

      cfg.hsync_polarity    = 0;
      cfg.hsync_front_porch = 8;
      cfg.hsync_pulse_width = 4;
      cfg.hsync_back_porch  = 8;
      cfg.vsync_polarity    = 0;
      cfg.vsync_front_porch = 8;
      cfg.vsync_pulse_width = 4;
      cfg.vsync_back_porch  = 8;
      cfg.pclk_active_neg   = 1;
      _bus_instance.config(cfg);
    }
    {
      auto cfg = _panel_instance.config();
      cfg.memory_width  = 800;
      cfg.memory_height = 480;
      cfg.panel_width   = 800;
      cfg.panel_height  = 480;
      cfg.offset_x      = 0;
      cfg.offset_y      = 0;
      _panel_instance.config(cfg);
    }
    _panel_instance.setBus(&_bus_instance);
    setPanel(&_panel_instance);
  }
#else
public:
  LGFX_Configured() {
    // 범용 디스플레이 드라이버 매핑
  }
#endif
};
