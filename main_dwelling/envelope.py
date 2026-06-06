import bpy  # type: ignore
import math

from materials import get_metal_roof_material
from utils import add_window


def _add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Add all windows and doors to exterior walls."""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    window_z_ground = oz + 1.0
    window_z_first = first_floor_z + 1.0
    spacing = LENGTH / 4

    north_wall_y = oy + WIDTH / 2 - NORTH_RECESS + EXTERIOR_WALL_THICKNESS / 2
    north_wall_outer_face = north_wall_y + EXTERIOR_WALL_THICKNESS / 2
    south_wall_y = oy - WIDTH / 2

    east_west_window_spacing = WIDTH / 3
    south_spacing = LENGTH / 4

    add_window("MainDwelling_NorthWall_Ground", (ox - spacing, north_wall_outer_face, window_z_ground), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_NorthWall_Ground", (ox + spacing, north_wall_outer_face, window_z_ground), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')

    add_window("MainDwelling_NorthWall_First", (ox - spacing, north_wall_outer_face, window_z_first), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_NorthWall_First", (ox + spacing, north_wall_outer_face, window_z_first), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')

    add_window("MainDwelling_EastWall_Ground", (ox + LENGTH / 2, oy + 1.5, oz + 1.5), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MainDwelling_EastWall_Ground", (ox + LENGTH / 2, oy - 2, oz + 1.5), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')

    add_window("MainDwelling_EastWall_First", (ox + LENGTH / 2, oy + 1.5, first_floor_z + 1.5), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MainDwelling_EastWall_First", (ox + LENGTH / 2, oy - 2, first_floor_z + 1.5), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')

    add_window("MainDwelling_WestWall_Ground", (ox - LENGTH / 2, oy + 1.7, oz + 1.45), width=0.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')

    add_window("MainDwelling_WestWall_First", (ox - LENGTH / 2, oy, first_floor_z + 1.45), width=1.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')

    add_window("MainDwelling_SouthWall_Ground", (ox + 3, south_wall_y, oz + 1.5), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    add_window("MainDwelling_SouthWall_Ground", (ox + 1.5, south_wall_y, oz + 1.0), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    add_window("MainDwelling_SouthWall_Ground", (ox - 0.7, south_wall_y, oz + 1.45), width=1.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    add_window("MainDwelling_SouthWall_Ground", (ox - 3.3, south_wall_y, oz + 2.15), width=1.2, height=0.7, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

    add_window("MainDwelling_SouthWall_First", (ox + 3.2, south_wall_y, first_floor_z + 1.5), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    add_window("MainDwelling_SouthWall_First", (ox + 1.0, south_wall_y, first_floor_z + 1.5), width=0.6, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    add_window("MainDwelling_SouthWall_First", (ox - 0.8, south_wall_y, first_floor_z + 1.4), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    add_window("MainDwelling_SouthWall_First", (ox - 3.3, south_wall_y, first_floor_z + 0.4), width=1.2, height=2.8, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')

    first_floor_slab = bpy.data.objects.get("MainDwelling_FirstFloor")
    if first_floor_slab:
        interior_face_y = south_wall_y + EXTERIOR_WALL_THICKNESS / 2
        window_slab_opening_depth = 0.4
        cutter_center_y = interior_face_y + window_slab_opening_depth / 2

        bpy.ops.mesh.primitive_cube_add(location=(ox - 3.2, cutter_center_y, first_floor_z + 0.1))
        window_cutter = bpy.context.active_object
        window_cutter.name = "MainDwelling_WindowSlabCutter_StairLanding"
        window_cutter.scale = (1.0 / 2, window_slab_opening_depth / 2, 0.2 / 2)
        bpy.ops.object.transform_apply(scale=True)

        bool_mod = first_floor_slab.modifiers.new(name="StairWindow_Cut", type='BOOLEAN')
        bool_mod.object = window_cutter
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.solver = 'EXACT'

        window_cutter.hide_viewport = True
        window_cutter.hide_render = True


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
