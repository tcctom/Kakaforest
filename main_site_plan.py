import bpy  # type: ignore
import sys
import os
import mathutils
import math # Needed for the rotation correction

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

def import_linz_terrain(obj_path):
    """
    Import a textured terrain OBJ that is already in site coordinates.
    """
    if not os.path.exists(obj_path):
        print(f"Error: Terrain OBJ not found at {obj_path}")
        return None

    # Save a list of current objects to find what got added
    old_objects = set(bpy.data.objects)

    # Import the OBJ
    try:
        bpy.ops.wm.obj_import(filepath=obj_path)
    except AttributeError:
        bpy.ops.import_scene.obj(filepath=obj_path)

    # Find the newly imported object
    new_objects = set(bpy.data.objects) - old_objects
    if new_objects:
        terrain_obj = list(new_objects)[0]
        terrain_obj.name = "LINZ_Aerial_Terrain"

        # Ensure it stays perfectly centered at your main dwelling origin
        terrain_obj.location = (0, 0, 0)

        print("LINZ Terrain imported at origin using native site coordinates.")
        return terrain_obj
    
    return None

def create_excavation_cutter(contour_points, depth=5.0, name="Excavation_Cutter"):
    """Creates a 3D solid box from grid points to act as a Boolean cutter."""
    xs = [p[0] for p in contour_points]
    ys = [p[1] for p in contour_points]
    
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    z_top = max([p[2] for p in contour_points]) # The top surface height
    z_bottom = z_top - depth                    # Push down into the ground
    
    # 8 corners of a solid box
    verts = [
        (x_min, y_min, z_bottom), (x_max, y_min, z_bottom),
        (x_max, y_max, z_bottom), (x_min, y_max, z_bottom),
        (x_min, y_min, z_top),    (x_max, y_min, z_top),
        (x_max, y_max, z_top),    (x_min, y_max, z_top)
    ]
    
    # 6 faces to close the 3D volume
    faces = [
        (0, 1, 2, 3), # Bottom
        (4, 5, 6, 7), # Top
        (0, 1, 5, 4), # Front
        (1, 2, 6, 5), # Right
        (2, 3, 7, 6), # Back
        (3, 0, 4, 7)  # Left
    ]
    
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    cutter_obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(cutter_obj)
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Hide it from view and render so it's just an invisible cutting tool
    cutter_obj.hide_viewport = True
    cutter_obj.hide_render = True
    
    return cutter_obj




cleanup()

# Paths to your external asset files
hdri_path = os.path.abspath("textures/MorningSkyHDRI002B/MorningSkyHDRI002B_1K_HDR.exr")
terrain_obj_path = os.path.abspath("Terrain/terrain.obj")

# Set the sky
set_hdri_sky(hdri_path)

# Load your exact GIS accurate mapped mesh
# (Assuming this returns the imported object, or names it 'terrain')
linz_terrain = import_linz_terrain(terrain_obj_path) 
if not linz_terrain:
    # Fallback if your function doesn't return the object directly
    linz_terrain = bpy.data.objects.get("terrain") 

# Toggle features on/off
SHOW_GROUND = True  # Set to False to hide ground terrain

