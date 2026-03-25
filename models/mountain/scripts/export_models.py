import bpy

import sys
sys.path.append('../utils')
from export_utils import *

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.material_slot_remove_unused()

for obj in bpy.context.selected_objects:
    if obj.data is not None:
        obj.data = obj.data.copy()

bpy.ops.object.select_all(action='DESELECT')
purge_unused(bpy.data.meshes)

# join rocks into one object and bake
bpy.ops.object.select_all(action='DESELECT')
rock_coll = bpy.data.collections['rocks']
for rock in rock_coll.all_objects:
    rock.select_set(True)
bpy.context.view_layer.objects.active = rock
bpy.ops.object.join()
rock.name = 'rocks'

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(island_margin=0.02)
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

#join trees
bpy.ops.object.select_all(action='DESELECT')
tree_coll = bpy.data.collections['trees']
for tree in tree_coll.all_objects:
    tree.select_set(True)
bpy.context.view_layer.objects.active = tree
bpy.ops.object.join()
tree.name = 'trees'

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(island_margin=0.02)
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

ground = bpy.data.objects['ground']
ground.data.uv_layers['bake'].active = True
leaves = bpy.data.objects['leaves']
leaves.data.uv_layers['bake'].active = True

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


# Baseline resolution
q = 4096

def makesize(q):
    return {
        'ao': q >> 1,
        'default': q,
    }


bake_objects(
    # {
    #     'object': ground,
    #     'size': makesize(q),
    # },
    # {
    #     'object': leaves,
    #     'size': makesize(q),
    # },
    # {
    #     'object': rock,
    #     'size': makesize(q),
    #     'margin' : {
    #         'roughness': q,
    #     },
    # },
    {
        'object': tree,
        'size': makesize(q),
    },
)

bpy.ops.wm.quit_blender()
