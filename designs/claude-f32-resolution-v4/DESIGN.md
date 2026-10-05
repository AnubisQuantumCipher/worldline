# F32-CONFLICT resolution design, v4

**Status: DRAFT design by an author. It is not a review and not acceptance. Nothing was executed.**

- **Author.** A Claude Code general-purpose drafting subagent (claude-opus-5-5), working for the Claude lead on
  2026-10-05. It is the same author as v1–v3. It did not write the F32 investigation, D1, PK-0, any reviewed lane, or
  any review of this design.
- **Method.** Static reading only. No WORLDLINE or COSMOGONY code, test, compiler, prover, runner or native library was
  run. The only programs used were `sha256sum`, `cmp`, `diff`, `grep` and `od`. v1 also ran a standard-library `ast`
  parse on scratch copies.
- **Edits.** No source tree was edited. Every file in this directory was written with the harness's file-write tool.
- **Evidence.** `evidence.json` in this directory gives the path, sha256 and line range for every citation.
- **JACKAL.** `jackal.json` holds the two derived counts, both from v3 and unchanged. Each was routed through
  `jackal_exact` with status `exact`:
  - the A1 collection count, 1+2 = 3;
  - the checkpoint files that record neither patched test file, 8-3 = 5.

  v4 derives no new number. Every other count and hash here was read from tool output.
- **Consequence ceiling.** Informational. A static design cannot show a returned decision code; only the admitted-frame
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
| R191 | `/home/sicarii/.cache/cosmogony-release-v1.9.1-20260930`, the 1.9.1 release tree cited by OB-003's own `where` list |
| IO8 | `W/work/integrated-ordinary-v8`, the original roster's launcher home |

---

## 0. What changed

### 0.1 From v3 to v4

v3 was reviewed by an independent Claude review subagent in `WT/designs/claude-f32-resolution-v3/review/claude-v1/`.
The verdict was **ENDORSED_WITH_REQUIRED_CHANGES**:

- REVIEW.md sha256 `a7e5dfb2f06e3e39bb2a292cc6804c2042e4977f965e6f6342eab8587787aa11`
- review.json sha256 `9e120e580a283b90f4892b98e16e6a31116a3345e045e8688d2b9b7d78ef07a3`

That review closed RC-1 through RC-5 and notes 1, 2, 4, 5 and 6. It found note 3 PARTIALLY_CLOSED and raised RC-6. v4
changes only RC-6 and N-1 through N-4.

The patch is unchanged. `f32-r-a.patch` here is byte-identical to the v1, v2 and v3 copies:

- sha256 `226e7fc871b7f17622f7ea2480725644d1ab527765a391157af8b24e5f136650`
- `cmp` against v3's copy reports identical.

| Item | What v4 does | Where |
|---|---|---|
| **RC-6** Re-targeting the roster launches | Corrects v3's "cwd re-targeted" statement. A launch's recorded cwd does not select the source; the runner does. `IO8/run_checks.py` (`b047481f…`) hard-binds `source = root/'source'` (:8-9) and launches the child with `cwd=source` (:36). It sets `PYTHONPATH` and `WORLDLINE_CORE_LIB` from that source (:52-53) and writes receipts under its own `evidence/` (:47-48). Each cited launch's `launcher_argv` names that runner (ORIGINAL-ORDINARY-ROSTER.json:2191, :2216, :2391). **Re-targeting therefore means re-targeting the launcher**: the `run_checks.py` path in `launcher_argv`, and with it the receipt and scope unit, become a runner co-located with the integrated candidate. That runner's bytes must match `b047481f…` except for recorded, reviewed path differences, as in the roster's own re-based pattern (:3, :20). `child_argv`, mode, label and environment stay unchanged. A run through the unchanged IO8 launcher executes `IO8/source` and earns no F32 credit | §7, §8, §9 |
| N-1 Wording | Says "a 1.9.1-era control" throughout, because R191 has several transaction-level AUTHORIZED assertions. The open identity question is not pre-empted | §0.2, §1, §4, §7 |
| N-2 Table cell | Corrects the `phase1-native-lifetime` cell. :2855 and :2891 carry hashes; only :1479 and :1483 are path-only | §2 item 4 |
| N-3 STATUS drift | Cites STATUS.md at the hash this author read, `985dfcaa…`, with line numbers for that read. That read is a byte snapshot taken once so that the hash and the line numbers agree | §8, §10, evidence.json |
| N-4 D1 v5 | D1 v5 exists and binds the pre-R-A bytes at DESIGN.md:168. That file is still being edited: this author read it at sha256 `f150e0af…`, then `daecd389…`, then `aab19886…`, then `004b524a…` (the last is the snapshot recorded in evidence.json), and :168 held the pre-R-A bytes each time. The re-bind obligation is restated as "the first revision after R-A is composed" | §2 item 5, §7, §8 |

Nothing else changed from v3.

### 0.2 From v2 to v3 (history)

v2 was reviewed in `WT/designs/claude-f32-resolution-v2/review/claude-v1/`. The verdict was ENDORSED_WITH_REQUIRED_CHANGES
(REVIEW.md `865691006b593ed4559ceb755e54ba4c888b737fe6b15da35132431a339fff28`, review.json
`b8b27d23afa2d4c3e7867f4de7eed700210053c590b5cc399a01864269787746`).

| Item | What v3 did | Where |
|---|---|---|
| **RC-5** Identity of OB-003's "1.9.1 control" | Withdrew v2's identification. The judge-mutation refusal family (S5 `test_transaction.py:276-329`) and `test_typed_absence.py:1238-1252` were added after 1.9.1. Named a 1.9.1-era transaction-level AUTHORIZED control, `test_clean_commit_exchanges_mapping_and_links_receipt` (R191 :118-121; S5 :148-151). Which control OB-003 means, and whether its positive leg holds under the same `_freshness` double, stay OPEN in OB-003 | §1, §4, §7, E5 |
| Notes | Recorded the eight checkpoint files (8-3 = 5). Re-targeted the roster cwd, which v4 corrects through RC-6. Added the null-metadata static reasoning, labelled unverified. Routed the A1 count through JACKAL (1+2 = 3). Corrected the R-D wording. Updated the live STATUS citation | §2, §5, §7, §11 |

### 0.3 From v1 to v2 (history)

v1 was reviewed in `WT/designs/claude-f32-resolution-v1/review/claude-v1/`. The verdict was ENDORSED_WITH_REQUIRED_CHANGES
(REVIEW.md `b491d9d24127411e485b48751bc8a16846b95532dacd962db9f3c69196717681`, review.json
`98e7dbe14a6dae6a6c77ed65325fe5561849f4f9d176ff49476adb76d31f0d7b`).

v2 then made these changes:

- **RC-1:** the complete inventory, including the metadata-tests double collection and the lifetime :92-105
  differential.
- **RC-2:** the baseline must hold every A1–A4 module.
- **RC-3:** the AUTHORIZED requirement on A1–A4 was attributed to the preserved-controls rule.
- **RC-4:** all three inventories that record the patched files.
- **Notes:** Claude review wording, revalidation wording, the live STATUS citation, and lanes in flight.

---

## 1. Summary

**The conflict is in one fixture, not in the requirements.** OB-003 and the four AUTHORIZED controls (A1–A4) conflict
only through one fixture derivation that item1 V2 left inconsistent.

