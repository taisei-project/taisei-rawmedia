import bpy

import itertools
import sys
sys.path.append('../utils')
from export_utils import *

bpy.ops.object.mode_set(mode='OBJECT')

col_ground = bpy.data.collections['ground']
col_mansion = bpy.data.collections['mansion']
col_roof = bpy.data.collections['roof']

cols_mansion = (col_mansion, col_roof)
cols_all = (col_mansion, col_roof, col_ground)

for obj in itertools.chain(*(c.all_objects for c in cols_all)):
    obj.select_set(True)

for obj in bpy.context.selected_objects:
    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        if mod.name.startswith('apply'):
            print('{}: apply {}'.format(obj.name, mod.name))
            bpy.ops.object.modifier_apply(modifier=mod.name)

bpy.ops.object.select_all(action='DESELECT')
for obj in itertools.chain(*(c.all_objects for c in cols_mansion)):
    obj.select_set(True)
export_obj('models/mansion.iqm')

bpy.ops.object.select_all(action='DESELECT')
for obj in col_ground.all_objects:
   obj.select_set(True)
export_obj('models/ground.iqm')

# Baseline resolution
q = 4096

bake_objects(
    {
        'object': col_ground,
        'size': q,
        'exclude_passes': {'ao'},
    },
    {
        'object': cols_mansion,
        'output_name': 'mansion',
        'size': q,
        'exclude_passes': {'ao'},
    },
)

bpy.ops.wm.quit_blender()
