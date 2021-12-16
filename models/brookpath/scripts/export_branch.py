import bpy

import sys
sys.path.append('../utils')
from export_utils import *


bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')

obj_branch = bpy.data.objects['branch']
obj_leaves = bpy.data.objects['leaves']

obj_branch.select_set(True)
export_obj('models/branch.iqm')
obj_branch.select_set(False)

obj_leaves.select_set(True)
export_obj('models/leaves.iqm')
obj_leaves.select_set(False)

# Baseline resolution
q = 2048

bake_objects(
    {
        'object': obj_branch,
        'size': q,
        'exclude_passes': {'roughness'},
    },
    {
        'object': obj_leaves,
        'size': q,
        'exclude_passes': {'roughness'},
    },
)

bpy.ops.wm.quit_blender()
