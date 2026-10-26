# Source-only RAM legality driver — UNRUN / UNQUALIFIED

This proposal imports and calls the unchanged current `ram_qualification_v2` helpers. It does not patch helper globals, seed existing objects, compile dependencies, link, run GNATprove, or infer legality from a filesystem probe. No job has been run. Current disk admission prevents launch.

The two adapter GPRs keep the actual origin Source_Files/imports and resolve relative source paths to the identical sources. Only each main Object_Dir moves to a new owned mountpoint. The single-target command is `gprbuild -c -u -j1 -v ... target.adb -cargs -gnatc -gnatwe`; the actual verbose compiler invocation must contain all strict switches and exactly the requested target, or no pass is recorded.

Root must review the proposal and, only after admission, create the selected empty directory `object-mounts/reservation` or `object-mounts/utf8` under this proposal. The driver rejects absent/nonempty/symlink mountpoints. Do not precreate them now or use `-p`. No existing object directory is overlaid or writable. Imported Attest/SPARKlib outputs stay readonly; an unexpected required write is retained as a failure, not a reason to widen mounts.

A later authorized invocation needs the original toolchain environment and heavy wrapper, `PYTHONDONTWRITEBYTECODE=1`, and `PYTHONPATH` explicitly prepending the parent completion-20261026 directory. Arguments are target (`reservation` or `utf8`), new bounded run label, and the independently reviewed proposal.json SHA256. One invocation handles one target. No command is authorized or run by this document.

The retained v2 sandbox provides read-only host root and read-only recreated `/dev`. All compiler outputs, temporary/cache files and stdout/stderr share a 32MiB tmpfs with1024inodes. Restore is a separate32MiB tmpfs. A preallocated8MiB archive uses the retained hard-limited writer and full RAM restore comparison. Direct driver receipts enforce a cumulative4MiB ceiling. Original outer-wrapper records and terminal-scope evidence remain separate and binding.

Success requires actual exit0, one recognizable strict compiler invocation, no warnings/errors, unchanged exact sources, private mounts gone, and complete verified retention. Any admission refusal, unrecognized response-file invocation, timeout, OOM, cap/inode/archive exhaustion, missing receipt or lost ephemeral data means failure/no credit. All failed output that can be retained remains evidence; no guaranteed-retention or proof claim is made.

Historical v1 retained a real devnull/readonly-Attest failure; current v2 probe was stopped by storage admission before tool start. Both are pinned in proposal.json. The source-pinned current helper has not earned runtime qualification from earlier helper versions. Target legality, replay/UTF8 semantics, integrated proof, resource and Phase One acceptance remain UNRUN/OPEN.
