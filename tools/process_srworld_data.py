import os
import re
import json

base_dir = '/Volumes/D2T/projects/srw-game-modding'
src_dir = os.path.join(base_dir, 'research/srworld')
data_dir = os.path.join(base_dir, 'web/data')
os.makedirs(data_dir, exist_ok=True)

# 繁简常用字转换字典 (涵盖机战常用繁体字)
t2s_dict = {
    '氣力': '气力', '攻擊': '攻击', '說明': '说明', '參加': '参加', '參與': '参与',
    '機體': '机体', '機師': '机师', '駕駛': '驾驶', '熟練度': '熟练度', '勝利': '胜利',
    '條件': '条件', '敗北': '败北', '敵人': '敌人', '敵': '敌', '隱藏': '隐藏',
    '獲得': '获得', '入手': '入手', '關卡': '关卡', '話': '话', '傷': '伤',
    '迴避': '回避', '命中': '命中', '防禦': '防御', '專利': '专利', '專用': '专用',
    '戰鬥': '战斗', '戰': '战', '狀態': '状态', '裝甲': '装甲', '運動性': '运动性',
    '強化': '强化', '殘彈': '残弹', '回復': '恢复', '消費': '消耗', '點': '点',
    '發動': '发动', '幾率': '几率', '標誌': '标志', '等級': '等级', '補給': '补给',
    '修理': '修理', '變形': '变形', '合體': '合体', '分離': '分离', '換裝': '换装',
    '登場': '登场', '擊墜': '击坠', '擊破': '击破', '撤退': '撤退', '增援': '增援',
    '連邦': '联邦', '鋼彈': '高达', '異變': '异变', '奪還': '夺还', '作戰': '作战',
    '混亂': '混乱', '決戰': '决战', '逆襲': '逆袭', '後記': '后记', '綫': '线',
    '閒': '间', '陣': '阵', '兩': '两', '隻': '只', '個': '个', '這': '这',
    '麽': '么', '爲': '为', '與': '与', '屬': '属', '於': '于', '隨': '随',
    '關': '关', '開': '开', '頭': '头', '總': '总', '數': '数', '結': '结',
    '終': '终', '難': '难', '極': '极', '強': '强', '寶': '宝', '術': '术',
    '師': '师', '飛': '飞', '竜': '龙', '龍': '龙', '滅': '灭', '萬': '万',
    '隊': '队', '圖': '图', '紙': '纸', '號': '号', '愛': '爱', '靈': '灵'
}

def to_simplified(text):
    if not text:
        return ""
    res = text
    for k, v in t2s_dict.items():
        res = res.replace(k, v)
    return res

# ==============================================================
# 1. 解析合体技 (I_data08.utf8.txt)
# ==============================================================
combos = []
combos_file = os.path.join(src_dir, 'I_data08.utf8.txt')
if os.path.exists(combos_file):
    with open(combos_file, 'r', encoding='utf-8') as f:
        c_text = f.read()
    c_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', c_text, re.S)
    for r in c_rows[1:]:
        cols = [re.sub(r'<[^>]+>', ' ', c).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)]
        cols = [re.sub(r'\s+', ' ', c) for c in cols]
        if len(cols) >= 6:
            name, mecha, req, rng, power, desc = cols[:6]
            combos.append({
                'id': f'combo_{len(combos)+1}',
                'name': to_simplified(name),
                'mecha': to_simplified(mecha),
                'req': to_simplified(req),
                'range': rng,
                'power': power,
                'desc': to_simplified(desc)
            })
print(f'Parsed {len(combos)} combo attacks.')

# ==============================================================
# 2. 解析精神一览 (I_data04.utf8.txt)
# ==============================================================
spirits = []
spirits_file = os.path.join(src_dir, 'I_data04.utf8.txt')
if os.path.exists(spirits_file):
    with open(spirits_file, 'r', encoding='utf-8') as f:
        s_text = f.read()
    s_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', s_text, re.S)
    for r in s_rows[1:]:
        cols = [re.sub(r'<[^>]+>', ' ', c).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)]
        cols = [re.sub(r'\s+', ' ', c) for c in cols]
        if len(cols) >= 3:
            name, sp, desc = cols[:3]
            spirits.append({
                'id': f'spirit_{len(spirits)+1}',
                'name': to_simplified(name),
                'sp': sp,
                'desc': to_simplified(desc)
            })
