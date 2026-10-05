# Root-worker runtime lane: seam design v8

| | |
|---|---|
| Author | Claude Code lead claude-opus-4-8 (drafting subagent, author role) |
| Date | 2026-10-05 |
| Status | **DRAFT_FOR_INDEPENDENT_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. The author reviews, accepts and closes nothing; author checks are self-checks. Every original obligation (OB-001 … OB-219), accepted case, deterministic fixture, control, contract, threshold, proof floor and scope remains **OPEN** and unchanged. |
| Supersedes | v7 `SEAM-DESIGN.md` (sha256 `62b7d5877a4df95b86ab5354d64d4fadd6bcf8017da20b8ba53dbbec34169f16`, 184450 bytes, 1526 lines), v7 `seams.json` (`de716b0bf38671abef088957014885ecd1002380b8eb56f5966230cd1ba2e817`), v7 `jackal.json` (`f691a36b3a9efbd49e6d56ad2c264f85b0b83f17ab64ef1fd58db698f181263f`) and v7 `AUTHOR-NOTES.md` (`b651f5e61fe3deca19e6bed1753bb83e7b93d059cc39a2fbc1ea1768968e9da6`). All were read only and re-hashed unchanged; the first two equal the v7 review's `design_sha256` and `seams_sha256`. |
| Answers | The sealed independent review of v7 in `WT/designs/claude-root-worker-seam-design-v7/review/claude-v1/`: `REVIEW.md` `4d09a69a8af251f02ea49273ad0c35aa4c39b86628f6be6128f4184a1e19cf9f` (19064 bytes), `review.json` `4ba840c61dbf5cf58c8291535084cb8db6e2fa3088bb8a236fb24b0f8c309693` (14979), `checks.json` `1770794001691ab77736ef2cbfa4e26f9b107166a3c8bd6adae2248b9c09cda3` (6144), `review-freeze.json` `c65eed5b2ff472e22eb26e4a17392a5d4e68d3363a1b5ef098f06be94667d2f6` (613). The freeze names "claude-opus-5-5 (independent Claude Code review subagent, fresh context)", `reviewer_kind` claude-subagent, `different_from_author` true, and lists the first three files with exactly these hashes and sizes (recomputed, equal). Verdict **ENDORSED_WITH_REQUIRED_CHANGES**: eleven of the twelve V6-REQs CLOSED_AT_DESIGN_LEVEL and verified against the lane source; V6-REQ-H PARTIALLY_CLOSED; two required changes, V7R-H and V7R-CITE. Not read, as directed: that directory's `raw-final-message.txt`, `review-records/`, and every `gpt61-v*` directory. |
| C-API status | Bound in Appendix B and §A.4, unchanged from v7 (carried): CAPI5R ENDORSED_WITH_REQUIRED_CHANGES; CAPI6R ENDORSED, those and the earlier RC4 items CLOSED_AT_DESIGN_LEVEL only; ROOT_WORKER_INTEGRATION OPEN. The PK-0 packet under `WT/packets/capi-pk0/` was not read. |
| Scope | Design only, for the draft lane `W/work/protected-original-root-worker-repair-v1` (status `INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY`). The lane draft is someone else's unreviewed source and was not touched. v8 grants no execution, proof, build, test, review, operator or acceptance authority, and adds no approval gate. |
| Location | `WT/designs/claude-root-worker-seam-design-v8/` |
| **What this document consists of** | v8 is (1) the text of this file; (2) the v7 `SEAM-DESIGN.md` line ranges listed in §B.1 (slices C7-…), each bound by the sha256 of its exact bytes, with the quoted replacements R8-1 … R8-9 of §B.2 applied; (3) transitively, everything those v7 slices carry: slice C7-B is v7's own §B, so the v6 slices it binds (C6-…) with R7-1 … R7-86, and through them the v5 … v1 chains, minus the withdrawals W5-1 and W5-2. Every other v7 text is superseded by the map of §B.3. Every identity a normative statement relies on is bound in Appendix B of this file, and every ruling's owner and evidence requirement is stated in §A.3 of this file. |
| Companion files | `seams.json` (machine twin), `jackal.json` (JACKAL record), `AUTHOR-NOTES.md` (process record, sweep record, deviations). Identities: Appendix D. |
| Write history | Every file in the location above was created or changed only with the Write and Edit tools. One read-only helper script was written under `scratch/` and is disclosed in AUTHOR-NOTES §5. Bash was read-only. |

Every statement about source is **static**: read from files, or reasoned from what was read. Nothing was compiled, run, imported, proved, tested or measured. Kernel, systemd, SQLite, interpreter and Ada-visibility statements marked **[unverified reasoning]** are the author's reading and name their evidence item.

---

## A. Closure tables

v8 answers exactly the two required changes the sealed v7 review left: **V7R-H** and **V7R-CITE**. Everything the v7 review found CLOSED_AT_DESIGN_LEVEL stays closed and is carried unchanged. "Closed at design level" is not acceptance; the underlying proof, native and control obligations stay OPEN. The author closes nothing.

### A.1 The two required changes

Each change is quoted verbatim from the sealed `review.json` `required_changes[].change`.

| Id | Required change (verbatim) | v8 answer | Where |
|---|---|---|---|
| V7R-H | "Specify the exact edit to rw/protected_root_worker.py:191-199 that preserves the original p.quarantine(operation,error) in the owned-is-None failure case: convert the ':195 elif self.phase==\"UNKNOWN_WORKER_OWNERSHIP\"' into an unconditional 'else:' (or re-establish the quarantine condition independently of the removed :192). Correct V7-H.1 and R7-65: with :192 removed the exception handling is NOT 'unchanged' and the elif does NOT 'become the plain alternative' — its guard evaluates False in its only reachable case, silently dropping the native quarantine." | V8-H.1 gives the exact before/after of the handler. The `:195 elif self.phase=='UNKNOWN_WORKER_OWNERSHIP'` becomes an unconditional `else:`, so `p.quarantine (operation, error)` runs in **every** `owned is None` failure, independent of any phase value; `:192`'s blanket phase pin is removed and the in-memory phase is set, after the settlement, from the committed custody phase (fail-closed to the wedge). The design states the handler **is** changed, minimally, to preserve the quarantine — not "unchanged". R7-65's carried one-liner is corrected by R8-2. The quarantine fix does not depend on the router row-3 successor change, which stays the OPEN, unreviewed lane-code obligation it already was. | V8-H; R8-2 |
| V7R-CITE | "Correct the line citations the design presents as exact: rw/daemon.py:390-393 (comment lines, not the progress send; _send is the generic writer :388-400); the D-H7 table boundaries :703->:705 (journal checks), :729-731->:730-731 (cgroup2 require), :732-736->:733-735 (sandbox require, :736 begins the env loop); and the loose wordings 'front's owners' (rw/protected_root_resource.py:161 closes resource state owners), 'V1's PARAMETERS' (rw/resource_child_execution.py:207 is the base roster) and 'host pid' (C1:241 writes the init pid)." | Every cited location is corrected by quotation: the `daemon.py` progress/`_send` citation (R8-3); the D-H7 table boundaries `:705`, `:730-731`, `:733-735` (R8-7, R8-8) and the `launch_reserved` enforcement cite `:730-731` (R8-9); "front's owners"→resource-state owners with `:161` and the surviving custody/transport descriptors (R8-6); "V1's PARAMETERS"→the base `PARAMETERS` roster at `:207` (R8-4); "host pid"→the namespace init's pid written at `C1:241` (R8-1, R8-5). None changes a conclusion. V8-CITE lists each. | V8-CITE; R8-1, R8-3 … R8-9 |

