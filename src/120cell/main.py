# pylint: disable=unused-import
# pylint: disable=undefined-variable
# pylint: disable=used-before-assignment

from itertools import combinations, product
import numpy as np
from vapory import *

# Media is not implemented when this script was written
try:
    from vapory import Media

except ImportError:
    class Media(POVRayElement):
        """Media()"""

from cell120 import VERTS, EDGES, FACES



# ---- global settings for our scene

# objects in our scene will be scaled
SCALE = 10

# edge color, edge thickness and texture of the rhombus
RHOMBUS_EDGE_COLOR = (1, 1, 1)
RHOMBUS_EDGE_THICKNESS = 0.05
DEFAULT_PENROSE_TEXTURE = Finish('ambient', 0.3, 'diffuse', 0.7, 'phong', 1)


# color, thickness, and texture of the edges 120-cell
CELL_120_EDGE_COLOR = (1, 1, 1)
CELL_120_EDGE_THICKNESS = 0.05
CELL_120_EDGE_TEXTURE = Texture('T_Chrome_4D', Pigment('color', CELL_120_EDGE_COLOR, 'transmit', 0),
                                Finish('reflection', 0.4, 'brilliance', 0.4))

# color, texture of the faces of the 120-cell
CELL_120_FACE_COLOR = 'Blue'
INTERIOR = Interior(Media('intervals', 1, 'samples', 1, 1, 'emission', 1))
CELL_120_FACE_TEXTURE = Texture(Pigment('color', CELL_120_FACE_COLOR, 'transmit', 0.7),
                                Finish('reflection', 0, 'brilliance', 0))

# A helper function for objects union
def pov_union(object_list, *args):
    return Object(Union(*object_list), *args)



# ----- settings for the Penrose tilings

# we will set these colors later
THIN_RHOMBUS_COLOR = None
FAT_RHOMBUS_COLOR = None
NUM_LINES = 15
SHIFT = np.random.random(5)
GRIDS = [np.exp(2j * np.pi * i / 5) for i in range(5)]


def rhombus(r, s, kr, ks):
    if (s - r)**2 % 5 == 1:
        color = THIN_RHOMBUS_COLOR
    else:
        color = FAT_RHOMBUS_COLOR

    point = (GRIDS[r] * (ks - SHIFT[s])
             - GRIDS[s] * (kr - SHIFT[r])) *1j / GRIDS[s-r].imag
    index = [np.ceil((point/grid).real + shift)
             for grid, shift in zip(GRIDS, SHIFT)]
    vertices = []
    for index[r], index[s] in [(kr, ks), (kr+1, ks), (kr+1, ks+1), (kr, ks+1)]:
        vertices.append(np.dot(index, GRIDS))

    vertices_real = [(z.real, z.imag) for z in vertices]
    return vertices_real, color


def tile(num_lines):
    for r, s in combinations(range(5), 2):
        for kr, ks in product(range(-num_lines, num_lines+1), repeat=2):
            yield rhombus(r, s, kr, ks)


# ----- settings for the 120-cell projection

# the pole for stereographic projection
POLE = 2

# project 4d vertices to 3d
def stereo_projection(point_4d, pole):
    x, y, z, w = point_4d
    return np.array([x, y, z]) * 4 * pole / (w - 2 * pole)

verts_3d = np.array([stereo_projection(v, POLE) for v in VERTS])
# the bottom of the 120-cell
bottom = min([v[2] for v in verts_3d])


# ----- now begin our scene

camera = Camera('location', (0, 60, -100), 'look_at', (0, 0, 110))
light1 = LightSource((50, -50, -50), 'color', (1, 1, 1))
light2 = LightSource((-50, 50, -50), 'color', (1, 1, 1))


# ----- floor -----
objects_pool = []
THIN_RHOMBUS_COLOR = (1, 0, 1)
FAT_RHOMBUS_COLOR = (0, 1, 1)

