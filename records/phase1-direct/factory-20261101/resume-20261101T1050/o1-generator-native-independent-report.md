**Verdict: retained evidence supports normal wrapper termination with a failed worker. It does not establish successful generation, failure-cleanup execution, or qualification.**

Read-only verification on `b916c7a9f550613bb1daa54f31ecd6b1f59a0ba6`:

- **OBSERVED:** closure packet SHA256 matches `a456f5f1ad116ac4af5b846e06d25c63076e5081fd8d651134e2ba6ee9bc39e0`. All 7 closure references and 38 result-review references match their sizes/hashes. Checkpoint D158 manifest, helper and operational-source pins match. Parent is exactly `7a3127281389f58f2291c86d123ec1f920cee6b7`; tracked diff is empty.
- **OBSERVED:** all 461 failed-inventory entries remain present; file hashes match and total logical file bytes equal **4,739,339**. Inventory is preservation evidence, not recovery evidence.
- **FAILED:** actual root tool exit **1**, guard/heavy/worker **125**, minimal `gprbuild` **4**. Target/version exited **0**, reporting `aarch64-linux-gnu` / `16.1.0`. Native-session public call/result fields and timestamps match the extracted packet; omitted session metadata explains whole-payload inequality.
- **FAILED:** retained compiler diagnostic identifies `gnatcoll-boyer_moore.adb:77:06` obsolescent renamed predefined unit. Actual command and partial ALI retain `-gnatwa`/`-gnatwe`; no warning weakening observed.
- **OBSERVED:** admission recorded 19,228,788 KiB available memory; running cgroup cap 8,589,934,592 bytes, swap cap zero, retained peak 105,226,240 bytes and sampled OOM counters zero. Collected-unit `MemoryMax=infinity` is terminal default output, not evidence that the running cap changed.

**Terminal assessment:** the guard source and receipts agree: typed reaped launcher exit 125 → complete inherited terminal receipt → exact fresh collected tuple → `normal_wrapper_exit=true`, with no guard failure-cleanup call. My fresh read-only `systemctl show` confirms the exact scope is `not-found`, `inactive`, empty `ControlGroup`. Initial readback lacked bus environment; retry with the recorded user-bus environment succeeded.

Preserve two limitations:

1. Heavy-helper `populated=false` derives from absent `cgroup.events` after collection; it is **not** a literal observed `populated 0` sample. The terminal conclusion depends on the complete chain, not collection alone.
2. Root capture still says `cleanup=UNDETERMINED_EXTERNAL_RECONCILIATION_REQUIRED`, and worker terminal remains `UNKNOWN`. Neither should be rewritten as cleanup-proved. Exact scope inactivity is confirmed; absence of every possible differently named successor was not independently surveyed.

The proposed three-site `Ada.Unchecked_Deallocation` canonicalization addresses a materially distinct, newly observed dependency/compiler compatibility failure. This finding **does not approve the derivative, reset D158/D159 zero revision budgets, or authorize rerun**.

Smallest sound next step: retain this failed attempt and prepare a separately reviewed compatibility dossier with exact preimage/patch/derived identity and unchanged strict gates. Future acceptance requires clean dependency builds plus lifecycle/dependent-consumer validation and complete generator evidence on the admitted source.

Core/helpers, generation, determinism and recovery **UNRUN**; derivative behavior **UNPROVEN**; generator **UNQUALIFIED**; **F7 NOT PERFORMED**. No writes, tests, operational drivers, mutation, network or storage expansion performed.