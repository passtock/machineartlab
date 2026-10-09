import os
import sys
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
from matplotlib.patches import Polygon, Rectangle, Circle, FancyBboxPatch
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def generate_blueprints():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 70)
    print("Generating High-Resolution CNC Engineering Blueprints & 3D Renders")
    print("=" * 70)

    # =========================================================================
    # [1] 2D CNC 종합 제작 도면 (팔각모_CNC가공_종합제작도면.png)
    # =========================================================================
    fig = plt.figure(figsize=(24, 16), facecolor='#0b1329')
    
    # Grid setup: 3 columns, 2 rows
    # Col 1: Part 1 (Side Trapezoid) & Part 2 (Brim)
    # Col 2: Part 3 (Top Octagon) & 3D Assembly Diagram
    # Col 3: Sheet Nesting Layout (4x8 Plywood) & BOM / Specs Title Block
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 1.1, 1.1], height_ratios=[1.0, 1.0],
                          left=0.04, right=0.96, bottom=0.04, top=0.93, wspace=0.18, hspace=0.22)

    # Global Style Palette
    c_bg = '#0f172a'
    c_border = '#334155'
    c_part = '#38bdf8'      # Bright Sky Blue for cut part
    c_part_fill = '#1e293b' # Dark Slate Fill
    c_dim = '#fbbf24'       # Amber Yellow for dimensions
    c_sub = '#94a3b8'       # Cool Slate Gray
    c_white = '#f8fafc'
    c_green = '#4ade80'

    # ----------------------------------------------------
    # Subplot 1: Part 1 - Side Trapezoid (8 EA)
    # ----------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor(c_bg)
    ax1.set_title("[PART 1] 측면 사다리꼴 패널 (Side Trapezoid) - 8 EA", color=c_white, fontsize=13, fontweight='bold', pad=10)
    
    side_pts = np.array([[-135, 0], [135, 0], [200, 400], [-200, 400]])
    poly1 = Polygon(side_pts, closed=True, facecolor='#1e293b', edgecolor='#38bdf8', linewidth=2.5)
    ax1.add_patch(poly1)
    
    # Centerline
    ax1.plot([0, 0], [-25, 425], color='#ef4444', linestyle='--', linewidth=1.2, alpha=0.8)
    
    # Dimensions
    # Bottom width (270)
    ax1.annotate('', xy=(-135, -25), xytext=(135, -25), arrowprops=dict(arrowstyle='<->', color=c_dim, lw=1.5))
    ax1.plot([-135, -135], [0, -35], color=c_dim, lw=0.8, linestyle=':')
    ax1.plot([135, 135], [0, -35], color=c_dim, lw=0.8, linestyle=':')
    ax1.text(0, -42, '아래 밑변: 270.0 mm (27 cm)', color=c_dim, fontsize=10.5, ha='center', va='top', fontweight='bold')
    
    # Top width (400)
    ax1.annotate('', xy=(-200, 425), xytext=(200, 425), arrowprops=dict(arrowstyle='<->', color=c_dim, lw=1.5))
    ax1.plot([-200, -200], [400, 435], color=c_dim, lw=0.8, linestyle=':')
    ax1.plot([200, 200], [400, 435], color=c_dim, lw=0.8, linestyle=':')
    ax1.text(0, 442, '위 윗변: 400.0 mm (40 cm)', color=c_dim, fontsize=10.5, ha='center', va='bottom', fontweight='bold')
    
    # Height (400)
    ax1.annotate('', xy=(225, 0), xytext=(225, 400), arrowprops=dict(arrowstyle='<->', color=c_dim, lw=1.5))
    ax1.plot([135, 235], [0, 0], color=c_dim, lw=0.8, linestyle=':')
    ax1.plot([200, 235], [400, 400], color=c_dim, lw=0.8, linestyle=':')
    ax1.text(240, 200, '높이: 400.0 mm\n(40 cm)', color=c_dim, fontsize=10.5, ha='left', va='center', fontweight='bold')
    
    # Slant edge annotation
    ax1.text(-185, 200, '빗변: 405.25 mm', color=c_green, fontsize=9.5, ha='right', va='center', rotation=80.76)
    ax1.text(120, 20, '80.76°', color='#f472b6', fontsize=9.5)
    ax1.text(175, 375, '99.24°', color='#f472b6', fontsize=9.5)
    
    ax1.text(0, 180, '수량: 8개 (CNC 외곽가공)\n엣지 베벨(모따기): 20.61°\n(8각 조립 시 빈틈없이 밀착)', color=c_white,
             fontsize=10.5, ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#0b1329', edgecolor='#38bdf8', lw=1.2))

    ax1.set_xlim(-260, 310)
    ax1.set_ylim(-70, 480)
    ax1.set_aspect('equal')
    ax1.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax1.spines.values(): spine.set_color(c_border)

    # ----------------------------------------------------
    # Subplot 2: Part 2 - Brim / Visor (1 EA)
    # ----------------------------------------------------
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(c_bg)
    ax2.set_title("[PART 2] 모자 챙 패널 (Brim / Visor) - 1 EA", color=c_white, fontsize=13, fontweight='bold', pad=10)
    
    brim_pts = np.array([[-260, 0], [260, 0], [325, 500], [-325, 500]])
    poly2 = Polygon(brim_pts, closed=True, facecolor='#1e293b', edgecolor='#38bdf8', linewidth=2.5)
    ax2.add_patch(poly2)
    
    ax2.plot([0, 0], [-25, 525], color='#ef4444', linestyle='--', linewidth=1.2, alpha=0.8)
    
    # Bottom width (520)
    ax2.annotate('', xy=(-260, -25), xytext=(260, -25), arrowprops=dict(arrowstyle='<->', color=c_dim, lw=1.5))
    ax2.plot([-260, -260], [0, -35], color=c_dim, lw=0.8, linestyle=':')
    ax2.plot([260, 260], [0, -35], color=c_dim, lw=0.8, linestyle=':')
    ax2.text(0, -42, '아래 밑변(모자 결합부): 520.0 mm (52 cm)', color=c_dim, fontsize=10.5, ha='center', va='top', fontweight='bold')
    
    # Top width (650)
    ax2.annotate('', xy=(-325, 525), xytext=(325, 525), arrowprops=dict(arrowstyle='<->', color=c_dim, lw=1.5))
    ax2.plot([-325, -325], [500, 535], color=c_dim, lw=0.8, linestyle=':')
    ax2.plot([325, 325], [500, 535], color=c_dim, lw=0.8, linestyle=':')
    ax2.text(0, 542, '위 윗변(챙 외곽 끝): 650.0 mm (65 cm)', color=c_dim, fontsize=10.5, ha='center', va='bottom', fontweight='bold')
    
    # Height (500)
    ax2.annotate('', xy=(355, 0), xytext=(355, 500), arrowprops=dict(arrowstyle='<->', color=c_dim, lw=1.5))
    ax2.plot([260, 365], [0, 0], color=c_dim, lw=0.8, linestyle=':')
    ax2.plot([325, 365], [500, 500], color=c_dim, lw=0.8, linestyle=':')
    ax2.text(370, 250, '돌출 높이(깊이):\n500.0 mm (50 cm)', color=c_dim, fontsize=10.5, ha='left', va='center', fontweight='bold')

    ax2.text(-310, 250, '빗변: 504.21 mm', color=c_green, fontsize=9.5, ha='right', va='center', rotation=82.59)
    ax2.text(240, 25, '82.59°', color='#f472b6', fontsize=9.5)
    ax2.text(290, 465, '97.41°', color='#f472b6', fontsize=9.5)

    ax2.text(0, 230, '수량: 1개 (챙 단독 가공)\n사다리꼴 8각모 전면 2면에 안착 결합\n외곽 모서리 R20 라운딩 권장', color=c_white,
             fontsize=10.5, ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#0b1329', edgecolor='#38bdf8', lw=1.2))

    ax2.set_xlim(-400, 470)
    ax2.set_ylim(-70, 580)
    ax2.set_aspect('equal')
    ax2.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax2.spines.values(): spine.set_color(c_border)

    # ----------------------------------------------------
    # Subplot 3: Part 3 - Top Octagon Cover (Optional)
    # ----------------------------------------------------
    ax3 = fig.add_subplot(gs[0, 1])
    ax3.set_facecolor(c_bg)
    ax3.set_title("[PART 3] 상부 정팔각형 덮개판 (Top Octagon Plate) - 1 EA", color=c_white, fontsize=13, fontweight='bold', pad=10)

    n = 8
    R_top = (400.0 / 2.0) / math.sin(math.pi / n)
    r_top = (400.0 / 2.0) / math.tan(math.pi / n)
    oct_pts = []
    for i in range(n):
        ang = math.pi / n + i * (2 * math.pi / n)
        oct_pts.append([R_top * math.cos(ang), R_top * math.sin(ang)])
    oct_pts = np.array(oct_pts)
    
    poly3 = Polygon(oct_pts, closed=True, facecolor='#1e293b', edgecolor='#38bdf8', linewidth=2.5)
    ax3.add_patch(poly3)

    # Incircle dashed
    circle_in = Circle((0, 0), r_top, fill=False, edgecolor='#64748b', linestyle=':', lw=1.2)
    ax3.add_patch(circle_in)
    
    # Outer Dimension Across Flats
    ax3.annotate('', xy=(-r_top, -r_top - 35), xytext=(r_top, -r_top - 35), arrowprops=dict(arrowstyle='<->', color=c_dim, lw=1.5))
    ax3.plot([-r_top, -r_top], [-r_top, -r_top - 45], color=c_dim, lw=0.8, linestyle=':')
    ax3.plot([r_top, r_top], [-r_top, -r_top - 45], color=c_dim, lw=0.8, linestyle=':')
    ax3.text(0, -r_top - 55, f'대변 거리(내경): {2*r_top:.1f} mm', color=c_dim, fontsize=10.5, ha='center', va='top', fontweight='bold')

    ax3.text(0, 50, f'한 변의 길이: 400.0 mm\n(8개 측면 윗변과 100% 일치)\n외접원 직경: Ø{2*R_top:.1f} mm\n상부 덮개 및 프레임용', color=c_white,
             fontsize=10.5, ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#0b1329', edgecolor='#38bdf8', lw=1.2))

    ax3.set_xlim(-600, 600)
    ax3.set_ylim(-600, 600)
    ax3.set_aspect('equal')
    ax3.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax3.spines.values(): spine.set_color(c_border)

    # ----------------------------------------------------
    # Subplot 4: 3D Assembly Geometry Specification
    # ----------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor(c_bg)
    ax4.set_title("[3D ASSEMBLED SPEC] 팔각모 3D 조립 입체 기하 사양", color=c_white, fontsize=13, fontweight='bold', pad=10)

    # Draw side profile of the frustum
    # Bottom apothem: 325.9mm, Top apothem: 482.8mm, Height: 367.9mm
    r_bot = (270.0 / 2.0) / math.tan(math.pi / n)
    H_3d = math.sqrt(400.0**2 - (r_top - r_bot)**2)
    
    # Profile polygon
    prof_pts = np.array([
        [-r_bot, 0],
        [ r_bot, 0],
        [ r_top, H_3d],
        [-r_top, H_3d]
    ])
    poly_prof = Polygon(prof_pts, closed=True, facecolor='#1e293b', edgecolor='#38bdf8', linewidth=2.0)
    ax4.add_patch(poly_prof)

    # Center axis
    ax4.plot([0, 0], [-30, H_3d + 40], color='#ef4444', linestyle='--', lw=1.2)

    # Brim attached to front profile
    # Brim slopes forward from right side (+r_bot)
    brim_tilt = math.radians(-18.0)
    brim_x_end = r_bot + 500.0 * math.cos(brim_tilt)
    brim_z_end = 500.0 * math.sin(brim_tilt)
    ax4.plot([r_bot, brim_x_end], [0, brim_z_end], color='#22c55e', lw=3.0)
    ax4.plot([r_bot, brim_x_end], [-15, brim_z_end - 15], color='#22c55e', lw=1.5, linestyle=':')
    ax4.text((r_bot + brim_x_end)/2.0, (brim_z_end)/2.0 - 25, '모자 챙 (Brim)\n깊이 500mm / 하향 18°', color='#4ade80', fontsize=9.5, ha='center', va='top', fontweight='bold')

    # Height dimension
    ax4.annotate('', xy=(-r_top - 35, 0), xytext=(-r_top - 35, H_3d), arrowprops=dict(arrowstyle='<->', color=c_dim, lw=1.5))
    ax4.plot([-r_bot, -r_top - 45], [0, 0], color=c_dim, lw=0.8, linestyle=':')
    ax4.plot([-r_top, -r_top - 45], [H_3d, H_3d], color=c_dim, lw=0.8, linestyle=':')
    ax4.text(-r_top - 50, H_3d/2.0, f'3D 완성 수직 높이:\n{H_3d:.1f} mm', color=c_dim, fontsize=10.5, ha='right', va='center', fontweight='bold')

    # Diameter annotations
    R_bot = (270.0 / 2.0) / math.sin(math.pi / n)
    ax4.annotate('', xy=(-r_bot, -25), xytext=(r_bot, -25), arrowprops=dict(arrowstyle='<->', color=c_dim, lw=1.2))
    ax4.text(0, -35, f'하단 내경 Ø{2*r_bot:.1f} / 외경 Ø{2*R_bot:.1f} mm', color=c_dim, fontsize=9.5, ha='center', va='top')

    ax4.annotate('', xy=(-r_top, H_3d + 25), xytext=(r_top, H_3d + 25), arrowprops=dict(arrowstyle='<->', color=c_dim, lw=1.2))
    ax4.text(0, H_3d + 35, f'상단 내경 Ø{2*r_top:.1f} / 외경 Ø{2*R_top:.1f} mm', color=c_dim, fontsize=9.5, ha='center', va='bottom')

    # Angle annotations
    ax4.text(r_bot + 25, 45, '경사각 66.90°\n(수직 대비 23.10°)', color='#f472b6', fontsize=9.5)

    ax4.set_xlim(-650, 900)
    ax4.set_ylim(-200, 480)
    ax4.set_aspect('equal')
    ax4.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax4.spines.values(): spine.set_color(c_border)

    # ----------------------------------------------------
    # Subplot 5: Sheet Nesting Layout (4x8 Plywood 1220 x 2440 mm)
    # ----------------------------------------------------
    ax5 = fig.add_subplot(gs[0, 2])
    ax5.set_facecolor(c_bg)
    ax5.set_title("[CNC NESTING] 표준 4×8 합판 (1220×2440mm) 2장 절단 배치도", color=c_white, fontsize=13, fontweight='bold', pad=10)

    # Draw 2 sheets side by side
    sw, sh = 1220, 2440
    # Sheet 1
    rect_s1 = Rectangle((0, 0), sw, sh, fill=True, facecolor='#1e293b', edgecolor='#64748b', lw=1.8, linestyle='--')
    ax5.add_patch(rect_s1)
    ax5.text(sw/2.0, sh - 70, '[원장 1] 8x 측면 패널 지그재그 배치', color=c_dim, fontsize=10.0, ha='center', fontweight='bold')

    # Draw 4 pairs of interlocking trapezoids
    margin_x, margin_y, gap_y, gap_x = 80, 100, 60, 40
    for r in range(4):
        yb = margin_y + r * (400 + gap_y)
        # Normal
        p1 = [[margin_x + 65, yb], [margin_x + 65 + 270, yb], [margin_x + 400, yb + 400], [margin_x, yb + 400]]
        ax5.add_patch(Polygon(p1, closed=True, facecolor='#0284c7', edgecolor=c_white, lw=1.2, alpha=0.9))
        ax5.text(margin_x + 200, yb + 200, f'#{r*2+1}', color=c_white, fontsize=8.5, ha='center', va='center', fontweight='bold')
        # Inverted
        xi = margin_x + 400 + gap_x
        p2 = [[xi, yb], [xi + 400, yb], [xi + 400 - 65, yb + 400], [xi + 65, yb + 400]]
        ax5.add_patch(Polygon(p2, closed=True, facecolor='#0369a1', edgecolor=c_white, lw=1.2, alpha=0.9))
        ax5.text(xi + 200, yb + 200, f'#{r*2+2}', color=c_white, fontsize=8.5, ha='center', va='center', fontweight='bold')

    # Sheet 2
    s2_x = sw + 300
    rect_s2 = Rectangle((s2_x, 0), sw, sh, fill=True, facecolor='#1e293b', edgecolor='#64748b', lw=1.8, linestyle='--')
    ax5.add_patch(rect_s2)
    ax5.text(s2_x + sw/2.0, sh - 70, '[원장 2] 챙 1EA + 상판 1EA 배치', color=c_dim, fontsize=10.0, ha='center', fontweight='bold')

    # Brim on Sheet 2
    brim_x = s2_x + sw/2.0
    brim_y = 120
    bp = [[brim_x - 260, brim_y], [brim_x + 260, brim_y], [brim_x + 325, brim_y + 500], [brim_x - 325, brim_y + 500]]
    ax5.add_patch(Polygon(bp, closed=True, facecolor='#10b981', edgecolor=c_white, lw=1.5))
    ax5.text(brim_x, brim_y + 250, '챙 (Brim)\n520x650x500', color=c_white, fontsize=9.0, ha='center', va='center', fontweight='bold')

    # Top Octagon on Sheet 2
    oct_y = brim_y + 500 + 100 + R_top
    oct_nest = [[s2_x + sw/2.0 + x, oct_y + y] for (x, y) in oct_pts]
    ax5.add_patch(Polygon(oct_nest, closed=True, facecolor='#6366f1', edgecolor=c_white, lw=1.5))
    ax5.text(s2_x + sw/2.0, oct_y, f'상판 (Top Cover)\ns=400mm', color=c_white, fontsize=9.0, ha='center', va='center', fontweight='bold')

    ax5.set_xlim(-100, s2_x + sw + 100)
    ax5.set_ylim(-100, sh + 150)
    ax5.set_aspect('equal')
    ax5.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax5.spines.values(): spine.set_color(c_border)

    # ----------------------------------------------------
    # Subplot 6: Title Block & Technical Specifications
    # ----------------------------------------------------
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_facecolor(c_bg)
    ax6.set_title("[SPEC & BOM] 발주 정보 및 가공 주기사항 (Notes)", color=c_white, fontsize=13, fontweight='bold', pad=10)

    # Information Box
    info_text = (
        "■ 프로젝트: 머신아트랩 대형 팔각모 및 챙 조형물\n"
        "■ 가공 방식: CNC 2.5D 라우터 판재 가공 (V-Carve / Flat Cut)\n"
        "■ 추천 소재: 자작나무 합판(Birch Plywood) 15~18T 또는 포맥스/아크릴\n"
        "■ 가공 엔드밀: Ø6.0mm ~ Ø8.0mm 초경 정삭 엔드밀\n"
        "───────────────────────────────────────\n"
        "■ [부품 목록표 / BOM]\n"
        "  1. 팔각모 측면 사다리꼴 패널: 8 EA (아래 270 x 위 400 x 높이 400)\n"
        "  2. 전면 모자 챙 패널: 1 EA (아래 520 x 위 650 x 깊이 500)\n"
        "  3. 상부 팔각 덮개판 (옵션): 1 EA (한 변 400, 외경 Ø1045.2mm)\n"
        "───────────────────────────────────────\n"
        "■ [3D 조립 및 모따기(Miter) 각도 안내]\n"
        "  • 8개 패널 결합 시 사이 각도(Dihedral): 138.78°\n"
        "  • 패널 빗변 모따기 각도(Bevel Cut): 20.61°\n"
        "    (양쪽 20.61°씩 깎아 맞대면 빈틈없이 138.78° 완벽 밀착)\n"
        "  • 3D 완성 수직 높이: 367.93 mm | 챙 하향 경사각: 18.0°\n"
        "───────────────────────────────────────\n"
        "■ 납품 파일: 1:1 DXF (5종) / 3D STEP (3종) / 3D STL & OBJ"
    )
    ax6.text(0.04, 0.94, info_text, color=c_white, fontsize=10.2, va='top', fontfamily='Malgun Gothic', linespacing=1.45)
    
    ax6.set_xlim(0, 1)
    ax6.set_ylim(0, 1)
    ax6.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax6.spines.values(): spine.set_color(c_border)

    # Master Title Header
    fig.suptitle("MACHINE ART LAB | 팔각모(8-Sided Cap) 및 전면 챙(Brim) CNC 종합 가공 제작도면",
                 color=c_white, fontsize=19, fontweight='bold', y=0.98)

    blueprint_path = os.path.join(out_dir, "팔각모_CNC가공_종합제작도면.png")
    fig.savefig(blueprint_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"[OK] Generated Blueprint Image: {os.path.basename(blueprint_path)}")

    # =========================================================================
    # [2] 3D 다각도 조립 렌더링 뷰 (팔각모_3D_조립_렌더링.png)
    # =========================================================================
    fig3d = plt.figure(figsize=(20, 15), facecolor='#0b1329')
    
    # 4 Views: Isometric, Front, Top, Side
    views = [
        ("3D 입체 원근 뷰 (Isometric 3D View)", 25, 45),
        ("정면도 (Front View - XZ)", 0, 0),
        ("평면도 (Top View - XY)", 90, -90),
        ("우측면도 (Right Side View - YZ)", 0, 90)
    ]
    
    # Load assembled STL
    stl_path = os.path.join(out_dir, "09_팔각모_3D_어셈블리_완성형.stl")
    tm = trimesh.load(stl_path, force='mesh')

    for idx, (title, elev, azim) in enumerate(views):
        ax = fig3d.add_subplot(2, 2, idx + 1, projection='3d')
        ax.set_facecolor('#0f172a')
        ax.view_init(elev=elev, azim=azim)
        
        # Plot mesh collection
        # Subsample faces slightly if very dense for fast plotting
        step_f = 2 if len(tm.faces) > 5000 else 1
        mesh_faces = tm.vertices[tm.faces[::step_f]]
        
        # Color facets based on normal to give shaded 3D feel
        normals = tm.face_normals[::step_f]
        # Light from top-front
        light_dir = np.array([0.5, 0.5, 0.7])
        light_dir = light_dir / np.linalg.norm(light_dir)
        intensity = np.clip(np.dot(normals, light_dir), 0.15, 1.0)
        
        # Base color: Steel Cyan
        colors = np.zeros((len(intensity), 4))
        for fi, iv in enumerate(intensity):
            colors[fi] = [0.1 + 0.15*iv, 0.4 + 0.5*iv, 0.7 + 0.29*iv, 0.95]
            
        poly_col = Poly3DCollection(mesh_faces, facecolors=colors, edgecolors='#1e293b', linewidths=0.2)
        ax.add_collection3d(poly_col)
        
        # Bounds
        b = tm.bounds
        max_extent = np.max(b[1] - b[0]) / 2.0
        center = (b[0] + b[1]) / 2.0
        ax.set_xlim(center[0] - max_extent, center[0] + max_extent)
        ax.set_ylim(center[1] - max_extent, center[1] + max_extent)
        ax.set_zlim(center[2] - max_extent, center[2] + max_extent)
        
        ax.set_title(title, color=c_white, fontsize=12.5, fontweight='bold', pad=12)
        ax.set_axis_off()

    fig3d.suptitle("MACHINE ART LAB | 팔각모 & 전면 챙 3D 어셈블리 4개 시점 렌더링 뷰",
                   color=c_white, fontsize=18, fontweight='bold', y=0.98)
    
    render_3d_path = os.path.join(out_dir, "팔각모_3D_조립_렌더링.png")
    fig3d.savefig(render_3d_path, dpi=180, facecolor=fig3d.get_facecolor(), edgecolor='none')
    plt.close(fig3d)
    print(f"[OK] Generated 3D Multi-View Render: {os.path.basename(render_3d_path)}")

    print("\nAll technical drawings and renders generated successfully!")

if __name__ == "__main__":
    generate_blueprints()
