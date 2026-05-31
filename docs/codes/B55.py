# # B55: Difference (A55 応用 ─ 順序付き集合)
#
# ## 概要
#
# クエリ列が与えられ、type=1 は「集合に x を追加」、type=2 は
#         「集合内の x との差の最小値」を答える。
#
# ## アルゴリズム
#
# 「x 以下の最大要素」「x 以上の最小要素」を取得できる
#                 順序付き集合 (Sorted Set) を使い、(x - 前者), (後者 - x)
#                 の min を答える。Python 標準には無いので平方分割の
#                 SortedSet ライブラリを使用。
#
# ## 計算量
#
# 各クエリ O(√N) (バケット平方分割の場合)。
#
# ## 読み方の地図
#
# - 問題の型: データ構造 / 順序集合 / 難易度目安: ★4
# - 要約: 順序付き集合で、ある値 x に最も近い要素との差を答える。
# - まず入力ブロックで、どの変数・配列に何が入るかを確認する。
# - 次に中心となる配列・状態・データ構造の意味を 1 行で言語化する。
# - 最後に答えを出す式や出力ループだけを、入力例と照らして追う。
#
# ## このコードで特に見る場所
#
# - 入力、前処理、判定・更新、出力の 4 ブロックに分けて読む。
# - 各変数・配列には「何を保存しているか」という役割があるので、名前だけで追わない。
# - 小さい入力例を 1 つ作り、ループが 1 回進むごとに値がどう変わるかを見る。

# ----- SortedSet (平方分割ベース) ----------------------------------
# 出典: https://github.com/tatyam-prime/SortedSet
# 競プロでは「std::set 互換」として広く使われている定番ライブラリ。
import math
from bisect import bisect_left, bisect_right
from typing import Generic, Iterable, Iterator, TypeVar, Union, List
T = TypeVar('T')


class SortedSet(Generic[T]):
    BUCKET_RATIO = 50
    REBUILD_RATIO = 170

    def _build(self, a=None) -> None:
        "バケットに均等分割する"
        if a is None:
            a = list(self)
        size = self.size = len(a)
        bucket_size = int(math.ceil(math.sqrt(size / self.BUCKET_RATIO)))
        self.a = [a[size * i // bucket_size: size * (i + 1) // bucket_size] for i in range(bucket_size)]

    def __init__(self, a: Iterable[T] = []) -> None:
        "ソート済みかつ重複なしなら O(N), そうでなければ O(N log N) で構築"
        a = list(a)
        if not all(a[i] < a[i + 1] for i in range(len(a) - 1)):
            a = sorted(set(a))
        self._build(a)

    def __iter__(self) -> Iterator[T]:
        for i in self.a:
            for j in i:
                yield j

    def __reversed__(self) -> Iterator[T]:
        for i in reversed(self.a):
            for j in reversed(i):
                yield j

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return "SortedSet" + str(self.a)

    def __str__(self) -> str:
        s = str(list(self))
        return "{" + s[1: len(s) - 1] + "}"

    def _find_bucket(self, x: T) -> List[T]:
        "x が含まれるべきバケットを返す"
        for a in self.a:
            if x <= a[-1]:
                return a
        return a

    def __contains__(self, x: T) -> bool:
        if self.size == 0:
            return False
        a = self._find_bucket(x)
        i = bisect_left(a, x)
        return i != len(a) and a[i] == x

    def add(self, x: T) -> bool:
        "追加 / O(√N)"
        if self.size == 0:
            self.a = [[x]]
            self.size = 1
            return True
        a = self._find_bucket(x)
        i = bisect_left(a, x)
        if i != len(a) and a[i] == x:
            return False
        a.insert(i, x)
        self.size += 1
        if len(a) > len(self.a) * self.REBUILD_RATIO:
            self._build()
        return True

    def discard(self, x: T) -> bool:
        "削除 / O(√N)"
        if self.size == 0:
            return False
        a = self._find_bucket(x)
        i = bisect_left(a, x)
        if i == len(a) or a[i] != x:
            return False
        a.pop(i)
        self.size -= 1
        if len(a) == 0:
            self._build()
        return True

    def lt(self, x: T) -> Union[T, None]:
        "x より小さい最大要素"
        for a in reversed(self.a):
            if a[0] < x:
                return a[bisect_left(a, x) - 1]

    def le(self, x: T) -> Union[T, None]:
        "x 以下の最大要素"
        for a in reversed(self.a):
            if a[0] <= x:
                return a[bisect_right(a, x) - 1]

    def gt(self, x: T) -> Union[T, None]:
        "x より大きい最小要素"
        for a in self.a:
            if a[-1] > x:
                return a[bisect_right(a, x)]

    def ge(self, x: T) -> Union[T, None]:
        "x 以上の最小要素"
        for a in self.a:
            if a[-1] >= x:
                return a[bisect_left(a, x)]

    def __getitem__(self, x: int) -> T:
        if x < 0:
            x += self.size
        if x < 0:
            raise IndexError
        for a in self.a:
            if x < len(a):
                return a[x]
            x -= len(a)
        raise IndexError

    def index(self, x: T) -> int:
        ans = 0
        for a in self.a:
            if a[-1] >= x:
                return ans + bisect_left(a, x)
            ans += len(a)
        return ans

    def index_right(self, x: T) -> int:
        ans = 0
        for a in self.a:
            if a[-1] > x:
                return ans + bisect_right(a, x)
            ans += len(a)
        return ans
# ----- SortedSet ここまで -------------------------------------------

# --- 入力 -----------------------------------------------------------
Q = int(input())
Query = [tuple(map(int, input().split())) for _ in range(Q)]

# --- クエリ処理 -----------------------------------------------------
INF = 1 << 61
# 番兵 -INF, +INF を入れておくと、x より小さい/大きい数が無くても
# 探索が崩れず実装が楽になる。
Set = SortedSet([-INF, INF])

for type, x in Query:
    if type == 1:
        Set.add(x)
    if type == 2:
        if len(Set) == 2:                # 番兵 2 つ ⇒ 実要素が無い
            print(-1)
            continue
        v1 = Set.le(x)                    # x 以下の最大
        v2 = Set.ge(x)                    # x 以上の最小
        print(min(x - v1, v2 - x))
