// ============================================================================
//  Funny Face — APK → Figma reconstruction (v1)   [TEMPLATE — fill C, FONTS, screens]
//  Canvas 360×800 dp. No status bar. Requires assets.js + icons.js concatenated ABOVE
//  (build-plugin.py produces plugin.js = assets.js + icons.js + this file).
//  Every layer must trace to one XML view or one code instruction — else delete it.
// ============================================================================
const C = {
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
};
const R = { card: 16, tile: 20, pill: 100, sm: 10, dialog: 20, r12: 14, r69: 69 };
// Theme: Base.Theme.FacePuzzle parent Theme.AppCompat.Light.NoActionBar → nền SÁNG.
// windowBackground = @mipmap/window_bg (đã export assets/v1/40-anh-app/window_bg.png)
// android:fontFamily mặc định = @font/lato_regular_400 ; android:textSize = 14sp
const FONTS = {                               // res/font/*.ttf → family Figma (đều là Google Fonts)
  main:       { family: 'Lato',       w: { 100:'Thin', 300:'Light', 400:'Regular', 600:'SemiBold', 700:'Bold', 900:'Black' } },
  inter:      { family: 'Inter',      w: { 400:'Regular', 700:'Bold' } },
  montserrat: { family: 'Montserrat', w: { 400:'Regular', 600:'SemiBold' } },
  nunito:     { family: 'Nunito',     w: { 700:'Bold', 900:'Black' } },
  onest:      { family: 'Onest',      w: { 700:'Bold' } },
  poppins:    { family: 'Poppins',    w: { 400:'Regular', 500:'Medium' } },
  roboto:     { family: 'Roboto',     w: { 500:'Medium' } },
};
const DEFAULT_FONT = 'main';
const SCREEN_W = 360, SCREEN_H = 800;
const LOADED = {};

