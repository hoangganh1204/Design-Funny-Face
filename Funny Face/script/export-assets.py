#!/usr/bin/env python3
"""export-assets.py — Funny Face. Sinh tự động từ specs/ (Plan 1 Phase 4).
KHOÁ = tên file không đuôi. webp/gif -> PNG; vector .xml -> SVG.
LƯU Ý app này: ảnh nội dung nằm ở res/mipmap-*, không phải res/drawable-* (xem BUCKETS).
Chạy: python3 "Funny Face/script/export-assets.py"
"""
import os, json, subprocess
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT); RES = os.path.join(ROOT, 'decompiled/resources/res')
OUT = os.path.join(ROOT, 'assets/v1'); VD2SVG = os.path.join(REPO, 'tools/vd2svg.py')
BUCKETS = ['drawable-xxxhdpi','drawable-xxhdpi','drawable-xhdpi','drawable-hdpi',
           'drawable-nodpi','drawable-mdpi','drawable',
           'mipmap-xxxhdpi','mipmap-xxhdpi','mipmap-xhdpi',
           'mipmap-hdpi','mipmap-mdpi']
BITMAPS = {'40-anh-app': ['ic_launcher_foreground', 'ic_launcher', 'bg_level_difficulty', 'bg_level_easy', 'bg_level_intermediate', 'ic_splash', 'img_app_name', 'img_banner_face_puzzle', 'img_banner_funny_puzzle', 'img_notify_puzzle', 'window_bg']}
VECTORS = {'10-icons': ['bg_splash', 'ic_back_1', 'ic_back_2', 'ic_check_box_selected', 'ic_check_box_unselected', 'ic_close', 'ic_delete', 'ic_empty', 'ic_gallery_btn', 'ic_home', 'ic_layers', 'ic_music', 'ic_pause_filter', 'ic_pause_music', 'ic_play_filter', 'ic_play_music', 'ic_record', 'ic_rotation_camera', 'ic_setting', 'ic_setting_language', 'ic_setting_policy', 'ic_setting_share', 'ic_setting_term', 'ic_share', 'ic_tick', 'ic_tick_disabled']}
# shape/selector -> KHÔNG export, dựng bằng rect/stroke trong code.js:
SHAPES_IN_CODE = ['bg_ad_native_media_white', 'bg_black_40_rounded', 'bg_button_my_library', 'bg_funny_puzzle', 'bg_funny_puzzle_text_name', 'bg_item_setting', 'bg_loading_rounded', 'bg_name_open_native', 'bg_primary_rounded', 'bg_primary_rounded_enabled', 'bg_solid_rounded_12', 'bg_white_corner_69', 'ic_check_box', 'ic_state_play_music', 'ic_tick_selector']

def find(n):
    for b in BUCKETS:
        for e in ('.png','.webp','.jpg','.jpeg','.gif'):
            p = os.path.join(RES, b, n + e)
            if os.path.exists(p): return p

def bmp_export():
    ok = miss = 0
    for grp, names in BITMAPS.items():
        d = os.path.join(OUT, grp); os.makedirs(d, exist_ok=True)
        for n in names:
            s = find(n)
            if not s: print('MISS bitmap', n); miss += 1; continue
            im = Image.open(s)
            if getattr(im, 'is_animated', False): im.seek(im.n_frames - 1)
            im.convert('RGBA').save(os.path.join(d, n + '.png')); ok += 1
    print(f'bitmap: {ok} ok, {miss} miss')

def vec_export():
    for grp, names in VECTORS.items():
        d = os.path.join(OUT, grp); os.makedirs(d, exist_ok=True)
        r = subprocess.run(['python3', VD2SVG, os.path.join(RES, 'drawable'), *names],
                           capture_output=True, text=True)
        svgs = json.loads(r.stdout or '{}')
        for k, v in svgs.items():
            open(os.path.join(d, k + '.svg'), 'w', encoding='utf-8').write(v)
        print(f'vector: {len(svgs)}/{len(names)} -> {grp}')
        for l in r.stderr.strip().split('\n'):
            if l and not l.startswith('OK'): print('  ', l)

if __name__ == '__main__':
    bmp_export(); vec_export()
    print(f'shape/selector dựng trong code.js (không export): {len(SHAPES_IN_CODE)}')