### A.2 Everything the v7 review closed stays closed

From `review.json` `rc_closure`, carried unchanged:
- **CLOSED_AT_DESIGN_LEVEL (v7):** V6-REQ-A, B, C, D, E, F, G, I, J, L; V6-REQ-K at design level with adoption OPEN (CJ-H-1/CJ-H-2/CJ-H-5 open). v8 changes none of these sections except for the V7R-CITE line corrections, which change no conclusion (V8-CITE).
- **V6-REQ-H:** was PARTIALLY_CLOSED only for V7R-H. v8 closes V7R-H at design level (V8-H); the native handler body, its proof and the lab control stay OPEN, and the router row-3 successor change (`rw/root_worker_endpoint_router.py:26-31`) stays OPEN unreviewed lane code.
- **Carried closed:** V5-REQ-B, H, L, M and V4-REQ-H, V4-REQ-K stay CLOSED_AT_DESIGN_LEVEL. V4-REQ-H's condition (the factory holds no pipe end) is met by V7-J, carried. The nine PARTIALLY_CLOSED V5-REQs (A, C, D, E, F, G, I, J, K) stay so.
- **Clauses and rulings:** clauses 04.3 and 12.1 stay closed (no `RootStateRec` field or column is added by v8); 09.4 stays closed (met by V7-I, carried); 07.1 stays closed (D6:83 corrected in v7, carried); D-2b stays CLOSED_AT_DESIGN_LEVEL (C2-116 untouched; no R7 or R8 targets it); the frontier control is unchanged. D-1a … D-9a stay PARTIALLY_CLOSED (§A.3).

v8 adds no refusal, cap, narrowed domain, retired control or approval gate, and no new operator item.

### A.3 Rulings, stated normatively

Each ruling, owner and evidence requirement is quoted verbatim from the sealed v6 `review.json` `rulings[]` (the canonical rulings; the v7 review confirmed v7 changed none, and v8 changes none). This table is normative in v8. Where an owner names a GPT-6.1 review, the sealed v7 review records the reading (REVIEW.md, verbatim): "Under the 2026-10-05 17:05Z direction, independent reviews are Claude subagents; no GPT-6.1 gate is claimed." v8 does not decide that reading; it records it.

| Ruling | Ruling (verbatim) | Owner (verbatim) | Evidence required (verbatim) | v8 |
|---|---|---|---|---|
| D-1a | "PARTIALLY_CLOSED; V6-REQ-A, V6-REQ-B" | "Lead source designer; independent reviewer (Claude review subagent under the 2026-10-05 17:05Z direction)" | "Concrete typed Reference/Decide/Post and embedding/witness definitions, all original clause and case mapping, later full body/reference/termination/native-cost proof and matching controls." | carried (V7-A, V7-B); V7R-CITE on V7-A.1 (R8-4) |
| D-1b | "PARTIALLY_CLOSED; V6-REQ-B, V6-REQ-C" | "Lead scoped model/caller designer; independent reviewer" | "Explicit fresh/replay/historical domains, faithful scope/epoch spans, rollover accepted/refusal controls and full caller/kernel proof." | carried (V7-B, V7-C) |
| D-2a | "PARTIALLY_CLOSED; V6-REQ-A, V6-REQ-E" | "Lead authors schema/callers; operator provisions or installs authoritative state" | "Complete version union over every constructor/loader/schema/creation slot, one-shot full DDL/head/provisioning evidence, v1 parity and v2 genuine startup plus absence/crash controls." | carried (V7-A, V7-E) |
| D-2b | "CLOSED_AT_DESIGN_LEVEL (carried by C2-116)" | "Lead prepares concrete equivalence/adoption package; applicable operator authority; independent review" | "Original bytes/roster retained, exact version/domain mapping, all original negative cases and genuine positives, no replacement or passing-history credit." | carried unchanged |
| D-3a | "PARTIALLY_CLOSED; lab evidence OPEN; V6-REQ-J protects the carried V4-REQ-H closure" | "Lead protocol designer; operator for lab execution" | "Full LIVE/UNKNOWN rosters, true descriptor/lock/wait custody, buffered/raw drain continuity, failure/restart controls and authentic terminal collection." | carried (V7-J); lab evidence OPEN |
| D-4a | "PARTIALLY_CLOSED; V6-REQ-C, V6-REQ-K" | "Lead prepares native accounting comparison; independent review; operator selects any authoritative resource-policy change" | "Kind/grant/owner/amount/cost/rollover domain matrix, faithful host/ledger cost proof, no first-root grant borrowing or new caps, concurrency/status/cancel/recovery controls." | carried (V7-C, V7-K); V7R-CITE on V7-K (R8-6 … R8-9) |
| D-5a | "PARTIALLY_CLOSED; V6-REQ-A, V6-REQ-D, V6-REQ-J" | "Lead prepares native/OS design; independent review; operator for delegation and privileged lab action" | "Native classifier/root/child compatibility, actual cgroup/namespace lineage, immutable outer ceilings/capacity, coordinator privilege/FD custody, actor separation and matching controls." | carried (V7-A, V7-D, V7-J) |
| D-5b | "PARTIALLY_CLOSED; V6-REQ-J" | "Lead helper designer; independent review; operator for privileged execution/installation" | "Explicit input/native/source union, exact ABI/protocol/argv/env/stdin/EOF, FD inheritance audit, authentic ACK/ECHILD/waits/drains and retained native-body/cost obligations." | carried (V7-J) |
| D-6a | "PARTIALLY_CLOSED; V6-REQ-F, V6-REQ-H" | "Lead historical/canonical model designer; independent review" | "Original QUARANTINE_USE and K4 transitions/callers, authentic historical result/receipt/cause, current-denial/lost-ACK/never-launched/serial positives, no EOF/return settlement." | carried (V7-F); the V6-REQ-H part closed by V8-H (the original QUARANTINE_USE now provably preserved) |
| D-7a | "PARTIALLY_CLOSED; V6-REQ-E" | "Lead native/provenance designer; child-authority and independent re-review; operator for any original API/owner-policy alteration" | "Per-pair producer/canonical encoding/custody mapping, copied-tag and one-side corruption refusals, positive distinct-source equality, exact wire/layout and full original case preservation." | carried (V7-E) |
| D-8a | "PARTIALLY_CLOSED; V6-REQ-I" | "Lead OS/native requester designer; independent review" | "Raw relative/host credentials, namespace/socket/custody and transaction/request joins, native decode/decision semantics, current-object and exact-type caller coverage." | carried (V7-I); V7R-CITE on the daemon cite (R8-3) |
| D-8b | "PARTIALLY_CLOSED; V6-REQ-F, V6-REQ-I, V6-REQ-J; measurements stay with the operator under OP-7" | "Lead prepares domain-preserving protocol; operator for kernel measurement; independent review" | "Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client." | carried (V7-F, V7-I, V7-J); K-29 under OP-7 |
| D-9a | "PARTIALLY_CLOSED; V6-REQ-A, V6-REQ-F, V6-REQ-G, V6-REQ-H" | "Lead additive SPARK relation and caller designer; independent review; operator for fault campaign" | "Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes." | carried (V7-A, V7-F, V7-G); the V6-REQ-H part closed by V8-H (lost-ACK/half-transfer quarantine preserved) |

