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
3. **commit & push:** 変更された `.data/` ファイルと `docs/index.html` をコミットしてプッシュする。コミットメッセージは `Rebuild unified knowledge graph with cognee` とする。`docs/` の変更は `.github/workflows/pages.yml` による GitHub Pages デプロイを自動的に開始する。

## 注意事項

- ingest.py は cognee をリセット（prune）してから全ページを再投入するため、べき等である
- visualize.py は cognee グラフが空の場合 wiki リンクのみで生成する（フォールバック）
- `.data/` 配下のテキストファイルは cognee が生成する中間ファイル。変更があればコミットに含める
- `OPENAI_API_KEY` 環境変数が必要
- GitHub Pages の Source は **GitHub Actions** を推奨する。従来の branch ビルドは GitHub 管理の `actions/upload-artifact@v4`（Node.js 20）を使い、非推奨警告を出す。Pages ワークフローは branch ビルドが残っていても、その管理ワークフローをキャンセルしてから `docs/` を GitHub Actions 経由でデプロイする。設定変更の権限がある場合は自動移行も試みる
