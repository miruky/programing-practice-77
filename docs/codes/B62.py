# =====================================================================
# B62: Print a Path (A62 応用 ─ DFS で経路出力)
# ---------------------------------------------------------------------
# 【概要】無向グラフで、頂点 1 から頂点 N までの単純パスを 1 つ出力する。
# 【アルゴリズム】DFS で訪問しながらパスをスタックに積み、ゴールに着いたら
#                 そのまま出力して終了。バックトラック時は pop する。
# 【計算量】O(N + M)。
# 【注意】Python の再帰デフォルト上限は 1000 なので、N が大きいときは
#         setrecursionlimit を引き上げる。
# =====================================================================
import sys
sys.setrecursionlimit(1 << 20)

# --- 入力 -----------------------------------------------------------
N, M = map(int, input().split())
g = [[] for _ in range(N)]
for _ in range(M):
    A, B = map(int, input().split())
    A -= 1
    B -= 1
    g[A].append(B)
    g[B].append(A)

# --- DFS の状態 -----------------------------------------------------
visited = [False] * (N + 1)
path = []


def dfs(i: int):
    path.append(i)
    # ゴール (N-1) に到達 ─ そのままパスを出力して全プロセス終了
    if i == N - 1:
        for x in path:
            print(x + 1)                 # 1-indexed に戻す
        exit(0)

    # 通常の DFS
    visited[i] = True
    for j in g[i]:
        if not visited[j]:
            dfs(j)
    path.pop()                            # バックトラック


dfs(0)
