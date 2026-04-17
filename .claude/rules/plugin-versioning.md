---
description: プラグインのファイルを変更したら plugin.json の version を必ず bump する
globs: plugins/**
---

`plugins/<name>/` 配下のファイル（commands, skills, hooks, agents, MCP 定義など）を変更した場合は、同一 PR 内で `plugins/<name>/.claude-plugin/plugin.json` の `version` を semver に従って bump すること。

- bug fix / 内部修正のみ → patch
- 後方互換のある機能追加・改善 → minor
- 破壊的変更 → major

bump し忘れると Claude Code 側のプラグイン自動更新が走らず、ユーザーに変更が届かない。
