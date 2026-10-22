# Contributing to Claude Code / Codex Plugins

This marketplace distributes the same skills to Claude Code and Codex. Keep workflows and domain knowledge shared, and isolate host-specific tool calls and configuration. Read [AGENTS.md](AGENTS.md) before editing; Claude Code imports it through `CLAUDE.md`.

## Quick Start

1. Fork this repository and create a working branch.
2. Add your plugin under `plugins/<plugin-name>/` using kebab-case names.
3. Add both manifests shown below, with matching name, version, description, and author.
4. Register the plugin in both marketplace catalogs.
5. Validate the package and test the affected workflows in both hosts.
6. Submit a pull request describing behavior, requirements, and validation results.

## Package Structure

```text
.claude-plugin/marketplace.json       # Claude Code catalog
.agents/plugins/marketplace.json      # Codex catalog
plugins/your-plugin/
├── .claude-plugin/
│   └── plugin.json                   # Claude Code manifest
├── plugin.json                      # Agent Plugins 1.0 manifest for Codex
├── README.md                        # Installation, usage, requirements, license
├── skills/
│   └── your-skill/
│       ├── SKILL.md                  # Shared workflow
│       └── agents/
│           └── openai.yaml           # Required here only for manual-only skills
├── references/                      # Optional shared runtime/domain instructions
├── agents/                          # Optional Claude Code agent definitions
├── commands/                        # Optional Claude Code commands
├── hooks/                           # Optional host-specific hooks and scripts
└── scripts/                         # Optional supporting scripts
```

Keep referenced files inside the plugin so an installed copy is self-contained. Use relative Markdown links, not symlinks or references to sibling plugins. `skills/<name>/agents/openai.yaml` is skill metadata; it does not register a named Codex subagent. Claude Code's `agents/*.md` definitions are also not automatically registered in Codex. Follow the existing `agent-review` and `pr-review` approach: read the definition body and pass it to a Codex subagent.

## Manifests

Claude Code: `plugins/your-plugin/.claude-plugin/plugin.json`:

```json
{
  "name": "your-plugin",
  "version": "1.0.0",
  "description": "What the plugin does",
  "author": {"name": "Your Name"}
}
```

Codex: `plugins/your-plugin/plugin.json`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "your-plugin",
  "version": "1.0.0",
  "description": "What the plugin does",
  "author": {"name": "Your Name"},
  "license": "Apache-2.0",
  "extensions": {
    "com.openai": {
      "interface": {
        "displayName": "Your Plugin",
        "shortDescription": "A concise workflow summary",
        "developerName": "Your Name",
        "category": "Productivity",
        "capabilities": []
      }
    }
  }
}
```

Use a short description of at most 30 characters. Portable skills are discovered from the root `skills/` directory; do not put Claude-specific `dependencies`, `agents`, or component paths in the portable manifest. The existing `.claude-plugin/plugin.json` remains the Claude manifest. A separate `.codex-plugin/plugin.json` is unnecessary for the portable format used here.

When changing plugin content, bump both manifests to the same version once per PR: patch for fixes, minor for compatible new functionality, major for breaking changes. Keep package identity and publisher information consistent. Do not add speculative metadata or placeholders for external connections.

## Marketplace Registration

Add an entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-plugin",
  "source": "./plugins/your-plugin",
  "description": "What the plugin does"
}
```

Add an entry to `.agents/plugins/marketplace.json`:

```json
{
  "name": "your-plugin",
  "source": {"source": "local", "path": "./plugins/your-plugin"},
  "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
  "category": "Productivity"
}
```

Paths are relative to the repository root, not the `.agents/plugins/` directory. Keep the marketplace name consistent across the two catalogs. The validation script checks this repository's local-source and policy conventions.

## Skills and Host Differences

Each `SKILL.md` starts with YAML frontmatter. Use folded block scalars for descriptions as required by `.claude/rules/yaml-frontmatter.md`:

```yaml
---
name: your-skill
description: >-
  Use when the user needs this specific workflow.
---
```

