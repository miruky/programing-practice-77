#!/usr/bin/env python3
"""
競技プログラミングの鉄則77 ─ Python 実装解説サイト 静的サイトジェネレーター

このスクリプトは以下を行う:
  1. scripts/problems.json (問題メタデータ) を読む
  2. docs/codes/*.py (解説付き Python コード) を読む
  3. docs/index.html を生成
  4. docs/problems/*.html を各問題ぶん生成
"""
import json
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CODES_DIR = DOCS / "codes"
PROBLEMS_DIR = DOCS / "problems"
META_PATH = ROOT / "scripts" / "problems.json"

PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)

with META_PATH.open(encoding="utf-8") as f:
    META = json.load(f)

CHAPTERS = META["chapters"]
PROBLEMS = META["problems"]
EXTRAS = META["extras"]

# id -> data 辞書
PROBLEMS_BY_ID = {p["id"]: p for p in PROBLEMS}
# 章番号 -> [問題,...]
PROBLEMS_BY_CHAPTER = {c["id"]: [] for c in CHAPTERS}
for p in PROBLEMS:
    PROBLEMS_BY_CHAPTER[p["chapter"]].append(p)
# 章番号 -> 補足 (base 問題のあとに表示する)
EXTRAS_BY_BASE = {}
for e in EXTRAS:
    EXTRAS_BY_BASE.setdefault(e["base"], []).append(e)

CHAPTER_BY_ID = {c["id"]: c for c in CHAPTERS}

# 全エントリ (本編 + 補足) を index ページに並べる順序
ALL_ENTRIES = []  # (id, title, summary, tags, chapter_id, code_filename)
for p in PROBLEMS:
    ALL_ENTRIES.append({
        "id": p["id"],
        "title": p["title"],
        "summary": p["summary"],
        "tags": p["tags"],
        "chapter": p["chapter"],
        "code_file": f"{p['id']}.py",
        "is_extra": False,
        "base": p["id"],
    })
    # 補足を続けて入れる
    for e in EXTRAS_BY_BASE.get(p["id"], []):
        ALL_ENTRIES.append({
            "id": e["id"],
            "title": e["title"],
            "summary": e["summary"],
            "tags": e["tags"],
            "chapter": p["chapter"],
            "code_file": f"{e['id']}.py",
            "is_extra": True,
            "base": e["base"],
        })

ENTRIES_BY_ID = {e["id"]: e for e in ALL_ENTRIES}


def esc(s):
    return html.escape(str(s), quote=True)


# =====================================================================
#  SVG アイコン定義 (Lucide / Heroicons 系のアウトラインスタイル)
#  currentColor を継承するので、CSS の color から色付け可能。
# =====================================================================
ICON_SEARCH = (
    '<svg class="icon icon-search" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>'
)
ICON_FILE = (
    '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/>'
    '<path d="M14 2v6h6"/></svg>'
)
ICON_EXTERNAL = (
    '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
    '<path d="M15 3h6v6"/><path d="M10 14 21 3"/></svg>'
)
ICON_EYE_OFF = (
    '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/>'
    '<path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/>'
    '<path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/>'
    '<line x1="2" y1="2" x2="22" y2="22"/></svg>'
)
ICON_EYE = (
    '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>'
    '<circle cx="12" cy="12" r="3"/></svg>'
)
ICON_CLIPBOARD = (
    '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/>'
    '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>'
)
LOGO_SVG = (
    '<svg viewBox="0 0 64 64" aria-hidden="true">'
    '<g fill="none" stroke="white" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M22 22 L12 32 L22 42"/><path d="M42 22 L52 32 L42 42"/>'
    '<path d="M37 18 L27 46"/></g></svg>'
)


def strip_python_comments(code: str) -> str:
    """# コメント (純コメント行 + 行末コメント) を除去した Python コードを返す。

    docstring (''' / \"\"\") はコメント扱いせず保持する。
    連続する空行は 1 行に圧縮する。
    """
    out_lines = []
    for line in code.split("\n"):
        # 1) 純コメント行 (前空白の後すぐ #) は丸ごと削除
        if re.match(r"^\s*#", line):
            continue
        # 2) 行末コメント: 最初の # から行末までを切り捨て (末尾の空白も除去)
        #    ※鉄則本のコードでは # を含む文字列リテラルが存在しない前提
        idx = line.find("#")
        if idx >= 0:
            line = line[:idx].rstrip()
        out_lines.append(line)

    # 連続する空行を 1 行に圧縮
    collapsed = []
    for l in out_lines:
        if l.strip() == "" and collapsed and collapsed[-1].strip() == "":
            continue
        collapsed.append(l)

    return "\n".join(collapsed).strip("\n") + "\n"


