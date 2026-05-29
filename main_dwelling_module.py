import bpy  # type: ignore
import math

from utils import apply_shadowclad_grooves, add_window, create_corrugated_iron_material, add_corner_trim
from materials import get_interior_wall_material, get_floor_wood_material

def create_material(name, color):
    """Create or get a material with the given name and color"""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat


# === HELPER FUNCTIONS FOR MAIN DWELLING ===

def _create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat):
    """Create all exterior walls for ground and first floors with recessed north wall"""
    wall_depth_ground = ENCLOSED_WIDTH - 2*EXTERIOR_WALL_THICKNESS
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    
    # Interior wall material for interior faces
    interior_wall_mat = get_interior_wall_material()
    
    # === GROUND FLOOR EXTERIOR WALLS ===
    # North Wall (recessed NORTH_RECESS inward from north edge)
    # North edge is at oy - WIDTH/2, recess by NORTH_RECESS, position at outer face minus half thickness
    north_wall_y = oy - WIDTH/2 + NORTH_RECESS - EXTERIOR_WALL_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(ox, north_wall_y, oz + GROUND_FLOOR_HEIGHT/2))
    north_wall_ground = bpy.context.active_object
    north_wall_ground.name = "MainDwelling_NorthWall_Ground"
    north_wall_ground.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    north_wall_ground.data.materials.append(potius_mat)
    north_wall_ground.data.materials.append(interior_wall_mat)
    # Assign interior material to south face (index 1)
    north_wall_ground.data.polygons[1].material_index = 1
    
    # South Wall (extends to full WIDTH)
    south_wall_y = oy + WIDTH/2 - EXTERIOR_WALL_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(ox, south_wall_y, oz + GROUND_FLOOR_HEIGHT/2))
    south_wall_ground = bpy.context.active_object
    south_wall_ground.name = "MainDwelling_SouthWall_Ground"
    south_wall_ground.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    south_wall_ground.data.materials.append(potius_mat)
    south_wall_ground.data.materials.append(interior_wall_mat)
    # Assign interior material to north face (index 3)
    south_wall_ground.data.polygons[3].material_index = 1
    
    # East Wall (spans FULL 7m north-south, flush with floors and roof)
    east_west_wall_depth = WIDTH  # Full 7m span to match floor/roof edges
    bpy.ops.mesh.primitive_cube_add(location=(ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS/2, oy, oz + GROUND_FLOOR_HEIGHT/2))
    east_wall_ground = bpy.context.active_object
    east_wall_ground.name = "MainDwelling_EastWall_Ground"
    east_wall_ground.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    east_wall_ground.data.materials.append(potius_mat)
    east_wall_ground.data.materials.append(interior_wall_mat)
    # Assign interior material to west face (index 2)
    east_wall_ground.data.polygons[2].material_index = 1
    
    # West Wall (spans FULL 7m north-south, flush with floors and roof)
    bpy.ops.mesh.primitive_cube_add(location=(ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS/2, oy, oz + GROUND_FLOOR_HEIGHT/2))
    west_wall_ground = bpy.context.active_object
    west_wall_ground.name = "MainDwelling_WestWall_Ground"
    west_wall_ground.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    west_wall_ground.data.materials.append(potius_mat)
    west_wall_ground.data.materials.append(interior_wall_mat)
    # Assign interior material to east face (index 0)
    west_wall_ground.data.polygons[0].material_index = 1
    
    # === FIRST FLOOR EXTERIOR WALLS ===
    # North Wall (recessed, same as ground floor)
    bpy.ops.mesh.primitive_cube_add(location=(ox, north_wall_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    north_wall_first = bpy.context.active_object
    north_wall_first.name = "MainDwelling_NorthWall_First"
    north_wall_first.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    north_wall_first.data.materials.append(potius_mat)
    north_wall_first.data.materials.append(interior_wall_mat)
    # Assign interior material to south face (index 1)
    north_wall_first.data.polygons[1].material_index = 1
    
    # South Wall (extends to full WIDTH)
    bpy.ops.mesh.primitive_cube_add(location=(ox, south_wall_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    south_wall_first = bpy.context.active_object
    south_wall_first.name = "MainDwelling_SouthWall_First"
    south_wall_first.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    south_wall_first.data.materials.append(potius_mat)
    south_wall_first.data.materials.append(interior_wall_mat)
    # Assign interior material to north face (index 3)
    south_wall_first.data.polygons[3].material_index = 1
    
    # East Wall (spans FULL 7m north-south, independent of recessed north wall)
    bpy.ops.mesh.primitive_cube_add(location=(ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS/2, oy, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    east_wall_first = bpy.context.active_object
    east_wall_first.name = "MainDwelling_EastWall_First"
    east_wall_first.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    east_wall_first.data.materials.append(potius_mat)
    east_wall_first.data.materials.append(interior_wall_mat)
    # Assign interior material to west face (index 2)
    east_wall_first.data.polygons[2].material_index = 1
    
    # West Wall (spans FULL 7m north-south, independent of recessed north wall)
    bpy.ops.mesh.primitive_cube_add(location=(ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS/2, oy, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    west_wall_first = bpy.context.active_object
    west_wall_first.name = "MainDwelling_WestWall_First"
    west_wall_first.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    west_wall_first.data.materials.append(potius_mat)
    west_wall_first.data.materials.append(interior_wall_mat)
    # Assign interior material to east face (index 0)
    west_wall_first.data.polygons[0].material_index = 1


def _create_180_degree_staircase_southwest(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, first_floor_slab, floor_mat):
    """Create 180-degree dog-legged staircase in southwest corner with clockwise turn
    
    Spatial Configuration:
    - Location: Southwest corner of floor plan
    - Type: 180-degree half-turn (dog-leg) with clockwise ascent
    - Stairwell footprint: ~2000mm (E-W) × 3000mm (N-S)
    - Flight 1: Starts at NORTH edge, travels SOUTH along EAST edge → Landing
    - Landing: 2000mm wide × 1000mm deep at SOUTH edge, spans East-West
    - Flight 2: Starts at landing, turns 180° clockwise, travels NORTH along WEST edge → Upper floor
    
    Args:
        ox, oy, oz: Origin coordinates (building center)
        WIDTH: Total building width (7m N-S)
        LENGTH: Total building length (9m E-W)
        GROUND_FLOOR_HEIGHT: Ground floor height (2.5m)
        EXTERIOR_WALL_THICKNESS: Wall thickness (0.2m)
        first_floor_slab: First floor slab object for boolean cut
        floor_mat: Material for landing
    """
    # Constants
    TOTAL_RISE = 2.7  # 2700mm (ground floor height + first floor thickness)
    STAIRWELL_WIDTH = 2.0  # 2000mm E-W
    STAIRWELL_LENGTH = 3.0  # 3000mm N-S
    FLIGHT_WIDTH = 0.9  # 900mm per flight
    CENTRAL_GAP = 0.2  # 200mm between flights
    LANDING_DEPTH = 1.0  # 1000mm N-S
    
    # Step dimensions
    STEPS_PER_FLIGHT = 7
    STEP_RISE = TOTAL_RISE / (STEPS_PER_FLIGHT * 2)  # 192.86mm
    STEP_TREAD = 0.285  # 285mm (code compliant: 250-300mm range)
    
    # Landing height (mid-point)
    LANDING_HEIGHT = TOTAL_RISE / 2  # 1.35m
    
    # Southwest corner interior reference (oz is ground level)
    west_interior_x = ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS
    south_interior_y = oy + WIDTH/2 - EXTERIOR_WALL_THICKNESS
    
    # Stairwell boundaries in SW corner
    stairwell_west_x = west_interior_x
    stairwell_east_x = west_interior_x - STAIRWELL_WIDTH
    stairwell_south_y = south_interior_y
    stairwell_north_y = south_interior_y - STAIRWELL_LENGTH
    
    # Materials
    stairs_mat = create_material("StairsWood", (0.6, 0.4, 0.25, 1))
    landing_mat = floor_mat
    
    # === FLIGHT 1: Ground to Landing (SOUTH along EAST edge) ===
    # Starts at NORTH edge, travels SOUTH
    flight1_x = stairwell_east_x + FLIGHT_WIDTH/2 + 0.05  # East edge, 50mm from edge
    flight1_start_y = stairwell_north_y + STEP_TREAD/2 + 0.05  # Start from north
    
    for i in range(STEPS_PER_FLIGHT):
        step_height = oz + STEP_RISE * (i + 1)
        step_y = flight1_start_y + (i * STEP_TREAD)  # Move south (positive Y)
        
        bpy.ops.mesh.primitive_cube_add(location=(flight1_x, step_y, step_height))
        step = bpy.context.active_object
        step.name = f"MainDwelling_Stairs_Flight1_Step_{i+1:02d}"
        step.scale = (FLIGHT_WIDTH/2, STEP_TREAD/2, STEP_RISE/2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stairs_mat)
    
    # === LANDING: At SOUTH edge, spans East-West ===
    landing_x = (stairwell_west_x + stairwell_east_x) / 2
    landing_y = stairwell_south_y - LANDING_DEPTH/2  # South edge
    landing_z = oz + LANDING_HEIGHT
    
    bpy.ops.mesh.primitive_cube_add(location=(landing_x, landing_y, landing_z))
    landing = bpy.context.active_object
    landing.name = "MainDwelling_Stairs_Landing"
    landing.scale = (STAIRWELL_WIDTH/2, LANDING_DEPTH/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    landing.data.materials.append(landing_mat)
    
    # UV unwrap for texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # === FLIGHT 2: Landing to Upper Floor (NORTH along WEST edge, clockwise turn) ===
    # Starts at landing (south), travels NORTH
    flight2_x = stairwell_west_x - FLIGHT_WIDTH/2 - 0.05  # West edge, 50mm from wall
    flight2_start_y = stairwell_south_y - LANDING_DEPTH - STEP_TREAD/2  # Start from south end
    
    for i in range(STEPS_PER_FLIGHT):
        step_height = landing_z + STEP_RISE * (i + 1)
        step_y = flight2_start_y - (i * STEP_TREAD)  # Move north (negative Y)
        
        bpy.ops.mesh.primitive_cube_add(location=(flight2_x, step_y, step_height))
        step = bpy.context.active_object
        step.name = f"MainDwelling_Stairs_Flight2_Step_{i+1:02d}"
        step.scale = (FLIGHT_WIDTH/2, STEP_TREAD/2, STEP_RISE/2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stairs_mat)
    
    # === STAIRWELL OPENING in First Floor Slab ===
    # Opening encompasses Flight 2 and Landing
    opening_x = (stairwell_west_x + stairwell_east_x) / 2
    opening_y = stairwell_south_y - LANDING_DEPTH/2 - (STEPS_PER_FLIGHT * STEP_TREAD)/2
    opening_width = STAIRWELL_WIDTH + 0.1  # Add small margin
    opening_length = LANDING_DEPTH + (STEPS_PER_FLIGHT * STEP_TREAD) + 0.1
    
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    
    bpy.ops.mesh.primitive_cube_add(location=(opening_x, opening_y, first_floor_z + 0.1))
    stairwell_cutter = bpy.context.active_object
    stairwell_cutter.name = "MainDwelling_StairwellCutter_180deg"
    stairwell_cutter.scale = (opening_width/2, opening_length/2, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    
    # Boolean modifier to cut opening
    bool_mod = first_floor_slab.modifiers.new(name="Stairwell_Cut", type='BOOLEAN')
    bool_mod.object = stairwell_cutter
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.solver = 'EXACT'
    
    # Hide cutter
    stairwell_cutter.hide_viewport = True
    stairwell_cutter.hide_render = True
    
    print(f"180-degree staircase created in southwest corner")
    print(f"  Flight 1 (EAST edge): {STEPS_PER_FLIGHT} steps, North→South")
    print(f"  Landing (SOUTH edge): {LANDING_HEIGHT}m height, spans East-West")
    print(f"  Flight 2 (WEST edge): {STEPS_PER_FLIGHT} steps, South→North (clockwise)")
    print(f"  Stairwell footprint: {STAIRWELL_WIDTH}m × {STAIRWELL_LENGTH}m")
    print(f"  Step rise: {STEP_RISE*1000:.1f}mm, tread: {STEP_TREAD*1000:.0f}mm")


def _create_floors(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat):
    """Create ground floor and first floor slabs (no stairs - to be added later)"""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    
    # Floor dimensions: fit within exterior walls (between interior faces)
    floor_length = LENGTH - 2 * EXTERIOR_WALL_THICKNESS  # East-west, inside walls
    # North-south: fit between south interior face and north interior face
    floor_width = WIDTH - EXTERIOR_WALL_THICKNESS  # Account for south wall thickness
    # Center the floor slightly north since south wall reduces the width
    floor_center_y = oy - EXTERIOR_WALL_THICKNESS/2
    
    # Ground Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, floor_center_y, oz + 0.05))
    ground_floor = bpy.context.active_object
    ground_floor.name = "MainDwelling_GroundFloor"
    ground_floor.scale = (floor_length/2, floor_width/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    ground_floor.data.materials.append(floor_mat)
    
    # UV unwrap for texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # First Floor - 200mm thick with stairwell opening
    # Located so bottom is at first_floor_z and top is at first_floor_z + 0.2
    bpy.ops.mesh.primitive_cube_add(location=(ox, floor_center_y, first_floor_z + 0.1))
    first_floor_slab = bpy.context.active_object
    first_floor_slab.name = "MainDwelling_FirstFloor"
    first_floor_slab.scale = (floor_length/2, floor_width/2, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    first_floor_slab.data.materials.append(floor_mat)
    
    # UV unwrap for texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create 180-degree staircase in southwest corner
    _create_180_degree_staircase_southwest(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, 
                                            EXTERIOR_WALL_THICKNESS, first_floor_slab, floor_mat)


def _create_interior_partitions_ground_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Create ground floor interior partitions for guest bedroom with built-in wardrobe
    
    Args:
        WIDTH: Total building width (7m - full roof span)
        ENCLOSED_WIDTH: Enclosed building width (6m - north wall recessed)
        NORTH_RECESS: Distance north wall is recessed from north edge (1m)
    """
    interior_wall_mat = get_interior_wall_material()
    
    # Guest bedroom in NE corner: 3.4m (E-W) × 3m (N-S)
    GUEST_BEDROOM_WIDTH = 3.4   # E-W dimension
    GUEST_BEDROOM_DEPTH = 3.0   # N-S dimension
    
    # Interior reference points (north wall recessed from north edge by NORTH_RECESS)
    east_interior_face = ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS
    north_interior_face = oy - WIDTH/2 + NORTH_RECESS
    
    # Ground floor wall height (slightly shorter to avoid poking through first floor slab)
    FLOOR_SLAB_THICKNESS = 0.1
    ground_floor_wall_height = GROUND_FLOOR_HEIGHT - FLOOR_SLAB_THICKNESS
    
    # West partition wall (N-S) - separates guest bedroom from rest of ground floor
    # Position so that east face of wall is exactly GUEST_BEDROOM_WIDTH from east interior face
    # Extended 500mm south beyond original GUEST_BEDROOM_DEPTH
    WEST_WALL_EXTENSION = 0.5  # Additional 500mm south
    west_partition_x = east_interior_face + GUEST_BEDROOM_WIDTH + INTERIOR_WALL_THICKNESS/2
    west_partition_center_y = north_interior_face + (GUEST_BEDROOM_DEPTH + WEST_WALL_EXTENSION)/2
    
    bpy.ops.mesh.primitive_cube_add(location=(west_partition_x, west_partition_center_y, oz + ground_floor_wall_height/2))
    west_partition = bpy.context.active_object
    west_partition.name = "MainDwelling_GroundFloor_GuestBedroomWestWall"
    west_partition.scale = (INTERIOR_WALL_THICKNESS/2, (GUEST_BEDROOM_DEPTH + WEST_WALL_EXTENSION)/2, ground_floor_wall_height/2)
    bpy.ops.object.transform_apply(scale=True)
    west_partition.data.materials.append(interior_wall_mat)
    
    # South partition wall (E-W) - southern edge of guest bedroom
    south_partition_y = north_interior_face + GUEST_BEDROOM_DEPTH - INTERIOR_WALL_THICKNESS/2
    south_partition_center_x = east_interior_face + GUEST_BEDROOM_WIDTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(south_partition_center_x, south_partition_y, oz + ground_floor_wall_height/2))
    south_partition = bpy.context.active_object
    south_partition.name = "MainDwelling_GroundFloor_GuestBedroomSouthWall"
    south_partition.scale = (GUEST_BEDROOM_WIDTH/2, INTERIOR_WALL_THICKNESS/2, ground_floor_wall_height/2)
    bpy.ops.object.transform_apply(scale=True)
    south_partition.data.materials.append(interior_wall_mat)
    
    # Door on south wall, positioned clear of wardrobe (wardrobe is on west side)
    # Place door about 1.5m from east wall
    door_x = east_interior_face + 2.9
    add_window("MainDwelling_GroundFloor_GuestBedroomSouthWall", (door_x, south_partition_y + INTERIOR_WALL_THICKNESS/2, oz + 1.0), 
               width=0.9, height=2.0, depth=INTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # === CUPBOARD IN GUEST BEDROOM ===
    # Create a cupboard in NW corner of guest bedroom: 600mm (E-W) × 2000mm (N-S)
    CUPBOARD_WIDTH = 0.6    # E-W dimension (600mm)
    CUPBOARD_DEPTH = 2.0    # N-S dimension (2000mm)
    
    # West N-S partition of cupboard - 600mm west of guest bedroom west wall
    # Current west wall outer (west) face is at: west_partition_x + INTERIOR_WALL_THICKNESS/2
    # New wall center is 600mm west of that, plus half its thickness
    cupboard_west_wall_x = west_partition_x + INTERIOR_WALL_THICKNESS/2 + CUPBOARD_WIDTH + INTERIOR_WALL_THICKNESS/2
    cupboard_west_wall_center_y = north_interior_face + CUPBOARD_DEPTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(cupboard_west_wall_x, cupboard_west_wall_center_y, oz + ground_floor_wall_height/2))
    cupboard_west_wall = bpy.context.active_object
    cupboard_west_wall.name = "MainDwelling_GroundFloor_GuestBedroomCupboardWestWall"
    cupboard_west_wall.scale = (INTERIOR_WALL_THICKNESS/2, CUPBOARD_DEPTH/2, ground_floor_wall_height/2)
    bpy.ops.object.transform_apply(scale=True)
    cupboard_west_wall.data.materials.append(interior_wall_mat)
    
    # South E-W partition of cupboard - connects the two N-S walls at 2m from north wall
    cupboard_south_wall_y = north_interior_face + CUPBOARD_DEPTH - INTERIOR_WALL_THICKNESS/2
    cupboard_south_wall_center_x = west_partition_x + INTERIOR_WALL_THICKNESS/2 + CUPBOARD_WIDTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(cupboard_south_wall_center_x, cupboard_south_wall_y, oz + ground_floor_wall_height/2))
    cupboard_south_wall = bpy.context.active_object
    cupboard_south_wall.name = "MainDwelling_GroundFloor_GuestBedroomCupboardSouthWall"
    cupboard_south_wall.scale = (CUPBOARD_WIDTH/2, INTERIOR_WALL_THICKNESS/2, ground_floor_wall_height/2)
    bpy.ops.object.transform_apply(scale=True)
    cupboard_south_wall.data.materials.append(interior_wall_mat)
    
    # === KING BED IN GUEST BEDROOM ===
    # Same dimensions as master bedroom bed (1.8m wide × 2.0m long)
    BED_WIDTH = 1.8  # E-W dimension
    BED_LENGTH = 2.0  # N-S dimension
    BED_HEIGHT = 0.6  # Total height (base + mattress)
    
    bed_mat = create_material("BedFabric", (0.95, 0.95, 0.9, 1))
    
    # Position bed with headboard (pillow side) against south partition, centered E-W in bedroom
    guest_bed_x = east_interior_face + GUEST_BEDROOM_WIDTH/2
    guest_bed_y = south_partition_y - INTERIOR_WALL_THICKNESS/2 - BED_LENGTH/2
    guest_bed_z = oz + BED_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(guest_bed_x, guest_bed_y, guest_bed_z))
    guest_bed = bpy.context.active_object
    guest_bed.name = "MainDwelling_GuestBedroom_KingBed"
    guest_bed.scale = (BED_WIDTH/2, BED_LENGTH/2, BED_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    guest_bed.data.materials.append(bed_mat)
    
    # === PARTITION WALL EAST OF STAIRCASE ===
    # N-S wall immediately west of (actually east of) staircase footprint, 2.5m long from south wall
    STAIRWELL_WIDTH = 2.0  # Staircase is 2m E-W
    PARTITION_LENGTH = 2.5  # 2.5m N-S dimension
    
    # Calculate positions (staircase is in SW corner)
    west_interior_x = ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS
    south_interior_y = oy + WIDTH/2 - EXTERIOR_WALL_THICKNESS
    
    # Staircase east edge is 2m east of west wall
    stairwell_east_x = west_interior_x - STAIRWELL_WIDTH
    
    # Position partition at east edge of stairwell (immediately west/adjacent to stairwell)
    partition_x = stairwell_east_x - INTERIOR_WALL_THICKNESS/2
    partition_center_y = south_interior_y - PARTITION_LENGTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(partition_x, partition_center_y, oz + ground_floor_wall_height/2))
    stair_partition = bpy.context.active_object
    stair_partition.name = "MainDwelling_GroundFloor_StaircasePartition"
    stair_partition.scale = (INTERIOR_WALL_THICKNESS/2, PARTITION_LENGTH/2, ground_floor_wall_height/2)
    bpy.ops.object.transform_apply(scale=True)
    stair_partition.data.materials.append(interior_wall_mat)
    
    # === LOG BURNER AND FLUE (SOUTH OF GUEST BEDROOM CUPBOARD) ===
    # Position log burner south of cupboard, opening faces west
    LOG_BURNER_WIDTH = 0.5   # E-W dimension
    LOG_BURNER_DEPTH = 0.65  # N-S dimension  
    LOG_BURNER_HEIGHT = 0.7  # Height of main body
    FLUE_DIAMETER = 0.15     # 150mm diameter flue pipe
    FLUE_HEIGHT = 6.8        # Extends through ground floor ceiling and first floor
    
    # Materials
    log_burner_mat = create_material("LogBurner", (0.1, 0.1, 0.1, 1))  # Dark metal
    flue_mat = create_material("FluePipe", (0.15, 0.15, 0.15, 1))      # Metal pipe
    
    # Position: centered on cupboard E-W, 0.3m south of cupboard south wall
    cupboard_south_edge_y = north_interior_face + CUPBOARD_DEPTH
    log_burner_x = west_partition_x + INTERIOR_WALL_THICKNESS/2 + CUPBOARD_WIDTH/2 + 0.10
    log_burner_y = cupboard_south_edge_y + 0.8 + LOG_BURNER_DEPTH/2
    log_burner_z = oz + LOG_BURNER_HEIGHT/2
    
    # Create log burner body
    bpy.ops.mesh.primitive_cube_add(location=(log_burner_x, log_burner_y, log_burner_z))
    log_burner = bpy.context.active_object
    log_burner.name = "MainDwelling_GuestBedroom_LogBurner"
    log_burner.scale = (LOG_BURNER_WIDTH/2, LOG_BURNER_DEPTH/2, LOG_BURNER_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    log_burner.data.materials.append(log_burner_mat)
    
    # Create flue pipe (vertical cylinder)
    flue_z = oz + LOG_BURNER_HEIGHT + FLUE_HEIGHT/2
    bpy.ops.mesh.primitive_cylinder_add(location=(log_burner_x, log_burner_y, flue_z), radius=FLUE_DIAMETER/2, depth=FLUE_HEIGHT)
    flue = bpy.context.active_object
    flue.name = "MainDwelling_GuestBedroom_Flue"
    flue.data.materials.append(flue_mat)


def _create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS):
    """Create kitchen bench against the ground floor south wall
    
    Args:
        WIDTH: Total building width (7m - full roof span)
        LENGTH: Building length (9m - east-west)
        EXTERIOR_WALL_THICKNESS: Thickness of exterior walls (0.2m)
    """
    # Kitchen bench specifications
    BENCH_LENGTH = 2.4  # E-W dimension
    BENCH_DEPTH = 0.6   # N-S dimension
    BENCH_HEIGHT = 0.9  # Standard counter height
    BENCH_THICKNESS = 0.05  # Benchtop thickness
    
    # Calculate positions
    # South wall interior face
    south_interior_y = oy + WIDTH/2 - EXTERIOR_WALL_THICKNESS
    # West wall interior face
    west_interior_x = ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS
    
    # Bench center position (starts from west wall, extends 3.6m east)
    bench_center_x = west_interior_x - BENCH_LENGTH/2 - 2.1  # Start 2.1m from west wall
    bench_center_y = south_interior_y - BENCH_DEPTH/2
    bench_top_z = oz + BENCH_HEIGHT
    
    # Create materials
    bench_mat = create_material("KitchenBench", (0.85, 0.82, 0.75, 1))  # Light wood/laminate color
    cabinet_mat = create_material("KitchenCabinet", (0.4, 0.35, 0.3, 1))  # Darker cabinet color
    
    # Base cabinets
    cabinet_height = BENCH_HEIGHT - BENCH_THICKNESS
    bpy.ops.mesh.primitive_cube_add(location=(bench_center_x, bench_center_y, oz + cabinet_height/2))
    cabinets = bpy.context.active_object
    cabinets.name = "MainDwelling_KitchenBench_Cabinets"
    cabinets.scale = (BENCH_LENGTH/2, BENCH_DEPTH/2, cabinet_height/2)
    bpy.ops.object.transform_apply(scale=True)
    cabinets.data.materials.append(cabinet_mat)
    
    # Benchtop
    bpy.ops.mesh.primitive_cube_add(location=(bench_center_x, bench_center_y, bench_top_z - BENCH_THICKNESS/2))
    benchtop = bpy.context.active_object
    benchtop.name = "MainDwelling_KitchenBench_Top"
    benchtop.scale = (BENCH_LENGTH/2, BENCH_DEPTH/2, BENCH_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    benchtop.data.materials.append(bench_mat)
    
    print(f"Kitchen bench created: {BENCH_LENGTH}m long, starting from west wall at x={west_interior_x} extending east")


def _create_interior_partitions_first_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Create first floor interior partitions for master bedroom, ensuite, and wardrobe
    
    Args:
        WIDTH: Total building width (7m - full roof span)
        ENCLOSED_WIDTH: Enclosed building width (6m - north wall recessed)
        NORTH_RECESS: Distance north wall is recessed from north edge (1m)
    """
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    interior_wall_mat = get_interior_wall_material()
    
    # Master bedroom & ensuite dimensions
    MASTER_BEDROOM_WIDTH = 4.0  # E-W dimension (interior space from east wall)
    ENSUITE_DEPTH = 2.0
    ENSUITE_WIDTH = 2.0
    
    # Interior dimensions (north wall recessed from north edge by NORTH_RECESS)
    north_interior_face = oy - WIDTH/2 + NORTH_RECESS
    south_interior_face = oy + WIDTH/2 - EXTERIOR_WALL_THICKNESS
    interior_depth = south_interior_face - north_interior_face
    bedroom_interior_width = MASTER_BEDROOM_WIDTH  # Full 4m interior space
    east_interior_face = ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS
    
    # Main partition wall (N-S) - aligned with bedroom partitions at MASTER_BEDROOM_WIDTH from east wall
    main_partition_x = east_interior_face + MASTER_BEDROOM_WIDTH + INTERIOR_WALL_THICKNESS/2
    main_partition_center_y = (north_interior_face + south_interior_face) / 2  # Center between recessed north and full-width south
    bpy.ops.mesh.primitive_cube_add(location=(main_partition_x, main_partition_center_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    main_partition = bpy.context.active_object
    main_partition.name = "MainDwelling_FirstFloor_MainPartition"
    main_partition.scale = (INTERIOR_WALL_THICKNESS/2, interior_depth/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    main_partition.data.materials.append(interior_wall_mat)
    
    # Bedroom south partition (E-W wall) - spans exactly MASTER_BEDROOM_WIDTH (4m) from east wall
    bedroom_partition_y = south_interior_face - ENSUITE_DEPTH
    bedroom_partition_center_x = east_interior_face + MASTER_BEDROOM_WIDTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(bedroom_partition_center_x, bedroom_partition_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    bedroom_south_partition = bpy.context.active_object
    bedroom_south_partition.name = "MainDwelling_FirstFloor_BedroomSouthPartition"
    bedroom_south_partition.scale = (MASTER_BEDROOM_WIDTH/2, INTERIOR_WALL_THICKNESS/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    bedroom_south_partition.data.materials.append(interior_wall_mat)
    
    # Ensuite/wardrobe dividing wall (N-S)
    ensuite_wardrobe_wall_x = east_interior_face + ENSUITE_WIDTH
    ensuite_wardrobe_wall_center_y = south_interior_face - ENSUITE_DEPTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(ensuite_wardrobe_wall_x, ensuite_wardrobe_wall_center_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    ensuite_wardrobe_wall = bpy.context.active_object
    ensuite_wardrobe_wall.name = "MainDwelling_FirstFloor_EnsuiteWardrobeWall"
    ensuite_wardrobe_wall.scale = (INTERIOR_WALL_THICKNESS/2, ENSUITE_DEPTH/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    ensuite_wardrobe_wall.data.materials.append(interior_wall_mat)
    
    # Add doorways
    # Door from hallway to master bedroom
    add_window("MainDwelling_FirstFloor_MainPartition", (main_partition_x - INTERIOR_WALL_THICKNESS/2, oy - 2.0, first_floor_z + 1.0), 
               width=0.8, height=2.0, depth=INTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # Door from bedroom to ensuite
    add_window("MainDwelling_FirstFloor_BedroomSouthPartition", (east_interior_face + 0.45, bedroom_partition_y + INTERIOR_WALL_THICKNESS/2, first_floor_z + 1.0), 
               width=0.8, height=2.0, depth=INTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # Door from bedroom to walk-in wardrobe
    add_window("MainDwelling_FirstFloor_BedroomSouthPartition", (ensuite_wardrobe_wall_x + 1.5, bedroom_partition_y + INTERIOR_WALL_THICKNESS/2, first_floor_z + 1.0), 
               width=0.8, height=2.0, depth=INTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # King bed in master bedroom (1.8m wide × 2.0m long)
    BED_WIDTH = 1.8  # E-W dimension
    BED_LENGTH = 2.0  # N-S dimension
    BED_HEIGHT = 0.6  # Total height (base + mattress)
    
    bed_mat = create_material("BedFabric", (0.95, 0.95, 0.9, 1))
    
    # Position bed with headboard against south partition, centered E-W
    bed_x = east_interior_face + MASTER_BEDROOM_WIDTH/2
    bed_y = bedroom_partition_y - INTERIOR_WALL_THICKNESS/2 - BED_LENGTH/2
    bed_z = first_floor_z + BED_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(bed_x, bed_y, bed_z))
    bed = bpy.context.active_object
    bed.name = "MainDwelling_MasterBedroom_KingBed"
    bed.scale = (BED_WIDTH/2, BED_LENGTH/2, BED_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    bed.data.materials.append(bed_mat)


def _furnish_master_ensuite(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS):
    """Furnish master bedroom ensuite with shower, toilet, and vanity
    
    Layout (2m × 2m ensuite in SE corner):
    - Shower: NW corner, stepping in from east
    - Toilet: SW corner, back against west wall
    - Vanity: SE corner, back against east wall
    - Entrance: East side of north wall
    """
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    
    # Ensuite dimensions
    ENSUITE_WIDTH = 2.0   # E-W dimension
    ENSUITE_DEPTH = 2.0   # N-S dimension
    
    # Calculate ensuite boundaries
    east_interior_face = ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS
    south_interior_face = oy + WIDTH/2 - EXTERIOR_WALL_THICKNESS
    
    # Ensuite corners
    ensuite_east = east_interior_face
    ensuite_west = east_interior_face + ENSUITE_WIDTH
    ensuite_south = south_interior_face
    ensuite_north = south_interior_face - ENSUITE_DEPTH
    
    # Materials
    white_mat = create_material("BathroomWhite", (0.95, 0.95, 0.95, 1))
    chrome_mat = create_material("Chrome", (0.8, 0.8, 0.8, 1))
    glass_mat = create_material("ShowerGlass", (0.7, 0.85, 0.9, 0.3))
    
    # === SHOWER IN NW CORNER (stepping in from east) ===
    SHOWER_SIZE = 0.9  # 900mm square shower
    SHOWER_TRAY_HEIGHT = 0.15  # 150mm high tray
    WALL_THICKNESS = 0.1  # 100mm thick walls
    WALL_HEIGHT = 2.0
    
    # Position shower in NW corner - back walls align with room walls
    # West wall of shower aligns with west wall of ensuite
    # North wall of shower aligns with north wall of ensuite
    shower_west_edge = ensuite_west
    shower_east_edge = ensuite_west - SHOWER_SIZE
    shower_north_edge = ensuite_north
    shower_south_edge = ensuite_north + SHOWER_SIZE
    shower_x_center = (shower_west_edge + shower_east_edge) / 2
    shower_y_center = (shower_north_edge + shower_south_edge) / 2
    
    # Shower tray (raised platform)
    bpy.ops.mesh.primitive_cube_add(location=(shower_x_center, shower_y_center, first_floor_z + SHOWER_TRAY_HEIGHT/2))
    shower_tray = bpy.context.active_object
    shower_tray.name = "MainDwelling_Ensuite_ShowerTray"
    shower_tray.scale = (SHOWER_SIZE/2, SHOWER_SIZE/2, SHOWER_TRAY_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    shower_tray.data.materials.append(white_mat)
    
    # Shower walls (tile/panel material)
    tile_mat = create_material("ShowerTile", (0.9, 0.9, 0.88, 1))
    
    # West wall (back wall against ensuite west wall)
    west_wall_x = shower_west_edge - WALL_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(west_wall_x, shower_y_center, 
                                               first_floor_z + SHOWER_TRAY_HEIGHT + WALL_HEIGHT/2))
    west_wall = bpy.context.active_object
    west_wall.name = "MainDwelling_Ensuite_ShowerWallWest"
    west_wall.scale = (WALL_THICKNESS/2, SHOWER_SIZE/2, WALL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall.data.materials.append(tile_mat)
    
    # North wall (side wall against ensuite north wall)
    north_wall_y = shower_north_edge - WALL_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(shower_x_center, north_wall_y, 
                                               first_floor_z + SHOWER_TRAY_HEIGHT + WALL_HEIGHT/2))
    north_wall = bpy.context.active_object
    north_wall.name = "MainDwelling_Ensuite_ShowerWallNorth"
    north_wall.scale = (SHOWER_SIZE/2, WALL_THICKNESS/2, WALL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall.data.materials.append(tile_mat)
    
    # Shower glass screen (east side - entrance, shorter than walls)
    glass_thickness = 0.01
    glass_height = 1.8
    glass_x = shower_east_edge + glass_thickness/2
    bpy.ops.mesh.primitive_cube_add(location=(glass_x, shower_y_center, 
                                               first_floor_z + SHOWER_TRAY_HEIGHT + glass_height/2))
    shower_screen = bpy.context.active_object
    shower_screen.name = "MainDwelling_Ensuite_ShowerScreen"
    shower_screen.scale = (glass_thickness/2, SHOWER_SIZE/2, glass_height/2)
    bpy.ops.object.transform_apply(scale=True)
    shower_screen.data.materials.append(glass_mat)
    
    # Shower head (mounted on west wall)
    bpy.ops.mesh.primitive_uv_sphere_add(location=(west_wall_x + 0.15, shower_y_center, 
                                                    first_floor_z + SHOWER_TRAY_HEIGHT + 1.8), radius=0.05)
    shower_head = bpy.context.active_object
    shower_head.name = "MainDwelling_Ensuite_ShowerHead"
    shower_head.data.materials.append(chrome_mat)
    
    # === TOILET IN SW CORNER (back against west wall) ===
    TOILET_WIDTH = 0.4  # N-S dimension
    TOILET_DEPTH = 0.6  # E-W dimension (depth from wall)
    TOILET_HEIGHT = 0.4
    TOILET_TANK_HEIGHT = 0.8
    
    # Position in SW corner, tank against west wall, bowl facing east
    toilet_east_edge = ensuite_west - TOILET_DEPTH
    toilet_center_x = (ensuite_west + toilet_east_edge) / 2
    toilet_center_y = ensuite_south - TOILET_WIDTH/2 - 0.15  # 150mm from south wall
    
    # Toilet bowl (combined bowl and tank as one unit for simplicity)
    bpy.ops.mesh.primitive_cube_add(location=(toilet_center_x, toilet_center_y, first_floor_z + TOILET_HEIGHT/2))
    toilet_bowl = bpy.context.active_object
    toilet_bowl.name = "MainDwelling_Ensuite_ToiletBowl"
    toilet_bowl.scale = (TOILET_DEPTH/2, TOILET_WIDTH/2, TOILET_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    toilet_bowl.data.materials.append(white_mat)
    
    # Toilet tank (against west wall)
    tank_width = 0.15
    bpy.ops.mesh.primitive_cube_add(location=(ensuite_west - tank_width/2, toilet_center_y, 
                                               first_floor_z + TOILET_TANK_HEIGHT/2))
    toilet_tank = bpy.context.active_object
    toilet_tank.name = "MainDwelling_Ensuite_ToiletTank"
    toilet_tank.scale = (tank_width/2, TOILET_WIDTH/2, TOILET_TANK_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    toilet_tank.data.materials.append(white_mat)
    
    # === VANITY IN SE CORNER (back against east wall, facing west) ===
    VANITY_WIDTH = 0.6  # N-S dimension
    VANITY_DEPTH = 0.5  # E-W dimension (depth from wall)
    VANITY_HEIGHT = 0.85
    BASIN_HEIGHT = 0.15
    
    # Position in SE corner, back against east wall, facing west
    vanity_west_edge = ensuite_east + VANITY_DEPTH
    vanity_center_x = (ensuite_east + vanity_west_edge) / 2
    vanity_center_y = ensuite_south - VANITY_WIDTH/2
    
    # Vanity cabinet
    cabinet_mat = create_material("VanityCabinet", (0.4, 0.3, 0.2, 1))
    bpy.ops.mesh.primitive_cube_add(location=(vanity_center_x, vanity_center_y, first_floor_z + VANITY_HEIGHT/2))
    vanity_cabinet = bpy.context.active_object
    vanity_cabinet.name = "MainDwelling_Ensuite_VanityCabinet"
    vanity_cabinet.scale = (VANITY_DEPTH/2, VANITY_WIDTH/2, VANITY_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    vanity_cabinet.data.materials.append(cabinet_mat)
    
    # Basin
    bpy.ops.mesh.primitive_cube_add(location=(vanity_center_x, vanity_center_y, 
                                               first_floor_z + VANITY_HEIGHT + BASIN_HEIGHT/2))
    basin = bpy.context.active_object
    basin.name = "MainDwelling_Ensuite_Basin"
    basin.scale = ((VANITY_DEPTH - 0.1)/2, (VANITY_WIDTH - 0.1)/2, BASIN_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    basin.data.materials.append(white_mat)
    
    # Tap (positioned toward front/west of basin)
    bpy.ops.mesh.primitive_cylinder_add(location=(vanity_center_x + 0.15, vanity_center_y, 
                                                   first_floor_z + VANITY_HEIGHT + 0.15), radius=0.02, depth=0.2)
    tap = bpy.context.active_object
    tap.name = "MainDwelling_Ensuite_Tap"
    tap.data.materials.append(chrome_mat)


def _add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Add all windows and doors to exterior walls
    
    Args:
        WIDTH: Total building width (7m - full roof span, south wall position)
        ENCLOSED_WIDTH: Enclosed building width (6m - north wall recessed)
        NORTH_RECESS: Distance north wall is recessed from north edge (1m)
    """
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    window_z_ground = oz + 1.0
    window_z_first = first_floor_z + 1.0
    spacing = LENGTH / 4
    
    # Calculate wall positions
    north_wall_y = oy - WIDTH/2 + NORTH_RECESS - EXTERIOR_WALL_THICKNESS/2
    north_wall_interior_face = north_wall_y + EXTERIOR_WALL_THICKNESS/2  # Interior face position
    south_wall_y = oy + WIDTH/2
    
    # East/West walls span full WIDTH, centered at oy
    east_west_window_spacing = WIDTH / 3
    south_spacing = LENGTH / 4
    
    # GROUND FLOOR - NORTH WALL (recessed) - position at interior face
    add_window("MainDwelling_NorthWall_Ground", (ox - spacing, north_wall_interior_face, window_z_ground), width=2.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    #add_window("MainDwelling_NorthWall_Ground", (ox, north_wall_interior_face, window_z_ground), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_NorthWall_Ground", (ox + spacing, north_wall_interior_face, window_z_ground), width=2.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # FIRST FLOOR - NORTH WALL (recessed) - position at interior face
    add_window("MainDwelling_NorthWall_First", (ox - spacing, north_wall_interior_face, window_z_first), width=2.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_NorthWall_First", (ox + spacing, north_wall_interior_face, window_z_first), width=2.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # GROUND FLOOR - EAST WALL (spans full 7m)
    add_window("MainDwelling_EastWall_Ground", (ox - LENGTH/2, oy - 1.5, oz + 1.2), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    add_window("MainDwelling_EastWall_Ground", (ox - LENGTH/2, oy + 2, oz + 1.2), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # FIRST FLOOR - EAST WALL (spans full 7m)
    add_window("MainDwelling_EastWall_First", (ox - LENGTH/2, oy - 1.5, first_floor_z + 1.2), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    add_window("MainDwelling_EastWall_First", (ox - LENGTH/2, oy + 2, first_floor_z + 1.2), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # GROUND FLOOR - WEST WALL (spans full 7m)
    add_window("MainDwelling_WestWall_Ground", (ox + LENGTH/2, oy - 1.5, oz + 1.4), width=0.9, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MainDwelling_WestWall_Ground", (ox + LENGTH/2, oy + 1.5, oz + 1.4), width=0.9, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # FIRST FLOOR - WEST WALL (spans full 7m)
    add_window("MainDwelling_WestWall_First", (ox + LENGTH/2, oy - 1.5, first_floor_z + 1.2), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MainDwelling_WestWall_First", (ox + LENGTH/2, oy + 1.5, first_floor_z + 1.2), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # GROUND FLOOR - SOUTH WALL (full width)
    add_window("MainDwelling_SouthWall_Ground", (ox - 3, south_wall_y, oz + 1.4), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_SouthWall_Ground", (ox - 1.5, south_wall_y, oz + 1.0), width=1.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_SouthWall_Ground", (ox + 0.8, south_wall_y, oz + 1.4), width=2.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    # Double-height window at stair landing - ground floor portion
    add_window("MainDwelling_SouthWall_Ground", (ox + 3.3, south_wall_y, oz + 2.15), width=1.2, height=0.7, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # FIRST FLOOR - SOUTH WALL (full width)
    add_window("MainDwelling_SouthWall_First", (ox - 3.2, south_wall_y, first_floor_z + 1.2), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_SouthWall_First", (ox - 1.0, south_wall_y, first_floor_z + 1.2), width=0.6, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_SouthWall_First", (ox + 0.8, south_wall_y, first_floor_z + 1.2), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    # Double-height window at stair landing - first floor portion
    add_window("MainDwelling_SouthWall_First", (ox + 3.3, south_wall_y, first_floor_z + 0.4), width=1.2, height=2.8, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # Cut opening in first floor slab for double-height window
    first_floor_slab = bpy.data.objects.get("MainDwelling_FirstFloor")
    if first_floor_slab:
        # Position cutter to cut floor flush with interior face of south wall
        interior_face_y = south_wall_y - EXTERIOR_WALL_THICKNESS/2
        window_slab_opening_depth = 0.4  # Extend north into room
        cutter_center_y = interior_face_y - window_slab_opening_depth/2
        
        bpy.ops.mesh.primitive_cube_add(location=(ox + 3.2, cutter_center_y, first_floor_z + 0.1))
        window_cutter = bpy.context.active_object
        window_cutter.name = "MainDwelling_WindowSlabCutter_StairLanding"
        window_cutter.scale = (1.0/2, window_slab_opening_depth/2, 0.2/2)
        bpy.ops.object.transform_apply(scale=True)
        
        # Boolean modifier to cut opening
        bool_mod = first_floor_slab.modifiers.new(name="StairWindow_Cut", type='BOOLEAN')
        bool_mod.object = window_cutter
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.solver = 'EXACT'
        
        # Hide cutter
        window_cutter.hide_viewport = True
        window_cutter.hide_render = True


def _create_gable_roof(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, roof_style):
    """Create the main gable roof with either traditional or flush style"""
    roof_height_from_eaves = (WIDTH / 2) * math.tan(math.radians(ROOF_PITCH))
    eave_height = oz + TOTAL_HEIGHT
    ridge_height = eave_height + roof_height_from_eaves
    
    roof_mat = create_corrugated_iron_material()
    gable_material = create_material("GableEnd", (0.22, 0.22, 0.24, 1))
    
    if roof_style == "flush":
        mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
        obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
        bpy.context.collection.objects.link(obj)
        
        east_edge = ox - LENGTH/2
        west_edge = ox + LENGTH/2
        # Roof spans full 7m WIDTH, flush with building edges
        north_eave_y = oy - WIDTH/2
        south_eave_y = oy + WIDTH/2
        
        verts = [
            (east_edge, north_eave_y, eave_height),
            (west_edge, north_eave_y, eave_height),
            (east_edge, oy, ridge_height),
            (west_edge, oy, ridge_height),
            (east_edge, south_eave_y, eave_height),
            (west_edge, south_eave_y, eave_height),
        ]
        
        faces = [
            (0, 1, 3, 2),  # North roof slope
            (2, 3, 5, 4),  # South roof slope
            (0, 2, 4),     # East gable triangle
            (1, 5, 3),     # West gable triangle
        ]
        
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        
        obj.data.materials.append(roof_mat)
        obj.data.materials.append(gable_material)
        
        for i, face in enumerate(mesh.polygons):
            if i < 2:
                face.material_index = 0
            else:
                face.material_index = 1
    else:  # traditional
        mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
        obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
        bpy.context.collection.objects.link(obj)
        
        half_length = (LENGTH + 2 * ROOF_OVERHANG) / 2
        north_eave_y = oy - WIDTH/2 - ROOF_OVERHANG
        south_eave_y = oy + WIDTH/2 + ROOF_OVERHANG
        
        verts = [
            (ox - half_length, north_eave_y, eave_height),
            (ox + half_length, north_eave_y, eave_height),
            (ox - half_length, oy, ridge_height),
            (ox + half_length, oy, ridge_height),
            (ox - half_length, south_eave_y, eave_height),
            (ox + half_length, south_eave_y, eave_height),
        ]
        
        faces = [
            (0, 1, 3, 2),
            (2, 3, 5, 4),
        ]
        
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(roof_mat)
        
        # Create separate gable end triangles
        for side, x_pos in [("East", ox - LENGTH/2), ("West", ox + LENGTH/2)]:
            verts = [
                (x_pos, oy - WIDTH/2, eave_height),
                (x_pos, oy + WIDTH/2, eave_height),
                (x_pos, oy, ridge_height)
            ]
            edges = []
            faces = [(0, 1, 2)]
            
            gable_mesh = bpy.data.meshes.new(f"MainDwelling_Gable_{side}")
            gable_mesh.from_pydata(verts, edges, faces)
            gable_mesh.update()
            
            gable = bpy.data.objects.new(f"MainDwelling_Gable_{side}", gable_mesh)
            bpy.context.collection.objects.link(gable)
            gable.data.materials.append(gable_material)


# === MAIN BUILDING FUNCTIONS ===

def build_main_dwelling(origin=(0, 0, 0), show_roof=True, roof_style="traditional"):
    """
    Build the main dwelling structure with ENCLOSED GABLE PORCH:
    - 7m × 9m base (9m runs east-west, 7m north-south)
    - North wall recessed 1m to create patio (ground) and covered balcony (first floor)
    - Two stories: ground floor 2.5m ceiling, first floor 2.4m ceiling
    - Potius residential system with 200mm exterior walls
    - Interior walls 110mm
    - Gable roof, 35° pitch, ridge runs east-west
    - 2.5m × 2.5m enclosed porch with gable roof, door in west porch wall
    - Windows/doors on north and east walls
    
    Args:
        origin: (x, y, z) tuple for building location
        show_roof: Boolean to show/hide roof for interior viewing
        roof_style: "traditional" (overhang on all sides, separate gable ends) or 
                    "flush" (flush with building edges, covers recessed north balcony)
    """
    ox, oy, oz = origin
    
    # Dimensions from specifications
    WIDTH = 7.0  # Total north-south dimension (roof span)
    ENCLOSED_WIDTH = 6.0  # Enclosed building width (north wall recessed 1m)
    LENGTH = 9.0
    GROUND_FLOOR_HEIGHT = 2.5
    FIRST_FLOOR_HEIGHT = 2.4
    TOTAL_HEIGHT = GROUND_FLOOR_HEIGHT + FIRST_FLOOR_HEIGHT
    EXTERIOR_WALL_THICKNESS = 0.20
    INTERIOR_WALL_THICKNESS = 0.11
    ROOF_PITCH = 35
    ROOF_OVERHANG = 0.6
    NORTH_RECESS = 1.0  # North wall recessed to create patio/balcony
    
    # Materials
    potius_mat = create_material("PotiusExterior", (0.22, 0.22, 0.24, 1))
    floor_mat = get_floor_wood_material()
    
    # === CREATE SHARED COMPONENTS ===
    _create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat)
    _create_floors(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat)
    
    # === ENTRANCE PORCH (WEST SIDE) - ENCLOSED WITH GABLE ROOF ===
    
    # Porch dimensions: 2.5m Ã— 2.5m floor, walls wrap 2.5m width Ã— 1.5m depth
    # Remaining 1m is open but covered by porch roof
    PORCH_WIDTH = 2.5   # North-south dimension
    PORCH_TOTAL_DEPTH = 2.5   # Total east-west depth
    PORCH_WALL_DEPTH = 1.5    # Depth covered by walls
    PORCH_OPEN_DEPTH = 1.0    # Open covered area (2.5 - 1.5)
    PORCH_HEIGHT = GROUND_FLOOR_HEIGHT  # Same height as ground floor
    PORCH_WALL_THICKNESS = EXTERIOR_WALL_THICKNESS
    
    porch_mat = potius_mat  # Use same material as main building
    
    # Porch floor/deck - positioned west of west wall, centered
    porch_center_x = ox + LENGTH/2 + PORCH_TOTAL_DEPTH/2
    porch_center_y = oy  # Centered on building
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_center_x, porch_center_y, oz + 0.05))
    porch_floor = bpy.context.active_object
    porch_floor.name = "MainDwelling_PorchFloor"
    porch_floor.scale = (PORCH_TOTAL_DEPTH/2, PORCH_WIDTH/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    porch_floor.data.materials.append(floor_mat)
    
    # Porch walls - wrap the 2.5m width and first 1.5m of depth
    
    # North porch wall (runs E-W for 1.5m)
    porch_wall_x = ox + LENGTH/2 + PORCH_WALL_DEPTH/2
    north_porch_wall_y = oy - PORCH_WIDTH/2 + PORCH_WALL_THICKNESS/2
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_wall_x, north_porch_wall_y, oz + PORCH_HEIGHT/2))
    north_porch_wall = bpy.context.active_object
    north_porch_wall.name = "MainDwelling_PorchWall_North"
    north_porch_wall.scale = (PORCH_WALL_DEPTH/2, PORCH_WALL_THICKNESS/2, PORCH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    north_porch_wall.data.materials.append(porch_mat)
    
    # South porch wall (runs E-W for 1.5m)
    south_porch_wall_y = oy + PORCH_WIDTH/2 - PORCH_WALL_THICKNESS/2
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_wall_x, south_porch_wall_y, oz + PORCH_HEIGHT/2))
    south_porch_wall = bpy.context.active_object
    south_porch_wall.name = "MainDwelling_PorchWall_South"
    south_porch_wall.scale = (PORCH_WALL_DEPTH/2, PORCH_WALL_THICKNESS/2, PORCH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    south_porch_wall.data.materials.append(porch_mat)
    
    # West porch wall (partial - connects north and south walls at 1.5m mark)
    west_porch_wall_x = ox + LENGTH/2 + PORCH_WALL_DEPTH - PORCH_WALL_THICKNESS/2
    porch_wall_span = PORCH_WIDTH - 2*PORCH_WALL_THICKNESS  # Between north and south walls
    
    bpy.ops.mesh.primitive_cube_add(location=(west_porch_wall_x, oy, oz + PORCH_HEIGHT/2))
    west_porch_wall = bpy.context.active_object
    west_porch_wall.name = "MainDwelling_PorchWall_West"
    west_porch_wall.scale = (PORCH_WALL_THICKNESS/2, porch_wall_span/2, PORCH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    west_porch_wall.data.materials.append(porch_mat)
    
    # Porch entrance door on west wall
    # Position needs to be on OUTER face of wall (west side)
    porch_door_x = ox + LENGTH/2 + PORCH_WALL_DEPTH  # Outer face, not center
    print(f"Adding porch door at x={porch_door_x}, y={oy}, z={oz + 1.0}")
    add_window("MainDwelling_PorchWall_West", (porch_door_x, oy, oz + 1.0), 
               width=0.9, height=2.0, depth=PORCH_WALL_THICKNESS, axis='X', inward_offset='-X')
    print("Porch door window call completed")
    
    # Porch gable roof - 35Â° pitch, ridge running E-W like main roof
    PORCH_ROOF_PITCH = 35
    PORCH_ROOF_OVERHANG = 0.3  # Small overhang
    
    porch_roof_height_from_eaves = (PORCH_WIDTH / 2) * math.tan(math.radians(PORCH_ROOF_PITCH))
    porch_eave_height = oz + PORCH_HEIGHT
    porch_ridge_height = porch_eave_height + porch_roof_height_from_eaves
    
    # Create porch roof mesh
    porch_roof_mesh = bpy.data.meshes.new("MainDwelling_PorchRoofMesh")
    porch_roof_obj = bpy.data.objects.new("MainDwelling_PorchRoof", porch_roof_mesh)
    bpy.context.collection.objects.link(porch_roof_obj)
    
    # Porch roof vertices with overhang
    porch_roof_length = PORCH_TOTAL_DEPTH + 2 * PORCH_ROOF_OVERHANG
    porch_roof_west = ox + LENGTH/2 + PORCH_TOTAL_DEPTH + PORCH_ROOF_OVERHANG
    porch_roof_east = ox + LENGTH/2 - PORCH_ROOF_OVERHANG
    porch_roof_north = oy - PORCH_WIDTH/2 - PORCH_ROOF_OVERHANG
    porch_roof_south = oy + PORCH_WIDTH/2 + PORCH_ROOF_OVERHANG
    
    porch_verts = [
        # North eave edge
        (porch_roof_east, porch_roof_north, porch_eave_height),
        (porch_roof_west, porch_roof_north, porch_eave_height),
        # Ridge line (center)
        (porch_roof_east, oy, porch_ridge_height),
        (porch_roof_west, oy, porch_ridge_height),
        # South eave edge
        (porch_roof_east, porch_roof_south, porch_eave_height),
        (porch_roof_west, porch_roof_south, porch_eave_height),
    ]
    
    porch_faces = [
        (0, 1, 3, 2),  # North roof slope
        (2, 3, 5, 4),  # South roof slope
    ]
    
    porch_roof_mesh.from_pydata(porch_verts, [], porch_faces)
    porch_roof_mesh.update()
    porch_roof_obj.data.materials.append(create_corrugated_iron_material())
    
    # Large opening in main building's west wall connecting to porch
    add_window("MainDwelling_WestWall_Ground", (ox + LENGTH/2, oy, oz + 1.1), 
               width=2.0, height=2.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # === INTERIOR PARTITIONS ===
    _create_interior_partitions_ground_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS)
    _create_interior_partitions_first_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS)
    
    # === ENSUITE FURNITURE ===
    _furnish_master_ensuite(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS)
    
    # === KITCHEN BENCH ===
    _create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
    
    # === WINDOWS AND DOORS ===
    _add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS)
    
    # === GABLE ROOF ===
    if show_roof:
        _create_gable_roof(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, roof_style)
    
    print(f"Main Dwelling built at origin {origin}")


def build_main_dwelling_simple_porch(origin=(0, 0, 0), show_roof=True, roof_style="traditional"):
    """
    Build the main dwelling with a SIMPLE OPEN PORCH entrance option:
    - 2.5m Ã— 1.5m deck (same width as enclosed porch, but only 1.5m deep)
    - No walls - just a roof and deck
    - Monopitch (single-slope) roof sloping outward from building
    - Main entrance door on the main structure's west wall (not on porch)
    
    Args:
        origin: (x, y, z) tuple for building location
        show_roof: Boolean to show/hide main roof for interior viewing
        roof_style: "traditional" or "flush" for main building roof
    """
    ox, oy, oz = origin
    
    # Dimensions from specifications
    WIDTH = 7.0  # Total north-south dimension (roof span)
    ENCLOSED_WIDTH = 6.0  # Enclosed building width (north wall recessed 1m)
    NORTH_RECESS = 1.0  # North wall recessed to create patio/balcony
    LENGTH = 9.0
    GROUND_FLOOR_HEIGHT = 2.5
    FIRST_FLOOR_HEIGHT = 2.4
    TOTAL_HEIGHT = GROUND_FLOOR_HEIGHT + FIRST_FLOOR_HEIGHT
    EXTERIOR_WALL_THICKNESS = 0.20
    INTERIOR_WALL_THICKNESS = 0.11
    ROOF_PITCH = 35
    ROOF_OVERHANG = 0.6
    
    # Materials
    potius_mat = create_material("PotiusExterior", (0.22, 0.22, 0.24, 1))
    floor_mat = get_floor_wood_material()
    
    # === CREATE SHARED COMPONENTS ===
    _create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat)
    _create_floors(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat)
    
    # === SIMPLE OPEN ENTRANCE PORCH (WEST SIDE) ===
    
    # Porch dimensions: 2.5m wide Ã— 1.5m deep, OPEN (no walls)
    PORCH_WIDTH = 2.5   # North-south dimension
    PORCH_DEPTH = 1.5   # East-west depth
    
    # Porch deck - positioned west of west wall, centered
    porch_center_x = ox + LENGTH/2 + PORCH_DEPTH/2
    porch_center_y = oy  # Centered on building
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_center_x, porch_center_y, oz + 0.05))
    porch_deck = bpy.context.active_object
    porch_deck.name = "MainDwelling_PorchDeck_Simple"
    porch_deck.scale = (PORCH_DEPTH/2, PORCH_WIDTH/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    porch_deck.data.materials.append(floor_mat)
    
    # Main entrance door on MAIN BUILDING'S WEST WALL (not on porch)
    # Door: 0.9m wide Ã— 2.0m high, centered on west wall
    main_door_x = ox + LENGTH/2  # On west wall face
    add_window("MainDwelling_WestWall_Ground", (main_door_x, oy, oz + 1.0), width=0.9, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # Monopitch porch roof - single slope, high at building, low at outer edge
    PORCH_ROOF_PITCH = 15  # degrees (gentler slope for monopitch)
    PORCH_ROOF_OVERHANG = 0.3  # Small overhang on sides and front
    
    # Roof starts at eave height (top of ground floor walls) and slopes downward
    porch_roof_high_height = oz + GROUND_FLOOR_HEIGHT
    porch_roof_drop = PORCH_DEPTH * math.tan(math.radians(PORCH_ROOF_PITCH))
    porch_roof_low_height = porch_roof_high_height - porch_roof_drop
    
    # Create monopitch roof mesh
    porch_roof_mesh = bpy.data.meshes.new("MainDwelling_PorchRoof_Monopitch")
    porch_roof_obj = bpy.data.objects.new("MainDwelling_PorchRoof_Simple", porch_roof_mesh)
    bpy.context.collection.objects.link(porch_roof_obj)
    
    # Roof extends with overhang on north, south, and west sides
    porch_roof_east = ox + LENGTH/2  # Flush with building wall
    porch_roof_west = ox + LENGTH/2 + PORCH_DEPTH + PORCH_ROOF_OVERHANG  # Outer edge with overhang
    porch_roof_north = oy - PORCH_WIDTH/2 - PORCH_ROOF_OVERHANG
    porch_roof_south = oy + PORCH_WIDTH/2 + PORCH_ROOF_OVERHANG
    
    porch_verts = [
        # High edge (at building wall)
        (porch_roof_east, porch_roof_north, porch_roof_high_height),  # 0: NE corner (high)
        (porch_roof_east, porch_roof_south, porch_roof_high_height),  # 1: SE corner (high)
        # Low edge (at outer edge)
        (porch_roof_west, porch_roof_north, porch_roof_low_height),   # 2: NW corner (low)
        (porch_roof_west, porch_roof_south, porch_roof_low_height),   # 3: SW corner (low)
    ]
    
    porch_faces = [
        (0, 1, 3, 2),  # Single sloped roof plane
    ]
    
    porch_roof_mesh.from_pydata(porch_verts, [], porch_faces)
    porch_roof_mesh.update()
    porch_roof_obj.data.materials.append(create_corrugated_iron_material())
    
    # === INTERIOR PARTITIONS ===
    _create_interior_partitions_ground_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS)
    _create_interior_partitions_first_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS)
    
    # === ENSUITE FURNITURE ===
    _furnish_master_ensuite(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS)
    
    # === KITCHEN BENCH ===
    _create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
    
    # === WINDOWS AND DOORS ===
    _add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS)
    
    # === GABLE ROOF ===
    if show_roof:
        _create_gable_roof(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, roof_style)
    
    print(f"Main Dwelling with simple open porch built at origin {origin}") 
