# Independent design review: F32-CONFLICT resolution design v5

**What this is.** This is an independent design review by a Claude Code review subagent (claude-opus-5-5) with a fresh context. I authored nothing under review, and I am not the drafting agent. The review grants no acceptance, and every original Phase One obligation stays OPEN. It does not claim the original GPT-6.1 gate. The human's 2026-10-05 ~17:05Z direction superseded that gate (STATUS.md blob at `fda902d`, :279-291). The design records this at DESIGN.md:630-634 and :850-851.

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**
- RC-7 parts (1) to (4) are CLOSED.
- RC-1 to RC-6 remain CLOSED.
- Notes 2 and 3 are CLOSED. Note 1 is PARTIALLY_CLOSED.
- R-A and its patch are unchanged and sound. I reproduced them a fifth time.
- New required change **RC-8**. v5's new Class A text claims that RUN re-checks all five carried inputs live, so that "any difference fails closed". That is false for three of the five: `tool_inventory.py`, `native_inventory.py` and `runtime_inventory.py`. Unlike RC-7, this gap does **not** fail closed.
- RC-8 also asks for a precise binding target for `action-baseline.json` `source_files` (this is the gap left by note 1).

## Inputs and identities
- **Override file read first.** Then the brief `WT/briefs/f32-resolution-design-v5.md`, sha256 `6bd80989f103032f0f49fee5a8f0c4366ec2ba0a1a7190f84fdc2f3dd4e5441b` (57 lines).
- **Under review.** All four hashes match brief:15-19:
  - DESIGN.md `1752159a…`
  - evidence.json `33226211…`
  - jackal.json `76b19ff9…`
  - f32-r-a.patch `226e7fc8…`. `cmp` shows it is identical to v4's copy, and its sha256 equals the v1, v2 and v3 copies.
- **RUN.** `IO8/run_checks.py` is `b047481f…` (304 lines), read in full.
- **ROSTER.** `ORIGINAL-ORDINARY-ROSTER.json` is `4a4cd1b3…` (2605 lines). REQUIRED-LIFETIME-CONTROLS.json is `9c836b3e…`.
- **Sealed reviews read** (hashes match DESIGN.md:52-53, :78-79, :94-95, :107-108):
  - v4 REVIEW.md `ddde224a…` and review.json `d1f01dce…`
  - v3 REVIEW.md `a7e5dfb2…`
  - v2 REVIEW.md `86569100…`
  - v1 REVIEW.md `b491d9d2…`
- **What I did not read.** v5 has no `review/` directory. I read nothing under review-records/, no gpt61-* directory and no transcript.
- **evidence.json.** 111 of its 113 citations match the live bytes (JACKAL exact, parsed=111+2, exact=113). The two mismatches are the two files evidence.json declares live (`live_files_note`):
  - STATUS.md is now `8544b32b`. `git show fda902d:STATUS.md` gives `985dfcaa`, and the cited lines hold there.
  - D1 v5 DESIGN.md is now `5994b243`. Its :168 still binds `76141dfb`/`22b5b189` and binds neither post-image hash.
- **Method.**
  - Reading and sha256 only.
  - R-A was applied in memory with Python; no file was written. Python `ast` and `hashlib` were used.
  - The roster and runner-input JSON files were read with standard-library `json`.
  - No WORLDLINE code was imported or executed, and `git apply` was not used.
  - All eight Ada skills were loaded before I read `core/worldline_core.gpr`. No other Ada was read; the Ada facts carry over from the sealed reviews, whose file hashes are among the 111 that match.
- **Disclosure.**
  - An `ls -la` of IO8's root, issued as a backgrounded Bash command, ran the user's `eza` alias. It hung in state S and was still running at 5m35s.
  - I did not stop it, per the no-interrupt rule. It writes nothing.
  - No file was written by me.

## 0. Closure versus v4

