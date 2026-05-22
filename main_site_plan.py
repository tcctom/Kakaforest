import bpy  # type: ignore
import sys
import os
from importlib import reload

# Add current directory to sys.path so Blender can find your modules
dir = os.path.dirname(bpy.data.filepath)
if dir not in sys.path:
    sys.path.append(dir)

import björken_module
import ww1_module
import ww1_furniture
import wet_wing_lower1
import wet_wing_upper1
import ground_module
import outdoor_structures
import main_dwelling_module
import utils

# Reload modules to pick up any changes
reload(utils)
reload(björken_module)
reload(ww1_module)
reload(ww1_furniture)
reload(wet_wing_lower1)
reload(wet_wing_upper1)
reload(ground_module)
reload(outdoor_structures)
reload(main_dwelling_module)

def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def setup_blue_sky():
    """Set up a simple blue sky background"""
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        # Deep sky blue color (RGB)
        bg_node.inputs[0].default_value = (0.2, 0.4, 0.7, 1.0)
        bg_node.inputs[1].default_value = 1.0  # Strength

cleanup()
setup_blue_sky()

# Toggle features on/off
SHOW_GROUND = True  # Set to False to hide ground terrain

# 0. Build ground terrain (optional)
if SHOW_GROUND:
    # Import helper functions for easier point generation
    from ground_module import line_points, grid_points, combine_points, point
    
    north_björken = grid_points((-6, -2.5, -0.5), (3, -8, -0.5), x_spacing=0.4)
    
    # South of cottage - upward slope
    south_björken = grid_points((-5, 3.1, -0.5), (5, 6, 1.8), x_spacing=0.4, slope_direction='y')
    southwest_björken = grid_points((4, 4.1, -0.5), (22, 14, 1.8), x_spacing=0.4, slope_direction='y')
    
    
    # TRANSITION SLOPES - from parking up to cottage level
    # Gradual slope from parking (-2m) up to cottage area (-0.5m) 
    # This is the slope visible in the photo - about 1:4 grade
    slope_parking_to_cottage_west = grid_points((4, -4, -1.3), (10, -2.5, -0.7), x_spacing=0.25, slope_direction='y')
    slope_parking_to_cottage_mid = grid_points((9, -3.5, -1.0), (15, -2.5, -0.6), x_spacing=0.25, slope_direction='y')
    slope_parking_to_cottage_east = grid_points((14, -4, -1.4), (20, -2.5, -0.8), x_spacing=0.25, slope_direction='y')
    
    # Area where person is standing in photo - around Y=0, Z~0 to 0.2
    photo_person_area = grid_points((7, -1, -0.2), (11, 0.5, 0.2), x_spacing=0.3)
    
    # Additional natural undulation points for realism
    natural_bumps = [
        point(8, -6, -1.95),  # Small bump near camera position
        point(9, -5, -1.6),   # Mid-slope variation
        point(10, -3, -0.9),  # Mid-slope variation
        point(11, -4.5, -1.2), # Eastern slope variation
    ]
    
    # Water tank area - flat pad at (-3, 10, 2)
    water_tank_pad = grid_points((-5, 6, 1.0), (-1, 16, 1.0), x_spacing=0.5)
    by_water_tank_pad = grid_points((-0.5, 7, 1.5), (6, 16, 2.0), x_spacing=0.5)
    
    
    # FOREST areas (default for everything else)
    forest_areas = []
    forest_areas.append(south_björken)
    #forest_areas.append(southwest_björken)
    #forest_areas.append(drive_end_parking_east)
    #forest_areas.append(drive_mid_area)
    #forest_areas.append(slope_parking_to_cottage_west)
    #forest_areas.append(slope_parking_to_cottage_mid)
    #forest_areas.append(slope_parking_to_cottage_east)
    #forest_areas.append(photo_person_area)
    #forest_areas.append(natural_bumps)
    #forest_areas.append(by_water_tank_pad)
    
    # Build terrain layers for each material type
    ground_module.grass_plane(north_björken)

    #badminton and surrounding area is mostly grass, but with some natural undulation and patches of moss/gravel
    ground_module.grass_plane(grid_points((-10, -10, -3), (8, -18, -3.2), x_spacing=0.5, slope_direction='y'))
        
    #under and around Björken is mostly gravel with some patches of grass 
    ground_module.gravel_plane(grid_points((-10, -2.5, -0.5), (8, 3.1, -0.5), x_spacing=0.4))

    drive_end_parking_west = grid_points((4, -10, -2.0), (12, -6, -1.9), x_spacing=0.3)
    drive_mid_area = grid_points((5, -5.5, -1.7), (15, -4, -1.5), x_spacing=0.3)
    drive_end_parking_east = grid_points((12, -10, -2.1), (18, -6, -2.0), x_spacing=0.3)

    ground_module.gravel_plane(drive_end_parking_west)
    ground_module.gravel_plane(drive_mid_area)
    ground_module.gravel_plane(drive_end_parking_east)
    
    ground_module.gravel_plane(water_tank_pad)
    
    ground_module.forest_plane(south_björken)
    ground_module.forest_plane(southwest_björken)

    ground_module.forest_plane(slope_parking_to_cottage_west)
    
    # Main Dwelling area (60m north of Björken, 5m lower elevation)
    # Ground level at -5.0, building sits on slight clearing
    main_dwelling_clearing = grid_points((-6, -68, -5.0), (6, -52, -5.0), x_spacing=0.4)
    ground_module.grass_plane(main_dwelling_clearing)
    
    # Forest surrounds on all sides of main dwelling
    main_dwelling_forest_north = grid_points((-8, -72, -5.2), (8, -68, -5.1), x_spacing=0.5)
    main_dwelling_forest_south = grid_points((-8, -52, -5.1), (8, -48, -4.8), x_spacing=0.5)
    main_dwelling_forest_east = grid_points((-10, -68, -5.2), (-6, -52, -5.1), x_spacing=0.5)
    main_dwelling_forest_west = grid_points((6, -68, -5.1), (10, -52, -5.0), x_spacing=0.5)
    
    ground_module.forest_plane(main_dwelling_forest_north)
    ground_module.forest_plane(main_dwelling_forest_south)
    ground_module.forest_plane(main_dwelling_forest_east)
    ground_module.forest_plane(main_dwelling_forest_west)

