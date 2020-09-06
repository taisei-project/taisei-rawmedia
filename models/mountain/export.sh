#!/bin/bash

# works with blender 2.82

if [ $# -ne 1 ]; then
	echo Usage: $0 TAISEIPATH
	exit 1
fi

respath=$1

blender leaf_texture.blend --background --python scripts/render_groundtex.py
blender mountain.blend --python scripts/export_models.py

mkdir -p $respath/gfx/stage3
mkdir -p $respath/models/stage3

for tex in ground rocks trees; do
	mkbasis textures/"$tex"_baked_diffuse.png -o $respath/gfx/stage3/"$tex"_diffuse.basis
	mkbasis textures/"$tex"_baked_ambient.png -o $respath/gfx/stage3/"$tex"_ambient.basis
	mkbasis textures/"$tex"_baked_normal.png --normal -o $respath/gfx/stage3/"$tex"_normal.basis
	mkbasis textures/"$tex"_baked_roughness.png --r --linear -o $respath/gfx/stage3/"$tex"_roughness.basis
done

convert textures/leaves_baked_ambient.png \( textures/leaves_alpha_.png -colorspace gray -alpha off \) -compose copy-opacity -composite textures/leaves_composite_ambient.png
convert textures/leaves_baked_normal.png \( textures/leaves_alpha_.png -colorspace gray -alpha off \) -compose copy-opacity -composite textures/leaves_composite_normal.png
convert textures/leaves_baked_roughness.png \( textures/leaves_alpha_.png -colorspace gray -alpha off \) -compose copy-opacity -composite textures/leaves_composite_roughness.png
convert textures/leaves_baked_diffuse.png \( textures/leaves_alpha_.png -colorspace gray -alpha off \) -compose copy-opacity -composite textures/leaves_composite_diffuse.png

mkbasis textures/leaves_composite_diffuse.png --rgba --no-multiply-alpha -o $respath/gfx/stage3/leaves_diffuse.basis
mkbasis textures/leaves_composite_ambient.png --rgba --no-multiply-alpha -o $respath/gfx/stage3/leaves_ambient.basis
mkbasis textures/leaves_composite_normal.png --normal -o $respath/gfx/stage3/leaves_normal.basis
mkbasis textures/leaves_composite_roughness.png --gray-alpha --linear --no-multiply-alpha -o $respath/gfx/stage3/leaves_roughness.basis

cp -v models/ground.iqm $respath/models/stage3/
cp -v models/rocks.iqm $respath/models/stage3/
cp -v models/trees.iqm $respath/models/stage3/
cp -v models/leaves.iqm $respath/models/stage3/
