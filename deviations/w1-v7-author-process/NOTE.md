# W-1 v7 drafting author: process record (preserved; disclosed)

**Who.** The W-1 drafting agent (`a6d9c9e22b6b98dc0`), resumed by the lead at ~11:57Z on 2026-10-05 to draft W-1 v7 on
W-1's own review track. It handed back shortly after 14:01:10Z, its last dated observation.

**Its source.** The author's handback report and Appendix G of `proposal/ISOLATION-STORAGE-PROPOSAL-v7.md` (sha256
`8646f0fed3cf3f61dceb4fbf3a583f96f2bf7a0adce4986cb415789edeb82a7a`). Both are model output, recorded as stated.

## What the lead verified

All engineering only, not review.
- **Hashes.** `ISOLATION-STORAGE-PROPOSAL-v7.md` (501544 bytes, 4823 lines) and `v7-support/jackal.json` (`d62cca55…`)
  equal the report.
- **Carried units.** Splitting v6 (118 units) and v7 (124 units) by the unit rule, all 29 units that v7's §18.5 marks
  CARRIED are byte-identical to v6.
- **JACKAL.** The re-runs reproduce `exact`: J3, the Gate 0 allowance identity, = 0; J8 `29+63+26-118` = 0; J9
  `118+6` = 124.

## Disclosures

1. **`git status --short` ran once in the worktree at ~14:01Z without `GIT_OPTIONAL_LOCKS=0`.**
   - **The effect.** git may refresh its own index during status.
   - **Why it is harmless here.** wt-1 is the lead's isolation worktree, not a WORLDLINE managed root, so the
     PRIME-id trap does not apply. The output showed only the author's two new paths.
   - **Classification.** A minor deviation from the read-only intent, disclosed.
2. **Transcripts.** The author reports reading only its own transcript. The lead's resume message named its own record
   path explicitly.
3. **SIA.** One `sia.ask` earlier in the task, before its context compaction. No SIA note.
4. **Not done.** No scratch file, no privileged or mutating command, no compiler, prover or WORLDLINE code. Host
   observations are dated and read-only.
5. **Interruptions.** None.

## What this does not change

None of these items grants anything or closes any obligation. V5-B01, V5-B02 and W1-V5-PRESERVATION stay OPEN by the
author's own conclusion. Every W-1 correction stays open until W-1's own independent actual gpt-6.1-sol review rules.
