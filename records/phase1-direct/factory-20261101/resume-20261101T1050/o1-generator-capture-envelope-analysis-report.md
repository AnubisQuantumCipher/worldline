**No finite static bound exists for inherited root streams.** A soft-only file cap is the smallest concrete capture solution; complete failure reconciliation remains conditional.

Source findings:

- Guard creates heavy in a fresh session, inheriting root stdout/stderr: `xgen_guard.py:347`. Guard itself has no normal stream emissions during `run()`; monitoring and caught errors go to `guard.jsonl` (`343–375`).
- Heavy’s Git subprocesses capture stdout but inherit stderr (`phase1_heavy.py:55–56`). `flock` and its locked helper inherit both streams (`64–66`); `numfmt` inherits stderr (`76`). These producers have no explicit output bound here.
- After launcher redirection (`93–94`), heavy’s own cleanup `systemctl stop/kill` still inherits root streams (`127,132`). The lexical `with stdout/stderr` does not redirect these calls.
- Actual `systemd-run`/worker-wrapper streams go to `JOB/launcher.stdout/.stderr`; actual timeout/worker streams go to `JOB/stdout/.stderr` (`151–152`).
- Scoped searches of carrier scripts and factory Python sources found **no reusable reviewed root-capture facility**. The discovered guard derivatives provide owned cleanup, not external root-stream supervision.

The smallest candidate envelope is:

1. Register two exclusive root-control capture files outside W/JOB, each capped at **8MiB**. Add **16,777,216 bytes** to admission: minimum **24,067,695,616 bytes**, plus separately registered root metadata.
2. Apply **only soft RLIMIT_FSIZE=8MiB**, retaining the fresh inherited unlimited hard limit. Compiler and archive children can then set their existing 64MiB and 4,311,744,512-byte hard limits. Preserve clean environment and sole guard entrypoint.
3. Retain actual process exit and both capture sizes/hashes. Any nonzero, signal, capture size ≥cap, missing stream or failed close is FAILED; capped output never qualifies as complete evidence.
4. Perform separate terminal reconciliation using existing exact-unit parsing and observation (`owned_scope`, `scope_observation`, bounded `stop_scope`). Preserve the guard/heavy receipts and external readback together.

**Cleanup qualification:** capture overflow signals the *writing process*, not the guard merely sharing its FD. Thus child overflow ordinarily leaves guard cleanup available. However, `cancel_launch_group()` requires the original live `Popen` relationship and deliberately avoids signalling once its child is reaped (`115–119`). An external root cannot safely reconstruct that relationship from a bare PID or fabricate a `Popen` object. `cleanup_owned()` also requires launcher cancellation **before** reading the scope receipt (`224–245`); exact-scope stopping alone does not establish launcher quiescence.

Consequently, normal completion can use existing receipts plus exact terminal readback without new software. If guard termination loses that cleanup path, root must establish current original launcher-group identity/quiescence before exact-scope cleanup; absent that evidence, record **cleanup UNVERIFIED and prohibit a successor**. I cannot certify unconditional cleanup from two capture files and native scope commands alone.

The durable DUAT stop receipt was read: it records user-paused reclamation, 32 completed remainder items, native worker terminal, and 90 unlaunched items. Runtime admission remains ungranted.