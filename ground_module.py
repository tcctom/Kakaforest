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
    - 45-degree slope on south side (cut into hillside)
    - Turning circle 5m NW of cottage NW corner, 2m below cottage level
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
    SLOPE_ANGLE = 45  # degrees for south bank
    SLOPE_LENGTH = 2.0  # meters of 45° slope before blending
    TURNING_CIRCLE_OFFSET = 5.0  # meters NW from NW corner
    TURNING_CIRCLE_DROP = 2.0  # meters below cottage floor
    TURNING_CIRCLE_DIAMETER = 5.0  # meters
    
    # Calculate key positions
    # Cottage corners
    cottage_nw = (ox - COTTAGE_W/2, oy - COTTAGE_D/2)  # (-3.1, -2.1)
    cottage_ne = (ox + COTTAGE_W/2, oy - COTTAGE_D/2)  # (3.1, -2.1)
    cottage_sw = (ox - COTTAGE_W/2, oy + COTTAGE_D/2)  # (-3.1, 2.1)
    cottage_se = (ox + COTTAGE_W/2, oy + COTTAGE_D/2)  # (3.1, 2.1)
    
    # Turning circle center (5m NW from NW corner - 45° diagonal)
    turning_offset_x = -TURNING_CIRCLE_OFFSET * math.cos(math.radians(45))
    turning_offset_y = -TURNING_CIRCLE_OFFSET * math.sin(math.radians(45))
    turning_center_x = cottage_nw[0] + turning_offset_x  # ~-6.6
    turning_center_y = cottage_nw[1] + turning_offset_y  # ~-5.6
    turning_center_z = oz - TURNING_CIRCLE_DROP  # -2.0
    
    # South slope calculations
    slope_height = SLOPE_LENGTH * math.tan(math.radians(SLOPE_ANGLE))  # 2m rise
    slope_top_y = cottage_se[1] + FLAT_EXTENSION  # South edge of flat area
    slope_bottom_y = slope_top_y + SLOPE_LENGTH  # End of slope
    
    # Create mesh for terrain
    mesh = bpy.data.meshes.new("GroundMesh")
    ground = bpy.data.objects.new("Ground_Terrain", mesh)
    bpy.context.collection.objects.link(ground)
    
    # Simple terrain with key elevation points
    # Grid vertices covering the site
    terrain_size = 25  # meters in each direction from origin
    
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
            z = oz  # Default: cottage level
            
            # Turning circle area: flat at -2m
            dist_to_turning = math.sqrt((x - turning_center_x)**2 + (y - turning_center_y)**2)
            if dist_to_turning < TURNING_CIRCLE_DIAMETER/2:
                z = turning_center_z
            
            # South slope area (south of cottage + flat extension)
            elif y > slope_top_y:
                if y < slope_bottom_y:
                    # On the slope
                    slope_progress = (y - slope_top_y) / SLOPE_LENGTH
                    z = oz + slope_progress * slope_height
                else:
                    # Beyond slope
                    z = oz + slope_height
            
            # Gradual transition from turning circle to cottage level
            elif dist_to_turning < TURNING_CIRCLE_DIAMETER/2 + 3.0:
                # Blend zone
                blend_factor = (dist_to_turning - TURNING_CIRCLE_DIAMETER/2) / 3.0
                z = turning_center_z + blend_factor * (oz - turning_center_z)
            
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
    
    # Create turning circle surface (flat circular disk)
    bpy.ops.mesh.primitive_cylinder_add(
        location=(turning_center_x, turning_center_y, turning_center_z - 0.05),
        radius=TURNING_CIRCLE_DIAMETER/2,
        depth=0.1
    )
    turning_circle = bpy.context.active_object
    turning_circle.name = "TurningCircle"
    
    # Gravel/compacted earth material for driveway
    gravel_mat = create_material("GravelDrive", (0.5, 0.45, 0.4, 1.0))  # Light brown gravel
    turning_circle.data.materials.append(gravel_mat)
    
    return ground
