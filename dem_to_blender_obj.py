import rasterio
import numpy as np
import trimesh
from pyproj import Transformer
from PIL import Image

# -----------------------------
# USER SETTINGS
# -----------------------------
tif_path = "Terrain/BR25.tif"
img_path = "Terrain/LINZ_Aerial.tif"
obj_path = "Terrain/terrain.obj"

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
# DEBUG INFO
# -----------------------------
dem_left, dem_bottom, dem_right, dem_top = src.bounds

print("\n===== DEM INFO =====")
print(f"DEM CRS: {src.crs}")
print(f"DEM size (pixels): {src.width} x {src.height}")
print(f"DEM bounds:")
print(f"  Left   = {dem_left:.2f}")
print(f"  Right  = {dem_right:.2f}")
print(f"  Bottom = {dem_bottom:.2f}")
print(f"  Top    = {dem_top:.2f}")

print("\n===== IMAGERY INFO =====")
print(f"Image CRS: {img_src.crs}")
print(f"Image size (pixels): {img_src.width} x {img_src.height}")
print(f"Image bounds:")
print(f"  Left   = {img_left:.2f}")
print(f"  Right  = {img_right:.2f}")
print(f"  Bottom = {img_bottom:.2f}")
print(f"  Top    = {img_top:.2f}")

print("\n===== DWELLING LOCATION =====")
print(f"Lat/Lon: ({lat}, {lon})")
print(f"DEM coordinates: X={x0:.2f}, Y={y0:.2f}")

# Distance from dwelling to DEM edges
dist_west = x0 - dem_left
dist_east = dem_right - x0
dist_south = y0 - dem_bottom
dist_north = dem_top - y0

print("\n===== DISTANCE TO DEM EDGES =====")
print(f"West:  {dist_west:.1f} m")
print(f"East:  {dist_east:.1f} m")
print(f"South: {dist_south:.1f} m")
print(f"North: {dist_north:.1f} m")

# Largest centred square possible
max_half_size = min(
    dist_west,
    dist_east,
    dist_south,
    dist_north
)

print("\n===== MAXIMUM CENTRED TERRAIN =====")
print(f"Maximum half-size around dwelling: {max_half_size:.1f} m")
print(f"Maximum square area: {max_half_size*2:.1f} m × {max_half_size*2:.1f} m")


# -----------------------------
# SAMPLE GRID AROUND ORIGIN
# -----------------------------
half_size = 730  # 2000m total area

# Build clean geographic coordinate ranges
xs = np.arange(x0 - half_size, x0 + half_size, step)
ys = np.arange(y0 - half_size, y0 + half_size, step)

w = len(xs)
h = len(ys)

# Find origin elevation
origin_z = next(src.sample([(x0, y0)]))[0]

verts = []
uvs = []

# OBJ import in Blender defaults to Y-up with forward on -Z, which flips one
# horizontal axis during conversion. Export with inverted local_y in OBJ Z to
# keep project coordinates visually correct after default import.
# X = East/West, Y = elevation, Z = -North/South (for Blender OBJ default axes)
for y in ys:
    for x in xs:
        z = next(src.sample([(x, y)]))[0]
        
        local_x = x - x0
        local_y = y - y0
        local_z = z - origin_z
        
        verts.append([local_x, local_z, -local_y])
        
        # Normalized UV coordinates
        u = (x - img_left) / img_width_m
        v = (y - img_bottom) / img_height_m
        uvs.append([u, v])

verts = np.array(verts)
uvs = np.array(uvs)

# -----------------------------
# BUILD MESH FACES (counter-clockwise winding -> upward normals)
# -----------------------------
faces = []
for y in range(h - 1):
    for x in range(w - 1):
        i = y * w + x

        # i       = (x, y)
        # i+1     = (x+1, y)
        # i+w     = (x, y+1)
        # i+w+1   = (x+1, y+1)
        faces.append([i, i + 1, i + w])
        faces.append([i + 1, i + w + 1, i + w])

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
mesh.export(obj_path)
print("Done: Terrain exported for Blender OBJ defaults (flat orientation, correct side mapping).")