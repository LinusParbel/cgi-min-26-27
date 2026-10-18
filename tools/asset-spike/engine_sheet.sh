#!/usr/bin/env bash
# Merge SpikeViewer screenshots <prefix>_*.png into ONE image (fewer images to read).
# Usage: engine_sheet.sh <prefix> <out.png> [tile_px=400]
set -eu
PREFIX="$1"; OUT="$2"; T="${3:-400}"
FF="${FFMPEG:-ffmpeg}"; files=("${PREFIX}"_*.png); args=(); filt=""; i=0
for f in "${files[@]}"; do args+=(-i "$f"); filt+="[$i]scale=$T:$T[v$i];"; i=$((i+1)); done
for ((j=0;j<i;j++)); do filt+="[v$j]"; done
"$FF" -y -loglevel error "${args[@]}" -filter_complex "${filt}hstack=$i" "$OUT"
