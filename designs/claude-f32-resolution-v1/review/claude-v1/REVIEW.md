# Independent design review: F32-CONFLICT resolution design v1

**What this is.** An independent design review by a Claude Code review subagent (claude-opus-5-5) with a fresh context. I authored nothing under review. It grants no acceptance, and every original Phase One obligation stays OPEN.

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**
- R-A is sound and non-weakening. Its exact bytes reproduce independently.
- The required changes all correct the design's inventory, attribution or baseline statements. None changes the patch.

## Inputs

**Brief.** `W/work/claude-lead-isolation-v1/wt-1/briefs/f32-resolution-design-v1.md`, sha256 `f3ad5f07eafc7b276b4df467348f9cf0de9662f46bf9be9dc5dd5b7d01b3a514` (49 lines).

**Under review.** `WT/designs/claude-f32-resolution-v1/`. All three hashes match the brief:

| File | sha256 |
|---|---|
| DESIGN.md | `d83bd68e…2c7a0222` |
| evidence.json | `18051d25…d2c47e5b` |
| f32-r-a.patch | `226e7fc8…2c136650` |

**Method.**
- Passive reading and sha256 only.
- `git apply --check` was run against S5. It writes nothing.
- The patch was applied in memory in Python, with nothing written. Post-images were checked with `hashlib` and the standard-library `ast` module.
- No WORLDLINE code was imported or executed.

**What I did not read.**
- The scratchpad `f32/` copies. I re-derived everything from S5 plus the patch instead.
- Any review directory or session transcript.

**Ada skills.** All eight were loaded before reading the Ada specs.

## Independently reproduced (design claims confirmed)

**The patch.**
- It applies forward to S5 (`git apply --check` rc=0).
- It changes exactly one line in each file: `test_finalization_kernel.py:251` and `test_raw_evaluation_default.py:75`.
- Post-image sha256 values equal the design's: `4da992dd…7327aa4` and `77f0cb99…ffad7262` (DESIGN.md:314-315).
- Line counts are unchanged, 289 and 561.

**AST scope.**

| File | Methods before / after | Only method changed | Assert-call ASTs before / after |
|---|---|---|---|
| `test_raw_evaluation_default.py` | 43 / 43 | `RawRequiredFailureControls.bound_request` | 62 / 62, identical and in order |
| `test_finalization_kernel.py` | 26 / 26 | `FinalizationNativeControls.collapse_values` | 38 / 38, identical and in order |

**The 35-field equivalence.**
- `RawDependencyControls.checkpoint()` (raw :525-533) and the literal (raw :473-481) each have 35 keywords, over the same key set.
- After R-A, both `bound_request` and `collapse_values` produce a keyword mapping with no differences from the literal.
- Before R-A, the only difference is `resulting_requirement: None vs h(8)`.
- Both functions define `h` identically (raw :472, :524).

**Contract (S5 `core/`).**
- `Required_Present` requires `Resulting_Requirement.Present` in candidate mode (`worldline-collapse.ads:148-151`).
- `Evidence_Holds` requires `Same(Current, Resulting)` (:188).
- `Post` makes Authorized equivalent to `All_Hold` (:217), and anything not `Required_Present` is never Authorized (:219-220).
- `Same` is false when either side is absent (`worldline-identities.ads:80-82`).
- `Decide` checks EEI (`collapse.adb:20-23`) before Identity_Absent (:24-25).
- The wire accepts an absent Resulting in candidate mode and forbids a present one in checkpoint mode (`collapse_wire.ads:129-136`).

So at S5, AUTHORIZED is unreachable for these requests, as a matter of the proved contract.

**Native paths.**
- Raw path:
  - It joins the context (`worldline-c_api.adb:809-816`).
  - It overwrites only the two roster bytes (:817-818).
  - It checks metadata only after Authorized (:862-872).
- Finalization path:
  - It joins first (`evaluation_finalization_c.adb:473-484`), and kind 2 uses the metadata inside the join (:405-406).
  - It overwrites only the rosters (:485-486).
  - Its post-decision metadata check applies to kind 1 only (:491-496).
- The join compares the request with its projection modulo the rosters (`worldline-evaluation_authority.ads:197-199`, :225-226). The tests build the projection from the request itself (raw :67, fin :239), so R-A cannot open a join mismatch.

**Lineage.**
- The V1→V2 diff of the raw test is exactly one line, :530 (`resulting_requirement=h(8)` → `None`).
- The pre-item1→V1 diff adds Resulting at :223-224, :232, :246, :373, :478 and :530.
- `test_finalization_kernel.py` is `76141dfb…` in ENG/source, V1, V2, S5, item1-repair and integrated-ordinary-v8.
- V2 changed seven files (V2 `complete.patch` headers), as the design states (DESIGN.md:144-151).