def base_head(title, description="", favicon_path="assets/favicon.svg"):
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}" />
<link rel="icon" type="image/svg+xml" href="{favicon_path}" />
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;500;700&amp;family=Noto+Sans+JP:wght@400;600;700&amp;display=swap" rel="stylesheet" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css" />
'''


def common_header(home_path="."):
    return f'''<header class="site-header">
  <a href="{home_path}/index.html" class="brand">
    <span class="logo">{LOGO_SVG}</span>
    <span>
      競技プログラミングの鉄則77<br />
      <small>Python 実装ぜんぶ解説サイト</small>
    </span>
  </a>
  <nav>
    <a href="{home_path}/index.html">問題一覧</a>
    <a class="source-link" href="https://github.com/E869120/kyopro-tessoku" target="_blank" rel="noopener noreferrer">原著リポジトリ{ICON_EXTERNAL}</a>
  </nav>
</header>'''


def footer_html():
    return '''<footer>
  © 2024+ 当サイトはオープンソースのコード解説集です。出題および C++/Java の原典コードは
  <a href="https://github.com/E869120/kyopro-tessoku" target="_blank" rel="noopener noreferrer">E869120/kyopro-tessoku</a>
  に帰属します。Python コードは本サイト側で日本語コメントを追加しています。
</footer>'''


# =====================================================================
#  index.html の生成
# =====================================================================
def build_index():
    chip_html = (
        f'<div class="stat-chip"><strong>{len(PROBLEMS)}</strong> 問の本編解答</div>'
        f'<div class="stat-chip"><strong>{len(EXTRAS)}</strong> 件の補足コード</div>'
        f'<div class="stat-chip"><strong>{len(CHAPTERS)}</strong> 章を網羅</div>'
    )

    filter_buttons = '<button class="active" data-chapter="all">すべて</button>'
    for c in CHAPTERS:
        filter_buttons += f'<button data-chapter="{c["id"]}" style="border-color:{c["color"]}33;color:{c["color"]}">{c["id"]}章 {esc(c["title"])}</button>'

    sections_html = ''
    for c in CHAPTERS:
        chap_problems = PROBLEMS_BY_CHAPTER.get(c["id"], [])
        if not chap_problems:
            continue
        cards = ''
        for p in chap_problems:
            cards += render_card(p, c)
            # base 問題の直後に補足カードを並べる
            for e in EXTRAS_BY_BASE.get(p["id"], []):
                cards += render_extra_card(e, c)
        sections_html += f'''
<section class="chapter-section" data-chapter="{c['id']}">
  <div class="chapter-head">
    <span class="accent-bar" style="background: {c['color']}"></span>
    <span class="num">{c['id']}章</span>
    <h2>{esc(c['title'])}</h2>
    <span class="summary">{esc(c['summary'])}</span>
  </div>
  <div class="problems-grid">
    {cards}
  </div>
</section>'''

    html_out = base_head(
        "競技プログラミングの鉄則77 | Python 実装ぜんぶ解説",
        "鉄則77 の全77問+補足コードを、日本語の解説コメント付きで読めるサイト",
    )
    html_out += '<link rel="stylesheet" href="assets/css/styles.css" />\n'
    html_out += '</head><body>\n'
    html_out += common_header(".")
    html_out += '''
<section class="hero">
  <h1>競技プログラミングの鉄則77 ─<br/>Python 実装ぜんぶ解説</h1>
  <div class="stats">
''' + chip_html + '''
  </div>
</section>

<div class="search-wrap">
  <div class="search-inner">
    <div class="search-input-wrap">''' + ICON_SEARCH + '''<input class="search-input" id="search" type="search" placeholder="問題タイトル・タグ・要約から検索 (例: ダイクストラ, DP, 累積和)" /></div>
    <div class="chapter-filter">''' + filter_buttons + '''</div>
  </div>
</div>

