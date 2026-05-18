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
APPLIED = META.get("applied", [])
FINAL = META.get("final", [])

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

# 基本問題 ID -> 応用問題エントリ (1 対 1)
APPLIED_BY_BASE = {a["base"]: a for a in APPLIED}
# 応用問題 ID -> 応用問題エントリ
APPLIED_BY_ID = {a["id"]: a for a in APPLIED}

# 章番号 -> [力試し問題,...] (chap10 のみ)
FINAL_BY_CHAPTER = {c["id"]: [] for c in CHAPTERS}
for f in FINAL:
    FINAL_BY_CHAPTER[f["chapter"]].append(f)
FINAL_BY_ID = {f["id"]: f for f in FINAL}

CHAPTER_BY_ID = {c["id"]: c for c in CHAPTERS}

# 全エントリ (本編 + 補足 + 力試し) を index ページに並べる順序
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
        "is_final": False,
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
            "is_final": False,
            "base": e["base"],
        })
# 力試し問題は最後 (= 10 章セクションの末尾) に並べる
for f in FINAL:
    ALL_ENTRIES.append({
        "id": f["id"],
        "title": f["title"],
        "summary": f["summary"],
        "tags": f["tags"],
        "chapter": f["chapter"],
        "code_file": f"{f['id']}.py",
        "is_extra": False,
        "is_final": True,
        "base": f["id"],
        "atcoder": f.get("atcoder"),
    })

ENTRIES_BY_ID = {e["id"]: e for e in ALL_ENTRIES}

# 応用問題ページ用に独立した一覧 (前後ナビゲーション用に並びを保持)
APPLIED_ENTRIES = []
for p in PROBLEMS:
    a = APPLIED_BY_BASE.get(p["id"])
    if a is None:
        continue
    APPLIED_ENTRIES.append({
        "id": a["id"],
        "title": a["title"],
        "summary": a["summary"],
        "tags": a["tags"],
        "chapter": a["chapter"],
        "code_file": f"{a['id']}.py",
        "base": a["base"],
        "atcoder": a.get("atcoder"),
    })


def esc(s):
    return html.escape(str(s), quote=True)


def write_html(path, content):
    """生成 HTML の各行末尾空白を削ってから保存する。"""
    normalized = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
    path.write_text(normalized, encoding="utf-8")


# =====================================================================
#  AtCoder 風 難易度色バッジ
#  鉄則本の ★1〜★5 を AtCoder の色レンジ (灰/茶/緑/水/青) に対応付ける。
#  公式の対応表ではなく、本サイト独自の目安マッピング。
# =====================================================================
AC_COLORS = {
    1: {"name": "灰", "css": "ac-1"},
    2: {"name": "茶", "css": "ac-2"},
    3: {"name": "緑", "css": "ac-3"},
    4: {"name": "水", "css": "ac-4"},
    5: {"name": "青", "css": "ac-5"},
}

EXTRAS_BY_ID = {e["id"]: e for e in EXTRAS}


def effective_difficulty(entry_id):
    """エントリ ID から表示用の★を返す。
    A/C: 既定の difficulty。
    B (応用): base の A 問題 difficulty + 1 (上限 5)。
    補足コード: base の A 問題 difficulty (据え置き)。
    """
    if entry_id in PROBLEMS_BY_ID and "difficulty" in PROBLEMS_BY_ID[entry_id]:
        return PROBLEMS_BY_ID[entry_id]["difficulty"]
    if entry_id in FINAL_BY_ID and "difficulty" in FINAL_BY_ID[entry_id]:
        return FINAL_BY_ID[entry_id]["difficulty"]
    if entry_id in APPLIED_BY_ID:
        base = APPLIED_BY_ID[entry_id]["base"]
        base_diff = PROBLEMS_BY_ID.get(base, {}).get("difficulty")
        if base_diff is None:
            return None
        return min(5, base_diff + 1)
    if entry_id in EXTRAS_BY_ID:
        base = EXTRAS_BY_ID[entry_id]["base"]
        return PROBLEMS_BY_ID.get(base, {}).get("difficulty")
    return None


def render_ac_badge(diff, *, mini=False):
    """AtCoder 色バッジ HTML を返す。mini=True ならカード用の小型版。"""
    if diff is None or diff not in AC_COLORS:
        return ''
    info = AC_COLORS[diff]
    klass = f"ac-badge ac-badge--{info['css']}"
    if mini:
        klass += " ac-badge--mini"
    return (
        f'<span class="{klass}" title="本サイト独自マッピング: 鉄則本 ★{diff} ≒ AtCoder {info["name"]}色">'
        f'<span class="ac-star">★{diff}</span>'
        f'<span class="ac-name">{info["name"]}</span></span>'
    )


