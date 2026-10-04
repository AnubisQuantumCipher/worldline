# Workflow lineage in the isolated worktree

From 2026-10-04 ~19:00Z the lead's mutable workflow records continue here.

The guarded shared tree `work/claude-workflow-v1` is **read-only** for the lead from now on (see `../ISOLATION.md`).
Its tools, packets 01–14, overlays, `REPAIR-MAP.md`, `README.md` and `ledger.json` stay exactly as they are, as
inputs and history.

## Copied, byte-identical at copy time (sha256)

| File | sha256 |
|---|---|
| `ledger.py` | `f70850f49ff0a0de92cfdb3737dcae37b484f7dfeb67f760805d593eaffdb20d` |
| `ledger.json` | `172b51fee23e76ebc2e3d0b7126802160b4e9b6aa1377a822195a3571f0a608c` |

The ledger state at copy is 3187 items: 3028 OPEN, 159 DRAFTED, 0 ENGINEERING_VERIFIED, 0 REVIEWED,
0 STRICT_VERIFIED. The last change before the copy, D1431/D1432 → DRAFTED (packet 13), was made in the guarded tree
through `ledger.py` in Bash. It is recorded in `../ISOLATION.md`.

## Superseded statements in the read-only tree

**`REPAIR-MAP.md`**, the storage bullet "unit-run margin 81956060 bytes (JACKAL exact, 18:30Z) and falling". That
figure used past outputs as bounds. It is superseded by the Gate 0 in `../RUNBOOK-first-proof-iteration.md` (v4):
- a labelled-allowance requirement of 9304350902252/1397 bytes;
- a margin of −7648075570156/1397 at 18:49Z;
- result: NOT ESTABLISHED, DEFERRED.

**Frozen frame v5 `FRAME.md`**, "Storage representation". The phrases "the measured `obj` growth bound used by the
storage gate" and "decides whether even a single unit run can be budgeted" carry the same flaw. The frame is frozen
and under review, so it is not edited. Any successor `FRAME.md` will state allowances, not bounds.
