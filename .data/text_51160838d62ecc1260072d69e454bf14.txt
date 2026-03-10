# Interpretability（解釈可能性）

**Interpretability（解釈可能性）** とは、AI モデル（特に深層学習）の内部表現・推論過程・判断根拠を人間が理解できる形にする研究領域。Mechanistic Interpretability とも呼ばれる。

## なぜ重要か

- モデルが正しい理由で正解しているか確認できない（ショートカット学習の検出）
- 有害な内部表現や危険な目標が潜在していないか検証できない
- アライメントの達成度を直接検証する手段となる

## 主なアプローチ

### 機械的解釈可能性（Mechanistic Interpretability）
ニューラルネットワークの回路レベルで動作を解析する。特定の特徴・概念がどのユニット・サブグラフで表現されているかを特定する。

### 活性化解析（Activation Analysis）
中間層の活性化値を可視化・クラスタリングし、モデルが内部で何を「表現」しているかを調べる。

### プロービング（Probing）
中間表現に小さな分類器を当て、特定の概念（品詞・感情・事実）がエンコードされているか検証する。

### 因果介入（Causal Intervention）
活性化値を直接書き換え（activation patching）、行動変化から因果関係を特定する。

### SAE によるモデル比較と活性化操舵

Sparse Autoencoders（SAE）で微調整前後のモデルを比較し、活性化が変化した潜在特徴量を特定する。活性化操舵（steering）で因果効果を検証する。

OpenAI の研究（2025年12月）では、微調整によるミスアライメントが**二重メカニズム**で発生することが発見された：
1. 悪意的ペルソナ特徴量の**活性化**（従来の理解）
2. 有用なアシスタント特徴量の**抑制**（新発見）

「アシスタント・ペルソナ」特徴量の操舵によりミスアライメントスコアを 1% 未満に低減可能。ミスアライメント・ペルソナは双方向性（整列にも不整列にも操舵可能）だが、アシスタント特徴量は保護的役割に限定（一方向性）という非対称性が確認された。 — [Helpful assistant features suppress emergent misalignment](https://alignment.openai.com/helpful-assistant-features/)

### SAE 潜在帰属分析（Δ-attribution）

従来のモデル比較（Δ-activation）を超え、テイラー展開で活性化と出力の因果関係を近似する手法。単一モデルで機能し、比較モデルが不要。

OpenAI の研究（2025年12月）では、創発的ミスアライメントと不適切な検証という一見異なる現象が、単一の「provocative（扇動的コンテンツ）」特徴量で統一的に制御されることが発見された。この特徴量の操舵でミスアライメント 53% 増、不適切検証 40% 増を引き起こせる。 — [Debugging misaligned completions with sparse-autoencoder latent attribution](https://alignment.openai.com/sae-latent-attribution/)

## アライメントとの関係

| Interpretability の発見 | アライメントへの活用 |
|------------------------|-------------------|
| 有害概念の表現箇所特定 | ターゲット消去・モデル編集 |
| 欺瞞的挙動の回路検出 | 安全性フィルタの設計 |
| 報酬ハッキングの内部表現 | より堅牢な報酬モデル設計 |
| 保護的特徴量の抑制検出 | アシスタント特徴量の復元による再整列化 |
| 統一的因果特徴量の発見 | 複数の不整合を単一介入で修正 |

## 主要概念

- [Superposition（重畳表現）](./superposition.md) — 解釈可能性の根本障壁
- [Monosemanticity（単義性）](./monosemanticity.md) — 辞書学習の目標状態
- [Attribution Graph（帰属グラフ）](./attribution-graph.md) — 計算過程の可視化データ構造

## パターン

- [トイモデルによるアライメント探査](./toy-model-probing.md) — 最小モデルで理論構築
- [辞書学習による特徴分解](./dictionary-learning-feature-decomposition.md) — Superposition の解消
- [回路追跡](./circuit-tracing.md) — 推論過程の追跡
- [モデル差分による安全性検証](./model-diffing-safety-verification.md) — 安全訓練の深さを検証
- [自動解釈性監査](./automated-interpretability-auditing.md) — 解釈性ツールで監査をスケール
- [特徴ベース安全性分類](./feature-based-safety-classification.md) — 透明な安全性判定

## 関連概念

- [スケーラブルオーバーサイト](./scalable-oversight.md) — Interpretability で監視を強化
- [RLHF](./rlhf.md) — 報酬モデルの検証に Interpretability を活用

---
[tag-concept](./tag-concept.md) · [tag-interpretability](./tag-interpretability.md)
