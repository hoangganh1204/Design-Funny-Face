# Plan 1 — APK folder → Figma v1 (code-first, zero-omission)

> A self-contained procedure to rebuild any Android app as a Figma plugin from its APK.
> Vietnamese version: `plan-1-apk-to-figma-v1.vi.md`.
>
> **Core stance: the decompiled code is the single source of truth. Read it exhaustively —
> absolutely no errors, no omissions. Screenshots are an optional cross-check, never the method.**

## Goal
From a folder that contains one `.apk`, produce a **Figma plugin** that reconstructs the app 1:1
(exact dp sizes, real text, real assets, every screen, every state) — with correctness **derived and
audited from the code itself**, not from eyeballing a phone.

## Prime directives (priority order)
1. **Code is authoritative.** Every number/color/text/asset/behaviour traces to a decompiled file+line
   or a resolved resource. Read the *whole* relevant file — never skim, never infer from a name. When
   unclear, **resolve** it (Appendix C), don't guess.
2. **Zero omission.** Every nav destination, dialog, runtime state, and list item is derived from code
   and present. Coverage is **mechanically audited against the code** (Phase 6).
3. **Obfuscated/stripped ⇒ resolve, don't approximate.** A code field → R value → `public.xml`/
   `resources.arsc` → real name. Never substitute a guess for an unresolved value; mark and resolve it.
4. **Screenshots are a bonus, not the mechanism.** Correctness comes from complete code reading +
   resolved layouts + the coverage audit. A rendered self-preview (from *our* build) is the sanity
   glance; a client screenshot, if available, is an extra cross-check — the plan must be correct
   **without** one.

Reference canvas: **360×800 dp** (`sdp`==dp, `ssp`==sp in the base bucket). No status bar (that is
system UI, not the app).

## Kit & prerequisites
Use the portable `kit/` next to this plan — it has the proven, app-agnostic tools + templates so you
don't rebuild them per app (see `kit/README.md`). Install once: **apktool, jadx, node, python3+Pillow,
Figma desktop**. Shared tools → repo `tools/`: `build-plugin.py · verify.js + figma-mock.js · vd2svg.py
· resolve-layout.py · resolve-arsc.py · fetch-remote-config.py`. Per-app templates → `<App>/{figma/v1,
script}/`: `code.js` (the framework — helpers + `screen()/dialog()` registries; write one builder per
screen/state), `manifest.json · build.sh · export-assets.py · download-remote.py · capture-scene.js ·
render-preview.py · make-v2.py`.

---

## Phase 0 — Setup & decode
```
apktool d app.apk -o out        # res/ (layout, drawable, values) + AndroidManifest.xml + *.properties
jadx -d out app.apk             # sources/ (Java/Kotlin) to read runtime; jadx also decodes resources
grep -oE 'package="[^"]*"|versionName="[^"]*"|versionCode="[^"]*"' out/.../AndroidManifest.xml
```
- Move apk → `<App>/apk/`, decode → `<App>/decompiled/{resources,sources}`.
- **Split APKs / bundles first.** If you got a `.apks`/`.xapk`/`.apkm` or a base + `config.*`/`split_*`
  APKs, **merge them before decoding** (`bundletool build-apks --mode=universal`, or unzip the bundle
  and merge splits) — otherwise density buckets, some drawables and libs are missing, and resource ids
  will resolve to NULL. Symptom later: `resolve-arsc.py` reports an id NULL "likely split APK".
- **Assess APK age** (zip timestamps are normalized to `1981`, useless). Proxy: read
  `play-services-ads.properties` / other lib `.properties` (SDK version ≈ build era); scan
  `res/drawable` for seasonal names. State to the client "built ~T, the live app may differ" — a data
  point, not a licence to approximate.

## Phase 1 — Build the exact screen map from code
- **Manifest = list of Activities.** Single-activity + Navigation Component is common → read
  `res/navigation/*.xml` (startDestination + every destination = a Fragment). ⚠ `startDestination`
  in XML may be overridden by code in the launcher Activity — verify. The nav graph is the
  **authoritative set** every screen must reconcile against. Also note any 2nd Activity (overlays,
  transparent effect activities).
- **Design tokens** from `res/values/`: `colors.xml`, `styles.xml` (typography), `dimens.xml`.
  - ⚠ Don't trust `colorPrimary` — a template app's real brand color is usually **hardcoded in
    layouts**; measure frequency: `grep -ohE '#[0-9a-fA-F]{6,8}' res/layout/{fragment,item,activity}_*.xml | sort | uniq -c | sort -rn`, then confirm where code sets it.
  - ⚠ **Dark theme is often fake:** an empty `values-night/colors.xml` + a `DayNight` parent ≠ real
    dark mode. Verify.
