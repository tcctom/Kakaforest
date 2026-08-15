import bpy  # type: ignore
import math
import mathutils

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

def grid_points(corner1, corner2, x_spacing=0.2, y_spacing=None, slope_direction='xy'):
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



def vector_grid_points(pt1, pt2, length, width_spacing=1.0, length_spacing=None, slope_direction='length'):
    """
    Generate a sloped, rectangular grid of points starting from an arbitrary width edge line.
    Supports both positive (forward) and negative (backward) projection lengths.
    """
    if length_spacing is None:
        length_spacing = width_spacing
        
    v1 = mathutils.Vector(pt1)
    v2 = mathutils.Vector(pt2)
    
    # 1. LOCAL WIDTH DIRECTION
    width_vec = v2 - v1
    total_width = width_vec.length
    if total_width < 0.001:
        raise ValueError("pt1 and pt2 cannot be the exact same coordinate.")
        
    u_width = width_vec.normalized()
    
    # 2. PERPENDICULAR LENGTH DIRECTION
    u_length_base = mathutils.Vector((-u_width.y, u_width.x, 0.0)).normalized()
    
    # FIX: Determine the true direction multiplier (1.0 or -1.0) based on length sign
    length_sign = 1.0 if length >= 0 else -1.0
    u_length = u_length_base * length_sign
    
    # Use the absolute value for calculating total distance spans in the loop
    total_length = abs(length)
    
    # 3. INTERPOLATE GRID POINT STEP LOOPS
    points = []
    
    w_dist = 0.0
    while w_dist <= total_width + 0.001:
        l_dist = 0.0
        while l_dist <= total_length + 0.001: # FIX: use total_length (always positive)
            
            tw = w_dist / total_width if total_width > 0 else 0
            tl = l_dist / total_length if total_length > 0 else 0
            
            # Position offset calculation handles direction automatically via updated u_length
            pos_offset = (u_width * w_dist) + (u_length * l_dist)
            target_pt = v1 + pos_offset
            
            if slope_direction == 'width':
                t = tw
            elif slope_direction == 'length':
                t = tl
            else:
                t = (tw + tl) / 2.0
                
            z_val = v1.z + t * (v2.z - v1.z)
            
            points.append((target_pt.x, target_pt.y, z_val))
            
            l_dist += length_spacing
        w_dist += width_spacing
        
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

def fit_plane_to_points(points):
    """
    Fit a plane (z = ax + by + c) to a set of 3D points using least squares.
    
    Args:
        points: List of (x, y, z) tuples
    
    Returns:
        (a, b, c) coefficients where z = ax + by + c
    """
    if len(points) < 3:
        # Not enough points for a plane, return horizontal plane at average z
        avg_z = sum(p[2] for p in points) / len(points) if points else 0.0
        return (0.0, 0.0, avg_z)
    
    # Build matrices for least squares: z = ax + by + c
    # A * [a, b, c]^T = Z
    n = len(points)
    sum_x = sum(p[0] for p in points)
    sum_y = sum(p[1] for p in points)
    sum_z = sum(p[2] for p in points)
    sum_xx = sum(p[0]**2 for p in points)
    sum_yy = sum(p[1]**2 for p in points)
    sum_xy = sum(p[0]*p[1] for p in points)
    sum_xz = sum(p[0]*p[2] for p in points)
    sum_yz = sum(p[1]*p[2] for p in points)
    
    # Solve using normal equations
    # [sum_xx  sum_xy  sum_x ] [a]   [sum_xz]
    # [sum_xy  sum_yy  sum_y ] [b] = [sum_yz]
    # [sum_x   sum_y   n     ] [c]   [sum_z ]
    
    # Using Cramer's rule or simple matrix inversion for 3x3
    det = (sum_xx * (sum_yy * n - sum_y * sum_y) - 
           sum_xy * (sum_xy * n - sum_x * sum_y) + 
           sum_x * (sum_xy * sum_y - sum_yy * sum_x))
    
    if abs(det) < 1e-10:
        # Degenerate case - return horizontal plane at average
        avg_z = sum_z / n
        return (0.0, 0.0, avg_z)
    
    # Calculate a, b, c using Cramer's rule
    det_a = (sum_xz * (sum_yy * n - sum_y * sum_y) - 
             sum_xy * (sum_yz * n - sum_y * sum_z) + 
             sum_x * (sum_yz * sum_y - sum_yy * sum_z))
    
    det_b = (sum_xx * (sum_yz * n - sum_y * sum_z) - 
             sum_xz * (sum_xy * n - sum_x * sum_y) + 
             sum_x * (sum_xy * sum_z - sum_yz * sum_x))
    
    det_c = (sum_xx * (sum_yy * sum_z - sum_y * sum_yz) - 
             sum_xy * (sum_xy * sum_z - sum_x * sum_yz) + 
             sum_xz * (sum_xy * sum_y - sum_yy * sum_x))
    
    a = det_a / det
    b = det_b / det
    c = det_c / det
    
    return (a, b, c)

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

