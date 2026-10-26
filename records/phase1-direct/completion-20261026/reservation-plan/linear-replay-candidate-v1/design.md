# Unintegrated reservation replay proposal

Status: SOURCE ONLY. Ada legality, proof, checked runtime and the Plan-to-replay
bridge are UNRUN/UNPROVEN. Production source, its existing public contract,
assertion policies, pins and tests are unchanged. No C1-C4 gate is closed.

## Narrow actual contract change

`reconciled-gone.patch` adds only a declaration/Post to the existing private
Reconciled_Gone function. Its body and the public input domain are unchanged.
Existing Resource_Reservation_Lifecycle.Remove_Row is an expression function:
for Reconcile_Observed it returns Row.Observed = Gone. The caller supplies Gone
exactly when Observed_False is true, otherwise Unknown. Therefore its existing
exact definition entails Reconciled_Gone'Result = Observed_False. This is the
source-derived proof obligation, not a fabricated GNATprove result. The added
checked Post performs one Boolean equality per original reconciliation call.
It performs no parse, prefix scan, allocation, or additional acquisition.

## Independent result replay

The separate Ghost package is not imported by production. It never calls Plan
and never invokes Python objects. Conforms derives expected output only from
the immutable captured Data, cached Root/Rows/Op, and scalar replay state. The
candidate Mask influences only the comparison result, never expected choices.
Appending Conforms to production Plan's Post is NOT included or approved yet.

Capture_Ready retains schema/profile/row-count validation and the original
ordering: optional builtin validation, then optional uniqueness. Each optional
pass runs at most once. Flags are enabled only by literal true. Missing and
nonstring identity payloads retain their original uniqueness treatment; string
identity equality uses the existing decoded-value Equal, including escape
equivalence. Parse/Field retain last-key-wins semantics. No digest substitutes
for equality and no identity spelling or observation is normalized.

Replay_Rows tracks Matches, Last_Match, Failed and Same. Each mask entry is
compared once. After the first malformed row, expected remaining entries are
zero and no later row is inspected. A matched attach-unit records byte1 and
position before malformed unitEq, matching the original partial Ada output.
An unmatched attach-unit admits unitEq only when explicitly JSON null; missing
is still malformed. Completed non-identity-match operations reset position to
zero. Identity-match succeeds only for exactly one selection. Control captures
expect a zero mask and preserve guard validation/short-circuit order before
delegating the complete manager capture. Reconciliation uses literalFalse,
not truth conversion of the original observation. eq and ne remain distinct.

## Checked work and memory boundaries

The candidate removes the rejected replay-of-prefix patterns, not original
comparison complexity. A replay performs at most one original n(n-1)/2 pair
pass, one optional n-row builtin pass, one n-row decision pass, and n mask
comparisons. It caches the input root/rows/op once. The remaining Element,
Field, Equal, Text, parser, and manager-query costs remain controlling; this
is NOT a claim of total O(n) time or constant physical memory. In particular,
Element still scans from the array start and uniqueness remains pairwise.
Adding a checked replay would duplicate a constant number of original passes.
No row index, mask copy, normalized payload array, recursion, prefix quantifier,
new Pre, new input cap, or assertion suppression is introduced here.

Scalar loop invariants bound Matches and Last_Match by the processed count.
They are not advertised as a complete functional induction. Bounds, flow,
termination, full malformed-domain behavior, allocation and deadline safety,
and producer dependency proof remain to be established on the installed tools.
The existing manager's pure Decide may allocate and is evaluated again in the
guard replay; its original complexity/resource obligations remain open.

## Required equivalence and integration obligations

1. Prove the constant Reconciled_Gone Post against the actual existing
   Remove_Row definition, retaining all existing contracts and callers.
2. Build and prove this package without new exclusions/Assume/justifications;
   establish range, flow and termination for all original inputs and bounds.
3. Prove Conforms equivalent to the earlier declarative Plan_Conforms over
   every Mask lower bound/null length, malformed prefix/partial output,
   duplicate-key spelling, optional flag, row operation and control branch.
4. Prove production Plan establishes Conforms without repeated executable
   prefix scans. That bridge is currently UNPROVEN; neither implementation
   similarity nor scalar bound invariants discharge it. Preserve the current
   range contract in any future strengthening. Do not remove required checked
   obligations merely to obtain the advertised complexity.
5. Retain and execute the original ordinary/native/alias/fault controls plus
   independent model comparison and the accepted opaque64-row cost witness.
   Measure actual checked work, stack/allocation and original deadlines.
6. Only the root may adopt any integrated successor and regenerate source
   pins after review. Complete C1-C4, full same-source campaigns, O1,
   authentic protected/actor evidence and F7 remain separate obligations.

The earlier e6bed patch and its quartic counterexample remain historical
evidence. This candidate neither applies that patch nor deletes its failure.
