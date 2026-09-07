#!/usr/bin/env bash
set -euo pipefail

task_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$task_dir"

python skill/operational-intervention-decision/scripts/analyze_packet.py \
  --shipments input/sources/shipment_cohorts.csv \
  --operations input/sources/shift_operations.csv \
  --baseline-label baseline \
  --pilot-label pilot \
  --treated-line Harbor \
  --comparison-line Ridge \
  --full-shift-dates 2026-07-06,2026-07-07,2026-07-08,2026-07-20,2026-07-21,2026-07-22 \
  --planned-mix standard=0.75,complex=0.25 \
  --planned-orders-per-shift 800 \
  --planned-shifts 20 \
  --productive-hour-cap 68 \
  --hourly-cost 32 \
  --avoidable-event-cost 48 \
  > deliverables/numerical_basis.md

echo "Wrote deliverables/numerical_basis.md"
