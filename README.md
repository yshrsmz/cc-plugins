# Claude Code Plugins

A community-driven marketplace for Claude Code extensions and plugins.

## Quick Start

Add this marketplace to your Claude Code:

```bash
/plugin marketplace add yshrsmz/cc-plugins
```

Browse available plugins:

```bash
/plugin list
```

Install a plugin:

```bash
/plugin install <plugin-name>
```

## Available Plugins

### Slash Commands

- **hello-command** - Simple greeting command with fun tech facts
- **format-json** - Format all JSON files in your project with consistent indentation

### Hooks

- **session-logger** - Log session start and end events to track Claude Code usage

### Output Styles

- **minimal-style** - Clean, minimal output style with subtle colors

## Plugin Categories

### 💬 Slash Commands
Custom commands that can be invoked with `/` in Claude Code to automate workflows.

### 🪝 Hooks
Event-driven shell commands that execute in response to Claude Code events (SessionStart, PreToolUse, UserPromptSubmit, etc.).

### 🎨 Output Styles
Custom formatting styles to personalize Claude Code's appearance.

### 🔌 MCP Servers
Model Context Protocol servers that extend Claude Code with new tools and integrations. *(Coming soon)*

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
