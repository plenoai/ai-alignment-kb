---
name: deploy
description: cognee ナレッジグラフを再構築し、統合ビジュアライゼーションを生成して GitHub Pages にデプロイする
user_invocable: true
---

# Deploy スキル

AI Alignment KB のナレッジグラフを再構築し、GitHub Pages にデプロイする。

## 手順

1. **cognee ingest:** `uv run ingest.py` を実行して wiki ページを cognee に投入し、ナレッジグラフを構築する（cognify）。これは数分かかる。
2. **visualize:** `uv run visualize.py` を実行して cognee + wiki の統合グラフを `docs/index.html` に生成する。`--wiki` フラグは付けない（cognee 込みで生成する）。
3. **commit & push:** 変更された `.data/` ファイルと `docs/index.html` をコミットしてプッシュする。コミットメッセージは `Rebuild unified knowledge graph with cognee` とする。

## 注意事項

- ingest.py は cognee をリセット（prune）してから全ページを再投入するため、べき等である
- visualize.py は cognee グラフが空の場合 wiki リンクのみで生成する（フォールバック）
- `.data/` 配下のテキストファイルは cognee が生成する中間ファイル。変更があればコミットに含める
- `OPENAI_API_KEY` 環境変数が必要
