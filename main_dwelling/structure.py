import bpy  # type: ignore
import bmesh
import mathutils

from materials import get_interior_wall_material
from main_dwelling.materials_nodes import create_laminate_floor_material, create_material


def _create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat):
    """Create all exterior walls for ground and first floors with recessed north wall."""
    wall_depth_ground = ENCLOSED_WIDTH - 2 * EXTERIOR_WALL_THICKNESS
    first_floor_z = oz + GROUND_FLOOR_HEIGHT

    interior_wall_mat = get_interior_wall_material()
    print(f"Creating exterior walls at origin ({ox}, {oy}, {oz}) with dimensions: WIDTH={WIDTH}, ENCLOSED_WIDTH={ENCLOSED_WIDTH}, LENGTH={LENGTH}, GROUND_FLOOR_HEIGHT={GROUND_FLOOR_HEIGHT}, FIRST_FLOOR_HEIGHT={FIRST_FLOOR_HEIGHT}, EXTERIOR_WALL_THICKNESS={EXTERIOR_WALL_THICKNESS}, NORTH_RECESS={NORTH_RECESS}")
    print(f"oy : {oy}, WIDTH: {WIDTH}, NORTH_RECESS: {NORTH_RECESS}, EXTERIOR_WALL_THICKNESS: {EXTERIOR_WALL_THICKNESS}")
    north_wall_y = oy + WIDTH / 2 - NORTH_RECESS - EXTERIOR_WALL_THICKNESS / 2 + 0.01

    bpy.ops.mesh.primitive_cube_add(location=(ox, north_wall_y, oz + GROUND_FLOOR_HEIGHT / 2))
    north_wall_ground = bpy.context.active_object
    north_wall_ground.name = "MD_GF_NorthWall"
    north_wall_ground.scale = (LENGTH / 2, EXTERIOR_WALL_THICKNESS / 2, GROUND_FLOOR_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall_ground.data.materials.append(potius_mat)
    north_wall_ground.data.materials.append(interior_wall_mat)
    north_wall_ground.data.polygons[3].material_index = 1

    south_wall_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS / 2
    bpy.ops.mesh.primitive_cube_add(location=(ox, south_wall_y, oz + GROUND_FLOOR_HEIGHT / 2))
    south_wall_ground = bpy.context.active_object
    south_wall_ground.name = "MD_GF_SouthWall"
    south_wall_ground.scale = (LENGTH / 2, EXTERIOR_WALL_THICKNESS / 2, GROUND_FLOOR_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall_ground.data.materials.append(potius_mat)
    south_wall_ground.data.materials.append(interior_wall_mat)
    south_wall_ground.data.polygons[1].material_index = 1

    east_west_wall_depth = WIDTH
    bpy.ops.mesh.primitive_cube_add(location=(ox + LENGTH / 2 - EXTERIOR_WALL_THICKNESS / 2, oy, oz + GROUND_FLOOR_HEIGHT / 2))
    east_wall_ground = bpy.context.active_object
    east_wall_ground.name = "MD_GF_EastWall"
    east_wall_ground.scale = (EXTERIOR_WALL_THICKNESS / 2, east_west_wall_depth / 2, GROUND_FLOOR_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    east_wall_ground.data.materials.append(potius_mat)
    east_wall_ground.data.materials.append(interior_wall_mat)
    east_wall_ground.data.polygons[0].material_index = 1

    bpy.ops.mesh.primitive_cube_add(location=(ox - LENGTH / 2 + EXTERIOR_WALL_THICKNESS / 2, oy, oz + GROUND_FLOOR_HEIGHT / 2))
    west_wall_ground = bpy.context.active_object
    west_wall_ground.name = "MD_GF_WestWall"
    west_wall_ground.scale = (EXTERIOR_WALL_THICKNESS / 2, east_west_wall_depth / 2, GROUND_FLOOR_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall_ground.data.materials.append(potius_mat)
    west_wall_ground.data.materials.append(interior_wall_mat)
    west_wall_ground.data.polygons[2].material_index = 1

    north_wall_first_height = FIRST_FLOOR_HEIGHT + 0.65
    bpy.ops.mesh.primitive_cube_add(location=(ox, north_wall_y, first_floor_z + north_wall_first_height / 2))
    north_wall_first = bpy.context.active_object
    north_wall_first.name = "MD_FF_NorthWall"
    north_wall_first.scale = (LENGTH / 2, EXTERIOR_WALL_THICKNESS / 2, north_wall_first_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall_first.data.materials.append(potius_mat)
    north_wall_first.data.materials.append(interior_wall_mat)
    north_wall_first.data.polygons[3].material_index = 1

    bpy.ops.mesh.primitive_cube_add(location=(ox, south_wall_y, first_floor_z + FIRST_FLOOR_HEIGHT / 2))
    south_wall_first = bpy.context.active_object
    south_wall_first.name = "MD_FF_SouthWall"
    south_wall_first.scale = (LENGTH / 2, EXTERIOR_WALL_THICKNESS / 2, FIRST_FLOOR_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall_first.data.materials.append(potius_mat)
    south_wall_first.data.materials.append(interior_wall_mat)
    south_wall_first.data.polygons[1].material_index = 1

    bpy.ops.mesh.primitive_cube_add(location=(ox + LENGTH / 2 - EXTERIOR_WALL_THICKNESS / 2, oy, first_floor_z + FIRST_FLOOR_HEIGHT / 2))
    east_wall_first = bpy.context.active_object
    east_wall_first.name = "MD_FF_EastWall"
    east_wall_first.scale = (EXTERIOR_WALL_THICKNESS / 2, east_west_wall_depth / 2, FIRST_FLOOR_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    east_wall_first.data.materials.append(potius_mat)
    east_wall_first.data.materials.append(interior_wall_mat)
    east_wall_first.data.polygons[0].material_index = 1

    bpy.ops.mesh.primitive_cube_add(location=(ox - LENGTH / 2 + EXTERIOR_WALL_THICKNESS / 2, oy, first_floor_z + FIRST_FLOOR_HEIGHT / 2))
    west_wall_first = bpy.context.active_object
    west_wall_first.name = "MD_FF_WestWall"
    west_wall_first.scale = (EXTERIOR_WALL_THICKNESS / 2, east_west_wall_depth / 2, FIRST_FLOOR_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall_first.data.materials.append(potius_mat)
    west_wall_first.data.materials.append(interior_wall_mat)
    west_wall_first.data.polygons[2].material_index = 1


def _create_180_degree_staircase_southwest(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS,  floor_mat):
    """Create 180-degree dog-legged staircase in southwest corner with clockwise turn."""
    GROUND_FLOOR_SLAB_THICKNESS = 0.1
    FIRST_FLOOR_SLAB_THICKNESS = 0.2
    ground_floor_top = oz + GROUND_FLOOR_SLAB_THICKNESS
    first_floor_top = oz + GROUND_FLOOR_HEIGHT + FIRST_FLOOR_SLAB_THICKNESS
    TOTAL_RISE = first_floor_top - ground_floor_top
    STAIRWELL_WIDTH = 2.0
    STAIRWELL_LENGTH = 3.0
    FLIGHT_WIDTH = 0.95
    LANDING_DEPTH = 1.0
    LANDING_HEIGHT = TOTAL_RISE / 2

    STEPS_PER_FLIGHT = 7
    STEP_RISE = TOTAL_RISE / (STEPS_PER_FLIGHT * 2)
    STEP_TREAD = 0.28
    MODELED_STEPS_PER_FLIGHT = STEPS_PER_FLIGHT - 1


    west_interior_x = ox - LENGTH / 2 + EXTERIOR_WALL_THICKNESS
    south_interior_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS

    stairwell_west_x = west_interior_x
    stairwell_east_x = west_interior_x + STAIRWELL_WIDTH
    stairwell_south_y = south_interior_y
    stairwell_north_y = south_interior_y + STAIRWELL_LENGTH

    stairs_mat = create_material("StairsWood", (0.6, 0.4, 0.25, 1))
    landing_mat = floor_mat

    flight1_x = stairwell_east_x - FLIGHT_WIDTH / 2 
    landing_north_y = stairwell_south_y + LANDING_DEPTH
    flight1_start_y = landing_north_y + (MODELED_STEPS_PER_FLIGHT * STEP_TREAD) - (STEP_TREAD / 2)

    for i in range(MODELED_STEPS_PER_FLIGHT):
        step_height = ground_floor_top + STEP_RISE * (i + 0.5)
        step_y = flight1_start_y - (i * STEP_TREAD)

        bpy.ops.mesh.primitive_cube_add(location=(flight1_x, step_y, step_height))
        step = bpy.context.active_object
        step.name = f"MainDwelling_Stairs_Flight1_Step_{i + 1:02d}"
        step.scale = (FLIGHT_WIDTH / 2, STEP_TREAD / 2, STEP_RISE / 2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stairs_mat)

    landing_x = (stairwell_west_x + stairwell_east_x) / 2
    landing_y = stairwell_south_y + LANDING_DEPTH / 2
    landing_top_z = ground_floor_top + LANDING_HEIGHT
    landing_z = landing_top_z - 0.075

    bpy.ops.mesh.primitive_cube_add(location=(landing_x, landing_y, landing_z))
    landing = bpy.context.active_object
    landing.name = "MainDwelling_Stairs_Landing"
    landing.scale = (STAIRWELL_WIDTH / 2, LANDING_DEPTH / 2, 0.11)
    bpy.ops.object.transform_apply(scale=True)
    landing.data.materials.append(landing_mat)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    flight2_x = stairwell_west_x + FLIGHT_WIDTH / 2 
    flight2_start_y = stairwell_south_y + LANDING_DEPTH + STEP_TREAD / 2

    for i in range(MODELED_STEPS_PER_FLIGHT):
        step_height = landing_top_z + STEP_RISE * (i + 0.5)
        step_y = flight2_start_y + (i * STEP_TREAD)

        bpy.ops.mesh.primitive_cube_add(location=(flight2_x, step_y, step_height))
        step = bpy.context.active_object
        step.name = f"MainDwelling_Stairs_Flight2_Step_{i + 1:02d}"
        step.scale = (FLIGHT_WIDTH / 2, STEP_TREAD / 2, STEP_RISE / 2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stairs_mat)

    # Stairwell opening is now created directly in first-floor slab geometry in _create_floors.

    print("180-degree staircase created in southwest corner")
    print(f"  Flight 1 (EAST edge): {MODELED_STEPS_PER_FLIGHT} modeled treads + landing as final tread")
    print(f"  Landing (SOUTH edge): {LANDING_HEIGHT}m height, spans East-West")
    print(f"  Flight 2 (WEST edge): {MODELED_STEPS_PER_FLIGHT} modeled treads + floor as final tread")
    print(f"  Stairwell footprint: {STAIRWELL_WIDTH}m × {STAIRWELL_LENGTH}m")
    print(f"  Step rise: {STEP_RISE * 1000:.1f}mm, tread: {STEP_TREAD * 1000:.0f}mm")

def _create_staircase_southmiddle2(ox, oy, oz,  floor_mat):
    """Create a staircase near south-middle."""
    STEP_TREAD = 0.20
    STEP_WIDTH = 0.92
    STEP_RISE = 0.186

    landing_x_offset = 0.5 * STEP_TREAD + 0.5 * STEP_WIDTH
    landing_y_offset = 0.5 * STEP_WIDTH + 0.5 * STEP_TREAD

    create_step(ox, oy, oz, 0, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox+STEP_TREAD, oy, oz, 1, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox+2 * STEP_TREAD, oy, oz, 2, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox+3 * STEP_TREAD, oy , oz, 3, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox+4 * STEP_TREAD, oy , oz, 4, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox+5 * STEP_TREAD, oy , oz, 5, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)

    # Calculate the exact X offset required for the larger landing block
    landing_x = ox + (6 * STEP_TREAD) - (STEP_TREAD / 2) + (STEP_WIDTH / 2)
    create_step(landing_x, oy, oz, 6, floor_mat, STEP_WIDTH, STEP_WIDTH, STEP_RISE, chop="diagonal2a")
    create_step(landing_x, oy, oz, 7, floor_mat, STEP_WIDTH, STEP_WIDTH, STEP_RISE, chop="diagonal2b")
    create_step(landing_x, oy+STEP_WIDTH, oz, 8, floor_mat, STEP_WIDTH, STEP_WIDTH, STEP_RISE, chop="diagonal1a")
    create_step(landing_x, oy+STEP_WIDTH, oz, 9, floor_mat, STEP_WIDTH, STEP_WIDTH, STEP_RISE, chop="diagonal1b")

    create_step(ox+5 * STEP_TREAD, oy+STEP_WIDTH, oz, 10, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox+4 * STEP_TREAD, oy+STEP_WIDTH, oz, 11, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox+3 * STEP_TREAD, oy+STEP_WIDTH, oz, 12, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox+2 * STEP_TREAD, oy+STEP_WIDTH, oz, 13, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    #create_step(ox+1 * STEP_TREAD, oy+STEP_WIDTH, oz, 14, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    #create_step(ox, oy+STEP_WIDTH, oz, 15, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)

def _create_staircase_southmiddle3(ox, oy, oz,  floor_mat):
    """Create a staircase near south-middle."""
    STEP_TREAD = 0.20
    STEP_WIDTH = 1.05
    STEP_RISE = 0.186

    ox = ox + 0.5

    create_step(ox-STEP_TREAD/2, oy, oz, 0, floor_mat, STEP_TREAD*2, STEP_WIDTH, STEP_RISE,chop="diagonal2b")
    create_step(ox-STEP_TREAD/2, oy, oz, 1, floor_mat, STEP_TREAD*2, STEP_WIDTH, STEP_RISE,chop="diagonal2a")
    #create_step(ox, oy, oz, 0, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    #create_step(ox-STEP_TREAD, oy, oz, 1, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-2 * STEP_TREAD, oy, oz, 2, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-3 * STEP_TREAD, oy , oz, 3, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-4 * STEP_TREAD, oy , oz, 4, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-5 * STEP_TREAD, oy , oz, 5, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-6 * STEP_TREAD, oy, oz, 6, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-7 * STEP_TREAD, oy, oz, 7, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-8 * STEP_TREAD, oy, oz, 8, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-9 * STEP_TREAD, oy, oz, 9, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-10 * STEP_TREAD, oy, oz, 10, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-11 * STEP_TREAD, oy, oz, 11, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-12 * STEP_TREAD, oy, oz, 12, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)


    #landing_x_offset = 0.5 * STEP_TREAD + 0.5 * STEP_WIDTH
    #landing_y_offset = 0.5 * STEP_WIDTH + 0.5 * STEP_TREAD
    #create_step(ox-5 * STEP_TREAD - landing_x_offset, oy , oz, 6, floor_mat, STEP_WIDTH, STEP_WIDTH, STEP_RISE)
    #create_step(ox-5 * STEP_TREAD - landing_x_offset, oy + landing_y_offset , oz, 7, floor_mat, STEP_WIDTH, STEP_TREAD,STEP_RISE)
    #create_step(ox-5 * STEP_TREAD - landing_x_offset, oy + landing_y_offset + STEP_TREAD , oz, 8, floor_mat, STEP_WIDTH, STEP_TREAD,STEP_RISE)
    #create_step(ox-5 * STEP_TREAD - landing_x_offset, oy + landing_y_offset + 2*STEP_TREAD , oz, 9, floor_mat, STEP_WIDTH, STEP_TREAD,STEP_RISE)
    #create_step(ox-5 * STEP_TREAD - landing_x_offset, oy + landing_y_offset + 3*STEP_TREAD , oz, 10, floor_mat, STEP_WIDTH, STEP_TREAD,STEP_RISE)

def _create_staircase_southmiddle4(ox, oy, oz,  floor_mat):
    """Create a staircase near south-middle."""
    STEP_TREAD = 0.24
    STEP_WIDTH = 0.95
    STEP_RISE = 0.186

    create_step(ox, oy, oz, 0, floor_mat, STEP_WIDTH, STEP_TREAD, STEP_RISE)
    create_step(ox,oy-STEP_TREAD, oz, 1, floor_mat, STEP_WIDTH, STEP_TREAD, STEP_RISE)

    create_step(ox,oy-STEP_TREAD*1.5-STEP_WIDTH/2, oz, 2, floor_mat, STEP_WIDTH, STEP_WIDTH, STEP_RISE,chop="diagonal2b")
    create_step(ox,oy-STEP_TREAD*1.5-STEP_WIDTH/2, oz, 3, floor_mat, STEP_WIDTH, STEP_WIDTH, STEP_RISE,chop="diagonal2a")


    ox = ox + 0.43
    oy = oy - 0.85
    create_step(ox-4 * STEP_TREAD, oy, oz, 4, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-5 * STEP_TREAD, oy, oz, 5, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-6 * STEP_TREAD, oy, oz, 6, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-7 * STEP_TREAD, oy, oz, 7, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-8 * STEP_TREAD, oy, oz, 8, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-9 * STEP_TREAD, oy, oz, 9, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-10 * STEP_TREAD, oy, oz, 10, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-11 * STEP_TREAD, oy, oz, 11, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    create_step(ox-12 * STEP_TREAD, oy, oz, 12, floor_mat, STEP_TREAD, STEP_WIDTH, STEP_RISE)
    #create_step(ox-10.5 * STEP_TREAD-STEP_WIDTH/2, oy, oz, 11, floor_mat, STEP_WIDTH, STEP_WIDTH, STEP_RISE,chop="diagonal1a")
    #create_step(ox-10.5 * STEP_TREAD-STEP_WIDTH/2, oy, oz, 12, floor_mat, STEP_WIDTH, STEP_WIDTH, STEP_RISE,chop="diagonal1b")





def create_step(step_x, step_y, oz, step_number, floor_mat, STEP_X_SIZE, STEP_Y_SIZE, STEP_RISE, chop="none"):
    """
    Create a single step or one of four sharp triangular diagonal corner steps.
    
    diagonal1a / 1b: Split from Bottom-Left (-X,-Y) to Top-Right (+X,+Y)
    diagonal2a / 2b: Split from Top-Left (-X,+Y) to Bottom-Right (+X,-Y)
    """
    step_height = oz + STEP_RISE * (step_number + 0.5)
    
    # 1. Create a blank mesh data container and link it to an object
    mesh_data = bpy.data.meshes.new(name=f"MD_Stairs_Step_Mesh_{step_number + 1:02d}")
    step = bpy.data.objects.new(f"MD_Stairs_Step_{step_number + 1:02d}", mesh_data)
    bpy.context.collection.objects.link(step)
    
    # Set global position and apply material
    step.location = (step_x, step_y, step_height)
    step.data.materials.append(floor_mat)
    
    # Initialize an empty bmesh structure
    bm = bmesh.new()
    
    # Define local half-dimensions relative to object origin (0, 0, 0)
    hx = STEP_X_SIZE / 2
    hy = STEP_Y_SIZE / 2
    hz = STEP_RISE / 2
    
    if chop == "none":
        # Standard 8-vertex Box Step
        v1 = bm.verts.new((-hx, -hy, -hz))
        v2 = bm.verts.new((hx, -hy, -hz))
        v3 = bm.verts.new((hx, hy, -hz))
        v4 = bm.verts.new((-hx, hy, -hz))
        v5 = bm.verts.new((-hx, -hy, hz))
        v6 = bm.verts.new((hx, -hy, hz))
        v7 = bm.verts.new((hx, hy, hz))
        v8 = bm.verts.new((-hx, hy, hz))
        
        # Build the 6 faces of the standard cube step
        bm.faces.new((v1, v2, v3, v4)) # Bottom
        bm.faces.new((v5, v6, v7, v8)) # Top
        bm.faces.new((v1, v2, v6, v5)) # Front
        bm.faces.new((v2, v3, v7, v6)) # Right
        bm.faces.new((v3, v4, v8, v7)) # Back
        bm.faces.new((v4, v1, v5, v8)) # Left
        
    elif chop == "diagonal1a":
        # Diagonal from Bottom-Left to Top-Right (Keeps Bottom-Right Half)
        v1 = bm.verts.new((-hx, -hy, -hz))
        v2 = bm.verts.new((hx, -hy, -hz))
        v3 = bm.verts.new((hx, hy, -hz))
        
        v4 = bm.verts.new((-hx, -hy, hz))
        v5 = bm.verts.new((hx, -hy, hz))
        v6 = bm.verts.new((hx, hy, hz))
        
        bm.faces.new((v1, v2, v3))     # Bottom
        bm.faces.new((v4, v6, v5))     # Top
        bm.faces.new((v1, v2, v5, v4)) # Front Side
        bm.faces.new((v2, v3, v6, v5)) # Right Side
        bm.faces.new((v3, v1, v4, v6)) # Diagonal Chopped Side

    elif chop == "diagonal1b":
        # Diagonal from Bottom-Left to Top-Right (Keeps Top-Left Half)
        v1 = bm.verts.new((-hx, -hy, -hz))
        v2 = bm.verts.new((hx, hy, -hz))
        v3 = bm.verts.new((-hx, hy, -hz))
        
        v4 = bm.verts.new((-hx, -hy, hz))
        v5 = bm.verts.new((hx, hy, hz))
        v6 = bm.verts.new((-hx, hy, hz))
        
        bm.faces.new((v1, v3, v2))     # Bottom
        bm.faces.new((v4, v5, v6))     # Top
        bm.faces.new((v1, v2, v5, v4)) # Diagonal Chopped Side
        bm.faces.new((v2, v3, v6, v5)) # Back Side
        bm.faces.new((v3, v1, v4, v6)) # Left Side

    elif chop == "diagonal2a":
        # Diagonal from Top-Left to Bottom-Right (Keeps Bottom-Left Half)
        v1 = bm.verts.new((-hx, -hy, -hz))
        v2 = bm.verts.new((hx, -hy, -hz))
        v3 = bm.verts.new((-hx, hy, -hz))
        
        v4 = bm.verts.new((-hx, -hy, hz))
        v5 = bm.verts.new((hx, -hy, hz))
        v6 = bm.verts.new((-hx, hy, hz))
        
        bm.faces.new((v1, v3, v2))     # Bottom
        bm.faces.new((v4, v5, v6))     # Top
        bm.faces.new((v1, v2, v5, v4)) # Front Side
        bm.faces.new((v2, v3, v6, v5)) # Diagonal Chopped Side
        bm.faces.new((v3, v1, v4, v6)) # Left Side

    elif chop == "diagonal2b":
        # Diagonal from Top-Left to Bottom-Right (Keeps Top-Right Half)
        v1 = bm.verts.new((hx, -hy, -hz))
        v2 = bm.verts.new((hx, hy, -hz))
        v3 = bm.verts.new((-hx, hy, -hz))
        
        v4 = bm.verts.new((hx, -hy, hz))
        v5 = bm.verts.new((hx, hy, hz))
        v6 = bm.verts.new((-hx, hy, hz))
        
        bm.faces.new((v1, v2, v3))     # Bottom
        bm.faces.new((v4, v6, v5))     # Top
        bm.faces.new((v1, v2, v5, v4)) # Right Side
        bm.faces.new((v2, v3, v6, v5)) # Back Side
        bm.faces.new((v3, v1, v4, v6)) # Diagonal Chopped Side

    # Finalize the vertex definitions and geometry data
    bm.to_mesh(mesh_data)
    bm.free()
    mesh_data.update()
    
    # Ensure the newly instantiated step remains selected and active in the viewport context
    bpy.context.view_layer.objects.active = step
    return step


def _create_180_degree_staircase_southmiddle(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS,  floor_mat):
    """Create a 180-degree dog-legged staircase near south-middle, rotated 90 degrees."""
    GROUND_FLOOR_SLAB_THICKNESS = 0.1
    FIRST_FLOOR_SLAB_THICKNESS = 0.2
    ground_floor_top = oz + GROUND_FLOOR_SLAB_THICKNESS
    first_floor_top = oz + GROUND_FLOOR_HEIGHT + FIRST_FLOOR_SLAB_THICKNESS
    TOTAL_RISE = first_floor_top - ground_floor_top
    # Rotated 90 degrees from the southwest variant: run direction is along X.
    STAIRWELL_WIDTH = 3.0
    STAIRWELL_LENGTH = 2.0
    FLIGHT_WIDTH = 0.95
    LANDING_DEPTH = 1.0
    LANDING_HEIGHT = TOTAL_RISE / 2

    STEPS_PER_FLIGHT = 7
    STEP_RISE = TOTAL_RISE / (STEPS_PER_FLIGHT * 2)
    STEP_TREAD = 0.28
    MODELED_STEPS_PER_FLIGHT = STEPS_PER_FLIGHT - 1


    west_interior_x = ox -2
    south_interior_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS

    stairwell_west_x = west_interior_x
    stairwell_east_x = west_interior_x + STAIRWELL_WIDTH
    stairwell_south_y = south_interior_y
    stairwell_north_y = south_interior_y + STAIRWELL_LENGTH

    stairs_mat = create_material("StairsWood", (0.6, 0.4, 0.25, 1))
    landing_mat = floor_mat

    flight1_y = stairwell_south_y + FLIGHT_WIDTH / 2
    flight1_start_x = stairwell_west_x + LANDING_DEPTH + STEP_TREAD / 2

    for i in range(MODELED_STEPS_PER_FLIGHT):
        step_height = ground_floor_top + STEP_RISE * (i + 0.5)
        step_x = flight1_start_x + (i * STEP_TREAD)

        bpy.ops.mesh.primitive_cube_add(location=(step_x, flight1_y, step_height))
        step = bpy.context.active_object
        step.name = f"MainDwelling_Stairs_Flight1_Step_{i + 1:02d}"
        step.scale = (STEP_TREAD / 2, FLIGHT_WIDTH / 2, STEP_RISE / 2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stairs_mat)

    landing_x = stairwell_east_x - LANDING_DEPTH / 2
    landing_y = (stairwell_south_y + stairwell_north_y) / 2
    landing_top_z = ground_floor_top + LANDING_HEIGHT
    landing_z = landing_top_z - 0.075

    bpy.ops.mesh.primitive_cube_add(location=(landing_x, landing_y, landing_z))
    landing = bpy.context.active_object
    landing.name = "MainDwelling_Stairs_Landing"
    landing.scale = (LANDING_DEPTH / 2, STAIRWELL_LENGTH / 2, 0.11)
    bpy.ops.object.transform_apply(scale=True)
    landing.data.materials.append(landing_mat)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    flight2_y = stairwell_north_y - FLIGHT_WIDTH / 2
    flight2_start_x = stairwell_east_x - LANDING_DEPTH - STEP_TREAD / 2

    for i in range(MODELED_STEPS_PER_FLIGHT):
        step_height = landing_top_z + STEP_RISE * (i + 0.5)
        step_x = flight2_start_x - (i * STEP_TREAD)

        bpy.ops.mesh.primitive_cube_add(location=(step_x, flight2_y, step_height))
        step = bpy.context.active_object
        step.name = f"MainDwelling_Stairs_Flight2_Step_{i + 1:02d}"
        step.scale = (STEP_TREAD / 2, FLIGHT_WIDTH / 2, STEP_RISE / 2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stairs_mat)

    # Stairwell opening is now created directly in first-floor slab geometry in _create_floors.

    print("180-degree staircase created in south-middle, rotated 90 degrees")
    print(f"  Flight 1 (SOUTH edge): {MODELED_STEPS_PER_FLIGHT} modeled treads + landing as final tread")
    print(f"  Landing (EAST edge): {LANDING_HEIGHT}m height, spans South-North")
    print(f"  Flight 2 (NORTH edge): {MODELED_STEPS_PER_FLIGHT} modeled treads + floor as final tread")
    print(f"  Stairwell footprint: {STAIRWELL_WIDTH}m × {STAIRWELL_LENGTH}m")
    print(f"  Step rise: {STEP_RISE * 1000:.1f}mm, tread: {STEP_TREAD * 1000:.0f}mm")


def _create_floors(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat):
    """Create ground floor and first floor slabs with laminate texture on top surfaces only."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT

    floor_length = LENGTH - 2 * EXTERIOR_WALL_THICKNESS
    floor_width = WIDTH - EXTERIOR_WALL_THICKNESS
    floor_center_y = oy + EXTERIOR_WALL_THICKNESS / 2

    laminate_mat = create_laminate_floor_material()
    white_ceiling_mat = create_material("WhiteCeiling", (1.0, 1.0, 1.0, 1.0))

    bpy.ops.mesh.primitive_cube_add(location=(ox, floor_center_y, oz + 0.05))
    ground_floor = bpy.context.active_object
    ground_floor.name = "MainDwelling_GroundFloor"
    ground_floor.scale = (floor_length / 2, floor_width / 2, 0.05)
    bpy.ops.object.transform_apply(scale=True)

    ground_floor.data.materials.append(floor_mat)
    ground_floor.data.materials.append(laminate_mat)

    for i, poly in enumerate(ground_floor.data.polygons):
        if poly.normal.z > 0.9:
            poly.material_index = 1
            print(f"Ground floor: Assigned laminate to polygon {i} (top face)")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Build first-floor slab with a built-in stairwell opening in the southwest corner.
    first_floor_thickness = 0.2
    first_floor_center_z = first_floor_z + first_floor_thickness / 2

    stairwell_width = 2.0
    stairwell_length = 3.0

    west_interior_x = ox - LENGTH / 2 + EXTERIOR_WALL_THICKNESS
    south_interior_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS
    opening_east_x = west_interior_x + stairwell_width
    opening_north_y = south_interior_y + stairwell_length - 0.3

    floor_west_x = ox - floor_length / 2
    floor_east_x = ox + floor_length / 2
    floor_south_y = floor_center_y - floor_width / 2
    floor_north_y = floor_center_y + floor_width / 2

    slab_parts = []

    # North strip (full width) above stairwell opening.
    north_strip_depth = floor_north_y - opening_north_y
    if north_strip_depth > 0:
        north_strip_center_y = (opening_north_y + floor_north_y) / 2
        bpy.ops.mesh.primitive_cube_add(location=(ox, north_strip_center_y, first_floor_center_z))
        north_strip = bpy.context.active_object
        north_strip.name = "MD_FirstFloor_NorthStrip"
        north_strip.scale = (floor_length / 2, north_strip_depth / 2, first_floor_thickness / 2)
        bpy.ops.object.transform_apply(scale=True)
        slab_parts.append(north_strip)

    # Southeast block below north strip and east of opening.
    se_width = floor_east_x - opening_east_x
    se_depth = opening_north_y - floor_south_y
    if se_width > 0 and se_depth > 0:
        se_center_x = (opening_east_x + floor_east_x) / 2
        se_center_y = (floor_south_y + opening_north_y) / 2
        bpy.ops.mesh.primitive_cube_add(location=(se_center_x, se_center_y, first_floor_center_z))
        southeast_block = bpy.context.active_object
        southeast_block.name = "MD_FirstFloor_SouthEastBlock"
        southeast_block.scale = (se_width / 2, se_depth / 2, first_floor_thickness / 2)
        bpy.ops.object.transform_apply(scale=True)
        slab_parts.append(southeast_block)

    if not slab_parts:
        raise RuntimeError("Failed to create first-floor slab parts for stairwell opening")

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in slab_parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = slab_parts[0]
    if len(slab_parts) > 1:
        bpy.ops.object.join()
    first_floor_slab = bpy.context.view_layer.objects.active
    first_floor_slab.name = "MD_FirstFloor"

    first_floor_slab.data.materials.append(floor_mat)
    first_floor_slab.data.materials.append(laminate_mat)
    first_floor_slab.data.materials.append(white_ceiling_mat)

    for i, poly in enumerate(first_floor_slab.data.polygons):
        if poly.normal.z > 0.9:
            poly.material_index = 1
            print(f"First floor: Assigned laminate to polygon {i} (top face)")
        elif poly.normal.z < -0.9:
            poly.material_index = 2
            print(f"First floor: Assigned white ceiling to polygon {i} (bottom face)")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

def _create_floors2(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat):
    """Create ground floor and first floor slabs with laminate texture on top surfaces only."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT

    floor_length = LENGTH - 2 * EXTERIOR_WALL_THICKNESS
    floor_width = WIDTH - EXTERIOR_WALL_THICKNESS
    floor_center_y = oy + EXTERIOR_WALL_THICKNESS / 2

    laminate_mat = create_laminate_floor_material()
    white_ceiling_mat = create_material("WhiteCeiling", (1.0, 1.0, 1.0, 1.0))

    bpy.ops.mesh.primitive_cube_add(location=(ox, floor_center_y, oz + 0.05))
    ground_floor = bpy.context.active_object
    ground_floor.name = "MainDwelling_GroundFloor"
    ground_floor.scale = (floor_length / 2, floor_width / 2, 0.05)
    bpy.ops.object.transform_apply(scale=True)

    ground_floor.data.materials.append(floor_mat)
    ground_floor.data.materials.append(laminate_mat)

    for i, poly in enumerate(ground_floor.data.polygons):
        if poly.normal.z > 0.9:
            poly.material_index = 1
            print(f"Ground floor: Assigned laminate to polygon {i} (top face)")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Build first-floor slab with a built-in stairwell opening in the southwest corner.
    first_floor_thickness = 0.2
    first_floor_center_z = first_floor_z + first_floor_thickness / 2

    stairwell_width = 1.9
    stairwell_length = 2.32

    opening_west_x = ox - 0.13 
    opening_east_x = opening_west_x + stairwell_length
    opening_south_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS
    opening_north_y = opening_south_y + stairwell_width 

    floor_west_x = ox - floor_length / 2
    floor_east_x = ox + floor_length / 2
    floor_south_y = floor_center_y - floor_width / 2
    floor_north_y = floor_center_y + floor_width / 2

    slab_parts = []

    # North strip (full width) above stairwell opening.
    north_strip_depth = floor_north_y - opening_north_y
    if north_strip_depth > 0:
        north_strip_center_y = (opening_north_y + floor_north_y) / 2
        bpy.ops.mesh.primitive_cube_add(location=(ox, north_strip_center_y, first_floor_center_z))
        north_strip = bpy.context.active_object
        north_strip.name = "MD_FirstFloor_NorthStrip"
        north_strip.scale = (floor_length / 2, north_strip_depth / 2, first_floor_thickness / 2)
        bpy.ops.object.transform_apply(scale=True)
        slab_parts.append(north_strip)

    # Southeast block below north strip and east of opening.
    se_width = floor_east_x - opening_east_x
    se_depth = opening_north_y - floor_south_y
    print(f"  SE width = {se_width:.2f}, SE depth = {se_depth:.2f}")
    if se_width > 0 and se_depth > 0:
        se_center_x = (opening_east_x + floor_east_x) / 2
        se_center_y = (floor_south_y + opening_north_y) / 2
        bpy.ops.mesh.primitive_cube_add(location=(se_center_x, se_center_y, first_floor_center_z))
        southeast_block = bpy.context.active_object
        southeast_block.name = "MD_FirstFloor_SouthEastBlock"
        southeast_block.scale = (se_width / 2, se_depth / 2, first_floor_thickness / 2)
        bpy.ops.object.transform_apply(scale=True)
        slab_parts.append(southeast_block)

    # Southwest block below north strip and west of opening.
    sw_width = 4.8 #opening_west_x - floor_west_x
    sw_depth = 1 #opening_north_y - floor_south_y
    print(f"  SW width = {sw_width:.2f}, SW depth = {sw_depth:.2f}")
    bpy.ops.mesh.primitive_cube_add(location=(-1.9, -3, first_floor_center_z))
    southwest_block = bpy.context.active_object
    southwest_block.name = "MD_FirstFloor_SouthWestBlock"
    southwest_block.scale = (sw_width / 2, sw_depth / 2, first_floor_thickness / 2)
    bpy.ops.object.transform_apply(scale=True)
    slab_parts.append(southwest_block)

    sw_width = 3.0
    sw_depth = 0.95
    print(f"  SW width = {sw_width:.2f}, SW depth = {sw_depth:.2f}")
    bpy.ops.mesh.primitive_cube_add(location=(-2.8, -3.9, first_floor_center_z))
    southwest_block = bpy.context.active_object
    southwest_block.name = "MD_FirstFloor_SouthWestBlock"
    southwest_block.scale = (sw_width / 2, sw_depth / 2, first_floor_thickness / 2)
    bpy.ops.object.transform_apply(scale=True)
    slab_parts.append(southwest_block)   

    if not slab_parts:
        raise RuntimeError("Failed to create first-floor slab parts for stairwell opening")

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in slab_parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = slab_parts[0]
    if len(slab_parts) > 1:
        bpy.ops.object.join()
    first_floor_slab = bpy.context.view_layer.objects.active
    first_floor_slab.name = "MD_FirstFloor"

    first_floor_slab.data.materials.append(floor_mat)
    first_floor_slab.data.materials.append(laminate_mat)
    first_floor_slab.data.materials.append(white_ceiling_mat)

    for i, poly in enumerate(first_floor_slab.data.polygons):
        if poly.normal.z > 0.9:
            poly.material_index = 1
            print(f"First floor: Assigned laminate to polygon {i} (top face)")
        elif poly.normal.z < -0.9:
            poly.material_index = 2
            print(f"First floor: Assigned white ceiling to polygon {i} (bottom face)")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

def _create_floors3(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat):
    """Create ground floor and first floor slabs with laminate texture on top surfaces only."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT

    floor_length = LENGTH - 2 * EXTERIOR_WALL_THICKNESS
    floor_width = WIDTH - EXTERIOR_WALL_THICKNESS
    floor_center_y = oy + EXTERIOR_WALL_THICKNESS / 2

    laminate_mat = create_laminate_floor_material()
    white_ceiling_mat = create_material("WhiteCeiling", (1.0, 1.0, 1.0, 1.0))

    bpy.ops.mesh.primitive_cube_add(location=(ox, floor_center_y, oz + 0.05))
    ground_floor = bpy.context.active_object
    ground_floor.name = "MainDwelling_GroundFloor"
    ground_floor.scale = (floor_length / 2, floor_width / 2, 0.05)
    bpy.ops.object.transform_apply(scale=True)

    ground_floor.data.materials.append(floor_mat)
    ground_floor.data.materials.append(laminate_mat)

    for i, poly in enumerate(ground_floor.data.polygons):
        if poly.normal.z > 0.9:
            poly.material_index = 1
            print(f"Ground floor: Assigned laminate to polygon {i} (top face)")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Build first-floor slab with a built-in stairwell opening in the southwest corner.
    first_floor_thickness = 0.2
    first_floor_center_z = first_floor_z + first_floor_thickness / 2

    stairwell_width = 1.2
    stairwell_length = 4.0

    opening_west_x = ox - floor_length / 2 + 2.5
    opening_east_x = opening_west_x + stairwell_length
    opening_south_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS
    opening_north_y = opening_south_y + stairwell_width 

    floor_west_x = ox - floor_length / 2
    floor_east_x = ox + floor_length / 2
    floor_south_y = floor_center_y - floor_width / 2
    floor_north_y = floor_center_y + floor_width / 2

    slab_parts = []

    # North strip (full width) above stairwell opening.
    north_strip_depth = floor_north_y - opening_north_y
    if north_strip_depth > 0:
        north_strip_center_y = (opening_north_y + floor_north_y) / 2
        bpy.ops.mesh.primitive_cube_add(location=(ox, north_strip_center_y, first_floor_center_z))
        north_strip = bpy.context.active_object
        north_strip.name = "MD_FirstFloor_NorthStrip"
        north_strip.scale = (floor_length / 2, north_strip_depth / 2, first_floor_thickness / 2)
        bpy.ops.object.transform_apply(scale=True)
        slab_parts.append(north_strip)

    # Southeast block below north strip and east of opening.
    se_width = floor_east_x - opening_east_x
    se_depth = opening_north_y - floor_south_y
    print(f"  SE width = {se_width:.2f}, SE depth = {se_depth:.2f}, floor_east_x = {floor_east_x:.2f}, opening_east_x = {opening_east_x:.2f}, floor_south_y = {floor_south_y:.2f}, opening_north_y = {opening_north_y:.2f}")
    if se_width > 0 and se_depth > 0:
        se_center_x = (opening_east_x + floor_east_x) / 2
        se_center_y = (floor_south_y + opening_north_y) / 2
        bpy.ops.mesh.primitive_cube_add(location=(se_center_x, se_center_y, first_floor_center_z))
        southeast_block = bpy.context.active_object
        southeast_block.name = "MD_FirstFloor_SouthEastBlock"
        southeast_block.scale = (se_width / 2, se_depth / 2, first_floor_thickness / 2)
        bpy.ops.object.transform_apply(scale=True)
        slab_parts.append(southeast_block)


    sw_width = opening_west_x - ox + floor_length / 2 
    sw_depth = 1.25
    print(f"  SW width = {sw_width:.2f}, SW depth = {sw_depth:.2f}")
    bpy.ops.mesh.primitive_cube_add(location=(opening_west_x - sw_width / 2, se_center_y, first_floor_center_z))
    southwest_block = bpy.context.active_object
    southwest_block.name = "MD_FirstFloor_SouthWestBlock"
    southwest_block.scale = (sw_width / 2, sw_depth / 2, first_floor_thickness / 2)
    bpy.ops.object.transform_apply(scale=True)
    slab_parts.append(southwest_block)   

    if not slab_parts:
        raise RuntimeError("Failed to create first-floor slab parts for stairwell opening")

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in slab_parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = slab_parts[0]
    if len(slab_parts) > 1:
        bpy.ops.object.join()
    first_floor_slab = bpy.context.view_layer.objects.active
    first_floor_slab.name = "MD_FirstFloor"

    first_floor_slab.data.materials.append(floor_mat)
    first_floor_slab.data.materials.append(laminate_mat)
    first_floor_slab.data.materials.append(white_ceiling_mat)

    for i, poly in enumerate(first_floor_slab.data.polygons):
        if poly.normal.z > 0.9:
            poly.material_index = 1
            print(f"First floor: Assigned laminate to polygon {i} (top face)")
        elif poly.normal.z < -0.9:
            poly.material_index = 2
            print(f"First floor: Assigned white ceiling to polygon {i} (bottom face)")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

def _create_floors4(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat):
    """Create ground floor and first floor slabs with laminate texture on top surfaces only."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    recessed_width = 1

    floor_length = LENGTH - 2 * EXTERIOR_WALL_THICKNESS
    floor_width = WIDTH - EXTERIOR_WALL_THICKNESS - recessed_width
    floor_center_y = oy + EXTERIOR_WALL_THICKNESS / 2 - recessed_width / 2

    laminate_mat = create_laminate_floor_material()
    white_ceiling_mat = create_material("WhiteCeiling", (1.0, 1.0, 1.0, 1.0))

    bpy.ops.mesh.primitive_cube_add(location=(ox, floor_center_y, oz + 0.05))
    ground_floor = bpy.context.active_object
    ground_floor.name = "MainDwelling_GroundFloor"
    ground_floor.scale = (floor_length / 2, floor_width / 2, 0.05)
    bpy.ops.object.transform_apply(scale=True)

    ground_floor.data.materials.append(floor_mat)
    ground_floor.data.materials.append(laminate_mat)

    for i, poly in enumerate(ground_floor.data.polygons):
        if poly.normal.z > 0.9:
            poly.material_index = 1
            print(f"Ground floor: Assigned laminate to polygon {i} (top face)")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Build first-floor slab with a built-in stairwell opening in the southwest corner.
    first_floor_thickness = 0.2
    first_floor_center_z = first_floor_z + first_floor_thickness / 2

    stairwell_width = 1.2
    stairwell_length = 3.15

    opening_west_x = ox - floor_length / 2 + 3.4
    opening_east_x = opening_west_x + stairwell_length
    opening_south_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS
    opening_north_y = opening_south_y + stairwell_width 

    floor_west_x = ox - floor_length / 2
    floor_east_x = ox + floor_length / 2
    floor_south_y = floor_center_y - floor_width / 2
    floor_north_y = floor_center_y + floor_width / 2

    slab_parts = []

    # North strip (full width) above stairwell opening.
    north_strip_depth = floor_north_y - opening_north_y
    if north_strip_depth > 0:
        north_strip_center_y = (opening_north_y + floor_north_y) / 2
        bpy.ops.mesh.primitive_cube_add(location=(ox, north_strip_center_y, first_floor_center_z))
        north_strip = bpy.context.active_object
        north_strip.name = "MD_FirstFloor_NorthStrip"
        north_strip.scale = (floor_length / 2, north_strip_depth / 2, first_floor_thickness / 2)
        bpy.ops.object.transform_apply(scale=True)
        slab_parts.append(north_strip)

    # Southeast block below north strip and east of opening.
    se_width = floor_east_x - opening_east_x
    se_depth = opening_north_y - floor_south_y
    print(f"  SE width = {se_width:.2f}, SE depth = {se_depth:.2f}, floor_east_x = {floor_east_x:.2f}, opening_east_x = {opening_east_x:.2f}, floor_south_y = {floor_south_y:.2f}, opening_north_y = {opening_north_y:.2f}")
    if se_width > 0 and se_depth > 0:
        se_center_x = (opening_east_x + floor_east_x) / 2
        se_center_y = (floor_south_y + opening_north_y) / 2
        bpy.ops.mesh.primitive_cube_add(location=(se_center_x, se_center_y, first_floor_center_z))
        southeast_block = bpy.context.active_object
        southeast_block.name = "MD_FirstFloor_SouthEastBlock"
        southeast_block.scale = (se_width / 2, se_depth / 2, first_floor_thickness / 2)
        bpy.ops.object.transform_apply(scale=True)
        slab_parts.append(southeast_block)


    sw_width = opening_west_x - ox + floor_length / 2 
    sw_depth = 1.25
    print(f"  SW width = {sw_width:.2f}, SW depth = {sw_depth:.2f}")
    bpy.ops.mesh.primitive_cube_add(location=(opening_west_x - sw_width / 2, se_center_y, first_floor_center_z))
    southwest_block = bpy.context.active_object
    southwest_block.name = "MD_FirstFloor_SouthWestBlock"
    southwest_block.scale = (sw_width / 2, sw_depth / 2, first_floor_thickness / 2)
    bpy.ops.object.transform_apply(scale=True)
    slab_parts.append(southwest_block)   

    if not slab_parts:
        raise RuntimeError("Failed to create first-floor slab parts for stairwell opening")

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in slab_parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = slab_parts[0]
    if len(slab_parts) > 1:
        bpy.ops.object.join()
    first_floor_slab = bpy.context.view_layer.objects.active
    first_floor_slab.name = "MD_FirstFloor"

    first_floor_slab.data.materials.append(floor_mat)
    first_floor_slab.data.materials.append(laminate_mat)
    first_floor_slab.data.materials.append(white_ceiling_mat)

    for i, poly in enumerate(first_floor_slab.data.polygons):
        if poly.normal.z > 0.9:
            poly.material_index = 1
            print(f"First floor: Assigned laminate to polygon {i} (top face)")
        elif poly.normal.z < -0.9:
            poly.material_index = 2
            print(f"First floor: Assigned white ceiling to polygon {i} (bottom face)")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
