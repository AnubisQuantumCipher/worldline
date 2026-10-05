# F32-CONFLICT resolution design, v6

**Status: DRAFT design by an author. It is not a review and not acceptance. Nothing was executed.**

- **Author.** A Claude Code general-purpose drafting subagent (claude-opus-5-5), working for the Claude lead on
  2026-10-05. It is the same author as v1–v5. It did not write the F32 investigation, D1, PK-0, any reviewed lane, or
  any review of this design.
- **Method.** Static reading only. Nothing was run: no WORLDLINE or COSMOGONY code, test, compiler, prover, runner or
  native library.
  - Programs used: `sha256sum`, `cmp`, `diff`, `grep`, `od`, `command ls -1`, and read-only `git show`/`git log` with
    `GIT_OPTIONAL_LOCKS=0`.
  - Standard-library JSON reads of the roster and runner-input files, used to count and never to execute.
  - v1 also ran a standard-library `ast` parse on scratch copies.
  - `IO8/run_checks.py` was re-read in full (304 lines), along with the import lines of its three co-located modules.
    For v6, every file the runner reads or imports is mapped to the mechanism that guarantees its identity (§8 step 3,
    table T).
- **Edits.** No source tree was edited. Every file in this directory was written with the harness's file-write tool.
- **Evidence.** `evidence.json` in this directory gives the path, sha256 and line range for every citation.
- **JACKAL.** `jackal.json` holds the four derived counts. Each was routed through `jackal_exact` with status `exact`:
  - 1+2 = 3, the A1 collection count (v3);
  - 8-3 = 5, checkpoint files that record neither patched file (v3);
  - 52-13 = 39, roster launches whose `child_argv` holds no IO8 path (v5);
  - 5-2 = 3, Class A inputs that RUN does not check (v6).

  Every other count and hash was read from tool output.
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
| R191 | `/home/sicarii/.cache/cosmogony-release-v1.9.1-20260930`, the 1.9.1 release tree that OB-003's own `where` list cites |
| IO8 | `W/work/integrated-ordinary-v8`, the original roster's launcher home |
| RUN | `IO8/run_checks.py`, sha256 `b047481ffb47328ea09f50da3a37eb13f88b6ff4fb1ef8e7540cc95bf7d7fa18`, 304 lines |
| ROSTER | `O/ORIGINAL-ORDINARY-ROSTER.json` |

**Launch indices.** Indices are 0-based positions in ROSTER `literal_g8_launches`. Native-build is launch 0.

---

## 0. What changed

### 0.1 From v5 to v6

v5 was reviewed by an independent Claude review subagent in `WT/designs/claude-f32-resolution-v5/review/claude-v1/`.
The verdict was **ENDORSED_WITH_REQUIRED_CHANGES**:

- REVIEW.md sha256 `8137719a7c521344bc04e2abed70b09c5a1b3f6e5229eccd51f0f08fd40e9661`
- review.json sha256 `91cc2eb90513b21efe8913892c4492f64c73cf3ceac9c5de15c99a38e1377c98`

That review closed RC-1 to RC-7 and notes 2–3, found note 1 partially closed, and raised RC-8. v6 changes only RC-8
and that review's non-blocking notes, and adds the identity-guarantee table T that the lead asked for.

The patch is unchanged. `f32-r-a.patch` here is byte-identical to the v1–v5 copies: sha256
`226e7fc871b7f17622f7ea2480725644d1ab527765a391157af8b24e5f136650`, and `cmp` against v5's copy reports identical.

| Item | What v6 does | Where |
|---|---|---|
| **RC-8(a)** The three inventory modules | v5 said RUN re-checks every Class A input live and fails closed. That is withdrawn for three of the five (JACKAL exact, parsed=5-2, exact=3): `tool_inventory.py`, `native_inventory.py` and `runtime_inventory.py`. RUN imports them from `root`, which is `sys.path[0]` because `/usr/bin/python3 <root>/run_checks.py` is launched without `-B` (ROSTER launcher_argv, e.g. :2187-2194). It records only its own digest (:260), and its `tools` entry covers only python3, systemd-run and `child[0]` (:259). `runtime-closure.json` mentions none of them (grep count 0). So a changed module does **not** fail closed: the module defines the very observation it is compared against (:186, :210). Their identity is now established by a **provisioning-record identity check**: each must be sha256-equal to IO8's (`51aa43cc5797254a6262f11f87889d69f6171d4303d29e077758aa9ee21cb80b`, `ac693a0602ec541c017228114ec262df9ab274e4fabb6dcec53dd4412452f6c0`, `4888f64d6125e1bce74fdde7e07f7ced16a961930903d725cd47adb2e3ff0259`). The record also lists the candidate root's complete importable set. "Fails closed" is kept only for `vendor-template.json` (:223, :225) and `native-input-baseline.json` (:233) | §8 step 3 (Class A, table T) |
| **RC-8(b)** Binding target for `source_files` | `action-baseline.json` `source_files` is bound to the frozen, reviewed inventory of the exact tree RUN observes: `<candidate-root>/source` under the :170-180 exclusions, compared at :189 and :285. That inventory must contain R-A's post-images, `tests/test_finalization_kernel.py` `4da992dd…` and `tests/test_raw_evaluation_default.py` `77f0cb99…`. The R-A lane's own inventory serves only if the candidate is exactly that lane | §8 step 1, step 3 (Class B, table T) |
| Note 1 Ordering wording | Launches 8–46 each depend on their immediate predecessor, so they form a strictly linear chain. E1's ancestry is 35←34←…←8←7←3←2. Launches 1, 4, 5 and 6 are side branches. The wording is now "a failure in their `depends_on` ancestry stops them; E6 requires every launch" | §8 step 3, §9 |
| Note 2 Why `action-baseline.json` is Class B | It holds no IO8 path (grep count 0). It is Class B because its `source_files` must change for the candidate | §8 step 3 |
| Note 3 Index base | 0-based indices, stated once above | header, §7, §8, §9 |
| Lead request: table T | Every file the re-targeted runner reads or imports is mapped to exactly one guaranteeing mechanism: a RUN assert, a provisioning-record identity check, or a reviewed regeneration or recorded launch backed by RUN asserts. This also covers outputs of the build launches that consuming launches read. No input is left unguarded | §8 step 3 |

Nothing else changed from v5.

### 0.2 From v4 to v5 (history)

v4 was reviewed in `WT/designs/claude-f32-resolution-v4/review/claude-v1/`. The verdict was
ENDORSED_WITH_REQUIRED_CHANGES:

- REVIEW.md `ddde224a5f4bb2591cda964d0a040c3030f6b2cb64c3124a59aa8c6a2a610aff`
- review.json `d1f01dceae2969d8ee1782b681649604fb18efe2429f7ead7e8231f162ae99bc`

v5 then made these changes:

- **RC-7(1):** `child_argv` is derived by RUN. 39 path-free launches stay byte-equal, and 13 are re-based.
- **RC-7(2):** the native-build receipt is now provisioned.
- **RC-7(3):** carry-over is dropped for the four root-bearing inputs. v5's companion claim that the remaining Class A
  inputs are re-checked live is corrected by RC-8(a).
- **RC-7(4):** launch ordering.
- **Re-read corrections:** RUN holds no IO8 path literal, has no lifetime mode, and uses `exist_ok=False`.
- **Notes:** the action-baseline binding (completed by RC-8(b)), the STATUS commit, and D1 v5.

### 0.3 From v3 to v4 (history)

v3 was reviewed in `WT/designs/claude-f32-resolution-v3/review/claude-v1/`. The verdict was
ENDORSED_WITH_REQUIRED_CHANGES:

- REVIEW.md `a7e5dfb2f06e3e39bb2a292cc6804c2042e4977f965e6f6342eab8587787aa11`
- review.json `9e120e580a283b90f4892b98e16e6a31116a3345e045e8688d2b9b7d78ef07a3`

v4 then made these changes:

- **RC-6:** re-targeting means re-targeting the launcher.
- **N-1:** "a 1.9.1-era control".
- **N-2:** a table cell.
- **N-3:** STATUS cited at the hash read.
- **N-4:** D1 v5 re-binds in the first revision after R-A is composed.

### 0.4 From v2 to v3 (history)

v2 was reviewed in `WT/designs/claude-f32-resolution-v2/review/claude-v1/`. The verdict was
ENDORSED_WITH_REQUIRED_CHANGES:

- REVIEW.md `865691006b593ed4559ceb755e54ba4c888b737fe6b15da35132431a339fff28`
- review.json `b8b27d23afa2d4c3e7867f4de7eed700210053c590b5cc399a01864269787746`

v3 then made these changes:

