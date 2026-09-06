import bpy  # type: ignore
import os
import math

from materials import get_kitchen_bench_material, get_kitchen_cabinet_material
from main_dwelling.materials_nodes import create_material, create_textured_material2


FLOOR_SLAB_THICKNESS = 0.1
FIRST_FLOOR_SLAB_THICKNESS = 0.2

def _create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS):
    """Create L-shaped kitchen bench"""
    BENCH_LENGTH = 2.6
    BENCH_DEPTH = 0.6
    BENCH_HEIGHT = 0.9
    BENCH_THICKNESS = 0.05
    L_SECTION_LENGTH = 1.8
    SINK_OUTER_WIDTH_EW = 0.55
    SINK_OUTER_DEPTH_NS = 0.45
    SINK_RIM = 0.03
    SINK_DIVIDER_WIDTH = 0.04
    SINK_LEFT_BOWL_RATIO = 0.6
    SINK_CENTER_X_OFFSET = 0.2
    SINK_BOWL_DEPTH = 0.22
    FAUCET_STEM_RADIUS = 0.012
    FAUCET_STEM_HEIGHT = 0.22
    FAUCET_SPOUT_LENGTH = 0.16
    FAUCET_SPOUT_RADIUS = 0.009
    FRIDGE_WIDTH = 0.7
    FRIDGE_DEPTH = 0.7
    FRIDGE_HEIGHT = 2.4
    FRIDGE_GAP = 0.05
    FRIDGE_FACE_THICKNESS = 0.02
    FRIDGE_HANDLE_WIDTH = 0.02
    FRIDGE_HANDLE_DEPTH = 0.015
    FRIDGE_HANDLE_HEIGHT = 1.4
    ISLAND_BASE_WIDTH_EW = 1.5
    ISLAND_BASE_DEPTH_NS = 0.6
    ISLAND_BENCH_THICKNESS = BENCH_THICKNESS
    ISLAND_NORTH_OVERHANG = 0.38
    ISLAND_GAP_FROM_BENCH = 1.2

    south_interior_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS
    west_interior_x = ox - LENGTH / 2 + EXTERIOR_WALL_THICKNESS
    
    FLOOR_TOP = oz + 0.1

    # This is the west end of the main E-W bench run (at the L-turn junction).
    main_bench_west_end = west_interior_x 
    main_bench_east_end = main_bench_west_end + BENCH_LENGTH
    l_section_x = main_bench_west_end + BENCH_DEPTH / 2
    l_section_y = south_interior_y + BENCH_DEPTH + L_SECTION_LENGTH / 2

    bench_center_x = main_bench_west_end + BENCH_LENGTH / 2
    bench_center_y = south_interior_y + BENCH_DEPTH / 2
    bench_top_z = FLOOR_TOP + BENCH_HEIGHT


    # Full-height fridge/freezer placeholder, placed just east of main bench.
    fridge_center_x = main_bench_east_end + FRIDGE_GAP + FRIDGE_WIDTH / 2
    fridge_center_y = south_interior_y + FRIDGE_DEPTH / 2

    island_base_center_x = west_interior_x + BENCH_LENGTH + FRIDGE_WIDTH - ISLAND_BASE_WIDTH_EW / 2 - 0.1
    island_base_south_y = south_interior_y + BENCH_DEPTH + ISLAND_GAP_FROM_BENCH
    island_base_center_y = island_base_south_y + ISLAND_BASE_DEPTH_NS / 2
    island_top_depth_ns = ISLAND_BASE_DEPTH_NS + ISLAND_NORTH_OVERHANG
    island_top_center_y = island_base_center_y + ISLAND_NORTH_OVERHANG / 2

    sink_center_x = bench_center_x + SINK_CENTER_X_OFFSET
    sink_center_y = bench_center_y
    sink_inner_width = SINK_OUTER_WIDTH_EW - (SINK_RIM * 2)
    sink_inner_depth = SINK_OUTER_DEPTH_NS - (SINK_RIM * 2)
    split_width = sink_inner_width - SINK_DIVIDER_WIDTH
    sink_left_bowl_width = split_width * SINK_LEFT_BOWL_RATIO
    sink_right_bowl_width = split_width - sink_left_bowl_width
    sink_left_x = sink_center_x - (SINK_DIVIDER_WIDTH + sink_right_bowl_width) / 2
    sink_right_x = sink_center_x + (SINK_DIVIDER_WIDTH + sink_left_bowl_width) / 2

    bench_mat = get_kitchen_bench_material()
    cabinet_mat = get_kitchen_cabinet_material()
    fridge_body_mat = create_material("KitchenFridgeBody", (0.80, 0.82, 0.84, 1.0))
    fridge_face_mat = create_material("KitchenFridgeFace", (0.90, 0.91, 0.92, 1.0))
    fridge_handle_mat = create_material("KitchenFridgeHandle", (0.45, 0.47, 0.50, 1.0))
    sink_mat = create_material("KitchenSinkSteel", (0.70, 0.72, 0.75, 1.0))
    faucet_mat = create_material("KitchenFaucetChrome", (0.78, 0.80, 0.84, 1.0))

    cabinet_height = BENCH_HEIGHT - BENCH_THICKNESS

    bpy.ops.mesh.primitive_cube_add(location=(bench_center_x, bench_center_y, FLOOR_TOP + cabinet_height / 2))
    cabinets_main = bpy.context.active_object
    cabinets_main.name = "MainDwelling_KitchenBench_Cabinets_Main"
    cabinets_main.scale = (BENCH_LENGTH / 2, BENCH_DEPTH / 2, cabinet_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    cabinets_main.data.materials.append(cabinet_mat)

    bpy.ops.mesh.primitive_cube_add(location=(bench_center_x, bench_center_y, bench_top_z - BENCH_THICKNESS / 2))
    benchtop_main = bpy.context.active_object
    benchtop_main.name = "MainDwelling_KitchenBench_Top_Main"
    benchtop_main.scale = (BENCH_LENGTH / 2, BENCH_DEPTH / 2, BENCH_THICKNESS / 2)
    bpy.ops.object.transform_apply(scale=True)
    benchtop_main.data.materials.append(bench_mat)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Double-bowl sink cutouts in center of main bench top.
    bpy.ops.mesh.primitive_cube_add(location=(sink_left_x, sink_center_y, bench_top_z - BENCH_THICKNESS / 2))
    sink_cutout_left = bpy.context.active_object
    sink_cutout_left.name = "MainDwelling_KitchenSink_Cutout_Left"
    sink_cutout_left.scale = (sink_left_bowl_width / 2, sink_inner_depth / 2, (BENCH_THICKNESS + 0.03) / 2)
    bpy.ops.object.transform_apply(scale=True)

    bpy.ops.mesh.primitive_cube_add(location=(sink_right_x, sink_center_y, bench_top_z - BENCH_THICKNESS / 2))
    sink_cutout_right = bpy.context.active_object
    sink_cutout_right.name = "MainDwelling_KitchenSink_Cutout_Right"
    sink_cutout_right.scale = (sink_right_bowl_width / 2, sink_inner_depth / 2, (BENCH_THICKNESS + 0.03) / 2)
    bpy.ops.object.transform_apply(scale=True)

    sink_bool_left = benchtop_main.modifiers.new(name="KitchenSinkCutoutLeft", type='BOOLEAN')
    sink_bool_left.operation = 'DIFFERENCE'
    sink_bool_left.object = sink_cutout_left
    sink_bool_left.solver = 'EXACT'

    sink_bool_right = benchtop_main.modifiers.new(name="KitchenSinkCutoutRight", type='BOOLEAN')
    sink_bool_right.operation = 'DIFFERENCE'
    sink_bool_right.object = sink_cutout_right
    sink_bool_right.solver = 'EXACT'

    sink_cutout_left.hide_viewport = True
    sink_cutout_left.hide_render = True
    sink_cutout_right.hide_viewport = True
    sink_cutout_right.hide_render = True

    # Undermount double sink bowls beneath benchtop.
    sink_bowl_z = bench_top_z - BENCH_THICKNESS - SINK_BOWL_DEPTH / 2 + 0.01
    bpy.ops.mesh.primitive_cube_add(location=(sink_left_x, sink_center_y, sink_bowl_z))
    sink_bowl_left = bpy.context.active_object
    sink_bowl_left.name = "MainDwelling_KitchenSink_Bowl_Left"
    sink_bowl_left.scale = (sink_left_bowl_width / 2, sink_inner_depth / 2, SINK_BOWL_DEPTH / 2)
    bpy.ops.object.transform_apply(scale=True)
    sink_bowl_left.data.materials.append(sink_mat)

    bpy.ops.mesh.primitive_cube_add(location=(sink_right_x, sink_center_y, sink_bowl_z))
    sink_bowl_right = bpy.context.active_object
    sink_bowl_right.name = "MainDwelling_KitchenSink_Bowl_Right"
    sink_bowl_right.scale = (sink_right_bowl_width / 2, sink_inner_depth / 2, SINK_BOWL_DEPTH / 2)
    bpy.ops.object.transform_apply(scale=True)
    sink_bowl_right.data.materials.append(sink_mat)

    # Simple faucet at the south side of the sink.
    faucet_x = sink_center_x
    faucet_y = sink_center_y - (SINK_OUTER_DEPTH_NS / 2) + 0.05
    faucet_stem_z = bench_top_z + FAUCET_STEM_HEIGHT / 2
    bpy.ops.mesh.primitive_cylinder_add(radius=FAUCET_STEM_RADIUS, depth=FAUCET_STEM_HEIGHT, location=(faucet_x, faucet_y, faucet_stem_z))
    faucet_stem = bpy.context.active_object
    faucet_stem.name = "MainDwelling_KitchenSink_FaucetStem"
    faucet_stem.data.materials.append(faucet_mat)

    faucet_spout_z = bench_top_z + FAUCET_STEM_HEIGHT - 0.02
    bpy.ops.mesh.primitive_cylinder_add(radius=FAUCET_SPOUT_RADIUS, depth=FAUCET_SPOUT_LENGTH, location=(faucet_x, faucet_y + FAUCET_SPOUT_LENGTH / 2, faucet_spout_z))
    faucet_spout = bpy.context.active_object
    faucet_spout.name = "MainDwelling_KitchenSink_FaucetSpout"
    faucet_spout.rotation_euler[0] = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    faucet_spout.data.materials.append(faucet_mat)

    bpy.ops.mesh.primitive_cube_add(location=(fridge_center_x, fridge_center_y, FLOOR_TOP + FRIDGE_HEIGHT / 2))
    fridge_cabinet = bpy.context.active_object
    fridge_cabinet.name = "MainDwelling_Kitchen_FridgeFreezer_Cabinet"
    fridge_cabinet.scale = (FRIDGE_WIDTH / 2, FRIDGE_DEPTH / 2, FRIDGE_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    fridge_cabinet.data.materials.append(fridge_body_mat)

    # Appliance front panel so the unit reads as a fridge/freezer face.
    fridge_face_y = fridge_center_y + FRIDGE_DEPTH / 2 + FRIDGE_FACE_THICKNESS / 2
    bpy.ops.mesh.primitive_cube_add(location=(fridge_center_x, fridge_face_y, FLOOR_TOP + FRIDGE_HEIGHT / 2))
    fridge_face = bpy.context.active_object
    fridge_face.name = "MainDwelling_Kitchen_FridgeFreezer_Face"
    fridge_face.scale = (FRIDGE_WIDTH / 2, FRIDGE_FACE_THICKNESS / 2, FRIDGE_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    fridge_face.data.materials.append(fridge_face_mat)

    # Horizontal split detail between freezer (top) and fridge (bottom).
    split_height = FLOOR_TOP + FRIDGE_HEIGHT * 0.62
    bpy.ops.mesh.primitive_cube_add(location=(fridge_center_x, fridge_face_y + 0.001, split_height))
    fridge_split = bpy.context.active_object
    fridge_split.name = "MainDwelling_Kitchen_FridgeFreezer_Split"
    fridge_split.scale = (FRIDGE_WIDTH / 2, 0.0025, 0.003)
    bpy.ops.object.transform_apply(scale=True)
    fridge_split.data.materials.append(fridge_handle_mat)

    # Vertical handle near the right side of the face.
    handle_x = fridge_center_x + FRIDGE_WIDTH / 2 - 0.06
    handle_y = fridge_face_y + FRIDGE_HANDLE_DEPTH / 2 + 0.002
    handle_z = FLOOR_TOP + FRIDGE_HEIGHT / 2
    bpy.ops.mesh.primitive_cube_add(location=(handle_x, handle_y, handle_z))
    fridge_handle = bpy.context.active_object
    fridge_handle.name = "MainDwelling_Kitchen_FridgeFreezer_Handle"
    fridge_handle.scale = (FRIDGE_HANDLE_WIDTH / 2, FRIDGE_HANDLE_DEPTH / 2, FRIDGE_HANDLE_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    fridge_handle.data.materials.append(fridge_handle_mat)

    # Kitchen island base and top (north overhang for stools).
    bpy.ops.mesh.primitive_cube_add(location=(island_base_center_x, island_base_center_y, FLOOR_TOP + cabinet_height / 2))
    island_base = bpy.context.active_object
    island_base.name = "MainDwelling_KitchenIsland_Base"
    island_base.scale = (ISLAND_BASE_WIDTH_EW / 2, ISLAND_BASE_DEPTH_NS / 2, cabinet_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    island_base.data.materials.append(cabinet_mat)

    bpy.ops.mesh.primitive_cube_add(location=(island_base_center_x, island_top_center_y, bench_top_z - ISLAND_BENCH_THICKNESS / 2))
    island_top = bpy.context.active_object
    island_top.name = "MainDwelling_KitchenIsland_Top"
    island_top.scale = (ISLAND_BASE_WIDTH_EW / 2, island_top_depth_ns / 2, ISLAND_BENCH_THICKNESS / 2)
    bpy.ops.object.transform_apply(scale=True)
    island_top.data.materials.append(bench_mat)

    bpy.ops.mesh.primitive_cube_add(location=(l_section_x, l_section_y, FLOOR_TOP + cabinet_height / 2))
    cabinets_l = bpy.context.active_object
    cabinets_l.name = "MainDwelling_KitchenBench_Cabinets_LSection"
    cabinets_l.scale = (BENCH_DEPTH / 2, L_SECTION_LENGTH / 2, cabinet_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    cabinets_l.data.materials.append(cabinet_mat)

    bpy.ops.mesh.primitive_cube_add(location=(l_section_x, l_section_y, bench_top_z - BENCH_THICKNESS / 2))
    benchtop_l = bpy.context.active_object
    benchtop_l.name = "MainDwelling_KitchenBench_Top_LSection"
    benchtop_l.scale = (BENCH_DEPTH / 2, L_SECTION_LENGTH / 2, BENCH_THICKNESS / 2)
    bpy.ops.object.transform_apply(scale=True)
    benchtop_l.data.materials.append(bench_mat)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    WALL_CABINET_DEPTH = 0.35
    WALL_CABINET_HEIGHT = 0.7
    WALL_CABINET_GAP = 0.45
    wall_cabinet_z = bench_top_z + WALL_CABINET_GAP + WALL_CABINET_HEIGHT / 2

    wall_cab_length_ns = BENCH_DEPTH + L_SECTION_LENGTH
    wall_cab_ns_y = south_interior_y + wall_cab_length_ns / 2
    wall_cab_ns_x = main_bench_west_end + WALL_CABINET_DEPTH / 2

    bpy.ops.mesh.primitive_cube_add(location=(wall_cab_ns_x, wall_cab_ns_y, wall_cabinet_z))
    wall_cab_ns = bpy.context.active_object
    wall_cab_ns.name = "MainDwelling_KitchenBench_WallCabinet_NS"
    wall_cab_ns.scale = (WALL_CABINET_DEPTH / 2, wall_cab_length_ns / 2, WALL_CABINET_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    wall_cab_ns.data.materials.append(cabinet_mat)

    print(f"L-shaped kitchen bench created: {BENCH_LENGTH}m E-W section, {L_SECTION_LENGTH}m N-S section with N-S wall cabinet")
    print(f"Double-bowl kitchen sink (60/40) created at ({sink_center_x:.2f}, {sink_center_y:.2f}) with {SINK_OUTER_WIDTH_EW}m x {SINK_OUTER_DEPTH_NS}m footprint")
    print(f"Fridge/freezer placeholder cabinet created at ({fridge_center_x:.2f}, {fridge_center_y:.2f}): {FRIDGE_WIDTH}m x {FRIDGE_DEPTH}m x {FRIDGE_HEIGHT}m")
    print(f"Kitchen island created at ({island_base_center_x:.2f}, {island_base_center_y:.2f}): base {ISLAND_BASE_WIDTH_EW}m x {ISLAND_BASE_DEPTH_NS}m, top north overhang {ISLAND_NORTH_OVERHANG}m")


def _create_dining_table(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, TABLE_LENGTH = 1.8, TABLE_WIDTH = 0.9):
    """Create dining table on ground floor."""
    TABLE_HEIGHT = 0.75
    LEG_SIZE = 0.08
    TOP_THICKNESS = 0.04
    FLOOR_TOP = oz + 0.1

    CLEARANCE = 0.4
    table_x = ox - 1.10
    table_y = oy + 1.65
    table_top_z = FLOOR_TOP + TABLE_HEIGHT - TOP_THICKNESS / 2

    table_mat = create_material("DiningTableWood", (0.55, 0.35, 0.20, 1))

    bpy.ops.mesh.primitive_cube_add(location=(table_x, table_y, table_top_z))
    table_top = bpy.context.active_object
    table_top.name = "MainDwelling_DiningTable_Top"
    table_top.scale = (TABLE_LENGTH / 2, TABLE_WIDTH / 2, TOP_THICKNESS / 2)
    bpy.ops.object.transform_apply(scale=True)
    table_top.data.materials.append(table_mat)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    leg_height = TABLE_HEIGHT - TOP_THICKNESS
    leg_z = FLOOR_TOP + leg_height / 2
    leg_inset = 0.1

    leg_positions = [
        (table_x - TABLE_LENGTH / 2 + leg_inset, table_y - TABLE_WIDTH / 2 + leg_inset),
        (table_x + TABLE_LENGTH / 2 - leg_inset, table_y - TABLE_WIDTH / 2 + leg_inset),
        (table_x - TABLE_LENGTH / 2 + leg_inset, table_y + TABLE_WIDTH / 2 - leg_inset),
        (table_x + TABLE_LENGTH / 2 - leg_inset, table_y + TABLE_WIDTH / 2 - leg_inset),
    ]

    for i, (leg_x, leg_y) in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cube_add(location=(leg_x, leg_y, leg_z))
        leg = bpy.context.active_object
        leg.name = f"MainDwelling_DiningTable_Leg_{i + 1}"
        leg.scale = (LEG_SIZE / 2, LEG_SIZE / 2, leg_height / 2)
        bpy.ops.object.transform_apply(scale=True)
        leg.data.materials.append(table_mat)

    print(f"Dining table created at ({table_x:.2f}, {table_y:.2f}, {oz}): {TABLE_LENGTH}m × {TABLE_WIDTH}m × {TABLE_HEIGHT}m")


def _furnish_main_bathroom(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS):
    """Furnish main bathroom with shower components."""
    east_interior_face = ox + LENGTH / 2 - EXTERIOR_WALL_THICKNESS
    south_interior_face = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS
    west_interior_face = east_interior_face - 2
    bathroom_north = south_interior_face + 2.3

    white_mat = create_material("BathroomWhite", (0.95, 0.95, 0.95, 1))
    chrome_mat = create_material("Chrome", (0.8, 0.8, 0.8, 1))
    FLOOR_TOP = oz + 0.1

    SHOWER_SIZE = 0.9
    WALL_THICKNESS = 0.08
    WALL_HEIGHT = 2.4

    shower_x_center = west_interior_face + SHOWER_SIZE / 2
    shower_y_center = south_interior_face + SHOWER_SIZE / 2

    #create_shower_tray( x_center=shower_x_center, y_center=shower_y_center, z_bottom=FLOOR_TOP, size=SHOWER_SIZE, height=0.15,
    #    material=white_mat, name_prefix="GroundFloor_Bathroom", )

    granite_path = os.path.abspath("textures/granite_tile_03/granite_tile_03_diff_1k.jpg")
    tile_mat = create_textured_material2( name="ShowerTile", texture_path=granite_path,
        rotation_z=0, scale=(1.5, 1.5, 1.5),
        roughness=0.2, projection='BOX', )

    bpy.ops.mesh.primitive_cube_add(location=(west_interior_face + 0.03, south_interior_face + SHOWER_SIZE/2 + 0.03, FLOOR_TOP + WALL_HEIGHT / 2))
    northsouth_wall = bpy.context.active_object
    northsouth_wall.name = "MD_Bathroom_ShowerWallWest"
    northsouth_wall.scale = (WALL_THICKNESS / 4, 0.5, WALL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    northsouth_wall.data.materials.append(tile_mat)

    bpy.ops.mesh.primitive_cube_add(location=(shower_x_center, south_interior_face + 0.03, FLOOR_TOP + WALL_HEIGHT / 2))
    eastwest_wall = bpy.context.active_object
    eastwest_wall.name = "MD_Bathroom_ShowerWallSouth"
    eastwest_wall.scale = (0.5, WALL_THICKNESS / 4, WALL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    eastwest_wall.data.materials.append(tile_mat)


    create_toilet(
        west_edge=west_interior_face +1.2,
        south_edge=south_interior_face,
        floor_top=FLOOR_TOP,
        material=white_mat,
        name_prefix="MD_MainBathroom",
        rotation_z_degrees=90
    )

    create_vanity(
        east_edge=east_interior_face - 0.05,
        south_edge=south_interior_face + 1.8,
        floor_top=FLOOR_TOP,
        basin_material=white_mat,
        chrome_material=chrome_mat,
        name_prefix="MD_MainBathroom",
    )


def _furnish_master_ensuite(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS):
    """Furnish master bedroom ensuite with shower, toilet, and vanity."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    FIRST_FLOOR_SLAB_THICKNESS = 0.2
    first_floor_top = first_floor_z + FIRST_FLOOR_SLAB_THICKNESS

    ENSUITE_WIDTH = 2.0
    ENSUITE_DEPTH = 2.0

    east_interior_face = ox + LENGTH / 2 - EXTERIOR_WALL_THICKNESS
    south_interior_face = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS

    ensuite_east = east_interior_face
    ensuite_west = east_interior_face - ENSUITE_WIDTH
    ensuite_south = south_interior_face
    ensuite_north = south_interior_face + ENSUITE_DEPTH

    white_mat = create_material("BathroomWhite", (0.95, 0.95, 0.95, 1))
    chrome_mat = create_material("Chrome", (0.8, 0.8, 0.8, 1))

    SHOWER_SIZE = 0.9
    SHOWER_TRAY_HEIGHT = 0 #0.15
    WALL_THICKNESS = 0.08
    WALL_HEIGHT = 2.0

    shower_west_edge = ensuite_west
    shower_east_edge = ensuite_west + SHOWER_SIZE
    shower_north_edge = ensuite_south + SHOWER_SIZE  #ensuite_north
    shower_south_edge = ensuite_south #ensuite_north - SHOWER_SIZE
    shower_x_center = (shower_west_edge + shower_east_edge) / 2
    shower_y_center = (shower_north_edge + shower_south_edge) / 2

    #create_shower_tray( x_center=shower_x_center, y_center=shower_y_center, z_bottom=first_floor_top,
    #    size=SHOWER_SIZE, height=SHOWER_TRAY_HEIGHT, material=white_mat, name_prefix="FirstFloor_Ensuite", )

    granite_path = os.path.abspath("textures/granite_tile_03/granite_tile_03_diff_1k.jpg")
    tile_mat = create_textured_material2(
        name="ShowerTile",
        texture_path=granite_path,
        rotation_z=0,
        scale=(1.5, 1.5, 1.5),
        roughness=0.2,
        projection='BOX',
    )

    northsouth_wall_x = shower_west_edge + WALL_THICKNESS / 2
    bpy.ops.mesh.primitive_cube_add(location=(northsouth_wall_x-WALL_THICKNESS/2, shower_y_center, first_floor_top + SHOWER_TRAY_HEIGHT + WALL_HEIGHT / 2))
    northsouth_wall = bpy.context.active_object
    northsouth_wall.name = "MD_Ensuite_ShowerWallWest"
    northsouth_wall.scale = (WALL_THICKNESS / 4, SHOWER_SIZE / 2, WALL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    northsouth_wall.data.materials.append(tile_mat)

    eastwest_wall_y = shower_south_edge - WALL_THICKNESS / 2
    bpy.ops.mesh.primitive_cube_add(location=(shower_x_center, eastwest_wall_y + WALL_THICKNESS/2, first_floor_top + SHOWER_TRAY_HEIGHT + WALL_HEIGHT / 2))
    eastwest_wall = bpy.context.active_object
    eastwest_wall.name = "MD_Ensuite_ShowerWallNorth"
    eastwest_wall.scale = (SHOWER_SIZE / 2, WALL_THICKNESS / 4, WALL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    eastwest_wall.data.materials.append(tile_mat)

    glass_mat = bpy.data.materials.get("Glass")
    if not glass_mat:
        glass_mat = bpy.data.materials.new(name="Glass")
        glass_mat.use_nodes = True
        glass_mat.blend_method = 'BLEND'
        bsdf = glass_mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.8, 0.95, 1.0, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.0
            bsdf.inputs['IOR'].default_value = 1.52
            bsdf.inputs['Alpha'].default_value = 0.3
            transmission_input = bsdf.inputs.get('Transmission Weight') or bsdf.inputs.get('Transmission')
            if transmission_input:
                transmission_input.default_value = 1.0

    glass_thickness = 0.01
    glass_height = 1.8
    glass_z_location = first_floor_top + SHOWER_TRAY_HEIGHT + glass_height / 2

    east_glass_x = shower_east_edge - glass_thickness / 2

    bpy.ops.mesh.primitive_cube_add(location=(east_glass_x, shower_y_center, glass_z_location))
    east_glass = bpy.context.active_object
    east_glass.name = "MD_Ensuite_ShowerScreenEast"
    east_glass.scale = (glass_thickness / 2, SHOWER_SIZE / 2, glass_height / 2)
    bpy.ops.object.transform_apply(scale=True)

    east_glass.data.materials.append(glass_mat)
    east_glass.show_transparent = True
    east_glass.display_type = 'TEXTURED'

    north_glass_y = shower_north_edge - glass_thickness / 2

    bpy.ops.mesh.primitive_cube_add(location=(shower_x_center, north_glass_y, glass_z_location))
    north_glass = bpy.context.active_object
    north_glass.name = "MD_Ensuite_ShowerScreenNorth"
    north_glass.scale = (SHOWER_SIZE / 2, glass_thickness / 2, glass_height / 2)
    bpy.ops.object.transform_apply(scale=True)

    north_glass.data.materials.append(glass_mat)
    north_glass.show_transparent = True
    north_glass.display_type = 'TEXTURED'

    bpy.ops.mesh.primitive_uv_sphere_add(location=(northsouth_wall_x + 0.15, shower_y_center, first_floor_top + SHOWER_TRAY_HEIGHT + 1.8), radius=0.1)
    shower_head = bpy.context.active_object
    shower_head.name = "MD_Ensuite_ShowerHead"
    shower_head.data.materials.append(chrome_mat)

    create_toilet(
        west_edge=ensuite_west+1.2,
        south_edge=ensuite_south,
        floor_top=first_floor_top,
        material=white_mat,
        name_prefix="MD_Ensuite",
        rotation_z_degrees=90
    )

    create_vanity(
        east_edge=ensuite_east - 0.05,
        south_edge=ensuite_south +1.2,
        floor_top=first_floor_top,
        basin_material=white_mat,
        chrome_material=chrome_mat,
        name_prefix="MD_Ensuite",
        rotation_z_degrees=0,
    )

def _furnish_guest_bedroom(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Furnish guest bedroom with bed and ....
    bedroom is in north east corner on the ground floor, with main bathroom to the south of it. 
    The bed is placed against the east wall, with the headboard against the wall and the foot of the bed facing west. 
    The bed is a standard double bed size (1.6m x 2.0m) and is positioned centrally along the east wall, leaving space on either side for bedside tables or access. 
    The bed is raised slightly off the floor to allow for under-bed storage and to provide a comfortable sleeping height. 
    The bedding is simple and neutral in color, complementing the overall aesthetic of the room.
    """

    east_interior_face = ox + LENGTH / 2 - EXTERIOR_WALL_THICKNESS
    north_interior_face = oy + WIDTH / 2 - NORTH_RECESS - EXTERIOR_WALL_THICKNESS


    BED_WIDTH = 1.6
    BED_LENGTH = 2.0
    BED_HEIGHT = 0.6
    FLOOR_TOP = oz + FLOOR_SLAB_THICKNESS

    bed_mat = create_material("BedFabric", (0.95, 0.95, 0.9, 1))

    guest_bed_x = east_interior_face - BED_LENGTH / 2 
    guest_bed_y = north_interior_face - BED_WIDTH / 2 - 0.9
    guest_bed_z = FLOOR_TOP + BED_HEIGHT / 2

    bpy.ops.mesh.primitive_cube_add(location=(guest_bed_x, guest_bed_y, guest_bed_z))
    guest_bed = bpy.context.active_object
    guest_bed.name = "MD_GuestBedroom_QueenBed"
    guest_bed.scale = (BED_LENGTH / 2, BED_WIDTH / 2, BED_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    guest_bed.data.materials.append(bed_mat)

def _furnish_master_bedroom(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, GROUND_FLOOR_HEIGHT):
    """Furnish master bedroom with bed and ....
    bedroom is in north east corner on the first floor, with ensuite to the south of it. 
    The bed is placed against the east wall, with the headboard against the wall and the foot of the bed facing west. 
    The bed is a standard king bed size (1.8m x 2.0m) and is positioned centrally along the east wall, leaving space on either side for bedside tables or access. 
    The bed is raised slightly off the floor to allow for under-bed storage and to provide a comfortable sleeping height. 
    The bedding is simple and neutral in color, complementing the overall aesthetic of the room.
    """

    east_interior_face = ox + LENGTH / 2 - EXTERIOR_WALL_THICKNESS
    north_interior_face = oy + WIDTH / 2 - NORTH_RECESS - EXTERIOR_WALL_THICKNESS
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    first_floor_top = first_floor_z + FIRST_FLOOR_SLAB_THICKNESS


    BED_WIDTH = 1.8
    BED_LENGTH = 2.0
    BED_HEIGHT = 0.6

    bed_mat = create_material("BedFabric", (0.95, 0.95, 0.9, 1))

    bed_x = east_interior_face - BED_LENGTH / 2 #- 1.5
    bed_y = north_interior_face - BED_WIDTH / 2 - 0.9
    bed_z = first_floor_top + BED_HEIGHT / 2

    bpy.ops.mesh.primitive_cube_add(location=(bed_x, bed_y, bed_z))
    bed = bpy.context.active_object
    bed.name = "MD_MasterBedroom_KingBed"
    bed.scale = (BED_LENGTH / 2, BED_WIDTH / 2, BED_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    bed.data.materials.append(bed_mat)


def create_shower_tray(x_center, y_center, z_bottom, size, height, material, name_prefix="MainDwelling"):
    """Create a shower tray at a specific X, Y, and bottom Z coordinate."""
    z_center = z_bottom + height / 2
    bpy.ops.mesh.primitive_cube_add(location=(x_center, y_center, z_center))
    shower_tray = bpy.context.active_object
    shower_tray.name = f"{name_prefix}_ShowerTray"
    shower_tray.scale = (size / 2, size / 2, height / 2)
    bpy.ops.object.transform_apply(scale=True)
    if material:
        shower_tray.data.materials.append(material)
    return shower_tray


def create_toilet(west_edge, south_edge, floor_top, material, name_prefix="MD", rotation_z_degrees=0):
    """Create a simple toilet fixture with bowl and tank from west/south room edges.

    rotation_z_degrees rotates the toilet assembly around its center in plan.
    """
    toilet_width = 0.4
    toilet_depth = 0.6
    toilet_height = 0.4
    toilet_tank_height = 0.8
    toilet_tank_width = 0.15
    south_offset = 0.15

    toilet_center_x = west_edge + toilet_depth / 2
    toilet_center_y = south_edge + toilet_width / 2 + south_offset
    theta = math.radians(rotation_z_degrees)

    bpy.ops.mesh.primitive_cube_add(location=(toilet_center_x, toilet_center_y, floor_top + toilet_height / 2))
    toilet_bowl = bpy.context.active_object
    toilet_bowl.name = f"{name_prefix}_ToiletBowl"
    toilet_bowl.scale = (toilet_depth / 2, toilet_width / 2, toilet_height / 2)
    toilet_bowl.rotation_euler[2] = theta
    bpy.ops.object.transform_apply(scale=True)
    toilet_bowl.data.materials.append(material)

    """bpy.ops.mesh.primitive_cube_add(location=(west_edge + toilet_tank_width / 2, toilet_center_y, floor_top + toilet_tank_height / 2))
    toilet_tank = bpy.context.active_object
    toilet_tank.name = f"{name_prefix}_ToiletTank"
    toilet_tank.scale = (toilet_tank_width / 2, toilet_width / 2, toilet_tank_height / 2)
    toilet_tank.rotation_euler[2] = theta
    bpy.ops.object.transform_apply(scale=True)
    toilet_tank.data.materials.append(material)"""

    return toilet_bowl#, toilet_tank


def create_vanity(east_edge, south_edge, floor_top, basin_material, chrome_material, name_prefix="MD", rotation_z_degrees=0):
    """Create a vanity cabinet, basin, and tap from east/south room edges.

    rotation_z_degrees rotates the vanity assembly around its center in plan.
    """
    vanity_width = 0.6
    vanity_depth = 0.5
    vanity_height = 0.85
    basin_height = 0.15

    vanity_center_x = east_edge - vanity_depth / 2
    vanity_center_y = south_edge + vanity_width / 2
    theta = math.radians(rotation_z_degrees)

    cabinet_mat = create_material("VanityCabinet", (0.4, 0.3, 0.2, 1))
    bpy.ops.mesh.primitive_cube_add(location=(vanity_center_x, vanity_center_y, floor_top + vanity_height / 2))
    vanity_cabinet = bpy.context.active_object
    vanity_cabinet.name = f"{name_prefix}_VanityCabinet"
    vanity_cabinet.scale = (vanity_depth / 2, vanity_width / 2, vanity_height / 2)
    vanity_cabinet.rotation_euler[2] = theta
    bpy.ops.object.transform_apply(scale=True)
    vanity_cabinet.data.materials.append(cabinet_mat)

    bpy.ops.mesh.primitive_cube_add(location=(vanity_center_x, vanity_center_y, floor_top + vanity_height + basin_height / 2))
    basin = bpy.context.active_object
    basin.name = f"{name_prefix}_Basin"
    basin.scale = ((vanity_depth - 0.1) / 2, (vanity_width - 0.1) / 2, basin_height / 2)
    basin.rotation_euler[2] = theta
    bpy.ops.object.transform_apply(scale=True)
    basin.data.materials.append(basin_material)

    tap_offset_x = 0.15 * math.cos(theta)
    tap_offset_y = 0.15 * math.sin(theta)
    bpy.ops.mesh.primitive_cylinder_add(location=(vanity_center_x + tap_offset_x, vanity_center_y + tap_offset_y, floor_top + vanity_height + 0.15), radius=0.02, depth=0.2)
    tap = bpy.context.active_object
    tap.name = f"{name_prefix}_Tap"
    tap.data.materials.append(chrome_material)

    return vanity_cabinet, basin, tap