# =====================================================================
#  コメント表示時に出す「読み方ガイド」と簡易図解
#  生成時に各問題のタグから学習のつまずきどころを推定し、問題ページへ埋め込む。
#  main.js 側でコメント表示トグルと同期して hidden を切り替える。
# =====================================================================
GUIDE_DEFS = {
    "cumsum2d": {
        "label": "2 次元累積和",
        "mental": "Z[i][j] は「左上からここまでの合計」です。欲しい長方形は、大きく取って、上と左を引き、左上を戻します。",
        "steps": [
            "0 行目・0 列目を余分に持つ理由を先に確認する。",
            "Z を作る式では「今のマス + 上 + 左 - 左上」と読む。",
            "答えの式は「右下 - 上 - 左 + 左上」の順に分解する。",
        ],
        "pitfall": "A-1 / B-1 が出るので、元配列は 0-index、累積和は 1-index と割り切って読むと混乱しにくいです。",
    },
    "imos2d": {
        "label": "2 次元いもす法",
        "mental": "長方形全体を毎回塗らず、四隅だけに + / - の印を置きます。最後に累積和を取ると、印が面に広がります。",
        "steps": [
            "まず四隅への更新だけを追う。ここではまだ完成形ではない。",
            "横方向の累積で印を横に伸ばす。",
            "縦方向の累積で面に復元し、必要なセルを数える。",
        ],
        "pitfall": "右端・下端に置く -1 は、矩形の外側を止めるための印です。閉区間か半開区間かだけを必ず確認します。",
    },
    "cumsum1d": {
        "label": "1 次元累積和",
        "mental": "S[i] は先頭から i 個分の合計です。区間 [l, r] は、右端までの合計から左手前までを引きます。",
        "steps": [
            "S[0] = 0 を番兵として用意する。",
            "S[i] = S[i-1] + A[i-1] で前から足す。",
            "区間和は S[r] - S[l-1] または半開区間なら S[r] - S[l] と読む。",
        ],
        "pitfall": "問題が 1-indexed で来るか、Python の配列が 0-indexed かで式が 1 つずれます。",
    },
    "imos1d": {
        "label": "いもす法",
        "mental": "区間全体を更新せず、始点で +、終点の次で - を置きます。累積和を取ると各位置の値に戻ります。",
        "steps": [
            "各区間の左端に加算、右端の次に減算する。",
            "差分配列を左から累積して本当の値に戻す。",
            "復元後の配列を出力・集計する。",
        ],
        "pitfall": "右端が含まれる区間なら r+1 に -、半開区間 [l, r) なら r に - を置きます。",
    },
    "binary": {
        "label": "二分探索",
        "mental": "答えの候補を一直線に並べ、NG と OK の境目を探します。毎回、真ん中を見て半分捨てます。",
        "steps": [
            "何が OK で何が NG かを言葉で決める。",
            "left / right が常に条件を満たすように初期化する。",
            "mid の判定結果で、境目がどちら側にあるかだけ更新する。",
        ],
        "pitfall": "探索しているのは値そのものではなく、条件が切り替わる境目です。",
    },
    "twopointer": {
        "label": "しゃくとり法",
        "mental": "左端と右端で窓を持ち、条件を壊さない範囲で右端だけ前へ進めます。",
        "steps": [
            "左端 l を 1 つずつ進める。",
            "条件を満たす限り右端 r を進める。",
            "その l から作れる区間数をまとめて足す。",
        ],
        "pitfall": "r を毎回 l に戻さないことが高速化の本体です。",
    },
    "dp": {
        "label": "動的計画法",
        "mental": "dp は「途中結果のメモ」です。dp[i] や dp[i][j] の日本語意味を決めると、遷移式が読みやすくなります。",
        "steps": [
            "dp の添字が何を表すかを先に固定する。",
            "初期状態だけを手で入れる。",
            "小さい状態から大きい状態へ、使う/使わない・進む/進まないで遷移する。",
        ],
        "pitfall": "式を先に暗記するより、dp[i] の意味を日本語で読めるかを優先します。",
    },
    "bitdp": {
        "label": "bitDP",
        "mental": "整数 1 個を、ON/OFF の集合として使います。bit が 1 なら、その要素をすでに選んでいる状態です。",
        "steps": [
            "状態 state を 2 進数で見て、どの要素が入っているか確認する。",
            "1 << k で k 番目の要素を表す。",
            "OR や XOR で集合の追加・反転を行う。",
        ],
        "pitfall": "状態数は 2^N なので、N が小さい問題専用の考え方です。",
    },
    "graph": {
        "label": "グラフ探索",
        "mental": "頂点を点、辺を道として、今いる点から行ける点へ順に広げます。",
        "steps": [
            "まず入力を隣接リスト G に変換する。",
            "visited / dist で、訪問済みや距離を記録する。",
            "DFS は深く、BFS は近い順に広げると読む。",
        ],
        "pitfall": "グリッド問題も、各マスを頂点だと思えば同じ形になります。",
    },
    "dijkstra": {
        "label": "ダイクストラ法",
        "mental": "未確定の中で一番距離が短い頂点を確定し、その頂点から隣を更新します。",
        "steps": [
            "cur[v] を暫定最短距離として初期化する。",
            "ヒープから距離最小の頂点を取り出す。",
            "その頂点から伸びる辺で隣の距離を改善する。",
        ],
        "pitfall": "辺の重みが負の場合は使えません。古い候補がヒープに残るので、確定済みならスキップします。",
    },
    "unionfind": {
        "label": "Union-Find",
        "mental": "グループの代表者だけを覚えます。同じ代表なら同じ連結成分です。",
        "steps": [
            "root(x) で x の代表を探す。",
            "unite(a, b) で 2 つの集合を結合する。",
            "same(a, b) で代表が同じかを見る。",
        ],
        "pitfall": "辺削除は苦手なので、削除クエリは逆順に見て追加へ変換することがあります。",
    },
    "segtree": {
        "label": "セグメント木",
        "mental": "配列を区間ごとに二分した木です。親には子 2 つをまとめた値を置きます。",
        "steps": [
            "葉に元配列の値を置く。",
            "親を max / sum などの演算で作る。",
            "クエリでは関係ない区間を捨て、完全に含まれる区間だけ使う。",
        ],
        "pitfall": "半開区間 [l, r) で統一すると実装のズレが減ります。",
    },
    "flow": {
        "label": "最大フロー",
        "mental": "辺には容量があり、まだ流せる残り容量を残余グラフで管理します。",
        "steps": [
            "各辺に逆辺を追加して残余グラフを作る。",
            "s から t まで流せる道を探す。",
            "流した分だけ順辺を減らし、逆辺を増やす。",
        ],
        "pitfall": "逆辺は「あとで流れを取り消せる余地」を表します。ここが最大フローの一番見落としやすい点です。",
    },
    "greedy": {
        "label": "貪欲法",
        "mental": "その場の選択が後で損にならない基準を見つけて、順に決めます。",
        "steps": [
            "何を基準に並べるかを確認する。",
            "先頭から見て、採用できるものを採用する。",
            "なぜ後で取り返しがつく/つかないかをコメントで確認する。",
        ],
        "pitfall": "貪欲は実装より「その選び方でよい理由」が本体です。",
    },
    "math": {
        "label": "数学・数え上げ",
        "mental": "全部試す代わりに、式・周期・余り・不変量で一気に数えます。",
        "steps": [
            "何を数えたいかを集合や式に置き換える。",
            "重複・余り・周期を確認する。",
            "計算量が定数または log になっているか見る。",
        ],
        "pitfall": "式変形だけを追うとつらいので、小さい例で 1 回手計算すると読みやすいです。",
    },
    "default": {
        "label": "実装の基本",
        "mental": "入力、前処理、判定・更新、出力の 4 ブロックに分けて読むと崩れにくいです。",
        "steps": [
            "入力で何が変数・配列に入るか確認する。",
            "ループが何を全探索・更新しているか見る。",
            "最後に答えへどう変換しているか確認する。",
        ],
        "pitfall": "名前だけで追わず、各変数・配列に入っている意味を 1 行で言語化します。",
    },
}


