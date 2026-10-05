# Independent design review: F32-CONFLICT resolution design v3

**What this is.** This is an independent design review by a Claude Code review subagent (claude-opus-5-5) with a fresh context. I authored nothing under review and I am not the drafting agent. The review grants no acceptance, and every original Phase One obligation stays OPEN. It does not claim the original GPT-6.1 review gate. That gate was superseded by the human's 2026-10-05 ~17:05Z direction (WT/STATUS.md:279-291), and the design records this at DESIGN.md:573-575.

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**
- R-A and its exact patch are sound and weaken nothing. I reproduced them independently a third time.
- RC-1 through RC-5 are CLOSED.
- Notes 1, 2, 4, 5 and 6 are CLOSED.
- Note 3 (roster cwd) is PARTIALLY_CLOSED. Implementing it exposed a factual error in the closure plan. One new required change, RC-6, corrects it. RC-6 touches no patch byte and adds no gate.

## Inputs and identities
- **Brief:** `WT/briefs/f32-resolution-design-v3.md`, sha256 `0284eba98d14f945dfed6be9d066022fbf8690a45158945545928957daddb298` (55 lines).
- **Under review:** all four hashes match the brief (brief :15-19):
  - DESIGN.md `37879bc8…58ea5e`
  - evidence.json `d193351c…a8f0ce`
  - jackal.json `a6b3b722…4278de`
  - f32-r-a.patch `226e7fc8…2c136650`. `cmp` shows it is identical to the v1 and v2 copies.
- **v3 has no `review/` directory.** I read no review of v3, nothing under review-records/, and no session transcript.
- **Closure targets read:**
  - v2 sealed review: REVIEW.md `86569100…`, review.json `b8b27d23…`, freeze `ec5bc0b2…`;
  - v1 sealed review: REVIEW.md `b491d9d2…`.
- **evidence.json:** 84 of its 85 cited hashes match the live files. The one mismatch is the live WT/STATUS.md, which has moved from `5bff2f4a…` to `f4edc251…`.
- **Method.**
  - Reading, sha256 and `git apply --check` (rc=0; it writes nothing).
  - Post-images built in memory with Python `hashlib` and `ast`.
  - No WORLDLINE code imported or executed.
  - All eight Ada skills loaded before reading the Ada bodies.
  - JACKAL for the two derived counts.

## 0. RC closure, notes, and what else changed versus v2

**RC-1 to RC-4: still CLOSED.**
- RC-1, A1 collected three times and the lifetime :92-105 differential:
  - DESIGN.md:231-259, :302-303, :318-323, :530, :532, :594, :596.
  - Re-verified: row_projection :12 and :20, no `load_tests` (grep count 0); metadata stderr :3, :47, :82 ("Ran 79 tests") and :84 ("OK").
  - Caller sites by grep: lifetime :95/:109/:122/:137/:154; raw :84, :93-156, :217; row :87, :106; fin :258, :269.
- RC-2, baseline holds every A1–A4 module (DESIGN.md:466-468, :547-561, :587, :592, :596):
  - all eight evidence.json `observed_absent_paths_RC2` are absent;
  - the S5 copies match `f6bc3e2f`, `d9ae6698`, `fe91b945` and `b8b0d136`.
- RC-3, attribution: DESIGN.md:88-97, :375-383.
- RC-4, historical inventories: DESIGN.md:202-225, :538. Line pairs re-verified, for example `phase1-2026-10-02.json` :2241, :2276, :2456.

**RC-5: CLOSED.**
- v2's identification is withdrawn at DESIGN.md:56, :102-108, :391-396 and :524. I verified each part:
  - The judge-mutation method is absent from R191 `tests/test_transaction.py` (`4235eaa6`) and from pre-item1 ENG (`8973372c`). It first appears in V1 at :276, and V1 = V2 = S5 = `d93fdc1f`.
  - S5 :276-329 holds three subTest refusals (:286, :324-327) and no unmutated AUTHORIZED leg.
  - `test_original_positive_commit_retains_the_measured_staged_requirement` appears 0 times in R191, ENG, V1 and V2 (`2d618967` in all four). It appears once in item1-repair and once in S5 (`6a535bf8`).
  - item1-repair HANDOFF.md:34-36 records the appended control.
  - `test_clean_commit_exchanges_mapping_and_links_receipt`: R191 :118 with `assertEqual(prepared.decision,"AUTHORIZED")` at :121; S5 :148 with the assert at :150.
