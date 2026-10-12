# Phase One — Claude lead execution status

Working root: `/home/sicarii/Work/worldline-phase1-claude-20261012`
- `source/` — git working copy; `c932d9a` = byte-identical Source20 baseline (frozen tree untouched),
  `337c9a3` = Source21 candidate rev 1 (three SPARK predicate defects closed). Further proof repairs are
  uncommitted until the unit proofs pass; then commit rev 2.
- `baseline-source20/` — pristine Source20 copy built for A/B only (library sha256 47b0d340…).
- `proof-tree/` — `git archive` of the committed candidate for the isolated full proof (never edited).
- `evidence/` — every run's meta/stdout/stderr; `DIAGNOSIS-*.json` are the defect records.
- `diag/observe_acquisition_closure.py` — operand observer (wraps `_native_acquisition_state` only).
- `roster/run_roster.py` — replays the 116 planned + 11 additional original actions (not yet run).

## Established so far (all with retained evidence)
1. Source20 first original error root cause (evidence/diag-acq-v1, v2, DIAGNOSIS-acquisition-closure-failed-cgroup-read.json):
   nondeterministic; sole rejecting record = `memory.events` cgroup read that raised ENOENT, retained honestly as
   readReturned=false/bytes=null/exception=…; `Controls_Ended.Successful_Cgroup_Read` refused it although the
   agent-native producer already reads that shape as absence. Fixed in `Runner_Acquisition_Bytes` (Failed_Cgroup_Read).
   Replay of the exact failing operands through the corrected predicate: True; 8 contradictory variants: False.
   Original method re-run 3/3 OK after the fix (v3, v4, v5; was 1/2 before).
2. Two more pre-existing Source20 failures found by the repo's own tests and confirmed by A/B on an untouched library
   (DIAGNOSIS-preexisting-source20-failures-ab.json): null processWaitReturncode accepted; +inf timer refused
   (binary64 digit boundary). Fixed; 58/58 tests in the five quick suites pass on the corrected library.
3. Exact recorded all-unit compile ran exit 0 on 337c9a3 (objects were already current; a fresh-object rerun
   belongs in the final chain).
4. Proof: the original Source20 units are NOT proof-clean at level 3 (two units alone: 21 unproved). The full strict
   proof never completed in the Codex frame (600 s child deadline). A full-project survey (-j8, isolated tree) is
   running; proof repairs so far: Encoded'First range check (slide to 1-based), D init, Nonzero init warning,
   Exponent/Matches loop invariants, vacuous variant removed, Archive_Envelope postconditions
   (Array_Element strict sub-span, Array_Length >0 ⇒ Length ≥ 2, Decode Children ≤ Encoded) so structural
   recursion variants prove. Rule kept: no pragma Assume, no justification, no contract weakening.

## Proof campaign findings (2026-10-12 01:30-01:50Z)
- The Source20 strict proof had NEVER run to completion: `gnatprove -U` aborted after 11 units on two hard errors
  (`Inline_For_Proof` with non-equality Posts in `worldline-resources.ads`); after removing the redundant annotations
  the flow survey aborted after 18 units on three SPARK legality errors (`E0007` constraint depends on variable in
  `worldline-raw_json.adb` ×2 and `worldline-evaluation_agent_native.adb`). Both fixed (constants), plus array
  initializers and the Archive_Envelope Bytes_Valid/Materialize restructure (total Materialize, defining Post).
- Remaining known flow findings before the next survey: ~20 `while` loops without variants and dead initializers in
  `worldline-evaluation_agent_native.adb` / `worldline-raw_json.adb`. Expect more units to surface as analysis
  reaches them. Workflow: `evidence/flow-survey-vN` (fast, whole project) → fix → `prove-units-vN` → full survey.
- Evidence of pre-existence: `baseline-source20/.prove-units.stderr` (two units, 21 unproved) and
  `baseline-source20/.prove-envelope.stderr` (31 unproved) on the untouched Source20 library/source.

