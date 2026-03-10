# Attribution Graph（帰属グラフ）

**Attribution Graph（帰属グラフ）** とは、言語モデルの特定プロンプトに対する計算過程を、入力トークン → 中間特徴 → 出力トークンの有向非巡回グラフ（DAG）として表現したもの。[回路追跡](./circuit-tracing.md) パターンの中核データ構造。

## 構造

| ノード種別 | 役割 |
|-----------|------|
| 入力ノード | トークン埋め込み |
| 中間ノード | 各位置・各層で活性化した Transcoder 特徴 |
| 出力ノード | 候補トークンのロジット |
| エラーノード | MLP の未説明部分（近似誤差） |

エッジは線形帰属の重みを持ち、特徴間の影響度を定量化する。

## 活用

- **多段推論の可視化**: Dallas → Texas → Austin のような推論ステップを個別の特徴クラスタとして追跡
- **幻覚の原因特定**: 「既知回答」特徴の誤発火を検出
- **安全訓練の検証**: 拒否回路がどの事前学習特徴を集約しているか確認
- **Jailbreak 分析**: 攻撃がなぜ拒否回路を迂回するか回路レベルで解明

## 制約

- 注意パターンの形成過程（QK 回路）は説明できない（凍結して近似）
- エラーノードに隠れた重要な計算が存在する可能性
- 置換モデルと元モデルの忠実性は完全ではない

## 関連概念

- [回路追跡](./circuit-tracing.md) — Attribution Graph を生成するパターン
- [Monosemanticity（単義性）](./monosemanticity.md) — グラフのノードが解釈可能であるための前提
- [Interpretability（解釈可能性）](./interpretability.md) — 上位の研究領域

## ソース

- Circuit Tracing: Revealing Computational Graphs in Language Models (Anthropic, 2025)
- On the Biology of a Large Language Model (Anthropic, 2025)

---
[tag-concept](./tag-concept.md) · [tag-interpretability](./tag-interpretability.md)
