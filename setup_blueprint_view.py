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
    # Set world background to white
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    # Set world background to pure white (nodes exist by default in Blender 5.1+)
    if world.node_tree:
        bg_node = world.node_tree.nodes.get('Background')
        if bg_node:
            bg_node.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)  # White RGBA
    
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
    
    # Use SINGLE white color
    space.shading.color_type = 'SINGLE'
    space.shading.single_color = (1.0, 1.0, 1.0)  # Pure white
    
    # Set viewport background color to white
    space.shading.background_type = 'VIEWPORT'
    space.shading.background_color = (1.0, 1.0, 1.0)  # White background
    
    # Disable X-ray mode (it causes gray transparency)
    space.shading.show_xray = False
    
    # Disable shadows and lighting effects
    space.shading.show_shadows = False
    space.shading.show_backface_culling = False
    
    # Enable cavity shading for edge highlighting - use BOTH for maximum effect
    space.shading.show_cavity = True
    space.shading.cavity_type = 'BOTH'  # Both world and screen
    
    # Maximum cavity settings for strongest possible edge lines
    space.shading.cavity_ridge_factor = 2.5  # Very strong ridge lines
    space.shading.cavity_valley_factor = 2.5  # Very strong valley lines
    
    # Set light to be flat for blueprint look
    space.shading.light = 'FLAT'
    
    # Configure overlays for clean blueprint view
    space.overlay.show_floor = False  # Hide grid floor
    space.overlay.show_axis_x = False  # Hide X axis
    space.overlay.show_axis_y = False  # Hide Y axis
    space.overlay.show_axis_z = False  # Hide Z axis
    space.overlay.show_cursor = False  # Hide 3D cursor
    space.overlay.show_object_origins = False  # Hide origin points
    space.overlay.show_text = True  # Keep text visible
    space.overlay.show_wireframes = True  # Enable wireframe edges on objects
    space.overlay.show_ortho_grid = False  # Hide orthographic grid
    space.overlay.show_outline_selected = False  # Don't highlight selected
    
    print("✓ Viewport configured for blueprint view")
    return True


def create_blueprint_camera(name="Blueprint_Camera", location=(0, 0, 15), clip_height=1.2, ortho_scale=30.0):
    """
    Create and configure an orthographic camera for top-down blueprint view.
    
    Args:
        name: Name for the camera
        location: Tuple (x, y, z) for camera position. Default is centered at 15m height.
        clip_height: Z-height in meters where to clip the view (default 1.2m for interior view)
        ortho_scale: Size of the orthographic view area
    """
    # Check if camera already exists, remove it
    if name in bpy.data.objects:
        old_cam = bpy.data.objects[name]
        bpy.data.objects.remove(old_cam, do_unlink=True)
    
    # Create camera data and object
    cam_data = bpy.data.cameras.new(name=name)
    cam_object = bpy.data.objects.new(name, cam_data)
    
    # Link to scene collection
    bpy.context.scene.collection.objects.link(cam_object)
    
    # Set camera type to ORTHOGRAPHIC
    cam_data.type = 'ORTHO'
    
    # Set orthographic scale (adjust based on scene size)
    cam_data.ortho_scale = ortho_scale
    
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
    
    print(f"✓ Camera '{name}' created at {location}")
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


def create_section_cutter(cut_height):
    """
    Create a large cube that acts as a boolean cutter to remove geometry above cut_height.
    """
    cutter_name = "Blueprint_Cutter"
    
    # Remove existing cutter if present
    if cutter_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[cutter_name], do_unlink=True)
    
    # Create a large cube positioned to cut everything above cut_height
    bpy.ops.mesh.primitive_cube_add(
        size=200,  # Very large to cover entire scene
        location=(0, 0, cut_height + 100)  # Position it above the cut height
    )
    cutter = bpy.context.active_object
    cutter.name = cutter_name
    cutter.display_type = 'WIRE'  # Show as wireframe so it doesn't block view
    cutter.hide_viewport = True  # Hide from viewport completely
    cutter.hide_render = True  # Hide from renders
    
    print(f"✓ Created section cutter at Z={cut_height}m")
    return cutter


