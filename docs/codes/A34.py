# # A34: Grundy 数によるゲーム
#
# ## 概要
#
# 各山から X 個 or Y 個取るゲーム。複数山を XOR で合成。
#
# ## アルゴリズム
#
# Grundy 数
#   grundy[i] = "石 i 個の山" の Grundy 数 (= mex 値)
#   mex とは「遷移先に出ない最小の非負整数」のこと。
#   全山の Grundy 値の XOR が 0 でなければ先手必勝。
#
# ## 計算量
#
# O(maxA + N)
#
# ## ポイント
#
# 1 手で 1 山から 2 通りしか動かないので Grundy は {0,1,2} に収まる。
#
# ## 読み方の地図
#
# - 問題の型: ゲーム / Grundy / 難易度目安: ★4
# - 要約: 複数山の独立ゲームを Grundy 数の XOR で解く。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 整数 state を 2 進数として見て、各 bit が ON/OFF の集合を表す。
# - 1 << k は k 番目だけが ON の集合。OR は追加、XOR は反転として読む。
# - 状態数は 2^N。N が小さいからこそ成立する全探索 + DP/探索。

# --- 入力 -----------------------------------------------------------
N, X, Y = map(int, input().split())
A = list(map(int, input().split()))

# --- Grundy 数の計算 ---------------------------------------------
# Transit[k] = True ⇔ 遷移先に Grundy 値 k が存在する。
grundy = [None] * 100001
for i in range(100001):
    Transit = [False, False, False]
    if i >= X:
        Transit[grundy[i - X]] = True
    if i >= Y:
        Transit[grundy[i - Y]] = True

    # mex (Transit) を求める: 含まれない最小の非負整数
    if Transit[0] == False:
        grundy[i] = 0
    elif Transit[1] == False:
        grundy[i] = 1
    else:
        grundy[i] = 2

# --- 全山の Grundy 値を XOR して勝敗判定 -------------------------
XOR_Sum = 0
for i in range(N):
    XOR_Sum = (XOR_Sum ^ grundy[A[i]])

if XOR_Sum >= 1:
    print("First")
else:
    print("Second")
