import bpy  # type: ignore
import sys
import os
from importlib import reload

# Add current directory to sys.path so Blender can find your modules
dir = os.path.dirname(bpy.data.filepath)
if dir not in sys.path:
    sys.path.append(dir)

import björken_module
import wet_wing_module
import wet_wing_furniture
import ground_module
import utils

# Reload modules to pick up any changes
reload(utils)
reload(björken_module)
reload(wet_wing_module)
reload(wet_wing_furniture)
reload(ground_module)

def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

cleanup()

# Toggle features on/off
SHOW_GROUND = True  # Set to False to hide ground terrain

# 0. Build ground terrain (optional)
if SHOW_GROUND:
    ground_module.build_ground_terrain(cottage_origin=(0, 0, 0))

# 1. Build existing cottage
# Set show_roof=False to hide roof for interior viewing
björken_module.build_red_cottage(origin=(0, 0, 0))

# 2. Build Wet Wing at your specific coords
# Moved 9m West (+X) and 4m South (+Y)
# Set show_roof=False to hide roof for interior viewing
wet_wing_module.build_potius_wet_wing(origin=(11.0, 4.0, 2.7))
#wet_wing_module.build_potius_wet_wing(origin=(11.0, 4.0, 2.7), show_roof=False)

print("Modular Site Build Complete.")