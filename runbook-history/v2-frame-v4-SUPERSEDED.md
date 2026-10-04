# First engineering proof iteration (scratch frame v4) - lead runbook, v2

v1 (preserved as RUNBOOK-first-proof-iteration.SUPERSEDED-v1.md) wrongly assumed a previous run's obj could be
cleaned to make the next run fit. CORRECTED (WORLDLINE monitor note, 2026-10-04): failed attempts and raw proof
evidence stay retained; nothing under RUNS (obj, proof outputs, attempts, dispatch records) is ever hand-deleted.
Capacity comes only from a live budget or from eligible inactive task-owned material reclaimed through
project-vault's exact-candidate full recovery comparison and guarded offload. Frame qualification/adoption
waives none of this.

## Paths
V4=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-frame-v4
WF=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-workflow-v1
LT=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-v2/tools
P=/home/sicarii/.claude/jobs/c9272506/tmp/p1

## Gate 0 - capacity budget (fresh, immediately before EVERY dispatch)
1. Live preflight: /usr/bin/python3 -B /home/sicarii/.codex/skills/project-vault/scripts/storage_status.py
   (observe local free, configured reserve, backup service state, pins, queue).
2. Budget with JACKAL (never by hand): margin = free - reserve - 2 x G, where G is the measured growth
   bound for the action and the second G is temporary full-restore space.
   - Full prove-all-k: G = 1121220323 bytes (measured F10K obj growth; JACKAL exact). At 17:2xZ:
     margin = -877420998 (JACKAL exact) -> NOT ESTABLISHED -> DEFERRED.
   - Single prove-file/prove-subp: pessimistic G = 543154002 bytes (F10K shared data_representation +
     all unit-level files + largest unit's subprogram outputs + all hash-named and session entries;
     JACKAL exact). At 17:2xZ margin = 278711644 (JACKAL exact) -> one unit run budgetable.
3. Dispatch only if the fresh margin is >= 0. Otherwise defer and continue source/design work.
4. After each run: measure the run directory's actual growth (du -sb of RUNS/<run>/source/obj and the
   attempt dir) and use the measured value, not the bound, for the next budget. Record the output paths.
5. Offload/reclaim: only eligible inactive task-owned material, only via `project-vault put EXACT_DIR --offload`
   (exact-candidate snapshot, full restore comparison, guarded retirement), only after a fresh successful
   backup/health check. The iPad backup failed with EIO at 2026-10-04 12:01 EDT and the backup service is
   failed, so offload is NOT currently available; an old receipt or a mounted path proves nothing.
   Unique source, proof evidence, compiler pins and tool identities stay local regardless.

## Steps (after QUALIFIED_ENGINEERING_SCRATCH_FRAME)
1. Adopt: /usr/bin/python3 -B $V4/scratch.py adopt $P/review-scratch-v4c/events.jsonl $P/review-scratch-v4c/argv.json
2. Materialize iteration 3 (14 core units from packets 01,02,04-11; ~32 MB measured for iter-2 materializations):
   /usr/bin/python3 -B $V4/scratch.py materialize iter3 $WF/overlays/iter-3-core
3. Gate 0, then ONE unit run (first choice: worldline-resources.adb, 45 drafted items):
   /usr/bin/python3 -B $V4/scratch.py dispatch iter3 prove-file worldline-resources.adb   (background)
   The task-owned output pin is taken by the frame (`project-vault pin RUNS/iter3`).
4. Answer the challenge: find the challenge line in <dispatch_dir>/run.stdout, then
   /usr/bin/python3 -B $LT/lead_jackal_answer.py show CHALLENGE_PATH
   -> actual MCP jackal_exact on the printed memory_expression -> save the verbatim text to <dispatch_dir>/mcp-1.txt
   /usr/bin/python3 -B $LT/lead_jackal_answer.py answer CHALLENGE_PATH <dispatch_dir>/mcp-1.txt <dispatch_dir>/receipt-1.json <dispatch_dir>/answer-1.json
5. After result.json: map diagnostics with $LT/diagnostic_map.py (SOURCE_DIR=RUNS/iter3/source,
   CHILD_STDERR=attempt child.stderr); move ledger items whose diagnostic is absent AND whose checks are proved to
   ENGINEERING_VERIFIED with evidence = attempt result.json + map. Then Gate 0 again before any further run.
