import bpy  # type: ignore
import math

# ============================================================================
# SURVEY POINT GENERATOR FUNCTIONS
# ============================================================================

def point(x, y, z):
    """Single survey point. Simple wrapper for clarity."""
    return (x, y, z)

def line_points(start, end, num_points=None, spacing=None):
    """
    Generate evenly-spaced points along a line.
    
    Args:
        start: (x, y, z) starting point
        end: (x, y, z) ending point
        num_points: Total number of points (including start/end)
        spacing: Spacing between points in meters (alternative to num_points)
    
    Returns:
        List of (x, y, z) tuples
    
    Example:
        # 5 points from (0,0,0) to (10,0,0)
        line_points((0,0,0), (10,0,0), num_points=5)
        
        # Points every 1m along a line
        line_points((0,0,0), (10,5,2), spacing=1.0)
    """
    sx, sy, sz = start
    ex, ey, ez = end
    
    if spacing is not None:
        # Calculate num_points from spacing
        length = math.sqrt((ex-sx)**2 + (ey-sy)**2 + (ez-sz)**2)
        num_points = max(2, int(length / spacing) + 1)
    elif num_points is None:
        num_points = 2
    
    points = []
    for i in range(num_points):
        t = i / (num_points - 1) if num_points > 1 else 0
        x = sx + t * (ex - sx)
        y = sy + t * (ey - sy)
        z = sz + t * (ez - sz)
        points.append((x, y, z))
    
    return points

def grid_points(corner1, corner2, x_spacing=1.0, y_spacing=None, slope_direction='xy'):
    """
    Generate a rectangular grid of points with bilinear interpolation for slopes.
    
    The Z elevation is interpolated between the two opposite corners.
    The slope direction controls how the interpolation occurs.
    
    Args:
        corner1: (x, y, z) first corner
        corner2: (x, y, z) opposite corner
        x_spacing: Spacing in X direction (meters)
        y_spacing: Spacing in Y direction (meters), defaults to x_spacing
        slope_direction: How to interpolate Z values: 'x', 'y', or 'xy'/'diagonal'
            'x': slope only in X direction (constant along Y)
            'y': slope only in Y direction (constant along X)
            'xy' or 'diagonal': diagonal slope (default)
    
    Returns:
        List of (x, y, z) tuples
    
    Examples:
        # Flat 1m grid at elevation 0
        grid_points((-5,-5,0), (5,5,0), x_spacing=1.0)
        
        # Sloped grid along X axis: SW corner at -2m, NE corner at -3.7m
        grid_points((6,-8,-2), (12,-14,-3.7), x_spacing=0.5, slope_direction='x')
        
        # Diagonal slope (default behavior)
        grid_points((6,-8,-2), (12,-14,-3.7), x_spacing=0.5, slope_direction='xy')
    """
    if y_spacing is None:
        y_spacing = x_spacing
    
    x1, y1, z1 = corner1
    x2, y2, z2 = corner2
    
    # Ensure min/max order for x and y
    x_min, x_max = min(x1, x2), max(x1, x2)
    y_min, y_max = min(y1, y2), max(y1, y2)
    
    points = []
    x = x_min
    while x <= x_max + 0.001:  # Small epsilon for floating point
        y = y_min
        while y <= y_max + 0.001:
            # Calculate interpolation factors (0 to 1)
            tx = (x - x_min) / (x_max - x_min) if x_max > x_min else 0
            ty = (y - y_min) / (y_max - y_min) if y_max > y_min else 0
            
            # Interpolate Z based on slope direction
            if slope_direction == 'x':
                # Slope only in X direction (constant along Y)
                t = tx
            elif slope_direction == 'y':
                # Slope only in Y direction (constant along X)
                t = ty
            else:  # 'xy' or 'diagonal'
                # Diagonal slope - average of both directions
                t = (tx + ty) / 2
            
            z = z1 + t * (z2 - z1)
            
            points.append((x, y, z))
            y += y_spacing
        x += x_spacing
    
    return points