- **Fonts:** list `res/font/*.ttf` → map each to a Figma-available family (Google Fonts). Note which
  view uses which font (headings, digital readouts, stencil, etc.).
- **Resolve, never read raw.** For every layout, run `tools/resolve-layout.py <res> <layout.xml>` so
  `@dimen/@color/@string/@drawable` become real values. Any residual raw `@…`/`0x…` is a hole to fill
  (Phase 6 / Appendix C), not a value to invent.

## Phase 2 — Exhaustive runtime read (the heart of the plan)
Layout XML says what a screen *can* contain; **code decides what the user actually sees**. For **every**
fragment/activity in the nav graph, open and read **completely**: the Fragment/Activity, its
ViewBinding usage, its Adapter/Controller/ViewHolder, its ViewModel/repository, and every custom `View`
it inflates. Parallelize with one subagent per screen cluster — but each agent must produce a *complete*
spec, not a sketch. For each screen answer all six:

**A. Geometry** (from the resolved layout): every element `role · x/y dp · w/h dp · bg #hex · radius`;
text = `exact resolved string · size sp · font · color · align`. Nothing undocumented.

**B. Visibility** (from code): table `view | XML default | runtime setter | condition | RESULT`. Know
each helper (`show()/gone()/inv()`, and the *different* `show(v,bool)`/`visible(v,bool)` which can be
VISIBLE **or** GONE), the default branch, and every `if(state)/when(...)`. Trap: a view declared
`visible` may always be GONE; a view declared `invisible` may be the normal state.

**C. Lists** (exact, from code): how each list is built — `enum.values()`, hardcoded `listOf`, Epoxy
`buildModels`, Room DB, or remote JSON → **exact count + names + order**, *including code-inserted
items* (ad tiles, an "Add" tile, a trailing promo). `spanCount`/layoutManager may be set in code, not
XML. The design count must equal the code count (off-by-one = a missed inserted item).

**D. Hardcoded data** — copy verbatim, exact order: `grep -rn "arrayListOf\|listOf(\|enum class\|values()"`.
Worst error class: inventing N items when the code has M.

**E. Content source per view:** local drawable / remote URL / seasonal switch. Map model→field
(`@SerializedName`) so you know exactly which field feeds each image/text. Views with `src` may be
overridden by an image loader; many views have no `src` at all (set at runtime).

**F. Seasonal / A-B / remote-config branches:** build the **default branch first** (what most users
see). `grep -rn "RemoteConfig\|getLong(\|getBoolean(\|Variant\|ShowUIEvent"`; read
`res/xml/remote_config_defaults.xml`. A key absent from defaults returns `0/false/""`. Each season/
variant may have its own geometry for the same view.

**States — generate them all.** One Activity/layout usually has several runtime states; each state is
its **own frame**. Common axes to sweep: connectivity (off/connecting/connected/lost); permission
(granted/denied); data (empty/loading/data/error); package (free-with-ads / purchased-PRO); first-run
vs return (onboarding/consent only once, EU-only); feature toggles (icon swaps by flag). Prefer a
`buildX(f, state)` function and register one `screen()` per state so none is missed.

**Easy-to-miss — check each explicitly:**
- `res/menu/*.xml` inflated via `getMenuInflater()` → toolbar actions (Settings/Share/PRO) that are
  **not in the layout XML**.
- Custom views whose class name is `*View`/`*Layout` **not** under `android/androidx` draw their
  visible part in `onDraw()` (step dots, progress, indicators) — invisible in the layout tree. Open the
  class and read `onDraw`.
- Hidden `RecyclerView`s inside a layout (color picker, device list, language list, FAQ).
- Ripple/selector drawables wrapping the real image (`<ripple>`→`<item drawable="@mipmap/…">`).
- Backgrounds with a baked-in motif (a faint "?" or brush) — use the real image, don't hand-draw.

**Flags (state them, never fake them):** NativeAdView/banner = **AD SLOT**; Lottie/PAG/video =
**animation** (static in Figma, note the raw asset name); remote/API image = **runtime**; OS/SDK UI
(UMP/GDPR consent, In-App Review, cast/share sheet, permission dialogs) = **labelled placeholder**.

