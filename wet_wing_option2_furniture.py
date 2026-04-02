import bpy  # type: ignore

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_wet_wing_option2_furniture(origin=(0,0,0), building_width=10.0, building_depth=6.0, exterior_wall_thickness=0.15):
    """
    Add furniture to the Potius Wet Wing Option 2 - Upper Level (60m²).
    
    This furnishes the main 10m x 6m building which is the upper sanctuary level.
    The lower level (40m²) is a separate structure created by build_under_extension.
    
    Upper Level: Great Room (kitchen, dining, lounge), Master Suite
    
    Args:
        origin: (x, y, z) tuple for building origin (already raised at z=2.4)
        building_width: Building width in meters (X-direction) - default 10.0
        building_depth: Building depth in meters (Y-direction) - default 6.0
        exterior_wall_thickness: Thickness of exterior walls in meters
    """
    ox, oy, oz = origin
    W, D = building_width, building_depth
    EXTERIOR_WALL_THICKNESS = exterior_wall_thickness
    
    # ==================== UPPER LEVEL (60m²) - This entire building ====================
    
    # === GREAT ROOM (Full North Wall - 10m) ===
    # Kitchen counter along west portion of north wall
    KITCHEN_LENGTH = 4.0  # meters along north wall
    KITCHEN_DEPTH = 0.65  # meters extending into room
    KITCHEN_HEIGHT = 0.9
    KITCHEN_TOP_THICKNESS = 0.04
    
    kitchen_x = ox + W/2 - KITCHEN_LENGTH/2  # West side of north wall
    kitchen_y = oy - D/2 + EXTERIOR_WALL_THICKNESS + KITCHEN_DEPTH/2
    kitchen_z = oz + KITCHEN_HEIGHT/2
    
    # Kitchen base cabinets
    bpy.ops.mesh.primitive_cube_add(location=(kitchen_x, kitchen_y, kitchen_z))
    kitchen_base = bpy.context.active_object
    kitchen_base.name = "WetWing2_KitchenBase"
    kitchen_base.scale = (KITCHEN_LENGTH/2, KITCHEN_DEPTH/2, KITCHEN_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    kitchen_base.data.materials.append(create_material("KitchenCabinet", (0.3, 0.25, 0.2, 1)))
    
    # Kitchen countertop
    kitchen_top_z = oz + KITCHEN_HEIGHT + KITCHEN_TOP_THICKNESS/2
    
    bpy.ops.mesh.primitive_cube_add(location=(kitchen_x, kitchen_y, kitchen_top_z))
    kitchen_top = bpy.context.active_object
    kitchen_top.name = "WetWing2_KitchenCounter"
    kitchen_top.scale = ((KITCHEN_LENGTH + 0.05)/2, (KITCHEN_DEPTH + 0.05)/2, KITCHEN_TOP_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    kitchen_top.data.materials.append(create_material("WhiteCountertop", (0.88, 0.85, 0.8, 1)))
    
    # Dining table in center of great room
    TABLE_LENGTH = 2.0
    TABLE_WIDTH = 1.0
    TABLE_HEIGHT = 0.75
    TABLE_THICKNESS = 0.05
    
    table_x = ox  # Center of room
    table_y = oy - D/2 + 2.5  # Middle of north half
    table_z = oz + TABLE_HEIGHT
    
    bpy.ops.mesh.primitive_cube_add(location=(table_x, table_y, table_z))
    table = bpy.context.active_object
    table.name = "WetWing2_DiningTable"
    table.scale = (TABLE_LENGTH/2, TABLE_WIDTH/2, TABLE_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    table.data.materials.append(create_material("OakTable", (0.65, 0.5, 0.35, 1)))
    
    # Lounge sofa facing north (view)
    SOFA_WIDTH = 2.5
    SOFA_DEPTH = 0.9
    SOFA_HEIGHT = 0.4
    SOFA_BACK_HEIGHT = 0.8
    
    sofa_x = ox - 1.5  # East side of great room
    sofa_y = oy - D/2 + 3.5
    sofa_z = oz + SOFA_HEIGHT/2
    
    # Sofa seat
    bpy.ops.mesh.primitive_cube_add(location=(sofa_x, sofa_y, sofa_z))
    sofa_seat = bpy.context.active_object
    sofa_seat.name = "WetWing2_SofaSeat"
    sofa_seat.scale = (SOFA_WIDTH/2, SOFA_DEPTH/2, SOFA_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    sofa_seat.data.materials.append(create_material("SofaFabric", (0.35, 0.45, 0.5, 1)))
    
    # Sofa back
    sofa_back_z = oz + SOFA_HEIGHT + SOFA_BACK_HEIGHT/2
    sofa_back_y = sofa_y + SOFA_DEPTH/2 - 0.1
    
    bpy.ops.mesh.primitive_cube_add(location=(sofa_x, sofa_back_y, sofa_back_z))
    sofa_back = bpy.context.active_object
    sofa_back.name = "WetWing2_SofaBack"
    sofa_back.scale = (SOFA_WIDTH/2, 0.15/2, SOFA_BACK_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    sofa_back.data.materials.append(create_material("SofaFabric", (0.35, 0.45, 0.5, 1)))
    
    # === MASTER SUITE (Upper Level SE Corner) ===
    # King bed against east wall, in SE corner
    MASTER_BED_WIDTH = 2.0  # meters (X-direction) - king bed
    MASTER_BED_LENGTH = 2.0  # meters (Y-direction)
    MASTER_BED_HEIGHT = 0.5
    
    master_bed_x = ox - W/2 + EXTERIOR_WALL_THICKNESS + MASTER_BED_WIDTH/2
    master_bed_y = oy + D/2 - EXTERIOR_WALL_THICKNESS - 1.5 - MASTER_BED_LENGTH/2
    master_bed_z = oz + MASTER_BED_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(master_bed_x, master_bed_y, master_bed_z))
    master_bed = bpy.context.active_object
    master_bed.name = "WetWing2_MasterBed"
    master_bed.scale = (MASTER_BED_WIDTH/2, MASTER_BED_LENGTH/2, MASTER_BED_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    master_bed.data.materials.append(create_material("MasterBedding", (0.25, 0.3, 0.4, 1)))
    
    # Master bedside table
    NIGHTSTAND_SIZE = 0.5
    NIGHTSTAND_HEIGHT = 0.6
    
    nightstand_x = master_bed_x + MASTER_BED_WIDTH/2 + NIGHTSTAND_SIZE/2 + 0.1
    nightstand_y = master_bed_y
    nightstand_z = oz + NIGHTSTAND_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(nightstand_x, nightstand_y, nightstand_z))
    nightstand = bpy.context.active_object
    nightstand.name = "WetWing2_Nightstand"
    nightstand.scale = (NIGHTSTAND_SIZE/2, NIGHTSTAND_SIZE/2, NIGHTSTAND_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    nightstand.data.materials.append(create_material("OakFurniture", (0.6, 0.45, 0.3, 1)))


def build_under_extension_furniture(origin=(0,0,0), building_width=10.0, building_depth=4.0, exterior_wall_thickness=0.15):
    """
    Add furniture to the lower level (under extension) - 40m².
    
    Lower Level: Mudroom, Guest Suite, Bathroom/Laundry
    
    Args:
        origin: (x, y, z) tuple for building origin
        building_width: Building width in meters (X-direction) - default 10.0
        building_depth: Building depth in meters (Y-direction) - default 4.0
        exterior_wall_thickness: Thickness of exterior walls in meters
    """
    ox, oy, oz = origin
    W, D = building_width, building_depth
    EXTERIOR_WALL_THICKNESS = exterior_wall_thickness
    
    # === MUDROOM AREA (NE Corner) ===
    # Mudroom bench near entrance on east wall (entrance is near north wall)
    BENCH_WIDTH = 1.5
    BENCH_DEPTH = 0.45
    BENCH_HEIGHT = 0.45
    
    bench_x = ox - W/2 + EXTERIOR_WALL_THICKNESS + BENCH_DEPTH/2
    bench_y = oy - D/2 + 0.8  # Near entrance door on east wall
    bench_z = oz + BENCH_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(bench_x, bench_y, bench_z))
    bench = bpy.context.active_object
    bench.name = "UnderExt_MudroomBench"
    bench.scale = (BENCH_DEPTH/2, BENCH_WIDTH/2, BENCH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    bench.data.materials.append(create_material("OakFurniture", (0.6, 0.45, 0.3, 1)))
    
    # === GUEST SUITE (West Side) ===
    # Guest bed - Double bed against west wall (moved from east to avoid stairs)
    GUEST_BED_WIDTH = 1.4  # meters (X-direction) - double bed
    GUEST_BED_LENGTH = 2.0  # meters (Y-direction)
    GUEST_BED_HEIGHT = 0.5  # meters
    
    guest_bed_x = ox + W/2 - EXTERIOR_WALL_THICKNESS - GUEST_BED_WIDTH/2
    guest_bed_y = oy - D/2 + GUEST_BED_LENGTH/2 + 0.5  # Near north wall
    guest_bed_z = oz + GUEST_BED_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(guest_bed_x, guest_bed_y, guest_bed_z))
    guest_bed = bpy.context.active_object
    guest_bed.name = "UnderExt_GuestBed"
    guest_bed.scale = (GUEST_BED_WIDTH/2, GUEST_BED_LENGTH/2, GUEST_BED_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    guest_bed.data.materials.append(create_material("GuestBedding", (0.85, 0.85, 0.95, 1)))
    
    # === BATHROOM/LAUNDRY (South End, East Side) ===
    # Washing machine on east side, south of staircase
    WASHER_SIZE = 0.6
    WASHER_HEIGHT = 0.85
    
    washer_x = ox - W/2 + EXTERIOR_WALL_THICKNESS + 1.5  # East side, clear of stairs
    washer_y = oy + D/2 - EXTERIOR_WALL_THICKNESS - 0.5
    washer_z = oz + WASHER_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(washer_x, washer_y, washer_z))
    washer = bpy.context.active_object
    washer.name = "UnderExt_WashingMachine"
    washer.scale = (WASHER_SIZE/2, WASHER_SIZE/2, WASHER_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    washer.data.materials.append(create_material("WhiteAppliance", (0.95, 0.95, 0.95, 1)))
    
    # Bathroom sink/vanity next to washer
    SINK_WIDTH = 0.8
    SINK_DEPTH = 0.5
    SINK_HEIGHT = 0.85
    
    sink_x = washer_x + WASHER_SIZE/2 + SINK_WIDTH/2 + 0.1  # Next to washer
    sink_y = washer_y
    sink_z = oz + SINK_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(sink_x, sink_y, sink_z))
    sink = bpy.context.active_object
    sink.name = "UnderExt_BathroomSink"
    sink.scale = (SINK_WIDTH/2, SINK_DEPTH/2, SINK_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    sink.data.materials.append(create_material("BathroomVanity", (0.7, 0.65, 0.6, 1)))
