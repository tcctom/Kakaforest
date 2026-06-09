import bpy  # type: ignore
import math

from materials import get_metal_roof_material
from utils import add_window


def build_simple_open_porch(
    ox,
    oy,
    oz,
    LENGTH,
    GROUND_FLOOR_HEIGHT,
    EXTERIOR_WALL_THICKNESS,
    floor_mat,
    create_textured_material,
    deck_texture_path,
):
    """Create the simple west-side entrance porch with deck, steps, door opening, and roof."""
    # Porch dimensions: 2.5m wide x 1.5m deep, OPEN (no walls)
    PORCH_WIDTH = 2.5  # North-south dimension
    PORCH_DEPTH = 1.5  # East-west depth

    # Porch deck - positioned west of west wall, centered
    porch_center_x = ox - LENGTH / 2 - PORCH_DEPTH / 2
    porch_center_y = oy

    bpy.ops.mesh.primitive_cube_add(location=(porch_center_x, porch_center_y, oz + 0.05))
    porch_deck = bpy.context.active_object
    porch_deck.name = "MainDwelling_PorchDeck_Simple"
    porch_deck.scale = (PORCH_DEPTH / 2, PORCH_WIDTH / 2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    porch_deck.data.materials.append(floor_mat)

    # UV unwrap for porch deck texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Steps down from porch deck on west side - using decking material
    STEP_WIDTH = 2.5  # Full porch width (north-south)
    STEP_DEPTH = 0.4  # 400mm deep (east-west)
    STEP_HEIGHT = 0.15  # 150mm rise per step
    NUM_STEPS = 6  # Total number of steps
    deck_mat = create_textured_material("TimberDecking", deck_texture_path)

    for i in range(NUM_STEPS):
        step_x = ox - LENGTH / 2 - PORCH_DEPTH - STEP_DEPTH / 2 - (i * STEP_DEPTH)
        step_z = oz + 0.05 - STEP_HEIGHT * (i + 1)

        bpy.ops.mesh.primitive_cube_add(location=(step_x, porch_center_y, step_z))
        step = bpy.context.active_object
        step.name = f"MainDwelling_PorchStep{i + 1}_Simple"
        step.scale = (STEP_DEPTH / 2, STEP_WIDTH / 2, STEP_HEIGHT / 2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(deck_mat)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')

    # Main entrance door on main building west wall
    main_door_x = ox - LENGTH / 2
    add_window(
        "MainDwelling_WestWall_Ground",
        (main_door_x, oy, oz + 1.0),
        width=0.9,
        height=2.0,
        depth=EXTERIOR_WALL_THICKNESS,
        axis='X',
        inward_offset='+X',
    )

    # Monopitch porch roof - high at building, low at outer edge
    PORCH_ROOF_PITCH = 15
    PORCH_ROOF_OVERHANG = 0.3

    # Define roof boundaries early to calculate the true span
    porch_roof_building = ox - LENGTH / 2
    porch_roof_outer = ox - LENGTH / 2 - PORCH_DEPTH - PORCH_ROOF_OVERHANG
    porch_roof_span = abs(porch_roof_outer - porch_roof_building)

    # Base the vertical drop on the full span to maintain a true 15-degree angle
    porch_roof_high_height = oz + GROUND_FLOOR_HEIGHT
    porch_roof_drop = porch_roof_span * math.tan(math.radians(PORCH_ROOF_PITCH))
    porch_roof_low_height = porch_roof_high_height - porch_roof_drop
    
    # Track the exact dynamic angle in radians for the fascia boards
    actual_roof_pitch_rad = math.radians(PORCH_ROOF_PITCH)

    # Support posts on west edge of porch
    POST_SIZE = 0.15
    POST_INSET = 0.2
    post_x = ox - LENGTH / 2 - PORCH_DEPTH
    post_height = porch_roof_low_height - oz

    post_north_y = oy + PORCH_WIDTH / 2 - POST_INSET
    bpy.ops.mesh.primitive_cube_add(location=(post_x, post_north_y, oz + post_height / 2))
    post_north = bpy.context.active_object
    post_north.name = "MainDwelling_PorchPost_North"
    post_north.scale = (POST_SIZE / 2, POST_SIZE / 2, post_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    post_north.data.materials.append(floor_mat)

    post_south_y = oy - PORCH_WIDTH / 2 + POST_INSET
    bpy.ops.mesh.primitive_cube_add(location=(post_x, post_south_y, oz + post_height / 2))
    post_south = bpy.context.active_object
    post_south.name = "MainDwelling_PorchPost_South"
    post_south.scale = (POST_SIZE / 2, POST_SIZE / 2, post_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    post_south.data.materials.append(floor_mat)

    porch_roof_mesh = bpy.data.meshes.new("MainDwelling_PorchRoof_Monopitch")
    porch_roof_obj = bpy.data.objects.new("MainDwelling_PorchRoof_Simple", porch_roof_mesh)
    bpy.context.collection.objects.link(porch_roof_obj)

    porch_roof_north = oy + PORCH_WIDTH / 2 + PORCH_ROOF_OVERHANG
    porch_roof_south = oy - PORCH_WIDTH / 2 - PORCH_ROOF_OVERHANG

    porch_verts = [
        (porch_roof_building, porch_roof_north, porch_roof_high_height),
        (porch_roof_building, porch_roof_south, porch_roof_high_height),
        (porch_roof_outer, porch_roof_north, porch_roof_low_height),
        (porch_roof_outer, porch_roof_south, porch_roof_low_height),
    ]
    porch_faces = [
        (0, 1, 3, 2),
    ]

    porch_roof_mesh.from_pydata(porch_verts, [], porch_faces)
    porch_roof_mesh.update()
    porch_roof_obj.data.materials.append(get_metal_roof_material())

    bpy.context.view_layer.objects.active = porch_roof_obj
    porch_roof_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    porch_roof_obj.select_set(False)

    # Add roof structure for realism
    FASCIA_HEIGHT = 0.20
    FASCIA_THICKNESS = 0.025
    PURLIN_SIZE = (0.090, 0.045)

    fascia_west_x = porch_roof_outer - FASCIA_THICKNESS / 2
    fascia_west_y = (porch_roof_north + porch_roof_south) / 2
    fascia_west_z = porch_roof_low_height - FASCIA_HEIGHT / 2

    bpy.ops.mesh.primitive_cube_add(location=(fascia_west_x, fascia_west_y, fascia_west_z))
    fascia_west = bpy.context.active_object
    fascia_west.name = "MainDwelling_PorchRoof_FasciaWest"
    fascia_west_length = porch_roof_south - porch_roof_north
    fascia_west.scale = (FASCIA_THICKNESS / 2, fascia_west_length / 2, FASCIA_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    fascia_west.data.materials.append(floor_mat)

    fascia_north_x = (porch_roof_building + porch_roof_outer) / 2
    fascia_north_y = porch_roof_north + FASCIA_THICKNESS / 2
    fascia_north_z_high = porch_roof_high_height - FASCIA_HEIGHT / 2
    fascia_north_z_low = porch_roof_low_height - FASCIA_HEIGHT / 2
    fascia_north_z = (fascia_north_z_high + fascia_north_z_low) / 2
    fascia_north_length = porch_roof_span

    bpy.ops.mesh.primitive_cube_add(location=(fascia_north_x, fascia_north_y, fascia_north_z))
    fascia_north = bpy.context.active_object
    fascia_north.name = "MainDwelling_PorchRoof_FasciaNorth"
    fascia_north.scale = (fascia_north_length / 2, FASCIA_THICKNESS / 2, FASCIA_HEIGHT / 2)
    fascia_north.rotation_euler[1] = -actual_roof_pitch_rad
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    fascia_north.data.materials.append(floor_mat)

    fascia_south_y = porch_roof_south - FASCIA_THICKNESS / 2

    bpy.ops.mesh.primitive_cube_add(location=(fascia_north_x, fascia_south_y, fascia_north_z))
    fascia_south = bpy.context.active_object
    fascia_south.name = "MainDwelling_PorchRoof_FasciaSouth"
    fascia_south.scale = (fascia_north_length / 2, FASCIA_THICKNESS / 2, FASCIA_HEIGHT / 2)
    fascia_south.rotation_euler[1] = -actual_roof_pitch_rad
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    fascia_south.data.materials.append(floor_mat)

    PURLIN_SPACING = 0.6
    num_purlins = int(porch_roof_span / PURLIN_SPACING)

    for i in range(1, num_purlins):
        purlin_x = porch_roof_building - (i * PURLIN_SPACING)
        purlin_y = (porch_roof_north + porch_roof_south) / 2
        distance_from_high = abs(purlin_x - porch_roof_building)
        slope_drop = distance_from_high * math.tan(math.radians(PORCH_ROOF_PITCH))
        purlin_z = porch_roof_high_height - slope_drop - PURLIN_SIZE[1] / 2

        bpy.ops.mesh.primitive_cube_add(location=(purlin_x, purlin_y, purlin_z))
        purlin = bpy.context.active_object
        purlin.name = f"MainDwelling_PorchRoof_Purlin_{i}"
        purlin_length = porch_roof_south - porch_roof_north
        purlin.scale = (PURLIN_SIZE[0] / 2, purlin_length / 2, PURLIN_SIZE[1] / 2)
        bpy.ops.object.transform_apply(scale=True)
        purlin.data.materials.append(floor_mat)