**Where A1–A4's AUTHORIZED requirement comes from.** It comes from the preserved-controls rule, not from OB-003:

- "original deterministic fixtures and controls cannot be reduced to obtain a pass" (O/WORKSPACE-RULES.md:6).
- "Keep every original contract, accepted case, fixture, control … fixed" (RECOVERY-AND-AUTONOMY.txt:5).
- The original ordinary roster's launches for the three modules (O/ORIGINAL-ORDINARY-ROSTER.json :2174-2198,
  :2199-2223, :2374-2398).
- REQUIRED-LIFETIME-CONTROLS.json:3-24.

Each of A1–A4 asserts that a fully bound candidate evaluation is AUTHORIZED when its requirement is unchanged and its
matching context is complete.

**OB-003 needs its own positive case.** OB-003's acceptance test refuses requirement-changing candidates "while the
1.9.1 control is AUTHORIZED" (O/OBLIGATIONS-v2.json:95). That control is transaction-level, not one of A1–A4.

- **What v2 got wrong.** v2 named the judge-mutation refusals (`tests/test_transaction.py:276-329`) and
  `tests/test_typed_absence.py:1238-1252` as that control. Neither exists in 1.9.1.
  - The judge-mutation method is absent from R191 `tests/test_transaction.py` and from pre-item1
    `ENG/source/tests/test_transaction.py`. It first appears in item1 V1 (V1 `tests/test_transaction.py:276`).
  - `test_original_positive_commit_retains_the_measured_staged_requirement` is absent from R191 and from pre-item1
    `test_typed_absence.py`, which have the same sha256, `2d618967…`. It is an item1-repair addition
    (W/work/item1-repair/HANDOFF.md:34-36).
- **A 1.9.1-era control.** One transaction-level AUTHORIZED control that does exist in 1.9.1 is
  `test_clean_commit_exchanges_mapping_and_links_receipt`. It is at R191 `tests/test_transaction.py:118-121` and S5
  :148-151, and asserts `prepared.decision == "AUTHORIZED"`.
- **What stays open.** This design does not establish which control OB-003 means, or whether its positive leg holds
  under the same `_freshness` pass-through double. Both stay OPEN as part of OB-003. S5's judge-mutation family contains
  only the three refusals, with no unmutated AUTHORIZED leg under the double.
- **The requirements are compatible.** Both want an unchanged-requirement candidate authorized and a changed one
  refused.

**How the inconsistency arose.**

- **Item1 V1 kept the two consistent.** It gave the shared fixture `resulting_requirement=h(8)`, equal to its
  `current_requirement` (V1 test file :530). The candidate-mode helpers inherited that value implicitly.
- **Item1 V2 broke it.** It had to make that slot absent for checkpoint mode, so it set the fixture to `None` (V2 :530).
  The two candidate-mode helpers built from the fixture were not updated, and V2's own HANDOFF declares only the
  checkpoint change (V2 HANDOFF.md:5, :9).

**Recommendation: R-A.**

- **The change.** The two candidate-mode helpers, `bound_request` and `collapse_values`, explicitly supply
  `resulting_requirement` equal to the fixture's own `current_requirement`. That is exactly the value item1 V1
  produced, and it matches how the helpers already supply `evaluated_requirement` on the line above.
- **What stays unchanged.** Every assertion, the kernel, the wire, the ABI, the contracts, the production producers,
  and the checkpoint fixture, which keeps `None`. The assert-call ASTs are identical and in the same order.
- **Size.** Two keyword arguments in two helper functions, appended on existing lines. No other line number moves.

**Who decides.** The lead. This is routine, reversible engineering that preserves the original external contract and
success domain. It is not an API or contract redefinition (§10). The obligation stays OPEN until both of these exist:

- independent review by a Claude review subagent, under the human's 2026-10-05 ~17:05Z direction;
- the admitted-frame matching-source runs in §9.

---

## 2. Re-verification of the F32 FINDINGS against source

Each claim the design relies on was re-read at S5 unless another tree is named.

| FINDINGS claim | Verified at | Result |
|---|---|---|
| The checkpoint fixture has `current=h(8)`, `resulting=None` and `roster_complete=False` | `tests/test_raw_evaluation_default.py:522-533`, values at :526 and :530 | confirmed |
| `bound_request` switches to candidate mode and does not set `resulting_requirement` | same file :71-81 | confirmed |
| `collapse_values` does the same | `tests/test_finalization_kernel.py:245-255` | confirmed |
| Four AUTHORIZED assertions | raw :88-89; finalization :262-263; row projection :95-96 (method :86-99); lifetime :162-163 (method :152-168) | confirmed |
| `CollapseInput` has no defaults | `runtime/worldline/core.py:214-258` (docstring :216) | confirmed |
| `None` encodes absent, with all-zero bytes | `runtime/worldline/core.py:595-598` | confirmed |
| Wire field order | `core.py:120-122` and `core/worldline-collapse_wire.ads:55-57` | confirmed |
| Candidate mode accepts an absent Resulting; checkpoint mode requires it absent | `core/worldline-collapse_wire.ads:89-137`, specifically :132-136 | confirmed |
| Decode keeps presence | `core/worldline-collapse_wire.ads:237` | confirmed |
| Candidate mode requires Resulting present | `core/worldline-collapse.ads:148-154` (:151) | confirmed |
| Evidence requires `Same(Current, Resulting)` | `core/worldline-collapse.ads:184-195` (:188) | confirmed |
| `Post` makes Authorized equivalent to `All_Hold` | `core/worldline-collapse.ads:213-217` | confirmed |
| `Same` is false when either side is absent | `core/worldline-identities.ads:80-82` | confirmed |
| `Decide` returns EEI when roster readiness is 0, then Identity_Absent | `core/worldline-collapse.adb:20-25` | confirmed |
| The C entry points overwrite only the roster bytes | `core/worldline-c_api.adb:817-819`; `core/evaluation_finalization_c.adb:485-487` | confirmed |
| The Python callers pass the request through unchanged | `runtime/worldline/evaluation_wire.py:94-122`; `runtime/worldline/finalization_kernel.py:286-322` | confirmed |
| `test_collapse_recomputes_carried_roster` and `test_revalidation_binding` set Resulting explicitly | raw :471-490 (:478); `tests/test_revalidation_binding.py:303-318` (:315) | confirmed |
| Lineage hashes | sha256 in the three trees | confirmed (§3) |
| Recorded pre-item1 runs | `B/phase1-evaluation-checked-scan-ordinary-v1/evidence/default-tests-v1`; `B/phase1-finalization-ordinary-v2/evidence/default-tests-v1` | confirmed (below) |

In both recorded runs:

- `child.stderr` line 4 reads "test_complete_owned_join_and_padded_epoch … ok", line 44 reads "Ran 41 tests", and
  line 46 reads "OK".
- The returncode is 0 in `child-wait.json` and in `result.json`.
- The test file listed under `inputs/` has sha256 `53db45a0…`, the pre-item1 bytes.
- The runs were read as found and are not authenticated.

**One FINDINGS inference is weaker than stated.** FINDINGS says `bound_request` is absent from V1's
`original-methods.json`. That is true but uninformative. The list names only `test_*` methods, so it also omits
`checkpoint()`, which V1 did change at :530 (V1 `original-methods.json`).

