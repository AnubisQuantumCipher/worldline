#!/usr/bin/env bash
# Restore a WORLDLINE installation from a backup directory written by install.sh.
#
#   scripts/rollback.sh ~/.local/state/worldline/install-backups/<stamp>-<pid> [--with-state]
#
# Restores, in the order that keeps the machine usable at every step: the daemon is stopped
# first, then the runtime, launchers, unit, desktop config and plugin commit are put back, then
# the daemon is started and asked to answer.
#
# --with-state additionally restores the store, receipts, transactions and events captured in
# the backup. That is a data rollback, not just an engine rollback: anything WORLDLINE recorded
# after the backup was taken — new worlds, collapses, receipts — is discarded. It is off by
# default for that reason, and refused unless the backup actually contains a state copy.
#
# What a backup cannot restore is stated rather than assumed: payload data under
# ~/.local/share/worldline is only present if the install ran with WORLDLINE_BACKUP_PAYLOADS=1.
# Without it, restoring an old store against newer payloads (or vice versa) is your decision to
# make deliberately; payload-inventory.txt records what existed at backup time.
set -euo pipefail

BACKUP="${1:-}"
WITH_STATE=0
[[ "${2:-}" == "--with-state" ]] && WITH_STATE=1
[[ -n "$BACKUP" && -d "$BACKUP" ]] || { echo "rollback: usage: $0 <backup-dir> [--with-state]" >&2; exit 2; }

LIB_HOME="$HOME/.local/lib"
DEST="$LIB_HOME/worldline"
PLUGIN="$HOME/.config/omarchy/plugins/khephri.worldline"
SERVICE="$HOME/.config/systemd/user/worldlined.service"
STATE="$HOME/.local/state/worldline"
SHARE="$HOME/.local/share/worldline"
SOCKET="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/worldline/worldlined.sock"

# A backup whose manifest is missing was interrupted while being written, and restoring it would
# overwrite a working installation with a partial copy. The manifest is written last by design.
if [[ ! -f "$BACKUP/backup-manifest.json" ]]; then
  echo "rollback: $BACKUP has no backup-manifest.json, so it was never completed." >&2
  echo "rollback: restoring it could overwrite a working installation with a partial copy. Refusing." >&2
  exit 2
fi
UNCAPTURED=$(python3 -c 'import json,sys; print(",".join(json.load(open(sys.argv[1])).get("uncaptured", [])))' "$BACKUP/backup-manifest.json" 2>/dev/null || echo "unreadable")
if [[ -n "$UNCAPTURED" && "$UNCAPTURED" != "unreadable" ]]; then
  echo "rollback: this backup is incomplete — present on the machine but not captured: $UNCAPTURED" >&2
  echo "rollback: refusing rather than restoring a partial installation." >&2
  exit 2
fi

echo "rollback: restoring from $BACKUP"
[[ -f "$BACKUP/install-receipt.json" ]] && echo "rollback: that install's receipt is $BACKUP/install-receipt.json"

if [[ "$WITH_STATE" == "1" && ! -d "$BACKUP/state/worldline" ]]; then
  echo "rollback: --with-state was requested but this backup holds no state copy." >&2
  exit 2
fi

if systemctl --user is-active --quiet worldlined.service; then
  echo "rollback: stopping the daemon"
  systemctl --user stop worldlined.service
  for _ in $(seq 1 100); do systemctl --user is-active --quiet worldlined.service || break; sleep 0.1; done
  for _ in $(seq 1 50); do [[ -S "$SOCKET" ]] || break; sleep 0.1; done
fi
LEFTOVER=$(systemctl --user list-units 'worldline-*' --all --plain --no-legend 2>/dev/null | awk '{print $1}' | grep -v '^worldlined.service$' || true)
if [[ -n "$LEFTOVER" ]]; then
  echo "rollback: transient world units are still present; stop them before rolling back:" >&2
  printf '%s\n' "$LEFTOVER" >&2
  exit 2
