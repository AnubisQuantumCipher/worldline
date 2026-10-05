# Author notes: root-worker seam design v3

Author: Claude Code lead claude-opus-5-5 (drafting subagent, author role). Date: 2026-10-05.

These notes go with `SEAM-DESIGN.md` v3 in this directory. They are the author's own account and review nothing. Nothing here closes or accepts anything, and every obligation stays OPEN. Aliases are those of SEAM-DESIGN §C.2.

## 1. What v3 does

- **The closure tables (§A)** quote every required change, RQ-1's required change, every PARTIALLY_CLOSED clause gap, and every PARTIALLY_CLOSED ruling's owner, evidence and gap verbatim from the sealed review. A read-only script confirmed that each quoted string occurs verbatim in SEAM-DESIGN.md (§5.3).
- **Carrying v2 text (§B).** v3 carries v2 text by line range and sha256: 43 slices and 43 quoted line replacements, R3-1 … R3-43. Compared with the first v3 draft, it now also carries the v2 sections that hold reviewed content:
  - §3.1–§3.4, §3.6, §3.7 and §3.9 (scoped clauses, domains, embedding, lemmas);
  - §4.1 (record grammar);
  - §5.3 (P-CE1 … P-CE4) and §5.5 (dispatcher);
  - §9.2 (options A, B, C and E);
  - §11.1 (U-1 … U-12);
  - §18 (the OPEN list the review keeps open).

  Only the rejected lines are replaced.
- **The design answers** are V-A … V-Q. New author observations are NF-1 … NF-11 (§A.7).

## 2. OPEN items and honest uncertainties

1. **RQ-1 trade-off.** v3 follows the review's direction: current context only where an original native command checks it. Consequences:
   - A scope or universe rollover between reserve and launch now passes the pre-effect, writes EFFECT_INTENT, and is refused by the native Record_Launch_Intent or Record_Running (`Context_Changed`).
   - The original semantics then apply: quarantine and K4 (`rw/protected_operations.py:767-768`).
   - v2's FRESH placement refused earlier, at the pre-effect, before EFFECT_INTENT.
   - The reviewer should judge which placement preserves the original domain better. v3 does not claim either is accepted-case-neutral.
2. **Design tables are unreviewed specifications:** the O×U table and C×P rules (V-F.3), the mutation table (V-F.4), the crash and recovery table (V-G.5), the drain failure table (V-H.3) and the per-gate modes (V-I.5). Individual cells may be wrong. The native relations, once written, are the authority.
3. **CV-R completeness.** It is not shown that the residuals R1, R2 and R3 exactly cover D_raw \ D_emb. G6 was folded into R2 during drafting, and other residual classes may exist.
4. **L-RB-4** needs a static audit of every predicate for position independence. That audit was not done.
5. **PD-1 … PD-5, L-BR-1, L-SAT-1 and CJ-1** are stated, not proved. PD-1 is partly a Python producer-correspondence obligation.
6. **The custody genesis is the root of trust** and cannot be bound by the descriptor, because the genesis binds the descriptor's digest. v3 authenticates it by source-lease DATA, which is Python, and by a native HMAC check of the head MAC under the issuer key. Key handling in the private arena (lifetime, zeroization) is OPEN.
7. **The canonical JSON recognizer (V-C.1)** has two forms, UTF8 and ASCII (NF-8). Number canonicality rests on the Python check alone, and the escaping details depend on RC-4.
8. **Confinement M-1 … M-5 is unmeasured** (K-17, K-18, K-20, K-21). NF-1 (an `O_RDONLY` procfs dirfd still allows write-opens) and NF-6 (systemctl reachable) are the author's reading.
9. **Drain transfer.**
   - The StreamReader quiescence relies on asyncio behaviour (RC-1).
   - The crash window between STOP_INTENT and FREEZE can lose StreamReader-buffered bytes on today's V3 slots, as a crash does today. Successor slots close that window.
   - kcmp across PID namespaces (K-5) and the host pid from pidfd fdinfo (K-4) are unmeasured.
