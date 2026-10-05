# Seam design v8: author notes

Process record of the drafting subagent (claude-opus-4-8, author role). This file binds nothing normative (RR8-6 applies the same rule to v7's notes). Every number here is observed.

## 1. Task

The lead's v8 brief: close the two required changes the sealed v7 review left — **V7R-H** (load-bearing: the V7-H.1 fix for the `rw/protected_root_worker.py:192` wedge was defective and silently dropped the native `p.quarantine` in the `owned is None` case) and **V7R-CITE** (imprecise line citations) — keep everything v7 closed, carry v7 by hash-pinned slices with quoted R8 replacements, re-run the stale-text sweep, and quote the exact before/after of the handler. v8 changes nothing else.

## 2. Inputs

- **Read in full:** the v7 review `D7R/REVIEW.md` and `D7R/review.json`; the lane handler `rw/protected_root_worker.py:186-205` and the router `rw/root_worker_endpoint_router.py:19-34`; `launch_reserved` (`rw/protected_scoped_resource_runtime.py:698-745`) and `rw/daemon.py:388-400` to confirm every corrected citation; the v7 design sections the R8s touch.
- **Hashed:** v1 … v7 designs, the v5/v6/v7 reviews, CAPI `APPENDIX-BINDINGS.md`/`DESIGN.md`, the lane source files, bound in Appendix B.
- **Not read:** every `gpt61-v*` directory (so CAPI5R/CAPI6R were not hashed — bound as recorded from D4); the v7 review's `raw-final-message.txt` and `review-records/`; `WT/packets/capi-pk0/`; `~/.local/share/sia/.gbrain/`; the lead's or any other agent's transcript. I read my own subagent transcript only to confirm prior deviations for §5.
- **SIA:** no call, no note in the v8 task.
- **Ada skills:** all eight were loaded earlier this session; Ada files read here: none new (the `.ads` identities are carried from v7's Appendix B and re-hashed).
- **JACKAL:** no call (no numeral derived); v7's J7-1/J7-2 carried.

## 3. V7R-H — the handler fix

The lane handler (`rw/protected_root_worker.py:191-199`) sets `self.phase='UNKNOWN_WORKER_OWNERSHIP'` at `:192` **before** the branch, and the `:195 elif self.phase=='UNKNOWN_WORKER_OWNERSHIP'` reads that just-set value — so today, in the `owned is None` case, the elif is always true and `p.quarantine` runs. v7 proposed "remove `:192`, the elif becomes a plain alternative, the handling is unchanged". The review correctly showed this drops the quarantine: with `:192` gone, in the `owned is None` case `self.phase` is still `'FRONT_OWNED'` (the failure precedes the launch), the elif is **False**, and `p.quarantine` is silently skipped — a changed native settlement; and "unchanged"/"plain alternative" is self-contradictory.

v8's fix (V8-H.1), with exact before/after in the design:
1. delete `:192`;
2. change the `:195 elif` to an unconditional `else:` — so `p.quarantine(operation,error)` runs in **every** `owned is None` failure, independent of any phase;
3. set the in-memory phase, after the settlement, from the committed custody phase via `committed_front_phase(operation)`, fail-closed to `UNKNOWN_WORKER_OWNERSHIP`.

The quarantine preservation (step 2) does **not** depend on the phase helper (step 3) or on the router row-3 successor change, which stays the OPEN unreviewed lane-code obligation it already was (the router `:29` today requires a *distinct* fresh front). The design states the handler **is** changed, minimally. R8-2 corrects the carried one-liner (R7-65's result). The native body, its proof and control V8-N.H are OPEN. verify.py confirms `p.quarantine` is in the sole `else` arm of the "after".

## 4. V7R-CITE — citation corrections

Each was verified against the lane source and corrected by quotation (nine R8 blocks; see V8-CITE and §B.2). All confirmed at the source line numbers:
- `rw/daemon.py`: `_send` def `:389`, comment `:390-393`, `is_closing` drop `:394-395` (R8-3).
- `rw/protected_scoped_resource_runtime.py`: `NEVER_DISPATCHED`/no-slot require `:705`, original-request require `:707-708`, journal load `:704` (R8-7); `from_mapping` `:729`, cgroup2 require `:730-731` (R8-8, R8-9); sandbox path `:732`, sandbox require `:733-735`, env loop begins `:736` (R8-6, R8-8).
- `rw/protected_root_resource.py:161` closes resource-state owners (R8-6); `rw/resource_child_execution.py:207` is the base `PARAMETERS` roster (R8-4); `C1:241` writes the init's pid (R8-1, R8-5).

None changes a conclusion.

## 5. Sweep

**Method.** `scratch/sweep.py` composes the reader-visible v8 text — the three carried v7 slices' live lines with the R8 substitutions applied, the superseded V7-H range dropped, plus v8's own sections and the R8 result lines — excluding the `v6:`/`v5:` old-text inside R-block fences (the composition drops those). It confirms each V7R-H/V7R-CITE target string is absent from the live text, and scans the live text for the stale classes of V7-M (capacity/stride, D-4a dependence, pidfd-only evidence, RC-10/11/12, oom-kill, "as in the original", the "unchanged" handler claim).

**Result (observed).** All eight targets RESOLVED. Residual class hits are each a kept class already accepted at the v7 review: capacity/stride *withdrawal* statements; D-4a *negations*; corrected "worker gone"/E-CR pidfd rows and the closure-barrier R1 statement (physical closure under closed 04.5); RC-13/14/15 rename-provenance and the inherited RC-01…12 required changes; and the V7-M sweep table's descriptions. The v6-and-earlier expansion is unchanged from v7 (already swept and accepted); v8 touches only 9 v7 lines, supersedes V7-H and adds v8 sections, so the sweep is scoped to those deltas, which is stated in Appendix C.

## 6. Deviations

1. **Read-only helper scripts under `scratch/`.** `scratch/verify.py` and `scratch/sweep.py` were written with the Write tool under the v8 directory (the brief permits "scratch under a scratch/ subdir of v8") and run as `python3 scratch/<name>.py`. They read files and the v8 document and print to standard output; they write nothing. They are part of the published file set under `scratch/` and are disclosed here. No command read standard input, and no file was created by a shell redirection.
2. No other deviation. Write/Edit only under `seam-design-v8/`; Bash read-only; `command ls`/`sha256sum`/`awk`/`sed`/`grep`/`python3 -c` only; nothing executed, imported, proved or measured; nothing under `/srv`; `.gbrain` never touched; `/home/sicarii`, `~/iPad`, `~/iPadBackup` never statted.

## 7. What I did not do

- I reviewed, accepted, closed and adopted nothing; OB-001 … OB-219 stay OPEN. "Closed at design level" is not acceptance.
- I added no refusal, cap, narrowed domain, retired control or approval gate, and no operator item. The handler edit preserves the original native settlement; it removes none.
- I did not change any v7 design conclusion; v8 is v7 plus the two corrections (the Map-against-v7 section is exhaustive).
- I ran no code, compiler, prover, test, service, `systemctl`, sudo, namespace, project-vault or restic.
- I did not interrupt, stop or time out any process, and started no background task.
