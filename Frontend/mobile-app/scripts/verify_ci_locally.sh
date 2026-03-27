#!/bin/bash
# Local CI verification script for monorepo structure

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

cd "$PROJECT_ROOT"

echo "--- Running Flutter Pub Get ---"
flutter pub get

echo "--- Running Flutter Analyze ---"
flutter analyze

echo "--- Running Flutter Test ---"
flutter test

echo "--- Running Flutter Build APK (Release) ---"
# Note: This might fail if signing is not configured locally, 
# but it verifies the build process.
flutter build apk --release