function rgb(h){h=h.replace('#','');if(h.length===3)h=h.split('').map(c=>c+c).join('');if(h.length===8)h=h.slice(2);return{r:parseInt(h.slice(0,2),16)/255,g:parseInt(h.slice(2,4),16)/255,b:parseInt(h.slice(4,6),16)/255};}
function alphaOf(h){h=h.replace('#','');return h.length===8?parseInt(h.slice(0,2),16)/255:undefined;}
function solid(h,o){const a=o!==undefined?o:alphaOf(h);const p={type:'SOLID',color:rgb(h)};if(a!==undefined)p.opacity=a;return p;}
function grad(a,b,dir){const t=dir==='h'?[[1,0,0],[0,1,0]]:[[0,1,0],[-1,0,1]];return[{type:'GRADIENT_LINEAR',gradientTransform:t,gradientStops:[{position:0,color:Object.assign(rgb(a),{a:alphaOf(a)!==undefined?alphaOf(a):1})},{position:1,color:Object.assign(rgb(b),{a:alphaOf(b)!==undefined?alphaOf(b):1})}]}];}
const imgCache={};
function imageFill(name,scaleMode){if(typeof ASSETS==='undefined'||!ASSETS[name])return null;if(!imgCache[name]){const b=figma.base64Decode?figma.base64Decode(ASSETS[name]):Uint8Array.from(atob(ASSETS[name]),c=>c.charCodeAt(0));imgCache[name]=figma.createImage(b).hash;}const p={type:'IMAGE',scaleMode:scaleMode||'FILL',imageHash:imgCache[name]};if(p.scaleMode==='TILE')p.scalingFactor=0.5;return p;}
function pickFont(fk,weight){const def=FONTS[fk]||FONTS[DEFAULT_FONT];const fam=def.family,want=def.w[weight||400]||def.w[400]||'Regular';if(LOADED[fam]){if(LOADED[fam][want])return{family:fam,style:want};if(LOADED[fam].Regular)return{family:fam,style:'Regular'};const any=Object.keys(LOADED[fam])[0];if(any)return{family:fam,style:any};}const d=FONTS[DEFAULT_FONT].family;if(LOADED[d]&&LOADED[d].Regular)return{family:d,style:'Regular'};return{family:'Roboto',style:'Regular'};}
function frame(name,x,y,w,h,o){o=o||{};const f=figma.createFrame();f.name=name;f.x=x;f.y=y;f.resize(Math.max(w,0.01),Math.max(h,0.01));f.fills=o.fill?[solid(o.fill,o.opacity)]:[];if(o.gradient)f.fills=grad(o.gradient[0],o.gradient[1],o.gradientDir);if(o.image){const p=imageFill(o.image,o.scaleMode);if(p)f.fills=[p];}if(o.radius!==undefined)f.cornerRadius=o.radius;if(o.radiusTop!==undefined){f.topLeftRadius=o.radiusTop;f.topRightRadius=o.radiusTop;}if(o.stroke){f.strokes=[solid(o.stroke,o.strokeOpacity)];f.strokeWeight=o.strokeW||1;}if(o.shadow)f.effects=[{type:'DROP_SHADOW',color:{r:0.04,g:0.02,b:0.10,a:o.shadow===true?0.55:o.shadow},offset:{x:0,y:8},radius:24,spread:-2,visible:true,blendMode:'NORMAL'}];if(o.clip!==undefined)f.clipsContent=o.clip;return f;}
function rect(name,x,y,w,h,o){o=o||{};const r=figma.createRectangle();r.name=name;r.x=x;r.y=y;r.resize(Math.max(w,0.01),Math.max(h,0.01));r.fills=o.fill?[solid(o.fill,o.opacity)]:[];if(o.gradient)r.fills=grad(o.gradient[0],o.gradient[1],o.gradientDir);if(o.image){const p=imageFill(o.image,o.scaleMode);if(p)r.fills=[p];}if(o.radius!==undefined)r.cornerRadius=o.radius;if(o.stroke){r.strokes=[solid(o.stroke,o.strokeOpacity)];r.strokeWeight=o.strokeW||1;}if(o.rotate)r.rotation=o.rotate;return r;}
function ellipse(name,x,y,w,h,o){o=o||{};const e=figma.createEllipse();e.name=name;e.x=x;e.y=y;e.resize(w,h);e.fills=o.fill?[solid(o.fill,o.opacity)]:[];if(o.image){const p=imageFill(o.image,o.scaleMode);if(p)e.fills=[p];}if(o.gradient)e.fills=grad(o.gradient[0],o.gradient[1],o.gradientDir);if(o.stroke){e.strokes=[solid(o.stroke,o.strokeOpacity)];e.strokeWeight=o.strokeW||1;}return e;}
function text(chars,x,y,o){o=o||{};const t=figma.createText();t.fontName=pickFont(o.font,o.weight);t.characters=chars;t.fontSize=o.size||14;t.fills=o.gradient?grad(o.gradient[0],o.gradient[1],o.gradientDir||'v'):[solid(o.color||C.textHi,o.opacity)];t.x=x;t.y=y;if(o.w){t.textAutoResize=o.h?'NONE':'HEIGHT';t.resize(o.w,o.h||Math.max(t.height,1));}else t.textAutoResize='WIDTH_AND_HEIGHT';if(o.align)t.textAlignHorizontal=o.align;if(o.valign)t.textAlignVertical=o.valign;if(o.lineHeight)t.lineHeight={value:o.lineHeight,unit:'PIXELS'};if(o.rotate)t.rotation=o.rotate;t.name=chars.length>26?chars.slice(0,26)+'…':chars;return t;}
function textC(chars,y,o){o=Object.assign({w:SCREEN_W,align:'CENTER'},o||{});return text(chars,0,y,o);}
function img(name,x,y,w,h,mode){return rect(name,x,y,w,h,{image:name,scaleMode:mode||'FIT'});}
var ICON_ON_LIGHT=' ic_setting_language ic_setting_policy ic_setting_term ic_setting_share ic_tick_disabled ic_tick_enabled ';function tintIcon(sv){return sv.replace(/(fill|stroke)="#([0-9a-fA-F]{6})"/g,function(m,att,hx){var r=parseInt(hx.slice(0,2),16),g=parseInt(hx.slice(2,4),16),b=parseInt(hx.slice(4,6),16);var mx=Math.max(r,g,b),mn=Math.min(r,g,b);var sat=mx?(mx-mn)/mx:0;var lum=(0.2126*r+0.7152*g+0.0722*b)/255;return (sat<0.25&&lum<0.45)?att+'="#f5f3ff"':m;});}
function iconDark(name,x,y,w,h){var keep=ICON_ON_LIGHT;ICON_ON_LIGHT=' '+name+' ';var n=icon(name,x,y,w,h);ICON_ON_LIGHT=keep;return n;}
function svgNode(name,x,y,w,h){if(typeof ICONS==='undefined'||!ICONS[name])return null;const n=figma.createNodeFromSvg(ICON_ON_LIGHT.indexOf(' '+name+' ')>=0?ICONS[name]:tintIcon(ICONS[name]));n.name=name;n.x=x;n.y=y;n.resize(w,h);return n;}
function icon(name,x,y,w,h){const s=svgNode(name,x,y,w,h);if(s)return s;if(typeof ASSETS!=='undefined'&&ASSETS[name])return img(name,x,y,w,h,'FIT');return null;}
function screenBg(f,h){const bg=rect('bg',0,0,SCREEN_W,h,{gradient:['2b2252','3d3070'],gradientDir:'v'});f.appendChild(bg);const pat=rect('hoạ tiết mặt',0,0,SCREEN_W,h,{image:'pattern_overlay',scaleMode:'TILE'});f.appendChild(pat);return{bg:bg,pat:pat};}
function patternOn(f,h){const p=rect('hoạ tiết mặt',0,0,SCREEN_W,h,{image:'pattern_overlay',scaleMode:'TILE'});f.appendChild(p);return p;}
function dashRect(parent,x,y,w,h,r,color,sw,dash){const sv='<svg xmlns="http://www.w3.org/2000/svg" width="'+w+'" height="'+h+'">'+'<rect x="'+(sw/2)+'" y="'+(sw/2)+'" width="'+(w-sw)+'" height="'+(h-sw)+'" rx="'+r+'" '+'fill="none" stroke="#'+color+'" stroke-width="'+sw+'" stroke-dasharray="'+(dash||'12,9')+'" stroke-linecap="round"/></svg>';const n=figma.createNodeFromSvg(sv);n.name='khung nét đứt';n.x=x;n.y=y;n.resize(w,h);parent.appendChild(n);return n;}
function add(parent){for(let i=1;i<arguments.length;i++)if(arguments[i])parent.appendChild(arguments[i]);return parent;}
function grow(f,h){if(h>f.height)f.resize(SCREEN_W,h);}
function vpath(parent,x,y,w,h,vb,d,o){o=o||{};const svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+vb+'"><path d="'+d+'" fill="'+(o.fill?'#'+o.fill:'none')+'"'+(o.stroke?' stroke="#'+o.stroke+'" stroke-width="'+(o.sw||2)+'" stroke-linecap="round" stroke-linejoin="round"':'')+'/></svg>';const n=figma.createNodeFromSvg(svg);n.name=o.name||'icon';n.x=x;n.y=y;n.resize(w,h);add(parent,n);return n;}
function backChevron(p,x,y,s,c){return vpath(p,x,y,s,s,'24 24','M15 5 L8 12 L15 19',{stroke:c||C.white,sw:2.4,name:'ic_back'});}
// image placeholder for remote/runtime content that isn't in the APK (label it honestly)
function remoteTile(parent,x,y,w,h,label,r){const g=frame('remote · '+(label||''),x,y,w,h,{fill:C.surface,stroke:C.line,strokeW:1,radius:r!==undefined?r:R.card,clip:true});add(parent,g);add(g,text(label||'remote',0,h/2-8,{size:10,font:'main',color:C.onDarkSub,w:w,align:'CENTER'}));return g;}
// real photo (downloaded asset) or fallback placeholder
function photo(parent,x,y,w,h,key,mode,r){if(typeof ASSETS!=='undefined'&&ASSETS[key]){const n=rect(key,x,y,w,h,{image:key,scaleMode:mode||'FILL',radius:r});add(parent,n);return n;}return remoteTile(parent,x,y,w,h,key,r);}
// toolbar: back + centered title + optional right text/gear. Match the app's real toolbar geometry.
function toolbar(parent,title,o){o=o||{};const h=o.h||56;const g=frame('Toolbar · '+(title||''),0,0,SCREEN_W,h,o.transparent?{}:{fill:o.fill||C.toolbar});if(o.back!==false){const ic=icon('ic_back',20,(h-24)/2,24,24);if(ic)add(g,ic);else backChevron(g,20,(h-22)/2,22,C.white);}if(title)add(g,text(title,52,0,{size:o.size||18,font:o.font||'main',weight:700,color:C.textHi,w:SCREEN_W-104,h:h,valign:'CENTER',align:'CENTER'}));if(o.rightText)add(g,text(o.rightText,SCREEN_W-80,0,{size:o.rightSize||15,font:'main',weight:700,color:o.rightColor||C.accent,w:60,h:h,valign:'CENTER',align:'RIGHT'}));if(!o.transparent&&o.divider!==false)add(g,rect('divider',0,h-1,SCREEN_W,1,{fill:C.toolbarDiv}));add(parent,g);return g;}
// AD SLOT placeholder (native/banner filled at runtime — not in the APK)
function adSlot(parent,x,y,w,h,label){if(!SHOW_ADS)return null;const g=frame('AD SLOT · '+(label||'Native'),x,y,w,h,{fill:C.surface,stroke:C.line,strokeW:1,radius:R.card});add(g,rect('ad-badge',10,10,26,16,{fill:C.surfaceHi,radius:4}));add(g,text('AD',10,10,{size:9,weight:700,font:'main',color:C.onDarkSub,w:26,h:16,align:'CENTER',valign:'CENTER'}));add(g,text(label||'',0,h/2-8,{size:12,font:'main',color:C.onDarkSub,w:w,align:'CENTER'}));add(parent,g);return g;}
// scrim + centered dialog card; use one artboard per dialog
function dcard(f,w,h,o){o=o||{};add(f,rect('scrim',0,0,SCREEN_W,SCREEN_H,{fill:'000000',opacity:o.scrim!==undefined?o.scrim:0.6}));const y=o.y!==undefined?o.y:(SCREEN_H-h)/2;const d=frame(o.name||'dialog',(SCREEN_W-w)/2,y,w,h,{fill:o.fill||C.card,radius:o.radius!==undefined?o.radius:R.dialog,shadow:true,clip:true});add(f,d);return d;}
function sheet(f,h,o){o=o||{};add(f,rect('scrim',0,0,SCREEN_W,SCREEN_H,{fill:'000000',opacity:o.scrim!==undefined?o.scrim:0.6}));const d=frame(o.name||'sheet',0,SCREEN_H-h,SCREEN_W,h,{fill:o.fill||C.card,radiusTop:o.radius!==undefined?o.radius:20,clip:true});add(f,d);return d;}

