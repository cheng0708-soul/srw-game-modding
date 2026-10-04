# 机战IMPACT 金手指调研记录（本机方案）— 2026-10-02

## 本机事实（已核实）
- PCSX2 v2.8.2（x86_64/Rosetta），App: /Volumes/D2T/Downloads/PCSX2-v2.8.2.app
- 配置目录: ~/Library/Application Support/PCSX2/
  - cheats/ 下已有 2 个先例 pnach（SLPM-65788 / SLPM-65888=DQ8），extended(RAW) 写法
  - PCSX2.ini: EnableCheats=true（已开）、BackupSavestate=true、MemoryCards 指向 ~/Documents/RetroArch/saves/LRPS2
- 游戏: /Volumes/D2T/RetroArch/roms/ps2/超级机器人对战IMPACT完全汉化版(WGF).iso
  - SLPS-25104 / 版本 1.05 / CRC **10C3D363**（2026-10-02 18:42 emulog 实测）
  - 今晚 18:42–18:56 游玩；sstates: SLPS-25104 (10C3D363).01–.05 (+backup)；记忆卡 Mcd001.ps2（18:56 存档）
- 累计游玩 ≈ 44.4 小时（emulog playtime 159989s）

## 目标与条件（攻略源核实）
- G-3ガンダム: 第1部 Scene5/第26話「裏切りのコレクター」、ベンメル生存＆10EP增援、クリス击坠 → 「戦場は大空高く」(27話)前入手
- シャア専用ザク: 同话、バーニィ击坠 → 同前入手
- 两者第1部限定，无后续补救条件；同周目可并得（非二択）
- 若已过判定点：只能靠"变更/追加码"

## 民间码源（已定位，2026-10-02 拉取）
- 5ch 改造スレ1: kako.5ch.net/test/read.cgi/gameover/1016767066
- 5ch 改造スレ2: kako.5ch.net/test/read.cgi/gameover/1018264775  ← 含"名字/代码"对照表（好版在 1835–1894 行区域）
- 5ch 改造スレ3: kako.5ch.net/test/read.cgi/gameover/1021288750  ← 1246–1251 行再现 BG-3/シャアザク 条目
- 華魯サンジュ博客（实测记录）:
  - entry-10263326716「やあってやるぜ！IMPACTコード」
  - entry-10247131076「コード使って逆襲のシャア小隊！」
  - entry-10272845289「思い起こすは一年戦争・・・・！」 ← 目标两条在此
  - entry-10255463493 / entry-10295514216（更多机体块）
- チートのお部屋出張所: cheatroom.blog.fc2.com/blog-entry-121.html（同游戏相关）
- 中文"汉化版可用"码表（直接可用的 pnach 格式，仅金钱/零件/EXP等，无机体变更）:
  围炉Go wlgooo.com/20391.html / 逗游 doyo.cn/article/519179 / oonews
- 转换工具链: OmniConvert（Windows，本机有 /Users/wangluke/Applications/CrossOver.app 可跑）

## 候选码（待内存核对+副本实测）
- シャア専用ザク 存在/追加: `3C6CC02C 1456E7A6`（a3博客 + スレ2干净版；两次独立互证）
- G-3ガンダム("BG-3"表记): `3C6CC12C 1456E7A6`（同上）
- 注意: 网传"错位抄本"把两者地址对调（スレ2前半、韩站）；已用8个互证点排除（黑狮子B72C/兽魔B62C/零影B92C/飞影B82C/爆龙BB2C/核心推进器BE2C/高达BF2C/等）
- 校验用已知互证点（后续内存核对时用）: ダンクーガ=2F2C、マスターガンダム=012C、νHWS=F52C、サザビー=F32C、Hi-ν=F82C、ビギナ・ギナ=FA2C、ザクⅢ改=EE2C
- 格式: PAR2/AR2 系加密（master EC878304 1434A4A4）→ 需轉換为 PCSX2 extended RAW 后使用

## 民间使用注意（从原帖整理）
- 単行"存在フラグ"码可能不够：有 Hi-ν 单行失败案例（5ch3 #491）；必要时用完整4行块（..2C/..31/..26(4C)/..2E）
- 跨部值差异: 例如 νHWS 存在フラグ = 一部 E7A6 / 二部 E7A0 / 三部 E7A6
- 已知 bug 案例: 同机体2台→バグ；整备画面看パイロット→冻结（特定码）；"出撃させるまでギャプラン表示"等显示残留；"セーブに反映されない"ケースあり
- 存在フラグ硬出 → 不会看到仲间加入事件对话；建议改完内存档→关码→重启验证
- 5ch3 亦有"復号化→修改→再暗号化"的操作史（社区自带转换流程）

## 执行草案（待用户确认后动手）
- P0 备份: LRPS2 记忆卡目录 + SLPS-25104 sstates → /Volumes/D2T（带日期）
- P1 兼容性测试（无害）: 开"资金MAX"码（2025E838 05F5E0FF 等）→ 看数字变化 → 关码
- P2 内存核对: PCSX2 调试器 Memory View 查 0x25E838(资金)与 3C6CC02C/12C 对应 RAW 地址真身（仅读）
- P3 变更码实测（副本）: 复制记忆卡 → 两台杂兵放格纳库前位 → 开码 → 观察 → 游戏内存档 → 关码 → 重启验证（查武器/换乘/出击/整备各画面）
- P4 定案: 整理为 SLPS-25104_10C3D363.pnach（分组注释）+ 记录
- 失败分支: 换码源/补齐4行块 → 存档修改器(srwi_tool 1.4a, 需CrossOver) → 自行定位(调试器)

## 待确认
- 用户当前进度（第几部/话）；クリス/バーニィ在否；牺牲品机体；是否只补这两台
