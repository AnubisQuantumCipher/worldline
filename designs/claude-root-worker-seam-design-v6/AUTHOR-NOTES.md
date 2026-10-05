# Author notes: root-worker seam design v6

Process record, deviations, uncertainties and OPEN items for `SEAM-DESIGN.md` v6. These notes are the author's own record. They review, accept and close nothing.

## 1. Task and role

- **Task.** From the lead: draft seam design v6 in `WT/designs/claude-root-worker-seam-design-v6/`, answering V5-REQ-A … V5-REQ-M of the sealed independent review of v5 (`WT/designs/claude-root-worker-seam-design-v5/review/claude-v1/`) exactly as the review states them, keeping everything it closed, and changing nothing else.
- **Process change, as relayed by the lead.** By the human's direction of 2026-10-05, independent reviews are done by independent Claude review subagents rather than gpt-6.1-sol; the substance is unchanged. The review's freeze names its reviewer kind (`claude-subagent`, `different_from_author` true).
- **Role limits kept.** The author reviewed, accepted, closed and adopted nothing. No agent was spawned. In particular H′ is offered, not adopted (V6-K.4).
- **Inputs read first, in full:** `REVIEW.md` and `review.json` of the v5 review, with the freeze checked against the three files it lists (equal). Not read: `raw-final-message.txt` (not in the freeze), `review/gpt61-v1`, `review-records/`.

## 2. Process record

**Reads.** The Read tool, and Bash used read-only: `sed -n`, `awk`, `grep`, `sha256sum`, `wc`, `cut`, `nl`, `command ls`, `test -e`, and Python scripts on standard input that read files and printed to standard output. No command redirected output to a file; no `mkdir`, `cp`, `mv`, `rm`, `tee`, `chmod` or `touch`; no git command.

**Writes.** Exactly four files, all in `WT/designs/claude-root-worker-seam-design-v6/`, created or changed only with Write and Edit: `SEAM-DESIGN.md` (written in chunks at a temporary `@@CONTINUE@@` marker, and with four `@@…@@` placeholders in Appendix D filled last; the verification confirms none remains), `jackal.json`, `AUTHOR-NOTES.md`, `seams.json`.

**Not run.** No compiler, prover, test, WORLDLINE, COSMOGONY or root-worker code (nothing imported or executed), service, `systemctl`, sudo, namespace, project-vault or restic. Nothing under `/srv`.

**Not read.** `WT/packets/capi-pk0/`; `~/.local/share/sia/.gbrain/`; the lead's top-level transcript and every other transcript. `/home/sicarii` itself, `~/iPad` and `~/iPadBackup` were not listed or stat'ed. The lane draft and its preimage were read and not changed.

**No interruption.** No TaskStop, `kill`, `timeout` wrapper or background task. Every command ran in the foreground to completion.

**Verification (final run, observed).** A read-only Python script read the v4 and v5 designs, the sealed v5 review and v6 `SEAM-DESIGN.md`, and printed:
- 13 C5 slices, every hash equal to the stated v5 lines' hash; no overlap; every v5 line covered by a slice or a superseded range of §B.3, or empty or `---`;
- 29 R6 blocks, each quoted `v5:` or `v4:` text equal to the stated lines; every v5 target inside its stated C5 slice; every v4 target inside its C4 slice as v5's §B.1 states it and replaced by no R5; no line targeted twice;
- every V5-REQ change quoted verbatim from `review.json`; every ruling string verbatim; the 22 non-closed clause gaps verbatim from REVIEW.md, and exactly the set `review.json` lists as not closed;
- every markdown table row with its header's cell count; every `V6-…` reference resolving to a heading (the two control labels V6-N.B and V6-N.C are labels inside V6-N);
- after the fill, no `@@…@@` placeholder left.
- Final problems: 0.

**Citation spot checks.** Newly cited source lines were printed and compared while drafting. Corrections made before the final run: the version-check lines (`rw/resource_child_execution.py:113`, `rw/canonical_exchange_kernel.py:32`), and `SYSTEMD_LAUNCH_FAILED` at `rw/linux/systemd.py:232-233`.

## 3. SIA

One `sia.ask` at the start of this task, about prior decisions on custody return, reattach, the workload dispatcher and a service-class coordinator. Its truth-boundary line, verbatim: "boundary: senses live · chains pass · graph complete · 6 span(s) redacted at ingest · semantic recall · associative rerank off by measured default; retrieval.associative_rerank enables it · absence of recall ≠ evidence of absence". Every result was a `[model]`-origin agent note; none was opened and none is used as evidence. No `sia.note` was written.

## 4. Skills

The eight Ada skills were loaded in this session before any Ada reading: `ada`, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`, `ada-2005-amendment`, `ada-high-integrity`. v6 reads Ada specifications only through citations carried from v5 and v4.

## 5. JACKAL

No numeral in v6 was derived by arithmetic, so no call was made (`jackal.json`). One count that would have been a subtraction (the 37 closed clauses) was instead observed by listing `clause_closure` directly. v5's J5-1 … J5-4 are carried.

## 6. Deviations

- **None** against the hard limits, as far as the author knows.
- **Form.** The lead preferred a self-contained v6 with the composed text inlined. v6 carries by hash-pinned slices instead (see §7, item 1); this is a departure from a preference, not from a limit, and is disclosed here.

## 7. Uncertainties and choices for the reviewer

1. **Why the composed text is not inlined.** The effective text is the chain v1 → v2 → v3 → v4 → v5 with its replacements, several hundred kilobytes. Composing it means generating text by script and writing it to a file, which the Write/Edit-only rule makes possible only by retyping it through the model, where a transcription error could pass unnoticed. Every carried range is instead pinned by sha256 and verified by script, and every replacement quotes its target exactly. The reviewer can recompose mechanically from the pins.
2. **H′'s adoption (V6-K.4).** The author reads H′ as changing no resource-policy field, so its adoption would be the lead's engineering decision and not a D-4a selection. The reviewer should check that reading; if it is wrong, H′ becomes a D-4a package, and CG-2 and CG-3 still stay OPEN with their conditions unchanged.
3. **R1 custody return** still cannot detect an escaped descriptor holder (V6-F.4); it rests on OB-ESC and AU-2. Only R2 has the fresh-`flock` test.
4. **RC-10 decides V6-I's branch** before the code is reviewed. If neither branch matches the installed behaviour, V6-I must be revisited.
5. **The dispatcher's evidence fields** (CJ-DISP-4, CJ-DISP-5) come from helper frames and cgroup files, not from the manager's journal and properties; the runner's classification must still match.
6. **The material layout** (V6-A.3) and the convention table (V6-A.2) are new designs. Only the two conventions themselves are observed.
7. **`archive_equal`'s rounding and bit layout** depend on RC-5.

## 8. OPEN items

V6-P of the design lists everything OPEN; V5-O and V4-O (carried) remain. In short:
- every original obligation, OB-001 … OB-219;
- V5-REQ-A … V5-REQ-M; every required change, clause and ruling not CLOSED_AT_DESIGN_LEVEL;
- CG-1 … CG-4; CJ-DISP-1 … 6, CJ-ARCH-1 … 3, CJ-H-1 … 4, CJ-JSON; OB-ESC with AU-2;
- K-1 … K-28 and RC-1 … RC-7, RC-9 … RC-12;
- H′'s deltas D-H1 … D-H6;
- the independent review of v6.
