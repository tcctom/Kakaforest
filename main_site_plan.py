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
import materials
import utils

# Reload modules to pick up any changes
reload(materials)
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
    
    # Clear materials to force recreation with textures
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

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
    
    north_björken = grid_points((6, -57.5, 4.5), (-3, -52, 4.5), x_spacing=0.4)
    
    # South of cottage - upward slope
    south_björken = grid_points((5, -63.1, 4.5), (-5, -66, 6.8), x_spacing=0.4, slope_direction='y')
    southwest_björken = grid_points((-4, -64.1, 4.5), (-22, -74, 6.8), x_spacing=0.4, slope_direction='y')
    
    
    # TRANSITION SLOPES - from parking up to cottage level
    # Gradual slope from parking (-2m) up to cottage area (-0.5m) 
    # This is the slope visible in the photo - about 1:4 grade
    slope_parking_to_cottage_west = grid_points((-4, -56, 3.7), (-10, -57.5, 4.3), x_spacing=0.25, slope_direction='y')
    slope_parking_to_cottage_mid = grid_points((-9, -56.5, 4.0), (-15, -57.5, 4.4), x_spacing=0.25, slope_direction='y')
    slope_parking_to_cottage_east = grid_points((-14, -56, 3.6), (-20, -57.5, 4.2), x_spacing=0.25, slope_direction='y')
    
    # Area where person is standing in photo - around Y=0, Z~0 to 0.2
    photo_person_area = grid_points((-7, -59, 4.8), (-11, -60.5, 5.2), x_spacing=0.3)
    
    # Additional natural undulation points for realism
    natural_bumps = [
        point(-8, -54, 3.05),  # Small bump near camera position
        point(-9, -55, 3.4),   # Mid-slope variation
        point(-10, -57, 4.1),  # Mid-slope variation
        point(-11, -55.5, 3.8), # Eastern slope variation
    ]
    
    # Water tank area - flat pad at (-3, 70, 7)
    water_tank_pad = grid_points((5, -66, 6.0), (1, -76, 6.0), x_spacing=0.5)
    by_water_tank_pad = grid_points((0.5, -67, 6.5), (-6, -76, 7.0), x_spacing=0.5)
    
    
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
    #ground_module.grass_plane(north_björken)

    #badminton and surrounding area is mostly grass, but with some natural undulation and patches of moss/gravel
    #ground_module.grass_plane(grid_points((10, -50, 2), (-8, -42, 1.8), x_spacing=0.5, slope_direction='y'))
        
    #under and around Björken is mostly gravel with some patches of grass 
    #ground_module.gravel_plane(grid_points((10, -57.5, 4.5), (-8, -63.1, 4.5), x_spacing=0.4))

    #drive_end_parking_west = grid_points((-4, -50, 3.0), (-12, -54, 3.1), x_spacing=0.3)
    #drive_mid_area = grid_points((-5, -54.5, 3.3), (-15, -56, 3.5), x_spacing=0.3)
    #drive_end_parking_east = grid_points((-12, -50, 2.9), (-18, -54, 3.0), x_spacing=0.3)

    #ground_module.gravel_plane(drive_end_parking_west)
    #ground_module.gravel_plane(drive_mid_area)
    #ground_module.gravel_plane(drive_end_parking_east)
    
    #ground_module.gravel_plane(water_tank_pad)
    
    #ground_module.forest_plane(south_björken)
    #ground_module.forest_plane(southwest_björken)

    #ground_module.forest_plane(slope_parking_to_cottage_west)
    
    # Main Dwelling area (at origin, with Björken 60m south and 5m higher elevation)
    # Ground level at 0.0, building sits on slight clearing
    main_dwelling_clearing = grid_points((6, 4, 0.0), (-6, -9, 0.0), x_spacing=0.4)
    ground_module.gravel_plane(main_dwelling_clearing)
    

    
    # Forest surrounds on all sides of main dwelling
    main_dwelling_forest_north = grid_points((18, 32, 0), (-8, 3.5, -4.2), x_spacing=0.5, slope_direction='y')
    flat_grass_play_area = grid_points((10, -28, 0.5), (-30, -8, 0.5), x_spacing=0.5, slope_direction='y')
    main_dwelling_forest_east = grid_points((30, 3.5, -0.2), (6, -8, -0.1), x_spacing=0.5)
    main_dwelling_forest_west = grid_points((-6, 18, -0.5), (-30, -7.5, -3.1), x_spacing=0.5, slope_direction='y')
    
    ground_module.forest_plane(main_dwelling_forest_north)
    ground_module.forest_plane(flat_grass_play_area)
    ground_module.forest_plane(main_dwelling_forest_east)
    ground_module.gravel_plane(main_dwelling_forest_west)
    ground_module.gravel_plane(grid_points((-30, -8, 0.5), (-6, -7.5, -0.5), x_spacing=0.5, slope_direction='y'))

