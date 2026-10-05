# F32-CONFLICT resolution design, v1

**Status: DRAFT design by an author. It is not a review and not acceptance. Nothing was executed.**

- **Author.** A Claude Code general-purpose drafting subagent (claude-opus-5-5), working for the Claude lead on
  2026-10-05. It did not write the F32 investigation, D1, PK-0 or any reviewed lane.
- **Method.** Static reading only. No WORLDLINE or COSMOGONY code, test, compiler, prover or native library was run.
  The only programs run were `sha256sum`, `diff`, `grep` and a standard-library `ast` parse of scratch copies.
- **Edits.** No source tree was edited. The post-image and patch in §6 were built from copies in the session
  scratchpad.
- **Evidence.** `evidence.json` in this directory gives the path, sha256 and line range for every citation.
- **JACKAL.** No `jackal.json`. Every count and hash here was read from tool output; none was derived.
- **Consequence ceiling.** Informational. A static design cannot show a returned decision code. Only the admitted-frame
  runs in §9 can.

Path abbreviations:

| Name | Path |
|---|---|
| W | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow` |
| S5 | `W/work/claude-composition-v5-beta/source` |
| O | `W/outputs/claude-phase1-handoff-20261004` |
| WT | `W/work/claude-lead-isolation-v1/wt-1` |
| B | `/home/sicarii/Work/ada-spark-readiness-20260927/codex-continuation-20260930` |
| ENG | `B/phase1-finalization-owned-acquisition-engineering-v1` |
| V1 / V2 | `ENG/authority-item1-priority-v1` / `ENG/authority-item1-priority-v2` |

---

## 1. Summary

**What the evidence shows.** OB-003 and the four AUTHORIZED controls do not conflict as requirements. They conflict
only through one fixture derivation that item1 V2 left inconsistent.

- **OB-003 itself requires the positive case.** Its acceptance test says the unchanged-requirement "1.9.1 control is
  AUTHORIZED" (O/OBLIGATIONS-v2.json:95).
- **Each control's original intent is that case.** Every one of the four controls asserts that a fully bound candidate
  evaluation with an unchanged requirement and a complete matching context is AUTHORIZED.
- **Item1 V1 kept the two consistent.** It gave the shared fixture `resulting_requirement=h(8)`, equal to its
  `current_requirement` (V1 test file :530). The candidate-mode helpers inherited that value.
- **Item1 V2 broke the consistency.** For checkpoint mode it had to make that slot absent, so it set the fixture to
  `None` (V2 :530). The two candidate-mode helpers built from the fixture were not updated. V2's own HANDOFF declares
  only the checkpoint change (V2 HANDOFF.md:5, :9).

**Recommendation: R-A.**

- **The change.** The two candidate-mode helpers, `bound_request` and `collapse_values`, explicitly supply
  `resulting_requirement` equal to the fixture's own `current_requirement`. That is exactly the value item1 V1
  produced. The helpers already supply `evaluated_requirement` the same way, on the line above.
- **What stays unchanged.**
  - Every assertion. The static AST check finds the assert-call ASTs identical and in the same order.
  - The kernel, wire, ABI and contracts, and the production producers.
  - The checkpoint fixture, which keeps `None`.
- **Size.** Two keyword arguments in two helper functions, appended on existing lines. No other line number moves.

**Who decides.** The lead. This is routine, reversible engineering. It preserves the original external contract and
success domain, and it is not an API or contract redefinition (§10). The obligation stays OPEN until the independent
GPT-6.1 review and the admitted-frame matching-source runs in §9 exist.

---

## 2. Re-verification of the F32 FINDINGS against source

Each claim the design relies on was re-read at S5 unless another tree is named.

| FINDINGS claim | Verified at | Result |
|---|---|---|
| The checkpoint fixture has `current=h(8)`, `resulting=None` and `roster_complete=False` | `tests/test_raw_evaluation_default.py:522-533`, values at :526 and :530 | confirmed |
| `bound_request` switches to candidate mode and does not set `resulting_requirement` | same file :71-81 | confirmed |
| `collapse_values` does the same | `tests/test_finalization_kernel.py:245-255` | confirmed |
| Four AUTHORIZED assertions | raw :88-89, finalization :262-263, row projection :95-96 (method :86-99), lifetime :162-163 (method :152-168) | confirmed |
| `CollapseInput` has no defaults | `runtime/worldline/core.py:214-258` (docstring :216) | confirmed |
| `None` encodes absent with all-zero bytes | `runtime/worldline/core.py:595-598` | confirmed |
| Wire field order | `core.py:120-122` and `core/worldline-collapse_wire.ads:55-57` | confirmed |
| Candidate mode accepts an absent Resulting; checkpoint mode requires it absent | `core/worldline-collapse_wire.ads:89-137`, specifically :132-136 | confirmed |
| Decode keeps presence | `core/worldline-collapse_wire.ads:237` | confirmed |
| Candidate mode requires Resulting present | `core/worldline-collapse.ads:148-154` (:151) | confirmed |
| Evidence requires `Same(Current, Resulting)` | `core/worldline-collapse.ads:184-195` (:188) | confirmed |
| `Post` makes Authorized equivalent to `All_Hold` | `core/worldline-collapse.ads:213-217` | confirmed |
| `Same` is false when either side is absent | `core/worldline-identities.ads:80-82` | confirmed |
| Decide order: EEI when roster readiness is 0, then Identity_Absent | `core/worldline-collapse.adb:20-25` | confirmed |
| The C entry points overwrite only the roster bytes | `core/worldline-c_api.adb:817-819`; `core/evaluation_finalization_c.adb:485-487` | confirmed |
| The Python callers pass the request through unchanged | `runtime/worldline/evaluation_wire.py:94-122`; `runtime/worldline/finalization_kernel.py:286-322` | confirmed |
| `test_collapse_recomputes_carried_roster` and `test_revalidation_binding` set Resulting explicitly | raw :471-490 (:478); `tests/test_revalidation_binding.py:303-318` (:315) | confirmed |
| Lineage hashes | sha256 of the three trees | confirmed; see the table in §3 |
| Recorded pre-item1 runs | `B/phase1-evaluation-checked-scan-ordinary-v1/evidence/default-tests-v1` and `B/phase1-finalization-ordinary-v2/evidence/default-tests-v1` | confirmed (details below) |

The recorded pre-item1 runs:

- `child.stderr` line 4 reads "test_complete_owned_join_and_padded_epoch … ok", line 44 "Ran 41 tests", line 46 "OK".
- The returncode is 0 in both `child-wait.json` and `result.json`.
- The test file each run lists under `inputs/` has sha256 `53db45a0…`, the pre-item1 bytes.
- These runs were read as found and are not authenticated.

**One FINDINGS inference is weaker than stated.** FINDINGS says `bound_request` is absent from V1's
`original-methods.json`. That is true but tells us little. The list names only `test_*` methods, so it also omits
`checkpoint()`, which V1 did change at :530 (V1 `original-methods.json`).

**New static observations.** These were not in FINDINGS.

1. **Two pairs of identities, not a conflict.** The context join, which hosts the metadata relation, compares the
   request with its projection only modulo the carried rosters (`core/worldline-evaluation_authority.ads:197-199`,
   :225-226). The synthetic joins in these tests build the projection from the request itself
   (raw :67, finalization :239). Whatever Resulting value the helper supplies therefore appears identically on both
   sides of the join. R-A cannot open a join mismatch.
2. **Raw-path metadata is checked only after Decide returns Authorized** (`core/worldline-c_api.adb:857-872`).
   - Affected: the row-projection refusal at :97-99, which corrupts metadata and expects INVALID_REQUEST.
   - Why it matters: at S5 that refusal can only refuse for the intended reason once the positive at :95-96 is
     reachable.
   - Not affected: the finalization path joins metadata inside `Context_Joined` before the decision
     (`core/evaluation_finalization_c.adb:399-409`, :473-484), so `test_finalization_kernel.py:264-266` is not affected.
   - What remains open: the actual codes are a run question (§9).
3. **The lifetime control needs no edit.** Its oracle pins (`tests/test_context_cast_lifetime.py:19-37`, :73-77) bind
   `oracle_finalization_kernel_cast_lifetime.py` and `oracle_evaluation_context_cast_lifetime.py`, not
   `test_finalization_kernel.py`. It reaches the request only through `self.fixture.collapse_values()` (:154).
4. **Nothing in S5 verifies the assurance checkpoint inventories.**
   - `assurance/checkpoints/phase1-native-lifetime-2026-10-03.json:2853-2855` and :2888-2891 hold historical sha256
     inventories. The latter records `53db45a0…`, the pre-item1 test bytes, so it already differs from S5.
   - A grep of S5's `*.py` and `*.sh` for `assurance/checkpoints` and `phase1-native-lifetime` returns nothing.
5. **Frozen lanes in WT bind the current bytes of both test files.**
   - `WT/packets/capi-pk0-v2/packet.json:198-199`
   - `WT/designs/claude-native-bigint-d1-design-v4/DESIGN.md:191`
   - Consequence: R-A changes those inputs, so those lanes must be re-bound by their next revisions. They are never
     edited in place (§8).
6. **No control depends on the absent value.** Searching the eight modules that reuse these helpers for
   IDENTITY_ABSENT, EXECUTION_EVIDENCE_INCOMPLETE or REQUIREMENT_CHANGED finds only raw :457, a history-selector reason,
   and raw :492, a separate literal request. Neither uses `bound_request` or `collapse_values`.

---

## 3. Original intent of each control, and what "original fixture" means here

### 3.1 Lineage of the bytes

| Tree | `test_raw_evaluation_default.py` | `test_finalization_kernel.py` | `worldline-collapse.ads` | Candidate-mode request built by the helpers |
|---|---|---|---|---|
| ENG/source (pre-item1) | `53db45a0…` | `76141dfb…` | `ba6e2a53…`: no Resulting at all (`ENG/source/core/worldline-collapse.ads:135-152`, :180-189) | no such field; AUTHORIZED reachable |
| V1 source | `979e4639…` | `76141dfb…` (unchanged) | `98b2661b…`: OB-003 conjunct added | fixture `resulting=h(8)` (V1 :530), so the helpers carry `h(8)` = current; AUTHORIZED reachable |
| V2 source = item1-repair = S5 = integrated-ordinary-v8 | `22b5b189…` | `76141dfb…` (unchanged) | `98b2661b…` | fixture `resulting=None` (V2 :530), so the helpers carry None; AUTHORIZED unreachable |

- **Wire spec.** V1 `c09c0dcd…`; V2 and S5 `987b3fa7…`.
- **V2's wire change.** It adds `R.Resulting_Requirement.Present = 0` to the checkpoint-mode slot rule (V2
  `core/worldline-collapse_wire.ads:132-136`).
- **V2's changed files.** Exactly seven:
  - `core/worldline-collapse_wire.ads`
  - `runtime/worldline/evaluation_context.py`
  - `runtime/worldline/proof_manifest.py`
  - `runtime/worldline/transaction.py`
  - `tests/test_core_abi.py`
  - `tests/test_raw_evaluation_default.py`
  - `tests/worldline_collapse_checks.adb`

### 3.2 Intent per control

- **raw :83-90, `test_complete_owned_join_and_padded_epoch`.**
  - Present since pre-item1. The method bytes are unchanged and outside V1's changed-method list.
  - Intent: a complete owned join with a padded epoch is AUTHORIZED, and the request bytes are not mutated.
  - Evidence: the recorded pre-item1 runs report "ok".
- **finalization :257-266, `test_additive_finalization_collapse_requires_full_context_and_metadata`.**
  - The file has never changed.
  - Intent: a full finalization context and metadata give AUTHORIZED, and removing metadata gives INVALID_REQUEST.
- **row projection :86-99, `test_default_join_requires_projection_and_keeps_legacy_layout`.**
  - Never changed (`74a19597…` in every tree).
  - Intent: the default join with projection is AUTHORIZED, the legacy layouts stay queryable, and corrupted metadata
    gives INVALID_REQUEST.
  - Evidence: the pre-item1 `metadata-tests-v1` runs report "ok".
- **lifetime :152-168, `test_discarded_full_prepared_graph_releases_without_cyclic_collection`.**
  - One version only (`f6bc3e2f…`).
  - Intent: a fully joined prepared graph decides AUTHORIZED, then releases without cyclic GC.
  - Requirement status: it is listed in `O/REQUIRED-LIFETIME-CONTROLS.json:3-24` as required, status UNRUN, "ALL remain
    required".

All four take their candidate request from the same derivation:

- the shared fixture `RawDependencyControls.checkpoint()`, with
- mode CANDIDATE_EVALUATION,
- `evaluated_requirement` := the fixture's `current_requirement`,
- `executed_verifiers` := its `declared_verifiers`, and
- the checkpoint slots cleared.

**The common premise is an unchanged-requirement candidate.** All four controls assume that the candidate's evidence
was evaluated against the current requirement and that nothing changed the requirement. Before item1, the kernel had
no Resulting input, so that premise was implicit. Item1 V1 made it explicit:

- The kernel gained the conjunct.
- The fixture's Resulting became `h(8)` = current.
- The V1 HANDOFF states the rule: "valid typed/raw fixtures explicitly supply their actual resulting identity"
  (V1 HANDOFF.md:11) and "There is no defaulting to current/evaluated" (:5).

### 3.3 What "original fixture" means for these helpers

Item1 is itself a repair in the lineage, so "original" has to be read across three layers.

1. **Pre-item1 bytes.** These are the original controls and assertions. The request field did not exist.
2. **Item1 V1.** This is the first fixture in the post-OB-003 domain. Its candidate derivations produce a present
   Resulting equal to current. That is the faithful translation of the pre-item1 premise.
3. **Item1 V2.**
   - Original for checkpoint fixtures: they must carry absence. This is enforced by V2's new controls,
     `tests/test_core_abi.py:190-217` and `tests/worldline_collapse_checks.adb:328-341`.
   - Silent for candidate fixtures. Its HANDOFF says "Valid checkpoint fixtures explicitly supply absence" and "V1
     original assertions/cases remain, with necessary valid-checkpoint fixture updates" (V2 HANDOFF.md:5, :9).
   - The None that reached the candidate helpers is therefore an undeclared side effect, not a decision.

So the original fixture for the candidate helpers is the value V1 produced: Resulting present and equal to the
fixture's current requirement. The original fixture for `checkpoint()` is V2's None. R-A preserves both. The
alternatives each break one of them (§5).

**Value-level check.** This was static, using `ast` on scratch copies.

- After R-A, the request `bound_request` builds equals the literal request at raw :473-481, keyword for keyword, over
  all 35 keywords. That literal belongs to `test_collapse_recomputes_carried_roster`, which item1 V1 updated
  (`resulting_requirement=h(8)` at :478) and which asserts AUTHORIZED at :490.
- Before R-A the only difference was `resulting_requirement`: None against `h(8)`.
- `collapse_values` performs the identical replacement on the identical fixture.

---

## 4. Is this a genuine requirement conflict?

No. The two sets of requirements are jointly satisfiable, and the source already contains controls that satisfy both
at once.

- **OB-003** (`O/ALL-ORIGINAL-OBLIGATIONS.md:47-65`; `O/OBLIGATIONS-v2.json:80-95`).
  - Closure: "in Candidate_Evaluation mode Decide requires Same(Current_Requirement, Resulting_Requirement), with
    Resulting_Requirement recomputed from the staging payload at prepare and at commit".
  - Test: requirement-changing candidates refuse REQUIREMENT_CHANGED "while the 1.9.1 control is AUTHORIZED".
  - The positive unchanged-requirement case is therefore part of OB-003 itself.
- **Controls that satisfy both today.**
  - `tests/test_core_abi.py:219-254` asserts AUTHORIZED for `resulting=h(8)=current`, REQUIREMENT_CHANGED for
    `h(99)`, and IDENTITY_ABSENT for None.
  - raw :471-490 asserts AUTHORIZED with `resulting=h(8)`.
  - `tests/test_revalidation_binding.py:303-318` supplies the measured Resulting.
- **The four controls do not require an absent Resulting.** They require an unchanged-requirement candidate. Absence
  reached them only through the V2 fixture side effect.

F32-CONFLICT should therefore be reclassified from "two original requirements conflict" to "fixture-consistency defect
introduced at item1 V2; the requirements are jointly satisfiable". The obligation stays OPEN until §9 is satisfied.

---

## 5. Candidate resolutions

Notation used below:

- **A1–A4** are the four AUTHORIZED controls.
- **CK** is the V2 checkpoint-absence controls: raw :535-550, `test_core_abi.py:190-217` and
  `worldline_collapse_checks.adb:328-341`.
- **OB3-C** is the OB-003 explicit controls: `test_core_abi.py:219-254`, plus OB-003's own acceptance test and the
  mutant obligation.

| ID | Resolution | OB-003 | A1–A4 assertions | CK | Contract / API | Verdict |
|---|---|---|---|---|---|---|
| **R-A** | `bound_request` and `collapse_values` supply `resulting_requirement` = the fixture's own `current_requirement`, the V1 value; no assertion changes | unchanged | unchanged, and reachable again | unchanged (`checkpoint()` keeps None) | unchanged | **RECOMMENDED** |
| R-A′ (cosmetic variant of R-A) | same values; the keyword goes on its own new line, or a shared `candidate()` helper is added and used by both helpers | unchanged | unchanged | unchanged | unchanged | Acceptable, but it shifts the cited line numbers and touches more lines. R-A is preferred for minimality |
| R-B1 | Kernel: in candidate mode, absent Resulting counts as Same / not required | **weakened**: contradicts the closure text and `Same`'s "two absent values are never the same" (`worldline-collapse.ads:27-28`; `worldline-identities.ads:80-82`) | pass | unchanged | changes `Required_Present`, `Evidence_Holds`, `Post` and the proved contract | **REJECTED.** Absence would acquire authority, which the phase prompt forbids (`complete-phase1-prompt.txt:34`, :42; `O/HANDOFF.md:119`). It also turns OB3-C `test_core_abi.py:248-249` (expects IDENTITY_ABSENT) into a failure |
| R-B2 | Python or C marshalling fills Resulting := Current when None in candidate mode | **weakened**: Resulting would be copied rather than recomputed from the staging payload (OB-003 closure; `worldline-collapse.ads:60-61`) | pass | unchanged | Python gains an independent authorization input | **REJECTED.** It contradicts "no defaulting to current/evaluated" (V1 HANDOFF.md:5; V2 HANDOFF.md:5) and "Python has no independent definition of authorization" (`O/HANDOFF.md:27`). It also breaks OB3-C :248-249 at the Python boundary |
| R-B3 | Kernel: reorder the refusals in `Decide` | unchanged | still not AUTHORIZED, because `Post` makes Authorized ⇔ `All_Hold` (`worldline-collapse.ads:217`) | unchanged | body only | **REJECTED.** It does not resolve anything |
| R-B4 | Remove or soften the OB-003 conjunct | **removed** | pass | n/a | contract lowered | **REJECTED.** It is a direct weakening, and it fails OB-003's mutant/proof-gate test |
| R-C1 | Change the four assertions to expect IDENTITY_ABSENT or EEI | unchanged | **weakened**: the accepted case is removed | unchanged | unchanged | **REJECTED.** It removes accepted successes (`O/WORKSPACE-RULES.md:6`; `RECOVERY-AND-AUTONOMY.txt:5`) |
| R-C2 | Skip, xfail or delete the four controls | unchanged | **removed** | unchanged | unchanged | **REJECTED** for the same reasons. The roster also requires them (`O/ORIGINAL-ORDINARY-ROSTER.json` entries at :2174-2198, :2199-2223, :2374-2398; `REQUIRED-LIFETIME-CONTROLS.json`) |
| R-D | Restore `checkpoint()` to `resulting=h(8)` (undo the V2 fixture change) | unchanged | pass | **broken**: a checkpoint request with Resulting present is malformed (`collapse_wire.ads:132-133`) | unchanged | **REJECTED.** It trades one set of failing controls for another. raw :535-543 (AUTHORIZED, `valid: True`), raw :545-550, `test_finalization_kernel.py:282-289` and the CK checks would refuse INVALID_REQUEST or change their dependency answers |
| R-E | Revert V2's checkpoint-absence wire rule as well as the fixture | unchanged in candidate mode | pass | **removed** | wire contract lowered | **REJECTED.** It weakens typed absence: "A slot the question does not consult must be empty" (`collapse_wire.ads:126-127`). It also reverses a reviewed V2 repair and breaks CK |
| R-F | Rebuild the four controls on the real producer path (`bind_selected` with `resulting_requirement=policy`, as `producer_case` does at raw :162-226) | unchanged | the assertion text could stay, but each control's mechanism changes (synthetic TEST_ONLY join → producer join) | unchanged | unchanged | **REJECTED as unnecessary.** It replaces what the original controls exercise (padded epoch, synthetic owned context, metadata layout) and goes beyond the minimal consistent repair. Producer-path coverage already exists (raw :228-249, :358-380; `test_recovery_packet_producer.py:40-53`) |
| R-G | Treat this as a reserved contract decision and escalate to the operator | — | — | — | — | **Not warranted.** R-A preserves the contract and the success domain (§10). Escalation would invent an approval gate (`RECOVERY-AND-AUTONOMY.txt:7`) |
| R-H (optional, additive) | Add new paired refusal controls next to R-A, such as a raw-path `bound_request` variant with `resulting=h(99)` expecting REQUIREMENT_CHANGED | unchanged (strengthened) | unchanged | unchanged | unchanged | **Optional.** Not needed to close F32. If adopted, it is a separate additive control with its own review. It replaces nothing |

**Why byte-identity of `test_finalization_kernel.py` cannot be kept.**

- `collapse_values` builds its request only from `RawDependencyControls.checkpoint()` plus fixed replacements
  (`test_finalization_kernel.py:245-251`).
- `checkpoint()` must keep `resulting=None`, which rules out R-D and R-E.
- So the only way to supply Resulting without weakening OB-003 (R-B) or the assertions (R-C) is inside
  `collapse_values`.

This is the minimum byte change the requirements allow. It restores the request value V1 produced for this unchanged
method.

---

## 6. Exact proposed diff (R-A)

The patch was authored against S5. It applies equally to `W/work/item1-repair/source` and
`W/work/integrated-ordinary-v8/source`, which hold the same bytes for both files.

```diff
--- a/tests/test_finalization_kernel.py
+++ b/tests/test_finalization_kernel.py
@@ -248,7 +248,7 @@
         request = replace(original, mode='CANDIDATE_EVALUATION',
             evaluated_requirement=original.current_requirement,
             executed_verifiers=original.declared_verifiers,
-            expected_checkpoint=None, witnessed_checkpoint=None)
+            expected_checkpoint=None, witnessed_checkpoint=None, resulting_requirement=original.current_requirement)
         agent = record({'id': 'agent', 'origin': 'agent', 'format': 'exit', 'status': 'PASS',
             'exitCode': 0, 'supervision': {'kind': 'SUPERVISED'},
             'resources': {'ceilingFired': False}}, ENGINE_DECLARATIONS['agent'])