**Recorded pre-item1 runs** (read as found, not authenticated).
- `default-tests-v1`, both roots: `child.stderr` :4 "ok", :44 "Ran 41 tests", :46 "OK"; `child-wait.json` returncode 0.
- Both runs' inputs list the raw test file at `53db45a0…`.

**Pins.**
- No test, oracle pin or proof manifest in S5 pins either patched file:
  - the oracle pins (`test_context_cast_lifetime.py:19-20`, `test_finalization_cast_lifetime.py:22`) bind only the `oracle_*` files;
  - `proof_manifest.py` CONTRACT_PINS list no Python tests.
- Only the historical `assurance/checkpoints` inventories record these files (see RC-4).

**Authority text.**
- `RECOVERY-AND-AUTONOMY.txt:7` (sha256 `f0c36233…`) delegates "routine engineering… that preserve the original external contract and success domain" and forbids invented approval gates.
- Its :5 fixes every contract, accepted case, fixture and control.

## Answers to the brief

**1. Characterization.**
- **Correct:** AUTHORIZED is unreachable on S5 (contract above).
- **Cause correct:** V2 changed only the shared fixture line (V2 diff), and the candidate helpers derive from that fixture (raw :71-75, fin :245-251). V2 HANDOFF.md:5 and :9 declare only checkpoint-fixture updates.
- **Nuance.** The coupling was already latent in V1. The helpers got `h(8)` only implicitly, through a CHECKPOINT_RETURN-mode fixture carrying a candidate-only slot. V1's `original-methods.json` omits `checkpoint()` and the helpers, despite V1 HANDOFF.md:11's "precisely". The design notes the omission (DESIGN.md:95-97).
- **OB-003 reading.** OB-003's acceptance does require a positive unchanged-requirement case (OBLIGATIONS-v2.json:95). But "the 1.9.1 control" is a transaction-level control, the family at `tests/test_transaction.py:~300-330` with `_freshness` doubled. It is not A1–A4, which are bound by the preserved-controls rule (RC-3).
- **Under-inventoried reach** (RC-1).
  - `test_evaluation_row_projection.py` has no `load_tests`. It imports `RawRequiredFailureControls` at module level (:12) and subclasses it (:20), so metadata-tests collects A1 (`test_complete_owned_join_and_padded_epoch`), and every refusal twin at raw :92-160, twice: once as `MetadataNativeControls` and once as `RawRequiredFailureControls`.
  - Observed in the recorded pre-item1 metadata runs: `child.stderr` :3 and :47, "Ran 79 tests". A1 therefore executes in 3 places (JACKAL exact, parsed=1+2).
  - `test_recovery_packet_producer.py` restricts collection with `load_tests` (:207-212), so it is unaffected.

**2. Original intent.** Supported.
- Pre-item1 had no Resulting field (`ENG/source/core/worldline-collapse.ads` `ba6e2a53…`).
- V1's candidate derivations yield `h(8)` = current. Its rule is "valid typed/raw fixtures explicitly supply their actual resulting identity" (V1 HANDOFF.md:11), with "no defaulting" (:5).
- V2 made checkpoint absence original for checkpoint fixtures (V2 HANDOFF.md:5) and is silent on the candidate helpers.
- R-A preserves both. It does not reduce a fixture (WORKSPACE-RULES.md:6). It makes explicit what V1 supplied implicitly, the same way V1 updated the literal at raw :478.

**3. R-A preservation.**
- **Preserved:** every assertion (AST above), the kernel, wire, ABI, contract pins and `checkpoint()` (raw :530 still `None`).
- **No weakening or narrowing:** the checkpoint controls CK (raw :535-550, `test_core_abi.py:190-217`, `worldline_collapse_checks.adb:328-341`) and the OB-003 controls (`test_core_abi.py:219-254`) are untouched.
- **The 35-field equivalence is correct.**
- **Other callers:**
  - `producer_case` (raw :217) calls `bound_request` but overrides `resulting_requirement` explicitly (raw :224), so its value is unchanged.
  - `staged_journal` and `test_recovery_packet_producer` inherit that override.
  - `test_finalization_cast_lifetime.py` and `test_tagged_object_cursor.py` instantiate the fixture but never call `collapse_values`.
  - `test_revalidation_binding.py:303-323` builds its own request with explicit Resulting (:315).
- **Row projection :97-99 is correctly handled.** It is reachable only once :95-96 authorizes, because metadata is checked after Authorized (`c_api.adb:862-868`).
- **Control the design did not list** (RC-1): `test_context_cast_lifetime.py:92-105`, in REQUIRED-LIFETIME-CONTROLS.json:5. It asserts `new_result == old_result` through `collapse_values` (:95, :100-104). At S5 it compares two refusals. Under R-A, in the PASS iteration, it becomes a real differential on the authorized path. This is a meaning change the design omits (DESIGN.md:125-127, §7). It restores intent and does not weaken anything.

