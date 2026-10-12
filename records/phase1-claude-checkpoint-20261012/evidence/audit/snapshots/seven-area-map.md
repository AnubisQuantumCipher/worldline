# WORLDLINE Phase One: requirement-to-code map (read-only survey by a fresh-context Explore subagent, 2026-10-12 02:50Z)

Source root: /home/sicarii/Work/worldline-phase1-claude-20261012/source (f21a688 + the observer redesign working tree).
Model-origin survey; every claim below is a pointer to be verified against the files named, not evidence by itself.

## Global facts
- Exactly one core unit is SPARK_Mode Off: Worldline.C_API (worldline-c_api.ads:6, .adb:95). No Skip_Proof, pragma Assume or
  False_Positive anywhere in core; the only annotation is Hide_Info in worldline-chain_authority.adb.
- All 163 wl_* exports are declared in Worldline.C_API; the SPARK *_C_API/*_C packages export only version/layout symbols.
- Decision-path code outside core: protected-canonical/full_physical_actuator.c (calls wl_canonical_exchange_decide_v1 then
  wl_actuator_exchange); cosmogony-use-component/src/*_c_api.ad[sb] are SPARK Off; protected-resource/run_service.py is Python.
- Exports with no runtime caller (tests/protected-canonical only): wl_custody_operation_bootstrap_decide_v2, wl_genesis_archive_matches_v1,
  wl_operation_archive_json_matches_v1, wl_scoped_archive_json_matches_v1, wl_decimal_binary64_v1, wl_native_diagnostic_control_v1;
  bound but test-only: wl_evaluation_{classify,admissible,transition_allowed,advance}, wl_collapse_decide, wl_resources_can_reserve,
  wl_reservation_lifecycle_plan, wl_recovery_select, wl_recovery_authorization_decide_v2.

## 1. Evaluation lifecycle
(a) SPARK: worldline-evaluation.ads (Execution_State; Transition_Allowed/Advance/Classify/Admissible/Roster_Complete with Post),
    worldline-evaluation_v2.ads (Admissible Post: Completed & Passed & Bundle in Not_Covered|Verified & Report ok & Evidence_Complete),
    worldline-evaluation_wire.ads, evaluation_pending(.v2).ads, evaluation_completion(.roster).ads, evaluation_raw_roster.ads
    (Classify Post = Reference; Promotion_Roster), evaluation_finalization.ads, worldline-evaluation_authority.ads, worldline-collapse.ads
    (Decide Post: Authorized = All_Hold), worldline-collapse_wire.ads; C layers in SPARK evaluation_{pending,pending_v2,completion,finalization}_c.
    No Pre/Post (Global => null only): Runner_Lifecycle(_Bytes).Allowed, Runner_Acquisition_Bytes.Closed, Runner_Outcome(_Bytes).Decide.
(b) C API: wl_evaluation_{classify,admissible,transition_allowed,advance,roster_complete}, wl_evaluation_wire_*, wl_collapse_decide,
    Authority_Glue: wl_collapse_raw_dependencies_v1, wl_collapse_decide_raw_evaluation_v1/_v2/_v3, wl_pending_decide_v1/_v2,
    wl_completion_decide_v1, wl_completion_raw_decide_v1, wl_completion_metadata_matches_v1, wl_finalization_decide_v1,
    wl_collapse_decide_finalization_v1, wl_runner_lifecycle_allowed_v1, wl_runner_outcome_decide_v1, wl_evaluation_acquisitions_closed_v1,
    Evaluation_Policy_Project_V1, Evaluation_Capture_Plan_V1, Evaluation_Producer_Derive_V1.
(c) Runtime: transaction.py (+recovery_observation.CollapseObservation.decide; prepare :375, commit _authorize :648/:791 via
    core.collapse_decide_with_evaluation; _observe_authorization :812 packet path wl_recovery_packet_decide_v1), evaluation_pending.py +
    pending_kernel_v2.py, evaluation_terminal.py + completion_kernel.py, evaluation_writer.py + raw_completion_kernel.py,
    finalization_writer.py/finalization_journal.py + finalization_kernel.py (acquisitions_closed gates generation close :81-108, :336),
    runner.py + runner_lifecycle.py (:341-1031), runner_outcome.py (runner.py:1093), finalize.roster_decision, model.py:164.
(d) Tests: test_evaluation_authority.py, test_raw_evaluation_default.py, test_evaluation_terminal.py, test_evaluation_pending*.py,
    test_pending_owned_abi.py, test_completion_owned_abi.py, test_finalization_kernel.py, test_finalization_owned_abi.py,
    test_evaluation_roster_d2.py, test_evaluation_row_projection.py, test_evaluation_lifecycle_promotion.py,
    test_runner_lifecycle_bytes_v35.py, test_runner_lifecycle_native_v35.py, test_runner_outcome_native_v35.py,
    test_agent_acquisition_ownership.py, test_evaluation_acquisition_raw_producer.py, test_private_acquisition_terminal.py, test_core_abi.py,
    test_typed_absence.py; Ada harness runner_lifecycle_controls.adb.
SPARK Off on the path: C_API.Evaluation_Admissible input checks (c_api.adb:867-925); Authority_Glue composes the authorization outside SPARK
    (Bound.Roster_Complete := (if Agent_Ready = 1 then P_Ready else 0) at c_api.adb:3354-3355, then Decide_Wire); Python adds the owner
    conjunction in recovery_observation.py:185-188 (skipped when owner is None); Python builds the roster list in finalize.roster_decision.

## 2. Resource reservations
(a) SPARK: resource_run_ledger.ads (Check Post = Decision_Reference, Ready => Conserved_Reference & Contained_Reference & epoch+1;
    Changed_Row_Allowed), resource_run_ledger_wire.ads, resource_run_ledger_c_api.ads (no Post), resource_scoped_run_ledger(.wire).ads
    (Check Ready branch quoted in the survey), worldline-resources.ads (Can_Reserve/Try_Reserve), resource_admission.ads (Admit Post =
    Decision_Conforms), resource_ledger.ads, resource_quantities.ads, resource_reservation_lifecycle.ads (Plan Post = Plan_Conforms),
    resource_reservation_transition.ads (Check/Apply never called), worldline-ordinary_reservation_lifecycle.ads (Plan: range-only Post),
    worldline-manager_resource_lifecycle.ads (Decide returns JSON String, no Post), resource_observation_classification(_wire),
    resource_actor_admission(_wire), worldline-resource_actor_execution(_wire), worldline-resource_child_execution(_wire),
    worldline-custody_v2_k4_resource_ack.ads (no Post).
(b) C API: wl_resource_run_ledger_check_v1, wl_resource_scoped_run_ledger_{check,validate,classify}_v1, wl_resource_policy_admit,
    wl_resource_ledger_compute/headroom, wl_resources_can_reserve, wl_reservation_lifecycle_plan, wl_ordinary_reservation_lifecycle_plan,
    wl_manager_resource_lifecycle_v1, wl_resource_observation_{classify,current,genesis_current}_v1, wl_resource_actor_admission_check_v1,
    Resource_Actor_Execution_Decide, Child_Decide, wl_journal_witness_decide_v1 (Resource_ACK kind).
(c) Runtime: protected-resource/run_service.py RunLedgerService.mutate -> resource_run_ledger.ResourceRunLedgerKernel.check then durable
    append; protected_resource_runtime.launch_reserved (:733) requires RESOURCE_NATIVE_RESERVATION_REQUIRED_BEFORE_LAUNCH, submit_bound
    (RECORD_LAUNCH_INTENT) then systemd-run; resource_scoped_run_ledger.ScopedRunLedgerKernel used by protected_scoped_resource_*,
    root_worker_closed*, root_worker_failed_closure, protected_root_observation, resource_actor_admission; admission.py uses resource_policy,
    resource_ledger, ordinary_reservation_lifecycle (:542-1026); manager_resource_lifecycle.py, resource_os_observation.py,
    resource_actor_execution.py, resource_child_execution.py, canonical_k4_recovery.py (journal_witness_kernel.verify_resource_ack).
    resource_kernel.py (Can_Reserve) and reservation_lifecycle._api are test-only.
(d) Tests: test_resource_run_ledger_v1.py, test_resource_scoped_history_v1.py, test_ordinary_reservation_lifecycle_v35.py,
    test_reservation_lifecycle.py, test_manager_resource_lifecycle_native.py, test_resource_kernel.py, test_resource_ledger.py,
    test_resource_headroom.py, test_resource_policy.py, test_resource_owned_abi.py, test_resource_os_observation_v1.py,
    test_resource_actor_execution_v1.py, test_resource_child_execution_v1.py; Ada manager_resource_lifecycle_controls.adb,
    resource_policy_smoke.adb; protected-resource/controls/test_full_resource_replay_v2.py.
SPARK Off on the path: C_API *_Transport marshalling; the Python launch precondition and run_service.py.

## 3. Recovery state machine
(a) SPARK: worldline-transitions.ads (Transaction_Allowed Post quoted), worldline-recovery.ads (Select_Action, Matches),
    worldline-recovery_protocol.ads (Advance Post = Reference; Changed_Only_By_Resolution), worldline-recovery_authorization(.v3).ads
    (Select_Action Post = Action_Reference; Next_State Post), worldline-recovery_packet.ads (Inspect, Complete), worldline-recovery_owner_replay.ads;
    no Post: worldline-recovery_material_replay.ads, worldline-recovery_archive.ads; worldline-custody_v2_operation_journal.ads
    (Transition_Allowed no Post; Startup/Recovery/Append/Bootstrap_Decide; Recovery_Decide Post only implies Value.Status = Parsed);
    worldline-transaction_relations.ads (Marker_State no Post; Decide range-only Post); worldline-journal_witness.ads (no Post); worldline-owner_transitions.ads.
(b) C API: wl_transition_allowed, wl_transaction_transition_allowed, wl_recovery_select, wl_recovery_protocol_decide_v1,
    wl_recovery_authorization_decide_v2/_v3, wl_recovery_packet_decide_v1, wl_recovery_packet_decide_with_facts_v1,
    wl_recovery_packet_projection_matches_v1, wl_recovery_syntax_inputs_v1, wl_transaction_relation_v1, wl_custody_operation_{startup,append,recovery,bootstrap}_decide_v2,
    wl_journal_witness_decide_v1, wl_owner_transition_authorize_v1, wl_full_physical_recover_v1 (C).
(c) Runtime: transaction.py (_set_state :1994 cross-checks wl_transaction_transition_allowed vs the Python table, CORE_DISAGREEMENT;
    _finish_committed :1452 RECOVERY_UNAUTHORIZED; _recover_one :1656 transaction_relation.marker_state), protected_recovery_capture.py
    (redecide_packet == 'AUTHORIZED' in Python, plus v3 and protocol), recovery_authority_kernel_v3.py (protected_operations.py),
    custody_operation_startup_kernel.py (protected_startup.py, protected_operations.py), journal_witness_kernel.py (canonical_owner_witness.py,
    canonical_k4_recovery.py), recovery_protocol_kernel.py (protected-lab/recovery_principal.py); recovery_kernel.py and v2 kernel have no runtime callers.
(d) Tests: test_recovery_authority.py, test_recovery_kernel.py, test_recovery_protocol_native.py, test_recovery_protocol_typed_adapter.py,
    test_recovery_witness_relation(.v3).py, test_owned_recovery_history_abi.py, test_recovery_packet_producer.py, test_recovery_observation_codec.py,
    test_transaction.py, test_custody_startup_native_v35.py, test_journal_witness_native_v35.py (needs WORLDLINE_JOURNAL_WITNESS_CORPUS),
    test_owner_transitions.py, test_lifecycle_integrity.py.
SPARK Off on the path: C_API Custody_Operation_Decide_V2 marshalling (getpid/geteuid imports); physical recover in C; Python composition of the
    historical verdict into the v3 input.

## 4. Evidence roster and completeness
(a) SPARK: evaluation_history.ads (Lifecycle Pending/Error/Rollback_Fence/Completed; Select_Evidence Post quoted; Head_Decision refusal order
    Evidence_Absent, Evidence_Superseded, Requirement_Absent/Changed, Evidence_Fenced, Evaluation_Incomplete, Evidence_Fail_Terminal),
    evaluation_raw_roster.ads (Classify, Promotion_Roster, Genuine_Required_Failure), evaluation_completion_roster.ads,
    evaluation_completion.ads (Apply Post: history retained, only the selected row changes), evaluation_finalization.ads (Seal),
    worldline-evaluation_authority.ads, worldline-owner_retry_audit.ads (Decide Post = Reference; Ready = Holds); no Post:
    worldline-evaluation_policy.ads, worldline-evaluation_producer.ads, worldline-retained_evidence_replay.ads, worldline-journal_witness.ads,
    worldline-recovery_material_replay.ads.
(b) C API: wl_evaluation_history_select, Completion_Raw_Decide, Completion_Decide, Finalization_Decide(_Mixed), wl_evaluation_policy_project_v1,
    Evaluation_Capture_Plan_V1, wl_evaluation_producer_derive_v1, wl_owner_audit_decide_v1, wl_journal_witness_decide_v1, Recovery_Packet_Decide*.
(c) Runtime: evaluation_history.select_history (evaluation_authority.py:277 read -> transaction._observe_decision; validation.py:586;
    evaluation_terminal.py:534), revalidate.py, finalize.py, evaluation_policy.py, evaluation_producer.py, owner_retry_audit.py,
    recovery_observation.py; anchor.py rollback detection is pure Python.
(d) Tests: test_evaluation_history.py, test_raw_evaluation_default.py, test_evaluation_roster_d2.py, test_evaluation_row_projection.py,
    test_evaluation_terminal.py, test_finalization_kernel.py, test_revalidation_binding.py, test_recovery_packet_producer.py,
    test_owner_retry_audit.py, test_policy_source_raw_correspondence.py, test_evaluation_policy_raw_producer.py, test_evaluator_completeness.py,
    test_anchor_witness.py, test_chain_verification.py.

## 5. Typed optional identities
(a) SPARK: worldline-identities.ads (10 Optional_* records; Same = both present and equal), worldline-collapse_wire.ads (Raw_Optional_Hash/Counter,
    Hash_Well_Formed forbids a present all-zero hash; Decode; Decide_Wire Post), worldline-recovery.ads (Optional_Marker, Matches),
    worldline-recovery_authorization(.v3).ads (Optional_Digest/Epoch), evaluation_history/completion/finalization, worldline-evaluation_authority.ads
    (Optional_Bytes), worldline-owner_transitions.ads (Optional_Identity), resource_run_ledger_wire.ads (Decode Post: Present = (Raw.Present = 1)),
    worldline-root_custody_model.ads (Same_Present_Digest: a present zero digest is NOT absence here), root_custody_row_schema/views,
    root_custody_phase_values, worldline-custody_v2_archive_chain.ads (Optional_Span).
(b) C API/headers: wl_collapse_decide, wl_abi_version, wl_layout_size, wl_layout_offset (SPARK Off), per-family layout exports, headers
    worldline_core.h (wl_optional_hash, wl_optional_counter, wl_collapse_request), evaluation_*.h, resource_*_v1.h,
    worldline_recovery_authorization_v3.h, worldline_chain_authority_v1.h, worldline_owner_audit.h.
(c) Runtime: core.py (COptionalHash/COptionalCounter; _optional_hash raises INVALID_HASH for an all-zero present digest; layout check at load
    raises CoreUnavailable on mismatch), evaluation_history.py, recovery_authority_kernel_v3.py, resource_run_ledger.py, owner_transitions.py,
    completion_kernel.py, pending_kernel_v2.py, root_worker_codec.py.
(d) Tests: test_typed_absence.py, test_abi_layout.py, test_core_abi.py, test_recovery_witness_relation_v3.py, test_evaluation_history.py,
    test_resource_run_ledger_v1.py, test_owner_transitions.py, test_raw_evaluation_default.py, test_evaluation_roster_d2.py, test_*_owned_abi.py.

## 6. Capability attenuation
(a) SPARK: worldline-operation_authority.ads (Attenuates quoted: same parent/issuer/instance/root set/policy/owner/epoch, allowed-ops subset,
    ceiling <=, issued_at >=, expires_at <=; Eligible and Reference opaque), worldline-canonical_operation.ads (Decide = opaque Reference),
    worldline-canonical_exchange.ads, worldline-canonical_owner_completion.ads, worldline-owner_transitions.ads (Authorize Post quoted),
    worldline-owner_retry_audit.ads, worldline-owner_conjunction.ads, worldline-custody_v2_owner_canonical.ads (Posts only imply
    Current_Matches/Parsed), cosmogony-capabilities.ads, cosmogony-revocable_capabilities.ads (Derive Post: Granted = Can_Derive, Attenuates),
    cosmogony-governed_capabilities.ads, worldline-startup_issuer_source.ads (Corresponds replays grants through Revocable_Capabilities.Check_Request).
    Use allowance and per-ancestor revocation/epoch/expiry live only in the body of Operation_Authority.Eligible (.adb:44-69); no contract states them.
(b) C API: wl_operation_authority_decide_v1, wl_canonical_operation_decide_v1, wl_canonical_exchange_decide_v1, wl_canonical_owner_completion_decide_v1,
    wl_owner_transition_authorize_v1, wl_owner_audit_decide_v1, Startup_Admission_Decide_V1, Startup_Owner_Admission_Decide_V1.
    No core export calls any Cosmogony Derive or Attenuates.
(c) Runtime: operation_authority_kernel.py (protected_operations.py, operation_owner_kernel.py), canonical_*_kernel.py, owner_transitions.py /
    owner_retry_audit.py (protected_owner.py, owner_collapse_data.py), startup_admission_kernel.py (protected_startup.py),
    capability_use_kernel.py + protected_capability_uses.py load libcosmogony_core.so through an external `adapter` package NOT in the tree;
    capabilities.py is a registry only.
(d) Tests: test_operation_exports_native.py, test_canonical_operation_exports_native.py, test_resource_actor_execution_v1.py,
    test_owner_transitions.py, test_owner_retry_audit.py, test_capability_native_binding_simulation.py, test_capabilities.py;
    canonical-owner-completion-tests/canonical_owner_completion_controls.adb, use-reservation-tests/use_reservation_tests.adb.
SPARK Off on the path: all cosmogony-use-component/src/cosmogony-*_c_api.ad[sb].

## 7. Receipt-chain rules
(a) SPARK: worldline-receipts.ads (Link, Append Post quoted), worldline-causal_graph.ads, worldline-chain_authority.ads (Replay Post =
    Replay_Reference; Prefix_Step/Finish_Reference), worldline-retained_custody_chain.ads (Verify Post constrains only Failing_Row),
    worldline-custody_v2_archive_chain.ads (Verify, Base_Matches), worldline-custody_v2_domain_hmac.ads (Mac, Pre only),
    worldline-ordinary_receipt_policy.ads (Decide Post = opaque Reference; Verify_History, Receipt_Predecessor_Status no Post);
    custody_v2_history/provision call Archive_Chain.Verify; custody_v2_closed_v1 calls Retained_Custody_Chain.Verify.
(b) C API: wl_receipt_link, wl_causal_link (Link only; Append not exported), wl_chain_authority_replay_v1, wl_retained_chain_verify_v1,
    wl_ordinary_receipt_policy_decide_v35, wl_ordinary_receipt_verify_history_v35, Custody_Load_Decide_V2, wl_custody_provision_decide_v2,
    Custody_Closed_Decide_V2, Genesis_Archive_Matches_V1 (test-only).
(c) Runtime: store.py (append_receipt/event append: Python SQL picks the last row as predecessor, then core.receipt_link/causal_link, then
    ordinary_receipt_policy functions; verify_chains is a Python loop over *_link, called from controller.py:594, daemon.py:510,
    protected_owner.py:589, protected_recovery_capture.py:195, relocate.py:1061; replay_native_chains has no caller),
    chain_authority.replay_chain via operation_owner_kernel.replay_owner_chain (canonical_operation_chains.py),
    retained_chain_kernel.verify_current_owner (protected_root_worker.py:37), custody_provision_kernel.py, custody_load_kernel.py,
    custody_closed_kernel.py, anchor.py (pure Python).
(d) Tests: test_chain_authority_native.py, test_chain_authority_analyzed_transport.py, test_chain_verification.py, test_anchor_witness.py,
    test_transaction.py, test_custody_provision_kernel.py, test_core_abi.py. No test_*.py exercises Ordinary_Receipt_Policy
    (ordinary_receipt_policy_v35_controls.py / _regressions.py are not imported anywhere).

## Gaps and uncertainties (survey's list, verbatim in substance)
1. The raw-evaluation authorization is assembled outside SPARK (C_API.Authority_Glue, c_api.adb:3158-3435, then the Python owner conjunction);
   the packet path composes in SPARK but Recovery_Packet.Inspect's Post is only Complete'Result = Inspect(...).State.
2. Many decision units have no functional contract (AoRTE only): Runner_Lifecycle(_Bytes), Runner_Outcome(_Bytes), Runner_Acquisition_Bytes,
   Evaluation_Policy, Evaluation_Producer, Journal_Witness, Custody_V2_K4_Resource_Ack, Retained_Evidence_Replay, Recovery_Material_Replay,
   Transaction_Relations.Marker_State, Manager_Resource_Lifecycle.Decide, Custody_V2_Operation_Journal.Transition_Allowed.
3. Some Posts only point at opaque functions: Ordinary_Receipt_Policy.Decide, Operation_Authority.Decide, Canonical_Operation.Decide (Reference
   without expression); Operation_Authority.Eligible opaque.
4. Proved kernels runtime never reaches while runtime uses weaker ones: Evaluation lifecycle v1 exports and legacy wl_collapse_decide are test-only;
   Recovery.Select_Action test-only (production uses Transaction_Relations.Marker_State, no Post); Resources.Can_Reserve and
   Resource_Reservation_Lifecycle.Plan test-only (ordinary admission uses Ordinary_Reservation_Lifecycle.Plan, range-only Post);
   Resource_Reservation_Transition.Check/Apply never called.
5. "Rollback cannot restore revoked authority" is not carried by SPARK: Rollback_Fence exists but nothing produces it; ledger rollback detection is
   pure Python (anchor.py).
6. Ordinary receipt chain runs in Python (Link plus Python predecessor selection); native Chain_Authority.Replay only for canonical operation chains;
   Retained_Custody_Chain.Verify and Archive_Chain.Verify Posts do not state link continuity.
7. Capability derivation has no runtime path and no tests: Cosmogony Derive/Attenuates unreachable from any wl_* export; runtime capability checks go
   through libcosmogony_core.so (SPARK Off C APIs) via an out-of-tree adapter; every grant fixture uses parent=None; no attenuation-refusal test;
   docs/phase1-checkpoint-2026-10-02.md lists capability attenuation and receipt/causal authority as open.
8. Two presence conventions coexist (Collapse_Wire forbids a present all-zero hash; Root_Custody_Model and Recovery_Authorization(_V3) allow it);
   ABI layout equality is checked at load and in tests, not proved (a declared boundary assumption in proof-manifest.json).
9. The tree's proof-manifest.json covers only 90 subprograms in 12 packages (stale relative to REQUIRED_PROVED 1623); evaluation_epoch.ads:13-15
   says Is_Successor "remains unproved here and there".
10. Untested custody decisions: no test_*.py calls wl_custody_operation_recovery_decide_v2 or wl_custody_operation_append_decide_v2.
11. Survey limits: environment-gated native tests not run; protected-* runtime callers not exhaustively mapped.
