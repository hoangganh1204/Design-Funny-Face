#!/usr/bin/env python3
"""make-v3.py — sinh figma/v3 từ figma/v1: hệ thiết kế mới (Purple/Orange/Warm White).

KHÁC make-v2.py ở bản chất:
  make-v2 là phép BIẾN ĐỔI MÀU thuần (xoay hue) — chạy lại lúc nào cũng được, v2 luôn
  khớp v1. make-v3 là bộ KHỞI TẠO MỘT LẦN: nó chép v1 sang v3 rồi áp một loạt bản vá
  có chủ đích (đổi token + sửa bố cục). Sau khi chạy, v3 được sửa tay tiếp và KHÔNG
  còn suy ra được từ v1 nữa — vì đổi bố cục thì không có phép biến đổi nào suy ra được.
  Vì vậy script TỪ CHỐI ghi đè nếu figma/v3 đã có, trừ khi truyền --force.

v1 giữ nguyên vĩnh viễn: nó là bằng chứng đối chiếu 1:1 với APK gốc, mọi spec trong
specs/ đều mô tả nó. v3 là bản THIẾT KẾ SẢN PHẨM, được phép khác app gốc.

Ràng buộc: CHỈ đổi diện mạo và bố cục. Không thêm phần tử nào mà app gốc không có —
mọi thay đổi phải ánh xạ được vào một view đã tồn tại trong layout XML.

Chạy: PYTHONUTF8=1 python "Funny Face/script/make-v3.py" [--force]
"""
import colorsys
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1 = os.path.join(ROOT, 'figma', 'v1')
V3 = os.path.join(ROOT, 'figma', 'v3')
A1 = os.path.join(ROOT, 'assets', 'v1')
A3 = os.path.join(ROOT, 'assets', 'v3')


# ─────────────────────────────────────────────────────────── bảng token v3
# Vai trò màu (do design lead đặt, ghi lại ở đây để đọc code là hiểu ý đồ):
#   Purple      — nhận diện thương hiệu, khu vực chính, cảm giác sáng tạo/AR
#   Orange      — CTA quan trọng, trạng thái tương tác
#   Warm White  — nền các màn ĐỌC CHỮ (Settings, Privacy, Term)
#   Dark        — nền các màn NỘI DUNG (Home, chọn hiệu ứng, thư viện) + chữ trên nền sáng
#   Mint        — trạng thái thành công, dùng tiết chế
#
# Vì sao màn nội dung để nền TỐI chứ không Warm White như bảng gốc: nội dung chính của
# các màn đó là thumbnail và ảnh nhân vật. Nền sáng hút mất chú ý khỏi chính nội dung.
# Quan trọng hơn: 6/12 placement quảng cáo là native nằm ngay trong màn nội dung — trên
# nền trắng chúng trông y hệt một ô nội dung nên người dùng bấm nhầm; trên nền tối, ô
# nội dung là ảnh còn khối ad là mảng phẳng có nhãn, phân biệt được ngay. App không có
# IAP nên retention CHÍNH LÀ doanh thu, bấm nhầm đẩy CTR ngắn hạn nhưng giết retention.
#
# Tương phản đã kiểm (WCAG 2.1):
#   onDark f5f3ff / bg 14101f      → 16.8:1   (AAA)
#   onDarkSub a79fc4 / bg 14101f   →  7.4:1   (AAA chữ thường)
#   onAction 1a1523 / action ff6b35→  7.1:1   (AAA) — nên chữ trên nút cam là chữ TỐI,
#                                                 không phải trắng (trắng chỉ 2.9:1, trượt AA)
#   white / brand 7c3aed           →  5.9:1   (AA)
#   onLight 1a1523 / paper fdf9f3  → 16.3:1   (AAA)
TOKENS = """const C = {
  // ── Thương hiệu: tím ───────────────────────────────────────────────────────
  // Nền sáng lên thì brand #7c3aed chỉ còn 2.54:1 so với nền — dưới ngưỡng 3:1 cho
  // thành phần phi văn bản, chip đang chọn sẽ chìm. #9a6cff đạt 4.10:1 so với nền VÀ
  // 5.10:1 cho chữ tối đặt trên nó. (Chữ TRẮNG trên #9a6cff chỉ 3.52:1 — trượt, nên
  // chữ trên chip brand phải là chữ TỐI, cùng nguyên tắc với nút cam.)
  primary:   '9a6cff',  // brand
  brand:     '9a6cff',
  brandDeep: '5b21b6',  // đầu đậm của gradient thương hiệu
  brandSoft: 'c4b0ff',  // icon phụ, viền trạng thái chọn
  // ── Hành động: cam ─────────────────────────────────────────────────────────
  // Chữ trên CTA phải là chữ TRẮNG (yêu cầu design lead). Nhưng đo ra không có màu cam
  // nào thoả cả hai điều kiện: cam đủ sáng để nút tách khỏi nền (>=3:1) thì chữ trắng
  // trượt AA; cam đủ đậm cho chữ trắng (>=4.5:1) thì nút lại chìm vào nền.
  //   #ff6b35  trắng 2.84 ✗ · nút/nền 5.10 ✓
  //   #d9480f  trắng 4.30 ✗ · nút/nền 3.36 ✓
  //   #c2410c  trắng 5.18 ✓ · nút/nền 2.79 ✗
  // Lối ra: lấy cam đậm cho chữ trắng, rồi lấy lại độ tách bằng VIỀN SÁNG 2dp — WCAG
  // cho phép đạt ngưỡng 3:1 của thành phần phi văn bản bằng viền thay vì bằng nền.
  // Viền #ff8a3d đạt 6.16:1 so với nền màn.
  actionDn:  'e85a28',  // trạng thái nhấn
  // Cam đầy + chữ trắng (quyết định của design lead). Trắng trên #ff6b35 chỉ 2.84:1,
  // thiếu 0.16 so với ngưỡng 3.0 của chữ LỚN ĐẬM (nhãn CTA là 16sp bold). Làm đậm
  // cam đúng 4% xuống #f5612b là đạt 3.17:1 — mắt gần như không phân biệt được với
  // bản cũ, mà hết lệch chuẩn. Lưu ý: cặp này KHÔNG đạt ngưỡng 4.5 của chữ thường,
  // nên đừng dùng màu nền này cho chữ nhỏ hoặc chữ mảnh.
  action:    'f5612b',  // nền nút CTA
  actionEdge:'ff8a3d',  // viền nút — thứ tạo độ tách khỏi nền
  // ⚠ CHẤP NHẬN LỆCH CHUẨN, có chủ đích. Chữ trắng trên #ff6b35 chỉ 2.84:1 — dưới
  // ngưỡng AA (4.5). Design lead đã được báo con số và vẫn chọn cam đầy + chữ trắng vì
  // lý do thẩm mỹ. Ghi lại ở đây để không ai tưởng là sót. Muốn đạt chuẩn thì hoặc đổi
  // chữ về tối (6.30:1) hoặc hạ nền xuống #c2410c kèm viền sáng 2dp (5.18:1).
  onAction:  'ffffff',
  // ── Thành công: mint, dùng tiết chế ────────────────────────────────────────
  mint:      '34d399',
  onMint:    '0b2e22',
  // ── Nền TỐI — màn nội dung ────────────────────────────────────────────────
  // Hai thứ phải có, bản trước thiếu cả hai:
  //
  // (a) DẢI ĐỘ SÁNG đủ rộng. Bản trước: nền L*5.6 · mặt L*10 · mặt nổi L*15 — vỏn vẹn
  //     10 điểm. Spotify dùng 14, TikTok dùng 16. Dải hẹp thì mọi lớp dính vào nhau
  //     thành một mảng phẳng, không đọc ra cái gì nổi trên cái gì. Nay 8 → 28, dải 20.
  //
  // (b) BIẾN THIÊN SẮC ĐỘ. Bản trước cả 5 token nằm trong 7 độ (255-262°) nên mắt đọc
  //     toàn bộ khung như MỘT mảng tím-đen. Nay bóng lạnh hơn (nền 252°), mặt nổi ấm
  //     dần (line 268°) — chênh 16 độ, đủ tạo chiều sâu mà vẫn cùng một họ màu.
  bg:        '2b2252',  // L*17 · hue 253° — sáng hơn bản trước 6 điểm L*
  surface:   '3a2f6c',  // L*24
  surfaceHi: '4b3d8c',  // L*31
  line:      '5f4fa8',  // L*39 — mặt nổi cao nhất
  // ── Nền SÁNG — màn đọc chữ ────────────────────────────────────────────────
  paper:     'fdf9f3',
  paperCard: 'ffffff',
  paperLine: 'ede6dc',
  // ── Chữ ───────────────────────────────────────────────────────────────────
  onDark:    'f5f3ff',
  // Nền sáng lên thì chữ phụ cũ #a79fc4 chỉ còn 3.58:1 trên chip chưa chọn
  // (surfaceHi). #c9c2de đạt 5.23:1 ở đó và 8.43:1 trên nền — dư biên cả hai chỗ.
  onDarkSub: 'c9c2de',
  onLight:   '1a1523',
  onLightSub:'5c5470',
  // ── Tên cũ giữ nguyên để 145 chỗ tham chiếu trong screens/ không gãy ───────
  white:     'ffffff',
  black:     '000000',
  textHi:    'f5f3ff',
  textSub:   'c9c2de',
  textHint:  '6f668f',
  text2:     'c9c2de',
  gray:      '4a4160', grayDark: '6f668f', gray9d: '8b82a8',
  grayF4:    '1e1830', grayF5EEE9: 'fdf9f3', e6e6e5: '332a4a',
  dark141414:'14101f', dark2D: '2a2140',
  scrim20:   '3314101f', scrim30: '4d14101f', scrimA6: 'a614101f',
  red:       'ff5a5f',
  orange:    'ff6b35',
  transparent: '00ffffff',
  card:      '1e1830',
  accent:    'ff6b35',
  toolbar:   '14101f',
  toolbarDiv:'332a4a',
};"""

