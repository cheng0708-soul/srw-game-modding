/**
 * SUPER ROBOT WARS IMPACT - TACTICAL ARCHIVE
 * Core Interactive Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // ==============================================================
  // 1. Audio Synthesizer (Web Audio API)
  // ==============================================================
  let audioCtx = null;
  let soundEnabled = true;

  function initAudio() {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
  }

  function playBeep(freq = 880, type = 'sine', duration = 0.08, gainVal = 0.05) {
    if (!soundEnabled) return;
    try {
      initAudio();
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {
      // AudioContext unavailable
    }
  }

  const soundToggleBtn = document.getElementById('soundToggleBtn');
  if (soundToggleBtn) {
    soundToggleBtn.addEventListener('click', () => {
      soundEnabled = !soundEnabled;
      soundToggleBtn.innerHTML = soundEnabled ? '🔊 战术音效: 开' : '🔇 战术音效: 关';
      if (soundEnabled) playBeep(987, 'triangle', 0.12, 0.08);
    });
  }

  // ==============================================================
  // 2. Navigation smooth scroll & active state
  // ==============================================================
  // navLinks reuse
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      playBeep(659, 'sine', 0.05);
      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');
    });
  });

  // ==============================================================
  // 3. Section 1: Secrets Matrix (隐藏要素互动雷达)
  // ==============================================================
  const STORAGE_KEY = 'srw_impact_cleared_secrets';
  let clearedSecrets = new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'));

  const secretsGrid = document.getElementById('secretsGrid');
  const secretFilterBtns = document.querySelectorAll('.secret-filter-btn');
  const searchInput = document.getElementById('secretSearchInput');
  const progressFill = document.getElementById('progressFill');
  const progressCounter = document.getElementById('progressCounter');
  const resetProgressBtn = document.getElementById('resetProgressBtn');

  let currentPartFilter = 'ALL';
  let currentSearchQuery = '';

  function updateProgressHUD() {
    const total = (window.SRW_SECRETS || []).length;
    const completed = clearedSecrets.size;
    const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
    if (progressCounter) progressCounter.textContent = `${completed} / ${total} (${pct}%)`;
    if (progressFill) progressFill.style.width = `${pct}%`;
  }

  function renderSecrets() {
    if (!secretsGrid || !window.SRW_SECRETS) return;
    secretsGrid.innerHTML = '';

    const filtered = window.SRW_SECRETS.filter(item => {
      const matchPart = (currentPartFilter === 'ALL') || 
                        (currentPartFilter === 'P1' && item.part.includes('第1部')) ||
                        (currentPartFilter === 'P2' && item.part.includes('第2部')) ||
                        (currentPartFilter === 'P3' && item.part.includes('第3部'));
      
      const q = currentSearchQuery.toLowerCase();
      const matchQuery = !q || 
                         item.title.toLowerCase().includes(q) || 
                         item.condition.toLowerCase().includes(q) ||
                         (item.stages && item.stages.some(s => s.toLowerCase().includes(q)));
      return matchPart && matchQuery;
    });

    if (filtered.length === 0) {
      secretsGrid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 48px; color: var(--text-muted); font-family: var(--font-hud);">
          [ ⚠️ 未检测到符合条件的战术隐藏要素 ]
        </div>
      `;
      return;
    }

    filtered.forEach(item => {
      const isCompleted = clearedSecrets.has(item.id);
      const card = document.createElement('div');
      card.className = `secret-card ${isCompleted ? 'completed' : ''}`;
      card.id = `card_${item.id}`;

      const stagesHtml = (item.stages || []).map(st => `<span class="stage-badge">🚩 ${st}</span>`).join('');

      card.innerHTML = `
        <div class="secret-card-header">
          <img src="assets/images/${item.image}" alt="${item.title}" class="secret-mecha-avatar" onerror="this.src='assets/images/srw_tactical_insignia.jpg'">
          <div class="secret-header-meta">
            <div class="secret-part-tag">${item.part} · NO.${item.id.replace('sec_', '')}</div>
            <h3 class="secret-title">${item.title}</h3>
          </div>
        </div>
        <div class="secret-stages">${stagesHtml}</div>
        <div class="secret-condition-box">${item.condition}</div>
        <div class="secret-card-footer">
          <label class="checkbox-label">
            <input type="checkbox" data-id="${item.id}" ${isCompleted ? 'checked' : ''}>
            <span>${isCompleted ? '✓ 本轮已达成' : '标记已入手'}</span>
          </label>
        </div>
      `;

      const cb = card.querySelector('input[type="checkbox"]');
      cb.addEventListener('change', (e) => {
        playBeep(isCompleted ? 440 : 1320, 'triangle', 0.1, 0.08);
        if (e.target.checked) {
          clearedSecrets.add(item.id);
          card.classList.add('completed');
          cb.nextElementSibling.textContent = '✓ 本轮已达成';
        } else {
          clearedSecrets.delete(item.id);
          card.classList.remove('completed');
          cb.nextElementSibling.textContent = '标记已入手';
        }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(clearedSecrets)));
        updateProgressHUD();
      });

      secretsGrid.appendChild(card);
    });

    updateProgressHUD();
  }

  secretFilterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      playBeep(659, 'sine', 0.06);
      secretFilterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentPartFilter = btn.dataset.part;
      renderSecrets();
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearchQuery = e.target.value.trim();
      renderSecrets();
    });
  }

  if (resetProgressBtn) {
    resetProgressBtn.addEventListener('click', () => {
      if (confirm('确定要重置当前保存在本机的隐藏要素达成记录吗？')) {
        clearedSecrets.clear();
        localStorage.removeItem(STORAGE_KEY);
        playBeep(330, 'square', 0.2);
        renderSecrets();
      }
    });
  }

  // ==============================================================
  // 4. Section 2: Timeline Stages (判定关卡速查表)
  // ==============================================================
  const timelineTabs = document.querySelectorAll('.timeline-tab:not(.tactic-tab):not(.db-tab)');
  const timelineTableBody = document.getElementById('timelineTableBody');

  function renderTimeline(part) {
    if (!timelineTableBody || !window.SRW_TIMELINE) return;
    const rows = window.SRW_TIMELINE[part] || [];
    timelineTableBody.innerHTML = '';

    rows.forEach(r => {
      const tr = document.createElement('tr');
      const stage = r['关卡'] || r['关卡／事件'] || r['stage'] || Object.values(r)[0] || '';
      const action = r['关键动作（做错不可逆）'] || r['要素'] || r['判定要点'] || r['req'] || Object.values(r)[1] || '';
      const target = r['涉及要素'] || r['条件'] || Object.values(r)[2] || '';

      tr.innerHTML = `
        <td style="font-weight: 700; color: var(--accent-cyan); white-space: nowrap;">${stage}</td>
        <td>${action}</td>
        <td><span style="color: var(--accent-amber);">${target}</span></td>
      `;
      timelineTableBody.appendChild(tr);
    });
  }

  timelineTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      playBeep(700, 'sine', 0.05);
      timelineTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      renderTimeline(tab.dataset.part);
    });
  });

  // ==============================================================
  // 5. Section 3: 105 Stages Walkthrough Guide (全流程战术攻防手册)
  // ==============================================================
  const stagePartBtns = document.querySelectorAll('.stage-part-btn');
  const stageListDisplay = document.getElementById('stageListDisplay');
  const stageSearchInput = document.getElementById('stageSearchInput');
  let currentStagePart = '第1部 地上篇';
  let stageSearchQuery = '';

  function renderStagesGuide() {
    if (!stageListDisplay || !window.SRW_STAGES_GUIDE) return;
    stageListDisplay.innerHTML = '';

    const q = stageSearchQuery.toLowerCase();
    const filtered = window.SRW_STAGES_GUIDE.filter(st => {
      const matchPart = !currentStagePart || st.part === currentStagePart;
      const matchQ = !q || 
                     st.title.toLowerCase().includes(q) || 
                     st.skill_req.toLowerCase().includes(q) || 
                     st.scene.toLowerCase().includes(q) ||
                     st.tactics.toLowerCase().includes(q);
      return matchPart && matchQ;
    });

    if (filtered.length === 0) {
      stageListDisplay.innerHTML = `
        <div style="text-align: center; padding: 48px; color: var(--text-muted); font-family: var(--font-hud);">
          [ ⚠️ 未检测到符合条件的战术关卡攻略 ]
        </div>
      `;
      return;
    }

    filtered.forEach(st => {
      const card = document.createElement('div');
      card.className = 'stage-walkthrough-card';
      card.innerHTML = `
        <div class="stage-wt-header">
          <div class="stage-wt-badge">${st.part} · ${st.scene}</div>
          <h3 class="stage-wt-title">${st.stage_number} ${st.title}</h3>
        </div>
        <div class="stage-wt-body">
          <div class="stage-wt-skill">
            <span class="skill-label">⭐ 熟练度判定条件:</span>
            <span class="skill-content">${st.skill_req}</span>
          </div>
          ${st.enemies ? `
          <div class="stage-wt-enemies">
            <span class="enemy-label">⚔️ 敌方初期配置:</span>
            <span class="enemy-content">${st.enemies}</span>
          </div>` : ''}
          <div class="stage-wt-tactics">
            <span class="tactics-label">💡 战术作战指导:</span>
            <p class="tactics-content">${st.tactics}</p>
          </div>
        </div>
      `;
      stageListDisplay.appendChild(card);
    });
  }

  stagePartBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      playBeep(650, 'triangle', 0.05);
      stagePartBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentStagePart = btn.dataset.part;
      renderStagesGuide();
    });
  });

  if (stageSearchInput) {
    stageSearchInput.addEventListener('input', (e) => {
      stageSearchQuery = e.target.value.trim();
      renderStagesGuide();
    });
  }

  // ==============================================================
  // 6. Section 4: Cheats Workbench (金手指在线工作台)
  // ==============================================================
  const cheatListEl = document.getElementById('cheatList');
  const codeDisplayEl = document.getElementById('codeDisplay');
  const cheatCategoryBtns = document.querySelectorAll('.cheat-cat-btn');
  const cheatSearchInput = document.getElementById('cheatSearchInput');
  const btnSelectAll = document.getElementById('btnSelectAll');
  const btnDeselectAll = document.getElementById('btnDeselectAll');
  const btnSelectPart1 = document.getElementById('btnSelectPart1');
  const btnSelectPart2 = document.getElementById('btnSelectPart2');
  const btnSelectPart3 = document.getElementById('btnSelectPart3');
  const btnCopyPnach = document.getElementById('btnCopyPnach');
  const btnDownloadPnach = document.getElementById('btnDownloadPnach');
  const selectedCheatsCountEl = document.getElementById('selectedCheatsCount');

  let activeCheatCat = 'ALL';
  let cheatSearchQuery = '';
  let enabledCheats = new Set();

  (window.SRW_CHEATS || []).forEach(c => {
    if (c.default_enabled) enabledCheats.add(c.id);
  });

  function generatePnachContent() {
    let out = `gametitle=SUPER ROBOT WARS IMPACT (WGF汉化版) [SLPS-25104] [10C3D363]\n`;
    out += `// ============================================================\n`;
    out += `// 由 SRW IMPACT 战术整备室在线定制导出\n`;
    out += `// 适用: PCSX2 模拟器 cheats 目录 (SLPS-25104_10C3D363.pnach)\n`;
    out += `// 当前启用补丁条数: ${enabledCheats.size} 项\n`;
    out += `// 注意: 标有 ·第1部/·第2部/·第3部 的条目, 只勾选你当前所在部的版本\n`;
    out += `// ============================================================\n\n`;

    (window.SRW_CHEATS || []).forEach(c => {
      if (enabledCheats.has(c.id)) {
        out += `[${c.title}]\n`;
        out += `description=${c.description}\n`;
        c.patches.forEach(p => {
          out += `${p}\n`;
        });
        if (c.raw_code) out += `// 原码: ${c.raw_code}\n`;
        out += `\n`;
      }
    });

    return out;
  }

  function updateCodePreview() {
    if (!codeDisplayEl) return;
    const content = generatePnachContent();
    codeDisplayEl.textContent = content;
    if (selectedCheatsCountEl) {
      selectedCheatsCountEl.textContent = `${enabledCheats.size} 项已激活`;
    }
  }

  function renderCheats() {
    if (!cheatListEl || !window.SRW_CHEATS) return;
    cheatListEl.innerHTML = '';

    const filtered = window.SRW_CHEATS.filter(c => {
      const matchCat = (activeCheatCat === 'ALL') || (c.category === activeCheatCat);
      const q = cheatSearchQuery.toLowerCase();
      const matchQuery = !q || c.title.toLowerCase().includes(q) || c.description.toLowerCase().includes(q);
      return matchCat && matchQuery;
    });

    filtered.forEach(c => {
      const isChecked = enabledCheats.has(c.id);
      const itemEl = document.createElement('div');
      itemEl.className = `cheat-item ${isChecked ? 'checked' : ''}`;
      itemEl.innerHTML = `
        <div class="cheat-item-main">
          <input type="checkbox" ${isChecked ? 'checked' : ''}>
          <div>
            <div class="cheat-item-title">${c.title}</div>
            <div class="cheat-item-desc">${c.description}</div>
          </div>
        </div>
        <span class="cheat-item-badge">${c.category}</span>
      `;

      itemEl.addEventListener('click', () => {
        playBeep(isChecked ? 550 : 880, 'sine', 0.05);
        if (enabledCheats.has(c.id)) {
          enabledCheats.delete(c.id);
          itemEl.classList.remove('checked');
          itemEl.querySelector('input').checked = false;
        } else {
          enabledCheats.add(c.id);
          itemEl.classList.add('checked');
          itemEl.querySelector('input').checked = true;
        }
        updateCodePreview();
      });

      cheatListEl.appendChild(itemEl);
    });

    updateCodePreview();
  }

  cheatCategoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      playBeep(659, 'sine', 0.06);
      cheatCategoryBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCheatCat = btn.dataset.cat;
      renderCheats();
    });
  });

  if (cheatSearchInput) {
    cheatSearchInput.addEventListener('input', (e) => {
      cheatSearchQuery = e.target.value.trim();
      renderCheats();
    });
  }

  if (btnSelectAll) {
    btnSelectAll.addEventListener('click', () => {
      playBeep(1000, 'triangle', 0.08);
      (window.SRW_CHEATS || []).forEach(c => enabledCheats.add(c.id));
      renderCheats();
    });
  }

  if (btnDeselectAll) {
    btnDeselectAll.addEventListener('click', () => {
      playBeep(400, 'triangle', 0.08);
      enabledCheats.clear();
      renderCheats();
    });
  }

  [[btnSelectPart1, '·第1部'], [btnSelectPart2, '·第2部'], [btnSelectPart3, '·第3部']].forEach(([btn, tag]) => {
    if (btn) {
      btn.addEventListener('click', () => {
        playBeep(880, 'triangle', 0.1);
        enabledCheats.clear();
        (window.SRW_CHEATS || []).forEach(c => {
          if (c.pack === 'fix' && c.title.endsWith(tag)) enabledCheats.add(c.id);
        });
        renderCheats();
      });
    }
  });

  if (btnCopyPnach) {
    btnCopyPnach.addEventListener('click', () => {
      const code = generatePnachContent();
      navigator.clipboard.writeText(code).then(() => {
        playBeep(1200, 'square', 0.15);
        const originalText = btnCopyPnach.innerHTML;
        btnCopyPnach.innerHTML = '✓ 代码已复制！';
        setTimeout(() => {
          btnCopyPnach.innerHTML = originalText;
        }, 2000);
      });
    });
  }

  if (btnDownloadPnach) {
    btnDownloadPnach.addEventListener('click', () => {
      playBeep(1500, 'sine', 0.2);
      const code = generatePnachContent();
      const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'SLPS-25104_10C3D363.pnach';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // ==============================================================
  // 7. Section 5: Tactics & Combos (合体技与精神全集)
  // ==============================================================
  const tacticTabs = document.querySelectorAll('.tactic-tab');
  const tacticDisplay = document.getElementById('tacticDisplay');
  const tacticSearchInput = document.getElementById('tacticSearchInput');
  let currentTacticType = 'combos';
  let tacticSearchQuery = '';

  function renderTactics() {
    if (!tacticDisplay || !window.SRW_SRWORLD_TACTICS) return;
    const data = window.SRW_SRWORLD_TACTICS[currentTacticType] || [];
    tacticDisplay.innerHTML = '';

    const q = tacticSearchQuery.toLowerCase();
    const filtered = data.filter(item => {
      const textAll = Object.values(item).join(' ').toLowerCase();
      return !q || textAll.includes(q);
    });

    if (filtered.length === 0) {
      tacticDisplay.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 36px; color: var(--text-muted); font-family: var(--font-hud);">
          [ ⚠️ 未检测到符合条件的战术数据 ]
        </div>
      `;
      return;
    }

    if (currentTacticType === 'combos') {
      tacticDisplay.className = 'tactics-grid';
      filtered.forEach(c => {
        const card = document.createElement('div');
        card.className = 'combo-card';
        card.innerHTML = `
          <div class="combo-card-header">
            <span class="combo-title">${c.name}</span>
            <span class="combo-power">💥 ${c.power}</span>
          </div>
          <div class="combo-meta">
            <div><strong style="color: var(--accent-cyan);">参与机体:</strong> ${c.mecha}</div>
            <div style="display: flex; gap: 14px; margin-top: 4px;">
              <span><strong>消耗:</strong> <span style="color: var(--accent-amber);">${c.req}</span></span>
              <span><strong>射程:</strong> ${c.range}</span>
            </div>
          </div>
          <div class="combo-desc">${c.desc}</div>
        `;
        tacticDisplay.appendChild(card);
      });
    } else {
      tacticDisplay.className = 'timeline-table-wrap';
      const table = document.createElement('table');
      table.className = 'tactical-table';
      
      let thead = '<thead><tr>';
      if (currentTacticType === 'spirits') {
        thead += '<th>精神名称</th><th style="width: 100px;">SP 消耗</th><th>效果说明与战术评价</th>';
      } else if (currentTacticType === 'items') {
        thead += '<th>强化芯片 / 道具名称</th><th style="width: 140px;">类别</th><th>效果说明</th>';
      } else {
        thead += '<th style="width: 200px;">机体 / 机师技能</th><th>效果说明与计算公式</th>';
      }
      thead += '</tr></thead>';

      let tbody = '<tbody>';
      filtered.forEach(item => {
        tbody += '<tr>';
        if (currentTacticType === 'spirits') {
          tbody += `<td style="font-weight: 700; color: var(--accent-gold);">${item.name}</td>`;
          tbody += `<td style="font-family: var(--font-hud); color: var(--accent-cyan); font-weight: 800;">${item.sp}</td>`;
          tbody += `<td>${item.desc}</td>`;
        } else if (currentTacticType === 'items') {
          tbody += `<td style="font-weight: 700; color: var(--accent-cyan);">${item.name}</td>`;
          tbody += `<td><span class="stage-badge">${item.category}</span></td>`;
          tbody += `<td>${item.desc}</td>`;
        } else {
          tbody += `<td style="font-weight: 700; color: var(--accent-amber);">${item.name}</td>`;
          tbody += `<td>${item.desc}</td>`;
        }
        tbody += '</tr>';
      });
      tbody += '</tbody>';

      table.innerHTML = thead + tbody;
      tacticDisplay.appendChild(table);
    }
  }

  tacticTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      playBeep(700, 'sine', 0.05);
      tacticTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentTacticType = tab.dataset.type;
      renderTactics();
    });
  });

  if (tacticSearchInput) {
    tacticSearchInput.addEventListener('input', (e) => {
      tacticSearchQuery = e.target.value.trim();
      renderTactics();
    });
  }

  // ==============================================================
  // 8. Section 6: Database (Extras) Tabs
  // ==============================================================
  const dbTabs = document.querySelectorAll('.db-tab');
  const dbTableHead = document.getElementById('dbTableHead');
  const dbTableBody = document.getElementById('dbTableBody');

  function renderDatabase(type) {
    if (!dbTableHead || !dbTableBody || !window.SRW_EXTRAS) return;
    dbTableHead.innerHTML = '';
    dbTableBody.innerHTML = '';

    const list = window.SRW_EXTRAS[type] || [];
    if (list.length === 0) return;

    const keys = Object.keys(list[0]);
    const trHead = document.createElement('tr');
    keys.forEach(k => {
      const th = document.createElement('th');
      th.textContent = k;
      trHead.appendChild(th);
    });
    dbTableHead.appendChild(trHead);

    list.forEach(item => {
      const tr = document.createElement('tr');
      keys.forEach(k => {
        const td = document.createElement('td');
        td.innerHTML = item[k];
        tr.appendChild(td);
      });
      dbTableBody.appendChild(tr);
    });
  }

  dbTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      playBeep(700, 'sine', 0.05);
      dbTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      renderDatabase(tab.dataset.type);
    });
  });

  // ==============================================================
  // 9. Initial Renders for all components
  // ==============================================================
  renderSecrets();
  renderTimeline('第1部');
  renderStagesGuide();
  renderCheats();
  renderTactics();
  renderDatabase('inheritances');


  // ==============================================================
  // 10. TACTICAL MULTI-VIEW CONSOLE & SECRETS SUB-TABS (v2.5)
  // ==============================================================

  // 10.1 聚焦工作台视窗调度器
  let isFocusedViewMode = true; // 默认开启单模块聚焦模式，告别漫长翻滚
  let currentActiveView = 'secrets'; // 默认进入隐藏要素总装库

  const viewNames = {
    'hero': '🏠 指挥室总览',
    'secrets': '🛸 隐藏要素总装库',
    'stagesGuide': '📖 105关全流程攻略',
    'cheats': '⚡ 金手指战术工坊',
    'tacticsSection': '💥 战术攻防手册',
    'timeline': '📋 历史档案速查',
    'database': '💾 机体与资料库'
  };

  const allPanels = document.querySelectorAll('.tactical-view-panel, #hero');
  // navLinks reuse
  const quickPills = document.querySelectorAll('.quick-pill');
  const activeViewIndicator = document.getElementById('activeViewIndicator');
  const viewModeToggleBtn = document.getElementById('viewModeToggleBtn');

  function switchTacticalView(viewId, smoothScroll = true) {
    if (!viewId) return;
    currentActiveView = viewId;

    if (activeViewIndicator && viewNames[viewId]) {
      activeViewIndicator.textContent = viewNames[viewId];
    }

    // 更新导航高亮
    navLinks.forEach(link => {
      const href = link.getAttribute('href') ? link.getAttribute('href').replace('#', '') : '';
      const dataView = link.dataset.view;
      if (href === viewId || dataView === viewId) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    quickPills.forEach(pill => {
      if (pill.dataset.target === viewId) {
        pill.classList.add('active');
      } else {
        pill.classList.remove('active');
      }
    });

    // 聚焦模式下：仅展示当前视窗；平铺模式下：展示全部并滚动
    if (isFocusedViewMode) {
      allPanels.forEach(p => {
        if (p.id === viewId) {
          p.style.display = 'block';
          p.style.animation = 'hudPanelFadeIn 0.35s ease-out';
        } else {
          p.style.display = 'none';
        }
      });
      if (smoothScroll) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } else {
      allPanels.forEach(p => {
        p.style.display = 'block';
      });
      const targetElem = document.getElementById(viewId);
      if (targetElem && smoothScroll) {
        targetElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }

  // 绑定主导航与快捷药丸按钮
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const targetId = link.getAttribute('href').replace('#', '');
      playBeep(850, 'sine', 0.04);
      switchTacticalView(targetId);
    });
  });

  quickPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const targetId = pill.dataset.target;
      playBeep(850, 'sine', 0.04);
      switchTacticalView(targetId);
      // 同步 URL hash
      history.replaceState(null, null, '#' + targetId);
    });
  });

  // 模式切换按钮（聚焦视窗 / 全页平铺）
  if (viewModeToggleBtn) {
    viewModeToggleBtn.addEventListener('click', () => {
      isFocusedViewMode = !isFocusedViewMode;
      playBeep(1000, 'square', 0.05);
      if (isFocusedViewMode) {
        viewModeToggleBtn.textContent = '🎛️ 聚焦视窗: 开';
        viewModeToggleBtn.classList.remove('btn-secondary');
        switchTacticalView(currentActiveView);
      } else {
        viewModeToggleBtn.textContent = '📜 全页平铺: 开';
        viewModeToggleBtn.classList.add('btn-secondary');
        allPanels.forEach(p => p.style.display = 'block');
      }
    });
  }

  // 监听 URL Hash 变化实现直接路由访问
  window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById(hash)) {
      switchTacticalView(hash, false);
    }
  });

  // 10.2 隐藏要素 7 大子 Tab 渲染与交互
  const subNavBtns = document.querySelectorAll('.secrets-sub-btn');
  const subPanels = {
    'radar': document.getElementById('subTabRadar'),
    'matrix': document.getElementById('subTabMatrix'),
    'containers': document.getElementById('subTabContainers'),
    'remodels': document.getElementById('subTabRemodels'),
    'cg': document.getElementById('subTabCG'),
    'checkpoints': document.getElementById('subTabCheckpoints'),
    'tips': document.getElementById('subTabTips')
  };

  function switchSecretsSubTab(subKey) {
    subNavBtns.forEach(btn => {
      if (btn.dataset.sub === subKey) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    Object.keys(subPanels).forEach(key => {
      if (subPanels[key]) {
        if (key === subKey) {
          subPanels[key].style.display = 'block';
        } else {
          subPanels[key].style.display = 'none';
        }
      }
    });
  }

  subNavBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      playBeep(750, 'sine', 0.04);
      switchSecretsSubTab(btn.dataset.sub);
    });
  });

  // 渲染 路线决策矩阵
  function renderRouteMatrix() {
    const container = document.getElementById('matrixContainer');
    if (!container || !window.SRW_ROUTE_BRANCHES) return;
    container.innerHTML = '';

    window.SRW_ROUTE_BRANCHES.forEach(mat => {
      const card = document.createElement('div');
      card.className = 'hud-table-card';

      let tableHtml = `
        <div class="hud-table-header">
          <div>
            <div class="hud-table-title">${mat.title}</div>
            <div class="hud-table-subtitle">${mat.subtitle}</div>
          </div>
        </div>
        <div class="hud-table-desc">${mat.desc}</div>
        <div style="overflow-x: auto;">
          <table class="hud-data-table">
            <thead>
              <tr>${mat.headers.map(h => `<th>${h}</th>`).join('')}</tr>
            </thead>
            <tbody>
              ${mat.rows.map(row => `
                <tr class="${row.some(c => c.includes('★') || c.includes('★★★★★')) ? 'highlight-row' : ''}">
                  ${row.map(cell => `<td>${cell}</td>`).join('')}
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
        <div class="hud-table-notes">
          ${mat.notes.map(n => `<div>📌 ${n}</div>`).join('')}
        </div>
      `;
      card.innerHTML = tableHtml;
      container.appendChild(card);
    });
  }

  // 渲染 隐藏宝箱与集装箱
  function renderContainers() {
    const container = document.getElementById('containersDisplay');
    if (!container || !window.SRW_CONTAINERS) return;
    container.innerHTML = '';

    const card = document.createElement('div');
    card.className = 'hud-table-card';
    card.innerHTML = `
      <div class="hud-table-header">
        <div>
          <div class="hud-table-title">全 13 处隐藏密室宝箱与 BOSS 掉落机体零件全览</div>
          <div class="hud-table-subtitle">含破墙密室探索 / 熟练度判定掉落 / 强力隐藏机体</div>
        </div>
      </div>
      <div style="overflow-x: auto;">
        <table class="hud-data-table">
          <thead>
            <tr>
              <th>出现关卡</th>
              <th>位置与探索方式</th>
              <th>获得机体 / 强化零件 / 资金奖励</th>
              <th>获取类型</th>
            </tr>
          </thead>
          <tbody>
            ${window.SRW_CONTAINERS.map(item => `
              <tr>
                <td style="font-weight: 700; color: var(--accent-gold);">${item.stage}</td>
                <td>${item.location}</td>
                <td style="color: var(--accent-cyan); font-weight: 600;">${item.content}</td>
                <td><span style="background: rgba(0,240,255,0.1); border: 1px solid rgba(0,240,255,0.3); padding: 2px 6px; border-radius: 2px; font-size: 0.8rem;">${item.type}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
    container.appendChild(card);
  }

  // 渲染 机体改造继承
  function renderRemodels() {
    const container = document.getElementById('remodelsDisplay');
    if (!container || !window.SRW_REMODEL_INHERIT) return;
    container.innerHTML = '';

    const card = document.createElement('div');
    card.className = 'hud-table-card';
    card.innerHTML = `
      <div class="hud-table-header">
        <div>
          <div class="hud-table-title">7 大主力机体改造继承全览（换代不亏钱）</div>
          <div class="hud-table-subtitle">机体段数 100% 沿用 · 前期投资满改安心打法</div>
        </div>
      </div>
      <div style="overflow-x: auto;">
        <table class="hud-data-table">
          <thead>
            <tr>
              <th>改造前原型机</th>
              <th>换代继承机体</th>
              <th>继承发生时点</th>
              <th>战略价值与注意事项</th>
            </tr>
          </thead>
          <tbody>
            ${window.SRW_REMODEL_INHERIT.map(item => `
              <tr>
                <td style="font-weight: 700; color: #ff99aa;">${item.before}</td>
                <td style="font-weight: 800; color: var(--accent-cyan);">➔ ${item.after}</td>
                <td style="color: var(--accent-gold); font-family: var(--font-hud);">${item.timing}</td>
                <td>${item.note}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
    container.appendChild(card);
  }

  // 渲染 全 20 项 CG 收集
  function renderCGGallery() {
    const container = document.getElementById('cgGalleryDisplay');
    if (!container || !window.SRW_CG_GALLERY) return;
    container.innerHTML = '';

    const grid = document.createElement('div');
    grid.className = 'cg-grid';

    window.SRW_CG_GALLERY.forEach(item => {
      const card = document.createElement('div');
      card.className = 'cg-card';
      card.innerHTML = `
        <div class="cg-name">🎬 ${item.name}</div>
        <div class="cg-cond"><strong>达成时机与条件:</strong> ${item.condition}</div>
      `;
      grid.appendChild(card);
    });

    container.appendChild(grid);
  }

  // 渲染 剧情关卡打卡清单
  function renderCheckpoints() {
    const container = document.getElementById('checkpointsDisplay');
    if (!container || !window.SRW_CHECKPOINTS) return;
    container.innerHTML = '';

    const savedCheckpoints = JSON.parse(localStorage.getItem('srw_checkpoints_cleared') || '{}');

    window.SRW_CHECKPOINTS.forEach((partGroup, partIdx) => {
      const partCard = document.createElement('div');
      partCard.className = 'checkpoint-part-card';

      let itemsHtml = partGroup.items.map((item, itemIdx) => {
        const itemKey = `chk_${partIdx}_${itemIdx}`;
        const isChecked = savedCheckpoints[itemKey] ? 'checked' : '';
        return `
          <div class="checkpoint-item">
            <input type="checkbox" class="checkpoint-checkbox" data-key="${itemKey}" ${isChecked}>
            <div class="checkpoint-stage-badge">${item.stage}</div>
            <div class="checkpoint-action">${item.action}</div>
          </div>
        `;
      }).join('');

      partCard.innerHTML = `
        <div class="checkpoint-part-title">⚔️ ${partGroup.part} 关键判定打卡</div>
        <div class="checkpoint-list">${itemsHtml}</div>
      `;
      container.appendChild(partCard);
    });

    // 绑定 Checkbox 点击
    container.querySelectorAll('.checkpoint-checkbox').forEach(cb => {
      cb.addEventListener('change', (e) => {
        playBeep(900, 'sine', 0.03);
        const key = e.target.dataset.key;
        savedCheckpoints[key] = e.target.checked;
        localStorage.setItem('srw_checkpoints_cleared', JSON.stringify(savedCheckpoints));
      });
    });
  }

  // 渲染 避坑与秘技
  function renderTips() {
    const container = document.getElementById('tipsDisplay');
    if (!container || !window.SRW_TIPS_GUIDE) return;
    container.innerHTML = '';

    window.SRW_TIPS_GUIDE.forEach(tip => {
      const card = document.createElement('div');
      card.className = 'tip-hud-card';
      card.innerHTML = `
        <div class="tip-hud-title">
          <span>⚠️ ${tip.title}</span>
          <span class="tip-hud-tag">${tip.tag}</span>
        </div>
        <div class="tip-hud-content">${tip.content}</div>
      `;
      container.appendChild(card);
    });
  }

  // 渲染所有子板块
  renderRouteMatrix();
  renderContainers();
  renderRemodels();
  renderCGGallery();
  renderCheckpoints();
  renderTips();

  // 根据当前 URL Hash 初始化视图
  const initHash = window.location.hash.replace('#', '');
  if (initHash && document.getElementById(initHash)) {
    switchTacticalView(initHash, false);
  } else {
    switchTacticalView('secrets', false);
  }

});
