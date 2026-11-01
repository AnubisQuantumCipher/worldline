Prospective sequence only; **no admission or launch performed**, no judge work inspected, no files written.

1. **Authorization boundary:** require fresh exact-v2 judge approval, explicit transfer from DUAT owner `01a195f9`, then current admission. Inactive service is not owner release. The reported 32 retirements/90 unattempted remain owner-reported state; they confer no storage window.

2. **Fresh preflight, at most 60 seconds old:** record carrier HEAD `aad6dadd56d794940702a54187eafb4d7800ca63`, tracked state and protected vault pins. Require both exact paths absent, including dangling links:
   - `records/phase1-direct/completion-20261026/o1-xgen-build-v1`
   - `records/phase1-direct/factory-20261101/o1-xgen-build-job-v1`

   Independently verify manifest SHA256 `561833c2cfed7979a2148ab0151329ee3c58752aacfa3586c5ddc0c17b0e541e`, every manifest payload, all 342 source pins and 2623 runtime/tool pins, and unchanged heavy-helper hash `c3c7fcc84bb509668d0136606449486d1179d67d7c89bf68f6f5db79a4ece61a`. Preserve immutable review packet `3cfe5702…` and external seals separately from mutable run receipts.

3. **Storage/bridge admission:** fresh bridge-specific device/pairing readback; both expected `fuse.ifuse` mounts, matching vault markers and readable repository object; fresh vault pins/operations/queue readback. Protect carrier, source/tool inputs, package, root captures, W and JOB against retirement. Require filesystem available bytes **≥24,050,918,400**, before separately budgeted root captures. Do not interpret sampled limits as reserved aggregate capacity.

4. **Sole entry point after envelope resolution:** from the exact carrier, with stdin `/dev/null`, clean environment containing only:

   ```text
   PATH=/usr/bin
   LC_ALL=C
   TZ=UTC
   HOME=<absolute W>/control
   PYTHONOPTIMIZE=0
   PYTHONDONTWRITEBYTECODE=1
   XDG_RUNTIME_DIR=/run/user/<actual uid>
   DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/<actual uid>/bus
   ```

   Execute pinned `/usr/bin/python3 -B -W error <absolute package>/xgen_guard.py`. Do not invoke worker/heavy directly or create W/JOB first. Guard calls unchanged heavy helper with `--timeout 1500s --swap-max 0`; helper owns shared flock, post-lock 14GiB MemAvailable admission and actual 8GiB/swap0 verification. First memory refusal cancels; no automatic successor.

5. **Retain supervision evidence:** 60-second admission/lock bound; 1500-second inner deadline plus inherited 30-second kill grace; 1590-second monitor; bounded launcher cancellation and owned-scope cleanup. Preserve all failed outputs, actual process exits, cgroup samples, capacity classes, diagnostics, recovery comparison and hashes.

6. **Terminal readback:** require reaped integer launcher exit and exact scope identity. For a nonempty cgroup require actual well-formed `populated 0`; missing/malformed is UNKNOWN. Normal collected scope requires exact successful native tuple `Id=<owned unit>, LoadState=not-found, ActiveState=inactive, ControlGroup=""`, together with complete inherited unpopulated/inactive terminal receipt. Failure cleanup cannot substitute collected state for population proof. Then repeat external source/tool/helper/manifest/payload identity checks and protected-pin/storage readback. Exit0 remains qualification UNPROVEN and grants no O1/Phase One/F7 acceptance.

**Capture-envelope gap:** guard inherits stdout/stderr. Heavy captures `systemd-run`/wrapper streams in `JOB/launcher.stdout` and `.stderr`; its worker captures actual `timeout + xgen_worker` streams in `JOB/stdout` and `JOB/stderr`. Native build logs are separately retained in `W/live/logs`. Guard/bootstrap output therefore needs exclusive root captures outside W/JOB, with their own budget and supervision.

An unreviewed minimal candidate is two 8MiB root captures, adding **16,777,216 bytes** to admission (**24,067,695,616 bytes total**), with only a soft file limit and unchanged unlimited hard limit. A lowered inherited hard limit would prevent the worker’s 64MiB and archive’s 4,311,744,512-byte setters. However, soft-limit SIGXFSZ could terminate guard before Python cleanup, and outside captures are not monitored by this package. Resolve that exact root capture/supervision envelope through an existing reviewed facility before launch; this plan does not establish one.