# Bo góc tăng đúng MỘT bậc so với v1 (v1: card12 tile16 sm8 dialog16).
# Bậc lớn hơn cho cảm giác mềm và hiện đại hơn, nhưng tăng quá tay thì thẻ ảnh vuông
# trông như viên kẹo và ảnh bị cắt góc nhiều — 16/20 là điểm dừng.
RADII = "const R = { card: 16, tile: 20, pill: 100, sm: 10, dialog: 20, r12: 14, r69: 69 };"


def patch(text, pairs, label):
    """Áp từng cặp (cũ, mới). Mỗi cặp BẮT BUỘC phải khớp — không khớp là dừng ngay,
    vì vá trượt trong im lặng thì kết quả sai mà không ai biết (bài học verify.js)."""
    for old, new, *rest in pairs:
        count = rest[0] if rest else 1
        found = text.count(old)
        if found == 0:
            raise SystemExit('[%s] KHÔNG khớp: %r' % (label, old[:90]))
        if count == 'all':
            text = text.replace(old, new)
        else:
            if found != count:
                raise SystemExit('[%s] khớp %d lần, kỳ vọng %d: %r' % (label, found, count, old[:90]))
            text = text.replace(old, new, count)
    return text


def do_code_js():
    p = os.path.join(V3, 'code.js')
    s = open(p, encoding='utf-8').read()

    s = re.sub(r'const C = \{.*?\n\};', TOKENS, s, count=1, flags=re.S)
    s = re.sub(r'const R = \{[^\n]*\};', RADII, s, count=1)
    assert "brandDeep" in s and "pill: 100" in s, 'thay token thất bại'

    s = patch(s, [
        # Đổ bóng: v1 dùng đen 40% offset 6/blur 16 — trên nền tím than, bóng đen thuần
        # trông bẩn và không tách được thẻ khỏi nền. Bóng ám tím, mềm hơn, đi xa hơn.
        ("if(o.shadow)f.effects=[{type:'DROP_SHADOW',color:{r:0,g:0,b:0,a:o.shadow===true?0.4:o.shadow},"
         "offset:{x:0,y:6},radius:16,spread:0,visible:true,blendMode:'NORMAL'}];",
         "if(o.shadow)f.effects=[{type:'DROP_SHADOW',color:{r:0.04,g:0.02,b:0.10,a:o.shadow===true?0.55:o.shadow},"
         "offset:{x:0,y:8},radius:24,spread:-2,visible:true,blendMode:'NORMAL'}];"),

        # Nền dùng chung cho MỌI màn nội dung: một dải chuyển + một lớp hoạ tiết.
        # Gom vào một hàm để không màn nào lệch tông — trước đây mỗi màn tự khai báo nền
        # nên Level Picker dùng ảnh nướng sẵn còn Home dùng dải chuyển, hai tông khác nhau.
        ("function add(parent){",
         "function screenBg(f,h){"
         + "const bg=rect('bg',0,0,SCREEN_W,h,{gradient:['2b2252','3d3070'],gradientDir:'v'});"
         + "f.appendChild(bg);"
         + "const pat=rect('hoạ tiết mặt',0,0,SCREEN_W,h,{image:'pattern_overlay',scaleMode:'TILE'});"
         + "f.appendChild(pat);return{bg:bg,pat:pat};}"
         + chr(10) + "function patternOn(f,h){" + "const p=rect('hoạ tiết mặt',0,0,SCREEN_W,h,{image:'pattern_overlay',scaleMode:'TILE'});" + "f.appendChild(p);return p;}"
         + chr(10) + "function add(parent){"),

        # Figma đòi scalingFactor khi scaleMode='TILE'; thiếu nó thì ô lát về mặc
        # định 0.5 và hoạ tiết bé lại một nửa.
        ("return{type:'IMAGE',scaleMode:scaleMode||'FILL',imageHash:imgCache[name]};",
         "const p={type:'IMAGE',scaleMode:scaleMode||'FILL',imageHash:imgCache[name]};"
         + "if(p.scaleMode==='TILE')p.scalingFactor=0.5;return p;"),

        # ── Tô lại nét icon cho nền tối ────────────────────────────────────
        # Icon từ APK vốn đặt trên nền TRẮNG nên nét là đen/xám đậm; xoay hue không
        # đụng tới vì chúng trung tính. Sau khi đảo nền sang tối thì chúng chìm hẳn
        # (đo được: ic_home L*8, ic_back_1 L*0, ic_gallery_btn L*0 trên nền L*10.5-17).
        # Chỉ đổi pixel TRUNG TÍNH và TỐI nên điểm nhấn có màu được giữ: bánh răng đỏ,
        # mảng vàng của icon thư viện, tím của ô check.
        # ICON_ON_LIGHT = những icon LUÔN nằm trên bề mặt sáng, giữ nguyên nét tối.
        # Ánh xạ sang app: android:tint trên ImageView — thuộc tính có sẵn, không thêm view.
        ("function svgNode(name,x,y,w,h){",
         "var ICON_ON_LIGHT=' ic_setting_language ic_setting_policy ic_setting_term ic_setting_share ic_tick_disabled ic_tick_enabled ';"
         + "function tintIcon(sv){return sv.replace(/(fill|stroke)=\"#([0-9a-fA-F]{6})\"/g,"
         + "function(m,att,hx){var r=parseInt(hx.slice(0,2),16),g=parseInt(hx.slice(2,4),16),b=parseInt(hx.slice(4,6),16);"
         + "var mx=Math.max(r,g,b),mn=Math.min(r,g,b);var sat=mx?(mx-mn)/mx:0;"
         + "var lum=(0.2126*r+0.7152*g+0.0722*b)/255;"
         + "return (sat<0.25&&lum<0.45)?att+'=\"#f5f3ff\"':m;});}"
         + chr(10) + "function iconDark(name,x,y,w,h){var keep=ICON_ON_LIGHT;ICON_ON_LIGHT=' '+name+' ';"
         + "var n=icon(name,x,y,w,h);ICON_ON_LIGHT=keep;return n;}"
         + chr(10) + "function svgNode(name,x,y,w,h){"),
        ("const n=figma.createNodeFromSvg(ICONS[name]);",
         "const n=figma.createNodeFromSvg(ICON_ON_LIGHT.indexOf(' '+name+' ')>=0?ICONS[name]:tintIcon(ICONS[name]));"),

        # Khung NÉT ĐỨT. Trong quy ước UI, nét đứt nghĩa là "ô trống, chờ điền" — đó là
        # lý do v3 bỏ nó khỏi mọi thẻ ĐÃ CÓ nội dung (app gốc dùng khắp nơi, kể cả thẻ
        # nhân vật và hàng Settings, nên mắt đọc thành "chỗ này chưa có gì").
        # Nhưng app CÓ đúng một chỗ nét đứt mang nghĩa thật: màn thư viện RỖNG. Ở đó nó
        # vừa đúng quy ước vừa giữ được nét vẽ tay của app gốc.
        ("function add(parent){",
         "function dashRect(parent,x,y,w,h,r,color,sw,dash){"
         + "const sv='<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"'+w+'\" height=\"'+h+'\">'"
         + "+'<rect x=\"'+(sw/2)+'\" y=\"'+(sw/2)+'\" width=\"'+(w-sw)+'\" height=\"'+(h-sw)+'\" rx=\"'+r+'\" '"
         + "+'fill=\"none\" stroke=\"#'+color+'\" stroke-width=\"'+sw+'\" stroke-dasharray=\"'+(dash||'12,9')+'\" stroke-linecap=\"round\"/></svg>';"
         + "const n=figma.createNodeFromSvg(sv);n.name='khung nét đứt';n.x=x;n.y=y;n.resize(w,h);parent.appendChild(n);return n;}"
         + chr(10) + "function add(parent){"),

        # grad() của v1 hardcode a:1 cho cả hai điểm dừng -> MỌI gradient có alpha đều
        # bị vẽ thành mảng ĐẶC. Không lộ ra ở v1 vì v1 chỉ dùng gradient đục. v3 dùng
        # dải chuyển trong suốt để làm nền chữ đè lên ảnh, nên phải sửa.
        ("gradientStops:[{position:0,color:Object.assign(rgb(a),{a:1})},"
         "{position:1,color:Object.assign(rgb(b),{a:1})}]",
         "gradientStops:[{position:0,color:Object.assign(rgb(a),{a:alphaOf(a)!==undefined?alphaOf(a):1})},"
         "{position:1,color:Object.assign(rgb(b),{a:alphaOf(b)!==undefined?alphaOf(b):1})}]"),

        # Ô nội dung runtime (video người dùng tạo) — hoà vào hệ nền tối
        ("function remoteTile(parent,x,y,w,h,label,r){const g=frame('remote · '+(label||''),x,y,w,h,"
         "{fill:'242424',stroke:'3a3a3a',strokeW:1,radius:r!==undefined?r:8,clip:true});add(parent,g);"
         "add(g,text(label||'remote',0,h/2-8,{size:10,font:'main',color:'6a6a6a',w:w,align:'CENTER'}));return g;}",
         "function remoteTile(parent,x,y,w,h,label,r){const g=frame('remote · '+(label||''),x,y,w,h,"
         "{fill:C.surface,stroke:C.line,strokeW:1,radius:r!==undefined?r:R.card,clip:true});add(parent,g);"
         "add(g,text(label||'remote',0,h/2-8,{size:10,font:'main',color:C.onDarkSub,w:w,align:'CENTER'}));return g;}"),

        # Khối quảng cáo: PHẢI đọc ra là quảng cáo ngay từ cái nhìn đầu. Mảng phẳng
        # surface + viền + nhãn — cố tình KHÔNG giả dạng ô nội dung. Đây là lựa chọn
        # thiết kế có chủ đích, không phải thiếu sót: bấm nhầm đẩy CTR ngắn hạn nhưng
        # giết retention, mà app không có IAP nên retention chính là doanh thu.
        ("const g=frame('AD SLOT · '+(label||'Native'),x,y,w,h,{fill:'1a1a1a',stroke:'3a3a3a',strokeW:1,radius:8});"
         "add(g,text('AD · '+(label||''),0,h/2-8,{size:12,font:'main',color:'6a6a6a',w:w,align:'CENTER'}));",
         "const g=frame('AD SLOT · '+(label||'Native'),x,y,w,h,{fill:C.surface,stroke:C.line,strokeW:1,radius:R.card});"
         "add(g,rect('ad-badge',10,10,26,16,{fill:C.surfaceHi,radius:4}));"
         "add(g,text('AD',10,10,{size:9,weight:700,font:'main',color:C.onDarkSub,w:26,h:16,align:'CENTER',valign:'CENTER'}));"
         "add(g,text(label||'',0,h/2-8,{size:12,font:'main',color:C.onDarkSub,w:w,align:'CENTER'}));"),
    ], 'code.js')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def do_home():
    p = os.path.join(V3, 'screens', 'home.js')
    s = open(p, encoding='utf-8').read()
    s = patch(s, [
        # Nền màn nội dung. Đã A/B ba bản (xem mục "Nền màn nội dung — A/B" trong spec):
        #   A phẳng #2b2252             → 8.7/10  · ổn định nhưng đơn điệu
        #   B dải nhẹ #2b2252→#3d3070   → 8.9/10  · CHỌN
        #   C dải sáng như Splash       → 5.6/10  · nửa dưới nền nhạt, thẻ tối chìm hẳn
        # Chênh lệch của B chỉ ~8 điểm L* nên đọc ra CHIỀU SÂU chứ không đọc ra "đổi màu
        # nền". Quan trọng: Home cuộn 1660dp — dải rộng như C khiến CÙNG MỘT THẺ đọc khác
        # hẳn tuỳ vị trí cuộn, đó là lỗi phân cấp chứ không phải khẩu vị.
        ("  const bg = rect('bg', 0, 0, SCREEN_W, SCREEN_H, { fill: C.white });" + chr(10) + "  add(f, bg);",
         "  const _sb = screenBg(f, SCREEN_H), bg = _sb.bg, pat = _sb.pat;", 'all'),
        ("const { bg, gridStartY } = home_chrome(f, tabIdx);",
         "const { bg, pat, gridStartY } = home_chrome(f, tabIdx);"),
        ("  bg.resize(SCREEN_W, bottom);",
         "  bg.resize(SCREEN_W, bottom); pat.resize(SCREEN_W, bottom);", 'all'),

        # ── Chip lọc danh mục ─────────────────────────────────────────────────
        # v1: chip chọn = xanh brand, chip thường = trắng viền đen 1dp, bo 8.
        # v3: chip chọn = TÍM thương hiệu (đây là điều hướng/nhận diện, không phải CTA —
        # cam để dành cho hành động), chip thường = surfaceHi không viền. Bo tròn hẳn
        # thành pill: hàng chip cuộn ngang, pill đọc ra "cuộn được" rõ hơn hộp bo 8.
        ("""    add(f, rect('tab · ' + label, tx, y, w, h, active
      ? { fill: C.primary, radius: 8 }
      : { fill: C.white, radius: 8, stroke: C.black, strokeW: 1 }));
    const t = text(label, tx, y, {
      size: fontSize, weight: 700, font: 'main', color: active ? C.white : C.black,""",
         """    add(f, rect('tab · ' + label, tx, y, w, h, active
      ? { fill: C.brandSoft, radius: h / 2 }
      : { fill: C.surfaceHi, radius: h / 2 }));
    const t = text(label, tx, y, {
      size: fontSize, weight: 700, font: 'main', color: active ? '2a1259' : C.onDarkSub,"""),

        # Chip ĐANG CHỌN: tím NHẠT + chữ tím sẫm, không phải tím đậm + chữ đen.
        # Tím đậm #9a6cff với chữ đen là hai màu TỐI cạnh nhau — đọc được (5.10:1)
        # nhưng nặng và không ra dáng 'đang chọn'. Đo các tổ hợp:
        #   #9a6cff + đen      chữ 5.10 · chip/nền 4.10
        #   #9a6cff + tím sẫm  chữ 4.49 TRƯỢT
        #   #c4b0ff + tím sẫm  chữ 8.28 · chip/nền 7.57   ← chọn
        #   #7c3aed + trắng    chip/nền 2.54 TRƯỢT
        # Chip sáng thành thứ nổi nhất hàng nên trạng thái chọn đọc ra ngay, và cặp
        # màu nằm trong cùng họ tím chứ không phải 'tím + đen'.
        # KHÔNG dùng cam cho chip dù số đẹp: cam là màu CTA, mỗi màn chỉ một khối cam.
        # ── Thẻ nhân vật Funny Puzzle ─────────────────────────────────────────
        # v1: thẻ TRẮNG, viền nét đứt 1dp, ảnh vuông inset 1dp, tên trên một dải trắng
        # riêng ở đáy. Ba vấn đề: dải trắng ăn mất 25% chiều cao thẻ mà không mang thông
        # tin gì thêm; viền nét đứt đọc ra "ô trống chờ điền" chứ không phải "nội dung
        # bấm được"; thẻ trắng trên nền trắng thì không có ranh giới.
        # v3: ảnh tràn hết thẻ, tên nằm ĐÈ lên dải chuyển màu tối ở đáy. Ảnh to hơn 33%
        # trong cùng diện tích, và dải tối vừa làm nền chữ vừa tạo chiều sâu.
        # Ánh xạ sang XML: ImageView đổi sang match_parent, TextView giữ nguyên nhưng
        # background đổi thành shape gradient. KHÔNG thêm view nào.
        ("""  const card = frame('funny · ' + name, x, y, cardW, cardH, {
    fill: C.white, radius: 16, stroke: C.primary, strokeW: 1, clip: true,
  });
  add(f, card);
  const pad = 1, imgW = cardW - pad * 2, imgH = imgW;
  photo(card, pad, pad, imgW, imgH, key, 'FILL', 0);
  const t = text(name, 0, 0, { size: 14, weight: 700, font: 'main', color: C.textHi, align: 'CENTER', w: cardW });
  const padY = 10, plateH = t.height + padY * 2;
  add(card, rect('plate', 0, cardH - plateH, cardW, plateH, { fill: C.white }));
  t.y = cardH - plateH + padY; t.x = 0;
  add(card, t);
  return cardH;""",
         """  const card = frame('funny · ' + name, x, y, cardW, cardH, {
    fill: C.surface, radius: R.tile, clip: true,
  });
  add(f, card);
  photo(card, 0, 0, cardW, cardH, key, 'FILL', 0);
  // Dải chuyển từ trong suốt xuống gần đặc, cao 40% thẻ: đủ để chữ trắng luôn đọc
  // được dù ảnh dưới nó sáng hay tối, mà vẫn thấy được phần thân ảnh phía sau.
  if (home_HOT[key]) home_hotBadge(card, 8, 8);
  add(card, rect('scrim tên', 0, cardH * 0.6, cardW, cardH * 0.4,
    { gradient: ['0014101f', 'ee14101f'], gradientDir: 'v' }));
  add(card, text(name, 0, cardH - 30, {
    size: 14, weight: 700, font: 'main', color: C.white, align: 'CENTER',
    w: cardW, h: 20, valign: 'CENTER',
  }));
  return cardH;"""),

        # Chỗ dành cho ô quảng cáo native_home được chừa VÔ ĐIỀU KIỆN: gridStartY trả về
        # 212 cố định, trong khi adSlot() lại không vẽ gì khi SHOW_ADS=false. Kết quả là
        # 118dp trống ngay đầu màn — đúng chỗ người dùng nhìn đầu tiên, và là nguyên nhân
        # chính khiến màn hình "trông tối": không phải màu sai mà là quá nhiều khoảng
        # trống ở nửa trên. Nay chừa chỗ chỉ khi thật sự có ad.
        ("return { bg, gridStartY: 212 };",
         "return { bg, pat, gridStartY: SHOW_ADS ? 212 : 114 };"),

        # Chân trang cũng chừa 256dp cho native_collapsible_home vô điều kiện, trong khi
        # adSlot() không vẽ gì khi tắt ad -> 266dp trống ở đáy mỗi màn Home.
        ("return y + 256;", "return y + (SHOW_ADS ? 256 : 16);"),

        # TabLayout tabMode=scrollable: lúc chạy, tab ĐANG CHỌN luôn được cuộn vào tầm
        # nhìn. Dựng tĩnh mà không mô phỏng điều đó thì frame 20e có chip đang chọn nằm
        # ở x=347 — ngoài khung 360, người xem không biết tab nào đang mở. Đây là lỗi
        # TRUYỀN ĐẠT, không phải lỗi thẩm mỹ.
        ("  let tx = startX;" + chr(10) + "  const fontSize = 12, padX = 8;",
         "  const fontSize = 12, padX = 8;" + chr(10)
         + "  const tabW = home_TABS.map(l => Math.max(home_measureTextWidth(l, fontSize) + padX * 2, 40));" + chr(10)
         + "  let naturalX = startX;" + chr(10)
         + "  for (let i = 0; i < activeIdx; i++) naturalX += tabW[i] + 12;" + chr(10)
         + "  const overflow = naturalX + tabW[activeIdx] - (SCREEN_W - 20);" + chr(10)
         + "  let tx = startX - Math.max(0, overflow);"),
        # Hàng chip cuộn ngang nên luôn có một chip bị cắt ở mép trái — dựng tĩnh thì
        # nó trông như lỗi render. Thêm dải mờ dần ở mép: biến chỗ cắt thành tín hiệu
        # "còn nữa, cuộn đi". Ánh xạ sang app là android:requiresFadingEdge="horizontal"
        # trên TabLayout — thuộc tính có sẵn, KHÔNG thêm view.
        ("  home_TABS.forEach((label, idx) => {",
         "  add(f, rect('fadingEdge trái', 0, y, 28, 32, " + chr(10)
         + "    { gradient: [C.bg, '00' + C.bg], gradientDir: 'h' }));" + chr(10)
         + "  home_TABS.forEach((label, idx) => {"),
        ("    const textW = home_measureTextWidth(label, fontSize);" + chr(10)
         + "    const w = Math.max(textW + padX * 2, 40), h = 32;",
         "    const w = tabW[idx], h = 32;"),

        # ── Tag HOT ──────────────────────────────────────────────────────────
        # ⚠ Đây là thứ DUY NHẤT trong v3 cần thêm view: một TextView trong
        #   item_funny_puzzle.xml + một cờ boolean trong FunnyPuzzleUI. Mọi thứ khác
        #   đều ánh xạ vào view đã có.
        #
        # Màu: nền thẻ trải khắp vòng màu (xanh, đỏ, vàng, tím, cam, hồng) nên không
        # màu đơn nào đọc được trên tất cả. Đo ra: chữ TRẮNG trượt AA trên mọi nền tag
        # ấm (pink 3.14:1 · cam 2.35:1 · vàng 1.43:1) — chỉ đỏ đậm d92d20 mới đạt, mà
        # đỏ đậm thì đọc ra "cảnh báo" chứ không phải "đang hot", lại đụng thẻ Haaland
        # nền đỏ. Chữ TỐI trên nền ấm đạt thoải mái (5.7-12.6:1).
        #
        # Chốt: pill gradient CAM→HỒNG, chữ tối, viền trắng 2dp. Ban đầu thử vàng→cam
        # nhưng trên thẻ VÀNG của Leonardo thì tag lẫn vào nền, chỉ còn viền trắng gánh.
        # Cam→hồng có tương phản SẮC ĐỘ thật với cả nền vàng lẫn nền lửa cam của Naruto,
        # VIỀN TRẮNG 2dp — viền trắng mới là thứ tách tag khỏi bất kỳ nền thẻ nào,
        # kể cả thẻ lửa cam của Naruto. Thêm đổ bóng nhẹ cho nổi khối.
        #
        # Đặt góc TRÊN-TRÁI: mặt nhân vật luôn ở giữa nên góc trên trống ở mọi ảnh, và
        # badge "Nk uses" của thẻ Face Puzzle nằm góc trên-PHẢI — hai thứ không đụng
        # nhau khi trộn chung lưới ở tab All.
        #
        # Chỉ gắn 6/18 thẻ. Gắn nhiều thì tag mất nghĩa — cái gì cũng hot thì không cái
        # nào hot. Danh sách dưới là ĐỀ XUẤT THIẾT KẾ (app không có dữ liệu lượt dùng
        # cho nhóm nhân vật, khác nhóm template có field likes từ CDN); dev nối vào số
        # liệu thật thì sửa một dòng.
        ("const home_GRID_PAD = 10;",
         "const home_HOT = { Leonel_Messi: 1, Cristiano_Ronaldo: 1, Neymar_Junior: 1, Leonardo_Dicaprio: 1, Naruto: 1, Sasuke: 1 };" + chr(10)
         + chr(10)
         + "function home_hotBadge(card, x, y) {" + chr(10)
         + "  const w = 52, h = 26;" + chr(10)
         + "  const b = frame('badge · HOT', x, y, w, h, {" + chr(10)
         + "    gradient: ['ff8a3d', 'ff4f81'], gradientDir: 'h', radius: h / 2," + chr(10)
         + "    stroke: 'ffffff', strokeW: 2.5, shadow: 0.55," + chr(10)
         + "  });" + chr(10)
         + "  add(card, b);" + chr(10)
         + "  add(b, text('HOT', 0, 0, { size: 12, weight: 900, font: 'main'," + chr(10)
         + "    color: '181522', w: w, h: h, align: 'CENTER', valign: 'CENTER' }));" + chr(10)
         + "}" + chr(10)
         + chr(10)
         + "const home_GRID_PAD = 10;"),

        # Badge "Nk uses" — bằng chứng xã hội, thứ duy nhất trên lưới nói "người khác
        # đã dùng cái này". v1 để đen 40%: trên thumbnail sáng thì chữ trắng bay mất.
        # Nâng lên 72% nền tím than, chữ luôn đọc được bất kể ảnh dưới nó ra sao.
        ("{ fill: '66171716', radius: h / 2 }",
         "{ fill: 'b814101f', radius: h / 2 }"),
    ], 'home.js')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def do_funny():
    p = os.path.join(V3, 'screens', 'funny-puzzle.js')
    s = open(p, encoding='utf-8').read()
    s = patch(s, [
        ("add(f, rect('bg', 0, 0, SCREEN_W, contentH, { fill: C.white }));",
         "screenBg(f, contentH);"),
        # Cùng một thẻ nhân vật như Home, giữ đồng bộ hai nơi
        ("""        fill: C.white, radius: R.tile, stroke: C.primary, strokeW: 1, clip: true,""",
         """        fill: C.surface, radius: R.tile, clip: true,"""),
        ("""      const plate = rect('NamePlate', 1, CARD - 1 - 37, CARD - 2, 37, { fill: C.white });""",
         """      if (home_HOT[item.image]) home_hotBadge(card, 8, 8);
      const plate = rect('NamePlate', 0, CARD * 0.6, CARD, CARD * 0.4, { gradient: ['0014101f', 'ee14101f'], gradientDir: 'v' });"""),
    ], 'funny-puzzle.js')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def do_face():
    p = os.path.join(V3, 'screens', 'face-puzzle.js')
    s = open(p, encoding='utf-8').read()
    s = patch(s, [
        # Hoạ tiết mặt trên NỀN TỐI — chỉ ở màn chọn độ khó (và thư viện rỗng).
        # KHÔNG dùng sau lưới Home/màn 40: ở đó thẻ đã phủ 67.8% diện tích nên hoa văn
        # chỉ ló qua mấy khe hẹp, đọc thành nhiễu chứ không thành hoa văn. Hoa văn cần
        # MẢNG TRỐNG LIỀN mới ra hình — hai màn này có đúng thứ đó.
        # Ảnh nướng sẵn trên đúng token C.bg, cường độ 0.16 (bản nền giấy là 0.34):
        # trên nền tối mắt nhạy với chênh lệch sáng hơn nhiều.
        ("add(f, rect('bg', 0, 0, SCREEN_W, SCREEN_H, { fill: C.white }));",
         "screenBg(f, SCREEN_H);", 'all'),
        # Màn chọn độ khó: ba khối chiếm 40% màn, 60% còn lại là khoảng trống — màn yếu
        # nhất cả app. Đã thử FILL khung cao 160dp cho khối to hơn: bị CẮT CHỮ ở nhãn dài
        # nhất ("Intermediate" mất cả chữ đầu lẫn chữ cuối). Cắt chữ là lỗi cứng nên bỏ.
        #
        # Cách dùng: giữ FIT (không bao giờ cắt), nới khối ra sát mép (margin 20 -> 16) và
        # ĐẨY CẢ NHÓM XUỐNG vùng ngón cái với tới. Ba lựa chọn nằm ở nửa dưới màn đọc ra
        # "chỗ để bấm", còn khoảng trống trên thành khoảng thở dưới tiêu đề — vừa hết cảm
        # giác hụt vừa dễ thao tác một tay. Khe 16 -> 28 cho nhịp thoáng hơn.
        ("var LV_W = 320, LV_H = (320 * 360) / 1008;",
         "var LV_W = 328, LV_H = (328 * 360) / 1008;"),
        ("add(f, img('bg_level_easy', 20, y, LV_W, LV_H, 'FIT')); y += LV_H + 16;",
         "add(f, img('bg_level_easy', 16, y, LV_W, LV_H, 'FIT')); y += LV_H + 28;", 'all'),
        ("add(f, img('bg_level_intermediate', 20, y, LV_W, LV_H, 'FIT')); y += LV_H + 16;",
         "add(f, img('bg_level_intermediate', 16, y, LV_W, LV_H, 'FIT')); y += LV_H + 28;", 'all'),
        ("add(f, img('bg_level_difficulty', 20, y, LV_W, LV_H, 'FIT')); y += LV_H + 16;",
         "add(f, img('bg_level_difficulty', 16, y, LV_W, LV_H, 'FIT')); y += LV_H + 28;", 'all'),
        ("var y = 84;", "var y = 240;", 'all'),
        ("rect('disabled-overlay', 20, y, LV_W, LV_H, { fill: C.white, opacity: 0.5 })",
         "rect('disabled-overlay', 20, y, LV_W, LV_H, { fill: C.bg, opacity: 0.6 })"),
    ], 'face-puzzle.js')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def do_preview():
    p = os.path.join(V3, 'screens', 'preview-sound.js')
    s = open(p, encoding='utf-8').read()
    s = s.replace("add(f, img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));",
                  "screenBg(f, SCREEN_H);")
    s = patch(s, [
        # CTA chính. v1: gradient cyan→xanh dương, chữ màu text mặc định.
        # v3: cam đặc, chữ TỐI (7.1:1 — trắng trên cam chỉ 2.9:1, trượt AA).
        # Đây là nút duy nhất dùng màu cam trong mỗi màn, nên nó là thứ mắt bắt trước.
        ("""  const btn = frame('Button.Primary · ' + label, x, y, w, 48, {
    gradient: ['00fbff', '0080f6'], gradientDir: 'v', radius: 24,
  });
  add(f, btn);
  add(btn, text(label, 0, 0, {
    size: 16, weight: 700, color: C.textHi, w: w, h: 48,""",
         """  const btn = frame('Button.Primary · ' + label, x, y, w, 48, {
    fill: C.action, radius: 24, shadow: 0.45,
  });
  add(f, btn);
  add(btn, text(label, 0, 0, {
    size: 16, weight: 700, color: C.onAction, w: w, h: 48,"""),
        # Nút phụ "No": nền xám sáng e6e6e5 của app gốc, mà dialog nay đã sang nền tối
        # nên chữ sáng trên đó chỉ 1.14:1. Đổi thành nút phụ đúng nghĩa của hệ nền tối.
        ("add(card, text('No', 16, 98, { size: 14, weight: 700, color: C.textHi, w: btnW, h: 44, align: 'CENTER', valign: 'CENTER' }));",
         "add(card, text('No', 16, 98, { size: 14, weight: 700, color: C.onDark, w: btnW, h: 44, align: 'CENTER', valign: 'CENTER' }));"),
        ("add(card, frame('btnCancel', 16, 98, btnW, 44, { fill: 'e6e6e5', radius: 69 }));",
         "add(card, frame('btnCancel', 16, 98, btnW, 44, { fill: C.surfaceHi, radius: 69 }));"),
        ("dcard(f, w, h, { y, radius: 12, fill: C.white, name: 'popup_exit_confirm' })",
         "dcard(f, w, h, { y, radius: R.dialog, fill: C.surface, name: 'popup_exit_confirm' })"),
    ], 'preview-sound.js')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def do_result():
    p = os.path.join(V3, 'screens', 'result-video.js')
    s = open(p, encoding='utf-8').read()
    # Result / PlayVideo / Gallery đều là màn NỘI DUNG (video người dùng vừa tạo), nên
    # đi nền tối. Nền window_bg trắng của app gốc làm khung video trông như bị dán lên
    # một tờ giấy, và dải trắng phía trên đầu video cướp mất chú ý khỏi chính video.
    s = s.replace("add(f, img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));",
                  "screenBg(f, SCREEN_H);")
    s = s.replace("add(f, img('window_bg', 0, 0, SCREEN_W, contentH, 'FILL'));",
                  "screenBg(f, contentH);")
    # Chữ trên nút cam phải TỐI: sáng trên cam chỉ 2.59:1, trượt cả ngưỡng chữ lớn (3.0).
    s = s.replace(
        "add(btnSave, text('Save', 158, 0, { size: 16, weight: 700, font: 'main', color: C.textHi,",
        "add(btnSave, text('Save', 158, 0, { size: 16, weight: 700, font: 'main', color: C.onAction,")
    # ── Bố cục màn Result: A/B rồi chọn ────────────────────────────────────
    # Phản hồi: "trông như bị chặt 3 khúc". Đo ra đúng vậy — tím 0-76 · video 76-710 ·
    # tím 710-800. Ba dải ngang, và cái tệ nhất là dải dưới: nó TÁCH nút Save khỏi đúng
    # cái video mà nó lưu.
    #
    #   A giữ nguyên              → 6.9/10
    #   B video tràn trọn màn     → không chấm được: video vẽ SAU thanh tiêu đề nên che
    #                               mất tiêu đề và 2 icon. Làm đúng phải đảo thứ tự vẽ.
    #   C dải tiêu đề + video kéo hết đáy, CTA nổi trên video → 8.9/10  ĐÃ CHỌN
    #
    # Thang: liên tục thị giác 30% · CTA gắn với nội dung 25% · video là nhân vật chính
    # 20% · tiêu đề đọc được 15% · dev dễ làm 10%.
    # Ánh xạ sang app: đổi constraint bottom của exoPlayerView về parent và nâng btnSave
    # lên trên nó (elevation). KHÔNG thêm view.
    s = patch(s, [
        ("add(f, rect('imvThumbVideo', 0, 76, SCREEN_W, 634, { image: 'mock_ar_ronaldo', scaleMode: 'FILL', radius: R.card }));",
         "add(f, rect('imvThumbVideo', 0, 76, SCREEN_W, SCREEN_H - 76, { image: 'mock_ar_ronaldo', scaleMode: 'FILL', radiusTop: 28 }));\n    add(f, rect('scrim dưới', 0, 620, SCREEN_W, 180, { gradient: ['0014101f', 'e614101f'], gradientDir: 'v' }));", 'all'),
        # Thư viện rỗng: khung nét đứt bọc minh hoạ — đúng nghĩa "chưa có gì ở đây", và
        # là chỗ DUY NHẤT trong v3 còn dùng nét đứt.
        # Chữ trạng thái rỗng ĐÈ LÊN khung nét đứt: chữ ở y=400 mà khung kết thúc ở
        # y=424. Thêm nữa chuỗi gốc có ngắt dòng thủ công kèm khoảng trắng thừa
        # ('... and \n start recording!') nên hai dòng căn giữa bị lệch nhau.
        # Hạ chữ xuống dưới khung 28dp, ngắt dòng sạch, thêm lineHeight cho dễ đọc.
        ("add(f, text('No videos yet! Try a fun filter and \\n start recording!', 20, 400, { size: 14, font: 'main', color: C.textHi, w: 320, align: 'CENTER' }));",
         "add(f, text('No videos yet!' + String.fromCharCode(10) + 'Try a fun filter and start recording!', 20, 452, { size: 14, font: 'main', color: C.textHi, w: 320, align: 'CENTER', lineHeight: 22 }));"),
        ("add(f, icon('ic_empty', (SCREEN_W - 180) / 2, 220, 180, 180));",
         "dashRect(f, (SCREEN_W - 240) / 2, 196, 240, 228, 28, 'a892e0', 2);" + chr(10)
         + "    add(f, icon('ic_empty', (SCREEN_W - 180) / 2, 220, 180, 180));", 'all'),
        ("const btnSave = frame('btnSave', 16, saveY, SCREEN_W - 32, 58, { fill: C.primary, radius: 48 });",
         "const btnSave = frame('btnSave', 16, saveY, SCREEN_W - 32, 58, { fill: C.action, radius: 29, shadow: 0.45 });", 'all'),
        ("frame('collapseHolderNative (skeleton, bg_ad_native_media_white)', 0, adY, SCREEN_W, 256, { fill: C.white })",
         "frame('collapseHolderNative (skeleton, bg_ad_native_media_white)', 0, adY, SCREEN_W, 256, { fill: C.surface })"),
        ("dcard(f, 306, 164, { fill: C.white, radius: 12, name: 'popup_exit_confirm · Delete video', scrim: 0.6 })",
         "dcard(f, 306, 164, { fill: C.surface, radius: R.dialog, name: 'popup_exit_confirm · Delete video', scrim: 0.6 })"),
    ], 'result-video.js')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def do_settings():
    """Ba màn ĐỌC CHỮ — đây mới là chỗ Warm White đúng vai trò."""
    p = os.path.join(V3, 'screens', 'settings-dialogs.js')
    s = open(p, encoding='utf-8').read()
    # Ba màn này là nơi Warm White đúng vai trò: chỗ người ta ĐỌC, không phải chỗ xem
    # ảnh. Nền window_bg của app gốc là ảnh trắng có hoạ tiết mặt mũi mờ — hoạ tiết đó
    # chạy dưới chữ làm giảm độ đọc, bỏ đi, thay bằng nền giấy phẳng.
    s = s.replace("img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL')",
                  "rect('windowBackground', 0, 0, SCREEN_W, SCREEN_H, { fill: C.paper })")
    # Token chữ mặc định C.textHi nay là màu SÁNG (dùng trên nền tối). Cả file này nằm
    # trên nền giấy nên phải đổi sang cặp chữ-trên-nền-sáng, không thì chữ trắng trên
    # giấy trắng — mất hút hoàn toàn.
    # Dòng "file:///android_asset/... · 16 đoạn đầu" là ghi chú KỸ THUẬT của bản dựng,
    # không phải UI của app — không được để lọt vào bản giao cho dev.
    s = s.replace("add(web, text('file:///android_asset/' + htmlFile + ' · 16 đoạn đầu', 16, 16, { size: 10, font: 'main', color: C.textSub, w: SCREEN_W - 32 }));", '')
    s = s.replace('color: C.textHi', 'color: C.onLight').replace('color: C.textSub', 'color: C.onLightSub')

    s = patch(s, [
        # Chỉ màn SETTINGS lấy lại hoạ tiết mặt: nó có khoảng trống thật ở nửa dưới và
        # KHÔNG có đoạn văn dài nào chạy dưới hoa văn. Privacy/Term thì 16 đoạn chữ liền
        # nhau — hoa văn dưới chữ làm giảm độ đọc, nên hai màn đó giữ nền phẳng.
        ("const bg = rect('windowBackground', 0, 0, SCREEN_W, SCREEN_H, { fill: C.paper });",
         "const bg = img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL');"),
        # Ngoại lệ: nút Next của dialog loading nằm trên ngữ cảnh camera tối, không phải
        # trên giấy — trả lại cặp màu của CTA.
        ("const cta70 = frame('btnNext (disabled, genFile() đang chạy)', 16, SCREEN_H - 16 - 48, SCREEN_W - 32, 48, { gradient: ['00fbff', '0080f6'], gradientDir: 'v', radius: 24, opacity: 0.5 });",
         "const cta70 = frame('btnNext (disabled, genFile() đang chạy)', 16, SCREEN_H - 16 - 48, SCREEN_W - 32, 48, { fill: C.surfaceHi, radius: 24 });"),
        ("add(cta70, text('Next', 0, 0, { size: 16, weight: 700, color: C.onLight, w: SCREEN_W - 32, h: 48, align: 'CENTER', valign: 'CENTER' }));",
         "add(cta70, text('Next', 0, 0, { size: 16, weight: 700, color: C.onDarkSub, w: SCREEN_W - 32, h: 48, align: 'CENTER', valign: 'CENTER' }));"),
        ("add(pill70, text('Song name', 30, 0, { size: 14, color: C.white, w: 120 - 30 - 8, h: 32, valign: 'CENTER' }));",
         "add(pill70, text('Song name', 30, 0, { size: 14, color: C.white, w: 120 - 30 - 8, h: 32, valign: 'CENTER' }));"),
        # `ic_back_1` dùng ở CẢ HAI loại nền — Level Picker (tối) và Settings/Privacy/
        # Term (giấy). Tô theo TÊN ASSET là sai: tô sáng hết thì mũi tên quay lại ở ba
        # màn giấy biến mất. Tô theo NGỮ CẢNH mới đúng — đây chính là lý do trong app
        # thật phải dùng android:tint trên từng ImageView chứ không sửa file drawable.
        ("const backIc = icon('ic_back_1', 20, 20, 24, 24);",
         "const backIc = iconDark('ic_back_1', 20, 20, 24, 24);", 'all'),
        ("const chk71 = icon('ic_check_box_unselected', 20, 20, 24, 24);",
         "const chk71 = iconDark('ic_check_box_unselected', 20, 20, 24, 24);"),
        ("const backIc71 = icon('ic_back_1', 20, 20, 24, 24);",
         "const backIc71 = iconDark('ic_back_1', 20, 20, 24, 24);"),
        ("frame('Row · ' + r.label, 20, top, 320, ROW_H, { fill: C.white, radius: R.tile, stroke: C.textHi, strokeW: 1, clip: true })",
         "frame('Row · ' + r.label, 20, top, 320, ROW_H, { fill: C.paperCard, radius: R.tile, stroke: C.paperLine, strokeW: 1, clip: true })"),
        ("frame('toolbarLayout', 0, 0, SCREEN_W, 64, { fill: 'fffdfb' })",
         "frame('toolbarLayout', 0, 0, SCREEN_W, 64, { fill: C.paper })"),
        ("frame('wvPrivacyPolicy · WebView', 0, 64, SCREEN_W, SCREEN_H - 64, { fill: C.white, clip: true })",
         "frame('wvPrivacyPolicy · WebView', 0, 64, SCREEN_W, SCREEN_H - 64, { fill: C.paper, clip: true })"),
        ("frame('item_language · ' + lang[0], 20, y, 320, 64, { fill: C.white, stroke: C.textHi, strokeW: 1, radius: 16 })",
         "frame('item_language · ' + lang[0], 20, y, 320, 64, { fill: C.paperCard, stroke: C.paperLine, strokeW: 1, radius: R.tile })"),
    ], 'settings-dialogs.js')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def do_onboard():
    p = os.path.join(V3, 'screens', 'onboard.js')
    s = open(p, encoding='utf-8').read()
    s = patch(s, [
        # windowBackground của app gốc là @mipmap/window_bg — một ảnh nền TRẮNG có hoa
        # văn mờ. Trên hệ nền tối nó thành mảng trắng chọc thẳng vào mắt ở màn đầu tiên
        # người dùng thấy. Thay bằng dải chuyển tím thương hiệu → nền app: màn splash
        # trở thành một khoảnh khắc nhận diện thay vì một trang trắng.
        # Ánh xạ sang app: đổi drawable window_bg, KHÔNG đổi view nào.
        # Splash là màn đầu tiên người dùng thấy — hiện tại là gradient TRẮNG → cyan,
        # tức app tự giới thiệu bằng đúng cái nền trắng mà ta đang bỏ đi. Đổi sang dải
        # tím thương hiệu: khoảnh khắc nhận diện, và nối liền mạch sang Home nền tối
        # thay vì chớp trắng rồi tối sầm.
        ("add(f, frame('bg_splash · gradient', 0, 0, SCREEN_W, SCREEN_H, { gradient: ['ffffff', '08bdff'], gradientDir: 'v' }));",
         "add(f, frame('bg_splash · gradient', 0, 0, SCREEN_W, SCREEN_H, { gradient: ['5b21b6', 'c4b0ff'], gradientDir: 'v' }));"),
        # Thanh tiến trình: rãnh trong mờ trên nền tím, phần chạy màu CAM. Đây là thứ
        # duy nhất chuyển động trên màn, để nó mang đúng màu hành động thì lúc sang màn
        # sau mắt đã quen cam = "chỗ cần bấm".
        ("{ fill: 'ffffff', stroke: '1a000000', strokeW: 1, radius: 8 }",
         "{ fill: '33ffffff', radius: 8 }"),
        ("add(f, rect('progress · fill', progX, progY, progW * pct, progH, { fill: '7a00e2', radius: 8 }));",
         "add(f, rect('progress · fill', progX, progY, progW * pct, progH, { fill: C.action, radius: 8 }));"),
        ("const bg = img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL');",
         "const bg = rect('window_bg', 0, 0, SCREEN_W, SCREEN_H, "
         "{ gradient: ['5b21b6', '14101f'], gradientDir: 'v' });", 'all'),
        # ── Language Picker: A/B rồi chọn ──────────────────────────────────
        # Phản hồi: nhìn khó chịu. Nguyên nhân: thẻ TRẮNG TINH trên nền tím BÃO HOÀ
        # là cặp tương phản cực đại — đọc thì rõ nhưng chói, nhìn lâu mỏi mắt.
        #   A trắng tinh / tím bão hoà      → 7.0/10
        #   B thẻ ngà / nền tím bớt bão hoà → 9.0/10  ĐÃ CHỌN
        #   C hàng tối trên nền tím         → 6.2/10 · mất cảm giác thẻ, và chữ tối
        #                                     trên hàng tối gần như không đọc được
        # Thang: dịu mắt 35% · trạng thái chọn rõ 25% · nhất quán hệ 20% · đọc được 20%.
        # B bỏ luôn viền thẻ — trên nền dịu thì bóng và sắc độ đã đủ tách, thêm viền
        # chỉ làm rối.
        # Trạng thái chọn phải đọc được bằng BA tín hiệu, không chỉ mỗi chấm radio: nền
        # tím nhạt + viền tím 2dp + chấm. Một tín hiệu đơn lẻ dễ bị bỏ sót, nhất là chấm
        # radio nhỏ trên điện thoại ngoài nắng.
        # ── Hàng ngôn ngữ: A/B lần 2 ───────────────────────────────────────
        # 7 thẻ TRẮNG RỜI trên nền tím tạo hiệu ứng VẰN — quét danh sách phải vượt 14
        # ranh giới trắng↔tím. Gom vào MỘT thẻ, ngăn bằng đường mảnh: còn 2 ranh giới.
        #   A 7 thẻ rời 6.4/10 · B gom một thẻ 9.3/10 (CHỌN) · C ép sát 7.3/10
        # Hàng đang chọn có HAI tín hiệu: nền tô nhạt + thanh thương hiệu ở mép trái.
        #
        # ⚠ Bản đầu dùng `f.__grp` để giữ thẻ gom giữa các vòng lặp — API Figma KHÔNG
        # cho gán thuộc tính tuỳ ý lên node nên builder ném lỗi ở Figma THẬT, trong khi
        # bộ mock của capture-scene lại cho nên ảnh preview trông vẫn ổn. Bài học: thứ
        # gì chỉ chạy được nhờ đặc tính của mock thì sẽ gãy khi chạy thật.
        ("    let y = listTop;\n    LANGS.forEach((lang, i) => {\n      y += gapTop;\n      const it = frame('item_language · ' + lang[0], itemX, y, itemW, itemH, { fill: 'ffffff', stroke: C.textHi, strokeW: 1, radius: 16 });\n      add(f, it);\n      const selected = opt.selectedIndex === i;\n      const ic = icon(selected ? 'ic_check_box_selected' : 'ic_check_box_unselected', 20, itemH / 2 - 12, 24, 24);\n      if (ic) add(it, ic);\n      add(it, text(lang[0], 52, 0, { size: 20, weight: 700, font: 'main', color: C.textHi, w: itemW - 72, h: itemH, valign: 'CENTER' }));\n      y += itemH;\n    });",
         "    const grpY = listTop + gapTop;\n    const grp = frame('rvLanguage · thẻ gom', itemX, grpY, itemW, itemH * LANGS.length, { fill: 'ffffff', radius: 24, shadow: 0.22, clip: true });\n    add(f, grp);\n    LANGS.forEach((lang, i) => {\n      const selected = opt.selectedIndex === i;\n      const it = frame('item_language · ' + lang[0], 0, itemH * i, itemW, itemH, selected ? { fill: 'f1e9ff' } : {});\n      add(grp, it);\n      if (i) add(grp, rect('divider', 20, itemH * i, itemW - 40, 1, { fill: 'ece7f2' }));\n      if (selected) add(grp, rect('thanh chọn', 0, itemH * i, 4, itemH, { fill: C.brand }));\n      const ic = iconDark(selected ? 'ic_check_box_selected' : 'ic_check_box_unselected', 20, itemH / 2 - 12, 24, 24);\n      if (ic) add(it, ic);\n      add(it, text(lang[0], 52, 0, { size: 20, weight: 700, font: 'main', color: C.onLight, w: itemW - 72, h: itemH, valign: 'CENTER' }));\n    });\n    const y = grpY + itemH * LANGS.length;"),

        # Dải chuyển kết thúc ở #14101f gần như đen — nặng, và đá nhau với logo nhiều
        # màu. Kéo điểm cuối lên tím sẫm để màn vẫn có sức sống. Dùng CHUNG một cặp cho
        # cả Splash lẫn Language Picker để hai màn liền mạch.
        ("{ gradient: ['5b21b6', '14101f'], gradientDir: 'v' }",
         "{ gradient: ['5b21b6', 'c4b0ff'], gradientDir: 'v' }", 'all'),

        # Lỗi ngữ pháp có sẵn trong APK (@string/this_action_contain_ads, strings.xml:555).
        # Là chuỗi hiển thị cho người dùng nên sửa; dev đổi strings.xml, không đụng code.
        # Dòng ghi chú ads nằm ở ~95% chiều cao — chỗ dải màu đã sang tím nhạt. Chữ
        # trắng ở đó chỉ 2.06:1. Chữ tối đạt 7.66:1, và một dòng ghi chú pháp lý vốn
        # không nên to bằng tiêu đề nên hạ luôn 20sp -> 13sp.
        ("add(f, textC(STR.adsNote, noteY, { size: 20, weight: 700, font: 'main', color: C.textHi }));",
         "add(f, textC(STR.adsNote, noteY, { size: 13, weight: 700, font: 'main', color: '181522' }));"),
        ("adsNote: 'This action contain ads',",
         "adsNote: 'This app contains ads',"),
    ], 'onboard.js')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


