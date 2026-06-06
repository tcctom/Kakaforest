from main_dwelling import config as dwelling_config


def get_main_dwelling_dimensions():
    """Return frequently used main-dwelling dimensional constants in call-site order."""
    return (
        dwelling_config.WIDTH,
        dwelling_config.ENCLOSED_WIDTH,
        dwelling_config.NORTH_RECESS,
        dwelling_config.LENGTH,
        dwelling_config.GROUND_FLOOR_HEIGHT,
        dwelling_config.FIRST_FLOOR_HEIGHT,
        dwelling_config.TOTAL_HEIGHT,
        dwelling_config.EXTERIOR_WALL_THICKNESS,
        dwelling_config.INTERIOR_WALL_THICKNESS,
        dwelling_config.ROOF_PITCH,
        dwelling_config.ROOF_OVERHANG,
    )
