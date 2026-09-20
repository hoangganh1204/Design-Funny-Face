# Plan 2 — Custom Figma v2 (reskin) from v1

> A self-contained procedure to derive a differentiated "v2" skin from an existing v1.
> Precondition: `<App>/figma/v1` + `<App>/assets/v1` already work (see Plan 1).
> Vietnamese version: `plan-2-reskin-v2.vi.md`.
> Kit: reuse `../kit/` (make-v2.py template, hue-rotate/duotone snippets, shared build tools).

## Goal
Produce `figma/v2` that reads as a **different app** while the **layout stays identical** to v1.
Only color / pattern / corner-radius change. This is a *reskin*, not a redesign.

## The rules (what may / may NOT change)
| MUST keep identical | MAY change (to differentiate) |
|---|---|
| Every position, coordinate, size, spacing | Brand color palette (hue-rotate the whole set by ONE fixed angle) |
| Layout order (**do NOT move Back↔Next**, do not reorder buttons) | Background tone (keep dark if content art needs dark — retint, don't invert) |
| Characteristic shapes (pill button, switch, step-dots, indicators) | Corner radius — bump exactly **one step** |
| Content/product photos (weapons, items, avatars, wallpapers, mascots, emoji, flags) | Brand-colored art (wordmark, brand icons, selection chrome) |
| Screen/dialog count & every state | Brand-colored card/frame "chrome" (item frames, row cards, tab bars) |

## Rule 1 — Color: rotate the whole brand palette by ONE angle
- **Sample the real brand color first.** A fixed angle applied to different base hues gives garbage
  (a warm navy rotated the same way as a warm orange goes muddy) — sample the actual tokens, then pick
  an angle that shifts the *whole* family coherently. The dark neutrals are handled in Rule 2.
- Compute the rotated hex for **every** brand token by the SAME angle:
  ```python
  import colorsys
  def rot(hex, deg):
      h,l,s = colorsys.rgb_to_hls(*[int(hex[i:i+2],16)/255 for i in (0,2,4)])
      return '%02x%02x%02x'%tuple(int(c*255) for c in colorsys.hls_to_rgb((h+deg/360)%1, l, s))
  # e.g. rot('ffcd6a', 150) → a cyan; apply the SAME 150 to gradients, CTAs, accents.
  ```
- Keep **functional colors** as-is — they carry meaning, not brand: error/countdown red, success
  green, decline red, links, and any third-party SDK widget color (e.g. a rate-SDK button).
- Readability: hue-rotation **preserves lightness**, so a light brand color stays light → black text on
  the CTA stays legible. Verify after rotating.

## Rule 2 — Background: retint, keep it dark (if content is dark)
- Product photos and dramatic art are usually **designed for a dark background**; a light bg clashes →
  keep it dark. (If the app is genuinely light-themed, shift within light tones instead.)
- Shift the neutral dark toward the new brand hue (e.g. near-black → a dark tint of the new hue), and
  the toolbar/cards likewise. Enough to read as "a different app", not enough to fight the photos.
- Retint the hardcoded dark box literals too (input fields, dialog card fill, detail backgrounds) — a
  neutral `#191919` box on a tinted screen betrays the reskin.

## Rule 3 — Corner radius: one step
- Bump the main CTA/tile/list radii by ~+4dp (e.g. button 10→14, tile 14→18, row 16→20).
- **Do not** change the characteristic silhouette (e.g. a pixel-button's face + black bottom edge +
  corner notch). One step, no more, or it becomes a different component.

## Rule 4 — Assets: recolor ONLY brand art, by the method that fits the asset
Three buckets — classify **each** asset, apply the right treatment:
1. **Content / product photos** (weapons, items, avatars, wallpapers, mascot, emoji, flags): **DO NOT
   touch.** Hue-rotating a multi-color photo yields wrong colors.
2. **Brand marks that ARE colored** (splash wordmark, colored progress bar, selected-state radio,
   pointer/hint): **hue-rotate by the same angle** as the palette (per-pixel HLS rotate, keep alpha).
3. **Brand "chrome" that is near-grey/metal** (item card frames, row cards, tab bars): hue-rotate
   does nothing on grey → **duotone** instead: map luminance → gradient(shadow=dark brand → highlight=
   light brand), preserving the metallic detail. Optional: a light **multiply overlay** in the new hue
   on large metal textures (e.g. a splash backdrop) for cohesion.

> The "chrome" layer is the one people forget: item frames / row cards stay grey while everything else
> changed → it looks half-reskinned. Recolor the frames too.

## Rule 5 — Design cohesion when reskinning (don't just recolor blindly)
- Buttons share 1–2 height tiers; a status/PRO tag is one consistent color throughout; feature icons
  are **different-but-harmonious** (sibling hues, not clashing); secondary/among lines are **dimmer**
  than the accent (a connector line < an indicator dot). Consistency beats a locally-pretty color.
- If the brief is a **"free" edition** rather than a color reskin, distinguish IAP from ads: remove
  Vip/PRO/upgrade/Remove-Ads, but **keep** ads (banner/native/reward) — that is the revenue. IAP ≠ ads
  ≠ cross-promo ≠ reward-ad.

## Rule 6 — Keep code + asset in sync (a `make-v2` script, not a hand-fork)
Do **not** hand-fork v1's `code.js`. Write `<App>/script/make-v2.py` that reads `figma/v1/code.js`,
applies the exact string swaps (brand tokens, radius, bg retints, page titles, header comment) and
writes `figma/v2/code.js`. Then any fix in v1 → re-run make-v2 → v2 stays consistent (identical layout
guaranteed, because only tokens change). Assets: `assets/v2/` = a copy of `assets/v1` + the hue-rotate/
duotone reskin applied to the classified brand set.

## Steps (recipe)
```
1. Sample the real brand color; pick the hue angle           → verify: black text still legible on CTA
2. assets/v2 = copy assets/v1; hue-rotate brand marks;       → verify: product photos byte-identical to
   duotone chrome frames; (opt) tint large metal textures       v1; brand marks + frames on new hue
3. Write make-v2.py: v1/code.js → v2/code.js (tokens,        → verify: node --check v2/code.js
   radius +1 step, bg retint, page titles, id/name)
4. build: build-plugin.py --src assets/v2 --plugin figma/v2  → verify: mock green; node count == v1
5. Visual self-check: capture-scene v2 + render-preview      → verify: same layout, new identity,
   (ASSETS_DIR=assets/v2)                                       product photos untouched, chrome on-theme
6. figma/v2/manifest.json: different id + name               → verify: runs on Figma desktop
```

## Common reskin traps (each has bitten a real build)
- Fixed hue angle on a different base hue → wrong color (warm→muddy). **Sample first**, then choose.
- Duotoning a photo → destroys it. Only duotone grey chrome, never product art.
- **Forgetting the chrome layer** — item frames/row cards left grey. Recolor them.
- Moving Back/Next or reordering buttons → it becomes "another app", not a reskin. Layout is frozen.
- Neutral hue rotation → wrong color: a fixed angle that suits one family turns another (navy→brown).
- Retinting `#000000`/`#ffffff`/scrims/shadows by mistake → only retint the *neutral dark surfaces*,
  never true black button text, true white, or overlay scrims.
- Bumping radius too much → loses the characteristic silhouette. One step only.
- Hand-forking code.js → v1 and v2 drift. Always regenerate v2 with make-v2.

## Definition of done
- v2 node count == v1 (layout identical); Back/Next and all positions unchanged.
- Palette + background + chrome frames on the new theme; product photos byte-identical to v1.
- `make-v2.py` regenerates `v2/code.js` from `v1/code.js` deterministically.
- Visual self-check: same screens, clearly different identity, no half-reskinned grey chrome.
