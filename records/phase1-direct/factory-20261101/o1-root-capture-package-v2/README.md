D159 sole operational revision: prospective checked root capture

Runtime admission is NOT GRANTED. No actual guard/heavy/generator/build/proof/service,
lock, mount, archive, network, W/JOB or runtime root-control creation was performed.
The fixed operational entry, only AFTER independent review and fresh admission, is:

    /usr/bin/bash --noprofile --norc /home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/factory-20261101/o1-root-capture-package-v2/entry.sh

Do not run that command to review this packet. launch.sh accepts no arguments and has
one fixed unchanged D158 guard argv. entry.sh supplies the clean environment. Tools
and sources are pinned in tool-pins.json/input-references.json and MUST be rechecked
externally before launch. These scripts provide no admission, scheduling or authority.

Before launch, the sole owner must establish canonical checked ancestors, owner-only
custody, a fresh owner1000 mode0700 root at the fixed o1-xgen-root-control-v2 path,
no preexisting entries, and no hostile same-UID mutator. The launcher does not create
that directory. Noclobber + absent/non-symlink checks + FD/path regular/single-link/
mode600/owner1000 identities preopen status and four capture files BEFORE the guard.
A same-UID hostile race is outside that custody assumption, not prevented by Bash.
Entry-shell inherited descriptors beyond 0/1/2 must be excluded by launch admission.

Four complete files are required: stdout, stderr, stdout-consumer.stderr and
stderr-consumer.stderr. Each must retain the initially opened device/inode/mode/
owner/link identity and be empty for the expected successful guard. Their 8MiB
soft FSIZE cap is inherited; guard hard FSIZE stays unlimited. The two explicit
process substitutions immediately retain $!, close inherited writer FDs, and exec
native timeout1650s/kill-after5s + GNU tee --output-error=exit with NO FILE operands.
The guard duplicates the two writer FDs to 1/2 and closes all our extra writer and
regular-file FDs. Parent closes its writers and regular capture FDs, then waits BOTH
consumers regardless of previous failure. No set-e cleanup shortcut is used.

status contains guard/stdout_consumer/stderr_consumer typed WAIT_STATUS:n values.
NOT_STARTED is distinct from zero. WAIT_STATUS is Bash's encoding; >128 does not
claim to distinguish signal termination from an explicit numerical exit. The status
receipt is written through a THIRD checked native tee pipeline with both PIPESTATUS
values checked. This tee also has the1650s IO timeout and5s grace. Parent FD-close
commands are checked but are NOT claimed to detect every OS close errno; actual
capture/receipt data finalization is checked by tee's stdout write/fclose behavior.
The finite receipt is <1KiB; its postcheck bounds size below10000B. No fsync or power-
loss durability claim is made. Each receipt pipeline has its own IO deadline; this
is not a single1650s aggregate envelope. Original1500/1590 job/guard deadlines stay.

A persisted receipt saying capture_rejected=0 is insufficient: receipt close/write
may subsequently fail. External actual process exit0, three WAIT_STATUS:0 fields,
four complete empty regular captures, status identity/retention, source/tool checks,
and ALL unchanged terminal/resource/ownership gates are required jointly. Receipt
failure, missing/unparseable status, nonzero/signal exit, interruption, cap, delayed
EOF, or consumer failure rejects. Unknown cleanup remains UNKNOWN, forbids a
successor and requires reconciliation using original launcher identity. No bare-PID
kill or unconditional native cleanup is supplied or implied by these scripts.

Budget: four8MiB +1MiB metadata =33MiB, plus33MiB recovery, plus existing16MiB R,
plus unchanged14,050,918,400B original peak +10,000,000,000B reserve =24,136,901,632B
minimum available. Per-process FSIZE is not an aggregate quota/reservation. Current
capacity, post-lock memory, pins, bridge/vault custody, terminal ownership, and host
coredump resource policy are separate live admission dependencies. Tests did NOT set
RLIMIT_CORE=0; outside core artifacts are UNKNOWN. Do not infer storage safety from
a timeout 'dumped core' flag. No external cleanup was attempted.

Synthetic review evidence is retained, not rerunnable in place: the test runners
use exclusive output files. Review exact source-at-execution JSON, compile commands,
fixture.sh bytes and constrained replacement rosters in test-results.json and
final-test-results.json. Reproduce only under a separately authorized bounded fresh
owned root; NEVER source/run entry.sh or the operational guard for a synthetic test.
Test replacements are fixed guard body/root,1650s->0.4s,5s->0.1s, and a tee-only fault
wrapper. The final native diagnostic case's exact recipe is in evidence-audit.json.
LD_PRELOAD reaches only the final test tee, never timeout/Bash/guard/product. Native
libc write/fclose faults and an actual zero FSIZE diagnostic failure were tested;
this is not a claim that all hidden libc writes were intercepted.

All four attempt histories are retained.33 individual expected exit dispositions
were observed, but no failed harness is relabeled PASS. The two full-suite semantic
assertions and final diagnostic assertion failed due to fixture/oracle assumptions;
one intermediate strict compile failed. evidence-audit.json independently validates
only narrower retained properties. Details and remaining UNRUN boundaries are in
AUTHOR-REPORT.md. manifest.json inventories every payload, directory, FIFO and
symlink by type. Never hash/open the FIFO or dereference the retained /dev/full
symlink. The manifest excludes itself; its expected SHA must come from the external
writer-release message, not a self-attested file. No commits or pushes were made.

Required unresolved outer control before actual runtime: HARD+SOFT CORE0, verified
before this launcher and bound by root into the same revision2 review packet. FSIZE
hard must stay unlimited. This is a parent admission prerequisite, not a retroactive
claim about the retained synthetic tests, and is not yet qualified by this package.
