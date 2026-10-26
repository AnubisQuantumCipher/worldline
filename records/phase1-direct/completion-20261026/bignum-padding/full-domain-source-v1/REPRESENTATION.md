# Full-domain arithmetic source proposal

This directory is an isolated, unbuilt proposal. `full_domain_columns.ads` and
`.adb` implement seven short, allocation-free functions with scalar contracts.
They are not a replacement standard runtime, a proof result, or a Phase One
acceptance claim. No production source, original contract, input domain or gate
was changed. The tmpfs reviews here have a separate operational scope.

## Exact finite failure and separate representation limits

The retained parent-executed counterexample has 805 little-endian bytes: byte
805 is one and all preceding bytes are zero. Its mathematical magnitude is
256^804 = 2^6432. This needs 202 base-2^32 limbs. Installed `s-genbig.adb`
1176-1195 rejects `X'Last - J > 200`, so 201 significant limbs are allowed and
202 are rejected. The recorded STORAGE_ERROR is a real significant-value
failure, independently of redundant high-zero padding. It does not establish
that every long operand fails.

Removing that guard alone leaves the distinct `s-shabig.ads` 23-bit `Length`
subtype and packed length/sign header. Its maximum is 8,388,607 32-bit limbs,
33,554,428 bytes. A value whose first nonzero byte is at offset 33,554,429
requires another limb. That second threshold is source-derived, not executed.
Length additions, the normalization one-past sentinel, and temporary arrays
also require review: addition allocates `Sum (0 .. X'Last)`; multiplication
allocates `Result (1 .. X.Len + Y.Len)`; division allocates several full vectors.

Installed `a-nbnbin.adb` `Adjust` deep-copies the whole `Bignum_Data`. Therefore
widening a header does not bound copies, implicit Old snapshots, stack vectors
or peak memory. No constant increase is proposed as a full-domain repair.

## Original domain and exact representation

Current `Resource_Quantities.Byte_Count` admits 0 through
`Long_Long_Integer'Last`; invalid spans return the specified zero/Invalid/False
outcomes, and empty or high-zero spans remain legal. `Power_Reference` is also
callable for every admitted exponent without a data span. A dense value for
256^N occupies N+1 bytes; its exact compact representation is a zero run of
length N followed by one. A run of N bytes 255 represents 256^N-1. These are full
values, not hashes, modular residues or fixed-word approximations.

The proposal uses little-endian runs whose length is an unsigned 64-bit count.
All original nonnegative signed-64 exponents convert exactly. `Power_256_Runs`
returns two fixed records and never evaluates N+1 in the original signed type.
This covers the original Power input range structurally. It does not make a
64-bit run length a sufficient general representation for every possible
sequence of arbitrary standard Big_Integer operations.

Arbitrary dense input cannot in general be compressed into constant space.
A complete backend therefore needs both compact uniform runs and immutable
dense pages. A candidate physical layout is an explicit sign plus a handle to
immutable, nonoverlapping little-endian segments: either a repeated-byte run
or a page of literal bytes, with wide logical offsets and a separately budgeted
physical page pool. A page index is an ownership-checked pool index, not an
unchecked raw pointer. High-zero removal must skip entire run segments and use
exact cached highest-nonzero metadata. A carry through a huge 255 run, and a
borrow through a huge zero run, must split a constant number of runs rather than
iterate over the logical run length.

`Add_Uniform` and `Subtract_Uniform` implement that narrow constant-size split:
the carry/borrow is a fixed point after the first column. The scalar assertions
are proof obligations, not assumed axioms. `Subtract_Three` gives the exact
Euclidean byte-column relation for Available-Withheld-Floor-Requested with
borrow in 0..3. The seven functions contain no loop, recursion, allocator,
pointer, imported assumption or disabled check. Their byte/range algebra and
run-length contracts still need compiler and GNATprove qualification. A proof
that run concatenation has the intended mathematical value also remains open.

## Necessary standard-runtime work, without a cap change

The smallest coherent backend change needs all of the following; the supplied
kernel implements only the scalar/run slice.

