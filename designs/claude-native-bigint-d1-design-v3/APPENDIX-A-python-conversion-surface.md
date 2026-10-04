# Appendix A to D1 DESIGN v3: Python decimal-integer conversion surface (OD-2 input)

Status: **DRAFT for independent actual gpt-6.1-sol review.** Nothing here was executed, reviewed or accepted.
O-PYTHON, O-PY-AUDIT and O-PY-COST stay OPEN. This appendix is part of the D1 DESIGN v3 package
(`DESIGN.md` in this directory cites its sha256).

## A.0 How this was produced (observed)

- Source tree: `C5` = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-composition-v5-beta/source`
  (the current reviewed candidate). For every listed file the v4 base is byte-identical except where DESIGN.md §3 F28
  says otherwise; none of the listed Python files differs between v4 and v5-beta.
- Method: a read-only Python `ast` scan run by the drafting agent in this session. No WORLDLINE module was imported or
  executed. The scan visited every `.py` file and every `#!...python` script under `runtime/`, `protected-resource/`,
  `protected-startup/`, `protected-runtime/`, `native/`, `scripts/`, `cli/` and `daemon/`. It also parsed every string
  constant that contains `import` and a newline as Python source, which found the inline child-interpreter source at
  `runtime/worldline/simulation.py:30`.
- A site is a call `json.loads`, `json.dumps`, `json.load` or `json.dump`; only the first two occur.
- Observed totals: **192** sites. Scope partition (observed counts; their sums are JACKAL results K-41, K-42, K-47,
  K-55, K-56, K-57 in DESIGN.md §15):

| Scope | Meaning | Sites |
|---|---|---|
| PROD-RUNTIME | `runtime/` production code (daemon, CLI, helpers, private evaluator, protected Python modules under `runtime/worldline/`) | 122 |
| INLINE-CHILD | source text executed by a `-I -S` child interpreter (`trusted_inline`) | 2 |
| PROD-PROTECTED | protected-service entry code outside `runtime/` | 10 |
| ORIGINAL-CONTROL | original control/campaign code under `*/controls/` | 25 |
| BUILD-TOOL | `native/build_guard.py` (Root native-build action) | 3 |
| INSTALL-RELEASE-SCRIPT | `scripts/` (install, release, preflight and assurance tooling) | 30 |

The v2 Appendix A listed 124 `runtime/` sites. That figure equals 122 + 2 (K-41): v2 counted the two inline-child sites
under `runtime/`. v2 omitted the 68 sites outside `runtime/` (K-47), and classified 20 sites, including the daemon
request parser, as host-bounded "PR" without a demonstrated bound. That classification is withdrawn (DESIGN.md §11,
V2-F16).

## A.1 Disposition rule under each OD-2 option

- **E0 (no decision):** every site keeps today's behaviour. A decimal integer beyond the interpreter's configured limit
  raises `ValueError` at the site. That is an OPEN failure, never an accepted refusal.
- **E1 (interpreter-wide unlimited):** a site is covered only if its interpreter belongs to a process class that
  DESIGN.md §11.3 shows is configured before the site's first relevant conversion. The `json` calls themselves do not
  change.
- **E2 (scoped codec):** every PROD-RUNTIME, PROD-PROTECTED, BUILD-TOOL and INSTALL-RELEASE-SCRIPT site either moves to
  the codec, with every existing keyword setting preserved, or carries a reviewed data-flow demonstration that its
  integers are bounded below 10**640. Such a demonstration is an audit result about where the value comes from. It is
  never a new cap. INLINE-CHILD sites need the codec text inlined into the child source, because trusted helpers may
  import the standard library only (`runtime/worldline/trusted.py:31-33`), or such a demonstration. ORIGINAL-CONTROL
  files stay byte-identical. New additive PY controls (DESIGN.md §12.5) exercise the large-integer cases instead.
- No site is excluded by module role alone. That was the defect in v2's EV/ST/PR classes.

## A.2 Complete site list

