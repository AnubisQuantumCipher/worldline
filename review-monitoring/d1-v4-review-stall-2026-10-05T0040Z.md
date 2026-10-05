# D1 DESIGN v4 review: suspected stall (read-only observations; nothing interrupted)

**Status: the review is INCOMPLETE.** Corrected 2026-10-05 ~00:52Z at the supervisor's instruction. The first version
of this note (git history, commit `aaf3f87`) overstated the diagnosis. It said the batched calls "were never handed"
to the MCP client and that "JACKAL never received the calls". Those claims are withdrawn, and the corrected assessment
is below.

**Method.** Every observation was a read-only check of files or `/proc`:
- no process was signalled, interrupted or restarted;
- the reviewer's working directory was not touched;
- no arithmetic was substituted, and the review was not duplicated.

**Reviewer.** Actual `gpt-6.1-sol` with `max` effort, from the rollout's `turn_context`.
- Runner: `review_runner_v2.py` (sha256 `07cea533…`), pid 3218302, started by the lead's background task `b97kh4q33`.
- `codex exec`: pid 3218303.
- Thread: `01a1095e-6ffe-7690-8724-755b504108c5`, started ~00:02Z.
- Its own JACKAL chain: ledger proxy pid 3218484, `unshare` pid 3218540, server pid 3218622.

## Observations (as read; no inference)

1. **Event stream.** `review-records/live/review-d1-design-v4/events-1.jsonl` has 61 lines. It was last written at
   00:05:39Z and was unchanged at 00:39Z and again at 00:51Z. The last completed item, `item_30`, is a commentary
   message announcing a JACKAL replay of the draft arithmetic.
2. **Rollout.** `~/.codex/sessions/2026/10/04/rollout-2026-10-04T20-02-26-01a1095e-….jsonl` has 100 lines and was last
   written at 00:05:39Z.
   - Its last entries are a `custom_tool_call` named `exec`. Its input issues `Promise.allSettled` over the draft's
     `jackal_exact` calls through `tools.mcp__jackal__jackal_exact`.
   - A token-usage record follows. No tool output is recorded after it.
3. **Review directory.** `designs/claude-native-bigint-d1-design-v4/review/gpt61-v1` was empty at 00:51Z. No
   checkpoint had been written.
4. **Process wait states** (at ~00:39Z and ~00:51Z):

   | Process | pid | State |
   |---|---|---|
   | `codex exec` | 3218303 | `futex_do_wait` |
   | Ledger proxy | 3218484 | `anon_pipe_read`; its stdin is `pipe:[27177974]` from codex, and it writes to the server's stdin `pipe:[27177979]` |
   | JACKAL server | 3218622 | `ep_poll`; `/proc/…/syscall` showed 22 (`epoll_pwait`) |
   | Runner | 3218302 | `do_wait` |

5. **JACKAL ledger.** `~/.local/state/jackal/results.jsonl` is recall, not evidence. Since 00:05:34Z it shows one
   completed row, at 00:30:39Z, attributable to the package reviewer. It shows no row matching the draft's
   `jackal_exact` inputs.

## Corrected assessment

**Suspected tool-layer stall in the reviewer's `exec` batch.** The observations support it:
- the event stream and rollout have not changed since 00:05:39Z;
- the processes are in wait states;
- there are no completed ledger rows for the draft inputs.

**What they do not prove:**
- that the batch never reached JACKAL;
- the exact place it is stuck: the JavaScript runtime, codex's MCP client, the proxy or the server;
- that no call executed. The ledger is recall, so its silence is not evidence that nothing executed.

A wait state is a snapshot, not a trace.

**Effect.**
- The D1 v4 review is **INCOMPLETE**. No verdict, checkpoint or arithmetic result exists.
- D1 v4's closure claims, the findings F32/F34/F35/F36, and every original Phase One obligation and acceptance
  requirement stay OPEN.
- The stuck runner holds one of the three runner slots.

**Lead action.**
- The reviewer and its pending tool are left untouched.
- Any recovery that needs an interruption or restart is a human decision. The proposal is
  `review-monitoring/d1-v4-review-recovery-proposal.md`. It has not been performed.
