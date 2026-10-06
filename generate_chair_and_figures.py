"""
Machine Art Lab (머신아트랩) - 3D Parametric CAD & Mannequin Generator
Scale: 1:10 Anthropometric & Kinetic Art Scale

Models Generated:
1. chair.step / chair.stl (Seat 40x20mm, Backrest 40x20mm, Height 100mm)
2. person_seated.step / person_seated.stl (Seated mannequin resting on chair)
3. person_standing.step / person_standing.stl (Standing mannequin matching 1:10 scale)
4. chair_with_seated_person.step / chair_with_seated_person.stl (Integrated assembly)
5. comparison_scene.step / comparison_scene.stl (Comparative studio assembly)
"""

import sys
import os
import math
import numpy as np

# FreeCAD library path detection
freecad_paths = [
    r"C:\Program Files\FreeCAD 1.1\bin",
    r"C:\Program Files\FreeCAD 1.0\bin",
    r"C:\Program Files\FreeCAD 0.21\bin",
    r"C:\Program Files\FreeCAD\bin"
]
for p in freecad_paths:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.append(p)

import FreeCAD
import Part
import MeshPart

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ==========================================
# CAD Primitives & Geometric Helpers
# ==========================================

def make_sphere(r, center):
    s = Part.makeSphere(r)
    s.translate(center)
    return s

def make_cylinder_between(p1, p2, r1, r2=None):
    if r2 is None or abs(r1 - r2) < 1e-4:
        v = p2.sub(p1)
        length = v.Length
        if length < 1e-4:
            return Part.makeSphere(r1)
        axis = v.normalize()
        return Part.makeCylinder(r1, length, p1, axis, 360)
    else:
        v = p2.sub(p1)
        length = v.Length
        if length < 1e-4:
            return Part.makeSphere(r1)
        axis = v.normalize()
        return Part.makeCone(r1, r2, length, p1, axis, 360)

def make_rounded_plate_xz(width, height, thickness, r_fillet, center_pt):
    """Watertight analytical rounded rectangular plate in XZ plane with thickness along Y."""
    w = width - 2 * r_fillet
    h = height - 2 * r_fillet
    box = Part.makeBox(w, thickness, h)
    box.translate(FreeCAD.Vector(-w/2, -thickness/2, -h/2))
    
    cyls = []
    for cx in [-w/2, w/2]:
        for cz in [-h/2, h/2]:
            c = Part.makeCylinder(r_fillet, thickness, FreeCAD.Vector(cx, -thickness/2, cz), FreeCAD.Vector(0, 1, 0), 360)
            cyls.append(c)
            
    box_x = Part.makeBox(width, thickness, h)
    box_x.translate(FreeCAD.Vector(-width/2, -thickness/2, -h/2))
    box_z = Part.makeBox(w, thickness, height)
    box_z.translate(FreeCAD.Vector(-w/2, -thickness/2, -height/2))
    
    plate = box.fuse([box_x, box_z] + cyls)
    plate.translate(center_pt)
    return plate

def make_foot(ankle_pos, foot_y_dir=1.0):
    """Articulated anatomical foot plate with heel, metatarsal arch, and toes flat on Z=0."""
    heel_pt = FreeCAD.Vector(ankle_pos.x, ankle_pos.y - 4.0 * foot_y_dir, 3.0)
    ball_pt = FreeCAD.Vector(ankle_pos.x, ankle_pos.y + 11.0 * foot_y_dir, 3.0)
    toes_pt = FreeCAD.Vector(ankle_pos.x, ankle_pos.y + 16.0 * foot_y_dir, 2.5)
    
    s_heel = make_sphere(3.2, heel_pt)
    s_ball = make_sphere(3.2, ball_pt)
    s_toes = make_sphere(2.6, toes_pt)
    
    bridge = make_cylinder_between(ankle_pos, ball_pt, 2.5, 2.5)
    sole1 = make_cylinder_between(heel_pt, ball_pt, 2.8, 2.8)
    sole2 = make_cylinder_between(ball_pt, toes_pt, 2.8, 2.3)
    return s_heel.fuse([s_ball, s_toes, bridge, sole1, sole2])

