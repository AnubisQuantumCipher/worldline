# Phase 1 autonomous decisions

All entries are internal engineering decisions. Independent acceptance is NOT PERFORMED.
A PENDING entry is a proposal, not an authorization to execute its dependent action.

## D0 — isolated source and delegated ownership

- Status: TESTED isolation; reviewer verdict APPROVE (actual GPT-6.1, scratch/reviewer/step0-review-approved.json).
- Options: shared checkout; isolated worktree at the user's frozen commit. Choice: isolated ext4 worktree `astra/phase1-blockers-20261013T165716Z` from `a1bda52b53a9a220b2333fe09a135e2d94127dbc`.
- Evidence: `git worktree add -b astra/phase1-blockers-20261013T165716Z /home/sicarii/Work/worldline-phase1-blockers-20261013T165716Z a1bda52`; `findmnt -T` reports ext4. Retained identity: `records/phase1-blockers/preflight/identity.txt`.
- Ownership: coordinator alone edits product, docs, scripts and commits. Acquisition agent owns `scratch/acquisition/`; analysis agent owns `scratch/old-analysis/`; GPT-6.1 internal reviewer owns `scratch/reviewer/`. Agents hand proposed patches back for coordinator application. Coordinator also drafts Step 0 because the available agent slots include the coordinator.
- Isolation exceptions are precisely the user-mandated new worktree Git registration, new branch, shared `~/.worldline-heavy.lock`, and transient systemd scopes. All task artifacts, temporary files and caches remain inside this worktree. No other checkout, branch, Cosmogony file, installed runtime or process is modified. No external vault pin, SIA note, or publication is written under this run's stricter isolation instruction.
- Reversal: stop only owned commands; retain evidence; do not remove this or any other worktree during the run. Revert this branch's later product commits individually if needed.

## D1 — heavy-job admission and containment

- Status: APPROVE product heavy by actual GPT-6.1 after contained negative self-tests; launcher SHA256 c3c7fcc84bb509668d0136606449486d1179d67d7c89bf68f6f5db79a4ece61a.
- Options: uncontained command; raise historical cap; bounded scope at unchanged cap. Choice: `scripts/phase1_heavy.py` launches `flock /home/sicarii/.worldline-heavy.lock` and checks `/proc/meminfo` only inside the lock. Require at least `14GiB` (conservative interpretation of requested `14GB`); otherwise release and retry after five minutes, recording each check.
- Every launched job has `systemd-run --user --scope`, `MemoryMax=8G`, `MemorySwapMax=0`, explicit wall deadline, RUSAGE_CHILDREN process peak RSS (GNU time unavailable), streamed stdout/stderr and cgroup samples. Solver invocations additionally require `--memlimit` and `--timeout`; level and full scope remain unchanged. Historical acquisition launcher explicitly used MemorySwapMax=0; acquisition copies and hashes identify that original setting in scratch/acquisition/historical-index-v1.json. The option remains explicit for faithful replay.
- Evidence: initial review rejected exit-code retry ambiguity and insufficient descendant cleanup; retained at scratch/reviewer/step0-review-draft.txt. Revised launcher requires an admission marker, independent supervisor samples, actual cap validation and positive terminal unit state before unlocking. Contained negative self-tests passed as recorded in records/phase1-blockers/launcher-verification.json; reviewer approved product heavy, old minimal probes and acquisition stage measurements. The original full-build baseline follows the unchanged scope under this authorization; no product guarantee is inferred from launcher tests. Launcher output is measurement, never proof of product correctness. A killed recorder can leave the final cgroup sample absent; absence stays UNKNOWN and requires external scope/journal corroboration.
- Reversal: cease using launcher, retain all logs; replace it only with a reviewer-approved launcher preserving or strengthening the same admission, scope and retention rules. Never raise the cap implicitly.

## D2 — acceptance gates bind

- Options: treat bounded checkpoints as completion; retain all original gates. Choice: exact gate roster in docs/phase1-acceptance.md.
- Evidence: GPT-6.1 reviewed SHA256 `5a76d01fb2688eed05ed5f347541fcd85a4087c412b2c3c1530f03b53ffec6c0`, APPROVE; artifact scratch/reviewer/step0-review-approved.json. Covers all four blockers and seven original areas.
- Reversal: gates cannot be removed or weakened; append correction/additional gates under review if an omission is found. Independent acceptance remains NOT PERFORMED.

D1 self-test repairs retained: launcher-exit75-v1 lacked user-bus environment; v2 and descendant-v1 found missing `/usr/bin/time`. No payload started in these failed attempts. Replaced the unavailable observer with Python RUSAGE_CHILDREN and retained cgroup aggregate samples; no host package installation. Exact terminal inactive scope records retained for v2/descendant-v1.

