# First engineering proof iteration (scratch frame v5): lead runbook, v4.2

**v4.2.** This is v4.1 with observation O4 qualified, following the actual gpt-6.1-sol package review
(`wt-1/package-review/gpt61-v1`, PKG-FACTS). O4 is a limits-observation-to-wait proxy, not a target spawn-to-exit
duration. The allowance input stays 3632 s and is not lowered. Gate 0's formula and every allowance are unchanged. v4.1
is preserved as `runbook-history/v4.1-SUPERSEDED.md`.

**v4.1.** This is v4 with the "enforced bound" section corrected per the WORLDLINE monitor. Gate 0 itself is
unchanged.

**Frame blocker, independent of storage.** Actual gpt-6.1-sol left V5-B02 OPEN on frame v5. Frame mutations must stay
within the intended run tree. No unprivileged design meeting that criterion has been shown, so no frame is qualified
and no step below can start. See `frame-v6-PLAN.md`.

**Location.** This runbook is durable: it lives in the isolated worktree `work/claude-lead-isolation-v1/wt-1` (see
`ISOLATION.md`). The superseded versions sit in `runbook-history/`:

| Version | Why superseded |
|---|---|
| v1 | Wrongly assumed obj could be cleaned |
| v2 | Targeted frame v4, which actual gpt-6.1-sol left UNQUALIFIED |
| v3 | Gate 0 used past outputs as bounds |

**What the WORLDLINE monitor corrected in v3 (2026-10-04).** v3 called historical F10K output sizes and approximate
record sizes "growth bounds". It also said to "use the measured value, not the bound, for the next budget".

- A past observation does not bound the next changed-source run. JACKAL exact arithmetic does not validate that
  assumption.
- v4 therefore separates **observations** from **allowances**. An allowance is a judgment made explicit, with its
  justification stated.
- v4 adds every retained output, temporary full-restore space and ongoing agent/review growth above the unchanged
  reserve.
- **An allowance is never lowered because an earlier run used less.** An observation can only raise an allowance.
- If safe capacity cannot be established, dispatch stays deferred.

**Standing rules** (unchanged):
- Nothing under RUNS or any evidence directory is hand-deleted.
- Capacity comes only from a live budget, or from verified offload of eligible inactive task-owned material through
  project-vault's exact-candidate full recovery comparison.
- Every review, including any pre-review, is actual gpt-6.1-sol through `review_runner_v2.py`.
- Lead edits that would land in the guarded tree go to `wt-1`.

## Paths

```
V5=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-frame-v5
WF=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-workflow-v1   (read-only from now on)
WT=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1
LT=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-v2/tools
P=/home/sicarii/.claude/jobs/c9272506/tmp/p1
RUNS=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-runs-v5
```

## Gate 0: capacity (fresh, immediately before EVERY dispatch)

### Observations

Each value is as read from the named source.

| Id | Observation | Source |
|---|---|---|
| O1 | F10K full `prove-all-k` obj growth on unchanged commonV4: 1121220323 bytes | `du -sb` of `full-formal-diagnostic-v10k-retry1/source/obj` |
| O2 | One F10K identity-record set, observed per-file sizes: runtime closure 25492333, proof data 5582338, proof ELF 3198141, vendors 701976 | F10K evidence `*-before.json` |
| O3 | F10K `child.stderr` for the full `-k` run: 1170572 bytes | F10K evidence |
| O4 | F10K full `-k` run interval proxy: 3632 s, the difference of whole-second timestamp displays from `effective-limits-before.json` (14:54:38Z) to `child-wait.json` (15:55:10Z). The full-stamp interval is 3631279103/1000000 s. This interval runs from the limits observation to the wait record. It is not a separately recorded target spawn-to-exit duration. 3632 is kept as the allowance input and is not lowered to the finer value. | JACKAL exact, formal=false: parsed=`15*3600+55*60+10-(14*3600+54*60+38)` gives 3632; parsed=`15*3600+55*60+10+112498/1000000-(14*3600+54*60+38+833395/1000000)` gives 3631279103/1000000. Timestamps read from the F10K records. |
| O5 | Ambient free-space decline from 11289907200 at 17:58:11Z to 11188842496 at 18:44:45Z | `df` / `storage_status.py` |

O5 is a mean rate of 50532352/1397 bytes/s (JACKAL exact, formal=false). It includes this session's own self-checks
and reviews, which is the "ongoing agent/review growth".

**What these observations are not.** None of them is a bound on a changed-source run. O1 comes from different
source text, and O4 and O5 are single samples.

### Allowances

