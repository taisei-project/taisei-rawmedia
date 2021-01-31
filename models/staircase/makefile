TYPES := diffuse normal ambient roughness
TEXTURE_PATH := $(PREFIX)gfx/stage5/
MODEL_PATH := $(PREFIX)models/stage5/

STAIRS_MODELS := wall stairs metal
STAIRS_BAKE_TEXTURES := $(STAIRS_MODELS)

STAIRS_BLEND_FILE := staircase.blend

STAIRS_TEXTURE_FILES := $(filter-out metal_baked_ambient.png,$(foreach pre, $(STAIRS_BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_baked_$(suf).png)))
STAIRS_BASIS_FILES := $(filter-out metal_ambient.basis,$(foreach pre, $(STAIRS_BAKE_TEXTURES), $(foreach suf, $(TYPES), textures/$(pre)_$(suf).basis)))

STAIRS_MODEL_FILES := $(foreach mod, $(STAIRS_MODELS), models/$(mod).iqm)

TEXTURE_FILES := $(STAIRS_TEXTURE_FILES)
BASIS_FILES   := $(STAIRS_BASIS_FILES)
MODEL_FILES   := $(STAIRS_MODEL_FILES)

all: $(MODEL_FILES) $(BASIS_FILES)

$(STAIRS_TEXTURE_FILES) $(STAIRS_MODEL_FILES) &: $(STAIRS_BLEND_FILE)
	blender $(STAIRS_BLEND_FILE) --python scripts/export_models.py

textures/%_normal.basis: textures/%_baked_normal.png
	mkbasis $< --normal -o $@
	
textures/%_diffuse.basis: textures/%_baked_diffuse.png
	whereis mkbasis
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