If a workflow must only run on explicit invocation, add `disable-model-invocation: true` to its frontmatter and create `agents/openai.yaml` beside the skill with this exact minimal policy:

```yaml
policy:
  allow_implicit_invocation: false
```

Otherwise omit that policy file. Put behavioral instructions in `SKILL.md` and supporting references. For host-specific behavior:

- Map Claude tool names to actual available Codex tools. Never assume an identical `Task`, `AskUserQuestion`, MCP tool prefix, model name, or environment variable exists.
- Ask in chat and wait for a response when a required question tool is unavailable.
- Respect available subagent concurrency. Wait for every requested result and preserve any required context isolation.
- Read applicable `AGENTS.md`, `CLAUDE.md`, and referenced rules. Resolve imports such as `@AGENTS.md`.
- Save Codex project learnings to `AGENTS.md` or referenced checked-in guidance and reusable workflows to `.agents/skills/<name>/SKILL.md`; do not silently save them to Claude-only memory or rules.
- Resolve bundled scripts from the installed skill location, not the user's working directory. Run shell scripts with `bash`, without `chmod`.
- Describe external tools and authentication requirements. The Firebase dependency in the Android Claude manifest does not configure Firebase MCP for Codex.

Claude-only commands, hooks, output styles, and MCP declarations are not automatically portable. If adding one, document the host support and test the relevant format. Portable MCP servers use root `mcp.json` with the Agent Plugins MCP schema, while Claude Code uses `.mcp.json`; do not assume the files or settings are merged. See the [official packaging documentation](https://developers.openai.com/plugins/build/plugins).

## Validation and Testing

Run the dependency-free structure checks and regression tests:

```bash
python3 scripts/validate_plugins.py
python3 -m unittest discover -s tests -v
```

These check catalog inventory, local sources, synchronized manifests, manual invocation policies, package containment, and relative Markdown links. They enforce repository conventions, not complete upstream JSON/YAML schemas.

With Claude Code installed, validate its catalog and each changed plugin. On CLI 2.1.306 this command checks manifests; passing an individual `SKILL.md` is not supported. The optional native-host regression tests use Codex app-server to parse all 14 skills from a separate copy of the plugin packages, without model calls, marketplace registration, or user configuration changes. If either CLI is missing, its integration tests are skipped.

```bash
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate ./plugins/your-plugin
```

For interactive Claude Code testing:

```bash
claude --plugin-dir ./plugins/your-plugin
```

For Codex, register the local checkout, inspect the catalog, and install the changed plugin:

```bash
codex plugin marketplace add /absolute/path/to/cc-plugins
codex plugin list --marketplace yshrsmz-cc-plugins --available
codex plugin add your-plugin@yshrsmz-cc-plugins
```

Start a fresh session and verify skill discovery and invocation. Desktop users can install from the plugin list instead. Test that manual-only skills remain manual, referenced files are available from the installed package, missing MCP tools produce setup guidance, and proposed edits or external writes wait for the required user decision. Exercise destructive workflows only against disposable fixtures or their dry-run mode. Do not post GitHub reviews or delete real branches as an installation test.

Existing review criteria must remain intact during portability work. If simplifying a skill or changing its triggering behavior, also follow the comparison-evaluation requirements in `.claude/rules/skill-validation.md`.

## Pull Requests

Use a descriptive title and explain the problem, resulting behavior, affected hosts, dependencies, and test results. Include any behavior that could not be exercised in a host. Before submitting, check:

- Both catalogs and manifests are present and consistent.
- Installation and usage examples match the supported hosts.
- New behavior has appropriate regression coverage and relevant checks pass.
- No secrets, local credentials, dependency directories, or unrelated changes are included.
- Naming follows kebab-case and versions follow SemVer.
- Licensing is stated; Apache-2.0 is the repository default.

Be respectful and constructive in reviews. Questions and plugin requests belong in [GitHub issues](https://github.com/yshrsmz/cc-plugins/issues). Contributions are licensed under Apache-2.0 unless a plugin directory specifies otherwise.
