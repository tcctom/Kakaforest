# Kaka Forest Retreat - Blender Scripting Project

## Environment
- **Blender Version**: 5.1
- **Python API**: bpy (Blender Python API)
- **OS**: Windows

## Project Overview
This project creates a modular site planning system for architectural visualization in Blender. The main goal is to procedurally generate building structures and site layouts for the Kaka Forest Retreat.

## Code Structure
- `main_site_plan.py` - Main orchestration script that builds the complete site
- `björken_module.py` - Red cottage building module
- `wet_wing_module.py` - Potius wet wing building module
- `utils.py` - Shared utility functions (shadowclad grooves, windows, materials)
- Module reloading pattern used for iterative development

## Coordinate System
- **Origin**: (0, 0, 0) is ground level  
- **X-axis**: West (+X) / East (-X)
  - Red cottage (Björken) at X=0 is on the EAST side
  - Wet wing at X=11 is on the WEST side
- **Y-axis**: South (+Y) / North (-Y) 
- **Z-axis**: Up (+Z) / Down (-Z)
- Building fronts typically face North (-Y direction)
- When adding windows: use `axis='Y'` for north/south walls, `axis='X'` for east/west walls

## Coding Conventions
- Use `# type: ignore` comment after `import bpy` to suppress type checking warnings
- Functions use tuple unpacking for origin coordinates: `ox, oy, oz = origin`
- Dimensions typically specified as: `W, D, H` (Width, Depth, Height) in meters
- Material creation pattern: Check if exists with `.get()` before creating new
- Use `bpy.ops.object.transform_apply()` after scaling objects
- Module reload pattern at start of main script for development workflow

## Common Patterns
- **Building modules**: Each module has a `build_*` function that accepts `origin=(x, y, z)` parameter
- **Cleanup**: Start scripts with `cleanup()` function to clear scene
- **Materials**: Create materials with node-based system using Principled BSDF
- **Measurements**: Real-world metric measurements (meters, degrees)

## Architectural Elements
- Shadowclad grooves: Vertical grooves created via boolean difference operations (150mm spacing typical)
- Gable roofs with pitch angles (e.g., 35°)
- Verandahs and building extensions
- Window and door openings

## Helper Conventions
- When suggesting Blender operations, prefer using `bpy.ops` for simplicity in scripts
- Always include location parameters explicitly for clarity
- Consider scale application when dimensions are critical
- Boolean operations are used for architectural details (grooves, openings)
