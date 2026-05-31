# # A49 (補足版): 貪欲法 (基本) ─ 37454 点
#
# ## 概要
#
# 各ターンで「次のスコアが大きくなる方」を貪欲に選択する解法。
#
# ## 特徴
#
# 将来を考慮しないため最適性は弱いが、実装が単純。
#
# ## 読み方の地図
#
# - 問題の型: ヒューリスティック / 貪欲 / 難易度目安: ★5
# - 要約: 本書 266ページ前半の貪欲解。37454 点。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 貪欲法は、何を基準に並べるか・どの候補を先に取るかが本体。
# - コードより先に「その選択をしても後で損しない理由」をコメントで確認する。
# - ソート後は、左から順に決めて戻らない構造になっているかを見る。

# --- 入力 -----------------------------------------------------------
T = int(input())
P = [None] * T
Q = [None] * T
R = [None] * T
for i in range(T):
    P[i], Q[i], R[i] = map(int, input().split())
    P[i] -= 1  # 0-indexed に
    Q[i] -= 1
    R[i] -= 1

# 配列 A の初期化 (操作のたびに増減する 20 要素配列)
A = [0] * 20

# --- 貪欲法 ---------------------------------------------------------
CurrentScore = 0
for i in range(T):
    # パターン A を試したときのスコア
    ScoreA = CurrentScore
    PatA = [0] * 20
    for j in range(20):
        PatA[j] = A[j]
    PatA[P[i]] += 1
    PatA[Q[i]] += 1
    PatA[R[i]] += 1
    for j in range(20):
        if PatA[j] == 0:
            ScoreA += 1

    # パターン B を試したときのスコア
    ScoreB = CurrentScore
    PatB = [0] * 20
    for j in range(20):
        PatB[j] = A[j]
    PatB[P[i]] -= 1
    PatB[Q[i]] -= 1
    PatB[R[i]] -= 1
    for j in range(20):
        if PatB[j] == 0:
            ScoreB += 1

    # スコアが大きい方を採用
    if ScoreA >= ScoreB:
        print("A")
        CurrentScore = ScoreA
        for j in range(20):
            A[j] = PatA[j]
    else:
        print("B")
        CurrentScore = ScoreB
        for j in range(20):
            A[j] = PatB[j]
