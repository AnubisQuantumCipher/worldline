#!/usr/bin/env bash
# Build, verify, and install the WORLDLINE engine (runtime, proved library, launchers, unit),
# then bring the desktop plugin to a PINNED commit of its own repository.
#
# Source of truth:
#   engine   this repository (~/Projects/worldline)
#   plugin   the sibling repository ~/Projects/worldline-omarchy, deployed as a git checkout at
#            ~/.config/omarchy/plugins/khephri.worldline whose `origin` remote is that repo.
#            The plugin is never copied file-by-file: it is fast-forwarded, so the deployed
#            tree always equals a commit of the plugin repository.
#
# Order matters and is deliberate (1.3.1):
#   refuse after a partial install  ->  resolve both identities  ->  build, test and prove  ->
#   fail-closed preflight  ->  STOP the daemon  ->  back up (consistent, because nothing is
#   writing)  ->  install  ->  start  ->  verify that what is running is what was built  ->
#   write a receipt.
#
# The daemon is stopped BEFORE the backup and the swap. That is what closes the window in which
# a fork, race or ghost could start work against a half-replaced runtime, and it is what makes
# the store backup consistent rather than a copy of a live SQLite file.
#
# Rollback: every install writes a backup directory (printed at the end and named in the
# receipt) holding the previous ~/.local/lib/worldline, both launchers, the unit, shell.json,
# bindings.lua, the plugin checkout's previous commit id, and the whole state directory
# (store, receipts, transactions, events) minus the backup area itself. Restore it with
# scripts/rollback.sh. Payload data under ~/.local/share/worldline is NOT copied unless
# WORLDLINE_BACKUP_PAYLOADS=1; its size and contents are recorded either way. After a verified
# install the newest WORLDLINE_BACKUP_KEEP backups (default 5) are kept and older ones removed,
# with each removal printed; WORLDLINE_BACKUP_KEEP=0 keeps every backup forever.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"
# shellcheck disable=SC1090
# The reference machine keeps GNAT FSF under ~/opt/gnat; elsewhere (CI, packaging) the
# toolchain is already on PATH.
if [[ -f "${GNAT_ENV:-$HOME/opt/gnat/env.sh}" ]]; then source "${GNAT_ENV:-$HOME/opt/gnat/env.sh}"; fi

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/runtime"
# The behaviour gates, the proof gate and the installed daemon must all exercise the library
# this build produced. A WORLDLINE_CORE_LIB inherited from the caller would silently point them
# at a different one, so it is dropped here rather than trusted.
unset WORLDLINE_CORE_LIB

PLUGIN_SRC="${WORLDLINE_PLUGIN_SRC:-$ROOT/../worldline-omarchy}"
PLUGIN_REF="${WORLDLINE_PLUGIN_REF:-}"
SKIP_PROOF="${WORLDLINE_SKIP_PROOF:-0}"
BACKUP_PAYLOADS="${WORLDLINE_BACKUP_PAYLOADS:-0}"

LIB_HOME="$HOME/.local/lib"
DEST="$LIB_HOME/worldline"
PLUGIN="$HOME/.config/omarchy/plugins/khephri.worldline"
SERVICE="$HOME/.config/systemd/user/worldlined.service"
SHELL_CONFIG="$HOME/.config/omarchy/shell.json"
BINDINGS="$HOME/.config/hypr/bindings.lua"
STATE="$HOME/.local/state/worldline"
SHARE="$HOME/.local/share/worldline"
BACKUP="$STATE/install-backups/$(date -u +%Y%m%dT%H%M%SZ)-$$"
RECEIPT="$BACKUP/install-receipt.json"
SOCKET="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/worldline/worldlined.sock"

DAEMON_STOPPED=0
PREVIOUS_PID=""
RUNTIME_REPLACED=0
INSTALL_DONE=0
on_exit() {
  local code=$?
  [[ "$INSTALL_DONE" == "1" || "$code" == "0" ]] && return
  echo "install: ABORTED (exit $code)." >&2
  [[ -n "${STAGE:-}" && -d "${STAGE:-}" ]] && rm -rf "$STAGE"
  if [[ "$DAEMON_STOPPED" == "1" ]]; then
    echo "install: the worldlined daemon is STOPPED and was not restarted." >&2
    if [[ "$RUNTIME_REPLACED" == "1" ]]; then
      echo "install: the runtime HAS been replaced. Roll back with:" >&2
      echo "install:   $ROOT/scripts/rollback.sh $BACKUP" >&2
    else
      echo "install: nothing was replaced. Bring the daemon back with:" >&2
      echo "install:   systemctl --user start worldlined.service" >&2
    fi
  fi
  [[ -f "${PARTIAL_MARKER:-/nonexistent}" ]] && echo "install: a partial-install marker remains at $PARTIAL_MARKER" >&2
  return 0
}
trap on_exit EXIT

