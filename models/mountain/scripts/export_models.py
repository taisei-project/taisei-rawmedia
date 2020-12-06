import bpy

import sys
sys.path.append('../utils')
from export_utils import *


bpy.ops.object.mode_set(mode='OBJECT')


# join rocks into one object and bake
bpy.ops.object.select_all(action='DESELECT')
rock_coll = bpy.data.collections['rocks']
for rock in rock_coll.all_objects:
    rock.select_set(True)

bpy.context.view_layer.objects.active = rock

bpy.ops.object.join()

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.uv.smart_project(island_margin=0.03)
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')
#join trees
tree_coll = bpy.data.collections['trees']
for tree in tree_coll.all_objects:
    tree.select_set(True)
bpy.context.view_layer.objects.active = tree
bpy.ops.object.join()

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.uv.smart_project(island_margin=0.03)
bpy.ops.object.mode_set(mode='OBJECT')

ground = bpy.data.objects['ground']
ground.data.uv_layers['bake'].active = True
leaves = bpy.data.objects['leaves']
leaves.data.uv_layers['bake'].active = True

ground.select_set(True)
tree.select_set(True)
rock.select_set(True)
leaves.select_set(True)

baketex_names = [
    'leaves_baked',
    'ground_baked',
    'rocks_baked',
    'trees_baked',
]

bake('normal','NORMAL', baketex_names=baketex_names)
bake('roughness','ROUGHNESS', baketex_names=baketex_names)
bake('ambient','COMBINED', baketex_names=baketex_names)
bake('diffuse','DIFFUSE',pass_filter={'COLOR'}, baketex_names=baketex_names)

bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['leaves_alpha'].select_set(True)
bake('','EMIT', baketex_names=['leaves_alpha'])

bpy.ops.object.select_all(action='DESELECT')
rock.select_set(True)
export_obj('models/rocks.iqm')

bpy.ops.object.select_all(action='DESELECT')
tree.select_set(True)
export_obj('models/trees.iqm')

bpy.ops.object.select_all(action='DESELECT')
ground.select_set(True)
export_obj('models/ground.iqm')

bpy.ops.object.select_all(action='DESELECT')
leaves.select_set(True)
export_obj('models/leaves.iqm')


# save all generated textures
bpy.data.images['rocks_baked'].save()
bpy.data.images['trees_baked'].save()
bpy.data.images['ground_baked'].save()
bpy.data.images['leaves_baked'].save()
bpy.data.images['leaves_alpha'].save()

bpy.ops.wm.quit_blender()
