import bpy

bpy.context.scene.render.filepath = 'textures/sky.hdr'
bpy.ops.render.render(write_still=True)
