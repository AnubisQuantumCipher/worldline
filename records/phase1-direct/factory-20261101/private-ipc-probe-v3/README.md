# Private IPC probe v3: final-counter retention repair

This is the single evidence-driven revision of the rejected IPC-DIAGNOSTIC-V2
preparation. V2, its rejected review, and all earlier execution failures remain
unchanged. Root owns integration and any future launch. This directory contains
source preparation and author-run pure synthetic tests only.

The only probe function changed from the exact v2 preimage is
`shm_mount_evidence`. For each proposed next retained prefix, it constructs a new
envelope with that prefix's FINAL retained/omitted counters and completeness flag,
then measures the actual sorted JSON encoding. It adopts the proposed envelope
only if it fits 2816 bytes (the unchanged3072-byte evidence limit minus256 for
the later opened-FD observation). On overflow the prior valid bounded envelope
remains untouched. Total candidate count, exact LF-joined candidate hash and
incompleteness survive, allowing the available mocked FD observation to be read
and retained before the existing explicit incompleteness refusal.

The exact27-row,3466-byte regression reproduces the v2 failure: final counters
25/15/10 produce2817 bytes, exceeding2816; evidence is not published and FD
observation is never reached. V3 retains14/25 candidates, marks11 omitted and
complete=false, measures2638 bytes before FD metadata, and preserves mocked
fdinfo/mnt_id before refusing. The new regression suite checks286 bounded
counter-width fixtures, including9/10 and99/100 candidate/omitted transitions
and9/10 retained transitions. Existing synthetic predicate, stacked-row, maximum
row-count/length, JSON escaping, oversized-ID and stdout-overflow cases also pass.

`complete` means bounded candidate/selected-ID retention only. It does not mean
descriptor-to-row correlation, safe topology, qualification or successful IPC.
A successor consumer must uniquely join the opened descriptor's mount ID to a
retained row before relying on that correlation. Synthetic unknown ID999 and
duplicate row ID cases explicitly remain UNPROVEN for that join; this patch
does not reject them or change the original selector/predicates.

All other probe functions and constants are AST-identical to v2, including the
first-longest/first-tie selector, every mount/identity/quota predicate, original
MAX_RESULT8192, evidence3072, result basename, semaphore and cleanup code. No
collector, guard, namespace/topology policy or original resource cap changed.
The inherited 32MiB/1024-inode output, separate restore,8MiB archive,4MiB receipts,
8GiB/swap0, storage ownership/admission and original deadlines still apply outside
this source. No mechanism qualification is inherited from historical execution.

Inherited caveats remain: result-file JSON is pretty-printed while stdout uses
compact JSON, so the result-file8192-byte check can refuse when compact stdout
fits. A result receipt may be written before the final tmp-directory descriptor
close; a later close failure can therefore leave an earlier result file that
does not represent terminal success. No result file may override nonzero tool
termination or replace final stdout, cleanup, archive and independent readback.
The compact overflow fallback remains FAILED and explicitly records discarded
mandatory fields and unknown cleanup. This revision repairs none of those
separate interpretation/lifecycle boundaries.

`source_tests.py` and `boundary_tests.py` are derived copies with the new exact
probe pin, v3 identity and a formation comparison against v2. Regression tests
load v2 definitions only to preserve the exact old defect; neither probe's main
is invoked. All mount/maps/fdinfo fixtures are synthetic and read_limited is
mocked; os.open is forbidden in the observation path. Real I/O is limited to
reading source and writing this directory's test receipts. No real FD, mount,
IPC, semaphore, socket, namespace, heavy job, compiler or prover observation ran.

Three author suites exited0 in1.431 seconds under one total60-second deadline,
with -B, -W error, PYTHONDONTWRITEBYTECODE=1 and PYTHONOPTIMIZE=0. These are tests,
not formal proof or independent review. Static checks observe only the intended
function delta; all functions in source/tests are at most41 lines. The directory
is hash-bound by manifest.json, not OS-immutable. Root must seal it externally,
commission fresh paired reviewers and a separate judge, and admit any later
actual diagnostic separately. No launch, production integration, proof credit,
Phase One gate or F7 acceptance is established here.
