import re

html_path = "/Volumes/D2T/projects/srw-game-modding/web/index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. 更新 Header 导航与状态栏
old_nav_pattern = r'<nav class="main-nav">.*?</nav>'
new_nav = '''<nav class="main-nav">
        <a href="#secrets" class="nav-link active" data-view="secrets"><span>🛸</span> 隐藏要素</a>
        <a href="#stagesGuide" class="nav-link" data-view="stagesGuide"><span>📖</span> 105关攻略</a>
        <a href="#cheats" class="nav-link" data-view="cheats"><span>⚡</span> 金手指定制</a>
        <a href="#tacticsSection" class="nav-link" data-view="tacticsSection"><span>💥</span> 战术攻防</a>
        <a href="#timeline" class="nav-link" data-view="timeline"><span>📋</span> 历史档案</a>
        <a href="#database" class="nav-link" data-view="database"><span>💾</span> 数据库</a>
      </nav>'''
html = re.sub(old_nav_pattern, new_nav, html, flags=re.DOTALL)

# 更新 header-actions 增加视窗模式切换
old_actions_pattern = r'<div class="header-actions">.*?</div>\s*</div>\s*</header>'
new_actions = '''<div class="header-actions">
        <button id="viewModeToggleBtn" class="btn-icon" title="切换单模块视窗/全页平铺">🎛️ 聚焦视窗: 开</button>
        <button id="soundToggleBtn" class="btn-icon">🔊 战术音效: 开</button>
        <div class="author-pill">
          <span class="author-badge-icon">🎖️</span>
          <span class="author-badge-text">作者: <strong>luke爱分享</strong></span>
        </div>
      </div>
    </div>
    <!-- HUD Tactical Status Bar -->
    <div class="hud-status-strip">
      <div class="container status-strip-inner">
        <div class="status-indicator">
          <span class="status-dot"></span>
          <span class="status-label">TACTICAL CONSOLE:</span>
          <span id="activeViewIndicator" class="status-view-tag">🛸 隐藏要素总装库</span>
        </div>
        <div class="status-quick-pills">
          <button class="quick-pill active" data-target="secrets">🛸 隐藏要素 (32+7)</button>
          <button class="quick-pill" data-target="stagesGuide">📖 105关全攻略</button>
          <button class="quick-pill" data-target="cheats">⚡ 金手指定制</button>
          <button class="quick-pill" data-target="tacticsSection">💥 战术攻防</button>
          <button class="quick-pill" data-target="timeline">📋 历史档案</button>
          <button class="quick-pill" data-target="hero">🏠 指挥室</button>
        </div>
      </div>
    </div>
  </header>'''
html = re.sub(old_actions_pattern, new_actions, html, flags=re.DOTALL)

# 2. 改造 #secrets Section 为多维子Tab架构
old_secrets_pattern = r'<section id="secrets".*?<!-- SECTION 2:'
new_secrets_block = '''<section id="secrets" class="tactical-view-panel" style="padding-top: 32px;">
      <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
        <h2 style="font-family: var(--font-hud); font-size: 1.6rem; color: var(--text-bright); display: flex; align-items: center; gap: 10px;">
          <span style="color: var(--accent-cyan);">§ 01</span> 隐藏要素全维战术总装库
        </h2>
        <span style="font-size: 0.85rem; color: var(--accent-gold); font-family: var(--font-hud);">INTERACTIVE SECRETS LAB · 7 维全域资料</span>
      </div>

      <!-- Sub Tabs Navigation -->
      <div class="secrets-subnav-bar">
        <button class="secrets-sub-btn active" data-sub="radar"><span>🛰️</span> 要素雷达 (32项)</button>
        <button class="secrets-sub-btn" data-sub="matrix"><span>🧭</span> 关键路线决策矩阵</button>
        <button class="secrets-sub-btn" data-sub="containers"><span>📦</span> 隐藏宝箱与集装箱</button>
        <button class="secrets-sub-btn" data-sub="remodels"><span>🔄</span> 机体改造继承</button>
        <button class="secrets-sub-btn" data-sub="cg"><span>🎬</span> 全20项CG与结局</button>
        <button class="secrets-sub-btn" data-sub="checkpoints"><span>📋</span> 关卡进度打卡清单</button>
        <button class="secrets-sub-btn" data-sub="tips"><span>💡</span> 核心秘技与避坑指南</button>
      </div>

      <!-- Sub Panel 1: 原有的要素雷达 (含搜索与卡片) -->
      <div id="subTabRadar" class="secrets-sub-panel active">
        <div class="tactical-controls">
          <div class="filter-pills">
            <button class="filter-btn secret-filter-btn active" data-part="ALL">全部 (32项)</button>
            <button class="filter-btn secret-filter-btn" data-part="P1">第1部 地上/宇宙 (15项)</button>
            <button class="filter-btn secret-filter-btn" data-part="P2">第2部 逆转篇 (5项)</button>
            <button class="filter-btn secret-filter-btn" data-part="P3">第3部 银河篇 (12项)</button>
          </div>

          <div class="search-box">
            <span class="search-icon">🔍</span>
            <input type="text" id="secretSearchInput" class="search-input" placeholder="输入机体/机师/关卡(如东方不败、雪霸)...">
          </div>
        </div>

        <div class="progress-hud">
          <div class="progress-info">
            <span class="progress-title">本周目达成进度:</span>
            <span id="progressCounter" class="progress-counter">0 / 32 (0%)</span>
          </div>
          <div class="progress-track">
            <div id="progressFill" class="progress-fill"></div>
          </div>
          <button id="resetProgressBtn" class="btn-reset-progress">重置进度</button>
        </div>

        <div id="secretsGrid" class="secrets-grid"></div>
      </div>

      <!-- Sub Panel 2: 路线决策矩阵 -->
      <div id="subTabMatrix" class="secrets-sub-panel" style="display: none;">
        <div id="matrixContainer" class="subtab-content-wrap"></div>
      </div>

      <!-- Sub Panel 3: 隐藏宝箱与集装箱 -->
      <div id="subTabContainers" class="secrets-sub-panel" style="display: none;">
        <div id="containersDisplay" class="subtab-content-wrap"></div>
      </div>

      <!-- Sub Panel 4: 机体改造继承 -->
      <div id="subTabRemodels" class="secrets-sub-panel" style="display: none;">
        <div id="remodelsDisplay" class="subtab-content-wrap"></div>
      </div>

      <!-- Sub Panel 5: 全20项CG与结局 -->
      <div id="subTabCG" class="secrets-sub-panel" style="display: none;">
        <div id="cgGalleryDisplay" class="subtab-content-wrap"></div>
      </div>

      <!-- Sub Panel 6: 关卡进度打卡清单 -->
      <div id="subTabCheckpoints" class="secrets-sub-panel" style="display: none;">
        <div id="checkpointsDisplay" class="subtab-content-wrap"></div>
      </div>

      <!-- Sub Panel 7: 核心秘技与避坑指南 -->
      <div id="subTabTips" class="secrets-sub-panel" style="display: none;">
        <div id="tipsDisplay" class="subtab-content-wrap"></div>
      </div>
    </section>

    <!-- SECTION 2:'''
html = re.sub(old_secrets_pattern, new_secrets_block, html, flags=re.DOTALL)

# 3. 为各大主要 section 增加 class="tactical-view-panel"
for sec_id in ['timeline', 'stagesGuide', 'cheats', 'tacticsSection', 'database']:
    html = html.replace(f'<section id="{sec_id}"', f'<section id="{sec_id}" class="tactical-view-panel"')

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("index.html 更新成功！")
