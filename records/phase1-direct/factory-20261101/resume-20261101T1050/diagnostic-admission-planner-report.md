Read-only planning complete. **No admission, lock acquisition, probe, namespace, compiler, proof, or storage mutation executed.** v6/guard-v3 were neither inspected nor used.

1. **Seal first.** D156’s rejected v1 package cannot launch. Require the sole revision’s exact immutable packet, fresh independent/adversarial reviews and separate judge approval. Then require explicit window transfer from DUAT owner `01a195f9-dee5-7cb0-a440-777959511b7c`; completed offloads alone do not transfer ownership. Factory adoption: `FACTORY-v2-ADOPTION.md:50–60,119–131`; composition requirement: `ipc-diagnostic-package-v1/manifest.json:71–90`.

2. **Build a fresh nominal-only admission record using a pure reader.** There is **no existing dry-run CLI**:
   - Running `ipc_diagnostic_guard_v2.py` opens LOG and launches the wrapper (`:276–306`).
   - Running collector with `ipc-probe` launches `parent()` (`ram_qualification_v5.py:930–936`).
   - Guard `preflight()` only checks output absence, reserve and assertions, then constructs operational argv (`guard_v2.py:221–231`).
   
   Safely read JSON/source/AST, resolve/hash files and observe `/proc`, cgroup and namespace metadata; do not import/execute target source functions. Use:
   ```bash
   git --no-optional-locks rev-parse HEAD
   git --no-optional-locks status --porcelain=v1 --untracked-files=all
   sha256sum records/phase1-direct/factory-20261101/ipc-mechanism-preflight-v1.json
   ```
   The historical preflight is navigation only: it names v4 collector/v1 guards and explicitly says post-lock admission UNRUN (`ipc-mechanism-preflight-v1.json:4,21–46`). Generate the new record only after the new package is sealed and root has its writer window.

3. **Recheck the complete identity closure before and after execution.**
   - Preserve/reverify `chunk-proof-preflight-v1.json`’s 168 source pins, 16 absolute tool pins, 1573 runtime sources, 161 driver-input source pins, original `objects`/`attest`/`sparklib` inventories and separate `sparklib_lib` inventory.
   - Compare complete path roster, kind, mode, `mtime_ns`, UID/GID, file bytes and SHA256; separately verify private-dependency manifest, libc, selected PATH resolutions and the exact newly sealed collector/probe/guard/heavy-wrapper/package/review hashes.
   - Evidence: `ipc-admission-independent-check-v1.json:200–255`; `chunk-proof-preflight-v1.json:4,339,9061,9703,9770`.
   - Nominal collector’s internal `source_state()` verifies **only collector and probe**; it does not implement that full closure (`ram_qualification_v5.py:361–378`).

4. **Avoid self-reference.** Package manifest excludes itself; externally pin its finalized hash (`manifest.json:90`). Keep the immutable input inventory separate from the newly generated admission record, its external seal/readback, monitor log, job directory and inner-output directory. Explicitly register those exclusions and capture their terminal inventories separately. Do not include a mutable root receipt in its own hash map, rewrite a sealed receipt after embedding its digest, or treat expected output growth as source drift. Old failure records remain preserved. No broader historical exclusion is established by this inspection.

5. **Fresh capacity/ownership predicates.**
   - Single integrator, sole source writer released, explicit storage handoff, current reservation/pin disposition, no competing heavy lane, terminal prior owned scopes/descendants/mounts and released heavy lock.
   - Exact new JOB/INNER/LOG absent via `lexists`, including dangling symlinks.
   - Current host `/dev/shm` directory identity, parent IPC/mount namespaces and deterministic **new-inner-path-derived** witness/semaphore names absent (`collector:465–480`).
   - Registered archive/restore/retrieval overlap and output budgets; actual `f_bavail*f_frsize` above unchanged reserve plus admitted peak, startup +60MB and sampled stop +30MB.
   - Core limit0; assertions enabled; bytecode disabled; exact PATH/tool resolutions; working user systemd bus.
   - Actual **post-lock** MemAvailable ≥14GiB; worker cgroup readback exactly8GiB/swap0. Wrapper enforces these at `scripts/phase1_heavy.py:64–92,139–150`. Historical free-space/memory observations confer no admission.

**Draft operation only:** the old reviewed command shape is:
```bash
ulimit -c 0
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -W error \
  records/phase1-direct/factory-20261101/ipc_diagnostic_guard_v2.py
```
It internally invokes `phase1_heavy.py --out JOB --timeout 240s --swap-max 0 -- python COLLECTOR ipc-probe` (`guard_v2.py:229–231`). **Do not execute this rejected version.** Substitute only the exact subsequently sealed, approved successor command. Preserve tool/collector/wrapper/monitor deadlines180/220/240/270s, all original budgets and first-refusal/no-successor behavior (`README.md:81–99`).

Additional pitfalls: heavy wrapper creates `tracked.diff` before lock/admission (`phase1_heavy.py:52–65`), so bound/register current dirty-diff size; its internal memory retry is otherwise unbounded (`:60–72`), hence the guard must retain its first-refusal stop and bounded cleanup. Lock-free observation is momentary; namespace identities and deterministic names must be recomputed for the actual fresh path. Sampling is not a quota or atomic reservation.

Smallest sound next step: seal/review the sole revision. Acceptance evidence for this **diagnostic only** additionally requires fresh admission, actual raw archived stdout/stderr, complete recovery comparison, explicit tool/collector/guard exits, noOOM/cgroup evidence, exact-source readback, terminal owned-scope/descendant/mount cleanup and independent raw-result review. No mechanism qualification or Phase One acceptance follows.

<oai-mem-citation>
<citation_entries>
MEMORY.md:613-622|note=[carrier and historical admission boundaries checked against current source]
</citation_entries>
<rollout_ids>
01a1787b-9465-7363-96e3-47c837eec185
</rollout_ids>
</oai-mem-citation>
