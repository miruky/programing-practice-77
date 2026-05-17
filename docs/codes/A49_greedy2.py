# =====================================================================
# A49 (補足版): 貪欲法 (評価関数版) ─ 40978 点
# ---------------------------------------------------------------------
# 【概要】"配列の絶対値の合計が小さいほど将来 0 になりやすい" という
#         発想を取り入れた評価関数を使う。
# 【特徴】将来性を加味した貪欲法でスコアが大きく改善する。
# =====================================================================

# --- 入力 -----------------------------------------------------------
T = int(input())
P = [None] * T
Q = [None] * T
R = [None] * T
for i in range(T):
    P[i], Q[i], R[i] = map(int, input().split())
    P[i] -= 1
    Q[i] -= 1
    R[i] -= 1

# 配列 A の初期化
A = [0] * 20

# --- 貪欲法 (評価関数: 絶対値和を最小化) ---------------------------
for i in range(T):
    # パターン A の場合 (絶対値の合計を計算)
    ScoreA = 0
    PatA = [0] * 20
    for j in range(20):
        PatA[j] = A[j]
    PatA[P[i]] += 1
    PatA[Q[i]] += 1
    PatA[R[i]] += 1
    for j in range(20):
        ScoreA += abs(PatA[j])

    # パターン B の場合
    ScoreB = 0
    PatB = [0] * 20
    for j in range(20):
        PatB[j] = A[j]
    PatB[P[i]] -= 1
    PatB[Q[i]] -= 1
    PatB[R[i]] -= 1
    for j in range(20):
        ScoreB += abs(PatB[j])

    # スコアの小さい方 (絶対値が小さい方) を採用
    if ScoreA <= ScoreB:
        print("A")
        CurrentScore = ScoreA
        for j in range(20):
            A[j] = PatA[j]
    else:
        print("B")
        CurrentScore = ScoreB
        for j in range(20):
            A[j] = PatB[j]
