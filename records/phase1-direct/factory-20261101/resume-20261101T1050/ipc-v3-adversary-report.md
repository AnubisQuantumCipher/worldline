**APPROVE revision 2 solely as adequate to prepare a separately reviewed successor collector/guard.** No mandatory defect remains in the counter-fit repair. This grants no launch authority, qualification, proof, Phase One gate or F7 credit.

**VERIFIED:** Packet SHA-256 is `09689e1fd544ea1c6f2bb99b1dbc267974f619acf88e1852ccae1ea2c1b68623`; all **42 references** match declared sizes and hashes. Independent AST comparison confirms only `shm_mount_evidence` changed from v2; all other function and nonfunction AST remains identical. All four original v1 `record_os_evidence` requirement calls remain present.

**TESTED, pure synthetic:** Independently reproduced the historical 27-row, 3466-byte counterexample. V2 loses candidate evidence before reading fdinfo. V3 retains **14/25 candidates**, records **11 omissions**, preserves candidate digest `7002e71ef42de9719a32ab2799a143e9dfeabebb0113a0499c9015dd5d2172f6`, retains mocked opened FD ID `3`, then refuses with `shm candidate evidence incomplete: bound refusal`. Encoding measures **2638 bytes before FD metadata, 2665 afterward**.

At `probe.py:124–133`, each adopted prefix is measured with its final counters and completeness value. Rejecting the next addition preserves the preceding bounded envelope. Additional independent checks covered 110 bounded counter/length fixtures, JSON expansion, late selected-row omission, invalid FD IDs and original mount failures. No repair counterexample emerged.

The following mandatory consumer counterexamples remain:

- **Unknown FD ID:** BASE with `mnt_id: 999` returns retention `complete=true`, although no retained row matches.
- **Duplicate mount ID:** Appending `3 2 0:3 /ipc /dev/shm rw - tmpfs tmpfs rw` likewise permits `complete=true` with an ambiguous ID join.
- **Serialization disagreement:** A synthetic report measured **7800 compact bytes versus 8193 pretty bytes**. Compact stdout fitting cannot establish that the result-file write succeeded.
- **Terminal precedence:** With in-memory result capture and a mocked final tmp-FD close failure, `finish` records an earlier `PASSED` result and subsequently raises. Terminal failure must override that earlier receipt.

Accordingly, the successor must require a **unique retained-row FD-ID join** before claiming correlation. Unknown, missing, ambiguous or incomplete joins remain **UNPROVEN**. Retention completeness establishes neither safe topology nor qualification. Preserve the original selector, predicates, ceilings, overflow refusal and terminal-failure precedence.

**Review history:** Two reviewer harness attempts stopped because their late-selected fixtures incorrectly assumed one large ancestor would force overflow. A targeted measurement showed a single maximum-length ancestor still fits at 2779 bytes. The corrected two-ancestor fixture explicitly refuses while preserving the selected structured record and opened ID. These were harness expectation failures, not source failures.

**UNPROVEN/UNRUN:** Real topology, descriptor correlation, IPC behavior, collector/guard composition, runtime resource enforcement and whole-system correctness. Synthetic execution remained below the aggregate 60-second allowance. No files or pycache were written; no receipt-writing main, actual probe, IPC, mount, namespace, compiler, prover or storage operation ran.

**Smallest sound next step:** Separate judge resolution of this exact packet, followed by preparation and exact-source review of the successor collector/guard. Acceptance evidence must include unique-join negative controls, preserved resource/predicate pins, both serialization boundaries and terminal-status precedence. The sole revision is consumed; histories remain retained.

Backend model/effort identity is not independently attestable within this reviewer; root must verify native routing provenance before relying on this verdict.