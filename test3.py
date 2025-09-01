import gdspy
import numpy as np
import json
import cairosvg

# === Parameters ===
clip_size = 3               # Size of each clip (microns)
cd = 0.09                   # Contact dimension
pitch = 0.18                # Distance between contact centers
num_clips = 10              # ✅ Reduced to 10 for fast preview
shapes = ['square', 'octagon', 'hexagon']
layer = 1                   # Contact layer
boundary_layer = layer + 1  # Clip boundary layer
num_contacts = int(clip_size // pitch)

# Seed for reproducibility
np.random.seed(42)

# Create GDS library
lib = gdspy.GdsLibrary()
top_cell = lib.new_cell('TOP')

# Contact shape generator
def create_contact(center, cd, shape='square'):
    x, y = center
    if shape == 'square':
        return gdspy.Rectangle((x - cd / 2, y - cd / 2), (x + cd / 2, y + cd / 2), layer=layer)
    elif shape == 'octagon':
        return gdspy.Round((x, y), cd / 2, number_of_points=8, inner_radius=0, layer=layer)
    elif shape == 'hexagon':
        return gdspy.Round((x, y), cd / 2, number_of_points=6, inner_radius=0, layer=layer)
    else:
        raise ValueError(f"Unsupported shape: {shape}")

# === JSON hierarchy storage ===
hierarchy = {}

# === Generate 10 clips ===
for i in range(num_clips):
    cell_name = f'CLIP_{i}'
    cell = lib.new_cell(cell_name)

    # Random offset and shape
    h_offset = np.random.uniform(-pitch / 2, pitch / 2)
    v_offset = np.random.uniform(-pitch / 2, pitch / 2)
    shape = np.random.choice(shapes)

    hierarchy[cell_name] = {
        'polygons': [],
        'references': [],
        'shape': shape
    }

    # Add contacts
    for row in range(num_contacts):
        for col in range(num_contacts):
            x = (col + 0.5) * pitch + h_offset
            y = (row + 0.5) * pitch + v_offset
            if 0 < x < clip_size and 0 < y < clip_size:
                contact = create_contact((x, y), cd, shape)
                cell.add(contact)
                hierarchy[cell_name]['polygons'].append({
                    'type': shape,
                    'layer': layer,
                    'center': [round(x, 4), round(y, 4)]
                })

    # Add clip boundary
    boundary = gdspy.Rectangle((0, 0), (clip_size, clip_size), layer=boundary_layer)
    cell.add(boundary)
    hierarchy[cell_name]['polygons'].append({
        'type': 'boundary',
        'layer': boundary_layer,
        'points': [[0, 0], [clip_size, 0], [clip_size, clip_size], [0, clip_size]]
    })

    # Place clips in grid (5 per row)
    clips_per_row = 5
    dx = (i % clips_per_row) * (clip_size + 1)
    dy = (i // clips_per_row) * (clip_size + 1)
    ref = gdspy.CellReference(cell, origin=(dx, dy))
    top_cell.add(ref)

    # Reference info in hierarchy
    hierarchy['TOP'] = hierarchy.get('TOP', {'polygons': [], 'references': []})
    hierarchy['TOP']['references'].append({
        'ref_cell': cell_name,
        'origin': [dx, dy],
        'rotation': 0,
        'magnification': 1
    })

# === Export GDS ===
lib.write_gds('test_small.gds')
print("✅ GDS file 'test_small.gds' created.")

# === Export SVG ===
top_cell.write_svg('layout_small.svg')
print("✅ SVG file 'layout_small.svg' created.")

# === Export JSON Hierarchy Report ===
with open('hierarchy_small.json', 'w') as f:
    json.dump(hierarchy, f, indent=2)
print("✅ JSON hierarchy report written to 'hierarchy_small.json'.")

# === Convert SVG → PNG + PDF ===
cairosvg.svg2png(url='layout_small.svg', write_to='layout_small.png', scale=1.0)
print("✅ PNG exported as 'layout_small.png'.")

cairosvg.svg2pdf(url='layout_small.svg', write_to='layout_small.pdf')
print("✅ PDF exported as 'layout_small.pdf'.")
