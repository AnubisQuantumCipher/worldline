# Step 3 source and execution map

Scope: MEASURED static correspondence at frozen product `a1bda52b53a9a220b2333fe09a135e2d94127dbc`, not a proof or execution result. Exact searches and output locations are recorded in `evidence/step3-map-commands.json`. The tests and projects below are focused existing controls, never replacements for the unchanged complete original runtime roster.

## Common proof and production boundary

Required final proof scope remains `gnatprove -P core/worldline_core.gpr -U --mode=all --level=3 --report=all --checks-as-errors=on --proof-warnings=on -j2`, with explicit solver `--memlimit` and `--timeout` and the shared resource runner. A focused `-u` analysis may diagnose a seed unit but cannot satisfy this gate or its complete imported closure. The production shared library is built by `core/worldline_core.gpr`; `worldline.gpr` and the frozen original build roster retain their separate required coverage. Do not use `tests/worldline_tests.gpr` alone as all-unit build evidence.

Both `core/worldline-c_api.adb` and `core/evaluation_completion_c.adb` directly import `Native_Diagnostic_Trace`. The complete C API shared library and checked error/diagnostic paths consequently retain the unresolved full-value lifetime issue. Pure authority kernels below can be inspected and proved without waiting for a changed diagnostic representation. Production runs can collect factual behavior while this issue remains open, but cannot be promoted to complete end-to-end retirement or Phase 1 acceptance evidence.

## Conservation and resource authority

Core specification/body seeds (both `.ads` and `.adb` for each):

- `worldline-resources`: complete quantity arithmetic, reserve conditions, state conformance.
- `resource_quantities`, `resource_ledger`, `resource_reservation_transition`: quantity relations, complete withheld ledger, `Conserved`, `Change_Conserved`, operation/final-transition relations, `Apply` entry/exit state equations.
- `resource_run_ledger`, `resource_scoped_run_ledger`: run/context/epoch ownership and conservation joins.
- Wire/ABI consumers: `worldline-resources_c_api`, `worldline-resource_ledger_c_api`, `resource_run_ledger_c_api`, `resource_scoped_run_ledger_wire`; preserve all field/layout/input validation.

Production trace to collect:

- `runtime/worldline/admission.py` imports `kernel_compute_ledger` and `kernel_compute_headroom`, calls the former at its withheld-ledger calculation and the latter at actual admission decisions.
- `runtime/worldline/resource_ledger.py:126` `compute_ledger` and `:213` `compute_headroom` marshal complete magnitudes and call the selected native library. Record exact loaded library identity, retained complete input roster, call entry, returned decision, and actual admission effect.
- `runtime/worldline/protected_resource_runtime.py` also calls `compute_ledger` during protected projection; `resource_run_ledger.py:210` binds `wl_resource_run_ledger_check_v1`; protected principal/resource service routes must be exercised using authentic retained identities.
- `resource_kernel.can_reserve` is an ABI surface; static search did not locate a production call site in this frozen Python tree. Do not use an isolated direct call as proof of the currently used production admission route.

Existing focused controls: `resource-tests/resource_tests.gpr`, `resource-ledger-correspondence-tests/resource_ledger_correspondence_tests.gpr`, `resources-prefix-correspondence-tests/resources_prefix_correspondence_tests.gpr`, `use-reservation-tests/use_reservation_tests.gpr`; Python `test_resource_kernel.py`, `test_resource_headroom.py`, `test_resource_run_ledger_v1.py`, `test_resource_scoped_history_v1.py`, and `test_admission_enforcement.py` plus original admission regressions. Each is a component gate until production entry/decision/effect evidence joins it.

`'Old` dependency: ordinary inline state snapshots in `resource_reservation_transition.Apply` are distinct from dynamically managed diagnostic sequence snapshots. Its pure conservation proof can proceed. The final linked native path still includes the diagnostic boundary.

## Lifecycle authority

