#!/usr/bin/env zsh

GLOBAL_ARGS="$@"
OUT="${OUT:-$PWD/_out_}"

SRGB_LINEAR_SAMPLING=(
    abstract_brown.webp
    marisa_bombbg.webp
    menu/mainmenubg.webp
    reimubg.webp
    stage1/cirnobg.webp
    stage2/spellbg1.webp
    stage2/spellbg2.webp
    stage3/spellbg1.webp
    stage3/spellbg2.webp
    stage3/wspellbg.webp
    stage3/wspellclouds.webp
    stage4/kurumibg1.webp
    stage5/spell_bg.webp
    stage5/tower.webp
    stage6/spellbg_chalk.webp
    stage6/spellbg_classic.webp
    stage6/spellbg_modern.webp
    stage6/towertop.webp
    stage6/towerwall.webp
    titletransition.webp
    youmu_bombbg1.webp
)

SRGB_LINEAR_SAMPLING_LQ=(
    stage6/spellbg_toe.webp
)

SRGB_LINEAR_SAMPLING_NO_MIPS=(
    loading.webp
    static.webp
)

SRGB_LINEAR_SAMPLING_NO_MIPS_LQ=(
    # stage6/spellbg_toe.webp
)

SRGBA_LINEAR_SAMPLING=(
    stage1/horizon.webp
    stage1/snowlayer.webp
    stage1/waterplants.webp
    stage4/kurumibg2.webp
    stage5/spell_clouds.webp
)

RGB=(
    powersurge_flow.webp
    stage5/noise.png
)

GRAY=(
    cell_noise.webp
    gaplight.png
    runes.webp
    stage3/wspellswarm.webp
)

GRAY_ALPHA=(
    stage1/fog.webp
    stage5/spell_lightning.webp
)

FAIL=0

function make-basis-cmd {
    local dry_run=0

    if [[ "$1" = "--dry-run" ]]; then
        dry_run=1
        shift
    fi

    local input="$1"
    local output="$OUT/${input%.*}.basis"

    if [[ $OVERWRITE -le 0 && -e "$output" ]]; then
        [[ $dry_run -ge 1 ]] && echo "$output: file exists; call with OVERWRITE=1 to overwrite" 1>&2
        return 0
    fi

    if [[ $dry_run -ge 1 ]]; then
        mkdir -pv "$(dirname "$output")" || return 1
    fi

    shift

    if [[ $dry_run -ge 1 ]]; then
        mkbasis "$input" $@ $GLOBAL_ARGS --dry-run >/dev/null || return 1
    fi

    echo mkbasis "$input" $@ $GLOBAL_ARGS -o "$output"
}

function make-cmd-list {
    local err=0

    for x in $SRGB_LINEAR_SAMPLING; do
        make-basis-cmd "$@" $x --no-srgb-sampling
        let err+=$?
    done

    for x in $SRGB_LINEAR_SAMPLING_LQ; do
        make-basis-cmd "$@" $x --no-srgb-sampling --fast
        let err+=$?
    done

    for x in $SRGB_LINEAR_SAMPLING_NO_MIPS; do
        make-basis-cmd "$@" $x --no-srgb-sampling --no-mipmaps
        let err+=$?
    done

    for x in $SRGB_LINEAR_SAMPLING_NO_MIPS_LQ; do
        make-basis-cmd "$@" $x --no-srgb-sampling --no-mipmaps --fast
        let err+=$?
    done

    for x in $SRGBA_LINEAR_SAMPLING; do
        make-basis-cmd "$@" $x --rgba --no-srgb-sampling
        let err+=$?
    done

    for x in $RGB; do
        make-basis-cmd "$@" $x --linear
        let err+=$?
    done

    for x in $GRAY; do
        make-basis-cmd "$@" $x --linear --r
        let err+=$?
    done

    for x in $GRAY_ALPHA; do
        make-basis-cmd "$@" $x --linear --gray-alpha
        let err+=$?
    done

    return $([[ $err -eq 0 ]])
}

if [[ $LIST_ONLY -gt 0 ]]; then
    make-cmd-list --dry-run
    exit $?
fi

make-cmd-list --dry-run >/dev/null || exit $?
make-cmd-list | shuf | time parallel --bar --nice 17
