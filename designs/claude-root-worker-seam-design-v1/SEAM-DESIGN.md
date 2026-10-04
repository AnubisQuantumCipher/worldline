# Root-worker runtime lane: seam-by-seam design analysis (v1)

**Status: DRAFT_FOR_GPT61_REVIEW.** This is an analysis-and-design draft written by a Claude Code
analysis subagent (claude-opus-5-5) for the Claude lead. It reviews nothing, grants nothing and
qualifies nothing. It must be judged by a different-author actual `gpt-6.1-sol` review before any
code is written. Every original obligation, accepted case, deterministic fixture, control, contract,
threshold and proof floor remains **OPEN** and unchanged.

---

## 0. Scope, basis and truth boundary

**Lane.** `W/work/protected-original-root-worker-repair-v1`, where
W = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow`. Its status is
`INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY`.

**Basis identities.** These were observed with `sha256sum` and match the handoff's own records:

| File (`handoff-to-claude-v1-retry1/`) | sha256 |
|---|---|
| `HANDOFF.md` | `f0d6add2f97011654d9a603df9f50f8c09d73e80cd4f3fcc37150af3ad77d14d` |
| `handoff-freeze.json` | `c8c6e40addc56654f28f7517f0c5ff64cc999424e1ae9ccb831fd799da96f33c` |
| `binary-delta.json` | `be41995133b8641ba244397e1cf6068bade22f478bdbe15590ddaf55a2f6bb16` |
| `source-inventory.json` | `0a12d06d2b43a1949bac24369dc615576105b3d6de11e5653ebfe559235637f3` |
| `human-delta.patch` | `de2406cca971d51681a2b9c6265cbb4f5d22f6070c66f75f6e5d2349166c364b` |

**Snapshot check.** This was observed by read-only hashing. All 736 inventoried `source/` files are
present with matching sha256, and there are 736 files under `source/`. File modes were not rechecked.

**Method.**
- Static reading only.
- Python was used solely for JSON/AST/text processing of source *text*. The contract-pin
  recomputation re-implements `proof_manifest.normalized_ada` in a standalone script; no WORLDLINE
  or COSMOGONY module was imported.
- Nothing was compiled, run, proved or tested.
- No lab, `/srv`, service, socket, store or window was touched.
- SIA was used read-only (`sia.search`). No note was written.
- Skills loaded: the `ada` hub, `ada-omarchy`, `spark-users-guide`, `ada-programming`,
  `advanced-ada`, `gnat-toolchain`, `ada-high-integrity`, `ada-2005-amendment`, `worldline` and
  `cosmogony`.

**Prior input.** `W/work/claude-root-worker-notes-v1` holds model-origin Claude subagent notes. They
are not review and not evidence. Every claim reused here was re-checked against the cited lines
unless it is marked *[carry-over, not re-checked]*.

**Anchor notation.**

| Notation | Meaning |
|---|---|
| `R/` | lane `source/` |
| `rw/` | `R/runtime/worldline/` |
| `RW:n` | lane `handoff-to-claude-v1-retry1/HANDOFF.md`, line n |
| `P1:n` | `W/outputs/claude-phase1-handoff-20261004/HANDOFF.md`, line n |
| `PROMPT:n` | `/home/sicarii/Documents/complete-phase1-prompt.txt`, line n |
| `ROADMAP:n` | `/home/sicarii/Work/ada-spark-readiness-20260927/roadmap-requirements.md`, line n |
| `RC` | `R/protected-canonical/required_controls.json`. This is the inherited preimage roster, status `SOURCE_ONLY_UNRUN_UNADMITTED`. |
| `OB-nnn` | `OBLIGATIONS-v2.json` |
| `GATE` | `W/work/protected-original-root-worker-repair-v1/dependency-source/lab/intent_gate.py` |

**Unverified kernel statements.** Statements about Linux kernel semantics marked
**[unverified reasoning]** are my own. Each needs a measured observation in an authorized lab.

**Numbers.**
- Observed counts are tool outputs.
- Derived numerals went through JACKAL `jackal_exact`:
  - `parsed=24+36`, `exact=60`, `status=exact`, `formal=false`;
  - `parsed=63-3`, `exact=60`, `status=exact`, `formal=false`.
- Non-claims for both results: "NOT formal-bounded: this lane carries no Lean-checked certificate".

---

## 1. Findings that precede every seam (P0)

These stop the main path before any seam-specific logic is reached. Each was verified by reading.
None changes any original requirement.

**P0-1. Self-deadlock on the selected Gate mutex. Pre-existing; not introduced by the draft.**
- `GATE:371` (and `dependency-preimage/lab/intent_gate.py:362`) sets `self.mutex = threading.Lock()`,
  which is non-reentrant.
- Scoped code acquires it and then calls a method that acquires it again on the same thread:
  - `rw/protected_scoped_resource_runtime.py:385` takes `with self.gate.mutex,self.order:`;
  - it then calls `reconcile_context()` at `:388`;
  - `reconcile_context` itself takes `with self.gate.mutex,self.order:` at `:357`.
- `CanonicalOperationPrincipal._reserve` calls `intent_for_operation` (`rw/protected_operations.py:640`).
  Every scoped reservation would therefore block forever on the first request, rather than refuse.
- The same nesting exists in the lane preimage (`preimage/.../protected_scoped_resource_runtime.py:356,382`).
- The Claude lead had already verified this by reading (`claude-root-worker-notes-v1/NOTES.json`).
- Other nestings were listed by the prior notes *[carry-over, not re-checked]*:
  - `:412 → protected_scoped_resource_service.py:213`;
  - `:630 → :642 → :357`;
  - the draft's `protected_root_observation.py:57 → canonical_actor_execution.py:61`.

**P0-2. One stale contract pin refuses every protected start.**
- I recomputed every effective `CONTRACT_PINS` entry from the AST literals of `proof_manifest.py`,
  using the original normalized grammar.
  - Preimage: 171 effective pins, all matching.
  - Draft: 191 effective pins, with exactly one mismatch, `runtime/worldline/protected_operations.py`
    (pinned at `rw/proof_manifest.py:1012`).
- Consequences:
  - `contract_problems` is non-empty, so `StartupLease.construct()` refuses
    `STARTUP_EXACT_NATIVE_PROOF_UNAVAILABLE` (`rw/protected_startup.py:683-684`).
  - `RootWorkerIntake` refuses `ROOT_WORKER_ORIGINAL_FULL_SOURCE_PROOF_ADMISSION_REQUIRED`
    (`rw/protected_root_worker.py:355-357`).

**P0-3. Most of the lane is unpinned.**
- There are 60 source-tree delta entries (JACKAL exact, see §0). Of these, 24 are covered by
  `CONTRACT_PINS` keys and 36 are not (observed).
- The 36 unpinned entries include:
  - `protected-root/native_root_worker_supervisor_v1.c`, `worker_entry.py` and `launcher.py`;
  - every `rw/root_worker_*.py`;
  - `protected_root_*.py`;
  - `protected_startup.py`, `daemon.py` and `proof_manifest.py`;
  - the new `tests/test_resource_child_execution_v1.py`.

**P0-4. `attach_scoped_resource` is defined twice. Pre-existing.**
- It is defined at `rw/protected_scoped_resource_runtime.py:52` and again at `:961`.
- The later definition shadows the earlier one at import. It drops the exact early-selected producer
  check: `selected==gate.root/'authority/resource/run-scoped-config-v1.json' and selected in
  lease.allowed`, code `SCOPED_EXACT_EARLY_SELECTED_PRODUCER_REQUIRED`.
- Nothing calls either definition yet, so this is latent until seam 2 wires attachment.

**P0-5. The root route omits original pre-dispatch guards of `_invoke_serial`.**
- `CanonicalOperationPrincipal.invoke` routes every non-owner operation to `RootWorkerFront.invoke`
  (`rw/protected_operations.py:716-726`).
- That route does not apply three original guards:
  1. the unresolved-use gate (`:730`, `OPERATION_UNRESOLVED_NATIVE_USE_BEFORE_ORDINARY_ROUTE`);
  2. the genuine request-context check (`:728`, `context.peer is request and current_peer() is request`);
  3. the workload-route refusal (`:744-745`, `OPERATION_ORIGINAL_WORKLOAD_RESOURCE_ROUTE_UNINTEGRATED`).
- Preserving these guards on the root route is required. It is not a new refusal.

**P0-6. Integration base.**
- The lane's preimage is the actor-stdin V4 protected lineage, not commonV4.
- Observed: the selected commonV4 source contains none of the following:
  - `protected_operations.py`, `protected_scoped_resource_runtime.py` or `canonical_operation_kernel.py`;
  - the SPARK units `Worldline.Canonical_Operation`, `Worldline.Operation_Authority`,
    `Worldline.Canonical_Exchange`, `Resource_Scoped_Run_Ledger` or `Worldline.Resource_Child_Execution`.
- Its `core/` has 149 entries against 176 in the lane preimage. Its `protected_startup.py` and
  `worldline-c_api.adb` differ from the lane preimage.
- The lane changes `core/worldline-c_api.adb` from 56543 to 148068 bytes (observed). That collides
  with the lead's C-API boundary consolidation (A1; design v3 in progress).
- Every seam slice below is authored against the lane lineage. Composing it into the lead's common
  composition is a separate, explicit, reviewed import (P1:91: "Do not import the whole draft blindly
  into commonV4"; P1:153).

**Main-path order of refusal or blockage, as read:**
1. startup: P0-2 → seam 2;
2. first reservation: P0-1;
3. `pre_effect`: seams 1 and 7;
4. worker intake: seams 8, 9(a), 2 and 3;
5. `collapse.commit`: seams 1 and 6;
6. collector: seams 6, 9(b) and 2.

---

## 2. Seams

Each seam lists:
- its current draft state, with anchors;
- the original requirement it must preserve, quoted;
- a design direction with invariants;
- decisions requested from the reviewer;
- dependencies;
- what is lead-only source work and what needs privilege or the operator;
- additive controls;
- risks and size.

### Seam 1 — Full scoped original pre-effect conjunction

**Current draft state.**
- `rw/protected_root_worker.py:162` calls `p._reserve(request)`. `:167` calls the unchanged original
  `p.pre_effect(operation)`. `:168-171` replays `RESERVE_USE` and appends `EFFECT_INTENT` with
  `boundaries=[boundary]`, which drops the `DISPATCH_INTENT` resource reply that `_invoke_serial`
  retains at `rw/protected_operations.py:749`.
- `pre_effect` (`rw/protected_operations.py:678-715`):
  - `:687` selects the operation's launch policy.
  - `:688` scoped `machine_admission(...,'DISPATCH')` compares that policy with
    `resource_launch_material`. When `principal.root_worker` is set, `resource_launch_material`
    returns the root `handler_plan` (`:469-476`). The result is a refusal,
    `SCOPED_CALLER_MACHINE_POLICY_DIFFERS_FROM_ACTUAL_OWNER_PLAN`
    (`rw/protected_scoped_resource_runtime.py:640-641`), unless the owner `worker_policy` happens to
    equal that operation's policy.
  - `:690` uses the inherited old-ledger `collect` (`rw/protected_resource_runtime.py:316-...`).
  - `:708` passes the scoped `ScopedState` to `CanonicalOperationKernel.observe`
    (`rw/canonical_operation_kernel.py:28`), whose old typed marshal raises
    `ValueError('complete typed State input is required')` (`rw/resource_run_ledger.py:181`).
  - The path fails closed and does not flatten, but no positive route exists.
- The original conjunction `core/worldline-canonical_operation.adb:3-35` consumes the flat
  `L.Ledger_State`.
- `Root_Admission` (`core/worldline-resource_child_execution.ads:172-184`) is
  `Authorize_Execution` plus controller facts. It has no `Reserve_Use` replay, binding or collapse
  clauses, so it is not a substitute (RW:28).
- The same old-state dependency exists in two more places:
  - the broker exchange inputs (`rw/canonical_full_broker.py:117-140`, `resource.state`/`rows` at
    `:130-137`);
  - the K4 owner-completion path (`rw/protected_operations.py:605-621`).

**Original requirement (quoted).**
- RW:28: "Author an additive closed typed scoped/native conjunction that redecides the complete
  original grant/use/request/current/evaluation/collapse inputs, preserving every original clause,
  accepted case and full proof obligation. Merely passing the selected root/actor native status does
  not replace this."
- P1:125: "Do not flatten full scoped history into an older RunState or copy a readiness flag."
- P1:107: "caller-filled equal bytes alone are insufficient."
- ROADMAP:105: "Put the consequential collapse rule in SPARK: … capabilities, resource epoch, legal
  transaction …"
- ROADMAP:113: "Python has no independent definition of authorization."
- PROMPT:32.
- OB-198, OB-061, OB-023, OB-219, OB-131.
- RC required genuine cases:
  - "every ordinary operation with missing/wrong/right-widened/revoked/expired grant";
  - "complete grant lineage attenuation with outstanding use ceiling before effect";
  - "complete historical K4 resource packets stay in original or scoped native domains; no
    projection".

**Design direction.**

1. **New additive SPARK unit**, spec first: `Worldline.Scoped_Canonical_Operation`.
   - Decision type: the original five values `Authority_Refused | Resource_Refused |
     Binding_Mismatch | Collapse_Refused | Ready`.
   - `Decide` carries `Post => Decide'Result = Reference(...)`.
   - Inputs:
     - the unchanged authority frame (`Authority_Data, G, H, B, Now, E`);
     - the complete scoped packet `State, History, Rows, Projection, Buckets, Observed, Facts, Current`;
     - `Bound, Requester, Peer, Collapse`.
   - Clauses, in original order:
     - **C1, authority (literal):** `A.Decide(..., A.Reserve_Use, E, Empty, Empty) = A.Reserved_Replay`.
     - **C2, resource (lifted, not flattened):**
       - `S.Valid`, which is Shape ∧ Physical [per-bucket held/charged conservation] ∧ Contained
         [`L.Parent_Supports` + same physical key + projected-charge bound] ∧ Current_Valid;
       - ∧ `S.Native_Valid`;
       - ∧ ∃I: `S.Retained_Origin(Rows(I))` ∧ `L.Same_Binding(Rows(I).Bound, Bound)` ∧
         `Rows(I).State ∈ {Reserved, Launch_Intent, Running}` ∧ `Rows(I).Scope` equals `State.Current`.
     - **C3, binding (literal):** the original equalities, with `State.Scope` read as
       `State.Current` (instance, policy, policy epoch), plus `Bound.Resource_Epoch = B.Resource_Epoch`.
     - **C4, collapse (literal):** the original clause for `Commit_Collapse | Commit_Transaction`.