def guide_kind(entry):
    text = " ".join([entry.get("title", ""), entry.get("summary", ""), " ".join(entry.get("tags", []))])
    if "最大フロー" in text or "マッチング" in text:
        return "flow"
    if "ダイクストラ" in text:
        return "dijkstra"
    if "UnionFind" in text or "Union-Find" in text:
        return "unionfind"
    if "セグメント木" in text:
        return "segtree"
    if "bitDP" in text or "状態BFS" in text:
        return "bitdp"
    if "2次元" in text and "いもす" in text:
        return "imos2d"
    if "2次元" in text and "累積和" in text:
        return "cumsum2d"
    if "いもす" in text:
        return "imos1d"
    if "累積和" in text:
        return "cumsum1d"
    if "二分探索" in text or "LIS" in text:
        return "binary"
    if "しゃくとり" in text:
        return "twopointer"
    if "DP" in text or "dp" in text:
        return "dp"
    if "BFS" in text or "DFS" in text or "グラフ" in text or "木DP" in text:
        return "graph"
    if "貪欲" in text or "区間スケジューリング" in text:
        return "greedy"
    if "数学" in text or "GCD" in text or "mod" in text or "包除" in text or "素数" in text:
        return "math"
    return "default"


def visual_html(kind):
    """簡易図解。全問題ではなく、図が効く型だけ返す。"""
    if kind == "cumsum2d":
        cells = ""
        for r in range(4):
            for c in range(4):
                klass = "v-cell"
                if r < 1 and c < 1:
                    klass += " is-corner"
                elif r < 1:
                    klass += " is-cut"
                elif c < 1:
                    klass += " is-cut"
                elif 1 <= r <= 3 and 1 <= c <= 3:
                    klass += " is-target"
                cells += f'<span class="{klass}"></span>'
        return f'''
      <div class="visual visual-cumsum2d" aria-hidden="true">
        <div class="visual-title">右下 - 上 - 左 + 左上</div>
        <div class="v-grid">{cells}</div>
        <div class="visual-legend"><span class="target"></span>欲しい範囲 <span class="cut"></span>引く範囲 <span class="corner"></span>戻す範囲</div>
      </div>'''
    if kind == "imos2d":
        return '''
      <div class="visual visual-imos2d" aria-hidden="true">
        <div class="visual-title">四隅だけに印を置く</div>
        <div class="imos-box"><span class="corner-plus tl">+1</span><span class="corner-minus tr">-1</span><span class="corner-minus bl">-1</span><span class="corner-plus br">+1</span></div>
      </div>'''
    if kind == "cumsum1d":
        return '''
      <div class="visual visual-line" aria-hidden="true">
        <div class="visual-title">区間和 = 右端まで - 左手前まで</div>
        <div class="line-cells"><span>S[0]</span><span>S[l-1]</span><span class="active">l..r</span><span>S[r]</span></div>
      </div>'''
    if kind == "imos1d":
        return '''
      <div class="visual visual-line" aria-hidden="true">
        <div class="visual-title">始点で +、終点の次で -</div>
        <div class="line-cells"><span></span><span class="plus">+1</span><span class="active">区間</span><span class="minus">-1</span></div>
      </div>'''
    if kind == "binary":
        return '''
      <div class="visual visual-line" aria-hidden="true">
        <div class="visual-title">NG / OK の境目を探す</div>
        <div class="binary-line"><span class="ng">NG</span><span class="ng">NG</span><span class="mid">mid</span><span class="ok">OK</span><span class="ok">OK</span></div>
      </div>'''
    if kind == "twopointer":
        return '''
      <div class="visual visual-line" aria-hidden="true">
        <div class="visual-title">窓を右へ滑らせる</div>
        <div class="window-line"><span></span><span class="l">l</span><span class="active">window</span><span class="r">r</span><span></span></div>
      </div>'''
    if kind == "dp":
        return '''
      <div class="visual visual-dp" aria-hidden="true">
        <div class="visual-title">小さい状態から大きい状態へ</div>
        <div class="dp-flow"><span>dp[i-2]</span><span>dp[i-1]</span><strong>dp[i]</strong></div>
      </div>'''
    if kind == "bitdp":
        return '''
      <div class="visual visual-bit" aria-hidden="true">
        <div class="visual-title">整数を集合として読む</div>
        <div class="bit-row"><span>1</span><span>0</span><span>1</span><span>1</span></div>
        <div class="bit-caption">ON の bit = 選ばれている要素</div>
      </div>'''
    if kind == "graph":
        return '''
      <div class="visual visual-graph" aria-hidden="true">
        <div class="visual-title">点と道に変換して探索</div>
        <div class="graph-shape"><span class="node n1">1</span><span class="node n2">2</span><span class="node n3">3</span><span class="edge e1"></span><span class="edge e2"></span></div>
      </div>'''
    if kind == "dijkstra":
        return '''
      <div class="visual visual-graph" aria-hidden="true">
        <div class="visual-title">距離最小から確定</div>
        <div class="graph-shape"><span class="node n1 fixed">0</span><span class="node n2">4</span><span class="node n3">7</span><span class="edge e1"></span><span class="edge e2"></span></div>
      </div>'''
    if kind == "unionfind":
        return '''
      <div class="visual visual-uf" aria-hidden="true">
        <div class="visual-title">代表者が同じなら同じ集合</div>
        <div class="uf-groups"><span>1</span><span>2</span><span>3</span></div><div class="uf-groups alt"><span>4</span><span>5</span></div>
      </div>'''
    if kind == "segtree":
        return '''
      <div class="visual visual-tree" aria-hidden="true">
        <div class="visual-title">区間を半分ずつまとめる</div>
        <div class="tree-level"><span>[0,8)</span></div><div class="tree-level"><span>[0,4)</span><span>[4,8)</span></div><div class="tree-level"><span>[0,2)</span><span>[2,4)</span><span>[4,6)</span><span>[6,8)</span></div>
      </div>'''
    if kind == "flow":
        return '''
      <div class="visual visual-flow" aria-hidden="true">
        <div class="visual-title">容量つきの道に流す</div>
        <div class="flow-row"><span>s</span><span>L</span><span>R</span><span>t</span></div>
      </div>'''
    return ""


