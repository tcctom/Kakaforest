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
import wet_wing_option2_module
import wet_wing_option2_furniture
import ground_module
import utils

# Reload modules to pick up any changes
reload(utils)
reload(björken_module)
reload(wet_wing_module)
reload(wet_wing_furniture)
reload(wet_wing_option2_module)
reload(wet_wing_option2_furniture)
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
    # Photo reference: taken from ~(8,-6,-2) looking south, person at ~(9,0,0.2) is 1.75m tall
    
    # Court area - relatively flat
    badminton = grid_points((-7, -10, -3), (5, -14, -3.2), x_spacing=0.5, slope_direction='y')
    
    # Under and around Björken cottage - relatively flat platform
    under_björken = grid_points((-7, -2.5, -0.5), (5, 3.1, -0.5), x_spacing=0.4)
    north_björken = grid_points((-4, -2.5, -0.5), (1, -6, -0.5), x_spacing=0.4)
    
    # South of cottage - upward slope
    south_björken = grid_points((-3, 3.1, -0.5), (3, 5.1, 1.8), x_spacing=0.4, slope_direction='y')
    southwest_björken = grid_points((3, 3.1, -0.5), (13, 9.1, 1.8), x_spacing=0.4, slope_direction='y')
    
    # PARKING & DRIVE AREAS - with natural variation (not perfectly flat)
    # Main parking area - slight undulation
    drive_end_parking_west = grid_points((6, -8, -2.0), (10, -6, -1.9), x_spacing=0.3)
    drive_end_parking_east = grid_points((10.5, -8, -2.1), (15, -6, -2.0), x_spacing=0.3)
    
    # Parking area closer to cottage - slightly higher with variation
    drive_mid_area = grid_points((7, -5.5, -1.7), (12, -4, -1.5), x_spacing=0.3)
    
    # TRANSITION SLOPES - from parking up to cottage level
    # Gradual slope from parking (-2m) up to cottage area (-0.5m) 
    # This is the slope visible in the photo - about 1:4 grade
    slope_parking_to_cottage_west = grid_points((6, -4, -1.3), (9, -2.5, -0.7), x_spacing=0.25, slope_direction='y')
    slope_parking_to_cottage_mid = grid_points((9, -3.5, -1.0), (12, -2.5, -0.6), x_spacing=0.25, slope_direction='y')
    slope_parking_to_cottage_east = grid_points((12, -4, -1.4), (15, -2.5, -0.8), x_spacing=0.25, slope_direction='y')
    
    # Area where person is standing in photo - around Y=0, Z~0 to 0.2
    photo_person_area = grid_points((7, -1, -0.2), (11, 0.5, 0.2), x_spacing=0.3)
    
    # Additional natural undulation points for realism
    natural_bumps = [
        point(8, -6, -1.95),  # Small bump near camera position
        point(9, -5, -1.6),   # Mid-slope variation
        point(10, -3, -0.9),  # Mid-slope variation
        point(11, -4.5, -1.2), # Eastern slope variation
    ]
    
    # Combine all survey points
    survey_points = combine_points(
        badminton, under_björken, north_björken, south_björken, southwest_björken,
        drive_end_parking_west, drive_end_parking_east, drive_mid_area,
        slope_parking_to_cottage_west, slope_parking_to_cottage_mid, slope_parking_to_cottage_east,
        photo_person_area, natural_bumps
    )
    
    ground_module.build_ground_terrain(cottage_origin=(0, 0, 0), contour_points=survey_points,)
        #ground_module.build_ground_terrain(cottage_origin=(0, 0, 0))

# 1. Build existing cottage
# Set show_roof=False to hide roof for interior viewing
björken_module.build_red_cottage(origin=(0, 0, 0))

# 2. Build Wet Wing - OPTION 1 (6m × 6m)
# Moved 9m West (+X) and 4m South (+Y)
# Set show_roof=False to hide roof for interior viewing
wet_wing_module.build_potius_wet_wing(origin=(11.0, 4.0, 1.2), show_roof=False)

# 3. Build Wet Wing - OPTION 2 (10m × 6m + 10m × 4m extension)
# Main building: 10m wide (X) × 6m deep (Y)
#wet_wing_option2_module.build_potius_wet_wing_option2(origin=(12.0, 4.0, 2.4), show_roof=True)
# Add furniture to wet wing option 2
#wet_wing_option2_furniture.build_wet_wing_option2_furniture(origin=(12.0, 4.0, 2.4), building_width=10.0, building_depth=6.0)
# Under extension: 10m wide (X) × 4m deep (Y), positioned beneath the main building
#wet_wing_option2_module.build_under_extension(origin=(12.0, 3.0, 0))





print("Modular Site Build Complete.")