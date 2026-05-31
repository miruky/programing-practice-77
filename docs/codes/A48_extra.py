# # A48 (補足版): 焼きなまし法 (差分計算で高速化)
#
# ## 概要
#
# A48 と同じ問題に対する高速版。
#
# ## 高速化のポイント
#
#   2-opt の反転は経路長の "差分" だけ計算できる:
#     - 削除される 2 辺: P[l-1]-P[l], P[r]-P[r+1]
#     - 追加される 2 辺: P[l-1]-P[r], P[l]-P[r+1]
#   採用が決まるまで実際の反転は行わず、O(1) で評価する。
#
# ## 読み方の地図
#
# - 問題の型: ヒューリスティック / 焼きなまし / 難易度目安: ★4
# - 要約: 区間反転前後のスコア差分のみを計算し高速化した実装。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 入力、前処理、判定・更新、出力の 4 ブロックに分けて読む。
# - 各変数・配列には「何を保存しているか」という役割があるので、名前だけで追わない。
# - 小さい入力例を 1 つ作り、ループが 1 回進むごとに値がどう変わるかを見る。

import math
import random


class point2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dist(self, p):
        return ((self.x - p.x) ** 2 + (self.y - p.y) ** 2) ** 0.5


def get_score(n, points, P):
    score = 0
    for i in range(n):
        score += points[P[i]].dist(points[P[i + 1]])
    return score


def simulated_annealing(n, points):
    P = [i % n for i in range(n + 1)]
    current_score = get_score(n, points, P)
    NUM_LOOPS = 150000
    for t in range(NUM_LOOPS):
        l = random.randint(1, n - 1)
        r = random.randint(1, n - 1)
        if l > r:
            l, r = r, l
        # 差分計算: 反転前後で変化する 2 つの辺だけ計算する
        new_score = current_score
        new_score -= points[P[l - 1]].dist(points[P[l]])
        new_score -= points[P[r]].dist(points[P[r + 1]])
        new_score += points[P[l - 1]].dist(points[P[r]])
        new_score += points[P[l]].dist(points[P[r + 1]])

        T = 30 - 28 * (t / NUM_LOOPS)
        probability = math.exp(min((current_score - new_score) / T, 0))
        if random.random() < probability:
            # 採用が決まった時のみ、実際に区間を反転する
            P[l:r + 1] = reversed(P[l:r + 1])
            current_score = new_score
    return P


# --- 入力 -----------------------------------------------------------
N = int(input())
points = [None] * N
for i in range(N):
    x, y = map(int, input().split())
    points[i] = point2d(x, y)

answer = simulated_annealing(N, points)
for i in answer:
    print(i + 1)
