# =====================================================================
# A49: ビームサーチ
# ---------------------------------------------------------------------
# 【概要】各ターンで操作 A または B を選び、最終的なスコアを最大化する。
# 【アルゴリズム】ビームサーチ
#   各ターンの "良さげな状態" を高々 WIDTH 個に絞って探索を進める。
#   貪欲法より広く、全探索より絞った中間的な戦略。
# 【計算量】O(T * WIDTH * log(WIDTH))
# =====================================================================

import copy


# 1 ターンの操作 (3 つのインデックス)
class round:
    def __init__(self, p, q, r):
        self.p = p
        self.q = q
        self.r = r


# 盤面の状態
class state:
    def __init__(self, n):
        self.score = 0      # スコア
        self.x = [0] * n    # 配列 X の値
        self.lastmove = '?'  # この状態に至った操作 ('A' or 'B')
        self.lastpos = -1    # 1 つ前の状態の位置 (経路復元用)


def beam_search(N, T, rounds):
    WIDTH = 10000
    # beam[i] = i 手目時点の候補状態リスト
    beam = [list() for _ in range(T + 1)]
    beam[0].append(state(N))

    for i in range(T):
        candidate = list()
        for j in range(len(beam[i])):
            # --- 操作 A の場合 ---
            sousa_a = copy.deepcopy(beam[i][j])
            sousa_a.lastmove = 'A'
            sousa_a.lastpos = j
            sousa_a.x[rounds[i].p] += 1
            sousa_a.x[rounds[i].q] += 1
            sousa_a.x[rounds[i].r] += 1
            # 配列 x のうち 0 の個数をスコアに足す
            sousa_a.score += sousa_a.x.count(0)

            # --- 操作 B の場合 ---
            sousa_b = copy.deepcopy(beam[i][j])
            sousa_b.lastmove = 'B'
            sousa_b.lastpos = j
            sousa_b.x[rounds[i].p] -= 1
            sousa_b.x[rounds[i].q] -= 1
            sousa_b.x[rounds[i].r] -= 1
            sousa_b.score += sousa_b.x.count(0)

            candidate.append(sousa_a)
            candidate.append(sousa_b)

        # スコアの高い順にソートし、上位 WIDTH 件だけを残す
        candidate.sort(key=lambda s: -s.score)
        beam[i + 1] = copy.deepcopy(candidate[:WIDTH])

    # --- 復元: スコア最大の終端から逆方向にたどる -------------------
    current_place = 0  # ビームは score 降順なので先頭が最良
    answer = [None] * T
    for i in range(T, 0, -1):
        answer[i - 1] = beam[i][current_place].lastmove
        current_place = beam[i][current_place].lastpos
    return answer


# --- 入力 -----------------------------------------------------------
T = int(input())
rounds = [None] * T
for i in range(T):
    p, q, r = map(int, input().split())
    rounds[i] = round(p - 1, q - 1, r - 1)  # 0-indexed に直す

# --- ビームサーチを実行 ---------------------------------------------
answer = beam_search(20, T, rounds)

for c in answer:
    print(c)
