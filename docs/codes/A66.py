# # A66: Union-Find (素集合データ構造)
#
# ## 概要
#
# 2 種類のクエリ:
#   "1 u v": u と v を同じグループにする
#   "2 u v": u と v が同じグループか判定する
#
# ## アルゴリズム
#
# Union-Find (Disjoint Set Union)
#   - 各頂点の "親" を持つ。根まで辿れば代表要素が分かる。
#   - 経路圧縮 + サイズによるマージで、木が深くなりにくいようにする。
#
# ## 計算量
#
# 1 操作 ほぼ O(α(N)) ≒ O(1)
#
# ## 読み方の地図
#
# - 問題の型: グラフ / UnionFind / 難易度目安: ★3
# - 要約: 連結成分の管理ができる Union-Find のクエリ処理。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - root(x) は x の代表者を返す。同じ代表者なら同じ連結成分に属する。
# - unite(a,b) は 2 つのグループを結合するだけで、辺そのものを保存しているわけではない。
# - 削除クエリは苦手なので、必要なら時系列を逆順にして「追加」に変換して読む。

class unionfind:
    def __init__(self, n):
        self.n = n
        self.par = [-1] * (n + 1)   # 親 (-1 なら根)
        self.size = [1] * (n + 1)   # 自分が根のときのグループサイズ

    def root(self, x):
        # 根なら自分自身を返す。
        if self.par[x] == -1:
            return x

        # 経路圧縮: x から根までの途中ノードを、直接根へつなぎ直す。
        # 次回以降の root(x) がほぼ一瞬になる。
        self.par[x] = self.root(self.par[x])
        return self.par[x]

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
