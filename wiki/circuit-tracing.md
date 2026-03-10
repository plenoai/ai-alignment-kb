# 回路追跡（Circuit Tracing）

モデルの計算過程を [Attribution Graph](./attribution-graph.md) として可視化し、入力から出力に至る推論ステップを特徴レベルで追跡する。

## コンテキスト

大規模言語モデルが特定の出力を生成する際、内部でどのような計算ステップを経ているかが不透明である。Chain-of-thought を出力させても、表出された推論と内部計算が一致しているか（faithfulness）検証できない。

## 問題

**モデルの出力は観察できるが、内部の推論過程は見えない。正しい理由で正しい答えを出しているのか、ショートカットや偶然なのか判別できない。**

## フォース

- 完全な因果グラフが理想だが、活性化する特徴が多すぎて全追跡は不可能
- 近似（注意パターンの凍結、正規化の固定）が必要だが、粗い近似は実際の計算と乖離する
- 注意パターンの形成過程（QK 回路）は現在の手法では追跡不能
- エラーノードに隠れた重要な計算が存在する可能性がある

## 解決策

**Cross-layer Transcoder（CLT）で MLP を置換した置換モデルを構築し、特徴間の線形帰属を計算して Attribution Graph を生成する。グラフ刈り込みで主要な計算パスを抽出する。**

```
[入力トークン]
      ↓
  [Transcoder 特徴 L1] ──帰属──→ [Transcoder 特徴 L2]
      ↓                              ↓
  [Transcoder 特徴 L3] ──帰属──→ [出力ロジット]
```

### 分析手法

| 手法 | 用途 |
|------|------|
| パス追跡 | 入力から出力への情報経路を特定 |
| 並列計算の検出 | 独立した回路が同一出力に貢献するケースを発見 |
| 抑制メカニズムの検出 | 誤った出力を抑制する回路を特定 |
| 摂動検証 | 特徴値の操作による効果を予測と比較 |
| Supernode 化 | 類似特徴をグループ化し概念レベルで理解 |

## 結果コンテキスト

**得られるもの**
- モデルの推論過程を特徴レベルで可視化・検証できる
- 幻覚・jailbreak・不忠実な CoT の原因を回路レベルで特定できる
- 安全訓練がどのように回路を変化させたか確認できる

**失うもの**
- 注意パターンの形成過程は説明できない（凍結近似の限界）
- 置換モデルと元モデルの忠実性は不完全（再構成誤差 ~11.5%）
- 大規模モデルへの適用にはCLT の事前訓練が必要

## 既知の使用例

- **Circuit Tracing (2025)**: Claude 3.5 Haiku で手法を実証。頭字語解読・事実想起・加算の回路を可視化
- **On the Biology of a Large Language Model (2025)**: Claude 3.5 Haiku の内部メカニズムを網羅的に調査
  - 幻覚: 「既知回答」特徴の誤発火が原因と特定
  - 安全訓練: 事前学習の危害カテゴリ特徴を集約して拒否回路を構築
  - Jailbreak: アクロスティック攻撃が文字単位で処理され、意味統合前に出力される回路を解明
  - CoT 忠実性: 内部計算（ルックアップテーブル）と表出推論（標準アルゴリズム）の乖離を検出
- **Emergent Introspective Awareness (2025)**: モデルが自身の活性化状態を検査できる証拠を回路レベルで調査

## 関連パターン

- [辞書学習による特徴分解](./dictionary-learning-feature-decomposition.md) — 回路追跡の前提（解釈可能なノードの供給）
- [自動解釈性監査](./automated-interpretability-auditing.md) — 回路追跡をツールとして監査エージェントに搭載
- [トイモデルによるアライメント探査](./toy-model-probing.md) — 回路追跡の理論をトイモデルで検証
- [検証天井](./verification-ceiling.md) — 回路追跡は検証天井を引き上げる

## ソース

- Circuit Tracing: Revealing Computational Graphs in Language Models (Anthropic, 2025)
- On the Biology of a Large Language Model (Anthropic, 2025)

---
[tag-pattern](./tag-pattern.md) · [tag-interpretability](./tag-interpretability.md)