- **RC-5:** withdrew v2's identification of OB-003's "1.9.1 control".
- **Notes:** eight checkpoint files; roster cwd; null-metadata reasoning labelled unverified; JACKAL count; R-D
  wording; STATUS citation.

### 0.5 From v1 to v2 (history)

v1 was reviewed in `WT/designs/claude-f32-resolution-v1/review/claude-v1/`. The verdict was
ENDORSED_WITH_REQUIRED_CHANGES:

- REVIEW.md `b491d9d24127411e485b48751bc8a16846b95532dacd962db9f3c69196717681`
- review.json `98e7dbe14a6dae6a6c77ed65325fe5561849f4f9d176ff49476adb76d31f0d7b`

v2 then made these changes:

- **RC-1:** complete inventory.
- **RC-2:** the baseline holds every A1–A4 module.
- **RC-3:** attribution.
- **RC-4:** historical inventories.
- **Notes:** various.

---

## 1. Summary

**The conflict is in one fixture, not in the requirements.** OB-003 and the four AUTHORIZED controls (A1–A4) conflict
only through one fixture derivation that item1 V2 left inconsistent.

**Why A1–A4 must be AUTHORIZED.** The requirement comes from the preserved-controls rule, not from OB-003:

- "original deterministic fixtures and controls cannot be reduced to obtain a pass" (O/WORKSPACE-RULES.md:6).
- "Keep every original contract, accepted case, fixture, control … fixed" (RECOVERY-AND-AUTONOMY.txt:5).
- The original ordinary roster's launches for the three modules (ROSTER :2174-2198, :2199-2223, :2374-2398).
- REQUIRED-LIFETIME-CONTROLS.json:3-24.

Each of A1–A4 asserts that a fully bound candidate evaluation is AUTHORIZED when its requirement is unchanged and its
matching context is complete.

**OB-003 needs its own positive case.** OB-003's acceptance test refuses requirement-changing candidates "while the
1.9.1 control is AUTHORIZED" (O/OBLIGATIONS-v2.json:95). That control is transaction-level, not A1–A4.

- **What v2 got wrong.** v2 named the judge-mutation refusals (`tests/test_transaction.py:276-329`) and
  `tests/test_typed_absence.py:1238-1252`. Neither exists in 1.9.1:
  - The judge-mutation method is absent from R191 `tests/test_transaction.py` and from pre-item1
    `ENG/source/tests/test_transaction.py`. It first appears in item1 V1 (V1 `tests/test_transaction.py:276`).
  - `test_original_positive_commit_retains_the_measured_staged_requirement` is absent from R191 and from pre-item1
    `test_typed_absence.py`, which share sha256 `2d618967…`. It is an item1-repair addition
    (W/work/item1-repair/HANDOFF.md:34-36).
- **A 1.9.1-era control.** One transaction-level AUTHORIZED control that does exist in 1.9.1 is
  `test_clean_commit_exchanges_mapping_and_links_receipt` (R191 `tests/test_transaction.py:118-121`; S5 :148-151). It
  asserts `prepared.decision == "AUTHORIZED"`.
- **What stays open.** This design does not establish which control OB-003 means, nor whether its positive leg holds
  under the same `_freshness` pass-through double. Both stay OPEN as part of OB-003. S5's judge-mutation family contains
  only the three refusals and no unmutated AUTHORIZED leg under the double.
- **The two requirements are compatible.** Both want an unchanged-requirement candidate authorized and a changed one
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
- **What stays unchanged.** Every assertion (the assert-call ASTs are identical and in the same order), the kernel,
  wire, ABI and contracts, the production producers, and the checkpoint fixture, which keeps `None`.
- **Size.** Two keyword arguments in two helper functions, appended on existing lines. No other line number moves.

**Who decides.** The lead. This is routine, reversible engineering that preserves the original external contract and
success domain, and it is not an API or contract redefinition (§10). The obligation stays OPEN until both of these
exist:

- independent review by a Claude review subagent, under the human's 2026-10-05 ~17:05Z direction;
- the admitted-frame matching-source runs in §9.

---

## 2. Re-verification of the F32 FINDINGS against source

Each claim the design relies on was re-read at S5, unless another tree is named.

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
| Lineage hashes | sha256 of the three trees | confirmed (§3) |
| Recorded pre-item1 runs | `B/phase1-evaluation-checked-scan-ordinary-v1/evidence/default-tests-v1`; `B/phase1-finalization-ordinary-v2/evidence/default-tests-v1` | confirmed (below) |

**The recorded pre-item1 runs.** In both runs:

- `child.stderr` line 4 reads "test_complete_owned_join_and_padded_epoch … ok", line 44 reads "Ran 41 tests", and line
  46 reads "OK".
- The returncode is 0 in `child-wait.json` and in `result.json`.
- The test file listed under `inputs/` has sha256 `53db45a0…`, the pre-item1 bytes.
- The runs were read as found and are not authenticated.

**One FINDINGS inference is weaker than stated.** FINDINGS says `bound_request` is absent from V1's
`original-methods.json`. That is true but uninformative. The list names only `test_*` methods, so it also omits
`checkpoint()`, which V1 did change at :530 (V1 `original-methods.json`).

**New static observations** (not in FINDINGS):

1. **R-A cannot open a join mismatch.** The context join compares the request with its projection modulo the carried
   rosters only (`core/worldline-evaluation_authority.ads:197-199`, :225-226). The synthetic joins in these tests build
   the projection from the request itself (raw :67, finalization :239). Whatever Resulting value the helper supplies
   therefore appears identically on both sides.
2. **On the raw path, metadata is checked only after Decide returns Authorized** (`core/worldline-c_api.adb:857-872`).
   - So the row-projection refusal at :97-99, which corrupts metadata and expects INVALID_REQUEST, refuses for its
     intended reason only once the positive at :95-96 is reachable.
   - The finalization path is different. It joins metadata inside `Context_Joined` before the decision
     (`core/evaluation_finalization_c.adb:399-409`, :473-484), so `test_finalization_kernel.py:264-266` is not
     affected.
   - The actual codes are a run question (§9).
3. **The lifetime module needs no edit.**
   - Its oracle pins (`tests/test_context_cast_lifetime.py:19-37`, :73-77) bind
     `oracle_finalization_kernel_cast_lifetime.py` and `oracle_evaluation_context_cast_lifetime.py`, not
     `test_finalization_kernel.py`.
   - It reaches the request only through `self.fixture.collapse_values()`, at :95, :109, :122, :137 and :154.
4. **Historical checkpoint inventories.** S5's `assurance/checkpoints/` holds eight files. Three record the patched
   test files. The other five record neither file (JACKAL exact, parsed=8-3, exact=5):
   - `phase1-native-2026-10-03.json`
   - `phase1-native-cached-2026-10-03.json`
   - `phase1-native-frozen-2026-10-03.json`
   - `phase1-native-kernel-filter-2026-10-03.json`
   - `phase1-native-metadata-2026-10-03.json`

   What the three record:
   - Each records `test_finalization_kernel.py` as `76141dfb…`, the current bytes, which R-A will change.
   - Each records `test_raw_evaluation_default.py` as `53db45a0…`, the pre-item1 bytes, which already differ from S5's
     `22b5b189…`.
   - Two also record `test_evaluation_row_projection.py` as `74a19597…`, which R-A does not change.
   - `phase1-native-lifetime-2026-10-03.json` also lists both patched paths at :1479 and :1483, without hashes.

   Nothing reads these files: a grep of S5's `*.py`, `*.sh` and `*.gpr` for `assurance/checkpoints`,
   `phase1-2026-10-02`, `phase1-bound-loader` and `phase1-native-lifetime` returns nothing.

   | Inventory | `test_finalization_kernel.py` `76141dfb…` | `test_raw_evaluation_default.py` `53db45a0…` | `test_evaluation_row_projection.py` `74a19597…` |
   |---|---|---|---|
   | `assurance/checkpoints/phase1-2026-10-02.json` | :2276-2279 (path and hash) | :2456-2459 (path and hash) | :2241-2244 (path and hash) |
   | `assurance/checkpoints/phase1-bound-loader-2026-10-02.json` | :2452-2455 (path and hash) | :2632-2635 (path and hash) | :2407-2410 (path and hash) |
   | `assurance/checkpoints/phase1-native-lifetime-2026-10-03.json` | :2854-2855 (path and hash); path-only listing at :1479 | :2890-2891 (path and hash); path-only listing at :1483 | — |

