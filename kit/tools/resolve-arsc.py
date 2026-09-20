#!/usr/bin/env python3
"""resolve-arsc.py — resolve an Android resource id → its file path / value, straight from
resources.arsc inside the APK. Use when jadx/apktool `public.xml` dropped an entry (a
stripped name) or when you need the real file behind an obfuscated id.

    python3 resolve-arsc.py app.apk 0x7f08016f
    python3 resolve-arsc.py app.apk 2131231087
    python3 resolve-arsc.py app.apk --type drawable --dump   # list every drawable id → path

A NULL entry (offset 0xffffffff in every config) usually means the resource lives in a
SPLIT APK (base+config/density/language splits) not present in this file — merge the splits
(`.apks`/`.xapk`/bundletool) or fetch that split, then re-run.
"""
import struct, sys, zipfile

def load(apk):
    return zipfile.ZipFile(apk).read('resources.arsc')

class Arsc:
    def __init__(self, d):
        self.d = d
        self.u16 = lambda o: struct.unpack_from('<H', d, o)[0]
        self.u32 = lambda o: struct.unpack_from('<I', d, o)[0]
        self.u8  = lambda o: d[o]
        assert self.u16(0) == 0x0002, 'not a resources.arsc'
        self.global_strings = self._pool(12)
        self.types = {}          # typeName -> typeId
        self.type_chunks = {}    # typeId -> [chunk offsets]
        self._walk(12 + self.u32(16), len(d))

    def _pool(self, off):
        u16, u32, d = self.u16, self.u32, self.d
        cnt = u32(off + 8); flags = u32(off + 16); sstart = u32(off + 20)
        utf8 = (flags & 256) != 0; out = []
        for i in range(cnt):
            so = off + sstart + u32(off + 28 + i * 4); p = so
            if utf8:
                n = d[p]; p += 1
                if n & 0x80: p += 1
                b = d[p]; p += 1
                if b & 0x80: b = ((b & 0x7f) << 8) | d[p]; p += 1
                out.append(d[p:p + b].decode('utf-8', 'replace'))
            else:
                n = u16(so); p = so + 2
                if n & 0x8000: n = ((n & 0x7fff) << 16) | u16(p); p += 2
                out.append(d[p:p + n * 2].decode('utf-16-le', 'replace'))
        return out

    def _walk(self, off, stop):
        u16, u32 = self.u16, self.u32
        p = off
        while p + 8 <= stop:
            t = u16(p); hs = u16(p + 2); cs = u32(p + 4)
            if cs < 8 or p + cs > stop: return
            if t == 0x0200:                       # PACKAGE
                type_strings_off = p + u32(p + 268)
                self._type_names = self._pool(type_strings_off)
                self._walk(p + hs, p + cs)
            elif t == 0x0201:                     # TABLE_TYPE
                tid = self.u8(p + 8)
                self.type_chunks.setdefault(tid, []).append(p)
                nm = getattr(self, '_type_names', [])
                if tid - 1 < len(nm): self.types[nm[tid - 1]] = tid
            p += cs

    def entry_value(self, typeid, entry):
        """Return (path_or_value, dataType) for the first config where the entry exists, else None."""
        u16, u32, d = self.u16, self.u32, self.d
        for p in self.type_chunks.get(typeid, []):
            hs = u16(p + 2); ec = u32(p + 12); es = u32(p + 16); flags8 = self.u8(p + 9)
            if entry >= ec: continue
            if flags8 & 0x01:                     # FLAG_SPARSE: array of (idx u16, off u16)
                base = p + hs; eo = None
                for i in range(ec):
                    idx = u16(base + i * 4); off = u16(base + i * 4 + 2)
                    if idx == entry: eo = off * 4; break
                if eo is None: continue
            else:
                eo = u32(p + hs + entry * 4)
                if eo == 0xffffffff: continue
            ent = p + es + eo
            ehsz = u16(ent); eflags = u16(ent + 2)
            if eflags & 0x0001:                   # COMPLEX map (shape/selector/layer-list)
                return ('<complex map: shape/selector/layer-list>', -1)
            vo = ent + ehsz; dt = self.u8(vo + 3); data = u32(vo + 4)
            if dt == 0x03 and data < len(self.global_strings):
                return (self.global_strings[data], dt)
            return ('0x%08x (dataType=0x%02x)' % (data, dt), dt)
        return None

def main():
    a = sys.argv
    if len(a) < 2: sys.exit(__doc__)
    ar = Arsc(load(a[1]))
    if '--dump' in a:
        tname = a[a.index('--type') + 1] if '--type' in a else 'drawable'
        tid = ar.types.get(tname)
        if not tid: sys.exit('unknown type %s; known: %s' % (tname, ', '.join(sorted(ar.types))))
        maxe = max(u32 for u32 in [struct.unpack_from('<I', ar.d, p + 12)[0] for p in ar.type_chunks[tid]])
        for e in range(maxe):
            v = ar.entry_value(tid, e)
            if v: print('0x7f%02x%04x  %s' % (tid, e, v[0]))
        return
    rid = a[2]
    rid = int(rid, 16) if rid.lower().startswith('0x') else int(rid)
    typeid = (rid >> 16) & 0xff; entry = rid & 0xffff
    v = ar.entry_value(typeid, entry)
    if v is None:
        print('id 0x%08x (type=0x%02x entry=0x%04x): NULL in every config → likely in a SPLIT APK '
              '(merge base+config splits and retry).' % (rid, typeid, entry))
    else:
        print('id 0x%08x → %s' % (rid, v[0]))

if __name__ == '__main__':
    main()
