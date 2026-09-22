# -*- coding: utf-8 -*-
"""
button_10_servos.ino 기반 10채널 서보 & 버튼 하드웨어 배선 회로도 생성기
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Enable Korean font on Windows
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def draw_schematic(output_path):
    fig, ax = plt.subplots(figsize=(16, 9.5), dpi=300, facecolor='#0F172A')
    ax.set_facecolor('#0F172A')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Fonts & Colors
    c_bg_mcu = '#1E293B'
    c_border_mcu = '#38BDF8'
    c_btn_box = '#1E293B'
    c_btn_border = '#34D399'
    c_srv_box = '#1E293B'
    c_srv_border = '#F472B6'
    c_pwr_box = '#1E293B'
    c_pwr_border = '#FBBF24'
    c_wire_sig = '#38BDF8'
    c_wire_gnd = '#94A3B8'
    c_wire_vcc = '#EF4444'

    # Title
    ax.text(8.0, 9.55, "10-Servo & 10-Button Controller Wiring Schematic", 
            fontsize=20, fontweight='bold', color='#FFFFFF', ha='center')
    ax.text(8.0, 9.2, "[button_10_servos.ino] 아두이노 메가 2560 핀맵 및 1:1 매칭 하드웨어 회로도", 
            fontsize=13, color='#94A3B8', ha='center')

    # 1. Central MCU: Arduino Mega 2560
    mcu_rect = patches.FancyBboxPatch((5.8, 2.5), 4.4, 6.2, 
                                     boxstyle="round,pad=0.15", 
                                     facecolor=c_bg_mcu, edgecolor=c_border_mcu, linewidth=2.5)
    ax.add_patch(mcu_rect)
    ax.text(8.0, 8.4, "Arduino Mega 2560", fontsize=16, fontweight='bold', color='#38BDF8', ha='center')
    ax.text(8.0, 8.05, "(ATmega2560 Main Controller)", fontsize=10, color='#94A3B8', ha='center')

    # MCU Left Pins (Analog In for Buttons)
    btn_pins_left = [
        ("A0", "Left-1 (엄지)"),
        ("A3", "Left-2 (검지)"),
        ("A4", "Left-3 (중지)"),
        ("A10", "Left-4 (약지)"),
        ("A11", "Left-5 (소지)"),
        ("A5", "Right-1 (엄지)"),
        ("A6", "Right-2 (검지)"),
        ("A7", "Right-3 (중지)"),
        ("A8", "Right-4 (약지)"),
        ("A9", "Right-5 (소지)")
    ]

    mcu_left_y_start = 7.5
    mcu_y_step = 0.46
    for i, (pin, name) in enumerate(btn_pins_left):
        y = mcu_left_y_start - i * mcu_y_step
        # Pin dot
        ax.plot(5.8, y, 'o', color='#34D399', markersize=6)
        ax.text(6.0, y, f"{pin} : {name}", fontsize=9, color='#E2E8F0', va='center', fontweight='bold')

    # MCU Right Pins (Digital PWM for Servos)
    srv_pins_right = [
        ("D2", "PWM SG1 (왼손 엄지)"),
        ("D3", "PWM SG2 (왼손 검지)"),
        ("D4", "PWM SG3 (왼손 중지)"),
        ("D5", "PWM SG4 (왼손 약지)"),
        ("D6", "PWM SG5 (왼손 소지)"),
        ("D7", "PWM SD1 (오른손 엄지)"),
        ("D8", "PWM SD2 (오른손 검지)"),
        ("D9", "PWM SD3 (오른손 중지)"),
        ("D10", "PWM SD4 (오른손 약지)"),
        ("D11", "PWM SD5 (오른손 소지)")
    ]

    for i, (pin, name) in enumerate(srv_pins_right):
        y = mcu_left_y_start - i * mcu_y_step
        # Pin dot
        ax.plot(10.2, y, 'o', color='#F472B6', markersize=6)
        ax.text(10.0, y, f"{pin} : {name}", fontsize=9, color='#E2E8F0', va='center', ha='right', fontweight='bold')

    # MCU Bottom Pins: D12, 5V, GND
    ax.plot(8.0, 2.5, 'o', color='#FBBF24', markersize=7)
    ax.text(8.0, 2.75, "D12 : POWER_SERVO_PIN (Relay Ctrl)", fontsize=9.5, color='#FBBF24', ha='center', fontweight='bold')

    ax.plot(6.4, 2.5, 'o', color='#94A3B8', markersize=6)
    ax.text(6.4, 2.75, "GND", fontsize=9.5, color='#94A3B8', ha='center', fontweight='bold')

    # 2. Left Side: 10 Push Buttons Card
    btn_card = patches.FancyBboxPatch((0.5, 2.5), 4.2, 6.2, 
                                      boxstyle="round,pad=0.15", 
                                      facecolor=c_btn_box, edgecolor=c_btn_border, linewidth=2)
    ax.add_patch(btn_card)
    ax.text(2.6, 8.4, "10-Key Push Buttons", fontsize=15, fontweight='bold', color='#34D399', ha='center')
    ax.text(2.6, 8.05, "내부 풀업 (INPUT_PULLUP) 직결", fontsize=10, color='#94A3B8', ha='center')

    # Button labels & wires
    for i, (pin, name) in enumerate(btn_pins_left):
        y = mcu_left_y_start - i * mcu_y_step
        # Button icon / box
        btn_box = patches.Rectangle((0.8, y - 0.16), 1.8, 0.32, facecolor='#0F172A', edgecolor='#34D399', linewidth=1)
        ax.add_patch(btn_box)
        hand_tag = "[LH]" if i < 5 else "[RH]"
        ax.text(1.7, y, f"{hand_tag} SW {i+1} ({pin})", fontsize=8.5, color='#FFFFFF', ha='center', va='center', fontweight='bold')

        # Wire from Button to MCU Pin
        ax.plot([2.6, 3.4, 5.8], [y, y, y], color='#34D399', linewidth=1.5, alpha=0.85)

        # GND pin to left
        ax.plot([0.8, 0.6], [y, y], color='#94A3B8', linewidth=1.2)

    # Common Button GND Rail on far left
    ax.plot([0.6, 0.6], [mcu_left_y_start, mcu_left_y_start - 9 * mcu_y_step], color='#94A3B8', linewidth=2)
    ax.text(0.6, mcu_left_y_start + 0.2, "Common GND Rail", fontsize=8.5, color='#94A3B8', ha='center')
    # Wire from Button GND rail down to MCU GND
    ax.plot([0.6, 0.6, 6.4], [mcu_left_y_start - 9 * mcu_y_step, 1.8, 1.8], color='#94A3B8', linewidth=1.5, linestyle='--')
    ax.plot([6.4, 6.4], [1.8, 2.5], color='#94A3B8', linewidth=1.5, linestyle='--')

    # 3. Right Side: 10 Servo Motors Card
    srv_card = patches.FancyBboxPatch((11.3, 2.5), 4.2, 6.2, 
                                      boxstyle="round,pad=0.15", 
                                      facecolor=c_srv_box, edgecolor=c_srv_border, linewidth=2)
    ax.add_patch(srv_card)
    ax.text(13.4, 8.4, "10-Servo Motors", fontsize=15, fontweight='bold', color='#F472B6', ha='center')
    ax.text(13.4, 8.05, "SG90 / MG996R 메탈 기어", fontsize=10, color='#94A3B8', ha='center')

    for i, (pin, name) in enumerate(srv_pins_right):
        y = mcu_left_y_start - i * mcu_y_step
        # Servo box
        srv_box = patches.Rectangle((13.4, y - 0.16), 1.9, 0.32, facecolor='#0F172A', edgecolor='#F472B6', linewidth=1)
        ax.add_patch(srv_box)
        hand_tag = "[LH]" if i < 5 else "[RH]"
        ax.text(14.35, y, f"{hand_tag} Servo {i+1} ({pin})", fontsize=8.5, color='#FFFFFF', ha='center', va='center', fontweight='bold')

        # Wire from MCU Pin to Servo Signal
        ax.plot([10.2, 12.6, 13.4], [y, y, y], color='#F472B6', linewidth=1.5, alpha=0.85)

        # Servo Power pins to right
        ax.plot([15.3, 15.45], [y + 0.06, y + 0.06], color='#EF4444', linewidth=1.2) # VCC
        ax.plot([15.3, 15.45], [y - 0.06, y - 0.06], color='#94A3B8', linewidth=1.2) # GND

    # Servo Power Rails on far right
    ax.plot([15.45, 15.45], [mcu_left_y_start + 0.06, mcu_left_y_start - 9 * mcu_y_step + 0.06], color='#EF4444', linewidth=2.5)
    ax.plot([15.55, 15.55], [mcu_left_y_start - 0.06, mcu_left_y_start - 9 * mcu_y_step - 0.06], color='#94A3B8', linewidth=2.5)
    ax.text(15.45, mcu_left_y_start + 0.25, "+5V", fontsize=8.5, color='#EF4444', ha='center', fontweight='bold')
    ax.text(15.55, mcu_left_y_start - 9 * mcu_y_step - 0.25, "GND", fontsize=8.5, color='#94A3B8', ha='center', fontweight='bold')

    # 4. Bottom Section: Relay Module & External 5V Power Supply
    relay_card = patches.FancyBboxPatch((6.2, 0.5), 3.6, 1.4, 
                                       boxstyle="round,pad=0.1", 
                                       facecolor=c_pwr_box, edgecolor=c_pwr_border, linewidth=2)
    ax.add_patch(relay_card)
    ax.text(8.0, 1.55, "Relay / MOSFET Module", fontsize=12, fontweight='bold', color='#FBBF24', ha='center')
    ax.text(8.0, 1.25, "IN: Pin 12 (LOW=ON / HIGH=OFF)", fontsize=9, color='#E2E8F0', ha='center')
    ax.text(8.0, 0.95, "서보 전원 차단/인가 안전 제어", fontsize=8.5, color='#94A3B8', ha='center')

    # Wire from Pin 12 to Relay
    ax.plot([8.0, 8.0], [2.5, 1.9], color='#FBBF24', linewidth=2)

    # External 5V Power Supply Box
    ext_pwr = patches.FancyBboxPatch((11.3, 0.5), 4.2, 1.4, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor='#1E293B', edgecolor='#EF4444', linewidth=2)
    ax.add_patch(ext_pwr)
    ax.text(13.4, 1.55, "External Power Supply (DC 5V 5A~10A)", fontsize=12, fontweight='bold', color='#EF4444', ha='center')
    ax.text(13.4, 1.25, "10개 서보 모터 피크 전류(대용량) 공급", fontsize=9, color='#E2E8F0', ha='center')
    ax.text(13.4, 0.95, "Brown-out 방지 독립 전원 회로", fontsize=8.5, color='#94A3B8', ha='center')

    # Wire from Ext Power to Relay, then to Servos
    # Power +5V into Relay
    ax.plot([11.3, 9.8], [1.1, 1.1], color='#EF4444', linewidth=2)
    # Power switched out from Relay to Servo +5V Rail
    ax.plot([9.8, 10.5, 10.5, 15.45], [0.8, 0.8, 0.2, 0.2], color='#EF4444', linewidth=2.5)
    ax.plot([15.45, 15.45], [0.2, mcu_left_y_start - 9 * mcu_y_step + 0.06], color='#EF4444', linewidth=2.5)

    # Common GND line linking MCU GND, External Power GND, and Servo GND
    ax.plot([6.4, 6.4, 11.3], [1.8, 0.2, 0.2], color='#94A3B8', linewidth=2, linestyle='--')
    ax.plot([13.4, 13.4, 15.55], [0.5, 0.1, 0.1], color='#94A3B8', linewidth=2, linestyle='--')
    ax.plot([15.55, 15.55], [0.1, mcu_left_y_start - 9 * mcu_y_step - 0.06], color='#94A3B8', linewidth=2, linestyle='--')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Schematic saved successfully to {output_path}!")

if __name__ == "__main__":
    out_img = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\hand_controller_pack\circuit_schematic_button_10_servos.png"
    draw_schematic(out_img)