10. **FRESH socket identity (J4)** depends on K-15. The domain-preserving fallback (V-I.6) has an availability cost: requests wait until custody returns. That cost is recorded in V-L.5, not resolved.
11. **Capacity.** No reserved-capacity completion is claimed. P-M1, P-M2, P-D1 and option F await the operator's D-4a selection. F's dynamic ceiling needs measurement (K-8, K-16).
12. **CAPI5 dependence.** R-QUAL, the branch-sensitive R-GATE and MQ1–MQ14 are used as labelled, unreviewed dependencies. If CAPI5's review changes them, V-K.3 … V-K.9 follow the accepted rules.
13. **Startup v2 (V-J.2):**
    - the command names in `runtime.tools` are not fixed (U-3 says "under their installed names");
    - the provisioner entry paths are U-5's and U-12's proposals;
    - the draft's `attach_scoped_resource` reads `runtime.resource_scoped_producer`, which v1's exact runtime keyset cannot carry. That is consistent with U-11 ("v2 only"), not a new finding.
14. **Per-gate worker modes (V-I.5)** are a proposal. In particular, the before-exec capture serves both the root's own operation (RETAINED) and transferred requests (FRESH).
15. **The child protocol (V-E.1)** journals to the scoped observation journal. The exact event names and their native relation are not written.
16. Every original obligation OB-001 … OB-219 and every v2 §18 item (C2-18) stays OPEN.

## 3. Where the reviewer may want to look first

1. The RQ-1 placement (§2 item 1): V-B.10, and C2-31 with R3-25 … R3-31.
2. V-C.1 and V-C.3: the two JSON forms, `Installed_Digest`, the custody genesis as root, and the catalogue anchored through the run-scoped config.
3. V-F.2 and V-F.3: the O mapping, which keeps v2's five values (broker progress is an attribute), and the O×U cells.
4. V-E.3: whether any retained capability, view or channel is missing.
5. V-H.2 and V-H.3: the quiescence rules and crash windows.
6. V-K: every **[depends on unreviewed CAPI5]** label, and the RW table placement against CAPI4's layout (`CAPI4/DESIGN.md:337-356`).

## 4. Corrections made to the first v3 draft during author verification

These came from static re-reading before handback. They are listed so that the reviewer can see what changed.

- **Line citations** corrected against the source, for example:
  - the snapshot check is `rw/protected_scoped_resource_runtime.py:696` and `rw/protected_operations.py:711`;
  - broker `recover` is at `:177`, and the flock helper at `rw/protected_startup.py:374-385`;
  - the genesis DATA binding is `:275-277`;
  - also the escrow precondition, the custody FD lines, the C helper ranges and the CAPI4 binding rows.
- **The O mapping** no longer invents an `IN_FLIGHT` value; v2's five O values are kept.
- **Owner plan.** The proposed owner plan v2 was dropped, because v2 §11.2 keeps `-plan-v1`.
- **Startup keysets.** `runtime.resource_scoped_producer` was restored, because the draft reads it, and the `provisioned_state` additions were restored as U-3 has them.
- **Circularity.** The custody genesis was removed from the descriptor's `files`.
- **JSON forms.** The canonical form for the startup containers is UTF-8, not ASCII. The run-scoped config is ASCII.
- **Genesis authenticity.** The custody genesis is not MAC'd today; only its events and head are.
- **Catalogue.** It is anchored through the run-scoped config's `["catalogue"]` value, not through the OS-producer config.
- **Lease descriptors.** The startup-lease descriptors are lock OFDs, not state files.
- **CAS order.** V-F.6 now checks replay before the CAS, so a caller whose acknowledgement was lost gets its own event back.
- **Host pid.** V-H.4 no longer assumes the worker knows its host pid.
- **Carried text that conflicted with v3** was replaced rather than left standing:
  - C2-62's settlement row required a handler terminal, and its handoff rows lacked roster evidence;
  - C2-84 and C2-93 made cookies and namespace records mandatory, or refused;
  - C2-74 and C2-18 referred to the T1–T5 protocol.

## 5. Process record

### 5.1 Writes and refusals

