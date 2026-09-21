# Changelog

## 1.2.0 — 2026-09-20 · contained network, timeouts, prune, anchored receipts, git roots

Everything a finished tool needs that 1.1.1 still lacked, each exercised for real afterwards.

### Added

- **Network policy per world** (`network.policy` in the global config: `shared`, `allowlist`,
  `none`). Under `allowlist` a world gets an empty network namespace and exactly one door: a
  proxy the daemon runs on a Unix socket bound into the world's runtime, which only connects to
  the adapter's provider hosts plus `network.allow`; the in-world forwarder sets the proxy
  environment every CLI honours. Refusals are recorded on the agent check (`network.refused`),
  so a blocked host is evidence, not a mystery. `none` is the same namespace without the door.
  Checks and services get no network under either restrictive policy; `simulate` stays shared
  (documented). Default remains `shared`, unchanged behaviour.
- **Timeouts.** `fork --timeout SECONDS`, `race --timeout`, and `limits.defaultTimeoutSeconds`.
  A world that exceeds its limit is stopped through its unit; the agent check reads
  `FAIL · TIMEOUT: …`, project checks are `UNASSESSED` with the reason, the job is `TIMED_OUT`
  with `{"code":"TIMEOUT","seconds":N}`, and the world finalizes `DEGRADED`.
- **`worldline prune`** (`--older-than DAYS`, `--keep N`, `--logs`, `--dry-run`, `--yes`).
  Deletes the payload directories of finished worlds that nothing living refers to and marks
  them `payload_pruned`; records, receipts, and causal events stay, and a `prune` event is
  recorded per world. PRIME, the checkpoint `return` goes back to, running worlds, and any
  directory still referenced by an unpruned world or a live root are never touched. Anything
  that needs a pruned payload refuses `PAYLOAD_PRUNED`. `doctor.storeUsage` reports bytes by area.
- **Anchored receipts.** Every committed receipt is appended to an Ed25519-signed, hash-chained
  ledger in the Custos format, so `attest verify-custos LEDGER PUBKEY` replays the chain and
  every signature with the SPARK-proved implementation in `~/Projects/attest`. `anchor.exportPath`
  mirrors the ledger somewhere the store's writer does not control; `worldline anchor`,
  `log --verify`, and `doctor.anchor` report the local verdict, the attest verdict, and whether
  the external copy matches, is behind, or shows a local rollback. Receipts that predate the
  ledger are backfilled at startup.
- **Store schema migrations.** The SQLite `user_version` is now `STORE_SCHEMA_VERSION` (2) with
  forward-only migrations recorded in `meta.schemaMigrations`; a store newer than the runtime
  is refused `UNSUPPORTED_SCHEMA` by name instead of being opened.
- **`show` carries repository facts** (`head`, `branch`, `dirty`, hashes) for `repo` roots.
- **Bounded status document.** A world summary caps its delta file list at 200 entries and
  says so (`truncated`, `total`); `show` still returns everything.

### Fixed

- **A git repository root could never collapse.** `git diff` rewrote the freshly materialized
  staged tree's index (racy stat data; `GIT_OPTIONAL_LOCKS` does not cover that write), so
  commit re-hashed a different tree and refused `STAGED_ROOT_MISMATCH` every time. Inspection
  now runs against a private copy of the index. The full cycle — agent commits inside its
  world, collapse lands the commit in the live repository, return takes it out — is in
  `tests/test_boundaries.py::RepositoryRootCollapse`.
- **`return` after a reconcile.** A checkpoint displaced by a reconcile (PRIME changed while the
  daemon watched, a new generation was published from it) is now accepted when it hashes to
  that generation's state root, alongside the receipt-witness rule from 1.1.1.
- **`return` to a checkpoint that predates a root registration** says so
  (`RETURN_POINT_INCOMPLETE` names the missing root) instead of a bare root key.

Suite: 94.

## 1.1.1 — 2026-09-20 · the builtin agents actually run