def build_ground_terrain(
    contour_points=None,
    fallback_bounds=(-5.0, 5.0, -5.0, 5.0, 0.0),
    material_type='gravel',
    name_suffix='',
    use_planar=False,
    extension=1.0,
    thickness=0.100
):
    """
    Creates structural ground terrain (e.g., gravel pad, yard space).
    
    Args:
        contour_points: Optional list of (x, y, z) tuples for terrain contours
        fallback_bounds: (x_min, x_max, y_min, y_max, z) if no contour points are passed
        material_type: Type of ground material: 'grass', 'gravel' (default), 'forest'
        name_suffix: Optional suffix for object name (e.g., '_GravelPad')
        use_planar: If True, fit a flat planar slope to the points
        extension: How far (in meters) to extend mesh beyond boundaries
        thickness: Downward thickness added to the pad in meters (default 100mm)
    """
    import bpy
    import math

    GRID_SPACING = 0.5  # 500mm grid resolution for interpolated meshes
    
    # Create mesh and container object
    mesh = bpy.data.meshes.new(f"GroundMesh{name_suffix}")
    ground_obj = bpy.data.objects.new(f"Ground_Terrain{name_suffix}", mesh)
    bpy.context.collection.objects.link(ground_obj)
    
    # --------------------------------------------------
    # GEOMETRY GENERATION
    # --------------------------------------------------
    if contour_points is None or len(contour_points) == 0:
        # Generic flat plane fallback using explicit bounds
        x_min, x_max, y_min, y_max, z_ground = fallback_bounds
        x_min -= extension
        x_max += extension
        y_min -= extension
        y_max += extension
        
        verts = [
            (x_min, y_min, z_ground),
            (x_max, y_min, z_ground),
            (x_max, y_max, z_ground),
            (x_min, y_max, z_ground),
        ]
        faces = [(0, 1, 2, 3)]
    else:
        # Interpolated grid generation from survey data
        xs = [p[0] for p in contour_points]
        ys = [p[1] for p in contour_points]
        
        x_min, x_max = min(xs) - extension, max(xs) + extension
        y_min, y_max = min(ys) - extension, max(ys) + extension
        
        if use_planar:
            plane_a, plane_b, plane_c = fit_plane_to_points(contour_points)
        
        x_steps = int((x_max - x_min) / GRID_SPACING) + 1
        y_steps = int((y_max - y_min) / GRID_SPACING) + 1
        
        verts = []
        vertex_index = {}
        
        for j in range(y_steps):
            for i in range(x_steps):
                x = x_min + i * GRID_SPACING
                y = y_min + j * GRID_SPACING
                
                if use_planar:
                    z = plane_a * x + plane_b * y + plane_c
                else:
                    z = interpolate_elevation(x, y, contour_points, power=2)
                
                verts.append((x, y, z))
                vertex_index[(i, j)] = len(verts) - 1
        
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
    
    # --------------------------------------------------
    # SLOPE-BASED VERTEX COLORS
    # --------------------------------------------------
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="SlopeShading")
    color_layer = mesh.vertex_colors["SlopeShading"]
    
    flat_color = (0.3, 0.4, 0.2, 1.0)
    steep_color = (0.5, 0.4, 0.3, 1.0)
    
    for poly in mesh.polygons:
        slope_factor = 1.0 - abs(poly.normal.z)
        steepness = min(slope_factor * 3.0, 1.0)
        
        poly_color = [
            flat_color[k] * (1 - steepness) + steep_color[k] * steepness
            for k in range(4)
        ]
        for loop_idx in poly.loop_indices:
            color_layer.data[loop_idx].color = poly_color

    # --------------------------------------------------
    # MATERIALS
    # --------------------------------------------------
    if material_type == 'grass':
        ground_mat = create_grass_material()
    elif material_type == 'gravel':
        ground_mat = create_gravel_material()
    else:
        ground_mat = create_forest_material()
        
    ground_obj.data.materials.append(ground_mat)

    # --------------------------------------------------
    # ADD PHYSICAL THICKNESS (Solidify Modifier)
    # --------------------------------------------------
    if thickness > 0.0:
        solidify = ground_obj.modifiers.new(name="GravelThickness", type='SOLIDIFY')
        solidify.thickness = thickness
        solidify.offset = -1.0  # Expands downward from your elevations
        solidify.use_rim = True  # Creates clean structural side walls

    return ground_obj


