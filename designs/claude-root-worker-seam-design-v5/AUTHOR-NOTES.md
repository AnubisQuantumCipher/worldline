# Author notes: root-worker seam design v5

Process record, deviations, uncertainties and OPEN items for `SEAM-DESIGN.md` v5. These notes are the author's own record. They review, accept and close nothing.

## 1. Task and role

- **Task.** Draft root-worker seam design v5 answering the sealed actual gpt-6.1-sol review of v4 (`WT/designs/claude-root-worker-seam-design-v4/review/gpt61-v1/`), as the same author role: design only.
- **Role limits kept.** The author reviewed, accepted and closed nothing. No reviewer was spawned. Reviews in this lineage are actual GPT-6.1 only.
- **Inputs read first, in full:** `REVIEW.md` and `review.json` of the v4 review (every key, including `required_changes`, `required_change_detail`, `clause_detail`, `rulings`, `findings_assessment`, `findings_detail`, `rq1`, `rq1_window_assessment`, `carried_assessments`, `operator_items`, `open_obligations`, `open_design_dependencies`, `closure_amendment`). The freeze was checked against the three files it lists (equal).

## 2. Process record

**Reads.** The Read tool, and Bash used read-only: `sed -n`, `grep`, `sha256sum`, `wc`, `cut`, `nl`, `awk`, `command ls`, `test -e`, and Python scripts on standard input that read files and printed to standard output. No command redirected output to a file; no `mkdir`, `cp`, `mv`, `rm`, `tee`, `chmod` or `touch`. No git command was run.

**Writes.** Exactly four files, all in `WT/designs/claude-root-worker-seam-design-v5/`, created or changed only with the Write and Edit tools: `SEAM-DESIGN.md` (written in chunks with Write, then Edit appends at a temporary `@@CONTINUE@@` marker that the last chunk removed; the verification confirms the marker is absent), `jackal.json`, `AUTHOR-NOTES.md`, `seams.json`. A system note that offered Bash for file changes was not used; the task's Write/Edit-only rule governs.

**Not run.** No compiler, prover, test, WORLDLINE, COSMOGONY or root-worker code (nothing imported or executed), service, `systemctl`, sudo, namespace, project-vault or restic. Nothing under `/srv`.

**Not read.** `WT/packets/capi-pk0/`; `~/.local/share/sia/.gbrain/`; the lead's top-level session transcript (`…/0e157c30-….jsonl`), not even partly. `/home/sicarii` itself, `~/iPad` and `~/iPadBackup` were not listed or stat'ed. The lane draft was read and not changed.

**No interruption.** No TaskStop, `kill`, `timeout` wrapper or background task was used. Every command ran in the foreground to completion. No agent was spawned.

**Verification (final run, observed output).** A read-only Python script read the v2, v3 and v4 designs, the sealed v4 review and v5 `SEAM-DESIGN.md`, and printed:
- v4 `SEAM-DESIGN.md` sha256 prefix `f65629cb45e6`, 1911 lines;
- 14 C4 slices, every hash equal to the stated lines' hash; no overlap; every v4 line covered by a slice or a superseded range, or empty or `---`;
- 17 R5 blocks, numbered R5-1 … R5-17 in order; every quoted `v4:` or `v3:` text equal to the stated lines; every target inside its stated C4 slice or (for v3) its C3 slice as v4's §B.1 states it; no v3 target replaced by an R4; no line targeted twice;
- W5-1 inside C2-62 (v2 970-1010) with v2 line 1003 empty and 1004 starting "Invariants of the relation."; W5-2 equal to C3-VF5 (v3 1299-1374);
- 62 table-cell quotations in §A, each equal to a string of `review.json`; every V4-REQ change, every V3-REQ remaining gap, all 31 non-closed clause gaps (with their status), and the owner, evidence and gap of all 12 PARTIALLY_CLOSED rulings found verbatim; the D-2b owner and evidence, the OP-7 reservation text and the ten `open_design_dependencies` found verbatim; every NF4 status equal to `findings_detail[].status` and to the prefix of `findings_assessment`; every NF, N and DF assessment and the frontier sha256 present;
- every markdown table row with its header's cell count (pipes inside backticks ignored);
- every `V5-X.n` reference resolving to a heading (three resolve to combined headings: "V5-B.2 … V5-B.4", "V5-G.2, V5-G.3", "V5-H.5, V5-H.6").
- Final problems: 0 (after fixing, during drafting, one clause quotation taken from `REVIEW.md` instead of `review.json` (03.3), and two partial quotations of the OP-7 reservation).

