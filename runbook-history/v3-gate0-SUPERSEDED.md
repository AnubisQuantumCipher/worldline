# First engineering proof iteration (scratch frame v5): lead runbook, v3

## History

- **v1** is preserved as `RUNBOOK-first-proof-iteration.SUPERSEDED-v1.md`. It wrongly assumed obj could be cleaned.
- **v2** is preserved as `RUNBOOK-first-proof-iteration.SUPERSEDED-v2-frame-v4.md`. It targeted frame v4, which
  actual gpt-6.1-sol left UNQUALIFIED with V4-B01..B04.
- **v3** targets frame v5, frozen with frame-inventory sha256 `c45720ef1f3e938b58a557387f6ddd32dc1db9839987b8dd691a21294dd5aa45`.

Standing rules, unchanged:
- Nothing under RUNS or any evidence directory is ever hand-deleted.
- Capacity comes only from a live budget, or from verified offload of eligible inactive task-owned material.
- Every review, including any pre-review, is actual gpt-6.1-sol through `review_runner_v2.py`.

## Paths

```
V5=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-frame-v5
WF=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-workflow-v1
LT=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-v2/tools
P=/home/sicarii/.claude/jobs/c9272506/tmp/p1
RUNS=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-runs-v5
```

## Gate 0: capacity budget (fresh, immediately before EVERY dispatch)

1. Run the live preflight: `/usr/bin/python3 -B /home/sicarii/.codex/skills/project-vault/scripts/storage_status.py`.
   It reports local free space, the configured reserve, backup service state, pins and the queue.
2. Compute the margin with JACKAL, never by hand: margin = free − reserve − 2 × G.
   - G is the measured growth bound for the action plus attempt records.
   - The second G is temporary full-restore space.
   - Use these bounds:

     | Action | G |
     |---|---|
     | Full `prove-all-k` | 1121220323 + 16000000 |
     | Single `prove-file` / `prove-subp` | 543154002 + 16000000 |

   - If the reviewer rejects v5's compact identity records, add 102818436 to G.
   - Example at 2026-10-04 ~18:30Z: free 11218264064. The unit-run margin was 81956060 (JACKAL exact, including the
     ~9 MB materialization).
3. Dispatch only if the fresh margin is ≥ 0. Otherwise defer and continue with source and design work.
4. After each run:
   - Measure the actual growth with `du -sb` of `RUNS/<run>/source/obj` and of the attempt directory.
   - Use the measured value, not the bound, for the next budget.
   - Record the output paths.
5. Offload and reclaim follow these rules:
   - Only eligible inactive task-owned material.
   - Only via `project-vault put EXACT_DIR --offload`.
   - Only after a fresh successful backup and health check.

   At 2026-10-04 the backup service is failed (iPad EIO), so offload is NOT available. This is operator package
   item S-1.

## Steps (only after QUALIFIED_ENGINEERING_SCRATCH_FRAME for v5)

1. **Adopt.**
   `/usr/bin/python3 -B $V5/scratch.py adopt $P/review-scratch-v5/events.jsonl $P/review-scratch-v5/argv.json`
   - Check first that the runner record directory holds `events.jsonl` and `argv.json`. Otherwise use the paths the
     runner actually wrote.
2. **Materialize iteration 3.** This is 14 core units from packets 01, 02 and 04–12. Candidate packet 13 is
   deliberately not included.
   `/usr/bin/python3 -B $V5/scratch.py materialize iter3 $WF/overlays/iter-3-core`
3. **Gate 0, then ONE unit run.** First choice is `worldline-resources.adb`, which has 45 drafted items.
   `/usr/bin/python3 -B $V5/scratch.py dispatch iter3 prove-file worldline-resources.adb` (run in the background)
   - `dispatch` prints its directory. `run-wait.json` and `terminal.json` there carry the actual run wait.
4. **Answer each challenge.**
   1. Read the challenge line in `<dispatch_dir>/run.stdout`.
   2. Run `/usr/bin/python3 -B $LT/lead_jackal_answer.py show CHALLENGE_PATH`.
   3. Call actual MCP `jackal_exact` on the printed `memory_expression`.
   4. Save the verbatim text to `<dispatch_dir>/mcp-N.txt`.
   5. Run `/usr/bin/python3 -B $LT/lead_jackal_answer.py answer CHALLENGE_PATH <dispatch_dir>/mcp-N.txt <dispatch_dir>/receipt-N.json <dispatch_dir>/answer-N.json`.
5. **After `result.json`.**
   1. Read `result.json`: `success`, `record_errors`, `launch_seal_drift`, `owned_terminal`.
   2. If `release-withheld.json` exists, the window is still reserved. Resolve it explicitly, never with a script.
   3. Map diagnostics with `$LT/diagnostic_map.py`, using SOURCE_DIR = `RUNS/iter3/source` and CHILD_STDERR = the
      attempt's `child.stderr`.
   4. Move a ledger item to ENGINEERING_VERIFIED only when its diagnostic is absent and its checks are proved. The
      evidence is the attempt's `result.json` plus the map.
   5. Run Gate 0 again before any further run.
