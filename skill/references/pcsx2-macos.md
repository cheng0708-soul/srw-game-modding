# macOS PCSX2 机制速查（本机库）

## 路径
- 应用: `/Volumes/D2T/Downloads/PCSX2-v2.8.2.app`
- 配置根: `~/Library/Application Support/PCSX2/`
  - `cheats/` — 金手指（`<SERIAL>_<CRC>.pnach`）
  - `sstates/` — 即时档（`<SERIAL> (<CRC>).NN.p2s`）
  - `inis/PCSX2.ini` — 全局设置（EnableCheats 等；`[MemoryCards]` 指向实际记忆卡目录）
  - `gamesettings/<SERIAL>_<CRC>.ini` — 每游戏设置；`[Cheats] Enable = <组名>` **= 启用白名单（未列出 = 未勾选）**
  - `logs/emulog.txt` — 查 CRC/版本/游玩时长
- 记忆卡实际位置由 PCSX2.ini 决定（本机曾 = `~/Documents/RetroArch/saves/LRPS2/`）
- 游戏 ISO: `/Volumes/D2T/RetroArch/roms/ps2/…`

## pnach 规则
- 行格式: `patch=1,EE,<8位地址>,extended,<8位值>`；`//` 注释；`[组名]` 分组；`gametitle=` 首行可选。
- `extended` = 地址最高 nibble 为类型码（0=8bit, 1=16bit, 2=32bit …）。
- 分组勾选状态存 gamesettings（见上）→ **不在白名单的组 = 默认未勾选**，批量新增不怕默认全开。
- 已有分组切勿改名/改序（用户勾选状态会失联）。

## 即时档 (.p2s) 读取
- = ZIP 容器；条目含 `eeMemory.bin`（= 32MB EE 主内存，作弊地址 = 直接偏移）、`GS.bin`、`Screenshot.png` 等；条目用 **zstd（zip 方法 93）** 压缩 —— macOS 自带 Python 3.9 的 zipfile 不支持。
- 解法: 手动解析 zip（跳过 local header 取 compress_size 原始字节）→ `/opt/homebrew/bin/zstd -d` → 原始 bin。
- `scripts/savestate_read.py <file.p2s> <addr>...` 已封装。
- 验证样例: 已拥有单位的存在标志 ≠ 0；未拥有 = 0（曾据此核对用户存档：丹拜因(托德)=01、G-3=00 等）。

## 其他要点
- 金手指总开关: `PCSX2.ini` 的 `EnableCheats = true` **+** 属性面板最上方「启用作弊」勾选框（都要开）。
- 改 pnach 后需重新载入游戏/属性页才会刷新。
- 备份方案: rsync 即时档 + 记忆卡 + 配置快照 + SHA256SUMS（样例见 BK 备份目录）。
- 长任务脚本不要 `| head`（SIGPIPE 会掐死脚本使其半途而废）；全量输出重定向到文件再查看。
- 改写前确认 PCSX2 未运行: `ps aux | grep -i pcsx2`。
