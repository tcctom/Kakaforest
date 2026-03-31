import bpy  # type: ignore
import math

from utils import create_corrugated_iron_material, add_corner_trim

def create_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

def build_potius_wet_wing(origin=(0,0,0)):
    ox, oy, oz = origin
    W, D = 6.0, 6.0
    H_BASE = 2.4
    WALL_THICKNESS = 0.2  # Interior wall thickness
    
    # Main Shell - Create custom box WITHOUT top face
    mesh = bpy.data.meshes.new("WetWingMesh")
    obj = bpy.data.objects.new("WetWing_Shell", mesh)
    bpy.context.collection.objects.link(obj)
    
    # Define vertices for a box without top
    hw, hd, hh = W/2, D/2, H_BASE/2
    verts = [
        # Bottom face (z = -hh)
        (-hw, -hd, -hh),  # 0: NW bottom
        (hw, -hd, -hh),   # 1: NE bottom
        (hw, hd, -hh),    # 2: SE bottom
        (-hw, hd, -hh),   # 3: SW bottom
        # Top face (z = hh)
        (-hw, -hd, hh),   # 4: NW top
        (hw, -hd, hh),    # 5: NE top
        (hw, hd, hh),     # 6: SE top
        (-hw, hd, hh),    # 7: SW top
    ]
    
    # Faces: bottom + 4 walls (NO top face)
    faces = [
        (0, 1, 2, 3),    # Bottom
        (0, 4, 5, 1),    # North wall (-Y)
        (1, 5, 6, 2),    # East wall (+X)
        (2, 6, 7, 3),    # South wall (+Y)
        (3, 7, 4, 0),    # West wall (-X)
    ]
    
    mesh.from_pydata(verts, [], faces)
    obj.location = (ox, oy, oz + H_BASE/2)
    obj.data.materials.append(create_material("RedCottage", (0.7, 0.05, 0.05, 1)))
    
    # Interior Wall - North to South divider in the middle
    # Runs along Y-axis at center X position (ox)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + H_BASE/2))
    interior_wall = bpy.context.active_object
    interior_wall.name = "WetWing_InteriorWall"
    interior_wall.scale = (WALL_THICKNESS/2, D/2, H_BASE/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Interior walls typically white/light color
    interior_wall.data.materials.append(create_material("InteriorWhite", (0.95, 0.95, 0.95, 1)))
    
    # Skillion Roof (HIGH ON NORTH: -Y)
    # Rotation is now -12 to lift the North edge (-Y)
    bpy.ops.mesh.primitive_cube_add(location=(ox, oy, oz + 3.2))
    roof = bpy.context.active_object
    roof.scale = (W/2 + 0.3, D/2 + 0.3, 0.05)
    roof.rotation_euler = (math.radians(-12), 0, 0)
    roof.data.materials.append(create_corrugated_iron_material())
    
    # Add white corner trim to all 4 exterior corners
    add_corner_trim(origin=(ox, oy, oz), width=W, depth=D, height=H_BASE)