def make_head(head_center, jaw_offset_y=1.5):
    """Sculpted cranium with facial taper and chin."""
    cranium = Part.makeSphere(7.2)
    cranium.translate(head_center)
    jaw_pt = FreeCAD.Vector(head_center.x, head_center.y + jaw_offset_y, head_center.z - 7.5)
    jaw_cone = make_cylinder_between(head_center, jaw_pt, 5.5, 3.5)
    chin = make_sphere(3.8, jaw_pt)
    return cranium.fuse([jaw_cone, chin])

# ==========================================
# 1. Chair CAD Model Builder
# ==========================================

def build_chair(base_x=0.0, base_y=0.0):
    """
    Constructs the chair solid matching the user sketches:
    - Seat plate: Width 40mm, Depth 20mm, Height Z=50mm
    - Backrest plate: Width 40mm, Height 20mm, Z=80-100mm
    - Total Height: 100mm (10cm)
    - Curved tubular connector & sturdy vertical pillar with mechanism collar
    """
    parts = []
    
    # 1. Pedestal Base Disk (Stable standalone base for display & 3D printing)
    base_disk = Part.makeCylinder(18.0, 2.5, FreeCAD.Vector(base_x, base_y, 0), FreeCAD.Vector(0, 0, 1), 360)
    base_step = Part.makeCone(18.0, 10.0, 1.5, FreeCAD.Vector(base_x, base_y, 2.5), FreeCAD.Vector(0, 0, 1), 360)
    parts.append(base_disk.fuse(base_step))
    
    # 2. Main Vertical Support Pillar
    pillar = Part.makeCylinder(2.8, 39.0, FreeCAD.Vector(base_x, base_y, 3.5), FreeCAD.Vector(0, 0, 1), 360)
    parts.append(pillar)
    
    # 3. Kinematic Mechanism Collar / Fitting
    collar = Part.makeCylinder(4.2, 4.0, FreeCAD.Vector(base_x, base_y, 41.5), FreeCAD.Vector(0, 0, 1), 360)
    parts.append(collar)
    
    # 4. Under-seat Support Bracket
    bracket = Part.makeBox(12.0, 16.0, 3.0)
    bracket.translate(FreeCAD.Vector(base_x - 6.0, base_y - 8.0, 44.5))
    parts.append(bracket)
    
    # 5. Curved Saddle Seat Plate (Width 40mm, Depth 20mm, Thickness 2.5mm)
    width = 40.0
    depth = 20.0
    thickness = 2.5
    r_curve = 45.0
    center_z = 47.5 + r_curve
    cyl_out = Part.makeCylinder(r_curve, depth, FreeCAD.Vector(base_x, base_y - depth/2, center_z), FreeCAD.Vector(0, 1, 0), 360)
    cyl_in = Part.makeCylinder(r_curve - thickness, depth + 2, FreeCAD.Vector(base_x, base_y - depth/2 - 1, center_z), FreeCAD.Vector(0, 1, 0), 360)
    seat_shell = cyl_out.cut(cyl_in)
    
    box_w = Part.makeBox(width, depth, 30.0)
    box_w.translate(FreeCAD.Vector(base_x - width/2, base_y - depth/2, 40.0))
    seat = seat_shell.common(box_w)
    parts.append(seat)
    
    # 6. Smooth Curved Tube Connector to Backrest (Diameter 3.6mm)
    r_tube = 1.8
    # Horizontal under-seat section
    t_run = Part.makeCylinder(r_tube, 8.0, FreeCAD.Vector(base_x, base_y, 46.0), FreeCAD.Vector(0, -1, 0), 360)
    
    # 90-degree Toroidal elbow arc: center (base_x, base_y - 8, 52), R=6.0
    torus = Part.makeTorus(6.0, r_tube, FreeCAD.Vector(base_x, base_y - 8.0, 52.0), FreeCAD.Vector(1, 0, 0))
    clip_box = Part.makeBox(20.0, 10.0, 10.0)
    clip_box.translate(FreeCAD.Vector(base_x - 10.0, base_y - 18.0, 42.0))
    elbow = torus.common(clip_box)
    
    # Vertical ascending tube
    t_vert = Part.makeCylinder(r_tube, 38.0, FreeCAD.Vector(base_x, base_y - 14.0, 52.0), FreeCAD.Vector(0, 0, 1), 360)
    
    # Backrest rear mounting tab
    t_tab = Part.makeCylinder(r_tube, 2.5, FreeCAD.Vector(base_x, base_y - 14.0, 90.0), FreeCAD.Vector(0, 1, 0), 360)
    
    tube = t_run.fuse([elbow, t_vert, t_tab])
    parts.append(tube)
    
    # 7. Backrest Plate (Width 40mm, Height 20mm, Thickness 2.5mm, Top Z=100mm)
    backrest = make_rounded_plate_xz(40.0, 20.0, 2.5, 2.5, FreeCAD.Vector(base_x, base_y - 12.5, 90.0))
    parts.append(backrest)
    
    chair_solid = parts[0].fuse(parts[1:])
    return chair_solid

