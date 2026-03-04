# Constitutional AI

**Constitutional AI（CAI）** とは、Anthropic が提案したアライメント手法。「原則（Constitution）」と呼ばれる文章リストを用いて、AI が自己批判・自己改善するループを構築する。人間アノテーターへの依存を削減しつつ、RLHF と同等以上のアライメントを実現する。

## 背景

RLHF は人間アノテーターが膨大な選好データを作成する必要があり、スケールコストが高い。Constitutional AI はこの問題に対し、AI 自身を判定者として活用する。

## 主要ステップ

### 1. SL-CAI（Supervised Learning）
1. 有害なプロンプトに対してモデルに回答させる
2. 「原則」に照らして自己批判させる
3. 批判を踏まえて回答を改訂させる
4. 改訂済み回答でファインチューニングする

### 2. RL-CAI（Reinforcement Learning）
1. 複数回答を AI 判定者（原則に基づく）に比較させる
2. その選好データで報酬モデルを学習する（RLAIF）
3. 報酬モデルで RL 最適化する

## Constitutional の例

> 「回答が有害・倫理的に問題ある場合、人間に危害を加えないように改訂してください」

原則は自然言語で記述するため、意図の表現が柔軟かつ監査しやすい。

## 関連概念

- [RLHF](./rlhf.md) — Constitutional AI の前身・比較対象
- [スケーラブルオーバーサイト](./scalable-oversight.md) — 人間監視をスケールする上位概念

---
[tag-concept](./tag-concept.md) · [tag-constitutional-ai](./tag-constitutional-ai.md)
