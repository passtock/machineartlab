import os
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def merge_15_obj_files():
    parts_dir = r"C:\Users\passp\Desktop\univercity\4-2\머신아트랩\장수익작가님\비너스_15등분"
    output_obj = r"C:\Users\passp\Desktop\univercity\4-2\머신아트랩\장수익작가님\비너스_15등분_통합.obj"
    
    total_vertices = 0
    total_faces = 0
    v_offset = 0
    
    t0 = time.time()
    print(f"Merging 15 parts into: {output_obj}")
    
    with open(output_obj, "w", encoding="utf-8") as out_f:
        out_f.write("# Venus 15-part sliced mesh (Merged OBJ)\n")
        out_f.write("# Contains 15 separate objects (Venus_Part_01 ~ Venus_Part_15)\n\n")
        
        for i in range(1, 16):
            part_filename = f"비너스_15등분_{i:02d}.obj"
            part_path = os.path.join(parts_dir, part_filename)
            
            if not os.path.exists(part_path):
                raise FileNotFoundError(f"Missing file: {part_path}")
                
            out_f.write(f"o Venus_Part_{i:02d}\n")
            out_f.write(f"g Venus_Part_{i:02d}\n")
            
            part_verts = 0
            part_faces = 0
            
            with open(part_path, "r", encoding="utf-8") as in_f:
                for line in in_f:
                    if line.startswith("v "):
                        out_f.write(line)
                        part_verts += 1
                    elif line.startswith("f "):
                        # Parse face indices and offset by v_offset
                        tokens = line.strip().split()[1:]
                        new_tokens = []
                        for tok in tokens:
                            # Handle v, v/vt, v/vt/vn, v//vn formats if any
                            sub_tokens = tok.split("/")
                            v_idx = int(sub_tokens[0]) + v_offset
                            sub_tokens[0] = str(v_idx)
                            new_tokens.append("/".join(sub_tokens))
                        out_f.write(f"f {' '.join(new_tokens)}\n")
                        part_faces += 1
                        
            v_offset += part_verts
            total_vertices += part_verts
            total_faces += part_faces
            print(f"  - Added Part {i:02d}: {part_verts} vertices, {part_faces} faces (cumulative vertex offset: {v_offset})")
            
    file_size_mb = os.path.getsize(output_obj) / (1024 * 1024)
    print(f"\nMerge Complete in {time.time() - t0:.2f}s!")
    print(f"Total Vertices: {total_vertices}")
    print(f"Total Faces: {total_faces}")
    print(f"Output File Size: {file_size_mb:.2f} MB")
    print(f"File Path: {output_obj}")

if __name__ == "__main__":
    merge_15_obj_files()
