# # C20: Mayor's Challenge (力試し問題 / ヒューリスティック)
#
# ## 概要
#
# N×N グリッドの K 個の区画を L 個の連結な特別区にまとめる。
#         各区画には人口 A、面積 B が与えられ、特別区ごとの (合計 A, 合計 B)
#         の最小/最大比をスコアとする。スコアを最大化する。
#
# ## アルゴリズム
#
# Union-Find で「小さい連結成分から併合」する貪欲法で
#                 初期解を作り、その後「ランダムに 1 区画の色を変えてみる」
#                 焼きなまし法で改善する。
#
# ## 計算量
#
# 貪欲 O(K² + KE)、焼きなまし 0.95 秒のループ。
#
# ## 注意
#
# Python は C++ より遅いため、C++ 版より得点が下がる可能性あり。

import random
import time
# ---------------------------------------------------------------------
# 【読み方の地図】
# - 問題の型: ヒューリスティック / 焼きなまし / UnionFind / 難易度目安: ★5
# - 要約: K 区画を L 個の連結特別区にまとめる問題を、貪欲 + 焼きなまし法で解く。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
# 【このコードで特に見る場所】
# - root(x) は x の代表者を返す。同じ代表者なら同じ連結成分に属する。
# - unite(a,b) は 2 つのグループを結合するだけで、辺そのものを保存しているわけではない。
# - 削除クエリは苦手なので、必要なら時系列を逆順にして「追加」に変換して読む。
# ---------------------------------------------------------------------


# --- Union-Find ------------------------------------------------------
class UnionFind:
    def __init__(self, n):
        self.par = [-1] * (n + 1)
        self.siz = [1] * (n + 1)

    def root(self, x):
        while self.par[x] != -1:
            x = self.par[x]
        return x

    def unite(self, u, v):
        ru, rv = self.root(u), self.root(v)
        if ru == rv:
            return
        if self.siz[ru] < self.siz[rv]:
            self.par[ru] = rv
            self.siz[rv] += self.siz[ru]
        else:
            self.par[rv] = ru
            self.siz[ru] += self.siz[rv]

    def same(self, u, v):
        return self.root(u) == self.root(v)


# --- 入力 -----------------------------------------------------------
N, K, L = map(int, input().split())
A = [0] * (K + 1)
B = [0] * (K + 1)
for i in range(1, K + 1):
    A[i], B[i] = map(int, input().split())
C = [[0] * (N + 1)]
for i in range(1, N + 1):
    C.append([0] + list(map(int, input().split())))

# --- 隣接グラフを構築 (区画 ↔ 区画) ---------------------------------
G = [set() for _ in range(K + 1)]
for i in range(1, N + 1):
    for j in range(1, N + 1):
        if i != N and C[i][j] != 0 and C[i + 1][j] != 0 and C[i][j] != C[i + 1][j]:
            G[C[i][j]].add(C[i + 1][j])
            G[C[i + 1][j]].add(C[i][j])
        if j != N and C[i][j] != 0 and C[i][j + 1] != 0 and C[i][j] != C[i][j + 1]:
            G[C[i][j]].add(C[i][j + 1])
            G[C[i][j + 1]].add(C[i][j])
G = [list(s) for s in G]                  # 後で index アクセスするためリスト化

answer = [0] * (K + 1)

# 連結性チェック用 DFS
visited = [False] * (K + 1)

def dfs(pos, color):
    stack = [pos]
    while stack:
        v = stack.pop()
        if visited[v]:
            continue
        visited[v] = True
        for nv in G[v]:
            if answer[nv] == color and not visited[nv]:
                stack.append(nv)


def get_score():
    # 各特別区が連結かつ存在するか
    for i in range(1, K + 1):
        visited[i] = False
    for i in range(1, L + 1):
        pos = -1
        for j in range(1, K + 1):
            if answer[j] == i:
                pos = j
        if pos == -1:
            return 0.0
        dfs(pos, i)
    for i in range(1, K + 1):
        if not visited[i]:
            return 0.0

    # スコア計算
    p = [0] * (L + 1)
    q = [0] * (L + 1)
    for i in range(1, K + 1):
        p[answer[i]] += A[i]
        q[answer[i]] += B[i]
    pmin, pmax = min(p[1:L + 1]), max(p[1:L + 1])
    qmin, qmax = min(q[1:L + 1]), max(q[1:L + 1])
    if pmax == 0 or qmax == 0:
        return 0.0
    return min(pmin / pmax, qmin / qmax)


# --- 貪欲法で初期解 (小さい連結成分から K - L 回併合) --------------
uf = UnionFind(K)
for _ in range(K - L):
    min_size = 10 ** 9
    v1, v2 = -1, -1
    for j in range(1, K + 1):
        for v in G[j]:
            if not uf.same(j, v):
                s1 = uf.siz[uf.root(j)]
                s2 = uf.siz[uf.root(v)]
                if min_size > s1 + s2:
                    min_size = s1 + s2
                    v1, v2 = j, v
    if v1 != -1:
        uf.unite(v1, v2)

# --- Union-Find の根を色番号に変換 ---------------------------------
roots = sorted(set(uf.root(i) for i in range(1, K + 1)))
root_to_color = {r: idx + 1 for idx, r in enumerate(roots)}
for i in range(1, K + 1):
    answer[i] = root_to_color[uf.root(i)]

# --- 山登り / 焼きなまし法で改善 (0.95 秒) -------------------------
TIME_LIMIT = 0.95
ti = time.time()
current_score = get_score()
while time.time() - ti < TIME_LIMIT:
    # 隣接する別色の頂点を選んで色を交換してみる
    v = random.randint(1, K)
    if not G[v]:
        continue
    x = answer[G[v][random.randint(0, len(G[v]) - 1)]]
    if answer[v] == x:
        continue
    old_x = answer[v]
    answer[v] = x
    new_score = get_score()

    # 焼きなまし: 確率で悪化も受理
    rv = (random.random() + 0.5)         # ≒ [0.5, 1.5]
    rv /= 1.5
    temp = 0.0040 - 0.0039 * ((time.time() - ti) / TIME_LIMIT)
    import math
    if new_score != 0.0 and rv < math.exp((new_score - current_score) / max(temp, 1e-9)):
        current_score = new_score
    else:
        answer[v] = old_x

# --- 出力 -----------------------------------------------------------
print("\n".join(str(answer[i]) for i in range(1, K + 1)))
