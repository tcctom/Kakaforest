import bpy  # type: ignore
import math

from utils import create_corrugated_iron_material, add_corner_trim, add_window, add_door

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build(origin=(0,0,0)):
    """
    Build a 10m (X) by 4m (Y) extension module that sits underneath the main wet wing.
    This has flat-topped walls at 2.4m height with no roof (roof is provided by main building above).
    
    Args:
        origin: (x, y, z) tuple for the south edge of this extension (which connects to main wet wing north wall)
    """
    ox, oy, oz = origin
    W, D = 10.0, 4.0  # 10m wide (X), 4m deep (Y)
    H = 2.4  # Simple flat wall height
    EXTERIOR_WALL_THICKNESS = 0.15  # 150mm exterior walls
    
    # Create red cottage material
    red_mat = create_material("RedCottage", (0.7, 0.05, 0.05, 1))
    
    # Build 4 simple walls - all same height
    # North Wall (Front of extension, -Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy - D/2 + EXTERIOR_WALL_THICKNESS/2, oz + H/2))
    north_wall = bpy.context.active_object
    north_wall.name = "UnderExt_NorthWall"
    north_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall.data.materials.append(red_mat)
    
    # South Wall (+Y side) - Connects to main wet wing
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy + D/2 - EXTERIOR_WALL_THICKNESS/2, oz + H/2))
    south_wall = bpy.context.active_object
    south_wall.name = "UnderExt_SouthWall"
    south_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall.data.materials.append(red_mat)
    
    # West Wall (+X side)
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2 - EXTERIOR_WALL_THICKNESS/2, oy, oz + H/2))
    west_wall = bpy.context.active_object
    west_wall.name = "UnderExt_WestWall"
    west_wall.scale = (EXTERIOR_WALL_THICKNESS/2, (D - 2*EXTERIOR_WALL_THICKNESS)/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall.data.materials.append(red_mat)
    
    # East Wall (-X side)
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2 + EXTERIOR_WALL_THICKNESS/2, oy, oz + H/2))
    east_wall = bpy.context.active_object
    east_wall.name = "UnderExt_EastWall"
    east_wall.scale = (EXTERIOR_WALL_THICKNESS/2, (D - 2*EXTERIOR_WALL_THICKNESS)/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    east_wall.data.materials.append(red_mat)
    
    # Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + 0.05))
    floor = bpy.context.active_object
    floor.name = "UnderExt_Floor"
    floor.scale = (W/2, D/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    floor.data.materials.append(create_material("FloorWood", (0.5, 0.35, 0.2, 1)))
    
    # Add corner trim (all same height)
    trim_mat = create_material("WhiteTrim", (1.0, 1.0, 1.0, 1))
    trim_width = 0.15
    
    # NW Corner
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2, oy - D/2, oz + H/2))
    nw_trim = bpy.context.active_object
    nw_trim.name = "UnderExtTrim_NW"
    nw_trim.scale = (trim_width/2, trim_width/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    nw_trim.data.materials.append(trim_mat)
    
    # NE Corner
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2, oy - D/2, oz + H/2))
    ne_trim = bpy.context.active_object
    ne_trim.name = "UnderExtTrim_NE"
    ne_trim.scale = (trim_width/2, trim_width/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    ne_trim.data.materials.append(trim_mat)
    
    # SE Corner
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2, oy + D/2, oz + H/2))
    se_trim = bpy.context.active_object
    se_trim.name = "UnderExtTrim_SE"
    se_trim.scale = (trim_width/2, trim_width/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    se_trim.data.materials.append(trim_mat)
    
    # SW Corner
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2, oy + D/2, oz + H/2))
    sw_trim = bpy.context.active_object
    sw_trim.name = "UnderExtTrim_SW"
    sw_trim.scale = (trim_width/2, trim_width/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    sw_trim.data.materials.append(trim_mat)
    
    # Add windows on North face - spread across the 10m wide wall
    add_window("UnderExt_NorthWall", position=(ox-3.0, oy - D/2, oz+1.1), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS)
    add_window("UnderExt_NorthWall", position=(ox-0.0, oy - D/2, oz+1.1), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS)
    add_window("UnderExt_NorthWall", position=(ox+3.3, oy - D/2, oz+1.1), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS)
    
    # Add windows on West and East walls - 4m deep walls
    add_window("UnderExt_WestWall", position=(ox + W/2, oy - D/2 + 1.0, oz + 1.5), width=1.8, height=1.4, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("UnderExt_WestWall", position=(ox + W/2, oy - D/2 + 2.4, oz + 1.5), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    add_window("UnderExt_EastWall", position=(ox - W/2, oy + D/2 - 1.0, oz + 1.2), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # === VERANDAH on North Face ===
    # 10m wide x 1.5m deep verandah extending north from the building
    VERANDAH_DEPTH = 1.5  # extends 1.5m in -Y direction
    VERANDAH_THICKNESS = 0.15  # deck thickness
    VERANDAH_HEIGHT = oz  # at ground level
    VERANDAH_ROOF_HEIGHT = 2.3  # roof height above ground
    
    # Verandah deck
    verandah_y = oy - D/2 - VERANDAH_DEPTH/2  # centered 1.5m north of north wall
    bpy.ops.mesh.primitive_cube_add(location=(ox, verandah_y, VERANDAH_HEIGHT + VERANDAH_THICKNESS/2))
    verandah_deck = bpy.context.active_object
    verandah_deck.name = "UnderExt_VerandahDeck"
    verandah_deck.scale = (W/2, VERANDAH_DEPTH/2, VERANDAH_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    verandah_deck.data.materials.append(create_material("DeckWood", (0.6, 0.45, 0.3, 1)))
    
    # Support posts for verandah (4 posts along the north edge - going all the way to roof)
    POST_WIDTH = 0.1
    POST_HEIGHT = VERANDAH_ROOF_HEIGHT - 0.05  # from ground to just below roof surface
    post_mat = create_material("PostWood", (0.45, 0.35, 0.25, 1))
    
    post_positions_x = [ox - W/2 + 1.0, ox - W/2 + W/3, ox + W/2 - W/3, ox + W/2 - 1.0]  # 4 posts along width
    post_y = oy - D/2 - VERANDAH_DEPTH + POST_WIDTH/2  # at north edge of verandah
    
    for i, post_x in enumerate(post_positions_x):
        bpy.ops.mesh.primitive_cube_add(location=(post_x, post_y, POST_HEIGHT/2))
        post = bpy.context.active_object
        post.name = f"UnderExt_VerandahPost_{i+1}"
        post.scale = (POST_WIDTH/2, POST_WIDTH/2, POST_HEIGHT/2)
        bpy.ops.object.transform_apply(scale=True)
        post.data.materials.append(post_mat)
    
    # Verandah roof - corrugated iron with slight pitch
    ROOF_THICKNESS = 0.05
    ROOF_OVERHANG = 0.2  # Extra overhang beyond posts
    ROOF_PITCH = 5  # degrees, slight pitch for drainage
    
    verandah_roof_y = oy - D/2 - VERANDAH_DEPTH/2  # centered over verandah
    bpy.ops.mesh.primitive_cube_add(location=(ox, verandah_roof_y, oz + VERANDAH_ROOF_HEIGHT))
    verandah_roof = bpy.context.active_object
    verandah_roof.name = "UnderExt_VerandahRoof"
    verandah_roof.scale = ((W + ROOF_OVERHANG)/2, (VERANDAH_DEPTH + ROOF_OVERHANG)/2, ROOF_THICKNESS/2)
    verandah_roof.rotation_euler = (math.radians(ROOF_PITCH), 0, 0)  # Pitch slopes away from building (north edge lower)
    bpy.ops.object.transform_apply(scale=True)
    verandah_roof.data.materials.append(create_corrugated_iron_material())
    
    # Add entrance door on East wall near north wall - Mudroom entrance
    entrance_y_position = oy - D/2 + 0.8  # 0.8m from north wall
    add_door("UnderExt_EastWall", position=(ox - W/2, entrance_y_position, oz), width=1.1, height=2.2, depth=EXTERIOR_WALL_THICKNESS, axis='X')
    
    # Staircase going up from lower to upper level - L-shaped with landing
    # First run: starts near north wall and runs south (towards +Y) for 6 steps
    # Landing at step 6, then turns 90 degrees
    # Second run: turns east (towards -X) for remaining 6 steps
    STAIR_WIDTH = 1.2  # meters wide
    STAIR_HEIGHT = 2.4  # rises to upper level
    NUM_STEPS = 12  # number of individual steps
    STEP_HEIGHT = STAIR_HEIGHT / NUM_STEPS  # 0.2m per step
    STEP_DEPTH = 0.25  # 0.25m per step
    
    # First run configuration (steps 1-6, going south)
    FIRST_RUN_STEPS = 6
    stair_x = ox + 0.6  # X position for first run
    stair_start_y = oy - D/2 + 1.4  # Starting 1.4m from north wall
    
    # Landing configuration
    LANDING_SIZE = 1.2  # 1.2m × 1.2m landing
    landing_height = FIRST_RUN_STEPS * STEP_HEIGHT  # 1.2m high
    landing_y = stair_start_y + (FIRST_RUN_STEPS * STEP_DEPTH) + 0.4  # After 6 steps, plus 0.4m clearance
    landing_x = stair_x  # Same X as first run
    
    # Second run configuration (steps 7-12, going east/-X)
    SECOND_RUN_STEPS = NUM_STEPS - FIRST_RUN_STEPS  # 6 steps
    second_run_start_x = landing_x  # Start from landing position
    second_run_y = landing_y  # Y position for second run
    
    stair_mat = create_material("StairOak", (0.6, 0.45, 0.3, 1))
    
    # Create first run of steps (1-8, going south/+Y)
    for step_num in range(FIRST_RUN_STEPS):
        step_y = stair_start_y + (step_num * STEP_DEPTH) + STEP_DEPTH/2
        step_z = oz + (step_num * STEP_HEIGHT) + STEP_HEIGHT/2
        
        bpy.ops.mesh.primitive_cube_add(location=(stair_x, step_y, step_z))
        step = bpy.context.active_object
        step.name = f"UnderExt_Step_{step_num+1}"
        step.scale = (STAIR_WIDTH/2, STEP_DEPTH/2, STEP_HEIGHT/2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stair_mat)
    
    # Create landing platform at step 8
    landing_z = oz + landing_height
    bpy.ops.mesh.primitive_cube_add(location=(landing_x, landing_y, landing_z))
    landing = bpy.context.active_object
    landing.name = "UnderExt_Landing"
    landing.scale = (LANDING_SIZE/2, LANDING_SIZE/2, STEP_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    landing.data.materials.append(stair_mat)
    
    # Create second run of steps (9-12, going east/-X)
    for step_num in range(SECOND_RUN_STEPS):
        step_x = second_run_start_x - (step_num * STEP_DEPTH) - STEP_DEPTH/2 - LANDING_SIZE/2
        step_z = oz + (FIRST_RUN_STEPS + step_num) * STEP_HEIGHT + STEP_HEIGHT/2
        
        bpy.ops.mesh.primitive_cube_add(location=(step_x, second_run_y, step_z))
        step = bpy.context.active_object
        step.name = f"UnderExt_Step_{FIRST_RUN_STEPS + step_num + 1}"
        step.scale = (STEP_DEPTH/2, STAIR_WIDTH/2, STEP_HEIGHT/2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stair_mat)
    
    # === CREATE STAIRWELL OPENING IN UPPER FLOOR ===
    # This cuts an L-shaped hole in the floor above to allow the stairs to pass through
    upper_floor_z = oz + STAIR_HEIGHT  # Upper floor is at this height
    OPENING_CLEARANCE = 0.1  # Extra clearance around stairs
    
    # Get the upper floor object
    upper_floor = bpy.data.objects.get("WetWing2_Floor")
    if upper_floor:
        # First opening: for the first run (going south/+Y)
        first_run_opening_width = STAIR_WIDTH + OPENING_CLEARANCE
        first_run_opening_length = (FIRST_RUN_STEPS * STEP_DEPTH) + OPENING_CLEARANCE
        first_opening_x = stair_x
        first_opening_y = stair_start_y + first_run_opening_length/2
        
        bpy.ops.mesh.primitive_cube_add(location=(first_opening_x, first_opening_y, upper_floor_z + 0.05))
        first_cutter = bpy.context.active_object
        first_cutter.name = "StairwellCutter1"
        first_cutter.scale = (first_run_opening_width/2, first_run_opening_length/2, 0.1)
        bpy.ops.object.transform_apply(scale=True)
        
        # Boolean difference to cut first opening
        bool_mod1 = upper_floor.modifiers.new(name="StairwellCut1", type='BOOLEAN')
        bool_mod1.operation = 'DIFFERENCE'
        bool_mod1.object = first_cutter
        bpy.context.view_layer.objects.active = upper_floor
        bpy.ops.object.modifier_apply(modifier="StairwellCut1")
        bpy.data.objects.remove(first_cutter, do_unlink=True)
        
        # Second opening: for the landing and second run (going east/-X)
        second_run_opening_width = (SECOND_RUN_STEPS * STEP_DEPTH) + LANDING_SIZE + OPENING_CLEARANCE
        second_run_opening_length = STAIR_WIDTH + OPENING_CLEARANCE
        second_opening_x = landing_x - second_run_opening_width/2 + LANDING_SIZE/2
        second_opening_y = landing_y
        
        bpy.ops.mesh.primitive_cube_add(location=(second_opening_x, second_opening_y, upper_floor_z + 0.05))
        second_cutter = bpy.context.active_object
        second_cutter.name = "StairwellCutter2"
        second_cutter.scale = (second_run_opening_width/2, second_run_opening_length/2, 0.1)
        bpy.ops.object.transform_apply(scale=True)
        
        # Boolean difference to cut second opening
        bool_mod2 = upper_floor.modifiers.new(name="StairwellCut2", type='BOOLEAN')
        bool_mod2.operation = 'DIFFERENCE'
        bool_mod2.object = second_cutter
        bpy.context.view_layer.objects.active = upper_floor
        bpy.ops.object.modifier_apply(modifier="StairwellCut2")
        bpy.data.objects.remove(second_cutter, do_unlink=True)
    
    # Stairwell partition wall - on west side of stairwell, extending from lower to upper floor
    # This wall follows the first run of stairs (going south)
    INTERNAL_WALL_THICKNESS = 0.1  # 100mm internal wall
    stairwell_partition_x = ox + 1.2  # West edge of stairwell (matches partition_x in upper level)
    first_run_length = FIRST_RUN_STEPS * STEP_DEPTH  # Length of first stair run
    stairwell_partition_y = stair_start_y + first_run_length/2  # Centered along first run
    white_wall_mat = create_material("WhiteWall", (0.95, 0.95, 0.95, 1))
    
    bpy.ops.mesh.primitive_cube_add(location=(stairwell_partition_x, stairwell_partition_y, oz + STAIR_HEIGHT/2))
    stairwell_partition = bpy.context.active_object
    stairwell_partition.name = "UnderExt_StairwellPartition"
    stairwell_partition.scale = (INTERNAL_WALL_THICKNESS/2, first_run_length/2, STAIR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    stairwell_partition.data.materials.append(white_wall_mat)
    
    # === LOG BURNER (Wood Stove) ===
    # Positioned east of the stairs with opening facing east
    LOG_BURNER_WIDTH = 0.6  # meters (Y-direction)
    LOG_BURNER_DEPTH = 0.5  # meters (X-direction)
    LOG_BURNER_HEIGHT = 0.8  # meters (main body height)
    LOG_BURNER_LEG_HEIGHT = 0.15  # meters (legs below body)
    FLUE_DIAMETER = 0.15  # meters
    FLUE_HEIGHT = 2.2  # meters (goes up to near ceiling)
    
    # Position east of stairs
    log_burner_x = ox - 0.3  # East of stairs (ox + 0.6 is stair position)
    log_burner_y = oy - D/2 + 2.0  # Near middle of north section
    
    # Create materials
    stove_mat = create_material("CastIronStove", (0.15, 0.15, 0.15, 1))  # Dark iron
    flue_mat = create_material("StoveFlue", (0.2, 0.2, 0.2, 1))
    
    # Stove legs
    bpy.ops.mesh.primitive_cube_add(location=(log_burner_x, log_burner_y, oz + LOG_BURNER_LEG_HEIGHT/2))
    stove_legs = bpy.context.active_object
    stove_legs.name = "UnderExt_StoveLegs"
    stove_legs.scale = (LOG_BURNER_DEPTH/2, LOG_BURNER_WIDTH/2, LOG_BURNER_LEG_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    stove_legs.data.materials.append(stove_mat)
    
    # Main stove body
    stove_body_z = oz + LOG_BURNER_LEG_HEIGHT + LOG_BURNER_HEIGHT/2
    bpy.ops.mesh.primitive_cube_add(location=(log_burner_x, log_burner_y, stove_body_z))
    stove_body = bpy.context.active_object
    stove_body.name = "UnderExt_StoveBody"
    stove_body.scale = (LOG_BURNER_DEPTH/2, LOG_BURNER_WIDTH/2, LOG_BURNER_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    stove_body.data.materials.append(stove_mat)
    
    # Stove door/opening indicator (small panel on east face)
    door_thickness = 0.05
    door_width = 0.35
    door_height = 0.4
    door_x = log_burner_x - LOG_BURNER_DEPTH/2 - door_thickness/2  # East face (-X)
    door_z = stove_body_z
    
    bpy.ops.mesh.primitive_cube_add(location=(door_x, log_burner_y, door_z))
    stove_door = bpy.context.active_object
    stove_door.name = "UnderExt_StoveDoor"
    stove_door.scale = (door_thickness/2, door_width/2, door_height/2)
    bpy.ops.object.transform_apply(scale=True)
    stove_door.data.materials.append(create_material("StoveDoorGlass", (0.1, 0.1, 0.1, 0.3)))
    
    # Flue pipe going up
    flue_start_z = oz + LOG_BURNER_LEG_HEIGHT + LOG_BURNER_HEIGHT
    flue_z = flue_start_z + FLUE_HEIGHT/2
    
    bpy.ops.mesh.primitive_cylinder_add(radius=FLUE_DIAMETER/2, depth=FLUE_HEIGHT, location=(log_burner_x, log_burner_y, flue_z))
    flue_pipe = bpy.context.active_object
    flue_pipe.name = "UnderExt_FluePipe"
    flue_pipe.data.materials.append(flue_mat)
    
    # Add door on south wall to connect to upper level (at top of stairs)
    #add_door("UnderExt_SouthWall", position=(ox + W/2 - STAIR_WIDTH - 0.5, oy + D/2, oz + STAIR_HEIGHT), width=0.9, height=2.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y')


def furniture(origin=(0,0,0), building_width=10.0, building_depth=4.0, exterior_wall_thickness=0.15):
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
    
    # === KITCHEN (South Wall) ===
    # Kitchen counter along south wall
    KITCHEN_LENGTH = 3.6  # meters along south wall
    KITCHEN_DEPTH = 0.65  # meters extending into room (northward)
    KITCHEN_HEIGHT = 0.9
    KITCHEN_TOP_THICKNESS = 0.04
    
    kitchen_x = ox + W/2 - EXTERIOR_WALL_THICKNESS - KITCHEN_LENGTH/2  
    kitchen_y = oy + D/2 - EXTERIOR_WALL_THICKNESS - KITCHEN_DEPTH/2
    kitchen_z = oz + KITCHEN_HEIGHT/2
    
    # Kitchen base cabinets
    bpy.ops.mesh.primitive_cube_add(location=(kitchen_x, kitchen_y, kitchen_z))
    kitchen_base = bpy.context.active_object
    kitchen_base.name = "UnderExt_KitchenBase"
    kitchen_base.scale = (KITCHEN_LENGTH/2, KITCHEN_DEPTH/2, KITCHEN_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    kitchen_base.data.materials.append(create_material("KitchenCabinet", (0.3, 0.25, 0.2, 1)))
    
    # Kitchen countertop
    kitchen_top_z = oz + KITCHEN_HEIGHT + KITCHEN_TOP_THICKNESS/2
    
    bpy.ops.mesh.primitive_cube_add(location=(kitchen_x, kitchen_y, kitchen_top_z))
    kitchen_top = bpy.context.active_object
    kitchen_top.name = "UnderExt_KitchenCounter"
    kitchen_top.scale = ((KITCHEN_LENGTH + 0.05)/2, (KITCHEN_DEPTH + 0.05)/2, KITCHEN_TOP_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    kitchen_top.data.materials.append(create_material("WhiteCountertop", (0.88, 0.85, 0.8, 1)))
    
    # === DINING AREA (West Side) ===
    # Dining table - seats 8 comfortably
    DINING_TABLE_LENGTH = 1.1  # meters (Y-direction) - seats 3 per side + 1 per end
    DINING_TABLE_WIDTH = 2.2  # meters (X-direction)
    DINING_TABLE_HEIGHT = 0.75  # meters - standard dining height
    TABLE_TOP_THICKNESS = 0.05  # meters
    
    dining_table_x = ox + W/2 - EXTERIOR_WALL_THICKNESS - DINING_TABLE_WIDTH/2 - 0.2
    dining_table_y = oy - D/2 + DINING_TABLE_LENGTH/2 + 0.9  # Centered in space
    dining_table_z = oz + DINING_TABLE_HEIGHT/2
    
    # Table base/legs
    bpy.ops.mesh.primitive_cube_add(location=(dining_table_x, dining_table_y, dining_table_z))
    table_base = bpy.context.active_object
    table_base.name = "UnderExt_DiningTableBase"
    table_base.scale = (DINING_TABLE_WIDTH/2, DINING_TABLE_LENGTH/2, DINING_TABLE_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    table_base.data.materials.append(create_material("TableWood", (0.4, 0.3, 0.2, 1)))
    
    # Table top
    table_top_z = oz + DINING_TABLE_HEIGHT + TABLE_TOP_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(dining_table_x, dining_table_y, table_top_z))
    table_top = bpy.context.active_object
    table_top.name = "UnderExt_DiningTableTop"
    table_top.scale = ((DINING_TABLE_WIDTH + 0.1)/2, (DINING_TABLE_LENGTH + 0.1)/2, TABLE_TOP_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    table_top.data.materials.append(create_material("TableTopOak", (0.55, 0.4, 0.25, 1)))
    
    