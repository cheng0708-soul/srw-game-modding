with open('/Volumes/D2T/projects/srw-game-modding/web/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 替换掉 50-63 行的冗余旧代码
old_block = '''  // ==============================================================
  // 2. Navigation smooth scroll & active state
  // ==============================================================
  // navLinks reuse
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      playBeep(659, 'sine', 0.05);
      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');
    });
  });'''

if old_block in text:
    text = text.replace(old_block, '''  // ==============================================================
  // 2. Navigation managed in Module 10 (Tactical Console Engine)
  // ==============================================================
  const navLinks = document.querySelectorAll('.main-nav .nav-link');''')
    print("成功替换旧导航声明！")
else:
    print("警告：未直接匹配，尝试正则替换")

with open('/Volumes/D2T/projects/srw-game-modding/web/js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

