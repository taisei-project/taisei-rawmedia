import bpy

import sys
sys.path.append('../utils')
from export_utils import *

bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.collections['ground'].all_objects:
    obj.select_set(True)
for obj in bpy.data.collections['mansion'].all_objects:
    obj.select_set(True)
for obj in bpy.data.collections['roof'].all_objects:
    obj.select_set(True)


baketex_names = [
    'mansion_baked',
    'ground_baked',
]

bake('normal','NORMAL', baketex_names=baketex_names)
bake('roughness','ROUGHNESS', baketex_names=baketex_names)
bake('ambient','COMBINED', baketex_names=baketex_names)
bake('diffuse','DIFFUSE',pass_filter={'COLOR'}, baketex_names=baketex_names)


bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.collections['ground'].all_objects:
    obj.select_set(True)

export_obj('models/ground.iqm')

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.collections['mansion'].all_objects:
    obj.select_set(True)
for obj in bpy.data.collections['roof'].all_objects:
    obj.select_set(True)

export_obj('models/mansion.iqm')

bpy.ops.wm.quit_blender()
