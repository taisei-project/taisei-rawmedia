TYPES := diffuse normal ambient roughness
TEXTURE_PATH := $(PREFIX)gfx/stage2/
MODEL_PATH := $(PREFIX)models/stage2/

PATH_BAKE_TEXTURES := ground rocks
PATH_MODELS := ground rocks grass

PATH_BLEND_FILE := path.blend

PATH_TEXTURE_FILES := $(foreach pre, $(PATH_BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_baked_$(suf).png))
PATH_BASIS_FILES := $(foreach pre, $(PATH_BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_$(suf).basis))

PATH_MODEL_FILES := $(foreach mod, $(PATH_MODELS), models/$(mod).iqm)

BRANCH_BAKE_TEXTURES := branch leaves
BRANCH_MODELS := branch leaves

BRANCH_BLEND_FILE := branch.blend
BRANCH_INPUT_TEXTURES := textures/leaf_diffuse.png textures/leaf_normal.png

BRANCH_TEXTURE_FILES := $(foreach pre, $(BRANCH_BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_baked_$(suf).png))
BRANCH_BASIS_FILES := $(foreach pre, $(BRANCH_BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_$(suf).basis))

BRANCH_MODEL_FILES := $(foreach mod, $(BRANCH_MODELS), models/$(mod).iqm)

GRASS_INPUT_TEXTURE := textures/grass.png
GRASS_BASIS_FILES := $(foreach suf, $(TYPES), textures/grass_$(suf).basis)

TEXTURE_FILES := $(PATH_TEXTURE_FILES) $(BRANCH_TEXTURE_FILES)
BASIS_FILES   := $(PATH_BASIS_FILES) $(BRANCH_BASIS_FILES) $(GRASS_BASIS_FILES) textures/water_floor.basis
MODEL_FILES   := $(PATH_MODEL_FILES) $(BRANCH_MODEL_FILES)

all: $(MODEL_FILES) $(BASIS_FILES)

$(PATH_TEXTURE_FILES) $(PATH_MODEL_FILES) &: $(PATH_BLEND_FILE)
	blender $(PATH_BLEND_FILE) --python scripts/export_models.py
	
$(BRANCH_TEXTURE_FILES) $(BRANCH_MODEL_FILES) &: $(BRANCH_BLEND_FILE) $(BRANCH_INPUT_TEXTURES)
	blender $(BRANCH_BLEND_FILE) --python scripts/export_branch.py


textures/grass_baked_normal.png:
	convert -size 256x256 xc:rgb\(128,128,128\) $@

textures/grass_baked_roughness.png: $(GRASS_INPUT_TEXTURE)
	convert $< -grayscale Rec709Luminance $@
	
textures/grass_baked_diffuse.png: $(GRASS_INPUT_TEXTURE)
	cp $< $@
	
textures/grass_baked_ambient.png: $(GRASS_INPUT_TEXTURE)
	convert $< $@

textures/leaves_composite_roughness.png: textures/leaves_baked_roughness.png
	convert $< -morphology Erode disk:1 -transparent black $@ # trick 17
	
textures/leaves_roughness.basis: textures/leaves_composite_roughness.png
	mkbasis $< --gray-alpha --linear --no-multiply-alpha -o $@

textures/%_normal.basis: textures/%_baked_normal.png
	mkbasis $< --normal -o $@
	
textures/%_diffuse.basis: textures/%_baked_diffuse.png
	whereis mkbasis
	mkbasis $< --rgb -o $@
	
textures/%_ambient.basis: textures/%_baked_ambient.png
	mkbasis $< --rgb -o $@
	
textures/%_roughness.basis: textures/%_baked_roughness.png
	mkbasis $< --gray-alpha --linear --no-multiply-alpha -o $@

textures/water_floor.basis: textures/water_floor.png
	mkbasis $< --rgb -o $@

install: $(MODEL_FILES) $(BASIS_FILES)
	mkdir -p $(TEXTURE_PATH)
	mkdir -p $(MODEL_PATH)
	for f in $(BASIS_FILES); do \
		cp $$f $(TEXTURE_PATH)/$$(basename $$f); \
	done
	for f in $(MODEL_FILES); do \
		cp $$f $(MODEL_PATH)/$$(basename $$f); \
	done
		
.PHONY: install all
