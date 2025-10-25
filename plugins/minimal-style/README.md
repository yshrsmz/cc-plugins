# Minimal Output Style

A clean, minimal output style for Claude Code with subtle colors and reduced visual noise.

## Installation

Add this marketplace to Claude Code:
```bash
/plugin marketplace add yshrsmz/cc-plugins
```

Then install the plugin:
```bash
/plugin install minimal-style
```

## Features

- Subtle, muted color palette
- High readability
- Low visual distraction
- Clean code blocks
- Distinct but gentle error/warning colors

## Color Scheme

- **Assistant text**: Light gray (#E0E0E0)
- **User text**: Medium gray (#A0A0A0), bold
- **System messages**: Dark gray (#808080), italic
- **Errors**: Soft red (#FF6B6B)
- **Success**: Teal (#4ECDC4)
- **Warnings**: Yellow (#FFE66D)
- **Info**: Mint (#95E1D3)
- **Code blocks**: Light gray on dark background
- **Links**: Blue (#6C9BCF), underlined

## Preview

```
User: Hello Claude
Assistant: Hello! How can I help you today?
System: Command completed successfully
Error: File not found
Success: Tests passed
Warning: Deprecated API usage
Info: 5 files changed
```

## Customization

Edit `minimal.json` to adjust:
- Colors (hex values)
- Text formatting (bold, italic, underline)
- Background colors

## Files

- `plugin.json` - Plugin manifest
- `minimal.json` - Output style definition
- `README.md` - This file