## D3 — native dependency layout without external artifact writes

- Status: APPROVE/CONCUR actual GPT-6.1 reviewer.
- Options: put native artifact outside this worktree (forbidden); change guard's outside-source rule (rejected); materialize immutable source inside an owned scratch frame. Choice: `git archive a1bda52` into `scratch/coordinator/acquisition-baseline/frame/source`, with sibling `frame/native-artifacts`. Preserve original native guard and all inputs. This layout also matches PrivateEvaluator's `package.parent/native-artifacts` lookup.
- Evidence: `records/phase1-blockers/preflight/source-inventory.json`; native/build_guard.py source placement rule and environment reset; runtime/worldline/linux/private_evaluator.py artifact resolution. Builder's /tmp will be bind-mounted to worktree-owned TMPDIR with bwrap, because its explicit environment clears TMPDIR. Fresh core/pending libraries will be copied from this run only, with hashes and commit/source joins. Build output is not proof.
- Reversal: cease using this scratch frame and retain it as evidence; create a new frame for a successor. Do not alter original source guard, old artifact directories or another session's builds.

## D4 — isolate imported SPARKlib after baseline violation

- Status: APPROVE/CONCUR actual GPT-6.1, conditional on private path resolution and read-only host guard.
- Failure: `gprbuild -p -P worldline.gpr -j2` in full-build-baseline-v1 emitted archive/index actions for installed SPARKlib. Installed `lib/gnat/sparklib_obj/sparklib.lexch` and `lib/gnat/sparklib_lib/libsparklib.a` had current-run timestamps. This violated the worktree-only instruction. The build returned 4 with `gprlib: no object files specified`. No retrospective isolation claim is made; user was informed. No shared-file restoration or further modification is authorized.
- Options: reuse writable installed project (rejected); silently ignore failure (rejected); private exact dependency source copy. Choice: copy original `sparklib.gpr`, `sparklib_common.gpr` and their relative `include/spark` tree into `scratch/coordinator/private-sparklib`, preserving source semantics and scenario choices. Set private GPR_PROJECT_PATH AFTER sourcing GNAT env, inspect resolution, and run future builds with host read-only and only this worktree writable where supported.
- Evidence: `records/phase1-blockers/full-build-baseline-v1/{stdout,stderr,result.jsonl}`; private source inventory and project resolution retained with successor build. Private dependency rebuild cannot erase historical violation or convert it to PASS.
- Reversal: stop using private prefix and retain it; any alternative must retain worktree output confinement. Never restore shared files during concurrent work.

## D5 — retirement gate remains FAILED-OPEN

- Status: APPROVE actual GPT-6.1 for mechanism-specific analysis publication and unchanged original FAILED-OPEN gate; independent acceptance NOT PERFORMED.
- Options: original automatic full-value/implicit-Old implementation; controlled owner; limited owner; borrowed observer; allocating fresh Old; named explicit prestate/manual release; unsupported blanket impossibility claim. Choice: retain original production contracts and mark O1 FAILED-OPEN after retained initial and corrected independent experiments. No narrowed production claim or new representation is adopted. The small explicit-prestate positive control is not a production substitute.
- Evidence: docs/old-retirement-analysis.md, scratch/old-analysis/evidence/handback-v2.json, scratch/reviewer/old-review-v1.md and old-review-v2.md with each exact command and source hash. Corrected controlled form builds but SPARK rejects controlled types; corrected fresh Old builds and proves value equality while the strict checker reports a leak. The original M4 ownership failure is separate. These exclude those mechanisms on the installed tools; universal impossibility remains UNVERIFIED.
- Reversal: retain failures, implement a concrete representation satisfying every original lifetime/value/exception/cost clause, add tests and full proof without new assumptions or bounds, and obtain fresh GPT-6.1 review. Continue independent authority work now; do not widen the proof boundary or claim manual cleanup closes automatic retirement.

## D6 — defer premature full proof to unblock Step 1

- Status: CONCUR actual GPT-6.1, scheduling only.
- Options: let a baseline full proof block all acquisition prerequisites; defer our owned proof and finish Step 1 first. Choice: stop only the scope named by full-proof-baseline-v1/scope.jsonl. It reached proof generation but has no complete report; retain all logs, caches and terminal records as NOT COMPLETED / COORDINATOR-DEFERRED. This is not an unproved-count result or a serious failed proof attempt.
- Evidence: retained full-proof-baseline-v1 stdout/cgroup/scope records; prerequisite pending/native/private builds were waiting on the same shared lock. Full proof remains required later on the frozen source at original scope and configured level with explicit unchanged solver bounds.
- Reversal: launch a fresh full run under a new evidence directory after acquisition prerequisites/repair. Do not overwrite the deferred attempt or treat its partial prover outcomes as final failures or successes.

