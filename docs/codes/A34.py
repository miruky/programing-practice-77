# =====================================================================
# A34: Grundy 数によるゲーム
# ---------------------------------------------------------------------
# 【概要】各山から X 個 or Y 個取るゲーム。複数山を XOR で合成。
# 【アルゴリズム】Grundy 数
#   grundy[i] = "石 i 個の山" の Grundy 数 (= mex 値)
#   mex とは「遷移先に出ない最小の非負整数」のこと。
#   全山の Grundy 値の XOR が 0 でなければ先手必勝。
# 【計算量】O(maxA + N)
# 【ポイント】1 手で 1 山から 2 通りしか動かないので Grundy は {0,1,2} に収まる。
# =====================================================================

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
