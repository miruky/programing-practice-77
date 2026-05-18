# =====================================================================
# C16: Flights (力試し問題)
# ---------------------------------------------------------------------
# 【概要】N 個の空港と M 本のフライト (A→B、出発 S[i] 〜到着 T[i])。
#         全フライトを「時刻順に並べたグラフ」上で、最大いくつ乗り継げるか。
#         乗り継ぎには K 分の待機が必要。
# 【アルゴリズム】(空港, 時刻) を頂点として時刻順に並べ、フライト本体
#                 (S → T) と「同じ空港での待機」をエッジに持つ DAG を構築。
#                 トポロジカル順 (= 時刻順) で DP し最長路を求める。
# 【計算量】O((N + M) log(N + M))。
# =====================================================================

# --- 入力 -----------------------------------------------------------
N, M, K = map(int, input().split())
A = [0] * (M + 1)
B = [0] * (M + 1)
S = [0] * (M + 1)
T = [0] * (M + 1)
for i in range(1, M + 1):
    A[i], S[i], B[i], T[i] = map(int, input().split())
    T[i] += K                              # 到着 + 待機

# --- 頂点候補となる (時刻, 種別, 路線/空港番号) を時刻順に並べる -----
# 種別: 出発=2 / 到着=1 / 仮想 (空港の最初・最後)=0
# 出発の種別番号を大きくすることで、同時刻なら「到着 → 出発」の順になる。
List = []
for i in range(1, M + 1):
    List.append((S[i], 2, i))
    List.append((T[i], 1, i))
for i in range(1, N + 1):
    List.append((-1, 0, i))                # 空港の始点 (仮想)
    List.append((2_100_000_000, 0, i))     # 空港の終点 (仮想)
List.sort()

# --- 各路線・各空港に頂点番号を割り振る ----------------------------
VertS = [0] * (M + 1)                      # 路線 i の出発頂点
VertT = [0] * (M + 1)                      # 路線 i の到着頂点
Airport = [[] for _ in range(N + 1)]       # 空港 i に属する頂点番号列

for idx, (t, kind, who) in enumerate(List):
    v = idx + 1                            # 頂点番号は 1-indexed
    if kind == 2:
        VertS[who] = v
        Airport[A[who]].append(v)
    elif kind == 1:
        VertT[who] = v
        Airport[B[who]].append(v)
    else:
        Airport[who].append(v)

# --- グラフを構築 (「逆向き」: 各頂点 v は『この頂点に到達する辺』を持つ) -
LEN = len(List)
G = [[] for _ in range(LEN + 2)]

# 路線に対応する辺 (出発 → 到着、重み 1)
for i in range(1, M + 1):
    G[VertT[i]].append((VertS[i], 1))

# 空港で待つことに対応する辺 (時刻早い → 遅い、重み 0)
for i in range(1, N + 1):
    for j in range(len(Airport[i]) - 1):
        G[Airport[i][j + 1]].append((Airport[i][j], 0))

# 仮想始点 0 → 各空港の最初の頂点
# 仮想終点 LEN+1 ← 各空港の最後の頂点
for i in range(1, N + 1):
    G[Airport[i][0]].append((0, 0))
    G[LEN + 1].append((Airport[i][-1], 0))

# --- DP (頂点番号が時刻昇順なので 1, 2, ..., LEN+1 の順で OK) ------
dp = [0] * (LEN + 2)
for i in range(1, LEN + 2):
    for prev, w in G[i]:
        if dp[i] < dp[prev] + w:
            dp[i] = dp[prev] + w

# --- 出力 -----------------------------------------------------------
print(dp[LEN + 1])