# ==========================================
# 2. Seated Mannequin Builder (1:10 Scale)
# ==========================================

def build_seated_figure(offset_x=0.0, offset_y=0.0):
    """
    Constructs the seated figure sitting naturally on the chair:
    - Pelvis sit-bones resting on seat surface at Z=50mm
    - Thighs forward along Y, knees bent ~90 degrees
    - Calves down to floor with feet resting flat on Z=0
    - Upright torso resting gently against backrest
    - Arms resting naturally forward on thighs
    """
    parts = []
    
    # Head & Neck
    head_c = FreeCAD.Vector(offset_x, offset_y + 0.5, 115.0)
    parts.append(make_head(head_c))
    
    neck_base = FreeCAD.Vector(offset_x, offset_y - 1.0, 96.0)
    neck_top = FreeCAD.Vector(offset_x, offset_y + 0.0, 107.0)
    parts.append(make_cylinder_between(neck_base, neck_top, 2.8, 2.6))
    parts.append(make_sphere(3.2, neck_base))
    parts.append(make_sphere(3.0, neck_top))
    
    # Torso
    chest_top = FreeCAD.Vector(offset_x, offset_y - 2.0, 94.0)
    waist_pt = FreeCAD.Vector(offset_x, offset_y - 1.0, 72.0)
    pelvis_pt = FreeCAD.Vector(offset_x, offset_y + 0.0, 54.0)
    
    parts.append(make_cylinder_between(chest_top, waist_pt, 7.0, 5.0))
    parts.append(make_cylinder_between(waist_pt, pelvis_pt, 5.0, 6.5))
    parts.append(make_sphere(7.5, chest_top))
    parts.append(make_sphere(5.5, waist_pt))
    parts.append(make_sphere(7.0, pelvis_pt))
    
    # Shoulders Bar
    sh_l = FreeCAD.Vector(offset_x - 16.0, offset_y - 2.0, 94.0)
    sh_r = FreeCAD.Vector(offset_x + 16.0, offset_y - 2.0, 94.0)
    parts.append(make_cylinder_between(sh_l, sh_r, 3.5, 3.5))
    parts.append(make_sphere(4.0, sh_l))
    parts.append(make_sphere(4.0, sh_r))
    
    # Pelvis Bar
    hip_l = FreeCAD.Vector(offset_x - 9.5, offset_y + 2.0, 54.0)
    hip_r = FreeCAD.Vector(offset_x + 9.5, offset_y + 2.0, 54.0)
    parts.append(make_cylinder_between(hip_l, hip_r, 4.0, 4.0))
    parts.append(make_sphere(4.5, hip_l))
    parts.append(make_sphere(4.5, hip_r))
    
    # Arms: Shoulders -> Elbows -> Wrists -> Hands on thighs
    for sign in [-1, 1]:
        sh = FreeCAD.Vector(offset_x + sign * 16.0, offset_y - 2.0, 94.0)
        elb = FreeCAD.Vector(offset_x + sign * 15.5, offset_y + 10.0, 73.0)
        wri = FreeCAD.Vector(offset_x + sign * 11.5, offset_y + 26.0, 56.0)
        hand = FreeCAD.Vector(offset_x + sign * 11.0, offset_y + 36.0, 55.0)
        
        parts.append(make_cylinder_between(sh, elb, 3.2, 2.5))
        parts.append(make_sphere(3.0, elb))
        parts.append(make_cylinder_between(elb, wri, 2.5, 2.0))
        parts.append(make_sphere(2.5, wri))
        parts.append(make_cylinder_between(wri, hand, 2.0, 1.6))
        parts.append(make_sphere(2.0, hand))
        
    # Legs: Hips -> Knees -> Ankles -> Feet on ground
    for sign in [-1, 1]:
        hip = FreeCAD.Vector(offset_x + sign * 9.5, offset_y + 2.0, 54.0)
        knee = FreeCAD.Vector(offset_x + sign * 9.5, offset_y + 40.0, 51.0)
        ankle = FreeCAD.Vector(offset_x + sign * 9.5, offset_y + 40.0, 7.0)
        
        parts.append(make_cylinder_between(hip, knee, 3.8, 3.2))
        parts.append(make_sphere(3.8, knee))
        parts.append(make_cylinder_between(knee, ankle, 3.2, 2.6))
        parts.append(make_sphere(3.0, ankle))
        parts.append(make_foot(ankle, foot_y_dir=1.0))
        
    body = parts[0].fuse(parts[1:])
    return body

