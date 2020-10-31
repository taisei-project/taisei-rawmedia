#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
import subprocess
import multiprocessing
import os

root_path = Path(__file__).resolve().parent
raw_path = root_path / 'raw'
template_kra = root_path / 'template.kra'
sources = tuple(x.relative_to(raw_path) for x in raw_path.glob('**/*.jpg'))
# sources = [Path('locations/hakurei.jpg')]


def mkpath(root, p, suffix=None):
    if suffix is not None:
        p = p.with_suffix(suffix)

    p = root / p
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def cmd(cmd, *args, **kwargs):
    print('CMD: ', cmd)
    subprocess.check_call(cmd, *args, **kwargs)


def dequantize(src, dst):
    cmd([
        'gmic',
        src,
        'gcd_unquantize', '6,1,1,5,15',
        '-o', dst,
    ])
    return dst


def denoise(src, dst):
    cmd([
        'waifu2x-converter-cpp',
        '-i', src,
        '-o', dst,
        '-m', 'noise',
        '-p', '0',
        '--noise-level', '2',
    ])
    return dst


def kritaprocess(src_dequant, src_denoise, dst):
    e = dict(**os.environ)
    if 'PYTHONPATH' in e:
        e['PYTHONPATH'] = str(root_path) + os.pathsep + e['PYTHONPATH']
    else:
        e['PYTHONPATH'] = str(root_path)

    cmd([
        'kritarunner',
        '-s', 'krita_process',
        '--',
        template_kra,
        src_dequant,
        src_denoise,
        dst,
    ], env=e)

    return dst


def postprocess(src, dst):
    cmd([
        'convert',
        '-verbose',
        src,
        '-colorspace', 'Gray',
        '-filter', 'RobidouxSharp',
        '-resize', 'x1200',
        '-gravity', 'Center',
        '-crop', '1600x1200+0x0',
        '+repage',
        '-print', '%w %h\n',
        dst,
    ])
    return dst


def encodebasis(src, dst):
    cmd([
        'mkbasis',
        '--linear',
        '--r',
        src,
        '-o', dst,
    ])
    return dst


with TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)

    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as ex:

        futures = []

        for p in sources:
            src = raw_path / p

            f_dequant = ex.submit(dequantize, src, mkpath(tmpdir / 'dequant', p, '.png'))
            f_denoise = ex.submit(denoise, src, mkpath(tmpdir / 'denoise', p, '.png'))

            def future(p=p, f_dequant=f_dequant, f_denoise=f_denoise):
                src = kritaprocess(
                    f_dequant.result(),
                    f_denoise.result(),
                    mkpath(tmpdir / 'kritaprocess', p, '.png')
                )

                src = postprocess(src, mkpath(root_path / 'out-png', p, '.png'))
                return encodebasis(src, mkpath(root_path / 'out-basis', p, '.basis'))

            futures.append(ex.submit(future))

        for fut in futures:
            print(fut.result())