--- a/tests/test_raw_evaluation_default.py
+++ b/tests/test_raw_evaluation_default.py
@@ -72,7 +72,7 @@
         request = replace(RawDependencyControls.checkpoint(), mode='CANDIDATE_EVALUATION',
             evaluated_requirement=RawDependencyControls.checkpoint().current_requirement,
             executed_verifiers=RawDependencyControls.checkpoint().declared_verifiers,
-            expected_checkpoint=None, witnessed_checkpoint=None)
+            expected_checkpoint=None, witnessed_checkpoint=None, resulting_requirement=RawDependencyControls.checkpoint().current_requirement)
         agent = record({'id': 'agent', 'origin': 'agent', 'format': 'exit', 'status': 'PASS',
             'exitCode': 0, 'supervision': {'kind': 'SUPERVISED'},
             'resources': {'ceilingFired': False}}, ENGINE_DECLARATIONS['agent'])
```

Identities, all read from `sha256sum` output:

| Item | Before (S5) | After (scratch post-image) |
|---|---|---|
| `tests/test_finalization_kernel.py` | `76141dfb2ddea1c9fb62e5ea09d27830432e96273f85e984da94f5ebbafb4a62` | `4da992ddfd206134131c31ea306fc19d46500ca8501a5214e540f55357327aa4` |
| `tests/test_raw_evaluation_default.py` | `22b5b189f9686f456214666b5a4dc4b0e3c93ee5b48f983b18994f8119f1a4f0` | `77f0cb999bca30a6eaa1ec663e21ee9cb152f405cb1ae1a591a20465ffad7262` |
| patch text above as a file (with `--label` headers, no timestamps) | — | `226e7fc871b7f17622f7ea2480725644d1ab527765a391157af8b24e5f136650` |

Static scope check: `ast` on scratch copies; nothing imported or run.

- **`test_raw_evaluation_default.py`.**
  - It has 43 class methods before and 43 after. Only `('RawRequiredFailureControls', 'bound_request')` changed.
    None are missing and none were added.
  - It has 62 assert-call ASTs before and 62 after, identical and in the same order.
- **`test_finalization_kernel.py`.**
  - It has 26 methods before and 26 after. Only `('FinalizationNativeControls', 'collapse_values')` changed.
  - It has 38 assert-call ASTs before and 38 after, identical and in the same order.
- **Line counts.** These are unchanged: 561 and 289. Every cited assertion line keeps its number.

The keyword is appended on the existing line, which keeps every cited line number stable. R-A′ formatting has the same
semantics.

---

## 7. R-A against each original requirement

| Requirement | Where | Effect of R-A |
|---|---|---|
| OB-003 Same(Current, Resulting), presence, Requirement_Changed | `worldline-collapse.ads:148-154`, :184-195, :213-217, :269-272; `.adb:41-45` | No byte change; the contract pin is unaffected |
| OB-003 explicit controls (IDENTITY_ABSENT / REQUIREMENT_CHANGED / AUTHORIZED) | `test_core_abi.py:219-254` | Unchanged; still required |
| Independent recomputation of Resulting by production | `transaction.py:364-366`, :745-750, :1118-1120; `evaluation_context.py:419-426` | Unchanged. R-A touches only TEST_ONLY synthetic helpers. Those helpers already supply every other identity as a synthetic `h(n)`, including `evaluated_requirement` = current on the line above |
| No defaulting to current/evaluated | V1 HANDOFF.md:5; V2 HANDOFF.md:5 | Preserved. No producer or encoder default is added; the value is explicit test input, as V1 HANDOFF.md:11 requires |
| Typed absence; equality of absent values never authorizes | `complete-phase1-prompt.txt:42`; `O/HANDOFF.md:119` | Preserved. The positive now carries a present value |
| V2 checkpoint absence | `collapse_wire.ads:126-136`; CK controls | Unchanged; `checkpoint()` keeps None |
| A1–A4 accepted cases | raw :88-89, fin :262-263, row :95-96, lifetime :162-163 | Assertions unchanged; reachable given native readiness and join |
| Refusal twins in the same modules | raw :92-160; fin :264-266, :268-280; row :97-99, :105-110; lifetime :107-118 | Assertions unchanged. Each now has a reachable positive baseline, so its refusal is attributable to the mutated conjunct. For row :97-99 this was not true before (`c_api.adb:862-868`) |
| Lifetime and oracle controls | `test_context_cast_lifetime.py` (no edit), oracle pins :19-20 | Unaffected; bytes `f6bc3e2f…` stay |
| Python has no independent authorization | `O/HANDOFF.md:27` | Unchanged; the native kernel still decides |
| Proof scope, floors, CONTRACT_PINS, Ada bodies | `proof-manifest.json`, `prove.sh` | No Ada, C or proof-manifest change. The full matching-source strict proof stays required for Phase One independently of F32 |
| Original ordinary roster | `ORIGINAL-ORDINARY-ROSTER.json` :2174-2198, :2199-2223, :2374-2398, :2600-2605 | Commands unchanged. "results_transferred": false and "source_matching_rerun_required": true still apply; the runs must use the integrated source that contains R-A |
| Historical checkpoint inventories | `assurance/checkpoints/*.json` | Historical; not edited; not a gate (§2 item 4) |
| Frozen lanes binding these bytes | PK-0 v2 `packet.json:198-199`; D1 v4 `DESIGN.md:191` | Their next revisions must re-bind to the integrated source. They must never be edited in place. That is a sequencing task for the lead, not a weakening |

R-A adds no cap, no new refusal, no suppressed assertion or Ghost, and no assumption.

---

## 8. Integration shape

1. **Author the delta as its own lane**, following the item1-repair pattern (`W/work/item1-repair/HANDOFF.md`).
   - Use a new complete source copy whose baseline is S5, or whichever integrated candidate the lead selects.
   - Do not edit S5 itself: it is pinned by reviews that are in progress.
   - Record a forward and reverse patch (the §6 text) and `changed-paths.json` listing exactly the two test files.
   - Add a static-preservation record. It must state that the assert-call ASTs are retained, that only the two
     FunctionDefs changed, and that every other source byte, mode and link is unchanged.
2. **Get an independent `gpt-6.1-sol` review** of this design and of the exact delta, with the actual model verified.
3. **Compose it into the integrated candidate** that the admitted frame will build and run. Re-bind the PK-0 and D1
   lanes' inputs in their next revisions.

## 9. Controls and evidence that close F32-CONFLICT

The runs must be on matching source in the admitted, resource-admitted frame, with the built library identical to the
integrated candidate.

| # | Evidence | Pass criterion |
|---|---|---|
| E0 (recommended baseline) | Run the four modules on the pre-R-A source | Records the actual codes the four assertions return today (FINDINGS left this open). This is evidence, not acceptance |
| E1 | Roster `default-tests` (`test_raw_evaluation_default`) | Child wait0 and scope wait0. Every assertion passes as written, including :88-89, the :92-160 refusals, :490 and :535-550 |
| E2 | Roster `metadata-tests` (`test_evaluation_row_projection`) | As above, including :95-96, :97-99 and :105-110 |
| E3 | Roster `finalization-kernel-tests` (`test_finalization_kernel`) | As above, including :262-263, :264-266, :268-280 and :282-289 |
| E4 | `REQUIRED-LIFETIME-CONTROLS.json`: all of `test_context_cast_lifetime.py` and `test_finalization_cast_lifetime.py` | All pass, including :162-165 |
| E5 | OB-003 and typed-absence neighbours: `test_core_abi` (:190-254), `test_revalidation_binding`, `test_resulting_requirement_caller`, `test_typed_absence`, and the Ada `worldline_collapse_checks` wire checks | All pass unchanged, showing R-A did not weaken OB-003 or CK |
| E6 | The full original ordinary roster and the full matching-source strict proof campaign, as already required for Phase One | Not credited to F32 alone, but F32 is not closed against a source that has not passed them |
| E7 | Independent `gpt-6.1-sol` review of the design and the delta | No unresolved major findings |

**If a post-R-A run returns a code other than AUTHORIZED at any of the four**, for example EEI from native readiness or
INVALID_REQUEST from a join, that is a different defect. It must be recorded as a new open obligation with its raw
evidence. It does not reopen any weakening option in §5.

---

## 10. Who decides

**The lead decides.** The authority comes from `RECOVERY-AND-AUTONOMY.txt:7`, recorded at `WT/STATUS.md:335-339`:
"Routine engineering, sequencing and API implementation choices that preserve the original external contract and
success domain are yours to resolve. Do not invent approval gates." R-A falls inside that delegation:

1. **It changes only TEST_ONLY helper code.** That is two keyword arguments in two fixture helpers. It touches no
   production module, Ada spec or body, C header, ABI layout, wire encoding, proof manifest or contract pin.
2. **It preserves the original external contract exactly.** OB-003's conjunct, presence rule and refusal codes are
   byte-identical, and so is V2's checkpoint absence.
3. **It restores the original success domain.** The accepted cases become reachable again, and no accepted case is
   removed or turned into a refusal.
4. **It is reversible.** A single reverse patch undoes it.
5. **It is none of the reserved items** (merge, release, install, sudo, production, real PRIME, or an incompatible
   API change).

The options that would be reserved (R-B1, R-B2, R-B4 and R-E, which redefine the kernel contract, wire contract or
caller semantics) are also weakenings. They are rejected outright rather than escalated.

Lead authority does not mean self-acceptance. Under `O/WORKSPACE-RULES.md:7` and `WT/STATUS.md:323-324`, E7 (an
actual GPT-6.1 review) and E1–E6 remain required before F32-CONFLICT can be closed. That review requirement is the
original review requirement, not a new approval gate.

---

## 11. Non-claims and residuals

- No decision code has been observed at either the S5 bytes or the R-A bytes. Every outcome here is a static reading of
  the contracts and bodies.
- The recorded pre-item1 runs were read as found. Their authenticity is not established.
- The behaviour of the raw path with null metadata is not established statically (row :105-110). Whatever it is, R-A
  does not change it.
- R-A does not close OB-003. OB-003 remains OPEN with its own acceptance test, mutant and proof obligations and its
  narrowed parts (OB-017, OB-018, OB-024).
- R-A does not close any item1, Item7, K4 or K6 obligation, or any obligation for confinement, custody or the Phase One
  exit.
- This design has not been reviewed.
