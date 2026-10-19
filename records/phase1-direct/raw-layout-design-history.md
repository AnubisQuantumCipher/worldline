# Retained raw wire decoding: layout and representation repair

Status: candidate implementation; no whole-system or Phase One acceptance claim.

## Defects and required behavior

The generic native C wire decoder reads fields using compiler layout attributes.
Flow analysis treated attributes of an uninitialized result as reads, while the
proof model lacked concrete C record offsets. Independently, endpoint testing
reproduced an overflow at the largest valid byte-array index because a slice end
added one before subtracting one. The original value-size precondition also
rejected nested native component images when C alignment added trailing padding.
All original values, layouts, inputs, and padding rejection requirements remain.

## Changes

Record and array representation clauses pin the layout reported by the installed
compiler before the change. Original fields, scalar types, field offsets, bit
sizes, alignments, value sizes and object sizes are preserved. A compiler JSON
comparison and a source comparison after removing only the new clauses are
retained under raw-layout-baseline-v1. This is evidence for this compiler/target,
not a claim of portable layout across every target.

Slice end offsets are grouped before addition to the physical first index,
avoiding an unrepresentable transient one-past-end index. The little-endian
primitive scans its native word width with a guard for shorter admitted input;
its result-width postcondition and signed conversion are independently proved.
No Relaxed_Initialization or initialization assumption remains on decoder results.

For the seven compiler types with different value and object sizes, Load and
Source_Padding_Valid admit exactly either size. This strengthens the operations'
input coverage while preserving every originally admitted input. No intermediate
length, oversized representation, or arbitrary truncation is authorized. The
record-padding validator continues to traverse every supplied byte and recursively
validate component padding; additional trailing object bytes must be zero.
Load only decodes full-range wire scalar fields and never grants authority.
Semantic validation and all existing caller authorization gates remain required.

## Evidence and limits

raw-id-runtime-baseline-v1 preserves the original maximum-index overflow.
raw-layout-runtime-v1 preserves the nested native-size precondition failure.
raw-layout-runtime-v2 completed the aggregate checked build, native comparisons
for every retained decoder schema at low and maximum indices, both value/object
representations, and every-byte single-mutation padding checks. Its test-only
Unchecked_Conversion independently interprets owned initialized native storage;
field equality identifies semantic bytes versus padding. The original Ada core
tests and fuzz run passed in the same job. Test-only conversion is not production
authority and is not formal proof.

The first strict proof attempt rejected Unreferenced annotations on parameters
still mentioned in layout attributes. Nine leaf validators now use an explicitly
initialized, constant, type-specific layout witness. Their Raw parameter remains
an overload witness and is truly unused. A mixed-type others aggregate was
rejected at compilation and replaced with named field initializers; both failed
attempts remain preserved. No warning category was disabled.

Whole-decoder strict no-inlining level-3 proof is being assessed separately.
Whole-project strict proof, complete runtime roster, full-domain successor repair,
implicit whole-value Old retirement, protected/actor evidence and independent
acceptance remain open. These local checks do not waive any of those obligations.

## Proof representation cost

raw-layout-proof-v3 reached the original 300-second deadline (exit 124). A live
process observation showed gnatwhy3 transforming the 70-field Raw_Observation
loader, consuming CPU and increasing memory before solver completion. This is
preserved as an incomplete proof, not a proved result or a solver counterexample.
The 52 record loaders now return one direct named aggregate rather than building
successive partial record states. The six fixed-array loaders are unchanged.
Every field, expression and order is checked against the pre-refactor source and
compiler field roster in aggregate-conversion.json. Attribute-only layout objects
supply static pinned offsets; their values are neither read nor returned. Formal
analysis must establish that no uninitialized value reaches a returned record.

## Negative length controls and exception boundaries

The production library is configured Library_Standalone => encapsulated. The
first added tests deliberately violated an Ada Load precondition across separate
Ada runtimes. A specific handler failed to catch the library exception; a broad
handler reached an unwinder abort. GDB traces preserve the exact precondition
entry and libgcc unwinder failure. Separate-process dynamic probes likewise
failed their required assertion-message oracle; these failures remain recorded.
They are not reclassified as passing refusals.

The new raw_decode_contracts.gpr tests the same source and checked objects in one
Ada runtime. Its separate-process controls require either successful decoding at
an original value/native object size or the exact decoder precondition assertion
for an invalid length. Crashes and other exceptions fail. All 188 controls passed.
The native-layout/padding tests also pass against the actual encapsulated library,
and 45 existing native integration controls passed; these are separate claims.
No cross-runtime Ada exception propagation guarantee is claimed or repaired.
The original C guards and exception-containment obligations remain required.

The original assurance runner now executes the native raw layout tests, builds
the single-runtime contract probe and runs its length controls. All existing
assurance steps remain. Hosted CI and full Phase One acceptance have not been run
or established by these additions.

The length-control fixture is checked against every current Load declaration and
its compiled-probe instantiation mapping. Empty, omitted and duplicate rosters
are negative controls and reject. The positive runs, field/padding comparisons,
length-refusal controls, strict proof and source comparisons retain distinct
scopes. None substitutes for the original full project acceptance chain.

## Shared total field-membership predicate

raw-aggregate-proof-v2 also reached its 900-second deadline, after progressing
through decoder and padding entities without an emitted counterexample. Padding
validators duplicated the same guarded subtraction 511 times. In_Field now
encapsulates that total comparison. Its postcondition states the exact original
predicate; it has no added precondition and handles zero Width and every Count
value. Every former expression passes its original offset, position and width.
This preserves the condition and lets its arithmetic be proved once. The full
unit and all padding controls must be checked again before claiming this version
verified. Original failed/timed-out attempts remain retained.
