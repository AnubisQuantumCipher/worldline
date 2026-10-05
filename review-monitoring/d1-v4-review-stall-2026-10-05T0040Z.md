# D1 DESIGN v4 review: stall diagnosis (read-only; nothing interrupted)

**Context.** Recorded by the lead at 2026-10-05 ~00:40Z, at the supervisor's request. Every observation below was a
read-only check of files or `/proc`:
- no process was signalled, interrupted or restarted;
- the reviewer's working directory was not touched;
- no arithmetic was substituted, and the review was not duplicated.

**Reviewer.** Actual `gpt-6.1-sol`, runner `review_runner_v2.py` (pid 3218302), `codex exec` pid 3218303, thread
`01a1095e-6ffe-7690-8724-755b504108c5`, started ~00:02Z.

## Observations

1. **Event stream.** `review-records/live/review-d1-design-v4/events-1.jsonl` has 61 lines and was last written at
   00:05:39Z. The last completed item, `item_30`, is a commentary message: "I'm checking DR-C5's contracts for the same
   horizon hazard and replaying the draft arithmetic through JACKAL."
2. **Rollout.** `~/.codex/sessions/2026/10/04/rollout-2026-10-04T20-02-26-01a1095e-….jsonl` has 100 lines and was last
   written at 00:05:39Z.
   - Its last entries are a `custom_tool_call` named `exec`. That is the model's JavaScript tool, which runs
     `Promise.allSettled` over all draft `jackal_exact` calls concurrently, about 209 calls through
     `tools.mcp__jackal__jackal_exact`.
   - A token-usage record follows. No tool output follows.
3. **JACKAL ledger.** `~/.local/state/jackal/results.jsonl` is used here only as a liveness signal, not as evidence. It
   logs every MCP call that completes through any `jackal-mcp-ledger` proxy.
   - It has one row after 00:05:34Z: 00:30:39Z, which matches the package reviewer's `jackal-04.json`.
   - **None of the 208 distinct draft `jackal_exact` inputs appears.**
4. **Processes**, at ~00:39Z:

   | Process | pid | Observed state |
   |---|---|---|
   | `codex exec` | 3218303 | `futex_do_wait`, 0.2% CPU |
   | Its `jackal-mcp-ledger` proxy | 3218484 | `anon_pipe_read`. Its stdin is `pipe:[27177974]` from codex; it writes the server's stdin `pipe:[27177979]` |
   | JACKAL server | 3218622 | syscall 22, `epoll_pwait` with an infinite timeout, idle on its stdin `pipe:[27177979]` |

## Assessment

**BLOCKED, in the reviewer's own tool layer.**
- **What is waiting on what.** The JACKAL server is idle and waiting for input. The proxy has received no request from
  codex. So the batched calls were never handed from codex's `exec` JavaScript runtime to its MCP client. That is
  consistent with a stall in codex's tool bridge when about 209 concurrent MCP promises are issued.
- **Not a JACKAL refusal, and no partial result.** JACKAL never received the calls, so the replay produced no
  arithmetic in either direction. No result is to be inferred from the draft's own `jackal.json`.
- **No timeout to free it.** The runner's stream-idle limit (30 min) governs the model stream, not a pending tool. It
  is not known whether codex times out this tool.

**Effect on obligations.** The D1 v4 review is incomplete. Its arithmetic-replay check is unperformed. Every original
Phase One obligation, D1's V3-RC1..RC3 closure, and F32/F34/F35/F36 stay OPEN.

**Lead action.**
- None on the reviewer, per the instruction not to interrupt, restart or duplicate.
- The package re-review (pid 3129404) is progressing normally: `REVIEW.md` was written at 00:40:11Z, and its JACKAL
  calls completed.
- Restarting the reviewer, letting it resume, or abandoning it is left for the human or supervisor to decide.
