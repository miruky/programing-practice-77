#!/usr/bin/env python3
"""docs/codes/*.py の先頭 docstring を Markdown 風に再構造化する。

既存形式:
    # =====================================================================
    # A16: ダンジョン1 (基礎 DP)
    # ---------------------------------------------------------------------
    # 【概要】部屋 1 から部屋 N まで...
    # 【アルゴリズム】1 次元動的計画法
    #   dp[i] = ...
    # 【計算量】O(N)
    # 【実装メモ】...
    # =====================================================================
    # ---------------------------------------------------------------------
    # 【読み方の地図】
    # - 問題の型: DP / 難易度目安: ★2
    # - 要約: ...
    # ---------------------------------------------------------------------

新形式 (Markdown 化):
    # # A16: ダンジョン1 (基礎 DP)
    #
    # ## 概要
    # 部屋 1 から部屋 N まで...
    #
    # ## アルゴリズム
    # 1 次元動的計画法
    #
    # - `dp[i]` = ...
    #
    # ## 計算量
    # O(N)
    #
    # ## 実装メモ
    # ...
    #
    # ## 読み方の地図
    #
    # - 問題の型: DP / 難易度目安: ★2
    # - 要約: ...
"""
import re
from pathlib import Path

CODES_DIR = Path(__file__).resolve().parent.parent / "docs" / "codes"


def parse_old_docstring(code: str):
    """既存の # コメントブロックから (header_md_lines, code_body) を返す。

    ルール:
      - 先頭の # で始まる連続行を docstring とみなす。
      - 空行が来た時点で docstring 終了 (それ以降は body)。
      - 空行前にも import 等のコード行が来たら停止。
    """
    lines = code.split("\n")
    doc_lines = []  # 元の docstring の各行 (# を剥がしたもの)
    rest_idx = 0
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            body = stripped[1:]
            if body.startswith(" "):
                body = body[1:]
            doc_lines.append(body)
            rest_idx = i + 1
            continue
        # 空行またはコード行 → docstring 終了
        rest_idx = i
        break

    body_code = "\n".join(lines[rest_idx:]).lstrip("\n")
    return doc_lines, body_code


def to_markdown(doc_lines, problem_id):
    """既存の docstring を Markdown 風に再構造化する。"""
    if not doc_lines:
        return []

    # 1) ======= 罫線、------- 罫線を除去
    cleaned = []
    for ln in doc_lines:
        if re.fullmatch(r"[=\-]{3,}", ln.strip()):
            continue
        cleaned.append(ln)

    md_lines = []

    # 2) 最初の非空行はタイトル (= 「A16: ダンジョン1 (基礎 DP)」)。# を付けて H1 にする。
    title_set = False
    i = 0
    while i < len(cleaned) and cleaned[i].strip() == "":
        i += 1
    if i < len(cleaned):
        title = cleaned[i].strip()
        md_lines.append(f"# {title}")
        md_lines.append("")
        title_set = True
        i += 1

    # 3) 残りを 1 行ずつ処理:
    #    【XX】Y → ## XX  (新しい段落として開く)
    #    その後の行は本文 (空行までを集める)
    current_section_lines = []

    def flush_section():
        nonlocal current_section_lines
        if not current_section_lines:
            return
        # 「【読み方の地図】」セクションでは、各「- 」項目をそのままリスト化
        for ln in current_section_lines:
            md_lines.append(ln)
        md_lines.append("")
        current_section_lines = []

    while i < len(cleaned):
        ln = cleaned[i]
        s = ln.rstrip()
        # 【XXX】Y... を見出し化 (Y がインライン続きでも H2 → 本文に分割)
        m = re.match(r"^【([^】]+)】\s*(.*)$", s.lstrip())
        if m:
            flush_section()
            md_lines.append(f"## {m.group(1)}")
            md_lines.append("")
            rest = m.group(2)
            if rest:
                # 本文 1 行目
                current_section_lines.append(rest)
            i += 1
            continue

        # 既に箇条書き形式 (「- 」「* 」「1. 」「2. 」) はそのまま
        # それ以外で、コードっぽい行 (インデント 4+) は段落として残す
        if s == "":
            # 段落の区切り
            flush_section()
            i += 1
            continue

        current_section_lines.append(s)
        i += 1

    flush_section()

    # 末尾の空行を削る
    while md_lines and md_lines[-1].strip() == "":
        md_lines.pop()

    # 4) Markdown 化のフィニッシュ: 同じ識別子 (`dp[i]`, `A[i]` 等) を code 化したいが、
    #    過度な置換を避けるため、ここでは何もしない (元から `dp[i]` などは生で書かれている)。

    return md_lines


def rebuild_header_comments(md_lines):
    """Markdown 行リストを # プレフィックス付きの Python コメントに戻す。"""
    out = []
    for ln in md_lines:
        if ln == "":
            out.append("#")
        else:
            out.append(f"# {ln}")
    return out


def process_file(path: Path):
    code = path.read_text(encoding="utf-8")
    old_lines, body = parse_old_docstring(code)
    if not old_lines:
        # 元々 docstring が無い → 何もしない
        return False
    md = to_markdown(old_lines, path.stem)
    new_comments = rebuild_header_comments(md)
    # 結合: ヘッダコメント + 空行 1 つ + 本体
    new_text = "\n".join(new_comments) + "\n\n" + body
    # 末尾改行を 1 個にそろえる
    new_text = new_text.rstrip("\n") + "\n"
    path.write_text(new_text, encoding="utf-8")
    return True


def main():
    files = sorted(CODES_DIR.glob("*.py"))
    changed = 0
    for f in files:
        if process_file(f):
            changed += 1
    print(f"Rewrote {changed}/{len(files)} files")


if __name__ == "__main__":
    main()
