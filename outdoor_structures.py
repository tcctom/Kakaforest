import bpy  # type: ignore
import os
import random
import math

def create_boulder_material():
    """Create or get the boulder material with namaqualand texture"""
    mat = bpy.data.materials.get("BoulderMaterial")
    if mat:
        return mat
    
    mat = bpy.data.materials.new(name="BoulderMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)
    
    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_node.location = (0, 0)
    
    # Get texture directory
    if bpy.data.filepath:
        blend_dir = os.path.dirname(os.path.abspath(bpy.data.filepath))
    else:
        blend_dir = r"c:\KakaForestRetreat"
    
    texture_dir = os.path.join(blend_dir, "textures", "namaqualand_boulder_03")
    
    # Find texture files
    color_path = None
    rough_path = None
    normal_path = None
    
    if os.path.exists(texture_dir):
        for filename in os.listdir(texture_dir):
            if 'diff' in filename.lower() and filename.endswith('.jpg'):
                color_path = os.path.join(texture_dir, filename)
            elif 'rough' in filename.lower() and filename.endswith('.exr'):
                rough_path = os.path.join(texture_dir, filename)
            elif 'nor' in filename.lower() and filename.endswith('.exr'):
                normal_path = os.path.join(texture_dir, filename)
    
    if color_path and os.path.exists(color_path):
        try:
            # Color texture
            color_img = bpy.data.images.get(os.path.basename(color_path))
            if not color_img:
                color_img = bpy.data.images.load(color_path)
            
            color_tex = nodes.new(type='ShaderNodeTexImage')
            color_tex.location = (-600, 200)
            color_tex.image = color_img
            color_tex.image.colorspace_settings.name = 'sRGB'
            
            # Texture coordinate
            tex_coord = nodes.new(type='ShaderNodeTexCoord')
            tex_coord.location = (-1200, 0)
            
            # Mapping node
            mapping = nodes.new(type='ShaderNodeMapping')
            mapping.location = (-800, 0)
            mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
            
            # Link texture
            links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], color_tex.inputs['Vector'])
            links.new(color_tex.outputs['Color'], bsdf_node.inputs['Base Color'])
            
            # Roughness texture
            if rough_path and os.path.exists(rough_path):
                rough_img = bpy.data.images.get(os.path.basename(rough_path))
                if not rough_img:
                    rough_img = bpy.data.images.load(rough_path)
                
                rough_tex = nodes.new(type='ShaderNodeTexImage')
                rough_tex.location = (-600, -200)
                rough_tex.image = rough_img
                rough_tex.image.colorspace_settings.name = 'Non-Color'
                links.new(mapping.outputs['Vector'], rough_tex.inputs['Vector'])
                links.new(rough_tex.outputs['Color'], bsdf_node.inputs['Roughness'])
            else:
                bsdf_node.inputs['Roughness'].default_value = 0.9
            
            # Normal map
            if normal_path and os.path.exists(normal_path):
                normal_img = bpy.data.images.get(os.path.basename(normal_path))
                if not normal_img:
                    normal_img = bpy.data.images.load(normal_path)
                
                normal_tex = nodes.new(type='ShaderNodeTexImage')
                normal_tex.location = (-600, -400)
                normal_tex.image = normal_img
                normal_tex.image.colorspace_settings.name = 'Non-Color'
                
                normal_map = nodes.new(type='ShaderNodeNormalMap')
                normal_map.location = (-300, -400)
                normal_map.inputs['Strength'].default_value = 1.0
                
                links.new(mapping.outputs['Vector'], normal_tex.inputs['Vector'])
                links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])
                links.new(normal_map.outputs['Normal'], bsdf_node.inputs['Normal'])
        
        except Exception as e:
            print(f"Boulder texture error: {e}")
            bsdf_node.inputs['Base Color'].default_value = (0.5, 0.45, 0.4, 1.0)
            bsdf_node.inputs['Roughness'].default_value = 0.9
    else:
        bsdf_node.inputs['Base Color'].default_value = (0.5, 0.45, 0.4, 1.0)
        bsdf_node.inputs['Roughness'].default_value = 0.9
    
    # Connect BSDF to output
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    return mat