# ==========================================
# 3. Standing Mannequin Builder (1:10 Scale)
# ==========================================

def build_standing_figure(offset_x=0.0, offset_y=0.0):
    """
    Constructs the standing mannequin matching the exact scale:
    - Same limb proportions as seated figure
    - Total Height: ~163-168mm (1:10 scale of 1.68m adult)
    - Feet flat on floor Z=0
    """
    parts = []
    
    # Head & Neck
    head_c = FreeCAD.Vector(offset_x, offset_y, 156.0)
    parts.append(make_head(head_c))
    
    neck_base = FreeCAD.Vector(offset_x, offset_y, 137.0)
    neck_top = FreeCAD.Vector(offset_x, offset_y, 148.0)
    parts.append(make_cylinder_between(neck_base, neck_top, 2.8, 2.6))
    parts.append(make_sphere(3.2, neck_base))
    parts.append(make_sphere(3.0, neck_top))
    
    # Torso
    chest_top = FreeCAD.Vector(offset_x, offset_y, 134.0)
    waist_pt = FreeCAD.Vector(offset_x, offset_y, 108.0)
    pelvis_pt = FreeCAD.Vector(offset_x, offset_y, 88.0)
    
    parts.append(make_cylinder_between(chest_top, waist_pt, 7.0, 5.0))
    parts.append(make_cylinder_between(waist_pt, pelvis_pt, 5.0, 6.5))
    parts.append(make_sphere(7.5, chest_top))
    parts.append(make_sphere(5.5, waist_pt))
    parts.append(make_sphere(7.0, pelvis_pt))
    
    # Shoulders Bar
    sh_l = FreeCAD.Vector(offset_x - 16.0, offset_y, 133.0)
    sh_r = FreeCAD.Vector(offset_x + 16.0, offset_y, 133.0)
    parts.append(make_cylinder_between(sh_l, sh_r, 3.5, 3.5))
    parts.append(make_sphere(4.0, sh_l))
    parts.append(make_sphere(4.0, sh_r))
    
    # Pelvis Bar
    hip_l = FreeCAD.Vector(offset_x - 9.5, offset_y, 86.0)
    hip_r = FreeCAD.Vector(offset_x + 9.5, offset_y, 86.0)
    parts.append(make_cylinder_between(hip_l, hip_r, 4.0, 4.0))
    parts.append(make_sphere(4.5, hip_l))
    parts.append(make_sphere(4.5, hip_r))
    
    # Arms: Hanging naturally at sides
    for sign in [-1, 1]:
        sh = FreeCAD.Vector(offset_x + sign * 16.0, offset_y, 133.0)
        elb = FreeCAD.Vector(offset_x + sign * 16.5, offset_y, 106.0)
        wri = FreeCAD.Vector(offset_x + sign * 16.5, offset_y, 82.0)
        hand = FreeCAD.Vector(offset_x + sign * 16.5, offset_y, 70.0)
        
        parts.append(make_cylinder_between(sh, elb, 3.2, 2.5))
        parts.append(make_sphere(3.0, elb))
        parts.append(make_cylinder_between(elb, wri, 2.5, 2.0))
        parts.append(make_sphere(2.5, wri))
        parts.append(make_cylinder_between(wri, hand, 2.0, 1.6))
        parts.append(make_sphere(2.0, hand))
        
    # Legs: Hips -> Knees -> Ankles -> Feet on ground
    for sign in [-1, 1]:
        hip = FreeCAD.Vector(offset_x + sign * 9.5, offset_y, 86.0)
        knee = FreeCAD.Vector(offset_x + sign * 9.5, offset_y, 46.0)
        ankle = FreeCAD.Vector(offset_x + sign * 9.5, offset_y, 7.0)
        
        parts.append(make_cylinder_between(hip, knee, 3.8, 3.2))
        parts.append(make_sphere(3.8, knee))
        parts.append(make_cylinder_between(knee, ankle, 3.2, 2.6))
        parts.append(make_sphere(3.0, ankle))
        parts.append(make_foot(ankle, foot_y_dir=1.0))
        
    body = parts[0].fuse(parts[1:])
    return body

