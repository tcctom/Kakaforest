import rasterio
import numpy as np
import trimesh
from pyproj import Transformer
from PIL import Image

# -----------------------------
# USER SETTINGS
# -----------------------------
tif_path = "BR25.tif"
img_path = "LINZ/LINZ_Aerial.tif"

# your dwelling coordinate
lat = -41.783213855839
lon = 172.92023483494785

# mesh resolution (increase for smoother terrain)
step = 2  # meters between sampled points

# -----------------------------
# OPEN DEM & IMAGERY
# -----------------------------
src = rasterio.open(tif_path)
img_src = rasterio.open(img_path)

img_left, img_bottom, img_right, img_top = img_src.bounds
img_width_m = img_right - img_left
img_height_m = img_top - img_bottom

# transform lat/lon → DEM CRS
transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
x0, y0 = transformer.transform(lon, lat)

# -----------------------------
# SAMPLE GRID AROUND ORIGIN
# -----------------------------
half_size = 150  # 300m total area

# Build clean geographic coordinate ranges
xs = np.arange(x0 - half_size, x0 + half_size, step)
ys = np.arange(y0 - half_size, y0 + half_size, step)

w = len(xs)
h = len(ys)

# Find origin elevation
origin_z = next(src.sample([(x0, y0)]))[0]

verts = []
uvs = []

# Map coordinates to a flat grid array sequentially
for y in ys:
    for x in xs:
        z = next(src.sample([(x, y)]))[0]
        
        local_x = x - x0
        local_y = y - y0
        local_z = z - origin_z
        
        # Map to Trimesh: [X=Horizontal, Y=Vertical Elevation, Z=Depth]
        verts.append([local_x, local_z, local_y])
        
        # Normalized UV coordinates
        u = (x - img_left) / img_width_m
        v = (y - img_bottom) / img_height_m
        uvs.append([u, v])

verts = np.array(verts)
uvs = np.array(uvs)

# -----------------------------
# BUILD MESH FACES (Flipped Winding Order)
# -----------------------------
faces = []
for y in range(h - 1):
    for x in range(w - 1):
        i = y * w + x
        
        # CRITICAL FIX: We reversed the order of vertex connections 
        # (e.g., [i, i+w, i+1] instead of [i, i+1, i+w]).
        # This flips the terrain geometry right-side up when viewed from above.
        faces.append([i, i + w, i + 1])
        faces.append([i + 1, i + w, i + w + 1])

faces = np.array(faces)

# -----------------------------
# CREATE MATERIAL & MESH
# -----------------------------
texture_img = Image.open(img_path)
material = trimesh.visual.material.SimpleMaterial(image=texture_img)
visuals = trimesh.visual.TextureVisuals(uv=uvs, material=material)

mesh = trimesh.Trimesh(vertices=verts, faces=faces, visual=visuals)

# -----------------------------
# EXPORT NATIVE OBJ
# -----------------------------
mesh.export("terrain.obj")
print("Done: Terrain geometry flipped right-side up and successfully exported!")