#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, shutil, hashlib, time

BASE = "/Users/wangluke/.hermes/cache/scratch/impact-cheats"
PNACH = "/Users/wangluke/Library/Application Support/PCSX2/cheats/SLPS-25104_10C3D363.pnach"
BK = "/Volumes/D2T/Backups/IMPACT-存档备份-2026-10-02"
README = os.path.join(BASE, "IMPACT-补机体说明-2026-10-02.md")

# ---------- 1. rename combo groups to Chinese ----------
t = open(PNACH, encoding="utf-8").read()
ren = {"[ダンクーガ 断空光牙剣版]": "[断空我·断空光牙剑版]",
       "[ダンガイオー 螺旋拳版]": "[弹劾凰·螺旋拳版]",
       "[ライディーン ゴッドボイス版]": "[莱丁·GodVoice版]"}
for k, v in ren.items():
    if k in t:
        t = t.replace(k, v)
    else:
        print("WARN rename not found:", k)

# header structure note
old_hdr = "// 用法: 游戏属性 -> Cheats -> 各分组可单独开关"
new_hdr = ("// 用法: 游戏属性 -> Cheats -> 各分组可单独开关\n"
           "// 结构: ①补漏19组(你已选的保持) ②便利码5组 ③必杀技3组 ④全机体目录160组 ⑤机师补充18组\n"
           "// (②③④⑤全部默认未勾选 —— 要用哪台在面板里打勾; 面板有搜索框)")
if old_hdr in t:
    t = t.replace(old_hdr, new_hdr, 1)
else:
    print("WARN header note not found")

open(PNACH, "w", encoding="utf-8").write(t)

# also update generator script names for reproducibility
bs_path = os.path.join(BASE, "build_full_catalog.py")
bs = open(bs_path, encoding="utf-8").read()
for k, v in {"ダンクーガ 断空光牙剣版": "断空我·断空光牙剑版",
             "ダンガイオー 螺旋拳版": "弹劾凰·螺旋拳版",
             "ライディーン ゴッドボイス版": "莱丁·GodVoice版"}.items():
    bs = bs.replace(k, v)
open(bs_path, "w", encoding="utf-8").write(bs)

# ---------- 2. parse groups from pnach ----------
lines = t.splitlines()
def parse_group(i0):
    name = lines[i0][1:-1]
    desc = ""
    addr = ""
    j = i0 + 1
    while j < len(lines) and not lines[j].startswith("["):
        lj = lines[j]
        if lj.startswith("description="):
            desc = lj.split("=", 1)[1]
        if lj.startswith("patch="):
            parts = lj.split(",")
            if len(parts) >= 5:
                addr = parts[4]
        j += 1
    return name, desc, addr

catalog_rows = []
in_cat = False
for i, l in enumerate(lines):
    if l.startswith("// ★★ 全机体目录"):
        in_cat = True
        continue
    if l.startswith("// ★ 机师补充"):
        in_cat = False
    if in_cat and l.startswith("["):
        name, desc, addr = parse_group(i)
        jp = desc.split("｜")[0] if "｜" in desc else desc
        catalog_rows.append((name, jp, addr))

print("catalog rows:", len(catalog_rows))

tbl = "| # | 名称 | 日文名 | 写入 |\n|---|------|--------|------|\n"
for k, (name, jp, addr) in enumerate(catalog_rows, 1):
    tbl += "| %d | %s | %s | %s |\n" % (k, name, jp, addr)

# ---------- 3. README update ----------
rd = open(README, encoding="utf-8").read()
reps = [
    ("应能看到 19 个分组（[G-3高达]、[夏亚专用扎古] …）。",
     "应能看到 205 个分组（补漏 19 + 便利码 5 + 必杀技 3 + 全机体目录 160 + 机师补充 18；后四类全部默认未勾选，用哪台勾哪台）。"),
    ("以下 5 组已放在 pnach 文件末尾，**行首带 \"//\" = 不生效**；要用哪个：去掉对应行首的 `// ` 即可（或直接叫我开启）。全部来自日站长期流通码并逐条解密核验：",
     "以下 5 组现在是正式分组（在面板里直接勾选；默认未勾选）。全部来自日站长期流通码并逐条解密核验："),
]
for a, b in reps:
    if a in rd:
        rd = rd.replace(a, b)
    else:
        print("WARN readme text not found:", a[:30])

