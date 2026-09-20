# Hợp đồng viết builder màn — Funny Face Figma v1 (Plan 1 Phase 5)

Bạn viết MỘT file: figma/v1/screens/<cụm>.js  — chỉ chứa lời gọi screen()/dialog().
KHÔNG sửa code.js, main.js, hay file của cụm khác. Không import/require gì.

## Môi trường đã có sẵn (khai báo trong code.js, ghép TRƯỚC file của bạn)
Canvas: SCREEN_W=360, SCREEN_H=800 (dp). Không vẽ status bar.

C = { primary:'016cf7', white:'ffffff', black:'000000', textHi:'171716', textSub:'999894',
      textHint:'bab8b6', text2:'a3a3a3', gray:'c0c0c0', grayDark:'6d6969', gray9d:'9d9d9d',
      grayF4:'f4f4f4', grayF5EEE9:'f5eee9', e6e6e5:'e6e6e5', dark141414:'141414', dark2D:'2d2d2d',
      scrim20:'33000000', scrim30:'4d000000', scrimA6:'a61f1e26', red:'ff4342', orange:'f19336' }
  → Màu KHÔNG có trong C thì viết thẳng hex 6 hoặc 8 ký tự ('rrggbb' hoặc 'aarrggbb'), lấy từ spec.
R = { card:12, tile:16, pill:30, sm:8, dialog:16, r12:12, r69:69 }
FONTS keys: 'main'(Lato, mặc định), 'inter', 'montserrat', 'nunito', 'onest', 'poppins', 'roboto'
  Theme app là LIGHT (Theme.AppCompat.Light.NoActionBar), chữ mặc định 14sp màu C.textHi, font Lato.

## Helper (chữ ký chính xác)
frame(name,x,y,w,h,o)   o={fill,opacity,gradient:[a,b],gradientDir:'h'|'v',image,scaleMode,
                           radius,radiusTop,stroke,strokeOpacity,strokeW,shadow,clip}
rect(name,x,y,w,h,o)    o như frame + rotate
ellipse(name,x,y,w,h,o) o={fill,image,gradient,stroke,strokeW}
text(chars,x,y,o)       o={size,weight,font,color,opacity,w,h,align:'LEFT'|'CENTER'|'RIGHT',
                           valign:'TOP'|'CENTER'|'BOTTOM',lineHeight,gradient,rotate}
textC(chars,y,o)        text căn giữa toàn chiều rộng màn
img(name,x,y,w,h,mode)  ảnh từ ASSETS theo KHOÁ = tên file không đuôi; mode 'FIT'|'FILL'
icon(name,x,y,w,h)      SVG từ ICONS, tự lùi về ảnh PNG nếu không có SVG
svgNode(name,x,y,w,h)   chỉ SVG
vpath(parent,x,y,w,h,vb,d,o)  vẽ path tự chế, vb='24 24', o={fill,stroke,sw,name}
photo(parent,x,y,w,h,key,mode,r)  ảnh thật nếu có, KHÔNG có thì tự thành placeholder có nhãn
remoteTile(parent,x,y,w,h,label,r)  ô placeholder có nhãn cho nội dung runtime
adSlot(parent,x,y,w,h,label)        ô AD SLOT có nhãn
toolbar(parent,title,o)  o={h,fill,transparent,back:false,size,font,rightText,rightSize,
                            rightColor,divider:false}
dcard(f,w,h,o)   scrim + thẻ dialog căn giữa → trả về thẻ để add() con vào
sheet(f,h,o)     scrim + bottom sheet
add(parent,a,b,c,...)   append, tự bỏ qua null
grow(f,h)        nới cao frame nếu nội dung vượt (dùng cho list dài)

## Đăng ký màn
screen('<số thứ tự> · <Tên màn>', '<nguồn: file:dòng + ghi chú runtime>', (f) => { ... });
dialog('<số> · <Tên dialog/state>', '<nguồn>', (f) => { ... });
  - screen() → trang "Screens"; dialog() → trang "Dialogs & States".
  - MỖI runtime state là MỘT lời gọi riêng. Đặt tên có hậu tố state, vd
    '03 · Home · Face Puzzle tab', '03b · Home · Funny Puzzle tab'.
  - Tham số 2 (note) sẽ được ghi vào setPluginData('source') — ghi file:dòng để truy vết.

## LUẬT BẮT BUỘC (Plan 1 Phase 5)
1. MỖI layer phải truy được về 1 view XML hoặc 1 lệnh code trong spec của bạn.
   Không truy được ⇒ XOÁ. Không thêm caption/nhãn trang trí trùng tên frame.
2. Dùng SỐ THẬT từ spec (x/y/w/h dp, hex, sp, chuỗi đã resolve). Không làm tròn cho đẹp,
   không bịa. Chuỗi phải là chuỗi đã resolve, không phải @string/....
3. Ảnh: dùng KHOÁ = tên file trong assets/v1/ (xem danh sách bên dưới). Ảnh KHÔNG có trong
   APK/CDN → dùng photo()/remoteTile() để nó tự thành placeholder CÓ NHÃN. Không thay ảnh khác.
4. Quảng cáo → adSlot() có nhãn placement. Lottie/PAG/video → vẽ khung tĩnh + ghi tên asset gốc
   trong note. Camera live/ảnh người dùng → remoteTile() có nhãn.
5. Nội dung cao hơn 800dp (list dài) → gọi grow(f, y + padding) ở cuối builder, đừng để bị cắt.
6. Không để frame đè nhau trong cùng builder. verify.js sẽ bắt.

## KHOÁ ảnh có sẵn trong assets/v1 (dùng đúng tên này)
10-icons/      26 SVG: ic_back_1 ic_back_2 ic_close ic_delete ic_empty ic_gallery_btn ic_home
               ic_layers ic_music ic_pause_filter ic_pause_music ic_play_filter ic_play_music
               ic_record ic_rotation_camera ic_setting_language ic_setting_policy ic_check_box_selected
               ic_check_box_unselected bg_splash … (xem thư mục để chắc)
20-nhanvat-origin/  20 PNG khoá = field `image` trong data_funny.json (vd Kylian_Mbappe)
21-nhanvat-overlay/ 20 PNG cùng khoá
30-template-v2/     18 PNG khoá = <folder>_<id>  (Face_Puzzle_Video1 … Whirl_Face_Video6)
31-template-v1/     8 PNG khoá = v1_Video1 … v1_Video8
40-anh-app/         11 PNG: window_bg img_app_name ic_splash ic_launcher ic_launcher_foreground
               img_banner_face_puzzle img_banner_funny_puzzle img_notify_puzzle
               bg_level_easy bg_level_intermediate bg_level_difficulty
KHÔNG có (đã xác minh không tồn tại trong APK): img_intro_1/2/3 → dùng remoteTile có nhãn.

## Kiểm tra trước khi báo xong
node --check "figma/v1/screens/<cụm>.js"   (phải sạch)
Báo lại ≤10 dòng: số screen(), số dialog(), khoá ảnh đã dùng, chỗ nào phải placeholder và vì sao.
