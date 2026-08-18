import os

# Core dimensions (meters)
WIDTH = 7.4
ENCLOSED_WIDTH = 6.0  #should be WIDTH minus NORTH_RECESS minus 2 * EXTERIOR_WALL_THICKNESS
LENGTH = 9.0
NORTH_RECESS = 1.0

# Vertical dimensions (meters)
GROUND_FLOOR_HEIGHT = 2.4
FIRST_FLOOR_HEIGHT = 2.6 # add 0.2 for first floor thickness
TOTAL_HEIGHT = GROUND_FLOOR_HEIGHT + FIRST_FLOOR_HEIGHT #+ 0.2  # add 0.2 for first floor thickness

# Wall thicknesses (meters)
EXTERIOR_WALL_THICKNESS = 0.15
INTERIOR_WALL_THICKNESS = 0.11

# Roof defaults
ROOF_PITCH = 35
ROOF_OVERHANG = 0.6


def get_texture_path(*parts):
    """Return an absolute path under the repository textures directory."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "textures", *parts)
