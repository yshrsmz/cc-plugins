# writing

Prose editing skills for Japanese technical documents — detecting the tells of AI-generated writing, and cleaning up redundancy. **Both skills read and rewrite Japanese text, and their output is in Japanese.**

## Skills

### `deai`

Detects "AI-ness" (AI 生成感) in a Japanese document across 21 categories — overblown significance, AI-favoured vocabulary, uniform sentence rhythm, over-structured headings, and writing that only makes sense to someone who followed the conversation that produced it — then proposes concrete rewrites and applies the ones you approve.

Trigger phrases include 「AI感を消して」, 「AIっぽさを除去して」, 「人間が書いたように直して」, and 「経緯を知らない読者向けに書き直して」.

The skill runs as a forked subagent (`context: fork`) so that it reads the document **without** the conversation that produced it. That isolation is what makes category 21 (writing that depends on conversational context) detectable at all — an author who still holds the context reads those passages as self-evident.

### `dedupe-cleanup`

Finds redundant and duplicated passages in a document and proposes rewrites. Takes an optional file path as its argument.

Trigger phrases include 「ドキュメントの重複を直して」, 「冗長な表現を削除して」, and 「文書の校正をして」.

`deai` deliberately leaves the generic redundancy patterns (「〜することができる」「〜を行う」「〜という」) to this skill rather than flagging them itself, because they are ordinary wordiness rather than a tell of AI authorship. Broader categories still overlap — both skills flag synonym repetition and empty modifiers — so running them on the same document will surface some findings twice.

## Installation

Install via the `yshrsmz-cc-plugins` marketplace:

```
/plugin install writing@yshrsmz-cc-plugins
```

## License

Apache-2.0
