
GROUND_TEXTURES         := diffuse normal ambient ao roughness
ROCKS_TEXTURES          := diffuse normal ambient ao roughness
BRANCH_TEXTURES         := diffuse normal ambient ao
LEAVES_TEXTURES         := diffuse normal ambient ao

TEXTURE_PATH := $(PREFIX)gfx/stage2/
MODEL_PATH := $(PREFIX)models/stage2/

TEX_BAKED := textures/baked
TEX_BASIS := textures/basis

PATH_BLEND_FILE := path.blend
PATH_MODELS := ground grass rocks

PATH_TEXTURE_FILES := \
	$(foreach suf, $(ROCKS_TEXTURES), $(TEX_BAKED)/rocks_$(suf).png) \
	$(foreach suf, $(GROUND_TEXTURES), $(TEX_BAKED)/ground_$(suf).png) \
	$(TEX_BAKED)/ground_alpha.png \

PATH_BASIS_FILES := \
	$(foreach suf, $(GROUND_TEXTURES), $(TEX_BASIS)/ground_$(suf).basis) \
	$(foreach suf, $(ROCKS_TEXTURES), $(TEX_BASIS)/rocks_$(suf).basis) \

PATH_MODEL_FILES := $(foreach mod, $(PATH_MODELS), models/$(mod).iqm)

BRANCH_BLEND_FILE := branch.blend
BRANCH_MODELS := branch leaves

BRANCH_TEXTURE_FILES := \
	$(foreach suf, $(BRANCH_TEXTURES), $(TEX_BAKED)/branch_$(suf).png) \
	$(foreach suf, $(LEAVES_TEXTURES), $(TEX_BAKED)/leaves_$(suf).png) \
	$(TEX_BAKED)/leaves_alpha.png \

BRANCH_BASIS_FILES := \
	$(foreach suf, $(BRANCH_TEXTURES), $(TEX_BASIS)/branch_$(suf).basis) \
	$(foreach suf, $(LEAVES_TEXTURES), $(TEX_BASIS)/leaves_$(suf).basis) \

BRANCH_MODEL_FILES := $(foreach mod, $(BRANCH_MODELS), models/$(mod).iqm)

BRANCH_INPUT_TEXTURES := textures/leaf_diffuse.png textures/leaf_normal.png

LAKEFLOOR_BASEDIR := ../mansion/textures/gravel

LAKEFLOOR_DIFFUSE := $(LAKEFLOOR_BASEDIR)/color.png
LAKEFLOOR_DIFFUSE_BASIS := $(TEX_BASIS)/lakefloor_diffuse.basis

LAKEFLOOR_NORMAL := $(LAKEFLOOR_BASEDIR)/normal.png
LAKEFLOOR_NORMAL_BASIS := $(TEX_BASIS)/lakefloor_normal.basis

LAKEFLOOR_DEPTH := $(LAKEFLOOR_BASEDIR)/depth.png
LAKEFLOOR_DEPTH_BASIS := $(TEX_BASIS)/lakefloor_depth.basis

LAKEFLOOR_BASIS_FILES := $(LAKEFLOOR_DIFFUSE_BASIS) $(LAKEFLOOR_NORMAL_BASIS) $(LAKEFLOOR_DEPTH_BASIS)

TEXTURE_FILES := $(PATH_TEXTURE_FILES) $(BRANCH_TEXTURE_FILES)
BASIS_FILES   := $(PATH_BASIS_FILES) $(BRANCH_BASIS_FILES) $(LAKEFLOOR_BASIS_FILES)
MODEL_FILES   := $(PATH_MODEL_FILES) $(BRANCH_MODEL_FILES)

MKBASIS_ARGS :=

all: $(MODEL_FILES) $(BASIS_FILES)

$(PATH_TEXTURE_FILES) $(PATH_MODEL_FILES) &: $(PATH_BLEND_FILE)
	blender --background $(PATH_BLEND_FILE) -P scripts/export_models.py
	
