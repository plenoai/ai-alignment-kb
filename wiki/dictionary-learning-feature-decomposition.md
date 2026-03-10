# 辞書学習による特徴分解

Sparse Autoencoder をモデルの活性化値に適用し、多義的なニューロンを単義的（monosemantic）な特徴方向に分解して、モデル内部を検査可能にする。

## コンテキスト

大規模言語モデルの内部表現を理解したいが、個々のニューロンは [Superposition](./superposition.md) により複数の概念を同時に符号化しており、ニューロン単位の分析では意味のある情報が得られない。

## 問題

**ニューロンは多義的（polysemantic）であり、1 つのニューロンの活性化を見ても何を表現しているか判別できない。モデル内部の安全性検査が不可能になる。**

## フォース

- 特徴の数はニューロン数をはるかに超える（superposition）ため、1:1 対応は存在しない
- 辞書が小さすぎると粗い特徴しか得られず、大きすぎると偽の特徴（artifact）が現れる
- 大規模モデルへの適用には膨大な訓練コストがかかる
- 抽出された特徴が本当にモデルの計算に使われているか検証が必要

## 解決策

**Sparse Autoencoder（SAE）をモデルの中間活性化値に訓練し、スパース性制約のもとで活性化を再構成する辞書を学習する。辞書の各要素が解釈可能な単義的特徴に対応する。**

```
活性化ベクトル x ∈ ℝ^d
        ↓
    [Encoder]  →  スパースな特徴ベクトル f ∈ ℝ^n  (n >> d)
        ↓
    [Decoder]  →  再構成 x̂ ≈ x
```

### 特徴の検証方法

| 検証手段 | 内容 |
|----------|------|
| データセット例 | 特徴が最大活性化するテキスト群を確認 |
| ロジット効果 | 特徴が促進/抑制するトークンを確認 |
| 因果介入 | 特徴値を操作し出力変化を確認 |
| 他特徴との接続 | [Attribution Graph](./attribution-graph.md) 上での位置を確認 |

## 結果コンテキスト

**得られるもの**
- モデル内部の概念的表現を人間が解釈可能な形で抽出できる
- 安全性関連の特徴（有害概念、偽情報、バイアス）を直接発見し介入できる
- [回路追跡](./circuit-tracing.md) の前提条件（解釈可能なノード）を満たす

**失うもの**
- 再構成誤差により、一部の計算が辞書に捕捉されない（dark matter）
- 特徴の粒度選択（辞書サイズ）に明確な基準がなく、試行錯誤が必要
- 大規模モデルへの適用には大量の計算リソースが必要

## 既知の使用例

- **Towards Monosemanticity (2023)**: 1 層 Transformer の MLP 活性化に SAE を適用。数千の解釈可能な特徴を抽出
- **Scaling Monosemanticity (2024)**: Claude 3 Sonnet に適用。安全性関連特徴（有害コンテンツ検出、偽情報、コードセキュリティ）を大規模に抽出
- **Features as Classifiers (2024)**: 抽出した特徴を安全性分類器の入力として使用 → [特徴ベース安全性分類](./feature-based-safety-classification.md)

## 関連パターン

- [回路追跡](./circuit-tracing.md) — 分解した特徴を使って計算過程を追跡
- [トイモデルによるアライメント探査](./toy-model-probing.md) — 辞書学習の理論的基盤をトイモデルで構築
- [モデル差分による安全性検証](./model-diffing-safety-verification.md) — Crosscoder で辞書学習をモデル間に拡張
- [特徴ベース安全性分類](./feature-based-safety-classification.md) — 抽出した特徴の応用

## ソース

- Towards Monosemanticity (Anthropic, 2023)
- Scaling Monosemanticity (Anthropic, 2024)

---
[tag-pattern](./tag-pattern.md) · [tag-interpretability](./tag-interpretability.md)
