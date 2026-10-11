import json
import re

# 读取已整理好的 隐藏要素总整理-中文-2026-10-04.md
source_md = "/Volumes/D2T/projects/srw-game-modding/research/隐藏要素总整理-中文-2026-10-04.md"

with open(source_md, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 提取所有隐藏要素（33项）
# 原有的 32 条 + 托度在拜斯顿威尔的专属说明
secrets_list = []

# 解析现有的 web/data/secrets.js 作为基础
with open("/Volumes/D2T/projects/srw-game-modding/web/data/secrets.js", "r", encoding="utf-8") as f:
    raw_js = f.read().replace("window.SRW_SECRETS = ", "").rstrip(";\n ")
    try:
        base_secrets = json.loads(raw_js)
    except:
        base_secrets = []

# 为每条要素补充详细标签、机体图片映射和难度
image_map = {
    "断空我": "srw_tactical_insignia.jpg",
    "魔神": "srw_tactical_insignia.jpg",
    "葛莱丽亚": "alteisen.png",
    "罗莎美亚": "fa_hyakushiki_kai.png",
    "托度": "weissritter.png",
    "雪山": "kampfer.png",
    "所罗门": "fa_hyakushiki_kai.png",
    "普露": "rein_weissritter.png",
    "量产型大魔神": "srw_tactical_insignia.jpg",
    "德克萨斯麦克": "god_gundam.png",
    "G-3": "fa_hyakushiki_kai.png",
    "飞影": "srw_tactical_insignia.jpg",
    "精神感应高达": "master_gundam.png",
    "休巴兹": "master_gundam.png",
    "尊者高达": "master_gundam.png",
    "夏莎拉": "rein_weissritter.png",
    "卡特": "fa_hyakushiki_kai.png",
    "金吉马克": "alteisen.png",
    "普露兹": "rein_weissritter.png",
    "X艾斯蒂巴利斯改": "alteisen_riese.png",
    "零影": "master_gundam.png",
    "翼霸": "weissritter.png",
    "真·盖塔": "alteisen_riese.png",
    "天神音波": "god_gundam.png",
    "v高达": "fa_hyakushiki_kai.png",
    "古罗拜因": "kampfer.png",
    "基丽嘉": "rein_weissritter.png",
    "石破LOVELOVE天惊拳": "god_gundam.png",
    "加鲁迪": "kampfer.png",
    "白鸟九十九": "alteisen_riese.png",
    "逆袭的夏亚": "fa_hyakushiki_kai.png"
}

# 格式化基础 secrets
for idx, s in enumerate(base_secrets):
    title = s.get("title", s.get("要素", ""))
    img = "srw_tactical_insignia.jpg"
    for k, v in image_map.items():
        if k in title:
            img = v
            break
    s["image"] = img
    s["id"] = f"sec_{idx+1}"

# 2. 分支路线决策矩阵
branches = [
    {
        "id": "route_p1_s3",
        "title": "第1部 第3场景：三关排序决策矩阵",
        "subtitle": "A＝「纽约」 ｜ B＝「东南亚吉翁秘密基地」 ｜ C＝「中央亚洲沙漠地区」",
        "desc": "进入第3场景时需从三个关卡中自主选择攻克顺序。选择顺序将不可逆地决定进入地上路线(4B)还是拜斯顿威尔路线(4A)，并直接互斥影响核阻止、京宝梵及雪山事件。",
        "headers": ["选择顺序", "地上路线(4B)", "拜斯顿威尔(4A)", "所罗门核阻止", "京宝梵入手", "综合评价与战略收益"],
        "rows": [
            ["A → B → C", "○", "×", "○", "放弃雪山则可行", "★ 推荐方案一：走地上路线，可拿全装百式改/百式改与核阻止成功，收益整体最大。"],
            ["A → C → B", "○", "×", "×", "可与雪山同时", "折中方案：可兼顾雪山事件与京宝梵，但无法达成核阻止。"],
            ["B → A → C", "○", "×", "○", "放弃雪山则可行", "可行方案：东南亚放首位触发核阻止与卡特登场，走地上路线。"],
            ["B → C → A", "×", "○", "○", "放弃雪山则可行", "拜斯顿威尔方案：A放第3位进入4A路线，提前获得翼霸＋妖精。"],
            ["C → A → B", "○", "×", "×", "×", "不推荐：无法获得京宝梵与核阻止，收益较弱。"],
            ["C → B → A", "×", "○", "○", "×", "★ 推荐方案二：走拜斯顿威尔路线首选顺序，可达成核阻止与翼霸早期加入。"]
        ],
        "notes": [
            "核心规则：A选第1、2位＝地上路线(4B)；A选第3位＝拜斯顿威尔路线(4A，翼霸早期＋迷彩型翼霸)。",
            "鱼与熊掌不可兼得：全要素至少需放弃两项，请根据想要主力机体（全装百式改 vs 迷彩翼霸）决策。"
        ]
    },
    {
        "id": "route_p3_s3",
        "title": "第3部 第3场景：地球(A) / 火星(B) / 月球(C) 排序决策",
        "subtitle": "难度梯次动态上升 ｜ 古罗拜因唯一解 ｜ 规避母舰零件丢失重大BUG",
        "desc": "第3部进入第3场景后需依次攻克三大战区。随着攻克进度，后选战区难度判定（HARD/NORMAL）所需熟练度依次递增（第1个选需38+，第2个需40+，第3个需42+）。",
        "headers": ["推荐排序", "古罗拜因获得", "v高达 / v高达HWS", "避开BUG保障", "战略结论"],
        "rows": [
            ["C(月球) → A(地球) → B(火星)", "✅ 必须C先于A", "可根据熟练度灵活控", "✅ 完全避开BUG", "★★★★★ 最佳唯一解！既能满足古罗拜因前置，又彻底避免了地球篇放末尾母舰离脱吃零件的恶性BUG。"],
            ["A(地球) → B(火星) → C(月球)", "❌ 永久无法说得", "易进HARD", "❌ 存在隐患", "不推荐：先打A则德克萨斯殖民地无法说得古罗拜因。"],
            ["B(火星) → C(月球) → A(地球)", "✅ 满足C先于A", "易进HARD", "❌ 触发恶性BUG", "极度危险：地球篇放在最后，母舰永久离脱时会导致身上携带的强化零件永久消失！必须避开！"]
        ],
        "notes": [
            "【重大BUG警报】：原版游戏程序在地球篇最后结算时，母舰暂时离脱时未解绑身上的强化芯片，导致珍贵零件永久蒸发！必须把地球篇排在中间或最前！",
            "【古罗拜因硬性铁律】：必须先选月球篇(C)后选地球篇(A)，否则在德克萨斯殖民地杰特无法说得古罗拜因。"
        ]
    },
    {
        "id": "route_cca_hidden",
        "title": "隐藏终章「逆袭的夏亚篇」准入与熟练度统筹法则",
        "subtitle": "第99话通关时 熟练度 ≥ 50 ｜ 全程最高可拿 97 点",
        "desc": "通关第99话『然后前往决战的银河』时，如果累积熟练度达到50或以上，将在全剧终后解锁隐藏Scene 6『逆袭的夏亚』，包含第100话与第101话，阿姆罗驾驶ν高达与夏亚沙萨比最终决战！",
        "headers": ["结局CG版本", "前置条件", "参战机体与特征", "结局CG动画收录"],
        "rows": [
            ["结局版本 A", "获得 真·盖塔 ＋ 熟练度≥50 通关隐藏章", "真·盖塔1/2/3 极限输出", "收录 结局A CG 动画"],
            ["结局版本 B", "获得 真·白骑士 ＋ 熟练度≥50 通关隐藏章", "真·白骑士 超远狙击与HP回复", "收录 结局B CG 动画"],
            ["结局版本 C", "两者皆无（保留原机） ＋ 熟练度≥50 通关", "盖塔龙 ＋ 原版白骑士", "收录 结局C CG 动画"]
        ],
        "notes": [
            "控熟练度秘诀：如果想拿『v高达HWS』，进月球篇前难度需压制在 NORMAL（熟练度 < 当时关数÷2）；拿完后可全力拿熟练度冲破50以进隐藏章！",
            "通关隐藏章后，SOUND SELECT 将正式解锁逆袭夏亚传奇神曲『BEYOND THE TIME』！"
        ]
    }
]

# 3. 隐藏集装箱与掉落宝箱全览
containers = [
    {
        "stage": "第1部 最终话「掌控动荡大地者」",
        "location": "西北角宝箱",
        "content": "熟练度 ≥ 16 获得【高达】；熟练度 ≤ 15 获得【资金 20,000】",
        "type": "条件宝箱"
    },
    {
        "stage": "第1部 最终话「掌控动荡大地者」",
        "location": "中央建筑（击破墙壁）",
        "content": "获得【吉姆加农II】",
        "type": "破墙隐藏"
    },
    {
        "stage": "第2部「愤怒的魔神」",
        "location": "中央建筑（击破墙壁）",
        "content": "获得【里克·迪亚士（黑）】（另东南角宝箱为资金 20,000）",
        "type": "破墙隐藏"
    },
    {
        "stage": "第2部「捷达之门」",
        "location": "中央核心区（击破墙壁）",
        "content": "获得【核心战机】（东北角宝箱为资金 10,000）",
        "type": "破墙隐藏"
    },
    {
        "stage": "第2部「鲁那兹内部」",
        "location": "中央＋邻室（击破墙壁）",
        "content": "获得强化零件【奥拉转换器】 ＋ 隐藏机体【杰钢】",
        "type": "破墙隐藏"
    },
    {
        "stage": "第2部「所罗门内部」",
        "location": "西南密室（击破墙壁）",
        "content": "需核阻止成功：熟练度 ≥ 30 获得【百式改】；熟练度 ≤ 29 获得【全装百式改】（东南角为资金 10,000）",
        "type": "破墙隐藏"
    },
    {
        "stage": "第3部「燃烧的宇宙」",
        "location": "东侧 / 西侧密室（击破墙壁）",
        "content": "获得神级强化零件【太阳帆】 ＋ 【资金 50,000】",
        "type": "破墙隐藏"
    },
    {
        "stage": "第3部「金德拉要塞内」",
        "location": "北侧 / 西南侧（击破墙壁）",
        "content": "获得超强装甲装配零件【宇宙合金格伦】 ＋ 【超合金新Z】",
        "type": "破墙隐藏"
    },
    {
        "stage": "第3部「以真诚之心」",
        "location": "西北密室×2（击破墙壁）",
        "content": "获得神级强化零件【V-UP组件(U)】 ＋ 【资金 50,000】",
        "type": "破墙隐藏"
    },
    {
        "stage": "第1部「德雷古城」",
        "location": "击倒拜因掉落宝箱",
        "content": "获得圣战士隐藏强机【莱尼克】",
        "type": "BOSS击坠掉落"
    },
    {
        "stage": "第2部「冯·布劳」",
        "location": "击倒凯利掉落宝箱",
        "content": "获得大型MA【瓦尔·瓦罗】",
        "type": "BOSS击坠掉落"
    },
    {
        "stage": "第3部「太平洋上」",
        "location": "击倒谬吉掉落宝箱",
        "content": "获得圣战士黑色重机【兹瓦士】",
        "type": "BOSS击坠掉落"
    },
    {
        "stage": "第3部「月神五号」",
        "location": "击倒哈曼、古利明、马士文掉落宝箱",
        "content": "哈曼掉落【卡碧尼】、古利明掉落【葵·曼沙】、马士文掉落【扎古III改】",
        "type": "BOSS击坠掉落"
    }
]

# 4. 机体改造继承表
remodel_inherits = [
    {
        "before": "古铁 (Alteisen)",
        "after": "古铁巨神 (Alteisen Riese)",
        "timing": "第3部 第3场景 起",
        "note": "南部响介爱机，机体改造、武器改造 100% 沿用，主力直接满改不亏！"
    },
    {
        "before": "白骑士 (Weissritter)",
        "after": "真·白骑士 (Rein Weissritter)",
        "timing": "第3部「月近海·暗礁空域」后",
        "note": "艾克瑟莲机体，需早乙女研究所满足真白骑士条件，改造值完全继承。"
    },
    {
        "before": "ZZ高达",
        "after": "全装甲ZZ高达 (FA ZZ Gundam)",
        "timing": "第3部 第3场景 起",
        "note": "捷多主力座驾，大范围地图炮清场神器，改造全额继承。"
    },
    {
        "before": "翼霸 (Dunbine/Bilbine)",
        "after": "迷彩型翼霸 (夜战型)",
        "timing": "第3部「奈尔加尔重工码头」后",
        "note": "需走拜斯顿威尔路线提前获得翼霸，改造值完美继承升级。"
    },
    {
        "before": "抚子号 (Nadesico)",
        "after": "抚子号 Y组件",
        "timing": "第2部「迎向明天的勇气」起",
        "note": "战舰主炮威力与装甲大幅提升，前期改造投资全额返还沿用。"
    },
    {
        "before": "盖塔1 / 2 / 3",
        "after": "盖塔龙 / 狮虎 / 波塞冬 (Getter Dragon)",
        "timing": "第1部 第24关 后",
        "note": "换代剧情触发，三机改造值自动按对应形态平移继承。"
    },
    {
        "before": "盖塔龙 / 狮虎 / 波塞冬",
        "after": "真·盖塔 1 / 2 / 3 (Shin Getter)",
        "timing": "第3部 早乙女研究所满足条件入手时",
        "note": "盖塔系最终神机，继承盖塔龙的全部改造段数，最暴力输出端。"
    }
]

# 5. 全 20 项 CG 演示与结局收集大全
cg_gallery = [
    {"name": "片头动画 (Opening Movie)", "condition": "游戏启动初期默认获得"},
    {"name": "结局 A (Ending Movie A)", "condition": "获得【真·盖塔】 ＋ 累积熟练度≥50 通关隐藏终章"},
    {"name": "结局 B (Ending Movie B)", "condition": "获得【真·白骑士】 ＋ 累积熟练度≥50 通关隐藏终章"},
    {"name": "结局 C (Ending Movie C)", "condition": "两者皆无（保留原机） ＋ 累积熟练度≥50 通关隐藏终章"},
    {"name": "飞影登场", "condition": "飞影现身的任意关卡，其在地图中触发合体出击时"},
    {"name": "黑狮子合体", "condition": "黑狮子与飞影在战场中执行三位一体合体时"},
    {"name": "凤雷鹰合体", "condition": "凤雷鹰与飞影在战场中执行三位一体合体时"},
    {"name": "爆龙合体", "condition": "爆龙与飞影在战场中执行三位一体合体时"},
    {"name": "剑狼合体", "condition": "剑狼出现的关卡首次触发合体演出时"},
    {"name": "拜坎夫合体", "condition": "第3部「金德拉要塞内」洛姆登场执行最强合体演出"},
    {"name": "弹劾凤合体 A", "condition": "第1部「新宿」关卡中触发首次合体剧情时"},
    {"name": "弹劾凤合体 B", "condition": "第2部「地球近海1」关卡中触发进阶合体剧情时"},
    {"name": "重力爆破 (Gravity Blast)", "condition": "第1部「奈尔加尔重工码头」抚子号出场发射相转移炮"},
    {"name": "艾斯蒂巴利斯出击", "condition": "第2部「防御卫星近海」明人驾驶空战型出击时"},
    {"name": "断空光牙剑", "condition": "第3部「兽战机队基地」断空我HP压至30%以下满足武装觉醒时"},
    {"name": "迪拉德增援", "condition": "第3部「迪拉德近海」开局敌方大军出现增援"},
    {"name": "W魔神 联合出击", "condition": "第3部「巴德斯岛」敌方第一次增援后双魔神共鸣"},
    {"name": "斯派泽分离", "condition": "第2部「冯·布劳」开局古连泰沙分离机动"},
    {"name": "对杰妮拉决战", "condition": "第3部「绿洲宇域」击坠杰妮拉触发"},
    {"name": "天神音波 (God Voice)", "condition": "第3部「妖魔岛」洸击坠巴拉奥取得莱丁新武器后"}
]

# 6. 按进度打卡速查清单
checkpoints = [
    {
        "part": "第1部 地上篇 / 宇宙篇",
        "items": [
            {"stage": "第1关前 准备界面", "action": "断空我机体与武器至少各改1段（解锁第2部野性爆发力）"},
            {"stage": "「东京」", "action": "除葛莱丽亚外敌人全灭 → 葛莱丽亚与巴斯托尔加入"},
            {"stage": "「两个新人类」", "action": "卡美由说得罗莎美亚（前置步骤1）"},
            {"stage": "第3场景三连选", "action": "严格按决策矩阵排序：A(纽约)选1/2位走地上，选3位走拜斯顿威尔"},
            {"stage": "「纽约」", "action": "座间翔说得托度并击坠之；选位决定4A/4B走向"},
            {"stage": "「东南亚吉翁秘密基地」", "action": "斯罗击坠爱娜＝雪山事件；击坠卡特＝所罗门核阻止；放过爱娜＝留京宝梵"},
            {"stage": "「中央亚洲沙漠地区」", "action": "5EP前破3金字塔且不击杀三人，击坠普露；斯罗在队选2/3位＝京宝梵"},
            {"stage": "「宇宙科学研究所」", "action": "斯罗说得爱娜；爱娜→巴尼顺序说得诺利斯（全员生存加入）"},
            {"stage": "「德雷古城」", "action": "击倒拜因回收掉落宝箱＝莱尼克"},
            {"stage": "「早乙女研究所」", "action": "选第1、2位＝德克萨斯麦克加入（否则第3部自动加入）"},
            {"stage": "「无人岛」（第26话）", "action": "贝梅尔存活到第10EP；克丽丝击破G-3、巴尼击破夏亚扎古"},
            {"stage": "最终话「掌控动荡大地者」", "action": "明镜高达HP全程保持>50%；东方不败打残后用非多蒙击坠；开2处宝箱"}
        ]
    },
    {
        "part": "第2部 逆转篇 / 宇宙篇",
        "items": [
            {"stage": "「巨石群」", "action": "3回合内把古罗拜因HP打到50%以下（古罗拜因前置1）"},
            {"stage": "「废弃殖民地带」", "action": "洛姆切换为剑狼形态，2次行动内迅速说得基娜（前置1）"},
            {"stage": "「鲁那兹内部」", "action": "捷多说得普露兹→击退古利明且普露兹HP<20%→捷多再说得；破墙拿奥拉转换器+杰钢"},
            {"stage": "「所罗门内部」", "action": "需核阻止成功：破西南墙拿百式改(熟练≥30)或全装百式改(熟练≤29)"},
            {"stage": "「机甲诺伊德空间」", "action": "出击选第1、2位＝X艾斯蒂巴利斯改；选第3、4位＝ZⅡ"},
            {"stage": "「让宇宙激震」", "action": "击坠迪翁德拉后洛姆说得基娜 → 基娜与科隆正式加入"}
        ]
    },
    {
        "part": "第3部 银河篇 / 决战篇",
        "items": [
            {"stage": "「迪拉德南部」", "action": "骷髅HP压至30%以下，乔说得依路贝拉（零影前置1）"},
            {"stage": "「奈尔加尔重工码头」", "action": "拜斯顿威尔路线翼霸升级为迷彩型翼霸"},
            {"stage": "「早乙女研究所」", "action": "真盖塔/真白骑士二选一：敌人邻接研究所＝真盖塔；不邻接+响介说得艾克瑟莲＝真白骑士"},
            {"stage": "「兽战机队基地」", "action": "断空我交战夏皮罗且HP压到30%以下，双方存活 → 觉醒断空光牙剑"},
            {"stage": "「穆特隆遗迹」&「妖魔岛」", "action": "洸亲自击坠戈斯坦、班加与巴拉奥 → 觉醒天神音波"},
            {"stage": "第3场景三连选", "action": "【必须选择 C(月球) → A(地球) → B(火星)】，规避母舰离脱吃零件恶性BUG"},
            {"stage": "「德克萨斯殖民地」", "action": "因C先于A，捷多可正式说得古罗拜因加入"},
            {"stage": "「史卡尔月面基地」", "action": "玛丽亚说得基丽嘉（奖励特殊技能「精神统一」）"},
            {"stage": "「恶魔殖民地内部」", "action": "多蒙说得蕾因 → 习得合体技「石破LOVELOVE天惊拳」"},
            {"stage": "「金德拉要塞内」", "action": "加鲁迪HP<90%，洛姆→莉娜顺序说得（奖励「精神统一」）；破墙拿2大超合金零件"},
            {"stage": "「月神五号」", "action": "克瓦特罗说得卡特→击坠哈曼/古利明→科说得卡特加入；击坠三大BOSS拿3大MA机体"},
            {"stage": "「火星机甲诺伊德基地」", "action": "罗美娜说得→乔击坠依路贝拉（零影加入）；【10回合内通关】（白鸟九十九加入条件）"},
            {"stage": "第99话「走向决战的银河」", "action": "通关时【累积熟练度 ≥ 50】 → 解锁隐藏终章「逆袭的夏亚篇」"}
        ]
    }
]

# 7. 豆知识与避坑秘技
tips = [
    {
        "title": "规避强化零件永久蒸发重大BUG",
        "tag": "致命陷阱",
        "content": "在第3部第3场景中，若把『地球篇』放在最后一个攻克，母舰会在关卡结算时暂时离脱。由于游戏底层事件代码缺陷，离脱时母舰装备的所有强化零件将直接被系统从内存注销且无法恢复！对策：必须按照『C(月球) → A(地球) → B(火星)』的顺序攻略！"
    },
    {
        "title": "熟练度双控平衡法（HWS vs 逆袭夏亚）",
        "tag": "战术统筹",
        "content": "v高达HWS需要进入第3部第3场景月球篇前难度为NORMAL（熟练度低于当前关卡数÷2）；而最终隐藏章『逆袭的夏亚』要求第99话通关时熟练度≥50。操作方案：前期精确放水将熟练度压制在 38 以下进入月球篇取得 HWS，之后全速收割所有BOSS熟练度冲破 50 点，两全其美。"
    },
    {
        "title": "全灭练级与资金翻倍刷分法",
        "tag": "资源收益",
        "content": "当打不过强力BOSS或资金捉襟见肘时，可在战斗中派遣高幸运、高努力机体击破精英怪并收割经验资金，随后主动让母舰被击坠或达成败北条件。游戏将保留当关所得全部金钱和等级重新开始该关，是攻克高难度关卡的经典战术。"
    },
    {
        "title": "金手指面板与原版名称速查",
        "tag": "金手指对照",
        "content": "在金手指工坊中：翼霸对应『维尔宾』、迷彩型对应『维尔宾(夜战型)』、真白骑士对应『白骑士＆白骑士·里昂』、古铁巨神对应『古铁＆古铁·里昂』、剑狼对应『拳龙』、普露兹对应『普露二号』、休巴兹对应『施瓦茨』。"
    }
]

# 输出完整的 secrets.js
output = {
    "SRW_SECRETS": base_secrets,
    "SRW_ROUTE_BRANCHES": branches,
    "SRW_CONTAINERS": containers,
    "SRW_REMODEL_INHERIT": remodel_inherits,
    "SRW_CG_GALLERY": cg_gallery,
    "SRW_CHECKPOINTS": checkpoints,
    "SRW_TIPS_GUIDE": tips
}

js_content = f"""// IMPACT 隐藏要素终极全装数据库 (纯中文 / 零假名 / 社区权威术语对齐)
// 包含：32项机体武器要素、3大决策矩阵、13大隐藏宝箱、7大改造继承、20大CG收集、全章节打卡速查、避坑秘技

window.SRW_SECRETS = {json.dumps(base_secrets, ensure_ascii=False, indent=2)};
window.SRW_ROUTE_BRANCHES = {json.dumps(branches, ensure_ascii=False, indent=2)};
window.SRW_CONTAINERS = {json.dumps(containers, ensure_ascii=False, indent=2)};
window.SRW_REMODEL_INHERIT = {json.dumps(remodel_inherits, ensure_ascii=False, indent=2)};
window.SRW_CG_GALLERY = {json.dumps(cg_gallery, ensure_ascii=False, indent=2)};
window.SRW_CHECKPOINTS = {json.dumps(checkpoints, ensure_ascii=False, indent=2)};
window.SRW_TIPS_GUIDE = {json.dumps(tips, ensure_ascii=False, indent=2)};
"""

with open("/Volumes/D2T/projects/srw-game-modding/web/data/secrets.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("secrets.js 全新升级完成！数据量与维度大幅扩充！")
