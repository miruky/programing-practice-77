# =====================================================================
# A46: 貪欲法による TSP (Nearest Neighbor)
# ---------------------------------------------------------------------
# 【概要】N 都市を訪問する巡回経路 (TSP) の近似解を貪欲法で求める。
# 【アルゴリズム】貪欲法 (Nearest Neighbor Heuristic)
#   現在地から最も近い未訪問都市へ移動するだけのシンプルな手法。
# 【計算量】O(N^2)
# 【補足】最適解の保証はないが、初期解の生成にちょうどよい。
# =====================================================================
# ---------------------------------------------------------------------
# 【読み方の地図】
# - 問題の型: ヒューリスティック / 貪欲 / TSP / 難易度目安: ★3
# - 要約: 現在地から最も近い都市へ移動する貪欲法（TSP）。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
# 【このコードで特に見る場所】
# - 貪欲法は、何を基準に並べるか・どの候補を先に取るかが本体。
# - コードより先に「その選択をしても後で損しない理由」をコメントで確認する。
# - ソート後は、左から順に決めて戻らない構造になっているかを見る。
# ---------------------------------------------------------------------

# 2 次元の点を表すクラス
class point2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # ユークリッド距離
    def dist(self, p):
        return ((self.x - p.x) ** 2 + (self.y - p.y) ** 2) ** 0.5


def play_greedy(n, points):
    """貪欲法で巡回経路 P を返す (0-indexed)"""
    current_place = 0
    visited = [False] * n
    visited[0] = True
    P = [0]
    for i in range(1, n):
        mindist = 10 ** 10
        min_id = -1
        # 未訪問の中で最も近い都市を探す
        for j in range(n):
            if not visited[j] and mindist > points[current_place].dist(points[j]):
                mindist = points[current_place].dist(points[j])
                min_id = j
        visited[min_id] = True
        P.append(min_id)
        current_place = min_id
    P.append(0)  # 最後はスタートへ戻る
    return P


# --- 入力 -----------------------------------------------------------
N = int(input())
points = [None] * N
for i in range(N):
    x, y = map(int, input().split())
    points[i] = point2d(x, y)

# --- 貪欲法による経路を求める ---------------------------------------
answer = play_greedy(N, points)

# 1-indexed に直して出力
for i in answer:
    print(i + 1)
