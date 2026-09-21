#!/usr/bin/env bash
# Build the manual and whitepaper PDFs from their Markdown sources: Markdown → HTML (python
# markdown) → PDF (LibreOffice, headless). Output goes to docs/pdf/ and, with --install, to
# ~/Documents (the previous PDFs are kept with a .pre-<version> suffix).
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
OUT="$HERE/pdf"; mkdir -p "$OUT"
VERSION=$(python3 -c 'import sys; sys.path.insert(0, "'"$HERE"'/../runtime"); import worldline; print(worldline.__version__)')
build() {
  local source="$1" title="$2" base="$3"
  python3 - "$source" "$OUT/$base.html" "$title" <<'PY'
import re, sys
import markdown
source, target, title = sys.argv[1:4]
text = open(source, encoding="utf-8").read()
front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
subtitle = ""
if front:
    for line in front.group(1).splitlines():
        if line.startswith("subtitle:"):
            subtitle = line.split(":", 1)[1].strip()
    text = text[front.end():]
body = markdown.markdown(text, extensions=["tables", "fenced_code", "toc"], extension_configs={"toc": {"title": "Contents"}})
css = """
body { font-family: 'Liberation Serif', 'DejaVu Serif', serif; font-size: 11pt; line-height: 1.35; max-width: 17cm; margin: 2cm auto; color: #111; }
h1 { font-size: 20pt; margin-top: 1.4em; border-bottom: 1px solid #999; padding-bottom: 0.15em; }
h2 { font-size: 14pt; margin-top: 1.1em; }
h3 { font-size: 12pt; }
code, pre { font-family: 'Liberation Mono', 'DejaVu Sans Mono', monospace; font-size: 9.5pt; }
pre { background: #f3f3f3; padding: 0.6em; border: 1px solid #ccc; white-space: pre-wrap; }
table { border-collapse: collapse; width: 100%; margin: 0.6em 0; font-size: 10pt; }
th, td { border: 1px solid #bbb; padding: 0.25em 0.45em; vertical-align: top; }
th { background: #e9e9e9; text-align: left; }
.title { font-size: 26pt; font-weight: bold; letter-spacing: 0.08em; margin-bottom: 0; }
.subtitle { color: #444; margin-top: 0.2em; margin-bottom: 2em; }
"""
html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title><style>{css}</style></head><body><p class='title'>WORLDLINE</p><p class='subtitle'>{title}<br>{subtitle}</p>{body}</body></html>"
open(target, "w", encoding="utf-8").write(html)
PY
  (cd "$OUT" && soffice --headless --convert-to pdf:writer_web_pdf_Export "$base.html" >/dev/null 2>&1) || (cd "$OUT" && soffice --headless --convert-to pdf "$base.html" >/dev/null 2>&1)
  [[ -f "$OUT/$base.pdf" ]] || { echo "build-pdf: $base.pdf was not produced" >&2; exit 1; }
  echo "built $OUT/$base.pdf ($(pdfinfo "$OUT/$base.pdf" 2>/dev/null | awk '/^Pages/{print $2}') pages)"
}
build "$HERE/user-manual.md" "User and Operations Manual" "WORLDLINE-User-Manual"
build "$HERE/whitepaper.md" "Technical Whitepaper" "WORLDLINE-Whitepaper"
if [[ ${1:-} == --install ]]; then
  for base in WORLDLINE-User-Manual WORLDLINE-Whitepaper; do
    if [[ -f "$HOME/Documents/$base.pdf" ]]; then mv -n "$HOME/Documents/$base.pdf" "$HOME/Documents/$base.pre-$VERSION.pdf"; fi
    install -m 0644 "$OUT/$base.pdf" "$HOME/Documents/$base.pdf"
    echo "installed ~/Documents/$base.pdf"
  done
fi
