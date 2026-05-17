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
//        ボタンクリックで display を切替える。
//        Prism は両方を初回ロード時にハイライト済みなので、再描画不要。
// =====================================================================
(function () {
  const fullBlock = document.querySelector('.code-block-full');
  const strippedBlock = document.querySelector('.code-block-stripped');
  if (!fullBlock || !strippedBlock) return;

  let commentsHidden = false;

  function applyState() {
    if (commentsHidden) {
      fullBlock.hidden = true;
      strippedBlock.hidden = false;
    } else {
      fullBlock.hidden = false;
      strippedBlock.hidden = true;
    }
  }

  // ----- コメント表示トグル -----
  const toggleBtn = document.getElementById('toggle-comments');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      commentsHidden = !commentsHidden;
      toggleBtn.textContent = commentsHidden ? '💬 コメントを表示' : '🚫 コメントを非表示';
      toggleBtn.classList.toggle('active', commentsHidden);
      applyState();
    });
  }

  // ----- コードコピー (現在表示している方をコピー) -----
  const copyBtn = document.getElementById('copy-code');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const visible = commentsHidden ? strippedBlock : fullBlock;
      const codeEl = visible.querySelector('code');
      if (!codeEl) return;
      // Prism がハイライトした後の textContent は元のコード本文 + 行番号ダミー (空)
      // 行番号プラグインの span は textContent に影響しない
      const text = codeEl.textContent;
      navigator.clipboard.writeText(text).then(() => {
        const orig = copyBtn.textContent;
        copyBtn.textContent = '✓ コピーしました!';
        setTimeout(() => (copyBtn.textContent = orig), 1500);
      });
    });
  }
})();
