import bpy  # type: ignore

"""
Materials Module for Kaka Forest Retreat
Centralized material definitions for consistent appearance across all buildings.

Color Format:
- Colors are defined as RGBA tuples: (Red, Green, Blue, Alpha)
- RGB values range from 0.0 (black) to 1.0 (white)
- Alpha is transparency: 1.0 = opaque, 0.0 = fully transparent
- Examples:
  - (1.0, 1.0, 1.0, 1.0) = pure white
  - (0.0, 0.0, 0.0, 1.0) = pure black
  - (0.5, 0.5, 0.5, 1.0) = 50% gray
  - (0.8, 0.8, 0.75, 1.0) = warm light gray (slightly yellow tint)
"""

def create_material(name, color):
    """Create or get a material with the given name and color
    
    Args:
        name: Unique material name
        color: RGBA tuple (Red, Green, Blue, Alpha) with values 0.0-1.0
        
    Returns:
        Blender material object
    """
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat


# === COMMON BUILDING MATERIALS ===

def get_interior_wall_material():
    """Interior wall material - warm neutral gray
    
    RGB(0.8, 0.8, 0.75):
    - R=0.8, G=0.8: Light gray base
    - B=0.75: Slightly reduced blue adds warmth (subtle yellow/cream tint)
    - Overall: Comfortable neutral that's not stark white
    """
    return create_material("InteriorWall", (0.8, 0.8, 0.75, 1.0))


def get_floor_wood_material():
    """Wooden floor material - laminate with texture
    
    Uses laminate_floor_02 texture from PolyHaven if available.
    Falls back to simple brown color if texture files not found.
    
    To use textures:
    1. Download from https://polyhaven.com/a/laminate_floor_02
    2. Place files in: c:\\KakaForestRetreat\\textures\\laminate_floor_02\\
    3. Files needed: laminate_floor_02_diff_1k.jpg, laminate_floor_02_rough_1k.jpg
    """
    mat = bpy.data.materials.get("FloorWood")
    if mat:
        return mat
    
    mat = bpy.data.materials.new(name="FloorWood")
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
    
    # Try to load texture
    import os
    
    # Get the project directory - use absolute path
    if bpy.data.filepath:
        blend_dir = os.path.dirname(os.path.abspath(bpy.data.filepath))
    else:
        # If blend file not saved, assume we're in the project root
        blend_dir = r"c:\KakaForestRetreat"
    
    texture_dir = os.path.join(blend_dir, "textures", "laminate_floor_02")
    color_path = os.path.join(texture_dir, "laminate_floor_02_diff_1k.jpg")
    rough_path = os.path.join(texture_dir, "laminate_floor_02_rough_1k.exr")
    
    print(f"Floor material: Loading textures from {texture_dir}")
    
    if os.path.exists(color_path):
        try:
            # Color texture - check if already loaded
            color_img = bpy.data.images.get("laminate_floor_02_diff_1k.jpg")
            if not color_img:
                color_img = bpy.data.images.load(color_path)
                print("  ✓ Color texture loaded")
            else:
                print("  ✓ Color texture (cached)")
                
            color_tex = nodes.new(type='ShaderNodeTexImage')
            color_tex.location = (-600, 200)
            color_tex.image = color_img
            color_tex.image.colorspace_settings.name = 'sRGB'
            
            # UV mapping
            uv_map = nodes.new(type='ShaderNodeUVMap')
            uv_map.location = (-1000, 0)
            
            # Mapping node for scale control
            mapping = nodes.new(type='ShaderNodeMapping')
            mapping.location = (-800, 0)
            mapping.inputs['Scale'].default_value = (4.0, 4.0, 4.0)  # Adjust scale as needed
            
            # Texture coordinate
            tex_coord = nodes.new(type='ShaderNodeTexCoord')
            tex_coord.location = (-1200, 0)
            
            # Link texture
            links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], color_tex.inputs['Vector'])
            links.new(color_tex.outputs['Color'], bsdf_node.inputs['Base Color'])
            
            # Roughness texture
            if os.path.exists(rough_path):
                try:
                    rough_img = bpy.data.images.get("laminate_floor_02_rough_1k.exr")
                    if not rough_img:
                        rough_img = bpy.data.images.load(rough_path)
                        print("  ✓ Roughness texture loaded")
                    else:
                        print("  ✓ Roughness texture (cached)")
                        
                    rough_tex = nodes.new(type='ShaderNodeTexImage')
                    rough_tex.location = (-600, -200)
                    rough_tex.image = rough_img
                    rough_tex.image.colorspace_settings.name = 'Non-Color'
                    links.new(mapping.outputs['Vector'], rough_tex.inputs['Vector'])
                    links.new(rough_tex.outputs['Color'], bsdf_node.inputs['Roughness'])
                except Exception as e:
                    print(f"  ! Roughness texture failed: {e}, using default")
                    bsdf_node.inputs['Roughness'].default_value = 0.4
            else:
                bsdf_node.inputs['Roughness'].default_value = 0.4
            
        except Exception as e:
            print(f"  ✗ Error loading texture: {e}")
            # Fallback to simple color
            bsdf_node.inputs['Base Color'].default_value = (0.5, 0.35, 0.2, 1.0)
            bsdf_node.inputs['Roughness'].default_value = 0.4
    else:
        print("  ! Texture not found, using fallback color")
        # Fallback to simple color
        bsdf_node.inputs['Base Color'].default_value = (0.5, 0.35, 0.2, 1.0)
        bsdf_node.inputs['Roughness'].default_value = 0.4
    
    # Connect BSDF to output
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    return mat


