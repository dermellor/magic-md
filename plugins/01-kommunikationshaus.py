#!/usr/bin/env python3
"""Convert Kommunikationshaus Markdown to a styled HTML grid layout.

Detects documents with [!MISSION] + [!POSITIONING] callouts followed by
Why/What/How pillars (## H2) containing cards (### H3) with #### Proofs.
Replaces the body with styled HTML. Passes non-matching documents through.

Must run before 02-callouts.py (basename sort: 01-k > 01-i, so after
01-image-embeds but before 02-callouts).
"""

import re
import sys


def parse(lines):
    """Parse Kommunikationshaus Markdown into a structured dict."""
    data = {
        "title": "",
        "mission_label": "",
        "mission": "",
        "positioning": "",
        "pillars": [],
    }

    i = 0

    # Skip frontmatter
    if i < len(lines) and lines[i].strip() == "---":
        i += 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1

    # Skip blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1

    # H1 title
    if i < len(lines) and lines[i].startswith("# "):
        data["title"] = lines[i][2:].strip()
        i += 1

    while i < len(lines) and not lines[i].strip():
        i += 1

    # Mission callout: > [!MISSION] Label\n> body
    m = re.match(r"^>\s*\[!MISSION\]\s*(.*)", lines[i]) if i < len(lines) else None
    if m:
        data["mission_label"] = m.group(1).strip()
        i += 1
        parts = []
        while i < len(lines) and re.match(r"^>", lines[i]):
            parts.append(re.sub(r"^>\s?", "", lines[i]).strip())
            i += 1
        data["mission"] = " ".join(p for p in parts if p)

    while i < len(lines) and not lines[i].strip():
        i += 1

    # Positioning callout: > [!POSITIONING] Label\n> body
    m = (
        re.match(r"^>\s*\[!POSITIONING\]\s*(.*)", lines[i])
        if i < len(lines)
        else None
    )
    if m:
        i += 1
        parts = []
        while i < len(lines) and re.match(r"^>", lines[i]):
            parts.append(re.sub(r"^>\s?", "", lines[i]).strip())
            i += 1
        data["positioning"] = " ".join(p for p in parts if p)

    # Parse pillars
    pillar = None
    card = None
    in_proofs = False

    while i < len(lines):
        line = lines[i]

        if line.strip() == "---":
            i += 1
            continue

        # H2 = new pillar
        h2 = re.match(r"^## (.+)", line)
        if h2:
            if card and pillar:
                pillar["cards"].append(card)
                card = None
            if pillar:
                data["pillars"].append(pillar)
            pillar = {"name": h2.group(1).strip(), "claim": "", "cards": []}
            in_proofs = False
            i += 1
            continue

        # Blockquote right after H2 (before any H3) = pillar claim
        if pillar and not pillar["claim"] and not pillar["cards"]:
            bq = re.match(r"^>\s?(.*)", line)
            if bq:
                parts = []
                while i < len(lines) and re.match(r"^>", lines[i]):
                    parts.append(re.sub(r"^>\s?", "", lines[i]).strip())
                    i += 1
                pillar["claim"] = " ".join(p for p in parts if p)
                continue

        # H3 = new card
        h3 = re.match(r"^### (.+)", line)
        if h3 and pillar:
            if card:
                pillar["cards"].append(card)
            card = {"title": h3.group(1).strip(), "description": "", "proofs": []}
            in_proofs = False
            i += 1
            continue

        # H4 Proofs
        if re.match(r"^#### Proofs", line) and card:
            in_proofs = True
            i += 1
            continue

        # Ordered list item = proof
        li = re.match(r"^\d+\.\s+(.*)", line)
        if li and card and in_proofs:
            card["proofs"].append(li.group(1).strip())
            i += 1
            continue

        # Non-blank text = card description
        if card and not in_proofs and line.strip():
            if card["description"]:
                card["description"] += " " + line.strip()
            else:
                card["description"] = line.strip()
            i += 1
            continue

        i += 1

    if card and pillar:
        pillar["cards"].append(card)
    if pillar:
        data["pillars"].append(pillar)

    return data


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(data, prefix=""):
    # No indentation — Pandoc treats 4+ leading spaces as code blocks.
    h = []

    # Preserve any leading content (e.g. design <style> from 00-design.sh)
    if prefix:
        h.append(prefix)
        h.append("")

    h.append(f"<style>\n{CSS}\n</style>")
    h.append("")
    h.append('<div class="komhaus">')

    # Mission
    if data["mission"]:
        label = ""
        if data["mission_label"]:
            label = f'<span class="komhaus-label">{esc(data["mission_label"])}</span>'
        h.append(f'<div class="komhaus-mission">{label}{esc(data["mission"])}</div>')

    # Positioning
    if data["positioning"]:
        h.append(f'<div class="komhaus-positioning">{esc(data["positioning"])}</div>')

    # Flat grid: headers in row 1, all cards share rows 2-4 via subgrid
    ncpp = max((len(p["cards"]) for p in data["pillars"]), default=3)
    npillars = len(data["pillars"])
    # Column template: (ncpp × 1fr + spacer) per pillar, no trailing spacer
    col_parts = []
    for pi in range(npillars):
        col_parts.append(f"repeat({ncpp}, 1fr)")
        if pi < npillars - 1:
            col_parts.append("0.75rem")
    col_tpl = " ".join(col_parts)
    h.append(f'<div class="komhaus-body" style="grid-template-columns:{col_tpl}">')

    # Pillar headers (row 1, each spanning ncpp columns)
    pillar_icons = {
        "why": '<svg class="komhaus-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>',
        "what": '<svg class="komhaus-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
        "how": '<svg class="komhaus-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
    }
    for i, pillar in enumerate(data["pillars"]):
        col = i * (ncpp + 1) + 1
        slug = re.sub(r"[^a-z0-9]", "", pillar["name"].lower())
        icon = pillar_icons.get(slug, "")
        claim = ""
        if pillar["claim"]:
            claim = f"<p>{esc(pillar['claim'])}</p>"
        h.append(
            f'<div class="komhaus-pillar-header" style="grid-column:{col}/span {ncpp}">'
            f'<h2>{icon}{esc(pillar["name"])}</h2>{claim}</div>'
        )

    # Cards (rows 2-4, explicitly placed in columns)
    for i, pillar in enumerate(data["pillars"]):
        for j, card in enumerate(pillar["cards"]):
            col = i * (ncpp + 1) + j + 1
            h.append(f'<div class="komhaus-card" style="grid-column:{col}">')
            h.append(f"<h3>{esc(card['title'])}</h3>")
            if card["description"]:
                h.append(f'<p class="komhaus-desc">{esc(card["description"])}</p>')
            else:
                h.append('<p class="komhaus-desc"></p>')
            if card["proofs"]:
                items = "".join(f"<li>{esc(p)}</li>" for p in card["proofs"])
                h.append(f'<div class="komhaus-proofs"><ul>{items}</ul></div>')
            else:
                h.append('<div class="komhaus-proofs"></div>')
            h.append("</div>")

    h.append("</div>")
    h.append("</div>")

    return "\n".join(h)


