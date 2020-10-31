#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

krita paper.kra --export --export-filename out-png/paper.png || exit $?
convert \
    -verbose \
    out-png/paper.png \
    -colorspace Lab \
    -filter RobidouxSharp \
    -resize x1200 \
    -colorspace sRGB \
    -gravity Center \
    -crop 1600x1200+0+0 \
    +repage \
    out-png/paper.png \
|| exit $?
mkbasis out-png/paper.png --no-srgb-sampling --incredibly-slow -o out-basis/paper.basis || exit $?
