D159 revision2 author report — source preparation only, independent verdict pending

Carrier HEAD observed before and after:7a3127281389f58f2291c86d123ec1f920cee6b7.
Owned writes were confined to this new package root. Sealed D158 manifest remains
561833c2cfed7979a2148ab0151329ee3c58752aacfa3586c5ddc0c17b0e541e; all40payloads
matched. scripts/phase1_heavy.py remains
c3c7fcc84bb509668d0136606449486d1179d67d7c89bf68f6f5db79a4ece61a.
No D158 source revisions; no original caps/flags/deadlines changed. Input identities
and requested author role are in input-references.json; no backend attestation exists.

The correction is independently checked pipe-to-file capture, not a new orchestrator.
launch.sh contains the fixed guard command, preopen/FD plumbing, explicit two-PID
waits, checked native receipt pipeline and empty-stream postconditions. entry.sh
retains the fixed clean env. Original native job deadlines1500/1590s are unchanged;
1650s+5s applies independently to each native IO consumer, including final receipt.
Three native tee invocations have no FILE operands. Four capture files are separate
from the native W/JOB roots. Parent closes every one of OUR extra descriptors; this
is not a promise to sanitize arbitrary unregistered caller-owned inherited FDs.

TESTED/OBSERVED: actual native GNU tee9.11 is used for first-write EIO and ENOSPC,
partial write then ENOSPC, empty-input stdout fclose/close EIO, both stream roles,
receipt first/partial/close failure, native FSIZE overflow and exact-boundary output,
consumer death, shortened delayed EOF, guard nonzero/signal, exclusive-creation
refusal for existing regular/FIFO/symlink targets, bad root mode, retained status
conflict, and guard extra-FD/soft8MiB/hard-unlimited checks. These are synthetic
compositions, not actual D158 native qualification. The LD_PRELOAD C fixture uses
POSIX dlsym function pointers only inside test tee; strict C11 warnings/Werror pass
on original and later corrected shim compiles. No install or product injection.
Bash syntax passes; shellcheck was unavailable (tool-pins.json). No formal proof.

Actual evidence commands and outcomes:
1. python3 -B run_tests.py:24expected individual dispositions, overall exit1.
   test-source-at-execution.json pins exact source. attempt-01.stdout/stderr and
   test-results.json retain commands/env/raw diagnostics/all fixtures. FAILED semantic
   assertion: lost_diag write() hook did not intercept glibc's diagnostic stdio, so
   diagnostic file retained43bytes. Native first-write/partial/close/cap controls are
   separate, successful observations; the suite itself remains FAILED.
2. python3 -B final_tests.py (first version retained as attempt-02-final_tests.py):
   strict compile rejected fwrite_unlocked macro expansion. Full compiler stderr and
   source pins retained in final-compile-command.json/final-source-at-execution.json.
   No test ran in this compile-failed attempt. This failure remains FAILED.
3. python3 -B final_tests.py (current):8targeted expected dispositions, overall exit1.
   final-03-source-at-execution.json and final-test-results.json pin source/fixtures.
   Imported diagnostic stdio hooks suppressed text but an inline libc newline remained.
   FAILED zero-diagnostic assertion; no claim all libc writes were intercepted. All
   native close/write controls still have their independently retained raw outcomes.
4. python3 -B final_diag_test.py:one materially different native kernel diagnostic
   control, overall exit1 due to an overstrict zero-file assertion. The tee-only shim
   installs FSIZE0 when inducing stdout EIO. Actual tee gets SIGXFSZ; wrapper consumer
   WAIT_STATUS:153 is retained, with guard0/other consumer0/external1. Timeout itself
   emits 'timeout: the monitored command dumped core' into its own still-writable
   diagnostic descriptor. That is observed capture, not a swallowed tee error. Its
   final-04-source-at-execution.json, final-04-compile-command.json, raw stdout/stderr,
   fixture and files remain; no final-test-results file was fabricated for this failed
   attempt. Final shim is fault.c/fault-diag.so. Older fault.so/fault-final.so and
   attempt sources remain. Not all controls were rerun with the final shim.

The read-only evidence audit PASSED narrower assertions, not the failed suites:
all32 prior raw exit dispositions and constrained recipes exactly reconstruct the
retained fixtures from unchanged launch.sh; the33rd kernel-diagnostic fixture recipe
is separately reconstructed. Every execution-time source pin resolves to retained
bytes, including failed C/test versions. Its actual native status153, timeout text
and failure are checked. The first audit selector probe failed on substring ambiguity;
that probe and its corrected exact-name check are reported, not hidden. This audit
reexecuted no producer/consumer. Execution commands/raw diagnostics are retained in
per-suite JSON plus public author tool transcript; external transcript provenance is
not claimed to be backend attestation.

