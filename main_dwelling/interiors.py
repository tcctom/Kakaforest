import bpy  # type: ignore

from materials import get_interior_wall_material, get_kitchen_bench_material
from main_dwelling.materials_nodes import create_material
from utils import add_window


def _create_interior_partitions_ground_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Create ground floor interior partitions for guest bedroom with built-in wardrobe."""
    interior_wall_mat = get_interior_wall_material()

    GUEST_BEDROOM_WIDTH = 3.30
    GUEST_BEDROOM_DEPTH = 3.6

    east_interior_face = ox + LENGTH / 2 - EXTERIOR_WALL_THICKNESS
    north_interior_face = oy + WIDTH / 2 - NORTH_RECESS

    FLOOR_SLAB_THICKNESS = 0.1
    ground_floor_wall_height = GROUND_FLOOR_HEIGHT - FLOOR_SLAB_THICKNESS

    WEST_WALL_EXTENSION = 0.7
    west_partition_x = east_interior_face - GUEST_BEDROOM_WIDTH - INTERIOR_WALL_THICKNESS / 2
    west_partition_center_y = north_interior_face - (GUEST_BEDROOM_DEPTH + WEST_WALL_EXTENSION) / 2

    bpy.ops.mesh.primitive_cube_add(location=(west_partition_x, west_partition_center_y, oz + ground_floor_wall_height / 2))
    west_partition = bpy.context.active_object
    west_partition.name = "MainDwelling_GroundFloor_GuestBedroomWestWall"
    west_partition.scale = (INTERIOR_WALL_THICKNESS / 2, (GUEST_BEDROOM_DEPTH + WEST_WALL_EXTENSION) / 2, ground_floor_wall_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    west_partition.data.materials.append(interior_wall_mat)

    south_partition_y = north_interior_face - GUEST_BEDROOM_DEPTH + INTERIOR_WALL_THICKNESS / 2
    south_partition_center_x = east_interior_face - GUEST_BEDROOM_WIDTH / 2

    bpy.ops.mesh.primitive_cube_add(location=(south_partition_center_x, south_partition_y, oz + ground_floor_wall_height / 2))
    south_partition = bpy.context.active_object
    south_partition.name = "MainDwelling_GroundFloor_GuestBedroomSouthWall"
    south_partition.scale = (GUEST_BEDROOM_WIDTH / 2, INTERIOR_WALL_THICKNESS / 2, ground_floor_wall_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    south_partition.data.materials.append(interior_wall_mat)

    door_x = east_interior_face - 2.6
    add_window(
        "MainDwelling_GroundFloor_GuestBedroomSouthWall",
        (door_x, south_partition_y - INTERIOR_WALL_THICKNESS / 2, oz + 1.0),
        width=0.8,
        height=2.0,
        depth=INTERIOR_WALL_THICKNESS,
        axis='Y',
        inward_offset='+Y',
    )

    SOUTH_WALL_WEST_EXTENSION = 0.8

    south_wall_west_end_x = east_interior_face - GUEST_BEDROOM_WIDTH
    south_wall_extension_center_x = south_wall_west_end_x - SOUTH_WALL_WEST_EXTENSION / 2

    bpy.ops.mesh.primitive_cube_add(location=(south_wall_extension_center_x, south_partition_y, oz + ground_floor_wall_height / 2))
    south_wall_extension = bpy.context.active_object
    south_wall_extension.name = "MainDwelling_GroundFloor_GuestBedroomSouthWall_WestExtension"
    south_wall_extension.scale = (SOUTH_WALL_WEST_EXTENSION / 2, INTERIOR_WALL_THICKNESS / 2, ground_floor_wall_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall_extension.data.materials.append(interior_wall_mat)

    south_wall_extension_west_x = south_wall_west_end_x - SOUTH_WALL_WEST_EXTENSION
    south_wall_south_face_y = south_partition_y - INTERIOR_WALL_THICKNESS / 2
    south_wall_return_center_y = south_wall_south_face_y - WEST_WALL_EXTENSION / 2

    bpy.ops.mesh.primitive_cube_add(location=(south_wall_extension_west_x+0.05, south_wall_return_center_y, oz + ground_floor_wall_height / 2))
    south_wall_return = bpy.context.active_object
    south_wall_return.name = "MainDwelling_GroundFloor_GuestBedroomSouthWall_WestReturn"
    south_wall_return.scale = (INTERIOR_WALL_THICKNESS / 2, WEST_WALL_EXTENSION / 2, ground_floor_wall_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall_return.data.materials.append(interior_wall_mat)

    # Add a physical door leaf to close the new small cupboard on the south face.
    SMALL_CUPBOARD_DOOR_THICKNESS = 0.04
    SMALL_CUPBOARD_DOOR_SOUTH_OFFSET = 0.7
    small_cupboard_opening_width = abs(west_partition_x - south_wall_extension_west_x) - INTERIOR_WALL_THICKNESS
    small_cupboard_door_width = max(0.2, small_cupboard_opening_width)
    door_hinge_x = west_partition_x - INTERIOR_WALL_THICKNESS / 2
    small_cupboard_door_x = door_hinge_x - small_cupboard_door_width / 2
    small_cupboard_door_y = south_wall_south_face_y - SMALL_CUPBOARD_DOOR_THICKNESS / 2 - SMALL_CUPBOARD_DOOR_SOUTH_OFFSET
    small_cupboard_door_height = 2.0

    bpy.ops.mesh.primitive_cube_add(location=(small_cupboard_door_x, small_cupboard_door_y, oz + small_cupboard_door_height / 2))
    small_cupboard_door = bpy.context.active_object
    small_cupboard_door.name = "MainDwelling_GroundFloor_GuestBedroomSmallCupboardSouthDoor"
    small_cupboard_door.scale = (
        small_cupboard_door_width / 2,
        SMALL_CUPBOARD_DOOR_THICKNESS / 2,
        small_cupboard_door_height / 2,
    )
    bpy.ops.object.transform_apply(scale=True)
    small_cupboard_door.data.materials.append(interior_wall_mat)

    CUPBOARD_WIDTH = 0.6
    CUPBOARD_DEPTH = 2.2

    cupboard_west_wall_x = west_partition_x - INTERIOR_WALL_THICKNESS / 2 - CUPBOARD_WIDTH - INTERIOR_WALL_THICKNESS / 2
    cupboard_west_wall_center_y = north_interior_face - CUPBOARD_DEPTH / 2

    bpy.ops.mesh.primitive_cube_add(location=(cupboard_west_wall_x, cupboard_west_wall_center_y, oz + ground_floor_wall_height / 2))
    cupboard_west_wall = bpy.context.active_object
    cupboard_west_wall.name = "MainDwelling_GroundFloor_GuestBedroomCupboardWestWall"
    cupboard_west_wall.scale = (INTERIOR_WALL_THICKNESS / 2, CUPBOARD_DEPTH / 2, ground_floor_wall_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    cupboard_west_wall.data.materials.append(interior_wall_mat)

    cupboard_south_wall_y = north_interior_face - CUPBOARD_DEPTH + INTERIOR_WALL_THICKNESS / 2
    cupboard_south_wall_center_x = west_partition_x - INTERIOR_WALL_THICKNESS / 2 - CUPBOARD_WIDTH / 2

    bpy.ops.mesh.primitive_cube_add(location=(cupboard_south_wall_center_x, cupboard_south_wall_y, oz + ground_floor_wall_height / 2))
    cupboard_south_wall = bpy.context.active_object
    cupboard_south_wall.name = "MainDwelling_GroundFloor_GuestBedroomCupboardSouthWall"
    cupboard_south_wall.scale = (CUPBOARD_WIDTH / 2, INTERIOR_WALL_THICKNESS / 2, ground_floor_wall_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    cupboard_south_wall.data.materials.append(interior_wall_mat)

    BED_WIDTH = 1.6
    BED_LENGTH = 2.0
    BED_HEIGHT = 0.6

    bed_mat = create_material("BedFabric", (0.95, 0.95, 0.9, 1))

    guest_bed_x = east_interior_face - GUEST_BEDROOM_WIDTH / 2 + 0.3
    guest_bed_y = south_partition_y + INTERIOR_WALL_THICKNESS / 2 + BED_LENGTH / 2
    guest_bed_z = oz + BED_HEIGHT / 2

    bpy.ops.mesh.primitive_cube_add(location=(guest_bed_x, guest_bed_y, guest_bed_z))
    guest_bed = bpy.context.active_object
    guest_bed.name = "MainDwelling_GuestBedroom_KingBed"
    guest_bed.scale = (BED_WIDTH / 2, BED_LENGTH / 2, BED_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    guest_bed.data.materials.append(bed_mat)

    STAIRWELL_WIDTH = 2.0
    PARTITION_LENGTH = 2.6

    west_interior_x = ox - LENGTH / 2 + EXTERIOR_WALL_THICKNESS
    south_interior_y = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS

    stairwell_east_x = west_interior_x + STAIRWELL_WIDTH

    partition_x = stairwell_east_x + INTERIOR_WALL_THICKNESS / 2
    partition_center_y = south_interior_y + PARTITION_LENGTH / 2

    full_partition_height = GROUND_FLOOR_HEIGHT + FIRST_FLOOR_HEIGHT

    bpy.ops.mesh.primitive_cube_add(location=(partition_x, partition_center_y, oz + full_partition_height / 2))
    stair_partition = bpy.context.active_object
    stair_partition.name = "MainDwelling_StaircasePartition_BothFloors"
    stair_partition.scale = (INTERIOR_WALL_THICKNESS / 2, PARTITION_LENGTH / 2, full_partition_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    stair_partition.data.materials.append(interior_wall_mat)

    LOG_BURNER_WIDTH = 0.5
    LOG_BURNER_DEPTH = 0.65
    LOG_BURNER_HEIGHT = 0.7
    LEG_HEIGHT = 0.15
    LEG_DIAMETER = 0.05
    FLUE_DIAMETER = 0.15
    FLUE_HEIGHT = 6.8

    log_burner_mat = create_material("LogBurner", (0.1, 0.1, 0.1, 1))
    flue_mat = create_material("FluePipe", (0.15, 0.15, 0.15, 1))
    granite_mat = get_kitchen_bench_material()
    glass_mat = create_material("LogBurnerGlass", (0.1, 0.1, 0.1, 0.3))

    cupboard_south_edge_y = north_interior_face - CUPBOARD_DEPTH
    log_burner_x = west_partition_x - INTERIOR_WALL_THICKNESS / 2 - CUPBOARD_WIDTH / 2 - 0.10
    log_burner_y = cupboard_south_edge_y - 0.3 - LOG_BURNER_DEPTH / 2

    FLOOR_TOP = oz + 0.1
    HEARTH_THICKNESS = 0.03
    log_burner_z = FLOOR_TOP + HEARTH_THICKNESS + LEG_HEIGHT + LOG_BURNER_HEIGHT / 2

    HEARTH_WIDTH = LOG_BURNER_WIDTH + 0.4
    hearth_north_edge = cupboard_south_edge_y
    HEARTH_DEPTH = 1.3
    hearth_south_edge = hearth_north_edge - HEARTH_DEPTH
    hearth_y = (hearth_north_edge + hearth_south_edge) / 2

    bpy.ops.mesh.primitive_cube_add(location=(log_burner_x, hearth_y, FLOOR_TOP + HEARTH_THICKNESS / 2))
    hearth = bpy.context.active_object
    hearth.name = "MainDwelling_GuestBedroom_Hearth"
    hearth.scale = (HEARTH_WIDTH / 2, HEARTH_DEPTH / 2, HEARTH_THICKNESS / 2)
    bpy.ops.object.transform_apply(scale=True)
    hearth.data.materials.append(granite_mat)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.mesh.primitive_cube_add(location=(log_burner_x, log_burner_y, log_burner_z))
    log_burner = bpy.context.active_object
    log_burner.name = "MainDwelling_GuestBedroom_LogBurner"
    log_burner.scale = (LOG_BURNER_WIDTH / 2, LOG_BURNER_DEPTH / 2, LOG_BURNER_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    log_burner.data.materials.append(log_burner_mat)

    leg_offset_x = LOG_BURNER_WIDTH / 2 - LEG_DIAMETER
    leg_offset_y = LOG_BURNER_DEPTH / 2 - LEG_DIAMETER
    leg_positions = [
        (log_burner_x - leg_offset_x, log_burner_y - leg_offset_y),
        (log_burner_x + leg_offset_x, log_burner_y - leg_offset_y),
        (log_burner_x - leg_offset_x, log_burner_y + leg_offset_y),
        (log_burner_x + leg_offset_x, log_burner_y + leg_offset_y),
    ]

    for i, (leg_x, leg_y) in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(
            location=(leg_x, leg_y, FLOOR_TOP + HEARTH_THICKNESS + LEG_HEIGHT / 2),
            radius=LEG_DIAMETER / 2,
            depth=LEG_HEIGHT,
        )
        leg = bpy.context.active_object
        leg.name = f"MainDwelling_GuestBedroom_LogBurner_Leg_{i + 1}"
        leg.data.materials.append(log_burner_mat)

    GLASS_WIDTH = LOG_BURNER_WIDTH * 0.8
    GLASS_HEIGHT = LOG_BURNER_HEIGHT * 0.7
    GLASS_THICKNESS = 0.01

    glass_x = log_burner_x - LOG_BURNER_WIDTH / 2 - GLASS_THICKNESS / 2
    glass_z = log_burner_z

    bpy.ops.mesh.primitive_cube_add(location=(glass_x, log_burner_y, glass_z))
    glass_door = bpy.context.active_object
    glass_door.name = "MainDwelling_GuestBedroom_LogBurner_GlassDoor"
    glass_door.scale = (GLASS_THICKNESS / 2, GLASS_WIDTH / 2, GLASS_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    glass_door.data.materials.append(glass_mat)

    glass_mat.blend_method = 'BLEND'
    bsdf = glass_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Alpha'].default_value = 0.3
    bsdf.inputs['Transmission Weight'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.0

    flue_z = FLOOR_TOP + HEARTH_THICKNESS + LEG_HEIGHT + LOG_BURNER_HEIGHT + FLUE_HEIGHT / 2
    bpy.ops.mesh.primitive_cylinder_add(location=(log_burner_x, log_burner_y, flue_z), radius=FLUE_DIAMETER / 2, depth=FLUE_HEIGHT)
    flue = bpy.context.active_object
    flue.name = "MainDwelling_GuestBedroom_Flue"
    flue.data.materials.append(flue_mat)


def _create_interior_partitions_first_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Create first floor interior partitions for master bedroom, ensuite, and wardrobe."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    interior_wall_mat = get_interior_wall_material()

    MASTER_BEDROOM_WIDTH = 4.0
    ENSUITE_DEPTH = 2.0
    ENSUITE_WIDTH = 2.0

    north_interior_face = oy + WIDTH / 2 - NORTH_RECESS
    south_interior_face = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS
    interior_depth = north_interior_face - south_interior_face
    east_interior_face = ox + LENGTH / 2 - EXTERIOR_WALL_THICKNESS

    main_partition_x = east_interior_face - MASTER_BEDROOM_WIDTH - INTERIOR_WALL_THICKNESS / 2
    main_partition_center_y = (north_interior_face + south_interior_face) / 2
    bpy.ops.mesh.primitive_cube_add(location=(main_partition_x, main_partition_center_y, first_floor_z + FIRST_FLOOR_HEIGHT / 2))
    main_partition = bpy.context.active_object
    main_partition.name = "MainDwelling_FirstFloor_MainPartition"
    main_partition.scale = (INTERIOR_WALL_THICKNESS / 2, interior_depth / 2, FIRST_FLOOR_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    main_partition.data.materials.append(interior_wall_mat)

    bedroom_partition_y = south_interior_face + ENSUITE_DEPTH
    bedroom_partition_center_x = east_interior_face - MASTER_BEDROOM_WIDTH / 2

    bpy.ops.mesh.primitive_cube_add(location=(bedroom_partition_center_x, bedroom_partition_y, first_floor_z + FIRST_FLOOR_HEIGHT / 2))
    bedroom_south_partition = bpy.context.active_object
    bedroom_south_partition.name = "MainDwelling_FirstFloor_BedroomSouthPartition"
    bedroom_south_partition.scale = (MASTER_BEDROOM_WIDTH / 2, INTERIOR_WALL_THICKNESS / 2, FIRST_FLOOR_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    bedroom_south_partition.data.materials.append(interior_wall_mat)

    ensuite_wardrobe_wall_x = east_interior_face - ENSUITE_WIDTH
    ensuite_wardrobe_wall_center_y = south_interior_face + ENSUITE_DEPTH / 2

    bpy.ops.mesh.primitive_cube_add(location=(ensuite_wardrobe_wall_x, ensuite_wardrobe_wall_center_y, first_floor_z + FIRST_FLOOR_HEIGHT / 2))
    ensuite_wardrobe_wall = bpy.context.active_object
    ensuite_wardrobe_wall.name = "MainDwelling_FirstFloor_EnsuiteWardrobeWall"
    ensuite_wardrobe_wall.scale = (INTERIOR_WALL_THICKNESS / 2, ENSUITE_DEPTH / 2, FIRST_FLOOR_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    ensuite_wardrobe_wall.data.materials.append(interior_wall_mat)

    add_window(
        "MainDwelling_FirstFloor_MainPartition",
        (main_partition_x + INTERIOR_WALL_THICKNESS / 2, oy + 2.0, first_floor_z + 1.0),
        width=0.8,
        height=2.0,
        depth=INTERIOR_WALL_THICKNESS,
        axis='X',
        inward_offset='-X',
    )

    add_window(
        "MainDwelling_FirstFloor_BedroomSouthPartition",
        (east_interior_face - 0.45, bedroom_partition_y - INTERIOR_WALL_THICKNESS / 2, first_floor_z + 1.0),
        width=0.8,
        height=2.0,
        depth=INTERIOR_WALL_THICKNESS,
        axis='Y',
        inward_offset='+Y',
    )

    add_window(
        "MainDwelling_FirstFloor_BedroomSouthPartition",
        (ensuite_wardrobe_wall_x - 1.5, bedroom_partition_y - INTERIOR_WALL_THICKNESS / 2, first_floor_z + 1.0),
        width=0.8,
        height=2.0,
        depth=INTERIOR_WALL_THICKNESS,
        axis='Y',
        inward_offset='+Y',
    )

    BED_WIDTH = 1.8
    BED_LENGTH = 2.0
    BED_HEIGHT = 0.6

    bed_mat = create_material("BedFabric", (0.95, 0.95, 0.9, 1))

    bed_x = east_interior_face - MASTER_BEDROOM_WIDTH / 2
    bed_y = bedroom_partition_y + INTERIOR_WALL_THICKNESS / 2 + BED_LENGTH / 2
    bed_z = first_floor_z + BED_HEIGHT / 2

    bpy.ops.mesh.primitive_cube_add(location=(bed_x, bed_y, bed_z))
    bed = bpy.context.active_object
    bed.name = "MainDwelling_MasterBedroom_KingBed"
    bed.scale = (BED_WIDTH / 2, BED_LENGTH / 2, BED_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    bed.data.materials.append(bed_mat)
