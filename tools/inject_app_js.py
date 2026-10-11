import re

app_path = "/Volumes/D2T/projects/srw-game-modding/web/js/app.js"
with open(app_path, "r", encoding="utf-8") as f:
    code = f.read()

# 准备新逻辑注入
inject_code = '''
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
  const navLinks = document.querySelectorAll('.main-nav .nav-link');
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
'''

# 替换最后的代码块
target_str = "renderDatabase('inheritances');\n});"
if target_str in code:
    code = code.replace(target_str, f"renderDatabase('inheritances');\n\n{inject_code}\n}});")
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("app.js 注入成功！")
else:
    print("未找到注入锚点，请检查")
