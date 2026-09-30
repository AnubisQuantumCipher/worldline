# Changelog

## 1.9.1 — 2026-09-30 · installer shell restart, truthful docs

**No change to the authority path, the kernel or the store.** This release fixes one installer
defect and two places where the documentation claimed more than the code does.

### Upgrading

- No store migration is needed. As after any release, revalidate VALID worlds before collapse,
  because the requirement identity includes the runtime tree.
- The known limitations listed under 1.9.0 are unchanged.

### Fixed

- **`install.sh` and `scripts/rollback.sh` no longer ask the desktop shell to rescan its plugins
  just before restarting it.**
  - A rescan keeps creating plugin objects for a moment after it returns. quickshell 0.3.1 frees
    its IPC handler registry as soon as the restart's kill arrives, so an object that completes in
    that window registers into freed memory and the shell segfaults instead of exiting
    (quickshell-mirror/quickshell#956).
  - Two of the three shell crashes on the reference machine were the installer's rescan racing
    its own restart. The restart re-reads every plugin anyway.
  - This carries the fix from the unmerged draft PR #7 onto the current release.
  - Tests:
    - `tests/test_rollback.py` runs the real rollback with a recording shim and asserts that no
      rescan is issued.
    - The installer's post-build path has no automated control, so a second test reads the
      shipped `install.sh` restart block instead.
    - Both tests fail against the 1.9.0 scripts.

### Documentation

- **The user manual no longer says a failed revalidation always leaves a world refused.** That
  holds only once the earlier evidence is stale. `validation.effective_evidence` still takes the
  newest PASS, so while an earlier PASS (from finalization or a revalidation) is fresh, a later
  FAIL does not supersede it. The Phase 1 documents already stated this (item 5); the manual now
  agrees with them.
- **SECURITY.md's review line is current, and names who reviewed.** It said "last reviewed
  against release 1.7.3" while describing 1.9.0 semantics. It now names 1.9.1. It also says
  that every review, including the 2026-09-02 audit document, was carried out by AI agents and
  checked against mechanical evidence, and that no human security audit is claimed.
- **`docs/release-process.md` records the repository rules now in force.** `main` changes only
  through a merged pull request whose up-to-date head passed `assurance / assure`, and a pushed
  `v*` tag can be neither moved nor deleted. Both GitHub rulesets have no bypass actors.

## 1.9.0 — 2026-09-29 · typed absence and honest collapse inputs

**The collapse decision no longer accepts a missing value as a matching one, and every input it
consults is measured.** Each identity is its own SPARK type with explicit presence; two absent
values are never equal, and nothing absent or unmeasured is ever authorized. Foreign managed
writes, PRIME stability and watch coverage are measured and decided in the kernel. The request
is decoded and validated by a proved SPARK unit instead of unproved C-boundary code. The
requirements-to-contract table is in `docs/phase1-typed-absence.md`.

### Upgrading

- **Install the library and runtime together.** The collapse request is ABI generation 5. A
  generation-4 library or runtime is refused at load, as in 1.8.0.
- **No store migration.** The SQLite schema (`user_version` 2), every table and column, world
  content identities, and the causal and receipt chain bytes are unchanged. Content roots (the
  identity of what an evaluation examined) now include symlink targets and use a new domain
  tag, so none computed by an earlier release compares equal to one computed now.
- **Pending transactions.** A PREPARED or AUTHORIZED transaction does not survive a daemon
  restart. At first start, recovery aborts it (`RECOVERED_BEFORE_COMMIT`), or finishes it when
  the live marker shows its exchange already happened. Prepare again. A rollback does the same.
- **Revalidate VALID worlds before collapse, as after every release.** The requirement identity
  includes the engine version, runtime tree and kernel library, so every stored evaluation is
  stale after an upgrade. The stricter evidence rules below therefore apply only to evidence
  1.9.0 writes, and 1.9.0 revalidation writes it in the required form.
- Worlds that are not VALID (ARCHIVED or COLLAPSED candidates) cannot be revalidated.
  Re-applying them stays refused with EVIDENCE_STALE, as after any upgrade. Also unchanged:
  - checkpoint returns to `prime-*` generations, witnessed as in 1.8.0, including the genesis
    PRIME;
  - pre-1.3 worlds are not promotable;
  - pruned or payload-less worlds are refused (PAYLOAD_PRUNED / INCOMPLETE_WORLD).
- **Upgrading directly from 1.7.3:** every 1.8.0 note also applies.
  - A project with no `.worldline.json` cannot collapse.
  - Pre-1.3 worlds are not promotable.
  - A PRIME from before the last root was removed, and a COLLAPSED `return-*` that published a
    generation, are no longer return points.
- **New refusals:**
  - **MEASUREMENT_ABSENT** — no PRIME watcher (no registered root could be watched), or
    conflicts or foreign writes could not be measured. 1.8.0 skipped the PRIME-stability guard
    here. `fork` refuses PRIME_WATCH_UNAVAILABLE for the same reason. (Without inotify at all
    the daemon does not start, as before.)
  - **WATCH_INCOMPLETE** — a registered root is not completely watched: a broken mapping, a
    root directory that went away or was moved, part of its tree that could not be watched (an
    unreadable directory, say), an overflowed event queue, or a watcher whose reader stopped.
    `doctor` lists the unwatched roots and why; the next reconcile walks them again. A root that
    cannot be watched completely never stops the daemon from starting.
  - **STORE_NOT_RELOCATED** (at daemon start) — the store's records name another store's files:
    it was copied without `worldline-relocate`.
  - **CHECKPOINT_IDENTITY_TAKEN** (at commit, before the exchange; the transaction is ABORTED
    and nothing changes) — the PRIME generation the commit would publish has the identity of an
    existing world. A declined `return` leaves its vehicle holding exactly that identity; in 1.8.0
    such a commit exchanged live PRIME and then failed to record it.
  - **RECOVERY_IO_FAILED** (at start) — recovery met an I/O error finishing a transaction; the
    transaction is quarantined and the daemon starts, as for any unrecoverable transaction.
  - **FOREIGN_MANAGED_WRITE** — live PRIME content differs from the PRIME record and the
    watcher did not report it. The refusal marks PRIME dirty; the next status or prepare
    records the change as a PRIME generation, and a retry proceeds.
  - **PRIME_CHANGED** (the error code is still PRIME_CHANGED_DURING_CAPTURE, at prepare and at
    commit) — PRIME changed while the decision was being made. The window runs from the
    requirement read through the capture, merge and staged-merge evaluation to the decision, and
    the refusal leaves a DENIED transaction record. A change between the commit decision and the
    exchange aborts the transaction with the same code.
  - **STAGED_UNTESTED**, now also in three new cases:
    - the bytes a staged-merge evaluation examined differ from the staged bytes;
    - a candidate whose declared finalization manifests are missing, where no staged
      evaluation covers the result. 1.8.0 re-captured the candidate silently;
    - a symlink in PRIME retargeted since the candidate was evaluated (content roots ignored
      link targets since 1.3.0).
  - **IDENTITY_ABSENT** — a required identity is missing from a world row or prepared record.
    Only damaged or hand-edited stores produce it.
  - **EVIDENCE_SUBJECT_MISMATCH** — the evaluation speaking for a world was bound to another
    world (previously EVIDENCE_CONTEXT_INVALID "belongs to a different world", decided in
    Python), or a return vehicle names another subject.
  - **CHECKPOINT_MISMATCH** — a witness exists but disagrees. CHECKPOINT_UNWITNESSED now means
    no witness.
  - **REQUIREMENT_IDENTITY_UNAVAILABLE** — the kernel library or the resource policy cannot be
    read, so no requirement can be stated. 1.8.0 hashed the unreadable value as null.
  - **TRANSACTION_RECORD_FOREIGN** — a transaction record names a path outside this store (a
    store copied without `worldline-relocate`). Recovery quarantines it and writes nothing;
    earlier releases aborted the ORIGINAL store's transaction and deleted its staging.
  - For evidence written by 1.9.0:
    - a policy-check record must state its profile;
    - a check with no declared verifier must record that none executed;
    - a record that ran an undeclared bundle does not match.
- **Codes.** OWNER_MISMATCH (3) is never produced. Codes 15–20 are new. Consumers of the header
  and the desktop plugin must learn them.
- **Receipts.** `foreignWorldContamination.state` now reports a measurement, with
  `measuredBy` and `measurement`. The receipt keys are otherwise unchanged. The evidence
  binding's `stagedValidation` gains `examinedContentRoot`. A FOREIGN_MANAGED_WRITE refusal
  lists the measurement under `details.contamination` as well as `details.foreignWrites`.
- **Before installing,** list pending transactions with `worldline transaction list` on the
  running release (they are aborted at the first start of the new one). **After installing and
  before the first collapse,** run `worldline doctor --refresh` on the new daemon and read
  `promotionReadiness`: the foreign-write measurement, unwatched roots and why, and the VALID
  worlds that are fresh, need revalidation, or cannot be revalidated (missing manifest, payload
  or base). Never start a daemon on a copy of a store that was not relocated with
  `worldline-relocate`: the store records absolute paths. 1.9.0 refuses to start on such a copy
  (STORE_NOT_RELOCATED); earlier releases started and acted on the original, aborting its
  transactions, stopping its running agents and overwriting its exported anchor ledger.

### Security: collapse inputs that were assumed, not measured (every deployment)

Each defect below was reproduced on released 1.8.0 before it was fixed, by one script run
against both trees (retained with the release evidence). On 1.8.0 every scenario was
AUTHORIZED and COMMITTED; on 1.9.0 each is refused by the kernel with the decision named. The
1.9.0 side is also tested end to end in `tests/test_typed_absence.py`. The fourth needs write
access to the store; the others arise in normal operation or from host conditions.

- **An unreported write into live PRIME went live under a receipt that denied it.** A file
  written into a managed root with no watcher event was carried into the new PRIME, and the
  receipt stated `foreignWorldContamination: NONE` with nothing measured. No PRIME generation
  or causal event ever recorded the write. 1.9.0 refuses FOREIGN_MANAGED_WRITE, records an
  `unaccounted-write` event, and reconciles the change into its own generation before a retry.
- **No watcher meant no stability guard.** With no PRIME watcher (no registered root could be
  watched), prepare and commit skipped the generation check and authorized. 1.9.0 refuses
  MEASUREMENT_ABSENT.
- **Partial watch coverage was invisible.** A watcher watching none of the registered roots
  still authorized. 1.9.0 compares the registered roots with the roots actually watched and
  refuses WATCH_INCOMPLETE.
- **A missing declared manifest was silently re-captured as "tested".** With write access to
  the store, delete a candidate's declared manifests after its evaluation, edit its payload and
  restate the row's delta: prepare captured whatever the payload held, treated it as the bytes
  the evidence covered, and committed the edited bytes. 1.9.0 leaves the tested root absent:
  STAGED_UNTESTED unless a staged evaluation covers the staged bytes.
- **A staged PASS was trusted for bytes it never named.** After a staged-merge evaluation
  passed, prepare set the tested root to the staged root, whatever that evaluation had
  examined. 1.9.0 keeps the tested root as what the candidate's evidence examined; the kernel
  accepts the staged bytes only if the staged evaluation ran the current requirement with a
  complete roster and the declared verifiers over exactly those bytes.
- **A symlink retargeted in PRIME went live unevaluated.** Content roots, the identity of what
  an evaluation examined, left out symlink targets (the field was misnamed since 1.3.0). With
  PRIME's `shared.txt -> v1.txt` retargeted to `v2.txt` after a candidate was evaluated, the
  staged tree looked tested and was committed. 1.9.0 includes the target: STAGED_UNTESTED
  unless a staged evaluation covers it. Found by the adversarial review of this release.

### Changed

- The owner pair is retired: it was one computed value passed to both sides, so it constrained
  nothing. An evidence-subject pair replaces it, produced from the promotion's own arguments on
  one side and from the speaking evaluation's binding (or the return vehicle's mission hash) on
  the other. The Python "belongs to a different world" check no longer decides promotion; the
  structural and hash checks of a validation context stay.
- The staged-root comparison at commit is the kernel's (STAGED_ROOT_MISMATCH with a DENIED
  record); the Python pre-check is gone. At prepare the staged root is one observation and
  equality is a commit obligation.
- Commit refuses a prepared record written by an earlier runtime (TRANSACTION_RECORD_LEGACY),
  and treats a record that does not state that conflicts were measured as unmeasured.
- A conflicted merge records no staged root: null in the transaction record, the literal
  `"absent"` in the store, never a zero digest.
- Revalidation records the content root it examined before any check runs, and refuses
  REVALIDATION_INPUT_CHANGED if the tree moved while the checks ran. The checks run over the
  world's declared manifests materialized into a daemon-owned scratch tree (verified entry for
  entry, PAYLOAD_INTEGRITY_FAILED otherwise), not over the read-only payload, so what they
  examine -- bytes, modes, attributes -- is exactly what promotion compares with the staged
  tree, and a revalidated world's own evidence covers its collapse when PRIME has not moved.
  Each revalidation now copies the payload once.
