# # A70 (補足版): XOR を使った高速版
#
# ## 概要
#
# A70 の状態 BFS の高速版。
#
# ## 高速化の鍵
#
# 「ビット k を反転する」 = 「2^k を XOR する」
#   つまり get_next 関数を単純な XOR 1 つに置き換えられる:
#     nex = pos ^ (1 << x) ^ (1 << y) ^ (1 << z)
#   さらにグラフを実体化せず、BFS 内で直接遷移を計算する。
#
# ## 計算量
#
# A70 と同じだが定数倍が約 1/5 と高速。
#
# ## 読み方の地図
#
# - 問題の型: グラフ / BFS / XOR / 難易度目安: ★4
# - 要約: ランプ反転を XOR 1 回で表現し、A70 を約 1/5 の実行時間に。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 整数 state を 2 進数として見て、各 bit が ON/OFF の集合を表す。
# - 1 << k は k 番目だけが ON の集合。OR は追加、XOR は反転として読む。
# - 状態数は 2^N。N が小さいからこそ成立する全探索 + DP/探索。

from collections import deque

# --- 入力 -----------------------------------------------------------
N, M = map(int, input().split())
A = list(map(int, input().split()))
actions = [list(map(lambda x: int(x) - 1, input().split())) for _ in range(M)]

# --- スタート・ゴール ----------------------------------------------
start = sum(A[i] * (2 ** i) for i in range(N))
goal = 2 ** N - 1

# --- BFS の初期化 -------------------------------------------------
dist = [-1] * (2 ** N)
dist[start] = 0
Q = deque()
Q.append(start)

# --- BFS (グラフを持たず、その場で遷移を計算) ---------------------
while len(Q) >= 1:
    pos = Q.popleft()
    for x, y, z in actions:
        # 3 ビット同時反転 = 3 つの 2^k を XOR
        nex = pos ^ (1 << x) ^ (1 << y) ^ (1 << z)
        if dist[nex] == -1:
            dist[nex] = dist[pos] + 1
            Q.append(nex)

print(dist[goal])
