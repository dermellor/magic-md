#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$SKILL_DIR/scripts/template.html"

DESIGN="default"
DESIGN_SET=false
OUTPUT=""
OPEN=false

INPUT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --design)  DESIGN="$2"; DESIGN_SET=true; shift 2 ;;
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

if [[ -z "$OUTPUT" ]]; then
  BASENAME="$(basename "$INPUT" .md)"
  OUTPUT="${BASENAME}.html"
fi

# Find .magic-md.conf by walking up from input file's directory
CONFIG_FILE=""
CONFIG_DIR=""
search_dir="$(cd "$(dirname "$INPUT")" && pwd)"
while [[ "$search_dir" != "/" ]]; do
  if [[ -f "$search_dir/.magic-md.conf" ]]; then
    CONFIG_FILE="$search_dir/.magic-md.conf"
    CONFIG_DIR="$search_dir"
    break
  fi
  search_dir="$(dirname "$search_dir")"
done

# Parse config: simple key=value format
# design=sipgate
# designs_dir=path/to/designs
# plugin=path/to/plugin.py
config_design=""
config_designs_dir=""
EXTRA_PLUGINS=()

if [[ -n "$CONFIG_FILE" ]]; then
  while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ -z "$key" || "$key" == \#* ]] && continue
    key="$(echo "$key" | xargs)"
    value="$(echo "$value" | xargs)"
    # Resolve relative paths
    if [[ -n "$value" && "$value" != /* ]]; then
      resolved="$CONFIG_DIR/$value"
    else
      resolved="$value"
    fi
    case "$key" in
      design)      config_design="$value" ;;
      designs_dir) config_designs_dir="$resolved" ;;
      plugin)
        if [[ -f "$resolved" && -x "$resolved" ]]; then
          EXTRA_PLUGINS+=("$resolved")
        else
          echo "Warning: Plugin not found or not executable: $resolved" >&2
        fi
        ;;
    esac
  done < "$CONFIG_FILE"
fi

# Config design applies only if --design wasn't explicitly passed
if [[ -n "$config_design" && "$DESIGN_SET" == false ]]; then
  DESIGN="$config_design"
fi

export MAGIC_MD_INPUT_DIR="$(cd "$(dirname "$INPUT")" && pwd)"
export MAGIC_MD_VAULT_ROOT="${VAULT_ROOT:-$(pwd)}"
export MAGIC_MD_DESIGN="$DESIGN"

# Design lookup: config dir first, then bundled
export MAGIC_MD_DESIGNS_DIR="$SKILL_DIR/designs"
if [[ -n "$config_designs_dir" && -f "$config_designs_dir/$DESIGN.css" ]]; then
  export MAGIC_MD_DESIGNS_DIR="$config_designs_dir"
fi

TMPFILE="$(mktemp /tmp/render-XXXXXX.md)"
trap 'rm -f "$TMPFILE"' EXIT
cat "$INPUT" > "$TMPFILE"

# Collect all plugins: bundled + extra, sorted together by basename
ALL_PLUGINS=()
while IFS= read -r p; do
  ALL_PLUGINS+=("$p")
done < <(find "$SKILL_DIR/plugins" -maxdepth 1 -type f -perm +111 2>/dev/null)
for p in "${EXTRA_PLUGINS[@]+"${EXTRA_PLUGINS[@]}"}"; do
  ALL_PLUGINS+=("$p")
done

# Sort by basename so numeric prefixes control order across all sources
IFS=$'\n' SORTED_PLUGINS=($(for p in "${ALL_PLUGINS[@]+"${ALL_PLUGINS[@]}"}"; do
  echo "$(basename "$p")|$p"
done | sort -t'|' -k1,1 | cut -d'|' -f2))
unset IFS

for plugin in "${SORTED_PLUGINS[@]+"${SORTED_PLUGINS[@]}"}"; do
  PLUGIN_TMPFILE="$(mktemp /tmp/render-plugin-XXXXXX.md)"
  if "$plugin" < "$TMPFILE" > "$PLUGIN_TMPFILE"; then
    mv "$PLUGIN_TMPFILE" "$TMPFILE"
  else
    echo "Warning: Plugin $(basename "$plugin") failed, skipping" >&2
    rm -f "$PLUGIN_TMPFILE"
  fi
done

pandoc "$TMPFILE" \
  --from markdown \
  --to html5 \
  --standalone \
  --template "$TEMPLATE" \
  --metadata title="$(basename "$INPUT" .md)" \
  --wrap=none \
  -o "$OUTPUT"

echo "Rendered: $OUTPUT (design: $DESIGN)"

if $OPEN; then
  open "$OUTPUT"
fi
