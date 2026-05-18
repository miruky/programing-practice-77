# =====================================================================
# A67: 最小全域木 (クラスカル法)
# ---------------------------------------------------------------------
# 【概要】N 頂点 M 辺の重み付き連結グラフから、すべての頂点を繋ぐ
#         辺の重みの合計が最小となる "最小全域木 (MST)" を求める。
# 【アルゴリズム】クラスカル法
#   1. 辺を重みの昇順にソート。
#   2. 各辺について、両端が異なる連結成分なら採用 (Union-Find で管理)。
#   ループや余計な辺はスキップされ、N-1 本選ぶと MST が完成。
# 【計算量】O(M log M)
# =====================================================================
# ---------------------------------------------------------------------
# 【読み方の地図】
# - 問題の型: グラフ / MST / クラスカル / 難易度目安: ★4
# - 要約: 辺を短い順にソートし Union-Find で MST を構築。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
# 【このコードで特に見る場所】
# - root(x) は x の代表者を返す。同じ代表者なら同じ連結成分に属する。
# - unite(a,b) は 2 つのグループを結合するだけで、辺そのものを保存しているわけではない。
# - 削除クエリは苦手なので、必要なら時系列を逆順にして「追加」に変換して読む。
# ---------------------------------------------------------------------

class unionfind:
    """A66 と同じ Union-Find 実装"""
    def __init__(self, n):
        self.n = n
        self.par = [-1] * (n + 1)
        self.size = [1] * (n + 1)

    def root(self, x):
        while self.par[x] != -1:
            x = self.par[x]
        return x

    def unite(self, u, v):
        rootu = self.root(u)
        rootv = self.root(v)
        if rootu != rootv:
            if self.size[rootu] < self.size[rootv]:
                self.par[rootu] = rootv
                self.size[rootv] += self.size[rootu]
            else:
                self.par[rootv] = rootu
                self.size[rootu] += self.size[rootv]

    def same(self, u, v):
        return self.root(u) == self.root(v)


# --- 入力 -----------------------------------------------------------
N, M = map(int, input().split())
edges = [list(map(int, input().split())) for _ in range(M)]

# --- 辺を重みの昇順にソート --------------------------------------
edges.sort(key=lambda x: x[2])

# --- クラスカル法 --------------------------------------------------
uf = unionfind(N)
answer = 0
for a, b, c in edges:
    # 違うグループならこの辺を MST に追加
    if not uf.same(a, b):
        uf.unite(a, b)
        answer += c

print(answer)
