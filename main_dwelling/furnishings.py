import bpy  # type: ignore
import os
import math

from materials import get_kitchen_bench_material, get_kitchen_cabinet_material
from main_dwelling.materials_nodes import create_material, create_textured_material2


FLOOR_SLAB_THICKNESS = 0.1
FIRST_FLOOR_SLAB_THICKNESS = 0.2

def _create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS):
    """Create L-shaped kitchen bench"""
    BENCH_LENGTH = 2.4
    BENCH_DEPTH = 0.6
    BENCH_HEIGHT = 0.9
    BENCH_THICKNESS = 0.05
    L_SECTION_LENGTH = 1.8

    south_interior_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS
    west_interior_x = ox - LENGTH / 2 + EXTERIOR_WALL_THICKNESS

    FLOOR_TOP = oz + 0.1

    bench_center_x = west_interior_x + BENCH_LENGTH / 2 + 2.1
    bench_center_y = south_interior_y + BENCH_DEPTH / 2
    bench_top_z = FLOOR_TOP + BENCH_HEIGHT

    main_bench_east_end = west_interior_x + 2.1
    l_section_x = main_bench_east_end + BENCH_DEPTH / 2
    l_section_y = south_interior_y + BENCH_DEPTH + L_SECTION_LENGTH / 2

    bench_mat = get_kitchen_bench_material()
    cabinet_mat = get_kitchen_cabinet_material()

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
    wall_cab_ns_x = main_bench_east_end + WALL_CABINET_DEPTH / 2

    bpy.ops.mesh.primitive_cube_add(location=(wall_cab_ns_x, wall_cab_ns_y, wall_cabinet_z))
    wall_cab_ns = bpy.context.active_object
    wall_cab_ns.name = "MainDwelling_KitchenBench_WallCabinet_NS"
    wall_cab_ns.scale = (WALL_CABINET_DEPTH / 2, wall_cab_length_ns / 2, WALL_CABINET_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    wall_cab_ns.data.materials.append(cabinet_mat)

    print(f"L-shaped kitchen bench created: {BENCH_LENGTH}m E-W section, {L_SECTION_LENGTH}m N-S section with N-S wall cabinet")


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

    bathroom_west = east_interior_face - 2
    bathroom_north = south_interior_face + 2.3

    white_mat = create_material("BathroomWhite", (0.95, 0.95, 0.95, 1))
    chrome_mat = create_material("Chrome", (0.8, 0.8, 0.8, 1))
    FLOOR_TOP = oz + 0.1

    WALL_THICKNESS = 0.1
    WALL_HEIGHT = 2.0

    shower_x_center = east_interior_face - 0.5#(bathroom_west + bathroom_west + 1) / 2
    shower_y_center = (bathroom_north + bathroom_north - 0.36) / 2

    create_shower_tray(
        x_center=shower_x_center,
        y_center=shower_y_center,
        z_bottom=FLOOR_TOP,
        size=1.0,
        height=0.15,
        material=white_mat,
        name_prefix="GroundFloor_Bathroom",
    )

    granite_path = os.path.abspath("textures/granite_tile_03/granite_tile_03_diff_1k.jpg")
    tile_mat = create_textured_material2(
        name="ShowerTile",
        texture_path=granite_path,
        rotation_z=0,
        scale=(1.5, 1.5, 1.5),
        roughness=0.2,
        projection='BOX',
    )

    bpy.ops.mesh.primitive_cube_add(location=(east_interior_face - 0.03, bathroom_north - 0.2, FLOOR_TOP + WALL_HEIGHT / 2))
    east_wall = bpy.context.active_object
    east_wall.name = "MD_Bathroom_ShowerWallEast"
    east_wall.scale = (WALL_THICKNESS / 4, 0.5, WALL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    east_wall.data.materials.append(tile_mat)

    bpy.ops.mesh.primitive_cube_add(location=(shower_x_center, bathroom_north + 0.35, FLOOR_TOP + WALL_HEIGHT / 2))
    north_wall = bpy.context.active_object
    north_wall.name = "MD_Bathroom_ShowerWallNorth"
    north_wall.scale = (0.5, WALL_THICKNESS / 4, WALL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall.data.materials.append(tile_mat)


    create_toilet(
        west_edge=bathroom_west,
        south_edge=south_interior_face,
        floor_top=FLOOR_TOP,
        material=white_mat,
        name_prefix="MD_MainBathroom",
    )

    create_vanity(
        east_edge=east_interior_face,
        south_edge=south_interior_face,
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

    SHOWER_SIZE = 1.0
    SHOWER_TRAY_HEIGHT = 0.15
    WALL_THICKNESS = 0.1
    WALL_HEIGHT = 2.0

    shower_west_edge = ensuite_west
    shower_east_edge = ensuite_west + SHOWER_SIZE
    shower_north_edge = ensuite_north
    shower_south_edge = ensuite_north - SHOWER_SIZE
    shower_x_center = (shower_west_edge + shower_east_edge) / 2
    shower_y_center = (shower_north_edge + shower_south_edge) / 2

    create_shower_tray(
        x_center=shower_x_center,
        y_center=shower_y_center,
        z_bottom=first_floor_top,
        size=SHOWER_SIZE,
        height=SHOWER_TRAY_HEIGHT,
        material=white_mat,
        name_prefix="FirstFloor_Ensuite",
    )

    granite_path = os.path.abspath("textures/granite_tile_03/granite_tile_03_diff_1k.jpg")
    tile_mat = create_textured_material2(
        name="ShowerTile",
        texture_path=granite_path,
        rotation_z=0,
        scale=(1.5, 1.5, 1.5),
        roughness=0.2,
        projection='BOX',
    )

    west_wall_x = shower_west_edge + WALL_THICKNESS / 2
    bpy.ops.mesh.primitive_cube_add(location=(west_wall_x, shower_y_center, first_floor_top + SHOWER_TRAY_HEIGHT + WALL_HEIGHT / 2))
    west_wall = bpy.context.active_object
    west_wall.name = "MainDwelling_Ensuite_ShowerWallWest"
    west_wall.scale = (WALL_THICKNESS / 4, SHOWER_SIZE / 2, WALL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall.data.materials.append(tile_mat)

    north_wall_y = shower_north_edge - WALL_THICKNESS / 2
    bpy.ops.mesh.primitive_cube_add(location=(shower_x_center, north_wall_y, first_floor_top + SHOWER_TRAY_HEIGHT + WALL_HEIGHT / 2))
    north_wall = bpy.context.active_object
    north_wall.name = "MainDwelling_Ensuite_ShowerWallNorth"
    north_wall.scale = (SHOWER_SIZE / 2, WALL_THICKNESS / 4, WALL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall.data.materials.append(tile_mat)

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
    east_glass.name = "MainDwelling_Ensuite_ShowerScreenEast"
    east_glass.scale = (glass_thickness / 2, SHOWER_SIZE / 2, glass_height / 2)
    bpy.ops.object.transform_apply(scale=True)

    east_glass.data.materials.append(glass_mat)
    east_glass.show_transparent = True
    east_glass.display_type = 'TEXTURED'

    south_glass_y = shower_south_edge + glass_thickness / 2

    bpy.ops.mesh.primitive_cube_add(location=(shower_x_center, south_glass_y, glass_z_location))
    south_glass = bpy.context.active_object
    south_glass.name = "MainDwelling_Ensuite_ShowerScreenSouth"
    south_glass.scale = (SHOWER_SIZE / 2, glass_thickness / 2, glass_height / 2)
    bpy.ops.object.transform_apply(scale=True)

    south_glass.data.materials.append(glass_mat)
    south_glass.show_transparent = True
    south_glass.display_type = 'TEXTURED'

    bpy.ops.mesh.primitive_uv_sphere_add(location=(west_wall_x + 0.15, shower_y_center, first_floor_top + SHOWER_TRAY_HEIGHT + 1.8), radius=0.1)
    shower_head = bpy.context.active_object
    shower_head.name = "MainDwelling_Ensuite_ShowerHead"
    shower_head.data.materials.append(chrome_mat)

    create_toilet(
        west_edge=ensuite_west,
        south_edge=ensuite_south,
        floor_top=first_floor_top,
        material=white_mat,
        name_prefix="MD_Ensuite",
    )

    create_vanity(
        east_edge=ensuite_east,
        south_edge=ensuite_south,
        floor_top=first_floor_top,
        basin_material=white_mat,
        chrome_material=chrome_mat,
        name_prefix="MD_Ensuite",
        rotation_z_degrees=270,
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

    bed_x = east_interior_face - BED_LENGTH / 2 - 1.5
    bed_y = north_interior_face - BED_WIDTH / 2 - 1
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


def create_toilet(west_edge, south_edge, floor_top, material, name_prefix="MD"):
    """Create a simple toilet fixture with bowl and tank from west/south room edges."""
    toilet_width = 0.4
    toilet_depth = 0.6
    toilet_height = 0.4
    toilet_tank_height = 0.8
    toilet_tank_width = 0.15
    south_offset = 0.15

    toilet_center_x = west_edge + toilet_depth / 2
    toilet_center_y = south_edge + toilet_width / 2 + south_offset

    bpy.ops.mesh.primitive_cube_add(location=(toilet_center_x, toilet_center_y, floor_top + toilet_height / 2))
    toilet_bowl = bpy.context.active_object
    toilet_bowl.name = f"{name_prefix}_ToiletBowl"
    toilet_bowl.scale = (toilet_depth / 2, toilet_width / 2, toilet_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    toilet_bowl.data.materials.append(material)

    bpy.ops.mesh.primitive_cube_add(location=(west_edge + toilet_tank_width / 2, toilet_center_y, floor_top + toilet_tank_height / 2))
    toilet_tank = bpy.context.active_object
    toilet_tank.name = f"{name_prefix}_ToiletTank"
    toilet_tank.scale = (toilet_tank_width / 2, toilet_width / 2, toilet_tank_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    toilet_tank.data.materials.append(material)

    return toilet_bowl, toilet_tank


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
