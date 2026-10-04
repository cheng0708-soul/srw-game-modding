import os
import re
import json

base_dir = '/Volumes/D2T/projects/srw-game-modding'
web_dir = os.path.join(base_dir, 'web')
data_dir = os.path.join(web_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

# 1. 解析 pnach
pnach_path = os.path.join(base_dir, 'pnach/SLPS-25104_10C3D363.pnach')
with open(pnach_path, 'r', encoding='utf-8', errors='ignore') as f:
    pnach_raw = f.read()

cheats = []
blocks = pnach_raw.split('\n[')
for i, b in enumerate(blocks):
    if i == 0:
        continue
    b = '[' + b
    title_match = re.search(r'\[(.*?)\]', b)
    if not title_match:
        continue
    title = title_match.group(1).strip()
    desc_match = re.search(r'description=(.*)', b)
    desc = desc_match.group(1).strip() if desc_match else title
    patches = re.findall(r'(patch=[^\n\r]+)', b)
    raw_codes = re.findall(r'//\s*原码:\s*([^\n\r]+)', b)
    notes = re.findall(r'//\s*说明:\s*([^\n\r]+)', b)
    
    if any(k in title for k in ['资金', '熟练度', '精神', 'EN', '气力', '经验', '金钱', '修理', '补给']):
        cat = '便利辅助'
    elif '机师' in title or '加入' in title or '驾驶' in title:
        cat = '隐藏机师'
    elif '合体技' in title or '必杀技' in title:
        cat = '必杀技能'
    elif any(k in title for k in ['东方不败', '尊者', '神高达', '雪霸', '全装甲百式改', '京宝梵', '瓦兹', '白骑士', '古铁', '纯白', '古铁巨人']):
        cat = '热门王牌机'
    elif any(k in title for k in ['高达', '扎古', '吉姆', '勇士', '大魔', '沙扎比', '卡碧尼', '猎犬', '汉谟拉比', '雅典娜', '加普兰', '拜亚兰']):
        cat = '高达系列'
    elif any(k in title for k in ['魔神', '盖塔', '铁金刚', '维纳斯', '戴安娜', '波士', '米涅瓦']):
        cat = '魔神与盖塔'
    elif any(k in title for k in ['丹拜因', '比尔拜因', '巴斯特尔', '维尔宾', '兹瓦斯', '莱拉克']):
        cat = '圣战士系列'
    else:
        cat = '超级与其他'

    cheats.append({
        'id': f'cheat_{i}',
        'title': title,
        'description': desc,
        'category': cat,
        'patches': patches,
        'raw_code': raw_codes[0] if raw_codes else '',
        'note': notes[0] if notes else '',
        'default_enabled': (i <= 20)
    })

with open(os.path.join(data_dir, 'cheats.js'), 'w', encoding='utf-8') as f:
    f.write('window.SRW_CHEATS = ' + json.dumps(cheats, ensure_ascii=False, indent=2) + ';\n')

# 2. 解析 隐藏要素 Markdown 表格
doc_path = os.path.join(base_dir, 'research/隐藏要素总整理-中文-2026-10-04.md')
with open(doc_path, 'r', encoding='utf-8') as f:
    doc_text = f.read()

def parse_markdown_table(table_text):
    rows = []
    lines = [l.strip() for l in table_text.strip().split('\n') if l.strip()]
    if len(lines) < 2:
        return rows
    # headers
    headers = [h.strip() for h in lines[0].strip('|').split('|')]
    for line in lines[2:]:
        if not line.startswith('|'):
            continue
        cols = [c.strip() for c in line.strip('|').split('|')]
        if len(cols) == len(headers):
            row_dict = dict(zip(headers, cols))
            rows.append(row_dict)
    return rows

# 提取 §二、§三、§四 的表格
secrets = []

# Part 1
p1_text = doc_text[doc_text.find('## §二 第1部 隐藏要素'):doc_text.find('## §三 第2部 隐藏要素')]
p1_table = p1_text[p1_text.find('| # |'):]
p1_table = p1_table[:p1_table.find('\n\n')]
for r in parse_markdown_table(p1_table):
    r['part'] = '第1部 地上/宇宙篇'
    secrets.append(r)

# Part 2
p2_text = doc_text[doc_text.find('## §三 第2部 隐藏要素'):doc_text.find('## §四 第3部 隐藏要素')]
p2_table = p2_text[p2_text.find('| # |'):]
p2_table = p2_table[:p2_table.find('\n\n')]
for r in parse_markdown_table(p2_table):
    r['part'] = '第2部 逆转篇'
    secrets.append(r)

# Part 3
p3_text = doc_text[doc_text.find('## §四 第3部 隐藏要素'):doc_text.find('## §五 关键选择指南')]
p3_table = p3_text[p3_text.find('| # |'):]
p3_table = p3_table[:p3_table.find('\n\n')]
for r in parse_markdown_table(p3_table):
    r['part'] = '第3部 银河篇'
    secrets.append(r)

# 处理 secrets 数据字段和配图
for idx, s in enumerate(secrets):
    s['id'] = f'sec_{idx+1}'
    name = s.get('要素', '')
    s['title'] = name
    cond = s.get('条件', '')
    s['condition'] = cond
    
    # 提取关键关卡
    stages = re.findall(r'「(.*?)」', cond)
    s['stages'] = stages[:3]
    
    # 匹配图片
    if any(k in name for k in ['东方不败', '尊者', '盟主']):
        s['image'] = 'master_gundam.png'
    elif any(k in name for k in ['神高达', '石破', '休巴兹', '明镜']):
        s['image'] = 'god_gundam.png'
    elif '百式' in name:
        s['image'] = 'fa_hyakushiki.png'
    elif '京宝梵' in name:
        s['image'] = 'kampfer.jpg'
    elif any(k in name for k in ['真·白骑士', '白骑士']):
        s['image'] = 'rein_weissritter.png'
    elif any(k in name for k in ['古铁', '京介']):
        s['image'] = 'alteisen_riese.png'
    elif any(k in name for k in ['登霸', '翼霸', '巴斯托尔']):
        s['image'] = 'alteisen.png'
    elif any(k in name for k in ['逆袭的夏亚', '隐藏章']):
        s['image'] = 'srw_impact_hero_banner.jpg'
    else:
        s['image'] = 'srw_tactical_insignia.jpg'

with open(os.path.join(data_dir, 'secrets.js'), 'w', encoding='utf-8') as f:
    f.write('window.SRW_SECRETS = ' + json.dumps(secrets, ensure_ascii=False, indent=2) + ';\n')
print(f'Generated secrets.js with {len(secrets)} items.')

# 3. 提取 进度速查表 (§六)
timeline_pattern = r'###\s*(第[123]部)\n\n(\|[\s\S]*?)(?=(?:\n###|\n##|\Z))'
timeline_matches = re.findall(timeline_pattern, doc_text)
timeline_tables = {}
for part_name, t_text in timeline_matches:
    rows = parse_markdown_table(t_text)
    timeline_tables[part_name] = rows

with open(os.path.join(data_dir, 'timeline.js'), 'w', encoding='utf-8') as f:
    f.write('window.SRW_TIMELINE = ' + json.dumps(timeline_tables, ensure_ascii=False, indent=2) + ';\n')
print(f'Generated timeline.js with {len(timeline_tables)} parts.')

# 4. 提取 改造继承表 与 集装箱表 (§七)
inherit_text = doc_text[doc_text.find('### 改造继承表'):doc_text.find('### 熟练度奖励特殊技能')]
inherit_table = inherit_text[inherit_text.find('|'):]
inherit_table = inherit_table[:inherit_table.find('\n\n')]
inherit_rows = parse_markdown_table(inherit_table)

container_text = doc_text[doc_text.find('### 隐藏集装箱一览'):doc_text.find('### 改造继承表')]
container_table = container_text[container_text.find('|'):]
container_table = container_table[:container_table.find('\n\n')]
container_rows = parse_markdown_table(container_table)

# 5. 提取 全CG获得条件 (§九)
cg_text = doc_text[doc_text.find('## §九 附录：全CG演示获得条件'):doc_text.find('## §十 来源与备注')]
cg_table = cg_text[cg_text.find('|'):]
cg_table = cg_table[:cg_table.find('\n\n')]
cg_rows = parse_markdown_table(cg_table)

extra_data = {
    'inheritances': inherit_rows,
    'containers': container_rows,
    'cg_gallery': cg_rows
}
with open(os.path.join(data_dir, 'extras.js'), 'w', encoding='utf-8') as f:
    f.write('window.SRW_EXTRAS = ' + json.dumps(extra_data, ensure_ascii=False, indent=2) + ';\n')
print('Generated extras.js (inheritances, containers, CG).')
