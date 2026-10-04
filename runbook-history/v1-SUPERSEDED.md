# First engineering proof iteration (scratch frame v4) - lead runbook

Preconditions: v4 review = QUALIFIED_ENGINEERING_SCRATCH_FRAME (review dir work/claude-scratch-frame-v4/review/gpt61-v1);
runner record P/review-scratch-v4c has events.jsonl + argv.json + runner-terminal.json.

V4=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-frame-v4
WF=/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-workflow-v1
P=/home/sicarii/.claude/jobs/c9272506/tmp/p1

1. Adopt (fresh lead observation; validates review profile, rollout join, retained observation):
   /usr/bin/python3 -B $V4/scratch.py adopt $P/review-scratch-v4c/events.jsonl $P/review-scratch-v4c/argv.json
2. Materialize iteration 3 (packets 01,02,04-11 core units = 14 files):
   /usr/bin/python3 -B $V4/scratch.py materialize iter3 $WF/overlays/iter-3-core
3. Dispatch (background); its stdout prints dispatch_dir:
   /usr/bin/python3 -B $V4/scratch.py dispatch iter3 prove-all-k
4. Watch <dispatch_dir>/run.stdout for the challenge JSON line (challenge_path, memory_expression).
   python3 -B $P/../../../../Documents/.../claude-lead-v2/tools/lead_jackal_answer.py show CHALLENGE_PATH
   -> MCP jackal_exact(expression) -> save verbatim text to <dispatch_dir>/mcp-1.txt
   lead_jackal_answer.py answer CHALLENGE_PATH <dispatch_dir>/mcp-1.txt <dispatch_dir>/receipt-1.json <dispatch_dir>/answer-1.json
5. Expect ~1 h (F10K full -k took ~61 min). Output ~1.1 GB under RUNS/iter3/source/obj.
   Storage: free must stay > 10 GB reserve; only ONE full -k fits before cleanup of a previous run's obj.
6. After result.json: map diagnostics with claude-lead-v2/tools/diagnostic_map.py (SOURCE_DIR=RUNS/iter3/source,
   CHILD_STDERR=attempt child.stderr) and move ledger items whose diagnostic is absent AND whose checks are
   proved to ENGINEERING_VERIFIED (evidence = attempt result.json + map).
