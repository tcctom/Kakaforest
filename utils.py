import math

import bpy  # type: ignore

def apply_shadowclad_grooves(target_name, width, height, spacing=0.150):
    """
    Creates vertical grooves by 'Difference' booleans across all four wall faces.
    Assumes target is a rectangular box centered at its location.
    width = X dimension, depth = Y dimension.
    """
    wall = bpy.data.objects.get(target_name)
    if not wall: return

    groove_depth = 0.02  # 20mm groove depth
    depth = wall.dimensions.y  # Depth in Y direction
    
    all_cutters = []
    
    # North and South faces (grooves run along X axis)
    for face_name, y_offset in [("North", -depth/2), ("South", depth/2)]:
        num_grooves = int(width / spacing)
        start_x = wall.location.x - (width / 2) + (spacing / 2)
        
        for i in range(num_grooves):
            bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
            cutter = bpy.context.active_object
            cutter.scale = (0.005, groove_depth/2, height/2)
            bpy.ops.object.transform_apply(scale=True)
            
            # Position on North or South face
            y_sign = -1 if face_name == "North" else 1
            cutter.location = (
                start_x + (i * spacing), 
                wall.location.y + y_offset + y_sign * (groove_depth/2), 
                wall.location.z
            )
            all_cutters.append(cutter)
    
    # East and West faces (grooves run along Y axis)
    for face_name, x_offset in [("West", -width/2), ("East", width/2)]:
        num_grooves = int(depth / spacing)
        start_y = wall.location.y - (depth / 2) + (spacing / 2)
        
        for i in range(num_grooves):
            bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
            cutter = bpy.context.active_object
            cutter.scale = (groove_depth/2, 0.005, height/2)
            bpy.ops.object.transform_apply(scale=True)
            
            # Position on West or East face
            x_sign = -1 if face_name == "West" else 1
            cutter.location = (
                wall.location.x + x_offset + x_sign * (groove_depth/2), 
                start_y + (i * spacing), 
                wall.location.z
            )
            all_cutters.append(cutter)

    # Join all cutters into one object for a single Boolean operation
    bpy.ops.object.select_all(action='DESELECT')
    for c in all_cutters:
        c.select_set(True)
    bpy.context.view_layer.objects.active = all_cutters[0]
    bpy.ops.object.join()
    
    master_cutter = bpy.context.active_object
    master_cutter.name = "Shadowclad_Cutters"

    # Apply the Boolean to the Wall
    bool_mod = wall.modifiers.new(name="Shadowclad_Grooves", type='BOOLEAN')
    bool_mod.object = master_cutter
    bool_mod.operation = 'DIFFERENCE'
    
    # Hide the cutter
    master_cutter.hide_viewport = True
    master_cutter.hide_render = True

def add_opening(
    wall_name,
    position,
    width=1.2,
    height=1.4,
    depth=0.5,
    axis='Y',
    inward_offset=None,
    position_mode='center',
    opening_name_prefix='Opening',
    modifier_name='Opening_Cut',
):
    """
    Cuts a rectangular opening in a wall.

    Args:
        wall_name: Name of the wall object to cut into.
        position: Opening center when position_mode='center', or bottom center when 'bottom'.
        width: Opening width in meters.
        height: Opening height in meters.
        depth: Wall depth to cut through.
        axis: 'Y' for north/south walls, 'X' for east/west walls.
        inward_offset: '+X', '-X', '+Y', '-Y' or None for automatic inward placement.
        position_mode: 'center' or 'bottom'.
        opening_name_prefix: Prefix for created cutter object name.
        modifier_name: Boolean modifier name on the target wall.
    """
    wall = bpy.data.objects.get(wall_name)
    if not wall:
        print(f"Wall '{wall_name}' not found")
        return None

    x, y, z = position
    if position_mode == 'bottom':
        z = z + height / 2

    if axis == 'Y':
        if inward_offset:
            y_off = depth / 2 if inward_offset == '+Y' else -depth / 2
        else:
            y_off = depth / 2
        center_offset = (x, y + y_off, z)
        cutter_dims = (width, depth * 1.1, height)
    else:
        if inward_offset:
            x_off = depth / 2 if inward_offset == '+X' else -depth / 2
        elif 'West' in wall_name:
            x_off = depth / 2
        elif 'East' in wall_name:
            x_off = -depth / 2
        else:
            x_off = depth / 2 if x < wall.location.x else -depth / 2

        center_offset = (x + x_off, y, z)
        cutter_dims = (depth * 1.1, width, height)

    bpy.ops.mesh.primitive_cube_add(location=center_offset)
    cutter = bpy.context.active_object
    cutter.name = f"{opening_name_prefix}_{wall_name}"
    cutter.dimensions = cutter_dims

    bool_mod = wall.modifiers.new(name=modifier_name, type='BOOLEAN')
    bool_mod.object = cutter
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.solver = 'EXACT'

    cutter.hide_viewport = True
    cutter.hide_render = True

    return {
        'wall': wall,
        'cutter': cutter,
        'center_offset': center_offset,
        'cutter_dims': cutter_dims,
        'axis': axis,
    }