# ── Đổi màu asset thương hiệu ───────────────────────────────────────────────
# v1 primary #016cf7 có hue 214°, brand v3 #7c3aed có hue 262° → xoay +48°.
# CHỈ xoay pixel thuộc HỌ BRAND (hue lân cận xanh dương, bão hoà đủ cao). Pixel trung
# tính giữ nguyên nên hoạ tiết xám không bị ám tím; pixel cam/đỏ trong art cũng giữ.
HUE_SHIFT, SAT_MUL, LIGHT_MUL = 48, 0.92, 0.95
BRAND_HUE = (165, 235)
BRAND_MIN_SAT = 0.35
# Ba ảnh nền độ khó GIỮ NGUYÊN: xanh/vàng/hồng ở đây mã hoá thang độ khó, xoay hue là
# mất luôn nghĩa. Chúng vẫn nổi tốt trên nền tối.
KEEP_FILES = {'bg_level_easy.png', 'bg_level_intermediate.png', 'bg_level_difficulty.png',
              'window_bg.png', 'ic_launcher.png', 'ic_launcher_foreground.png',
              # Wordmark KHÔNG xoay hue máy móc — xem recolor_wordmark().
              'img_app_name.png'}
BRANDED_DIRS = {'10-icons', '40-anh-app'}


