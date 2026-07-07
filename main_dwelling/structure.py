import bpy  # type: ignore

from materials import get_interior_wall_material
from main_dwelling.materials_nodes import create_laminate_floor_material, create_material


def _get_stair_layout_spec(layout, ox, oy, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS):
    """Return shared XY layout spec for staircase and first-floor opening."""
    south_interior_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS

    if layout == "southwest":
        west_interior_x = ox - LENGTH / 2 + EXTERIOR_WALL_THICKNESS
        return {
            "layout": layout,
            "stairwell_west_x": west_interior_x,
            "stairwell_south_y": south_interior_y,
            "stairwell_width": 2.0,
            "stairwell_length": 3.0,
            # Keep this trim for continuity with current slab opening behavior.
            "opening_north_trim": 0.3,
        }

    if layout == "southmiddle":
        west_interior_x = ox
        return {
            "layout": layout,
            "stairwell_west_x": west_interior_x,
            "stairwell_south_y": south_interior_y,
            "stairwell_width": 3.0,
            "stairwell_length": 2.0,
            # Keep this trim for continuity with current slab opening behavior.
            "opening_north_trim": 0.3,
        }

    raise ValueError(f"Unsupported stair layout: {layout}")


def _create_180_degree_staircase(layout, ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat):
    """Create a 180-degree dog-legged staircase using a named shared layout."""
    spec = _get_stair_layout_spec(layout, ox, oy, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)

    GROUND_FLOOR_SLAB_THICKNESS = 0.1
    FIRST_FLOOR_SLAB_THICKNESS = 0.2
    ground_floor_top = oz + GROUND_FLOOR_SLAB_THICKNESS
    first_floor_top = oz + GROUND_FLOOR_HEIGHT + FIRST_FLOOR_SLAB_THICKNESS
    TOTAL_RISE = first_floor_top - ground_floor_top

    STAIRWELL_WIDTH = spec["stairwell_width"]
    STAIRWELL_LENGTH = spec["stairwell_length"]
    FLIGHT_WIDTH = 0.95
    LANDING_DEPTH = 1.0
    LANDING_HEIGHT = TOTAL_RISE / 2

    STEPS_PER_FLIGHT = 7
    STEP_RISE = TOTAL_RISE / (STEPS_PER_FLIGHT * 2)
    STEP_TREAD = 0.28
    MODELED_STEPS_PER_FLIGHT = STEPS_PER_FLIGHT - 1

    stairwell_west_x = spec["stairwell_west_x"]
    stairwell_east_x = stairwell_west_x + STAIRWELL_WIDTH
    stairwell_south_y = spec["stairwell_south_y"]
    stairwell_north_y = stairwell_south_y + STAIRWELL_LENGTH

    stairs_mat = create_material("StairsWood", (0.6, 0.4, 0.25, 1))
    landing_mat = floor_mat

    if layout == "southwest":
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

        print("180-degree staircase created in southwest corner")
        print(f"  Flight 1 (EAST edge): {MODELED_STEPS_PER_FLIGHT} modeled treads + landing as final tread")
        print(f"  Landing (SOUTH edge): {LANDING_HEIGHT}m height, spans East-West")
        print(f"  Flight 2 (WEST edge): {MODELED_STEPS_PER_FLIGHT} modeled treads + floor as final tread")
    elif layout == "southmiddle":
        flight1_y = stairwell_north_y - FLIGHT_WIDTH / 2
        landing_east_x = stairwell_west_x + LANDING_DEPTH
        flight1_start_x = landing_east_x + (MODELED_STEPS_PER_FLIGHT * STEP_TREAD) - (STEP_TREAD / 2)

        for i in range(MODELED_STEPS_PER_FLIGHT):
            step_height = ground_floor_top + STEP_RISE * (i + 0.5)
            step_x = flight1_start_x - (i * STEP_TREAD)

            bpy.ops.mesh.primitive_cube_add(location=(step_x, flight1_y, step_height))
            step = bpy.context.active_object
            step.name = f"MainDwelling_Stairs_Flight1_Step_{i + 1:02d}"
            step.scale = (STEP_TREAD / 2, FLIGHT_WIDTH / 2, STEP_RISE / 2)
            bpy.ops.object.transform_apply(scale=True)
            step.data.materials.append(stairs_mat)

        landing_x = stairwell_west_x + LANDING_DEPTH / 2
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

        flight2_y = stairwell_south_y + FLIGHT_WIDTH / 2
        flight2_start_x = stairwell_west_x + LANDING_DEPTH + STEP_TREAD / 2

        for i in range(MODELED_STEPS_PER_FLIGHT):
            step_height = landing_top_z + STEP_RISE * (i + 0.5)
            step_x = flight2_start_x + (i * STEP_TREAD)

            bpy.ops.mesh.primitive_cube_add(location=(step_x, flight2_y, step_height))
            step = bpy.context.active_object
            step.name = f"MainDwelling_Stairs_Flight2_Step_{i + 1:02d}"
            step.scale = (STEP_TREAD / 2, FLIGHT_WIDTH / 2, STEP_RISE / 2)
            bpy.ops.object.transform_apply(scale=True)
            step.data.materials.append(stairs_mat)

        print("180-degree staircase created in south-middle, rotated 90 degrees")
        print(f"  Flight 1 (NORTH edge): {MODELED_STEPS_PER_FLIGHT} modeled treads + landing as final tread")
        print(f"  Landing (WEST edge): {LANDING_HEIGHT}m height, spans South-North")
        print(f"  Flight 2 (SOUTH edge): {MODELED_STEPS_PER_FLIGHT} modeled treads + floor as final tread")
    else:
        raise ValueError(f"Unsupported stair layout: {layout}")

    # Stairwell opening is created in _create_floors using the same shared layout spec.
    print(f"  Stairwell footprint: {STAIRWELL_WIDTH}m × {STAIRWELL_LENGTH}m")
    print(f"  Step rise: {STEP_RISE * 1000:.1f}mm, tread: {STEP_TREAD * 1000:.0f}mm")


