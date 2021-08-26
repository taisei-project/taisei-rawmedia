
import bpy
import bpy_types

import os
import shutil
import contextlib
import dataclasses
import datetime
import collections
from collections.abc import Callable

def cleanup_mesh():
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.editmode_toggle()

def export_obj(filepath):
    bpy.ops.export.iqm(
        filepath=filepath,
        usemesh=True,
        usemods=False,
        useskel=False,
        usebbox=False,
        usecol=False
    )

class PerPassBakeSetting:
    def __init__(self, setting_name, value_or_mapping, default_value=None):
        if isinstance(value_or_mapping, collections.abc.Mapping):
            self.mapping = {}

            def insert(pass_name, val):
                if not isinstance(pass_name, str):
                    raise TypeError(
                        f'{setting_name}: Keys must be strings or tuples/sets of strings')

                if pass_name in self.mapping:
                    raise ValueError(
                        f'{setting_name}: Multiple values specified for pass `{pass_name}`')

                self.mapping[pass_name] = self._process_value(val)

            for key, value in value_or_mapping.items():
                if isinstance(key, str):
                    insert(key, value)
                else:
                    for pass_name in key:
                        insert(pass_name, value)

            if default_value is not None and 'default' not in self.mapping:
                insert('default', default_value)

            self.const_value = None
        else:
            self.const_value = self._process_value(value_or_mapping)
            self.mapping = None

    @staticmethod
    def _process_value(value):
        return value

    def get_value(self, bake_pass):
        if self.mapping is None:
            return self.const_value

        try:
            return self.mapping[bake_pass.name]
        except KeyError:
            return self.mapping['default']

class PerPassBakeIntSetting(PerPassBakeSetting):
    @staticmethod
    def _process_value(value):
        return int(value)

class PerPassBakeSizeSetting(PerPassBakeSetting):
    @staticmethod
    def _process_value(value):
        try:
            w, h = value
        except TypeError:
            w, h = value, value

        return int(w), int(h)

class BakeConfig:
    DEFAULT_SIZE = 2048
    DEFAULT_MARGIN = 16

    def __init__(self, object,
                 size=DEFAULT_SIZE, alpha=False, exclude_passes=None, margin=DEFAULT_MARGIN):
        if isinstance(object, str):
            object = bpy.data.objects[object]

        self.obj = object
        self.size = PerPassBakeSizeSetting('size', size, self.DEFAULT_SIZE)
        self.margin = PerPassBakeIntSetting('margin', margin, self.DEFAULT_MARGIN)
        self.alpha = alpha

        if exclude_passes is None:
            self.exclude_passes = set()
        else:
            self.exclude_passes = {
                (bake_passes[p] if isinstance(p, str) else p) for p in exclude_passes
            }

def create_bake_output_image(
    obj, bake_pass, size, alpha=False, format='PNG'):
    name = f'bake.{obj.name}.{bake_pass.name}'
    w, h = size

    img = bpy.data.images.new(name, w, h, alpha=alpha and bake_pass.may_have_alpha)
    img.file_format = format
    img.colorspace_settings.name = bake_pass.colorspace
    img.colorspace_settings.is_data = (bake_pass.colorspace == 'Non-Color')
    img.filepath_raw = f'//textures/baked/{obj.name}_{bake_pass.name}.png'

    return img

def get_material_output_node(m):
    if not m.use_nodes or not m.node_tree:
        return None

    # FIXME: there may be multiple output nodes, or the node
    # may be named something like 'Material Output.001' after
    # some copypaste freak accident. Maybe we should deal with
    # that here (with a warning).
    try:
        return m.node_tree.nodes['Material Output']
    except KeyError:
        return None

def object_uses_one_of_materials(obj, mats):
    for mat in mats:
        if mat in obj.data.materials.values():
            return True
    return False