Every builtin adapter was exercised for real, with the operator's own credentials, in a private
harness (own store, socket, and root; real `$HOME`). None of the four had ever completed a
world on this machine. Each failure was reproduced, fixed at its cause, and covered by a test;
then claude and codex forks reached `VALID`, a real three-lane race (claude, codex, claude)
reached `VALID` on all lanes, the codex lane was collapsed through a prepared transaction and
returned, and `log --verify` replayed clean both times.

### Fixed — why no real world ever finished

- **DNS did not work inside any world.** `/run` is a fresh tmpfs in the sandbox, and on this
  machine `/etc/resolv.conf` is the systemd-resolved symlink into `/run/systemd/resolve`, so
  every agent failed name resolution with "Try again" and reconnected until it gave up (codex sat
  `MUTABLE` for minutes doing exactly that). The resolver directory is now bound read-only into
  the world. `tests/test_sandbox.py` resolves a real name from inside a world.
- **Claude Code refused to start as namespace root.** `--dangerously-skip-permissions` is
  rejected when euid is 0, and the sandbox mapped the operator to uid 0. Agent worlds, checks,
  and shells now run as the real uid inside the user namespace (nothing about reach changes; the
  real uid is the only one mapped). `simulate` futures keep namespace root on purpose.
- **Claude Code refused its own output format.** `--print --output-format stream-json` requires
  `--verbose` since Claude Code 2.1; the adapter's argv lacked it.
