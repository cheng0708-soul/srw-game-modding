#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""seesaa 攻略ラボ via web.archive 补抓"""
import re, os, time, subprocess, html as H

OUT = "/Volumes/D2T/projects/srw-game-modding/research/hidden-elements"
home = os.path.join(OUT, "seesaa-wayback-home.html")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"

def curl(url, timeout=70):
    r = subprocess.run(["curl", "-sL", "-m", str(timeout), "-A", UA, url],
                       capture_output=True, text=True)
    return r.stdout

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

h = open(home, encoding="utf-8", errors="replace").read()
print("home html len:", len(h))
raw_t = strip_tags(h)
open(os.path.join(OUT, "seesaa-home.txt"), "w", encoding="utf-8").write(
    "# source: http://srw-impact.seesaa.net/ (via web.archive.org)\n# fetched: %s\n\n%s"
    % (time.strftime("%Y-%m-%d %H:%M"), raw_t))
print("saved seesaa-home.txt", len(raw_t))
print("----- home text head -----")
print(raw_t[:1500])
print("----- end head -----")

pairs, seen = [], set()
for m in re.finditer(r'(?is)<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', h):
    u, t = m.group(1), H.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
    if "srw-impact.seesaa.net" not in u:
        continue
    a = u.find("srw-impact.seesaa.net")
    u2 = "http://" + u[a:].split("#")[0].rstrip('"').rstrip("'")
    if u2 not in seen:
        seen.add(u2)
        pairs.append((u2, t))
print("unique seesaa links:", len(pairs))
for u, t in pairs:
    print("  ", t[:44], "->", u)

kw = ["隠し", "入手", "条件", "引継", "引き継", "小ネタ", "チャート", "システム", "特徴", "ストーリー", "強化", "合体"]
pick = [(u, t) for u, t in pairs if any(k in t for k in kw)]
print("picked:", len(pick))

manifest = os.path.join(OUT, "_manifest.txt")
okc = 0
for u, t in pick[:15]:
    slug = re.sub(r"[^0-9]", "", u.split("/")[-1])[:14] or "home"
    name = "seesaa-art" + slug
    txt_p = os.path.join(OUT, name + ".txt")
    if os.path.exists(txt_p):
        print("SKIP", name)
        continue
    page = curl("https://web.archive.org/web/2024/" + u)
    if not page or len(page) < 500:
        print("FAIL", name, u, len(page or ""))
        continue
    raw_p = os.path.join(OUT, "_raw", name + ".html")
    os.makedirs(os.path.dirname(raw_p), exist_ok=True)
    open(raw_p, "w", encoding="utf-8").write(page)
    t2 = strip_tags(page)
    open(txt_p, "w", encoding="utf-8").write(
        "# source: %s (via web.archive.org)\n# fetched: %s\n\n%s"
        % (u, time.strftime("%Y-%m-%d %H:%M"), t2))
    with open(manifest, "a", encoding="utf-8") as f:
        f.write("%s\t%s\t%s\n" % (name, u, time.strftime("%Y-%m-%d %H:%M")))
    print("OK", name, len(t2), "|", t[:40])
    okc += 1
    time.sleep(2.0)
print("DONE: seesaa fetched", okc)
