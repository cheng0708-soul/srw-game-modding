#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""seesaa 攻略ラボ via web.archive — 修正 cp932 编码后抓全 14 个菜单页"""
import re, os, time, subprocess, html as H

OUT = "/Volumes/D2T/projects/srw-game-modding/research/hidden-elements"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"

def curl_bytes(url, timeout=70):
    r = subprocess.run(["curl", "-sL", "-m", str(timeout), "-A", UA, url],
                       capture_output=True)
    return r.stdout

def decode(b):
    for enc in ("utf-8", "cp932", "euc-jp"):
        try:
            return b.decode(enc)
        except Exception:
            continue
    return b.decode("cp932", "replace")

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

# ---- 1) 修正首页解码 ----
hb = open(os.path.join(OUT, "seesaa-wayback-home.html"), "rb").read()
h = decode(hb)
t = strip_tags(h)
open(os.path.join(OUT, "seesaa-home.txt"), "w", encoding="utf-8").write(
    "# source: http://srw-impact.seesaa.net/ (via web.archive.org, cp932 decoded)\n# fetched: %s\n\n%s"
    % (time.strftime("%Y-%m-%d %H:%M"), t))
print("seesaa-home.txt 重写完成:", len(t), "chars")
print("----- 首页文本头 -----")
print(t[:900])
print("----- 完 -----")

# ---- 2) 抓 14 个菜单页 ----
articles = ["49150176", "49150248", "49150426", "49150492", "49150351", "49152939",
            "49155669", "49158767", "49158279", "49157590", "49158338", "49158416",
            "49158523", "49158817"]
manifest = os.path.join(OUT, "_manifest.txt")
okc = 0
for slug in articles:
    name = "seesaa-art" + slug
    txt_p = os.path.join(OUT, name + ".txt")
    if os.path.exists(txt_p):
        print("SKIP", name)
        continue
    url = "http://srw-impact.seesaa.net/article/%s.html" % slug
    page = curl_bytes("https://web.archive.org/web/2024/" + url)
    if not page or len(page) < 400:
        print("FAIL", name, len(page or b""))
        time.sleep(3)
        continue
    raw_p = os.path.join(OUT, "_raw", name + ".html")
    os.makedirs(os.path.dirname(raw_p), exist_ok=True)
    open(raw_p, "wb").write(page)
    t2 = strip_tags(decode(page))
    open(txt_p, "w", encoding="utf-8").write(
        "# source: %s (via web.archive.org)\n# fetched: %s\n\n%s"
        % (url, time.strftime("%Y-%m-%d %H:%M"), t2))
    with open(manifest, "a", encoding="utf-8") as f:
        f.write("%s\t%s\t%s\n" % (name, url, time.strftime("%Y-%m-%d %H:%M")))
    head = t2.splitlines()[2][:70] if len(t2.splitlines()) > 2 else "?"
    print("OK", name, len(t2), "|", head)
    okc += 1
    time.sleep(2.5)
print("DONE: fetched", okc, "/", len(articles))
