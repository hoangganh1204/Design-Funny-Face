// main.js — điểm chạy, build-plugin ghép SAU screens/*.js
// Gói Free của Figma giới hạn 3 trang. Nếu createPage() thất bại (hết quota) thì đổ
// nội dung vào TRANG HIỆN TẠI, xếp tiếp xuống dưới phần đã dựng — không mất frame nào.
let __y0 = 0;
async function buildSafe(title, list, first){
  try {
    const p = await buildPage(title, list);
    if (p && p.children && p.children.length) return p;
    throw new Error('trang rỗng');
  } catch (e) {
    const page = figma.currentPage;
    const built = flowOrder(list).map(sc => {
      const f = frame(sc.name, 0, 0, SCREEN_W, SCREEN_H, { fill: C.white, clip: true });
      try { sc.build(f); } catch (err) {
        add(f, text('BUILD ERR: ' + sc.name + ' — ' + err.message, 8, 8,
                    { size: 11, color: 'ff5555', w: SCREEN_W - 16 }));
      }
      f.setPluginData('source', sc.note || '');
      f.setPluginData('builtBy', BUILT_BY);
      page.appendChild(f); return f;
    });
    __y0 = layoutGrid(built, __y0) + 200;
    figma.notify('Hết quota trang (gói Free) — đã dựng "' + title + '" vào trang hiện tại.');
    return page;
  }
}
async function main(){if(figma.loadAllPagesAsync)await figma.loadAllPagesAsync();await clearPrevious();const fams={};Object.keys(FONTS).forEach(k=>{fams[FONTS[k].family]=FONTS[k].w;});for(const fam of Object.keys(fams)){LOADED[fam]={};for(const st of new Set(Object.values(fams[fam]))){try{await figma.loadFontAsync({family:fam,style:st});LOADED[fam][st]=true;}catch(e){}}}try{await figma.loadFontAsync({family:'Roboto',style:'Regular'});LOADED['Roboto']={Regular:true};}catch(e){}const p1=await buildSafe('📱 Funny Face · Screens',SCREENS,true);const p2=await buildSafe('💬 Funny Face · Dialogs & States',DIALOGS,false);await figma.setCurrentPageAsync(p1);removeStalePages([p1,p2]);figma.viewport.scrollAndZoomIntoView(p1.children);figma.closePlugin('Funny Face: '+SCREENS.length+' screens + '+DIALOGS.length+' dialogs/states.');}
main();
