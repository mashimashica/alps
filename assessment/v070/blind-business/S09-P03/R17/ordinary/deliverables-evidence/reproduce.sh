#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

python skill/operational-intervention-decision/scripts/analyze_packet.py \
  input/sources/shipment_cohorts.csv \
  input/sources/shift_operations.csv \
  --intervention-line Harbor \
  --control-line Ridge \
  --baseline-period baseline \
  --trial-period pilot \
  --planned-mix standard=0.75,complex=0.25 \
  --planned-orders-per-shift 800 \
  --shifts 20 \
  --hour-cap 68 \
  --exclude-operations-date 2026-07-31 \
  --avoidable-cost 48 \
  --hour-cost 32
