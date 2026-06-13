import bpy  # type: ignore
import sys
import os
from importlib import reload


# Add current directory to sys.path so Blender can find your modules
dir = os.path.dirname(bpy.data.filepath)
if dir not in sys.path:
    sys.path.append(dir)

# Clear cached dwelling modules so failed/partial imports do not persist across runs.
for mod_name in [
    "main_dwelling_module",
    "main_dwelling.config",
    "main_dwelling.furnishings",
    "main_dwelling.interiors",
    "main_dwelling.structure",
    "main_dwelling.deck",
    "main_dwelling.materials_nodes",
    "main_dwelling.envelope",
    "main_dwelling.exterior_details",
    "main_dwelling.porch",
    "main_dwelling.material_setup",
    "main_dwelling.build_context",
    "main_dwelling.runtime_context",
    "main_dwelling.build_pipeline",
]:
    sys.modules.pop(mod_name, None)

import björken_module
import ww1_module
import ww1_furniture
import wet_wing_lower1
import wet_wing_upper1
import ground_module
import driveway
import outdoor_structures
import main_dwelling_module
import main_dwelling.config as main_dwelling_config
import main_dwelling.furnishings as main_dwelling_furnishings
import main_dwelling.interiors as main_dwelling_interiors
import main_dwelling.structure as main_dwelling_structure
import main_dwelling.deck as main_dwelling_deck
import main_dwelling.materials_nodes as main_dwelling_materials_nodes
import main_dwelling.envelope as main_dwelling_envelope
import main_dwelling.exterior_details as main_dwelling_exterior_details
import main_dwelling.porch as main_dwelling_porch
import main_dwelling.material_setup as main_dwelling_material_setup
import main_dwelling.build_context as main_dwelling_build_context
import main_dwelling.runtime_context as main_dwelling_runtime_context
import main_dwelling.build_pipeline as main_dwelling_build_pipeline
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
reload(driveway)
reload(outdoor_structures)
reload(main_dwelling_config)
reload(main_dwelling_materials_nodes)
reload(main_dwelling_deck)
reload(main_dwelling_structure)
reload(main_dwelling_interiors)
reload(main_dwelling_furnishings)
reload(main_dwelling_envelope)
reload(main_dwelling_exterior_details)
reload(main_dwelling_porch)
reload(main_dwelling_material_setup)
reload(main_dwelling_build_context)
reload(main_dwelling_runtime_context)
reload(main_dwelling_build_pipeline)
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

def set_hdri_sky(image_path):
    """
    Sets the background world environment to use an HDRI image
    for realistic sky and ambient lighting.
    """
    if not os.path.exists(image_path):
        print(f"Error: HDRI file not found at {image_path}")
        return None

    # Ensure the World settings are using nodes
    world = bpy.context.scene.world
    if not world:
        # Create a world if somehow one doesn't exist
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
        
    world.use_nodes = True
    node_tree = world.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    
    # Clean up existing background/environment nodes to prevent overlapping
    for node in list(nodes):
        if node.type in ['BACKGROUND', 'TEX_ENVIRONMENT']:
            nodes.remove(node)
            
    # Find the World Output node (it's always there by default)
    output_node = next((n for n in nodes if n.type == 'OUTPUT_WORLD'), None)
    if not output_node:
        output_node = nodes.new(type='ShaderNodeOutputWorld')
        output_node.location = (400, 0)

    # 1. Create a Background Shader node
    bg_node = nodes.new(type='ShaderNodeBackground')
    bg_node.location = (200, 0)
    bg_node.inputs['Strength'].default_value = 1.0  # Control sky brightness here
    
    # 2. Create an Environment Texture node
    env_node = nodes.new(type='ShaderNodeTexEnvironment')
    env_node.location = (0, 0)
    
    # 3. Load the actual .hdr or .exr image file
    try:
        hdr_image = bpy.data.images.load(image_path)
        env_node.image = hdr_image
    except Exception as e:
        print(f"Failed to load HDRI image data: {e}")
        return None
        
    # 4. Link everything together
    links.new(env_node.outputs['Color'], bg_node.inputs['Color'])
    links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])
    
    print("HDRI Sky successfully applied!")
    return world


cleanup()
#setup_blue_sky()
# Path to the actual HDR panorama map file from your download folder
hdri_path = os.path.abspath("textures/MorningSkyHDRI002B/MorningSkyHDRI002B_1K_HDR.exr")

# Set the sky
set_hdri_sky(hdri_path)

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
    # Small banks down on east and west sides - narrow strips need fine X spacing, reasonable Y spacing
    ground_module.gravel_plane(grid_points((6, 4, 0.0), (7, -9, -1), x_spacing=0.5, y_spacing=0.5, slope_direction='x'))
    ground_module.gravel_plane(grid_points((-7, -9, -1),(-6, 4, 0.0), x_spacing=0.5, y_spacing=0.5, slope_direction='x'))
    

    
    # Forest surrounds on all sides of main dwelling
    main_dwelling_forest_north = grid_points((18, 32, 0), (-8, 3.5, -4.2), x_spacing=0.5, slope_direction='y')

    main_dwelling_forest_west = grid_points((-6, 18, -0.5), (-30, -3.5, -3.1), x_spacing=0.5, slope_direction='y')
    
    ground_module.forest_plane(main_dwelling_forest_north)
    ground_module.forest_plane(grid_points((2, -28, 0.5), (-30, -8, 0.5), x_spacing=0.5, slope_direction='y')) #flat_grass_play_area
    ground_module.forest_plane(grid_points((2, -15, 0.5), (5, -8, 1), x_spacing=0.5, slope_direction='x')) 
    ground_module.forest_plane(grid_points((9, -15, 1  ), (5, -8, 1), x_spacing=0.5, slope_direction='y'))
    ground_module.forest_plane(grid_points((9, -15, 1  ), (13, -8, -2), x_spacing=0.5, slope_direction='x'))
    ground_module.forest_plane(grid_points((10, 3.5, -0.2), (6.5, -8, -0.2), x_spacing=0.5)) #main dwelling east 1
    ground_module.forest_plane(grid_points((10, -8, -0.2), (20, 3.5, -6), x_spacing=0.5, slope_direction='x')) #main dwelling east 2
    ground_module.gravel_plane(main_dwelling_forest_west)
    ground_module.gravel_plane(grid_points((-30, -3.5, -0.5), (-6, -7.5, -0.5), x_spacing=0.5, slope_direction='y'))
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


from driveway import create_sloping_driveway  
driveway.create_sloping_driveway(width=4.0, thickness=0.15)


print("Modular Site Build Complete.")