# RLHF（人間フィードバックによる強化学習）

**Reinforcement Learning from Human Feedback（RLHF）** とは、人間の評価・選好をフィードバック信号として AI モデルを強化学習する手法。ChatGPT や Claude など主要 LLM のアライメントに採用されている。

## 概要

事前学習済みモデルをそのまま使うと、人間の意図に沿わない出力（有害・不誠実・無益）をする可能性がある。RLHF はこの問題を、人間の判断を直接学習に組み込むことで解決する。

## 主要ステップ

### 1. SFT（Supervised Fine-Tuning）
人間が作成した高品質な例示データでモデルをファインチューニングする。

### 2. 報酬モデルの学習（Reward Modeling）
人間アノテーターが複数の回答を比較・ランク付けし、その選好データから報酬モデルを学習する。

### 3. RL 最適化（PPO など）
報酬モデルのスコアを報酬として、強化学習（主に PPO）でメインモデルを最適化する。

## 課題と派生手法

| 課題 | 対応手法 |
|------|---------|
| 報酬ハッキング（reward hacking） | KL ペナルティ、RLHF + Constitutional AI |
| アノテーターの偏り・スケールコスト | AI Feedback（RLAIF）、Constitutional AI |
| 人間選好の多様性 | 多様なアノテーター、価値観の明示化 |

## 関連概念

- [スケーラブルオーバーサイト](./scalable-oversight.md) — RLHF のスケール問題への対応
- [Constitutional AI](./constitutional-ai.md) — アノテーターコストを削減する派生手法
- [Interpretability](./interpretability.md) — 報酬モデルの内部表現理解

---
[tag-concept](./tag-concept.md) · [tag-rlhf](./tag-rlhf.md)