## Phase 3 — Real content when it is server-driven (still code-derived)
If the app pulls content/lists from a server/CDN, the APK alone won't match the live app — but the app's
own keys fetch the real data deterministically (this is code-derived, not eyeballing):
- Private CDN repo (raw host → 404 unauthenticated) → the token is in **Firebase Remote Config**. Fetch
  exactly like the app, using `google_api_key`+`google_app_id` from `res/values/strings.xml`:
  ```
  POST https://firebaseremoteconfig.googleapis.com/v1/projects/<PROJECT_NUMBER>/namespaces/firebase:fetch?key=<google_api_key>
  {"appId":"<google_app_id>","appInstanceId":"<any>"}
  ```
  → returns all remote params: asset token + every remote list (JSON). Download images with the token
  → convert to PNG.
- Confirm which **field** the code actually reads (`image_url` vs `preview_url`, `thumbnail` vs a newer
  variant) — trace it in the model/repository, don't pick the newest-looking file.
- **Security:** never commit the token (keep it in `/tmp`); a PAT expires → refetch RC.

## Phase 4 — Export assets (name = key, exact)
- **Bitmap** (`.webp/.png/.jpg/.gif`): pick the highest-density bucket; **convert WEBP/GIF → PNG**
  (Figma can't read WEBP; GIF → grab a representative frame). File name (no ext) = the code lookup key.
- **VectorDrawable** (`drawable/*.xml`) → **SVG** (`tools/vd2svg.py`, handles pathData/gradient/alpha
  `#AARRGGBB`/evenOdd/group transform). Extracting only PNGs loses all nav/settings icons — always
  convert vectors. Render-check an icon after converting.
- **Baked images** (dialog art, category tiles, launcher icon): use the **original bytes**, never redraw.
- **Uneven transparent margins**: source images with different padding look mismatched at the same box
  size → normalize (crop to subject bbox, then center so the subject fills the same fraction of the cell).
- **Launcher icon is adaptive**: 108dp canvas, **safe zone 72dp (66%)**, each device masks differently
  (circle/squircle/square). Export legacy 48→192px + round + adaptive foreground + background color +
  512 for store; subject must stay inside the safe zone.
- A referenced asset that resolves to a **stripped/split-APK id** → resolve via `resources.arsc`; if it
  genuinely lives in a split APK not present, record that fact (do not silently substitute).

## Phase 5 — Build the plugin (each layer traces to code)
Separate **assets** from **build code** so swapping an image never touches logic. Reuse the thin
declarative framework: `frame/rect/ellipse/text/img/svgNode/photo` helpers + `screen()/dialog()`
registries + a font loader + page layout. Every Figma layer must trace to one XML view or one code
instruction — if it can't, delete it (don't add captions that duplicate the frame name; use
`setPluginData` for notes).
```
python3 tools/build-plugin.py --src "<App>/assets/v1" --plugin "<App>/figma/v1"
# scans assets → base64 → assets.js/icons.js → concat with code.js → plugin.js → runs verify
```
- **Fonts:** load every mapped family; a missing style → fall back to Regular and **log** (Figma has
  **no auto-fallback** — non-Latin text in a Latin font renders **blank**; choose Noto Sans <script>
  per label content: Arabic/Thai/JP/KR/Cyrillic…).
- **Build first, place later:** some frames self-size taller than the base height (full grids, long
  lists) → measure the *real* height after building, then lay out rows and `f.resize(W, max(H, y+pad))`
  so tall content isn't clipped and rows don't overlap.
- **Compress embeds** (~2× display size): opaque → JPEG q≈80; alpha → quantized PNG. Keeps the plugin
  small without visible loss.
- **Vector icons in Figma** (`createNodeFromSvg`): badge text must be **paths** (not SVG `<text>`);
  clip facets to the shape; leave viewBox padding so icons don't touch the container edge.

## Phase 6 — Completeness audit (code-derived, NO screenshot needed)
This is where "no omission" is enforced mechanically, against the code:
1. **Destination coverage:** diff `nav_graph` destinations (+ 2nd activities) vs the `screen()`
   registry → **zero missing**. Every fragment/activity has ≥1 frame (more if multi-state).
2. **Resolve coverage:** re-run `resolve-layout` on every built layout → assert **no residual raw
   `@…`/`0x…`** in anything drawn. Each hole resolved via `public.xml`/`.arsc` or explicitly flagged.
3. **Count coverage:** for each list screen, `code-derived count == rendered count`. Off-by-one = a
   missed inserted item; fix.
4. **State coverage:** for each fragment, list its `setVisibility/when(state)` branches → each mapped
   to a frame. An unmapped branch = a missing screen.
5. **Asset audit** (`tools/verify.js` + `figma-mock.js`): every asset the code requests exists; every
   embedded asset is used or logged; no overlapping frames; no empty text. Run by *executing* the
   plugin in a fake Figma API (`sh <App>/script/build.sh`) — static string scans give false results
   for dynamically-built asset names.
