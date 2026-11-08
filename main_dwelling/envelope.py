import bpy  # type: ignore
import math

from materials import get_metal_roof_material
from main_dwelling.materials_nodes import create_material
from utils import add_window, add_door, add_opening


def _add_gable_roof_framing(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, overhang=0.0):
    """Add a ridge beam, rafters, and a slim fascia to suggest a real roof build."""
    eave_height = oz + TOTAL_HEIGHT
    roof_drop = 0.06
    pitch_rad = math.radians(ROOF_PITCH)
    pitch_tan = math.tan(pitch_rad)
    ridge_height = eave_height + (WIDTH / 2) * pitch_tan - roof_drop
    eave_edge_z = eave_height - (overhang * pitch_tan)

    framing_mat = create_material("RoofFramingTimber", (0.55, 0.40, 0.25, 1.0))
    fascia_mat = create_material("RoofFasciaTrim", (0.68, 0.52, 0.35, 1.0))

    ridge_beam_height = 0.24
    ridge_beam_width = 0.10
    ridge_beam_z = ridge_height - ridge_beam_height / 2 - 0.03

    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, ridge_beam_z))
    ridge_beam = bpy.context.active_object
    ridge_beam.name = "MainDwelling_RidgeBeam"
    ridge_beam.scale = ((LENGTH / 2) + overhang, ridge_beam_width / 2, ridge_beam_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    ridge_beam.data.materials.append(framing_mat)

    rafter_width = 0.06
    rafter_depth = 0.24
    rafter_spacing = 0.6
    rafter_setback = -0.05  # Negative setback to extend rafters beyond the wall edges
    rafter_tail_cutback = 0.14
    rafter_tail_cut_raise = 0.045
    rafter_tail_cut_height = 1.0
    rafter_plumb_cut_half_span = 0.6
    rafter_plumb_cut_height = max(2.0, (ridge_height - eave_edge_z) + 2.0)
    rafter_plumb_cut_center_z = (ridge_height + eave_edge_z) / 2

    fascia_depth = 0.025
    fascia_height = 0.18
    fascia_z = eave_edge_z - fascia_height / 2 - 0.01

    north_fascia_y = oy + (WIDTH / 2) + overhang + 0.002
    south_fascia_y = oy - (WIDTH / 2) - overhang - 0.002
    fascia_half_length = (LENGTH / 2) + overhang - 0.04
    north_fascia_inner_y = north_fascia_y - (fascia_depth / 2)
    south_fascia_inner_y = south_fascia_y + (fascia_depth / 2)
    north_eave_y = oy + (WIDTH / 2) + overhang
    south_eave_y = oy - (WIDTH / 2) - overhang
    base_rafter_run = ((WIDTH / 2) + overhang) / math.cos(pitch_rad) - 0.17

    rafter_count = max(2, int((LENGTH - 2 * rafter_setback) / rafter_spacing) + 1)
    start_x = ox - (LENGTH / 2) + rafter_setback
    end_x = ox + (LENGTH / 2) - rafter_setback
    actual_spacing = (end_x - start_x) / (rafter_count - 1)

    rafter_north_center_y = (oy + north_eave_y) / 2
    rafter_south_center_y = (oy + south_eave_y) / 2
    rafter_center_z = ((ridge_height + eave_edge_z) / 2) - (rafter_depth / 2) - 0.02
    rafter_extra_run = 0.10
    tip_y_from_depth = (rafter_depth / 2) * math.sin(pitch_rad)
    cos_pitch = max(0.001, math.cos(pitch_rad))
    min_north_run = 2 * (north_fascia_inner_y - rafter_north_center_y - tip_y_from_depth + 0.01) / cos_pitch
    min_south_run = 2 * (rafter_south_center_y - south_fascia_inner_y - tip_y_from_depth + 0.01) / cos_pitch
    rafter_run = max(base_rafter_run, min_north_run, min_south_run) + rafter_extra_run

    for i in range(rafter_count):
        rafter_x = start_x + (i * actual_spacing)

        bpy.ops.mesh.primitive_cube_add(location=(rafter_x, rafter_north_center_y, rafter_center_z))
        north_rafter = bpy.context.active_object
        north_rafter.name = f"MainDwelling_Rafter_North_{i + 1:02d}"
        north_rafter.scale = (rafter_width / 2, rafter_run / 2, rafter_depth / 2)
        north_rafter.rotation_euler[0] = -pitch_rad
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        north_rafter.data.materials.append(framing_mat)
        bpy.ops.mesh.primitive_cube_add(
            location=(
                rafter_x,
                north_fascia_inner_y + rafter_plumb_cut_half_span,
                rafter_plumb_cut_center_z,
            )
        )
        north_plumb_cut = bpy.context.active_object
        north_plumb_cut.scale = (
            (rafter_width / 2) + 0.08,
            rafter_plumb_cut_half_span,
            rafter_plumb_cut_height / 2,
        )
        bpy.ops.object.transform_apply(scale=True)
        bool_mod = north_rafter.modifiers.new(name="OuterPlumbCut", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.solver = 'EXACT'
        bool_mod.object = north_plumb_cut
        bpy.context.view_layer.objects.active = north_rafter
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        bpy.data.objects.remove(north_plumb_cut, do_unlink=True)

        north_tip_y = north_rafter.location.y + max(corner[1] for corner in north_rafter.bound_box)
        north_bottom_z = north_rafter.location.z + min(corner[2] for corner in north_rafter.bound_box)
        north_cut_top_z = north_bottom_z + rafter_tail_cut_raise
        bpy.ops.mesh.primitive_cube_add(
            location=(
                rafter_x,
                north_tip_y - (rafter_tail_cutback / 2),
                north_cut_top_z - (rafter_tail_cut_height / 2),
            )
        )
        north_cut = bpy.context.active_object
        north_cut.scale = (
            (rafter_width / 2) + 0.01,
            (rafter_tail_cutback / 2) + 0.01,
            rafter_tail_cut_height / 2,
        )
        bpy.ops.object.transform_apply(scale=True)
        bool_mod = north_rafter.modifiers.new(name="OuterTailCut", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.solver = 'EXACT'
        bool_mod.object = north_cut
        bpy.context.view_layer.objects.active = north_rafter
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        bpy.data.objects.remove(north_cut, do_unlink=True)

        bpy.ops.mesh.primitive_cube_add(location=(rafter_x, rafter_south_center_y, rafter_center_z))
        south_rafter = bpy.context.active_object
        south_rafter.name = f"MainDwelling_Rafter_South_{i + 1:02d}"
        south_rafter.scale = (rafter_width / 2, rafter_run / 2, rafter_depth / 2)
        south_rafter.rotation_euler[0] = pitch_rad
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        south_rafter.data.materials.append(framing_mat)
        bpy.ops.mesh.primitive_cube_add(
            location=(
                rafter_x,
                south_fascia_inner_y - rafter_plumb_cut_half_span,
                rafter_plumb_cut_center_z,
            )
        )
        south_plumb_cut = bpy.context.active_object
        south_plumb_cut.scale = (
            (rafter_width / 2) + 0.08,
            rafter_plumb_cut_half_span,
            rafter_plumb_cut_height / 2,
        )
        bpy.ops.object.transform_apply(scale=True)
        bool_mod = south_rafter.modifiers.new(name="OuterPlumbCut", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.solver = 'EXACT'
        bool_mod.object = south_plumb_cut
        bpy.context.view_layer.objects.active = south_rafter
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        bpy.data.objects.remove(south_plumb_cut, do_unlink=True)

        south_tip_y = south_rafter.location.y + min(corner[1] for corner in south_rafter.bound_box)
        south_bottom_z = south_rafter.location.z + min(corner[2] for corner in south_rafter.bound_box)
        south_cut_top_z = south_bottom_z + rafter_tail_cut_raise
        bpy.ops.mesh.primitive_cube_add(
            location=(
                rafter_x,
                south_tip_y + (rafter_tail_cutback / 2),
                south_cut_top_z - (rafter_tail_cut_height / 2),
            )
        )
        south_cut = bpy.context.active_object
        south_cut.scale = (
            (rafter_width / 2) + 0.01,
            (rafter_tail_cutback / 2) + 0.01,
            rafter_tail_cut_height / 2,
        )
        bpy.ops.object.transform_apply(scale=True)
        bool_mod = south_rafter.modifiers.new(name="OuterTailCut", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.solver = 'EXACT'
        bool_mod.object = south_cut
        bpy.context.view_layer.objects.active = south_rafter
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        bpy.data.objects.remove(south_cut, do_unlink=True)

    bpy.ops.mesh.primitive_cube_add(location=(ox, north_fascia_y, fascia_z))
    north_fascia = bpy.context.active_object
    north_fascia.name = "MainDwelling_Fascia_North"
    north_fascia.scale = (fascia_half_length, fascia_depth / 2, fascia_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    north_fascia.data.materials.append(fascia_mat)

    bpy.ops.mesh.primitive_cube_add(location=(ox, south_fascia_y, fascia_z))
    south_fascia = bpy.context.active_object
    south_fascia.name = "MainDwelling_Fascia_South"
    south_fascia.scale = (fascia_half_length, fascia_depth / 2, fascia_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    south_fascia.data.materials.append(fascia_mat)


def _add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, option=1):
    """Add all windows and doors to exterior walls."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    window_z_first = first_floor_z + 1.2

    north_wall_ground_y = oy + WIDTH / 2 - NORTH_RECESS - EXTERIOR_WALL_THICKNESS / 2 + 0.01
    north_wall_first_y = north_wall_ground_y
    if option == 5:
        north_wall_first_y = oy + WIDTH / 2 - EXTERIOR_WALL_THICKNESS / 2 + 0.01
    ground_north_wall_outer_face = north_wall_ground_y + EXTERIOR_WALL_THICKNESS / 2
    first_north_wall_outer_face = north_wall_first_y + EXTERIOR_WALL_THICKNESS / 2
    south_wall_y = oy - WIDTH / 2

    if option == 1 or option == 2:
        add_window("MD_GF_NorthWall", (ox - 2.9, ground_north_wall_outer_face, oz+1.0), width=1.5, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_GF_NorthWall", (ox + 2.9, ground_north_wall_outer_face, oz+1.0), width=1.5, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_GF_NorthWall", (ox - 1.1, ground_north_wall_outer_face, oz+1.5), width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_FF_NorthWall", (ox - LENGTH / 4 + 0.2, first_north_wall_outer_face, window_z_first+0.05), width=2.7, height=2.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_FF_NorthWall", (ox + LENGTH / 4 + 0.4, first_north_wall_outer_face, window_z_first+0.55), width=1.8, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    if option == 3 or option == 4:
        #add_window("MD_GF_NorthWall", (ox - 3.05, ground_north_wall_outer_face, oz+1.55), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        #add_window("MD_GF_NorthWall", (ox - 0.5, ground_north_wall_outer_face, oz+1.1), width=1.5, height=2.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_GF_NorthWall", (ox - 1.9, ground_north_wall_outer_face, oz+1.1), width=2.7, height=2.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_GF_NorthWall", (ox + 2.95, ground_north_wall_outer_face, oz+1.55), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        #add_window("MD_FF_NorthWall", (ox -3.05, first_north_wall_outer_face, window_z_first+0.55), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        #add_window("MD_FF_NorthWall", (ox - 0.5, first_north_wall_outer_face, window_z_first+0.1), width=1.5, height=2.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_FF_NorthWall", (ox - 1.9, first_north_wall_outer_face, window_z_first+0.1), width=2.7, height=2.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_FF_NorthWall", (ox + 2.95, first_north_wall_outer_face, window_z_first+0.55), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    if option == 5:
        add_window("MD_GF_NorthWall", (ox - 1.9, ground_north_wall_outer_face, oz+1.1), width=2.7, height=2.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_GF_NorthWall", (ox + 2.95, ground_north_wall_outer_face, oz+1.55), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_FF_NorthWall", (ox - 1.9, first_north_wall_outer_face, window_z_first+0.55), width=2.7, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_FF_NorthWall", (ox + 2.95, first_north_wall_outer_face, window_z_first+0.55), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_FF_EastWall", (ox + LENGTH / 2, oy + 2.6, window_z_first + 0.4), width=0.6, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
        add_window("MD_FF_EastWall", (ox + LENGTH / 2, oy, window_z_first + 0.4), width=0.6, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
        add_window("MD_FF_EastWall", (ox + LENGTH / 2, oy - 2.6, window_z_first + 0.4), width=0.6, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')


    #add_window("MD_GF_EastWall", (ox + LENGTH / 2, oy + 0.8, oz + 1.65), width=1.2, height=0.7, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MD_GF_EastWall", (ox + LENGTH / 2, oy - 2.4, oz + 1.7), width=1.2, height=0.6, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')

    if option != 5:
        #add_window("MD_FF_EastWall", (ox + LENGTH / 2, oy + 0.8, window_z_first + 0.5), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
        add_window("MD_FF_EastWall", (ox + LENGTH / 2, oy + 2.0, window_z_first + 0.4), width=0.6, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
        add_window("MD_FF_EastWall", (ox + LENGTH / 2, oy - 0.6, window_z_first + 0.4), width=0.6, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
        #add_window("MD_FF_EastWall", (ox + LENGTH / 2, oy - 2.8, window_z_first + 0.6), width=0.6, height=0.8, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')

    #add_window("MD_FF_WestWall", (ox - LENGTH / 2, oy, window_z_first + 0.6), width=1.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    add_window("MD_FF_WestWall", (ox - LENGTH / 2, oy, window_z_first + 0.7), width=0.9, height=1.5, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')

    if option == 1:
        #south wall windows - option 1
        add_window("MD_GF_SouthWall", (ox + 1.5, south_wall_y, oz + 1.0), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_GF_SouthWall", (ox - 0.7, south_wall_y, oz + 1.5), width=1.8, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_GF_SouthWall", (ox - 3.3, south_wall_y, oz + 2.15), width=1.2, height=0.7, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

        add_window("MD_FF_SouthWall", (ox + 3.2, south_wall_y, first_floor_z + 1.5), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox + 1.0, south_wall_y, first_floor_z + 1.5), width=0.6, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox - 0.8, south_wall_y, first_floor_z + 1.4), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox - 3.3, south_wall_y, first_floor_z + 1.0), width=1.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

        add_window("MD_GF_WestWall", (ox - LENGTH / 2, oy + 1.7, oz + 1.45), width=0.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')

    if option == 2:
        #south wall windows - option 2
        add_window("MD_GF_SouthWall", (ox - 0.8, south_wall_y, oz + 1.0), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_GF_SouthWall", (ox - 2.8, south_wall_y, oz + 1.5), width=1.6, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_GF_SouthWall", (ox + 1.5, south_wall_y, oz + 2.15), width=1.2, height=0.7, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

        add_window("MD_FF_SouthWall", (ox + 3.2, south_wall_y, first_floor_z + 1.5), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox - 2.8, south_wall_y, first_floor_z + 1.4), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox + 1.5, south_wall_y, first_floor_z + 1.0), width=1.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

        add_window("MD_GF_WestWall", (ox - LENGTH / 2, oy + 1.7, oz + 1.45), width=0.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')

    if option == 3:
        #south wall windows - option 3
        add_window("MD_GF_SouthWall", (ox + 1.4, south_wall_y, oz + 1.0), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_GF_SouthWall", (ox - 2.8, south_wall_y, oz + 1.5), width=1.6, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

        add_window("MD_FF_SouthWall", (ox + 3.2, south_wall_y, window_z_first + 0.5), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox - 0.0, south_wall_y, window_z_first + 0.4), width=1.8, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox - 2.8, south_wall_y, window_z_first + 0.4), width=1.8, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

        add_window("MD_GF_WestWall", (ox - LENGTH / 2, oy + 1.2, oz + 1.45), width=0.9, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')

    if option == 4 or option == 5:
        #south wall windows - option 4/5
        #add_door("MD_GF_SouthWall", (ox - 0.7, south_wall_y, oz+0.1), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_opening("MD_GF_SouthWall", (ox - 0.6, south_wall_y, oz+1.0), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_GF_SouthWall", (ox - 3.15, south_wall_y, oz + 1.5), width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

        #add_window("MD_FF_SouthWall", (ox + 3.2, south_wall_y, window_z_first + 0.5), width=0.7, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox - 0.6, south_wall_y, window_z_first + 0.5), width=1.2, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox - 3.15, south_wall_y, window_z_first + 0.5), width=1.2, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox + 1.95, south_wall_y, window_z_first + 0.5), width=1.2, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox + 4.15, south_wall_y, window_z_first + 0.7), width=0.6, height=0.8, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

        add_window("MD_GF_WestWall", (ox - LENGTH / 2, oy, oz + 1.55), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')


def _add_gable_windows(ox, oy, oz, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, option=1):
    """Add windows to gable exterior walls after roof/gables are created."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    west_x = ox - LENGTH / 2
    east_x = ox + LENGTH / 2

    def _add_west_upper_window_fin(
        window_center_y,
        window_center_z,
        window_width,
        window_height,
        fin_depth=0.275,
        fin_thickness=0.045,
        edge_gap=0.06,
    ):
        """Create a vertical external fin just north of the upper west window."""
        fin_height = window_height + 0.2
        fin_center_y = window_center_y + (window_width / 2) + edge_gap + (fin_thickness / 2)
        fin_center_x = west_x - (fin_depth / 2)
        fin_center_z = window_center_z + 0.1

        bpy.ops.mesh.primitive_cube_add(location=(fin_center_x, fin_center_y, fin_center_z))
        fin = bpy.context.active_object
        fin.name = "MD_FF_WestUpperWindow_Fin"
        fin.scale = (fin_depth / 2, fin_thickness / 2, fin_height / 2)
        bpy.ops.object.transform_apply(scale=True)

        # Match the exterior cladding material from the west gable wall.
        west_gable = bpy.data.objects.get("MD_FF_WestGableWall")
        if west_gable and west_gable.data and len(west_gable.data.materials) > 0:
            fin_mat = west_gable.data.materials[0]
        else:
            fin_mat = create_material("WindowFinPaint", (0.93, 0.93, 0.93, 1.0))
        fin.data.materials.append(fin_mat)

    # West gable window (existing default behavior)
    #add_window( "MD_FF_WestGableWall", (west_x, oy, first_floor_z + 3.8), width=1.8, height=0.7, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X', )
    west_window_center_y = oy
    west_window_center_z = first_floor_z + 3.1
    west_window_width = 0.9
    west_window_height = 1.1
    add_window( "MD_FF_WestGableWall",
        (west_x, west_window_center_y, west_window_center_z),
        width=west_window_width, height=west_window_height,
        depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X', )
    
    #_add_west_upper_window_fin( west_window_center_y, west_window_center_z - 0.7, west_window_width, west_window_height + 1.4, )

    # Optional east gable window variant used in option 4/5.
    if option == 4 or option == 5:
        #add_window( "MD_FF_EastGableWall", (east_x, oy, first_floor_z + 3.8), width=1.8, height=0.7, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X', )
        add_window( "MD_FF_EastGableWall", (east_x, oy, first_floor_z + 3.8), width=0.6, height=0.8, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X', )


def _create_gable_roof(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, EXTERIOR_WALL_THICKNESS, roof_style, potius_mat):
    """Create the main gable roof with traditional, flush, or 150mm gable styles.

    roof_style values:
        - "traditional": default gable roof with standard north/south overhang
        - "flush": roof plane runs flush with the main wall faces
        - "gable_150mm": gable roof with a 150mm overhang on all four sides

    Args:
        potius_mat: Exterior cladding material for gable ends
    """
    roof_height_from_eaves = (WIDTH / 2) * math.tan(math.radians(ROOF_PITCH))
    eave_height = oz + TOTAL_HEIGHT
    ridge_height = eave_height + roof_height_from_eaves
    pitch_tan = math.tan(math.radians(ROOF_PITCH))

    roof_mat = get_metal_roof_material()
    interior_wall_mat = create_material("InteriorWallPaint", (0.96, 0.94, 0.90, 1.0))

    def _create_gable_wall(side_name, x_outer, x_inner):
        object_name = f"MD_FF_{side_name}GableWall"
        verts = [
            (x_outer, oy - WIDTH / 2, eave_height),
            (x_outer, oy + WIDTH / 2, eave_height),
            (x_outer, oy, ridge_height),
            (x_inner, oy - WIDTH / 2, eave_height),
            (x_inner, oy + WIDTH / 2, eave_height),
            (x_inner, oy, ridge_height),
        ]

        faces = [
            (0, 1, 2),      # outer triangular face
            (3, 5, 4),      # inner triangular face
            (0, 3, 4, 1),   # north sloped side
            (1, 4, 5, 2),   # ridge side
            (2, 5, 3, 0),   # south sloped side
        ]

        gable_mesh = bpy.data.meshes.new(f"{object_name}Mesh")
        gable_mesh.from_pydata(verts, [], faces)
        gable_mesh.update()

        gable = bpy.data.objects.new(object_name, gable_mesh)
        bpy.context.collection.objects.link(gable)
        gable.data.materials.append(potius_mat)
        gable.data.materials.append(interior_wall_mat)

        interior_target_x = x_inner
        interior_face = None
        best_delta = None
        for poly in gable_mesh.polygons:
            center_x = sum(gable_mesh.vertices[idx].co.x for idx in poly.vertices) / len(poly.vertices)
            delta = abs(center_x - interior_target_x)
            if interior_face is None or delta < best_delta:
                interior_face = poly
                best_delta = delta

        if interior_face is not None:
            interior_face.material_index = 1

        if not gable_mesh.uv_layers:
            gable_mesh.uv_layers.new(name="UVMap")
        uv_layer = gable_mesh.uv_layers.active.data

        for poly in gable_mesh.polygons:
            for loop_idx in poly.loop_indices:
                loop = gable_mesh.loops[loop_idx]
                vert = gable_mesh.vertices[loop.vertex_index]
                u = (vert.co.y - (oy - WIDTH / 2)) / 2.0
                v = (vert.co.z - eave_height) / 2.0
                uv_layer[loop_idx].uv = (u, v)

    if roof_style == "flush":
        mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
        obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
        bpy.context.collection.objects.link(obj)

        east_edge = ox + LENGTH / 2
        west_edge = ox - LENGTH / 2
        # Roof spans full 7m WIDTH, flush with building edges
        north_eave_y = oy + WIDTH / 2
        south_eave_y = oy - WIDTH / 2

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
        ]

        mesh.from_pydata(verts, [], faces)
        mesh.update()

        obj.data.materials.append(roof_mat)

        _add_gable_roof_framing(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, overhang=0.0)

        # Create UV layer and set UVs for gable faces
        if not mesh.uv_layers:
            mesh.uv_layers.new(name="UVMap")

        uv_layer = mesh.uv_layers.active.data
        for poly_idx, poly in enumerate(mesh.polygons):
            for loop_idx in poly.loop_indices:
                loop = mesh.loops[loop_idx]
                vert = mesh.vertices[loop.vertex_index]
                u = (vert.co.x - (ox - LENGTH / 2)) / 2.0
                v = (vert.co.y - (oy - WIDTH / 2)) / 2.0
                uv_layer[loop_idx].uv = (u, v)

        # UV unwrap roof faces only
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)

        # Flush gable walls sit directly at the main east/west wall outer faces.
        west_x_outer = ox - LENGTH / 2
        west_x_inner = west_x_outer + EXTERIOR_WALL_THICKNESS
        east_x_outer = ox + LENGTH / 2
        east_x_inner = east_x_outer - EXTERIOR_WALL_THICKNESS

        _create_gable_wall("West", west_x_outer, west_x_inner)
        _create_gable_wall("East", east_x_outer, east_x_inner)
    elif roof_style == "gable_150mm":
        mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
        obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
        bpy.context.collection.objects.link(obj)

        overhang = 0.15
        eave_z = eave_height - (overhang * pitch_tan)
        half_length = (LENGTH + 2 * overhang) / 2
        north_eave_y = oy + WIDTH / 2 + overhang
        south_eave_y = oy - WIDTH / 2 - overhang

        verts = [
            (ox - half_length, north_eave_y, eave_z),
            (ox + half_length, north_eave_y, eave_z),
            (ox - half_length, oy, ridge_height),
            (ox + half_length, oy, ridge_height),
            (ox - half_length, south_eave_y, eave_z),
            (ox + half_length, south_eave_y, eave_z),
        ]

        faces = [
            (0, 1, 3, 2),
            (2, 3, 5, 4),
        ]

        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(roof_mat)
        _add_gable_roof_framing(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, overhang=0.15)

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)

        west_x_outer = ox - LENGTH / 2
        west_x_inner = west_x_outer + EXTERIOR_WALL_THICKNESS
        east_x_outer = ox + LENGTH / 2
        east_x_inner = east_x_outer - EXTERIOR_WALL_THICKNESS

        _create_gable_wall("West", west_x_outer, west_x_inner)
        _create_gable_wall("East", east_x_outer, east_x_inner)
    else:  # traditional
        mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
        obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
        bpy.context.collection.objects.link(obj)

        eave_z = eave_height - (ROOF_OVERHANG * pitch_tan)
        half_length = (LENGTH + 2 * ROOF_OVERHANG) / 2
        north_eave_y = oy + WIDTH / 2 + ROOF_OVERHANG
        south_eave_y = oy - WIDTH / 2 - ROOF_OVERHANG

        verts = [
            (ox - half_length, north_eave_y, eave_z),
            (ox + half_length, north_eave_y, eave_z),
            (ox - half_length, oy, ridge_height),
            (ox + half_length, oy, ridge_height),
            (ox - half_length, south_eave_y, eave_z),
            (ox + half_length, south_eave_y, eave_z),
        ]

        faces = [
            (0, 1, 3, 2),
            (2, 3, 5, 4),
        ]

        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(roof_mat)
        _add_gable_roof_framing(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, overhang=ROOF_OVERHANG)

        # UV unwrap for texture display
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)

        west_x_outer = ox - LENGTH / 2
        west_x_inner = west_x_outer + EXTERIOR_WALL_THICKNESS
        east_x_outer = ox + LENGTH / 2
        east_x_inner = east_x_outer - EXTERIOR_WALL_THICKNESS

        _create_gable_wall("West", west_x_outer, west_x_inner)
        _create_gable_wall("East", east_x_outer, east_x_inner)