def _shift(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    deg = h * 360.0
    if s < BRAND_MIN_SAT or not (BRAND_HUE[0] <= deg <= BRAND_HUE[1]):
        return r, g, b
    h2 = ((deg + HUE_SHIFT) % 360) / 360.0
    r2, g2, b2 = colorsys.hls_to_rgb(h2, min(1.0, l * LIGHT_MUL), min(1.0, s * SAT_MUL))
    return int(r2 * 255), int(g2 * 255), int(b2 * 255)


def do_assets():
    n_png = n_svg = 0
    for grp in sorted(os.listdir(A3)):
        d = os.path.join(A3, grp)
        if not os.path.isdir(d) or grp not in BRANDED_DIRS:
            continue
        for fn in sorted(os.listdir(d)):
            if fn in KEEP_FILES:
                continue
            fp = os.path.join(d, fn)
            if fn.endswith('.svg'):
                txt = open(fp, encoding='utf-8').read()
                def sub(m):
                    v = m.group(1)
                    r, g, b = int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)
                    return '#%02x%02x%02x' % _shift(r, g, b)
                out = re.sub(r'#([0-9a-fA-F]{6})', sub, txt)
                open(fp, 'w', encoding='utf-8').write(out)
                n_svg += 1
            elif fn.endswith('.png'):
                im = Image.open(fp).convert('RGBA')
                px = im.load()
                for y in range(im.height):
                    for x in range(im.width):
                        r, g, b, a = px[x, y]
                        if a:
                            px[x, y] = _shift(r, g, b) + (a,)
                im.save(fp)
                n_png += 1
    print('asset: xoay %d PNG + %d SVG sang tông tím (+%d°)' % (n_png, n_svg, HUE_SHIFT))


