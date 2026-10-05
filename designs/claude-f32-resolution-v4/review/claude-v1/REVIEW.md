# Independent design review: F32-CONFLICT resolution design v4

**What this is.** An independent design review by a Claude Code review subagent (claude-opus-5-5) with a fresh context. I authored nothing under review and I am not the drafting agent. This review grants no acceptance, and every original Phase One obligation stays OPEN. It does not claim the original GPT-6.1 gate. That gate was superseded by the human's 2026-10-05 ~17:05Z direction (STATUS.md snapshot `985dfcaa`:279-291), and the design records this at DESIGN.md:595-600 and :719-720.

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**
- RC-6 is CLOSED. RC-1 to RC-5 remain CLOSED. N-1 to N-4 are CLOSED.
- R-A and its patch are unchanged and sound. I reproduced them a fourth time.
- New required change **RC-7**. While closing RC-6, v4 added text about the re-targeted runner that the runner's own code contradicts:
  - the claim that `child_argv` stays "as recorded" for every roster launch;
  - an incomplete list of the inputs that must be provisioned;
  - an option to "carry over" inputs that cannot be carried over.

  Every one of these failure modes fails closed, so no false credit can result. RC-7 is a fact-correction to the closure plan, not a gate, and it touches no byte of the patch.

## Inputs and identities
- **Brief:** `WT/briefs/f32-resolution-design-v4.md`, sha256 `ec53898af4328c3e594b00c8b14093c0eccb44c0767508e3c2c3408c5cfaac65` (56 lines).
- **Under review:** all four hashes match the brief (brief:15-19).
  - DESIGN.md `dd241b38…`
  - evidence.json `d7494f8c…`
  - jackal.json `d908b6f0…`
  - f32-r-a.patch `226e7fc8…`, identical by sha256 to the v1, v2 and v3 copies.
- **No review of v4 was read.** v4 has no `review/` directory. I read nothing under review-records/, no gpt61-* directory and no transcript.
- **Closure target read:** the sealed v3 review, REVIEW.md `a7e5dfb2…`:1-157.
- **evidence.json:** 98 of its 100 citations match the live bytes. The two mismatches are the two files it declares live (evidence.json `live_files_note`):
  - STATUS.md: live is `3922be40`. The recorded `985dfcaa` is the STATUS.md blob at WT commit `fda902d`, and I verified the cited lines there.
  - D1 v5 DESIGN.md: live has moved to `34c0ffdc`, then `a92df674`, then `f5c524b1` during this review.
- **Method.**
  - Reading, sha256 and `git apply --check` (rc=0, writes nothing).
  - Post-images built in memory with Python `ast`/`hashlib`.
  - No WORLDLINE code imported or executed.
  - No Ada source was read in this review, so the Ada skills were not needed; the Ada facts carry over from the sealed reviews and their unchanged bytes.
  - JACKAL for derived numbers.
- **Disclosure: two transient scratch files.**
  - A redirect left a scratch file at `/tmp/x`, a copy of part of v3 DESIGN.md.
  - I made one copy of D1 v5 DESIGN.md in the scratchpad so that I could hash and grep a single consistent snapshot.
  - Both were deleted immediately. No project file was written.

## 0. Closure versus v3
**RC-6: CLOSED.** The required statements are all present and correct for the cited launches (DESIGN.md:58, :564, :601-619, :631-633):
- The runner, not the recorded cwd, selects the source. This holds: `IO8/run_checks.py` (`b047481f`):8-9, :36, :47-48 and :52-53.
- The launcher path, receipt and scope unit are re-targeted. The roster names the IO8 runner at :2191, :2216 and :2391, with receipts at :2196, :2221 and :2396.
- The bytes must match `b047481f` except for reviewed path differences.
- A run through the unchanged IO8 runner earns no F32 credit.
- The re-based pattern is cited correctly: ORIGINAL-ORDINARY-ROSTER.json:3 and :20. The v7 runner `0dd83815` differs from IO8's runner by the formal-diagnostic additions (authorization, FORMAL_COMMAND, proof inventories) and by the unit prefix. The design correctly cites it as "pattern only" (:616-617).