for rhombi, color in tile(NUM_LINES):
    p1, p2, p3, p4 = rhombi
    polygon = Polygon(5, p1, p2, p3, p4, p1,
                      Texture(Pigment('color', color), DEFAULT_PENROSE_TEXTURE))
    objects_pool.append(polygon)

    for p, q in zip(rhombi, [p2, p3, p4, p1]):
        cylinder = Cylinder(p, q, RHOMBUS_EDGE_THICKNESS,
                            Texture(Pigment('color', RHOMBUS_EDGE_COLOR), DEFAULT_PENROSE_TEXTURE))
        objects_pool.append(cylinder)

    for point in rhombi:
        x, y = point
        sphere = Sphere((x, y, 0), RHOMBUS_EDGE_THICKNESS,
                        Texture(Pigment('color', RHOMBUS_EDGE_COLOR), DEFAULT_PENROSE_TEXTURE))
        objects_pool.append(sphere)

floor = pov_union(objects_pool, 'rotate', (90, 0, 0), 'scale', SCALE)


# ----- left wall -----
objects_pool = []
THIN_RHOMBUS_COLOR = (0.75, 0.25, 1)
FAT_RHOMBUS_COLOR = (1, 0.25, 0.5)

for rhombi, color in tile(NUM_LINES):
    p1, p2, p3, p4 = rhombi
    polygon = Polygon(5, p1, p2, p3, p4, p1,
                      Texture(Pigment('color', color), DEFAULT_PENROSE_TEXTURE))
    objects_pool.append(polygon)

    for p, q in zip(rhombi, [p2, p3, p4, p1]):
        cylinder = Cylinder(p, q, RHOMBUS_EDGE_THICKNESS,
                            Texture(Pigment('color', RHOMBUS_EDGE_COLOR), DEFAULT_PENROSE_TEXTURE))
        objects_pool.append(cylinder)

    for point in rhombi:
        x, y = point
        sphere = Sphere((x, y, 0), RHOMBUS_EDGE_THICKNESS,
                        Texture(Pigment('color', RHOMBUS_EDGE_COLOR), DEFAULT_PENROSE_TEXTURE))
        objects_pool.append(sphere)

left = pov_union(objects_pool, 'rotate', (0, -60, 0), 'translate', (-10, 0, 10), 'scale', SCALE)


# ----- right wall -----
objects_pool = []
THIN_RHOMBUS_COLOR = (0.5, 0, 1)
FAT_RHOMBUS_COLOR = (0, 0.5, 1)

for rhombi, color in tile(NUM_LINES):
    p1, p2, p3, p4 = rhombi
    polygon = Polygon(5, p1, p2, p3, p4, p1,
                      Texture(Pigment('color', color), DEFAULT_PENROSE_TEXTURE))
    objects_pool.append(polygon)

    for p, q in zip(rhombi, [p2, p3, p4, p1]):
        cylinder = Cylinder(p, q, RHOMBUS_EDGE_THICKNESS,
                            Texture(Pigment('color', RHOMBUS_EDGE_COLOR), DEFAULT_PENROSE_TEXTURE))
        objects_pool.append(cylinder)

    for point in rhombi:
        x, y = point
        sphere = Sphere((x, y, 0), RHOMBUS_EDGE_THICKNESS,
                        Texture(Pigment('color', RHOMBUS_EDGE_COLOR), DEFAULT_PENROSE_TEXTURE))
        objects_pool.append(sphere)

right = pov_union(objects_pool, 'rotate', (0, 60, 0), 'translate', (10, 0, 10), 'scale', SCALE)


# ----- walls are finished, let's draw the 120-cell!
objects_pool = []

# firstly the vertices
for v in verts_3d:
    ball = Sphere(v, CELL_120_EDGE_THICKNESS)
    objects_pool.append(ball)

# and the edges
for i, j in EDGES:
    u, v = verts_3d[i], verts_3d[j]
    edge = Cylinder(u, v, CELL_120_EDGE_THICKNESS)
    objects_pool.append(edge)

verts_and_edges = pov_union(objects_pool, CELL_120_EDGE_TEXTURE)

# finally the faces
objects_pool = []
for f in FACES:
    pentagon_verts = [verts_3d[index] for index in f]
    pentagon = Polygon(5, *pentagon_verts)
    objects_pool.append(pentagon)

faces = pov_union(objects_pool, CELL_120_FACE_TEXTURE, INTERIOR)
cell120 = pov_union([verts_and_edges, faces], 'translate', (0, -bottom, 4), 'scale', 7)


scene = Scene(camera, objects=[light1, light2, floor, left, right, cell120],
              included=['colors.inc', 'metals.inc'])
scene.render('penrose_povray.png', width=600, height=480, antialiasing=0.001, remove_temp=False)
