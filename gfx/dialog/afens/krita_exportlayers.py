
from krita import *
from contextlib import contextmanager

import pathlib
import tempfile
import shutil
import re
import argparse


kr = Krita.instance()
kr.setBatchmode(True)

exportConfig = InfoObject()
exportConfig.setProperty("saveSRGBProfile", False)
exportConfig.setProperty("compression", 1)

export_overrides = pathlib.Path(__file__).parent / 'export-overrides'


def __main__(args):
    p = argparse.ArgumentParser(description='Export layers from character art for further processing', prog=__file__)

    p.add_argument('kra',
        type=pathlib.Path,
        help='path to the source .kra',
    )

    p.add_argument('output',
        type=pathlib.Path,
        help='path to the output directory',
    )

    p.add_argument('--legacy',
        default=False,
        action='store_true',
        help='export single variant with static face (for v1.3.x)',
    )

    args = p.parse_args(args)

    kra_path = args.kra
    out_path = args.output
    is_legacy = args.legacy

    basename = kra_path.stem

    doc = kr.openDocument(str(kra_path))
    doc.setBatchmode(True)
    bounds = doc.bounds()
    root = doc.rootNode()

    def msg(*args):
        print(f'[{basename}]', *args)

    def export(node, suffix='', doc=doc):
        fname = f'{basename}{suffix}.png'
        out = str(out_path / fname)
        override = export_overrides / fname

        if override.is_file():
            shutil.copy(override, out)
            msg(f'Copied `{override}` as `{out}`')
        else:
            sync(doc=doc)
            node.save(out, 1, 1, exportConfig, bounds)
            doc.waitForDone()
            msg(f'Exported `{out}`')

    def sync(doc=doc):
        doc.waitForDone()
        doc.refreshProjection()
        doc.waitForDone()

    @contextmanager
    def conditions(*cond_list, root=root):
        cond_disabled = findConditionallyDisabled(root, cond_list)
        setVisibleAll(cond_disabled, False)
        cond_enabled = findConditionallyEnabled(root, cond_list)
        setVisibleAll(cond_enabled, True)
        yield
        setVisibleAll(cond_enabled, False)
        setVisibleAll(cond_disabled, True)

    @contextmanager
    def hideExtraneous(*keep_list, root=root):
        trash, _ = findExtraneous(root, keep_list)
        trash = filterVisible(trash)
        setVisibleAll(trash, False)
        yield
        setVisibleAll(trash, True)

    @contextmanager
    def temporarilyVisible(*nodes):
        for n in nodes: n.setVisible(True)
        yield
        for n in nodes: n.setVisible(False)

    if is_legacy:
        expressions = findNode(root.childNodes(), 'expression')

        if expressions:
            expressions_children = expressions.childNodes()
            setVisibleAll(expressions_children, False)

            normal_face = findNode(expressions_children, 'normal')

            if normal_face:
                normal_face.setVisible(True)

        variants = findNode(root.childNodes(), 'variant')

        if variants:
            setVisibleAll(variants.childNodes(), False)

        alphamap = findNode(root.childNodes(), 'alphamap')

        with conditions('novariant', 'face=normal'):
            if alphamap:
                with temporarilyVisible(alphamap):
                    msg('Exporting alphamap...')
                    export(alphamap, '.alphamap')

            msg('Exporting base...')
            export(root)

        msg('Done')

        return

    expressions, exp_overlay = findWithOverlay(root, 'expression')
    if expressions:
        with temporarilyVisible(expressions):
            setVisibleAll(expressions.childNodes(), False)
            exp_overlay = filterVisible(exp_overlay)
            for face in expressions.childNodes():
                msg(f'Exporting face `{face.name()}`...')
                with hideExtraneous(exp_overlay, face), conditions(f'face={face.name()}'), temporarilyVisible(face):
                    export(root, f'_face_{face.name()}')

    alphamap = findNode(root.childNodes(), 'alphamap')

    if alphamap:
        alphamap.setVisible(False)

    variants, _ = findWithOverlay(root, 'variant')

    if variants:
        with temporarilyVisible(variants):
            setVisibleAll(variants.childNodes(), False)
            for var in variants.childNodes():
                with temporarilyVisible(var), conditions(f'variant={var.name()}'):
                    if alphamap:
                        with temporarilyVisible(alphamap):
                            # BUG: broken due to https://bugs.kde.org/show_bug.cgi?id=409949
                            msg(f'Exporting variant `{var.name()}` alphamap...')
                            export(alphamap, f'_variant_{var.name()}.alphamap')

                    msg(f'Exporting variant `{var.name()}`...')
                    export(root, f'_variant_{var.name()}')

    with conditions('novariant'):
        if alphamap:
            with temporarilyVisible(alphamap):
                msg('Exporting alphamap...')
                export(alphamap, '.alphamap')

        msg('Exporting base...')
        export(root)

    msg('Done')
    # import code; code.interact(local=locals())


def findNode(nodes, name):
    for node in nodes:
        if node.name() == name:
            return node


def findWithOverlay(root, name):
    siblings = []

    for n in reversed(root.childNodes()):
        if n.name() == name:
            return n, siblings

        x, sib = findWithOverlay(n, name)

        if x:
            return x, siblings + sib

        siblings.append(n)

    return None, []


def findExtraneous(root, keepset):
    trash = []
    found_kept = False

    if root in keepset:
        return trash, True

    for n in root.childNodes():
        nested_trash, nested_found_kept = findExtraneous(n, keepset)

        if nested_found_kept:
            found_kept = True
            trash += nested_trash
        else:
            trash.append(n)

    return trash, found_kept


def walkNodes(root):
    for n in root.childNodes():
        yield n

        for s in walkNodes(n):
            yield s


def findConditionallyDisabled(root, true_conds):
    r = re.compile(r'@disable-if\[(.*?)\]')
    ret = []

    for n in walkNodes(root):
        if not n.visible():
            continue

        nconds = r.findall(n.name())

        for c in nconds:
            if c in true_conds:
                ret.append(n)

    return ret


def findConditionallyEnabled(root, true_conds):
    r = re.compile(r'@enable-if\[(.*?)\]')
    ret = []

    for n in walkNodes(root):
        if n.visible():
            continue

        nconds = r.findall(n.name())

        for c in nconds:
            if c in true_conds:
                ret.append(n)

    return ret


def filterVisible(nodes):
    return [n for n in nodes if n.visible()]


def setVisibleAll(nodes, val):
    for n in nodes:
        n.setVisible(val)