def learning_panel_html(entry):
    kind = guide_kind(entry)
    guide = GUIDE_DEFS[kind]
    steps = "".join(f"<li>{esc(s)}</li>" for s in guide["steps"])
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in entry.get("tags", []))
    visual = visual_html(kind)
    diff = effective_difficulty(entry["id"])
    diff_text = f"★{diff}" if diff else "未設定"
    return f'''
  <section class="explain-panel" hidden>
    <div class="explain-panel-head">
      <span class="explain-kicker">コメント表示中だけの読み方ガイド</span>
      <strong>{esc(guide["label"])}</strong>
    </div>
    <div class="explain-panel-body">
      <div class="explain-copy">
        <p class="explain-lead">{esc(guide["mental"])}</p>
        <ol>{steps}</ol>
        <p class="explain-pitfall"><strong>詰まりやすい点:</strong> {esc(guide["pitfall"])}</p>
        <div class="explain-meta-line"><span>難易度目安: {esc(diff_text)}</span><span>{tags}</span></div>
      </div>
      {visual}
    </div>
  </section>'''


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
    total = len(PROBLEMS) + len(EXTRAS) + len(APPLIED) + len(FINAL)
    chip_html = (
        f'<div class="stat-chip"><strong>{len(PROBLEMS)}</strong> 問の本編 (A)</div>'
        f'<div class="stat-chip"><strong>{len(APPLIED)}</strong> 問の応用 (B)</div>'
        f'<div class="stat-chip"><strong>{len(FINAL)}</strong> 問の力試し (C)</div>'
        f'<div class="stat-chip"><strong>{len(EXTRAS)}</strong> 件の補足コード</div>'
        f'<div class="stat-chip"><strong>{total}</strong> 問掲載</div>'
    )

    filter_buttons = '<button class="active" data-chapter="all">すべて</button>'
    for c in CHAPTERS:
        filter_buttons += f'<button data-chapter="{c["id"]}" style="border-color:{c["color"]}33;color:{c["color"]}">{c["id"]}章 {esc(c["title"])}</button>'

    sections_html = ''
    for c in CHAPTERS:
        chap_problems = PROBLEMS_BY_CHAPTER.get(c["id"], [])
        chap_finals = FINAL_BY_CHAPTER.get(c["id"], [])
        if not chap_problems and not chap_finals:
            continue
        cards = ''
        for p in chap_problems:
            cards += render_card(p, c)
            # base 問題の直後に補足カードを並べる
            for e in EXTRAS_BY_BASE.get(p["id"], []):
                cards += render_extra_card(e, c)
        # 力試し問題は章末尾に並べる (10 章のみ)
        for f in chap_finals:
            cards += render_final_card(f, c)
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
    write_html(DOCS / "index.html", html_out)