**RC-7(1): CLOSED** (DESIGN.md:63, :592, :659-673).
- **RUN derives `child`.** It computes `child` at RUN:60-166, records it at :254, and executes it in child mode at :23 and :36.
- **Path-bearing launches.**
  - 13 of the 52 roster `literal_g8_launches` carry an IO8 path in `child_argv`.
  - These are exactly the modes listed at DESIGN.md:666-669, and they correspond to RUN:75, :79, :83, :87, :91, :101, :105, :115, :119, :143, :145, :162 and :164.
  - This leaves 39 path-free launches (JACKAL exact, parsed=52-13, exact=39).
- **Re-based roster.** The re-based roster `future_rebased_roster_preparation_only_unadmitted` matches the literal roster mode-for-mode, and its `child_argv` equals the literal one modulo the v7→IO8 path for all 52 launches.
- **Recorded receipts.** The 7 recorded IO8 `evidence/*/inputs-before.json` files all carry `child_argv` byte-equal to the roster.
- **Line citations.** ROSTER:8-9, :1306-1307 and :2155 hold the cited paths.

**RC-7(2): CLOSED** (DESIGN.md:64, :710-715).
- RUN reads `evidence/native-build-v1/result.json` for every mode except native-build (:237-240).
- It requires scope 0, child 0 and `inputs_unchanged` (:241), compares the artifacts (:250), and pins the digest (:251-252, :290).
- The label `v1` is hard-coded at :238, which is consistent with "fresh native-build launch".

**RC-7(3): CLOSED** (DESIGN.md:65, :690-715). Carry-over is dropped for each of the four inputs, and the design's IO8 hit counts reproduce:
- `build.json`: 1 hit, at :2.
- `tool-inventory-template.json`: 4 hits, at :34-39.
- `runtime-closure.json`: 4 hits, at :7, :34168, :34171 and :444704.
- The native-build receipt: 4 hits.

The replacement Class A text is new, and it is the subject of RC-8.

**RC-7(4): CLOSED, with an overstatement** (DESIGN.md:66, :724-735, :759).
- **Launch indices.** They are 0-based and consistent with evidence.json `f32_launch_indices`: native-build is 0, default-tests 35, metadata-tests 36 and finalization-kernel-tests 43.
- **depends_on lines.** They hold:
  - :2183, default-tests depends on authority-tests;
  - :2208, metadata-tests depends on default-tests;
  - :2383, finalization-kernel-tests depends on finalization-tests.
- **pending-build's condition** is a root gate (roster launch 2).
- **RUN enforces native-build first** for every other mode (:237-241).
- **The overstatement** (non-blocking note 1): ":735 A failure anywhere upstream stops them" and ":728 none of them is strictly linear".

**Note 1: PARTIALLY_CLOSED** (DESIGN.md:68, :626, :701-702).
- `source_files` is now bound to a frozen, reviewed inventory rather than a launch-time observation, so the :189 check is no longer self-referential.
- But the reference named is "the R-A lane" inventory. Step 3 composes R-A into "the integrated candidate that the admitted frame will build and run" (:636).
- RUN :189 and :285 compare `observe_source()` of `root/source`, the tree actually run.
- If the integrated candidate contains anything besides the R-A lane, the R-A-lane inventory cannot match. The run then fails closed and E1-E3 cannot execute as written. See RC-8(b).

**Note 2: CLOSED.** Commit `fda902dad0058e4f76f3cfad6417e8ab8690224f` exists, and its STATUS.md blob hashes to `985dfcaa…`. The cited lines are :279-291, :323-324, :329, :337, :355-361 and :393-397.

**Note 3: CLOSED.** The obligation text is unchanged (DESIGN.md:270-272, :594, :744-749). D1 v5 is still pre-R-A at :168 in the live `5994b243`.

**RC-1 to RC-6: still CLOSED.**
- I compared v4 and v5 with `diff`. The changes in §§1-6 are rewording and re-wrapping.
- §8 step 3 and the §9 preamble are rewritten for RC-7.
- E1 adds the criterion "`inputs_unchanged` true (RUN:292)". This strengthens the criterion and is not a weakening.
- E1-E3 gain launch numbers.
- No assertion, accepted case, criterion or control was removed.

