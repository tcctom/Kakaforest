import bpy  # type: ignore
import math
import os

from materials import get_interior_wall_material, get_metal_roof_material
from utils import add_window, add_door


def create_black_box_profile_roof_material():
    """Create a black corrugated roof material using the box profile displacement map as bump."""
    material_name = "PorchRoof_BlackBoxProfile"
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        mat = bpy.data.materials.new(name=material_name)

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new(type='ShaderNodeOutputMaterial')
    out.location = (500, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (220, 0)
    bsdf.inputs['Base Color'].default_value = (0.03, 0.03, 0.03, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.45
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    disp_path = os.path.abspath("textures/box_profile_metal_sheet/box_profile_metal_sheet_disp_1k.png")
    if not os.path.exists(disp_path):
        disp_path = os.path.abspath("textures/box_profile_metal_sheet/box_profile_metal_sheet_disp_1k.jpg")

    if os.path.exists(disp_path):
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-700, -150)

        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-500, -150)
        mapping.inputs['Scale'].default_value = (8.0, 2.0, 1.0)
        mapping.inputs['Rotation'].default_value[2] = 1.5708  # 90 degrees

        disp_tex = nodes.new(type='ShaderNodeTexImage')
        disp_tex.location = (-280, -150)
        disp_tex.image = bpy.data.images.load(disp_path, check_existing=True)
        disp_tex.image.colorspace_settings.name = 'Non-Color'

        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (-20, -150)
        bump.inputs['Strength'].default_value = 0.20
        bump.inputs['Distance'].default_value = 0.02

        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], disp_tex.inputs['Vector'])
        links.new(disp_tex.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    else:
        print(f"[PORCH DEBUG] missing box-profile texture: {disp_path}")

    return mat


def create_porch_wall(name, location, size, exterior_mat, interior_face_index=None):
    """Create a porch wall and assign exterior cladding to the outside face set."""
    bpy.ops.mesh.primitive_cube_add(location=location)
    wall_obj = bpy.context.active_object
    wall_obj.name = name
    wall_obj.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)

    wall_obj.data.materials.append(exterior_mat)

    if interior_face_index is not None:
        interior_mat = get_interior_wall_material()
        wall_obj.data.materials.append(interior_mat)
        wall_obj.data.polygons[interior_face_index].material_index = 1

    #print(
    #    f"[PORCH DEBUG] created {name}: "
    #    f"location={tuple(round(v, 3) for v in wall_obj.location)} "
    #    f"dimensions={tuple(round(v, 3) for v in wall_obj.dimensions)} "
    #    f"verts={len(wall_obj.data.vertices)}"
    #)

    return wall_obj


def _debug_wall_bounds(wall_obj, label):
    xs = []
    ys = []
    zs = []
    for vert in wall_obj.data.vertices:
        world = wall_obj.matrix_world @ vert.co
        xs.append(world.x)
        ys.append(world.y)
        zs.append(world.z)

    #print(
    #    f"[PORCH DEBUG] {label} {wall_obj.name}: "
    #    f"x=({min(xs):.3f},{max(xs):.3f}) "
    #    f"y=({min(ys):.3f},{max(ys):.3f}) "
    #    f"z=({min(zs):.3f},{max(zs):.3f})"
    #)


def slope_wall_top_to_roof(wall_obj, roof_building_y, roof_outer_y, roof_high_height, roof_low_height, roof_clearance=0.02):
    """Slope the top vertices of a wall so they follow the porch roof line in Y."""
    _debug_wall_bounds(wall_obj, "before slope")

    roof_y_span = roof_outer_y - roof_building_y
    roof_z_span = roof_low_height - roof_high_height

    if roof_y_span == 0:
        return wall_obj

    max_local_z = max(vert.co.z for vert in wall_obj.data.vertices)
    top_vertex_tolerance = 0.001

    for vert in wall_obj.data.vertices:
        if vert.co.z < max_local_z - top_vertex_tolerance:
            continue

        world_pos = wall_obj.matrix_world @ vert.co
        world_y = world_pos.y
        t = (world_y - roof_building_y) / roof_y_span
        t = max(0.0, min(1.0, t))
        target_world_z = (roof_high_height + (roof_z_span * t)) - roof_clearance
        vert.co.z += target_world_z - world_pos.z

    wall_obj.data.update()

    bpy.context.view_layer.objects.active = wall_obj
    wall_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    wall_obj.select_set(False)

    _debug_wall_bounds(wall_obj, "after slope")

    return wall_obj