- **Claude Code's hooks blocked the mission.** The projected `settings.json` carries the
  operator's desktop hooks (a cockpit tracker on every event on this machine); inside a world the
  script does not exist, the `UserPromptSubmit` hook exits 2, and Claude Code reports *success*
  having done nothing. Hooks are disabled in-world via `--settings '{"disableAllHooks":true}'`
  (`--bare` would also refuse the operator's OAuth credential).
- **omp died with `SQLITE_READONLY`.** It stamps `schema_version` into `~/.omp/agent/agent.db`
  at startup, and the database was bound read-only. The world now gets a per-world private copy
  made with the SQLite backup API (WAL folded in, `0600`, under the world's runtime) and bound
  writable; the host database is never mounted. `CredentialProjection.private_copy` plus
  `materialize_private_copies` in the runner; the sandbox refuses a writable projection that is
  not inside the world runtime. (omp still fails on this machine, honestly: its configured
  default model is rejected by the provider — the same request fails outside WORLDLINE.)
- **pi was reported `AVAILABLE` with an empty login.** `~/.pi/agent/auth.json` exists but
  declares no provider, so every pi world died with "No API key found". The adapter now reads the
  file's shape (never a value) and reports `UNAVAILABLE: pi has no provider credentials … run
  \`pi login\``.
- **An unauthenticated agent produced a DEAD world instead of a refusal.** `fork` and `race`
  now probe the adapter's credentials before the freeze and refuse `ADAPTER_AUTH_UNAVAILABLE`
  with no world, no checkpoint, and no generation left behind
  (`test_unauthenticated_adapter_is_refused_before_any_checkpoint`).
- **Daemon log spam after a detached fork.** Progress events for a client that had already
  disconnected raised `socket.send() raised exception` every few seconds; the daemon now drops
  them silently (the causal chain is the durable record).
- **A full disk answered `INTERNAL_ERROR`.** Fault injection on a 6 MB tmpfs: the daemon
  survived, PRIME stayed intact, `doctor` stayed `OK`, and everything recovered once space
  returned — but `fork`, `collapse --prepare`, and `status` all failed with the unnamed
  `INTERNAL_ERROR: daemon operation failed`. Storage failures are now named: `DISK_FULL`
  (ENOSPC, EDQUOT, SQLite "disk is full") or `STORAGE_ERROR`, with the errno name and path in
  the details, and logged with a traceback.
- **`return` refused a checkpoint that had been live.** Found on the live machine after the
  first real collapse into `aegis-anubis`: `return --prepare` answered
  `PAYLOAD_INTEGRITY_FAILED: candidate payload path set differs from its manifest`. The
  displaced checkpoint had been PRIME since 2026-08-29 and the project had written 257
  generated files (`out/`, `keys/`) into it; its stored manifest describes it as it was
  committed, not as it was displaced. What `return` restores is the state at the instant of
  displacement, and every committed exchange already records that as its receipt's
  `beforeRoot`. A return point whose stored manifest no longer matches is now captured fresh
  and accepted only if it hashes to a `beforeRoot` some committed receipt recorded; the return
  receipt's `afterRoot` then equals that `beforeRoot`. A payload that changed after it left
  reality matches neither and is refused with the reason
  (`tests/test_boundaries.py::ReturnAfterTheCheckpointWasLive`).
- **The skill's `pick_candidate.py` recommended PRIME itself.** `list` includes the PRIME
  generation as a `VALID` world with an empty delta, which won every ranking. PRIME rows are
  excluded as "a checkpoint, not a candidate".

### Tests

`tests/test_boundaries.py` (new, 4 scenarios): hostile root contents (unicode, spaces, shell
metacharacters, leading dashes, mixed modes, nested and empty directories, relative symlinks,
hardlinks; `EXTERNAL_SYMLINK` and `UNSUPPORTED_SPECIAL_FILE` refusals; everything preserved
through collapse, return, and `root remove`), malformed agent output (binary junk, a 100 KB
line, then a valid event), daemon `kill -9` with a running agent and a `PREPARED` transaction
(after restart: world `DEAD/DAEMON_RESTART`, job `DEGRADED`, transaction
`ABORTED/RECOVERED_BEFORE_COMMIT`, PRIME untouched, fresh commit works), and a competing daemon
(`DAEMON_ALREADY_RUNNING`). Suite: 83.

## 1.1.0 — 2026-09-20 · prepared transactions, supervision, proved lifecycle, cockpit

The desktop plugin was rewritten around an explicit transaction contract, and the engine grew
the pieces that contract needs. Every item below was reproduced first, fixed, and covered by a
test (`tests/test_lifecycle_integrity.py`, 13 new tests; suite 72). The proof gate reran on the
one kernel change: 130 checks, all proved, nothing assumed, threshold unchanged.

### Fixed — diagnostics that lied

- **`doctor.storeIntegrity` reported DEGRADED over its own retained history.** The scan only
  counted each world's produced payload (`payload_path`), never the frozen checkpoint it was
  forked from (`base_payload_path`), so after `root remove` every fork checkpoint read as
  `ORPHANED_GENERATION`. The skill's health check completed "successfully" with that finding
  in its final report. The scan now references both; the health check asserts `OK`.
- **`doctor.systemd` stuck at `UNAVAILABLE: starting` for the whole session.** The capability
  registry cached the first probe forever, and the daemon starts while the user's systemd
  manager is still "starting". `UNAVAILABLE` answers are re-probed after 30 s (`AVAILABLE`
  stays cached); every entry carries `probedAt`.
- **`transaction list` crashed on any DENIED row** (`NON_CANONICAL_JSON … bytes`): the error
  column is a JSON blob and was forwarded raw.

### Fixed — worlds nobody supervised

- **A world could stay MUTABLE forever.** `create_world` inserted the row before `run_world`
  could fail (unknown adapter, invalid `.worldline.json`, sandbox refusal), and the startup
  sweep only handled worlds that had a job. Such a world reads as "running" on every surface
  and blocks every later `root add`/`root remove` with `ROOT_SET_BUSY` — the live machine had
  one (`harden`, born 2026-08-29). `run_world` now terminates a world whose run cannot start
  (`evidence.supervision` records why), the adapter is resolved *before* the checkpoint is
  frozen (an unknown adapter used to leak a full generation on disk), and the startup sweep
  covers job-less nonterminal worlds.
- **The old sweep wrote a transition the proved kernel forbids.** `mark_orphaned_jobs_degraded`
  set `MUTABLE → DEGRADED` straight in SQL; `Transitions.Allowed` permits `MUTABLE →
  FINALIZING | DEAD` only. Lost supervision now goes through `World.transition` to `DEAD`
  (no coherent payload exists), with `DAEMON_RESTART` or `NO_SUPERVISING_JOB` in the evidence.
- **Isolated instances could start transient units but never stop, query, or cancel them.**
  `systemctl --user` insists on `$XDG_RUNTIME_DIR/systemd/private` and does not fall back to
  the session bus the way `systemd-run --user` does, so any redirected `XDG_RUNTIME_DIR` (the
  health check, the e2e tests, a second daemon) lost supervision after launch. The adapter now
  addresses the manager that owns the units explicitly.

### Added — the contract a UI can be honest with

- `worldline collapse WORLD --prepare --json` / `worldline return [WORLD] --prepare --json`
  stage the transaction and return the facts (decision, before/candidate/staged roots, managed
  roots, every operation, evaluated conflicts and contamination, dependency changes,
  `candidate_alias`, `prepared_at`) leaving it PREPARED; `worldline transaction commit ID
  [--yes]`, `abort ID`, `list`, `show ID`. Commit re-verifies PRIME against the reviewed
  `beforeRoot` and refuses with `PRIME_CHANGED_AFTER_PREPARE`; a DENIED transaction can never
  commit; a duplicate commit is `INVALID_TRANSACTION_STATE`.
- `worldline cancel WORLD` stops the agent's transient unit. The world finalizes DEGRADED with
  the agent check `FAIL` (`USER_CANCELLED`), project checks recorded `UNASSESSED` with the
  reason, and the job `CANCELLED` — partial work stays inspectable, never collapsible.
- `init` / `root add` / `root remove` `--dry-run --json`: the confirmation facts as data,
  nothing moved.
- `race --name N` prefixes the alpha/beta/gamma lanes so a second race does not collide.
- `doctor` gains `recovery` (quarantined transactions, previously invisible until a mutation
  refused), `openTransactions` (a PREPARED review holds a staged payload and freezes the root
  set), and `unsupervisedWorlds`.

### Kernel

- `wl_transaction_transition_allowed` is exported through the C ABI and consulted on every
  transaction state change; the Python mirror table is kept only as a cross-check and a
  disagreement raises `CORE_DISAGREEMENT`. The transaction lifecycle is therefore enforced by
  the proved unit, closing the first half of `DOC-CORRECTIONS.md` §1.
- The kernel's parent comparison is no longer tautological: `prepare` supplies the parent
  identity the store holds as `expected_parent` and the candidate's claim as
  `candidate_parent`, and a forged claim is denied `PARENT_MISMATCH` (test). `_authorize`
  re-checks the same pair at commit (`parentContentExpected` in the record).
- No SPARK source changed; only `worldline-c_api.{ads,adb}` (the declared unproved boundary)
  and the header. `prove.sh` reran: 130/130, manifest regenerated and re-verified.

### Install and source of truth

- `omarchy/` is gone from this repository. It held a 665-line 1.0 snapshot of the plugin that
  `install.sh` copied over the deployed cockpit — the next install would have silently replaced
  the 1.1 mission-control overlay with it. The plugin lives in `~/Projects/worldline-omarchy`
  and is deployed as a git checkout at `~/.config/omarchy/plugins/khephri.worldline`; the
  installer fast-forwards that checkout (refusing on local edits) and validates it with
  `omarchy-plugin-validate`. The checkout's remote is `origin`, so `omarchy plugin update
  khephri.worldline` works too.
- `install.sh` backs up the previous library, launchers, unit, `shell.json`, `bindings.lua`,
  and the plugin commit id under `~/.local/state/worldline/install-backups/<stamp>`, refuses
  to restart the daemon while agent jobs are running (`WORLDLINE_FORCE=1` overrides), waits
  for the new socket, and restarts the shell so keepLoaded plugin components actually swap.

### Documented

- `SECURITY.md` §3 and `DOC-CORRECTIONS.md` §1/§6 updated for the lifecycle export and the
  meaningful parent check. Nothing about network containment or chain authentication changed:
  the world still shares the host network, and the evidence chain is still an unsigned hash
  chain.

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
