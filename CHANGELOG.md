# Changelog

## 1.0.2 — 2026-09-02 · recovery, evidence coverage, and honest surfaces

A second audit pass covered the surfaces the first one did not reach: the QML desktop plugin
(both copies), the Ada/SPARK core source and proof gate, the public claims documents, and the
remaining crash-consistency defects. Every finding below survived an adversarial verification
pass. The Ada logic itself was checked hard and is sound — SHA-256 was differentially tested
byte-identical against `hashlib` for every length 0–599 plus the NIST vectors, and the C ABI,
the atomic-exchange design and the durability primitives all hold. No Ada source changed here,
so the 130-check proof is untouched.

### Fixed — availability

- **Recovery could permanently brick the daemon.** A crash between the prepared-record write
  and its database row leaves the two durably disagreeing; `_load_record` treats that as fatal
  and `recover_all` had no per-transaction containment, so the exception propagated out of
  `daemon.start()` **before the socket was published** — every command, including the read-only
  diagnostics needed to understand the problem, then failed with `DAEMON_UNAVAILABLE` on every
  boot until the operator hand-edited JSON and SQLite. Recovery now quarantines an unresolvable
  transaction and reports it; mutation (`prepare`/`commit`) refuses with `RECOVERY_INCOMPLETE`
  while any quarantine stands. Fail open for diagnosis, fail closed for anything touching PRIME.

- **A second, identical brick via non-idempotent checkpoint publication.** `publish_checkpoint`
  inserts a world under the deterministic alias `prime-<transactionId>` and only then calls
  `set_prime`, so a crash between them made replay hit the UNIQUE constraint forever — with the
  atomic exchange already committed, i.e. the user's files collapsed while the recorded PRIME
  was stale. The insert now adopts an existing generation when its content identity matches
  (`instance_id` is not part of `content_id`, so a genuine replay matches) and raises
  `RECOVERY_STATE_MISMATCH` on real divergence.

### Fixed — evidence integrity

- **A collapse could commit with no receipt, permanently, while `log --verify` passed.** A crash
  between the COMMITTED state write and the receipt append left the chains internally consistent
  and merely shorter, so verification reported clean over the hole — breaking the system's
  central claim that every committed collapse has a receipt in a tamper-evident chain. Recovery
  now replays `_finish_committed` for any COMMITTED transaction lacking a receipt, and
  `doctor` reports `receiptCoverage` so the gap is visible even if that replay fails.

- **`doctor` now reports `storeIntegrity`.** A SIGKILL during `worldline init` can leave the
  operator's real directory inside the store with no row pointing at it — and `rootIntegrity`
  answered `OK` because it iterates rows that do not exist. The new scan reports unreferenced
  captured payloads (recovering the original path from the manifest written before the rename),
  orphaned live mappings, and orphaned prepared records whose staged payload is unreclaimed.

### Fixed — the proof gate

- **The gate could not distinguish a healthy `gnatprove` run from a stale or empty one.** It
  discarded gnatprove's exit status, never removed the previous summary, and had no floor — so a
  run that analyzed nothing reported "0 checks, all proved, nothing assumed" and passed. It now
  fails on a non-zero gnatprove exit, deletes the stale summary first, enforces
  `MINIMUM_CHECKS = 130`, records `summarySha256` binding the manifest to the artifact it was
  read from, and screens (comment-stripped, case-insensitive) for `pragma Assume`, GNATprove
  justification pragmas, and any `SPARK_Mode => Off` outside the declared C-boundary exception.

### Fixed — desktop plugin (both copies)

- **An in-world agent could forge UI chrome on the collapse-authorization screen.** QML `Text`
  defaults to `AutoText`, so Qt's rich-text heuristic rendered engine-supplied strings —
  including agent-chosen filenames — as markup on the exact panel a human reads before
  approving an irreversible PRIME replacement. All 65 `Text` elements across both copies are now
  `textFormat: Text.PlainText`. (No code execution was possible and no exfiltration channel
  could be constructed; this was display spoofing, and it was the only defect in the pass with a
  genuine in-scope adversary.)
- **The panel affirmed two gates it never evaluated.** "Foreign contamination: NONE" and
  "Conflicts: 0" were read from world fields the runtime never writes (they are `[]` at
  construction and assigned nowhere). Before a collapse they now read `UNEVALUATED — computed at
  collapse.prepare` and `—`. The real gate always ran server-side; the defect was misinformation
  at the decision point.
- Delta file lists rendered as left-truncated JSON blobs because the lookup missed the key the
  runtime actually emits (`pathDisplay`). Job failures rendered as `[object Object]`. A world
  alias beginning with `-` was parsed as an option by `worldline return`, retargeting PRIME's
  parent; commands now pass `--`. A check whose status was neither PASS nor FAIL (e.g.
  `UNAVAILABLE`) was rounded up to a green PASS badge; it now reports `UNASSESSED`.

### Claims corrected

`SKILL.md` no longer tells an agent that a world is "already contained" without qualification —
network effects are not contained, and that sentence gates unattended runs. Also corrected: the
kernel-authority sentence (the kernel supplies the verdict; the runtime decides what is compared
and performs the exchange), the `simulate` claim (filesystem-only), `SECURITY.md` on what of
`$HOME` is actually projected into a world, the sandbox uid description, and the health-check
assertion count (25, not 26). Corrections required in the whitepaper and user manual — which are
PDFs and cannot be edited here — are itemized with exact replacement wording in
`DOC-CORRECTIONS.md`.

### Tests

`tests/test_security_hardening.py` grows to 14 tests covering recovery containment, the mutation
gate, `storeIntegrity`, and `receiptCoverage` alongside the existing git-config-exec, alias, and
root-integrity coverage. Full suite: 58 passed. Health check and both Ada binaries
(`worldline_core_tests`, `worldline_core_fuzz`) pass.

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
