#!/usr/bin/env python3
"""Convert Obsidian callouts (> [!type]) to styled HTML divs."""

import re
import sys

lines = sys.stdin.read().split("\n")
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

print("\n".join(output), end="")
