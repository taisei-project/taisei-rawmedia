#!/usr/bin/env python3

import argparse
import contextlib
import io
import itertools
import multiprocessing
import operator
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from concurrent.futures import (
    ThreadPoolExecutor,
    wait,
    FIRST_EXCEPTION
)


class Geometry:
    regex = re.compile(r'(\d+)x(\d+)([+-]\d+)([+-]\d+)')

    def __init__(self, g):
        (
            self.width,
            self.height,
            self.offset_x,
            self.offset_y,
        ) = (int(s) for s in Geometry.regex.findall(g)[0])

    def __str__(self):
        return '{}x{}{:+}{:+}'.format(self.width, self.height, self.offset_x, self.offset_y)


class Padding:
    def __init__(self, top=0, bottom=0, left=0, right=0):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    @classmethod
    def from_offset(cls, x=0, y=0):
        return cls(top=y, bottom=-y, left=x, right=-x)

    def _apply_op_copy(self, other, op):
        if not isinstance(other, Padding):
            other = Padding(other, other, other, other)

        return Padding(
            top=op(self.top, other.top),
            bottom=op(self.bottom, other.bottom),
            left=op(self.left, other.left),
            right=op(self.right, other.right)
        )

    def _apply_op(self, other, op):
        if not isinstance(other, Padding):
            other = Padding(other, other, other, other)

        self.top = op(self.top, other.top)
        self.bottom = op(self.bottom, other.bottom)
        self.left = op(self.left, other.left)
        self.right = op(self.right, other.right)

    def __add__(self, other): return self._apply_op_copy(other, operator.add)
    def __sub__(self, other): return self._apply_op_copy(other, operator.sub)
    def __mul__(self, other): return self._apply_op_copy(other, operator.mul)
    def __neg__(self, other): return self._apply_op_copy(other, operator.neg)
    def __iadd__(self, other): return self._apply_op(other, operator.add)
    def __isub__(self, other): return self._apply_op(other, operator.sub)
    def __imul__(self, other): return self._apply_op(other, operator.mul)
    def __neg__(self, other): return self._apply_op(other, operator.neg)


resize_filter = 'RobidouxSharp'
resize_scale = 1000.0 / 3072.0
sprite_size_factor = 0.5


class Character:
    def __init__(self, *, im_args=None, offset_x=0, offset_y=0):
        self.im_args = im_args if im_args else []
        self.offset_x = offset_x
        self.offset_y = offset_y


characters = {
    'cirno':   Character(),
    'elly':    Character(),
    'hina':    Character(),
    'iku':     Character(),
    'kurumi':  Character(),
    'marisa':  Character(im_args=['-flop']),
    'reimu':   Character(im_args=['-flop']),
    'scuttle': Character(offset_x=-16),
    'wriggle': Character(),
    'youmu':   Character(im_args=['-flop'], offset_x=32),
    'yumemi':  Character(offset_y=120),
}


def export_layers(kra, outdir, legacy):
    kra = str(kra.resolve())
    outdir = str(outdir.resolve())
    cwd = str(pathlib.Path(__file__).parent)
    os.environ['PYTHONPATH'] = cwd

    cmd = ['kritarunner', '-s', 'krita_exportlayers', '--', kra, outdir]

    if legacy:
        cmd.append('--legacy')

    subprocess.call(cmd, cwd=cwd)


def try_remove_file(path):
    with contextlib.suppress(FileNotFoundError):
        path.unlink()


def update_sprite_def(path, w, h, padding=None):
    try_remove_file(path.with_name(path.name + '.renameme'))

    sprdef_text = '\nw = {:g}\nh = {:g}'.format(w, h)

    if padding:
        sprdef_text += (
            '\npadding_top = {:g}'
            '\npadding_bottom = {:g}'
            '\npadding_left = {:g}'
            '\npadding_right = {:g}'
            '\n'
        ).format(padding.top, padding.bottom, padding.left, padding.right)

    path.write_text(sprdef_text)


def get_center_offset(g_base, g_object):
    ofs_x = g_object.offset_x - (g_base.width  - g_object.width)  / 2 - g_base.offset_x
    ofs_y = g_object.offset_y - (g_base.height - g_object.height) / 2 - g_base.offset_y
    return ofs_x, ofs_y


def calculate_relative_padding(g_base, g_object):
    m = Padding()
    m.top = g_object.offset_y - g_base.offset_y
    m.bottom = (g_base.offset_y + g_base.height) - (g_object.offset_y + g_object.height)
    m.left = g_object.offset_x - g_base.offset_x
    m.right = (g_base.offset_x + g_base.width) - (g_object.offset_x + g_object.width)
    return m


