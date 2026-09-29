# Phase 1: evaluation lifecycle authority (1.8.0)

This closes the evaluation-lifecycle item of the COSMOGONY Phase 1 authority-kernel expansion,
on the 1.7.3 line. The `Worldline.Evaluation` SPARK unit owns the classification of every check
record, the per-check promotion predicate, the roster rule, and the lifecycle relation. The
collapse decision (`Worldline.Collapse.Decide`) now carries the checkpoint-return case as an
explicit, witnessed mode. Python maps observed fields to the kernel's finite categories, asks
the kernel, and records what it answered. It has no admission expression of its own.

The requirement (roadmap, Phase 1):

> Model evaluation lifecycle explicitly. Admissibility requires completed execution, passing
> outcome and complete evidence. Not attempted, interrupted, incomplete, evaluator-incomplete
> and unknown execution cannot authorize. No default branch may manufacture completion.

## Requirements to contracts

Line numbers are in `core/worldline-evaluation.ads` (E) and `core/worldline-collapse.ads` (C)
at this release. Every contract below is proved by GNATprove at `--level=3` (see "Proof").

| Clause | Contract | Runtime call sites |
| --- | --- | --- |
| The lifecycle is modelled explicitly | `Transition_Allowed` (E:21-36): the exact relation as the postcondition. Completed is reachable only from Started, an examiner only from Prepared, and every terminal state is final. `Advance` (E:38-44) moves only along it. | C exports `wl_evaluation_transition_allowed` and `wl_evaluation_advance`; `Core.evaluation_transition_allowed` and `Core.evaluation_advance`. No runtime state is persisted through them in 1.8.0 (see "Decisions", D5). |
| A classification is a legal lifecycle end | `Classify` (E:120-160) postcondition: `Reachable` (E:49-54) holds of every result, and a result is never Prepared or Started. | `finalize.evaluation_record` |
| Admissibility requires completed execution and a passing outcome | `Admissible` (E:181-192) exact postcondition: `Execution = Completed and Result = Passed`. `Classify` postcondition: an outcome exists exactly when execution completed, and it is the recorded verdict (`Completion_Possible`, E:103-118). | `finalize.evaluation_record`, which is called by `roster_decision` at finalize, revalidate and promotion |
| Admissibility requires complete evidence | `Admissible` requires `Evidence_Complete (Presence)` (E:172-178) over the typed facts `Evidence_Presence` (E:164-170): record identified, verdict recorded, examiner binding established, declaration matches the policy, and a declared bundle named as what executed. | `finalize.evaluation_presence` reads each fact from a named field, and the declaration from the requirement record (`check_declarations`), never from the result. |
| Not attempted, interrupted, incomplete, evaluator-incomplete and unknown execution cannot authorize | `Admissible` admits only `Completed`. `Classify` names the refusals: a malformed channel is Unclassified, a stopped supervisor is Interrupted, unassessed or absent status with no exit is Not_Attempted, a sandbox that never started is Error_Before_Examiner, and unsatisfied imports never complete. | as above |
| No default branch manufactures completion | `Classify` starts at Unclassified and completes only through `Completion_Possible`. `Roster_Complete` (E:200-207): an empty roster is complete only when `Empty_Declared`. `Decide` in Checkpoint_Return mode requires a witness (C:89-100, C:102-116). | `roster_decision` (finalize, revalidate, promotion); `CollapseTransaction._checkpoint_fields` |
| A saved classification is not authority | (runtime) every decision site recomputes from the raw record | `roster_decision` never reads a stored `evaluation`; `tests/test_authority_static_audit.py` enforces it |

## Proof

`prove.sh` runs `gnatprove -P core/worldline_core.gpr -U --level=3` and fails unless every
check is proved with none justified and no `pragma Assume`, the total reaches the floor
(`MINIMUM_CHECKS = 158`), and every subprogram in the summary is flow analyzed without error and
proved. `REQUIRED_PROVED` names the subprograms this release claims: `Evaluation.Transition_Allowed`,
`Advance`, `Classify`, `Admissible`, `Roster_Complete`, `Collapse.Decide`, and the transaction
lifecycle. `proof-manifest.json` records per-subprogram coverage, and `verify_proof_manifest.py`
and assurance compare it with a fresh run: the coverage must be identical, where the library
hash and the summary bytes may differ by toolchain.

**Not proved (boundary).** The C ABI decode in `worldline-c_api` (`SPARK_Mode => Off`) and the
Python mapping of observations to categories. The C layer rejects every out-of-range code, every
Boolean byte other than 0 or 1, and every nonzero reserved byte with 255. A classification that
`Classify` could not have produced (an outcome without completion, or the reverse) is also an
invalid encoding. `tests/test_abi_layout.py` compares the header, the ctypes records and the
library's own layout (`wl_layout_size`) field by field. The runtime refuses a library whose
`wl_abi_version` is not 4.

**External assumptions.** SHA-256 is functionally correct (tested against published vectors,
not proved) and collision-resistant: every identity equality `Decide` proves is an equality of
digests. The runtime supplies authentic observations, and it computes each `Decide` input from
the independent source its comment names.