**4. Rejected options.** Each rejection is sound:
- **R-B1** contradicts `Same` (`identities.ads:80-82`) and breaks `test_core_abi.py:248-249`.
- **R-B2** is a Python default, against V1 HANDOFF.md:5 and O/HANDOFF.md:27.
- **R-B3** is defeated by `Post` (:217).
- **R-B4**, **R-C1** and **R-C2** are direct weakenings.
- **R-D** breaks raw :537-538 and :543 via `collapse_wire.ads:132-133`.
  - Imprecision: `test_finalization_kernel.py:282-289` compares two calls and would pass vacuously (INVALID = INVALID) rather than "refuse". The rejection still stands.
- **R-E** lowers the wire rule.
- **R-F** replaces the mechanism of the original controls.
- **R-G** would invent a gate.

No non-weakening option is missed. One cosmetic variant is not material: a literal Resulting value (32 bytes of 8) instead of `.current_requirement`. R-H stays optional. REQUIREMENT_CHANGED on the native path is exercised by `test_core_abi.py:247` and :321 and end-to-end by `test_transaction.py:327`.

**5. Authority.**
- R-A is within the delegation (RECOVERY-AND-AUTONOMY.txt:7). It is TEST_ONLY helper code, reversible, and no API or contract change.
- No gate is added or lowered.
- Optional E0 is evidence, not a gate.

**6. Closure plan.**
- **Present:** matching-source runs E1–E4, the OB-003 and typed-absence neighbours (E5), the full roster plus strict proof (E6), and independent review (E7).
- **Frozen lanes:** they are re-bound in their next revisions, never edited in place (DESIGN.md:351, :367). Both lanes bind the current bytes (`packet.json:198-199`; D1 v4 `DESIGN.md:191`).
- **Gaps:**
  - The E2 and E4 named-line lists omit the extra A1 instances and lifetime :92-105 (RC-1).
  - E4 cannot run on item1-repair or integrated-ordinary-v8, because neither contains `tests/test_context_cast_lifetime.py`. §6's "applies equally" (DESIGN.md:282-283) holds only for the two patched files (RC-2).
- **Still open:** F32-CONFLICT, OB-003, E1–E7, the UNRUN lifetime controls, the full roster and the strict proof.

**7. Anything else.** No added cap, domain narrowing, assertion or Ghost suppression, or assumption.

## Required changes
- **RC-1.** Complete the inventory of affected and meaning-changing controls:
  - A1 and the raw :92-160 twins run in metadata-tests under both `MetadataNativeControls` and `RawRequiredFailureControls`.
  - `test_context_cast_lifetime.py:92-105` changes from a refusal-equality to a positive-path differential.
  - Name them in §2 item 6, §3.2, §7 and in E2 and E4.
  - Record the actual codes returned at :100-103 for both statuses. This is evidence only, not a new criterion.
- **RC-2.** In §6 and §8, state that the R-A lane baseline, and the source for E1–E6, must contain every A1–A4 module, from the S5 lineage or a successor. State that E4 is unsatisfiable on integrated-ordinary-v8 or item1-repair as they stand.
- **RC-3.** In §1 and §4, attribute A1–A4's AUTHORIZED requirement to the preserved-controls rule (WORKSPACE-RULES.md:6; RECOVERY-AND-AUTONOMY.txt:5; roster; REQUIRED-LIFETIME-CONTROLS). OB-003's "1.9.1 control" (OBLIGATIONS-v2.json:95) is the transaction-level control. The conclusion is unchanged.
- **RC-4.** In §2 item 4 and §7, cover all three historical inventories. Each records `76141dfb…` and the pre-item1 `53db45a0…`, and none is read by code:
  - `phase1-2026-10-02.json:2279`, :2459
  - `phase1-bound-loader-2026-10-02.json:2455`, :2635
  - `phase1-native-lifetime-2026-10-03.json:2855`, :2891

## Non-blocking notes
- **GPT-6.1 lines.** DESIGN.md:58, :365, :383 and :410-411 still say GPT-6.1. They are superseded by STATUS.md:279-291, per the brief.
- **Wording.** DESIGN.md:232 says `test_revalidation_binding` "supplies the measured Resulting". At :315 it supplies the same policy `requirementHash` identity as current.
- **Citation drift.** evidence.json pins STATUS.md at `d327f014…`, but the live file is now `45152525…`. The directive is now at :375-392. The primary authority citation, RECOVERY-AND-AUTONOMY.txt:7, is stable.
- **Lanes in flight.** PK-0 v3 and D1 v5 are being authored now (STATUS.md:327-332). Any run or proof they take on pre-R-A bytes earns no F32 credit.
