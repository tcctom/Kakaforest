import bpy  # type: ignore
import math

from utils import apply_shadowclad_grooves, add_window, create_corrugated_iron_material, add_corner_trim
from materials import get_interior_wall_material, get_floor_wood_material, get_metal_roof_material, get_kitchen_bench_material, get_kitchen_cabinet_material

def create_material(name, color):
    """Create or get a material with the given name and color"""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat


def create_textured_material(name, texture_path):
    """Create or get a material with an image texture"""
    mat = bpy.data.materials.get(name)
    if mat:
        print(f"DEBUG: Material '{name}' already exists, returning cached version")
        return mat
    
    print(f"DEBUG: Creating new material '{name}' with texture: {texture_path}")
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Get the Principled BSDF node
    principled = nodes.get("Principled BSDF")
    
    # Create Image Texture node
    tex_image = nodes.new(type='ShaderNodeTexImage')
    tex_image.location = (-300, 300)
    
    # Load the image
    try:
        img = bpy.data.images.load(texture_path)
        tex_image.image = img
        tex_image.image.colorspace_settings.name = 'sRGB'  # Ensure proper color space
    except Exception as e:
        print(f"WARNING: Could not load texture: {texture_path}, Error: {e}")
    
    # Add Mapping node for rotation control
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-600, 300)
    mapping.inputs['Rotation'].default_value[2] = math.radians(90)  # Rotate 90° on Z-axis
    # Scale for ~150mm grooves with Generated coordinates
    mapping.inputs['Scale'].default_value = (3.2, 3.2, 3.2)
    
    # Add Texture Coordinate node
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-800, 300)
    
    # Connect nodes: TexCoord -> Mapping -> Image Texture -> Principled BSDF
    # Use 'Generated' coordinates which work for both cubes and custom geometry
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
    links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
    
    # Adjust material properties for better wood appearance
    principled.inputs['Roughness'].default_value = 0.7  # Natural wood finish
    
    return mat


def create_laminate_floor_material():
    """Create or get laminate floor material with texture for top surfaces"""
    mat = bpy.data.materials.get("LaminateFloor")
    if mat:
        print(f"DEBUG: Material 'LaminateFloor' already exists, returning cached version")
        return mat
    
    import os
    texture_path = os.path.join(os.path.dirname(__file__), "textures", "laminate_floor_02", "laminate_floor_02_diff_1k.jpg")
    
    print(f"DEBUG: Creating new material 'LaminateFloor' with texture: {texture_path}")
    mat = bpy.data.materials.new(name="LaminateFloor")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Get the Principled BSDF node
    principled = nodes.get("Principled BSDF")
    
    # Create Image Texture node
    tex_image = nodes.new(type='ShaderNodeTexImage')
    tex_image.location = (-300, 300)
    
    # Load the image
    try:
        img = bpy.data.images.load(texture_path)
        tex_image.image = img
        tex_image.image.colorspace_settings.name = 'sRGB'
    except Exception as e:
        print(f"WARNING: Could not load laminate floor texture: {texture_path}, Error: {e}")
    
    # Add Mapping node for scale control (no rotation for floors)
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-600, 300)
    # Scale appropriately for floor planks
    mapping.inputs['Scale'].default_value = (2.0, 2.0, 2.0)
    
    # Add Texture Coordinate node
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-800, 300)
    
    # Connect nodes: TexCoord -> Mapping -> Image Texture -> Principled BSDF
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
    links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
    
    # Adjust material properties for laminate floor
    principled.inputs['Roughness'].default_value = 0.4  # Slightly glossy laminate finish
    
    return mat


# === HELPER FUNCTIONS FOR MAIN DWELLING ===