def rectangle_points(corner1, corner2, z_height, spacing=1.0):
    """
    Generate points along the perimeter of a rectangle (not filled).
    Useful for defining boundaries.
    
    Args:
        corner1: (x, y) first corner
        corner2: (x, y) opposite corner
        z_height: Z elevation for all points
        spacing: Spacing between points along edges
    
    Returns:
        List of (x, y, z) tuples
    
    Example:
        # Perimeter of 10x8m rectangle at elevation 1.5m
        rectangle_points((-5,-4), (5,4), z_height=1.5, spacing=1.0)
    """
    x1, y1 = corner1
    x2, y2 = corner2
    
    # Four edges
    points = []
    # Bottom edge (y=y1)
    points.extend(line_points((x1, y1, z_height), (x2, y1, z_height), spacing=spacing))
    # Right edge (x=x2)
    points.extend(line_points((x2, y1, z_height), (x2, y2, z_height), spacing=spacing)[1:])  # Skip duplicate corner
    # Top edge (y=y2)
    points.extend(line_points((x2, y2, z_height), (x1, y2, z_height), spacing=spacing)[1:])
    # Left edge (x=x1)
    points.extend(line_points((x1, y2, z_height), (x1, y1, z_height), spacing=spacing)[1:-1])  # Skip both corners
    
    return points

def combine_points(*point_lists):
    """
    Combine multiple point lists into one.
    
    Example:
        ridge = line_points((0,10,5), (10,10,5), spacing=1.0)
        valley = line_points((0,-10,-2), (10,-10,-2), spacing=1.0)
        all_points = combine_points(ridge, valley)
    """
    combined = []
    for point_list in point_lists:
        if isinstance(point_list, list):
            combined.extend(point_list)
        else:
            combined.append(point_list)  # Single point tuple
    return combined

# ============================================================================
# TERRAIN INTERPOLATION
# ============================================================================

