# Ralph Loop — Claude Code 自律改善スキル

Claude Code のスキルとして実装された自律改善ループ。QA・Fix・Refactor の3フェーズを自動で繰り返し、人間が寝ている間にコード品質を向上させる。

**Source:**
- https://x.com/hiroki_daichi/status/2028833810314662262 — @hiroki_daichi による紹介ツイート

**Date:** 2026-03-04

## 背景にある問題

コード品質の継続的改善は重要だが、手動で行うには繰り返し作業が多く、人間の時間を大量に消費する：
- バグ発見 → Issue 起票 → 修正 → リファクタリング のサイクルを手動で回すのは非効率
- 夜間など人間が不在の時間帯は改善が止まる
- 自動化しようとすると暴走リスクや品質劣化のリスクがある

## 解決策

### 3フェーズの自律改善ループ

| フェーズ | 担当 | 内容 |
|---------|------|------|
| QA | バグ発見エージェント | バグを特定して Issue を起票 |
| Fix | 修正エージェント | Issue を修正して close |
| Refactor | 品質改善エージェント | コード品質を向上 |

この3フェーズを1ラウンドとして、終了条件に達するまで自動で繰り返す。

### コマンドインターフェース

```bash
improve 120        # 2時間（分指定）実行
improve --rounds 5 # 5ラウンド実行
```

### 安全網

- **E2E テスト:** 各ラウンド終了後に自動実行
- **自動リバート:** Refactor でテストが壊れたら自動的に元に戻す
- **早期終了:** Open Issue がゼロになれば自動終了

### 実行フロー

```
夜: improve コマンドを実行
  ↓
Round N: QA → Fix → Refactor
  ↓
E2E テスト → 失敗なら自動 Revert
  ↓
振り返り（結果記録）→ 自己学習（改善手法の改善）
  ↓
終了条件判定（時間/ラウンド/Issue=0）
  ↓
朝: コード品質が向上した状態で確認
```

## 観察されたパターン

- [クローズドループ自律改善](./closed-loop-autonomous-improvement.md) — QA→Fix→Refactor の反復サイクルと終了条件・安全網の構造
- [Read-Write 境界](./read-write-boundary.md) — 自動リバートによる「書き込みの可逆化」
- [定量ヘルススコア](./quantitative-health-score.md) — Open Issue 数を終了条件のゲートとして使用
- [メタ改善ループ](./meta-improvement-loop.md) — 振り返り→自己学習フェーズで改善手法そのものを更新

---
[tag-case](./tag-case.md) · [tag-scalable-oversight](./tag-scalable-oversight.md)
