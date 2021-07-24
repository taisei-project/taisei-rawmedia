import bpy

import sys
sys.path.append('../utils')
from export_utils import *

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')

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
bpy.ops.object.select_all(action='DESELECT')

arcs_metal.select_set(True)
stairs_metal.select_set(True)
bpy.context.view_layer.objects.active = stairs_metal
bpy.ops.object.join()
bpy.ops.object.select_all(action='DESELECT')

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
    #bpy.ops.uv.smart_project(island_margin=0.003)
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.003)
    #bpy.ops.uv.pack_islands(rotate=True, margin=0.001)
    #bpy.ops.uv.lightmap_pack(PREF_IMG_PX_SIZE=2048, PREF_MARGIN_DIV=0.1)
    bpy.ops.object.editmode_toggle()

bpy.ops.object.select_all(action='DESELECT')
baketex_names = [name + '_baked' for name in models.keys()]

for _, obj in models.items():
    obj.select_set(True)

'''
bake('ambient','COMBINED', baketex_names=baketex_names)
bake('normal','NORMAL', baketex_names=baketex_names)
bake('roughness','ROUGHNESS', baketex_names=baketex_names)
set_metallic('metal', 0)
bake('diffuse','DIFFUSE',pass_filter={'COLOR'}, baketex_names=baketex_names)
prepare_depth_bake()
bake('depth', 'ROUGHNESS', baketex_names=baketex_names)
'''
bpy.ops.object.select_all(action='DESELECT')

for name, obj in models.items():
    obj.select_set(True) 
    export_obj('models/{}.iqm'.format(name))
    obj.select_set(False)

bpy.ops.wm.quit_blender()
