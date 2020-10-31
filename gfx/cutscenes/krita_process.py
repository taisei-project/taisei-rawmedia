
from krita import *
from pathlib import Path

kr = Krita.instance()
kr.setBatchmode(True)

exportConfig = InfoObject()
exportConfig.setProperty("saveSRGBProfile", False)
exportConfig.setProperty("compression", 1)

def __main__(args):
    template_kra = args[0]
    dequant_in = args[1]
    denoise_in = args[2]
    out = args[3]
    print(args)

    doc = kr.openDocument(template_kra)

    try:
        root = doc.rootNode()
        node_denoise = None
        node_dequant = None

        for n in root.childNodes():
            if n.name() == 'image':
                inode = n
                for n in inode.childNodes():
                    if n.name() == 'denoised':
                        node_denoise = n
                    elif n.name() == 'dequantized':
                        node_dequant = n
                break

        assert node_denoise is not None
        assert node_dequant is not None

        layer_denoise = doc.createFileLayer("denoise_layer", denoise_in, "None")
        layer_dequant = doc.createFileLayer("dequant_layer", dequant_in, "None")

        node_denoise.addChildNode(layer_denoise, None)
        node_dequant.addChildNode(layer_dequant, None)

        bounds = node_denoise.bounds()
        doc.resizeImage(bounds.x(), bounds.y(), bounds.width(), bounds.height())

        doc.waitForDone()
        doc.refreshProjection()
        doc.waitForDone()

        root.save(out, 1, 1, exportConfig, bounds)
    finally:
        doc.close()

    pass

'''
__main__([
      '/data/wip/taisei cutscenes/template.kra',
      '/data/wip/taisei cutscenes/dequantized/hakurei shrine.png',
      '/data/wip/taisei cutscenes/denoised/hakurei shrine.png',
      '/tmp/hakurei_shrine.png',
      ])
'''
