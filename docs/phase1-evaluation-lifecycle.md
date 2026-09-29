# Phase 1: evaluation lifecycle authority (1.8.0)

This closes the evaluation-lifecycle item of the COSMOGONY Phase 1 authority-kernel expansion,
on the 1.7.3 line.

- The `Worldline.Evaluation` SPARK unit classifies every check record, admits or refuses each
  check, judges the roster, and states the lifecycle relation.
- The collapse decision (`Worldline.Collapse.Decide`) carries the checkpoint-return case as an
  explicit mode.
- Python maps observed fields to the kernel's finite categories, asks the kernel, and records
  what it answered.

The requirement (roadmap, Phase 1):

> Model evaluation lifecycle explicitly. Admissibility requires completed execution, passing
> outcome and complete evidence. Not attempted, interrupted, incomplete, evaluator-incomplete
> and unknown execution cannot authorize. No default branch may manufacture completion.

## Requirements to contracts

Line numbers refer to `core/worldline-evaluation.ads` (E) and `core/worldline-collapse.ads` (C)
at this release. Every contract below is proved by GNATprove at `--level=3` (see "Proof").

| Clause | Contract | Runtime call sites |
| --- | --- | --- |
| The lifecycle is modelled explicitly | `Transition_Allowed` (E:21-36) states the whole relation as its postcondition: Completed is reachable only from Started, an examiner only from Prepared, and every terminal state is final. `Advance` (E:38-44) moves only along it. | C exports `wl_evaluation_transition_allowed` and `wl_evaluation_advance`. No runtime state is persisted through them in 1.8.0 (D5). |
| A classification never claims an attempt in flight | The `Classify` postcondition (E:113-151) excludes Prepared and Started. The C layer refuses those codes as admission input. | `finalize.evaluation_record` |
| Admissibility requires completed execution and a passing outcome | `Admissible` (E:172-183) has an exact postcondition: `Execution = Completed and Result = Passed`. `Classify` postcondition: an outcome exists exactly when execution completed, the outcome is the recorded verdict, and completion requires `Completion_Possible` (E:96-111). | `evaluation_record`, called by `roster_decision` at finalize, revalidate and promotion |
| Admissibility requires complete evidence | `Admissible` requires `Evidence_Complete (Presence)` (E:163-169) over the typed facts `Evidence_Presence` (E:155-161): record identified, verdict recorded, examiner binding established, declaration matches the policy, and a declared bundle named as what executed. | `finalize.evaluation_presence` reads each fact from a named field. The declaration comes from the requirement record (`check_declarations`), never from the result. |
| Not attempted, interrupted, incomplete, evaluator-incomplete and unknown execution cannot authorize | `Admissible` admits only `Completed`. `Classify` names these refusals: a malformed channel is Unclassified; an agent record whose supervision is absent or stopped is Interrupted; an external record with unassessed status, or with absent status, no exit and no channel, is Not_Attempted; an external sandbox that never started is Error_Before_Examiner; and a FAIL with unsatisfied imports never completes. | as above |
| No default branch manufactures completion | `Classify` starts at Unclassified and completes only through `Completion_Possible`. `Roster_Complete` (E:191-198) treats an empty roster as complete only when `Empty_Declared`. `Decide` in Checkpoint_Return mode requires a witness (C:89-100, C:102-116). | `roster_decision` (finalize, revalidate, promotion); `CollapseTransaction._checkpoint_fields` |
| A saved classification is not authority | Runtime: every decision site recomputes from the raw record. | Behavioural test: a forged saved evaluation is refused (`tests/test_evaluation_authority.py`). Tripwire: `tests/test_authority_static_audit.py`. |

**What the Classify postcondition does not say.** It fixes the safety direction: what may
complete, that an outcome is the recorded verdict, and the named refusals above. It does not
determine every non-completed classification. For example, it does not say whether a stopped
external run is Interrupted or Incomplete_Unknown. Those choices are the body's, tested but
not specified. None of them can admit.

## Proof

`prove.sh` runs `gnatprove -P core/worldline_core.gpr -U --level=3`. It fails unless:

- every check is proved, none justified, with no `pragma Assume`;
- no GNATprove annotation of any kind appears in the source (justification or skip);
- the total reaches the floor (`MINIMUM_CHECKS = 156`);
- in the summary's per-unit section, every listed subprogram line is exactly the "flow analyzed
  without error and proved" form, and each unit lists as many proved subprograms as it
  analyzed. A skipped proof, a skipped flow analysis or an unknown line format fails the gate.

