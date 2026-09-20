#!/usr/bin/env python3
"""TEMPLATE — export APK drawables → <App>/assets/v1. Edit BITMAPS/VECTORS/PNG_ICONS with the
asset names each screen needs (from Phase 2). webp/gif→PNG; vector .xml→SVG. name(no ext)=key.
Run: python3 "<App>/script/export-assets.py"
"""

# Console Windows mac dinh cp1252 nen khong in duoc tieng Viet -> UnicodeEncodeError,
# va script chet GIUA CHUNG, de lai ket qua va do dang ma khong bao gi ro rang.
# Khong bat nguoi chay phai nho dat PYTHONUTF8=1; tu lo lay cho chac.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    if hasattr(_s, 'reconfigure'):
        _s.reconfigure(encoding='utf-8', errors='replace')
import os, glob, json, subprocess
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT); RES = os.path.join(ROOT, 'decompiled/resources/res')
OUT = os.path.join(ROOT, 'assets/v1'); VD2SVG = os.path.join(REPO, 'tools/vd2svg.py')
BUCKETS = ['drawable-xxxhdpi','drawable-xxhdpi','drawable-xhdpi','drawable-hdpi','drawable-nodpi','drawable-mdpi','drawable']
BITMAPS = {  # 'group-folder': ['name1','name2', ...]  ← EDIT
  '01-example': ['splash_background'],
}
VECTORS = { '10-icons': ['ic_back'] }        # ← EDIT (vector .xml → svg)
PNG_ICONS = { '10-icons': [] }               # ← PNG icons living in base drawable
def find(n):
    for b in BUCKETS:
        for e in ('.png','.webp','.jpg','.jpeg','.gif'):
            p=os.path.join(RES,b,n+e)
            if os.path.exists(p): return p
def bmp():
    for grp,names in list(BITMAPS.items())+list(PNG_ICONS.items()):
        d=os.path.join(OUT,grp); os.makedirs(d,exist_ok=True)
        for n in names:
            s=find(n)
            if not s: print('MISS',n); continue
            im=Image.open(s)
            if getattr(im,'is_animated',False): im.seek(im.n_frames-1)
            im.convert('RGBA').save(os.path.join(d,n+'.png'))
def vec():
    for grp,names in VECTORS.items():
        d=os.path.join(OUT,grp); os.makedirs(d,exist_ok=True)
        for n in names:
            x=glob.glob(os.path.join(RES,'drawable*',n+'.xml'))
            if not x: print('MISS vec',n); continue
            r=subprocess.run(['python3',VD2SVG,os.path.dirname(x[0]),n],capture_output=True,text=True)
            try: svg=json.loads(r.stdout).get(n)
            except Exception: svg=None
            if svg: open(os.path.join(d,n+'.svg'),'w').write(svg)
            else: print('EMPTY vec',n,'(layer-list/selector → draw inline)')
if __name__=='__main__': bmp(); vec(); print('done →',OUT)
