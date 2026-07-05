import os
import sys

import bpy  # type: ignore
import math
import mathutils

if __package__ in {None, ""}:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from materials import get_interior_door_material, get_interior_wall_material, get_kitchen_bench_material
from main_dwelling.materials_nodes import create_material, create_textured_material2
from utils import add_window



def _create_interior_partitions_ground_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Create ground floor interior partitions."""

    GUEST_BEDROOM_WIDTH = 3.20 #east wall to west wall
    GUEST_BEDROOM_DEPTH = 3.35 #north wall to south wall
    CUPBOARD_INTERIOR_XAXIS = 0.6
    CUPBOARD_DEPTH = 1.95
    FLOOR_SLAB_THICKNESS = 0.1
    FLOOR_TOP = oz + FLOOR_SLAB_THICKNESS

    east_interior_face = ox + LENGTH / 2 - EXTERIOR_WALL_THICKNESS
    south_interior_face = oy - WIDTH / 2 + EXTERIOR_WALL_THICKNESS
    north_interior_face = oy + WIDTH / 2 - NORTH_RECESS
    ground_floor_wall_height = GROUND_FLOOR_HEIGHT - FLOOR_SLAB_THICKNESS

    west_partition_x = east_interior_face - GUEST_BEDROOM_WIDTH - INTERIOR_WALL_THICKNESS / 2
    west_partition_center_y = north_interior_face - GUEST_BEDROOM_DEPTH/ 2
    south_partition_y = north_interior_face - GUEST_BEDROOM_DEPTH + INTERIOR_WALL_THICKNESS / 2
    south_partition_center_x = east_interior_face - GUEST_BEDROOM_WIDTH / 2

    create_interior_wall( name="MD_GF_GuestBedroomWestWall",
        location=(west_partition_x, west_partition_center_y, FLOOR_TOP + ground_floor_wall_height / 2),
        size=(INTERIOR_WALL_THICKNESS, GUEST_BEDROOM_DEPTH, ground_floor_wall_height),
    )
    add_window( "MD_GF_GuestBedroomWestWall",
        (west_partition_x - INTERIOR_WALL_THICKNESS / 2, oy + 1.6, FLOOR_TOP + 1.0),
        width=1.5, height=2.0, depth=INTERIOR_WALL_THICKNESS,
        axis='X', inward_offset='+X',
    )
    create_interior_wall( name="MD_GF_GuestBedroomWestWall_Ext",
        location=(west_partition_x, south_partition_y -0.4, FLOOR_TOP + ground_floor_wall_height / 2),
        size=(INTERIOR_WALL_THICKNESS, 0.7, ground_floor_wall_height),
    )

    create_interior_wall( name="MD_GF_GuestBedroomSouthWall",
        location=(south_partition_center_x, south_partition_y, FLOOR_TOP + ground_floor_wall_height / 2),
        size=(GUEST_BEDROOM_WIDTH, INTERIOR_WALL_THICKNESS, ground_floor_wall_height),
    )

    # Bathroom partition: runs south-to-north and ties into GuestBedroomSouthWall.
    bathroom_partition_x = east_interior_face - 2.0 - INTERIOR_WALL_THICKNESS / 2
    bathroom_partition_length = south_partition_y - south_interior_face
    bathroom_partition_center_y = south_interior_face + bathroom_partition_length / 2

    create_interior_wall( name="MD_GF_BathroomPartitionWall",
        location=(bathroom_partition_x, bathroom_partition_center_y, FLOOR_TOP + ground_floor_wall_height / 2),
        size=(INTERIOR_WALL_THICKNESS, bathroom_partition_length, ground_floor_wall_height),
    )

    # Door opening center is 700 mm from the southern edge to the start of the opening.
    bathroom_door_width = 0.8
    bathroom_door_center_y = south_interior_face + 0.7 + bathroom_door_width / 2
    add_window("MD_GF_BathroomPartitionWall",
        (bathroom_partition_x - INTERIOR_WALL_THICKNESS / 2, bathroom_door_center_y, FLOOR_TOP + 1.0),
        width=bathroom_door_width, height=2.0, depth=INTERIOR_WALL_THICKNESS,
        axis='X', inward_offset='+X',
    )

    door_x = east_interior_face - 2.6
    add_window( "MD_GF_GuestBedroomSouthWall",
        (door_x, south_partition_y - INTERIOR_WALL_THICKNESS / 2, FLOOR_TOP + 1.0),
        width=0.8, height=2.0, depth=INTERIOR_WALL_THICKNESS,
        axis='Y', inward_offset='+Y',
    )

    south_wall_west_end_x = east_interior_face - GUEST_BEDROOM_WIDTH

    south_wall_extension_west_x = south_wall_west_end_x - CUPBOARD_INTERIOR_XAXIS
    south_wall_south_face_y = south_partition_y - INTERIOR_WALL_THICKNESS / 2

    # Add a physical door leaf to close the new small cupboard on the south face.
    SMALL_CUPBOARD_DOOR_THICKNESS = 0.04
    SMALL_CUPBOARD_DOOR_SOUTH_OFFSET = 0.7
    small_cupboard_opening_width = abs(west_partition_x - south_wall_extension_west_x) - INTERIOR_WALL_THICKNESS
    small_cupboard_door_width = max(0.2, small_cupboard_opening_width)
    door_hinge_x = west_partition_x - INTERIOR_WALL_THICKNESS / 2
    small_cupboard_door_x = door_hinge_x - small_cupboard_door_width / 2
    small_cupboard_door_y = south_wall_south_face_y - SMALL_CUPBOARD_DOOR_THICKNESS / 2 - SMALL_CUPBOARD_DOOR_SOUTH_OFFSET
    small_cupboard_door_height = 2.0

    bpy.ops.mesh.primitive_cube_add(location=(small_cupboard_door_x, small_cupboard_door_y, FLOOR_TOP + small_cupboard_door_height / 2))
    small_cupboard_door = bpy.context.active_object
    small_cupboard_door.name = "MD_GF_GuestBedroomSmallCupboardSouthDoor"
    small_cupboard_door.scale = (
        small_cupboard_door_width / 2,
        SMALL_CUPBOARD_DOOR_THICKNESS / 2,
        small_cupboard_door_height / 2,
    )
    bpy.ops.object.transform_apply(scale=True)
    interior_door_mat = get_interior_door_material()
    small_cupboard_door.data.materials.append(interior_door_mat)


    cupboard_west_wall_x = west_partition_x - INTERIOR_WALL_THICKNESS / 2 - CUPBOARD_INTERIOR_XAXIS - INTERIOR_WALL_THICKNESS / 2
    cupboard_west_wall_center_y = north_interior_face - CUPBOARD_DEPTH / 2

    cupboard_south_wall_y = north_interior_face - CUPBOARD_DEPTH + INTERIOR_WALL_THICKNESS / 2
    cupboard_south_wall_center_x = west_partition_x - INTERIOR_WALL_THICKNESS / 2 - CUPBOARD_INTERIOR_XAXIS / 2

    create_interior_wall( name="MD_GF_GuestBedroomCupboardSouthWall",
        location=(cupboard_south_wall_center_x, cupboard_south_wall_y, FLOOR_TOP + ground_floor_wall_height / 2),
        size=(CUPBOARD_INTERIOR_XAXIS, INTERIOR_WALL_THICKNESS, ground_floor_wall_height),
    )

    create_interior_wall( name="MD_GF_GuestBedroomSouthWall_WestExtension",
        location=(cupboard_south_wall_center_x, south_partition_y, FLOOR_TOP + ground_floor_wall_height / 2),
        size=(CUPBOARD_INTERIOR_XAXIS, INTERIOR_WALL_THICKNESS, ground_floor_wall_height),
    )

    create_interior_wall( name="MD_GF_NorthOfLogBurner_NS",
        location=(cupboard_west_wall_x, cupboard_west_wall_center_y, FLOOR_TOP + ground_floor_wall_height / 2),
        size=(INTERIOR_WALL_THICKNESS, CUPBOARD_DEPTH, ground_floor_wall_height),
    )

    create_interior_wall( name="MD_GF_SouthOfLogBurner_NS",
        location=(cupboard_west_wall_x, south_wall_south_face_y - 0.3, FLOOR_TOP + ground_floor_wall_height / 2),
        size=(INTERIOR_WALL_THICKNESS, 0.8, ground_floor_wall_height),
    )    

    BED_WIDTH = 1.6
    BED_LENGTH = 2.0
    BED_HEIGHT = 0.6

    bed_mat = create_material("BedFabric", (0.95, 0.95, 0.9, 1))

    guest_bed_x = east_interior_face - GUEST_BEDROOM_WIDTH / 2 + 0.3
    guest_bed_y = south_partition_y + INTERIOR_WALL_THICKNESS / 2 + BED_LENGTH / 2
    guest_bed_z = FLOOR_TOP + BED_HEIGHT / 2

    bpy.ops.mesh.primitive_cube_add(location=(guest_bed_x, guest_bed_y, guest_bed_z))
    guest_bed = bpy.context.active_object
    guest_bed.name = "MD_GuestBedroom_KingBed"
    guest_bed.scale = (BED_WIDTH / 2, BED_LENGTH / 2, BED_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    guest_bed.data.materials.append(bed_mat)

    STAIRWELL_WIDTH = 2.0
    PARTITION_LENGTH = 2.7

    west_interior_x = ox - LENGTH / 2 + EXTERIOR_WALL_THICKNESS
    south_interior_y = south_interior_face

    stairwell_east_x = west_interior_x + STAIRWELL_WIDTH

    partition_x = stairwell_east_x + INTERIOR_WALL_THICKNESS / 2
    partition_center_y = south_interior_y + PARTITION_LENGTH / 2

    full_partition_height = (GROUND_FLOOR_HEIGHT - FLOOR_SLAB_THICKNESS) + FIRST_FLOOR_HEIGHT

    create_interior_wall( name="MD_StaircasePartition_BothFloors",
        location=(partition_x, partition_center_y, FLOOR_TOP + full_partition_height / 2),
        size=(INTERIOR_WALL_THICKNESS, PARTITION_LENGTH, full_partition_height),
    )

    #create_interior_wall( name="MD_StaircaseDivider_BothFloors",
    #    location=(stairwell_east_x - 1, south_interior_y + 1 + 1.7 / 2, FLOOR_TOP + 3.7/2),
    #    size=(INTERIOR_WALL_THICKNESS, 1.7, 3.7),
    #)

    create_balustrade(name="MD_StaircaseDivider_BothFloors"
                      , location=(stairwell_east_x - 1, south_interior_y + 1, FLOOR_TOP)
                      , size=(INTERIOR_WALL_THICKNESS, 1.7, 2.45), rise_top=1.25)

    # Upstairs Return (East-West, rotated 90 degrees)
    # Adjusted size: (Thickness, Length/Run=1.0m, Height=1.0m)
    create_balustrade(
        name="MD_Staircase_Baulustrade_Upstairs",
        location=(stairwell_east_x, south_interior_y + 2.65, oz + 2.7),
        size=(INTERIOR_WALL_THICKNESS, 1.0, 1.0), 
        rise_top=0.0, 
        rise_bottom=0.0, 
        hide_start_post=True, 
        hide_end_post=True,
        rotation_z=90.0 # Flips the rail to line up East-West
    )

    # Create wall behind log burner (East)
    create_fireplace_wall( name="MD_HearthWallEast",
        location=(west_partition_x-0.1, oy, oz + 0.6),
        size=(0.1, 1.3, 1.2)
    )

    # Create wall south of log burner
    create_fireplace_wall( name="MD_HearthWallSouth",
        location=(west_partition_x-0.45, oy - 0.6, oz + 0.6),
        size=(0.6, 0.1, 1.2)
    )

    # Create wall north of log burner
    create_fireplace_wall( name="MD_HearthWallNorth",
        location=(west_partition_x-0.45, oy + 0.6, oz + 0.6),
        size=(0.6, 0.1, 1.2)
    )

    # --- 2. Place Candlestick on top of South Wall ---
    # Radius = 0.04m (8cm total diameter base)
    # Height = 0.3m (30cm tall)
    # Location matches the wall's X and Y, with Z calculated to rest perfectly on top.
    #create_candlestick( name="Prop_WoodenCandlestick_01", location=(0.5, -0.6, 1.35), radius=0.04, height=0.3    )

    # Place your real 3D candlestick asset onto the South wall
    import_candlestick(
        name="Prop_RealCandlestick_01",
        location=(0.5, oy - 0.6, oz+1.2), 
        scale=(1.0, 1.0, 1.0)
    )


    #create hearth and log burner
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
    log_burner_x = west_partition_x - INTERIOR_WALL_THICKNESS / 2 - CUPBOARD_INTERIOR_XAXIS / 2 - 0.20
    log_burner_y = oy

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

    #create_floor_covering("Floor_A", (0,0,0.501), (2,2), "textures\\granite_tile_03\\granite_tile_03_diff_1k.jpg")
    create_floor_covering(name="Floor_A"
                          , location=(3.3,-3.05,FLOOR_TOP+0.001), size=(2.05,2.7)
                          , texture_path="C:\\Users\\Tom (local)\\GH\\Kakaforest\\textures\\granite_tile_03\\granite_tile_03_diff_1k.jpg"
                          ,texture_image_width=0.5
                          )




def _create_interior_partitions_first_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Create first floor interior partitions for master bedroom, ensuite, and wardrobe."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    FIRST_FLOOR_SLAB_THICKNESS = 0.2
    first_floor_top = first_floor_z + FIRST_FLOOR_SLAB_THICKNESS
    first_floor_wall_height = FIRST_FLOOR_HEIGHT - FIRST_FLOOR_SLAB_THICKNESS
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
    main_partition = create_wall(
        name="MD_FF_MainPartition",
        location=(main_partition_x, main_partition_center_y, first_floor_top + first_floor_wall_height / 2),
        size=(INTERIOR_WALL_THICKNESS, interior_depth, first_floor_wall_height),
        material=interior_wall_mat,
    )

    bedroom_partition_y = south_interior_face + ENSUITE_DEPTH
    bedroom_partition_center_x = east_interior_face - MASTER_BEDROOM_WIDTH / 2

    bedroom_south_partition = create_wall(
        name="MD_FF_BedroomSouthPartition",
        location=(bedroom_partition_center_x, bedroom_partition_y, first_floor_top + first_floor_wall_height / 2),
        size=(MASTER_BEDROOM_WIDTH, INTERIOR_WALL_THICKNESS, first_floor_wall_height),
        material=interior_wall_mat,
    )

    ensuite_wardrobe_wall_x = east_interior_face - ENSUITE_WIDTH
    ensuite_wardrobe_wall_center_y = south_interior_face + ENSUITE_DEPTH / 2

    ensuite_wardrobe_wall = create_wall(
        name="MD_FF_EnsuiteWardrobeWall",
        location=(ensuite_wardrobe_wall_x, ensuite_wardrobe_wall_center_y, first_floor_top + first_floor_wall_height / 2),
        size=(INTERIOR_WALL_THICKNESS, ENSUITE_DEPTH, first_floor_wall_height),
        material=interior_wall_mat,
    )

    add_window(
        "MD_FF_MainPartition",
        (main_partition_x + INTERIOR_WALL_THICKNESS / 2, oy + 2.0, first_floor_top + 1.0),
        width=0.8, height=2.0, depth=INTERIOR_WALL_THICKNESS,
        axis='X', inward_offset='-X',
    )

    add_window(
        "MD_FF_BedroomSouthPartition",
        (east_interior_face - 0.45, bedroom_partition_y - INTERIOR_WALL_THICKNESS / 2, first_floor_top + 1.0),
        width=0.8, height=2.0, depth=INTERIOR_WALL_THICKNESS,
        axis='Y', inward_offset='+Y',
    )

    add_window(
        "MD_FF_BedroomSouthPartition",
        (ensuite_wardrobe_wall_x - 1.5, bedroom_partition_y - INTERIOR_WALL_THICKNESS / 2, first_floor_top + 1.0),
        width=0.8, height=2.0, depth=INTERIOR_WALL_THICKNESS,
        axis='Y', inward_offset='+Y',
    )

    BED_WIDTH = 1.8
    BED_LENGTH = 2.0
    BED_HEIGHT = 0.6

    bed_mat = create_material("BedFabric", (0.95, 0.95, 0.9, 1))

    bed_x = east_interior_face - MASTER_BEDROOM_WIDTH / 2
    bed_y = bedroom_partition_y + INTERIOR_WALL_THICKNESS / 2 + BED_LENGTH / 2
    bed_z = first_floor_top + BED_HEIGHT / 2

    bpy.ops.mesh.primitive_cube_add(location=(bed_x, bed_y, bed_z))
    bed = bpy.context.active_object
    bed.name = "MainDwelling_MasterBedroom_KingBed"
    bed.scale = (BED_WIDTH / 2, BED_LENGTH / 2, BED_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    bed.data.materials.append(bed_mat)



def create_balustrade(name, location, size, rise_top=0.0, rise_bottom=0.0, 
                      hide_start_post=False, hide_end_post=False, rotation_z=0.0):
    """
    Creates a sloped balustrade assembly for stairs with independently controllable 
    top and bottom slope gains. Includes a rotation parameter for orientation alignment.
    
    Parameters:
    - size (tuple): (width/thickness, horizontal_run/length, flat_height)
    - rotation_z (float): Z-axis rotation in degrees (e.g., 90.0 for East-West alignment)
    """
    width, run, flat_height = size
    post_width = width  
    baluster_width = width * 0.5  
    baluster_spacing = 0.2  
    handrail_thickness = 0.05  

    slope_angle = math.atan2(rise_top, run)
    created_parts = []
    
    # -------------------------------------------------------------------------
    # 1. CREATE END POSTS
    # -------------------------------------------------------------------------
    if not hide_start_post:
        y_offset = post_width / 2
        bpy.ops.mesh.primitive_cube_add(location=(0.0, y_offset, flat_height / 2))
        start_post = bpy.context.active_object
        start_post.name = f"{name}_Start_Post"
        start_post.scale = (post_width / 2, post_width / 2, flat_height / 2)
        bpy.ops.object.transform_apply(scale=True)
        created_parts.append(start_post)
        
    if not hide_end_post:
        y_offset = -post_width / 2
        post_z_base = rise_bottom
        post_z_top = flat_height + rise_top
        current_post_height = post_z_top - post_z_base
        
        bpy.ops.mesh.primitive_cube_add(
            location=(0.0, run + y_offset, post_z_base + (current_post_height / 2))
        )
        end_post = bpy.context.active_object
        end_post.name = f"{name}_End_Post"
        end_post.scale = (post_width / 2, post_width / 2, current_post_height / 2)
        bpy.ops.object.transform_apply(scale=True)
        created_parts.append(end_post)

    # -------------------------------------------------------------------------
    # 2. CREATE BALUSTERS
    # -------------------------------------------------------------------------
    start_margin = post_width if not hide_start_post else 0.0
    end_margin = post_width if not hide_end_post else 0.0
    
    available_run = run - (start_margin + end_margin)
    num_spaces = max(1, round(available_run / baluster_spacing))
    actual_spacing = available_run / num_spaces

    for i in range(1 if not hide_start_post else 0, num_spaces + (0 if not hide_end_post else 1)):
        b_y = start_margin + (i * actual_spacing) if not hide_start_post else (i * actual_spacing)
        b_z_base = (b_y / run) * rise_bottom
        b_z_top = flat_height + ((b_y / run) * rise_top) - handrail_thickness
        b_height = b_z_top - b_z_base
        
        if b_height > 0:
            bpy.ops.mesh.primitive_cube_add(
                location=(0.0, b_y, b_z_base + (b_height / 2))
            )
            baluster = bpy.context.active_object
            baluster.name = f"{name}_Baluster_{i}"
            baluster.scale = (baluster_width / 2, baluster_width / 2, b_height / 2)
            bpy.ops.object.transform_apply(scale=True)
            created_parts.append(baluster)

    # -------------------------------------------------------------------------
    # 3. CREATE HANDRAIL
    # -------------------------------------------------------------------------
    sloped_length = math.sqrt(run**2 + rise_top**2)
    bpy.ops.mesh.primitive_cube_add(location=(0.0, sloped_length / 2, -handrail_thickness / 2))
    rail = bpy.context.active_object
    rail.name = f"{name}_Handrail"
    rail.scale = (width / 2, sloped_length / 2, handrail_thickness / 2)
    bpy.ops.object.transform_apply(scale=True)
    
    rail.rotation_euler[0] = slope_angle
    rail.location.z += flat_height
    bpy.ops.object.transform_apply(rotation=True, location=True)
    created_parts.append(rail)

    # -------------------------------------------------------------------------
    # 4. ASSEMBLY, ROTATION, AND LOCATION
    # -------------------------------------------------------------------------
    if not created_parts:
        return None

    bpy.ops.object.select_all(action='DESELECT')
    for part in created_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = created_parts[0]
    bpy.ops.object.join()
    
    final_balustrade = bpy.context.active_object
    final_balustrade.name = name
    
    # Apply rotation around object origin before moving to world location
    if rotation_z != 0.0:
        final_balustrade.rotation_euler[2] = math.radians(rotation_z)
        bpy.ops.object.transform_apply(rotation=True)
    
    final_balustrade.location = location

    return final_balustrade


def create_fireplace_wall(name, location, size):
    """
    High-level wrapper that automatically loads the specific stone 
    material and builds a fireplace wall.
    """
    # 1. Look for or create the specific HearthWall material
    # (Using .get() prevents creating duplicate materials in Blender if run multiple times)
    hearth_wall_mat = bpy.data.materials.get("HearthWall")
    
    if hearth_wall_mat is None:
        stone_path = os.path.abspath("textures/stone_wall_05/stone_wall_05_ao_1k.jpg")
        hearth_wall_mat = create_textured_material2(
            name="HearthWall",
            texture_path=stone_path,
            rotation_z=0,
            scale=(1.5, 1.5, 1.5),
            roughness=0.2,
            projection='BOX',
        )
    
    # 2. Pass everything down to the generic wall creator
    return create_wall(name, location, size, material=hearth_wall_mat)

def create_interior_wall(name, location, size):
    """
    High-level wrapper that automatically loads the specific material and builds an interior wall.
    """
    interior_wall_mat = get_interior_wall_material()
    
    return create_wall(name, location, size, material=interior_wall_mat)

def create_wall(name, location, size, material):
    """
    Low-level utility to spawn a wall primitive, scale it to real-world
    dimensions, apply transforms, and attach a material.
    """
    # Spawn the initial default 2m x 2m x 2m cube
    bpy.ops.mesh.primitive_cube_add(location=location)
    wall_obj = bpy.context.active_object
    wall_obj.name = name
    
    # Scale from center (Target_Size / 2)
    wall_obj.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    
    # Apply scale so textures don't stretch
    bpy.ops.object.transform_apply(scale=True)
    
    # Attach material if one was provided
    if material:
        wall_obj.data.materials.append(material)
        
    return wall_obj

def create_candlestick(name, location, radius, height):
    """
    High-level wrapper that loads the wooden candlestick material 
    and handles the generation of the prop.
    """
    # 1. Look for or create the wooden material
    wood_mat = bpy.data.materials.get("WoodenCandlestickMat")
    
    if wood_mat is None:
        diffuse_path = os.path.abspath("models/textures/wooden_candlestick_diff_1k.jpg")
        rough_path = os.path.abspath("models/textures/wooden_candlestick_rough_1k.exr")
        
        # Reusing your custom textured material function. 
        # Note: If your function doesn't support roughness maps yet, 
        # you can pass rough_path into it or tweak it to handle EXR files.
        wood_mat = create_textured_material2(
            name="WoodenCandlestickMat",
            texture_path=diffuse_path,
            rotation_z=0,
            scale=(1.0, 1.0, 1.0),
            roughness=0.4,  # Fallback if your function doesn't parse the EXR map yet
            projection='BOX'
        )
        
    # 2. Pass dimensions and material to our generic cylinder engine
    return create_cylinder(name, location, radius, height, material=wood_mat)

def create_cylinder(name, location, radius, height, material=None):
    """
    Low-level utility to spawn a cylinder, scale it to real-world
    dimensions, apply transforms, and attach a material.
    """
    # 1. Spawn a default cylinder (Blender default is radius=1m, depth/height=2m)
    # We set vertices=32 for a smooth, clean round look.
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, 
        radius=1.0, 
        depth=2.0, 
        location=location
    )
    
    obj = bpy.context.active_object
    obj.name = name
    
    # 2. Scale from center (Target / Default)
    # Default radius is 1, so scale factor is just the target radius.
    # Default height is 2, so scale factor is target height / 2.
    obj.scale = (radius, radius, height / 2)
    
    # 3. Apply scale transform so textures don't warp
    bpy.ops.object.transform_apply(scale=True)
    
    # 4. Attach material if provided
    if material:
        obj.data.materials.append(material)
        
    return obj

def append_prop(blend_filepath, object_name, location, scale=(1.0, 1.0, 1.0)):
    """
    Low-level utility to append an object from an external .blend file,
    properly catch it in the current scene, scale it, and position it.
    """
    if not os.path.exists(blend_filepath):
        print(f"Error: Blend file not found at {blend_filepath}")
        return None

    # 1. Take a snapshot of all object names *before* the append operation
    existing_objects = set(bpy.data.objects.keys())
    
    # 2. Path inside the blend file pointing to the Object directory
    inner_dir = os.path.join(blend_filepath, "Object")
    
    # 3. Append the specific object
    bpy.ops.wm.append(
        filepath=os.path.join(inner_dir, object_name),
        directory=inner_dir,
        filename=object_name
    )
    
    # 4. Compare snapshots to find the exact object that was just added
    # This completely bypasses the unpredictable 'active_object' quirk
    new_objects = set(bpy.data.objects.keys()) - existing_objects
    
    if not new_objects:
        print(f"Error: Could not find appended object '{object_name}' in scene data.")
        return None
        
    # Grab the newly appended object from our set
    prop_obj = bpy.data.objects[list(new_objects)[0]]
    
    # 5. Position and scale it correctly
    prop_obj.location = location
    prop_obj.scale = scale
    
    # 6. Make it the active/selected object so we can cleanly apply the scale transform
    bpy.context.view_layer.objects.active = prop_obj
    prop_obj.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    
    return prop_obj

def import_candlestick(name, location, scale=(1.0, 1.0, 1.0)):
    """
    High-level wrapper to append the true 3D candlestick mesh 
    from its source .blend file.
    """
    # 1. Update this path to where your asset .blend file is located
    blend_path = os.path.abspath("models/wooden_candlestick_1k.blend")
    
    # 2. Update this to the exact name of the object inside that .blend file
    object_name_inside_blend = "wooden_candlestick" 
    
    # 3. Append the object using our utility
    prop = append_prop(blend_path, object_name_inside_blend, location, scale)
    
    if prop:
        prop.name = name
        # The blend file likely already has the material assigned natively!
        # If the material loses its textures, we can use your custom 
        # material creator to re-link 'wooden_candlestick_diff_1k.jpg'.
        
    return prop


def create_floor_covering(name, location, size, texture_path, texture_image_width=0.0):
    """
    Creates a flat floor covering plane, builds a new material, 
    and maps an image texture to it with optional real-world scale tiling.
    
    Parameters:
    - name (str): Unique name for the floor object and material.
    - location (tuple): (x, y, z) coordinates for the center of the floor.
    - size (tuple): (width_x, length_y) dimensions of the floor.
    - texture_path (str): Relative or absolute system path to the image texture.
    - texture_image_width (float): The real-world width that the texture image file 
                                  represents (e.g., 1.0 for a 1-meter square tile map).
    """
    width_x, length_y = size

    # --- CHOOSE THE PATH RESOLVER ---
    if not os.path.isabs(texture_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        texture_path = os.path.join(script_dir, texture_path)
    # --------------------------------

    # 1. Create the Floor Geometry
    bpy.ops.mesh.primitive_plane_add(location=location)
    floor_obj = bpy.context.active_object
    floor_obj.name = name
    
    floor_obj.scale = (width_x / 2, length_y / 2, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    if hasattr(bpy.ops.uv, "unwrap"):
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    else:
        print("Warning: UV unwrap operator not available; skipping floor UV unwrap.")
    bpy.ops.object.mode_set(mode='OBJECT')

    # 2. Setup the Material and Nodes
    mat = bpy.data.materials.new(name=f"Mat_{name}")
    mat.use_nodes = True
    floor_obj.data.materials.append(mat)
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    
    if os.path.exists(texture_path):
        try:
            img = bpy.data.images.load(texture_path)
            
            # Create shader node chain
            tex_node = nodes.new(type='ShaderNodeTexImage')
            tex_node.image = img
            
            # Handle Tiling Scale calculations if texture_image_width is provided
            if texture_image_width > 0.0:
                coord_node = nodes.new(type='ShaderNodeTexCoord')
                mapping_node = nodes.new(type='ShaderNodeMapping')
                
                # Calculate how many times the real-world image width fits across the floor dimensions
                tiling_factor_x = width_x / texture_image_width
                tiling_factor_y = length_y / texture_image_width
                
                # Assign the repeating scale values to the Mapping node
                mapping_node.inputs['Scale'].default_value = (tiling_factor_x, tiling_factor_y, 1.0)
                
                # Link UV Coordinates -> Mapping Node -> Image Texture
                links.new(coord_node.outputs['UV'], mapping_node.inputs['Vector'])
                links.new(mapping_node.outputs['Vector'], tex_node.inputs['Vector'])
            
            # Link final texture color payload to the Principal Shader base color input
            links.new(tex_node.outputs['Color'], principled.inputs['Base Color'])
            
        except Exception as e:
            print(f"Warning: Could not read image file. Error: {e}")
    else:
        print(f"Warning: Texture path not found at: {texture_path}")

    return floor_obj
