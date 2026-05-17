# =====================================================================
# A58: セグメント木 (区間最大値)
# ---------------------------------------------------------------------
# 【概要】配列に対して
#   "1 pos x": A[pos] = x に更新
#   "2 l r":   A[l..r-1] の最大値を出力
#   のクエリを処理する。
# 【アルゴリズム】セグメント木 (Segment Tree)
#   各ノードに対応区間の最大値を保持し、更新・クエリ共に O(log N)。
# 【計算量】更新 O(log N), クエリ O(log N)
# =====================================================================

class segtree:
    """0-indexed の RMQ セグメント木"""

    def __init__(self, n):
        # n 以上の最小の 2 のべき乗を size とする
        self.size = 1
        while self.size < n:
            self.size *= 2
        # 葉の数 size、内部ノードを含む配列サイズ 2*size
        self.dat = [0] * (self.size * 2)

    # 位置 pos の値を x に更新する
    def update(self, pos, x):
        pos += self.size  # 葉のインデックスに変換
        self.dat[pos] = x
        # 親方向へ値を更新していく
        while pos >= 2:
            pos //= 2
            self.dat[pos] = max(self.dat[pos * 2], self.dat[pos * 2 + 1])

    # 区間 [l, r) の最大値を返す (a, b は現在ノードの担当区間、u はノード番号)
    def query(self, l, r, a, b, u):
        if r <= a or b <= l:
            return -1000000000   # 重ならない
        if l <= a and b <= r:
            return self.dat[u]   # 完全に含まれる
        m = (a + b) // 2
        answerl = self.query(l, r, a, m, u * 2)
        answerr = self.query(l, r, m, b, u * 2 + 1)
        return max(answerl, answerr)


# --- 入力 -----------------------------------------------------------
N, Q = map(int, input().split())
queries = [list(map(int, input().split())) for _ in range(Q)]

# --- クエリ処理 ---------------------------------------------------
Z = segtree(N)
for q in queries:
    tp, *cont = q
    if tp == 1:
        pos, x = cont
        Z.update(pos - 1, x)  # 1-indexed → 0-indexed
    if tp == 2:
        l, r = cont
        # 半開区間 [l-1, r-1)
        answer = Z.query(l - 1, r - 1, 0, Z.size, 1)
        print(answer)
