#!/bin/bash

# works with blender 2.82

# TODO: this probably wants to be a makefile

if [ $# -ne 1 ]; then
	echo Usage: $0 TAISEIPATH
	exit 1
fi

respath=$1

#blender corridor.blend --python scripts/export_corridor.py
#blender mansion.blend --python scripts/export_mansion.py
mkdir -p $respath/gfx/stage4
mkdir -p $respath/models/stage4

for tex in ground mansion corridor; do
	mkbasis textures/"$tex"_baked_diffuse.png -o $respath/gfx/stage4/"$tex"_diffuse.basis
	mkbasis textures/"$tex"_baked_ambient.png -o $respath/gfx/stage4/"$tex"_ambient.basis
	mkbasis textures/"$tex"_baked_normal.png --normal -o $respath/gfx/stage4/"$tex"_normal.basis
	mkbasis textures/"$tex"_baked_roughness.png --r --linear -o $respath/gfx/stage4/"$tex"_roughness.basis
done

cp -v models/mansion.iqm $respath/models/stage4/
cp -v models/ground.iqm $respath/models/stage4/
cp -v models/corridor.iqm $respath/models/stage4/
