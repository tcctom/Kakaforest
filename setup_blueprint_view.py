"""
Blender Python Script: Setup 2D Architectural Blueprint View
Creates a top-down orthographic view with flat shading and cavity lines
for architectural floor plan visualization.
"""

import bpy  # type: ignore
from mathutils import Euler  # type: ignore
import math


def setup_blueprint_viewport():
    """
    Configure the active 3D viewport for blueprint-style rendering.
    Sets flat shading with white background and cavity edge highlighting.
    """
    # Find the active 3D viewport
    area = None
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D':
            area = a
            break
    
    if area is None:
        print("Error: No 3D View area found!")
        return False
    
    # Get the 3D view space
    space = area.spaces.active
    
    # Set shading mode to SOLID (flat)
    space.shading.type = 'SOLID'
    
    # Set color type to SINGLE with pure white background
    space.shading.color_type = 'SINGLE'
    space.shading.single_color = (1.0, 1.0, 1.0)  # Pure white
    
    # Enable cavity shading for edge highlighting
    space.shading.show_cavity = True
    space.shading.cavity_type = 'WORLD'  # Use world-space cavity
    
    # Set ridge and valley to maximum for strong edge definition
    space.shading.cavity_ridge_factor = 1.0  # Maximum ridge
    space.shading.cavity_valley_factor = 1.0  # Maximum valley
    
    # Optional: Set light to be flat/minimal for blueprint look
    space.shading.light = 'FLAT'
    
    print("✓ Viewport configured for blueprint view")
    return True


def create_blueprint_camera(location=(0, 0, 15), clip_height=1.2):
    """
    Create and configure an orthographic camera for top-down blueprint view.
    
    Args:
        location: Tuple (x, y, z) for camera position. Default is centered at 15m height.
        clip_height: Z-height in meters where to clip the view (default 1.2m for interior view)
    """
    # Check if Blueprint_Camera already exists, remove it
    if "Blueprint_Camera" in bpy.data.objects:
        old_cam = bpy.data.objects["Blueprint_Camera"]
        bpy.data.objects.remove(old_cam, do_unlink=True)
    
    # Create camera data and object
    cam_data = bpy.data.cameras.new(name="Blueprint_Camera")
    cam_object = bpy.data.objects.new("Blueprint_Camera", cam_data)
    
    # Link to scene collection
    bpy.context.scene.collection.objects.link(cam_object)
    
    # Set camera type to ORTHOGRAPHIC
    cam_data.type = 'ORTHO'
    
    # Set orthographic scale (adjust based on scene size)
    cam_data.ortho_scale = 30.0  # Covers roughly 30m x 30m area
    
    # Position camera
    cam_object.location = location
    
    # Point camera straight down (top-down view)
    # Rotation in Euler angles: (90° around X-axis points camera down)
    cam_object.rotation_euler = Euler((math.radians(0), 0, 0), 'XYZ')
    
    # Set up clipping to cut at specified height
    # The clip_start determines minimum distance from camera
    # Since camera is at location[2] height and we want to clip at clip_height:
    # clip_start = camera_height - clip_height
    camera_height = location[2]
    cam_data.clip_start = camera_height - clip_height
    cam_data.clip_end = camera_height + 1.0  # Just above camera
    
    # Make this the active scene camera
    bpy.context.scene.camera = cam_object
    
    print(f"✓ Blueprint camera created at {location}")
    print(f"  - Orthographic scale: {cam_data.ortho_scale}m")
    print(f"  - Clipping at Z={clip_height}m (clip_start={cam_data.clip_start}m)")
    
    return cam_object


def setup_section_plane_method(clip_height=1.2):
    """
    Alternative method: Create a section plane with boolean modifiers
    to cut through buildings at specified height.
    This is more complex but gives cleaner cuts for complex geometry.
    
    Args:
        clip_height: Z-height in meters where to section the view
    """
    # Create a large plane at the clip height
    bpy.ops.mesh.primitive_plane_add(
        size=100,
        location=(0, 0, clip_height)
    )
    section_plane = bpy.context.active_object
    section_plane.name = "Section_Plane"
    
    # Add solidify modifier to give it thickness
    solidify = section_plane.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = 50  # Very thick to ensure it cuts everything above
    solidify.offset = 1.0  # Extend upward
    
    # Hide the section plane from render and viewport
    section_plane.hide_viewport = True
    section_plane.hide_render = True
    
    print(f"✓ Section plane created at Z={clip_height}m")
    print("  Note: To use boolean cutting, manually apply Boolean modifiers")
    print("  to building objects using this plane as the cutter.")
    
    return section_plane


def view_through_camera():
    """
    Set the active viewport to view through the active camera.
    """
    # Find the active 3D viewport
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Toggle camera view
                    space.region_3d.view_perspective = 'CAMERA'
                    print("✓ Viewport set to camera view")
                    return True
    return False


def main():
    """
    Main function to set up complete blueprint view.
    """
    print("\n" + "="*60)
    print("Setting up 2D Architectural Blueprint View")
    print("="*60 + "\n")
    
    # Step 1: Configure viewport shading
    if not setup_blueprint_viewport():
        print("Failed to configure viewport!")
        return
    
    # Step 2: Create blueprint camera
    # Adjust location based on your site center and size
    # For Kaka Forest Retreat, center might be around (5, -5, 15)
    camera = create_blueprint_camera(
        location=(5, -5, 20),  # Adjust X, Y to center on your site
        clip_height=1.2  # Cut at 1.2m height to see interior
    )
    
    # Step 3: Switch viewport to camera view
    view_through_camera()
    
    # Optional: Create section plane for manual boolean cutting
    # Uncomment the line below if you want to use boolean method instead
    # setup_section_plane_method(clip_height=1.2)
    
    print("\n" + "="*60)
    print("Blueprint view setup complete!")
    print("="*60)
    print("\nTips:")
    print("- Adjust camera ortho_scale in Object Properties if view is too tight/loose")
    print("- Change clip_height parameter to section at different heights")
    print("- Use Numpad 0 to toggle camera view on/off")
    print("- Render with F12 to get a clean blueprint image")


# Run the setup
if __name__ == "__main__":
    main()