def build_simple_open_porch(
    ox,
    oy,
    oz,
    LENGTH,
    GROUND_FLOOR_HEIGHT,
    EXTERIOR_WALL_THICKNESS,
    floor_mat,
    create_textured_material,
    deck_texture_path,
):
    """Create the simple west-side entrance porch with deck, steps, door opening, and roof."""
    # Porch dimensions: 2.5m wide x 1.5m deep, OPEN (no walls)
    PORCH_WIDTH = 2.5  # North-south dimension
    PORCH_DEPTH = 1.5  # East-west depth

    # Porch deck - positioned west of west wall, centered
    porch_center_x = ox - LENGTH / 2 - PORCH_DEPTH / 2
    porch_center_y = oy

    bpy.ops.mesh.primitive_cube_add(location=(porch_center_x, porch_center_y, oz + 0.05))
    porch_deck = bpy.context.active_object
    porch_deck.name = "MainDwelling_PorchDeck_Simple"
    porch_deck.scale = (PORCH_DEPTH / 2, PORCH_WIDTH / 2, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    porch_deck.data.materials.append(floor_mat)

    # UV unwrap for porch deck texture display
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Steps down from porch deck on west side - using decking material
    STEP_WIDTH = 2.5  # Full porch width (north-south)
    STEP_DEPTH = 0.4  # 400mm deep (east-west)
    STEP_HEIGHT = 0.16  # 160mm rise per step
    NUM_STEPS = 7  # Total number of steps
    deck_mat = create_textured_material("TimberDecking", deck_texture_path)

    for i in range(NUM_STEPS):
        step_x = ox - LENGTH / 2 - PORCH_DEPTH - STEP_DEPTH / 2 - (i * STEP_DEPTH)
        step_z = oz + 0.05 - STEP_HEIGHT * (i + 1)

        bpy.ops.mesh.primitive_cube_add(location=(step_x, porch_center_y, step_z))
        step = bpy.context.active_object
        step.name = f"MainDwelling_PorchStep{i + 1}_Simple"
        step.scale = (STEP_DEPTH / 2, STEP_WIDTH / 2, STEP_HEIGHT / 2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(deck_mat)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')

    # Main entrance door on main building west wall
    main_door_x = ox - LENGTH / 2
    add_window( "MD_GF_WestWall",
        (main_door_x, oy, oz + 1.0),
        width=0.9, height=2.0, depth=EXTERIOR_WALL_THICKNESS,
        axis='X', inward_offset='+X',
    )

    # Monopitch porch roof - high at building, low at outer edge
    PORCH_ROOF_PITCH = 15
    PORCH_ROOF_OVERHANG = 0.3

    # Define roof boundaries early to calculate the true span
    porch_roof_building = ox - LENGTH / 2
    porch_roof_outer = ox - LENGTH / 2 - PORCH_DEPTH - PORCH_ROOF_OVERHANG
    porch_roof_span = abs(porch_roof_outer - porch_roof_building)

    # Base the vertical drop on the full span to maintain a true 15-degree angle
    porch_roof_high_height = oz + GROUND_FLOOR_HEIGHT
    porch_roof_drop = porch_roof_span * math.tan(math.radians(PORCH_ROOF_PITCH))
    porch_roof_low_height = porch_roof_high_height - porch_roof_drop

    #print(
    #    "[PORCH DEBUG] roof south porch: "
    #    f"building_y={porch_roof_building:.3f} outer_y={porch_roof_outer:.3f} "
    #    f"high_z={porch_roof_high_height:.3f} low_z={porch_roof_low_height:.3f}"
    #)
    
    # Track the exact dynamic angle in radians for the fascia boards
    actual_roof_pitch_rad = math.radians(PORCH_ROOF_PITCH)

    # Support posts on west edge of porch
    POST_SIZE = 0.15
    POST_INSET = 0.2
    post_x = ox - LENGTH / 2 - PORCH_DEPTH
    post_height = porch_roof_low_height - oz

    post_north_y = oy + PORCH_WIDTH / 2 - POST_INSET
    bpy.ops.mesh.primitive_cube_add(location=(post_x, post_north_y, oz + post_height / 2))
    post_north = bpy.context.active_object
    post_north.name = "MainDwelling_PorchPost_North"
    post_north.scale = (POST_SIZE / 2, POST_SIZE / 2, post_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    post_north.data.materials.append(floor_mat)

    post_south_y = oy - PORCH_WIDTH / 2 + POST_INSET
    bpy.ops.mesh.primitive_cube_add(location=(post_x, post_south_y, oz + post_height / 2))
    post_south = bpy.context.active_object
    post_south.name = "MainDwelling_PorchPost_South"
    post_south.scale = (POST_SIZE / 2, POST_SIZE / 2, post_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    post_south.data.materials.append(floor_mat)

    porch_roof_mesh = bpy.data.meshes.new("MainDwelling_PorchRoof_Monopitch")
    porch_roof_obj = bpy.data.objects.new("MainDwelling_PorchRoof_Simple", porch_roof_mesh)
    bpy.context.collection.objects.link(porch_roof_obj)

    porch_roof_north = oy + PORCH_WIDTH / 2 + PORCH_ROOF_OVERHANG
    porch_roof_south = oy - PORCH_WIDTH / 2 - PORCH_ROOF_OVERHANG

    porch_verts = [
        (porch_roof_building, porch_roof_north, porch_roof_high_height),
        (porch_roof_building, porch_roof_south, porch_roof_high_height),
        (porch_roof_outer, porch_roof_north, porch_roof_low_height),
        (porch_roof_outer, porch_roof_south, porch_roof_low_height),
    ]
    porch_faces = [
        (0, 1, 3, 2),
    ]

    porch_roof_mesh.from_pydata(porch_verts, [], porch_faces)
    porch_roof_mesh.update()
    porch_roof_obj.data.materials.append(get_metal_roof_material())

    bpy.context.view_layer.objects.active = porch_roof_obj
    porch_roof_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    porch_roof_obj.select_set(False)

    # Add roof structure for realism
    FASCIA_HEIGHT = 0.20
    FASCIA_THICKNESS = 0.025
    PURLIN_SIZE = (0.090, 0.045)

    fascia_west_x = porch_roof_outer - FASCIA_THICKNESS / 2
    fascia_west_y = (porch_roof_north + porch_roof_south) / 2
    fascia_west_z = porch_roof_low_height - FASCIA_HEIGHT / 2

    bpy.ops.mesh.primitive_cube_add(location=(fascia_west_x, fascia_west_y, fascia_west_z))
    fascia_west = bpy.context.active_object
    fascia_west.name = "MainDwelling_PorchRoof_FasciaWest"
    fascia_west_length = porch_roof_south - porch_roof_north
    fascia_west.scale = (FASCIA_THICKNESS / 2, fascia_west_length / 2, FASCIA_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    fascia_west.data.materials.append(floor_mat)

    fascia_north_x = (porch_roof_building + porch_roof_outer) / 2
    fascia_north_y = porch_roof_north + FASCIA_THICKNESS / 2
    fascia_north_z_high = porch_roof_high_height - FASCIA_HEIGHT / 2
    fascia_north_z_low = porch_roof_low_height - FASCIA_HEIGHT / 2
    fascia_north_z = (fascia_north_z_high + fascia_north_z_low) / 2
    fascia_north_length = porch_roof_span

    bpy.ops.mesh.primitive_cube_add(location=(fascia_north_x, fascia_north_y, fascia_north_z))
    fascia_north = bpy.context.active_object
    fascia_north.name = "MainDwelling_PorchRoof_FasciaNorth"
    fascia_north.scale = (fascia_north_length / 2, FASCIA_THICKNESS / 2, FASCIA_HEIGHT / 2)
    fascia_north.rotation_euler[1] = -actual_roof_pitch_rad
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    fascia_north.data.materials.append(floor_mat)

    fascia_south_y = porch_roof_south - FASCIA_THICKNESS / 2

    bpy.ops.mesh.primitive_cube_add(location=(fascia_north_x, fascia_south_y, fascia_north_z))
    fascia_south = bpy.context.active_object
    fascia_south.name = "MainDwelling_PorchRoof_FasciaSouth"
    fascia_south.scale = (fascia_north_length / 2, FASCIA_THICKNESS / 2, FASCIA_HEIGHT / 2)
    fascia_south.rotation_euler[1] = -actual_roof_pitch_rad
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    fascia_south.data.materials.append(floor_mat)

    PURLIN_SPACING = 0.6
    num_purlins = int(porch_roof_span / PURLIN_SPACING)

    for i in range(1, num_purlins):
        purlin_x = porch_roof_building - (i * PURLIN_SPACING)
        purlin_y = (porch_roof_north + porch_roof_south) / 2
        distance_from_high = abs(purlin_x - porch_roof_building)
        slope_drop = distance_from_high * math.tan(math.radians(PORCH_ROOF_PITCH))
        purlin_z = porch_roof_high_height - slope_drop - PURLIN_SIZE[1] / 2

        bpy.ops.mesh.primitive_cube_add(location=(purlin_x, purlin_y, purlin_z))
        purlin = bpy.context.active_object
        purlin.name = f"MainDwelling_PorchRoof_Purlin_{i}"
        purlin_length = porch_roof_south - porch_roof_north
        purlin.scale = (PURLIN_SIZE[0] / 2, purlin_length / 2, PURLIN_SIZE[1] / 2)
        bpy.ops.object.transform_apply(scale=True)
        purlin.data.materials.append(floor_mat)


def build_porch_south_side(
    ox,
    oy,
    oz,
    WIDTH,
    LENGTH,
    GROUND_FLOOR_HEIGHT,
    EXTERIOR_WALL_THICKNESS,
    floor_mat,
    create_textured_material,
    deck_texture_path,
    exterior_mat,
    west_corner_miter_run=0.90,
    miter_seam_overlap=0.02,
):
    """Create a simple open porch on the south wall with a 6m west-to-east run and monopitch roof."""
    PORCH_LENGTH = 7.9  # West-to-east run
    PORCH_DECK_LENGTH = 3.2  # West-to-east run
    PORCH_DEPTH = 1.8  # South projection depth
    PORCH_ROOF_PITCH = 20
    PORCH_ROOF_OVERHANG = 0.01
    PORCH_EXTERIOR_WALL_THICKNESS = 0.15
    PORCH_INTERIOR_WALL_THICKNESS = 0.11

    porch_west_x = ox - LENGTH / 2
    south_wall_outer_y = oy - WIDTH / 2
    porch_roof_high_height = oz + 2.6

    porch_east_x = porch_west_x + PORCH_LENGTH
    porch_deck_center_x = porch_west_x + PORCH_DECK_LENGTH / 2
    porch_center_y = south_wall_outer_y - PORCH_DEPTH / 2
    floor_top = oz - 0.1
    deck_z = oz-0.25

    bpy.ops.mesh.primitive_cube_add(location=(porch_deck_center_x, porch_center_y, deck_z))
    porch_deck = bpy.context.active_object
    porch_deck.name = "MD_PorchDeck_South"
    porch_deck.scale = (PORCH_DECK_LENGTH / 2, PORCH_DEPTH / 2, 0.05)
    bpy.ops.object.transform_apply(scale=True)

    deck_mat = create_textured_material("TimberDecking", deck_texture_path)
    porch_deck.data.materials.append(deck_mat)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    porch_wall_height = 2.3
    porch_wall_z = floor_top + porch_wall_height / 2 
    porch_south_wall = create_porch_wall( name="MD_GF_SouthExtension",
        location=(ox + 0.75, south_wall_outer_y - PORCH_DEPTH, porch_wall_z-0.2),
        size=(PORCH_LENGTH-PORCH_DECK_LENGTH -0.05, PORCH_EXTERIOR_WALL_THICKNESS, porch_wall_height-0.3), exterior_mat=exterior_mat, interior_face_index=1, )
    porch_east_wall = create_porch_wall( name="MD_GF_SouthExtension2",
        location=(ox + 3.0, south_wall_outer_y - PORCH_DEPTH/2, porch_wall_z),
        size=(PORCH_EXTERIOR_WALL_THICKNESS, PORCH_DEPTH, porch_wall_height), exterior_mat=exterior_mat, interior_face_index=0, )
    porch_west_wall = create_porch_wall( name="MD_GF_SouthExtensionWest",
        location=(ox-1.5, south_wall_outer_y - PORCH_DEPTH/2, porch_wall_z),
        size=(PORCH_EXTERIOR_WALL_THICKNESS, PORCH_DEPTH, porch_wall_height), exterior_mat=exterior_mat, interior_face_index=2, )
    porch_interior_wall = create_porch_wall( name="MD_GF_SouthExtensionInterior",
        location=(ox + 0.8, south_wall_outer_y - PORCH_DEPTH/2, porch_wall_z),
        size=(PORCH_INTERIOR_WALL_THICKNESS, PORCH_DEPTH, porch_wall_height), exterior_mat=exterior_mat, interior_face_index=0, )

    porch_roof_building = south_wall_outer_y
    porch_roof_outer = south_wall_outer_y - PORCH_DEPTH - PORCH_ROOF_OVERHANG - 0.07
    porch_roof_span = abs(porch_roof_outer - porch_roof_building)

    porch_roof_drop = porch_roof_span * math.tan(math.radians(PORCH_ROOF_PITCH))
    porch_roof_low_height = porch_roof_high_height - porch_roof_drop

    #slope_wall_top_to_roof( porch_south_wall, porch_roof_building, porch_roof_outer, porch_roof_high_height, porch_roof_low_height, )
    slope_wall_top_to_roof( porch_east_wall, porch_roof_building, porch_roof_outer, porch_roof_high_height, porch_roof_low_height, )
    slope_wall_top_to_roof( porch_west_wall, porch_roof_building, porch_roof_outer, porch_roof_high_height, porch_roof_low_height, )
    slope_wall_top_to_roof( porch_interior_wall, porch_roof_building, porch_roof_outer, porch_roof_high_height, porch_roof_low_height, )


    add_window( "MD_GF_SouthExtension", (ox - 0.35, south_wall_outer_y - PORCH_DEPTH - PORCH_EXTERIOR_WALL_THICKNESS / 2, floor_top + 1.5),
        width=1.2, height=0.9, depth=PORCH_EXTERIOR_WALL_THICKNESS, axis='Y', inward_offset='+Y',    )

    add_door( "MD_GF_SouthExtensionWest", (ox - 1.5 + PORCH_EXTERIOR_WALL_THICKNESS / 2, south_wall_outer_y - PORCH_DEPTH/2, floor_top),
        width=0.9, height=2.0, depth=PORCH_EXTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X', open_angle_degrees=90, hinge_side='right',    )

    add_door( "MD_GF_SouthExtensionInterior", (ox + 0.8 + PORCH_INTERIOR_WALL_THICKNESS/2, south_wall_outer_y - 1.25, floor_top),
        width=0.7, height=2.0, depth=PORCH_INTERIOR_WALL_THICKNESS, axis='X', inward_offset='-X', open_angle_degrees=-90, hinge_side='left',    )

    #_debug_wall_bounds(porch_south_wall, "after window cut")
    #_debug_wall_bounds(porch_east_wall, "after window cut")
    #_debug_wall_bounds(porch_west_wall, "after window cut")

    porch_roof_west = porch_west_x - PORCH_ROOF_OVERHANG
    porch_roof_east = porch_east_x + PORCH_ROOF_OVERHANG

    POST_SIZE = 0.15
    POST_INSET = 0.2
    post_y = south_wall_outer_y - PORCH_DEPTH
    post_height = porch_roof_low_height - deck_z

    post_west_x = porch_west_x + POST_INSET
    bpy.ops.mesh.primitive_cube_add(location=(post_west_x, post_y, deck_z + post_height / 2) )
    post_west = bpy.context.active_object
    post_west.name = "MD_PorchPost_SouthWest"
    post_west.scale = (POST_SIZE / 2, POST_SIZE / 2, post_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    post_west.data.materials.append(floor_mat)

    #post_east_x = porch_east_x - POST_INSET
    #bpy.ops.mesh.primitive_cube_add(location=(post_east_x, post_y, deck_z + post_height / 2))
    #post_east = bpy.context.active_object
    #post_east.name = "MD_PorchPost_SouthEast"
    #post_east.scale = (POST_SIZE / 2, POST_SIZE / 2, post_height / 2)
    #bpy.ops.object.transform_apply(scale=True)
    #post_east.data.materials.append(floor_mat)

    porch_roof_mesh = bpy.data.meshes.new("MD_PorchRoof_Monopitch_South")
    porch_roof_obj = bpy.data.objects.new("MD_PorchRoof_South", porch_roof_mesh)
    bpy.context.collection.objects.link(porch_roof_obj)

    roof_thickness = 0.07
    # 45-degree miter seam from the building corner out to the southwest roof edge.
    # Ensure the seam reaches at least the full roof span so the two roofs meet.
    miter_run = max(0.0, max(west_corner_miter_run, porch_roof_span) + miter_seam_overlap)
    miter_low_x = porch_west_x - miter_run

    porch_verts = [
        # top surface
        (porch_west_x, porch_roof_building, porch_roof_high_height),
        (porch_roof_east, porch_roof_building, porch_roof_high_height),
        (miter_low_x, porch_roof_outer, porch_roof_low_height),
        (porch_roof_east, porch_roof_outer, porch_roof_low_height),
        # underside surface
        (porch_west_x, porch_roof_building, porch_roof_high_height - roof_thickness),
        (porch_roof_east, porch_roof_building, porch_roof_high_height - roof_thickness),
        (miter_low_x, porch_roof_outer, porch_roof_low_height - roof_thickness),
        (porch_roof_east, porch_roof_outer, porch_roof_low_height - roof_thickness),
    ]
    porch_faces = [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 2, 6, 4),
        (1, 5, 7, 3),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
    ]

    porch_roof_mesh.from_pydata(porch_verts, [], porch_faces)
    porch_roof_mesh.update()
    porch_roof_obj.data.materials.append(create_black_box_profile_roof_material())

    # Exposed rafters under the roof panel.
    rafter_width = 0.06
    rafter_height = 0.12
    rafter_inset = 0.15
    rafter_end_overhang = 0.00
    rafter_spacing = 0.8
    pitch_rad = math.radians(PORCH_ROOF_PITCH)

    # Run rafters close to full roof depth, with a slight extension beyond the wall lines.
    rafter_count = max(2, int(PORCH_LENGTH / rafter_spacing) + 1)
    start_x = miter_low_x + rafter_inset
    end_x = porch_east_x - rafter_inset
    actual_spacing = (end_x - start_x) / (rafter_count - 1)

    for i in range(rafter_count):
        rafter_x = start_x + i * actual_spacing

        # Respect the 45-degree miter by shortening rafters near the southwest corner.
        local_high_y = porch_roof_building
        if miter_run > 0.0 and rafter_x < porch_west_x:
            local_high_y = porch_roof_building + (rafter_x - porch_west_x)
        local_span = max(0.15, local_high_y - porch_roof_outer)
        local_center_y = (local_high_y + porch_roof_outer) / 2
        t = (local_center_y - porch_roof_building) / (porch_roof_outer - porch_roof_building)
        local_top_z = porch_roof_high_height + (porch_roof_low_height - porch_roof_high_height) * t
        local_rafter_z = local_top_z - roof_thickness - rafter_height / 2 - 0.01

        bpy.ops.mesh.primitive_cube_add(location=(rafter_x, local_center_y, local_rafter_z))
        rafter = bpy.context.active_object
        rafter.name = f"MainDwelling_PorchRafter_{i + 1:02d}"
        rafter.scale = (rafter_width / 2, local_span / 2, rafter_height / 2)
        rafter.rotation_euler[0] = pitch_rad
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        rafter.data.materials.append(floor_mat)

    bpy.context.view_layer.objects.active = porch_roof_obj
    porch_roof_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    porch_roof_obj.select_set(False)


def build_verandah_west_side(
    ox,
    oy,
    oz,
    WIDTH,
    LENGTH,
    floor_mat,
    create_textured_material,
    deck_texture_path,
    south_overlap=0.0,
    south_corner_miter_run=0.90,
    deck_south_extension=1.8,
    miter_seam_overlap=0.02,
):
    """
    Create a west-side verandah that connects to the south porch and runs
    north along the outside of the main west wall.
    Uses the same deck and roof style as the south porch.

    Args:
        south_overlap: Extra overlap (meters) to extend south for seamless
            connection with the south porch deck/roof edge.
    """
    VERANDAH_RUN_NORTH = 5.0
    VERANDAH_DEPTH = 1.8
    VERANDAH_ROOF_PITCH = 20
    VERANDAH_ROOF_OVERHANG = 0.01

    west_wall_outer_x = ox - LENGTH / 2
    south_wall_outer_y = oy - WIDTH / 2

    # Extend slightly south to guarantee visual/physical overlap at junction.
    verandah_south_y = south_wall_outer_y - south_overlap
    verandah_north_y = south_wall_outer_y + VERANDAH_RUN_NORTH
    verandah_total_run = verandah_north_y - verandah_south_y
    verandah_center_y = (verandah_south_y + verandah_north_y) / 2
    verandah_center_x = west_wall_outer_x - VERANDAH_DEPTH / 2

    deck_z = oz - 0.25
    porch_roof_high_height = oz + 2.6

    # Deck slab extends south so it joins the south porch deck footprint.
    deck_south_y = verandah_south_y - deck_south_extension
    deck_north_y = verandah_north_y
    deck_total_run = deck_north_y - deck_south_y
    deck_center_y = (deck_south_y + deck_north_y) / 2

    bpy.ops.mesh.primitive_cube_add(location=(verandah_center_x, deck_center_y, deck_z))
    verandah_deck = bpy.context.active_object
    verandah_deck.name = "MD_VerandahDeck_West"
    verandah_deck.scale = (VERANDAH_DEPTH / 2, deck_total_run / 2, 0.05)
    bpy.ops.object.transform_apply(scale=True)

    deck_mat = create_textured_material("TimberDecking", deck_texture_path)
    verandah_deck.data.materials.append(deck_mat)

    bpy.context.view_layer.objects.active = verandah_deck
    verandah_deck.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    verandah_deck.select_set(False)

    verandah_roof_building_x = west_wall_outer_x
    verandah_roof_outer_x = west_wall_outer_x - VERANDAH_DEPTH - VERANDAH_ROOF_OVERHANG - 0.07
    verandah_roof_span = abs(verandah_roof_outer_x - verandah_roof_building_x)

    verandah_roof_drop = verandah_roof_span * math.tan(math.radians(VERANDAH_ROOF_PITCH))
    verandah_roof_low_height = porch_roof_high_height - verandah_roof_drop

    verandah_roof_south = verandah_south_y - VERANDAH_ROOF_OVERHANG
    verandah_roof_north = verandah_north_y + VERANDAH_ROOF_OVERHANG

    # 45-degree miter seam from the building corner out to the southwest roof edge.
    # Ensure the seam reaches at least the full roof span so the two roofs meet.
    miter_run = max(0.0, max(south_corner_miter_run, verandah_roof_span) + miter_seam_overlap)
    verandah_roof_south = min(verandah_roof_south, south_wall_outer_y - miter_run)
    miter_low_y = south_wall_outer_y - miter_run

    # Corner posts along outer edge (open verandah).
    POST_SIZE = 0.15
    POST_INSET = 0.2
    post_x = west_wall_outer_x - VERANDAH_DEPTH
    post_height = verandah_roof_low_height - deck_z

    post_south_y = verandah_roof_south + POST_INSET
    post_north_y = verandah_roof_north - POST_INSET
    post_mid_y = (post_south_y + post_north_y) / 2
    for i, post_y in enumerate((post_south_y, post_mid_y, post_north_y), start=1):
        bpy.ops.mesh.primitive_cube_add(location=(post_x, post_y, deck_z + post_height / 2))
        post = bpy.context.active_object
        post.name = f"MD_VerandahPost_West_{i}"
        post.scale = (POST_SIZE / 2, POST_SIZE / 2, post_height / 2)
        bpy.ops.object.transform_apply(scale=True)
        post.data.materials.append(floor_mat)

    verandah_roof_mesh = bpy.data.meshes.new("MD_VerandahRoof_Monopitch_West")
    verandah_roof_obj = bpy.data.objects.new("MD_VerandahRoof_West", verandah_roof_mesh)
    bpy.context.collection.objects.link(verandah_roof_obj)

    roof_thickness = 0.07
    roof_verts = [
        # Top surface: high near building (east), low at outer west edge.
        (verandah_roof_building_x, south_wall_outer_y, porch_roof_high_height),
        (verandah_roof_building_x, verandah_roof_north, porch_roof_high_height),
        (verandah_roof_outer_x, miter_low_y, verandah_roof_low_height),
        (verandah_roof_outer_x, verandah_roof_north, verandah_roof_low_height),
        # Underside.
        (verandah_roof_building_x, south_wall_outer_y, porch_roof_high_height - roof_thickness),
        (verandah_roof_building_x, verandah_roof_north, porch_roof_high_height - roof_thickness),
        (verandah_roof_outer_x, miter_low_y, verandah_roof_low_height - roof_thickness),
        (verandah_roof_outer_x, verandah_roof_north, verandah_roof_low_height - roof_thickness),
    ]
    roof_faces = [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 2, 6, 4),
        (1, 5, 7, 3),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
    ]

    verandah_roof_mesh.from_pydata(roof_verts, [], roof_faces)
    verandah_roof_mesh.update()
    verandah_roof_obj.data.materials.append(create_black_box_profile_roof_material())

    # Exposed rafters, matching south porch style but arrayed along north-south run.
    rafter_width = 0.06
    rafter_height = 0.12
    rafter_inset = 0.15
    rafter_end_overhang = 0.00
    rafter_spacing = 0.8
    pitch_rad = math.radians(VERANDAH_ROOF_PITCH)

    rafter_count = max(2, int(verandah_total_run / rafter_spacing) + 1)
    start_y = miter_low_y + rafter_inset
    end_y = verandah_north_y - rafter_inset
    actual_spacing = (end_y - start_y) / (rafter_count - 1)

    for i in range(rafter_count):
        rafter_y = start_y + i * actual_spacing

        # Respect the 45-degree miter by shortening rafters near the southwest corner.
        local_building_x = verandah_roof_building_x
        if miter_run > 0.0 and rafter_y < south_wall_outer_y:
            local_building_x = verandah_roof_building_x + (rafter_y - south_wall_outer_y)
        local_span = max(0.15, local_building_x - verandah_roof_outer_x)
        local_center_x = (local_building_x + verandah_roof_outer_x) / 2
        t = (local_center_x - verandah_roof_building_x) / (verandah_roof_outer_x - verandah_roof_building_x)
        local_top_z = porch_roof_high_height + (verandah_roof_low_height - porch_roof_high_height) * t
        local_rafter_z = local_top_z - roof_thickness - rafter_height / 2 - 0.01

        bpy.ops.mesh.primitive_cube_add(location=(local_center_x, rafter_y, local_rafter_z))
        rafter = bpy.context.active_object
        rafter.name = f"MD_VerandahRafter_West_{i + 1:02d}"
        rafter.scale = (local_span / 2, rafter_width / 2, rafter_height / 2)
        rafter.rotation_euler[1] = -pitch_rad
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        rafter.data.materials.append(floor_mat)

    bpy.context.view_layer.objects.active = verandah_roof_obj
    verandah_roof_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    verandah_roof_obj.select_set(False)
