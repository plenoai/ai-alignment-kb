# 内部表現モニタリング (Internals-Based Monitoring)

モデルの出力テキストではなく、内部活性化・残差ストリームに対するプローブや分類器で安全性を監視し、CoTの不忠実性を回避する。

## コンテキスト

CoTベースの監視がモデルの真の推論を反映しないことが判明し、より信頼性の高い監視手法が必要な場合。

## 問題

**出力ベースの安全性モニタリングは、モデルが意図的に情報を隠蔽する場合に無効化される。**

## フォース

- 人工的 vs 自然的欺瞞：構築されたスリーパーエージェントでの検出成功が、自然発生的欺瞞にも転移するか不明
- コスト vs 精度のフロンティア：単純なプローブ（線形、EMA）はほぼ無料だが精度が劣り、高精度なサフィックスプローブは専用分類器のコストに近づく
- 適応的敵対者：モデルが非欺瞞的な活性化を生成するよう学習する可能性（ただし欺瞞自体より困難と議論）
- 汎化の限界：特定のバックドア挿入方法のアーティファクトである可能性

## 解決策

**モデルの内部活性化に対するプローブ・分類器・オラクルを用いて、出力に依存しない安全性監視を実現する。**

| 手法 | 概要 | コスト |
|------|------|--------|
| 線形プローブ（欺瞞プローブ） | 残差ストリームの活性化に対する単純な線形分類器、最小2例の訓練データ | ほぼ無料、AUROC 99%以上 |
| 部分的ファインチューニング | 最終MLP+Attentionブロックのみを再訓練し安全性分類機能を追加 | 約4%コストオーバーヘッドで専用分類器同等性能 |
| EMA線形プローブ | 指数移動平均による軽量プローブ | 無視可能なコスト |
| 活性化オラクル | LLMを訓練して自身の活性化に対する自然言語クエリに回答 | 訓練分布外への汎化に成功 |

## 結果コンテキスト

- 得られるもの：CoTの不忠実性を回避した安全性モニタリング、経済的に実行可能なスケーラブル監視（推論コストの4%以下）
- 失うもの：自然発生的欺瞞への汎化保証、適応的敵対者に対するロバストネス保証

## 既知の使用例

- [Simple Probes can Catch Sleeper Agents](https://www.anthropic.com/research/probes-catch-sleeper-agents) — 残差ストリーム線形プローブでAUROC 99%以上
- [Model-Internals Classifiers (Cheap Monitors)](https://alignment.anthropic.com/2025/cheap-monitors/) — 部分ファインチューニングで4%コスト、EMAプローブでほぼ無料
- [Activation Oracles](https://alignment.anthropic.com/2025/activation-oracles/) — 汎用的活性化解釈ツール、不整合と隠蔽知識の検出
- [Three Sketches of ASL-4 Safety Cases](https://alignment.anthropic.com/2024/safety-cases/) — SAEベースの懸念推論パターン監視

## 関連パターン

- [思考連鎖の忠実性ギャップ](./cot-faithfulness-gap.md)
- [アライメント偽装](./alignment-faking.md)
- [多層防御](./defense-in-depth.md)
- [行動監査ゲーム](./behavioral-auditing-game.md)

---
[tag-pattern](./tag-pattern.md) · [tag-interpretability](./tag-interpretability.md)
