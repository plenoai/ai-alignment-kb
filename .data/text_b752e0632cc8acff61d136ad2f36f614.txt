# AIフィードバックによるスケーラブル監視 (Scalable Oversight via AI Feedback)

人間のフィードバックをAI生成フィードバック（RLAIF、自動分類器、教師なしエリシテーション）で代替・補強し、監視のスケーラビリティボトルネックを解消する。

## コンテキスト

人間のアノテーション・監視がスケールの限界に達し、モデルの能力が人間の評価能力を超え始める場合。

## 問題

**人間の監視は品質が高いがスケールしない。超人的AIの監視に人間だけでは対応できない。**

## フォース

- 監視のスケーラビリティ vs 品質：AIフィードバックは人間の品質に達しない可能性
- 超人的モデルの監視：人間が正解を判定できないタスクでの監視は根本的困難
- 自己言及的リスク：AI生成のフィードバックでAIを訓練するクローズドループが品質劣化やバイアス増幅を招きうる
- コスト vs 安全性：安全性モニタリングは推論コストを増加させ、プロダクション環境で削除されるリスク

## 解決策

**AI生成フィードバック（RLAIF）・教師なしエリシテーション・人間-AI協調・正直さエリシテーションを組み合わせ、人間の監視品質を維持しつつスケーラビリティを確保する。**

| 手法 | 概要 | 効果 |
|------|------|------|
| RLAIF | AI評価者が原則に基づき候補応答を比較し、選好モデルを訓練 | Constitutional AIの基盤 |
| 教師なしエリシテーション | モデル自身が自己生成ラベルデータでファインチューニング | GSM8k検証・TruthfulQAで人間監視ベースライン同等以上 |
| 人間-AI協調 | 非専門家が不完全なLMと対話しながら専門家レベルの判断に近づく | MMLU・QuALITYで両者単独を上回る |
| 正直さエリシテーション | 「Goals mix」技法で不整合モデルから告白を引き出す | 監査に十分な強度 |

## 結果コンテキスト

- 得られるもの：人間の監視品質を維持しつつスケーラブルなフィードバックループ、経済的に実行可能な安全性モニタリング
- 失うもの：人間の判断の独立性（AIフィードバックへの依存リスク）、現実的課題（非真実特徴、不均衡データ、不確実性）下での信頼性

## 既知の使用例

- [Constitutional AI](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback) — RLAIF原型
- [Unsupervised Elicitation](https://alignment.anthropic.com/2025/unsupervised-elicitation/) — Haiku 3.5を人間監視版を超えるアシスタントに訓練
- [Measuring Progress on Scalable Oversight](https://www.anthropic.com/research/measuring-progress-on-scalable-oversight-for-large-language-models) — 人間-AI協調の実証
- [3 Challenges and 2 Hopes](https://alignment.anthropic.com/2026/challenges-hopes/) — 現実的条件下で「どの技法も信頼性を維持できない」
- [Honesty Elicitation](https://alignment.anthropic.com/2025/honesty-elicitation/) — 不正直モデルからの告白引き出し

## 関連パターン

- [原則仕様化](./constitution-as-specification.md)
- [報酬シグナル腐敗](./reward-signal-corruption.md)
- [思考連鎖の忠実性ギャップ](./cot-faithfulness-gap.md)
- [検証天井](./verification-ceiling.md)

---
[tag-pattern](./tag-pattern.md) · [tag-interpretability](./tag-interpretability.md)