No ruling's owner or evidence requirement is changed by v8. D-6a and D-9a retained the V6-REQ-H gap after v7; V8-H closes that gap at design level, while every other sub-item of each ruling stays as the sealed review left it, PARTIALLY_CLOSED.

### A.4 Carried exactly as the reviews closed them

- **V6-REQ-H carriage (V5-REQ-H base).** v7's V7-H is superseded by V8-H (§B.3). The two carried one-liners it governs stay: R7-64 (Release_Hold scope, inside C6-VH) is unchanged; R7-65 (the quarantine one-liner, inside C6-VH via C7-B) is corrected by R8-2. V5-REQ-H's launch order and phase-conditional append are untouched.
- **V4-REQ-K and the C-API.** v5 V5-K carried verbatim; CAPI identities bound in Appendix B of this file: CAPI5 `APPENDIX-BINDINGS.md` `f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2`, CAPI6 `APPENDIX-BINDINGS.md` `9f9f3dfa897d0c320226df39c89bc5c156fc87ebc3e24959ab0c08bba5db1946` (recomputed), and the CAPI5R/CAPI6R review identities (recorded; Appendix B explains why not recomputed).
- **D-2b** carried by C2-116 through the chain; `frontier_sha256` `a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb`; unchanged.
- **R7-1 … R7-86** are carried inside C7-B. Three of their result lines are corrected by R8 (R8-1 on R7-58, R8-2 on R7-65, R8-3 on R7-70); no other R7 is touched, and no R8 changes an R7's `v6:` quoted text.
- **Operator items** OP-1 … OP-9 unchanged; K-29 stays under OP-7's existing D-8b reservation. No operator item is added, lowered or widened; no approval gate is added.

---

## B. What v8 carries from v7, and how to read it

### B.1 Bound v7 slices

- v7 `SEAM-DESIGN.md` has 1526 lines and ends with a newline (observed). Its whole-file sha256 is `62b7d5877a4df95b86ab5354d64d4fadd6bcf8017da20b8ba53dbbec34169f16`.
- Each slice's sha256 is that of the UTF-8 bytes of its lines, each followed by `\n`. A read-only script computed them (Appendix C).
- CARRIED_WITH_LINE_REPLACEMENTS slices are part of v8 with the listed lines replaced by the §B.2 text. Slice C7-B is v7's §B; it carries v6 through its own slice table (C6-…) with R7-1 … R7-86, and through C6-B the v5 … v1 chains, so an R8 may also replace a line of an R7 block's `v7:` result text (RR8-4).

| Slice | v7 lines | sha256 | Disposition | Content |
|---|---|---|---|---|
| C7-B | 128-865 | `79e4419412ad070f773094f7bca55160e1a66e0d18ed479a2f4db9a790175ef3` | CARRIED_WITH_LINE_REPLACEMENTS (R8-1, R8-2, R8-3) | v7 §B: the C6 slice table, R7-1 … R7-86, v7's map and reading rules |
| C7-VAG | 933-1104 | `dd9406c1372c93b70eb484caf90ef404e4fa2b1f823728d502089f219ec6f070` | CARRIED_WITH_LINE_REPLACEMENTS (R8-4, R8-5) | V7-A … V7-G: material/capacity/`fold`, CG-2, CG-4, dispatcher, JSON modes, custody-return, Unknown routes |
| C7-VIQ | 1127-1403 | `409d2863e9c2a8369f80731681e6db43903d75bbb974b8044100448a178813b3` | CARRIED_WITH_LINE_REPLACEMENTS (R8-6, R8-7, R8-8, R8-9) | V7-I … V7-Q: RELAY loss, factory, H′, carriage-repair, sweep, controls, measurements, open, non-claims |

### B.2 Line replacements

Each replacement quotes the exact v7 line, then gives the v8 text. The reason names V7R-H or V7R-CITE.

**R8-1 replaces v7 line 618 (in C7-B, the `v7:` result of R7-58).** V7R-CITE: `C1:241` writes the init pid.
```text
v7:
1. **Recorded identities.** The boot identity, `/proc/sys/kernel/random/boot_id` read as the original reads it (`rw/protected_scoped_resource_runtime.py:145`), is recorded in the custody `HELD` event and in the `EXECUTION_NATIVE` record. The worker's host pid and start tick are in the `EXECUTION_NATIVE` record, whose process capture holds `host_pid` and `start_tick` (`RawProcess`, `rw/resource_child_execution.py:18`; captured through the worker pidfd at `rw/protected_root_resource.py:129-134`). The namespace init's host pid comes from the HELD frame (`C1:241`); its start tick is read by the front while it holds the init pidfd that the same frame passes (`C1:247`), under the pairing of v7 V7-F.1, and is recorded in the `HELD` event (R6-16 as replaced by R7-35), or the event records that the init pidfd was already terminal.
v8:
1. **Recorded identities.** The boot identity, `/proc/sys/kernel/random/boot_id` read as the original reads it (`rw/protected_scoped_resource_runtime.py:145`), is recorded in the custody `HELD` event and in the `EXECUTION_NATIVE` record. The worker's host pid and start tick are in the `EXECUTION_NATIVE` record, whose process capture holds `host_pid` and `start_tick` (`RawProcess`, `rw/resource_child_execution.py:18`; captured through the worker pidfd at `rw/protected_root_resource.py:129-134`). The namespace init's pid, which the HELD frame writes (`C1:241`, the init's pid in the host PID namespace), comes from that frame; its start tick is read by the front while it holds the init pidfd that the same frame passes (`C1:247`), under the pairing of v7 V7-F.1, and is recorded in the `HELD` event (R6-16 as replaced by R7-35), or the event records that the init pidfd was already terminal.
```

**R8-2 replaces v7 line 674 (in C7-B, the `v7:` result of R7-65).** V7R-H: the handler is changed, minimally, to preserve the quarantine.
```text
v7:
- U is quarantined by the invoke path's original exception handling (`rw/protected_root_worker.py:193-198`): `owned.retain_and_stop_unknown` when a dispatch owner exists (`:193-194`), otherwise `p.quarantine (operation, error)` (`:195-198`, the `elif` becoming the plain alternative). Line `:192`, which sets the front's in-memory phase to `UNKNOWN_WORKER_OWNERSHIP` on every failure and so makes `:159` refuse every later root invoke, is replaced by v7 V7-H.1: the in-memory phase follows the committed custody phase, so after `FRONT_OWNED (g+1)` the front serves.
v8:
- U is quarantined by the invoke path's exception handling, which v6 V6-H changes minimally to preserve the quarantine (v8 V8-H.1, with the exact before/after): `owned.retain_and_stop_unknown` runs when a dispatch owner exists, and the `elif self.phase=='UNKNOWN_WORKER_OWNERSHIP'` guard at `rw/protected_root_worker.py:195` becomes an unconditional `else:`, so `p.quarantine (operation, error)` runs in **every** `owned is None` failure — independent of any phase value, exactly the original native settlement. Line `:192`, which pinned the in-memory phase to `UNKNOWN_WORKER_OWNERSHIP` on every failure and so made `:159` refuse every later root invoke, is removed; the phase is set after the settlement from the committed custody phase, fail-closed to `UNKNOWN_WORKER_OWNERSHIP`. The handler is therefore changed (not "unchanged"), and only minimally; the serve-again behaviour and the router row-3 successor change stay OPEN unreviewed lane code (v8 V8-H.1) and the quarantine fix does not depend on them.
```