def apply_section_to_all_objects(cut_height):
    """
    Apply boolean difference modifiers to all mesh objects using section cutter.
    This physically removes geometry above the cut height to reveal interiors.
    Uses smart ordering to preserve windows/doors.
    Also hides deck/verandah objects that clutter the floor plan.
    """
    # Hide deck and verandah objects from view (they clutter floor plans)
    # BUT NOT walls that might have these keywords
    # Also hide terrain, boulders, and site elements
    hide_keywords = ['deck', 'Deck', 'verandah', 'Verandah', 'Pile', 'Bearer', 'Joist',
                     'Boulder', 'boulder', 'Terrain', 'terrain', 'Ground_', 'Gravel',
                     'WaterTank', 'Pavers']
    hidden_count = 0
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # Skip if it's a wall object
            if 'Wall' in obj.name or 'wall' in obj.name:
                continue
            for keyword in hide_keywords:
                if keyword in obj.name:
                    obj.hide_viewport = True
                    obj.hide_render = True
                    hidden_count += 1
                    break
    print(f"  Hidden {hidden_count} deck/terrain/site objects")
    
    # FIRST: Enable wireframe on ALL mesh objects for edge visibility
    # EXCEPT the background plane and labels
    wire_count = 0
    for obj in bpy.data.objects:
        if (obj.type == 'MESH' and 
            not obj.name.startswith('Label_') and 
            not obj.name.startswith('Blueprint_') and
            obj.name != 'Blueprint_Background'):
            obj.show_wire = True
            obj.show_all_edges = True
            wire_count += 1
    print(f"  Enabled wireframe on {wire_count} objects")
    
    # Create the cutter cube
    cutter = create_section_cutter(cut_height)
    
    count = 0
    skipped = []
    
    # First pass: collect all objects and check for existing booleans
    objects_with_booleans = []
    regular_objects = []
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj != cutter and not obj.name.startswith('Label_'):
            has_boolean = any(mod.type == 'BOOLEAN' for mod in obj.modifiers)
            if has_boolean:
                objects_with_booleans.append(obj)
            else:
                regular_objects.append(obj)
    
    # Apply to all objects
    for obj in objects_with_booleans + regular_objects:
        # Remove any existing Blueprint_Section modifier
        for mod in list(obj.modifiers):
            if mod.name == "Blueprint_Section":
                obj.modifiers.remove(mod)
        
        # Add new boolean modifier AT THE END
        bool_mod = obj.modifiers.new(name="Blueprint_Section", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = cutter
        bool_mod.solver = 'EXACT'
        
        # Ensure this modifier is last in the stack
        while obj.modifiers.find(bool_mod.name) < len(obj.modifiers) - 1:
            try:
                # Move down one position at a time
                override = {'object': obj}
                with bpy.context.temp_override(**override):
                    bpy.ops.object.modifier_move_down(modifier=bool_mod.name)
            except:
                break  # Can't move further
        
        count += 1
    
    print(f"\n✓ Applied section cutting to {count} objects at Z={cut_height}m")
    print(f"  - {len(objects_with_booleans)} objects had existing booleans (windows/doors)")
    print(f"  - {len(regular_objects)} regular objects")
    print(f"  Note: Geometry above {cut_height}m is now hidden via boolean modifiers")
    
    # Count visible objects with wireframe
    visible_wire_count = sum(1 for obj in bpy.data.objects 
                             if obj.type == 'MESH' and not obj.hide_viewport 
                             and obj.show_wire and not obj.name.startswith('Blueprint_'))
    print(f"  {visible_wire_count} visible objects have wireframe edges enabled\n")
    
    return count


def remove_section_from_all_objects():
    """
    Remove section cutting modifiers from all objects and delete the cutter.
    Also restores visibility of deck/verandah objects.
    """
    # Remove cutter object
    cutter_name = "Blueprint_Cutter"
    if cutter_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[cutter_name], do_unlink=True)
    
    # Restore visibility of deck/verandah/terrain objects
    hide_keywords = ['deck', 'Deck', 'verandah', 'Verandah', 'Pile', 'Bearer', 'Joist',
                     'Boulder', 'boulder', 'Terrain', 'terrain', 'Ground_', 'Gravel',
                     'WaterTank', 'Pavers']
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for keyword in hide_keywords:
                if keyword in obj.name:
                    obj.hide_viewport = False
                    obj.hide_render = False
                    break
    
    # Remove boolean modifiers and disable wireframe display
    count = 0
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for mod in list(obj.modifiers):
                if mod.name == "Blueprint_Section":
                    obj.modifiers.remove(mod)
                    count += 1
            # Disable wireframe display
            obj.show_wire = False
            obj.show_all_edges = False
    
    print(f"✓ Removed section modifiers from {count} objects")
    print(f"✓ Restored visibility of deck/verandah objects")
    print(f"✓ Disabled wireframe edge display")


