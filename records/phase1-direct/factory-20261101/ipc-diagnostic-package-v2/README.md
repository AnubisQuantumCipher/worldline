# IPC diagnostic composition revision2: source-only repair

This is the sole permitted evidence-driven revision of IPC-DIAGNOSTIC-COMPOSITION
after D156 rejected revision1 on four synthetic counterexamples. The earlier
APPROVE report, adversarial rejection, judge, failed source and evidence remain
unchanged. No decision/execution history or review allowance is reset. Root must
commission fresh paired review and a separate judge for these exact bytes.

Only registered new ram_qualification_v6.py, ipc_diagnostic_guard_v3.py and this
directory were written. The v3 probe remains exactly8d7816d6...b16260. Existing
collectors/guards, product source, docs and continuation remain unchanged. Hashes,
patches, commands, failures and preimages are sealed in manifest.json.

## Four repairs and original operational boundaries

1. A retained mount row must contain printable ASCII only and exactly three fields
   after its mountinfo separator. Embedded LF/CR/VT/FF/tab and a space-appended
   second record are rejected before candidate hashing or FD correlation. Original
   selector/topology/mount predicates are unchanged. All candidates must still be
   retained before verifying the global hash or requiring a unique decimal FD-ID
   join. Incomplete evidence keeps only a declared, explicitly UNVERIFIED hash.
2. Copied stage/error fields are type/length checked (128/512 characters); tool
   fields are reduced to bounded scalar observations. Malformed input yields a
   bounded UNPROVEN summary instead of letting an oversized copied field escape.
   diagnostic_write contains ordinary diagnostic generation and receipt-I/O
   exceptions, returning explicit failure metadata so parent still attempts its
   mandatory result. Real I/O failure can also defeat that mandatory write; this
   is not hidden or guaranteed away. Cancellation/process failure is still the
   owned guard's responsibility.
3. Consumer archive processing no longer uses tarfile/getmembers. A local bounded
   single-gzip inflater feeds exact512-byte USTAR headers. Before expanding each
   member payload it rejects unsupported format/version/type/extensions, checksum,
   link/owner-name/device/reserved fields, noncanonical paths, duplicate/unlisted
   entries, inventory kind/metadata/size mismatch, entry excess and logical-size
   excess. GNU/PAX/symlink/hardlink entries are not accepted or skipped.
4. JSON parsing rejects duplicate keys, NaN/Infinity and finite-token overflow such
   as1e10000. Optional report equality compares canonical JSON encodings with
   type-sensitive numbers/booleans/containers, so integer3 and float3.0 differ.

Every original collector operational function except parent is AST-identical to
v4. Parent changes only fresh output identity and separately contained diagnostic
receipt metadata. Its terminal success expression and positive/negative checks
remain unchanged. Guardv3 is exactly four literal substitutions from the original
guard: JOB, LOG, fresh inner output and collector filename. It adds no source-pin
enforcement; root's pre/postlaunch exact source/tool/runtime readbacks remain
mandatory. All source/test functions are<=60 lines; collector maximum54.

## Bounded archive scan and metadata contract

Compressed input remains<=8MiB. Delivered logical file data remains<=32MiB and
member count remains<1024. Read/output requests are<=65536 bytes, compressed tails
are<=65536 bytes, headers512 bytes and selected captures<=8193/8192 bytes. zlib's
bounded inflater state is an explicit external implementation dependency, not a
proved Python/native-memory guarantee. No general tar-extension parser runs.

The independent expanded framing bound is34,612,224 bytes, derived as
32MiB +1023*(512-byte header +511-byte maximum file padding) +1024-byte end records
+10239-byte maximum final record padding. This permits existing USTAR framing; it
does not increase the32MiB payload or entry ceiling. Every file is hashed while
streamed and matched to inventory. Every header is checked against retain()'s
actual normalization: UID/GID0, empty uname/gname, preserved mode, mtime truncated
to seconds and directory trailing slash. Exact nanosecond metadata still belongs
to the original inventory/full-restoration comparison, not the USTAR timestamp.
Two zero end records and exact10240-byte record padding precede a checked single
gzip EOF; concatenated/trailing compressed data refuses. The compressed archive
hash/size is checked again against the streamed bytes. Missing inventory members
and unlisted archive members both refuse. Raw archives remain untouched.

