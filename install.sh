#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"
# shellcheck disable=SC1090
source "${GNAT_ENV:-$HOME/opt/gnat/env.sh}"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/runtime"

echo "== WORLDLINE build =="
gprbuild -q -P worldline.gpr

echo "== WORLDLINE Ada behavior =="
./bin/worldline_core_tests
./bin/worldline_core_fuzz

echo "== WORLDLINE runtime behavior =="
python3 -m unittest discover -s tests -p 'test_*.py'

echo "== WORLDLINE proof gate =="
./prove.sh
python3 verify_proof_manifest.py

LIB_HOME="$HOME/.local/lib"
DEST="$LIB_HOME/worldline"
STAGE="$LIB_HOME/.worldline-install-$$"
PLUGIN="$HOME/.config/omarchy/plugins/khephri.worldline"
SERVICE="$HOME/.config/systemd/user/worldlined.service"
SHELL_CONFIG="$HOME/.config/omarchy/shell.json"
BINDINGS="$HOME/.config/hypr/bindings.lua"
BACKUP="$HOME/.local/state/worldline/install-backups/$(date -u +%Y%m%dT%H%M%SZ)-$$"

install -d -m 0700 "$LIB_HOME" "$STAGE" "$STAGE/runtime" "$BACKUP"
install -m 0600 "$SHELL_CONFIG" "$BACKUP/shell.json"
install -m 0600 "$BINDINGS" "$BACKUP/bindings.lua"

cp -a runtime/worldline "$STAGE/runtime/worldline"
install -m 0755 lib/libworldline_core.so "$STAGE/libworldline_core.so"
install -m 0600 proof-manifest.json "$STAGE/proof-manifest.json"
install -m 0644 core/worldline_core.h "$STAGE/worldline_core.h"

if [[ -e "$DEST" ]]; then
  OLD="$LIB_HOME/.worldline-old-$$"
  mv "$DEST" "$OLD"
  mv "$STAGE" "$DEST"
  rm -rf "$OLD"
else
  mv "$STAGE" "$DEST"
fi

install -d -m 0700 "$HOME/.local/bin"
install -m 0755 cli/worldline "$HOME/.local/bin/worldline"
install -m 0755 daemon/worldlined "$HOME/.local/bin/worldlined"

PLUGIN_STAGE="$HOME/.config/omarchy/plugins/.khephri.worldline-$$"
rm -rf "$PLUGIN_STAGE"
cp -a omarchy "$PLUGIN_STAGE"
if [[ -e "$PLUGIN" ]]; then
  PLUGIN_OLD="$HOME/.config/omarchy/plugins/.khephri.worldline-old-$$"
  mv "$PLUGIN" "$PLUGIN_OLD"
  mv "$PLUGIN_STAGE" "$PLUGIN"
  rm -rf "$PLUGIN_OLD"
else
  mv "$PLUGIN_STAGE" "$PLUGIN"
fi

install -d -m 0700 "$HOME/.config/systemd/user"
install -m 0644 daemon/worldlined.service "$SERVICE"

python3 - <<'PY'
from pathlib import Path
from worldline.install_config import patch_bindings, patch_shell
patch_shell(Path.home() / ".config/omarchy/shell.json")
patch_bindings(Path.home() / ".config/hypr/bindings.lua")
PY

systemctl --user daemon-reload
systemctl --user enable worldlined.service
systemctl --user restart worldlined.service
omarchy-shell shell rescanPlugins
hyprctl reload
CONFIG_ERRORS=$(hyprctl configerrors)
if [[ -n "$CONFIG_ERRORS" ]]; then
  printf '%s\n' "$CONFIG_ERRORS" >&2
  exit 1
fi

echo "WORLDLINE installed. No managed root was initialized and no AI agent was launched."
echo "Configuration backup: $BACKUP"
