
MANSION_TEXTURES  := diffuse normal ambient    roughness
GROUND_TEXTURES   := diffuse normal ambient    roughness depth

TEXTURE_PATH := $(PREFIX)gfx/stage4/
MODEL_PATH := $(PREFIX)models/stage4/

TEX_BAKED := textures/baked
TEX_BASIS := textures/basis

MANSION_MODELS := mansion ground
MANSION_BAKE_TEXTURES := $(MANSION_MODELS)

MANSION_BLEND_FILE := mansion.blend

MANSION_TEXTURE_FILES := \
	$(foreach suf, $(MANSION_TEXTURES), $(TEX_BAKED)/mansion_$(suf).png) \
	$(foreach suf, $(GROUND_TEXTURES), $(TEX_BAKED)/ground_$(suf).png) \

MANSION_BASIS_FILES := \
	$(foreach suf, $(MANSION_TEXTURES), $(TEX_BASIS)/mansion_$(suf).basis) \
	$(foreach suf, $(GROUND_TEXTURES), $(TEX_BASIS)/ground_$(suf).basis) \

MANSION_MODEL_FILES := $(foreach mod, $(MANSION_MODELS), models/$(mod).iqm)

TEXTURE_FILES := $(MANSION_TEXTURE_FILES)
BASIS_FILES   := $(MANSION_BASIS_FILES)
MODEL_FILES   := $(MANSION_MODEL_FILES)

MKBASIS_ARGS :=

all: $(MODEL_FILES) $(BASIS_FILES)

$(MANSION_TEXTURE_FILES) $(MANSION_MODEL_FILES) &: $(MANSION_BLEND_FILE)
	blender --background $(MANSION_BLEND_FILE) -P scripts/export_mansion.py

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

$(TEX_BASIS)/%_ao.basis: $(TEX_BAKED)/%_ao.png
	mkbasis $< --r --linear \
		--preprocess-late ' -filter gaussian -resize 50% ' \
		$(MKBASIS_ARGS) -o $@

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
