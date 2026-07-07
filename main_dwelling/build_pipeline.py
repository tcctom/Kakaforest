from main_dwelling.envelope import (
    _add_exterior_windows_and_doors,
    _add_west_gable_window,
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
)
from main_dwelling.materials_nodes import create_material


def run_main_dwelling_build_pipeline(
    ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT,
    TOTAL_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS, ROOF_PITCH, ROOF_OVERHANG,
    show_roof,
    roof_style,
    potius_mat,
):
    """Run the post-shell build sequence for interior, detailing, and optional roof."""
    # Interior partitions
    _create_interior_partitions_ground_floor( ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS, )
    _create_interior_partitions_first_floor ( ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS, )
    #_create_stair_partitions(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS)


    # Ensuite and bathroom
    _furnish_master_ensuite( ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, )
    _furnish_main_bathroom( ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, )
    _furnish_guest_bedroom( ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, )
    _furnish_master_bedroom(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, GROUND_FLOOR_HEIGHT)

    # Kitchen and dining
    #_create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
    _create_dining_table(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)

    # Exterior openings
    _add_exterior_windows_and_doors( ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, )

    # Balcony railing
    add_first_floor_balcony_railing( ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, create_material, )

    # Gable roof
    if show_roof:
        _create_gable_roof( ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, roof_style, potius_mat, )

        _add_west_gable_window( ox, oy, oz, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, roof_style,        )
