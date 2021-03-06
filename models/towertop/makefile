TYPES := diffuse normal ambient roughness
TEXTURE_PATH := $(PREFIX)gfx/stage6/
MODEL_PATH := $(PREFIX)models/stage6/

TOWER_BAKE_TEXTURES := tower stairs rim
TOWER_MODELS := $(TOWER_BAKE_TEXTURES) top_plate spire_spike

TOWER_BLEND_FILE := towertop.blend

TOWER_TEXTURE_FILES := $(foreach pre, $(TOWER_BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_baked_$(suf).png))
TOWER_BASIS_FILES := $(foreach pre, $(TOWER_BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_$(suf).basis))

TOWER_MODEL_FILES := $(foreach mod, $(TOWER_MODELS), models/$(mod).iqm)

TEXTURE_FILES := $(TOWER_TEXTURE_FILES)
BASIS_FILES   := $(TOWER_BASIS_FILES) textures/sky.basis
MODEL_FILES   := $(TOWER_MODEL_FILES) models/calabi-yau-quintic.iqm

all: $(MODEL_FILES) $(BASIS_FILES)

$(TOWER_TEXTURE_FILES) $(TOWER_MODEL_FILES) &: $(TOWER_BLEND_FILE)
	blender $(TOWER_BLEND_FILE) --python scripts/export_models.py

textures/sky.basis: textures/sky.png
	mkbasis $< --rgb -o $@

textures/%_normal.basis: textures/%_baked_normal.png
	mkbasis $< --normal -o $@
	
textures/%_diffuse.basis: textures/%_baked_diffuse.png
	mkbasis $< --rgb -o $@
	
textures/%_ambient.basis: textures/%_baked_ambient.png
	mkbasis $< --rgb -o $@
	
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
		
.PHONY: install all