def add_window(wall_name, position, width=1.2, height=1.4, depth=0.5, frame_thickness=0.05, axis='Y', inward_offset=None):
    """
    Adds a window to a wall by cutting a hole and adding glass.
    
    Args:
        wall_name: Name of the wall object to cut into
        position: (x, y, z) world position for window center on OUTER wall face
        width: Window width in meters (default 1.2m)
        height: Window height in meters (default 1.4m) 
        depth: Wall depth to cut through (default 0.5m)
        frame_thickness: Thickness of window frame (default 0.05m)
        axis: 'Y' for north/south walls (default), 'X' for east/west walls
        inward_offset: Override auto-detection: '+X', '-X', '+Y', '-Y' or None for auto
    """
    opening_data = add_opening(
        wall_name,
        position,
        width=width,
        height=height,
        depth=depth,
        axis=axis,
        inward_offset=inward_offset,
        position_mode='center',
        opening_name_prefix='Window_Opening',
        modifier_name='Window_Cut',
    )
    if not opening_data:
        return

    center_offset = opening_data['center_offset']

    # Determine frame and glass orientation based on wall axis
    if axis == 'Y':
        frame_dims = (width, depth * 0.9, height)
        frame_cutter_dims = (width - frame_thickness*2, depth * 0.9 + 0.04, height - frame_thickness*2)
        glass_dims = (width - frame_thickness*2, 0.004, height - frame_thickness*2)
    else:
        frame_dims = (depth * 0.9, width, height)
        frame_cutter_dims = (depth * 0.9 + 0.04, width - frame_thickness*2, height - frame_thickness*2)
        glass_dims = (0.004, width - frame_thickness*2, height - frame_thickness*2)
    
    # Create window frame (painted wood) - positioned slightly inward
    # Use most of the depth for the frame so it's visible
    bpy.ops.mesh.primitive_cube_add(location=center_offset)
    frame = bpy.context.active_object
    frame.name = f"Window_Frame_{wall_name}"
    frame.dimensions = frame_dims
    
    # Create frame material (painted wood - white/cream)
    frame_mat = bpy.data.materials.get("WindowFrame") or bpy.data.materials.new(name="WindowFrame")
    frame_mat.use_nodes = True
    bsdf = frame_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.9, 1.0)  # Off-white
        bsdf.inputs['Roughness'].default_value = 0.3
    
    if not frame.data.materials:
        frame.data.materials.append(frame_mat)
    else:
        frame.data.materials[0] = frame_mat
    
    # Cut hole in frame for glass  
    bpy.ops.mesh.primitive_cube_add(location=center_offset)
    frame_cutter = bpy.context.active_object
    frame_cutter.dimensions = frame_cutter_dims
    
    bool_mod = frame.modifiers.new(name="Frame_Opening", type='BOOLEAN')
    bool_mod.object = frame_cutter
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.solver = 'EXACT'
    
    frame_cutter.hide_viewport = True
    frame_cutter.hide_render = True
    
    # Create glass pane (transparent) - centered in the opening
    bpy.ops.mesh.primitive_cube_add(location=center_offset)
    glass = bpy.context.active_object
    glass.name = f"Window_Glass_{wall_name}"
    glass.dimensions = glass_dims
    
    # Glass material with proper transparency
    glass_mat = bpy.data.materials.get("Glass") or bpy.data.materials.new(name="Glass")
    glass_mat.use_nodes = True
    glass_mat.blend_method = 'BLEND'  # Enable transparency
    #glass_mat.shadow_method = 'HASHED'  # Better shadows for transparent materials
    
    # Configure Principled BSDF for glass
    bsdf = glass_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.8, 0.95, 1.0, 1.0)  # Slight blue tint
        bsdf.inputs['Roughness'].default_value = 0.0  # Smooth glass
        bsdf.inputs['IOR'].default_value = 1.52  # Glass IOR
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Alpha'].default_value = 0.3  # Semi-transparent
        
        # Set transmission for transparency (Blender 4.0+ uses 'Transmission Weight')
        transmission_input = bsdf.inputs.get('Transmission Weight') or bsdf.inputs.get('Transmission')
        if transmission_input:
            transmission_input.default_value = 1.0  # Full glass transmission
    
    # Ensure viewport display shows transparency
    glass.show_transparent = True
    glass.display_type = 'TEXTURED'
    
    if not glass.data.materials:
        glass.data.materials.append(glass_mat)
    else:
        glass.data.materials[0] = glass_mat
    
    return (frame, glass)