# 1. Build existing cottage (60m south of main dwelling, 5m higher elevation)
# Set show_roof=False to hide roof for interior viewing
#björken_module.build_red_cottage(origin=(0, -60, 5.0))

# 1a. Build Main Dwelling
# Now located at origin (0, 0, 0)
# This is the new two-story 6m × 8m main dwelling structure
# Roof options: 
#   - "traditional": Overhang on all sides, separate gable end triangles
#   - "flush": Flush with all walls, north side extends 1m down for balcony shading
#main_dwelling_module.build_main_dwelling(origin=(0, 0, 0), show_roof=True, roof_style="flush")
main_dwelling_module.build_main_dwelling_simple_porch(origin=(0, 0, 0), show_roof=True, roof_style="flush")

# 1a. Build North Deck - extends 3m north from ground floor
main_dwelling_module.build_north_deck(origin=(0, 0, 0))

# 1b. Build boulder row along south edge of clearing
outdoor_structures.build_boulder_row(start_pos=(5, -7.8, 0), end_pos=(-5, -7.8, 0), spacing=0.4)
# and north and south of porch
outdoor_structures.create_single_boulder(position=(-6.5, 2.2, -0.4), base_size=1.0)
outdoor_structures.create_single_boulder(position=(-6.5, 1.6, -0.4), base_size=0.9)
outdoor_structures.create_single_boulder(position=(-6.5, -1.9, -0.4), base_size=0.9)


# 1c. Pavers extending east from cottage
outdoor_structures.build_pavers_east(origin=(0, -60, 4.55))

# 2. Build Wet Wing - OPTION 1 (6m × 6m)
# Moved 9m West (+X) and 4m South (+Y) from Björken
# Set show_roof=False to hide roof for interior viewing
#ww1_module.build_potius_wet_wing(origin=(-11.0, -64.0, 6.2), show_roof=False)

# 3. Build Wet Wing - OPTION 2 (10m × 6m + 10m × 4m extension)
# Upper level: 10m wide (X) × 6m deep (Y) - positioned relative to Björken
#wet_wing_upper1.build(origin=(-13.0, -66.0, 7.4), show_roof=False)
#wet_wing_upper1.furniture(origin=(-13.0, -66.0, 7.4), building_width=10.0, building_depth=6.0)

# Lower level: 10m wide (X) × 4m deep (Y) - positioned relative to Björken
#wet_wing_lower1.build(origin=(-13.0, -65.0, 5.0))
#wet_wing_lower1.furniture(origin=(-13.0, -65.0, 5.0), building_width=10.0, building_depth=4.0)

# 4. Water Tank - 25000 liter cylindrical tank
# Diameter: 3.5m, Height: 2.5m, Bottom center relative to Main Dwelling 
#outdoor_structures.build_water_tank(origin=(3.0, -73.0, 6.0))  #behind björken
outdoor_structures.build_water_tank(origin=(-19.0, -5.5, -0.5))
outdoor_structures.build_water_tank(origin=(-23.0, -5.5, -0.5))

#https://www.devan.co.nz/shop/tanks/water-tanks-above/4000-ltr-tank-2/
#outdoor_structures.build_water_tank(origin=(-3.0, -4.5, -0.0), diameter=1.7, height=1.8)

#https://www.devan.co.nz/shop/tanks/water-tanks-above/1000-ltr-tank-2/
outdoor_structures.build_water_tank(origin=(-2.2, -4.1, -0.0), diameter=0.9, height=2.0)




print("Modular Site Build Complete.")