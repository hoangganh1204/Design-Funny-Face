# -*- coding: utf-8 -*-
"""Áp một phương án logo (build/logo/<ID>_*.png) vào mọi nơi đang dùng nó.

    python3 script/apply-logo.py D

Ba đích, phải đi cùng nhau nếu không ba bản sẽ lệch nhau:
  assets/v3/40-anh-app/{ic_splash,img_app_name}.png   -> nguồn cho figma/v3
  assets/v4/40-anh-app/{ic_splash,img_app_name}.png   -> nguồn cho figma/v4
  app res/drawable-xxhdpi/{ic_splash,img_app_name}.webp

Sửa PNG trong assets/ chưa đủ: build-plugin.py nhúng base64 vào plugin.js, nên phải
build lại plugin thì Figma mới thấy. Script này chạy luôn bước đó.
"""
import os, shutil, subprocess, sys
from PIL import Image

APP_DESIGN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # <repo>/Funny Face
REPO = os.path.dirname(APP_DESIGN)
LOGO = os.path.join(APP_DESIGN, 'build', 'logo')
ANDROID = '/home/ubuntu/workspace/Mobile/funny-face/app/src/main/res/drawable-xxhdpi'

PAIRS = [('_splash.png', 'ic_splash'), ('_word.png', 'img_app_name')]


def main(vid):
    for suffix, stem in PAIRS:
        src = os.path.join(LOGO, vid + suffix)
        if not os.path.exists(src):
            sys.exit(f'thiếu {src} — chạy make-logo.py trước')
        im = Image.open(src).convert('RGBA')
        # Header v3 là nền TỐI, header v4 là nền SÁNG. Phương án nào cần hai bản mực
        # thì để sẵn <ID>_word_light.png; phương án tự mang nền (badge) dùng chung một file.
        light_src = os.path.join(LOGO, vid + suffix.replace('.png', '_light.png'))
        im_v3 = Image.open(light_src).convert('RGBA') if os.path.exists(light_src) else im

        for v, art in (('v3', im_v3), ('v4', im)):
            dst = os.path.join(APP_DESIGN, 'assets', v, '40-anh-app', stem + '.png')
            art.save(dst)
            print(f'  {os.path.relpath(dst, REPO)}  {art.size}')

        wdst = os.path.join(ANDROID, stem + '.webp')
        if os.path.isdir(ANDROID):
            im.save(wdst, 'WEBP', lossless=True, quality=100)
            print(f'  {wdst}  {im.size}')

    print('\nbuild lại plugin:')
    for v in ('v3', 'v4'):
        r = subprocess.run(['python3', os.path.join(REPO, 'tools', 'build-plugin.py'),
                            '--src', os.path.join(APP_DESIGN, 'assets', v),
                            '--plugin', os.path.join(APP_DESIGN, 'figma', v)],
                           capture_output=True, text=True)
        tail = [l for l in (r.stdout + r.stderr).strip().splitlines() if l.strip()][-2:]
        print(f'  {v}: ' + ' | '.join(tail))
        if r.returncode != 0:
            sys.exit(f'build {v} lỗi')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('dùng: python3 script/apply-logo.py <A|B|C|D|E>')
    main(sys.argv[1].upper())
