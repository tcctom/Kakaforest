import bpy  # type: ignore
import math

from utils import create_corrugated_iron_material, add_corner_trim, add_window, add_door

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build(origin=(0,0,0), show_roof=True):  # Set show_roof=False to hide roof
    """
    Build a two-level wet wing with:
    - Lower Level (40m²): 10m x 4m - Entry & Utility wing
    - Upper Level (60m²): 10m x 6m - Sanctuary wing
    
    Layout:
    - Lower: Mudroom (SW corner), staircase, guest suite + bathroom/laundry
    - Upper: Great room (full 10m north wall), master suite (SE corner), deck
    """
    ox, oy, oz = origin
    W, D = 10.0, 6.0  # Changed from 6.0, 6.0 to 10.0 (X-width), 6.0 (Y-depth)
    H_BASE = 2.4
    EXTERIOR_WALL_THICKNESS = 0.15  # 150mm exterior walls
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
    
    # Floor (stairwell opening will be created from build_under_extension)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + 0.05))
    floor = bpy.context.active_object
    floor.name = "WetWing2_Floor"
    floor.scale = (W/2, D/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    floor.data.materials.append(create_material("FloorWood", (0.5, 0.35, 0.2, 1)))
    
    # === UPPER LEVEL (60m²) - This entire 10m x 6m building ===
    # This is the sanctuary wing - great room with full north wall, master suite
    # The lower level (40m²) is a separate 10m x 4m structure built by build_under_extension()
    # No internal floor division needed - this whole building is one open upper level
    
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
    
    # Internal partition wall running north-south, aligned with west edge of stairs
    INTERNAL_WALL_THICKNESS = 0.1  # 100mm internal wall
    INTERNAL_WALL_HEIGHT = 2.4  # Standard room height
    partition_x = ox + 1.2  # Aligns with west edge of staircase (stair_x + STAIR_WIDTH/2)
    
    bpy.ops.mesh.primitive_cube_add(location=(partition_x, oy, oz + INTERNAL_WALL_HEIGHT/2))
    partition_wall = bpy.context.active_object
    partition_wall.name = "WetWing2_PartitionWall"
    partition_wall.scale = (INTERNAL_WALL_THICKNESS/2, (D - 2*EXTERIOR_WALL_THICKNESS)/2, INTERNAL_WALL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Use white paint material for internal wall
    white_wall_mat = create_material("WhiteWall", (0.95, 0.95, 0.95, 1))
    partition_wall.data.materials.append(white_wall_mat)
    
    # Add two door openings in the partition wall - one near north, one near south
    # Wall runs from oy - 2.85 to oy + 2.85 (5.7m total length)
    # North door: 0.5m from north edge
    add_door("WetWing2_PartitionWall", position=(partition_x, oy - D/2 + EXTERIOR_WALL_THICKNESS + 0.5, oz), 
             width=0.9, height=2.1, depth=INTERNAL_WALL_THICKNESS, axis='X')
    # South door: 0.5m from south edge  
    add_door("WetWing2_PartitionWall", position=(partition_x, oy + D/2 - EXTERIOR_WALL_THICKNESS - 0.5, oz), 
             width=0.9, height=2.1, depth=INTERNAL_WALL_THICKNESS, axis='X')
    
    # Internal wall running east-west, 4m south of north wall, connecting west wall to partition
    cross_wall_y = oy - D/2 + 4.0  # 4m south of north wall
    cross_wall_length = (W/2 - EXTERIOR_WALL_THICKNESS) - (partition_x - ox)  # From west wall inner edge to partition center
    cross_wall_x = partition_x + cross_wall_length/2  # Centered between partition and west wall
    
    bpy.ops.mesh.primitive_cube_add(location=(cross_wall_x, cross_wall_y, oz + INTERNAL_WALL_HEIGHT/2))
    cross_wall = bpy.context.active_object
    cross_wall.name = "WetWing2_CrossWall"
    cross_wall.scale = (cross_wall_length/2, INTERNAL_WALL_THICKNESS/2, INTERNAL_WALL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    cross_wall.data.materials.append(white_wall_mat)
    
    # Add door opening in cross wall near west wall
    door_x_position = ox + W/2 - EXTERIOR_WALL_THICKNESS - 0.5  # 0.5m from west wall inner edge
    add_door("WetWing2_CrossWall", position=(door_x_position, cross_wall_y, oz), 
             width=0.9, height=2.1, depth=INTERNAL_WALL_THICKNESS, axis='Y')
    
    # Additional north-south wall, 1.8m east of west wall, running from cross wall to south wall
    ns_wall_x = ox + W/2 - 1.9  # 1.8m from west wall inner edge
    ns_wall_length = (D/2 - EXTERIOR_WALL_THICKNESS) - (4.0 - D/2)  # From cross wall to south wall
    ns_wall_y = cross_wall_y + ns_wall_length/2  # Centered between cross wall and south wall
    
    bpy.ops.mesh.primitive_cube_add(location=(ns_wall_x, ns_wall_y, oz + INTERNAL_WALL_HEIGHT/2))
    ns_wall = bpy.context.active_object
    ns_wall.name = "WetWing2_NSWall"
    ns_wall.scale = (INTERNAL_WALL_THICKNESS/2, ns_wall_length/2, INTERNAL_WALL_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    ns_wall.data.materials.append(white_wall_mat)
    
    # Add windows on North face - spread across the 10m wide wall
    add_window("WetWing2_NorthWall", position=(ox-3.3, oy - D/2, oz+1.4), width=2.0, height=1.6, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox-3.3, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox, oy - D/2, oz+1.4), width=2.0, height=1.6, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox+3.3, oy - D/2, oz+1.4), width=2.0, height=1.6, depth=EXTERIOR_WALL_THICKNESS)
    add_window("WetWing2_NorthWall", position=(ox+3.3, oy - D/2, oz+3.0), width=2.0, height=0.9, depth=EXTERIOR_WALL_THICKNESS)
    
    # Add windows on South face - spread across the 10m wide wall
    add_window("WetWing2_SouthWall", position=(ox-3.3, oy + D/2, oz+1.4), width=2.0, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("WetWing2_SouthWall", position=(ox, oy + D/2, oz+1.4), width=2.0, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("WetWing2_SouthWall", position=(ox+3.3, oy + D/2, oz+1.4), width=2.0, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # Add windows on West face (+X side) - 6m deep wall
    add_window("WetWing2_WestWall", position=(ox + W/2, oy - D/2 + 1.3, oz + 1.4), width=1.5, height=1.4, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("WetWing2_WestWall", position=(ox + W/2, oy - D/2 + 3.1, oz + 1.4), width=1.5, height=1.4, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("WetWing2_WestWall", position=(ox + W/2, oy - D/2 + 4.9, oz + 1.4), width=1.5, height=1.4, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # Add windows on East face (-X side) - 6m deep wall
    add_window("WetWing2_EastWall", position=(ox - W/2, oy - D/2 + 2.0, oz + 1.6), width=2.2, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    add_window("WetWing2_EastWall", position=(ox - W/2, oy - D/2 + 4.7, oz + 1.0), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')


def furniture(origin=(0,0,0), building_width=10.0, building_depth=6.0, exterior_wall_thickness=0.15):
    """
    Add furniture to the Potius Wet Wing - Upper Level (60m²).
    
    This furnishes the main 10m x 6m building which is the upper sanctuary level.
    
    Upper Level: Great Room (kitchen, dining, lounge), Master Suite
    
    Args:
        origin: (x, y, z) tuple for building origin (already raised at z=2.4)
        building_width: Building width in meters (X-direction) - default 10.0
        building_depth: Building depth in meters (Y-direction) - default 6.0
        exterior_wall_thickness: Thickness of exterior walls in meters
    """
    ox, oy, oz = origin
    W, D = building_width, building_depth
    EXTERIOR_WALL_THICKNESS = exterior_wall_thickness
    
    # ==================== UPPER LEVEL (60m²) - This entire building ====================
    
    # === GREAT ROOM ===
    # Dining table in center of great room
    TABLE_LENGTH = 2.0
    TABLE_WIDTH = 1.0
    TABLE_HEIGHT = 0.75
    TABLE_THICKNESS = 0.05
    
    table_x = ox - 3    # Center of room
    table_y = oy - D/2 + 2.5  # Middle of north half
    table_z = oz + TABLE_HEIGHT
    
    bpy.ops.mesh.primitive_cube_add(location=(table_x, table_y, table_z))
    table = bpy.context.active_object
    table.name = "WetWing2_DiningTable"
    table.scale = (TABLE_LENGTH/2, TABLE_WIDTH/2, TABLE_THICKNESS/2)
    bpy.ops.object.transform_apply(scale=True)
    table.data.materials.append(create_material("OakTable", (0.65, 0.5, 0.35, 1)))
    
    # Lounge sofa facing north (view)
    SOFA_WIDTH = 2.5
    SOFA_DEPTH = 0.9
    SOFA_HEIGHT = 0.4
    SOFA_BACK_HEIGHT = 0.8
    
    sofa_x = ox - 3  # East side of great room
    sofa_y = oy - D/2 + 3.5
    sofa_z = oz + SOFA_HEIGHT/2
    
    # Sofa seat
    bpy.ops.mesh.primitive_cube_add(location=(sofa_x, sofa_y, sofa_z))
    sofa_seat = bpy.context.active_object
    sofa_seat.name = "WetWing2_SofaSeat"
    sofa_seat.scale = (SOFA_WIDTH/2, SOFA_DEPTH/2, SOFA_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    sofa_seat.data.materials.append(create_material("SofaFabric", (0.35, 0.45, 0.5, 1)))
    
    # Sofa back
    sofa_back_z = oz + SOFA_HEIGHT + SOFA_BACK_HEIGHT/2
    sofa_back_y = sofa_y + SOFA_DEPTH/2 - 0.1
    
    bpy.ops.mesh.primitive_cube_add(location=(sofa_x, sofa_back_y, sofa_back_z))
    sofa_back = bpy.context.active_object
    sofa_back.name = "WetWing2_SofaBack"
    sofa_back.scale = (SOFA_WIDTH/2, 0.15/2, SOFA_BACK_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    sofa_back.data.materials.append(create_material("SofaFabric", (0.35, 0.45, 0.5, 1)))
    
    # === MASTER SUITE (Northwest Corner Room - 3.6m x 4m) ===
    # King bed with headboard against west side of north-south partition wall
    MASTER_BED_WIDTH = 2.0  # meters (X-direction) - king bed
    MASTER_BED_LENGTH = 1.8  # meters (Y-direction)
    MASTER_BED_HEIGHT = 0.5
    
    # Partition wall is at ox + W/2 - 3.6, bed is west of partition (in the NW room)
    partition_x = ox + W/2 - 3.6
    master_bed_x = partition_x + MASTER_BED_WIDTH/2 + 0.05  # West of partition (higher X), headboard against partition
    master_bed_y = oy - D/2 + EXTERIOR_WALL_THICKNESS + MASTER_BED_LENGTH/2 + 1  # Near north wall
    master_bed_z = oz + MASTER_BED_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(master_bed_x, master_bed_y, master_bed_z))
    master_bed = bpy.context.active_object
    master_bed.name = "WetWing2_MasterBed"
    master_bed.scale = (MASTER_BED_WIDTH/2, MASTER_BED_LENGTH/2, MASTER_BED_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    master_bed.data.materials.append(create_material("MasterBedding", (0.25, 0.3, 0.4, 1)))
    
    # Master bedside table - on west side of bed (away from partition)
    NIGHTSTAND_SIZE = 0.5
    NIGHTSTAND_HEIGHT = 0.6
    
    nightstand_x = master_bed_x + MASTER_BED_WIDTH/2 + NIGHTSTAND_SIZE/2 + 0.1  # West side of bed (higher X)
    nightstand_y = master_bed_y
    nightstand_z = oz + NIGHTSTAND_HEIGHT/2
    
    bpy.ops.mesh.primitive_cube_add(location=(nightstand_x, nightstand_y, nightstand_z))
    nightstand = bpy.context.active_object
    nightstand.name = "WetWing2_Nightstand"
    nightstand.scale = (NIGHTSTAND_SIZE/2, NIGHTSTAND_SIZE/2, NIGHTSTAND_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    nightstand.data.materials.append(create_material("OakFurniture", (0.6, 0.45, 0.3, 1)))
