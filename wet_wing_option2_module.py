import bpy  # type: ignore
import math

from utils import create_corrugated_iron_material, add_corner_trim, add_window, add_door
import wet_wing_option2_furniture

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_potius_wet_wing_option2(origin=(0,0,0), show_roof=True):  # Set show_roof=False to hide roof
    """
    Build a two-level wet wing with:
    - Lower Level (40m²): 10m x 4m - Entry & Utility wing
    - Upper Level (60m²): 10m x 6m - Sanctuary wing
    
    Layout:
    - Lower: Mudroom (SW corner), staircase, guest suite + bathroom/laundry
    - Upper: Great room (full 10m north wall), master suite (SE corner), deck
    """
    ox, oy, oz = origin
    W, D = 10.0, 6.0  # Changed from 6.0, 6.0 to 10.0 (X-width), 6.0 (Y-depth)
    H_BASE = 2.4
    EXTERIOR_WALL_THICKNESS = 0.15  # 150mm exterior walls
    ROOF_PITCH = 12  # degrees (skillion roof pitch)
    ROOF_HEIGHT_CENTER = 3.2  # meters above origin
    roof_thickness = 0.05
    
    # Calculate wall heights based on mono-pitch roof (north wall is HIGHER)
    # Roof tilts -12° (negative rotation lifts north edge)
    run_to_edge = D/2 + 0.3  # Distance from center to roof edge (5.3m for 10m depth)
    roof_rise = run_to_edge * math.sin(math.radians(ROOF_PITCH))  # ~1.103m (use sin for rotation)
    clearance = 0.03  # 30mm clearance so walls don't poke through roof
    
    # North wall (-Y) is taller, south wall (+Y) is shorter
    H_NORTH = ROOF_HEIGHT_CENTER + roof_rise - (roof_thickness/2) - clearance  # ~4.273m
    H_SOUTH = ROOF_HEIGHT_CENTER - roof_rise - (roof_thickness/2) - clearance  # ~2.073m
    
    # Create red cottage material
    red_mat = create_material("RedCottage", (0.7, 0.05, 0.05, 1))
    
    # Build 4 exterior walls as separate solid boxes
    # North Wall (Higher wall, -Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy - D/2 + EXTERIOR_WALL_THICKNESS/2, oz + H_NORTH/2))
    north_wall = bpy.context.active_object
    north_wall.name = "WetWing2_NorthWall"
    north_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H_NORTH/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall.data.materials.append(red_mat)
    
    # South Wall (Lower wall, +Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy + D/2 - EXTERIOR_WALL_THICKNESS/2, oz + H_SOUTH/2))
    south_wall = bpy.context.active_object
    south_wall.name = "WetWing2_SouthWall"
    south_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H_SOUTH/2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall.data.materials.append(red_mat)
    
    # West Wall (+X side) - Wall with sloped top matching roof
    mesh = bpy.data.meshes.new("WestWallMesh")
    west_wall = bpy.data.objects.new("WetWing2_WestWall", mesh)
    bpy.context.collection.objects.link(west_wall)
    
    # Wall positioned at west side, inner edge accounting for north/south wall thickness
    wall_depth = D - 2*EXTERIOR_WALL_THICKNESS
    half_depth = wall_depth / 2
    half_thick = EXTERIOR_WALL_THICKNESS / 2
    
    verts = [
        # Bottom face
        (-half_thick, -half_depth, 0),  # 0: SW bottom inner
        (half_thick, -half_depth, 0),   # 1: SW bottom outer
        (half_thick, half_depth, 0),    # 2: NW bottom outer
        (-half_thick, half_depth, 0),   # 3: NW bottom inner
        # Top face (north is taller)
        (-half_thick, -half_depth, H_NORTH),  # 4: N top inner
        (half_thick, -half_depth, H_NORTH),   # 5: N top outer
        (half_thick, half_depth, H_SOUTH),    # 6: S top outer
        (-half_thick, half_depth, H_SOUTH),   # 7: S top inner
    ]
    
    faces = [
        (0, 1, 2, 3),    # Bottom
        (4, 5, 6, 7),    # Top (sloped)
        (0, 4, 5, 1),    # North end
        (2, 6, 7, 3),    # South end
        (1, 5, 6, 2),    # Outer face
        (3, 7, 4, 0),    # Inner face
    ]
    
    mesh.from_pydata(verts, [], faces)
    west_wall.location = (ox + W/2 - EXTERIOR_WALL_THICKNESS/2, oy, oz)  # WEST wall at +X (higher X = west)
    west_wall.data.materials.append(red_mat)
    
    # East Wall (-X side) - Mirror of west wall
    mesh = bpy.data.meshes.new("EastWallMesh")
    east_wall = bpy.data.objects.new("WetWing2_EastWall", mesh)
    bpy.context.collection.objects.link(east_wall)
    mesh.from_pydata(verts, [], faces)
    east_wall.location = (ox - W/2 + EXTERIOR_WALL_THICKNESS/2, oy, oz)  # EAST wall at -X (lower X = east)
    east_wall.data.materials.append(red_mat)
    
    # Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + 0.05))
    floor = bpy.context.active_object
    floor.name = "WetWing2_Floor"
    floor.scale = (W/2, D/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    floor.data.materials.append(create_material("FloorWood", (0.5, 0.35, 0.2, 1)))
    
    # Create stairwell opening in floor (west wall, near south edge)
    STAIR_WIDTH_OPENING = 1.3  # slightly larger than stair width for clearance
    STAIR_RUN_OPENING = 3.1  # slightly larger than stair run
    #stairwell_x = ox + W/2 - EXTERIOR_WALL_THICKNESS - STAIR_WIDTH_OPENING/2
    stairwell_x = ox
    stairwell_y = oy + D/2 - 1.5 - STAIR_RUN_OPENING/2  # positioned to align with stairs from below
    
    bpy.ops.mesh.primitive_cube_add(location=(stairwell_x, stairwell_y, oz + 0.05))
    stairwell_cutter = bpy.context.active_object
    stairwell_cutter.name = "StairwellCutter"
    stairwell_cutter.scale = (STAIR_WIDTH_OPENING/2, STAIR_RUN_OPENING/2, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    
    # Boolean difference to cut hole in floor
    bool_mod = floor.modifiers.new(name="StairwellCut", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = stairwell_cutter
    bpy.context.view_layer.objects.active = floor
    bpy.ops.object.modifier_apply(modifier="StairwellCut")
    bpy.data.objects.remove(stairwell_cutter, do_unlink=True)
    
    # === UPPER LEVEL (60m²) - This entire 10m x 6m building ===
    # This is the sanctuary wing - great room with full north wall, master suite
    # The lower level (40m²) is a separate 10m x 4m structure built by build_under_extension()
    # No internal floor division needed - this whole building is one open upper level
    
    # Skillion Roof (HIGH ON NORTH: -Y)
    if show_roof:  # Set show_roof=False in function call to hide roof
        bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + ROOF_HEIGHT_CENTER))
        roof = bpy.context.active_object
        roof.name = "WetWing2_Roof"
        roof.scale = (W/2 + 0.3, D/2 + 0.3, roof_thickness/2)
        roof.rotation_euler = (math.radians(-ROOF_PITCH), 0, 0)
        roof.data.materials.append(create_corrugated_iron_material())
    
    # Add white corner trim to all 4 corners (north corners are taller)
    # North corners use H_NORTH, south corners use H_SOUTH
    trim_mat = create_material("WhiteTrim", (1.0, 1.0, 1.0, 1))
    trim_width = 0.15
    
    # NW Corner (tall)
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2, oy - D/2, oz + H_NORTH/2))
    nw_trim = bpy.context.active_object
    nw_trim.name = "CornerTrim2_NW"
    nw_trim.scale = (trim_width/2, trim_width/2, H_NORTH/2)
    bpy.ops.object.transform_apply(scale=True)
    nw_trim.data.materials.append(trim_mat)
    
    # NE Corner (tall)
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2, oy - D/2, oz + H_NORTH/2))
    ne_trim = bpy.context.active_object
    ne_trim.name = "CornerTrim2_NE"
    ne_trim.scale = (trim_width/2, trim_width/2, H_NORTH/2)
    bpy.ops.object.transform_apply(scale=True)
    ne_trim.data.materials.append(trim_mat)
    
    # SE Corner (shorter)
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2, oy + D/2, oz + H_SOUTH/2))
    se_trim = bpy.context.active_object
    se_trim.name = "CornerTrim2_SE"
    se_trim.scale = (trim_width/2, trim_width/2, H_SOUTH/2)
    bpy.ops.object.transform_apply(scale=True)
    se_trim.data.materials.append(trim_mat)
    
    # SW Corner (shorter)
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2, oy + D/2, oz + H_SOUTH/2))
    sw_trim = bpy.context.active_object
    sw_trim.name = "CornerTrim2_SW"
    sw_trim.scale = (trim_width/2, trim_width/2, H_SOUTH/2)
    bpy.ops.object.transform_apply(scale=True)
    sw_trim.data.materials.append(trim_mat)
    
    # Internal partition wall running north-south, 3.6m from west wall
    INTERNAL_WALL_THICKNESS = 0.1  # 100mm internal wall
    INTERNAL_WALL_HEIGHT = 2.4  # Standard room height
    partition_x = ox + W/2 - 3.6  # 3.6m from west wall
    
    bpy.ops.mesh.primitive_cube_add(location=(partition_x, oy, oz + INTERNAL_WALL_HEIGHT/2))
    partition_wall = bpy.context.active_object
    partition_wall.name = "WetWing2_PartitionWall"
    partition_wall.scale = (INTERNAL_WALL_THICKNESS/2, (D - 2*EXTERIOR_WALL_THICKNESS)/2, INTERNAL_WALL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Use white paint material for internal wall
    white_wall_mat = create_material("WhiteWall", (0.95, 0.95, 0.95, 1))
    partition_wall.data.materials.append(white_wall_mat)
    
    # Internal wall running east-west, 4m south of north wall, connecting west wall to partition
    cross_wall_y = oy - D/2 + 4.0  # 4m south of north wall
    cross_wall_length = 3.6 - EXTERIOR_WALL_THICKNESS  # From west wall inner edge to partition center
    cross_wall_x = ox + W/2 - 3.6/2 - EXTERIOR_WALL_THICKNESS/2  # Centered between west wall and partition
    
    bpy.ops.mesh.primitive_cube_add(location=(cross_wall_x, cross_wall_y, oz + INTERNAL_WALL_HEIGHT/2))
    cross_wall = bpy.context.active_object
    cross_wall.name = "WetWing2_CrossWall"
    cross_wall.scale = (cross_wall_length/2, INTERNAL_WALL_THICKNESS/2, INTERNAL_WALL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    cross_wall.data.materials.append(white_wall_mat)
    
    # Add windows on North face - spread across the 10m wide wall
    add_window("WetWing2_NorthWall", position=(ox-3.3, oy - D/2, oz+1.4), width=2.0, height=1.8, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox-3.3, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox, oy - D/2, oz+1.4), width=2.0, height=1.8, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox+3.3, oy - D/2, oz+1.4), width=2.0, height=1.8, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox+3.3, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    
    # Add windows on West face (+X side) - 6m deep wall
    add_window("WetWing2_WestWall", position=(ox + W/2, oy - D/2 + 1.3, oz + 1.4), width=1.5, height=1.4, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("WetWing2_WestWall", position=(ox + W/2, oy - D/2 + 3.1, oz + 1.4), width=1.5, height=1.4, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("WetWing2_WestWall", position=(ox + W/2, oy - D/2 + 4.9, oz + 1.4), width=1.5, height=1.4, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # Add windows on East face (-X side) - 6m deep wall
    add_window("WetWing2_EastWall", position=(ox - W/2, oy - D/2 + 2.0, oz + 1.6), width=2.2, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    add_window("WetWing2_EastWall", position=(ox - W/2, oy - D/2 + 4.7, oz + 1.0), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')


def build_under_extension(origin=(0,0,0)):
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
    add_window("UnderExt_WestWall", position=(ox + W/2, oy - D/2 + 1.0, oz + 1.5), width=1.2, height=2.5, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("UnderExt_WestWall", position=(ox + W/2, oy - D/2 + 2.9, oz + 1.5), width=1.5, height=1.8, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
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
    
    # Staircase going up from lower to upper level - along west wall, going south
    # Staircase starts near north wall and runs south (towards +Y)
    STAIR_WIDTH = 1.2  # meters wide
    STAIR_RUN = 3.0  # meters long (going south)
    STAIR_HEIGHT = 2.4  # rises to upper level
    NUM_STEPS = 12  # number of individual steps
    STEP_HEIGHT = STAIR_HEIGHT / NUM_STEPS  # 0.2m per step
    STEP_DEPTH = STAIR_RUN / NUM_STEPS  # 0.25m per step
    
    #stair_x = ox + W/2 - EXTERIOR_WALL_THICKNESS - STAIR_WIDTH/2  # Just inside west wall
    stair_x = ox
    stair_start_y = oy - D/2 + 1.5  # Starting 1.5m from north wall
    
    stair_mat = create_material("StairOak", (0.6, 0.45, 0.3, 1))
    
    # Create individual steps
    for step_num in range(NUM_STEPS):
        step_y = stair_start_y + (step_num * STEP_DEPTH) + STEP_DEPTH/2
        step_z = oz + (step_num * STEP_HEIGHT) + STEP_HEIGHT/2
        
        bpy.ops.mesh.primitive_cube_add(location=(stair_x, step_y, step_z))
        step = bpy.context.active_object
        step.name = f"UnderExt_Step_{step_num+1}"
        step.scale = (STAIR_WIDTH/2, STEP_DEPTH/2, STEP_HEIGHT/2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stair_mat)
    
    # Add door on south wall to connect to upper level (at top of stairs)
    #add_door("UnderExt_SouthWall", position=(ox + W/2 - STAIR_WIDTH - 0.5, oy + D/2, oz + STAIR_HEIGHT), width=0.9, height=2.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y')
