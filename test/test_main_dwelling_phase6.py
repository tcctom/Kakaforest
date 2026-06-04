import bpy  # type: ignore
import sys
import os
import importlib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and reload module
import main_dwelling_module
importlib.reload(main_dwelling_module)

# Cleanup
def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

cleanup()

# Build main dwelling with Phase 6 elements (stairs, deck, roof)
print("\n" + "="*60)
print("TESTING PHASE 6: Main Dwelling - Stairs, Deck, and Roof")
print("="*60)

main_dwelling_module.build_main_dwelling(
    origin=(0, 0, 0),
    show_roof=True,
    roof_style="flush"
)

# Also build the north deck
main_dwelling_module.build_north_deck(
    origin=(0, 0, 0),
    building_length=9.0,
    building_width=7.0,
    north_recess=1.0
)

# Set up top orthographic view
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        space = area.spaces.active
        space.region_3d.view_perspective = 'ORTHO'
        space.shading.type = 'SOLID'
        # Set to top view
        space.region_3d.view_rotation = (0, 0, 0, 1)  # Top down view
        break

print("\n" + "="*60)
print("Phase 6 Test Complete!")
print("="*60)
print("Expected Layout (Top View, North = +Y = Up):")
print("  - Main dwelling: 9m (E-W) × 7m (N-S)")
print("  - Staircase in SW corner (-X, -Y)")
print("  - Deck extending north (+Y) from north wall")
print("  - Gable roof running E-W with ridge along center")
print("\nVerification Checklist:")
print("  [ ] Staircase in SW (lower-left) corner")
print("  [ ] Stairs Flight 1 on EAST side of stairwell")
print("  [ ] Stairs Flight 2 on WEST side of stairwell")
print("  [ ] Landing in middle, at south end")
print("  [ ] Deck extending northward (upward on screen) from north wall")
print("  [ ] Deck piles and joists properly positioned")
print("  [ ] Roof gable ends on east/west sides")
print("="*60 + "\n")
