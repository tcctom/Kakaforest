from materials import get_floor_wood_material


def create_main_dwelling_materials(create_textured_material, exterior_texture_path):
    """Create and return core exterior and floor materials for the main dwelling."""
    potius_mat = create_textured_material("PotiusExterior", exterior_texture_path)
    floor_mat = get_floor_wood_material()
    return potius_mat, floor_mat