# 0. Build ground terrain and clear the LINZ terrain
if SHOW_GROUND and linz_terrain:
    # Import helper functions
    from ground_module import grid_points
    
    # 1. Define the clearing footprint
    main_dwelling_clearing = grid_points((6, 4, 0.0), (-6, -7.5, 0.0), x_spacing=0.4)
    
    # 2. Build the visual gravel plane (sits perfectly on top)
    gravel_pad = ground_module.gravel_plane(main_dwelling_clearing)
    
    # 3. Create the invisible 3D box to dig into the LINZ terrain
    cutter = create_excavation_cutter(main_dwelling_clearing, depth=-2.0)
    
    # 4. Apply the Boolean Modifier to the LINZ terrain to "excavate"
    bool_mod = linz_terrain.modifiers.new(name="Dwelling_Excavation", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter
    bool_mod.solver = 'EXACT'  # 'EXACT' handles dense GIS topography meshes beautifully
    

# 1. Build existing cottage (60m south of main dwelling, 5m higher elevation)
# Set show_roof=False to hide roof for interior viewing
björken_module.build_red_cottage(origin=(21, -57, 8.0))

# 1a. Build Main Dwelling
# Now located at origin (0, 0, 0)
# This is the new two-story 6m × 8m main dwelling structure
# Roof options: 
#   - "traditional": Overhang on all sides, separate gable end triangles
#   - "flush": Flush with all walls, north side extends 1m down for balcony shading
main_dwelling_module.build_main_dwelling_simple_porch(origin=(0, -1, 0), show_roof=True, roof_style="flush")

# 1a. Build North Deck - extends 3m north from ground floor
main_dwelling_module.build_north_deck(origin=(0, -1, 0))

# 1b. Build boulder row along south edge of clearing
#outdoor_structures.build_boulder_row(start_pos=(5, -7.8, 0), end_pos=(-5, -7.8, 0), spacing=0.4)
# and north and south of porch
#outdoor_structures.create_single_boulder(position=(-6.5, 2.2, -0.4), base_size=1.0)
#outdoor_structures.create_single_boulder(position=(-6.5, 1.6, -0.4), base_size=0.9)
#outdoor_structures.create_single_boulder(position=(-6.5, -1.9, -0.4), base_size=0.9)


# 1c. Pavers extending east from cottage
#outdoor_structures.build_pavers_east(origin=(0, -60, 4.55))

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


#ground_module.build_off_axis_plane((-14, -5.8, -0.5), (-13.2, -10, -0.5), length=-12, spacing=0.5, name="Tank_Pad", material_type='gravel',)


# 4. Water Tank - 25000 liter cylindrical tank
# Diameter: 3.5m, Height: 2.5m, Bottom center relative to Main Dwelling 
#outdoor_structures.build_water_tank(origin=(3.0, -73.0, 6.0))  #behind björken
outdoor_structures.build_water_tank(origin=(-16.0, -10.5, -0.5))
outdoor_structures.build_water_tank(origin=(-20.0, -12.0, -0.5))

#https://www.devan.co.nz/shop/tanks/water-tanks-above/4000-ltr-tank-2/
#outdoor_structures.build_water_tank(origin=(-3.0, -4.5, -0.0), diameter=1.7, height=1.8)

#https://www.devan.co.nz/shop/tanks/water-tanks-above/1000-ltr-tank-2/
outdoor_structures.build_water_tank(origin=(-2.2, -5.1, -0.0), diameter=0.9, height=2.0)

path_points_1 = [
        mathutils.Vector((-4.5, -6.5, 0.0)),       
        mathutils.Vector((-7.5, -6.5, 0.0)),       
        mathutils.Vector((-12, -2.2, -1.4)),       
        mathutils.Vector((-17, -1.4, -1.7)),       
        mathutils.Vector((-24, -2.9, -1.8)), 
        mathutils.Vector((-28.0, -7, -2.2)), 
        mathutils.Vector((-31.0, -7.5, -2.5))
    ]


from driveway import create_sloping_driveway  
create_sloping_driveway(name="Main_Drivewayv1", width=3.3, thickness=0.15, path_points=path_points_1, debug_show_points=True)

#Would you be able to analyse the attached image and give me a set of path points in meters? 
#Just the x, y is fine (put z to 0 on all). the red dot just north of center is the origin. North of that is plus Y and east of that is plus X. 
#Can you also see the 10 meter scale bottom right?

# The origin (0, 0, 0) is the red dot north of center
path_points_main_drive = [
    mathutils.Vector((-33.5, 50.0, -10.5)),   # Top entrance at the public road boundary
    mathutils.Vector((-36, 35.0, -8)),   # Heading straight south along the top ridge
    mathutils.Vector((-36.5, 20.0, -6.5)),   # Shifting slightly west past the northern red pin
    mathutils.Vector((-35.0, 10, -5)),   
    mathutils.Vector((-34.0, 0.0, -3.5)),   # Continuing south down the western flank
    mathutils.Vector((-32.0, -11.0, -2.5)), # Passing perfectly west of your center origin dot
    mathutils.Vector((-29.0, -26.0, -2.0)),  # Winding lower down the western track
    mathutils.Vector((-24.0, -38.0, -0.5)),  # Straightening south toward the bottom turn
    mathutils.Vector((-20.0, -45.0, 2.0)),   # Sweeping around the bottom bend (crossing X axis)
    mathutils.Vector((-12.0, -46.0, 2.5))    # Terminating near the bottom right building clearing
]

path_points_AMD_ROW = [
    mathutils.Vector((32.0, 110.0, -22.1)),  
    mathutils.Vector((1.0, 80.0, -13.5)),  
    mathutils.Vector((-35.0, 50.0, -10.5))   
]

create_sloping_driveway(name="Main_Driveway", width=4.0, thickness=0.15, path_points=path_points_main_drive, debug_show_points=True)
create_sloping_driveway(name="AMD_ROW", width=6.0, thickness=0.25, path_points=path_points_AMD_ROW, debug_show_points=True)

outdoor_structures.create_beech_trunk( name="beech_tree", location=(-1.6, -11.1, 4), radius=0.4, height=7.0 )  
outdoor_structures.create_beech_trunk( name="beech_tree2", location=(-14, 4, 2), radius=0.4, height=7.0 )  
outdoor_structures.create_beech_trunk( name="beech_tree3", location=(-14.5, -6.7, 2.5), radius=0.4, height=7.0 )  

print("Modular Site Build Complete.")