# # B06: Lottery (A06 応用 ─ 1 次元累積和)
#
# ## 概要
#
# 配列 A は各回のくじの結果 (1=アタリ, 0=ハズレ)。
#         Q 個の区間 [L,R] について、アタリとハズレの数を比べて
#         "win"/"draw"/"lose" を出力する。
#
# ## アルゴリズム
#
# アタリ用とハズレ用の累積和を別々に持ち、区間内の個数を
#                 引き算 (S[R] - S[L-1]) で O(1) 取得。
#
# ## 計算量
#
# 前計算 O(N) + クエリ O(Q)。
#
# ## 読み方の地図
#
# - 問題の型: 累積和 / 難易度目安: ★3
# - 要約: アタリ/ハズレの累積和を 2 つ持ち、区間内の勝敗を O(1) で判定する。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - S[i] は先頭から i 個分の合計。S[0]=0 を置くと端の例外処理が消える。
# - 区間和は「右端までの合計 - 左手前までの合計」と読む。
# - 入力が 1-indexed、Python 配列が 0-indexed なので添字の変換だけ注意する。

# --- 入力 -----------------------------------------------------------
N = int(input())
A = list(map(int, input().split()))
Q = int(input())
L = [None] * Q
R = [None] * Q
for i in range(Q):
    L[i], R[i] = map(int, input().split())

# --- アタリ / ハズレの累積和 ---------------------------------------
# Atari[i] = A[0..i-1] の中のアタリの個数 (1-indexed)
# Hazre[i] = A[0..i-1] の中のハズレの個数 (1-indexed)
Atari = [0] * (N + 1)
Hazre = [0] * (N + 1)
for i in range(1, N + 1):
    # 前の値を引き継ぎつつ、新しい A[i-1] の分だけ増やす。
    Atari[i] = Atari[i - 1] + (1 if A[i - 1] == 1 else 0)
    Hazre[i] = Hazre[i - 1] + (1 if A[i - 1] == 0 else 0)

# --- 質問処理 -------------------------------------------------------
# 区間 [L[i], R[i]] のアタリ数 = Atari[R[i]] - Atari[L[i]-1]
for i in range(Q):
    NumAtari = Atari[R[i]] - Atari[L[i] - 1]
    NumHazre = Hazre[R[i]] - Hazre[L[i] - 1]
    if NumAtari > NumHazre:
        print("win")
    elif NumAtari == NumHazre:
        print("draw")
    else:
        print("lose")
