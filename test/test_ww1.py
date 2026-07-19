"""
Test script for ww1_module.py coordinate transformation
Verifies East = +X, North = +Y convention

To run: Open in Blender and execute script in Scripting workspace
"""
import bpy  # type: ignore
import sys
import importlib

# Add parent directory to path
sys.path.insert(0, r"c:\KakaForestRetreat")

# Import and reload modules (including furniture)
import archive.ww1_furniture as ww1_furniture
import archive.ww1_module as ww1_module
importlib.reload(ww1_furniture)  # Reload furniture first
importlib.reload(ww1_module)      # Then reload main module
from archive.ww1_module import build_potius_wet_wing

# Clear scene
for obj in list(bpy.context.scene.objects):
    bpy.data.objects.remove(obj)

# Build wet wing at origin
build_potius_wet_wing(origin=(0, 0, 0))

# Set up top orthographic view
bpy.ops.object.camera_add(location=(0, 0, 20))
camera = bpy.context.active_object
camera.name = "TopView"
camera.rotation_euler = (0, 0, 0)  # Looking straight down
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 15.0

bpy.context.scene.camera = camera

print("=" * 60)
print("TEST: WW1 Module Coordinate Verification")
print("=" * 60)
print("✓ Building rendered at origin (0, 0, 0)")
print("\nCoordinate System: East = +X, North = +Y")
print("\nVerification checklist:")
print("[ ] North wall (WetWing_NorthWall) is on +Y side (top of screen) - TALLER")
print("[ ] South wall (WetWing_SouthWall) is on -Y side (bottom of screen) - SHORTER")
print("[ ] East wall (WetWing_EastWall) is on +X side (right of screen)")
print("[ ] West wall (WetWing_WestWall) is on -X side (left of screen)")
print("[ ] North verandah extends NORTH from building (+Y direction)")
print("[ ] East verandah is on EAST side of building (+X direction)")
print("[ ] Windows on north wall are visible on +Y face")
print("[ ] Bed is against WEST wall (-X side) in north room")
print("[ ] Kitchen benchtop is on EAST side (+X) in south room")
print("\nSwitch to top orthographic view to verify visually.")
print("Roof should slope down from North (higher) to South (lower)")
print("=" * 60)
