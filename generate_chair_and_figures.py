"""
Machine Art Lab (머신아트랩) - 3D Parametric CAD & Multi-Plate Slicer Generator
Scale: 1:10 Anthropometric & Kinetic Art Scale

Key Features:
1. Ultra-Smooth Analytical & Lofted Geometry:
   - Analytical smooth cylinders & cones for chair pillar, collar, and limbs.
   - Smooth conical under-seat bracket (zero sharp box corners).
   - Ergonomic curved saddle seat with R=3.0mm rounded corners.
   - Seamless swept 3D circular pipe for backrest tube.
   - Ergonomically contoured & rounded backrest plate.
   - Anatomically lofted continuous S-curve torso for human mannequins.
   - Natural curved sloping shoulders (trapezius line) & curved pelvic cradle.
   - High-density meshing for glassy smooth STL/3MF surfaces in slicers.

2. Detachable Base Disk:
   - Base disk separated from chair pillar with a precision central socket hole (Ø5.8mm with lead-in chamfer).
   - Chair pillar extends to Z=0 with lead-in chamfer for easy push-fit insertion.

3. Multi-Plate Print Batch Generation (Bambu Studio 256x256mm Bed Optimized):
   - Plate 1: 11x Chairs (의자 본체 11개)
   - Plate 2: 11x Seated Persons (앉아있는 사람 11개)
   - Plate 3: 11x Base Disks + 3x Standing Persons (분리형 원판 11개 + 서있는 사람 3개)
   - Plate 3A: 11x Base Disks (원판 11개 전용 플레이트 - 서포트 없는 고속 출력)
   - Plate 4: 3x Standing Persons (서있는 사람 3개 전용 플레이트)
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
import Mesh

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

def make_rounded_plate_xy(width, depth, height, r_fillet, center_pt=FreeCAD.Vector(0,0,0)):
    """Watertight analytical rounded rectangular plate in XY plane with height along Z."""
    w = width - 2 * r_fillet
    d = depth - 2 * r_fillet
    box = Part.makeBox(w, d, height)
    box.translate(FreeCAD.Vector(-w/2, -d/2, -height/2))
    cyls = []
    for cx in [-w/2, w/2]:
        for cy in [-d/2, d/2]:
            c = Part.makeCylinder(r_fillet, height, FreeCAD.Vector(cx, cy, -height/2), FreeCAD.Vector(0, 0, 1), 360)
            cyls.append(c)
    box_x = Part.makeBox(width, d, height)
    box_x.translate(FreeCAD.Vector(-width/2, -d/2, -height/2))
    box_y = Part.makeBox(w, depth, height)
    box_y.translate(FreeCAD.Vector(-w/2, -depth/2, -height/2))
    plate = box.fuse([box_x, box_y] + cyls)
    plate.translate(center_pt)
    return plate

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
    """Sculpted cranium with facial taper and smooth chin."""
    cranium = Part.makeSphere(7.2)
    cranium.translate(head_center)
    jaw_pt = FreeCAD.Vector(head_center.x, head_center.y + jaw_offset_y, head_center.z - 7.5)
    jaw_cone = make_cylinder_between(head_center, jaw_pt, 5.5, 3.5)
    chin = make_sphere(3.8, jaw_pt)
    return cranium.fuse([jaw_cone, chin])

# ==========================================
# 1. Detachable Chair Base Disk Builder
# ==========================================

def build_chair_base(base_x=0.0, base_y=0.0):
    """
    Constructs the detachable circular pedestal base disk:
    - Outer diameter: Ø36.0mm (Radius 18.0mm), Height: 4.0mm
    - Smooth conical top bevel (from R=18 to R=10 at Z=2.5 to 4.0mm)
    - Precision center socket hole: Ø5.8mm (Radius 2.9mm) for snug slip-fit of Ø5.6mm pillar
    - 0.8mm 45-degree lead-in chamfer at the top entrance for effortless pillar insertion
    """
    r_base = 18.0
    h_base = 4.0
    r_hole = 2.9  # Ø5.8mm socket (0.2mm diametral clearance for tight slide-fit)
    
    base_cyl = Part.makeCylinder(r_base, 2.5, FreeCAD.Vector(base_x, base_y, 0), FreeCAD.Vector(0,0,1), 360)
    base_cone = Part.makeCone(r_base, 10.0, 1.5, FreeCAD.Vector(base_x, base_y, 2.5), FreeCAD.Vector(0,0,1), 360)
    base_solid = base_cyl.fuse(base_cone)
    
    # Through-hole with top entrance guide chamfer
    hole = Part.makeCylinder(r_hole, h_base + 1.0, FreeCAD.Vector(base_x, base_y, -0.5), FreeCAD.Vector(0,0,1), 360)
    chamfer = Part.makeCone(r_hole + 0.8, r_hole, 1.0, FreeCAD.Vector(base_x, base_y, h_base - 0.8), FreeCAD.Vector(0,0,1), 360)
    hole_cutter = hole.fuse(chamfer)
    
    base_plate = base_solid.cut(hole_cutter)
    return base_plate

# ==========================================
# 2. Smooth Chair CAD Model Builder (Detached)
# ==========================================

def build_chair(base_x=0.0, base_y=0.0):
    """
    Constructs the standalone smooth chair solid:
    - Main pillar: Smooth analytical cylinder Ø5.6mm (Radius 2.8mm) from Z=0 to Z=42.5mm
      Bottom tip has 0.6mm insertion lead-in chamfer for easy insertion into base hole
    - Mechanism collar: Smooth cylinder Ø8.4mm (Radius 4.2mm)
    - Under-seat bracket: Smooth conical expansion boss (no sharp square boxes!)
    - Saddle seat: Ergonomic saddle curve (R=45mm) with R=3.0mm rounded corners
    - Backrest tube: Seamless swept 3D circular pipe (Ø3.6mm)
    - Backrest: Ergonomic rounded rectangular plate with smooth corner fillets (40x20mm, top Z=100mm)
    """
    parts = []
    
    # 1. Main Vertical Support Pillar (with bottom lead-in chamfer for base insertion)
    tip_cone = Part.makeCone(2.3, 2.8, 0.6, FreeCAD.Vector(base_x, base_y, 0), FreeCAD.Vector(0, 0, 1), 360)
    pillar = Part.makeCylinder(2.8, 41.9, FreeCAD.Vector(base_x, base_y, 0.6), FreeCAD.Vector(0, 0, 1), 360)
    parts.append(tip_cone.fuse(pillar))
    
    # 2. Kinematic Mechanism Collar / Fitting
    collar = Part.makeCylinder(4.2, 3.5, FreeCAD.Vector(base_x, base_y, 41.5), FreeCAD.Vector(0, 0, 1), 360)
    parts.append(collar)
    
    # 3. Smooth Conical Under-seat Bracket (replaces sharp rectangular box)
    bracket = Part.makeCone(4.2, 7.0, 2.5, FreeCAD.Vector(base_x, base_y, 45.0), FreeCAD.Vector(0, 0, 1), 360)
    parts.append(bracket)
    
    # 4. Ergonomic Saddle Seat Plate with Smooth Rounded Corners (40x20x2.5mm)
    width = 40.0
    depth = 20.0
    thickness = 2.5
    r_curve = 45.0
    cyl_out = Part.makeCylinder(r_curve, depth + 10.0, FreeCAD.Vector(base_x, base_y - depth/2 - 5.0, 47.5 + r_curve), FreeCAD.Vector(0, 1, 0), 360)
    cyl_in = Part.makeCylinder(r_curve - thickness, depth + 12.0, FreeCAD.Vector(base_x, base_y - depth/2 - 6.0, 47.5 + r_curve), FreeCAD.Vector(0, 1, 0), 360)
    seat_shell = cyl_out.cut(cyl_in)
    
    seat_boundary = make_rounded_plate_xy(width, depth, 30.0, 3.0, FreeCAD.Vector(base_x, base_y, 50.0))
    seat = seat_shell.common(seat_boundary)
    parts.append(seat)
    
    # 5. Seamless Swept 3D Circular Pipe Connector (Ø3.6mm, R=1.8mm)
    e1 = Part.makeLine(FreeCAD.Vector(base_x, base_y, 46.2), FreeCAD.Vector(base_x, base_y - 8.0, 46.2))
    e2 = Part.makeCircle(6.0, FreeCAD.Vector(base_x, base_y - 8.0, 52.2), FreeCAD.Vector(1, 0, 0), 180, 270)
    e3 = Part.makeLine(FreeCAD.Vector(base_x, base_y - 14.0, 52.2), FreeCAD.Vector(base_x, base_y - 14.0, 90.0))
    edges = Part.__sortEdges__([e1, e2, e3])
    w = Part.Wire(edges)
    circ = Part.makeCircle(1.8, FreeCAD.Vector(base_x, base_y, 46.2), FreeCAD.Vector(0, -1, 0))
    circ_w = Part.Wire([circ])
    pipe = w.makePipeShell([circ_w], True, True)
    
    tab = Part.makeCylinder(1.8, 3.0, FreeCAD.Vector(base_x, base_y - 14.0, 90.0), FreeCAD.Vector(0, 1, 0), 360)
    tube = pipe.fuse(tab)
    parts.append(tube)
    
    # 6. Ergonomic Rounded Backrest Plate (40x20x2.5mm, top at Z=100mm)
    w_bk = 40.0 - 2 * 3.0
    h_bk = 20.0 - 2 * 3.0
    b_box = Part.makeBox(w_bk, 2.5, h_bk)
    b_box.translate(FreeCAD.Vector(base_x - w_bk/2, base_y - 12.5 - 1.25, 90.0 - h_bk/2))
    cyls = []
    for cx in [base_x - w_bk/2, base_x + w_bk/2]:
        for cz in [90.0 - h_bk/2, 90.0 + h_bk/2]:
            c = Part.makeCylinder(3.0, 2.5, FreeCAD.Vector(cx, base_y - 12.5 - 1.25, cz), FreeCAD.Vector(0, 1, 0), 360)
            cyls.append(c)
    box_x = Part.makeBox(40.0, 2.5, h_bk)
    box_x.translate(FreeCAD.Vector(base_x - 20.0, base_y - 12.5 - 1.25, 90.0 - h_bk/2))
    box_z = Part.makeBox(w_bk, 2.5, 20.0)
    box_z.translate(FreeCAD.Vector(base_x - w_bk/2, base_y - 12.5 - 1.25, 80.0))
    backrest = b_box.fuse([box_x, box_z] + cyls)
    parts.append(backrest)
    
    chair_solid = parts[0].fuse(parts[1:])
    return chair_solid

# ==========================================
# 3. Smooth Seated Mannequin Builder (1:10 Scale)
# ==========================================

def build_seated_figure(offset_x=0.0, offset_y=0.0):
    """
    Constructs the seated figure with smooth organic curves:
    - Smooth continuous lofted anatomical torso following the spine curve
    - Natural curved sloping shoulders (trapezius contour into shoulder spheres)
    - Natural contoured pelvic cradle (into hip spheres)
    - Smooth tapered cylindrical limbs with spherical joints
    - Feet flat on floor Z=0, hands resting forward on thighs
    """
    parts = []
    
    # Head & Neck
    head_c = FreeCAD.Vector(offset_x, offset_y + 0.5, 115.0)
    parts.append(make_head(head_c))
    
    neck_base = FreeCAD.Vector(offset_x, offset_y - 1.0, 95.0)
    neck_top = FreeCAD.Vector(offset_x, offset_y + 0.0, 107.0)
    parts.append(make_cylinder_between(neck_base, neck_top, 2.8, 2.5))
    parts.append(make_sphere(3.0, neck_base))
    parts.append(make_sphere(3.0, neck_top))
    
    # Smooth continuous lofted torso (chest -> ribcage -> waist -> pelvis)
    pts_radii = [
        (FreeCAD.Vector(offset_x, offset_y - 2.0, 94.0), 7.5),
        (FreeCAD.Vector(offset_x, offset_y - 2.2, 85.0), 7.2),
        (FreeCAD.Vector(offset_x, offset_y - 1.5, 75.0), 5.8),
        (FreeCAD.Vector(offset_x, offset_y - 0.8, 65.0), 6.0),
        (FreeCAD.Vector(offset_x, offset_y + 0.0, 54.0), 7.0)
    ]
    wires = [Part.Wire([Part.makeCircle(r, pt, FreeCAD.Vector(0, 0, 1))]) for pt, r in pts_radii]
    torso = Part.makeLoft(wires, True)
    s_top = make_sphere(7.5, pts_radii[0][0])
    s_bot = make_sphere(7.0, pts_radii[-1][0])
    parts.append(torso.fuse([s_top, s_bot]))
    
    # Natural sloping shoulders (replacing rigid horizontal crossbar)
    sh_l = FreeCAD.Vector(offset_x - 16.0, offset_y - 2.0, 93.0)
    sh_r = FreeCAD.Vector(offset_x + 16.0, offset_y - 2.0, 93.0)
    chest_top = pts_radii[0][0]
    parts.append(make_cylinder_between(chest_top, sh_l, 4.2, 3.5))
    parts.append(make_cylinder_between(chest_top, sh_r, 4.2, 3.5))
    parts.append(make_sphere(4.0, sh_l))
    parts.append(make_sphere(4.0, sh_r))
    
    # Natural pelvic cradle (replacing rigid horizontal crossbar)
    hip_l = FreeCAD.Vector(offset_x - 9.5, offset_y + 2.0, 54.0)
    hip_r = FreeCAD.Vector(offset_x + 9.5, offset_y + 2.0, 54.0)
    pelvis_pt = pts_radii[-1][0]
    parts.append(make_cylinder_between(pelvis_pt, hip_l, 5.0, 4.2))
    parts.append(make_cylinder_between(pelvis_pt, hip_r, 5.0, 4.2))
    parts.append(make_sphere(4.5, hip_l))
    parts.append(make_sphere(4.5, hip_r))
    
    # Arms: Shoulders -> Elbows -> Wrists -> Hands on thighs
    for sign in [-1, 1]:
        sh = FreeCAD.Vector(offset_x + sign * 16.0, offset_y - 2.0, 93.0)
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
        
        parts.append(make_cylinder_between(hip, knee, 4.0, 3.2))
        parts.append(make_sphere(3.8, knee))
        parts.append(make_cylinder_between(knee, ankle, 3.2, 2.6))
        parts.append(make_sphere(3.0, ankle))
        parts.append(make_foot(ankle, foot_y_dir=1.0))
        
    body = parts[0].fuse(parts[1:])
    return body

# ==========================================
# 4. Smooth Standing Mannequin Builder (1:10 Scale)
# ==========================================

def build_standing_figure(offset_x=0.0, offset_y=0.0):
    """
    Constructs the standing mannequin with smooth organic curves:
    - Height: ~163.4mm (1:10 scale of 1.68m adult)
    - Smooth continuous lofted anatomical torso
    - Natural sloping shoulders & contoured pelvic girdle
    - Smooth tapered cylindrical limbs with spherical joints
    """
    parts = []
    
    # Head & Neck
    head_c = FreeCAD.Vector(offset_x, offset_y, 156.0)
    parts.append(make_head(head_c))
    
    neck_base = FreeCAD.Vector(offset_x, offset_y, 136.0)
    neck_top = FreeCAD.Vector(offset_x, offset_y, 148.0)
    parts.append(make_cylinder_between(neck_base, neck_top, 2.8, 2.5))
    parts.append(make_sphere(3.0, neck_base))
    parts.append(make_sphere(3.0, neck_top))
    
    # Smooth continuous lofted torso
    pts_radii = [
        (FreeCAD.Vector(offset_x, offset_y, 134.0), 7.5),
        (FreeCAD.Vector(offset_x, offset_y, 122.0), 7.2),
        (FreeCAD.Vector(offset_x, offset_y, 110.0), 5.8),
        (FreeCAD.Vector(offset_x, offset_y, 98.0), 6.0),
        (FreeCAD.Vector(offset_x, offset_y, 88.0), 7.0)
    ]
    wires = [Part.Wire([Part.makeCircle(r, pt, FreeCAD.Vector(0, 0, 1))]) for pt, r in pts_radii]
    torso = Part.makeLoft(wires, True)
    s_top = make_sphere(7.5, pts_radii[0][0])
    s_bot = make_sphere(7.0, pts_radii[-1][0])
    parts.append(torso.fuse([s_top, s_bot]))
    
    # Natural sloping shoulders
    sh_l = FreeCAD.Vector(offset_x - 16.0, offset_y, 133.0)
    sh_r = FreeCAD.Vector(offset_x + 16.0, offset_y, 133.0)
    chest_top = pts_radii[0][0]
    parts.append(make_cylinder_between(chest_top, sh_l, 4.2, 3.5))
    parts.append(make_cylinder_between(chest_top, sh_r, 4.2, 3.5))
    parts.append(make_sphere(4.0, sh_l))
    parts.append(make_sphere(4.0, sh_r))
    
    # Natural pelvic cradle
    hip_l = FreeCAD.Vector(offset_x - 9.5, offset_y, 86.0)
    hip_r = FreeCAD.Vector(offset_x + 9.5, offset_y, 86.0)
    pelvis_pt = pts_radii[-1][0]
    parts.append(make_cylinder_between(pelvis_pt, hip_l, 5.0, 4.2))
    parts.append(make_cylinder_between(pelvis_pt, hip_r, 5.0, 4.2))
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
        
    # Legs: Hips -> Knees -> Ankles -> Feet
    for sign in [-1, 1]:
        hip = FreeCAD.Vector(offset_x + sign * 9.5, offset_y, 86.0)
        knee = FreeCAD.Vector(offset_x + sign * 9.5, offset_y, 46.0)
        ankle = FreeCAD.Vector(offset_x + sign * 9.5, offset_y, 7.0)
        
        parts.append(make_cylinder_between(hip, knee, 4.0, 3.2))
        parts.append(make_sphere(3.8, knee))
        parts.append(make_cylinder_between(knee, ankle, 3.2, 2.6))
        parts.append(make_sphere(3.0, ankle))
        parts.append(make_foot(ankle, foot_y_dir=1.0))
        
    body = parts[0].fuse(parts[1:])
    return body

# ==========================================
# 5. Multi-Plate Print Batch Layout Engine
# ==========================================

def center_prototype_xy(shape):
    """Translates shape so that its bounding box center is at (0, 0) and bottom is at Z=0."""
    bb = shape.BoundBox
    p = shape.copy()
    p.translate(FreeCAD.Vector(-bb.Center.x, -bb.Center.y, -bb.ZMin))
    return p

def create_plate1_chairs(chair_prototype):
    """Plate 1: 11x Chairs arranged with wide front-back clearance (48.6mm gap) on 256x256mm plate."""
    proto = center_prototype_xy(chair_prototype)
    items = []
    # Row 0 (4 chairs): Y = +75.0
    for x in [-78.0, -26.0, 26.0, 78.0]:
        cp = proto.copy()
        cp.translate(FreeCAD.Vector(x, 75.0, 0))
        items.append(cp)
    # Row 1 (4 chairs): Y = 0.0
    for x in [-78.0, -26.0, 26.0, 78.0]:
        cp = proto.copy()
        cp.translate(FreeCAD.Vector(x, 0.0, 0))
        items.append(cp)
    # Row 2 (3 chairs): Y = -75.0
    for x in [-52.0, 0.0, 52.0]:
        cp = proto.copy()
        cp.translate(FreeCAD.Vector(x, -75.0, 0))
        items.append(cp)
    return Part.makeCompound(items)

def create_plate2_seated(seated_prototype):
    """Plate 2: 11x Seated Persons arranged on 256x256mm build plate within safe [-122, 122]mm boundaries."""
    proto = center_prototype_xy(seated_prototype)
    items = []
    # Row 0 (4 figures): Y = +85.0
    for x in [-78.0, -26.0, 26.0, 78.0]:
        cp = proto.copy()
        cp.translate(FreeCAD.Vector(x, 85.0, 0))
        items.append(cp)
    # Row 1 (4 figures): Y = 0.0
    for x in [-78.0, -26.0, 26.0, 78.0]:
        cp = proto.copy()
        cp.translate(FreeCAD.Vector(x, 0.0, 0))
        items.append(cp)
    # Row 2 (3 figures): Y = -85.0
    for x in [-52.0, 0.0, 52.0]:
        cp = proto.copy()
        cp.translate(FreeCAD.Vector(x, -85.0, 0))
        items.append(cp)
    return Part.makeCompound(items)

def create_plate2_seated_split(seated_prototype):
    """Plate 2 Split: 2-Plate arrangement (Plate A: 6x, Plate B: 5x) with 41.0mm front-back gap."""
    proto = center_prototype_xy(seated_prototype)
    items_a = []
    for y in [58.0, -58.0]:
        for x in [-66.0, 0.0, 66.0]:
            cp = proto.copy()
            cp.translate(FreeCAD.Vector(x, y, 0))
            items_a.append(cp)
    
    items_b = []
    for x in [-66.0, 0.0, 66.0]:
        cp = proto.copy()
        cp.translate(FreeCAD.Vector(x, 58.0, 0))
        items_b.append(cp)
    for x in [-38.0, 38.0]:
        cp = proto.copy()
        cp.translate(FreeCAD.Vector(x, -58.0, 0))
        items_b.append(cp)
    return Part.makeCompound(items_a), Part.makeCompound(items_b)

def create_plate3_combined(base_prototype, standing_prototype):
    """Plate 3: 11x Base Disks + 3x Standing Persons on 256x256mm build plate."""
    items = []
    # 3 Standing Figures in back row
    stand_xs = [-60.0, 0.0, 60.0]
    for x in stand_xs:
        sp = standing_prototype.copy()
        sp.translate(FreeCAD.Vector(x, 75.0, 0))
        items.append(sp)
    
    # 11 Base Disks in 3 rows
    # Row 1 (4 disks): Y = 25.0
    for x in [-72.0, -24.0, 24.0, 72.0]:
        bp = base_prototype.copy()
        bp.translate(FreeCAD.Vector(x, 25.0, 0))
        items.append(bp)
    # Row 2 (4 disks): Y = -25.0
    for x in [-72.0, -24.0, 24.0, 72.0]:
        bp = base_prototype.copy()
        bp.translate(FreeCAD.Vector(x, -25.0, 0))
        items.append(bp)
    # Row 3 (3 disks): Y = -75.0
    for x in [-48.0, 0.0, 48.0]:
        bp = base_prototype.copy()
        bp.translate(FreeCAD.Vector(x, -75.0, 0))
        items.append(bp)
        
    return Part.makeCompound(items)

def create_plate3_bases_only(base_prototype):
    """Plate 3A (Dedicated): 11x Base Disks only (fast ~30min supportless print)."""
    items = []
    xs = [-72.0, -24.0, 24.0, 72.0]
    ys = [50.0, 0.0, -50.0]
    count = 0
    for r, y in enumerate(ys):
        for c, x in enumerate(xs):
            if count >= 11:
                break
            bp = base_prototype.copy()
            bp.translate(FreeCAD.Vector(x, y, 0))
            items.append(bp)
            count += 1
    return Part.makeCompound(items)

def create_plate4_standing_only(standing_prototype):
    """Plate 4 (Dedicated): 3x Standing Persons only."""
    items = []
    for x in [-50.0, 0.0, 50.0]:
        sp = standing_prototype.copy()
        sp.translate(FreeCAD.Vector(x, 0.0, 0))
        items.append(sp)
    return Part.makeCompound(items)

def create_plate_chair_with_seated(chair_prototype, seated_prototype):
    """Plate: 11x Chair + Seated Person Assembly centered within safe [-122.5, 122.5]mm build plate."""
    fused_proto = center_prototype_xy(chair_prototype.fuse(seated_prototype))
    items = []
    # Row 0 (4 items): Y = +85.0
    for x in [-78.0, -26.0, 26.0, 78.0]:
        cp = fused_proto.copy()
        cp.translate(FreeCAD.Vector(x, 85.0, 0))
        items.append(cp)
    # Row 1 (4 items): Y = 0.0
    for x in [-78.0, -26.0, 26.0, 78.0]:
        cp = fused_proto.copy()
        cp.translate(FreeCAD.Vector(x, 0.0, 0))
        items.append(cp)
    # Row 2 (3 items): Y = -85.0
    for x in [-52.0, 0.0, 52.0]:
        cp = fused_proto.copy()
        cp.translate(FreeCAD.Vector(x, -85.0, 0))
        items.append(cp)
    return Part.makeCompound(items)

def create_plate_chair_with_seated_rot90(chair_prototype, seated_prototype):
    """Plate: 11x Chair + Seated Person Rotated 90° for widened 18.0mm front-back (Y) row clearance on 1 plate."""
    proto_c = center_prototype_xy(chair_prototype.fuse(seated_prototype))
    proto_rot = proto_c.copy()
    proto_rot.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 90)
    items = []
    # Col 0 (left 4 items): X = -82.0
    for y in [87.0, 29.0, -29.0, -87.0]:
        cp = proto_rot.copy()
        cp.translate(FreeCAD.Vector(-82.0, y, 0))
        items.append(cp)
    # Col 1 (center 3 items with large 38mm gap): X = 0.0
    for y in [58.0, 0.0, -58.0]:
        cp = proto_rot.copy()
        cp.translate(FreeCAD.Vector(0.0, y, 0))
        items.append(cp)
    # Col 2 (right 4 items): X = +82.0
    for y in [87.0, 29.0, -29.0, -87.0]:
        cp = proto_rot.copy()
        cp.translate(FreeCAD.Vector(82.0, y, 0))
        items.append(cp)
    return Part.makeCompound(items)

def create_plate_chair_with_seated_split(chair_prototype, seated_prototype):
    """Plate Split (Recommended): 2 Plates (6x and 5x) with massive 41.0mm front-back gap for tree supports."""
    fused_proto = center_prototype_xy(chair_prototype.fuse(seated_prototype))
    
    # Plate 1 (6 items: 2 rows of 3)
    items_a = []
    for y in [58.0, -58.0]:
        for x in [-66.0, 0.0, 66.0]:
            cp = fused_proto.copy()
            cp.translate(FreeCAD.Vector(x, y, 0))
            items_a.append(cp)
            
    # Plate 2 (5 items: 2 rows of 3 and 2)
    items_b = []
    for x in [-66.0, 0.0, 66.0]:
        cp = fused_proto.copy()
        cp.translate(FreeCAD.Vector(x, 58.0, 0))
        items_b.append(cp)
    for x in [-38.0, 38.0]:
        cp = fused_proto.copy()
        cp.translate(FreeCAD.Vector(x, -58.0, 0))
        items_b.append(cp)
        
    return Part.makeCompound(items_a), Part.makeCompound(items_b)


# ==========================================
# 6. Ultra-Smooth Studio Rendering Engine
# ==========================================

def render_3d_view(shapes_with_colors, output_png, elev=18, azim=45, title="", zoom_padding=0.15, deflection=0.08):
    """Generates high-resolution shaded 3D perspective renders with smooth shading (no wireframe lines)."""
    fig = plt.figure(figsize=(10, 8), dpi=200)
    ax = fig.add_subplot(111, projection='3d')
    
    key_light = np.array([-0.5, 0.7, 0.6])
    key_light = key_light / np.linalg.norm(key_light)
    fill_light = np.array([0.6, -0.4, 0.5])
    fill_light = fill_light / np.linalg.norm(fill_light)
    
    all_points = []
    
    for shape, base_color in shapes_with_colors:
        m = MeshPart.meshFromShape(shape, LinearDeflection=deflection, AngularDeflection=0.10)
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
                intensity = 0.32 + 0.55 * dot_key + 0.18 * dot_fill
            else:
                intensity = 0.5
                
            color = np.clip(base_rgb * intensity, 0, 1)
            shaded_colors.append(color)
            
        # edgecolors=None removes facet wireframe edges for glassy smooth shading
        poly = Poly3DCollection(verts, facecolors=shaded_colors, edgecolors=None, linewidths=0, alpha=0.99)
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
    fig.patch.set_facecolor('#0b0f19')  # Deep obsidian studio background
    ax.set_facecolor('#0b0f19')
    
    if title:
        plt.title(title, color='#f8fafc', fontsize=14, pad=-15, weight='bold')
        
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', dpi=200)
    plt.close()
    print(f"  [Rendered Image] -> {output_png}", flush=True)

# ==========================================
# 7. Main Execution Pipeline
# ==========================================

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(root_dir, "models")
    plates_dir = os.path.join(models_dir, "plates")
    previews_dir = os.path.join(root_dir, "previews")
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(plates_dir, exist_ok=True)
    os.makedirs(previews_dir, exist_ok=True)
    
    print("=" * 70, flush=True)
    print("Machine Art Lab - Ultra-Smooth 3D CAD & Multi-Plate Slicer Pipeline", flush=True)
    print("=" * 70, flush=True)
    
    # 1. Build Base Prototypes
    print("\n[1/5] Building Ultra-Smooth Parametric Geometries...", flush=True)
    chair_base = build_chair_base(0, 0)
    print(f"  - Detachable Base Disk: Volume={chair_base.Volume:.1f} mm^3, Height={chair_base.BoundBox.ZLength:.1f} mm (Valid={chair_base.isValid()})", flush=True)
    
    chair = build_chair(0, 0)
    print(f"  - Smooth Chair Body: Volume={chair.Volume:.1f} mm^3, Height={chair.BoundBox.ZLength:.1f} mm (Valid={chair.isValid()})", flush=True)
    
    seated = build_seated_figure(0, 0)
    print(f"  - Smooth Seated Figure: Volume={seated.Volume:.1f} mm^3, Height={seated.BoundBox.ZLength:.1f} mm (Valid={seated.isValid()})", flush=True)
    
    standing = build_standing_figure(0, 0)
    print(f"  - Smooth Standing Figure: Volume={standing.Volume:.1f} mm^3, Height={standing.BoundBox.ZLength:.1f} mm (Valid={standing.isValid()})", flush=True)
    
    standing_side = build_standing_figure(52, 6)
    chair_seated_comp = Part.makeCompound([chair, chair_base, seated])
    comparison_scene = Part.makeCompound([chair, chair_base, seated, standing_side])
    
    # 2. Build Slicer Plate Compounds (Widened Spacing & Split Options)
    print("\n[2/5] Arranging Slicer Print Plates (256x256mm Bambu Bed)...", flush=True)
    plate1_chairs = create_plate1_chairs(chair)
    print(f"  - Plate 1 (11x Chairs, 48.6mm Y-gap): {len(plate1_chairs.Solids)} bodies arranged", flush=True)
    
    plate2_seated = create_plate2_seated(seated)
    print(f"  - Plate 2 (11x Seated Figures, Centered): {len(plate2_seated.Solids)} bodies arranged", flush=True)
    
    plate2_seated_sp1, plate2_seated_sp2 = create_plate2_seated_split(seated)
    print(f"  - Plate 2 Split (6x & 5x Seated, 41.0mm Y-gap): {len(plate2_seated_sp1.Solids)}+{len(plate2_seated_sp2.Solids)} bodies arranged", flush=True)
    
    plate3_combined = create_plate3_combined(chair_base, standing)
    print(f"  - Plate 3 (11x Bases + 3x Standing): {len(plate3_combined.Solids)} bodies arranged", flush=True)
    
    plate3_bases = create_plate3_bases_only(chair_base)
    print(f"  - Plate 3A (11x Bases Only): {len(plate3_bases.Solids)} bodies arranged", flush=True)
    
    plate4_standing = create_plate4_standing_only(standing)
    print(f"  - Plate 4 (3x Standing Only): {len(plate4_standing.Solids)} bodies arranged", flush=True)
    
    plate_chair_seated = create_plate_chair_with_seated(chair, seated)
    print(f"  - Plate Integrated (11x Chair+Seated Assemblies, Centered): {len(plate_chair_seated.Solids)} bodies arranged", flush=True)
    
    plate_chair_seated_rot90 = create_plate_chair_with_seated_rot90(chair, seated)
    print(f"  - Plate Integrated Rotated 90° (11x Assemblies, 18.0mm Y-gap): {len(plate_chair_seated_rot90.Solids)} bodies arranged", flush=True)
    
    plate_chair_seated_sp1, plate_chair_seated_sp2 = create_plate_chair_with_seated_split(chair, seated)
    print(f"  - Plate Integrated Split (6x & 5x Assemblies, 41.0mm Y-gap): {len(plate_chair_seated_sp1.Solids)}+{len(plate_chair_seated_sp2.Solids)} bodies arranged", flush=True)
    
    # 3. Export High-Resolution Individual Files (STEP, STL, 3MF)
    print("\n[3/5] Exporting High-Resolution Individual CAD/Mesh Files...", flush=True)
    single_targets = [
        ("chair", chair, 0.03, 0.05),
        ("chair_base", chair_base, 0.02, 0.04),
        ("person_seated", seated, 0.05, 0.08),
        ("person_standing", standing, 0.05, 0.08),
        ("chair_with_seated_person", chair_seated_comp, 0.05, 0.08),
        ("comparison_scene", comparison_scene, 0.06, 0.08)
    ]
    for name, shape, lin_defl, ang_defl in single_targets:
        step_p = os.path.join(models_dir, f"{name}.step")
        stl_p = os.path.join(models_dir, f"{name}.stl")
        tmf_p = os.path.join(models_dir, f"{name}.3mf")
        
        shape.exportStep(step_p)
        mesh = MeshPart.meshFromShape(shape, LinearDeflection=lin_defl, AngularDeflection=ang_defl)
        mesh.write(stl_p)
        mesh.write(tmf_p)
        print(f"  -> {name}: STEP ({os.path.getsize(step_p):,} B), STL ({mesh.CountFacets:,} facets), 3MF", flush=True)
        
    # 4. Export Arranged Plates (STEP, STL, 3MF)
    print("\n[4/5] Exporting Arranged Print Plates (Ready for Bambu Studio / OrcaSlicer)...", flush=True)
    plate_targets = [
        ("Plate1_Chairs_x11", plate1_chairs, 0.04, 0.06),
        ("Plate2_Seated_Persons_x11", plate2_seated, 0.06, 0.08),
        ("Plate2_Seated_Persons_Plate1_x6", plate2_seated_sp1, 0.06, 0.08),
        ("Plate2_Seated_Persons_Plate2_x5", plate2_seated_sp2, 0.06, 0.08),
        ("Plate3_Bases_x11_and_Standing_Persons_x3", plate3_combined, 0.05, 0.08),
        ("Plate3_Bases_x11", plate3_bases, 0.03, 0.05),
        ("Plate4_Standing_Persons_x3", plate4_standing, 0.05, 0.08),
        ("Plate_Chair_with_Seated_Person_x11", plate_chair_seated, 0.05, 0.08),
        ("Plate_Chair_with_Seated_Person_Rotated90_x11", plate_chair_seated_rot90, 0.05, 0.08),
        ("Plate_Chair_with_Seated_Person_Plate1_x6", plate_chair_seated_sp1, 0.05, 0.08),
        ("Plate_Chair_with_Seated_Person_Plate2_x5", plate_chair_seated_sp2, 0.05, 0.08)
    ]
    for name, shape, lin_defl, ang_defl in plate_targets:
        for target_dir in [models_dir, plates_dir]:
            step_p = os.path.join(target_dir, f"{name}.step")
            stl_p = os.path.join(target_dir, f"{name}.stl")
            tmf_p = os.path.join(target_dir, f"{name}.3mf")
            
            shape.exportStep(step_p)
            mesh = MeshPart.meshFromShape(shape, LinearDeflection=lin_defl, AngularDeflection=ang_defl)
            mesh.write(stl_p)
            mesh.write(tmf_p)
        print(f"  -> [PLATE] {name}: {mesh.CountFacets:,} facets ({os.path.getsize(stl_p):,} bytes)", flush=True)
        
    # 5. Generate Studio Previews & Documentation Renders
    print("\n[5/5] Generating Smooth Studio Previews & Documentation Renders...", flush=True)
    
    # 1. Chair Detail with Detachable Base
    render_3d_view(
        [(chair, '#3b82f6'), (chair_base, '#0ea5e9')],
        os.path.join(previews_dir, "preview_chair_isometric.png"),
        elev=22, azim=45,
        title="Smooth Chair & Detachable Base Assembly (Height 100mm, Base Ø36mm)"
    )
    
    # 2. Chair with Seated Figure
    render_3d_view(
        [(chair, '#3b82f6'), (chair_base, '#0ea5e9'), (seated, '#f8fafc')],
        os.path.join(previews_dir, "preview_chair_with_seated_figure.png"),
        elev=20, azim=50,
        title="Smooth Chair with Seated Mannequin Assembly"
    )
    
    # 3. Side Profile Comparison
    render_3d_view(
        [(chair, '#3b82f6'), (chair_base, '#0ea5e9'), (seated, '#f8fafc'), (standing_side, '#cbd5e1')],
        os.path.join(previews_dir, "preview_side_profile.png"),
        elev=4, azim=0,
        title="Side Profile View - Ergonomic Curves & 1:10 Anthropometry"
    )
    
    # 4. Comparative Isometric
    render_3d_view(
        [(chair, '#3b82f6'), (chair_base, '#0ea5e9'), (seated, '#f8fafc'), (standing_side, '#cbd5e1')],
        os.path.join(previews_dir, "preview_comparison_isometric.png"),
        elev=18, azim=45,
        title="1:10 Scale Comparative Study (Smooth Solids & Detachable Bases)"
    )
    
    # 5. Standing Figure Detail
    render_3d_view(
        [(standing, '#f8fafc')],
        os.path.join(previews_dir, "preview_standing_figure.png"),
        elev=10, azim=25,
        title="1:10 Scale Articulated Mannequin with Smooth Lofted Torso (163.4mm)"
    )
    
    # 6. Plate 1 Layout Preview (11x Chairs - 48.6mm Gap)
    render_3d_view(
        [(plate1_chairs, '#3b82f6')],
        os.path.join(previews_dir, "preview_plate1_chairs_x11.png"),
        elev=38, azim=45,
        title="Plate 1: 11x Chairs Batch Arrangement (48.6mm Front-Back Gap)",
        deflection=0.15
    )
    
    # 7. Plate 2 Layout Preview (11x Seated Persons)
    render_3d_view(
        [(plate2_seated, '#f8fafc')],
        os.path.join(previews_dir, "preview_plate2_seated_persons_x11.png"),
        elev=38, azim=45,
        title="Plate 2: 11x Seated Figures Batch Arrangement (256x256mm Bed)",
        deflection=0.15
    )
    
    # 8. Plate 3 Layout Preview (11x Bases + 3x Standing Persons)
    render_3d_view(
        [(plate3_bases, '#0ea5e9'), (plate4_standing, '#f8fafc')],
        os.path.join(previews_dir, "preview_plate3_combined.png"),
        elev=38, azim=45,
        title="Plate 3: 11x Detachable Bases + 3x Standing Figures (256x256mm Bed)",
        deflection=0.15
    )
    
    # 9. Plate Integrated Split Plate 1 Preview (6x Assemblies - 41.0mm Gap)
    render_3d_view(
        [(plate_chair_seated_sp1, '#3b82f6')],
        os.path.join(previews_dir, "preview_plate_chair_with_seated_split_p1.png"),
        elev=38, azim=45,
        title="Plate Split 1: 6x Chair+Seated Assemblies (41.0mm Front-Back Gap)",
        deflection=0.15
    )
    
    # 10. Plate Integrated Split Plate 2 Preview (5x Assemblies - 41.0mm Gap)
    render_3d_view(
        [(plate_chair_seated_sp2, '#3b82f6')],
        os.path.join(previews_dir, "preview_plate_chair_with_seated_split_p2.png"),
        elev=38, azim=45,
        title="Plate Split 2: 5x Chair+Seated Assemblies (41.0mm Front-Back Gap)",
        deflection=0.15
    )
    
    # 11. Plate Integrated Rotated 90° Preview (11x Assemblies - 18.0mm Gap)
    render_3d_view(
        [(plate_chair_seated_rot90, '#3b82f6')],
        os.path.join(previews_dir, "preview_plate_chair_with_seated_rot90.png"),
        elev=38, azim=45,
        title="Plate Rotated 90°: 11x Chair+Seated Assemblies (18.0mm Front-Back Gap)",
        deflection=0.15
    )
    
    # 12. Plate Integrated 11x Centered Preview
    render_3d_view(
        [(plate_chair_seated, '#3b82f6')],
        os.path.join(previews_dir, "preview_plate_chair_with_seated_person_x11.png"),
        elev=38, azim=45,
        title="Plate Integrated: 11x Chair+Seated Assemblies (Safe Bed Centered)",
        deflection=0.15
    )
    
    print("\n" + "=" * 70, flush=True)
    print("All models, plates, STL/3MF/STEP files, and studio renders successfully generated!", flush=True)
    print("=" * 70, flush=True)

if __name__ == '__main__':
    main()
