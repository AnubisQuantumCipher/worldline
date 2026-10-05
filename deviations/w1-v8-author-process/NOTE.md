# W-1 v8 drafting author: process record (preserved; disclosed)

**Who.** The W-1 drafting agent (`a6d9c9e22b6b98dc0`). The lead restarted it at ~15:54Z on 2026-10-05, after the
previous Claude Code session ended mid-task. It replied at ~16:17Z; the handback tool was unavailable in the new
session, so its report came as a reply.

**Its source.** The author's report and Appendix H of `proposal/ISOLATION-STORAGE-PROPOSAL-v8.md` (sha256
`804da95bed429aded004a433d9b43aa6f7fe94a9e94d66eda74d2a44ec4367a6`). Both are model output, recorded as stated.

## What the lead verified

All engineering only, not review.
- **Hashes.** Both files equal the report: v8 is 197628 bytes, and `v8-support/jackal.json` is `cdae49fc…`.
- **Change map.** All 124 §18.5 rows equal v7's unit bytes by sha256 and size: 45 C, 41 A, 38 R. JACKAL reproduces
  `45+41+38-124` = 0 and `124+7` = 131, both `exact`.
- **Form.** v8 is NOT one self-contained document. CARRIED and AMENDED units are hash-bound stubs over the v7 text,
  because the lead's v8 instruction asked it to carry unchanged v7 sections by hash. Some AMENDED units state
  superseding rules rather than exact old and new text, so a reviewer must read v7 alongside v8. This is flagged to the
  reviewer.

## Disclosures

1. **WebFetch.** The author used WebFetch to read upstream Linux v7.2 kernel source (commoncap, ptrace, pidfd, fs/proc)
   at about 15:23-15:30Z. That is an outside read, not a mutation. Whether the installed 7.2.6-1 build matches upstream
   is its premise P-KSRC.
2. **An automatically saved output.** One oversized read-only output was saved by the harness to the session
   tool-results directory, about 31 KB. The author did not write that file.
3. **Transcripts.** It reports never reading the lead's transcript.
4. **Not done.** No git and nothing privileged. Writes went only to the two paths, by Write/Edit.
5. **SIA.** One `sia.ask` at the start; no notes.
6. **Interruptions.** None.

## What this does not change

Nothing here grants or closes anything. V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION and W1-V7-HOLDER-STATE
stay OPEN by the author's own statement. Every W-1 item stays open until W-1's own independent actual gpt-6.1-sol review
rules.
