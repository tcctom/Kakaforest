import bpy
import mathutils
import os

def create_sloping_driveway_v1(name="Driveway", width=4.0, thickness=0.15):
    print("\n" + "="*40)
    print(f"STARTING 3D BEVEL SWEEP: '{name}'")
    print("="*40)
    
    # 0. CLEANUP OLD LOGS/OBJECTS TO PREVENT CLUTTER
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    if f"{name}_Profile" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[f"{name}_Profile"], do_unlink=True)

    # Sloped target coordinates
    path_points = [
        mathutils.Vector((-12, 5, -1)),       
        mathutils.Vector((-25, 10, -1.5)),   
        mathutils.Vector((-30, 25, -2.0)),  
        mathutils.Vector((-25, 40, -2.5))   
    ]
    
    # 1. CREATE THE MAIN SLOPED PATH (MUST BE 3D)
    path_data = bpy.data.curves.new(name=f"{name}_Path_Data", type='CURVE')
    path_data.dimensions = '3D'
    path_data.twist_mode = 'Z_UP' # CRITICAL: Forces normals to face the sky globally
    
    polyline = path_data.splines.new('BEZIER')
    polyline.bezier_points.add(len(path_points) - 1)
    
    for i, p in enumerate(path_points):
        bp = polyline.bezier_points[i]
        bp.co = p
        bp.tilt = 0.0 # Keeps the surface perfectly parallel to the horizon
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        
    path_obj = bpy.data.objects.new(name, path_data)
    bpy.context.collection.objects.link(path_obj)
    
    # 2. CREATE A HORIZONTAL PROFILE CURVE (The 4m wide flat line cross-section)
    profile_data = bpy.data.curves.new(name=f"{name}_Prof_Data", type='CURVE')
    profile_data.dimensions = '2D'
    
    prof_line = profile_data.splines.new('POLY')
    prof_line.points.add(1) # Needs 2 points total for a simple line string
    
    # Draw a 4-meter wide straight line running along the local X axis
    half_w = width / 2.0
    prof_line.points[0].co = (-half_w, 0, 0, 1)
    prof_line.points[1].co = (half_w, 0, 0, 1)
    
    profile_obj = bpy.data.objects.new(f"{name}_Profile", profile_data)
    bpy.context.collection.objects.link(profile_obj)
    # Hide the profile template from the viewport render to keep things clean
    profile_obj.hide_viewport = True
    profile_obj.hide_render = True
    
    # 3. SWEEP THE PROFILE ALONG THE PATH
    path_data.bevel_mode = 'OBJECT'
    path_data.bevel_object = profile_obj
    path_data.use_fill_caps = True # Closes off the starting and ending edges
    print("-> Successfully swept horizontal profile along the sloped 3D path.")
    
    # 4. APPLY SOLIDIFY FOR REAL THICKNESS
    solid_mod = path_obj.modifiers.new(name="Driveway_Thickness", type='SOLIDIFY')
    solid_mod.thickness = thickness
    solid_mod.offset = -1.0 # Pushes the slab downwards
    
    # Force Viewport Graph Update
    bpy.context.view_layer.objects.active = path_obj
    bpy.context.view_layer.update()
    print("="*40)
    print("DRIVEWAY EXTENDED FLAT & SLOPED SUCCESSFULLY")
    print("="*40 + "\n")
    
    return path_obj

