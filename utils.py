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

def add_window(wall_name, position, width=1.2, height=1.4, depth=0.5, frame_thickness=0.05):
    """
    Adds a window to a wall by cutting a hole and adding glass.
    
    Args:
        wall_name: Name of the wall object to cut into
        position: (x, y, z) world position for window center on OUTER wall face
        width: Window width in meters (default 1.2m)
        height: Window height in meters (default 1.4m) 
        depth: Wall depth to cut through (default 0.5m)
        frame_thickness: Thickness of window frame (default 0.05m)
    """
    wall = bpy.data.objects.get(wall_name)
    if not wall:
        print(f"Wall '{wall_name}' not found")
        return
    
    x, y, z = position
    
    # Position adjustments - offset inward from wall face
    # The position given is the outer wall face, so offset by depth/2 to get center
    y_offset = depth / 2  # Offset inward from the face
    
    # Create window opening (cutter) - positioned at center of wall thickness
    bpy.ops.mesh.primitive_cube_add(location=(x, y + y_offset, z))
    cutter = bpy.context.active_object
    cutter.name = f"Window_Opening_{wall_name}"
    cutter.dimensions = (width, depth * 1.1, height)  # Slightly oversized to ensure clean cut
    
    # Add Boolean modifier to wall (use EXACT solver for clean cuts)
    bool_mod = wall.modifiers.new(name="Window_Cut", type='BOOLEAN')
    bool_mod.object = cutter
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.solver = 'EXACT'
    
    # Move cutter to separate collection and hide it
    cutter.hide_viewport = True
    cutter.hide_render = True
    
    # Create window frame (painted wood) - positioned slightly inward
    # Use most of the depth for the frame so it's visible
    frame_depth = depth * 0.9
    bpy.ops.mesh.primitive_cube_add(location=(x, y + y_offset, z))
    frame = bpy.context.active_object
    frame.name = f"Window_Frame_{wall_name}"
    frame.dimensions = (width, frame_depth, height)
    
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
    bpy.ops.mesh.primitive_cube_add(location=(x, y + y_offset, z))
    frame_cutter = bpy.context.active_object
    frame_cutter.dimensions = (width - frame_thickness*2, frame_depth + 0.04, height - frame_thickness*2)
    
    bool_mod = frame.modifiers.new(name="Frame_Opening", type='BOOLEAN')
    bool_mod.object = frame_cutter
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.solver = 'EXACT'
    
    frame_cutter.hide_viewport = True
    frame_cutter.hide_render = True
    
    # Create glass pane (transparent) - centered in the opening
    bpy.ops.mesh.primitive_cube_add(location=(x, y + y_offset, z))
    glass = bpy.context.active_object
    glass.name = f"Window_Glass_{wall_name}"
    glass.dimensions = (width - frame_thickness*2, 0.004, height - frame_thickness*2)
    
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


