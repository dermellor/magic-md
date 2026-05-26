# skill-render

A Claude Code / Codex skill that renders Markdown files to styled, standalone HTML.

## Features

- Pandoc-based Markdown to HTML conversion
- CSS designs with automatic font embedding (Base64)
- Plugin pipeline for custom preprocessing
- Standalone output (no external dependencies)

## Requirements

- [Pandoc](https://pandoc.org/) (`brew install pandoc`)
- Python 3
- Bash

## Installation

Add as a Git submodule to your project:

```bash
git submodule add https://github.com/marcelmellor/skill-render.git .skills/render
```

## Plugins

Plugins are executable scripts in `plugins/` that transform Markdown via stdin/stdout, run in filename order before Pandoc.

```bash
# Example: plugins/01-strip-comments.sh
#!/usr/bin/env bash
sed '/^%%/d'
```

See [SKILL.md](SKILL.md) for full documentation.

## License

MIT