## Proof campaign structure (2026-10-12 02:30Z onward)
- Keep-going flow survey of f21a688 (evidence/flow-survey-v3-keepgoing, breakdown.txt): 214 units; 727 legality
  errors, 446 flow findings, 388 warnings. 509 of the errors were the access-discriminant design of the two
  `Prepared_History` observer records (Custody_V2_Owner_Canonical / K4_Resource_Ack) cascading through
  operation_journal, journal_witness, fold_engine; 156 were box-notation/ownership in machine_evidence; the rest
  small classes (loop-invariant placement 26, E0007 13, E0005 10, structural variant 1).
- Observer redesign (lead, working tree): the records lose their access discriminants; every operation receives the
  arena explicitly; the observer records the arena's extent and whole-bytes SHA-256 digest at establishment,
  refuses any arena of a different extent, and `Source_Matches` (the frame handoff) compares the digest, which
  keeps the original exact-full-bytes relation as a real check instead of a tautological self-compare. Behavior on
  every reachable input is unchanged; the unreachable null/null and both-non-null refusal branches vanish with the
  states that made them reachable. Family flow survey after the redesign: 0 errors, 1 finding (callee
  Classify_All lacks Always_Terminates; assigned to the recovery_material_replay owner), 7 warnings.
- Unit owners (fresh-context Claude subagents, one git worktree each under wt/<name>, branch campaign/<name>,
  evidence under evidence-wt/<name>, shared rules in campaign/BRIEF.md): machine-evidence; legality-small
  (operation_result_relations, recovery_material_replay, resources, closed_v1, root_output_sequence,
  transaction_archive_json, native_lifetime_observation, scoped_record_source, excluded_source_owner,
  native_diagnostic_trace); flow-a (report_parser, evaluation_role_native); flow-b (producer_values,
  startup_installation, native_execution_views). Waves flow-c/flow-d pending. Definition of done per unit: the
  exact strict switches at level 3, zero unproved, zero justified, no Assume, no weakening.
- Full level-3 survey with -k of f21a688 running in survey-tree (evidence/prove-full-survey-v2) to inventory the
  unproved checks of every legal unit; its result drives the next wave of owners.
- Gate facts: prove.sh/verify_proof_manifest.py accept per-unit lines only in the fully proved form
  (`flow analyzed (0 errors, N checks, M warnings and 0 pragma Assume statements) and proved (K checks)`), so
  warnings are tolerated by the gate but every subprogram must be proved; MINIMUM_CHECKS and the 1623-name roster
  are pinned in runtime/worldline/proof_manifest.py; CONTRACT_PINS must be refreshed after any .ads contract edit.

## Remaining chain (in order)
- digest survey → repair every unproved check → re-prove changed units → commit rev N
- fresh clean all-unit compile (exact command) → FULL strict proof (-j2 exact command, isolated tree) on final commit
- complete runtime roster (116 + 11) after the proof on the same commit (roster/run_roster.py --clean --additions)
- prove.sh (manifest regeneration) + scripts/assurance.py run (project gate: Ada tests, fuzz, discover suite,
  private-host suite, evaluation-domain gate, proof gate, manifest) on the committed head
- independent review (fresh-context Claude review subagents; GPT-6.1 not available from this harness) of the
  requirement-to-evidence matrix; then publish branch + PR to AnubisQuantumCipher/worldline and read back hosted checks
- root-gated authentic protected/actor fixtures: report precisely what needs the operator (sudo refuses: password required)

## Roster facts (2026-10-12 02:40Z)
- The original Codex frame executed only roster rows 1-7 on Source20 (receipts native-build-v1 … acquisition-regression-tests-v1
  in C20/evidence) before the first original error; rows 8-116 and the 11 additions have never run on Source20. Their outcomes
  in roster-run-1 are first observations, not regressions.
- A/B of 77 custody/journal/fold/witness test modules (evidence/tests-redesign-v1/AB-NOTE.md): every failing module fails
  identically on the untouched Source20 baseline (root-gated, missing corpora, AF_UNIX path length, and several genuine
  pre-existing refusals such as test_custody_provision_kernel 'Prior_Context_Refused'); one load-induced flaky test rerun 3/3 OK.

