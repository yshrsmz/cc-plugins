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

必要に応じて `enabledPlugins` も一緒に設定できます:

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
    "base@yshrsmz-cc-plugins": true
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

### base
Essential commands and hooks for common workflows.

**Commands:**
- `/check-pr` - Automated PR review comment analysis and issue resolution workflow
  - Fetches review comments using `gh` commands
  - Analyzes feedback from copilot, claude, and reviewers
  - Creates individual commits for each fix
  - Verifies build/test/lint after changes

**Hooks:**
- SessionStart - Injects current date/time context automatically

**MCP Servers:**
- Sequential Thinking - Enhanced reasoning capabilities for complex problems

### codex-mcp
Codex MCP integration for comprehensive code reviews.

**Commands:**
- `/codex-review` - In-depth code review workflow with Codex
  - Analyzes staged and unstaged changes via git
  - Checks architecture compliance (MVI patterns, clean architecture)
  - Reviews code quality, testing coverage, and Android best practices
  - Provides actionable feedback with specific file/line references

**MCP Servers:**
- Codex - Code analysis and review capabilities

### serena-mcp
Serena MCP integration for IDE assistance.

**MCP Servers:**
- Serena - IDE assistant providing project context and insights

## Plugin Categories

### 💬 Slash Commands
Custom commands that can be invoked with `/` in Claude Code to automate workflows.

### 🪝 Hooks
Event-driven shell commands that execute in response to Claude Code events (SessionStart, PreToolUse, UserPromptSubmit, etc.).

### 🔌 MCP Servers
Model Context Protocol servers that extend Claude Code with new tools and integrations.

Available MCP integrations:
- **Sequential Thinking** (base plugin) - Enhanced reasoning for complex problems
- **Codex** (codex-mcp plugin) - Code analysis and review capabilities
- **Serena** (serena-mcp plugin) - IDE assistant with project context

### 🛠️ Skills
Specialized capabilities that provide domain knowledge and workflows. *(Coming soon)*

## Contributing

We welcome plugin contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Steps

1. Fork this repository
2. Create your plugin in the `plugins/` directory
3. Add a `plugin.json` manifest
4. Include a detailed README
5. Register your plugin in `.claude-plugin/marketplace.json`
6. Submit a pull request

## Plugin Structure

Each plugin should follow this structure:

```
plugins/
└── your-plugin/
    ├── plugin.json          # Required: Plugin manifest
    ├── README.md            # Required: Documentation
    └── [plugin files]       # Your plugin implementation
```

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