def create_white_background_plane():
    """
    Create a large white plane at ground level to act as background.
    This ensures the area around the building appears white instead of gray.
    """
    plane_name = "Blueprint_Background"
    
    # Remove existing plane if present
    if plane_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[plane_name], do_unlink=True)
    
    # Create large plane at ground level
    bpy.ops.mesh.primitive_plane_add(
        size=3000,  # Very large to cover entire viewport and beyond
        location=(0, 0, -0.05)  # Below ground to avoid z-fighting
    )
    plane = bpy.context.active_object
    plane.name = plane_name
    
    # Disable wireframe display on the background plane
    plane.show_wire = False
    plane.show_all_edges = False
    
    # Set object color for SOLID shading mode (this is what viewport shows)
    plane.color = (1.0, 1.0, 1.0, 1.0)  # Pure white RGBA
    
    # Also create a simple white material (for completeness)
    mat_name = "Blueprint_White"
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
        # Simple diffuse white - works in all shading modes
        if mat.node_tree:
            nodes = mat.node_tree.nodes
            nodes.clear()
            diffuse = nodes.new(type='ShaderNodeBsdfDiffuse')
            diffuse.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
            output = nodes.new(type='ShaderNodeOutputMaterial')
            mat.node_tree.links.new(diffuse.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material
    if plane.data.materials:
        plane.data.materials[0] = mat
    else:
        plane.data.materials.append(mat)
    
    print(f"✓ Created white background plane (3000x3000 units)")
    return plane


def create_room_label(text, location, size=0.5):
    """
    Create a text object label for rooms (e.g., "Kitchen", "Living Room").
    
    Args:
        text: Label text to display
        location: Tuple (x, y, z) for label position
        size: Text size in Blender units
    
    Returns:
        Text object
    """
    # Check if label already exists
    label_name = f"Label_{text.replace(' ', '_')}"
    if label_name in bpy.data.objects:
        print(f"  Label '{text}' already exists at {bpy.data.objects[label_name].location}")
        return bpy.data.objects[label_name]
    
    # Create text curve
    text_data = bpy.data.curves.new(name=label_name, type='FONT')
    text_data.body = text
    text_data.size = size
    text_data.align_x = 'CENTER'
    text_data.align_y = 'CENTER'
    
    # Create object
    text_obj = bpy.data.objects.new(label_name, text_data)
    bpy.context.scene.collection.objects.link(text_obj)
    
    # Position
    text_obj.location = location
    
    # Rotate to lie flat (readable from top camera)
    text_obj.rotation_euler = (0, 0, 0)  # Flat on XY plane
    
    # Make text visible in all viewports
    text_obj.show_name = False
    text_obj.show_in_front = True  # Always show in front (X-ray mode)
    
    # Create simple material for text (materials have nodes by default in Blender 5.1+)
    if "Label_Material" not in bpy.data.materials:
        mat = bpy.data.materials.new(name="Label_Material")
        # Set base color to black for text visibility
        if mat.node_tree and "Principled BSDF" in mat.node_tree.nodes:
            mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0, 0, 0, 1)
    
    if bpy.data.materials.get("Label_Material"):
        text_data.materials.append(bpy.data.materials["Label_Material"])
    
    print(f"✓ Created label: '{text}' at {location}")
    return text_obj


