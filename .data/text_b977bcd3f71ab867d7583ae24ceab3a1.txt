# Superposition（重畳表現）

**Superposition（重畳表現）** とは、ニューラルネットワークが持つ次元数（ニューロン数）よりも多くの特徴を同時に符号化する現象。個々のニューロンが複数の無関係な概念を担う（polysemanticity）原因であり、Interpretability の根本障壁となる。

## メカニズム

モデルは特徴をニューロンに 1:1 対応させるのではなく、高次元空間内の**方向**として表現する。特徴の発火がまばら（sparse）であるほど、互いの干渉を抑えながら多くの特徴を詰め込める。

### Superposition を支配する要因

| 要因 | 影響 |
|------|------|
| 特徴のスパース性 | スパースなほど多くの特徴を重畳可能 |
| 特徴の重要度 | 重要な特徴ほど優先的に表現される |
| 特徴間の相関 | 類似特徴は近くに配置され干渉しやすい |
| モデルの次元数 | 次元が増えると重畳の必要性が減る |

## アライメントとの関係

- **隠れた能力**: モデルが表面上は見えない内部表現を持つ可能性がある（deceptive alignment のリスク）
- **監査の困難**: ニューロン単位の検査では安全性の検証ができない
- **解決の方向**: [辞書学習による特徴分解](./dictionary-learning-feature-decomposition.md) で重畳を解消し、検査可能にする

## 関連概念

- [Monosemanticity（単義性）](./monosemanticity.md) — Superposition の対極。1 特徴 = 1 概念
- [Interpretability（解釈可能性）](./interpretability.md) — Superposition が主要障壁
- [辞書学習による特徴分解](./dictionary-learning-feature-decomposition.md) — Superposition を解消する手法

## ソース

- Toy Models of Superposition (Anthropic, 2022)
- Distributed Representations: Composition & Superposition (Anthropic, 2023)
- Superposition, Memorization, and Double Descent (Anthropic, 2023)

---
[tag-concept](./tag-concept.md) · [tag-interpretability](./tag-interpretability.md)
