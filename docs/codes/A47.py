# # A47: 山登り法 (2-opt)
#
# ## 概要
#
# TSP の経路を局所探索 (山登り法) で改善する。
#
# ## アルゴリズム
#
# 山登り法 (Hill Climbing)
#   ランダムに区間 [l, r] を選び、その区間を反転 (2-opt move)。
#   反転後にスコア (経路長) が改善すれば採用、悪化したら戻す。
#
# ## 計算量
#
# 1 ループ O(N)。NUM_LOOPS 回繰り返す。
#
# ## ポイント
#
# Python ではループ回数が制限されるため PyPy3 推奨。
#
# ## 読み方の地図
#
# - 問題の型: ヒューリスティック / 山登り / TSP / 難易度目安: ★4
# - 要約: ランダムな区間反転で改善した場合のみ受理する局所探索。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 入力、前処理、判定・更新、出力の 4 ブロックに分けて読む。
# - 各変数・配列には「何を保存しているか」という役割があるので、名前だけで追わない。
# - 小さい入力例を 1 つ作り、ループが 1 回進むごとに値がどう変わるかを見る。

import random


class point2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dist(self, p):
        return ((self.x - p.x) ** 2 + (self.y - p.y) ** 2) ** 0.5


def get_score(n, points, P):
    """巡回路 P の合計距離"""
    score = 0
    for i in range(n):
        score += points[P[i]].dist(points[P[i + 1]])
    return score


def hill_climbing(n, points):
    # 初期解: 0,1,...,n-1,0 (順番通り)
    P = [i % n for i in range(n + 1)]
    current_score = get_score(n, points, P)
    NUM_LOOPS = 40000
    for t in range(NUM_LOOPS):
        # ランダムな区間 [l, r] を選ぶ
        l = random.randint(1, n - 1)
        r = random.randint(1, n - 1)
        if l > r:
            l, r = r, l
        # 区間を反転 (2-opt)
        P[l:r + 1] = reversed(P[l:r + 1])
        new_score = get_score(n, points, P)
        if current_score >= new_score:
            # 改善 → 採用
            current_score = new_score
        else:
            # 悪化 → 元に戻す
            P[l:r + 1] = reversed(P[l:r + 1])
    return P


# --- 入力 -----------------------------------------------------------
N = int(input())
points = [None] * N
for i in range(N):
    x, y = map(int, input().split())
    points[i] = point2d(x, y)

# --- 山登り法 ------------------------------------------------------
answer = hill_climbing(N, points)

# 1-indexed で出力
for i in answer:
    print(i + 1)
