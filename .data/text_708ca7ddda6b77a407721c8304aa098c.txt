# 行動監査ゲーム (Behavioral Auditing Game)

意図的に欠陥を埋め込んだ「モデル生物」を検証のグラウンドトゥルースとして活用する形式的監査手法。

## コンテキスト

AIモデルの安全性を事前に検証する必要があるが、自然発生する欺瞞行動を待つのはリスクが高すぎる場合。

## 問題

**自然発生的な欺瞞的アライメントのグラウンドトゥルースが存在しないため、監査手法の有効性を測定できない。**

## フォース

- 人工的 vs 自然的欠陥：埋め込まれた欺瞞が自然発生する欺瞞と同じ検出困難性を持つか不明
- 人間の専門家のスケーラビリティ限界：ブラインド監査には複数の独立チームが必要だが確保が困難
- 監査の一回性：一度結果を知ったチームの再利用が困難（「ネタバレ」効果）
- データアクセスの必要性：訓練データへのアクセスなしでは診断が困難

## 解決策

**既知の欠陥を埋め込んだ「モデル生物」を構築し、ブラインド監査演習のグラウンドトゥルースとして活用する。**

| ステップ | 手法 | 成果 |
|---------|------|------|
| モデル生物構築 | SFT + DPO + 敵対訓練 | 52種の報酬モデルバイアスを悪用するモデル |
| ブラインド監査 | レッド/ブルーチーム演習 | 4チーム中3チームが隠れた目的を特定（最速90分） |
| 自動監査エージェント | 調査・評価・レッドチーム | 調査10-42%、評価88%、幅優先レッドチーム7/10発見 |
| オープンソース再現 | Llama 3.3 70B | 研究コミュニティへの公開 |

## 結果コンテキスト

- 得られるもの：監査手法の定量的評価が可能になる、再現可能なテストベッド
- 失うもの：人工的欠陥が自然欠陥を代表する保証、完全な自動化（人間の判断が依然不可欠）

## 既知の使用例

- [Auditing Language Models for Hidden Objectives](https://www.anthropic.com/research/auditing-hidden-objectives) — 4チーム中3チームがSAE分析で隠れた目的を特定（最速90分）
- [Open Source Replication of the Auditing Game](https://alignment.anthropic.com/2025/auditing-mo-replication/) — Llama 3.3 70Bでオープンソース再現
- [Pre-deployment auditing can catch an overt saboteur](https://alignment.anthropic.com/2026/auditing-overt-saboteur/) — 人間監査者が3体の破壊工作モデル全てを特定
- [Petri](https://alignment.anthropic.com/2025/petri/) — 14モデル×111シードの自動監査フレームワーク
- [Bloom](https://alignment.anthropic.com/2025/bloom-auto-evals/) — 自動行動評価スイート生成

## 関連パターン

- [アライメント偽装](./alignment-faking.md)
- [レッドチーム・モジュラリティ](./red-team-modularity.md)
- [多層防御](./defense-in-depth.md)
- [階層的エージェント監視](./hierarchical-agent-oversight.md)

---
[tag-pattern](./tag-pattern.md) · [tag-scalable-oversight](./tag-scalable-oversight.md)
