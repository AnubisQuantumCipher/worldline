# Retained raw decoder: representation and verification repair

This is a nonfinal Phase One implementation checkpoint. Verification status is
recorded separately in the execution receipts and final summary; neither this
rationale nor a passing subset establishes Phase One acceptance.

## Required behavior and defects

Preserve every original wire field and scalar domain, native ABI, accepted value
image, padding rejection, caller authorization gate and original acceptance test.
The previous decoder had an observed maximum-index slice overflow, rejected some
nested native images because their alignment padding exceeded the value size,
and produced flow findings when querying layout attributes on partial records.

## Final implementation

Wire representation clauses pin the layouts actually reported by the compiler.
Field offsets, bit sizes, value sizes, object sizes and alignment are unchanged;
the baseline JSON, compiler comparison and original-source comparison are kept
in `raw-layout-baseline-v1`. This is evidence for the configured target/compiler,
not a portability claim for arbitrary targets.

Record loaders return complete named aggregates. Their fixed field boundaries
are derived from that same compiler-pinned layout. This removes unused dummy
record objects and partial record updates. `fixed-field-slices.json` records each
field's origin; native-layout tests independently compare the decoded fields to
the compiler's actual native representation. Fixed-array loaders retain their
original ranges. Slice-end offsets are grouped before addition to Data'First,
avoiding a transient one-past-end value at the maximum index.

For types whose value and object sizes differ, the precondition accepts exactly
either size. All originally admitted value images remain valid; arbitrary extra
lengths and partial extra padding are not admitted. Load interprets scalar fields
and grants no authority. Source_Padding_Valid examines all supplied padding bytes,
including trailing native object padding, and rejects nonzero padding.

In_Field is a total predicate over Byte_Count. Its postcondition states the exact
original guarded-subtraction comparison; no new precondition or size cap is
introduced. The extraction is mechanically reversible to the preceding source.
Outer padding scans are omitted only where compiler-pinned field extents cover
every byte of the record object. GNATprove had proved those rejection branches
unreachable. All nested padding-validation calls remain byte-for-byte unchanged.
The coverage and nested-call comparison are recorded in padding-warning-cleanup.json.
No warning category, assertion, ghost check, original proof floor or fixture is disabled.

## Verification design

The raw decoder test covers every declared Load schema at low and maximum array
indices, both value and native object sizes, zero/all-one and byte-position
patterns. Its test-only native conversion uses initialized owned value storage;
field equality supplies an independent compiler-layout oracle. Every byte is
mutated individually: a byte that changes no native field must be rejected as
padding. This includes inner-record and trailing-object padding.

Length controls run the same source in one Ada runtime and in separate processes.
They require successful decoding for each admitted size and the exact decoder
precondition assertion for invalid sizes. Crashes and other diagnostics fail.
The fixture must cover every Load declaration and match the probe instantiations;
empty, omitted and duplicate rosters are rejection controls.

The production library is encapsulated. Deliberately violating Ada preconditions
across separately owned Ada runtimes exposed exception-unwinding failures; the
traces and failed dynamic controls remain preserved. The single-runtime contract
controls do not establish cross-runtime exception propagation. Actual library
layout/padding tests and the existing C-interface/native integration controls are
separate evidence. Original C guards and exception containment remain required.

The existing assurance runner and its shared release roster now require the raw
layout test, contract-probe build and length controls. All original steps remain.
Local checks do not establish hosted CI success or independent acceptance.

## Preserved negative evidence

- `raw-id-runtime-baseline-v1`: original maximum-index overflow.
- `raw-layout-runtime-v1`: nested native-size precondition failure.
- `raw-layout-proof-v1` and `raw-final-flow-v1`: inappropriate unused-witness annotations rejected.
- `raw-layout-proof-v2`: mixed-type aggregate initialization rejected and corrected.
- `raw-layout-proof-v3`, `raw-aggregate-proof-v1/v2`: incomplete timed-out proof attempts.
- `raw-membership-proof-v1`: numerical obligations discharged, but strict run failed on unused-layout and unreachable-branch warnings.
- `raw-aggregate-runtime-v1/v2`, `raw-invalid-length-trace-v1/v2`, `raw-length-controls-v1`: cross-runtime exception-test failures, not passing refusals.

Whole-source strict proof, the original full runtime roster, full-domain successor
behavior, whole-value implicit Old retirement, protected and real actor evidence,
and independent F7 acceptance remain required. This repair does not waive them.
