import bpy  # type: ignore
import sys
import os
from importlib import reload

# Add current directory to sys.path so Blender can find your modules
dir = os.path.dirname(bpy.data.filepath)
if dir not in sys.path:
    sys.path.append(dir)

import björken_module
import wet_wing_module
import wet_wing_furniture
import ground_module
import utils

# Reload modules to pick up any changes
reload(utils)
reload(björken_module)
reload(wet_wing_module)
reload(wet_wing_furniture)
reload(ground_module)

def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

cleanup()

# Toggle features on/off
SHOW_GROUND = True  # Set to False to hide ground terrain

# 0. Build ground terrain (optional)
if SHOW_GROUND:
    # Import helper functions for easier point generation
    from ground_module import line_points, grid_points, combine_points, point
    
    # Define survey points using helper functions
    # This is much easier than typing out every coordinate!
    
    #misc = [point(0, -10, -4.5),point(0, -11, -4.5)]
    
    badminton = grid_points((-7, -10, -4.5), (15, -14, -4.5), x_spacing=0.5)
    under_björken = grid_points((-7, -2.5, -0.5), (5, 3.1, -0.5), x_spacing=0.5)
    north_björken = grid_points((-4, -2.5, -0.5), (1, -6, -0.5), x_spacing=0.5)
    
    # Ridge 3m south of cottage, 2m above floor level
    ridge = line_points((-3, 5.1, 2), (4, 5.1, 2), spacing=0.5)
    ridge2 = line_points((-4, 6.1, 2.2), (6, 6.1, 2.2), spacing=0.5)
    
    # Valley area northeast, 2m below floor level
    drive_end_parking = grid_points((6, -8, -2), (12, -5, -2), x_spacing=0.5)
    drive_border_slope = grid_points((6, -8, -2), (12, -9, -2.7), x_spacing=0.25)
    slope1 = grid_points((6, -9, -2.7), (12, -14, -3.7), x_spacing=0.25)
    
    # Combine all survey points
    survey_points = combine_points(badminton, under_björken, north_björken, ridge, ridge2, drive_end_parking, drive_border_slope, slope1)
    
    ground_module.build_ground_terrain(cottage_origin=(0, 0, 0), contour_points=survey_points,)
        #ground_module.build_ground_terrain(cottage_origin=(0, 0, 0))

# 1. Build existing cottage
# Set show_roof=False to hide roof for interior viewing
björken_module.build_red_cottage(origin=(0, 0, 0))

# 2. Build Wet Wing at your specific coords
# Moved 9m West (+X) and 4m South (+Y)
# Set show_roof=False to hide roof for interior viewing
wet_wing_module.build_potius_wet_wing(origin=(11.0, 4.0, 0.7))
#wet_wing_module.build_potius_wet_wing(origin=(11.0, 4.0, 2.7), show_roof=False)

print("Modular Site Build Complete.")