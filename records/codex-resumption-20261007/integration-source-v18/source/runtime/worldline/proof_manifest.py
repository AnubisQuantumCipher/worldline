"""The proof-manifest checks, shared by the proof gate and the runtime (1.9.2, OB-084/OB-085).

verify_proof_manifest.py (the build and install gate) and proof.ProofStatus (what a receipt's
`invariantPreservation` says) both import this module, so the gate and the runtime cannot
disagree about what a manifest must show. It imports nothing that loads the kernel.

Pinned here: the check floor, the subprograms whose proof is a claim of this release, the one
unit left unanalyzed on purpose, and the contracts the claim depends on (CONTRACT_PINS).
Changing any of them is a deliberate edit of this file; derive pin values with
`python3 verify_proof_manifest.py --print-contract-pins`, never by hand.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

# Accepted minimum for this proof scope. Keep or raise it; restore proof coverage
# when analysis falls below it. A candidate cannot lower its own acceptance bar.
MINIMUM_CHECKS = 251
# Subprograms whose proof is a claim of this release. 1.9.2 adds the chain links and appends the
# receipt and causal chains are built from, so dropping them from the proof refuses (OB-085).
REQUIRED_PROVED = [
    "Worldline.Collapse.Decide",
    "Worldline.Collapse_Wire.Decide_Wire",
    "Worldline.Collapse_Wire.Decode",
    "Worldline.Evaluation.Admissible",
    "Worldline.Evaluation.Advance",
    "Worldline.Evaluation.Classify",
    "Worldline.Evaluation.Roster_Complete",
    "Worldline.Evaluation.Transition_Allowed",
    "Worldline.Transitions.Advance",
    "Worldline.Transitions.Transaction_Allowed",
    "Worldline.Receipts.Append",
    "Worldline.Receipts.Link",
    "Worldline.Causal_Graph.Append",
    "Worldline.Causal_Graph.Link",
    'Worldline.Evaluation_V2.Transition_Allowed',
    'Worldline.Evaluation_V2.Advance',
    'Worldline.Evaluation_V2.Classify',
    'Worldline.Evaluation_V2.Admissible',
    'Worldline.Evaluation_V2.Report_Integrity_Of',
    'Worldline.Evaluation_V2.Confined_Report_Integrity_Of',
    'Worldline.Evaluation_V2.Roster_Complete',
    'Worldline.Evaluation_Wire.Decode',
    'Worldline.Evaluation_Wire.Classify_Wire',
    'Worldline.Evaluation_Wire.Admit_Wire',
    'Worldline.Evaluation_Wire.Confined_Admit_Wire',
    'Worldline.Evaluation_Wire.Roster_Wire',
    'Evaluation_Raw_Roster.Selected',
    'Evaluation_Raw_Roster.Failure_For_Check',
    'Evaluation_Raw_Roster.Classify',
    'Evaluation_Raw_Roster.Any_Completed_Failure',
    'Worldline.Evaluation_Authority.Report_Of',
    'Worldline.Evaluation_Authority.Dependencies',
    'Worldline.Evaluation_Authority.Needs_Primary',
    'Worldline.Evaluation_Authority.Needs_Staged',
    'Worldline.Evaluation_Authority.Needs_Agent',
    'Worldline.Evaluation_Authority.Structural_Result',
    'Worldline.Evaluation_Authority.Structural_Terminal',
    'Worldline.Evaluation_Authority.Structural_Optional',
    'Worldline.Evaluation_Authority.Structural_Results',
    'Worldline.Evaluation_Authority.Carried_Results_Equal',
    'Worldline.Evaluation_Authority.Carried_Replay_Equal',
    'Worldline.Evaluation_Authority.Envelope_Reference',
    'Worldline.Evaluation_Authority.Decide_Envelope',
    'Worldline.Evaluation_Authority.Equal_Optional',
    'Worldline.Evaluation_Authority.Context_Valid',
    'Worldline.Evaluation_Authority.Context_Equal',
    'Worldline.Evaluation_Authority.Effective_Row',
    'Worldline.Evaluation_Authority.Across',
    'Worldline.Evaluation_Authority.Epoch_Across',
    'Worldline.Evaluation_Authority.Binding_Across',
    'Worldline.Evaluation_Authority.Cursor_Across',
    'Worldline.Evaluation_Authority.Required_Equal',
    'Worldline.Evaluation_Authority.Rows_Join',
    'Worldline.Evaluation_Authority.Without_Carried_Rosters',
    'Worldline.Evaluation_Authority.Context_Reference',
    'Worldline.Evaluation_Authority.Join_Context',
    'Worldline.Evaluation_Authority.Row_Metadata_Reference',
    'Worldline.Evaluation_Authority.Metadata_Reference',
    'Worldline.Evaluation_Authority.Join_Metadata',
    'Evaluation_Finalization.Plan_Valid',
    'Evaluation_Finalization.Same_Plan',
    'Evaluation_Finalization.Requirements',
    'Evaluation_Finalization.Start_Valid',
    'Evaluation_Finalization.Same_Start',
    'Evaluation_Finalization.Input_Valid',
    'Evaluation_Finalization.Same_Input',
    'Evaluation_Finalization.Start_Reference',
    'Evaluation_Finalization.Record_Start',
    'Evaluation_Finalization.Input_Reference',
    'Evaluation_Finalization.Record_Input',
    'Evaluation_Finalization.Row_Valid',
    'Evaluation_Finalization.Capture_Valid',
    'Evaluation_Finalization.Input_Unchanged',
    'Evaluation_Finalization.Bound_To',
    'Evaluation_Finalization.Bind_Row',
    'Evaluation_Finalization.Bind_Rows',
    'Evaluation_Finalization.Capture_Reference',
    'Evaluation_Finalization.Classify_Capture',
    'Evaluation_Finalization.Final_Identity',
    'Evaluation_Finalization.Content_Reference',
    'Evaluation_Finalization.Content_Matches',
    'Evaluation_Finalization.Artifacts_Valid',
    'Evaluation_Finalization.History_Projection',
    'Evaluation_Finalization.Seal_Reference',
    'Evaluation_Finalization.Seal',
    'Evaluation_Finalization.Payload_Spans',
    'Evaluation_Finalization.Artifact_Binding',
    'Canonical_Artifacts.Part',
    'Canonical_Artifacts.Prefix',
    'Canonical_Artifacts.Canonical',
    'Canonical_Artifacts.Field',
    'Canonical_Artifacts.String_Is',
    'Canonical_Artifacts.Root_Matches',
    'Canonical_Artifacts.Tagged_Matches',
    'Canonical_Artifacts.Array_Payloads_Match',
    'Canonical_Artifacts.Artifact_Hash',
    'Canonical_Artifacts.Bindings',
    'Canonical_Artifacts.Byte_At',
    'Canonical_Artifacts.Match',
    'Canonical_Artifacts.Hex',
    'Canonical_Artifacts.Character_At',
    'Canonical_Artifacts.String_Node',
    'Canonical_Artifacts.Key_Less',
    'Canonical_Artifacts.B64_Digit',
    'Canonical_Artifacts.Base64',
    'Canonical_Artifacts.Binary_At',
    'Canonical_Artifacts.String_Binary_Matches',
    'Canonical_Artifacts.Element',
    'Canonical_Artifacts.Elements',
    'Canonical_Artifacts.Integer_Matches',
    'Canonical_Artifacts.Artifact_Hash.Feed',
    'Worldline.Recovery_Authorization.Same',
    'Worldline.Recovery_Authorization.Classify_Native',
    'Worldline.Recovery_Authorization.Select_Action',
    'Worldline.Recovery_Authorization.Next_State',
    'Worldline.Recovery_Authorization_Wire.Well_Formed',
    'Worldline.Recovery_Authorization_Wire.Decode',
    'Worldline.Recovery_Authorization_Wire.Selected_Action',
    'Worldline.Recovery_Authorization_Wire.Decide',
    'Resource_Quantities.Span_Valid',
    'Resource_Quantities.Digit',
    'Resource_Quantities.Power_Reference',
    'Resource_Quantities.Prefix_Reference',
    'Resource_Quantities.Radix_Power',
    'Resource_Quantities.Prefix_Value',
    'Resource_Quantities.Magnitude',
    'Resource_Quantities.Value',
    'Resource_Quantities.Is_Zero',
    'Resource_Quantities.Is_Negative',
    'Resource_Quantities.Compare',
    'Resource_Quantities.Capacity_Fits',
    'Resource_Quantities.Scale_Column',
    'Resource_Quantities.Column_Bounds',
    'Resource_Quantities.Higher_Column_Order',
    'Resource_Quantities.Radix_Power_Worker',
    'Resource_Quantities.Prefix_Value_Worker',
    'Resource_Quantities.Prefix_Bounds',
    'Resource_Quantities.Prefix_Monotone',
    'Resource_Quantities.Prefix_Padding',
    'Resource_Quantities.Borrow_Column_Facts',
    'Resource_Admission.Outcome',
    'Resource_Admission.At_Gate',
    'Resource_Admission.At_Disk',
    'Resource_Admission.Numeric_Rejection',
    'Resource_Admission.Binary_Reference',
    'Resource_Admission.Concurrency_Reference',
    'Resource_Admission.Pressure_Reference',
    'Resource_Admission.Disk_Bytes_Reference',
    'Resource_Admission.Disk_Inodes_Reference',
    'Resource_Admission.Capacity_Reference',
    'Resource_Admission.Decision_Conforms',
    'Resource_Admission.Check_Binary',
    'Resource_Admission.Check_Capacity',
    'Resource_Admission.Admit',
    'Resource_Ledger.Rows_Valid',
    'Resource_Ledger.Slot_Valid',
    'Resource_Ledger.Disjoint',
    'Resource_Ledger.Layout_Valid',
    'Resource_Ledger.Contains',
    'Resource_Ledger.Canonical_In_Slot',
    'Resource_Ledger.Arena_Frame_Zero',
    'Resource_Ledger.Output_Representation',
    'Resource_Ledger.Withheld_Reference',
    'Resource_Ledger.Row_Reference',
    'Resource_Ledger.Total_Reference',
    'Resource_Ledger.Prefix_Total',
    'Resource_Ledger.Storage_Sufficient',
    'Resource_Ledger.Result_Conforms',
    'Resource_Ledger.Compute',
    'Resource_Ledger.Headroom_Input_Valid',
    'Resource_Ledger.Headroom_Reference',
    'Resource_Ledger.Headroom_Storage_Sufficient',
    'Resource_Ledger.Headroom_Conforms',
    'Resource_Ledger.Compute_Headroom',
    'Resource_Ledger.Whole',
    'Resource_Ledger.Column_Product',
    'Resource_Ledger.Column_Bounds',
    'Resource_Ledger.Power_Factor',
    'Resource_Ledger.Power_Monotone',
    'Resource_Ledger.Prefix_Quotient',
    'Resource_Ledger.Remainder_Witness',
    'Resource_Ledger.Advance_Column',
    'Resource_Ledger.Combined_Remainder',
    'Resource_Ledger.Equal_Prefix',
    'Resource_Ledger.Padded_Prefix',
    'Resource_Ledger.Bounded_Prefix',
    'Resource_Ledger.Magnitude_Remainder',
    'Resource_Ledger.Zero_Extension',
    'Resource_Ledger.Output_Prefix_Value',
    'Resource_Ledger.Trimmed_Value',
    'Resource_Ledger.Lift_Slice',
    'Resource_Ledger.Prefix_Total_Worker',
    'Resource_Ledger.Magnitude_Order',
    'Resource_Ledger.Canonicalize',
    'Resource_Ledger.Binary_Reference',
    'Resource_Ledger.Binary_Signs',
    'Resource_Ledger.Binary',
    'Resource_Ledger.Compute_Row',
    'Resource_Ledger.Processed_Conforms',
    'Resource_Reservation_Lifecycle.Span_Valid',
    'Resource_Reservation_Lifecycle.Same_Identity',
    'Resource_Reservation_Lifecycle.Inputs_Valid',
    'Resource_Reservation_Lifecycle.Remove_Row',
    'Resource_Reservation_Lifecycle.Any_Removal',
    'Resource_Reservation_Lifecycle.Plan_Conforms',
    'Resource_Reservation_Lifecycle.Plan',
    'Resource_Reservation_Transition.Identity_Valid',
    'Resource_Reservation_Transition.Present_Identity_Valid',
    'Resource_Reservation_Transition.Same_Identity',
    'Resource_Reservation_Transition.Context_Valid',
    'Resource_Reservation_Transition.Same_Context',
    'Resource_Reservation_Transition.Binding_Valid',
    'Resource_Reservation_Transition.Same_Binding',
    'Resource_Reservation_Transition.Nonnegative_Valid',
    'Resource_Reservation_Transition.Epoch_Valid',
    'Resource_Reservation_Transition.State_Shape',
    'Resource_Reservation_Transition.Magnitude_Sum_Equals',
    'Resource_Reservation_Transition.Signed_Sum_Equals',
    'Resource_Reservation_Transition.Is_Successor',
    'Resource_Reservation_Transition.Counted_Amount',
    'Resource_Reservation_Transition.Conserved_Reference',
    'Resource_Reservation_Transition.Conserved',
    'Resource_Reservation_Transition.Same_Reservation_Reference',
    'Resource_Reservation_Transition.Same_Reservation',
    'Resource_Reservation_Transition.Proposed_Row_Reference',
    'Resource_Reservation_Transition.Proposed_Row',
    'Resource_Reservation_Transition.Change_Reference',
    'Resource_Reservation_Transition.Change_Conserved',
    'Resource_Reservation_Transition.Request_Shape',
    'Resource_Reservation_Transition.Decision_Reference',
    'Resource_Reservation_Transition.Check',
    'Resource_Reservation_Transition.Apply',
    'Resource_Reservation_Transition.Prefix_Step',
    'Resource_Reservation_Transition.Prefix_Padding',
    'Resource_Reservation_Transition.Power_Factor',
    'Resource_Reservation_Transition.Prefix_Tail',
    'Resource_Reservation_Transition.Prefix_Decomposition',
    'Resource_Reservation_Transition.Magnitude_Columns',
    'Resource_Reservation_Transition.Column_Quotient',
    'Resource_Reservation_Transition.Unique_Column',
    'Resource_Reservation_Transition.Addition_Step',
    'Resource_Reservation_Transition.Radix_Product_Regroup',
    'Resource_Reservation_Transition.Positive_Factor_Cancellation',
    'Resource_Reservation_Transition.Addition_Mismatch',
    'Resource_Reservation_Transition.Addition_Finish',
    'Resource_Reservation_Transition.Zero_Prefix',
    'Resource_Reservation_Transition.Nonnegative_Magnitude',
    'Worldline.Resources.Digit_At',
    'Worldline.Resources.Radix_Power',
    'Worldline.Resources.Prefix_Value',
    'Worldline.Resources.Magnitude',
    'Worldline.Resources.Fits_Mathematically',
    'Worldline.Resources.Subtract_Column',
    'Worldline.Resources.Fits_By_Addition',
    'Worldline.Resources.Can_Reserve',
    'Worldline.Resources.Sum_Equals',
    'Worldline.Resources.Reserve_Mathematically_Conforms',
    'Worldline.Resources.Reserve_Conforms',
    'Worldline.Resources.Try_Reserve',
    'Worldline.Resources.Power_Quotient',
    'Worldline.Resources.Prefix_Quotient',
    'Worldline.Resources.Positive_Multiple',
    'Worldline.Resources.Remainder_From_Witness',
    'Worldline.Resources.Power_Order',
    'Worldline.Resources.Complete_Prefix',
    'Worldline.Resources.Prefix_Growth',
    'Worldline.Resources.Low_Prefix_Exact',
    'Worldline.Resources.Prefix_Modulus',
    'Worldline.Resources.Value_Modulus',
    'Worldline.Resources.Matching_Prefix',
    'Worldline.Resources.Prefix_Step',
    'Worldline.Resources.Extended_Digit_Bound',
    'Worldline.Resources.Compare_Extensions',
    'Worldline.Resources.Addition_Column',
    'Worldline.Resources.Subtraction_Column',
    'Worldline.Resources.Sum_Modulus',
    'Worldline.Resources.Mismatching_Sum_Column',
    'Worldline.Resource_Wire.Can_Reserve',
    'Worldline.Recovery.Matches',
    'Worldline.Recovery.Select_Action',
]
# The one unit not analyzed on purpose: the C ABI entry points (SPARK_Mode => Off) -- pointer
# dereference, exception handlers, file and byte hashing marshalling, and the decoding and
# validation of evaluation observations, classifications and presence records. From 1.9.0 the
# collapse request is not here: Worldline.Collapse_Wire decodes and validates it, and is proved.
# Full-domain V3 adds coverage; the original required sequence stays a literal prefix.
REQUIRED_PROVED += ['Worldline.Recovery_Authorization_V3.Same_Epoch_Reference', 'Worldline.Recovery_Authorization_V3.Same_Binding_Reference', 'Worldline.Recovery_Authorization_V3.Same', 'Worldline.Recovery_Authorization_V3.Classify_Native', 'Worldline.Recovery_Authorization_V3.Action_Reference', 'Worldline.Recovery_Authorization_V3.Select_Action', 'Worldline.Recovery_Authorization_V3.Next_State', 'Worldline.Recovery_Authorization_V3_Wire.Well_Formed', 'Worldline.Recovery_Authorization_V3_Wire.Decode', 'Worldline.Recovery_Authorization_V3_Wire.Selected_Action', 'Worldline.Recovery_Authorization_V3_Wire.Decide']

REQUIRED_PROVED += ['Worldline.Recovery_Authorization_V3_Wire.Encode_Original', 'Worldline.Recovery_Authorization_V3_Wire.Equal_Prefix', 'Worldline.Recovery_Authorization_V3_Wire.Zero_Padding', 'Worldline.Recovery_Authorization_V3_Wire.Positive_Prefix']

UNANALYZED_BOUNDARY = {"worldline-c_api"}


# The contracts this release claims, pinned by digest (1.9.0; review of a23c265). The check
# floor cannot see a postcondition clause deleted -- GNATprove counts a whole Post as one check --
# and the C boundary is exempt from the SPARK_Mode screen, so neither the count nor the coverage
# parse notices a weakened Decide or a policy shortcut in Collapse_Decide. Each pin covers a
# specification's text with comments and layout removed, or the whole unproved C boundary body
# (a pin on Collapse_Decide's text alone could be sidestepped by a declaration elsewhere in the
# file that its unqualified names resolve to; review of 19d0297).
# 1.9.2 (OB-085): the receipt and causal chains, the world identity and the ancestry claim are
# pinned too. Receipts.Link and Causal_Graph.Link carry no postcondition (Global => null only),
# so the value they return is set by their BODIES, which are pinned as well.
CONTRACT_PINS = {
    'core/canonical_artifacts.ads': '303ac80cabec2e2ef34029f6f8bd27c4100592cc9b8791b79f9a7475b9a0fa11',
    'core/canonical_artifacts.adb': 'da52dd9ed5856088f2fc3fd6cdf04065f8236456c4f7ec9593e7aff4b21fb80c',
    'artifact-tests/canonical_artifact_tests.gpr': 'bce2824cc8181edb5f1e9d5b9c0a391d70d68302b9f717ae44f87a0cd4a1ea05',
    'artifact-tests/test_canonical_artifacts.adb': '43137b6f14b3c71b87de8f09c957e95d29a7d44dab5c67fc92698be12c50b8f1',
    'core/evaluation_finalization.ads': '3b8a3d418361e255cd7cff14d4acc9e17ab9684dba66ea398fd83ef579ce20b2',
    'core/evaluation_finalization.adb': 'f17fdd15b13842c466a1e118f1accf02de4c08f50b529bbc60a117cd621bde92',
    'core/evaluation_finalization_c.ads': '6ca339c64f2399ab819c1a5d1d3195d365a4cd19a330cbf7ad42bdd112cc2fc0',
    'core/evaluation_finalization_c.adb': '6d045dff8ad7c03250c7c36e20680465f883a2b08938e8bc7cc2d6bda0902f1a',
    'core/evaluation_completion.ads': '6eba1ac186ea36ffc07a1bb5320288b151cbc0a6435fce0d1255aa4c75418c3b',
    'core/evaluation_completion.adb': '1dc167205298b20bebddd0a5f7cec246827a7406b797681189bf73f29818a700',
    'core/evaluation_completion_roster.ads': '5af5ec8259073ad74444b5a4596b2a4b05e568c7d26739b9210e9b4616a2a2a3',
    'core/evaluation_completion_roster.adb': 'f52e2b9d4a909b3c2b616e92aaf7b87ce4ddb8a6e8b34ea99068915dc9bb253a',
    'core/evaluation_pending_v2.ads': '1e20de75c125ff20b5ad5750466430e959fb104b27f905403e38a35eb01f8321',
    'core/evaluation_pending_v2.adb': 'd8864beff6356c688f3ed26c84d27e6d0e315c423e150ee257e45df71bad3a66',
    'evaluation-authority-tests/test_evaluation_authority.adb': '071e0f859f92ac1576f95dc1c6e6f89df84c59edb304b36c3e15f0a887e98730',
    'evaluation-authority-tests/evaluation_authority_tests.gpr': 'f9ba8e8e3b9593454c25f74a5678599ebdf09afbf8510b119ebfa6f8820a98f4',
    'core/worldline-evaluation_authority.ads': '1ee7d183c40c6b98b7f98277f96924e3135fedd83900134a3ff4461bcf237694',
    'core/worldline-evaluation_authority.adb': 'd907b1d4eda41e7f7167695520085071686c834f8c1adb6691307661c3043d3a',
    'core/evaluation_completion_c.ads': '7b46d8a2b7af881a2f25e5d8637362140c493096f7970145021a42a2c27ff408',
    'core/evaluation_completion_c.adb': '6e2409ec629f107ddd50dc54d89e1686383df1dd7b4d26a23039d8d3a9905a94',
    'core/resource_ledger.ads': 'ddf46ac440a9c372f7c4b30d1d91463061a45be05653fee181f25164bdd2f0f1',
    'core/resource_ledger.adb': '01994b6554254e009a7b1a8b9ca3e7df2fc1b488829176db65db6e2cb7c8418c',
    'core/resource_reservation_transition.adb': '3af393cccae017478ec583bd32f4f8d543add470253d9e367a6e21f86cdfbcc4',
    'core/resource_quantities.ads': '21640498940fc92941624d97a6645bf14a3e1fa9bf3bc951c6f85e93d0d5f412',
    'core/resource_quantities.adb': 'a527cfdeae1671b27a901e6adc7f80fc89966980acc80f2775d77b540a63ec47',
    'pending-component/core/resource_quantities.ads': '21640498940fc92941624d97a6645bf14a3e1fa9bf3bc951c6f85e93d0d5f412',
    'pending-component/core/resource_quantities.adb': 'a527cfdeae1671b27a901e6adc7f80fc89966980acc80f2775d77b540a63ec47',
    'core/evaluation_history.ads': 'e58eea740afa7f385a386ad97ad78380eb61ccac35d7669f14768dd4ac30cc3a',
    'core/evaluation_history.adb': 'e714beb4979f89706e3d7636fbfcfe23d1a99b319b53635b06dc3fdf6248209f',
    'core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5',
    'core/evaluation_epoch.adb': '1958820a7247823c06a3295ab6fbd86bd1bff3ccd7cf6d7c71d94425e11d0259',
    'pending-component/core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5',
    'pending-component/core/evaluation_epoch.adb': '1958820a7247823c06a3295ab6fbd86bd1bff3ccd7cf6d7c71d94425e11d0259',
    'core/worldline-resources.ads': '3abbfe401429b72094c8e06be392ff3cb7612149f125d1249f4b8bf5792c978e',
    'core/worldline-resources.adb': '0e65d26b226f8de7c665ff0effde568057f5fd135f7dafad85f110a697ea8e17',
    'core/worldline-evaluation_v2.ads': '8e1f18244b924a7c9c05c67fdf785491a910c9f7c59966381b38962c2f68a72c',
    'core/worldline-evaluation_v2.adb': '2fc57758a66ac2c7aa9ef6e108fdcbf93b1b286fd64b6620d8bca54ce32312eb',
    'core/worldline-evaluation_wire.ads': '8b190a32f057a30a700e3331bd72aa2cfc18c5d6f3540b824756197f09077c7a',
    'core/worldline-evaluation_wire.adb': '30696c9e2b4be84aad47d406864213a176f494e07dbed6f6907efe601d3be530',
    'core/evaluation_raw_roster.ads': '6bdb761e4be7a6dec36373293ffb7de064ddaa250a811ce9ebb6dcf2db69788b',
    'core/evaluation_raw_roster.adb': 'f2808bdf8a8403cde066aee07565eb0c494e4081a04783c9dbdc1ec5c37abe6f',
    'core/worldline-evaluation_report_facts.ads': 'f8bfee03303776b2825662bb1ce394fdf3c3e6acf3e7b1084500e50eba430f82',
    'core/worldline-evaluation_report_facts.adb': 'ffdc1629f8eaef1ec4ab1bbc4fc988f2f1546dd8b5013ec4635888d77f8240fb',
    'core/worldline-evaluation_report_wire.ads': 'a58347985c4242421c4114ecf61ddaf6f84229e62ab2114cd0947b7feee29b19',
    'core/worldline-evaluation_report_wire.adb': '19ed101a83a9a9350a660cd7693a8be7ffee86557fa6d58e7959a0ae9973ff78',
    'evaluation-wire-tests/evaluation_wire_tests.gpr': '8fde6733c882c9be99a7fbcdce0c6ba0a8eca138a4b68e65ec77efdc84160d89',
    # The project files decide which file is compiled as each unit; a pin on a source's text
    # binds nothing if they may redirect it (review of ab1d4bb).
    "worldline.gpr": "edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021",
    "core/worldline_core.gpr": "0a69d56380704b0e2859c8f24a31f638b983558382844b10621f3afdcc0a8469",
    "core/worldline_core_sources.gpr": "fc7be69ee1d21269d12f600a3dab22b53c21362d178280d5f8ddcacf5c09802c",
    "core/attest_sha256.gpr": "5d75d10379e9397a9e08517d56728b2f53479fd7c0e9dff3b5dccaa8e8c0f9ee",
    "tests/worldline_tests.gpr": "d452b39691f23078635cb829b0ef94040342cefec9288cd4cccb821a51ca6a82",
    "core/worldline.ads": "4e08ff1dedc1f28b526a19b37c343b2d71f5f1e35409abda2afdbd92a73ab866",
    "core/attest/attest.ads": "bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587",
    "core/attest/attest-sha256.ads": "1d38534d6bcaa9a6646225db8f26f0a7b940444cda3ed0d109816119d51bff05",
    "core/worldline-c_api.ads": "fa1a0d10bfd2d8a33426b7ce9c31b37fb58a48988d620ea574d8677a93c1340a",
    "core/worldline-collapse.ads": "94ef49a258a46363eea81d44e168ce4e7cc618fdf128e916e92e447f2ffe32e2",
    "core/worldline-collapse_wire.ads": "48270be156ee3f1c7d7f6215917c9b8026ac5346c45064cf7803950c137ddd76",
    "core/worldline-identities.ads": "ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21",
    "core/worldline-evaluation.ads": "06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e",
    "core/worldline-transitions.ads": "5b9c8f89900d01eeb40818de6392e1f23f8e2606cba702dd06e72e4257406c27",
    "core/worldline-c_api.adb": "0f5249db1edef5cd40acfed0a5ce63d6fb8c223951137ebf4efc9e0faab4bde2",
    "core/worldline-receipts.ads": "45e8c276cf73d8d0311f247a1c87e9bf88614d46fde2bfe6c5f858ee2d20827b",
    "core/worldline-receipts.adb": "1ee34566208a835951d21d79be1bc6ffd287b3c61b43bad76210a7a546b156bb",
    "core/worldline-causal_graph.ads": "1f5271eed9dc2bdacf2642a9647bab7a2b29a707c7749664ba09f7fac79ce14f",
    "core/worldline-causal_graph.adb": "a7e80ad0b061be82ce2727e5aeabd6fa27335807d66445ad01dc3fb3931dfab5",
    "core/worldline-world.ads": "3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5",
    "core/worldline-ancestry.ads": "718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db",
    'core/resource_admission.adb': '0da682e7cd0aa85daea88a9f36926fa213240b9273cd7015108f95f4f48ee63c',
    'core/resource_admission.ads': '2d93c087e980ec50ce77a21efdeb4c2d3a96e503493e55c0a9cbbb27e80381f2',
    'core/resource_reservation_lifecycle.adb': '3cf6bbe8dfef85f485be16eb9185768ace28ddc6a3ea5bfe0cd0aa26dd8aef41',
    'core/resource_reservation_lifecycle.ads': '8e3c85334abc8ff747e6f468bea29f04196c3c11cffa10a68207b96c8b3e0400',
    'core/resource_reservation_transition.ads': '668286cd1a05a5820ac0b75c3c3d7f7f25ddb005b78d05960f6aa1d9320f8f78',
    'core/worldline-recovery.adb': '75763d6eb35c647df523a728c6939e21cda6c3d7b44ba54fb2a4a917f3149e24',
    'core/worldline-recovery.ads': '735d3411bd85c84f7e9f0449c34808f9c9ae226d82aac5e396448b4d27f4668a',
    'core/worldline-recovery_authorization.adb': 'd90b75ec516fbf8ddb0f0bf40ee39297e70eebc001d4edad6b0142c7da092e7d',
    'core/worldline-recovery_authorization.ads': '3b95bc25da8343b9d0c4cd6e133614bb59cdce65740142d9c2d2ed072e62dec6',
    'core/worldline-recovery_authorization_c_api.adb': '0f3e1162efebf4b9d15197c5e224c4ebec3bd4f63a476b49a5a584c466c0e471',
    'core/worldline-recovery_authorization_c_api.ads': 'afc10c9f738f0bba486ade982b7250327b31972f64c5a33b319f1662d2ff059e',
    'core/worldline-recovery_authorization_wire.adb': 'e0c1054dd20e34bf1ddbcaefd9665c7588fc4683c8dad1a91351c89597928f62',
    'core/worldline-recovery_authorization_wire.ads': 'a6b453f40b2eee2d860008ecb11b9720f6be2a5be5c1aca52a91f264c40d687c',
    'core/worldline-resource_wire.adb': 'ec1ea00cf321f841aafcb874047c48d1ff28363d29ea042c6703a60a2be32f80',
    'core/worldline-resource_wire.ads': 'b0af3ef936e727ba9113430ebc29c2843124f82e584b3bb294dc23af2667ad75',
}


# Source-selected V3 composition; no prior manifest is evidence for this candidate.
CONTRACT_PINS.update({'core/worldline-recovery_authorization_v3.adb': '21536d8595e0d6d14764b56309eb2f88d28bd88fc47b6fe9c16f915c98ed63dd', 'core/worldline-recovery_authorization_v3.ads': '8b3f3c7477c461dadceba33ab421cf54d4c77129e2875768346d93c91f3fdd51', 'core/worldline-recovery_authorization_v3_c_api.adb': 'fa1d4aa2b0e138656314651f52312113dbdaa6bd3f491714115c234e8f2e5d39', 'core/worldline-recovery_authorization_v3_c_api.ads': '96b679271cea641ab5bcf84784fa08193d56b19b456a67d3d08007268d8ed2b5', 'core/worldline-recovery_authorization_v3_wire.adb': '5df8bd9bcd6842aaf033bde67edd121e6d9e0bdfd6f29158f0f8b1a57fd36bc6', 'core/worldline-recovery_authorization_v3_wire.ads': '30a49ffee1fecf33fe798e524cda06f73a8a2164ffe92c2bce8a10155a45f90e', 'core/worldline_core.gpr': '0a69d56380704b0e2859c8f24a31f638b983558382844b10621f3afdcc0a8469', 'recovery-epoch-tests/recovery_epoch_tests.gpr': '600c9e1b3b3524f1419f2419a0e0925641a9dec1c822fb0b5ddb1e2afc9bc880', 'recovery-epoch-tests/test_epochs.adb': 'b134c380bb6990c55df7c21c590627585c57a8f0bbb99453a4d4c61913a68670'})

def normalized_ada(text: str) -> str:
    """Ada source with `--` comments removed (outside string literals) and all layout
    collapsed to single spaces, so a pin changes only when the code does."""
    lines = []
    for line in text.splitlines():
        in_string = False
        cut = len(line)
        for index, char in enumerate(line):
            if char == '"':
                in_string = not in_string
            elif not in_string and line.startswith("--", index):
                cut = index
                break
        lines.append(line[:cut])
    return " ".join(" ".join(lines).split())


def contract_text(root: Path, key: str) -> str:
    relative, _, subprogram = key.partition("#")
    text = normalized_ada((root / relative).read_text(encoding="utf-8"))
    if not subprogram:
        return text
    start = text.find(f"function {subprogram} ")
    end = text.find(f"end {subprogram};", start)
    if start < 0 or end < 0 or text.find(f"function {subprogram} ", start + 1) >= 0:
        raise ValueError(f"cannot isolate {key}")
    return text[start:end + len(f"end {subprogram};")]


def contract_pin(root: Path, key: str) -> str:
    return hashlib.sha256(contract_text(root, key).encode("utf-8")).hexdigest()


def export_problems(root: Path) -> list[str]:
    """The C symbol the runtime calls for the collapse decision must be bound exactly once, to
    Collapse_Decide, whose body is pinned (review of 0ee1112: moving the binding to another
    function left every pin intact)."""
    text = normalized_ada((root / "core/worldline-c_api.ads").read_text(encoding="utf-8"))
    bindings = text.count('External_Name => "wl_collapse_decide"')
    declared = ('function Collapse_Decide (Request : C_Collapse_Request_Access) return Interfaces.Unsigned_8 '
                'with Export, Convention => C, External_Name => "wl_collapse_decide";')
    problems = []
    if bindings != 1:
        problems.append(f"wl_collapse_decide is bound {bindings} times")
    if declared not in text:
        problems.append("wl_collapse_decide is not bound to Collapse_Decide")
    raw_declared = ('function Decide_Raw (Request, Primary, Primary_Raw, Primary_Confinement, '
        'Staged, Staged_Raw, Staged_Confinement, Agent : System.Address; '
        'Agent_Confinement : Byte) return Byte with Export, Convention => C, '
        'External_Name => "wl_collapse_decide_raw_evaluation_v1";')
    if text.count('External_Name => "wl_collapse_decide_raw_evaluation_v1"') != 1 or raw_declared not in text:
        problems.append('raw collapse authority binding differs')
    context_declared = ('function Decide_Raw_Context (Request, Primary, Primary_Raw, Primary_Confinement, Primary_Context, '
        'Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address; '
        'Agent_Confinement : Byte) return Byte with Export, Convention => C, '
        'External_Name => "wl_collapse_decide_raw_evaluation_v2";')
    if text.count('External_Name => "wl_collapse_decide_raw_evaluation_v2"') != 1 or context_declared not in text:
        problems.append('full-context raw collapse authority binding differs')
    dependency_declared = ('function Dependencies (Request : System.Address) return Byte '
        'with Export, Convention => C, External_Name => "wl_collapse_raw_dependencies_v1";')
    if text.count('External_Name => "wl_collapse_raw_dependencies_v1"') != 1 or dependency_declared not in text:
        problems.append('raw collapse dependency binding differs')
    metadata_declared = ('function Decide_Raw_Metadata (Request, Primary, Primary_Raw, Primary_Confinement, Primary_Context, '
        'Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address; '
        'Agent_Confinement : Byte) return Byte with Export, Convention => C, '
        'External_Name => "wl_collapse_decide_raw_evaluation_v3";')
    if text.count('External_Name => "wl_collapse_decide_raw_evaluation_v3"') != 1 or metadata_declared not in text:
        problems.append('full-row metadata raw collapse authority binding differs')
    finalization = normalized_ada((root / 'core/evaluation_finalization_c.ads').read_text(encoding='utf-8'))
    final_entry = ('function Decide (Input, Output : System.Address) return Interfaces.C.int '
        'with Export, Convention => C, External_Name => "wl_finalization_decide_v1";')
    mixed_entry = ('function Decide_Mixed (Collapse : System.Address; Primary_Kind : U32; '
        'Primary, Primary_Raw, Primary_Confinement, Primary_Context : System.Address; '
        'Staged_Kind : U32; Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address; '
        'Agent_Confinement : U8) return U8 with Export, Convention => C, '
        'External_Name => "wl_collapse_decide_finalization_v1";')
    if finalization.count('External_Name => "wl_finalization_decide_v1"') != 1 or final_entry not in finalization:
        problems.append('finalization Start/Input/Seal native entry differs')
    if finalization.count('External_Name => "wl_collapse_decide_finalization_v1"') != 1 or mixed_entry not in finalization:
        problems.append('finalization mixed collapse native entry differs')
    v3 = normalized_ada((root / 'core/worldline-recovery_authorization_v3_c_api.ads').read_text(encoding='utf-8'))
    for symbol in ('wl_recovery_authorization_version_v3', 'wl_recovery_authorization_layout_v3',
                   'wl_recovery_authorization_decide_v3'):
        if v3.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'full-domain recovery export binding differs: {symbol}')
    return problems


# Fixed source inventory of the reviewed Phase 1 core. Adding or removing a unit requires
# an explicit reviewed change here; discovering a file must never grant it permission.
# Membership is not proof: every existing contract pin, source digest, expected-unit,
# per-subprogram coverage and proof-floor check remains independently required.
DECLARED_CORE_ADA_SOURCES = frozenset({
    'core/canonical_artifacts.ads',
    'core/canonical_artifacts.adb',
    'core/evaluation_finalization.ads',
    'core/evaluation_finalization.adb',
    'core/evaluation_finalization_c.ads',
    'core/evaluation_finalization_c.adb',
    'core/worldline-evaluation_authority.adb',
    'core/worldline-evaluation_authority.ads',
    'core/worldline-evaluation_v2.ads',
    'core/worldline-evaluation_v2.adb',
    'core/worldline-evaluation_wire.ads',
    'core/worldline-evaluation_wire.adb',
    'core/evaluation_raw_roster.ads',
    'core/evaluation_raw_roster.adb',
    'core/attest/attest-sha256.adb',
    'core/attest/attest-sha256.ads',
    'core/attest/attest.ads',
    'core/evaluation_completion.adb',
    'core/evaluation_completion.ads',
    'core/evaluation_completion_c.adb',
    'core/evaluation_completion_c.ads',
    'core/evaluation_completion_roster.adb',
    'core/evaluation_completion_roster.ads',
    'core/evaluation_epoch.adb',
    'core/evaluation_epoch.ads',
    'core/evaluation_history.adb',
    'core/evaluation_history.ads',
    'core/evaluation_pending.adb',
    'core/evaluation_pending.ads',
    'core/evaluation_pending_c.adb',
    'core/evaluation_pending_c.ads',
    'core/evaluation_pending_v2.adb',
    'core/evaluation_pending_v2.ads',
    'core/evaluation_pending_v2_c.adb',
    'core/evaluation_pending_v2_c.ads',
    'core/resource_admission.adb',
    'core/resource_admission.ads',
    'core/resource_ledger.adb',
    'core/resource_ledger.ads',
    'core/resource_quantities.adb',
    'core/resource_quantities.ads',
    'core/resource_reservation_lifecycle.adb',
    'core/resource_reservation_lifecycle.ads',
    'core/resource_reservation_transition.adb',
    'core/resource_reservation_transition.ads',
    'core/spark-big_integers.ads',
    'core/spark.ads',
    'core/worldline-ancestry.adb',
    'core/worldline-ancestry.ads',
    'core/worldline-c_api.adb',
    'core/worldline-c_api.ads',
    'core/worldline-causal_graph.adb',
    'core/worldline-causal_graph.ads',
    'core/worldline-collapse.adb',
    'core/worldline-collapse.ads',
    'core/worldline-collapse_wire.adb',
    'core/worldline-collapse_wire.ads',
    'core/worldline-evaluation.adb',
    'core/worldline-evaluation.ads',
    'core/worldline-evaluation_history_c_api.adb',
    'core/worldline-evaluation_history_c_api.ads',
    'core/worldline-evaluation_report_facts.adb',
    'core/worldline-evaluation_report_facts.ads',
    'core/worldline-evaluation_report_wire.adb',
    'core/worldline-evaluation_report_wire.ads',
    'core/worldline-identities.ads',
    'core/worldline-receipts.adb',
    'core/worldline-receipts.ads',
    'core/worldline-recovery.adb',
    'core/worldline-recovery.ads',
    'core/worldline-recovery_c_api.adb',
    'core/worldline-recovery_c_api.ads',
    'core/worldline-reservation_lifecycle_c_api.adb',
    'core/worldline-reservation_lifecycle_c_api.ads',
    'core/worldline-resource_ledger_c_api.adb',
    'core/worldline-resource_ledger_c_api.ads',
    'core/worldline-resource_policy_c_api.adb',
    'core/worldline-resource_policy_c_api.ads',
    'core/worldline-resource_wire.adb',
    'core/worldline-resource_wire.ads',
    'core/worldline-resources.adb',
    'core/worldline-resources.ads',
    'core/worldline-resources_c_api.adb',
    'core/worldline-resources_c_api.ads',
    'core/worldline-transitions.adb',
    'core/worldline-transitions.ads',
    'core/worldline-world.adb',
    'core/worldline-world.ads',
    'core/worldline.ads',
    'core/worldline-recovery_authorization.adb',
    'core/worldline-recovery_authorization.ads',
    'core/worldline-recovery_authorization_c_api.adb',
    'core/worldline-recovery_authorization_c_api.ads',
    'core/worldline-recovery_authorization_wire.adb',
    'core/worldline-recovery_authorization_wire.ads',
})


def stray_sources(root: Path) -> list[str]:
    """Ada files under core/ that are absent from the fixed reviewed inventory."""
    found = {path.relative_to(root).as_posix() for path in (root / "core").rglob("*.ad[bs]")}
    return sorted(found - DECLARED_CORE_ADA_SOURCES)


def missing_sources(root: Path) -> list[str]:
    """Required core units cannot disappear when a fresh manifest is generated."""
    return sorted(path for path in DECLARED_CORE_ADA_SOURCES if not (root / path).is_file())


def contract_problems(root: Path) -> list[str]:
    try:
        problems = export_problems(root)
    except OSError as exc:
        return [f"pinned contract unreadable: core/worldline-c_api.ads: {exc}"]
    problems += [f"an Ada source outside the pinned set could be compiled into the core: {path}" for path in stray_sources(root)]
    problems += [f"a required reviewed Ada source is missing: {path}" for path in missing_sources(root)]
    for key, pinned in CONTRACT_PINS.items():
        try:
            actual = contract_pin(root, key)
        except (OSError, ValueError) as exc:
            problems.append(f"pinned contract unreadable: {key}: {exc}")
            continue
        if actual != pinned:
            problems.append(f"pinned contract changed: {key} (a deliberate change updates CONTRACT_PINS)")
    return problems


DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/worldline-recovery_authorization_v3.ads', 'core/worldline-recovery_authorization_v3.adb', 'core/worldline-recovery_authorization_v3_wire.ads', 'core/worldline-recovery_authorization_v3_wire.adb', 'core/worldline-recovery_authorization_v3_c_api.ads', 'core/worldline-recovery_authorization_v3_c_api.adb'])

def expected_units(root: Path) -> set[str]:
    """Every SPARK unit the proof must cover: one per core specification, plus Attest."""
    units = {path.stem for path in (root / "core").glob("*.ads")}
    units |= {path.stem for path in (root / "core" / "attest").glob("*.ads")}
    return units


def source_paths(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {
        "worldline.gpr": root / "worldline.gpr",
        "attest/attest.ads": root / "core/attest/attest.ads",
        "attest/attest-sha256.ads": root / "core/attest/attest-sha256.ads",
        "attest/attest-sha256.adb": root / "core/attest/attest-sha256.adb",
    }
    for pattern in ("*.ads", "*.adb", "*.gpr", "*.h"):
        for path in sorted((root / "core").glob(pattern)):
            result[f"core/{path.name}"] = path
    return result


def proof_source_files(root: Path) -> list[str]:
    """Every file the proof sources, the contract pins and the coverage expectation read, as
    paths relative to the tree: what an install copies beside the library (OB-084)."""
    files = {path.relative_to(root).as_posix() for path in source_paths(root).values()}
    files |= {key.partition("#")[0] for key in CONTRACT_PINS}
    return sorted(files)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ----- the GNATprove summary, parsed as a whole and fail-closed (1.9.2, OB-085) ------------------

class SummaryError(ValueError):
    """A summary line or structure this parser does not recognize. Never skipped."""


_CATEGORIES = ("Data Dependencies", "Flow Dependencies", "Initialization", "Non-Aliasing", "Run-time Checks",
               "Assertions", "Functional Contracts", "LSP Verification", "Termination", "Concurrency")
_COLUMNS = ("total", "flow", "provers", "justified", "unproved")
_COL = r"\.|\d+(?: \([^()]*\))?"
_ROW = re.compile(rf"^(?P<label>[A-Za-z][A-Za-z -]*?)\s+(?P<total>{_COL})\s+(?P<flow>{_COL})\s+"
                  rf"(?P<provers>{_COL})\s+(?P<justified>{_COL})\s+(?P<unproved>{_COL})\s*$")
_HEADER = re.compile(r"^SPARK Analysis results\s+Total\s+Flow\s+Provers\s+Justified\s+Unproved\s*$")
_RULE = re.compile(r"^-{20,}\s*$")
_BANNER = re.compile(r"^={10,}\s*$")
_MAX_STEPS = re.compile(r"^max steps used for successful proof: \d+\s*$")
_NO_DIFFICULT = re.compile(r"^No check found with max time greater than \d+ seconds?\s*$")
_DIFFICULT = re.compile(r"^\S+:\d+:\d+: .+ proved in max \d+ seconds?\s*$")
_ANALYZED = re.compile(r"^Analyzed (\d+) units?\s*$")
_UNIT = re.compile(r"^in unit (\S+), (\d+) subprograms and packages out of (\d+) analyzed$")
_SUBPROGRAM = re.compile(
    r"^  (\S+) at (\S+) flow analyzed \(0 errors, \d+ checks, \d+ warnings and "
    r"0 pragma Assume statements\) and proved \((\d+) checks\)$")
_TITLES = {"Summary of SPARK analysis": "summary", "Most difficult proved checks": "difficult",
           "Detailed analysis report": "detailed"}


def _count(value: str) -> int:
    return 0 if value == "." else int(value.split(" ", 1)[0])


def parse_summary(text: str) -> dict[str, Any]:
    """Every line of a gnatprove.out summary must be recognized: the titled sections, the
    results table (each known category at most once, exactly one Total row, the categories
    summing to it column by column, and Total = Flow + Provers + Justified + Unproved), the
    difficult-checks list and the per-unit report (only fully proved subprograms). Anything
    else raises SummaryError."""
    lines = text.splitlines()
    section: str | None = None
    seen: dict[str, int] = {}
    header = 0
    categories: dict[str, dict[str, int]] = {}
    total: dict[str, int] | None = None
    analyzed_units: int | None = None
    units: dict[str, dict[str, int]] = {}
    subprograms: dict[str, dict[str, Any]] = {}
    listed: dict[str, int] = {}
    current_unit: str | None = None
    index = 0
    while index < len(lines):
        line = lines[index].rstrip("\r")
        if not line.strip():
            index += 1
            continue
        if _BANNER.match(line) and index + 2 < len(lines) and _BANNER.match(lines[index + 2]):
            title = lines[index + 1].strip()
            if title not in _TITLES:
                raise SummaryError(f"unknown section: {title!r}")
            section = _TITLES[title]
            seen[section] = seen.get(section, 0) + 1
            if seen[section] > 1:
                raise SummaryError(f"section repeated: {title!r}")
            current_unit = None
            index += 3
            continue
        if section is None:
            raise SummaryError(f"line outside every section: {line!r}")
        if section == "summary":
            if _RULE.match(line):
                pass
            elif _HEADER.match(line):
                header += 1
            elif _MAX_STEPS.match(line):
                pass
            else:
                row = _ROW.match(line)
                if row is None:
                    raise SummaryError(f"unrecognized results line: {line!r}")
                label = row.group("label").strip()
                counts = {column: _count(row.group(column)) for column in _COLUMNS}
                if label == "Total":
                    if total is not None:
                        raise SummaryError("more than one Total row")
                    total = counts
                elif label in _CATEGORIES:
                    if label in categories:
                        raise SummaryError(f"category repeated: {label}")
                    if total is not None:
                        raise SummaryError(f"category after the Total row: {label}")
                    categories[label] = counts
                else:
                    raise SummaryError(f"unknown results category: {label!r}")
        elif section == "difficult":
            if not (_NO_DIFFICULT.match(line) or _DIFFICULT.match(line)):
                raise SummaryError(f"unrecognized difficult-checks line: {line!r}")
        else:
            analyzed = _ANALYZED.match(line)
            unit = _UNIT.match(line)
            if analyzed is not None:
                if analyzed_units is not None or units:
                    raise SummaryError("the analyzed-units count is repeated or misplaced")
                analyzed_units = int(analyzed.group(1))
            elif unit is not None:
                current_unit = unit.group(1)
                if current_unit in units:
                    raise SummaryError(f"unit repeated: {current_unit}")
                units[current_unit] = {"analyzed": int(unit.group(2)), "available": int(unit.group(3))}
                listed[current_unit] = 0
            elif line.startswith("  ") and current_unit is not None:
                sub = _SUBPROGRAM.match(line)
                if sub is None:
                    raise SummaryError(f"unit {current_unit}: not a proved subprogram: {line.strip()}")
                name, where, checks = sub.groups()
                # Overloads share a name; the manifest keys coverage by name, last one kept (as
                # the gate always recorded it). Each is still counted against its unit.
                subprograms[name] = {"at": where, "checks": int(checks), "proved": True}
                listed[current_unit] += 1
            else:
                raise SummaryError(f"unrecognized report line: {line!r}")
        index += 1
    for required in ("summary", "detailed"):
        if required not in seen:
            raise SummaryError(f"the {required} section is missing")
    if header != 1:
        raise SummaryError(f"the results table has {header} header rows")
    if total is None:
        raise SummaryError("the Total row is missing")
    for column in _COLUMNS:
        if sum(counts[column] for counts in categories.values()) != total[column]:
            raise SummaryError(f"the categories do not sum to the Total row in column {column}")
    if total["total"] != total["flow"] + total["provers"] + total["justified"] + total["unproved"]:
        raise SummaryError("the Total row's columns do not add up to its total")
    if analyzed_units is None or analyzed_units != len(units):
        raise SummaryError(f"the report lists {len(units)} units but says {analyzed_units} were analyzed")
    for unit_name, counts in units.items():
        if listed[unit_name] != counts["analyzed"]:
            raise SummaryError(f"unit {unit_name}: {counts['analyzed']} analyzed but {listed[unit_name]} listed as proved")
    return {**total, "categories": categories, "units": units, "subprograms": subprograms}


# ----- the manifest checks --------------------------------------------------------------------

CHECK_NAMES = ("manifest", "contract-pins", "zero-exceptions", "floor", "summary-digest-recorded", "coverage",
               "source-hashes", "library-hash", "summary")


def manifest_findings(manifest: Any, root: Path, *, library: Path | None = None, library_sha256: str | None = None,
                      summary: bytes | None = None, require_summary: bool = False) -> list[tuple[str, str]]:
    """Every check the gate applies to a manifest against the proof sources under `root`, as
    (check name, problem) in order; empty when all pass. `library` (or its already computed
    digest) is compared with the recorded library hash; `summary`, when given or required, is
    the gnatprove.out the manifest must have been written from."""
    if not isinstance(manifest, Mapping):
        return [("manifest", "the proof manifest is not a JSON object")]
    findings: list[tuple[str, str]] = [("contract-pins", text) for text in contract_problems(root)]
    proof = manifest.get("proof")
    if not isinstance(proof, Mapping):
        return findings + [("manifest", "the proof manifest records no proof counts")]
    if any(type(proof.get(key)) is not int or proof.get(key) != 0 for key in ("justified", "unproved", "pragmaAssume")):
        findings.append(("zero-exceptions", "proof manifest does not record a zero-exception proof"))
    total = proof.get("total")
    if (type(total) is not int or type(proof.get("minimumChecks")) is not int
            or proof.get("minimumChecks") != MINIMUM_CHECKS or total < MINIMUM_CHECKS):
        findings.append(("floor", f"proof manifest records {total!r} checks against a floor of {MINIMUM_CHECKS}"))
    recorded_summary = proof.get("summarySha256")
    if not isinstance(recorded_summary, str) or not re.fullmatch(r"[0-9a-f]{64}", recorded_summary):
        findings.append(("summary-digest-recorded", "proof manifest records no summarySha256"))
    coverage = manifest.get("coverage")
    if not isinstance(coverage, Mapping):
        return findings + [("coverage", "proof manifest records no per-subprogram coverage")]
    subprograms = coverage.get("subprograms")
    units = coverage.get("units")
    boundary = coverage.get("unanalyzedBoundary")
    boundary_valid = (isinstance(boundary, list) and all(isinstance(name, str) for name in boundary)
                      and len(boundary) == len(set(boundary)) and set(boundary) == UNANALYZED_BOUNDARY)
    if coverage.get("requiredProved") != REQUIRED_PROVED or not boundary_valid:
        findings.append(("coverage", "proof manifest does not claim the pinned required subprograms and boundary"))
    if not isinstance(subprograms, Mapping) or not subprograms or not isinstance(units, Mapping):
        return findings + [("coverage", "proof manifest coverage is empty")]
    if any(not (isinstance(value, Mapping) and value.get("proved") is True
                and type(value.get("checks")) is int and value["checks"] >= 0)
           for value in subprograms.values()):
        findings.append(("coverage", "proof manifest records an unproved subprogram"))
    unproved_required = [name for name in REQUIRED_PROVED if name not in subprograms]
    if unproved_required:
        findings.append(("coverage", "required subprograms not proved: " + ", ".join(unproved_required)))
    missing_units = sorted(expected_units(root) - set(units))
    if missing_units:
        findings.append(("coverage", "proof manifest does not cover units: " + ", ".join(missing_units)))
    for unit, counts in units.items():
        if (not isinstance(counts, Mapping) or type(counts.get("analyzed")) is not int
                or type(counts.get("available")) is not int or counts["analyzed"] < 0
                or counts.get("analyzed") != counts.get("available") or (
                unit not in UNANALYZED_BOUNDARY and not counts.get("available"))):
            findings.append(("coverage", f"proof manifest records an unanalyzed unit: {unit}"))
            break
    paths = source_paths(root)
    recorded = manifest.get("sourceHashes")
    if not isinstance(recorded, Mapping) or set(recorded) != set(paths):
        findings.append(("source-hashes", "proof source set changed after proof"))
    else:
        for key, path in paths.items():
            if not path.is_file() or recorded[key] != digest(path):
                findings.append(("source-hashes", f"proof source changed after proof: {key}"))
                break
    if library is not None or library_sha256 is not None:
        recorded_library = (manifest.get("library") or {}).get("sha256") if isinstance(manifest.get("library"), Mapping) else None
        actual = library_sha256
        if actual is None and library is not None:
            actual = digest(library) if library.is_file() else None
        if actual is None or recorded_library != actual:
            findings.append(("library-hash", "proved library changed after proof"))
    if summary is None:
        if require_summary:
            findings.append(("summary", "the proof summary is missing, so the recorded counts cannot be re-derived"))
    else:
        findings += [("summary", text) for text in summary_problems(manifest, summary)]
    return findings


def manifest_problems(manifest: Any, root: Path, **options: Any) -> list[str]:
    return [text for _name, text in manifest_findings(manifest, root, **options)]


def summary_problems(manifest: Mapping[str, Any], summary: bytes) -> list[str]:
    """The summary the manifest names: its digest, and the counts and coverage re-derived from
    it, must equal what the manifest records (OB-085)."""
    proof = manifest.get("proof") if isinstance(manifest.get("proof"), Mapping) else {}
    coverage = manifest.get("coverage") if isinstance(manifest.get("coverage"), Mapping) else {}
    problems: list[str] = []
    if hashlib.sha256(summary).hexdigest() != proof.get("summarySha256"):
        problems.append("the proof summary's digest differs from the manifest's summarySha256")
    try:
        parsed = parse_summary(summary.decode("utf-8"))
    except UnicodeDecodeError as exc:
        return problems + [f"the proof summary is not UTF-8: {exc}"]
    except SummaryError as exc:
        return problems + [f"the proof summary is not recognized: {exc}"]
    for key in ("total", "justified", "unproved"):
        if parsed[key] != proof.get(key):
            problems.append(f"the proof summary records {key} {parsed[key]}, the manifest {proof.get(key)!r}")
    if parsed["units"] != coverage.get("units") or parsed["subprograms"] != coverage.get("subprograms"):
        problems.append("the proof summary's per-unit coverage differs from the manifest's")
    return problems


def load_manifest(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

# Additive protected recovery protocol obligation; no exception/floor change.
REQUIRED_PROVED += ['Worldline.Recovery_Protocol.Reference', 'Worldline.Recovery_Protocol.Advance', 'Worldline.Recovery_Protocol.Changed_Only_By_Resolution', 'Worldline.Recovery_Protocol_Wire.Well_Formed', 'Worldline.Recovery_Protocol_Wire.Decide']
CONTRACT_PINS.update({'core/worldline-recovery_protocol.adb': '1188891c1663c1c0c3ec47d304af9aaf5b14b1f9a74cff6ad771d47d06f5f573', 'core/worldline-recovery_protocol.ads': '7ca9a947061fce2a3278ab064ede1f8c2edad77fb3ecbdb68ef3f1cc41131eec', 'core/worldline-recovery_protocol_c_api.adb': '7caa6d15eda261907906643357d1444d4b912133865fc8503db5b8a1ee8223e2', 'core/worldline-recovery_protocol_c_api.ads': '3e03b5a62930533f5d930fa7e5f2117e1e8099239cf7a5d17651169c7d16b946', 'core/worldline-recovery_protocol_wire.adb': '4716e4c67604bc3ebb236994a30a1f98a2f2684e99fa8a3dde6c6529c2c49d2b', 'core/worldline-recovery_protocol_wire.ads': '389d2fd4ad5a625f1ac5274da214c9b8e953f261882b300fbbfa96d17b5c1cd4', 'core/worldline_core.gpr': 'dec2af772325ced7eea79ff5970d0be8cb7f023d48436d25e458a35940e9f38c', 'recovery-protocol-tests/test_protocol.adb': '04a6b065ae31533e8dcb04b4661aedb467bc0c89a5613bb4fcec01b7734c0447', 'recovery-protocol-tests/recovery_protocol_tests.gpr': '2ab0cb616d8ff722655c92a6767e3c4bf8feb94707b5330f881601d8eb054d40'})

_protected_protocol_original_export_problems = export_problems

def export_problems(root: Path) -> list[str]:
    # Preserve every established export/control before checking new bindings.
    problems = _protected_protocol_original_export_problems(root)
    text = normalized_ada((root / 'core/worldline-recovery_protocol_c_api.ads').read_text(encoding='utf-8'))
    for symbol in ('wl_recovery_protocol_version_v1', 'wl_recovery_protocol_layout_v1',
                   'wl_recovery_protocol_decide_v1'):
        if text.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'protected recovery protocol export binding differs: {symbol}')
    return problems

# Complete-chain source additions; no old proof evidence transfers.
REQUIRED_PROVED += ['Worldline.Chain_Authority.Link', 'Worldline.Chain_Authority.Present', 'Worldline.Chain_Authority.Prefix_Reference', 'Worldline.Chain_Authority.Replay_Reference', 'Worldline.Chain_Authority.Replay', 'Worldline.Chain_Authority_Wire.Well_Formed', 'Worldline.Chain_Authority_Wire.Decode', 'Worldline.Chain_Authority_Wire.Decide']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/worldline-chain_authority.adb', 'core/worldline-chain_authority.ads', 'core/worldline-chain_authority_c_api.adb', 'core/worldline-chain_authority_c_api.ads', 'core/worldline-chain_authority_wire.adb', 'core/worldline-chain_authority_wire.ads'])
CONTRACT_PINS.update({'core/worldline-chain_authority.adb': '4c7052b3835615308d6332303d9e9ccc2bab7b741a6c7a8457c7f98a8a4b8881', 'core/worldline-chain_authority.ads': 'b96d3635c43ec01db68f07140f0343a620214b1672c3be6114cbc40a593e44ae', 'core/worldline-chain_authority_c_api.adb': 'f2ef756386993a1283198b489f23ad371cd05c0cf13b9a78deade84793c2b919', 'core/worldline-chain_authority_c_api.ads': 'a90a458e11cd824506bd350de0bb84001e62b7982960459a3c7c30723276b99a', 'core/worldline-chain_authority_wire.adb': '9ff2355dbebbf8192b78e21adb225bb8405968612a1c8cc6e6778f27c42961e4', 'core/worldline-chain_authority_wire.ads': '7baf22c73d65bb6ba5dbe5386453da06a8b600f8a81e58931bf9c6377bada4f1'})
_chain_predecessor_export_problems = export_problems
def export_problems(root: Path) -> list[str]:
    problems = _chain_predecessor_export_problems(root)
    spec = (root / 'core/worldline-chain_authority_c_api.ads').read_text()
    body = (root / 'core/worldline-chain_authority_c_api.adb').read_text()
    if spec.count('External_Name => "wl_chain_authority_replay_v1"') != 1 or 'Result_At (Output).all := W.Decide (Owned, H);' not in body:
        problems.append('complete-chain native export is not bound to the selected full-row wire decision')
    return problems

# Complete owner-operation component; all original rules/callers stay required.
REQUIRED_PROVED += ['Worldline.Owner_Transitions.Present', 'Worldline.Owner_Transitions.Same', 'Worldline.Owner_Transitions.Cursor_Present', 'Worldline.Owner_Transitions.Same_Cursor', 'Worldline.Owner_Transitions.Common_Present', 'Worldline.Owner_Transitions.Common_Valid', 'Worldline.Owner_Transitions.Latest_Failed_Head', 'Worldline.Owner_Transitions.Query_For', 'Worldline.Owner_Transitions.Retry_Holds', 'Worldline.Owner_Transitions.Retry_Reference', 'Worldline.Owner_Transitions.Reference', 'Worldline.Owner_Transitions.Authorize', 'Worldline.Owner_Transitions_Wire.Identity_Valid', 'Worldline.Owner_Transitions_Wire.Cursor_Valid', 'Worldline.Owner_Transitions_Wire.Row_Valid', 'Worldline.Owner_Transitions_Wire.Grant_Valid', 'Worldline.Owner_Transitions_Wire.Request_Valid', 'Worldline.Owner_Transitions_Wire.Well_Formed', 'Worldline.Owner_Transitions_Wire.Span', 'Worldline.Owner_Transitions_Wire.Identity', 'Worldline.Owner_Transitions_Wire.Epoch', 'Worldline.Owner_Transitions_Wire.Cursor', 'Worldline.Owner_Transitions_Wire.Subject', 'Worldline.Owner_Transitions_Wire.Content', 'Worldline.Owner_Transitions_Wire.Requirement', 'Worldline.Owner_Transitions_Wire.Run', 'Worldline.Owner_Transitions_Wire.Row', 'Worldline.Owner_Transitions_Wire.Grant', 'Worldline.Owner_Transitions_Wire.Decode', 'Worldline.Owner_Transitions_Wire.Rows', 'Worldline.Owner_Transitions_Wire.Decide']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/worldline-owner_transitions.adb', 'core/worldline-owner_transitions.ads', 'core/worldline-owner_transitions_wire.adb', 'core/worldline-owner_transitions_wire.ads'])
CONTRACT_PINS.update({'core/worldline-owner_transitions.adb': '6e8735f539da94f023a7a9fd3ac76a1d6566c6d97e7cfe349205d1f285bbc387', 'core/worldline-owner_transitions.ads': '6a372ec0b94c9a5f6f29a3a652981c4d0532a0500feafe7d569cd668dc7a44e4', 'core/worldline-owner_transitions_wire.adb': '1fdad555d323af2a611072caa703d272bb074a61f481ba9677285eba13818d0b', 'core/worldline-owner_transitions_wire.ads': '8867a739ddc2b22c3d73c8908a0be7bb8ecd1410bbe9232776499aa57837f814'})
_owner_predecessor_export_problems = export_problems
def export_problems(root: Path) -> list[str]:
    problems = _owner_predecessor_export_problems(root)
    spec = (root / 'core/worldline-c_api.ads').read_text()
    body = (root / 'core/worldline-c_api.adb').read_text()
    exports = ('wl_owner_transition_version_v1','wl_owner_transition_layout_v1','wl_owner_transition_authorize_v1')
    if any(spec.count('External_Name => "' + name + '"') != 1 for name in exports) or 'Owner_Wire.Decide (A, H, F, Final_Present, Raw)' not in body:
        problems.append('complete owner-operation ABI is not bound to the full native wire relation')
    return problems

# Explicit complete source composition; every original proof condition stays required.
REQUIRED_PROVED += ['Resource_Run_Ledger.Id_Valid', 'Resource_Run_Ledger.Same', 'Resource_Run_Ledger.Optional_Same', 'Resource_Run_Ledger.Same_Epoch', 'Resource_Run_Ledger.Context_Valid', 'Resource_Run_Ledger.Same_Context', 'Resource_Run_Ledger.Binding_Valid', 'Resource_Run_Ledger.Same_Binding', 'Resource_Run_Ledger.Has_Effect', 'Resource_Run_Ledger.Counted', 'Resource_Run_Ledger.Row_Valid', 'Resource_Run_Ledger.Same_Row', 'Resource_Run_Ledger.Exact_Value', 'Resource_Run_Ledger.Amount_Reference', 'Resource_Run_Ledger.Amount', 'Resource_Run_Ledger.Included', 'Resource_Run_Ledger.Sum_Reference', 'Resource_Run_Ledger.Sum', 'Resource_Run_Ledger.Cgroup_Inside', 'Resource_Run_Ledger.Shape', 'Resource_Run_Ledger.Conserved_Reference', 'Resource_Run_Ledger.Conserved', 'Resource_Run_Ledger.Parent_Supports', 'Resource_Run_Ledger.Contained_Reference', 'Resource_Run_Ledger.Contained', 'Resource_Run_Ledger.Native_Valid', 'Resource_Run_Ledger.Changed_Row_Allowed', 'Resource_Run_Ledger.Decision_Reference', 'Resource_Run_Ledger.Check', 'Resource_Run_Ledger_Wire.Well_Formed', 'Resource_Run_Ledger_Wire.Decode', 'Resource_Run_Ledger_Wire.Decode_Rows', 'Resource_Run_Ledger_Wire.Decode_Native', 'Resource_Run_Ledger_Wire.Decide']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/resource_run_ledger.adb', 'core/resource_run_ledger.ads', 'core/resource_run_ledger_c_api.adb', 'core/resource_run_ledger_c_api.ads', 'core/resource_run_ledger_wire.adb', 'core/resource_run_ledger_wire.ads', 'core/worldline-recovery_protocol.adb', 'core/worldline-recovery_protocol.ads', 'core/worldline-recovery_protocol_c_api.adb', 'core/worldline-recovery_protocol_c_api.ads', 'core/worldline-recovery_protocol_wire.adb', 'core/worldline-recovery_protocol_wire.ads'])
CONTRACT_PINS.update({'artifact-tests/canonical_artifact_tests.gpr': 'bce2824cc8181edb5f1e9d5b9c0a391d70d68302b9f717ae44f87a0cd4a1ea05', 'artifact-tests/test_canonical_artifacts.adb': '43137b6f14b3c71b87de8f09c957e95d29a7d44dab5c67fc92698be12c50b8f1', 'core/attest/attest-sha256.ads': '1d38534d6bcaa9a6646225db8f26f0a7b940444cda3ed0d109816119d51bff05', 'core/attest/attest.ads': 'bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587', 'core/attest_sha256.gpr': '5d75d10379e9397a9e08517d56728b2f53479fd7c0e9dff3b5dccaa8e8c0f9ee', 'core/canonical_artifacts.adb': 'da52dd9ed5856088f2fc3fd6cdf04065f8236456c4f7ec9593e7aff4b21fb80c', 'core/canonical_artifacts.ads': '303ac80cabec2e2ef34029f6f8bd27c4100592cc9b8791b79f9a7475b9a0fa11', 'core/evaluation_completion.adb': '1dc167205298b20bebddd0a5f7cec246827a7406b797681189bf73f29818a700', 'core/evaluation_completion.ads': '6eba1ac186ea36ffc07a1bb5320288b151cbc0a6435fce0d1255aa4c75418c3b', 'core/evaluation_completion_c.adb': '6e2409ec629f107ddd50dc54d89e1686383df1dd7b4d26a23039d8d3a9905a94', 'core/evaluation_completion_c.ads': '7b46d8a2b7af881a2f25e5d8637362140c493096f7970145021a42a2c27ff408', 'core/evaluation_completion_roster.adb': 'f52e2b9d4a909b3c2b616e92aaf7b87ce4ddb8a6e8b34ea99068915dc9bb253a', 'core/evaluation_completion_roster.ads': '5af5ec8259073ad74444b5a4596b2a4b05e568c7d26739b9210e9b4616a2a2a3', 'core/evaluation_epoch.adb': '1958820a7247823c06a3295ab6fbd86bd1bff3ccd7cf6d7c71d94425e11d0259', 'core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'core/evaluation_finalization.adb': 'f17fdd15b13842c466a1e118f1accf02de4c08f50b529bbc60a117cd621bde92', 'core/evaluation_finalization.ads': '3b8a3d418361e255cd7cff14d4acc9e17ab9684dba66ea398fd83ef579ce20b2', 'core/evaluation_finalization_c.adb': '6d045dff8ad7c03250c7c36e20680465f883a2b08938e8bc7cc2d6bda0902f1a', 'core/evaluation_finalization_c.ads': '6ca339c64f2399ab819c1a5d1d3195d365a4cd19a330cbf7ad42bdd112cc2fc0', 'core/evaluation_history.adb': 'e714beb4979f89706e3d7636fbfcfe23d1a99b319b53635b06dc3fdf6248209f', 'core/evaluation_history.ads': 'e58eea740afa7f385a386ad97ad78380eb61ccac35d7669f14768dd4ac30cc3a', 'core/evaluation_pending_v2.adb': 'd8864beff6356c688f3ed26c84d27e6d0e315c423e150ee257e45df71bad3a66', 'core/evaluation_pending_v2.ads': '1e20de75c125ff20b5ad5750466430e959fb104b27f905403e38a35eb01f8321', 'core/evaluation_raw_roster.adb': 'f2808bdf8a8403cde066aee07565eb0c494e4081a04783c9dbdc1ec5c37abe6f', 'core/evaluation_raw_roster.ads': '6bdb761e4be7a6dec36373293ffb7de064ddaa250a811ce9ebb6dcf2db69788b', 'core/resource_admission.adb': '0da682e7cd0aa85daea88a9f36926fa213240b9273cd7015108f95f4f48ee63c', 'core/resource_admission.ads': '2d93c087e980ec50ce77a21efdeb4c2d3a96e503493e55c0a9cbbb27e80381f2', 'core/resource_ledger.adb': '01994b6554254e009a7b1a8b9ca3e7df2fc1b488829176db65db6e2cb7c8418c', 'core/resource_ledger.ads': 'ddf46ac440a9c372f7c4b30d1d91463061a45be05653fee181f25164bdd2f0f1', 'core/resource_quantities.adb': 'a527cfdeae1671b27a901e6adc7f80fc89966980acc80f2775d77b540a63ec47', 'core/resource_quantities.ads': '21640498940fc92941624d97a6645bf14a3e1fa9bf3bc951c6f85e93d0d5f412', 'core/resource_reservation_lifecycle.adb': '3cf6bbe8dfef85f485be16eb9185768ace28ddc6a3ea5bfe0cd0aa26dd8aef41', 'core/resource_reservation_lifecycle.ads': '8e3c85334abc8ff747e6f468bea29f04196c3c11cffa10a68207b96c8b3e0400', 'core/resource_reservation_transition.adb': '3af393cccae017478ec583bd32f4f8d543add470253d9e367a6e21f86cdfbcc4', 'core/resource_reservation_transition.ads': '668286cd1a05a5820ac0b75c3c3d7f7f25ddb005b78d05960f6aa1d9320f8f78', 'core/resource_run_ledger.adb': '95880816a92fd4a435d9749392676e312a800f9d63d912649e0cdbb3baaff9a9', 'core/resource_run_ledger.ads': '4f2324ec6464f533cea438860725075e340b192645f14c2d1424c0d135b8fe3e', 'core/resource_run_ledger_c_api.adb': 'f23aebc393245e5ce85edeb387297536a66ca74a6ca727a032662f3c084f4547', 'core/resource_run_ledger_c_api.ads': 'c492e646c056e6931151725be3e0092ec1bb9195a32f51a8fa675722c1815cbf', 'core/resource_run_ledger_wire.adb': '9dfbf2149d066c31e5a2e8271c1cbb1246c9c1ad6eadb038bb3377e9bda11088', 'core/resource_run_ledger_wire.ads': 'b09d4e07df8652f8f87b2a6526f0fa26875253ea1dc8909bbec6b330d6d02eed', 'core/worldline-ancestry.ads': '718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db', 'core/worldline-c_api.adb': 'c5c7c80c20f40cfdaa227453e33310a2196bedc6174ce15c5033d462328402fd', 'core/worldline-c_api.ads': 'c9af2976fe490a72d80e7a1287baf9c9c3427008d3cc8efadd3e139eaef96872', 'core/worldline-causal_graph.adb': 'a7e80ad0b061be82ce2727e5aeabd6fa27335807d66445ad01dc3fb3931dfab5', 'core/worldline-causal_graph.ads': '1f5271eed9dc2bdacf2642a9647bab7a2b29a707c7749664ba09f7fac79ce14f', 'core/worldline-chain_authority.adb': '4c7052b3835615308d6332303d9e9ccc2bab7b741a6c7a8457c7f98a8a4b8881', 'core/worldline-chain_authority.ads': 'b96d3635c43ec01db68f07140f0343a620214b1672c3be6114cbc40a593e44ae', 'core/worldline-chain_authority_c_api.adb': 'f2ef756386993a1283198b489f23ad371cd05c0cf13b9a78deade84793c2b919', 'core/worldline-chain_authority_c_api.ads': 'a90a458e11cd824506bd350de0bb84001e62b7982960459a3c7c30723276b99a', 'core/worldline-chain_authority_wire.adb': '9ff2355dbebbf8192b78e21adb225bb8405968612a1c8cc6e6778f27c42961e4', 'core/worldline-chain_authority_wire.ads': '7baf22c73d65bb6ba5dbe5386453da06a8b600f8a81e58931bf9c6377bada4f1', 'core/worldline-collapse.ads': '94ef49a258a46363eea81d44e168ce4e7cc618fdf128e916e92e447f2ffe32e2', 'core/worldline-collapse_wire.ads': '48270be156ee3f1c7d7f6215917c9b8026ac5346c45064cf7803950c137ddd76', 'core/worldline-evaluation.ads': '06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e', 'core/worldline-evaluation_authority.adb': 'd907b1d4eda41e7f7167695520085071686c834f8c1adb6691307661c3043d3a', 'core/worldline-evaluation_authority.ads': '1ee7d183c40c6b98b7f98277f96924e3135fedd83900134a3ff4461bcf237694', 'core/worldline-evaluation_report_facts.adb': 'ffdc1629f8eaef1ec4ab1bbc4fc988f2f1546dd8b5013ec4635888d77f8240fb', 'core/worldline-evaluation_report_facts.ads': 'f8bfee03303776b2825662bb1ce394fdf3c3e6acf3e7b1084500e50eba430f82', 'core/worldline-evaluation_report_wire.adb': '19ed101a83a9a9350a660cd7693a8be7ffee86557fa6d58e7959a0ae9973ff78', 'core/worldline-evaluation_report_wire.ads': 'a58347985c4242421c4114ecf61ddaf6f84229e62ab2114cd0947b7feee29b19', 'core/worldline-evaluation_v2.adb': '2fc57758a66ac2c7aa9ef6e108fdcbf93b1b286fd64b6620d8bca54ce32312eb', 'core/worldline-evaluation_v2.ads': '8e1f18244b924a7c9c05c67fdf785491a910c9f7c59966381b38962c2f68a72c', 'core/worldline-evaluation_wire.adb': '30696c9e2b4be84aad47d406864213a176f494e07dbed6f6907efe601d3be530', 'core/worldline-evaluation_wire.ads': '8b190a32f057a30a700e3331bd72aa2cfc18c5d6f3540b824756197f09077c7a', 'core/worldline-identities.ads': 'ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21', 'core/worldline-owner_transitions.adb': '6e8735f539da94f023a7a9fd3ac76a1d6566c6d97e7cfe349205d1f285bbc387', 'core/worldline-owner_transitions.ads': '6a372ec0b94c9a5f6f29a3a652981c4d0532a0500feafe7d569cd668dc7a44e4', 'core/worldline-owner_transitions_wire.adb': '1fdad555d323af2a611072caa703d272bb074a61f481ba9677285eba13818d0b', 'core/worldline-owner_transitions_wire.ads': '8867a739ddc2b22c3d73c8908a0be7bb8ecd1410bbe9232776499aa57837f814', 'core/worldline-receipts.adb': '1ee34566208a835951d21d79be1bc6ffd287b3c61b43bad76210a7a546b156bb', 'core/worldline-receipts.ads': '45e8c276cf73d8d0311f247a1c87e9bf88614d46fde2bfe6c5f858ee2d20827b', 'core/worldline-recovery.adb': '75763d6eb35c647df523a728c6939e21cda6c3d7b44ba54fb2a4a917f3149e24', 'core/worldline-recovery.ads': '735d3411bd85c84f7e9f0449c34808f9c9ae226d82aac5e396448b4d27f4668a', 'core/worldline-recovery_authorization.adb': 'd90b75ec516fbf8ddb0f0bf40ee39297e70eebc001d4edad6b0142c7da092e7d', 'core/worldline-recovery_authorization.ads': '3b95bc25da8343b9d0c4cd6e133614bb59cdce65740142d9c2d2ed072e62dec6', 'core/worldline-recovery_authorization_c_api.adb': '0f3e1162efebf4b9d15197c5e224c4ebec3bd4f63a476b49a5a584c466c0e471', 'core/worldline-recovery_authorization_c_api.ads': 'afc10c9f738f0bba486ade982b7250327b31972f64c5a33b319f1662d2ff059e', 'core/worldline-recovery_authorization_v3.adb': '21536d8595e0d6d14764b56309eb2f88d28bd88fc47b6fe9c16f915c98ed63dd', 'core/worldline-recovery_authorization_v3.ads': '8b3f3c7477c461dadceba33ab421cf54d4c77129e2875768346d93c91f3fdd51', 'core/worldline-recovery_authorization_v3_c_api.adb': 'fa1d4aa2b0e138656314651f52312113dbdaa6bd3f491714115c234e8f2e5d39', 'core/worldline-recovery_authorization_v3_c_api.ads': '96b679271cea641ab5bcf84784fa08193d56b19b456a67d3d08007268d8ed2b5', 'core/worldline-recovery_authorization_v3_wire.adb': '5df8bd9bcd6842aaf033bde67edd121e6d9e0bdfd6f29158f0f8b1a57fd36bc6', 'core/worldline-recovery_authorization_v3_wire.ads': '30a49ffee1fecf33fe798e524cda06f73a8a2164ffe92c2bce8a10155a45f90e', 'core/worldline-recovery_authorization_wire.adb': 'e0c1054dd20e34bf1ddbcaefd9665c7588fc4683c8dad1a91351c89597928f62', 'core/worldline-recovery_authorization_wire.ads': 'a6b453f40b2eee2d860008ecb11b9720f6be2a5be5c1aca52a91f264c40d687c', 'core/worldline-recovery_protocol.adb': '1188891c1663c1c0c3ec47d304af9aaf5b14b1f9a74cff6ad771d47d06f5f573', 'core/worldline-recovery_protocol.ads': '7ca9a947061fce2a3278ab064ede1f8c2edad77fb3ecbdb68ef3f1cc41131eec', 'core/worldline-recovery_protocol_c_api.adb': '7caa6d15eda261907906643357d1444d4b912133865fc8503db5b8a1ee8223e2', 'core/worldline-recovery_protocol_c_api.ads': '3e03b5a62930533f5d930fa7e5f2117e1e8099239cf7a5d17651169c7d16b946', 'core/worldline-recovery_protocol_wire.adb': '4716e4c67604bc3ebb236994a30a1f98a2f2684e99fa8a3dde6c6529c2c49d2b', 'core/worldline-recovery_protocol_wire.ads': '389d2fd4ad5a625f1ac5274da214c9b8e953f261882b300fbbfa96d17b5c1cd4', 'core/worldline-resource_wire.adb': 'ec1ea00cf321f841aafcb874047c48d1ff28363d29ea042c6703a60a2be32f80', 'core/worldline-resource_wire.ads': 'b0af3ef936e727ba9113430ebc29c2843124f82e584b3bb294dc23af2667ad75', 'core/worldline-resources.adb': '0e65d26b226f8de7c665ff0effde568057f5fd135f7dafad85f110a697ea8e17', 'core/worldline-resources.ads': '3abbfe401429b72094c8e06be392ff3cb7612149f125d1249f4b8bf5792c978e', 'core/worldline-transitions.ads': '5b9c8f89900d01eeb40818de6392e1f23f8e2606cba702dd06e72e4257406c27', 'core/worldline-world.ads': '3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5', 'core/worldline.ads': '4e08ff1dedc1f28b526a19b37c343b2d71f5f1e35409abda2afdbd92a73ab866', 'core/worldline_core.gpr': '36ca160e38852873b02317a6365796c781c7d78afcf05cf4133c7488c5bcc5f0', 'core/worldline_core_sources.gpr': 'fc7be69ee1d21269d12f600a3dab22b53c21362d178280d5f8ddcacf5c09802c', 'evaluation-authority-tests/evaluation_authority_tests.gpr': 'f9ba8e8e3b9593454c25f74a5678599ebdf09afbf8510b119ebfa6f8820a98f4', 'evaluation-authority-tests/test_evaluation_authority.adb': '071e0f859f92ac1576f95dc1c6e6f89df84c59edb304b36c3e15f0a887e98730', 'evaluation-wire-tests/evaluation_wire_tests.gpr': '8fde6733c882c9be99a7fbcdce0c6ba0a8eca138a4b68e65ec77efdc84160d89', 'pending-component/core/evaluation_epoch.adb': '1958820a7247823c06a3295ab6fbd86bd1bff3ccd7cf6d7c71d94425e11d0259', 'pending-component/core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'pending-component/core/resource_quantities.adb': 'a527cfdeae1671b27a901e6adc7f80fc89966980acc80f2775d77b540a63ec47', 'pending-component/core/resource_quantities.ads': '21640498940fc92941624d97a6645bf14a3e1fa9bf3bc951c6f85e93d0d5f412', 'recovery-epoch-tests/recovery_epoch_tests.gpr': '600c9e1b3b3524f1419f2419a0e0925641a9dec1c822fb0b5ddb1e2afc9bc880', 'recovery-epoch-tests/test_epochs.adb': 'b134c380bb6990c55df7c21c590627585c57a8f0bbb99453a4d4c61913a68670', 'recovery-protocol-tests/recovery_protocol_tests.gpr': '2ab0cb616d8ff722655c92a6767e3c4bf8feb94707b5330f881601d8eb054d40', 'recovery-protocol-tests/test_protocol.adb': '04a6b065ae31533e8dcb04b4661aedb467bc0c89a5613bb4fcec01b7734c0447', 'tests/worldline_tests.gpr': 'd452b39691f23078635cb829b0ef94040342cefec9288cd4cccb821a51ca6a82', 'worldline.gpr': 'edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021'})

# Complete additive owner audit, subject projection and collapse conjunction.
REQUIRED_PROVED += ['Worldline.Owner_Retry_Audit.Query_For', 'Worldline.Owner_Retry_Audit.Same_Row', 'Worldline.Owner_Retry_Audit.Same_Finalization', 'Worldline.Owner_Retry_Audit.Same_Prefix', 'Worldline.Owner_Retry_Audit.Same_Grant', 'Worldline.Owner_Retry_Audit.Receipt_Holds', 'Worldline.Owner_Retry_Audit.Attempt_Holds', 'Worldline.Owner_Retry_Audit.Binding_Holds', 'Worldline.Owner_Retry_Audit.Before_Closed', 'Worldline.Owner_Retry_Audit.Holds', 'Worldline.Owner_Retry_Audit.Reference', 'Worldline.Owner_Retry_Audit.Decide', 'Worldline.Owner_Retry_Audit_Wire.Valid', 'Worldline.Owner_Retry_Audit_Wire.Decode', 'Worldline.Owner_Retry_Audit_Wire.Well_Formed', 'Worldline.Owner_Retry_Audit_Wire.Final', 'Worldline.Owner_Retry_Audit_Wire.Decide', 'Worldline.Owner_Conjunction.Nibble', 'Worldline.Owner_Conjunction.Hash_Holds', 'Worldline.Owner_Conjunction.Scope_Holds', 'Worldline.Owner_Conjunction.Original_Scope_Holds', 'Worldline.Owner_Conjunction.Adopt_Holds', 'Worldline.Owner_Conjunction.Checkpoint_Holds', 'Worldline.Owner_Conjunction.Checkpoint_Reference', 'Worldline.Owner_Conjunction.Authorize_Checkpoint', 'Worldline.Owner_Conjunction.Retry_Holds', 'Worldline.Owner_Conjunction.Retry_Reference', 'Worldline.Owner_Conjunction.Authorize_Retry', 'Worldline.Owner_Conjunction.Adopt_Receipt_Holds', 'Worldline.Owner_Conjunction.Adopt_Receipt_Reference', 'Worldline.Owner_Conjunction.Authorize_Adopt_Receipt', 'Worldline.Owner_Conjunction_Wire.Scope_Valid', 'Worldline.Owner_Conjunction_Wire.Scope', 'Worldline.Owner_Conjunction_Wire.Checkpoint_Reference', 'Worldline.Owner_Conjunction_Wire.Authorize_Checkpoint', 'Worldline.Owner_Conjunction_Wire.Retry_Reference', 'Worldline.Owner_Conjunction_Wire.Authorize_Retry', 'Worldline.Owner_Conjunction_Wire.Adopt_Receipt_Reference', 'Worldline.Owner_Conjunction_Wire.Authorize_Adopt_Receipt', 'Worldline.Owner_Subject_Projection.Feed', 'Worldline.Owner_Subject_Projection.Feed_String', 'Worldline.Owner_Subject_Projection.UTF8_Valid', 'Worldline.Owner_Subject_Projection.Quoted', 'Worldline.Owner_Subject_Projection.Reference', 'Worldline.Owner_Subject_Projection.Project', 'Worldline.Owner_Subject_Projection.Matches']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/worldline-owner_retry_audit.ads', 'core/worldline-owner_retry_audit.adb', 'core/worldline-owner_retry_audit_wire.ads', 'core/worldline-owner_retry_audit_wire.adb', 'core/worldline-owner_conjunction.ads', 'core/worldline-owner_conjunction.adb', 'core/worldline-owner_conjunction_wire.ads', 'core/worldline-owner_conjunction_wire.adb', 'core/worldline-owner_subject_projection.ads', 'core/worldline-owner_subject_projection.adb'])
CONTRACT_PINS.update({'core/worldline-owner_retry_audit.ads': 'f10e8a5758de157d40ab487c2b5071232cc8ede3b0984b36e75e922dff5b49e0', 'core/worldline-owner_retry_audit.adb': 'd444de903bc184300bbfd6e95348f4307827b7ad3948e4fe77c091daec52b5bd', 'core/worldline-owner_retry_audit_wire.ads': '60772578c6f02b53ea7b4d5614dde93f4e6d02e073847932c4647853d205f979', 'core/worldline-owner_retry_audit_wire.adb': 'a90756485c89699537c11c14b86fe5444c9ab7eb8fd3352ca4006f4610ab666f', 'core/worldline-owner_conjunction.ads': '62559ebaa5c94a88435d44333ac61aede278af67813f3ab7ac72d27bd86ec89d', 'core/worldline-owner_conjunction.adb': '9d6f3f09c955a8612747f088a14802c5004a9a656009389e11254d6d623f3c32', 'core/worldline-owner_conjunction_wire.ads': 'a078f33e659fcb0c0eac74e63777425181bd5e2865566abfb79f36fc34aa510d', 'core/worldline-owner_conjunction_wire.adb': '8aedcbc566fc59ca8a600a6410199ef8ec31b3fbffb655e856e679007f0fc7c7', 'core/worldline-owner_subject_projection.ads': '2aa7d9d7208c340ae46ac36a4bf74d0dfe1ce2f53fdae435f95fcdc39479b7f7', 'core/worldline-owner_subject_projection.adb': 'abcf67952cd84158f7a536c8315402ab6a7cb3a9f32ba13e7587ad1d0119df72', 'core/worldline-c_api.ads': '4c533f63b629146beea81b20c7bddcae385beafb61ffc62cc866212f6d5c4c6b', 'core/worldline-c_api.adb': '30173e332d646fa1763d2dba61c11ad451d0f1d5ec41fef1cd41a1014ae076ce', 'core/worldline_core.gpr': 'a530e073951d381f14ee4508095f34e550c68030f1b5f754ca78e0d5e79dcd56'})
_owner_audit_predecessor_export_problems = export_problems
def export_problems(root: Path) -> list[str]:
    problems = _owner_audit_predecessor_export_problems(root)
    spec = normalized_ada((root / 'core/worldline-c_api.ads').read_text())
    body = normalized_ada((root / 'core/worldline-c_api.adb').read_text())
    exports = ('wl_owner_audit_version_v1','wl_owner_audit_layout_v1','wl_owner_audit_decide_v1')
    if any(spec.count('External_Name => "'+name+'"') != 1 for name in exports):
        problems.append('complete owner audit ABI exports differ')
    binding = ('function Owner_Audit_Decide (Mode : Interfaces.Unsigned_8; Data : System.Address; Data_Length : Interfaces.C.size_t; '
        'Before : System.Address; Before_Count : Interfaces.C.size_t; After : System.Address; After_Count : Interfaces.C.size_t; '
        'Before_Present : Interfaces.Unsigned_8; Before_Final : System.Address; After_Present : Interfaces.Unsigned_8; '
        'After_Final : System.Address; Audit, Original, Scope, Resulting : System.Address; Adopt_Present : Interfaces.Unsigned_8; '
        'Adopt, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_owner_audit_decide_v1";')
    if binding not in spec or any(call not in body for call in
        ('Retry_Wire.Decide (A, B, H, BF, AF, Before_Present, After_Present, Q)',
         'Join_Wire.Authorize_Retry (A, B, H, BF, AF, Before_Present, After_Present, C, S, Q)',
         'Join_Wire.Authorize_Checkpoint (A, B, BF, Before_Present, C, R, S, Adopt_Present, G)',
         'Join_Wire.Authorize_Adopt_Receipt (A, B, BF, Before_Present, C, R, S, Q)')):
        problems.append('owner audit export does not bind complete native conjunction')
    return problems

# Exact complete owner caller composition; no prior proof credit transfers.
CONTRACT_PINS.update({'artifact-tests/canonical_artifact_tests.gpr': 'bce2824cc8181edb5f1e9d5b9c0a391d70d68302b9f717ae44f87a0cd4a1ea05', 'artifact-tests/test_canonical_artifacts.adb': '43137b6f14b3c71b87de8f09c957e95d29a7d44dab5c67fc92698be12c50b8f1', 'core/attest/attest-sha256.ads': '1d38534d6bcaa9a6646225db8f26f0a7b940444cda3ed0d109816119d51bff05', 'core/attest/attest.ads': 'bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587', 'core/attest_sha256.gpr': '5d75d10379e9397a9e08517d56728b2f53479fd7c0e9dff3b5dccaa8e8c0f9ee', 'core/canonical_artifacts.adb': 'da52dd9ed5856088f2fc3fd6cdf04065f8236456c4f7ec9593e7aff4b21fb80c', 'core/canonical_artifacts.ads': '303ac80cabec2e2ef34029f6f8bd27c4100592cc9b8791b79f9a7475b9a0fa11', 'core/evaluation_completion.adb': '1dc167205298b20bebddd0a5f7cec246827a7406b797681189bf73f29818a700', 'core/evaluation_completion.ads': '6eba1ac186ea36ffc07a1bb5320288b151cbc0a6435fce0d1255aa4c75418c3b', 'core/evaluation_completion_c.adb': '6e2409ec629f107ddd50dc54d89e1686383df1dd7b4d26a23039d8d3a9905a94', 'core/evaluation_completion_c.ads': '7b46d8a2b7af881a2f25e5d8637362140c493096f7970145021a42a2c27ff408', 'core/evaluation_completion_roster.adb': 'f52e2b9d4a909b3c2b616e92aaf7b87ce4ddb8a6e8b34ea99068915dc9bb253a', 'core/evaluation_completion_roster.ads': '5af5ec8259073ad74444b5a4596b2a4b05e568c7d26739b9210e9b4616a2a2a3', 'core/evaluation_epoch.adb': '1958820a7247823c06a3295ab6fbd86bd1bff3ccd7cf6d7c71d94425e11d0259', 'core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'core/evaluation_finalization.adb': 'f17fdd15b13842c466a1e118f1accf02de4c08f50b529bbc60a117cd621bde92', 'core/evaluation_finalization.ads': '3b8a3d418361e255cd7cff14d4acc9e17ab9684dba66ea398fd83ef579ce20b2', 'core/evaluation_finalization_c.adb': '6d045dff8ad7c03250c7c36e20680465f883a2b08938e8bc7cc2d6bda0902f1a', 'core/evaluation_finalization_c.ads': '6ca339c64f2399ab819c1a5d1d3195d365a4cd19a330cbf7ad42bdd112cc2fc0', 'core/evaluation_history.adb': 'e714beb4979f89706e3d7636fbfcfe23d1a99b319b53635b06dc3fdf6248209f', 'core/evaluation_history.ads': 'e58eea740afa7f385a386ad97ad78380eb61ccac35d7669f14768dd4ac30cc3a', 'core/evaluation_pending_v2.adb': 'd8864beff6356c688f3ed26c84d27e6d0e315c423e150ee257e45df71bad3a66', 'core/evaluation_pending_v2.ads': '1e20de75c125ff20b5ad5750466430e959fb104b27f905403e38a35eb01f8321', 'core/evaluation_raw_roster.adb': 'f2808bdf8a8403cde066aee07565eb0c494e4081a04783c9dbdc1ec5c37abe6f', 'core/evaluation_raw_roster.ads': '6bdb761e4be7a6dec36373293ffb7de064ddaa250a811ce9ebb6dcf2db69788b', 'core/resource_admission.adb': '0da682e7cd0aa85daea88a9f36926fa213240b9273cd7015108f95f4f48ee63c', 'core/resource_admission.ads': '2d93c087e980ec50ce77a21efdeb4c2d3a96e503493e55c0a9cbbb27e80381f2', 'core/resource_ledger.adb': '01994b6554254e009a7b1a8b9ca3e7df2fc1b488829176db65db6e2cb7c8418c', 'core/resource_ledger.ads': 'ddf46ac440a9c372f7c4b30d1d91463061a45be05653fee181f25164bdd2f0f1', 'core/resource_quantities.adb': 'a527cfdeae1671b27a901e6adc7f80fc89966980acc80f2775d77b540a63ec47', 'core/resource_quantities.ads': '21640498940fc92941624d97a6645bf14a3e1fa9bf3bc951c6f85e93d0d5f412', 'core/resource_reservation_lifecycle.adb': '3cf6bbe8dfef85f485be16eb9185768ace28ddc6a3ea5bfe0cd0aa26dd8aef41', 'core/resource_reservation_lifecycle.ads': '8e3c85334abc8ff747e6f468bea29f04196c3c11cffa10a68207b96c8b3e0400', 'core/resource_reservation_transition.adb': '3af393cccae017478ec583bd32f4f8d543add470253d9e367a6e21f86cdfbcc4', 'core/resource_reservation_transition.ads': '668286cd1a05a5820ac0b75c3c3d7f7f25ddb005b78d05960f6aa1d9320f8f78', 'core/resource_run_ledger.adb': '95880816a92fd4a435d9749392676e312a800f9d63d912649e0cdbb3baaff9a9', 'core/resource_run_ledger.ads': '4f2324ec6464f533cea438860725075e340b192645f14c2d1424c0d135b8fe3e', 'core/resource_run_ledger_c_api.adb': 'f23aebc393245e5ce85edeb387297536a66ca74a6ca727a032662f3c084f4547', 'core/resource_run_ledger_c_api.ads': 'c492e646c056e6931151725be3e0092ec1bb9195a32f51a8fa675722c1815cbf', 'core/resource_run_ledger_wire.adb': '9dfbf2149d066c31e5a2e8271c1cbb1246c9c1ad6eadb038bb3377e9bda11088', 'core/resource_run_ledger_wire.ads': 'b09d4e07df8652f8f87b2a6526f0fa26875253ea1dc8909bbec6b330d6d02eed', 'core/worldline-ancestry.ads': '718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db', 'core/worldline-c_api.adb': '4c0564d7870ab50b44eec707140d4402166811190d1b88307265134b2d0273fa', 'core/worldline-c_api.ads': '4c533f63b629146beea81b20c7bddcae385beafb61ffc62cc866212f6d5c4c6b', 'core/worldline-causal_graph.adb': 'a7e80ad0b061be82ce2727e5aeabd6fa27335807d66445ad01dc3fb3931dfab5', 'core/worldline-causal_graph.ads': '1f5271eed9dc2bdacf2642a9647bab7a2b29a707c7749664ba09f7fac79ce14f', 'core/worldline-chain_authority.adb': '4c7052b3835615308d6332303d9e9ccc2bab7b741a6c7a8457c7f98a8a4b8881', 'core/worldline-chain_authority.ads': 'b96d3635c43ec01db68f07140f0343a620214b1672c3be6114cbc40a593e44ae', 'core/worldline-chain_authority_c_api.adb': 'f2ef756386993a1283198b489f23ad371cd05c0cf13b9a78deade84793c2b919', 'core/worldline-chain_authority_c_api.ads': 'a90a458e11cd824506bd350de0bb84001e62b7982960459a3c7c30723276b99a', 'core/worldline-chain_authority_wire.adb': '9ff2355dbebbf8192b78e21adb225bb8405968612a1c8cc6e6778f27c42961e4', 'core/worldline-chain_authority_wire.ads': '7baf22c73d65bb6ba5dbe5386453da06a8b600f8a81e58931bf9c6377bada4f1', 'core/worldline-collapse.ads': '94ef49a258a46363eea81d44e168ce4e7cc618fdf128e916e92e447f2ffe32e2', 'core/worldline-collapse_wire.ads': '48270be156ee3f1c7d7f6215917c9b8026ac5346c45064cf7803950c137ddd76', 'core/worldline-evaluation.ads': '06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e', 'core/worldline-evaluation_authority.adb': 'd907b1d4eda41e7f7167695520085071686c834f8c1adb6691307661c3043d3a', 'core/worldline-evaluation_authority.ads': '1ee7d183c40c6b98b7f98277f96924e3135fedd83900134a3ff4461bcf237694', 'core/worldline-evaluation_report_facts.adb': 'ffdc1629f8eaef1ec4ab1bbc4fc988f2f1546dd8b5013ec4635888d77f8240fb', 'core/worldline-evaluation_report_facts.ads': 'f8bfee03303776b2825662bb1ce394fdf3c3e6acf3e7b1084500e50eba430f82', 'core/worldline-evaluation_report_wire.adb': '19ed101a83a9a9350a660cd7693a8be7ffee86557fa6d58e7959a0ae9973ff78', 'core/worldline-evaluation_report_wire.ads': 'a58347985c4242421c4114ecf61ddaf6f84229e62ab2114cd0947b7feee29b19', 'core/worldline-evaluation_v2.adb': '2fc57758a66ac2c7aa9ef6e108fdcbf93b1b286fd64b6620d8bca54ce32312eb', 'core/worldline-evaluation_v2.ads': '8e1f18244b924a7c9c05c67fdf785491a910c9f7c59966381b38962c2f68a72c', 'core/worldline-evaluation_wire.adb': '30696c9e2b4be84aad47d406864213a176f494e07dbed6f6907efe601d3be530', 'core/worldline-evaluation_wire.ads': '8b190a32f057a30a700e3331bd72aa2cfc18c5d6f3540b824756197f09077c7a', 'core/worldline-identities.ads': 'ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21', 'core/worldline-owner_conjunction.adb': '9d6f3f09c955a8612747f088a14802c5004a9a656009389e11254d6d623f3c32', 'core/worldline-owner_conjunction.ads': '62559ebaa5c94a88435d44333ac61aede278af67813f3ab7ac72d27bd86ec89d', 'core/worldline-owner_conjunction_wire.adb': '8aedcbc566fc59ca8a600a6410199ef8ec31b3fbffb655e856e679007f0fc7c7', 'core/worldline-owner_conjunction_wire.ads': 'a078f33e659fcb0c0eac74e63777425181bd5e2865566abfb79f36fc34aa510d', 'core/worldline-owner_retry_audit.adb': 'd444de903bc184300bbfd6e95348f4307827b7ad3948e4fe77c091daec52b5bd', 'core/worldline-owner_retry_audit.ads': 'f10e8a5758de157d40ab487c2b5071232cc8ede3b0984b36e75e922dff5b49e0', 'core/worldline-owner_retry_audit_wire.adb': 'a90756485c89699537c11c14b86fe5444c9ab7eb8fd3352ca4006f4610ab666f', 'core/worldline-owner_retry_audit_wire.ads': '60772578c6f02b53ea7b4d5614dde93f4e6d02e073847932c4647853d205f979', 'core/worldline-owner_subject_projection.adb': 'abcf67952cd84158f7a536c8315402ab6a7cb3a9f32ba13e7587ad1d0119df72', 'core/worldline-owner_subject_projection.ads': '2aa7d9d7208c340ae46ac36a4bf74d0dfe1ce2f53fdae435f95fcdc39479b7f7', 'core/worldline-owner_transitions.adb': '6e8735f539da94f023a7a9fd3ac76a1d6566c6d97e7cfe349205d1f285bbc387', 'core/worldline-owner_transitions.ads': '6a372ec0b94c9a5f6f29a3a652981c4d0532a0500feafe7d569cd668dc7a44e4', 'core/worldline-owner_transitions_wire.adb': '1fdad555d323af2a611072caa703d272bb074a61f481ba9677285eba13818d0b', 'core/worldline-owner_transitions_wire.ads': '8867a739ddc2b22c3d73c8908a0be7bb8ecd1410bbe9232776499aa57837f814', 'core/worldline-receipts.adb': '1ee34566208a835951d21d79be1bc6ffd287b3c61b43bad76210a7a546b156bb', 'core/worldline-receipts.ads': '45e8c276cf73d8d0311f247a1c87e9bf88614d46fde2bfe6c5f858ee2d20827b', 'core/worldline-recovery.adb': '75763d6eb35c647df523a728c6939e21cda6c3d7b44ba54fb2a4a917f3149e24', 'core/worldline-recovery.ads': '735d3411bd85c84f7e9f0449c34808f9c9ae226d82aac5e396448b4d27f4668a', 'core/worldline-recovery_authorization.adb': 'd90b75ec516fbf8ddb0f0bf40ee39297e70eebc001d4edad6b0142c7da092e7d', 'core/worldline-recovery_authorization.ads': '3b95bc25da8343b9d0c4cd6e133614bb59cdce65740142d9c2d2ed072e62dec6', 'core/worldline-recovery_authorization_c_api.adb': '0f3e1162efebf4b9d15197c5e224c4ebec3bd4f63a476b49a5a584c466c0e471', 'core/worldline-recovery_authorization_c_api.ads': 'afc10c9f738f0bba486ade982b7250327b31972f64c5a33b319f1662d2ff059e', 'core/worldline-recovery_authorization_v3.adb': '21536d8595e0d6d14764b56309eb2f88d28bd88fc47b6fe9c16f915c98ed63dd', 'core/worldline-recovery_authorization_v3.ads': '8b3f3c7477c461dadceba33ab421cf54d4c77129e2875768346d93c91f3fdd51', 'core/worldline-recovery_authorization_v3_c_api.adb': 'fa1d4aa2b0e138656314651f52312113dbdaa6bd3f491714115c234e8f2e5d39', 'core/worldline-recovery_authorization_v3_c_api.ads': '96b679271cea641ab5bcf84784fa08193d56b19b456a67d3d08007268d8ed2b5', 'core/worldline-recovery_authorization_v3_wire.adb': '5df8bd9bcd6842aaf033bde67edd121e6d9e0bdfd6f29158f0f8b1a57fd36bc6', 'core/worldline-recovery_authorization_v3_wire.ads': '30a49ffee1fecf33fe798e524cda06f73a8a2164ffe92c2bce8a10155a45f90e', 'core/worldline-recovery_authorization_wire.adb': 'e0c1054dd20e34bf1ddbcaefd9665c7588fc4683c8dad1a91351c89597928f62', 'core/worldline-recovery_authorization_wire.ads': 'a6b453f40b2eee2d860008ecb11b9720f6be2a5be5c1aca52a91f264c40d687c', 'core/worldline-recovery_protocol.adb': '1188891c1663c1c0c3ec47d304af9aaf5b14b1f9a74cff6ad771d47d06f5f573', 'core/worldline-recovery_protocol.ads': '7ca9a947061fce2a3278ab064ede1f8c2edad77fb3ecbdb68ef3f1cc41131eec', 'core/worldline-recovery_protocol_c_api.adb': '7caa6d15eda261907906643357d1444d4b912133865fc8503db5b8a1ee8223e2', 'core/worldline-recovery_protocol_c_api.ads': '3e03b5a62930533f5d930fa7e5f2117e1e8099239cf7a5d17651169c7d16b946', 'core/worldline-recovery_protocol_wire.adb': '4716e4c67604bc3ebb236994a30a1f98a2f2684e99fa8a3dde6c6529c2c49d2b', 'core/worldline-recovery_protocol_wire.ads': '389d2fd4ad5a625f1ac5274da214c9b8e953f261882b300fbbfa96d17b5c1cd4', 'core/worldline-resource_wire.adb': 'ec1ea00cf321f841aafcb874047c48d1ff28363d29ea042c6703a60a2be32f80', 'core/worldline-resource_wire.ads': 'b0af3ef936e727ba9113430ebc29c2843124f82e584b3bb294dc23af2667ad75', 'core/worldline-resources.adb': '0e65d26b226f8de7c665ff0effde568057f5fd135f7dafad85f110a697ea8e17', 'core/worldline-resources.ads': '3abbfe401429b72094c8e06be392ff3cb7612149f125d1249f4b8bf5792c978e', 'core/worldline-transitions.ads': '5b9c8f89900d01eeb40818de6392e1f23f8e2606cba702dd06e72e4257406c27', 'core/worldline-world.ads': '3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5', 'core/worldline.ads': '4e08ff1dedc1f28b526a19b37c343b2d71f5f1e35409abda2afdbd92a73ab866', 'core/worldline_core.gpr': '1c1ef87df90c161642b9995c850dfc2781453cf475c6efa4979dc4fd13a8eab7', 'core/worldline_core_sources.gpr': 'fc7be69ee1d21269d12f600a3dab22b53c21362d178280d5f8ddcacf5c09802c', 'evaluation-authority-tests/evaluation_authority_tests.gpr': 'f9ba8e8e3b9593454c25f74a5678599ebdf09afbf8510b119ebfa6f8820a98f4', 'evaluation-authority-tests/test_evaluation_authority.adb': '071e0f859f92ac1576f95dc1c6e6f89df84c59edb304b36c3e15f0a887e98730', 'evaluation-wire-tests/evaluation_wire_tests.gpr': '8fde6733c882c9be99a7fbcdce0c6ba0a8eca138a4b68e65ec77efdc84160d89', 'pending-component/core/evaluation_epoch.adb': '1958820a7247823c06a3295ab6fbd86bd1bff3ccd7cf6d7c71d94425e11d0259', 'pending-component/core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'pending-component/core/resource_quantities.adb': 'a527cfdeae1671b27a901e6adc7f80fc89966980acc80f2775d77b540a63ec47', 'pending-component/core/resource_quantities.ads': '21640498940fc92941624d97a6645bf14a3e1fa9bf3bc951c6f85e93d0d5f412', 'recovery-epoch-tests/recovery_epoch_tests.gpr': '600c9e1b3b3524f1419f2419a0e0925641a9dec1c822fb0b5ddb1e2afc9bc880', 'recovery-epoch-tests/test_epochs.adb': 'b134c380bb6990c55df7c21c590627585c57a8f0bbb99453a4d4c61913a68670', 'recovery-protocol-tests/recovery_protocol_tests.gpr': '2ab0cb616d8ff722655c92a6767e3c4bf8feb94707b5330f881601d8eb054d40', 'recovery-protocol-tests/test_protocol.adb': '04a6b065ae31533e8dcb04b4661aedb467bc0c89a5613bb4fcec01b7734c0447', 'tests/worldline_tests.gpr': 'd452b39691f23078635cb829b0ef94040342cefec9288cd4cccb821a51ca6a82', 'worldline.gpr': 'edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021'})

# Root isolated visible-operator source repair: original policy remains exact above.
CONTRACT_PINS.update({'core/resource_run_ledger_c_api.adb': '4048d0313716e2bed44bc4fe35e93e63cf39abf291c502322c52ab71ad6eaaa9', 'core/worldline-recovery_protocol_c_api.adb': 'db84f51488796b85cd2ff8565a355baa90f14399d8358daf41fb28c88f758590'})

# Prospective typed protocol value adapter; no foreign-memory/body boundary exemption.
REQUIRED_PROVED += ['Worldline.Recovery_Protocol_ABI.Apply']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/worldline-recovery_protocol_abi.ads', 'core/worldline-recovery_protocol_abi.adb'])
CONTRACT_PINS.update({'core/worldline-recovery_protocol_abi.ads': '7ca9a017eb112cde748227006cd5c6ffccda126cd7dd09fa7d4c36b1499ab62b', 'core/worldline-recovery_protocol_abi.adb': '362c5447a336cb8a1a87a81ce42e0c02deb8c2224bfe5330e4ca8e9a653c5247', 'protocol-adapter-tests/protocol_adapter_tests.gpr': '7e57d05ba13972588bc37cbe9b3b1a1d5c64b297a92e52349df6f08fcb5fbe47', 'protocol-adapter-tests/test_protocol_adapter.adb': '6055576865adf8a23c98ae8b7c9def207c8f253debbeb0d39548a94fdc310680', 'core/worldline-recovery_protocol_c_api.adb': '8c125a5179474ee15d1144f24a8cab91a3c1511c2f638f992852a778f22005cd', 'core/worldline_core.gpr': 'c71c25ef0c962026010ce1c81c51bd0be1d33853d471d1ab4919b16907c755e6'})

# GNAT16 pure functions retain implicit total termination; the illegal
# explicit function aspect is removed. Full body/variant proof is required.
CONTRACT_PINS.update({'core/worldline-chain_authority.ads': '68d27869ef933e66fde9e4008043ab00cd27fb2fe6dc9e92710b6dab94310272'})

# Full common-preimage reviewed source composition; all original obligations remain required.
REQUIRED_PROVED += ['Worldline.Chain_Authority.Prefix_Step', 'Worldline.Chain_Authority.Finish_Reference', 'Evaluation_Epoch.Nonnegative_Valid', 'Evaluation_Epoch.Scale_Column', 'Evaluation_Epoch.Column_Bounds', 'Evaluation_Epoch.Prefix_Step', 'Evaluation_Epoch.Prefix_Bounds', 'Evaluation_Epoch.Prefix_Padding', 'Evaluation_Epoch.Power_Factor', 'Evaluation_Epoch.Prefix_Tail', 'Evaluation_Epoch.Positive_Multiple', 'Evaluation_Epoch.Distinct_Columns', 'Evaluation_Epoch.Remainder_From_Witness', 'Evaluation_Epoch.Prefix_Modulus', 'Evaluation_Epoch.Magnitude_Modulus', 'Evaluation_Epoch.Unsigned_Value', 'Evaluation_Epoch.Carry_Input', 'Evaluation_Epoch.Column_Division', 'Evaluation_Epoch.Matching_Column', 'Evaluation_Epoch.Increment_Modulus', 'Evaluation_Epoch.Mismatching_Column', 'Evaluation_Epoch.Same_Value', 'Evaluation_Epoch.Is_Successor', 'Evaluation_Finalization.Seal_Classification_Equation', 'Evaluation_Finalization.Seal_Equation', 'Evaluation_Finalization.Values.Record_Start_Value', 'Evaluation_Finalization.Values.Record_Input_Value', 'Worldline.Resources.Sum_Prefix_Step', 'Worldline.Resources.Reserve_Prefix_Step', 'Worldline.Owner_Transitions.Query_Equation', 'Worldline.Owner_Transitions.Retry_Equation', 'Resource_Ledger.Total_Worker_Recurrence', 'Resource_Ledger.Ordered_Magnitude_Columns', 'Resource_Ledger.Written_Prefix_Step', 'Resource_Ledger.Quantity_Slot_Frame', 'Resource_Ledger.Checked_Detail_Step', 'Resource_Ledger.Retained_Detail_Frame', 'Evaluation_Completion.History_Update_Reference', 'Evaluation_Completion.History_Update_Check', 'Evaluation_Completion.Update_Composition_Equality', 'Resource_Reservation_Transition.Operation_Row_Reference', 'Resource_Reservation_Transition.Operation_Row_Status', 'Resource_Reservation_Transition.Final_Transition_Reference', 'Resource_Reservation_Transition.Final_Transition_Status', 'Resource_Reservation_Transition.Decision_Composition_Equality', 'Resource_Run_Ledger.Same_Run_Metadata', 'Resource_Run_Ledger.Changed_Row_Composition_Equality', 'Evaluation_Completion.Apply', 'Evaluation_Completion.Current_Matches_Head', 'Evaluation_Completion.Cursor_Matches', 'Evaluation_Completion.Decide', 'Evaluation_Completion.Find_Run', 'Evaluation_Completion.From_History', 'Evaluation_Completion.History_Binding_Matches', 'Evaluation_Completion.History_Index', 'Evaluation_Completion.History_Reference', 'Evaluation_Completion.History_Row_Conforms', 'Evaluation_Completion.Intent_Binding', 'Evaluation_Completion.Project', 'Evaluation_Completion.Project_Reference', 'Evaluation_Completion.Reference', 'Evaluation_Completion.Results_Reference', 'Evaluation_Completion.Results_Valid', 'Evaluation_Completion.Retained_Summary_Matches', 'Evaluation_Completion.Same_Binding', 'Evaluation_Completion.Same_Execution', 'Evaluation_Completion.Same_Requirement', 'Evaluation_Completion.Same_Result', 'Evaluation_Completion.Same_Results', 'Evaluation_Completion.Same_Results_Reference', 'Evaluation_Completion.Same_Terminal', 'Evaluation_Completion.Same_Verifier', 'Evaluation_Completion.Update_Reference', 'Evaluation_Completion.Valid_Binding', 'Evaluation_Completion.Valid_Cursor', 'Evaluation_Completion.Valid_Result', 'Evaluation_Completion.Valid_Terminal', 'Evaluation_Raw_Roster.Captured_Failure', 'Evaluation_Raw_Roster.Evaluation_Completed', 'Evaluation_Raw_Roster.Failure_For_Check_Reference', 'Evaluation_Raw_Roster.Genuine_Required_Failure', 'Evaluation_Raw_Roster.Matches_Classification', 'Evaluation_Raw_Roster.Promotion_Roster', 'Evaluation_Raw_Roster.Reference', 'Evaluation_Raw_Roster.Required_Evidence', 'Evaluation_Raw_Roster.Row_Bound', 'Evaluation_Raw_Roster.Same_Current_Requirement', 'Evaluation_Raw_Roster.Valid_Checks', 'Evaluation_Raw_Roster.Valid_Rows', 'Evaluation_History.Cursor_Matches', 'Evaluation_History.Epoch_One', 'Evaluation_History.Epoch_Quantity', 'Evaluation_History.Epoch_Valid', 'Evaluation_History.Epoch_Zero', 'Evaluation_History.Failure_Reference_Conforms', 'Evaluation_History.Finalization_Valid', 'Evaluation_History.Find_Completed_Failure', 'Evaluation_History.Head_Decision', 'Evaluation_History.Head_Record', 'Evaluation_History.Head_Reference', 'Evaluation_History.History_Valid', 'Evaluation_History.Is_Current_Failure', 'Evaluation_History.Next_Epoch', 'Evaluation_History.Query_Complete', 'Evaluation_History.Query_Valid', 'Evaluation_History.Result_Conforms', 'Evaluation_History.Row_Valid', 'Evaluation_History.Same_Epoch', 'Evaluation_History.Same_Identity', 'Evaluation_History.Select_Evidence', 'Evaluation_History.Span_Valid', 'Resource_Reservation_Transition.Unique_Negative_Bound', 'Resource_Reservation_Transition.Unique_Positive_Bound', 'Resource_Reservation_Transition.Factor_Negative_Bound', 'Resource_Reservation_Transition.Factor_Positive_Bound']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/evaluation_finalization-values.adb', 'core/evaluation_finalization-values.ads'])
CONTRACT_PINS.update({'core/canonical_artifacts.ads': '303ac80cabec2e2ef34029f6f8bd27c4100592cc9b8791b79f9a7475b9a0fa11', 'core/canonical_artifacts.adb': '2b6ce26d3f6643e89ffdfb26c9289ba093f0e812bd57610a09045617bd5e092e', 'artifact-tests/canonical_artifact_tests.gpr': 'bce2824cc8181edb5f1e9d5b9c0a391d70d68302b9f717ae44f87a0cd4a1ea05', 'artifact-tests/test_canonical_artifacts.adb': '43137b6f14b3c71b87de8f09c957e95d29a7d44dab5c67fc92698be12c50b8f1', 'core/evaluation_finalization.ads': '19ef348296b7d170dd238be6f7299beee07e5c4903209ec9d720e6856a573639', 'core/evaluation_finalization.adb': '1bd5ca259cbd1426f94157c7cd4964b69549c4bb992d1d4e3a9206134b146fd5', 'core/evaluation_finalization_c.ads': '8080094b47ce399c6a76c990e7112a4504faf81731066d26439d56bd2f447ec6', 'core/evaluation_finalization_c.adb': '8701200ec9bc0e8fb8e1c1cb78137fbcd23e0bc04b3025bdec6a7d92da290f01', 'core/evaluation_completion.ads': 'e1caaf4b7523a4b1ee7f7fd86e7cc41039830cf65e57fe9c999c5c5035fbe252', 'core/evaluation_completion.adb': '2a7d3cc5e4154b1e98602cd3d3e47f32aad7c03f0ad4895e6fc3a68a5fa35808', 'core/evaluation_completion_roster.ads': '5af5ec8259073ad74444b5a4596b2a4b05e568c7d26739b9210e9b4616a2a2a3', 'core/evaluation_completion_roster.adb': 'f52e2b9d4a909b3c2b616e92aaf7b87ce4ddb8a6e8b34ea99068915dc9bb253a', 'core/evaluation_pending_v2.ads': '1e20de75c125ff20b5ad5750466430e959fb104b27f905403e38a35eb01f8321', 'core/evaluation_pending_v2.adb': 'd8864beff6356c688f3ed26c84d27e6d0e315c423e150ee257e45df71bad3a66', 'evaluation-authority-tests/test_evaluation_authority.adb': '071e0f859f92ac1576f95dc1c6e6f89df84c59edb304b36c3e15f0a887e98730', 'evaluation-authority-tests/evaluation_authority_tests.gpr': 'f9ba8e8e3b9593454c25f74a5678599ebdf09afbf8510b119ebfa6f8820a98f4', 'core/worldline-evaluation_authority.ads': '1ee7d183c40c6b98b7f98277f96924e3135fedd83900134a3ff4461bcf237694', 'core/worldline-evaluation_authority.adb': 'd907b1d4eda41e7f7167695520085071686c834f8c1adb6691307661c3043d3a', 'core/evaluation_completion_c.ads': 'd3f7dd59480c257d5e488801a98f46de5435967c0c468a52db5b61d3cf360ee0', 'core/evaluation_completion_c.adb': '33e4763cf15e91c699627371a257e7dee58dd1de1875e38e300ba6310c8f57a3', 'core/resource_ledger.ads': 'ddf46ac440a9c372f7c4b30d1d91463061a45be05653fee181f25164bdd2f0f1', 'core/resource_ledger.adb': '2fcdaddc7c3f087a2e9e328d7f6f27d64fda537c84e25f442fe2495c8fb1c620', 'core/resource_reservation_transition.adb': 'cc875b343d5f1a5ca9f1b97a7ed45f7b5e4aea04c514d8d7a780ca400a832acf', 'core/resource_quantities.ads': 'ab8c65271ab244786aad52e4cb8243be0d481f8067e1b8a2cdaa7bce162c8e63', 'core/resource_quantities.adb': 'a527cfdeae1671b27a901e6adc7f80fc89966980acc80f2775d77b540a63ec47', 'pending-component/core/resource_quantities.ads': '21640498940fc92941624d97a6645bf14a3e1fa9bf3bc951c6f85e93d0d5f412', 'pending-component/core/resource_quantities.adb': '93a42adfed8b5f2311f33818e3d33c5e1a21c089b7930d26d7a3b9bdb53169b4', 'core/evaluation_history.ads': 'e58eea740afa7f385a386ad97ad78380eb61ccac35d7669f14768dd4ac30cc3a', 'core/evaluation_history.adb': '74a24e09ac21e8900167db0f25b43cfd33d000eb52922653133a8e631a911c3f', 'core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'core/evaluation_epoch.adb': '70e53cd579be574d89aba973d9a916bd00271dbd4784865ed540c0369b032e2c', 'pending-component/core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'pending-component/core/evaluation_epoch.adb': '70e53cd579be574d89aba973d9a916bd00271dbd4784865ed540c0369b032e2c', 'core/worldline-resources.ads': '3abbfe401429b72094c8e06be392ff3cb7612149f125d1249f4b8bf5792c978e', 'core/worldline-resources.adb': '782d50baa7a319894daf629f0d1c42ad51d7c374e88f0fbc3515812ab0a67ea4', 'core/worldline-evaluation_v2.ads': '8e1f18244b924a7c9c05c67fdf785491a910c9f7c59966381b38962c2f68a72c', 'core/worldline-evaluation_v2.adb': '2fc57758a66ac2c7aa9ef6e108fdcbf93b1b286fd64b6620d8bca54ce32312eb', 'core/worldline-evaluation_wire.ads': '8b190a32f057a30a700e3331bd72aa2cfc18c5d6f3540b824756197f09077c7a', 'core/worldline-evaluation_wire.adb': '30696c9e2b4be84aad47d406864213a176f494e07dbed6f6907efe601d3be530', 'core/evaluation_raw_roster.ads': '6bdb761e4be7a6dec36373293ffb7de064ddaa250a811ce9ebb6dcf2db69788b', 'core/evaluation_raw_roster.adb': '807532e6fb340903d4342a384d8c4c7ca22df7f0da42382134c1731e4af386cd', 'core/worldline-evaluation_report_facts.ads': 'f8bfee03303776b2825662bb1ce394fdf3c3e6acf3e7b1084500e50eba430f82', 'core/worldline-evaluation_report_facts.adb': 'ffdc1629f8eaef1ec4ab1bbc4fc988f2f1546dd8b5013ec4635888d77f8240fb', 'core/worldline-evaluation_report_wire.ads': 'a58347985c4242421c4114ecf61ddaf6f84229e62ab2114cd0947b7feee29b19', 'core/worldline-evaluation_report_wire.adb': '19ed101a83a9a9350a660cd7693a8be7ffee86557fa6d58e7959a0ae9973ff78', 'evaluation-wire-tests/evaluation_wire_tests.gpr': '8fde6733c882c9be99a7fbcdce0c6ba0a8eca138a4b68e65ec77efdc84160d89', 'worldline.gpr': 'edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021', 'core/worldline_core.gpr': '702cc20adf361a486634004088771fa7cd515a9c24b746ae51ef8973b01f94d1', 'core/worldline_core_sources.gpr': 'fc7be69ee1d21269d12f600a3dab22b53c21362d178280d5f8ddcacf5c09802c', 'core/attest_sha256.gpr': '5d75d10379e9397a9e08517d56728b2f53479fd7c0e9dff3b5dccaa8e8c0f9ee', 'tests/worldline_tests.gpr': 'd452b39691f23078635cb829b0ef94040342cefec9288cd4cccb821a51ca6a82', 'core/worldline.ads': '4e08ff1dedc1f28b526a19b37c343b2d71f5f1e35409abda2afdbd92a73ab866', 'core/attest/attest.ads': 'bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587', 'core/attest/attest-sha256.ads': '1d38534d6bcaa9a6646225db8f26f0a7b940444cda3ed0d109816119d51bff05', 'core/worldline-c_api.ads': '4c533f63b629146beea81b20c7bddcae385beafb61ffc62cc866212f6d5c4c6b', 'core/worldline-collapse.ads': '94ef49a258a46363eea81d44e168ce4e7cc618fdf128e916e92e447f2ffe32e2', 'core/worldline-collapse_wire.ads': '48270be156ee3f1c7d7f6215917c9b8026ac5346c45064cf7803950c137ddd76', 'core/worldline-identities.ads': 'ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21', 'core/worldline-evaluation.ads': '06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e', 'core/worldline-transitions.ads': '5b9c8f89900d01eeb40818de6392e1f23f8e2606cba702dd06e72e4257406c27', 'core/worldline-c_api.adb': '4c0564d7870ab50b44eec707140d4402166811190d1b88307265134b2d0273fa', 'core/worldline-receipts.ads': '45e8c276cf73d8d0311f247a1c87e9bf88614d46fde2bfe6c5f858ee2d20827b', 'core/worldline-receipts.adb': '1ee34566208a835951d21d79be1bc6ffd287b3c61b43bad76210a7a546b156bb', 'core/worldline-causal_graph.ads': '1f5271eed9dc2bdacf2642a9647bab7a2b29a707c7749664ba09f7fac79ce14f', 'core/worldline-causal_graph.adb': 'a7e80ad0b061be82ce2727e5aeabd6fa27335807d66445ad01dc3fb3931dfab5', 'core/worldline-world.ads': '3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5', 'core/worldline-ancestry.ads': '718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db', 'core/resource_admission.adb': '0da682e7cd0aa85daea88a9f36926fa213240b9273cd7015108f95f4f48ee63c', 'core/resource_admission.ads': '2d93c087e980ec50ce77a21efdeb4c2d3a96e503493e55c0a9cbbb27e80381f2', 'core/resource_reservation_lifecycle.adb': '3cf6bbe8dfef85f485be16eb9185768ace28ddc6a3ea5bfe0cd0aa26dd8aef41', 'core/resource_reservation_lifecycle.ads': '8e3c85334abc8ff747e6f468bea29f04196c3c11cffa10a68207b96c8b3e0400', 'core/resource_reservation_transition.ads': 'c82a593982275ceed2574269328981d0d6915bd70f1f91fe7a19e954c266b4c9', 'core/worldline-recovery.adb': '75763d6eb35c647df523a728c6939e21cda6c3d7b44ba54fb2a4a917f3149e24', 'core/worldline-recovery.ads': '735d3411bd85c84f7e9f0449c34808f9c9ae226d82aac5e396448b4d27f4668a', 'core/worldline-recovery_authorization.adb': 'd90b75ec516fbf8ddb0f0bf40ee39297e70eebc001d4edad6b0142c7da092e7d', 'core/worldline-recovery_authorization.ads': '3b95bc25da8343b9d0c4cd6e133614bb59cdce65740142d9c2d2ed072e62dec6', 'core/worldline-recovery_authorization_c_api.adb': 'bf4819001b99778de6bfc17f4ab5543ee8107ee83f3e7b8bb1ea410f932e542d', 'core/worldline-recovery_authorization_c_api.ads': '0ee0ae55e1c0958bf0f385dbe738961bd35217f82dafffcc5524b5eed376fd01', 'core/worldline-recovery_authorization_wire.adb': 'e0c1054dd20e34bf1ddbcaefd9665c7588fc4683c8dad1a91351c89597928f62', 'core/worldline-recovery_authorization_wire.ads': 'a6b453f40b2eee2d860008ecb11b9720f6be2a5be5c1aca52a91f264c40d687c', 'core/worldline-resource_wire.adb': 'ec1ea00cf321f841aafcb874047c48d1ff28363d29ea042c6703a60a2be32f80', 'core/worldline-resource_wire.ads': 'b0af3ef936e727ba9113430ebc29c2843124f82e584b3bb294dc23af2667ad75', 'core/worldline-recovery_authorization_v3.adb': '21536d8595e0d6d14764b56309eb2f88d28bd88fc47b6fe9c16f915c98ed63dd', 'core/worldline-recovery_authorization_v3.ads': '8b3f3c7477c461dadceba33ab421cf54d4c77129e2875768346d93c91f3fdd51', 'core/worldline-recovery_authorization_v3_c_api.adb': 'ba72af17a278f31ad28b4673cbf6209a85e7cf698c9393f8c4622073fee7f7e5', 'core/worldline-recovery_authorization_v3_c_api.ads': '2353d8de714b2a052d272ca41fc5abf6e95b41471793b573507b38476e37bce0', 'core/worldline-recovery_authorization_v3_wire.adb': '5df8bd9bcd6842aaf033bde67edd121e6d9e0bdfd6f29158f0f8b1a57fd36bc6', 'core/worldline-recovery_authorization_v3_wire.ads': '30a49ffee1fecf33fe798e524cda06f73a8a2164ffe92c2bce8a10155a45f90e', 'recovery-epoch-tests/recovery_epoch_tests.gpr': '600c9e1b3b3524f1419f2419a0e0925641a9dec1c822fb0b5ddb1e2afc9bc880', 'recovery-epoch-tests/test_epochs.adb': 'b134c380bb6990c55df7c21c590627585c57a8f0bbb99453a4d4c61913a68670', 'core/worldline-recovery_protocol.adb': '1188891c1663c1c0c3ec47d304af9aaf5b14b1f9a74cff6ad771d47d06f5f573', 'core/worldline-recovery_protocol.ads': '7ca9a947061fce2a3278ab064ede1f8c2edad77fb3ecbdb68ef3f1cc41131eec', 'core/worldline-recovery_protocol_c_api.adb': '66481b8aa19d26eeffe28230b6557ce181dad9183386c81a88b88729567fcdd0', 'core/worldline-recovery_protocol_c_api.ads': '89720f0d302e8d707c51cf5d292dc4e51a5c64cf3f3280260a574d2442af79ea', 'core/worldline-recovery_protocol_wire.adb': '4716e4c67604bc3ebb236994a30a1f98a2f2684e99fa8a3dde6c6529c2c49d2b', 'core/worldline-recovery_protocol_wire.ads': '389d2fd4ad5a625f1ac5274da214c9b8e953f261882b300fbbfa96d17b5c1cd4', 'recovery-protocol-tests/test_protocol.adb': '04a6b065ae31533e8dcb04b4661aedb467bc0c89a5613bb4fcec01b7734c0447', 'recovery-protocol-tests/recovery_protocol_tests.gpr': '2ab0cb616d8ff722655c92a6767e3c4bf8feb94707b5330f881601d8eb054d40', 'core/worldline-chain_authority.adb': '4c7052b3835615308d6332303d9e9ccc2bab7b741a6c7a8457c7f98a8a4b8881', 'core/worldline-chain_authority.ads': '5a37eeb3d50c9541b522b467d7d2511138c0436b2a22a5eb0635849f77c92cf4', 'core/worldline-chain_authority_c_api.adb': '12182bc025f1312fdaa96c7354d08a2364fff4809454f5c702e1d4143c4d9e0e', 'core/worldline-chain_authority_c_api.ads': 'c2f4ab1103fb9aab92b7809bb6914e698a387c1f5850a3b3771f785d9c56e115', 'core/worldline-chain_authority_wire.adb': '9ff2355dbebbf8192b78e21adb225bb8405968612a1c8cc6e6778f27c42961e4', 'core/worldline-chain_authority_wire.ads': '7baf22c73d65bb6ba5dbe5386453da06a8b600f8a81e58931bf9c6377bada4f1', 'core/worldline-owner_transitions.adb': 'b3049b6773bed28e252c1faaa6926e6e71c3ca51a40701ad2293aa0474d8556f', 'core/worldline-owner_transitions.ads': '0d7692119a7eb400f06d1bc8b3792f9f6925f58096d23b059d8f6ea5a49000b3', 'core/worldline-owner_transitions_wire.adb': 'dcb872cec43e33aec9773ab1e95757d487dee0da9b7eb50a1f9c0a1dffe55afd', 'core/worldline-owner_transitions_wire.ads': '8867a739ddc2b22c3d73c8908a0be7bb8ecd1410bbe9232776499aa57837f814', 'core/resource_run_ledger.adb': 'eab01a895796c7e679d9241668b1d18bc768cf021fb48aed6d7fba982b042152', 'core/resource_run_ledger.ads': '77eaebdce9f0ed74f7478518a6ce1e9635fb1071e1409c17d5e7f2b5ac830648', 'core/resource_run_ledger_c_api.adb': '414cd21f48edb89e878b8efd44c77fdbe9e37b689275e5b8414f65ef83218ba1', 'core/resource_run_ledger_c_api.ads': '4c4f966a69168902bda7ed222790ca046ffd7fd7694869bebe65079bd6ff49e2', 'core/resource_run_ledger_wire.adb': 'bea60305b4242bcf72caaaa7eb1e2ded6837e72755006d9410dfb218c0b11c2c', 'core/resource_run_ledger_wire.ads': 'b09d4e07df8652f8f87b2a6526f0fa26875253ea1dc8909bbec6b330d6d02eed', 'core/worldline-owner_retry_audit.ads': 'f10e8a5758de157d40ab487c2b5071232cc8ede3b0984b36e75e922dff5b49e0', 'core/worldline-owner_retry_audit.adb': 'd444de903bc184300bbfd6e95348f4307827b7ad3948e4fe77c091daec52b5bd', 'core/worldline-owner_retry_audit_wire.ads': '60772578c6f02b53ea7b4d5614dde93f4e6d02e073847932c4647853d205f979', 'core/worldline-owner_retry_audit_wire.adb': 'a90756485c89699537c11c14b86fe5444c9ab7eb8fd3352ca4006f4610ab666f', 'core/worldline-owner_conjunction.ads': '62559ebaa5c94a88435d44333ac61aede278af67813f3ab7ac72d27bd86ec89d', 'core/worldline-owner_conjunction.adb': '9d6f3f09c955a8612747f088a14802c5004a9a656009389e11254d6d623f3c32', 'core/worldline-owner_conjunction_wire.ads': 'a078f33e659fcb0c0eac74e63777425181bd5e2865566abfb79f36fc34aa510d', 'core/worldline-owner_conjunction_wire.adb': '8aedcbc566fc59ca8a600a6410199ef8ec31b3fbffb655e856e679007f0fc7c7', 'core/worldline-owner_subject_projection.ads': '2aa7d9d7208c340ae46ac36a4bf74d0dfe1ce2f53fdae435f95fcdc39479b7f7', 'core/worldline-owner_subject_projection.adb': 'abcf67952cd84158f7a536c8315402ab6a7cb3a9f32ba13e7587ad1d0119df72', 'core/worldline-recovery_protocol_abi.ads': '7ca9a017eb112cde748227006cd5c6ffccda126cd7dd09fa7d4c36b1499ab62b', 'core/worldline-recovery_protocol_abi.adb': '362c5447a336cb8a1a87a81ce42e0c02deb8c2224bfe5330e4ca8e9a653c5247', 'protocol-adapter-tests/protocol_adapter_tests.gpr': '7e57d05ba13972588bc37cbe9b3b1a1d5c64b297a92e52349df6f08fcb5fbe47', 'protocol-adapter-tests/test_protocol_adapter.adb': '6055576865adf8a23c98ae8b7c9def207c8f253debbeb0d39548a94fdc310680', 'epoch-correspondence-tests/epoch_correspondence_core_tests.gpr': '5216f9a5a0d7f9430e4f8fe400181a6d111179bff4520d981ae3c37d18f2bc4e', 'epoch-correspondence-tests/epoch_correspondence_pending_tests.gpr': '1af95a0f4a5851f4aac0775bd8d2493fa26224639d312f097db87fb88da8ba28', 'epoch-correspondence-tests/test_epoch_correspondence.adb': 'a297bb45d5c87dd010997741f10beb7598310dd7662a255e50ad51160dd88c1a', 'core/evaluation_finalization-values.adb': 'c6dd5ea011677b3a8ae31f9d5b2ccddd51fc5549ed5f07eef27add39a3ead320', 'core/evaluation_finalization-values.ads': 'f3fe2b54ad04f1a43c5fdd181fc149fffc3441f2b744b9da6da6ef8bab8d13ce', 'finalization-value-controls/finalization_value_controls.gpr': '756918630a4b54abaff8e68e4ae84aac7a7de2b670ebea00bb86b0a6edc6e421', 'finalization-value-controls/test_finalization_parent_values.adb': '9e87197fa326dc73f582f05cc473beff73d0b08c82da4dee29951827e358de28', 'finalization-value-controls/test_finalization_projection.adb': '669b4aa0804d272585ab5fa3569a7db4435e14ea0d7224165ee8470370ebdefd', 'finalization-value-controls/test_finalization_values.adb': '3242b812f6c19ea65f5d523c6155964e6e41b7b06976718f6391761db7106b6d', 'resources-prefix-correspondence-tests/resources_prefix_correspondence_tests.gpr': 'd238363ed2e518627c36a4afe965398ac4cef15b4264f7b3d50f25b771460978', 'resources-prefix-correspondence-tests/test_resources_prefix_correspondence.adb': '19a94f3caffa77dfa2ffd705db5c1b9cd842b43fb53b7023227a3c4718cf3725', 'wire-initialization-tests/test_wire_initialization.adb': 'e779f4827c714b6329addd074cdefee94737bbada08f81a82875a6a4daba000c', 'wire-initialization-tests/wire_initialization_tests.gpr': 'bfe67074a1b0fa4193667beae58279c4746b50f8a05a6c0184354dcbe7570224', 'resource-ledger-correspondence-tests/resource_ledger_correspondence_tests.gpr': 'd1f489d22d3508c17e9c529836ec22db29d339db94f5ed70a6a0b3c365883ec8', 'resource-ledger-correspondence-tests/test_resource_ledger_correspondence.adb': 'b90bec45288928ed08de52b0103f16243c221bf05887cdd0eb4a0d75c498fa3f', 'decision-correspondence-tests/decision_correspondence_tests.gpr': '52637b39b04f201af2c2088f748a3ab7c1b032e813457638b12f1d6c18661016', 'decision-correspondence-tests/test_completion_correspondence.adb': '6ad18e9ec3136d2bf14ca45cb711801fc125ac6e307598ce0c7e0b5c6e36e945', 'decision-correspondence-tests/test_history_correspondence.adb': 'd293c070a38372238ac0c546deb2b8cab3df6f83ba21428f720ebccb6ed597cf', 'decision-correspondence-tests/test_raw_roster_correspondence.adb': 'ba17660670e42559e2b38af0d71f1c08c7126fbc527096bfb988e1aa2a59956b', 'decision-correspondence-tests/test_run_metadata_correspondence.adb': '93b4b7b7f610aaf0c844738886c347589769363e94f26d77edd4ccf4bedecad9', 'decision-correspondence-tests/test_transition_correspondence.adb': 'ac2b451ac7e78e52fcf4ee89d164fdb006f5326748517aa3b52cd99a00fb9fb1', 'core/evaluation_pending_c.ads': '9a829c27690ccecd8bf06a77357aaa0f0997b5c247848e7a9ca3697347f91f47', 'core/evaluation_pending_c.adb': '4fca4bd24b1edb06a3cfb1e2c87c3dedcfc97cdbe54a264044f8116da0cf19d0', 'core/evaluation_pending_v2_c.ads': '6044a6ef02b3b91d1064f2202a0370c34afbaff174570df26aca69f5e350653c', 'core/evaluation_pending_v2_c.adb': '54d2ea7a0a5e0bd99bc0b74fff2da73b2e233b0e451c9d5dfe3fed373de15d41', 'core/spark-big_integers.ads': 'f96017313a6e785d5c4697d95e610ced1a3612d20b7310dddb5af230226dbf1a', 'core/worldline-evaluation_history_c_api.ads': '3f2c70e3fc6f86cb5879e4b75b2e62c83eafe68f480e530c30d8b8612e194995', 'core/worldline-evaluation_history_c_api.adb': '3e5a4ceba275452894625d63364cd3d2c8abee223850808ef28000e5681f8f8d', 'core/worldline-recovery_c_api.ads': 'b0543c4f0fbc16e5247a2fb2528c419702676f1b1a8dbb1fe52708355e619f09', 'core/worldline-recovery_c_api.adb': '76d9095196c575d754b7cfb8c8ee31e631a8c0454d3455ea88edf99645c2864f', 'core/worldline-reservation_lifecycle_c_api.ads': '877551b73cb48992858a63d21961ffb9a7ab7cd7ad80312c1555c4d1cd55928f', 'core/worldline-reservation_lifecycle_c_api.adb': '2a37628e389855c7ad24cb2423d1cfdb716e63fc683108f019cec12225702598', 'core/worldline-resource_ledger_c_api.ads': '6ae817dda2eff2f1c9ef1e68fb43926b13ec4fdf954fb74a5948c0234e45c0aa', 'core/worldline-resource_ledger_c_api.adb': 'b78d12f34a0803a9b1e9a6d6617529c7bacaabc98944055b661583a4d6fddf7c', 'core/worldline-resource_policy_c_api.ads': 'e76d6da8722bd145d3c58093e578cf821c9a3d593e6fe94628315d45e5e775ff', 'core/worldline-resource_policy_c_api.adb': 'e7fb372df8cd92f7af6925b68678867ce4c24c94a83c35a0f64cc05a66fb57fd', 'core/worldline-resources_c_api.ads': '81210bc3272c53b7210e76033f19d96d2a066dedef17f7c9c6726fcf7f1e31d7', 'core/worldline-resources_c_api.adb': '5216ff373877ffbb60d71be980f666c23c74f06f99d383dd89ffca37e8dc7bcd'})

# Finite installed-eligibility source repair; no proof or native-cost credit.
CONTRACT_PINS.update({'core/resource_quantities.ads': '21640498940fc92941624d97a6645bf14a3e1fa9bf3bc951c6f85e93d0d5f412', 'core/evaluation_finalization_c.adb': 'ccb7a2fed1ff3de44a29ec427606837064c6eb8d51e93856ad89310927459cb2'})

# SHA256 source-only warning repair; all original proof obligations remain.
CONTRACT_PINS.update({'core/attest/attest-sha256.adb': '7ef39ea3e0627f562a3db75f3f392337869f96aa17ed5bf76015410b95306e9f'})

# Whole common V4 composition normalized pins; every original obligation remains OPEN.
CONTRACT_PINS.update({'core/canonical_artifacts.ads': '303ac80cabec2e2ef34029f6f8bd27c4100592cc9b8791b79f9a7475b9a0fa11', 'core/canonical_artifacts.adb': '2b6ce26d3f6643e89ffdfb26c9289ba093f0e812bd57610a09045617bd5e092e', 'artifact-tests/canonical_artifact_tests.gpr': 'bce2824cc8181edb5f1e9d5b9c0a391d70d68302b9f717ae44f87a0cd4a1ea05', 'artifact-tests/test_canonical_artifacts.adb': '43137b6f14b3c71b87de8f09c957e95d29a7d44dab5c67fc92698be12c50b8f1', 'core/evaluation_finalization.ads': '19ef348296b7d170dd238be6f7299beee07e5c4903209ec9d720e6856a573639', 'core/evaluation_finalization.adb': '1bd5ca259cbd1426f94157c7cd4964b69549c4bb992d1d4e3a9206134b146fd5', 'core/evaluation_finalization_c.ads': '8080094b47ce399c6a76c990e7112a4504faf81731066d26439d56bd2f447ec6', 'core/evaluation_finalization_c.adb': 'ccb7a2fed1ff3de44a29ec427606837064c6eb8d51e93856ad89310927459cb2', 'core/evaluation_completion.ads': 'e1caaf4b7523a4b1ee7f7fd86e7cc41039830cf65e57fe9c999c5c5035fbe252', 'core/evaluation_completion.adb': '2a7d3cc5e4154b1e98602cd3d3e47f32aad7c03f0ad4895e6fc3a68a5fa35808', 'core/evaluation_completion_roster.ads': '5af5ec8259073ad74444b5a4596b2a4b05e568c7d26739b9210e9b4616a2a2a3', 'core/evaluation_completion_roster.adb': 'f52e2b9d4a909b3c2b616e92aaf7b87ce4ddb8a6e8b34ea99068915dc9bb253a', 'core/evaluation_pending_v2.ads': '1e20de75c125ff20b5ad5750466430e959fb104b27f905403e38a35eb01f8321', 'core/evaluation_pending_v2.adb': 'd8864beff6356c688f3ed26c84d27e6d0e315c423e150ee257e45df71bad3a66', 'evaluation-authority-tests/test_evaluation_authority.adb': '071e0f859f92ac1576f95dc1c6e6f89df84c59edb304b36c3e15f0a887e98730', 'evaluation-authority-tests/evaluation_authority_tests.gpr': 'f9ba8e8e3b9593454c25f74a5678599ebdf09afbf8510b119ebfa6f8820a98f4', 'core/worldline-evaluation_authority.ads': '1ee7d183c40c6b98b7f98277f96924e3135fedd83900134a3ff4461bcf237694', 'core/worldline-evaluation_authority.adb': 'd907b1d4eda41e7f7167695520085071686c834f8c1adb6691307661c3043d3a', 'core/evaluation_completion_c.ads': 'd3f7dd59480c257d5e488801a98f46de5435967c0c468a52db5b61d3cf360ee0', 'core/evaluation_completion_c.adb': '33e4763cf15e91c699627371a257e7dee58dd1de1875e38e300ba6310c8f57a3', 'core/resource_ledger.ads': 'ddf46ac440a9c372f7c4b30d1d91463061a45be05653fee181f25164bdd2f0f1', 'core/resource_ledger.adb': '2fcdaddc7c3f087a2e9e328d7f6f27d64fda537c84e25f442fe2495c8fb1c620', 'core/resource_reservation_transition.adb': 'cc875b343d5f1a5ca9f1b97a7ed45f7b5e4aea04c514d8d7a780ca400a832acf', 'core/resource_quantities.ads': '21640498940fc92941624d97a6645bf14a3e1fa9bf3bc951c6f85e93d0d5f412', 'core/resource_quantities.adb': 'a527cfdeae1671b27a901e6adc7f80fc89966980acc80f2775d77b540a63ec47', 'pending-component/core/resource_quantities.ads': '21640498940fc92941624d97a6645bf14a3e1fa9bf3bc951c6f85e93d0d5f412', 'pending-component/core/resource_quantities.adb': '93a42adfed8b5f2311f33818e3d33c5e1a21c089b7930d26d7a3b9bdb53169b4', 'core/evaluation_history.ads': 'e58eea740afa7f385a386ad97ad78380eb61ccac35d7669f14768dd4ac30cc3a', 'core/evaluation_history.adb': '74a24e09ac21e8900167db0f25b43cfd33d000eb52922653133a8e631a911c3f', 'core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'core/evaluation_epoch.adb': '70e53cd579be574d89aba973d9a916bd00271dbd4784865ed540c0369b032e2c', 'pending-component/core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'pending-component/core/evaluation_epoch.adb': '70e53cd579be574d89aba973d9a916bd00271dbd4784865ed540c0369b032e2c', 'core/worldline-resources.ads': '3abbfe401429b72094c8e06be392ff3cb7612149f125d1249f4b8bf5792c978e', 'core/worldline-resources.adb': '782d50baa7a319894daf629f0d1c42ad51d7c374e88f0fbc3515812ab0a67ea4', 'core/worldline-evaluation_v2.ads': '8e1f18244b924a7c9c05c67fdf785491a910c9f7c59966381b38962c2f68a72c', 'core/worldline-evaluation_v2.adb': '2fc57758a66ac2c7aa9ef6e108fdcbf93b1b286fd64b6620d8bca54ce32312eb', 'core/worldline-evaluation_wire.ads': '8b190a32f057a30a700e3331bd72aa2cfc18c5d6f3540b824756197f09077c7a', 'core/worldline-evaluation_wire.adb': '30696c9e2b4be84aad47d406864213a176f494e07dbed6f6907efe601d3be530', 'core/evaluation_raw_roster.ads': '6bdb761e4be7a6dec36373293ffb7de064ddaa250a811ce9ebb6dcf2db69788b', 'core/evaluation_raw_roster.adb': '807532e6fb340903d4342a384d8c4c7ca22df7f0da42382134c1731e4af386cd', 'core/worldline-evaluation_report_facts.ads': 'f8bfee03303776b2825662bb1ce394fdf3c3e6acf3e7b1084500e50eba430f82', 'core/worldline-evaluation_report_facts.adb': 'ffdc1629f8eaef1ec4ab1bbc4fc988f2f1546dd8b5013ec4635888d77f8240fb', 'core/worldline-evaluation_report_wire.ads': 'a58347985c4242421c4114ecf61ddaf6f84229e62ab2114cd0947b7feee29b19', 'core/worldline-evaluation_report_wire.adb': '19ed101a83a9a9350a660cd7693a8be7ffee86557fa6d58e7959a0ae9973ff78', 'evaluation-wire-tests/evaluation_wire_tests.gpr': '8fde6733c882c9be99a7fbcdce0c6ba0a8eca138a4b68e65ec77efdc84160d89', 'worldline.gpr': 'edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021', 'core/worldline_core.gpr': '702cc20adf361a486634004088771fa7cd515a9c24b746ae51ef8973b01f94d1', 'core/worldline_core_sources.gpr': 'fc7be69ee1d21269d12f600a3dab22b53c21362d178280d5f8ddcacf5c09802c', 'core/attest_sha256.gpr': '5d75d10379e9397a9e08517d56728b2f53479fd7c0e9dff3b5dccaa8e8c0f9ee', 'tests/worldline_tests.gpr': 'd452b39691f23078635cb829b0ef94040342cefec9288cd4cccb821a51ca6a82', 'core/worldline.ads': '4e08ff1dedc1f28b526a19b37c343b2d71f5f1e35409abda2afdbd92a73ab866', 'core/attest/attest.ads': 'bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587', 'core/attest/attest-sha256.ads': '1d38534d6bcaa9a6646225db8f26f0a7b940444cda3ed0d109816119d51bff05', 'core/worldline-c_api.ads': '4c533f63b629146beea81b20c7bddcae385beafb61ffc62cc866212f6d5c4c6b', 'core/worldline-collapse.ads': '94ef49a258a46363eea81d44e168ce4e7cc618fdf128e916e92e447f2ffe32e2', 'core/worldline-collapse_wire.ads': '48270be156ee3f1c7d7f6215917c9b8026ac5346c45064cf7803950c137ddd76', 'core/worldline-identities.ads': 'ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21', 'core/worldline-evaluation.ads': '06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e', 'core/worldline-transitions.ads': '5b9c8f89900d01eeb40818de6392e1f23f8e2606cba702dd06e72e4257406c27', 'core/worldline-c_api.adb': '4c0564d7870ab50b44eec707140d4402166811190d1b88307265134b2d0273fa', 'core/worldline-receipts.ads': '45e8c276cf73d8d0311f247a1c87e9bf88614d46fde2bfe6c5f858ee2d20827b', 'core/worldline-receipts.adb': '1ee34566208a835951d21d79be1bc6ffd287b3c61b43bad76210a7a546b156bb', 'core/worldline-causal_graph.ads': '1f5271eed9dc2bdacf2642a9647bab7a2b29a707c7749664ba09f7fac79ce14f', 'core/worldline-causal_graph.adb': 'a7e80ad0b061be82ce2727e5aeabd6fa27335807d66445ad01dc3fb3931dfab5', 'core/worldline-world.ads': '3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5', 'core/worldline-ancestry.ads': '718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db', 'core/resource_admission.adb': '0da682e7cd0aa85daea88a9f36926fa213240b9273cd7015108f95f4f48ee63c', 'core/resource_admission.ads': '2d93c087e980ec50ce77a21efdeb4c2d3a96e503493e55c0a9cbbb27e80381f2', 'core/resource_reservation_lifecycle.adb': '3cf6bbe8dfef85f485be16eb9185768ace28ddc6a3ea5bfe0cd0aa26dd8aef41', 'core/resource_reservation_lifecycle.ads': '8e3c85334abc8ff747e6f468bea29f04196c3c11cffa10a68207b96c8b3e0400', 'core/resource_reservation_transition.ads': 'c82a593982275ceed2574269328981d0d6915bd70f1f91fe7a19e954c266b4c9', 'core/worldline-recovery.adb': '75763d6eb35c647df523a728c6939e21cda6c3d7b44ba54fb2a4a917f3149e24', 'core/worldline-recovery.ads': '735d3411bd85c84f7e9f0449c34808f9c9ae226d82aac5e396448b4d27f4668a', 'core/worldline-recovery_authorization.adb': 'd90b75ec516fbf8ddb0f0bf40ee39297e70eebc001d4edad6b0142c7da092e7d', 'core/worldline-recovery_authorization.ads': '3b95bc25da8343b9d0c4cd6e133614bb59cdce65740142d9c2d2ed072e62dec6', 'core/worldline-recovery_authorization_c_api.adb': 'bf4819001b99778de6bfc17f4ab5543ee8107ee83f3e7b8bb1ea410f932e542d', 'core/worldline-recovery_authorization_c_api.ads': '0ee0ae55e1c0958bf0f385dbe738961bd35217f82dafffcc5524b5eed376fd01', 'core/worldline-recovery_authorization_wire.adb': 'e0c1054dd20e34bf1ddbcaefd9665c7588fc4683c8dad1a91351c89597928f62', 'core/worldline-recovery_authorization_wire.ads': 'a6b453f40b2eee2d860008ecb11b9720f6be2a5be5c1aca52a91f264c40d687c', 'core/worldline-resource_wire.adb': 'ec1ea00cf321f841aafcb874047c48d1ff28363d29ea042c6703a60a2be32f80', 'core/worldline-resource_wire.ads': 'b0af3ef936e727ba9113430ebc29c2843124f82e584b3bb294dc23af2667ad75', 'core/worldline-recovery_authorization_v3.adb': '21536d8595e0d6d14764b56309eb2f88d28bd88fc47b6fe9c16f915c98ed63dd', 'core/worldline-recovery_authorization_v3.ads': '8b3f3c7477c461dadceba33ab421cf54d4c77129e2875768346d93c91f3fdd51', 'core/worldline-recovery_authorization_v3_c_api.adb': 'ba72af17a278f31ad28b4673cbf6209a85e7cf698c9393f8c4622073fee7f7e5', 'core/worldline-recovery_authorization_v3_c_api.ads': '2353d8de714b2a052d272ca41fc5abf6e95b41471793b573507b38476e37bce0', 'core/worldline-recovery_authorization_v3_wire.adb': '5df8bd9bcd6842aaf033bde67edd121e6d9e0bdfd6f29158f0f8b1a57fd36bc6', 'core/worldline-recovery_authorization_v3_wire.ads': '30a49ffee1fecf33fe798e524cda06f73a8a2164ffe92c2bce8a10155a45f90e', 'recovery-epoch-tests/recovery_epoch_tests.gpr': '600c9e1b3b3524f1419f2419a0e0925641a9dec1c822fb0b5ddb1e2afc9bc880', 'recovery-epoch-tests/test_epochs.adb': 'b134c380bb6990c55df7c21c590627585c57a8f0bbb99453a4d4c61913a68670', 'core/worldline-recovery_protocol.adb': '1188891c1663c1c0c3ec47d304af9aaf5b14b1f9a74cff6ad771d47d06f5f573', 'core/worldline-recovery_protocol.ads': '7ca9a947061fce2a3278ab064ede1f8c2edad77fb3ecbdb68ef3f1cc41131eec', 'core/worldline-recovery_protocol_c_api.adb': '66481b8aa19d26eeffe28230b6557ce181dad9183386c81a88b88729567fcdd0', 'core/worldline-recovery_protocol_c_api.ads': '89720f0d302e8d707c51cf5d292dc4e51a5c64cf3f3280260a574d2442af79ea', 'core/worldline-recovery_protocol_wire.adb': '4716e4c67604bc3ebb236994a30a1f98a2f2684e99fa8a3dde6c6529c2c49d2b', 'core/worldline-recovery_protocol_wire.ads': '389d2fd4ad5a625f1ac5274da214c9b8e953f261882b300fbbfa96d17b5c1cd4', 'recovery-protocol-tests/test_protocol.adb': '04a6b065ae31533e8dcb04b4661aedb467bc0c89a5613bb4fcec01b7734c0447', 'recovery-protocol-tests/recovery_protocol_tests.gpr': '2ab0cb616d8ff722655c92a6767e3c4bf8feb94707b5330f881601d8eb054d40', 'core/worldline-chain_authority.adb': '4c7052b3835615308d6332303d9e9ccc2bab7b741a6c7a8457c7f98a8a4b8881', 'core/worldline-chain_authority.ads': '5a37eeb3d50c9541b522b467d7d2511138c0436b2a22a5eb0635849f77c92cf4', 'core/worldline-chain_authority_c_api.adb': '12182bc025f1312fdaa96c7354d08a2364fff4809454f5c702e1d4143c4d9e0e', 'core/worldline-chain_authority_c_api.ads': 'c2f4ab1103fb9aab92b7809bb6914e698a387c1f5850a3b3771f785d9c56e115', 'core/worldline-chain_authority_wire.adb': '9ff2355dbebbf8192b78e21adb225bb8405968612a1c8cc6e6778f27c42961e4', 'core/worldline-chain_authority_wire.ads': '7baf22c73d65bb6ba5dbe5386453da06a8b600f8a81e58931bf9c6377bada4f1', 'core/worldline-owner_transitions.adb': 'b3049b6773bed28e252c1faaa6926e6e71c3ca51a40701ad2293aa0474d8556f', 'core/worldline-owner_transitions.ads': '0d7692119a7eb400f06d1bc8b3792f9f6925f58096d23b059d8f6ea5a49000b3', 'core/worldline-owner_transitions_wire.adb': 'dcb872cec43e33aec9773ab1e95757d487dee0da9b7eb50a1f9c0a1dffe55afd', 'core/worldline-owner_transitions_wire.ads': '8867a739ddc2b22c3d73c8908a0be7bb8ecd1410bbe9232776499aa57837f814', 'core/resource_run_ledger.adb': 'eab01a895796c7e679d9241668b1d18bc768cf021fb48aed6d7fba982b042152', 'core/resource_run_ledger.ads': '77eaebdce9f0ed74f7478518a6ce1e9635fb1071e1409c17d5e7f2b5ac830648', 'core/resource_run_ledger_c_api.adb': '414cd21f48edb89e878b8efd44c77fdbe9e37b689275e5b8414f65ef83218ba1', 'core/resource_run_ledger_c_api.ads': '4c4f966a69168902bda7ed222790ca046ffd7fd7694869bebe65079bd6ff49e2', 'core/resource_run_ledger_wire.adb': 'bea60305b4242bcf72caaaa7eb1e2ded6837e72755006d9410dfb218c0b11c2c', 'core/resource_run_ledger_wire.ads': 'b09d4e07df8652f8f87b2a6526f0fa26875253ea1dc8909bbec6b330d6d02eed', 'core/worldline-owner_retry_audit.ads': 'f10e8a5758de157d40ab487c2b5071232cc8ede3b0984b36e75e922dff5b49e0', 'core/worldline-owner_retry_audit.adb': 'd444de903bc184300bbfd6e95348f4307827b7ad3948e4fe77c091daec52b5bd', 'core/worldline-owner_retry_audit_wire.ads': '60772578c6f02b53ea7b4d5614dde93f4e6d02e073847932c4647853d205f979', 'core/worldline-owner_retry_audit_wire.adb': 'a90756485c89699537c11c14b86fe5444c9ab7eb8fd3352ca4006f4610ab666f', 'core/worldline-owner_conjunction.ads': '62559ebaa5c94a88435d44333ac61aede278af67813f3ab7ac72d27bd86ec89d', 'core/worldline-owner_conjunction.adb': '9d6f3f09c955a8612747f088a14802c5004a9a656009389e11254d6d623f3c32', 'core/worldline-owner_conjunction_wire.ads': 'a078f33e659fcb0c0eac74e63777425181bd5e2865566abfb79f36fc34aa510d', 'core/worldline-owner_conjunction_wire.adb': '8aedcbc566fc59ca8a600a6410199ef8ec31b3fbffb655e856e679007f0fc7c7', 'core/worldline-owner_subject_projection.ads': '2aa7d9d7208c340ae46ac36a4bf74d0dfe1ce2f53fdae435f95fcdc39479b7f7', 'core/worldline-owner_subject_projection.adb': 'abcf67952cd84158f7a536c8315402ab6a7cb3a9f32ba13e7587ad1d0119df72', 'core/worldline-recovery_protocol_abi.ads': '7ca9a017eb112cde748227006cd5c6ffccda126cd7dd09fa7d4c36b1499ab62b', 'core/worldline-recovery_protocol_abi.adb': '362c5447a336cb8a1a87a81ce42e0c02deb8c2224bfe5330e4ca8e9a653c5247', 'protocol-adapter-tests/protocol_adapter_tests.gpr': '7e57d05ba13972588bc37cbe9b3b1a1d5c64b297a92e52349df6f08fcb5fbe47', 'protocol-adapter-tests/test_protocol_adapter.adb': '6055576865adf8a23c98ae8b7c9def207c8f253debbeb0d39548a94fdc310680', 'epoch-correspondence-tests/epoch_correspondence_core_tests.gpr': '5216f9a5a0d7f9430e4f8fe400181a6d111179bff4520d981ae3c37d18f2bc4e', 'epoch-correspondence-tests/epoch_correspondence_pending_tests.gpr': '1af95a0f4a5851f4aac0775bd8d2493fa26224639d312f097db87fb88da8ba28', 'epoch-correspondence-tests/test_epoch_correspondence.adb': 'a297bb45d5c87dd010997741f10beb7598310dd7662a255e50ad51160dd88c1a', 'core/evaluation_finalization-values.adb': 'c6dd5ea011677b3a8ae31f9d5b2ccddd51fc5549ed5f07eef27add39a3ead320', 'core/evaluation_finalization-values.ads': 'f3fe2b54ad04f1a43c5fdd181fc149fffc3441f2b744b9da6da6ef8bab8d13ce', 'finalization-value-controls/finalization_value_controls.gpr': '756918630a4b54abaff8e68e4ae84aac7a7de2b670ebea00bb86b0a6edc6e421', 'finalization-value-controls/test_finalization_parent_values.adb': '9e87197fa326dc73f582f05cc473beff73d0b08c82da4dee29951827e358de28', 'finalization-value-controls/test_finalization_projection.adb': '669b4aa0804d272585ab5fa3569a7db4435e14ea0d7224165ee8470370ebdefd', 'finalization-value-controls/test_finalization_values.adb': '3242b812f6c19ea65f5d523c6155964e6e41b7b06976718f6391761db7106b6d', 'resources-prefix-correspondence-tests/resources_prefix_correspondence_tests.gpr': 'd238363ed2e518627c36a4afe965398ac4cef15b4264f7b3d50f25b771460978', 'resources-prefix-correspondence-tests/test_resources_prefix_correspondence.adb': '19a94f3caffa77dfa2ffd705db5c1b9cd842b43fb53b7023227a3c4718cf3725', 'wire-initialization-tests/test_wire_initialization.adb': 'e779f4827c714b6329addd074cdefee94737bbada08f81a82875a6a4daba000c', 'wire-initialization-tests/wire_initialization_tests.gpr': 'bfe67074a1b0fa4193667beae58279c4746b50f8a05a6c0184354dcbe7570224', 'resource-ledger-correspondence-tests/resource_ledger_correspondence_tests.gpr': 'd1f489d22d3508c17e9c529836ec22db29d339db94f5ed70a6a0b3c365883ec8', 'resource-ledger-correspondence-tests/test_resource_ledger_correspondence.adb': 'b90bec45288928ed08de52b0103f16243c221bf05887cdd0eb4a0d75c498fa3f', 'decision-correspondence-tests/decision_correspondence_tests.gpr': '52637b39b04f201af2c2088f748a3ab7c1b032e813457638b12f1d6c18661016', 'decision-correspondence-tests/test_completion_correspondence.adb': '6ad18e9ec3136d2bf14ca45cb711801fc125ac6e307598ce0c7e0b5c6e36e945', 'decision-correspondence-tests/test_history_correspondence.adb': 'd293c070a38372238ac0c546deb2b8cab3df6f83ba21428f720ebccb6ed597cf', 'decision-correspondence-tests/test_raw_roster_correspondence.adb': 'ba17660670e42559e2b38af0d71f1c08c7126fbc527096bfb988e1aa2a59956b', 'decision-correspondence-tests/test_run_metadata_correspondence.adb': '93b4b7b7f610aaf0c844738886c347589769363e94f26d77edd4ccf4bedecad9', 'decision-correspondence-tests/test_transition_correspondence.adb': 'ac2b451ac7e78e52fcf4ee89d164fdb006f5326748517aa3b52cd99a00fb9fb1', 'core/evaluation_pending_c.ads': '9a829c27690ccecd8bf06a77357aaa0f0997b5c247848e7a9ca3697347f91f47', 'core/evaluation_pending_c.adb': '4fca4bd24b1edb06a3cfb1e2c87c3dedcfc97cdbe54a264044f8116da0cf19d0', 'core/evaluation_pending_v2_c.ads': '6044a6ef02b3b91d1064f2202a0370c34afbaff174570df26aca69f5e350653c', 'core/evaluation_pending_v2_c.adb': '54d2ea7a0a5e0bd99bc0b74fff2da73b2e233b0e451c9d5dfe3fed373de15d41', 'core/spark-big_integers.ads': 'f96017313a6e785d5c4697d95e610ced1a3612d20b7310dddb5af230226dbf1a', 'core/worldline-evaluation_history_c_api.ads': '3f2c70e3fc6f86cb5879e4b75b2e62c83eafe68f480e530c30d8b8612e194995', 'core/worldline-evaluation_history_c_api.adb': '3e5a4ceba275452894625d63364cd3d2c8abee223850808ef28000e5681f8f8d', 'core/worldline-recovery_c_api.ads': 'b0543c4f0fbc16e5247a2fb2528c419702676f1b1a8dbb1fe52708355e619f09', 'core/worldline-recovery_c_api.adb': '76d9095196c575d754b7cfb8c8ee31e631a8c0454d3455ea88edf99645c2864f', 'core/worldline-reservation_lifecycle_c_api.ads': '877551b73cb48992858a63d21961ffb9a7ab7cd7ad80312c1555c4d1cd55928f', 'core/worldline-reservation_lifecycle_c_api.adb': '2a37628e389855c7ad24cb2423d1cfdb716e63fc683108f019cec12225702598', 'core/worldline-resource_ledger_c_api.ads': '6ae817dda2eff2f1c9ef1e68fb43926b13ec4fdf954fb74a5948c0234e45c0aa', 'core/worldline-resource_ledger_c_api.adb': 'b78d12f34a0803a9b1e9a6d6617529c7bacaabc98944055b661583a4d6fddf7c', 'core/worldline-resource_policy_c_api.ads': 'e76d6da8722bd145d3c58093e578cf821c9a3d593e6fe94628315d45e5e775ff', 'core/worldline-resource_policy_c_api.adb': 'e7fb372df8cd92f7af6925b68678867ce4c24c94a83c35a0f64cc05a66fb57fd', 'core/worldline-resources_c_api.ads': '81210bc3272c53b7210e76033f19d96d2a066dedef17f7c9c6726fcf7f1e31d7', 'core/worldline-resources_c_api.adb': '5216ff373877ffbb60d71be980f666c23c74f06f99d383dd89ffca37e8dc7bcd', 'core/attest/attest-sha256.adb': '7ef39ea3e0627f562a3db75f3f392337869f96aa17ed5bf76015410b95306e9f'})

# Explicit complete marker values; original decision bodies and full domains stay required.
CONTRACT_PINS.update({'core/worldline-recovery.ads': 'b2eff79e29cd18c5a69672e3c6063faa120345d19a3f4cc76cf8ae31a69df7fc', 'explicit-recovery-marker-tests/test_explicit_recovery_markers.adb': '28b5ec869dfe195e56e2ebb0ced6fa999c5a1741723823a76a4ac13238eb4587', 'explicit-recovery-marker-tests/explicit_recovery_marker_tests.gpr': '384aebff4d2ab33af8d460dc1c3f74e7f6472db93333b637c3aed0076a05162c'})
