#!/usr/bin/env python3
"""TEMPLATE — download real remote images with the token from /tmp/rc.json (fetch-remote-config).
Collect image_url/preview_url/... from the remote lists + bundled JSONs, then download+PNG.
  TOKEN=<pat or from rc> RC=/tmp/rc.json python3 "<App>/script/download-remote.py"
Set BASE to the CDN base the code uses (trace it in sources: ds.i.* / Glide URL builder).
"""

# Console Windows mac dinh cp1252 nen khong in duoc tieng Viet -> UnicodeEncodeError,
# va script chet GIUA CHUNG, de lai ket qua va do dang ma khong bao gi ro rang.
# Khong bat nguoi chay phai nho dat PYTHONUTF8=1; tu lo lay cho chac.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    if hasattr(_s, 'reconfigure'):
        _s.reconfigure(encoding='utf-8', errors='replace')
import os, io, json, urllib.request
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'assets/v1'); RC=json.load(open(os.environ.get('RC','/tmp/rc.json')))['entries']
BASE='https://raw.githubusercontent.com/<Owner>/<Repo>/main/'     # ← EDIT (from code)
TOKEN=os.environ.get('TOKEN') or RC.get('tg_access_token') or open('/tmp/gh_token.txt').read().strip()
MAXDIM=800
def L(k):
    try: return json.loads(RC.get(k,'[]'))
    except Exception: return []
# EDIT: map group → list of image_url paths (from remote lists L('key') and/or bundled assets/*.json)
JOBS = {
  # '20-photos': [it['image_url'] for it in L('some_remote_list')],
}
def fetch(u):
    return urllib.request.urlopen(urllib.request.Request(BASE+u,headers={'Authorization':'token '+TOKEN,'User-Agent':'okhttp/4.12.0'}),timeout=30).read()
ok=miss=0
for grp,urls in JOBS.items():
    d=os.path.join(OUT,grp); os.makedirs(d,exist_ok=True)
    for u in urls:
        if not u: continue
        key=os.path.splitext(os.path.basename(u))[0]
        try:
            im=Image.open(io.BytesIO(fetch(u)))
            if getattr(im,'is_animated',False): im.seek(im.n_frames//2)
            im=im.convert('RGBA'); w,h=im.size
            if max(w,h)>MAXDIM: s=MAXDIM/max(w,h); im=im.resize((int(w*s),int(h*s)),Image.LANCZOS)
            im.save(os.path.join(d,key+'.png')); ok+=1
        except Exception as e: print('MISS',u,str(e)[:60]); miss+=1
print('done: %d ok, %d miss'%(ok,miss))
