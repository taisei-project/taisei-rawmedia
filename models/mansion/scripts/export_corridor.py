import bpy

import sys
sys.path.append('../utils')
from export_utils import *

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')

corridor_col = bpy.data.collections['corridor']

for o in corridor_col.all_objects:
    o.select_set(True)

export_obj('models/corridor.iqm')

bake_objects(
    {
        'object': corridor_col,
        'size': 2048,
        'exclude_passes': {'ao'},
    },
    normal_samples=64
)

bpy.ops.wm.quit_blender()