**New static observations** (not in FINDINGS):

1. **R-A cannot open a join mismatch.** The context join compares the request with its projection, modulo the carried
   rosters only (`core/worldline-evaluation_authority.ads:197-199`, :225-226). The synthetic joins in these tests build
   the projection from the request itself (raw :67, finalization :239). Whatever Resulting value the helper supplies
   therefore appears identically on both sides.
2. **On the raw path, metadata is checked only after Decide returns Authorized** (`core/worldline-c_api.adb:857-872`).
   - Consequence: the row-projection refusal at :97-99 corrupts metadata and expects INVALID_REQUEST. It refuses for
     its intended reason only once the positive at :95-96 is reachable.
   - The finalization path joins metadata inside `Context_Joined`, before the decision
     (`core/evaluation_finalization_c.adb:399-409`, :473-484). So `test_finalization_kernel.py:264-266` is not
     affected.
   - The actual codes are a run question (§9).
3. **The lifetime module needs no edit.**
   - Its oracle pins (`tests/test_context_cast_lifetime.py:19-37`, :73-77) bind
     `oracle_finalization_kernel_cast_lifetime.py` and `oracle_evaluation_context_cast_lifetime.py`, not
     `test_finalization_kernel.py`.
   - It reaches the request only through `self.fixture.collapse_values()`, at :95, :109, :122, :137 and :154.
4. **Historical checkpoint inventories.** S5's `assurance/checkpoints/` holds eight files. Three record the patched
   test files; the other five record neither file (JACKAL exact, parsed=8-3, exact=5). The five are
   `phase1-native-2026-10-03.json`, `phase1-native-cached-2026-10-03.json`, `phase1-native-frozen-2026-10-03.json`,
   `phase1-native-kernel-filter-2026-10-03.json` and `phase1-native-metadata-2026-10-03.json`.

   What the three record:
   - Each records `test_finalization_kernel.py` with sha256 `76141dfb…`. These are the current bytes, which R-A will
     change.
   - Each records `test_raw_evaluation_default.py` with sha256 `53db45a0…`. These are the pre-item1 bytes, which
     already differ from S5's `22b5b189…`.
   - Two also record `test_evaluation_row_projection.py` as `74a19597…`. R-A does not change that file.
   - `phase1-native-lifetime-2026-10-03.json` also lists both patched paths at :1479 and :1483, without hashes.

   Nothing reads them: a grep of S5's `*.py`, `*.sh` and `*.gpr` for `assurance/checkpoints`, `phase1-2026-10-02`,
   `phase1-bound-loader` and `phase1-native-lifetime` returns nothing.

   | Inventory | `test_finalization_kernel.py` `76141dfb…` | `test_raw_evaluation_default.py` `53db45a0…` | `test_evaluation_row_projection.py` `74a19597…` |
   |---|---|---|---|
   | `assurance/checkpoints/phase1-2026-10-02.json` | :2276-2279 (path and hash) | :2456-2459 (path and hash) | :2241-2244 (path and hash) |
   | `assurance/checkpoints/phase1-bound-loader-2026-10-02.json` | :2452-2455 (path and hash) | :2632-2635 (path and hash) | :2407-2410 (path and hash) |
   | `assurance/checkpoints/phase1-native-lifetime-2026-10-03.json` | :2854-2855 (path and hash); path-only listing at :1479 | :2890-2891 (path and hash); path-only listing at :1483 | — |

5. **Frozen lanes in WT bind the pre-R-A bytes of both test files:**
   - `WT/packets/capi-pk0-v2/packet.json:198-199`;
   - `WT/designs/claude-native-bigint-d1-design-v4/DESIGN.md:191`;
   - `WT/designs/claude-native-bigint-d1-design-v5/DESIGN.md:168`. That file is still being edited: this author read it
     at sha256 `f150e0af…`, `daecd389…`, `aab19886…` and `004b524a…`, the last recorded in evidence.json, and :168 held the pre-R-A
     bytes at each read. D1 v5 was authored
     after v3 and did not re-bind.

   R-A changes those inputs. So the first revision of each lane after R-A is composed must re-bind to the integrated
   source. Existing revisions are never edited in place, and any run or proof they take on pre-R-A bytes earns no F32
   credit (§8).
6. **Full inventory of controls R-A affects or whose meaning it changes.** All assertions are unchanged.
   - **A1, `test_complete_owned_join_and_padded_epoch` (raw :83-90).** It is collected three times (JACKAL exact,
     parsed=1+2, exact=3):
     - once in default-tests, as `test_raw_evaluation_default.RawRequiredFailureControls`;
     - twice in metadata-tests. `test_evaluation_row_projection.py` imports `RawRequiredFailureControls` at module level
       (:12), subclasses it (:20), and defines no `load_tests`. So the loader collects both
       `MetadataNativeControls.test_complete_owned_join_and_padded_epoch` and the imported
       `RawRequiredFailureControls.test_complete_owned_join_and_padded_epoch`.
     - The recorded pre-item1 metadata runs show this in both roots. In `metadata-tests-v1/child.stderr`, line 3 is the
       `MetadataNativeControls` instance and line 47 the `RawRequiredFailureControls` instance, both "ok". Line 82
       reads "Ran 79 tests" and line 84 reads "OK". The listed inputs are `test_evaluation_row_projection.py`
       `74a19597…` and `test_raw_evaluation_default.py` `53db45a0…`.
   - **The raw :92-160 refusal twins**, which all use `bound_request.`
     - Each is collected in default-tests once and in metadata-tests twice, once under each class. Examples:
       `test_same_legacy_hashes_do_not_join_another_full_subject` at stderr :40 and :79;
       `test_context_preserves_all_ordered_actual_rows` at :10 and :54.
     - Their assertions are unchanged. Under R-A each gains a reachable positive baseline.
   - **A2** (fin :257-266) and its twins (fin :268-280).
   - **A3** (row :86-99), including the metadata refusal at :97-99. Also row :105-110.
   - **A4** (lifetime :152-168).
   - **`test_original_whole_projection_context_metadata_and_native_conjunction` (lifetime :92-105),** listed in
     REQUIRED-LIFETIME-CONTROLS.json:5.
     - For `status` in PASS and FAIL, it builds old and new prepared graphs from `collapse_values()` (:95). It asserts
       equal snapshots (:99, :105) and `new_result == old_result` (:100-104).
     - At S5, its PASS iteration compares two refusals: Identity_Absent, Execution_Evidence_Incomplete or
       INVALID_REQUEST.
     - Under R-A, the PASS iteration becomes a real differential on the authorized path. Old and new transport are
       compared where the native decision can return AUTHORIZED. This restores the intended meaning, weakens nothing,
       and leaves the assertion unchanged.
     - The actual codes at :100-103 for both statuses are recorded as evidence only (§9 E4). They are not a new
       criterion.
   - **Lifetime :107-118** (`test_original_conjunct_mutations_refuse_with_unchanged_results`). Its INVALID_REQUEST
     refusals come from the join, so they are unchanged. It gains a reachable positive baseline.
   - **Lifetime :120-133 and :135-150.** These call `collapse_values()` and join, but never decide. The join is
     unaffected (item 1).
   - **Not affected:**
     - `producer_case` calls `bound_request` (raw :217) but overrides `resulting_requirement` explicitly (raw :224).
     - `staged_journal` and `test_recovery_packet_producer.py` inherit that override. That module also restricts its
       collection with `load_tests` (:207-212).
     - `test_finalization_cast_lifetime.py` and `test_tagged_object_cursor.py` never call `collapse_values`.
     - `test_revalidation_binding.py:303-323` builds its own request.
     - Raw :457 is a history-selector reason, and raw :492 uses a separate literal request.