def get_metal_roof_material():
    """Metal roof material - box profile corrugated metal sheet with texture
    
    Uses box_profile_metal_sheet texture from PolyHaven if available.
    Falls back to simple metallic gray if texture files not found.
    
    To use textures:
    1. Download from https://polyhaven.com/a/box_profile_metal_sheet
    2. Place files in: c:\\KakaForestRetreat\\textures\\box_profile_metal_sheet\\
    3. Files needed: *_diff_1k.jpg, *_rough_1k.exr
    """
    mat = bpy.data.materials.get("MetalRoof")
    if mat:
        return mat
    
    mat = bpy.data.materials.new(name="MetalRoof")
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
    
    # Try to load texture
    import os
    
    # Get the project directory - use absolute path
    if bpy.data.filepath:
        blend_dir = os.path.dirname(os.path.abspath(bpy.data.filepath))
    else:
        # If blend file not saved, assume we're in the project root
        blend_dir = r"c:\KakaForestRetreat"
    
    texture_dir = os.path.join(blend_dir, "textures", "box_profile_metal_sheet")
    
    # Find texture files (they may have different naming patterns)
    color_path = None
    rough_path = None
    
    if os.path.exists(texture_dir):
        for filename in os.listdir(texture_dir):
            if 'diff' in filename.lower() and filename.endswith('.jpg'):
                color_path = os.path.join(texture_dir, filename)
            elif 'rough' in filename.lower() and filename.endswith('.exr'):
                rough_path = os.path.join(texture_dir, filename)
    
    print(f"Roof material: Loading textures from {texture_dir}")
    
    if color_path and os.path.exists(color_path):
        try:
            # Color texture - check if already loaded
            color_img = bpy.data.images.get(os.path.basename(color_path))
            if not color_img:
                color_img = bpy.data.images.load(color_path)
                print("  ✓ Color texture loaded")
            else:
                print("  ✓ Color texture (cached)")
                
            color_tex = nodes.new(type='ShaderNodeTexImage')
            color_tex.location = (-600, 200)
            color_tex.image = color_img
            color_tex.image.colorspace_settings.name = 'sRGB'
            
            # UV mapping
            uv_map = nodes.new(type='ShaderNodeUVMap')
            uv_map.location = (-1000, 0)
            
            # Mapping node for scale control (roof may need different scale)
            mapping = nodes.new(type='ShaderNodeMapping')
            mapping.location = (-800, 0)
            mapping.inputs['Scale'].default_value = (2.0, 2.0, 2.0)  # Adjust scale as needed
            
            # Texture coordinate
            tex_coord = nodes.new(type='ShaderNodeTexCoord')
            tex_coord.location = (-1200, 0)
            
            # Link texture
            links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], color_tex.inputs['Vector'])
            links.new(color_tex.outputs['Color'], bsdf_node.inputs['Base Color'])
            
            # Set metallic property for metal roof
            bsdf_node.inputs['Metallic'].default_value = 0.8
            
            # Roughness texture
            if rough_path and os.path.exists(rough_path):
                try:
                    rough_img = bpy.data.images.get(os.path.basename(rough_path))
                    if not rough_img:
                        rough_img = bpy.data.images.load(rough_path)
                        print("  ✓ Roughness texture loaded")
                    else:
                        print("  ✓ Roughness texture (cached)")
                        
                    rough_tex = nodes.new(type='ShaderNodeTexImage')
                    rough_tex.location = (-600, -200)
                    rough_tex.image = rough_img
                    rough_tex.image.colorspace_settings.name = 'Non-Color'
                    links.new(mapping.outputs['Vector'], rough_tex.inputs['Vector'])
                    links.new(rough_tex.outputs['Color'], bsdf_node.inputs['Roughness'])
                except Exception as e:
                    print(f"  ! Roughness texture failed: {e}, using default")
                    bsdf_node.inputs['Roughness'].default_value = 0.3
            else:
                bsdf_node.inputs['Roughness'].default_value = 0.3
            
        except Exception as e:
            print(f"  ✗ Error loading texture: {e}")
            # Fallback to simple metallic color
            bsdf_node.inputs['Base Color'].default_value = (0.6, 0.6, 0.65, 1.0)
            bsdf_node.inputs['Metallic'].default_value = 0.8
            bsdf_node.inputs['Roughness'].default_value = 0.3
    else:
        print("  ! Texture not found, using fallback metallic color")
        # Fallback to simple metallic color
        bsdf_node.inputs['Base Color'].default_value = (0.6, 0.6, 0.65, 1.0)
        bsdf_node.inputs['Metallic'].default_value = 0.8
        bsdf_node.inputs['Roughness'].default_value = 0.3
    
    # Connect BSDF to output
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    return mat


