import bpy  # type: ignore

from main_dwelling import config as dwelling_config
from main_dwelling.materials_nodes import create_material, create_textured_material


def build_north_deck(origin=(0, 0, 0), building_length=9.3, building_width=7.0, DECK_EXTENSION = 3.0, PILE_SIZE = 0.15, BEARER_SIZE = (0.150, 0.200), add_boundary_joist=False):
    """
    Build a timber deck extending 3 meters north from the recessed north wall of the main dwelling.
    The deck is constructed with piles, bearers, joists, and 90mm x 25mm decking boards.

    Args:
        origin: (x, y, z) tuple for building origin (same as main dwelling)
        building_length: East-west dimension of building (9m default)
        building_width: North-south dimension of building (7m default)
    """
    ox, oy, oz = origin

    DECK_THICKNESS = 0.025
    DECK_BOARD_WIDTH = 0.090
    BOARD_GAP = 0.005
   
    PILE_HEIGHT_ABOVE_GROUND = 0.4
    PILE_DEPTH_BELOW_GROUND = 0.6
    
    JOIST_SIZE = (0.090, 0.190)
    JOIST_SPACING = 0.45

    #north_wall_y = oy + building_width / 2 - north_recess
    deck_start_y = oy
    deck_end_y = deck_start_y + DECK_EXTENSION
    deck_center_y = (deck_start_y + deck_end_y) / 2

    DECK_HEIGHT_OFFSET = -0.52

    deck_west_x = ox - building_length / 2
    deck_east_x = ox + building_length / 2
    deck_center_x = ox

    texture_path = dwelling_config.get_texture_path("knotted-timber-staggered-1995-mm-architextures.jpg")
    deck_mat = create_textured_material("TimberDecking", texture_path)
    structure_mat = create_material("TreatedTimber", (0.55, 0.45, 0.35, 1))

    pile_cols = 4
    pile_spacing_ns = DECK_EXTENSION / 2
    pile_spacing_ew = building_length / (pile_cols + 1)
    NORTH_BEARER_INSET = 0.15

    pile_y_middle = deck_start_y + pile_spacing_ns
    pile_y_north = deck_start_y + (2 * pile_spacing_ns) - NORTH_BEARER_INSET

    pile_positions = [
        ("Middle", pile_y_middle),
        ("North", pile_y_north),
    ]

    pile_center_z = oz + DECK_HEIGHT_OFFSET - PILE_DEPTH_BELOW_GROUND + (PILE_DEPTH_BELOW_GROUND + PILE_HEIGHT_ABOVE_GROUND) / 2

    for row_name, pile_y in pile_positions:
        for col in range(pile_cols):
            pile_x = deck_east_x - (col + 1) * pile_spacing_ew

            bpy.ops.mesh.primitive_cube_add(location=(pile_x, pile_y, pile_center_z))
            pile = bpy.context.active_object
            pile.name = f"Deck_Pile_{row_name}_C{col + 1}"
            pile.scale = (PILE_SIZE / 2, PILE_SIZE / 2, (PILE_DEPTH_BELOW_GROUND + PILE_HEIGHT_ABOVE_GROUND) / 2)
            bpy.ops.object.transform_apply(scale=True)
            pile.data.materials.append(structure_mat)

    bearer_z = oz + DECK_HEIGHT_OFFSET + PILE_HEIGHT_ABOVE_GROUND - BEARER_SIZE[1] / 2

    bpy.ops.mesh.primitive_cube_add(location=(deck_center_x, pile_y_middle, bearer_z))
    bearer = bpy.context.active_object
    bearer.name = "Deck_Bearer_Middle"
    bearer.scale = (building_length / 2, BEARER_SIZE[0] / 2, BEARER_SIZE[1] / 2)
    bpy.ops.object.transform_apply(scale=True)
    bearer.data.materials.append(structure_mat)

    bpy.ops.mesh.primitive_cube_add(location=(deck_center_x, pile_y_north, bearer_z))
    bearer = bpy.context.active_object
    bearer.name = "Deck_Bearer_North"
    bearer.scale = (building_length / 2, BEARER_SIZE[0] / 2, BEARER_SIZE[1] / 2)
    bpy.ops.object.transform_apply(scale=True)
    bearer.data.materials.append(structure_mat)

    joist_z = oz + DECK_HEIGHT_OFFSET + PILE_HEIGHT_ABOVE_GROUND + JOIST_SIZE[1] / 2
    num_joists = int(building_length / JOIST_SPACING) + 1

    for i in range(num_joists):
        joist_x = deck_east_x - (i * JOIST_SPACING)
        if joist_x < deck_west_x:
            break

        bpy.ops.mesh.primitive_cube_add(location=(joist_x, deck_center_y, joist_z))
        joist = bpy.context.active_object
        joist.name = f"Deck_Joist_{i + 1:02d}"
        joist.scale = (JOIST_SIZE[0] / 2, DECK_EXTENSION / 2, JOIST_SIZE[1] / 2)
        bpy.ops.object.transform_apply(scale=True)
        joist.data.materials.append(structure_mat)

    if add_boundary_joist:
        # Optional rim/boundary joist along the north deck edge.
        boundary_joist_y = deck_end_y - JOIST_SIZE[0] / 2
        bpy.ops.mesh.primitive_cube_add(location=(deck_center_x, boundary_joist_y, joist_z))
        boundary_joist = bpy.context.active_object
        boundary_joist.name = "Deck_BoundaryJoist_North"
        boundary_joist.scale = (building_length / 2, JOIST_SIZE[0] / 2, JOIST_SIZE[1] / 2)
        bpy.ops.object.transform_apply(scale=True)
        boundary_joist.data.materials.append(structure_mat)

    deck_surface_z = oz + DECK_HEIGHT_OFFSET + PILE_HEIGHT_ABOVE_GROUND + JOIST_SIZE[1] + DECK_THICKNESS / 2
    num_boards = int(DECK_EXTENSION / (DECK_BOARD_WIDTH + BOARD_GAP)) + 1

    for i in range(num_boards):
        board_y = deck_start_y + (i * (DECK_BOARD_WIDTH + BOARD_GAP)) + DECK_BOARD_WIDTH / 2
        if board_y > deck_end_y:
            break

        bpy.ops.mesh.primitive_cube_add(location=(deck_center_x, board_y, deck_surface_z))
        board = bpy.context.active_object
        board.name = f"Deck_Board_{i + 1:02d}"
        board.scale = (building_length / 2, DECK_BOARD_WIDTH / 2, DECK_THICKNESS / 2)
        bpy.ops.object.transform_apply(scale=True)
        board.data.materials.append(deck_mat)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')

    print(f"North Deck built at origin {origin}, extending {DECK_EXTENSION}m north")
