# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code プラグインマーケットプレースリポジトリ。プラグイン（commands, hooks, MCP servers, skills）を管理・配布する。ビルドシステムやパッケージマネージャーは不要で、マークダウンとシェルスクリプトで構成される。

## Architecture

```
.claude-plugin/marketplace.json   ← プラグインレジストリ（全プラグインの一覧と source パス）
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json    ← プラグインマニフェスト（name, version, description, author）
    commands/                     ← スラッシュコマンド（.md ファイル）
    skills/                       ← Agent Skills（<name>/SKILL.md）
    hooks/                        ← hooks.json + スクリプト
    .mcp.json                     ← MCP サーバー定義
output-styles/                    ← カスタム出力スタイル定義
```

**重要**: `commands/`, `skills/`, `agents/`, `hooks/` はプラグインルートに配置する。`.claude-plugin/` の中には `plugin.json` のみ。

## Testing

ビルドやユニットテストはない。プラグインの動作確認はローカルで行う:

```bash
claude --plugin-dir ./plugins/<plugin-name>
```

## Naming Conventions

- プラグイン名・コマンド名・ファイル名: kebab-case
- ブランチ名: `feature/add-auth`, `fix/login-bug` 等の kebab-case

## Contribution Guidelines

新規プラグイン作成時は `CONTRIBUTING.md` を参照。プラグインの品質基準、ディレクトリ構造の詳細、提出プロセスが記載されている。