5. **Frozen lanes in WT bind the pre-R-A bytes of both test files:**
   - `WT/packets/capi-pk0-v2/packet.json:198-199`;
   - `WT/designs/claude-native-bigint-d1-design-v4/DESIGN.md:191`;
   - `WT/designs/claude-native-bigint-d1-design-v5/DESIGN.md:168`. That file is still being edited. This author read it
     at sha256 `f150e0af…`, `daecd389…`, `aab19886…`, `004b524a…`, `29861405…` and then `9cd0d035…`; the last is the
     byte snapshot recorded in evidence.json. Line 168 held the pre-R-A bytes at every read. D1 v5 was authored after v3
     and did not re-bind.

   R-A changes those inputs. So the first revision of each lane after R-A is composed must re-bind to the integrated
   source. Existing revisions are never edited in place, and any run or proof they take on pre-R-A bytes earns no F32
   credit (§8).
6. **Full inventory of controls that R-A affects or whose meaning it changes.** All assertions are unchanged.
   - **A1, `test_complete_owned_join_and_padded_epoch` (raw :83-90).** It is collected three times (JACKAL exact,
     parsed=1+2, exact=3):
     - once in default-tests, as `test_raw_evaluation_default.RawRequiredFailureControls`;
     - twice in metadata-tests. `test_evaluation_row_projection.py` imports `RawRequiredFailureControls` at module level
       (:12), subclasses it (:20), and defines no `load_tests`. So the loader collects both
       `MetadataNativeControls.test_complete_owned_join_and_padded_epoch` and the imported
       `RawRequiredFailureControls.test_complete_owned_join_and_padded_epoch`.
     - The recorded pre-item1 metadata runs show this in both roots. In `metadata-tests-v1/child.stderr`, line 3 is the
       `MetadataNativeControls` instance and line 47 is the `RawRequiredFailureControls` instance, both "ok". Line 82
       reads "Ran 79 tests" and line 84 reads "OK". The listed inputs are `test_evaluation_row_projection.py`
       `74a19597…` and `test_raw_evaluation_default.py` `53db45a0…`.
   - **The raw :92-160 refusal twins,** which all use `bound_request`.
     - Each is collected in default-tests once and in metadata-tests twice, under both classes. Examples:
       `test_same_legacy_hashes_do_not_join_another_full_subject` at stderr :40 and :79, and
       `test_context_preserves_all_ordered_actual_rows` at :10 and :54.
     - Their assertions are unchanged. Under R-A each gains a reachable positive baseline.
   - **A2** (fin :257-266) and its twins (fin :268-280).
   - **A3** (row :86-99), including the metadata refusal at :97-99. Also row :105-110.
   - **A4** (lifetime :152-168).
   - **`test_original_whole_projection_context_metadata_and_native_conjunction` (lifetime :92-105),** listed in
     REQUIRED-LIFETIME-CONTROLS.json:5.
     - For `status` in PASS and FAIL, it builds old and new prepared graphs from `collapse_values()` (:95). It asserts
       equal snapshots (:99, :105) and `new_result == old_result` (:100-104).
     - At S5 its PASS iteration compares two refusals: Identity_Absent, Execution_Evidence_Incomplete or
       INVALID_REQUEST.
     - Under R-A the PASS iteration becomes a real differential on the authorized path, comparing old and new transport
       where the native decision can return AUTHORIZED. This restores the intended meaning and weakens nothing. The
       assertion is unchanged.
     - The actual codes at :100-103, for both statuses, are recorded as evidence only (§9 E4). They are not a new
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
| ENG/source (pre-item1) | `53db45a0…` | `76141dfb…` | `ba6e2a53…`: no Resulting at all (`ENG/source/core/worldline-collapse.ads:135-152`, :180-189) | no such field; AUTHORIZED reachable |
| V1 source | `979e4639…` | `76141dfb…` (unchanged) | `98b2661b…`: OB-003 conjunct added | fixture `resulting=h(8)` (V1 :530), so the helpers carry `h(8)` = current; AUTHORIZED reachable |
| V2 source = item1-repair = S5 = integrated-ordinary-v8 | `22b5b189…` | `76141dfb…` (unchanged) | `98b2661b…` | fixture `resulting=None` (V2 :530), so the helpers carry None; AUTHORIZED unreachable |

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

- **A1: raw :83-90, `test_complete_owned_join_and_padded_epoch`.**
  - Present since pre-item1 with unchanged method bytes; outside V1's changed-method list.
  - Intent: a complete owned join with a padded epoch is AUTHORIZED, and the request bytes are not mutated.
  - Evidence: the recorded pre-item1 default runs report "ok".
  - Collected in default-tests once and in metadata-tests twice (§2 item 6). The recorded pre-item1 metadata runs report
    "ok" for both metadata-tests instances.
  - The raw :92-160 twins share the same collection.
- **A2: finalization :257-266, `test_additive_finalization_collapse_requires_full_context_and_metadata`.**
  - The file has never changed.
  - Intent: a full finalization context and metadata give AUTHORIZED, and removing the metadata gives INVALID_REQUEST.
- **A3: row projection :86-99, `test_default_join_requires_projection_and_keeps_legacy_layout`.**
  - Never changed: `74a19597…` in every tree.
  - Intent: the default join with projection is AUTHORIZED, the legacy layouts stay queryable, and corrupted metadata
    gives INVALID_REQUEST.
  - Evidence: the pre-item1 `metadata-tests-v1` runs report "ok".
- **A4: lifetime :152-168, `test_discarded_full_prepared_graph_releases_without_cyclic_collection`.**
  - One version only: `f6bc3e2f…`.
  - Intent: a fully joined prepared graph decides AUTHORIZED, then releases without cyclic GC.
  - Required: O/REQUIRED-LIFETIME-CONTROLS.json:3-24 lists it ("ALL remain required"; status UNRUN).
- **Lifetime :92-105, `test_original_whole_projection_context_metadata_and_native_conjunction`.**
  - Same module and lineage as A4; listed in REQUIRED-LIFETIME-CONTROLS.json:5.
  - Intent: for both a PASS and a FAIL capture, the new transport produces the same complete snapshot and the same native
    decision as the original transport.
  - With R-A, the PASS case compares the two on the path where authorization is possible. That is the strong form of its
    intent (§2 item 6).

**The shared derivation.** Every request above is derived from `RawDependencyControls.checkpoint()` with these
replacements:

- mode CANDIDATE_EVALUATION;
- `evaluated_requirement` set to the fixture's `current_requirement`;
- `executed_verifiers` set to its `declared_verifiers`;
- the checkpoint slots cleared.

The common premise is an unchanged-requirement candidate: its evidence was evaluated against the current requirement,
and nothing changed that requirement.

- Before item1, the kernel had no Resulting input, so the premise was implicit.
- Item1 V1 made it explicit. The kernel gained the conjunct, and the fixture's Resulting became `h(8)` = current. Its
  HANDOFF states the rules: "valid typed/raw fixtures explicitly supply their actual resulting identity" (V1
  HANDOFF.md:11) and "There is no defaulting to current/evaluated" (:5).

### 3.3 What "original fixture" means for these helpers

Item1 is itself a repair in the lineage, so "original" has three layers:

1. **Pre-item1 bytes.** The original controls and assertions. The request field did not exist.
2. **Item1 V1.** The first fixture in the post-OB-003 domain. Its candidate derivations produce a present Resulting
   equal to current. That is the faithful translation of the pre-item1 premise.
3. **Item1 V2.**
   - For checkpoint fixtures, which must carry absence, it is original. V2's new controls enforce this
     (`tests/test_core_abi.py:190-217`; `tests/worldline_collapse_checks.adb:328-341`).
   - For candidate fixtures it is silent. Its HANDOFF says "Valid checkpoint fixtures explicitly supply absence" and "V1
     original assertions/cases remain, with necessary valid-checkpoint fixture updates" (V2 HANDOFF.md:5, :9).
   - The None that reached the candidate helpers is therefore an undeclared side effect, not a decision.

So the original fixture for the candidate helpers is V1's value: Resulting present and equal to the fixture's current
requirement. The original fixture for `checkpoint()` is V2's None. R-A preserves both, and each alternative in §5 breaks
one of them.

**Value-level check.** This is static: `ast` on scratch copies in v1, independently reproduced by every review.

- After R-A, the request built by `bound_request` equals the literal request at raw :473-481, keyword for keyword, over
  all 35 keywords.
- That literal belongs to `test_collapse_recomputes_carried_roster`. Item1 V1 updated it (`resulting_requirement=h(8)`
  at :478), and it asserts AUTHORIZED at :490.
- Before R-A, the only difference was `resulting_requirement`: None against `h(8)`.
- `collapse_values` performs the identical replacement on the identical fixture.

---

## 4. Is this a genuine requirement conflict?

No. The two requirement families are jointly satisfiable, and the source already contains controls that satisfy both.

**The AUTHORIZED requirement on A1–A4 comes from the preserved-controls rule:**

- O/WORKSPACE-RULES.md:6: "Contracts, accepted cases, proof scope/coverage/floors, original deterministic fixtures and
  controls cannot be reduced to obtain a pass".
