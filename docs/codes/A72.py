# # A72: 行のビット全探索 + 列の貪欲法
#
# ## 概要
#
# H×W のグリッドを K 回の "行/列まるごと黒く塗る" 操作で塗り、
#         黒マスを最大化する。
#
# ## アルゴリズム
#
# H が小さいので、行の使い方は 2^H 通り全探索。
#   - 行に対する選び方を固定したら、残り操作数で塗る列を貪欲に選ぶ
#     (列ごとの白マス数が多いものから順に塗ると総黒マス数が最大)。
#
# ## 計算量
#
# O(2^H * H * W * log W)
#
# ## 読み方の地図
#
# - 問題の型: 全探索 / 貪欲 / 難易度目安: ★3
# - 要約: 行の選び方を 2^H 通り全探索し、列は貪欲に処理する。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 貪欲法は、何を基準に並べるか・どの候補を先に取るかが本体。
# - コードより先に「その選択をしても後で損しない理由」をコメントで確認する。
# - ソート後は、左から順に決めて戻らない構造になっているかを見る。

import itertools


def paint_row(H, W, d, remaining_steps):
    """残り操作回数 remaining_steps を列に消費して、最終的な黒マス数を返す"""
    # 各列に対して (白マスの個数, 列の番号) を作り、白が多い順にソート
    column = [
        ([d[i][j] for i in range(H)].count('.'), j)
        for j in range(W)
    ]
    column.sort(reverse=True)

    # 上位 remaining_steps 個を塗る
    for j in range(remaining_steps):
        idx = column[j][1]
        for i in range(H):
            d[i][idx] = '#'

    # 最終的な黒マス数
    return sum(map(lambda l: l.count('#'), d))


# --- 入力 -----------------------------------------------------------
H, W, K = map(int, input().split())
c = [input() for _ in range(H)]

# --- 行の塗り方を 2^H 通り全探索 ----------------------------------
# v[i] == 1: 行 i を黒く塗る
answer = 0
for v in itertools.product([0, 1], repeat=H):
    # 元のグリッドをコピー (mutable な 2 次元リスト)
    d = [list(c[i]) for i in range(H)]
    remaining_steps = K
    for i in range(H):
        if v[i] == 1:
            d[i] = ['#'] * W
            remaining_steps -= 1
    # 操作回数を超えていなければ、残りで列を貪欲に塗る
    if remaining_steps >= 0:
        subanswer = paint_row(H, W, d, remaining_steps)
        answer = max(answer, subanswer)

print(answer)