fail() { echo "install: $*" >&2; exit 2; }

# A path that is a symlink is never written through: replacing it would silently convert a
# deliberate link into a regular file, and copying it into the backup would dereference it, so
# the link could not be restored. Both are refusals, not fixups.
refuse_symlink() {
  if [[ -L "$1" ]]; then
    fail "$2 is a symlink ($1 -> $(readlink "$1")). Installing would replace the link with a regular file and the backup could not restore it. Resolve it deliberately, then re-run."
  fi
}

PARTIAL_MARKER="$STATE/install-incomplete"
if [[ -f "$PARTIAL_MARKER" ]]; then
  echo "install: a previous install did not finish. It recorded:" >&2
  sed 's/^/install:   /' "$PARTIAL_MARKER" >&2
  echo "install: the installation on disk may be half-replaced, so a backup taken now would" >&2
  echo "install: capture that broken state as if it were the good one. Roll back with the backup" >&2
  echo "install: named above first, or set WORLDLINE_FORCE_AFTER_PARTIAL=1 to proceed anyway." >&2
  [[ "${WORLDLINE_FORCE_AFTER_PARTIAL:-0}" == "1" ]] || exit 2
fi

# ---- identities, resolved and pinned BEFORE anything is built or replaced --------------------
# The engine archive alone does not name the plugin. Resolving the plugin commit first means an
# unreachable or unpinned plugin aborts in a second, with the existing installation whole and
# before a multi-minute build — rather than after the runtime has already been swapped.
echo "== identities =="
# `git -C DIR rev-parse HEAD` walks UP out of DIR. Unpack a release archive inside any other
# repository and that repository's HEAD would be recorded as the engine commit — a false identity
# in the receipt, which is worse than no identity. The engine commit is therefore accepted only
# from a checkout whose own top level IS this directory.
ENGINE_TOPLEVEL=$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || true)
ROOT_REAL=$(cd "$ROOT" && pwd -P)
if [[ -n "$ENGINE_TOPLEVEL" && "$(cd "$ENGINE_TOPLEVEL" 2>/dev/null && pwd -P)" == "$ROOT_REAL" ]]; then
  ENGINE_COMMIT=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo "unknown")
  ENGINE_DIRTY=$(git -C "$ROOT" status --porcelain --untracked-files=no 2>/dev/null || true)
else
  ENGINE_COMMIT="unknown"
  ENGINE_DIRTY=""
  echo "install: WARNING — $ROOT is not a git checkout of its own, so this engine corresponds to no"
  echo "install: commit this installer can name. The receipt will record engineCommit 'unknown'."
  [[ -n "$ENGINE_TOPLEVEL" ]] && echo "install: (it sits inside $ENGINE_TOPLEVEL, whose HEAD is deliberately NOT claimed as the engine.)"
fi
if [[ -n "$ENGINE_DIRTY" && "${WORLDLINE_ALLOW_DIRTY:-0}" != "1" ]]; then
  echo "install: the engine worktree has uncommitted changes, so the installed engine would not" >&2
  echo "install: correspond to any commit. Commit them, or set WORLDLINE_ALLOW_DIRTY=1." >&2
  printf '%s\n' "$ENGINE_DIRTY" >&2
  exit 2
fi

if [[ -z "$PLUGIN_REF" ]]; then
  if [[ "${WORLDLINE_PLUGIN_ALLOW_MOVING_REF:-0}" == "1" ]]; then
    PLUGIN_REF=main
    echo "install: WARNING — pinning the plugin to the moving ref 'main' by explicit request."
  else
    echo "install: WORLDLINE_PLUGIN_REF is not set. An engine release does not identify the plugin," >&2
    echo "install: so this installer will not pick one for you. Set it to an exact commit:" >&2
    echo "install:   WORLDLINE_PLUGIN_REF=\$(git -C $PLUGIN_SRC rev-parse main) ./install.sh" >&2
    echo "install: or set WORLDLINE_PLUGIN_ALLOW_MOVING_REF=1 to accept whatever 'main' is now." >&2
    exit 2
  fi
