# Author notes: root-worker seam design v4

Author: Claude Code lead claude-opus-5-5 (drafting subagent, author role). Date: 2026-10-05.

These notes go with `SEAM-DESIGN.md` v4 in this directory. They are the author's own account and review nothing. Nothing here closes or accepts anything, and every obligation stays OPEN. Aliases are those of SEAM-DESIGN §C.2.

## 1. What v4 does

- **Answers the sealed v3 review** (D3R, verdict ENDORSED_WITH_REQUIRED_CHANGES): V3-REQ-A … V3-REQ-L, RQ-1, every NOT_CLOSED or PARTIALLY_CLOSED clause, and every PARTIALLY_CLOSED ruling. Each change, gap, owner and evidence text is quoted verbatim (§A).
- **Carries exactly what the review closed or verified:** D-2b, RC-05, RC-10, the closed clauses, NF-1 … NF-11 with their assessments, N-1 … N-10, DF-1 … DF-6, OP-1 … OP-9 (with OP-7's range repair) and the review's clarifications (§A.6).
- **Carries v3 text by hash.** 24 v3 slices, bound by line range and sha256, with 64 quoted replacements R4-1 … R4-64. Six of the replacements target v2 lines that v3 carries (R4-45 … R4-49, R4-58). Superseded v3 text is mapped in §B.3.
- **Binds both sealed C-API reviews** (CAPI5R, CAPI6R) and composes root-worker stages with CAPI6's fixed WF-X protocol and (d1)–(d4) capture rules (V4-K).
- **New design:** typed consumer contracts and a corrected dependency graph (V4-A); one consistent set of witness laws with a residual audit, and the RQ-1 rollover mapping (V4-B); authenticity premises, anti-rollback limits, native number canonicality and one P3 definition (V4-C); a full-domain accounting matrix with no selection (V4-D); the child relation, exact surfaces, COMMIT_CHILD enforcement and an exhaustive authority inventory (V4-E); the complete custody relation and mutation gates (V4-F); release, closure, reconstruction seed and recovery routes (V4-G); armed intervals, reattachment and EOF rules (V4-H); non-circular requester joins, typed operands, per-gate contracts and RELAY (V4-I); startup union, initial authentication and migration (V4-J); a progress model (V4-L).

## 2. Process record

### 2.1 Writes and refusals

- Created with the Write tool, then changed only with the Edit tool, all in `WT/designs/claude-root-worker-seam-design-v4/`: `SEAM-DESIGN.md`, `jackal.json`, `AUTHOR-NOTES.md`, `seams.json`.
- No Write or Edit was refused. Nothing was written anywhere else.

### 2.2 Bash use (read-only), and one deviation

- **Forms used:** `sed -n`, `grep` (including `grep -c` and `grep -rn` over the lane source), `sha256sum`, `wc`, `cut`, `nl`, `fold`, `awk`, `cat`, `head`, `tail`, `command ls`, `ls -la` of my own record file's metadata, `df -h`, `cd` before a command, and Python scripts read from a quoted here-document on standard input. The scripts only read files and printed to standard output.
- **No output redirection** to any file. `2>&1` appeared only into a pipe.
- **Not run:** no compiler, prover, test, WORLDLINE, COSMOGONY or root-worker code (nothing imported or executed), service, `systemctl`, sudo, namespace, project-vault or restic. Nothing under `/srv`.
- **Not read:** `WT/packets/capi-pk0/`; `~/.local/share/sia/.gbrain/`. `/home/sicarii`, `~/iPad` and `~/iPadBackup` were never listed or statted.
- **Deviation (reported, not repeated).** To recover my own SIA truth-boundary line after context compaction, a read-only Python script scanned the session record file that the system named as this conversation's transcript (`~/.claude/projects/-home-sicarii/0e157c30-….jsonl`). It did not filter to my own entries. It printed a `grep -o` count of boundary-line strings, and then the last two `sia.ask` calls in the file with truncated results. Those two calls are dated 2026-10-04 and appear to be the lead's, not mine, so the file is, or contains, the lead's session record. I stopped reading it at once. Nothing from it is used anywhere in v4, and it was not read again.
- **The census behind AU-1** (V4-F.5): `grep -c "journal\.append("` over `rw/*.py`, printing the per-file counts of call sites. It was used only to motivate choke-point gating; no count is claimed in the design.

### 2.3 Author checks (self-checks, not review)

The final run of the read-only verification script printed (observed):
- every §B.1 slice hash equal to the v3 lines it names, with no overlap;
- every R4 quotation equal to the v3 or v2 lines it names, each inside its stated slice, no v2 target replaced by an R3, no line targeted twice, and R4-1 … R4-64 complete;
- each slice's declared replacement list equal to the replacements that target it;
- transitively, every C2 slice of v3 §B.1 against v2, every R3 quotation against v2, and every v1 slice of v2's Appendix C against v1: all matched;
- every quoted cell of §A equal to the sealed `review.json` field it quotes;
- every Markdown table row with its header's cell count, and every `V4-…` reference resolving to a heading;
- v3's Appendix B inputs: none changed.

The script is re-run after the last edit, and its result is reported in the handback.

### 2.4 Interruptions

None. No `TaskStop`, kill, timeout wrapper or background task was used.

### 2.5 Execution

None, beyond the read-only commands of §2.2.

### 2.6 JACKAL

No numeral was derived, so no call was made (`jackal.json`).

### 2.7 Skills

The eight Ada skills were loaded for this task and applied: `ada`, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`, `ada-2005-amendment`, `ada-high-integrity`. The SPARK User's Guide is release 28.0w documentation, not evidence about the installed toolchain.

### 2.8 Storage

`df -h` showed 9.3G available of 493G on the filesystem holding WT (observed), below the 10 GB reserve the lead mentioned. No storage action was taken: project-vault is outside this task's limits. v4 carries v3 by hash. Its design file is larger than v3's because of 64 quoted replacements (each quoting the old lines for verification) and the verbatim review quotations; its size is in the handback.

## 3. SIA

One `sia.ask` at the start of this task, as the lead required. Its detailed result is not in my working context after compaction, so I cannot quote its origin labels or its truth-boundary line here, and I do not borrow another session's line for it. Nothing from SIA is used as evidence. No SIA note was written.

## 4. Honest uncertainties

- **RC-5.** `Number_Canonical` relies on CPython's float rendering: the shortest round-trip digits and its notation thresholds. The example lexemes in V4-M (`1e16` refused, `1e+16` accepted, `-0.0` accepted) are my recollection of CPython, unverified here.
- **M8 (c).** Letting the front stop the root unit on an authorized `job.cancel` when no owner is reachable harmonizes with the original cancellation and `retain_and_stop_unknown`. It changes C2-93's UNKNOWN row (R4-49). The reviewer should judge whether this preserves 12.3; a stop settles nothing, and holds stay.
- **K-23** was added late: the claim that `kill` from the coordinator's PID namespace cannot reach outside it is kernel semantics, so it needed its own measurement item, and OP-7's range now runs to K-23.
- **RELAY.** Relay mode adds a relay channel and a per-gate re-read round trip. Its authentication rests on the custody channel the helper creates. Its cost and the exact frame format are unspecified.
- **Option G** is new and unselected. Its handler-metering gap is E's.
- **Escrow read copy.** Keeping a non-reading read-end copy of transferred output pipes (V4-H.3) is new. It is meant to make reclaim possible without affecting EOF (K-22).
- **The child sub-helper calling the native library** (V4-E.3) makes the C helper depend on the SPARK library's ABI. That is new native surface, unproved, with cost obligations.
- **The workload refusal on the root route.** V4-B.5 keeps the serial route's workload refusal on the root route until a reviewed dispatcher exists (C2-55 item 1). The lane's root route does not refuse workload operations today (NF4-1, NF4-2), so this restores the serial order rather than adding a refusal. The reviewer should confirm that reading.
- **Generation and sub-generation** are stored as SQLite `INTEGER`, as in v3's DDL and the v1 journal's rowid ordering. The native relation uses arbitrary-precision quantities. Whether the storage representation counts as a cap is for review.
- **QUEUED progress events** use a new event name on the original progress channel. They are optional and informational; whether clients tolerate an unknown event name is unverified.
- **L-RB-4's audit** covers the specifications listed in V4-B.1, not every called body.

## 5. Corrections made while drafting v4

- v3's E6 placed `Record_Launch_Intent` after HELD; the original commits it before dispatch (NF4-12). Fixed by R4-59 and R4-61.
- v3's DDL had no event kind for the transition to FRONT_OWNED (g+1) (NF4-13). Fixed by R4-29. The self-review also found that V4-F.2 first named that event obliquely; it now names `FRONT_OWNED (g+1)` and states that a request is queued durably before any transfer.
- My first cross-reference design for anti-rollback appended boundaries to the operation journal, which could conflict with that journal's state machine. It now uses observation events (V4-C.2).
- Wrong citations fixed before the final check: the raw-drain lines (`rw/protected_root_supervisor.py:251`, `:260-269`, `:268`), the quantity definitions (`core/resource_quantities.ads:13-17`, `:92-96`) and `Classify_Reference`'s first line (`:232`).
- The V4-J subsections were renumbered so that every reference resolves; a reference to a nonexistent V4-K.4 was corrected; five table rows with a missing cell were completed.
- R4 numbering was extended twice (R4-58 for W2, R4-59 … R4-64 for the child table), and every list that names them was updated.
- A sentence in V4-A.4 first said the root route already refuses workloads; it now cites the serial route and C2-55 item 1.

## 6. OPEN items

Everything in SEAM-DESIGN V4-O stays OPEN, together with v2's §18 list (C2-18 as amended) and every original obligation OB-001 … OB-219.
