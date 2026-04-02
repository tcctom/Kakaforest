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
    BED_WIDTH = 2.0  # meters (X-direction)
    BED_LENGTH = 1.8  # meters (Y-direction)
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
    pillow1.data.materials.append(create_material("Pillow", (0.65, 0.78, 0.92, 1)))
    
    # Right pillow
    bpy.ops.mesh.primitive_cube_add(location=(pillow_x, bed_y + 0.4, pillow_z))
    pillow2 = bpy.context.active_object
    pillow2.name = "WetWing_Pillow2"
    pillow2.scale = (pillow_depth/2, pillow_width/2, PILLOW_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    pillow2.data.materials.append(create_material("Pillow", (0.65, 0.78, 0.92, 1)))
    
    # Kitchen Benchtop - Against interior wall (east side), south end
    BENCHTOP_WIDTH = 2.4  # meters (Y-direction, along the wall)
    BENCHTOP_DEPTH = 0.6  # meters (X-direction, extending from wall)
    BENCHTOP_HEIGHT = 0.9  # meters (standard benchtop height)
    BENCHTOP_THICKNESS = 0.04  # meters (top surface thickness)
    INTERIOR_WALL_THICKNESS = 0.11  # meters
    
    # Position: East side of interior wall (negative X), toward south end
    # Interior wall center is at ox, east face is at ox - INTERIOR_WALL_THICKNESS/2
    # Position benchtop 1m from south wall
    benchtop_x = ox - INTERIOR_WALL_THICKNESS/2 - BENCHTOP_DEPTH/2  # East side of interior wall
    benchtop_y = oy + D/2 - 1.0 - BENCHTOP_WIDTH/2  # 1m from south wall
    benchtop_z = oz + BENCHTOP_HEIGHT/2  # Half height above floor
    
    # Benchtop base (cabinet)
    bpy.ops.mesh.primitive_cube_add(location=(benchtop_x, benchtop_y, benchtop_z))
    benchtop_base = bpy.context.active_object
    benchtop_base.name = "WetWing_Benchtop_Base"
    benchtop_base.scale = (BENCHTOP_DEPTH/2, BENCHTOP_WIDTH/2, BENCHTOP_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    benchtop_base.data.materials.append(create_material("KitchenCabinet", (0.85, 0.85, 0.8, 1)))
    
    # Benchtop surface (slightly overhanging)
    benchtop_top_depth = BENCHTOP_DEPTH + 0.05  # Slight overhang
    benchtop_top_width = BENCHTOP_WIDTH + 0.05  # Slight overhang
    benchtop_top_z = oz + BENCHTOP_HEIGHT + BENCHTOP_THICKNESS/2
    
    bpy.ops.mesh.primitive_cube_add(location=(benchtop_x, benchtop_y, benchtop_top_z))
    benchtop_top = bpy.context.active_object
    benchtop_top.name = "WetWing_Benchtop_Surface"
    benchtop_top.scale = (benchtop_top_depth/2, benchtop_top_width/2, BENCHTOP_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Benchtop color options:
    benchtop_top.data.materials.append(create_material("Countertop", (0.65, 0.5, 0.35, 1)))  # Warm Bamboo/Timber (current)
    # benchtop_top.data.materials.append(create_material("Countertop", (0.4, 0.25, 0.18, 1)))  # Rich Walnut
    # benchtop_top.data.materials.append(create_material("Countertop", (0.88, 0.85, 0.8, 1)))  # Light Stone/Composite
    # benchtop_top.data.materials.append(create_material("Countertop", (0.7, 0.55, 0.4, 1)))  # Natural Oak
