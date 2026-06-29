"""
Test script for main dwelling ground floor coordinate transformation
Phase 4: Test ground floor exterior walls and interior partitions only
"""

import bpy  # type: ignore
import sys
import os
import importlib

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and reload modules to get latest changes
import main_dwelling_module
importlib.reload(main_dwelling_module)

from main_dwelling_module import (
    _create_exterior_walls,
    _create_interior_partitions_ground_floor,
    _create_kitchen_bench,
    _create_dining_table,
    create_textured_material
)

# Clear scene
for obj in bpy.context.scene.objects:
    bpy.data.objects.remove(obj)

# Building parameters
ox, oy, oz = (0, 0, 0)
WIDTH = 7.0
ENCLOSED_WIDTH = 6.0
LENGTH = 9.0
GROUND_FLOOR_HEIGHT = 2.5
FIRST_FLOOR_HEIGHT = 2.4
EXTERIOR_WALL_THICKNESS = 0.20
INTERIOR_WALL_THICKNESS = 0.11
NORTH_RECESS = 1.0

# Create materials
texture_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "textures", "thermal-redwood--shou-sugi-ban--char--brushed--black-rainscreen-117-1235-mm-architextures.jpg")
potius_mat = create_textured_material("PotiusExterior", texture_path)

# Build ground floor only
print("\n=== Building Ground Floor Exterior Walls ===")
_create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat)

print("\n=== Building Ground Floor Interior Partitions ===")
_create_interior_partitions_ground_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS)

print("\n=== Building Kitchen Bench ===")
_create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)

print("\n=== Building Dining Table ===")
_create_dining_table(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)

# Set up top orthographic view
bpy.ops.object.camera_add(location=(0, 0, 20))
camera = bpy.context.active_object
camera.rotation_euler = (0, 0, 0)  # Looking straight down
bpy.context.scene.camera = camera

print("\n=== Ground Floor Test Complete ===")
print("\nVERIFICATION CHECKLIST:")
print("[ ] North wall (MD_GF_NorthWall) is on +Y side (top of screen)")
print("[ ] South wall (MD_GF_SouthWall) is on -Y side (bottom of screen)")
print("[ ] East wall (MD_GF_EastWall) is on +X side (right of screen)")
print("[ ] West wall (MD_GF_WestWall) is on -X side (left of screen)")
print("[ ] Guest bedroom is in NE corner (+X, +Y)")
print("[ ] Kitchen bench is in SW corner (-X, -Y)")
print("[ ] Dining table is between kitchen and guest bedroom")
print("[ ] Stairwell partition is east of dining table")
print("[ ] Log burner is south of guest bedroom cupboard")
print("[ ] All interior elements are INSIDE the building")