<main class="chapters">
''' + sections_html + '''
</main>
''' + footer_html() + '''
<script src="assets/js/main.js"></script>
</body></html>
'''
    (DOCS / "index.html").write_text(html_out, encoding="utf-8")


def render_card(p, c):
    search_text = (p["title"] + " " + p["summary"] + " " + " ".join(p["tags"])).lower()
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in p["tags"])
    style = f'style="--card-color:{c["color"]}"'
    return f'''
    <a class="problem-card" href="problems/{p['id']}.html" data-chapter="{c['id']}" data-search="{esc(search_text)}" {style}>
      <div class="pid">{p['id']} ・ {c['id']}章</div>
      <h3>{esc(p['title'])}</h3>
      <p>{esc(p['summary'])}</p>
      <div class="tags">{tags}</div>
    </a>'''


def render_extra_card(e, c):
    search_text = (e["title"] + " " + e["summary"] + " " + " ".join(e["tags"])).lower()
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in e["tags"])
    return f'''
    <a class="problem-card" href="problems/{e['id']}.html" data-chapter="{c['id']}" data-search="{esc(search_text)}">
      <div class="pid">+ {e['base']} 補足コード</div>
      <h3>{esc(e['title'])}</h3>
      <p>{esc(e['summary'])}</p>
      <div class="tags">{tags}</div>
    </a>'''


# =====================================================================
#  問題ページ生成
# =====================================================================
def build_problem_pages():
    # navigation のため、ALL_ENTRIES の順番リストを作る
    order = [e["id"] for e in ALL_ENTRIES]
    for idx, entry in enumerate(ALL_ENTRIES):
        prev_id = order[idx - 1] if idx > 0 else None
        next_id = order[idx + 1] if idx + 1 < len(order) else None
        build_problem_page(entry, prev_id, next_id)


def build_problem_page(entry, prev_id, next_id):
    code_path = CODES_DIR / entry["code_file"]
    code = code_path.read_text(encoding="utf-8") if code_path.exists() else ""
    stripped_code = strip_python_comments(code) if code else ""
    chapter = CHAPTER_BY_ID[entry["chapter"]]

    tags_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in entry["tags"])

    prev_html = render_nav(prev_id, "前の問題", "prev")
    next_html = render_nav(next_id, "次の問題", "next")

    description_meta = (
        f"{entry['id']}: {entry['title']} ─ 競技プログラミングの鉄則77 の Python 実装と日本語解説"
    )

    title = f"{entry['id']}: {entry['title']} | 鉄則77 Python解説"

    html_out = base_head(title, description_meta, favicon_path="../assets/favicon.svg")
    html_out += '<link rel="stylesheet" href="../assets/css/styles.css" />\n'
    html_out += '</head><body>\n'
    html_out += common_header("..")

    html_out += f'''
<main class="problem-detail">
  <nav class="breadcrumb">
    <a href="../index.html">問題一覧</a> /
    <span style="color: {chapter['color']}">{chapter['id']}章: {esc(chapter['title'])}</span> /
    <strong>{esc(entry['id'])}</strong>
  </nav>

  <span class="id-pill">{esc(entry['id'])}</span>
  <h1>{esc(entry['title'])}</h1>

  <div class="summary">{esc(entry['summary'])}</div>

  <div class="meta">
    <div class="meta-item">
      <strong>章</strong>
      <span style="color: {chapter['color']}">{chapter['id']}章: {esc(chapter['title'])}</span>
    </div>
    <div class="meta-item">
      <strong>主な技法</strong>
      <div class="tags" style="margin-top:4px">{tags_html}</div>
    </div>
    <div class="meta-item">
      <strong>原典</strong>
      {source_link_html(entry, chapter)}
    </div>
  </div>

  <div class="code-actions">
    <span class="file-label">{ICON_FILE}{esc(entry['code_file'])} ─ Python 3</span>
    <div class="actions">
      <button id="toggle-comments" type="button">{ICON_EYE}<span class="label">コメントを表示</span></button>
      <button id="copy-code" type="button">{ICON_CLIPBOARD}<span class="label">コードをコピー</span></button>
    </div>
  </div>
  <pre class="line-numbers code-block-full" hidden><code class="language-python">{esc(code)}</code></pre>
  <pre class="line-numbers code-block-stripped"><code class="language-python">{esc(stripped_code)}</code></pre>

  <div class="nav-arrows">
    {prev_html}
    {next_html}
  </div>
</main>
'''
    html_out += footer_html()
    # Prism JS components
    html_out += '''
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-core.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/line-numbers/prism-line-numbers.min.css" />
<script src="../assets/js/main.js"></script>
</body></html>
'''
    (PROBLEMS_DIR / f"{entry['id']}.html").write_text(html_out, encoding="utf-8")


def source_link_html(entry, chapter):
    """原典 GitHub リンク (A55 のみ Python が存在しないので C++ を指す)"""
    chap_str = str(chapter['id']).zfill(2)
    base = entry['code_file'].replace('.py', '')
    if entry['id'] == 'A55':
        url = f"https://github.com/E869120/kyopro-tessoku/blob/main/codes/cpp/chap{chap_str}/answer_A55.cpp"
        label = "GitHub で C++ 原文を見る (Python は当サイト独自実装)"
    else:
        url = f"https://github.com/E869120/kyopro-tessoku/blob/main/codes/python/chap{chap_str}/answer_{base}.py"
        label = "GitHub で原文を見る"
    return f'<a class="source-link" href="{url}" target="_blank" rel="noopener noreferrer">{esc(label)}{ICON_EXTERNAL}</a>'


def render_nav(target_id, label, klass):
    if target_id is None:
        return f'<a class="{klass} disabled"><div class="nav-label">{label}</div><div class="nav-title">─</div></a>'
    e = ENTRIES_BY_ID[target_id]
    return (f'<a class="{klass}" href="{target_id}.html">'
            f'<div class="nav-label">{label}</div>'
            f'<div class="nav-title">{esc(target_id)}: {esc(e["title"])}</div>'
            '</a>')


# =====================================================================
#  実行
# =====================================================================
def main():
    print("Generating index.html...")
    build_index()
    print(f"Generating {len(ALL_ENTRIES)} problem pages...")
    build_problem_pages()
    print("Done!")


if __name__ == "__main__":
    main()
