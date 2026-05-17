# =====================================================================
# A68: 最大フロー (Ford-Fulkerson)
# ---------------------------------------------------------------------
# 【概要】頂点 1 から頂点 N までの最大フロー量を求める。
# 【アルゴリズム】Ford-Fulkerson 法
#   1. 残余グラフ G を構築。各辺 (a→b, 容量 c) に逆辺 (b→a, 容量 0) を追加。
#   2. DFS で増加路 (s から t への容量 >0 のパス) を 1 本見つけ、流す。
#   3. 流せなくなるまで繰り返す。
# 【計算量】Ford-Fulkerson は O(F * (N+M))。F は最大フロー値。
# =====================================================================

class maxflow_edge:
    """残余グラフの辺: to (相手), cap (残容量), rev (逆辺のインデックス)"""
    def __init__(self, to, cap, rev):
        self.to = to
        self.cap = cap
        self.rev = rev


def dfs(pos, goal, F, G, used):
    """pos から goal への増加路を 1 本探す。流せた量を返す"""
    if pos == goal:
        return F
    used[pos] = True
    for e in G[pos]:
        if e.cap > 0 and not used[e.to]:
            flow = dfs(e.to, goal, min(F, e.cap), G, used)
            if flow >= 1:
                # 残余グラフの容量を更新
                e.cap -= flow
                G[e.to][e.rev].cap += flow  # 逆辺の容量を増やす
                return flow
    return 0  # 増加路が見つからなかった


def maxflow(N, s, t, edges):
    """s から t への最大フロー量"""
    G = [list() for _ in range(N + 1)]
    for a, b, c in edges:
        # 辺と逆辺をペアで追加
        G[a].append(maxflow_edge(b, c, len(G[b])))
        G[b].append(maxflow_edge(a, 0, len(G[a]) - 1))

    INF = 10 ** 10
    total_flow = 0
    while True:
        used = [False] * (N + 1)
        F = dfs(s, t, INF, G, used)
        if F > 0:
            total_flow += F
        else:
            break
    return total_flow


# --- 入力 -----------------------------------------------------------
N, M = map(int, input().split())
edges = [list(map(int, input().split())) for _ in range(M)]

# --- 最大フローを計算 --------------------------------------------
answer = maxflow(N, 1, N, edges)
print(answer)
