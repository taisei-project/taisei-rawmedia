#!/bin/bash

# works with blender 2.82

if [ $# -ne 1 ]; then
	echo Usage: $0 TAISEIPATH
	exit 1
fi

respath=$1/resources/00-taisei.pkgdir/

blender leaf_texture.blend --background --python scripts/render_groundtex.py
blender mountain.blend --background --python scripts/export_objs.py

convert textures/ground_baked.png $respath/gfx/stage3/ground.webp
convert textures/rocks.png $respath/gfx/stage3/rocks.webp
convert textures/leaves_baked.png \( textures/leaves_alpha.png -colorspace gray -alpha off \) -compose copy-opacity -composite $respath/gfx/stage3/leaves.webp

cp -v objs/ground.obj $respath/models/stage3/
cp -v objs/rocks.obj $respath/models/stage3/
cp -v objs/leaves.obj $respath/models/stage3/
