# Changelog

## 1.0.1 — 2026-09-02 · security hardening

Follows the aggressive audit recorded in `SECURITY-AUDIT-2026-09-02.md`. The containment,
atomic-collapse, and crash-recovery core was found sound and unchanged; this release fixes a
confirmed host-level RCE and four supporting integrity/robustness bugs, and adds an honest
threat-model document. No Ada / proved-kernel source changed, so `proof-manifest.json` and the
130-check proof are untouched.

### Fixed

- **[critical] Host RCE via a hostile repository's `.git/config`.** `GitAdapter` inspected
  registered repos with host-side, unsandboxed `git`, and `git` executes commands named in the
  repo's own config during ordinary inspection (`core.fsmonitor` on `status`; hooks; textconv
  drivers). Because inspection runs at `worldline init` / `root add` **before** the operator
  confirms, a cloned hostile repo got code execution as the operator. Confirmed live on git
  2.55.0 (`core.fsmonitor` via `status --porcelain=v2`). `GitAdapter._run` now injects
  highest-precedence `-c` overrides for every exec-capable knob (fsmonitor, hooksPath,
  diff.external, sshCommand, pager, editor, askPass, credential.helper, uploadpack hook,
  protocol handlers) and a hardened environment (global/system config → `/dev/null`, no
  terminal/credential prompts, `GIT_OPTIONAL_LOCKS=0`, protocol restricted to local files).

- **[medium] Stale inotify watcher after collapse/return.** The atomic exchange swaps the
  `live` mapping, leaving every watch pinned to the pre-collapse payload inodes, so the
  `PRIME_CHANGED_DURING_CAPTURE` generation guard and dirty/reconcile tracking silently went
  stale after the first commit. `_collapse_commit` now rebuilds the watcher. (PRIME integrity
  was never at risk — the commit-time content re-hash is watcher-independent — but the
  defense-in-depth guard is now live again.)

- **[medium] No cross-process daemon exclusion.** A second `worldlined` would unlink the live
  socket and run collapses concurrently against the same WAL store, so two self-consistent
  exchanges could race. The daemon now takes an advisory `flock` on `worldlined.lock` for its
  lifetime and a second instance fails fast with `DAEMON_ALREADY_RUNNING`.

- **[low] Unbounded staging growth.** Denied/aborted transactions left a full PRIME-sized
  staged payload on disk. Terminal denied/aborted transactions now reclaim their staging
  directory (the signed transaction record is kept).

- **[low] Weak world-alias validation.** Operator-supplied fork/race names now reject control
  characters, names longer than 128 characters, and the reserved `PRIME` / `prime-*`
  provenance names (via `validate_user_alias`). WORLDLINE's own internal worlds still use those
  names through `validate_alias`, unchanged.

- **[low] Textconv residual on the RCE.** `GitAdapter.capture` now also passes `--no-textconv`
  on both diffs, closing the last attribute-driven diff-driver vector on top of the `-c`
  hardening.

- **[low] Power-loss torn PRIME.** The staged payload's directory entries are now fsynced before
  the atomic exchange (file contents were already fsynced), so a crash immediately after the
  durable rename cannot leave PRIME pointing at a tree whose dirents never reached disk.

- **[low] Silent root divergence made visible.** `worldline doctor` now reports `rootIntegrity`:
  a registered root that is no longer a symlink routing through the live mapping (e.g. an
  interrupted `root remove`, after which collapses would "commit" without touching the user's
  files) is surfaced as `BROKEN` instead of failing silently.

- **[low] `pick_candidate.py` exit-code contract.** A hostile `status.json` with NaN/Infinity in
  a delta now exits `3` (bad input) instead of crashing to `1`.

### Tests

- New `tests/test_security_hardening.py` locks in the fixes: a hostile `.git/config`
  (`core.fsmonitor` + `diff.external`) does not execute through the exact `capture()` argv — with
  a control that proves the repo is genuinely armed — plus the alias rules and the `doctor`
  root-integrity detection. Full suite: 51 passed.

### Documented, not changed (see SECURITY.md)

- The world sandbox shares the host network and mounts real agent credentials — inherent to
  letting an agent reach its model API, so the mitigation is a network-egress policy, a design
  decision left to the operator.
- The evidence chain is a hash chain with no asymmetric signature and no external anchor, so it
  is tamper-evident only against the sandboxed agent (which cannot reach the store), not against
  a same-uid process outside the sandbox. `invariantPreservation: PROVED` reflects the proved
  hash kernel, not an authenticated attestation of the running library.
