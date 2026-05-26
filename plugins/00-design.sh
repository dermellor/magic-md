#!/usr/bin/env bash
set -euo pipefail

# Injects CSS design as a <style> block at the top of the Markdown.
# Pandoc passes raw HTML through, so the style ends up in the final output.
#
# Env vars (set by render.sh):
#   MAGIC_MD_DESIGN      – design name (e.g. "default", "sipgate")
#   MAGIC_MD_DESIGNS_DIR – absolute path to designs/ directory
#
# Also runs embed-fonts-css.sh to inline font files as Base64.

DESIGN="${MAGIC_MD_DESIGN:-default}"
DESIGNS_DIR="${MAGIC_MD_DESIGNS_DIR:-}"

if [[ -z "$DESIGNS_DIR" ]]; then
  echo "Error: MAGIC_MD_DESIGNS_DIR not set" >&2
  exit 1
fi

CSS_FILE="$DESIGNS_DIR/$DESIGN.css"

if [[ ! -f "$CSS_FILE" ]]; then
  echo "Error: Design not found: $CSS_FILE" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)/scripts"
CSS_CONTENT="$(bash "$SCRIPT_DIR/embed-fonts-css.sh" "$CSS_FILE")"

echo "<style>"
echo "$CSS_CONTENT"
echo "</style>"
echo ""
cat