def prepare_depth_bake(configs, mats):
    print('Preparing materials for depth map bake…')

    enabled_mats = set()

    for mat in mats:
        out = get_material_output_node(mat)
        bsdf = out.inputs['Surface'].links[0].from_node
        assert isinstance(bsdf, bpy.types.ShaderNodeBsdfPrincipled)

        roughness_input = bsdf.inputs['Roughness']
        roughness_input.default_value = 0.0

        depth = find_node_by_label(mat.node_tree, 'Depth Map')

        if depth is None:
            for link in roughness_input.links:
                mat.node_tree.links.remove(link)
            print(f' - {mat.name}: set roughness to 0')
        else:
            mat.node_tree.links.new(roughness_input, depth.outputs['Depth'])
            print(f' * {mat.name}: link depth map to roughness')
            enabled_mats.add(mat)

    for cfg in tuple(configs):
        obj = cfg.obj
        if not object_uses_one_of_materials(obj, enabled_mats):
            print(f"Object `{obj.name}` skipped: no materials have a depth map")
            configs.remove(cfg)

def prepare_diffuse_bake(configs, mats):
    print('Preparing materials for diffuse map bake…')

    for mat in mats:
        out = get_material_output_node(mat)
        bsdf = out.inputs['Surface'].links[0].from_node
        assert isinstance(bsdf, bpy.types.ShaderNodeBsdfPrincipled)

        metallic_input = bsdf.inputs['Metallic']
        metallic_input.default_value = 0.0

        for link in metallic_input.links:
            mat.node_tree.links.remove(link)

        print(f' * {mat.name}: set metallic to 0')

@dataclasses.dataclass
class BakePass:
    name: str = None
    blender_name: str = None
    blender_pass_filter: set[str] = None
    colorspace: str = 'Non-Color'
    samples: int = 0
    may_have_alpha: bool = False
    prepare: Callable[[set, set], None] = dataclasses.field(
        default_factory=lambda: lambda configs, mats: None, repr=False)

    def __hash__(self):
        return id(self)

bake_passes = collections.OrderedDict((
    # NOTE: order matters. prepare functions have side effects!

    ('ambient',     BakePass('ambient',     'COMBINED',     None,       'sRGB')),
    ('ao',          BakePass('ao',          'AO',           None)),
    ('normal',      BakePass('normal',      'NORMAL',       None, samples=1)),
    ('roughness',   BakePass('roughness',   'ROUGHNESS',    None, samples=1, may_have_alpha=True)),
    ('diffuse',     BakePass('diffuse',     'DIFFUSE',      {'COLOR'},  'sRGB',
                             samples=1, prepare=prepare_diffuse_bake)),
    ('depth',       BakePass('depth',       'ROUGHNESS',    None,
                             samples=1, prepare=prepare_depth_bake)),
))

class BakeError(RuntimeError):
    pass