**R8-3 replaces v7 line 714 (in C7-B, the `v7:` result of R7-70).** V7R-CITE: `rw/daemon.py:390-393` are comments; `_send` is the generic writer `:388-400`.
```text
v7:
`PROGRESS_BYTES` is one more RELAY frame type, worker to front, with the same framing, MAC and binding as V5-I.5's frames. Its payload is one progress line (`{"id", "event", "data"}`, `:339-340`) of the request. Every frame whose bytes the front writes to the client for (g, r, s), `PROGRESS_BYTES` and `RESPONSE_BYTES` alike, carries an output sequence number `out_seq` inside its MAC'd binding, assigned in production order (v7 V7-I.3): progress emitted before the handler returns precedes the response, and progress emitted afterwards by detached work (`:390-393`) follows it. The front writes the frames strictly in `out_seq` order, so the client receives the bytes in the order the original's writer would; it writes while the client connection is open, and drops a frame otherwise, exactly as `_send` drops writes to a closing writer (`:394-400`).
v8:
`PROGRESS_BYTES` is one more RELAY frame type, worker to front, with the same framing, MAC and binding as V5-I.5's frames. Its payload is one progress line (`{"id", "event", "data"}`, `:339-340`) of the request. Every frame whose bytes the front writes to the client for (g, r, s), `PROGRESS_BYTES` and `RESPONSE_BYTES` alike, carries an output sequence number `out_seq` inside its MAC'd binding, assigned in production order (v7 V7-I.3): progress emitted before the handler returns precedes the response, and progress emitted afterwards by detached work — which the original sends through the generic writer `_send` (`rw/daemon.py:388-400`; `:390-393` are its explanatory comment, not the send) — follows it. The front writes the frames strictly in `out_seq` order, so the client receives the bytes in the order the original's writer would; it writes while the client connection is open, and drops a frame otherwise, exactly as `_send` drops writes to a closing writer (`rw/daemon.py:394-400`).
```

**R8-4 replaces v7 line 947 (in C7-VAG, V7-A.1).** V7R-CITE: `:207` is the base roster.
```text
v7:
**The `decide_v2` roster.** `wl_resource_child_execution_decide_v2`'s `PARAMETERS` roster is V1's (`rw/resource_child_execution.py:207`) in V1 order, with `FactsV2` and then `Selection` inserted immediately before `Output` (R6-7). Both are rosters (`slot_kind` 2; size word = element count) whose `record_kind`s are R6-7's (k) and (k+1). The material serializes this roster without `Output`, so `decide_v2`'s `param_count` is V1's `param_count` plus the two inserted rosters. The X-8 convention-P argument list (R6-7) is exactly this roster's pairs, in this order, then the output record.
v8:
**The `decide_v2` roster.** `wl_resource_child_execution_decide_v2`'s `PARAMETERS` roster is the base V1 `PARAMETERS` roster (`rw/resource_child_execution.py:207`) in that order, with `FactsV2` and then `Selection` inserted immediately before `Output` (R6-7). Both are rosters (`slot_kind` 2; size word = element count) whose `record_kind`s are R6-7's (k) and (k+1). The material serializes this roster without `Output`, so `decide_v2`'s `param_count` is the base roster's `param_count` plus the two inserted rosters. The X-8 convention-P argument list (R6-7) is exactly this roster's pairs, in this order, then the output record.
```

**R8-5 replaces v7 line 1066 (in C7-VAG, V7-F.1).** V7R-CITE: `C1:241` writes the init pid.
```text
v7:
When the HELD frame arrives (it carries the init's host pid p at `C1:241` and its pidfd P at `C1:247`), the front:
v8:
When the HELD frame arrives (it carries the namespace init's pid p — its pid in the host PID namespace — written at `C1:241`, and the init pidfd P at `C1:247`), the front:
```

**R8-6 replaces v7 line 1163 (in C7-VIQ, V7-K.1).** V7R-CITE: `:161` closes resource-state owners; the sandbox require is `:733-735`.
```text
v7:
The front's owners are closed while a coordinator owns custody (`rw/protected_root_resource.py:161`), and the coordinator cannot reach the manager (M-4). `launch_reserved` requires a sandbox `argv[0]` (`rw/protected_scoped_resource_runtime.py:732-735`), and `launch_root_worker` uses `handler_plan`'s `worker_policy` and coordinator argv; neither fits. D-H7 is the request-root launch, run by the coordinator as custody owner, step for step against `launch_reserved` (`:698-776`):
v8:
The front's resource-state owners are closed while a coordinator owns custody (`rw/protected_root_resource.py:161`); its custody and transport descriptors survive in escrow. The coordinator cannot reach the manager (M-4). `launch_reserved` requires a sandbox `argv[0]` (the require at `rw/protected_scoped_resource_runtime.py:733-735`), and `launch_root_worker` uses `handler_plan`'s `worker_policy` and coordinator argv; neither fits. D-H7 is the request-root launch, run by the coordinator as custody owner, step for step against `launch_reserved` (`:698-776`):
```

**R8-7 replaces v7 line 1167 (in C7-VIQ, V7-K.2 step 1).** V7R-CITE: the journal check boundary is `:705`.
```text
v7:
| 1. checks | journal row `NEVER_DISPATCHED`, no slot, original request unchanged (`:703-708`) | the same, in the coordinator |
v8:
| 1. checks | journal row `NEVER_DISPATCHED`, no slot, original request unchanged (the `NEVER_DISPATCHED`/no-slot require at `:705`, the original-request require at `:707-708`; `:704` loads the journal) | the same, in the coordinator |
```

**R8-8 replaces v7 line 1168 (in C7-VIQ, V7-K.2 step 2).** V7R-CITE: `:729` is `from_mapping`; the cgroup2 require is `:730-731`, the sandbox require `:733-735`.
```text
v7:
| 2. plan | `resource_launch_material` (`:711`), whose non-root branch returns `policy['plans'][op]['launch']` with its executable checks (`rw/protected_operations.py:476-485`) | the same branch and checks. The plan's `policy` and `systemd_properties` are used, with `enforcement == 'cgroup2'` and `systemd_properties == policy.unit_properties ()` required exactly (`:729-731`). The plan's `argv`, `environment` and sandbox check (`:732-736`) apply to each per-agent child (V7-K.1), not to the request root's main process |
v8:
| 2. plan | `resource_launch_material` (`:711`), whose non-root branch returns `policy['plans'][op]['launch']` with its executable checks (`rw/protected_operations.py:476-485`) | the same branch and checks. The plan's `policy` and `systemd_properties` are used (`:729` is `ResourcePolicy.from_mapping`), with `enforcement == 'cgroup2'` and `systemd_properties == policy.unit_properties ()` required exactly at `:730-731`. The plan's `argv` and `environment` checks (`:724-728`, `:736-738`) and the sandbox require (`:733-735`, `:732` binds the sandbox path) apply to each per-agent child (V7-K.1), not to the request root's main process |
```

**R8-9 replaces v7 line 1182 (in C7-VIQ, V7-K.3).** V7R-CITE: the cgroup2 require is `:730-731`.
```text
v7:
The request root's policy is the WL operation's own launch plan's `policy`, `policy['plans'][op]['launch']['policy']`: the policy the serial route admits at its fresh boundary (`rw/protected_operations.py:687`) and the one `launch_reserved` enforces for that reservation (`rw/protected_scoped_resource_runtime.py:729-731`). It is not `worker_policy`. Per-agent leaves take the runner's own `resource_properties=self.gate.unit_properties ()` (`rw/runner.py:697-703`).
v8:
The request root's policy is the WL operation's own launch plan's `policy`, `policy['plans'][op]['launch']['policy']`: the policy the serial route admits at its fresh boundary (`rw/protected_operations.py:687`) and the one `launch_reserved` enforces for that reservation (the `enforcement == 'cgroup2'` and `systemd_properties == policy.unit_properties ()` require at `rw/protected_scoped_resource_runtime.py:730-731`). It is not `worker_policy`. Per-agent leaves take the runner's own `resource_properties=self.gate.unit_properties ()` (`rw/runner.py:697-703`).
```

