# Claude Code Plugins

A community-driven marketplace for Claude Code extensions and plugins.

## Quick Start

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

## Available Plugins

各プラグインは Agent Skills（`/<skill-name>` で起動、または文脈に応じて自動起動）と Subagents（特定タスクに特化したエージェント）で構成されています。

### android
Android development best practices, code generation, and debugging assistance.

**Skills:**
- `/agent-review` - Android プロジェクト（app / library）のコード変更を Claude Code の Task subagent でレビューする。プロジェクト文脈を実行時に検出
- `/codex-review` - Android プロジェクトのコード変更を Codex MCP サーバーでレビューする
- `/crashlytics-triage` - Firebase MCP 経由で Crashlytics のクラッシュレポートを調査する。リリース後のヘルスチェックと個別イシューの深掘りに対応

**Agents:**
- `android-compose-architect` - Android アーキテクチャと Jetpack Compose 実装の設計・リファクタリング
- `android-library-architect` - Android ライブラリの公開 API 設計・Java 相互運用・スレッド安全性のレビュー

### github
Git/GitHub safety rules and PR review workflows.

**Skills:**
- `/git-operations` - すべての git 操作（commit, branch, rebase, push, PR 作成など）の安全ガイドライン
- `/review-pr` - PR をレビューし、結果を GitHub にインラインコメントとして投稿する
- `/check-pr` - PR のレビューコメントと CI ステータスを確認し、各指摘を個別コミット・push する
- `/reply-pr` - check-pr の評価結果に基づき、各レビューコメントに返信してスレッドを解決する
- `/issue-triage` - オープン issue を並列調査し、実現性（HIGH/MEDIUM/LOW）でグループ化した優先度表を作成する
- `/release-notify` - リリース後、対応した issue にコメントしてユーザーに通知する
- `/renovate-pr-review` - Renovate / Dependabot の依存更新 PR の changelog を並列調査し、破壊的変更への追随や関連ファイルの同期更新を行う

**Agents:**
- `review-pr-bugs` - PR の差分からバグ・セキュリティ問題を検出する
- `review-pr-quality` - PR の差分からコード品質（DRY・一貫性・パフォーマンス）の問題を検出する
- `review-pr-rules` - PR の差分がプロジェクト規約（CLAUDE.md / .claude/rules/）に準拠しているかチェックする

### meta
Meta-workflow skills for Claude Code itself.

**Skills:**
- `/session-review` - 現在のセッションを振り返り、保存価値のある学び（プロジェクト固有の注意点・ユーザーの好み・再利用可能なワークフロー）を抽出し、適切な保存先（`.claude/rules/`, `CLAUDE.md`, 新規 skill など）に分類して提案・適用する

## Plugin Categories

### 🛠️ Skills
`/` で起動できる、あるいは文脈に応じて自動起動する特化機能。ドメイン知識やワークフローを提供します。各プラグインの中心的な構成要素です。

### 🤖 Subagents
特定タスクに特化したエージェント定義。レビューやアーキテクチャ設計など、専門的な判断を委譲できます。

### 🪝 Hooks / 🔌 MCP Servers / 💬 Slash Commands
Claude Code のプラグインは hooks（イベント駆動のシェルコマンド）、MCP サーバー、スラッシュコマンドもサポートしています。現在このマーケットプレースのプラグインは主に Skills と Subagents で構成されています。

## Contributing

We welcome plugin contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Steps

1. Fork this repository
2. Create your plugin in the `plugins/` directory
3. Add a `.claude-plugin/plugin.json` manifest
4. Register your plugin in `.claude-plugin/marketplace.json`
5. Submit a pull request

## Plugin Structure

Each plugin should follow this structure:

```
plugins/
└── your-plugin/
    ├── .claude-plugin/
    │   └── plugin.json      # Required: Plugin manifest (name, version, description, author)
    ├── commands/            # Optional: slash commands (.md)
    ├── skills/              # Optional: Agent Skills (<name>/SKILL.md)
    ├── agents/              # Optional: subagent definitions (.md)
    ├── hooks/               # Optional: hooks.json + scripts
    └── .mcp.json            # Optional: MCP server definitions
```

**Important**: `commands/`, `skills/`, `agents/`, `hooks/` go in the plugin root. Only `plugin.json` lives inside `.claude-plugin/`.

## Documentation

- [Creating Plugins](https://docs.claude.com/en/docs/claude-code/creating-plugins)
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)

## Support

- [Report Issues](https://github.com/yshrsmz/cc-plugins/issues)
- [Request Plugins](https://github.com/yshrsmz/cc-plugins/issues/new)
- [Claude Code Issues](https://github.com/anthropics/claude-code/issues)

## License

This repository is licensed under [Apache License 2.0](./LICENSE).

Individual plugins may have their own licenses - check each plugin's directory for specific licensing information.

## Disclaimer

These plugins are community-contributed and not officially supported by Anthropic. Review code before installation and use at your own discretion.
