# 競技プログラミングの鉄則77 ─ Python 実装ぜんぶ解説サイト

書籍『競技プログラミングの鉄則 〜アルゴリズムと思考力を高める 77 の技術〜』
に登場する **全 77 問 + 補足コード (合計 83 ファイル)** の Python 実装を、
日本語の解説コメント付きでブラウザから読めるようにする静的 Web サイトです。

- 📚 **対象書籍**: [競技プログラミングの鉄則](https://www.amazon.co.jp/dp/483997750X)
- 🔗 **原典コード**: [E869120/kyopro-tessoku](https://github.com/E869120/kyopro-tessoku)
- 🎨 **シンタックスハイライト**: [Prism.js](https://prismjs.com/) (tomorrow theme)
- 🌐 **デプロイ先**: GitHub Pages

---

## ✨ 特徴

- **モダンなダーク UI**: 章ごとに色分けされたカードレイアウト
- **シンタックスハイライト**: Prism.js で Python コードがカラフルかつ読みやすい
- **行ごとの日本語解説**: 各 `#` コメントに当サイトが書き足した解説を付加
- **検索 & 章フィルタ**: タイトル・タグ・要約から問題を絞り込める
- **問題間ナビゲーション**: 前/次の問題へワンクリックで移動
- **モバイル対応**: スマホでも快適に閲覧できるレスポンシブデザイン

## 📁 ディレクトリ構成

```
.
├── docs/                 ← GitHub Pages 公開ディレクトリ
│   ├── index.html        ← トップページ (章別カードリスト)
│   ├── assets/
│   │   ├── css/styles.css
│   │   └── js/main.js
│   ├── codes/            ← 解説コメント付き Python ソース (83 ファイル)
│   │   ├── A01.py
│   │   ├── ...
│   │   └── A77.py
│   └── problems/         ← 各問題の解説 HTML (83 ファイル)
│       ├── A01.html
│       ├── ...
│       └── A77.html
├── scripts/
│   ├── problems.json     ← 問題メタデータ (章・タイトル・タグ等)
│   └── build.py          ← 静的サイトジェネレーター
├── source-repo/          ← 原典 (kyopro-tessoku) のクローン
└── README.md             ← このファイル
```

## 🚀 GitHub Pages へのデプロイ手順

このリポジトリは `docs/` ディレクトリを公開するように構成されています。

1. このディレクトリを新しい GitHub リポジトリにプッシュする:
   ```bash
   cd "/Users/h_miruky/Library/Mobile Documents/com~apple~CloudDocs/develop/programming-practice-web-site"
   git init
   git add docs scripts README.md .gitignore
   git commit -m "Initial commit: kyopro-tessoku Python explainer site"
   git branch -M main
   git remote add origin git@github.com:<YOUR_GITHUB_USERNAME>/<REPO_NAME>.git
   git push -u origin main
   ```

2. GitHub の Web UI で **Settings → Pages** を開き、
   - **Source**: `Deploy from a branch`
   - **Branch**: `main` / `/docs`
   を選択して **Save** を押す。

3. 数分後に `https://<YOUR_GITHUB_USERNAME>.github.io/<REPO_NAME>/` で公開されます。

> 💡 **代替案 (GitHub Actions で自動デプロイ)**:
> `.github/workflows/pages.yml` などで GitHub Actions の "Deploy static content to Pages"
> アクションを使えば、main ブランチへの push 時に自動で公開できます。

## 🛠 ローカルで確認するには

```bash
cd docs
python3 -m http.server 8000
# ブラウザで http://localhost:8000 を開く
```

## 🔄 コンテンツの更新方法

1. `docs/codes/*.py` のコメントを編集する (各問題の Python 解説)。
2. `scripts/problems.json` を編集する (タイトル/タグ/要約の調整)。
3. `python3 scripts/build.py` を実行して HTML を再生成する。
4. 変更を commit & push する。

## ⚖ ライセンス・帰属

- **問題の原文と C++/Java/Python の原典コード**: [E869120/kyopro-tessoku](https://github.com/E869120/kyopro-tessoku)
  リポジトリに帰属します (作者: E869120 / 米田優峻 氏)。
- **本サイトで追加された日本語解説コメント・HTML/CSS/JS・ジェネレータースクリプト**:
  学習用途・私的閲覧用に作成された派生著作物です。書籍と原典リポジトリへの敬意を払い、
  原典を学習されたい方には書籍購入をおすすめします。