The floor, the required subprograms and the declared boundary are pinned in
`verify_proof_manifest.py`, and `prove.sh` imports them from there. The verifier refuses a
manifest that:

- claims fewer checks than the floor;
- drops a required subprogram;
- omits a core unit.

Assurance compares the per-subprogram coverage of a fresh run with the committed one. The
library hash and the summary bytes may differ by toolchain.

**Not proved (boundary).** Two things sit outside the proof: the C ABI decode in
`worldline-c_api` (`SPARK_Mode => Off`), and the Python mapping of observations to categories.
The C layer answers 255 for:

- every out-of-range code;
- every Boolean byte other than 0 or 1;
- every nonzero reserved byte;
- every classification `Classify` could not have produced: an outcome without completion,
  completion without an outcome, or an in-flight state.

The library reports each record's size and each field's offset by name (`wl_layout_size`,
`wl_layout_offset`). At load the runtime refuses a library that is not ABI generation 4, or
whose sizes or named offsets differ from its own ctypes records. `tests/test_abi_layout.py`
also compiles the header with `cc` and compares every offset and every code table with the
runtime.

**External assumptions.**

- SHA-256 is functionally correct and collision-resistant. Correctness is tested against
  published vectors, not proved. Every identity equality `Decide` proves is an equality of
  digests.
- The runtime supplies authentic observations, and it computes each `Decide` input from the
  independent source its comment names.

## Decisions

- **D1: unsatisfied imports relabel a FAIL, not a PASS (1.7.3 semantics kept).** The import
  analysis is conservative: module level, absolute, satisfied by the standard library or a
  staged sibling. It cannot tell a helper the evaluator failed to stage from the candidate's
  own module under test, which a test is supposed to import. A FAIL with a gap is
  Evaluator_Incomplete. It is not a verdict on the candidate, and it cannot admit either way.
  A PASS with a gap resolved its imports and stays a completed pass.
  - A first 1.8.0 candidate refused every PASS with a gap. Review showed this made the common
    test layout unpromotable. It also did not keep candidate code out of the examiner: the same
    import moved into a function passed.
  - That the examiner's judgment is independent of candidate code it runs remains a stated
    non-claim.
- **D2: the promotion roster, and an empty one must be declared.** At promotion, the kernel
  gives two verdicts, and both are required:
  1. The policy roster: the policy's required checks, plus `protected-paths` whenever the
     policy protects anything. It is empty-and-complete only when a `.worldline.json` was read
     (`sourceSha256` present).
  2. The agent's own exit. It is judged from the subject's finalization record, because no
     revalidation re-runs it.

  A project with no policy has declared nothing, so its collapse is refused
  (EXECUTION_EVIDENCE_INCOMPLETE). A policy file whose `checks` is `[]` is an explicit
  declaration.
- **D3: checkpoint return is an explicit kernel case.** `Collapse_Request` layout 4 adds
  `Evaluation_Mode` and a checkpoint witness. In Checkpoint_Return mode, `Decide` does not
  consult the candidate-evaluation fields. It requires `Checkpoint_Witnessed` and
  `Expected_Checkpoint = Witnessed_Checkpoint`. What this establishes, exactly:
  - Python walks the PRIME lineage (`CollapseTransaction._checkpoint_witness`). Each PRIME is
    parented on the PRIME it displaced. The walk decides whether the subject world was ever
    live (`Checkpoint_Witnessed`).
  - The kernel's equality checks that the subject's content identity agrees with the one a
    different record states for it: its lineage child's `parent_content`, or the PRIME
    register. On an unaltered store the two always agree.
  - The bytes restored are bound separately, by `return_point_manifests`: the stored manifest,
    or a committed receipt's `beforeRoot`.

  So a world that never became live has no witness and is refused (CHECKPOINT_UNWITNESSED).
  The actor string still selects the mode, but it no longer grants anything. Two kinds of
  world are not return points in 1.8.0, although 1.7.3 accepted them:
  - A PRIME from before a reset. Removing the last root starts a new lineage.
  - A COLLAPSED `return-*` world whose commit published a new generation. The published
    generation (`prime-*`) is the return point.
