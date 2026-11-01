**Verdict: retained evidence supports normal terminal wrapper completion with a failed worker. It does not qualify the generator or authorize a successor run.**

Read-only verification completed on carrier HEAD `b916c7a9f550613bb1daa54f31ecd6b1f59a0ba6`, parent `7a3127281389f58f2291c86d123ec1f920cee6b7`, tree `d0a3b94925fd99be66c874f25ee1b131ddca14be`.

- **OBSERVED — integrity/provenance:** closure packet SHA256 exactly `a456f5f1ad116ac4af5b846e06d25c63076e5081fd8d651134e2ba6ee9bc39e0`. All seven direct references and 38 nested review-packet references match. Extracted public tool fields and timestamps match native session lines 4861, 4863, 4868 and 4871; the extraction intentionally omits internal metadata.
- **OBSERVED — source preservation:** tracked diff is empty. Operational source and helper bytes match the checkpoint identities and committed HEAD. D158’s 40 payloads, D159’s 253 manifested descendants, 342 input pins, 2,623 tool/runtime pins and 16 capture-tool pins match. FIFO was only `lstat`-checked; fixture symlink was only `readlink`-checked.
- **FAILED — first native attempt:** actual root tool exit **1**; capture status guard `WAIT_STATUS:125`; both consumers `WAIT_STATUS:0`; guard/heavy-worker exit **125**; minimal `gprbuild` exit **4**. Target/version stages exited **0**, retaining `aarch64-linux-gnu` and `16.1.0`.
- **OBSERVED — immediate compiler failure:** `gnatcoll-boyer_moore.adb:77:06` emits the obsolescent renamed predefined-unit warning. Strict `-gnatwa`/`-gnatwe` remain enabled in actual argv and partial ALI evidence. The staged body’s SHA256 and Git blob match acquisition receipt line 249 for `AdaCore/gnatcoll-core@1d4374ae9187fd14d42ca99a3deb0ab2ff1ebc55`.
- **OBSERVED — resources:** post-lock admission recorded `19228788 kB` available; cgroup cap **8,589,934,592 bytes**, swap cap **0**, recorded peak **105,226,240 bytes**, and retained memory-event observations show zero OOM/OOM-kill/max events. This is failure-run measurement, not capacity qualification.
- **OBSERVED — failed inventory:** independently checked exact path set, modes and file hashes: **461 entries, 4,739,339 logical bytes**, no mismatch. Inventory alone establishes no recovery.

The terminal claim is supported **jointly** by the typed, reaped launcher exit `125`, guard `normal_wrapper_exit=true` with `reason=null`, complete inherited terminal receipt, and exact fresh collected tuple. My fresh `systemctl show` also returned exit 0 with the same exact unit ID, `LoadState=not-found`, `ActiveState=inactive`, and empty `ControlGroup`. No cleanup artifact or guard cleanup call is evidenced. The selected current process scan found no matching successor, and the heavy-lock observation contained no matching lock row; this is a bounded observation, not an all-process or hostile same-UID guarantee.

**Precision caveat:** the helper’s inherited `populated=false` follows missing cgroup files in its last observation; its implementation maps missing `cgroup.events` to false. It is **not** an independently sampled `populated 0`. Keep `normal_terminal_readback.terminal=false`, `populated=null`, `collected_scope=true`, root `cleanup=UNDETERMINED_EXTERNAL_RECONCILIATION_REQUIRED`, and worker `terminal=UNKNOWN` intact. Collection alone would be insufficient for failure-cleanup proof. These limitations do not contradict the narrower normal-wrapper-completion classification supported by the combined evidence.

The prospective three-site `Ada.Unchecked_Deallocation` canonicalization is a **materially distinct dependency/compiler compatibility issue**. Local runtime declarations explicitly identify the legacy unit as the renaming and support the proposed interpretation. Its build success, behavioral equivalence, downstream compatibility and complete selected configuration/runtime provenance remain **UNTESTED/UNPROVEN**; no `.cgpr` was retained. It changes dependency input identity and therefore needs separately reviewed derivative provenance and execution authority. It neither resets nor spends nonexistent D158/D159 revisions: **both remain zero**.

**UNRUN:** core/helpers, generation, determinism and recovery. **UNQUALIFIED:** generator. **F7 NOT PERFORMED; Phase One remains open.**

Smallest sound next step: the separate judge evaluates this unchanged packet, followed by a distinct dependency-compatibility dossier identifying exact preimage/derivative boundaries and required acceptance evidence. No implementation, test execution, retry, admission, release or acceptance is approved by this review.

<oai-mem-citation>
<citation_entries>
MEMORY.md:701-703|note=[carrier isolation and acceptance evidence boundaries rechecked against current source]
</citation_entries>
<rollout_ids>
01a1787b-9465-7363-96e3-47c837eec185
</rollout_ids>
</oai-mem-citation>