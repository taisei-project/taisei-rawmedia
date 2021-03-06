TYPES := diffuse normal ambient roughness
TEXTURE_PATH := $(PREFIX)gfx/stage6/
MODEL_PATH := $(PREFIX)models/stage6/

SKY_BLEND_FILE := sky.blend
SKY_TEXTURE_FILE := textures/sky.hdr
SKY_PNG_FILE := textures/sky.png
SKY_BASIS_FILE := textures/sky.basis.zst

TOWER_BAKE_TEXTURES := tower stairs rim tower_bottom spires
TOWER_MODELS := $(TOWER_BAKE_TEXTURES) top_plate

TOWER_BLEND_FILE := towertop.blend

TOWER_TEXTURE_FILES := $(foreach pre, $(TOWER_BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_baked_$(suf).png))
TOWER_BASIS_FILES := $(foreach pre, $(TOWER_BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_$(suf).basis)) $(SKY_BASIS_FILE)

TOWER_MODEL_FILES := $(foreach mod, $(TOWER_MODELS), models/$(mod).iqm)

TEXTURE_FILES := $(TOWER_TEXTURE_FILES)
BASIS_FILES   := $(TOWER_BASIS_FILES) $(SKY_BASIS_FILE)
MODEL_FILES   := $(TOWER_MODEL_FILES) models/calabi-yau-quintic.iqm

all: $(MODEL_FILES) $(BASIS_FILES)

$(SKY_TEXTURE_FILE) &: $(SKY_BLEND_FILE)
	blender $(SKY_BLEND_FILE) --background --python scripts/render_sky.py

$(SKY_PNG_FILE): $(SKY_TEXTURE_FILE)
	convert $< -colorspace sRGB $@
$(SKY_BASIS_FILE): $(SKY_PNG_FILE)
	mkbasis $< --uastc --incredibly-slow --rgb -o $@
	
$(TOWER_TEXTURE_FILES) $(TOWER_MODEL_FILES) &: $(TOWER_BLEND_FILE) $(SKY_TEXTURE_FILE)
	blender $(TOWER_BLEND_FILE) --python scripts/export_models.py

models/calabi-yau-quintic.iqm: calabi-yau-quintic.blend
	blender calabi-yau-quintic.blend --python scripts/calabi-yau-quintic.py

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
