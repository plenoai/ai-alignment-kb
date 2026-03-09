# ハーネスエンジニアリング

## 概要

AI エージェントを制御するランタイム基盤の設計。制約、フィードバックループ、ドキュメント構造、ライフサイクル管理を通じて、エージェントが大規模に信頼性をもって動作できるようにする。

> "the emerging discipline of designing constraints, feedback loops, documentation structures, and lifecycle management systems that allow AI coding agents to operate reliably at scale." — gtcode.com

OpenAI の Ryan Lopopolo が 2026年2月に公開した記事で体系化された概念であり、同チームは5ヶ月間「手作業で書かれたソースコードなし」の制約下で約100万行のプロダクトを構築・出荷した実験を通じてこの手法を確立した。

## Harness Engineering と Harness Hardening

現在の文献から2つの関連概念が浮かび上がる：

| 概念 | 焦点 | 例 |
|------|------|-----|
| **Harness Engineering** | エージェントを制御するランタイム基盤の設計 | 制約、フィードバックループ、AGENTS.md、承認メカニズム |
| **Harness Hardening** | そのハーネス自体のセキュリティ強化 | OS サンドボックス、ネットワーク隔離、クレデンシャル分離、防御の多層化 |

Symphony の SPEC.md は "Harness hardening refers to external isolation layers (OS/container/VM sandboxing, network restrictions, separate credentials) beyond Codex built-in controls" と明示的に定義している。

## 構成要素

OpenAI はハーネスを3つのカテゴリーに分類する：

| カテゴリー | 内容 | 具体例 |
|-----------|------|--------|
| コンテキストエンジニアリング | エージェントが参照する知識基盤の継続的強化 | 設計仕様・アーキテクチャマップを「単一情報源」として機械的に検証 |
| アーキテクチャ制約 | エージェントの行動をコードレベルで制約 | カスタムリンター、構造テスト（ArchUnit 等）、依存関係フローの強制（Types → Config → Repo → Service → Runtime → UI） |
| ガベージコレクション（エントロピー管理） | ドキュメント矛盾やアーキテクチャ違反を発見する定期エージェント | 矛盾検出エージェント、陳腐化した仕様の自動フラグ |

Martin Fowler は "if an architectural constraint matters enough to document, it matters enough to enforce with a linter" と原則を要約している。

### AGENTS.md — ドキュメント駆動行動制御

エージェントは「取得・観察できるもの」しか行動に反映できない。リポジトリ内のドキュメントが主要な操舵メカニズムとなる：

> "AGENTS.md is a README for AI agents" — 失敗駆動のドキュメンテーションがアクティブなフィードバックループに変換される。

エージェントが間違えるたびに、その間違いが二度と起きないようハーネスを改善する。これがハーネスエンジニアリングの中核サイクルである。

## Read-Write 境界との違い

[Read-Write 境界](./read-write-boundary.md)は「エージェントが何をしてよいか」の論理的な境界を引くパターンである。ハーネスエンジニアリングは「エージェントが何をできるか」の物理的・環境的な制約を設ける概念であり、レイヤーが異なる。

