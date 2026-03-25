
GROUND_TEXTURES := ambient ao diffuse normal roughness
LEAVES_TEXTURES := ambient ao diffuse normal roughness
ROCKS_TEXTURES  := ambient ao diffuse normal roughness
TREES_TEXTURES  := ambient ao diffuse normal roughness

TEXTURE_PATH := $(PREFIX)/gfx/stage3/
MODEL_PATH := $(PREFIX)/models/stage3/

TEX_BAKED := textures/baked
TEX_BASIS := textures/basis

MOUNTAIN_MODELS := ground leaves rocks trees
MOUNTAIN_BAKE_TEXTURES := $(MOUNTAIN_MODELS)

MOUNTAIN_BLEND_FILE := mountain.blend

MOUNTAIN_TEXTURE_FILES := \
	$(foreach suf, $(GROUND_TEXTURES), $(TEX_BAKED)/ground_$(suf).png) \
	$(foreach suf, $(LEAVES_TEXTURES), $(TEX_BAKED)/leaves_$(suf).png) \
	$(TEX_BAKED)/leaves_alpha.png \
	$(foreach suf, $(ROCKS_TEXTURES), $(TEX_BAKED)/rocks_$(suf).png) \
	$(foreach suf, $(TREES_TEXTURES), $(TEX_BAKED)/trees_$(suf).png) \
	
MOUNTAIN_BASIS_FILES := \
	$(foreach suf, $(GROUND_TEXTURES), $(TEX_BASIS)/ground_$(suf).basis) \
	$(foreach suf, $(LEAVES_TEXTURES), $(TEX_BASIS)/leaves_$(suf).basis) \
	$(foreach suf, $(ROCKS_TEXTURES), $(TEX_BASIS)/rocks_$(suf).basis) \
	$(foreach suf, $(TREES_TEXTURES), $(TEX_BASIS)/trees_$(suf).basis) \
	$(TEX_BASIS)/envmap.basis \

MOUNTAIN_MODEL_FILES := $(foreach mod, $(MOUNTAIN_MODELS), models/$(mod).iqm)

LEAF_TEXTURES = textures/leaf.png textures/leaf_normal/Image0001.png textures/leaf_uv/Image0001.png
LEAF_BLEND_FILE := leaf_texture.blend

INPUT_TEXTURES := textures/veins.png

MKBASIS_ARGS :=

all: $(MOUNTAIN_MODEL_FILES) $(MOUNTAIN_BASIS_FILES)


$(LEAF_TEXTURES) &: $(LEAF_BLEND_FILE) $(INPUT_TEXTURES)
	blender $(LEAF_BLEND_FILE) --background --python scripts/render_leaftex.py


$(MOUNTAIN_TEXTURE_FILES) $(MOUNTAIN_MODEL_FILES) &: $(MOUNTAIN_BLEND_FILE) $(LEAF_TEXTURES) $(INPUT_TEXTURES)
	blender --background $(MOUNTAIN_BLEND_FILE) --python scripts/export_models.py

textures/leaves_composite_roughness.png: textures/leaves_baked_roughness.png textures/leaves_alpha_.png
	convert textures/leaves_baked_roughness.png \( textures/leaves_alpha_.png -colorspace gray -alpha off -morphology Erode disk:1 \) -compose copy-opacity -composite textures/leaves_composite_roughness.png

textures/leaves_roughness.basis: textures/leaves_composite_roughness.png
	mkbasis $< --gray-alpha --linear --no-multiply-alpha -o $@

$(TEX_BASIS)/leaves_roughness.basis: $(TEX_BAKED)/leaves_roughness.png $(TEX_BAKED)/leaves_alpha.png
	mkbasis $(TEX_BAKED)/leaves_roughness.png --gray-alpha --linear \
		--external-alpha-path $(TEX_BAKED)/leaves_alpha.png \
		--preprocess-late ' -filter catrom -resize 50% ' \
		$(MKBASIS_ARGS) -o $@
	
$(TEX_BASIS)/leaves_normal.basis: $(TEX_BAKED)/leaves_normal.png $(TEX_BAKED)/leaves_alpha.png
	mkbasis $(TEX_BAKED)/leaves_normal.png --normal \
		--external-alpha-path $(TEX_BAKED)/leaves_alpha.png \
		--blend-background '#7f7fff' \
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

$(TEX_BASIS)/envmap.basis: textures/belfast_sunset_puresky_4k.hdr
	mkbasis $< --rgb --equirect-cubemap -o $@
	
install: $(MODEL_FILES) $(BASIS_FILES)
	mkdir -p $(TEXTURE_PATH)
	mkdir -p $(MODEL_PATH)
	for f in $(MOUNTAIN_BASIS_FILES); do \
		cp $$f $(TEXTURE_PATH)/$$(basename $$f); \
	done
	for f in $(MOUNTAIN_MODEL_FILES); do \
		cp $$f $(MODEL_PATH)/$$(basename $$f); \
	done
		
.PHONY: install all
