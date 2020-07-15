import bpy
import os
import shutil

def export_obj(filepath):
    bpy.ops.export.iqm(
        filepath=filepath,
        usemesh=True,
        usemods=False,
        useskel=False,
        usebbox=False,
        usecol=False
    )
    
def save_image(img, suffix): # 10/10 best api
    img.save()
    path,ext = os.path.splitext(img.filepath[2:])
    shutil.copy(img.filepath[2:], path+suffix+ext)

def bake(name, type, baketex_names, pass_filter=None):
    print('baking {}'.format(type))
    if pass_filter != None:
        bpy.ops.object.bake(type=type, pass_filter=pass_filter)
    else:
        bpy.ops.object.bake(type=type)

    suffix = '_'+name

    for texname in baketex_names:
        save_image(bpy.data.images[texname], suffix)