2. **Refinement, proved rather than assumed.**
   - Define a Ghost projection `Proj` from single-frame, identity-projection scoped inputs to
     original inputs. It is used only in specifications, never at run time.
   - Prove `Scoped_Refines_Original`, with `Always_Terminates` and `Global => null`:
     `Post => (if Single_Frame_Identity(y) then Scoped.Reference(y) = Canonical_Operation.Reference(Proj(y)))`.
     The pattern is `Root_Refines_Original` (`core/worldline-resource_child_execution.ads:232-237`).
   - This shows that on the original domain no accepted case is lost and no refusal becomes
     acceptance.
   - Per-clause lemmas: C1, C3 and C4 are syntactically identical. C2 relates
     `S.Physical`/`S.Contained`/`S.Native_Valid` to `L.Conserved`/`L.Contained`/`L.Native_Valid`
     (`core/resource_run_ledger.ads:236-275`; `core/resource_scoped_run_ledger.ads:181-215,303-312`).
3. **ABI.**
   - Export `wl_scoped_canonical_operation_{version,layout,decide}_v1` only through the sole
     `worldline-c_api`. `UNANALYZED_BOUNDARY = {"worldline-c_api"}` (`rw/proof_manifest.py:316`).
   - Follow the C-API boundary design v3 pattern. No new `SPARK_Mode => Off` unit.
   - Note that the existing `Worldline.Canonical_Operation_C_API` is already `SPARK_Mode => Off`
     outside that boundary (`R/core/worldline-canonical_operation_c_api.ads:2`). It stays an open
     original body obligation and is not a precedent.
4. **Python wrapper.**
   - `ScopedCanonicalOperationKernel` with exact version/size/alignment/offset checks, as in
     `rw/canonical_operation_kernel.py:13-27`.
   - It reuses the scoped `_marshal` (`rw/resource_scoped_run_ledger.py`) and
     `OperationAuthorityKernel.prepare`.
   - It returns the raw input, arena, rosters and output, and never a Python verdict.
5. **Caller.** `pre_effect` gets a branch selected by exact type.
   - The original branch stays byte-identical when `type(self.resources) is ProtectedResourcePrincipal`.
   - The scoped branch, when `type(...) is ProtectedScopedResourcePrincipal`:
     - takes plan and policy from the single seam-7 crosswalk entry;
     - acquires `gate.mutex` exactly once (SL-0) across context → capture → inspect → decide;
     - re-checks `before == current_snapshot()`;
     - leaves the collapse evaluation (`:692-706`) unchanged;
     - retains `S.record(packet)`, raw sources and the raw native I/O in `FULL_PRE_EFFECT_BOUNDARY`;
     - keeps `collapse_packet`/`collapse_values` byte-compatible for the broker.
   - The root route keeps `DISPATCH_INTENT` in its `EFFECT_INTENT` boundaries.
6. **Successor slices with the same pattern:**
   - a scoped `Canonical_Exchange` input for the broker (`collapse.commit`);
   - a scoped owner-completion (K4) input.

**Invariants.**
- **I1.1** No run-time projection of scoped state into `L.Ledger_State`. `Proj` is Ghost-only.
- **I1.2** Every original clause appears literally (C1, C3, C4) or as a lifted predicate with a proved
  refinement on the original domain (C2).
- **I1.3** The decision type and caller obedience are unchanged: only `Ready` proceeds, and every
  other value refuses with the original named code.
- **I1.4** Exactly one use: `RESERVED_NEW` at reserve and one `RESERVED_REPLAY` before
  `EFFECT_INTENT`. No second grant or use.
- **I1.5** Every identity pair is fed from two independent producers (OB-030).

**Decisions requested.**
- **D-1a** Is the C2 lift faithful? In particular, consider the projected-charge rounding
  (`numerator/denominator`) in `S.Contained` against `L.Contained`'s raw amounts.
- **D-1b** For a fresh pre-effect, should `Rows(I).Scope = State.Current` be required, or is the
  epoch equality sufficient after a context rollover between reserve and pre-effect?

**Dependencies.**
- SL-0 (P0-1, P0-2).
- Seam 7, for plan and policy.
- C-API design v3 (A1).
- D1/D2 native Big_Integer cost designs, because the new unit uses `SPARK.Big_Integers`.
- The F8-successor formal frame, for proof credit.

**Authority.**
- Lead-only source work: the spec, bodies, wrapper, caller branch and value fixtures.
- Proof credit needs the admitted strict frame. The lead's STATUS records that frame as BLOCKED, and
  W-1 awaits an operator decision.
- Runtime positives need a root lab (operator).

**Additive controls.**
- Pure native value fixtures (Ada `-gnata`, like `operation_authority_controls`):
  - each clause mutated → its exact named decision;
  - every original `Canonical_Operation` fixture vector, embedded single-frame → the same decision;
  - multi-frame and multi-bucket vectors: stale scope, a parent row missing, bucket conservation off
    by one unit → `Resource_Refused`.
