import bpy

import sys
sys.path.append('../utils')
from export_utils import *


bpy.ops.object.mode_set(mode='OBJECT')


bpy.ops.object.select_all(action='SELECT')
for obj in bpy.context.selected_objects:
    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=mod.name)


bpy.ops.object.select_all(action='DESELECT')

rocks = bpy.data.objects['rocks']
ground = bpy.data.objects['ground']
grass = bpy.data.objects['grass']

rocks.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(island_margin=0.03)
bpy.ops.object.mode_set(mode='OBJECT')
ground.select_set(True)

#ground = bpy.data.objects['ground']
#ground.data.uv_layers['bake'].active = True
#leaves = bpy.data.objects['leaves']
#leaves.data.uv_layers['bake'].active = True

baketex_names = [
    'rocks_baked',
    'ground_baked',
]

bake('normal','NORMAL', baketex_names=baketex_names)
bake('roughness','ROUGHNESS', baketex_names=baketex_names)
bake('ambient','COMBINED', baketex_names=baketex_names)
bake('diffuse','DIFFUSE',pass_filter={'COLOR'}, baketex_names=baketex_names)


bpy.ops.object.select_all(action='DESELECT')
rocks.select_set(True)
export_obj('models/rocks.iqm')

bpy.ops.object.select_all(action='DESELECT')
ground.select_set(True)
export_obj('models/ground.iqm')

bpy.ops.object.select_all(action='DESELECT')
grass.select_set(True)
export_obj('models/grass.iqm')


#for tex in baketex_names:
#    # save all generated textures
#    bpy.data.images[tex].save()

bpy.ops.wm.quit_blender()
