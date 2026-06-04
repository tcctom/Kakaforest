"""
Test script for björken_module.py coordinate transformation
Verifies North = +Y convention

To run: Open in Blender and execute script in Scripting workspace
"""
import bpy  # type: ignore
import sys
import importlib

# Add parent directory to path
sys.path.insert(0, r"c:\KakaForestRetreat")

# Import and reload module
import björken_module
importlib.reload(björken_module)
from björken_module import build_red_cottage

# Clear scene
for obj in list(bpy.context.scene.objects):
    bpy.data.objects.remove(obj)

# Build cottage at origin
build_red_cottage(origin=(0, 0, 0))

# Set up top orthographic view
bpy.ops.object.camera_add(location=(0, 0, 20))
camera = bpy.context.active_object
camera.name = "TopView"
camera.rotation_euler = (0, 0, 0)  # Looking straight down
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 15.0

bpy.context.scene.camera = camera

print("=" * 60)
print("TEST: Björken Module Coordinate Verification")
print("=" * 60)
print("✓ Building rendered at origin (0, 0, 0)")
print("\nVerification checklist:")
print("[ ] North wall (Cottage_NorthWall) is on +Y side (top of screen)")
print("[ ] South wall (Cottage_SouthWall) is on -Y side (bottom of screen)")
print("[ ] Verandah (Cottage_Verandah) extends NORTH from building (+Y direction)")
print("[ ] Verandah posts are on NORTH edge of verandah")
print("[ ] Windows on north wall are visible on +Y face")
print("[ ] East/West wall windows positioned symmetrically")
print("\nSwitch to top orthographic view to verify visually.")
print("=" * 60)