print(f'Parsed {len(spirits)} spirit commands.')

# ==============================================================
# 3. 解析道具与强化芯片 (I_data07.utf8.txt)
# ==============================================================
items = []
items_file = os.path.join(src_dir, 'I_data07.utf8.txt')
if os.path.exists(items_file):
    with open(items_file, 'r', encoding='utf-8') as f:
        it_text = f.read()
    it_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', it_text, re.S)
    for r in it_rows[1:]:
        cols = [re.sub(r'<[^>]+>', ' ', c).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)]
        cols = [re.sub(r'\s+', ' ', c) for c in cols]
        if len(cols) >= 2:
            name, desc = cols[:2]
            cat = '能力加成'
            if any(k in desc for k in ['回復', '恢复', '消費', '消耗']):
                cat = '消耗品'
            elif any(k in name for k in ['裝甲', '装甲', 'バリア', '护盾', 'チョバム', '大型']):
                cat = '防御与装甲'
            elif any(k in name for k in ['高性能', '照準', 'レーダー', 'サイト', 'ブースター']):
                cat = '移动与射程'
            items.append({
                'id': f'item_{len(items)+1}',
                'name': to_simplified(name),
                'category': cat,
                'desc': to_simplified(desc)
            })
print(f'Parsed {len(items)} items/parts.')

# ==============================================================
# 4. 解析机体与机师特殊技能 (I_data05.utf8.txt)
# ==============================================================
skills = []
skills_file = os.path.join(src_dir, 'I_data05.utf8.txt')
if os.path.exists(skills_file):
    with open(skills_file, 'r', encoding='utf-8') as f:
        sk_text = f.read()
    sk_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', sk_text, re.S)
    for r in sk_rows[1:]:
        cols = [re.sub(r'<[^>]+>', ' ', c).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)]
        cols = [re.sub(r'\s+', ' ', c) for c in cols]
        if len(cols) >= 2:
            name, desc = cols[:2]
            skills.append({
                'id': f'skill_{len(skills)+1}',
                'name': to_simplified(name),
                'desc': to_simplified(desc)
            })
print(f'Parsed {len(skills)} pilot & mecha special abilities.')

# 导出战术要素数据
srw_tactics = {
    'combos': combos,
    'spirits': spirits,
    'items': items,
    'skills': skills
}
with open(os.path.join(data_dir, 'srworld_tactics.js'), 'w', encoding='utf-8') as f:
    f.write('window.SRW_SRWORLD_TACTICS = ' + json.dumps(srw_tactics, ensure_ascii=False, indent=2) + ';\n')

# ==============================================================
# 5. 解析 关卡战术攻防手册 (从 18 个关卡流程文件中解析)
# ==============================================================
stage_files = [
    ('第1部 地上篇', 'Scene 1 异变', 'I_data13_a_1.utf8.txt'),
    ('第1部 地上篇', 'Scene 2 日本', 'I_data13_a_2.utf8.txt'),
    ('第1部 地上篇', 'Scene 3 世界', 'I_data13_a_3.utf8.txt'),
    ('第1部 地上篇', 'Scene 4B 地底帝国侵略', 'I_data13_a_4.utf8.txt'),
    ('第1部 地上篇', 'Scene 5 百鬼帝国的威胁', 'I_data13_a_5.utf8.txt'),
    ('第1部 地上篇', 'Scene 6 贾布罗夺还', 'I_data13_a_6.utf8.txt'),
    ('第2部 宇宙篇', 'Scene 1 侵略', 'I_data13_b_1.utf8.txt'),
    ('第2部 宇宙篇', 'Scene 2 侵略者', 'I_data13_b_2.utf8.txt'),
    ('第2部 宇宙篇', 'Scene 3 暗跃', 'I_data13_b_3.utf8.txt'),
    ('第2部 宇宙篇', 'Scene 4 星之屑作战', 'I_data13_b_4.utf8.txt'),
    ('第2部 宇宙篇', 'Scene 5 殖民卫星夺还', 'I_data13_b_5.utf8.txt'),
    ('第2部 宇宙篇', 'Scene 6 地球圈混乱', 'I_data13_b_6.utf8.txt'),
    ('第3部 银河篇', 'Scene 1 迪拉德突入', 'I_data13_c_1.utf8.txt'),
    ('第3部 银河篇', 'Scene 2 浮上', 'I_data13_c_2.utf8.txt'),
    ('第3部 银河篇', 'Scene 3C 月球篇', 'I_data13_c_3_1.utf8.txt'),
    ('第3部 银河篇', 'Scene 3A 地球篇', 'I_data13_c_3_2.utf8.txt'),
    ('第3部 银河篇', 'Scene 3B 火星篇', 'I_data13_c_3_3.utf8.txt'),
    ('第3部 银河篇', 'Scene 4 宇宙激震', 'I_data13_c_4.utf8.txt'),
    ('第3部 银河篇', 'Scene 5 银河决战', 'I_data13_c_5.utf8.txt'),
    ('隐藏终章', 'Scene 6 逆袭的夏亚', 'I_data13_c_6.utf8.txt')
]