def show_ground_floor_plan():
    """
    ONE-COMMAND setup for ground floor plan view.
    Switches camera, applies section cutting, and adds default labels.
    """
    print("\n" + "="*60)
    print("Setting up GROUND FLOOR PLAN VIEW")
    print("="*60 + "\n")
    
    # DIAGNOSTIC: Check building position
    print("\n" + "-"*60)
    print("DIAGNOSTIC: Building position check:")
    print("-"*60)
    north_wall = bpy.data.objects.get('MainDwelling_NorthWall_Ground')
    if north_wall:
        print(f"North wall location: {north_wall.location}")
        print(f"North wall dimensions (scale): {north_wall.scale}")
        bbox = north_wall.bound_box
        min_x = min([v[0] for v in bbox])
        max_x = max([v[0] for v in bbox])
        min_y = min([v[1] for v in bbox])
        max_y = max([v[1] for v in bbox])
        print(f"North wall bounding box: X({min_x:.2f} to {max_x:.2f}), Y({min_y:.2f} to {max_y:.2f})")
    
    south_wall = bpy.data.objects.get('MainDwelling_SouthWall_Ground')
    if south_wall:
        print(f"South wall location: {south_wall.location}")
    
    print(f"\nCamera BP_Ground_Floor location: {bpy.data.objects['BP_Ground_Floor'].location}")
    print("-"*60 + "\n")
    
    # Switch to ground floor camera
    switch_to_camera('BP_Ground_Floor')
    view_through_camera()
    
    # Create white background plane
    create_white_background_plane()
    
    print("Applying section cut to reveal interior walls...")
    apply_section_to_all_objects(1.3)  # Slightly higher to avoid deck edge issues
    
    # Add sample labels (customize these for your actual rooms)
    print("\nAdding room labels...")
    # Example labels - adjust coordinates to match your building layout
    # Using Z at cut height so labels are visible
    create_room_label('GROUND FLOOR', (0, -1.5, 1.3), size=0.8)
    
    print("\n" + "="*60)
    print("✓ GROUND FLOOR PLAN READY!")
    print("="*60)
    print("\nWhat you should see:")
    print("  - White background with black edge lines (no shadows)")
    print("  - All walls, partitions, and rooms visible as cross-section")
    print("  - Windows and doors visible as openings")
    print("  - Geometry above 1.3m height is cut away")
    print("  - 'GROUND FLOOR' label visible in center")
    print("\nTo add room labels:")
    print("  create_room_label('Kitchen', (x, y, 1.3), size=0.5)")
    print("  create_room_label('Living Room', (x, y, 1.3), size=0.5)")
    print("\nNote: Adjust label coordinates (x, y) to match room centers")
    print("="*60)


def show_first_floor_plan():
    """
    ONE-COMMAND setup for first floor plan view.
    Switches camera, applies section cutting, and adds default labels.
    """
    print("\n" + "="*60)
    print("Setting up FIRST FLOOR PLAN VIEW")
    print("="*60 + "\n")
    
    # Switch to first floor camera
    switch_to_camera('BP_First_Floor')
    view_through_camera()
    
    # Apply section cutting at 4.0m
    print("Applying section cut to reveal interior walls...")
    apply_section_to_all_objects(4.0)
    
    # Add sample labels
    print("\nAdding room labels...")
    create_room_label('FIRST FLOOR', (0, -1.5, 3.8), size=0.8)
    
    print("\n✓ First floor plan ready!")
    print("  To add more labels: create_room_label('Bedroom', (x, y, 3.8), size=0.5)")
    print("="*60)


def show_roof_plan():
    """
    ONE-COMMAND setup for roof plan view.
    """
    print("\n" + "="*60)
    print("Setting up ROOF PLAN VIEW")
    print("="*60 + "\n")
    
    switch_to_camera('BP_Roof_Plan')
    view_through_camera()
    apply_section_to_all_objects(7.5)
    
    print("\n✓ Roof plan ready!")
    print("="*60)


def show_site_plan():
    """
    ONE-COMMAND setup for site overview.
    Removes all section cutting to show complete buildings.
    """
    print("\n" + "="*60)
    print("Setting up SITE PLAN VIEW")
    print("="*60 + "\n")
    
    switch_to_camera('BP_Site_Plan')
    view_through_camera()
    remove_section_from_all_objects()
    
    print("\n✓ Site plan ready!")
    print("="*60)


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


