# AI Alignment Knowledge Base

AI の目標・価値観・行動を人間の意図に一致させるためのパターン集。分野横断的に事例を収集し、再利用可能なパターンとして抽象化する。

→ **[Wiki を読む](./wiki/index.md)** · **[Knowledge Graph を見る](https://plenoai.github.io/ai-alignment-kb/)**

## サブドメイン

| サブドメイン | 概要 |
|------------|------|
| [Scalable Oversight](./wiki/tag-scalable-oversight.md) | 人間の監視品質をスケールさせる設計 |
| [RLHF](./wiki/tag-rlhf.md) | 人間フィードバックによる強化学習 |
| [Constitutional AI](./wiki/tag-constitutional-ai.md) | 原則ベースの自己改善アライメント |
| [Interpretability](./wiki/tag-interpretability.md) | AI 判断過程の可視化・理解 |

## セットアップ・起動

```bash
cp .env.example .env   # OPENAI_API_KEY を設定
uv run ingest.py       # wiki/ をナレッジグラフに投入
uv run search.py <クエリ>  # 検索
uv run visualize.py        # グラフを可視化 → docs/index.html（GitHub Pages にも反映）
```
