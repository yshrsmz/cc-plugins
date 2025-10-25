# Contributing to Claude Code Plugins

Thank you for your interest in contributing to the Claude Code Plugins marketplace! This guide will help you submit high-quality plugins.

## Table of Contents

- [Quick Start](#quick-start)
- [Plugin Types](#plugin-types)
- [Submission Guidelines](#submission-guidelines)
- [Plugin Structure](#plugin-structure)
- [Testing Your Plugin](#testing-your-plugin)
- [Pull Request Process](#pull-request-process)

## Quick Start

1. **Fork the repository**
   ```bash
   gh repo fork yshrsmz/cc-plugins
   cd cc-plugins
   ```

2. **Create your plugin directory**
   ```bash
   mkdir -p plugins/your-plugin-name
   cd plugins/your-plugin-name
   ```

3. **Create required files**
   - `plugin.json` - Plugin manifest (required)
   - `README.md` - Documentation (required)
   - Your plugin implementation files

4. **Register your plugin**
   Add your plugin to `.claude-plugin/marketplace.json`

5. **Test your plugin**
   Install and test locally before submitting

6. **Submit a pull request**

## Plugin Types

### Slash Commands

Custom commands invoked with `/command-name`.

**Structure:**
```
plugins/your-command/
├── plugin.json
├── README.md
└── your-command.md    # Command prompt
```

**plugin.json example:**
```json
{
  "name": "your-command",
  "version": "1.0.0",
  "author": {
    "name": "Your Name",
    "email": "your.email@example.com"
  },
  "description": "Brief description",
  "license": "Apache-2.0",
  "keywords": ["command", "utility"],
  "commands": {
    "your-command": "./your-command.md"
  }
}
```

### Hooks

Event-driven shell scripts that respond to Claude Code events.

**Available hooks:**
- `PreToolUse` - Before Claude executes a tool
- `PostToolUse` - After a tool completes successfully
- `Notification` - When Claude sends notifications
- `UserPromptSubmit` - When user submits a prompt
- `Stop` - When the main agent finishes responding
- `SubagentStop` - When a subagent completes
- `PreCompact` - Before context compaction
- `SessionStart` - When session starts or resumes
- `SessionEnd` - When session terminates

**Structure:**
```
plugins/your-hook/
├── plugin.json
├── README.md
└── hook-script.sh     # Your hook implementation
```

**plugin.json example:**
```json
{
  "name": "your-hook",
  "version": "1.0.0",
  "description": "Brief description",
  "hooks": {
    "SessionStart": "./session-start.sh"
  }
}
```

### MCP Servers

Model Context Protocol servers that extend Claude Code capabilities.

**Structure:**
```
plugins/your-mcp-server/
├── plugin.json
├── README.md
└── server implementation files
```

### Skills

Specialized capabilities with domain knowledge.

**Structure:**
```
plugins/your-skill/
├── plugin.json
├── README.md
└── skill implementation files
```

## Submission Guidelines

### Quality Standards

✅ **DO:**
- Write clear, descriptive README files
- Include usage examples
- Test thoroughly before submitting
- Use semantic versioning
- Follow existing plugin naming conventions (kebab-case)
- Include appropriate keywords for discoverability
- Specify a license (Apache-2.0 recommended)
- Keep plugins focused on a single purpose

❌ **DON'T:**
- Submit untested plugins
- Include malicious or obfuscated code
- Use copyrighted material without permission
- Create duplicate functionality without improvement
- Include secrets, API keys, or credentials
- Submit plugins that require external paid services without disclosure

### Naming Conventions

- Use kebab-case: `my-awesome-plugin`
- Be descriptive but concise
- Avoid generic names like `utility` or `helper`
- For commands, use verb-noun format: `format-json`, `check-types`

### README Requirements

Your README must include:

1. **Title and description**
2. **Installation instructions**
3. **Usage examples**
4. **Configuration options** (if any)
5. **Requirements/dependencies** (if any)
6. **License information**

## Plugin Structure

### Required Files

```
plugins/your-plugin/
├── plugin.json          # REQUIRED: Plugin manifest
└── README.md            # REQUIRED: Documentation
```

### plugin.json Schema

**Minimal example:**
```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "What this plugin does"
}
```

**Complete example:**
```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "author": {
    "name": "Your Name",
    "email": "your.email@example.com",
    "url": "https://yoursite.com"
  },
  "description": "Detailed plugin description",
  "homepage": "https://github.com/you/plugin",
  "repository": {
    "type": "git",
    "url": "https://github.com/you/plugin"
  },
  "license": "Apache-2.0",
  "keywords": ["keyword1", "keyword2"],
  "commands": {
    "command-name": "./command.md"
  },
  "hooks": {
    "preCommit": "./pre-commit.sh"
  },
  "outputStyles": {
    "style-name": "./style.json"
  }
}
```

## Testing Your Plugin

### Local Testing

1. **Add marketplace locally:**
   ```bash
   /plugin marketplace add /path/to/cc-plugins
   ```

2. **List available plugins:**
   ```bash
   /plugin list
   ```

3. **Install your plugin:**
   ```bash
   /plugin install your-plugin-name
   ```

4. **Test functionality:**
   - For commands: Run `/your-command`
   - For hooks: Trigger the relevant event
   - For output styles: Apply and verify rendering

5. **Uninstall and reinstall:**
   ```bash
   /plugin uninstall your-plugin-name
   /plugin install your-plugin-name
   ```

### Testing Checklist

- [ ] Plugin installs without errors
- [ ] All documented features work as expected
- [ ] No console errors or warnings
- [ ] README instructions are accurate
- [ ] Examples in README are tested
- [ ] Plugin works in different scenarios
- [ ] Uninstall works cleanly

## Pull Request Process

1. **Ensure your plugin meets all requirements**
   - Has `plugin.json` and `README.md`
   - Is registered in `.claude-plugin/marketplace.json`
   - Has been tested locally
   - Follows naming conventions

2. **Create a descriptive PR**
   - Title: `Add [plugin-name] plugin` or `Update [plugin-name]`
   - Description should include:
     - What the plugin does
     - Type of plugin (command, hook, style, etc.)
     - Any special requirements
     - Testing performed

3. **PR template:**
   ```markdown
   ## Plugin Details

   **Name:** plugin-name
   **Type:** Slash Command / Hook / Output Style / MCP Server / Skill
   **Description:** Brief description of what it does

   ## Testing

   - [ ] Installed and tested locally
   - [ ] README examples verified
   - [ ] No errors in console
   - [ ] Works as documented

   ## Additional Notes

   Any special considerations, dependencies, or requirements.
   ```

4. **Address review feedback**
   - Respond to comments promptly
   - Make requested changes
   - Re-test after modifications

5. **After approval**
   - Squash commits if requested
   - Ensure CI passes (when available)
   - Plugin will be merged and available to all users

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and improve
- Focus on making the marketplace better for everyone

## Questions?

- Open an issue for questions about contributing
- Check existing plugins for examples
- Review [Claude Code documentation](https://docs.claude.com/en/docs/claude-code)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0, unless you specify a different license in your plugin's directory.

---

Thank you for contributing to the Claude Code Plugins marketplace!
