Use the existing files for manual root readback; no new checker or approval is implied.

Let `W=records/phase1-direct/completion-20261026/o1-xgen-build-v1` and `JOB=records/phase1-direct/factory-20261101/o1-xgen-build-job-v1`.

1. **Actual termination and retained receipts**

   Read external root exit/captures; `W/control/guard.jsonl`; and JOB’s `launch.jsonl`, `result.jsonl`, `worker-result.json`, `xgen-worker-result.json`, `scope.jsonl`, `terminal-scope.jsonl`, `launcher.stdout/.stderr`, `stdout`, `stderr`.

   Success requires actual root, heavy and worker exits all integer zero; complete final guard event with `normal_wrapper_exit=true`, `outer_exit=0`, `reason=null`; no signal, timeout, receipt write/flush/close failure or capture exhaustion. A JSON exit never overrides actual nonzero termination.

   The successful worker receipt intentionally remains:

   ```text
   execution = OBSERVED_TERMINAL_PENDING
   source_validation/build/generation/determinism/recovery = OBSERVED
   exit = 0
   terminal = UNKNOWN
   qualification = UNPROVEN
   acceptance_credit = false
   ```

   Do not rewrite those labels. External terminal evidence completes the operational observation separately.

2. **Exact seven-stage command/diagnostic evidence**

   `xgen-worker-result.json.stages` must contain the successful sequence:

   ```text
   target, version, minimal, core, helpers, generation-a, generation-b
   ```

   Each requires actual `exit=0`, identities matching the complete `W/live/logs/<stage>.stdout/.stderr`, each stream strictly below **67,108,864 bytes**, and `diagnostic_validation=OBSERVED_EXACT_PROGRESS_OR_SILENCE`.

   - Target: precisely one LF-terminated `aarch64-linux-gnu` stdout record; empty stderr.
   - Version: precisely one LF-terminated `16.1.0` stdout record; empty stderr.
   - Minimal/core/helpers: empty stderr; stdout exclusively exact stage-specific records from sealed `progress-policy.json`, or silence.
   - Both generations: both streams empty.

   Unknown progress, warnings, missing final LF, CR/tab/control/non-ASCII bytes, records over4096 bytes, over8192 records, hash drift or exact-limit captures fail. Do not trim or extend the whitelist after failure. Check retained argv against the original DEBUG/static, strict warning/check, fixed `-j2` commands.

3. **Source-specific template correspondence and twice-generation**

   Read sealed `template-roster.json`, staged `W/live/source/spark/src/why/xgen/xtree.adb`, its21 templates, `generation_evidence`, and both `W/live/generation-a` / `generation-b`.

   Require the exact ordered21 `Process` names;35 unique `Add` callback names;35 template placeholder occurrences whose name set equals those callbacks. This source-specific join is essential: delimiter absence alone cannot detect lines deleted after unknown callbacks.

   Each generation contains exactly the21 roster outputs plus21 templates. Every output is a nonempty regular file with neither `_@` nor `@_`. All21 output byte counts/SHA256 values agree across generations and with `generation_evidence.outputs`; `generation_evidence.executable` matches the same unchanged `xtree` used for both runs.

4. **Full local payload recovery**

   Read `recovery_evidence`, `W/control/recovery-inventory.json`, `create.stdout/.stderr`, `extract.stdout/.stderr`, `W/archive/live.tar`, and `W/restore`.

   Require `recovery_evidence.state=OBSERVED_COMPLETE`; create/extract actual exits zero; all four streams empty, with strict matching counts/hashes and each below262144 bytes. The archive is strictly below **4,311,744,512 bytes**, matching its recorded identity and unchanged across restoration.

   Require the inventory receipt’s count/hash to match. Compare every live/restored relative name, kind, permission mode, file byte count and SHA256, plus live/restored root mode. Preserve the original staged source bytes and generated CGPR files within that recovered payload.

   Inventory bounds remain8192 entries,4GiB logical payload,64MiB individual files, supported names no longer99 ASCII bytes, and no links/hardlinks/special objects or privilege modes. This establishes local payload recovery only; UID/GID, nanosecond timestamps, ACLs/xattrs, whole filesystem metadata and DUAT retirement remain outside its claim.

5. **Actual resources and terminal state**

   Read JOB’s `admission.jsonl`, `admitted.json`, `cgroup.jsonl`, `supervisor.jsonl`, `rusage.json`, `scope-journal.txt`; guard samples; and fresh exact-unit terminal readback.

   Require post-lock MemAvailable≥**15,032,385,536 bytes**, actual `memory.max=8589934592`, `memory.swap.max=0`, retained peak/events evidence and no OOM kill. Confirm all registered capacity classes, reserve/shutdown margin and finite deadlines held; report measured RSS separately from aggregate cgroup peak. Sampling is not a disk quota or protection against unrelated writers.

   Bind receipts to the exact owned scope and reaped launcher. Require well-formed actual `populated 0` for a retained cgroup; alternatively, normal completion may use the exact collected-scope tuple plus complete inherited unpopulated/inactive receipt. Missing population evidence is UNKNOWN. Failure cleanup cannot treat collection alone as population proof.

6. **External identity and final classification**

   Repeat root manifest/payload/helper/source/tool identities, staged342 source identities, protected pins and carrier source state against the admitted packet. Include root-envelope Bash/env identities and capture size/hash readback. Successful files do not prove unobserved runtime limits, sandbox semantics or fsync durability.

   **Any failed predicate:** retain the first native attempt as FAILED or INCOMPLETE; preserve actual failure, partial logs/archive/restore and UNRUN stages. No automatic successor, whitelist expansion, revision or D158 reset.

   **Every predicate satisfied:** root may record the fixed generator prerequisite as **TESTED/OBSERVED successful build, twice-generation determinism and local payload recovery**, subject to independent raw-result review. Keep package `qualification=UNPROVEN`; this does not close **O1, D47, Phase One or F7**, establish semantic adequacy, or authorize DUAT retirement.