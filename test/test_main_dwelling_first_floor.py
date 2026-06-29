"""
Test script for main dwelling first floor coordinate transformation
Phase 5: Test first floor walls, partitions, ensuite, and windows
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
    _create_interior_partitions_first_floor,
    _furnish_master_ensuite,
    _add_exterior_windows_and_doors,
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

# Build both floors exterior walls to see full structure
print("\n=== Building Exterior Walls (Both Floors) ===")
_create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat)

print("\n=== Building First Floor Interior Partitions ===")
_create_interior_partitions_first_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS)

print("\n=== Furnishing Master Ensuite ===")
_furnish_master_ensuite(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS)

print("\n=== Adding Exterior Windows and Doors ===")
_add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS)

# Set up view at first floor level
bpy.ops.object.camera_add(location=(0, 0, 20))
camera = bpy.context.active_object
camera.rotation_euler = (0, 0, 0)  # Looking straight down
bpy.context.scene.camera = camera

print("\n=== First Floor Test Complete ===")
print("\nVERIFICATION CHECKLIST:")
print("[ ] North wall (MD_FF_NorthWall) is on +Y side (top of screen)")
print("[ ] South wall (MD_FF_SouthWall) is on -Y side (bottom of screen)")
print("[ ] East wall (MD_FF_EastWall) is on +X side (right of screen)")
print("[ ] West wall (MD_FF_WestWall) is on -X side (left of screen)")
print("[ ] Master bedroom is in NE corner (+X, +Y)")
print("[ ] Ensuite is in SE corner (+X, -Y)")
print("[ ] Windows on north wall cut inward (-Y direction)")
print("[ ] Windows on south wall cut inward (+Y direction)")
print("[ ] Windows on east wall cut inward (-X direction)")
print("[ ] Windows on west wall cut inward (+X direction)")
print("[ ] Shower in NW corner of ensuite, toilet in SW, vanity in SE")
print("[ ] All interior elements are INSIDE the building")
