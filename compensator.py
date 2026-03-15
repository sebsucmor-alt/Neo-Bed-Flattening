import json
import argparse
import math
import os

def cubic_interpolate(p, x):
    return p[1] + 0.5 * x * (p[2] - p[0] + x * (2.0 * p[0] - 5.0 * p[1] + 4.0 * p[2] - p[3] + x * (3.0 * (p[1] - p[2]) + p[3] - p[0])))

def bicubic_interpolate(grid, x, y):
    y_idx = int(y)
    x_idx = int(x)
    y_diff = y - y_idx
    x_diff = x - x_idx

    p = [0.0] * 4
    for j in range(4):
        row_idx = max(0, min(y_idx - 1 + j, len(grid) - 1))
        row = grid[row_idx]
        row_p = [0.0] * 4
        for i in range(4):
            col_idx = max(0, min(x_idx - 1 + i, len(row) - 1))
            row_p[i] = row[col_idx]
        p[j] = cubic_interpolate(row_p, x_diff)
    
    return cubic_interpolate(p, y_diff)

def generate_stl(vertices, indices, output_path):
    with open(output_path, 'w') as f:
        f.write("solid neo_bed_flattening\n")
        for i in range(0, len(indices), 3):
            v1 = vertices[indices[i]]
            v2 = vertices[indices[i+1]]
            v3 = vertices[indices[i+2]]

            # Normal calculation
            ax, ay, az = v2[0]-v1[0], v2[1]-v1[1], v2[2]-v1[2]
            bx, by, bz = v3[0]-v1[0], v3[1]-v1[1], v3[2]-v1[2]
            nx = ay*bz - az*by
            ny = az*bx - ax*bz
            nz = ax*by - ay*bx
            length = math.sqrt(nx*nx + ny*ny + nz*nz)
            if length == 0: length = 1.0
            
            f.write(f"  facet normal {nx/length} {ny/length} {nz/length}\n")
            f.write("    outer loop\n")
            f.write(f"      vertex {v1[0]} {v1[1]} {v1[2]}\n")
            f.write(f"      vertex {v2[0]} {v2[1]} {v2[2]}\n")
            f.write(f"      vertex {v3[0]} {v3[1]} {v3[2]}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write("endsolid neo_bed_flattening\n")

def main():
    parser = argparse.ArgumentParser(
        description='Neo-Bed-Flattening: Klipper Bed Mesh STL Generator\nSource: https://github.com/sebsucmor-alt/Neo-Bed-Flattening/',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='Klipper bed_mesh JSON file')
    parser.add_argument('--output', '-o', default='neo_bed_flattening.stl', help='Output STL file path')
    parser.add_argument('--base', '-b', type=float, default=0.5, help='Base plate thickness in mm')
    parser.add_argument('--smoothing', '-s', type=int, default=2, help='Smoothing level (upsampling)')
    parser.add_argument('--no-invert', action='store_true', help='Do not invert for compensation')
    parser.add_argument('--mirror-x', action='store_true', help='Mirror the mesh in X axis')
    parser.add_argument('--mirror-y', action='store_true', help='Mirror the mesh in Y axis')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File {args.input} not found.")
        return

    with open(args.input, 'r') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return

    points = []
    min_x, max_x, min_y, max_y = 0.0, 220.0, 0.0, 220.0

    if 'profile' in data and 'points' in data['profile']:
        points = data['profile']['points']
        if 'mesh_params' in data['profile']:
            p = data['profile']['mesh_params']
            min_x = p.get('min_x', 0)
            max_x = p.get('max_x', 220)
            min_y = p.get('min_y', 0)
            max_y = p.get('max_y', 220)
    elif 'probed_matrix' in data:
        points = data['probed_matrix']
        min_x = data.get('mesh_min', [0, 0])[0]
        min_y = data.get('mesh_min', [0, 0])[1]
        max_x = data.get('mesh_max', [220, 220])[0]
        max_y = data.get('mesh_max', [220, 220])[1]

    if not points:
        print("Error: Could not find mesh points in JSON.")
        return

    # Mirroring logic
    if args.mirror_x:
        points = [row[::-1] for row in points]
    if args.mirror_y:
        points = points[::-1]

    yr_raw = len(points)
    xr_raw = len(points[0]) if yr_raw > 0 else 0
    
    z_min = min(min(row) for row in points)
    z_max = max(max(row) for row in points)
    
    invert = not args.no_invert
    smoothing = args.smoothing
    
    x_count = (xr_raw - 1) * (smoothing + 1) + 1
    y_count = (yr_raw - 1) * (smoothing + 1) + 1
    
    vertices = []
    step_x = (max_x - min_x) / (x_count - 1)
    step_y = (max_y - min_y) / (y_count - 1)
    
    # Top surface
    for y in range(y_count):
        for x in range(x_count):
            gx = x / (smoothing + 1)
            gy = y / (smoothing + 1)
            z_val = bicubic_interpolate(points, gx, gy)
            
            thickness = (args.base + (z_max - z_val)) if invert else (args.base + z_val)
            px = min_x + x * step_x
            py = min_y + y * step_y
            vertices.append([px, py, thickness])
            
    # Bottom surface
    N = x_count * y_count
    for y in range(y_count):
        for x in range(x_count):
            px = min_x + x * step_x
            py = min_y + y * step_y
            vertices.append([px, py, 0.0])
            
    indices = []
    # Grid triangles
    for y in range(y_count - 1):
        for x in range(x_count - 1):
            v1 = y * x_count + x
            v2 = y * x_count + (x + 1)
            v3 = (y + 1) * x_count + (x + 1)
            v4 = (y + 1) * x_count + x
            
            # Top
            indices.extend([v1, v3, v2])
            indices.extend([v1, v4, v3])
            
            # Bottom
            b1, b2, b3, b4 = v1+N, v2+N, v3+N, v4+N
            indices.extend([b1, b2, b3])
            indices.extend([b1, b3, b4])
            
    # Walls
    for y in range(y_count - 1):
        t1, t2 = y * x_count, (y + 1) * x_count
        b1, b2 = t1 + N, t2 + N
        indices.extend([t1, b1, b2])
        indices.extend([t1, b2, t2])
        
        t3, t4 = t1 + (x_count - 1), t2 + (x_count - 1)
        b3, b4 = t3 + N, t4 + N
        indices.extend([t3, b4, b3])
        indices.extend([t3, t4, b4])
        
    for x in range(x_count - 1):
        t1, t2 = x, x+1
        b1, b2 = t1 + N, t2 + N
        indices.extend([t1, b2, b1])
        indices.extend([t1, t2, b2])
        
        t3, t4 = (y_count - 1) * x_count + x, (y_count - 1) * x_count + x + 1
        b3, b4 = t3 + N, t4 + N
        indices.extend([t3, b3, b4])
        indices.extend([t3, b4, t4])
        
    print(f"Generating STL: {args.output} ({len(vertices)} vertices, {len(indices)//3} facets)...")
    generate_stl(vertices, indices, args.output)
    print("Done.")

if __name__ == "__main__":
    main()
