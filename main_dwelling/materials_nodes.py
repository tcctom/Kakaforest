import bpy  # type: ignore
import math
import os

from main_dwelling import config as dwelling_config


def create_material(name, color):
    """Create or get a material with the given name and color."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat


def create_textured_material(name, texture_path):
    """Create or get a material with an image texture."""
    mat = bpy.data.materials.get(name)
    if mat:
        print(f"DEBUG: Material '{name}' already exists, returning cached version")
        return mat

    print(f"DEBUG: Creating new material '{name}' with texture: {texture_path}")
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    principled = nodes.get("Principled BSDF")

    tex_image = nodes.new(type='ShaderNodeTexImage')
    tex_image.location = (-300, 300)

    try:
        img = bpy.data.images.load(texture_path)
        tex_image.image = img
        tex_image.image.colorspace_settings.name = 'sRGB'
    except Exception as e:
        print(f"WARNING: Could not load texture: {texture_path}, Error: {e}")

    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-600, 300)
    mapping.inputs['Rotation'].default_value[2] = math.radians(90)
    mapping.inputs['Scale'].default_value = (3.2, 3.2, 3.2)

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-800, 300)

    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
    links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])

    principled.inputs['Roughness'].default_value = 0.7
    return mat


def create_textured_material2(name, texture_path, rotation_z=0, scale=(1.0, 1.0, 1.0), roughness=0.5, projection='FLAT'):
    """Create or get a material with an image texture with customizable mapping."""
    mat = bpy.data.materials.get(name)
    if mat:
        print(f"DEBUG: Material '{name}' already exists, returning cached version")
        return mat

    print(f"DEBUG: Creating new material '{name}' with texture: {texture_path}")
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)

    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    tex_image = nodes.new(type='ShaderNodeTexImage')
    tex_image.location = (-300, 0)
    tex_image.projection = projection
    if projection == 'BOX':
        tex_image.projection_blend = 0.1

    if os.path.exists(texture_path):
        try:
            img = bpy.data.images.load(texture_path)
            tex_image.image = img
            tex_image.image.colorspace_settings.name = 'sRGB'
        except Exception as e:
            print(f"WARNING: Could not load texture: {texture_path}, Error: {e}")
    else:
        print(f"WARNING: Texture file not found at: {texture_path}")

    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Rotation'].default_value[2] = math.radians(rotation_z)
    mapping.inputs['Scale'].default_value = scale

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)

    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
    links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])

    principled.inputs['Roughness'].default_value = roughness
    return mat


def create_laminate_floor_material():
    """Create or get laminate floor material with texture for top surfaces."""
    mat = bpy.data.materials.get("LaminateFloor")
    if mat:
        print("DEBUG: Material 'LaminateFloor' already exists, returning cached version")
        return mat

    texture_path = dwelling_config.get_texture_path("laminate_floor_02", "laminate_floor_02_diff_1k.jpg")

    print(f"DEBUG: Creating new material 'LaminateFloor' with texture: {texture_path}")
    mat = bpy.data.materials.new(name="LaminateFloor")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    principled = nodes.get("Principled BSDF")

    tex_image = nodes.new(type='ShaderNodeTexImage')
    tex_image.location = (-300, 300)

    try:
        img = bpy.data.images.load(texture_path)
        tex_image.image = img
        tex_image.image.colorspace_settings.name = 'sRGB'
    except Exception as e:
        print(f"WARNING: Could not load laminate floor texture: {texture_path}, Error: {e}")

    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-600, 300)
    mapping.inputs['Scale'].default_value = (4.0, 4.0, 4.0)

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-800, 300)

    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
    links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])

    principled.inputs['Roughness'].default_value = 0.4
    return mat


def create_glass_material(name="ShowerGlass"):
    """Create a physically accurate glass material using nodes."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    principled.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
    principled.inputs['Roughness'].default_value = 0.0
    principled.inputs['IOR'].default_value = 1.45
    principled.inputs['Transmission Weight'].default_value = 1.0

    mat.diffuse_color = (0.7, 0.85, 0.9, 0.2)
    mat.blend_method = 'BLEND'

    return mat