Archived full stdout remains the observation source; optional result files cannot
override terminal failure. Pretty result JSON and compact stdout retain distinct
8192-byte checks, and a receipt can precede final tmp-FD close. Disagreement remains
UNPROVEN. A successful observational FD join never grants qualification. Even an
unexpected original nominal parent0 does not close the six-case mechanism gate.

Original retention/archive/restore, failure logs, socket rejection, cleanup, shared
lock,8GiB/swap0, post-lock14GiB,10GB reserve,+60MB/+30MB margins,32MiB/1024-inode
output and separate restoration,8MiB archive,4MiB receipts/outer metadata and512KiB
monitor log are unchanged. Tool/collector/wrapper/monitor remain180/220/240/270s.
No actual run or storage window is authorized by this package.

## Tests, preserved author failure and compatibility

Final exact-source tests pass all prior44 cases, four r1 counterexamples,13 scanner
controls, six row-delimiter/trailing-record controls, bounded-field/nonfinite-token
and optional-generation/receipt-I/O containment checks. The four old defects are
reproduced against preserved v5 definitions before checking v6. The unlisted33MiB
member now refuses after3584 expanded bytes, before expanding its payload. Tests
use bounded synthetic writers rather than allocating that payload all at once.

The original actual485-byte v4 archive and matching inside-result inventory were
read, hashed and passed through the new scanner. Its stdout hash remains
5cbae8de...a1752a and original FAILED/private-identity/private-shm-mount-mismatch
outcome is preserved. This is archive-consumer compatibility, not a new restore,
mount/FD/IPC observation or mechanism qualification.

One author test initially failed because its7996-byte regression fixture omitted
stdout's LF and was7995 bytes. Exact failed script and execution receipt are kept.
Only that fixture was corrected from the reviewer's actual tool recipe. Prior
passing candidate/source-test snapshots are also kept when row-boundary closure
was strengthened. Earlier receipts name those exact earlier source hashes;
final-tests.json binds the final collector. Snapshots are evidence, not additional
launchable candidates or permission to execute them.

All test execution used -B -W error, PYTHONOPTIMIZE=0 and
PYTHONDONTWRITEBYTECODE=1 under one aggregate60-second budget. Recorded elapsed
time includes the failed fixture attempt and final affected-source rerun. No live
parent/main/guard/sandbox, semaphore/socket, namespace/mount/FD observation,
compiler/proof, network or storage-management operation ran. Synthetic boundary
tests mock inside-receipt/stat/hash/open seams while exercising the actual bounded
scanner on in-memory archives; historical compatibility reads the existing archive
directly. Injected containment tests and AST ordering are not a formal proof of
whole-parent finalization. Author tests are not independent review.

## Next authorized step

Root seals the exact immutable review packet, commissions fresh paired reviewers
and a separate judge, and retains every r1 dissent/failure. Only after approval,
registration of all output/recovery overlap, explicit current storage-owner handoff
and fresh full admission may root consider the fixed nominal command with core0:

    PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -W error records/phase1-direct/factory-20261101/ipc_diagnostic_guard_v3.py

Fresh outputs are private-ipc-diagnostic-job-v3, ipc_diagnostic_guard_v3.jsonl and
completion-20261026/ram-qualification-ipc-probe-v6. Inherited dispatcher modes confer
no launch authority beyond this one separately admitted ipc-probe/normal run.
Required terminal raw/archive/source/host/cgroup/cleanup readbacks remain unchanged.
No universal parser, resource, Python, zlib, OS or whole-system proof is claimed.
Mechanism qualification, product integration, G0/A/O/C/F and F7 remain open.