- The openness of OB-003's control identity and its `_freshness` leg is stated at :112-114, :400-401, :524, :597 and :665-666.
- OB-003's `where` list does cite R191 (OBLIGATIONS-v2.json:87-90).
- There is a residual wording issue (non-blocking note N-1).

**Note 1 (checkpoint files): CLOSED, with one table misstatement (N-2).**
- Eight files observed. Grep hit counts: 2, 2 and 4 in the three named files; 0 in the five named at DESIGN.md:204-208.
- JACKAL exact, parsed=8-3, exact=5.
- `phase1-native-lifetime-2026-10-03.json` :1479 and :1483 are path-only list entries.

**Note 2 (live STATUS): CLOSED.**
- The author pins `5bff2f4a`. The live file has since moved to `f4edc251` (drift N-3).

**Note 3 (roster cwd): PARTIALLY_CLOSED, see RC-6.**
- The text was added at DESIGN.md:58, :537, :577 and :588.

**Note 4 (null metadata): CLOSED.**
- Added at DESIGN.md:650-660, labelled as unverified. It matches my own static reading; see §3.

**Note 5: CLOSED.**
- jackal.json records 1+2=3 and 8-3=5. I reproduced both (checks.json).

**Note 6: CLOSED.**
- The fin :282-289 "pass vacuously" wording is now in the R-D row (DESIGN.md:442).

**Anything else changed versus v2.**
- I ran a word-level diff of the two DESIGN.md files: 370 hunks.
- Apart from the listed items, the hunks are rewording, re-wrapping and hash/line updates.
- E7 is now included in "E1–E7 remain required" (:634-635). This is not weaker.
- No assertion, accepted case, criterion or control was removed. The patch is byte-identical.

## 1. Characterization: CORRECT
- AUTHORIZED is unreachable on S5 for A1–A4, because every helper-built request carries an absent Resulting:
  - raw :71-75 and fin :245-251, with `checkpoint()` at raw :530;
  - `Required_Present`, `Same` and `Post` (`collapse.ads:148-154`, :188, :217; `identities.ads:80-82`).
- The cause is V2's :530 change, which was not propagated to the helpers (V2 HANDOFF.md:5, :9).
- OB-003's acceptance requires a transaction-level positive (OBLIGATIONS-v2.json:95), separate from A1–A4. Its identity stays OPEN.

## 2. Original intent: SUPPORTED
- The lineage table (DESIGN.md:278-282) matches the evidence hashes.
- V1 HANDOFF.md:5 and :11 support "no defaulting" and "explicit resulting".
- The precedent at `test_revalidation_binding.py:314-315` stands.

## 3. R-A preservation: CONFIRMED (reproduced)
- `git apply --check` rc=0. Exactly one line changes per file: fin :251, raw :75.
- **Post-images:** `4da992dd…7327aa4` and `77f0cb99…ffad7262`, equal to DESIGN.md:502-503.
- **Unchanged structure:**
  - line counts 289/289 and 561/561;
  - methods 26/26 and 43/43; only `FinalizationNativeControls.collapse_values` and `RawRequiredFailureControls.bound_request` differ;
  - assert-call ASTs 38/38 and 62/62, identical and in order.
- The 35-keyword equivalence stands as reproduced by the v1 and v2 reviews. The bytes are unchanged.
- **Row :97-99:** metadata is matched only after Authorized (`c_api.adb:862-871`).
- **Row :105-110, my unverified static reading:**
  - `Metadata_Base` returns Null when `Extent_Valid` fails (`evaluation_completion_c.adb:893-898`, :258-265).
  - `Context_Matches` rejects a null Context extent with 255 (:733, :751-757).
  - When P_Ready = Agent_Ready = 1, the result is `Invalid_Request` (`c_api.adb:809-812`). Otherwise the rosters are 0 (:817-818).
  - The Python wrapper passes NULL for `metadata_context=None` (`evaluation_wire.py:105`).
  - None of this depends on Resulting.
- Nothing else changes meaning beyond the inventoried set.

## 4. Rejected options: SOUND
- Unchanged from v2, which upheld them.
- No non-weakening option is missed.

## 5. Authority: WITHIN DELEGATION
- RECOVERY-AND-AUTONOMY.txt:7 (`f0c36233`). The live STATUS.md :391-395 records it.
- No gate is added or lowered.

## 6. Closure plan: complete in scope, one factual error (RC-6)
- E0–E7 cover:
  - the matching-source runs;
  - all 14 lifetime controls;
  - the OB-003 neighbours, including S5 test_transaction :148-151;
  - the full roster;
  - strict proof.