def _create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat):
    """Create all exterior walls for ground and first floors with recessed north wall"""
    wall_depth_ground = ENCLOSED_WIDTH - 2*EXTERIOR_WALL_THICKNESS
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    
    # Interior wall material for interior faces
    interior_wall_mat = get_interior_wall_material()
    
    # === GROUND FLOOR EXTERIOR WALLS ===
    # North Wall (recessed NORTH_RECESS inward from north edge)
    # North edge is at oy + WIDTH/2, recess by NORTH_RECESS, position at outer face minus half thickness
    north_wall_y = oy + WIDTH/2 - NORTH_RECESS + EXTERIOR_WALL_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(ox, north_wall_y, oz + GROUND_FLOOR_HEIGHT/2))
    north_wall_ground = bpy.context.active_object
    north_wall_ground.name = "MainDwelling_NorthWall_Ground"
    north_wall_ground.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    north_wall_ground.data.materials.append(potius_mat)
    north_wall_ground.data.materials.append(interior_wall_mat)
    # Assign interior material to south face (index 3)
    north_wall_ground.data.polygons[3].material_index = 1
    
    # South Wall (extends to full WIDTH)
    south_wall_y = oy - WIDTH/2 + EXTERIOR_WALL_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(ox, south_wall_y, oz + GROUND_FLOOR_HEIGHT/2))
    south_wall_ground = bpy.context.active_object
    south_wall_ground.name = "MainDwelling_SouthWall_Ground"
    south_wall_ground.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    south_wall_ground.data.materials.append(potius_mat)
    south_wall_ground.data.materials.append(interior_wall_mat)
    # Assign interior material to north face (index 1)
    south_wall_ground.data.polygons[1].material_index = 1
    
    # East Wall (spans FULL 7m north-south, flush with floors and roof)
    east_west_wall_depth = WIDTH  # Full 7m span to match floor/roof edges
    bpy.ops.mesh.primitive_cube_add(location=(ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS/2, oy, oz + GROUND_FLOOR_HEIGHT/2))
    east_wall_ground = bpy.context.active_object
    east_wall_ground.name = "MainDwelling_EastWall_Ground"
    east_wall_ground.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    east_wall_ground.data.materials.append(potius_mat)
    east_wall_ground.data.materials.append(interior_wall_mat)
    # Assign interior material to west face (index 0)
    east_wall_ground.data.polygons[0].material_index = 1
    
    # West Wall (spans FULL 7m north-south, flush with floors and roof)
    bpy.ops.mesh.primitive_cube_add(location=(ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS/2, oy, oz + GROUND_FLOOR_HEIGHT/2))
    west_wall_ground = bpy.context.active_object
    west_wall_ground.name = "MainDwelling_WestWall_Ground"
    west_wall_ground.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    west_wall_ground.data.materials.append(potius_mat)
    west_wall_ground.data.materials.append(interior_wall_mat)
    # Assign interior material to east face (index 2)
    west_wall_ground.data.polygons[2].material_index = 1
    
    # === FIRST FLOOR EXTERIOR WALLS ===
    # North Wall (recessed, same as ground floor)
    bpy.ops.mesh.primitive_cube_add(location=(ox, north_wall_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    north_wall_first = bpy.context.active_object
    north_wall_first.name = "MainDwelling_NorthWall_First"
    north_wall_first.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    north_wall_first.data.materials.append(potius_mat)
    north_wall_first.data.materials.append(interior_wall_mat)
    # Assign interior material to south face (index 3)
    north_wall_first.data.polygons[3].material_index = 1
    
    # South Wall (extends to full WIDTH)
    bpy.ops.mesh.primitive_cube_add(location=(ox, south_wall_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    south_wall_first = bpy.context.active_object
    south_wall_first.name = "MainDwelling_SouthWall_First"
    south_wall_first.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    south_wall_first.data.materials.append(potius_mat)
    south_wall_first.data.materials.append(interior_wall_mat)
    # Assign interior material to north face (index 1)
    south_wall_first.data.polygons[1].material_index = 1
    
    # East Wall (spans FULL 7m north-south, independent of recessed north wall)
    bpy.ops.mesh.primitive_cube_add(location=(ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS/2, oy, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    east_wall_first = bpy.context.active_object
    east_wall_first.name = "MainDwelling_EastWall_First"
    east_wall_first.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    east_wall_first.data.materials.append(potius_mat)
    east_wall_first.data.materials.append(interior_wall_mat)
    # Assign interior material to west face (index 0)
    east_wall_first.data.polygons[0].material_index = 1
    
    # West Wall (spans FULL 7m north-south, independent of recessed north wall)
    bpy.ops.mesh.primitive_cube_add(location=(ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS/2, oy, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    west_wall_first = bpy.context.active_object
    west_wall_first.name = "MainDwelling_WestWall_First"
    west_wall_first.scale = (EXTERIOR_WALL_THICKNESS/2, east_west_wall_depth/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    # Add both materials (exterior and interior)
    west_wall_first.data.materials.append(potius_mat)
    west_wall_first.data.materials.append(interior_wall_mat)
    # Assign interior material to east face (index 2)
    west_wall_first.data.polygons[2].material_index = 1


def _create_180_degree_staircase_southwest(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, first_floor_slab, floor_mat):
    """Create 180-degree dog-legged staircase in southwest corner with clockwise turn
    
    Spatial Configuration:
    - Location: Southwest corner of floor plan
    - Type: 180-degree half-turn (dog-leg) with clockwise ascent
    - Stairwell footprint: ~2000mm (E-W) × 3000mm (N-S)
    - Flight 1: Starts at NORTH edge, travels SOUTH along EAST edge → Landing
    - Landing: 2000mm wide × 1000mm deep at SOUTH edge, spans East-West
    - Flight 2: Starts at landing, turns 180° clockwise, travels NORTH along WEST edge → Upper floor
    
    Args:
        ox, oy, oz: Origin coordinates (building center)
        WIDTH: Total building width (7m N-S)
        LENGTH: Total building length (9m E-W)
        GROUND_FLOOR_HEIGHT: Ground floor height (2.5m)
        EXTERIOR_WALL_THICKNESS: Wall thickness (0.2m)
        first_floor_slab: First floor slab object for boolean cut
        floor_mat: Material for landing
    """
    # Constants
    TOTAL_RISE = 2.7  # 2700mm (ground floor height + first floor thickness)
    STAIRWELL_WIDTH = 2.0  # 2000mm E-W
    STAIRWELL_LENGTH = 3.0  # 3000mm N-S
    FLIGHT_WIDTH = 0.9  # 900mm per flight
    CENTRAL_GAP = 0.2  # 200mm between flights
    LANDING_DEPTH = 1.0  # 1000mm N-S
    
    # Step dimensions
    STEPS_PER_FLIGHT = 7
    STEP_RISE = TOTAL_RISE / (STEPS_PER_FLIGHT * 2)  # 192.86mm
    STEP_TREAD = 0.285  # 285mm (code compliant: 250-300mm range)
    
    # Landing height (mid-point)
    LANDING_HEIGHT = TOTAL_RISE / 2  # 1.35m
    
    # Southwest corner interior reference (oz is ground level)
    west_interior_x = ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS
    south_interior_y = oy - WIDTH/2 + EXTERIOR_WALL_THICKNESS
    
    # Stairwell boundaries in SW corner
    stairwell_west_x = west_interior_x
    stairwell_east_x = west_interior_x + STAIRWELL_WIDTH
    stairwell_south_y = south_interior_y
    stairwell_north_y = south_interior_y + STAIRWELL_LENGTH
    
    # Materials
    stairs_mat = create_material("StairsWood", (0.6, 0.4, 0.25, 1))
    landing_mat = floor_mat
    
    # === FLIGHT 1: Ground to Landing (SOUTH along EAST edge) ===
    # Starts at NORTH edge, travels SOUTH
    flight1_x = stairwell_east_x - FLIGHT_WIDTH/2 - 0.05  # East edge, 50mm from edge
    flight1_start_y = stairwell_north_y - STEP_TREAD/2 - 0.05  # Start from north
    
    for i in range(STEPS_PER_FLIGHT):
        step_height = oz + STEP_RISE * (i + 1)
        step_y = flight1_start_y - (i * STEP_TREAD)  # Move south (negative Y)
        
        bpy.ops.mesh.primitive_cube_add(location=(flight1_x, step_y, step_height))
        step = bpy.context.active_object
        step.name = f"MainDwelling_Stairs_Flight1_Step_{i+1:02d}"
        step.scale = (FLIGHT_WIDTH/2, STEP_TREAD/2, STEP_RISE/2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stairs_mat)
    
    # === LANDING: At SOUTH edge, spans East-West ===
    landing_x = (stairwell_west_x + stairwell_east_x) / 2
    landing_y = stairwell_south_y + LANDING_DEPTH/2  # South edge
    # Landing top surface must align with top of step 7
    # Step 7 top = oz + 7*STEP_RISE + STEP_RISE/2 = oz + LANDING_HEIGHT + STEP_RISE/2
    # Landing thickness = 0.1m (scale 0.05 on 2m cube), so center = top - 0.05
    landing_z = oz + LANDING_HEIGHT + STEP_RISE/2 - 0.05
    
    bpy.ops.mesh.primitive_cube_add(location=(landing_x, landing_y, landing_z))
    landing = bpy.context.active_object
    landing.name = "MainDwelling_Stairs_Landing"
    landing.scale = (STAIRWELL_WIDTH/2, LANDING_DEPTH/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    landing.data.materials.append(landing_mat)
    
    # UV unwrap for texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # === FLIGHT 2: Landing to Upper Floor (NORTH along WEST edge, clockwise turn) ===
    # Starts at landing (south), travels NORTH
    flight2_x = stairwell_west_x + FLIGHT_WIDTH/2 + 0.05  # West edge, 50mm from wall
    flight2_start_y = stairwell_south_y + LANDING_DEPTH + STEP_TREAD/2  # Start from south end
    
    for i in range(STEPS_PER_FLIGHT):
        step_height = landing_z + STEP_RISE * (i + 1)
        step_y = flight2_start_y + (i * STEP_TREAD)  # Move north (positive Y)
        
        bpy.ops.mesh.primitive_cube_add(location=(flight2_x, step_y, step_height))
        step = bpy.context.active_object
        step.name = f"MainDwelling_Stairs_Flight2_Step_{i+1:02d}"
        step.scale = (FLIGHT_WIDTH/2, STEP_TREAD/2, STEP_RISE/2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stairs_mat)
    
    # === STAIRWELL OPENING in First Floor Slab ===
    # Opening encompasses Flight 2 and Landing
    opening_x = (stairwell_west_x + stairwell_east_x) / 2
    opening_y = stairwell_south_y + LANDING_DEPTH/2 + (STEPS_PER_FLIGHT * STEP_TREAD)/2
    opening_width = STAIRWELL_WIDTH + 0.1  # Add small margin
    opening_length = LANDING_DEPTH + (STEPS_PER_FLIGHT * STEP_TREAD) + 0.1
    
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    
    bpy.ops.mesh.primitive_cube_add(location=(opening_x, opening_y, first_floor_z + 0.1))
    stairwell_cutter = bpy.context.active_object
    stairwell_cutter.name = "MainDwelling_StairwellCutter_180deg"
    stairwell_cutter.scale = (opening_width/2, opening_length/2, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    
    # Boolean modifier to cut opening
    bool_mod = first_floor_slab.modifiers.new(name="Stairwell_Cut", type='BOOLEAN')
    bool_mod.object = stairwell_cutter
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.solver = 'EXACT'
    
    # Hide cutter
    stairwell_cutter.hide_viewport = True
    stairwell_cutter.hide_render = True
    
    print(f"180-degree staircase created in southwest corner")
    print(f"  Flight 1 (EAST edge): {STEPS_PER_FLIGHT} steps, North→South")
    print(f"  Landing (SOUTH edge): {LANDING_HEIGHT}m height, spans East-West")
    print(f"  Flight 2 (WEST edge): {STEPS_PER_FLIGHT} steps, South→North (clockwise)")
    print(f"  Stairwell footprint: {STAIRWELL_WIDTH}m × {STAIRWELL_LENGTH}m")
    print(f"  Step rise: {STEP_RISE*1000:.1f}mm, tread: {STEP_TREAD*1000:.0f}mm")


def _create_floors(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat):
    """Create ground floor and first floor slabs with laminate texture on top surfaces only"""
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    
    # Floor dimensions: fit within exterior walls (between interior faces)
    floor_length = LENGTH - 2 * EXTERIOR_WALL_THICKNESS  # East-west, inside walls
    # North-south: fit between south interior face and north interior face
    floor_width = WIDTH - EXTERIOR_WALL_THICKNESS  # Account for south wall thickness
    # Center the floor slightly north since south wall reduces the width
    floor_center_y = oy + EXTERIOR_WALL_THICKNESS/2
    
    # Create laminate floor material for top surfaces
    laminate_mat = create_laminate_floor_material()
    
    # Create white ceiling material for first floor underside
    white_ceiling_mat = create_material("WhiteCeiling", (1.0, 1.0, 1.0, 1.0))
    
    # === GROUND FLOOR ===
    bpy.ops.mesh.primitive_cube_add(location=(ox, floor_center_y, oz + 0.05))
    ground_floor = bpy.context.active_object
    ground_floor.name = "MainDwelling_GroundFloor"
    ground_floor.scale = (floor_length/2, floor_width/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    
    # Add both materials (default for sides/bottom, laminate for top)
    ground_floor.data.materials.append(floor_mat)  # Material slot 0 - default
    ground_floor.data.materials.append(laminate_mat)  # Material slot 1 - laminate
    
    # Assign laminate material to top face only
    # In Blender cube after scale: face index 5 is -Z(bottom), face index 4 is +Z(top)
    # But we need to check the normal direction - top face has positive Z normal
    for i, poly in enumerate(ground_floor.data.polygons):
        if poly.normal.z > 0.9:  # Top face (normal pointing up in +Z)
            poly.material_index = 1  # Laminate texture
            print(f"Ground floor: Assigned laminate to polygon {i} (top face)")
    
    # UV unwrap for texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # === FIRST FLOOR ===
    # 200mm thick with stairwell opening
    # Located so bottom is at first_floor_z and top is at first_floor_z + 0.2
    bpy.ops.mesh.primitive_cube_add(location=(ox, floor_center_y, first_floor_z + 0.1))
    first_floor_slab = bpy.context.active_object
    first_floor_slab.name = "MainDwelling_FirstFloor"
    first_floor_slab.scale = (floor_length/2, floor_width/2, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    
    # Add materials: default for sides, white for bottom (ceiling), laminate for top
    first_floor_slab.data.materials.append(floor_mat)  # Material slot 0 - default (sides)
    first_floor_slab.data.materials.append(laminate_mat)  # Material slot 1 - laminate (top)
    first_floor_slab.data.materials.append(white_ceiling_mat)  # Material slot 2 - white ceiling (bottom)
    
    # Assign materials based on normal direction
    for i, poly in enumerate(first_floor_slab.data.polygons):
        if poly.normal.z > 0.9:  # Top face (normal pointing up in +Z)
            poly.material_index = 1  # Laminate texture
            print(f"First floor: Assigned laminate to polygon {i} (top face)")
        elif poly.normal.z < -0.9:  # Bottom face (normal pointing down in -Z)
            poly.material_index = 2  # White ceiling
            print(f"First floor: Assigned white ceiling to polygon {i} (bottom face)")
    
    # UV unwrap for texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create 180-degree staircase in southwest corner
    _create_180_degree_staircase_southwest(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, 
                                            EXTERIOR_WALL_THICKNESS, first_floor_slab, floor_mat)


def _create_interior_partitions_ground_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Create ground floor interior partitions for guest bedroom with built-in wardrobe
    
    Args:
        WIDTH: Total building width (7m - full roof span)
        ENCLOSED_WIDTH: Enclosed building width (6m - north wall recessed)
        GROUND_FLOOR_HEIGHT: Height of ground floor (2.5m)
        FIRST_FLOOR_HEIGHT: Height of first floor (2.4m)
        NORTH_RECESS: Distance north wall is recessed from north edge (1m)
    """
    interior_wall_mat = get_interior_wall_material()
    
    # Guest bedroom in NE corner: 3.4m (E-W) × 3m (N-S)
    GUEST_BEDROOM_WIDTH = 3.4   # E-W dimension
    GUEST_BEDROOM_DEPTH = 3.0   # N-S dimension
    
    # Interior reference points (north wall recessed from north edge by NORTH_RECESS)
    east_interior_face = ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS
    north_interior_face = oy + WIDTH/2 - NORTH_RECESS
    
    # Ground floor wall height (slightly shorter to avoid poking through first floor slab)
    FLOOR_SLAB_THICKNESS = 0.1
    ground_floor_wall_height = GROUND_FLOOR_HEIGHT - FLOOR_SLAB_THICKNESS
    
    # West partition wall (N-S) - separates guest bedroom from rest of ground floor
    # Position so that east face of wall is exactly GUEST_BEDROOM_WIDTH from east interior face
    # Extended 500mm south beyond original GUEST_BEDROOM_DEPTH
    WEST_WALL_EXTENSION = 0.5  # Additional 500mm south
    west_partition_x = east_interior_face - GUEST_BEDROOM_WIDTH - INTERIOR_WALL_THICKNESS/2
    west_partition_center_y = north_interior_face - (GUEST_BEDROOM_DEPTH + WEST_WALL_EXTENSION)/2
    
    bpy.ops.mesh.primitive_cube_add(location=(west_partition_x, west_partition_center_y, oz + ground_floor_wall_height/2))
    west_partition = bpy.context.active_object
    west_partition.name = "MainDwelling_GroundFloor_GuestBedroomWestWall"
    west_partition.scale = (INTERIOR_WALL_THICKNESS/2, (GUEST_BEDROOM_DEPTH + WEST_WALL_EXTENSION)/2, ground_floor_wall_height/2)
    bpy.ops.object.transform_apply(scale=True)
    west_partition.data.materials.append(interior_wall_mat)
    
    # South partition wall (E-W) - southern edge of guest bedroom
    south_partition_y = north_interior_face - GUEST_BEDROOM_DEPTH + INTERIOR_WALL_THICKNESS/2
    south_partition_center_x = east_interior_face - GUEST_BEDROOM_WIDTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(south_partition_center_x, south_partition_y, oz + ground_floor_wall_height/2))
    south_partition = bpy.context.active_object
    south_partition.name = "MainDwelling_GroundFloor_GuestBedroomSouthWall"
    south_partition.scale = (GUEST_BEDROOM_WIDTH/2, INTERIOR_WALL_THICKNESS/2, ground_floor_wall_height/2)
    bpy.ops.object.transform_apply(scale=True)
    south_partition.data.materials.append(interior_wall_mat)
    
    # Door on south wall, positioned clear of wardrobe (wardrobe is on west side)
    # Place door about 1.5m from east wall
    door_x = east_interior_face - 2.9
    add_window("MainDwelling_GroundFloor_GuestBedroomSouthWall", (door_x, south_partition_y - INTERIOR_WALL_THICKNESS/2, oz + 1.0), 
               width=0.9, height=2.0, depth=INTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    
    # === CUPBOARD IN GUEST BEDROOM ===
    # Create a cupboard in NW corner of guest bedroom: 600mm (E-W) × 2000mm (N-S)
    CUPBOARD_WIDTH = 0.6    # E-W dimension (600mm)
    CUPBOARD_DEPTH = 2.0    # N-S dimension (2000mm)
    
    # West N-S partition of cupboard - 600mm west of guest bedroom west wall
    # Current west wall outer (west) face is at: west_partition_x - INTERIOR_WALL_THICKNESS/2
    # New wall center is 600mm west of that, plus half its thickness
    cupboard_west_wall_x = west_partition_x - INTERIOR_WALL_THICKNESS/2 - CUPBOARD_WIDTH - INTERIOR_WALL_THICKNESS/2
    cupboard_west_wall_center_y = north_interior_face - CUPBOARD_DEPTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(cupboard_west_wall_x, cupboard_west_wall_center_y, oz + ground_floor_wall_height/2))
    cupboard_west_wall = bpy.context.active_object
    cupboard_west_wall.name = "MainDwelling_GroundFloor_GuestBedroomCupboardWestWall"
    cupboard_west_wall.scale = (INTERIOR_WALL_THICKNESS/2, CUPBOARD_DEPTH/2, ground_floor_wall_height/2)
    bpy.ops.object.transform_apply(scale=True)
    cupboard_west_wall.data.materials.append(interior_wall_mat)
    
    # South E-W partition of cupboard - connects the two N-S walls at 2m from north wall
    cupboard_south_wall_y = north_interior_face - CUPBOARD_DEPTH + INTERIOR_WALL_THICKNESS/2
    cupboard_south_wall_center_x = west_partition_x - INTERIOR_WALL_THICKNESS/2 - CUPBOARD_WIDTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(cupboard_south_wall_center_x, cupboard_south_wall_y, oz + ground_floor_wall_height/2))
    cupboard_south_wall = bpy.context.active_object
    cupboard_south_wall.name = "MainDwelling_GroundFloor_GuestBedroomCupboardSouthWall"
    cupboard_south_wall.scale = (CUPBOARD_WIDTH/2, INTERIOR_WALL_THICKNESS/2, ground_floor_wall_height/2)
    bpy.ops.object.transform_apply(scale=True)
    cupboard_south_wall.data.materials.append(interior_wall_mat)
    
    # === KING BED IN GUEST BEDROOM ===
    # Same dimensions as master bedroom bed (1.8m wide × 2.0m long)
    BED_WIDTH = 1.8  # E-W dimension
    BED_LENGTH = 2.0  # N-S dimension
    BED_HEIGHT = 0.6  # Total height (base + mattress)
    
    bed_mat = create_material("BedFabric", (0.95, 0.95, 0.9, 1))
    
    # Position bed with headboard (pillow side) against south partition, centered E-W in bedroom
    guest_bed_x = east_interior_face - GUEST_BEDROOM_WIDTH/2
    guest_bed_y = south_partition_y + INTERIOR_WALL_THICKNESS/2 + BED_LENGTH/2
    guest_bed_z = oz + BED_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(guest_bed_x, guest_bed_y, guest_bed_z))
    guest_bed = bpy.context.active_object
    guest_bed.name = "MainDwelling_GuestBedroom_KingBed"
    guest_bed.scale = (BED_WIDTH/2, BED_LENGTH/2, BED_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    guest_bed.data.materials.append(bed_mat)
    
    # === PARTITION WALL EAST OF STAIRCASE ===
    # N-S wall immediately west of (actually east of) staircase footprint, 2.5m long from south wall
    # This partition extends through BOTH floors (ground + first floor)
    STAIRWELL_WIDTH = 2.0  # Staircase is 2m E-W
    PARTITION_LENGTH = 2.5  # 2.5m N-S dimension
    
    # Calculate positions (staircase is in SW corner)
    west_interior_x = ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS
    south_interior_y = oy - WIDTH/2 + EXTERIOR_WALL_THICKNESS
    
    # Staircase east edge is 2m east of west wall
    stairwell_east_x = west_interior_x + STAIRWELL_WIDTH
    
    # Position partition at east edge of stairwell (immediately west/adjacent to stairwell)
    partition_x = stairwell_east_x + INTERIOR_WALL_THICKNESS/2
    partition_center_y = south_interior_y + PARTITION_LENGTH/2
    
    # Full height partition extending through both floors
    full_partition_height = GROUND_FLOOR_HEIGHT + FIRST_FLOOR_HEIGHT
    
    bpy.ops.mesh.primitive_cube_add(location=(partition_x, partition_center_y, oz + full_partition_height/2))
    stair_partition = bpy.context.active_object
    stair_partition.name = "MainDwelling_StaircasePartition_BothFloors"
    stair_partition.scale = (INTERIOR_WALL_THICKNESS/2, PARTITION_LENGTH/2, full_partition_height/2)
    bpy.ops.object.transform_apply(scale=True)
    stair_partition.data.materials.append(interior_wall_mat)
    
    # === LOG BURNER AND FLUE (SOUTH OF GUEST BEDROOM CUPBOARD) ===
    # Position log burner south of cupboard, opening faces west
    LOG_BURNER_WIDTH = 0.5   # E-W dimension
    LOG_BURNER_DEPTH = 0.65  # N-S dimension  
    LOG_BURNER_HEIGHT = 0.7  # Height of main body
    LEG_HEIGHT = 0.15        # 150mm tall legs
    LEG_DIAMETER = 0.05      # 50mm diameter legs
    FLUE_DIAMETER = 0.15     # 150mm diameter flue pipe
    FLUE_HEIGHT = 6.8        # Extends through ground floor ceiling and first floor
    
    # Materials
    log_burner_mat = create_material("LogBurner", (0.1, 0.1, 0.1, 1))  # Dark metal
    flue_mat = create_material("FluePipe", (0.15, 0.15, 0.15, 1))      # Metal pipe
    granite_mat = get_kitchen_bench_material()  # Granite slab
    glass_mat = create_material("LogBurnerGlass", (0.1, 0.1, 0.1, 0.3))  # Dark tinted glass
    
    # Position: centered on cupboard E-W, 0.3m south of cupboard south wall
    cupboard_south_edge_y = north_interior_face - CUPBOARD_DEPTH
    log_burner_x = west_partition_x - INTERIOR_WALL_THICKNESS/2 - CUPBOARD_WIDTH/2 - 0.10
    log_burner_y = cupboard_south_edge_y - 0.8 - LOG_BURNER_DEPTH/2
    
    FLOOR_TOP = oz + 0.1  # Ground floor top surface (100mm thick slab)
    HEARTH_THICKNESS = 0.03  # 30mm thick
    log_burner_z = FLOOR_TOP + HEARTH_THICKNESS + LEG_HEIGHT + LOG_BURNER_HEIGHT/2  # Sits on hearth + legs
    
    # Granite hearth slab (larger than log burner footprint, extends to partition on north)
    HEARTH_WIDTH = LOG_BURNER_WIDTH + 0.4  # 200mm each side E-W
    # Calculate depth to extend from partition (north) to 200mm south of log burner (south)
    hearth_north_edge = cupboard_south_edge_y  # Butts against partition
    hearth_south_edge = log_burner_y + LOG_BURNER_DEPTH/2 + 0.2  # 200mm south of burner
    HEARTH_DEPTH = hearth_south_edge - hearth_north_edge
    hearth_y = (hearth_north_edge + hearth_south_edge) / 2  # Center of slab
    
    bpy.ops.mesh.primitive_cube_add(location=(log_burner_x, hearth_y, FLOOR_TOP + HEARTH_THICKNESS/2))
    hearth = bpy.context.active_object
    hearth.name = "MainDwelling_GuestBedroom_Hearth"
    hearth.scale = (HEARTH_WIDTH/2, HEARTH_DEPTH/2, HEARTH_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    hearth.data.materials.append(granite_mat)
    
    # UV unwrap hearth for texture
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create log burner body
    bpy.ops.mesh.primitive_cube_add(location=(log_burner_x, log_burner_y, log_burner_z))
    log_burner = bpy.context.active_object
    log_burner.name = "MainDwelling_GuestBedroom_LogBurner"
    log_burner.scale = (LOG_BURNER_WIDTH/2, LOG_BURNER_DEPTH/2, LOG_BURNER_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    log_burner.data.materials.append(log_burner_mat)
    
    # Create 4 legs (corners of log burner)
    leg_offset_x = LOG_BURNER_WIDTH/2 - LEG_DIAMETER
    leg_offset_y = LOG_BURNER_DEPTH/2 - LEG_DIAMETER
    leg_positions = [
        (log_burner_x - leg_offset_x, log_burner_y - leg_offset_y),  # SW
        (log_burner_x + leg_offset_x, log_burner_y - leg_offset_y),  # SE
        (log_burner_x - leg_offset_x, log_burner_y + leg_offset_y),  # NW
        (log_burner_x + leg_offset_x, log_burner_y + leg_offset_y),  # NE
    ]
    
    for i, (leg_x, leg_y) in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(
            location=(leg_x, leg_y, FLOOR_TOP + HEARTH_THICKNESS + LEG_HEIGHT/2),
            radius=LEG_DIAMETER/2,
            depth=LEG_HEIGHT
        )
        leg = bpy.context.active_object
        leg.name = f"MainDwelling_GuestBedroom_LogBurner_Leg_{i+1}"
        leg.data.materials.append(log_burner_mat)
    
    # Glass door (west face, where opening faces)
    GLASS_WIDTH = LOG_BURNER_WIDTH * 0.8  # Slightly smaller than burner width
    GLASS_HEIGHT = LOG_BURNER_HEIGHT * 0.7  # 70% of burner height
    GLASS_THICKNESS = 0.01  # 10mm thick glass
    
    glass_x = log_burner_x + LOG_BURNER_WIDTH/2 + GLASS_THICKNESS/2  # West face
    glass_z = log_burner_z  # Centered vertically
    
    bpy.ops.mesh.primitive_cube_add(location=(glass_x, log_burner_y, glass_z))
    glass_door = bpy.context.active_object
    glass_door.name = "MainDwelling_GuestBedroom_LogBurner_GlassDoor"
    glass_door.scale = (GLASS_THICKNESS/2, GLASS_WIDTH/2, GLASS_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    glass_door.data.materials.append(glass_mat)
    
    # Configure glass transparency
    glass_mat.blend_method = 'BLEND'
    bsdf = glass_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Alpha'].default_value = 0.3
    bsdf.inputs['Transmission Weight'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.0
    
    # Create flue pipe (vertical cylinder)
    flue_z = FLOOR_TOP + HEARTH_THICKNESS + LEG_HEIGHT + LOG_BURNER_HEIGHT + FLUE_HEIGHT/2
    bpy.ops.mesh.primitive_cylinder_add(location=(log_burner_x, log_burner_y, flue_z), radius=FLUE_DIAMETER/2, depth=FLUE_HEIGHT)
    flue = bpy.context.active_object
    flue.name = "MainDwelling_GuestBedroom_Flue"
    flue.data.materials.append(flue_mat)


def _create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS):
    """Create L-shaped kitchen bench against the ground floor south wall and stairwell partition
    
    Args:
        WIDTH: Total building width (7m - full roof span)
        LENGTH: Building length (9m - east-west)
        EXTERIOR_WALL_THICKNESS: Thickness of exterior walls (0.2m)
    """
    # Kitchen bench specifications
    BENCH_LENGTH = 2.4  # E-W dimension (main section)
    BENCH_DEPTH = 0.6   # N-S dimension
    BENCH_HEIGHT = 0.9  # Standard counter height
    BENCH_THICKNESS = 0.05  # Benchtop thickness
    L_SECTION_LENGTH = 2.0  # N-S dimension (L-section along stairwell)
    
    # Calculate positions
    # South wall interior face
    south_interior_y = oy - WIDTH/2 + EXTERIOR_WALL_THICKNESS
    # West wall interior face
    west_interior_x = ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS
    
    # Stairwell position (2m wide E-W)
    STAIRWELL_WIDTH = 2.0
    stairwell_east_x = west_interior_x + STAIRWELL_WIDTH
    
    # Main bench center position (runs E-W along south wall)
    bench_center_x = west_interior_x + BENCH_LENGTH/2 + 2.1  # Start 2.1m from west wall
    bench_center_y = south_interior_y + BENCH_DEPTH/2
    bench_top_z = oz + BENCH_HEIGHT
    
    # L-section center position (runs N-S along stairwell partition, on WEST side)
    # Position it at the east end of main bench, extending north
    main_bench_east_end = west_interior_x + 2.1  # East end of main bench
    l_section_x = main_bench_east_end + BENCH_DEPTH/2  # West of stairwell partition
    l_section_y = south_interior_y + BENCH_DEPTH + L_SECTION_LENGTH/2  # North from main bench corner
    
    # Create materials
    bench_mat = get_kitchen_bench_material()  # Granite texture
    cabinet_mat = get_kitchen_cabinet_material()  # Darker cabinet color
    
    cabinet_height = BENCH_HEIGHT - BENCH_THICKNESS
    
    # === MAIN SECTION (E-W along south wall) ===
    # Base cabinets
    bpy.ops.mesh.primitive_cube_add(location=(bench_center_x, bench_center_y, oz + cabinet_height/2))
    cabinets_main = bpy.context.active_object
    cabinets_main.name = "MainDwelling_KitchenBench_Cabinets_Main"
    cabinets_main.scale = (BENCH_LENGTH/2, BENCH_DEPTH/2, cabinet_height/2)
    bpy.ops.object.transform_apply(scale=True)
    cabinets_main.data.materials.append(cabinet_mat)
    
    # Benchtop
    bpy.ops.mesh.primitive_cube_add(location=(bench_center_x, bench_center_y, bench_top_z - BENCH_THICKNESS/2))
    benchtop_main = bpy.context.active_object
    benchtop_main.name = "MainDwelling_KitchenBench_Top_Main"
    benchtop_main.scale = (BENCH_LENGTH/2, BENCH_DEPTH/2, BENCH_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    benchtop_main.data.materials.append(bench_mat)
    
    # UV unwrap for texture
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # === L-SECTION (N-S along stairwell partition) ===
    # Base cabinets
    bpy.ops.mesh.primitive_cube_add(location=(l_section_x, l_section_y, oz + cabinet_height/2))
    cabinets_l = bpy.context.active_object
    cabinets_l.name = "MainDwelling_KitchenBench_Cabinets_LSection"
    cabinets_l.scale = (BENCH_DEPTH/2, L_SECTION_LENGTH/2, cabinet_height/2)
    bpy.ops.object.transform_apply(scale=True)
    cabinets_l.data.materials.append(cabinet_mat)
    
    # Benchtop
    bpy.ops.mesh.primitive_cube_add(location=(l_section_x, l_section_y, bench_top_z - BENCH_THICKNESS/2))
    benchtop_l = bpy.context.active_object
    benchtop_l.name = "MainDwelling_KitchenBench_Top_LSection"
    benchtop_l.scale = (BENCH_DEPTH/2, L_SECTION_LENGTH/2, BENCH_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    benchtop_l.data.materials.append(bench_mat)
    
    # UV unwrap for texture
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # === WALL CABINETS ===
    WALL_CABINET_DEPTH = 0.35  # Shallower than base cabinets
    WALL_CABINET_HEIGHT = 0.7  # 700mm tall
    WALL_CABINET_GAP = 0.45  # 450mm gap above benchtop
    wall_cabinet_z = bench_top_z + WALL_CABINET_GAP + WALL_CABINET_HEIGHT/2
    
    # Wall cabinet along N-S partition (from south wall north along stairwell)
    # Calculate length to extend from south wall to north end of L-section
    wall_cab_length_ns = BENCH_DEPTH + L_SECTION_LENGTH  # Full length from south wall
    wall_cab_ns_y = south_interior_y + wall_cab_length_ns/2  # Center from south wall northward
    wall_cab_ns_x = main_bench_east_end + WALL_CABINET_DEPTH/2  # Against partition, west side
    
    bpy.ops.mesh.primitive_cube_add(location=(wall_cab_ns_x, wall_cab_ns_y, wall_cabinet_z))
    wall_cab_ns = bpy.context.active_object
    wall_cab_ns.name = "MainDwelling_KitchenBench_WallCabinet_NS"
    wall_cab_ns.scale = (WALL_CABINET_DEPTH/2, wall_cab_length_ns/2, WALL_CABINET_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    wall_cab_ns.data.materials.append(cabinet_mat)
    
    print(f"L-shaped kitchen bench created: {BENCH_LENGTH}m E-W section, {L_SECTION_LENGTH}m N-S section with N-S wall cabinet")


def _create_dining_table(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS):
    """Create dining table north of stairs on ground floor
    
    Table dimensions: 1800mm long × 800mm wide × 750mm high
    Positioned north of the southwest corner staircase
    
    Args:
        WIDTH: Total building width (7m)
        LENGTH: Building length (9m)
        EXTERIOR_WALL_THICKNESS: Thickness of exterior walls (0.2m)
    """
    # Table dimensions
    TABLE_LENGTH = 1.8  # Long axis (E-W)
    TABLE_WIDTH = 0.8   # Short axis (N-S)
    TABLE_HEIGHT = 0.75
    LEG_SIZE = 0.08     # 80mm square legs
    TOP_THICKNESS = 0.04  # 40mm thick top
    
    
    # Position table north of stairs with clearance
    CLEARANCE = 0.4  # 400mm clearance from stairwell
    table_x = ox - 1.0
    table_y = oy + 1.3
    table_top_z = oz + TABLE_HEIGHT - TOP_THICKNESS/2
    
    # Create material
    table_mat = create_material("DiningTableWood", (0.55, 0.35, 0.20, 1))  # Medium wood tone
    
    # === TABLE TOP ===
    bpy.ops.mesh.primitive_cube_add(location=(table_x, table_y, table_top_z))
    table_top = bpy.context.active_object
    table_top.name = "MainDwelling_DiningTable_Top"
    table_top.scale = (TABLE_LENGTH/2, TABLE_WIDTH/2, TOP_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    table_top.data.materials.append(table_mat)
    
    # UV unwrap for texture
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # === TABLE LEGS (4 corners) ===
    leg_height = TABLE_HEIGHT - TOP_THICKNESS
    leg_z = oz + leg_height/2
    leg_inset = 0.1  # Inset legs 100mm from edges
    
    # Corner positions
    leg_positions = [
        (table_x - TABLE_LENGTH/2 + leg_inset, table_y - TABLE_WIDTH/2 + leg_inset),  # SE
        (table_x + TABLE_LENGTH/2 - leg_inset, table_y - TABLE_WIDTH/2 + leg_inset),  # SW
        (table_x - TABLE_LENGTH/2 + leg_inset, table_y + TABLE_WIDTH/2 - leg_inset),  # NE
        (table_x + TABLE_LENGTH/2 - leg_inset, table_y + TABLE_WIDTH/2 - leg_inset),  # NW
    ]
    
    for i, (leg_x, leg_y) in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cube_add(location=(leg_x, leg_y, leg_z))
        leg = bpy.context.active_object
        leg.name = f"MainDwelling_DiningTable_Leg_{i+1}"
        leg.scale = (LEG_SIZE/2, LEG_SIZE/2, leg_height/2)
        bpy.ops.object.transform_apply(scale=True)
        leg.data.materials.append(table_mat)
    
    print(f"Dining table created at ({table_x:.2f}, {table_y:.2f}, {oz}): {TABLE_LENGTH}m × {TABLE_WIDTH}m × {TABLE_HEIGHT}m")


def _create_interior_partitions_first_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Create first floor interior partitions for master bedroom, ensuite, and wardrobe
    
    Args:
        WIDTH: Total building width (7m - full roof span)
        ENCLOSED_WIDTH: Enclosed building width (6m - north wall recessed)
        NORTH_RECESS: Distance north wall is recessed from north edge (1m)
    """
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    interior_wall_mat = get_interior_wall_material()
    
    # Master bedroom & ensuite dimensions
    MASTER_BEDROOM_WIDTH = 4.0  # E-W dimension (interior space from east wall)
    ENSUITE_DEPTH = 2.0
    ENSUITE_WIDTH = 2.0
    
    # Interior dimensions (north wall recessed from north edge by NORTH_RECESS)
    north_interior_face = oy + WIDTH/2 - NORTH_RECESS
    south_interior_face = oy - WIDTH/2 + EXTERIOR_WALL_THICKNESS
    interior_depth = north_interior_face - south_interior_face
    bedroom_interior_width = MASTER_BEDROOM_WIDTH  # Full 4m interior space
    east_interior_face = ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS
    
    # Main partition wall (N-S) - aligned with bedroom partitions at MASTER_BEDROOM_WIDTH from east wall
    main_partition_x = east_interior_face - MASTER_BEDROOM_WIDTH - INTERIOR_WALL_THICKNESS/2
    main_partition_center_y = (north_interior_face + south_interior_face) / 2  # Center between recessed north and full-width south
    bpy.ops.mesh.primitive_cube_add(location=(main_partition_x, main_partition_center_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    main_partition = bpy.context.active_object
    main_partition.name = "MainDwelling_FirstFloor_MainPartition"
    main_partition.scale = (INTERIOR_WALL_THICKNESS/2, interior_depth/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    main_partition.data.materials.append(interior_wall_mat)
    
    # Bedroom south partition (E-W wall) - spans exactly MASTER_BEDROOM_WIDTH (4m) from east wall
    bedroom_partition_y = south_interior_face + ENSUITE_DEPTH
    bedroom_partition_center_x = east_interior_face - MASTER_BEDROOM_WIDTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(bedroom_partition_center_x, bedroom_partition_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    bedroom_south_partition = bpy.context.active_object
    bedroom_south_partition.name = "MainDwelling_FirstFloor_BedroomSouthPartition"
    bedroom_south_partition.scale = (MASTER_BEDROOM_WIDTH/2, INTERIOR_WALL_THICKNESS/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    bedroom_south_partition.data.materials.append(interior_wall_mat)
    
    # Ensuite/wardrobe dividing wall (N-S)
    ensuite_wardrobe_wall_x = east_interior_face - ENSUITE_WIDTH
    ensuite_wardrobe_wall_center_y = south_interior_face + ENSUITE_DEPTH/2
    
    bpy.ops.mesh.primitive_cube_add(location=(ensuite_wardrobe_wall_x, ensuite_wardrobe_wall_center_y, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    ensuite_wardrobe_wall = bpy.context.active_object
    ensuite_wardrobe_wall.name = "MainDwelling_FirstFloor_EnsuiteWardrobeWall"
    ensuite_wardrobe_wall.scale = (INTERIOR_WALL_THICKNESS/2, ENSUITE_DEPTH/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    ensuite_wardrobe_wall.data.materials.append(interior_wall_mat)
    
    # Add doorways
    # Door from hallway to master bedroom
    add_window("MainDwelling_FirstFloor_MainPartition", (main_partition_x + INTERIOR_WALL_THICKNESS/2, oy + 2.0, first_floor_z + 1.0), 
               width=0.8, height=2.0, depth=INTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # Door from bedroom to ensuite
    add_window("MainDwelling_FirstFloor_BedroomSouthPartition", (east_interior_face - 0.45, bedroom_partition_y - INTERIOR_WALL_THICKNESS/2, first_floor_z + 1.0), 
               width=0.8, height=2.0, depth=INTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    
    # Door from bedroom to walk-in wardrobe
    add_window("MainDwelling_FirstFloor_BedroomSouthPartition", (ensuite_wardrobe_wall_x - 1.5, bedroom_partition_y - INTERIOR_WALL_THICKNESS/2, first_floor_z + 1.0), 
               width=0.8, height=2.0, depth=INTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    
    # King bed in master bedroom (1.8m wide × 2.0m long)
    BED_WIDTH = 1.8  # E-W dimension
    BED_LENGTH = 2.0  # N-S dimension
    BED_HEIGHT = 0.6  # Total height (base + mattress)
    
    bed_mat = create_material("BedFabric", (0.95, 0.95, 0.9, 1))
    
    # Position bed with headboard against south partition, centered E-W
    bed_x = east_interior_face - MASTER_BEDROOM_WIDTH/2
    bed_y = bedroom_partition_y + INTERIOR_WALL_THICKNESS/2 + BED_LENGTH/2
    bed_z = first_floor_z + BED_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(bed_x, bed_y, bed_z))
    bed = bpy.context.active_object
    bed.name = "MainDwelling_MasterBedroom_KingBed"
    bed.scale = (BED_WIDTH/2, BED_LENGTH/2, BED_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    bed.data.materials.append(bed_mat)


def _furnish_master_ensuite(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS):
    """Furnish master bedroom ensuite with shower, toilet, and vanity
    
    Layout (2m × 2m ensuite in SE corner):
    - Shower: NW corner, stepping in from east
    - Toilet: SW corner, back against west wall
    - Vanity: SE corner, back against east wall
    - Entrance: East side of north wall
    """
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    FIRST_FLOOR_SLAB_THICKNESS = 0.2  # First floor is 200mm thick
    first_floor_top = first_floor_z + FIRST_FLOOR_SLAB_THICKNESS
    
    # Ensuite dimensions
    ENSUITE_WIDTH = 2.0   # E-W dimension
    ENSUITE_DEPTH = 2.0   # N-S dimension
    
    # Calculate ensuite boundaries
    east_interior_face = ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS
    south_interior_face = oy - WIDTH/2 + EXTERIOR_WALL_THICKNESS
    
    # Ensuite corners
    ensuite_east = east_interior_face
    ensuite_west = east_interior_face - ENSUITE_WIDTH
    ensuite_south = south_interior_face
    ensuite_north = south_interior_face + ENSUITE_DEPTH
    
    # Materials
    white_mat = create_material("BathroomWhite", (0.95, 0.95, 0.95, 1))
    chrome_mat = create_material("Chrome", (0.8, 0.8, 0.8, 1))
    glass_mat = create_material("ShowerGlass", (0.7, 0.85, 0.9, 0.3))
    
    # === SHOWER IN NW CORNER (stepping in from east) ===
    SHOWER_SIZE = 0.9  # 900mm square shower
    SHOWER_TRAY_HEIGHT = 0.15  # 150mm high tray
    WALL_THICKNESS = 0.1  # 100mm thick walls
    WALL_HEIGHT = 2.0
    
    # Position shower in NW corner - back walls align with room walls
    # West wall of shower aligns with west wall of ensuite
    # North wall of shower aligns with north wall of ensuite
    shower_west_edge = ensuite_west
    shower_east_edge = ensuite_west + SHOWER_SIZE
    shower_north_edge = ensuite_north
    shower_south_edge = ensuite_north - SHOWER_SIZE
    shower_x_center = (shower_west_edge + shower_east_edge) / 2
    shower_y_center = (shower_north_edge + shower_south_edge) / 2
    
    # Shower tray (raised platform) - sits on top of first floor slab
    bpy.ops.mesh.primitive_cube_add(location=(shower_x_center, shower_y_center, first_floor_top + SHOWER_TRAY_HEIGHT/2))
    shower_tray = bpy.context.active_object
    shower_tray.name = "MainDwelling_Ensuite_ShowerTray"
    shower_tray.scale = (SHOWER_SIZE/2, SHOWER_SIZE/2, SHOWER_TRAY_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    shower_tray.data.materials.append(white_mat)
    
    # Shower walls (tile/panel material)
    tile_mat = create_material("ShowerTile", (0.9, 0.9, 0.88, 1))
    
    # West wall (back wall against ensuite west wall)
    west_wall_x = shower_west_edge + WALL_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(west_wall_x, shower_y_center, 
                                               first_floor_top + SHOWER_TRAY_HEIGHT + WALL_HEIGHT/2))
    west_wall = bpy.context.active_object
    west_wall.name = "MainDwelling_Ensuite_ShowerWallWest"
    west_wall.scale = (WALL_THICKNESS/2, SHOWER_SIZE/2, WALL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall.data.materials.append(tile_mat)
    
    # North wall (side wall against ensuite north wall)
    north_wall_y = shower_north_edge + WALL_THICKNESS/2
    bpy.ops.mesh.primitive_cube_add(location=(shower_x_center, north_wall_y, 
                                               first_floor_top + SHOWER_TRAY_HEIGHT + WALL_HEIGHT/2))
    north_wall = bpy.context.active_object
    north_wall.name = "MainDwelling_Ensuite_ShowerWallNorth"
    north_wall.scale = (SHOWER_SIZE/2, WALL_THICKNESS/2, WALL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall.data.materials.append(tile_mat)
    
    # Shower glass screen (east side - entrance, shorter than walls)
    glass_thickness = 0.01
    glass_height = 1.8
    glass_x = shower_east_edge - glass_thickness/2
    bpy.ops.mesh.primitive_cube_add(location=(glass_x, shower_y_center, 
                                               first_floor_top + SHOWER_TRAY_HEIGHT + glass_height/2))
    shower_screen = bpy.context.active_object
    shower_screen.name = "MainDwelling_Ensuite_ShowerScreen"
    shower_screen.scale = (glass_thickness/2, SHOWER_SIZE/2, glass_height/2)
    bpy.ops.object.transform_apply(scale=True)
    shower_screen.data.materials.append(glass_mat)
    
    # Shower head (mounted on west wall)
    bpy.ops.mesh.primitive_uv_sphere_add(location=(west_wall_x - 0.15, shower_y_center, 
                                                    first_floor_top + SHOWER_TRAY_HEIGHT + 1.8), radius=0.05)
    shower_head = bpy.context.active_object
    shower_head.name = "MainDwelling_Ensuite_ShowerHead"
    shower_head.data.materials.append(chrome_mat)
    
    # === TOILET IN SW CORNER (back against west wall) ===
    TOILET_WIDTH = 0.4  # N-S dimension
    TOILET_DEPTH = 0.6  # E-W dimension (depth from wall)
    TOILET_HEIGHT = 0.4
    TOILET_TANK_HEIGHT = 0.8
    
    # Position in SW corner, tank against west wall, bowl facing east
    toilet_east_edge = ensuite_west + TOILET_DEPTH
    toilet_center_x = (ensuite_west + toilet_east_edge) / 2
    toilet_center_y = ensuite_south + TOILET_WIDTH/2 + 0.15  # 150mm from south wall
    
    # Toilet bowl (combined bowl and tank as one unit for simplicity)
    bpy.ops.mesh.primitive_cube_add(location=(toilet_center_x, toilet_center_y, first_floor_top + TOILET_HEIGHT/2))
    toilet_bowl = bpy.context.active_object
    toilet_bowl.name = "MainDwelling_Ensuite_ToiletBowl"
    toilet_bowl.scale = (TOILET_DEPTH/2, TOILET_WIDTH/2, TOILET_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    toilet_bowl.data.materials.append(white_mat)
    
    # Toilet tank (against west wall)
    tank_width = 0.15
    bpy.ops.mesh.primitive_cube_add(location=(ensuite_west + tank_width/2, toilet_center_y, 
                                               first_floor_top + TOILET_TANK_HEIGHT/2))
    toilet_tank = bpy.context.active_object
    toilet_tank.name = "MainDwelling_Ensuite_ToiletTank"
    toilet_tank.scale = (tank_width/2, TOILET_WIDTH/2, TOILET_TANK_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    toilet_tank.data.materials.append(white_mat)
    
    # === VANITY IN SE CORNER (back against east wall, facing west) ===
    VANITY_WIDTH = 0.6  # N-S dimension
    VANITY_DEPTH = 0.5  # E-W dimension (depth from wall)
    VANITY_HEIGHT = 0.85
    BASIN_HEIGHT = 0.15
    
    # Position in SE corner, back against east wall, facing west
    vanity_west_edge = ensuite_east - VANITY_DEPTH
    vanity_center_x = (ensuite_east + vanity_west_edge) / 2
    vanity_center_y = ensuite_south + VANITY_WIDTH/2
    
    # Vanity cabinet
    cabinet_mat = create_material("VanityCabinet", (0.4, 0.3, 0.2, 1))
    bpy.ops.mesh.primitive_cube_add(location=(vanity_center_x, vanity_center_y, first_floor_top + VANITY_HEIGHT/2))
    vanity_cabinet = bpy.context.active_object
    vanity_cabinet.name = "MainDwelling_Ensuite_VanityCabinet"
    vanity_cabinet.scale = (VANITY_DEPTH/2, VANITY_WIDTH/2, VANITY_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    vanity_cabinet.data.materials.append(cabinet_mat)
    
    # Basin
    bpy.ops.mesh.primitive_cube_add(location=(vanity_center_x, vanity_center_y, 
                                               first_floor_top + VANITY_HEIGHT + BASIN_HEIGHT/2))
    basin = bpy.context.active_object
    basin.name = "MainDwelling_Ensuite_Basin"
    basin.scale = ((VANITY_DEPTH - 0.1)/2, (VANITY_WIDTH - 0.1)/2, BASIN_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    basin.data.materials.append(white_mat)
    
    # Tap (positioned toward front/west of basin)
    bpy.ops.mesh.primitive_cylinder_add(location=(vanity_center_x - 0.15, vanity_center_y, 
                                                   first_floor_top + VANITY_HEIGHT + 0.15), radius=0.02, depth=0.2)
    tap = bpy.context.active_object
    tap.name = "MainDwelling_Ensuite_Tap"
    tap.data.materials.append(chrome_mat)


def _add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS):
    """Add all windows and doors to exterior walls
    
    Args:
        WIDTH: Total building width (7m - full roof span, south wall position)
        ENCLOSED_WIDTH: Enclosed building width (6m - north wall recessed)
        NORTH_RECESS: Distance north wall is recessed from north edge (1m)
    """
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    window_z_ground = oz + 1.0
    window_z_first = first_floor_z + 1.0
    spacing = LENGTH / 4
    
    # Calculate wall positions
    north_wall_y = oy + WIDTH/2 - NORTH_RECESS + EXTERIOR_WALL_THICKNESS/2
    north_wall_outer_face = north_wall_y + EXTERIOR_WALL_THICKNESS/2  # Outer face position for windows
    south_wall_y = oy - WIDTH/2
    
    # East/West walls span full WIDTH, centered at oy
    east_west_window_spacing = WIDTH / 3
    south_spacing = LENGTH / 4
    
    # GROUND FLOOR - NORTH WALL (recessed) - position at outer face
    add_window("MainDwelling_NorthWall_Ground", (ox - spacing, north_wall_outer_face, window_z_ground), width=2.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    #add_window("MainDwelling_NorthWall_Ground", (ox, north_wall_outer_face, window_z_ground), width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_NorthWall_Ground", (ox + spacing, north_wall_outer_face, window_z_ground), width=2.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # FIRST FLOOR - NORTH WALL (recessed) - position at outer face
    add_window("MainDwelling_NorthWall_First", (ox - spacing, north_wall_outer_face, window_z_first), width=2.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_NorthWall_First", (ox + spacing, north_wall_outer_face, window_z_first), width=2.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # GROUND FLOOR - EAST WALL (spans full 7m)
    add_window("MainDwelling_EastWall_Ground", (ox + LENGTH/2, oy + 1.5, oz + 1.2), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MainDwelling_EastWall_Ground", (ox + LENGTH/2, oy - 2, oz + 1.2), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # FIRST FLOOR - EAST WALL (spans full 7m)
    add_window("MainDwelling_EastWall_First", (ox + LENGTH/2, oy + 1.5, first_floor_z + 1.2), width=1.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MainDwelling_EastWall_First", (ox + LENGTH/2, oy - 2, first_floor_z + 1.2), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # GROUND FLOOR - WEST WALL (spans full 7m)
    add_window("MainDwelling_WestWall_Ground", (ox - LENGTH/2, oy + 1.7, oz + 1.45), width=0.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    #add_window("MainDwelling_WestWall_Ground", (ox - LENGTH/2, oy - 0.65, oz + 1.1), width=0.5, height=1.8, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # FIRST FLOOR - WEST WALL (spans full 7m)
    add_window("MainDwelling_WestWall_First", (ox - LENGTH/2, oy, first_floor_z + 1.2), width=1.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    #add_window("MainDwelling_WestWall_First", (ox - LENGTH/2, oy - 1.5, first_floor_z + 1.2), width=1.5, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # GROUND FLOOR - SOUTH WALL (full width)
    add_window("MainDwelling_SouthWall_Ground", (ox + 3, south_wall_y, oz + 1.5), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    add_window("MainDwelling_SouthWall_Ground", (ox + 1.5, south_wall_y, oz + 1.0), width=1.2, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    add_window("MainDwelling_SouthWall_Ground", (ox - 0.7, south_wall_y, oz + 1.45), width=1.8, height=1.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    # Double-height window at stair landing - ground floor portion
    add_window("MainDwelling_SouthWall_Ground", (ox - 3.3, south_wall_y, oz + 2.15), width=1.2, height=0.7, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    
    # FIRST FLOOR - SOUTH WALL (full width)
    add_window("MainDwelling_SouthWall_First", (ox + 3.2, south_wall_y, first_floor_z + 1.2), width=1.0, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    add_window("MainDwelling_SouthWall_First", (ox + 1.0, south_wall_y, first_floor_z + 1.2), width=0.6, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    add_window("MainDwelling_SouthWall_First", (ox - 0.8, south_wall_y, first_floor_z + 1.2), width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    # Double-height window at stair landing - first floor portion
    add_window("MainDwelling_SouthWall_First", (ox - 3.3, south_wall_y, first_floor_z + 0.4), width=1.2, height=2.8, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y')
    
    # Cut opening in first floor slab for double-height window
    first_floor_slab = bpy.data.objects.get("MainDwelling_FirstFloor")
    if first_floor_slab:
        # Position cutter to cut floor flush with interior face of south wall
        interior_face_y = south_wall_y + EXTERIOR_WALL_THICKNESS/2
        window_slab_opening_depth = 0.4  # Extend north into room
        cutter_center_y = interior_face_y + window_slab_opening_depth/2
        
        bpy.ops.mesh.primitive_cube_add(location=(ox - 3.2, cutter_center_y, first_floor_z + 0.1))
        window_cutter = bpy.context.active_object
        window_cutter.name = "MainDwelling_WindowSlabCutter_StairLanding"
        window_cutter.scale = (1.0/2, window_slab_opening_depth/2, 0.2/2)
        bpy.ops.object.transform_apply(scale=True)
        
        # Boolean modifier to cut opening
        bool_mod = first_floor_slab.modifiers.new(name="StairWindow_Cut", type='BOOLEAN')
        bool_mod.object = window_cutter
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.solver = 'EXACT'
        
        # Hide cutter
        window_cutter.hide_viewport = True
        window_cutter.hide_render = True


def _create_gable_roof(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, roof_style, potius_mat):
    """Create the main gable roof with either traditional or flush style
    
    Args:
        potius_mat: Exterior cladding material for gable ends
    """
    roof_height_from_eaves = (WIDTH / 2) * math.tan(math.radians(ROOF_PITCH))
    eave_height = oz + TOTAL_HEIGHT
    ridge_height = eave_height + roof_height_from_eaves
    
    roof_mat = get_metal_roof_material()
    # Use the same exterior cladding material for gable ends
    gable_material = potius_mat
    
    if roof_style == "flush":
        mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
        obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
        bpy.context.collection.objects.link(obj)
        
        east_edge = ox + LENGTH/2
        west_edge = ox - LENGTH/2
        # Roof spans full 7m WIDTH, flush with building edges
        north_eave_y = oy + WIDTH/2
        south_eave_y = oy - WIDTH/2
        
        verts = [
            (east_edge, north_eave_y, eave_height),
            (west_edge, north_eave_y, eave_height),
            (east_edge, oy, ridge_height),
            (west_edge, oy, ridge_height),
            (east_edge, south_eave_y, eave_height),
            (west_edge, south_eave_y, eave_height),
        ]
        
        faces = [
            (0, 1, 3, 2),  # North roof slope
            (2, 3, 5, 4),  # South roof slope
            (0, 2, 4),     # East gable triangle
            (1, 5, 3),     # West gable triangle
        ]
        
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        
        obj.data.materials.append(roof_mat)
        obj.data.materials.append(gable_material)
        
        for i, face in enumerate(mesh.polygons):
            if i < 2:
                face.material_index = 0
            else:
                face.material_index = 1
        
        # Create UV layer and set UVs for gable faces
        if not mesh.uv_layers:
            mesh.uv_layers.new(name="UVMap")
        
        uv_layer = mesh.uv_layers.active.data
        for poly_idx, poly in enumerate(mesh.polygons):
            if poly_idx >= 2:  # Gable faces
                for loop_idx in poly.loop_indices:
                    loop = mesh.loops[loop_idx]
                    vert = mesh.vertices[loop.vertex_index]
                    # Scale UVs: world_dimension / 2.0 to match wall UV scale
                    # This gives ~150mm grooves after material's 13.33x scaling
                    u = (vert.co.y - (oy + WIDTH/2)) / 2.0
                    v = (vert.co.z - eave_height) / 2.0
                    uv_layer[loop_idx].uv = (u, v)
        
        # UV unwrap roof faces only
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        for i in range(2):
            mesh.polygons[i].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)
    else:  # traditional
        mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
        obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
        bpy.context.collection.objects.link(obj)
        
        half_length = (LENGTH + 2 * ROOF_OVERHANG) / 2
        north_eave_y = oy + WIDTH/2 + ROOF_OVERHANG
        south_eave_y = oy - WIDTH/2 - ROOF_OVERHANG
        
        verts = [
            (ox - half_length, north_eave_y, eave_height),
            (ox + half_length, north_eave_y, eave_height),
            (ox - half_length, oy, ridge_height),
            (ox + half_length, oy, ridge_height),
            (ox - half_length, south_eave_y, eave_height),
            (ox + half_length, south_eave_y, eave_height),
        ]
        
        faces = [
            (0, 1, 3, 2),
            (2, 3, 5, 4),
        ]
        
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(roof_mat)
        
        # UV unwrap for texture display
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)
        
        # Create separate gable end triangles
        for side, x_pos in [("East", ox - LENGTH/2), ("West", ox + LENGTH/2)]:
            verts = [
                (x_pos, oy - WIDTH/2, eave_height),
                (x_pos, oy + WIDTH/2, eave_height),
                (x_pos, oy, ridge_height)
            ]
            edges = []
            faces = [(0, 1, 2)]
            
            gable_mesh = bpy.data.meshes.new(f"MainDwelling_Gable_{side}")
            gable_mesh.from_pydata(verts, edges, faces)
            gable_mesh.update()
            
            gable = bpy.data.objects.new(f"MainDwelling_Gable_{side}", gable_mesh)
            bpy.context.collection.objects.link(gable)
            gable.data.materials.append(gable_material)
            
            # Create UV layer with normalized coordinates (0-1 range)
            if not gable_mesh.uv_layers:
                gable_mesh.uv_layers.new(name="UVMap")
            uv_layer = gable_mesh.uv_layers.active.data
            
            # Calculate gable dimensions
            gable_width = WIDTH
            gable_height = roof_height_from_eaves
            
            for poly in gable_mesh.polygons:
                for loop_idx in poly.loop_indices:
                    loop = gable_mesh.loops[loop_idx]
                    vert = gable_mesh.vertices[loop.vertex_index]
                    # Scale UVs so that 150mm (0.15m) = 1 texture repeat BEFORE material scaling
                    # We want: actual_dimension / 0.15m texture repeats
                    # Then material's 13.33x brings it to correct scale
                    # So: UV = world_dimension / (0.15m * 13.33) = world_dimension / 2.0
                    u = (vert.co.y - (oy - WIDTH/2)) / 2.0  # 7m span / 2.0 = 3.5 UV units
                    v = (vert.co.z - eave_height) / 2.0
                    uv_layer[loop_idx].uv = (u, v)
                    print(f"  Gable face {poly_idx}, vert: Y={vert.co.y:.2f}, Z={vert.co.z:.2f} -> UV=({u:.4f}, {v:.4f})")
            
            print(f"=== END GABLE UV DEBUG ===\n")
            
            print(f"DEBUG: Created gable {side} with material {gable_material.name}")


# === MAIN BUILDING FUNCTIONS ===

def build_north_deck(origin=(0, 0, 0), building_length=9.0, building_width=7.0, north_recess=1.0):
    """
    Build a timber deck extending 3 meters north from the recessed north wall of the main dwelling.
    The deck is constructed with piles, bearers, joists, and 90mm x 25mm decking boards.
    
    Args:
        origin: (x, y, z) tuple for building origin (same as main dwelling)
        building_length: East-west dimension of building (9m default)
        building_width: North-south dimension of building (7m default)
        north_recess: How far north wall is recessed (1m default)
    """
    ox, oy, oz = origin
    
    # Deck dimensions
    DECK_EXTENSION = 3.0  # 3 meters north
    DECK_THICKNESS = 0.025  # 25mm decking board thickness
    DECK_BOARD_WIDTH = 0.090  # 90mm board width
    BOARD_GAP = 0.005  # 5mm gap between boards
    
    # Structural dimensions
    PILE_SIZE = 0.15  # 150mm x 150mm H5 timber piles
    PILE_HEIGHT_ABOVE_GROUND = 0.4  # 400mm above ground to deck surface
    PILE_DEPTH_BELOW_GROUND = 0.6  # 600mm below ground
    BEARER_SIZE = (0.150, 0.200)  # 150mm x 200mm bearers (W x H)
    JOIST_SIZE = (0.090, 0.190)  # 90mm x 190mm joists (W x H)
    JOIST_SPACING = 0.45  # 450mm centers
    
    # Calculate deck position (north of recessed wall)
    # North edge of building is at oy + building_width/2
    # Recessed north wall is at oy + building_width/2 - north_recess
    north_wall_y = oy + building_width/2 - north_recess
    deck_start_y = north_wall_y + 1.0  # Move 1 meter further north
    deck_end_y = deck_start_y + DECK_EXTENSION
    deck_center_y = (deck_start_y + deck_end_y) / 2
    
    # Deck height adjustment: lower by 520mm (raised 80mm from original)
    DECK_HEIGHT_OFFSET = -0.52  # 520mm below ground level
    
    # Deck spans full building length east-west
    deck_west_x = ox - building_length/2
    deck_east_x = ox + building_length/2
    deck_center_x = ox
    
    # Materials
    import os
    texture_path = os.path.join(os.path.dirname(__file__), "textures", "knotted-timber-staggered-1995-mm-architextures.jpg")
    deck_mat = create_textured_material("TimberDecking", texture_path)
    structure_mat = create_material("TreatedTimber", (0.55, 0.45, 0.35, 1))
    
    # === PILES (Foundation Posts) ===
    # Arrange piles in 2 rows (middle and north) x 4 columns
    # South row removed - joists use hangers to connect directly to building
    pile_cols = 4
    pile_spacing_ns = DECK_EXTENSION / 2  # Spacing for middle and north positions
    pile_spacing_ew = building_length / (pile_cols + 1)  # E-W spacing between columns
    NORTH_BEARER_INSET = 0.15  # 150mm inset from north edge for overhang
    
    # Calculate pile row positions to match bearer positions
    pile_y_middle = deck_start_y + pile_spacing_ns
    pile_y_north = deck_start_y + (2 * pile_spacing_ns) - NORTH_BEARER_INSET
    
    pile_positions = [
        ("Middle", pile_y_middle),
        ("North", pile_y_north)
    ]
    
    pile_center_z = oz + DECK_HEIGHT_OFFSET - PILE_DEPTH_BELOW_GROUND + (PILE_DEPTH_BELOW_GROUND + PILE_HEIGHT_ABOVE_GROUND) / 2
    
    for row_name, pile_y in pile_positions:
        for col in range(pile_cols):
            pile_x = deck_east_x - (col + 1) * pile_spacing_ew
            
            bpy.ops.mesh.primitive_cube_add(location=(pile_x, pile_y, pile_center_z))
            pile = bpy.context.active_object
            pile.name = f"Deck_Pile_{row_name}_C{col+1}"
            pile.scale = (PILE_SIZE/2, PILE_SIZE/2, (PILE_DEPTH_BELOW_GROUND + PILE_HEIGHT_ABOVE_GROUND)/2)
            bpy.ops.object.transform_apply(scale=True)
            pile.data.materials.append(structure_mat)
    
    # === BEARERS (Main beams running East-West on top of piles) ===
    # 2 bearers: middle and north (south bearer omitted - joists use hangers to connect to building)
    bearer_z = oz + DECK_HEIGHT_OFFSET + PILE_HEIGHT_ABOVE_GROUND - BEARER_SIZE[1]/2
    
    # Middle bearer
    bpy.ops.mesh.primitive_cube_add(location=(deck_center_x, pile_y_middle, bearer_z))
    bearer = bpy.context.active_object
    bearer.name = "Deck_Bearer_Middle"
    bearer.scale = (building_length/2, BEARER_SIZE[0]/2, BEARER_SIZE[1]/2)
    bpy.ops.object.transform_apply(scale=True)
    bearer.data.materials.append(structure_mat)
    
    # North bearer (inset for overhang)
    bpy.ops.mesh.primitive_cube_add(location=(deck_center_x, pile_y_north, bearer_z))
    bearer = bpy.context.active_object
    bearer.name = "Deck_Bearer_North"
    bearer.scale = (building_length/2, BEARER_SIZE[0]/2, BEARER_SIZE[1]/2)
    bpy.ops.object.transform_apply(scale=True)
    bearer.data.materials.append(structure_mat)
    
    # === JOISTS (Smaller beams running North-South, perpendicular to bearers) ===
    # Joists span from south bearer to north bearer
    joist_z = oz + DECK_HEIGHT_OFFSET + PILE_HEIGHT_ABOVE_GROUND + JOIST_SIZE[1]/2
    num_joists = int(building_length / JOIST_SPACING) + 1
    
    for i in range(num_joists):
        joist_x = deck_east_x - (i * JOIST_SPACING)
        if joist_x < deck_west_x:
            break
        
        bpy.ops.mesh.primitive_cube_add(location=(joist_x, deck_center_y, joist_z))
        joist = bpy.context.active_object
        joist.name = f"Deck_Joist_{i+1:02d}"
        joist.scale = (JOIST_SIZE[0]/2, DECK_EXTENSION/2, JOIST_SIZE[1]/2)
        bpy.ops.object.transform_apply(scale=True)
        joist.data.materials.append(structure_mat)
    
    # === DECKING BOARDS (90mm x 25mm boards running East-West) ===
    deck_surface_z = oz + DECK_HEIGHT_OFFSET + PILE_HEIGHT_ABOVE_GROUND + JOIST_SIZE[1] + DECK_THICKNESS/2
    num_boards = int(DECK_EXTENSION / (DECK_BOARD_WIDTH + BOARD_GAP)) + 1
    
    for i in range(num_boards):
        board_y = deck_start_y + (i * (DECK_BOARD_WIDTH + BOARD_GAP)) + DECK_BOARD_WIDTH/2
        if board_y > deck_end_y:
            break
        
        bpy.ops.mesh.primitive_cube_add(location=(deck_center_x, board_y, deck_surface_z))
        board = bpy.context.active_object
        board.name = f"Deck_Board_{i+1:02d}"
        board.scale = (building_length/2, DECK_BOARD_WIDTH/2, DECK_THICKNESS/2)
        bpy.ops.object.transform_apply(scale=True)
        board.data.materials.append(deck_mat)
        
        # UV unwrap for proper texture display
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"North Deck built at origin {origin}, extending {DECK_EXTENSION}m north")


def build_main_dwelling(origin=(0, 0, 0), show_roof=True, roof_style="traditional"):
    """
    Build the main dwelling structure with ENCLOSED GABLE PORCH:
    - 7m × 9m base (9m runs east-west, 7m north-south)
    - North wall recessed 1m to create patio (ground) and covered balcony (first floor)
    - Two stories: ground floor 2.5m ceiling, first floor 2.4m ceiling
    - Potius residential system with 200mm exterior walls
    - Interior walls 110mm
    - Gable roof, 35° pitch, ridge runs east-west
    - 2.5m × 2.5m enclosed porch with gable roof, door in west porch wall
    - Windows/doors on north and east walls
    
    Args:
        origin: (x, y, z) tuple for building location
        show_roof: Boolean to show/hide roof for interior viewing
        roof_style: "traditional" (overhang on all sides, separate gable ends) or 
                    "flush" (flush with building edges, covers recessed north balcony)
    """
    ox, oy, oz = origin
    
    # Dimensions from specifications
    WIDTH = 7.0  # Total north-south dimension (roof span)
    ENCLOSED_WIDTH = 6.0  # Enclosed building width (north wall recessed 1m)
    LENGTH = 9.0
    GROUND_FLOOR_HEIGHT = 2.5
    FIRST_FLOOR_HEIGHT = 2.4
    TOTAL_HEIGHT = GROUND_FLOOR_HEIGHT + FIRST_FLOOR_HEIGHT
    EXTERIOR_WALL_THICKNESS = 0.20
    INTERIOR_WALL_THICKNESS = 0.11
    ROOF_PITCH = 35
    ROOF_OVERHANG = 0.6
    NORTH_RECESS = 1.0  # North wall recessed to create patio/balcony
    
    # Materials
    import os
    texture_path = os.path.join(os.path.dirname(__file__), "textures", "thermal-redwood--shou-sugi-ban--char--brushed--black-rainscreen-117-1235-mm-architextures.jpg")
    potius_mat = create_textured_material("PotiusExterior", texture_path)
    floor_mat = get_floor_wood_material()
    
    # === CREATE SHARED COMPONENTS ===
    _create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat)
    _create_floors(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat)
    
    # === ENTRANCE PORCH (WEST SIDE) - ENCLOSED WITH GABLE ROOF ===
    
    # Porch dimensions: 2.5m Ã— 2.5m floor, walls wrap 2.5m width Ã— 1.5m depth
    # Remaining 1m is open but covered by porch roof
    PORCH_WIDTH = 2.5   # North-south dimension
    PORCH_TOTAL_DEPTH = 2.5   # Total east-west depth
    PORCH_WALL_DEPTH = 1.5    # Depth covered by walls
    PORCH_OPEN_DEPTH = 1.0    # Open covered area (2.5 - 1.5)
    PORCH_HEIGHT = GROUND_FLOOR_HEIGHT  # Same height as ground floor
    PORCH_WALL_THICKNESS = EXTERIOR_WALL_THICKNESS
    
    porch_mat = potius_mat  # Use same material as main building
    
    # Porch floor/deck - positioned west of west wall, centered
    porch_center_x = ox - LENGTH/2 - PORCH_TOTAL_DEPTH/2
    porch_center_y = oy  # Centered on building
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_center_x, porch_center_y, oz + 0.05))
    porch_floor = bpy.context.active_object
    porch_floor.name = "MainDwelling_PorchFloor"
    porch_floor.scale = (PORCH_TOTAL_DEPTH/2, PORCH_WIDTH/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    porch_floor.data.materials.append(floor_mat)
    
    # Porch walls - wrap the 2.5m width and first 1.5m of depth
    
    # North porch wall (runs E-W for 1.5m)
    porch_wall_x = ox - LENGTH/2 - PORCH_WALL_DEPTH/2
    north_porch_wall_y = oy + PORCH_WIDTH/2 - PORCH_WALL_THICKNESS/2
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_wall_x, north_porch_wall_y, oz + PORCH_HEIGHT/2))
    north_porch_wall = bpy.context.active_object
    north_porch_wall.name = "MainDwelling_PorchWall_North"
    north_porch_wall.scale = (PORCH_WALL_DEPTH/2, PORCH_WALL_THICKNESS/2, PORCH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    north_porch_wall.data.materials.append(porch_mat)
    
    # South porch wall (runs E-W for 1.5m)
    south_porch_wall_y = oy - PORCH_WIDTH/2 + PORCH_WALL_THICKNESS/2
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_wall_x, south_porch_wall_y, oz + PORCH_HEIGHT/2))
    south_porch_wall = bpy.context.active_object
    south_porch_wall.name = "MainDwelling_PorchWall_South"
    south_porch_wall.scale = (PORCH_WALL_DEPTH/2, PORCH_WALL_THICKNESS/2, PORCH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    south_porch_wall.data.materials.append(porch_mat)
    
    # West porch wall (partial - connects north and south walls at 1.5m mark)
    west_porch_wall_x = ox - LENGTH/2 - PORCH_WALL_DEPTH + PORCH_WALL_THICKNESS/2
    porch_wall_span = PORCH_WIDTH - 2*PORCH_WALL_THICKNESS  # Between north and south walls
    
    bpy.ops.mesh.primitive_cube_add(location=(west_porch_wall_x, oy, oz + PORCH_HEIGHT/2))
    west_porch_wall = bpy.context.active_object
    west_porch_wall.name = "MainDwelling_PorchWall_West"
    west_porch_wall.scale = (PORCH_WALL_THICKNESS/2, porch_wall_span/2, PORCH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    west_porch_wall.data.materials.append(porch_mat)
    
    # Porch entrance door on west wall
    # Position needs to be on OUTER face of wall (west side)
    porch_door_x = ox - LENGTH/2 - PORCH_WALL_DEPTH  # Outer face, not center
    print(f"Adding porch door at x={porch_door_x}, y={oy}, z={oz + 1.0}")
    add_window("MainDwelling_PorchWall_West", (porch_door_x, oy, oz + 1.0), 
               width=0.9, height=2.0, depth=PORCH_WALL_THICKNESS, axis='X', inward_offset='+X')
    print("Porch door window call completed")
    
    # Porch gable roof - 35Â° pitch, ridge running E-W like main roof
    PORCH_ROOF_PITCH = 35
    PORCH_ROOF_OVERHANG = 0.3  # Small overhang
    
    porch_roof_height_from_eaves = (PORCH_WIDTH / 2) * math.tan(math.radians(PORCH_ROOF_PITCH))
    porch_eave_height = oz + PORCH_HEIGHT
    porch_ridge_height = porch_eave_height + porch_roof_height_from_eaves
    
    # Create porch roof mesh
    porch_roof_mesh = bpy.data.meshes.new("MainDwelling_PorchRoofMesh")
    porch_roof_obj = bpy.data.objects.new("MainDwelling_PorchRoof", porch_roof_mesh)
    bpy.context.collection.objects.link(porch_roof_obj)
    
    # Porch roof vertices with overhang
    porch_roof_length = PORCH_TOTAL_DEPTH + 2 * PORCH_ROOF_OVERHANG
    porch_roof_west = ox - LENGTH/2 - PORCH_TOTAL_DEPTH - PORCH_ROOF_OVERHANG
    porch_roof_east = ox - LENGTH/2 + PORCH_ROOF_OVERHANG
    porch_roof_north = oy + PORCH_WIDTH/2 + PORCH_ROOF_OVERHANG
    porch_roof_south = oy - PORCH_WIDTH/2 - PORCH_ROOF_OVERHANG
    
    porch_verts = [
        # North eave edge
        (porch_roof_east, porch_roof_north, porch_eave_height),
        (porch_roof_west, porch_roof_north, porch_eave_height),
        # Ridge line (center)
        (porch_roof_east, oy, porch_ridge_height),
        (porch_roof_west, oy, porch_ridge_height),
        # South eave edge
        (porch_roof_east, porch_roof_south, porch_eave_height),
        (porch_roof_west, porch_roof_south, porch_eave_height),
    ]
    
    porch_faces = [
        (0, 1, 3, 2),  # North roof slope
        (2, 3, 5, 4),  # South roof slope
    ]
    
    porch_roof_mesh.from_pydata(porch_verts, [], porch_faces)
    porch_roof_mesh.update()
    porch_roof_obj.data.materials.append(get_metal_roof_material())
    
    # UV unwrap for texture display
    bpy.context.view_layer.objects.active = porch_roof_obj
    porch_roof_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    porch_roof_obj.select_set(False)
    
    # Large opening in main building's west wall connecting to porch
    add_window("MainDwelling_WestWall_Ground", (ox - LENGTH/2, oy, oz + 1.1), 
               width=2.0, height=2.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # === INTERIOR PARTITIONS ===
    _create_interior_partitions_ground_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS)
    _create_interior_partitions_first_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS)
    
    # === ENSUITE FURNITURE ===
    _furnish_master_ensuite(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS)
    
    # === KITCHEN BENCH ===
    _create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
    
    # === DINING TABLE ===
    _create_dining_table(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
    
    # === WINDOWS AND DOORS ===
    _add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS)
    
    # === GABLE ROOF ===
    if show_roof:
        _create_gable_roof(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, roof_style, potius_mat)
    
    print(f"Main Dwelling built at origin {origin}")


def build_main_dwelling_simple_porch(origin=(0, 0, 0), show_roof=True, roof_style="traditional"):
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
    WIDTH = 7.0  # Total north-south dimension (roof span)
    ENCLOSED_WIDTH = 6.0  # Enclosed building width (north wall recessed 1m)
    NORTH_RECESS = 1.0  # North wall recessed to create patio/balcony
    LENGTH = 9.0
    GROUND_FLOOR_HEIGHT = 2.5
    FIRST_FLOOR_HEIGHT = 2.4
    TOTAL_HEIGHT = GROUND_FLOOR_HEIGHT + FIRST_FLOOR_HEIGHT
    EXTERIOR_WALL_THICKNESS = 0.20
    INTERIOR_WALL_THICKNESS = 0.11
    ROOF_PITCH = 35
    ROOF_OVERHANG = 0.6
    
    # Materials
    import os
    texture_path = os.path.join(os.path.dirname(__file__), "textures", "thermal-redwood--shou-sugi-ban--char--brushed--black-rainscreen-117-1235-mm-architextures.jpg")
    potius_mat = create_textured_material("PotiusExterior", texture_path)
    floor_mat = get_floor_wood_material()
    
    # === CREATE SHARED COMPONENTS ===
    _create_exterior_walls(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS, potius_mat)
    _create_floors(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, floor_mat)
    
    # === SIMPLE OPEN ENTRANCE PORCH (WEST SIDE) ===
    
    # Porch dimensions: 2.5m wide Ã— 1.5m deep, OPEN (no walls)
    PORCH_WIDTH = 2.5   # North-south dimension
    PORCH_DEPTH = 1.5   # East-west depth
    
    # Porch deck - positioned west of west wall, centered
    porch_center_x = ox - LENGTH/2 - PORCH_DEPTH/2
    porch_center_y = oy  # Centered on building
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_center_x, porch_center_y, oz + 0.05))
    porch_deck = bpy.context.active_object
    porch_deck.name = "MainDwelling_PorchDeck_Simple"
    porch_deck.scale = (PORCH_DEPTH/2, PORCH_WIDTH/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    porch_deck.data.materials.append(floor_mat)
    
    # UV unwrap for porch deck texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Steps down from porch deck on west side - using decking material
    STEP_WIDTH = 2.5  # Full porch width (north-south)
    STEP_DEPTH = 0.4  # 400mm deep (east-west)
    STEP_HEIGHT = 0.15  # 150mm rise per step
    deck_texture_path = os.path.join(os.path.dirname(__file__), "textures", "knotted-timber-staggered-1995-mm-architextures.jpg")
    deck_mat = create_textured_material("TimberDecking", deck_texture_path)
    
    # First step (closer to porch)
    step1_x = ox - LENGTH/2 - PORCH_DEPTH - STEP_DEPTH/2
    step1_z = oz + 0.05 - STEP_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(step1_x, porch_center_y, step1_z))
    step1 = bpy.context.active_object
    step1.name = "MainDwelling_PorchStep1_Simple"
    step1.scale = (STEP_DEPTH/2, STEP_WIDTH/2, STEP_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    step1.data.materials.append(deck_mat)
    
    # UV unwrap for texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Second step (further from porch)
    step2_x = step1_x + STEP_DEPTH
    step2_z = step1_z - STEP_HEIGHT
    
    bpy.ops.mesh.primitive_cube_add(location=(step2_x, porch_center_y, step2_z))
    step2 = bpy.context.active_object
    step2.name = "MainDwelling_PorchStep2_Simple"
    step2.scale = (STEP_DEPTH/2, STEP_WIDTH/2, STEP_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    step2.data.materials.append(deck_mat)
    
    # UV unwrap for texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Main entrance door on MAIN BUILDING'S WEST WALL (not on porch)
    # Door: 0.9m wide × 2.0m high, centered on west wall
    main_door_x = ox - LENGTH/2  # On west wall face
    add_window("MainDwelling_WestWall_Ground", (main_door_x, oy, oz + 1.0), width=0.9, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # Monopitch porch roof - single slope, high at building, low at outer edge
    PORCH_ROOF_PITCH = 15  # degrees (gentler slope for monopitch)
    PORCH_ROOF_OVERHANG = 0.3  # Small overhang on sides and front
    
    # Roof starts at eave height (top of ground floor walls) and slopes downward
    porch_roof_high_height = oz + GROUND_FLOOR_HEIGHT
    porch_roof_drop = PORCH_DEPTH * math.tan(math.radians(PORCH_ROOF_PITCH))
    porch_roof_low_height = porch_roof_high_height - porch_roof_drop
    
    # Support posts on west edge of porch (to hold up roof)
    POST_SIZE = 0.15  # 150mm x 150mm posts
    POST_INSET = 0.2  # 200mm inset from north/south edges (wider spacing)
    post_x = ox - LENGTH/2 - PORCH_DEPTH  # West edge of deck
    post_height = porch_roof_low_height - oz  # Height to match sloped roof at west edge
    
    # North post
    post_north_y = oy + PORCH_WIDTH/2 - POST_INSET
    bpy.ops.mesh.primitive_cube_add(location=(post_x, post_north_y, oz + post_height/2))
    post_north = bpy.context.active_object
    post_north.name = "MainDwelling_PorchPost_North"
    post_north.scale = (POST_SIZE/2, POST_SIZE/2, post_height/2)
    bpy.ops.object.transform_apply(scale=True)
    post_north.data.materials.append(floor_mat)
    
    # South post
    post_south_y = oy - PORCH_WIDTH/2 + POST_INSET
    bpy.ops.mesh.primitive_cube_add(location=(post_x, post_south_y, oz + post_height/2))
    post_south = bpy.context.active_object
    post_south.name = "MainDwelling_PorchPost_South"
    post_south.scale = (POST_SIZE/2, POST_SIZE/2, post_height/2)
    bpy.ops.object.transform_apply(scale=True)
    post_south.data.materials.append(floor_mat)
    PORCH_ROOF_PITCH = 15  # degrees (gentler slope for monopitch)
    PORCH_ROOF_OVERHANG = 0.3  # Small overhang on sides and front
    
    # Roof starts at eave height (top of ground floor walls) and slopes downward
    porch_roof_high_height = oz + GROUND_FLOOR_HEIGHT
    porch_roof_drop = PORCH_DEPTH * math.tan(math.radians(PORCH_ROOF_PITCH))
    porch_roof_low_height = porch_roof_high_height - porch_roof_drop
    
    # Create monopitch roof mesh
    porch_roof_mesh = bpy.data.meshes.new("MainDwelling_PorchRoof_Monopitch")
    porch_roof_obj = bpy.data.objects.new("MainDwelling_PorchRoof_Simple", porch_roof_mesh)
    bpy.context.collection.objects.link(porch_roof_obj)
    
    # Roof extends with overhang on north, south, and west sides
    porch_roof_building = ox - LENGTH/2  # Flush with building wall (should be HIGH)
    porch_roof_outer = ox - LENGTH/2 - PORCH_DEPTH - PORCH_ROOF_OVERHANG  # Outer edge with overhang (should be LOW)
    porch_roof_north = oy + PORCH_WIDTH/2 + PORCH_ROOF_OVERHANG
    porch_roof_south = oy - PORCH_WIDTH/2 - PORCH_ROOF_OVERHANG
    
    porch_verts = [
        # Building edge should be HIGH, outer should be LOW (swap these to fix rendering)
        (porch_roof_building, porch_roof_north, porch_roof_low_height),  # 0: At building (swap to LOW)
        (porch_roof_building, porch_roof_south, porch_roof_low_height),  # 1: At building (swap to LOW)
        # Outer edge  
        (porch_roof_outer, porch_roof_north, porch_roof_high_height),   # 2: At outer edge (swap to HIGH)
        (porch_roof_outer, porch_roof_south, porch_roof_high_height),   # 3: At outer edge (swap to HIGH)
    ]
    
    porch_faces = [
        (0, 1, 3, 2),  # Single sloped roof plane
    ]
    
    porch_roof_mesh.from_pydata(porch_verts, [], porch_faces)
    porch_roof_mesh.update()
    porch_roof_obj.data.materials.append(get_metal_roof_material())
    
    # UV unwrap for texture display
    bpy.context.view_layer.objects.active = porch_roof_obj
    porch_roof_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    porch_roof_obj.select_set(False)
    
    # Add roof structure for realism
    FASCIA_HEIGHT = 0.20  # 200mm fascia board height
    FASCIA_THICKNESS = 0.025  # 25mm thickness
    PURLIN_SIZE = (0.090, 0.045)  # 90mm x 45mm purlins (W x H)
    
    # Fascia board along west (low) edge
    fascia_west_x = porch_roof_west - FASCIA_THICKNESS/2
    fascia_west_y = (porch_roof_north + porch_roof_south) / 2
    fascia_west_z = porch_roof_low_height - FASCIA_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(fascia_west_x, fascia_west_y, fascia_west_z))
    fascia_west = bpy.context.active_object
    fascia_west.name = "MainDwelling_PorchRoof_FasciaWest"
    fascia_west_length = porch_roof_south - porch_roof_north
    fascia_west.scale = (FASCIA_THICKNESS/2, fascia_west_length/2, FASCIA_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    fascia_west.data.materials.append(floor_mat)
    
    # Fascia board along north edge
    fascia_north_x = (porch_roof_east + porch_roof_west) / 2
    fascia_north_y = porch_roof_north + FASCIA_THICKNESS/2
    fascia_north_z_high = porch_roof_high_height - FASCIA_HEIGHT/2
    fascia_north_z_low = porch_roof_low_height - FASCIA_HEIGHT/2
    fascia_north_z = (fascia_north_z_high + fascia_north_z_low) / 2
    fascia_north_length = porch_roof_west - porch_roof_east
    
    bpy.ops.mesh.primitive_cube_add(location=(fascia_north_x, fascia_north_y, fascia_north_z))
    fascia_north = bpy.context.active_object
    fascia_north.name = "MainDwelling_PorchRoof_FasciaNorth"
    fascia_north.scale = (fascia_north_length/2, FASCIA_THICKNESS/2, FASCIA_HEIGHT/2)
    # Rotate to follow roof slope
    fascia_north.rotation_euler[1] = math.radians(PORCH_ROOF_PITCH)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    fascia_north.data.materials.append(floor_mat)
    
    # Fascia board along south edge
    fascia_south_y = porch_roof_south - FASCIA_THICKNESS/2
    
    bpy.ops.mesh.primitive_cube_add(location=(fascia_north_x, fascia_south_y, fascia_north_z))
    fascia_south = bpy.context.active_object
    fascia_south.name = "MainDwelling_PorchRoof_FasciaSouth"
    fascia_south.scale = (fascia_north_length/2, FASCIA_THICKNESS/2, FASCIA_HEIGHT/2)
    # Rotate to follow roof slope
    fascia_south.rotation_euler[1] = math.radians(PORCH_ROOF_PITCH)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    fascia_south.data.materials.append(floor_mat)
    
    # Purlins (horizontal beams running east-west across the roof)
    PURLIN_SPACING = 0.6  # 600mm spacing
    num_purlins = int((porch_roof_west - porch_roof_east) / PURLIN_SPACING)
    
    for i in range(1, num_purlins):
        purlin_x = porch_roof_east + (i * PURLIN_SPACING)
        purlin_y = (porch_roof_north + porch_roof_south) / 2
        # Calculate height along the slope
        distance_from_high = purlin_x - porch_roof_east
        slope_drop = distance_from_high * math.tan(math.radians(PORCH_ROOF_PITCH))
        purlin_z = porch_roof_high_height - slope_drop - PURLIN_SIZE[1]/2
        
        bpy.ops.mesh.primitive_cube_add(location=(purlin_x, purlin_y, purlin_z))
        purlin = bpy.context.active_object
        purlin.name = f"MainDwelling_PorchRoof_Purlin_{i}"
        purlin_length = porch_roof_south - porch_roof_north
        purlin.scale = (PURLIN_SIZE[0]/2, purlin_length/2, PURLIN_SIZE[1]/2)
        bpy.ops.object.transform_apply(scale=True)
        purlin.data.materials.append(floor_mat)
    
    # === INTERIOR PARTITIONS ===
    _create_interior_partitions_ground_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS)
    _create_interior_partitions_first_floor(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, FIRST_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, INTERIOR_WALL_THICKNESS, NORTH_RECESS)
    
    # === ENSUITE FURNITURE ===
    _furnish_master_ensuite(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS)
    
    # === KITCHEN BENCH ===
    _create_kitchen_bench(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
    
    # === DINING TABLE ===
    _create_dining_table(ox, oy, oz, WIDTH, LENGTH, EXTERIOR_WALL_THICKNESS)
    
    # === WINDOWS AND DOORS ===
    _add_exterior_windows_and_doors(ox, oy, oz, WIDTH, ENCLOSED_WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, NORTH_RECESS)
    
    # === FIRST FLOOR BALCONY RAILING (North Edge) ===
    RAILING_HEIGHT = 1.0  # 1 meter high
    RAILING_POST_SIZE = 0.075  # 75mm square posts
    RAILING_RAIL_HEIGHT = 0.050  # 50mm high horizontal rails
    RAILING_RAIL_DEPTH = 0.040  # 40mm deep horizontal rails
    POST_SPACING = 1.5  # 1.5m between posts
    
    # Railing position - along north edge of first floor balcony
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    railing_y = oy + WIDTH/2  # At the north edge of the balcony (1m north of recessed wall)
    railing_west_x = ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS  # Inside west wall
    railing_east_x = ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS  # Inside east wall
    railing_length = railing_east_x - railing_west_x
    
    # Material for railing - use treated timber
    railing_mat = create_material("RailingTimber", (0.55, 0.45, 0.35, 1))
    
    # Create posts at regular intervals
    num_posts = int(railing_length / POST_SPACING) + 1
    actual_spacing = railing_length / (num_posts - 1) if num_posts > 1 else railing_length
    
    for i in range(num_posts):
        post_x = railing_west_x + (i * actual_spacing)
        post_z = first_floor_z + RAILING_HEIGHT/2
        
        bpy.ops.mesh.primitive_cube_add(location=(post_x, railing_y, post_z))
        post = bpy.context.active_object
        post.name = f"MainDwelling_BalconyRailing_Post_{i+1:02d}"
        post.scale = (RAILING_POST_SIZE/2, RAILING_POST_SIZE/2, RAILING_HEIGHT/2)
        bpy.ops.object.transform_apply(scale=True)
        post.data.materials.append(railing_mat)
    
    # Top rail (horizontal)
    top_rail_x = (railing_west_x + railing_east_x) / 2
    top_rail_z = first_floor_z + RAILING_HEIGHT - RAILING_RAIL_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(top_rail_x, railing_y, top_rail_z))
    top_rail = bpy.context.active_object
    top_rail.name = "MainDwelling_BalconyRailing_TopRail"
    top_rail.scale = (railing_length/2, RAILING_RAIL_DEPTH/2, RAILING_RAIL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    top_rail.data.materials.append(railing_mat)
    
    # Middle rail (horizontal)
    mid_rail_z = first_floor_z + RAILING_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(top_rail_x, railing_y, mid_rail_z))
    mid_rail = bpy.context.active_object
    mid_rail.name = "MainDwelling_BalconyRailing_MidRail"
    mid_rail.scale = (railing_length/2, RAILING_RAIL_DEPTH/2, RAILING_RAIL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    mid_rail.data.materials.append(railing_mat)
    
    # Bottom rail (horizontal)
    bottom_rail_z = first_floor_z + 0.15  # 150mm above floor level
    
    bpy.ops.mesh.primitive_cube_add(location=(top_rail_x, railing_y, bottom_rail_z))
    bottom_rail = bpy.context.active_object
    bottom_rail.name = "MainDwelling_BalconyRailing_BottomRail"
    bottom_rail.scale = (railing_length/2, RAILING_RAIL_DEPTH/2, RAILING_RAIL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    bottom_rail.data.materials.append(railing_mat)
    
    # === GABLE ROOF ===
    if show_roof:
        _create_gable_roof(ox, oy, oz, WIDTH, LENGTH, TOTAL_HEIGHT, ROOF_PITCH, ROOF_OVERHANG, roof_style, potius_mat)
    
    print(f"Main Dwelling with simple open porch built at origin {origin}") 
