# OpenClaw 自己強化エージェント設計

OpenClaw（exe.dev）の設計ブログ記事で紹介された、自律エージェントが自分自身の動作を継続的に改善する設計。主エージェント（main）と監視エージェント（ops/coach）を分離し、複数の安全制約を組み合わせる。

## 概要

- **情報源:** https://zenn.dev/akasara/articles/52dc506100f7ad
- **システム:** OpenClaw — WhatsApp・Telegram・Discord 等のメッセージングプラットフォームと AI エージェントを接続するブリッジツール
- **設計目標:** AI エージェントが自分の動作ルール（スキル・設定）を継続的に改善しつつ、暴走を防ぐ

## 観察されたパターン

### Read-Write 境界

`ops/coach` エージェントには "Never apply config changes automatically. Propose only" という非交渉ルールが設定されている。設定変更の「提案」と「適用」を分離し、適用には人間の確認を必須とする。

`activeHours`（09:00–23:00）による稼働時間制限は、**人間がレビューできない時間帯に書き込みゲートを閉じる**という Read-Write 境界の実装条件として機能する。

→ [Read-Write 境界](./read-write-boundary.md)

### クローズドループ自律改善

"1 Heartbeat = 1 改善" ルールにより、1サイクルあたりの変更を単一の改善に限定する。これにより各変更が独立して観察・帰属可能になり、problems.md への記録と組み合わせることで改善サイクルが閉じる。

→ [クローズドループ自律改善](./closed-loop-autonomous-improvement.md)

### 階層的エージェント監視

main（実行エージェント）と ops/coach（監視エージェント）を完全に分離し、coach が全体の健全性を俯瞰する2層構造。

→ [階層的エージェント監視](./hierarchical-agent-oversight.md)

---
[tag-case](./tag-case.md) · [tag-scalable-oversight](./tag-scalable-oversight.md)
