**Correction: my previous reservation paragraph was incomplete. Its proposed 24,188,281,856-byte floor is insufficient and must not be used for admission.** Preserve that plan as incomplete; this addendum grants no execution or decision-review revision.

Use this conservative additive ledger, with `MiB = 1,048,576 bytes`:

| Reservation | Additional bound |
|---|---:|
| Existing original floor | 24,178,844,672 bytes |
| Already registered D160 dossier + R2 metadata + D161 source/R3 metadata | 16 MiB |
| New configuration package + complete recovery allowance | 2 + 2 MiB |
| New review metadata + complete recovery allowance | 2 + 2 MiB |
| Configuration live root + complete recovery allowance | 1 + 1 MiB |
| Helper/control roots + complete recovery allowance | 8 + 8 MiB |
| Fresh D159 capture derivative roots + complete recovery allowance | 33 + 33 MiB |

Thus:

```text
base                    = 24,178,844,672
previous additions      = 16 MiB
new package/review/live/helper additions
                        = 26 MiB
fresh capture additions = 66 MiB
total additions         = 108 MiB = 113,246,208 bytes

proposed conservative floor
                        = 24,292,090,880 bytes
```

Without a new capture allocation, the arithmetic would be **24,222,884,864 bytes** (baseline plus 42 MiB), but that is **not** the selected composition and does not justify omitting capture custody.

Prefer a **fresh derivative of the original D159 capture package**, binding its exact entry/launcher/guard/control paths to the new configuration package. Retain its capture, descriptor, timeout, consumer-status and identity checks. Initial allowlisted environment custody must still precede the first Bash; the entry script alone does not prove that prerequisite.

Reuse `scripts/phase1_heavy.py` only inside that finite outer composition. Its backoff/lock/cleanup loops and ambient-environment handling prevent treating it as independently qualified. Missing terminal evidence—including missing `cgroup.events`—remains **UNKNOWN**, never observed `populated 0`; helper-reported `populated=false` alone cannot authorize a successor.

Keep the existing **1 GiB shutdown-growth margin unchanged**. Reconcile these reservations against the current ledger, actual retained failed outputs and any additional allocations before admission; the arithmetic is a proposed conservative bound, not measured capacity or a reservation against unrelated writers.

No writes or runs occurred. **No admission granted. F7 NOT PERFORMED.**