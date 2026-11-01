**APPROVE_SOURCE_PREPARATION — revision2 only.** No mandatory defect survived this read-only review. This grants no runtime/storage admission or acceptance credit.

- **OBSERVED:** HEAD remained `aad6dadd56d794940702a54187eafb4d7800ca63`. All **130 packet references matched before and after**. Packet SHA256: `3cfe570241560773312a07ad5f9cfae1413d12ea30ffb52b7d6cf8f5d10f1b0e`; package manifest: `561833c2cfed7979a2148ab0151329ee3c58752aacfa3586c5ddc0c17b0e541e`.
- **OBSERVED:** Original inputs, runtime/tool pins, profile, roster and common helpers are byte-identical to v1. Existing operational function changes are confined to `xgen_guard.run`, `xgen_worker.stage_command` and `xgen_recovery.capture`. Command flags, deadlines, resource limits and terminal/cleanup implementations remain unchanged.
- **TESTED:** The inspected read-only suite passed **68 tests**. Independently constructed harnesses passed **98 additional build/receipt cases** and **50 recovery-capture cases**. Aggregate synthetic execution stayed below two seconds of reported tool time.
- **TESTED:** Final write/flush/short-write/budget failures cannot retain zero success; tested existing nonzero results remain unchanged. Cleanup exceptions cannot restore zero. The suite also exercises close failure, which escapes the top-level receipt context and prevents successful process termination.
- **TESTED:** Actual composed build consumers reject warnings, malformed framing, incomplete/overlong/excess records, controls/non-ASCII, identity drift and ambiguous capture bounds. Tested rejected captures remain intact; both streams are consumed completely where identities permit reading.
- **TESTED:** Actual recovery capture rejects all tested nonempty output on either stream, identity failures and nonzero statuses. These are synthetic consumer results, **not authentic native producer reachability evidence**.

Reproduction, from `records/phase1-direct/factory-20261101/o1-xgen-build-package-v2`:

```bash
XGEN_READ_ONLY_TESTS=1 PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/python3 -B -W error source_tests.py
```

Public raw results:

```text
Ran 68 tests in 0.259s
OK

COMPOSED_STAGE minimal clean_pass,18_malformed_rejected_full_logs_and_both_streams,8_identity_failures_rejected
COMPOSED_STAGE core clean_pass,18_malformed_rejected_full_logs_and_both_streams,8_identity_failures_rejected
COMPOSED_STAGE helpers clean_pass,18_malformed_rejected_full_logs_and_both_streams,8_identity_failures_rejected
FINAL_RECEIPT 0 clean/write/short/flush checked; cleanup_failure_cannot_restore_zero
FINAL_RECEIPT 2 clean/write/short/flush checked; cleanup_failure_cannot_restore_zero
FINAL_RECEIPT -9 clean/write/short/flush checked; cleanup_failure_cannot_restore_zero
FINAL_RECEIPT 125 clean/write/short/flush checked; cleanup_failure_cannot_restore_zero
EXACT_LINE_BOUNDARY 4096 bytes accepted; next byte rejected by composed stage matrix
ADVERSARIAL_CASES 98 ELAPSED_SECONDS 0.178252

RECOVERY_CAPTURE create clean_pass,14_nonempty_streams_rejected_without_trim,6_identity_failures_and4_nonzero_exits_rejected
RECOVERY_CAPTURE extract clean_pass,14_nonempty_streams_rejected_without_trim,6_identity_failures_and4_nonzero_exits_rejected
RECOVERY_CASES 50 ELAPSED_SECONDS 0.026094

PACKET_POSTCHECK_MATCHED 130
NO_PACKAGE_PYCACHE True
```

The exact additional heredoc commands and outputs are preserved in my public tool calls: successful build/receipt invocation `83b78d`, recovery invocation `ca1366`, postcheck `7bc6cf`. Root should retain those complete command bodies in the public evidence capture. A preliminary reviewer harness failed because its global `os.read` mock intercepted policy loading (`KeyError 3`); that harness error and correction remain public and provide no product-failure evidence.

**UNRUN/UNPROVEN:** native output-format compatibility, warning-free builds, sandbox behavior, actual resource fit, generation determinism, native recovery and authentic cgroup/terminal behavior. Successful flush does not prove durable storage. Future W/JOB roots remain absent; no writes, operational mains, compiler/generator/archive/service/lock/network operations or peer-report inspection occurred.

The smallest sound next step is the separate fresh judge on this exact packet. Any later attempt still requires current storage-owner handoff and explicit admission, followed by complete same-source native receipts and postchecks. IPC composition remains separately blocked; D47, O1 closure and Phase One remain open; **F7 is NOT PERFORMED**.

<oai-mem-citation>
<citation_entries>
MEMORY.md:701-703|note=[Historical carrier and acceptance distinctions used for orientation and rechecked against current packet]
</citation_entries>
<rollout_ids>
01a1787b-9465-7363-96e3-47c837eec185
</rollout_ids>
</oai-mem-citation>