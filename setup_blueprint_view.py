"""
Blender Python Script: Setup 2D Architectural Blueprint View
Creates a top-down orthographic view with flat shading and cavity lines
for architectural floor plan visualization.
"""

import bpy  # type: ignore
from mathutils import Euler  # type: ignore
import math


# -----------------------------------------------------------------------------
# Blueprint Tuning
# -----------------------------------------------------------------------------
# One-switch style preset:
# True  -> clean presentation mode (minimal clutter, clear walls/openings)
# False -> legacy technical mode (heavier edge/wire overlays)
PLAN_CLEAN_MODE = True

# Clean mode contrast preset:
# 'strong' (default) -> crisper wall/opening definition
# 'soft'             -> lighter, more subdued drawing look
PRESENTATION_CONTRAST = 'strong'

# Structural objects that keep wire edges when clean mode is enabled.
STRUCTURE_WIRE_KEYWORDS = ('wall', 'partition', 'slab', 'floor', 'roof', 'beam', 'column', 'stair')

if PLAN_CLEAN_MODE:
    SHOW_GLOBAL_WIREFRAME_OVERLAY = False
    EMPHASIZE_OPENINGS_IN_SOLID_VIEW = True
    SHOW_WIREFRAME_FOR_ALL_MESHES = False

    if PRESENTATION_CONTRAST.lower() == 'soft':
        ANNOTATION_COLOR = (0.2, 0.2, 0.2, 1.0)
        DIMENSION_LINE_BEVEL = 0.004
        WALL_FILL_COLOR = (0.985, 0.985, 0.985, 1.0)
        CAVITY_RIDGE_FACTOR = 2.1
        CAVITY_VALLEY_FACTOR = 2.1
        OPENING_GUIDE_COLOR = (0.30, 0.30, 0.30, 1.0)
    else:
        # Default strong presentation preset
        ANNOTATION_COLOR = (0.16, 0.16, 0.16, 1.0)
        DIMENSION_LINE_BEVEL = 0.005
        WALL_FILL_COLOR = (0.99, 0.99, 0.99, 1.0)
        CAVITY_RIDGE_FACTOR = 2.6
        CAVITY_VALLEY_FACTOR = 2.6
        OPENING_GUIDE_COLOR = (0.22, 0.22, 0.22, 1.0)
else:
    # Previous stronger look (kept for comparison)
    ANNOTATION_COLOR = (0.0, 0.0, 0.0, 1.0)
    DIMENSION_LINE_BEVEL = 0.008
    SHOW_GLOBAL_WIREFRAME_OVERLAY = True
    EMPHASIZE_OPENINGS_IN_SOLID_VIEW = False
    WALL_FILL_COLOR = (1.0, 1.0, 1.0, 1.0)
    CAVITY_RIDGE_FACTOR = 1.8
    CAVITY_VALLEY_FACTOR = 1.8
    SHOW_WIREFRAME_FOR_ALL_MESHES = True
    OPENING_GUIDE_COLOR = (0.0, 0.0, 0.0, 1.0)


def _get_opening_cutter_objects():
    """
    Find boolean cutter objects used for door/window/opening modifiers.
    These cutters can be displayed as lightweight opening guides in top-down plans.
    """
    cutters = set()
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for mod in obj.modifiers:
            if mod.type != 'BOOLEAN' or mod.object is None:
                continue
            if mod.name == 'Blueprint_Section':
                continue
            mod_name = mod.name.lower()
            if any(token in mod_name for token in ('window', 'door', 'opening', 'cut')):
                cutters.add(mod.object)
    return cutters


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
    
    # Use OBJECT colors so text/dimension objects can be forced to pure black
    # while walls/background remain white.
    space.shading.color_type = 'OBJECT'
    
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
    
    # Strong but slightly reduced cavity settings for cleaner text edges.
    space.shading.cavity_ridge_factor = CAVITY_RIDGE_FACTOR
    space.shading.cavity_valley_factor = CAVITY_VALLEY_FACTOR
    
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
    # Previous: True (caused hatched wire overlay on text glyphs)
    space.overlay.show_wireframes = SHOW_GLOBAL_WIREFRAME_OVERLAY
    space.overlay.show_ortho_grid = False  # Hide orthographic grid
    space.overlay.show_outline_selected = False  # Don't highlight selected
    # Hide helper gizmos (camera frames/lights/empties) while keeping overlays on.
    if hasattr(space.overlay, 'show_extras'):
        space.overlay.show_extras = False
    
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

    # Disable only diagonal composition guides (the big X), preserving other guides.
    for attr in dir(cam_data):
        if attr.startswith('show_composition_') and 'diagonal' in attr:
            try:
                setattr(cam_data, attr, False)
            except Exception:
                pass
    
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


