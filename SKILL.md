---
name: render
description: Renders Markdown files to styled, standalone HTML with embedded fonts. Use when the user wants to render, export, or print a Markdown document.
argument-hint: <path/to/file.md> [--design name]
allowed-tools:
  - Bash(bash .skills/render/scripts/render.sh *)
  - Bash(bash .skills/render/scripts/embed-fonts-css.sh *)
---

# Render

Converts Markdown files to styled, standalone HTML with embedded brand fonts.

## How it works

A shell script (`render.sh`) converts a Markdown file to a complete HTML file via Pandoc. The CSS design (including fonts as Base64) is embedded inline. The output is a standalone HTML file that can be opened in a browser, printed, or exported as PDF.

## Usage

```bash
bash .skills/render/scripts/render.sh <input.md> [--design name] [--output path.html] [--open]
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `<input.md>` | (required) | Path to the Markdown source file |
| `--design` | `default` | Name of the CSS design (without `.css`) |
| `--output` | `{name}.html` | Output path |
| `--open` | - | Open HTML in browser after rendering |

## Designs

Designs are CSS files in `designs/`. The `default` design uses system fonts. Add custom designs by placing a CSS file with `@font-face` declarations and styling for `.content`, headings, code, tables, blockquotes, and callouts.

Font `url()` paths in CSS are automatically converted to Base64 data URIs, so the output HTML is fully standalone.

## Plugins

Plugins extend the Markdown preprocessing pipeline. They are executable scripts in `plugins/`, run in filename order before Pandoc. Each plugin reads Markdown from stdin and writes transformed Markdown to stdout.

### Writing a plugin

1. Create an executable script in `plugins/` (any language)
2. Name it with a numeric prefix for ordering: `01-myplugin.py`
3. Read from stdin, write to stdout
4. Exit 0 on success (non-zero skips the plugin with a warning)

Example (`plugins/01-strip-comments.sh`):

```bash
#!/usr/bin/env bash
sed '/^%%/d'
```

### Built-in preprocessing

Before plugins run, the core preprocessor resolves:
- `![[image.ext]]` embeds to standard Markdown image syntax
- `> [!type]` callouts to styled HTML divs

Set `VAULT_ROOT` env var if your Markdown references files relative to a vault root.

## Workflow

1. Identify the Markdown file
2. Choose a design (default: `default`)
3. Run: `bash .skills/render/scripts/render.sh "My Article.md" --design default --open`
4. Output HTML is created at the specified path (or next to the input file)
