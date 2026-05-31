# # A55: 集合(順序付き) クエリ処理
#
# ## 概要
#
# 整数集合に対する 3 種類のクエリを処理する:
#   "1 x": 集合に x を追加 (重複は無視)
#   "2 x": 集合から x を削除
#   "3 x": 集合内で x 以上の最小要素を出力 (なければ -1)
#
# ## データ構造
#
# Python では順序付き集合の標準ライブラリがないため、
#   ソート済みリスト (sortedcontainers.SortedList) や、
#   組込み set + bisect を組合せて実装する。
#   ここでは "並び順をキープしたリスト + bisect" のアプローチを採る。
#
# ## 計算量
#
# 挿入/削除 O(N) (リストの shift)、検索 O(log N)
#
# ## 別解
#
# sortedcontainers.SortedList を使うと挿入/削除も O(log N)。
#
# ## 補足
#
# 原典リポジトリには Python 実装がなく、C++ 版 (set) を
#   参考に当サイトで Python に書き起こした。
#
# ## 読み方の地図
#
# - 問題の型: データ構造 / 二分探索 / 難易度目安: ★3
# - 要約: lower_bound 相当を含む順序付き集合のクエリ処理。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 二分探索は値を探すというより、条件が NG から OK に切り替わる境目を探す。
# - bisect_left は「その値を入れてもソートが崩れない一番左の位置」を返す。
# - LIS や座標圧縮では、配列そのものではなく順位・置き場所を管理する。

import bisect

# --- 入力 -----------------------------------------------------------
Q = int(input())
queries = [list(map(int, input().split())) for _ in range(Q)]

# --- ソート済みリストでの実装 ---------------------------------------
S = []
for tp, x in queries:
    if tp == 1:
        # 挿入位置を二分探索 → 重複なら何もしない
        pos = bisect.bisect_left(S, x)
        if pos >= len(S) or S[pos] != x:
            S.insert(pos, x)
    elif tp == 2:
        pos = bisect.bisect_left(S, x)
        if pos < len(S) and S[pos] == x:
            S.pop(pos)
    elif tp == 3:
        # x 以上の最小要素 = lower_bound に相当
        pos = bisect.bisect_left(S, x)
        if pos == len(S):
            print(-1)
        else:
            print(S[pos])
