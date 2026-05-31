# # C19: Gasoline Optimization (力試し問題)
#
# ## 概要
#
# 長さ L の道に N 個のガソリンスタンドがあり、A[i] 地点で C[i] 円。
#         スタートから L まで進むとき、K 区間先のガソリンを今地点で
#         買えるとする (= 各位置で連続 K 区間の最小価格を支払う)。
#         全位置 1..L-K の最小価格の合計を求める。届かない区間があれば -1。
#
# ## アルゴリズム
#
# 各位置の最小価格を一次元配列に詰めて、セグメント木
#                 (区間最小値クエリ) を使い、各窓 [i, i+K) の min を取る。
#
# ## 計算量
#
# O(L log L)。
#
# ## 読み方の地図
#
# - 問題の型: データ構造 / セグメント木 / 難易度目安: ★5
# - 要約: 各位置の最小ガソリン価格をセグメント木 (RMQ) で取り、K 区間の min を合計する。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 葉が元配列、親が子 2 つの集約値。max / sum など、何を集約するかだけ変わる。
# - 更新は葉を書き換えてから親へ戻る。クエリは関係ない区間を捨てる。
# - 半開区間 [l,r) に統一すると、右端のズレを避けやすい。

# --- 入力 -----------------------------------------------------------
N, L, K = map(int, input().split())
A = [0] * (N + 1)
C = [0] * (N + 1)
for i in range(1, N + 1):
    A[i], C[i] = map(int, input().split())

# --- 各地点での値段の最小値 -----------------------------------------
INF = 1 << 60
Min_Value = [INF] * (L + 1)
for i in range(1, N + 1):
    if Min_Value[A[i]] > C[i]:
        Min_Value[A[i]] = C[i]

# --- セグメント木 (区間 min) ----------------------------------------
class SegmentTree:
    def __init__(self, n):
        self.siz = 1
        while self.siz < n:
            self.siz *= 2
        self.dat = [INF] * (self.siz * 2)

    def update(self, pos, x):
        pos = pos + self.siz - 1
        self.dat[pos] = x
        while pos >= 2:
            pos //= 2
            self.dat[pos] = min(self.dat[pos * 2], self.dat[pos * 2 + 1])

    # [l, r) の min を求める。u は現在のノード、[a, b) はそのカバー区間
    def query(self, l, r, a, b, u):
        if r <= a or b <= l:
            return INF
        if l <= a and b <= r:
            return self.dat[u]
        m = (a + b) // 2
        return min(self.query(l, r, a, m, u * 2),
                   self.query(l, r, m, b, u * 2 + 1))

Z = SegmentTree(L)
for i in range(1, L):
    Z.update(i, Min_Value[i])

# --- 各位置 i (=1..L-K) で [i, i+K) の min を加算 -------------------
Answer = 0
for i in range(1, L - K + 1):
    v = Z.query(i, i + K, 1, Z.siz + 1, 1)
    if v == INF:
        print(-1)
        break
    Answer += v
else:
    print(Answer)
