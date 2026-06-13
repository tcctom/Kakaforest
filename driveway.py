import bpy
import mathutils

def create_sloping_driveway(name="Driveway", width=4.0, thickness=0.15):
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

7