- An ABI layout test per field.
- A mutant body dropping a clause → the proof gate fails (pins + `REQUIRED_PROVED`).
- In the lab: a scoped positive operation on both the serial and the root route, plus the RC
  grant-refusal set.

**Risks.**
- The C2 refinement may not prove as stated. Then the scoped predicate changes, never the original.
- Quantified-roster proof cost.
- ABI churn with C-API v3.

**Size.** L. XL with the exchange and K4 successors.

### Seam 2 — Startup and provisioning correspondence

**Current draft state.**
- `rw/protected_startup.py:467-472`: `reconcile_admission` unconditionally raises
  `StartupRefusal('PROTECTED_FULL_LEDGER_STARTUP_RECONCILER_UNAVAILABLE')`.
  - `StartupRefusal` is a `RuntimeError` (`:26`), so `RuntimeController`'s
    `except WorldlineError` (`rw/controller.py:174-183`) does not catch it.
  - `construct()` (`:660-712`) therefore fails for:
    - the front (`rw/protected_root_endpoint.py:14`);
    - the worker (`R/protected-root/worker_entry.py:28`);
    - the collector reconstruction (`rw/root_worker_closed.py:138`).
  - `serve()` falls back to quarantined diagnostics (`:799-812`).
- Nothing calls `attach_scoped_resource` (P0-4). Front and worker both require
  `controller.protected_resources` to be exactly `ProtectedScopedResourcePrincipal`
  (`protected_root_endpoint.py:15-17`; `worker_entry.py:29-31`). Only
  `ProtectedScopedResourcePrincipal.reconcile(controller)` sets it
  (`rw/protected_scoped_resource_runtime.py:611-622`).
- The runtime descriptor key set is exact (`rw/protected_startup.py:264-268`;
  `R/protected-startup/protected-startup-v1.schema.json` runtime `additionalProperties:false`). It
  rejects `runtime['resource_scoped_producer']`, which `:54` reads.
- The root custody journal (`rw/root_worker_journal.py`) needs pre-existing material:
  - the owner genesis file `worldline.owner-provisioned-root-custody-v1` (`:37-49`);
  - the issuer key digest (`:50-53`);
  - the database path listed in `provisioned_state` (`:54-55`);
  - a database whose tables match column (name, type) only (`:85-92`). There is no
    `sqlite_master.sql`, PK, NOT NULL, CHECK or UNIQUE verification.
  - a genesis row and a MAC'd head (`:93-114`).
  - The genesis `initial_event` field is required but unused by `_load`.
- No provisioner exists, and there is no schema for `worldline.protected-root-worker-plan-v1` or for
  the custody genesis.
- The frontier control asserts the gap (`R/protected-startup/controls/test_protected_startup_v1.py:97-105`).

**Original requirement (quoted).**
- RW:29: "Scoped construction and runtime descriptor fields require an explicit exact
  schema/installation/provisioning union. … its genuine first-provision construction, complete DDL
  constraints, admission/initial head and one-shot custody source are not finished. Never bypass
  startup or initialize missing prior state."
- P1:99: "The full ledger startup reconciler still needs genuine accepted behavior. Missing prior
  journals/keys/history must not silently create new Genesis or reset custody."
- P1:149: "Implement genuine startup and owner provision without recreating missing history."
- OB-202: "The daemon always starts and runs recovery".
- OB-146: a durable quarantine cleared only by a recorded owner action.
- OB-051: fails closed when the ledger is missing.
- OB-185: reconciliation resumes authorized progress.
- OB-055, OB-070, OB-067.
- RC:
  - "operation journal deletion before/after intent refuses without reinitialization";
  - "authentic initial empty store and actual later PRIME context progression";
  - "operation mutation partial DB/file/bootstrap crash retains diagnosis".

**Design direction.**
1. **Versioned descriptor successor**, as an exact union: `worldline.protected-startup-v2`.
   - Runtime keys are the original nine plus `resource_scoped_producer`.
   - `tools` includes `resource_supervisor_v3`, `bwrap`, `systemctl` and `systemd_run`.
   - `provisioned_state` includes the root-worker owner plan, the operation crosswalk (seam 7), the
     custody genesis, and the custody database and lock.
   - The early envelope selects `/usr/include/asm-generic/socket.h` as DATA.
   - The version is selected by the exact `schema` value. v1 descriptors keep their exact accepted
     behavior, and nothing is defaulted between versions.
2. **One `attach_scoped_resource`** that keeps the stricter exact-producer check (P0-4). `construct()`
   calls it after `StateStore` and before `RuntimeController`, only for v2.
3. **A genuine full-ledger startup reconciler** behind `reconcile_admission`. This is not the
   historical selected-row reconcile.
   1. Native whole-snapshot `validate` must return `CONSISTENT_SNAPSHOT`.
   2. Each non-terminal row is classified from the durable launch journal, the root custody journal
      (CLOSED witnesses, UNKNOWN, phase rows; see seam 9), current manager and cgroup facts, and
      transferred-slot custody (seam 3).
   3. Every transition goes through native scoped Check:
      - authentic CLOSED witness → `RECORD_TERMINAL` → `RELEASE_HOLD` or `CHARGE_BUDGET`;
      - durably proven `NEVER_LAUNCHED` → `RELEASE_HOLD`;
      - otherwise → `RETAIN_UNCERTAIN` / `SETTLEMENT_UNKNOWN`, with holds kept.
   4. Operations left `WORKER_OWNED` by a dead daemon become durable `QUARANTINED`. Owner resolution
      (K4) clears them.
   5. The daemon always starts. A reconciler refusal becomes a named diagnostic state; nothing
      fabricates success.
4. **An offline one-shot custody provisioner** for the operator, run as root. It is modelled on
   `R/protected-canonical/provision_operation_head.py`, `operation_head_schema.sql` and
   `_offline_operation_slot` (`rw/protected_startup.py:328-355`).
   - It requires the exact selected ENTRY and a declared creation slot.
   - It creates the database exclusively, with full DDL constraints:
     - `PRIMARY KEY`, `NOT NULL`, `CHECK(kind IN …)`;
     - a UNIQUE `event_id`;
     - a single-row head.
   - Admission goes `UNUSED → INTENT → CONSUMED` with the owner envelope.
   - It writes a MAC'd genesis row. The initial head binds `initial_event`.
   - It fsyncs the file and the directory.
   - At run time the database is opened `mode=rw` only, and the complete `sqlite_master.sql` text is
     verified as well as the columns.
5. **An owner-plan JSON schema and a per-operation crosswalk schema** (seam 7), bound in the
   descriptor's `files`.
6. **Frontier control.** The bytes of `test_current_source_frontier_names_full_ledger_startup_gap`
   are retained as history. It is superseded only by a reviewed successor that keeps every negative
   (missing journal, key, genesis or head refuses with nothing created; unknown rows are kept) and
   adds the genuine positive. The supersession needs explicit GPT-6.1 review and lead adoption.

**Invariants.**
- **I2.1** No startup path creates schema, key, genesis, lock, head or history. Absence refuses by name.
- **I2.2** Exactly one provisioning entry may create the custody database, once, under the exact
  ENTRY and creation slot.
- **I2.3** Nothing is released or charged without an authentic CLOSED witness or a durable
  `NEVER_LAUNCHED` proof, decided natively.
- **I2.4** The daemon always starts, and recovery runs before any consequential request is served.
- **I2.5** v1 descriptors and controls keep their exact behavior.

**Decisions requested.**
- **D-2a** v2 descriptor versus an exact union inside v1.
- **D-2b** Retirement procedure for the frontier control.

**Dependencies.**
- SL-0.
- Seam 9: the crash-point table and the phase rows.
- Seam 3: slots inside the reconcile.
- Seam 7: the schemas.

**Authority.**
- Lead-only: the schemas, provisioner source, reconciler source and attach wiring.
- Operator: running the provisioner, creating or using a `/srv` lab installation, and every startup
  control. All need root (`rw/protected_startup.py:153`; `GATE:157`).

**Additive controls.** All of these run in the lab.
- Positive v2 startup.
- A missing journal, genesis, key or head refuses, with inode and bytes unchanged before and after.
- A second provisioner run refuses.
- DDL constraint violations are rejected.
- A crash between `INTENT` and `CONSUMED` resolves without reinitialization.
- A restart with prior LIVE or UNKNOWN rows keeps the holds.
- The OB-202 analog: a hung or missing `systemctl` still lets the daemon start.
- v1 descriptor parity.

**Risks.** This changes a reviewed startup component. Mixed v1/v2 history. Root only.

**Size.** L.

### Seam 3 — Other-LIVE resource ownership and custody

**Current draft state.**
- The intake refuses any other LIVE reservation: `rw/protected_root_observation.py:122-127`,
  `ROOT_CAPTURE_OTHER_LIVE_OWNED_DESCRIPTOR_ROSTER_UNAVAILABLE`.
- The front refuses to relinquish in two cases:
  - while any other slot is live (`rw/protected_root_resource.py:156-157`);
  - while daemon background tasks exist or acquisitions are not quiescent
    (`rw/protected_root_worker.py:139-143`).
- In the worker, the fresh scoped producer has no `slots` entry even for its own root:
  - `_capture` (`rw/protected_scoped_resource_runtime.py:227-250`) finds no slot, so the physical
    phase is UNAVAILABLE;
  - `_retained_closed` finds no witness, so the row is `UNKNOWN`;
  - `RootControllerCapture._current` (`rw/protected_root_observation.py:50-97`) uses that packet;
  - `Root_Controller_Holds` requires `Observed = L.Live`
    (`core/worldline-resource_child_execution.ads:71-87`);
  - so the worker's admission refuses (`R/protected-root/worker_entry.py:39-40`).
