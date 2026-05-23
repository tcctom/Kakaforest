import bpy  # type: ignore
import math

from utils import apply_shadowclad_grooves, add_window, create_corrugated_iron_material, add_corner_trim

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
    
    # === GROUND FLOOR EXTERIOR WALLS ===
    # North Wall (recessed NORTH_RECESS inward from north edge)
    # North edge is at oy - WIDTH/2, recess by NORTH_RECESS, position at outer face minus half thickness
    north_wall_y = oy - WIDTH/2 + NORTH_RECESS - EXTERIOR_WALL_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(ox, north_wall_y, oz + GROUND_FLOOR_HEIGHT/2))
    north_wall_ground = bpy.context.active_object
    north_wall_ground.name = "MainDwelling_NorthWall_Ground"
    north_wall_ground.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall_ground.data.materials.append(potius_mat)
    
    # South Wall (extends to full WIDTH)
    south_wall_y = oy + WIDTH/2 - EXTERIOR_WALL_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(ox, south_wall_y, oz + GROUND_FLOOR_HEIGHT/2))
    south_wall_ground = bpy.context.active_object
    south_wall_ground.name = "MainDwelling_SouthWall_Ground"
    south_wall_ground.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall_ground.data.materials.append(potius_mat)
    
    # East Wall (spans FULL 7m north-south, flush with floors and roof)
    east_west_wall_depth = WIDTH  # Full 7m span to match floor/roof edges
    bpy.ops.mesh.primitive_cube_add(location=(ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS/2, oy, oz + GROUND_FLOOR_HEIGHT/2))
    east_wall_ground = bpy.context.active_object
    east_wall_ground.name = "MainDwelling_EastWall_Ground"
    east_wall_ground.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    east_wall_ground.data.materials.append(potius_mat)
    
    # West Wall (spans FULL 7m north-south, flush with floors and roof)
    bpy.ops.mesh.primitive_cube_add(location=(ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS/2, oy, oz + GROUND_FLOOR_HEIGHT/2))
    west_wall_ground = bpy.context.active_object
    west_wall_ground.name = "MainDwelling_WestWall_Ground"
    west_wall_ground.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall_ground.data.materials.append(potius_mat)
    
    # === FIRST FLOOR EXTERIOR WALLS ===
    # North Wall (recessed, same as ground floor)
    bpy.ops.mesh.primitive_cube_add(location=(ox, north_wall_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    north_wall_first = bpy.context.active_object
    north_wall_first.name = "MainDwelling_NorthWall_First"
    north_wall_first.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall_first.data.materials.append(potius_mat)
    
    # South Wall (extends to full WIDTH)
    bpy.ops.mesh.primitive_cube_add(location=(ox, south_wall_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    south_wall_first = bpy.context.active_object
    south_wall_first.name = "MainDwelling_SouthWall_First"
    south_wall_first.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall_first.data.materials.append(potius_mat)
    
    # East Wall (spans FULL 7m north-south, independent of recessed north wall)
    bpy.ops.mesh.primitive_cube_add(location=(ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS/2, oy, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    east_wall_first = bpy.context.active_object
    east_wall_first.name = "MainDwelling_EastWall_First"
    east_wall_first.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    east_wall_first.data.materials.append(potius_mat)
    
    # West Wall (spans FULL 7m north-south, independent of recessed north wall)
    bpy.ops.mesh.primitive_cube_add(location=(ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS/2, oy, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    west_wall_first = bpy.context.active_object
    west_wall_first.name = "MainDwelling_WestWall_First"
    west_wall_first.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall_first.data.materials.append(potius_mat)


def _create_floors(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat):
    """Create ground floor and first floor slabs"""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    
    # Floor dimensions: fit within exterior walls
    floor_length = LENGTH - 2 * EXTERIOR_WALL_THICKNESS  # East-west, inside walls
    floor_width = WIDTH  # North-south, full width to match roof
    
    # Ground Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + 0.05))
    ground_floor = bpy.context.active_object
    ground_floor.name = "MainDwelling_GroundFloor"
    ground_floor.scale = (floor_length/2, floor_width/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    ground_floor.data.materials.append(floor_mat)
    
    # First Floor with stairs opening
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, first_floor_z - 0.05))
    first_floor_slab = bpy.context.active_object
    first_floor_slab.name = "MainDwelling_FirstFloor"
    first_floor_slab.scale = (floor_length/2, floor_width/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    first_floor_slab.data.materials.append(floor_mat)
    
    # Stairs opening in first floor slab (just west of 4m bedroom partition line for alignment verification)
    stairs_opening_x = ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS + 4.7  # 0.5m west of bedroom partition
    stairs_opening_y = oy - 0.5  # Slightly north of center
    
    # Create stairs cutter manually (2.2m N-S × 1.2m E-W)
    bpy.ops.mesh.primitive_cube_add(location=(stairs_opening_x, stairs_opening_y, first_floor_z - 0.05))
    stairs_cutter = bpy.context.active_object
    stairs_cutter.name = "MainDwelling_StairsCutter"
    stairs_cutter.scale = (1.2/2, 2.2/2, 0.05)  # E-W width, N-S length, floor thickness
    bpy.ops.object.transform_apply(scale=True)
    
    # Boolean modifier to cut opening in floor
    bool_mod = first_floor_slab.modifiers.new(name="Stairs_Cut", type='BOOLEAN')
    bool_mod.object = stairs_cutter
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.solver = 'EXACT'
    
    # Hide the cutter
    stairs_cutter.hide_viewport = True
    stairs_cutter.hide_render = True
    
    # Create stairs to match the opening
    STAIR_WIDTH = 1.0  # E-W width (fits within 1.2m opening)
    NUM_STEPS = 12  # 12 steps (13th step is the first floor itself)
    STAIR_RISE = GROUND_FLOOR_HEIGHT / (NUM_STEPS+1)  # ~208mm rise per step
    STAIR_TREAD = 2.2 / NUM_STEPS  # Tread depth spanning 2.2m N-S
    
    stairs_mat = create_material("StairsWood", (0.6, 0.4, 0.25, 1))
    
    # Create individual steps (starting from north, going south)
    for i in range(NUM_STEPS):
        step_height = oz + STAIR_RISE * (i + 1)  # Full rise for each step
        step_y = stairs_opening_y + 2.2/2 - STAIR_TREAD * (i + 0.5)  # Start from north, move south
        
        bpy.ops.mesh.primitive_cube_add(location=(stairs_opening_x, step_y, step_height))
        step = bpy.context.active_object
        step.name = f"MainDwelling_Stairs_Step_{i+1:02d}"
        step.scale = (STAIR_WIDTH/2, STAIR_TREAD/2, STAIR_RISE/2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stairs_mat)


def _create_interior_partitions_ground_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Create ground floor interior partitions for guest bedroom with built-in wardrobe
    
    Args:
        WIDTH: Total building width (7m - full roof span)
        ENCLOSED_WIDTH: Enclosed building width (6m - north wall recessed)
        NORTH_RECESS: Distance north wall is recessed from north edge (1m)
    """
    interior_wall_mat = create_material("InteriorWall", (0.9, 0.9, 0.85, 1))
    
    # Guest bedroom in NE corner: 4m (E-W) × 3m (N-S)
    GUEST_BEDROOM_WIDTH = 4.0   # E-W dimension
    GUEST_BEDROOM_DEPTH = 3.0   # N-S dimension
    
    # Interior reference points (north wall recessed from north edge by NORTH_RECESS)
    east_interior_face = ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS
    north_interior_face = oy - WIDTH/2 + NORTH_RECESS
    
    # Ground floor wall height (slightly shorter to avoid poking through first floor slab)
    FLOOR_SLAB_THICKNESS = 0.1
    ground_floor_wall_height = GROUND_FLOOR_HEIGHT - FLOOR_SLAB_THICKNESS
    
    # West partition wall (N-S) - separates guest bedroom from rest of ground floor
    # Position so that east face of wall is exactly GUEST_BEDROOM_WIDTH from east interior face
    west_partition_x = east_interior_face + GUEST_BEDROOM_WIDTH + INTERIOR_WALL_THICKNESS/2
    west_partition_center_y = north_interior_face + GUEST_BEDROOM_DEPTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(west_partition_x, west_partition_center_y, oz + ground_floor_wall_height/2))
    west_partition = bpy.context.active_object
    west_partition.name = "MainDwelling_GroundFloor_GuestBedroomWestWall"
    west_partition.scale = (INTERIOR_WALL_THICKNESS/2, GUEST_BEDROOM_DEPTH/2, ground_floor_wall_height/2)
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
    door_x = east_interior_face + 2.5
    add_window("MainDwelling_GroundFloor_GuestBedroomSouthWall", (door_x, south_partition_y + INTERIOR_WALL_THICKNESS/2, oz + 1.0), 
               width=0.9, height=2.0, depth=INTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')


def _create_interior_partitions_first_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Create first floor interior partitions for master bedroom, ensuite, and wardrobe
    
    Args:
        WIDTH: Total building width (7m - full roof span)
        ENCLOSED_WIDTH: Enclosed building width (6m - north wall recessed)
        NORTH_RECESS: Distance north wall is recessed from north edge (1m)
    """
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    interior_wall_mat = create_material("InteriorWall", (0.9, 0.9, 0.85, 1))
    
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
    add_window("MainDwelling_FirstFloor_MainPartition", (main_partition_x - INTERIOR_WALL_THICKNESS/2, oy - 2.3, first_floor_z + 1.0), 
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
    add_window("MainDwelling_NorthWall_Ground", (ox - spacing, north_wall_interior_face, window_z_ground), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    #add_window("MainDwelling_NorthWall_Ground", (ox, north_wall_interior_face, window_z_ground), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_NorthWall_Ground", (ox + spacing, north_wall_interior_face, window_z_ground), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # FIRST FLOOR - NORTH WALL (recessed) - position at interior face
    add_window("MainDwelling_NorthWall_First", (ox - spacing, north_wall_interior_face, window_z_first), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_NorthWall_First", (ox + spacing, north_wall_interior_face, window_z_first), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # GROUND FLOOR - EAST WALL (spans full 7m)
    add_window("MainDwelling_EastWall_Ground", (ox - LENGTH/2, oy - 2, oz + 1.2), width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    add_window("MainDwelling_EastWall_Ground", (ox - LENGTH/2, oy + 2, oz + 1.2), width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # FIRST FLOOR - EAST WALL (spans full 7m)
    add_window("MainDwelling_EastWall_First", (ox - LENGTH/2, oy - 2, first_floor_z + 1.2), width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    add_window("MainDwelling_EastWall_First", (ox - LENGTH/2, oy + 2, first_floor_z + 1.2), width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # GROUND FLOOR - WEST WALL (spans full 7m)
    add_window("MainDwelling_WestWall_Ground", (ox + LENGTH/2, oy - 1.5, oz + 1.4), width=0.5, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MainDwelling_WestWall_Ground", (ox + LENGTH/2, oy + 1.5, oz + 1.4), width=0.5, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # FIRST FLOOR - WEST WALL (spans full 7m)
    add_window("MainDwelling_WestWall_First", (ox + LENGTH/2, oy - 1.5, first_floor_z + 1.2), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MainDwelling_WestWall_First", (ox + LENGTH/2, oy + 1.5, first_floor_z + 1.2), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # GROUND FLOOR - SOUTH WALL (full width)
    add_window("MainDwelling_SouthWall_Ground", (ox - south_spacing, south_wall_y, oz + 1.0), width=1.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_SouthWall_Ground", (ox, south_wall_y, oz + 1.4), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_SouthWall_Ground", (ox + south_spacing, south_wall_y, oz + 1.4), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # FIRST FLOOR - SOUTH WALL (full width)
    add_window("MainDwelling_SouthWall_First", (ox - 3.2, south_wall_y, first_floor_z + 1.2), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_SouthWall_First", (ox - 1.0, south_wall_y, first_floor_z + 1.2), width=0.6, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_SouthWall_First", (ox + south_spacing, south_wall_y, first_floor_z + 1.2), width=2.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')


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
    floor_mat = create_material("FloorWood", (0.5, 0.35, 0.2, 1))
    
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
    floor_mat = create_material("FloorWood", (0.5, 0.35, 0.2, 1))
    
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
    
    # === WINDOWS AND DOORS ===
    _add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS)
    
    # === GABLE ROOF ===
    if show_roof:
        _create_gable_roof(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, roof_style)
    
    print(f"Main Dwelling with simple open porch built at origin {origin}") 
