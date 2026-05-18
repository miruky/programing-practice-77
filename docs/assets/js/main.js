// =====================================================================
//  SVG アイコン定義 (build.py 側と同じ Lucide ライクなアウトライン)
// =====================================================================
const SVG_ATTRS = 'class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';
const ICONS = {
  eyeOff: `<svg ${SVG_ATTRS}><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/></svg>`,
  eye: `<svg ${SVG_ATTRS}><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`,
  clipboard: `<svg ${SVG_ATTRS}><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>`,
  check: `<svg ${SVG_ATTRS}><polyline points="20 6 9 17 4 12"/></svg>`,
};

// =====================================================================
//  検索 + 章フィルタ (トップページ用)
// =====================================================================
(function () {
  const searchInput = document.getElementById('search');
  const cards = document.querySelectorAll('.problem-card');
  const filterButtons = document.querySelectorAll('.chapter-filter button');
  const sections = document.querySelectorAll('.chapter-section');

  let activeChapter = 'all';

  function applyFilter() {
    const q = (searchInput && searchInput.value.trim().toLowerCase()) || '';
    cards.forEach(card => {
      const text = card.dataset.search || '';
      const chap = card.dataset.chapter || '';
      const matchesQuery = !q || text.indexOf(q) !== -1;
      const matchesChap = activeChapter === 'all' || activeChapter === chap;
      card.style.display = matchesQuery && matchesChap ? '' : 'none';
    });
    sections.forEach(sec => {
      const visibles = sec.querySelectorAll('.problem-card:not([style*="display: none"])');
      sec.style.display = visibles.length ? '' : 'none';
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', applyFilter);
  }
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeChapter = btn.dataset.chapter || 'all';
      applyFilter();
    });
  });
})();

// =====================================================================
//  コードコピー / コメント表示トグル (問題詳細ページ用)
//  方針: ビルド時にコメント有り版 / 無し版の 2 つの <pre> を生成しておき、
//        ボタンクリックで hidden を切替える。再描画不要で確実に動作。
// =====================================================================
(function () {
  const fullBlock = document.querySelector('.code-block-full');
  const strippedBlock = document.querySelector('.code-block-stripped');
  if (!fullBlock || !strippedBlock) return;
  const explainPanels = document.querySelectorAll('.explain-panel');

  let commentsHidden = true;

  function applyState() {
    fullBlock.hidden = commentsHidden;
    strippedBlock.hidden = !commentsHidden;
    explainPanels.forEach(panel => {
      panel.hidden = commentsHidden;
    });
  }

  // ----- コメント表示トグル -----
  const toggleBtn = document.getElementById('toggle-comments');
  if (toggleBtn) {
    toggleBtn.classList.toggle('active', commentsHidden);
    toggleBtn.addEventListener('click', () => {
      commentsHidden = !commentsHidden;
      const icon = commentsHidden ? ICONS.eye : ICONS.eyeOff;
      const label = commentsHidden ? 'コメントを表示' : 'コメントを非表示';
      toggleBtn.innerHTML = `${icon}<span class="label">${label}</span>`;
      toggleBtn.classList.toggle('active', commentsHidden);
      applyState();
    });
  }
  applyState();

  // ----- コードコピー (現在表示している方をコピー) -----
  const copyBtn = document.getElementById('copy-code');
  if (copyBtn) {
    const defaultHTML = `${ICONS.clipboard}<span class="label">コードをコピー</span>`;
    copyBtn.addEventListener('click', () => {
      const visible = commentsHidden ? strippedBlock : fullBlock;
      const codeEl = visible.querySelector('code');
      if (!codeEl) return;
      const text = codeEl.textContent;
      navigator.clipboard.writeText(text).then(() => {
        copyBtn.innerHTML = `${ICONS.check}<span class="label">コピーしました</span>`;
        copyBtn.classList.add('success');
        setTimeout(() => {
          copyBtn.innerHTML = defaultHTML;
          copyBtn.classList.remove('success');
        }, 1500);
      });
    });
  }
})();