fi

if [[ -d "$BACKUP/lib-worldline" ]]; then
  echo "rollback: runtime and proved library"
  OLD="$LIB_HOME/.worldline-rollback-$$"
  [[ -e "$DEST" ]] && mv "$DEST" "$OLD"
  cp -a "$BACKUP/lib-worldline" "$DEST"
  rm -rf "$OLD"
else
  echo "rollback: this backup holds no runtime copy (was there an installation before it?)"
fi

for launcher in worldline worldlined; do
  [[ -f "$BACKUP/$launcher" ]] && install -m 0755 "$BACKUP/$launcher" "$HOME/.local/bin/$launcher"
done
[[ -f "$BACKUP/worldlined.service" ]] && install -m 0644 "$BACKUP/worldlined.service" "$SERVICE"
[[ -f "$BACKUP/shell.json" ]] && install -m 0600 "$BACKUP/shell.json" "$HOME/.config/omarchy/shell.json"
[[ -f "$BACKUP/bindings.lua" ]] && install -m 0600 "$BACKUP/bindings.lua" "$HOME/.config/hypr/bindings.lua"

PLUGIN_RESTORED="not attempted"
if [[ -f "$BACKUP/plugin-commit" && -d "$PLUGIN/.git" ]]; then
  WANT=$(cat "$BACKUP/plugin-commit")
  echo "rollback: plugin -> $WANT"
  if ! git -C "$PLUGIN" rev-parse --verify --quiet "${WANT}^{commit}" >/dev/null; then
    PLUGIN_RESTORED="FAILED (commit absent)"
    echo "rollback: WARNING the plugin commit $WANT is not present in $PLUGIN; leaving it as it is." >&2
  elif git -C "$PLUGIN" checkout --quiet --detach "$WANT"; then
    PLUGIN_RESTORED="$WANT"
  else
    # A dirty plugin checkout is one of the reasons an install aborts, so it is exactly the state
    # an operator reaching for rollback may be in. Aborting here would leave the engine rolled
    # back and the daemon still stopped, which is worse than finishing and saying so.
    PLUGIN_RESTORED="FAILED (local changes)"
    echo "rollback: WARNING could not move the plugin to $WANT (local changes?)." >&2
    echo "rollback: the ENGINE is being rolled back; the PLUGIN is NOT. Resolve with:" >&2
    echo "rollback:   git -C $PLUGIN status" >&2
  fi
fi

if [[ "$WITH_STATE" == "1" ]]; then
  echo "rollback: state (store, receipts, transactions, events) — discarding anything recorded since the backup"
  ASIDE="$HOME/.local/state/.worldline-superseded-$(date -u +%Y%m%dT%H%M%SZ)"
  # The current state is moved aside, never deleted: a data rollback must itself be reversible.
  if [[ -d "$STATE" ]]; then
    mkdir -p "$ASIDE"
    tar -C "$HOME/.local/state" -cf - --exclude='worldline/install-backups' worldline | tar -C "$ASIDE" -xf -
    find "$STATE" -mindepth 1 -maxdepth 1 -not -name install-backups -exec rm -rf {} +
  fi
  tar -C "$BACKUP/state" -cf - worldline | tar -C "$HOME/.local/state" -xf -
  echo "rollback: the superseded state was kept at $ASIDE"
  if [[ -d "$BACKUP/share/worldline" ]]; then
    echo "rollback: payload data (this backup was taken with WORLDLINE_BACKUP_PAYLOADS=1)"
    PASIDE="$HOME/.local/share/.worldline-superseded-$(date -u +%Y%m%dT%H%M%SZ)"
    if [[ -d "$SHARE" ]]; then
      mkdir -p "$PASIDE"
      tar -C "$HOME/.local/share" -cf - worldline | tar -C "$PASIDE" -xf -
      rm -rf "$SHARE"
    fi
    tar -C "$BACKUP/share" -cf - worldline | tar -C "$HOME/.local/share" -xf -
    echo "rollback: the superseded payloads were kept at $PASIDE"
  elif [[ -f "$BACKUP/payload-inventory.txt" ]]; then
    echo "rollback: payload data was NOT captured by that install, so it is left as it is."
    echo "rollback: what existed at backup time is listed in $BACKUP/payload-inventory.txt"
  fi
