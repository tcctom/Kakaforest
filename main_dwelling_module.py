import bpy  # type: ignore
import math

from utils import apply_shadowclad_grooves, add_window, create_corrugated_iron_material, add_corner_trim

def create_material(name, color):
    """Create or get a material with the given name and color"""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_main_dwelling(origin=(0, 0, 0), show_roof=True, roof_style="traditional"):
    """
    Build the main dwelling structure based on specifications:
    - 6m × 8m rectangular base (8m runs east-west)
    - Two stories: ground floor 2.5m ceiling, first floor 2.4m ceiling
    - Potius residential system with 200mm exterior walls
    - Interior walls 110mm
    - Gable roof, 35° pitch, ridge runs east-west
    - Windows/doors on north and east walls
    
    Args:
        origin: (x, y, z) tuple for building location
        show_roof: Boolean to show/hide roof for interior viewing
        roof_style: "traditional" (overhang on all sides, separate gable ends) or 
                    "flush" (flush with walls, north side extends 1m down for balcony shading)
    """
    ox, oy, oz = origin
    
    # Dimensions from specifications
    WIDTH = 6.0   # meters (north-south direction, Y-axis)
    LENGTH = 8.0  # meters (east-west direction, X-axis)
    GROUND_FLOOR_HEIGHT = 2.5  # meters
    FIRST_FLOOR_HEIGHT = 2.4   # meters
    TOTAL_HEIGHT = GROUND_FLOOR_HEIGHT + FIRST_FLOOR_HEIGHT
    
    # Wall thicknesses from Potius specs
    EXTERIOR_WALL_THICKNESS = 0.20  # 200mm
    INTERIOR_WALL_THICKNESS = 0.11  # 110mm
    
    # Roof specifications
    ROOF_PITCH = 35  # degrees
    ROOF_OVERHANG = 0.6  # Standard overhang on all sides
    
    # Materials - Dark tones to blend with forest setting
    # Dark charcoal grey for cedar cladding
    potius_mat = create_material("PotiusExterior", (0.22, 0.22, 0.24, 1))  # Dark charcoal grey
    floor_mat = create_material("FloorWood", (0.5, 0.35, 0.2, 1))
    
    # === GROUND FLOOR EXTERIOR WALLS ===
    
    # North Wall (-Y side) - Will have patio doors and large windows
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy - WIDTH/2 + EXTERIOR_WALL_THICKNESS/2, oz + GROUND_FLOOR_HEIGHT/2))
    north_wall_ground = bpy.context.active_object
    north_wall_ground.name = "MainDwelling_NorthWall_Ground"
    north_wall_ground.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall_ground.data.materials.append(potius_mat)
    
    # South Wall (+Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy + WIDTH/2 - EXTERIOR_WALL_THICKNESS/2, oz + GROUND_FLOOR_HEIGHT/2))
    south_wall_ground = bpy.context.active_object
    south_wall_ground.name = "MainDwelling_SouthWall_Ground"
    south_wall_ground.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall_ground.data.materials.append(potius_mat)
    
    # East Wall (-X side) - Will have entrance
    wall_depth_ground = WIDTH - 2*EXTERIOR_WALL_THICKNESS
    bpy.ops.mesh.primitive_cube_add(location=(ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS/2, oy, oz + GROUND_FLOOR_HEIGHT/2))
    east_wall_ground = bpy.context.active_object
    east_wall_ground.name = "MainDwelling_EastWall_Ground"
    east_wall_ground.scale = (EXTERIOR_WALL_THICKNESS/2, wall_depth_ground/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    east_wall_ground.data.materials.append(potius_mat)
    
    # West Wall (+X side)
    bpy.ops.mesh.primitive_cube_add(location=(ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS/2, oy, oz + GROUND_FLOOR_HEIGHT/2))
    west_wall_ground = bpy.context.active_object
    west_wall_ground.name = "MainDwelling_WestWall_Ground"
    west_wall_ground.scale = (EXTERIOR_WALL_THICKNESS/2, wall_depth_ground/2, GROUND_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall_ground.data.materials.append(potius_mat)
    
    # === FIRST FLOOR EXTERIOR WALLS ===
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    
    # North Wall - First Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy - WIDTH/2 + EXTERIOR_WALL_THICKNESS/2, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    north_wall_first = bpy.context.active_object
    north_wall_first.name = "MainDwelling_NorthWall_First"
    north_wall_first.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall_first.data.materials.append(potius_mat)
    
    # South Wall - First Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy + WIDTH/2 - EXTERIOR_WALL_THICKNESS/2, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    south_wall_first = bpy.context.active_object
    south_wall_first.name = "MainDwelling_SouthWall_First"
    south_wall_first.scale = (LENGTH/2, EXTERIOR_WALL_THICKNESS/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall_first.data.materials.append(potius_mat)
    
    # East Wall - First Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS/2, oy, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    east_wall_first = bpy.context.active_object
    east_wall_first.name = "MainDwelling_EastWall_First"
    east_wall_first.scale = (EXTERIOR_WALL_THICKNESS/2, wall_depth_ground/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    east_wall_first.data.materials.append(potius_mat)
    
    # West Wall - First Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox + LENGTH/2 - EXTERIOR_WALL_THICKNESS/2, oy, first_floor_z + FIRST_FLOOR_HEIGHT/2))
    west_wall_first = bpy.context.active_object
    west_wall_first.name = "MainDwelling_WestWall_First"
    west_wall_first.scale = (EXTERIOR_WALL_THICKNESS/2, wall_depth_ground/2, FIRST_FLOOR_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall_first.data.materials.append(potius_mat)
    
    # === FLOORS ===
    
    # Ground Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + 0.05))
    ground_floor = bpy.context.active_object
    ground_floor.name = "MainDwelling_GroundFloor"
    ground_floor.scale = (LENGTH/2, WIDTH/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    ground_floor.data.materials.append(floor_mat)
    
    # First Floor (ceiling of ground floor / floor of first floor)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, first_floor_z - 0.05))
    first_floor_slab = bpy.context.active_object
    first_floor_slab.name = "MainDwelling_FirstFloor"
    first_floor_slab.scale = (LENGTH/2, WIDTH/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    first_floor_slab.data.materials.append(floor_mat)
    
    # === ENTRANCE PORCH (WEST SIDE) ===
    
    # Porch dimensions: 2.5m × 2.5m floor, walls wrap 2.5m width × 1.5m depth
    # Remaining 1m is open but covered by porch roof
    PORCH_WIDTH = 2.5   # North-south dimension
    PORCH_TOTAL_DEPTH = 2.5   # Total east-west depth
    PORCH_WALL_DEPTH = 1.5    # Depth covered by walls
    PORCH_OPEN_DEPTH = 1.0    # Open covered area (2.5 - 1.5)
    PORCH_HEIGHT = GROUND_FLOOR_HEIGHT  # Same height as ground floor
    PORCH_WALL_THICKNESS = EXTERIOR_WALL_THICKNESS
    
    porch_mat = potius_mat  # Use same material as main building
    
    # Porch floor/deck - positioned west of west wall, centered
    porch_center_x = ox + LENGTH/2 + PORCH_TOTAL_DEPTH/2
    porch_center_y = oy  # Centered on building
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_center_x, porch_center_y, oz + 0.05))
    porch_floor = bpy.context.active_object
    porch_floor.name = "MainDwelling_PorchFloor"
    porch_floor.scale = (PORCH_TOTAL_DEPTH/2, PORCH_WIDTH/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    porch_floor.data.materials.append(floor_mat)
    
    # Porch walls - wrap the 2.5m width and first 1.5m of depth
    
    # North porch wall (runs E-W for 1.5m)
    porch_wall_x = ox + LENGTH/2 + PORCH_WALL_DEPTH/2
    north_porch_wall_y = oy - PORCH_WIDTH/2 + PORCH_WALL_THICKNESS/2
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_wall_x, north_porch_wall_y, oz + PORCH_HEIGHT/2))
    north_porch_wall = bpy.context.active_object
    north_porch_wall.name = "MainDwelling_PorchWall_North"
    north_porch_wall.scale = (PORCH_WALL_DEPTH/2, PORCH_WALL_THICKNESS/2, PORCH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    north_porch_wall.data.materials.append(porch_mat)
    
    # South porch wall (runs E-W for 1.5m)
    south_porch_wall_y = oy + PORCH_WIDTH/2 - PORCH_WALL_THICKNESS/2
    
    bpy.ops.mesh.primitive_cube_add(location=(porch_wall_x, south_porch_wall_y, oz + PORCH_HEIGHT/2))
    south_porch_wall = bpy.context.active_object
    south_porch_wall.name = "MainDwelling_PorchWall_South"
    south_porch_wall.scale = (PORCH_WALL_DEPTH/2, PORCH_WALL_THICKNESS/2, PORCH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    south_porch_wall.data.materials.append(porch_mat)
    
    # West porch wall (partial - connects north and south walls at 1.5m mark)
    west_porch_wall_x = ox + LENGTH/2 + PORCH_WALL_DEPTH - PORCH_WALL_THICKNESS/2
    porch_wall_span = PORCH_WIDTH - 2*PORCH_WALL_THICKNESS  # Between north and south walls
    
    bpy.ops.mesh.primitive_cube_add(location=(west_porch_wall_x, oy, oz + PORCH_HEIGHT/2))
    west_porch_wall = bpy.context.active_object
    west_porch_wall.name = "MainDwelling_PorchWall_West"
    west_porch_wall.scale = (PORCH_WALL_THICKNESS/2, porch_wall_span/2, PORCH_HEIGHT/2)
    bpy.ops.object.transform_apply(scale=True)
    west_porch_wall.data.materials.append(porch_mat)
    
    # Porch entrance door on west wall
    # Position needs to be on OUTER face of wall (west side)
    porch_door_x = ox + LENGTH/2 + PORCH_WALL_DEPTH  # Outer face, not center
    print(f"Adding porch door at x={porch_door_x}, y={oy}, z={oz + 1.0}")
    add_window("MainDwelling_PorchWall_West", (porch_door_x, oy, oz + 1.0), 
               width=0.9, height=2.0, depth=PORCH_WALL_THICKNESS, axis='X', inward_offset='-X')
    print("Porch door window call completed")
    
    # Porch gable roof - 35° pitch, ridge running E-W like main roof
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
    porch_roof_west = ox + LENGTH/2 + PORCH_TOTAL_DEPTH + PORCH_ROOF_OVERHANG
    porch_roof_east = ox + LENGTH/2 - PORCH_ROOF_OVERHANG
    porch_roof_north = oy - PORCH_WIDTH/2 - PORCH_ROOF_OVERHANG
    porch_roof_south = oy + PORCH_WIDTH/2 + PORCH_ROOF_OVERHANG
    
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
    porch_roof_obj.data.materials.append(create_corrugated_iron_material())
    
    # Large opening in main building's west wall connecting to porch
    # Opening should be wide enough for comfortable access (2m wide, 2.2m high)
    add_window("MainDwelling_WestWall_Ground", (ox + LENGTH/2, oy, oz + 1.1), 
               width=2.0, height=2.2, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # === WINDOWS AND DOORS ===
    
    # GROUND FLOOR - NORTH WALL
    # 3 large windows/patio doors: 2m height, widths 1.5m, 2.0m, 1.5m, evenly spaced
    window_z_ground = oz + 1.0  # 1m from ground
    spacing = LENGTH / 4  # Evenly space 3 windows across 8m length
    
    add_window("MainDwelling_NorthWall_Ground", (ox - spacing, oy - WIDTH/2, window_z_ground), 
               width=1.5, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y')
    add_window("MainDwelling_NorthWall_Ground", (ox, oy - WIDTH/2, window_z_ground), 
               width=2.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y')  # Center
    add_window("MainDwelling_NorthWall_Ground", (ox + spacing, oy - WIDTH/2, window_z_ground), 
               width=1.5, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='Y')
    
    # FIRST FLOOR - NORTH WALL
    # 3 windows matching ground floor placement, 1.2m height
    window_z_first = first_floor_z + 1.2
    
    add_window("MainDwelling_NorthWall_First", (ox - spacing, oy - WIDTH/2, window_z_first), 
               width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y')
    add_window("MainDwelling_NorthWall_First", (ox, oy - WIDTH/2, window_z_first), 
               width=2.0, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y')  # Center
    add_window("MainDwelling_NorthWall_First", (ox + spacing, oy - WIDTH/2, window_z_first), 
               width=1.5, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y')
    
    # GROUND FLOOR - EAST WALL
    # 2 small windows (1.2m wide, 1.0m high)
    east_window_spacing = WIDTH / 3
    
    add_window("MainDwelling_EastWall_Ground", (ox - LENGTH/2, oy - east_window_spacing/2, oz + 1.2), 
               width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    add_window("MainDwelling_EastWall_Ground", (ox - LENGTH/2, oy + east_window_spacing/2, oz + 1.2), 
               width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # FIRST FLOOR - EAST WALL
    # 2 small windows (1.2m wide, 1.0m high)
    add_window("MainDwelling_EastWall_First", (ox - LENGTH/2, oy - east_window_spacing/2, first_floor_z + 1.2), 
               width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    add_window("MainDwelling_EastWall_First", (ox - LENGTH/2, oy + east_window_spacing/2, first_floor_z + 1.2), 
               width=1.2, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')
    
    # GROUND FLOOR - WEST WALL
    # 2 very small windows (0.5m wide, 0.6m high) - accounting for porch
    west_window_spacing = WIDTH / 3
    
    add_window("MainDwelling_WestWall_Ground", (ox + LENGTH/2, oy - west_window_spacing, oz + 1.8), 
               width=0.5, height=0.6, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MainDwelling_WestWall_Ground", (ox + LENGTH/2, oy + west_window_spacing, oz + 1.8), 
               width=0.5, height=0.6, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # FIRST FLOOR - WEST WALL
    # 2 small windows (0.8m wide, 1.0m high)
    add_window("MainDwelling_WestWall_First", (ox + LENGTH/2, oy - west_window_spacing, first_floor_z + 1.2), 
               width=0.8, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    add_window("MainDwelling_WestWall_First", (ox + LENGTH/2, oy + west_window_spacing, first_floor_z + 1.2), 
               width=0.8, height=1.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')
    
    # GROUND FLOOR - SOUTH WALL
    # 3 medium windows (1.2m wide, 1.4m high), evenly spaced
    south_spacing = LENGTH / 4
    
    add_window("MainDwelling_SouthWall_Ground", (ox - south_spacing, oy + WIDTH/2, oz + 1.0), 
               width=1.2, height=1.4, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    add_window("MainDwelling_SouthWall_Ground", (ox, oy + WIDTH/2, oz + 1.0), 
               width=1.2, height=1.4, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')  # Center
    add_window("MainDwelling_SouthWall_Ground", (ox + south_spacing, oy + WIDTH/2, oz + 1.0), 
               width=1.2, height=1.4, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')
    
    # FIRST FLOOR - SOUTH WALL
    # 3 medium windows (1.2m wide, 1.2m high), evenly spaced
    add_window("MainDwelling_SouthWall_First", (ox - south_spacing, oy + WIDTH/2, first_floor_z + 1.2), 
               width=1.2, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')  # Left
    add_window("MainDwelling_SouthWall_First", (ox, oy + WIDTH/2, first_floor_z + 1.2), 
               width=1.2, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')  # Center
    add_window("MainDwelling_SouthWall_First", (ox + south_spacing, oy + WIDTH/2, first_floor_z + 1.2), 
               width=1.2, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='-Y')  # Right
    
    # === GABLE ROOF ===
    if show_roof:
        # Calculate roof dimensions
        roof_height_from_eaves = (WIDTH / 2) * math.tan(math.radians(ROOF_PITCH))
        eave_height = oz + TOTAL_HEIGHT  # Top of walls
        ridge_height = eave_height + roof_height_from_eaves
        
        # Create corrugated iron material
        roof_mat = create_corrugated_iron_material()
        gable_material = create_material("GableEnd", (0.22, 0.22, 0.24, 1))
        
        if roof_style == "flush":
            # FLUSH GABLE: Roof is flush with all wall planes (no overhang)
            # North side extends down 1m for balcony shading
            mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
            obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
            bpy.context.collection.objects.link(obj)
            
            # Flush with wall faces (no overhang on any side)
            east_edge = ox - LENGTH/2
            west_edge = ox + LENGTH/2
            south_eave_y = oy + WIDTH/2  # Flush with south wall
            
            # North side: extends down 1m below eave for balcony shading
            # Calculate how far north to extend to drop 1m at 35° pitch
            BALCONY_SHADE_DROP = 1.0  # meters
            north_extension = BALCONY_SHADE_DROP / math.tan(math.radians(ROOF_PITCH))
            north_eave_y = oy - WIDTH/2 - north_extension  # Extended north for shading
            north_eave_z = eave_height - BALCONY_SHADE_DROP  # Dropped 1m
            
            verts = [
                # North eave edge (extended for balcony shading)
                (east_edge, north_eave_y, north_eave_z),    # 0: NE corner
                (west_edge, north_eave_y, north_eave_z),    # 1: NW corner
                # Ridge points
                (east_edge, oy, ridge_height),              # 2: E ridge
                (west_edge, oy, ridge_height),              # 3: W ridge
                # South eave edge (flush with wall)
                (east_edge, south_eave_y, eave_height),     # 4: SE corner
                (west_edge, south_eave_y, eave_height),     # 5: SW corner
            ]
            
            faces = [
                (0, 1, 3, 2),  # North roof slope (extended for balcony)
                (2, 3, 5, 4),  # South roof slope
                (0, 2, 4),     # East gable triangle
                (1, 5, 3),     # West gable triangle
            ]
            
            mesh.from_pydata(verts, [], faces)
            mesh.update()
            
            # Apply materials - roof slopes get corrugated iron, gables get wall material
            obj.data.materials.append(roof_mat)
            obj.data.materials.append(gable_material)
            
            # Assign materials to faces
            for i, face in enumerate(mesh.polygons):
                if i < 2:  # First two faces are roof slopes
                    face.material_index = 0
                else:  # Last two faces are gable ends
                    face.material_index = 1
            
        else:  # roof_style == "traditional"
            # TRADITIONAL GABLE: Separate gable end triangles with overhang on all sides
            mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
            obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
            bpy.context.collection.objects.link(obj)
            
            # Define vertices for roof with overhang on all sides
            half_length = (LENGTH + 2 * ROOF_OVERHANG) / 2
            north_eave_y = oy - WIDTH/2 - ROOF_OVERHANG
            south_eave_y = oy + WIDTH/2 + ROOF_OVERHANG
            
            verts = [
                # North eave edge
                (ox - half_length, north_eave_y, eave_height),  # 0: NW corner
                (ox + half_length, north_eave_y, eave_height),  # 1: NE corner
                # Ridge
                (ox - half_length, oy, ridge_height),            # 2: W ridge
                (ox + half_length, oy, ridge_height),            # 3: E ridge
                # South eave edge
                (ox - half_length, south_eave_y, eave_height),  # 4: SW corner
                (ox + half_length, south_eave_y, eave_height),  # 5: SE corner
            ]
            
            faces = [
                (0, 1, 3, 2),  # North roof plane
                (2, 3, 5, 4),  # South roof plane
            ]
            
            mesh.from_pydata(verts, [], faces)
            mesh.update()
            obj.data.materials.append(roof_mat)
            
            # Create separate gable end triangles
            for side, x_pos in [("East", ox - LENGTH/2), ("West", ox + LENGTH/2)]:
                verts = [
                    (x_pos, oy - WIDTH/2, eave_height),     # Bottom left (north eave)
                    (x_pos, oy + WIDTH/2, eave_height),     # Bottom right (south eave)
                    (x_pos, oy, ridge_height)                # Top center (ridge)
                ]
                edges = []
                faces = [(0, 1, 2)]
                
                gable_mesh = bpy.data.meshes.new(f"MainDwelling_Gable_{side}")
                gable_mesh.from_pydata(verts, edges, faces)
                gable_mesh.update()
                
                gable = bpy.data.objects.new(f"MainDwelling_Gable_{side}", gable_mesh)
                bpy.context.collection.objects.link(gable)
                gable.data.materials.append(gable_material)
    
    print(f"Main Dwelling built at origin {origin}")
