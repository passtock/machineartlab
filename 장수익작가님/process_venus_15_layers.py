import os
import sys
import time
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

def process_all_layers():
    t_start = time.time()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "비너스_15등분_교대가공")
    os.makedirs(out_dir, exist_ok=True)
    
    print("=" * 70)
    print("Venus 15 Layers Generator - Genuine M8 Screw Threads (+0.15mm 3D Print Tolerance)")
    print("=" * 70)
    
    # Layer Specifications: Z bounds and Big Clearance Hole parameters
    # Even layers (2, 4, 6, 8, 10, 12, 14): Big hole on LEFT (-26.0, 0.6) | Bolt on RIGHT (21.7, -0.05)
    # Odd layers (3, 5, 7, 9, 11, 13, 15): Big hole on RIGHT (21.5, 0.1)  | Bolt on LEFT (-26.0, 0.5)
    # Special Layer 1: No big hole, blind bolt on LEFT bored halfway from bottom (Z <= 221.5mm)
    # Special Layer 2: Big hole on LEFT (Ø23.5mm), blind bolt on RIGHT bored halfway from bottom (Z <= 198.15mm)
    layer_configs = {
        1:  {"z": (213.014, 230.150), "side": None,    "cx":   0.0, "cy": 0.0, "dia":  0.0},
        2:  {"z": (190.150, 206.238), "side": "LEFT",  "cx": -26.0, "cy": 0.6, "dia": 23.5},
        3:  {"z": (165.708, 182.780), "side": "RIGHT", "cx":  21.5, "cy": 0.1, "dia": 70.0},
        4:  {"z": (142.326, 158.417), "side": "LEFT",  "cx": -26.0, "cy": 0.6, "dia": 70.0},
        5:  {"z": (122.311, 139.383), "side": "RIGHT", "cx":  21.5, "cy": 0.1, "dia": 70.0},
        6:  {"z": ( 94.503, 110.591), "side": "LEFT",  "cx": -26.0, "cy": 0.6, "dia": 70.0},
        7:  {"z": ( 71.562,  88.634), "side": "RIGHT", "cx":  21.5, "cy": 0.1, "dia": 50.0},
        8:  {"z": ( 46.680,  62.775), "side": "LEFT",  "cx": -26.0, "cy": 0.6, "dia": 70.0},
        9:  {"z": ( 20.813,  37.885), "side": "RIGHT", "cx":  21.5, "cy": 0.1, "dia": 60.0},
        10: {"z": ( -1.144,  14.944), "side": "LEFT",  "cx": -26.0, "cy": 0.6, "dia": 53.0},
        11: {"z": (-29.935, -12.863), "side": "RIGHT", "cx":  21.5, "cy": 0.1, "dia": 43.0},
        12: {"z": (-48.967, -32.879), "side": "LEFT",  "cx": -26.0, "cy": 0.6, "dia": 44.0},
        13: {"z": (-73.722, -56.650), "side": "RIGHT", "cx":  21.5, "cy": 0.1, "dia": 51.0},
        14: {"z": (-96.790, -80.702), "side": "LEFT",  "cx": -26.0, "cy": 0.6, "dia": 31.0},
        15: {"z": (-121.539,-104.467), "side": "RIGHT", "cx":  21.5, "cy": 0.1, "dia": 58.0},
    }

    # Load Master Meshes (1.obj, 2.obj, 볼트.obj)
    print("[1/3] Loading Master Meshes (1.obj, 2.obj, 볼트.obj)...")
    t_load = time.time()
    tm1 = trimesh.load(os.path.join(script_dir, "1.obj"), force="mesh")
    m1_master = Manifold(Mesh(vert_properties=np.ascontiguousarray(tm1.vertices, dtype=np.float32), 
                             tri_verts=np.ascontiguousarray(tm1.faces, dtype=np.uint32)))

    tm2 = trimesh.load(os.path.join(script_dir, "2.obj"), force="mesh")
    m2_master = Manifold(Mesh(vert_properties=np.ascontiguousarray(tm2.vertices, dtype=np.float32), 
                             tri_verts=np.ascontiguousarray(tm2.faces, dtype=np.uint32)))

    # Load Bolt and apply +0.15mm radial tolerance (FDM clearance)
    bolt = trimesh.load(os.path.join(script_dir, "볼트.obj"), force="mesh")
    cx0, cy0 = -18.896184, 0.0
    v_bolt = bolt.vertices.copy()
    dx = v_bolt[:,0] - cx0
    dy = v_bolt[:,1] - cy0
    r = np.hypot(dx, dy)
    delta_r = 0.15
    v_bolt[:,0] += (dx / r) * delta_r
    v_bolt[:,1] += (dy / r) * delta_r

    # Left Thread Cutter: X = -26.0, Y = +0.5
    v_left = v_bolt.copy()
    v_left[:,0] += (-26.0 - cx0)
    v_left[:,1] += (0.5 - cy0)
    m_bolt_left = Manifold(Mesh(vert_properties=np.ascontiguousarray(v_left, dtype=np.float32), 
                                tri_verts=np.ascontiguousarray(bolt.faces, dtype=np.uint32)))

    # Right Thread Cutter: X = +21.7, Y = -0.05
    v_right = v_bolt.copy()
    v_right[:,0] += (21.7 - cx0)
    v_right[:,1] += (-0.05 - cy0)
    m_bolt_right = Manifold(Mesh(vert_properties=np.ascontiguousarray(v_right, dtype=np.float32), 
                                 tri_verts=np.ascontiguousarray(bolt.faces, dtype=np.uint32)))

    print(f"      Master meshes & thread cutters loaded successfully in {time.time()-t_load:.2f}s.")
    print("[2/3] Processing 15 layers with genuine M8 threads & big clearance holes...")

    layer_meshes = []

    for i in range(1, 16):
        t_layer = time.time()
        cfg = layer_configs[i]
        z_min, z_max = cfg["z"]
        layer_h = z_max - z_min
        
        box_layer = Manifold.cube([400, 400, layer_h + 0.1]).translate([-200, -200, z_min])
        l_left = m1_master ^ box_layer
        l_right = m2_master ^ box_layer
        
        out_bodies = []
        
        if i == 1:
            # Layer 1: Skull Top Crown
            # No big hole.
            # Blind bolt on Left bored halfway from bottom (Z in [213.014, 221.5]).
            # Top half (Z > 221.5) remains 100% solid inside the skull (ZERO protrusion).
            trim_box = Manifold.cube([60, 60, 221.5 - (z_min - 10.0)]).translate([-56, -30, z_min - 10.0])
            blind_cutter = m_bolt_left ^ trim_box
            l1_left_threaded = l_left - blind_cutter
            
            out_bodies.append(l1_left_threaded)
            out_bodies.append(l_right)
            
        elif i == 2:
            # Layer 2: Big hole on LEFT (Ø23.5mm). Blind bolt on RIGHT (halfway).
            r_big = cfg["dia"] / 2.0
            big_hole = Manifold.cylinder(height=layer_h + 10.0, radius_low=r_big, radius_high=r_big, circular_segments=64)
            big_hole = big_hole.translate([cfg["cx"], cfg["cy"], z_min - 5.0])
            l2_left_cut = l_left - big_hole
            
            # Blind bolt on RIGHT bored halfway from bottom (Z from 190.15 up to 198.15)
            trim_box = Manifold.cube([60, 60, 198.15 - (z_min - 10.0)]).translate([0, -30, z_min - 10.0])
            blind_cutter = m_bolt_right ^ trim_box
            l2_right_threaded = l_right - blind_cutter
            
            out_bodies.append(l2_left_cut)
            out_bodies.append(l2_right_threaded)
            
        else:
            # Layers 3 ~ 15:
            if i % 2 == 1:
                # Odd layer: LEFT is M8 thread through-hole, RIGHT is Big Hole
                l_left_threaded = l_left - m_bolt_left
                r_big = cfg["dia"] / 2.0
                big_hole = Manifold.cylinder(height=layer_h + 10.0, radius_low=r_big, radius_high=r_big, circular_segments=64)
                big_hole = big_hole.translate([cfg["cx"], cfg["cy"], z_min - 5.0])
                l_right_cut = l_right - big_hole
                
                out_bodies.append(l_left_threaded)
                out_bodies.append(l_right_cut)
            else:
                # Even layer: LEFT is Big Hole, RIGHT is M8 thread through-hole
                r_big = cfg["dia"] / 2.0
                big_hole = Manifold.cylinder(height=layer_h + 10.0, radius_low=r_big, radius_high=r_big, circular_segments=64)
                big_hole = big_hole.translate([cfg["cx"], cfg["cy"], z_min - 5.0])
                l_left_cut = l_left - big_hole
                l_right_threaded = l_right - m_bolt_right
                
                out_bodies.append(l_left_cut)
                out_bodies.append(l_right_threaded)
                
        # Merge bodies for this layer into final watertight manifold
        layer_manifold = out_bodies[0] + out_bodies[1]
        out_mesh_data = layer_manifold.to_mesh()
        combined_mesh = trimesh.Trimesh(vertices=out_mesh_data.vert_properties, 
                                        faces=out_mesh_data.tri_verts, 
                                        process=False)
        layer_meshes.append(combined_mesh)
        
        # Save output OBJ & STL
        out_name_obj = f"비너스_{i:02d}층.obj"
        out_name_stl = f"비너스_{i:02d}층.stl"
        out_path_obj = os.path.join(out_dir, out_name_obj)
        out_path_stl = os.path.join(out_dir, out_name_stl)
        
        combined_mesh.export(out_path_obj)
        combined_mesh.export(out_path_stl)
        
        elapsed = time.time() - t_layer
        file_size_mb = os.path.getsize(out_path_obj) / (1024 * 1024)
        
        side_desc = f"{cfg['side']} Ø{cfg['dia']:.1f}mm" if cfg['side'] else "NO Big Hole"
        bolt_desc = "Blind (half)" if i in [1, 2] else "Through M8"
        print(f"[{i:02d}/15] {out_name_obj:14s} | Big Hole: {side_desc:16s} | Bolt: {bolt_desc:14s} | Faces: {len(combined_mesh.faces):6d} | Size: {file_size_mb:.2f}MB ({elapsed:.2f}s)")
        
    # Generate Integrated Assembly and Exploded Views
    print("\n[3/3] Generating Integrated Assembly & 10mm Exploded View...")
    merged_mesh = trimesh.util.concatenate(layer_meshes)
    merged_mesh.export(os.path.join(out_dir, "비너스_15등분_전체조립_통합.obj"))
    merged_mesh.export(os.path.join(out_dir, "비너스_15등분_전체조립_통합.stl"))
    
    exploded_parts = []
    for idx, lm in enumerate(layer_meshes):
        cp = lm.copy()
        cp.apply_translation([0, 0, (15 - (idx + 1)) * 10.0])
        exploded_parts.append(cp)
    exploded_mesh = trimesh.util.concatenate(exploded_parts)
    exploded_mesh.export(os.path.join(out_dir, "비너스_15등분_간격전개_10mm.obj"))
    exploded_mesh.export(os.path.join(out_dir, "비너스_15등분_간격전개_10mm.stl"))
    
    print("\n" + "=" * 70)
    print(f"All 15 layers & assemblies generated successfully in {time.time() - t_start:.2f}s!")
    print(f"Output directory: {os.path.abspath(out_dir)}")
    print("=" * 70)

if __name__ == "__main__":
    process_all_layers()