def restore_image_reference_empties():
    """
    Recovery helper: unhide IMAGE empties that may have been hidden by older
    blueprint script versions, so window markers become visible again.
    """
    restored = 0
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY' and getattr(obj, 'empty_display_type', None) == 'IMAGE':
            if obj.hide_viewport or obj.hide_render:
                obj.hide_viewport = False
                obj.hide_render = False
                restored += 1

    if restored:
        print(f"✓ Restored {restored} image reference empty object(s)")
    return restored


def hide_area_light_helpers():
    """
    Hide AREA light helper gizmos in viewport.
    AREA lights display as a rectangle with a diagonal X, which can clutter
    blueprint views. This does not touch window/image reference empties.
    """
    hidden = 0
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and getattr(obj.data, 'type', None) == 'AREA':
            if not obj.hide_viewport:
                obj.hide_viewport = True
                hidden += 1

    if hidden:
        print(f"✓ Hid {hidden} AREA light helper object(s) in viewport")
    return hidden


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


def apply_section_to_all_objects(cut_height, hide_site_elements=True):
    """
    Apply boolean difference modifiers to all mesh objects using section cutter.
    This physically removes geometry above the cut height to reveal interiors.
    Uses smart ordering to preserve windows/doors.
    Optionally hides deck/verandah/site objects that clutter the floor plan.

    Args:
        cut_height: Section cut height in meters.
        hide_site_elements: If True, hide deck/site objects using keyword matching.
    """
    # Hide deck and verandah objects from view (they clutter floor plans)
    # BUT NOT walls that might have these keywords
    # Also hide terrain, boulders, and site elements
    if hide_site_elements:
        hide_keywords = ['deck', 'Deck', 'verandah', 'Verandah', 'Pile', 'Bearer', 'Joist',
                         'Boulder', 'boulder', 'Terrain', 'terrain', 'Ground_', 'Gravel',
                         'xWaterTank', 'Pavers', 'Drive', 'Tree', 'Bush', 'Fence', 'Gate']
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
    else:
        print("  Keeping deck/terrain/site objects visible")
    
    opening_cutters = _get_opening_cutter_objects() if EMPHASIZE_OPENINGS_IN_SOLID_VIEW else set()

    # FIRST: Enable wireframe on ALL mesh objects for edge visibility
    # EXCEPT the background plane and labels
    wire_count = 0
    structure_wire_count = 0
    hidden_wire_count = 0
    opening_guide_count = 0
    for obj in bpy.data.objects:
        if (obj.type == 'MESH' and 
            not obj.name.startswith('Label_') and 
            not obj.name.startswith('Blueprint_') and
            obj.name != 'Blueprint_Background'):
            obj.color = WALL_FILL_COLOR
            name_lower = obj.name.lower()
            is_structure_obj = any(keyword in name_lower for keyword in STRUCTURE_WIRE_KEYWORDS)

            # Previous behavior: show wireframe for every mesh object.
            if SHOW_WIREFRAME_FOR_ALL_MESHES or is_structure_obj:
                obj.show_wire = True
                obj.show_all_edges = True
                if is_structure_obj:
                    structure_wire_count += 1
            else:
                obj.show_wire = False
                obj.show_all_edges = False
                hidden_wire_count += 1

            # With global wireframe overlay off, small opening details can disappear.
            # Show actual opening cutter meshes as wire guides for clear apertures.
            if EMPHASIZE_OPENINGS_IN_SOLID_VIEW and obj in opening_cutters:
                obj.hide_viewport = False
                obj.hide_render = True
                obj.display_type = 'WIRE'
                obj.show_in_front = True
                obj.color = OPENING_GUIDE_COLOR
                opening_guide_count += 1
            elif obj.display_type == 'WIRE':
                obj.display_type = 'TEXTURED'

            wire_count += 1
    print(f"  Enabled wireframe on {wire_count} objects")
    if not SHOW_WIREFRAME_FOR_ALL_MESHES:
        print(f"  Structural wireframes: {structure_wire_count} objects")
        print(f"  Non-structural wireframes suppressed: {hidden_wire_count} objects")
    if EMPHASIZE_OPENINGS_IN_SOLID_VIEW:
        print(f"  Showing {opening_guide_count} opening guide cutters (wireframe)")
    
    # Create the cutter cube
    cutter = create_section_cutter(cut_height)
    
    count = 0
    skipped = []
    
    # First pass: collect all objects and check for existing booleans
    objects_with_booleans = []
    regular_objects = []
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj != cutter and not obj.name.startswith('Label_'):
            if obj in opening_cutters:
                continue  # Keep opening guide cutters unmodified for consistent visibility
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
                     'WaterTank', 'Pavers', 'Driveway']
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
        text_obj = bpy.data.objects[label_name]
        text_obj.location = location  # Update location
        print(f"  Label '{text}' updated to {location}")
        return text_obj
    
    # Create text curve
    text_data = bpy.data.curves.new(name=label_name, type='FONT')
    text_data.body = text
    text_data.size = size
    text_data.resolution_u = 24  # Smoother glyph curves in viewport
    text_data.fill_mode = 'FRONT'
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
    # text_obj.color = (0.0, 0.0, 0.0, 1.0)  # Previous: crisp black
    text_obj.color = ANNOTATION_COLOR
    
    # Create simple material for text (materials have nodes by default in Blender 5.1+)
    if "Label_Material" not in bpy.data.materials:
        mat = bpy.data.materials.new(name="Label_Material")
        # Set base color to black for text visibility
        if mat.node_tree and "Principled BSDF" in mat.node_tree.nodes:
            # mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0, 0, 0, 1)  # Previous: black
            mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = ANNOTATION_COLOR
    
    if bpy.data.materials.get("Label_Material"):
        text_data.materials.append(bpy.data.materials["Label_Material"])
    
    print(f"✓ Created label: '{text}' at {location}")
    return text_obj


