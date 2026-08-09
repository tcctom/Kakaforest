import bpy  # type: ignore
import math

from materials import get_metal_roof_material
from main_dwelling.materials_nodes import create_material
from utils import add_window, add_door


def _add_flush_roof_framing(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH):
    """Add a ridge beam and paired rafters under the flush gable roof."""
    ridge_height = oz + TOTAL_HEIGHT + (WIDTH / 2) * math.tan(math.radians(ROOF_PITCH))
    pitch_rad = math.radians(ROOF_PITCH)

    framing_mat = create_material("RoofFramingTimber", (0.55, 0.40, 0.25, 1.0))

    ridge_beam_height = 0.18
    ridge_beam_width = 0.10
    ridge_beam_z = ridge_height - ridge_beam_height / 2 - 0.03

    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, ridge_beam_z))
    ridge_beam = bpy.context.active_object
    ridge_beam.name = "MainDwelling_RidgeBeam"
    ridge_beam.scale = (LENGTH / 2, ridge_beam_width / 2, ridge_beam_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    ridge_beam.data.materials.append(framing_mat)

    rafter_width = 0.06
    rafter_depth = 0.14
    rafter_spacing = 0.65
    rafter_setback = 0.12

    north_eave_y = oy + WIDTH / 2
    south_eave_y = oy - WIDTH / 2
    rafter_run = (WIDTH / 2) / math.cos(pitch_rad)

    rafter_count = max(2, int((LENGTH - 2 * rafter_setback) / rafter_spacing) + 1)
    start_x = ox - (LENGTH / 2) + rafter_setback
    end_x = ox + (LENGTH / 2) - rafter_setback
    actual_spacing = (end_x - start_x) / (rafter_count - 1)

    rafter_north_center_y = (oy + north_eave_y) / 2
    rafter_south_center_y = (oy + south_eave_y) / 2
    rafter_center_z = ridge_height - ((WIDTH / 4) * math.tan(pitch_rad)) - (rafter_depth / 2) - 0.02

    for i in range(rafter_count):
        rafter_x = start_x + (i * actual_spacing)

        bpy.ops.mesh.primitive_cube_add(location=(rafter_x, rafter_north_center_y, rafter_center_z))
        north_rafter = bpy.context.active_object
        north_rafter.name = f"MainDwelling_Rafter_North_{i + 1:02d}"
        north_rafter.scale = (rafter_width / 2, rafter_run / 2, rafter_depth / 2)
        north_rafter.rotation_euler[0] = -pitch_rad
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        north_rafter.data.materials.append(framing_mat)

        bpy.ops.mesh.primitive_cube_add(location=(rafter_x, rafter_south_center_y, rafter_center_z))
        south_rafter = bpy.context.active_object
        south_rafter.name = f"MainDwelling_Rafter_South_{i + 1:02d}"
        south_rafter.scale = (rafter_width / 2, rafter_run / 2, rafter_depth / 2)
        south_rafter.rotation_euler[0] = pitch_rad
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        south_rafter.data.materials.append(framing_mat)


def _add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, option=1):
    """Add all windows and doors to exterior walls."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    window_z_first = first_floor_z + 1.2

    north_wall_y = oy + WIDTH / 2 - NORTH_RECESS - EXTERIOR_WALL_THICKNESS / 2 + 0.01
    north_wall_outer_face = north_wall_y + EXTERIOR_WALL_THICKNESS / 2
    south_wall_y = oy - WIDTH / 2

    if option == 1 or option == 2:
        add_window("MD_GF_NorthWall", (ox - 2.9, north_wall_outer_face, oz+1.0), width=1.5, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_GF_NorthWall", (ox + 2.9, north_wall_outer_face, oz+1.0), width=1.5, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_GF_NorthWall", (ox - 1.1, north_wall_outer_face, oz+1.5), width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    if option == 3 or option == 4:
        add_window("MD_GF_NorthWall", (ox - LENGTH / 4, north_wall_outer_face, oz+1.1), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        add_window("MD_GF_NorthWall", (ox + LENGTH / 4, north_wall_outer_face, oz+1.5), width=1.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
        

    add_window("MD_FF_NorthWall", (ox - LENGTH / 4, north_wall_outer_face, window_z_first), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MD_FF_NorthWall", (ox + LENGTH / 4, north_wall_outer_face, window_z_first+0.5), width=1.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')

    add_window("MD_GF_EastWall", (ox + LENGTH / 2, oy + 1.0, oz + 1.65), width=1.5, height=0.7, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MD_GF_EastWall", (ox + LENGTH / 2, oy - 2.6, oz + 1.65), width=0.9, height=0.7, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')

    add_window("MD_FF_EastWall", (ox + LENGTH / 2, oy + 1.0, window_z_first + 0.5), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MD_FF_EastWall", (ox + LENGTH / 2, oy - 2.6, window_z_first + 0.5), width=0.7, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')

    add_window("MD_FF_WestWall", (ox - LENGTH / 2, oy, window_z_first + 0.45), width=1.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')

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

    if option == 4:
        #south wall windows - option 4
        add_door("MD_GF_SouthWall", (ox - 0.8, south_wall_y, oz+0.1), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_GF_SouthWall", (ox - 2.8, south_wall_y, oz + 1.5), width=1.6, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

        add_window("MD_FF_SouthWall", (ox + 3.2, south_wall_y, window_z_first + 0.5), width=0.7, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox - 0.0, south_wall_y, window_z_first + 0.4), width=1.8, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
        add_window("MD_FF_SouthWall", (ox - 2.8, south_wall_y, window_z_first + 0.4), width=1.8, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

        add_window("MD_GF_WestWall", (ox - LENGTH / 2, oy + 1.2, oz + 1.45), width=0.9, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')


def _add_west_gable_window(ox, oy, oz, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, roof_style):
    """Add a small window on the west gable after the roof has been created."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    west_x = ox - LENGTH / 2
    window_z = first_floor_z + 3.45
    inset_depth = EXTERIOR_WALL_THICKNESS * 0.35

    if roof_style == "traditional":
        # Historical side naming in gable creation can be swapped.
        # Pick whichever gable object is physically closest to the west side.
        gable_candidates = []
        for name in ("MainDwelling_Gable_West", "MainDwelling_Gable_East"):
            obj = bpy.data.objects.get(name)
            if obj:
                gable_candidates.append(obj)

        if not gable_candidates:
            print("West gable window skipped: no gable objects were found")
            return

        def _world_x_center(obj):
            if getattr(obj.data, "vertices", None):
                xs = [(obj.matrix_world @ v.co).x for v in obj.data.vertices]
                return sum(xs) / len(xs)
            return obj.location.x

        target = min(gable_candidates, key=lambda obj: abs(_world_x_center(obj) - west_x))
        target_x = _world_x_center(target)

        # Gable faces are single-surface meshes (no thickness), so offset outward
        # so the frame and glass are visible from the exterior.
        inward_offset = '-X' if target_x <= ox else '+X'

        window_parts = add_window(
            target.name,
            (target_x, oy, window_z),
            width=0.6,
            height=0.6,
            depth=EXTERIOR_WALL_THICKNESS,
            axis='X',
            inward_offset=inward_offset,
        )

        if window_parts:
            frame, glass = window_parts
            interior_sign = 1.0 if target_x <= ox else -1.0
            frame.location.x += interior_sign * inset_depth
            glass.location.x += interior_sign * inset_depth
        return

    # Flush roof has integrated gable faces in MainDwelling_Roof.
    roof_obj = bpy.data.objects.get("MainDwelling_Roof")
    if not roof_obj:
        print("West gable window skipped: MainDwelling_Roof not found")
        return

    window_parts = add_window(
        "MainDwelling_Roof",
        (west_x, oy, window_z),
        width=0.6,
        height=0.6,
        depth=EXTERIOR_WALL_THICKNESS,
        axis='X',
        inward_offset='+X',
    )

    if window_parts:
        frame, glass = window_parts
        frame.location.x += inset_depth
        glass.location.x += inset_depth


