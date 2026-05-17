# =====================================================================
# A57: ダブリング
# ---------------------------------------------------------------------
# 【概要】配列 A の各要素は「1 ステップ後の移動先」を表す。
#         開始位置 X から Y ステップ後の位置を Q 個のクエリに答える。
# 【アルゴリズム】ダブリング (Binary Lifting)
#   dp[d][i] = 位置 i から 2^d ステップ進んだ位置
#   遷移: dp[d][i] = dp[d-1][dp[d-1][i]]
#   Y を 2 進数表記し、ビットが立っている分だけ前進する。
# 【計算量】前計算 O(N log Y), クエリ O(log Y)
# =====================================================================

# --- 入力 -----------------------------------------------------------
N, Q = map(int, input().split())
A = list(map(int, input().split()))
queries = [list(map(int, input().split())) for _ in range(Q)]

# --- 前計算 (ダブリングテーブル) -----------------------------------
LEVELS = 30  # 2^30 > 10^9, 十分大きい
dp = [[None] * N for _ in range(LEVELS)]
for i in range(0, N):
    dp[0][i] = A[i] - 1  # 1-indexed の入力を 0-indexed に変換
for d in range(1, LEVELS):
    for i in range(0, N):
        dp[d][i] = dp[d - 1][dp[d - 1][i]]

# --- クエリ処理 ---------------------------------------------------
for X, Y in queries:
    current_place = X - 1  # 0-indexed に
    # Y の 2 進数表記の各桁について該当のステップ分前進する
    for d in range(29, -1, -1):
        if ((Y >> d) & 1) == 1:
            current_place = dp[d][current_place]
    print(current_place + 1)  # 1-indexed に戻して出力