def cleanup_dimensions():
    """
    Remove all existing dimension line objects from the scene.
    Call this before creating new dimensions to avoid duplicates when renaming.
    """
    removed_count = 0
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Dim_"):
            bpy.data.objects.remove(obj, do_unlink=True)
            removed_count += 1
    
    if removed_count > 0:
        print(f"✓ Cleaned up {removed_count} old dimension objects")


def cleanup_labels():
    """
    Remove all existing room label objects from the scene.
    Call this before creating new labels to avoid stale labels when switching plans.
    """
    removed_count = 0
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Label_"):
            bpy.data.objects.remove(obj, do_unlink=True)
            removed_count += 1

    if removed_count > 0:
        print(f"✓ Cleaned up {removed_count} old label objects")


def create_dimension_line(start, end, offset=0.5, text_size=0.3, z_height=1.3, name_suffix=""):
    """
    Create an architectural dimension line with measurement text.
    
    Args:
        start: Tuple (x, y) for start point
        end: Tuple (x, y) for end point  
        offset: Distance to offset the dimension line from the measured edge (in meters)
        text_size: Size of dimension text
        z_height: Z coordinate for all elements (should match floor plan cut height)
        name_suffix: Optional suffix for unique naming
    
    Returns:
        List of created objects [dimension_line, extension_line1, extension_line2, text]
    """
    dim_name = f"Dim_{name_suffix}" if name_suffix else f"Dim_{start[0]}_{start[1]}"
    
    # Remove existing dimension objects with the same name if they exist
    old_obj_names = [f'{dim_name}_line', f'{dim_name}_ext0', f'{dim_name}_ext1', f'{dim_name}_text']
    for obj_name in old_obj_names:
        if obj_name in bpy.data.objects:
            obj = bpy.data.objects[obj_name]
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Calculate distance
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx**2 + dy**2)
    
    # Determine if horizontal or vertical
    is_horizontal = abs(dx) > abs(dy)
    
    # Calculate offset direction (perpendicular to measurement line)
    if is_horizontal:
        offset_dir = (0, offset if dy >= 0 else -offset)
    else:
        offset_dir = (offset if dx >= 0 else -offset, 0)
    
    # Offset points for dimension line
    start_offset = (start[0] + offset_dir[0], start[1] + offset_dir[1], z_height)
    end_offset = (end[0] + offset_dir[0], end[1] + offset_dir[1], z_height)
    
    created_objects = []
    
    # Create dimension line
    curve_data = bpy.data.curves.new(f'{dim_name}_line', type='CURVE')
    curve_data.dimensions = '3D'
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(1)
    polyline.points[0].co = (start_offset[0], start_offset[1], start_offset[2], 1)
    polyline.points[1].co = (end_offset[0], end_offset[1], end_offset[2], 1)
    
    dim_obj = bpy.data.objects.new(f'{dim_name}_line', curve_data)
    bpy.context.scene.collection.objects.link(dim_obj)
    
    # Set line properties
    # curve_data.bevel_depth = 0.008  # Previous: thicker/stronger
    curve_data.bevel_depth = DIMENSION_LINE_BEVEL
    curve_data.use_fill_caps = True
    # dim_obj.color = (0.0, 0.0, 0.0, 1.0)  # Previous: black
    dim_obj.color = ANNOTATION_COLOR
    created_objects.append(dim_obj)
    
    # Create extension lines (ticks at ends)
    ext_length = 0.15
    
    for i, (point, point_offset) in enumerate([(start, start_offset), (end, end_offset)]):
        ext_curve = bpy.data.curves.new(f'{dim_name}_ext{i}', type='CURVE')
        ext_curve.dimensions = '3D'
        ext_line = ext_curve.splines.new('POLY')
        ext_line.points.add(1)
        
        # Extension line from original point to beyond dimension line
        if is_horizontal:
            ext_start = (point[0], point[1], z_height)
            ext_end = (point[0], point_offset[1] + (ext_length if offset > 0 else -ext_length), z_height)
        else:
            ext_start = (point[0], point[1], z_height)
            ext_end = (point_offset[0] + (ext_length if offset > 0 else -ext_length), point[1], z_height)
        
        ext_line.points[0].co = (ext_start[0], ext_start[1], ext_start[2], 1)
        ext_line.points[1].co = (ext_end[0], ext_end[1], ext_end[2], 1)
        
        ext_obj = bpy.data.objects.new(f'{dim_name}_ext{i}', ext_curve)
        bpy.context.scene.collection.objects.link(ext_obj)
        # ext_curve.bevel_depth = 0.008  # Previous: thicker/stronger
        ext_curve.bevel_depth = DIMENSION_LINE_BEVEL
        ext_curve.use_fill_caps = True
        # ext_obj.color = (0.0, 0.0, 0.0, 1.0)  # Previous: black
        ext_obj.color = ANNOTATION_COLOR
        created_objects.append(ext_obj)
    
    # Create measurement text
    mid_x = (start_offset[0] + end_offset[0]) / 2
    mid_y = (start_offset[1] + end_offset[1]) / 2
    
    # Format distance (show in meters with 2 decimal places)
    text_str = f"{distance:.2f}m"
    
    text_data = bpy.data.curves.new(f'{dim_name}_text', type='FONT')
    text_data.body = text_str
    text_data.size = text_size
    text_data.resolution_u = 24  # Smoother numeric/text glyph curves
    text_data.fill_mode = 'FRONT'
    text_data.align_x = 'CENTER'
    text_data.align_y = 'CENTER'
    
    text_obj = bpy.data.objects.new(f'{dim_name}_text', text_data)
    bpy.context.scene.collection.objects.link(text_obj)
    
    # Position text slightly offset from dimension line
    text_offset_dist = 0.15
    if is_horizontal:
        text_loc = (mid_x, mid_y + (text_offset_dist if offset > 0 else -text_offset_dist), z_height)
    else:
        text_loc = (mid_x + (text_offset_dist if offset > 0 else -text_offset_dist), mid_y, z_height)
    
    text_obj.location = text_loc
    text_obj.show_in_front = True
    # text_obj.color = (0.0, 0.0, 0.0, 1.0)  # Previous: black
    text_obj.color = ANNOTATION_COLOR
    created_objects.append(text_obj)
    
    # Apply black material to all dimension objects
    if "Dimension_Material" not in bpy.data.materials:
        mat = bpy.data.materials.new(name="Dimension_Material")
        if mat.node_tree and "Principled BSDF" in mat.node_tree.nodes:
            # mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0, 0, 0, 1)  # Previous: black
            mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = ANNOTATION_COLOR
    
    dim_mat = bpy.data.materials.get("Dimension_Material")
    for obj in created_objects:
        if hasattr(obj.data, 'materials'):
            if len(obj.data.materials) == 0:
                obj.data.materials.append(dim_mat)
            else:
                obj.data.materials[0] = dim_mat
    
    print(f"✓ Dimension: {text_str} from {start} to {end}")
    return created_objects


