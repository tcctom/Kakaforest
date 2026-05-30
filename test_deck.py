import bpy  # type: ignore
import sys
import os
from importlib import reload

# Add current directory to sys.path so Blender can find your modules
dir = os.path.dirname(bpy.data.filepath)
if dir not in sys.path:
    sys.path.append(dir)

import main_dwelling_module
import materials
import utils

# Reload modules
reload(materials)
reload(utils)
reload(main_dwelling_module)

def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear materials to force recreation with textures
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

cleanup()

# Build the deck independently for testing
# You can also build it with the main dwelling by running main_site_plan.py
main_dwelling_module.build_north_deck(origin=(0, 0, 0))

print("North deck test completed!")
