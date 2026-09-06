from main_dwelling.config import WIDTH
from main_dwelling.envelope import (
    _add_gable_windows,
    _add_exterior_windows_and_doors,
    _create_gable_roof,
)
from main_dwelling.exterior_details import add_first_floor_balcony_railing
from main_dwelling.furnishings import (
    _create_dining_table,
    _create_kitchen_bench,
    _furnish_main_bathroom,
    _furnish_master_bedroom,
    _furnish_master_ensuite,
    _furnish_guest_bedroom,
)
from main_dwelling.interiors import (
    _create_interior_partitions_first_floor,
    _create_interior_partitions_ground_floor,
    _create_stair_partitions,
    _create_stair_partitions2,
    _create_stair_partitions3,_create_stair_partitions4,
)
from main_dwelling.materials_nodes import create_material


def run_main_dwelling_build_pipeline(
    ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT,
    TOTAL_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS, ROOF_PITCH, ROOF_OVERHANG,
    show_roof,    roof_style,    potius_mat,
    option=1,
):
    """Run the post-shell build sequence for interior, detailing, and optional roof."""
    # Interior partitions
    _create_interior_partitions_ground_floor( ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS, option=option, )
    _create_interior_partitions_first_floor ( ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS, option=option, )
    
    if option == 1:
        _create_stair_partitions(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS)
    if option == 2:
        _create_stair_partitions2(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS)
    if option == 3:
        _create_stair_partitions3(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS)
    if option == 4:
        _create_stair_partitions4(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS)

    # Ensuite and bathroom
    _furnish_master_ensuite( ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, )
    _furnish_main_bathroom( ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, )
    _furnish_guest_bedroom( ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, )
    _furnish_master_bedroom(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, GROUND_FLOOR_HEIGHT)

    # Kitchen and dining
    if option == 1:
        _create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
        _create_dining_table(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, TABLE_LENGTH = 0.9, TABLE_WIDTH = 1.8)
    if option == 2:
        _create_kitchen_bench(ox-2.1, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
        _create_dining_table(ox-1.9, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, TABLE_LENGTH = 0.9, TABLE_WIDTH = 1.8)
    if option == 3:
        _create_kitchen_bench(ox-2.1, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
        _create_dining_table(ox-2.4, oy-0.5, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, TABLE_LENGTH = 0.9, TABLE_WIDTH = 1.8)
    if option == 4:
        _create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
        _create_dining_table(ox-2.0, oy-0.2, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, TABLE_LENGTH = 0.9, TABLE_WIDTH = 1.8)

    # Exterior openings
    _add_exterior_windows_and_doors( ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, option=option)

    # Balcony railing
    add_first_floor_balcony_railing( ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, create_material, )

    # Gable roof
    if show_roof:
        _create_gable_roof( ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, EXTERIOR_WALL_THICKNESS, roof_style, potius_mat, )
        _add_gable_windows( ox, oy, oz, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, option=option )