def _create_gable_roof(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, roof_style, potius_mat):
    """Create the main gable roof with either traditional or flush style.

    Args:
        potius_mat: Exterior cladding material for gable ends
    """
    roof_height_from_eaves = (WIDTH / 2) * math.tan(math.radians(ROOF_PITCH))
    eave_height = oz + TOTAL_HEIGHT
    ridge_height = eave_height + roof_height_from_eaves

    roof_mat = get_metal_roof_material()
    # Use the same exterior cladding material for gable ends
    gable_material = potius_mat

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
            (0, 2, 4),  # East gable triangle
            (1, 5, 3),  # West gable triangle
        ]

        mesh.from_pydata(verts, [], faces)
        mesh.update()

        obj.data.materials.append(roof_mat)
        obj.data.materials.append(gable_material)

        _add_flush_roof_framing(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH)

        for i, face in enumerate(mesh.polygons):
            if i < 2:
                face.material_index = 0
            else:
                face.material_index = 1

        # Create UV layer and set UVs for gable faces
        if not mesh.uv_layers:
            mesh.uv_layers.new(name="UVMap")

        uv_layer = mesh.uv_layers.active.data
        for poly_idx, poly in enumerate(mesh.polygons):
            if poly_idx >= 2:  # Gable faces
                for loop_idx in poly.loop_indices:
                    loop = mesh.loops[loop_idx]
                    vert = mesh.vertices[loop.vertex_index]
                    # Scale UVs: world_dimension / 2.0 to match wall UV scale
                    # This gives ~150mm grooves after material's 13.33x scaling
                    u = (vert.co.y - (oy + WIDTH / 2)) / 2.0
                    v = (vert.co.z - eave_height) / 2.0
                    uv_layer[loop_idx].uv = (u, v)

        # UV unwrap roof faces only
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        for i in range(2):
            mesh.polygons[i].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)
    else:  # traditional
        mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
        obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
        bpy.context.collection.objects.link(obj)

        half_length = (LENGTH + 2 * ROOF_OVERHANG) / 2
        north_eave_y = oy + WIDTH / 2 + ROOF_OVERHANG
        south_eave_y = oy - WIDTH / 2 - ROOF_OVERHANG

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

        # UV unwrap for texture display
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)

        # Create separate gable end triangles
        for side, x_pos in [("East", ox - LENGTH / 2), ("West", ox + LENGTH / 2)]:
            verts = [
                (x_pos, oy - WIDTH / 2, eave_height),
                (x_pos, oy + WIDTH / 2, eave_height),
                (x_pos, oy, ridge_height),
            ]
            edges = []
            faces = [(0, 1, 2)]

            gable_mesh = bpy.data.meshes.new(f"MainDwelling_Gable_{side}")
            gable_mesh.from_pydata(verts, edges, faces)
            gable_mesh.update()

            gable = bpy.data.objects.new(f"MainDwelling_Gable_{side}", gable_mesh)
            bpy.context.collection.objects.link(gable)
            gable.data.materials.append(gable_material)

            # Create UV layer with normalized coordinates (0-1 range)
            if not gable_mesh.uv_layers:
                gable_mesh.uv_layers.new(name="UVMap")
            uv_layer = gable_mesh.uv_layers.active.data

            # Calculate gable dimensions
            gable_width = WIDTH
            gable_height = roof_height_from_eaves

            for poly in gable_mesh.polygons:
                for loop_idx in poly.loop_indices:
                    loop = gable_mesh.loops[loop_idx]
                    vert = gable_mesh.vertices[loop.vertex_index]
                    # Scale UVs so that 150mm (0.15m) = 1 texture repeat BEFORE material scaling
                    # We want: actual_dimension / 0.15m texture repeats
                    # Then material's 13.33x brings it to correct scale
                    # So: UV = world_dimension / (0.15m * 13.33) = world_dimension / 2.0
                    u = (vert.co.y - (oy - WIDTH / 2)) / 2.0  # 7m span / 2.0 = 3.5 UV units
                    v = (vert.co.z - eave_height) / 2.0
                    uv_layer[loop_idx].uv = (u, v)
                    print(f"  Gable face {poly}, vert: Y={vert.co.y:.2f}, Z={vert.co.z:.2f} -> UV=({u:.4f}, {v:.4f})")

            print("=== END GABLE UV DEBUG ===\\n")

            print(f"DEBUG: Created gable {side} with material {gable_material.name}")
