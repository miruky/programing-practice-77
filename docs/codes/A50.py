# # A50: 山登り法 (numpy + 差分計算)
#
# ## 概要
#
# 配列 B 上のピラミッド型関数で配列 A を近似する。
#
# ## アルゴリズム
#
# 山登り法 + numpy のベクトル演算
#   - 各操作の (X, Y, H) を持つ。
#   - 「小さな変更」をランダムに行い、スコアが改善すれば採用、悪化なら戻す。
#   - 差分配列 delta を前計算して、加減を numpy で高速化する。
#
# ## 計算量
#
# 時間で打ち切り (TIME_LIMIT)。
#
# ## 読み方の地図
#
# - 問題の型: ヒューリスティック / numpy / 差分計算 / 難易度目安: ★5
# - 要約: 差分計算で評価を高速化し、numpy を活用するヒューリスティック。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 入力、前処理、判定・更新、出力の 4 ブロックに分けて読む。
# - 各変数・配列には「何を保存しているか」という役割があるので、名前だけで追わない。
# - 小さい入力例を 1 つ作り、ループが 1 回進むごとに値がどう変わるかを見る。

import numpy as np
import random
import time
import sys

# --- 定数・入力 ----------------------------------------------------
N = 100
Q = 1000
A = np.array([list(map(int, input().split())) for _ in range(N)])

# --- 初期解を生成 -------------------------------------------------
X = [random.randint(0, N - 1) for _ in range(Q)]
Y = [random.randint(0, N - 1) for _ in range(Q)]
H = [1] * Q
B = np.zeros((3 * N, 3 * N))  # 端を超えても安全な広めの配列
for i in range(Q):
    B[Y[i]][X[i]] += 1

# --- ピラミッド型関数の前計算 -------------------------------------
# H = i のとき影響する範囲を numpy 配列 delta[i] として持つ。
delta = [None] * (N + 1)
for i in range(1, N + 1):
    delta[i] = np.array([
        [max(i - abs(y) - abs(x), 0) for x in range(-i + 1, i)]
        for y in range(-i + 1, i)
    ])


def get_score():
    """現在のスコア (大きいほど良い)"""
    return 200000000 - np.absolute(A - B[N:2 * N, N:2 * N]).sum()


TIME_LIMIT = 5.4
current_score = get_score()
ti = time.time()

# --- 山登り法 -----------------------------------------------------
loops = 0
while time.time() - ti < TIME_LIMIT:
    # ランダムな変更を試す
    t = random.randint(0, Q - 1)
    old_x, new_x = X[t], X[t] + random.randint(-9, +9)
    old_y, new_y = Y[t], Y[t] + random.randint(-9, +9)
    old_h, new_h = H[t], H[t] + random.randint(-19, +19)
    if new_x < 0 or new_x >= N or new_y < 0 or new_y >= N or new_h <= 0 or new_h > N:
        continue

    # 変更を適用 (古い分を引いて新しい分を足す)
    B[N + Y[t] - H[t] + 1:N + Y[t] + H[t], N + X[t] - H[t] + 1:N + X[t] + H[t]] -= delta[H[t]]
    X[t], Y[t], H[t] = new_x, new_y, new_h
    B[N + Y[t] - H[t] + 1:N + Y[t] + H[t], N + X[t] - H[t] + 1:N + X[t] + H[t]] += delta[H[t]]

    new_score = get_score()

    if current_score < new_score:
        # 採用
        current_score = new_score
    else:
        # 不採用: 元に戻す
        B[N + Y[t] - H[t] + 1:N + Y[t] + H[t], N + X[t] - H[t] + 1:N + X[t] + H[t]] -= delta[H[t]]
        X[t], Y[t], H[t] = old_x, old_y, old_h
        B[N + Y[t] - H[t] + 1:N + Y[t] + H[t], N + X[t] - H[t] + 1:N + X[t] + H[t]] += delta[H[t]]
    loops += 1

# --- 出力 ----------------------------------------------------------
print(Q)
for i in range(Q):
    print(X[i], Y[i], H[i])
print("score =", current_score, file=sys.stderr)
print("loops =", loops, file=sys.stderr)