---

## 3. Original intent of each control, and what "original fixture" means here

### 3.1 Lineage of the bytes

| Tree | `test_raw_evaluation_default.py` | `test_finalization_kernel.py` | `worldline-collapse.ads` | Candidate-mode request built by the helpers |
|---|---|---|---|---|
| ENG/source (pre-item1) | `53db45a0…` | `76141dfb…` | `ba6e2a53…`: no Resulting at all (`ENG/source/core/worldline-collapse.ads:135-152`, :180-189) | No such field; AUTHORIZED reachable |
| V1 source | `979e4639…` | `76141dfb…` (unchanged) | `98b2661b…`: OB-003 conjunct added | Fixture `resulting=h(8)` (V1 :530), so the helpers carry `h(8)` = current; AUTHORIZED reachable |
| V2 source = item1-repair = S5 = integrated-ordinary-v8 | `22b5b189…` | `76141dfb…` (unchanged) | `98b2661b…` | Fixture `resulting=None` (V2 :530), so the helpers carry None; AUTHORIZED unreachable |

- **Wire spec.** V1 is `c09c0dcd…`; V2 and S5 are `987b3fa7…`. V2's wire change adds
  `R.Resulting_Requirement.Present = 0` to the checkpoint-mode slot rule (V2 `core/worldline-collapse_wire.ads:132-136`).
- **V2's changed files.** Exactly seven:
  - `core/worldline-collapse_wire.ads`
  - `runtime/worldline/evaluation_context.py`
  - `runtime/worldline/proof_manifest.py`
  - `runtime/worldline/transaction.py`
  - `tests/test_core_abi.py`
  - `tests/test_raw_evaluation_default.py`
  - `tests/worldline_collapse_checks.adb`

### 3.2 Intent per control

**A1: raw :83-90, `test_complete_owned_join_and_padded_epoch`.**

- Present since pre-item1, with unchanged method bytes. It is outside V1's changed-method list.
- Intent: a complete owned join with a padded epoch is AUTHORIZED, and the request bytes are not mutated.
- Evidence: the recorded pre-item1 default runs report "ok".
- It is collected in default-tests once and in metadata-tests twice (§2 item 6). The recorded pre-item1 metadata runs
  report "ok" for both metadata-tests instances.
- The raw :92-160 twins share the same collection.

**A2: finalization :257-266, `test_additive_finalization_collapse_requires_full_context_and_metadata`.**

- The file has never changed.
- Intent: a full finalization context and metadata give AUTHORIZED, and removing the metadata gives INVALID_REQUEST.

**A3: row projection :86-99, `test_default_join_requires_projection_and_keeps_legacy_layout`.**

- Never changed: `74a19597…` in every tree.
- Intent: the default join with projection is AUTHORIZED, the legacy layouts stay queryable, and corrupted metadata
  gives INVALID_REQUEST.
- Evidence: the pre-item1 `metadata-tests-v1` runs report "ok".

**A4: lifetime :152-168, `test_discarded_full_prepared_graph_releases_without_cyclic_collection`.**

- One version only, `f6bc3e2f…`.
- Intent: a fully joined prepared graph decides AUTHORIZED, then releases without cyclic GC.
- Required: it is listed in O/REQUIRED-LIFETIME-CONTROLS.json:3-24, which says "ALL remain required", status UNRUN.

**Lifetime :92-105, `test_original_whole_projection_context_metadata_and_native_conjunction`.**

- Same module and lineage as A4; listed in REQUIRED-LIFETIME-CONTROLS.json:5.
- Intent: for both a PASS and a FAIL capture, the new transport produces the same complete snapshot and the same native
  decision as the original transport.
- With R-A, the PASS case compares the two on the path where authorization is possible. That is the strong form of its
  intent (§2 item 6).

**The shared derivation.** All of these take their request from `RawDependencyControls.checkpoint()` with these
replacements:

- mode CANDIDATE_EVALUATION;
- `evaluated_requirement` := the fixture's `current_requirement`;
- `executed_verifiers` := the fixture's `declared_verifiers`;
- the checkpoint slots cleared.

The common premise is an unchanged-requirement candidate: the evidence was evaluated against the current requirement,
and nothing changed that requirement.

- Before item1 the kernel had no Resulting input, so the premise was implicit.
- Item1 V1 made it explicit. The kernel gained the conjunct, and the fixture's Resulting became `h(8)` = current.
- V1's HANDOFF states the rules: "valid typed/raw fixtures explicitly supply their actual resulting identity" (V1
  HANDOFF.md:11) and "There is no defaulting to current/evaluated" (:5).

### 3.3 What "original fixture" means for these helpers

Item1 is itself a repair in the lineage, so "original" has three layers:

1. **Pre-item1 bytes.** These hold the original controls and assertions. The request field did not exist.
2. **Item1 V1.** This is the first fixture in the post-OB-003 domain. Its candidate derivations produce a present
   Resulting equal to current, which is the faithful translation of the pre-item1 premise.
3. **Item1 V2.**
   - It is original for checkpoint fixtures, which must carry absence. V2's new controls enforce this
     (`tests/test_core_abi.py:190-217`; `tests/worldline_collapse_checks.adb:328-341`).
   - It is silent on candidate fixtures. Its HANDOFF says "Valid checkpoint fixtures explicitly supply absence" and "V1
     original assertions/cases remain, with necessary valid-checkpoint fixture updates" (V2 HANDOFF.md:5, :9).
   - The None that reached the candidate helpers is therefore an undeclared side effect, not a decision.

So the original fixture for the candidate helpers is V1's value: Resulting present and equal to the fixture's current
requirement. The original fixture for `checkpoint()` is V2's None. R-A preserves both. The alternatives in §5 each break
one of them.

**Value-level check.** This is static: `ast` on scratch copies in v1, independently reproduced by the reviews of v1, v2
and v3.

- After R-A, the request `bound_request` builds equals the literal request at raw :473-481 keyword-for-keyword, over all
  35 keywords.
- That literal belongs to `test_collapse_recomputes_carried_roster`. Item1 V1 updated it (`resulting_requirement=h(8)`
  at :478), and it asserts AUTHORIZED at :490.
- Before R-A, the only difference was `resulting_requirement`: None against `h(8)`.
- `collapse_values` makes the identical replacement on the identical fixture.

---

## 4. Is this a genuine requirement conflict?

No. The two requirement families are jointly satisfiable, and the source already contains controls that satisfy both.

**The AUTHORIZED requirement on A1–A4** comes from the preserved-controls rule:

- O/WORKSPACE-RULES.md:6: "Contracts, accepted cases, proof scope/coverage/floors, original deterministic fixtures and
  controls cannot be reduced to obtain a pass".
- RECOVERY-AND-AUTONOMY.txt:5: "Keep every original contract, accepted case, fixture, control, proof scope/floor and
  checked assertion fixed".