D4 corrective guard preflight: private-v2 failed toolchain discovery before compilation because the read-only root also made `/dev/null` unwritable. `readonly-dev-probe.stderr` records Permission denied; a private `--dev /dev --proc /proc` namespace allows that probe while preserving a read-only host and worktree-only real filesystem output. Private-v3 uses those pseudo-filesystem mounts. No proof/build scope changed.

## D7 — local reproduction is diagnostic, not historical carrier acceptance

- Status: actual GPT-6.1 permits declared diagnostic adaptation with explicit non-equivalence; no A0/A2 acceptance credit authorized solely by this adapter.
- Options: execute historical carrier with old source paths/external mutations (forbidden); preserve original test target in a frozen worktree-owned frame and reviewed resource scope. Choice: `scratch/acquisition/run_local_diagnostic.sh SOURCE_COPY selected|full`, original selected testcase or full roster, unchanged MemoryMax=8G, swap=0 and original 1000s selected deadline, with current same-source artifacts. No prior library is imported as proof.
- Evidence: scratch/acquisition/LOCAL-DIAGNOSTIC-ENVIRONMENT.md, historical-v1/profile.json and original raw receipts. This adapter does not contain the historical external observer/admission/collector; results must name that difference. A measured local OOM can identify this payload's memory failure but not infer the earlier full-campaign timeout cause or complete missing historical custody/collector joins.
- Reversal: retain run; recover and qualify the original observer/carrier inside the isolation boundary before claiming exact historical carrier reproduction or full campaign acceptance. No weakened gate or hidden observer omission.

## D8 — bounded private ownership witness integration

- Status: APPROVE FOR EXPERIMENTAL PRODUCT INTEGRATION by actual GPT-6.1; A1/A2 full gates remain OPEN.
- Options: global JSON iterencode (rejected for changed accepted depth); public tagged streaming encoder (held: whole owned-copy peak still decoder-dominated and mutable caller contract unqualified); private detached-tree leaf-path witnesses. Choice: private `_owned` exact-builtin optimization only. It retains complete detached values and processes original codec witnesses per root-to-leaf path, retiring temporary encoded bytes before advancing. Original generic codecs and whole-root uncertain/hooked fallback remain.
- Evidence: scratch/acquisition/private-owned-v3.patch SHA256 cdf20ed0e2ebeadada2e156f5a6bfb8239848c2ced1838e96bfb6dc541cfd1c1, additive test SHA256 c7922c5daf4e34370fc2f4b866a832ef91db99179538a443c180de7259325264. Bounded original-depth comparisons and unchanged ownership controls plus actual-fast interruption controls are retained in scratch/acquisition/private-owned-controls-v3 and private-fast-interruptions-v3 outputs. Guarded fixed width30000 fixture measured peak ru_maxrss_kib52160 versus baseline163996; observed elapsed5.003101986003458s versus2.0016668980097165s. These are fixture measurements, not universal complexity or campaign claims.
- Additive regression threshold100000KiB is an explicitly chosen engineering bound for this exact fixture under Linux; it is not a new admitted-value limit and does not replace unchanged8G campaign cap. No original tests/guarantees removed. Runtime tradeoff must be tested against unchanged full campaign deadline.
- Reversal: revert only the private-witness implementation commit if actual original controls/campaign disqualify it; retain all experimental/failure evidence and additive regressions. Full acceptance remains open until actual-source full campaign, fault scope and evidence joins pass.

## D9 — measure the fresh fixture instead of inherited pre-exec RSS

- Status: CONCUR actual GPT-6.1 after independent exec-inheritance probe and corrected baseline/repaired observer results.
- Options: raise the regression bound (rejected); replace RUSAGE_SELF with approximate VmHWM (rejected); fork the measurement worker from its small post-exec launcher. Choice: fresh post-exec fork retains the identical fixture and `ru_maxrss_kib <= 100000` predicate and records both launcher and worker counters.
- Evidence: combined actual-product controls v1 failed at 164960 KiB; reviewer rss-observer-scope-v1 independently measured parent/fresh-exec child RUSAGE_SELF 209132 despite child VmHWM 13868 kB. Corrected identical fixture measured original baseline 158000 KiB (rejects bound), repaired 45928 KiB (satisfies bound), both under unchanged 8G, in scratch/acquisition/fresh-observer-{baseline,repaired}-v1. This corrects measurement scope; it does not enlarge the bound or establish whole-campaign boundedness. Exact observer SHA256 cfe84b2f4cbfeae3cb6b0d78d183551b97ce7bf87d3faaa0f50398692477164a.
- Reversal: revert only the added observer correction, retain original contaminated and corrected raw results. Any replacement must independently reject the original implementation on the same fixture and preserve the declared threshold.
