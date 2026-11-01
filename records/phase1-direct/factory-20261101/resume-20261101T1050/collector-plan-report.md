The smallest successor is a fresh v4-derived collector plus a literal-only guard copy, with one separate diagnostic consumer. Preserve the original mechanism checker and exit behavior.

Verified preimages:

- Collector `ram_qualification_v4.py`: `2cb4bdc25dfec576c5117d303406193f1d8ad4b083946f7f5df874f0ca165716`
- Guard `ipc_capacity_guard_v1.py`: `b82daae76209bb40acc6898bde0043fb9e41e0658bdd34f957e8052a3bedb50e`
- V3 probe: `8d7816d6a37ed353c6682dd27b97c4b7cbbc95f7e20282cb84a4c10177b16260`

Proposed exact patch scope:

1. Copy collector to `completion-20261026/ram_qualification_v5.py`.
2. Change only probe path/pin, fresh output suffix to `ram-qualification-ipc-probe-v5`, and the diagnostic-consumer additions below.
3. Copy guard to `factory-20261101/ipc_diagnostic_guard_v2.py`. Change `JOB`, `LOG`, expected inner output path and collector filename to fresh identities. Preserve guard functions and control flow.
4. Admit only fixed `ipc-probe` → probe `normal`. No automatic successor or other mode launch.

The guard cannot run byte-unchanged: it hardcodes occupied v1/v4 output/log paths and the v4 collector. Its unchanged logic can be reused through a reviewed literal-only successor with a new exact hash. The guard currently contains no collector/probe hash pin; root must retain fresh prelaunch and terminal exact-hash checks.

Add a small diagnostic consumer that reads **archived `tool.stdout` first**, independently of the optional `tmp/private-ipc-probe.json`. Save a bounded `mount-diagnostic-check.json` and reference it from parent `result.json`. Keep existing `check_ipc_retained`, positive predicates, `tool_ok` and parent return condition unchanged.

That consumer should:

- Require complete verified archival retention before interpreting the diagnostic.
- Validate evidence size, row/count accounting, row ordering/index uniqueness, completeness and candidate hash against the exact retained strings.
- Validate the one decimal opened-FD mount ID and compare it with the first field of every retained candidate row.
- Establish correlation only when exactly one retained row has that ID. Record selected-row versus opened-row agreement separately.
- Record missing ID999, duplicate IDs, incomplete rows or malformed evidence as explicit **UNPROVEN/REFUSED interpretation**, retaining raw stdout/archive references. `complete=true` alone establishes retention, not the join.
- Never substitute the joined row into the original selector or change mount acceptance.

For the expected repeated original predicate failure, preserve:

```text
probe tool exit2
inside collector exit0 after complete inventory/archive/restore
parent collector exit1
guard exit1 after normal terminal readback
mechanism UNQUALIFIED
```

The old nominal run already demonstrated this retention structure: tool exit2, inside exit0, complete 485-byte archive containing all five entries, parent/guard failure. Its missing result-file error was secondary. V5 should expose the newly retained stdout diagnostic without replacing that actual failure.

Existing `inside()` already saves `tool-result.json` before inventory and archives stdout/stderr despite a nonzero tool exit. Keep that order and unchanged archive/restore functions. Unsupported entries, quota exhaustion or incomplete restoration still fail with existing bounded failure logs and **LOST_EPHEMERAL_OUTPUTS**, never complete-retention credit.

Preserve all bounds:

| Boundary | Existing limit |
|---|---:|
| Output and separate restoration filesystems | 32MiB / 1,024 inodes each |
| Archive / collector receipts | 8MiB / 4MiB |
| Outer metadata / monitor log | 4MiB / 512KiB |
| Scope / swap | 8GiB / zero |
| Post-lock available memory | 14GiB |
| Linux reserve | 10,000,000,000 bytes |
| Guard admission / sampled stop margin | reserve +60MB / +30MB |
| Tool / collector / heavy wrapper / monitor | 180s / 220s / 240s / 270s |

Keep original bounded cleanup, first memory-refusal cancellation, core0, optimization0 and bytecode suppression1. Sampling remains cooperative observation, not a quota.

Before launch, require fresh paired review and judge of the exact collector/guard/consumer package, synthetic tests for exit2-without-result, mismatched result/stdout, ID999, duplicate IDs, incomplete evidence and archive failure, registered fresh output/recovery budgets, and an explicit current storage-owner window.

Afterward root and the independent reader must rehash the complete archive and every inventory member, inspect full stdout/stderr and tool outcome, verify source/tool/runtime/original-output identities, host-name absence, actual cgroup limits/OOM counters, empty private mountpoints, exact inactive/unpopulated scope and released lock.

Pretty-result versus compact-stdout overflow and receipt-before-final-close remain material caveats. An earlier result file must never override nonzero tool termination or later failure stdout.

This single nominal diagnostic cannot qualify the mechanism, even if it unexpectedly succeeds. The five other controls, compiler/proof work and all product/F7 gates remain separate. No files or runtime state changed during this planning pass.