fi
if [[ -d "$PLUGIN_SRC/.git" ]]; then
  git -C "$PLUGIN_SRC" rev-parse --verify --quiet "${PLUGIN_REF}^{commit}" >/dev/null \
    || fail "plugin ref '$PLUGIN_REF' does not resolve to a commit in $PLUGIN_SRC"
  PLUGIN_TARGET=$(git -C "$PLUGIN_SRC" rev-parse "${PLUGIN_REF}^{commit}")
else
  fail "$PLUGIN_SRC is not a git repository; cannot pin a plugin commit"
fi
echo "install: engine $ENGINE_COMMIT"
echo "install: plugin $PLUGIN_TARGET ($PLUGIN_REF)"

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

# ---- fail-closed preflight, taken immediately before the daemon is stopped -------------------
# Deliberately after the build: the answer must describe the machine at the moment work stops,
# not the machine as it was minutes earlier. An unreadable daemon is not permission. scripts/preflight.py treats every unanswered question
# as a refusal; see tests/test_preflight.py for the controls.
echo "== preflight =="
PREFLIGHT_ARGS=()
[[ "${WORLDLINE_ALLOW_GHOSTS:-0}" == "1" ]] && PREFLIGHT_ARGS+=(--allow-ghosts)
[[ "$BACKUP_PAYLOADS" == "1" ]] && PREFLIGHT_ARGS+=(--with-payloads)
[[ "${WORLDLINE_DAEMON_DOWN_UNCHECKED:-0}" == "1" ]] && PREFLIGHT_ARGS+=(--daemon-down-unchecked)
if ! python3 "$ROOT/scripts/preflight.py" "${PREFLIGHT_ARGS[@]}"; then
  echo "install: preflight refused the upgrade; nothing was changed." >&2
  echo "install: resolve the named gates, or inspect with: python3 scripts/preflight.py --json" >&2
  exit 2
fi

# ---- stop the daemon, then confirm nothing is left running ------------------------------------
# Everything below this line happens with no daemon writing to the store and no new world able
# to start. If the script aborts from here on, the daemon stays stopped: that is fail-safe, and
# the operator is told so.
UNIT_ENABLED=$(systemctl --user is-enabled worldlined.service 2>/dev/null || true)
UNIT_ACTIVE=$(systemctl --user show -p ActiveState --value worldlined.service 2>/dev/null || echo unreachable)
[[ -n "$UNIT_ACTIVE" ]] || UNIT_ACTIVE=unreachable
if [[ "$UNIT_ENABLED" == "masked" || -L "$SERVICE" ]]; then
  fail "worldlined.service is masked or its unit path is a symlink; that is deliberate configuration this installer will not silently destroy"
fi
# `is-active --quiet` exits non-zero for failed, activating AND deactivating alike, so using it
# here would skip the stop for a unit that is on its way up (and will finish coming up during
# the backup) or on its way down (and may still be writing). The state is read instead, and
# anything other than a settled `inactive` gets a real stop — which also cancels a pending
# auto-restart, since the unit is Restart=on-failure.
if [[ "$UNIT_ACTIVE" == "unreachable" ]]; then
  fail "the user manager could not report ActiveState for worldlined.service; refusing to guess whether it is running"
fi
if [[ "$UNIT_ACTIVE" != "inactive" ]]; then
  echo "== stopping the daemon (ActiveState=$UNIT_ACTIVE) for the duration of the upgrade =="
  PREVIOUS_PID=$(systemctl --user show -p MainPID --value worldlined.service 2>/dev/null || echo "")
  DAEMON_STOPPED=1
  systemctl --user stop worldlined.service
  for _ in $(seq 1 100); do
    systemctl --user is-active --quiet worldlined.service || break
    sleep 0.1
  done
  systemctl --user is-active --quiet worldlined.service && fail "the daemon did not stop; refusing to replace a running runtime"
  for _ in $(seq 1 50); do [[ -S "$SOCKET" ]] || break; sleep 0.1; done
else
  echo "== the daemon is already inactive =="
fi
LEFTOVER=$(systemctl --user list-units 'worldline-*' --all --plain --no-legend 2>/dev/null | awk '{print $1}' | grep -v '^worldlined.service$' || true)
if [[ -n "$LEFTOVER" ]]; then
  echo "install: transient world units are still present after stopping the daemon:" >&2
  printf '%s\n' "$LEFTOVER" >&2
  echo "install: the daemon has been stopped. Start it again with:" >&2
  echo "install:   systemctl --user start worldlined.service" >&2
  exit 2
fi