def export_char(name, args, executor, futures, temp_dir):
    taisei = args.taisei
    char = characters[name]
    kra = pathlib.Path(__file__).parent / f'{name}.kra'
    dest_dir = taisei / 'atlas' / 'portraits' / 'dialog'
    sprite_overrides = taisei / 'atlas' / 'overrides' / 'dialog'
    offset_padding = Padding.from_offset(char.offset_x, char.offset_y)

    resize_args = [
        '-colorspace', 'LAB',
        '-filter', resize_filter,
        '-resize', f'{100 * resize_scale}%',
        '-colorspace', 'sRGB',
    ]

    for p in itertools.chain(dest_dir.glob(f'{name}_*.*'), dest_dir.glob(f'{name}.*')):
        p.unlink()

    def optimize_image(path):
        if not args.fast:
            subprocess.check_call([taisei / 'scripts' / 'optimize-img.sh', path])

    def parallel_task(*args, **kwargs):
        futures.append(executor.submit(*args, **kwargs))

    temp_dir = temp_dir / name
    temp_dir.mkdir()

    export_layers(kra, temp_dir, args.legacy)

    variants = [
        x.stem[len(f'{name}_variant_'):]
        for x in temp_dir.glob(f'{name}_variant_*.png')
        if '.' not in x.stem
    ]

    def export_trimmed(img_name):
        img_in   = temp_dir / img_name
        img_out  = dest_dir / img_name

        geom = Geometry(subprocess.check_output([
            'convert',
            img_in,
        ] + resize_args + [
            '-depth', '8',
        ] + char.im_args + [
            '-trim',
            '-print', '%wx%h%O',
            img_out,
        ], text=True))
        print(f'Exported `{img_out}`')
        parallel_task(optimize_image, img_out)
        return geom

    def export_cropped(img_name, crop_geometry):
        img_in   = temp_dir / img_name
        img_out  = dest_dir / img_name

        subprocess.check_call([
            'convert',
            img_in,
        ] + resize_args + [
            '-depth', '8',
        ] + char.im_args + [
            '-crop', str(crop_geometry),
            img_out,
        ], text=True)
        print(f'Exported `{img_out}`')
        parallel_task(optimize_image, img_out)

    g_base = export_trimmed(f'{name}.png')

    if (temp_dir / f'{name}.alphamap.png').is_file():
        parallel_task(export_cropped, f'{name}.alphamap.png', g_base)

    for var in variants:
        @parallel_task
        def export_variant(var=var):
            g_var = export_trimmed(f'{name}_variant_{var}.png')

            if (temp_dir / f'{name}_variant_{var}.alphamap.png').is_file():
                parallel_task(export_cropped, f'{name}_variant_{var}.alphamap.png', g_var)

            pad = calculate_relative_padding(g_base, g_var) * sprite_size_factor

            update_sprite_def(
                sprite_overrides / f'{name}_variant_{var}.spr',
                g_var.width * sprite_size_factor, g_var.height * sprite_size_factor,
                pad + offset_padding
            )

    update_sprite_def(
        sprite_overrides / f'{name}.spr',
        g_base.width * sprite_size_factor, g_base.height * sprite_size_factor,
        offset_padding
    )

    for face in itertools.chain(temp_dir.glob('*_face_*.png'), temp_dir.glob('*_misc_*.png')):
        @parallel_task
        def face_task(face=face):
            face_sprite_name = face.stem
            g_face = export_trimmed(f'{face_sprite_name}.png')
            pad = calculate_relative_padding(g_base, g_face) * sprite_size_factor

            update_sprite_def(
                sprite_overrides / f'{face_sprite_name}.spr',
                g_face.width * sprite_size_factor,
                g_face.height * sprite_size_factor,
                pad + offset_padding
            )


def main(args):
    parser = argparse.ArgumentParser(description='Export raw character portraits into a Taisei repository', prog=args[0])

    parser.add_argument('taisei',
        type=pathlib.Path,
        help='path to the Taisei source root',
    )

    parser.add_argument('characters',
        metavar='character',
        nargs='*',
        choices=set(characters.keys()) | {'all'},
        default='all',
        help='which portraits to export (default: all)'
    )

    parser.add_argument('--fast',
        default=False,
        action='store_true',
        help='do not optimize images',
    )

    parser.add_argument('--legacy',
        default=False,
        action='store_true',
        help='export single variant with static face (for v1.3.x)',
    )

    args = parser.parse_args()

    if args.characters == 'all':
        args.characters = set(characters.keys())
    else:
        args.characters = set(args.characters)
        if 'all' in args.characters:
            args.characters = set(characters.keys())

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = pathlib.Path(temp_dir)
        futures = []

        with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() + 2) as ex:
            for name in args.characters:
                futures.append(ex.submit(export_char, name, args, ex, futures, temp_dir))

            while futures:
                futures.pop().result()

    print("Export finished, don't forget to regenerate the portraits atlas.")
    return 0


if __name__ == '__main__':
    exit(main(sys.argv))