- **D4: reserved names.**
  - The adapter names `worldline` and `system` are refused in `agentCommands`, because a
    fork's actor is its adapter's name.
  - The check ids `agent` and `protected-paths` are refused in policies, because those roster
    slots belong to results WORLDLINE produces itself.
- **D5: Prepared and Started stay in the model, unpersisted.** The runtime records only
  classifications. The kernel proves that a classification is never in flight: it is Not
  Attempted or a terminal state. Persisting per-check lifecycle steps belongs with the
  recovery state machine (Phase 1, item 7).
- **D6: a system future is never promoted.** Simulation worlds already could not collapse,
  and now they cannot be a `return` subject either. Their VALID/DEGRADED state reports what
  the in-future runner said. Each result carries the kernel's classification, which admits
  nothing, because no policy declares those commands.

## Defects closed (reproduced on 1.7.3 first)

The reproducers ran against the unmodified 1.7.3 source and are retained with the release
evidence. The 1.8.0 side of the first four scenarios is tested end to end in
`tests/test_evaluation_lifecycle_promotion.py`.

1. **Re-applying a world whose required check failed.** The check COMPLETED with FAIL, so the
   world was DEGRADED. It became ARCHIVED when a sibling collapsed. Then `return <it>` was
   AUTHORIZED and committed its bytes as PRIME, because the promotion boundary checked only
   that execution reached the examiner. 1.8.0 refuses it with EXECUTION_EVIDENCE_INCOMPLETE.
2. **Re-applying a world whose agent failed.** The policy checks passed but the agent's own
   exit did not. The world went DEGRADED, then ARCHIVED, and was AUTHORIZED and committed.
   This was found by the review of the first 1.8.0 candidate, whose promotion roster still left
   the agent out. 1.8.0 refuses it (D2).
3. **The synthetic world a refused `return` leaves behind.** It stayed VALID with actor
   `worldline`. After any later PRIME change, `return <it>` took the checkpoint path, which
   needs no evidence. It promoted a world whose evidence had been refused as stale, and it
   reverted the newer policy. 1.8.0 refuses it with CHECKPOINT_UNWITNESSED.
4. **An undeclared empty roster.** A project with no policy collapsed with the execution roster
   reported complete. 1.8.0 refuses it (D2).
5. **Malformed observations.** A Boolean `exitCode` counted as an integer exit status, and an
   empty bundle record counted as no bundle. Both now fail to complete or to verify. Tested in
   `tests/test_evaluation_authority.py`.

## Divergence from 1.7.3 (parity campaign)

This is sampling, not proof. Both classifiers ran over a generated grid of 162,000 check
records. The 1.8.0 side runs with a declaration synthesized to match each record, so
declaration mismatches are covered by unit tests, not by this grid. Classes are assigned by
record shape, and a record with two features gets the combined class.

- 120,532 records were classified identically.
- 41,468 diverged. Every divergence falls in a declared class:
  - a Boolean exit code is not an exit status;
  - an empty or falsy bundle record is unverifiable;
  - both of those together;
  - a declared bundle must name what executed;
  - on the agent path, a FAIL with unsatisfied imports is evaluator-incomplete (inadmissible
    either way).
- No record is admitted by 1.8.0 that 1.7.3 refused.

## What Python still decides (listed, owned by later items)

`tests/test_authority_static_audit.py` lists every remaining comparison with a verdict, and
every read of a saved verdict field, in the promotion modules. Each entry has a count and a
reason. The main remaining decisions:

- **`transaction.prepare`: a staged-merge revalidation outcome selects `tested := staged`.** The
  outcome is now the kernel's roster verdict. The tested=staged obligation belongs to Phase 1,
  item 1.
- **`validation.effective_evidence`: which evaluation speaks for a world.** A later FAIL does not
  supersede an earlier PASS under an unchanged requirement. This belongs to Phase 1, item 5
  (one effective evaluation). Promotion recomputes every check of the selected evaluation in the
  kernel, but it does not choose the evaluation.
- **`finalize._private_report_verified`: report-integrity facts.** These are inputs to the
  kernel, and they can only lower trust.

This release does not complete Phase 1. Typed absence, the rest of the collapse rule, resource
and capability accounting, recovery and the receipt chain are separate items. The running
installation is a separate state from this source.
