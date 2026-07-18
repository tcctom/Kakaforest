from click import option

import bpy  # type: ignore
import addon_utils
import sys
import os
import mathutils
import math # Needed for the rotation correction

from importlib import reload

option = 3

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

def setup_nz_sun_and_sky(latitude=-41.783213855839, longitude=172.92023483494785, month=6, day=21, time=12.0, use_cycles=False):
    """
    Sets up a geographically accurate sun and sky.
    use_cycles=False (Default): Incredibly fast, zero lag for drafting/coding.
    use_cycles=True: Slow, grainy preview, but photo-realistic for final renders.
    """
    world = bpy.context.scene.world
    world.use_nodes = True
    node_tree = world.node_tree
    nodes = node_tree.nodes
    nodes.clear() 

    node_sky = nodes.new(type='ShaderNodeTexSky')
    node_bg = nodes.new(type='ShaderNodeBackground')
    node_output = nodes.new(type='ShaderNodeOutputWorld')
    
    node_tree.links.new(node_sky.outputs['Color'], node_bg.inputs['Color'])
    node_tree.links.new(node_bg.outputs['Background'], node_output.inputs['Surface'])

    if use_cycles:
        # High quality realism mode
        bpy.context.scene.render.engine = 'CYCLES'
        node_sky.sky_type = 'MULTIPLE_SCATTERING'
    else:
        # Fast drafting mode (Zero lag, no grain in Blender 5.x)
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        node_sky.sky_type = 'HOSEK_WILKIE'
        
    node_sky.sun_disc = True
    
    node_bg = nodes.new(type='ShaderNodeBackground')
    node_output = nodes.new(type='ShaderNodeOutputWorld')
    
    node_tree.links.new(node_sky.outputs['Color'], node_bg.inputs['Color'])
    node_tree.links.new(node_bg.outputs['Background'], node_output.inputs['Surface'])
    
    # 3. Create or grab the Sun Light object
    if "NZ_Sun" in bpy.data.objects:
        sun_obj = bpy.data.objects["NZ_Sun"]
    else:
        sun_data = bpy.data.lights.new(name="NZ_Sun", type='SUN')
        sun_data.energy = 5.0  
        sun_obj = bpy.data.objects.new(name="NZ_Sun", object_data=sun_data)
        bpy.context.collection.objects.link(sun_obj)

    # 4. NATIVE SOLAR GEOMETRY MATH (Bypasses the Add-on entirely)
    # Convert degrees to radians for math operations
    lat_rad = math.radians(latitude)
    
    # Calculate Day of the Year
    days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_of_year = sum(days_in_months[:month-1]) + day
    
    # Solar Declination Angle (Earth's tilt relative to the sun)
    # 284 is the offset from the winter solstice
    declination = math.radians(23.45 * math.sin(math.radians((360.0 / 365.0) * (284 + day_of_year))))
    
    # Solar Hour Angle (15 degrees of rotation per hour relative to solar noon)
    # Standard NZ Time Zone is UTC+12. solar_noon is approximated.
    hour_angle = math.radians((time - 12.0) * 15.0)
    
    # Calculate Solar Elevation (Altitude) Angle
    sin_elevation = (math.sin(lat_rad) * math.sin(declination) + 
                     math.cos(lat_rad) * math.cos(declination) * math.cos(hour_angle))
    elevation = math.asin(max(-1.0, min(1.0, sin_elevation))) # Clamp to safe ranges
    
    # Calculate Solar Azimuth Angle (Compass direction)
    cos_azimuth = ((math.sin(declination) - math.sin(lat_rad) * math.sin(elevation)) / 
                   (math.cos(lat_rad) * math.cos(elevation)))
    cos_azimuth = max(-1.0, min(1.0, cos_azimuth)) # Clamp
    
    # Adjust azimuth quadrant based on afternoon vs morning hours
    if hour_angle > 0:
        azimuth = (2.0 * math.pi) - math.acos(cos_azimuth)
    else:
        azimuth = math.acos(cos_azimuth)

    # 5. Apply calculation results to the Sky Texture Node
    node_sky.sun_elevation = elevation
    node_sky.sun_rotation = azimuth
    
    # 6. Apply calculation results to our actual Sun Light object
    sun_obj.rotation_mode = 'XYZ'
    sun_obj.rotation_euler[0] = (math.pi / 2.0) - elevation
    sun_obj.rotation_euler[1] = 0.0
    sun_obj.rotation_euler[2] = azimuth + math.pi

    print(f"Sun successfully positioned mathematically:")
    print(f" -> Azimuth: {math.degrees(azimuth):.2f}°")
    print(f" -> Elevation: {math.degrees(elevation):.2f}°")