**N-1: CLOSED.**
- The only remaining "the 1.9.1 control" text is the quotation of OBLIGATIONS-v2.json:95 (DESIGN.md:110-111, :410, :713).
- §4 lists the other R191 AUTHORIZED assertions (:421-425). I verified them at R191 `test_freshness.py:90`, `test_typed_absence.py:134`, `test_lifecycle_integrity.py:283`, `test_private_world_flow.py:71` and `test_transaction.py:121`.

**N-2: CLOSED.** The cell at DESIGN.md:230 matches `phase1-native-lifetime-2026-10-03.json` (`c57a57c9`):
- :2854-2855 holds the path and `76141dfb`;
- :2890-2891 holds the path and `53db45a0`;
- :1479 and :1483 are path-only.

**N-3: CLOSED.** The snapshot `985dfcaa` is reproducible as `git show fda902d:STATUS.md`. The cited lines hold the cited text:
- :279-291, the 17:05Z direction;
- :323-324, F32 open;
- :329 PK-0 v3 and :337 D1 v5;
- :355-361, the model-identity record;
- :393-397, the delegation.

**N-4: CLOSED.**
- D1 v5 :168 still binds `76141dfb` / `22b5b189` in my snapshot `f5c524b1`.
- The obligation now reads "first revision after R-A is composed" (:240-242, :566, :620-623).
- `packets/capi-pk0-v3/` has no `packet.json`, and a grep finds no binding of either hash there.

**RC-1 to RC-5: still CLOSED.**
- I ran a token-level diff of v3 against v4 for §§1-6. Outside the N-1 additions, every hunk is rewording.
- One clause was dropped: the `load_tests` sentence "so it does not re-collect the raw class". That is a removed claim, not a weakening.
- No assertion, accepted case, criterion or control was removed.
- E1-E7 are unchanged in substance (:635-644).

## 1. Characterization: CORRECT (unchanged from v3; bytes unchanged)
- S5 hashes are unchanged: raw `22b5b189`, fin `76141dfb`, lifetime `f6bc3e2f`, row `74a19597`.
- OB-003's acceptance requires its own transaction-level positive case. Its identity stays OPEN (DESIGN.md:110-127, :426-427).

## 2. Original intent: SUPPORTED
This is unchanged from v3 (DESIGN.md:290-388).

## 3. R-A preservation: CONFIRMED (reproduced)
- `git apply --check` gives rc=0.
- Post-images are `4da992dd…7327aa4` and `77f0cb99…ffad7262`, equal to DESIGN.md:528-529.
- Line counts are 289/289 and 561/561.
- Methods are 26/26 and 43/43. Only `FinalizationNativeControls.collapse_values` and `RawRequiredFailureControls.bound_request` differ.
- Assert-call ASTs are 38/38 and 62/62, identical and in order.
- The callers found by grep match the inventory: lifetime :95/:109/:122/:137/:154; fin :258/:269; raw :84-156, :217; row :87/:106.
- The 35-keyword equivalence stands as reproduced in the earlier reviews; the bytes are unchanged.
- The row :97-99 dependence is handled (DESIGN.md:198-200, :558).

## 4. Rejected options: SOUND
This is unchanged from v3 (DESIGN.md:458-483). No non-weakening option is missed.

## 5. Authority: WITHIN DELEGATION
- The delegation is snapshot STATUS.md:393-397 and RECOVERY-AND-AUTONOMY.txt:7.
- The re-targeting of the launcher is sequencing (DESIGN.md:675-676).
- No gate is added or lowered.

## 6. Closure plan: one factual error class (RC-7)
The runner computes `child_argv` from mode and root; it does not take it as an input (run_checks.py:60-166). The runner also embeds or demands root-relative state that v4's list omits or offers to "carry over":