stages_guide = []
stage_id_counter = 1

for part, scene_title, fname in stage_files:
    fpath = os.path.join(src_dir, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 清洗掉 html 标签获取段落
    # 按照 "第XX话" 切分
    parts_raw = re.split(r'(?:第\s*(\d+)\s*話|第\s*(\d+)\s*话)', content)
    # parts_raw 的结构是: [前置文本, 话数1, None, 内容1, 话数2, None, 内容2, ...]
    
    # 提取本篇注意事项
    scene_notes = ""
    notes_match = re.search(r'本篇注意事項[：:](.*?)(?:第\s*\d+\s*話|第\s*\d+\s*话|\Z)', content, re.S)
    if notes_match:
        scene_notes = re.sub(r'<[^>]+>', ' ', notes_match.group(1))
        scene_notes = re.sub(r'\s+', ' ', scene_notes).strip()

    # 循环提取每一话
    idx = 1
    while idx < len(parts_raw):
        s_num = parts_raw[idx] or parts_raw[idx+1]
        raw_body = parts_raw[idx+2] if (idx+2) < len(parts_raw) else ""
        idx += 3
        if not s_num or not raw_body:
            continue

        clean_body = re.sub(r'<[^>]+>', '\n', raw_body)
        lines = [l.strip() for l in clean_body.split('\n') if l.strip()]
        
        title_line = lines[0] if lines else f'第{s_num}话'
        title_line = re.sub(r'[\-—=]+', '', title_line).strip()
        
        # 提取熟练度
        skill_req = ""
        skill_match = re.search(r'熟練度\s*[：:]([^\n]+)', clean_body)
        if skill_match:
            skill_req = skill_match.group(1).strip()
            
        # 提取初期敌军
        enemies_init = ""
        enemy_match = re.search(r'敵方初期配置\s*[：:]([^\n]+)', clean_body)
        if enemy_match:
            enemies_init = enemy_match.group(1).strip()

        # 战术提示（前 400 字符的核心摘要）
        tactics_summary = []
        for l in lines[1:]:
            if any(k in l for k in ['熟練度', '敵方初期配置', '本節完', 'Next', 'Back', 'Top']):
                continue
            if len(l) > 10:
                tactics_summary.append(l)
            if len(' '.join(tactics_summary)) > 300:
                break
        tactics_text = ' '.join(tactics_summary)

        stages_guide.append({
            'id': f'stage_{stage_id_counter}',
            'part': part,
            'scene': scene_title,
            'scene_notes': to_simplified(scene_notes),
            'stage_number': f'第{s_num}话',
            'title': to_simplified(title_line),
            'skill_req': to_simplified(skill_req) or '按击坠/回合条件达成',
            'enemies': to_simplified(enemies_init),
            'tactics': to_simplified(tactics_text)
        })
        stage_id_counter += 1

with open(os.path.join(data_dir, 'srworld_stages.js'), 'w', encoding='utf-8') as f:
    f.write('window.SRW_STAGES_GUIDE = ' + json.dumps(stages_guide, ensure_ascii=False, indent=2) + ';\n')

print(f'Generated srworld_stages.js with {len(stages_guide)} detailed stage tactical guides!')
