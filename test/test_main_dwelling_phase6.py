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

# Create visual axis indicators to show coordinate system
def create_axis_arrows():
    """Create colored arrows showing coordinate system: X=East(Red), Y=North(Green), Z=Up(Blue)"""
    arrow_length = 5.0
    arrow_thickness = 0.1
    
    # X-axis arrow (RED = EAST)
    bpy.ops.mesh.primitive_cylinder_add(location=(arrow_length/2, 0, 0), rotation=(0, 1.5708, 0))
    x_arrow = bpy.context.active_object
    x_arrow.name = "Axis_X_EAST"
    x_arrow.scale = (arrow_thickness, arrow_thickness, arrow_length/2)
    bpy.ops.object.transform_apply(scale=True)
    x_mat = bpy.data.materials.new("Axis_X_RED")
    x_mat.diffuse_color = (1, 0, 0, 1)  # Red
    x_arrow.data.materials.append(x_mat)
    
    # Add cone at end
    bpy.ops.mesh.primitive_cone_add(location=(arrow_length, 0, 0), rotation=(0, 1.5708, 0))
    x_cone = bpy.context.active_object
    x_cone.name = "Axis_X_Tip"
    x_cone.scale = (arrow_thickness*3, arrow_thickness*3, arrow_thickness*5)
    bpy.ops.object.transform_apply(scale=True)
    x_cone.data.materials.append(x_mat)
    
    # Y-axis arrow (GREEN = NORTH)
    bpy.ops.mesh.primitive_cylinder_add(location=(0, arrow_length/2, 0), rotation=(1.5708, 0, 0))
    y_arrow = bpy.context.active_object
    y_arrow.name = "Axis_Y_NORTH"
    y_arrow.scale = (arrow_thickness, arrow_thickness, arrow_length/2)
    bpy.ops.object.transform_apply(scale=True)
    y_mat = bpy.data.materials.new("Axis_Y_GREEN")
    y_mat.diffuse_color = (0, 1, 0, 1)  # Green
    y_arrow.data.materials.append(y_mat)
    
    # Add cone at end
    bpy.ops.mesh.primitive_cone_add(location=(0, arrow_length, 0), rotation=(1.5708, 0, 0))
    y_cone = bpy.context.active_object
    y_cone.name = "Axis_Y_Tip"
    y_cone.scale = (arrow_thickness*3, arrow_thickness*3, arrow_thickness*5)
    bpy.ops.object.transform_apply(scale=True)
    y_cone.data.materials.append(y_mat)
    
    # Z-axis arrow (BLUE = UP)
    bpy.ops.mesh.primitive_cylinder_add(location=(0, 0, arrow_length/2))
    z_arrow = bpy.context.active_object
    z_arrow.name = "Axis_Z_UP"
    z_arrow.scale = (arrow_thickness, arrow_thickness, arrow_length/2)
    bpy.ops.object.transform_apply(scale=True)
    z_mat = bpy.data.materials.new("Axis_Z_BLUE")
    z_mat.diffuse_color = (0, 0, 1, 1)  # Blue
    z_arrow.data.materials.append(z_mat)
    
    # Add cone at end
    bpy.ops.mesh.primitive_cone_add(location=(0, 0, arrow_length))
    z_cone = bpy.context.active_object
    z_cone.name = "Axis_Z_Tip"
    z_cone.scale = (arrow_thickness*3, arrow_thickness*3, arrow_thickness*5)
    bpy.ops.object.transform_apply(scale=True)
    z_cone.data.materials.append(z_mat)
    
    print("\nAxis indicators created:")
    print("  RED arrow = +X = EAST")
    print("  GREEN arrow = +Y = NORTH")
    print("  BLUE arrow = +Z = UP")

create_axis_arrows()

# Build main dwelling with Phase 6 elements (stairs, deck, roof)
print("\n" + "="*60)
print("TESTING PHASE 6: Main Dwelling - Stairs, Deck, and Roof")
print("="*60)

main_dwelling_module.build_main_dwelling_simple_porch(
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
