# # A62: 深さ優先探索 (DFS) で連結判定
#
# ## 概要
#
# 無向グラフの頂点 1 から到達可能な頂点数で連結判定を行う。
#
# ## アルゴリズム
#
# DFS (再帰版)
#
# ## 計算量
#
# O(N + M)
#
# ## 注意
#
# Python の再帰上限はデフォルト 1000。大きなグラフでは
#         setrecursionlimit を引き上げる必要がある。
#
# ## 読み方の地図
#
# - 問題の型: グラフ / DFS / 難易度目安: ★2
# - 要約: DFS で連結性を判定する基本問題。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 入力をまず隣接リストやグリッドの隣接関係に変換している部分を見る。
# - visited や dist は「もう見たか」「何手で来たか」を記録するための配列。
# - DFS は深く進む、BFS は近い順に広がる。この違いだけ先に押さえる。

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
