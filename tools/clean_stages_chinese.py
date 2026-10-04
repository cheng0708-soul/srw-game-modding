import os
import re
import json

base_dir = '/Volumes/D2T/projects/srw-game-modding'
stages_path = os.path.join(base_dir, 'web/data/srworld_stages.js')

with open(stages_path, 'r', encoding='utf-8') as f:
    text = f.read()
raw_stages = json.loads(text.replace('window.SRW_STAGES_GUIDE = ', '').rstrip(';\n'))

# 关卡名称专门对照表
stage_title_map = {
    '飞龙乘雲': '飞龙乘云',
    '3心': '三颗心',
    '3つの心': '三颗心',
    '黑鐵城': '黑铁之城',
    '黑鐵の城': '黑铁之城',
    'ファイヤー·オン！': 'Fire On！火力全开！',
    '「男らしく」でいこう': '男子汉的坚守',
    '舞い上がる翼、舞い降りた翼': '舞扬之翼、降临之翼',
    '宿命の战火': '宿命的战火',
    '黑色死神': '黑色死神',
    '灼热の咆哮': '灼热的咆哮',
    '剑皇宿命': '剑皇宿命',
    '异变': '异变',
    '夺还': '夺还',
    '混乱': '混乱',
    '决战': '决战',
    '逆袭のシャア': '逆袭的夏亚'
}

# 彻底的繁简转换大字典
s_map = {
    '雲': '云', '亞': '亚', '瑪': '玛', '頭': '头', '霧': '雾', '話': '话', '發': '发',
    '牢': '牢', '騷': '骚', '員': '员', '麗': '丽', '絲': '丝', '認': '认', '為': '为',
    '聯': '联', '邦': '邦', '軍': '军', '備': '备', '館': '馆', '進': '进', '隸': '隶',
    '屬': '属', '於': '于', '僅': '仅', '嚴': '严', '峻': '峻', '勢': '势', '應': '应',
    '這': '这', '麽': '么', '兩': '两', '隻': '只', '個': '个', '機': '机', '擊': '击',
    '墜': '坠', '鐵': '铁', '敗': '败', '選': '选', '擇': '择', '陣': '阵', '圖': '图',
    '紙': '纸', '開': '开', '始': '始', '結': '结', '束': '束', '隨': '随', '著': '着',
    '戰': '战', '鬥': '斗', '態': '态', '裝': '装', '甲': '甲', '運': '运', '動': '动',
    '殘': '残', '彈': '弹', '復': '复', '點': '点', '動': '动', '幾': '几', '率': '率',
    '標': '标', '誌': '志', '級': '级', '體': '体', '師': '师', '駕': '驾', '駛': '驶',
    '隱': '隐', '藏': '藏', '獲': '获', '得': '得', '條': '条', '件': '件', '難': '难',
    '寶': '宝', '術': '术', '滅': '灭', '萬': '万', '隊': '队', '號': '号', '愛': '爱',
    '靈': '灵', '獨': '独', '立': '立', '斷': '断', '敵': '敌', '來': '来', '報': '报',
    '談': '谈', '論': '论', '間': '间', '傷': '伤', '氣': '气', '力': '力', '迴': '回',
    '避': '避', '防': '防', '禦': '御', '專': '专', '變': '变', '形': '形', '合': '合',
    '分': '分', '離': '离', '換': '换', '登': '登', '場': '场', '破': '破', '增': '增',
    '援': '援', '鋼': '钢', '異': '异', '奪': '夺', '還': '还', '作': '作', '混': '混',
    '亂': '乱', '決': '决', '逆': '逆', '襲': '袭', '後': '后', '記': '记', '綫': '线',
    '關': '关', '總': '总', '數': '数', '終': '终', '極': '极', '強': '强', '飛': '飞',
    '竜': '龙', '龍': '龙', '補': '补', '給': '给', '修': '修', '理': '理'
}

# 叠字与错词修正
cleanups = [
    ('藤原藤原', '藤原'),
    ('戴安娜AA', '戴安娜A'),
    ('飞行要塞咕噜飞行要塞', '飞行要塞咕噜'),
    ('咕噜飞行要塞', '飞行要塞咕噜'),
    ('热那亚M9M9', '热那亚M9'),
    ('托洛斯D7D7', '托洛斯D7'),
    ('贝尔加斯V5V5', '贝尔加斯V5'),
    ('魔神ZZ', '魔神Z'),
    ('波士波士', '波士'),
    ('刚多尔母舰号', '刚多尔母舰'),
    ('特装型老虎特装型', '特装型老虎'),
    ('盖塔11', '盖塔1'),
    ('机械恐龙·扎伊', '机械恐龙·扎伊'),
    ('机械恐龙·萨奇', '机械恐龙·萨奇'),
    ('机械恐龙·巴德', '机械恐龙·巴德'),
    ('机械恐龙·', '机械恐龙'),
    ('机械铁甲鬼', '机械铁甲鬼'),
    ('阿修罗男爵男爵', '阿修罗男爵'),
    ('古铁巨神巨神', '古铁巨神'),
    ('白骑士白骑士', '白骑士')
]

kana_re = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]+')

cleaned_stages = []
for s in raw_stages:
    st_title = s.get('title', '')
    tactics = s.get('tactics', '')
    skill_req = s.get('skill_req', '')
    enemies = s.get('enemies', '')
    
    # 过滤备忘文本
    if any(k in st_title for k in ['之前把', '之前给', '注意事项', '挂上CT']) or len(tactics) < 15:
        continue
        
    # 标题映射
    for k, v in stage_title_map.items():
        st_title = st_title.replace(k, v)
        
    # 繁简转换
    for k, v in s_map.items():
        st_title = st_title.replace(k, v)
        skill_req = skill_req.replace(k, v)
        enemies = enemies.replace(k, v)
        tactics = tactics.replace(k, v)
        
    # 叠字修正
    for k, v in cleanups:
        st_title = st_title.replace(k, v)
        skill_req = skill_req.replace(k, v)
        enemies = enemies.replace(k, v)
        tactics = tactics.replace(k, v)
        
    # 确保假名清除
    st_title = kana_re.sub('', st_title)
    skill_req = kana_re.sub('', skill_req)
    enemies = kana_re.sub('', enemies)
    tactics = kana_re.sub('', tactics)
    
    st_title = re.sub(r'[\-—=\s]+', ' ', st_title).strip()
    skill_req = re.sub(r'\s+', ' ', skill_req).strip()
    enemies = re.sub(r'\s+', ' ', enemies).strip()
    tactics = re.sub(r'\s+', ' ', tactics).strip()
    
    cleaned_stages.append({
        'id': f'stage_{len(cleaned_stages)+1}',
        'part': s['part'],
        'scene': s['scene'],
        'stage_number': s['stage_number'],
        'title': st_title,
        'skill_req': skill_req or '击坠指定头目或达成关卡胜利条件',
        'enemies': enemies,
        'tactics': tactics
    })

print(f'Total clean stages: {len(cleaned_stages)}')

# 检验假名
total_kana = 0
for cs in cleaned_stages:
    for k, v in cs.items():
        m = kana_re.findall(v)
        if m:
            total_kana += len(m)

print(f'Residual kana count: {total_kana}')

with open(stages_path, 'w', encoding='utf-8') as f:
    f.write('window.SRW_STAGES_GUIDE = ' + json.dumps(cleaned_stages, ensure_ascii=False, indent=2) + ';\n')

print('Successfully updated web/data/srworld_stages.js!')
