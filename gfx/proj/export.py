#!/usr/bin/env python3

import sys
import os
import pathlib

script = pathlib.Path(__file__)

try:
    from krita import *
except ImportError:
    basedir = str(script.parent)
    module = script.stem
    os.environ['PYTHONPATH'] = os.pathsep.join([basedir] + list(filter(None, os.environ.get('PYTHONPATH', '').split(os.pathsep))))
    os.execlp('kritarunner', 'kritarunner', '-s', module, *sys.argv[1:])


kr = Krita.instance()
kr.setBatchmode(True)

exportConfig = InfoObject()
exportConfig.setProperty("saveSRGBProfile", False)
exportConfig.setProperty("compression", 1)

resize_filter = 'RobidouxSharp'
resize_scale = 0.75 / 4
sprite_size_factor = 0.5
supersampling = 2.0

sprite_size_factor /= supersampling
resize_scale *= supersampling


def process(kra, taisei_dir, temp_dir, executor, futures):
    doc = kr.openDocument(str(kra))
    doc.setBatchmode(True)

    def sync(doc=doc):
        doc.waitForDone()
        doc.refreshProjection()
        doc.waitForDone()

    bounds = doc.bounds()
    root = doc.rootNode()

    bullets = findNode(root.childNodes(), 'bullets').childNodes()
    setVisibleAll(bullets, False)

    for bullet in bullets:
        name = bullet.name()
        export_path = temp_dir / f'{name}.png'
        print(f'Exporting `{name}` as `{export_path}`...')
        bullet.setVisible(True)
        doc.refreshProjection()
        doc.waitForDone()
        root.save(str(export_path), 1, 1, exportConfig, bounds)
        doc.waitForDone()
        futures.append(executor.submit(postprocess, name, export_path, taisei_dir))
        bullet.setVisible(False)


def postprocess(name, export_path, taisei_dir):
    import subprocess

    print(f'Begin post-process for `{export_path}`')

    atlas_dir = taisei_dir / 'atlas'
    atlas_subdir = 'proj'
    out_dir = atlas_dir / 'common' / atlas_subdir
    override_dir = atlas_dir / 'overrides' / atlas_subdir
    out_path = out_dir / f'{name}.png'

    for suffix in ('png', 'webp'):
        tryRemoveFile(out_dir / f'{name}.{suffix}')

    w, h = subprocess.check_output([
        'convert',
        export_path,
        '-filter', resize_filter,
        '-colorspace', 'RGB',
        '-resize', f'{100 * resize_scale}%',
        '-colorspace', 'sRGB',
        '-depth', '8',
        '-trim',
        '-print', '%w %h',
        out_path,
    ], text=True).split()

    w, h = float(w) * sprite_size_factor, float(h) * sprite_size_factor

    tryRemoveFile(override_dir / f'{name}.spr.renameme')
    (override_dir / f'{name}.spr').write_text('\nw = {:g}\nh = {:g}'.format(w, h))

    subprocess.check_call([taisei_dir / 'scripts' / 'optimize-img.sh', out_path])

    print(f'End post-process for `{export_path}`')


def __main__(args):
    import tempfile
    from concurrent.futures import ProcessPoolExecutor as Executor

    kra = script.parent / 'bullets.kra'
    taisei = pathlib.Path(args[0])

    assert kra.is_file()
    assert taisei.is_dir()

    futures = []

    with tempfile.TemporaryDirectory() as temp_dir, Executor() as ex:
        process(kra, taisei, pathlib.Path(temp_dir), ex, futures)

        for fut in futures:
            fut.result()

        # import code; code.interact(local=locals())


def findNode(nodes, name):
    for node in nodes:
        if node.name() == name:
            return node


def setVisibleAll(nodes, val):
    for n in nodes:
        n.setVisible(val)


def tryRemoveFile(path):
    try:
        pathlib.Path(path).unlink()
    except FileNotFoundError:
        pass