def build_boulder_row(start_pos, end_pos, spacing=1.2, size_variation=0.2):
    """
    Build a row of boulders between two points with natural variation.
    
    Args:
        start_pos: Tuple (x, y, z) for the start position
        end_pos: Tuple (x, y, z) for the end position
        spacing: Average spacing between boulders (meters)
        size_variation: Random variation in boulder size (0-1, where 0.3 = ±30%)
    """
    start_x, start_y, start_z = start_pos
    end_x, end_y, end_z = end_pos
    
    # Calculate distance and number of boulders
    distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
    num_boulders = int(distance / spacing) + 1
    
    # Get boulder material
    boulder_mat = create_boulder_material()
    
    boulders = []
    for i in range(num_boulders):
        # Calculate position along the line
        t = i / (num_boulders - 1) if num_boulders > 1 else 0.5
        x = start_x + t * (end_x - start_x)
        y = start_y + t * (end_y - start_y)
        z = start_z + t * (end_z - start_z)
        
        # Add some random offset perpendicular to the line
        offset = random.uniform(-0.15, 0.15)
        dx = end_y - start_y
        dy = -(end_x - start_x)
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            x += (dx / length) * offset
            y += (dy / length) * offset
        
        # Random boulder size (base size ~0.6m with variation)
        base_size = 0.8
        size_factor = 1.0 + random.uniform(-size_variation, size_variation)
        # More extreme variation in dimensions for irregular, jagged boulders
        scale_x = base_size * size_factor * random.uniform(0.6, 1.5)
        scale_y = base_size * size_factor * random.uniform(0.6, 1.5)
        scale_z = base_size * size_factor * random.uniform(0.5, 1.2)  # Can be flatter or blockier
        
        # Create boulder using CUBE for angular, jagged appearance
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(x, y, z + scale_z/2)
        )
        boulder = bpy.context.active_object
        boulder.name = f"Boulder_{i+1:02d}"
        boulder.scale = (scale_x, scale_y, scale_z)
        
        # Random rotation for natural appearance - more extreme angles
        boulder.rotation_euler = (
            random.uniform(-math.pi/4, math.pi/4),
            random.uniform(-math.pi/4, math.pi/4),
            random.uniform(0, math.pi*2)
        )
        
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        
        # Add subdivision surface BEFORE displacement - minimal to keep angular
        subsurf_mod = boulder.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf_mod.levels = 2  # Enough geometry for displacement but still angular
        subsurf_mod.render_levels = 2
        
        # Primary displacement modifier for large jagged rocky features
        displace_mod = boulder.modifiers.new(name="DisplaceLarge", type='DISPLACE')
        displace_mod.strength = random.uniform(0.5, 0.9)  # Very strong for jagged appearance
        displace_mod.mid_level = 0.5
        
        # Create noise texture for displacement - use MUSGRAVE for angular rocky appearance
        noise_tex = bpy.data.textures.new(name=f"BoulderNoise_{i}", type='MUSGRAVE')
        noise_tex.musgrave_type = 'RIDGED_MULTIFRACTAL'  # Creates sharp ridges and breaks
        noise_tex.noise_scale = random.uniform(1.0, 2.0)  # Larger angular features
        noise_tex.dimension_max = random.uniform(0.5, 1.0)  # Lower = sharper edges
        noise_tex.lacunarity = random.uniform(3.0, 4.0)  # Higher = more angular contrast
        noise_tex.octaves = random.uniform(3.0, 5.0)  # More layers of angular detail
        noise_tex.noise_basis = 'BLENDER_ORIGINAL'
        displace_mod.texture = noise_tex
        displace_mod.texture_coords = 'OBJECT'
        
        # Secondary displacement for sharp fractures and edges
        displace_mod2 = boulder.modifiers.new(name="DisplaceDetail", type='DISPLACE')
        displace_mod2.strength = random.uniform(0.15, 0.3)  # Sharp edge details
        displace_mod2.mid_level = 0.5
        
        noise_tex2 = bpy.data.textures.new(name=f"BoulderNoiseDetail_{i}", type='VORONOI')
        noise_tex2.noise_scale = random.uniform(5.0, 8.0)  # Creates angular cell patterns
        noise_tex2.distance_metric = 'DISTANCE_SQUARED'  # Sharper cell edges
        displace_mod2.texture = noise_tex2
        displace_mod2.texture_coords = 'OBJECT'
        
        # Apply smooth shading for natural appearance
        bpy.context.view_layer.objects.active = boulder
        bpy.ops.object.shade_smooth()
        
        boulder.data.materials.append(boulder_mat)
        boulders.append(boulder)
    
    return boulders


