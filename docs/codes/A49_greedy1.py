# =====================================================================
# A49 (補足版): 貪欲法 (基本) ─ 37454 点
# ---------------------------------------------------------------------
# 【概要】各ターンで「次のスコアが大きくなる方」を貪欲に選択する解法。
# 【特徴】将来を考慮しないため最適性は弱いが、実装が単純。
# =====================================================================

# --- 入力 -----------------------------------------------------------
T = int(input())
P = [None] * T
Q = [None] * T
R = [None] * T
for i in range(T):
    P[i], Q[i], R[i] = map(int, input().split())
    P[i] -= 1  # 0-indexed に
    Q[i] -= 1
    R[i] -= 1

# 配列 A の初期化 (操作のたびに増減する 20 要素配列)
A = [0] * 20

# --- 貪欲法 ---------------------------------------------------------
CurrentScore = 0
for i in range(T):
    # パターン A を試したときのスコア
    ScoreA = CurrentScore
    PatA = [0] * 20
    for j in range(20):
        PatA[j] = A[j]
    PatA[P[i]] += 1
    PatA[Q[i]] += 1
    PatA[R[i]] += 1
    for j in range(20):
        if PatA[j] == 0:
            ScoreA += 1

    # パターン B を試したときのスコア
    ScoreB = CurrentScore
    PatB = [0] * 20
    for j in range(20):
        PatB[j] = A[j]
    PatB[P[i]] -= 1
    PatB[Q[i]] -= 1
    PatB[R[i]] -= 1
    for j in range(20):
        if PatB[j] == 0:
            ScoreB += 1

    # スコアが大きい方を採用
    if ScoreA >= ScoreB:
        print("A")
        CurrentScore = ScoreA
        for j in range(20):
            A[j] = PatA[j]
    else:
        print("B")
        CurrentScore = ScoreB
        for j in range(20):
            A[j] = PatB[j]