def render_card(p, c):
    """基本問題カード ─ 応用問題が存在する場合は "応用 B0X" バッジを差し込む"""
    search_text = (p["title"] + " " + p["summary"] + " " + " ".join(p["tags"])).lower()
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in p["tags"])
    style = f'style="--card-color:{c["color"]}"'
    applied = APPLIED_BY_BASE.get(p["id"])
    applied_badge = ''
    if applied:
        applied_badge = f'<span class="applied-badge">応用 {esc(applied["id"])}</span>'
        # 応用問題のタイトルも検索対象に含める
        search_text += " " + applied["title"].lower() + " " + applied["summary"].lower()
    ac_badge = render_ac_badge(effective_difficulty(p["id"]), mini=True)
    return f'''
    <a class="problem-card" href="problems/{p['id']}.html" data-chapter="{c['id']}" data-search="{esc(search_text)}" {style}>
      <div class="pid">{p['id']} ・ {c['id']}章{applied_badge}{ac_badge}</div>
      <h3>{esc(p['title'])}</h3>
      <p>{esc(p['summary'])}</p>
      <div class="tags">{tags}</div>
    </a>'''


def render_extra_card(e, c):
    search_text = (e["title"] + " " + e["summary"] + " " + " ".join(e["tags"])).lower()
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in e["tags"])
    ac_badge = render_ac_badge(effective_difficulty(e["id"]), mini=True)
    return f'''
    <a class="problem-card" href="problems/{e['id']}.html" data-chapter="{c['id']}" data-search="{esc(search_text)}">
      <div class="pid">+ {e['base']} 補足コード{ac_badge}</div>
      <h3>{esc(e['title'])}</h3>
      <p>{esc(e['summary'])}</p>
      <div class="tags">{tags}</div>
    </a>'''


