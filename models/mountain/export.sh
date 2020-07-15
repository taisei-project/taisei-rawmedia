#!/bin/bash

# works with blender 2.82

if [ $# -ne 1 ]; then
	echo Usage: $0 TAISEIPATH
	exit 1
fi

respath=$1/resources/00-taisei.pkgdir/

#blender leaf_texture.blend --background --python scripts/render_groundtex.py
blender mountain.blend --python scripts/export_models.py

convert textures/ground_baked_ambient.png -quality 90% $respath/gfx/stage3/ground_ambient.webp
convert textures/ground_baked_normal.png -quality 90% $respath/gfx/stage3/ground_normal.webp
convert textures/ground_baked_roughness.png -quality 90% $respath/gfx/stage3/ground_roughness.webp
convert textures/ground_baked_diffuse.png -quality 90% $respath/gfx/stage3/ground_diffuse.webp

convert textures/trees_ambient.png -quality 90% $respath/gfx/stage3/trees_ambient.webp
convert textures/trees_normal.png -quality 90% $respath/gfx/stage3/trees_normal.webp
convert textures/trees_roughness.png -quality 90% $respath/gfx/stage3/trees_roughness.webp
convert textures/trees_diffuse.png -quality 90% $respath/gfx/stage3/trees_diffuse.webp

convert textures/rocks_ambient.png -quality 90% $respath/gfx/stage3/rocks_ambient.webp
convert textures/rocks_normal.png -quality 90% $respath/gfx/stage3/rocks_normal.webp
convert textures/rocks_roughness.png -quality 90% $respath/gfx/stage3/rocks_roughness.webp
convert textures/rocks_diffuse.png -quality 90% $respath/gfx/stage3/rocks_diffuse.webp

convert textures/leaves_baked_ambient.png -quality 90% \( textures/leaves_alpha_.png -colorspace gray -alpha off \) -compose copy-opacity -composite $respath/gfx/stage3/leaves_ambient.webp
convert textures/leaves_baked_normal.png -quality 90% \( textures/leaves_alpha_.png -colorspace gray -alpha off \) -compose copy-opacity -composite $respath/gfx/stage3/leaves_normal.webp
convert textures/leaves_baked_roughness.png -quality 90% \( textures/leaves_alpha_.png -colorspace gray -alpha off \) -compose copy-opacity -composite $respath/gfx/stage3/leaves_roughness.webp
convert textures/leaves_baked_diffuse.png -quality 90% \( textures/leaves_alpha_.png -colorspace gray -alpha off \) -compose copy-opacity -composite $respath/gfx/stage3/leaves_diffuse.webp

cp -v models/ground.iqm $respath/models/stage3/
cp -v models/rocks.iqm $respath/models/stage3/
cp -v models/trees.iqm $respath/models/stage3/
cp -v models/leaves.iqm $respath/models/stage3/
