# # B69: Black Company 2 (A69 応用 ─ 二部マッチング / 最大フロー)
#
# ## 概要
#
# N 人の社員が、24 時間のうちどの時間に出勤可能かが文字列で与え
#         られる。各社員は最大 10 時間勤務、各時間帯はちょうど M 人で
#         埋まる必要がある。可能か判定する。
#
# ## アルゴリズム
#
# 最大フローに帰着:
#                 源点 S → 社員 i: 容量 10
#                 社員 i → 時刻 j: 容量 1 (出勤可能なら)
#                 時刻 j → 終点 T: 容量 M
#         最大フローが M × 24 (必要総人時) と一致すれば Yes。
#
# ## 計算量
#
# Ford-Fulkerson は最悪 O(VE · F) だが本問は小規模で十分。
#
# ## 読み方の地図
#
# - 問題の型: グラフ / マッチング / 最大フロー / 難易度目安: ★5
# - 要約: 1 人 10 時間制約付きシフトを二部マッチング (最大フロー) で組む。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 残余グラフでは「まだ流せる容量」を見る。逆辺は流れを戻せる余地を表す。
# - s から t までの増加路を 1 本見つけ、流せる最小容量だけ流す、を繰り返す。
# - 二部マッチング系は「左側 → 右側」の辺に容量 1 を張る変換を先に理解する。

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
            return F
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

# --- グラフ構築 -----------------------------------------------------
# 頂点番号: 0..N-1 が社員、N..N+23 が時刻、N+24 が S、N+25 が T
S = N + 24
T = S + 1
g = FordFulkerson(T + 1)

for i in range(N):
    C = input()
    g.add_edge(S, i, 10)                  # 社員 i は最大 10 時間勤務
    for j, c in enumerate(C):
        if c == '1':
            g.add_edge(i, N + j, 1)       # 出勤可能な時刻と接続

for j in range(24):
    g.add_edge(N + j, T, M)               # 各時刻 j にちょうど M 人必要

# --- 判定 -----------------------------------------------------------
print("Yes" if g.max_flow(S, T) == M * 24 else "No")
