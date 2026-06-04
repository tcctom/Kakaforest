import bpy  # type: ignore
import math

from utils import apply_shadowclad_grooves, add_window, create_corrugated_iron_material, add_corner_trim
from materials import get_metal_roof_material

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_red_cottage(origin=(0,0,0), show_roof=True):  # Set show_roof=False to hide roof
    ox, oy, oz = origin
    W, D, H = 6.2, 4.2, 2.4 
    PITCH = 35
    EXTERIOR_WALL_THICKNESS = 0.15  # 150mm exterior walls
    INTERIOR_WALL_THICKNESS = 0.11  # 110mm interior walls 
    
    # Create red cottage material
    red_mat = create_material("RedCottage", (0.7, 0.05, 0.05, 1))
    
    # Build 4 exterior walls as separate solid boxes
    # North Wall (+Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy + D/2 - EXTERIOR_WALL_THICKNESS/2, oz + H/2))
    north_wall = bpy.context.active_object
    north_wall.name = "Cottage_NorthWall"
    north_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    north_wall.data.materials.append(red_mat)
    
    # South Wall (-Y side)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy - D/2 + EXTERIOR_WALL_THICKNESS/2, oz + H/2))
    south_wall = bpy.context.active_object
    south_wall.name = "Cottage_SouthWall"
    south_wall.scale = (W/2, EXTERIOR_WALL_THICKNESS/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    south_wall.data.materials.append(red_mat)
    
    # East Wall (+X side, positive X = east direction)
    wall_depth = D - 2*EXTERIOR_WALL_THICKNESS
    bpy.ops.mesh.primitive_cube_add(location=(ox + W/2 - EXTERIOR_WALL_THICKNESS/2, oy, oz + H/2))
    east_wall = bpy.context.active_object
    east_wall.name = "Cottage_EastWall"
    east_wall.scale = (EXTERIOR_WALL_THICKNESS/2, wall_depth/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    east_wall.data.materials.append(red_mat)
    
    # West Wall (-X side, negative X = west direction)
    bpy.ops.mesh.primitive_cube_add(location=(ox - W/2 + EXTERIOR_WALL_THICKNESS/2, oy, oz + H/2))
    west_wall = bpy.context.active_object
    west_wall.name = "Cottage_WestWall"
    west_wall.scale = (EXTERIOR_WALL_THICKNESS/2, wall_depth/2, H/2)
    bpy.ops.object.transform_apply(scale=True)
    west_wall.data.materials.append(red_mat)
    
    # Floor
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + 0.05))
    floor = bpy.context.active_object
    floor.name = "Cottage_Floor"
    floor.scale = (W/2, D/2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    floor.data.materials.append(create_material("FloorWood", (0.5, 0.35, 0.2, 1)))

    # Verandah dimensions (defined early for use in foundations and roof)
    VERANDAH_LENGTH = 4.0  # meters (along north face, X-direction)
    VERANDAH_WIDTH = 1.5   # meters (depth from cottage, Y-direction)
    VERANDAH_HEIGHT = 0.1  # meters (thickness)

    # FOUNDATIONS: Piles and Bearers
    # Foundation material - treated timber
    foundation_mat = create_material("FoundationTimber", (0.4, 0.35, 0.25, 1))
    
    # Pile specifications
    PILE_SIZE = 0.15  # 150mm x 150mm square piles
    PILE_DEPTH = 0.6  # 600mm into ground
    PILE_HEIGHT_TOTAL = PILE_DEPTH + 0.1  # Extend 100mm above ground to bearer level
    
    # Bearer specifications
    BEARER_WIDTH = 0.15  # 150mm wide
    BEARER_HEIGHT = 0.2  # 200mm high
    
    # Create piles in a grid pattern
    # Main building piles: every 1.5m along X, every 2.1m along Y
    pile_x_positions = [W/2 - 0.5, W/2 - 2.0, W/2 - 3.5, W/2 - 5.0, W/2 - 5.7]  # 5 rows
    pile_y_positions = [D/2 - 0.5, 0, -D/2 + 0.5]  # 3 columns for main building
    
    # Main building piles
    for px in pile_x_positions:
        for py in pile_y_positions:
            pile_z = oz - PILE_DEPTH + PILE_HEIGHT_TOTAL/2
            bpy.ops.mesh.primitive_cube_add(location=(ox + px, oy + py, pile_z))
            pile = bpy.context.active_object
            pile.name = f"Foundation_Pile"
            pile.scale = (PILE_SIZE/2, PILE_SIZE/2, PILE_HEIGHT_TOTAL/2)
            bpy.ops.object.transform_apply(scale=True)
            pile.data.materials.append(foundation_mat)
    
    # Verandah piles (north side, under 4.0m × 1.5m verandah)
    # Verandah spans X: from -0.9 to +3.1, Y: from 2.1 to 3.6
    verandah_pile_x_positions = [2.8, 1.5, 0.2, -0.6]  # Along verandah length
    verandah_pile_y_positions = [D/2 + VERANDAH_WIDTH/2, D/2 + VERANDAH_WIDTH - 0.3]  # Two rows under verandah
    
    for px in verandah_pile_x_positions:
        for py in verandah_pile_y_positions:
            pile_z = oz - PILE_DEPTH + PILE_HEIGHT_TOTAL/2
            bpy.ops.mesh.primitive_cube_add(location=(ox + px, oy + py, pile_z))
            pile = bpy.context.active_object
            pile.name = f"Foundation_Pile_Verandah"
            pile.scale = (PILE_SIZE/2, PILE_SIZE/2, PILE_HEIGHT_TOTAL/2)
            bpy.ops.object.transform_apply(scale=True)
            pile.data.materials.append(foundation_mat)
    
    # Create bearers running along X-axis (spanning the building width)
    # Positioned on top of piles
    bearer_z = oz - 0.05  # Just below floor level
    
    # Main building bearers
    for py in pile_y_positions:
        bpy.ops.mesh.primitive_cube_add(location=(ox, oy + py, bearer_z))
        bearer = bpy.context.active_object
        bearer.name = f"Foundation_Bearer"
        bearer.scale = (W/2, BEARER_WIDTH/2, BEARER_HEIGHT/2)
        bpy.ops.object.transform_apply(scale=True)
        bearer.data.materials.append(foundation_mat)
    
    # Verandah bearers (shorter bearers for 4.0m verandah)
    verandah_center_x = ox + (W/2 - VERANDAH_LENGTH/2)  # ox + 1.1
    for py in verandah_pile_y_positions:
        bpy.ops.mesh.primitive_cube_add(location=(verandah_center_x, oy + py, bearer_z))
        bearer = bpy.context.active_object
        bearer.name = f"Foundation_Bearer_Verandah"
        bearer.scale = (VERANDAH_LENGTH/2, BEARER_WIDTH/2, BEARER_HEIGHT/2)
        bpy.ops.object.transform_apply(scale=True)
        bearer.data.materials.append(foundation_mat)

    # Gable Roof (covers cottage + verandah with overhang)
    if show_roof:  # Set show_roof=False in function call to hide roof
        ROOF_OVERHANG = 0.3   # meters (300mm overhang on all sides)
        ROOF_PITCH = 35       # degrees
        
        # Roof dimensions
        roof_width_outer = W + 2 * ROOF_OVERHANG  # 6.8m - full roof span with overhang
        roof_width_inner = W  # 6.2m - building width (for gable walls)
        roof_depth = D + VERANDAH_WIDTH + 2 * ROOF_OVERHANG  # 6.3m (north-south)
        
        # Ridge position: centered between south edge (with overhang) and north edge (with overhang)
        ridge_y_offset = 0.75  # Shifted north to cover verandah
        
        # Calculate rise from ridge to edges
        run = roof_depth / 2  # 3.15m from ridge to each edge
        rise = run * math.tan(math.radians(ROOF_PITCH))
        
        mesh = bpy.data.meshes.new("GableMesh")
        obj = bpy.data.objects.new("Cottage_Roof", mesh)
        bpy.context.collection.objects.link(obj)
        
        half_w_outer = roof_width_outer / 2  # 3.4m - includes overhang
        half_w_inner = roof_width_inner / 2  # 3.1m - at building edge
        
        # Vertices: outer edges for roof planes, inner edges for gable walls
        verts = [
            # Outer base perimeter (with overhang)
            (-half_w_outer, -run, 0),  # 0: NW base outer
            (half_w_outer, -run, 0),   # 1: NE base outer
            (half_w_outer, run, 0),    # 2: SE base outer
            (-half_w_outer, run, 0),   # 3: SW base outer
            
            # Inner base (at building edge for gable walls)
            (-half_w_inner, -run, 0),  # 4: NW base inner
            (half_w_inner, -run, 0),   # 5: NE base inner
            (half_w_inner, run, 0),    # 6: SE base inner
            (-half_w_inner, run, 0),   # 7: SW base inner
            
            # Ridge points
            (-half_w_inner, 0, rise),  # 8: W ridge inner (for gable wall)
            (half_w_inner, 0, rise),   # 9: E ridge inner (for gable wall)
            (-half_w_outer, 0, rise),  # 10: W ridge outer (for roof planes)
            (half_w_outer, 0, rise)    # 11: E ridge outer (for roof planes)
        ]
        
        faces = [
            (0, 1, 11, 10),  # North roof plane (full width with overhang)
            (2, 3, 10, 11),  # South roof plane (full width with overhang)
            (4, 8, 7),       # West gable triangle (at building edge only)
            (5, 6, 9),       # East gable triangle (at building edge only)
            (4, 5, 6, 7),    # Interior ceiling/bottom
            (0, 4, 5, 1),    # North soffit under eave overhang
            (3, 7, 6, 2),    # South soffit under eave overhang
            (0, 10, 8, 4),   # West gable overhang connection
            (1, 5, 9, 11)    # East gable overhang connection
        ]
        
        mesh.from_pydata(verts, [], faces)
        obj.location = (ox, oy + ridge_y_offset, oz + H)
        
        # Add both materials: [0] = Metal Roof (textured), [1] = Red Cottage (gables)
        obj.data.materials.append(get_metal_roof_material())
        obj.data.materials.append(create_material("RedCottage", (0.7, 0.05, 0.05, 1)))
        
        # Assign materials to specific faces
        # Gable triangles (West and East) use Red Cottage material
        obj.data.polygons[2].material_index = 1  # West gable triangle
        obj.data.polygons[3].material_index = 1  # East gable triangle
        # All other faces default to material index 0 (Metal Roof)
        
        # UV unwrap for texture display
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)
    # Position: east edge at ox+W/2, extends 4m along north face toward west
    verandah_x = ox + (W/2 - VERANDAH_LENGTH/2)  # Center: ox + 3.1 - 2.0 = ox + 1.1
    verandah_y = oy + D/2 + VERANDAH_WIDTH/2     # North of cottage: oy + 2.1 + 0.75
    verandah_z = oz + VERANDAH_HEIGHT/2          # Just above ground
    
    bpy.ops.mesh.primitive_cube_add(location=(verandah_x, verandah_y, verandah_z))
    verandah = bpy.context.active_object
    verandah.name = "Cottage_Verandah"
    verandah.scale = (VERANDAH_LENGTH/2, VERANDAH_WIDTH/2, VERANDAH_HEIGHT/2) 
    bpy.ops.object.transform_apply(scale=True)
    verandah.data.materials.append(create_material("WoodenDecking", (0.55, 0.35, 0.18, 1)))

    # Verandah support posts - 3 white posts (90mm x 90mm)
    POST_SIZE = 0.09  # 90mm square posts
    POST_HEIGHT = H - VERANDAH_HEIGHT  # From deck to roof level
    white_mat = create_material("WhitePost", (0.95, 0.95, 0.95, 1))
    
    # Position posts at outer edge of verandah (north edge)
    post_y = oy + D/2 + VERANDAH_WIDTH - POST_SIZE/2  # At north edge of verandah
    post_z = oz + VERANDAH_HEIGHT + POST_HEIGHT/2  # From deck level to roof
    
    # Three posts evenly spaced along verandah length
    post_x_positions = [
        verandah_x + VERANDAH_LENGTH/2 - 0.5,  # Near east end
        verandah_x,                              # Center
        verandah_x - VERANDAH_LENGTH/2 + 0.5    # Near west end
    ]
    
    for post_x in post_x_positions:
        bpy.ops.mesh.primitive_cube_add(location=(post_x, post_y, post_z))
        post = bpy.context.active_object
        post.name = "Verandah_Post"
        post.scale = (POST_SIZE/2, POST_SIZE/2, POST_HEIGHT/2)
        bpy.ops.object.transform_apply(scale=True)
        post.data.materials.append(white_mat)

    # Add windows on North wall
    add_window("Cottage_NorthWall", position=(ox+1.2, oy + D/2, oz+1.05), width=1.8, height=2.1, depth=EXTERIOR_WALL_THICKNESS)
    add_window("Cottage_NorthWall", position=(ox-2, oy + D/2, oz+1.6), width=1.0, height=1.125, depth=EXTERIOR_WALL_THICKNESS)

    # Add window on East wall (east = +X direction)
    add_window("Cottage_EastWall", position=(ox + W/2, oy + 0.8, oz + 1.0), width=0.8, height=2.0, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X')


    # Add window on West wall (west = -X direction)
    add_window("Cottage_WestWall", position=(ox - W/2, oy + 0.8, oz + 1.6), width=0.8, height=1.125, depth=EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='+X')

    # Add white corner trim to all 4 exterior corners
    add_corner_trim(origin=(ox, oy, oz), width=W, depth=D, height=H)