- Only `_before_constructors` injects physical facts, and only for the root row (`:131-142`).

**Original requirement (quoted).**
- RW:30: "Preserve every row, originating context, observed descriptor and retained custody; this
  refusal is an engineering gap, not a domain exception."
- P1:127: "Full other-LIVE reservation custody, unknown charges, exact lost-response replay, legal
  subsequent lifecycle steps, owner Retry/Adopt/quarantine and startup reconciliation remain
  required."
- OB-176, OB-211.
- RC: "unknown dispatch and mapping retain full held resource/use and quarantine"; "real all-child
  resource launch/Running/terminal/release/charge lineage".

**Design direction.**
1. **Typed slot-custody roster in the custody frame.**
   - It covers every non-terminal reservation that has an owned slot (actor V3 slots and the root
     slot itself).
   - Descriptors transferred: supervisor channel, helper/namespace/actor pidfds, namespace fd,
     credential receiver, stdin writer if open, and raw-output drain ownership.
   - Each slot also carries its `HELD`, `RUNNING` and `EXECUTION` events and its dispatch.
2. **Worker-side `TransferredSlot`** (a new exact type) registered in `producer.slots`.
   - `observe()` reads through the transferred `host_proc`.
   - Facts are computed exactly as the front computes them. Classification comes only from native
     scoped `Classify`.
3. **Raw drains.** Each pipe read end has exactly one owner at a time, moved by a durable
   `DRAIN_TRANSFER` record that holds a byte offset. No byte is lost or double-read.
4. **Symmetric return of slot custody** to the reconstructed front at closure, through the
   `ClosedFrontEscrow` roster.
5. **Relinquish rule.** The front's refusals become "every live slot is in the transfer roster". A
   live slot that cannot be transferred keeps the named refusal, and the obligation stays OPEN.

**Invariants.**
- **I3.1** One durable owner per live slot. Ownership changes are journaled before descriptors move.
- **I3.2** Classification comes only from native `Classify` over fresh facts read through owned,
  re-identified descriptors (dev/ino/fdinfo).
- **I3.3** Transfer never relabels a row LIVE, REAPED or RELEASED. UNKNOWN stays UNKNOWN, with holds.
- **I3.4** Exactly one drain owner, and no byte loss.

**Decision requested.**
- **D-3a** Transfer actor V3 slots into the worker, or require their prior terminal state? The second
  option would refuse an original accepted case (a consequential operation while a fork job runs), so
  this design proposes transfer.

**Dependencies.** SL-0; seams 9, 4, 5 and 8 (receive ordering).

**Authority.** Source is lead-only. The demonstration needs live actors and a root worker (operator, lab).

**Additive controls.**
- Handoff while an actor is LIVE → the actor is classified LIVE in the worker and its terminal is
  collected.
- An actor that is UNKNOWN → it stays held.
- A substituted pidfd is refused.
- Drain continuity: complete bytes across the transfer.
- The root's own row is LIVE through its transferred slot, and UNKNOWN when its namespace pidfd is
  terminal.

**Risks.** asyncio transport handover. Descriptor limits: these must be observed, and no new caps
may be added.

**Size.** L.

### Seam 4 — Live request multiplexing

**Current draft state.**
- Every non-owner operation is routed to the root worker under `operation_lock`
  (`rw/protected_operations.py:716-726`). The operation roster `OPS` includes `ping`, `status`,
  `list`, `show` and `job.cancel` (`rw/operation_authority_kernel.py:8`).
- The router (`rw/root_worker_endpoint_router.py:19-34`):
  - refuses when no collector exists (`:24`);
  - otherwise awaits every collector while holding its lock (`:20-25`).
  - So `status` and `job.cancel` wait for closure.
- `rw/protected_root_worker.py:191-199`: any exception after `_reserve` sets
  `UNKNOWN_WORKER_OWNERSHIP` (`:192`), including a legitimate native pre-effect denial before any
  launch.
  - The `elif` at `:195` is always true.
  - Every later `invoke` then refuses (`:159`), and the router refuses everything because no
    collector exists. The endpoint is wedged, owner resolution included.
  - This contradicts the original `_invoke_serial`, where `quarantine.resolve` stays reachable (`:730`).
- P0-5 also applies.

**Original requirement (quoted).**
- RW:31: "The original concurrent/status/new-request cases require fresh original client socket/raw
  request transferred to the actual live owner, independent fresh native grant/use/current
  admission, full durable per-request lifetime and correct response/progress ownership. Waiting
  forever or authorizing through the first root grant is not acceptable."
- P1:115.
- OB-158 and OB-163: the event loop is never blocked.
- OB-186: "One requester cannot deny service to another, and every create resolves to a definite state."
- RC: "concurrent intents cannot borrow one available use".

**Design direction.**
1. **One Store owner, front XOR worker**, held by the custody phase machine (seam 9).
2. **Pre-dispatch refusals keep `FRONT_OWNED`.** A refusal before `offer.transfer()` follows the
   original `_invoke_serial` semantics: `quarantine()` of the reserved use and the unresolved-use
   gate. Owner routes stay reachable.
3. **Durable request transfer while a worker owns state.**
   1. The front appends `REQUEST_TRANSFER_INTENT` (full raw line, original host observation, socket
      identity).
   2. It sends the client socket FD and a sealed memfd.
   3. The worker appends `REQUEST_INTAKE` (a CAS against the intent; seam 9) and acknowledges.
   4. The front closes its copy only after the durable intake.
   5. A lost ACK is resolved from the journal: exactly once, never dropped, never dispatched twice.
4. **Worker request loop with the original `_dispatch_line` semantics**, using the crosswalk peer
   from seam 8.
   - Each consequential request gets its own `_reserve` → scoped pre-effect (seam 1) →
     `EFFECT_INTENT`, under the worker principal's original `operation_lock`.
   - Read-only operations are answered from the live owners.
   - `job.cancel` reaches worker-owned jobs.
   - Responses and progress are written only by the worker, on the transferred socket.
5. **Physical accounting for requests executed inside the live coordinator.** Decision D-4a covers
   three options:
   - **(A)** A contained child hold of the live root reservation. The parent is the root
     reservation and the physical container is the root cgroup. `Parent_Supports`/`Contained` apply
     natively, and the cost comes from the request's own crosswalk plan (seam 7). An over-capacity
     request is refused natively, never by a Python cap.
   - **(B)** A per-request ownership-handoff chain.
   - **(C)** One long-lived coordinator with nested per-request units.
   - The recommendation, for review, is (A). It keeps one Store owner and the original serialization
     without inventing costs. It needs reviewed native grammar for an in-coordinator hold that is
     neither an actor child nor a copied readiness flag.
6. **Worker lifetime.** The worker closes only when no requests are in flight, no detached tasks
   remain and no child holds are live.
   - Requests that arrive during `TRANSFER_PENDING` or `RECONSTRUCTING` are durably queued and
     dispatched to the next live owner.
   - Only ownership `UNKNOWN` yields a named refusal for ordinary routes, as the original unresolved
     gate does.
   - Owner routes (`owner.retry`/`adopt`/`recover`, `quarantine.resolve`) are forwarded to the
     current owner in every phase.
7. **No `await gather(collectors)` under the router lock.** The event loop never blocks.

**Invariants.**
- **I4.1** A single Store owner.
- **I4.2** Fresh native admission per request, and no borrowed use.
- **I4.3** Exactly-once durable transfer.
- **I4.4** Response and progress belong to the admitting owner.
- **I4.5** The worker closes only after everything it owns is terminal.
- **I4.6** A pre-dispatch refusal never changes ownership.
- **I4.7** Owner resolution is reachable in every phase.
- **I4.8** The original pre-dispatch guards (P0-5) are preserved.

**Decision requested.** D-4a, above.

**Dependencies.** Seams 1, 3, 5, 8 and 9; SL-0.

**Authority.** Source is lead-only. Demonstration is in the lab (operator).

**Additive controls.**
- `status`, `list` and `show` are answered within a bound during a long detached fork or race.
- `job.cancel` of a worker-owned job.
- A second consequential operation while the first one's detached job runs gets its own
  `RESERVED_NEW`, pre-effect and `EFFECT_INTENT`.
- Two concurrent intents on a grant with one remaining use: exactly one succeeds, natively (RC).
- A pre-effect denial keeps `FRONT_OWNED`, and `quarantine.resolve` succeeds.
- A lost transfer ACK is handled exactly once.
- An owner operation during `WORKER_OWNED`.

**Risks.** The largest seam. Fairness under OB-186 may use only original policy.

**Size.** XL.

### Seam 5 — Dynamic original child dispatch

**Current draft state.**
- `ResourceChildExecutionKernel.task_reservation` and `.child` (`rw/resource_child_execution.py:203-205`)
  have no caller.
- The owner plan requires `child_dispatch` (`rw/protected_root_worker.py:100`), but nothing consumes it.
- The runner captures the complete workload (`rw/runner.py:649-656`) and then launches a sibling
  transient unit under the legacy guard (`:693-704`).
- The root route lacks the workload refusal (P0-5).
- The root unit is forced to `Delegate=no` (`rw/protected_root_resource.py:70`; HELD check
  `rw/protected_root_supervisor.py:116`). So no nested cgroup is possible.
- Follow-up rights raise `OPERATION_SCOPED_FOLLOWUP_DISPATCH_UNAVAILABLE` (`rw/canonical_followup.py:95`).
- The child authority review lists, among its physical controls: "current V3 helper lacks it and
  cannot establish parent task positive"
  (`W/work/resource-child-authority-source-v1/review/gpt61-v1/review.json`).