**Every other §7-§9 runner statement verified against RUN:**
- `root`/`source` (:8-9).
- No IO8 path literal. The scope prefix is at :203. The system paths are at :24-26, :49-51, :61, :203 and :214.
- `exist_ok=False` (:47-48) and the labels (:45-46).
- The environment from `source` (:52-55).
- The runtime closure (:182-186, :286-288).
- The effective environment assert (:211-213) and the tool observation (:208, :280).
- The four `action-baseline` fields (:189/:285, :210, :217-219, :225).
- `observe_source` exclusions (:170-180).
- Vendors (:221-225) and native inputs (:233).
- `build.json` (:242-245, :250).
- The library copy (:199-202). S5 `core/worldline_core.gpr:6-8` holds Library_Dir `../lib`, Library_Name `worldline_core` and dynamic kind.
- The binary copy (:226-229).
- There is no lifetime mode (grep `cast_lifetime` in RUN returns 0). REQUIRED-LIFETIME-CONTROLS.json:2 "authority" is as quoted.

The one statement that does not hold is in RC-8.

## 1. Characterization: CORRECT (bytes unchanged)
- S5 hashes are raw `22b5b189`, fin `76141dfb`, row `74a19597`, lifetime `f6bc3e2f`, finalization lifetime `d9ae6698`, and oracles `fe91b945` and `b8b0d136`.
- **The helpers carry None.** `checkpoint()` has `resulting_requirement=None` at raw :530. `bound_request` (raw :71-81) and `collapse_values` (fin :245-255) do not override it.
- **So AUTHORIZED is unreachable.** This rests on the contract facts confirmed by the sealed reviews, at unchanged Ada hashes.
- **OB-003.** Its acceptance (OBLIGATIONS-v2.json:95) requires its own transaction-level positive. Its identity stays OPEN (DESIGN.md:145-151, :442-457).

## 2. Original intent: SUPPORTED (unchanged since v3; DESIGN.md:320-417)

## 3. R-A preservation: CONFIRMED (reproduced)
- **Patch application.** It applied in memory to S5. Post-images are `4da992dd…7327aa4` and `77f0cb99…ffad7262` (DESIGN.md:558-559).
- **Unchanged structure.**
  - Lines are 289/289 and 561/561.
  - Methods are 26/26 and 43/43. Only `FinalizationNativeControls.collapse_values` and `RawRequiredFailureControls.bound_request` changed.
  - Assert-call ASTs are 38/38 and 62/62, identical and in order.
- **35-keyword equivalence.** The literal at raw :473 and `checkpoint()` at :525 each have 35 keywords over the same key set. Before R-A, after the helper's replacements, the only difference is `resulting_requirement`; after R-A there is none.
- **Callers match the inventory.** `bound_request` is called at raw :84-156 and :217, and row :87 and :106. `collapse_values` is called at fin :258 and :269, and lifetime :95, :109, :122, :137 and :154.
- **Collection.** Only `test_recovery_packet_producer.py` has `load_tests` (:207).
- **Row :97-99 is handled** (DESIGN.md:226-232, :586).

## 4. Rejected options: SOUND (unchanged; DESIGN.md:488-502). No non-weakening option is missed.

## 5. Authority: WITHIN DELEGATION
- The authority is RECOVERY-AND-AUTONOMY.txt:7 (`f0c36233`) and the STATUS snapshot :393-397.
- No gate is added or lowered.
- RC-8 is a fact-correction to the provisioning record, not an approval gate.

## 6. Closure plan: complete in scope except RC-8
- E0-E7 cover the following (DESIGN.md:762-771):
  - the matching-source runs;
  - all 14 lifetime controls (REQUIRED-LIFETIME-CONTROLS.json:4-21);
  - the OB-003 neighbours;
  - the full roster with runner-derived argv;
  - strict proof.
