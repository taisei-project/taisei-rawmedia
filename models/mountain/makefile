LEAF_TEXTURES = textures/leaf.png textures/leaf_normal/Image0001.png textures/leaf_uv/Image0001.png
LEAF_BLEND_FILE := leaf_texture.blend


BAKE_TEXTURES := ground rocks trees leaves
TYPES := diffuse normal ambient roughness
MODELS := ground rocks leaves trees

BLEND_FILE := mountain.blend
INPUT_TEXTURES := textures/veins.png

TEXTURE_PATH := $(PREFIX)gfx/stage3/
MODEL_PATH := $(PREFIX)models/stage3/

TEXTURE_FILES := $(foreach pre, $(BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_baked_$(suf).png))
BASIS_FILES := $(foreach pre, $(BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_$(suf).basis))

MODEL_FILES := $(foreach mod, $(MODELS), models/$(mod).iqm)

TEXTURE_FILES += leaves_alpha_.png

all: $(MODEL_FILES) $(BASIS_FILES)


$(LEAF_TEXTURES) &: $(LEAF_BLEND_FILE) $(INPUT_TEXTURES)
	blender $(LEAF_BLEND_FILE) --background --python scripts/render_leaftex.py


$(TEXTURE_FILES) $(MODEL_FILES) &: $(BLEND_FILE) $(LEAF_TEXTURES) $(INPUT_TEXTURES)
	blender $(BLEND_FILE) --python scripts/export_models.py

textures/leaves_composite_roughness.png: textures/leaves_baked_roughness.png textures/leaves_alpha_.png
	convert textures/leaves_baked_roughness.png \( textures/leaves_alpha_.png -colorspace gray -alpha off -morphology Erode disk:1 \) -compose copy-opacity -composite textures/leaves_composite_roughness.png

textures/leaves_roughness.basis: textures/leaves_composite_roughness.png
	mkbasis $< --gray-alpha --linear --no-multiply-alpha -o $@

textures/%_normal.basis: textures/%_baked_normal.png
	mkbasis $< --normal -o $@
	
textures/%_diffuse.basis: textures/%_baked_diffuse.png
	whereis mkbasis
	mkbasis $< --rgb --no-multiply-alpha -o $@
	
textures/%_ambient.basis: textures/%_baked_ambient.png
	mkbasis $< --rgb --no-multiply-alpha -o $@
	
textures/%_roughness.basis: textures/%_baked_roughness.png
	mkbasis $< --gray-alpha --linear --no-multiply-alpha -o $@

install: $(MODEL_FILES) $(BASIS_FILES)
	mkdir -p $(TEXTURE_PATH)
	mkdir -p $(MODEL_PATH)
	for f in $(BASIS_FILES); do \
		cp $$f $(TEXTURE_PATH)/$$(basename $$f); \
	done
	for f in $(MODEL_FILES); do \
		cp $$f $(MODEL_PATH)/$$(basename $$f); \
	done
		
.PHONY: install