def create_corrugated_iron_material():
    """
    Creates a black corrugated iron material for roofs.
    Returns the material object.
    """
    mat = bpy.data.materials.get("CorrugatedIron") or bpy.data.materials.new(name="CorrugatedIron")
    mat.use_nodes = True
    
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)  # Nearly black
        bsdf.inputs['Metallic'].default_value = 0.9  # High metallic for iron
        bsdf.inputs['Roughness'].default_value = 0.4  # Some weathering/texture
        bsdf.inputs['Specular IOR Level'].default_value = 0.5  # Moderate reflections
    
    return mat


def _get_white_four_panel_door_material(axis='Y'):
    """
    Returns a painted white door leaf material with a procedural 4-panel look.
    Axis-specific variants keep panel direction correct for both Y and X walls.
    """
    axis_key = 'Y' if axis == 'Y' else 'X'
    mat_name = f"DoorLeaf_White_4Panel_{axis_key}"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    texcoord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    combine_xyz = nodes.new(type='ShaderNodeCombineXYZ')
    brick = nodes.new(type='ShaderNodeTexBrick')
    ramp = nodes.new(type='ShaderNodeValToRGB')
    bump = nodes.new(type='ShaderNodeBump')

    # Simple layout for readability in the shader editor.
    texcoord.location = (-900, 0)
    mapping.location = (-720, 0)
    sep_xyz.location = (-560, -180)
    combine_xyz.location = (-380, -20)
    brick.location = (-180, 20)
    ramp.location = (40, -120)
    bump.location = (240, -120)
    bsdf.location = (440, 20)
    output.location = (650, 20)

    # Use generated coordinates so the panel texture fits each door object bounds.
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0)

    # Align width/height mapping to the visible door face for each axis.
    if axis_key == 'Y':
        # Door width is local X; height is local Z.
        links.new(sep_xyz.outputs['X'], combine_xyz.inputs['X'])
        links.new(sep_xyz.outputs['Z'], combine_xyz.inputs['Y'])
    else:
        # Door width is local Y; height is local Z.
        links.new(sep_xyz.outputs['Y'], combine_xyz.inputs['X'])
        links.new(sep_xyz.outputs['Z'], combine_xyz.inputs['Y'])

    combine_xyz.inputs['Z'].default_value = 0.0

    # Brick texture configured as 2x2 panel blocks with narrow grooves.
    brick.offset = 0.0
    brick.offset_frequency = 1
    brick.squash = 1.0
    brick.squash_frequency = 1
    brick.inputs['Scale'].default_value = 2.0
    brick.inputs['Mortar Size'].default_value = 0.03
    brick.inputs['Mortar Smooth'].default_value = 0.0
    brick.inputs['Brick Width'].default_value = 0.44
    brick.inputs['Row Height'].default_value = 0.44
    brick.inputs['Color1'].default_value = (0.98, 0.98, 0.98, 1.0)
    brick.inputs['Color2'].default_value = (0.93, 0.93, 0.93, 1.0)
    brick.inputs['Mortar'].default_value = (0.74, 0.74, 0.74, 1.0)

    # Convert panel boundaries to a subtle groove normal.
    ramp.color_ramp.elements[0].position = 0.12
    ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp.color_ramp.elements[1].position = 0.42
    ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.02
    bump.invert = True

    bsdf.inputs['Roughness'].default_value = 0.4
    bsdf.inputs['Specular IOR Level'].default_value = 0.35

    links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], sep_xyz.inputs['Vector'])
    links.new(combine_xyz.outputs['Vector'], brick.inputs['Vector'])
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(brick.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

def add_corner_trim(origin, width, depth, height, trim_width=0.15, trim_depth=0.02):
    """
    Adds white corner trim planks to all 4 exterior corners of a building.
    
    Args:
        origin: (x, y, z) tuple for building center at ground level
        width: Building width (X dimension) in meters
        depth: Building depth (Y dimension) in meters  
        height: Building height in meters
        trim_width: Width of trim plank (default 0.15m / 150mm)
        trim_depth: Depth of trim plank projecting from wall (default 0.02m / 20mm)
    """
    ox, oy, oz = origin
    
    # Create white trim material
    trim_mat = bpy.data.materials.get("WhiteTrim") or bpy.data.materials.new(name="WhiteTrim")
    trim_mat.use_nodes = True
    bsdf = trim_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)  # Pure white
        bsdf.inputs['Roughness'].default_value = 0.2  # Painted finish
    
    # Corner positions relative to origin (at building edges)
    corners = [
        ("NW", -width/2, -depth/2),
        ("NE", width/2, -depth/2),
        ("SE", width/2, depth/2),
        ("SW", -width/2, depth/2),
    ]
    
    trim_objects = []
    for corner_name, corner_x, corner_y in corners:
        bpy.ops.mesh.primitive_cube_add(location=(ox + corner_x, oy + corner_y, oz + height/2))
        trim = bpy.context.active_object
        trim.name = f"CornerTrim_{corner_name}"
        trim.scale = (trim_width/2, trim_width/2, height/2)
        bpy.ops.object.transform_apply(scale=True)
        trim.data.materials.append(trim_mat)
        trim_objects.append(trim)
    
    return trim_objects

