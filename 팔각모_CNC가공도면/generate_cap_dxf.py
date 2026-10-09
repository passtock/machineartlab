import os
import sys
import math
import ezdxf
from ezdxf.enums import TextEntityAlignment
import numpy as np

def create_dxf_files():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 70)
    print("Generating Professional 2D CNC CAD Files (DXF) for Octagonal Cap & Brim")
    print("=" * 70)

    # ----------------------------------------------------
    # Geometry Definitions (Units: mm)
    # ----------------------------------------------------
    # 1. Side Trapezoid (8 EA)
    # Bottom: 270mm (27cm), Top: 400mm (40cm), Height: 400mm (40cm)
    side_pts = [
        (-135.0, 0.0),
        ( 135.0, 0.0),
        ( 200.0, 400.0),
        (-200.0, 400.0)
    ]

    # 2. Brim (1 EA)
    # Bottom: 520mm (52cm), Top: 650mm (650mm), Height: 500mm (50cm)
    brim_pts = [
        (-260.0, 0.0),
        ( 260.0, 0.0),
        ( 325.0, 500.0),
        (-325.0, 500.0)
    ]

    # 3. Top Octagonal Cover Plate (1 EA)
    # Regular octagon with edge s = 400mm
    # Apothem r_in = 400 / (2 * tan(pi/8)) = 482.843mm
    # Circumradius R_out = 400 / (2 * sin(pi/8)) = 522.625mm
    n = 8
    r_top = (400.0 / 2.0) / math.tan(math.pi / n)
    R_top = (400.0 / 2.0) / math.sin(math.pi / n)
    top_oct_pts = []
    for i in range(n):
        ang = math.pi / n + i * (2 * math.pi / n) # flat side horizontal
        top_oct_pts.append((R_top * math.cos(ang), R_top * math.sin(ang)))

    # Helper function to setup standard layers
    def setup_layers(doc):
        # CUT (Cyan - Toolpath contour)
        doc.layers.add(name="CUT", color=4) # Cyan
        # CUT_INNER (Green - Inner holes / details)
        doc.layers.add(name="CUT_INNER", color=3) # Green
        # ENGRAVE_MARK (Red - Fold/Bend/Miter lines)
        doc.layers.add(name="MARK_FOLD", color=1) # Red
        # DIMENSION (Yellow)
        doc.layers.add(name="DIMENSION", color=2) # Yellow
        # TEXT_ANNOTATION (White)
        doc.layers.add(name="TEXT_LABEL", color=7) # White
        # STOCK_SHEET (Dark Gray)
        doc.layers.add(name="STOCK_SHEET", color=8) # Gray

    # Helper function to draw dimension with extension lines and arrows
    def draw_linear_dim(msp, p1, p2, offset, text, vertical=False):
        # p1, p2: (x, y)
        x1, y1 = p1
        x2, y2 = p2
        color = 2
        
        if not vertical:
            # Horizontal dimension
            y_dim = y1 + offset
            # Extension lines
            msp.add_line((x1, y1 + (5 if offset>0 else -5)), (x1, y_dim + (10 if offset>0 else -10)), dxfattribs={'layer': 'DIMENSION'})
            msp.add_line((x2, y2 + (5 if offset>0 else -5)), (x2, y_dim + (10 if offset>0 else -10)), dxfattribs={'layer': 'DIMENSION'})
            # Dimension line
            msp.add_line((x1, y_dim), (x2, y_dim), dxfattribs={'layer': 'DIMENSION'})
            # Arrows
            arr = 12.0
            msp.add_line((x1, y_dim), (x1 + arr, y_dim + arr*0.25), dxfattribs={'layer': 'DIMENSION'})
            msp.add_line((x1, y_dim), (x1 + arr, y_dim - arr*0.25), dxfattribs={'layer': 'DIMENSION'})
            msp.add_line((x2, y_dim), (x2 - arr, y_dim + arr*0.25), dxfattribs={'layer': 'DIMENSION'})
            msp.add_line((x2, y_dim), (x2 - arr, y_dim - arr*0.25), dxfattribs={'layer': 'DIMENSION'})
            # Text
            cx = (x1 + x2) / 2.0
            msp.add_text(text, height=20.0, dxfattribs={'layer': 'DIMENSION'}).set_placement((cx, y_dim + 8.0), align=TextEntityAlignment.BOTTOM_CENTER)
        else:
            # Vertical dimension
            x_dim = x1 + offset
            msp.add_line((x1 + (5 if offset>0 else -5), y1), (x_dim + (10 if offset>0 else -10), y1), dxfattribs={'layer': 'DIMENSION'})
            msp.add_line((x2 + (5 if offset>0 else -5), y2), (x_dim + (10 if offset>0 else -10), y2), dxfattribs={'layer': 'DIMENSION'})
            msp.add_line((x_dim, y1), (x_dim, y2), dxfattribs={'layer': 'DIMENSION'})
            arr = 12.0
            msp.add_line((x_dim, y1), (x_dim + arr*0.25, y1 + arr), dxfattribs={'layer': 'DIMENSION'})
            msp.add_line((x_dim, y1), (x_dim - arr*0.25, y1 + arr), dxfattribs={'layer': 'DIMENSION'})
            msp.add_line((x_dim, y2), (x_dim + arr*0.25, y2 - arr), dxfattribs={'layer': 'DIMENSION'})
            msp.add_line((x_dim, y2), (x_dim - arr*0.25, y2 - arr), dxfattribs={'layer': 'DIMENSION'})
            cy = (y1 + y2) / 2.0
            txt = msp.add_text(text, height=20.0, dxfattribs={'layer': 'DIMENSION'})
            txt.set_placement((x_dim + (8.0 if offset>0 else -8.0), cy), align=TextEntityAlignment.MIDDLE_LEFT if offset>0 else TextEntityAlignment.MIDDLE_RIGHT)

    # =========================================================================
    # [1] 단품 1: 팔각모 측면 사다리꼴 (01_팔각모_측면사다리꼴_단품.dxf)
    # =========================================================================
    doc1 = ezdxf.new("R2010")
    setup_layers(doc1)
    msp1 = doc1.modelspace()
    
    # Outer cut polyline
    msp1.add_lwpolyline(side_pts, close=True, dxfattribs={'layer': 'CUT'})
    # Centerline
    msp1.add_line((0, -20), (0, 420), dxfattribs={'layer': 'MARK_FOLD'})
    
    # Dimensions
    draw_linear_dim(msp1, (-135, 0), (135, 0), -45, "270.0 mm (Bottom Width)")
    draw_linear_dim(msp1, (-200, 400), (200, 400), 45, "400.0 mm (Top Width)")
    draw_linear_dim(msp1, (200, 0), (200, 400), 60, "400.0 mm (Height)", vertical=True)
    draw_linear_dim(msp1, (-200, 0), (-200, 400), -60, "400.0 mm (Height)", vertical=True)
    
    # Title & Information block
    msp1.add_text("OCTAGONAL CAP - SIDE TRAPEZOID PANEL", height=28.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -110), align=TextEntityAlignment.MIDDLE_CENTER)
    msp1.add_text("QTY: 8 EA | SCALE 1:1 (mm) | CNC ROUTER / LASER PROFILE", height=18.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -145), align=TextEntityAlignment.MIDDLE_CENTER)
    msp1.add_text("Slant Edge Length: 405.25mm | Base Angle: 80.76 deg | Top Angle: 99.24 deg", height=15.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -175), align=TextEntityAlignment.MIDDLE_CENTER)
    msp1.add_text("Miter Joint Edge Bevel: 20.61 deg (Dihedral 138.78 deg)", height=15.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -200), align=TextEntityAlignment.MIDDLE_CENTER)
    
    fp1 = os.path.join(out_dir, "01_팔각모_측면사다리꼴_단품.dxf")
    doc1.saveas(fp1)
    print(f"[OK] Saved: {os.path.basename(fp1)}")

    # =========================================================================
    # [2] 단품 2: 팔각모 챙 (02_팔각모_챙_단품.dxf)
    # =========================================================================
    doc2 = ezdxf.new("R2010")
    setup_layers(doc2)
    msp2 = doc2.modelspace()
    
    msp2.add_lwpolyline(brim_pts, close=True, dxfattribs={'layer': 'CUT'})
    msp2.add_line((0, -25), (0, 525), dxfattribs={'layer': 'MARK_FOLD'})
    
    draw_linear_dim(msp2, (-260, 0), (260, 0), -50, "520.0 mm (Base Width / Cap Joint)")
    draw_linear_dim(msp2, (-325, 500), (325, 500), 50, "650.0 mm (Outer Tip Width)")
    draw_linear_dim(msp2, (325, 0), (325, 500), 70, "500.0 mm (Brim Depth/Height)", vertical=True)
    draw_linear_dim(msp2, (-325, 0), (-325, 500), -70, "500.0 mm (Brim Depth/Height)", vertical=True)
    
    msp2.add_text("OCTAGONAL CAP - BRIM / VISOR PANEL", height=30.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -125), align=TextEntityAlignment.MIDDLE_CENTER)
    msp2.add_text("QTY: 1 EA | SCALE 1:1 (mm) | CNC ROUTER / LASER PROFILE", height=18.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -165), align=TextEntityAlignment.MIDDLE_CENTER)
    msp2.add_text("Slant Edge Length: 504.21mm | Base Angle: 82.59 deg | Outer Angle: 97.41 deg", height=15.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -200), align=TextEntityAlignment.MIDDLE_CENTER)
    
    fp2 = os.path.join(out_dir, "02_팔각모_챙_단품.dxf")
    doc2.saveas(fp2)
    print(f"[OK] Saved: {os.path.basename(fp2)}")

    # =========================================================================
    # [3] 단품 3: 상부 팔각 덮개 (03_팔각모_상부팔각판_단품.dxf)
    # =========================================================================
    doc3 = ezdxf.new("R2010")
    setup_layers(doc3)
    msp3 = doc3.modelspace()
    
    msp3.add_lwpolyline(top_oct_pts, close=True, dxfattribs={'layer': 'CUT'})
    # Center cross lines
    msp3.add_line((-R_top - 30, 0), (R_top + 30, 0), dxfattribs={'layer': 'MARK_FOLD'})
    msp3.add_line((0, -R_top - 30), (0, R_top + 30), dxfattribs={'layer': 'MARK_FOLD'})
    
    # Outer dimension
    draw_linear_dim(msp3, (-r_top, -r_top), (r_top, -r_top), -60, f"{2*r_top:.1f} mm (Width Across Flats)")
    draw_linear_dim(msp3, (R_top, -r_top), (R_top, r_top), 60, f"{2*r_top:.1f} mm (Height Across Flats)", vertical=True)
    
    msp3.add_text("OCTAGONAL CAP - TOP OCTAGONAL COVER PLATE (OPTIONAL)", height=30.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -R_top - 140), align=TextEntityAlignment.MIDDLE_CENTER)
    msp3.add_text("QTY: 1 EA | SCALE 1:1 (mm) | MATCHES 8x 400mm TOP EDGES", height=18.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -R_top - 180), align=TextEntityAlignment.MIDDLE_CENTER)
    msp3.add_text(f"Edge Length: 400.0mm | Incircle Dia: {2*r_top:.1f}mm | Circumcircle Dia: {2*R_top:.1f}mm", height=15.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -R_top - 215), align=TextEntityAlignment.MIDDLE_CENTER)
    
    fp3 = os.path.join(out_dir, "03_팔각모_상부팔각판_단품.dxf")
    doc3.saveas(fp3)
    print(f"[OK] Saved: {os.path.basename(fp3)}")

    # =========================================================================
    # [4] 네스팅 배치도: 표준 1220x2440mm (4x8) 합판 최적 절단 배치 (04_팔각모_CNC_네스팅_원장배치도.dxf)
    # =========================================================================
    # Side trapezoids (width: 400 at top, 270 at bottom, height: 400)
    # If nested interlocking: (400 + 270) = 670mm wide pair!
    # Height of a pair = 400mm + clearance.
    # 8 side panels = 4 interlocking pairs!
    # 4 pairs stacked vertically = 4 * (400 + 25) = 1700mm <= 2440mm!
    # Width of pair = 670mm <= 1220mm!
    # Brim (650x500mm) fits beside them in the remaining 1220 - 670 = 550mm or top/bottom!
    # 2 Sheets layout ensures generous spacing (>20mm between parts, 25mm sheet margins)
    doc4 = ezdxf.new("R2010")
    setup_layers(doc4)
    msp4 = doc4.modelspace()
    
    sheet_w, sheet_h = 1220.0, 2440.0
    
    # Sheet 1: 8 Side Panels (Interlocking pairs)
    msp4.add_lwpolyline([(0, 0), (sheet_w, 0), (sheet_w, sheet_h), (0, sheet_h)], close=True, dxfattribs={'layer': 'STOCK_SHEET'})
    msp4.add_text("SHEET #1 (1220 x 2440 mm) - 8x SIDE TRAPEZOID PANELS", height=32.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((sheet_w/2, sheet_h + 50), align=TextEntityAlignment.BOTTOM_CENTER)
    
    # Nesting 8 panels into 4 rows of interlocking pairs
    margin_x = 80.0
    margin_y = 120.0
    gap_y = 50.0
    gap_x = 35.0
    
    for row in range(4):
        y_base = margin_y + row * (400.0 + gap_y)
        
        # Left panel: Normal orientation (bottom at y_base, top at y_base + 400)
        # Shifted so left edge is at x_left
        p_norm = [
            (margin_x + 65.0,        y_base),
            (margin_x + 65.0 + 270.0, y_base),
            (margin_x + 400.0,        y_base + 400.0),
            (margin_x,                y_base + 400.0)
        ]
        msp4.add_lwpolyline(p_norm, close=True, dxfattribs={'layer': 'CUT'})
        msp4.add_text(f"SIDE PANEL #{row*2 + 1}", height=16.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((margin_x + 200.0, y_base + 200.0), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Right panel: Inverted orientation (interlocking!)
        # Top at y_base, bottom at y_base + 400
        x_inv = margin_x + 400.0 + gap_x
        p_inv = [
            (x_inv,                y_base),
            (x_inv + 400.0,        y_base),
            (x_inv + 400.0 - 65.0, y_base + 400.0),
            (x_inv + 65.0,         y_base + 400.0)
        ]
        msp4.add_lwpolyline(p_inv, close=True, dxfattribs={'layer': 'CUT'})
        msp4.add_text(f"SIDE PANEL #{row*2 + 2}", height=16.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((x_inv + 200.0, y_base + 200.0), align=TextEntityAlignment.MIDDLE_CENTER)
        
    # Sheet 2: Brim Panel + Top Octagon Plate
    x_offset_sheet2 = sheet_w + 300.0
    msp4.add_lwpolyline([(x_offset_sheet2, 0), (x_offset_sheet2 + sheet_w, 0), (x_offset_sheet2 + sheet_w, sheet_h), (x_offset_sheet2, sheet_h)], close=True, dxfattribs={'layer': 'STOCK_SHEET'})
    msp4.add_text("SHEET #2 (1220 x 2440 mm) - 1x BRIM + 1x TOP OCTAGON PLATE", height=32.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((x_offset_sheet2 + sheet_w/2, sheet_h + 50), align=TextEntityAlignment.BOTTOM_CENTER)
    
    # Place Brim on Sheet 2
    brim_center_x = x_offset_sheet2 + sheet_w / 2.0
    brim_base_y = 120.0
    p_brim_nested = [
        (brim_center_x - 260.0, brim_base_y),
        (brim_center_x + 260.0, brim_base_y),
        (brim_center_x + 325.0, brim_base_y + 500.0),
        (brim_center_x - 325.0, brim_base_y + 500.0)
    ]
    msp4.add_lwpolyline(p_brim_nested, close=True, dxfattribs={'layer': 'CUT'})
    msp4.add_text("BRIM / VISOR (1 EA)", height=22.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((brim_center_x, brim_base_y + 250.0), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Place Top Octagon Plate on Sheet 2
    oct_center_x = x_offset_sheet2 + sheet_w / 2.0
    oct_center_y = brim_base_y + 500.0 + 80.0 + R_top + 20.0
    p_oct_nested = [(oct_center_x + x, oct_center_y + y) for (x, y) in top_oct_pts]
    msp4.add_lwpolyline(p_oct_nested, close=True, dxfattribs={'layer': 'CUT'})
    msp4.add_text("TOP OCTAGON COVER (1 EA)", height=22.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((oct_center_x, oct_center_y), align=TextEntityAlignment.MIDDLE_CENTER)

    fp4 = os.path.join(out_dir, "04_팔각모_CNC_네스팅_원장배치도.dxf")
    doc4.saveas(fp4)
    print(f"[OK] Saved: {os.path.basename(fp4)}")

    # =========================================================================
    # [5] 종합 제작 도면 (05_팔각모_종합_제작도면.dxf)
    # =========================================================================
    doc5 = ezdxf.new("R2010")
    setup_layers(doc5)
    msp5 = doc5.modelspace()
    
    # Place Side Panel at (0, 0)
    msp5.add_lwpolyline(side_pts, close=True, dxfattribs={'layer': 'CUT'})
    msp5.add_line((0, -20), (0, 420), dxfattribs={'layer': 'MARK_FOLD'})
    draw_linear_dim(msp5, (-135, 0), (135, 0), -45, "270.0 mm (Bottom)")
    draw_linear_dim(msp5, (-200, 400), (200, 400), 45, "400.0 mm (Top)")
    draw_linear_dim(msp5, (200, 0), (200, 400), 55, "400.0 mm (H)", vertical=True)
    msp5.add_text("[PART 1] SIDE TRAPEZOID (QTY: 8 EA)", height=24.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((0, -100), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Place Brim at (700, 0)
    bx0, by0 = 700.0, 0.0
    p_brim_draw = [(bx0 + x, by0 + y) for (x, y) in brim_pts]
    msp5.add_lwpolyline(p_brim_draw, close=True, dxfattribs={'layer': 'CUT'})
    msp5.add_line((bx0, by0 - 25), (bx0, by0 + 525), dxfattribs={'layer': 'MARK_FOLD'})
    draw_linear_dim(msp5, (bx0 - 260, by0), (bx0 + 260, by0), -50, "520.0 mm (Joint Base)")
    draw_linear_dim(msp5, (bx0 - 325, by0 + 500), (bx0 + 325, by0 + 500), 50, "650.0 mm (Outer Tip)")
    draw_linear_dim(msp5, (bx0 + 325, by0), (bx0 + 325, by0 + 500), 65, "500.0 mm (Depth)", vertical=True)
    msp5.add_text("[PART 2] BRIM / VISOR (QTY: 1 EA)", height=24.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((bx0, by0 - 100), align=TextEntityAlignment.MIDDLE_CENTER)

    # Place Top Octagon at (1700, 250)
    ox0, oy0 = 1750.0, 250.0
    p_oct_draw = [(ox0 + x, oy0 + y) for (x, y) in top_oct_pts]
    msp5.add_lwpolyline(p_oct_draw, close=True, dxfattribs={'layer': 'CUT'})
    draw_linear_dim(msp5, (ox0 - r_top, oy0 - r_top), (ox0 + r_top, oy0 - r_top), -50, f"{2*r_top:.1f} mm (Width)")
    msp5.add_text("[PART 3] TOP OCTAGON COVER (QTY: 1 EA)", height=24.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((ox0, oy0 - R_top - 90), align=TextEntityAlignment.MIDDLE_CENTER)

    # Title block border & text
    frame_pts = [(-350, -250), (2400, -250), (2400, 850), (-350, 850)]
    msp5.add_lwpolyline(frame_pts, close=True, dxfattribs={'layer': 'DIMENSION'})
    msp5.add_text("MACHINE ART LAB - OCTAGONAL CAP & BRIM CNC SHOP DRAWING", height=32.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((1025, 780), align=TextEntityAlignment.TOP_CENTER)
    msp5.add_text("MATERIAL: PLYWOOD / MDF / ACRYLIC / AL-COMPOSITE | UNIT: mm | 1:1 CNC CUTTING", height=18.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((1025, 730), align=TextEntityAlignment.TOP_CENTER)
    msp5.add_text("ASSEMBLY SPEC: DIHEDRAL 138.78 deg | EDGE BEVEL 20.61 deg | CAP 3D HEIGHT 367.93 mm", height=18.0, dxfattribs={'layer': 'TEXT_LABEL'}).set_placement((1025, 690), align=TextEntityAlignment.TOP_CENTER)

    fp5 = os.path.join(out_dir, "05_팔각모_종합_제작도면.dxf")
    doc5.saveas(fp5)
    print(f"[OK] Saved: {os.path.basename(fp5)}")

    print("\nAll 5 DXF CAD files created successfully!")

if __name__ == "__main__":
    create_dxf_files()