def render_final_card(f, c):
    """力試し問題 (C 問題) のカード ─ ピンク系のバッジで A 問題と区別する"""
    search_text = (f["title"] + " " + f["summary"] + " " + " ".join(f["tags"])).lower()
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in f["tags"])
    style = f'style="--card-color:{c["color"]}"'
    ac_badge = render_ac_badge(effective_difficulty(f["id"]), mini=True)
    return f'''
    <a class="problem-card problem-card--final" href="problems/{f['id']}.html" data-chapter="{c['id']}" data-search="{esc(search_text)}" {style}>
      <div class="pid">{f['id']} ・ {c['id']}章<span class="final-badge">力試し</span>{ac_badge}</div>
      <h3>{esc(f['title'])}</h3>
      <p>{esc(f['summary'])}</p>
      <div class="tags">{tags}</div>
    </a>'''


# =====================================================================
#  応用問題関連 (B 問題)
# =====================================================================
def atcoder_url(slug):
    """slug は "contest_id/task_id" 形式 (例: tessoku-book/tessoku_book_bz)"""
    if not slug:
        return None
    contest, task = slug.split("/", 1)
    return f"https://atcoder.jp/contests/{contest}/tasks/{task}"


def applied_source_link_html(applied, chapter):
    """応用問題の原典 (editorial 内 Python ソース) への GitHub リンク"""
    chap_str = str(chapter['id']).zfill(2)
    url = f"https://github.com/E869120/kyopro-tessoku/blob/main/editorial/chap{chap_str}/python/answer_{applied['id']}.py"
    label = "GitHub で原文 (editorial) を見る"
    return f'<a class="source-link" href="{url}" target="_blank" rel="noopener noreferrer">{esc(label)}{ICON_EXTERNAL}</a>'


def applied_link_block_for_base(base_id):
    """基本問題ページに埋め込む『応用問題への誘導ブロック』を返す。応用が無ければ空文字列。"""
    a = APPLIED_BY_BASE.get(base_id)
    if a is None:
        return ''
    atc = atcoder_url(a.get("atcoder"))
    atc_link = ''
    if atc:
        atc_link = f' <a class="source-link" style="margin-left:6px" href="{atc}" target="_blank" rel="noopener noreferrer">AtCoder で問題を見る{ICON_EXTERNAL}</a>'
    return f'''
  <div class="applied-banner">
    <span class="applied-banner-label">応用問題</span>
    <a class="applied-banner-link" href="{a['id']}.html">
      <strong>{esc(a['id'])}: {esc(a['title'])}</strong>
      <span class="applied-banner-summary">{esc(a['summary'])}</span>
    </a>
    {atc_link}
  </div>'''