- RECOVERY-AND-AUTONOMY.txt:5: "Keep every original contract, accepted case, fixture, control, proof scope/floor and
  checked assertion fixed".
- The roster launches at ROSTER :2174-2198, :2199-2223 and :2374-2398. The roster also records
  "results_transferred": false and "source_matching_rerun_required": true (:2600-2605).
- O/REQUIRED-LIFETIME-CONTROLS.json:3-24.

**OB-003** (O/ALL-ORIGINAL-OBLIGATIONS.md:47-65; O/OBLIGATIONS-v2.json:80-95):

- **Closure:** "in Candidate_Evaluation mode Decide requires Same(Current_Requirement, Resulting_Requirement), with
  Resulting_Requirement recomputed from the staging payload at prepare and at commit".
- **Acceptance test:** requirement-changing candidates refuse REQUIREMENT_CHANGED "while the 1.9.1 control is
  AUTHORIZED" (:95). That control is transaction-level and separate from A1–A4.
- **It is not the judge-mutation family, nor `test_typed_absence.py:1238-1252`.** Neither is in R191 or in pre-item1
  `ENG/source`.
  - The judge-mutation family (`test_transaction.py:276-329`) first appears in item1 V1 (V1
    `tests/test_transaction.py:276`). It contains three refusals and no unmutated AUTHORIZED leg under the `_freshness`
    double.
  - `test_typed_absence.py:1238-1252` was added by item1-repair (W/work/item1-repair/HANDOFF.md:34-36).
- **One 1.9.1-era candidate.** `test_clean_commit_exchanges_mapping_and_links_receipt` is a 1.9.1-era transaction-level
  AUTHORIZED control (R191 `tests/test_transaction.py:118-121`; S5 :148-151). It asserts
  `prepared.decision == "AUTHORIZED"`.
- **There are others.** R191 has other transaction-level AUTHORIZED assertions, for example `tests/test_freshness.py:90`,
  `tests/test_typed_absence.py:134`, `tests/test_lifecycle_integrity.py:283` and `tests/test_private_world_flow.py:71`.
- **Still open.** This design does not establish which control OB-003 means, nor whether its positive leg holds under
  the same `_freshness` pass-through double. Both remain OPEN within OB-003.
- **OB-003 and A1–A4 are compatible.** OB-003 does not require A1–A4 and does not conflict with them. Both require an
  unchanged-requirement candidate to be authorized.

**Controls that satisfy both today:**

- `tests/test_core_abi.py:219-254` asserts AUTHORIZED for `resulting=h(8)=current`, REQUIREMENT_CHANGED for `h(99)`,
  and IDENTITY_ABSENT for None.
- Raw :471-490 asserts AUTHORIZED with `resulting=h(8)`.
- `tests/test_revalidation_binding.py:303-318` supplies an explicit Resulting at :315. It is the same policy
  `requirementHash` identity as the current requirement at :314, not a separately measured value.

**What A1–A4 actually require.** An unchanged-requirement candidate. Nothing in them requires an absent Resulting; that
absence reached them only through V2's fixture side effect.

**Reclassification.** F32-CONFLICT should be reclassified. It is not "two original requirements conflict" but "a
fixture-consistency defect introduced at item1 V2, with the requirements jointly satisfiable". The obligation stays OPEN
until §9 is satisfied.

---

## 5. Candidate resolutions

Notation:

- **A1–A4** are the four AUTHORIZED controls (§3.2).
- **CK** is the V2 checkpoint-absence controls: raw :535-550, `test_core_abi.py:190-217` and
  `worldline_collapse_checks.adb:328-341`.
- **OB3-C** is the OB-003 explicit controls (`test_core_abi.py:219-254`), plus OB-003's own acceptance test and mutant
  obligation.

| ID | Resolution | OB-003 | A1–A4 assertions | CK | Contract / API | Verdict |
|---|---|---|---|---|---|---|
| **R-A** | `bound_request` and `collapse_values` supply `resulting_requirement` = the fixture's own `current_requirement` (the V1 value). No assertion changes | unchanged | unchanged, and reachable again | unchanged (`checkpoint()` keeps None) | unchanged | **RECOMMENDED** |
| R-A′ (cosmetic variant of R-A) | Same values, but the keyword goes on its own new line or into a shared `candidate()` helper | unchanged | unchanged | unchanged | unchanged | Acceptable. It shifts cited line numbers and touches more lines, so R-A is preferred for minimality |
| R-B1 | Kernel: in candidate mode, absent Resulting counts as Same or is not required | **weakened**: contradicts the closure text and `Same`'s "two absent values are never the same" (`worldline-collapse.ads:27-28`; `worldline-identities.ads:80-82`) | pass | unchanged | changes `Required_Present`, `Evidence_Holds`, `Post` and the proved contract | **REJECTED.** Absence would acquire authority, which `complete-phase1-prompt.txt:34` and :42 and `O/HANDOFF.md:119` forbid. It also breaks OB3-C `test_core_abi.py:248-249` (IDENTITY_ABSENT) |
| R-B2 | Python/C marshalling fills Resulting := Current when it is None in candidate mode | **weakened**: Resulting is copied, not recomputed from the staging payload (OB-003 closure; `worldline-collapse.ads:60-61`) | pass | unchanged | Python gains an independent authorization input | **REJECTED.** Contradicts "no defaulting to current/evaluated" (V1 HANDOFF.md:5; V2 HANDOFF.md:5) and "Python has no independent definition of authorization" (`O/HANDOFF.md:27`). It also breaks OB3-C :248-249 at the Python boundary |
| R-B3 | Kernel: reorder the refusals in `Decide` | unchanged | still not AUTHORIZED, because `Post` makes Authorized ⇔ `All_Hold` (`worldline-collapse.ads:217`) | unchanged | body only | **REJECTED.** Resolves nothing |
| R-B4 | Remove or soften the OB-003 conjunct | **removed** | pass | n/a | contract lowered | **REJECTED.** A direct weakening, and it fails OB-003's mutant/proof-gate test |
| R-C1 | Change the four assertions to expect IDENTITY_ABSENT or EEI | unchanged | **weakened**: the accepted case is removed | unchanged | unchanged | **REJECTED.** Removes accepted successes (`O/WORKSPACE-RULES.md:6`; `RECOVERY-AND-AUTONOMY.txt:5`) |
| R-C2 | Skip, xfail or delete the four controls | unchanged | **removed** | unchanged | unchanged | **REJECTED** for the same reasons. The roster also requires them (ROSTER :2174-2198, :2199-2223, :2374-2398; `REQUIRED-LIFETIME-CONTROLS.json`) |
| R-D | Restore `checkpoint()` to `resulting=h(8)`, undoing the V2 fixture change | unchanged | pass | **broken**: a checkpoint request with Resulting present is malformed (`collapse_wire.ads:132-133`) | unchanged | **REJECTED.** It trades one set of failing controls for another. Raw :535-543 (AUTHORIZED, `valid: True`), raw :545-550 and CK would refuse INVALID_REQUEST or change their dependency answers. `test_finalization_kernel.py:282-289` compares `collapse_decide_with_evaluation` with `collapse_decide` on the same request, so it would pass vacuously (INVALID_REQUEST = INVALID_REQUEST) rather than refuse, and would stop showing the ignored-data semantics it checks. The rejection stands |
| R-E | Revert V2's checkpoint-absence wire rule as well as the fixture | unchanged in candidate mode | pass | **removed** | wire contract lowered | **REJECTED.** Weakens typed absence ("A slot the question does not consult must be empty", `collapse_wire.ads:126-127`), reverses a reviewed V2 repair, and breaks CK |
| R-F | Rebuild the four controls on the real producer path (`bind_selected` with `resulting_requirement=policy`, as `producer_case` does at raw :162-226) | unchanged | the assertion text could stay, but the control mechanism changes from a synthetic TEST_ONLY join to a producer join | unchanged | unchanged | **REJECTED as unnecessary.** It replaces what the original controls exercise (padded epoch, synthetic owned context, metadata layout) and goes beyond the minimal consistent repair. Producer-path coverage already exists (raw :228-249, :358-380; `test_recovery_packet_producer.py:40-53`) |
| R-G | Treat this as a reserved contract decision and escalate to the operator | — | — | — | — | **Not warranted.** R-A preserves the contract and the success domain (§10). Escalation would invent an approval gate (`RECOVERY-AND-AUTONOMY.txt:7`) |
| R-H (optional, additive) | Add new paired refusal controls next to R-A, for example a raw-path `bound_request` variant with `resulting=h(99)` expecting REQUIREMENT_CHANGED | unchanged (strengthened) | unchanged | unchanged | unchanged | **Optional.** Not needed to close F32. If adopted, it is a separate additive control with its own review, and it replaces nothing |