# ---- backup, taken while nothing is writing ---------------------------------------------------
echo "== backup =="
install -d -m 0700 "$LIB_HOME" "$BACKUP" "$BACKUP/state"
STAGE=$(mktemp -d "$LIB_HOME/.worldline-install-XXXXXXXX")
chmod 0700 "$STAGE"
install -d -m 0700 "$STAGE/runtime"
for target in "$DEST" "$HOME/.local/bin/worldline" "$HOME/.local/bin/worldlined" "$SERVICE" "$SHELL_CONFIG" "$BINDINGS"; do
  refuse_symlink "$target" "the install target $(basename "$target")"
done
printf '%s\n' "started $(date -u +%Y-%m-%dT%H:%M:%SZ) backup=$BACKUP engine=$ENGINE_COMMIT plugin=$PLUGIN_TARGET" > "$PARTIAL_MARKER"
printf '{"unitEnabled":"%s","unitActive":"%s"}\n' "${UNIT_ENABLED:-unknown}" "${UNIT_ACTIVE:-unknown}" > "$BACKUP/unit-state.json"
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
# The store, receipts, transactions and events — everything the daemon owns except the backup
# area itself, which lives inside the directory being copied and would otherwise recurse.
if [[ -d "$STATE" ]]; then
  tar -C "$HOME/.local/state" -cf - --exclude='worldline/install-backups' \
      --exclude='worldline/install-incomplete' worldline \
    | tar -C "$BACKUP/state" -xf -
fi
# Written last on purpose: rollback.sh refuses a backup with no manifest, which is how an
# interrupted backup is told apart from a complete one.
python3 "$ROOT/scripts/backup_manifest.py" "$BACKUP" "$DEST" \
  "$HOME/.local/bin/worldline" "$HOME/.local/bin/worldlined" "$SERVICE" "$SHELL_CONFIG" "$BINDINGS" \
  || fail "the backup does not hold everything that exists on this machine; refusing to install over it"