Columns: number, scope, `file:line` (under `C5`), call, enclosing function (for inline sources: the child), keyword
settings as written. Every listed setting must be preserved byte-for-byte by an E2 codec. `parse_int` is not used at
any site today.

| # | Scope | Site | Call | Enclosing | Settings |
|---|---|---|---|---|---|
| 1 | PROD-RUNTIME | `runtime/worldline/admission.py:430` | `json.loads` | `_load` | (defaults) |
| 2 | PROD-RUNTIME | `runtime/worldline/admission.py:477` | `json.dumps` | `_store` | indent=2 |
| 3 | PROD-RUNTIME | `runtime/worldline/anchor.py:343` | `json.loads` | `read_pin` | (defaults) |
| 4 | PROD-RUNTIME | `runtime/worldline/canonical.py:43` | `json.dumps` | `canonical_bytes` | ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':') |
| 5 | PROD-RUNTIME | `runtime/worldline/canonical.py:54` | `json.loads` | `parse_canonical` | (defaults); argument `data.decode("utf-8", "strict")` |
| 6 | PROD-RUNTIME | `runtime/worldline/causal.py:277` | `json.loads` | `why` | (defaults) |
| 7 | PROD-RUNTIME | `runtime/worldline/checks.py:878` | `json.loads` | `_parse` | (defaults) |
| 8 | PROD-RUNTIME | `runtime/worldline/cli_main.py:105` | `json.dumps` | `_emit` | indent=2, sort_keys=True, ensure_ascii=False |
| 9 | PROD-RUNTIME | `runtime/worldline/cli_main.py:109` | `json.dumps` | `_emit` | indent=2, sort_keys=True, ensure_ascii=False |
| 10 | PROD-RUNTIME | `runtime/worldline/cli_main.py:654` | `json.dumps` | `main` | sort_keys=True |
| 11 | PROD-RUNTIME | `runtime/worldline/client.py:61` | `json.loads` | `request` | (defaults) |
| 12 | PROD-RUNTIME | `runtime/worldline/client_peer.py:115` | `json.loads` | `__init__` | (defaults) |
| 13 | PROD-RUNTIME | `runtime/worldline/client_peer.py:137` | `json.loads` | `observation` | (defaults) |
| 14 | PROD-RUNTIME | `runtime/worldline/client_peer.py:220` | `json.loads` | `preparer_observations` | (defaults) |
| 15 | PROD-RUNTIME | `runtime/worldline/client_peer_relay.py:95` | `json.loads` | `receive_request_peer` | object_pairs_hook=unique |
| 16 | PROD-RUNTIME | `runtime/worldline/client_peer_relay.py:102` | `json.loads` | `receive_request_peer` | (defaults) |
| 17 | PROD-RUNTIME | `runtime/worldline/config.py:83` | `json.loads` | `load` | (defaults) |
| 18 | PROD-RUNTIME | `runtime/worldline/controller.py:1208` | `json.loads` | `_manifest_origin` | (defaults) |
| 19 | PROD-RUNTIME | `runtime/worldline/daemon.py:304` | `json.loads` | `_dispatch_line` | (defaults); request `id` may be any non-Boolean `int` (`:309-311`) |
| 20 | PROD-RUNTIME | `runtime/worldline/environment.py:140` | `json.loads` | `capture_workspace` | (defaults) |
| 21 | PROD-RUNTIME | `runtime/worldline/environment.py:227` | `json.loads` | `_parse_dependency_group` | (defaults) |
| 22 | PROD-RUNTIME | `runtime/worldline/evaluation_pending.py:75` | `json.dumps` | `canonical` | ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False |
| 23 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:122` | `json.loads` | `bytes_value` | (defaults) |
| 24 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:150` | `json.loads` | `decode_payload` | (defaults) |
| 25 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:568` | `json.loads` | `_observe` | (defaults) |
| 26 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:614` | `json.loads` | `observe_raw` | (defaults) |
| 27 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:657` | `json.loads` | `_captured_observation_events_locked` | (defaults) |
| 28 | PROD-RUNTIME | `runtime/worldline/evaluation_terminal.py:685` | `json.loads` | `_captured_stream_locked` | (defaults) |
| 29 | PROD-RUNTIME | `runtime/worldline/install_config.py:31` | `json.loads` | `patch_shell` | (defaults) |
| 30 | PROD-RUNTIME | `runtime/worldline/install_config.py:58` | `json.dumps` | `patch_shell` | ensure_ascii=False, indent=2 |
| 31 | PROD-RUNTIME | `runtime/worldline/project.py:106` | `json.loads` | `load` | (defaults) |
| 32 | PROD-RUNTIME | `runtime/worldline/proof.py:129` | `json.loads` | `_inspect` | (defaults) |
| 33 | PROD-RUNTIME | `runtime/worldline/proof.py:165` | `json.loads` | `_inspect` | (defaults) |
| 34 | PROD-RUNTIME | `runtime/worldline/proof_manifest.py:921` | `json.loads` | `load_manifest` | (defaults) |
| 35 | PROD-RUNTIME | `runtime/worldline/protected_owner.py:35` | `json.dumps` | `canonical` | sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False |
| 36 | PROD-RUNTIME | `runtime/worldline/protected_owner.py:43` | `json.loads` | `exact` | object_pairs_hook=pairs |
| 37 | PROD-RUNTIME | `runtime/worldline/protected_recovery_capture.py:58` | `json.loads` | `exact_json` | object_pairs_hook=pairs |
| 38 | PROD-RUNTIME | `runtime/worldline/protected_startup.py:36` | `json.dumps` | `canonical` | sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False |
| 39 | PROD-RUNTIME | `runtime/worldline/protected_startup.py:47` | `json.loads` | `exact_json` | object_pairs_hook=pairs, parse_constant=(refusing lambda) |
| 40 | PROD-RUNTIME | `runtime/worldline/relocate.py:454` | `json.loads` | `_plan_transaction_records` | (defaults) |
| 41 | PROD-RUNTIME | `runtime/worldline/relocate.py:1124` | `json.loads` | `main` | (defaults) |
| 42 | PROD-RUNTIME | `runtime/worldline/relocate.py:1134` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 43 | PROD-RUNTIME | `runtime/worldline/relocate.py:1140` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 44 | PROD-RUNTIME | `runtime/worldline/relocate.py:1142` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 45 | PROD-RUNTIME | `runtime/worldline/report.py:74` | `json.dumps` | `prepare_private_report` | sort_keys=True, separators=(',', ':') |
| 46 | PROD-RUNTIME | `runtime/worldline/report.py:118` | `json.loads` | `collect_private_report` | (defaults) |
| 47 | PROD-RUNTIME | `runtime/worldline/report.py:193` | `json.loads` | `_collect_private_report_observed` | (defaults) |
| 48 | PROD-RUNTIME | `runtime/worldline/returning.py:182` | `json.loads` | `_receipt_with_before_root` | (defaults) |
| 49 | PROD-RUNTIME | `runtime/worldline/runner.py:844` | `json.loads` | `read_stdout` | (defaults) |
| 50 | INLINE-CHILD | `runtime/worldline/simulation.py:30` (inline source, line 8) | `json.loads` | child `-I -S` interpreter | (defaults) |
| 51 | INLINE-CHILD | `runtime/worldline/simulation.py:30` (inline source, line 24) | `json.dumps` | child `-I -S` interpreter | sort_keys=True, separators=(',', ':') |
| 52 | PROD-RUNTIME | `runtime/worldline/simulation.py:238` | `json.loads` | `run` | (defaults) |
| 53 | PROD-RUNTIME | `runtime/worldline/store.py:211` | `json.loads` | `_json_load` | (defaults) |
| 54 | PROD-RUNTIME | `runtime/worldline/store.py:887` | `json.loads` | `causal_events_for_world` | (defaults) |
| 55 | PROD-RUNTIME | `runtime/worldline/store.py:1005` | `json.loads` | `receipt_for_transaction` | (defaults) |
| 56 | PROD-RUNTIME | `runtime/worldline/store.py:1010` | `json.loads` | `receipt_for_candidate` | (defaults) |
| 57 | PROD-RUNTIME | `runtime/worldline/store.py:1063` | `json.loads` | `verify_chains` | (defaults) |
| 58 | PROD-RUNTIME | `runtime/worldline/store.py:1085` | `json.loads` | `verify_chains` | (defaults) |
| 59 | PROD-RUNTIME | `runtime/worldline/store.py:1174` | `json.loads` | `last_receipt` | (defaults) |
| 60 | PROD-RUNTIME | `runtime/worldline/transaction.py:552` | `json.loads` | `listing` | (defaults) |
| 61 | PROD-RUNTIME | `runtime/worldline/transaction.py:791` | `json.loads` | `_authorize` | (defaults) |
| 62 | PROD-RUNTIME | `runtime/worldline/transaction.py:810` | `json.loads` | `_observe_authorization` | (defaults) |
| 63 | PROD-RUNTIME | `runtime/worldline/transaction.py:1918` | `json.loads` | `_marker` | (defaults) |
| 64 | PROD-RUNTIME | `runtime/worldline/transaction.py:1933` | `json.loads` | `_load_record` | (defaults) |
| 65 | PROD-RUNTIME | `runtime/worldline/agents/pi.py:52` | `json.loads` | `_declares_provider` | (defaults) |
| 66 | PROD-RUNTIME | `runtime/worldline/linux/criu.py:72` | `json.loads` | `restore` | (defaults) |
| 67 | PROD-RUNTIME | `runtime/worldline/linux/docker.py:86` | `json.loads` | `capture` | (defaults) |
| 68 | PROD-RUNTIME | `runtime/worldline/linux/examiner_loader.py:285` | `json.loads` | `decode_policy` | object_pairs_hook=_unique, parse_constant=_nonfinite |
| 69 | PROD-RUNTIME | `runtime/worldline/linux/hyprland.py:36` | `json.loads` | `query` | (defaults) |
| 70 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:445` | `json.loads` | `_retain` | (defaults) |
| 71 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:445` | `json.dumps` | `_retain` | (defaults) |
| 72 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:580` | `json.loads` | `_namespace_anchor` | object_pairs_hook=unique |
| 73 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:911` | `json.dumps` | `_mount_handle` | (defaults) |
| 74 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1061` | `json.dumps` | `_acknowledgement` | (defaults) |
| 75 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1117` | `json.loads` | `_native_json` | object_pairs_hook=unique, parse_constant=invalid, parse_float=finite |
| 76 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1121` | `json.dumps` | `_native_reply` | sort_keys=True, separators=(',', ':'), allow_nan=False |
| 77 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1370` | `json.loads` | `_entry_preparation` | object_pairs_hook=unique_fields, parse_constant=invalid_constant, parse_float=finite_float |
| 78 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1395` | `json.loads` | `_entry_preparation` | object_pairs_hook=unique_fields, parse_constant=invalid_constant, parse_float=finite_float |
| 79 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1455` | `json.dumps` | `_entry_preparation` | (defaults) |
| 80 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1503` | `json.loads` | `_observe` | object_pairs_hook=unique_fields |
| 81 | PROD-RUNTIME | `runtime/worldline/linux/kernel_role_observer.py:1535` | `json.loads` | `_observe` | (defaults) |
| 82 | PROD-RUNTIME | `runtime/worldline/linux/namespace_lifetime.py:176` | `json.dumps` | `send_packet` | sort_keys=True |
| 83 | PROD-RUNTIME | `runtime/worldline/linux/namespace_lifetime.py:204` | `json.loads` | `receive_packet` | object_pairs_hook=unique |
| 84 | PROD-RUNTIME | `runtime/worldline/linux/namespace_lifetime.py:565` | `json.dumps` | `_seed` | sort_keys=True |
| 85 | PROD-RUNTIME | `runtime/worldline/linux/namespace_lifetime.py:606` | `json.dumps` | `_quota_reader` | sort_keys=True |
| 86 | PROD-RUNTIME | `runtime/worldline/linux/namespace_lifetime.py:707` | `json.dumps` | `_descriptor_reader` | sort_keys=True |
| 87 | PROD-RUNTIME | `runtime/worldline/linux/native_lifetime.py:676` | `json.dumps` | `receive` | sort_keys=True, separators=(',', ':') |
| 88 | PROD-RUNTIME | `runtime/worldline/linux/native_lifetime.py:711` | `json.dumps` | `receive` | sort_keys=True, separators=(',', ':') |
| 89 | PROD-RUNTIME | `runtime/worldline/linux/private_case_copy.py:260` | `json.dumps` | `copy_case_tree` | sort_keys=True, separators=(',', ':') |
| 90 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:445` | `json.loads` | `_send_entry_preparation` | (defaults) |
| 91 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:445` | `json.dumps` | `_send_entry_preparation` | allow_nan=False |
| 92 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:454` | `json.dumps` | `_send_entry_preparation` | allow_nan=False, separators=(',', ':') |
| 93 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:462` | `json.dumps` | `_send_entry_preparation` | (defaults) |
| 94 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:491` | `json.loads` | `_send_entry_preparation` | object_pairs_hook=_unique_role_fields |
| 95 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:578` | `json.dumps` | `_send` | sort_keys=True, separators=(',', ':'), allow_nan=False |
| 96 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:601` | `json.loads` | `_receive` | object_pairs_hook=_unique_role_fields |
| 97 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:671` | `json.dumps` | `retain_read` | sort_keys=True, separators=(',', ':'), allow_nan=False |
| 98 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:797` | `json.loads` | `compile_entry` | object_pairs_hook=_unique_role_fields |
| 99 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:993` | `json.dumps` | `copy_frozen_tree` | sort_keys=True, ensure_ascii=True |
| 100 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1224` | `json.loads` | `_native_artifact` | object_pairs_hook=_unique_role_fields |
| 101 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1368` | `json.dumps` | `_loader_policy` | sort_keys=True, separators=(',', ':'), allow_nan=False |
| 102 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1535` | `json.dumps` | `_launch_and_collect` | (defaults) |
| 103 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1596` | `json.loads` | `_collect_launched` | (defaults) |
| 104 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1666` | `json.loads` | `_collect_observed` | (defaults) |
| 105 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1782` | `json.dumps` | `_sandbox` | (defaults) |
| 106 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1866` | `json.loads` | `_run_role` | (defaults) |
| 107 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1939` | `json.loads` | `_read_message` | (defaults) |
| 108 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:1977` | `json.loads` | `_bootstrap` | (defaults) |
| 109 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2026` | `json.dumps` | `_bootstrap` | (defaults) |
| 110 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2297` | `json.dumps` | `worker_broker` | (defaults) |
| 111 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2304` | `json.dumps` | `worker_broker` | (defaults) |
| 112 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2308` | `json.dumps` | `worker_broker` | (defaults) |
| 113 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2503` | `json.dumps` | `broker` | (defaults) |
| 114 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2507` | `json.dumps` | `broker` | (defaults) |
| 115 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2540` | `json.dumps` | `broker` | (defaults) |
| 116 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2544` | `json.dumps` | `broker` | (defaults) |
| 117 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2609` | `json.dumps` | `_bootstrap` | indent=2 |
| 118 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2616` | `json.dumps` | `_candidate_request` | (defaults) |
| 119 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2681` | `json.dumps` | `_role` | (defaults) |
| 120 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2692` | `json.loads` | `_role` | object_pairs_hook=_unique_role_fields |
| 121 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2714` | `json.dumps` | `_role` | (defaults) |
| 122 | PROD-RUNTIME | `runtime/worldline/linux/private_evaluator.py:2759` | `json.loads` | `<module>` (`__main__` role entry) | (defaults) |
| 123 | PROD-RUNTIME | `runtime/worldline/linux/systemd.py:265` | `json.loads` | `launch_private_evaluator` | (defaults) |
| 124 | PROD-RUNTIME | `runtime/worldline/linux/systemd.py:593` | `json.loads` | `journal_events` | (defaults) |
| 125 | PROD-PROTECTED | `protected-resource/gate_bridge.py:16` | `json.loads` | `detached` | (defaults) |
| 126 | PROD-PROTECTED | `protected-resource/gate_bridge.py:31` | `json.loads` | `gate_bytes` | (defaults) |
| 127 | PROD-PROTECTED | `protected-resource/gate_bridge.py:156` | `json.loads` | `_rpc` | (defaults) |
| 128 | PROD-PROTECTED | `protected-resource/gate_bridge.py:270` | `json.loads` | `submit_from_existing_gate` | (defaults) |
| 129 | PROD-PROTECTED | `protected-resource/gate_bridge.py:290` | `json.loads` | `main` | (defaults) |
| 130 | PROD-PROTECTED | `protected-resource/run_service.py:23` | `json.dumps` | `canonical` | sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False |
| 131 | PROD-PROTECTED | `protected-resource/run_service.py:51` | `json.loads` | `parse_canonical` | (defaults) |
| 132 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:32` | `json.dumps` | `canonical` | sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False |
| 133 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:39` | `json.loads` | `parse` | object_pairs_hook=pairs, parse_constant=(refusing lambda) |
| 134 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:108` | `json.loads` | `checked_descriptor` | (defaults) |
| 135 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:134` | `json.dumps` | `execute_case` | (defaults) |
| 136 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:176` | `json.dumps` | `main` | (defaults) |
| 137 | ORIGINAL-CONTROL | `protected-resource/controls/run_campaign.py:180` | `json.dumps` | `<module>` | (defaults) |
| 138 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:17` | `json.loads` | `fixture` | (defaults) |
| 139 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:51` | `json.dumps` | `test_exact_committed_duplicate_and_recover_return_original_result_without_append` | sort_keys=True |
| 140 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:56` | `json.dumps` | (same test) | sort_keys=True |
| 141 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:66` | `json.dumps` | `test_committed_lost_ack_after_restart_reconciles_once` | sort_keys=True |
| 142 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:68` | `json.dumps` | (same test) | sort_keys=True |
| 143 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:73` | `json.loads` | `test_same_id_changed_complete_packet_or_owner_refuses_without_mutation` | (defaults) |
| 144 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:73` | `json.dumps` | (same test) | (defaults) |
| 145 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:105` | `json.dumps` | `test_legacy_result_import_preserves_complete_original_row` | sort_keys=True |
| 146 | ORIGINAL-CONTROL | `protected-resource/controls/test_full_resource_replay_v2.py:108` | `json.dumps` | (same test) | sort_keys=True |
| 147 | PROD-PROTECTED | `protected-startup/launcher.py:26` | `json.loads` | `main` | (defaults) |
| 148 | PROD-PROTECTED | `protected-startup/launcher.py:41` | `json.dumps` | `main` | sort_keys=True |
| 149 | PROD-PROTECTED | `protected-startup/owner_provision_bootstrap.py:24` | `json.loads` | `provision` | (defaults) |
| 150 | ORIGINAL-CONTROL | `protected-startup/controls/additional_startup_controls.py:13` | `json.loads` | `fixture` | (defaults) |
| 151 | ORIGINAL-CONTROL | `protected-startup/controls/run_campaign.py:41` | `json.dumps` | `canonical` | sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False |
| 152 | ORIGINAL-CONTROL | `protected-startup/controls/run_campaign.py:47` | `json.loads` | `parse` | object_pairs_hook=pairs, parse_constant=(refusing lambda) |
| 153 | ORIGINAL-CONTROL | `protected-startup/controls/run_campaign.py:157` | `json.dumps` | `execute_case` | sort_keys=True |
| 154 | ORIGINAL-CONTROL | `protected-startup/controls/run_campaign.py:191` | `json.dumps` | `main` | sort_keys=True |
| 155 | ORIGINAL-CONTROL | `protected-startup/controls/run_campaign.py:195` | `json.dumps` | `<module>` | (defaults) |
| 156 | ORIGINAL-CONTROL | `protected-startup/controls/test_protected_startup_v1.py:28` | `json.loads` | `test_missing_prior_lock_does_not_regenerate` | (defaults) |
| 157 | ORIGINAL-CONTROL | `protected-startup/controls/test_protected_startup_v1.py:36` | `json.loads` | `test_legacy_endpoint_refuses_without_removing_it` | (defaults) |
| 158 | ORIGINAL-CONTROL | `protected-runtime/controls/loader_probe.py:51` | `json.loads` | `main` | (defaults) |
| 159 | ORIGINAL-CONTROL | `protected-runtime/controls/loader_probe.py:58` | `json.dumps` | `main` | sort_keys=True |
| 160 | BUILD-TOOL | `native/build_guard.py:33` | `json.dumps` | `main` | (defaults) |
| 161 | BUILD-TOOL | `native/build_guard.py:50` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 162 | BUILD-TOOL | `native/build_guard.py:51` | `json.dumps` | `main` | (defaults) |
| 163 | INSTALL-RELEASE-SCRIPT | `scripts/assurance.py:140` | `json.loads` | `proof_facts` | (defaults) |
| 164 | INSTALL-RELEASE-SCRIPT | `scripts/assurance.py:371` | `json.dumps` | `run` | indent=2, sort_keys=True |
| 165 | INSTALL-RELEASE-SCRIPT | `scripts/backup_manifest.py:53` | `json.dumps` | `main` | indent=2 |
| 166 | INSTALL-RELEASE-SCRIPT | `scripts/engine_codes.py:350` | `json.dumps` | `main` | indent=2 |
| 167 | INSTALL-RELEASE-SCRIPT | `scripts/evaluation_domain_gate.py:47` | `json.loads` | `run` | (defaults) |
| 168 | INSTALL-RELEASE-SCRIPT | `scripts/plugin_compat.py:53` | `json.loads` | `named_commit` | (defaults) |
| 169 | INSTALL-RELEASE-SCRIPT | `scripts/plugin_compat.py:85` | `json.loads` | `main` | (defaults) |
| 170 | INSTALL-RELEASE-SCRIPT | `scripts/plugin_compat.py:89` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 171 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:125` | `json.loads` | `prepared_transactions` | (defaults) |
| 172 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:177` | `json.dumps` | `main` | indent=2 |
| 173 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:206` | `json.loads` | `main` | (defaults) |
| 174 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:274` | `json.loads` | `main` | (defaults) |
| 175 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:350` | `json.loads` | `main` | (defaults) |
| 176 | INSTALL-RELEASE-SCRIPT | `scripts/preflight.py:391` | `json.dumps` | `main` | indent=2 |
| 177 | INSTALL-RELEASE-SCRIPT | `scripts/prune_backups.py:62` | `json.dumps` | `main` | indent=2 |
| 178 | INSTALL-RELEASE-SCRIPT | `scripts/prune_backups.py:92` | `json.dumps` | `main` | indent=2 |
| 179 | INSTALL-RELEASE-SCRIPT | `scripts/release_gate.py:234` | `json.loads` | `main` | (defaults) |
| 180 | INSTALL-RELEASE-SCRIPT | `scripts/release_gate.py:242` | `json.loads` | `main` | (defaults) |
| 181 | INSTALL-RELEASE-SCRIPT | `scripts/release_gate.py:244` | `json.loads` | `main` | (defaults) |
| 182 | INSTALL-RELEASE-SCRIPT | `scripts/release_gate.py:265` | `json.dumps` | `main` | indent=2, sort_keys=True |
| 183 | INSTALL-RELEASE-SCRIPT | `scripts/release_gate.py:266` | `json.dumps` | `main` | indent=2 |
| 184 | INSTALL-RELEASE-SCRIPT | `scripts/release_notes.py:41` | `json.loads` | `main` | (defaults) |
| 185 | INSTALL-RELEASE-SCRIPT | `scripts/release_notes.py:42` | `json.loads` | `main` | (defaults) |
| 186 | INSTALL-RELEASE-SCRIPT | `scripts/verify_install.py:88` | `json.loads` | `main` | (defaults) |
| 187 | INSTALL-RELEASE-SCRIPT | `scripts/verify_install.py:143` | `json.loads` | `main` | (defaults) |
| 188 | INSTALL-RELEASE-SCRIPT | `scripts/verify_install.py:205` | `json.dumps` | `main` | indent=2 |
| 189 | INSTALL-RELEASE-SCRIPT | `scripts/verify_release_pair_report.py:36` | `json.dumps` | `problems` | sort_keys=True, separators=(',', ':'), ensure_ascii=True |
| 190 | INSTALL-RELEASE-SCRIPT | `scripts/verify_release_pair_report.py:66` | `json.loads` | `main` | (defaults) |
| 191 | INSTALL-RELEASE-SCRIPT | `scripts/verify_release_pair_report.py:66` | `json.loads` | `main` | (defaults; second call on the same line) |
| 192 | INSTALL-RELEASE-SCRIPT | `scripts/verify_release_pair_report.py:70` | `json.dumps` | `main` | sort_keys=True |

