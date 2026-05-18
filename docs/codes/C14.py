# =====================================================================
# C14: Commute Route (力試し問題)
# ---------------------------------------------------------------------
# 【概要】N 頂点 M 辺の重み付き無向グラフ。頂点 1 → N の最短経路の
#         少なくとも 1 本上に乗っている頂点の個数を求める。
# 【アルゴリズム】頂点 1 始点と頂点 N 始点の 2 回ダイクストラ法で
#                 dist1[v], distN[v] を求め、
#                 dist1[v] + distN[v] == dist1[N] となる v を数える。
# 【計算量】O((N + M) log N)。
# =====================================================================
from heapq import heappush, heappop

INF = 1 << 61

# --- 入力 -----------------------------------------------------------
N, M = map(int, input().split())
G = [[] for _ in range(N + 1)]
for _ in range(M):
    A, B, C = map(int, input().split())
    G[A].append((B, C))
    G[B].append((A, C))

# 始点 start からの最短距離をリストで返すダイクストラ
def dijkstra(start):
    cur = [INF] * (N + 1)
    cur[start] = 0
    Q = [(0, start)]
    while Q:
        d, x = heappop(Q)
        if d > cur[x]:
            continue
        for y, w in G[x]:
            nd = d + w
            if nd < cur[y]:
                cur[y] = nd
                heappush(Q, (nd, y))
    return cur

# --- 2 回ダイクストラ ---------------------------------------------
dist1 = dijkstra(1)
distN = dijkstra(N)

# --- 最短経路上の頂点を数える --------------------------------------
Answer = 0
for v in range(1, N + 1):
    if dist1[v] + distN[v] == dist1[N]:
        Answer += 1

# --- 出力 -----------------------------------------------------------
print(Answer)