## Lead progress (2026-10-12 03:15Z)
- Observer redesign + family flow fixes + Archive_Envelope payload Posts committed as a WIP checkpoint on main (see git log).
- Archive_Envelope proves completely at level 3: 120 checks, 0 unproved, 0 warnings (evidence/archive-envelope-payload-post-v1).
- legality-small owner interim: all 29 legality errors in its ten units cleared; proofs/tests in progress; spec changes to refresh in
  CONTRACT_PINS: recovery_material_replay.ads (JSON Subprogram_Variant, Classify_All Always_Terminates), resources.ads (Radix_Power Post
  strengthened, vestigial Prefix_Value variant removal).
- Seven-area requirement-to-code map saved at campaign/seven-area-map.md (fresh-context survey; lists real SPARK-Off glue and contract gaps
  in Source20's design that the matrix must carry honestly).

## Unit-owner results (2026-10-12 04:00Z)
- machine-evidence: DONE. custody_v2_machine_evidence proves 188/188 at level 3 (0 unproved, 0 warnings), commit 259647f on
  campaign/machine-evidence (body only). Techniques: 'Position -> pinned literal offsets guarded by pragma Compile_Time_Error (the
  project's own C_API technique; build fails closed on a layout change), Global => null on three helpers to stop contextual inlining
  (a 5.8 MB VC file had pinned gnatwhy3 at the memory cap), string-literal hoisting (GNATprove 16.1 treats equal literals as distinct
  terms), observer declarations for 'Access. Found and reported (not fixed) a pre-existing defect: Joined compares frame lengths
  against 'Size/8 while the producer emits ctypes sizeof frames, so it can never accept a genuine frame
  (evidence/DIAGNOSIS-machine-evidence-size-vs-object-size.md). test_resource_owned_abi failures are pre-existing (A/B).
- The family proof of the observer redesign (owner_canonical, k4, operation_journal, fold_engine, journal_witness) at -j4 was
  OOM-killed after 95 min at the 8G cap; partial results: owner_canonical 85 unproved (string-concatenation length checks on JSON
  building, Type_Is preconditions, index/overflow on First+I, Classify_All termination), journal_witness 1 (Input'First for empty
  arrays); k4/operation_journal/fold_engine unknown. Recovery_Packet proves 0 unproved after the explicit span-validity guards
  (evidence/recovery-packet-v2). Re-run of the family at -j2 / CAP=3G unit by unit is queued behind memory.
- Memory, not CPU, is the binding constraint: 31 GB total; kernel OOM kills hit four scopes (23:33-23:41 local) incl. roster row 6
  (the ten-module acquisition regression run) and one owner's run. Rules now: one gnatprove per owner, -j2, CAP=3G.

## Gate build finding and sweep (2026-10-12 04:25Z)
- `gprbuild -q -p -P worldline.gpr` (the exact build step of prove.sh and scripts/assurance.py) FAILS on this machine with
  `gprlib: no object files specified` (evidence/aggregate-build-check-v1, -v2): the aggregate pulls the toolchain's prebuilt
  sparklib library project and gprbuild tries to rebuild its library. `tests/worldline_tests.gpr` alone builds (exit 0) and the
  aggregate builds with `-XGPR_TOOL=gnatprove` (sparklib then declares itself Externally_Built, exactly as gnatprove sees it;
  evidence/aggregate-build-check-v3). The built `bin/worldline_core_tests` and `bin/worldline_core_fuzz` both PASS
  (evidence/ada-tests-check-v1). The hosted CI uses the same GNAT-FSF-builds versions on x86_64; whether its build step passes is
  unknown (no readback yet). Decision pending: run the gate with `GPR_TOOL=gnatprove` in the environment (no source change) vs a
  project-file change; to be settled in the final chain and recorded.
- Roster-run-2 rows 6 and 40 (the two revalidation test suites) were OOM-killed at the 8G scope cap after 25-32 min under load
  (journal: 8G memory peak); row 30 (test_proof_source_inventory) fails on stale CONTRACT_PINS, expected until the pin refresh.
  The roster must be rerun on the final commit on a quiet machine.
- unit-sweep-v1 (lead-tree = main dd911db): sequential level-3 proof of every unowned core unit, one gnatprove at a time;
  evidence/unit-sweep-v1/results.csv. First 24 units: all 0 unproved.
- Owners active: legality-small, flow-a, flow-b, family-a (owner_canonical+journal_witness), family-b (k4+operation_journal+fold_engine),
  flow-c, flow-d. Two owner scopes hit the 3G per-scope cap (per-scope OOM, not global); owners rerun or split with --limit-subp.

## Runtime diagnosis (2026-10-12 06:00-07:00Z): two pre-existing Source20 defects behind the first error
1. Python encoder defect (deterministic): evaluation_context.agent_context_pair's sealed-finalization branch passes a tuple of
   bytes (seal subject, content, evidence) to evaluation_terminal.value_bytes, which accepts only JSON-like values (the module's own
   comment at _required_value says so) and raises CAPTURE_VALUE_UNSUPPORTED for bytes. Unchanged since integrated-candidate-v1;
   masked on Source20 by the acquisition-closure error. Evidence: diag-transaction-release-capture-v1 (value-bytes-refusals.jsonl:
   tuple(bytes, bytes, bytes, dict)). Fix (working tree): both sides use finalization_journal.encode, the lossless bytes-capable
   encoder the same function's caller already uses for bytes-bearing tuples; comparison stays exact per field.
2. Quadratic run-time contract evaluation in the checks build (pre-existing, -gnata): Archive_Base64.Decoded_Byte's precondition
   re-validated the whole base64 span (Canonical, O(n)) on every byte, and Decode's postcondition and body call it per byte, so
   decoding an n-byte leaf cost O(n^2) under checks. gdb samples (diag-transaction-release-capture-v1/gdb-samples.txt) show the
   checks-mode relation kernel inside archive_base64.canonical in every sample; replay of the captured 120 KB input: Source20 17.1 s,
   candidate 20.3 s, release 1.0 s; the captured 3.8 MB input did not finish. Fix (main working tree): local-first preconditions —
   Decoded_Byte Pre = Byte_Readable (the two sextets it reads are in-span digits) or else the original
   (Canonical and Offset < Decoded_Length); Decoded_Length Pre = local span condition or else Canonical. Both are weaker
   (the original condition remains a sufficient disjunct, so no caller changes); results are unchanged on the original domain.
   Archive_Base64 proves 0 unproved, 0 warnings at level 3 (evidence/archive-base64-local-pre-v1). Replay with the fix:
   120 KB input 3.5 s; 3.8 MB input completes in 281 s with code 12 (release: 116 s, code 12).
3. The records' "original timeout obligation" (N59) is the complete acquisition suite (roster row 6) reaching its original deadline
   in the checks configuration; the original prompt: "A timeout is fixed only when the original test succeeds under its original
   conditions". Defect 2 is a demonstrated cause of checks-mode slowness on these paths; row 6 must be re-measured on the fixed
   source on a quiet machine. Remaining checks overhead after the fix is a ~2.5-3.5x constant factor; the release-mode kernel itself
   needs 116 s for the 3.8 MB relation input (JSON prefix re-parsing per field), so deadlines remain at risk and are measured, not assumed.

## Runtime fixes committed on main (2026-10-12 07:00-08:10Z)
- f484b29: (1) agent_context_pair sealed branch: bytes-capable lossless encoding (was CAPTURE_VALUE_UNSUPPORTED on every call);
  (2) Archive_Base64 local-first preconditions (checks-mode quadratic base64 decoding removed; unit proves 0 unproved/0 warnings).
- 41e6f43: agent records compared in canonical JSON form (retained side is sorted-key canonical evidence). test_finalization_agent_binding
  74/74 OK on the checks library built from f484b29 (Source20: 5 errors).
- 9a2c814: test fixture correction in test_finalization_kernel.collapse_values (resulting requirement supplied, as Collapse requires and
  the sibling fixture does). test_finalization_kernel 17/17, test_finalization_owned_abi 8/8.
- Known remaining test-harness defects (pre-existing, also on Source20): test_context_cast_lifetime (3 of 5) compares raw pointer fields
  captured_results/retained_results that its snapshot does not exclude, and an audit trace that includes the first ctypes dlsym.
  To be triaged with the complete roster result.
- roster-run-3 started on 9a2c814 with a 1800 s survey deadline (evidence/roster-run-3).