rd += """

## 九、全机体目录（新增 160 组，默认全部未勾选）

**机制**：勾选状态保存在 PCSX2 设置里（游戏属性 → Cheats）。未勾选的组 = 完全不生效，随时可勾/可取消。
面板顶部有搜索框，输入名字可快速过滤（如输入"高达"）。

**使用建议（重要）**：
1. 已经拥有的机体不必勾（没有任何意义）。
2. **剧情之后会正常入手的机体，不建议提前勾**——社区报告过"提前加 + 剧情再给 = 变两台"的混乱。
3. 在非第 1 部的进度里启用时，若机体不出现：把该组的 `00000001` 换成
   `00000003`（第1部）/ `0000001F`（第2部）/ `00000004`（第3部）——即日站的"按部换值"规则。
4. 老规矩：先验证再在游戏内存档；异常就把对应组取消勾选（或删文件）即可复原。

**第 2 部相关推荐**（当年攻略里第 2 部的隐藏要素）：力奇·戴亚斯(黑)、核心推进器、
诺耶·吉尔、瓦尔·瓦罗、艾斯特巴利斯改、ZⅡ(MS/MA)、百式改、全装甲百式改、杰刚、
古铁＆古铁·里昂、白骑士＆白骑士·里昂；机师：夏扎拉、基娜、科隆、普露二号、卡多。

**第 3 部相关推荐**：零影、维尔宾(夜战型)、飞翼卡里巴(夜战型)、真盖塔 1/2/3、
ν高达 / ν高达HWS；必杀技组：断空光牙剑、GodVoice；机师：东方不败、施瓦茨。

### 全机体目录全表（160 组）

""" + tbl + """

## 十、必杀技追加 / 机师补充说明

- **必杀技 3 组**：把「已有该机体的」单位换成"追加必杀技版本"（断空我→断空光牙剑版、
  弹劾凰→螺旋拳版、莱丁→GodVoice版）。没有对应机体时勾了也没效果。
- **机师 18 组**：第 2/3 部相关与隐藏机师（普露二号、卡多、基娜、科隆、夏扎拉、洛姆、
  蕾娜、迪奥多拉、格罗拜因、加鲁迪、罗尔·克兰、米娅·爱丽丝、兰巴·诺姆、帕伊·桑达、
  东方不败、施瓦茨、艾尔·比安诺、马修玛）。勾上后连机体一起用（东方不败 ↔ 尊者高达）。
- **便利码 5 组**：资金MAX、强化零件全、全机 15 段改造+插件4格、EN&弹药不减、战后等级MAX。
- 仍未收录：SP不减、换装限制解除（多行特殊格式，未完全解密干净，需要再说）。

## 十一、文件位置速查

- 补丁（唯一真身）：`~/Library/Application Support/PCSX2/cheats/SLPS-25104_10C3D363.pnach`
- 打开方式：Finder → 前往 → 前往文件夹（⇧⌘G）→ 粘贴 `~/Library/Application Support/PCSX2/cheats`
- 备份副本（含本说明）：`/Volumes/D2T/Backups/IMPACT-存档备份-2026-10-02/`
"""

open(README, "w", encoding="utf-8").write(rd)
print("README updated:", len(rd), "chars")

# ---------- 4. copy both to backup dir + checksum ----------
shutil.copy2(PNACH, os.path.join(BK, "SLPS-25104_10C3D363.pnach"))
shutil.copy2(README, os.path.join(BK, "IMPACT-补机体说明-2026-10-02.md"))
lines2 = []
for f in ["SLPS-25104_10C3D363.pnach", "IMPACT-补机体说明-2026-10-02.md"]:
    b = open(os.path.join(BK, f), "rb").read()
    lines2.append("%s  %s" % (hashlib.sha256(b).hexdigest(), f))
with open(os.path.join(BK, "SHA256SUMS.txt"), "a", encoding="utf-8") as fh:
    fh.write("\n# update2 %s\n" % time.strftime("%Y-%m-%d %H:%M") + "\n".join(lines2) + "\n")

print("backup synced")
tt = open(PNACH, encoding="utf-8").read()
print("FINAL:", len(tt.encode()), "bytes |", len([l for l in tt.splitlines() if l.startswith("[")]), "groups |",
      len([l for l in tt.splitlines() if l.startswith("patch=")]), "patches")
print("sha256:", hashlib.sha256(tt.encode()).hexdigest())
