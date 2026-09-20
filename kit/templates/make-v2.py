#!/usr/bin/env python3
"""TEMPLATE — regenerate figma/v2/code.js from figma/v1/code.js (reskin: colors+radius+bg tint).
Edit the R list with your sampled brand→new-hue swaps. Layout stays identical (only tokens change).
Run: python3 "<App>/script/make-v2.py"   (then build --src assets/v2 --plugin figma/v2)
"""
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s=open(os.path.join(ROOT,'figma/v1/code.js')).read()
R=[  # ('v1 substring','v2 substring') — brand tokens (same hue angle), radius +1, dark→tinted-dark
  ("accent: 'ffcd6a'","accent: '<newhex>'"),
  ("const R = { card: 12, tile: 16, pill: 30, sm: 8, dialog: 16 };",
   "const R = { card: 16, tile: 20, pill: 30, sm: 10, dialog: 20 };"),
  ("121212","<darktint>"),("1c1b1f","<toolbartint>"),
  ("📱 <App> · Screens","📱 <App> v2 · Screens"),
]
for a,b in R:
    if a not in s: print('  (skip, not found):',a[:50])
    s=s.replace(a,b)
open(os.path.join(ROOT,'figma/v2/code.js'),'w').write(s); print('figma/v2/code.js regenerated')
