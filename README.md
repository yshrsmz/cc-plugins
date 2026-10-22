# Claude Code / Codex Plugins

A community-driven plugin marketplace for Claude Code and Codex. Both hosts share the skills under `plugins/`; each host has its own marketplace catalog and manifest.

## Quick Start: Claude Code

### 1. マーケットプレースを追加する

#### グローバル（User scope）

自分の全プロジェクトでこのマーケットプレースを利用できるようにします。

```bash
/plugin marketplace add yshrsmz/cc-plugins
```

#### プロジェクトローカル（Project scope）

リポジトリの `.claude/settings.json` に `extraKnownMarketplaces` を追加します。チームメンバーがリポジトリを trust すると、マーケットプレースとプラグインのインストールを促すプロンプトが表示されます。

```json
{
  "extraKnownMarketplaces": {
    "yshrsmz-cc-plugins": {
      "source": {
        "source": "github",
        "repo": "yshrsmz/cc-plugins"
      }
    }
  }
}
```

必要に応じて `enabledPlugins` も一緒に設定できます。`extraKnownMarketplaces` のキー名がプラグイン参照時のマーケットプレース識別名になります:

```json
{
  "extraKnownMarketplaces": {
    "yshrsmz-cc-plugins": {
      "source": {
        "source": "github",
        "repo": "yshrsmz/cc-plugins"
      }
    }
  },
  "enabledPlugins": {
    "github@yshrsmz-cc-plugins": true
  }
}
```

### 2. プラグインをインストールする

プラグインのインストールには3つのスコープがあります。用途に応じて使い分けてください。

#### グローバル（User scope）

全プロジェクトで使えるようにインストールします。`--scope` を省略した場合のデフォルトです。

Claude Code 内から:

```bash
/plugin install <plugin-name>@yshrsmz-cc-plugins
```

ターミナルから:

```bash
claude plugin install <plugin-name>@yshrsmz-cc-plugins
# または明示的にスコープを指定
claude plugin install <plugin-name>@yshrsmz-cc-plugins --scope user
```

#### プロジェクトローカル（Project scope）

特定のリポジトリの全コラボレーターに共有されます。`.claude/settings.json` に設定が追加されます。

```bash
claude plugin install <plugin-name>@yshrsmz-cc-plugins --scope project
```

#### 個人ローカル（Local scope）

特定のリポジトリで自分だけが使えるようにインストールします。他のコラボレーターには共有されません。

```bash
claude plugin install <plugin-name>@yshrsmz-cc-plugins --scope local
```

### 3. プラグインを確認する

インストール済みプラグインの確認:

```bash
/plugin
```

`Installed` タブでスコープごとにグループ化されたプラグイン一覧を確認できます。

## Quick Start: Codex

Codex CLI 0.163.0 でカタログの認識を確認しています。プラグイン機能を利用できる Codex CLI またはデスクトップアプリを使ってください。

```bash
codex plugin marketplace add yshrsmz/cc-plugins
codex plugin list --marketplace yshrsmz-cc-plugins --available
codex plugin add github@yshrsmz-cc-plugins
```

`github` は `android`、`code-quality`、`meta`、`writing` に置き換えられます。CLI に `plugin add` がない環境では、デスクトップアプリのプラグイン一覧でこのマーケットプレースを選び、インストールしてください。更新には `codex plugin marketplace upgrade yshrsmz-cc-plugins` を使い、新しいセッションでスキルを確認します。

ローカルの変更を試す場合は、GitHub の指定の代わりにチェックアウトしたリポジトリの絶対パスを登録します。

```bash
codex plugin marketplace add /absolute/path/to/cc-plugins
```

インストール後はスキル選択から対象スキルを選ぶか、依頼文でスキル名を明示します。以下の一覧の `/skill-name` 表記は Claude Code 向けの省略形です。Claude Code では `/github:pr-review` のようにプラグイン名で修飾できます。Codex では同じスキル名を選択して使います。

