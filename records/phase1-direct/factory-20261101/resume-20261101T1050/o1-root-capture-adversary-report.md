**REJECT — D159 initial operational envelope.**

The 8MiB limit mechanism works under the stated regular-file preconditions, but the prescribed postchecks do not establish the required rejection of every root-capture write failure.

**Mandatory defect: an empty capture can conceal a failed diagnostic write.**

Registration line 30 requires any write/close error or nonzero termination to fail. However, [phase1_heavy.py](/home/sicarii/Work/worldline-phase1-direct-20261019/scripts/phase1_heavy.py:127) discards the `CompletedProcess` from both cleanup commands at lines 127 and 132. They inherit root stdout/stderr. The launch shell only opens regular files and applies `RLIMIT_FSIZE`; it does not supervise writes or record those subprocess exits.

A reproducible fault-injection scenario for a later authorized test is:

1. Worker result is zero, while heavy enters cleanup because its launcher still runs.
2. Cleanup `systemctl stop` attempts a diagnostic on inherited stderr. Its first write fails with `EIO` or transient `ENOSPC`, leaving the capture empty; the command exits nonzero.
3. Heavy discards that exit. The scope subsequently becomes terminal/collected, `process.wait()` completes, and heavy returns the worker’s zero.
4. Guard accepts the valid terminal/collected receipts and returns zero.
5. External postchecks find two regular, single-link, empty capture files; matching identities; zero root exit; and valid terminal receipts.

Those observations cannot distinguish this lost diagnostic from genuinely empty streams. Reopening, hashing and checking size cannot recover the missing write-error evidence. The defect concerns observability, not fsync durability.

**Evidence classification:** the discarded exit statuses and inheritance are OBSERVED in pinned source. The fault scenario is a source-derived counterexample; native fault injection is **UNRUN**, as required by this review’s read-only envelope.

**Verified observations**

- Before and after: HEAD `7a3127281389f58f2291c86d123ec1f920cee6b7`.
- Before and after: packet SHA `705d1623fa8307dbd6bf75108c40a970790c78dfd781e6b78f3ee5c57978fbf5`; **54 references, zero size/hash mismatches**.
- Before and after: all **four launch-tool pins match**, including resolved paths.
- Command SHA remains `912ba8e198b57efb0187b99e1acc4ba0bcf8d7722097d3df49ea68d4b8824885`.
- Registration SHA remains `951fa47c9164d9d03461a35ab8b5be20c120d2336803598591a4007ca7b2d22c`.
- Manifest remains `561833c2cfed7979a2148ab0151329ee3c58752aacfa3586c5ddc0c17b0e541e`; D158 source was neither changed nor reopened.

Public limit-introspection command, executed without operational entrypoints or file creation:

```bash
/usr/bin/env -i PATH=/usr/bin LC_ALL=C TZ=UTC /usr/bin/bash --noprofile --norc -c 'set -euC; [[ ! -o posix ]]; printf "initial soft=%s hard=%s\n" "$(ulimit -S -f)" "$(ulimit -H -f)"; [[ "$(ulimit -H -f)" == unlimited ]]; ulimit -S -f 8192; printf "capped soft=%s hard=%s\n" "$(ulimit -S -f)" "$(ulimit -H -f)"; exec /usr/bin/python3 -B -c "import resource; print(\"child RLIMIT_FSIZE=\", resource.getrlimit(resource.RLIMIT_FSIZE)); resource.setrlimit(resource.RLIMIT_FSIZE,(67108864,67108864)); print(\"compiler child limit=\", resource.getrlimit(resource.RLIMIT_FSIZE))"'
```

Observed exit 0:

```text
initial soft=unlimited hard=unlimited
capped soft=8192 hard=unlimited
child RLIMIT_FSIZE= (8388608, -1)
compiler child limit= (67108864, 67108864)
```

Separately executed:

```bash
/usr/bin/env -i PATH=/usr/bin LC_ALL=C TZ=UTC /usr/bin/bash --noprofile --norc -c 'set -euC; ulimit -S -f 8192; exec /usr/bin/python3 -B -c "import resource; resource.setrlimit(resource.RLIMIT_FSIZE,(4311744512,4311744512)); print(\"archive child limit=\", resource.getrlimit(resource.RLIMIT_FSIZE))"'
```

Observed exit 0:

```text
archive child limit= (4311744512, 4311744512)
```

The enclosing tool command’s measured wall time was approximately 0.073 seconds, below the 60-second aggregate introspection allowance.

Pinned installed `systemd-run(1)` documents caller execution-environment inheritance for `--scope`. Actual scoped-worker limit inheritance remains **UNRUN**. Source confirms compiler/archive children receive separately redirected streams before changing their limits.

Bash documentation also confirms that `noclobber` rejects existing **regular** files. It is not a special-file exclusion mechanism. Thus exclusive creation, absent targets, checked ancestors and directory custody remain necessary preconditions; this command establishes no protection against a hostile same-UID writer.

**Ownership and terminal boundary**

The proposal correctly preserves exact launcher ownership, terminal reconciliation, and the prohibition on successors after unverified cleanup. It does not claim unconditional emergency cleanup. The DUAT stop receipt and all five referenced identities match; that verifies retained receipt bytes, not current live quiescence or capacity. No reclamation was attempted.

**Smallest sound next step**

Use D159’s remaining operational revision to provide checked capture supervision that detects output and capture write/close failures independently of discarded child statuses, while leaving the sealed D158 package unchanged. Required acceptance evidence includes first-write failure, partial-write failure, cap overflow, redirection failure, nonzero/signal exit, and terminal/ownership reconciliation.

After resolving that defect, fresh native admission still requires the registered source/tool/pin, owner/descendant, bridge/vault, exclusive-path, capacity and post-lock memory checks. This review grants no runtime admission, O1 qualification, F7 acceptance or Phase One completion. No peer report was read.

<oai-mem-citation>
<citation_entries>
MEMORY.md:1697-1701|note=[Historical assurance boundaries checked against current governing documents]
</citation_entries>
<rollout_ids>
</rollout_ids>
</oai-mem-citation>