**Original requirement (quoted).**
- RW:32: "Wire the actual AgentRunner/Codex adapter/SandboxSpec/whole mission/stdin/EOF/argv/env/context/world/instance/check/finalization
  path to a distinct conserved child hold and actual nested namespace/cgroup parent. … Preserve the
  exact original Parent_Supports and Original_Holds. No child-as-root, sibling-unit ancestry claim,
  copied ready flag, extra capability use or static root plan is valid."
- P1:97 on the grammar: "distinct operation/reservation identities do not justify inventing workload
  inequality".
- ROADMAP:108.
- OB-066, OB-069, OB-010, OB-011, OB-134, OB-020.
- RC:
  - "all original fork/race/simulate/ghost/prune/revalidate accepted controls";
  - "original detached and race child holds retain root grant/use/request/causal relation without
    extra use";
  - "owner-authorized services/terminals/windows/automatic ghosts through same full grant/use".

**Design direction.**
1. **Interim.** On the root route, workload operations keep the existing named OPEN refusal (P0-5).
   Their positive controls stay required, and this is not an accepted refusal.
2. **A worker-side child dispatcher** replaces the runner's launch only under the root worker. The
   runner's capture is unchanged.
   1. **Durable TaskIntent.** It holds the task id, the complete original workload capture (adapter,
      context, SandboxSpec, argv, mission, stdin and EOF, env, world, instance, check, finalization),
      the world ancestry and the child plan (seam 7).
   2. **Child RESERVE.**
      - `new_row.parent` is the root reservation.
      - `operation` is the task id, which differs from the root operation. The reservation differs too.
      - capability, grant_use, owner and provenance are the root's.
      - workload follows the original grammar, with no fabricated inequality.
   3. **Native `task_reservation`** (`Task_Admission`: `S.Check` ∧ `Task_Request_Holds`, no extra A
      use) → scoped commit.
   4. **Physical nesting (D-5a).**
      - The root unit is `Delegate=yes`, with the coordinator moved into a leaf.
      - The child is spawned into a per-task cgroup under the root subtree (`clone3` with
        `CLONE_INTO_CGROUP`) **[unverified reasoning on cgroup v2 rules]**.
      - Child limits come from the child reservation through the crosswalk, and are read back from
        the kernel.
      - The HELD delegation check becomes an exact expected state from the owner plan.
   5. **Successor actor helper (V4).** It takes an authenticated parent namespace FD and creates a
      nested PID namespace. `NS_GET_PARENT` and pidfd observations feed `Namespace_Ancestry` and
      `Process_Ancestry`.
   6. **Before exec:**
      1. actor credential measurement;
      2. `K.Check` plus the native `child` decision `Child_Ready_Conjunction`, i.e. `K.Check` ∧
         `Parent_Holds` ∧ `Child_Holds` ∧ `Process_Ancestry` ∧ `Namespace_Ancestry`
         (`core/worldline-resource_child_execution.ads:194-208`);
      3. a durable witness, then ACK, then GO;
      4. the original stdin/EOF pump (actor stdin V4).
   7. **Closure.**
      - The child gets nested CLOSED/ECHILD, outer waits, raw drains, then `RECORD_TERMINAL` and
        release or charge.
      - The root settles only after every child is terminal. An unknown child keeps the root held.
   8. **Follow-up rights** go through the same path, using the broker's follow-up plans
      (`rw/canonical_full_broker.py:202-217`).
3. **Race:** three children under one root, with the same grant and use.

**Invariants.**
- **I5.1** No child runs without an active child reservation whose parent is the live root
  reservation (`Parent_Supports`, `Contained`).
- **I5.2** Children use no extra A use.
- **I5.3** Physical ancestry is decided natively from kernel observations.
- **I5.4** The coordinator never receives confined-actor K.Check credit. Actors never receive root
  rights or custody FDs.
- **I5.5** Root closure and settlement wait for every child.
- **I5.6** Original adapter, argv, env, stdin and EOF bytes are unchanged.

**Decisions requested.**
- **D-5a** The delegation model. Its security analysis covers the coordinator's inability to raise
  its own limits.
- **D-5b** The helper successor versus extending V3.

**Dependencies.**
- Seams 1, 3, 4, 7 and 9.
- The child authority secondary. Its controls are UNBUILT/UNRUN.
- Actor stdin V4; SL-0.

**Authority.**
- Lead-only: dispatcher and helper source.
- Operator: the root lab, systemd delegation, and model quota.
- Real actors may only be the WORLDLINE actor, `gpt-6-luna` with high reasoning, inside a world
  through the existing Codex adapter.

**Additive controls.**
- Every original fork, race, simulate, ghost, prune and revalidate accepted control on the root
  route (lab).
- Refusals: a child with a different capability or use, a sibling unit, a missing parent namespace,
  a stale TaskIntent, a copied ready flag.
- A child OOM is contained and is non-PASS (OB-020).
- An unknown child keeps the root held.
- A race with three children.
- Follow-up rights positive and denied. A committed return without post rights stays COMMITTED with
  `effectsSkipped`.

**Risks.**
- Delegation is a security-sensitive change.
- bwrap under a nested PID namespace with `/proc` remounted.
- Unproved privileged C helper.
- Model quota.

**Size.** XL.

### Seam 6 — Canonical committed outcome versus physical closure

**Current draft state.**
- The worker defers physical settlement (`rw/protected_root_worker.py:292-304`). But the commit path
  settles anyway:
  - `collapse.commit` → `controller._collapse_commit` (`rw/controller.py:680-699`) →
    `broker().commit` → `after_committed` (`rw/canonical_followup.py:72`) → `p.finish`
    (`:84`; `rw/protected_operations.py:778-811`).
  - `finish` runs `OBSERVE_EFFECT` and then `settle_historical` (`:805`) while the root is LIVE.
- Scoped `settle_historical` needs `principal.resource_scoped_historical_settlement`
  (`rw/protected_scoped_resource_runtime.py:530-531`), `resource_scoped_historical_lifecycle_binding`
  (`:548`) and `resource_scoped_owner_resolution_material` (`:571`).
  - None of the three is defined anywhere in the lane; grep finds only the `getattr` sites.
  - The refusal surfaces in the handler, and the worker's `except` path calls `p.quarantine` on an
    operation whose exchange already committed (`rw/protected_root_worker.py:306-308`).
- The collector passes the worker's later `result_capture` to `finish`
  (`rw/root_worker_closed.py:150-151`). `finish` requires it to equal the retained `RESULT_CAPTURE`
  (`rw/protected_operations.py:780-781`). A mismatch is expected, because `after_committed` stored an
  earlier capture.

**Original requirement (quoted).**
- RW:33: "An original broker's finish/posteffect call while the coordinator is LIVE must retain its
  genuine canonical effect/receipt/cause and per-right outcomes, defer physical root settlement to
  the authenticated CLOSED collector, and preserve historic settlement under fresh denial."
- P1:115: "handler return or EOF is not physical closure."
- P1:149.
- OB-076, OB-049, OB-095, OB-197.
- RC:
  - "historical committed settlement after current deny/revocation without new use/exchange/socket";
  - "lost result ACK and lost resource settlement ACK exactly same operation";
  - "committed return lacking post rights stays COMMITTED with effects skipped".

**Design direction.**
1. **Split `finish` into two named phases.**
   - `observe_committed_effect`:
     - `RESULT_CAPTURE` is write-once; later captures become additive report boundaries;
     - canonical effect, receipts and causal chain;
     - native `OBSERVE_EFFECT` → `EFFECT_OBSERVED`;
     - per-right follow-up outcomes.
   - `settle_physical`:
     - authentic physical terminal (CLOSED witness → REAPED → `RECORD_TERMINAL` → release or charge);
     - then `settle_historical` → native `SETTLE_USE` → `SETTLED`.
   - The serial path runs both in sequence and keeps its exact semantics.
2. **Root-worker LIVE mode.** The `OperationScope` carries the typed `RootWorkerProcess` owner.
   - `after_committed` runs only `observe_committed_effect` and records
     `ROOT_PHYSICAL_SETTLEMENT_DEFERRED`.
   - A committed effect is never quarantined for lack of physical closure.
3. **The three scoped historical adapters**, built from committed scoped history and the retained
   original capture, with no fresh peer, grant or exchange. They mirror the originals:
   `resource_historical_settlement` (`:505-520`), `resource_historical_lifecycle_binding` (`:572-584`)
   and `resource_owner_resolution_material` (`:852-897`).
4. **The collector** runs `settle_physical` against the retained `RESULT_CAPTURE` after the CLOSED
   witness.
5. **Ordering:** child holds settle before the root (seam 5).

**Invariants.**
- **I6.1** A committed canonical effect is never demoted to QUARANTINED or aborted by a gap in
  physical settlement.
- **I6.2** Release or charge happens only from a native REAPED classification over an authentic CLOSED.
- **I6.3** Historical settlement needs no live client or new use, and works after current denial.
- **I6.4** `RESULT_CAPTURE` is write-once.
- **I6.5** Serial-path behavior is unchanged.

**Decision requested.**
- **D-6a** The QUARANTINE semantics when canonical `EFFECT_OBSERVED` exists but physical settlement
  is UNKNOWN: retain at `EFFECT_OBSERVED` and route to K4, versus the native `QUARANTINE_USE`
  decision domain.

**Dependencies.** Seams 1 (scoped exchange and K4), 2, 5 and 9; the A1 scoped committed envelope.

**Authority.** Source is lead-only. Demonstration is in the lab.

**Additive controls.**
- Commit through the worker: `EFFECT_OBSERVED` while LIVE, `SETTLED` after CLOSED.
- Revoke after commit and before CLOSED: settlement still succeeds without a new use.
- Lost result ACK and lost settlement ACK.
- A committed return without post rights.
- Worker crash after commit: `EFFECT_OBSERVED` retained, physical UNKNOWN held, K4 available.

**Risks.** Every protected operation goes through `finish`. The serial controls must be re-run on
matching source.