Distinct `json.dumps` setting combinations that an E2 encoder must reproduce, read from the table above:

- (defaults)
- `indent=2`
- `indent=2, sort_keys=True`
- `indent=2, sort_keys=True, ensure_ascii=False`
- `ensure_ascii=False, indent=2`
- `sort_keys=True`
- `sort_keys=True, separators=(',', ':')`
- `sort_keys=True, separators=(',', ':'), allow_nan=False`
- `sort_keys=True, separators=(',', ':'), ensure_ascii=True`
- `sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False`
- `sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False`, and the same setting set in another
  keyword order
- `ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False`
- `sort_keys=True, ensure_ascii=True`
- `allow_nan=False`
- `allow_nan=False, separators=(',', ':')`

The distinct `json.loads` keyword sets are: (defaults); `object_pairs_hook` alone; `object_pairs_hook` with
`parse_constant`; and `object_pairs_hook` with `parse_constant` and `parse_float`. An E2 parser must add `parse_int`
without disturbing any of them.

## A.3 Non-JSON decimal-conversion candidate universe (observed AST counts; classification OPEN)

These counts come from the same read-only scan, inline sources included. Each counted node is a **candidate**, because
most operands are not integers. A count is not a finding that a conversion can see a workload-derived integer. Under E2,
O-PY-AUDIT must classify every candidate by data flow (DESIGN.md §11.4.4). Under E1, the per-process configuration
covers them.

