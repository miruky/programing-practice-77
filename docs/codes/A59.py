# =====================================================================
# A59: セグメント木 (区間和)
# ---------------------------------------------------------------------
# 【概要】A58 の "max" を "sum" に置き換えた版。
#   "1 pos x": A[pos] = x に更新
#   "2 l r":   A[l..r-1] の合計を出力
# 【アルゴリズム】演算子と単位元が違うだけで同じ構造。
#   - max → sum
#   - 単位元 -∞ → 0
#   - 結合演算 max(a,b) → a+b
# 【計算量】更新 O(log N), クエリ O(log N)
# =====================================================================

class segtree:
    def __init__(self, n):
        self.size = 1
        while self.size < n:
            self.size *= 2
        self.dat = [0] * (self.size * 2)

    def update(self, pos, x):
        pos += self.size
        self.dat[pos] = x
        while pos >= 2:
            pos //= 2
            # 親ノード = 子の和
            self.dat[pos] = self.dat[pos * 2] + self.dat[pos * 2 + 1]

    def query(self, l, r, a, b, u):
        if r <= a or b <= l:
            return 0           # 単位元 (加算なので 0)
        if l <= a and b <= r:
            return self.dat[u]
        m = (a + b) // 2
        answerl = self.query(l, r, a, m, u * 2)
        answerr = self.query(l, r, m, b, u * 2 + 1)
        return answerl + answerr


# --- 入力 -----------------------------------------------------------
N, Q = map(int, input().split())
queries = [list(map(int, input().split())) for _ in range(Q)]

# --- クエリ処理 ---------------------------------------------------
Z = segtree(N)
for q in queries:
    tp, *cont = q
    if tp == 1:
        pos, x = cont
        Z.update(pos - 1, x)
    if tp == 2:
        l, r = cont
        answer = Z.query(l - 1, r - 1, 0, Z.size, 1)
        print(answer)
