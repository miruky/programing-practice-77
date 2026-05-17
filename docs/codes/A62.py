# =====================================================================
# A62: 深さ優先探索 (DFS) で連結判定
# ---------------------------------------------------------------------
# 【概要】無向グラフの頂点 1 から到達可能な頂点数で連結判定を行う。
# 【アルゴリズム】DFS (再帰版)
# 【計算量】O(N + M)
# 【注意】Python の再帰上限はデフォルト 1000。大きなグラフでは
#         setrecursionlimit を引き上げる必要がある。
# =====================================================================

import sys

sys.setrecursionlimit(120000)  # 再帰の深さ上限を引き上げる


def dfs(pos, G, visited):
    """頂点 pos を始点とする DFS で visited を更新"""
    visited[pos] = True
    for i in G[pos]:
        if visited[i] == False:
            dfs(i, G, visited)


# --- 入力 -----------------------------------------------------------
N, M = map(int, input().split())
edges = [list(map(int, input().split())) for _ in range(M)]

# --- 隣接リスト -----------------------------------------------------
G = [list() for _ in range(N + 1)]
for a, b in edges:
    G[a].append(b)
    G[b].append(a)

# --- DFS -----------------------------------------------------------
visited = [False] * (N + 1)
dfs(1, G, visited)

# --- 連結判定 ----------------------------------------------------
# 全頂点 (1〜N) が訪問済みなら連結
answer = True
for i in range(1, N + 1):
    if visited[i] == False:
        answer = False

if answer == True:
    print("The graph is connected.")
else:
    print("The graph is not connected.")
