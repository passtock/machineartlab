import os
import sys
import math
import numpy as np
import ezdxf
from ezdxf.enums import TextEntityAlignment
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
from matplotlib.patches import Polygon, Rectangle

def generate_drawings():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 75)
    print("Generating CAD Drawings & Blueprints for [8 Side Panels + 1 Brim]")
    print("=" * 75)

    # -------------------------------------------------------------------------
    # Helper: Standard Layers for DXF
    # -------------------------------------------------------------------------
    def setup_layers(doc):
        # 1: Red, 2: Yellow, 3: Green, 4: Cyan, 7: White, 8: Gray
        doc.layers.add(name="CUT", color=4)             # Cyan (CNC Toolpath Outer Contour)
        doc.layers.add(name="DIMENSION", color=2)       # Yellow (Dimensions)
        doc.layers.add(name="TEXT_LABEL", color=7)      # White (Part Names & Callouts)
        doc.layers.add(name="CENTERLINE", color=1)      # Red (Centerlines)
        doc.layers.add(name="STOCK_SHEET", color=8)     # Gray (Stock Sheet 4x8 boundary)

    # -------------------------------------------------------------------------
    # [1] 팔각모_측면8개_챙1개_가공도면.dxf (4x8 원장 1220x2440mm 최적 네스팅 가공도면)
    # -------------------------------------------------------------------------
    doc_nest = ezdxf.new("R2010")
    setup_layers(doc_nest)
    msp_nest = doc_nest.modelspace()

    sheet_w, sheet_h = 1220.0, 2440.0
    # Sheet Boundary
    msp_nest.add_lwpolyline([(0, 0), (sheet_w, 0), (sheet_w, sheet_h), (0, sheet_h)], close=True, dxfattribs={'layer': 'STOCK_SHEET'})
    msp_nest.add_text("4x8 판재 원장 (1220 x 2440 mm) - 측면 8개 + 챙 1개 CNC 통합 가공 네스팅", height=28.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((sheet_w/2, sheet_h + 40), align=TextEntityAlignment.BOTTOM_CENTER)

    # Part 1: Brim at bottom (Centered at X = 610)
    brim_cx = sheet_w / 2.0 # 610.0
    brim_y0 = 60.0
    brim_pts_nest = [
        (brim_cx - 260.0, brim_y0),         # bottom-left (520 width)
        (brim_cx + 260.0, brim_y0),         # bottom-right
        (brim_cx + 325.0, brim_y0 + 500.0), # top-right (650 width)
        (brim_cx - 325.0, brim_y0 + 500.0)  # top-left
    ]
    msp_nest.add_lwpolyline(brim_pts_nest, close=True, dxfattribs={'layer': 'CUT'})
    msp_nest.add_text("모자 챙 (BRIM) - 1 EA [아래 520 x 위 650 x 깊이 500 mm]", height=20.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((brim_cx, brim_y0 + 250.0), align=TextEntityAlignment.MIDDLE_CENTER)
    msp_nest.add_line((brim_cx, brim_y0 - 20), (brim_cx, brim_y0 + 520), dxfattribs={'layer': 'CENTERLINE'})

    # Side Panels: 4 interlocking pairs (8 panels total)
    # Pair width = 770mm, Centered at X = 610 -> x0 = 225mm
    x0 = 225.0
    x_inv = x0 + 370.0
    y_start_sides = 615.0
    gap_y = 42.0

    side_polys_nest = []
    for row in range(4):
        y_b = y_start_sides + row * (400.0 + gap_y)

        # Left panel (Normal upright):
        p_norm = [
            (x0 + 65.0,        y_b),
            (x0 + 65.0 + 270.0, y_b),
            (x0 + 400.0,        y_b + 400.0),
            (x0,                y_b + 400.0)
        ]
        msp_nest.add_lwpolyline(p_norm, close=True, dxfattribs={'layer': 'CUT'})
        p_num_left = row * 2 + 1
        msp_nest.add_text(f"측면 #{p_num_left} (270x400x400)", height=15.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((x0 + 200.0, y_b + 200.0), align=TextEntityAlignment.MIDDLE_CENTER)
        side_polys_nest.append(p_norm)

        # Right panel (Inverted interlocking):
        p_inv = [
            (x_inv,                y_b),
            (x_inv + 400.0,        y_b),
            (x_inv + 400.0 - 65.0, y_b + 400.0),
            (x_inv + 65.0,         y_b + 400.0)
        ]
        msp_nest.add_lwpolyline(p_inv, close=True, dxfattribs={'layer': 'CUT'})
        p_num_right = row * 2 + 2
        msp_nest.add_text(f"측면 #{p_num_right} (270x400x400)", height=15.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((x_inv + 200.0, y_b + 200.0), align=TextEntityAlignment.MIDDLE_CENTER)
        side_polys_nest.append(p_inv)

    fn_nest_dxf = os.path.join(out_dir, "팔각모_측면8개_챙1개_가공도면.dxf")
    doc_nest.saveas(fn_nest_dxf)
    print(f"[OK] Generated DXF: {os.path.basename(fn_nest_dxf)}")

    # -------------------------------------------------------------------------
    # [2] 팔각모_측면8개_챙1개_정렬배치도면.dxf (부품별 직관적 그리드 정렬 및 치수 도면)
    # -------------------------------------------------------------------------
    doc_grid = ezdxf.new("R2010")
    setup_layers(doc_grid)
    msp_grid = doc_grid.modelspace()

    # Layout:
    # Row 1: Side Panels #1, #2, #3, #4 (Y = 1250)
    # Row 2: Side Panels #5, #6, #7, #8 (Y = 650)
    # Row 3: Brim (Y = 0, Centered)
    x_gap = 70.0
    panel_w = 400.0
    row1_y = 1280.0
    row2_y = 680.0
    brim_y = 50.0

    all_grid_side_polys = []
    for i in range(8):
        row_idx = 0 if i < 4 else 1
        col_idx = i % 4
        px = col_idx * (panel_w + x_gap)
        py = row1_y if row_idx == 0 else row2_y

        pts = [
            (px + 65.0,        py),
            (px + 65.0 + 270.0, py),
            (px + 400.0,        py + 400.0),
            (px,                py + 400.0)
        ]
        msp_grid.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'CUT'})
        msp_grid.add_text(f"측면 패널 #{i+1}", height=18.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((px + 200.0, py + 200.0), align=TextEntityAlignment.MIDDLE_CENTER)
        msp_grid.add_text("270 x 400 x 400 mm", height=13.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((px + 200.0, py + 165.0), align=TextEntityAlignment.MIDDLE_CENTER)
        msp_grid.add_line((px + 200.0, py - 20), (px + 200.0, py + 420), dxfattribs={'layer': 'CENTERLINE'})
        all_grid_side_polys.append(pts)

    # Dimensions on Panel #1
    p1_x = 0.0
    p1_y = row1_y
    # Bottom 270
    msp_grid.add_line((p1_x + 65.0, p1_y - 25), (p1_x + 335.0, p1_y - 25), dxfattribs={'layer': 'DIMENSION'})
    msp_grid.add_text("270.0", height=14.0, dxfattribs={'layer': 'DIMENSION'}).set_placement((p1_x + 200.0, p1_y - 45), align=TextEntityAlignment.MIDDLE_CENTER)
    # Top 400
    msp_grid.add_line((p1_x, p1_y + 425), (p1_x + 400.0, p1_y + 425), dxfattribs={'layer': 'DIMENSION'})
    msp_grid.add_text("400.0", height=14.0, dxfattribs={'layer': 'DIMENSION'}).set_placement((p1_x + 200.0, p1_y + 445), align=TextEntityAlignment.MIDDLE_CENTER)
    # Height 400
    msp_grid.add_line((p1_x - 30, p1_y), (p1_x - 30, p1_y + 400), dxfattribs={'layer': 'DIMENSION'})
    msp_grid.add_text("400.0", height=14.0, dxfattribs={'layer': 'DIMENSION'}).set_placement((p1_x - 55, p1_y + 200), align=TextEntityAlignment.MIDDLE_RIGHT)

    # Place Brim centered below 4 columns (Total row width: 4 * 400 + 3 * 70 = 1810)
    grid_total_w = 4 * panel_w + 3 * x_gap # 1810
    brim_center_grid_x = grid_total_w / 2.0 # 905.0
    brim_grid_pts = [
        (brim_center_grid_x - 260.0, brim_y),
        (brim_center_grid_x + 260.0, brim_y),
        (brim_center_grid_x + 325.0, brim_y + 500.0),
        (brim_center_grid_x - 325.0, brim_y + 500.0)
    ]
    msp_grid.add_lwpolyline(brim_grid_pts, close=True, dxfattribs={'layer': 'CUT'})
    msp_grid.add_text("전면 챙 패널 (BRIM) - 1 EA", height=22.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((brim_center_grid_x, brim_y + 270.0), align=TextEntityAlignment.MIDDLE_CENTER)
    msp_grid.add_text("520 x 650 x 500 mm", height=16.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((brim_center_grid_x, brim_y + 230.0), align=TextEntityAlignment.MIDDLE_CENTER)
    msp_grid.add_line((brim_center_grid_x, brim_y - 25), (brim_center_grid_x, brim_y + 525), dxfattribs={'layer': 'CENTERLINE'})

    # Dimensions on Brim
    # Bottom 520
    msp_grid.add_line((brim_center_grid_x - 260, brim_y - 30), (brim_center_grid_x + 260, brim_y - 30), dxfattribs={'layer': 'DIMENSION'})
    msp_grid.add_text("520.0", height=15.0, dxfattribs={'layer': 'DIMENSION'}).set_placement((brim_center_grid_x, brim_y - 50), align=TextEntityAlignment.MIDDLE_CENTER)
    # Top 650
    msp_grid.add_line((brim_center_grid_x - 325, brim_y + 530), (brim_center_grid_x + 325, brim_y + 530), dxfattribs={'layer': 'DIMENSION'})
    msp_grid.add_text("650.0", height=15.0, dxfattribs={'layer': 'DIMENSION'}).set_placement((brim_center_grid_x, brim_y + 550), align=TextEntityAlignment.MIDDLE_CENTER)
    # Height 500
    msp_grid.add_line((brim_center_grid_x - 355, brim_y), (brim_center_grid_x - 355, brim_y + 500), dxfattribs={'layer': 'DIMENSION'})
    msp_grid.add_text("500.0", height=15.0, dxfattribs={'layer': 'DIMENSION'}).set_placement((brim_center_grid_x - 380, brim_y + 250), align=TextEntityAlignment.MIDDLE_RIGHT)

    # Master Title for Grid Drawing
    msp_grid.add_text("MACHINE ART LAB | 팔각모 측면 8개 + 챙 1개 CNC 통합 제작도면 (1:1 mm)", height=32.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((grid_total_w/2.0, row1_y + 520.0), align=TextEntityAlignment.MIDDLE_CENTER)

    fn_grid_dxf = os.path.join(out_dir, "팔각모_측면8개_챙1개_정렬배치도면.dxf")
    doc_grid.saveas(fn_grid_dxf)
    print(f"[OK] Generated DXF: {os.path.basename(fn_grid_dxf)}")

    # -------------------------------------------------------------------------
    # [3] 고해상도 PNG 이미지 도면 생성 (1: 가공 네스팅 도면)
    # -------------------------------------------------------------------------
    fig1 = plt.figure(figsize=(14, 22), facecolor='#0b1329')
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.set_facecolor('#0f172a')

    # Sheet outline
    sheet_rect = Rectangle((0, 0), sheet_w, sheet_h, facecolor='#162036', edgecolor='#475569', linewidth=2.5, linestyle='-')
    ax1.add_patch(sheet_rect)

    # Brim
    brim_p = Polygon(brim_pts_nest, closed=True, facecolor='#1e293b', edgecolor='#38bdf8', linewidth=2.5)
    ax1.add_patch(brim_p)
    ax1.plot([brim_cx, brim_cx], [brim_y0 - 20, brim_y0 + 520], color='#ef4444', linestyle='--', linewidth=1.2)
    ax1.text(brim_cx, brim_y0 + 250, "모자 챙 (BRIM) - 1 EA\n아래 520 × 위 650 × 깊이 500 mm", color='#38bdf8', fontsize=12, fontweight='bold', ha='center', va='center')

    # Side Panels
    for idx, poly in enumerate(side_polys_nest):
        sp = Polygon(poly, closed=True, facecolor='#1e293b', edgecolor='#38bdf8', linewidth=2.2)
        ax1.add_patch(sp)
        # Center of polygon
        cx_p = np.mean([p[0] for p in poly])
        cy_p = np.mean([p[1] for p in poly])
        ax1.text(cx_p, cy_p, f"측면 #{idx+1}\n270×400×400", color='#f8fafc', fontsize=10.5, fontweight='bold', ha='center', va='center')

    # Dimensions / Annotations
    ax1.annotate('', xy=(0, sheet_h + 35), xytext=(sheet_w, sheet_h + 35), arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=1.8))
    ax1.text(sheet_w/2, sheet_h + 55, "원장 폭: 1220 mm (4 ft)", color='#fbbf24', fontsize=13, fontweight='bold', ha='center')

    ax1.annotate('', xy=(-35, 0), xytext=(-35, sheet_h), arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=1.8))
    ax1.text(-60, sheet_h/2, "원장 길이: 2440 mm (8 ft)", color='#fbbf24', fontsize=13, fontweight='bold', ha='center', va='center', rotation=90)

    # Sub-info box at bottom
    info_box = (
        "■ 4×8 판재(1220×2440mm) 1장으로 측면 8개 + 챙 1개 완벽 가공 가능\n"
        "■ 부품 간 이격 거리: 35~42mm (Ø6~8mm 엔드밀 절삭 및 탭 안전 확보)\n"
        "■ 좌우 안전 여백: ~225mm / 상하 여백: 60~85mm (클램핑 안전 영역 충분)\n"
        "■ 8개 측면 맞춤 결합 시 사선 빗각 베벨 각도: 양쪽 각각 20.61° 가공"
    )
    ax1.text(sheet_w/2, -80, info_box, color='#cbd5e1', fontsize=11, ha='center', va='top', bbox=dict(boxstyle='round,pad=0.8', facecolor='#1e293b', edgecolor='#334155'))

    ax1.set_xlim(-150, sheet_w + 150)
    ax1.set_ylim(-260, sheet_h + 120)
    ax1.set_aspect('equal')
    ax1.set_title("MACHINE ART LAB | 팔각모 측면 8개 + 챙 1개 CNC 원장 네스팅 도면 (1220 x 2440 mm)", color='#f8fafc', fontsize=16, fontweight='bold', pad=25)
    ax1.axis('off')

    fn_nest_png = os.path.join(out_dir, "팔각모_측면8개_챙1개_가공도면.png")
    fig1.savefig(fn_nest_png, dpi=200, facecolor=fig1.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close(fig1)
    print(f"[OK] Generated PNG: {os.path.basename(fn_nest_png)}")

    # -------------------------------------------------------------------------
    # [4] 고해상도 PNG 이미지 도면 생성 (2: 정렬 배치 도면)
    # -------------------------------------------------------------------------
    fig2 = plt.figure(figsize=(24, 18), facecolor='#0b1329')
    ax2 = fig2.add_subplot(1, 1, 1)
    ax2.set_facecolor('#0f172a')

    # Draw Brim
    brim_grid_p = Polygon(brim_grid_pts, closed=True, facecolor='#1e293b', edgecolor='#38bdf8', linewidth=2.8)
    ax2.add_patch(brim_grid_p)
    ax2.plot([brim_center_grid_x, brim_center_grid_x], [brim_y - 25, brim_y + 525], color='#ef4444', linestyle='--', linewidth=1.5)
    ax2.text(brim_center_grid_x, brim_y + 250, "전면 챙 패널 (BRIM) - 1 EA\n아래 밑변: 520.0 mm | 위 윗변: 650.0 mm | 깊이: 500.0 mm\n(사선 길이: 504.21 mm | 하단각: 82.59°)", 
             color='#38bdf8', fontsize=13, fontweight='bold', ha='center', va='center')

    # Brim dimensions
    ax2.annotate('', xy=(brim_center_grid_x - 260, brim_y - 25), xytext=(brim_center_grid_x + 260, brim_y - 25), arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=1.8))
    ax2.text(brim_center_grid_x, brim_y - 45, "520.0 mm (52 cm)", color='#fbbf24', fontsize=12, fontweight='bold', ha='center')

    ax2.annotate('', xy=(brim_center_grid_x - 325, brim_y + 525), xytext=(brim_center_grid_x + 325, brim_y + 525), arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=1.8))
    ax2.text(brim_center_grid_x, brim_y + 545, "650.0 mm (65 cm)", color='#fbbf24', fontsize=12, fontweight='bold', ha='center')

    ax2.annotate('', xy=(brim_center_grid_x - 355, brim_y), xytext=(brim_center_grid_x - 355, brim_y + 500), arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=1.8))
    ax2.text(brim_center_grid_x - 380, brim_y + 250, "500.0 mm\n(50 cm)", color='#fbbf24', fontsize=12, fontweight='bold', ha='right', va='center')

    # Draw 8 Side Panels
    for idx, poly in enumerate(all_grid_side_polys):
        sp = Polygon(poly, closed=True, facecolor='#1e293b', edgecolor='#38bdf8', linewidth=2.5)
        ax2.add_patch(sp)
        cx_p = np.mean([p[0] for p in poly])
        cy_p = np.mean([p[1] for p in poly])
        ax2.plot([cx_p, cx_p], [cy_p - 220, cy_p + 220], color='#ef4444', linestyle='--', linewidth=1.2, alpha=0.7)
        ax2.text(cx_p, cy_p, f"[PART 1-{idx+1}]\n측면 사다리꼴 패널\n아래 270 × 위 400 × 높이 400 mm", color='#f8fafc', fontsize=11, fontweight='bold', ha='center', va='center')

    # Dimensions on Side Panel #1
    ax2.annotate('', xy=(65, row1_y - 25), xytext=(335, row1_y - 25), arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=1.8))
    ax2.text(200, row1_y - 45, "270.0 mm (27 cm)", color='#fbbf24', fontsize=12, fontweight='bold', ha='center')

    ax2.annotate('', xy=(0, row1_y + 425), xytext=(400, row1_y + 425), arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=1.8))
    ax2.text(200, row1_y + 445, "400.0 mm (40 cm)", color='#fbbf24', fontsize=12, fontweight='bold', ha='center')

    ax2.annotate('', xy=(-30, row1_y), xytext=(-30, row1_y + 400), arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=1.8))
    ax2.text(-50, row1_y + 200, "400.0 mm\n(40 cm)", color='#fbbf24', fontsize=12, fontweight='bold', ha='right', va='center')

    # Title & Specifications Block
    spec_text = (
        "■ 부품 수량: 팔각모 측면 사다리꼴 8 EA + 전면 챙 1 EA (총 9개 부품)\n"
        "■ 측면 패널 치수: 밑변 270.0 mm × 윗변 400.0 mm × 높이 400.0 mm (사선 405.25 mm, 각도 80.76° / 99.24°)\n"
        "■ 챙 패널 치수: 밑변 520.0 mm × 윗변 650.0 mm × 깊이 500.0 mm (사선 504.21 mm, 각도 82.59° / 97.41°)\n"
        "■ 3D 조립 입체 높이: 367.93 mm | 바닥 외경 Ø705.5 mm | 상단 외경 Ø1045.3 mm\n"
        "■ CNC 베벨 모따기 각도: 인접 측면 결합부 양쪽 각각 20.61° 경사 가공 (이음새 틈 없이 밀착 결합)"
    )
    ax2.text(grid_total_w / 2.0, row1_y + 570.0, spec_text, color='#cbd5e1', fontsize=11.5, ha='center', va='bottom', 
             bbox=dict(boxstyle='round,pad=0.8', facecolor='#1e293b', edgecolor='#334155'), linespacing=1.4)

    ax2.set_xlim(-150, grid_total_w + 150)
    ax2.set_ylim(-130, row1_y + 750)
    ax2.set_aspect('equal')
    ax2.set_title("MACHINE ART LAB | 대형 팔각모 측면 8개 + 챙 1개 CNC 종합 정렬 제작도면", color='#f8fafc', fontsize=19, fontweight='bold', pad=30)
    ax2.axis('off')

    fn_grid_png = os.path.join(out_dir, "팔각모_측면8개_챙1개_정렬배치도면.png")
    fig2.savefig(fn_grid_png, dpi=200, facecolor=fig2.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close(fig2)
    print(f"[OK] Generated PNG: {os.path.basename(fn_grid_png)}")

    print("\nAll requested drawings (DXF & PNG) created successfully!")

if __name__ == '__main__':
    generate_drawings()
