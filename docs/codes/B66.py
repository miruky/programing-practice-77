# =====================================================================
# B66: Typhoon (A66 応用 ─ Union-Find + クエリ逆順処理)
# ---------------------------------------------------------------------
# 【概要】無向グラフから順に辺を「壊す」クエリと、特定の 2 頂点が連結かを
#         問うクエリが混在する。各連結性クエリに答える。
# 【アルゴリズム】辺の削除は Union-Find と相性が悪いので、クエリを逆順に
#                 処理する: 最終状態から始めて、削除クエリは「辺を追加」、
#                 連結クエリは「root が同じか」を判定。
#                 答えは逆順に得られるので、最後に反転して出力する。
# 【計算量】O((N + M + Q) α(N))。α は Ackermann の逆関数で実用上ほぼ定数。
# =====================================================================

# --- 入力 (辺) -----------------------------------------------------
N, M = map(int, input().split())
edge = []
for _ in range(M):
    A, B = map(int, input().split())
    A -= 1
    B -= 1
    edge.append((A, B))

# --- 入力 (クエリ) -------------------------------------------------
Q = int(input())
query = [list(map(int, input().split())) for _ in range(Q)]

# --- 「最後まで残る辺」を判定 (削除クエリで消されない辺) -----------
last = [True] * M
for q in query:
    if q[0] == 1:
        q[1] -= 1
        last[q[1]] = False
    else:
        q[1] -= 1
        q[2] -= 1

# --- Union-Find (path halving + union by size) --------------------
uf = [-1] * N


def root(i: int) -> int:
    while True:
        if uf[i] < 0:
            return i
        if uf[uf[i]] < 0:
            return uf[i]
        uf[i] = uf[uf[i]]                # 経路 1/2 圧縮
        i = uf[i]


def unite(i: int, j: int):
    i = root(i)
    j = root(j)
    if i == j:
        return
    if uf[i] > uf[j]:
        i, j = j, i
    uf[i] += uf[j]
    uf[j] = i


# --- 最終状態に残る辺だけ最初に繋ぐ -------------------------------
ans = []
for i in range(M):
    if last[i]:
        A, B = edge[i]
        unite(A, B)

# --- クエリを逆向きに処理 ------------------------------------------
for q in reversed(query):
    if q[0] == 1:
        A, B = edge[q[1]]
        unite(A, B)                       # 削除を「辺の追加」として実行
    else:
        _, U, V = q
        ans.append("Yes" if root(U) == root(V) else "No")

# --- 答えも逆順なので、戻して出力 ---------------------------------
for s in reversed(ans):
    print(s)