6. **Structured self-review pass:** re-read each cluster asking only "what did I omit?" — a menu, a
   custom `onDraw`, a hidden RecyclerView, an unhandled state, an unverified field. Findings → fixes.
7. **Optional visual sanity** — render *our own* build with the real APK fonts (this renders from the
   code-derived scene; it is not a phone screenshot):
   ```
   node <App>/script/capture-scene.js <App>/figma/v1/plugin.js > scene.json
   python3 <App>/script/render-preview.py     # → contact sheets per page, real TTF fonts + real assets
   ```
   A client screenshot, if available, is an extra cross-check — but the audit above is what guarantees
   correctness. Figma dev plugins run on **desktop only**; run once → the file syncs to figma.com.

---

## Appendix A — Where the correct info lives (never guess these)
| Question | Authoritative source (NOT layout XML) |
|---|---|
| How many items does this screen show? | Controller/Adapter/enum in `sources/` |
| How many languages/categories? | Hardcoded list in the corresponding source file |
| Is this view visible? | `setVisibility` in the Fragment binding + the default branch |
| What color is this bg/button? | `colors.xml` + shape `drawable/*.xml`, prefer code override |
| Where does this image come from? | Runtime API/remote if any; else `res/drawable` |
| How many variants of this screen? | remote-config key + variant enum |
| Launcher icon sizes? | `mipmap-*/` (48→192px) + `mipmap-anydpi/ic_launcher.xml` (adaptive 108dp) |
| What kind of notification? | Read code: `Toast` ≠ `Dialog` ≠ `Snackbar` |
| Which layout does this list item use? | `getDefaultLayout()` / adapter `onCreateViewHolder` |

## Appendix B — Common traps (each has bitten a real build)
1. **Ad-SDK layouts mixed in** — `res/layout` includes SDK layouts (AppLovin/Mbridge/Google…). Keep
   only the app package's layouts.
2. **Wrong notification type** — don't assume "notice = dialog". No-internet is often a **Toast**.
   Read the code.
3. **Fake / dark-pattern screens** — build them exactly, but note them: a "choose favorite" that
   personalizes nothing; an IAP "sale" countdown that resets each open; a rating nudge that always
   points at 5 stars and funnels <5-star to in-app feedback, =5-star to the store.
4. **Non-Latin text renders blank** — Figma has no auto font-fallback (Appendix, Phase 5 fonts).
5. **Nav bar / tabs drawn that the app hides** — read `setVisibility` + the running variant.
6. **Missing list element** — count mismatch → find the code-inserted item.
7. **Wrong API image field** — download all variants, confirm the field the code reads.
8. **Wrong seasonal branch** — each season may move a view (different margins for the same XML).
9. **Frames overlapping** — build-first-place-later + the overlap test.
10. **Drawing extra card/label** — every layer must trace to XML/code; don't wrap an image that is
    already a full baked tile.
11. **Caption duplicating the frame name** — use `setPluginData`, don't add on-canvas text.
12. **Wrong item layout** — check the binding model's `getDefaultLayout()`.
13. **Trusting the APK is current** — assess age in Phase 0.
14. **Trusting `colorPrimary`** — measure real color frequency in layouts.
15. **Missing menu resource** — read `res/menu/*.xml`.
16. **Missing custom-view `onDraw`** — dots/bars drawn in code.
17. **Only the happy-path state built** — generate every state.
18. **System/SDK UI faked as an app screen** — UMP/GDPR, In-App Review, cast picker, share sheet,
    permission dialogs are OS/SDK; make a labelled placeholder, don't invent an app screen.
19. **Lottie/PAG rendered as if static art** — SVG-from-Lottie usually shatters; use a static brand
    asset or a hand-matched SVG + note "original is animated".
20. **Tall content clipped** — loops (device list, FAQ, N languages) exceed the base height → resize
    the frame after building.

## Appendix C — Obfuscated / stripped APK
- **Activities in the Manifest usually survive** obfuscation → start the screen map there, not from
  105 anonymous layouts.
- **Decode a resource id: code field → id → file.** `setContentView(A0.f3307a)` → find `f3307a =
  2131492892` in the R-holder → `0x7f0c001c` → `res/values/public.xml` `<public type="layout" …
  id="0x7f0c001c"/>` → the real layout file. Exact, not guessed.
- **Stripped from `public.xml`?** Resolve the id straight from `resources.arsc`:
  `python3 tools/resolve-arsc.py app.apk 0x7f08016f` → the real file path, or "NULL → likely split APK"
  (then merge splits per Phase 0 and retry). Also `--type drawable --dump` lists every id→path. Never
  substitute a guess for an unresolved value.
