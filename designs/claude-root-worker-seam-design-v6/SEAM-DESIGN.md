# Root-worker runtime lane: seam design v6

| | |
|---|---|
| Author | Claude Code lead claude-opus-5-5 (drafting subagent, author role) |
| Date | 2026-10-05 |
| Status | **DRAFT_FOR_INDEPENDENT_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. The author reviews, accepts and closes nothing; author checks are self-checks. Every original obligation (OB-001 … OB-219), accepted case, deterministic fixture, control, contract, threshold, proof floor and scope remains **OPEN** and unchanged. |
| Supersedes | v5 `SEAM-DESIGN.md` (sha256 `938c832d03df0910506756ec295acef86ae2cacba4d7b2478a09c6d27f3685cf`, 234572 bytes, 1628 lines), v5 `seams.json` (`a3d3ff5482c188705050f7f83709ff2f5e418547ed4a71f26f705f8c5fe18ebe`), v5 `jackal.json` (`9adaaa83960f7064552dee1f85ffa38ad5191f0e6d6cd02321b287121e931628`) and v5 `AUTHOR-NOTES.md` (`d6e16bdfb23b2544218694508144ba32f72ab3c23f79fa9dcb0f2117d324b836`). All were read only and re-hashed unchanged; they equal the review's `design_sha256` and `seams_sha256`. |
| Answers | The sealed independent review of v5 in `WT/designs/claude-root-worker-seam-design-v5/review/claude-v1/`: `REVIEW.md` `d385baca2e5eba7a9605c486d1b5afb2f3fc56cae1d893eed9ba163bf1cc0a50` (30875 bytes), `review.json` `0b9a3b0705df9d40f7b4e109d4f2042cb6236dcc848fd48f32f27a0de5ff8187` (18321), `checks.json` `6f24f1a44718ce7f8d0b5159b3b78de1cb45ddbf4a2681cacdba9cfe10ead0ab` (8952), `review-freeze.json` `04b87e452db87f791194a633b8602bf716edc3a41dc4451a002e10d85d000a36` (613). The freeze names "claude-opus-5-5 (independent Claude Code review subagent, fresh context)", `reviewer_kind` claude-subagent, `different_from_author` true, and lists the first three files with exactly these hashes and sizes (recomputed, equal). By the human's direction of 2026-10-05, relayed by the lead, independent reviews are now done by independent Claude review subagents; the substance of the review obligation is unchanged. Verdict **ENDORSED_WITH_REQUIRED_CHANGES**: V4-REQ-H and V4-REQ-K CLOSED_AT_DESIGN_LEVEL; V4-REQ-A … G, I, J, L and RQ-1 PARTIALLY_CLOSED; 37 clauses CLOSED_AT_DESIGN_LEVEL and 22 PARTIALLY_CLOSED; D-2b CLOSED_AT_DESIGN_LEVEL, every other ruling PARTIALLY_CLOSED; required changes V5-REQ-A … V5-REQ-M. Not read: that directory's `raw-final-message.txt` (not in the freeze), `review/gpt61-v1`, and anything under `review-records/` (interrupted partial reviews), as directed. |
| C-API status | Unchanged from v5 (carried in substance): CAPI5R ENDORSED_WITH_REQUIRED_CHANGES (V5-RC4-GATE-EXCEPTION, V5-RC4-QUAL-CAPTURE); CAPI6R ENDORSED, those two and V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 CLOSED_AT_DESIGN_LEVEL only; ROOT_WORKER_INTEGRATION OPEN. Their identities are v5's header (carried by history) and Appendix B. The PK-0 packet under `WT/packets/capi-pk0/` was not read. |
| Scope | Design only, for the draft lane `W/work/protected-original-root-worker-repair-v1` (status `INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY`). The lane draft is someone else's unreviewed source and was not touched. v6 grants no execution, proof, build, test, review, operator or acceptance authority, and adds no approval gate. |
| Location | `WT/designs/claude-root-worker-seam-design-v6/` |
| **What this document consists of** | v6 is (1) the text of this file; (2) the v5 `SEAM-DESIGN.md` line ranges listed in §B.1 (slices C5-…), each bound by the sha256 of its exact bytes, with the quoted replacements R6-1 … R6-29 of §B.2 applied; (3) transitively, everything those v5 slices carry: slice C5-B is v5's own §B, so the v4 slices it binds (C4-…) with R5-1 … R5-17 (as amended by R6), and through them the v3, v2 and v1 chains, minus v5's withdrawals W5-1 and W5-2. Every other v5 text is superseded by the map of §B.3. Why the composed text is not inlined: AUTHOR-NOTES §7. |
| Companion files | `seams.json` (machine twin), `jackal.json` (JACKAL record), `AUTHOR-NOTES.md` (process record, uncertainties, OPEN items). Identities: Appendix D. |
| Write history | Every file in the location above was created or changed only with the Write and Edit tools. Bash was used only for read-only inspection (AUTHOR-NOTES §2). |

Every statement about source is **static**: read from files, or reasoned from what was read. Nothing was compiled, run, imported, proved, tested or measured. Kernel, systemd, SQLite, interpreter and Ada-visibility statements marked **[unverified reasoning]** are the author's reading and name their evidence item.

---

## A. Closure tables

"Answer" is a design statement for the reviewer. The author closes nothing. Every proof, native, control, physical and acceptance obligation stays OPEN.

### A.1 Required changes V5-REQ-A … V5-REQ-M

Each change is quoted verbatim from the sealed `review.json` `required_changes[].change`.

