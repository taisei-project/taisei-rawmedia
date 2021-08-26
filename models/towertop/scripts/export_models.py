import bpy

import sys
sys.path.append('../utils')
from export_utils import *
import math as m

for obj in bpy.data.objects:
    obj.hide_set(False)

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.material_slot_remove_unused()

bpy.ops.object.select_all(action='SELECT')
for obj in bpy.context.selected_objects:
    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        if mod.name.startswith('apply'):
            print('{}: apply {}'.format(obj.name, mod.name))
            bpy.ops.object.modifier_apply(modifier=mod.name)

tower = bpy.data.objects['tower']
tower_bottom = bpy.data.objects['tower_bottom']
pillars_bottom = bpy.data.objects['pillars_bottom']
pillars = bpy.data.objects['pillars']
rim = bpy.data.objects['rim']
stairs = bpy.data.objects['stairs']
top_plate = bpy.data.objects['top_plate']
rim_plate= bpy.data.objects['rim_plate']
spires = bpy.data.objects['spires']
bpy.ops.object.select_all(action='DESELECT')

rim.select_set(True)
pillars.select_set(True)
bpy.context.view_layer.objects.active = rim
bpy.ops.object.join()
cleanup_mesh()
rim.rotation_euler = (0, 0, 2*m.pi/12)
bpy.ops.object.select_all(action='DESELECT')

tower_bottom.select_set(True)
pillars_bottom.select_set(True)
bpy.context.view_layer.objects.active = tower_bottom
bpy.ops.object.join()
cleanup_mesh()
tower_bottom.rotation_euler = (0, 0, 2*m.pi/12)
bpy.ops.object.select_all(action='DESELECT')

spires.select_set(True)
spires.rotation_euler = (0, 0, 2*m.pi/12)
bpy.ops.object.select_all(action='DESELECT')

rim_plate.select_set(True)
rim_plate.rotation_euler = (0, 0, 2*m.pi/12)
top_plate.select_set(True)
bpy.context.view_layer.objects.active = top_plate
bpy.ops.object.join()
cleanup_mesh()
top_plate.name = 'floor'

models = {
    'rim': rim,
    'stairs': stairs,
    'tower': tower,
    'tower_bottom': tower_bottom,
    'spires': spires,
}

static_uv_models = {
    'floor': top_plate,
}

for obj in models.values():
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.002)
    if False:
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.pack_islands(rotate=True, margin=0.002)
        bpy.ops.uv.select_all(action='DESELECT')
    bpy.ops.object.editmode_toggle()

bpy.ops.object.select_all(action='DESELECT')

models.update(static_uv_models)

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

# NOTE: Additional downsampling is done when encoding to Basis (see makefile)
# This gives vastly superior results over just baking at low resolution

bake_objects(
    {
        'object': top_plate,
        'size': makesize(q >> 1),
        'exclude_passes': {'ambient', 'diffuse', 'roughness'},
    },
    {
        'object': rim,
        'size': makesize(q >> 0),
        'margin' : {
            'roughness': q,
        },
    },
    {
        'object': spires,
        'size': {
            'roughness': q >> 2,
            'default': q >> 1,
        },
        'margin' : {
            'roughness': q,
        },
        'exclude_passes': {'ambient', 'diffuse'},
    },
    {
        'object': stairs,
        'size': makesize(q >> 1),
        'margin' : {
            ('diffuse', 'roughness'): q,
        },
    },
    {
        'object': tower,
        'size': makesize(q >> 0),
        'margin' : {
            'roughness': q,
        },
    },
    {
        'object': tower_bottom,
        'size': makesize(q >> 1),
        'margin' : {
            'roughness': q,
        },
    },
)

bpy.ops.wm.quit_blender()
