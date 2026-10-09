import os
import trimesh
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

script_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(script_dir, "비너스_15등분_교대가공")
diagram_path = os.path.join(script_dir, "venus_15_layers_diagram.png")
fig, axes = plt.subplots(3, 5, figsize=(18, 11), facecolor='#0f172a')
axes = axes.flatten()

# Unified Axis Specifications:
# LEFT AXIS:  (-26.0, 0.5)
# RIGHT AXIS: ( 21.5, 0.0)
# UNIFIED BIG HOLE: Ø30.0mm
# BOLT: M16 (Ø16.0mm)

configs = {
    1:  {'side': 'NONE',  'cx': None,  'cy': None, 'dia': 0,    'bolt': (-26.0, 0.5), 'bolt_type': 'Blind M16 (Half)'},
    2:  {'side': 'LEFT',  'cx': -26.0, 'cy': 0.5,  'dia': 30.0, 'bolt': ( 21.5, 0.0), 'bolt_type': 'Blind M16 (Half)'},
    3:  {'side': 'RIGHT', 'cx':  21.5, 'cy': 0.0,  'dia': 30.0, 'bolt': (-26.0, 0.5), 'bolt_type': 'Through M16'},
    4:  {'side': 'LEFT',  'cx': -26.0, 'cy': 0.5,  'dia': 30.0, 'bolt': ( 21.5, 0.0), 'bolt_type': 'Through M16'},
    5:  {'side': 'RIGHT', 'cx':  21.5, 'cy': 0.0,  'dia': 30.0, 'bolt': (-26.0, 0.5), 'bolt_type': 'Through M16'},
    6:  {'side': 'LEFT',  'cx': -26.0, 'cy': 0.5,  'dia': 30.0, 'bolt': ( 21.5, 0.0), 'bolt_type': 'Through M16'},
    7:  {'side': 'RIGHT', 'cx':  21.5, 'cy': 0.0,  'dia': 30.0, 'bolt': (-26.0, 0.5), 'bolt_type': 'Through M16'},
    8:  {'side': 'LEFT',  'cx': -26.0, 'cy': 0.5,  'dia': 30.0, 'bolt': ( 21.5, 0.0), 'bolt_type': 'Through M16'},
    9:  {'side': 'RIGHT', 'cx':  21.5, 'cy': 0.0,  'dia': 30.0, 'bolt': (-26.0, 0.5), 'bolt_type': 'Through M16'},
    10: {'side': 'LEFT',  'cx': -26.0, 'cy': 0.5,  'dia': 30.0, 'bolt': ( 21.5, 0.0), 'bolt_type': 'Through M16'},
    11: {'side': 'RIGHT', 'cx':  21.5, 'cy': 0.0,  'dia': 30.0, 'bolt': (-26.0, 0.5), 'bolt_type': 'Through M16'},
    12: {'side': 'LEFT',  'cx': -26.0, 'cy': 0.5,  'dia': 30.0, 'bolt': ( 21.5, 0.0), 'bolt_type': 'Through M16'},
    13: {'side': 'RIGHT', 'cx':  21.5, 'cy': 0.0,  'dia': 30.0, 'bolt': (-26.0, 0.5), 'bolt_type': 'Through M16'},
    14: {'side': 'LEFT',  'cx': -26.0, 'cy': 0.5,  'dia': 30.0, 'bolt': ( 21.5, 0.0), 'bolt_type': 'Through M16'},
    15: {'side': 'RIGHT', 'cx':  21.5, 'cy': 0.0,  'dia': 30.0, 'bolt': (-26.0, 0.5), 'bolt_type': 'Through M16'},
}

for i in range(1, 16):
    ax = axes[i-1]
    ax.set_facecolor('#1e293b')
    fp = os.path.join(out_dir, f"비너스_{i:02d}층.obj")
    tm = trimesh.load(fp, force='mesh')
    
    z_mid = (tm.bounds[0][2] + tm.bounds[1][2]) / 2.0
    sec = tm.section(plane_origin=[0, 0, z_mid], plane_normal=[0, 0, 1])
    
    if sec:
        p2d, _ = sec.to_planar()
        for poly in p2d.polygons_full:
            x, y = poly.exterior.xy
            ax.fill(x, y, color='#334155', alpha=0.9, edgecolor='#64748b', linewidth=1.2)
            for hole in poly.interiors:
                hx, hy = hole.xy
                ax.fill(hx, hy, color='#0f172a', edgecolor='#94a3b8', linewidth=0.8)
                
    ax.axvline(0, color='#64748b', linestyle='--', linewidth=0.8, alpha=0.7)
    
    cfg = configs[i]
    bx, by = cfg['bolt']
    # Draw M16 Bolt circle (Radius = 8.0mm)
    circle_bolt = plt.Circle((bx, by), 8.0, color='#22c55e', fill=False, linewidth=1.5, linestyle=':')
    ax.add_patch(circle_bolt)
    ax.plot(bx, by, marker='o', color='#22c55e', markersize=5)
    btype = cfg['bolt_type']
    ax.text(bx, by + 12, f"{btype}", color='#4ade80', fontsize=7, ha='center', va='bottom', fontweight='bold')
    
    if cfg['cx'] is not None:
        cx, cy, d = cfg['cx'], cfg['cy'], cfg['dia']
        circle = plt.Circle((cx, cy), d/2.0, color='#f59e0b', fill=False, linewidth=1.8, linestyle='-')
        ax.add_patch(circle)
        ax.plot(cx, cy, marker='x', color='#f59e0b', markersize=6)
        ax.text(cx, cy - (d/2.0 + 10), f"dia {d:.0f}mm", color='#fbbf24', fontsize=7.5, ha='center', va='top', fontweight='bold')
    else:
        ax.text(25, 0, 'No Big Hole', color='#94a3b8', fontsize=7.5, ha='center', style='italic')

    ax.set_xlim(-95, 95)
    ax.set_ylim(-115, 145)
    ax.set_aspect('equal')
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax.spines.values():
        spine.set_color('#334155')
        
    side_str = cfg['side']
    dia_val = cfg['dia']
    title_side = f"[{side_str} dia {dia_val:.0f}]" if side_str != 'NONE' else '[TOP CROWN]'
    ax.set_title(f"Layer {i:02d} {title_side}", color='#f8fafc', fontsize=9.5, fontweight='bold', pad=4)

plt.suptitle('Venus 15-Layer Architecture: Coaxial M16 Bolt & Unified Ø30mm Alignment', color='#f8fafc', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(diagram_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
print('Diagram successfully saved to:', diagram_path)
