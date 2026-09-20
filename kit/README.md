# Gen-Figma Kit — portable toolset for Plan 1 & Plan 2

Copy `tools/` to your repo root and the `templates/` files into `<App>/{figma/v1,script}/`, then
follow `../Figma version 1/plan-1-*.md`. Everything here is proven and app-agnostic.

## Prerequisites (install once)
| Tool | Purpose | Check |
|---|---|---|
| `apktool` | decode res/ (layout, values, manifest) | `apktool --version` |
| `jadx` | decompile sources/ (java/kotlin) + resources | `jadx --version` |
| `node` | run build/verify/capture (Figma-mock) | `node -v` |
| `python3` + Pillow | asset export, RC fetch, arsc, preview render | `python3 -c "import PIL"` |
| Figma **desktop** | run the plugin (web can't run dev plugins) | — |

## tools/ (shared, copy to repo root `tools/`)
| File | Does |
|---|---|
| `build-plugin.py` | scan `assets/vN` → base64 → `assets.js`/`icons.js` → concat `code.js` → `plugin.js` → verify |
| `verify.js` + `figma-mock.js` | run the plugin in a fake Figma API: missing-asset / overlap / empty-text / bad-bytes |
| `vd2svg.py` | VectorDrawable `.xml` → SVG |
| `resolve-layout.py` | print a layout tree with `@string/@color/@dimen/@drawable` resolved to real values |
| `resolve-arsc.py` | resolve a resource id → file path from `resources.arsc` (when `public.xml` drops a name); flags split-APK entries |
| `fetch-remote-config.py` | pull Firebase Remote Config using the APK's `google_api_key`+`google_app_id` (asset token + remote lists) |

## templates/ (per-app, copy into `<App>/` and edit)
| File | Goes to | Edit |
|---|---|---|
| `code.js` | `<App>/figma/v1/` | fill `C` (measured colors), `FONTS` (map ttf→Figma family), write one `screen()`/`dialog()` per screen+state |
| `manifest.json` | `<App>/figma/v1/` | name + id |
| `build.sh` | `<App>/script/` | app path |
| `export-assets.py` | `<App>/script/` | `BITMAPS`/`VECTORS`/`PNG_ICONS` name lists (from Phase 2) |
| `download-remote.py` | `<App>/script/` | `BASE` (CDN from code) + `JOBS` (image_url lists) — only if content is remote |
| `capture-scene.js` | `<App>/script/` | none (generic) — records the built scene → `scene.json` |
| `render-preview.py` | `<App>/script/` | `FONT_MAP` (Figma family → APK ttf) — renders `scene.json` → PNG with real fonts |
| `make-v2.py` | `<App>/script/` | the token/radius/bg swaps for the reskin (Plan 2) |

## Fast path (per new app)
```
# 0. decode
mkdir -p "<App>"/{apk,decompiled,assets,figma,script}
mv app.apk "<App>/apk/"
apktool d "<App>/apk/app.apk" -o "<App>/decompiled/resources_tmp"   # or jadx for both
jadx -d "<App>/decompiled" "<App>/apk/app.apk" --no-debug-info
# 1. recon
cat "<App>/decompiled/resources/res/navigation/"*.xml            # screen map
python3 tools/resolve-layout.py "<App>/decompiled/resources/res" "<App>/.../fragment_x.xml"
# (remote?) python3 tools/fetch-remote-config.py --res "<App>/decompiled/resources/res"
# 2. copy templates, fill code.js + export-assets lists, then:
python3 "<App>/script/export-assets.py"
sh      "<App>/script/build.sh"                                  # build + structural verify
node    "<App>/script/capture-scene.js" "<App>/figma/v1/plugin.js" > scene.json
python3 "<App>/script/render-preview.py"                          # self-check (from code, not phone)
```

## Notes
- Never commit tokens (RC/PAT). `fetch-remote-config.py` saves to `/tmp/rc.json`.
- A resource id that `resolve-arsc.py` reports NULL is in a **split APK** — get the base+splits
  (`.apks`/`.xapk`, or `bundletool build-apks`) and merge, then retry.