def get_potius_exterior_material():
    """Potius cladding exterior - dark charcoal gray"""
    return create_material("PotiusExterior", (0.22, 0.22, 0.24, 1.0))


def get_bed_fabric_material():
    """Bed fabric - off-white linen"""
    return create_material("BedFabric", (0.95, 0.95, 0.9, 1.0))


def get_stairs_wood_material():
    """Stair treads - warm medium brown"""
    return create_material("StairsWood", (0.6, 0.4, 0.25, 1.0))


def get_bathroom_white_material():
    """Bathroom fixtures - bright white porcelain"""
    return create_material("BathroomWhite", (0.95, 0.95, 0.95, 1.0))


def get_chrome_material():
    """Chrome/metal fixtures - silvery gray"""
    return create_material("Chrome", (0.8, 0.8, 0.8, 1.0))


def get_shower_glass_material():
    """Shower glass - translucent blue-tinted"""
    return create_material("ShowerGlass", (0.7, 0.85, 0.9, 0.3))


def get_kitchen_bench_material():
    """Kitchen benchtop - light laminate"""
    return create_material("KitchenBench", (0.85, 0.82, 0.75, 1.0))


def get_kitchen_cabinet_material():
    """Kitchen cabinets - dark wood"""
    return create_material("KitchenCabinet", (0.4, 0.35, 0.3, 1.0))


def get_vanity_cabinet_material():
    """Bathroom vanity cabinet - medium brown"""
    return create_material("VanityCabinet", (0.4, 0.3, 0.2, 1.0))


def get_log_burner_material():
    """Log burner - dark metal"""
    return create_material("LogBurner", (0.1, 0.1, 0.1, 1.0))


def get_flue_pipe_material():
    """Flue pipe - medium gray metal"""
    return create_material("FluePipe", (0.15, 0.15, 0.15, 1.0))


def get_gable_end_material():
    """Gable end cladding - matches Potius exterior"""
    return create_material("GableEnd", (0.22, 0.22, 0.24, 1.0))
