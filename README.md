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
./install.sh
```

Order: build the library → Ada tests → Python suite → proof gate (`prove.sh`, every check
must prove; `WORLDLINE_SKIP_PROOF=1` skips only the re-run, the manifest is always verified
against the library) → refuse if agent jobs are running (`WORLDLINE_FORCE=1` overrides) →
**backup** → install runtime + library + launchers + user unit → fast-forward the plugin
checkout from `../worldline-omarchy` (refuses to overwrite a diverged checkout) → patch
`shell.json` and `bindings.lua` → restart `worldlined` → `hyprctl reload` → restart the shell
(`WORLDLINE_NO_SHELL_RESTART=1` defers it). It ends by printing what it installed and the
backup directory.

Verify afterwards:

```bash
worldline status --json | jq '.daemon'          # version, RUNNING
worldline doctor --json | jq '{rootIntegrity, storeIntegrity, recovery, openTransactions}'
bash ~/.claude/skills/worldline/scripts/health_check.sh   # 47 assertions, zero quota, host untouched
```

## Rollback

Every install writes `~/.local/state/worldline/install-backups/<UTC stamp>-<pid>/` holding
`lib-worldline/` (previous runtime + library + manifest), the previous `worldline` and
`worldlined` launchers, `worldlined.service`, `shell.json`, `bindings.lua`, and
`plugin-commit`. To go back to it:

```bash
B=~/.local/state/worldline/install-backups/<stamp>
worldline status --json | jq '[.jobs[] | select(.state=="RUNNING")] | length'   # must be 0
systemctl --user stop worldlined.service
rm -rf ~/.local/lib/worldline && cp -a "$B/lib-worldline" ~/.local/lib/worldline
install -m 0755 "$B/worldline" "$B/worldlined" ~/.local/bin/
install -m 0644 "$B/worldlined.service" ~/.config/systemd/user/worldlined.service
install -m 0600 "$B/shell.json" ~/.config/omarchy/shell.json
install -m 0600 "$B/bindings.lua" ~/.config/hypr/bindings.lua
git -C ~/.config/omarchy/plugins/khephri.worldline checkout --quiet "$(cat "$B/plugin-commit")"
systemctl --user daemon-reload && systemctl --user start worldlined.service
worldline status --json | jq -r .daemon.version    # the previous version
omarchy-restart-shell                               # only if the plugin commit changed
```

The store (`~/.local/share/worldline`, `~/.local/state/worldline`) is not part of the backup
and is not touched by a rollback: newer runtimes only add fields, and every generation and
receipt stays readable by the older code. Run `./install.sh` again to move forward.

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
