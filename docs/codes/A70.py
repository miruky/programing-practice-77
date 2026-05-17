# =====================================================================
# A70: 状態 BFS (ランプ点灯ゲーム)
# ---------------------------------------------------------------------
# 【概要】N 個のランプ (ON/OFF) の状態を頂点に持ち、M 種類の操作で
#         全 ON 状態 (2^N - 1) にする最小手数を求める。
# 【アルゴリズム】状態空間 BFS
#   - 状態は 0..2^N-1 の整数で表せる (各ビットがランプ ON/OFF)
#   - 各操作は (X, Y, Z) のランプを同時反転 → 状態遷移を構築する
#   - スタート → ゴールへの最短手数を BFS で求める
# 【計算量】O(2^N * M)
# =====================================================================

from collections import deque

# --- 入力 -----------------------------------------------------------
N, M = map(int, input().split())
A = list(map(int, input().split()))
actions = [list(map(lambda x: int(x) - 1, input().split())) for _ in range(M)]


def get_next(pos, x, y, z):
    """頂点 pos の状態から、ランプ x, y, z を反転した状態を返す"""
    # 各ビットを取り出して状態列に
    state = [(pos // (2 ** i)) % 2 for i in range(N)]
    # 反転 (1 → 0, 0 → 1)
    state[x] = 1 - state[x]
    state[y] = 1 - state[y]
    state[z] = 1 - state[z]
    # 状態列を整数に戻す
    ret = 0
    for i in range(N):
        if state[i] == 1:
            ret += 2 ** i
    return ret


# --- グラフを構築 (状態 → 状態) ----------------------------------
G = [list() for _ in range(2 ** N)]
for i in range(2 ** N):
    for x, y, z in actions:
        nextstate = get_next(i, x, y, z)
        G[i].append(nextstate)

# --- スタート・ゴール ----------------------------------------------
start = 0
for i in range(N):
    if A[i] == 1:
        start += 2 ** i
goal = 2 ** N - 1  # 全 ON

# --- BFS -----------------------------------------------------------
dist = [-1] * (2 ** N)
dist[start] = 0
Q = deque()
Q.append(start)
while len(Q) >= 1:
    pos = Q.popleft()
    for nex in G[pos]:
        if dist[nex] == -1:
            dist[nex] = dist[pos] + 1
            Q.append(nex)

print(dist[goal])