**Why `test_finalization_kernel.py` cannot stay byte-identical.**

- `collapse_values` builds its request only from `RawDependencyControls.checkpoint()` plus fixed replacements
  (`test_finalization_kernel.py:245-251`).
- `checkpoint()` must keep `resulting=None`, which rules out R-D and R-E.
- The only way to supply Resulting without weakening OB-003 (R-B) or the assertions (R-C) is therefore inside
  `collapse_values`.

That is the minimum byte change the requirements allow, and it restores the request value V1 produced for this
unchanged method.

---

## 6. Exact proposed diff (R-A)

The patch is authored against S5. The two patched files are also present in `W/work/item1-repair/source` and
`IO8/source` with the same bytes, so the patch applies there too.

**Applying it there is not enough.** Neither tree contains the A4 module `tests/test_context_cast_lifetime.py`, its
sibling `tests/test_finalization_cast_lifetime.py`, or the oracle files `tests/oracle_*_cast_lifetime.py`. Those exist in
S5 (`f6bc3e2f…`, `d9ae6698…`, `fe91b945…`, `b8b0d136…`). The baseline requirement is in §8.

`f32-r-a.patch` in this directory has sha256 `226e7fc871b7f17622f7ea2480725644d1ab527765a391157af8b24e5f136650` and is
byte-identical to the v1–v5 copies:

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

**Identities.** Read from `sha256sum` output in v1 and reproduced by every review.

| Item | Before (S5) | After (post-image) |
|---|---|---|
| `tests/test_finalization_kernel.py` | `76141dfb2ddea1c9fb62e5ea09d27830432e96273f85e984da94f5ebbafb4a62` | `4da992ddfd206134131c31ea306fc19d46500ca8501a5214e540f55357327aa4` |
| `tests/test_raw_evaluation_default.py` | `22b5b189f9686f456214666b5a4dc4b0e3c93ee5b48f983b18994f8119f1a4f0` | `77f0cb999bca30a6eaa1ec663e21ee9cb152f405cb1ae1a591a20465ffad7262` |
| `f32-r-a.patch` | — | `226e7fc871b7f17622f7ea2480725644d1ab527765a391157af8b24e5f136650` |

**Static scope check.** `ast` only in v1, with nothing imported or run; reproduced by every review.

- `test_raw_evaluation_default.py`: 43 methods before and 43 after. Only `('RawRequiredFailureControls', 'bound_request')`
  changed. Assert-call ASTs: 62 before and 62 after, identical and in the same order.
- `test_finalization_kernel.py`: 26 methods before and 26 after. Only `('FinalizationNativeControls', 'collapse_values')`
  changed. Assert-call ASTs: 38 before and 38 after, identical and in the same order.
- Line counts are unchanged: 561 and 289.

---

## 7. R-A against each original requirement

| Requirement | Where | Effect of R-A |
|---|---|---|
| OB-003: Same(Current, Resulting), presence, Requirement_Changed | `worldline-collapse.ads:148-154`, :184-195, :213-217, :269-272; `.adb:41-45` | No byte change; the contract pin is unaffected |
| OB-003 explicit native controls | `test_core_abi.py:219-254` | Unchanged and still required |
| OB-003's transaction-level "1.9.1 control" | `OBLIGATIONS-v2.json:95`. A 1.9.1-era transaction-level AUTHORIZED control is `test_clean_commit_exchanges_mapping_and_links_receipt` (R191 `test_transaction.py:118-121`; S5 :148-151); R191 has others (§4). The post-1.9.1 judge-mutation refusals are at S5 `test_transaction.py:276-329`, and the item1-repair positive at `test_typed_absence.py:1238-1252` | Unchanged and still required; separate from A1–A4. Which control OB-003 means, and whether its positive leg holds under the `_freshness` double, stay OPEN in OB-003 |
| Production recomputes Resulting independently | `transaction.py:364-366`, :745-750, :1118-1120; `evaluation_context.py:419-426` | Unchanged. R-A touches only TEST_ONLY synthetic helpers. Those helpers already supply every other identity as a synthetic `h(n)`, including `evaluated_requirement` = current on the line above |
| No defaulting to current/evaluated | V1 HANDOFF.md:5; V2 HANDOFF.md:5 | Preserved. No producer or encoder default is added. The value is explicit test input, as V1 HANDOFF.md:11 requires |
| Typed absence: equality of absent values never authorizes | `complete-phase1-prompt.txt:42`; `O/HANDOFF.md:119` | Preserved. The positive now carries a present value |
| V2 checkpoint absence | `collapse_wire.ads:126-136`; CK | Unchanged; `checkpoint()` keeps None |
| A1–A4 accepted cases (preserved-controls rule) | raw :88-89, fin :262-263, row :95-96, lifetime :162-163 | Assertions unchanged. They become reachable, given native readiness and the join |
| A1 and the raw :92-160 twins as collected in metadata-tests | `test_evaluation_row_projection.py:12`, :20 (no `load_tests`); recorded `metadata-tests-v1/child.stderr` :3, :47, :82 | The same unchanged assertions run under both `MetadataNativeControls` and `RawRequiredFailureControls`. R-A affects each instance identically |
| Refusal twins in the same modules | raw :92-160; fin :264-266, :268-280; row :97-99, :105-110; lifetime :107-118 | Assertions unchanged. Each now has a reachable positive baseline, so its refusal can be attributed to the mutated conjunct. For row :97-99 that was not true before (`c_api.adb:862-868`) |
| Lifetime differential `test_original_whole_projection_context_metadata_and_native_conjunction` | lifetime :92-105; REQUIRED-LIFETIME-CONTROLS.json:5 | Assertion unchanged. The PASS iteration moves from comparing two refusals to comparing on the authorized path, which restores its intended strength. The codes at :100-103 are recorded as evidence only |
| Lifetime join-only controls | lifetime :120-133, :135-150 | Unaffected: no decision is taken, and the join is unchanged |
| Lifetime module bytes and oracle pins | `test_context_cast_lifetime.py` (no edit); pins at :19-20 | Unaffected; bytes stay `f6bc3e2f…` |
| Python has no independent authorization | `O/HANDOFF.md:27` | Unchanged; the native kernel decides |
| Proof scope, floors, CONTRACT_PINS, Ada bodies | `proof-manifest.json`, `prove.sh` | No Ada, C or proof-manifest change. The full matching-source strict proof stays required for Phase One, independently of F32 |
| Original ordinary roster (RC-6, RC-7) | ROSTER :2174-2198, :2199-2223, :2374-2398, :2600-2605. Every literal launch's `launcher_argv` names RUN (e.g. :2191, :2216, :2391), and its receipt is under `IO8/evidence` (:2196, :2221, :2396) | The launcher, receipt and scope unit are re-targeted (§8 step 3). RUN derives `source` from its own location (:8-9), runs the child with `cwd=source` (:36), builds the environment from `source` (:52-55), and writes receipts under its own `evidence/` (:47-48). So a run through the unchanged RUN executes `IO8/source`, which has no R-A and no lifetime modules, and **earns no F32 credit**. RUN also derives `child_argv` itself (:60-166) and records it (:254). The 39 path-free launches stay byte-equal (JACKAL exact, 52-13 = 39), including the three F32 launches (default-tests :121, metadata-tests :123, finalization-kernel-tests :137). The 13 path-bearing launches are equal only modulo re-basing IO8 to the candidate root, as at ROSTER:8-9 (e.g. :1306-1307, :2155). Mode, label (`v1`) and the explicit inbound environment stay as recorded. "source_matching_rerun_required": true (:2604) and "results_transferred": false (:2602) apply. E1–E3 (0-based launches 35, 36 and 43) run inside their `depends_on` ancestry (§8 step 3, §9) |
| Historical checkpoint inventories | Eight files in S5 `assurance/checkpoints/`. Three record the patched files with path and hash: `phase1-2026-10-02.json` :2276-2279 and :2456-2459; `phase1-bound-loader-2026-10-02.json` :2452-2455 and :2632-2635; `phase1-native-lifetime-2026-10-03.json` :2854-2855 and :2890-2891, which also has path-only listings at :1479 and :1483. The other five record neither file (JACKAL exact, 8-3 = 5) | Historical: not edited, and no code reads them. After R-A, all three record a superseded `test_finalization_kernel.py` (`76141dfb…`). They already record the pre-item1 `test_raw_evaluation_default.py` (`53db45a0…`) |
| Lanes binding these bytes | PK-0 v2 `packet.json:198-199`; D1 v4 `DESIGN.md:191`; D1 v5 `DESIGN.md:168` (pre-R-A bytes; that file is still being edited; snapshot `9cd0d035…`) | The first revision of each lane after R-A is composed must re-bind to the integrated source. Existing revisions are never edited in place, and anything run on pre-R-A bytes earns no F32 credit. This is a sequencing task for the lead, not a weakening |

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
on either tree as it stands. Patching only the two test files there would leave A4 and lifetime :92-105 unrun.