Critical counterexample now OBSERVED: case-05/06 have guard WAIT_STATUS:0 and empty
stdout despite lost first write, but stdout consumer WAIT_STATUS:1 and external1.
case-08 has empty source stream yet close failure makes consumer1/external1.
case-101-final-receipt-close has all3 WAIT_STATUS:0 and capture_rejected=0 persisted,
but final receipt native close EIO produces external1. A receipt alone is not success.
case-13-consumer-death records stdout137 and stderr0, demonstrating the second wait
still occurs after first failure. case-14-delayed-eof records both124 under shortened
IO deadlines; this is not an actual1650s test or native descendant cleanup proof.

Power-of-Ten application (cross-language adaptations, not Holzmann quotations):
no recursion/goto, fixed2/4-entry resource loops and finite fixture lists; short Bash
functions (<60lines) and small C functions; explicit statuses and checked meaningful
returns; fixed guard argv, narrow FD capabilities and no shell eval; input/path/FD/
output validation; zero warnings on successful C compiles, failure retained. Bash,
GNU utilities, libc, kernel and Python test tooling are trusted boundaries, not
SPARK proof. Dynamic allocation/dispatch in OS/tools/fault-fixture is not falsely
represented as fixed-memory formally verified code. Critical authorization remains
in existing SPARK; this plumbing only refuses capture completion.

Authoring budgets:33 synthetic executions; sum recorded test/compile timings about
2.043s is a lower bound because failed drivers do not all record total completion.
Conservative aggregate observed tool wall <30s, below120s allowance. Each fixture
has7s outer timeout and0.4s IO deadline/0.1s grace; no further tests are running.
Final manifest includes full entry/type/byte counts, strictly under256entries and
8MiB source/reports +32MiB fixtures. Peak actual retained payload about17.4MB is also
below the32MiB fixture allowance alone;40MiB recovery was not consumed. No cleanup,
archive or offload was used to erase failures or create budget room.

UNPROVEN/UNRUN dependencies: real guard/bootstrap/heavy/worker/generator/native
build/proof; actual1650s deadline; actual source/runtime compatibility; terminal,
launcher/scope and full descendant cleanup; IPC; fresh storage/bridge/pin/memory
admission; fsync/power-loss durability; kernel/filesystem hangs and hostile same-UID
mutation. Parent Bash close return is checked but not a proved OS-close-error oracle.
Native data writer finalization is the tested tee boundary. Shell interruption yields
nonzero/UNKNOWN, and no successor is permitted without original-owner reconciliation.

RLIMIT_CORE=0 was NOT enforced in tests. Read-only shell reports unlimited core
and systemd-coredump pipe core_pattern. Actual host coredump activity or outside-owned
artifacts remain UNKNOWN; no query, cleanup or external write was performed. A core
flag or timeout text proves neither created artifact nor bounded storage. The parent
is separately assessing this real runtime-admission dependency. This author package
DOES NOT qualify the core/storage boundary and does not amend D158 or its budget.

Smallest sound next step: root validates this exact manifest/external SHA, then the
fresh nonauthor pair and separate judge review one immutable packet. Surviving
mandatory defects BLOCK; no revisions remain. Runtime requires fresh separate
admission including the core/storage dependency and all unchanged original gates.
No internal author approval, runtime admission, O1 qualification, Phase One acceptance
or F7 credit is claimed. F7 NOT PERFORMED. Writer release is issued only after seal
and exact readback in the external author message; this report is a manifest payload.

Pre-seal parent clarification: actual outer entry MUST independently install and
verify HARD+SOFT CORE0 before executing this unchanged sealed launcher, retaining
FSIZE hard unlimited. That outer control and its installed-handler semantics are
PENDING parent qualification and must be bound into the SAME D159 revision2 review
packet before fresh review. Nothing here claims prior tests ran with CORE0. Parent
reports sealed native children already set CORE(0,0); that parent observation is not
an additional author test. No late capture source changes or further IO runs occur.

Past-fixture provenance available without host queries: run_tests.execute records
cwd=BASE (this owned package), exact argv/env, relative elapsed seconds and the
case fixture path in every JSON record. Test runners did not explicitly retain tee
or timeout process PIDs or absolute UTC start/end timestamps; no values are invented.
The manifest retains filesystem mtime_ns as an observation, not execution-time
attestation. Existing raw stderr/receipts retain whatever signal/wait messages were
actually emitted. Root may separately reconcile scoped host metadata; core artifacts
and their full resource attribution remain UNKNOWN at this author seal.
