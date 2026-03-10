# 原則仕様化 (Constitution as Specification)

宣言的な原則セット（「憲法」）をモデルの訓練・分類・データフィルタリングの中心的ポリシー機構として用い、人間可読で監査可能なアライメント仕様を実現する。

## コンテキスト

AIシステムの望ましい行動を定義し、それを訓練プロセスに反映させる必要があるが、ルールの網羅的列挙が非現実的な場合。

## 問題

**望ましい行動の完全な列挙は不可能であり、個別ルールベースのアプローチはスケールしない。**

## フォース

- 網羅性 vs 簡潔性：一般原則はスケールするが細粒度の制御が失われ、詳細ルールは細粒度制御を提供するがスケールしない
- スケーラビリティ vs 安全性：人間の監視は必要だが限界があり、AIフィードバックによるスケーリングが求められる
- 透明性 vs 効率性：CoT推論が品質と解釈可能性を向上させるが計算コストを追加
- 仕様の曖昧性：原則間の矛盾が潜在し、モデルごとに異なる解決が行われる（3,307の細粒度価値が数千の矛盾を含む）

## 解決策

**宣言的な原則セットを定義し、2フェーズ訓練プロセスでモデルに内在化させる。**

| フェーズ | 手法 | 効果 |
|---------|------|------|
| SLフェーズ | モデルが応答を生成→原則に対する自己批評→修正、修正済み応答でファインチューニング | 原則に沿った応答の蒸留 |
| RLAIFフェーズ | 複数候補を生成→AIが原則に基づき評価→選好モデルを訓練→RLの報酬シグナルとして使用 | 人間アノテーションなしでのアライメント強化 |

一般原則（「人類にとって最善を尽くす」）からの汎化が成功し、権力追求を示さない。ただし詳細原則も相補的価値を持つ。

## 結果コンテキスト

- 得られるもの：人間可読で監査可能なアライメント仕様、人間アノテーションの大幅削減、非回避的応答（拒否ではなく説明）
- 失うもの：原則間の潜在的矛盾への対処責任、原則の質がシステムの質の上限を決定

## 既知の使用例

- [Constitutional AI: Harmlessness from AI Feedback](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback) — 2フェーズ訓練（SL+RLAIF）の原型
- [Specific versus General Principles](https://www.anthropic.com/research/specific-versus-general-principles-for-constitutional-ai) — 単一一般原則からの汎化成功
- [Constitutional Classifiers](https://www.anthropic.com/research/constitutional-classifiers) — 原則→合成データ→分類器訓練パイプライン（ジェイルブレイク86%→4.4%）
- [Stress-testing model specs](https://alignment.anthropic.com/2025/stress-testing-model-specs/) — 3,307の価値観と数千の矛盾を発見

## 関連パターン

- [AIフィードバックによるスケーラブル監視](./scalable-oversight-via-ai-feedback.md)
- [多層防御](./defense-in-depth.md)
- [報酬シグナル腐敗](./reward-signal-corruption.md)

---
[tag-pattern](./tag-pattern.md) · [tag-constitutional-ai](./tag-constitutional-ai.md)
