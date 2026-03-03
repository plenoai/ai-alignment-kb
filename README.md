# Scalable Oversight Framework

AI エージェントに対する人間の監視（Oversight）を、品質を落とさずスケールさせるための知識ベース。

## 構成

| ディレクトリ | 内容 |
|------------|------|
| [`app/patterns/`](./app/patterns/) | 再利用可能な設計パターン集 |
| [`packages/wiki/`](./packages/wiki/) | 概念・用語の解説 |
| [`packages/knowledge/`](./packages/knowledge/) | 事例・ソース素材 |

## パターン一覧

- [Read-Write 境界パターン](./app/patterns/read-write-boundary.md)
- [並列専門エージェントパターン](./app/patterns/parallel-specialist-agents.md)
- [ドメイン知識コード化パターン](./app/patterns/domain-knowledge-as-code.md)
- [外部化知識（RAG）パターン](./app/patterns/externalized-knowledge-rag.md)
- [定量ヘルススコアパターン](./app/patterns/quantitative-health-score.md)

## Wiki

- [スケーラブルオーバーサイトとは](./packages/wiki/scalable-oversight.md)
- [エージェント自律性のスペクトラム](./packages/wiki/agent-autonomy-spectrum.md)
