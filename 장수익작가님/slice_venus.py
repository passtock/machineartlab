import os
import sys
import time
import trimesh

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def slice_venus_15():
    input_file = r"C:\Users\passp\Desktop\univercity\4-2\머신아트랩\장수익작가님\비너스1.obj"
    output_dir = r"C:\Users\passp\Desktop\univercity\4-2\머신아트랩\장수익작가님\비너스_15등분"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading mesh: {input_file}")
    t_start = time.time()
    mesh = trimesh.load(input_file, force="mesh", process=False)
    print(f"Loaded in {time.time() - t_start:.2f}s")
    print(f"Total Vertices: {len(mesh.vertices)}, Total Faces: {len(mesh.faces)}")

    z_min = float(mesh.bounds[0][2])
    z_max = float(mesh.bounds[1][2])
    total_height = z_max - z_min
    num_slices = 15
    dz = total_height / num_slices

    print(f"Z range: {z_min:.4f} ~ {z_max:.4f} (Total Height: {total_height:.4f} mm)")
    print(f"Slice thickness: {dz:.4f} mm per layer\n")

    current = mesh
    results = []

    for i in range(num_slices):
        t_slice = time.time()
        part_idx = i + 1
        z_low = z_min + i * dz
        z_high = z_min + (i + 1) * dz
        out_filename = f"비너스_15등분_{part_idx:02d}.obj"
        out_path = os.path.join(output_dir, out_filename)

        if i < num_slices - 1:
            part = trimesh.intersections.slice_mesh_plane(
                current,
                plane_normal=[0, 0, -1],
                plane_origin=[0, 0, z_high],
                cap=True
            )
            current = trimesh.intersections.slice_mesh_plane(
                current,
                plane_normal=[0, 0, 1],
                plane_origin=[0, 0, z_high],
                cap=True
            )
        else:
            part = current

        # Export part
        part.export(out_path)
        file_size_mb = os.path.getsize(out_path) / (1024 * 1024)
        elapsed = time.time() - t_slice

        info = {
            "part": part_idx,
            "filename": out_filename,
            "z_low": float(part.bounds[0][2]),
            "z_high": float(part.bounds[1][2]),
            "height": float(part.bounds[1][2] - part.bounds[0][2]),
            "faces": len(part.faces),
            "vertices": len(part.vertices),
            "watertight": bool(part.is_watertight),
            "size_mb": file_size_mb,
            "time_sec": elapsed
        }
        results.append(info)
        print(f"[{part_idx:02d}/15] {out_filename} saved | Z: {info['z_low']:.2f}~{info['z_high']:.2f} ({info['height']:.2f}mm) | Faces: {info['faces']} | Watertight: {info['watertight']} | Size: {file_size_mb:.2f}MB ({elapsed:.2f}s)")

    print(f"\nAll 15 parts successfully created in {time.time() - t_start:.2f}s!")
    return results

if __name__ == "__main__":
    slice_venus_15()
