# Capture scanner and recursive projection repair

This candidate repairs the original input domain. It does not replace the full
Phase One proof, runtime roster, protected witnesses or independent acceptance.

## Line and word scanning

The original line scanner increments an absolute byte index beyond the final
legal index. `scoped-scan-baseline-v1` reproduces `CONSTRAINT_ERROR` with an owned,
one-byte array. The repair scans offsets bounded by the actual array length;
only offsets strictly inside the array are converted into readable indices.
The end offset remains representable even when the last absolute index has no
successor. This is the same representation used by the namespace scanner.

An empty value retains its original first index wherever representable. Only
the previously overflowing empty value at the maximum absolute index uses the
existing canonical empty span. A second matching field is rejected when the
first value is nonempty; the original empty-value duplicate behavior remains.
The field-name comparison, separator, newline and whitespace grammars remain.

`Word` consumes a known first nonspace byte before its continuation loop. Its
whitespace invariant preserves the entry offset so the outer progress check
can establish strict advance. Its new postcondition places every nonempty
result inside the supplied span. `Maps_Match` uses the same line-end helper
and retains all four original permitted roles and complete path comparisons.

## Recursive call cycle

The measure is a pair: an archive-span length followed by a call-stage rank.
Root capture uses provenance length and rank 3; subject capture uses the maximum
of subject and primary lengths and rank 2; role roster uses inventory length
and rank 1; initial-root transport uses inventory length and rank 0.

Field extraction has separately checked size contracts. Root-to-subject and
subject-to-roster may retain the same size but decrease the stage. Roster to
initial transport retains the inventory and decreases the stage. The call back
to root capture must shrink through nested original source fields. The existing
roster self-call still strictly shrinks its inventory. No depth limit, new
input precondition, trusted flag, or assumed child-size fact is introduced.

The public alias wrapper does not call itself. Its ineffective recursive
variant is removed; the local recursive `Find` retains its original strict
measure, and the function's implicit termination obligation remains. An attempt
to spell `Always_Terminates` explicitly on that function was rejected by the
installed tool and is retained in the failed proof receipts.

The last cycle check first exceeded its job deadline while analyzing the raw
native record inside the same function. The native comparison tail is now a
private, nonrecursive helper. Its comparison tokens and their order are
preserved, as recorded in `capture-native-tail-relocation.json`. The internal
precondition repeats the existing byte-shape gates. `Bytes_Shape` expresses its
unchanged predicate directly, exposing the validity and length facts to the
helper proof. No raw comparison was removed to make the cycle check smaller.

The maps path check likewise separates a complete role/path lookup from cursor
movement. The helper validates the encoded path, materializes it once, and
performs the original complete byte comparison and role alternatives. This
preserves the old short-circuit ordering while avoiding duplicate materialized
path arguments. The helper itself is included in the selected proof campaign.

## Evidence boundary

`capture-helper-proofs-v2` checks complete named helper scopes, including the
public postconditions. `capture-cycle-proofs-v1` checks the selected recursive
call sites. Inspect each fresh report and diagnostic, not a shared report's
aggregate cached total. These are local termination and safety obligations;
they do not prove complete capture authenticity or complete functional behavior.

The baseline failure, initial compile visibility error, command path typo,
missing word-loop progress invariant, and rejected function aspect remain in
their original receipts. The final verification summary records which repairs
and runtime checks actually completed. The short SIA recall timed out; a later
bounded recall succeeded with senses live, chains pass and graph complete.
Returned notes were model-origin navigation, and new note indexing was not
established by that recall. Local receipts remain the verification authority.