// ─── Công tắc quảng cáo ──────────────────────────────────────────────────────
// false = bản GỌN để trình bày: bỏ mọi ô quảng cáo và mọi frame chỉ-để-hiện-ad.
// true  = bản TRUNG THỰC 1:1 với app (ad là phần có thật của UI, Plan 1 yêu cầu dựng).
// Đổi 1 dòng này rồi build lại là chuyển qua lại, KHÔNG mất frame nào.
const SHOW_ADS = false;

// 7 ngon ngu hardcode, DUNG THU TU (data/system/AppSetting.java:44).
// De o code.js chu khong trong screens/onboard.js vi CA hai noi dung: man 12/12b/12c
// (cum onboard) va D71 (cum settings-dialogs). Truoc day D71 tu khai bao lai 2 dong
// ['English','Hindi'] cho "minh hoa" -> nhin vao tuong app chi co 2 ngon ngu.
const LANGS = [
  ['English', 'en'], ['Hindi', 'hi'], ['Spanish', 'es'], ['French', 'fr'],
  ['Portuguese', 'pt'], ['Vietnamese', 'vi'], ['Japanese', 'ja'],
];

const SCREENS=[],DIALOGS=[];
// opts.adOnly = frame này KHÔNG còn gì khi tắt ad (toàn bộ nội dung là quảng cáo)
//               -> bỏ hẳn khỏi registry khi SHOW_ADS=false.
// opts.adDup  = frame này chỉ khác một frame khác ở chỗ CÓ ad -> trùng lặp khi tắt ad.
// opts.excluded = design lead YÊU CẦU BỎ khỏi bản trình bày. Code vẫn giữ nguyên,
//                 bỏ cờ là frame quay lại. Ghi lý do vào note để không ai tưởng là sót.
function screen(name,note,build,opts){opts=opts||{};if(opts.excluded)return;if(!SHOW_ADS&&(opts.adOnly||opts.adDup))return;SCREENS.push({name,note,build});}
function dialog(name,note,build,opts){opts=opts||{};if(opts.excluded)return;if(!SHOW_ADS&&(opts.adOnly||opts.adDup))return;DIALOGS.push({name,note,build});}