def build_pavers_east(origin=(0, 0, 0)):
    """
    Build a paved area extending east from the red cottage.
    Pavers extend from x -3.1 to x -7.1 (4m east) and y +2.1 to y -2.1 (4.2m north-south).
    
    Args:
        origin: Tuple (x, y, z) for the reference point
    """
    ox, oy, oz = origin
    
    # Paver dimensions
    width_x = 4.0  # 4m in X direction (from -3.1 to -7.1)
    depth_y = 4.2  # 4.2m in Y direction (from +2.1 to -2.1)
    thickness = 0.05  # 5cm thick pavers
    
    # Center position: midpoint between the bounds
    center_x = ox - 5.1  # Midpoint of -3.1 and -7.1
    center_y = oy + 0.0  # Midpoint of +2.1 and -2.1
    center_z = oz + thickness / 2  # Half thickness above ground
    
    # Create paver plane
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(center_x, center_y, center_z)
    )
    pavers = bpy.context.active_object
    pavers.name = "Pavers_East"
    pavers.scale = (width_x, depth_y, thickness)
    bpy.ops.object.transform_apply(scale=True)
    
    # Create paver material
    paver_mat = bpy.data.materials.get("PaverStone") or bpy.data.materials.new(name="PaverStone")
    paver_mat.use_nodes = True
    principled = paver_mat.node_tree.nodes["Principled BSDF"]
    principled.inputs[0].default_value = (0.6, 0.55, 0.5, 1)  # Light gray/beige stone color
    principled.inputs[7].default_value = 0.8  # Roughness
    pavers.data.materials.append(paver_mat)
    
    return pavers

def build_water_tank(origin=(0, 0, 0)):
    """
    Build a 25000 liter cylindrical water tank.
    
    Args:
        origin: Tuple (x, y, z) for the base center of the tank
    """
    ox, oy, oz = origin
    
    # Tank specifications
    TANK_DIAMETER = 3.5
    TANK_HEIGHT = 2.5
    
    # Create cylindrical tank
    bpy.ops.mesh.primitive_cylinder_add(
        radius=TANK_DIAMETER/2, 
        depth=TANK_HEIGHT,
        location=(ox, oy, oz + TANK_HEIGHT/2)
    )
    water_tank = bpy.context.active_object
    water_tank.name = "WaterTank_25000L"
    
    # Create metal tank material
    tank_mat = bpy.data.materials.get("TankMetal") or bpy.data.materials.new(name="TankMetal")
    tank_mat.use_nodes = True
    principled = tank_mat.node_tree.nodes["Principled BSDF"]
    principled.inputs[0].default_value = (0.7, 0.7, 0.75, 1)  # Light gray metallic color
    principled.inputs[4].default_value = 0.8  # Metallic
    principled.inputs[7].default_value = 0.3  # Roughness
    water_tank.data.materials.append(tank_mat)
    
    return water_tank
