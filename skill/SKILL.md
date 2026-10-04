---
name: srw-game-modding
description: Use when modding 机战/SRW on PCSX2 (cheats, hidden units).
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [srw, 机战, pcsx2, cheats, pnach, ar2, emulation, game-modding]
metadata:
  hermes:
    tags: [srw, 机战, pcsx2, cheats, pnach, ar2, emulation]
    related_skills: [macos-emulation, switch-game-patches]
---

# 超级机器人大战(SRW/机战) 游戏修改 — 总流程

在 PCSX2(macOS) 上给机战系列做「隐藏要素补完 / 金手指 / 存档验证」的标准作业。
**已完成作品: IMPACT**（专档 `references/impact.md`）。做新作时按本流程走一遍，然后新建 `references/<作品名>.md`。

## When to Use
- 用户要给某作机战（SRW）补隐藏机体/机师、加金手指、或问「日站码怎么转 PCSX2」时。
- 需要在 PCSX2(macOS) 上写/改/调试 pnach 文件，或读即时档核对某地址数值时。
- 要扩展支持新的机战作品时（按文末「做新作时」指南执行）。

## 铁律（先读）
1. **只读研究 → 备份 → 才动手**。写入前备份: 即时档 + 记忆卡 + 配置（路径见 SOP §2）。
2. **一切数据必须有多来源验证链**: 日站原码 → 离线解密 → 与中文圈原码/博客实测交叉验证（至少 2 个独立证据）后才采用。
3. **测试协议**: 读档 → 看变化 → OK 才在游戏内存档；异常 = 取消勾选/删 pnach 完全复原（金手指是内存写入，只有游戏内存档后才固化）。
4. **绝不照抄网上码包**: 日站/网上清单常有「错位抄本」或版本差异，必须用已实机验证的锚点逐条校准。
5. 输出数字/结论必带时间戳；拿不到时间戳的数据降级为参考或不用。

## SOP
### 1) 定游戏身份
- 得到 SERIAL_CRC（PCSX2: `logs/emulog.txt` 或 cheats 目录已有文件名，如 `SLPS-25104_10C3D363`）。
- pnach 文件名必须 = `<SERIAL>_<CRC>.pnach`，放进 cheats 目录才会被加载。

### 2) 全量备份
```
sstates:  ~/Library/Application Support/PCSX2/sstates/
记忆卡:   见 PCSX2.ini [MemoryCards] 实际路径（本机曾 = ~/Documents/RetroArch/saves/LRPS2/）
配置:     inis/PCSX2.ini + gamesettings/*.ini
```
rsync 到 `/Volumes/D2T/Backups/` 下按日期建目录，附 SHA256SUMS。

### 3) 找码源（优先级顺序）
1. **5ch 改造スレ archives**（`kako.5ch.net/test/read.cgi/gameover/<id>`）— 精华 = 「ユニット存在フラグ表」「パイロット存在フラグ表」（一表打尽全单位/机师的存在标志码）。多スレ对照可发现错位。
2. **teruyuka.web.fc2.com/kaizo-code/** — 各作独立页，资金/改造/等级等成年码 + 主码。
3. **華魯サンジュのブログ**(ameblo) — 实测记录（"ok"/"だめ"标记）；4 行「变更块」= 基线码 + 字段改写（把某机体"变成"另一台或追加必杀技）。
4. **中文圈**: a9vg 老帖 / wlgooo 等 PCSX2 原码 / newswise — 用作交叉验证（他们的是已在 PCSX2 实跑的格式）。

### 4) 解密 AR2v2 → PCSX2 原始码
```python
import sys; sys.path.insert(0, "<本skill>/scripts")
from converter import AR2
a = AR2(0x05100518)                      # 默认密钥 AR1_SEED
d1, d2 = a.dec_pair(0x3C6CC12C, 0x1456E7A6)
# d1 = 0x00FD3E04(完整地址含类型nibble), d2 = 0x00000001(值)
# → patch=1,EE,00FD3E04,extended,00000001
```
- 校验: master `EC878304 1434A4A4` 应解出 `F01000DC 0022C307`（SRW IMPACT 系通用）。
- 多行码注意与值族细节: `references/ar2-decrypt.md`。

### 5) 校准（防错位/防版本差）
- 用「博客标注了名字的原码」当锚点；解密地址的邻接规律也是证据（错位往往整段差一格，2-3 个锚点即可定）。
- 需要时**直接读存档验证**: `scripts/savestate_read.py <file.p2s> <地址>`；已拥有单位的存在标志 ≠ 0。

### 6) 写 pnach
- 格式: UTF-8；`gametitle=` 行；`//` 注释；`[分组名]` + `description=` + `patch=1,EE,<8位地址>,extended,<8位值>`。
- **关键机制: 勾选状态存 `gamesettings/<SERIAL>_<CRC>.ini` 的 `[Cheats] Enable = <组名>`（白名单；不在名单 = 未勾选）**。
  → 批量新增内容天然默认 OFF（要用再勾）；**绝不能改名/重排已有分组**（会失联用户的勾选状态）。
- 新内容按「节」组织；名称用中文 + 日文原名注释（用户玩汉化版，要能对上）。

### 7) 交付与自检
- 自检: 分组数/行数统计、`patch=` 正则全检、重名检查、关键地址断言（对照锚点）。
- 给用户的说明写清: 文件路径、开关方法、换值规则、风险与回滚、「先验证再存档」。

## 值规则（存在标志类码）
- 通用值 `00000001`（原码值 1456E7A6）。
- 按部换值（日站规则，部分机体）: 第1部 `03` / 第2部 `1F` / 第3部 `04`（原码 1456E7A8 / AC / A1）。
- 单行不出 → 先换值，再怀疑地址。

## 已知坑（血泪教训）
- 网上清单错位普遍；宁可少用不可照抄。
- 「剧情会正常入手」的机体提前加 → 可能「两台」混乱；默认别给用户勾，说明风险。
- 已拥有单位标志值可能 ≠ 1（如 02/14/1E）；覆盖有未知风险 → 读存档确认后再决定。
- 金手指加入的机体: 不触发剧情台词；出击前显示残留 = 已知现象。
- 机体表 +4 / 机师表 +8 = 存在标志字节；+2/+9/+A 等 = 变换字段（4 行变更块的原理）。
- macOS Python 3.9 zipfile 读不了 zstd(方法93) 的 zip → 手动切 raw + `/opt/homebrew/bin/zstd -d`。
- 长脚本别 `| head`（SIGPIPE 会掐死脚本、后续段落不执行）；全量输出落文件再翻。

## 做新作时（扩展指南）
1. 按 SOP 1-4 收集 + 解密新作码。
2. 找该作「存在フラグ表」或等效来源，定出该作标志字节地址规律（不同作内存布局不同 — 用 2-3 个已知单位锚点验证；**公式不可跨作套用**）。
3. 新建 `references/<作品名>.md`: 序列号/CRC、来源URL、验证链、关键地址表、特有坑。
4. 本文件开头「已完成作品」列表加一行。

## 文件
- `references/impact.md` — IMPACT 专档（成果 + 地址表 + 错位史料）
- `references/ar2-decrypt.md` — AR2v2 格式/密钥/值族/多行码
- `references/pcsx2-macos.md` — macOS PCSX2 路径与机制速查（含存档读取）
- `scripts/converter.py` — AR2v2→PCSX2 解密器（自包含）
- `scripts/savestate_read.py` — 读即时档地址（验证用）
