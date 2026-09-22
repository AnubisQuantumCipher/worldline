# WORLDLINE

A branch operator for a working machine. PRIME is the captured state of the directories you
nominate; a **world** is a proposal forked from PRIME in which a coding agent runs isolated
(overlayfs + bubblewrap); exactly one world becomes reality through a single atomic filesystem
exchange (`renameat2(RENAME_EXCHANGE)`) that a SPARK-proved kernel authorized; `return` restores
the previous reality the same way. The desktop cockpit lives in the separate
`worldline-omarchy` repository (`../worldline-omarchy`), deployed as the Omarchy plugin
`khephri.worldline`.

| | |
|---|---|
| Runtime (Python 3.14) | `runtime/worldline` — daemon, CLI, store, transactions, sandbox, adapters |
| Proved kernel (Ada/SPARK) | `core/` → `lib/libworldline_core.so`, `proof-manifest.json`, `prove.sh` |
| Launchers | `cli/worldline`, `daemon/worldlined` (run the repo runtime; the installed copies live in `~/.local/bin`) |
| Tests | `tests/` — `python3 -m unittest discover -s tests -p 'test_*.py'` (PYTHONPATH=runtime), plus the Ada tests and fuzz in `tests/*.adb` |
| Docs | `CHANGELOG.md`, `SECURITY.md`, `DOC-CORRECTIONS.md`, and the operator skill at `~/.claude/skills/worldline` |

## Install

```bash
WORLDLINE_PLUGIN_REF=$(git -C ../worldline-omarchy rev-parse main) ./install.sh
```

The plugin commit is required: an engine release does not identify the plugin, so the installer
will not pick one (`WORLDLINE_PLUGIN_ALLOW_MOVING_REF=1` accepts whatever `main` is now, and
says so). Order, which is deliberate:

refuse if a previous install did not finish → resolve the engine and plugin identities → build
the library → Ada tests → Python suite → proof gate (`prove.sh`; `WORLDLINE_SKIP_PROOF=1` skips
only the re-run, the manifest is always verified against the library) → **fail-closed preflight**
(`scripts/preflight.py`; an unreadable daemon refuses, it does not pass) → **stop the daemon** →
backup (runtime, launchers, unit, desktop config, plugin commit, unit state, and the whole state
directory) → install runtime + library + launchers + unit → fast-forward the plugin to the pinned
commit → patch `shell.json` and `bindings.lua` → start `worldlined` → **verify that what is
running is what was built** (`scripts/verify_install.py`) → `hyprctl reload` → restart the shell
(`WORLDLINE_NO_SHELL_RESTART=1` defers it; a failed restart is reported, not hidden). It ends by
printing what it installed, the receipt and the backup directory.

The daemon is stopped before the backup and the swap. That is what prevents a fork, race or
ghost from starting against a half-replaced runtime, and what makes the store backup consistent
rather than a copy of a live SQLite file.

Verify afterwards:

```bash
worldline status --json | jq '.daemon'          # version, RUNNING
worldline doctor --json | jq '{rootIntegrity, storeIntegrity, recovery, openTransactions, policy}'
bash ~/.claude/skills/worldline/scripts/health_check.sh   # 47 assertions, zero quota, host untouched
```

## Rollback

Every install writes `~/.local/state/worldline/install-backups/<UTC stamp>-<pid>/` holding
`lib-worldline/` (previous runtime + library + manifest), the previous `worldline` and
`worldlined` launchers, `worldlined.service`, `shell.json`, `bindings.lua`, `plugin-commit`, the
unit's prior enablement and run state, `backup-manifest.json` (what was captured, and what was
absent rather than missed), and `state/` — the store, receipts, transactions and events, taken
with the daemon stopped.

```bash
scripts/rollback.sh ~/.local/state/worldline/install-backups/<stamp>              # engine only
scripts/rollback.sh ~/.local/state/worldline/install-backups/<stamp> --with-state # also the store
```

Engine-only is the default: the store keeps whatever has happened since. `--with-state` is a
data rollback — anything recorded after the backup is discarded — so the superseded store is
moved aside rather than deleted, and the path is printed. Rollback restores the unit's recorded
enablement instead of switching the daemon on, and refuses while transient world units exist.

Payload data under `~/.local/share/worldline` is copied only when the install ran with
`WORLDLINE_BACKUP_PAYLOADS=1`; otherwise `payload-inventory.txt` records what existed.

Older runtimes keep reading newer stores — newer ones add fields rather than change them. That
is rehearsed rather than assumed: `worldline-lab/deploy/rehearse.py` runs the upgrade and the
rollback on a throwaway copy and checks that the previous engine opens and verifies the store
the new one wrote to.

## Operating limits and hygiene (1.2.0)

| Concern | Setting or command |
|---|---|
| Egress from a world | `network.policy` = `shared` (default) · `allowlist` (provider hosts + `network.allow`, refusals recorded) · `none` |
| Runaway agents | `fork --timeout SECONDS`, `race --timeout`, `limits.defaultTimeoutSeconds` → job `TIMED_OUT`, world `DEGRADED` |
| Disk growth | `worldline prune [--older-than DAYS] [--keep N] [--logs] [--dry-run]`; `doctor.storeUsage` |
| Receipt integrity beyond the store | `worldline anchor`, `anchor.exportPath`, `attest verify-custos ~/.local/state/worldline/anchor.tsv ~/.config/worldline/anchor/public.hex` |
| Store format changes | forward-only migrations (`meta.schemaMigrations`); a newer store is refused, never downgraded |
| Model and effort for a builtin agent | `adapterOptions.<name>.argv`, e.g. codex `["-m", "gpt-5.6-luna", "-c", "model_reasoning_effort=max"]`; visible in `worldline adapters` |

## Continuous integration and releases

`.github/workflows/assurance.yml` is the one assurance of an exact commit: it checks out a full
commit id, verifies the checkout is that commit, and runs `scripts/assurance.py` — build, Ada
tests and fuzz, the Python suite (bubblewrap 0.11, overlayfs and a lingering user systemd
manager are set up on the x86_64 runner), the SPARK proof gate re-run on that build, and the
proof-manifest check with the library — recording every outcome, the tree identity and the
toolchain into `assurance.json`. `ci.yml` calls it for every push and pull request;
`release.yml` calls it for the commit a `v*` tag names and publishes only after
`scripts/release_gate.py` accepts that report for that commit (never "latest green main",
never a partial run, never a moved tag or an existing release), as a draft whose uploaded
assets are verified before it is published and again after. `docs/release-process.md` states
the boundaries. Publishing a release does not install it anywhere.

## Isolated testing

- `tests/test_boundaries.py` and `tests/test_lifecycle_integrity.py` start private daemons in
  temporary XDG trees with deterministic fixture agents.
- `../worldline-omarchy/tools/ui-harness.sh start` (fixture) or `start --real` (real
  credentials, private store and root) gives the cockpit and the CLI an isolated daemon;
  the summon payload it prints routes every command at that daemon.
- The skill's `scripts/health_check.sh` is the end-to-end acceptance run.
