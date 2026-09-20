#!/usr/bin/env bash
# Build, verify, and install the WORLDLINE engine (runtime, proved library, launchers, unit),
# then bring the desktop plugin to the matching release through its own git checkout.
#
# Source of truth:
#   engine   this repository (~/Projects/worldline)
#   plugin   the sibling repository ~/Projects/worldline-omarchy, deployed as a git checkout at
#            ~/.config/omarchy/plugins/khephri.worldline whose `origin` remote is that repo.
#            The plugin is never copied file-by-file: it is fast-forwarded, so the deployed
#            tree always equals a commit of the plugin repository.
#
# Rollback: every install writes a backup directory (printed at the end) holding the previous
# ~/.local/lib/worldline, both launchers, the unit, shell.json, and bindings.lua, plus the
# plugin checkout's previous commit id. See README "Rollback".
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"
# shellcheck disable=SC1090
source "${GNAT_ENV:-$HOME/opt/gnat/env.sh}"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/runtime"

PLUGIN_SRC="${WORLDLINE_PLUGIN_SRC:-$ROOT/../worldline-omarchy}"
PLUGIN_REF="${WORLDLINE_PLUGIN_REF:-main}"
SKIP_PROOF="${WORLDLINE_SKIP_PROOF:-0}"

echo "== WORLDLINE build =="
gprbuild -q -P worldline.gpr

echo "== WORLDLINE Ada behavior =="
./bin/worldline_core_tests
./bin/worldline_core_fuzz

echo "== WORLDLINE runtime behavior =="
python3 -m unittest discover -s tests -p 'test_*.py'

if [[ "$SKIP_PROOF" == "1" ]]; then
  echo "== WORLDLINE proof gate: SKIPPED (WORLDLINE_SKIP_PROOF=1) — manifest must still verify =="
else
  echo "== WORLDLINE proof gate =="
  ./prove.sh
fi
python3 verify_proof_manifest.py

LIB_HOME="$HOME/.local/lib"
DEST="$LIB_HOME/worldline"
STAGE="$LIB_HOME/.worldline-install-$$"
PLUGIN="$HOME/.config/omarchy/plugins/khephri.worldline"
SERVICE="$HOME/.config/systemd/user/worldlined.service"
SHELL_CONFIG="$HOME/.config/omarchy/shell.json"
BINDINGS="$HOME/.config/hypr/bindings.lua"
BACKUP="$HOME/.local/state/worldline/install-backups/$(date -u +%Y%m%dT%H%M%SZ)-$$"

echo "== active work check =="
if command -v worldline >/dev/null 2>&1 && systemctl --user is-active --quiet worldlined.service; then
  RUNNING=$(worldline status --json 2>/dev/null | python3 -c 'import json,sys
try:
    s=json.load(sys.stdin)
    print(sum(1 for j in s.get("jobs",[]) if j.get("state") in ("STARTING","RUNNING","FINALIZING")))
except Exception:
    print(0)' 2>/dev/null || echo 0)
  if [[ "${RUNNING:-0}" != "0" && "${WORLDLINE_FORCE:-0}" != "1" ]]; then
    echo "install: $RUNNING agent job(s) are running; restarting the daemon would orphan them." >&2
    echo "install: wait, or cancel them (worldline cancel WORLD), or set WORLDLINE_FORCE=1." >&2
    exit 2
  fi
fi

install -d -m 0700 "$LIB_HOME" "$STAGE" "$STAGE/runtime" "$BACKUP"
[[ -f "$SHELL_CONFIG" ]] && install -m 0600 "$SHELL_CONFIG" "$BACKUP/shell.json"
[[ -f "$BINDINGS" ]] && install -m 0600 "$BINDINGS" "$BACKUP/bindings.lua"
if [[ -d "$DEST" ]]; then cp -a "$DEST" "$BACKUP/lib-worldline"; fi
for launcher in worldline worldlined; do
  [[ -f "$HOME/.local/bin/$launcher" ]] && install -m 0755 "$HOME/.local/bin/$launcher" "$BACKUP/$launcher"
done
[[ -f "$SERVICE" ]] && install -m 0644 "$SERVICE" "$BACKUP/worldlined.service"
if [[ -d "$PLUGIN/.git" ]]; then
  git -C "$PLUGIN" rev-parse HEAD > "$BACKUP/plugin-commit"
fi

cp -a runtime/worldline "$STAGE/runtime/worldline"
find "$STAGE/runtime" -name __pycache__ -type d -prune -exec rm -rf {} +
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

echo "== desktop plugin =="
if [[ -d "$PLUGIN/.git" ]]; then
  if ! git -C "$PLUGIN" remote get-url origin >/dev/null 2>&1; then
    git -C "$PLUGIN" remote add origin "$PLUGIN_SRC"
  fi
  git -C "$PLUGIN" fetch --quiet origin "$PLUGIN_REF"
  if ! git -C "$PLUGIN" merge --ff-only FETCH_HEAD >/dev/null 2>&1; then
    echo "install: plugin checkout $PLUGIN has diverged from $PLUGIN_SRC ($PLUGIN_REF); refusing to overwrite local edits." >&2
    echo "install: inspect with: git -C $PLUGIN status; then git -C $PLUGIN reset --hard FETCH_HEAD if they are disposable." >&2
    exit 3
  fi
elif [[ -e "$PLUGIN" ]]; then
  echo "install: $PLUGIN exists but is not a git checkout; move it aside so the plugin can be cloned from $PLUGIN_SRC." >&2
  exit 3
else
  install -d -m 0755 "$HOME/.config/omarchy/plugins"
  git clone --quiet --branch "$PLUGIN_REF" "$PLUGIN_SRC" "$PLUGIN"
fi
if command -v omarchy-plugin-validate >/dev/null 2>&1; then
  omarchy-plugin-validate "$PLUGIN"
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
for _ in $(seq 1 50); do
  systemctl --user is-active --quiet worldlined.service && [[ -S "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/worldline/worldlined.sock" ]] && break
  sleep 0.1
done
"$HOME/.local/bin/worldline" status --json > /dev/null

hyprctl reload
CONFIG_ERRORS=$(hyprctl configerrors)
if [[ -n "$CONFIG_ERRORS" ]]; then
  printf '%s\n' "$CONFIG_ERRORS" >&2
  exit 1
fi
if [[ "${WORLDLINE_NO_SHELL_RESTART:-0}" != "1" ]]; then
  # The plugin's service and overlay are keepLoaded; the shell only swaps them on a restart.
  omarchy-shell -q shell rescanPlugins || true
  omarchy-restart-shell >/dev/null 2>&1 || true
fi

echo "WORLDLINE installed: runtime $(python3 -c 'import worldline; print(worldline.__version__)') · plugin $(git -C "$PLUGIN" rev-parse --short HEAD) · library $(sha256sum "$DEST/libworldline_core.so" | cut -c1-12)"
echo "No managed root was initialized and no AI agent was launched."
echo "Backup for rollback: $BACKUP"