Codex のプロジェクト設定で有効・無効を指定する場合は、信頼済みプロジェクトの `.codex/config.toml` に次を設定します。マーケットプレースの登録・プラグインの導入は別途必要です。

```toml
[plugins."github@yshrsmz-cc-plugins"]
enabled = true
```

`agents/*.md` は Claude Code のエージェント定義です。Codex では `agent-review`、`pr-review`、`simplify` がその本文を汎用サブエージェントへ渡します。プラグインの導入だけでは、これらは Codex の名前付きカスタムエージェントとして登録されません。`simplify` はサブエージェント機能がなければ逐次レビューします。他の並列処理を行うスキルにはサブエージェント機能が必要で、`deai` には会話を継承しないサブエージェントが必要です。手動起動限定のスキルは、両環境で自動起動を無効にしています。

Firebase Crashlytics を使う場合、Codex 側には Firebase MCP の接続・認証が別途必要です。Claude Code の `firebase` プラグイン依存は Codex には適用されません。このリポジトリから Firebase ツールをインストールする処理はありません。

配布形式と設定の詳細は [OpenAI 公式ドキュメント](https://developers.openai.com/plugins/build/plugins)を参照してください。

## Available Plugins

各プラグインは共通の Agent Skills と、必要に応じてサブエージェント向けの指示で構成されています。起動方法とエージェントの扱いは上記の各環境向け手順を参照してください。

### android
Android development best practices, code generation, and debugging assistance.

**Skills:**
- `/agent-review` - Android プロジェクト（app / library）のコード変更を Claude Code / Codex のサブエージェントでレビューする。プロジェクト文脈を実行時に検出
- `/codex-review` - Android プロジェクトのコード変更を Codex CLI（`codex exec`）でレビューする
  - 前提: `codex` CLI 0.154.0 以降がインストール済みかつ認証済みであること
- `/crashlytics-triage` - Firebase MCP 経由で Crashlytics のクラッシュレポートを調査する。リリース後のヘルスチェックと個別イシューの深掘りに対応
  - Claude Code の前提: firebase プラグインが必要（`firebase` マーケットプレースへの依存として自動インストールされる）。マーケットプレース未登録の場合は先に `claude plugin marketplace add firebase/firebase-tools` を実行すること

**Agents:**
- `android-compose-architect` - Android アーキテクチャと Jetpack Compose 実装の設計・リファクタリング
- `android-library-architect` - Android ライブラリの公開 API 設計・Java 相互運用・スレッド安全性のレビュー

### code-quality

Language-independent code simplification for Claude Code and Codex.

**Skills:**

- `/simplify` - 明示起動限定。ベースブランチとの差分全体と未コミット変更を再利用・品質・効率の3観点でレビューし、振る舞いを維持して修正・検証する。委譲機能がなければ逐次レビューする

詳細は [code-quality README](plugins/code-quality/README.md) を参照してください。

### github
Git/GitHub safety rules and PR review workflows.

**Skills:**
- `/git-operations` - すべての git 操作（commit, branch, rebase, push, PR 作成など）の安全ガイドライン
- `/pr-review` - PR をレビューし、結果を GitHub にインラインコメントとして投稿する
- `/pr-check` - PR のレビューコメントと CI ステータスを確認し、各指摘を個別コミット・push する
- `/pr-reply` - pr-check の評価結果に基づき、各レビューコメントに返信してスレッドを解決する
- `/issue-triage` - オープン issue を並列調査し、実現性（HIGH/MEDIUM/LOW）でグループ化した優先度表を作成する
- `/release-notify` - リリース後、対応した issue にコメントしてユーザーに通知する
- `/renovate-pr-review` - Renovate / Dependabot の依存更新 PR の changelog を並列調査し、破壊的変更への追随や関連ファイルの同期更新を行う
- `/branch-cleanup` - マージ済み PR の head SHA と照合して、ローカルのマージ済みブランチとその worktree を安全に削除する

**Agents:**
- `pr-review-bugs` - PR の差分からバグ・セキュリティ問題を検出する
- `pr-review-quality` - PR の差分からコード品質（DRY・一貫性・パフォーマンス）の問題を検出する
- `pr-review-rules` - PR の差分がプロジェクト規約（AGENTS.md / CLAUDE.md / 参照される規約ファイル）に準拠しているかチェックする

### meta
Meta-workflow skills for Claude Code and Codex.

**Skills:**
- `/session-review` - 現在のセッションを振り返り、保存価値のある学び（プロジェクト固有の注意点・ユーザーの好み・再利用可能なワークフロー）を抽出し、実行環境に適した保存先（`AGENTS.md`, `.claude/rules/`, `CLAUDE.md`, 新規 skill など）に分類して提案・適用する

### writing
Japanese prose editing: AI-generated-text detection plus redundancy, duplication, and consistency cleanup in a single pass.

**Skills:**
- `/deai` - 日本語ドキュメントから AI 生成感と、冗長・重複・表記揺れ・文章品質・整合性の問題を 26 カテゴリで検出し、1 つの指摘リストで修正案を提示して校正する。検出は観点ごとに 2 つのサブエージェントへ並列で分担させる。会話の文脈を持たないサブエージェントとして動くため、執筆者には自然に見える「経緯に依存した記述」も拾える

## Plugin Categories

### 🛠️ Skills
明示的に起動できる、あるいは文脈に応じて自動起動する特化機能。ドメイン知識やワークフローを提供します。各プラグインの中心的な構成要素です。

### 🤖 Subagents
特定タスクに特化した指示。Claude Code では名前付きエージェントとして使い、Codex では対応するスキルからサブエージェントへ指示を渡します。

### 🪝 Hooks / 🔌 MCP Servers / 💬 Slash Commands
Claude Code のプラグインは hooks（イベント駆動のシェルコマンド）、MCP サーバー、スラッシュコマンドもサポートしています。現在このマーケットプレースのプラグインは主に Skills と Subagents で構成されています。

## Contributing

We welcome plugin contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Steps

1. Fork this repository
2. Create your plugin in the `plugins/` directory
3. Add `.claude-plugin/plugin.json` and portable `plugin.json` manifests with matching identity and version
4. Register your plugin in both `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`
5. Submit a pull request

## Plugin Structure

Each plugin should follow this structure:

```
plugins/
└── your-plugin/
    ├── .claude-plugin/
    │   └── plugin.json      # Required: Plugin manifest (name, version, description, author)
    ├── plugin.json          # Required: Agent Plugins 1.0 manifest for Codex
    ├── references/          # Optional: shared runtime and domain instructions
    ├── commands/            # Optional: slash commands (.md)
    ├── skills/              # Optional: Agent Skills (<name>/SKILL.md)
    ├── agents/              # Optional: subagent definitions (.md)
    ├── hooks/               # Optional: hooks.json + scripts
    └── .mcp.json            # Optional: MCP server definitions
```

**Important**: `commands/`, `skills/`, `agents/`, `hooks/` go in the plugin root. Only the Claude Code manifest lives inside `.claude-plugin/`; the portable `plugin.json` lives at the plugin root. Shared skills are discovered under `skills/<name>/SKILL.md`. For manual-only skills, include `skills/<name>/agents/openai.yaml` with `policy.allow_implicit_invocation: false`.

## Documentation

- [Creating Plugins](https://docs.claude.com/en/docs/claude-code/creating-plugins)
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
- [Codex Plugin Packaging](https://developers.openai.com/plugins/build/plugins)
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)

## Support

- [Report Issues](https://github.com/yshrsmz/cc-plugins/issues)
- [Request Plugins](https://github.com/yshrsmz/cc-plugins/issues/new)
- [Claude Code Issues](https://github.com/anthropics/claude-code/issues)

## License

This repository is licensed under [Apache License 2.0](./LICENSE).

Individual plugins may have their own licenses - check each plugin's directory for specific licensing information.

## Disclaimer

These plugins are community-contributed and not officially supported by Anthropic or OpenAI. Review code before installation and use at your own discretion.
