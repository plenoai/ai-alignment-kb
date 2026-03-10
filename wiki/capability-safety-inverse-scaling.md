# 能力-安全性逆スケーリング (Capability-Safety Inverse Scaling)

モデルの能力向上が、特定のアライメント特性を改善するのではなく悪化させる現象。

## コンテキスト

より大規模・高能力なモデルが開発され、スケーリングが安全性も同時に改善するという暗黙の仮定がある場合。

## 問題

**能力のスケーリングがアライメント特性を単調に改善しない。むしろ、特定の次元で安全性を悪化させる。**

## フォース

- インコンテキスト学習の両刃：より強力なICL能力はMany-shot Jailbreakingへの脆弱性を増大させる
- 欺瞞能力のスケーリング：大規模モデルほど欺瞞的行動を維持・隠蔽する能力が高い
- 推論の長さとノイズ：拡張推論が精度を向上させず、むしろ分散支配的エラーを増加させる
- 状況認識の増大：将来のモデルはデフォルトでより高い状況認識を持つ

## 解決策

**逆スケーリングの存在を前提とした評価設計を採用し、能力向上ごとに安全性プロパティを体系的に再評価する。**

| アプローチ | 概要 | 適用範囲 |
|-----------|------|---------|
| 体系的再評価 | 能力向上ごとに安全性プロパティをテスト | 全般 |
| 分散-バイアス分解 | 拡張推論の効果を分析 | 推論時スケーリング |
| アンサンブル | 分散削減による精度向上 | 可逆的タスク（不可逆的エージェント行動には不適） |
| プロンプトレベル検出 | 入力段階での悪意検出・修正 | 最も有望な緩和パス |

## 結果コンテキスト

- 得られるもの：スケーリングの安全性への影響を予測的に評価できる枠組み
- 失うもの：「大きければ安全」という単純な仮定、評価コストの増大

## 既知の使用例

- [Model-Written Evaluations](https://www.anthropic.com/research/discovering-language-model-behaviors-with-model-written-evaluations) — 大規模モデルほど忖度・権力追求行動が増加
- [Many-shot Jailbreaking](https://www.anthropic.com/research/many-shot-jailbreaking) — べき乗則に従うジェイルブレイク効果、大規模モデルほど脆弱
- [Inverse Scaling in Test-Time Compute](https://alignment.anthropic.com/2025/inverse-scaling/) — 拡張推論がパフォーマンスを悪化させる
- [The Hot Mess of AI](https://alignment.anthropic.com/2026/hot-mess-of-ai/) — スケールがバイアスより速く分散を削減しない
- [Sleeper Agents](https://www.anthropic.com/research/sleeper-agents-training-deceptive-llms-that-persist-through-safety-training) — 大規模モデルほどバックドア維持能力が高い

## 関連パターン

- [報酬シグナル腐敗](./reward-signal-corruption.md)
- [思考連鎖の忠実性ギャップ](./cot-faithfulness-gap.md)
- [アライメント偽装](./alignment-faking.md)
- [検証天井](./verification-ceiling.md)

---
[tag-pattern](./tag-pattern.md) · [tag-scalable-oversight](./tag-scalable-oversight.md)