CSS = """\
/* === Kommunikationshaus === */

/* Override content container for full-width layout */
.content {
  max-width: none;
  padding: 1.5rem;
}

.komhaus {
  max-width: 1600px;
  margin: 0 auto;
  hyphens: auto;
  -webkit-hyphens: auto;
  word-break: break-word;
}

/* --- Banners --- */

.komhaus-mission {
  background: transparent;
  color: #202020;
  text-align: center;
  padding: 0.85rem 2.5rem;
  font-size: 1.15rem;
  border: none;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.komhaus-label {
  display: block;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.15rem;
  opacity: 0.65;
}

.komhaus-positioning {
  background: #202020;
  color: #fff;
  text-align: center;
  padding: 1.25rem 2.5rem;
  font-size: 1.35rem;
  font-weight: 700;
  border-radius: 6px;
  margin-bottom: 2rem;
}

/* --- Body: single flat grid for all headers + cards --- */

.komhaus-body {
  display: grid;
  /* columns set via inline style (dynamic per pillar count) */
  grid-template-rows: auto auto 1fr auto;
  gap: 0.5rem;
}

/* --- Pillar header (row 1) --- */

.komhaus-pillar-header {
  grid-row: 1;
  background: #fff;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  padding: 1rem 1.15rem;
}

.komhaus-pillar-header h2 {
  font-size: 2rem;
  margin: 0 0 0.5rem;
  padding: 0;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.komhaus-icon {
  width: 1.4rem;
  height: 1.4rem;
  flex-shrink: 0;
  color: #888;
}

.komhaus-pillar-header p {
  font-weight: 700;
  font-size: 0.85rem;
  line-height: 1.4;
  margin: 0;
}

/* --- Card (rows 2-4 via subgrid: title | desc | proofs) --- */

.komhaus-card {
  background: #F4F4F4;
  border-radius: 8px;
  padding: 0.9rem;
  display: grid;
  grid-template-rows: subgrid;
  grid-row: 2 / 5;
}

.komhaus-card h3 {
  font-size: 0.8rem;
  font-weight: 700;
  margin: 0;
}

.komhaus-desc {
  font-size: 0.78rem;
  line-height: 1.45;
  margin: 0;
  align-self: start;
}

/* --- Proofs --- */

.komhaus-proofs {
  border-top: 1px solid #DCDCDC;
  padding-top: 0.5rem;
  align-self: start;
}

.komhaus-proofs ul {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.komhaus-proofs li {
  font-size: 0.72rem;
  line-height: 1.4;
  color: #505050;
  margin-bottom: 0.3rem;
}

.komhaus-proofs li:last-child {
  margin-bottom: 0;
}

/* --- Print --- */

@media print {
  .content { padding: 1cm; }
  .komhaus-body { gap: 0.35rem; }
  .komhaus-card { break-inside: avoid; page-break-inside: avoid; }
  .komhaus-pillar-header { break-inside: avoid; }
}
"""


def main():
    content = sys.stdin.read()
    lines = content.split("\n")

    # Detect: needs all five markers
    checks = [
        any(re.match(r"^>\s*\[!MISSION\]", l) for l in lines),
        any(re.match(r"^>\s*\[!POSITIONING\]", l) for l in lines),
        any(re.match(r"^## Why\b", l) for l in lines),
        any(re.match(r"^## What\b", l) for l in lines),
        any(re.match(r"^## How\b", l) for l in lines),
    ]

    if not all(checks):
        print(content, end="")
        return

    # Extract leading <style> blocks (from 00-design.sh) before parsing
    prefix_lines = []
    rest_lines = []
    in_style = False
    past_prefix = False
    for line in lines:
        if not past_prefix:
            if line.strip() == "<style>":
                in_style = True
                prefix_lines.append(line)
                continue
            if in_style:
                prefix_lines.append(line)
                if line.strip() == "</style>":
                    in_style = False
                continue
            if not line.strip() and not rest_lines:
                prefix_lines.append(line)
                continue
            past_prefix = True
        rest_lines.append(line)

    prefix = "\n".join(prefix_lines).rstrip()
    data = parse(rest_lines)
    print(render(data, prefix), end="")


if __name__ == "__main__":
    main()
