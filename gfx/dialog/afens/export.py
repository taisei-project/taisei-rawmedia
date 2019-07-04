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

from collections import namedtuple

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


def enable_alphamap(kra_in, kra_out):
    namespace = 'http://www.calligra.org/DTD/krita'
    tagpref = '{' + namespace + '}'
    docname = 'maindoc.xml'

    ET.register_namespace('', namespace)

    with zipfile.ZipFile(kra_in, mode='r') as zinput:
        doc = ET.parse(zinput.open(docname))
        toplayers = doc.find(f'{tagpref}IMAGE').find(f'{tagpref}layers').findall(f'{tagpref}layer')
        have_alphamap = False

        for layer in toplayers:
            attrib = layer.attrib

            if attrib['name'] == 'alphamap':
                attrib['visible'] = '1'
                have_alphamap = True
            else:
                attrib['visible'] = '0'

        if not have_alphamap:
            return None

        newdoc = io.BytesIO()
        newdoc.write((
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<!DOCTYPE DOC PUBLIC '-//KDE//DTD krita 2.0//EN' 'http://www.calligra.org/DTD/krita-2.0.dtd'>\n"
        ).encode('utf8'))
        doc.write(newdoc, encoding='UTF-8', xml_declaration=False)
        newdoc.seek(0)
        newdoc = newdoc.read().decode('utf8')

        with zipfile.ZipFile(kra_out, 'w') as zoutput:
            zoutput.comment = zinput.comment

            for zinfo in zinput.infolist():
                if zinfo.filename == docname:
                    zoutput.writestr(docname, newdoc)
                else:
                    zoutput.writestr(zinfo, zinput.read(zinfo.filename))

    return kra_out



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

    in_alphamap  = temp_dir / f'{name}.alphamap.png'
    out_alphamap = dest_dir / f'{name}.alphamap.png'

    export_layers(kra, temp_dir)

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

    if (temp_dir / f'{name}.alphamap.png').is_file():
        @parallel_task
        def alphamap_task():
            subprocess.check_call([
                'convert',
                in_alphamap,
            ] + resize_args + [
                '-depth', '8',
            ] + char.im_args + [
                '-crop', str(g_base),
                out_alphamap,
            ], text=True)
            print(f'Exported `{out_alphamap}`')
            optimize_image(out_alphamap)

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


def OLD_export_char(name, args, executor):
    taisei = args.taisei
    im_extra_args = characters[name]
    srcfile = pathlib.Path(__file__).parent / f'{name}.kra'
    dest_dir = taisei / 'atlas' / 'portraits' / 'dialog'
    dest_png = dest_dir / f'{name}.png'
    dest_alphamap_png = dest_dir / f'{name}.alphamap.png'
    dest_webp = dest_dir / f'{name}.webp'
    dest_alphamap_webp = dest_dir / f'{name}.alphamap.webp'

    with tempfile.TemporaryDirectory() as tdir:
        tdir = pathlib.Path(tdir)

        # remove previous exports
        for img in [dest_png, dest_webp, dest_alphamap_png, dest_alphamap_webp]:
            with contextlib.suppress(FileNotFoundError):
                img.unlink()

        # start exporting, resizing, and cropping the main image
        main_img_task = executor.submit(export_layers, srcfile, tdir)

        main_img_task.result()
        print(tdir)
        input()
        quit(0)

        alphamap_kra = enable_alphamap(srcfile, tdir / srcfile.name)

        # start exporting the alphamap
        # we can't crop it until we're done with the main image
        if alphamap_kra:
            # NOTE: https://bugs.kde.org/409133
            alphamap_task = executor.submit(subprocess.call, ['krita', alphamap_kra, '--export', '--export-filename', out_alphamap_tmp])

        # wait for main image export to finish
        main_img_task.result()

        # fetch metadata from exported main image
        w, h, xofs, yofs = re.findall(r'.*? PNG (\d+)x(\d+).* \d+x\d+\+(\d+)\+(\d+)', subprocess.check_output(['identify', dest_png], text=True))[0]
        w, h, xofs, yofs = int(w), int(h), int(xofs), int(yofs)

        # now we can start optimizing it
        if not args.fast:
            main_img_task = executor.submit(subprocess.check_call, [taisei / 'scripts' / 'optimize-img.sh', dest_png])

        # update atlas overrides
        overrides = taisei / 'atlas' / 'overrides' / 'dialog'

        with contextlib.suppress(FileNotFoundError):
            (overrides / f'{name}.spr.renameme').unlink()

        sprdef = overrides / f'{name}.spr'

        try:
            sprdef_text = sprdef.read_text()
        except FileNotFoundError:
            # no override? create one with just w and h set
            sprdef_text = 'w = {:g}\nh = {:g}'.format(w/2, h/2)
        else:
            # update w and h, keep other properties
            sprdef_text = re.sub(r'[\t ]*w[\t ]+=[\t ]+.*', 'w = {:g}'.format(w/2), sprdef_text)
            sprdef_text = re.sub(r'[\t ]*h[\t ]+=[\t ]+.*', 'h = {:g}'.format(h/2), sprdef_text)

        sprdef_text = f'\n{sprdef_text.strip()}\n'
        sprdef.write_text(sprdef_text)

        if alphamap_kra:
            # wait for the alphamap export to finish
            alphamap_task.result()

            # now resize, crop, and optimize it
            # no need to defer it to a task since it needs to be done sequentially anyway,
            # and we have nothing else left to do in parallel
            subprocess.check_call([
                'convert',
                '-verbose',
                out_alphamap_tmp,
                '-filter', 'RobidouxSharp',
                '-resize', f'{100000/3072}%',  # 'x1000',
            ] + char.args + [
                # CAUTION: it's important to do this *after* char.args for flipping to work correctly!
                '-crop', f'{w}x{h}+{xofs}+{yofs}'
            ] + [dest_alphamap_png])

            if not args.fast:
                subprocess.check_call([taisei / 'scripts' / 'optimize-img.sh', dest_alphamap_png])

        # wait for the main image optimization to finish
        main_img_task.result()


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

        with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as ex:
            for name in args.characters:
                futures.append(ex.submit(export_char, name, args, ex, futures, temp_dir))

            while futures:
                futures.pop().result()

    print("Export finished, don't forget to regenerate the portraits atlas.")
    return 0


if __name__ == '__main__':
    exit(main(sys.argv))