### Step 1. Author the delta as its own lane

Follow the item1-repair pattern (`W/work/item1-repair/HANDOFF.md`).

- Use a new complete source copy whose baseline satisfies the requirement above: S5, or the integrated candidate the
  lead selects from S5's lineage.
- Do not edit S5 itself, because in-progress reviews pin it.
- Record a forward and reverse patch (`f32-r-a.patch`) and a `changed-paths.json` naming exactly the two test files.
- Record static preservation: the assert-call ASTs are retained, only the two FunctionDefs changed, and every other
  source byte, mode and link is unchanged.
- **Source inventory binding (RC-8(b)).** The `source_files` inventory used in step 3 is the frozen, reviewed inventory
  of the exact tree that RUN will observe, `<candidate-root>/source`. It is taken under RUN's `observe_source()` rules
  (:170-180) and must contain the post-images `tests/test_finalization_kernel.py` `4da992dd…` and
  `tests/test_raw_evaluation_default.py` `77f0cb99…`. This lane's own inventory serves as that reference only if the
  integrated candidate is exactly this lane.

### Step 2. Independent review

- A Claude review subagent with a fresh context, not the author, reviews the design and the exact delta, per the human's
  2026-10-05 ~17:05Z direction (WT/STATUS.md:279-291).
- The original texts required actual gpt-6.1-sol and said a Claude review cannot count as that gate (O/HANDOFF.md:173;
  `complete-phase1-prompt.txt:60`). The lead records that no record will claim the GPT-6.1 gate was met
  (WT/STATUS.md:355-361).

### Step 3. Compose R-A into the integrated candidate that the admitted frame will build and run

**Re-target the roster launcher (RC-6, RC-7, RC-8).** Every statement in this step was checked against RUN
(`b047481f…`, read in full) and against the import lines of the three inventory modules.

**What the runner binds.**

- RUN derives `root` from its own location (`Path(__file__).resolve().parent`, :8) and sets `source = root/'source'`
  (:9).
- It holds no IO8 path literal. A grep for the workspace path finds only the scope-unit name prefix
  `codex-worldline-finalization-integrated-v8-` at :203, which is a unit name, not a path.
- Its other absolute paths are system and toolchain locations outside the workspace: `/home/sicarii/opt/gnat` (:49),
  `/run/user/1000` (:50-51), `/usr/bin/python3` (:61 and others), `/usr/bin/systemd-run` (:203), `/usr/bin/systemctl`
  (:214), and `/proc/self/cgroup` and `/sys/fs/cgroup` (:24-26).
- A runner co-located with the integrated candidate (`<candidate-root>/run_checks.py`, with the candidate at
  `<candidate-root>/source`) therefore selects the candidate.
- Its bytes must equal `b047481f…`, except for recorded, reviewed differences. The scope-unit name prefix (:203) is the
  only IO8-specific literal such a review might change.
- The pattern comes from the roster's re-based preparation, which names a different runner in `launcher_argv`
  (ROSTER:20, inside `future_rebased_roster_preparation_only_unadmitted` at :3). That
  `full-formal-diagnostic-v7/run_checks.py` (`0dd83815…`) is cited for the pattern only. It carries additional
  formal-diagnostic changes and is not the runner for F32.

**`child_argv` is derived, not supplied (RC-7(1)).**

- RUN computes `child` from mode, `source`, `root` and the toolchain path (:60-166). In child mode it executes the
  `child_argv` recorded in `inputs-before.json` (:23, :36), which it wrote from that computation (:254).
- The 39 launches whose computed argv contains no IO8 path stay byte-equal at the re-targeted root (JACKAL exact,
  parsed=52-13, exact=39). These include default-tests (:121), metadata-tests (:123) and finalization-kernel-tests
  (:137).
- The 13 path-bearing launches contain `str(source/…)` or `str(root/…)`. They are:
  - native-build (:145)
  - completion-tests (:91)
  - transition-direct-tests (:87)
  - direct-tests (:75)
  - legacy-direct-tests (:79)
  - resource-direct-tests (:83)
  - roster-d2-tests (:101)
  - report-facts-tests (:105)
  - wire-tests (:115)
  - authority-tests (:119)
  - artifact-tests (:143)
  - recovery-epoch-build (:162)
  - recovery-epoch-tests (:164)
- These 13 equal the recorded argv only modulo re-basing IO8 to the candidate root, as at ROSTER:8-9 for native-build.
  IO8 examples are at ROSTER:1306-1307 (native-build) and :2155 (authority-tests). Nobody hard-codes or edits them; RUN
  computes them.
- Mode, label (`v1`; RUN accepts `v1`, `v2`, `v3` at :45-46) and the explicit inbound environment stay as recorded.

**Receipt and scope unit.**

- The receipt is `root/evidence/<mode>-<label>`, created with `exist_ok=False` (:47-48). It is therefore a new
  directory under the candidate root and must not pre-exist.
- The scope unit is `--unit=<prefix><mode>-<label>` (:203).

**Provisioning the co-located inputs (RC-7(2), RC-7(3), RC-8).** RUN reads or imports the inputs below relative to
`root`. Each belongs to exactly one class. Nothing in classes B or C is copied or edited from IO8. Table T below gives
the guaranteeing mechanism for every file.

- **Class A: carried byte-identical from IO8.**
  - **The three inventory modules (RC-8(a)): not checked by RUN.** `tool_inventory.py`, `native_inventory.py` and
    `runtime_inventory.py` are imported at :4-6.
    - The launcher is `/usr/bin/python3 <root>/run_checks.py` with no `-B` (ROSTER :2187-2194). Python therefore puts
      `root` first on `sys.path` and resolves these imports there, including any `__pycache__` bytecode present.
      `sys.dont_write_bytecode` (:3) stops writes, not reads.
    - RUN never digests or compares these modules. It records only its own digest (:260). Its `tools` entry covers only
      `/usr/bin/python3`, `/usr/bin/systemd-run` and `child[0]` (:259).
    - `runtime-closure.json` does not mention them; a grep for the three module names returns 0.
    - Because these modules implement the observations that RUN compares (:183-186, :208/:210, :231/:233, :280,
      :286-288), a changed module would **not** fail closed.
    - Their identity is therefore established by a **provisioning-record identity check**, not attributed to RUN. Each
      must be sha256-equal to IO8's:
      - `tool_inventory.py` `51aa43cc5797254a6262f11f87889d69f6171d4303d29e077758aa9ee21cb80b`
      - `native_inventory.py` `ac693a0602ec541c017228114ec262df9ab274e4fabb6dcec53dd4412452f6c0`
      - `runtime_inventory.py` `4888f64d6125e1bce74fdde7e07f7ced16a961930903d725cd47adb2e3ff0259`
    - Their own imports are standard-library only: `tool_inventory.py:2-3`, `native_inventory.py:6-11` and
      `runtime_inventory.py:6-7`.
    - **Importable set of the candidate root.** The same record lists the candidate root's complete importable set:
      every entry directly in `<candidate-root>` that Python could import as a module, meaning `*.py`, `*.pyc`,
      extension modules, directories with `__init__.py`, and any `__pycache__`.
      - The reviewed set must contain `run_checks.py` and the three modules at the hashes above.
      - It must contain no entry whose module name could be imported by RUN, by the three modules, or by the standard
        library they load.
      - It must contain no `__pycache__`. IO8 itself has none.
      - Other root scripts, such as IO8's `prepare_binding.py` and `static_check.py`, are listed and shown not to
        collide.
  - **`vendor-template.json` (fails closed).** Read at :221. RUN asserts each listed vendor file's live digest equals the
    template's (:223) and that the observed set equals `action-baseline.json` `vendor_inventory` (:225). It contains no
    IO8 path.
  - **`native-input-baseline.json` (fails closed).** RUN asserts it equals a live `native_inventory.observe()` (:233).
    It contains no IO8 path. Its trust depends on `native_inventory.py`, which is guaranteed by the provisioning-record
    check above.
  - **Recording.** These two are also sha256-recorded in the provisioning record (`edc2c8a2…` and `b57ae8a7…`).