def interpolate_elevation(x, y, contour_points, power=2):
    """
    Interpolate elevation (z) at position (x,y) using Inverse Distance Weighting.
    
    Args:
        x, y: Position to interpolate
        contour_points: List of (x, y, z) survey points
        power: IDW power parameter (default 2, higher = sharper transitions)
    
    Returns:
        Interpolated z value
    """
    if not contour_points:
        return 0.0
    
    # Calculate distances and weights
    weights = []
    values = []
    
    for px, py, pz in contour_points:
        # Calculate 2D distance
        dist = math.sqrt((x - px)**2 + (y - py)**2)
        
        # Handle exact match
        if dist < 0.001:  # Within 1mm
            return pz
        
        # IDW weight: 1/distance^power
        weight = 1.0 / (dist ** power)
        weights.append(weight)
        values.append(pz)
    
    # Weighted average
    total_weight = sum(weights)
    weighted_sum = sum(w * v for w, v in zip(weights, values))
    
    return weighted_sum / total_weight

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_ground_terrain(cottage_origin=(0, 0, 0), contour_points=None):
    """
    Creates ground terrain for the Kaka Forest Retreat site.
    
    Starting simple: flat ground 500mm under cottage, extending 1000mm each side.
    Can be expanded to use contour_points for accurate terrain modeling.
    
    COORDINATE SYSTEM:
    - Origin (0,0,0) = center of cottage at floor level
    - X-axis: West (+X) / East (-X)
    - Y-axis: South (+Y) / North (-Y)
    - Z-axis: Up (+Z) / Down (-Z)
    
    COTTAGE DIMENSIONS (from björken_module.py):
    - Width (X): 6.2m, so edges at X = ±3.1
    - Depth (Y): 4.2m, so edges at Y = ±2.1
    - South wall center: Y = +2.1
    - North wall center: Y = -2.1
    
    EXAMPLE CONTOUR POINT:
    - Point 3m south of cottage, 2m above floor: (0, 5.1, 2)
      Calculation: Y = 4.2/2 + 3.0 = 5.1
    
    EXAMPLE USAGE:
        # Method 1: Direct point specification
        survey_points = [
            (-3, 5.1, 2), (-2, 5.1, 2), (-1, 5.1, 2), (0, 5.1, 2),
            (1, 5.1, 2), (2, 5.1, 2), (3, 5.1, 2), (4, 5.1, 2),
        ]
        
        # Method 2: Using helper functions (RECOMMENDED)
        from ground_module import line_points, grid_points, combine_points
        
        ridge = line_points((-3, 5.1, 2), (4, 5.1, 2), spacing=1.0)  # 8 points
        valley = grid_points((6, -8, -2), (8, -6, -2), x_spacing=1.0)  # Grid
        survey_points = combine_points(ridge, valley)
        
        build_ground_terrain(origin=(0,0,0), contour_points=survey_points)
    
    Args:
        cottage_origin: (x, y, z) tuple for red cottage position (default (0,0,0))
        contour_points: Optional list of (x, y, z) tuples for terrain contours
                       Example: [(0, 5.1, 2), (-3, 4, 1.5), (3, 4, 1.5)]
    """
    ox, oy, oz = cottage_origin
    
    # Cottage dimensions (from björken_module.py)
    COTTAGE_W = 6.2  # Width (X-direction)
    COTTAGE_D = 4.2  # Depth (Y-direction)
    
    # Ground parameters
    GROUND_DEPTH = -0.5  # 500mm below cottage origin
    EXTENSION = 1.0  # 1000mm extension on each side
    GRID_SPACING = 0.5  # 500mm grid resolution for terrain mesh
    
    # Create mesh for terrain
    mesh = bpy.data.meshes.new("GroundMesh")
    ground = bpy.data.objects.new("Ground_Terrain", mesh)
    bpy.context.collection.objects.link(ground)
    
    if contour_points is None or len(contour_points) == 0:
        # Simple flat plane fallback
        x_min = ox - COTTAGE_W/2 - EXTENSION
        x_max = ox + COTTAGE_W/2 + EXTENSION
        y_min = oy - COTTAGE_D/2 - EXTENSION
        y_max = oy + COTTAGE_D/2 + EXTENSION
        z_ground = oz + GROUND_DEPTH
        
        verts = [
            (x_min, y_min, z_ground),
            (x_max, y_min, z_ground),
            (x_max, y_max, z_ground),
            (x_min, y_max, z_ground),
        ]
        faces = [(0, 1, 2, 3)]
    else:
        # Grid + Interpolation method using contour points
        # Determine terrain bounds from contour points
        xs = [p[0] for p in contour_points]
        ys = [p[1] for p in contour_points]
        
        x_min = min(xs) - EXTENSION
        x_max = max(xs) + EXTENSION
        y_min = min(ys) - EXTENSION
        y_max = max(ys) + EXTENSION
        
        # Create regular grid
        x_steps = int((x_max - x_min) / GRID_SPACING) + 1
        y_steps = int((y_max - y_min) / GRID_SPACING) + 1
        
        verts = []
        vertex_index = {}
        
        # Generate grid vertices with interpolated Z values
        for j in range(y_steps):
            for i in range(x_steps):
                x = x_min + i * GRID_SPACING
                y = y_min + j * GRID_SPACING
                
                # Inverse Distance Weighting (IDW) interpolation
                z = interpolate_elevation(x, y, contour_points, power=2)
                
                verts.append((x, y, z))
                vertex_index[(i, j)] = len(verts) - 1
        
        # Create quad faces from grid
        faces = []
        for j in range(y_steps - 1):
            for i in range(x_steps - 1):
                v1 = vertex_index[(i, j)]
                v2 = vertex_index[(i + 1, j)]
                v3 = vertex_index[(i + 1, j + 1)]
                v4 = vertex_index[(i, j + 1)]
                faces.append((v1, v2, v3, v4))
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Calculate vertex colors based on slope
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="SlopeShading")
    color_layer = mesh.vertex_colors["SlopeShading"]
    
    # Define colors for different slopes
    flat_color = (0.3, 0.4, 0.2, 1.0)   # Green-brown for flat ground
    steep_color = (0.5, 0.4, 0.3, 1.0)  # Tan-brown for steep slopes
    
    for poly in mesh.polygons:
        # Get face normal
        normal = poly.normal
        
        # Calculate slope angle from vertical (0° = flat, 90° = vertical)
        # Z component of normal: 1.0 = flat, 0.0 = vertical
        slope_factor = 1.0 - abs(normal.z)  # 0.0 = flat, 1.0 = vertical
        
        # Clamp and scale (slopes > 30° are considered steep)
        steepness = min(slope_factor * 3.0, 1.0)  # 0 to 1 range
        
        # Interpolate between flat and steep colors
        poly_color = [
            flat_color[i] * (1 - steepness) + steep_color[i] * steepness
            for i in range(4)
        ]
        
        # Apply color to all vertices of this face
        for loop_idx in poly.loop_indices:
            color_layer.data[loop_idx].color = poly_color
    
    # Apply ground material with vertex color support
    ground_mat = create_slope_material()
    ground.data.materials.append(ground_mat)
    
    return ground

def create_slope_material():
    """Create material that uses vertex colors for slope-based shading."""
    mat_name = "GroundSlope"
    mat = bpy.data.materials.get(mat_name)
    
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create nodes
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Vertex color input
        vcol = nodes.new('ShaderNodeVertexColor')
        vcol.layer_name = "SlopeShading"
        vcol.location = (-300, 0)
        
        # Connect vertex color to BSDF base color
        links.new(vcol.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Adjust material properties for natural ground look
        bsdf.inputs['Roughness'].default_value = 0.9
        bsdf.inputs['Specular IOR Level'].default_value = 0.2
    
    return mat