Core seeds: `resource_reservation_lifecycle`, `worldline-ordinary_reservation_lifecycle`, `worldline-manager_resource_lifecycle`, `worldline-runner_lifecycle`, `worldline-runner_lifecycle_bytes`, `worldline-runner_outcome`, `worldline-runner_outcome_bytes`; evaluation lifecycle additionally includes `worldline-evaluation`, `worldline-evaluation_v2`, `evaluation_pending`, `evaluation_pending_v2`, `evaluation_completion`, `evaluation_finalization`, and `worldline-transitions`.

Production trace to collect:

- `admission.py` actual release/reconcile paths call `ordinary_reservation_lifecycle.release_plan`/`reconcile_plan` via `_reservation_policy`; `_invoke` binds `wl_ordinary_reservation_lifecycle_plan`. `reservation_lifecycle.py` delegates its ordinary route to this native protocol profile, so legacy exact-byte transport alone is insufficient.
- `linux/systemd.py:312` and related owner/capture routines call `manager_resource_lifecycle.decide`, whose `_native` binds `wl_manager_resource_lifecycle_v1`. Inputs are complete terminal/identity observations, and returned actions drive effect execution.
- `runner.py:340` `_lifecycle` and other acquisition/finalization paths call `runner_lifecycle.allowed`, which binds `wl_runner_lifecycle_allowed_v1`.
- `transaction.py:1992` asks `core.transaction_transition_allowed` before persisting a state; its Python table is a fail-closed cross-check, and disagreement must remain an error.
- Evaluation finalization enters `Finalizer`, raw/finalization kernel calls and retained journal publication. Record a normal completed path and actual interruption/refusal/failure paths without using saved labels as authoritative decisions.

Existing focused controls: `reservation-tests/tests.gpr`, `completion-tests/completion_tests.gpr`, `transition-tests/tests.gpr`; Python `test_reservation_lifecycle.py`, `test_ordinary_reservation_lifecycle_v35.py`, `test_manager_resource_lifecycle_native.py`, `test_runner_lifecycle_native_v35.py`, `test_runner_lifecycle_bytes_v35.py`, `test_evaluation_lifecycle_promotion.py`, `test_lifecycle_integrity.py`, and the original ownership/fault controls.

`'Old` dependency: pure lifecycle relation/protocol bodies are independently inspectable/provable; the full native exceptional handoff, queue drain, postcheck exception cleanup, and checked model lifetime are dependent. `Release` proving a native leaf becomes null cannot close automatic model snapshot retirement.

## Recovery authority

Core seeds: `worldline-recovery`, `worldline-recovery_protocol`, `worldline-recovery_protocol_abi`, `worldline-recovery_authorization_v3`, `worldline-recovery_authorization_v3_wire`, `worldline-recovery_authorization_v3_c_api`, `worldline-recovery_material_replay`, `worldline-recovery_owner_replay`, `worldline-recovery_packet`, `worldline-recovery_syntax`, `worldline-recovery_archive`, `worldline-transaction_relations`; include their retained-evidence and evaluation authority imports in closure.

Production trace to collect:

- `transaction.py:35` currently imports `transaction_relation.marker_state` as `kernel_recovery_action`; `_recover_one` at `:1660` calls this route, then executes the returned finish/abort action. The older `recovery_kernel.select_action` exists but is not the current production marker route found by static search.
- `transaction_relation.py:31` `_decide` binds `wl_transaction_relation_v1`; `marker_state`, recovery-root/manifests/packet and committed-frame relations use complete raw requests. Record actual `_recover_one` entry, native decision, chosen effect, durable readback, and refusal behavior.
- `recovery_authority_kernel_v3.py:104` binds `wl_recovery_authorization_decide_v3`; protected operation/canonical exchange kernels compose those full-domain recovery bindings and actual native observations. `recovery_protocol_kernel.py:11` binds `wl_recovery_protocol_decide_v1` for protocol state transitions. Direct typed calls remain separate from authentic protected input/ownership evidence.