These are judgments, not bounds. Each has its justification, and each is to be reviewed.

| Id | Allowance | Value (bytes) | Justification |
|---|---|---|---|
| A_mat | Materialization: source copy plus overlay snapshot | 16777216 until measured | It is deterministic in base plus overlay. Once the run exists, replace it by its exact measured size, never by less. |
| A_obj | Generated output of one `prove-file` / `prove-subp` run on changed source | 2 × O1 = 2242440646 | JACKAL exact. There is no proven bound. The largest observation on this project is the whole-project unchanged-source run. A unit run is normally a subset of that, but changed sources add subprograms and VCs. The factor 2 is an explicit safety judgment. A full `prove-all-k` gets the same 2 × O1 judgment and is equally unproven. |
| A_rec | Every retained attempt record | 545393048 | JACKAL exact: 2 × 3 × O2-set (+ vendors) + 256 MiB + 64 MiB. Three identity sets (parent, child, after) are assumed in full form even though v5's compact form is under review, ×2. 256 MiB covers raw streams, about 200 × O3. 64 MiB covers the `gnatprove.out` copy and samples. |
| A_ambient | Agent/review growth during the run | 4 × O4 × 2 × O5-rate = 1468268019712/1397 | JACKAL exact. Frame v5 has no run timeout. 4 × the full-run duration is a duration judgment, and 2 × the observed rate is a rate judgment. Reviews and agents keep writing during a run. |
| R | Temporary full-restore space for everything the run retains | A_mat + A_obj + A_rec | The guarded-offload recovery comparison needs a full restored copy. |

### Rule

- **Required** = A_mat + A_obj + A_rec + A_ambient + R.
- **Dispatch only if** free − reserve − Required ≥ 0, computed with JACKAL from a fresh `storage_status.py` reading,
  with the configured reserve unchanged.
- **Otherwise** dispatch stays DEFERRED. Continue with source, design and review work, and keep operator package
  item S-1 open.
- **At 18:49Z on 2026-10-04:**
  - Required = 9304350902252/1397 bytes, about 6.66 GB (JACKAL exact, formal=false).
  - Free was 11185594368.
  - Margin = −7648075570156/1397, about −5.47 GB (JACKAL exact, formal=false).
  - Result: **NOT ESTABLISHED, DEFERRED.**

### After any run

1. Record its observed growth and retained sizes, with their paths.
2. Raise any allowance its observation exceeds. Never lower an allowance because a run used less.

### What would and would not change the allowances (corrected per the WORLDLINE monitor, 2026-10-04)

v4 claimed a runtime storage guard could become an enforced bound. That claim is withdrawn; v4 is preserved in
`runbook-history/v4-SUPERSEDED.md`.

- **A sampling monitor in the frame bounds nothing.** Periodic sampling plus a factor on the maximum observed write
  rate establishes neither the maximum future write rate nor the stop latency.
  - It cannot support a "never below the reserve" floor.
  - It never replaces or reduces A_obj.
  - It may be developed as additive defensive engineering: an extra, earlier stop condition, reviewed with frame v6.
- **The only candidate for an enforced limit** is an operator-provided, kernel-enforced quota or size-limited
  filesystem for RUNS, where writes beyond the limit fail.
  - It needs operator action and privileges.
  - It also needs its own reviewed, requirement-preserving admission argument before it may change this gate.
- **Until such an argument exists, this Gate 0 stays in force exactly as written.**

## Steps (only after QUALIFIED_ENGINEERING_SCRATCH_FRAME for v5 AND an established Gate 0)

1. **Adopt.**
   `/usr/bin/python3 -B $V5/scratch.py adopt $P/review-scratch-v5/events.jsonl $P/review-scratch-v5/argv.json`
   - Check first that the runner record holds both files.
2. **Materialize iteration 3.** Candidate packets 13 and 14 are not included.
   `/usr/bin/python3 -B $V5/scratch.py materialize iter3 $WF/overlays/iter-3-core`
   - Then replace A_mat by the exact `du -sb RUNS/iter3`.
3. **Gate 0 again, then ONE unit run** (first choice: `worldline-resources.adb`).
   `/usr/bin/python3 -B $V5/scratch.py dispatch iter3 prove-file worldline-resources.adb`
4. **Answer each challenge** with actual MCP `jackal_exact` through `$LT/lead_jackal_answer.py`, as in v3.
5. **Read `result.json`.** Resolve any `release-withheld.json` explicitly. Map diagnostics. Move ledger items only on
   absent diagnostics with proved checks. The ledger lineage now lives in `$WT`.