def add_door(
    wall_name,
    position,
    width=0.9,
    height=2.1,
    depth=0.5,
    axis='Y',
    inward_offset=None,
    open_angle_degrees=90,
    hinge_side='left',
    leaf_thickness=0.04,
):
    """
    Adds a door opening and a simple hinged door leaf.
    
    Args:
        wall_name: Name of the wall object to cut into
        position: (x, y, z) world position for door bottom center at wall surface.
        width: Door width in meters.
        height: Door height in meters.
        depth: Wall depth to cut through.
        axis: 'Y' for north/south walls, 'X' for east/west walls.
        inward_offset: '+X', '-X', '+Y', '-Y' or None for automatic inward placement.
        open_angle_degrees: Door swing angle around hinge in degrees (default 90).
        hinge_side: 'left' or 'right' viewed from the outside of the wall.
        leaf_thickness: Door panel thickness in meters.
    """
    opening_data = add_opening(
        wall_name,
        position,
        width=width,
        height=height,
        depth=depth,
        axis=axis,
        inward_offset=inward_offset,
        position_mode='bottom',
        opening_name_prefix='Door_Opening',
        modifier_name='Door_Cut',
    )
    if not opening_data:
        return

    center_x, center_y, center_z = opening_data['center_offset']
    hinge_side = hinge_side.lower()

    leaf_width = max(width - 0.02, 0.05)
    leaf_height = max(height - 0.02, 0.05)
    half_width = leaf_width / 2

    bpy.ops.mesh.primitive_cube_add(location=(center_x, center_y, center_z))
    door = bpy.context.active_object
    door.name = f"Door_Leaf_{wall_name}"

    if axis == 'Y':
        door.dimensions = (leaf_width, leaf_thickness, leaf_height)
    else:
        door.dimensions = (leaf_thickness, leaf_width, leaf_height)

    theta = math.radians(open_angle_degrees)
    if hinge_side == 'right':
        theta = -theta

    if axis == 'Y':
        hinge_x = center_x - half_width if hinge_side == 'left' else center_x + half_width
        hinge_y = center_y
        dx = center_x - hinge_x
        dy = center_y - hinge_y
        rotated_dx = dx * math.cos(theta) - dy * math.sin(theta)
        rotated_dy = dx * math.sin(theta) + dy * math.cos(theta)
        door.location.x = hinge_x + rotated_dx
        door.location.y = hinge_y + rotated_dy
        door.rotation_euler[2] = theta
    else:
        hinge_x = center_x
        hinge_y = center_y - half_width if hinge_side == 'left' else center_y + half_width
        dx = center_x - hinge_x
        dy = center_y - hinge_y
        rotated_dx = dx * math.cos(theta) - dy * math.sin(theta)
        rotated_dy = dx * math.sin(theta) + dy * math.cos(theta)
        door.location.x = hinge_x + rotated_dx
        door.location.y = hinge_y + rotated_dy
        door.rotation_euler[2] = theta

    door_mat = _get_white_four_panel_door_material(axis=axis)

    if not door.data.materials:
        door.data.materials.append(door_mat)
    else:
        door.data.materials[0] = door_mat

    return opening_data['cutter']



