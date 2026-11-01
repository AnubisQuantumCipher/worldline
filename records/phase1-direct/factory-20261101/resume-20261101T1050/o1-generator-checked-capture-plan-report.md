The counterexample is confirmed in source: heavy ignores cleanup-command exits at127/132. An independently checked pipe-to-file consumer closes that observability gap without changing D158.

Use **two explicit-PID Bash process substitutions**, each executing:

```text
timeout --signal=TERM --kill-after=5s 1650s tee --output-error=exit
```

Give `tee` **no FILE operands**. Redirect its stdout directly to its exclusive capture file and stderr to its separate exclusive diagnostic file. This avoids an extra copied output stream. Pin `timeout` and `tee`.

The exact plumbing obligations are:

1. Create stdout consumer; immediately save its `$!`.
2. Create stderr consumer; immediately save its `$!`. **Inside this second substitution, close the inherited stdout pipe writer before executing timeout.**
3. Run the unchanged guard with stdout/stderr duplicated from the two allocated writer FDs; close both extra FD numbers in the guard child.
4. Capture guard status without allowing `set -e` to skip cleanup.
5. Close both parent writer FDs.
6. Explicitly wait for **both saved consumer PIDs**, regardless of earlier failures. Retain all three statuses.
7. Accept only three zero statuses, four complete regular capture files strictly below8MiB, expected empty successful streams, and the unchanged source/resource/terminal predicates. Metadata retention failure also rejects success.

The root shell must retain unlimited hard FSIZE; apply only its8MiB soft limit. Consumer subprocesses can retain that limit or independently reduce their hard limit; they must not alter the guard’s hard limit.

This is bounded capture plumbing, not a new job scheduler. The1650-second consumer deadline is an **I/O failure deadline**, leaving generator1500/guard1590 deadlines unchanged. Expiry, including delayed EOF from surviving writers, rejects the attempt. It does not authorize terminating an unidentified launcher or claiming cleanup.

With four8MiB files,1MiB metadata and33MiB registered recovery margin, additional allowance is **66MiB =69,206,016 bytes**. Initial capacity minimum becomes **24,120,124,416 bytes**, preserving D158’s entire original budget and reserve.

Failure behavior:

| Failure | Required result |
|---|---|
| First/partial capture write returns EIO/ENOSPC | tee nonzero; reject even if producer’s ignored EPIPE permits heavy exit0 |
| Capture creation/redirection fails | consumer nonzero; retain external bootstrap error and other files |
| FSIZE reached or tee receives SIGXFSZ | nonzero and/or size≥cap; reject |
| Guard nonzero/signal | still close writers and wait both consumers; reject |
| Consumer waits indefinitely for EOF | timeout124/137; reject and reconcile exact owned processes/scope |
| Consumer diagnostic file fails | consumer status remains required; empty diagnostics cannot substitute for zero status |
| Status/receipt write or close fails | reject; external actual process termination remains necessary |
| Root shell interrupted before waits | capture completion UNKNOWN; no successor until owned-process reconciliation |

**Close-error qualification remains a validation obligation.** GNU tee is the trusted checked-I/O boundary: its stdout write/close failure must produce nonzero termination, including when its diagnostic cannot be retained. Installed documentation confirms `--output-error=exit` write-error behavior; native first-write, partial-write, close-error, cap, consumer-death and delayed-EOF fault tests remain UNRUN. Do not claim that dependency verified merely from this proposal.

No hidden process-substitution status may be accepted, and no `wait` may be skipped. Existing exact launcher/scope reconciliation remains mandatory; consumer timeouts provide no replacement for guard cleanup or launcher identity.