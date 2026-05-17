# =====================================================================
# A66: Union-Find (素集合データ構造)
# ---------------------------------------------------------------------
# 【概要】2 種類のクエリ:
#   "1 u v": u と v を同じグループにする
#   "2 u v": u と v が同じグループか判定する
# 【アルゴリズム】Union-Find (Disjoint Set Union)
#   - 各頂点の "親" を持つ。根まで辿れば代表要素が分かる。
#   - "ランク (この実装ではサイズ) によるマージ" で計算量を抑える。
# 【計算量】1 操作 ほぼ O(α(N)) ≒ O(1)
# 【補足】経路圧縮を入れるとさらに高速になる。
# =====================================================================

class unionfind:
    def __init__(self, n):
        self.n = n
        self.par = [-1] * (n + 1)   # 親 (-1 なら根)
        self.size = [1] * (n + 1)   # 自分が根のときのグループサイズ

    def root(self, x):
        # 根まで辿る
        while self.par[x] != -1:
            x = self.par[x]
        return x

    def unite(self, u, v):
        rootu = self.root(u)
        rootv = self.root(v)
        if rootu != rootv:
            # 小さい方の木を大きい方に繋ぐ (Union by size)
            if self.size[rootu] < self.size[rootv]:
                self.par[rootu] = rootv
                self.size[rootv] += self.size[rootu]
            else:
                self.par[rootv] = rootu
                self.size[rootu] += self.size[rootv]

    def same(self, u, v):
        return self.root(u) == self.root(v)


# --- 入力 -----------------------------------------------------------
N, Q = map(int, input().split())
queries = [list(map(int, input().split())) for _ in range(Q)]

# --- クエリ処理 ---------------------------------------------------
uf = unionfind(N)
for tp, u, v in queries:
    if tp == 1:
        uf.unite(u, v)
    if tp == 2:
        if uf.same(u, v):
            print("Yes")
        else:
            print("No")
