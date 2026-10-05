# C-API v6 drafting author: process record (preserved; disclosed)

**Who.** The C-API drafting agent (`a15cbfbc1dbf895f6`), resumed by the lead at ~05:07Z on 2026-10-05 to draft DESIGN
v6. It handed back at ~06:12Z.

**Its source.** The author's handback report and `designs/claude-capi-boundary-design-v6/AUTHOR-NOTES.md` (sha256
`414fd7363ed415ce5dd5c2f1c675780bb5917e9e9a08bc5ab0751ae48ba2aa08`). Both are model output, recorded as stated.

## What the lead verified

All engineering only, not review.
- **Files.** The five v6 hashes equal the report.
- **Carried slices.** A lead script recomputed 5/5 DESIGN slices and 14/14 A-BIND slices against the v5 bytes.
- **JACKAL.** J69 (`42+2` = 44) reproduces, status `exact`, formal=false.
- **Writes.** `git status` of wt-1 shows no new path attributable to this agent outside its directory.

## Disclosures

1. **`2>&1` into pipes, in nine read-only commands.** The author reports this as a deviation. In fact, the lead's
   resume message explicitly allowed `2>&1` into a pipe. No file was written. It is not a deviation from the lead's
   instruction.
2. **Commands outside the literal list.** One `ls` on an S5 subpath, `awk`, `cut`, `head`, `tail`, `sort`, `echo`, `cd`
   and quoted heredocs. All read-only by its account.
3. **Reading the lead session's transcript.** After a context compaction, the author read session transcripts
   read-only to recover state: first the lead session's file, then its own.
   - The lead's transcript contains summaries of other lanes. Depending on when it was read, that may include the seam
     v3 handback (with NF-1..NF-11) and the package v7 review results.
   - The author was asked not to read the seam v3 design directory or the package review in progress. By its account
     it read neither directory.
   - Reading the lead's transcript is not reading those directories. It is still an indirect path to their summaries.
   - It is disclosed so the independent reviewer can weigh any cross-lane influence. The only cross-lane input v6
     reports using is NF-5, which the lead relayed directly (L16).
4. **In-memory sketch execution, as in v5.** The design's own check sketch was executed in memory. The lead keeps the v5
   classification: an **author self-check**, not WORLDLINE code, not evidence and not a control run. The reviewer
   brief again forbids the reviewer to execute the sketch.
5. **SIA.** One `sia.ask` at the start, which corrects v5's omission. It returned only `[model]` notes, which were not
   used. No SIA note was written.
6. **Interruptions.** The author reports none: no TaskStop, kill or `timeout` wrapper, and nothing hung.

## What this does not change

None of these items grants anything or closes any obligation. V5-RC4-GATE-EXCEPTION, V5-RC4-QUAL-CAPTURE,
V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 stay NOT_CLOSED until the independent actual gpt-6.1-sol review of v6 rules on
them.
