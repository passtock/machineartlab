import os
import sys
import time

def parse_obj(filepath):
    """Fast OBJ parser for vertices and faces."""
    vertices = []
    faces = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.strip().split()
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith("f "):
                tokens = line.strip().split()[1:]
                sub_indices = []
                for tok in tokens:
                    sub_indices.append(tok.split("/")[0])
                faces.append([int(idx) for idx in sub_indices])
    return vertices, faces

def create_z_spaced_obj(parts_dir, output_path, gap_z=20.0):
    """
    Creates an exploded view OBJ where each successive layer is offset by gap_z along Z.
    Also shifts Part 01's base to Z=0.
    """
    print(f"\n[1] Creating Z-Spaced Exploded View (gap={gap_z}mm)...")
    t0 = time.time()
    
    total_verts = 0
    total_faces = 0
    v_offset = 0
    
    # First determine Z_min of part 1 to ground the base at Z=0
    part1_verts, _ = parse_obj(os.path.join(parts_dir, "비너스_15등분_01.obj"))
    z_base = min(v[2] for v in part1_verts)
    
    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write(f"# Venus 15-part sliced mesh - Z-axis Exploded View (Gap: {gap_z}mm)\n")
        out_f.write(f"# Base grounded at Z=0\n\n")
        
        for i in range(1, 16):
            filename = f"비너스_15등분_{i:02d}.obj"
            filepath = os.path.join(parts_dir, filename)
            verts, faces = parse_obj(filepath)
            
            # Additional Z shift for this layer
            shift_z = -z_base + (i - 1) * gap_z
            
            out_f.write(f"o Venus_Part_{i:02d}\n")
            out_f.write(f"g Venus_Part_{i:02d}\n")
            
            for vx, vy, vz in verts:
                out_f.write(f"v {vx:.6f} {vy:.6f} {vz + shift_z:.6f}\n")
                
            for face in faces:
                shifted_face = [str(idx + v_offset) for idx in face]
                out_f.write(f"f {' '.join(shifted_face)}\n")
                
            v_offset += len(verts)
            total_verts += len(verts)
            total_faces += len(faces)
            
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  -> Saved: {output_path} ({size_mb:.2f} MB, {total_verts} verts, {total_faces} faces in {time.time() - t0:.2f}s)")

def create_grid_spaced_obj(parts_dir, output_path, cols=5, padding=30.0):
    """
    Creates a flat grid arrangement on the XY plane (all parts grounded at Z=0).
    Arranged in 'cols' columns (e.g. 5 cols x 3 rows).
    """
    print(f"\n[2] Creating XY Ground Grid Arrangement ({cols} columns, padding={padding}mm)...")
    t0 = time.time()
    
    # Load all parts and calculate each part's bounding box and center
    parts_data = []
    max_w = 0.0
    max_d = 0.0
    
    for i in range(1, 16):
        filename = f"비너스_15등분_{i:02d}.obj"
        filepath = os.path.join(parts_dir, filename)
        verts, faces = parse_obj(filepath)
        
        xs = [v[0] for v in verts]
        ys = [v[1] for v in verts]
        zs = [v[2] for v in verts]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        
        cx = (min_x + max_x) / 2.0
        cy = (min_y + max_y) / 2.0
        
        w = max_x - min_x
        d = max_y - min_y
        
        if w > max_w: max_w = w
        if d > max_d: max_d = d
        
        parts_data.append({
            "idx": i,
            "verts": verts,
            "faces": faces,
            "cx": cx, "cy": cy, "min_z": min_z,
            "w": w, "d": d
        })
        
    cell_w = max_w + padding
    cell_d = max_d + padding
    
    total_verts = 0
    total_faces = 0
    v_offset = 0
    
    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write(f"# Venus 15-part sliced mesh - Flat Grid Arrangement ({cols} cols, padding: {padding}mm)\n")
        out_f.write(f"# All parts grounded at Z=0\n\n")
        
        for data in parts_data:
            i = data["idx"]
            col = (i - 1) % cols
            row = (i - 1) // cols
            
            # Target center for this cell
            target_cx = col * cell_w
            target_cy = -row * cell_d  # negative Y so rows go downward
            
            dx = target_cx - data["cx"]
            dy = target_cy - data["cy"]
            dz = -data["min_z"]  # ground bottom to Z=0
            
            out_f.write(f"o Venus_Part_{i:02d}\n")
            out_f.write(f"g Venus_Part_{i:02d}\n")
            
            for vx, vy, vz in data["verts"]:
                out_f.write(f"v {vx + dx:.6f} {vy + dy:.6f} {vz + dz:.6f}\n")
                
            for face in data["faces"]:
                shifted_face = [str(idx + v_offset) for idx in face]
                out_f.write(f"f {' '.join(shifted_face)}\n")
                
            v_offset += len(data["verts"])
            total_verts += len(data["verts"])
            total_faces += len(data["faces"])
            
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  -> Saved: {output_path} ({size_mb:.2f} MB, {total_verts} verts, {total_faces} faces in {time.time() - t0:.2f}s)")

if __name__ == "__main__":
    base_dir = r"C:\Users\passp\Desktop\univercity\4-2\머신아트랩\장수익작가님"
    parts_dir = os.path.join(base_dir, "비너스_15등분")
    
    # 1. Z-axis exploded with 20mm gap
    out_z20 = os.path.join(base_dir, "비너스_15등분_간격정렬_Z축_20mm.obj")
    create_z_spaced_obj(parts_dir, out_z20, gap_z=20.0)
    
    # 2. Z-axis exploded with 10mm gap (more compact)
    out_z10 = os.path.join(base_dir, "비너스_15등분_간격정렬_Z축_10mm.obj")
    create_z_spaced_obj(parts_dir, out_z10, gap_z=10.0)
    
    # 3. Flat XY grid arrangement (5x3)
    out_grid = os.path.join(base_dir, "비너스_15등분_간격정렬_평면그리드.obj")
    create_grid_spaced_obj(parts_dir, out_grid, cols=5, padding=30.0)
    
    print("\nAll alignment files successfully created!")
