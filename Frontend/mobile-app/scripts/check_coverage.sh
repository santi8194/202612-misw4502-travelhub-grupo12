#!/bin/bash

# Target coverage percentage
TARGET_PERCENTAGE=80

# File to check
LCOV_FILE="coverage/lcov.info"

if [ ! -f "$LCOV_FILE" ]; then
  echo "Error: $LCOV_FILE not found. Run 'flutter test --coverage' first."
  exit 1
fi

# Filter out non-core files using a temporary file
# Exclude: lib/main.dart, lib/l10n/*
TEMP_LCOV="coverage/lcov_filtered.info"

# Simple way to filter lcov.info if lcov tool is not available:
# We'll use a small awk script to filter out blocks we don't want.
awk -v exclude="lib/main.dart|lib/l10n/" '
  BEGIN { RS="SF:"; FS="\n"; ORS="" }
  NR==1 { print $0; next }
  $1 !~ exclude { print "SF:" $0 }
' "$LCOV_FILE" > "$TEMP_LCOV"

# Calculate total lines found (LF) and lines hit (LH)
LF=$(grep "^LF:" "$TEMP_LCOV" | cut -d: -f2 | awk '{s+=$1} END {print s}')
LH=$(grep "^LH:" "$TEMP_LCOV" | cut -d: -f2 | awk '{s+=$1} END {print s}')

if [ -z "$LF" ] || [ "$LF" -eq 0 ]; then
  echo "Error: No coverage data found in $TEMP_LCOV."
  exit 1
fi

# Calculate percentage
PERCENTAGE=$(awk "BEGIN {print ($LH / $LF) * 100}")

echo "---------------------------------------------------------"
echo "Core Logic Coverage Results:"
echo "Lines Found: $LF"
echo "Lines Hit  : $LH"
echo "Percentage : $PERCENTAGE%"
echo "Target     : $TARGET_PERCENTAGE%"
echo "---------------------------------------------------------"

if (( $(echo "$PERCENTAGE < $TARGET_PERCENTAGE" | bc -l) )); then
  echo "FAILED: Coverage is below $TARGET_PERCENTAGE%"
  exit 1
else
  echo "PASSED: Coverage is above $TARGET_PERCENTAGE%"
  exit 0
fi
