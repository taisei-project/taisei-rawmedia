import bpy

import sys
sys.path.append('../utils')
from export_utils import *


bpy.ops.object.mode_set(mode='OBJECT')

obj_rocks = bpy.data.objects['rocks']
obj_ground = bpy.data.objects['ground']
obj_grass = bpy.data.objects['grass']

objs = (obj_rocks, obj_ground, obj_grass)

bpy.ops.object.select_all(action='DESELECT')
for obj in objs:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    export_obj(f'models/{obj.name}.iqm')
    obj.select_set(False)

# Baseline resolution
q = 2048

bake_objects(
    {
        'object': (obj_ground, obj_grass),
        'output_name': 'ground',
        'size': q,
    },
    {
        'object': obj_rocks,
        'size': q,
    },
)

bpy.ops.wm.quit_blender()