**Size.** L.

### Seam 7 — Root plan cost and source crosswalk

**Current draft state.**
- One owner plan serves every operation (`rw/protected_root_worker.py:97-104`), with one `cost_key`,
  one `worker_policy` and one `child_dispatch`.
- `handler_plan` derives argv and unit properties from `worker_policy` for every operation
  (`rw/root_worker_plan.py:13-38`).
- Launch refuses unless the root `cost_key` equals the operation's
  (`rw/protected_root_resource.py:39-41`, `ROOT_RESOURCE_OWNER_OPERATION_COST_CROSSWALK_UNAVAILABLE`).
- The reservation amount comes from the operation's `cost_key`
  (`rw/protected_scoped_resource_runtime.py:391-392`), while enforcement comes from `worker_policy`.
  No native containment relates the two.
- Policy is split between pre-effect and machine admission (seam 1).
- **The RootController identity pairs are equal by construction**
  (`rw/protected_root_observation.py:36-49`). Each of these is filled from the same Python value as
  its `expected_*` partner:
  - `owner_endpoint`;
  - `source_lease`;
  - `worker_image`;
  - `handler_plan`;
  - `running_event`;
  - `store_genesis`.

  The process `source_lease` is caller-supplied the same way (`:74-76`, `:121`). The native
  `Controller_Valid` equalities are therefore vacuous (OB-030).
- `SO_PEERPIDFD` requires the header to be selected as DATA (`rw/root_worker_host_peer.py:14-17,32-33`).
  The `#define SO_PEERPIDFD 77` was observed in that header; the Python stdlib does not expose it.

**Original requirement (quoted).**
- RW:34: "One cost_key may not represent every original operation/owner case. … must all be joined
  faithfully without altering accepted domains or inventing physical costs."
- P1:107: "caller-filled equal bytes alone are insufficient."
- P1:129: "Do not add a domain cap".
- OB-030, OB-035, OB-039, OB-056, OB-122, OB-174, OB-211.
- RC: "full operation-policy versus resource-policy and Root_Set versus scoped Root_Head source-proven
  native crosswalk".

**Design direction.**
1. **Owner-provisioned per-operation table**, `worldline.protected-root-operation-crosswalk-v1`, bound
   by the descriptor and the early envelope.
   - It covers every original operation, owner operation and follow-up right.
   - Each entry holds:
     - the original plan digest (`cost_key`, `parent`, `launch`);
     - the coordinator plan: entry, envelope, interpreter, loader, argv template and coordinator
       `worker_policy`;
     - the helper image digest;
     - child adapter plans;
     - the physical catalogue key;
     - header DATA selections.
   - There is exactly one entry per operation. Absence refuses by name and is never defaulted.
2. **One source of plan truth.** Pre-effect, `launch_root_worker`, `resource_launch_material` and
   machine admission all read the same entry.
3. **Native containment predicate (additive SPARK).** The reserved kind, amount and `cost_key` must
   match the catalogue cost. The enforced unit limits, read back from the manager, must not exceed
   the reserved projection.
4. **Independent producers for every pair, under per-pair source domain tags:**

   | Field | Observed side | Expected side |
   |---|---|---|
   | endpoint | bound listener identity (`principal.endpoint_identity`) | descriptor DATA |
   | source_lease | executed-code `source_lease.check()` | owner plan source roster |
   | worker_image | `/proc/<helper>/exe` bytes through `host_proc` | crosswalk helper digest |
   | handler_plan | observed worker cmdline and exe | crosswalk coordinator plan |
   | running_event | root custody journal `RUNNING` | scoped history `RECORD_RUNNING` |
   | store_genesis | StateStore meta | `lease.genesis` |

5. **Header DATA selection**, with `SO_PEERPIDFD` kernel support observed at run time. An unsupported
   kernel refuses.

**Invariants.**
- **I7.1** One entry per operation, and no default.
- **I7.2** All plan, policy and cost consumers read that one entry.
- **I7.3** Enforced limits are natively contained in the reservation.
- **I7.4** Every pair comes from two producers with distinct tags.
- **I7.5** No physical cost is invented.

**Decision requested.**
- **D-7a** Should the RootController grammar change (a native ABI change requiring child-authority
  re-review), or should independent sourcing alone close the vacuity?

**Dependencies.** Seam 2 (schema and provisioning); seams 1 and 5; the D1/D2 cost designs; OB-174.

**Authority.** The schema and predicate are lead-only. Provisioning the table is operator work.

**Additive controls.**
- Corrupt one producer → `CONTROLLER_REFUSED`.
- The same value copied to both sides → refused.
- An operation without an entry → named refusal.
- Two operations with different cost keys both dispatch.
- Enforced `MemoryMax` above the reservation → refused.
- A changed header digest → refused.

**Risks.** The owner provisioning burden. Possible child ABI change.

**Size.** M.

### Seam 8 — Requester PID-namespace credential join

**Current draft state.**
- The helper unshares `CLONE_NEWPID` (`R/protected-root/native_root_worker_supervisor_v1.c:336`).
  Its namespace init unshares `CLONE_NEWNS`, makes `/` private and mounts a new `/proc` (`:257-258`).
  The worker is exec'd inside (`:291`). No user namespace is created.
- `CustodyReceipt.receive` (`rw/root_worker_custody.py:165-213`) builds the peer too early:
  1. it receives the original client socket at `:183`;
  2. it immediately builds `KernelPeer.capture_descriptor` and `RequestPeer(peer, frame['original_request'])`
     (`:184-185`);
  3. only afterwards does it receive `host_proc` and the pidfds (`:195-204`).
- `KernelPeer._read` re-reads `SO_PEERCRED` (`rw/client_peer.py:73-84`). `RequestPeer.__init__`
  requires the retained document's peer to equal the current reading (`:110-117`).
- **[unverified reasoning]** A peer outside the reader's active PID namespace reads PID 0. The helper
  comment at `.c:125-128` says the same for its custody sender. So every worker intake raises
  `PEER_REQUEST_MISMATCH`.
- `root_worker_host_peer.py` corrects only the supervisor-channel peer (RW:35).
- Exact-type `RequestPeer` gates exist in 11 modules (observed grep).
- The original requester UID domain includes 0. The OS producer V2 review says: "requester UID
  remains independent and can be configured zero".

**Original requirement (quoted).**
- RW:35: "Implement a genuine socket/host observation crosswalk retaining raw relative and original
  observed host credential bytes, actual socket identity and complete UID/GID domain. Do not trust a
  sender PID label, falsify linux.SO_PEERCRED bytes, or require a still-live original client for
  historical settlement."
- P1:137: "Complete real OS-principal/endpoint/owned-descriptor/native capture to kernel
  correspondence at the state transition."
- OB-023, OB-110, OB-092.
- RC:
  - "full UID/GID domain and same UID new process commit";
  - "foreign UID and delegated socket no extra rights";
  - "prepare versus commit actual peer/transaction joins".

**Design direction.**
1. **Receive the complete roster before building any peer.** That is the frame, socket, locks and
   origins, including a new optional `requester_pidfd`. On any failure, close everything.
2. **Front-side source record at transfer time.** It holds:
   - the original document, unchanged;
   - the front's fresh host `SO_PEERCRED` bytes;
   - the socket identity;
   - a requester pidfd taken with `SO_PEERPIDFD`, with its raw host fdinfo, or an explicit
     `UNAVAILABLE` with errno;
   - the front's PID-namespace and user-namespace identities.

   The original observation schema is unchanged (`worldline.client-request-observation-v1`). The new
   record is a separate, additive record.
3. **A new exact type `CrosswalkRequestPeer`.** It deliberately does not subclass `KernelPeer`: a
   subclass that returns retained bytes from `observation()` would relabel a retained record as a
   fresh kernel read.
   - It retains the raw relative ucred bytes exactly, and the original host document, never
     re-synthesized.
   - Mandatory checks:
     - socket `fstat` dev/ino/mode equals the original `socketIdentity` (same OFD);
     - relative UID/GID equals the original;
     - the worker's `/proc/self/ns/user` identity equals the front's.
   - The relative PID is recorded uninterpreted.
   - Host-PID evidence comes only from the requester pidfd through the transferred `host_proc`
     fdinfo, and must equal the original PID. Missing evidence is recorded, never synthesized.
   - `observation()` returns the original document only while the mandatory checks hold.
     `crosswalk_record()` is journaled at intake.
4. **Two modes.**
   - FRESH, for admission and handler execution, needs the live transferred socket.
   - HISTORICAL, for settlement and recovery, uses only authenticated retained records, needs no live
     client, and grants no new use or exchange. This matches the OS V2 review's historical-settlement
     route.
5. **Gate updates.** Each of the exact-type gates is updated explicitly, to the accepted type set for
   its context. Each change is enumerated for review. Outside worker custody, none admits the
   crosswalk peer.
6. **Native.** `requester_uid`/`requester_gid` stay sourced from the original host bytes, and the
   crosswalk digest goes into `current_source` (D-8a).
7. **No host PID reaches an actor role** (OB-110).

**Invariants.**
- **I8.1** No synthesized or relabeled `SO_PEERCRED` bytes. Both readings are retained.
- **I8.2** Same OFD and same user namespace are mandatory.
- **I8.3** Host-PID evidence comes only from kernel pidfd plus host procfs.
- **I8.4** FRESH needs the live socket. HISTORICAL never needs a live client.
- **I8.5** The full unsigned UID/GID domain, including 0.

**Decisions requested.**
- **D-8a** Native field versus producer fact for the relative/host correspondence.
- **D-8b** For FRESH, is pidfd host-PID evidence mandatory when `SO_PEERPIDFD` fails because the
  client process has exited? **[unverified reasoning]** Kernel behavior for exited peers may vary by
  version.

**Dependencies.** Seams 9, 4, 7 and 3.

