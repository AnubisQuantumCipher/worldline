**APPROVE_OPERATIONAL_ENVELOPE — D159 initial review, conditional on every registered prelaunch and completion check.** This is internal operational review only, not runtime admission, generator qualification, F7 or Phase One acceptance. No mandatory defect found within this envelope.

Reviewed carrier HEAD `7a3127281389f58f2291c86d123ec1f920cee6b7`. Before and after review, packet SHA-256 was `705d1623fa8307dbd6bf75108c40a970790c78dfd781e6b78f3ee5c57978fbf5`; all **54 referenced sizes/hashes matched**. Exact command digest `912ba8e198b57efb0187b99e1acc4ba0bcf8d7722097d3df49ea68d4b8824885` and registration digest `951fa47c9164d9d03461a35ab8b5be20c120d2336803598591a4007ca7b2d22c` matched. Installed Bash, env, Python and systemd-run manual matched their pinned bytes, hashes and resolved paths.

**Observed and tested**

- The exact clean, non-POSIX Bash limit sequence yields soft **8,388,608 bytes**, hard unlimited. A pure introspection test raised separate child limits to **67,108,864** and **4,311,744,512 bytes**, respectively; the parent retained soft 8MiB/hard unlimited. No files were created.
- Registration arithmetic totals **24,103,347,200 bytes**, matching its conservative admission minimum.
- Installed `systemd-run(1)` lines 61–65 document caller environment inheritance for scopes. Actual native scope inheritance remains UNRUN.
- Source inspection confirms guard/heavy root emitters inherit the capped descriptors. Systemd-run/worker output is separately redirected before compiler/archive children raise their own limits.

The public introspection command was:

```bash
/usr/bin/env -i PATH=/usr/bin LC_ALL=C TZ=UTC PYTHONDONTWRITEBYTECODE=1 \
/usr/bin/bash --noprofile --norc -c '
set -euC
[[ ! -o posix ]]
[[ "$(ulimit -H -f)" == unlimited ]]
ulimit -S -f 8192
printf "shell_soft_blocks=%s shell_hard=%s\n" "$(ulimit -S -f)" "$(ulimit -H -f)"
/usr/bin/python3 -B -c "import resource; print(\"python_fsize=\",resource.getrlimit(resource.RLIMIT_FSIZE)); resource.setrlimit(resource.RLIMIT_FSIZE,(67108864,67108864)); print(\"compiler_child_limit=\",resource.getrlimit(resource.RLIMIT_FSIZE))"
/usr/bin/python3 -B -c "import resource; print(\"second_child_inherited=\",resource.getrlimit(resource.RLIMIT_FSIZE)); resource.setrlimit(resource.RLIMIT_FSIZE,(4311744512,4311744512)); print(\"archive_child_limit=\",resource.getrlimit(resource.RLIMIT_FSIZE))"
printf "parent_soft_blocks=%s parent_hard=%s\n" "$(ulimit -S -f)" "$(ulimit -H -f)"
'
```

Exit **0**, output:

```text
shell_soft_blocks=8192 shell_hard=unlimited
python_fsize= (8388608, -1)
compiler_child_limit= (67108864, 67108864)
second_child_inherited= (8388608, -1)
archive_child_limit= (4311744512, 4311744512)
parent_soft_blocks=8192 parent_hard=unlimited
```

**Creation, evidence and ownership assessment**

`set -euC`, owner-only fresh directory admission, absent targets and `umask 077` jointly provide the prescribed exclusive creation boundary. Redirections occur left-to-right: failure opening stderr may leave an empty stdout file. That is a retained failed attempt, not grounds for retry or success. Pre-redirection failures require the external native-tool transcript.

The cap is per regular file and is a soft process limit, not aggregate quota or containment against malicious same-UID actors. Approval assumes the registered sole-writer/fresh-directory boundary. Successful streams must be empty: any content, missing capture, cap reached, nonzero/signal exit or observed write/close failure rejects completion. Those postchecks prevent capped/truncated output from qualifying as complete evidence; empty files alone cannot establish success.

Guard loss can leave cleanup unverified. Approval preserves the requirement to establish original launcher identity and quiescence before exact-scope reconciliation; no bare-PID reconstruction, unconditional cleanup claim or successor run is authorized. Normal completion still requires the typed reaped launcher exit, inherited terminal receipt and exact terminal/collected-scope readback.

**Limitations and next step**

No operational command, guard/main, build, service, lock, mount, archive or network action was executed. No peer D159 report was read. Model/effort were requested as Astra/medium; I have no independent backend attestation.

The smallest next step is separate judge review, then fresh native admission: exact identities, sole owner and terminal descendants, DUAT pause/release, bridge and protected pins, fresh exclusive root directory, complete disk budget, and post-lock memory admission. DUAT’s retained receipt describes a paused/released campaign; this review did not establish live storage or terminal state. No reclamation is authorized.

Native capture behavior, compiler/archive execution, cleanup, resource fit, determinism and recovery remain **UNPROVEN/UNRUN**. Acceptance requires their actual retained evidence under unchanged D158; its zero remaining source revisions and separate IPC/F7 boundaries remain intact.