def switch_to_camera(camera_name):
    """
    Switch the active scene camera to the specified camera.
    
    Args:
        camera_name: Name of the camera to switch to
    """
    if camera_name in bpy.data.objects:
        cam_object = bpy.data.objects[camera_name]
        bpy.context.scene.camera = cam_object
        print(f"✓ Switched to camera: {camera_name}")
        return True
    else:
        print(f"✗ Camera '{camera_name}' not found!")
        return False


def create_floor_plan_cameras(center_x=0, center_y=-1.5):
    """
    Create multiple cameras for different floor levels.
    
    Args:
        center_x: X coordinate to center cameras on site
        center_y: Y coordinate to center cameras on site
    
    Returns:
        Dictionary of created cameras
    """
    cameras = {}
    
    # Ground Floor Plan - cuts at 1.3m (slightly above standard door height)
    cameras['ground'] = create_blueprint_camera(
        name="BP_Ground_Floor",
        location=(center_x, center_y, 20),
        clip_height=1.3,
        ortho_scale=30.0
    )
    
    # First Floor Plan - cuts at 4.0m (above ground floor ceiling)
    cameras['first'] = create_blueprint_camera(
        name="BP_First_Floor", 
        location=(center_x, center_y, 20),
        clip_height=4.0,
        ortho_scale=30.0
    )
    
    # Roof Plan - cuts at 7.5m (above first floor ceiling)
    cameras['roof'] = create_blueprint_camera(
        name="BP_Roof_Plan",
        location=(center_x, center_y, 20),
        clip_height=7.5,
        ortho_scale=30.0
    )
    
    # Site Plan - no clipping, overview from high up
    cameras['site'] = create_blueprint_camera(
        name="BP_Site_Plan",
        location=(center_x, center_y, 50),
        clip_height=-5.0,  # Below ground, shows everything
        ortho_scale=50.0  # Wider view
    )
    
    return cameras


def main():
    """
    Main function to set up complete blueprint view with multiple floor cameras.
    """
    print("\n" + "="*60)
    print("Setting up 2D Architectural Blueprint View")
    print("="*60 + "\n")
    
    # Step 1: Configure viewport shading
    if not setup_blueprint_viewport():
        print("Failed to configure viewport!")
        return
    
    # Step 2: Create cameras for different floor levels
    print("\nCreating floor plan cameras...")
    cameras = create_floor_plan_cameras(center_x=0, center_y=-1.5)
    
    # Step 3: Set ground floor as default active camera
    switch_to_camera("BP_Ground_Floor")
    
    # Step 4: Switch viewport to camera view
    view_through_camera()
    
    print("\n" + "="*60)
    print("Blueprint view setup complete!")
    print("="*60)
    print("\nCreated Cameras:")
    print("  1. BP_Ground_Floor (cuts at 1.3m)")
    print("  2. BP_First_Floor (cuts at 4.0m)")
    print("  3. BP_Roof_Plan (cuts at 7.5m)")
    print("  4. BP_Site_Plan (overview, no clipping)")
    print("\n" + "="*60)
    print("ONE-COMMAND VIEW SETUP:")
    print("="*60)
    print("  show_ground_floor_plan()  - Complete ground floor setup")
    print("  show_first_floor_plan()   - Complete first floor setup")
    print("  show_roof_plan()          - Complete roof plan setup")
    print("  show_site_plan()          - Complete site overview")
    print("\n" + "="*60)
    print("\nManual controls (if needed):")
    print("  apply_section_to_all_objects(1.2)  - Cut at specific height")
    print("  create_room_label('Kitchen', (x, y, z), size=0.5)  - Add labels")
    print("  remove_section_from_all_objects()  - Remove all cutting")
    print("\nTips:")
    print("- Use Numpad 0 to toggle camera view on/off")
    print("- Labels Z-coord should match cut height (e.g., 0.1 for ground, 3.5 for first)")
    print("="*60)


# Run the setup
if __name__ == "__main__":
    main()