def show_ground_floor_plan(option=1, hide_site_elements=True):
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
    north_wall = bpy.data.objects.get('MD_GF_NorthWall')
    if north_wall:
        print(f"North wall location: {north_wall.location}")
        print(f"North wall dimensions (scale): {north_wall.scale}")
        bbox = north_wall.bound_box
        min_x = min([v[0] for v in bbox])
        max_x = max([v[0] for v in bbox])
        min_y = min([v[1] for v in bbox])
        max_y = max([v[1] for v in bbox])
        print(f"North wall bounding box: X({min_x:.2f} to {max_x:.2f}), Y({min_y:.2f} to {max_y:.2f})")
    
    south_wall = bpy.data.objects.get('MD_GF_SouthWall')
    if south_wall:
        print(f"South wall location: {south_wall.location}")
    
    print(f"\nCamera BP_Ground_Floor location: {bpy.data.objects['BP_Ground_Floor'].location}")
    print("-"*60 + "\n")
    
    # Switch to ground floor camera
    switch_to_camera('BP_Ground_Floor')
    set_blueprint_camera_visibility('BP_Ground_Floor')

    # Ensure no helper object stays selected (selected camera draws orange X frame).
    if bpy.context.view_layer.objects.active is not None:
        bpy.context.view_layer.objects.active = None
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

    view_through_camera()

    # Restore any image empties hidden by older script runs.
    restore_image_reference_empties()
    # Hide only AREA light helper gizmos that look like a big X rectangle.
    hide_area_light_helpers()
    
    # Create white background plane
    create_white_background_plane()
    
    print("Applying section cut to reveal interior walls...")
    apply_section_to_all_objects(1.7, hide_site_elements)  # Slightly higher to avoid deck edge issues

    # Clean up old labels so floor-specific labels do not accumulate.
    cleanup_labels()
    
    # Add sample labels (customize these for your actual rooms)
    print("\nAdding room labels...")
    # Example labels - adjust coordinates to match your building layout
    # Using Z at cut height so labels are visible
    create_room_label('GROUND FLOOR', (-2, -2, 1.3), size=0.4)
    create_room_label('Dining', (-2, 0, 1.3), size=0.4)
    create_room_label('Bathroom', (+3.6, -3.1, 1.3), size=0.4)
    create_room_label('Guest\nbedroom', (+3.5, 0, 1.3), size=0.4)

    if option == 1:
        create_room_label('Kitchen', (-0.8, -3, 1.3), size=0.4)
    if option == 2:
        create_room_label('Kitchen', (-2.8, -3, 1.3), size=0.4)
        create_room_label('Entrance', (-0.8, -4.0, 1.3), size=0.4)
    if option == 3:
        create_room_label('Kitchen', (-2.8, -3, 1.3), size=0.4)
        create_room_label('Hall', (1.2, -3, 1.3), size=0.4)
    if option == 4:
        create_room_label('Kitchen', (-2.8, -3.3, 1.3), size=0.4)
        create_room_label('Utility', (1.8, -5.5, 1.3), size=0.4)

    
    # Clean up old dimension lines (in case names were changed)
    cleanup_dimensions()
    
    # Add sample dimension lines
    print("\nAdding dimension lines...")
    # Example measurements - adjust to match your actual wall positions
    # Format: create_dimension_line((x1, y1), (x2, y2), offset, text_size, z_height, name)
    # north face
    create_dimension_line((-4.8, 2.0), (4.8, 2.0), offset=1.4, text_size=0.3, z_height=1.3, name_suffix="north_wall")
    create_dimension_line((-4.65, 1.5), (0.65, 1.5), offset=1.4, text_size=0.3, z_height=1.3, name_suffix="dining_width")
    create_dimension_line((0.75, 1.5), (1.35, 1.5), offset=1.4, text_size=0.3, z_height=1.3, name_suffix="gb_wardrobe_width")
    create_dimension_line((1.45, 1.5), (4.65, 1.5), offset=1.4, text_size=0.3, z_height=1.3, name_suffix="gb_eastwest_width")

    # east face
    create_dimension_line((4.85, 2.65), (4.85, -4.65), offset=2.2, text_size=0.3, z_height=1.3, name_suffix="east_wall")
    create_dimension_line((4.85, 1.5), (4.85, -4.5), offset=1.4, text_size=0.3, z_height=1.3, name_suffix="northsouth_length")
    create_dimension_line((4.85, 1.5), (4.85, -1.75), offset=0.6, text_size=0.3, z_height=1.3, name_suffix="gb_northsouth_length")
    create_dimension_line((4.85, -1.85), (4.85, -4.5), offset=0.6, text_size=0.3, z_height=1.3, name_suffix="bath_northsouth_length")

    if option == 4:
        create_dimension_line((3.2, -4.65), (3.2, -6.5), offset=2.2, text_size=0.3, z_height=1.3, name_suffix="utility_northsouth_length")
        create_dimension_line((-4.8, -4.7), (-1.6, -4.7), offset=-2.2, text_size=0.3, z_height=1.3, name_suffix="porchdeck_eastwest_length")
        create_dimension_line((-1.45, -6.5), (0.75, -6.5), offset=-0.4, text_size=0.3, z_height=1.3, name_suffix="entrance_eastwest_length")
        create_dimension_line((0.85, -6.5), (2.95, -6.5), offset=-0.4, text_size=0.3, z_height=1.3, name_suffix="utility_eastwest_length")
        create_dimension_line((-1.6, -6.5), (3.1, -6.5), offset=-0.9, text_size=0.3, z_height=1.3, name_suffix="porch_eastwest_length")


    print("\n" + "="*60)
    print("✓ GROUND FLOOR PLAN READY!")
    print("="*60)
    print("\nWhat you should see:")
    print("  - White background with black edge lines (no shadows)")
    print("  - All walls, partitions, and rooms visible as cross-section")
    print("  - Windows and doors visible as openings")
    print("  - Geometry above 1.3m height is cut away")
    print("  - 'GROUND FLOOR' label visible in center")
    print("  - Dimension lines showing measurements")
    print("\nTo add room labels:")
    print("  create_room_label('Kitchen', (x, y, 1.3), size=0.5)")
    print("  create_room_label('Living Room', (x, y, 1.3), size=0.5)")
    print("\nTo add dimension lines:")
    print("  create_dimension_line((x1, y1), (x2, y2), offset=0.5, text_size=0.25, z_height=1.3, name_suffix='name')")
    print("  - offset: distance from measured edge (positive=outward)")
    print("  - Works automatically for horizontal and vertical measurements")
    print("\nNote: Adjust coordinates to match your actual wall/room positions")
    print("="*60)


