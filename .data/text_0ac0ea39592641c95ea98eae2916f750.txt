# Monosemanticity（単義性）

**Monosemanticity（単義性）** とは、ニューラルネットワークの内部表現における 1 特徴 = 1 概念の対応関係。[Superposition](./superposition.md) の対極にある理想状態であり、[辞書学習による特徴分解](./dictionary-learning-feature-decomposition.md) パターンの目標。

## なぜ重要か

- ニューロンが単義的であれば、活性化パターンから「モデルが何を考えているか」を直接読み取れる
- 安全性に関連する概念（有害コンテンツ、欺瞞、バイアス）を個別に特定・介入できる
- モデルの内部状態に対する信頼性の高い監査が可能になる

## 達成の段階

| 段階 | 研究 | 規模 |
|------|------|------|
| 理論的理解 | Toy Models of Superposition (2022) | トイモデル |
| 1 層での実証 | Towards Monosemanticity (2023) | 1 層 Transformer |
| 本番モデルへの適用 | Scaling Monosemanticity (2024) | Claude 3 Sonnet |

## Polysemanticity との関係

現実のニューロンは多くの場合 polysemantic（多義的）である。Monosemanticity は個々のニューロンではなく、Sparse Autoencoder で見出される**特徴方向**において達成される。つまり、ニューロンの基底を入れ替えることで単義性を回復する。

## 関連概念

- [Superposition（重畳表現）](./superposition.md) — 単義性の障壁
- [Interpretability（解釈可能性）](./interpretability.md) — 単義性が前提条件
- [辞書学習による特徴分解](./dictionary-learning-feature-decomposition.md) — 単義性を達成する手法
- [回路追跡](./circuit-tracing.md) — 単義的な特徴を前提に計算を追跡

## ソース

- Towards Monosemanticity (Anthropic, 2023)
- Scaling Monosemanticity (Anthropic, 2024)

---
[tag-concept](./tag-concept.md) · [tag-interpretability](./tag-interpretability.md)
