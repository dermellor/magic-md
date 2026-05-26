#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESIGNS_DIR="$SKILL_DIR/designs"
PLUGINS_DIR="$SKILL_DIR/plugins"
TEMPLATE="$SKILL_DIR/scripts/template.html"

DESIGN="default"
OUTPUT=""
OPEN=false

INPUT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --design)  DESIGN="$2"; shift 2 ;;
    --output)  OUTPUT="$2"; shift 2 ;;
    --open)    OPEN=true; shift ;;
    -*)        echo "Unknown option: $1" >&2; exit 1 ;;
    *)         INPUT="$1"; shift ;;
  esac
done

if [[ -z "$INPUT" ]]; then
  echo "Usage: render.sh <input.md> [--design name] [--output path.html] [--open]" >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "Error: File not found: $INPUT" >&2
  exit 1
fi

CSS_FILE="$DESIGNS_DIR/$DESIGN.css"
if [[ ! -f "$CSS_FILE" ]]; then
  echo "Error: Design not found: $DESIGN (expected $CSS_FILE)" >&2
  echo "Available designs:" >&2
  ls "$DESIGNS_DIR"/*.css 2>/dev/null | xargs -n1 basename | sed 's/\.css$//' >&2
  exit 1
fi

if [[ -z "$OUTPUT" ]]; then
  BASENAME="$(basename "$INPUT" .md)"
  OUTPUT="${BASENAME}.html"
fi

CSS_CONTENT="$(bash "$SKILL_DIR/scripts/embed-fonts-css.sh" "$CSS_FILE")"

export MAGIC_MD_INPUT_DIR="$(cd "$(dirname "$INPUT")" && pwd)"
export MAGIC_MD_VAULT_ROOT="${VAULT_ROOT:-$(pwd)}"
export MAGIC_MD_DESIGN="$DESIGN"

TMPFILE="$(mktemp /tmp/render-XXXXXX.md)"
trap 'rm -f "$TMPFILE"' EXIT
cat "$INPUT" > "$TMPFILE"

# Plugin pipeline: run all executable scripts in plugins/ sorted by filename
if [[ -d "$PLUGINS_DIR" ]]; then
  for plugin in $(find "$PLUGINS_DIR" -maxdepth 1 -type f -executable 2>/dev/null | sort); do
    PLUGIN_TMPFILE="$(mktemp /tmp/render-plugin-XXXXXX.md)"
    if "$plugin" < "$TMPFILE" > "$PLUGIN_TMPFILE"; then
      mv "$PLUGIN_TMPFILE" "$TMPFILE"
    else
      echo "Warning: Plugin $(basename "$plugin") failed, skipping" >&2
      rm -f "$PLUGIN_TMPFILE"
    fi
  done
fi

pandoc "$TMPFILE" \
  --from markdown \
  --to html5 \
  --standalone \
  --template "$TEMPLATE" \
  --variable "design-css=$CSS_CONTENT" \
  --variable "design-name=$DESIGN" \
  --metadata title="$(basename "$INPUT" .md)" \
  --wrap=none \
  -o "$OUTPUT"

echo "Rendered: $OUTPUT (design: $DESIGN)"

if $OPEN; then
  open "$OUTPUT"
fi
