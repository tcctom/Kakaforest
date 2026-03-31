import bpy  # type: ignore

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_wet_wing_furniture(origin=(0,0,0), building_width=6.0, building_depth=6.0, exterior_wall_thickness=0.15):
    """
    Add furniture to the Potius Wet Wing.
    
    Args:
        origin: (x, y, z) tuple for building origin
        building_width: Building width in meters (X-direction)
        building_depth: Building depth in meters (Y-direction)
        exterior_wall_thickness: Thickness of exterior walls in meters
    """
    ox, oy, oz = origin
    W, D = building_width, building_depth
    EXTERIOR_WALL_THICKNESS = exterior_wall_thickness
    
    # King Bed - Pillows against west wall, 1m from north wall
    BED_WIDTH = 1.8  # meters (X-direction)
    BED_LENGTH = 2.0  # meters (Y-direction)
    BED_HEIGHT = 0.5  # meters (mattress height off floor)
    PILLOW_HEIGHT = 0.2  # meters
    
    # Position: West wall is at ox + W/2, north wall is at oy - D/2
    # Bed centered 1m from north wall means bed center at: oy - D/2 + 1.0 + BED_LENGTH/2
    bed_x = ox + W/2 - EXTERIOR_WALL_THICKNESS - BED_WIDTH/2  # Against west wall, inward by wall thickness
    bed_y = oy - D/2 + 1.0 + BED_LENGTH/2  # 1m from north wall + half bed length
    bed_z = oz + BED_HEIGHT/2  # Half bed height above floor
    
    # Mattress
    bpy.ops.mesh.primitive_cube_add(location=(bed_x, bed_y, bed_z))
    bed = bpy.context.active_object
    bed.name = "WetWing_Bed"
    bed.scale = (BED_WIDTH/2, BED_LENGTH/2, BED_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    bed.data.materials.append(create_material("Bedding", (0.9, 0.9, 0.85, 1)))
    
    # Pillows (two pillows against west wall)
    pillow_width = 0.6
    pillow_depth = 0.4
    pillow_z = bed_z + BED_HEIGHT/2 + PILLOW_HEIGHT/2
    pillow_x = ox + W/2 - EXTERIOR_WALL_THICKNESS - pillow_depth/2  # Against west wall
    
    # Left pillow
    bpy.ops.mesh.primitive_cube_add(location=(pillow_x, bed_y - 0.4, pillow_z))
    pillow1 = bpy.context.active_object
    pillow1.name = "WetWing_Pillow1"
    pillow1.scale = (pillow_depth/2, pillow_width/2, PILLOW_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    pillow1.data.materials.append(create_material("Bedding", (0.9, 0.9, 0.85, 1)))
    
    # Right pillow
    bpy.ops.mesh.primitive_cube_add(location=(pillow_x, bed_y + 0.4, pillow_z))
    pillow2 = bpy.context.active_object
    pillow2.name = "WetWing_Pillow2"
    pillow2.scale = (pillow_depth/2, pillow_width/2, PILLOW_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    pillow2.data.materials.append(create_material("Bedding", (0.9, 0.9, 0.85, 1)))
