**Host core storage is enabled. Inherited CORE=0 can suppress retained dumps through this configured systemd handler, but that is a handler dependency—not kernel pipe suppression.**

Observed configuration:

- `/proc/sys/kernel/core_pattern`:
  ```text
  |/usr/lib/systemd/systemd-coredump %P %u %g %s %t %c %h %d %F %I
  ```
  `%c` passes the crashing process’s soft CORE limit.
- `core_pipe_limit=16`; current parent soft/hard CORE are unlimited.
- `/etc/systemd/coredump.conf` contains only commented defaults. All four applicable drop-in directories and alternative main configurations are absent.
- Effective documented defaults on this64-bit host: `Storage=external`, compression enabled, `ProcessSizeMax=32GiB`, `ExternalSizeMax=32GiB`.
- MaxUse defaults to10% of disk capped4GiB; KeepFree defaults to15% capped4GiB. **These are cleanup targets, not hard storage bounds:** `coredump.conf(5)` expressly permits temporary excess during processing.
- Installed `systemd-coredump@.service` allows processing up to5minutes. Handler work occurs outside the generator’s user scope.

The installed `systemd-coredump(8)` states that processing requires sufficient `RLIMIT_CORE`. The pinned executable also contains the diagnostic `Resource limits disable core dumping for process`. Together with `%c`, this supports **CORE=0 as the existing handler’s suppression control**. No native crash validated that behavior during this inspection.

Smallest launch strengthening, before spawning **any** shell child, consumer, timeout or guard:

```bash
ulimit -S -c 0
ulimit -H -c 0
[[ "$(ulimit -S -c)" == 0 ]]
[[ "$(ulimit -H -c)" == 0 ]]
```

This changes only `RLIMIT_CORE`; retain **FSIZE hard∞** and the reviewed soft FSIZE cap. Hard CORE0 prevents ordinary descendants from restoring a positive limit. D158’s compiler/archive CORE setters remain compatible. The scoped child is expected to inherit it under the documented `systemd-run --scope` behavior.

Limits of the claim:

- CORE0 does not prevent the kernel invoking a piped handler or producing a “dumped core” wait-status indication.
- The handler may still retain crash metadata/log entries; do not claim zero external writes.
- `Storage=none` alone would still permit temporary core writes; the documented host-wide disabling combination is `Storage=none` plus `ProcessSizeMax=0`. No host change is needed or authorized here.
- Previous harness crashes ran without this control. Their outside artifacts remain **UNKNOWN**; future limits do not resolve that history.

**Next step:** register outer soft/hard CORE0 and handler/configuration identities in the permitted operational revision, enforce it before further authorized fault cases, and reconcile only those cases’ exact PID/time metadata for retained-core absence. No crash generation, dump retrieval, broad capacity audit, service change or reclamation occurred.