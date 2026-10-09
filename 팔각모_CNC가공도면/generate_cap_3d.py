import os
import sys
import math
import numpy as np

# FreeCAD 1.1 Python environment execution script
import FreeCAD
import Part
import MeshPart
import Mesh

def generate_3d_cad():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 70)
    print("Generating 3D Parametric CAD Solid Models (STEP / STL / OBJ)")
    print("=" * 70)

    # Plate thickness for 3D model representation (e.g., 15mm standard sheet)
    thickness = 15.0

    n = 8
    s_bot = 270.0
    s_top = 400.0
    h_slant = 400.0

    # Apothem & circumradii
    r_bot = (s_bot / 2.0) / math.tan(math.pi / n)
    R_bot = (s_bot / 2.0) / math.sin(math.pi / n)
    r_top = (s_top / 2.0) / math.tan(math.pi / n)
    R_top = (s_top / 2.0) / math.sin(math.pi / n)

    dr = r_top - r_bot
    H_3d = math.sqrt(h_slant**2 - dr**2)

    print(f"Cap Dimensions: Bottom Outer Ø{2*R_bot:.1f}mm, Top Outer Ø{2*R_top:.1f}mm, Height {H_3d:.1f}mm")

    # 1. Build 8 Side Panels as Solid Plates
    side_solids = []
    
    # Vertices of facet 0 (centered around X axis, between angle -pi/8 and +pi/8)
    a1 = -math.pi / n
    a2 =  math.pi / n
    
    # Outer surface vertices of Facet 0
    p_b1_out = FreeCAD.Vector(R_bot * math.cos(a1), R_bot * math.sin(a1), 0.0)
    p_b2_out = FreeCAD.Vector(R_bot * math.cos(a2), R_bot * math.sin(a2), 0.0)
    p_t2_out = FreeCAD.Vector(R_top * math.cos(a2), R_top * math.sin(a2), H_3d)
    p_t1_out = FreeCAD.Vector(R_top * math.cos(a1), R_top * math.sin(a1), H_3d)

    # Face normal of facet 0 pointing inwards
    # Slant vector: (dr, 0, H_3d) -> Inward normal: (-H_3d, 0, dr) normalized
    norm_len = math.sqrt(H_3d**2 + dr**2) # equals h_slant = 400.0
    nx = -H_3d / norm_len
    nz = dr / norm_len
    inward_offset = FreeCAD.Vector(nx * thickness, 0, nz * thickness)

    # Inner surface vertices
    p_b1_in = p_b1_out + inward_offset
    p_b2_in = p_b2_out + inward_offset
    p_t2_in = p_t2_out + inward_offset
    p_t1_in = p_t1_out + inward_offset

    # Construct single 3D panel solid using BRep Loft
    w1 = Part.makePolygon([p_b1_out, p_b2_out, p_t2_out, p_t1_out, p_b1_out])
    w2 = Part.makePolygon([p_b1_in, p_b2_in, p_t2_in, p_t1_in, p_b1_in])
    panel_solid_0 = Part.makeLoft([w1, w2], True)

    # Create 8 panels by rotating around Z axis
    for k in range(n):
        ang_deg = k * (360.0 / n)
        p_copy = panel_solid_0.copy()
        p_copy.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), ang_deg)
        side_solids.append(p_copy)

    # 2. Build Brim Solid (Visor)
    brim_w_bot = 520.0
    brim_w_top = 650.0
    brim_len = 500.0
    brim_tilt_deg = -18.0
    brim_tilt_rad = math.radians(brim_tilt_deg)

    x_attach = r_bot - 10.0
    
    def brim_coord(x_local, y_local, z_thick=0.0):
        X = x_attach + y_local * math.cos(brim_tilt_rad) - z_thick * math.sin(brim_tilt_rad)
        Y = x_local
        Z = y_local * math.sin(brim_tilt_rad) + z_thick * math.cos(brim_tilt_rad)
        return FreeCAD.Vector(X, Y, Z)

    bp1_out = brim_coord(-brim_w_bot/2.0, 0.0, 0.0)
    bp2_out = brim_coord( brim_w_bot/2.0, 0.0, 0.0)
    bp3_out = brim_coord( brim_w_top/2.0, brim_len, 0.0)
    bp4_out = brim_coord(-brim_w_top/2.0, brim_len, 0.0)

    bp1_in = brim_coord(-brim_w_bot/2.0, 0.0, -thickness)
    bp2_in = brim_coord( brim_w_bot/2.0, 0.0, -thickness)
    bp3_in = brim_coord( brim_w_top/2.0, brim_len, -thickness)
    bp4_in = brim_coord(-brim_w_top/2.0, brim_len, -thickness)

    bw_out = Part.makePolygon([bp1_out, bp2_out, bp3_out, bp4_out, bp1_out])
    bw_in  = Part.makePolygon([bp1_in,  bp2_in,  bp3_in,  bp4_in,  bp1_in])
    brim_solid = Part.makeLoft([bw_out, bw_in], True)

    # 3. Build Top Octagonal Cover Plate (Optional Crown Cover)
    top_oct_pts = []
    top_oct_pts_in = []
    for i in range(n):
        ang = math.pi / n + i * (2 * math.pi / n)
        top_oct_pts.append(FreeCAD.Vector(R_top * math.cos(ang), R_top * math.sin(ang), H_3d))
        top_oct_pts_in.append(FreeCAD.Vector(R_top * math.cos(ang), R_top * math.sin(ang), H_3d - thickness))
    top_oct_pts.append(top_oct_pts[0])
    top_oct_pts_in.append(top_oct_pts_in[0])

    top_w_out = Part.makePolygon(top_oct_pts)
    top_w_in  = Part.makePolygon(top_oct_pts_in)
    top_cover_solid = Part.makeLoft([top_w_out, top_w_in], True)

    # Combine All Components into Compound Assembly
    all_parts = side_solids + [brim_solid, top_cover_solid]
    assembly_compound = Part.makeCompound(all_parts)

    # 4. Export STEP Files
    step_path_full = os.path.join(out_dir, "06_팔각모_3D_어셈블리_완성형.step")
    assembly_compound.exportStep(step_path_full)
    print(f"[OK] Exported STEP Assembly: {os.path.basename(step_path_full)}")

    step_path_panel = os.path.join(out_dir, "07_팔각모_측면패널_단품.step")
    panel_solid_0.exportStep(step_path_panel)
    print(f"[OK] Exported STEP Single Panel: {os.path.basename(step_path_panel)}")

    step_path_brim = os.path.join(out_dir, "08_팔각모_챙_단품.step")
    brim_solid.exportStep(step_path_brim)
    print(f"[OK] Exported STEP Brim: {os.path.basename(step_path_brim)}")

    # 5. Export STL & OBJ Files using MeshPart
    mesh_doc = MeshPart.meshFromShape(assembly_compound, LinearDeflection=1.0, AngularDeflection=0.3)
    stl_path = os.path.join(out_dir, "09_팔각모_3D_어셈블리_완성형.stl")
    mesh_doc.write(stl_path)
    print(f"[OK] Exported STL Mesh: {os.path.basename(stl_path)}")

    obj_path = os.path.join(out_dir, "10_팔각모_3D_어셈블리_완성형.obj")
    mesh_doc.write(obj_path)
    print(f"[OK] Exported OBJ Mesh: {os.path.basename(obj_path)}")

    print("\nAll 3D Solid Models & CAD STEP/STL/OBJ files generated successfully!")

if __name__ == "__main__":
    generate_3d_cad()
