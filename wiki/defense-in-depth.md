# 多層防御 (Defense in Depth)

独立した複数の安全性検出レイヤーを冗長配置し、単一の防御層の突破がシステム全体の安全性を損なわないようにする。

## コンテキスト

単一の安全性手法では十分な保証が得られず、モデルの能力向上に伴い個々の防御が突破されるリスクがある場合。

## 問題

**いかなる単一の安全性手法も完全ではなく、モデルの能力向上により個別の防御が無効化されうる。**

## フォース

- 選択圧問題：同じバンパーへの反復テストが、そのバンパーを回避するモデルを進化させうる
- 曖昧なエビデンス：意図的欺瞞と訓練エラーの区別が困難
- リソース集約性：反復ごとに高価な計算リスタートが必要
- 能力天井：超人的推論能力を持つシステムに対するバンパー回避リスクの増大

## 解決策

**訓練→監査→警告サイン検出→根本原因特定→訓練修正→再訓練の反復ループを、独立した複数の防御レイヤーで構成する。**

| レイヤー | 手法 | 効果 |
|---------|------|------|
| 事前デプロイ監査 | 機械的解釈可能性、行動レッドチーミング、ハニーポット、活性化ファジング | 壊滅的不整合の事前検出 |
| デプロイ後モニタリング | リアルタイム異常検出、階層的要約、段階的ロールアウト | 運用中の逸脱検出 |
| 入出力分類器 | Constitutional Classifiers | ジェイルブレイク成功率 86%→4.4% |
| 迅速応答 | ジェイルブレイク拡散パターンの即時対応 | 1例から240倍の攻撃成功率削減 |

半ダースの独立バンパーで壊滅的不整合を検出可能。

## 結果コンテキスト

- 得られるもの：個別防御の突破が全体の安全性を損なわない耐障害性
- 失うもの：デプロイの速度とコスト（各レイヤーが推論/運用コストを加算）、完璧さの保証はなし

## 既知の使用例

- **OpenAI Agentic Governance（2023）:** 7 つのガバナンスプラクティス（タスク適合性評価、行動空間制約、デフォルト行動設定、可読性、自動モニタリング、帰属可能性、中断可能性）を明示的に「defense-in-depth」アプローチと位置づけ。 → [OpenAI エージェント型 AI ガバナンス事例](./openai-agentic-governance-case.md)
- [Putting up Bumpers](https://alignment.anthropic.com/2025/bumpers/) — 半ダースの独立バンパー戦略
- [Three Sketches of ASL-4 Safety Case Components](https://alignment.anthropic.com/2024/safety-cases/) — 機械的解釈可能性、AIコントロール、インセンティブ分析の3層
- [Constitutional Classifiers](https://www.anthropic.com/research/constitutional-classifiers) — 入出力分類器でジェイルブレイク成功率86%→4.4%
- [Rapid Response](https://arxiv.org/abs/2411.07494) — 1例から240倍の攻撃成功率削減

## 関連パターン

- [行動監査ゲーム](./behavioral-auditing-game.md)
- [階層的エージェント監視](./hierarchical-agent-oversight.md)
- [内部表現モニタリング](./internals-based-monitoring.md)
- [原則仕様化](./constitution-as-specification.md)
- [事前学習データ浄化](./pretraining-data-sanitization.md)

---
[tag-pattern](./tag-pattern.md) · [tag-scalable-oversight](./tag-scalable-oversight.md)
