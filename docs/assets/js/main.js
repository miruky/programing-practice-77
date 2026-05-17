// =====================================================================
//  検索 + 章フィルタ
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
    // 中身が全部隠れた章セクションごと非表示にする
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
//  コピー / ダウンロード ボタン (問題詳細ページ用)
// =====================================================================
(function () {
  const copyBtn = document.getElementById('copy-code');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const codeEl = document.querySelector('pre[class*="language-"] code');
      if (!codeEl) return;
      navigator.clipboard.writeText(codeEl.innerText).then(() => {
        const orig = copyBtn.innerText;
        copyBtn.innerText = 'コピーしました!';
        setTimeout(() => (copyBtn.innerText = orig), 1500);
      });
    });
  }
})();
