# =====================================================================
# B68: ALGO Express (A68 応用 ─ プロジェクト選択問題 / 最小カット)
# ---------------------------------------------------------------------
# 【概要】N 個の駅にスコア P[i] が与えられる (正/負あり)。M 個の有向制約
#         「a を選んだら b も選ぶ」がある。選び方の利益を最大化する。
# 【アルゴリズム】プロジェクト選択問題 → 最小カット (= 最大フロー) に帰着。
#                 - P[i] > 0: 源点 S → i に容量 P[i] (= 「i を選ばないと
#                   損する利益」)
#                 - P[i] < 0: i → 終点 T に容量 -P[i] (= 「i を選ぶときの
#                   コスト」)
#                 - 制約 a→b: a → b に容量 ∞
#         利益最大化値 = (P[i] > 0 の総和) − 最大フロー。
# 【計算量】Ford-Fulkerson は最悪 O(VE · 最大フロー) だが、本問は小さいので OK。
# =====================================================================

INF = 1 << 61


class Edge:
    def __init__(self, to, cap, rev):
        self.to = to
        self.cap = cap
        self.rev = rev


class FordFulkerson:
    def __init__(self, N):
        self.size = N
        self.g = [[] for _ in range(N)]

    def add_edge(self, a, b, c):
        g = self.g
        e = Edge(b, c, None)
        rev = Edge(a, 0, e)
        e.rev = rev
        g[a].append(e)
        g[b].append(rev)

    def dfs(self, i, goal, F):
        if i == goal:
            return F                      # ゴール到達 ─ 流せる量を返す
        self.visited[i] = True
        for e in self.g[i]:
            if e.cap == 0:
                continue
            if self.visited[e.to]:
                continue
            flow = self.dfs(e.to, goal, min(F, e.cap))
            if flow:
                e.cap -= flow
                e.rev.cap += flow
                return flow
        return 0

    def max_flow(self, s, t):
        ans = 0
        while True:
            self.visited = [False] * self.size
            F = self.dfs(s, t, INF)
            if F == 0:
                break
            ans += F
        return ans


# --- 入力 -----------------------------------------------------------
N, M = map(int, input().split())
P = list(map(int, input().split()))

# --- グラフ構築 -----------------------------------------------------
S = N                                      # 源点
T = N + 1                                  # 終点
g = FordFulkerson(T + 1)
offset = 0
for i in range(N):
    if P[i] >= 0:
        offset += P[i]                    # 全部選んだときの最大利益の上界
        g.add_edge(S, i, P[i])
    else:
        g.add_edge(i, T, -P[i])

# 制約: A を選んだら B も選ぶ ⇔ A→B 容量∞
for _ in range(M):
    A, B = map(int, input().split())
    A -= 1
    B -= 1
    g.add_edge(A, B, INF)

# --- 利益 = 上界 − 最小カット (= 最大フロー) -----------------------
print(offset - g.max_flow(S, T))