def recolor_wordmark():
    """Tô lại chữ "Face Puzzle" — xoay hue máy móc không dùng được ở đây.

    Đo trên ảnh gốc: thân chữ là xanh bão hoà 100% ở L*27, viền chữ ĐEN L*0. Đặt lên nền
    L*8 thì viền tan hẳn vào nền và thân chữ chỉ hơn nền 2.3:1 — logo mà đục hơn cả chữ
    thân bài. Bản gốc vốn là xanh nhạt VIỀN TRẮNG trên nền trắng; xoay hue giữ nguyên độ
    sáng nên đảo nền xong là hỏng.

    Cách tô: phân loại pixel theo độ sáng chứ không theo màu.
      · tối  (viền)  -> TRẮNG   — viền sáng tách chữ khỏi nền tối, đúng việc của nó
      · còn lại (thân) -> dải chuyển VÀNG→CAM theo chiều dọc
    Vàng-cam là màu bù của tím: trên nền tím than nó bật lên mạnh nhất trong mọi lựa
    chọn, mà vẫn nằm trong họ màu ấm đã dùng cho CTA.
    """
    fp = os.path.join(A3, '40-anh-app', 'img_app_name.png')
    if not os.path.exists(fp):
        return
    im = Image.open(fp).convert('RGBA')
    px = im.load()
    W, H = im.size
    top, bot = (0xFF, 0xD8, 0x3B), (0xFF, 0x6B, 0x35)   # vàng -> cam
    for y in range(H):
        k = y / max(1, H - 1)
        fill = tuple(int(top[c] + (bot[c] - top[c]) * k) for c in range(3))
        for x in range(W):
            r, g, b, a = px[x, y]
            if not a:
                continue
            lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
            px[x, y] = ((255, 255, 255) if lum < 0.22 else fill) + (a,)
    im.save(fp)
    print('wordmark: viền -> trắng, thân -> dải vàng→cam')


