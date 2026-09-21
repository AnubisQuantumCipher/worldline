#!/usr/bin/env bash
# Build the manual and whitepaper PDFs from their Markdown sources with LibreOffice's Markdown
# import (Writer, 25.8+). Output goes to docs/pdf/ and, with --install, to ~/Documents (the
# previous PDFs are kept with a .pre-<version> suffix).
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
OUT="$HERE/pdf"; mkdir -p "$OUT"
VERSION=$(python3 -c 'import sys; sys.path.insert(0, "'"$HERE"'/../runtime"); import worldline; print(worldline.__version__)')
build() {
  local source="$1" title="$2" base="$3"
  python3 - "$source" "$OUT/$base.md" "$title" <<'PY'
import re, sys
source, target, title = sys.argv[1:4]
text = open(source, encoding="utf-8").read()
front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
subtitle = ""
if front:
    for line in front.group(1).splitlines():
        if line.startswith("subtitle:"):
            subtitle = line.split(":", 1)[1].strip()
    text = text[front.end():]
open(target, "w", encoding="utf-8").write(f"# WORLDLINE\n\n**{title}**\n\n{subtitle}\n\n" + text)
PY
  (cd "$OUT" && soffice --headless --convert-to pdf "$base.md" >/dev/null 2>&1)
  [[ -f "$OUT/$base.pdf" ]] || { echo "build-pdf: $base.pdf was not produced" >&2; exit 1; }
  echo "built $OUT/$base.pdf ($(pdfinfo "$OUT/$base.pdf" 2>/dev/null | awk '/^Pages/{print $2}') pages)"
}
build "$HERE/user-manual.md" "User and Operations Manual" "WORLDLINE-User-Manual"
build "$HERE/whitepaper.md" "Technical Whitepaper" "WORLDLINE-Whitepaper"
if [[ ${1:-} == --install ]]; then
  for base in WORLDLINE-User-Manual WORLDLINE-Whitepaper; do
    if [[ -f "$HOME/Documents/$base.pdf" && ! -f "$HOME/Documents/$base.pre-$VERSION.pdf" ]]; then mv "$HOME/Documents/$base.pdf" "$HOME/Documents/$base.pre-$VERSION.pdf"; fi
    install -m 0644 "$OUT/$base.pdf" "$HOME/Documents/$base.pdf"
    echo "installed ~/Documents/$base.pdf"
  done
fi
