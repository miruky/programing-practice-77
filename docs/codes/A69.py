# =====================================================================
# A69: 二部マッチング (最大フローへの帰着)
# ---------------------------------------------------------------------
# 【概要】N×N のグリッドで '#' のマス (i, j) について、行 i と列 j を
#         結ぶ二部グラフのマッチング数を求める。
# 【アルゴリズム】最大フローへの帰着
#   - 行 1..N と列 1..N をそれぞれ "左頂点" と "右頂点" にする。
#   - 仮想のソース s と シンク t を追加。
#   - s → 各行, 各列 → t, 各 '#' に対して 行 → 列 の辺を張る。
#   - すべての辺の容量を 1 にして最大フローを求めれば最大マッチング。
# 【計算量】Ford-Fulkerson で O(マッチング数 * (N+M))
# =====================================================================

class maxflow_edge:
    def __init__(self, to, cap, rev):
        self.to = to
        self.cap = cap
        self.rev = rev


def dfs(pos, goal, F, G, used):
    if pos == goal:
        return F
    used[pos] = True
    for e in G[pos]:
        if e.cap > 0 and not used[e.to]:
            flow = dfs(e.to, goal, min(F, e.cap), G, used)
            if flow >= 1:
                e.cap -= flow
                G[e.to][e.rev].cap += flow
                return flow
    return 0


def maxflow(N, s, t, edges):
    G = [list() for _ in range(N + 1)]
    for a, b, c in edges:
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
N = int(input())
C = [input() for _ in range(N)]

# --- 最大フローのグラフを構築 ----------------------------------
# 頂点番号:
#   1..N         : 左 (行)
#   N+1..2N      : 右 (列)
#   2N+1         : ソース s
#   2N+2         : シンク t
edges = []
for i in range(N):
    for j in range(N):
        if C[i][j] == '#':
            # 行 (i+1) → 列 (N+j+1) の辺
            edges.append((i + 1, N + j + 1, 1))
for i in range(N):
    edges.append((2 * N + 1, i + 1, 1))         # s → 行
    edges.append((N + i + 1, 2 * N + 2, 1))     # 列 → t

# --- 最大フロー = 最大マッチング数 -------------------------------
answer = maxflow(2 * N + 2, 2 * N + 1, 2 * N + 2, edges)
print(answer)
