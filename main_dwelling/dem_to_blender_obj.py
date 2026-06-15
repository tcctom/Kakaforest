import rasterio
import numpy as np
import trimesh
from pyproj import Transformer

# -----------------------------
# USER SETTINGS
# -----------------------------
tif_path = "BR25.tif"

# your dwelling coordinate
lat = -41.783213855839
lon = 172.92023483494785

# mesh resolution (increase for smoother terrain)
step = 2  # meters between sampled points

# -----------------------------
# OPEN DEM
# -----------------------------
src = rasterio.open(tif_path)

# transform lat/lon → DEM CRS
transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
x0, y0 = transformer.transform(lon, lat)

# -----------------------------
# SAMPLE GRID AROUND ORIGIN
# -----------------------------
half_size = 150  # 300m total area

xs = np.arange(x0 - half_size, x0 + half_size, step)
ys = np.arange(y0 - half_size, y0 + half_size, step)

vertices = []
faces = []

z_values = []

# read elevation via sampling
for yi, y in enumerate(ys):
    row = []
    for xi, x in enumerate(xs):
        z = next(src.sample([(x, y)]))[0]
        row.append([x, y, z])
    vertices.append(row)

vertices = np.array(vertices)

# -----------------------------
# SHIFT TO LOCAL SPACE
# -----------------------------
# make dwelling = origin
origin_z = next(src.sample([(x0, y0)]))[0]

verts = []
for row in vertices:
    for v in row:
        x = v[0] - x0
        y = v[1] - y0
        z = v[2] - origin_z
        verts.append([x, z, y])  # Blender axis swap

verts = np.array(verts)

# -----------------------------
# BUILD MESH FACES
# -----------------------------
w = len(xs)
h = len(ys)

for y in range(h - 1):
    for x in range(w - 1):
        i = y * w + x
        faces.append([i, i + 1, i + w])
        faces.append([i + 1, i + w + 1, i + w])

mesh = trimesh.Trimesh(vertices=verts, faces=faces)

# -----------------------------
# EXPORT
# -----------------------------
mesh.export("terrain.obj")

print("Done: terrain.obj generated")