# 1. Build existing cottage
# Set show_roof=False to hide roof for interior viewing
björken_module.build_red_cottage(origin=(0, 0, 0))

# 1a. Build Main Dwelling
# Located 60m north (-Y direction) and 5m lower than Björken cottage
# This is the new two-story 6m × 8m main dwelling structure
# Roof options: 
#   - "traditional": Overhang on all sides, separate gable end triangles
#   - "flush": Flush with all walls, north side extends 1m down for balcony shading
main_dwelling_module.build_main_dwelling(origin=(0, -60, -5.0), show_roof=True, roof_style="flush")

# 1b. Pavers extending east from cottage
#outdoor_structures.build_pavers_east(origin=(0, 0, -0.45))

# 2. Build Wet Wing - OPTION 1 (6m × 6m)
# Moved 9m West (+X) and 4m South (+Y)
# Set show_roof=False to hide roof for interior viewing
#ww1_module.build_potius_wet_wing(origin=(11.0, 4.0, 1.2), show_roof=False)

# 3. Build Wet Wing - OPTION 2 (10m × 6m + 10m × 4m extension)
# Upper level: 10m wide (X) × 6m deep (Y) - positioned at z=2.4
#wet_wing_upper1.build(origin=(13.0, 6.0, 2.4), show_roof=False)
#wet_wing_upper1.furniture(origin=(13.0, 6.0, 2.4), building_width=10.0, building_depth=6.0)

# Lower level: 10m wide (X) × 4m deep (Y) - positioned at z=0
#wet_wing_lower1.build(origin=(13.0, 5.0, 0))
#wet_wing_lower1.furniture(origin=(13.0, 5.0, 0), building_width=10.0, building_depth=4.0)

# 4. Water Tank - 25000 liter cylindrical tank
# Diameter: 3.5m, Height: 2.5m, Bottom center at (-3, 13, 1)
#outdoor_structures.build_water_tank(origin=(-3.0, 13.0, 1.0))




print("Modular Site Build Complete.")