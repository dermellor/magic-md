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

## Plugins

Everything is a plugin. Executable scripts in `plugins/`, run in filename order before Pandoc. Each reads from stdin, writes to stdout.

### Bundled plugins

| Plugin | Description |
|--------|-------------|
| `00-design.sh` | Injects CSS design as `<style>` block (reads `MAGIC_MD_DESIGN`) |
| `01-image-embeds.py` | Resolves `![[image.ext]]` to standard Markdown image syntax |
| `02-callouts.py` | Converts `> [!type]` callouts to styled HTML divs |

Remove or replace any bundled plugin you don't need.

### Config file

Place a `.magic-md.conf` in your project root. `render.sh` searches upward from the input file.

```conf
# .magic-md.conf
design=sipgate
designs_dir=config/designs
plugin=config/plugins/05-shortcodes.py
plugin=config/plugins/06-diagrams.sh
```

| Key | Description |
|-----|-------------|
| `design` | Default design name (overridden by `--design`) |
| `designs_dir` | Path to additional designs directory (relative to config) |
| `plugin` | Path to an extra plugin (repeatable, relative to config) |

### Designs

Designs are CSS files. The `00-design.sh` plugin reads `MAGIC_MD_DESIGN`, loads the matching CSS, embeds fonts as Base64, and prepends a `<style>` block. The `default` design uses system fonts. Custom designs can live in the bundled `designs/` or in a `designs_dir` from the config.

### Environment variables

`render.sh` exports these env vars for plugins to use (all optional):

| Variable | Description |
|----------|-------------|
| `MAGIC_MD_INPUT_DIR` | Absolute path to the source file's directory |
| `MAGIC_MD_VAULT_ROOT` | Root directory for file lookups (defaults to cwd) |
| `MAGIC_MD_DESIGN` | Name of the active CSS design |
| `MAGIC_MD_DESIGNS_DIR` | Absolute path to the resolved designs directory |

### Writing a plugin

1. Create an executable script (any language)
2. Name it with a numeric prefix for ordering: `03-myplugin.py`
3. Read from stdin, write to stdout
4. Exit 0 on success (non-zero skips the plugin with a warning)

Bundled plugins go in `plugins/`. Extra plugins are referenced in `.magic-md.conf` and sorted together by basename.

## Workflow

1. Identify the Markdown file
2. Run: `bash .skills/render/scripts/render.sh "My Article.md" --open`
3. Design and plugins are resolved from `.magic-md.conf` (if present) or defaults
