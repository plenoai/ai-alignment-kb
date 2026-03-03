# Claude Ads / Claude Code 広告監査

Claude Code を使ったマルチプラットフォーム広告監査の事例。[スケーラブルオーバーサイト](./scalable-oversight.md)のパターンを実装した代表的な事例。

**Source:**
- https://github.com/AgriciDaniel/claude-ads — マルチプラットフォーム監査スキル（OSS）
- https://stormy.ai/blog/claude-code-google-ads-audit-guide — Google Ads 特化の実践ガイド

**Date:** 2026-03-03

## 背景にある問題

広告管理は専門知識を要する反復作業で、人間の監視コストが高い：
- 不正クリックが広告クリックの約 5.1%（世界で年間 ~380 億ドルの損失）
- 最適化なしでは予算の最大 35% が無駄に
- ブランド検索広告の 20-30% が競合不在でオーガニック流入に課金
- 手動監査は 1 アカウントあたり 4〜8 時間を要する

## 解決策

### マルチプラットフォーム監査（claude-ads）

5 つの主要広告プラットフォームを横断して、190 項目のチェックを並列エージェントで自動監査し、0-100 の Health Score で結果を提示するシステム。

| プラットフォーム | チェック数 |
|-----------------|-----------|
| Google Ads | 74 |
| Meta/Facebook | 46 |
| LinkedIn Ads | 25 |
| TikTok Ads | 25 |
| Microsoft/Bing Ads | 20 |
| **合計** | **190** |

```
中央オーケストレーター
├── 専門サブスキル（プラットフォーム別、6 並列）
├── 参照データファイル（業界別ベンチマーク）
└── 業界別テンプレート（11 業種）
```

### Google Ads 特化の反復最適化ループ（"Ralph Wiggum" プロセス）

| 指標 | 手動 | Claude Code |
|------|------|-------------|
| 監査時間 | 4〜8 時間 | 5 分以内 |
| チェック数 | 人的エラーあり | 190+ 自動化 |

1. 高コスト・ゼロコンバージョンキーワードの特定
2. キーワードカニバリゼーションの検出
3. ネガティブキーワードリストを API 経由で自動コミット

→ 午後の作業が 30 秒のタスクに短縮

## 観察されたパターン

- [並列専門エージェント](./parallel-specialist-agents.md) — 6 エージェントが 5 プラットフォームを同時分析
- [ドメイン知識コード化](./domain-knowledge-as-code.md) — 190 のチェック項目として専門知識を構造化
- [外部化知識](./externalized-knowledge.md) — 参照データファイルをオンデマンドで読み込む RAG 設計
- [定量ヘルススコア](./quantitative-health-score.md) — Ads Health Score (0-100) + A〜F グレード
- [Read-Write 境界](./read-write-boundary.md) — 監査（読み取り）は自動、変更実行は人間確認後

---
[tag-case](./tag-case.md)
