# Scalable Oversight Wiki

AI エージェントに対する人間の監視（Oversight）を、品質を落とさずスケールさせるためのパターン集。

## コアコンセプト

- [スケーラブルオーバーサイト](./scalable-oversight.md) — このWikiの中心的な問い
- [エージェント自律性のスペクトラム](./agent-autonomy-spectrum.md) — L0〜L5 の自律性レベル

## パターン

| パターン | 解決する問題 |
|---------|------------|
| [Read-Write 境界](./read-write-boundary.md) | AI の自律実行による不可逆な副作用 |
| [並列専門エージェント](./parallel-specialist-agents.md) | 単一エージェントの死角と処理速度 |
| [ドメイン知識コード化](./domain-knowledge-as-code.md) | 暗黙知に依存した監査の属人化 |
| [外部化知識](./externalized-knowledge.md) | モデル再学習なしの知識更新 |
| [定量ヘルススコア](./quantitative-health-score.md) | AI 評価の不透明性と監視コスト |

## 事例

- [Claude Ads](./claude-ads.md) — マルチプラットフォーム広告監査の設計
- [Claude Code による Google 広告監査](./google-ads-audit.md) — 手動 4〜8 時間を 5 分に短縮