- Write/keep a `resolve-layout` that prints the element tree with `@string/@color/@dimen/@drawable`
  replaced by real values — reading obfuscated layouts without it is reading blind.

## Appendix D — Per-screen checklist
```
[ ] Read Fragment + adapter/controller (not only XML)
[ ] Visibility table: view | XML | runtime | condition | default
[ ] A/B variant + default branch; remote-config keys + value-when-unfetched
[ ] Exact list order incl. code-inserted items
[ ] Hardcoded data copied verbatim
[ ] Source of each image: local / API / seasonal
[ ] Runtime text & color overrides
[ ] Seasonal theme table (incl. per-season geometry)
[ ] Every runtime state listed, one frame each
[ ] Menu resource + custom-view onDraw checked
[ ] Build → asset audit + overlap test
[ ] Coverage audits (destination/resolve/count/state) pass
```

## Appendix E — Honesty about limits (state up-front)
Cannot be taken statically from the APK, and must be labelled as such: content from a server/API
(changeable anytime), other A/B branches (only the default is built), remote-config-driven states, the
exact app version on the client's device, animations (Lottie/PAG/video — static in Figma), OS/SDK UI.
Say it before the client finds it.

## Appendix F — Subagent spec-extraction prompt (Phase 2, per cluster)
Dispatch one agent per screen cluster with a prompt like this (fill `<>`), so each returns a *complete*
spec, not a sketch:
```
You extract EXACT UI specs from a decompiled Android APK to rebuild screens 1:1 in Figma.
ACCURACY IS EVERYTHING — never fabricate a number/color/text/asset; trace every value to a file.
Flag runtime/remote/animation/DB items you cannot resolve statically instead of guessing.
PATHS: RES=<...>/decompiled/resources/res  APP=<...>/sources/<pkg>
KEY TOOL (exact geometry): python3 tools/resolve-layout.py "<RES>" "<RES>/layout/<file>.xml"
Canvas 360×800 dp (sdp==dp). Report every size in dp.
CLUSTER = <name>. Layouts: <fragment_x.xml + item/dialog layouts>. Fragments: <XFragment.java + adapter + viewmodel>.
For EACH screen produce a precise element tree: every element role · x/y dp · w/h dp · bg #hex · radius;
text = exact resolved string · size sp · font(@font resolved) · color · align. Note paddings/margins.
RUNTIME (read the Fragment/adapter): default visibility (setVisibility/gone/show), code-set text/colors,
how lists are built + EXACT count/names/order (find the data source: enum/hardcoded/DB/remote JSON),
every runtime STATE (one per setVisibility/when branch). Flag NativeAdView=AD SLOT, Lottie/PAG/video=
animation, remote/API image=runtime, OS/SDK UI=placeholder. List every drawable asset name (mark .webp).
Write the full spec to <scratch>/specs/<cluster>.md; return a SHORT summary (counts, key dims, flags).
```
Then, because the expectation is zero-omission, run a **completeness critic** pass over the specs: a
second read that asks only "what did the extractor miss — a menu, a custom onDraw, a hidden RecyclerView,
an unhandled state, an unverified field?" Feed its findings back before building.

---

## OUTPUT — folder structure (per app; `tools/` shared at repo root)
```
<Repo root>/
├─ tools/                        # SHARED across apps
│   ├─ build-plugin.py           # assets → assets.js/icons.js → plugin.js → verify
│   ├─ verify.js + figma-mock.js # run plugin in a fake Figma API (structural checks)
│   ├─ vd2svg.py                 # VectorDrawable XML → SVG
│   └─ resolve-layout.py         # @string/@color/@dimen/@drawable → real values
└─ <App>/
    ├─ apk/<app>.apk
    ├─ decompiled/{resources,sources}   # resources=res+manifest+.properties; sources=java/kotlin
    ├─ assets/v1/                        # exported; FILE NAME (no ext) = code key
    │   ├─ 01-<group>/*.png   10-icons/*.svg   ...
    ├─ figma/v1/
    │   ├─ manifest.json  code.js  assets.js*  icons.js*  plugin.js*   (*=generated)
    ├─ script/
    │   ├─ export-assets.py  download-remote.py  capture-scene.js  render-preview.py  build.sh
    └─ README.md                         # screens + runtime caveats + how to run in Figma
```

## Definition of done
- Destination/resolve/count/state audits pass → provably nothing omitted or unresolved.
- Every Figma layer traces to a code/XML source; every flagged item is labelled, none invented.
- README states exactly what is runtime/remote/animation/SDK.
- A client screenshot, if later provided, reveals **nothing new** — the code already told us.
