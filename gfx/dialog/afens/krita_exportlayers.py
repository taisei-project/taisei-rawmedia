
from krita import *
import pathlib
import tempfile


kr = Krita.instance()
kr.setBatchmode(True)

exportConfig = InfoObject()
exportConfig.setProperty("saveSRGBProfile", False)
exportConfig.setProperty("compression", 1)


def __main__(args):
    kra_path = pathlib.Path(args[0])
    out_path = pathlib.Path(args[1])

    basename = kra_path.stem

    doc = kr.openDocument(str(kra_path))
    doc.setBatchmode(True)
    bounds = doc.bounds()
    root = doc.rootNode()

    def export(node, suffix='', doc=doc):
        o = str(out_path / f'{basename}{suffix}.png')
        node.save(o, 1, 1, exportConfig, bounds)
        doc.waitForDone()
        print(f'Exported `{o}`')

    def sync(doc=doc):
        doc.waitForDone()
        doc.refreshProjection()
        doc.waitForDone()

    expressions, exp_overlay = findWithOverlay(root, 'expression')
    if expressions:
        exp_overlay = filterVisible(exp_overlay)

        for face in expressions.childNodes():
            print(f'Exporting face `{face.name()}`...')
            keep = exp_overlay + [face]
            trash, _ = findExtraneous(root, keep)
            trash = filterVisible(trash)
            setVisibleAll(trash, False)
            face.setVisible(True)
            sync()
            export(root, f'_face_{face.name()}')
            # export(face, f'_face_{face.name()}_reference')
            setVisibleAll(trash, True)

        expressions.setVisible(False)

    alphamap = findNode(root.childNodes(), 'alphamap')
    variants, _ = findWithOverlay(root, 'variant')

    if variants:
        variants.setVisible(True)
        setVisibleAll(variants.childNodes(), False)

    if alphamap:
        alphamap_trash, _ = findExtraneous(root, [alphamap])
        alphamap_trash = filterVisible(alphamap_trash)

    if variants:
        setVisibleAll(variants.childNodes(), False)
        for var in variants.childNodes():
            var.setVisible(True)

            if alphamap:
                print(f'Exporting variant `{var.name()}` alphamap...')

                # BUG: broken due to https://bugs.kde.org/show_bug.cgi?id=409949

                alphamap.setVisible(True)
                sync()
                export(alphamap, f'_variant_{var.name()}.alphamap')
                alphamap.setVisible(False)

                '''
                alphamap.setVisible(True)
                setVisibleAll(alphamap_trash, False)
                sync()
                export(root, f'_variant_{var.name()}.alphamap')
                setVisibleAll(alphamap_trash, True)
                alphamap.setVisible(False)
                '''

            print(f'Exporting variant `{var.name()}`...')
            sync()
            export(root, f'_variant_{var.name()}')

            var.setVisible(False)

        sync()

    if alphamap:
        alphamap.setVisible(True)
        sync()
        print('Exporting alphamap...')
        export(alphamap, '.alphamap')
        alphamap.setVisible(False)

    print('Exporting base...')
    sync()
    export(root)

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


def filterVisible(nodes):
    return [n for n in nodes if n.visible()]


def setVisibleAll(nodes, val):
    for n in nodes:
        n.setVisible(val)
