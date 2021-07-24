
STAIRS_TEXTURES := diffuse normal ambient roughness
WALL_TEXTURES   := diffuse normal ambient roughness depth
METAL_TEXTURES  := roughness

TEXTURE_PATH := $(PREFIX)gfx/stage5/
MODEL_PATH := $(PREFIX)models/stage5/

STAIRS_MODELS := wall stairs metal
STAIRS_BAKE_TEXTURES := $(STAIRS_MODELS)

STAIRS_BLEND_FILE := staircase.blend

STAIRS_TEXTURE_FILES := \
	$(foreach suf, $(STAIRS_TEXTURES), textures/stairs_baked_$(suf).png) \
	$(foreach suf, $(WALL_TEXTURES), textures/wall_baked_$(suf).png) \
	$(foreach suf, $(METAL_TEXTURES), textures/metal_baked_$(suf).png)

STAIRS_BASIS_FILES := \
	$(foreach suf, $(STAIRS_TEXTURES), textures/stairs_$(suf).basis) \
	$(foreach suf, $(WALL_TEXTURES), textures/wall_$(suf).basis) \
	$(foreach suf, $(METAL_TEXTURES), textures/metal_$(suf).basis)

STAIRS_MODEL_FILES := $(foreach mod, $(STAIRS_MODELS), models/$(mod).iqm)

TEXTURE_FILES := $(STAIRS_TEXTURE_FILES) textures/envmap.png
BASIS_FILES   := $(STAIRS_BASIS_FILES) textures/envmap.basis
MODEL_FILES   := $(STAIRS_MODEL_FILES)

all: $(MODEL_FILES) $(BASIS_FILES)

$(STAIRS_TEXTURE_FILES) $(STAIRS_MODEL_FILES) &: $(STAIRS_BLEND_FILE)
	blender $(STAIRS_BLEND_FILE) --no-window-focus --python scripts/export_models.py

textures/envmap.png: $(STAIRS_BLEND_FILE)
	blender $(STAIRS_BLEND_FILE) --no-window-focus --python scripts/export_envmap.py

textures/%_normal.basis: textures/%_baked_normal.png
	mkbasis $< --normal -o $@

textures/%_diffuse.basis: textures/%_baked_diffuse.png
	mkbasis $< --rgb -o $@

textures/%_ambient.basis: textures/%_baked_ambient.png
	mkbasis $< --rgb -o $@

textures/%_roughness.basis: textures/%_baked_roughness.png
	mkbasis $< --r --linear -o $@

textures/%_depth.basis: textures/%_baked_depth.png
	mkbasis $< --r --linear -o $@

textures/envmap.basis: textures/envmap.png
	mkbasis $< --rgb --equirect-cubemap -o $@

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
