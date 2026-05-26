#!/usr/bin/env python3
"""Pre-process Obsidian Markdown for Pandoc rendering.

Resolves:
- ![[image.ext]] embeds -> standard markdown ![](absolute/path)
- > [!type] callouts -> <div class="callout callout-type"> HTML blocks
"""

import re
import sys
import os


def find_file(name, input_dir, vault_root):
    candidate = os.path.join(input_dir, name)
    if os.path.exists(candidate):
        return os.path.abspath(candidate)
    for root, dirs, files in os.walk(vault_root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if name in files:
            return os.path.abspath(os.path.join(root, name))
    return None


def resolve_image_embeds(content, input_dir, vault_root):
    def replace_embed(match):
        filename = match.group(1)
        path = find_file(filename, input_dir, vault_root)
        if path:
            return f"![]({path})"
        print(f"Warning: Image not found: {filename}", file=sys.stderr)
        return match.group(0)

    return re.sub(
        r"!\[\[([^\]]+\.(?:svg|png|jpg|jpeg|gif|webp))\]\]", replace_embed, content
    )


def convert_callouts(text):
    lines = text.split("\n")
    output = []
    i = 0
    while i < len(lines):
        m = re.match(r"^>\s*\[!(\w+)\]\s*(.*)", lines[i])
        if m:
            ctype = m.group(1).lower()
            title = m.group(2).strip()
            body_lines = []
            i += 1
            while i < len(lines) and re.match(r"^>", lines[i]):
                line = re.sub(r"^>\s?", "", lines[i])
                body_lines.append(line)
                i += 1
            while body_lines and not body_lines[0].strip():
                body_lines.pop(0)
            while body_lines and not body_lines[-1].strip():
                body_lines.pop()
            body = "\n".join(body_lines)
            title_html = (
                f'<strong class="callout-title">{title}</strong>' if title else ""
            )
            output.append(f'<div class="callout callout-{ctype}">')
            if title_html:
                output.append(title_html)
            output.append("")
            output.append(body)
            output.append("")
            output.append("</div>")
            output.append("")
        else:
            output.append(lines[i])
            i += 1
    return "\n".join(output)


def main():
    input_file = sys.argv[1]
    input_dir = sys.argv[2]
    vault_root = sys.argv[3]

    with open(input_file, "r") as f:
        content = f.read()

    content = resolve_image_embeds(content, input_dir, vault_root)
    content = convert_callouts(content)
    print(content)


if __name__ == "__main__":
    main()
