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

## アライメントとの関係

| Interpretability の発見 | アライメントへの活用 |
|------------------------|-------------------|
| 有害概念の表現箇所特定 | ターゲット消去・モデル編集 |
| 欺瞞的挙動の回路検出 | 安全性フィルタの設計 |
| 報酬ハッキングの内部表現 | より堅牢な報酬モデル設計 |

## 関連概念

- [スケーラブルオーバーサイト](./scalable-oversight.md) — Interpretability で監視を強化
- [RLHF](./rlhf.md) — 報酬モデルの検証に Interpretability を活用

---
[tag-concept](./tag-concept.md) · [tag-interpretability](./tag-interpretability.md)