**(a) `child_argv`.** 13 of the 52 literal roster launches record a `child_argv` that holds absolute IO8 paths.
- Examples: native-build at roster :1306-1307, and authority-tests at :2155. authority-tests is default-tests' direct predecessor (:2183).
- At a re-targeted root these become the candidate's paths, exactly as the roster's own re-based native-build shows (:8-9).
- So "child_argv … stay as recorded" (DESIGN.md:58, :564, :618, :632) is false for E6. It holds only for the 39 path-free launches (JACKAL exact, parsed=52-13, exact=39), which include the three F32 launches.

**(b) The native-build prerequisite is missing from the provisioning list.**
- Every mode except native-build reads `root/evidence/native-build-v1/result.json` and requires scope 0, child 0 and inputs unchanged (run_checks.py:237-253).
- That receipt is missing from the provisioning list (DESIGN.md:607-613).

**(c) "Carried over" (DESIGN.md:606) cannot work for four inputs.** Each embeds IO8 absolute paths that the runner checks:
- `native-artifacts/build.json`:2 records the IO8 artifact path, asserted at :244 and :250.
- `tool-inventory-template.json`:34-39 `effective_environment` holds IO8 PYTHONPATH, WORLDLINE_CORE_LIB and PENDING_*, asserted at :211-213.
- `runtime-closure.json`:7, :34168, :34171 and :444704 hold IO8 paths, checked at :183-186.
- The evidence receipt in (b).

These must be produced fresh at the new root by recorded launches or reviewed regeneration. They must never be copied or edited from IO8.

**(d) Dependency order.** E1-E3 are roster launches with a `depends_on` chain (e.g. :2183, "stop all dependent actions on failure"). Native-build is launch 1 (roster :1301-1307, and :39 in the re-based pattern). The plan does not say that E1-E3 run in that chain.

Everything else is complete:
- E0-E7, all 14 lifetime controls, the OB-003 neighbours, the full roster and strict proof (DESIGN.md:635-644).
- The frozen lanes are re-bound in later revisions and never edited in place (:240-242, :566, :620-623).
- Still OPEN: everything in open_obligations.

## 7. Anything else
- I found no cap, domain narrowing, suppressed assertion or Ghost, added assumption or renamed readiness label.
- Every RC-7 defect fails closed at a runner assert, so no weakened run could earn credit.

## Required changes
**RC-7. Correct and complete the re-targeted runner provisioning** (DESIGN.md:58, :564, :601-619, :631-633).
1. Say that `child_argv` is derived by the runner. Path-free `child_argv` stays byte-equal. Path-bearing `child_argv` (13 launches, e.g. roster :1306-1307, :2155) is equal only modulo re-basing IO8 to the candidate root, as at roster :8-9. Hard-coding IO8 paths is not allowed.
2. Add `evidence/native-build-v1/result.json` (run_checks.py:238-253) to the provisioning list. It must come from a fresh native-build launch at the re-targeted root.
3. Drop the "carried over" option for these four inputs, because they embed IO8 paths the runner asserts:
   - `native-artifacts/build.json`:2 (:244, :250)
   - `tool-inventory-template.json`:34-39 (:211-213)
   - `runtime-closure.json`:7, :34168, :34171, :444704 (:183-186)
   - the native-build receipt

   Each must be regenerated by a recorded launch or a recorded, reviewed regeneration. Nothing is copied or edited from IO8.
4. State that E1-E3 run within the roster's `depends_on` chain (e.g. :2183), starting with native-build.

## Non-blocking notes
1. **action-baseline regeneration.** The regenerated `action-baseline.json` `source_files` should be bound to the reviewed, frozen inventory of the R-A lane (§8 step 1). If it is observed from the tree at launch time, the check at run_checks.py:189 becomes self-referential.
2. **Name the snapshot commit.** STATUS snapshot `985dfcaa` is the blob at WT commit `fda902d`. Naming the commit at DESIGN.md:659 would make it reproducible without searching.
3. **D1 v5 is still moving.** It has moved past `004b524a` (to `f5c524b1` at my last read) and still binds pre-R-A bytes at :168. That is already covered by DESIGN.md:240-242.
