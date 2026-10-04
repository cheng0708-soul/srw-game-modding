import json
import re

# 1. 加载 OpenCC 词典
t2s_dict = {}

# 加载词组
with open('/tmp/TSPhrases.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            t2s_dict[parts[0]] = parts[1].split(' ')[0]

# 加载单字
with open('/tmp/TSCharacters.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            t2s_dict[parts[0]] = parts[1].split(' ')[0]

def to_simplified(text):
    # 先做长词匹配替换，再做单字替换
    # 按长度降序排列长词
    sorted_words = sorted([k for k in t2s_dict.keys() if len(k) > 1], key=lambda x: -len(x))
    for w in sorted_words:
        if w in text:
            text = text.replace(w, t2s_dict[w])
    # 单字替换
    chars = [t2s_dict.get(c, c) for c in text]
    return ''.join(chars)

# 2. 机战社区权威专有名词表与病句修正
SRW_REPLACEMENTS = [
    # 核心主角与机体译名纠正
    ('廢铁', '古铁'),
    ('废铁', '古铁'),
    ('小白', '白骑士'),
    ('朗德·贝尔', '隆德·贝尔'),
    ('朗德贝尔', '隆德·贝尔'),
    ('式部司马式部司马亮', '式部雅人与司马亮'),
    ('司马亮铁壁', '司马亮开铁壁'),
    ('剛多爾', '刚多尔母舰'),
    ('刚多尔', '刚多尔母舰'),
    ('刚多尔母舰母舰', '刚多尔母舰'),
    ('盖塔变形钻地', '盖塔变形为盖塔2钻地'),
    ('魔神Z大魔神', '魔神Z、大魔神'),
    ('克连泰沙', '古连泰沙'),
    ('克连戴沙', '古连泰沙'),
    ('克连戴萨', '古连泰沙'),
    ('断空我一个了', '断空我一台了'),
    ('金米岛', '康培岛（金米岛）'),
    ('贾布罗', '贾布罗基地'),
    ('机械兽K7', '机械兽道拉拉K7'),
    ('机械兽U6', '机械兽加拉达K7/U6'),
    ('机械兽托洛斯D7', '机械兽托洛斯D7'),
    ('机械兽热那亚M9', '机械兽热那亚M9'),
    ('咸蛋超人甲', '敌机甲'),
    ('咸蛋超人', '敌机'),
    ('打针', '修理补给'),
    ('移攻3格', '移动攻击范围3格'),
    
    # 经典名词与规范
    ('百武帝国', '百鬼帝国'),
    ('贝加星联合军', '维加星联合军'),
    ('贝加星', '维加星'),
    ('木星蜥蜴', '木星蜥蜴（木连）'),
    ('圆盘兽', '圆盘兽'),
    ('机械恐龙', '机械恐龙'),
    ('机械白骨鬼', '机械白骨鬼'),
    ('机械铁甲鬼', '机械铁甲鬼'),
    ('特装型老虎', '老虎特装型（诺利斯专用）'),
    ('EZ-8', 'Ez-8'),
    ('扎古改', '扎古II改'),
    ('NT-1', '高达NT-1（阿历克斯）'),
    ('高达NT-1（阿历克斯）驾驶员', '高达NT-1驾驶员'),
    ('波士波士', '波士驾驶波士机器人'),
    ('波士（波士）', '波士（波士机器人）'),
    ('甲儿（魔神Z）', '甲儿（魔神Z）'),
    ('沙耶加（戴安娜A）', '沙耶加（戴安娜A）'),
    ('叶月博士（刚多尔母舰）', '叶月博士（刚多尔母舰）'),
    ('龙马（盖塔1）', '龙马（盖塔1）'),
    ('诺利斯（老虎特装型（诺利斯专用））', '诺利斯（老虎特装型）'),
    ('希德勒元帅（机械铁甲鬼）', '希德勒元帅（机械铁甲鬼）'),
    ('阿修罗男爵（飞行要塞咕噜）', '阿修罗男爵（飞行要塞咕噜）'),
    ('机械兽热那亚M9', '机械兽热那亚M9'),
    
    # 符号清理
    ('（:P）', ''),
    (':P', ''),
    ('T.T', ''),
    ('  ', ' '),
    ('：：', '：'),
    ('、、', '、'),
    ('。。', '。'),
    ('（ ', '（'),
    (' ）', '）')
]

with open('/Volumes/D2T/projects/srw-game-modding/web/data/srworld_stages.js', 'r', encoding='utf-8') as f:
    raw_js = f.read()

# 提取 JSON 列表
json_str = raw_js.replace('window.SRW_STAGES_GUIDE = ', '').rstrip(';\n ')
stages = json.loads(json_str)

print(f"总计关卡: {len(stages)}")

for s in stages:
    for field in ['part', 'scene', 'stage_number', 'title', 'skill_req', 'enemies', 'tactics']:
        val = s.get(field, '')
        if not val:
            continue
        # 1. 繁转简
        val = to_simplified(val)
        # 2. 术语纠正
        for old, new in SRW_REPLACEMENTS:
            val = val.replace(old, new)
        s[field] = val.strip()

# 写回
output_js = "window.SRW_STAGES_GUIDE = " + json.dumps(stages, ensure_ascii=False, indent=2) + ";\n"

with open('/Volumes/D2T/projects/srw-game-modding/web/data/srworld_stages.js', 'w', encoding='utf-8') as f:
    f.write(output_js)

with open('/Volumes/D2T/projects/srw-game-modding/docs/data/srworld_stages.js', 'w', encoding='utf-8') as f:
    f.write(output_js)

print("完成汉化和规范化转换！")
