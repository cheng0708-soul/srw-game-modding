import json

with open('/Volumes/D2T/projects/srw-game-modding/docs/data/srworld_stages.js', 'r', encoding='utf-8') as f:
    text = f.read().replace('window.SRW_STAGES_GUIDE = ', '').rstrip(';\n ')
stages = json.loads(text)

fine_replacements = [
    # 标题纠正
    ("·最终话", "然后前往决战的银河"),
    ("忌记忆", "伴随着可悲的记忆"),
    ("宇宙越", "跨越莫比乌斯的宇宙"),
    
    # 最终Boss & 逆鸭关卡精修
    ("阿露菲米（·）", "阿露菲米（佩露赛因·莉希卡尔）"),
    ("（原生种监察者）", "原生种监察者（Regisseur）"),
    ("葵丝（α·）", "葵丝（α·阿基尔）"),
    ("·吉翁兵（·）", "新吉翁兵（基拉·德卡）"),
    ("乍得·多加(邱尼)", "乍得·多加（邱尼机）"),
    ("（·()）", "蕾森（基拉·德卡·蕾森专用机）"),
    ("拉·凯拉姆号", "拟·亚加玛 / 拉·凯拉姆"),
    ("御统百合香（抚...", "御统百合香（抚子号）"),
    ("动用金手指把小罗丽调出来先XD", "动用金手指把萝莉机师阿露菲米调出来先"),
    ("艾克赛玲", "艾克瑟莲"),
    ("艾克赛琳", "艾克瑟莲"),
    ("裤袜脱落", "克瓦特罗（夏亚）"),
    ("阿寳", "阿姆罗"),
    ("阿宝", "阿姆罗"),
    ("阿中", "夏亚"),
    ("阿丽", "阿露菲米"),
    ("阿丽乖乖地", "阿露菲米乖乖地"),
    ("收声！再吵就给我去冰箱！", "“胡闹！给我去禁闭室反省！”"),
    ("番組必终来。人、...『最终回』！", "“故事终有落幕之时。属于众人的壮烈决战……最终回！”"),
    ("（阿姆罗：、！", "（阿姆罗：“那是自私的任性！”"),
    ("（阿姆罗：那是自私的任性！", "（阿姆罗：“那是自私的任性！”）")
]

for s in stages:
    for field in ['stage_number', 'title', 'skill_req', 'tactics']:
        val = s.get(field, '')
        if not val:
            continue
        for old, new in fine_replacements:
            val = val.replace(old, new)
        s[field] = val.strip()

# 写回 web 与 docs
output_js = "window.SRW_STAGES_GUIDE = " + json.dumps(stages, ensure_ascii=False, indent=2) + ";\n"

with open('/Volumes/D2T/projects/srw-game-modding/web/data/srworld_stages.js', 'w', encoding='utf-8') as f:
    f.write(output_js)

with open('/Volumes/D2T/projects/srw-game-modding/docs/data/srworld_stages.js', 'w', encoding='utf-8') as f:
    f.write(output_js)

print("决战关卡精修完成！")
