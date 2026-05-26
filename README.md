# magic-md

Markdown to styled, standalone HTML — as a Claude Code / Codex skill.

## Features

- Pandoc-based Markdown to HTML conversion
- CSS designs with automatic font embedding (Base64)
- Plugin pipeline for custom preprocessing (stdin/stdout)
- Bundled plugins for Obsidian syntax (image embeds, callouts)
- Standalone output (no external dependencies)

## Requirements

- [Pandoc](https://pandoc.org/) (`brew install pandoc`)
- Python 3
- Bash

## Installation

Add as a Git submodule to your project:

```bash
git submodule add https://github.com/dermellor/magic-md.git .skills/render
```

## Plugins

Everything is a plugin. Three are bundled:

| Plugin | What it does |
|--------|-------------|
| `00-design.sh` | Injects CSS design as `<style>` block |
| `01-image-embeds.py` | `![[image.ext]]` → standard Markdown images |
| `02-callouts.py` | `> [!type]` → styled HTML divs |

Add your own via `.magic-md.conf` in your project:

```conf
design=sipgate
designs_dir=config/designs
plugin=config/plugins/05-shortcodes.py
```

Extra plugins are sorted with bundled ones by filename prefix. See [SKILL.md](SKILL.md) for full documentation.

## License

MIT