- **Class B: regenerated by a recorded, reviewed regeneration, never carried.**
  - **`runtime-closure.json`.** It embeds IO8 paths at :7, :34168, :34171 and :444704. RUN reads its `spec` and
    `inventory` (:182), verifies the environment against `spec` (:183), asserts the live observation equals `inventory`
    (:184-186), and re-observes after the child (:286-288).
  - **`tool-inventory-template.json`.** Its `tool_inventory_spec.effective_environment` embeds the IO8 paths
    `PENDING_LIBRARY_DIR`, `PENDING_OBJECT_DIR`, `PYTHONPATH` and `WORLDLINE_CORE_LIB` (:34-39). RUN asserts these equal
    the environment it builds from `source` at :52-55 (asserted :211-213). The template's `tool_inventory_spec` drives
    the tool observation (:208, :280), which is compared with `action-baseline.json` `tool_inventory` (:210).
  - **`action-baseline.json`.** It contains no IO8 path (grep count 0). It is Class B because its `source_files` must
    change for the candidate. RUN uses four of its fields:
    - `source_files` must equal `observe_source()` of `<candidate-root>/source` at :189 and again at :285.
      `observe_source()` digests every file under `source` except the `obj/`, `lib/`, `resource-tests/obj/` and
      `resource-tests/bin/` subtrees (:170-180). Per RC-8(b), `source_files` is bound to the frozen, reviewed inventory
      of exactly that tree (step 1), which contains R-A's post-images `4da992dd…` and `77f0cb99…`. It is never observed
      from the tree at launch.
    - `tool_inventory` (:210), `manager_environment` (:217-219) and `vendor_inventory` (:225) are compared with live
      observations. The regeneration review records their values.
- **Class C: produced only by recorded launches at the candidate root.**
  - **`native-artifacts/libworldline_examiner_guard.so` and `native-artifacts/build.json`.** Written by the native-build
    child (`build_guard.py <root>/native-artifacts`, :145). `build.json` embeds its artifact's absolute path (IO8 :2).
    RUN asserts that path equals `root/native-artifacts/…` and that the digest matches (:242-245), and compares both
    files against the receipt (:250).
  - **`evidence/native-build-v1/result.json` (RC-7(2)).** Written by the native-build launch (:292-297). RUN requires it
    for every mode except native-build:
    - it reads the file (:237-240);
    - it requires `scope_wait == 0`, child returncode 0 and `inputs_unchanged` (:241);
    - it checks the native artifacts against it (:250) and pins its digest (:251-252, :290).

    The file must come from a fresh native-build launch through the re-targeted runner.
  - **`source/lib/libworldline_core.so`.** Copied into the receipt for `default-tests`, `metadata-tests`,
    `finalization-kernel-tests` and the other modes listed at :199, with its digest recorded (:200-202, :254). It is
    produced by the candidate's own `build` launch: `gprbuild -P core/worldline_core.gpr` (:60), with `Library_Dir`
    `../lib` (S5 `core/worldline_core.gpr:6-8`).
  - **The compiled test binaries** under `source/obj/…` and `source/resource-tests/bin/…`. The path-bearing test modes
    execute them, and RUN copies and records each one (:226-229). They are produced by the candidate's corresponding
    `*-build` launches.
  - **Other build outputs under the excluded subtrees.** For example, the pending-standalone outputs that the child
    environment names (:54-55). They are produced by the candidate's build launches.

**Table T: the mechanism that guarantees each file the re-targeted runner reads or imports.** "RUN assert" means a RUN
`assert` that stops the run with a non-zero exit. "Record check" means a comparison written into the provisioning or
evidence record and reviewed. RUN does not perform it.

| File (relative to `<candidate-root>` unless absolute) | Read or imported at | Guaranteeing mechanism |
|---|---|---|
| `run_checks.py` itself | executed by the launcher; own digest recorded at :260 | **Record check.** sha256 equals `b047481f…`, or the reviewed recorded difference (§8 step 3). Each receipt's recorded `runner_sha256` (:260) must equal that reviewed value |
| `tool_inventory.py`, `native_inventory.py`, `runtime_inventory.py` | imported from `sys.path[0]` = root (:4-6) | **Record check (RC-8(a)).** sha256-equal to IO8's three values. Not checked by RUN |
| Any other importable root entry, including `__pycache__` | could shadow an import (root is `sys.path[0]`) | **Record check (RC-8(a)).** The complete importable set is listed and reviewed: no colliding module name and no `__pycache__` |
| `vendor-template.json` | :221 | **RUN assert** at :223 and :225, which fails closed. Also sha256-recorded |
| `native-input-baseline.json` | :233 | **RUN assert** at :233, which fails closed, given the record-checked `native_inventory.py`. Also sha256-recorded |
| `runtime-closure.json` | :182 | **Reviewed regeneration** for the candidate root. RUN then asserts against it at :183 (environment) and :186 (inventory), and re-checks at :288 |
| `tool-inventory-template.json` | :206 | **Reviewed regeneration.** RUN then asserts against it at :213 (effective environment) and, through its spec, :210 (tool inventory equals the baseline) |
| `action-baseline.json` | :188 | **Reviewed regeneration.** `source_files` is bound to the frozen, reviewed inventory of `<candidate-root>/source` (RC-8(b)). RUN then asserts against it at :189 and :285 (source), :210 (tools), :219 (manager environment) and :225 (vendors) |
| `source/**` outside the excluded subtrees, including `tests/`, `runtime/`, `core/`, `native/` and any `__pycache__` in them | `observe_source()` (:170-180); copied and digested for the directories at :191-198 | **RUN assert** at :189 (before the child) and :285 (after the child) against the reviewed frozen inventory. The digests recorded at :198 are re-checked as unchanged at :279 |
| `native-artifacts/libworldline_examiner_guard.so`, `native-artifacts/build.json` | :242-250 | **Recorded launch:** the native-build launch at the candidate root. RUN asserts at :244-245 (path and digest, compiler returncode) and :250 (equal to the receipt) |
| `evidence/native-build-v1/result.json` | :237-240 | **Recorded launch:** native-build. RUN asserts at :241 (waits and unchanged inputs) and :252 (stable while read). Its digest is pinned and re-checked at :290 |
| `source/lib/libworldline_core.so` | copied and digested at :200-202 for the :199 modes | **Recorded launch** (`build`) plus a **record check.** RUN records the digest (:202, :254) and re-checks it as unchanged during the run (:279). It does not compare it with the build output. The record must capture the library's sha256 immediately after the `build` launch. Every consuming receipt's recorded `source_library` digest, including E1–E3, must equal that value. This is §9's "built library identical to the integrated candidate" |
| Compiled test binaries (`source/obj/…`, `source/resource-tests/bin/…`) | executed as `child[0]`; copied and digested at :226-229 | **Recorded launch** (the matching `*-build`) plus a **record check.** The recorded digest (:229, :254) must equal the digest captured immediately after its build launch. RUN re-checks it as unchanged during the run (:279) |
| Other excluded-subtree build outputs read by children (e.g. `source/lib/pending-standalone`, `source/obj/pending-standalone`; environment at :54-55) | read by the child process, not by RUN | **Recorded launch** plus a **record check.** The record captures a sha256 inventory of the excluded subtrees (`obj/`, `lib/`, `resource-tests/obj/`, `resource-tests/bin/`) immediately after the last build launch that precedes E1, and again after E3. The two must be equal |
| `evidence/<mode>-<label>/inputs-before.json`, `child-wait.json`, `scope.*`, `child.*` | written and read by RUN within the same invocation (:23, :254, :295, :299-301) | **RUN-internal.** Written into a receipt directory RUN creates with `exist_ok=False` (:48). They are outputs of this run, not provisioned inputs |
| System and toolchain files (`/usr/bin/python3`, `/usr/bin/systemd-run`, `child[0]` tools, the GNAT toolchain, vendor originals, native compiler and headers, the Python standard library and caches) | :259; tool observation :208; vendors :222; native inputs :231; runtime closure :184 | **RUN asserts** at :210 (tool inventory), :223 and :225 (vendors), :233 (native inputs) and :186 (runtime closure). The observing modules are record-checked as above |
| `/proc/self/cgroup`, `/sys/fs/cgroup/…` | child mode, :24-34 | **RUN asserts** at :32-34 (memory.max, swap and core limits) |

With table T, every file the re-targeted runner reads or imports has a named guaranteeing mechanism. For the three
inventory modules, the root's importable set, and the build outputs that consuming launches read, that mechanism is a
reviewed record check, not RUN.

**Launch ordering (RC-7(4) and note 1).** Indices are 0-based positions in `literal_g8_launches`.

- **Native-build first.** Native-build is launch 0 (ROSTER:1301-1307). RUN enforces that it precedes every other mode,
  because they all require its receipt (:237-241).
- **The linear chain.** Launches 8–46 each depend on their immediate predecessor, so they form a strictly linear chain
  of `depends_on` conditions, each saying "stop all dependent actions on failure". Launch 7 (completion-build) depends
  on launch 3 (build), and launch 3 depends on launch 2 (pending-build). Launch 2's own condition is a root review and
  admission gate.
- **Side branches.** Launches 1, 4, 5 and 6 are side branches. For example, launch 4 (entry-component-tests) carries no
  stop clause. Launches 47–51 require every preceding action.
