# =====================================================================
# A50 (補足版): 焼きなまし法 (numpy)
# ---------------------------------------------------------------------
# 【概要】A50 の山登り法を焼きなまし法に拡張した版。
# 【特徴】
#   - 高さ H の探索範囲をスコアに応じて狭めるテクニックを採用。
#   - 採用確率に温度 T を導入し、悪化解も確率的に採用。
# =====================================================================
# ---------------------------------------------------------------------
# 【読み方の地図】
# - 問題の型: ヒューリスティック / 焼きなまし / numpy / 難易度目安: ★5
# - 要約: 山登りを焼きなまし法に拡張した A50 の高得点版。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
# 【このコードで特に見る場所】
# - 入力、前処理、判定・更新、出力の 4 ブロックに分けて読む。
# - 各変数・配列には「何を保存しているか」という役割があるので、名前だけで追わない。
# - 小さい入力例を 1 つ作り、ループが 1 回進むごとに値がどう変わるかを見る。
# ---------------------------------------------------------------------

import math
import numpy as np
import random
import time
import sys

# --- 定数・入力 ---------------------------------------------------
N = 100
Q = 1000
A = np.array([list(map(int, input().split())) for _ in range(N)])

# --- 初期解 -------------------------------------------------------
X = [random.randint(0, N - 1) for _ in range(Q)]
Y = [random.randint(0, N - 1) for _ in range(Q)]
H = [1] * Q
B = np.zeros((3 * N, 3 * N))
for i in range(Q):
    B[Y[i]][X[i]] += 1

# --- ピラミッド型差分配列の前計算 --------------------------------
delta = [None] * (N + 1)
for i in range(1, N + 1):
    delta[i] = np.array([
        [max(i - abs(y) - abs(x), 0) for x in range(-i + 1, i)]
        for y in range(-i + 1, i)
    ])


def get_score():
    return 200000000 - np.absolute(A - B[N:2 * N, N:2 * N]).sum()


TIME_LIMIT = 5.4
current_score = get_score()
ti = time.time()

# --- 焼きなまし法 -------------------------------------------------
loops = 0
while time.time() - ti < TIME_LIMIT:
    t = random.randint(0, Q - 1)
    # スコアが上がるにつれて、H の探索範囲を狭くする (収束時の微調整)
    h_limit = 14
    if current_score >= 199900000:
        h_limit = 1
    elif current_score >= 199500000:
        h_limit = 7
    old_x, new_x = X[t], X[t] + random.randint(-1, +1)
    old_y, new_y = Y[t], Y[t] + random.randint(-1, +1)
    old_h, new_h = H[t], H[t] + random.randint(-h_limit, +h_limit)
    if new_x < 0 or new_x >= N or new_y < 0 or new_y >= N or new_h <= 0 or new_h > N:
        continue

    # 変更適用
    B[N + Y[t] - H[t] + 1:N + Y[t] + H[t], N + X[t] - H[t] + 1:N + X[t] + H[t]] -= delta[H[t]]
    X[t], Y[t], H[t] = new_x, new_y, new_h
    B[N + Y[t] - H[t] + 1:N + Y[t] + H[t], N + X[t] - H[t] + 1:N + X[t] + H[t]] += delta[H[t]]

    new_score = get_score()

    # 温度 T を経過時間で下げ、確率的に受理
    temperature = 180.0 - 179.0 * (time.time() - ti) / TIME_LIMIT
    probability = math.exp(min((new_score - current_score) / temperature, 0))
    if random.random() < probability:
        current_score = new_score
    else:
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