# ==========================================
# 4. Rendering Engine
# ==========================================

def render_3d_view(shapes_with_colors, output_png, elev=18, azim=45, title="", zoom_padding=0.15):
    """Generates high-resolution shaded 3D perspective renders."""
    fig = plt.figure(figsize=(10, 8), dpi=200)
    ax = fig.add_subplot(111, projection='3d')
    
    key_light = np.array([-0.5, 0.7, 0.6])
    key_light = key_light / np.linalg.norm(key_light)
    fill_light = np.array([0.6, -0.4, 0.5])
    fill_light = fill_light / np.linalg.norm(fill_light)
    
    all_points = []
    
    for shape, base_color in shapes_with_colors:
        m = MeshPart.meshFromShape(shape, Deflection=0.25)
        verts = []
        shaded_colors = []
        base_rgb = np.array(matplotlib.colors.to_rgb(base_color))
        
        for facet in m.Facets:
            pts = [list(p) for p in facet.Points]
            verts.append(pts)
            all_points.extend(pts)
            
            n = np.array([facet.Normal.x, facet.Normal.y, facet.Normal.z])
            norm_len = np.linalg.norm(n)
            if norm_len > 1e-4:
                n = n / norm_len
                dot_key = max(0.0, np.dot(n, key_light))
                dot_fill = max(0.0, np.dot(n, fill_light))
                intensity = 0.30 + 0.55 * dot_key + 0.20 * dot_fill
            else:
                intensity = 0.5
                
            color = np.clip(base_rgb * intensity, 0, 1)
            shaded_colors.append(color)
            
        poly = Poly3DCollection(verts, facecolors=shaded_colors, edgecolors='#1e293b', linewidths=0.18, alpha=0.98)
        ax.add_collection3d(poly)
        
    all_points = np.array(all_points)
    x_min, x_max = all_points[:, 0].min(), all_points[:, 0].max()
    y_min, y_max = all_points[:, 1].min(), all_points[:, 1].max()
    z_min, z_max = all_points[:, 2].min(), all_points[:, 2].max()
    
    mid_x = (x_max + x_min) * 0.5
    mid_y = (y_max + y_min) * 0.5
    mid_z = (z_max + z_min) * 0.5
    half_range = max(x_max - x_min, y_max - y_min, z_max - z_min) * 0.5 * (1.0 + zoom_padding)
    
    ax.set_xlim(mid_x - half_range, mid_x + half_range)
    ax.set_ylim(mid_y - half_range, mid_y + half_range)
    ax.set_zlim(0, 2 * half_range)
    
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.patch.set_facecolor('#0b0f19')  # Deep studio obsidian background
    ax.set_facecolor('#0b0f19')
    
    if title:
        plt.title(title, color='#f8fafc', fontsize=14, pad=-15, weight='bold')
        
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', dpi=200)
    plt.close()
    print(f"  [Rendered Image] -> {output_png}")