- **The F32 launches.**
  - E1 default-tests is launch 35 (depends on authority-tests, :2183). Its ancestry is 35←34←…←8←7←3←2.
  - E2 metadata-tests is launch 36 (depends on default-tests, :2208).
  - E3 finalization-kernel-tests is launch 43 (depends on finalization-tests, :2383).
- **What a failure stops.** A failure in their `depends_on` ancestry stops E1–E3. E6 requires every launch.

**The lifetime controls are not roster launches.** RUN's mode list (:43-44) has no mode for `test_context_cast_lifetime`
or `test_finalization_cast_lifetime`. E4 runs them in the separately reviewed, root-controlled action frame that
REQUIRED-LIFETIME-CONTROLS.json:2 names ("authority": "none; separately reviewed root-controlled action frame and
original gates required"). The same candidate-identity conditions apply.

**A run through the unchanged RUN earns no F32 credit.** It executes `IO8/source`.

**Re-bind the PK-0 and D1 lanes' inputs.**

- The first revision of each lane after R-A is composed must re-bind to the integrated source.
- D1 v5 (WT/STATUS.md:337) already exists and binds pre-R-A bytes at `DESIGN.md:168`.
- PK-0 v3 is being authored (WT/STATUS.md:329).
- Any run or proof either takes on pre-R-A bytes of the two files earns no F32 credit.

## 9. Controls and evidence that close F32-CONFLICT

All runs below are on matching source in the admitted, resource-admitted frame, under these conditions:

- The built library is identical to the integrated candidate (table T record check).
- That candidate contains R-A and every A1–A4 module (§8).
- Roster launches go through the re-targeted runner co-located with that candidate. Its inputs are provisioned and
  guaranteed as §8 step 3 and table T specify, and its runner-derived `child_argv` is as stated there.
- Roster launches run in the roster's order, starting with native-build (launch 0) at the candidate root. A failure in a
  launch's `depends_on` ancestry stops it.
- Receipts from the unchanged RUN earn no F32 credit.

| # | Evidence | Pass criterion |
|---|---|---|
| E0 (recommended baseline) | The four modules on the pre-R-A source, which must also contain every A1–A4 module (S5's lineage) | Records the actual codes the A1–A4 assertions and lifetime :100-103 return today, which FINDINGS left open. Evidence, not acceptance |
| E1 | Roster `default-tests` (`test_raw_evaluation_default`), launch 35, after its `depends_on` ancestry | Child wait0, scope wait0 and `inputs_unchanged` true (RUN:292). Every assertion passes as written, including :88-89, the :92-160 refusals, :490 and :535-550 |
| E2 | Roster `metadata-tests` (`test_evaluation_row_projection`), launch 36, after E1 | As in E1, including :95-96, :97-99 and :105-110. A1 (raw :83-90) and every raw :92-160 twin must pass in **both** collected instances: under `MetadataNativeControls` and under the imported `RawRequiredFailureControls`. The recorded pre-item1 baseline is `child.stderr` :3 and :47, "Ran 79 tests" |
| E3 | Roster `finalization-kernel-tests` (`test_finalization_kernel`), launch 43, after its `depends_on` ancestry | As in E1, including :262-263, :264-266, :268-280 and :282-289 |
| E4 | `REQUIRED-LIFETIME-CONTROLS.json`: all five controls in `test_context_cast_lifetime.py` and all nine in `test_finalization_cast_lifetime.py`, in their separately reviewed frame (§8 step 3) | All pass, including A4 at :162-165 and lifetime :92-105 (`new_result == old_result` and both snapshot equalities). **Evidence only:** record the actual `old_result` and `new_result` codes at :100-103 for both `status='PASS'` and `status='FAIL'`, on the E0 baseline and after R-A. This is not a new criterion. **Not satisfiable** on integrated-ordinary-v8 or item1-repair as they stand |
| E5 | OB-003 and typed-absence neighbours: `test_core_abi` (:190-254), `test_revalidation_binding`, `test_resulting_requirement_caller`, `test_typed_absence` (including :1238-1252), `test_transaction` (including :148-151 and :276-329), and the Ada `worldline_collapse_checks` wire checks | All pass unchanged, showing that R-A weakened neither OB-003 nor CK. Passing them does not settle which control OB-003 means or its `_freshness` positive leg, which stay OPEN in OB-003 |
| E6 | The full original ordinary roster (every launch, with path-bearing ones using runner-derived re-based argv) and the full matching-source strict proof campaign, as already required for Phase One | Not credited to F32 alone, but F32 is not closed against a source that has not passed them |
| E7 | Independent review of the design and delta by a Claude review subagent (fresh context, not the author), under the human's 17:05Z direction | No unresolved required changes. Recorded as `reviewer_kind: claude-subagent`, never as GPT-6.1 |

If a post-R-A run returns a code other than AUTHORIZED at any of A1–A4 (for example EEI from native readiness, or
INVALID_REQUEST from a join), that is a different defect. It must be recorded as a new open obligation with its raw
evidence, and it does not reopen any weakening option in §5.

---

## 10. Who decides

**The lead decides.** The authority is RECOVERY-AND-AUTONOMY.txt:7 (sha256 `f0c36233…`). It delegates "Routine
engineering, sequencing and API implementation choices that preserve the original external contract and success
domain … Do not invent approval gates."

**Where that directive is recorded.**

- WT/STATUS.md records it at :393-397.
- STATUS.md is cited at sha256 `985dfcaa16a22cf70d9ea3b483965564181ef75e14b5150dffaf509c496ba3a7`. That is the
  STATUS.md blob at WT commit `fda902dad0058e4f76f3cfad6417e8ab8690224f`, reproducible with
  `GIT_OPTIONAL_LOCKS=0 git show fda902d:STATUS.md`. Every WT/STATUS.md line number in this design refers to that blob.
- The live file keeps moving. The primary citation is the stable RECOVERY-AND-AUTONOMY.txt.

**Why R-A falls inside that delegation.**

1. **It changes TEST_ONLY helper code only:** two keyword arguments in two fixture helpers. It touches no production
   module, Ada spec or body, C header, ABI layout, wire encoding, proof manifest or contract pin.
2. **It preserves the original external contract exactly.** OB-003's conjunct, presence rule and refusal codes are
   byte-identical, and so is V2's checkpoint absence.
3. **It restores the original success domain.** The accepted cases become reachable again. No accepted case is removed
   or turned into a refusal.
4. **It is reversible** with one reverse patch.
5. **It is not a reserved item.** No merge, release, install, sudo, production, real-PRIME or incompatible API change is
   involved.

The launcher re-targeting, input provisioning and record checks in §8 step 3 are the same routine sequencing. They
change no runner semantics beyond recorded, reviewed differences.

**Reserved options are also weakenings.** R-B1, R-B2, R-B4 and R-E would redefine the kernel contract, the wire
contract or caller semantics. They are rejected outright rather than escalated.

**Lead authority is not self-acceptance.** E1–E7 remain required before F32-CONFLICT can be closed
(WT/STATUS.md:323-324).

- E7 requires an independent Claude review subagent under the human's 17:05Z direction (WT/STATUS.md:279-291).
- The review-independence rule is unchanged: the reviewer is never the author.

These are the original review and evidence requirements, not new approval gates.

---

## 11. Non-claims and residuals

- **No decision code observed.** Nothing was observed at the S5 bytes or at the R-A bytes. Every outcome here is a
  static reading of the contracts and bodies.
- **Pre-item1 runs not authenticated.** The recorded pre-item1 default-tests and metadata-tests runs were read as found.
- **No runner executed or provisioned.** No runner was executed or provisioned, and nothing beyond the static reading
  was compared. That reading covers the full read of RUN, the import lines of the three inventory modules, the `diff`
  against the v7 runner, and the greps and listings in §8.
- **Record checks are not runner checks.** The record checks in table T are requirements on the provisioning and
  evidence record. They are not runner checks, and they hold only once performed and reviewed.
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
- **Lifetime codes are evidence only.** The lifetime :92-105 codes are recorded under E4 and grant nothing beyond the
  unchanged assertion.
- **OB-003 stays OPEN.** R-A does not close it. Still open:
  - its own transaction-level acceptance test;
  - which control "the 1.9.1 control" designates;
  - whether that control's positive leg holds under the `_freshness` pass-through double;
  - its mutant and proof obligations;
  - its narrowed parts OB-017, OB-018 and OB-024.
- **No other obligation closed.** R-A does not close any item1, Item7, K4, K6, confinement, custody or Phase One exit
  obligation.
- **No GPT-6.1 gate claimed.** Every review of this design is a Claude review subagent, under the human's 2026-10-05
  direction.
- **v6 is unreviewed.**
