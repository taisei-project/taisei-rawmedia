import bpy

def export_obj(filepath):
    bpy.ops.export_scene.obj(
        filepath=filepath,
        axis_forward='-Y',
        axis_up='-Z',
        use_triangles=True,
        use_blen_objects=True,
        use_materials=False,
        use_selection=True,
    )

bpy.ops.object.mode_set(mode='OBJECT')


# join rocks and trees into one object and bake
bpy.ops.object.select_all(action='DESELECT')
rock_coll = bpy.data.collections['rocks']
for rock in rock_coll.all_objects:
    rock.select_set(True)
tree_coll = bpy.data.collections['trees']
for tree in tree_coll.all_objects:
    tree.select_set(True)

bpy.context.view_layer.objects.active = rock_coll.all_objects[0]

bpy.ops.object.join()

bpy.ops.uv.smart_project(island_margin=0.03)
bpy.ops.object.bake(type='COMBINED')
export_obj('objs/rocks.obj')

# bake the ground texture
bpy.ops.object.select_all(action='DESELECT')
ground = bpy.data.objects['ground']
ground.select_set(True)
ground.data.uv_layers['bake'].active = True
bpy.ops.object.bake(type='COMBINED')
export_obj('objs/ground.obj')

# bake the leaves texture
bpy.ops.object.select_all(action='DESELECT')
leaves = bpy.data.objects['leaves']
leaves.select_set(True)
leaves.data.uv_layers['bake'].active = True
bpy.ops.object.bake(type='COMBINED')
export_obj('objs/leaves.obj')

# bake alpha map of the leaves texture
bpy.ops.object.select_all(action='DESELECT')
leaves_alpha = bpy.data.objects['leaves_alpha']
leaves_alpha.select_set(True)
bpy.ops.object.bake(type='EMIT')


# save all generated textures
bpy.data.images['rocks'].save()
bpy.data.images['ground_baked'].save()
bpy.data.images['leaves_baked'].save()
bpy.data.images['leaves_alpha'].save()