Existing focused controls: `recovery-protocol-tests/recovery_protocol_tests.gpr`, `recovery-epoch-tests/recovery_epoch_tests.gpr`, `explicit-recovery-marker-tests/explicit_recovery_marker_tests.gpr`, `protocol-adapter-tests/protocol_adapter_tests.gpr`; Python `test_recovery_protocol_native.py`, `test_recovery_protocol_typed_adapter.py`, `test_recovery_witness_relation_v3.py`, `test_recovery_packet_producer.py`, `test_owned_recovery_history_abi.py`, `test_recovery_authority.py`, `test_transaction.py`, and `test_rollback.py`. Original power-loss/SIGKILL/storage/corruption/stale/restart/rollback/concurrency campaigns remain required; this list does not replace them.

`'Old` dependency: pure state machine, binding equality and retained-material replay proofs can proceed. A complete recovery run linked through C API can retain behavior evidence, but its diagnostic exceptional cleanup/lifetime gate and whole-source acceptance remain open.

## Evidence joins and effective evaluation

Core seeds: `evaluation_raw_roster`, `evaluation_history`, `evaluation_completion`, `evaluation_finalization`, `worldline-evaluation_authority`, `worldline-evaluation_wire`, `worldline-evaluation_producer`, `worldline-evaluation_policy`, `worldline-retained_evidence_replay`, `worldline-report_custody_native`, `worldline-native_execution_capture`, `worldline-native_execution_views`, `worldline-source_audit_native`, `worldline-source_syntax_provider`, `worldline-journal_witness`; include custody-v2 event/owner/root/subject evidence joins for protected evidence authenticity.

Production trace to collect:

- `finalize.py:161` `roster_decision` obtains each actual raw row through `evaluation_record` and invokes `core.evaluation_roster_complete` at `:192`. Missing rows and explicitly empty declared rosters remain distinct.
- `evaluation_authority.py` constructs `RawCompletionKernel` and uses `evaluation_history.select_history`; `raw_completion_kernel.py:30` binds `wl_completion_raw_decide_v1`, and `evaluation_history.py` binds `wl_evaluation_history_select`.
- `evaluation_producer.py:306` binds `wl_evaluation_producer_derive_v1` for source-derived observations. `transaction.py:1368` imports `transaction_relation.execution`, whose `_decide` uses `wl_transaction_relation_v1` and acquires current execution subjects at the original point.
- Capture the actual source/row/policy/agent/execution-subject material, selected loaded library, call request/return, retained journal/custody identity, and final promotion/refusal effect. Python booleans or source comments are not proof the decision came from proved code. Fake Core objects/mock kernels only test callers.

Existing focused controls: `roster-d2-tests/roster_d2_tests.gpr`, `evaluation-history-tests/tests.gpr`, `evaluation-authority-tests/evaluation_authority_tests.gpr`, `evaluation-wire-tests/evaluation_wire_tests.gpr`, `completion-tests/completion_tests.gpr`; Python `test_evaluation_roster_d2.py`, `test_completion_owned_abi.py`, `test_raw_evaluation_default.py`, `test_evaluation_row_projection.py`, `test_native_execution_completion_v34.py`, `test_revalidation_binding.py`, `test_finalization_journal_sequence.py`, `test_finalization_agent_binding.py`, and protected report/custody/fixture controls in the original roster.

`'Old` dependency: pure full-value joins between supplied arenas/records can proceed independently. The complete native completion API imports the diagnostic queue, and actual error diagnostics plus full checked runtime/proof closure remain dependent. Authentic protected provenance/ownership and actor execution are separate gates and cannot be supplied by this dependency map.

## Required honest runtime evidence

For each obligation, retain same-commit input and tool/library identities, exact command and working directory, actual production entry path, actual native symbol invocation and return, subsequent production effect/readback, positive and hostile controls, and original errors. A source map only demonstrates where to collect the evidence. None of these production executions was performed by the read-only mapping work.
