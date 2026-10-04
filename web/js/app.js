/**
 * SUPER ROBOT WARS IMPACT - TACTICAL ARCHIVE
 * Core Interactive Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Audio Synthesizer (Web Audio API)
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

  // 2. State & Storage
  const STORAGE_KEY = 'srw_impact_cleared_secrets';
  let clearedSecrets = new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'));

  // 3. Render Secrets
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

      // Checkbox listener
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

  // Filter Button Events
  secretFilterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      playBeep(659, 'sine', 0.06);
      secretFilterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentPartFilter = btn.dataset.part;
      renderSecrets();
    });
  });

  // Search Event
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearchQuery = e.target.value.trim();
      renderSecrets();
    });
  }

  // Reset Progress
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

  // 4. Cheats Workbench Logic
  const cheatListEl = document.getElementById('cheatList');
  const codeDisplayEl = document.getElementById('codeDisplay');
  const cheatCategoryBtns = document.querySelectorAll('.cheat-cat-btn');
  const cheatSearchInput = document.getElementById('cheatSearchInput');
  const btnSelectAll = document.getElementById('btnSelectAll');
  const btnDeselectAll = document.getElementById('btnDeselectAll');
  const btnSelectRecommended = document.getElementById('btnSelectRecommended');
  const btnCopyPnach = document.getElementById('btnCopyPnach');
  const btnDownloadPnach = document.getElementById('btnDownloadPnach');
  const selectedCheatsCountEl = document.getElementById('selectedCheatsCount');

  let activeCheatCat = 'ALL';
  let cheatSearchQuery = '';
  let enabledCheats = new Set();

  // Initialize default enabled
  (window.SRW_CHEATS || []).forEach(c => {
    if (c.default_enabled) enabledCheats.add(c.id);
  });

  function generatePnachContent() {
    let out = `gametitle=SUPER ROBOT WARS IMPACT (WGF汉化版) [SLPS-25104] [10C3D363]\n`;
    out += `// ============================================================\n`;
    out += `// 由 SRW IMPACT 战术整备室在线定制导出\n`;
    out += `// 适用: PCSX2 模拟器 cheats 目录 (SLPS-25104_10C3D363.pnach)\n`;
    out += `// 当前启用补丁条数: ${enabledCheats.size} 项\n`;
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

      itemEl.addEventListener('click', (e) => {
        // Toggle
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

  // Cheat Categories
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

  if (btnSelectRecommended) {
    btnSelectRecommended.addEventListener('click', () => {
      playBeep(880, 'triangle', 0.1);
      enabledCheats.clear();
      (window.SRW_CHEATS || []).forEach(c => {
        if (c.default_enabled) enabledCheats.add(c.id);
      });
      renderCheats();
    });
  }

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

  // 5. Timeline Tabs
  const timelineTabs = document.querySelectorAll('.timeline-tab');
  const timelineTableBody = document.getElementById('timelineTableBody');

  function renderTimeline(part) {
    if (!timelineTableBody || !window.SRW_TIMELINE) return;
    const rows = window.SRW_TIMELINE[part] || [];
    timelineTableBody.innerHTML = '';

    rows.forEach(r => {
      const tr = document.createElement('tr');
      // Look for keys
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

  // 6. Database (Extras) Tabs
  const dbTabs = document.querySelectorAll('.db-tab');
  const dbTableHead = document.getElementById('dbTableHead');
  const dbTableBody = document.getElementById('dbTableBody');

  function renderDatabase(type) {
    if (!dbTableHead || !dbTableBody || !window.SRW_EXTRAS) return;
    dbTableHead.innerHTML = '';
    dbTableBody.innerHTML = '';

    const list = window.SRW_EXTRAS[type] || [];
    if (list.length === 0) return;

    // Build headers from first item keys
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

  // Initial Runs
  renderSecrets();
  renderCheats();
  renderTimeline('第1部');
  renderDatabase('inheritances');
});

  // ==============================================================
  // 7. SRWorld Tactics (Combos, Spirits, Items, Abilities)
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
      // Combos Grid Cards
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
      // Table view for Spirits, Items, Skills
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
  // 8. 105 Stages Walkthrough Guide
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

  // Initial render of new sections
  renderTactics();
  renderStagesGuide();
