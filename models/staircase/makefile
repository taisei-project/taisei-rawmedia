
STAIRS_TEXTURES := diffuse normal ambient ao roughness
WALL_TEXTURES   := diffuse normal ambient ao roughness depth
METAL_TEXTURES  :=                        ao roughness

TEXTURE_PATH := $(PREFIX)gfx/stage5/
MODEL_PATH := $(PREFIX)models/stage5/

TEX_BAKED := textures/baked
TEX_BASIS := textures/basis

STAIRS_MODELS := wall stairs metal
STAIRS_BAKE_TEXTURES := $(STAIRS_MODELS)

STAIRS_BLEND_FILE := staircase.blend

STAIRS_TEXTURE_FILES := \
	$(foreach suf, $(STAIRS_TEXTURES), $(TEX_BAKED)/stairs_$(suf).png) \
	$(foreach suf, $(WALL_TEXTURES), $(TEX_BAKED)/wall_$(suf).png) \
	$(foreach suf, $(METAL_TEXTURES), $(TEX_BAKED)/metal_$(suf).png) \

STAIRS_BASIS_FILES := \
	$(foreach suf, $(STAIRS_TEXTURES), $(TEX_BASIS)/stairs_$(suf).basis) \
	$(foreach suf, $(WALL_TEXTURES), $(TEX_BASIS)/wall_$(suf).basis) \
	$(foreach suf, $(METAL_TEXTURES), $(TEX_BASIS)/metal_$(suf).basis) \

STAIRS_MODEL_FILES := $(foreach mod, $(STAIRS_MODELS), models/$(mod).iqm)

TEXTURE_FILES := $(STAIRS_TEXTURE_FILES) $(TEX_BAKED)/envmap.png
BASIS_FILES   := $(STAIRS_BASIS_FILES) $(TEX_BASIS)/envmap.basis
MODEL_FILES   := $(STAIRS_MODEL_FILES)

MKBASIS_ARGS :=

all: $(MODEL_FILES) $(BASIS_FILES)

$(STAIRS_TEXTURE_FILES) $(STAIRS_MODEL_FILES) &: $(STAIRS_BLEND_FILE)
	blender --background $(STAIRS_BLEND_FILE) -P scripts/export_models.py

$(TEX_BAKED)/envmap.png: $(STAIRS_BLEND_FILE)
	blender --background $(STAIRS_BLEND_FILE) -P scripts/export_envmap.py

$(TEX_BASIS)/%_normal.basis: $(TEX_BAKED)/%_normal.png
	mkbasis $< --normal $(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/%_diffuse.basis: $(TEX_BAKED)/%_diffuse.png
	mkbasis $< --rgb \
		--preprocess-late ' -colorspace RGB -filter lanczos -resize 50% -colorspace sRGB ' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/%_ambient.basis: $(TEX_BAKED)/%_ambient.png
	mkbasis $< --rgb $(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/%_roughness.basis: $(TEX_BAKED)/%_roughness.png
	mkbasis $< --r --linear \
		--preprocess-late ' -filter catrom -resize 50% ' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/%_depth.basis: $(TEX_BAKED)/%_depth.png
	mkbasis $< --r --linear \
		--preprocess-late ' -filter catrom -resize 50% ' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/metal_ao.basis: $(TEX_BAKED)/metal_ao.png
	mkbasis $< --r --linear \
		--preprocess-late ' -brightness-contrast 50,25 -filter gaussian -resize 50% ' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/%_ao.basis: $(TEX_BAKED)/%_ao.png
	mkbasis $< --r --linear \
		--preprocess-late ' -filter gaussian -resize 50% ' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/envmap.basis: $(TEX_BAKED)/envmap.png
	mkbasis $< --rgb --equirect-cubemap $(MKBASIS_ARGS) -o $@

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
