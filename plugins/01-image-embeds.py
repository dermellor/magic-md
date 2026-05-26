#!/usr/bin/env python3
"""Resolve Obsidian ![[image.ext]] embeds to standard Markdown image syntax.

Env vars (set by render.sh):
  MAGIC_MD_INPUT_DIR  – directory of the source Markdown file
  MAGIC_MD_VAULT_ROOT – root directory for file lookup fallback
"""

import os
import re
import sys


def find_file(name, input_dir, vault_root):
    candidate = os.path.join(input_dir, name)
    if os.path.exists(candidate):
        return os.path.abspath(candidate)
    if vault_root:
        for root, dirs, files in os.walk(vault_root):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            if name in files:
                return os.path.abspath(os.path.join(root, name))
    return None


def replace_embed(match):
    filename = match.group(1)
    input_dir = os.environ.get("MAGIC_MD_INPUT_DIR", ".")
    vault_root = os.environ.get("MAGIC_MD_VAULT_ROOT", "")
    path = find_file(filename, input_dir, vault_root)
    if path:
        return f"![]({path})"
    print(f"Warning: Image not found: {filename}", file=sys.stderr)
    return match.group(0)


content = sys.stdin.read()
content = re.sub(
    r"!\[\[([^\]]+\.(?:svg|png|jpg|jpeg|gif|webp))\]\]", replace_embed, content
)
print(content, end="")
