# Replay row-model proposal — source only

This is a separate, unintegrated shadow increment. No compiler, proof, runtime,
mount or heavy job ran. Existing product files and replay-proof-proposal-v1 were
not edited. Root must obtain fresh independent source review and separately
qualify exact source before integration.

before/ preserves the exact replay body and spec from replay-proof-proposal-v1.
after/ adds only private Equality_Model and Row_Model expression functions and
exact record-equality Posts on Equality_Row and Inspect_Row. row-model.patch is
unapplied. The operational branch bodies, replay fold, Conforms and public replay
spec remain byte-identical. static-verification.json records a textual
reconstruction check; it is not Ada verification. The initial checker's
declaration-line matching failure is retained separately.

Both models take Data, an already selected Row and existing Op. They use cached
Node values and a fixed number of row-local Field/Is_True/Is_False queries.
They do not call Parse, Element, a prefix predicate, uniqueness, Plan or a mask
traversal. Their definitions never call the branch function being specified.
The equality helper model admits arbitrary Op strings exactly as its helper does.

A matched attach with malformed unitEq retains (False,1); an unmatched attach
requires explicit JSON null. Release observes ne independently of eq.
Reconciliation observes literalFalse independently of original-state truth.
No Pre, input cap, row cap, assumption, justified check, exclusion or warning
suppression was added. Full-domain selector safety/termination remains unproved.

reference/declarative-preimage.patch retains the original independent iff target,
including mask/cardinality/position semantics. Its old repeated-prefix execution
technique remains rejected by the copied checked-cost-rejection receipt. Do not
apply that historical patch. The copied parent spec preserves its explicit
Code/Position/mask-byte range conjunction. No new public Plan predicate or bridge
is supplied by this increment.

row-cases.json contains source-derived boundary expectations, not executed tests.
A future admitted harness must select its Row outside the model; do not expose
private helpers or narrow their domain merely to make a harness convenient.

The new checked work is row-local and fixed in call structure; it is not claimed
constant-time in input bytes. Field can scan/parse the row transitively, and
existing optional uniqueness/Element/parser costs remain. Equality and Inspect
Posts may both evaluate on an equality row when checks are enabled. Actual
generated code, copying/allocation, transitive helper termination, peak resources
and deadline behavior require measurement/proof. No compiled resource bound or
whole-replay linear-time claim is made.

Next evidence is fresh exact-source review, complete selected-unit legality and
strict proof of both models, both Posts and all callers/dependencies at preserved
settings, then adversarial checked runtime/native evidence. Fold induction,
bidirectional declarative equivalence and production Plan establishment are
separate required steps. Preserve all original final gates and F7. No approval,
proof result or acceptance credit follows from these files.

Snapshots are hash-bound in manifest.json; they are not OS-enforced immutable.
