#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Round 3: s-rpg-navi BFS 续抓（上限700, 过滤静态资源, 增量+清单）"""
import re, os, time, urllib.request, urllib.parse, html as H

OUT = "/Volumes/D2T/projects/srw-game-modding/research/hidden-elements"
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
SLEEP = 0.4
JUNK = (".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".xml", ".woff", ".woff2", ".svg", ".webp", ".mp4")
manifest = os.path.join(OUT, "_manifest.txt")

def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "ja,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    for enc in ("utf-8", "cp932", "euc-jp"):
        try:
            return data.decode(enc)
        except Exception:
            continue
    return data.decode("utf-8", "replace")

def strip_tags(s):
    s = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", s)
    s = re.sub(r"(?is)<br\s*/?>", "\n", s)
    s = re.sub(r"(?is)<(li|tr)[^>]*>", "\n- ", s)
    s = re.sub(r"(?is)</(p|div|li|tr|h[1-6]|table|td)>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = H.unescape(s)
    s = re.sub(r"[ \t\u3000]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()

def hrefs(base, h):
    out, seen = [], set()
    for m in re.finditer(r"""href=["']([^"'#]+)["']""", h, re.I):
        u = urllib.parse.urljoin(base, m.group(1))
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

def save_page(name, url):
    raw_p = os.path.join(OUT, "_raw", name + ".html")
    txt_p = os.path.join(OUT, name + ".txt")
    os.makedirs(os.path.dirname(raw_p), exist_ok=True)
    if os.path.exists(raw_p):
        try:
            return open(raw_p, encoding="utf-8", errors="replace").read(), False
        except Exception:
            return "", False
    try:
        h = get(url)
        open(raw_p, "w", encoding="utf-8").write(h)
        t = strip_tags(h)
        open(txt_p, "w", encoding="utf-8").write(
            "# source: %s\n# fetched: %s\n\n%s" % (url, time.strftime("%Y-%m-%d %H:%M"), t))
        with open(manifest, "a", encoding="utf-8") as f:
            f.write("%s\t%s\t%s\n" % (name, url, time.strftime("%Y-%m-%d %H:%M")))
        print("OK  %-36s %7d chars" % (name, len(t)))
        return h, True
    except Exception as e:
        print("FAIL %-35s %s (%s)" % (name, e, url))
        return "", False

print("===== s-rpg-navi BFS 续抓 =====")
queue = ["https://s-rpg-navi.com/srw-impact/",
         "https://s-rpg-navi.com/srw-impact/scene/",
         "https://s-rpg-navi.com/srw-impact/chart/",
         "https://s-rpg-navi.com/srw-impact/tips/",
         "https://s-rpg-navi.com/srw-impact/pilot/"]
seen, new = set(), 0
processed = 0
while queue and new < 700:
    u = queue.pop(0)
    if u in seen:
        continue
    seen.add(u)
    if any(u.lower().endswith(x) for x in JUNK):
        continue
    rel = u.split("/srw-impact/", 1)[-1].strip("/")
    nm = "srpg-" + (re.sub(r"[^a-z0-9]+", "-", rel.lower()).strip("-") or "root")
    h, ok = save_page(nm, u)
    processed += 1
    if ok:
        new += 1
        time.sleep(SLEEP)
    if processed % 25 == 0:
        print("... progress: processed=%d new=%d queue=%d" % (processed, new, len(queue)))
    if h:
        for v in hrefs(u, h):
            if v.startswith("https://s-rpg-navi.com/srw-impact") and v not in seen:
                queue.append(v)
print("DONE: newly fetched=%d, processed=%d, queue-left=%d" % (new, processed, len(queue)))
