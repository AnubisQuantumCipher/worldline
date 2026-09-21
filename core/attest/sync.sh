#!/usr/bin/env bash
# Re-vendor the ATTEST SHA-256 units from ~/Projects/attest and record the upstream commit.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SRC="${ATTEST_SRC:-$HOME/Projects/attest}"
for f in attest.ads attest-sha256.ads attest-sha256.adb; do install -m 0644 "$SRC/src/$f" "$HERE/$f"; done
UP=$(git -C "$SRC" rev-parse HEAD 2>/dev/null || echo unknown)
sed -i -E "s/commit \`[0-9a-f]+\`|commit \`unknown\`/commit \`$UP\`/" "$HERE/README.md"
echo "vendored from $SRC @ $UP"
