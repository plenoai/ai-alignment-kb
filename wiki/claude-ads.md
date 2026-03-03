# Claude Ads

Claude Code 向けのマルチプラットフォーム広告監査スキル。[スケーラブルオーバーサイト](./scalable-oversight.md)のパターンを実装した代表的な事例。

**Source:** https://github.com/AgriciDaniel/claude-ads
**Date:** 2026-03-03

## 概要

5 つの主要広告プラットフォームを横断して、190 項目のチェックを並列エージェントで自動監査し、0-100 の Health Score で結果を提示するシステム。

| プラットフォーム | チェック数 |
|-----------------|-----------|
| Google Ads | 74 |
| Meta/Facebook | 46 |
| LinkedIn Ads | 25 |
| TikTok Ads | 25 |
| Microsoft/Bing Ads | 20 |
| **合計** | **190** |

## アーキテクチャ

```
中央オーケストレーター
├── 専門サブスキル（プラットフォーム別、6 並列）
├── 参照データファイル（業界別ベンチマーク）
└── 業界別テンプレート（11 業種）
```

## 観察されたパターン

- [並列専門エージェント](./parallel-specialist-agents.md) — 6 エージェントが 5 プラットフォームを同時分析
- [ドメイン知識コード化](./domain-knowledge-as-code.md) — 190 のチェック項目として専門知識を構造化
- [外部化知識](./externalized-knowledge.md) — 参照データファイルをオンデマンドで読み込む RAG 設計
- [定量ヘルススコア](./quantitative-health-score.md) — Ads Health Score (0-100) + A〜F グレード
- [Read-Write 境界](./read-write-boundary.md) — 監査（読み取り）は自動、変更実行は人間確認後

## 関連

- [Claude Code による Google 広告監査](./google-ads-audit.md)
