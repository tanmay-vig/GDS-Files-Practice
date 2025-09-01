import gdspy
import numpy as np

#parameters
clip_size = 3
cd = 0.09
pitch = 0.18
num_clips = 1000
shapes = ['square', 'octagon', 'hexagon']
layer = 1

num_contacts = int(clip_size // pitch)

np.random.seed(42)  

lib=gdspy.GdsLibrary()


def create_contact(center, cd , shape = 'square'):
    x,y = center
    if shape == 'square':
        return gdspy.Rectangle((x - cd/2, y - cd/2), (x + cd/2, y + cd/2), layer=layer)
    elif shape == 'octagon':
        return gdspy.Round((x,y), cd/2, number_of_points=8, inner_radius=0, layer=layer)
    elif shape == 'hexagon':
        return gdspy.Round((x,y), cd/2, number_of_points=6, inner_radius=0, layer=layer)
    else:
        raise ValueError("Unsupported shape: {}".format(shape)) 
    
for i in range(num_clips):
    cell = lib.new_cell(f'CLIP_{i}')
    h_offset = np.random.uniform(-pitch/2, pitch/2)
    v_offset = np.random.uniform(-pitch/2, pitch/2)
    shape = np.random.choice(shapes)

    for row in range(num_contacts):
        for col in range(num_contacts):
            x = (col + 0.5) * pitch + h_offset
            y = (row + 0.5) * pitch + v_offset
            if 0 < x < clip_size and 0 < y < clip_size:
                contact = create_contact((x, y), cd, shape)
                cell.add(contact) 
    
    cell.add(gdspy.Rectangle((0, 0), (clip_size, clip_size), layer=layer+1))

lib.write_gds('test.gds')
print("GDS file 'test.gds' created with 1000 clips.")