def setup_nz_sun_and_sky2(
    latitude=-41.783213855839,
    longitude=172.92023483494785,
    month=6,
    day=21,
    time=12.0,
    use_cycles=False,
    show_debug_sun=True,
):
    """
    New Zealand Sun & Sky for Blender 5.1
    Fixed: Vector-aligned rotation using explicit ENU Map coordinates.
    """

    scene = bpy.context.scene

    # --------------------------------------------------
    # WORLD SETUP
    # --------------------------------------------------
    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        scene.world = world

    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    sky = nt.nodes.new("ShaderNodeTexSky")
    bg = nt.nodes.new("ShaderNodeBackground")
    output = nt.nodes.new("ShaderNodeOutputWorld")

    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], output.inputs["Surface"])

    if use_cycles:
        scene.render.engine = 'CYCLES'
        sky.sky_type = 'MULTIPLE_SCATTERING'
    else:
        scene.render.engine = 'BLENDER_EEVEE'
        sky.sky_type = 'HOSEK_WILKIE'

    sky.sun_disc = True
    bg.inputs["Strength"].default_value = 1.0

    # --------------------------------------------------
    # SUN OBJECT SETUP
    # --------------------------------------------------
    if "NZ_Sun" in bpy.data.objects:
        sun_obj = bpy.data.objects["NZ_Sun"]
    else:
        sun_data = bpy.data.lights.new(name="NZ_Sun", type='SUN')
        sun_obj = bpy.data.objects.new(name="NZ_Sun", object_data=sun_data)
        bpy.context.collection.objects.link(sun_obj)

    sun_obj.data.energy = 5.0
    sun_obj.data.angle = math.radians(0.53)
    sun_obj.data.use_shadow = True

    # --------------------------------------------------
    # CORE ASTRONOMY MATH
    # --------------------------------------------------
    days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_of_year = sum(days_in_months[:month - 1]) + day
    lat_rad = math.radians(latitude)

    declination = math.radians(
        23.45 * math.sin(math.radians((360.0 / 365.0) * (284 + day_of_year)))
    )
    hour_angle = math.radians((time - 12.0) * 15.0)

    # Calculate Elevation (Altitude)
    sin_elev = (
        math.sin(lat_rad) * math.sin(declination) +
        math.cos(lat_rad) * math.cos(declination) * math.cos(hour_angle)
    )
    sin_elev = max(-1.0, min(1.0, sin_elev))
    elevation = math.asin(sin_elev)

    # Calculate Azimuth relative to the horizon
    y = math.sin(hour_angle)
    x = (
        math.cos(hour_angle) * math.sin(lat_rad)
        - math.tan(declination) * math.cos(lat_rad)
    )
    azimuth = math.atan2(y, x)
    azimuth = (azimuth + math.pi) % (2.0 * math.pi)

    # --------------------------------------------------
    # GENERATE PERFECT DIRECTORY VECTORS (ENU to Blender XYZ)
    # --------------------------------------------------
    east = math.cos(elevation) * math.sin(azimuth)
    north = math.cos(elevation) * math.cos(azimuth)
    up = math.sin(elevation)

    # --------------------------------------------------
    # SYNC RENDER ENGINES (Sky Node & Sun Lamp)
    # --------------------------------------------------
    # Match the Sky Texture node to your map layout (Counter-clockwise from East)
    sky.sun_elevation = elevation
    sky.sun_rotation = math.atan2(north, east)

    # Create the sun direction vector pointing to the sky
    sun_vector = mathutils.Vector((east, north, up))

    # CRITICAL FIX: To make the lamp shine DOWN from the sky, we track the INVERSE vector (-sun_vector).
    # This forces the light beam to travel Southwest towards the origin, matching a 9AM morning.
    tracking_rotation = (-sun_vector).to_track_quat('-Z', 'Y')
    
    sun_obj.rotation_mode = 'XYZ'
    sun_obj.rotation_euler = tracking_rotation.to_euler()

    # --------------------------------------------------
    # VISUAL DEBUG SUN SPHERE
    # --------------------------------------------------
    if show_debug_sun:
        if "NZ_DebugSun" not in bpy.data.objects:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=20)
            debug_sun = bpy.context.active_object
            debug_sun.name = "NZ_DebugSun"

            mat = bpy.data.materials.new("NZ_DebugSun_Mat")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Emission Strength"].default_value = 50.0
            debug_sun.data.materials.append(mat)
        else:
            debug_sun = bpy.data.objects["NZ_DebugSun"]

        if hasattr(debug_sun, "visible_shadow"):
            debug_sun.visible_shadow = False

        distance = 20000.0
        debug_sun.location = (east * distance, north * distance, up * distance)

    # --------------------------------------------------
    # EEVEE-NEXT SHADOW TWEAKS
    # --------------------------------------------------
    if scene.render.engine == 'BLENDER_EEVEE' and hasattr(scene, "eevee"):
        try:
            scene.eevee.use_shadows = True
        except:
            pass

    # --------------------------------------------------
    # DIAGNOSTIC LOGGING
    # --------------------------------------------------
    print("\n========== NZ SUN VECTOR DEBUG ==========")
    print(f"Time: {time:.2f} | Elevation: {math.degrees(elevation):.2f}°")
    print(f"Target Vector (To Sun):  X(East)={east:.3f}, Y(North)={north:.3f}, Z(Up)={up:.3f}")
    print(f"Light Trajectory (Rays): X={-east:.3f}, Y={-north:.3f}, Z={-up:.3f}")
    print("=========================================\n")

    return sun_obj
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
    """Create a prism cutter from the footprint of contour points."""
    def _cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    xy_points = sorted({(p[0], p[1]) for p in contour_points})
    if len(xy_points) < 3:
        raise ValueError("Need at least 3 unique XY points to build excavation cutter")

    lower = []
    for pt in xy_points:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], pt) <= 0:
            lower.pop()
        lower.append(pt)

    upper = []
    for pt in reversed(xy_points):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], pt) <= 0:
            upper.pop()
        upper.append(pt)

    hull = lower[:-1] + upper[:-1]
    if len(hull) < 3:
        raise ValueError("Computed cutter footprint is degenerate")

    z_top = max([p[2] for p in contour_points])
    z_other = z_top - depth
    z_min = min(z_top, z_other)
    z_max = max(z_top, z_other)

    bottom_verts = [(x, y, z_min) for x, y in hull]
    top_verts = [(x, y, z_max) for x, y in hull]
    verts = bottom_verts + top_verts

    n = len(hull)
    faces = []

    faces.append(tuple(range(n)))
    faces.append(tuple(range(2 * n - 1, n - 1, -1)))

    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    cutter_obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(cutter_obj)
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Hide it from view and render so it's just an invisible cutting tool
    cutter_obj.hide_viewport = True
    cutter_obj.hide_render = True
    
    return cutter_obj