**Citation spot checks.** Newly cited source lines were printed and compared while drafting; corrections made: `intent_for_operation` is at `rw/protected_scoped_resource_runtime.py:382` (its gate at `:386`); the CAPI5 owning-unit check is at `APPENDIX-BINDINGS.md:366-367` and the "`Decide` is in both tables" note at `:193`; `rw/chain_authority.py:58-73`; the original scoped launch's failure branch (`:770-776`) records UNKNOWN and stops nothing, which made the WL W3 row state the root launch's stop as a difference.

**JACKAL transcription cross-check.** After writing `jackal.json`, its four exact values were compared with the JACKAL ledger (`~/.local/state/jackal/results.jsonl`) only to catch transcription errors: the two integer results are equal in full; the two rational results match the ledger's stored prefix (the ledger truncates long outputs). The ledger is recall, not evidence, and is cited nowhere as a source; the values come from the tool results themselves.

## 3. SIA

One `sia.ask` at the start of this task, about prior work, decisions, failures and constraints for the root-worker seam design. Its truth-boundary line, verbatim: "boundary: senses live · chains pass · graph complete · 6 span(s) redacted at ingest · semantic recall · associative rerank off by measured default; retrieval.associative_rerank enables it · absence of recall ≠ evidence of absence". The results were `[model]`-origin agent notes; none was used as evidence, and absence of recall was not treated as evidence of absence. No `sia.note` was written (the task forbids notes).

## 4. Skills

The eight Ada skills were loaded for this task: `ada`, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`, `ada-2005-amendment`, `ada-high-integrity`. They shaped the SPARK statements (contracts stated, proofs OPEN; no `pragma Assume`; Stone … Platinum not claimed; native cost and representability left OPEN, with no domain cap). The SPARK User's Guide is release 28.0w documentation, not evidence about the installed toolchain.

## 5. JACKAL

Four derived numerals, one group of four `jackal_exact` calls, all `exact`, lane `rat`, `formal=false` (J5-1 … J5-4; `jackal.json`; design Appendix A). No other numeral in v5 was derived: line numbers, counts, sizes and hashes are observed. The author's own arithmetic was not used. One sum that would have been derived ("L + 8 bytes") was rewritten as words instead.

## 6. Deviations

- **None in the v5 work** against the hard limits, as far as the author knows.
- **Context compaction.** The conversation was compacted once during this task. The author continued from its own summary and re-read the review, v4 and the source as needed; the lead's transcript was not read.
- **Carried from v4 (disclosed then, recorded by the reviewer in `WT/deviations/seam-v4-author-process/NOTE.md`):** during v4 the author read the lead's top-level transcript. That did not recur.

## 7. Uncertainties for the reviewer

1. **IP routing (V5-B.5).** The lane routes every non-owner operation to the root route when a root worker is attached; v5 routes only the workload set there and serves every other operation on the serial route in the store-custody owner. The author reads this as restoring the original serial behaviour for those operations, but it changes the lane's routing, which the reviewer should judge.
2. **M8 (c) withdrawn (V5-F.5).** The author found no way for a process without store custody to reproduce `job.cancel`'s store reads, cancelled-set and response, so the front stop is withdrawn rather than repaired, and progress rests on the reattach endpoint. A worker that never completes a reattach is a stated non-equivalence.
3. **`CUSTODY_RETURNED` (V5-F.2)** rests on K-24 (PID-namespace teardown before the init pidfd reports terminal) and on the worker never passing a custody descriptor to another process (an audit, AU-1 class). If K-24 fails, the row's evidence is insufficient.
4. **RELAY transport loss (V5-I.5)** maps to the exception of a closed client connection (RC-10). This is the author's reading of what a daemon crash does to a request in the original.
5. **Option H (V5-D)** is offered with undesigned deltas D-H1 … D-H5; the AO-8 and AO-11 "part" entries are the author's judgement.
6. **`Number_Canonical` constants** (V5-C.3) are recalled IEEE and CPython behaviour, not read from installed source; RC-5 must confirm them.
7. **SQLite semantics** for the new DDL (NULL foreign-key child, BLOB `substr` and comparisons) are RC-7.
8. **K-range repair.** K-24 … K-27 extend OP-7's listed range the way v4's R4-1 and R4-5 did; the reviewer assessed v4's repair as completed and should assess this one.

## 8. OPEN items

V5-O of the design lists everything OPEN; V4-O (carried) and v2 §18 (carried) remain. In short: every original obligation OB-001 … OB-219; every required change, clause and ruling not CLOSED_AT_DESIGN_LEVEL; CG-1; all new statements and native bodies; P-A1 … P-A4; the accounting decision (D-4a); K-1 … K-27 and RC-1 … RC-7, RC-9, RC-10; the independent actual gpt-6.1-sol review of v5.
