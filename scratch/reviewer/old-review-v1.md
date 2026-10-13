# Internal independent toolchain reproduction

Claim class: TESTED negative build/tool rejection; PROVED only explicit-prestate toy contracts as recorded. Independent acceptance NOT PERFORMED.

Command: `python3 scripts/phase1_heavy.py --out scratch/reviewer/old-independent-scope-v1 --timeout 30m -- bash -c 'source /home/sicarii/opt/gnat/env.sh && python3 scratch/reviewer/probe_driver.py scratch/reviewer/old-independent-results-v1'`.
Source and exact build/proof commands, versions, source hashes, return codes and timeouts retained in `old-independent-results-v1/results.json`. Scope admission, actual caps, cgroup memory and terminal state retained in `old-independent-scope-v1/`.

Observed on GNAT/GNATprove FSF16.1.0:
- Original M4 build succeeds; strict proof rejects `Items` as not writable.
- Limited whole-object Old fails language legality.
- Observer-return Old compiler emits GNAT BUG DETECTED Storage_Error; proof rejects access traversal Old separately.
- Controlled toy fails early-freezing E0003; this is not evidence of Controlled support impossibility until Elaborate_Body repair considered.
- Fresh owning Old toy fails potentially-unevaluated Old restriction; this is not evidence of unconditional fresh owning Old support impossibility.
- Explicit-prestate toy proof has11 checks, zero justified/unproved; standard instantiated deallocator body is skipped SPARK-Off. No full queue, automatic Old retirement, exceptional postcheck, runtime leak control or whole target proof established.

Verdict: O1 remains FAILED-OPEN. These mechanism-specific rejections do not establish universal infeasibility of the exact original conjunction. No precise full-value production restatement is accepted yet. Second legality-corrected controlled/fresh variants queued separately; failed originals retained.