def create_sloping_driveway(name="Driveway", width=4.0, thickness=0.15, image_path="",     path_points = [
        mathutils.Vector((-10, 10, -1)),       
        mathutils.Vector((-15, 20, -1.5))   
    ]):
    print("\n" + "="*50)
    print(f"STARTING TEXTURED DRIVEWAY RE-BUILD: '{name}'")
    print("="*50)
    MY_LOCAL_IMAGE = r"C:\Users\Tom (local)\GH\Kakaforest\textures\gray_rocks\gray_rocks_diff_1k.jpg"    
    image_path = image_path if image_path else MY_LOCAL_IMAGE   

    # ---------------------------------------------------------
    # 1. CLEANUP PREVIOUS RUN OBJECTS
    # ---------------------------------------------------------
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    if f"{name}_Profile" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[f"{name}_Profile"], do_unlink=True)


    
    # ---------------------------------------------------------
    # 2. GENERATE THE GEOMETRY SWEEP (Fitted To Your Slopes)
    # ---------------------------------------------------------
    path_data = bpy.data.curves.new(name=f"{name}_Path_Data", type='CURVE')
    path_data.dimensions = '3D'
    path_data.twist_mode = 'Z_UP' 
    
    polyline = path_data.splines.new('BEZIER')
    polyline.bezier_points.add(len(path_points) - 1)
    for i, p in enumerate(path_points):
        bp = polyline.bezier_points[i]
        bp.co = p
        bp.tilt = 0.0
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        
    path_obj = bpy.data.objects.new(name, path_data)
    bpy.context.collection.objects.link(path_obj)
    
    # Horizontal profile definition
    profile_data = bpy.data.curves.new(name=f"{name}_Prof_Data", type='CURVE')
    profile_data.dimensions = '2D'
    prof_line = profile_data.splines.new('POLY')
    prof_line.points.add(1)
    half_w = width / 2.0
    prof_line.points[0].co = (-half_w, 0, 0, 1)
    prof_line.points[1].co = (half_w, 0, 0, 1)
    
    profile_obj = bpy.data.objects.new(f"{name}_Profile", profile_data)
    bpy.context.collection.objects.link(profile_obj)
    profile_obj.hide_viewport = True
    profile_obj.hide_render = True
    
    path_data.bevel_mode = 'OBJECT'
    path_data.bevel_object = profile_obj
    path_data.use_fill_caps = True 
    
    solid_mod = path_obj.modifiers.new(name="Driveway_Thickness", type='SOLIDIFY')
    solid_mod.thickness = thickness
    solid_mod.offset = -1.0 

    # ---------------------------------------------------------
    # 3. PROCEDURAL PBR IMAGE MATERIAL SETUP
    # ---------------------------------------------------------
    mat_name = f"{name}_Gravel_Material"
    # If material already exists, grab it, otherwise make it fresh
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)
        
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear() # Wipe clean
    
    # Create required standard node blocks
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (400, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (100, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.95 # Matte stones
    
    # Texture coordinate maps texture onto curve layout
    node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
    node_tex_coord.location = (-600, 0)
    
    # Mapping node handles tiling (prevents giant stretched rocks)
    node_mapping = nodes.new(type='ShaderNodeMapping')
    node_mapping.location = (-400, 0)
    # SCALE CONTROL: Tells image to repeat 5 times over X/Y space
    node_mapping.inputs['Scale'].default_value[0] = 3.0
    node_mapping.inputs['Scale'].default_value[1] = 3.0
    
    # Image node imports your specific jpg file
    node_image = nodes.new(type='ShaderNodeTexImage')
    node_image.location = (-150, 0)
    
    # Load image file safely via Python API
    if os.path.exists(image_path):
        loaded_img = bpy.data.images.load(image_path, check_existing=True)
        node_image.image = loaded_img
        print(f"-> Successfully loaded image texture file from: {image_path}")
    else:
        print(f"CRITICAL WARNING: Texture file path not found: {image_path}")
        print("Driveway mesh created but will appear magenta/pink until image link is fixed.")
        
    # Hook everything up sequentially
    links.new(node_tex_coord.outputs['Object'], node_mapping.inputs['Vector'])
    links.new(node_mapping.outputs['Vector'], node_image.inputs['Vector'])
    links.new(node_image.outputs['Color'], node_bsdf.inputs['Base Color'])
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    # ---------------------------------------------------------
    # 4. ASSIGN MATERIAL & PUSH TO VIEWPORT
    # ---------------------------------------------------------
    if path_obj.data.materials:
        path_obj.data.materials[0] = mat
    else:
        path_obj.data.materials.append(mat)
        
    bpy.context.view_layer.objects.active = path_obj
    bpy.context.view_layer.update()
    print("="*50)
    print("FINISHED EXECUTING TEXTURED SYSTEM SUCCESSFULLY")
    print("="*50 + "\n")
    
    return path_obj