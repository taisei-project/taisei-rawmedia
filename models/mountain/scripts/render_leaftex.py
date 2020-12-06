import bpy

bpy.context.scene.render.filepath = 'textures/leaf.png'
bpy.ops.render.render(write_still=True)
