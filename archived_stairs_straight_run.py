# ARCHIVED STAIRS IMPLEMENTATION - Straight-run stairs
# Date archived: 2026-05-27
# Reason: Replaced with dog-legged staircase with intermediate landing and battery storage

"""
Original straight-run staircase implementation
Location: Just west of 4m bedroom partition (x = 4.7m from east interior)
Configuration: Single straight run, 2.2m N-S × 1.2m E-W opening, 12 steps
"""

import bpy  # type: ignore

def create_material(name, color):
    """Create or get a material with the given name and color"""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return mat


def create_straight_run_stairs_archived(ox, oy, oz, LENGTH, GROUND_FLOOR_HEIGHT, EXTERIOR_WALL_THICKNESS, first_floor_slab):
    """
    ARCHIVED: Create straight-run stairs with opening in first floor slab
    
    This function creates the original straight-run staircase that was replaced.
    - Position: 4.7m from east interior wall, slightly north of center
    - Opening: 2.2m N-S × 1.2m E-W
    - Steps: 12 straight-run steps from north to south
    
    Args:
        ox, oy, oz: Origin coordinates
        LENGTH: Building length (9m)
        GROUND_FLOOR_HEIGHT: Height of ground floor (2.5m)
        EXTERIOR_WALL_THICKNESS: Exterior wall thickness (0.2m)
        first_floor_slab: The first floor slab object to cut opening in
    
    Returns:
        stairs_cutter: The cutter object used for boolean operation
    """
    first_floor_z = oz + GROUND_FLOOR_HEIGHT
    
    # Stairs opening position (just west of 4m bedroom partition line)
    stairs_opening_x = ox - LENGTH/2 + EXTERIOR_WALL_THICKNESS + 4.7  # 0.5m west of bedroom partition
    stairs_opening_y = oy - 0.5  # Slightly north of center
    
    # Create stairs cutter manually (2.2m N-S × 1.2m E-W)
    bpy.ops.mesh.primitive_cube_add(location=(stairs_opening_x, stairs_opening_y, first_floor_z - 0.05))
    stairs_cutter = bpy.context.active_object
    stairs_cutter.name = "MainDwelling_StairsCutter_Archived"
    stairs_cutter.scale = (1.2/2, 2.2/2, 0.05)  # E-W width, N-S length, floor thickness
    bpy.ops.object.transform_apply(scale=True)
    
    # Boolean modifier to cut opening in floor
    bool_mod = first_floor_slab.modifiers.new(name="Stairs_Cut", type='BOOLEAN')
    bool_mod.object = stairs_cutter
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.solver = 'EXACT'
    
    # Hide the cutter
    stairs_cutter.hide_viewport = True
    stairs_cutter.hide_render = True
    
    # Create stairs to match the opening
    STAIR_WIDTH = 1.0  # E-W width (fits within 1.2m opening)
    NUM_STEPS = 12  # 12 steps (13th step is the first floor itself)
    STAIR_RISE = GROUND_FLOOR_HEIGHT / (NUM_STEPS+1)  # ~208mm rise per step
    STAIR_TREAD = 2.2 / NUM_STEPS  # Tread depth spanning 2.2m N-S
    
    stairs_mat = create_material("StairsWood", (0.6, 0.4, 0.25, 1))
    
    # Create individual steps (starting from north, going south)
    for i in range(NUM_STEPS):
        step_height = oz + STAIR_RISE * (i + 1)  # Full rise for each step
        step_y = stairs_opening_y + 2.2/2 - STAIR_TREAD * (i + 0.5)  # Start from north, move south
        
        bpy.ops.mesh.primitive_cube_add(location=(stairs_opening_x, step_y, step_height))
        step = bpy.context.active_object
        step.name = f"MainDwelling_Stairs_Step_Archived_{i+1:02d}"
        step.scale = (STAIR_WIDTH/2, STAIR_TREAD/2, STAIR_RISE/2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(stairs_mat)
    
    return stairs_cutter


# End of archived straight-run stairs implementation