def show_first_floor_plan(option=1, hide_site_elements=True):
    """
    ONE-COMMAND setup for first floor plan view.
    Switches camera, applies section cutting, and adds default labels.
    """
    print("\n" + "="*60)
    print("Setting up FIRST FLOOR PLAN VIEW")
    print("="*60 + "\n")
    
    # Switch to first floor camera
    switch_to_camera('BP_First_Floor')
    set_blueprint_camera_visibility('BP_First_Floor')
    view_through_camera()

    # Restore any image empties hidden by older script runs.
    restore_image_reference_empties()
    # Hide only AREA light helper gizmos that look like a big X rectangle.
    hide_area_light_helpers()
    
    # Apply section cutting at 4.0m
    print("Applying section cut to reveal interior walls...")
    apply_section_to_all_objects(4.0, hide_site_elements)

    # Clean up old labels so floor-specific labels do not accumulate.
    cleanup_labels()
    
    # Add sample labels
    print("\nAdding room labels...")
    create_room_label('FIRST FLOOR', (-2, -2, 3.8), size=0.4)
    create_room_label('Master\nbedroom', (+3.4, 0, 3.8), size=0.4)
    create_room_label('Living', (-2, 0, 3.8), size=0.4)

    if option == 1:
        create_room_label('Office', (-1, -2, 3.8), size=0.4)

    if option == 3:
        create_room_label('HWC', (0.2, -1.0, 3.8), size=0.3)
        create_room_label('sleep\ncave\n2mx1m', (0.1, 0.7, 3.8), size=0.3)

    #if option == 4:
    #    create_room_label('HWC', (0.2, -0.8, 3.8), size=0.3)

    
    # Clean up old dimension lines (in case names were changed)
    cleanup_dimensions()
    
    # Add sample dimension lines
    print("\nAdding dimension lines...")
    # Example measurements - adjust to match your actual wall positions
    # Format: create_dimension_line((x1, y1), (x2, y2), offset, text_size, z_height, name)
    create_dimension_line((-4.8, 2.5), (4.8, 2.5), offset=0.9, text_size=0.3, z_height=3.8, name_suffix="north_wall")

    create_dimension_line((4.8, 2.65), (4.8, -4.65), offset=1.4, text_size=0.3, z_height=3.8, name_suffix="east_wall")
    create_dimension_line((4.8, 2.65), (4.8, 1.65), offset=0.6, text_size=0.3, z_height=3.8, name_suffix="balcony_northsouth_length")
    create_dimension_line((4.8, 1.5), (4.8, -2.4), offset=0.6, text_size=0.3, z_height=3.8, name_suffix="mb_northsouth_length")
    create_dimension_line((4.8, -2.5), (4.8, -4.5), offset=0.6, text_size=0.3, z_height=3.8, name_suffix="bath_northsouth_length")
    create_dimension_line((2.65, -4.65), (4.65, -4.65), offset=-0.4, text_size=0.3, z_height=3.8, name_suffix="bath_eastwest_length")

    if option == 1 or option == 2:
        create_dimension_line((0.3, 2.5), (4.3, 2.5), offset=0.4, text_size=0.3, z_height=3.8, name_suffix="mb_width")
        create_dimension_line((-4.35, 2.5), (0.2, 2.5), offset=0.4, text_size=0.3, z_height=3.8, name_suffix="living_width")
    if option == 3:
        create_dimension_line((0.8, 1.5), (4.3, 1.5), offset=1.4, text_size=0.3, z_height=3.8, name_suffix="mb_width")
        create_dimension_line((-4.35, 1.5), (0.7, 1.5), offset=1.4, text_size=0.3, z_height=3.8, name_suffix="living_width")
    if option == 4:
        create_dimension_line((-4.65, 1.7), (1.05, 1.7), offset=1.2, text_size=0.3, z_height=3.8, name_suffix="living_width")
        #create_dimension_line((-0.2, 2.5), (0.7, 2.5), offset=0.4, text_size=0.3, z_height=3.8, name_suffix="cave_width")
        create_dimension_line((1.15, 1.7), (4.65, 1.7), offset=1.2, text_size=0.3, z_height=3.8, name_suffix="mb_eastwest_width")


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
    set_blueprint_camera_visibility('BP_Roof_Plan')
    view_through_camera()
    apply_section_to_all_objects(7.5)
    cleanup_labels()
    
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
    set_blueprint_camera_visibility('BP_Site_Plan')
    view_through_camera()
    remove_section_from_all_objects()
    cleanup_labels()
    
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