- The roster launches: O/ORIGINAL-ORDINARY-ROSTER.json :2174-2198, :2199-2223, :2374-2398. At :2600-2605 the roster
  records "results_transferred": false and "source_matching_rerun_required": true.
- O/REQUIRED-LIFETIME-CONTROLS.json:3-24.

**OB-003** (O/ALL-ORIGINAL-OBLIGATIONS.md:47-65; O/OBLIGATIONS-v2.json:80-95).

- **Its closure:** "in Candidate_Evaluation mode Decide requires Same(Current_Requirement, Resulting_Requirement), with
  Resulting_Requirement recomputed from the staging payload at prepare and at commit".
- **Its acceptance test:** requirement-changing candidates refuse REQUIREMENT_CHANGED "while the 1.9.1 control is
  AUTHORIZED" (:95). That control is transaction-level and separate from A1–A4.
  - **It is not the judge-mutation family or `test_typed_absence.py:1238-1252`.** Neither exists in R191 or in
    pre-item1 `ENG/source`.
    - The judge-mutation family (`test_transaction.py:276-329`) first appears in item1 V1 (V1
      `tests/test_transaction.py:276`). It contains three refusals and no unmutated AUTHORIZED leg under the
      `_freshness` double.
    - `test_typed_absence.py:1238-1252` was added by item1-repair (W/work/item1-repair/HANDOFF.md:34-36).
  - **One 1.9.1-era candidate.** `test_clean_commit_exchanges_mapping_and_links_receipt` is a 1.9.1-era transaction-level
    AUTHORIZED control (R191 `tests/test_transaction.py:118-121`; S5 :148-151; it asserts
    `prepared.decision == "AUTHORIZED"`).
  - **It is one of several.** R191 has other transaction-level AUTHORIZED assertions, for example:
    - `tests/test_freshness.py:90`
    - `tests/test_typed_absence.py:134`
    - `tests/test_lifecycle_integrity.py:283`
    - `tests/test_private_world_flow.py:71`
  - **Still open.** This design does not establish which control OB-003 means, nor whether its positive leg holds under
    the same `_freshness` pass-through double. Both remain OPEN within OB-003.
- **OB-003 and A1–A4 are compatible.** OB-003 does not require A1–A4 and does not conflict with them. Both require an
  unchanged-requirement candidate to be authorized.

**Controls that satisfy both today:**

- `tests/test_core_abi.py:219-254` asserts AUTHORIZED for `resulting=h(8)=current`, REQUIREMENT_CHANGED for `h(99)`, and
  IDENTITY_ABSENT for None.
- Raw :471-490 asserts AUTHORIZED with `resulting=h(8)`.
- `tests/test_revalidation_binding.py:303-318` supplies an explicit Resulting at :315. It is the same policy
  `requirementHash` identity as the current requirement at :314, not a separately measured value.

**What A1–A4 actually require** is an unchanged-requirement candidate. Nothing in them requires an absent Resulting;
that absence reached them only through V2's fixture side effect.

**Reclassification.** F32-CONFLICT should be reclassified. It is not "two original requirements conflict"; it is "a
fixture-consistency defect introduced at item1 V2, with the requirements jointly satisfiable". The obligation stays OPEN
until §9 is satisfied.

---

## 5. Candidate resolutions

Notation:

- **A1–A4** are the four AUTHORIZED controls (§3.2).
- **CK** is the V2 checkpoint-absence controls: raw :535-550, `test_core_abi.py:190-217` and
  `worldline_collapse_checks.adb:328-341`.
- **OB3-C** is the OB-003 explicit controls (`test_core_abi.py:219-254`), plus OB-003's own acceptance test and its
  mutant obligation.

| ID | Resolution | OB-003 | A1–A4 assertions | CK | Contract / API | Verdict |
|---|---|---|---|---|---|---|
| **R-A** | `bound_request` and `collapse_values` supply `resulting_requirement` = the fixture's own `current_requirement` (the V1 value). No assertion changes | unchanged | unchanged, and reachable again | unchanged (`checkpoint()` keeps None) | unchanged | **RECOMMENDED** |
| R-A′ (cosmetic variant of R-A) | Same values, with the keyword on its own new line or in a shared `candidate()` helper | unchanged | unchanged | unchanged | unchanged | Acceptable. It shifts cited line numbers and touches more lines, so R-A is preferred for minimality |
| R-B1 | Kernel: in candidate mode, absent Resulting counts as Same or is not required | **weakened**: contradicts the closure text and `Same`'s "two absent values are never the same" (`worldline-collapse.ads:27-28`; `worldline-identities.ads:80-82`) | pass | unchanged | changes `Required_Present`, `Evidence_Holds`, `Post` and the proved contract | **REJECTED.** Absence would acquire authority, which `complete-phase1-prompt.txt:34` and :42 and `O/HANDOFF.md:119` forbid. It also breaks OB3-C `test_core_abi.py:248-249` (IDENTITY_ABSENT) |
| R-B2 | Python/C marshalling fills Resulting := Current when None in candidate mode | **weakened**: Resulting is copied instead of recomputed from the staging payload (OB-003 closure; `worldline-collapse.ads:60-61`) | pass | unchanged | Python gains an independent authorization input | **REJECTED.** Contradicts "no defaulting to current/evaluated" (V1 HANDOFF.md:5; V2 HANDOFF.md:5) and "Python has no independent definition of authorization" (`O/HANDOFF.md:27`). It also breaks OB3-C :248-249 at the Python boundary |
| R-B3 | Kernel: reorder the refusals in `Decide` | unchanged | still not AUTHORIZED, because `Post` makes Authorized ⇔ `All_Hold` (`worldline-collapse.ads:217`) | unchanged | body only | **REJECTED.** Resolves nothing |
| R-B4 | Remove or soften the OB-003 conjunct | **removed** | pass | n/a | contract lowered | **REJECTED.** A direct weakening; it also fails OB-003's mutant/proof-gate test |
| R-C1 | Change the four assertions to expect IDENTITY_ABSENT or EEI | unchanged | **weakened**: the accepted case is removed | unchanged | unchanged | **REJECTED.** Removes accepted successes (`O/WORKSPACE-RULES.md:6`; `RECOVERY-AND-AUTONOMY.txt:5`) |
| R-C2 | Skip, xfail or delete the four controls | unchanged | **removed** | unchanged | unchanged | **REJECTED** for the same reasons. The roster also requires them (`O/ORIGINAL-ORDINARY-ROSTER.json` entries at :2174-2198, :2199-2223, :2374-2398; `REQUIRED-LIFETIME-CONTROLS.json`) |
| R-D | Restore `checkpoint()` to `resulting=h(8)`, undoing the V2 fixture change | unchanged | pass | **broken**: a checkpoint request with Resulting present is malformed (`collapse_wire.ads:132-133`) | unchanged | **REJECTED.** It trades one set of failing controls for another. Raw :535-543 (AUTHORIZED, `valid: True`), raw :545-550 and CK would refuse INVALID_REQUEST or change their dependency answers. `test_finalization_kernel.py:282-289` compares `collapse_decide_with_evaluation` with `collapse_decide` on the same request. It would therefore pass vacuously (INVALID_REQUEST = INVALID_REQUEST) instead of refusing, and would stop showing the ignored-data semantics it checks. The rejection stands |
| R-E | Revert V2's checkpoint-absence wire rule as well as the fixture | unchanged in candidate mode | pass | **removed** | wire contract lowered | **REJECTED.** Weakens typed absence ("A slot the question does not consult must be empty", `collapse_wire.ads:126-127`), reverses a reviewed V2 repair, and breaks CK |
| R-F | Rebuild the four controls on the real producer path (`bind_selected` with `resulting_requirement=policy`, as `producer_case` does at raw :162-226) | unchanged | the assertion text could stay, but the control mechanism changes from a synthetic TEST_ONLY join to a producer join | unchanged | unchanged | **REJECTED as unnecessary.** It replaces what the original controls exercise (padded epoch, synthetic owned context, metadata layout) and goes beyond the minimal consistent repair. Producer-path coverage already exists (raw :228-249, :358-380; `test_recovery_packet_producer.py:40-53`) |
| R-G | Treat this as a reserved contract decision and escalate to the operator | — | — | — | — | **Not warranted.** R-A preserves the contract and the success domain (§10). Escalating would invent an approval gate (`RECOVERY-AND-AUTONOMY.txt:7`) |
| R-H (optional, additive) | Add new paired refusal controls next to R-A, for example a raw-path `bound_request` variant with `resulting=h(99)` expecting REQUIREMENT_CHANGED | unchanged (strengthened) | unchanged | unchanged | unchanged | **Optional.** Not needed to close F32. If adopted, it is a separate additive control with its own review and replaces nothing |

