import bpy

import sys
sys.path.append('../utils')
from export_utils import *
import math as m

bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='SELECT')
objs = list()
for obj in bpy.context.selected_objects:
    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        if mod.name.startswith('apply'):
            print('{}: apply {}'.format(obj.name,mod.name))
            bpy.ops.object.modifier_apply(modifier=mod.name)

tower = bpy.data.objects['tower']
metal_rings = bpy.data.objects['metal_rings']
metal_columns = bpy.data.objects['metal_columns']
bpy.ops.object.select_all(action='DESELECT')

metal_columns.select_set(True)
metal_rings.select_set(True)
bpy.context.view_layer.objects.active = metal_columns
bpy.ops.object.join()
bpy.ops.object.select_all(action='DESELECT')


models = {
    'tower': tower,
}

mirror_models = {
    'metal_columns': metal_columns,
}

for _, obj in models.items():
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.003)
    bpy.ops.object.editmode_toggle()
    
bpy.ops.object.select_all(action='DESELECT')
baketex_names = [name + '_baked' for name in models.keys()]

for _, obj in models.items():
    obj.select_set(True)
bake('normal','NORMAL', baketex_names=baketex_names)
bake('roughness','ROUGHNESS', baketex_names=baketex_names)
bake('ambient','COMBINED', baketex_names=baketex_names)
bake('diffuse','DIFFUSE',pass_filter={'COLOR'}, baketex_names=baketex_names)
bpy.ops.object.select_all(action='DESELECT')

for name, obj in {**models, **mirror_models}.items():
    obj.select_set(True) 
    export_obj('models/{}.iqm'.format(name))
    obj.select_set(False)

bpy.ops.wm.quit_blender()