fi

echo "rollback: starting the daemon"
systemctl --user daemon-reload
# Enablement is restored from what the install recorded, not assumed. A daemon that was disabled
# or inactive before that install is put back that way rather than silently switched on.
WAS_ENABLED=""
WAS_ACTIVE=""
if [[ -f "$BACKUP/unit-state.json" ]]; then
  WAS_ENABLED=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("unitEnabled",""))' "$BACKUP/unit-state.json" 2>/dev/null || true)
  WAS_ACTIVE=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("unitActive",""))' "$BACKUP/unit-state.json" 2>/dev/null || true)
fi
case "$WAS_ENABLED" in
  enabled) systemctl --user enable worldlined.service >/dev/null 2>&1 || true ;;
  disabled) systemctl --user disable worldlined.service >/dev/null 2>&1 || true
            echo "rollback: worldlined.service was disabled before that install; leaving it disabled." ;;
  *) echo "rollback: the backup records no unit enablement (unitEnabled='${WAS_ENABLED:-absent}'); leaving it as it is." ;;
esac
if [[ "$WAS_ACTIVE" == "inactive" || "$WAS_ACTIVE" == "failed" ]]; then
  echo "rollback: worldlined.service was '$WAS_ACTIVE' before that install; NOT starting it."
  echo "rollback: restored. start it yourself with: systemctl --user start worldlined.service"
  exit 0
fi
systemctl --user start worldlined.service
for _ in $(seq 1 100); do
  systemctl --user is-active --quiet worldlined.service && [[ -S "$SOCKET" ]] && break
  sleep 0.1
done
systemctl --user is-active --quiet worldlined.service || { echo "rollback: the daemon did not start" >&2; exit 2; }
"$HOME/.local/bin/worldline" --json status > /dev/null || { echo "rollback: the daemon does not answer" >&2; exit 2; }

# The marker travels with a --with-state restore unless removed here, and while it exists the
# next install refuses and tells the operator to roll back — the recovery loop could not close.
rm -f "$STATE/install-incomplete"

# The desktop is holding the plugin commit and the config this rollback just moved. Restoring the
# files without telling the shell leaves the running session on the version that was rolled back.
DESKTOP="not attempted"
if [[ "${WORLDLINE_NO_SHELL_RESTART:-0}" != "1" ]] && command -v omarchy-restart-shell >/dev/null 2>&1; then
  hyprctl reload >/dev/null 2>&1 || true
  omarchy-shell -q shell rescanPlugins >/dev/null 2>&1 || true
  if omarchy-restart-shell; then
    DESKTOP="ok"
  else
    DESKTOP="FAILED"
    echo "rollback: the desktop shell restart FAILED; the engine and plugin are rolled back but the" >&2
    echo "rollback: session may have no bar or plugin surfaces. Re-run omarchy-restart-shell." >&2
  fi
fi

echo "rollback: plugin: $PLUGIN_RESTORED · desktop shell: $DESKTOP"
echo "rollback: restored. runtime $(python3 -c 'import sys; sys.path.insert(0, "'"$DEST"'/runtime"); import worldline; print(worldline.__version__)' 2>/dev/null || echo '?') · plugin $(git -C "$PLUGIN" rev-parse --short HEAD 2>/dev/null || echo '?')"
[[ "$WITH_STATE" == "1" ]] || echo "rollback: the store was NOT restored (pass --with-state for that); anything recorded since the backup is still present."
