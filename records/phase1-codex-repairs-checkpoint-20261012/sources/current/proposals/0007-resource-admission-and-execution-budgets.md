# 0007 — Resource admission and execution budgets

Status: implemented in 1.4.0.

## The invariant

**WORLDLINE must not start work it cannot responsibly supervise with the resources currently
available.**

The motivating case is concrete. During JANUS II another session's prover held roughly 20 GB of a
32 GB machine. WORLDLINE would have started a world anyway, and a starved world produces evidence
that looks exactly like evidence produced on a quiet machine. For an engine whose product is what
a result is *worth*, "may I safely start this?" belongs in the engine rather than in the host's
OOM killer.

## Three things, kept apart

Confusing any two of these makes either the evidence dishonest or the freshness useless.

| | Where it lives | In `requirementHash`? |
|---|---|---|
| **Admission state** — MemAvailable, swap, pressure, disk bytes and inodes, outstanding reservations | consulted at the moment of the request; shown by `doctor` | **no.** Two runs must not stale each other's evidence because one machine had 21 GB free and the other 32 GB. |
| **Enforced resource policy** — the ceilings a workload is permitted | `limits.resources`, and the execution context | **yes.** A suite that passed under 32 GB is not the same evidence as one that passed under 2 GB. |
| **Observed telemetry** — peak memory, CPU time, task count, whether a ceiling fired | the world's evidence, under `resources.observed` | **no.** An identical verification must not be invalidated because this run peaked 40 MiB higher. |

## Admission is a transaction

A snapshot is not a reservation. Two requests that each observe 20 GB free and each take 16 GB is
the failure this exists to prevent, so the whole sequence runs under one exclusive file lock:

```
observe -> lock -> account outstanding reservations -> reserve -> authorize -> unlock
```

The reservation exists **before** the workload is spawned. It is released when the workload ends,
and anything that escapes that — a daemon killed mid-run — is caught by reconciliation, because
the service manager knows what is running and the ledger does not. The daemon reconciles at start,
and admission ignores any reservation whose unit the manager no longer has.

Accounting withholds only the **unused** part of a live reservation. Withholding all of it on top
of the memory a running workload already took would refuse work the machine can do; withholding
none would overcommit. Every decision records the arithmetic that produced it.

## Outcomes

`ADMITTED` · `RESOURCES_UNAVAILABLE` · `RESOURCE_STATE_UNKNOWN` · `RESOURCE_POLICY_INVALID` ·
`RESOURCE_LIMIT_EXCEEDED`

`RESOURCE_STATE_UNKNOWN` is never reported as `RESOURCES_UNAVAILABLE`. A thing that could not be
measured is not a thing that was measured and found wanting. An unreadable `/proc/meminfo`,
malformed pressure data, an absent memory-pressure file and an unreadable ledger all refuse as
unknown — and an unreadable ledger is not treated as an empty one, which would admit everything at
exactly the moment the accounting broke.

`QUEUED` is deliberately absent. Durable queuing brings priorities, starvation, cancellation,
persistence, fairness and restart semantics; that is a separate project. For now, refuse and
explain.

## Enforcement, not request

Ceilings are applied to the transient **unit**, so every descendant inherits them. An agent that
spawns Python that spawns a test suite that launches a prover stays inside one accounting
boundary; measured on a four-level process tree, every level reports the same cgroup.

`MemoryAccounting`, `CPUAccounting`, `TasksAccounting` and `IOAccounting` are always on, because
telemetry that was never collected is not evidence.

## Requested is not effective

This system keeps asking the right question at the wrong representation. The repository passed
while the release archive did not. The files on disk matched while the loaded process identity was
what mattered. A verifier's final bytes matched while the executed bytes could still differ.

So a configured `memoryMaxBytes` is **not** evidence that Linux enforced it. After launch the
effective ceiling is read back out of the kernel's own cgroup files — `memory.max`, `memory.high`,
`memory.swap.max`, `cpu.max`, `pids.max` — alongside what systemd was asked for, and the evidence
carries `requested`, `effective` and `observed` separately.

Both are sampled **while the unit lives**. `--collect` removes a finished unit and its cgroup, so
a reading taken after the workload ends measures nothing.

## An undeclared appetite is unmetered, not fatal

A default installation declares no ceiling. Refusing it would stop every existing installation
from forking anything, and inventing a number would be a guess dressed as accounting. So a policy
with no `memoryMaxBytes` is admitted **unmetered**: it reserves nothing and enforces nothing, and
the decision, `doctor` and the evidence all say so.

Unmetered means unaccounted, not unguarded. The floors still apply: the machine must still have
free memory, tolerable pressure and disk headroom.

## Configuration

```json
"limits": {
  "defaultTimeoutSeconds": null,
  "resources": {
    "memoryMaxBytes": 12884901888,
    "memoryHighBytes": 11811160064,
    "memorySwapMaxBytes": 1073741824,
    "cpuQuotaPercent": 400,
    "cpuWeight": 100,
    "tasksMax": 4096,
    "timeoutSeconds": 3600,
    "maxConcurrentWorkloads": 2,
    "enforcement": "cgroup2"
  },
  "admission": {
    "minFreeMemoryBytes": 2147483648,
    "minFreeDiskBytes": 2147483648,
    "minFreeInodes": 10000,
    "maxMemoryPressureHundredths": 5000
  }
}
```

Pressure is carried as integer hundredths of a percent and time as integer milliseconds. The wire
protocol is canonical JSON, which has no float, and a value that cannot be represented exactly has
no business being an identity or a threshold.

## What this does not do

- It does not guarantee completion. WORLDLINE reserves against its own ledger and the machine's
  observed state; another process may take the memory a microsecond later. Admission reduces the
  chance of starting work that cannot finish.
- It does not police the host. WORLDLINE governs the workloads it starts and will not stop
  anything it did not start.
- It does not make evidence produced under a satisfied budget correct evidence.