def excavate_area(
    linz_terrain,
    corner_a,
    corner_b,
    z=-0.2,
    x_spacing=0.4,
    depth=2.0,
    modifier_name="Excavation",
    cutter_name="Excavation_Cutter",
    create_gravel=True,
):
    """Create a rectangular clearing and apply it as a Boolean excavation on terrain."""
    clearing = ground_module.grid_points(
        (corner_a[0], corner_a[1], z),
        (corner_b[0], corner_b[1], z),
        x_spacing=x_spacing,
    )

    gravel_pad = None
    if create_gravel:
        gravel_pad = ground_module.gravel_plane(clearing)

    cutter = create_excavation_cutter(clearing, depth=depth, name=cutter_name)

    bool_mod = linz_terrain.modifiers.new(name=modifier_name, type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter
    bool_mod.solver = 'EXACT'  # Stable for dense terrain topology

    return clearing, gravel_pad, cutter, bool_mod

import bmesh
def excavate_strip(
    linz_terrain,
    start_xy,
    end_xy,
    width,
    z=-0.2,
    depth=-2.0,
    modifier_name="Strip_Excavation",
    cutter_name="Strip_Excavation_Cutter",
):
    """Create a diagonal strip cutter using a centerline and width."""
    sx, sy = start_xy
    ex, ey = end_xy
    dx = ex - sx
    dy = ey - sy
    length = (dx * dx + dy * dy) ** 0.5
    if length == 0:
        raise ValueError("start_xy and end_xy must be different points")

    ux = dx / length
    uy = dy / length
    px = -uy
    py = ux
    half_w = width * 0.5

    strip_outline = [
        (sx + px * half_w, sy + py * half_w, z),
        (ex + px * half_w, ey + py * half_w, z),
        (ex - px * half_w, ey - py * half_w, z),
        (sx - px * half_w, sy - py * half_w, z),
    ]

    cutter = create_excavation_cutter(strip_outline, depth=depth, name=cutter_name)

    # --- FORCE NORMALS OUTWARD ---
    bm = bmesh.new()
    bm.from_mesh(cutter.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces) 
    bm.to_mesh(cutter.data)
    bm.free()
    cutter.data.update()
    # -----------------------------

    bool_mod = linz_terrain.modifiers.new(name=modifier_name, type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter
    bool_mod.solver = 'EXACT'  # Use ... for long strips to avoid precision issues

    return strip_outline, cutter, bool_mod




cleanup()

# Set geographically accurate NZ Sky and Sun
# note, long and lat default to bach
# Setting it to March 20th at 4:30 PM (16.5) for long afternoon autumn shadows
#setup_nz_sun_and_sky( month=6, day=21, time=12.0, use_cycles=False)

setup_nz_sun_and_sky2(    month=1,    day=21,    time=9)
#setup_nz_sun_and_sky2(    month=12,    day=21,    time=11)
#setup_nz_sun_and_sky2(    month=12,    day=21,    time=12)
#setup_nz_sun_and_sky2(    month=6,    day=21,    time=15)

# Paths to your external asset files
terrain_obj_path = os.path.abspath("Terrain/terrain.obj")

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
    # Main dwelling clearing with gravel finish.
    clearing, gravel_pad, cutter, bool_mod = excavate_area(
        linz_terrain=linz_terrain,
        corner_a=(6, 3.0),
        corner_b=(-4.5, -8.5),
        z=-0.2,
        x_spacing=0.4,
        depth=-2.0,
        modifier_name="Dwelling_Excavation",
        cutter_name="Dwelling_Excavation_Cutter",
        create_gravel=True,
    )

    # Next area to cut out: same workflow, one function call.
    clearing2, gravel_pad2, cutter2, bool_mod2 = excavate_area(
        linz_terrain=linz_terrain,
        corner_a=(-4.0, -5.0),
        corner_b=(-10.0, -8.5),
        z=-0.2,
        x_spacing=0.4,
        depth=-2.0,
        modifier_name="Secondary_Excavation",
        cutter_name="Secondary_Excavation_Cutter",
        create_gravel=False,
    )

    # Optional diagonal strip cut (centerline start/end + width in meters).
    strip_outline, strip_cutter, strip_bool = excavate_strip(
         linz_terrain=linz_terrain,
         start_xy=(-3.50, -6.5),
         end_xy=(-26.0, -20.0),
         width=4.4999,  # Just under 3.5m to avoid boolean precision issues
         z=-0.2,
         depth=-2.0,
         modifier_name="Diagonal_Strip_Excavation",
         cutter_name="Diagonal_Strip_Cutter",
    )
    

# 1. Build existing cottage (60m south of main dwelling, 5m higher elevation)
# Set show_roof=False to hide roof for interior viewing
#björken_module.build_red_cottage(origin=(24, -56, 8.0))

# 1c. Pavers extending east from cottage
#outdoor_structures.build_pavers_east(origin=(27, -56, -7.55))


# 1a. Build Main Dwelling
# Now located at origin (0, 0, 0)
# This is the new two-story 6m × 8m main dwelling structure
# Roof options: 
#   - "traditional": Overhang on all sides, separate gable end triangles
#   - "flush": Flush with all walls, north side extends 1m down for balcony shading
foundation = ground_module.gravel_plane(ground_module.grid_points((5.0, 2.8, 0.2), (-4.5, -4.6, 0.2)),thickness=0.4)
main_dwelling_module.build_main_dwelling_simple_porch(origin=(0, -1, 0.2), show_roof=True, roof_style="flush", option=option)

# 1a. Build North Deck - extends 3m north from ground floor
main_dwelling_module.build_north_deck(origin=(0, -1, 0.2))

# 1b. Build boulder row along south edge of clearing
#outdoor_structures.build_boulder_row(start_pos=(5, -7.8, 0), end_pos=(-5, -7.8, 0), spacing=0.4)
# and north and south of porch
#outdoor_structures.create_single_boulder(position=(-6.5, 2.2, -0.4), base_size=1.0)
#outdoor_structures.create_single_boulder(position=(-6.5, 1.6, -0.4), base_size=0.9)
#outdoor_structures.create_single_boulder(position=(-6.5, -1.9, -0.4), base_size=0.9)



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
outdoor_structures.build_water_tank(origin=(-14.5, -13, -0.2))
outdoor_structures.build_water_tank(origin=(-18.0, -15, -0.2))

#https://www.devan.co.nz/shop/tanks/water-tanks-above/4000-ltr-tank-2/
#outdoor_structures.build_water_tank(origin=(-3.0, -4.5, -0.0), diameter=1.7, height=1.8)

#https://www.devan.co.nz/shop/tanks/water-tanks-above/1000-ltr-tank-2/
if option == 1:
    outdoor_structures.build_water_tank(origin=(-2.0, -5.1, -0.0), diameter=0.9, height=2.0)
if option == 2:
    outdoor_structures.build_water_tank(origin=(2.6, -5.1, -0.0), diameter=0.9, height=2.0)
if option == 3:
    outdoor_structures.build_water_tank(origin=(3.1, -5.1, -0.0), diameter=0.9, height=2.0)

path_points_1 = [
        mathutils.Vector((4.5, -6.5, 0.1)),       
        mathutils.Vector((-3.0, -6.5, 0.1)),       
        mathutils.Vector((-7.9, -6.2, -0.15)),       
        mathutils.Vector((-12, -2.4, -1.2)),       
        mathutils.Vector((-17, -1.9, -1.7)),       
        mathutils.Vector((-20, -2.5, -1.8)), 
        mathutils.Vector((-22, -3, -1.9)), 
        mathutils.Vector((-25, -4, -2.25)), 
        mathutils.Vector((-26, -6, -2.25)), 
        mathutils.Vector((-27.0, -8, -2.6)), 
        mathutils.Vector((-29.0, -10, -2.8)), 
        mathutils.Vector((-31.0, -10.0, -3.0))
    ]


from driveway import create_sloping_driveway  
create_sloping_driveway(name="Main_Drivewayv1", width=3.3, thickness=0.2, path_points=path_points_1, debug_show_points=True)

#Would you be able to analyse the attached image and give me a set of path points in meters? 
#Just the x, y is fine (put z to 0 on all). the red dot just north of center is the origin. North of that is plus Y and east of that is plus X. 
#Can you also see the 10 meter scale bottom right?

# The origin (0, 0, 0) is the red dot north of center
path_points_main_drive = [
    mathutils.Vector((-33.5, 50.0, -10.5)),   # Top entrance at the public road boundary
    mathutils.Vector((-36, 35.0, -8.5)),   # Heading straight south along the top ridge
    mathutils.Vector((-36.5, 20.0, -6.7)),   # Shifting slightly west past the northern red pin
    mathutils.Vector((-35.5, 10, -5.1)),   
    mathutils.Vector((-34.0, 0.0, -4.2)),   # Continuing south down the western flank
    mathutils.Vector((-32.0, -11.0, -2.9)), # Passing perfectly west of your center origin dot
    mathutils.Vector((-31.0, -18.5, -2.4)),  # Winding lower down the western track
    mathutils.Vector((-29.0, -26.0, -2.0)),  # Winding lower down the western track
    mathutils.Vector((-25.0, -38.0, -0.5)),  # Straightening south toward the bottom turn
    mathutils.Vector((-21.0, -45.0, 1.0)),   # Sweeping around the bottom bend (crossing X axis)
    mathutils.Vector((-17.5, -50.0, 2.0)),    
    mathutils.Vector((-13, -55.0, 3.0)),    
    mathutils.Vector((-6.0, -58.0, 4.6)),
    mathutils.Vector((-1.0, -57.5, 5.5)),
    mathutils.Vector((2, -57.0, 5.9)),
    mathutils.Vector((10, -55.5, 6.3)),
    mathutils.Vector((14, -54.0, 6.3))     # Terminating near the bottom right building clearing

]

path_points_AMD_ROW = [
    mathutils.Vector((32.0, 111.5, -22.1)),  
    mathutils.Vector((1.0, 81.0, -14.0)),  
    mathutils.Vector((-35.0, 50.0, -10.5)),  
    mathutils.Vector((-41.0, 46.0, -10.0))     
]

create_sloping_driveway(name="Main_Driveway", width=4.0, thickness=0.2, path_points=path_points_main_drive, debug_show_points=True)
create_sloping_driveway(name="AMD_ROW", width=6.0, thickness=0.25, path_points=path_points_AMD_ROW, debug_show_points=True)

outdoor_structures.create_beech_trunk( name="beech_tree", location=(-1.8, -11.2, 4), radius=0.25, height=7.0 )  
outdoor_structures.create_beech_trunk( name="beech_tree2", location=(-14, 4, 1.6), radius=0.25, height=7.0 )  
outdoor_structures.create_beech_trunk( name="beech_tree3", location=(-14.8, -7.2, 2.1), radius=0.25, height=7.0 )  

print("Modular Site Build Complete.")