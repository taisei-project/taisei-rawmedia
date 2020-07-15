import bpy

import sys
sys.path.append('../utils')
from export_utils import *

bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')

bpy.data.objects['corridor'].select_set(True)

baketex_names = [
    'corridor_baked',
]

bake('normal','NORMAL', baketex_names=baketex_names)
bake('roughness','ROUGHNESS', baketex_names=baketex_names)
bake('ambient','COMBINED', baketex_names=baketex_names)
bake('diffuse','DIFFUSE',pass_filter={'COLOR'}, baketex_names=baketex_names)

export_obj('models/corridor.iqm')

bpy.ops.wm.quit_blender()
