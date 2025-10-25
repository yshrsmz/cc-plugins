# Format JSON Command

A utility slash command that finds and formats all JSON files in your project with consistent 2-space indentation.

## Installation

Add this marketplace to Claude Code:
```bash
/plugin marketplace add yshrsmz/cc-plugins
```

Then install the plugin:
```bash
/plugin install format-json
```

## Usage

Run the command in your project directory:
```
/format-json
```

The command will:
- Recursively find all `.json` files
- Parse and validate each file
- Format with 2-space indentation
- Report results and any errors

## Example Output

```
Formatting JSON files...

✓ package.json - formatted
✓ tsconfig.json - formatted
✓ .claude-plugin/marketplace.json - formatted
✗ broken.json - Invalid JSON: Unexpected token

Formatted 3 files, 1 error
```

## Use Cases

- Clean up messy JSON configurations
- Ensure consistent formatting across team
- Fix indentation before committing
- Validate JSON syntax

## Files

- `plugin.json` - Plugin manifest
- `format-json.md` - Command prompt
- `README.md` - This file
