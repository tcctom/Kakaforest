import bpy  # type: ignore
import math

from utils import create_corrugated_iron_material, add_corner_trim, add_window

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_potius_wet_wing(origin=(0,0,0), show_roof=True):  # Set show_roof=False to hide roof
    ox, oy, oz = origin
    W, D = 6.0, 6.0
    H_BASE = 2.4
    EXTERIOR_WALL_THICKNESS = 0.15  # 150mm exterior walls
    INTERIOR_WALL_THICKNESS = 0.11  # 110mm interior wall
    ROOF_PITCH = 12  # degrees (skillion roof pitch)
    ROOF_HEIGHT_CENTER = 3.2  # meters above origin
    roof_thickness = 0.05
    
    # Calculate wall heights based on mono-pitch roof (north wall is HIGHER)
    # Roof tilts -12° (negative rotation lifts north edge)
    run_to_edge = D/2 + 0.3  # Distance from center to roof edge (3.3m)
    roof_rise = run_to_edge * math.sin(math.radians(ROOF_PITCH))  # ~0.686m (use sin for rotation)
    clearance = 0.03  # 30mm clearance so walls don't poke through roof
    
    # North wall (-Y) is taller, south wall (+Y) is shorter
    H_NORTH = ROOF_HEIGHT_CENTER + roof_rise - (roof_thickness/2) - clearance  # ~3.856m
    H_SOUTH = ROOF_HEIGHT_CENTER - roof_rise - (roof_thickness/2) - clearance  # ~2.490m
    
    # Create red cottage material
    red_mat = create_material("RedCottage", (0.7, 0.05, 0.05, 1))
    
    # Build 4 exterior walls as separate solid boxes
    # North Wall (Higher wall, -Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy - D/2 + EXTERIOR_WALL_THICKNESS/2, oz + H_NORTH/2))
    north_wall = bpy.context.active_object
    north_wall.name = "WetWing_NorthWall"
    north_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H_NORTH/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall.data.materials.append(red_mat)
    
    # South Wall (Lower wall, +Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy + D/2 - EXTERIOR_WALL_THICKNESS/2, oz + H_SOUTH/2))
    south_wall = bpy.context.active_object
    south_wall.name = "WetWing_SouthWall"
    south_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H_SOUTH/2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall.data.materials.append(red_mat)
    
    # West Wall (+X side) - Wall with sloped top matching roof
    mesh = bpy.data.meshes.new("WestWallMesh")
    west_wall = bpy.data.objects.new("WetWing_WestWall", mesh)
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
    east_wall = bpy.data.objects.new("WetWing_EastWall", mesh)
    bpy.context.collection.objects.link(east_wall)
    mesh.from_pydata(verts, [], faces)
    east_wall.location = (ox - W/2 + EXTERIOR_WALL_THICKNESS/2, oy, oz)  # EAST wall at -X (lower X = east)
    east_wall.data.materials.append(red_mat)
    
    # Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + 0.05))
    floor = bpy.context.active_object
    floor.name = "WetWing_Floor"
    floor.scale = (W/2, D/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    floor.data.materials.append(create_material("FloorWood", (0.5, 0.35, 0.2, 1)))
    
    # Interior Wall - North to South divider in the middle with sloped top
    mesh = bpy.data.meshes.new("InteriorWallMesh")
    interior_wall = bpy.data.objects.new("WetWing_InteriorWall", mesh)
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
    
    # Skillion Roof (HIGH ON NORTH: -Y)
    if show_roof:  # Set show_roof=False in function call to hide roof
        bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + ROOF_HEIGHT_CENTER))
        roof = bpy.context.active_object
        roof.name = "WetWing_Roof"
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
    nw_trim.name = "CornerTrim_NW"
    nw_trim.scale = (trim_width/2, trim_width/2, H_NORTH/2)
    bpy.ops.object.transform_apply(scale=True)
    nw_trim.data.materials.append(trim_mat)
    
    # NE Corner (tall)
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2, oy - D/2, oz + H_NORTH/2))
    ne_trim = bpy.context.active_object
    ne_trim.name = "CornerTrim_NE"
    ne_trim.scale = (trim_width/2, trim_width/2, H_NORTH/2)
    bpy.ops.object.transform_apply(scale=True)
    ne_trim.data.materials.append(trim_mat)
    
    # SE Corner (shorter)
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2, oy + D/2, oz + H_SOUTH/2))
    se_trim = bpy.context.active_object
    se_trim.name = "CornerTrim_SE"
    se_trim.scale = (trim_width/2, trim_width/2, H_SOUTH/2)
    bpy.ops.object.transform_apply(scale=True)
    se_trim.data.materials.append(trim_mat)
    
    # SW Corner (shorter)
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2, oy + D/2, oz + H_SOUTH/2))
    sw_trim = bpy.context.active_object
    sw_trim.name = "CornerTrim_SW"
    sw_trim.scale = (trim_width/2, trim_width/2, H_SOUTH/2)
    bpy.ops.object.transform_apply(scale=True)
    sw_trim.data.materials.append(trim_mat)
    
    # Add windows on North face (same dimensions as red cottage)
    add_window("WetWing_NorthWall", position=(ox-1.4, oy - D/2, oz+1.1), width=2.0, height=2.2, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing_NorthWall", position=(ox-1.4, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing_NorthWall", position=(ox+1.4, oy - D/2, oz+1.1), width=2.0, height=2.2, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing_NorthWall", position=(ox+1.4, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    
    # Add window on West face (0.5m wide, 1.2m tall, 0.8m off floor, 0.5m in from north)  
    # West = +X side (higher X values = west)
    add_window("WetWing_WestWall", position=(ox + W/2, oy - D/2 + 0.5, oz + 1.4), width=0.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # Verandah along north face (1.5m x 6m)
    VERANDAH_LENGTH = W  # 6.0m - full width of building
    VERANDAH_WIDTH = 1.5  # meters (depth from building, Y-direction)
    VERANDAH_HEIGHT = 0.1  # meters (thickness)
    
    verandah_x = ox  # Centered on building
    verandah_y = oy - D/2 - VERANDAH_WIDTH/2  # North of building
    verandah_z = oz + VERANDAH_HEIGHT/2  # Just above ground
    
    bpy.ops.mesh.primitive_cube_add(location=(verandah_x, verandah_y, verandah_z))
    verandah = bpy.context.active_object
    verandah.name = "WetWing_Verandah"
    verandah.scale = (VERANDAH_LENGTH/2, VERANDAH_WIDTH/2, VERANDAH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    verandah.data.materials.append(create_material("WoodenDecking", (0.55, 0.35, 0.18, 1)))
