#!/usr/bin/env python3
# Round 7: neighbors of the blog + 5ch thread3 parse + precision dump of 5ch2 list region
import html, re, ssl, urllib.request, urllib.parse, pathlib

OUT = pathlib.Path("/Users/wangluke/.hermes/cache/scratch/impact-cheats")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "ja,en;q=0.8"}

def strip_html(s):
    s = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|li|tr|h\d|table|ul|ol|blockquote|dd|dt|section|article)>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\u3000]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()

def fetch(url):
    safe = urllib.parse.quote(url, safe=":/?&=#%")
    req = urllib.request.Request(safe, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.read()
    except ssl.SSLError:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
            return r.read()

PAGES = [
    ("ameblo-4", "https://ameblo.jp/nanisiyou/entry-10255463493.html"),
    ("ameblo-5", "https://ameblo.jp/nanisiyou/entry-10295514216.html"),
]
for name, url in PAGES:
    try:
        raw = fetch(url)
        t = None
        for e in ("utf-8", "cp932", "euc_jp", "latin-1"):
            try:
                t = raw.decode(e)
                enc = e
                break
            except Exception:
                pass
        if t is None:
            t = raw.decode("utf-8", "replace")
            enc = "utf-8r"
        head = t[:3000].lower()
        body = strip_html(t) if ("<html" in head or "</" in head) else t
        (OUT / f"{name}.txt").write_text(body, encoding="utf-8")
        (OUT / f"raw_{name}.html").write_text(t, encoding="utf-8")
        print(f"[OK ] {name}: {len(raw)}B enc={enc} text={len(body)}c")
    except Exception as e:
        print(f"[ERR] {name}: {e!r}")

CODE = re.compile(r"[0-9A-Fa-f]{8}[\s:：\-]+[0-9A-Fa-f]{8}")
for nm in ("ameblo-4", "ameblo-5"):
    f = OUT / f"{nm}.txt"
    if not f.exists():
        print(f"\n===== {nm}: MISSING =====")
        continue
    lines = f.read_text(encoding="utf-8").splitlines()
    codes = [l for l in lines if CODE.search(l)]
    print(f"\n===== {nm}: {len(codes)} code lines =====")
    for l in codes[:130]:
        print(" ", l.strip()[:170])
    print(f"--- {nm}: keyword lines ---")
    n = 0
    for l in lines:
        if re.search(r"シャア|C02C|C12C|G-3|Ｇ－３|ガンダム|変更|追加|ok|だめ", l):
            print(" ", l.strip()[:220])
            n += 1
            if n >= 120:
                break
    rp = OUT / f"raw_{nm}.html"
    if rp.exists():
        ids = sorted(set(re.findall(r"entry-(1\d{10})", rp.read_text(encoding="utf-8", errors="replace"))))
        print(f"--- {nm}: entry ids ---")
        for i in ids:
            print("   ", i)

p = OUT / "5ch3.raw"
if p.exists():
    raw = p.read_bytes()
    txt = None
    for enc in ("utf-8", "cp932", "euc_jp", "shift_jis"):
        try:
            txt = raw.decode(enc)
            print("\n5ch3 decode:", enc)
            break
        except Exception:
            pass
    if txt is None:
        txt = raw.decode("utf-8", "replace")
    body = strip_html(txt)
    (OUT / "5ch3.txt").write_text(body, encoding="utf-8")
    lines = body.splitlines()
    print("5ch3 lines:", len(lines))
    print("--- 5ch3: keywords (シャア専用/C02C/C12C/BG-3/変更) ---")
    n = 0
    for i, l in enumerate(lines):
        if re.search(r"シャア専用|C02C|C12C|BG-3|G-3|変更コード|ください", l):
            print(i, l.strip()[:220])
            n += 1
            if n >= 120:
                break
    print("--- 5ch3: code lines w/ context (cap 120) ---")
    n = 0
    for i, l in enumerate(lines):
        if CODE.search(l):
            ctx = " | ".join(lines[max(0, i - 1): i + 2])
            print(i, ctx[:240])
            n += 1
            if n >= 120:
                break
else:
    print("\n5ch3.raw missing")

f = OUT / "5ch2.txt"
if f.exists():
    lines = f.read_text(encoding="utf-8").splitlines()
    print("\n=== 5ch2.txt lines 1850-1910 (1-indexed) ===")
    for i in range(1849, min(1911, len(lines))):
        print(i + 1, lines[i])