def bake_objects_pass(configs, bake_pass, samples=0, max_samples=0):
    objects_str = ', '.join(c.obj.name for c in configs)
    print(f"Preparing to bake {bake_pass.name} pass for objects: {objects_str}")

    bpy.ops.object.select_all(action='DESELECT')

    mats = set()
    cfgs = set()

    for cfg in configs:
        obj = cfg.obj

        def skip(reason, obj=obj):
            print(f"Object `{obj.name}` skipped: {reason}")

        if bake_pass in cfg.exclude_passes:
            skip("pass excluded")
            continue

        if not isinstance(obj.data, bpy_types.Mesh):
            skip("object is not a mesh")
            continue

        for mat in obj.data.materials:
            if not get_material_output_node(mat):
                raise BakeError(f'Material `{mat.name}` used by object `{obj.name}` '
                                 'has no output node')
            mats.add(mat)

        cfgs.add(cfg)

    if not cfgs:
        print(f'[{bake_pass.name}] Bake pass aborted: no suitable objects')
        return

    bake_pass.prepare(cfgs, mats)

    # prepare may remove cfgs
    if not cfgs:
        print(f'[{bake_pass.name}] Bake pass aborted: no suitable objects')
        return

    if samples == 0:
        samples = bake_pass.samples

    if samples == 0:
        samples = bpy.context.scene.cycles.samples

    if max_samples == 0:
        max_samples = bpy.context.scene.cycles.samples

    samples = min(samples, max_samples)
    assert samples > 0

    print(f'\n[{bake_pass.name}] Baking {bake_pass.blender_name}, {samples} samples, '
          f'colorspace: {bake_pass.colorspace}, pass filter: {bake_pass.blender_pass_filter}')

    t_begin = datetime.datetime.now()

    for cfg in cfgs:
        t_obj_begin = datetime.datetime.now()
        cfg.obj.select_set(True)

        sz = cfg.size.get_value(bake_pass)
        img = create_bake_output_image(cfg.obj, bake_pass, sz, alpha=cfg.alpha)

        print(
            f'[{bake_pass.name}] Baking object `{cfg.obj.name}` to '
            f'`{img.filepath_raw}`, {sz[0]}x{sz[1]}')

        junknodes = set()

        for mat in cfg.obj.data.materials:
            node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            node.image = img
            mat.node_tree.nodes.active = node
            junknodes.add((mat.node_tree.nodes, node))

        bake_args = {
            'normal_space': 'TANGENT',
            'type': bake_pass.blender_name,
            'margin': cfg.margin.get_value(bake_pass),
        }

        if bake_pass.blender_pass_filter is not None:
            bake_args['pass_filter'] = bake_pass.blender_pass_filter

        with cycles_samples(samples):
            bpy.ops.object.bake(**bake_args)

        img.save()
        bpy.data.images.remove(img)

        for nodeset, node in junknodes:
            nodeset.remove(node)

        cfg.obj.select_set(False)

        t_obj_end = datetime.datetime.now()
        print(f'[{bake_pass.name}] Object bake finished in {str(t_obj_end - t_obj_begin)}')

    t_end = datetime.datetime.now()
    print(f'[{bake_pass.name}] Bake pass finished in {str(t_end - t_begin)}')

def bake_objects(*configs, passes=None, samples=0, max_samples=0):
    if passes is None:
        passes = tuple(bake_passes.values())
    else:
        passes = [(bake_passes[p] if isinstance(p, str) else p) for p in passes]

    t_begin = datetime.datetime.now()

    configs = tuple(
        (cfg if isinstance(cfg, BakeConfig) else BakeConfig(**cfg))
        for cfg in configs
    )

    for bpass in passes:
        bake_objects_pass(
            configs=configs,
            bake_pass=bpass,
            samples=samples,
            max_samples=max_samples)

    t_end = datetime.datetime.now()

    print(f'All bake passes finished in {str(t_end - t_begin)}')

def find_node_by_label(node_tree, label):
    for node in node_tree.nodes:
        if node.label == label:
            return node

def purge_unused(collection):
    for obj in collection:
        if not obj.users:
            print(f'Purging unused object {obj}')
            collection.remove(obj)

@contextlib.contextmanager
def cycles_samples(num):
    prev = bpy.context.scene.cycles.samples
    bpy.context.scene.cycles.samples = num
    try:
        yield
    finally:
        bpy.context.scene.cycles.samples = prev


'''
OLD SHIT DO NOT USE
'''

def save_image(img, suffix): # 10/10 best api
    img.save()
    src = img.filepath[2:]
    path, ext = os.path.splitext(src)
    dst = path + suffix + ext
    shutil.copy(src, dst)
    print(src, '->', dst)

def set_active_images(names):
    for mat in bpy.data.materials:
        if mat.node_tree is None:
            continue

        for node in mat.node_tree.nodes:
            if isinstance(node, bpy.types.ShaderNodeTexImage):
                node.select = node.image.name in names
                print(f'{"+ Enable" if node.select else "- Disable"} output image `{node.image.name}` in material `{mat.name}`')
            else:
                node.select = False

def bake(name, type, baketex_names, pass_filter=None):
    set_active_images(baketex_names)

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