# Payload data is large and unchanged by an engine upgrade, so it is recorded rather than copied
# unless asked for. What is NOT copied is written down, so "restorable" is never assumed.
if [[ -d "$SHARE" ]]; then
  du -sb "$SHARE"/* 2>/dev/null > "$BACKUP/payload-inventory.txt" || true
  if [[ "$BACKUP_PAYLOADS" == "1" ]]; then
    install -d -m 0700 "$BACKUP/share"
    tar -C "$HOME/.local/share" -cf - worldline | tar -C "$BACKUP/share" -xf -
  fi
fi

# ---- install ------------------------------------------------------------------------------------
echo "== install =="
cp -a runtime/worldline "$STAGE/runtime/worldline"
find "$STAGE/runtime" -name __pycache__ -type d -prune -exec rm -rf {} +
install -m 0755 lib/libworldline_core.so "$STAGE/libworldline_core.so"
install -m 0600 proof-manifest.json "$STAGE/proof-manifest.json"
install -m 0644 core/worldline_core.h "$STAGE/worldline_core.h"

RUNTIME_REPLACED=1
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
  git -C "$PLUGIN" fetch --quiet origin "$PLUGIN_TARGET" || git -C "$PLUGIN" fetch --quiet origin \
    || fail "could not fetch $PLUGIN_TARGET from $PLUGIN_SRC; the engine runtime HAS been replaced and the daemon is stopped — roll back with: $ROOT/scripts/rollback.sh $BACKUP"
  if ! git -C "$PLUGIN" merge --ff-only "$PLUGIN_TARGET" >/dev/null 2>&1; then
    echo "install: plugin checkout $PLUGIN cannot fast-forward to $PLUGIN_TARGET;" >&2
    echo "install: refusing to overwrite local edits. The engine runtime HAS been replaced." >&2
    echo "install: inspect with: git -C $PLUGIN status" >&2
    echo "install: then either resolve it and re-run, or roll back with:" >&2
    echo "install:   scripts/rollback.sh $BACKUP" >&2
    exit 3
  fi
elif [[ -e "$PLUGIN" ]]; then
  fail "$PLUGIN exists but is not a git checkout; move it aside so the plugin can be cloned from $PLUGIN_SRC"
else
  install -d -m 0755 "$HOME/.config/omarchy/plugins"
  git clone --quiet "$PLUGIN_SRC" "$PLUGIN"
  git -C "$PLUGIN" checkout --quiet --detach "$PLUGIN_TARGET"
fi
if command -v omarchy-plugin-validate >/dev/null 2>&1; then
  omarchy-plugin-validate "$PLUGIN"
else
  echo "install: omarchy-plugin-validate is not installed; the plugin was not validated."
fi

install -d -m 0700 "$HOME/.config/systemd/user"
install -m 0644 daemon/worldlined.service "$SERVICE"

python3 - <<'PY'
from pathlib import Path
from worldline.install_config import patch_bindings, patch_shell
patch_shell(Path.home() / ".config/omarchy/shell.json")
patch_bindings(Path.home() / ".config/hypr/bindings.lua")
PY

# ---- start, then prove that what is running is what was built ----------------------------------
echo "== start and verify =="
systemctl --user daemon-reload
# Enablement is restored, not imposed: a daemon the operator had disabled stays disabled.
if [[ "$UNIT_ENABLED" == "enabled" || -z "$UNIT_ENABLED" ]]; then
  systemctl --user enable worldlined.service
else
  echo "install: worldlined.service was '$UNIT_ENABLED' before this install; leaving it that way."
fi
systemctl --user restart worldlined.service
for _ in $(seq 1 100); do
  systemctl --user is-active --quiet worldlined.service && [[ -S "$SOCKET" ]] && break
  sleep 0.1
done
systemctl --user is-active --quiet worldlined.service || fail "the daemon did not start; roll back with: scripts/rollback.sh $BACKUP"

MAIN_PID=$(systemctl --user show -p MainPID --value worldlined.service 2>/dev/null || echo "")
if ! python3 "$ROOT/scripts/verify_install.py" \
      --engine-commit "$ENGINE_COMMIT" --plugin-commit "$PLUGIN_TARGET" \
      --previous-pid "${PREVIOUS_PID:-}" --main-pid "${MAIN_PID:-}" \
      --proof-gate "$([[ "$SKIP_PROOF" == "1" ]] && echo skipped || echo ran)" \
      --source "$ROOT" --receipt "$RECEIPT"; then
  echo "install: the running installation does not match what was just built." >&2
  echo "install: roll back with: scripts/rollback.sh $BACKUP" >&2
  exit 2
fi

hyprctl reload || true
CONFIG_ERRORS=$(hyprctl configerrors || true)
if [[ -n "$CONFIG_ERRORS" && "$CONFIG_ERRORS" != "no errors" ]]; then
  echo "install: the engine is installed and verified, but Hyprland reports config errors:" >&2
  printf '%s\n' "$CONFIG_ERRORS" >&2
fi
SHELL_RESTART="not attempted"
if [[ "${WORLDLINE_NO_SHELL_RESTART:-0}" != "1" ]]; then
  # The plugin's service and overlay are keepLoaded; the shell only swaps them on a restart.
  # omarchy-restart-shell KILLS the running shell before relaunching it, and can exit non-zero
  # with the shell down or the session lock not re-secured. Printing a successful install over
  # that would be a lie about the state of the desktop, so its outcome is kept and shown.
  omarchy-shell -q shell rescanPlugins || echo "install: rescanPlugins failed; the shell may not see the new plugin commit." >&2
  if omarchy-restart-shell; then
    SHELL_RESTART="ok"
  else
    SHELL_RESTART="FAILED"
    echo "install: the desktop shell restart FAILED. The engine is installed and verified, but the" >&2
    echo "install: shell was killed as part of the restart and may not have come back: expect no bar," >&2
    echo "install: no plugin surfaces, or an unsecured session lock. Re-run omarchy-restart-shell," >&2
    echo "install: or roll back with: scripts/rollback.sh $BACKUP" >&2
  fi
fi

INSTALL_DONE=1
rm -f "$PARTIAL_MARKER"
echo "WORLDLINE installed: runtime $(python3 -c 'import worldline; print(worldline.__version__)') · engine ${ENGINE_COMMIT:0:12} · plugin $(git -C "$PLUGIN" rev-parse --short HEAD) · library $(sha256sum "$DEST/libworldline_core.so" | cut -c1-12)"
echo "No managed root was initialized and no AI agent was launched."
echo "Desktop shell restart: $SHELL_RESTART"
echo "Receipt: $RECEIPT"
echo "Backup for rollback: $BACKUP   (scripts/rollback.sh $BACKUP)"

# Only now, with this install verified and its own backup the newest one, are older backups
# pruned. Each holds a full copy of the state directory, so an installer that never prunes fills
# the disk — and a full disk is a worse failure than the one the backups insure against. The
# newest WORLDLINE_BACKUP_KEEP are kept; 0 disables pruning entirely.
python3 "$ROOT/scripts/prune_backups.py" "$STATE/install-backups" --keep "${WORLDLINE_BACKUP_KEEP:-5}" --apply \
  || echo "install: pruning old backups failed; they are still there, which is the safe direction." >&2
