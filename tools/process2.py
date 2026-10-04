#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, html, pathlib

BASE = pathlib.Path("/Users/wangluke/.hermes/cache/scratch/impact-cheats")

def strip_html_bytes(b):
    t = None
    for e in ("utf-8", "cp932", "euc_jp", "gb18030", "big5"):
        try:
            t = b.decode(e); break
        except Exception:
            pass
    if t is None:
        t = b.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>", "\n", t)
    t = re.sub(r"(?i)</(p|div|li|tr|h\d|table|ul|ol|blockquote|dd|dt|section|article)>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t\u3000]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()

print("################ teruyuka pages (1-9)")
for i in range(1, 10):
    p = BASE / ("teruyuka-%d.html" % i)
    if not p.exists():
        print("--- teruyuka-%d: MISSING" % i); continue
    t = strip_html_bytes(p.read_bytes())
    (BASE / ("teruyuka-%d.txt" % i)).write_text(t, encoding="utf-8")
    print("===== teruyuka-%d =====" % i)
    print(t[:1300])
    print()

print("################ newwise thread")
p = BASE / "newwise-thread.html"
if p.exists():
    t = strip_html_bytes(p.read_bytes())
    (BASE / "newwise-thread.txt").write_text(t, encoding="utf-8")
    print("total lines:", len(t.splitlines()))
    shown = 0
    for idx, l in enumerate(t.splitlines()):
        if re.search(r"[0-9A-Fa-f]{8}", l) and len(l) < 220:
            print("%d| %s" % (idx, l.strip()[:200])); shown += 1
            if shown >= 80: break
else:
    print("newwise missing")

print()
print("################ a9vg page2")
p = BASE / "a9vg-thread2.html"
if p.exists() and p.stat().st_size > 1000:
    t = strip_html_bytes(p.read_bytes())
    (BASE / "a9vg-thread2.txt").write_text(t, encoding="utf-8")
    print("size:", len(t))
    shown = 0
    for idx, l in enumerate(t.splitlines()):
        if re.search(r"[0-9A-Fa-f]{8}", l) and len(l) < 220:
            print("%d| %s" % (idx, l.strip()[:200])); shown += 1
            if shown >= 80: break
else:
    print("a9vg2 missing/small (will refetch)")

print()
print("################ 5ch3 targeted snippets")
p = BASE / "5ch3.txt"
if p.exists():
    L = p.read_text(encoding="utf-8").splitlines()
    for rng in [(478, 545), (1790, 1818), (365, 400)]:
        print("----- 5ch3 %d-%d -----" % rng)
        for i in range(rng[0]-1, min(rng[1], len(L))):
            print(i+1, L[i][:150])
        print()

print("################ usage-term grep (1機目/2機目/入れ替え etc.)")
terms = re.compile(r"1機目|2機目|1個目|2個目|入れ替え|先頭|一番上|余っ|あまっ|スポット|枠|並び")
count = 0
for f in sorted(BASE.glob("*.txt")):
    if f.name in ("5ch.txt",):
        continue
    try:
        for i, l in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if terms.search(l):
                print("%s:%d: %s" % (f.name, i, l.strip()[:170]))
                count += 1
                if count >= 90: break
    except Exception:
        pass
    if count >= 90:
        break