**Authority.** Source is lead-only. Demonstration needs a root PID namespace (lab, operator), and the
kernel semantics must be measured.

**Additive controls.**
- A host client reads PID 0 relative → accepted through the crosswalk.
- Socket inode mismatch → refused.
- A different user namespace → refused.
- A client that exited before intake → behavior per D-8b.
- HISTORICAL settlement after the client exited → succeeds.
- Requester UID 0 and the maximum unsigned UID.
- A delegated foreign-UID socket gains no extra rights.
- Preparer versus commit peer joins.

**Risks.** Kernel `SO_PEERPIDFD` semantics. The breadth of the gate changes.

**Size.** M.

### Seam 9 — Closure and current-ownership correspondence

**Current draft state.** These defects were observed by reading.

- **(a) Stale seed.**
  1. `CustodyOffer.__init__` calls `authorize_root()` (`rw/root_worker_custody.py:124`) and then
     builds the frame (`:125-132`).
  2. `transfer()` calls `authorize_root()` again (`:141`).
  3. That capture appends an ACK boundary to the operation journal
     (`rw/canonical_actor_execution.py:125-127`) after the seed's owner state was taken.
  4. The intake compares the seed with current state (`rw/protected_root_observation.py:110-111` →
     `rw/root_worker_current_state.py:75-115`, exact logical equality for non-custody SQLite).
     Refusal is expected.
- **(b) Reconstruction lock conflict.**
  - `RootWorkerFront(p, front.path)` (`rw/root_worker_closed.py:164`) opens the custody journal
    without `preheld` (`rw/protected_root_worker.py:117-118`).
  - That is a new OFD with `flock(LOCK_EX|LOCK_NB)` (`rw/root_worker_journal.py:59-62`;
    `rw/root_worker_custody.py:31`), taken while the escrowed OFD copies still hold the lock.
  - Result: `BlockingIOError`, then `UNKNOWN_CLOSED_RECONSTRUCTION`.
- **(c) EOF spin.** `poll_closed` returns `None` when FIONREAD is 0
  (`rw/protected_root_supervisor.py:181-182`). At EOF without CLOSED, the loop at `:218` re-arms on a
  permanently readable fd.
- **(d) No deadlines.** `accept` (`:77`) and the `to_thread` `recvmsg` calls (`:291`, `:310`, `:325`)
  have none.
- **(e) A lost ACK stops a possible owner.** The `invoke` `except` path calls
  `retain_and_stop_unknown`, which runs `systemctl --system stop` (`:346-362`) even if the worker had
  already committed `CUSTODY_ACK`.
- **(f) Worker death before `HANDLER_TERMINAL`.** The collector receives the terminal first
  (`rw/root_worker_closed.py:126`). At EOF it raises, so CLOSED/ECHILD and the outer wait are never
  collected.
- **(g) Retention growth.** Every capture embeds the raw bytes of every provisioned file
  (`rw/root_worker_current_state.py:62-70`) into `EXECUTION_NATIVE`
  (`rw/protected_root_observation.py:157-164`). `CustodyReceipt.intact()` and `claim()` redecide and
  re-append each time (`rw/root_worker_custody.py:214-238`). P1:101 records prior OOM history.
- **(h) Lingering units.** `RemainAfterExit=yes` units (`rw/protected_root_resource.py:69`) are never
  reset after CLOSED.
- **(i) Cancellation on registration failure.** `spawn_background` cancels the task when `own_task`
  registration fails (`rw/daemon.py:115-121`), and leaves a cancelled entry in `_background`.

What the draft already gets right: there is no EOF or handler-return settlement, and CLOSED requires
ECHILD, terminal pidfds, the outer wait and complete raw drains (`rw/root_worker_closed.py:44-83`).

**Original requirement (quoted).**
- RW:36: "Do not settle a LIVE root or release/charge on EOF, missing cgroup or a handler return.
  Unknown authenticity or failed durable capture keeps holds and named quarantine."
- P1:147 and P1:149: half-transfer, lost local/remote ACK, unknown native outcome, retained holds,
  authenticated CLOSED settlement.
- P1:163: fault campaigns.
- OB-049, OB-076, OB-146, OB-184, OB-185, OB-212.
- RC:
  - "unknown dispatch and mapping retain full held resource/use and quarantine";
  - "operation mutation partial DB/file/bootstrap crash retains diagnosis".

**Design direction.**
1. **A durable custody phase machine** in the custody journal, using `BEGIN IMMEDIATE` on one SQLite
   database. Phases:
   `PREPARED → HELD → RUNNING → EXECUTION_NATIVE → EXECUTION_ACK → HANDOFF_INTENT → FRONT_CLOSED →
   TRANSFER_SENT → (CUSTODY_ACK | ABANDON) → WORKER_OWNED → ORIGINAL_RESULT → HANDLER_TERMINAL →
   CLOSED_NS → CLOSED_OUTER → CLOSED_RAW → CLOSED_WITNESS → HISTORICAL_SETTLEMENT →
   FRONT_RECONSTRUCTION`, plus `UNKNOWN(cause)`.
   - Ownership decides who may act on state, so transition legality should be a native relation
     that Python obeys (D-9a).
2. **Ownership CAS.** The worker's `CUSTODY_ACK` and the front's `ABANDON` are appended in the same
   kind of IMMEDIATE transaction, conditioned on the head, so exactly one wins.
   - The worker must commit `CUSTODY_ACK` before `run_original`.
   - The front stops a worker only after its `ABANDON` commits.
   - A lost ACK is resolved by reading the journal.
3. **Seed freshness.** The frame and the `root_native` seed come from the last pre-close capture,
   taken inside `transfer()` immediately before `close_front_owners`.
   - Capture paths are read-only.
   - Retention appends precede the seed state.
4. **The fresh front reuses the escrowed custody-lock OFD** through `ClosedFrontEscrow.claim` as
   `preheld`. The old journal object closes only after the fresh front binds.
5. **EOF without CLOSED** becomes `UNKNOWN(ROOT_CHANNEL_EOF_WITHOUT_CLOSED)`, retained.
   - The collector then waits on pidfd terminal state, manager `MainPID==0` and the outer wait.
   - It never spins and never settles.
6. **Collect physical closure independently of `HANDLER_TERMINAL`.** If the terminal is missing, the
   canonical outcome is UNKNOWN: the use is quarantined and holds are kept. The physical REAPED fact
   is still recorded, and K4 decides.
7. **Every blocking wait** uses poll with deadlines joined to pidfd and manager state. A deadline
   produces UNKNOWN, never success.
8. **Content-addressed lossless retention.** Each distinct state's raw bytes are stored once and
   referenced by digest. `intact()` re-appends only when the state changes.
9. **After `CLOSED_WITNESS`, an owner-plan-selected unit reset**, recorded as factual cleanup and not
   as terminal authority.
10. **Durable registration intent before creating a detached task.** If registration fails, the task
    is never created, so nothing needs cancelling.
11. **A crash-point table**: every durable phase × crash → the legal state. The startup reconciler
    (seam 2) uses it.

**Invariants.**
- **I9.1** Exactly one owner, by durable CAS.
- **I9.2** Never stop a worker that may own state.
- **I9.3** No release, charge or settlement on EOF, a missing cgroup, a handler return or a deadline.
- **I9.4** Unknown → named quarantine, with holds.
- **I9.5** The seed equals the last pre-close state.
- **I9.6** Reconstruction uses the escrowed OFDs.
- **I9.7** Lossless retention without unbounded duplication.

**Decision requested.**
- **D-9a** Should the phase relation be native (an additive SPARK relation)?

**Dependencies.** Seams 2, 3, 4, 6 and 8; SL-0.

**Authority.** Source is lead-only. The fault campaign is lab and operator work, within the existing
specialized-validation boundary (P1:163).

**Additive controls.**
- A crash at each phase boundary ends in the legal state.
- A lost `CUSTODY_ACK` → no stop; the outcome is `WORKER_OWNED`.
- Worker `SIGKILL` before the terminal → physical closure collected and the use quarantined.
- Helper death → EOF and UNKNOWN, with bounded CPU.
- Reconstruction succeeds with the preheld lock.
- Retention size is bounded by the number of distinct states (observed).
- Half-transfer → the front keeps its escrow and the worker refuses intake.

**Risks.** Changing the journal schema requires re-provisioning (seam 2). SQLite locking-mode correctness.

**Size.** L.

### Seam 10 — Review, control and proof seal

**Current draft state.**
- P0-2: one stale pin.
- P0-3: 36 of the 60 source-tree delta entries are unpinned.
- `proof_manifest` keeps the original prefix and the child suffix (`rw/proof_manifest.py:1026-1034`).
  The floor is `MINIMUM_CHECKS = 251` (`:22`), and `UNANALYZED_BOUNDARY = {"worldline-c_api"}` (`:316`).
- There is no build or hardening recipe for the C supervisor.
- No root-worker control exists in any roster or in RC.
- `tests/test_resource_child_execution_v1.py` is not enrolled. The ordinary roster lists explicit
  `unittest` modules (`ORIGINAL-ORDINARY-ROSTER.json`, 52 literal launches observed), so it does not
  discover new files.
- No compiler, prover, runtime or control result exists (RW:37).

**Original requirement (quoted).**
- RW:37: "Add genuine required full-domain controls without mocking readiness/custody, dropping old
  fixtures, skips or rewriting expected refusals as completion."
- P1:153: "Recompute all effective normalized pins and full ordered proof enrollment without
  changing the original policy prefix or replacing original accepted cases."
- P1:161: floor 251, the sole `worldline-c_api` boundary, and zero unproved, zero justified, zero
  `pragma Assume`.
- P1:162: the 52-action ordinary roster plus `REQUIRED-LIFETIME-CONTROLS.json`, "these additions
  replace none".
