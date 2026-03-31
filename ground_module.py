import bpy  # type: ignore
import math

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_ground_terrain(cottage_origin=(0, 0, 0)):
    """
    Creates ground terrain for the Kaka Forest Retreat site.
    
    Features:
    - Flat area under cottage and extending a few meters in most directions
    - 45-degree slope on south side (banking up behind cottage)
    - 45-degree slope on north side (banking down in front of cottage)
    - Natural forest ground material
    
    Args:
        cottage_origin: (x, y, z) tuple for red cottage position (default (0,0,0))
    """
    ox, oy, oz = cottage_origin
    
    # Cottage dimensions (from björken_module.py)
    COTTAGE_W = 6.2  # Width (X-direction)
    COTTAGE_D = 4.2  # Depth (Y-direction)
    
    # Ground parameters
    FLAT_EXTENSION = 3.0  # meters of flat ground extending from cottage
    SLOPE_ANGLE = 45  # degrees for slopes
    SLOPE_LENGTH = 2.0  # meters of 45° slope before blending
    
    # South slope calculations (banks UP behind cottage)
    slope_height = SLOPE_LENGTH * math.tan(math.radians(SLOPE_ANGLE))  # 2m rise
    south_slope_top_y = oy + COTTAGE_D/2 + FLAT_EXTENSION  # South edge of flat area
    south_slope_bottom_y = south_slope_top_y + SLOPE_LENGTH  # End of slope
    
    # North slope calculations (banks DOWN in front of cottage)
    north_slope_top_y = oy - COTTAGE_D/2 - FLAT_EXTENSION  # North edge of flat area
    north_slope_bottom_y = north_slope_top_y - SLOPE_LENGTH  # End of slope
    
    # Create mesh for terrain
    mesh = bpy.data.meshes.new("GroundMesh")
    ground = bpy.data.objects.new("Ground_Terrain", mesh)
    bpy.context.collection.objects.link(ground)
    
    # Simple terrain with key elevation points
    # Grid vertices covering the site
    terrain_size = 40  # meters in each direction from origin
    
    verts = []
    faces = []
    
    # Create a grid of vertices
    grid_spacing = 2.0  # 2m grid
    grid_x = int(terrain_size / grid_spacing)
    grid_y = int(terrain_size / grid_spacing)
    
    for j in range(grid_y + 1):
        for i in range(grid_x + 1):
            # Position in grid
            x = ox - terrain_size/2 + i * grid_spacing
            y = oy - terrain_size/2 + j * grid_spacing
            
            # Calculate height based on position
            z = oz  # Default: cottage level (flat area)
            
            # South slope area (banks UP south of cottage)
            if y > south_slope_top_y:
                if y < south_slope_bottom_y:
                    # On the slope
                    slope_progress = (y - south_slope_top_y) / SLOPE_LENGTH
                    z = oz + slope_progress * slope_height
                else:
                    # Beyond slope (higher ground)
                    z = oz + slope_height
            
            # North slope area (banks DOWN north of cottage)
            elif y < north_slope_top_y:
                if y > north_slope_bottom_y:
                    # On the slope
                    slope_progress = (north_slope_top_y - y) / SLOPE_LENGTH
                    z = oz - slope_progress * slope_height
                else:
                    # Beyond slope (lower ground)
                    z = oz - slope_height
            
            verts.append((x, y, z))
    
    # Create faces from grid
    for j in range(grid_y):
        for i in range(grid_x):
            v1 = j * (grid_x + 1) + i
            v2 = v1 + 1
            v3 = v1 + (grid_x + 1) + 1
            v4 = v1 + (grid_x + 1)
            faces.append((v1, v2, v3, v4))
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Apply ground material (forest floor / grass)
    ground_mat = create_material("ForestGround", (0.3, 0.25, 0.15, 1.0))  # Brown-green earth tone
    ground.data.materials.append(ground_mat)
    
    return ground
