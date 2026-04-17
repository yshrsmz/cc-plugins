---
description: プラグインのファイルを変更したら plugin.json の version を必ず bump する
globs: plugins/**
---

`plugins/<name>/` 配下のファイル（commands, skills, hooks, agents, MCP 定義など）を変更した場合は、同一 PR 内で `plugins/<name>/.claude-plugin/plugin.json` の `version` を semver に従って bump すること。

- bug fix / 内部修正のみ → patch
- 後方互換のある機能追加・改善 → minor
- 破壊的変更 → major

## bump は PR 単位で 1 回だけ

bump は PR 全体で 1 回行えば十分。PR レビューで追加修正コミットを入れる場合でも、変更の性質（patch / minor / major）が既存 bump の範囲に収まるなら追加 bump は不要。

- 例: PR で minor bump 済み（1.0.0 → 1.1.0）→ レビュー指摘で typo 修正を追加コミット → 追加 bump **不要**
- 例外: レビュー途中で変更の性質が上がった場合のみ bump を引き上げる（例: 元々 patch bump だったが破壊的変更を追加する必要が出たので major に上げる）

理由: マージ後にユーザーに届くのは PR 全体であり、commit 単位で version を刻む必要はない。毎 commit bump すると PR が無駄にコンフリクトしやすくなり、履歴も汚れる。

## なぜ bump が必須か

bump し忘れると Claude Code 側のプラグイン自動更新が走らず、ユーザーに変更が届かない。