def set_blueprint_camera_visibility(active_camera_name):
    """
    Show only the active blueprint camera object and hide other blueprint
    camera objects in viewport. This removes large ortho camera frames (X box)
    from floor plan views.
    """
    camera_names = (
        'BP_Ground_Floor',
        'BP_First_Floor',
        'BP_Roof_Plan',
        'BP_Site_Plan',
    )

    for cam_name in camera_names:
        cam_obj = bpy.data.objects.get(cam_name)
        if cam_obj is None:
            continue
        should_hide = (cam_name != active_camera_name)
        cam_obj.hide_viewport = should_hide
        # Per-view-layer hide is more reliable in viewport than hide_viewport alone.
        try:
            cam_obj.hide_set(should_hide)
        except Exception:
            pass

    # Clear selection so hidden cameras do not keep selected outlines/guides.
    for obj in bpy.context.selected_objects:
        obj.select_set(False)


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
    
    # Ground Floor Plan - cuts at 1.7m 
    cameras['ground'] = create_blueprint_camera(
        name="BP_Ground_Floor",
        location=(center_x, center_y, 20),
        clip_height=1.7,
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
    set_blueprint_camera_visibility('BP_Ground_Floor')
    
    # Step 4: Switch viewport to camera view
    view_through_camera()
    
    print("\n" + "="*60)
    print("Blueprint view setup complete!")
    print("="*60)
    print("\nCreated Cameras:")
    print("  1. BP_Ground_Floor (cuts at 1.7m)")
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