- **Files created,** all with the Write tool and only in this directory: `SEAM-DESIGN.md`, `jackal.json`, this file and `seams.json` (planned after this file). All later changes to `SEAM-DESIGN.md` were made with the Edit tool.
- **Counts when this file was written** (observed by a read-only script over this agent's own session record): Write 2, Edit 145. After this file come one Edit (SEAM-DESIGN Appendix D) and one Write (`seams.json`). The handback reports the final counts.
- **Refusals.** No Write or Edit was refused. Two Edit calls returned "String to replace not found", because their `old_string` spanned non-adjacent table rows. Each was redone as a single-row Edit. These were tool errors in my own input, not permission refusals.
- **The lane draft** (`W/work/protected-original-root-worker-repair-v1`) was not changed. Neither were v2, the reviews, CAPI4 or CAPI5.

### 5.2 Bash use (read-only) and every deviation

There were 197 Bash commands in this task when this file was written (observed by the same script). All were read-only inspection. The forms used were:
- `sed -n`, `grep` (aliased to ugrep), `cut`, `nl`, `head`, `tail`, `wc`, `sha256sum`, `sort`, `echo`, `printf`, `awk`, `od`, `fold`, `cat`, `find`;
- `ls`, aliased to eza, and once `command ls`;
- shell variables, `for` loops and `cd` inside a single command;
- Python scripts given on standard input (`python3 - <<'PY'`) or by `python3 -c`. They read files as text or JSON, printed to standard output and wrote nothing.

Deviations, each disclosed:
1. **No redirection to any file.** `2>&1` was used only into a pipe. No command used `2>/dev/null`. The two commands whose text contains that string are my own audit scripts, which hold it as a search pattern.
2. **`cd`** inside single commands, affecting only that command's shell.
3. **`cat`** of the CAPI4 review's `review-freeze.json`, piped to `head`.
4. **A depth-1 `find -printf` of the CAPI5 directory.** It printed that directory's entry names, including the name of its `review` directory. Nothing under `review/` was listed, read or hashed.
5. **`ls -t` failed** under the eza alias ("invalid value"). It was rerun as `command ls -t`. That was the only failing Bash command.
6. **This agent's own session record** (`~/.claude/projects/-home-sicarii/0e157c30-4700-4604-ab0e-cc6c3b9c6c37/subagents/agent-a01ff3579cb09cea3.jsonl`) was read by read-only Python. The purpose was to verify the SIA truth-boundary line and labels, the loaded skills and this process record. A listing of that `subagents` directory showed other agents' record file names; none was read.
7. **One harness-persisted output file** (`.../tool-results/bma0loavc.txt`) was read with the Read tool. The harness wrote it because a command's output was too large to display. I did not write it.

### 5.3 Author checks run (self-checks, not review)

- **Slice verification** (SEAM-DESIGN Appendix C). For v2: 2296 lines, sha256 `db512ddb…e1b5`. 43 §B.1 rows matched. 43 replacement quotes were exact and lay inside their stated slices. No slices overlap. 22 transitive v1 slices matched.
- **Review quotes.** All 12 required changes, RQ-1, all 33 PARTIALLY_CLOSED clause gaps, all PARTIALLY_CLOSED ruling owner, evidence and gap texts, D-2b's owner and evidence, and the five domain and control findings occur verbatim.
- **Input identities** in Appendix B were hashed read-only.

### 5.4 Interruptions

None. No TaskStop, kill or timeout wrapper was used, and no background task. No command hung.

### 5.5 SIA

- One `sia.ask` at the start of this task and one `sia.recall` of a returned slug.
- The ask returned agent notes labelled `[model]` and one `[evidence]` item, the `skills/worldline` skill text. The recall returned a note labelled `[origin:model]`.
- Truth-boundary line, verbatim: "boundary: senses live · chains pass · graph complete · 6 span(s) redacted at ingest · semantic recall · associative rerank off by measured default; retrieval.associative_rerank enables it · absence of recall ≠ evidence of absence".
- SIA content is used as evidence for nothing. No SIA note was written.

### 5.6 Execution

- Nothing of WORLDLINE, COSMOGONY or the root worker was imported or executed. Python only read files as text or JSON.
- No compiler, prover, test, service, `systemctl`, sudo, namespace, project-vault or restic was used. Nothing under `/srv` was touched.
- `~/.local/share/sia/.gbrain/` was not touched, and `/home/sicarii` itself, `~/iPad` and `~/iPadBackup` were not listed or stat'ed.

### 5.7 JACKAL

No JACKAL call was made in this task, because no numeral in v3 is derived (`jackal.json`). The counts in the v3 files are observed and listed with their sources in `jackal.json`.

### 5.8 Skills

The eight Ada skills, `worldline` and `cosmogony` were loaded with the Skill tool at the start of this session and applied. They were not reloaded.

### 5.9 Storage

Only the four files in this directory were created. No scratch file was written.