1. Replace the `System.Shared_Bignums` contiguous discriminant/vector storage
   and packed header with an exact segmented representation. Separate logical
   offsets from physically allocated page counts. Prove every offset/carry and
   allocation-size calculation; do not substitute a new numerical cap.
2. Replace `System.Generic_Bignums` normalization, add/subtract, multiply,
   compare and division workspace with iterative segment/page algorithms.
   Preserve the full standard API, sign/zero rules and specified exception
   contracts while repairing the observed finite-limit defect.
   The current automatic stack vectors cannot remain for large dense values.
   Exponentiation and GCD need iterative control flow as well.
3. Replace `Allocate_Bignum`, `Adjust` and `Finalize` coherently. Immutable
   payload sharing can preserve full value on copies/Old while retaining only
   a bounded owner handle per snapshot. It requires proved retain/release,
   reference-count bounds from the physical live-handle budget, no wrap,
   no mutation through aliases, and complete final release. Last-owner graph
   traversal needs a fixed bounded cursor stack or budgeted work queue, not
   recursive page cleanup. Failed constructors must leave no leaked owner.
4. Preserve the public `Big_Integer` value semantics and exact GNATprove
   mathematical interpretation. Do not mix binaries using the old pointee
   header with the replacement header. Identify and rebuild the complete
   private runtime dependency closure before any ABI or proof claim.

Keeping the public opaque address layout might avoid changing clients' public
object size, but does not by itself establish binary compatibility. Reusing
immutable pages is not yet an implemented or proved ownership mechanism here.
It also does not close the separate application Finalizable/implicit Old O1
tool-support obligation.

## Checked mathematical evaluators are an additional dependency

Current `Power_Reference` and `Prefix_Reference` are recursive executable ghost
definitions. The body additionally has recursive Prefix_Bounds,
Prefix_Monotone and Prefix_Padding, and loop invariants repeatedly call exact
prefix/power definitions. A backend-only repair leaves their input-dependent
stack and repeated scans. Even replacing a recursive reference with a linear
scan does not remove quadratic checked rescans from per-byte invariants.

A concrete Power route is an iterative exponentiation-by-squaring worker with
at most 63 exponent bits for the original domain, plus segment multiplication
that recognizes exact zero-run shifts. Preserve the original recurrence as a
proved functional property. A direct compact Power constructor is smaller but
needs a separately proved bridge to the same mathematical recurrence.

A Prefix route needs an exact immutable byte-span constructor/slice and an
incremental builder whose ownership and mathematical relation are proved.
Build one owned immutable payload; prefix snapshots can share its pages while
keeping an exact length. Caller-owned mutable bytes cannot simply be borrowed
and returned as an enduring full-value Big_Integer. Per-byte checked model
calls must use a bounded incremental witness or another verified proof
structure rather than reimporting all prior bytes on every iteration. The
original independent recurrence and public full-value equalities remain the
target. No suppressing assertions, Ghost Off, imported model assumption or
new input Pre is proposed. This bridge is not implemented by the supplied
column kernel and must not be advertised as solved.

## Memory acceptance and next finite experiment

An 8GiB acceptance bound must count original input, unique immutable dense
payload pages, run/directory metadata, live owner/Old handles, bounded operation
workspace, automatic-cleanup work space, and all other process memory. Shared
owners avoid multiplying dense payload bytes but do not make the first owned
snapshot free. The exact original accepted workload/resource envelope is still
needed to discharge that inequality. A private allocator refusal cannot silently
become a new public input limit or an accepted result for an original value.

The smallest next experiment is a strict isolated compile/proof of this seven
function kernel, full-unit coverage, zero justified/unproved checks, and checked
scalar boundary tests. Include zero-length runs, exponent zero and the original
maximum exponent without expanding runs, carry through 255, borrow through
zero, and the three-debit total -768. Use a deliberately wrong carry/borrow
mutant as a negative control. This establishes only the narrow kernel. Next
would be one budgeted immutable-page owner with copy/Old/cleanup negatives;
then a checked exact Prefix bridge and the 805-byte counterexample. Full
standard arithmetic, whole-domain resource acceptance, O1 and F7 remain open.
