# D1 DESIGN v4 review: preservation and recovery proposal (for a human decision; NOT performed)

Prepared by the lead on 2026-10-05 ~00:55Z. Nothing here has been done.
- The reviewer, its pending tool and its processes stay untouched until a human decides.
- No duplicate review is started, and no weaker arithmetic is substituted.
- Every original obligation and acceptance requirement stays OPEN under every option.

## Affected reviewer, session and processes

| Item | Identity |
|---|---|
| Review | Actual `gpt-6.1-sol` (`max`) review of D1 DESIGN v4. Brief `wt-1/briefs/d1-design-v4.md`; the live copy is `review-records/live/review-d1-design-v4/BRIEF.md` |
| Design under review | `wt-1/designs/claude-native-bigint-d1-design-v4/`, in the state at commit `e7bedee`: DESIGN.md `3c636847…`, decisions.json `ec2d120c…`, APPENDIX-A `8c8772d0…`, jackal.json `c3de17e7…`, AUTHOR-NOTES `68883c03…` |
| Runner | `work/claude-lead-v2/tools/review_runner_v2.py` (`07cea533…`), pid 3218302, under the lead's background task `b97kh4q33` |
| Codex | `codex exec` pid 3218303, thread `01a1095e-6ffe-7690-8724-755b504108c5` |
| Rollout | `~/.codex/sessions/2026/10/04/rollout-2026-10-04T20-02-26-01a1095e-6ffe-7690-8724-755b504108c5.jsonl` |
| Stream records | `review-records/live/review-d1-design-v4/{events-1.jsonl, stderr-1.txt}` |
| Review directory | `…/design-v4/review/gpt61-v1`, empty at 00:51Z |
| JACKAL chain | Proxy pid 3218484, `unshare` pid 3218540, server pid 3218622 |
| Runner slot | One of `MAX_CONCURRENT = 3` flock slots is held |

## Preservation, before any recovery (read-only copies; the originals stay in place)

1. **Copy the records**, each with its sha256, into `review-records/d1-v4-stall-preserved-<UTC>/`:
   - the rollout file;
   - `events-1.jsonl`;
   - `stderr-1.txt`;
   - `BRIEF.md`;
   - a listing of the review directory.
2. **Record the processes** read-only: `ps` for every pid above, plus each pid's `/proc/<pid>/{status,wchan,syscall}`
   and fd listing, with the time.
3. **Record the design files' hashes**, for comparison after any resume.
4. **Record the ledger tail** as recall only, not evidence.

## How the runner behaves (read from the code)

If the codex process exits non-zero, without a completed turn and without a `turn.failed` event, the runner treats it
as retryable. Termination by a signal is such an exit. The runner then:
- waits 120 s, doubling up to 1800 s;
- resumes **the same thread** with `codex exec resume`, using the same model (`gpt-6.1-sol`, `max`), the same provider
  settings and the same review directory;
- sends its fixed CONTINUE message, which says the interruption was "a transport or capacity failure".

## Options for the human (no recommendation is implied by the order)

| Option | Action | Consequence |
|---|---|---|
| R0 Leave as is (current) | none | The review stays INCOMPLETE and the runner slot stays held. If the stall is real, the runner may never finish |
| R1 Terminate only `codex` pid 3218303 (SIGTERM), after preservation | The runner resumes the same thread after 120 s; codex's JACKAL children end with it, and a new chain is spawned on resume | The resumed model could repeat the same batch and stall again: the CONTINUE text gives no guidance on the batch. Its wording ("transport or capacity failure") would not describe a deliberate termination accurately, and changing it would be a runner change needing its own review. The partial `exec` state is lost |
| R2 Terminate the runner and codex, then start a **fresh** actual gpt-6.1-sol review in a new directory (`…/review/gpt61-v2`), after preservation | A new thread from the start | That is a second review of the same design. The incomplete first review is preserved as INCOMPLETE, with its records, and earns no credit |

## Checks after any resume or restart (R1 or R2)

- **Model.** The rollout `turn_context` must show `gpt-6.1-sol` / `max`, the provider must be `openai-review`, and
  `different_from_author` must be true.
- **Thread.**
  - R1: the same thread id. `runner-terminal.json` must list each attempt with its argv and the sha256 of its event
    stream.
  - R2: a new thread id, with the old thread preserved.
- **Source binding.** The design files' sha256 must equal the values above, and the brief's sha256 must be unchanged.
  The reviewer must recompute and record those hashes.
- **Review artifacts.**
  - Checkpoints must be create-only.
  - The final `review-freeze.json` must verify against exactly REVIEW.md, review.json and checks.json.
  - The JACKAL results the review relies on must appear in its own checks, with status and `parsed=` values.
- **Acceptance.** No acceptance or closure credit flows from the incomplete first attempt.

**Decision needed from the human:** R0, R1 or R2, or another option.
