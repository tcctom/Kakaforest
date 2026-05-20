import bpy  # type: ignore
import math

from utils import apply_shadowclad_grooves, add_window, create_corrugated_iron_material, add_corner_trim

def create_material(name, color):
    """Create or get a material with the given name and color"""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_main_dwelling(origin=(0, 0, 0), show_roof=True):
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
    
    # Materials
    potius_mat = create_material("PotiusExterior", (0.85, 0.85, 0.82, 1))  # Light grey
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
    
    # === WINDOWS AND DOORS ===
    
    # Ground floor north wall - Large windows and patio doors
    # Add three large window sections
    window_height = 2.0  # Tall windows for ground floor
    window_z = oz + 1.0  # 1m from ground
    
    # Window positions along north wall (spread along 8m length)
    add_window("MainDwelling_NorthWall_Ground", (ox - 2.5, oy - WIDTH/2, window_z), 
               width=1.5, height=window_height, depth=EXTERIOR_WALL_THICKNESS, axis='Y')
    add_window("MainDwelling_NorthWall_Ground", (ox, oy - WIDTH/2, window_z), 
               width=2.0, height=window_height, depth=EXTERIOR_WALL_THICKNESS, axis='Y')  # Center patio door
    add_window("MainDwelling_NorthWall_Ground", (ox + 2.5, oy - WIDTH/2, window_z), 
               width=1.5, height=window_height, depth=EXTERIOR_WALL_THICKNESS, axis='Y')
    
    # Ground floor east wall - Entrance
    add_window("MainDwelling_EastWall_Ground", (ox - LENGTH/2, oy, oz + 1.0), 
               width=1.0, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='X')  # Door
    
    # First floor windows - smaller standard windows
    first_window_z = first_floor_z + 1.2
    add_window("MainDwelling_NorthWall_First", (ox - 2.0, oy - WIDTH/2, first_window_z), 
               width=1.2, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y')
    add_window("MainDwelling_NorthWall_First", (ox + 2.0, oy - WIDTH/2, first_window_z), 
               width=1.2, height=1.2, depth=EXTERIOR_WALL_THICKNESS, axis='Y')
    
    # === GABLE ROOF ===
    if show_roof:
        # Calculate roof dimensions
        roof_height_from_eaves = (WIDTH / 2) * math.tan(math.radians(ROOF_PITCH))
        eave_height = oz + TOTAL_HEIGHT  # Top of walls
        ridge_height = eave_height + roof_height_from_eaves
        
        # Create corrugated iron material
        roof_mat = create_corrugated_iron_material()
        
        # Create roof as custom mesh (like Björken does)
        mesh = bpy.data.meshes.new("MainDwelling_RoofMesh")
        obj = bpy.data.objects.new("MainDwelling_Roof", mesh)
        bpy.context.collection.objects.link(obj)
        
        # Define vertices for roof with overhang
        half_length = (LENGTH + 2 * ROOF_OVERHANG) / 2
        north_eave_y = oy - WIDTH/2 - ROOF_OVERHANG
        south_eave_y = oy + WIDTH/2 + ROOF_OVERHANG
        
        verts = [
            # North eave edge (4 corners)
            (ox - half_length, north_eave_y, eave_height),  # 0: NW corner
            (ox + half_length, north_eave_y, eave_height),  # 1: NE corner
            # Ridge (2 points)
            (ox - half_length, oy, ridge_height),            # 2: W ridge
            (ox + half_length, oy, ridge_height),            # 3: E ridge
            # South eave edge (2 corners)
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
        
        # Gable end triangles (East and West)
        gable_material = create_material("GableEnd", (0.85, 0.85, 0.82, 1))
        
        # Create gable mesh manually for precise triangle shape
        for side, x_pos in [("East", ox - LENGTH/2), ("West", ox + LENGTH/2)]:
            verts = [
                (x_pos, oy - WIDTH/2, eave_height),     # Bottom left (north eave)
                (x_pos, oy + WIDTH/2, eave_height),     # Bottom right (south eave)
                (x_pos, oy, ridge_height)                # Top center (ridge)
            ]
            edges = []
            faces = [(0, 1, 2)]
            
            mesh = bpy.data.meshes.new(f"MainDwelling_Gable_{side}")
            mesh.from_pydata(verts, edges, faces)
            mesh.update()
            
            gable = bpy.data.objects.new(f"MainDwelling_Gable_{side}", mesh)
            bpy.context.collection.objects.link(gable)
            gable.data.materials.append(gable_material)
    
    print(f"Main Dwelling built at origin {origin}")
