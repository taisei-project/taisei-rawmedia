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
tower_bottom = bpy.data.objects['tower_bottom']
spire_bottom = bpy.data.objects['spire_bottom']
spire = bpy.data.objects['spire']
rim = bpy.data.objects['rim']
stairs = bpy.data.objects['stairs']
top_plate = bpy.data.objects['top_plate']
rim_plate= bpy.data.objects['rim_plate']
spire_spike = bpy.data.objects['spire_spike']
bpy.ops.object.select_all(action='DESELECT')

rim.select_set(True)
spire.select_set(True)
bpy.context.view_layer.objects.active = rim
bpy.ops.object.join()
rim.rotation_euler = (0, 0, 2*m.pi/12)
bpy.ops.object.select_all(action='DESELECT')


tower_bottom.select_set(True)
spire_bottom.select_set(True)
bpy.context.view_layer.objects.active = tower_bottom
bpy.ops.object.join()
tower_bottom.rotation_euler = (0, 0, 2*m.pi/12)
bpy.ops.object.select_all(action='DESELECT')


spire_spike.select_set(True)
spire_spike.rotation_euler = (0, 0, 2*m.pi/12)
bpy.ops.object.select_all(action='DESELECT')

rim_plate.select_set(True)
top_plate.select_set(True)
bpy.context.view_layer.objects.active = top_plate
bpy.ops.object.join()


models = {
    'rim': rim,
    'stairs': stairs,
    'tower': tower,
    'tower_bottom': tower_bottom,
    'spires': spire_spike,
}

mirror_models = {
    'top_plate': top_plate,
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

set_metallic('steps',0)
set_metallic('stair_holders',0)
bake('diffuse','DIFFUSE',pass_filter={'COLOR'}, baketex_names=baketex_names)
bpy.ops.object.select_all(action='DESELECT')

for name, obj in {**models, **mirror_models}.items():
    obj.select_set(True) 
    export_obj('models/{}.iqm'.format(name))
    obj.select_set(False)

bpy.ops.wm.quit_blender()
