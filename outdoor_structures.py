import bpy  # type: ignore

def build_pavers_east(origin=(0, 0, 0)):
    """
    Build a paved area extending east from the red cottage.
    Pavers extend from x -3.1 to x -7.1 (4m east) and y +2.1 to y -2.1 (4.2m north-south).
    
    Args:
        origin: Tuple (x, y, z) for the reference point
    """
    ox, oy, oz = origin
    
    # Paver dimensions
    width_x = 4.0  # 4m in X direction (from -3.1 to -7.1)
    depth_y = 4.2  # 4.2m in Y direction (from +2.1 to -2.1)
    thickness = 0.05  # 5cm thick pavers
    
    # Center position: midpoint between the bounds
    center_x = ox - 5.1  # Midpoint of -3.1 and -7.1
    center_y = oy + 0.0  # Midpoint of +2.1 and -2.1
    center_z = oz + thickness / 2  # Half thickness above ground
    
    # Create paver plane
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(center_x, center_y, center_z)
    )
    pavers = bpy.context.active_object
    pavers.name = "Pavers_East"
    pavers.scale = (width_x, depth_y, thickness)
    bpy.ops.object.transform_apply(scale=True)
    
    # Create paver material
    paver_mat = bpy.data.materials.get("PaverStone") or bpy.data.materials.new(name="PaverStone")
    paver_mat.use_nodes = True
    principled = paver_mat.node_tree.nodes["Principled BSDF"]
    principled.inputs[0].default_value = (0.6, 0.55, 0.5, 1)  # Light gray/beige stone color
    principled.inputs[7].default_value = 0.8  # Roughness
    pavers.data.materials.append(paver_mat)
    
    return pavers

def build_water_tank(origin=(0, 0, 0)):
    """
    Build a 25000 liter cylindrical water tank.
    
    Args:
        origin: Tuple (x, y, z) for the base center of the tank
    """
    ox, oy, oz = origin
    
    # Tank specifications
    TANK_DIAMETER = 3.5
    TANK_HEIGHT = 2.5
    
    # Create cylindrical tank
    bpy.ops.mesh.primitive_cylinder_add(
        radius=TANK_DIAMETER/2, 
        depth=TANK_HEIGHT,
        location=(ox, oy, oz + TANK_HEIGHT/2)
    )
    water_tank = bpy.context.active_object
    water_tank.name = "WaterTank_25000L"
    
    # Create metal tank material
    tank_mat = bpy.data.materials.get("TankMetal") or bpy.data.materials.new(name="TankMetal")
    tank_mat.use_nodes = True
    principled = tank_mat.node_tree.nodes["Principled BSDF"]
    principled.inputs[0].default_value = (0.7, 0.7, 0.75, 1)  # Light gray metallic color
    principled.inputs[4].default_value = 0.8  # Metallic
    principled.inputs[7].default_value = 0.3  # Roughness
    water_tank.data.materials.append(tank_mat)
    
    return water_tank
