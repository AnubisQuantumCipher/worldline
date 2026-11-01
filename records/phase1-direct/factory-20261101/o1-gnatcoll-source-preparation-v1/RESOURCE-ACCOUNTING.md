# Finite source accounting and remaining resource evidence

This is symbolic normal-path accounting for two specified Pattern source objects,
not a whole-process allocation or byte proof. The lifecycle C01-C10 plus C10R
has 11 Compile, 10 nonempty Compile and 20 allocation operations. The unchanged
consumer's six-character LF & "From " elaboration adds 1 Compile, 1 nonempty and
2 allocation operations: combined 12 / 11 / 22, at most two Pattern source objects
and four designated blocks live. Lifecycle Free/Free returns only its contribution
to the post-elaboration baseline; persistent consumer storage is not claimed freed.

Payload at motif length <=6 is <=6 Character +7 Offset units per Pattern;
combined <=12 Character +14 Offset units excludes headers, alignment and allocator
metadata. Both Pattern records separately contain 256 Offset entries, two accesses,
a Boolean and padding. At most one Compile runs at once; its two temporary prefix
arrays contribute <=12 Offset units. Compiler-generated copies, temporaries and
intrinsic lowering remain unaccounted bytes until separately evidenced.

Caller buffers are exactly 47 and 23 Characters at library level, each below
128 bytes under the source's Character-unit model; actual storage units/type size
still require target readback. Consumer locals are one Box and one class-wide
Cursor at a time, plus five state Booleans total across sequential cases. No
Get_Message/parser invocation or custom factory callback is authored. Dispatch,
finalization and all transitive runtime/library allocations remain separate.

Oracle loops are <=10 starts *6 comparisons; lifecycle calls are ten explicit
Run_Case plus C10R. No recursion, input-driven loop or fixture task/process is
introduced. Explicit public API calls on the normal path are 44 lifecycle
(11 Compile+11 Search+22 Free), 12 consumer (2 Open+2 First+5 Has_Element+3 Next),
and 1 persistent-elaboration Compile =57, below100. This count excludes internal
library calls and compiler copies; it is not a total transitive call bound.

Results use counter ranges0..25 and0..16384 with a checked <=128-byte Emit;
integer formatting is bounded by Integer'Image, Boolean formatting fixed. Normal
25 rows are <2 KiB. New Python functions operate on <=16384-byte admitted input,
at most26 splits and25 comparisons; stdin reads once with a 16385-byte limit to
identify excess. External I/O may block, requiring the future admitted deadline.
The negative-control source constructs only two fixed <=25-row payloads.

Prospective unchanged invocation fail thresholds: one combined executable per
required clean profile, <=5seconds, <=64MiB memory, stdout/stderr <=16KiB each,
fixture metadata/results <=64KiB. These are UNMEASURED fail thresholds within the
unchanged8GiB/swap0 and shared1500/1590s envelope, not additional resources. Binaries,
objects/logs and controls must fit existing output/descendant admission ceilings.
This source package is capped2MiB/64descendants plus2MiB recovery margin; no offload,
archive, compiler, config generation, wrapper or integration operation occurs.

Separate required evidence includes actual target type/storage sizes; generated
stack/transient/allocator/runtime closure; intrinsic generic resolution, lowering,
pool and null-actual handling; canonical Depends/Post and actual assertion policy;
both designated allocations/releases and return to post-elaboration baseline.
Canonical Post plus -gnata alone does not establish an independently executed
intrinsic postcondition. Public completion cannot observe private nulling or release.
Unconstrained array data addresses may differ from allocation bases. Flat RSS and
exit zero cannot replace allocator-path evidence. No shim/debugger source is added.

The parent's read-only planner identified later candidate compiler/runtime anchors
(sem_ch12 intrinsic instances, exp_ch6 dispatch, exp_intr pools/guards/nulling,
s-memory C-free and possible s-pooloc path). These are navigation only in this
package, not hashed consumed runtime identities or executed evidence. Later exact
source/lowering/ALI/config/link and scoped observations must bind whichever paths
actually execute. Existing tool/runtime pins are immutable inputs here; their
presence does not prove selected configuration, matching, linking or actual calls.