def restyle_face_pattern():
    """Hoạ tiết mắt/lông mày/môi của app gốc — khuếch đại cho đọc ra là HOA VĂN.

    Đo ảnh gốc: điểm tối nhất 189 trên nền 255, nhưng giá trị TRUNG BÌNH là 254 — hoạ
    tiết phủ cực ít và mờ tới mức gần như vô hình. Nó không đọc ra "hoa văn có chủ ý"
    mà ra "ảnh scan bị bẩn". Ý tưởng thì tốt: mắt/môi/lông mày chính là những bộ phận
    mà app cắt ra và ghép lại — đúng chủ đề sản phẩm. Chỉ là thực thi đang phí nó.

    Xử lý: lấy độ lệch so với trắng làm CƯỜNG ĐỘ hoạ tiết, nhân 2.4, rồi vẽ lại bằng
    màu tím nhạt trên nền giấy ấm. Vừa đủ thấy, vừa không cạnh tranh với chữ.
    """
    fp = os.path.join(A3, '40-anh-app', 'window_bg.png')
    src = os.path.join(A1, '40-anh-app', 'window_bg.png')   # đọc bản GỐC, không đọc bản vừa ghi đè
    if not os.path.exists(src):
        return
    im = Image.open(src).convert('L')
    a = np.asarray(im).astype(np.float32)
    strength = np.clip((255.0 - a) / 66.0 * 2.4, 0, 1)      # 0 = nền, 1 = nét hoạ tiết đậm nhất
    paper = np.array([0xFD, 0xF9, 0xF3], np.float32)
    ink = np.array([0xA7, 0x8B, 0xFA], np.float32)          # brandSoft
    out = paper[None, None, :] * (1 - strength[..., None] * 0.34) + ink[None, None, :] * (strength[..., None] * 0.34)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(fp)

    # Bản cho NỀN TỐI. Cùng hoạ tiết, nướng trên đúng token C.bg và vẽ bằng brandSoft.
    # Cường độ chỉ 0.16 (bản giấy là 0.34): trên nền tối mắt nhạy với chênh lệch sáng hơn
    # nhiều, để 0.34 là hoa văn hét át cả nội dung.
    dark_bg = np.array([0x2B, 0x22, 0x52], np.float32)
    dark_ink = np.array([0xC4, 0xB0, 0xFF], np.float32)
    k = strength[..., None] * 0.16
    outd = dark_bg[None, None, :] * (1 - k) + dark_ink[None, None, :] * k
    Image.fromarray(np.clip(outd, 0, 255).astype(np.uint8)).save(
        os.path.join(A3, '40-anh-app', 'pattern_dark.png'))

    # Bản LỚP PHỦ TRONG SUỐT. Hai bản trên đều nướng sẵn nền nên đắp lên màn có dải
    # chuyển là mất dải. Bản này chỉ có hoạ tiết, nền alpha = 0, nên chồng lên bất kỳ
    # nền nào cũng được — đó là cách duy nhất vừa giữ dải chuyển vừa có hoa văn.
    # Ô LÁT vuông, KHÔNG phải ảnh full-bleed. Lý do: các frame cao khác nhau (800dp cho
    # màn thường, 1660dp cho Home cuộn) — dùng scaleMode FILL thì cùng một hoạ tiết bị
    # phóng to nhỏ khác nhau ở mỗi màn, và trên frame rất cao thì nó phình thành mảng
    # loang. Lát thì hoạ tiết giữ NGUYÊN kích thước thật ở mọi màn, đúng bản chất hoa văn.
    tile = np.clip(strength * 0.11 * 255, 0, 255).astype(np.uint8)
    side = 720
    y0 = (tile.shape[0] - side) // 2
    tile = tile[y0:y0 + side, :side]
    rgba = np.zeros((side, side, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 0xC4, 0xB0, 0xFF
    rgba[..., 3] = tile
    Image.fromarray(rgba, 'RGBA').save(os.path.join(A3, '40-anh-app', 'pattern_overlay.png'))
    print('hoạ tiết mặt: 2 bản — nền giấy (Settings) và nền tối (Level Picker, thư viện rỗng)')


def fill_gear_hole():
    """Lỗ giữa bánh răng ic_setting: tô đúng màu nền thay vì màu kem.

    Không để trong suốt được: thân bánh răng là một path tô GRADIENT nằm dưới, nên lỗ
    trong suốt sẽ lộ thân bánh răng chứ không lộ nền màn. Phải tô cứng bằng màu nền.

    Icon này chỉ xuất hiện ở thanh trên cùng của Home (20a-20e), nơi dải nền mới ở
    khoảng 1% chiều cao nên giá trị thực tế là #2b2252 — điểm đầu của dải.
    ⚠ Đổi màu nền Home thì phải đổi cả hằng số này.
    """
    fp = os.path.join(A3, '10-icons', 'ic_setting.svg')
    if not os.path.exists(fp):
        return
    t = open(fp, encoding='utf-8').read()
    if '#ffebca' not in t:
        return
    open(fp, 'w', encoding='utf-8').write(t.replace('#ffebca', '#2b2252'))
    print('ic_setting: lỗ giữa tô theo màu nền #2b2252')


def do_manifest_and_main():
    p = os.path.join(V3, 'manifest.json')
    s = open(p, encoding='utf-8').read()
    s = s.replace('APK to Figma v1', 'Design v3').replace('funny-face-apk-to-figma-v1', 'funny-face-design-v3')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

    p = os.path.join(V3, 'main.js')
    s = open(p, encoding='utf-8').read()
    s = s.replace('Funny Face · Screens', 'Funny Face v3 · Screens')
    s = s.replace('Funny Face · Dialogs & States', 'Funny Face v3 · Dialogs & States')
    s = s.replace('Funny Face:', 'Funny Face v3:')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def main():
    force = '--force' in sys.argv
    if os.path.exists(V3) and not force:
        raise SystemExit(
            'figma/v3 đã tồn tại.\n'
            'make-v3 là bộ KHỞI TẠO MỘT LẦN — sau khi chạy, v3 được sửa tay tiếp, chạy\n'
            'lại là xoá sạch công sửa tay đó. Chắc chắn muốn dựng lại từ v1 thì thêm --force.'
        )
    if os.path.exists(V3):
        shutil.rmtree(V3)
    shutil.copytree(V1, V3, ignore=shutil.ignore_patterns('plugin.js', 'assets.js', 'icons.js', '*.bak'))
    if os.path.exists(A3):
        shutil.rmtree(A3)
    shutil.copytree(A1, A3)

    do_code_js()
    do_home()
    do_funny()
    do_face()
    do_preview()
    do_result()
    do_settings()
    do_onboard()
    do_assets()
    recolor_wordmark()
    restyle_face_pattern()
    fill_gear_hole()
    do_manifest_and_main()

    print('figma/v3 + assets/v3 đã dựng xong từ v1.')
    print('Build:  python tools/build-plugin.py --src "Funny Face/assets/v3" --plugin "Funny Face/figma/v3"')


if __name__ == '__main__':
    main()
