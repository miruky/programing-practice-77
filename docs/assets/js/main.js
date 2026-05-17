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
//  コードコピー / コメントトグル (問題詳細ページ用)
// =====================================================================
(function () {
  const codeEl = document.querySelector('pre[class*="language-"] code');
  if (!codeEl) return;

  // 初期コード (Prism がハイライト後でも textContent は元のコードを返す)
  const originalCode = codeEl.textContent.replace(/\s+$/, '');
  let commentsHidden = false;

  // # コメントを除去 (純コメント行は削除、行末コメントは切り詰め)
  function stripComments(code) {
    const lines = code.split('\n');
    const out = [];
    for (const line of lines) {
      if (/^\s*#/.test(line)) {
        continue; // 純コメント行は丸ごと削除
      }
      const idx = line.indexOf('#');
      if (idx === -1) {
        out.push(line);
      } else {
        // 行末コメントを削り、末尾の空白も除去
        out.push(line.substring(0, idx).replace(/\s+$/, ''));
      }
    }
    // 連続する空行を 1 行に圧縮
    const collapsed = [];
    for (const l of out) {
      if (l.trim() === '' && collapsed.length && collapsed[collapsed.length - 1].trim() === '') {
        continue;
      }
      collapsed.push(l);
    }
    return collapsed.join('\n').replace(/^\n+/, '').replace(/\n+$/, '');
  }

  function rerender() {
    const code = commentsHidden ? stripComments(originalCode) : originalCode;
    codeEl.textContent = code;
    if (window.Prism) {
      Prism.highlightElement(codeEl);
    }
  }

  // コメント切替ボタン
  const toggleBtn = document.getElementById('toggle-comments');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      commentsHidden = !commentsHidden;
      toggleBtn.textContent = commentsHidden ? '💬 コメントを表示' : '🚫 コメントを非表示';
      toggleBtn.classList.toggle('active', commentsHidden);
      rerender();
    });
  }

  // コードコピー
  const copyBtn = document.getElementById('copy-code');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const code = commentsHidden ? stripComments(originalCode) : originalCode;
      navigator.clipboard.writeText(code).then(() => {
        const orig = copyBtn.textContent;
        copyBtn.textContent = '✓ コピーしました!';
        setTimeout(() => (copyBtn.textContent = orig), 1500);
      });
    });
  }
})();
