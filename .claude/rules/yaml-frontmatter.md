プラグイン配下の Agent / Skill ファイル（`plugins/<name>/agents/*.md`, `plugins/<name>/skills/*/SKILL.md`, `plugins/<name>/commands/*.md` など）の YAML frontmatter で `description:` を書く場合は、folded block scalar (`>-`) を使うこと。

```yaml
---
name: foo
description: >-
  ここに 1 行で説明を書く。コロン `:` や引用符 `"` `'`、`<example>` のような XML 風タグを含めても安全。
tools: Read, Grep, Glob
model: opus
---
```

## なぜ

description には Anthropic の agent 規約で `<example>Context: ... user: "..." assistant: "..."</example>` のような例を埋め込むケースがあり、その中の `Context:` `user:` `assistant:` などが YAML から見ると「コロン + スペース」で mapping key と解釈されパースエラーになる（`mapping values are not allowed in this context`）。

`>-` は folded scalar で末尾改行を strip するため、

- 内部の `:` `"` `'` `<` `>` 等をエスケープしなくてよい
- 出力上は単一行の文字列としてパースされる（折り返し位置のスペースは保持されるが、改行は空白に畳まれる）
- 末尾の余計な改行が付かない

という性質があり、description 全般に最も安全。

## 適用範囲

- `description:` は短くてもコロン等を含まなくても、一貫性のため必ず `>-` を使う
- 内容は次行にインデント 2 スペースで書く
- `name:`, `tools:`, `model:`, `argument-hint:`, `disable-model-invocation:` などの単純なスカラ値は通常の書き方で構わない（block scalar にする必要はない）

## 既存ファイルを編集するとき

description を編集する際、まだ素のスカラ書きになっていれば `>-` 形式に直すこと。新規ファイルは最初から `>-` で書く。