- Frozen lanes are re-bound in later revisions, never edited in place:
  - PK-0 v2 `packet.json:198-199` and D1 v4 :191 still hold the pre-R-A hashes;
  - DESIGN.md:744-749 covers them.
- **The RC-8 gap.**
  - RUN never digests or compares the three inventory modules. It imports them from `root` (:4-6; `sys.path[0]` is the script directory) and pins only its own digest (:260). Its `tools` entry covers only python3, systemd-run and `child[0]` (:259).
  - `runtime-closure.json` `spec` does not cover them either. Its `trees`, `paths` and `elf_direct` name only system locations, and the strings `tool_inventory`, `native_inventory` and `runtime_inventory` occur nowhere in the file.
  - The modules are themselves the observation code. A modified `tool_inventory.py`, together with an `action-baseline.json` regenerated (Class B) through that same module, would be self-consistent at :210. A modified `runtime_inventory.py` defines the observation it is compared against at :186.
  - So DESIGN.md:65 ("RUN re-checks them live") and :684-685 ("RUN re-checks each against a live observation, so any difference fails closed") are false for 3 of the 5 Class A inputs (JACKAL exact, parsed=5-2, exact=3; Class A count parsed=1+1+1+1+1, exact=5).
  - The claim holds for `vendor-template.json` (:223, :225) and `native-input-baseline.json` (:233).
- **Still OPEN:** everything in open_obligations.

## 7. Anything else
- I found no cap, domain narrowing, suppressed assertion or Ghost, added assumption or renamed readiness label.
- The only safety property overstated is RC-8's. It is a provisioning-integrity statement and touches no patch byte.

## Required changes
**RC-8. Correct the Class A runner claim and pin the `source_files` binding target** (DESIGN.md:65, :68, :684-689, :698-702, :626).

**(a) The three inventory modules.**
- State that RUN does not check `tool_inventory.py`, `native_inventory.py` or `runtime_inventory.py`. Only its own digest is recorded (:260).
- Their byte identity must therefore be established and recorded in the provisioning record, not attributed to RUN. Each must be sha256-equal to IO8's:
  - `51aa43cc5797254a6262f11f87889d69f6171d4303d29e077758aa9ee21cb80b`
  - `ac693a0602ec541c017228114ec262df9ab274e4fabb6dcec53dd4412452f6c0`
  - `4888f64d6125e1bce74fdde7e07f7ced16a961930903d725cd47adb2e3ff0259`
- Because RUN puts `root` first on the import path, the record must also list the candidate root's complete set of importable files.
- Keep "fails closed" only for `vendor-template.json` (:223, :225) and `native-input-baseline.json` (:233).

**(b) The `source_files` binding target.** State that `action-baseline.json` `source_files` is bound to the frozen, reviewed inventory of the exact tree RUN executes, `<candidate-root>/source`, under the :170-180 exclusions. That inventory must contain R-A's post-images `4da992dd…` and `77f0cb99…`. The R-A lane inventory is that reference only if the candidate is exactly the R-A lane.

This is a fact-correction, not a gate.

## Non-blocking notes
1. **Ordering wording** (DESIGN.md:728, :735).
   - Launches 8-46 form a strictly linear `depends_on` chain, so ":728 none of them is strictly linear" misstates it.
   - Per the roster text, E1's ancestry is 35←34←…←7←3←2. Launches 1, 4, 5 and 6 are side branches; for example, entry-component-tests (launch 4) carries no stop clause.
   - So ":735 A failure anywhere upstream stops them" is broader than the roster. It is harmless for closure, since E6 requires the whole roster anyway. Say "a failure in their `depends_on` ancestry stops them; E6 requires every launch".
2. **`action-baseline.json` contains no IO8 path** (0 hits, `9d6a152c…`). It belongs in Class B because `source_files` must change, not because of an embedded path. DESIGN.md:65 ("only the five inputs that contain no IO8 path") should say so.
3. **Index base.** v4's review called native-build "launch 1". v5 uses 0-based indices (DESIGN.md:726, :732-733). Stating the index base once would avoid confusion.
