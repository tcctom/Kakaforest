import bpy  # type: ignore

from main_dwelling.build_context import get_main_dwelling_dimensions
from main_dwelling.build_pipeline import run_main_dwelling_build_pipeline
from main_dwelling.deck import build_north_deck
from main_dwelling.materials_nodes import (
    create_textured_material,
)
from main_dwelling.porch import build_simple_open_porch
from main_dwelling.runtime_context import get_main_dwelling_runtime_context
from main_dwelling.structure import (
    _create_exterior_walls,
    _create_floors,_create_floors2, _create_floors3,
    _create_180_degree_staircase_southwest,
    _create_180_degree_staircase_southmiddle,
    _create_staircase_southmiddle3,
    _create_staircase_southmiddle2
)
from materials import get_floor_wood_material

# === MAIN BUILDING FUNCTIONS ===

def build_main_dwelling_simple_porch(origin=(0, 0, 0), show_roof=True, roof_style="traditional", option=1):
    """
    Build the main dwelling with a SIMPLE OPEN PORCH entrance option:
    - 2.5m Ã— 1.5m deck (same width as enclosed porch, but only 1.5m deep)
    - No walls - just a roof and deck
    - Monopitch (single-slope) roof sloping outward from building
    - Main entrance door on the main structure's west wall (not on porch)
    
    Args:
        origin: (x, y, z) tuple for building location
        show_roof: Boolean to show/hide main roof for interior viewing
        roof_style: "traditional" or "flush" for main building roof
    """
    ox, oy, oz = origin
    
    # Dimensions from specifications
    (
        WIDTH,
        ENCLOSED_WIDTH,
        NORTH_RECESS,
        LENGTH,
        GROUND_FLOOR_HEIGHT,
        FIRST_FLOOR_HEIGHT,
        TOTAL_HEIGHT,
        EXTERIOR_WALL_THICKNESS,
        INTERIOR_WALL_THICKNESS,
        ROOF_PITCH,
        ROOF_OVERHANG,
    ) = get_main_dwelling_dimensions()

    runtime_context = get_main_dwelling_runtime_context()
    
    # Materials
    potius_mat = create_textured_material(
        "PotiusExterior",
        runtime_context.exterior_texture_path,
    )
    floor_mat = get_floor_wood_material()
    
    # === CREATE SHARED COMPONENTS ===
    _create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat)
    if option == 1:
        _create_floors(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat)
        _create_180_degree_staircase_southwest( ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat, )
        # === SIMPLE OPEN ENTRANCE PORCH (WEST SIDE) ===
        build_simple_open_porch( ox, oy, oz, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat, create_textured_material, runtime_context.porch_deck_texture_path,)

    if option == 2:
        _create_floors2(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat)
        _create_staircase_southmiddle2( ox+0.2, oy-2.95, oz+0.1, floor_mat, )

    if option == 3:
        _create_floors3(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat)
        _create_staircase_southmiddle3( ox+0.2, oy-2.95, oz+0.1, floor_mat, )


    
    run_main_dwelling_build_pipeline( ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT,
        TOTAL_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS, ROOF_PITCH, ROOF_OVERHANG,
        show_roof, roof_style, potius_mat, option=option, )   
    
    print(f"Main Dwelling with simple open porch built at origin {origin}") 