| Id | Required change (verbatim) | v6 answer | Where |
|---|---|---|---|
| V5-REQ-A | "Record the actual per-export ABI conventions (pairs vs triples), fix the convention of each new/successor export including X-8 and the sub-helper material, and make X-5 RootStateRec equal Root_State and the V5-J.2 columns (drop stop_intent/returned; add Owners_Open, Abort, Launched, Witness, Settled, Released_Unlaunched, Reattach_Epoch)." | The two observed conventions are recorded exactly from the wrappers: P (every argument a pointer and one size word, whose meaning is the record's byte size, the arena's byte length or a roster's element count) and T (Input and Arena pairs, then (pointer, element count, total byte size) triples, then the Result pair). Every new and successor export has a fixed convention; X-8 keeps P with two appended rosters; the sub-helper material is a byte layout of the exact P arguments. `RootStateRec` is now field for field `Root_State` and the root_state columns; `owner`, `stop_intent` and `returned` are gone. | V6-A; R6-6, R6-7, R6-14 |
| V5-REQ-B | "State that IP requests served in the worker run under the WL request's root-unit bound (AO-5/AO-6/AO-11 gap as for G); withdraw the serial-route cost equality for them; design a non-borrowing route or record an OPEN containment gap with a closure condition." | Stated. The cost equality is withdrawn for worker-served IP requests and kept only for front-served ones. OPEN containment gap CG-2, with a closure condition stated against the original obligation and independent of D-4a; H′ (V6-K) is a design that meets it. | V6-B; R6-9, R6-11 |
| V5-REQ-C | "Record queueing of later WL requests for g+1 as an OPEN containment gap against original per-request concurrency, not as a difference resolvable only by D-4a." | OPEN containment gap CG-3 against `P1/HANDOFF.md:115`, with its own closure condition, independent of D-4a. H′ meets it at design level. | V6-C; R6-10, R6-25, R6-29 |
| V5-REQ-D | "Complete the dispatcher interface and CJ-DISP-1: outcome, pid, launcher.wait, launcher stdio, supervision dict semantics and the original exceptions." | `WorkerSystemdDispatcher` and `DispatchedProcess` are specified against every attribute and method the runner uses (observed by grep): `launch`, `stop`, `outcome` with all thirteen supervision keys, `effective_limits`, `resource_telemetry`, `unit`, `pid`, `launcher.wait`, `launcher.stdin`, `launcher.stdout`, `launcher.stderr`, and the original exception codes. Each difference in evidence source is a named correspondence obligation. | V6-D |
| V5-REQ-E | "Specify archive_equal against the actual archive encoding (int sign plus LE magnitude; float binary64 bits via Round), with correspondence and costs; correct D5:693; map the original ValueError refusal class of the JSON checks." | The four layers of the actual encoding are specified from source. An integer compares as its sign flag and minimal little-endian magnitude, and a non-integer as the big-endian binary64 bits of `Round`, sign bit included, so −0.0 compares by its bit. Correspondence obligations and costs are stated, and D5:693 is corrected (R6-12). Each native status maps to the class the original check raises; the overflow lexeme keeps its `ValueError`. | V6-E; R6-12 |
| V5-REQ-F | "Define authentic CUSTODY_RETURNED and XC-4 evidence after a front restart; make the no-custody-descriptor-escape premise an explicit design obligation with an audit and a control." | Two regimes. If the front was alive since HELD, the two pidfds as before. If the front restarted, identity-gone evidence (`pidfd_open` of the recorded host pid, compared by recorded start tick) for the worker and the namespace init, plus a fresh exclusive `flock` that succeeds on every transferred lock file. OB-ESC is an explicit obligation with audit AU-2 and controls C-ESC-1 and C-ESC-2. | V6-F; R6-18, R6-20, R6-22, R6-24 |
| V5-REQ-G | "Give a legal durable route from Unknown back to service for a live reattachable worker, and specify the worker's behaviour while its mutations are refused." | `WORKER_REATTACHED` is legal in Unknown when `Before_Unknown` is a worker phase. `RECONCILED` returns to `Before_Unknown` on that durable event plus the worker's live identity, for cause classes that a reattach resolves. While Unknown, the worker mutates nothing, waits at the refused choke point without raising or quarantining, keeps its children and descriptors, accepts no transfer and keeps its reattach endpoint open. | V6-G; R6-17, R6-19, R6-26 |
| V5-REQ-H | "Specify PREPARED before machine admission and Record_Launch_Intent; replace the lane's unconditional UNKNOWN append in its no-slot failure branch with the original phase-conditional one." | The launch order is given with `PREPARED (g)` first. The lane's `PREPARED` record content moves to `HELD`. The no-slot failure branch appends `UNKNOWN` only in the original's phases (`DISPATCH_INTENDED`, `NAMESPACE_HELD`, `GO_INTENDED`, `UNKNOWN`), exactly as the original scoped launch does, so a `NEVER_DISPATCHED` row keeps `Never_Holds` and `Release_Hold`. | V6-H; R6-15, R6-16, R6-21 |
| V5-REQ-I | "Specify the RELAY transport-loss outcome if RC-10 shows that the original re-read raises nothing, adding no refusal or quarantine; specify the daemon-level steps for FRESH and RELAY requests." | Both RC-10 outcomes are specified. If the original re-read raises nothing on a closed client, the gate's value is the last authenticated front re-read, which the original re-read would have returned unchanged. The operation continues, and only the response write is lost, as `_send` drops writes to a closed writer. No refusal or quarantine is added. The daemon steps are split exactly: the front parses and answers parse errors as the original does; the custody owner captures, retains, locks, invokes, publishes and produces the response bytes. | V6-I; R6-23 |
| V5-REQ-J | "Specify how the sub-helper is created outside the coordinator's PID namespace given unshare(CLONE_NEWPID), and add a kernel measurement under OP-7." | The root helper v2 forks a child factory before its `unshare (CLONE_NEWPID)`. The factory stays in the host PID and mount namespaces and forks every sub-helper. K-28 is added under OP-7's existing reservation. | V6-J; R6-13 |
| V5-REQ-K | "Complete Option H with the mapping from per-agent launches onto launch_reserved (single dispatch per reservation, top-level only) and revise its AO marks." | H′: each WL request's own top-level reservation is dispatched once, as a request-root unit. Each per-agent runner launch is a child task of that same request's root, so no reservation is dispatched twice and no child is made top-level. The AO marks are revised, with the per-agent correspondences CJ-H-1 … CJ-H-4 OPEN. | V6-K |
| V5-REQ-L | "Add explicit R5 replacements for v4:1801 and v4:1804 in place of RR5-7 neutralisation; attribute CG-1 to the preimage; record owner.retry's UNINTEGRATED refusal as an OPEN containment gap." | R6-4 and R6-5 replace v4:1801 and v4:1804 by quotation, and R6-1 retires RR5-7's neutralisation. CG-1 is attributed to the preimage (`pre/protected_operations.py:729-730`). `owner.retry`'s refusal is OPEN containment gap CG-4 (`pre/protected_operations.py:720-722`, `rw/protected_operations.py:735-737`). | V6-L; R6-1, R6-4, R6-5, R6-8 |
| V5-REQ-M | "Split K-27: kernel memfd mapping under OP-7; dynamic-loader behaviour as a lead-owned RC item." | K-27 keeps only the kernel's memfd seal and mapping behaviour (OP-7). The loader's loading of `/proc/self/fd/N` becomes RC-11, lead-owned. | V6-M; R6-27 |

### A.2 V4-REQ, RQ-1 and clause status after the v5 review

From `review.json` `rc_closure`: V4-REQ-H and V4-REQ-K CLOSED_AT_DESIGN_LEVEL (carried unchanged, §A.4); V4-REQ-A, B, C, D, E, F, G, I, J, L and RQ-1 PARTIALLY_CLOSED, each answered by the V5-REQs the review maps to it (REVIEW.md §1). The 22 PARTIALLY_CLOSED clauses, with the review's remaining gap quoted verbatim from REVIEW.md's clause table:

| Clause | Remaining gap (verbatim) | v6 answer |
|---|---|---|
| 01.1 | "ABI convention and X-5 record (V5-REQ-A)" | V6-A |
| 01.5 | "Saturated witness specified; D_prod coverage (CV-B′, CV-R) OPEN" | Stays OPEN as an obligation; nothing in v6 claims D_prod coverage |
| 01.7 | "As RQ-1" | V6-B, V6-C, V6-L (R6-4, R6-11) |
| 02.1 | "archive_equal numeric premise (V5-REQ-E)" | V6-E |
| 02.2 | "Claim bounded honestly; authentic selection and currentness remain unmet obligations" | Unchanged: P-A1 … P-A4 stay OPEN obligations |
| 02.3 | "Crosswalk record given; convention and costs OPEN" | V6-A (convention T for X-3); costs stay OPEN |
| 02.4 | "No option meets every AO; H incomplete" | V6-K |
| 03.2 | "Sub-helper namespace placement (V5-REQ-J)" | V6-J |
| 03.3 | "CG-1 persists in deployments without a root worker; dispatcher interface incomplete" | V6-D, V6-L |
| 04.1 | "A complete product now exists; Unknown/reattach, PREPARED ordering and X-5 gaps remain" | V6-G, V6-H, V6-A |
| 04.3 | "X-5 record versus DDL" | V6-A.4 |
| 04.4 | "CUSTODY_RETURNED after a front restart" | V6-F |
| 06.2 | "As V4-REQ-D" | V6-K |
| 06.3 | "M8(c) withdrawn (acceptable); cancel progress while unreachable or Unknown is open" | V6-G (Unknown → service), reattach (carried); stays OPEN for a worker that never reattaches |
| 06.4 | "Later WL requests queued for g+1" | V6-C (CG-3) |
| 07.3 | "Route admitted; its launch-journal and PREPARED preconditions do not hold against the lane code (V5-REQ-H)" | V6-H |
| 09.2 | "RELAY transport-loss premise (RC-10)" | V6-I |
| 09.5 | "Unknown/reattach service dependency" | V6-G |
| 11.1 | "Per-export edges given; convention gap" | V6-A |
| 12.1 | "X-5 versus DDL; native genesis compare" | V6-A.4, V6-E |
| 12.2 | "CUSTODY_RETURNED after restart; no-launch preconditions" | V6-F, V6-H |
| 12.4 | "Unavailable-owner and Unknown progress" | V6-G, V6-F |

### A.3 Rulings

From `review.json` `rulings[].ruling`, verbatim: D-1a "PARTIALLY_CLOSED; V5-REQ-A, V5-REQ-B"; D-1b "PARTIALLY_CLOSED; V5-REQ-B"; D-2a "PARTIALLY_CLOSED; V5-REQ-A, V5-REQ-E"; D-2b "CLOSED_AT_DESIGN_LEVEL (carried by C2-116)"; D-3a "PARTIALLY_CLOSED; design-level repair complete (V4-REQ-H), lab evidence OPEN"; D-4a "PARTIALLY_CLOSED; V5-REQ-B, V5-REQ-C, V5-REQ-K"; D-5a "PARTIALLY_CLOSED; V5-REQ-A, V5-REQ-J"; D-5b "PARTIALLY_CLOSED; V5-REQ-J"; D-6a "PARTIALLY_CLOSED; V5-REQ-F, V5-REQ-H"; D-7a "PARTIALLY_CLOSED; V5-REQ-E"; D-8a "PARTIALLY_CLOSED; V5-REQ-I"; D-8b "PARTIALLY_CLOSED; V5-REQ-F, V5-REQ-I, V5-REQ-J; measurements stay with the operator under OP-7"; D-9a "PARTIALLY_CLOSED; V5-REQ-A, V5-REQ-F, V5-REQ-G, V5-REQ-H". Each is answered by the V6 sections of the REQs it names. Owners and evidence requirements are unchanged (the review checked them byte for byte against v5's §A.5, which is carried as history). D-3a is not closed: its lab and physical evidence stays OPEN.

### A.4 Carried exactly as the review closed them

Nothing below is changed by v6. Where an R6 touches the same section, it does not touch the closed text.
- **V4-REQ-H (CLOSED_AT_DESIGN_LEVEL):** v5 V5-H, carried verbatim as slice C5-VH. No R6 targets it. K-25 and OP-7 lab evidence stay OPEN.
- **V4-REQ-K (CLOSED_AT_DESIGN_LEVEL) and the C-API integration:** v5 V5-K, carried verbatim as slice C5-VK. No R6 targets it. Implementation, stage reviews and IC-10 stay OPEN.
- **The 37 CLOSED_AT_DESIGN_LEVEL clauses** (`clause_closure`): 01.2, 01.3, 01.4, 01.6, 03.1, 04.2, 04.5, 04.6, 05.1 … 05.5, 06.1, 07.1, 07.2, 07.4, 07.5, 08.1 … 08.7, 09.1, 09.3, 09.4, 10.1 … 10.4, 11.2 … 11.4, 12.3, 12.5. Their text is carried in the slices that held it. Three notes: **09.4** stays closed only if RELAY transport loss adds no refusal (`clause_notes`), which V6-I meets. **07.1**'s relations are untouched except row evidence (R6-15 … R6-20), which only adds conditions to existing rows and legalises `WORKER_REATTACHED` in one more phase; no relation, cross-condition or C×P rule is removed. **04.5**'s outer test (C4-VG23, R4-30) is unchanged.
- **D-2b (CLOSED_AT_DESIGN_LEVEL),** carried by C2-116 through C5-B; `frontier_sha256` `a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb`; the frontier control is unchanged.
- **R5-1 … R5-17 and W5-1, W5-2,** which the review found exact and justified, are carried inside C5-B. R6-2 and R6-3 change only the `v5:` result lines of R5-16 and R5-17, to extend the measurement range (RR6-4).
- **Operator items** (`operator_items`): OP-1 … OP-6, OP-8, OP-9 WITHIN_RESERVED_SCOPE; OP-7 "WITHIN_RESERVED_SCOPE_RANGE_REPAIR_COMPLETED for K-1 through K-27 (K-27 loader part should become a lead-owned RC item, V5-REQ-M)". v6 splits K-27 (V6-M) and adds K-28 (V6-J), the same kind of range repair (R6-2, R6-3). No operator item is added, lowered or widened; `no_new_operator_gate` stays true.

### A.5 The review's findings and v6's answers

| Id | Review assessment (verbatim status) | v6 answer | Where |
|---|---|---|---|
| NF5-1 | VERIFIED_STATIC_WITH_OWNER_ROUTE_EXCEPTION | The owner operations return before `_reserve`; the daemon steps for transferred requests are specified | V6-I.3 |
| NF5-2 | VERIFIED_STATIC_INCOMPLETE | Full dispatcher interface | V6-D |
| NF5-3 | VERIFIED_STATIC | Used by H′'s mapping | V6-K |
| NF5-4 | VERIFIED_STATIC_ABSENCE_IN_SELECTED_SOURCE | Unchanged | — |
| NF5-5 | VERIFIED_STATIC | Unchanged | — |
| NF5-6 | VERIFIED_STATIC | Unchanged | — |
| NF5-7 | VERIFIED_STATIC | Unchanged | — |
| RF-1 | archive encoding | V6-E | V6-E |
| RF-2 | `owner.retry`; CG-1 predates the lane | CG-4; CG-1 attributed | V6-L |
| RF-3 | sub-helper placement | factory | V6-J |
| RF-4 | unconditional UNKNOWN append | phase-conditional append | V6-H |
| RF-5 | `KernelPeer` re-read on an owned duplicate | RC-10 branches | V6-I |
| RF-6 | X-5 record | corrected | V6-A.4 |
| RF-7 | worker-served IP bound | CG-2 | V6-B |
| RF-8 | PREPARED after DISPATCH_INTENT | PREPARED first | V6-H |
| RF-9 | v4:1801 stale | R6-4 | V6-L |
| RF-10 | CUSTODY_RETURNED after restart; no-escape premise | two regimes; OB-ESC | V6-F |
| RF-11 | Unknown/reattach circularity | V6-G | V6-G |
| RF-12 | later-WL contingent on D-4a | CG-3 | V6-C |
| RF-13 | H's per-agent mapping | H′ | V6-K |

The review's other concerns are answered too: the JSON overflow refusal class (V6-E.4), and its offered option of a fresh `flock` as no-holder evidence (adopted in V6-F.2).

---

## B. What v6 carries from v5, and how to read it

### B.1 Bound v5 slices

- v5 `SEAM-DESIGN.md` has 1628 lines and ends with a newline (observed). Its whole-file sha256 is `938c832d03df0910506756ec295acef86ae2cacba4d7b2478a09c6d27f3685cf`.
- Each slice's sha256 is that of the UTF-8 bytes of its lines, each followed by `\n`. A read-only script computed them (Appendix C).
- CARRIED_VERBATIM slices are part of v6 exactly. CARRIED_WITH_LINE_REPLACEMENTS slices are part of v6 with the listed lines replaced by the §B.2 text. Slice C5-B is v5's §B; it carries v4 through its own slice table (C4-…) with R5-1 … R5-17, so an R6 may also replace a v4 line inside a C4 slice, or a line of an R5 block's `v5:` text (RR6-4).

| Slice | v5 lines | sha256 | Disposition | Content |
|---|---|---|---|---|
| C5-B | 181-409 | `cbd690a4b25a7ed68ed1c72f63dec1a4ed5cef481aee52642b46c962257c56ee` | CARRIED_WITH_LINE_REPLACEMENTS (R6-1 … R6-5) | v5 §B: the C4 slice table, R5-1 … R5-17, W5-1, W5-2, v5's map and reading rules |
| C5-VA | 463-572 | `ea7943eb07496788ef97854458b997e874a34568cef817a1e4205fc81f4e3aa3` | CARRIED_WITH_LINE_REPLACEMENTS (R6-6, R6-7) | V5-A.2 … V5-A.6: kept exports, X-1 … X-10, current observations, selection, graph |
| C5-VB | 575-626 | `d248a3f6f7ac6af7c6ed768edffcdc43321c68db5d44fc43dc616209a6c56f28` | CARRIED_WITH_LINE_REPLACEMENTS (R6-8 … R6-11) | V5-B heading, V5-B.1 … V5-B.5 |
| C5-VC | 645-704 | `22fddc39049f02555fa5b85dfe479358ba1f629eeeddc3c4ce36c7de506b513e` | CARRIED_WITH_LINE_REPLACEMENTS (R6-12) | V5-C: premises, bounded rollback, `Number_Canonical` |
| C5-VE | 745-825 | `da99193dcd7fac3aae83265dbf0cb2209c48b1277b73ebd33de5fe69578574f6` | CARRIED_WITH_LINE_REPLACEMENTS (R6-13, R6-14) | V5-E: child protocol, surfaces, helper protocol |
| C5-VF | 828-1036 | `503a9a76fd24177fac3656874ab9f66bd4f8d97f59841364fa5f6f90d9fd447b` | CARRIED_WITH_LINE_REPLACEMENTS (R6-15 … R6-20) | V5-F: types, three relations, cross-conditions, Next, mutations, CAS, pending intents |
| C5-VG | 1039-1078 | `5390ebb82f5055ab1dc7538e5d8adc80b378b76d4744cc9f75bff9ec39be366e` | CARRIED_WITH_LINE_REPLACEMENTS (R6-21, R6-22) | V5-G: no-launch route, recovery routes |
| C5-VH | 1081-1131 | `ca19aa5bb54fb9fcc8efcb641e912750c5f1756043ab456c9e54bac99db50a63` | CARRIED_VERBATIM | V5-H (V4-REQ-H, closed at design level) |
| C5-VI | 1134-1234 | `de6cb4ff0508c5bcf2d18a1c8434df08a909b2850931de36089d3081d3d4deb2` | CARRIED_WITH_LINE_REPLACEMENTS (R6-23, R6-29) | V5-I: joins, presence, gates, RELAY, ordering |
| C5-VJ | 1237-1391 | `098b032a9d117fc66b433fc8dd7d7df0e4d81f508ef1b88901dfea5146196546` | CARRIED_VERBATIM | V5-J: DDL, provisioning, migration |
| C5-VK | 1394-1437 | `231573a82df1c4eb23ad191a5fa944a4724a44f7d572cbe9edf259acc04e7b3f` | CARRIED_VERBATIM | V5-K (V4-REQ-K and the C-API integration, closed at design level) |
| C5-VL | 1440-1486 | `f6d5e08b82ba04d5d87f95d41a648db6bb1d1a134173265c691c29d10eb51614` | CARRIED_WITH_LINE_REPLACEMENTS (R6-24 … R6-26) | V5-L: placement, progress, reattach, queue |
| C5-VMNOP | 1489-1548 | `cf864cc14c9663f05e28f4a089b5c14bda2d6577180cf84e9eee93c091061ca8` | CARRIED_WITH_LINE_REPLACEMENTS (R6-27, R6-28) | V5-M controls, V5-N measurements, V5-O open list, V5-P non-claims |

### B.2 Line replacements

Each replacement quotes the exact v5 or v4 line or lines, then gives the v6 text.

**R6-1 replaces v5 line 407 (in C5-B; RR5-7).** No reading rule neutralises carried text (V5-REQ-L).
```text
v5:
- **RR5-7.** v4's M8 (c) front generation-root stop is withdrawn (V5-F.5). Carried text that names it, or "an authorized `job.cancel` when no owner is reachable", has no effect; `job.cancel` is served by a store-custody owner under M8 (a). "QUEUED progress events" inside carried text are withdrawn (V5-L.4).
v6:
- **RR5-7.** Retired by v6 (R6-1). Every carried text that named v4's M8 (c) front stop, "an authorized `job.cancel` when no owner is reachable", or QUEUED progress events is now replaced by an explicit quotation: R5-7, R5-8, R5-9 and R5-10 in v5, and R6-5 (v4 line 1804) in v6. No reading rule neutralises carried text.
```

**R6-2 replaces v5 line 354 (in C5-B; R5-16's result, G-12).**
```text
v5:
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace, socket, SQLite and interpreter semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14 in §16, K-15 … K-21 in v3 V-O, K-22 and K-23 in v4 V4-N, K-24 … K-27 in v5 V5-N) or its installed-runtime check (RC-1 … RC-4 in v3 V-O, RC-5 and RC-6 in v4 V4-N, RC-7, RC-9 and RC-10 in v5 V5-N).
v6:
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace, socket, SQLite, loader and interpreter semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14 in §16, K-15 … K-21 in v3 V-O, K-22 and K-23 in v4 V4-N, K-24 … K-27 in v5 V5-N with K-27 as narrowed by v6 V6-M, K-28 in v6 V6-O) or its installed-runtime check (RC-1 … RC-4 in v3 V-O, RC-5 and RC-6 in v4 V4-N, RC-7, RC-9 and RC-10 in v5 V5-N, RC-11 and RC-12 in v6 V6-O).
```

**R6-3 replaces v5 line 362 (in C5-B; R5-17's result, OP-7).** The same range repair as R4-1, R4-5, R5-16 and R5-17; no operator item is added.
```text
v5:
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 (§16), K-15 … K-21 (v3 V-O), K-22 and K-23 (v4 V4-N) and K-24 … K-27 (v5 V5-N) in an authorized lab | §3–§9, v3 V-B … V-I, v4 V4-B … V4-L and v5 V5-B … V5-L runtime evidence |
v6:
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 (§16), K-15 … K-21 (v3 V-O), K-22 and K-23 (v4 V4-N), K-24 … K-27 (v5 V5-N, K-27 narrowed by v6 V6-M) and K-28 (v6 V6-O) in an authorized lab | §3–§9, v3 V-B … V-I, v4 V4-B … V4-L, v5 V5-B … V5-L and v6 V6-B … V6-M runtime evidence |
```

**R6-4 replaces v4 line 1801 (in C4-VMNOP, carried by C5-B).** The RQ-1 control agrees with v5 V5-B.5 (V5-REQ-L).
```text
v4:
- **RQ-1** (pure and lab). Windows W0 … W5 on the root route, each with its refusal or `Ready`, its U records, its P class and its recovery. The root route's guard order equals the serial route's, with the `DISPATCH_INTENT` boundary present and quarantine before `CUSTODY_ACK`.
v6:
- **RQ-1** (pure and lab). For IP operations: windows W0, W1, W4 and W5 on the serial route in the custody owner (the front, or the worker by FRESH or RELAY), each with exactly the serial route's refusal or `Ready`, U records, P class, recovery and cost, and with no `Record_Launch_Intent` or `Record_Running` call; for a worker-served IP request the physical bound actually used is recorded (CG-2, v6 V6-B). For WL operations: windows W0 … W5 on the root route, each with its refusal or `Ready`, U records, P class and recovery, and the differences of v5 V5-B.5 recorded. The root route keeps the serial route's steps 1–4 and 6, runs step 7 (the handler) in the worker, and keeps step 8, with the `DISPATCH_INTENT` boundary present and quarantine before `CUSTODY_ACK`; it has no step 5 (CG-1, v6 V6-L).
```

**R6-5 replaces v4 line 1804 (in C4-VMNOP, carried by C5-B).** An explicit quotation in place of RR5-7 (V5-REQ-L).
```text
v4:
- **V4-F** (pure). `Legal` and `Next` for every row of the root, request and descriptor tables. A REQUEST and a DESCRIPTOR subject with the same subject string do not collide on replay. `CUSTODY_CAS_STALE`; `CUSTODY_ALTERNATIVE_TAKEN`; an event of an older generation refused; the initial state admits only `PREPARED (1)`. M1, M2 and M3 refuse a non-owner. M6 lets the front spool in Stop_Intent. M8 admits the original owner cancellation, the helper's kill before GO and the M8 (c) stop, and refuses a stop on a deadline.
v6:
- **V4-F** (pure). `Legal` and `Next` for every row of the root, request and descriptor tables. A REQUEST and a DESCRIPTOR subject with the same subject string do not collide on replay. `CUSTODY_CAS_STALE`; `CUSTODY_ALTERNATIVE_TAKEN`; an event of an older generation refused; the initial state admits only `PREPARED (1)`. M1, M2 and M3 refuse a non-owner. M6 lets the front spool in Stop_Intent. M8 admits the original owner cancellation and the helper's kill before GO; it refuses a front stop of a worker-owned generation's root on `job.cancel` (v4's M8 (c), withdrawn in v5 V5-F.5), and refuses a stop on a deadline.
```

**R6-6 replaces v5 line 500 (in C5-VA).** `RootStateRec` equals `Root_State` and the root_state columns (V5-REQ-A).
```text
v5:
- Records: (1) `RootStateRec {present: uint8; generation: Qty; operation: Id; phase: uint8; before_unknown: uint8; owner: uint8; closure_ns, closure_outer, closure_raw, stop_intent, returned: uint8; unknown_cause: Dig; head: Dig}`; (2) `SubjectStateRec {kind: uint8; generation: Qty; subject: Id; subgeneration: Qty; phase: uint8; mode: uint8 (None, Fresh, Relay); position: OptQty; carried_from: OptQty; head: Dig}`; (3) `EventRec {kind: uint8; generation: Qty; operation: Id; subject_kind: uint8; subject: Id; subgeneration: Qty; actor: uint8; record_digest: Dig; event_id: Dig}`; (4) `EvidenceRec {kind: uint8; value: Id}`; (5) `MutationInput {actor: uint8; mutation: uint8; subject_kind: uint8; subject: Id; generation: Qty}`; (6) `PhaseResult {status: uint8; root_count: Qty; subject_count: Qty; allowed: uint8}`.
v6:
- Records: (1) `RootStateRec {present: uint8; generation: Qty; operation: Id; phase: uint8; before_unknown: uint8; owners_open: uint8; abort_class: uint8; launched, closure_ns, closure_outer, closure_raw, witness, settled, released_unlaunched: uint8; unknown_cause: Dig; reattach_epoch: Qty; head: Dig}`, field for field `Root_State` and the root_state columns (v6 V6-A.4); (2) `SubjectStateRec {kind: uint8; generation: Qty; subject: Id; subgeneration: Qty; phase: uint8; mode: uint8 (None, Fresh, Relay); position: OptQty; carried_from: OptQty; head: Dig}`; (3) `EventRec {kind: uint8; generation: Qty; operation: Id; subject_kind: uint8; subject: Id; subgeneration: Qty; actor: uint8; record_digest: Dig; event_id: Dig}`; (4) `EvidenceRec {kind: uint8; value: Id}`; (5) `MutationInput {actor: uint8; mutation: uint8; subject_kind: uint8; subject: Id; generation: Qty}`; (6) `PhaseResult {status: uint8; root_count: Qty; subject_count: Qty; allowed: uint8}`. Convention T (v6 V6-A.2).
```

**R6-7 replaces v5 line 518 (in C5-VA).** X-8's convention (V5-REQ-A).
```text
v5:
- Records: every V1 record of the same unit, unchanged and first (the V1 `PARAMETERS` roster of `rw/resource_child_execution.py:207`; the scoped records `N_Raw_*` of `:75-82`), then (k) `FactsV2 {base: O.RawFacts; selected: uint8; delegation: Dig; producer_a: Dig; producer_b: Dig}` and (k+1) `Selection {row_index: Qty; family: uint8}`.
v6:
- Records: every V1 record of the same unit, unchanged and first (the V1 `PARAMETERS` roster of `rw/resource_child_execution.py:207`; the scoped records `N_Raw_*` of `:75-82`), then (k) `FactsV2 {base: O.RawFacts; selected: uint8; delegation: Dig; producer_a: Dig; producer_b: Dig}` and (k+1) `Selection {row_index: Qty; family: uint8}`. Convention P (v6 V6-A.2): the V1 arguments unchanged and in their V1 order, then two appended roster arguments, `FactsV2` and `Selection`, each a pointer and an element count, immediately before the output argument.
```

**R6-8 replaces v5 line 594 (in C5-VB).** OW is not "unchanged": `owner.retry` is refused (V5-REQ-L).
```text
v5:
- **OW (owner):** `owner.retry`, `owner.adopt`, `owner.recover` (`:284`, `:731-741`). Never on the root route (`:724`); unchanged.
v6:
- **OW (owner):** `owner.retry`, `owner.adopt`, `owner.recover` (`:284`, `:731-741`). Never on the root route (`:724`). `owner.adopt` and `owner.recover` run their original owner branch unchanged. `owner.retry` is refused before any reservation with `OWNER_ORIGINAL_FULL_RESOURCE_ATTEMPT_ROUTE_UNINTEGRATED` (`:735-737`), a refusal inherited from the preimage: OPEN containment gap CG-4 (v6 V6-L).
```

**R6-9 replaces v5 line 599 (in C5-VB).** The cost equality is withdrawn for worker-served IP (V5-REQ-B).
```text
v5:
- **OW and IP** to `_invoke_serial` in whichever process owns custody: the front in FRONT_* phases; the worker, by FRESH transfer or RELAY, while it owns (V5-I). No IP operation ever launches a root unit. So the W2 and W3 refusal sites that the root launch adds do not exist for IP operations, and their durable outcomes, recovery and costs are the original serial route's.
v6:
- **OW and IP** to `_invoke_serial` in whichever process owns custody: the front in FRONT_* phases; the worker, by FRESH transfer or RELAY, while it owns (V5-I). No IP operation ever launches a root unit, so the W2 and W3 refusal sites that the root launch adds do not exist for IP operations. Front-served IP requests have the original serial route's durable outcomes, recovery and costs. Worker-served IP requests have its durable outcomes and recovery, but their handler runs in the coordinator inside the WL request's root unit, under the bound admitted for that WL request, so their physical-bound cost is not the original's (AO-5, AO-6 and AO-11, as for G): OPEN containment gap CG-2 (v6 V6-B).
```

**R6-10 replaces v5 line 600 (in C5-VB).** Later WL queueing is a containment gap, not a D-4a matter (V5-REQ-C).
```text
v5:
- **WL** to the root route, which launches the request's own unit and runs the handler in the worker with the dispatcher of V5-B.6, while the front owns. While a worker owns, a later WL request is queued for the next generation unless D-4a selects an option that serves it (V5-D, V5-L).
v6:
- **WL** to the root route, which launches the request's own unit and runs the handler in the worker with the dispatcher of v6 V6-D, while the front owns. While a worker owns, a later WL request is queued for the next generation: OPEN containment gap CG-3 against the original per-request concurrency (v6 V6-C), whose closure condition does not depend on D-4a.
```

**R6-11 replaces v5 line 625 (in C5-VB).**
```text
v5:
**Statement.** For IP operations the durable outcome, recovery and cost in every window are the serial route's, because they run on it. For WL operations W0 … W3 use the same native commands at the same refusal points as the original scoped launch, and v5 adds the custody events listed; W4 adds the handoff and its custody costs. These are differences, stated; RQ-1 stays OPEN until the positives and refusals of v3 V-B.9, V-B.10, V4-M and V5-M exist with proofs.
v6:
**Statement.** For front-served IP operations the durable outcome, recovery and cost in every window are the serial route's, because they run on it. For worker-served IP operations the durable outcome and recovery are the serial route's and the physical bound is not (CG-2). For WL operations W0 … W3 use the same native commands at the same refusal points as the original scoped launch, and v5 adds the custody events listed; W4 adds the handoff and its custody costs; a later WL request waits for g+1 (CG-3). These are differences, stated; RQ-1 stays OPEN until the positives and refusals of v3 V-B.9, V-B.10, V4-M (with R6-4), V5-M and V6-N exist with proofs.
```

**R6-12 replaces v5 line 693 (in C5-VC).** The archive does not store number text (V5-REQ-E).
```text
v5:
**Archive extraction.** `extract` returns the exact lexeme span; numbers are compared as lexemes after `Number_Canonical`, never through a binary64 value. `archive_equal` compares a JSON number with an archived number by the same lexical rule (the archive grammar of `rw/operation_capture.py:15-39` stores the canonical text), so the sign of −0.0 survives extraction and comparison.
v6:
**Archive extraction.** `extract` returns the exact lexeme span, and `Number_Canonical` compares lexemes. `archive_equal` compares against the actual archive encoding (v6 V6-E): an integer as its sign flag and minimal little-endian magnitude, a non-integer as the big-endian binary64 bits of `Round`, with the sign bit taken from `Sign (X)`, so −0.0 compares by its sign bit. The archive does not store number text; v5's statement that it did is withdrawn.
```

**R6-13 replaces v5 line 785 (in C5-VE).** Where the sub-helper is created (V5-REQ-J).
```text
v5:
| Sub-helper (one per child) | a fork of the root helper, outside the coordinator's namespaces; no exec | — | inherited | inherited | root, as the helper | held: its channel to the root helper; the child init's pidfd; go write end; report read end; the actor-credential receiving end with `SO_PASSCRED`; out, err and stdin-writer until sent in `HELD_CHILD`, then closed; the decision library mapped read-only from the descriptor it hashed (V5-E.3) |
v6:
| Sub-helper (one per child) | a fork of the child factory (v6 V6-J), which the root helper forks before its `unshare (CLONE_NEWPID)`, so the sub-helper is in the host PID and mount namespaces, outside the coordinator's; no exec | — | inherited from the factory | inherited | root, as the helper | held: its channel to the root helper (created by the factory and passed to the root helper); the child init's pidfd; go write end; report read end; the actor-credential receiving end with `SO_PASSCRED`; out, err and stdin-writer until sent in `HELD_CHILD`, then closed; the decision library loaded from the sealed copy it hashed (V5-E.3) |
```

**R6-14 replaces v5 line 816 (in C5-VE).** The material's layout (V5-REQ-A).
```text
v5:
5. **Decision.** The material is the exact argument memory the worker passed to its own `decide`: the arena bytes and each record array, in the export's `PARAMETERS` order (`rw/resource_child_execution.py:207`), with counts and strides. The sub-helper rebuilds the pointers and calls `decide` in mode `CHILD_ADMISSION`. Only `Child_Ready_Conjunction` gives `AGREE_CHILD`.
v6:
5. **Decision.** The material is the exact argument memory the worker passed to its own `decide`, in convention P and the layout of v6 V6-A.3: for each entry of the export's `PARAMETERS` roster except `Output` (`rw/resource_child_execution.py:207`), its kind (record, arena or roster), the size word passed (byte size, byte length or element count) and its bytes. Every span inside the records is an index into one of the two arenas, so the copy keeps its meaning and no pointer is rebuilt from the material. The sub-helper passes its own copies with the same size words and calls `decide` in mode `CHILD_ADMISSION`. Only `Child_Ready_Conjunction` gives `AGREE_CHILD`.
```

**R6-15 replaces v5 line 885 (in C5-VF).** `PREPARED` precedes machine admission (V5-REQ-H).
```text
v5:
| Front_Owned (g) | `PREPARED (g)` | Prepared | Front | a WL operation's RESERVED and `EFFECT_INTENT` heads (V5-B.5); no other operation starts a root |
v6:
| Front_Owned (g) | `PREPARED (g)` | Prepared | Front | a WL operation's RESERVED and `EFFECT_INTENT` heads (V5-B.5), its reservation and its original request observation; committed before machine admission and before `Record_Launch_Intent` (v6 V6-H); no other operation starts a root |
```

**R6-16 replaces v5 line 886 (in C5-VF).**
```text
v5:
| Prepared | `HELD` | Held | Front | authentic HELD frame; machine admission at DISPATCH; sets `Launched` |
v6:
| Prepared | `HELD` | Held | Front | authentic HELD frame; machine admission at DISPATCH, `Record_Launch_Intent` and `DISPATCH_INTENT` already committed; the record carries the full launch packet, launch reply and dispatch (moved from the lane's `PREPARED` record) and the namespace init's host pid and start tick (v6 V6-F.2); sets `Launched` |
```

**R6-17 replaces v5 line 902 (in C5-VF).** Reattachment is legal from Unknown (V5-REQ-G).
```text
v5:
| Worker_Owned … Worker_Relinquish | `WORKER_REATTACHED (n)` | unchanged; `Reattach_Epoch` = n | Worker | the handshake of V5-L.3: n is the current epoch + 1, and the front's MAC verifies |
v6:
| Worker_Owned … Worker_Relinquish, or Unknown with `Before_Unknown` in those | `WORKER_REATTACHED (n)` | unchanged; `Reattach_Epoch` = n | Worker | the handshake of V5-L.3: n is the current epoch + 1, and the front's MAC verifies; the record keeps the handshake transcript (v6 V6-G) |
```

**R6-18 replaces v5 line 903 (in C5-VF).** Custody-return evidence in both regimes (V5-REQ-F).
```text
v5:
| Worker_Owned … Worker_Relinquish, Front_Retained_Escrow, or Unknown with `Before_Unknown` in those | `CUSTODY_RETURNED` | Custody_Returned | Collector or Reconciler | the worker pidfd terminal **and** the root namespace-init pidfd terminal (K-24), both held by the front since HELD; no request or descriptor subject of g in Intake (XC-6) |
v6:
| Worker_Owned … Worker_Relinquish, Front_Retained_Escrow, or Unknown with `Before_Unknown` in those | `CUSTODY_RETURNED` | Custody_Returned | Collector or Reconciler | evidence E-CR of v6 V6-F: either (front alive since HELD) the worker pidfd terminal and the root namespace-init pidfd terminal (K-24), or (front restarted) the worker and namespace-init identities gone and a fresh exclusive `flock` held on every transferred lock file; in both, obligation OB-ESC; no request or descriptor subject of g in Intake (XC-6) |
```

**R6-19 replaces v5 line 909 (in C5-VF).** The durable route back from Unknown (V5-REQ-G).
```text
v5:
| Unknown | `RECONCILED`, then the event that native evidence determines | that event's target | Reconciler only (INV-C5) | authentic durable evidence; never EOF or a deadline alone |
v6:
| Unknown | `RECONCILED`, then the event that native evidence determines | that event's target | Reconciler only (INV-C5) | authentic durable evidence; never EOF or a deadline alone. For a cause of class C-CHANNEL or C-DEADLINE with `Before_Unknown` a worker phase, a committed `WORKER_REATTACHED (n)` after the `UNKNOWN` event, with the worker's identity live, is such evidence, and the target is `Before_Unknown` (v6 V6-G) |
```

**R6-20 replaces v5 line 962 (in C5-VF).**
```text
v5:
- **XC-4** (loss and reclaim). `REQUEST_LOST` and `DRAIN_RECLAIMED` need the worker pidfd terminal.
v6:
- **XC-4** (loss and reclaim). `REQUEST_LOST` and `DRAIN_RECLAIMED` need the worker gone: its pidfd terminal while the front holds it, or, after a front restart, its identity gone (v6 V6-F.2).
```

**R6-21 replaces v5 lines 1046-1048 (in C5-VG).** The no-launch route's preconditions hold against the code (V5-REQ-H).
```text
v5:
1. **Root.** `PREPARED (g)` committed; the WL operation's use is RESERVED with `EFFECT_INTENT` (`rw/protected_operations.py:746-749`).
2. **Failure before dispatch.** `Record_Launch_Intent` refuses (W2), or any step before `DISPATCH_INTENT` fails. The launch journal is `Never_Dispatched`; the facts satisfy `Never_Holds` (`core/resource_observation_classification.ads:96-102`), so the native class is `Never_Launched`.
3. **`HANDOFF_ABORT (g, Never_Dispatched)`** (Front; ACK set free; no `TRANSFER_SENT (g)`). It sets `Released_Unlaunched` only together with step 4's commit.
v6:
1. **Root.** `PREPARED (g)` committed before machine admission and before `Record_Launch_Intent` (v6 V6-H); the WL operation's use is RESERVED with `EFFECT_INTENT` (`rw/protected_operations.py:746-749`).
2. **Failure before dispatch.** Machine admission refuses, `Record_Launch_Intent` refuses (W2), or any step before `DISPATCH_INTENT` fails. The no-slot failure branch appends `UNKNOWN` to the launch journal only in the original's phases (v6 V6-H), so the launch journal stays `Never_Dispatched`; the facts satisfy `Never_Holds` (`core/resource_observation_classification.ads:96-102`), so the native class is `Never_Launched`.
3. **`HANDOFF_ABORT (g, Never_Dispatched)`** (Front; ACK set free; no `TRANSFER_SENT (g)`). It sets `Released_Unlaunched` only together with step 4's commit.
```

**R6-22 replaces v5 line 1074 (in C5-VG).** RT-28 in both regimes (V5-REQ-F).
```text
v5:
| RT-28 | root Worker_Owned … Worker_Relinquish, or Unknown from them; worker and namespace-init pidfds terminal; no `CLOSED_WITNESS` | the two pidfds (K-24); XC-6 | `CUSTODY_RETURNED (g)`; escrow claim; U by RT-21 … RT-24 if its row qualifies, otherwise native `QUARANTINE_USE` → `HISTORICAL_SETTLEMENT`; `FRONT_RECONSTRUCTION`; `FRONT_OWNED (g+1)`. The root row keeps its holds (`Retain_Uncertain`) until g's physical events settle it | per the U row's original mapping | Automatic; P by owner if closure never arrives |
v6:
| RT-28 | root Worker_Owned … Worker_Relinquish, or Unknown from them; worker gone; no `CLOSED_WITNESS` | evidence E-CR (v6 V6-F): the two pidfds (K-24) while the front holds them, or after a front restart both identities gone and the fresh `flock`s; OB-ESC; XC-6 | `CUSTODY_RETURNED (g)`; the escrow claim, or after a restart the fresh locks as the reconstruction locks; U by RT-21 … RT-24 if its row qualifies, otherwise native `QUARANTINE_USE` → `HISTORICAL_SETTLEMENT`; `FRONT_RECONSTRUCTION`; `FRONT_OWNED (g+1)`. The root row keeps its holds (`Retain_Uncertain`) until g's physical events settle it | per the U row's original mapping | Automatic; P by owner if closure never arrives |
```

**R6-23 replaces v5 line 1225 (in C5-VI).** Transport loss adds no refusal (V5-REQ-I; the condition on 09.4).
```text
v5:
**Transport loss: the legal fallback state.** If the channel closes or a frame fails `relay_frame`, the gate use cannot complete. A RELAY client connection lives only in the front, so a front that lost the channel has lost the client connection too (its process ended, or it is reattaching after a restart). The worker therefore raises at that gate exactly what the original re-read raises when the client connection is gone **[unverified reasoning, RC-10: the exception `KernelPeer.observation ()` raises for a closed connection]**, and the original exception path follows, as for a client that disconnects mid-request in the original. No gate waits on a deadline, nothing is fabricated, and the request's custody events record the outcome (`REQUEST_RESPONDED` with the error response, or `REQUEST_LOST` if the worker dies).
v6:
**Transport loss: the legal fallback state.** If the channel closes or a frame fails `relay_frame`, the gate use cannot complete over RELAY. A RELAY client connection lives only in the front, so a front that lost the channel has lost the client connection too. The worker then does what the original re-read does when its client has gone, which RC-10 settles before B-RECV is reviewed (v6 V6-I.1): (a) if the original re-read raises, the worker raises the same class, code, message and details at that gate, and the original exception path follows; (b) if it raises nothing (it re-reads an owned descriptor, `rw/client_peer.py:73-90`), the worker takes as the gate's re-read the last authenticated front re-read for (g, r, s), which is exactly what the original re-read would return, and continues, adding no refusal and no quarantine; the response is produced and `REQUEST_RESPONDED` committed, and only its write is lost, as the original `_send` drops writes to a closed writer (`rw/daemon.py:394-400`). No gate waits on a deadline, nothing is fabricated, and `REQUEST_LOST` applies if the worker dies.
```

**R6-24 replaces v5 lines 1461-1464 (in C5-VL).** Progress rows in both custody regimes and from Unknown (V5-REQ-F, V5-REQ-G).
```text
v5:
| Worker owns, channel lost (front restarted, or the channel closed), worker alive | queued; then the worker | the reattach | `WORKER_REATTACHED (n)` (V5-L.3) | see the wedged row |
| Worker owns, alive, does not complete the reattach | queued | — | none | **stated difference**: this is the counterpart of an original daemon that does not respond, and nothing in the design ends it; the operator's existing remedies apply, and it is an OPEN fault-campaign item (OP-8). No deadline settles anything |
| Worker dead | queued; then the front of g+1 | collection of custody | `CUSTODY_RETURNED (g)` on the worker and namespace-init pidfds (kernel events, K-24), after `REQUEST_LOST` and `DRAIN_RECLAIMED`; no closure evidence needed | if a process in the coordinator's namespace keeps init alive, custody stays with the generation until it exits; stated condition |
| Unknown | queued | evidence | the Reconciler's `RECONCILED` on: a reattach (back to `Before_Unknown`), or the two pidfds terminal (`CUSTODY_RETURNED`) | as the two rows above |
v6:
| Worker owns, channel lost (front restarted, or the channel closed), worker alive | queued; then the worker | the reattach | `WORKER_REATTACHED (n)` (V5-L.3), legal also from Unknown (v6 V6-G) | see the wedged row |
| Worker owns, alive, does not complete the reattach | queued, `job.cancel` included | — | none | **stated difference**: this is the counterpart of an original daemon that does not respond, and nothing in the design ends it; the operator's existing remedies apply, and it is an OPEN fault-campaign item (OP-8). No deadline settles anything; 06.3's cancel progress stays OPEN for this case |
| Worker dead | queued; then the front of g+1 | collection of custody | `CUSTODY_RETURNED (g)` on evidence E-CR (v6 V6-F): the two pidfds while the front holds them (K-24), or after a front restart both identities gone and the fresh `flock`s; after `REQUEST_LOST` and `DRAIN_RECLAIMED`; no closure evidence needed | if a process in the coordinator's namespace keeps init alive, or holds a transferred lock, custody stays with the generation until it exits; stated condition, and the second is a violation of OB-ESC |
| Unknown | queued; the worker mutates nothing and waits at its refused choke point (v6 V6-G) | evidence | the Reconciler's `RECONCILED` on: a committed `WORKER_REATTACHED` with the worker live (back to `Before_Unknown`), or evidence E-CR (`CUSTODY_RETURNED`) | as the rows above |
```

**R6-25 replaces v5 line 1467 (in C5-VL).** (V5-REQ-C.)
```text
v5:
| A later WL request while a worker owns | queued for g+1, unless D-4a selects an option such as H (V5-D) | until g+1 | `FRONT_OWNED (g+1)` | **stated progress difference**, OPEN with D-4a |
v6:
| A later WL request while a worker owns | queued for g+1 | until g+1 | `FRONT_OWNED (g+1)` | **OPEN containment gap CG-3** against the original per-request concurrency (v6 V6-C); its closure condition does not depend on D-4a, and H′ (v6 V6-K) meets it at design level |
```

**R6-26 replaces v5 line 1479 (in C5-VL).**
```text
v5:
- **Handshake,** in RELAY framing under `DOMAIN_REATTACH` = `worldline.root-worker-reattach-v1` followed by one zero byte, all MACs `Hmac_Sha256 (K, DOMAIN_REATTACH ‖ …)` verified natively (S2H): front `HELLO {g, seen_epoch, nonce_f}`; worker `CHALLENGE {g, nonce_f, nonce_w, current_epoch}`; front `PROOF {g, nonce_f, nonce_w, current_epoch + 1}`; the worker requires its peer's `SO_PEERCRED` uid 0, verifies the MAC, commits `WORKER_REATTACHED (current_epoch + 1)` (M4, `Legal` per V5-F.2) and answers `READY {n}`. The new connection is then the transfer and RELAY channel for epoch n; frames of earlier epochs are refused.
v6:
- **Handshake,** in RELAY framing under `DOMAIN_REATTACH` = `worldline.root-worker-reattach-v1` followed by one zero byte, all MACs `Hmac_Sha256 (K, DOMAIN_REATTACH ‖ …)` verified natively (S2H): front `HELLO {g, seen_epoch, nonce_f}`; worker `CHALLENGE {g, nonce_f, nonce_w, current_epoch}`; front `PROOF {g, nonce_f, nonce_w, current_epoch + 1}`; the worker requires its peer's `SO_PEERCRED` uid 0, verifies the MAC, commits `WORKER_REATTACHED (current_epoch + 1)` (M4, `Legal` per V5-F.2 as replaced by R6-17, so also while the root is Unknown with a worker `Before_Unknown`) and answers `READY {n}`. The new connection is then the transfer and RELAY channel for epoch n; frames of earlier epochs are refused.
```

**R6-27 replaces v5 line 1515 (in C5-VMNOP).** K-27 split (V5-REQ-M).
```text
v5:
| K-27 | Loading a library through `/proc/self/fd/N` of a sealed `memfd` maps exactly the sealed bytes | V5-E.3 |
v6:
| K-27 | A sealed `memfd` (`F_SEAL_WRITE`, `F_SEAL_SHRINK`, `F_SEAL_GROW`) cannot be changed by any holder, its creator included, and mapping it maps exactly its sealed bytes. The dynamic loader's part is RC-11, lead-owned (v6 V6-M) | V5-E.3 |
```

**R6-28 replaces v5 line 1544 (in C5-VMNOP).**
```text
v5:
- No accounting option, cap, prerequisite or policy field is selected or added. H is offered for D-4a, not chosen.
v6:
- No accounting option, cap, prerequisite or policy field is selected or added. H′ (v6 V6-K) is the design offered to close CG-2 and CG-3; the author does not adopt it, and any authoritative resource-policy change stays with D-4a, for which none is proposed.
```

**R6-29 replaces v5 line 1200 (in C5-VI).** (V5-REQ-C.)
```text
v5:
| `rw/protected_scoped_resource_runtime.py:625` `lifecycle_packet` | custody owner | RETAINED | FRESH or RELAY when a transferred WL request launches under a selected D-4a option | HISTORICAL | `Row_Request_Capture` | the operation's own head |
v6:
| `rw/protected_scoped_resource_runtime.py:625` `lifecycle_packet` | custody owner | RETAINED | FRESH or RELAY when a transferred WL request launches on a route that meets CG-3's closure condition (v6 V6-C) | HISTORICAL | `Row_Request_Capture` | the operation's own head |
```

### B.3 Superseded v5 text

| v5 lines | v5 content | Status in v6 |
|---|---|---|
| 1-178 | Header; §A.1 … §A.8 (answers to the v4 review) | Superseded by the v6 header and §A. History, not normative. |
| 412-446 | §C truth boundary, bases, labels, numbers | v6 §C |
| 449-461 | V5-A heading; V5-A.1 "one wire convention" | V6-A.1, V6-A.2 |
| 627-642 | V5-B.6 dispatcher and CG-1 | V6-D (dispatcher), V6-L (CG-1) |
| 707-742 | V5-D (option H and the comparison) | V6-K |
| 1551-1628 | Appendices A … D | v6 Appendices A … D |

Every other v5 line outside the §B.1 slices is a separator or an empty line. v5's withdrawals W5-1 and W5-2 stay in force (inside C5-B). v6 makes no new withdrawal.

### B.4 Reading rules

- **RR6-1.** Inside carried v5 slices, v5's reading rules RR5-1 … RR5-8 (in C5-B; RR5-7 as replaced by R6-1) apply, and the aliases are those of v6 §C.2.
- **RR6-2.** A reference inside carried text to a superseded v5 section resolves through §B.3: V5-A.1 → V6-A.1 and V6-A.2; V5-B.6 → V6-D (the dispatcher) and V6-L (CG-1); V5-D, V5-D.1, V5-D.2 → V6-K; v5 §A, §C and the appendices → v6 §A, §C and the appendices.
- **RR6-3.** "v5 X" inside an R6 text means v5 section X as carried; "v6 Y" means this file's section Y.
- **RR6-4.** An R6 that replaces a line of an R5 block's `v5:` text changes that R5 replacement's result; the block's `v4:` text is unchanged. An R6 that replaces a v4 line names the C4 slice that contains it; no R6 replaces a line that an R5 replaces.
- **RR6-5.** Numbers inside carried slices keep their status: observed, or JACKAL exact (v2 J01 … J18; v5 J5-1 … J5-4). They are not re-derived.
- **RR6-6.** "AUTHOR-NOTES" inside a carried v5 slice means v5's `AUTHOR-NOTES.md` (`d6e16bdf…b836`).
- **RR6-7.** Inside carried text, `archive_equal` means the operation of V6-E; "custody-return evidence" means E-CR of V6-F; "the dispatcher" means the interface of V6-D. These rules name definitions; they do not neutralise any sentence.

---

## C. Truth boundary, bases and method

### C.1 What was done

- **Reading only.** The Read tool and read-only Bash (`sed -n`, `awk`, `grep`, `sha256sum`, `wc`, `cut`, `nl`, `command ls`, `test -e`, and Python scripts on standard input that read files and printed to standard output). No output was redirected to a file; no git command was run. Details: AUTHOR-NOTES §2.
- **Not run.** No compiler, prover, test, WORLDLINE, COSMOGONY or root-worker code (nothing imported or executed), service, `systemctl`, sudo, namespace, project-vault or restic. Nothing under `/srv`.
- **Not read.** `WT/packets/capi-pk0/`; `WT/designs/claude-root-worker-seam-design-v5/review/gpt61-v1` and anything under `review-records/`; the v5 review's `raw-final-message.txt` (not in the freeze); `~/.local/share/sia/.gbrain/`; any session transcript. The lane draft and its preimage were read and not changed.
- **SIA.** One `sia.ask` at the start of this task; nothing from it is used as evidence (AUTHOR-NOTES §3). No SIA note was written.
- **Skills.** The eight Ada skills were loaded in this session before Ada reading: `ada`, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`, `ada-2005-amendment`, `ada-high-integrity`.

### C.2 Bases (aliases)

| Alias | Path |
|---|---|
| `W` | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow` |
| `WT` | `W/work/claude-lead-isolation-v1/wt-1` |
| `L` | `W/work/protected-original-root-worker-repair-v1` (the draft lane) |
| `R` | `L/source`. Unprefixed `core/…`, `runtime/…` and `protected-*/…` paths are relative to `R`. |
| `rw/` | `R/runtime/worldline/` |
| `pre/` | `L/preimage/runtime/worldline/` (the lane's immutable primary copy, `L/handoff-to-claude-v1-retry1/HANDOFF.md`) |
| `C1` | `R/protected-root/native_root_worker_supervisor_v1.c` |
| `D2` … `D5` | `WT/designs/claude-root-worker-seam-design-v2` … `-v5`; `D5R` is `D5/review/claude-v1` |
| `CAPI5`, `CAPI6` | `WT/designs/claude-capi-boundary-design-v5`, `-v6` |
| `S5` | `W/work/claude-composition-v5-beta/source` |
| `P1/` | `W/outputs/claude-phase1-handoff-20261004/` |
| `D5:n`, `D4:n` | v5 or v4 `SEAM-DESIGN.md`, line n |

### C.3 Status labels

As v5 §C.3 (and v4 §C.3): OBSERVED; STATIC_REASONING; [unverified reasoning] naming a K or RC item; (bound to the sealed CAPI6R); DESIGN; OPEN.

### C.4 Numbers

Line numbers, counts, sizes and hashes in this document are observed. No numeral in v6 was derived by arithmetic, so no JACKAL call was made for v6 (`jackal.json`). v5's J5-1 … J5-4 are carried with their status (exact, lane `rat`, `formal=false`) inside C5-VC.

---

## V6-A. The actual ABI conventions, each export's convention, the material layout, and RootStateRec (V5-REQ-A; 01.1, 02.3, 04.3, 11.1, 12.1; D-1a, D-2a, D-5a, D-9a)

Carried: v5 V5-A.2 … V5-A.6 (C5-VA with R6-6, R6-7). V6-A.1 and V6-A.2 replace v5 V5-A.1, which called one convention "observed" when the existing exports use two.

### V6-A.1 Version, layout and return, as observed

- **Version.** `uint32_t wl_<unit>_version_v<N> (void)` returns N; every wrapper refuses another value with `CoreUnavailable` (for example `rw/resource_child_execution.py:113`, `rw/canonical_exchange_kernel.py:32`).
- **Layout.** `long wl_<unit>_layout_v<N> (uint32_t kind, uint32_t field)`: field 0 is the record's size, field 1 its alignment, field k ≥ 2 the offset of its (k−1)th field. Record kinds are numbered from 0 by the child export (`for kind,(_name,typ) in enumerate(_LAYOUT)`, `rw/resource_child_execution.py:114`), from 1 by the exchange and chain exports (`enumerate(…, 1)`, `rw/canonical_exchange_kernel.py:33`; `rw/chain_authority.py:69`), and by explicit kind numbers in the scoped ledger's `_LAYOUT` (`rw/resource_scoped_run_ledger.py:310`).
- **Return.** 0 means the result record was written; any other value is a transport refusal with no decision, which every wrapper raises as `CoreUnavailable` (`rw/canonical_exchange_kernel.py:66`; `rw/chain_authority.py:101-102`; `rw/resource_scoped_run_ledger.py:363`; `rw/resource_child_execution.py:195`).
- **Primitive records,** as v5 stated: `L.RawId`, `L.RawQuantity`, `L.RawEpoch`, `_Digest`. A span's `first` and `length` are indices into the arena the call passes, never machine pointers.

### V6-A.2 The two entry conventions, and the one each export uses

**Convention P (pairs).** Every argument is a pointer followed by one `size_t` word. The word is a record's byte size (`C.sizeof`) for a single record, the arena's byte length for an arena, and the **element count** for a roster array (`L._extent (count)`). Observed:
- `wl_resource_child_execution_decide_v1`: `[c_void_p, c_size_t]` repeated for each `PARAMETERS` entry, in that order, `Input` and `Arena` first and `Output` last (`rw/resource_child_execution.py:121`, `:207`; built at `:186-193`).
- `wl_resource_scoped_run_ledger_{check,validate,classify}_v1`: the packet record, the arena, one (array, count) pair per `_ROSTERS` entry, the result record (`rw/resource_scoped_run_ledger.py:316-321`; built at `:356-361`).

**Convention T (pairs and triples).** The Input record pair, the Arena pair, then one triple per roster, (pointer, element count, total byte size), then the Result record pair. Observed:
- `wl_canonical_exchange_decide_v1`, eight triples (`rw/canonical_exchange_kernel.py:37`; built at `:62-65`);
- `wl_canonical_operation_decide_v1` and `wl_operation_authority_decide_v1`, four triples each (`rw/canonical_operation_kernel.py:26`; `rw/operation_authority_kernel.py:77`);
- `wl_canonical_owner_completion_decide_v1`, the exchange's and the authority's triples in that order (`rw/canonical_owner_completion_kernel.py:38-39`);
- `wl_chain_authority_replay_v1`, a variant with no arena: the Anchors pair, one rows triple, the Result pair (`rw/chain_authority.py:75-76`, called at `:98-100`).

The third word of a triple is the total byte size of the array (`C.sizeof (item)` of a ctypes array), not a stride; v5's word "stride" is corrected here.

**Each new and successor export's convention, fixed:**

| Export | Convention | Arguments, in order |
|---|---|---|
| X-1 `wl_source_json_*_v1` | T | the entry's Input record (`JsonInput`, `NumberInput` or `ArchiveInput`), the Arena, the `PathStep` triple (`extract` only), `JsonResult` |
| X-2 `wl_roster_join_join_v1` | T | `RosterInput`, Arena, `RosterEntry` triple, `RosterResult` |
| X-3 `wl_root_crosswalk_decode_v1` | T | `CrosswalkInput`, Arena, `ChildPlan` triple, `HeaderData` triple, `CrosswalkResult` |
| X-4 `wl_custody_chain_verify_v2` | T | `ChainInput`, Arena, `EventRow` triple, `ChainResult` |
| X-5 `wl_root_custody_phase_*_v1` | T, with output triples | `legal`: `EventRec`, Arena, `RootStateRec`, `SubjectStateRec` and `EvidenceRec` triples, `PhaseResult`. `next`: the same, then an output `RootStateRec` triple and an output `SubjectStateRec` triple (writable, count = capacity), then an output-arena pair (pointer, byte capacity), then `PhaseResult`. `fold`: Arena, the `EventRow` triple, the stored `RootStateRec` and `SubjectStateRec` triples, the same outputs, `PhaseResult`. `mutation_allowed`: `MutationInput`, Arena, the two state triples, `PhaseResult` |
| X-6 `wl_requester_correspondence_*_v1` | T | `RequesterOperands` or `RelayFrameInput`, Arena, `JoinResult` (no roster) |
| X-7 `wl_child_event_legal_v1` | T | `ChildEventRec`, Arena, prior `ChildEventRec` triple, `ChildResult` |
| X-8 V2 successors of the scoped-ledger, observation and child exports | **P**, as their V1 exports (R6-7) | the V1 arguments unchanged, then a `FactsV2` (pointer, count) pair and a `Selection` (pointer, count) pair, then the output record |
| X-9 `wl_scoped_canonical_operation_decide_v1` and `_v2` | T, as `wl_canonical_operation_decide_v1` | `ScopedOperationInput`, Arena, triples for frames, rows, projection, buckets, natives and facts (and for `_v2` `FactsV2` and `Selection`), the result |
| X-10 exchange successor | T, as `wl_canonical_exchange_decide_v1` | its Input, Arena, the eight exchange triples, then frames, projection and buckets triples, Result |
| X-10 owner-completion successor | T, as `wl_canonical_owner_completion_decide_v1` | its Input, Arena, the exchange successor's triples, the authority triples, Result |

**Output capacity, no negotiation.** v5's `WL_ABI_CAPACITY` retry is withdrawn; it was a new mechanism that v5 had labelled as observed. `next` and `fold` write only rows whose number the wrapper knows from the inputs, and new quantity bytes only for a generation successor. The successor of an n-byte magnitude needs at most n + 1 bytes **[static reasoning]**. So the wrapper passes output rosters and an output arena sized from the inputs. The native unit reports `Capacity_Short` in `PhaseResult.status` only if the wrapper broke that rule, which is a wrapper defect and not a refusal of any input.

### V6-A.3 The sub-helper's material, byte for byte

The material is convention P's argument memory, serialized. All integers are little-endian.
1. 4 bytes `WLMP`; a 16-bit version, 1; a 16-bit export version (1 for `decide_v1`, 2 for `decide_v2`); a 32-bit count m of serialized parameters, which is the export's `PARAMETERS` roster without `Output`.
2. For each serialized parameter, in `PARAMETERS` order: a 32-bit index; an 8-bit kind (0 record, 1 arena, 2 roster); a 64-bit size word, exactly the value passed to `decide`; a 64-bit byte length (the size word for a record or an arena; the size word times the element's layout size for a roster); then that many bytes.
3. The material digest m is the SHA-256 of the whole byte string (V5-E.3).

The sub-helper checks the magic and versions; that m equals its own compiled roster's length without `Output`; every index in order; every kind against its own roster table; every record's size against `layout (kind, 0)`; and every byte length against the size word. Spans are arena indices, so the copies keep their meaning. The sub-helper calls `decide` with pointers to its own copies, the same size words, and its own output record.

### V6-A.4 `RootStateRec`, `Root_State` and the root_state columns

| `RootStateRec` field (R6-6) | `Root_State` (v5 V5-F.1) | root_state column (v5 V5-J.2) |
|---|---|---|
| `present: uint8` | the row exists | the row exists |
| `generation: Qty` | `Generation` | `generation` BLOB |
| `operation: Id` | `Operation` | `operation` TEXT |
| `phase: uint8` | `Phase` (`'Pos`) | `phase` TEXT, the phase name |
| `before_unknown: uint8` | `Before_Unknown`, meaningful only when `Phase = Unknown` | `before_unknown` TEXT or NULL; the record holds the `'Pos`, or 255 for NULL |
| `owners_open: uint8` | `Owners_Open` | `owners_open` 0 or 1 |
| `abort_class: uint8` | `Abort`, meaningful from Handoff_Aborted | `abort_class` TEXT or NULL; `'Pos`, or 255 for NULL |
| `launched`, `closure_ns`, `closure_outer`, `closure_raw`, `witness`, `settled`, `released_unlaunched: uint8` | the seven `Physical_Flags` fields | the seven 0-or-1 columns of the same names |
| `unknown_cause: Dig` (`present` 0 for absent) | `Unknown_Cause : Optional_Digest` | `unknown_cause` 64-hex TEXT or NULL |
| `reattach_epoch: Qty` | `Reattach_Epoch` | `reattach_epoch` BLOB |
| `head: Dig` | `Head` | `head_event` TEXT |

`Owner` is not stored. It is a function of the state (`Owner_Root`, v5 V5-F.2), in the type, the record and the DDL alike. v5's `owner`, `stop_intent` and `returned` fields are gone. X-5 `fold` compares every field above, so a state row that differs from the fold in any column is refused (RT-14 class).

---

## V6-B. Worker-served IP requests: containment gap CG-2 (V5-REQ-B; 01.7; D-1a, D-1b, D-4a)

**What happens (static).** While a worker owns generation g, an IP request is served by the worker (V5-B.5 as R6-9). Its handler runs in the coordinator. The coordinator is the main workload of g's root unit, which the front launched with the properties of the **WL request's** plan: `handler_plan (self.front, capture['resource_intent'].bound)` (`rw/protected_root_resource.py:38`), its policy (`:50`), and `--property=` for each of `plan['systemd_properties']` (`:68-71`). The IP handler's CPU, memory and tasks therefore count against the bound admitted for that WL request. This is G's handler-bound gap: AO-5 and AO-6 for handler code, and AO-11, because an IP handler can exhaust a bound admitted for another request and so kill admitted work.

**Withdrawn.** The cost equality for worker-served IP requests (R6-9, R6-11). Front-served IP requests keep it.

**CG-2 (OPEN containment gap).**
- **Gap.** A worker-served IP request uses a physical bound admitted for another request.
- **Interim behaviour.** Worker-served IP requests are still served; no refusal is added. The physical bound each one actually used is recorded (control V6-N.B), so the gap is visible and never counted as preserved behaviour.
- **Closure condition** (stated against the original obligation, not against any selection): every IP request served while a worker owns runs its handler under a physical bound that is either admitted for that same request or is the bound the original gives handler code, the daemon service's own. This must be shown by controls on matching source, by RC-9's read-back of the installed service's properties, and by the correspondence CJ-H-3.
- **Independence from D-4a.** The gap and its closure condition do not depend on D-4a. D-4a cannot waive or close it. Any authoritative resource-policy change that a closing route might need would be prepared as an exact package for D-4a; v6 proposes none.
- **A design that meets the condition:** H′ (V6-K). Its coordinator runs handler code under the installed service's own limits and holds no request's reservation. Whether H′ is adopted is for the lead (§V6-K.4). The author does not adopt it.

---

## V6-C. Later WL requests: containment gap CG-3 (V5-REQ-C; 06.4; D-4a)

**What happens (static).** The first WL operation's detached jobs keep the worker owning g after the initial result (`rw/protected_root_worker.py:184-190`). While it owns, a later WL request is queued for g+1 (V5-B.5 as R6-10; V5-L.2 as R6-25). It can therefore wait for unrelated jobs to finish. The original serves it concurrently with them, and P1 requires the "original per-request concurrency" (`P1/HANDOFF.md:115`).

**CG-3 (OPEN containment gap).**
- **Gap.** A WL request accepted while another generation's detached jobs run waits for g+1.
- **Interim behaviour.** It stays queued, durably, with no refusal (V5-L.4). The queueing is recorded per request (control V6-N.C) and never counted as preserved behaviour.
- **Closure condition:** every WL request accepted while earlier detached jobs run is admitted, reserved, launched and served concurrently with them, under its own reservation and its own physical bound, with no wait for a later generation. This must be shown by controls on matching source.
- **Independence from D-4a.** As for CG-2: D-4a can neither waive nor close it, and no policy change is proposed.
- **A design that meets the condition:** H′ (V6-K). Each WL request gets its own request-root unit while the service-class coordinator keeps serving.

---

## V6-D. The dispatcher's complete interface (V5-REQ-D; 03.3; D-5a)

Replaces v5 V5-B.6's dispatcher paragraphs (RR6-2). The dispatcher serves the root's own WL operation, and under H′ every WL request. The runner's code is unchanged; every attribute and method it uses was found by `grep` over `rw/runner.py` (NF5-2's evidence).

**`WorkerSystemdDispatcher` and `DispatchedProcess`:**

| Runner use (`rw/runner.py`) | Original (`rw/linux/systemd.py`) | Dispatcher behaviour | Original exceptions kept | Correspondence |
|---|---|---|---|---|
| `systemd.launch (instance_id, argv, description=…, nice=…, resource_properties=…)` (`:697-703`) | `launch` (`:156-234`): argv check, property checks, `Nice`, restart policy, `verify_manager`, then `systemd-run --user --pipe … --collect --service-type=exec` with `KillMode=control-group`, `SendSIGKILL=yes`, `TimeoutStopSec=10s`, `NoNewPrivileges`, `PrivateTmp=no`, `UMask=0022` | the same argument checks in the same order. The helper channel's liveness takes `verify_manager`'s place. Then one child task (V5-E.1). The leaf unit name is `self.unit_name (instance_id)`, the same string the original uses. The resource properties become the leaf's cgroup limits. `no_new_privs`, umask `0022` and the `Nice` value are applied by child init before exec. The stop semantics are those of the properties above (SIGTERM to the leaf, then `cgroup.kill` after the same stop timeout) | `INVALID_AGENT_COMMAND`, `RESOURCE_POLICY_INVALID`, `INVALID_PRIORITY`, `INVALID_RESTART_POLICY`; a helper refusal of `CREATE_CHILD` before any child exists is `SYSTEMD_LAUNCH_FAILED` with the unit, as a spawn failure is (`:232-233`) | CJ-DISP-1, CJ-DISP-6 |
| `unit.unit` (`:707`, `:808`, `:831`, and others) | the unit name | the leaf unit name | — | CJ-DISP-1 |
| `unit.pid` (`:804`) | `MainPID` if positive, else `None` (`:51-54`) | the actor's host pid from the relayed measurement once the actor has exec'd and until `CLOSED_CHILD`, else `None` | — | CJ-DISP-1 |
| `unit.launcher.wait ()` (`:276`) | `Popen.wait ()` of `systemd-run --pipe` | blocks until `CLOSED_CHILD`; returns the integer `systemd-run --pipe` returns for the same main-process status, or for a unit that never started (RC-12) | — | CJ-DISP-1, RC-12 |
| `unit.launcher.stdin` (`:905-908`), `stdout` (`:837-844`), `stderr` (`:881-891`), and `getattr (unit.launcher, name, None)` for those three (`:359`, `:390`) | the launcher's pipes | binary file objects with the same names over the child's stdin write end and out and err read ends: `write` and `close` on stdin, so EOF follows the last-writer rule (V4-H.5); line iteration on stdout; `read (n)` on stderr | — | CJ-DISP-1 |
| `systemd.stop (unit)` (`:312`, `:481`, `:483`, `:738`, `:817`, `:827`) | `stop` (`:717`), with `_validate_unit` (`:150-153`) | the same validation, then `STOP_UNIT` for the leaf (M8 (a)) | `FOREIGN_SYSTEMD_UNIT` | CJ-DISP-1, CJ-DISP-2 |
| `systemd.outcome (unit, exit_code, stopped=…, _raw_observer=…)` (`:342-347`) | `outcome` (`:623-714`) | returns a dict with exactly the original keys, `kind`, `unit`, `source`, `launcherExit`, `started`, `supervisionEvidence`, `stoppedByManager`, `exitCode`, `exitStatus`, `result`, `windowMilliseconds`, `events`, `launcherStderr`, as follows. **`kind`:** `SUPERVISED` exactly when `CHILD_READY` is committed and `CLOSED_CHILD` reports the exec released (the counterpart of the manager's started or process-exit entry); `LAUNCH_FAILED` when the actor never exec'd and the launcher exit is non-zero; otherwise `INDETERMINATE`, including when no `CLOSED_CHILD` frame exists. **`source`:** `child-closure`, or `child-closure-unavailable` when the frames cannot be read. **`started`:** `kind = SUPERVISED`. **`supervisionEvidence`:** `child-ready-and-closed` or `None`. **`stoppedByManager`:** a `STOP_UNIT` was executed for the leaf. **`exitCode` and `exitStatus`:** from the main status in `CLOSED_CHILD`. **`result`:** `stopped` after `STOP_UNIT`; `oom-kill` when the leaf's `memory.events` reports an OOM kill (the runner tests this value, `:937-938`); `failure` for a non-zero main status; `success` when started with launcher exit 0; otherwise `None`. **`windowMilliseconds`:** the original adapter's value. **`events`:** the closure-frame records. **`launcherStderr`:** the helper's diagnostic text, truncated as the original truncates. `_raw_observer` is called with (ordinal, record) for each acquired frame, as the original calls it | the original `UNIT_LAUNCH_FAILED` raised by the runner (`:944-950`) follows from `kind` unchanged | CJ-DISP-4 |
| `systemd.effective_limits`, `systemd.resource_telemetry` through `systemd_call (provider, unit, cancel_event=…)` (`:746`, `:761`, `:780`) | `:472-492` and following | dicts of the same shapes and `state` values (`OBSERVED`, `UNIT_GONE`, `UNAVAILABLE`). The `kernel` values come from the leaf's cgroup files, read through the read-only view. The `systemd` sub-dict's values are `None`, because a leaf cgroup has no manager properties | cancellation through `systemd_call` unchanged | CJ-DISP-5 |
| the runner's cancel (`:471-483`) | `controller_call` branch for an exact `SystemdProcess` | a `DispatchedProcess` takes the plain `self.systemd.stop` branch | — | CJ-DISP-2 |
| `guard.attach_unit (unit.unit)` (`:707`) | the admission ledger's unit name | the same string | — | CJ-DISP-1 |

**Correspondence obligations (OPEN):**
- **CJ-DISP-1:** each method returns what the original returns for the same unit, or raises the original exception with the original code.
- **CJ-DISP-2:** the two stop branches of the runner's cancel stop the same unit with the same ownership effect.
- **CJ-DISP-3:** the sandbox's argv runs inside the child namespaces as under the original manager (RC-6, K-20).
- **CJ-DISP-4:** the supervision dict's evidence fields come from helper closure frames, not from the manager's journal. The runner branches only on `kind` and `result` (`:937-982`), so those two must classify the same runs as the original does; the other fields are diagnostic and differ in source.
- **CJ-DISP-5:** limits and telemetry come from the kernel's cgroup files with the manager-property values absent; the runner's `ceilingFired` and `ceilingEvidence` (`:935-943`) must give the original classification.
- **CJ-DISP-6:** each original unit property maps to the leaf cgroup limit or process attribute that enforces the same thing (K-8, K-9, RC-6).

---

## V6-E. `archive_equal` against the actual archive encoding (V5-REQ-E; 02.1, 12.1; D-2a, D-7a)

### V6-E.1 The encoding, from source

The custody genesis row holds `root_worker_codec.archive (genesis)` (`rw/root_worker_journal.py:13`, `:96`), which is `operation_capture.archive (S.record (value))` (`rw/root_worker_codec.py:7`, `:19-20`). It has four layers:
1. **`S.record`** (`rw/resource_scoped_run_ledger.py:377-394`), over a JSON value:
   - a string s → `{'type': 'str', 'value': s}`; a boolean → `{'type': 'bool', 'value': b}`; null → `{'type': 'NoneType', 'value': None}`;
   - an integer v → `{'type': 'integer', 'negative': v < 0, 'magnitude': <lowercase hex of |v| as minimal little-endian bytes, empty for 0>}`;
   - a float x → `{'type': 'float', 'bits': <lowercase hex of struct.pack ('!d', x)>}`, the big-endian IEEE binary64 encoding;
   - an array → `{'type': 'list', 'items': [...]}`; an object → `{'type': 'dict', 'fields': {k: ...}}` in key insertion order.
2. **`operation_capture.archive`'s lift** (`rw/operation_capture.py:15-39`), over layer 1. Layer 1 holds no integer or float, because numbers have become strings and booleans. A dict becomes `['object', [[lift (key), lift (value)], ...]]`, a list `['list', [...]]`, and a string, boolean or None `['atom', x]`.
3. **`finalization_journal.encode`** (`rw/finalization_journal.py:44-60`): a list becomes `['list', [...]]`, and a string, boolean or None `['scalar', x]`.
4. **`evaluation_terminal.value_bytes`** (`rw/evaluation_terminal.py:76-91`): a list becomes `['array', [...]]`, a string `['str', base64 (UTF-8 with surrogatepass)]`, a boolean `['bool', b]`, None `['null']`. The result is `canonical`: `json.dumps` with `ensure_ascii=True`, `sort_keys=True`, compact separators and `allow_nan=False`, in ASCII (`rw/evaluation_pending.py:28-32`, `:74-76`).

So the archive is ASCII canonical JSON of nested arrays whose leaves are base64 strings, booleans and nulls. A JSON number survives only as layer 1's sign flag and hex magnitude, or as its hex bit pattern.

### V6-E.2 The comparison

`archive_equal (container, form, archive)` (X-1) recognizes the archive as form-ASCII canonical JSON, decodes layers 4 to 1, and compares the result with the JSON value tree of the container node by node:

| JSON value | Must equal, after decoding |
|---|---|
| object with keys k1 … kn in file order | `{'type': 'dict', 'fields': …}` with the same keys in the same order, each value equal |
| array | `{'type': 'list', 'items': …}`, the same length, each item equal |
| string | `{'type': 'str', 'value': s}` with the same code points, including any lone surrogate that the form admits |
| `true`, `false`, `null` | `{'type': 'bool', …}` with the same value, or `{'type': 'NoneType', 'value': None}` |
| integer lexeme X (`Integer (X)`) | `{'type': 'integer', 'negative': V < 0, 'magnitude': <minimal little-endian hex of abs (V)>}`, where V is X's integer value |
| non-integer lexeme X | `{'type': 'float', 'bits': <big-endian binary64 hex of (Sign (X), Round (M (X)))>}`. The sign bit is set exactly when `Sign (X)` is Negative, so −0.0 compares by its sign bit with every other bit zero, and `Round` is v5 V5-C.3's |

Any other shape, tag, key order, non-minimal magnitude, or bit pattern of the wrong length is `Archive_Mismatch` or `Archive_Malformed`.

### V6-E.3 Correspondence and costs

- **CJ-ARCH-1:** the native decode equals `restore_archive` followed by `S.restore` (`rw/root_worker_codec.py:22-28`) on every archive the loader accepts, including the round-trip requirement.
- **CJ-ARCH-2:** `Round` equals CPython's `float ()` of the lexeme, and the bit layout equals `struct.pack ('!d', …)` (RC-5).
- **CJ-ARCH-3:** the integer value of a canonical integer lexeme equals Python's `int`.
- **Costs (OPEN, D2 class).** JSON recognition, base64 and hex decoding, and the tree comparison are linear in the archive and container lengths. An integer lexeme of λ digits needs a decimal-to-binary conversion, quadratic in λ by schoolbook multiplication, with no cap. A non-integer lexeme costs what `Round` costs under v5 V5-C.3's window. No cost bound is claimed.

### V6-E.4 Refusal classes of the original JSON checks

The original Python checks run first, unchanged, and raise their original classes at their original points. The native verdict is consulted only after a check has accepted the bytes.

| Input | `exact_json` (form UTF8; `rw/protected_startup.py:40-51`) | `exact` (form ASCII; `rw/protected_resource_runtime.py:22-23`) |
|---|---|---|
| not JSON, bad UTF-8 | `json.JSONDecodeError` (a `ValueError`), or `UnicodeDecodeError` | the same |
| a duplicate key | `StartupRefusal` `STARTUP_DUPLICATE_JSON_KEY` | the last value is kept by `json.loads`; the canonical comparison then fails: `ResourceProducerRefusal` `RESOURCE_NONCANONICAL_PROTECTED_RECORD` |
| `NaN`, `Infinity`, `-Infinity` tokens | `StartupRefusal` `STARTUP_NONFINITE_JSON` (`:48`) | a non-finite float, then `ValueError` from `json.dumps (…, allow_nan=False)` |
| an overflow lexeme such as `1e309` | an infinite float, then **`ValueError`** from `canonical`'s `json.dumps (…, allow_nan=False)` (`:35-37`, called at `:50`): a plain `ValueError`, not a `StartupRefusal` | the same `ValueError` |
| any non-canonical spacing, order, escape or number form | `StartupRefusal` `STARTUP_NONCANONICAL_JSON` | `ResourceProducerRefusal` `RESOURCE_NONCANONICAL_PROTECTED_RECORD` |

These classes are **[unverified reasoning, RC-5]** for the installed CPython's `json`. The native statuses (`Not_Utf8`, `Bad_Token`, `Trailing_Bytes`, `Duplicate_Key`, `Key_Order`, `Spacing`, `Escape_Form`, `Number_Form`, `Number_Not_Finite`) therefore never stand in for the original exception: the original code raises it first, at the same point. The obligation CJ-JSON requires the native verdict to be `Ready` whenever the Python check accepted. A disagreement is a correspondence failure, refused fail-closed as `SOURCE_JSON_NATIVE_DISAGREES`, which the proof of CJ-JSON must exclude. It is not an accepted refusal of an original case.

---

## V6-F. Custody-return evidence in both regimes, and OB-ESC (V5-REQ-F; 04.4, 12.2, 12.4; D-6a, D-8b, D-9a)

### V6-F.1 Regime R1: the front has been alive since HELD

As in v5: the worker pidfd terminal, and the root namespace-init pidfd terminal (K-24). Both are held by the front since HELD. OB-ESC (V6-F.4) is part of the evidence's premise.

### V6-F.2 Regime R2: the front restarted and holds no pidfd

1. **Recorded identities.** The worker's host pid and start tick are in the `EXECUTION_NATIVE` record, whose process capture holds `host_pid` and `start_tick` (`RawProcess`, `rw/resource_child_execution.py:18`; captured at `rw/protected_root_resource.py:129-134`). The namespace init's host pid comes from the HELD frame (`C1:241`). Its start tick is read by the front from `/proc/<pid>/stat` at HELD and recorded in the `HELD` event (R6-16).
2. **Identity gone.** For each of the two: `pidfd_open (pid)` fails with `ESRCH`; or it succeeds, and `/proc/<pid>/stat` read while that pidfd is held shows a different start tick. A pid is unique among live processes, so a different start tick means the recorded process has exited **[unverified reasoning, K-4]**. An equal start tick means it is alive, and no custody return follows.
3. **No holder.** For every lock file of the transferred custody roster (the store, gate, broker and actuator locks and the issuer, universe and custody-journal locks, `rw/root_worker_custody.py:106-115`), a fresh `open` and `flock (LOCK_EX | LOCK_NB)` succeeds. The restarted front holds no earlier copy, so success means that no open file description anywhere holds that lock: neither the worker nor any process the worker could have passed one to **[unverified reasoning, K-6]**. The front keeps these fresh locks as the reconstruction's locks, in place of the escrow claim that died with the old front.
4. **The subject condition XC-6,** after `REQUEST_LOST` and `DRAIN_RECLAIMED`.

**XC-4** in R2 needs step 2 for the worker (R6-20).

### V6-F.3 The evidence, named

**E-CR** is R1's evidence or R2's steps 1–4, together with OB-ESC. It is required by `CUSTODY_RETURNED` (R6-18), RT-28 (R6-22) and V5-L.2's dead-worker row (R6-24).

### V6-F.4 OB-ESC: no custody descriptor escapes (explicit design obligation)

**Statement.** No process other than the worker, and the front's escrow until its release, ever holds a transferred custody descriptor: the lock and data file descriptors of the store, journals and authority state; client sockets; or slot and pipe descriptors.

**Mechanisms (DESIGN):**
- (i) every descriptor the worker receives is received close-on-exec (`MSG_CMSG_CLOEXEC`, K-26);
- (ii) the worker never sends a received custody descriptor by `SCM_RIGHTS`; its frames carry bytes only, and the descriptors the helper sends go to the worker, never from it;
- (iii) the worker never forks without exec while holding custody descriptors: every process it starts is spawned with `close_fds=True` or `posix_spawn`, and no fork-based multiprocessing is used in worker paths;
- (iv) the helper, the factory and the sub-helpers never receive a custody descriptor.

**Audit AU-2 (static, OPEN).** Every `SCM_RIGHTS` send site and every process-spawn site in the worker's code paths and in the v2 helper; every receive site's flags; and the absence of fork-based multiprocessing in worker paths.

**Controls.**
- **C-ESC-1 (lab, negative).** A fixture process holds a duplicate of a transferred lock's open file description after the worker exits. In R2 the fresh `flock` fails and `CUSTODY_RETURNED` is not committed. In R1 the design cannot detect the escape, and that is stated: R1 rests on OB-ESC and AU-2.
- **C-ESC-2 (lab, positive).** Normal worker exit gives E-CR in both regimes.

The premise, which v5 stated only in its AUTHOR-NOTES, is now an obligation of this design, listed in V6-P.

---

## V6-G. From Unknown back to service, and the worker's behaviour while refused (V5-REQ-G; 04.1, 09.5, 12.4; D-9a)

### V6-G.1 Cause classes of `UNKNOWN`

- **C-CHANNEL:** EOF without CLOSED on the custody channel, an error on that channel, or a front restart.
- **C-DEADLINE:** a deadline UNKNOWN (v2 §6.6).
- **C-APPEND:** a failed durable append by the phase owner.
- **C-EVIDENCE:** physical evidence that contradicts the chain.

The cause record names its class.

### V6-G.2 The durable route back

1. **Reattach.** While the root is Unknown with `Before_Unknown` in Worker_Owned … Worker_Relinquish, a front completes the V5-L.3 handshake. The worker commits `WORKER_REATTACHED (n)` (legal by R6-17). The record holds the handshake transcript: both nonces, the epochs, the front's MAC, and the peer's `SO_PEERCRED`.
2. **Reconcile.** The Reconciler commits `RECONCILED` with target `Before_Unknown` (legal by R6-19). It may do so only when the cause is C-CHANNEL or C-DEADLINE, the committed `WORKER_REATTACHED` follows the `UNKNOWN` event, and the worker's identity is live (its pidfd not terminal in R1; `pidfd_open` with an equal start tick in R2).
3. **C-APPEND.** The owner's own replay of the failed append succeeds, by the replay identity of V5-F.6. That committed event is the durable evidence, and the target is `Before_Unknown`.
4. **C-EVIDENCE.** No route back. The root stays Unknown until E-CR (`CUSTODY_RETURNED`) or until authentic evidence decides otherwise.

### V6-G.3 What the worker does while the root is Unknown

1. It mutates nothing that M1 … M3 gate: the store, the operation journal and the scoped ledger.
2. A protected section that reaches a refused choke point **does not raise**. It does not quarantine, and it does not fail the operation for this reason. It waits on the custody-commit condition, with no deadline, and re-evaluates `Mutation_Allowed` after each commit. It keeps the locks it holds, as any long protected section does; other requests in the worker wait behind it as in the original.
3. Its children keep running. Descriptor reading, spooling and stdin writing go on under M6 and M7, whose gates key on descriptor phases, not on the root phase.
4. It accepts no new transfer (XC-2) and commits no request intake (XC-3).
5. Its reattach endpoint stays open, and it commits `WORKER_REATTACHED` on a completed handshake.
6. The wait ends at `RECONCILED`, after which the waiting sections proceed, or at the worker's death, after which E-CR leads to `CUSTODY_RETURNED`.

---

## V6-H. `PREPARED` first, and the original phase-conditional `UNKNOWN` append (V5-REQ-H; 07.3, 12.2; D-6a, D-9a)

### V6-H.1 The launch order (DESIGN for `launch_root_worker`, `rw/protected_root_resource.py:27-141`)

1. the checks of `:33-49`, unchanged;
2. **custody `PREPARED (g)`**, with the operation, reservation, RESERVED and `EFFECT_INTENT` heads and the original request observation (R6-15);
3. machine admission at DISPATCH (`:51`);
4. `RECORD_LAUNCH_INTENT` (`:53-55`);
5. `DISPATCH_INTENT` in the launch journal (`:80-81`);
6. the slot (`:84-86`);
7. the launcher (`:96-99`) and HELD. The custody `HELD` event carries the full launch packet, launch reply and dispatch, which the lane's draft put in its `PREPARED` record (`:88-89`), and the init's host pid and start tick (R6-16).

The lane's draft commits `PREPARED` after `DISPATCH_INTENT` (`:80-89`). v6 moves it to step 2, so every failure from step 3 on happens with `PREPARED (g)` committed and `HANDOFF_ABORT (g, class)` legal.

### V6-H.2 The no-slot failure branch

The lane's draft appends `UNKNOWN` to the launch journal unconditionally when no slot exists (`rw/protected_root_resource.py:144-146`). v6 replaces that with the original scoped launch's phase-conditional append (`rw/protected_scoped_resource_runtime.py:770-776`): reload the launch journal, and append `UNKNOWN` only if the reservation's phase is `DISPATCH_INTENDED`, `NAMESPACE_HELD`, `GO_INTENDED` or `UNKNOWN`; then re-raise.
- **Phase still `NEVER_DISPATCHED`** (a failure in steps 3 or 4): nothing is appended. The facts satisfy `Never_Holds` (`core/resource_observation_classification.ads:96-102`), the class is `Never_Launched`, and the original `Release_Hold` applies (`core/resource_run_ledger.ads:317-320`). Custody commits `HANDOFF_ABORT (g, Never_Dispatched)`, and V5-G.1's route follows (with R6-21).
- **Phase `DISPATCH_INTENDED`** (a failure after step 5 but before the slot exists): the original append is made. Custody commits `HANDOFF_ABORT (g, Dispatched)`. No stop is made, because no slot exists, exactly as the original scoped launch makes none. Holds are retained (PR-b).
- **A slot exists:** the lane's `retain_and_stop_unknown` branch (`:142-143`), after `HANDOFF_ABORT (g, Dispatched)` (R5-8).
- U is quarantined by the invoke path's original exception handling (`rw/protected_root_worker.py:191-198`), unchanged.

---

## V6-I. RELAY transport loss and the daemon-level steps (V5-REQ-I; 09.2; D-8a, D-8b)

### V6-I.1 RC-10 decides the branch before the code is reviewed

R6-23 gives both branches. RC-10 is a lead-owned installed-runtime check of what `KernelPeer.observation ()` (`rw/client_peer.py:73-90`) returns or raises on an owned duplicate after the client has closed. It is performed before B-RECV is reviewed, and the implementation contains only the branch RC-10 selects. Nothing is chosen at run time.

### V6-I.2 Why branch (b) is exact

The original re-read compares a fresh `_read` (an `fstat` and `SO_PEERCRED` on the owned duplicate) with `_initial` and raises `PEER_TRANSPORT_CHANGED` on any difference (`:86-90`). If RC-10 shows that `_read` is unchanged after the client closes, the original returns `_initial` at every later gate. The front's re-read at transfer (JF), and every later authenticated relay response, already equal `_initial`: a difference would have raised and propagated. So the last authenticated re-read is exactly the value the original returns, and the worker loses nothing by using it. No refusal and no quarantine is added, which keeps clause 09.4 closed.

### V6-I.3 Daemon-level steps for a transferred request

| Step (`rw/daemon.py`) | Front | Custody owner, FRESH | Custody owner, RELAY |
|---|---|---|---|
| line read; router (`:307-313`) | yes; routes by the cached custody state (V5-L.1) | — | — |
| parse and validate: JSON, `id`, `op`, `args`, unknown operation, owner-only account (`:316-337`) | yes, exactly. Its error responses (`InvalidRequest`, `UNKNOWN_OPERATION`, `OPERATION_NEEDS_DAEMON_ACCOUNT`) are sent by the front through `_send`. No store write precedes them in the original either | — | — |
| `REQUEST_QUEUED`, then `REQUEST_TRANSFER_INTENT` | yes (V5-F.3) | — | — |
| `progress` callback (`:339-340`) | — | bound to the received socket's writer | bound to `PROGRESS_BYTES` frames (V6-I.4) |
| `RequestPeer.capture` (`:342-343`) | RELAY: the original call, at transfer | on the received socket (`KernelPeer.capture_descriptor`, `rw/client_peer.py:59-71`) | `RelayRequestPeer`, built from the front's capture |
| `observation`, `peer_uid` (`:344-345`) | — | yes | yes |
| `store.retain_client_request` (`:348`) | — | yes: the owner holds the store | yes |
| `RequestContext` (`:349`) | — | yes | yes |
| mutating: `_mutation_lock`, `_invoke`, publish (`:351-357`) | — | the owner's own lock and publisher | the same |
| non-mutating: `_invoke` (`:359`) | — | yes | yes |
| result, or the error mapping of `:360-372` | — | produces exactly `canonical_bytes (value) + b"\n"` (`:397`), commits `REQUEST_RESPONDED`, writes | produces the same bytes and commits `REQUEST_RESPONDED`; then `RESPONSE_BYTES`; the front writes and answers `RESPONSE_WRITTEN` |
| `finally`: close the retained peer (`:374-376`) | RELAY: after `RESPONSE_WRITTEN` | closes its duplicate | — |

Owner operations return before `_reserve` (`rw/protected_operations.py:731-741`; NF5-1's exception). They take the same daemon steps in the custody owner.

### V6-I.4 `PROGRESS_BYTES`

`PROGRESS_BYTES` is one more RELAY frame type, worker to front, with the same framing, MAC and binding as V5-I.5's frames. Its payload is one progress line (`{"id", "event", "data"}`, `:339-340`) of the request, sent before or after the response, as the original sends progress to the request's writer (`:390-393`). The front writes it while the client connection is open, and drops it otherwise, exactly as `_send` drops writes to a closing writer (`:394-400`).

---

## V6-J. The sub-helper's PID namespace: a child factory (V5-REQ-J; 03.2; D-5a, D-5b, D-8b)

**The problem.** The V1 root helper calls `unshare (CLONE_NEWPID)` and then forks init (`C1:336-337`). After that unshare, the helper's later children would be created in the new PID namespace **[unverified reasoning, K-28]**, so a sub-helper forked by the helper would not be outside the coordinator's namespace.

**The design (root helper v2).**
1. **Before** its `unshare (CLONE_NEWPID)`, the root helper forks a **child factory** F. It is connected by a `SOCK_SEQPACKET` socketpair created close-on-exec. F never unshares, never execs, and stays in the host PID and mount namespaces.
2. On each `CREATE_CHILD`, after the root helper has created the leaf cgroup, the root helper sends F the request and the leaf cgroup's descriptor. F forks the sub-helper into that leaf (`CLONE_INTO_CGROUP`, K-9), creates the sub-helper's socketpair, and passes the root-helper end back by `SCM_RIGHTS`. It then closes its copies of the leaf descriptor and the socketpair end.
3. The sub-helper is a child of F, in the host PID namespace. It then performs V5-E.1's E4: `unshare (CLONE_NEWPID)` and child init.
4. **F's surface.** argv, env and cwd are inherited, since F is a fork with no exec. Credentials are root, as the helper's. F holds its socketpair end and, only during one request, the leaf descriptor and the new socketpair's end. F holds no custody descriptor (OB-ESC (iv)).
5. **Reaping and closure order.** F reaps its sub-helpers and reports each exit to the root helper. The root helper waits for F before it sends its own `CLOSED … ECHILD` frame. This is internal to the successor helper and changes nothing in the front's barrier: CLOSED_NS, CLOSED_OUTER and CLOSED_RAW are exactly as carried (C4-VG23, R4-30), and clause 04.5 is untouched. Root settlement still waits for every child (CD-9).

**K-28 (OP-7, kernel measurement).**
- After `unshare (CLONE_NEWPID)`, the unsharing process's later forks are created in the new PID namespace.
- A process forked before the unshare stays in the original PID namespace, and so do its own forks.
- The factory's sub-helpers have the host namespace's `/proc/<pid>/ns/pid` identity.

---

## V6-K. H′: option H with the per-agent launch mapping (V5-REQ-K; 02.4, 06.2; D-4a)

Replaces v5 V5-D. Option G and v4's options A, B, C, E, F and F′ stand as v4 and v5 compared them. G stays unselected.

### V6-K.1 Structure

- **Service-class coordinator.** One per custody generation. It holds store custody and runs every handler and the job runner, as the original daemon does (`rw/protected_operations.py:750-754`; `rw/runner.py:694-703`). Its unit's limits are the installed daemon service's own, read back (RC-9) and set once. It holds no request's reservation.
- **Request root.** For each WL request, its own top-level reservation (parent none) is reserved by `_reserve` and dispatched **once**, as a request-root unit, by the root launch path. Its main process is the root helper v2 in holder mode: its init holds the delegated subtree and execs no coordinator. This satisfies the single-dispatch, top-level preconditions that `launch_reserved` and `launch_root_worker` both check (`rw/protected_scoped_resource_runtime.py:704-706`, `:723`; `rw/protected_root_resource.py:43-49`).
- **Per-agent launches.** Each runner launch (`rw/runner.py:697-703`; one per agent, several per request) is a **child task of that same request's root**. The child relation runs `TASK_INTENT`, child Reserve with `Task_Admission` (parent = the request's own root reservation), the child `Record_Launch_Intent`, `CREATE_CHILD` to that request's helper, HELD, Running, GO, measurement, agreement, READY and exec. The dispatcher (V6-D) presents it to the runner. No reservation is dispatched twice, and no child is made top-level: the lane's own text keeps child dispatch for "the child task/parent controller successor" (`rw/protected_scoped_resource_runtime.py:720-723`), which this is.

### V6-K.2 Comparison against AO-1 … AO-11 (revised marks)

| AO | H′ | Basis, or the obligation left OPEN |
|---|---|---|
| AO-1 grant and use | part | Each request reserves its own grant and use, and the coordinator holds none. The correspondence of the runner's per-agent admission gate (`self.gate.guard`, `rw/runner.py:694-696`) with the child rows is CJ-H-1, OPEN |
| AO-2 kind, amount, plan, cost | part | The request root uses its own plan's `Cost_Join`; per-agent children use the crosswalk's child plans. Their correspondence with the original per-agent `gate.unit_properties ()` amounts is CJ-H-2, OPEN |
| AO-3 owner and requester | ✓ | Bound to the request |
| AO-4 epoch and rollover | ✓ | The request root's Reserve, `Record_Launch_Intent` and `Record_Running` guards, and each child's |
| AO-5 immutable outer bound | ✓ | Each request root's bound is set once at its launch; the coordinator's limits are read once and never raised |
| AO-6 physical enforcement | part | Agents are enforced at their leaf cgroups inside their own request root. Handler code runs under the service's limits, as in the daemon; whether those limits equal the daemon's is CJ-H-3, OPEN (RC-9) |
| AO-7 no double count | ✓ | Request roots are siblings; each agent counts only in its own request's root |
| AO-8 future capacity | part | No protection is claimed. The coordinator's service-class limits exist beside the front's |
| AO-9 response progress | ✓ | The coordinator serves requests concurrently, with `operation_lock` only around the handler call, as the daemon does. A later WL request gets its own request root at once, which meets CG-2's and CG-3's closure conditions at design level |
| AO-10 native and process cost | part | Per WL request: the original root decisions (Reserve, pre-effect, `RESERVE_USE` replay, machine admission, `Record_Launch_Intent`, `Record_Running`, GO, terminal, release or charge, `OBSERVE_EFFECT`, `SETTLE_USE`), one request-root unit with its helper and factory. Per agent: `Task_Admission`, the child launch and run commands, two child decisions (worker and sub-helper), the terminal commit, one sub-helper, one init and the actor. The original uses one user-manager unit per agent (`rw/linux/systemd.py:179-197`). The difference in process structure and its cost correspondence is CJ-H-4, OPEN |
| AO-11 no new cap, prerequisite, borrowing or accepted failure | part | No cap and no borrowing. It adds the service-class coordinator launch kind, the holder mode and the RC-9 read |

### V6-K.3 Deltas H′ needs, all undesigned in detail

- **D-H1:** the coordinator's `PREPARED` evidence is its service launch record.
- **D-H2:** a native admission mode for a service-class coordinator, with no request binding.
- **D-H3:** the helper's holder mode, and its command routing from the coordinator.
- **D-H4:** reattach and handoff per generation for the coordinator.
- **D-H5:** the first WL request is an ordinary request.
- **D-H6:** the mapping of every runner launch onto a child task, with the dispatcher (V6-D).

### V6-K.4 Who decides

H′ changes no resource-policy field. Each request keeps its own admitted policy, and the coordinator uses the installed service's own limits, read back. The author therefore reads its adoption as engineering that the lead may decide, not as an authoritative resource-policy selection; this reading is for the reviewer to check (AUTHOR-NOTES §7). The author does not adopt it. Any authoritative policy change remains D-4a's (OP-3), none is proposed, and CG-2 and CG-3 stay OPEN until a route meeting their closure conditions is implemented and shown.

---

## V6-L. Carried text corrected, CG-1 attributed, CG-4 recorded (V5-REQ-L; 01.7, 03.3)

- **v4:1801 and v4:1804** are replaced by quotation (R6-4, R6-5), and RR5-7's neutralisation is retired (R6-1). No carried text is neutralised by a reading rule.
- **CG-1 (OPEN containment gap), attribution corrected.** The workload refusal `OPERATION_ORIGINAL_WORKLOAD_RESOURCE_ROUTE_UNINTEGRATED` is in the reviewed **preimage** (`pre/protected_operations.py:729-730`; preimage file sha256 `7674f11c26107d6c984ed8f8a883a2263f07a19e56e5a467f503ce90ae8b5e24`). It is carried unchanged into the lane (`rw/protected_operations.py:744-745`). The lane did not add it; v5's "the lane's containment" is corrected. Everything else v5 said of CG-1 stands:
  - no route, control or acceptance argument depends on it;
  - it is not on the root route;
  - in a deployment without a root worker it is the only route for WL requests, and their accepted cases are unmet and OPEN;
  - it closes only when the dispatcher (V6-D) is implemented, reviewed and its controls pass, and every original WL accepted case is served.
- **CG-4 (OPEN containment gap).** `owner.retry` is refused before any reservation with `OWNER_ORIGINAL_FULL_RESOURCE_ATTEMPT_ROUTE_UNINTEGRATED` (`rw/protected_operations.py:735-737`). That refusal is inherited from the preimage (`pre/protected_operations.py:720-722`). It refuses the original `owner.retry` accepted cases.
  - Closure condition: a genuine full-resource owner adapter in which the native owner reservation and an actual protected launch join before evaluation (the refusal's own message), implemented, reviewed, with every original `owner.retry` case served.
  - The OW class is not "unchanged" (R6-8).

---

## V6-M. K-27 split (V5-REQ-M)

- **K-27 (kernel, OP-7):** a sealed `memfd` cannot be changed by any holder, and mapping it maps exactly its sealed bytes (R6-27).
- **RC-11 (lead-owned installed-runtime check):** the installed dynamic loader, given `/proc/self/fd/N` of that sealed `memfd`, loads exactly those bytes and resolves the export symbols from them. This is used by V5-E.3 step 4.
- No lead-owned check remains in the operator's reservation, and the reservation is not widened beyond the kernel kind.

---

## V6-N. Controls added by v6

These join the additive roster (C2-17 with R3-9, R4-6, V4-M as amended by R6-4 and R6-5, and V5-M). **No original control is retired, and the frontier control is unchanged (C2-116).**

- **V6-A** (static).
  - Each export's arguments match its convention: P for the child, scoped-ledger and X-8 exports; T for the others.
  - `RootStateRec`'s layout entries equal its ctypes declaration, and every root_state column round-trips through it.
  - A material with a wrong magic, a version, a count, an index out of order, a wrong kind, a record size different from `layout (kind, 0)`, or an inconsistent byte length is refused by the sub-helper before any decision.
- **V6-N.B** (lab).
  - A worker-served IP request's handler runs in the WL root unit's cgroup, and the control records that bound (CG-2 visible).
  - A front-served IP request equals the serial route exactly.
- **V6-N.C** (lab). A WL request accepted while another generation's detached job runs is queued for g+1 and recorded (CG-3 visible).
- **V6-D** (lab).
  - For each row of V6-D's table, the dispatcher's result or exception equals the original's for the same unit and status: a normal exit, a non-zero exit, a signalled actor, an OOM-killed leaf (`result = oom-kill`), a `CREATE_CHILD` refusal (`SYSTEMD_LAUNCH_FAILED`), an abort before exec (`LAUNCH_FAILED`), and missing closure (`INDETERMINATE`).
  - A foreign unit name gives `FOREIGN_SYSTEMD_UNIT`.
- **V6-E** (pure).
  - `archive_equal` holds for a genesis containing an integer, a negative integer, zero, `0.5`, `-0.0` (sign bit set) and `1e+16`.
  - It fails for a flipped sign flag, a non-minimal magnitude, a one-bit change in a float, swapped key order, and a string differing in one code point.
  - For `1e309` the original `ValueError` is raised by the original code before any native call.
- **V6-F** (lab).
  - R1: E-CR on both pidfds.
  - R2: a restarted front with the worker gone (`ESRCH`, and a reused pid with a different start tick) and fresh `flock`s succeeding → `CUSTODY_RETURNED`.
  - A worker alive with an equal start tick → none.
  - C-ESC-1 and C-ESC-2.
- **V6-G** (pure and lab).
  - `WORKER_REATTACHED` from Unknown with a worker `Before_Unknown` → legal; from Unknown with `Before_Unknown` Front_* → refused.
  - `RECONCILED` back to `Before_Unknown` for C-CHANNEL after a reattach → legal; for C-EVIDENCE → refused.
  - A worker section reaching a refused choke point waits without raising, and proceeds after `RECONCILED`.
- **V6-H** (lab).
  - `PREPARED` precedes machine admission.
  - A machine-admission refusal and a `Record_Launch_Intent` refusal each leave the launch journal `NEVER_DISPATCHED`, with no `UNKNOWN` appended, `Release_Hold`, and `HANDOFF_ABORT (Never_Dispatched)`.
  - A failure after `DISPATCH_INTENT` with no slot appends `UNKNOWN` and makes no stop.
- **V6-I** (lab).
  - RC-10's outcome; then RELAY transport loss in the selected branch adds no refusal and no quarantine.
  - Each daemon step of V6-I.3 is executed by the process named there.
  - Parse errors are answered by the front with the original codes.
  - `PROGRESS_BYTES` are written while the client is connected, and dropped after it closes.
- **V6-J** (lab). K-28. Each sub-helper's PID namespace identity is the host's. The root helper's `CLOSED` frame follows the factory's exit.
- **V6-K** (none). H′ is not adopted, so no control is added. CJ-H-1 … CJ-H-4 are listed in V6-P.
- **V6-L** (static). Each R6 quotation is exact. No reading rule in v6 names a sentence of carried text to neutralise.

## V6-O. Measurement items and installed-runtime checks added or changed by v6

| Id | Question | Used in |
|---|---|---|
| K-27 (narrowed) | A sealed `memfd` cannot be changed by any holder, its creator included, and mapping it maps exactly its sealed bytes | V5-E.3 |
| K-28 | After `unshare (CLONE_NEWPID)` the unsharing process's later forks enter the new PID namespace; a process forked before it, and its forks, stay in the original one | V6-J |
| RC-11 | The installed dynamic loader loads exactly the bytes of `/proc/self/fd/N` of a sealed `memfd` and resolves the export symbols from them | V5-E.3, V6-M |
| RC-12 | The exit status the installed `systemd-run --pipe` returns for a normally exited, a signalled, and a never-started service | V6-D (`launcher.wait`) |

K items belong to OP-7's existing D-8b reservation, with R6-2 and R6-3's range repair. RC items are lead-owned. RC-10 is now also the selector of V6-I.1's branch.

## V6-P. Everything that remains OPEN (adds to V5-O and V4-O, carried)

- **All original obligations.** OB-001 … OB-219, every one OPEN, with no closure credited.
- **Required changes and closures.**
  - V5-REQ-A … V5-REQ-M.
  - V4-REQ-A … L, except V4-REQ-H and V4-REQ-K, which are closed at design level only.
  - V3-REQ and V2-REQ; RQ-1 … RQ-5.
  - Every PARTIALLY_CLOSED clause and ruling.
- **Containment gaps.** CG-1, CG-2, CG-3 and CG-4, each with its closure condition (V6-B, V6-C, V6-L).
- **Correspondences.**
  - CJ-DISP-1 … CJ-DISP-6;
  - CJ-ARCH-1 … CJ-ARCH-3, and CJ-JSON;
  - CJ-H-1 … CJ-H-4;
  - OB-ESC, with audit AU-2.
- **H′.** Deltas D-H1 … D-H6; its adoption (lead) and any D-4a policy change (operator), none proposed.
- **Measurements.** K-1 … K-28 (OP-7); RC-1 … RC-7, RC-9 … RC-12.
- **Bodies and proofs.** All bodies, `Post`s, proofs, native costs and controls; P-A1 … P-A4.
- **C-API.** CAPI6R's open obligations; ROOT_WORKER_INTEGRATION; L-CAPI-P; G-PROT; IC-10.
- **Acceptance.** Hosted assurance; publication, deployment and final Phase One acceptance.
- **Review.** The independent review of v6, of every slice and of the full lane.

## V6-Q. Non-claims (adds to V5-P and V4-P, carried)

- v6 reviews, accepts, proves and authorizes nothing, and adds no approval gate. Every original obligation stays OPEN.
- Nothing was compiled, run, imported, proved, tested or measured.
- No equivalence is claimed for worker-served IP requests (CG-2), for later WL requests (CG-3), or for the dispatcher's evidence fields (CJ-DISP-4, CJ-DISP-5).
- R1 custody return does not detect an escaped descriptor holder; it rests on OB-ESC and AU-2. R2 detects a holder of a transferred lock, and nothing else.
- `archive_equal`'s rounding and bit layout are the author's reading until RC-5. The refusal classes of V6-E.4 are the author's reading of CPython's `json` until RC-5.
- H′ is not adopted; its AO marks are design-level and partly OPEN.
- No liveness is claimed for a worker that never completes a reattach, or for a root in Unknown with a C-EVIDENCE cause.
- SIA recall is not evidence and is not used as evidence.

---

## Appendix A. JACKAL

No numeral in v6 was derived by arithmetic (§C.4), so no JACKAL call was made; `jackal.json` records this. v5's J5-1 … J5-4 keep their status inside carried slices: `exact`, lane `rat`, `formal=false`, informational about arithmetic only. The review re-ran them, and each was positive (`D5R/checks.json`).

## Appendix B. Inputs bound while drafting v6 (sha256, observed)

```
938c832d03df0910506756ec295acef86ae2cacba4d7b2478a09c6d27f3685cf  D5/SEAM-DESIGN.md
a3d3ff5482c188705050f7f83709ff2f5e418547ed4a71f26f705f8c5fe18ebe  D5/seams.json
9adaaa83960f7064552dee1f85ffa38ad5191f0e6d6cd02321b287121e931628  D5/jackal.json
d6e16bdfb23b2544218694508144ba32f72ab3c23f79fa9dcb0f2117d324b836  D5/AUTHOR-NOTES.md
d385baca2e5eba7a9605c486d1b5afb2f3fc56cae1d893eed9ba163bf1cc0a50  D5R/REVIEW.md
0b9a3b0705df9d40f7b4e109d4f2042cb6236dcc848fd48f32f27a0de5ff8187  D5R/review.json
6f24f1a44718ce7f8d0b5159b3b78de1cb45ddbf4a2681cacdba9cfe10ead0ab  D5R/checks.json
04b87e452db87f791194a633b8602bf716edc3a41dc4451a002e10d85d000a36  D5R/review-freeze.json
f65629cb45e6e8a5ea798f5130a7f98e1d365758a7175343444f4022864efbda  D4/SEAM-DESIGN.md
7674f11c26107d6c984ed8f8a883a2263f07a19e56e5a467f503ce90ae8b5e24  pre/protected_operations.py
9031e0bdd6fd10e911a908f1e15d8241aed94b0445946b5da45d821899133710  rw/runner.py
9d448dcc8741b698750147a8a0ccb9aaaf0215cba6a16c702facde394b6b52e4  rw/daemon.py
1022187a02c19fb25ecfcafcc9a43a91e5ab62cf243ae38014c14d4c73463ade  rw/client_peer.py
f1089a091399dd0c1a0602aebb027edff4737fbf562750e95e3a0c561067f723  rw/protected_root_resource.py
acf5ac0fb4035d53c3e053e7a3a10b4f29fd29d5bc0aefbdb0d9de181665080f  rw/protected_scoped_resource_runtime.py
76ae777b375b3ad2785399c73d9e14055b2f6cca58a30e2078b2b847ac87176e  rw/resource_child_execution.py
e506348f1efb6615151114a21ef238aca4dd0e81592aad7f1bb64b184ddd8076  rw/resource_scoped_run_ledger.py
e0148f27abfa652d8594a87660fc996e1e402101593f348824cae6a08dd41c6f  rw/canonical_exchange_kernel.py
b7c44b329c8c92701c06fcdfd7b5e6692b8b164ae7f699729afe60d0d30036a0  rw/canonical_operation_kernel.py
0c3998337f998f1961f3573a3e0743dce750b5777d47bb8bb205d3a74faffa06  rw/canonical_owner_completion_kernel.py
0fc7f5fde1357f1a97da2ce1977c60290cb15bb4e4e5b77205b4e678f6a5f482  rw/operation_authority_kernel.py
9f123d62282c8189a9b7b5f300b37d94d2544626820ca5d08ee9a72c81cab7f2  rw/chain_authority.py
d133785f88a76f09f816f484a58a85d4cd75052a96424b12a52c5434121afb05  rw/operation_capture.py
f2bc319b69f3491b9b16fde710fde122d94203ab2d5cfb94fb348d7c79d65793  rw/root_worker_codec.py
bf5472672be296d4b37c5cae113407a733625611b79b34c46316da729e1df8d7  rw/finalization_journal.py
9f5e97446797f09633008c3d8c1f7d6759b674122681887e73a7a6e78db53033  rw/evaluation_terminal.py
559dc067399ade18658116727cbe2f364f718791cb299bd563765075de5569fa  rw/evaluation_pending.py
e29a14a63d67fa3228ede57f0ad12aaa55cbf7c7cf61a8bc09971d5731680ca6  rw/protected_startup.py
fc6f00f698160f1a854ef7ae72c425f3c7ed11243809b6dac1a5132c0e2ad33f  rw/protected_resource_runtime.py
2510f8edac3937509d36bc3b38511af89f81ecf9a5eff77fefc87f927f3aa811  rw/root_worker_journal.py
15cbbfcd61a98da55a704af16fd5d853a3af64bc0aba84599d936440ba8f74a1  rw/protected_root_worker.py
ea1a01df19ddef2418d4e4ec14dab6cea1eaa70423172eedea36a48ec383f0cb  rw/protected_operations.py
25f38ae7c1b63f14329400155562c18e459b80f46797851ef81d82db03172169  rw/root_worker_custody.py
710d37c77de105bdd62d96e1ce31d5b0ad79fcbd7ae8b7e556bd1b7656462784  rw/linux/systemd.py
f2a321d07e667e80f4359634e8e4a956b555368b8d449e8c8c930b8f511aeff7  C1
2f3a0b4b3bb2a0996824859c2d9f8a59e7c58f624b2d81cb00e40e76bf588237  P1/HANDOFF.md
```

These are byte identities at the time of reading. They establish no authenticity, installed state or atomic snapshot.

## Appendix C. Slice and quote verification

A read-only Python script read the v4 and v5 designs, the sealed v5 review and this file. It printed to standard output and wrote no file. It checked (observed; the final run is in AUTHOR-NOTES §2):
- v5 `SEAM-DESIGN.md`: sha256 `938c832d…85cf`, 1628 lines, ending with a newline;
- every row of §B.1: the sha256 of the stated v5 lines equals the stated hash; no two slices overlap; every v5 line is in a slice, in a superseded range of §B.3, or is empty or `---`;
- every R6 replacement: the quoted `v5:` or `v4:` text equals the stated lines exactly; each v5 target lies inside its stated C5 slice; each v4 target lies inside its stated C4 slice (as v5's §B.1 states it) and is replaced by no R5; no line is targeted twice;
- every quotation in §A from the sealed `review.json` and REVIEW.md: equal to the text it quotes;
- every markdown table: each row has its header's cell count.

## Appendix D. Companion file identities

Observed with `sha256sum` and `wc -c` after the files were written. This file cannot contain its own hash; `seams.json` records it, and the handback records both.

| File | sha256 | Bytes |
|---|---|---|
| `jackal.json` | `5d6684296284d33d3580e5dc123401b493fdf2431d3d54c57b8b4d98abcc84b0` | 1018 |
| `AUTHOR-NOTES.md` | `95826c1ee59c7ef11cd9cefbcb3e212053d5ecbd05908224ba59572ebf922633` | 7331 |
| `seams.json` | recorded in the handback (it binds this file's hash) | — |
