# C-API v5 drafting author: process record, one command slip, and an in-memory sketch run (preserved; disclosed)

**Who.** The C-API DESIGN v4 drafting agent (`a15cbfbc1dbf895f6`), resumed by the lead to draft DESIGN v5. It is an
author-role Claude subagent. Its handback arrived shortly before 04:13:55Z on 2026-10-05, when the lead first read
the v5 files.

**Its source.** The author's handback report, and `designs/claude-capi-boundary-design-v5/AUTHOR-NOTES.md` §4–§5 (sha256
`ed45d1db766f3b03ec946946942a571ae50b0eae21e339c5724b5e2480280e47`). Both are model output, recorded as stated. The lead
re-hashed the five v5 files: all five equal the hashes in the report.

## 1. One command slip

**What it reports.** One read-only Bash command began with `mkdir -p /dev/null 2>/dev/null;` before its read-only Python
script.

**Its account of the effect.** `/dev/null` already exists as a device, so `mkdir -p` could create nothing. The command
failed, and its error message went to `/dev/null`. No file or directory was created or changed.

**How it is classified.** A `mkdir` invocation and a redirection are both outside the read-only Bash rule given to the
author. It is a rule deviation. It is not a guard-refusal workaround, and it reached no protected path.

**What the lead verified.** The v5 directory holds exactly the five reported files, and `git status` of wt-1 shows no
other new path from this agent. The lead did not reconstruct the command, and its effect is recorded as the author
stated it.

## 2. Bash commands outside the literal list

The author used `head`, `tail`, `cut`, `awk`, `cat -n`, `printf`, `echo`, `cd`, shell `for` loops, `2>&1 |` pipes, and
Python passed through quoted heredocs. It reports that all of these were read-only and that no output was redirected to a
file. These are recorded as deviations from the literal list, like the same disclosure in v4.

## 3. The author's in-memory execution of the design's own check sketch

**What was run.** A read-only Python script reconstructed the v5 B8 sketch from v4 plus BR1–BR8. It then executed the
sketch's definitions in an in-memory namespace:
- `normalized_ada` was reimplemented;
- the predecessor `export_problems` was a stub;
- the successor texts were assembled in memory from S5 source text and the design's tiles;
- results were printed and not stored.

It reports 82 mutation runs, each refused by its named check, and clean results on the PK-1 and PK-7 texts. No WORLDLINE
module was imported, `proof_manifest.py` was read as text, and no file was written.

**The author asked the lead to judge it** against the brief's "do not import or execute WORLDLINE code".

**The lead's judgment** (lead reasoning, not a review):
- **Within the rule as written.** The executed code is the design's own proposal text and the author's reimplementation,
  not WORLDLINE code. The S5 Ada sources were read as text and never compiled or run. The lead's own frame-v6 self-checks,
  which also ran lead-written check scripts, are the precedent.
- **Classification.** It is an **author self-check**. It is not a review, not evidence, not a run of the manifest, and
  not one of the B12 mutation controls. Those controls remain unwritten and unrun as real controls, and v5 §18 says so.
- **What it shows, and what it does not.** It differs from v4, whose sketch was never executed. It makes v5's internal
  consistency claims more concrete. It establishes no acceptance, and the reviewer brief tells the reviewer not to rely on
  it.
- **No change for the reviewer.** The independent reviewer's brief keeps the passive limit: it does not execute the
  design's check sketches.

## 4. Its SIA omission

- **What it did.** One `sia.ask`, made late in the drafting, returned only `[model]`-origin notes. The author did not use
  them.
- **What it missed.** The instruction to ask at the *start* of substantive work was not followed in time, and the author
  records that as an omission.
- **What it did not do.** It wrote no SIA note, as its brief required.

## 5. Interruptions

The author reports none in v5: no TaskStop, kill or `timeout` wrapper, and no command hung. The v4 TaskStop event
(`ba0hhwegp`, 2026-10-05T01:22:20.621Z) stays recorded in `deviations/capi-v4-author-taskstop/NOTE.md`. v5 binds that
note at its current version (sha256 `f5dada7c3ea424b8f404571cf5cfeef0ad7b2eb4f6a07634c6fd481e18e5a88b`, 4889 bytes).

## 6. What this does not change

None of these items grants anything or closes any obligation. V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 stay NOT_CLOSED until
the independent actual gpt-6.1-sol review of v5 rules on them. Every proof, native, control and acceptance obligation
stays OPEN.