def base_link_block_for_applied(base_id):
    """応用問題ページに埋め込む『対応する基本問題への誘導ブロック』を返す。"""
    p = PROBLEMS_BY_ID.get(base_id)
    if p is None:
        return ''
    return f'''
  <div class="applied-banner applied-banner--reverse">
    <span class="applied-banner-label">基本問題</span>
    <a class="applied-banner-link" href="{p['id']}.html">
      <strong>{esc(p['id'])}: {esc(p['title'])}</strong>
      <span class="applied-banner-summary">{esc(p['summary'])}</span>
    </a>
  </div>'''


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

    is_final = entry.get('is_final', False)

    description_meta = (
        f"{entry['id']}: {entry['title']} ─ 競技プログラミングの鉄則77 の Python 実装と日本語解説"
    )
    title = f"{entry['id']}: {entry['title']} | 鉄則77 Python解説"
    if is_final:
        title = f"{entry['id']}: {entry['title']} | 鉄則77 Python解説 (力試し問題)"

    html_out = base_head(title, description_meta, favicon_path="../assets/favicon.svg")
    html_out += '<link rel="stylesheet" href="../assets/css/styles.css" />\n'
    html_out += '</head><body>\n'
    html_out += common_header("..")

    # 力試し問題 (C) は対応する A 問題が無いので、AtCoder のリンクを meta に追加する。
    atc_meta_html = ''
    if is_final:
        atc_url = atcoder_url(entry.get('atcoder'))
        if atc_url:
            atc_link = (
                f'<a class="source-link" href="{atc_url}" target="_blank" '
                f'rel="noopener noreferrer">AtCoder で問題を見る{ICON_EXTERNAL}</a>'
            )
        else:
            atc_link = '<span style="color:#9ca3af">(AtCoder には掲載なし)</span>'
        atc_meta_html = f'''
    <div class="meta-item">
      <strong>AtCoder</strong>
      {atc_link}
    </div>'''

    id_pill_class = 'id-pill id-pill--final' if is_final else 'id-pill'
    ac_badge = render_ac_badge(effective_difficulty(entry['id']))
    ac_meta_html = ''
    if ac_badge:
        ac_meta_html = f'''
    <div class="meta-item">
      <strong>難易度</strong>
      <div style="margin-top:4px">{ac_badge}</div>
    </div>'''

    html_out += f'''
<main class="problem-detail">
  <nav class="breadcrumb">
    <a href="../index.html">問題一覧</a> /
    <span style="color: {chapter['color']}">{chapter['id']}章: {esc(chapter['title'])}</span> /
    <strong>{esc(entry['id'])}</strong>
  </nav>

  <span class="{id_pill_class}">{esc(entry['id'])}</span>
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
    </div>{ac_meta_html}
    <div class="meta-item">
      <strong>原典</strong>
      {source_link_html(entry, chapter)}
    </div>{atc_meta_html}
  </div>
  {applied_link_block_for_base(entry['id']) if (not entry.get('is_extra') and not is_final) else ''}
  <div class="code-actions">
    <span class="file-label">{ICON_FILE}{esc(entry['code_file'])} ─ Python 3</span>
    <div class="actions">
      <button id="toggle-comments" type="button">{ICON_EYE}<span class="label">コメントを表示</span></button>
      <button id="copy-code" type="button">{ICON_CLIPBOARD}<span class="label">コードをコピー</span></button>
    </div>
  </div>
  {learning_panel_html(entry)}
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
    write_html(PROBLEMS_DIR / f"{entry['id']}.html", html_out)


def source_link_html(entry, chapter):
    """原典 GitHub リンク
       - 力試し問題 C* は editorial/final/cpp の C++ ソースを指す (Python 版は当サイト独自実装)
       - A55 のみ Python 原典が無いので C++ を指す
       - それ以外は codes/python/chap{XX}/answer_AXX.py
    """
    chap_str = str(chapter['id']).zfill(2)
    base = entry['code_file'].replace('.py', '')
    if entry.get('is_final'):
        url = f"https://github.com/E869120/kyopro-tessoku/blob/main/editorial/final/cpp/answer_{base}.cpp"
        label = "GitHub で C++ 原文を見る (Python は当サイト独自実装)"
    elif entry['id'] == 'A55':
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


def render_applied_nav(target_id, label, klass):
    """応用問題ページの前後リンク (応用問題内でのみ移動)"""
    if target_id is None:
        return f'<a class="{klass} disabled"><div class="nav-label">{label}</div><div class="nav-title">─</div></a>'
    a = APPLIED_BY_ID[target_id]
    return (f'<a class="{klass}" href="{target_id}.html">'
            f'<div class="nav-label">{label}</div>'
            f'<div class="nav-title">{esc(target_id)}: {esc(a["title"])}</div>'
            '</a>')


# =====================================================================
#  応用問題ページ生成 (B 問題)
# =====================================================================
def build_applied_pages():
    order = [a["id"] for a in APPLIED_ENTRIES]
    for idx, entry in enumerate(APPLIED_ENTRIES):
        prev_id = order[idx - 1] if idx > 0 else None
        next_id = order[idx + 1] if idx + 1 < len(order) else None
        build_applied_page(entry, prev_id, next_id)


def build_applied_page(entry, prev_id, next_id):
    code_path = CODES_DIR / entry["code_file"]
    code = code_path.read_text(encoding="utf-8") if code_path.exists() else ""
    stripped_code = strip_python_comments(code) if code else ""
    chapter = CHAPTER_BY_ID[entry["chapter"]]

    tags_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in entry["tags"])

    prev_html = render_applied_nav(prev_id, "前の応用問題", "prev")
    next_html = render_applied_nav(next_id, "次の応用問題", "next")

    atc_url = atcoder_url(entry.get("atcoder"))
    atc_link = ''
    if atc_url:
        atc_link = (
            f'<a class="source-link" href="{atc_url}" target="_blank" '
            f'rel="noopener noreferrer">AtCoder で問題を見る{ICON_EXTERNAL}</a>'
        )
    else:
        atc_link = '<span style="color:#9ca3af">(AtCoder には掲載なし / 鉄則本 editorial 限定)</span>'

    description_meta = (
        f"{entry['id']}: {entry['title']} ─ 競技プログラミングの鉄則77 応用問題の Python 実装と日本語解説"
    )
    title = f"{entry['id']}: {entry['title']} | 鉄則77 Python解説 (応用問題)"

    html_out = base_head(title, description_meta, favicon_path="../assets/favicon.svg")
    html_out += '<link rel="stylesheet" href="../assets/css/styles.css" />\n'
    html_out += '</head><body>\n'
    html_out += common_header("..")

    ac_badge = render_ac_badge(effective_difficulty(entry['id']))
    ac_meta_html = ''
    if ac_badge:
        ac_meta_html = f'''
    <div class="meta-item">
      <strong>難易度</strong>
      <div style="margin-top:4px">{ac_badge}</div>
    </div>'''

    html_out += f'''
