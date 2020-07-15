#!/bin/bash

# works with blender 2.82

if [ $# -ne 1 ]; then
	echo Usage: $0 TAISEIPATH
	exit 1
fi

respath=$1/resources/00-taisei.pkgdir/

blender corridor.blend --python scripts/export_corridor.py
#blender mansion.blend --python scripts/export_mansion.py

cp -v textures/ground_baked_diffuse.png $respath/gfx/stage4/ground_diffuse.png
cp -v textures/ground_baked_roughness.png $respath/gfx/stage4/ground_roughness.png
cp -v textures/ground_baked_normal.png $respath/gfx/stage4/ground_normal.png
cp -v textures/ground_baked_ambient.png $respath/gfx/stage4/ground_ambient.png
cp -v textures/mansion_baked_diffuse.png $respath/gfx/stage4/mansion_diffuse.png
cp -v textures/mansion_baked_roughness.png $respath/gfx/stage4/mansion_roughness.png
cp -v textures/mansion_baked_normal.png $respath/gfx/stage4/mansion_normal.png
cp -v textures/mansion_baked_ambient.png $respath/gfx/stage4/mansion_ambient.png
cp -v textures/corridor_baked_diffuse.png $respath/gfx/stage4/corridor_diffuse.png
cp -v textures/corridor_baked_roughness.png $respath/gfx/stage4/corridor_roughness.png
cp -v textures/corridor_baked_normal.png $respath/gfx/stage4/corridor_normal.png
cp -v textures/corridor_baked_ambient.png $respath/gfx/stage4/corridor_ambient.png

cp -v models/mansion.iqm $respath/models/stage4/
cp -v models/ground.iqm $respath/models/stage4/
cp -v models/corridor.iqm $respath/models/stage4/