## Decisions

- **D1: unsatisfied imports never complete.** 1.7.3 counted a PASS from an examiner whose
  staged bundle could not satisfy a module-level import as COMPLETED/PASS. The import resolved
  from somewhere WORLDLINE did not stage, possibly the candidate's own tree. Such a run is now
  Evaluator_Incomplete, whatever it reported. To keep the stricter rule from blaming legitimate
  verifiers, a package the host installation provides in its system site-packages (read-only
  paths under `sys.base_prefix`) is not a gap. Observed before the change: every PASS record on
  the production store had `unsatisfiedImports: []`.
- **D2: an empty roster must be declared.** At promotion the roster is the policy's required
  checks, plus `protected-paths` whenever the policy protects anything. It is empty-and-complete
  only when a `.worldline.json` was read (`sourceSha256` present). A project with no policy has
  declared nothing, and a collapse there is refused (EXECUTION_EVIDENCE_INCOMPLETE).
  `"checks": []` is an explicit declaration. At finalization the agent's own exit is always on
  the roster.
- **D3: checkpoint return is an explicit kernel case.** `Collapse_Request` layout 4 adds
  `Evaluation_Mode` and a checkpoint witness. In Checkpoint_Return mode `Decide` does not consult
  the candidate-evaluation fields. It requires `Checkpoint_Witnessed` and
  `Expected_Checkpoint = Witnessed_Checkpoint`. The witness is the content identity a different
  record states for the subject:
  - the `parent_content` its child on the PRIME lineage recorded, or
  - the PRIME register's `primeContent`.

  Every PRIME is parented on the PRIME it displaced, so only worlds that were live have a
  witness. The actor string still selects the path, but it no longer grants anything.
- **D4: reserved names.** The adapter names `worldline` and `system` are refused in
  `agentCommands`, because a fork's actor is its adapter's name. The check ids `agent` and
  `protected-paths` are refused in policies, because those roster slots belong to results
  WORLDLINE produces itself.
- **D5: Prepared and Started stay in the model, unpersisted.** The runtime records only
  terminal classifications. The kernel proves that every classification is reachable under the
  lifecycle relation and is never an in-flight state. Persisting per-check lifecycle steps
  belongs with the recovery state machine (Phase 1, item 7).
- **D6: a system future is never promoted.** Simulation worlds already could not collapse. Now
  they cannot be a `return` subject either. Their VALID/DEGRADED state reports what the
  in-future runner said. Each result carries the kernel's classification, which admits nothing,
  because no policy declares those commands.

## Defects closed (reproduced on 1.7.3 first)

1. **Re-applying a failed world.** A world whose required exam COMPLETED with FAIL was DEGRADED,
   then ARCHIVED when a sibling collapsed. `return <it>` was AUTHORIZED and committed its bytes
   as PRIME, because the promotion boundary checked only that execution reached the examiner.
   1.8.0 refuses it with EXECUTION_EVIDENCE_INCOMPLETE.
2. **The synthetic world a refused `return` leaves behind.** It was VALID with actor
   `worldline`. After any later PRIME change, `return <it>` took the checkpoint path, which
   required no evidence. This promoted a world whose evidence had been refused as stale, and it
   reverted the newer policy. 1.8.0 refuses it with CHECKPOINT_UNWITNESSED.
3. **An undeclared empty roster.** A project with no policy collapsed with the execution
   roster reported complete. 1.8.0 refuses it (D2).
4. **Malformed observations.** A Boolean `exitCode` counted as an integer exit status. An empty
   bundle record counted as no bundle. Both now fail to complete or to verify.

The scenarios are tests in `tests/test_evaluation_lifecycle_promotion.py`. The 1.7.3-side
reproductions are retained with the release evidence.

## Divergence from 1.7.3 (parity campaign)

This is sampling, not proof. Both classifiers ran over a generated grid of 162,000 check
records:

- 120,394 were classified identically.
- 41,606 diverged. Every divergence falls in a declared class:
  - D1: unsatisfied imports never complete;
  - a Boolean exit code is not an exit status;
  - an empty or falsy bundle record is unverifiable;
  - a declared bundle must name what executed.
- No record is admitted by 1.8.0 that 1.7.3 refused.

## What Python still decides (listed, owned by later items)

`tests/test_authority_static_audit.py` lists every remaining comparison of a verdict with
"PASS" or "COMPLETED" in the promotion modules, each with its reason:

- **`transaction.prepare`: a staged-merge revalidation outcome selects `tested := staged`.**
  The outcome is now the kernel's roster verdict. The tested=staged obligation belongs to
  Phase 1, item 1.
- **`validation.effective_evidence`: which evaluation speaks for a world.** A later FAIL does not
  supersede an earlier PASS. This belongs to Phase 1, item 5 (one effective evaluation).
- **`finalize._private_report_verified`: report-integrity facts.** These are inputs to the
  kernel, and they can only lower trust.

This release does not complete Phase 1. Typed absence, the rest of the collapse rule, resource
and capability accounting, recovery and the receipt chain are separate items. The running
installation is a separate state from this source.
