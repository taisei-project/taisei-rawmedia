import bpy

import sys
sys.path.append('../utils')
from export_utils import *


bpy.ops.object.mode_set(mode='OBJECT')

obj = bpy.data.objects['quintic']

bpy.context.view_layer.objects.active = obj
for mod in obj.modifiers:
    bpy.ops.object.modifier_apply(modifier=mod.name)
obj.select_set(True) 
export_obj('models/calabi-yau-quintic.iqm')

bpy.ops.wm.quit_blender()
