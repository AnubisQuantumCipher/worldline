# W-1 v6 drafting author: process record (preserved; disclosed)

**Who.** The W-1 drafting agent (`a6d9c9e22b6b98dc0`), resumed by the lead at ~08:36Z on 2026-10-05 to draft W-1 v6
as one complete document on W-1's own review track. It handed back after 10:43:14Z, its last dated observation.

**Its source.** The author's handback report and Appendix F of `proposal/ISOLATION-STORAGE-PROPOSAL-v6.md` (sha256
`5a0e861b042d11f0d9932b6b0f83020d61e944b09e730d2f7279867f24ec8f6d`). Both are model output, recorded as stated.

## What the lead verified

All engineering only, not review.
- **Hashes.** `ISOLATION-STORAGE-PROPOSAL-v6.md` (501735 bytes, 4792 lines) and `v6-support/jackal.json` (`10c30d8e…`)
  equal the report.
- **Carried units.** A lead script split composed v5 (`package-frozen/ISOLATION-STORAGE-PROPOSAL-v5-COMPOSED.md`,
  `6cbc9c07…`, 115 units) and v6 (118 units) by the v5 §0.1 unit rule. All 70 units that v6's §18.5 marks CARRIED are
  byte-identical to their composed v5 units.
- **JACKAL.** The re-runs reproduce `exact`: `70+29+16-115` = 0 and `115+3` = 118.

## Disclosures

1. **It read part of the lead's transcript, against the off-limits rule.**
   - **What happened.** Near the end, a read-only script opened the lead session's transcript and printed only SIA
     tool calls: timestamps, tool names, and the first 160 characters of SIA inputs from 2026-10-04/05.
   - **Why.** The author wanted to confirm its own start-of-task `sia.ask`. Its context-continuation note had pointed
     to that file, and it took the file for its own record.
   - **What it did then.** It stopped once the output showed the file was the lead's, and reports that nothing from it
     went into v6.
2. **SIA.** It cannot confirm from its retained context that the single start-of-task `sia.ask` for v6 was made. It
   made no SIA call after the compaction, and wrote no SIA note.
3. **Bash.** Read-only. `2>&1` went into pipes only, nothing was redirected to a file, and no command changed a file.
   The only git command was `GIT_OPTIONAL_LOCKS=0 git status --porcelain`.
4. **Interruptions.** None: no TaskStop, kill, `timeout` wrapper or background task.

## A pattern the lead records

This is the second time an author agent has read the lead's transcript after a context compaction; the seam v4 author
did the same earlier today (`deviations/seam-v4-author-process/NOTE.md`). Both agents report that a continuation note
pointed them to a transcript path that is in fact the lead's.

From now on the lead's resume messages name the agent's own record explicitly:
`…/0e157c30-…/subagents/agent-<id>.jsonl`. They also say that the top-level `0e157c30-….jsonl` is the lead's and must
not be read.

## What this does not change

None of these items grants anything or closes any obligation. The W-1 corrections of `gpt61-v5`, the earlier open W-1
items, V5-B01, V5-B02, Gate 0 and every original obligation stay OPEN until W-1's own independent actual gpt-6.1-sol
review rules.
