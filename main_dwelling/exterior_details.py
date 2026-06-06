import bpy  # type: ignore


def add_first_floor_balcony_railing(ox, oy, oz, WIDTH, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, create_material):
    """Create a simple timber railing along the first-floor north balcony edge."""
    RAILING_HEIGHT = 1.0  # 1 meter high
    RAILING_POST_SIZE = 0.075  # 75mm square posts
    RAILING_RAIL_HEIGHT = 0.050  # 50mm high horizontal rails
    RAILING_RAIL_DEPTH = 0.040  # 40mm deep horizontal rails
    POST_SPACING = 1.5  # 1.5m between posts

    # Railing position - along north edge of first floor balcony
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    railing_y = oy + WIDTH / 2  # At the north edge of the balcony (1m north of recessed wall)
    railing_west_x = ox - LENGTH / 2 + EXTERIOR_WALL_THICKNESS  # Inside west wall
    railing_east_x = ox + LENGTH / 2 - EXTERIOR_WALL_THICKNESS  # Inside east wall
    railing_length = railing_east_x - railing_west_x

    # Material for railing - use treated timber
    railing_mat = create_material("RailingTimber", (0.55, 0.45, 0.35, 1))

    # Create posts at regular intervals
    num_posts = int(railing_length / POST_SPACING) + 1
    actual_spacing = railing_length / (num_posts - 1) if num_posts > 1 else railing_length

    for i in range(num_posts):
        post_x = railing_west_x + (i * actual_spacing)
        post_z = first_floor_z + RAILING_HEIGHT / 2

        bpy.ops.mesh.primitive_cube_add(location=(post_x, railing_y, post_z))
        post = bpy.context.active_object
        post.name = f"MainDwelling_BalconyRailing_Post_{i + 1:02d}"
        post.scale = (RAILING_POST_SIZE / 2, RAILING_POST_SIZE / 2, RAILING_HEIGHT / 2)
        bpy.ops.object.transform_apply(scale=True)
        post.data.materials.append(railing_mat)

    # Top rail (horizontal)
    top_rail_x = (railing_west_x + railing_east_x) / 2
    top_rail_z = first_floor_z + RAILING_HEIGHT - RAILING_RAIL_HEIGHT / 2

    bpy.ops.mesh.primitive_cube_add(location=(top_rail_x, railing_y, top_rail_z))
    top_rail = bpy.context.active_object
    top_rail.name = "MainDwelling_BalconyRailing_TopRail"
    top_rail.scale = (railing_length / 2, RAILING_RAIL_DEPTH / 2, RAILING_RAIL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    top_rail.data.materials.append(railing_mat)

    # Middle rail (horizontal)
    mid_rail_z = first_floor_z + RAILING_HEIGHT / 2

    bpy.ops.mesh.primitive_cube_add(location=(top_rail_x, railing_y, mid_rail_z))
    mid_rail = bpy.context.active_object
    mid_rail.name = "MainDwelling_BalconyRailing_MidRail"
    mid_rail.scale = (railing_length / 2, RAILING_RAIL_DEPTH / 2, RAILING_RAIL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    mid_rail.data.materials.append(railing_mat)

    # Bottom rail (horizontal)
    bottom_rail_z = first_floor_z + 0.15  # 150mm above floor level

    bpy.ops.mesh.primitive_cube_add(location=(top_rail_x, railing_y, bottom_rail_z))
    bottom_rail = bpy.context.active_object
    bottom_rail.name = "MainDwelling_BalconyRailing_BottomRail"
    bottom_rail.scale = (railing_length / 2, RAILING_RAIL_DEPTH / 2, RAILING_RAIL_HEIGHT / 2)
    bpy.ops.object.transform_apply(scale=True)
    bottom_rail.data.materials.append(railing_mat)