- OB-084, OB-085, OB-048, OB-115, OB-118, OB-212.

**Design direction.**
1. **Explicit reviewed pin deltas.** Refresh the stale pin as a recorded deliberate change. Append
   effective pins for every new or changed Python, C and Ada file. Never alter the original prefix.
2. **`REQUIRED_PROVED` and `DECLARED_CORE_ADA_SOURCES` entries** for every new SPARK unit: seam 1 and
   its exchange/K4 successors, the seam-7 containment predicate, and the seam-9 relation if adopted.
3. **C supervisor.**
   - A build recipe with exact compiler identity, warnings as errors, stack protector, FORTIFY, PIE
     and full RELRO.
   - Static analysis, and sanitizer and fuzz fixtures for the frame parsers, in the lab.
   - All recorded as unproved native-body obligations (OB-048 class), with no proof credit.
4. **An additive `protected-root/required_controls.json`** listing every control in §2. It is
   enrolled after the complete ordered original roster and the lifetime controls. It replaces none,
   allows no skips, and mocks no readiness or custody.
5. **Review cadence.** A different-author actual `gpt-6.1-sol` review per slice, then a full-lane
   review before source selection. Proof only in the F8-successor frame. Runtime only on matching
   source.

**Invariants.**
- **I10.1** The original prefix, floor and boundary are unchanged.
- **I10.2** Every changed file is pinned at slice freeze.
- **I10.3** No control is replaced.
- **I10.4** Source review gives no proof or runtime credit.
- **I10.5** A frontier control is retired only by a reviewed successor.

**Dependencies.** All seams. The lead's frame and capacity gates.

**Authority.** Authoring is lead-only. Proof and control campaigns are blocked by the lead's STATUS
gates (operator decision on W-1, capacity). Lab controls need the operator.

**Additive controls.**
- A manifest audit that recomputes pins.
- An unpinned-file detector.
- A stale-pin mutant.
- A C hardening-flag check.

**Size.** M (high volume).

---

## 3. Dependency-ordered plan

| Step | Slice | Content | Depends on | Who |
|---|---|---|---|---|
| 0 | **SL-0** hygiene (parallel) | P0-1 lock discipline (single `gate.mutex` acquisition, `_locked` internal variants, AST nested-acquisition audit; no Gate change); P0-4 single `attach_scoped_resource` with the exact producer check; P0-2/P0-3 pin record plan | — | lead; GPT-6.1 review |
| 1 | **SL-1 = recommended first slice** | Seam 1 **spec only**: `Worldline.Scoped_Canonical_Operation` `.ads` (Reference/Decide/Post, original decision type, clauses C1–C4), Ghost `Proj` + `Scoped_Refines_Original` statements, wire layout spec, and a `pre_effect` scoped-branch design record. No body, export, wiring or run. | — | lead; GPT-6.1 review |
| 2 | SL-2 | Seam 1 bodies, export through `worldline-c_api` (per C-API v3), wrapper, value fixtures; then scoped exchange (SL-2b) and K4 (SL-2c) successors | SL-1, C-API v3, D1/D2 | lead; proof needs admitted frame |
| 3 | SL-3 | Seam 7 crosswalk schema, independent pair producers, containment predicate (spec first) | SL-1 | lead |
| 4 | SL-4a | Seam 2 descriptor v2 union, attach in `construct`, custody provisioner source, plan schemas | SL-0, SL-3 | lead (source); operator to provision |
| 5 | SL-5 | Seam 9 phase machine/CAS/seed/lock/EOF/deadline/retention; seam 8 crosswalk peer and receive ordering | SL-0 | lead |
| 6 | SL-4b | Seam 2 genuine full-ledger reconciler using the seam-9 crash-point table | SL-4a, SL-5 | lead |
| 7 | SL-6 | Seam 6 `finish` split, three scoped historical adapters, collector settlement | SL-2, SL-5 | lead |
| 8 | SL-7 | Seam 3 slot-custody roster and `TransferredSlot` | SL-5 | lead |
| 9 | SL-8 | Seam 5 child dispatcher, helper successor, delegation per D-5a (interim named refusal kept) | SL-2, SL-3, SL-7 | lead (source); operator (lab, delegation, quota) |
| 10 | SL-9 | Seam 4 request transfer, worker loop, accounting per D-4a | SL-2, SL-5, SL-7, SL-8 | lead |
| 11 | SL-10 | Seam 10 seal (pins, `REQUIRED_PROVED`, controls roster, C recipe), full-lane GPT-6.1 review, explicit composition into the lead's common composition | all | lead; GPT-6.1 |
| 12 | SL-11 | Matching-source strict proof (F8 successor), the complete ordered ordinary roster plus lifetime plus additive controls, lab runtime and fault campaigns | SL-10 | operator gates (§4) |

**Why SL-1 first.**
- It is the smallest unit of seam work whose correctness can be judged independently. Contracts are
  the design, and it can be checked against `core/worldline-canonical_operation.adb`,
  `core/resource_run_ledger.ads` and `core/resource_scoped_run_ledger.ads` alone.
- It needs no lab, root, operator or other seam.
- It produces the decision object that seams 4, 6 and 9 consume for fresh per-request admission.

SL-0 is equally lead-only. It should be reviewed in parallel, because P0-1 blocks every scoped
runtime control.

---

## 4. Cannot start without operator action

1. **Any runtime execution of the lane.**
   - It needs euid 0:
     - `rw/protected_startup.py:153`;
     - `R/protected-root/worker_entry.py:19-20` and `launcher.py:12-13`;
     - `GATE:157`;
     - `.c:308`.
   - It needs a root-owned `/srv/cosmogony-canonical-v1.*` installation (`GATE:172-175`).
   - It needs system-manager units with `User=root` (`rw/protected_root_resource.py:68-71`).
   - It needs `CAP_SYS_ADMIN` for `unshare` and `mount` (`.c:257-258,336`).
   - Sudo needs the operator (PROMPT:74).
2. **Running the custody, operation-head and crosswalk provisioners**, and creating the v2
   installation (seams 2 and 7).
3. **The systemd delegation change** (`Delegate=yes`) for the root worker unit, and the helper
   successor's privileged behavior (seam 5).
4. **Real actor children in fork and race controls.** They spend model quota (`gpt-6-luna` with high
   reasoning, through the Codex adapter only).
5. **Fault campaigns** (SIGKILL, OOM, systemd or daemon restart, disk full, read-only FS, labeled
   power-loss simulation) inside the specialized-validation boundary (P1:163).
6. **Proof and control dispatch.** The lead's STATUS records frame qualification BLOCKED, capacity
   BLOCKED (negative margin; backup service failed) and "Operator approvals: None given". W-1 needs an
   operator decision.
7. **Any merge, release, install, production-service change or real PRIME mutation.** None of this
   design authorizes them.

---

## 5. Concerns: the lane depends on paused labs and infrastructure

- **No runtime path outside a root `/srv` lab.** The lane cannot execute anywhere else (§4.1). The
  status of any existing `/srv` lab and its resource windows was **not inspected**, as my limits
  required. RW:45: "Do not start a target, reuse a paused resource window".
- **COSMOGONY lab source is a runtime dependency.** The lane's dependency root is
  `W/work/protected-canonical-full-bridge-repair-v2/declared-inputs/composed-transaction-public-source`
  (`origin.json`): the Gate, issuer and universe come from there. COSMOGONY Authority v1 lab source is
  therefore a runtime dependency. Its preheld-lock overlays (`dependency-source/`) are draft and
  unreviewed.
- **Kernel features must be measured on the lab host:**
  - `SO_PEERPIDFD` (header define observed, value 77);
  - pidfd fdinfo namespace rendering;
  - `CLONE_INTO_CGROUP`;
  - cgroup v2 delegation.
  The analysis host reports Linux 7.2.6 (environment observation). The lab host's kernel is
  undetermined.
- **Storage and backup health** belong to the parent handoff (P1:179-181). Heavy lab or proof work
  waits on capacity and vault gates.

---

## 6. Decisions requested from the GPT-6.1 reviewer

| ID | Decision |
|---|---|
| D-1a | Faithfulness of the C2 lift, including projection rounding |
| D-1b | Require `Rows(I).Scope = State.Current` for a fresh pre-effect? |
| D-2a | Descriptor v2 versus a union inside v1 |
| D-2b | Frontier-control retirement procedure |
| D-3a | Transfer V3 actor slots versus requiring them terminal |
| D-4a | In-coordinator request accounting: (A), (B) or (C) |
| D-5a | Delegation model and its security argument |
| D-5b | Helper successor versus extending V3 |
| D-6a | Retained `EFFECT_OBSERVED` versus the quarantine domain when physical settlement is unknown |
| D-7a | RootController ABI change versus sourcing only |
| D-8a | Native field versus producer fact for the requester crosswalk |
| D-8b | Is pidfd evidence mandatory for FRESH when the client exited? |
| D-9a | A native custody-phase relation |

---

## 7. Non-claims

- This document reviews, accepts, qualifies, proves and authorizes nothing. Every original Phase One
  obligation and every lane seam remains OPEN.
- Nothing was compiled, run, imported, proved or tested. Every design is an untested engineering
  hypothesis.
- Hash and inventory agreement establishes only the byte identity of the analyzed snapshot. It does
  not establish authenticity, an atomic snapshot or installed state.
- Kernel-semantics statements marked [unverified reasoning] need measured lab observations.
- Observed counts are tool outputs. The two derived numerals are JACKAL `exact` (formal=false) and
  establish arithmetic only.
- Prior Claude notes and SIA results are model-origin recall, not evidence.
- Sizes (S/M/L/XL) are qualitative.
- Nothing here changes any original target, accepted case, fixture, control, contract, threshold or
  proof floor. Temporary named refusals mentioned here keep their obligations OPEN.