```
┌─────────────────────────────────────────┐
│  ハーネスエンジニアリング（物理層）       │
│  OS/コンテナ/VM サンドボックス            │
│  ネットワーク制限・認証スコープ最小化     │
│  ┌─────────────────────────────────────┐ │
│  │  Read-Write 境界（論理層）           │ │
│  │  読み取り＝自動 / 書き込み＝承認     │ │
│  │  ┌───────────────────────────────┐   │ │
│  │  │  エージェント本体              │   │ │
│  │  │  ツール呼び出し・推論          │   │ │
│  │  └───────────────────────────────┘   │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

| レイヤー | 制御対象 | 例 |
|---------|---------|-----|
| ハーネス（物理層） | 実行環境の能力上限 | VM 隔離、ネットワーク ACL、ファイルシステムマウント制限 |
| Read-Write 境界（論理層） | エージェントの行動ポリシー | 書き込み操作の承認ゲート、ドラフト生成 vs 実行 |
| エージェント本体 | 推論と計画 | ツール選択、プロンプト解釈 |

## 信頼境界の仮定

ハーネスエンジニアリングの核心は、エージェントが触れるすべてのデータソースを潜在的攻撃面とみなすことにある：

- **リポジトリ** — 悪意のあるコードやプロンプトインジェクションを含みうる
- **タスクトラッカー** — 課題タイトル・説明文が細工されうる
- **プロンプト入力** — 外部から注入される可能性がある

これらを前提とした防御策：

| 脅威 | ハーネスの対策 |
|------|--------------|
| プロンプトインジェクション | 発火対象タスクの事前フィルタリング、Web検索のキャッシュモード化 |
| 認証情報の漏洩 | トークンをエージェント環境に直接渡さず、スコープ制限付きプロキシ経由 |
| ファイルシステム逸脱 | ワークスペースパスのプリフィックス検証、ディレクトリ名のサニタイズ |
| ネットワーク経由の外部通信 | 許可リスト方式のネットワーク制限（デフォルト: ネットワークアクセス無効） |
| 設定ファイル改竄 | `.git`, `.agents`, `.codex` 等を読み取り専用に強制 |

## 多層防御アーキテクチャ

arXiv の OpenDev 論文は5層の独立した安全層を定義している。各層は独立に動作し、1層の障害が残り4層を損なわない：

| 層 | 名称 | 制御内容 |
|----|------|---------|
| L1 | プロンプト層 | セキュリティポリシー、行動安全性、read-before-edit ガードレール |
| L2 | スキーマ層 | プランモードホワイトリスト、サブエージェント別 allowed_tools、MCP ディスカバリゲーティング |
| L3 | ランタイム承認層 | 手動/半自動/自動レベル、永続的パーミッション |
| L4 | ツール層 | DANGEROUS_PATTERNS ブロックリスト、ストールリード検知、出力切り詰め、タイムアウト |
| L5 | ライフサイクルフック層 | pre-tool ブロッキング（exit code 2）、引数ミューテーション、JSON stdin プロトコル |

サブエージェント隔離: スキーマフィルタリング（許可リスト外のツールはサブエージェントに見えない）と `message_history=None`（フレッシュコンテキストで開始）で隔離境界を強制。

## サンドボックス実装技術

エージェント隔離の物理的実装は複数の技術スタックから選択される：

| 技術 | 隔離レベル | 特徴 | 適用場面 |
|------|-----------|------|---------|
| Docker コンテナ | カーネル共有 | 軽量だがカーネル脆弱性で脱出リスク | 信頼できるコードのみ |
| gVisor | ユーザー空間カーネル | syscall インターセプト、I/O で 10-30% オーバーヘッド | 計算集約タスク |
| Firecracker microVM | ハードウェア隔離 | 専用カーネル、起動 125ms、メモリ 5MiB 以下 | 本番エージェント実行 |
| OS ネイティブ | プラットフォーム依存 | macOS: Seatbelt、Linux: Landlock + seccomp | ローカル CLI |

### ファイルシステム + ネットワークの双方向隔離

Anthropic は Claude Code のサンドボックス設計で、**ファイルシステムとネットワークの両方の隔離が必須** と強調している：

> "effective sandboxing requires *both* filesystem and network isolation. Without network isolation, a compromised agent could exfiltrate sensitive files like SSH keys; without filesystem isolation, a compromised agent could easily escape the sandbox and gain network access." — Anthropic

実装: ネットワークは Unix ドメインソケット経由のプロキシサーバーに接続し、ドメイン単位の許可制御を行う。認証情報（git credentials、signing keys）はサンドボックス外に配置。この設計で **承認プロンプトを 84% 削減** した。

## 承認ポリシーの設計

NVIDIA AI Red Team のガイダンスに基づく段階的許可体系：

1. エンタープライズレベルの拒否リスト（ユーザーが上書き不可）
2. ワークスペース内の読み書きは自動承認
3. ホワイトリスト操作のみ許可
4. その他は全て個別承認が必要

重要原則: **承認結果をキャッシュしてはならない。** 一度承認された操作の再利用は、後続の悪意的活動を可能にする。

## 既知の実装例

- **OpenAI Codex:** クラウド実行は隔離コンテナ（ネットワーク無効、リポジトリのみプリロード）。CLI はプラットフォームネイティブサンドボックス（macOS: Seatbelt、Linux: Landlock + seccomp）。3つのモード: read-only / workspace-write / danger-full-access。
- **Symphony（OpenAI）:** ワークスペースパスのプリフィックス検証、ディレクトリ名サニタイズ、Linear GraphQL スコープ制限を仕様レベルで定義。 → [Symphony 事例](./symphony-case.md)
- **Claude Code（Anthropic）:** bubblewrap（Linux）/ Seatbelt（macOS）による OS レベル隔離。ファイルシステム隔離（CWD 内のみ書き込み可）+ ネットワーク隔離（Unix ソケットプロキシ経由）の双方向制御。承認プロンプト 84% 削減。
- **OpenAI Model Spec（2025-12）:** "autonomy must be bounded by a clear, mutually understood scope" + "every scope must include a shutdown timer"。高リスク活動（ハッキング、欺瞞、リソース取得、サブエージェント生成、自己改変）は明示的許可なく禁止。

## ソース

- [Harness engineering: leveraging Codex in an agent-first world（OpenAI, 2026-02）](https://openai.com/index/harness-engineering/)
- [Unlocking the Codex harness: how we built the App Server（OpenAI, 2026-02）](https://openai.com/index/unlocking-the-codex-harness/)
- [Harness Engineering（Martin Fowler, 2026）](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)
- [Claude Code Sandboxing（Anthropic）](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [Effective harnesses for long-running agents（Anthropic）](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Agent approvals & security（OpenAI Codex Docs）](https://developers.openai.com/codex/agent-approvals-security)
- [Model Spec（OpenAI, 2025-12-18）](https://model-spec.openai.com/2025-12-18.html)
- [Building AI Coding Agents for the Terminal（arXiv, 2026）](https://arxiv.org/html/2603.05344v1)
- [Practical Security Guidance for Sandboxing Agentic Workflows（NVIDIA, 2025）](https://developer.nvidia.com/blog/practical-security-guidance-for-sandboxing-agentic-workflows-and-managing-execution-risk/)
- [How to sandbox AI agents in 2026（Northflank）](https://northflank.com/blog/how-to-sandbox-ai-agents)
- [OpenAI Symphony SPEC.md](https://github.com/openai/symphony)

## 関連パターン

- [Read-Write 境界](./read-write-boundary.md) — 論理層の行動ポリシー。ハーネスエンジニアリングの内側で機能する
- [階層的エージェント監視](./hierarchical-agent-oversight.md) — 複数エージェントのハーネスをオーケストレータが統括する構成
- [エージェント自律性のスペクトラム](./agent-autonomy-spectrum.md) — ハーネスの厳しさは自律性レベルの選択と連動する

---
[tag-concept](./tag-concept.md) · [tag-scalable-oversight](./tag-scalable-oversight.md)
