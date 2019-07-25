#!/usr/bin/env python3

import argparse
import contextlib
import io
import itertools
import multiprocessing
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


resize_filter = 'RobidouxSharp'
resize_scale = 1000.0 / 3072.0


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
}


def export_layers(kra, outdir):
    kra = str(kra.resolve())
    outdir = str(outdir.resolve())
    cwd = str(pathlib.Path(__file__).parent)
    os.environ['PYTHONPATH'] = cwd
    subprocess.call(['kritarunner', '-s', 'krita_exportlayers', kra, outdir], cwd=cwd)


def try_remove_file(path):
    with contextlib.suppress(FileNotFoundError):
        path.unlink()


def update_sprite_def(path, w, h, ox=0, oy=0):
    try_remove_file(path.with_name(path.name + '.renameme'))

    '''
    try:
        sprdef_text = path.read_text()
    except FileNotFoundError:
        sprdef_text = 'w = {:g}\nh = {:g}\noffset_x = {:g}\noffset_y = {:g}'.format(w, h, ox, oy)
    else:
        sprdef_text = re.sub(r'[\t ]*w[\t ]+=[\t ]+.*', 'w = {:g}'.format(w), sprdef_text)
        sprdef_text = re.sub(r'[\t ]*h[\t ]+=[\t ]+.*', 'h = {:g}'.format(h), sprdef_text)
        sprdef_text = re.sub(r'[\t ]*offset_x[\t ]+=[\t ]+.*', 'offset_x = {:g}'.format(ox), sprdef_text)
        sprdef_text = re.sub(r'[\t ]*offset_y[\t ]+=[\t ]+.*', 'offset_y = {:g}'.format(ox), sprdef_text)

    sprdef_text = f'\n{sprdef_text.strip()}\n'
    '''
    sprdef_text = '\nw = {:g}\nh = {:g}\noffset_x = {:g}\noffset_y = {:g}\n'.format(w, h, ox, oy)
    path.write_text(sprdef_text)


def export_char(name, args, executor, futures, temp_dir):
    taisei = args.taisei
    char = characters[name]
    kra = pathlib.Path(__file__).parent / f'{name}.kra'
    dest_dir = taisei / 'atlas' / 'portraits' / 'dialog'
    sprite_overrides = taisei / 'atlas' / 'overrides' / 'dialog'

    resize_args = [
        '-filter', resize_filter,
        '-resize', f'{100 * resize_scale}%',
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

    in_base  = temp_dir / f'{name}.png'
    out_base = dest_dir / f'{name}.png'

    export_layers(kra, temp_dir)

    variants = [
        x.stem[len(f'{name}_variant_'):]
        for x in temp_dir.glob(f'{name}_variant_*.png')
        if '.' not in x.stem
    ]

    g_base = Geometry(subprocess.check_output([
        'convert',
        in_base,
    ] + resize_args + [
        '-depth', '8',
    ] + char.im_args + [
        '-trim',
        '-print', '%wx%h%O',
        out_base,
    ], text=True))
    print(f'Exported `{out_base}`')
    parallel_task(optimize_image, out_base)

    def export_cropped_to_base(img_name):
        img_in   = temp_dir / img_name
        img_out  = dest_dir / img_name

        subprocess.check_call([
            'convert',
            img_in,
        ] + resize_args + [
            '-depth', '8',
        ] + char.im_args + [
            '-crop', str(g_base),
            img_out,
        ], text=True)
        print(f'Exported `{img_out}`')
        optimize_image(img_out)

    if (temp_dir / f'{name}.alphamap.png').is_file():
        parallel_task(export_cropped_to_base, f'{name}.alphamap.png')

    for var in variants:
        parallel_task(export_cropped_to_base, f'{name}_variant_{var}.png')

        if (temp_dir / f'{name}_variant_{var}.alphamap.png').is_file():
            parallel_task(export_cropped_to_base, f'{name}_variant_{var}.alphamap.png')

        update_sprite_def(
            sprite_overrides / f'{name}_variant_{var}.spr',
            g_base.width / 2, g_base.height / 2,
            char.offset_x, char.offset_y
        )

    update_sprite_def(
        sprite_overrides / f'{name}.spr',
        g_base.width / 2, g_base.height / 2,
        char.offset_x, char.offset_y
    )

    for face in temp_dir.glob('*_face_*.png'):
        @parallel_task
        def face_task(face=face):
            face_sprite_name = face.stem
            out_face = dest_dir / f'{face_sprite_name}.png'

            g_face = Geometry(subprocess.check_output([
                'convert',
                face,
            ] + resize_args + [
                '-depth', '8',
            ] + char.im_args + [
                '-trim',
                '-print', '%wx%h%O',
                out_face,
            ], text=True))
            print(f'Exported `{out_face}`')
            parallel_task(optimize_image, out_face)

            g_face.offset_x -= g_base.offset_x
            g_face.offset_y -= g_base.offset_y

            ofs_x = char.offset_x + g_face.offset_x / 2 - (g_base.width  - g_face.width)  / 4
            ofs_y = char.offset_y + g_face.offset_y / 2 - (g_base.height - g_face.height) / 4

            update_sprite_def(
                sprite_overrides / f'{face_sprite_name}.spr',
                g_face.width / 2, g_face.height / 2,
                ofs_x, ofs_y
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
