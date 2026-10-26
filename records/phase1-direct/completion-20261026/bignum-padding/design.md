# Zero-coefficient prefix evaluation

Status: source change prepared; build, proof and runtime verification UNRUN.

The existing accepted encoding domain includes empty and high-zero-padded
little-endian operands. The unchanged successor regression has fifteen failed
subcases at 4096 redundant high zero bytes, including mathematical 0 + 1.
Its original inputs, exact-oracle fixture and failing output are retained under
`preimages/`, with a SHA256 roster in `preimages.json`.

The production path is `custody_event_capture.successor` through
`wl_custody_successor_le_v2`, `Custody_V2_Mutation_Decision.Successor_LE`, and
`Significant_Length`'s `Resource_Quantities.Is_Negative` call. Checked sign and
magnitude postconditions call `Prefix_Value`. The independent `Prefix_Reference`
already skips a zero digit. The public `Prefix_Value` postcondition instead
evaluated `0 * Power_Reference(Count - 1)`, constructing a value unrelated to the
small resulting magnitude. The installed GNAT `s-genbig.adb` Normalize routine
has `Bignum_Limit = 200` and raises Storage_Error on oversized intermediates.
This source path explains a concrete mechanism; no fresh stack trace is claimed.

The single source edit makes that zero contribution an Ada conditional
expression. All three original postcondition relations remain: nonnegative
result, exact predecessor recurrence, and equality to the independent prefix.
For a zero digit, the recurrence uses the identical integer value zero without
evaluating its irrelevant radix factor. For a nonzero digit its original
expression is unchanged. No input restriction, limit, imported assumption,
assertion policy, permission or public runtime function is changed.

JACKAL's `jackal-zero-product.json` records `0*x = 0` as status `exact`,
formal `false`. This is decidable polynomial identity over Q[x], outside the
Lean certificate chain; it does not establish Ada correctness or runtime success.

This is only the first narrow repair. The unchanged checked successor relation
also evaluates `Radix_Power` in loop invariants and private ghost helpers at
padded offsets. Large significant operands still exceed the installed model's
finite runtime representation. Neither problem is waived or relabeled solved.
Normalization and any model redesign require a separate proof design.

Required next evidence: root-serialized checked build; unchanged original
successor regression and exact source/library correspondence; original Ada
tests and fuzz; focused strict level-3 Resource_Quantities proof with retained
warnings/unproved/justified/Assume counts. Full Phase One proof/runtime,
retirement, authentic protected/actor evidence and independent F7 acceptance
remain open. No build, proof or test was run by this helper.
