# writing

A prose editing skill for Japanese technical documents — detecting the tells of AI-generated writing, together with redundancy, duplication, inconsistent notation, and internal contradictions. **The skill reads and rewrites Japanese text, and its output is in Japanese.**

## Skills

### `deai`

Checks a Japanese document across 26 categories and returns a single list of findings with concrete rewrites, then applies the ones you approve.

- Categories 1–21 cover the tells of AI-generated writing — overblown significance, AI-favoured vocabulary, uniform sentence rhythm, over-structured headings, and writing that only makes sense to someone who followed the conversation that produced it
- Categories 22–26 cover general document quality — duplicated content, inconsistent notation (表記揺れ), sentence construction, statements that contradict each other, and ordinary wordiness

Detection is split between two subagents that run in parallel — one for categories 1–21, one for 22–26 — so that neither set of checks crowds out the other. The skill then merges their findings: when one passage falls under several categories, it is reported once with all the categories listed, and gets one rewrite that satisfies all of them. Takes an optional file path as its argument.

Trigger phrases include 「AI感を消して」, 「AIっぽさを除去して」, 「人間が書いたように直して」, 「経緯を知らない読者向けに書き直して」, 「ドキュメントの重複を直して」, 「冗長な表現を削除して」, and 「文書の校正をして」.

Every judgement — detection, merging, and applying the edits — is made by subagents that never see the conversation that produced the document. The skill itself only launches them, waits for them, and asks you which findings to apply; it does not read or edit the document. The subagents pass their results to each other through files in a working directory, so the findings do not pile up in the calling session's context. That isolation is what makes category 21 (writing that depends on conversational context) detectable at all — an author who still holds the context reads those passages as self-evident. Pass the file path explicitly; the skill does not infer it from the conversation.

The skill does not run as a fork (`context: fork`). Subagents may run in the background and report back to the session that launched them; a forked skill finishes its turn before the detectors return, so their findings reached a caller that had no one to merge them. (Up to 1.0.0 the skill was forked and stopped after launching the detectors in interactive sessions.)

### Removed in 1.0.0: `dedupe-cleanup`

`dedupe-cleanup` was merged into `deai`. Running both on the same document produced the same finding twice — often with conflicting rewrites — because `deai` reached the same passages through its own categories. Use `writing:deai` for redundancy and duplication checks as well.

## Installation

Install via the `yshrsmz-cc-plugins` marketplace:

```
/plugin install writing@yshrsmz-cc-plugins
```

## License

Apache-2.0
