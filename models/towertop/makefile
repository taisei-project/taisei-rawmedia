
RIM_TEXTURES          := diffuse normal ambient ao roughness depth
SPIRES_TEXTURES       :=         normal         ao roughness
STAIRS_TEXTURES       := diffuse normal ambient ao roughness
TOWER_BOTTOM_TEXTURES := diffuse normal ambient ao roughness depth
TOWER_TEXTURES        := diffuse normal ambient ao roughness depth
FLOOR_TEXTURES        :=         normal         ao

TYPES := diffuse normal ambient roughness depth
TEXTURE_PATH := $(PREFIX)gfx/stage6/
MODEL_PATH := $(PREFIX)models/stage6/

TEX_BAKED := textures/baked
TEX_BASIS := textures/basis

SKY_BLEND_FILE := sky.blend
SKY_TEXTURE_FILE := textures/sky.hdr
SKY_BASIS_FILE := $(TEX_BASIS)/sky.basis.zst

TOWER_MODELS := tower stairs rim tower_bottom spires floor

TOWER_BLEND_FILE := towertop.blend

TOWER_TEXTURE_FILES := \
	$(foreach suf, $(RIM_TEXTURES), $(TEX_BAKED)/rim_$(suf).png) \
	$(foreach suf, $(SPIRES_TEXTURES), $(TEX_BAKED)/spires_$(suf).png) \
	$(foreach suf, $(STAIRS_TEXTURES), $(TEX_BAKED)/stairs_$(suf).png) \
	$(foreach suf, $(TOWER_BOTTOM_TEXTURES), $(TEX_BAKED)/tower_bottom_$(suf).png) \
	$(foreach suf, $(TOWER_TEXTURES), $(TEX_BAKED)/tower_$(suf).png) \
	$(foreach suf, $(FLOOR_TEXTURES), $(TEX_BAKED)/floor_$(suf).png) \

TOWER_BASIS_FILES := \
	$(foreach suf, $(RIM_TEXTURES), $(TEX_BASIS)/rim_$(suf).basis) \
	$(foreach suf, $(SPIRES_TEXTURES), $(TEX_BASIS)/spires_$(suf).basis) \
	$(foreach suf, $(STAIRS_TEXTURES), $(TEX_BASIS)/stairs_$(suf).basis) \
	$(foreach suf, $(TOWER_BOTTOM_TEXTURES), $(TEX_BASIS)/tower_bottom_$(suf).basis) \
	$(foreach suf, $(TOWER_TEXTURES), $(TEX_BASIS)/tower_$(suf).basis) \
	$(foreach suf, $(FLOOR_TEXTURES), $(TEX_BASIS)/floor_$(suf).basis) \

TOWER_MODEL_FILES := $(foreach mod, $(TOWER_MODELS), models/$(mod).iqm)

TEXTURE_FILES := $(TOWER_TEXTURE_FILES)
BASIS_FILES   := $(TOWER_BASIS_FILES) $(SKY_BASIS_FILE)
MODEL_FILES   := $(TOWER_MODEL_FILES) models/calabi-yau-quintic.iqm

MKBASIS_ARGS :=

all: $(MODEL_FILES) $(BASIS_FILES)

$(SKY_TEXTURE_FILE) &: $(SKY_BLEND_FILE)
	blender $(SKY_BLEND_FILE) --background --python scripts/render_sky.py

# Do not question these incantations. You will not have a good time.

$(SKY_BASIS_FILE): $(SKY_TEXTURE_FILE)
	mkbasis $< --uastc --incredibly-slow --rgb --equirect-cubemap \
		--preprocess ' -colorspace sRGB ' \
		$(MKBASIS_ARGS) -o $@

$(TOWER_TEXTURE_FILES) $(TOWER_MODEL_FILES) &: $(TOWER_BLEND_FILE) $(SKY_TEXTURE_FILE)
	blender $(TOWER_BLEND_FILE) --background --python scripts/export_models.py

models/calabi-yau-quintic.iqm: calabi-yau-quintic.blend
	blender calabi-yau-quintic.blend --python scripts/calabi-yau-quintic.py

$(TEX_BASIS)/%_normal.basis: $(TEX_BAKED)/%_normal.png
	mkbasis $< --normal --incredibly-slow $(MKBASIS_ARGS) -o $@

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
		--preprocess-late ' -filter catrom -resize 50% -normalize ' \
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

clean:
	rm -f $(BASIS_FILES) $(MODEL_FILES)

.PHONY: install all
