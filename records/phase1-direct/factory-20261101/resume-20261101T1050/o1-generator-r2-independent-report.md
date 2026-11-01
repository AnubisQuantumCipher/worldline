**APPROVE_SOURCE_PREPARATION** for the exact revision-2 packet. No surviving mandatory source-preparation defect found. This grants **no runtime/storage admission**, O1 closure, Phase One acceptance, or F7 credit.

Identity independently observed before and after review:

- HEAD: `aad6dadd56d794940702a54187eafb4d7800ca63`.
- Packet SHA256: `3cfe570241560773312a07ad5f9cfae1413d12ea30ffb52b7d6cf8f5d10f1b0e`.
- Package manifest: `561833c2cfed7979a2148ab0151329ee3c58752aacfa3586c5ddc0c17b0e541e`.
- All **130 packet references** matched byte counts and SHA256 before and after; all **40 manifest payloads** matched.
- Live read-only verification matched **342 input pins / 3,751,237 bytes** and **2,623 tool/runtime pins / 402,438,744 bytes**.

The two mandatory repairs are supported by source inspection and independently executed synthetic tests:

1. `xgen_guard.run` checks final receipt retention. Final write, flush, short-write, and budget failures convert otherwise successful termination to `125`; existing nonzero codes remain nonzero. Failure invokes the existing bounded cleanup independently of logging, with no second cleanup on an already failed monitor path. Entry-point context-manager close failure overrides successful `SystemExit`, preventing successful process termination. This is not fsync durability evidence.
2. Build and recovery validation checks complete captured files against strict length/hash identities. All three build stages validate both streams; stderr must be empty, stdout admits only finite exact registered progress records. Both recovery stages require silent streams. Unknown output, warnings, incomplete/control-byte records, missing evidence, malformed identities, hash drift, overflow and nonzero tool status fail. Rejected diagnostic interpretation continues hashing the full bounded capture.

Unchanged controls were inspected and tested: input/profile/common bytes, command flags and fixed `-j2`, separate compiler/archive limits, template callback join, shared heavy helper, cancellation order, malformed population remaining UNKNOWN, collected-scope distinction, and terminal receipt binding. The helper still uses post-lock 14 GiB admission, 8 GiB memory and swap zero; its otherwise unbounded paths depend on the external guard’s finite containment. Sampled capacity is explicitly **not** an aggregate quota.

Reproducible test command, executed in `records/phase1-direct/factory-20261101/o1-xgen-build-package-v2`:

```bash
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 XGEN_READ_ONLY_TESTS=1 \
  /usr/bin/python3 -B -W error source_tests.py
```

Raw result:

```text
Ran 68 tests in 0.200s

OK
```

Exit `0`. Entrypoint and selected fixtures were inspected first. This is independent execution of the supplied suite, not independent test authorship or proof of coverage. No filesystem fixtures, operational main, compiler, generator, archive, service, IPC, lock, network operation, or filesystem write was performed.

Pin verification command:

```bash
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -W error - <<'PY'
import xgen_common as c
for name in ('input-pins.json','tool-runtime-pins.json'):
    rows=c.load_json(c.HERE/name)
    c.verify_pins(rows)
    print(name, 'verified', len(rows),
          'bytes', sum(r['identity']['bytes'] for r in rows))
PY
```

Raw output:

```text
input-pins.json verified 342 bytes 3751237
tool-runtime-pins.json verified 2623 bytes 402438744
```

The public tool record also retains the exact before/after byte-count/SHA256 verification scripts and outputs:

```text
packet_references 130 mismatches []
manifest_references 40 mismatches []
after_packet_references 130 mismatches []
```

**Remaining UNRUN/UNPROVEN:** actual warning-free native compilation, compatibility of native progress output with the finite policy, generator determinism, full native recovery, sandbox/cgroup/launcher composition, resource fit and filesystem overhead. The tested warning/storage failures are synthetic integration cases; authentic producer reachability was not demonstrated. Conservative rejection of legitimate unknown progress remains possible and must retain failure without automatic policy expansion or another revision.

Smallest sound next step: preserve this exact packet for the separate fresh judge after both reviews finish. Only subsequent explicit current storage-owner handoff and admission may permit the one fixed attempt. Required execution evidence remains complete retained diagnostics, same-executable two-generation identity, full recovery comparison, resource observations and exact terminal evidence. D47 translator baseline and independent F7 remain open.

<oai-mem-citation>
<citation_entries>
MEMORY.md:701-710|note=[carrier identity and separation of bounded review from Phase One acceptance]
</citation_entries>
<rollout_ids>
</rollout_ids>
</oai-mem-citation>