# ==========================================
# Main Execution Pipeline
# ==========================================

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(root_dir, "models")
    previews_dir = os.path.join(root_dir, "previews")
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(previews_dir, exist_ok=True)
    
    print("=" * 60)
    print("Machine Art Lab - 3D CAD & Figure Generation Pipeline")
    print("=" * 60)
    
    # 1. Build Shapes
    print("\n[1/4] Building Parametric Geometry...")
    chair = build_chair(0, 0)
    print(f"  - Chair Solid: Volume={chair.Volume:.1f} mm^3, Height={chair.BoundBox.ZLength:.1f} mm (Valid={chair.isValid()})")
    
    seated = build_seated_figure(0, 0)
    print(f"  - Seated Figure: Volume={seated.Volume:.1f} mm^3, Height={seated.BoundBox.ZLength:.1f} mm (Valid={seated.isValid()})")
    
    standing = build_standing_figure(0, 0)
    print(f"  - Standing Figure: Volume={standing.Volume:.1f} mm^3, Height={standing.BoundBox.ZLength:.1f} mm (Valid={standing.isValid()})")
    
    standing_side = build_standing_figure(52, 6)
    chair_seated_comp = Part.makeCompound([chair, seated])
    comparison_scene = Part.makeCompound([chair, seated, standing_side])
    
    # 2. Export STEP CAD Files
    print("\n[2/4] Exporting STEP (ISO 10303) CAD Files...")
    step_targets = [
        ("chair.step", chair),
        ("person_seated.step", seated),
        ("person_standing.step", standing),
        ("chair_with_seated_person.step", chair_seated_comp),
        ("comparison_scene.step", comparison_scene)
    ]
    for filename, shape in step_targets:
        target_path = os.path.join(models_dir, filename)
        shape.exportStep(target_path)
        print(f"  -> Exported: {filename} ({os.path.getsize(target_path):,} bytes)")
        
    # 3. Export High-Resolution STL Files
    print("\n[3/4] Exporting High-Resolution STL Meshes for 3D Printing...")
    stl_targets = [
        ("chair.stl", chair, 0.12),
        ("person_seated.stl", seated, 0.15),
        ("person_standing.stl", standing, 0.15),
        ("chair_with_seated_person.stl", chair_seated_comp, 0.15),
        ("comparison_scene.stl", comparison_scene, 0.18)
    ]
    for filename, shape, defl in stl_targets:
        target_path = os.path.join(models_dir, filename)
        mesh = MeshPart.meshFromShape(shape, Deflection=defl)
        mesh.write(target_path)
        print(f"  -> Exported: {filename} ({mesh.CountFacets:,} facets, {os.path.getsize(target_path):,} bytes)")
        
    # 4. Generate Studio Renders
    print("\n[4/4] Generating Studio Previews & Documentation Renders...")
    # Palette: Steel Blue #2563eb, Titanium White #f8fafc, Brushed Nickel #cbd5e1
    
    # 1. Comparison Isometric
    render_3d_view(
        [(chair, '#3b82f6'), (seated, '#f8fafc'), (standing_side, '#cbd5e1')],
        os.path.join(previews_dir, "preview_comparison_isometric.png"),
        elev=18, azim=45,
        title="1:10 Scale Comparative Study (Chair, Seated & Standing Figure)"
    )
    
    # 2. Side View Profile (Direct comparison with sketch 2)
    render_3d_view(
        [(chair, '#3b82f6'), (seated, '#f8fafc'), (standing_side, '#cbd5e1')],
        os.path.join(previews_dir, "preview_side_profile.png"),
        elev=4, azim=0,
        title="Side Profile View - Kinematic Alignment & Anthropometry"
    )
    
    # 3. Chair with Seated Person Close-up
    render_3d_view(
        [(chair, '#3b82f6'), (seated, '#f8fafc')],
        os.path.join(previews_dir, "preview_chair_with_seated_figure.png"),
        elev=20, azim=50,
        title="Chair with Seated Figure Assembly"
    )
    
    # 4. Chair Isometric Detail
    render_3d_view(
        [(chair, '#3b82f6')],
        os.path.join(previews_dir, "preview_chair_isometric.png"),
        elev=22, azim=45,
        title="Chair Mechanism (Seat 40x20mm, Backrest 40x20mm, Height 100mm)"
    )
    
    # 5. Standing Figure Front
    render_3d_view(
        [(standing, '#f8fafc')],
        os.path.join(previews_dir, "preview_standing_figure.png"),
        elev=10, azim=25,
        title="1:10 Scale Standing Articulated Mannequin (Height ~168mm)"
    )
    
    print("\n" + "=" * 60)
    print("All CAD models, STL meshes, and studio renders successfully generated!")
    print("=" * 60)

if __name__ == '__main__':
    main()