def _create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat):
    """Create all exterior walls for ground and first floors with recessed north wall."""
    wall_depth_ground = ENCLOSED_WIDTH - 2 * EXTERIOR_WALL_THICKNESS
    first_floor_z = oz + GROUND_FLOOR_HEIGHT

    interior_wall_mat = get_interior_wall_material()

    north_wall_y = oy + WIDTH / 2 - NORTH_RECESS + EXTERIOR_WALL_THICKNESS / 2
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

    bpy.ops.mesh.primitive_cube_add(location=(ox, north_wall_y, first_floor_z + FIRST_FLOOR_HEIGHT / 2))
    north_wall_first = bpy.context.active_object
    north_wall_first.name = "MD_FF_NorthWall"
    north_wall_first.scale = (LENGTH / 2, EXTERIOR_WALL_THICKNESS / 2, FIRST_FLOOR_HEIGHT / 2)
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
    _create_180_degree_staircase("southwest", ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat)

def _create_180_degree_staircase_southmiddle(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS,  floor_mat):
    """Create a 180-degree dog-legged staircase near south-middle, rotated 90 degrees."""
    _create_180_degree_staircase("southmiddle", ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat)


def _create_floors(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat, stair_layout="southmiddle"):
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

    stair_spec = _get_stair_layout_spec(stair_layout, ox, oy, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
    opening_east_x = stair_spec["stairwell_west_x"] + stair_spec["stairwell_width"]
    opening_north_y = stair_spec["stairwell_south_y"] + stair_spec["stairwell_length"] - stair_spec["opening_north_trim"]

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
        north_strip.name = "MainDwelling_FirstFloor_NorthStrip"
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
        southeast_block.name = "MainDwelling_FirstFloor_SouthEastBlock"
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
    first_floor_slab.name = "MainDwelling_FirstFloor"

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

