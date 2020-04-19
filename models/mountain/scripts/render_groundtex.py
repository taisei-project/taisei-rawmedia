import bpy

bpy.context.scene.render.filepath = 'textures/ground.png'
bpy.ops.render.render(write_still=True)
