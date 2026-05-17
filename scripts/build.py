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
    <span class="logo">P</span>
    <span>
      競技プログラミングの鉄則77<br />
      <small>Python 実装ぜんぶ解説サイト</small>
    </span>
  </a>
  <nav>
    <a href="{home_path}/index.html">問題一覧</a>
    <a href="https://github.com/E869120/kyopro-tessoku" target="_blank" rel="noopener noreferrer">原著リポジトリ ↗</a>
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
    <input class="search-input" id="search" type="search" placeholder="🔍 問題タイトル・タグ・要約から検索 (例: ダイクストラ, DP, 累積和)" />
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
    <span>📄 {esc(entry['code_file'])} ─ Python 3</span>
    <div class="actions">
      <button id="toggle-comments">🚫 コメントを非表示</button>
      <button id="copy-code">📋 コードをコピー</button>
    </div>
  </div>
  <pre class="line-numbers"><code class="language-python">{esc(code)}</code></pre>

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
        label = "GitHub で C++ 原文を見る ↗ (Python は当サイト独自実装)"
    else:
        url = f"https://github.com/E869120/kyopro-tessoku/blob/main/codes/python/chap{chap_str}/answer_{base}.py"
        label = "GitHub で原文を見る ↗"
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'


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
