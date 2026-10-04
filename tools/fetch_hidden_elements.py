#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SRW IMPACT 后期隐藏要素资料 - 批量抓取（2026-10-04）
目标站点: s-rpg-navi.com / srw-impact.seesaa.net / toybox.gn.to / tuzigiri / ds-cheat
输出: /Volumes/D2T/projects/srw-game-modding/research/hidden-elements/*.txt
"""
import re, os, time, urllib.request, urllib.parse, html as H

OUT = "/Volumes/D2T/projects/srw-game-modding/research/hidden-elements"
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
SLEEP = 0.6
saved, failed = [], []

def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
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

def fetch_save(name, url):
    path = os.path.join(OUT, name + ".txt")
    if os.path.exists(path):
        print("SKIP (exists) %s" % name)
        return None
    try:
        h = get(url)
        t = strip_tags(h)
        with open(path, "w", encoding="utf-8") as f:
            f.write("# source: %s\n# fetched: %s\n\n%s" % (url, time.strftime("%Y-%m-%d %H:%M"), t))
        saved.append((name, url, len(t)))
        print("OK  %-30s %7d chars  %s" % (name, len(t), url))
        return h
    except Exception as e:
        failed.append((name, url, str(e)))
        print("FAIL %-30s %s  (%s)" % (name, e, url))
        return None

def links_with_text(base_url, h):
    out, seen = [], set()
    for m in re.finditer(r'(?is)<a\s[^>]*href="([^"#]+)"[^>]*>(.*?)</a>', h):
        u = urllib.parse.urljoin(base_url, m.group(1))
        if urllib.parse.urlparse(u).netloc != urllib.parse.urlparse(base_url).netloc:
            continue
        if u in seen:
            continue
        seen.add(u)
        txt = H.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        out.append((u, txt))
    return out

print("=========== A) 种子页 ===========")
h_srpg = fetch_save("srpg-main", "https://s-rpg-navi.com/srw-impact")
time.sleep(SLEEP)
h_seesaa = fetch_save("seesaa-home", "http://srw-impact.seesaa.net/")
time.sleep(SLEEP)
h_toybox = fetch_save("toybox-home", "http://toybox.gn.to/SRWIMPACT/index.htm")
if h_toybox is None:
    h_toybox = fetch_save("toybox-home2", "http://toybox.gn.to/SRWIMPACT/")
time.sleep(SLEEP)

print()
print("=========== B) s-rpg-navi 全子页（数据页/各Scene/チャート/Tips）===========")
if h_srpg:
    subs = [(u, t) for u, t in links_with_text("https://s-rpg-navi.com/srw-impact", h_srpg)
            if "/srw-impact/" in u and not u.rstrip("/").endswith("/srw-impact")]
    seen = set()
    for u, t in subs:
        if u in seen:
            continue
        seen.add(u)
        rel = u.split("/srw-impact/", 1)[-1].strip("/") or "root"
        nm = "srpg-" + (re.sub(r"[^a-z0-9]+", "-", rel.lower()).strip("-") or "root")
        fetch_save(nm, u)
        time.sleep(SLEEP)
    print("sub find count:", len(seen))
    for u, t in subs:
        print("   ", t[:40], "->", u)

print()
print("=========== C) seesaa 关键文章（按锚文本关键词）===========")
if h_seesaa:
    all_links = links_with_text("http://srw-impact.seesaa.net/", h_seesaa)
    kw = ["隠し", "入手", "条件", "引継", "引き継", "小ネタ", "チャート", "システム", "ストーリー", "特徴", "更新", "裏技"]
    pick, seen = [], set()
    for u, t in all_links:
        if u in seen:
            continue
        seen.add(u)
        if any(k in t for k in kw):
            pick.append((u, t))
    for u, t in pick[:15]:
        nm = "seesaa-" + re.sub(r"[^a-z0-9]", "", u.split("/")[-1])[:20]
        if re.search(r"\d", nm):
            nm = "seesaa-art" + re.sub(r"[^0-9]", "", u.split("/")[-1])[:12]
        fetch_save(nm, u)
        time.sleep(SLEEP)
    print("all same-domain links:", len(all_links), "| picked:", len(pick))
    for u, t in pick[:20]:
        print("   ", t[:48], "->", u)

print()
print("=========== D) toybox 子页 ===========")
if h_toybox:
    subs, seen = [], set()
    for u, t in links_with_text("http://toybox.gn.to/SRWIMPACT/index.htm", h_toybox):
        if u in seen:
            continue
        seen.add(u)
        subs.append((u, t))
    for u, t in subs[:20]:
        nm = "toybox-" + re.sub(r"[^a-z0-9]", "-", u.split("/")[-1].lower()).strip("-")[:30]
        fetch_save(nm, u)
        time.sleep(SLEEP)
    print("subs:", len(subs))
    for u, t in subs[:25]:
        print("   ", t[:48], "->", u)

print()
print("=========== E) 单页补充 ===========")
for nm, u in [("tuzigiri-condition", "http://srwimpact.tuzigiri.com/condition.html"),
              ("ds-cheat-impact", "https://ds-cheat.boy.jp/ps2/super_robot_wars_impact.html"),
              ("seesaa-49150426", "http://srw-impact.seesaa.net/article/49150426.html")]:
    fetch_save(nm, u)
    time.sleep(SLEEP)

print()
print("=========== 总结 ===========")
print("saved:", len(saved), "| failed:", len(failed))
for n, u, l in saved:
    print("  saved:", n, l)
for n, u, e in failed:
    print("  FAILED:", n, e)