// ============================== SCREENS =====================================
// One builder per screen (and per runtime STATE). Every value from the resolved layout/code.
// Builder mỗi màn nằm ở figma/v1/screens/*.js (build-plugin ghép vào đây).

const BUILT_BY = 'funny-face-apk-to-figma';
// Chạy lại plugin nhiều lần phải RA CÙNG KẾT QUẢ, không chồng thêm bộ frame mới.
// Cách làm: đánh dấu mọi frame plugin tạo bằng pluginData BUILT_BY, và khi chạy thì
// XOÁ hết frame mang dấu đó trước (trên mọi trang), đồng thời TÁI DÙNG trang cùng tên
// thay vì tạo trang mới (gói Starter chỉ cho 3 trang/file).
async function clearPrevious(){
  const pages = figma.root.children;
  for (const pg of pages) {
    if (pg.loadAsync) { try { await pg.loadAsync(); } catch (e) {} }
    for (const n of pg.children.slice()) {
      try {
        const marked = n.getPluginData && n.getPluginData('builtBy') === BUILT_BY;
        // Frame do các bản plugin CŨ tạo ra KHÔNG có dấu builtBy -> phải nhận thêm bằng
        // TÊN. Quy ước đặt tên của plugin: "<mã> · <tên màn>" với mã dạng 10 / 10b / 41g /
        // D51 / 90. Mẫu này đủ hẹp để không đụng layer người dùng tự vẽ.
        const legacy = typeof n.name === 'string' && /^D?\d{1,3}[a-z]?\s·\s/.test(n.name);
        if (marked || legacy) n.remove();
      } catch (e) {}
    }
  }
}
// clearPrevious() chi go FRAME, nen trang do ban plugin DOI TRUOC tao ra (tieu de khac di
// mot chut -> findOrCreatePage khong nhan ra de gop) se nam lai duoi dang TRANG RONG. Chay
// nhieu lan thi panel Pages day nhung trang '📱'/'💬' trung nhau. Ham nay don chung, va CHI
// don trang that su rong -> khong bao gio dung vao trang nguoi dung tu tao co noi dung.
function removeStalePages(keep){
  const ours = /Funny Face|📱|💬/;
  for (const pg of figma.root.children.slice()) {
    try {
      if (keep.indexOf(pg) !== -1) continue;
      if (!ours.test(pg.name)) continue;
      if (pg.children && pg.children.length) continue;
      if (figma.root.children.length <= 1) break;   // Figma luon can it nhat 1 trang
      pg.remove();
    } catch (e) {}
  }
}
function findOrCreatePage(title){
  const found = figma.root.children.filter(p => p.name === title);
  if (found.length) {
    for (let k = 1; k < found.length; k++) { try { found[k].remove(); } catch (e) {} }
    return found[0];
  }
  const p = figma.createPage(); p.name = title; return p;
}
// Thu tu tren canvas: theo SO MAN, khong theo thu tu file nguon duoc noi.
// Truoc day SCREENS giu nguyen thu tu dang ky -> build-plugin.py noi screens/*.js theo alphabet
// (face-puzzle, funny-puzzle, home, onboard, ...) nen canvas ra 30 -> 40 -> 20 -> 10 -> 50:
// Splash nam giua thay vi dau. Sap lai cho doc duoc tu trai sang phai, tren xuong duoi.
function flowKey(name){
  const m = /^D?(\d+)([a-z]*)/.exec(String(name || ''));
  return m ? [parseInt(m[1], 10), m[2] || ''] : [9999, ''];
}
function flowOrder(list){
  return list.slice().sort((a, b) => {
    const x = flowKey(a.name), y = flowKey(b.name);
    return x[0] - y[0] || (x[1] < y[1] ? -1 : x[1] > y[1] ? 1 : 0);
  });
}
// Dan luoi: 6 frame/hang. Neu danh sach du dai thi moi NHOM LUONG (chuc: 10 onboarding,
// 20 home, 25 preview Try Now, 30 face puzzle, 40 funny, 50 preview+sound, 60 result,
// 70 settings) bat dau o
// hang moi -> nhin phat ra ngay ranh gioi tung luong.
function layoutGrid(built, y0){
  const GAP_X = 60, GAP_Y = 120, PER_ROW = 6;
  const group = built.length > 8;
  let y = y0 || 0, col = 0, tall = 0, dec = null;
  built.forEach((f) => {
    // Chia theo KHOI 5 chu khong phai khoi 10: 10-14 onboarding · 20-24 home ·
    // 25-29 preview Try Now · 30-34 face puzzle · 40-44 funny · 50-54 preview+sound ·
    // 60-64 result · 70-74 settings. Khoi 10 se gop 25 chung hang voi 20a..20e -> tran hang.
    const d = Math.floor(flowKey(f.name)[0] / 5);
    if (col >= PER_ROW || (group && dec !== null && d !== dec)) {
      y += tall + GAP_Y; col = 0; tall = 0;
    }
    dec = d;
    f.x = col * (SCREEN_W + GAP_X); f.y = y;
    if (f.height > tall) tall = f.height;
    col += 1;
  });
  return y + tall + GAP_Y;
}
async function buildPage(title,list){const page=findOrCreatePage(title);const built=flowOrder(list).map(s=>{const f=frame(s.name,0,0,SCREEN_W,SCREEN_H,{fill:C.bg,clip:true});try{s.build(f);}catch(e){add(f,text('BUILD ERR: '+s.name+' — '+e.message,8,8,{size:11,color:'ff5555',w:SCREEN_W-16}));}f.setPluginData('source',s.note||'');f.setPluginData('builtBy',BUILT_BY);page.appendChild(f);return f;});layoutGrid(built,0);return page;}