**Why `test_finalization_kernel.py` cannot stay byte-identical.**

- `collapse_values` builds its request only from `RawDependencyControls.checkpoint()` plus fixed replacements
  (`test_finalization_kernel.py:245-251`).
- `checkpoint()` must keep `resulting=None`, which rules out R-D and R-E.
- The only way to supply Resulting without weakening OB-003 (R-B) or the assertions (R-C) is therefore inside
  `collapse_values`.

That is the minimum byte change the requirements allow, and it restores the request value V1 produced for this unchanged
method.

---

## 6. Exact proposed diff (R-A)

The patch is authored against S5. It also applies to the two patched files as they stand in `W/work/item1-repair/source`
and `IO8/source`, which hold the same bytes for those files.

**Applying it there is not enough.** Neither tree contains the A4 module `tests/test_context_cast_lifetime.py`, its
sibling `tests/test_finalization_cast_lifetime.py`, or the oracle files `tests/oracle_*_cast_lifetime.py`. Those exist
in S5 (`f6bc3e2f…`, `d9ae6698…`, `fe91b945…` and `b8b0d136…`). The baseline requirement is in §8.

`f32-r-a.patch` in this directory has sha256 `226e7fc871b7f17622f7ea2480725644d1ab527765a391157af8b24e5f136650` and is
byte-identical to the v1–v3 copies:

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

**Identities.** Read from `sha256sum` output in v1 and reproduced by all three reviews.

| Item | Before (S5) | After (post-image) |
|---|---|---|
| `tests/test_finalization_kernel.py` | `76141dfb2ddea1c9fb62e5ea09d27830432e96273f85e984da94f5ebbafb4a62` | `4da992ddfd206134131c31ea306fc19d46500ca8501a5214e540f55357327aa4` |
| `tests/test_raw_evaluation_default.py` | `22b5b189f9686f456214666b5a4dc4b0e3c93ee5b48f983b18994f8119f1a4f0` | `77f0cb999bca30a6eaa1ec663e21ee9cb152f405cb1ae1a591a20465ffad7262` |
| `f32-r-a.patch` | — | `226e7fc871b7f17622f7ea2480725644d1ab527765a391157af8b24e5f136650` |

**Static scope check.** This used `ast` only in v1, with nothing imported or run, and was reproduced by all three
reviews.

- `test_raw_evaluation_default.py`
  - Methods: 43 before and 43 after. The only change is `('RawRequiredFailureControls', 'bound_request')`.
  - Assert-call ASTs: 62 before and 62 after, identical and in order.
- `test_finalization_kernel.py`
  - Methods: 26 before and 26 after. The only change is `('FinalizationNativeControls', 'collapse_values')`.
  - Assert-call ASTs: 38 before and 38 after, identical and in order.
- Line counts are unchanged: 561 and 289.

---

## 7. R-A against each original requirement

