#!/bin/sh
# Build the Figma plugin(s) for Funny Face. Run: sh "Funny Face/script/build.sh"
set -e
APP="$(cd "$(dirname "$0")/.." && pwd)"     # <repo>/Funny Face
REPO="$(dirname "$APP")"                     # <repo> = App 6
python3 "$REPO/tools/build-plugin.py" --src "$APP/assets/v1" --plugin "$APP/figma/v1"
# v2 (reskin) — bật sau khi chạy Plan 2:
python3 "$REPO/tools/build-plugin.py" --src "$APP/assets/v2" --plugin "$APP/figma/v2"