- A recovery that finishes an exchange the daemon did not live to record publishes PRIME from
  the staged tree prepare recorded (kept beside the transaction by 1.9.0), not from a capture of
  live PRIME, when live PRIME no longer has the staged root. A write made while no daemon ran is
  recorded (`unaccounted-write`) and reconciled into its own generation, instead of being folded
  into the collapse. A transaction prepared by an earlier release has no such record; its
  recovery still uses the live capture, and records the difference the same way.
- Recovery replay is idempotent over the read-only records it copied the first time (1.8.0 and
  earlier stopped the daemon from starting with PermissionError). An exchange that renamed but
  failed afterwards (a directory fsync, or finishing itself) is no longer recorded ABORTED while
  its bytes are live: the running daemon finishes it in place and reports
  COMMIT_DURABILITY_UNCERTAIN (committed and recorded, but the exchange could not be made
  durable) after running the steps that follow any commit (a return's services, ghosts), and
  if finishing fails too it quarantines the transaction. A quarantine refuses
  RECOVERY_INCOMPLETE for prepare, commit, the PRIME freeze behind fork and return, reconcile,
  and root add and remove, until a restart's recovery settles it; the settled quarantine's
  status report is cleared. Recovery quarantines any error rather than stopping the daemon, and
  logs it with its traceback (RECOVERY_IO_FAILED for storage and SQLite operational errors,
  RECOVERY_FAILED otherwise), and a taken PRIME identity by name (CHECKPOINT_IDENTITY_TAKEN).
  The watcher is re-pointed after every commit attempt; if it cannot be rebuilt, PRIME is left
  unwatched (which refuses) rather than watched by a closed watcher, and the failure never
  replaces the commit's own error. With automatic ghosts enabled, a successful commit whose
  rebuild fails is still reported as an error (see Known limitations).
- Materialized revalidation inputs left by a killed daemon are removed at the next start.
- `prepare` and `fork` drain the watcher before deciding whether to reconcile, so a write the
  watcher had already seen is reconciled rather than refused as unaccounted.
- The watcher watches each directory before listing it, reports a root whose tree it could not
  watch completely, and drops a root directory that was moved (IN_MOVE_SELF) instead of
  following the old inode; a stopped reader thread leaves nothing reported as watched.
- WORLDLINE's own agent and protected-paths records are declared by origin with no profile;
  policy checks match only on an explicitly recorded profile.
- `doctor` gains `promotionReadiness` (read-only): pending transactions, watch coverage, the
  VALID-world census, and with `--refresh` the foreign-write measurement.
- A kernel refusal at commit, including EVIDENCE_STALE and PRIME_CHANGED_DURING_CAPTURE,
  carries `details.decision`, `details.transactionId`, `details.absentInputs` and
  `details.foreignWrites`.
- `doctor --refresh` reports a live capture it cannot take as an UNMEASURED foreign-write
  measurement instead of failing, and the census leaves out PRIME and WORLDLINE's own
  generations.

### Proof and ABI

- **Proof.** 251 checks proved, none justified, no `pragma Assume`; the floor rises from 156 to
  251. `Worldline.Collapse_Wire.Decode` and `Decide_Wire` join the required proved subprograms.
  The floor counts checks, and GNATprove counts a whole postcondition as one, so the contracts
  themselves are now pinned: `verify_proof_manifest.py` holds a digest of each contract
  specification (collapse, collapse wire, identities, evaluation, transitions), of the types
  they rest on (`worldline.ads`, `attest.ads`, `attest-sha256.ads`), of the C export table
  (`worldline-c_api.ads`), of the whole unproved C boundary body (`worldline-c_api.adb`) and of
  the five project files that decide which file is compiled as each unit; checks that
  `wl_collapse_decide` is bound exactly once and to `Collapse_Decide`; refuses any Ada source
  under `core/` outside the pinned set; and refuses a change to any pinned text that does not
  update its pin deliberately. The gate checks the pins before it writes the manifest. Pins
  cover text: a body the proof covers (such as `worldline-collapse.adb`) is guarded by the proof
  instead.
  `Decide`'s postcondition states that `Authorized` is exactly `All_Hold`, that nothing absent
  or unmeasured is authorized, that OWNER_MISMATCH is never returned, and for every refusal
  that what it names is actually the case. `Decide_Wire`'s postcondition states that a
  malformed request is 255 and a well-formed one is exactly `Decide` of its decoding.
- **ABI generation 5.** `wl_collapse_request` is a fresh all-`uint8_t` layout with no padding
  or reserved bytes: seven scalar bytes, 25 optional hashes (`wl_optional_hash`) and two
  optional counters (`wl_optional_counter`). `wl_layout_size` and `wl_layout_offset` report the
  new record (selector 0) and the two optional records (selectors 4 and 5) by field name.
- The kernel tests cover every decision code, each required identity absent on one side and on
  both, both phases, the staged-evidence cases and the checkpoint cases. A 20000-iteration fuzz
  run draws every pair (the watch sets and each staged value included) independently, compares
  `Decide` with an independent oracle, checks every refusal's reason against the oracle's own
  restatement, and requires every decision but OWNER_MISMATCH to occur. The wire tests cover a
  null request, each class of malformed encoding, each ignored slot on its own, and multi-byte
  counters.
- **Not measured** (stated, not hidden): ownership (uid/gid) is not part of a manifest, so a
  `chown` or `chgrp` in live PRIME is not a foreign write; a write in the moment between the
  last generation read and the exchange is attributed to the exchange.

### Known limitations (pre-existing, refuse safely; scheduled, not fixed in this release)

These were found by the adversarial review of this release. Each predates 1.9.0 and each
refuses rather than authorizes, so under the release's freeze rule they are stated here and
fixed in a later release rather than changed after review began.

- A read-only directory in PRIME (mode 0555 with contents) makes every collapse prepare fail
  with STORAGE_ERROR: the merge creates staged directories with their final mode before filling
  them. Present since 1.0.0.
- A declined `return` cannot be retried at the same PRIME (WORLD_CONFLICT), and each attempt
  leaves a frozen generation and a vehicle payload; its leftover vehicle also makes a later
  collapse of that world refuse CHECKPOINT_IDENTITY_TAKEN until PRIME moves.
- A hard-link group whose files carry extended attributes and a read-only mode cannot be
  materialized (XATTR_NOT_APPLICABLE): fork, prepare and revalidation refuse such a tree.
- Revalidation copies the payload once per run and needs free space for it; the copy is not
  under resource admission.

One more was found by the last review round, in this release's own repair of the watcher
rebuild. It also refuses rather than authorizes, and it is stated here so the freeze ends:

- With automatic ghosts enabled, a collapse or return that commits but whose watcher rebuild
  then fails (`inotify_init1` refused: EMFILE or ENOMEM) is answered PRIME_WATCH_UNAVAILABLE,
  "no registered root could be watched", although PRIME moved and the receipt was written. The
  ghost freeze that follows every commit refuses with no watcher, and its error replaces the
  commit's result. Check `worldline status` or the receipt before retrying; a retry of the same
  transaction is refused INVALID_TRANSACTION_STATE. That PRIME generation gets no automatic
  ghosts. In 1.8.0 the same rebuild failure replaced the result with INOTIFY_UNAVAILABLE. With
  ghosts disabled the commit's result is reported.

## 1.8.0 — 2026-09-29 · evaluation lifecycle authority

**The proved core now decides whether a world's evaluation can promote it, and four ways to
promote without a passing evaluation are closed.** The SPARK unit `Worldline.Evaluation`
classifies every check record, admits or refuses each one, and judges the whole roster. Python
maps observed fields to the kernel's categories and records the answers. The design and the
requirements-to-contract table are in `docs/phase1-evaluation-lifecycle.md`.

### Upgrading

- **A project with no `.worldline.json` can no longer collapse.** Add a policy that declares
  its checks. This minimal file explicitly declares that nothing is required:
  `{"schemaVersion": 1, "generated": [], "checks": [], "services": []}`. Test harnesses and
  health checks that collapse in a throwaway root need one too.
- Revalidate VALID worlds before collapse, as after any release. No store migration is needed.
- Two kinds of world are no longer return points. Returning to either is now refused with
  CHECKPOINT_UNWITNESSED:
  - A PRIME from before the last root was removed. Removing the last root starts a new lineage.
  - A COLLAPSED `return-*` world whose commit published a new generation. Return to that
    `prime-*` generation instead.

### Security: promotion without a passing evaluation (every deployment)

Each defect below was reproduced on 1.7.3 before it was fixed. The 1.8.0 side is tested end to
end in `tests/test_evaluation_lifecycle_promotion.py`.

- **`return` re-applied a world whose required check failed.** A required check COMPLETED with
  FAIL, so the world was DEGRADED. When a sibling collapsed, the world was ARCHIVED, and
  `return <world>` then authorized it and committed its bytes as PRIME. The promotion boundary
  asked only whether execution had reached the examiner, not whether the check passed. It now
  recomputes every required check from its raw record against the current policy's
  declaration. The kernel admits a check only when it completed, passed, and has complete
  evidence.
- **`return` re-applied a world whose agent failed.** The agent's own exit is on every
  finalization roster, and revalidation never re-runs it. A world DEGRADED only because its
  agent failed, then ARCHIVED, was authorized and committed. The promotion roster now includes
  the agent's exit, judged from the finalization record. The review of the first 1.8.0
  candidate found this.
- **A refused `return` left a world that could be returned to with no evidence.** `return X`
  creates a synthetic candidate before it decides. When the decision was a refusal, that
  candidate stayed VALID with the actor `worldline`. After any later PRIME change,
  `return <that world>` took the checkpoint path, which consulted no evidence. The result:
  - a world whose evidence had just been refused as stale was promoted;
  - the newer policy was reverted along with it.

  Checkpoint return is now an explicit mode of the kernel's collapse decision, and it needs a
  witness that the subject was once PRIME. A world that never became PRIME has no witness, so
  it is refused with CHECKPOINT_UNWITNESSED.
- **An empty roster counted as complete.** A project with no policy collapsed with its roster
  reported complete, because a loop over nothing found nothing wrong. The kernel's
  `Roster_Complete` treats an empty roster as complete only when a policy declared it.

### Changed

- Evidence presence is now a set of typed facts (`evaluation.evidencePresence`) rather than
  "the record is non-empty":
  - the record names its check;
  - a verdict is recorded;
  - the examiner binding holds;
  - the format and evaluator profile are the ones the policy declares for that check;
  - a declared verifier bundle names what executed.
- A Boolean `exitCode` is not an exit status. An empty or malformed `executedVerifierSet` is
  present and unverifiable, not absent.
- `protected-paths` is on the promotion roster whenever the policy protects anything, as it
  already was at finalization and revalidation.
- The adapter names `worldline` and `system` are refused in `agentCommands`. The check ids
  `agent` and `protected-paths` are refused in policies.
- A system future (`simulate`) cannot be the subject of `return`. Its results carry the
  kernel's classification, which admits none of them.
- Unchanged, deliberately: a PASS from an examiner whose staged bundle has unsatisfied imports
  is still a completed pass. The import analysis cannot tell a missing helper from the module
  under test. A FAIL with such a gap is EVALUATOR_INCOMPLETE. This was already so for
  supervised checks. It is new for an agent-origin record, where it is inadmissible either way.
- The agent record of a world forked by 1.3.0–1.4.x carries no `origin`. It is recognised by the
  exact shape the runner wrote, so revalidated worlds of that age stay promotable. A world
  forked before 1.3.0 has an agent record with no supervision at all: nothing observed its
  agent's exit, so it cannot be promoted, even after revalidation. Return to a PRIME generation
  instead, or fork again.

### Proof and ABI

- **Proof.** 156 checks proved, none justified, no `pragma Assume`; the floor rises from 130 to
  156. The postconditions state:
  - the whole lifecycle relation;
  - the exact admission predicate and roster rule;
  - the two collapse modes;
  - for `Classify`: what may complete, that an outcome is the recorded verdict, and the named
    refusals.
- **Coverage.** `proof-manifest.json` records per-subprogram coverage. The gate fails closed
  on any summary line that is not a proved subprogram, including a skipped proof, a skipped
  flow analysis or an unknown format. It also fails on any GNATprove annotation in the source.
  The floor and the required subprograms are pinned in `verify_proof_manifest.py`, which
  refuses a manifest that shrinks them. Assurance compares the coverage of a fresh run with the
  committed one.
- **ABI generation 4** (1.7.3 was collapse request layout 2):
  - The collapse request gains an evaluation mode and a checkpoint witness.
  - New exports: `wl_evaluation_classify`, `wl_evaluation_admissible` (typed evidence
    presence), `wl_evaluation_transition_allowed`, `wl_evaluation_advance`,
    `wl_evaluation_roster_complete`, `wl_abi_version`, `wl_layout_size` and `wl_layout_offset`
    (each field's offset, by name).
  - At load, the runtime refuses a library of another generation, or one whose record sizes or
    named field offsets differ from its own.
- **Invalid requests.** The C layer rejects:
  - every Boolean byte other than 0 or 1;
  - every nonzero reserved byte;
  - every classification `Classify` could not have produced: an outcome without completion,
    completion without an outcome, or an in-flight state.
- **Header checks.** A test compiles the header and compares every field offset and every code
  table with the runtime.

## 1.7.3 — 2026-09-29 · deployment guidance corrected

**Found by the rehearsal of the dedicated-account migration from the 1.7.2 release artifact.**
No code path changes; no store migration is needed.

### Fixed

- **`RestrictSUIDSGID=` is no longer recommended; it breaks every sandbox.** 1.7.0 to 1.7.2
  asked dedicated deployments to set it on the unit and on the account's user manager. Its
  seccomp filter answers `openat2` with ENOSYS (the flags live in a struct it cannot inspect),
  and bubblewrap 0.13 does not fall back: in the rehearsal, repository inspection refused
  `GIT_SANDBOX_UNAVAILABLE` ("Can't open source /usr: Function not implemented"), `simulate`
  refused `SIMULATION_FAILED`, and the doctor reported the sandbox `UNAVAILABLE`. Removing it
  restored all three (demonstrated with a transient unit with and without the setting). Setuid
  content stays covered by the content check (setuid and setgid bits refuse in anything a
  client can reach) and by the `nosuid` store mount.
- **The store's `nosuid` mount belongs outside the system roots `simulate` overlays** (`/usr`,
  `/etc`, `/var`, `/opt`, `/boot`), for example `/srv/<account>`. The kernel refuses an
  unprivileged overlay layer that has a mount beneath it, so a self-bind of `/var/lib/<account>`
  made `/var` unusable as a layer and `simulate` failed ("Can't make overlay mount … Invalid
  argument") for every account on the host; demonstrated by removing the mount in a private
  namespace, which restored the overlay. With the store under `/srv`, the rehearsal's exercise
  passed 22 of 22.

## 1.7.2 — 2026-09-29 · relocating stores with payload-less worlds

**Found by the rehearsal of the dedicated-account migration from the 1.7.1 release artifact, on
a consistent copy of a production store.** No store migration is needed. Existing VALID worlds
need revalidation before collapse, as after any release: the runtime changed.

### Fixed

- **`worldline-relocate` relocates a store that holds worlds without a payload.** The production
  store under rehearsal had six retained worlds with no payload directory: two DEAD forks that
  died before a payload existed, and four DEGRADED worlds whose payloads that store had itself
  lost at some point (they have identities). 1.7.1's dry run said nothing about them, and its
  real run rewrote the copy and then refused in verification ("retained world payloads are
  missing from the new store"), so such a store could not be relocated at all.
  - While planning, before anything is written, the relocation measures which retained worlds'
    payloads are absent from the copy. The relocation cannot lose what the old store does not
    have, so such a payload is exempt only on positive evidence that the old store lacks it too,
    and the basis is reported for each (`payloadsAbsentBeforeRelocation`): seen absent in the
    old store (`absent-in-old-store`), which counts only when the old store is present at its
    recorded path and is this store (its generations, a live link for each root its database
    records, at least one payload its database records seen present, and a record of this world
    at this path) and the path is walked without following a link to a component that does not
    exist; or attested absent by a caller who can see the
    old store when the relocating account cannot (`attested-absent-in-old-store`, from
    `--absent-in-old-store FILE`, a JSON list of instance ids; `-` reads it from standard
    input, as a pipe from the operator delivers it). Each entry says whether the old store could be checked; the report counts the
    attestation's ids, how many were used, lists unused ones and gives its SHA-256; a world
    that cannot be exempted says why (the old store is not there, is not this store, cannot be
    read, or does not record the world at that path). Verification
    does not require exempt payloads, and its verdict then reads
    `PRESENT_EXCEPT_ABSENT_FROM_OLD_STORE`. The old store's database is opened immutable, so it is
    never written.
  - Any other missing payload is a lost or incomplete copy: it is reported
    (`payloadsMissingFromCopy`, with the reason) and the real run refuses before writing
    anything. Neither world state nor a missing identity is evidence. The candidates of this
    release got this wrong three times: `24b511d` exempted every absent payload (a VALID
    world's payload missing from the copy only was relocated and reported present); `3416f89`
    decided by state (a payload-less DEAD world is archived when a sibling collapses and then
    refused the whole store); `ac9f621` took a world without an identity as never created
    (finalization writes the payload before the identity, so such a world may still have one)
    and a missing path as seen absent even when the old store was not there at all.
  - A rerun on a copy whose rows were already rewritten exempts nothing, since a payload lost by
    the first run would otherwise read as absent: re-stage a fresh copy instead.
  - A payload that disappears after planning still refuses in verification.
  - Reports list the first 50 worlds of each kind and count them all.
  - A store that predates `payload_pruned` (schema 1) is read, not refused with an
    `OperationalError`.

### Known limits

- An attestation is trusted as given: a caller who attests that the old store lacks a payload it
  has makes the relocation accept that payload's absence from the copy. Proving the copy complete
  remains the migration's, as before.
- The old store's database is read immutable: rows or updates still only in its WAL (a running
  daemon's) are not seen. A world found only there is not evidence, so its missing payload
  refuses; a stale path is compared as recorded.
- A world whose payload its own store lost stays recorded with its state; the relocation carries
  it as it is.

## 1.7.1 — 2026-09-29 · review and rehearsal hardening

**An independent review of 1.7.0 (commit ad64cd2) and a rehearsal of the dedicated-account
migration on a copy of a production store found the defects below; eight more independent
reviews, of the 1.7.1 candidates 796cb02, 4490013, 09f5c0b, c7d89f1, 300543c, 8ff1903, f50bbb1
and 0fa069c, found more, including defects the candidates' own fixes introduced; the last four
found nothing of major severity.
Each is fixed and tested, except those named under Known limits, and each new test was run
against the code it guards against and failed there.** No store migration is needed. Existing VALID worlds need revalidation before collapse, as
after any release: the runtime changed.

### Security: repository inspection

- **Nothing outside the inspected root is bound into the git sandbox.**
  - 1.7.0 bound a linked worktree's git directories, found from the root's `.git` file. That
    file is content a candidate controls. A `.git` file naming another world's or PRIME's
    repository put that repository's committed content into a world's recorded facts.
  - A repository root must now be a repository's top-level directory, with `.git` a real
    directory inside it. A linked worktree, a `.git` link and a subdirectory of a repository
    refuse by name: `GIT_LINKED_WORKTREE_UNSUPPORTED` or `NOT_A_GIT_ROOT`. Register the main
    checkout, or the directory with `--kind filesystem`.
  - **Upgrade note:** a root registered in one of those layouts now refuses captures.
    `worldline doctor` shows it as `BROKEN` under `rootIntegrity`, with the code. `root remove`
    still works, for any number of such roots: it records no repository facts for the root it
    removes, copies its bytes, `.git` included, and recreates a top-level `.git` link as it is
    even when it leaves the root; the other roots in such a layout are captured the same way while
    it publishes what remains (the candidates refused the link as `EXTERNAL_SYMLINK`, then each
    removal was refused by the other roots' captures).
- **`root remove` refuses before it changes anything.** It captures the remaining roots and runs
  the client-content check on that capture first, and re-reads the root it removes just before
  the swap (`ROOT_CHANGED_DURING_REMOVAL` if anything was written into it meanwhile, which used to
  be dropped). A refusal there (a FIFO, a hard link to outside, unsafe content, a write) leaves
  every root, the primary flag and the operator's path as they were. It used to swap the path
  first, and its rollback then re-added the primary root while another was primary, left it
  half-removed, and kept a full copy beside the path (fourth review; 1.7.0 too). A refusal after
  the swap now re-adds the root before making it primary and always moves the path back; the
  copy that stood at the path is removed only if it is exactly what was materialized, and kept as
  `.worldline-removal-kept-<id>` otherwise, and the prepared generation is removed unless it became
  PRIME (fifth review); where it was kept, the refusal says so in its message and as `keptAt`,
  and a failure that is not a refusal (a full disk) that kept it is reported as
  `ROOT_REMOVAL_ROLLED_BACK` (sixth and seventh reviews). Other roots are captured without
  repository facts only when their layout is what the sandbox cannot inspect; a repository
  refused for its content (`core.bare`, a bad line in its `.git/config`) still refuses, and any
  refusal of another root, whatever refused it (git, a FIFO, a hard link), names that root by its
  path in the message and as `root` (sixth and seventh reviews). The root being removed needs no
  repository facts, since removal copies its bytes and compares them on both reads with the same
  facts: a git refusal of its own repository, or a missing sandbox tool, no longer refuses its
  removal (sixth and seventh reviews). A write that lands after the re-read and before the swap is not caught (Known
  limits).
  - The doctor also names a repository that borrows objects from outside itself
    (`objects/info/alternates`, `GIT_ALTERNATES_OUTSIDE_ROOT`), which the sandbox cannot read.
    It reads that file without following links and judges each entry lexically, so nothing the
    repository names is looked up on the host.
- **The index is read at a fixed path, once.** 1.7.0 took the index path from git's own output
  about the repository and read the file twice, once to hash it and once to copy it. It is now
  `<root>/.git/index`, opened through one descriptor that refuses links at every step. The bytes
  that are hashed are the bytes that are copied.
- **Whether the sandbox started is bubblewrap's to say, not git's stderr.** bubblewrap reports
  the child's exit code (`--json-status-fd`) only when the sandbox set up and ran it. Without that
  report, inspection refuses with `GIT_SANDBOX_UNAVAILABLE`; in 1.7.0 a launch failure during
  `rev-parse --verify HEAD` recorded `head: null` for a repository that has a HEAD. With it, git's
  exit code stands whatever git's stderr says: in the first candidate, a repository filter that
  printed `bwrap:` made a working sandbox refuse. bubblewrap's own exec-failure report (exit 1,
  `bwrap: execvp`) still refuses, and git must resolve inside the directories the sandbox binds.
- **The task limit cannot be escaped, and the unit bounds memory, swap and tasks.**
  - The sandbox has no nested user namespace (`--disable-userns`) and no capabilities. A nested
    namespace would have started a fresh `RLIMIT_NPROC` count.
  - The allowance is 2048 tasks beyond the uid's current count, taken once per capture instead
    of once per git call. With 512, a burst of threads under the same uid could refuse an
    ordinary capture (reasoned in the review); such a refusal is now `GIT_SANDBOX_UNAVAILABLE`.
  - Inspection runs in the daemon's own cgroup, with OOM score 1000, so under memory pressure the
    kernel prefers to kill inspection; code a repository makes git run can lower that score again
    toward the unit's floor. The shipped unit sets `OOMPolicy=continue`, so an OOM kill inside its
    cgroup no longer stops the whole daemon (systemd's default `stop` did); if the daemon itself is
    killed, `Restart=` brings it back.
  - The shipped `worldlined.service` sets `MemoryMax=4G`, `MemorySwapMax=0` and `TasksMax=4096`.
    `memory.max` does not cover swap. 1.7.0's notes relied on a memory bound the shipped unit did
    not set.
  - A task limit reached when the sandbox is created refuses as `GIT_SANDBOX_UNAVAILABLE`, as does
    a sandbox launcher killed by a signal. Inside a started sandbox, git killed by any signal, a
    process git started that was killed (git's own `died of signal <n>` report at the end of a
    line, or its `external filter '<command>' failed <n>` above 128 for the signals it does not
    name, such as SIGPIPE; whether git then exits 128, or exits 0 after retrying another way, as
    `submodule status` retries `describe` and a filter falls back to the unfiltered file: sixth
    review; seventh review: an unanchored match was set off by a warning quoting a file named like
    one; eighth and ninth reviews: the report may follow quotes, a filter's partial output or a
    newline in a `%f` file name), and a submodule listing refused for want of resources (a fork
    git could not get),
    refuse as `GIT_INSPECTION_FAILED`, or `GIT_UNAVAILABLE` at the 15 s timeout. A git killed after launch was
    read by `rev-parse --verify HEAD` as "no HEAD", and a failed submodule listing as "no
    submodules" (third and fourth reviews).
  - A submodule listing that git itself refuses (a gitlink with no `.gitmodules` mapping, which
    `git add -A` over a nested checkout makes) is recorded as `submoduleListing: UNREADABLE` with
    git's reason, not as "no submodules", and does not refuse the capture: refusing it, as the
    fourth candidate did, made an ordinary repository uncapturable and every root in its store
    unremovable (fifth review).
- **`worldline doctor` probes the sandbox, not only git.** The `git` capability is
  `UNAVAILABLE`, with the reason, when bubblewrap, `prlimit` or `choom` is missing or the sandbox
  cannot start, for example with a git installed outside the system directories the sandbox binds.

### Client mode

- **A refused registration keeps the operator's directory.** The first 1.7.1 candidate deleted a
  refused generation, and registration's generation holds the operator's own directory, moved in:
  a client-mode `init` or `root add` whose content the check refused deleted it (second review,
  blocker, demonstrated). Only reconcile and remove, which publish fresh copies, discard what was
  refused; registration moves the directory back, and a generation that still holds a root being
  registered is kept, never deleted. A move is recorded the moment it happens, so a failure
  after it (a directory flush on a parent the account may write but not read) moves the
  directory back too; before, that case deleted it, in 1.7.0 as well (third review). A
  registration refusal no longer closes the gate: live content is not what was refused.
- **Group-write is allowed only in the daemon's own group.** 1.7.0 refused a group-write bit
  only on entries of the client group. A migration that changed only the owner keeps the
  operator's group, and the operator is a client, so that content was client-writable and passed
  the start check. Any group other than the daemon's own now refuses
  (`CLIENT_MODE_UNSAFE_CONTENT`). A named member of the client group who is also in the daemon's
  group refuses at startup (`INVALID_CLIENT_MODE`), and so does a data directory that is not
  apart from the state and config directories (the data directory is the gate and is moded for
  clients; state and config stay 0700 and may share a directory: sixth review, the candidate
  refused that too).
- **Extended ACLs and file capabilities refuse.** Manifests record xattrs and materialization
  re-applies them. A `u:<client>:rwx` entry grants write while the mode bits show only its mask;
  any `system.*acl*` xattr counts, not only the two POSIX names. A `security.capability` xattr
  grants its capabilities to whoever executes the file. An entry whose xattrs cannot be read
  refuses instead of reading as none. Materializing an xattr this account may not set refuses
  with `XATTR_NOT_APPLICABLE` instead of an unnamed `PermissionError`.
- **One daemon per store, decided before anything is opened.** `worldlined` takes a lock in the
  store's state directory before it validates its configuration or builds anything, then the
  daemon's older lock in the runtime directory, and only then closes the gate. A second start
  used to close a running daemon's gate before its lock refused it, and to write the database
  first. The gate closes when a start refuses after taking the store lock, when the
  configuration refuses (it is validated after the lock), when the lock cannot be taken or
  written and the start can see that no process holds it (a lock path that is not a regular
  file, a state path that is not a real directory of the daemon's, a full disk), and when a
  daemon fails in Python after the lock. A
  lock some process holds is a running daemon's, and its gate is left alone; whether one is held
  is read from the kernel's lock table, so a running daemon's lock that its owner made unreadable
  still counts (sixth review), and where the start cannot tell (the lock is not in the table as it
  sees it, from another pid namespace or on a filesystem whose table identities differ from
  `stat`'s, and it cannot be opened; or the state directory cannot be searched; or any error but
  "missing" answers) it is taken as held, whether or not a process holds it, and the gate is left
  as a clean stop leaves it; the start logs that it left the gate (seventh and eighth reviews). A lock reached through a
  state directory that is itself a link counts for nothing (sixth review: another store's daemon
  kept this gate open). What the gate does not cover is under Known limits. The lock is
  `worldline-store.lock` in the state directory; a lock path that is a directory, a link or a
  file hard-linked elsewhere refuses as `UNSAFE_STORE` before anything is written to it. The
  runtime directory is not enough on its own: systemd removes it with the unit, lock file
  included.
- **`live` holds mapping links only.** A copy that dereferenced links turned a mapping into a
  real directory, which the start check skipped and routing served. The start now refuses
  anything in `live` other than mapping links into a generation or transaction payload, and its
  marker; routing requires the same of `live/<key>` (`LIVE_MAPPING_BROKEN`).
- **The routing check compares the live directory by kernel identity.** Every component must
  exist and be searchable in the daemon's namespace. 1.7.0 used a lexical `realpath`, which
  skipped a component it could not see and popped the `..` after it, so a link the daemon cannot
  follow was reported as routing.
- **A refused reconcile or remove leaves no copy behind,** whether the content check refused it,
  the capture did (a FIFO, an external hard link, a git layout the sandbox cannot inspect), or
  publication did after the copy was made (sixth review). Before, each refused `status` request
  left another full copy of the roots.
- **A registration checks client-mode content before anything moves.** The check after the move
  stays; a registration killed between its database commit and that check left content that every
  later client-mode start refused (sixth review; 1.7.0 too).
- **`worldline doctor` reports client mode** (`clientMode`): the client group and uids; the gate
  as `OPEN`, `CLOSED` or `UNSAFE` with the mode, group and ACL it found; and the host facts the
  daemon can observe, each `OK`, `MISSING` or `UNKNOWN`: `fs.protected_hardlinks`, a `nosuid`
  store mount, and the unit's memory, swap and task limits. The mount is read from the host's
  mount table (PID 1's), which is what clients use, by walking the mount tree so a covered mount
  is not taken for the one in use: in a unit with `NoNewPrivileges=` and a mount namespace,
  systemd mounts everything `nosuid`, so the daemon's own view read `OK` over a suid-capable host
  mount. When PID 1 is not systemd (`PrivatePIDs=`, or a container whose init is something
  else) it is `UNKNOWN`; in a container whose init is systemd, "host" means the container's.
- **A world's recorded environment no longer lists `XDG_DATA_HOME`, `XDG_CONFIG_HOME`,
  `XDG_STATE_HOME` or `XDG_CACHE_HOME`.** Since 1.7.0 no sandbox passes them, and the record
  claimed they were passed. Docker containers no longer receive them either; they named host
  directories the container does not have.

### Relocation

- **The copy must be a copy.** A copy reached through a symlinked parent, a copy that overlaps
  the old store, a copy that is the old store under another name (a bind mount: same device and
  inode), a database file that is the old store's own, a mount anywhere inside the copy, and a
  file hard-linked to anything outside the copy each once had the relocation, or the relocated
  daemon, write the old store. Each now refuses. The old store's paths are resolved as far as the
  relocating account can see before they are looked up in the mount table: a store records the
  path its daemon was given, and under a symlinked home (`/home -> var/home`) a bind of the old
  store at the copy's path was relocated in place (sixth review, demonstrated). Mounts are found in the mount table: a bind
  mount on the same filesystem has the same device number, and the second candidate, comparing
  devices, still rewrote the old store through one (third review, demonstrated).
- **One user of the copy at a time.** A real run holds the copy's store lock, the one
  `worldlined` takes before it opens anything, and checks before writing and before reporting
  that the lock file was not replaced. Both runs first check, reading only, that the lock is free,
  so a daemon using the copy refuses the run before anything is written into it (sixth review: a
  canary file was written into the copy first). The first candidate's `--daemon-lock` did not keep a daemon
  out and is gone. Before the lock is written or the database opened: the mount table must show
  no mount inside the copy; no copy root may be on FUSE, a network filesystem or an idmapped
  mount; and no copy root may be, on the same device, the old store's location or overlap it as
  far as the mount table can relate them. These are read from the mount table alone, so they hold
  when the relocating account cannot see the old store, as in the dedicated-account migration
  (fifth review: a bind of the old store at the copy's path passed every other check there). When
  the account cannot resolve the old store's path at all (a link inside the operator's 0700 home,
  such as `~/.local/share` on another disk), a copy on a bind mount of a directory refuses as
  well, since it cannot be told from a view of the old store
  (seventh review, demonstrated); a btrfs subvolume mounted whole is not a bind (eighth and
  ninth reviews: every btrfs root read as one, and a subvolume name with a space still did). Where
  the account can neither see nor locate the old store (its path unsearchable or missing, as
  behind a tmpfs over the home), a copy named by the old store's own real path, or a view of it
  the mount table cannot relate, is caught by the ownership checks, not by these (ninth review: a
  missing path counted as hidden refused a moved store's copy on ostree's `/var`). The copy's lock must not be the old store's
  own file, and, where the old store is visible, a file made in each copy root must not appear in
  it. Processes holding the copy's database are found by device and inode from
  `/proc/<pid>/fdinfo` and that process's own mount table (mount ids differ between namespaces),
  without `stat` through their descriptors, which a hung FUSE mount would block, except on
  kernels whose fdinfo has no inode. The copy's own identity is read the same way, from its own
  fdinfo and mount table, as well as from `stat`: on btrfs, `stat` reports a subvolume's device
  and the mount table the filesystem's, and no holder ever matched (sixth review). The database
  files, `-journal` included, must be regular files of their own (sixth review: a FIFO named
  `-journal` hung the real run under the lock).
- **Links:** the daemon makes only the live and prepared mapping links. Any other link in the
  copy refuses, except inside content: a payload below its root, and anything inside a world's
  overlay (its upper layer, the agent's runtime snapshot, a check's frozen inputs). A link that
  resolves into the old store refuses wherever it is. A recorded location that exists in the copy
  must resolve inside the new store; this is checked while planning, before anything is written,
  and again in the verification, which also requires what the daemon does of each live mapping:
  a link into a generation or transaction payload.
- **Directories the account cannot read refuse,** except overlayfs work directories where the
  daemon makes them, `overlays/<world instance id>/<64-hex root key>/work/work` (0000 by design,
  holding only the kernel's transient state), which are counted. What they hold cannot be
  checked; an agent can make `work/work` in its own runtime or a check's, which the looser rules
  of the second and third candidates accepted. A file or link named like the database files is
  checked like any other unless it is a regular file.
- **Sockets, FIFOs and devices are skipped, and files are read in bounded chunks.** The
  rehearsal's relocation of a production copy crashed on a dead world's socket (`ENXIO`); a FIFO
  would have blocked it.
- **Records are kept byte for byte and counted (`recordColumnsKept`):** each world's evidence,
  which is hashed into the world's identity, and each revalidation record (`meta` rows
  `validation:*`). A private evaluator's check records where it ran, its sandbox command line and
  frozen inputs, under the old store; nothing reads a path back out of either. The production copy
  holds one such world, and 1.7.0 refused it. A mention in any other database column or row still
  refuses.
- **The report of PRIME content a client-mode daemon would refuse reads the copy.** Before the
  rewrite, the copy's live links still name the old store, and the first candidate followed them
  there. It now maps each link onto the new prefix, adds file capabilities and anything in `live`
  other than mapping links, and appears in the result of a real run too.
- Every error is reported as `RELOCATION_REFUSED` with its cause, including a corrupt database, a
  record that is not JSON and one nested too deeply to read, never a traceback. Transaction records must be regular files. The
  ownership report counts each entry once; 1.7.0 counted every directory twice.
- The relocation was rehearsed on a consistent copy of a production store with this release's
  code, run as the dedicated account: 6,255 location rows, 10 transaction records and 26
  mapping links planned; no refused file, column or row; no foreign-owned entry, mount or file
  linked outside; 73 overlay work directories counted; no PRIME content, read in the copy, that a
  client-mode daemon would refuse; one evidence record kept. One directory refused: an empty
  overlayfs probe (`wl-uidprobe-*/work/work`) left in production's data directory on 2026-09-20,
  which the migration's copy excludes.

### Fixed

- **Removing a tree never follows a link.** Prune, revalidation cleanup and verifier staging
  cleanup made every directory writable before removing it, by path, which followed links: an
  agent's upper layer with a link to PRIME's content, or to any directory the account owns, had
  prune set that directory to 0700 (second review, demonstrated). Every directory is now opened
  without following links and changed through its own descriptor.
- **`prune` never deletes outside the store, and records only what it removed.** Every directory
  a world owns is checked before any is removed: one that resolves outside the data directory (a
  link planted in a copy, or a relocated store's leftovers) is reported under `failures`, nothing
  of that world is removed, and it stays retained. A world nothing of which could be removed stays
  retained too (fourth review: it was recorded pruned with everything in place). A removal that
  fails part way records the world as pruned if its own payload is no longer whole, and the causal
  event names what was not removed. Whether it is pruned is decided from its own payload alone: a
  world whose payload is whole stays retained whatever else of it went, including when its
  overlay's removal also failed part way, and when its payload is another world's base and was
  therefore not offered (fifth and sixth reviews). A pruned world no longer counts as referring to
  a payload, so one it shared is reclaimed once no live world names it (sixth review: it was never
  reclaimed). A pruned world's overlay that is still there is offered again by the next prune.
- **A root holding a read-only directory can be copied again.** Materialization created each
  directory with its recorded mode, so a non-empty 0555 directory could not receive its entries
  and every fork, reconcile or removal of that root failed (1.7.0 too; third review). Directories
  are filled first and given their modes last.
- **A store path that exists as something other than a directory refuses as `UNSAFE_STORE`,**
  not a `FileExistsError` traceback.
- **A `package.json` that is not an object** (`[]`), **or whose declared dependencies cannot be
  recorded** (nested deeper than 64 levels, or holding a float, which canonical JSON refuses), is
  recorded as an unreadable dependency file instead of failing registration, reconcile and every
  capture of its root with an `AttributeError` (1.7.0 too; fifth review), a `RecursionError` or
  `NON_CANONICAL_JSON` (sixth and seventh reviews).
- **`status` reports any failure of its re-capture.** It reported refusals as a `DEGRADED` watch
  state, but a failure that was neither a refusal nor a storage error answered `INTERNAL_ERROR`
  on every request while the store stayed dirty; that is now `DEGRADED` too, with
  `RECAPTURE_FAILED` (seventh review). A storage failure is recorded the same way under its own
  name, `DISK_FULL` or `STORAGE_ERROR` with its errno (eighth and ninth reviews).
- **A publication that fails after recording its world keeps that world's payload,** in reconcile
  and in `root remove` alike. Both discard the fresh copy of a refused publication, but
  publication records the world before it moves PRIME; a failure in between (a full disk) had
  the discard delete a recorded world's payload (seventh and eighth reviews).
- **A daemon that resets the connection is `DAEMON_DISCONNECTED`,** not a `ConnectionResetError`
  traceback.

### Known limits

- A leftover the daemon's account cannot remove (a private evaluation's worker copies, owned by
  the account's subordinate uids, when the evaluation was killed before it reclaimed them) is
  reported by every prune and keeps `worldline-relocate` refusing the store until it is removed by
  hand. Directories a failed removal already made owner-accessible stay so.

- The gate closes on a failed start and when a daemon fails in Python, once the start has named
  its store. A daemon that stops cleanly, or is killed outright (SIGKILL, the OOM killer), leaves
  it as it was, and the next start closes it and checks again before opening it. A configuration
  whose store directories cannot be named (a relative `XDG_STATE_HOME`) refuses before the lock
  and leaves the gate as it was. A store lock that is a hard link of another store's held lock
  cannot be told from this store's own held lock, so a start refused on it leaves this gate alone
  (only the daemon account or root can make one).
- Daemons from earlier 1.7.1 candidates used other store-lock names and are not excluded by this
  one: stop them first, as for 1.7.0. Every `flock` error, not only "held" (`ENOLCK` too), reads
  as a lock in use; that refuses rather than risking a second daemon.
- The store lock is a file. Removing it while the daemon runs (only the daemon account or root
  can) lets a second daemon with another runtime directory start on the same store. The check
  that no process holds the lock and the closing of the gate are two steps; a daemon that starts
  in between can have its fresh gate closed. A start whose state path runs through a link above
  the state directory to another store's held lock refuses `DAEMON_ALREADY_RUNNING` and leaves
  this gate as a clean stop does.
- A registration's content check runs before the move and again after it. Content made unsafe
  in between, followed by a kill after the database commit, still leaves content every later
  client-mode start refuses; a `chmod` of the named entries by the daemon account repairs it.
- A publication that fails after recording its world but before moving PRIME leaves that world
  recorded, VALID and not PRIME: reconcile or removal refuses `NOT_FOUND` until live content
  changes (1.6.0 too), and prune never offers that world, so its generation stays until removed
  by hand. A relocation's dry run does not check that kept worlds' payloads exist; the real run
  finds out in its final verification, after rewriting the copy.
- `root remove` re-reads the root just before the swap. A write into the root after that re-read
  and before the swap is kept only in the store's previous payload, not at the operator's path:
  stop writers into a root before removing it. A rollback keeps a full copy beside the path
  whenever anything about the copy changed, its mtime included (an editor's temporary file).
- A process git starts that is killed by SIGPIPE, SIGINT or SIGQUIT and is not a filter leaves no
  report in git's output, so its effect cannot be told from a fact.
- A repository's content can make a submodule listing read like a resource failure (a gitlink at
  a path named `cannot fork`), or print a whole line that reads like git's report of a killed
  process; either refuses that repository's captures by name, and while it does, every operation
  that captures all roots refuses too, except removing that root. The doctor's `rootIntegrity`
  reports such a root as OK.
- The doctor does not report `OOMPolicy`, and the `git` capability's version is that of the git
  on the daemon's `PATH`; inspection always runs the one in `/usr/bin` or `/bin`.
- On btrfs, the relocation's holder check matches by the filesystem's device and the inode, so a
  file with the same inode number in another subvolume of the same filesystem, held open, refuses
  the relocation; the fix for btrfs is tested with a simulated `stat`, not on btrfs.
- When the relocating account cannot resolve the old store's path, a copy on any bind mount of a
  directory refuses, including an ostree system's `/var`; run the relocation where the old
  store's path resolves (for example by granting the account search on its parents for the run),
  or relocate before binding.
- Repository inspection runs the git in `/usr/bin` or `/bin`; a git installed elsewhere
  (`/usr/local/bin`) is refused by the doctor's probe and by every capture.
- `OOMPolicy=continue` is set by the shipped unit; a deployment that writes its own unit sets it
  itself (`SECURITY.md` limit 7).
- A 1.7.0 daemon holds only the runtime-directory lock. During an upgrade, a 1.7.1 start against
  a store that a 1.7.0 daemon still serves builds before the older lock refuses it: stop the old
  daemon first, as the installers do.

- Captures resolve registered root links on the daemon's event loop. A registered path under a
  mount that stops answering (a FUSE mount whose device went away) blocks the daemon until it
  answers. A dedicated unit with `ProtectHome=tmpfs` and a read-only bind of the project
  directory keeps other mounts in the home directory out of its view.
- The task allowance counts the uid's threads through `/proc` once per capture.
- Repository inspection binds `/etc` and `/usr` read-only, so a repository's filter can put their
  world-readable content into its own world's recorded facts; an agent can read them anyway.
- In a dedicated deployment, `fs.protected_hardlinks=1` joins the requirements WORLDLINE does
  not enforce. Without it a client can hard-link a PRIME file it can read into a directory of
  its own, and every capture of PRIME then refuses `EXTERNAL_HARDLINK` until the link is found.
  `worldline doctor` reports it. The client group and the daemon's group must be disjoint: named
  members are checked, but accounts whose primary group is the client group cannot be listed.
  `SECURITY.md` limit 7.

## 1.7.0 — 2026-09-28 · dedicated-account client mode

**The daemon can run as its own account, serve named client accounts, and be moved there.** The
store, PRIME's content and the policy that gates promotion no longer have to be the operator's to
write. Before this release, the daemon accepted only its own uid. It also resolved every managed
root through the operator's own link, so moving it to another account would have changed nothing
that mattered.

### Security: repository inspection could run commands on the host (every deployment)

- WORLDLINE inspects repository roots with `git status` and `git diff`, host-side and outside
  any sandbox. This happens at registration, at finalization of every world, at collapse prepare,
  and at every capture of PRIME.
- Earlier releases neutralized git's exec-capable settings with a `-c` denylist. No denylist can
  name a filter driver: a repository defines `filter.<any name>.clean` in its own config and
  applies it through `.gitattributes`.
- A world whose agent wrote such a configuration could therefore run commands as the daemon's
  account when the world was finalized. In a single-account install that is the operator, so the
  command ran outside the sandbox the world was meant to be confined to. An independent review of
  a 1.7.0 candidate demonstrated it.
- Every git process now runs in its own bubblewrap sandbox:
  - no network;
  - the system directories read-only, and a fresh `/tmp` of at most 256 MiB;
  - nothing of the host except the inspected root (read-only), a linked worktree's own git
    directories (read-only; found on the host from the root's `.git` file, and bound only when
    they are real directories holding a `HEAD`), and a private scratch directory;
  - at most 512 tasks beyond what the daemon's uid already has (`prlimit --nproc`), and the
    existing 15 s timeout. Memory is bounded by the daemon unit's own cgroup, not here.
- The index file git names is read on the host only when it lies inside the root or those git
  directories and is a regular file; a `.git/index` link elsewhere is treated as no index.
- Git behaves exactly as before, so the captured repository facts do not change. Anything a
  hostile configuration makes it run reaches nothing. The `-c` denylist stays as a second layer.
- `tests/test_security_hardening.py` arms a repository with a filter that lives inside it,
  proves on the host that it fires, proves through its marker in the captured diff that it ran
  inside the sandbox, and proves that it wrote nowhere the host can see.

### Managed roots resolve through the store (every deployment)

- The following once read a root through `realpath(<registered path>)`, a symlink in a directory
  the operator owns:
  - capture, reconcile, prepare, checkpoint, revalidation and validation;
  - `simulate`, `prune`, fork policy loading, service start and `why`.

  All of them now resolve the root's content through the store's own `live/<root key>`
  mapping. The registered path must still link to that mapping's `<root key>` entry, and the
  mapping must resolve inside the store. Anything else refuses with `LIVE_MAPPING_BROKEN`, the
  state the doctor already called `BROKEN`.
- The live directory is compared resolved. A HOME reached through a symlink, a doubled or
  trailing slash, or a relative link therefore still routes; a link straight to a payload
  does not.
- With one account this closed nothing new. With a dedicated daemon, a client that re-pointed
  its `~/Projects/<root>` link could have:
  - had its own directory captured as PRIME with no collapse;
  - had the gating policy loaded from it;
  - made `prune` treat PRIME's payload as unreferenced.

  An independent review demonstrated the first two.
- `why` refuses paths containing `..`, and reads only inside the root.
- `worldline doctor` reports a root `BROKEN` for exactly what captures refuse. Before, it could
  say `OK` for a root whose live mapping resolved outside the store.
- **Upgrade note:** a root whose registered path no longer links to its live mapping now refuses
  captures instead of silently adopting what is there. An interrupted `root remove` can leave
  such a root. `worldline doctor` lists it under `rootIntegrity`.

### Dedicated-account client mode

- It is opt-in, through the daemon's environment. Both variables are required, and any other
  combination refuses at startup with `INVALID_CLIENT_MODE`:
  - `WORLDLINE_CLIENT_GID`: exactly one group;
  - `WORLDLINE_CLIENT_UIDS`: at least one uid, distinct, in ASCII decimal digits only, never 0.

  The following also refuse with `INVALID_CLIENT_MODE`:
  - a runtime directory that overlaps data, state or config;
  - a client group the daemon account is not a member of;
  - a client uid whose primary group is the daemon's, or that is a member of it;
  - a HOME or XDG directory spelled through a symlink (masks and the gate are applied by path).

  Without the variables, nothing changes: owner-only, `0600`.
- With both set:
  - the runtime directory is `0750`, the socket `0660` (verified after bind) and
    `status.json` `0640`, all with the client group;
  - the daemon serves its own uid and the listed uids, and refuses every other peer with
    `PEER_UID_MISMATCH`.
- **Clients can read content on the way to PRIME, but can list or write no store directory.**
  - The directories from the store to PRIME's content are `0710` with the client group, so
    clients can traverse them but not list or write them. That path is:
    - data;
    - `live`;
    - `generations`, each generation and its payload;
    - `transactions`, and each transaction with its payload and mapping.
  - That also makes fork checkpoints, and the staged payloads of open transactions, reachable
    by name.
  - Manifests, state, worlds, overlays and config stay `0700`.
  - The data directory is the gate to all of it. It is created closed (`0700`) and opened
    (`0710`) only at daemon start, after the content check below. A store written before client
    mode is therefore readable at once, but nothing unchecked ever is.
  - Through daemon requests (`why`, `show`, `inspect`), clients see PRIME content whatever its
    modes.
- **Content a client can reach must be the daemon's and read-only to everyone else**
  (`CLIENT_MODE_UNSAFE_CONTENT`).
  - What is refused: an entry not owned by the daemon, any other-write bit, a group-write bit
    on an entry whose group is the client group, and any setuid, setgid or sticky bit. A
    group-write bit on an entry of the daemon's own group grants clients nothing, since a client
    in that group is refused, and umask-002 hosts put that bit on everything a world writes.
  - Where it is enforced: at collapse and return prepare (before a transaction exists), when a
    generation is published, and at daemon start (before the gate opens). A directory the daemon
    cannot read there refuses too. If publication finds live content unsafe while the daemon
    runs, the gate closes and every client loses reach into the store.
  - Why: manifests record modes and materialization re-applies them, so a candidate chooses the
    modes of what it stages. An independent review demonstrated a world that opened its root
    0777. It became PRIME, a write into it was adopted as a new PRIME with no transaction, and
    the policy file could be replaced the same way.
  - A client group equal to the daemon's primary group refuses with `INVALID_CLIENT_MODE`,
    because every file the daemon creates carries that group.
- **`init`, `root add`, `root remove` and `switch` belong to the daemon's own account.**
  - The root-set changes move directories between the operator and the store, which a
    dedicated account cannot do on a client's behalf.
  - `switch` drives the desktop and opens a terminal as the daemon.

  A listed client gets `OPERATION_NEEDS_DAEMON_ACCOUNT`. Every other
  operation is open to listed clients, and the daemon logs each mutating request with its
  requester's uid.
- **Every ordinary sandbox masks the daemon's HOME and its store.** This covers agents,
  legacy checks, services, `simulate`, `shell` and the materializers.
  - Before, only agent worlds masked the daemon's HOME. The others masked a fixed
    `/home/sicarii`, so a dedicated account's HOME was visible to candidate code.
  - A data, state, config or runtime directory that is under a system path (read-only bound,
    or overlaid by `simulate`) and outside that HOME gets its own tmpfs, by its configured
    spelling and by its resolved one.
  - `simulate`'s system overlays are now mounted before these masks. Mounted after them, as
    in an earlier candidate of this release, they covered the masks.
  - A HOME spelled through a symlink is masked where it really is.
  - The account's `XDG_*_HOME` variables are no longer passed in. They named directories inside
    the masked HOME, so tools used their HOME-relative defaults instead.
  - Before, a store under `/var/lib` would have been readable, anchor signing key included.
    The private evaluator's roles never see `/var`.
- The client checks the server's `SO_PEERCRED` before sending anything. It expects
  `WORLDLINE_DAEMON_UID` when that is set, and its own uid otherwise; anything else is refused
  with `DAEMON_PEER_UNEXPECTED`. In 1.6.0 the client checked nothing.
- A socket the caller cannot reach refuses with `DAEMON_ACCESS_DENIED`.
- `worldline shell` refuses from a client account with `SHELL_UNAVAILABLE_TO_CLIENT`.
- The CLI sends root paths for `init`, `root add` and `root remove` as absolute paths,
  because the daemon's working directory is not the caller's.

### Relocating a store: `worldline-relocate`

- A store records absolute paths to itself, so it cannot simply be moved. `worldline-relocate
  --from-data --from-state --to-data --to-state [--dry-run]` works on a stopped, quiescent copy
  already placed at the new location, and never writes the old copy. It refuses in these cases:
  - it is run as root;
  - the copy holds entries its account does not own;
  - a process it can see holds the copy's database open, compared by inode;
  - the copy's database is a symlink or has other hard links (a linked copy would rewrite the
    old store in place).

  It plans every rewrite and raises every planning refusal before it writes anything. A dry run
  plans against a private copy of the database, so it changes no byte of the store. It rewrites exactly the
  recorded locations:
  - six database location columns;
  - the transaction records;
  - the live and prepared mapping links.

  It then proves the result, after writing:
  - no database column or daemon-read file still names the old store;
  - the causal and receipt chains replay;
  - every mapping and retained payload resolves inside the new store.

  If that verification refuses, the copy is left rewritten and the old copy is still intact.
- Some mentions of the old path are kept byte for byte and only counted: user content, hashed
  records, agent output, the snapshots given to agents, and the single-account installer's
  `install-backups`. A mention anywhere else refuses.
- The report also names PRIME content a client-mode daemon would refuse at start, and counts
  directories it could not read (overlay work directories are `0000`), which it checks for
  ownership without descending into them.
- It ships in the release tree as `cli/worldline-relocate`. The installers do not put it on
  `PATH`.
- The operator's own root links are left for the migration to re-point.
- Tested end to end: a store with two collapses is relocated and served by a fresh daemon. It
  reports the same PRIME, the same chain verification and a working fork and collapse, and the
  old copy stays byte-identical.

### Fixed

- **Load-induced internal errors.**
  - A `docker info`, `docker ps` or `docker inspect` that outlives its window now refuses as
    `DOCKER_UNAVAILABLE`. Before, the uncaught `TimeoutExpired` failed finalization with
    `WORLDLINE_INTERNAL_ERROR`.
  - The private evaluator's bootstrap handshake window is 60 s instead of 15 s
    (`BOOTSTRAP_HANDSHAKE_SECONDS`), on both sides. Under a load average near 110, a bootstrap
    became ready after 19.86 s and was refused. It still fails closed at its deadline.
- **`worldlined` sets `umask 077` before it builds anything,** and the admission lock and ledger
  are created `0600` explicitly. Before, the build step created them before the daemon's own
  umask applied, so under a permissive unit umask they were `0644`. A client-group member could
  then have held the lock and stalled admission.
- **The self-capture guard compares resolved paths as well.** Before, a symlinked parent could
  walk a root into the store past the lexical check.
- **The client reads a refusal the daemon sent before closing.** A daemon refuses an unlisted
  peer and closes before reading anything; under load the client's send then failed with a
  broken pipe instead of reporting `PEER_UID_MISMATCH`, which was already in its receive buffer.
- **Every transient job unit sets `UMask=0022`.** What a world writes no longer depends on the
  host manager's umask. A hosted runner whose manager ran with a permissive umask made every
  agent-written file group-writable, which client mode then refused at collapse.

### Known limits

- Revalidation runs on the daemon's event loop, as before. A refused bootstrap now holds it for
  up to 60 s instead of 15 s.
- Receipts and causal events do not record which uid requested a change; the daemon's log does.
- In a dedicated deployment:
  - the daemon account needs search (`x`) permission on each directory above the registered
    root paths, to check that their links still route through the store;
  - job supervision needs the account's own systemd user manager (lingering), and the account
    must be a regular uid, not a system one. journald keeps a user journal only for regular uids,
    and supervision reads it; a system account's jobs would all be indeterminate;
  - clients need search permission on every directory above the data and runtime directories;
  - agents run with that account's credentials, and WORLDLINE does not provide any;
  - there is no supported way to add a root: the daemon cannot move the operator's
    directories, and clients may not ask;
  - the unit should set `RestrictSUIDSGID=yes` and a `MemoryMax=` (repository inspection runs
    inside the daemon's cgroup), and the store should sit on a `nosuid` mount.
  `SECURITY.md` limit 7.
- `simulate` runs a client's argv as the daemon account, in a sandbox that masks the store and
  HOME but shares the host network under `network.policy: shared`.
- Earlier PRIMEs' committed payloads stay readable by transaction id until `prune`.

## 1.6.0 — 2026-09-28 · stateful candidate leases

**Private examiners can now keep every candidate process out of the worker's identity, including
stateful harnesses that run many candidate commands against evolving state.** Earlier releases
gave `candidate.run` workers a separate identity from the examiner, but a verifier harness running
in a worker still started candidate subprocesses under its own worker identity.

### Candidate principal

- The private backend adds a third mapped identity. Examiners start candidate processes with
  `candidate.run_isolated` / `start_isolated` / `stream_isolated` / `wait_isolated` /
  `signal_isolated` / `teardown_isolated` as the candidate principal. These processes have no
  report, examiner-broker or worker-broker mount, and have their own PID namespace.
- Finalization accepts `candidate` role observations only with that principal's identity. It
  refuses any report in which a candidate observation shares a worker's UID or GID.

### Worker broker and scoped case leases

- A worker receives a worker-only broker socket, served only while a worker is active and only
  to that worker's mapped identity. A trusted harness in the worker can open a scoped case lease
  on a real directory strictly inside its copy of the candidate roots, as long as it does not
  overlap another lease.
- The backend copies the case into a separate candidate view and starts candidate commands
  there as the candidate principal. It accepts the normal argv/cwd validation, bounded stdin,
  and an allowlist of interpreter-determinism variables (`PYTHONHASHSEED`,
  `PYTHONDONTWRITEBYTECODE`). It provides stream, bounded blocking wait, SIGTERM/SIGKILL of the
  candidate's process group, and teardown.
- Candidate outputs are copied back only after every candidate handle of the case is torn
  down. Worker edits reach the candidate view only through an explicit copy-in guarded by the
  lease generation, and a side-effect-free `case_status` reports whether the worker view changed.
- Case copies accept only ordinary files, directories and symlinks whose lexical target stays in
  the case. They refuse hardlinks, special files, xattrs, special permission bits, nested mounts
  and observed mutation. Any protocol violation stops the broker and refuses the whole run.
- Every candidate start is recorded in the boundary evidence with its role observation and lease
  handle. Each lease records its open/copy/start/teardown/close events.

### Fixed

- The sandbox helper now reads exactly the three-byte role acknowledgement. Before, it could
  consume the first byte of candidate stdin written behind the acknowledgement on the same pipe.
- **Symlink targets that climb after a name are refused at capture and materialize
  (`EXTERNAL_SYMLINK`).** This escape has existed since the check was introduced. The check
  normalized targets lexically, but after `dirlink -> .` the kernel resolves
  `dirlink/../../outside` one level higher than normalization does. Repeating the pair reaches
  any path, so a world could carry a link that escapes its root into PRIME through an
  authorized collapse. Leading `..` that stay inside the root are unaffected.
  **Upgrade note:** a registered root that already contains such a link, even a harmless one
  like `a -> b/../c`, is refused at its next capture. Before upgrading, rewrite the link to
  its normalized form (`a -> c`). `find ROOT -type l` lists the candidates.
- The case copier applies the same rule to case trees (`CASE_COPY_LINK_ESCAPE`).
- A malformed principal label in boundary evidence (for example, a list) is refused instead of
  raising during finalization.
- A lease can be opened on a directory that the candidate input already contains. Before, the
  run was refused.

### Review, campaigns and documentation

- An independent review of the whole runtime delta since 1.5.0 found no critical or high
  issue. Its deferred items are low-severity and fail closed.
- A CodeRabbit review found the case copier's lexical symlink check, which led to the capture
  fix above, plus the malformed-label and committed-directory issues. All are fixed with
  regression tests that fail without the fixes.
- A finalizer regression test proves a candidate is admitted only under its own principal
  label (mutation-checked).
- Two retained adversarial campaigns, `test_private_lease_protocol_campaign.py` and
  `test_private_lease_fault_campaign.py`, attack the lease protocol. They cover overlap,
  ordering, replay, handle reuse, request fuzzing, role deaths, copy-out failures, extreme trees,
  nested user namespaces and `/proc`. Every scenario must end as a clean run or a whole-run
  refusal, never with a half-copied case.
- The private-host roster now requires 29 named cases, with zero skips.
- `SECURITY.md` is brought current through this release.

The candidate principal protects the examiner and worker processes and their mounts from
candidate code. It does not make a harness's judgment independent of the candidate outputs it
chooses to read, and it does not attest the host kernel, the installed isolation binaries, or an
operator account with administrative access.

## 1.5.0 — 2026-09-27 · private evaluation and report integrity

**Candidate bytes are data to the trusted evaluator, and private report checks keep candidate
workers out of the report writer's identity, mounts and process namespace.** See the compatibility
note below before upgrading.

### Private report profile

- A declared `private-evaluator-v1` check stages its trusted Python examiner from PRIME,
  freezes the candidate input before evaluation, and gives `candidate.run` workers a distinct
  subordinate host identity and disposable writable copies. Only the examiner receives the
  private report, broker and optional installed GNAT toolchain mounts.
- JUnit, GNATprove and benchmark reports are admitted only when the daemon collects an
  invocation-bound private report after clean supervisor observations. Legacy candidate-reachable
  report files remain nonadmissible. The profile and check order enter policy identity.
- Finalization, revalidation, prepare and commit require matching candidate snapshots, verifier
  identity and report evidence. Revalidation refuses preparatory changes to file metadata as
  well as file contents when the finalized or staged input lacks those changes.
- Hosted assurance requires the real private evaluator host suite. Its pinned vulnerable
  counterexample must still exhibit the known harness ownership defect; a control that merely
  crashes cannot satisfy the release gate.

The private boundary relies on the host kernel, installed isolation and toolchain binaries,
and trusted examiner logic. It does not make arbitrary candidate imports into the examiner safe.

### ⚠ Compatibility — verifier dependencies

**Staged verifiers no longer obtain undeclared sibling modules from the candidate's project
directory. Checks that relied on those imports may now fail even for an otherwise correct
candidate. Declare the authoritative helper files in the check's `verifiers` set and rerun
evaluation. WORLDLINE does not fall back to candidate-controlled dependencies to preserve the
former behaviour.**

A verifier now executes from a staging directory copied out of PRIME, not from the candidate's
writable overlay. Only files the policy *binds* are staged. Previously a top-level examiner's
undeclared sibling stayed importable from candidate-controlled storage — which is precisely the
hole: a forged helper beside the exam would be imported and would decide the verdict.

**The diagnostic you will see** is the examiner's own import failure, in the check's stderr:

```
Traceback (most recent call last):
  File "/run/worldline-verifiers/<root>/exam.py", line 4, in <module>
    import helper
ModuleNotFoundError: No module named 'helper'
```

and, on the check result, `evaluatorCompleteness.complete: false` naming the gap and the remedy.

**Before** — `exam.py` imports `helper.py` beside it; only `exam.py` is bound, and `doctor`
warns that the check will fail:

```json
{ "id": "exam", "kind": "tests", "required": true, "format": "exit",
  "argv": ["/usr/bin/python3", "exam.py"], "covers": ["src/**"] }
```

**After** — the helper is declared, so it is staged from PRIME alongside the entry point:

```json
{ "id": "exam", "kind": "tests", "required": true, "format": "exit",
  "argv": ["/usr/bin/python3", "exam.py"], "covers": ["src/**"],
  "verifiers": ["exam.py", "helper.py"] }
```

A verifier in its own directory (`evaluator/exam.py`) is unaffected: the default scope binds
that directory, so its helpers are already staged. The change bites the top-level layout, where
binding the whole directory would mean binding the repository.

### A stalled examination is not a failed candidate

Two outcomes that both block promotion must not tell the operator the same story:

| | `status` | `executionStatus` | `evaluationOutcome` |
|---|---|---|---|
| the candidate failed a valid examination | `FAIL` | `COMPLETED` | `FAIL` |
| the examination could not complete | `FAIL` | `EVALUATOR_INCOMPLETE` | `NONE` |

`EVALUATOR_INCOMPLETE` is raised from a conservative, module-level import analysis of the
**staged** verifiers, run over trusted bytes *before* anything executes — never inferred from
what the examination printed, because an examiner's stderr passes through processes the
candidate can reach. It considers only top-level absolute imports, so anything guarded by `try`
or deferred into a function is left alone: it misses rather than over-reports, because a false
positive would blame the evaluator for a candidate's genuine failure. Its absence does not
establish that the evaluator was complete.

### Trusted execution environment

- **One startup policy for every process WORLDLINE runs on its own behalf** (`worldline.trusted`).
  `python3 -c SRC` exposes the working directory on `sys.path[0]`; `python3 script.py` exposes
  the script's directory. Both are candidate-writable in normal operation. The check harness, the
  materializer, the simulation runner and the netguard forwarder now all start with `-I -S`.
  **Trusted helpers may import the standard library only**, because `-S` drops site-packages.
- **The legacy exit-status record producer is the daemon outside the sandbox.** It reads the
  service manager's exit observation and treats examiner stdout and stderr as candidate-reachable
  data. Report formats require the separate private profile above; they cannot borrow the legacy
  exit-status claim to authenticate a result file.
- **`ERROR_BEFORE_EXAMINER` is narrowed** to the one case supervisor-owned facts establish. An
  absent record is `INCOMPLETE_UNKNOWN`; a stopped or signalled unit is `INTERRUPTED`.
- **Engine-evaluated checks declare `origin: engine`** rather than being inferred from "a status
  is present and an exit code is not", which is also what a subverted harness looks like.
- **`evaluation` and `executionBinding` are attached before the evidence is hashed.** They were
  attached afterwards, and `evidence_manifest` shallow-copies each result, so the persisted
  evidence never carried them — and the commit-time gate that reads that evidence was comparing
  against fields that were always absent. Both of its guards were vacuous.

## 1.4.0 — 2026-09-22 · resource admission and execution budgets

**WORLDLINE must not start work it cannot responsibly supervise with the resources currently
available.** During JANUS II another session's prover held roughly 20 GB of a 32 GB machine;
WORLDLINE would have started a world anyway, and a starved world produces evidence that looks
exactly like evidence produced on a quiet machine.

- **One admission authority.** Every path that spawns supervised work — the agent world, each
  check, a declared service and its health probe, and `simulate` — asks it first and holds a
  reservation while it runs. The gate is passed explicitly rather than defaulted, because a
  component that can be constructed without one can spawn work nobody accounted for.
- **Admission is a transaction, not a probe.** `observe -> lock -> account -> reserve ->
  authorize` runs under one exclusive lock, because two requests that each see 20 GB free and
  each take 16 GB is the failure this exists to prevent. Sixteen processes racing one request
  against a 1500-record ledger produce exactly one admission; a harsher probe fills 18 GiB of
  headroom to within one request and never over.
- **Three things kept apart.** Admission state decides whether work may start and is never
  hashed — two runs must not stale each other's evidence because one machine had 21 GB free and
  the other 32 GB. The enforced policy is in `requirementHash`, because a suite that passed under
  32 GB is not the same evidence as one that passed under 2 GB. Telemetry is recorded and never
  hashed.
- **Ceilings the kernel actually holds.** They are applied to the unit, and read back out of the
  kernel's own cgroup files rather than assumed: a 256 MiB ceiling appears as
  `memory.max=268435456`, `pids.max=64` and `cpu.max` at exactly half a core, and a four-level
  process tree reports one identical cgroup at every level. Evidence records `requested`,
  `effective` and `observed` as three different things.
- **Outcomes are named, and unknown is not insufficient.** `ADMITTED`,
  `RESOURCES_UNAVAILABLE`, `RESOURCE_STATE_UNKNOWN`, `RESOURCE_POLICY_INVALID`,
  `RESOURCE_LIMIT_EXCEEDED`. `QUEUED` is deliberately absent: durable queuing brings priorities,
  starvation, cancellation and fairness, and that is another project.
- **An undeclared appetite is unmetered, not fatal.** Refusing the default configuration would
  stop every existing installation from forking anything, and inventing a number would be a guess
  dressed as accounting. Unmetered work reserves nothing and enforces nothing and says so — while
  every floor still applies.

### What the adversarial campaign found

Fourteen agents, six lenses. The transaction held; everything around it did not. Six blocking
defects, all repaired here and each with a regression control naming the attack it came from:

- the free-memory floor did not apply to unmetered work, and the shipped default is unmetered, so
  a machine 1.9 GiB below its own floor admitted work with headroom already negative;
- a service-manager blip was read as "the workload is dead", and admission wrote that verdict to
  disk, permanently deleting the accounting for workloads that were still running;
- three corrupt-ledger shapes escaped as tracebacks rather than refusals, a negative reservation
  manufactured headroom, and duplicate ids meant releasing one released both;
- telemetry for a unit systemd had never heard of was reported as measured, successful and under
  its ceiling;
- a workload the kernel OOM-killed was recorded as a clean run, because the truthful window is
  tens of milliseconds and the runner sampled once a second;
- `simulate` spawned supervised work with no reservation and no ceiling at all.

One claim was too strong and is corrected rather than defended: a same-uid workload can create a
sibling cgroup beside its own unit and leave both the ceiling and the accounting. Every shipped
call site puts the workload inside the sandbox, where that escape fails. The cgroup is the budget
for a workload that is not trying to leave it; the sandbox is what stops one that is.

### What this does not do

It does not guarantee completion — another process may take the memory a microsecond later. It
does not police the host; WORLDLINE governs the workloads it starts. And it does not make
evidence produced under a satisfied budget correct evidence.

## 1.3.2 — 2026-09-22 · installable from its own release archive

One defect, found by trying to install 1.3.1 on the machine it was built for.

- **1.3.1 could not be installed from its own published tarball.** Three controls in
  `tests/test_install_guards.py` build their fixture from `git ls-files`, and a release archive
  is not a git checkout, so `git` exited 128 and the three raised. The installer runs the Python
  suite as a gate, so the install aborted — correctly, before anything was replaced, but it
  meant the documented installation path (download the release, verify it, run `install.sh`)
  could not complete. Installing from a checkout hid it, which is exactly why the artifact
  itself is the thing that has to be tested.

  The fixture now prefers git's index when the tree is a checkout and falls back to a filesystem
  walk when it is not, so the controls run from a checkout and from an unpacked archive alike.
  Nothing is skipped: a self-skipping guard was one of the findings 1.3.1 set out to remove, and
  replacing "errors from a tarball" with "silently skips from a tarball" would have been the
  same defect wearing a different hat.

Found by an independent review of that fix, and repaired in it:

- **The archive recipe could not complete.** `WORLDLINE_PLUGIN_SRC` defaults to a sibling of the
  source tree, which exists in a developer layout and does not exist beside an unpacked release.
  The README recipe now sets it, and the installer's refusal names it instead of only reporting
  that a path is not a git repository.
- **The fallback walk copied a git worktree's `.git` file.** In a worktree `.git` is a regular
  file holding a gitlink, and the skip set only filtered directory names. A fixture that copied
  it would make its own `git init`/`add`/`commit` operate on the repository it points at — the
  reviewer reproduced exactly that, moving an external repository's branch while all ten controls
  still reported OK. `.git` is now excluded at any depth and a control asserts the fixture's git
  directory resolves inside the sandbox.
- **The skip set is anchored to the top level**, like `.gitignore`'s own `/obj/` and `/bin/`
  rules, so a tracked `cli/bin/helper.py` cannot vanish from the fixture because a directory
  somewhere is called `bin`.

No engine behaviour, no evidence semantics, no installer logic and no release-gate logic
changed. `v1.3.1`'s archive and tag are untouched.

## 1.3.1 — 2026-09-22 · deployment and install safety

Installation only. No engine behaviour, no evidence semantics and no release-gate logic changed;
`v1.3.0` remains the release that introduced those and its archive and tag are untouched.

- **An unreadable daemon is no longer read as "nothing is running".** The installer's inline job
  check parsed the status document with `except Exception: print(0)` and ended its pipeline with
  `|| echo 0`, so a daemon that could not be reached, answered with the wrong shape, or exited
  non-zero all resolved to "0 agent jobs" — and the upgrade restarted it anyway.
  `scripts/preflight.py` replaces it with three outcomes per gate where **UNKNOWN is a refusal**:
  the status parses and has the expected shape; no job is STARTING/RUNNING/FINALIZING; no world
  is still MUTABLE/FINALIZING; no transient `worldline-*` unit exists; no transaction is open;
  recovery, store integrity and every managed root report OK; no unsupervised world; ghosts are
  disabled (they fork on any PRIME checkpoint, so an enabled ghost refuses unless
  `--allow-ghosts`); and there is room for the backup. `tests/test_preflight.py` drives the real
  script against a fake CLI and proves each refusal.
- **The upgrade is ordered so it can be interrupted, and so the backup means something.** Refuse
  if a previous install did not finish → resolve BOTH identities → build, test, prove →
  preflight → **stop the daemon** → back up → install → start → verify → receipt. Stopping
  before the backup is what closes the window in which a fork, race or ghost could start against
  a half-replaced runtime, and what makes the store backup consistent instead of a copy of a
  live SQLite file. Identities resolve before the build, so an unpinned or unreachable plugin
  costs a second rather than a full build.
- **The plugin is pinned, not "whatever main is".** `WORLDLINE_PLUGIN_REF` is required and must
  resolve to a commit; a moving ref needs `WORLDLINE_PLUGIN_ALLOW_MOVING_REF=1` and says so. It
  is resolved before anything is replaced, so an unreachable plugin aborts with the installation
  still whole rather than after the runtime has been swapped. An engine archive does not identify
  the plugin, and the installer no longer pretends otherwise.
- **The backup covers the store.** The whole state directory (store, receipts, transactions,
  events) minus `install-backups`, which lives inside it and would otherwise recurse, taken with
  the daemon stopped. `scripts/backup_manifest.py` records what was captured so a file missing
  from a backup is distinguishable from one that never existed here. Payload data is inventoried
  and copied only with `WORLDLINE_BACKUP_PAYLOADS=1`; what is not copied is written down.
- **What ends up running is checked.** `scripts/verify_install.py` compares the runtime tree,
  library, proof manifest, header, both launchers, the unit, the pinned plugin commit and the
  version the *running* daemon reports, and writes an install receipt. The previous installer
  printed those values and compared none of them.
- **`scripts/rollback.sh`** restores a backup: engine by default, `--with-state` for a data
  rollback that moves the superseded store aside rather than deleting it. It restores the unit's
  recorded enablement and run state instead of switching the daemon on.
- **Hazards found by an adversarial review of the hardened installer itself**, all fixed here:
  the desktop shell restart *kills* the running shell and has three failure exits, every one of
  which was discarded while a success line printed over a possibly dead desktop; unit enablement
  and run state were never captured and a masked unit (a symlink to `/dev/null`) was silently
  destroyed; the staging directory was predictable and not required to be new; symlinked install
  targets were converted to regular files the backup could not restore; a caller-supplied
  `WORLDLINE_CORE_LIB` could point the gates at a library other than the one built; and
  re-running after a failed install overwrote the good backup with a copy of the broken state.
- **Rehearsed, not asserted.** `worldline-lab/deploy/rehearse.py` runs 1.2.x → 1.3.x → rollback
  on a throwaway copy with private daemons: the new engine opens the old store with identical
  receipt verification, a world finalized by the old engine takes the documented path
  (`EVIDENCE_CONTEXT_MISSING` → `revalidate` → promotable), and **the old engine then opens and
  verifies the store the new one wrote to**. The README's long-standing claim that older code
  keeps reading newer stores is now backed by that run rather than by assertion.
- **A second adversarial review, of the hardening itself.** It found that the preflight scored
  whatever it happened to record: with the daemon quiet, five of its store gates never ran at all
  and the remaining OK results produced `permitted: true`. The gate list is now a declared roster
  and **an unasked question is a refusal** — a gate missing from the results refuses exactly as a
  failed one does. The same review found the installer deciding whether to stop the daemon from
  `systemctl is-active --quiet`, whose non-zero exit conflates `deactivating`, `activating`,
  `failed` and "no user manager here": an upgrade could therefore replace the runtime under a
  live process. Both the installer and the preflight now read `ActiveState` and treat anything
  they cannot determine as a refusal, and open transactions are read from the store directory so
  that stopping the daemon does not blind the gate that matters most once it is stopped.
- **The receipt records what was observed, not what was placed.** `verify_install.py` now reads
  the kernel library the running daemon actually mapped from `/proc/<pid>/maps`, and checks that
  the daemon answering is a *new* process and the one the user manager supervises — a daemon that
  never restarted would otherwise pass every file comparison with the old runtime still in
  memory. It records whether the proof gate ran or was skipped with `WORLDLINE_SKIP_PROOF=1`, and
  it writes the receipt even when its own probes fail, so a failed verification is evidence
  rather than a missing file.
- **A false engine identity is worse than none.** `git -C DIR rev-parse HEAD` walks up out of
  `DIR`, so unpacking a release archive inside any other repository recorded *that* repository's
  commit as the engine. The commit is now accepted only from a checkout whose own top level is
  the engine directory; otherwise the receipt says `unknown` and the installer says why.
- **Backups no longer grow without bound.** Each one holds a full copy of the state directory, so
  an installer that never prunes eventually fills the disk — a worse failure than the one backups
  insure against. After a *verified* install the newest `WORLDLINE_BACKUP_KEEP` (default 5) are
  kept and older ones removed, each removal printed. `scripts/prune_backups.py` refuses to touch
  anything that is not recognisably one of its own backups and never follows a symlink out of the
  backup area.
- **The recovery path is tested.** `tests/test_rollback.py` drives the real `rollback.sh` against
  a sandbox installation with a simulated user manager: refusing an incomplete backup, keeping the
  superseded store aside, leaving a disabled unit disabled, not starting a daemon that was
  inactive before the install, and finishing the engine rollback while naming what happened to the
  plugin. The core-library guard is now executed rather than asserted by reading the source, and
  the dirty-worktree guard runs against a fixture checkout instead of skipping itself whenever the
  developer's worktree happens to be clean.

## 1.3.0 — 2026-09-21 · evidence freshness; exact-commit releases

- **Approval is bound to the exact content, rules and execution context it verified.** Every
  finalization now records a *validation context* (schema 1) inside the hashed evidence
  manifest: the canonical policy in force, the required checks and their semantics, the
  authoritative verifier files those checks name (hashed by content, from the checkpoint the
  world was forked from and again from the candidate's own tree), the engine identity
  (`__version__` + runtime tree hash) and the security-relevant execution configuration
  (network policy, projections, sandbox, check timeout), the PRIME at fork, the candidate's
  identity, the adapter and the results. Its `requirementHash` covers the requirement half
  only. At every promotion boundary the CURRENT PRIME's requirement hash is recomputed from the
  live policy and verifier bytes and compared with the candidate's; the pair also goes to the
  proved kernel (`Expected_Validation_Context` / `Candidate_Validation_Context`), which never
  authorizes a mismatch. Refusals are named: `EVIDENCE_STALE` (with the list of differences),
  `EVIDENCE_CONTEXT_MISSING`, `EVIDENCE_CONTEXT_INVALID` (wrong world, corrupted, unsupported
  schema), `VERIFIER_MODIFIED_BY_CANDIDATE` (the candidate rewrote, deleted or redirected a
  verifier its own evidence ran). Each refusal is a `promotion-refused` causal event; no
  transaction is created and PRIME is untouched. The requirement identity is semantic:
  reordering or reformatting `.worldline.json` does not stale evidence; changing a check's
  argv, cwd, required flag, format, covered paths, the protected list, a verifier's bytes, the
  engine or the network policy does.
- **Tested bytes vs staged bytes.** A three-way merge onto a PRIME that moved produces staged
  bytes the candidate's evidence never covered. The kernel now receives `Tested_Root` /
  `Staged_Content_Root` (content identities over manifest entries, timestamps excluded) and
  refuses `STAGED_UNTESTED` unless they agree. When they differ and there is no conflict,
  prepare runs the current checks over the staged result itself (a *staged validation*, bound
  to the candidate and the staged content root, with the protected-paths check evaluated on
  what would change in PRIME); only a PASS makes the staged content the tested content. The
  facts screen shows `Evidence:` with both identities, the untested paths and the staged
  validation's results. Prepare may therefore take as long as the project's checks.
- **Commit re-checks what prepare checked.** At the serialized commit boundary the candidate
  payload is re-captured and compared with the prepared identity (`CANDIDATE_CHANGED_AFTER_PREPARE`;
  a naive tamper is caught earlier as `PAYLOAD_INTEGRITY_FAILED`), the current requirement hash
  is recomputed and handed to the kernel (a policy/verifier/engine change between prepare and
  commit is `EVIDENCE_STALE` with `decision: VALIDATION_CONTEXT_MISMATCH`; a PRIME content change
  is still `PRIME_CHANGED_AFTER_PREPARE` first), and a record prepared by a runtime without
  validation contexts is refused `TRANSACTION_RECORD_LEGACY` (abort it, prepare again).
- **Return rules.** A *checkpoint return* (to a `prime-…` world: restoration of a previous
  reality) needs no candidate evidence; the transaction records mode `checkpoint-return` and the
  current requirement hash. *Re-application* of a candidate world (`return WORLD` for a
  COLLAPSED/ARCHIVED candidate) is a promotion and obeys the same freshness rules as a collapse,
  checked against that world's own context (mode `re-application`). Neither is a bypass.
- **`worldline revalidate WORLD` / `worldline validation WORLD`.** The documented path for an
  intact candidate whose evidence went stale (policy edited, verifier changed, engine upgraded,
  configuration changed) or that predates 1.3.0: the CURRENT PRIME's checks run again over the
  candidate's finalized bytes in the check sandbox, and a PASS context is stored beside the world
  (store meta `validation:<instance>`, bound to the world's content identity; no schema bump).
  A FAIL leaves the stale context in force. `validation` shows fresh/stale, the effective
  context and its source (`finalization` or `revalidation:<id>`), the differences and the
  revalidation history; `doctor` gains `policy` (the current requirement hash, checks, protected
  paths and verifiers). Revalidation never changes a world's state or payload and does not
  re-run the agent check.
- **Receipts name the evidence.** `evidenceBinding` (optional; 1.2 receipts verify unchanged)
  records mode, evidence source, candidate context hash, the requirement hash at prepare and at
  commit, tested and staged content roots, the staged validation and the untested path count.
  Two non-claims are added: freshness is identity comparison decided by the runtime with the
  kernel proving only the equality verdict, and checks are not re-run at commit.
- **Kernel.** `Collapse_Request` is version 2 (`WL_COLLAPSE_REQUEST_VERSION 2`) with four new
  hash fields; `Decision` gains `Validation_Context_Mismatch` (10) and `Staged_Untested` (11);
  the postcondition of `Decide` requires both new equalities for `Authorized`. 130 checks proved,
  nothing assumed; Ada behaviour and fuzz tests cover the new selectors.
- **Release workflow bound to the exact commit.** `.github/workflows/assurance.yml` (shared by
  `ci.yml` and `release.yml`) runs `scripts/assurance.py` on one full commit id: build, Ada
  tests and fuzz, the Python suite (incl. `tests/test_freshness.py` and
  `tests/test_release_gate.py`; the count is read from the run, never typed here), the proof gate re-run on that build and the manifest check with
  the library, recording every outcome, the checkout identity and the toolchain into
  `assurance.json`. `release.yml` publishes only after `scripts/release_gate.py` accepts that
  report for the tag's commit and tree (rejecting another SHA's run, partial or missing steps,
  version/tag/changelog mismatch, proof exceptions or a different proved source set, a remote
  tag elsewhere, an existing release, artifact substitution), creates the release as a draft,
  verifies the uploaded assets against the computed digests, publishes, and re-verifies. Notes
  are generated from the changelog and the recorded numbers; nothing is hard-coded. Tokens are
  read-only everywhere except the publish job.
- **After the separate adversarial review (JANUS II §7) — four repairs.** (R1) A verifier's
  helpers are as authoritative as the file a check names: the default verifier scope is now
  the named file's whole directory, and a check may declare `verifiers` globs to bind exactly
  the files it executes or reads; a top-level verifier without a declaration binds only itself,
  which `doctor.policy.warnings` and `validation` now say out loud. (R2) A declared service's
  argv, cwd, environment, health probe and restart policy are part of the requirement identity
  (`service changed: …` in the differences). (R3) An argv path inside the check's own `covers` is
  candidate data, not a verifier, and is now named in `doctor.policy.warnings` instead of being
  dropped silently; a *declared* verifier inside its own `covers` is refused at load,
  `INVALID_PROJECT_CONFIG … cannot be candidate-owned`. (R4) The execution identity now includes the environment
  the check runner forwards into the sandbox (PATH, LANG, toolchain selectors; session-specific
  names excluded), the check interpreter and the proved kernel library's hash, so a daemon that
  resolves different tools stales the evidence (`execution changed: checkEnvironment (PATH)`).
  Retained reproducers: `tests/test_freshness.py` class K; the reviewer's own tests are kept
  with the run artifacts.
- **Second review (fresh bytes after the repairs above) — six more.** (R1, blocking) A file
  the candidate ADDS inside a verifier scope — a shadow package beside the exam that hijacks
  `import helper` without changing a byte of any existing verifier — is now named
  `… (added)` in `verifiersModifiedByCandidate` and refused; candidate-side verifier resolution
  was already tree-wide, the comparison now runs both ways. (R2, major) Re-applying a world
  that has since been live (`return WORLD` for a world that became PRIME and was displaced)
  used its displaced payload as the "tested" content; the merge is now judged against the
  world's declared finalization manifests, the displaced differences are listed as untested
  paths, and only a passing staged validation over the actual bytes can authorize them. (R3)
  A check whose argv names no existing file (`make test`, `-m pytest`, `npm test`, `sh -c …`)
  binds no verifier and is now warned as such against the actual tree, never with a false
  "top-level verifier" message. (R4) A `return-…` world — an earlier return's result — is a
  previous reality like a `prime-…` checkpoint and can be returned to without candidate
  evidence (its copied context is bound to another instance and used to refuse). (R5) No test
  count is typed into the changelog; the notes derive it from the run. (R6) `release.yml`
  resolves the tag's target in the publish job independently of the resolve job, fails loudly
  when the release lookup errors for any reason other than "not found", and the gate bounds
  skipped tests (`--max-skipped`, default 3).
- **Third review (the last cycle) — APPROVE, with four non-blocking corrections applied:**
  SECURITY.md now states the verifier-binding limit beside the hold it qualifies (unnamed or
  covered examiners are warned, not refused); the gate requires a floor of tests to have run
  (`--min-tests`, default 150, a deliberate floor like the proof gate's); docs name the retained
  reproducer classes A–L; proof counts in prose are the numbers this release's gate printed and
  the release notes carry the derived count from the assurance run.
- **CI had been masking Python failures.** The old workflow ran the suite as
  `python3 -m unittest … 2>&1 | tail -n 40`, so the step's status was `tail`'s and three tests
  had been failing on every "green" main run since 1.2.1 (a codex-only adapter test, an
  Arch-only `/usr/bin/pacman` probe, and the simulation's `/boot` overlay on the runner). The
  assurance runner records the real outcome; those tests now skip with a recorded reason where
  the host genuinely lacks the capability (executable absent, a system root that cannot be an
  overlay lower layer) or probe a binary every Linux has. Supervision classification accepts the
  manager's own main-process-exit record as proof of supervision (some systemd versions log no
  "Started" entry for a workload that exits before the start job is reported) and its bounded
  journal window is 10 s.
- **Compatibility.** Store schema stays 2. Worlds finalized by 1.2.x carry no context and are
  refused `EVIDENCE_CONTEXT_MISSING` until revalidated; an engine upgrade stales every existing
  candidate by design (the engine is part of the requirement) — `worldline revalidate` is the
  answer, not a fork. PREPARED transactions from 1.2.x are refused at commit
  (`TRANSACTION_RECORD_LEGACY`). The plugin needs no change: new codes render as text.

## 1.2.2 — 2026-09-21 · why credits only what is in effect; codex provenance

- **`why` credited archived siblings.** Every world that touched a line has a range row, and the
  newest ordinal won, so after a three-lane race the lane that finished last but was never
  collapsed was named as the author of a line in PRIME. `why` now considers only worlds in
  effect (COLLAPSED, or PRIME itself), checks that the world's copy of the line is what PRIME
  holds, and lists the others as `bystanders`. A line no world in PRIME's lineage changed is
  answered as a **checkpoint attribution** (registration or return) instead of `NOT_FOUND`;
  a line past the end of the file is still not found.
- **codex file changes, commands, and messages are causal events.** `codex exec --json` nests
  touched paths under `item.changes[]`; the adapter now expands a completed file change into
  one `tool-event` per path (`apply_patch`, add/update/delete), records commands as `shell`
  tool events with the exit code, and agent messages as `agent-message`. Later worlds get
  file-level provenance with the tool named, not "not supplied by adapter".

## 1.2.1 — 2026-09-21 · per-adapter options; a failed finalization closes its job

- **`adapterOptions`** (global config): extra argv a builtin adapter inserts before the mission,
  shown verbatim in `worldline adapters` (`argvPreview`). The case that prompted it: running
  codex worlds on a chosen model and reasoning effort without touching the operator's own
  `~/.codex/config.toml` — `{"codex": {"argv": ["-m", "gpt-5.6-luna", "-c", "model_reasoning_effort=max"]}}`.
  Only builtin adapter names are accepted; generic adapters carry their own argv.
- **A world whose finalization failed left its job RUNNING.** Seen live: a cancelled codex lane
  died with `CORE_IO` while its base checkpoint was verified, the world went `DEAD`, and the job
  stayed `RUNNING` (the bar counted it, the root set stayed busy) until a daemon restart. The
  job is now closed with the error whatever state the world is in, and the reason is recorded
  under `evidence.supervision` as well as `materializationError`.
- **Base checkpoint verification retries** transient `CORE_*` read failures (the base is shared
  by every sibling and read by several finalizations at once) and then fails by name:
  `BASE_CHECKPOINT_UNVERIFIED` with the root and the cause.

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
