# =====================================================================
# B58: Jumping (A58 応用 ─ DP + セグメント木 (RMQ))
# ---------------------------------------------------------------------
# 【概要】座標 X[0..N-1] (昇順) の上を、「現在地から距離 [L, R] の範囲」に
#         一回でジャンプできるカエルがいる。X[0] から X[N-1] まで最少何回で
#         着くかを求める (届かなければ INF)。
# 【アルゴリズム】dp[i] = i 番目の点に着くための最少ジャンプ数。
#         dp[i] = min{ dp[j] : x_j ∈ [X[i]-R, X[i]-L] } + 1
#         X はソート済みなので、座標範囲 → 配列添字範囲は二分探索で求まる。
#         区間最小は RMQ 用セグメント木で O(log N)。
# 【計算量】O(N log N)。
# =====================================================================
import bisect

INF = 1 << 61
siz = 1 << 17                              # セグメント木の葉数 (2 の冪)
dat = [INF] * (siz * 2)                    # 1-indexed セグメント木の本体


# seg[i] に v を代入。経路を上に辿って min を更新。
def update(i: int, v: int) -> None:
    i += siz
    dat[i] = v
    while i > 1:
        i >>= 1
        dat[i] = min(dat[i * 2], dat[i * 2 + 1])


# seg[l..r-1] の最小値を取得。
def query(l: int, r: int) -> int:
    l += siz
    r += siz
    answer = INF
    while l < r:
        if l & 1:
            if answer > dat[l]:
                answer = dat[l]
            l += 1
        if r & 1:
            r -= 1
            if answer > dat[r]:
                answer = dat[r]
        l >>= 1
        r >>= 1
    return answer


# --- 入力 -----------------------------------------------------------
N, L, R = map(int, input().split())
X = list(map(int, input().split()))
dp = [0] * N

# --- DP -------------------------------------------------------------
# dp[0] = 0 (スタート地点)
update(0, 0)
for i in range(1, N):
    x = X[i]
    # 座標範囲 [x-R, x-L] にある点の添字範囲を二分探索
    posL = bisect.bisect_left(X, x - R)
    posR = bisect.bisect_right(X, x - L)
    dp[i] = query(posL, posR) + 1
    update(i, dp[i])

print(dp[-1])
