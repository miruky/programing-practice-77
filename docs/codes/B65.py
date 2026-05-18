# =====================================================================
# B65: Road to Promotion Hard (A65 応用 ─ 木 DP)
# ---------------------------------------------------------------------
# 【概要】N 頂点の木で頂点 T を「社長」とする。各頂点 i について、
#         「i 以下にある部下のうち、i から最も遠い人までの距離 (= rank[i])」
#         を全頂点について求める。
# 【アルゴリズム】T を根とする DFS で、子の rank に +1 した値の最大を
#                 自分の rank に集約する典型木 DP。
# 【計算量】O(N)。
# =====================================================================
import sys
sys.setrecursionlimit(1 << 30)

# --- 入力 -----------------------------------------------------------
N, T = map(int, input().split())
T -= 1
g = [[] for _ in range(N)]
for _ in range(N - 1):
    A, B = map(int, input().split())
    A -= 1
    B -= 1
    g[A].append(B)
    g[B].append(A)

rank = [0] * N


# 親方向に戻らないように parent を引き回す再帰 DFS
def dfs(parent: int, i: int) -> int:
    for j in g[i]:
        if j == parent:
            continue
        r = dfs(i, j) + 1
        if rank[i] < r:
            rank[i] = r
    return rank[i]


dfs(-1, T)

# --- 出力 -----------------------------------------------------------
print(*rank)