| Requirement | Where | Effect of R-A |
|---|---|---|
| OB-003: Same(Current, Resulting), presence, Requirement_Changed | `worldline-collapse.ads:148-154`, :184-195, :213-217, :269-272; `.adb:41-45` | No byte change; the contract pin is unaffected |
| OB-003 explicit native controls | `test_core_abi.py:219-254` | Unchanged; still required |
| OB-003's transaction-level "1.9.1 control" | `OBLIGATIONS-v2.json:95`. A 1.9.1-era transaction-level AUTHORIZED control is `test_clean_commit_exchanges_mapping_and_links_receipt` (R191 `test_transaction.py:118-121`; S5 :148-151); R191 has others (§4). The post-1.9.1 judge-mutation refusals are at S5 `test_transaction.py:276-329`, and the item1-repair positive at `test_typed_absence.py:1238-1252` | Unchanged and still required. Separate from A1–A4. Which control OB-003 means, and whether its positive leg holds under the `_freshness` double, stay OPEN in OB-003 |
| Production recomputes Resulting independently | `transaction.py:364-366`, :745-750, :1118-1120; `evaluation_context.py:419-426` | Unchanged. R-A touches only TEST_ONLY synthetic helpers. Those helpers already supply every other identity as a synthetic `h(n)`, including `evaluated_requirement` = current on the line above |
| No defaulting to current/evaluated | V1 HANDOFF.md:5; V2 HANDOFF.md:5 | Preserved. No producer or encoder default is added; the value is explicit test input, as V1 HANDOFF.md:11 requires |
| Typed absence: equality of absent values never authorizes | `complete-phase1-prompt.txt:42`; `O/HANDOFF.md:119` | Preserved; the positive now carries a present value |
| V2 checkpoint absence | `collapse_wire.ads:126-136`; CK | Unchanged; `checkpoint()` keeps None |
| A1–A4 accepted cases (preserved-controls rule) | raw :88-89, fin :262-263, row :95-96, lifetime :162-163 | Assertions unchanged. They become reachable, given native readiness and the join |
| A1 and the raw :92-160 twins as collected in metadata-tests | `test_evaluation_row_projection.py:12`, :20 (no `load_tests`); recorded `metadata-tests-v1/child.stderr` :3, :47, :82 | The same unchanged assertions run under both `MetadataNativeControls` and `RawRequiredFailureControls`. R-A affects each instance identically |
| Refusal twins in the same modules | raw :92-160; fin :264-266, :268-280; row :97-99, :105-110; lifetime :107-118 | Assertions unchanged. Each now has a reachable positive baseline, so its refusal can be attributed to the mutated conjunct. For row :97-99 that was not possible before (`c_api.adb:862-868`) |
| Lifetime differential `test_original_whole_projection_context_metadata_and_native_conjunction` | lifetime :92-105; REQUIRED-LIFETIME-CONTROLS.json:5 | Assertion unchanged. The PASS iteration moves from comparing two refusals to comparing on the authorized path, which restores its intended strength. The codes at :100-103 are recorded as evidence only |
| Lifetime join-only controls | lifetime :120-133, :135-150 | Unaffected: no decision is made, and the join is unchanged |
| Lifetime module bytes and oracle pins | `test_context_cast_lifetime.py` (no edit); pins at :19-20 | Unaffected; bytes stay `f6bc3e2f…` |
| Python has no independent authorization | `O/HANDOFF.md:27` | Unchanged; the native kernel decides |
| Proof scope, floors, CONTRACT_PINS and Ada bodies | `proof-manifest.json`, `prove.sh` | No Ada, C or proof-manifest change. The full matching-source strict proof stays required for Phase One, independently of F32 |
| Original ordinary roster (RC-6) | `ORIGINAL-ORDINARY-ROSTER.json` :2174-2198, :2199-2223, :2374-2398, :2600-2605. Each launch's `launcher_argv` names `IO8/run_checks.py` (:2191, :2216, :2391), with receipts under `IO8/evidence` (:2196, :2221, :2396). That runner (`b047481f…`) hard-binds `source = root/'source'` (:8-9), the child `cwd=source` (:36), `PYTHONPATH` and `WORLDLINE_CORE_LIB` from that source (:52-53), its own `evidence/` (:47-48), and the scope-unit prefix (:203) | Each launch keeps its `child_argv`, mode, label and explicit inbound environment. **The launcher is re-targeted**, not only the recorded cwd. The `run_checks.py` path in `launcher_argv`, the receipt and the scope unit become those of a runner co-located with the integrated candidate. That runner's bytes match `b047481f…` except for recorded, reviewed path differences, as in the roster's own re-based pattern (:3, :20). It is provisioned with the co-located inputs it reads (§8). A run through the unchanged `IO8/run_checks.py` executes `IO8/source`, which has no R-A and no lifetime modules, and **earns no F32 credit**. Still applicable: "source_matching_rerun_required": true (:2604) and "results_transferred": false (:2602). The roster has no lifetime launches, so those controls run under REQUIRED-LIFETIME-CONTROLS (E4) |
| Historical checkpoint inventories | Eight files in S5 `assurance/checkpoints/`. Three record the patched files with path and hash: `phase1-2026-10-02.json` :2276-2279 and :2456-2459; `phase1-bound-loader-2026-10-02.json` :2452-2455 and :2632-2635; `phase1-native-lifetime-2026-10-03.json` :2854-2855 and :2890-2891, which also has path-only listings at :1479 and :1483. The other five record neither file (JACKAL exact, 8-3 = 5) | Historical: not edited, and no code reads them. After R-A, all three record a superseded `test_finalization_kernel.py` (`76141dfb…`). They already record the pre-item1 `test_raw_evaluation_default.py` (`53db45a0…`) |
| Lanes binding these bytes | PK-0 v2 `packet.json:198-199`; D1 v4 `DESIGN.md:191`; D1 v5 `DESIGN.md:168` (pre-R-A bytes; that file is still being edited, last read at `004b524a…`) | The first revision of each lane after R-A is composed must re-bind to the integrated source. Existing revisions are never edited in place, and anything run on pre-R-A bytes earns no F32 credit. This is a sequencing task for the lead, not a weakening |

R-A adds no cap, no new refusal, no suppressed assertion or Ghost, and no assumption.

---

## 8. Integration shape

**The baseline must contain every A1–A4 module.** This applies to the R-A lane's baseline and to every source used for
E0–E6. The required modules are:

- `tests/test_raw_evaluation_default.py`
- `tests/test_finalization_kernel.py`
- `tests/test_evaluation_row_projection.py`
- `tests/test_context_cast_lifetime.py`
- `tests/test_finalization_cast_lifetime.py`, the other REQUIRED-LIFETIME-CONTROLS module
- the two `tests/oracle_*_cast_lifetime.py` files pinned by `test_context_cast_lifetime.py:73-77`

That means S5 or a successor in S5's lineage. `IO8/source` and `W/work/item1-repair/source` lack
`test_context_cast_lifetime.py`, `test_finalization_cast_lifetime.py` and both oracle files. E4 therefore cannot be met
on either tree as it stands, and patching only the two test files there would leave A4 and lifetime :92-105 unrun.

1. **Author the delta as its own lane**, following the item1-repair pattern (`W/work/item1-repair/HANDOFF.md`).
   - Use a new complete source copy whose baseline satisfies the requirement above: S5, or the integrated candidate the
     lead selects from S5's lineage.
   - Do not edit S5 itself, because in-progress reviews pin it.
   - Record a forward and reverse patch (`f32-r-a.patch`) and a `changed-paths.json` listing exactly the two test files.
   - Record static preservation: the assert-call ASTs are retained, only the two FunctionDefs changed, and all other
     source bytes, modes and links are unchanged.
2. **Get an independent review** of this design and of the exact delta.
   - The reviewer is a Claude review subagent with a fresh context, not the author. This follows the human's 2026-10-05
     ~17:05Z direction (WT/STATUS.md:279-291).
   - The original texts required actual gpt-6.1-sol and said a Claude review cannot count as that gate (O/HANDOFF.md:173;
     `complete-phase1-prompt.txt:60`).
   - The lead records that no record will claim the GPT-6.1 gate was met (WT/STATUS.md:355-361).
3. **Compose R-A into the integrated candidate** that the admitted frame will build and run.
   - **Re-target the roster launchers (RC-6).** For each roster launch run against the candidate, the launcher must be a
     `run_checks.py` co-located with the candidate, so that its `source = root/'source'` is the candidate.
     - Its bytes must match `IO8/run_checks.py` (`b047481f…`) except for recorded, reviewed path differences. One
       example is the scope-unit prefix at :203.
     - It must be provisioned with the co-located inputs that runner reads, either carried over or regenerated for the
       candidate, and each regeneration recorded and reviewed. These are:
       - `tool_inventory.py`, `native_inventory.py` and `runtime_inventory.py` (:4-6);
       - `runtime-closure.json` (:182);
       - `action-baseline.json` (:188-189), whose `source_files` must describe the candidate;
       - `tool-inventory-template.json` (:206) and `vendor-template.json` (:221);
       - `native-input-baseline.json` (:233);
       - `native-artifacts/` (:236).
     - The roster shows the same pattern: its re-based preparation names a different runner path in `launcher_argv`
       (ORIGINAL-ORDINARY-ROSTER.json:20, inside `future_rebased_roster_preparation_only_unadmitted` at :3).
     - That `full-formal-diagnostic-v7/run_checks.py` (`0dd83815…`) is cited only for the pattern. It carries further
       non-path differences for its own formal-diagnostic purpose and is not the runner for F32.
     - `child_argv`, mode, label and explicit inbound environment stay as recorded.
     - A run through the unchanged `IO8/run_checks.py` executes `IO8/source` and earns no F32 credit.
   - **Re-bind the PK-0 and D1 lanes' inputs.** For each lane, the first revision after R-A is composed must re-bind to
     the integrated source. D1 v5 (WT/STATUS.md:337) already exists and binds pre-R-A bytes at `DESIGN.md:168`. PK-0 v3
     is being authored (WT/STATUS.md:329). Any run or proof either takes on pre-R-A bytes of the two files earns no F32
     credit.