$(BRANCH_TEXTURE_FILES) $(BRANCH_MODEL_FILES) &: $(BRANCH_BLEND_FILE) $(BRANCH_INPUT_TEXTURES)
	blender --background $(BRANCH_BLEND_FILE) -P scripts/export_branch.py

$(LAKEFLOOR_DIFFUSE_BASIS): $(LAKEFLOOR_DIFFUSE)
	mkbasis $< \
		--rgb \
		--preprocess-late ' -colorspace RGB -filter lanczos -resize 1024x -colorspace sRGB ' \
		$(MKBASIS_ARGS) -o $@

$(LAKEFLOOR_NORMAL_BASIS): $(LAKEFLOOR_NORMAL)
	mkbasis $< \
		--normal \
		--preprocess-late ' -filter lanczos -resize 1024x ' \
		$(MKBASIS_ARGS) -o $@

$(LAKEFLOOR_DEPTH_BASIS): $(LAKEFLOOR_DEPTH)
	mkbasis $< \
		--r \
		--linear \
		--preprocess ' -filter catrom -resize 512x -set colorspace RGB -alpha extract -auto-level -negate ' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/ground_normal.basis: $(TEX_BAKED)/ground_normal.png $(TEX_BAKED)/ground_alpha.png
	mkbasis $(TEX_BAKED)/ground_normal.png \
		--normal \
		--external-alpha-path $(TEX_BAKED)/ground_alpha.png \
		--blend-background '#7f7fff' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/ground_diffuse.basis: $(TEX_BAKED)/ground_diffuse.png $(TEX_BAKED)/ground_alpha.png
	mkbasis $(TEX_BAKED)/ground_diffuse.png \
		--rgba \
		--external-alpha-path $(TEX_BAKED)/ground_alpha.png \
		--multiply-alpha \
		--multiply-alpha-blend-background '#64853e' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/ground_ambient.basis: $(TEX_BAKED)/ground_ambient.png $(TEX_BAKED)/ground_alpha.png
	mkbasis $(TEX_BAKED)/ground_ambient.png \
		--rgb \
		--external-alpha-path $(TEX_BAKED)/ground_alpha.png \
		--blend-background '#64853e' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/ground_ao.basis: $(TEX_BAKED)/ground_ao.png $(TEX_BAKED)/ground_alpha.png
	mkbasis $(TEX_BAKED)/ground_ao.png \
		--r \
		--linear \
		--external-alpha-path $(TEX_BAKED)/ground_alpha.png \
		--blend-background '#7f7f7f' \
		--preprocess-late ' -filter gaussian -resize 50% ' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/leaves_diffuse.basis: $(TEX_BAKED)/leaves_diffuse.png $(TEX_BAKED)/leaves_alpha.png
	mkbasis $(TEX_BAKED)/leaves_diffuse.png \
		--rgba \
		--external-alpha-path $(TEX_BAKED)/leaves_alpha.png \
		--multiply-alpha \
		--multiply-alpha-blend-background '#ff571d' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/leaves_ambient.basis: $(TEX_BAKED)/leaves_ambient.png $(TEX_BAKED)/leaves_alpha.png
	mkbasis $(TEX_BAKED)/leaves_ambient.png \
		--rgb \
		--external-alpha-path $(TEX_BAKED)/leaves_alpha.png \
		--blend-background '#ff571d' \
		$(MKBASIS_ARGS) -o $@

$(TEX_BASIS)/leaves_ao.basis: $(TEX_BAKED)/leaves_ao.png $(TEX_BAKED)/leaves_alpha.png
	mkbasis $(TEX_BAKED)/leaves_ao.png \
		--r \
		--linear \
		--external-alpha-path $(TEX_BAKED)/leaves_alpha.png \
		--blend-background '#7f7f7f' \
		--preprocess-late ' -filter gaussian -resize 50% ' \
		$(MKBASIS_ARGS) -o $@

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

$(TEX_BASIS)/water_floor.basis: textures/water_floor.png
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

clean:
	rm -f $(BASIS_FILES) $(TEXTURE_FILES) $(MODEL_FILES)

.PHONY: install all