### B.3 Superseded v7 text

| v7 lines | v7 content | Status in v8 |
|---|---|---|
| 1-127 | Header; §A.1 … §A.5 (answers to the v6 review) | Superseded by the v8 header and §A. History, not normative; §A.3 of this file states every ruling's owner and evidence. |
| 869-930 | §C truth boundary, bases, labels, numbers | v8 §C, which restates every alias and label |
| 1107-1124 | V7-H (the `:192` wedge fix, defective per V7R-H) | v8 V8-H |
| 1406-1526 | Appendices A … D | v8 Appendices A … D |

Every other v7 line outside the §B.1 slices is a separator or an empty line (Appendix C). The withdrawals W5-1 and W5-2 stay in force (inside C5-B, inside C6-B, inside C7-B). v8 makes no new withdrawal.

### B.4 Reading rules

- **RR8-1.** Inside carried v7 slices, v7's reading rules RR7-1 … RR7-7 (in C7-B) apply, and the aliases are those of v8 §C.2.
- **RR8-2.** A reference inside carried text to a superseded v7 section resolves through §B.3: v7 V7-H, V7-H.1, V7-H.2 → v8 V8-H, V8-H.1, V8-H.2; v7 §A, §C and the appendices → v8 §A, §C and the appendices.
- **RR8-3.** "v7 X" inside an R8 text means v7 section X as carried, with its R8 replacements; "v8 Y" means this file's section Y.
- **RR8-4.** An R8 that replaces a line of an R7 block's `v7:` result text changes that R7 replacement's result; the block's `v6:` quoted text is unchanged, and the R7 instruction still applies to its v6 target with the corrected result. No R8 replaces a line that any earlier R replaces, and no line is replaced twice (Appendix C).
- **RR8-5.** Numbers inside carried slices keep their status: observed, or JACKAL exact (v2 J01 … J18; v5 J5-1 … J5-4; v7 J7-1, J7-2). They are not re-derived.
- **RR8-6.** "AUTHOR-NOTES" inside a carried v7 slice means v7's `AUTHOR-NOTES.md` (`b651f5e6…9da6`), bound in Appendix B; it binds nothing normative.
- **RR8-7.** The installed-runtime check rename RC-10/11/12 → RC-13/14/15 of v7 §C.5 stands unchanged; v8 adds no further rename. The inherited required changes RC-01 … RC-12 are untouched.

---

## C. Truth boundary, bases and method

### C.1 What was done

- **Reading only.** The Read tool and read-only Bash (`sed -n`, `awk`, `grep`, `sha256sum`, `wc`, `command ls`, and `python3` on files or `-c` snippets — never on standard input). No git command was run. One read-only helper script was written under `scratch/` (AUTHOR-NOTES §5) and run as `python3 scratch/<name>.py`.
- **Not run.** No compiler, prover, test, WORLDLINE, COSMOGONY or root-worker code (nothing imported or executed), service, `systemctl`, sudo, namespace, project-vault or restic. Nothing under `/srv`.
- **Not read.** `WT/packets/capi-pk0/`; every `gpt61-v*` directory; the v7 review's `raw-final-message.txt` and `review-records/`; `~/.local/share/sia/.gbrain/`; any other agent's transcript. The lane draft and its preimage were read and not changed.
- **SIA.** No SIA call in the v8 task. No SIA note.
- **Skills.** The eight Ada skills were loaded in this session before Ada reading: `ada`, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`, `ada-2005-amendment`, `ada-high-integrity`.
- **JACKAL.** No call in the v8 task (no numeral was derived); v7's J7-1 and J7-2 are carried with their status.

### C.2 Bases (aliases)

As v7 §C.2 (which restates every version's aliases, carried through C7-B's reading rules), with two additions for this revision:

| Alias | Path |
|---|---|
| `D7` | `WT/designs/claude-root-worker-seam-design-v7` |
| `D7R` | `D7/review/claude-v1` (the sealed independent review of v7) |

All other aliases (`W`, `WT`, `L`, `R`, `rw/`, `pre/`, `C1`, `P1/`, `D2` … `D6`, `D5R`, `D6R`, `CAPI4` … `CAPI6`, `CAPI5R`, `CAPI6R`, `S5`, `A1`, `CHILD`, `RQC`, and the per-version `D:n` line forms) are v7 §C.2's, unchanged.

### C.3 Status labels

As v7 §C.3: OBSERVED; STATIC_REASONING; [unverified reasoning] naming a K or RC item; (bound to the sealed CAPI6R); DESIGN; OPEN.

### C.4 Numbers

Line numbers, counts, sizes and hashes in this document are observed. No numeral in v8 was derived by arithmetic, so no JACKAL call was made for v8; v7's J7-1 and J7-2 are carried with their status (`exact`, lane `rat`, `formal=false`), and the capacity rule they support is unchanged.

### C.5 The RC families

Unchanged from v7 §C.5 (carried): the inherited required changes RC-01 … RC-12, and the lead-owned installed-runtime checks RC-1 … RC-9 and RC-13, RC-14, RC-15 (the last three named RC-10, RC-11, RC-12 before v7). v8 renames nothing further.

---

## Map against v7 (the §18.5 map)

v8 is v7 with two corrections and nothing else. This map is exhaustive: every v8 change against v7.

| v8 element | v7 element | Change |
|---|---|---|
| Header, §A | v7 header, §A | Rewritten: answers the v7 review (V7R-H, V7R-CITE) instead of the v6 review; carries the rc_closure, the ruling table and the carried-closed set forward. No design statement changes except as the two required changes dictate. |
| §B (C7-B, C7-VAG, C7-VIQ slices + R8-1 … R8-9) | v7 §B | New carriage layer: v8 carries v7 by three hash-pinned slices with nine quoted replacements. |
| §C | v7 §C | Restated; adds aliases `D7`, `D7R`. |
| Map against v7 | — | New (this section). |
| V8-H | v7 V7-H | **Rewritten (V7R-H).** The handler before/after is given exactly; the `elif`→`else` preserves `p.quarantine` in every `owned is None` case; the "unchanged"/"plain alternative" claims are corrected. V8-H.2 (Release_Hold scope) is V7-H.2 verbatim in substance. |
| V8-CITE | — | New (V7R-CITE): lists each corrected citation and the R8 that makes it. |
| R8-2 | R7-65 result (v7:674) | Corrected one-liner (V7R-H). |
| R8-1, R8-5 | R7-58 result (v7:618), V7-F.1 (v7:1066) | `C1:241` wording (V7R-CITE). |
| R8-3 | R7-70 result (v7:714) | `daemon.py` progress/`_send` cite (V7R-CITE). |
| R8-4 | V7-A.1 (v7:947) | "V1's PARAMETERS" → base roster at `:207` (V7R-CITE). |
| R8-6 … R8-9 | V7-K.1/K.2/K.3 (v7:1163, 1167, 1168, 1182) | D-H7 boundary cites and "front's owners" (V7R-CITE). |
| V8-M, V8-N, V8-O, V8-P, V8-Q | v7 V7-M … V7-Q | Carried (C7-VIQ). V8-N adds one control (the handler before/after). |
| Appendices A-D | v7 appendices | Restated for v8's identities and companion hashes. |

Every carried v7 section not named above — V7-A … V7-G, V7-I … V7-Q — is bound byte-for-byte by its slice and changed only where an R8 above names its line. No design conclusion of v7 changes.

---

## V8-H. The front after `HANDOFF_ABORT`, with the quarantine preserved (V7R-H; supersedes V7-H; 07.3, 12.2; D-6a, D-9a)

### V8-H.1 The exact edit to `rw/protected_root_worker.py:191-199`

**Before (the lane, verbatim):**
```python
        except BaseException as error:
            self.phase='UNKNOWN_WORKER_OWNERSHIP'
            if owned is not None:
                await owned.retain_and_stop_unknown(error,offer)
            elif self.phase=='UNKNOWN_WORKER_OWNERSHIP':
                # No dispatch owner exists. Preserve the actual original hold,
                # named failure and native quarantine; never invent a release.
                p.quarantine(operation,error)
            raise
