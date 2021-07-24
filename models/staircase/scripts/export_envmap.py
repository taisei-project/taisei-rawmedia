import bpy

import sys
sys.path.append('../utils')
from export_utils import *

print('Rendering environment map…')
bpy.context.scene.render.filepath = '//textures/envmap.png'
bpy.ops.render.render(write_still=True)

bpy.ops.wm.quit_blender()
