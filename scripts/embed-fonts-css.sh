#!/usr/bin/env bash
set -euo pipefail

CSS_FILE="$1"

if [[ ! -f "$CSS_FILE" ]]; then
  echo "Error: CSS file not found: $CSS_FILE" >&2
  exit 1
fi

python3 -c "
import re, base64, sys, os

css_path = sys.argv[1]
css_dir = os.path.dirname(os.path.abspath(css_path))

with open(css_path, 'r') as f:
    css = f.read()

def replace_url(match):
    path = match.group(1)
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.join(css_dir, path)
    if not os.path.exists(path):
        print(f'Warning: Font not found: {path}', file=sys.stderr)
        return match.group(0)
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    ext = os.path.splitext(path)[1].lstrip('.')
    mime = f'font/{ext}'
    return f\"url('data:{mime};base64,{b64}')\"

result = re.sub(r\"url\(['\\\"]?([^)'\\\"]+\.woff2)['\\\"]?\)\", replace_url, css)
print(result)
" "$CSS_FILE"