```

**After (v8 DESIGN):**
```python
        except BaseException as error:
            if owned is not None:
                await owned.retain_and_stop_unknown(error,offer)
            else:
                # No dispatch owner exists. Preserve the actual original hold,
                # named failure and native quarantine; never invent a release.
                p.quarantine(operation,error)
            self.phase=self.committed_front_phase(operation)
            raise
```

**The three changes, exactly:**
1. **Delete** line `:192` `self.phase='UNKNOWN_WORKER_OWNERSHIP'` from the head of the handler.
2. **Change** line `:195` `elif self.phase=='UNKNOWN_WORKER_OWNERSHIP':` to `else:`.
3. **Insert**, after the settlement branch and before `raise`, `self.phase=self.committed_front_phase(operation)`.

**Why `p.quarantine` survives in every failure case.** The settlement is now a total split on `owned`: `if owned is not None` / `else`. Exactly one arm runs on every exception. In the `owned is None` arm `p.quarantine(operation,error)` runs **unconditionally** — its execution no longer reads `self.phase`, so no phase value can skip it. In the `owned is not None` arm `owned.retain_and_stop_unknown(error,offer)` runs, as before. The original ran the quarantine only because `:192` had set the phase that `:195` then tested; the new form removes that indirection and quarantines directly, so the native settlement is identical to the original in both cases:

| Failure case | `owned` | v7-review reading of the naive "remove :192" | v8 handler |
|---|---|---|---|
| failure before the launch returns (e.g. `_reserve`, `pre_effect`, `RESERVE_USE` replay, or `launch` raising) | `None` | `self.phase` still `'FRONT_OWNED'`, so the `elif` is **False** and `p.quarantine` is **silently dropped** (a changed native settlement) — the defect V7R-H names | the `else` runs `p.quarantine(operation,error)` — settlement preserved |
| failure after `launch` returned a dispatch owner | not `None` | `retain_and_stop_unknown` runs | `retain_and_stop_unknown` runs, unchanged |

So the fix re-establishes the quarantine independently of the removed `:192`, exactly as V7R-H requires. **The handler is changed** — `:192` removed, the `elif` made an `else`, and the phase assignment moved after the settlement. v7's claims that "the original exception handling is unchanged" and that "the `elif` becomes the plain alternative" were wrong and are withdrawn: removing `:192` alone leaves the `elif` guard, whose only reachable case (`owned is None`) then evaluates False and drops the quarantine.

### V8-H.2 The in-memory phase, fail-closed

`committed_front_phase(operation)` (DESIGN, new native helper, unreviewed) is a pure read of the committed root custody phase for the operation's generation (the X-5 fold over the custody chain the design already uses). It returns the in-memory phase the front should hold for routing:
- the committed phase is `FRONT_OWNED (g+1)` (the owners-open route completed) → `'FRONT_OWNED'`, so `:159` and the router `:22` let the front serve;
- the committed phase is `Handoff_Aborted` with owners closed, reconstruction pending → a non-`'FRONT_OWNED'` phase, and the reconstruction task is registered in `front.collectors` by the existing `collect_and_reconstruct` path, which the router `:22`-`:25` awaits (the row-2 path, existing code);
- the committed phase is `Unknown` (a custody commit failed) → `'UNKNOWN_WORKER_OWNERSHIP'`.

It **cannot fail the settlement or mask the original error**: it is wrapped so any read error yields `'UNKNOWN_WORKER_OWNERSHIP'` (fail-closed — the front never serves on uncertainty), and the handler always reaches `raise`, re-raising the original exception. This replaces `:192`'s blanket pin, which forced `'UNKNOWN_WORKER_OWNERSHIP'` even when the custody chain never went Unknown and so wedged `:159` after an ordinary abort.

**What this does not do, and does not depend on.** The handler does not itself commit `FRONT_OWNED (g+1)`; that commit is the existing V5-G.1 route (owners open) or the reconstruction path (owners closed), unchanged. The router row-3 successor change — accepting the *same* front back in `FRONT_OWNED` after `RECONCILED`, a change to `rw/root_worker_endpoint_router.py:26-31` whose `:29` today requires a **distinct** fresh front — stays the OPEN, unreviewed lane-code obligation it already was (V7-P; carried). The quarantine fix of V8-H.1 does not depend on it: the quarantine runs in the settlement branch, before the phase is read, so it holds whatever the router successor does.

### V8-H.3 `Release_Hold`'s scope (V7-H.2 verbatim in substance)

`Release_Hold` requires `Before.Kind = Held_Capacity`, and `Charge_Budget` requires `Irreversible_Budget` with `Terminal` and `Reaped` (`core/resource_run_ledger.ads:317-322`). On a `Never_Launched` abort the root row is released only if it is `Held_Capacity`; an `Irreversible_Budget` root row has no command and keeps its state and budget for owner resolution. `Released_Unlaunched` is set only with a `Release_Hold`. The carried statements R7-4, R7-5, R7-19, R7-20, R7-22, R7-64 and R7-77 (which reference "v7 V7-H.2") read as this section under RR8-2.

---

## V8-CITE. The corrected citations (V7R-CITE)

Each was presented in v7 as an exact line citation; each is corrected by quotation. None changes a conclusion.

| v7 cite | Corrected | Verified at | R8 |
|---|---|---|---|
| `rw/daemon.py:390-393` for the detached-work progress send | those are the explanatory comment; the send is the generic writer `_send` (`:388-400`); the closing-writer drop is `:394-400` | `rw/daemon.py:388-400` (def at `:389`, comment `:390-393`, `is_closing` drop `:394-395`, write/drain `:397-398`) | R8-3 |
| D-H7 step 1 journal checks `:703-708` | the `NEVER_DISPATCHED`/no-slot require is `:705`, the original-request require `:707-708`; `:704` loads the journal | `rw/protected_scoped_resource_runtime.py:704-708` | R8-7 |
| D-H7 step 2 cgroup2 require `:729-731`; `launch_reserved` enforce cite `:729-731` | `:729` is `ResourcePolicy.from_mapping`; the `enforcement=='cgroup2'` + `systemd_properties==unit_properties()` require is `:730-731` | `rw/protected_scoped_resource_runtime.py:729-731` | R8-8, R8-9 |
| D-H7 step 2 sandbox check `:732-736`; V7-K.1 sandbox argv `:732-735` | the sandbox require is `:733-735` (`:732` binds the path); `:736` begins the env loop | `rw/protected_scoped_resource_runtime.py:732-738` | R8-6, R8-8 |
| "front's owners are closed" | `:161` closes the front's **resource-state** owners; custody and transport descriptors survive in escrow | `rw/protected_root_resource.py:161` | R8-6 |
| "V1's `PARAMETERS`" | the base `PARAMETERS` roster at `:207` | `rw/resource_child_execution.py:207` | R8-4 |
| the namespace init's "host pid" "comes from the HELD frame (`C1:241`)" | `C1:241` **writes** the init's pid (its pid in the host PID namespace) | `C1:241` | R8-1, R8-5 |

---

## V8-N. Control added by v8

Joins the additive roster (carried V7-N as amended; **no original control is retired, and the frontier control is unchanged, C2-116**).

- **V8-N.H** (lab, against the exact handler before/after of V8-H.1). For each failure case of V8-H.1's table, the committed operation-journal outcome equals the original's: an `owned is None` failure commits `QUARANTINE_USE`/`QUARANTINED` exactly as the original `p.quarantine` does (no release invented, the hold retained); an `owned is not None` failure runs `retain_and_stop_unknown` exactly as the original. After the settlement, `committed_front_phase` yields `'FRONT_OWNED'` only when `FRONT_OWNED (g+1)` is committed, a non-serving phase while reconstruction is pending, and `'UNKNOWN_WORKER_OWNERSHIP'` when the chain is Unknown or the read fails; `:159` passes exactly when the phase is `'FRONT_OWNED'`. A negative control confirms the naive "remove `:192` only" variant drops the quarantine (the V7R-H defect), so the test distinguishes the two.

---

## V8-M … V8-Q (carried)

V7-M (the full carried-line sweep), V7-N (controls), V7-O (measurements, K-29, RC-13/14/15), V7-P (everything OPEN) and V7-Q (non-claims) are carried verbatim in slice C7-VIQ, with the V7R-CITE line corrections of §B.2 where they fall in that slice. v8 adds control V8-N.H above; it adds no measurement, no open item beyond what V8-H's native helper and the router row-3 change already leave OPEN (both listed in V7-P as carried, and restated in §V8-P below), and no non-claim beyond V7-Q's.

### V8-P additions to the carried open list

- The native body of the V8-H.1 handler edit and of `committed_front_phase`, their proof, and control V8-N.H — OPEN.
- The router row-3 successor change (`rw/root_worker_endpoint_router.py:26-31`) — OPEN, unreviewed lane code, as in V7-P.
- Everything V7-P carries stays OPEN: OB-001 … OB-219; V6-REQ-A … L (V6-REQ-H now closed at design level by V8-H); the nine PARTIALLY_CLOSED V5-REQs; CG-1 … CG-4; CJ-DISP-1..6, CJ-ARCH-1..3, CJ-JSON, CJ-H-1..5, OB-ESC/AU-2; K-1 … K-29, RC-1..7, RC-9, RC-13..15; H′ deltas D-H1 … D-H7 and adoption; all bodies/proofs/costs/controls; the C-API open items; hosted assurance, publication, deployment, final Phase One acceptance; the independent review of v8.

### V8-Q additions to the carried non-claims

- v8 reviews, accepts, proves and authorizes nothing, and adds no approval gate.
- Nothing was compiled, run, imported, proved, tested or measured.
- The V8-H handler edit is DESIGN: the native body and its proof stay OPEN, and no equivalence beyond "the native settlement `p.quarantine`/`retain_and_stop_unknown` is preserved in every failure case" is claimed.
- `committed_front_phase` is DESIGN; the serve-again behaviour and the router row-3 change are OPEN and the quarantine fix does not depend on them.

---

## Appendix A. JACKAL

No numeral in v8 was derived by arithmetic, so no JACKAL call was made for v8; `jackal.json` records this. v7's J7-1 `(2^64 - 1) + 1 - 256^8` and J7-2 `(2^128 - 1) + 1 - 256^16`, both `status=exact`, value 0, lane `rat`, `formal=false`, evaluator `4c0ae28d…5872`, are carried with their status inside slice C7-VAG (they support the capacity rule, unchanged). They are exact rational arithmetic, NOT formal-bounded, informational about arithmetic only.

## Appendix B. Every identity a normative statement relies on (sha256)

Recomputed with `sha256sum` while drafting v8 (observed), except where marked "recorded". This supersedes and re-binds v7's Appendix B, adding the v7 design and review identities.

```
531d11282f811518b868470c0012f23a5e34bdbe3891ef39194cd8f230933f46  D1V/SEAM-DESIGN.md
db512ddb0bc24c1282c45ebbdb035842234a833046b46b702d020cf14027e1b5  D2/SEAM-DESIGN.md
a0f2f411d654f1cce472a1ad2a13d3c082fff42def050c5ed4694a8b094d07a0  D3/SEAM-DESIGN.md
f65629cb45e6e8a5ea798f5130a7f98e1d365758a7175343444f4022864efbda  D4/SEAM-DESIGN.md
938c832d03df0910506756ec295acef86ae2cacba4d7b2478a09c6d27f3685cf  D5/SEAM-DESIGN.md
d385baca2e5eba7a9605c486d1b5afb2f3fc56cae1d893eed9ba163bf1cc0a50  D5R/REVIEW.md
0b9a3b0705df9d40f7b4e109d4f2042cb6236dcc848fd48f32f27a0de5ff8187  D5R/review.json
f41566d8bb694817f27efb4dd336d25e554357976808aad577b91365a9a10787  D6/SEAM-DESIGN.md
2f814fee89819789d6184b3802c3b77ffda45bd3e6e2fe43e264f47e05890d83  D6R/REVIEW.md
da28c753456d8ef10a0042c2ef2e62d9c4162f1cb1922e60e60b58aa2a5c1b39  D6R/review.json
62b7d5877a4df95b86ab5354d64d4fadd6bcf8017da20b8ba53dbbec34169f16  D7/SEAM-DESIGN.md
de716b0bf38671abef088957014885ecd1002380b8eb56f5966230cd1ba2e817  D7/seams.json
f691a36b3a9efbd49e6d56ad2c264f85b0b83f17ab64ef1fd58db698f181263f  D7/jackal.json
b651f5e61fe3deca19e6bed1753bb83e7b93d059cc39a2fbc1ea1768968e9da6  D7/AUTHOR-NOTES.md
4d09a69a8af251f02ea49273ad0c35aa4c39b86628f6be6128f4184a1e19cf9f  D7R/REVIEW.md
4ba840c61dbf5cf58c8291535084cb8db6e2fa3088bb8a236fb24b0f8c309693  D7R/review.json
1770794001691ab77736ef2cbfa4e26f9b107166a3c8bd6adae2248b9c09cda3  D7R/checks.json
c65eed5b2ff472e22eb26e4a17392a5d4e68d3363a1b5ef098f06be94667d2f6  D7R/review-freeze.json
f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2  CAPI5/APPENDIX-BINDINGS.md
9f9f3dfa897d0c320226df39c89bc5c156fc87ebc3e24959ab0c08bba5db1946  CAPI6/APPENDIX-BINDINGS.md
cfa0dca9e275e878b958f2f8da6b5cf54824534867773382965f2a887e98a417  CAPI6/DESIGN.md
73e82489706e03ca465e7dea2aed1823df0b50a8ce1c5ab0555c545579dc34d8  CAPI5R/REVIEW.md            (recorded)
800880d44bff4b234c82cc392a3008fd4d37139b0827d070120cf299370f403b  CAPI5R/review.json          (recorded)
c1398253713aa6d42ed11fda5194502ccae5a64825b36ef8100206f7d40719ef  CAPI5R/checks.json          (recorded)
91bddf1a46763251940db658f5115cd13ab9de4aa67c0a41ae169de165649af1  CAPI5R/review-freeze.json   (recorded)
12cfde3c3eed993b6056dc75d901710bdee1273e67cfe150a9648f99627da161  CAPI6R/REVIEW.md            (recorded)
bcfa259f8690c492b9284ef1ed9549efa7a5d3899edc1fbd5a0ae2ab7234d128  CAPI6R/review.json          (recorded)
12642ce4501f12b0a608264d9bd93a23f39fd6c7d2c85cee69d94a91a3e2f284  CAPI6R/checks.json          (recorded)
15fc9f07786eba0e0c1d3cde0250c8696e8ebeb96961ce6c22aeea2fcc590742  CAPI6R/review-freeze.json   (recorded)
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
25b590b09ebcf81f46726bdc276093a6e9861b6ab60859924eb151525f4adfe3  rw/root_worker_plan.py
a0781e70e8a4b2b630f6956d0c89208140edc871c4a2a003666573767a32d13d  rw/admission.py
774e35565b93aef70420183a591ceb3acf9ddc9148c0b4ae55fb83bb9efc83ce  rw/root_worker_endpoint_router.py
4a8c71fa4617b09af2aab8724375c09fabfb2acb5c1676e10f6690b7153270d9  rw/canonical_owner_witness.py
68740eda2668faddfe28bd3a8ac1720adac3de32f0bc68d8d95e45f94170d07b  rw/root_worker_closed.py
710d37c77de105bdd62d96e1ce31d5b0ad79fcbd7ae8b7e556bd1b7656462784  rw/linux/systemd.py
65a38d24f3c5444bd21bc15ecf8dee6ec9e2e93a71ba911f6678ca9b4797562d  R/core/resource_run_ledger.ads
23c43aaaad873052b8e2e192a4c33a46b1d08f7b427f11f7b27f10602553c07f  R/core/resource_observation_classification.ads
f2a321d07e667e80f4359634e8e4a956b555368b8d449e8c8c930b8f511aeff7  C1
2f3a0b4b3bb2a0996824859c2d9f8a59e7c58f624b2d81cb00e40e76bf588237  P1/HANDOFF.md
```

- **Recorded, not recomputed:** the eight CAPI5R and CAPI6R files live under `review/gpt61-v1`, which this task's limits forbid reading. They are bound as recorded in D4's Appendix B (D4:1873-1876, 1880-1883) and header (D4:10); D4's identity `f65629cb…bda` was recomputed and equals the line above.
- **C-API verdicts (recorded, from D4:10):** CAPI5R ENDORSED_WITH_REQUIRED_CHANGES (V5-RC4-GATE-EXCEPTION, V5-RC4-QUAL-CAPTURE); CAPI6R, of CAPI6 `DESIGN.md` `cfa0dca9…a417`, ENDORSED with no required changes, closing those two and V4-RC4-GATE, V4-RC4-ALIAS, V3-RC4 at design level only; ROOT_WORKER_INTEGRATION "OPEN".

These are byte identities at the time of reading. They establish no authenticity, installed state or atomic snapshot.

## Appendix C. Verification (observed)

A read-only Python script (`scratch/verify.py`, AUTHOR-NOTES §5) read the v1 … v7 designs, the sealed v7 review and this file, and printed to standard output; it wrote no file. Its final run checked:
- v7 `SEAM-DESIGN.md`: sha256 `62b7d587…6f16`, 1526 lines, trailing newline;
- §B.1: every C7 slice's sha256 equals the stated hash; the three slices and the four §B.3 superseded ranges leave only blank or `---` lines uncovered; no overlaps;
- §B.2: every R8's quoted `v7:` text equals the stated v7 line exactly; every target lies in its stated C7 slice; no target was replaced by any earlier R-block (R3 … R7) or lies in a superseded range; no line is targeted twice; R8-1 … R8-9 contiguous;
- the two required-change texts quoted from `review.json` are verbatim; the thirteen ruling owners/evidence quoted in §A.3 equal the sealed v6 `review.json` `rulings[]`;
- the handler before/after of V8-H.1: the "after" is the "before" with exactly the three edits, and `p.quarantine(operation,error)` appears in the sole `else` arm;
- every markdown table row has its header's cell count;
- the carried-line stale-text sweep, re-run on the v8 composition (V8-M-method), shows every remaining hit in a kept class, plus the three §B.2 result-line corrections.

**Final run, observed (`scratch/verify.py`).** v7 base `62b7d587…6f16`, 1526 lines, trailing newline. 3 C7 slices hash-verify; the three slices plus the four §B.3 superseded ranges leave only blank or `---` lines uncovered; no overlap. 9 R8 blocks, contiguous 1-9, each a single-line quote equal to its stated v7 line, each in its stated C7 slice, none in a superseded range, none targeted twice, none previously replaced by any earlier R. Both required-change texts quoted verbatim from `review.json`; the 13 ruling owners/evidence quoted verbatim from the sealed v6 `review.json`. The handler "after" equals the "before" with exactly the three edits of V8-H.1, and `p.quarantine(operation,error)` is in the sole `else` arm. Every table row matches its header's cell count. Problems: none.

**Sweep run, observed (`scratch/sweep.py`).** Over the reader-visible v8 composition (carried v7-slice live text with R8 applied, V7-H dropped, plus v8's own sections and the R8 results; fenced `v6:`/`v5:` old-text quotes excluded, as the composition drops them): all eight V7R-H and V7R-CITE target strings are **RESOLVED** (absent from live text) — the "unchanged"/"plain alternative" handler claim, the `daemon.py:390-393`-as-send cite, `:703-708`, `:729-731`, `:732-736`, `:732-735`, "The front's owners are closed", and "roster is V1's". The superseded V7-H lines (1107-1124) are covered by no slice. The residual stale-class hits are each a kept class already accepted at the v7 review: the capacity/stride *withdrawal* statements; the D-4a *negations* ("no longer says", "none depends on D-4a"); the corrected pidfd rows ("worker gone"/E-CR) and the closure-barrier R1 statement under closed 04.5; the RC-13/14/15 rename-provenance notes and the inherited RC-01…12 required changes; and the V7-M sweep table's own descriptions. No new stale text is introduced.

## Appendix D. Companion file identities

Observed with `sha256sum` and `wc -c` after the files were written. This file cannot contain its own hash; `seams.json` records it, and the handback records both.

| File | sha256 | Bytes |
|---|---|---|
| `jackal.json` | `30f7474c56dafca35f1cde6bbcff2c1ea220a4cf5a4cd3ca652939b51a799f87` | 1066 |
| `AUTHOR-NOTES.md` | `bc16520eb5ddd2b6ec274f68a48c6cbf57c35cedf7c65e74de4662d79029bf87` | 7035 |
| `scratch/verify.py` | `e3382baeb9f60b692c8b5a4061e1cffe7d2aa4f91c7dd28a965eb199a6b36156` | 5985 |
| `scratch/sweep.py` | `e70032760236270118d555df09fdcfc2b9280e22f4b44a4fcca929599f7352df` | 4532 |
| `seams.json` | recorded in the handback (it binds this file's hash) | — |

The two `scratch/` scripts are the read-only verification and sweep helpers (AUTHOR-NOTES §6); they write nothing and bind nothing normative.
