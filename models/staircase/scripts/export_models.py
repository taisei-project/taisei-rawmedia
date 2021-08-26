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

    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        if mod.name.startswith('apply'):
            print('{}: apply {}'.format(obj.name,mod.name))
            bpy.ops.object.modifier_apply(modifier=mod.name)

purge_unused(bpy.data.meshes)

arcs = bpy.data.objects['arcs']
wall = bpy.data.objects['wall']
stairs = bpy.data.objects['stairs']
arcs_metal = bpy.data.objects['arcs_metal']
stairs_metal = bpy.data.objects['stairs_metal']
envmap_light = bpy.data.objects['envmapLight']
bpy.ops.object.select_all(action='DESELECT')

# Disable environment map lighting
envmap_light.data.energy = 0

arcs.select_set(True)
wall.select_set(True)
bpy.context.view_layer.objects.active = wall
bpy.ops.object.join()
cleanup_mesh()
bpy.ops.object.select_all(action='DESELECT')

arcs_metal.select_set(True)
stairs_metal.select_set(True)
bpy.context.view_layer.objects.active = stairs_metal
bpy.ops.object.join()
cleanup_mesh()
bpy.ops.object.select_all(action='DESELECT')
stairs_metal.name = 'metal'

models = {
    'wall': wall,
    'stairs': stairs,
    'metal': stairs_metal,
}

for _, obj in models.items():
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    if obj is stairs:
        bpy.ops.uv.smart_project(island_margin=0.002)
    else:
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.002)
    bpy.ops.uv.pack_islands(rotate=True, margin=0.002)
    bpy.ops.object.editmode_toggle()

bpy.ops.object.select_all(action='DESELECT')

for name, obj in models.items():
    obj.select_set(True)
    export_obj('models/{}.iqm'.format(name))
    obj.select_set(False)

# Baseline resolution
q = 4096

def makesize(q):
    return {
        'ao': q >> 1,
        'default': q,
    }

bake_objects(
    {
        'object': wall,
        'size': makesize(q >> 0),
        'margin' : {
            #'roughness': q,
        },
    },
    {
        'object': stairs,
        'size': makesize(q >> 0),
        'margin' : {
            #'roughness': q,
        },
    },
    {
        'object': stairs_metal,
        'size': makesize(q >> 0),
        'exclude_passes': {'ambient', 'diffuse', 'normal'},
    },
)

bpy.ops.wm.quit_blender()
