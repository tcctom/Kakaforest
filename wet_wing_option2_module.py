import bpy  # type: ignore
import math

from utils import create_corrugated_iron_material, add_corner_trim, add_window, add_door
import wet_wing_option2_furniture

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_potius_wet_wing_option2(origin=(0,0,0), show_roof=True):  # Set show_roof=False to hide roof
    ox, oy, oz = origin
    W, D = 10.0, 6.0  # Changed from 6.0, 6.0 to 10.0 (X-width), 6.0 (Y-depth)
    H_BASE = 2.4
    EXTERIOR_WALL_THICKNESS = 0.15  # 150mm exterior walls
    INTERIOR_WALL_THICKNESS = 0.11  # 110mm interior wall
    ROOF_PITCH = 12  # degrees (skillion roof pitch)
    ROOF_HEIGHT_CENTER = 3.2  # meters above origin
    roof_thickness = 0.05
    
    # Calculate wall heights based on mono-pitch roof (north wall is HIGHER)
    # Roof tilts -12° (negative rotation lifts north edge)
    run_to_edge = D/2 + 0.3  # Distance from center to roof edge (5.3m for 10m depth)
    roof_rise = run_to_edge * math.sin(math.radians(ROOF_PITCH))  # ~1.103m (use sin for rotation)
    clearance = 0.03  # 30mm clearance so walls don't poke through roof
    
    # North wall (-Y) is taller, south wall (+Y) is shorter
    H_NORTH = ROOF_HEIGHT_CENTER + roof_rise - (roof_thickness/2) - clearance  # ~4.273m
    H_SOUTH = ROOF_HEIGHT_CENTER - roof_rise - (roof_thickness/2) - clearance  # ~2.073m
    
    # Create red cottage material
    red_mat = create_material("RedCottage", (0.7, 0.05, 0.05, 1))
    
    # Build 4 exterior walls as separate solid boxes
    # North Wall (Higher wall, -Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy - D/2 + EXTERIOR_WALL_THICKNESS/2, oz + H_NORTH/2))
    north_wall = bpy.context.active_object
    north_wall.name = "WetWing2_NorthWall"
    north_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H_NORTH/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall.data.materials.append(red_mat)
    
    # South Wall (Lower wall, +Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy + D/2 - EXTERIOR_WALL_THICKNESS/2, oz + H_SOUTH/2))
    south_wall = bpy.context.active_object
    south_wall.name = "WetWing2_SouthWall"
    south_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H_SOUTH/2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall.data.materials.append(red_mat)
    
    # West Wall (+X side) - Wall with sloped top matching roof
    mesh = bpy.data.meshes.new("WestWallMesh")
    west_wall = bpy.data.objects.new("WetWing2_WestWall", mesh)
    bpy.context.collection.objects.link(west_wall)
    
    # Wall positioned at west side, inner edge accounting for north/south wall thickness
    wall_depth = D - 2*EXTERIOR_WALL_THICKNESS
    half_depth = wall_depth / 2
    half_thick = EXTERIOR_WALL_THICKNESS / 2
    
    verts = [
        # Bottom face
        (-half_thick, -half_depth, 0),  # 0: SW bottom inner
        (half_thick, -half_depth, 0),   # 1: SW bottom outer
        (half_thick, half_depth, 0),    # 2: NW bottom outer
        (-half_thick, half_depth, 0),   # 3: NW bottom inner
        # Top face (north is taller)
        (-half_thick, -half_depth, H_NORTH),  # 4: N top inner
        (half_thick, -half_depth, H_NORTH),   # 5: N top outer
        (half_thick, half_depth, H_SOUTH),    # 6: S top outer
        (-half_thick, half_depth, H_SOUTH),   # 7: S top inner
    ]
    
    faces = [
        (0, 1, 2, 3),    # Bottom
        (4, 5, 6, 7),    # Top (sloped)
        (0, 4, 5, 1),    # North end
        (2, 6, 7, 3),    # South end
        (1, 5, 6, 2),    # Outer face
        (3, 7, 4, 0),    # Inner face
    ]
    
    mesh.from_pydata(verts, [], faces)
    west_wall.location = (ox + W/2 - EXTERIOR_WALL_THICKNESS/2, oy, oz)  # WEST wall at +X (higher X = west)
    west_wall.data.materials.append(red_mat)
    
    # East Wall (-X side) - Mirror of west wall
    mesh = bpy.data.meshes.new("EastWallMesh")
    east_wall = bpy.data.objects.new("WetWing2_EastWall", mesh)
    bpy.context.collection.objects.link(east_wall)
    mesh.from_pydata(verts, [], faces)
    east_wall.location = (ox - W/2 + EXTERIOR_WALL_THICKNESS/2, oy, oz)  # EAST wall at -X (lower X = east)
    east_wall.data.materials.append(red_mat)
    
    # Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + 0.05))
    floor = bpy.context.active_object
    floor.name = "WetWing2_Floor"
    floor.scale = (W/2, D/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    floor.data.materials.append(create_material("FloorWood", (0.5, 0.35, 0.2, 1)))
    
    # Interior Wall - North to South divider in the middle with sloped top
    mesh = bpy.data.meshes.new("InteriorWallMesh")
    interior_wall = bpy.data.objects.new("WetWing2_InteriorWall", mesh)
    bpy.context.collection.objects.link(interior_wall)
    
    half_thick_int = INTERIOR_WALL_THICKNESS / 2
    
    verts = [
        # Bottom face
        (-half_thick_int, -half_depth, 0),  # 0: N bottom west
        (half_thick_int, -half_depth, 0),   # 1: N bottom east
        (half_thick_int, half_depth, 0),    # 2: S bottom east
        (-half_thick_int, half_depth, 0),   # 3: S bottom west
        # Top face (north is taller)
        (-half_thick_int, -half_depth, H_NORTH),  # 4: N top west
        (half_thick_int, -half_depth, H_NORTH),   # 5: N top east
        (half_thick_int, half_depth, H_SOUTH),    # 6: S top east
        (-half_thick_int, half_depth, H_SOUTH),   # 7: S top west
    ]
    
    faces = [
        (0, 1, 2, 3),    # Bottom
        (4, 5, 6, 7),    # Top (sloped)
        (0, 4, 5, 1),    # North end
        (2, 6, 7, 3),    # South end
        (1, 5, 6, 2),    # East face
        (3, 7, 4, 0),    # West face
    ]
    
    mesh.from_pydata(verts, [], faces)
    interior_wall.location = (ox, oy, oz)
    interior_wall.data.materials.append(create_material("InteriorWhite", (0.95, 0.95, 0.95, 1)))
    
    # Add door to interior wall - 2m from north wall (north wall is at oy - D/2)
    # Interior wall runs N-S along X=0, so use axis='X' for the cut
    door_y_position = oy - D/2 + 2.0  # 2 meters from north wall
    add_door("WetWing2_InteriorWall", position=(ox, door_y_position, oz), width=0.9, height=2.1, depth=INTERIOR_WALL_THICKNESS, axis='X')
    
    # Skillion Roof (HIGH ON NORTH: -Y)
    if show_roof:  # Set show_roof=False in function call to hide roof
        bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + ROOF_HEIGHT_CENTER))
        roof = bpy.context.active_object
        roof.name = "WetWing2_Roof"
        roof.scale = (W/2 + 0.3, D/2 + 0.3, roof_thickness/2)
        roof.rotation_euler = (math.radians(-ROOF_PITCH), 0, 0)
        roof.data.materials.append(create_corrugated_iron_material())
    
    # Add white corner trim to all 4 corners (north corners are taller)
    # North corners use H_NORTH, south corners use H_SOUTH
    trim_mat = create_material("WhiteTrim", (1.0, 1.0, 1.0, 1))
    trim_width = 0.15
    
    # NW Corner (tall)
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2, oy - D/2, oz + H_NORTH/2))
    nw_trim = bpy.context.active_object
    nw_trim.name = "CornerTrim2_NW"
    nw_trim.scale = (trim_width/2, trim_width/2, H_NORTH/2)
    bpy.ops.object.transform_apply(scale=True)
    nw_trim.data.materials.append(trim_mat)
    
    # NE Corner (tall)
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2, oy - D/2, oz + H_NORTH/2))
    ne_trim = bpy.context.active_object
    ne_trim.name = "CornerTrim2_NE"
    ne_trim.scale = (trim_width/2, trim_width/2, H_NORTH/2)
    bpy.ops.object.transform_apply(scale=True)
    ne_trim.data.materials.append(trim_mat)
    
    # SE Corner (shorter)
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2, oy + D/2, oz + H_SOUTH/2))
    se_trim = bpy.context.active_object
    se_trim.name = "CornerTrim2_SE"
    se_trim.scale = (trim_width/2, trim_width/2, H_SOUTH/2)
    bpy.ops.object.transform_apply(scale=True)
    se_trim.data.materials.append(trim_mat)
    
    # SW Corner (shorter)
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2, oy + D/2, oz + H_SOUTH/2))
    sw_trim = bpy.context.active_object
    sw_trim.name = "CornerTrim2_SW"
    sw_trim.scale = (trim_width/2, trim_width/2, H_SOUTH/2)
    bpy.ops.object.transform_apply(scale=True)
    sw_trim.data.materials.append(trim_mat)
    
    # Add windows on North face - spread across the 10m wide wall
    add_window("WetWing2_NorthWall", position=(ox-3.5, oy - D/2, oz+1.1), width=2.0, height=2.2, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox-3.5, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox-0.5, oy - D/2, oz+1.1), width=2.0, height=2.2, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox-0.5, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox+2.5, oy - D/2, oz+1.1), width=2.0, height=2.2, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox+2.5, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    
    # Add windows on West face (+X side) - 6m deep wall
    add_window("WetWing2_WestWall", position=(ox + W/2, oy - D/2 + 0.6, oz + 1.4), width=0.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("WetWing2_WestWall", position=(ox + W/2, oy - D/2 + 2.4, oz + 1.4), width=0.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("WetWing2_WestWall", position=(ox + W/2, oy - D/2 + 4.2, oz + 1.4), width=0.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # Add windows on East face (-X side) - 6m deep wall
    add_window("WetWing2_EastWall", position=(ox - W/2, oy - D/2 + 1.5, oz + 1.0), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    add_window("WetWing2_EastWall", position=(ox - W/2, oy - D/2 + 4.0, oz + 1.0), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')


def build_under_extension(origin=(0,0,0)):
    """
    Build a 10m (X) by 4m (Y) extension module that sits underneath the main wet wing.
    This has flat-topped walls at 2.4m height with no roof (roof is provided by main building above).
    
    Args:
        origin: (x, y, z) tuple for the south edge of this extension (which connects to main wet wing north wall)
    """
    ox, oy, oz = origin
    W, D = 10.0, 4.0  # 10m wide (X), 4m deep (Y)
    H = 2.4  # Simple flat wall height
    EXTERIOR_WALL_THICKNESS = 0.15  # 150mm exterior walls
    
    # Create red cottage material
    red_mat = create_material("RedCottage", (0.7, 0.05, 0.05, 1))
    
    # Build 4 simple walls - all same height
    # North Wall (Front of extension, -Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy - D/2 + EXTERIOR_WALL_THICKNESS/2, oz + H/2))
    north_wall = bpy.context.active_object
    north_wall.name = "UnderExt_NorthWall"
    north_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall.data.materials.append(red_mat)
    
    # South Wall (+Y side) - Connects to main wet wing
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy + D/2 - EXTERIOR_WALL_THICKNESS/2, oz + H/2))
    south_wall = bpy.context.active_object
    south_wall.name = "UnderExt_SouthWall"
    south_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall.data.materials.append(red_mat)
    
    # West Wall (+X side)
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2 - EXTERIOR_WALL_THICKNESS/2, oy, oz + H/2))
    west_wall = bpy.context.active_object
    west_wall.name = "UnderExt_WestWall"
    west_wall.scale = (EXTERIOR_WALL_THICKNESS/2, (D - 2*EXTERIOR_WALL_THICKNESS)/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall.data.materials.append(red_mat)
    
    # East Wall (-X side)
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2 + EXTERIOR_WALL_THICKNESS/2, oy, oz + H/2))
    east_wall = bpy.context.active_object
    east_wall.name = "UnderExt_EastWall"
    east_wall.scale = (EXTERIOR_WALL_THICKNESS/2, (D - 2*EXTERIOR_WALL_THICKNESS)/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    east_wall.data.materials.append(red_mat)
    
    # Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + 0.05))
    floor = bpy.context.active_object
    floor.name = "UnderExt_Floor"
    floor.scale = (W/2, D/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    floor.data.materials.append(create_material("FloorWood", (0.5, 0.35, 0.2, 1)))
    
    # Add corner trim (all same height)
    trim_mat = create_material("WhiteTrim", (1.0, 1.0, 1.0, 1))
    trim_width = 0.15
    
    # NW Corner
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2, oy - D/2, oz + H/2))
    nw_trim = bpy.context.active_object
    nw_trim.name = "UnderExtTrim_NW"
    nw_trim.scale = (trim_width/2, trim_width/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    nw_trim.data.materials.append(trim_mat)
    
    # NE Corner
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2, oy - D/2, oz + H/2))
    ne_trim = bpy.context.active_object
    ne_trim.name = "UnderExtTrim_NE"
    ne_trim.scale = (trim_width/2, trim_width/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    ne_trim.data.materials.append(trim_mat)
    
    # SE Corner
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2, oy + D/2, oz + H/2))
    se_trim = bpy.context.active_object
    se_trim.name = "UnderExtTrim_SE"
    se_trim.scale = (trim_width/2, trim_width/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    se_trim.data.materials.append(trim_mat)
    
    # SW Corner
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2, oy + D/2, oz + H/2))
    sw_trim = bpy.context.active_object
    sw_trim.name = "UnderExtTrim_SW"
    sw_trim.scale = (trim_width/2, trim_width/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    sw_trim.data.materials.append(trim_mat)
    
    # Add windows on North face - spread across the 10m wide wall
    add_window("UnderExt_NorthWall", position=(ox-3.0, oy - D/2, oz+1.1), width=1.5, height=2.0, depth=EXTERIOR_WALL_THICKNESS)
    add_window("UnderExt_NorthWall", position=(ox-0.5, oy - D/2, oz+1.1), width=1.5, height=2.0, depth=EXTERIOR_WALL_THICKNESS)
    add_window("UnderExt_NorthWall", position=(ox+2.0, oy - D/2, oz+1.1), width=1.5, height=2.0, depth=EXTERIOR_WALL_THICKNESS)
    
    # Add windows on West and East walls - 4m deep walls
    add_window("UnderExt_WestWall", position=(ox + W/2, oy - D/2 + 2.0, oz + 1.2), width=0.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    add_window("UnderExt_EastWall", position=(ox - W/2, oy - D/2 + 2.0, oz + 1.2), width=0.5, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # Add door on south wall to connect to main house
    add_door("UnderExt_SouthWall", position=(ox, oy + D/2, oz), width=0.9, height=2.1, depth=EXTERIOR_WALL_THICKNESS, axis='Y')