## 9. Controls and evidence that close F32-CONFLICT

All runs below are on matching source in the admitted, resource-admitted frame. Three conditions apply:

- The built library is identical to the integrated candidate.
- That candidate contains R-A and every A1–A4 module (§8).
- Roster launches go through the re-targeted launcher co-located with that candidate, as described in §8 step 3, with
  their original `child_argv`, mode, label and environment. Receipts from the unchanged `IO8/run_checks.py` earn no F32
  credit.

| # | Evidence | Pass criterion |
|---|---|---|
| E0 (recommended baseline) | The four modules on the pre-R-A source, which must also contain every A1–A4 module (S5's lineage) | Records the actual codes that the A1–A4 assertions and lifetime :100-103 return today, which FINDINGS left open. Evidence, not acceptance |
| E1 | Roster `default-tests` (`test_raw_evaluation_default`) | Child wait0 and scope wait0. Every assertion passes as written, including :88-89, the :92-160 refusals, :490 and :535-550 |
| E2 | Roster `metadata-tests` (`test_evaluation_row_projection`) | As in E1, including :95-96, :97-99 and :105-110. A1 (raw :83-90) and every raw :92-160 twin pass in **both** collected instances, under `MetadataNativeControls` and under the imported `RawRequiredFailureControls`. The recorded pre-item1 baseline is `child.stderr` :3 and :47, "Ran 79 tests" |
| E3 | Roster `finalization-kernel-tests` (`test_finalization_kernel`) | As in E1, including :262-263, :264-266, :268-280 and :282-289 |
| E4 | `REQUIRED-LIFETIME-CONTROLS.json`: all five controls in `test_context_cast_lifetime.py` and all nine in `test_finalization_cast_lifetime.py` | All pass, including A4 at :162-165 and lifetime :92-105 (`new_result == old_result` and both snapshot equalities). **Evidence only:** record the actual `old_result` and `new_result` codes at :100-103 for both `status='PASS'` and `status='FAIL'`, on the E0 baseline and after R-A. This is not a new criterion. **Not satisfiable** on integrated-ordinary-v8 or item1-repair as they stand |
| E5 | The OB-003 and typed-absence neighbours: `test_core_abi` (:190-254), `test_revalidation_binding`, `test_resulting_requirement_caller`, `test_typed_absence` (including :1238-1252), `test_transaction` (including :148-151 and :276-329), and the Ada `worldline_collapse_checks` wire checks | All pass unchanged, showing that R-A weakened neither OB-003 nor CK. Passing them does not settle which control OB-003 means or its `_freshness` positive leg; both stay OPEN in OB-003 |
| E6 | The full original ordinary roster, and the full matching-source strict proof campaign, as already required for Phase One | Not credited to F32 alone, but F32 is not closed against a source that has not passed them |
| E7 | Independent review of the design and the delta by a Claude review subagent (fresh context, not the author), under the human's 17:05Z direction | No unresolved required changes. Recorded as `reviewer_kind: claude-subagent`, never as GPT-6.1 |

If a post-R-A run returns any code other than AUTHORIZED at A1–A4, that is a different defect. Examples are EEI from
native readiness or INVALID_REQUEST from a join. It must be recorded as a new open obligation with its raw evidence, and
it does not reopen any weakening option in §5.

---

## 10. Who decides

**The lead decides.** The authority is RECOVERY-AND-AUTONOMY.txt:7 (sha256 `f0c36233…`). It delegates "Routine
engineering, sequencing and API implementation choices that preserve the original external contract and success domain
… Do not invent approval gates."

- That directive is recorded in the live WT/STATUS.md at :393-397.
- This author read STATUS.md at sha256 `985dfcaa16a22cf70d9ea3b483965564181ef75e14b5150dffaf509c496ba3a7`, a
  byte snapshot taken once. Every WT/STATUS.md line number in this design refers to that read.
- STATUS.md is a live document and has moved several times during this work. The primary citation is the stable
  RECOVERY-AND-AUTONOMY.txt.

R-A falls inside that delegation for five reasons:

1. **It changes TEST_ONLY helper code only:** two keyword arguments in two fixture helpers. It touches no production
   module, Ada spec or body, C header, ABI layout, wire encoding, proof manifest or contract pin.
2. **It preserves the original external contract exactly.** OB-003's conjunct, presence rule and refusal codes are
   byte-identical, and so is V2's checkpoint absence.
3. **It restores the original success domain.** The accepted cases become reachable again, and no accepted case is
   removed or turned into a refusal.
4. **It is reversible** with one reverse patch.
5. **It is not a reserved item.** No merge, release, install, sudo, production, real-PRIME or incompatible API change.

The RC-6 launcher re-targeting is the same kind of routine sequencing. It changes no runner semantics beyond recorded,
reviewed path differences.

**Options that would be reserved are also weakenings.** R-B1, R-B2, R-B4 and R-E redefine the kernel contract, the wire
contract or caller semantics. They are rejected outright rather than escalated.

**Lead authority is not self-acceptance.** E1–E7 remain required before F32-CONFLICT can be closed
(WT/STATUS.md:323-324).

- E7 requires an independent Claude review subagent under the human's 17:05Z direction (WT/STATUS.md:279-291).
- The review-independence rule is unchanged: the reviewer is never the author.
- These are the original review and evidence requirements, not new approval gates.

---

## 11. Non-claims and residuals

- **No decision code observed.** Nothing has been run at the S5 bytes or at the R-A bytes. Every outcome here is a
  static reading of the contracts and bodies.
- **Recorded runs unauthenticated.** The recorded pre-item1 default-tests and metadata-tests runs were read as found.
  Their authenticity is not established.
- **No runner examined in execution.** No runner was executed, provisioned or compared beyond the static reading and
  `diff` in §7 and §8.
- **Null metadata on the raw path (row :105-110): static reasoning, unverified.** This is the author's reading only;
  nothing was run. With `metadata_context = None`:
  1. `Metadata_Base` of a null context returns `System.Null_Address`, because `Extent_Valid` is false for a null
     address of non-zero length (`core/evaluation_completion_c.adb:896-898`, :258-265).
  2. On the raw path, `Context_Matches` with a null context fails its extent check and returns 255
     (`evaluation_completion_c.adb:751-757`).
  3. So when primary readiness and agent readiness are both 1, `worldline-c_api.adb:810-812` returns Invalid_Request.
     Otherwise the roster bytes are 0 and the decision is EEI.

  Either way the result does not depend on Resulting, which is consistent with R-A not changing it. A run in §9 is
  still needed to observe it.
- **Lifetime :92-105 codes are evidence only.** They are recorded under E4 and grant nothing beyond the unchanged
  assertion.
- **R-A does not close OB-003.** OB-003 stays OPEN, including:
  - its own transaction-level acceptance test;
  - which control "the 1.9.1 control" designates;
  - whether that control's positive leg holds under the `_freshness` pass-through double;
  - its mutant and proof obligations;
  - its narrowed parts OB-017, OB-018 and OB-024.
- **No other obligation closed.** R-A does not close any item1, Item7, K4, K6, confinement, custody or Phase One exit
  obligation.
- **No GPT-6.1 gate claimed.** Every review of this design is a Claude review subagent under the human's 2026-10-05
  direction.
- **v4 is unreviewed.**
