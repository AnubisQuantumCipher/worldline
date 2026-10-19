# Custody input decoding repair

This is a nonfinal Phase One repair. Evidence classes and remaining gates are
recorded separately; decoder values confer no custody authority.

## Ownership and initialization

`Counts.Table` previously wrote a component of `Result` while its nested `Add`
also accessed `Result`. A separate local row count now receives each table's
output before assignment to the original destination. Table order, widths,
status changes and byte counts are preserved.

`Cell`, `Global_Field`, `Table` and `Intern` now receive the specific arena and
input span they use. They no longer capture the whole output owner while also
receiving its components as output arguments. The arena is fully initialized
before copying the original input prefix. No whole-owner copy, relaxed
initialization, input cap or SPARK exclusion is introduced.

## Arithmetic and constrained outputs

The selected `View_Byte` proof exposed overflow in the base64 quartet index.
An exact-source isolated reproducer raised `Constraint_Error` at that operation
with a maximum Count offset. The repair tests representability before forming
the quartet index and preserves the level-zero out-of-view convention. The
repaired source also runs against an independently decoded base64 reference.

Input-copy and SQL-append endpoint sums group their offsets before adding an
array origin, avoiding a transient one-past-end value. Tests include arrays
ending at the maximum Byte_Index.

`Append_SQL_Cell` previously assigned a null discriminant to every output,
including constrained actuals. It now initializes the actual variant and checks
class compatibility before writing arena bytes. An incompatible class returns
`Malformed`, leaving the arena and used extent unchanged. Unconstrained outputs
retain their original null initialization and normal behavior. Constrained
matching variants can receive the correctly typed decoded value. No public
precondition is tightened. The constructor's result-kind postcondition is
proved before relying on it in the append proof.

Null input still takes the early-return path. A local non-null class subtype
expresses the alternatives that can reach the final assignment; it removes a
proved-unreachable case without removing null inputs from the decoder domain.

## Verification boundaries

Selected strict proofs cover `View_Byte`, `View_Length`, `Empty_SQL_Cell` and
`Append_SQL_Cell`. The whole-unit numeric attempt timed out and does not establish
numeric safety of the remaining routines. Strict flow is a separate result.

Committed synthetic empty and populated envelopes are reproduced by the original
producer codec. Direct tests check all six table rosters, SQL classes, copied
input bytes, grown buffers, capacity refusal, rebased/maximal input indices, and
constrained-output compatibility/refusal. These are decoder controls, not real
protected startup, actor witnesses, authenticated history or F7 acceptance.

All original runtime and acceptance requirements remain. Existing compiler
array-syntax warnings remain visible; a compiler-directed syntax candidate is
preserved separately and is not silently treated as verified source.