- Frozen lanes are re-bound in later revisions, never edited in place (DESIGN.md:227-229, :539, :578-580). Bindings verified at `packet.json:198-199` and D1 v4 `DESIGN.md:191`.
- **RC-6, the error.** The design says the roster launches keep "argv unchanged" with cwd re-targeted (DESIGN.md:537, :577, :588). But the recorded `cwd` does not select the source tree:
  - Each cited launch's `launcher_argv` runs `W/work/integrated-ordinary-v8/run_checks.py` (ORIGINAL-ORDINARY-ROSTER.json:2191, :2216, :2391). The receipts are under `integrated-ordinary-v8/evidence` (:2196, :2221, :2396).
  - That runner (`b047481f…`) hard-binds `source = Path(__file__).parent/'source'` (run_checks.py:8-9). It launches the child with `cwd=source` (:36), sets `PYTHONPATH` and `WORLDLINE_CORE_LIB` from that same source (:52-53), and writes receipts under its own `evidence/` with `exist_ok=False` (:47-48).
  - So a launch whose argv is unchanged executes `integrated-ordinary-v8/source`, which has no R-A and no lifetime modules, whatever cwd is recorded.
  - Neither `claude-composition-v5-beta/` nor `item1-repair/` contains a `run_checks.py`.
  - The roster's own re-based preparation shows that a re-base re-targets the runner path as well. Its launches use `full-formal-diagnostic-v7/run_checks.py`, for example ORIGINAL-ORDINARY-ROSTER.json:20, inside `future_rebased_roster_preparation_only_unadmitted` (:3).
  - §9's identity conditions (:586-587) would reject such a run. Still, the instruction as written cannot be executed on the intended source.
- **Still OPEN:** everything in open_obligations.

## 7. Anything else
- I found no cap, domain narrowing, suppressed assertion or Ghost, added assumption, or renamed readiness label.

## Required changes
- **RC-6. Correct the roster re-targeting statement** at DESIGN.md:58, :537, :577 and :588.
  - Keep each launch's `child_argv`, mode, label and environment unchanged.
  - State that the launcher must also be re-targeted, not only cwd. That means the `run_checks.py` path in `launcher_argv`, and with it the receipt and scope unit, become a runner co-located with the integrated candidate.
  - That runner's bytes must match the original `integrated-ordinary-v8/run_checks.py` (`b047481f…`) except for recorded, reviewed path differences. This follows the roster's own re-based pattern (:3, :20).
  - State that a run through the unchanged `integrated-ordinary-v8` launcher executes `integrated-ordinary-v8/source` (run_checks.py:8-9, :36, :52-53) and earns no F32 credit.
  - This is a fact-correction to the closure plan, not a gate.

## Non-blocking notes
1. **N-1, RC-5 wording.** DESIGN.md:56, :397-398 and :524 say "**the** 1.9.1-era transaction-level AUTHORIZED control is `test_clean_commit…`".
   - 1.9.1 has many transaction-level AUTHORIZED assertions, for example R191 `test_freshness.py:90`, `test_typed_absence.py:134`, `test_lifecycle_integrity.py:283` and `test_private_world_flow.py:71`.
   - §1 :109 correctly says "A … control that does exist". Use "a" throughout so that the open identity question is not pre-empted.
2. **N-2, table cell.** DESIGN.md:225 marks `phase1-native-lifetime` :2854-2855 and :2890-2891 as "path only, no hash".
   - Those entries do carry sha256 values: `76141dfb` at :2855 and `53db45a0` at :2891.
   - Only :1479 and :1483 are path-only. The prose at :211-216 and :538 is correct.
3. **N-3, STATUS drift.** The live STATUS.md is now `f4edc251`, and lines from :336 on shifted by one.
   - :328-336 now ends before "D1 v5" (:337).
   - :352-358 and :390-394 still contain the cited text (:358, :392-393).
4. **N-4, D1 v5.** D1 v5 now exists (`designs/claude-native-bigint-d1-design-v5/DESIGN.md`, `bb19cd8b…`). It binds the pre-R-A bytes `76141dfb` and `22b5b189` at :168.
   - So "their next revisions must re-bind" (DESIGN.md:539, :578) does not hold for D1 v5. That lane did not re-bind.
   - The "no F32 credit for pre-R-A bytes" safeguard (:579-580) covers it. Restate the obligation as "the first revision after R-A is composed".
