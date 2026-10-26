# AGENTS.md

This file provides shared guidance to Claude Code and Codex when working with this repository.

## Project Overview

Claude Code と Codex に対応するプラグインマーケットプレースリポジトリ。プラグイン（commands, hooks, MCP servers, skills）を管理・配布する。ビルドシステムやパッケージマネージャーは不要で、マークダウン・JSON 設定・シェルスクリプトと、検証用 Python コードで構成される。

## Architecture

```
.claude-plugin/marketplace.json   ← Claude Code のレジストリ
.agents/plugins/marketplace.json  ← Codex のレジストリ
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json    ← Claude Code マニフェスト
    plugin.json                   ← Codex 用 Agent Plugins 1.0 マニフェスト
    agents/                       ← Claude Code エージェント定義。Codex では本文をサブエージェントへの指示として再利用
    commands/                     ← スラッシュコマンド（.md ファイル）
    skills/                       ← Agent Skills（<name>/SKILL.md）
    hooks/                        ← hooks.json + スクリプト
    .mcp.json                     ← MCP サーバー定義
output-styles/                    ← カスタム出力スタイル定義
```

**重要**: `commands/`, `skills/`, `agents/`, `hooks/` はプラグインルートに配置する。`.claude-plugin/` の中には `plugin.json` のみ。

## Testing

ビルドシステムや追加パッケージは不要。構造検証と回帰テストは Python 3 の標準ライブラリで実行する:

```bash
python3 scripts/validate_plugins.py
python3 -m unittest discover -s tests -v
```

Claude Code のマニフェスト検証（CLI 2.1.306 は個別 SKILL.md の検証には未対応）:

```bash
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate ./plugins/<plugin-name>
```

対話的な動作確認:

```bash
claude --plugin-dir ./plugins/<plugin-name>
```

## Naming Conventions

- プラグイン名・コマンド名・ファイル名: kebab-case
- ブランチ名: `feature/add-auth`, `fix/login-bug` 等の kebab-case

## Contribution Guidelines

新規プラグイン作成時は `CONTRIBUTING.md` を参照。プラグインの品質基準、ディレクトリ構造の詳細、提出プロセスが記載されている。

## Cross-host Maintenance

- スキルとレビュー基準は `plugins/` 内で共有する。実行環境固有の呼び出しだけ分岐し、Codex 用にスキル本文を複製しない。
- プラグイン内のファイルを変更したら、両マニフェストの `version` を同じ値で更新する。後方互換の機能追加は minor、修正は patch、破壊的変更は major。PR 単位で 1 回更新する。
- 新規プラグインは両マーケットプレースに登録する。手動起動限定のスキルは Claude の `disable-model-invocation: true` と Codex の `agents/openai.yaml` の `policy.allow_implicit_invocation: false` を揃える。
- `agents/*.md` の Claude 向け frontmatter を Codex のカスタムエージェント登録と見なさない。Codex ではスキルが定義本文を読み、汎用サブエージェントへ渡す。
- `.claude/rules/yaml-frontmatter.md` と `.claude/rules/skill-validation.md` を読み、frontmatter とスキル品質の規約に従う。スキルの簡素化やレビュー観点の削除には改変前後の比較評価が必要。
- ユーザーへの質問は `.claude/rules/ask-user-question.md` に従い、本文に書かずに質問ツールで行う。
- Git 操作には `plugins/github/skills/git-operations/SKILL.md` の規約に従う。
- Markdown は段落をハードラップしない。
