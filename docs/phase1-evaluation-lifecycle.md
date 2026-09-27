# Phase 1 evaluation lifecycle boundary

This is a bounded part of the COSMOGONY Phase 1 authority-kernel expansion. The
`Worldline.Evaluation` SPARK unit owns per-check execution classification, the
completed/pass/evidence admission predicate, and legal same-identity lifecycle
transitions. The C ABI validates each finite input code before calling SPARK. The
Python runtime maps observed raw fields into those codes and requires the new
exports. It has no independent per-check admission expression.

## Contract map

| Requirement | Enforced location | Boundary |
| --- | --- | --- |
| Unknown, interrupted and incomplete evaluation cannot admit | `Worldline.Evaluation.Admissible` | The observation category comes from Python. |
| Completed admission requires a pass | `Admissible` exact postcondition | A pass is only a classified check result, not proof that the evaluator is correct. |
| A missing per-check record cannot be promoted by default | `Admissible` requires explicit `Evidence_Complete`; runtime supplies `bool(result)` | The policy-wide roster is checked separately by finalization and transaction logic. |
| A completed evaluation cannot resume under the same identity | `Transition_Allowed` and `Advance` | These lifecycle transitions are specified and proved, but are not yet used by runtime state storage. |
| Unknown/malformed raw categories do not become completion | `Classify` and C ABI validation | Origin, supervisor, channel and bundle observations are trusted inputs, not proved facts. |

The C header now describes the actual v1.5 collapse request tail as well as the
new evaluation ABI. Existing collapse ABI behavior remains in place. The new
Python runtime refuses a library missing the evaluation exports.

## Scope and next work

This change does not complete Phase 1. The collapse request still contains bare
hashes and booleans; optional presence, coherent whole-roster evaluation,
capability and resource epochs, reservation accounting, recovery state, and
receipt-chain rules need their own SPARK contracts and runtime integration.
The C/Python boundary, evidence provenance, Linux supervision, and filesystem
observations remain outside this proof. `Transition_Allowed` is a specified
kernel operation awaiting runtime lifecycle integration.

See the local `evidence/README.md` for the exact build, proof, tests, source
identity and retained logs of this candidate. This document and the generated
`proof-manifest.json` are source-controlled; the running installation is a
separate state.
