#!/bin/sh
# Build the Figma plugin(s) for this app. Run: sh "<App>/script/build.sh"
set -e
cd "$(dirname "$0")/../.."   # repo root (adjust depth if your layout differs)
python3 tools/build-plugin.py --src "<App>/assets/v1" --plugin "<App>/figma/v1"
# v2 (reskin) — uncomment after Plan 2:
# python3 tools/build-plugin.py --src "<App>/assets/v2" --plugin "<App>/figma/v2"
