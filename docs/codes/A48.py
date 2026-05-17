# =====================================================================
# A48: 焼きなまし法 (Simulated Annealing)
# ---------------------------------------------------------------------
# 【概要】TSP に対する焼きなまし法。山登りより強力。
# 【アルゴリズム】焼きなまし法
#   山登り法を拡張し、悪化する解も確率 exp(ΔE / T) で受理する。
#   温度 T を時間とともに下げると、最初は探索的、後半は山登り的になる。
# 【計算量】1 ループ O(N)。
# =====================================================================

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
    NUM_LOOPS = 40000
    for t in range(NUM_LOOPS):
        # 反転する区間を選ぶ
        l = random.randint(1, n - 1)
        r = random.randint(1, n - 1)
        if l > r:
            l, r = r, l
        # 試しに反転
        P[l:r + 1] = reversed(P[l:r + 1])
        new_score = get_score(n, points, P)
        # 温度 T を時間と共に下げる
        T = 30 - 28 * (t / NUM_LOOPS)
        # 受理確率: 改善なら 1、悪化なら exp((current-new)/T)
        probability = math.exp(min((current_score - new_score) / T, 0))
        if random.random() < probability:
            current_score = new_score
        else:
            # 不採用: 元に戻す
            P[l:r + 1] = reversed(P[l:r + 1])
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
