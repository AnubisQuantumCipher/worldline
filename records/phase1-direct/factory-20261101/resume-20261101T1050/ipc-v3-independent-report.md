**APPROVE — only preparation of a separately reviewed successor collector/guard.** No mandatory unresolved defect found within this revision’s bounded evidence-retention scope. This is not independent product acceptance.

**Verified identity and scope:** Packet SHA-256 matches `09689e1fd544ea1c6f2bb99b1dbc267974f619acf88e1852ccae1ea2c1b68623`; all **42 references** match declared byte counts and hashes. Reviewed source SHA-256 is `8d7816d6a37ed353c6682dd27b97c4b7cbbc95f7e20282cb84a4c10177b16260`. Independent whole-top-level AST comparison against pinned v2 confirms only `shm_mount_evidence` changed. Original predicates, constants, selection policy, cleanup and terminal reporting remain unchanged. Read carrier `AGENTS.md` and factory `ADA-SPARK-AND-SKILLS.md`.

**TESTED independently, without receipt-writing mains:** Two bounded Python invocations totaled approximately **1.29 seconds** of synthetic-check execution, with `-B -W error`. No probe main, real IPC, namespace/mount operation, compiler/prover, or filesystem write was performed.

- Reproduced the pinned v2 defect: final envelope **2817 bytes**, exceeding **2816**, losing mount evidence before FD observation.
- Exact revised fixture: **25 candidates, 14 retained, 11 omitted, complete=false**, **2638 bytes** before FD metadata, correct candidate hash and retained mocked FD observation; explicit incompleteness refusal.
- Re-executed **286 counter-width fixtures**, inherited predicate/stacked-row/overflow checks, and all five inherited boundary cases: 512 rows, escaped 2048-byte row, oversized selected ID, 513-row rejection, and 2049-byte rejection.
- Added independent negative cases: missing, duplicate, overwidth and nonnumeric FD-ID fields retain the incomplete candidate envelope and raw fdinfo, then reject.
- Added escaped backslash and quote cases that permit **zero retained rows**: candidate count/hash, omitted count and available FD ID survive; refusal remains explicit.
- Maximum accepted 20-digit FD ID fits the unchanged final evidence ceiling.

**Repair adequacy:** `probe.py:123–135` constructs and measures each proposed prefix using its final counters and completeness flag before adoption. Overflow leaves the preceding valid envelope intact. `record_os_evidence` publishes that envelope, reads and retains FD evidence, then enforces incompleteness refusal. This repairs the demonstrated failure without changing topology predicates or resource ceilings.

**Mandatory successor obligations remain open:**

1. **Retention completeness is not descriptor correlation.** Unknown FD ID `999` and duplicate retained mount IDs can still have `complete=true`; independently reproduced. A successor must require a **unique retained-row join** for the opened FD ID before resolving hidden-row selection versus actual topology failure. Missing or ambiguous joins remain **UNPROVEN**.
2. **Pretty/compact overflow remains inherited.** `save_result` applies the 8192-byte ceiling to pretty JSON; stdout uses a smaller encoding. Either refusal/overflow prevents qualification. Overflow fallback explicitly discards mandatory fields and does not establish cleanup.
3. **Terminal failure overrides earlier receipts.** `finish` can save the result before closing the temporary-directory FD. A prior apparent success cannot override nonzero termination or replace final stdout, cleanup, archive and readback evidence.
4. Input failures outside ordinary retention-cap refusal can still prevent complete observation. No claim of universal diagnostic evidence completeness is established.

**Evidence classification:** Source identity and structural preservation are **OBSERVED**; bounded synthetic behavior is **TESTED**; no formal correctness claim is **PROVED**. Actual v3 execution, live topology discrimination, collector/guard composition, mechanism qualification and integrated resource behavior remain **UNPROVEN/UNRUN**. The v2 defect remains recorded as **FAILED**, not erased.

**Smallest sound next step:** Root may prepare the separate successor consumer, explicitly encoding unique FD-row correlation and failure precedence, then obtain exact-source composition review with deterministic negative tests and preserved resource/ownership limits. Any actual launch requires separate admission and full terminal evidence. No Phase One gate, execution authorization, qualification or F7 credit follows from this approval; the sole revision budget and prior histories remain unchanged.