<main class="problem-detail">
  <nav class="breadcrumb">
    <a href="../index.html">問題一覧</a> /
    <span style="color: {chapter['color']}">{chapter['id']}章: {esc(chapter['title'])}</span> /
    <a href="{entry['base']}.html">{esc(entry['base'])}</a> /
    <strong>{esc(entry['id'])}</strong>
  </nav>

  <span class="id-pill id-pill--applied">{esc(entry['id'])}</span>
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
    </div>{ac_meta_html}
    <div class="meta-item">
      <strong>原典</strong>
      {applied_source_link_html(entry, chapter)}
    </div>
    <div class="meta-item">
      <strong>AtCoder</strong>
      {atc_link}
    </div>
  </div>
  {base_link_block_for_applied(entry['base'])}
  <div class="code-actions">
    <span class="file-label">{ICON_FILE}{esc(entry['code_file'])} ─ Python 3</span>
    <div class="actions">
      <button id="toggle-comments" type="button">{ICON_EYE}<span class="label">コメントを表示</span></button>
      <button id="copy-code" type="button">{ICON_CLIPBOARD}<span class="label">コードをコピー</span></button>
    </div>
  </div>
  {learning_panel_html(entry)}
  <pre class="line-numbers code-block-full" hidden><code class="language-python">{esc(code)}</code></pre>
  <pre class="line-numbers code-block-stripped"><code class="language-python">{esc(stripped_code)}</code></pre>

  <div class="nav-arrows">
    {prev_html}
    {next_html}
  </div>
</main>
'''
    html_out += footer_html()
    html_out += '''
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-core.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/line-numbers/prism-line-numbers.min.css" />
<script src="../assets/js/main.js"></script>
</body></html>
'''
    write_html(PROBLEMS_DIR / f"{entry['id']}.html", html_out)


# =====================================================================
#  実行
# =====================================================================
def main():
    print("Generating index.html...")
    build_index()
    print(f"Generating {len(ALL_ENTRIES)} problem pages...")
    build_problem_pages()
    print(f"Generating {len(APPLIED_ENTRIES)} applied (B) problem pages...")
    build_applied_pages()
    print("Done!")


if __name__ == "__main__":
    main()