def create_grass_material():
    """Create grass material - green with vertex color shading."""
    mat_name = "Ground_Grass"
    mat = bpy.data.materials.get(mat_name)
    
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Base grass color (bright green)
        bsdf.inputs['Base Color'].default_value = (0.2, 0.5, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.95
        bsdf.inputs['Specular IOR Level'].default_value = 0.1
        
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_gravel_material():
    """Create gravel material - light gray/tan."""
    mat_name = "Ground_Gravel"
    mat = bpy.data.materials.get(mat_name)
    
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Gravel color (light gray/tan)
        bsdf.inputs['Base Color'].default_value = (0.6, 0.55, 0.5, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.85
        bsdf.inputs['Specular IOR Level'].default_value = 0.15
        
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_forest_material():
    """Create forest floor material - dark brown/green with vertex color shading."""
    mat_name = "Ground_Forest"
    mat = bpy.data.materials.get(mat_name)
    
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Vertex color input for slope shading
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

# ============================================================================
# CONVENIENCE FUNCTIONS - Simplified terrain builders with preset materials
# ============================================================================

def grass_plane(contour_points,  use_planar=True, extension=0.0, thickness=0.100):
    """
    Create a grass terrain plane from contour points.
    
    Args:
        contour_points: List of (x, y, z) tuples defining the terrain
        cottage_origin: Origin point (default (0, 0, 0))
        use_planar: Use planar interpolation for even slopes (default True)
        extension: Extension beyond points in meters (default 0.0)
    
    Returns:
        Ground object
    """
    return build_ground_terrain(
        contour_points=contour_points,
        material_type='grass',
        name_suffix='_Grass',
        use_planar=use_planar,
        extension=extension,
        thickness=thickness
    )

def gravel_plane(contour_points, use_planar=True, extension=0.0, thickness=0.100):
    """
    Create a gravel terrain plane from contour points.
    
    Args:
        contour_points: List of (x, y, z) tuples defining the terrain
        cottage_origin: Origin point (default (0, 0, 0))
        use_planar: Use planar interpolation for even slopes (default True)
        extension: Extension beyond points in meters (default 0.0)
    
    Returns:
        Ground object
    """
    return build_ground_terrain(
        contour_points=contour_points,
        material_type='gravel',
        name_suffix='_Gravel',
        use_planar=use_planar,
        extension=extension,
        thickness=thickness
    )

def forest_plane(contour_points, use_planar=True, extension=0.0, thickness=0.100):
    """
    Create a forest floor terrain plane from contour points.
    
    Args:
        contour_points: List of (x, y, z) tuples defining the terrain
        cottage_origin: Origin point (default (0, 0, 0))
        use_planar: Use planar interpolation for even slopes (default True)
        extension: Extension beyond points in meters (default 0.0)
    
    Returns:
        Ground object
    """
    return build_ground_terrain(
        contour_points=contour_points,
        material_type='forest',
        name_suffix='_Forest',
        use_planar=use_planar,
        extension=extension,
        thickness=thickness
    )

def build_off_axis_rect_mesh(name_suffix="Driveway_Pad", grid_points=None, width_steps=0, length_steps=0, material_type='forest'):
    """
    Creates a sloped rectangular mesh terrain structure that is completely un-snapped 
    from the global X/Y axes by utilizing raw point array sequence matrix data.
    """
    if not grid_points or width_steps < 2 or length_steps < 2:
        print("CRITICAL: Invalid grid point steps passed to off-axis generator.")
        return None

    mesh_name = f"OffAxisMesh_{name_suffix}"
    obj_name = f"OffAxis_Terrain_{name_suffix}"
    
    # Clean up old object if it exists to allow fresh re-runs
    if obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)
        
    mesh = bpy.data.meshes.new(mesh_name)
    obj = bpy.data.objects.new(obj_name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Connect the grid row and column indices into clean quad faces
    faces = []
    for w in range(width_steps - 1):
        for l in range(length_steps - 1):
            p0 = w * length_steps + l
            p1 = w * length_steps + (l + 1)
            p2 = (w + 1) * length_steps + (l + 1)
            p3 = (w + 1) * length_steps + l
            faces.append((p0, p1, p2, p3))
            
    mesh.from_pydata(grid_points, [], faces)
    mesh.update()
    
    # Assign material types natively matching your setup
    if material_type == 'grass':
        mat = create_grass_material()
    elif material_type == 'gravel':
        mat = create_gravel_material()
    else:
        mat = create_forest_material()
        
    obj.data.materials.append(mat)
    
    return obj

def build_off_axis_plane(pt1, pt2, length, spacing=0.5, name="Play_Area", material_type='forest'):
    """
    High-level wrapper to generate and build a sloped, rectangular grid plane 
    that is completely un-snapped from the global X/Y axes.
    
    Args:
        pt1: (x, y, z) Left coordinate of the width baseline
        pt2: (x, y, z) Right coordinate of the width baseline
        length: Total distance to project the grid perpendicular (can be negative)
        spacing: Grid step resolution for the terrain mesh (default 0.5m)
        name: Name suffix for the generated Blender object
        material_type: Type of material ('forest', 'grass', or 'gravel')
    """
    import math

    # 1. Calculate how many physical matrix steps the loops will require
    # (Adding +1 handles the baseline edge termination steps correctly)
    width_vec_len = math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)
    num_w_steps = int(width_vec_len / spacing) + 1
    num_l_steps = int(abs(length) / spacing) + 1

    # 2. Generate the un-snapped raw vector coordinate array
    grid_points_list = vector_grid_points(
        pt1=pt1, 
        pt2=pt2, 
        length=length, 
        width_spacing=spacing, 
        length_spacing=spacing
    )

    # 3. Call the mesh builder to connect the coordinates by index mapping
    return build_off_axis_rect_mesh(
        name_suffix=name,
        grid_points=grid_points_list,
        width_steps=num_w_steps,
        length_steps=num_l_steps,
        material_type=material_type
    )
