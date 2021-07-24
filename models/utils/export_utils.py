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
    src = img.filepath[2:]
    path, ext = os.path.splitext(src)
    dst = path + suffix + ext
    shutil.copy(src, dst)
    print(src, '->', dst)

def bake(name, type, baketex_names, pass_filter=None):
    colorspace = {
        'DIFFUSE'  : 'sRGB',
        'COMBINED' : 'sRGB',
    }.get(type, 'Non-Color')

    print(f'baking {type} as {name}, colorspace: {colorspace}, pass_filter={pass_filter}')

    for texname in baketex_names:
        bpy.data.images[texname].colorspace_settings.name = colorspace

    if pass_filter is not None:
        bpy.ops.object.bake(type=type, pass_filter=pass_filter)
    else:
        bpy.ops.object.bake(type=type)

    suffix = '_'+name

    for texname in baketex_names:
        save_image(bpy.data.images[texname], suffix)

def set_metallic(material, value):
    mat = bpy.data.materials[material]
    principled = mat.node_tree.nodes.get('Principled BSDF')
    principled.inputs['Metallic'].default_value = value

def get_input_link(node, input_name):
    socket = node.inputs[input_name]

    try:
        link = socket.links[0]
    except IndexError:
        return

    return link

def link_nodes(mat, left_node, left_output, right_node, right_input):
    o = left_node.outputs[left_output]
    i = right_node.inputs[right_input]
    mat.node_tree.links.new(o, i)

def find_node_by_label(node_tree, label):
    for node in node_tree.nodes:
        if node.label == label:
            return node

def prepare_depth_bake():
    print('Preparing materials for depth map baking…')
    materials = bpy.data.materials
    for mat in filter(lambda m: m.node_tree, materials):
        out = mat.node_tree.nodes['Material Output']
        bsdf = out.inputs['Surface'].links[0].from_node
        assert isinstance(bsdf, bpy.types.ShaderNodeBsdfPrincipled)

        roughness_input = bsdf.inputs['Roughness']
        roughness_input.default_value = 0.0

        depth = find_node_by_label(mat.node_tree, 'Depth Map')

        if depth is None:
            print(f' - {mat.name} skipped: no Depth Map node')
            for link in roughness_input.links:
                mat.node_tree.links.remove(link)
            continue

        mat.node_tree.links.new(roughness_input, depth.outputs['Depth'])
        print(f' * {mat.name}')

def purge_unused(collection):
    for obj in collection:
        if not obj.users:
            print(f'Purging unused object {obj}')
            collection.remove(obj)
