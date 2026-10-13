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