| Directory | `int(x)` base 10, non-literal `x` | `str(x)`, non-literal | `repr(x)` | `format(x)` | f-string fields | `%` format |
|---|---|---|---|---|---|---|
| `runtime/` (121 Python files) | 167 in 41 files | 582 in 73 files | 22 in 8 files | 0 | 1017 in 61 files | 1 in 1 file |
| `protected-resource/` (4) | 0 | 15 in 3 files | 0 | 0 | 0 | 0 |
| `protected-startup/` (5) | 0 | 28 in 4 files | 0 | 0 | 0 | 0 |
| `protected-runtime/` (2) | 0 | 2 in 1 file | 0 | 1 in 1 file | 0 | 0 |
| `native/` (1) | 0 | 4 in 1 file | 0 | 0 | 0 | 0 |
| `scripts/` (14) | 2 in 1 file | 56 in 10 files | 0 | 0 | 231 in 12 files | 0 |
| `cli/` (2 scripts) | 0 | 2 in 2 files | 0 | 0 | 0 | 0 |
| `daemon/` (1 script) | 0 | 1 in 1 file | 0 | 0 | 0 | 0 |

The scan did not count these further categories. O-PY-AUDIT must enumerate them:

- lazy `logging` formatting with `%d`/`%s` arguments (for example `daemon.py:339`);
- `str.format` with a non-literal receiver;
- `int.__format__` inside other formatting paths;
- any `decimal` or `fractions` use;
- third-party serializers.

Conversions in power-of-two bases (`hex`, `oct`, `bin`, `int(s, 16)`), and `int.to_bytes` / `int.from_bytes`, are
outside Python's limit (DESIGN.md §3 F4, F25).

_End of Appendix A._
