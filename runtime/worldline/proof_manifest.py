"""The proof-manifest checks, shared by the proof gate and the runtime (1.9.2, OB-084/OB-085).

verify_proof_manifest.py (the build and install gate) and proof.ProofStatus (what a receipt's
`invariantPreservation` says) both import this module, so the gate and the runtime cannot
disagree about what a manifest must show. It imports nothing that loads the kernel.

Pinned here: the check floor, the subprograms whose proof is a claim of this release, the one
unit left unanalyzed on purpose, and the contracts the claim depends on (CONTRACT_PINS).
Changing any of them is a deliberate edit of this file; derive pin values with
`python3 refresh_contract_pins.py --write` using the normalizer below, never by hand.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unicodedata
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
    'core/canonical_artifacts.ads': 'de5ecd7a705bd054497ac3594945b265d9ba3b34a332cd24f9849b2388b10f34',
    'core/canonical_artifacts.adb': '349e185ee8e821142f58a293c91874cffe1cf55b1699dea5217c26478d4bc428',
    'artifact-tests/canonical_artifact_tests.gpr': 'bce2824cc8181edb5f1e9d5b9c0a391d70d68302b9f717ae44f87a0cd4a1ea05',
    'artifact-tests/test_canonical_artifacts.adb': '43137b6f14b3c71b87de8f09c957e95d29a7d44dab5c67fc92698be12c50b8f1',
    'core/evaluation_finalization.ads': 'e0e85059342002b01291063b24c1a50ca2cfd94d0202e28e72806aefec332e5d',
    'core/evaluation_finalization.adb': '3e18a007d6d6d49f7bd6713d246727d27b792a517934cbadba21b0b8db1c3a95',
    'core/evaluation_finalization_c.ads': '28eb6e663262e471f71a97acf44c7683ba9c1f0979dcc88e1981a4395ea0f3c8',
    'core/evaluation_finalization_c.adb': 'e16932c56e25577c1782a927c60ad0cab68e3b503b11541a187cb5787bac5ac3',
    'core/evaluation_completion.ads': '0ced82cb877e8e9057b3b1ec796c72aee615bc4c67e95d6feecd168cda33a03b',
    'core/evaluation_completion.adb': '0fdf0e0e700022ed9113d5a3efaee58316da12d1b77feec79d5779e9a43fcd42',
    'core/evaluation_completion_roster.ads': '5af5ec8259073ad74444b5a4596b2a4b05e568c7d26739b9210e9b4616a2a2a3',
    'core/evaluation_completion_roster.adb': 'f52e2b9d4a909b3c2b616e92aaf7b87ce4ddb8a6e8b34ea99068915dc9bb253a',
    'core/evaluation_pending_v2.ads': '1e20de75c125ff20b5ad5750466430e959fb104b27f905403e38a35eb01f8321',
    'core/evaluation_pending_v2.adb': 'd8864beff6356c688f3ed26c84d27e6d0e315c423e150ee257e45df71bad3a66',
    'evaluation-authority-tests/test_evaluation_authority.adb': '071e0f859f92ac1576f95dc1c6e6f89df84c59edb304b36c3e15f0a887e98730',
    'evaluation-authority-tests/evaluation_authority_tests.gpr': 'f9ba8e8e3b9593454c25f74a5678599ebdf09afbf8510b119ebfa6f8820a98f4',
    'core/worldline-evaluation_authority.ads': 'ddf03fabb55ffcbf702dbaa066ad85a9f89a5b0e9600473b9b6824a2d1db767f',
    'core/worldline-evaluation_authority.adb': '45a92dcf5d9950d333e5c6394370ef99c99bc53dadfd9dbdcf81aab50a1f3954',
    'core/evaluation_completion_c.ads': '26a48384ae56b3590383c6ed9d408bad7dd55426cfa35402eb86d6921be34a73',
    'core/evaluation_completion_c.adb': '4eb799e6d6de99df449c2b20f7368a9602ed015b47ebff9f584f4eee8119b900',
    'core/resource_ledger.ads': '775e6daf668c1f3916b22d641a2c983d96bfa6dc9a7707709e1964a381ab950b',
    'core/resource_ledger.adb': '8b4e8022b8e938de425b07389bc8e243ff974bcd6cdbb21baf5a668b7735bd7e',
    'core/resource_reservation_transition.adb': 'f13ad8e1ef22ee22b3a6902b5c6945b0dcbb64d1385e28e8ad9d77fa083d0e86',
    'core/resource_quantities.ads': 'c39661155528ed7388b63277e034ac3bbbceba239119e4d7700218e905aeac65',
    'core/resource_quantities.adb': '155aa25399f30cb4837d589ae87c24ff8e2589dadbf27be06b9995bde3b6233b',
    'pending-component/core/resource_quantities.ads': 'ff725d00a0be90fa2ca4632e9f48878f5f58199cbfacf2a82bfa554f4cdfe63a',
    'pending-component/core/resource_quantities.adb': '48656286ffabeb9cac8436cafa2fe3bac2bb91a231ed17178966660c93f34206',
    'core/evaluation_history.ads': 'e58eea740afa7f385a386ad97ad78380eb61ccac35d7669f14768dd4ac30cc3a',
    'core/evaluation_history.adb': '74a24e09ac21e8900167db0f25b43cfd33d000eb52922653133a8e631a911c3f',
    'core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5',
    'core/evaluation_epoch.adb': 'ee9b16847dfb3dedce58a9b6539e2568816b745d2bd0cb808a36362072df9e1b',
    'pending-component/core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5',
    'pending-component/core/evaluation_epoch.adb': '76fa1977a41b3cdef9ee15972a1970db67771ec2f5bf0dab2cada0088679f363',
    'core/worldline-resources.ads': '7fdf97a76f11aeeecfcde00c0e5e2587fde0f3155983765d006026aac70d4530',
    'core/worldline-resources.adb': '8b9836dcb1eb091316a6dc08deb303aebdb664dcab5bb26e023c15e7a8ff8fb9',
    'core/worldline-evaluation_v2.ads': '8e1f18244b924a7c9c05c67fdf785491a910c9f7c59966381b38962c2f68a72c',
    'core/worldline-evaluation_v2.adb': '2fc57758a66ac2c7aa9ef6e108fdcbf93b1b286fd64b6620d8bca54ce32312eb',
    'core/worldline-evaluation_wire.ads': '8b190a32f057a30a700e3331bd72aa2cfc18c5d6f3540b824756197f09077c7a',
    'core/worldline-evaluation_wire.adb': '30696c9e2b4be84aad47d406864213a176f494e07dbed6f6907efe601d3be530',
    'core/evaluation_raw_roster.ads': '1fcc5358aad66d61571552e80be7572fc47cb21fc8b4ab2dad2005812cd9664b',
    'core/evaluation_raw_roster.adb': '51b238fc3489523bbc10acca6ee47dd274e391fb9491af8f65943b04396b4569',
    'core/worldline-evaluation_report_facts.ads': 'f8bfee03303776b2825662bb1ce394fdf3c3e6acf3e7b1084500e50eba430f82',
    'core/worldline-evaluation_report_facts.adb': 'ffdc1629f8eaef1ec4ab1bbc4fc988f2f1546dd8b5013ec4635888d77f8240fb',
    'core/worldline-evaluation_report_wire.ads': 'a58347985c4242421c4114ecf61ddaf6f84229e62ab2114cd0947b7feee29b19',
    'core/worldline-evaluation_report_wire.adb': '19ed101a83a9a9350a660cd7693a8be7ffee86557fa6d58e7959a0ae9973ff78',
    'evaluation-wire-tests/evaluation_wire_tests.gpr': '8fde6733c882c9be99a7fbcdce0c6ba0a8eca138a4b68e65ec77efdc84160d89',
    # The project files decide which file is compiled as each unit; a pin on a source's text
    # binds nothing if they may redirect it (review of ab1d4bb).
    "worldline.gpr": "edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021",
    "core/worldline_core.gpr": "f1a6492bceff785f35dec5f30d3d5470fe7f439b5a85c02ddcbb3b4b44a47436",
    "core/worldline_sparklib_link.gpr": "61837dd0ec6acc611b3a4c98050b30e464ecef2f46ea11c950670283b8aebe52",
    "core/worldline_core_sources.gpr": "ed7f3006aec84e5059b9163b0aa525ed829a256f2e418bb400e0291bb1434077",
    "core/attest_sha256.gpr": "f75c901810d0227f9b1331929e06a4405eb83c82385e5cab2be4f4e86daf8822",
    "tests/worldline_tests.gpr": "0cf4fdd19da37ad197a3ea063fdbb259a7400d4e3865e40088fd78ee6fb7560d",
    "core/worldline.ads": "6fc501e7d5e4927784d415e25c84339efd42a96358216c69825882deea3603e3",
    "core/attest/attest.ads": "bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587",
    "core/attest/attest-sha256.ads": "b5b299d3559e8a083d1edbbaefc96f76f73a0c4e0e6d2dfdcfb6d3fc0c4d7bec",
    "core/worldline-c_api.ads": "1da0afffd071cb78449216a359b362f9d31e6cae22e9d02c09cb19bfce097efe",
    "core/worldline-collapse.ads": "94ef49a258a46363eea81d44e168ce4e7cc618fdf128e916e92e447f2ffe32e2",
    "core/worldline-collapse_wire.ads": "48270be156ee3f1c7d7f6215917c9b8026ac5346c45064cf7803950c137ddd76",
    "core/worldline-identities.ads": "ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21",
    "core/worldline-evaluation.ads": "06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e",
    "core/worldline-transitions.ads": "5b9c8f89900d01eeb40818de6392e1f23f8e2606cba702dd06e72e4257406c27",
    "core/worldline-c_api.adb": "64a839d076a4e52d8fb65c599a91f9eb0812adef30f8e48a4e80669f56557f52",
    "core/worldline-receipts.ads": "a354588d79bc6d01973afcf10b9b31a08d996e2056a1bad8db05e97fe7636dd6",
    "core/worldline-receipts.adb": "8b30e5567ec7a86962f9cea3cd67b6d07194dc726e70b025bc2f97a406767829",
    "core/worldline-causal_graph.ads": "4c1db06549310c2dd93c26b9e109dd832a0f43390fe7ece37dbab06934b78ae7",
    "core/worldline-causal_graph.adb": "e3239b7770a185f4eef90d838c803a64b128e84380e3af27513867632ff3c121",
    "core/worldline-world.ads": "3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5",
    "core/worldline-ancestry.ads": "718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db",
    'core/resource_admission.adb': '0da682e7cd0aa85daea88a9f36926fa213240b9273cd7015108f95f4f48ee63c',
    'core/resource_admission.ads': '2d93c087e980ec50ce77a21efdeb4c2d3a96e503493e55c0a9cbbb27e80381f2',
    'core/resource_reservation_lifecycle.adb': '3cf6bbe8dfef85f485be16eb9185768ace28ddc6a3ea5bfe0cd0aa26dd8aef41',
    'core/resource_reservation_lifecycle.ads': '8e3c85334abc8ff747e6f468bea29f04196c3c11cffa10a68207b96c8b3e0400',
    'core/resource_reservation_transition.ads': '34d4b6d554999fc3366b78d0740be905c21e0d3c0c20b6fb96fa82691674a9d2',
    'core/worldline-recovery.adb': '75763d6eb35c647df523a728c6939e21cda6c3d7b44ba54fb2a4a917f3149e24',
    'core/worldline-recovery.ads': 'b2eff79e29cd18c5a69672e3c6063faa120345d19a3f4cc76cf8ae31a69df7fc',
    'core/worldline-recovery_authorization.adb': 'd90b75ec516fbf8ddb0f0bf40ee39297e70eebc001d4edad6b0142c7da092e7d',
    'core/worldline-recovery_authorization.ads': '3b95bc25da8343b9d0c4cd6e133614bb59cdce65740142d9c2d2ed072e62dec6',
    'core/worldline-recovery_authorization_c_api.adb': 'c9ccade8b28286a2166130c0057ca3187a7465a8c1521c523fda3429b004282c',
    'core/worldline-recovery_authorization_c_api.ads': '88a156f3749251a4cff6393739ce7b738e82fb9d625c71774489f99430914f34',
    'core/worldline-recovery_authorization_wire.adb': 'e0c1054dd20e34bf1ddbcaefd9665c7588fc4683c8dad1a91351c89597928f62',
    'core/worldline-recovery_authorization_wire.ads': 'a6b453f40b2eee2d860008ecb11b9720f6be2a5be5c1aca52a91f264c40d687c',
    'core/worldline-resource_wire.adb': 'ec1ea00cf321f841aafcb874047c48d1ff28363d29ea042c6703a60a2be32f80',
    'core/worldline-resource_wire.ads': 'b0af3ef936e727ba9113430ebc29c2843124f82e584b3bb294dc23af2667ad75',
}


# Source-selected V3 composition; no prior manifest is evidence for this candidate.
CONTRACT_PINS.update({'core/worldline-recovery_authorization_v3.adb': '21536d8595e0d6d14764b56309eb2f88d28bd88fc47b6fe9c16f915c98ed63dd', 'core/worldline-recovery_authorization_v3.ads': '8b3f3c7477c461dadceba33ab421cf54d4c77129e2875768346d93c91f3fdd51', 'core/worldline-recovery_authorization_v3_c_api.adb': '9a90152c2f15a615f61dbe3d96aa520f48ce541a0f8b9843dbb51553aef19ac4', 'core/worldline-recovery_authorization_v3_c_api.ads': '06832ec39eec8162227eadb2f158d7ca53ec6af0d796693d0701b32d430cf6c9', 'core/worldline-recovery_authorization_v3_wire.adb': '5df8bd9bcd6842aaf033bde67edd121e6d9e0bdfd6f29158f0f8b1a57fd36bc6', 'core/worldline-recovery_authorization_v3_wire.ads': '30a49ffee1fecf33fe798e524cda06f73a8a2164ffe92c2bce8a10155a45f90e', 'core/worldline_core.gpr': 'f1a6492bceff785f35dec5f30d3d5470fe7f439b5a85c02ddcbb3b4b44a47436', 'recovery-epoch-tests/recovery_epoch_tests.gpr': '600c9e1b3b3524f1419f2419a0e0925641a9dec1c822fb0b5ddb1e2afc9bc880', 'recovery-epoch-tests/test_epochs.adb': 'b134c380bb6990c55df7c21c590627585c57a8f0bbb99453a4d4c61913a68670'})

def ada_source_text(data: bytes) -> str:
    """Decode source-effective input without discarding layout or literal spelling."""
    return "".join(value for _, value in ada_tokens(data))


def ada_identifier_key(value: str) -> str:
    """Ada simple case folding, with ASCII keys for the pragma vocabulary.

    Full Unicode casing can expand one identifier character into several ASCII
    keyword letters. Python supplies common/full folding; the complete Unicode
    16.0 CaseFolding.txt S relation below supplies simple alternatives to full
    expansions. Keep token spelling separately: this key is not the projection.
    """
    simple_sources = (
        "\u1e9e\u1f88\u1f89\u1f8a\u1f8b\u1f8c\u1f8d\u1f8e"
        "\u1f8f\u1f98\u1f99\u1f9a\u1f9b\u1f9c\u1f9d\u1f9e"
        "\u1f9f\u1fa8\u1fa9\u1faa\u1fab\u1fac\u1fad\u1fae"
        "\u1faf\u1fbc\u1fcc\u1fd3\u1fe3\u1ffc\ufb05")
    simple_targets = (
        "\xdf\u1f80\u1f81\u1f82\u1f83\u1f84\u1f85\u1f86"
        "\u1f87\u1f90\u1f91\u1f92\u1f93\u1f94\u1f95\u1f96"
        "\u1f97\u1fa0\u1fa1\u1fa2\u1fa3\u1fa4\u1fa5\u1fa6"
        "\u1fa7\u1fb3\u1fc3\u0390\u03b0\u1ff3\ufb06")
    characters = []
    for character in value:
        if unicodedata.category(character) == "Cf":
            continue
        folded = character.casefold()
        if len(folded) != 1:
            position = simple_sources.find(character)
            folded = simple_targets[position] if position >= 0 else character
        characters.append(folded.upper() if "a" <= folded <= "z" else folded)
    return "".join(characters)


def ada_tokens(text: str | bytes, *, canonical_pragmas: bool = False):
    """Share one stateful lexer between source screening and contract pins.

    The initial profile is Ada 2022 and Latin-1 (UTF-8 with a BOM). Source
    pragmas can select UTF8/'8', plain BRACKETS/'b', or a documented Ada version.
    Rename_Pragma aliases take effect only subsequently, including aliases of
    controls and aliases of aliases. Redefinitions and unsupported controls are
    refused rather than guessed. Pragma names alone may be canonicalized for
    screening; the pin projection retains their original spelling.

    Identifier categories follow RM 2.3. Layout and literal spelling are retained,
    so ada_source_text also uses this lexer, not a separate decoding pass. Encoded
    bracket/ESC forms, legacy wide encodings, extension/ignore controls and
    ambiguous encoding lookahead are explicitly outside this lexical profile.
    """
    starts = frozenset(("Lu", "Ll", "Lt", "Lm", "Lo", "Nl"))
    extends = starts | {"Mn", "Mc", "Nd", "Pc", "Cf"}
    endings = "\r\n\v\f\x85\u2028\u2029"
    keywords = frozenset("""
        ABORT ABS ACCEPT ACCESS ALL AND ARRAY AT BEGIN BODY CASE CONSTANT
        DECLARE DELAY DELTA DIGITS DO ELSE ELSIF END ENTRY EXCEPTION EXIT FOR
        FUNCTION GENERIC GOTO IF IN IS LIMITED LOOP MOD NEW NOT NULL OF OR
        OTHERS OUT PACKAGE PRAGMA PRIVATE PROCEDURE RAISE RANGE RECORD REM
        RENAMES RETURN REVERSE SELECT SEPARATE SUBTYPE TASK TERMINATE THEN
        TYPE USE WHEN WHILE WITH XOR
    """.split())
    additions = {
        1995: frozenset("ABSTRACT ALIASED PROTECTED REQUEUE TAGGED UNTIL".split()),
        2005: frozenset("INTERFACE OVERRIDING SYNCHRONIZED".split()),
        2012: frozenset({"SOME"}),
        2022: frozenset({"PARALLEL"}),
    }
    languages = {"ADA_83": 1983, "ADA_95": 1995, "ADA_05": 2005,
                 "ADA_2005": 2005, "ADA_12": 2012, "ADA_2012": 2012,
                 "ADA_2022": 2022}
    refused = {"IGNORE_PRAGMA", "EXTENSIONS_ALLOWED", "USER_ASPECT_DEFINITION"}
    controls = set(languages) | refused | {"RENAME_PRAGMA", "WIDE_CHARACTER_ENCODING"}
    targets = controls | {"ANNOTATE", "ASSUME", "SPARK_MODE"}
    aliases = {}
    alias_targets = set()
    used_pragmas = set()
    version = 2022
    binary = isinstance(text, bytes)
    bom = text.startswith(b"\xef\xbb\xbf") if binary else text.startswith("\ufeff")
    encoding = "utf-8" if bom else "latin-1"
    index = (3 if binary else 1) if bom else 0
    transition = False
    name_prefix = False
    pragma = None
    pragma_name = None

    canonical = ada_identifier_key

    def at(position):
        if position >= len(text):
            return "", position
        if not binary:
            value, end = text[position], position + 1
        elif encoding == "latin-1" or text[position] < 128:
            value, end = chr(text[position]), position + 1
        else:
            first = text[position]
            if 0xC2 <= first <= 0xDF:
                width = 2
            elif 0xE0 <= first <= 0xEF:
                width = 3
            elif 0xF0 <= first <= 0xF4:
                width = 4
            else:
                raise ValueError(f"unsupported or malformed UTF-8 at byte {position}")
            end = position + width
            value = text[position:end].decode("utf-8")
        if transition and ord(value) >= 128:
            # GNAT scans ahead before applying this pragma (GNAT RM 2.210).
            # An ASCII token between it and high text makes both readings agree.
            raise ValueError("encoding change requires an intervening ASCII token before non-ASCII text")
        return value, end

    def spelling(start, end):
        value = text[start:end]
        return value.decode(encoding) if binary else value

    def reject_escape(position, char):
        if char not in ("[", "\x1b"):
            return
        probe = text[position:position + 12]
        if binary:
            probe = probe.decode("latin-1")
        if char == "\x1b" or re.match(
                r'\["(?:[0-9A-Fa-f]{2}|[0-9A-Fa-f]{4}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})"\]',
                probe):
            raise ValueError("unsupported GNAT bracket/ESC source encoding")

    def arguments(tokens):
        if not tokens:
            return []
        if tokens[0] != ("symbol", "(") or tokens[-1] != ("symbol", ")"):
            raise ValueError("malformed source control pragma: " + pragma_name)
        result = [[]]
        for token in tokens[1:-1]:
            if token == ("symbol", ","):
                result.append([])
            elif token in (("symbol", "("), ("symbol", ")"), ("symbol", ";")):
                raise ValueError("ambiguous source control arguments: " + pragma_name)
            else:
                result[-1].append(token)
        if any(not item for item in result):
            raise ValueError("empty source control argument: " + pragma_name)
        return result

    def apply_control():
        nonlocal encoding, transition, version
        if pragma_name not in controls:
            return
        if pragma_name in refused:
            raise ValueError("unsupported source-effective control: " + pragma_name)
        args = arguments(pragma[2:-1])
        if pragma_name == "RENAME_PRAGMA":
            if len(args) != 2:
                raise ValueError("Rename_Pragma requires New_Name and Renamed identifiers")
            fields = {}
            named = False
            for position, item in enumerate(args):
                if len(item) == 1 and item[0][0] == "identifier" and not named:
                    field, value = ("NEW_NAME", "RENAMED")[position], item[0][1]
                elif (len(item) == 4 and item[0][0] == item[3][0] == "identifier"
                      and item[1:3] == [("symbol", "="), ("symbol", ">")]):
                    named = True
                    field, value = canonical(item[0][1]), item[3][1]
                else:
                    raise ValueError("malformed or ambiguous Rename_Pragma arguments")
                if field not in {"NEW_NAME", "RENAMED"} or field in fields:
                    raise ValueError("malformed or duplicate Rename_Pragma association")
                fields[field] = canonical(value)
            if set(fields) != {"NEW_NAME", "RENAMED"}:
                raise ValueError("Rename_Pragma requires New_Name and Renamed identifiers")
            new, renamed = fields["NEW_NAME"], fields["RENAMED"]
            reserved = keywords | frozenset().union(
                *(extra for since, extra in additions.items() if version >= since))
            if (new in aliases or new in targets or new in reserved
                    or new in alias_targets or new in used_pragmas or new == renamed):
                raise ValueError("unsupported Rename_Pragma redefinition or forward binding: " + new)
            # Preserve generic harmless aliases too; GNAT validates target
            # legality. An existing alias is resolved at its declaration point.
            aliases[new] = aliases.get(renamed, renamed)
            alias_targets.add(aliases[new])
        elif pragma_name == "WIDE_CHARACTER_ENCODING":
            if len(args) != 1 or len(args[0]) != 1:
                raise ValueError("malformed Wide_Character_Encoding arguments")
            kind, value = args[0][0]
            method = canonical(value) if kind == "identifier" else {
                "'8'": "UTF8", "'b'": "BRACKETS",
                "'h'": "HEX", "'u'": "UPPER", "'s'": "SHIFT_JIS", "'e'": "EUC",
            }.get(value) if kind == "character" else None
            if method not in {"UTF8", "BRACKETS"}:
                raise ValueError("unsupported Wide_Character_Encoding method: " + value)
            selected = "utf-8" if method == "UTF8" else "latin-1"
            transition = binary and selected != encoding
            encoding = selected
        elif not args:
            version = languages[pragma_name]
        elif not (languages[pragma_name] >= 2005 and len(args) == 1
                  and len(args[0]) == 1 and args[0][0][0] == "identifier"):
            raise ValueError("unsupported Ada language-control arguments: " + pragma_name)
        # The single-entity Ada_05/12/2022 form marks an entity, not a mode.

    while index < len(text):
        start = index
        char, following = at(index)
        if char == "-" and at(following)[0] == "-":
            index = following
            while index < len(text) and at(index)[0] not in endings:
                _, index = at(index)
            yield "layout", spelling(start, index)
            continue
        if char.isspace():
            index = following
            yield "layout", char
            continue
        reject_escape(index, char)
        if unicodedata.category(char) in starts:
            index = following
            while index < len(text) and unicodedata.category(at(index)[0]) in extends:
                _, index = at(index)
            value = spelling(start, index)
            word = canonical(value)
            reserved = word in keywords or any(
                word in extra for since, extra in additions.items() if version >= since)
            name_prefix = not reserved or word == "ALL"
            kind = "identifier"
        elif char == "'" and not name_prefix and at(at(following)[1])[0] == "'":
            _, payload_end = at(following)
            reject_escape(following, at(following)[0])
            _, index = at(payload_end)
            kind, value = "character", spelling(start, index)
            name_prefix = False
        elif char in ('"', "%"):
            index = following
            while index < len(text):
                current, end = at(index)
                if current in endings:
                    raise ValueError("unterminated Ada string literal")
                reject_escape(index, current)
                index = end
                if current == char:
                    if at(index)[0] == char:
                        _, index = at(index)
                        continue
                    break
            else:
                raise ValueError("unterminated Ada string literal")
            kind, value = "string", spelling(start, index)
            name_prefix = False
        else:
            kind, value = "symbol", char
            name_prefix = char in ")]"
            index = following
        transition = False
        token = kind, value
        word = canonical(value) if kind == "identifier" else value
        if kind == "identifier" and word == "PRAGMA":
            if pragma is not None:
                raise ValueError("nested or unterminated source pragma")
            pragma = []
        if pragma is not None:
            if len(pragma) == 1:
                if kind != "identifier":
                    raise ValueError("malformed source pragma name")
                pragma_name = aliases.get(word, word)
                used_pragmas.add(word)
                if canonical_pragmas:
                    token = kind, pragma_name
            pragma.append((kind, value))
            if (kind, value) == ("symbol", ";"):
                apply_control()
                pragma = None
        yield token
    if pragma is not None and pragma_name in controls:
        raise ValueError("unterminated source control pragma: " + pragma_name)


def normalized_ada(text: str | bytes) -> str:
    """Collapse external layout/comments while preserving literal payloads."""
    parts = []
    layout = False
    for kind, token in ada_tokens(text):
        if kind == "layout":
            layout = bool(parts)
        else:
            if layout:
                parts.append(" ")
            parts.append(token)
            layout = False
    return "".join(parts)


def source_profile_problems(root: Path, paths) -> list[str]:
    """Refuse extra lexical configuration instead of assuming it was not applied.

    Standalone gnat.adc files and project-selected configuration/preprocessing or
    encoding overrides need a separate source-effective profile implementation.
    Project pins remain required; this is not a replacement GPR evaluator.
    """
    paths = tuple(paths)
    directories = {root, *(path.parent for path in paths)}
    configurations = set(root.rglob("gnat.adc"))
    configurations.update(path for directory in directories for path in directory.glob("*.adc"))
    problems = [
        "unsupported additional configuration pragma file: " + str(path)
        for path in sorted(configurations)
    ]
    attributes = {"GLOBAL_CONFIGURATION_PRAGMAS", "LOCAL_CONFIGURATION_PRAGMAS"}

    def lexical_override(argument):
        for match in re.finditer(r"-gnat(\S*)", argument):
            option = match[1]
            if option in {"2022", "22"}:
                continue
            if not option:
                return True
            # GNAT permits combined switches. After w/V/y the remainder is
            # warning/validity/style data, not another lexical-profile switch.
            for flag in option:
                if flag in "wVy":
                    break
                if flag in "WiXe" or flag.isdecimal():
                    return True
        return False

    for path in sorted(set(paths)):
        if path.suffix.lower() != ".gpr":
            continue
        try:
            for kind, value in ada_tokens(path.read_bytes()):
                if kind == "identifier" and ada_identifier_key(value) in attributes:
                    problems.append(f"unsupported project configuration pragma attribute: {path}: {value}")
                elif kind == "string":
                    argument = value[1:-1]
                    if lexical_override(argument):
                        problems.append(f"unsupported project lexical-profile switch: {path}: {value}")
        except (OSError, ValueError) as exc:
            problems.append(f"project lexical profile unreadable: {path}: {exc}")
    return problems


def contract_text(root: Path, key: str) -> str:
    relative, _, subprogram = key.partition("#")
    text = normalized_ada((root / relative).read_bytes())
    if not subprogram:
        return text
    start = text.find(f"function {subprogram} ")
    end = text.find(f"end {subprogram};", start)
    if start < 0 or end < 0 or text.find(f"function {subprogram} ", start + 1) >= 0:
        raise ValueError(f"cannot isolate {key}")
    return text[start:end + len(f"end {subprogram};")]


def contract_pin(root: Path, key: str) -> str:
    return hashlib.sha256(contract_text(root, key).encode("utf-8")).hexdigest()


# The public ABI stayed in C_API when typed semantic entries gained observer
# parameters. These identities are additional migration guards, NOT replacement
# CONTRACT_PINS or a proof of their contents. Full contract/source/proof/ABI gates
# remain required. Normalized identities preserve literal payloads and collapse
# only external layout/comments. They are still projections: additive raw-byte
# identities below bind every source byte, including comments. Each new raw
# pin requires complete-unit review; this intentionally refuses comment/layout
# changes as well. Aliases, bounds, copies, helpers, status branches, exception
# paths and literal bytes are within these complete raw source identities.
_TYPED_EXPORT_DECLARATIONS = {'wl_chain_authority_replay_v1': 'function Owned_Chain_Replay (Anchors : System.Address; '
                                 'Anchors_Length : Interfaces.C.size_t; Rows : System.Address; '
                                 'Rows_Count, Rows_Length : Interfaces.C.size_t; Output : '
                                 'System.Address; Output_Length : Interfaces.C.size_t) return '
                                 'Interfaces.C.int with Export, Convention => C, External_Name => '
                                 '"wl_chain_authority_replay_v1";',
 'wl_collapse_decide_finalization_v1': 'function Finalization_Decide_Mixed (Collapse : '
                                       'System.Address; Primary_Kind : Interfaces.Unsigned_32; '
                                       'Primary, Primary_Raw, Primary_Confinement, Primary_Context '
                                       ': System.Address; Staged_Kind : Interfaces.Unsigned_32; '
                                       'Staged, Staged_Raw, Staged_Confinement, Staged_Context, '
                                       'Agent : System.Address; Agent_Confinement : '
                                       'Interfaces.Unsigned_8) return Interfaces.Unsigned_8 with '
                                       'Export, Convention => C, External_Name => '
                                       '"wl_collapse_decide_finalization_v1";',
 'wl_finalization_decide_v1': 'function Finalization_Decide (Input, Output : System.Address) '
                              'return Interfaces.C.int with Export, Convention => C, External_Name '
                              '=> "wl_finalization_decide_v1";',
 'wl_recovery_authorization_decide_v3': 'function Owned_recovery_authorization_v3 (Input : '
                                        'System.Address; Input_Length : Interfaces.C.size_t; Arena '
                                        ': System.Address; Arena_Length : Interfaces.C.size_t; '
                                        'Output : System.Address; Output_Length : '
                                        'Interfaces.C.size_t) return Interfaces.C.int with Export, '
                                        'Convention => C, External_Name => '
                                        '"wl_recovery_authorization_decide_v3";',
 'wl_recovery_protocol_decide_v1': 'function Owned_recovery_protocol (Input : System.Address; '
                                   'Input_Length : Interfaces.C.size_t; Output : System.Address; '
                                   'Output_Length : Interfaces.C.size_t) return Interfaces.C.int '
                                   'with Export, Convention => C, External_Name => '
                                   '"wl_recovery_protocol_decide_v1";'}
_TYPED_EXPORT_NORMALIZED_UNIT_PINS = {'core/evaluation_finalization_c.adb': 'e16932c56e25577c1782a927c60ad0cab68e3b503b11541a187cb5787bac5ac3',
 'core/evaluation_finalization_c.ads': '28eb6e663262e471f71a97acf44c7683ba9c1f0979dcc88e1981a4395ea0f3c8',
 'core/worldline-c_api.adb': '64a839d076a4e52d8fb65c599a91f9eb0812adef30f8e48a4e80669f56557f52',
 'core/worldline-c_api.ads': '1da0afffd071cb78449216a359b362f9d31e6cae22e9d02c09cb19bfce097efe',
 'core/worldline-chain_authority_c_api.adb': 'f3a7c76c681bf8e82960929a3c30659c1926dba38d71bd59f96abaa875c5326a',
 'core/worldline-chain_authority_c_api.ads': 'c44a9c3ddd2dce171d5ff88c2da981b36afec678db7e830e24fa60699b1784b0',
 'core/worldline-recovery_authorization_v3_c_api.adb': '9a90152c2f15a615f61dbe3d96aa520f48ce541a0f8b9843dbb51553aef19ac4',
 'core/worldline-recovery_authorization_v3_c_api.ads': '06832ec39eec8162227eadb2f158d7ca53ec6af0d796693d0701b32d430cf6c9',
 'core/worldline-recovery_protocol_c_api.adb': 'b8921fc27ccca361edcb7b6477e3804c16cff2aa154fe279bc368d65f51ddf77',
 'core/worldline-recovery_protocol_c_api.ads': '659e9b509e0350d58039f67ce3741cb01eff6a266b970b00bf56f601b550d413'}
_TYPED_EXPORT_RAW_UNIT_PINS = {'core/evaluation_finalization_c.adb': 'dee2db8b374345f30aa39877e6489f1670509aa8a428ccf2be90ded8c3069fef',
 'core/evaluation_finalization_c.ads': '93bfb1a973ba6b72ca201e3e3869e094bdb162c931a786f3ca82df2594120b73',
 'core/worldline-c_api.adb': '56fd9834217306dff41751ff88fbc111515016ec711a0519dd4def206c9a28ae',
 'core/worldline-c_api.ads': 'd947b43d0b111a516fafc85789f2310e0942d43673524fc04c1451f23db88aa6',
 'core/worldline-chain_authority_c_api.adb': '9302e23d571f580aa0ed78b7c18158ae202000bae04109c9a5d61422e6569b50',
 'core/worldline-chain_authority_c_api.ads': 'd9be8c4167d43909e2d9e0aa1ba1cf53be115426f14029e9980b699741e56279',
 'core/worldline-recovery_authorization_v3_c_api.adb': 'e5b06e6ce91f9e1667c1ffa51ec05cc2fe519fde52d599f75a178f9a1cdc6c7b',
 'core/worldline-recovery_authorization_v3_c_api.ads': '4523ee8a7a771e92d12831720b37908fc115f5c8f7b9963221a3e37c5bfef99a',
 'core/worldline-recovery_protocol_c_api.adb': 'e8cde5b8c8fde61d16991755de370c2559c3105ba58c98f083fb86535d806c45',
 'core/worldline-recovery_protocol_c_api.ads': '425970d3ac20aba3f0895a75f894c1b877ba65566340f126c3cddc24d5528270'}


def _uses_typed_export_layout(text: str) -> bool:
    # A partial or mixed migration takes the strict typed branch and refuses.
    return any('"' + symbol + '"' in text for symbol in _TYPED_EXPORT_DECLARATIONS)


def _typed_export_correspondence_problems(root: Path) -> list[str]:
    """Closed reviewed transport layout; never infer authority from symbol presence.

    The literal inventory catches direct aspect/pragma/link-name duplicates.
    It is not an Ada constant-expression resolver or linker symbol audit. The
    unchanged complete source inventory and CONTRACT_PINS additionally reject
    nonliteral aliases/new sources; linked ELF/ABI controls remain required.
    """
    problems = []
    texts = {}
    raw_digests = {}
    paths = sorted(set((root / 'core').rglob('*.ads')) |
                   set((root / 'core').rglob('*.adb')))
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            raw = path.read_bytes()
            if relative in _TYPED_EXPORT_RAW_UNIT_PINS:
                raw_digests[relative] = hashlib.sha256(raw).hexdigest()
            texts[relative] = normalized_ada(raw)
        except (OSError, ValueError) as exc:
            problems.append(f'typed export source unreadable: {relative}: {exc}')
    spec = texts.get('core/worldline-c_api.ads', '')
    for symbol, declaration in _TYPED_EXPORT_DECLARATIONS.items():
        locations = [relative for relative, text in texts.items()
                     for _ in range(text.count('"' + symbol + '"'))]
        if locations != ['core/worldline-c_api.ads']:
            problems.append(f'typed export binding inventory differs: {symbol}: {locations}')
        if spec.count(declaration) != 1:
            problems.append(f'typed export ABI declaration differs: {symbol}')
    for relative, expected in _TYPED_EXPORT_NORMALIZED_UNIT_PINS.items():
        text = texts.get(relative)
        if text is None or hashlib.sha256(text.encode('utf-8')).hexdigest() != expected:
            problems.append(f'typed export normalized transport projection differs: {relative}')
    for relative, expected in _TYPED_EXPORT_RAW_UNIT_PINS.items():
        if raw_digests.get(relative) != expected:
            problems.append(f'typed export raw transport bytes differ: {relative}')
    return problems


def export_problems(root: Path) -> list[str]:
    """The C symbol the runtime calls for the collapse decision must be bound exactly once, to
    Collapse_Decide, whose body is pinned (review of 0ee1112: moving the binding to another
    function left every pin intact)."""
    text = normalized_ada((root / "core/worldline-c_api.ads").read_bytes())
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
    if problems:
        return problems
    typed_layout = _uses_typed_export_layout(text)
    if typed_layout:
        problems.extend(_typed_export_correspondence_problems(root))
        if problems:
            return problems
    finalization = normalized_ada((root / 'core/evaluation_finalization_c.ads').read_bytes())
    final_entry = ('function Decide (Input, Output : System.Address) return Interfaces.C.int '
        'with Export, Convention => C, External_Name => "wl_finalization_decide_v1";')
    mixed_entry = ('function Decide_Mixed (Collapse : System.Address; Primary_Kind : U32; '
        'Primary, Primary_Raw, Primary_Confinement, Primary_Context : System.Address; '
        'Staged_Kind : U32; Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address; '
        'Agent_Confinement : U8) return U8 with Export, Convention => C, '
        'External_Name => "wl_collapse_decide_finalization_v1";')
    if not typed_layout and (finalization.count('External_Name => "wl_finalization_decide_v1"') != 1 or final_entry not in finalization):
        problems.append('finalization Start/Input/Seal native entry differs')
    if not typed_layout and (finalization.count('External_Name => "wl_collapse_decide_finalization_v1"') != 1 or mixed_entry not in finalization):
        problems.append('finalization mixed collapse native entry differs')
    v3 = normalized_ada((root / 'core/worldline-recovery_authorization_v3_c_api.ads').read_bytes())
    for symbol in ('wl_recovery_authorization_version_v3', 'wl_recovery_authorization_layout_v3',
                   'wl_recovery_authorization_decide_v3'):
        if typed_layout and symbol == 'wl_recovery_authorization_decide_v3':
            continue  # Exact public profile and whole typed transport already checked.
        if v3.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'full-domain recovery export binding differs: {symbol}')
    owner_entry = ('function Excluded_Source_Owner_Decide_V1 (Input : System.Address; Length : Interfaces.C.size_t; '
                   'Status : System.Address) return Interfaces.C.int with Export, Convention => C, '
                   'External_Name => "wl_excluded_source_owner_decide_v1";')
    if text.count('External_Name => "wl_excluded_source_owner_decide_v1"') != 1 or owner_entry not in text:
        problems.append('fixed source-owner owned-buffer decision binding differs')
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
    problems = source_profile_problems(root, source_paths(root).values())
    try:
        problems += export_problems(root)
    except (OSError, ValueError) as exc:
        return problems + [f"pinned contract unreadable: core/worldline-c_api.ads: {exc}"]
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

# The pinned GPR excludes these local copies and imports the real SPARKlib
# units instead. Keep the copies in the explicit source inventory, but do not
# mistake their presence/hashes for proof of the imported implementations.
# This mapping is not an unanalyzed exemption: every imported dependency below
# remains subject to the same full per-unit coverage and zero-exception checks.
_LOCAL_SPARK_REPLACEMENTS = {
    "core/spark.ads": "spark",
    "core/spark-big_integers.ads": "spark-big_integers",
}
_IMPORTED_SPARK_UNITS = frozenset({
    "spark",
    "spark-big_integers",
    "spark-containers",
    "spark-containers-functional",
    "spark-containers-functional-base",
    "spark-containers-functional-holder",
    "spark-containers-functional-infinite_sequences",
    "spark-containers-parameter_checks",
    "spark-containers-types",
})


def expected_units(root: Path) -> set[str]:
    """Explicit selected local units and their real imported SPARKlib dependencies.

    Missing files cannot shrink coverage, and discovered files cannot enroll
    themselves. The source/frame identity must additionally bind the selected
    imported sources and projects; a local placeholder is not that evidence.
    """
    units = {Path(relative).stem for relative in DECLARED_CORE_ADA_SOURCES
             if relative not in _LOCAL_SPARK_REPLACEMENTS}
    return units | _IMPORTED_SPARK_UNITS


def source_paths(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {
        "worldline.gpr": root / "worldline.gpr",
        "attest/attest.ads": root / "core/attest/attest.ads",
        "attest/attest-sha256.ads": root / "core/attest/attest-sha256.ads",
        "attest/attest-sha256.adb": root / "core/attest/attest-sha256.adb",
        "attest/attest-custody_sha256.ads": root / "core/attest/attest-custody_sha256.ads",
        "attest/attest-custody_sha256.adb": root / "core/attest/attest-custody_sha256.adb",
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
CONTRACT_PINS.update({'core/worldline-recovery_protocol.adb': '1188891c1663c1c0c3ec47d304af9aaf5b14b1f9a74cff6ad771d47d06f5f573', 'core/worldline-recovery_protocol.ads': '7ca9a947061fce2a3278ab064ede1f8c2edad77fb3ecbdb68ef3f1cc41131eec', 'core/worldline-recovery_protocol_c_api.adb': 'b8921fc27ccca361edcb7b6477e3804c16cff2aa154fe279bc368d65f51ddf77', 'core/worldline-recovery_protocol_c_api.ads': '659e9b509e0350d58039f67ce3741cb01eff6a266b970b00bf56f601b550d413', 'core/worldline-recovery_protocol_wire.adb': '4716e4c67604bc3ebb236994a30a1f98a2f2684e99fa8a3dde6c6529c2c49d2b', 'core/worldline-recovery_protocol_wire.ads': '389d2fd4ad5a625f1ac5274da214c9b8e953f261882b300fbbfa96d17b5c1cd4', 'core/worldline_core.gpr': 'f1a6492bceff785f35dec5f30d3d5470fe7f439b5a85c02ddcbb3b4b44a47436', 'recovery-protocol-tests/test_protocol.adb': '04a6b065ae31533e8dcb04b4661aedb467bc0c89a5613bb4fcec01b7734c0447', 'recovery-protocol-tests/recovery_protocol_tests.gpr': '2ab0cb616d8ff722655c92a6767e3c4bf8feb94707b5330f881601d8eb054d40'})

_protected_protocol_original_export_problems = export_problems

def export_problems(root: Path) -> list[str]:
    # Preserve every established export/control before checking new bindings.
    problems = _protected_protocol_original_export_problems(root)
    if problems:
        return problems
    typed_layout = _uses_typed_export_layout(normalized_ada((root / 'core/worldline-c_api.ads').read_bytes()))
    text = normalized_ada((root / 'core/worldline-recovery_protocol_c_api.ads').read_bytes())
    for symbol in ('wl_recovery_protocol_version_v1', 'wl_recovery_protocol_layout_v1',
                   'wl_recovery_protocol_decide_v1'):
        if typed_layout and symbol == 'wl_recovery_protocol_decide_v1':
            continue  # Exact public profile and whole typed transport already checked.
        if text.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'protected recovery protocol export binding differs: {symbol}')
    return problems

# Complete-chain source additions; no old proof evidence transfers.
REQUIRED_PROVED += ['Worldline.Chain_Authority.Link', 'Worldline.Chain_Authority.Present', 'Worldline.Chain_Authority.Prefix_Reference', 'Worldline.Chain_Authority.Replay_Reference', 'Worldline.Chain_Authority.Replay', 'Worldline.Chain_Authority_Wire.Well_Formed', 'Worldline.Chain_Authority_Wire.Decode', 'Worldline.Chain_Authority_Wire.Decide']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/worldline-chain_authority.adb', 'core/worldline-chain_authority.ads', 'core/worldline-chain_authority_c_api.adb', 'core/worldline-chain_authority_c_api.ads', 'core/worldline-chain_authority_wire.adb', 'core/worldline-chain_authority_wire.ads'])
CONTRACT_PINS.update({'core/worldline-chain_authority.adb': 'ad10d252025b8d46dba16b99031b733f40d13d29d391a703bdf8b3b193c7166d', 'core/worldline-chain_authority.ads': '8aa61e6419fc3c2f8f76d5e0e279d1d338c1c6615b2ab7bc5ac8a8d408a8edff', 'core/worldline-chain_authority_c_api.adb': 'f3a7c76c681bf8e82960929a3c30659c1926dba38d71bd59f96abaa875c5326a', 'core/worldline-chain_authority_c_api.ads': 'c44a9c3ddd2dce171d5ff88c2da981b36afec678db7e830e24fa60699b1784b0', 'core/worldline-chain_authority_wire.adb': '9ff2355dbebbf8192b78e21adb225bb8405968612a1c8cc6e6778f27c42961e4', 'core/worldline-chain_authority_wire.ads': '7baf22c73d65bb6ba5dbe5386453da06a8b600f8a81e58931bf9c6377bada4f1'})
_chain_predecessor_export_problems = export_problems
def export_problems(root: Path) -> list[str]:
    problems = _chain_predecessor_export_problems(root)
    if problems:
        return problems
    typed_layout = _uses_typed_export_layout(normalized_ada((root / 'core/worldline-c_api.ads').read_bytes()))
    if typed_layout:
        # Predecessor verified all exact wrapper/typed-unit identities, including
        # Read_Anchors, every Read_Row/Decode, Write_Result(W.Decide(Owned,H)) and
        # the C_API status-zero-only publication. No call-substring substitution.
        return problems
    spec = (root / 'core/worldline-chain_authority_c_api.ads').read_text()
    body = (root / 'core/worldline-chain_authority_c_api.adb').read_text()
    if spec.count('External_Name => "wl_chain_authority_replay_v1"') != 1 or 'Result_At (Output).all := W.Decide (Owned, H);' not in body:
        problems.append('complete-chain native export is not bound to the selected full-row wire decision')
    return problems

# Complete owner-operation component; all original rules/callers stay required.
REQUIRED_PROVED += ['Worldline.Owner_Transitions.Present', 'Worldline.Owner_Transitions.Same', 'Worldline.Owner_Transitions.Cursor_Present', 'Worldline.Owner_Transitions.Same_Cursor', 'Worldline.Owner_Transitions.Common_Present', 'Worldline.Owner_Transitions.Common_Valid', 'Worldline.Owner_Transitions.Latest_Failed_Head', 'Worldline.Owner_Transitions.Query_For', 'Worldline.Owner_Transitions.Retry_Holds', 'Worldline.Owner_Transitions.Retry_Reference', 'Worldline.Owner_Transitions.Reference', 'Worldline.Owner_Transitions.Authorize', 'Worldline.Owner_Transitions_Wire.Identity_Valid', 'Worldline.Owner_Transitions_Wire.Cursor_Valid', 'Worldline.Owner_Transitions_Wire.Row_Valid', 'Worldline.Owner_Transitions_Wire.Grant_Valid', 'Worldline.Owner_Transitions_Wire.Request_Valid', 'Worldline.Owner_Transitions_Wire.Well_Formed', 'Worldline.Owner_Transitions_Wire.Span', 'Worldline.Owner_Transitions_Wire.Identity', 'Worldline.Owner_Transitions_Wire.Epoch', 'Worldline.Owner_Transitions_Wire.Cursor', 'Worldline.Owner_Transitions_Wire.Subject', 'Worldline.Owner_Transitions_Wire.Content', 'Worldline.Owner_Transitions_Wire.Requirement', 'Worldline.Owner_Transitions_Wire.Run', 'Worldline.Owner_Transitions_Wire.Row', 'Worldline.Owner_Transitions_Wire.Grant', 'Worldline.Owner_Transitions_Wire.Decode', 'Worldline.Owner_Transitions_Wire.Rows', 'Worldline.Owner_Transitions_Wire.Decide']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/worldline-owner_transitions.adb', 'core/worldline-owner_transitions.ads', 'core/worldline-owner_transitions_wire.adb', 'core/worldline-owner_transitions_wire.ads'])
CONTRACT_PINS.update({'core/worldline-owner_transitions.adb': 'b3049b6773bed28e252c1faaa6926e6e71c3ca51a40701ad2293aa0474d8556f', 'core/worldline-owner_transitions.ads': '0d7692119a7eb400f06d1bc8b3792f9f6925f58096d23b059d8f6ea5a49000b3', 'core/worldline-owner_transitions_wire.adb': '4e340e98c08587cfdc891e7f46b44febc194b81bc5bebfdd265d751434884319', 'core/worldline-owner_transitions_wire.ads': '8867a739ddc2b22c3d73c8908a0be7bb8ecd1410bbe9232776499aa57837f814'})
_owner_predecessor_export_problems = export_problems
def export_problems(root: Path) -> list[str]:
    problems = _owner_predecessor_export_problems(root)
    if problems:
        return problems
    spec = (root / 'core/worldline-c_api.ads').read_text()
    body = (root / 'core/worldline-c_api.adb').read_text()
    exports = ('wl_owner_transition_version_v1','wl_owner_transition_layout_v1','wl_owner_transition_authorize_v1')
    if any(spec.count('External_Name => "' + name + '"') != 1 for name in exports) or 'Owner_Wire.Decide (A, H, F, Final_Present, Raw)' not in body:
        problems.append('complete owner-operation ABI is not bound to the full native wire relation')
    return problems

# Explicit complete source composition; every original proof condition stays required.
REQUIRED_PROVED += ['Resource_Run_Ledger.Id_Valid', 'Resource_Run_Ledger.Same', 'Resource_Run_Ledger.Optional_Same', 'Resource_Run_Ledger.Same_Epoch', 'Resource_Run_Ledger.Context_Valid', 'Resource_Run_Ledger.Same_Context', 'Resource_Run_Ledger.Binding_Valid', 'Resource_Run_Ledger.Same_Binding', 'Resource_Run_Ledger.Has_Effect', 'Resource_Run_Ledger.Counted', 'Resource_Run_Ledger.Row_Valid', 'Resource_Run_Ledger.Same_Row', 'Resource_Run_Ledger.Exact_Value', 'Resource_Run_Ledger.Amount_Reference', 'Resource_Run_Ledger.Amount', 'Resource_Run_Ledger.Included', 'Resource_Run_Ledger.Sum_Reference', 'Resource_Run_Ledger.Sum', 'Resource_Run_Ledger.Cgroup_Inside', 'Resource_Run_Ledger.Shape', 'Resource_Run_Ledger.Conserved_Reference', 'Resource_Run_Ledger.Conserved', 'Resource_Run_Ledger.Parent_Supports', 'Resource_Run_Ledger.Contained_Reference', 'Resource_Run_Ledger.Contained', 'Resource_Run_Ledger.Native_Valid', 'Resource_Run_Ledger.Changed_Row_Allowed', 'Resource_Run_Ledger.Decision_Reference', 'Resource_Run_Ledger.Check', 'Resource_Run_Ledger_Wire.Well_Formed', 'Resource_Run_Ledger_Wire.Decode', 'Resource_Run_Ledger_Wire.Decode_Rows', 'Resource_Run_Ledger_Wire.Decode_Native', 'Resource_Run_Ledger_Wire.Decide']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/resource_run_ledger.adb', 'core/resource_run_ledger.ads', 'core/resource_run_ledger_c_api.adb', 'core/resource_run_ledger_c_api.ads', 'core/resource_run_ledger_wire.adb', 'core/resource_run_ledger_wire.ads', 'core/worldline-recovery_protocol.adb', 'core/worldline-recovery_protocol.ads', 'core/worldline-recovery_protocol_c_api.adb', 'core/worldline-recovery_protocol_c_api.ads', 'core/worldline-recovery_protocol_wire.adb', 'core/worldline-recovery_protocol_wire.ads'])
CONTRACT_PINS.update({'artifact-tests/canonical_artifact_tests.gpr': 'bce2824cc8181edb5f1e9d5b9c0a391d70d68302b9f717ae44f87a0cd4a1ea05', 'artifact-tests/test_canonical_artifacts.adb': '43137b6f14b3c71b87de8f09c957e95d29a7d44dab5c67fc92698be12c50b8f1', 'core/attest/attest-sha256.ads': 'b5b299d3559e8a083d1edbbaefc96f76f73a0c4e0e6d2dfdcfb6d3fc0c4d7bec', 'core/attest/attest.ads': 'bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587', 'core/attest_sha256.gpr': 'f75c901810d0227f9b1331929e06a4405eb83c82385e5cab2be4f4e86daf8822', 'core/canonical_artifacts.adb': '349e185ee8e821142f58a293c91874cffe1cf55b1699dea5217c26478d4bc428', 'core/canonical_artifacts.ads': 'de5ecd7a705bd054497ac3594945b265d9ba3b34a332cd24f9849b2388b10f34', 'core/evaluation_completion.adb': '0fdf0e0e700022ed9113d5a3efaee58316da12d1b77feec79d5779e9a43fcd42', 'core/evaluation_completion.ads': '0ced82cb877e8e9057b3b1ec796c72aee615bc4c67e95d6feecd168cda33a03b', 'core/evaluation_completion_c.adb': '4eb799e6d6de99df449c2b20f7368a9602ed015b47ebff9f584f4eee8119b900', 'core/evaluation_completion_c.ads': '26a48384ae56b3590383c6ed9d408bad7dd55426cfa35402eb86d6921be34a73', 'core/evaluation_completion_roster.adb': 'f52e2b9d4a909b3c2b616e92aaf7b87ce4ddb8a6e8b34ea99068915dc9bb253a', 'core/evaluation_completion_roster.ads': '5af5ec8259073ad74444b5a4596b2a4b05e568c7d26739b9210e9b4616a2a2a3', 'core/evaluation_epoch.adb': 'ee9b16847dfb3dedce58a9b6539e2568816b745d2bd0cb808a36362072df9e1b', 'core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'core/evaluation_finalization.adb': '3e18a007d6d6d49f7bd6713d246727d27b792a517934cbadba21b0b8db1c3a95', 'core/evaluation_finalization.ads': 'e0e85059342002b01291063b24c1a50ca2cfd94d0202e28e72806aefec332e5d', 'core/evaluation_finalization_c.adb': 'e16932c56e25577c1782a927c60ad0cab68e3b503b11541a187cb5787bac5ac3', 'core/evaluation_finalization_c.ads': '28eb6e663262e471f71a97acf44c7683ba9c1f0979dcc88e1981a4395ea0f3c8', 'core/evaluation_history.adb': '74a24e09ac21e8900167db0f25b43cfd33d000eb52922653133a8e631a911c3f', 'core/evaluation_history.ads': 'e58eea740afa7f385a386ad97ad78380eb61ccac35d7669f14768dd4ac30cc3a', 'core/evaluation_pending_v2.adb': 'd8864beff6356c688f3ed26c84d27e6d0e315c423e150ee257e45df71bad3a66', 'core/evaluation_pending_v2.ads': '1e20de75c125ff20b5ad5750466430e959fb104b27f905403e38a35eb01f8321', 'core/evaluation_raw_roster.adb': '51b238fc3489523bbc10acca6ee47dd274e391fb9491af8f65943b04396b4569', 'core/evaluation_raw_roster.ads': '1fcc5358aad66d61571552e80be7572fc47cb21fc8b4ab2dad2005812cd9664b', 'core/resource_admission.adb': '0da682e7cd0aa85daea88a9f36926fa213240b9273cd7015108f95f4f48ee63c', 'core/resource_admission.ads': '2d93c087e980ec50ce77a21efdeb4c2d3a96e503493e55c0a9cbbb27e80381f2', 'core/resource_ledger.adb': '8b4e8022b8e938de425b07389bc8e243ff974bcd6cdbb21baf5a668b7735bd7e', 'core/resource_ledger.ads': '775e6daf668c1f3916b22d641a2c983d96bfa6dc9a7707709e1964a381ab950b', 'core/resource_quantities.adb': '155aa25399f30cb4837d589ae87c24ff8e2589dadbf27be06b9995bde3b6233b', 'core/resource_quantities.ads': 'c39661155528ed7388b63277e034ac3bbbceba239119e4d7700218e905aeac65', 'core/resource_reservation_lifecycle.adb': '3cf6bbe8dfef85f485be16eb9185768ace28ddc6a3ea5bfe0cd0aa26dd8aef41', 'core/resource_reservation_lifecycle.ads': '8e3c85334abc8ff747e6f468bea29f04196c3c11cffa10a68207b96c8b3e0400', 'core/resource_reservation_transition.adb': 'f13ad8e1ef22ee22b3a6902b5c6945b0dcbb64d1385e28e8ad9d77fa083d0e86', 'core/resource_reservation_transition.ads': '34d4b6d554999fc3366b78d0740be905c21e0d3c0c20b6fb96fa82691674a9d2', 'core/resource_run_ledger.adb': 'c64d4369b0a58ac4290bbddb9390d2953406b8d44eade1ebc5de672635c560b1', 'core/resource_run_ledger.ads': '3a58b0c3721e0d7824f3ddd0674e3ef0bc0c485a5d313b33badc44be97c2fb5c', 'core/resource_run_ledger_c_api.adb': '71defbaa27c849a11e7628d1323ba0871b8e2b606c528dbf0d6e696caedb2892', 'core/resource_run_ledger_c_api.ads': 'e095a573d30b0c3aabe63a23fd13dca59e9a664c381c8e306863b9b152704e1d', 'core/resource_run_ledger_wire.adb': 'c2feb75a7b3616968802469e7df304afcc9af6ac113a02222796487d0a6df0b3', 'core/resource_run_ledger_wire.ads': 'b09d4e07df8652f8f87b2a6526f0fa26875253ea1dc8909bbec6b330d6d02eed', 'core/worldline-ancestry.ads': '718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db', 'core/worldline-c_api.adb': '64a839d076a4e52d8fb65c599a91f9eb0812adef30f8e48a4e80669f56557f52', 'core/worldline-c_api.ads': '1da0afffd071cb78449216a359b362f9d31e6cae22e9d02c09cb19bfce097efe', 'core/worldline-causal_graph.adb': 'e3239b7770a185f4eef90d838c803a64b128e84380e3af27513867632ff3c121', 'core/worldline-causal_graph.ads': '4c1db06549310c2dd93c26b9e109dd832a0f43390fe7ece37dbab06934b78ae7', 'core/worldline-chain_authority.adb': 'ad10d252025b8d46dba16b99031b733f40d13d29d391a703bdf8b3b193c7166d', 'core/worldline-chain_authority.ads': '8aa61e6419fc3c2f8f76d5e0e279d1d338c1c6615b2ab7bc5ac8a8d408a8edff', 'core/worldline-chain_authority_c_api.adb': 'f3a7c76c681bf8e82960929a3c30659c1926dba38d71bd59f96abaa875c5326a', 'core/worldline-chain_authority_c_api.ads': 'c44a9c3ddd2dce171d5ff88c2da981b36afec678db7e830e24fa60699b1784b0', 'core/worldline-chain_authority_wire.adb': '9ff2355dbebbf8192b78e21adb225bb8405968612a1c8cc6e6778f27c42961e4', 'core/worldline-chain_authority_wire.ads': '7baf22c73d65bb6ba5dbe5386453da06a8b600f8a81e58931bf9c6377bada4f1', 'core/worldline-collapse.ads': '94ef49a258a46363eea81d44e168ce4e7cc618fdf128e916e92e447f2ffe32e2', 'core/worldline-collapse_wire.ads': '48270be156ee3f1c7d7f6215917c9b8026ac5346c45064cf7803950c137ddd76', 'core/worldline-evaluation.ads': '06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e', 'core/worldline-evaluation_authority.adb': '45a92dcf5d9950d333e5c6394370ef99c99bc53dadfd9dbdcf81aab50a1f3954', 'core/worldline-evaluation_authority.ads': 'ddf03fabb55ffcbf702dbaa066ad85a9f89a5b0e9600473b9b6824a2d1db767f', 'core/worldline-evaluation_report_facts.adb': 'ffdc1629f8eaef1ec4ab1bbc4fc988f2f1546dd8b5013ec4635888d77f8240fb', 'core/worldline-evaluation_report_facts.ads': 'f8bfee03303776b2825662bb1ce394fdf3c3e6acf3e7b1084500e50eba430f82', 'core/worldline-evaluation_report_wire.adb': '19ed101a83a9a9350a660cd7693a8be7ffee86557fa6d58e7959a0ae9973ff78', 'core/worldline-evaluation_report_wire.ads': 'a58347985c4242421c4114ecf61ddaf6f84229e62ab2114cd0947b7feee29b19', 'core/worldline-evaluation_v2.adb': '2fc57758a66ac2c7aa9ef6e108fdcbf93b1b286fd64b6620d8bca54ce32312eb', 'core/worldline-evaluation_v2.ads': '8e1f18244b924a7c9c05c67fdf785491a910c9f7c59966381b38962c2f68a72c', 'core/worldline-evaluation_wire.adb': '30696c9e2b4be84aad47d406864213a176f494e07dbed6f6907efe601d3be530', 'core/worldline-evaluation_wire.ads': '8b190a32f057a30a700e3331bd72aa2cfc18c5d6f3540b824756197f09077c7a', 'core/worldline-identities.ads': 'ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21', 'core/worldline-owner_transitions.adb': 'b3049b6773bed28e252c1faaa6926e6e71c3ca51a40701ad2293aa0474d8556f', 'core/worldline-owner_transitions.ads': '0d7692119a7eb400f06d1bc8b3792f9f6925f58096d23b059d8f6ea5a49000b3', 'core/worldline-owner_transitions_wire.adb': '4e340e98c08587cfdc891e7f46b44febc194b81bc5bebfdd265d751434884319', 'core/worldline-owner_transitions_wire.ads': '8867a739ddc2b22c3d73c8908a0be7bb8ecd1410bbe9232776499aa57837f814', 'core/worldline-receipts.adb': '8b30e5567ec7a86962f9cea3cd67b6d07194dc726e70b025bc2f97a406767829', 'core/worldline-receipts.ads': 'a354588d79bc6d01973afcf10b9b31a08d996e2056a1bad8db05e97fe7636dd6', 'core/worldline-recovery.adb': '75763d6eb35c647df523a728c6939e21cda6c3d7b44ba54fb2a4a917f3149e24', 'core/worldline-recovery.ads': 'b2eff79e29cd18c5a69672e3c6063faa120345d19a3f4cc76cf8ae31a69df7fc', 'core/worldline-recovery_authorization.adb': 'd90b75ec516fbf8ddb0f0bf40ee39297e70eebc001d4edad6b0142c7da092e7d', 'core/worldline-recovery_authorization.ads': '3b95bc25da8343b9d0c4cd6e133614bb59cdce65740142d9c2d2ed072e62dec6', 'core/worldline-recovery_authorization_c_api.adb': 'c9ccade8b28286a2166130c0057ca3187a7465a8c1521c523fda3429b004282c', 'core/worldline-recovery_authorization_c_api.ads': '88a156f3749251a4cff6393739ce7b738e82fb9d625c71774489f99430914f34', 'core/worldline-recovery_authorization_v3.adb': '21536d8595e0d6d14764b56309eb2f88d28bd88fc47b6fe9c16f915c98ed63dd', 'core/worldline-recovery_authorization_v3.ads': '8b3f3c7477c461dadceba33ab421cf54d4c77129e2875768346d93c91f3fdd51', 'core/worldline-recovery_authorization_v3_c_api.adb': '9a90152c2f15a615f61dbe3d96aa520f48ce541a0f8b9843dbb51553aef19ac4', 'core/worldline-recovery_authorization_v3_c_api.ads': '06832ec39eec8162227eadb2f158d7ca53ec6af0d796693d0701b32d430cf6c9', 'core/worldline-recovery_authorization_v3_wire.adb': '5df8bd9bcd6842aaf033bde67edd121e6d9e0bdfd6f29158f0f8b1a57fd36bc6', 'core/worldline-recovery_authorization_v3_wire.ads': '30a49ffee1fecf33fe798e524cda06f73a8a2164ffe92c2bce8a10155a45f90e', 'core/worldline-recovery_authorization_wire.adb': 'e0c1054dd20e34bf1ddbcaefd9665c7588fc4683c8dad1a91351c89597928f62', 'core/worldline-recovery_authorization_wire.ads': 'a6b453f40b2eee2d860008ecb11b9720f6be2a5be5c1aca52a91f264c40d687c', 'core/worldline-recovery_protocol.adb': '1188891c1663c1c0c3ec47d304af9aaf5b14b1f9a74cff6ad771d47d06f5f573', 'core/worldline-recovery_protocol.ads': '7ca9a947061fce2a3278ab064ede1f8c2edad77fb3ecbdb68ef3f1cc41131eec', 'core/worldline-recovery_protocol_c_api.adb': 'b8921fc27ccca361edcb7b6477e3804c16cff2aa154fe279bc368d65f51ddf77', 'core/worldline-recovery_protocol_c_api.ads': '659e9b509e0350d58039f67ce3741cb01eff6a266b970b00bf56f601b550d413', 'core/worldline-recovery_protocol_wire.adb': '4716e4c67604bc3ebb236994a30a1f98a2f2684e99fa8a3dde6c6529c2c49d2b', 'core/worldline-recovery_protocol_wire.ads': '389d2fd4ad5a625f1ac5274da214c9b8e953f261882b300fbbfa96d17b5c1cd4', 'core/worldline-resource_wire.adb': 'ec1ea00cf321f841aafcb874047c48d1ff28363d29ea042c6703a60a2be32f80', 'core/worldline-resource_wire.ads': 'b0af3ef936e727ba9113430ebc29c2843124f82e584b3bb294dc23af2667ad75', 'core/worldline-resources.adb': '8b9836dcb1eb091316a6dc08deb303aebdb664dcab5bb26e023c15e7a8ff8fb9', 'core/worldline-resources.ads': '7fdf97a76f11aeeecfcde00c0e5e2587fde0f3155983765d006026aac70d4530', 'core/worldline-transitions.ads': '5b9c8f89900d01eeb40818de6392e1f23f8e2606cba702dd06e72e4257406c27', 'core/worldline-world.ads': '3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5', 'core/worldline.ads': '6fc501e7d5e4927784d415e25c84339efd42a96358216c69825882deea3603e3', 'core/worldline_core.gpr': 'f1a6492bceff785f35dec5f30d3d5470fe7f439b5a85c02ddcbb3b4b44a47436', 'core/worldline_core_sources.gpr': 'ed7f3006aec84e5059b9163b0aa525ed829a256f2e418bb400e0291bb1434077', 'evaluation-authority-tests/evaluation_authority_tests.gpr': 'f9ba8e8e3b9593454c25f74a5678599ebdf09afbf8510b119ebfa6f8820a98f4', 'evaluation-authority-tests/test_evaluation_authority.adb': '071e0f859f92ac1576f95dc1c6e6f89df84c59edb304b36c3e15f0a887e98730', 'evaluation-wire-tests/evaluation_wire_tests.gpr': '8fde6733c882c9be99a7fbcdce0c6ba0a8eca138a4b68e65ec77efdc84160d89', 'pending-component/core/evaluation_epoch.adb': '76fa1977a41b3cdef9ee15972a1970db67771ec2f5bf0dab2cada0088679f363', 'pending-component/core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'pending-component/core/resource_quantities.adb': '48656286ffabeb9cac8436cafa2fe3bac2bb91a231ed17178966660c93f34206', 'pending-component/core/resource_quantities.ads': 'ff725d00a0be90fa2ca4632e9f48878f5f58199cbfacf2a82bfa554f4cdfe63a', 'recovery-epoch-tests/recovery_epoch_tests.gpr': '600c9e1b3b3524f1419f2419a0e0925641a9dec1c822fb0b5ddb1e2afc9bc880', 'recovery-epoch-tests/test_epochs.adb': 'b134c380bb6990c55df7c21c590627585c57a8f0bbb99453a4d4c61913a68670', 'recovery-protocol-tests/recovery_protocol_tests.gpr': '2ab0cb616d8ff722655c92a6767e3c4bf8feb94707b5330f881601d8eb054d40', 'recovery-protocol-tests/test_protocol.adb': '04a6b065ae31533e8dcb04b4661aedb467bc0c89a5613bb4fcec01b7734c0447', 'tests/worldline_tests.gpr': '0cf4fdd19da37ad197a3ea063fdbb259a7400d4e3865e40088fd78ee6fb7560d', 'worldline.gpr': 'edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021'})

# Complete additive owner audit, subject projection and collapse conjunction.
REQUIRED_PROVED += ['Worldline.Owner_Retry_Audit.Query_For', 'Worldline.Owner_Retry_Audit.Same_Row', 'Worldline.Owner_Retry_Audit.Same_Finalization', 'Worldline.Owner_Retry_Audit.Same_Prefix', 'Worldline.Owner_Retry_Audit.Same_Grant', 'Worldline.Owner_Retry_Audit.Receipt_Holds', 'Worldline.Owner_Retry_Audit.Attempt_Holds', 'Worldline.Owner_Retry_Audit.Binding_Holds', 'Worldline.Owner_Retry_Audit.Before_Closed', 'Worldline.Owner_Retry_Audit.Holds', 'Worldline.Owner_Retry_Audit.Reference', 'Worldline.Owner_Retry_Audit.Decide', 'Worldline.Owner_Retry_Audit_Wire.Valid', 'Worldline.Owner_Retry_Audit_Wire.Decode', 'Worldline.Owner_Retry_Audit_Wire.Well_Formed', 'Worldline.Owner_Retry_Audit_Wire.Final', 'Worldline.Owner_Retry_Audit_Wire.Decide', 'Worldline.Owner_Conjunction.Nibble', 'Worldline.Owner_Conjunction.Hash_Holds', 'Worldline.Owner_Conjunction.Scope_Holds', 'Worldline.Owner_Conjunction.Original_Scope_Holds', 'Worldline.Owner_Conjunction.Adopt_Holds', 'Worldline.Owner_Conjunction.Checkpoint_Holds', 'Worldline.Owner_Conjunction.Checkpoint_Reference', 'Worldline.Owner_Conjunction.Authorize_Checkpoint', 'Worldline.Owner_Conjunction.Retry_Holds', 'Worldline.Owner_Conjunction.Retry_Reference', 'Worldline.Owner_Conjunction.Authorize_Retry', 'Worldline.Owner_Conjunction.Adopt_Receipt_Holds', 'Worldline.Owner_Conjunction.Adopt_Receipt_Reference', 'Worldline.Owner_Conjunction.Authorize_Adopt_Receipt', 'Worldline.Owner_Conjunction_Wire.Scope_Valid', 'Worldline.Owner_Conjunction_Wire.Scope', 'Worldline.Owner_Conjunction_Wire.Checkpoint_Reference', 'Worldline.Owner_Conjunction_Wire.Authorize_Checkpoint', 'Worldline.Owner_Conjunction_Wire.Retry_Reference', 'Worldline.Owner_Conjunction_Wire.Authorize_Retry', 'Worldline.Owner_Conjunction_Wire.Adopt_Receipt_Reference', 'Worldline.Owner_Conjunction_Wire.Authorize_Adopt_Receipt', 'Worldline.Owner_Subject_Projection.Feed', 'Worldline.Owner_Subject_Projection.Feed_String', 'Worldline.Owner_Subject_Projection.UTF8_Valid', 'Worldline.Owner_Subject_Projection.Quoted', 'Worldline.Owner_Subject_Projection.Reference', 'Worldline.Owner_Subject_Projection.Project', 'Worldline.Owner_Subject_Projection.Matches']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/worldline-owner_retry_audit.ads', 'core/worldline-owner_retry_audit.adb', 'core/worldline-owner_retry_audit_wire.ads', 'core/worldline-owner_retry_audit_wire.adb', 'core/worldline-owner_conjunction.ads', 'core/worldline-owner_conjunction.adb', 'core/worldline-owner_conjunction_wire.ads', 'core/worldline-owner_conjunction_wire.adb', 'core/worldline-owner_subject_projection.ads', 'core/worldline-owner_subject_projection.adb'])
CONTRACT_PINS.update({'core/worldline-owner_retry_audit.ads': 'f10e8a5758de157d40ab487c2b5071232cc8ede3b0984b36e75e922dff5b49e0', 'core/worldline-owner_retry_audit.adb': 'd444de903bc184300bbfd6e95348f4307827b7ad3948e4fe77c091daec52b5bd', 'core/worldline-owner_retry_audit_wire.ads': '60772578c6f02b53ea7b4d5614dde93f4e6d02e073847932c4647853d205f979', 'core/worldline-owner_retry_audit_wire.adb': 'ffeb183989406733268c9d25cac7b2501f1fb28bcf36af622ca1391e0bc9bd70', 'core/worldline-owner_conjunction.ads': '62559ebaa5c94a88435d44333ac61aede278af67813f3ab7ac72d27bd86ec89d', 'core/worldline-owner_conjunction.adb': '9d6f3f09c955a8612747f088a14802c5004a9a656009389e11254d6d623f3c32', 'core/worldline-owner_conjunction_wire.ads': 'a078f33e659fcb0c0eac74e63777425181bd5e2865566abfb79f36fc34aa510d', 'core/worldline-owner_conjunction_wire.adb': '8aedcbc566fc59ca8a600a6410199ef8ec31b3fbffb655e856e679007f0fc7c7', 'core/worldline-owner_subject_projection.ads': '2aa7d9d7208c340ae46ac36a4bf74d0dfe1ce2f53fdae435f95fcdc39479b7f7', 'core/worldline-owner_subject_projection.adb': 'abcf67952cd84158f7a536c8315402ab6a7cb3a9f32ba13e7587ad1d0119df72', 'core/worldline-c_api.ads': '1da0afffd071cb78449216a359b362f9d31e6cae22e9d02c09cb19bfce097efe', 'core/worldline-c_api.adb': '64a839d076a4e52d8fb65c599a91f9eb0812adef30f8e48a4e80669f56557f52', 'core/worldline_core.gpr': 'f1a6492bceff785f35dec5f30d3d5470fe7f439b5a85c02ddcbb3b4b44a47436'})
_owner_audit_predecessor_export_problems = export_problems
def export_problems(root: Path) -> list[str]:
    problems = _owner_audit_predecessor_export_problems(root)
    if problems:
        return problems
    spec = normalized_ada((root / 'core/worldline-c_api.ads').read_bytes())
    body = normalized_ada((root / 'core/worldline-c_api.adb').read_bytes())
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
CONTRACT_PINS.update({'artifact-tests/canonical_artifact_tests.gpr': 'bce2824cc8181edb5f1e9d5b9c0a391d70d68302b9f717ae44f87a0cd4a1ea05', 'artifact-tests/test_canonical_artifacts.adb': '43137b6f14b3c71b87de8f09c957e95d29a7d44dab5c67fc92698be12c50b8f1', 'core/attest/attest-sha256.ads': 'b5b299d3559e8a083d1edbbaefc96f76f73a0c4e0e6d2dfdcfb6d3fc0c4d7bec', 'core/attest/attest.ads': 'bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587', 'core/attest_sha256.gpr': 'f75c901810d0227f9b1331929e06a4405eb83c82385e5cab2be4f4e86daf8822', 'core/canonical_artifacts.adb': '349e185ee8e821142f58a293c91874cffe1cf55b1699dea5217c26478d4bc428', 'core/canonical_artifacts.ads': 'de5ecd7a705bd054497ac3594945b265d9ba3b34a332cd24f9849b2388b10f34', 'core/evaluation_completion.adb': '0fdf0e0e700022ed9113d5a3efaee58316da12d1b77feec79d5779e9a43fcd42', 'core/evaluation_completion.ads': '0ced82cb877e8e9057b3b1ec796c72aee615bc4c67e95d6feecd168cda33a03b', 'core/evaluation_completion_c.adb': '4eb799e6d6de99df449c2b20f7368a9602ed015b47ebff9f584f4eee8119b900', 'core/evaluation_completion_c.ads': '26a48384ae56b3590383c6ed9d408bad7dd55426cfa35402eb86d6921be34a73', 'core/evaluation_completion_roster.adb': 'f52e2b9d4a909b3c2b616e92aaf7b87ce4ddb8a6e8b34ea99068915dc9bb253a', 'core/evaluation_completion_roster.ads': '5af5ec8259073ad74444b5a4596b2a4b05e568c7d26739b9210e9b4616a2a2a3', 'core/evaluation_epoch.adb': 'ee9b16847dfb3dedce58a9b6539e2568816b745d2bd0cb808a36362072df9e1b', 'core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'core/evaluation_finalization.adb': '3e18a007d6d6d49f7bd6713d246727d27b792a517934cbadba21b0b8db1c3a95', 'core/evaluation_finalization.ads': 'e0e85059342002b01291063b24c1a50ca2cfd94d0202e28e72806aefec332e5d', 'core/evaluation_finalization_c.adb': 'e16932c56e25577c1782a927c60ad0cab68e3b503b11541a187cb5787bac5ac3', 'core/evaluation_finalization_c.ads': '28eb6e663262e471f71a97acf44c7683ba9c1f0979dcc88e1981a4395ea0f3c8', 'core/evaluation_history.adb': '74a24e09ac21e8900167db0f25b43cfd33d000eb52922653133a8e631a911c3f', 'core/evaluation_history.ads': 'e58eea740afa7f385a386ad97ad78380eb61ccac35d7669f14768dd4ac30cc3a', 'core/evaluation_pending_v2.adb': 'd8864beff6356c688f3ed26c84d27e6d0e315c423e150ee257e45df71bad3a66', 'core/evaluation_pending_v2.ads': '1e20de75c125ff20b5ad5750466430e959fb104b27f905403e38a35eb01f8321', 'core/evaluation_raw_roster.adb': '51b238fc3489523bbc10acca6ee47dd274e391fb9491af8f65943b04396b4569', 'core/evaluation_raw_roster.ads': '1fcc5358aad66d61571552e80be7572fc47cb21fc8b4ab2dad2005812cd9664b', 'core/resource_admission.adb': '0da682e7cd0aa85daea88a9f36926fa213240b9273cd7015108f95f4f48ee63c', 'core/resource_admission.ads': '2d93c087e980ec50ce77a21efdeb4c2d3a96e503493e55c0a9cbbb27e80381f2', 'core/resource_ledger.adb': '8b4e8022b8e938de425b07389bc8e243ff974bcd6cdbb21baf5a668b7735bd7e', 'core/resource_ledger.ads': '775e6daf668c1f3916b22d641a2c983d96bfa6dc9a7707709e1964a381ab950b', 'core/resource_quantities.adb': '155aa25399f30cb4837d589ae87c24ff8e2589dadbf27be06b9995bde3b6233b', 'core/resource_quantities.ads': 'c39661155528ed7388b63277e034ac3bbbceba239119e4d7700218e905aeac65', 'core/resource_reservation_lifecycle.adb': '3cf6bbe8dfef85f485be16eb9185768ace28ddc6a3ea5bfe0cd0aa26dd8aef41', 'core/resource_reservation_lifecycle.ads': '8e3c85334abc8ff747e6f468bea29f04196c3c11cffa10a68207b96c8b3e0400', 'core/resource_reservation_transition.adb': 'f13ad8e1ef22ee22b3a6902b5c6945b0dcbb64d1385e28e8ad9d77fa083d0e86', 'core/resource_reservation_transition.ads': '34d4b6d554999fc3366b78d0740be905c21e0d3c0c20b6fb96fa82691674a9d2', 'core/resource_run_ledger.adb': 'c64d4369b0a58ac4290bbddb9390d2953406b8d44eade1ebc5de672635c560b1', 'core/resource_run_ledger.ads': '3a58b0c3721e0d7824f3ddd0674e3ef0bc0c485a5d313b33badc44be97c2fb5c', 'core/resource_run_ledger_c_api.adb': '71defbaa27c849a11e7628d1323ba0871b8e2b606c528dbf0d6e696caedb2892', 'core/resource_run_ledger_c_api.ads': 'e095a573d30b0c3aabe63a23fd13dca59e9a664c381c8e306863b9b152704e1d', 'core/resource_run_ledger_wire.adb': 'c2feb75a7b3616968802469e7df304afcc9af6ac113a02222796487d0a6df0b3', 'core/resource_run_ledger_wire.ads': 'b09d4e07df8652f8f87b2a6526f0fa26875253ea1dc8909bbec6b330d6d02eed', 'core/worldline-ancestry.ads': '718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db', 'core/worldline-c_api.adb': '64a839d076a4e52d8fb65c599a91f9eb0812adef30f8e48a4e80669f56557f52', 'core/worldline-c_api.ads': '1da0afffd071cb78449216a359b362f9d31e6cae22e9d02c09cb19bfce097efe', 'core/worldline-causal_graph.adb': 'e3239b7770a185f4eef90d838c803a64b128e84380e3af27513867632ff3c121', 'core/worldline-causal_graph.ads': '4c1db06549310c2dd93c26b9e109dd832a0f43390fe7ece37dbab06934b78ae7', 'core/worldline-chain_authority.adb': 'ad10d252025b8d46dba16b99031b733f40d13d29d391a703bdf8b3b193c7166d', 'core/worldline-chain_authority.ads': '8aa61e6419fc3c2f8f76d5e0e279d1d338c1c6615b2ab7bc5ac8a8d408a8edff', 'core/worldline-chain_authority_c_api.adb': 'f3a7c76c681bf8e82960929a3c30659c1926dba38d71bd59f96abaa875c5326a', 'core/worldline-chain_authority_c_api.ads': 'c44a9c3ddd2dce171d5ff88c2da981b36afec678db7e830e24fa60699b1784b0', 'core/worldline-chain_authority_wire.adb': '9ff2355dbebbf8192b78e21adb225bb8405968612a1c8cc6e6778f27c42961e4', 'core/worldline-chain_authority_wire.ads': '7baf22c73d65bb6ba5dbe5386453da06a8b600f8a81e58931bf9c6377bada4f1', 'core/worldline-collapse.ads': '94ef49a258a46363eea81d44e168ce4e7cc618fdf128e916e92e447f2ffe32e2', 'core/worldline-collapse_wire.ads': '48270be156ee3f1c7d7f6215917c9b8026ac5346c45064cf7803950c137ddd76', 'core/worldline-evaluation.ads': '06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e', 'core/worldline-evaluation_authority.adb': '45a92dcf5d9950d333e5c6394370ef99c99bc53dadfd9dbdcf81aab50a1f3954', 'core/worldline-evaluation_authority.ads': 'ddf03fabb55ffcbf702dbaa066ad85a9f89a5b0e9600473b9b6824a2d1db767f', 'core/worldline-evaluation_report_facts.adb': 'ffdc1629f8eaef1ec4ab1bbc4fc988f2f1546dd8b5013ec4635888d77f8240fb', 'core/worldline-evaluation_report_facts.ads': 'f8bfee03303776b2825662bb1ce394fdf3c3e6acf3e7b1084500e50eba430f82', 'core/worldline-evaluation_report_wire.adb': '19ed101a83a9a9350a660cd7693a8be7ffee86557fa6d58e7959a0ae9973ff78', 'core/worldline-evaluation_report_wire.ads': 'a58347985c4242421c4114ecf61ddaf6f84229e62ab2114cd0947b7feee29b19', 'core/worldline-evaluation_v2.adb': '2fc57758a66ac2c7aa9ef6e108fdcbf93b1b286fd64b6620d8bca54ce32312eb', 'core/worldline-evaluation_v2.ads': '8e1f18244b924a7c9c05c67fdf785491a910c9f7c59966381b38962c2f68a72c', 'core/worldline-evaluation_wire.adb': '30696c9e2b4be84aad47d406864213a176f494e07dbed6f6907efe601d3be530', 'core/worldline-evaluation_wire.ads': '8b190a32f057a30a700e3331bd72aa2cfc18c5d6f3540b824756197f09077c7a', 'core/worldline-identities.ads': 'ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21', 'core/worldline-owner_conjunction.adb': '9d6f3f09c955a8612747f088a14802c5004a9a656009389e11254d6d623f3c32', 'core/worldline-owner_conjunction.ads': '62559ebaa5c94a88435d44333ac61aede278af67813f3ab7ac72d27bd86ec89d', 'core/worldline-owner_conjunction_wire.adb': '8aedcbc566fc59ca8a600a6410199ef8ec31b3fbffb655e856e679007f0fc7c7', 'core/worldline-owner_conjunction_wire.ads': 'a078f33e659fcb0c0eac74e63777425181bd5e2865566abfb79f36fc34aa510d', 'core/worldline-owner_retry_audit.adb': 'd444de903bc184300bbfd6e95348f4307827b7ad3948e4fe77c091daec52b5bd', 'core/worldline-owner_retry_audit.ads': 'f10e8a5758de157d40ab487c2b5071232cc8ede3b0984b36e75e922dff5b49e0', 'core/worldline-owner_retry_audit_wire.adb': 'ffeb183989406733268c9d25cac7b2501f1fb28bcf36af622ca1391e0bc9bd70', 'core/worldline-owner_retry_audit_wire.ads': '60772578c6f02b53ea7b4d5614dde93f4e6d02e073847932c4647853d205f979', 'core/worldline-owner_subject_projection.adb': 'abcf67952cd84158f7a536c8315402ab6a7cb3a9f32ba13e7587ad1d0119df72', 'core/worldline-owner_subject_projection.ads': '2aa7d9d7208c340ae46ac36a4bf74d0dfe1ce2f53fdae435f95fcdc39479b7f7', 'core/worldline-owner_transitions.adb': 'b3049b6773bed28e252c1faaa6926e6e71c3ca51a40701ad2293aa0474d8556f', 'core/worldline-owner_transitions.ads': '0d7692119a7eb400f06d1bc8b3792f9f6925f58096d23b059d8f6ea5a49000b3', 'core/worldline-owner_transitions_wire.adb': '4e340e98c08587cfdc891e7f46b44febc194b81bc5bebfdd265d751434884319', 'core/worldline-owner_transitions_wire.ads': '8867a739ddc2b22c3d73c8908a0be7bb8ecd1410bbe9232776499aa57837f814', 'core/worldline-receipts.adb': '8b30e5567ec7a86962f9cea3cd67b6d07194dc726e70b025bc2f97a406767829', 'core/worldline-receipts.ads': 'a354588d79bc6d01973afcf10b9b31a08d996e2056a1bad8db05e97fe7636dd6', 'core/worldline-recovery.adb': '75763d6eb35c647df523a728c6939e21cda6c3d7b44ba54fb2a4a917f3149e24', 'core/worldline-recovery.ads': 'b2eff79e29cd18c5a69672e3c6063faa120345d19a3f4cc76cf8ae31a69df7fc', 'core/worldline-recovery_authorization.adb': 'd90b75ec516fbf8ddb0f0bf40ee39297e70eebc001d4edad6b0142c7da092e7d', 'core/worldline-recovery_authorization.ads': '3b95bc25da8343b9d0c4cd6e133614bb59cdce65740142d9c2d2ed072e62dec6', 'core/worldline-recovery_authorization_c_api.adb': 'c9ccade8b28286a2166130c0057ca3187a7465a8c1521c523fda3429b004282c', 'core/worldline-recovery_authorization_c_api.ads': '88a156f3749251a4cff6393739ce7b738e82fb9d625c71774489f99430914f34', 'core/worldline-recovery_authorization_v3.adb': '21536d8595e0d6d14764b56309eb2f88d28bd88fc47b6fe9c16f915c98ed63dd', 'core/worldline-recovery_authorization_v3.ads': '8b3f3c7477c461dadceba33ab421cf54d4c77129e2875768346d93c91f3fdd51', 'core/worldline-recovery_authorization_v3_c_api.adb': '9a90152c2f15a615f61dbe3d96aa520f48ce541a0f8b9843dbb51553aef19ac4', 'core/worldline-recovery_authorization_v3_c_api.ads': '06832ec39eec8162227eadb2f158d7ca53ec6af0d796693d0701b32d430cf6c9', 'core/worldline-recovery_authorization_v3_wire.adb': '5df8bd9bcd6842aaf033bde67edd121e6d9e0bdfd6f29158f0f8b1a57fd36bc6', 'core/worldline-recovery_authorization_v3_wire.ads': '30a49ffee1fecf33fe798e524cda06f73a8a2164ffe92c2bce8a10155a45f90e', 'core/worldline-recovery_authorization_wire.adb': 'e0c1054dd20e34bf1ddbcaefd9665c7588fc4683c8dad1a91351c89597928f62', 'core/worldline-recovery_authorization_wire.ads': 'a6b453f40b2eee2d860008ecb11b9720f6be2a5be5c1aca52a91f264c40d687c', 'core/worldline-recovery_protocol.adb': '1188891c1663c1c0c3ec47d304af9aaf5b14b1f9a74cff6ad771d47d06f5f573', 'core/worldline-recovery_protocol.ads': '7ca9a947061fce2a3278ab064ede1f8c2edad77fb3ecbdb68ef3f1cc41131eec', 'core/worldline-recovery_protocol_c_api.adb': 'b8921fc27ccca361edcb7b6477e3804c16cff2aa154fe279bc368d65f51ddf77', 'core/worldline-recovery_protocol_c_api.ads': '659e9b509e0350d58039f67ce3741cb01eff6a266b970b00bf56f601b550d413', 'core/worldline-recovery_protocol_wire.adb': '4716e4c67604bc3ebb236994a30a1f98a2f2684e99fa8a3dde6c6529c2c49d2b', 'core/worldline-recovery_protocol_wire.ads': '389d2fd4ad5a625f1ac5274da214c9b8e953f261882b300fbbfa96d17b5c1cd4', 'core/worldline-resource_wire.adb': 'ec1ea00cf321f841aafcb874047c48d1ff28363d29ea042c6703a60a2be32f80', 'core/worldline-resource_wire.ads': 'b0af3ef936e727ba9113430ebc29c2843124f82e584b3bb294dc23af2667ad75', 'core/worldline-resources.adb': '8b9836dcb1eb091316a6dc08deb303aebdb664dcab5bb26e023c15e7a8ff8fb9', 'core/worldline-resources.ads': '7fdf97a76f11aeeecfcde00c0e5e2587fde0f3155983765d006026aac70d4530', 'core/worldline-transitions.ads': '5b9c8f89900d01eeb40818de6392e1f23f8e2606cba702dd06e72e4257406c27', 'core/worldline-world.ads': '3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5', 'core/worldline.ads': '6fc501e7d5e4927784d415e25c84339efd42a96358216c69825882deea3603e3', 'core/worldline_core.gpr': 'f1a6492bceff785f35dec5f30d3d5470fe7f439b5a85c02ddcbb3b4b44a47436', 'core/worldline_core_sources.gpr': 'ed7f3006aec84e5059b9163b0aa525ed829a256f2e418bb400e0291bb1434077', 'evaluation-authority-tests/evaluation_authority_tests.gpr': 'f9ba8e8e3b9593454c25f74a5678599ebdf09afbf8510b119ebfa6f8820a98f4', 'evaluation-authority-tests/test_evaluation_authority.adb': '071e0f859f92ac1576f95dc1c6e6f89df84c59edb304b36c3e15f0a887e98730', 'evaluation-wire-tests/evaluation_wire_tests.gpr': '8fde6733c882c9be99a7fbcdce0c6ba0a8eca138a4b68e65ec77efdc84160d89', 'pending-component/core/evaluation_epoch.adb': '76fa1977a41b3cdef9ee15972a1970db67771ec2f5bf0dab2cada0088679f363', 'pending-component/core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'pending-component/core/resource_quantities.adb': '48656286ffabeb9cac8436cafa2fe3bac2bb91a231ed17178966660c93f34206', 'pending-component/core/resource_quantities.ads': 'ff725d00a0be90fa2ca4632e9f48878f5f58199cbfacf2a82bfa554f4cdfe63a', 'recovery-epoch-tests/recovery_epoch_tests.gpr': '600c9e1b3b3524f1419f2419a0e0925641a9dec1c822fb0b5ddb1e2afc9bc880', 'recovery-epoch-tests/test_epochs.adb': 'b134c380bb6990c55df7c21c590627585c57a8f0bbb99453a4d4c61913a68670', 'recovery-protocol-tests/recovery_protocol_tests.gpr': '2ab0cb616d8ff722655c92a6767e3c4bf8feb94707b5330f881601d8eb054d40', 'recovery-protocol-tests/test_protocol.adb': '04a6b065ae31533e8dcb04b4661aedb467bc0c89a5613bb4fcec01b7734c0447', 'tests/worldline_tests.gpr': '0cf4fdd19da37ad197a3ea063fdbb259a7400d4e3865e40088fd78ee6fb7560d', 'worldline.gpr': 'edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021'})

# Root isolated visible-operator source repair: original policy remains exact above.
CONTRACT_PINS.update({'core/resource_run_ledger_c_api.adb': '71defbaa27c849a11e7628d1323ba0871b8e2b606c528dbf0d6e696caedb2892', 'core/worldline-recovery_protocol_c_api.adb': 'b8921fc27ccca361edcb7b6477e3804c16cff2aa154fe279bc368d65f51ddf77'})

# Prospective typed protocol value adapter; no foreign-memory/body boundary exemption.
REQUIRED_PROVED += ['Worldline.Recovery_Protocol_ABI.Apply']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/worldline-recovery_protocol_abi.ads', 'core/worldline-recovery_protocol_abi.adb'])
CONTRACT_PINS.update({'core/worldline-recovery_protocol_abi.ads': '7ca9a017eb112cde748227006cd5c6ffccda126cd7dd09fa7d4c36b1499ab62b', 'core/worldline-recovery_protocol_abi.adb': '362c5447a336cb8a1a87a81ce42e0c02deb8c2224bfe5330e4ca8e9a653c5247', 'protocol-adapter-tests/protocol_adapter_tests.gpr': '7e57d05ba13972588bc37cbe9b3b1a1d5c64b297a92e52349df6f08fcb5fbe47', 'protocol-adapter-tests/test_protocol_adapter.adb': '6055576865adf8a23c98ae8b7c9def207c8f253debbeb0d39548a94fdc310680', 'core/worldline-recovery_protocol_c_api.adb': 'b8921fc27ccca361edcb7b6477e3804c16cff2aa154fe279bc368d65f51ddf77', 'core/worldline_core.gpr': 'f1a6492bceff785f35dec5f30d3d5470fe7f439b5a85c02ddcbb3b4b44a47436'})

# GNAT16 pure functions retain implicit total termination; the illegal
# explicit function aspect is removed. Full body/variant proof is required.
CONTRACT_PINS.update({'core/worldline-chain_authority.ads': '8aa61e6419fc3c2f8f76d5e0e279d1d338c1c6615b2ab7bc5ac8a8d408a8edff'})

# Full common-preimage reviewed source composition; all original obligations remain required.
REQUIRED_PROVED += ['Worldline.Chain_Authority.Prefix_Step', 'Worldline.Chain_Authority.Finish_Reference', 'Evaluation_Epoch.Nonnegative_Valid', 'Evaluation_Epoch.Scale_Column', 'Evaluation_Epoch.Column_Bounds', 'Evaluation_Epoch.Prefix_Step', 'Evaluation_Epoch.Prefix_Bounds', 'Evaluation_Epoch.Prefix_Padding', 'Evaluation_Epoch.Power_Factor', 'Evaluation_Epoch.Prefix_Tail', 'Evaluation_Epoch.Positive_Multiple', 'Evaluation_Epoch.Distinct_Columns', 'Evaluation_Epoch.Remainder_From_Witness', 'Evaluation_Epoch.Prefix_Modulus', 'Evaluation_Epoch.Magnitude_Modulus', 'Evaluation_Epoch.Unsigned_Value', 'Evaluation_Epoch.Carry_Input', 'Evaluation_Epoch.Column_Division', 'Evaluation_Epoch.Matching_Column', 'Evaluation_Epoch.Increment_Modulus', 'Evaluation_Epoch.Mismatching_Column', 'Evaluation_Epoch.Same_Value', 'Evaluation_Epoch.Is_Successor', 'Evaluation_Finalization.Seal_Classification_Equation', 'Evaluation_Finalization.Seal_Equation', 'Evaluation_Finalization.Values.Record_Start_Value', 'Evaluation_Finalization.Values.Record_Input_Value', 'Worldline.Resources.Sum_Prefix_Step', 'Worldline.Resources.Reserve_Prefix_Step', 'Worldline.Owner_Transitions.Query_Equation', 'Worldline.Owner_Transitions.Retry_Equation', 'Resource_Ledger.Total_Worker_Recurrence', 'Resource_Ledger.Ordered_Magnitude_Columns', 'Resource_Ledger.Written_Prefix_Step', 'Resource_Ledger.Quantity_Slot_Frame', 'Resource_Ledger.Checked_Detail_Step', 'Resource_Ledger.Retained_Detail_Frame', 'Evaluation_Completion.History_Update_Reference', 'Evaluation_Completion.History_Update_Check', 'Evaluation_Completion.Update_Composition_Equality', 'Resource_Reservation_Transition.Operation_Row_Reference', 'Resource_Reservation_Transition.Operation_Row_Status', 'Resource_Reservation_Transition.Final_Transition_Reference', 'Resource_Reservation_Transition.Final_Transition_Status', 'Resource_Reservation_Transition.Decision_Composition_Equality', 'Resource_Run_Ledger.Same_Run_Metadata', 'Resource_Run_Ledger.Changed_Row_Composition_Equality', 'Evaluation_Completion.Apply', 'Evaluation_Completion.Current_Matches_Head', 'Evaluation_Completion.Cursor_Matches', 'Evaluation_Completion.Decide', 'Evaluation_Completion.Find_Run', 'Evaluation_Completion.From_History', 'Evaluation_Completion.History_Binding_Matches', 'Evaluation_Completion.History_Index', 'Evaluation_Completion.History_Reference', 'Evaluation_Completion.History_Row_Conforms', 'Evaluation_Completion.Intent_Binding', 'Evaluation_Completion.Project', 'Evaluation_Completion.Project_Reference', 'Evaluation_Completion.Reference', 'Evaluation_Completion.Results_Reference', 'Evaluation_Completion.Results_Valid', 'Evaluation_Completion.Retained_Summary_Matches', 'Evaluation_Completion.Same_Binding', 'Evaluation_Completion.Same_Execution', 'Evaluation_Completion.Same_Requirement', 'Evaluation_Completion.Same_Result', 'Evaluation_Completion.Same_Results', 'Evaluation_Completion.Same_Results_Reference', 'Evaluation_Completion.Same_Terminal', 'Evaluation_Completion.Same_Verifier', 'Evaluation_Completion.Update_Reference', 'Evaluation_Completion.Valid_Binding', 'Evaluation_Completion.Valid_Cursor', 'Evaluation_Completion.Valid_Result', 'Evaluation_Completion.Valid_Terminal', 'Evaluation_Raw_Roster.Captured_Failure', 'Evaluation_Raw_Roster.Evaluation_Completed', 'Evaluation_Raw_Roster.Failure_For_Check_Reference', 'Evaluation_Raw_Roster.Genuine_Required_Failure', 'Evaluation_Raw_Roster.Matches_Classification', 'Evaluation_Raw_Roster.Promotion_Roster', 'Evaluation_Raw_Roster.Reference', 'Evaluation_Raw_Roster.Required_Evidence', 'Evaluation_Raw_Roster.Row_Bound', 'Evaluation_Raw_Roster.Same_Current_Requirement', 'Evaluation_Raw_Roster.Valid_Checks', 'Evaluation_Raw_Roster.Valid_Rows', 'Evaluation_History.Cursor_Matches', 'Evaluation_History.Epoch_One', 'Evaluation_History.Epoch_Quantity', 'Evaluation_History.Epoch_Valid', 'Evaluation_History.Epoch_Zero', 'Evaluation_History.Failure_Reference_Conforms', 'Evaluation_History.Finalization_Valid', 'Evaluation_History.Find_Completed_Failure', 'Evaluation_History.Head_Decision', 'Evaluation_History.Head_Record', 'Evaluation_History.Head_Reference', 'Evaluation_History.History_Valid', 'Evaluation_History.Is_Current_Failure', 'Evaluation_History.Next_Epoch', 'Evaluation_History.Query_Complete', 'Evaluation_History.Query_Valid', 'Evaluation_History.Result_Conforms', 'Evaluation_History.Row_Valid', 'Evaluation_History.Same_Epoch', 'Evaluation_History.Same_Identity', 'Evaluation_History.Select_Evidence', 'Evaluation_History.Span_Valid', 'Resource_Reservation_Transition.Unique_Negative_Bound', 'Resource_Reservation_Transition.Unique_Positive_Bound', 'Resource_Reservation_Transition.Factor_Negative_Bound', 'Resource_Reservation_Transition.Factor_Positive_Bound']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/evaluation_finalization-values.adb', 'core/evaluation_finalization-values.ads'])
CONTRACT_PINS.update({'core/canonical_artifacts.ads': 'de5ecd7a705bd054497ac3594945b265d9ba3b34a332cd24f9849b2388b10f34', 'core/canonical_artifacts.adb': '349e185ee8e821142f58a293c91874cffe1cf55b1699dea5217c26478d4bc428', 'artifact-tests/canonical_artifact_tests.gpr': 'bce2824cc8181edb5f1e9d5b9c0a391d70d68302b9f717ae44f87a0cd4a1ea05', 'artifact-tests/test_canonical_artifacts.adb': '43137b6f14b3c71b87de8f09c957e95d29a7d44dab5c67fc92698be12c50b8f1', 'core/evaluation_finalization.ads': 'e0e85059342002b01291063b24c1a50ca2cfd94d0202e28e72806aefec332e5d', 'core/evaluation_finalization.adb': '3e18a007d6d6d49f7bd6713d246727d27b792a517934cbadba21b0b8db1c3a95', 'core/evaluation_finalization_c.ads': '28eb6e663262e471f71a97acf44c7683ba9c1f0979dcc88e1981a4395ea0f3c8', 'core/evaluation_finalization_c.adb': 'e16932c56e25577c1782a927c60ad0cab68e3b503b11541a187cb5787bac5ac3', 'core/evaluation_completion.ads': '0ced82cb877e8e9057b3b1ec796c72aee615bc4c67e95d6feecd168cda33a03b', 'core/evaluation_completion.adb': '0fdf0e0e700022ed9113d5a3efaee58316da12d1b77feec79d5779e9a43fcd42', 'core/evaluation_completion_roster.ads': '5af5ec8259073ad74444b5a4596b2a4b05e568c7d26739b9210e9b4616a2a2a3', 'core/evaluation_completion_roster.adb': 'f52e2b9d4a909b3c2b616e92aaf7b87ce4ddb8a6e8b34ea99068915dc9bb253a', 'core/evaluation_pending_v2.ads': '1e20de75c125ff20b5ad5750466430e959fb104b27f905403e38a35eb01f8321', 'core/evaluation_pending_v2.adb': 'd8864beff6356c688f3ed26c84d27e6d0e315c423e150ee257e45df71bad3a66', 'evaluation-authority-tests/test_evaluation_authority.adb': '071e0f859f92ac1576f95dc1c6e6f89df84c59edb304b36c3e15f0a887e98730', 'evaluation-authority-tests/evaluation_authority_tests.gpr': 'f9ba8e8e3b9593454c25f74a5678599ebdf09afbf8510b119ebfa6f8820a98f4', 'core/worldline-evaluation_authority.ads': 'ddf03fabb55ffcbf702dbaa066ad85a9f89a5b0e9600473b9b6824a2d1db767f', 'core/worldline-evaluation_authority.adb': '45a92dcf5d9950d333e5c6394370ef99c99bc53dadfd9dbdcf81aab50a1f3954', 'core/evaluation_completion_c.ads': '26a48384ae56b3590383c6ed9d408bad7dd55426cfa35402eb86d6921be34a73', 'core/evaluation_completion_c.adb': '4eb799e6d6de99df449c2b20f7368a9602ed015b47ebff9f584f4eee8119b900', 'core/resource_ledger.ads': '775e6daf668c1f3916b22d641a2c983d96bfa6dc9a7707709e1964a381ab950b', 'core/resource_ledger.adb': '8b4e8022b8e938de425b07389bc8e243ff974bcd6cdbb21baf5a668b7735bd7e', 'core/resource_reservation_transition.adb': 'f13ad8e1ef22ee22b3a6902b5c6945b0dcbb64d1385e28e8ad9d77fa083d0e86', 'core/resource_quantities.ads': 'c39661155528ed7388b63277e034ac3bbbceba239119e4d7700218e905aeac65', 'core/resource_quantities.adb': '155aa25399f30cb4837d589ae87c24ff8e2589dadbf27be06b9995bde3b6233b', 'pending-component/core/resource_quantities.ads': 'ff725d00a0be90fa2ca4632e9f48878f5f58199cbfacf2a82bfa554f4cdfe63a', 'pending-component/core/resource_quantities.adb': '48656286ffabeb9cac8436cafa2fe3bac2bb91a231ed17178966660c93f34206', 'core/evaluation_history.ads': 'e58eea740afa7f385a386ad97ad78380eb61ccac35d7669f14768dd4ac30cc3a', 'core/evaluation_history.adb': '74a24e09ac21e8900167db0f25b43cfd33d000eb52922653133a8e631a911c3f', 'core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'core/evaluation_epoch.adb': 'ee9b16847dfb3dedce58a9b6539e2568816b745d2bd0cb808a36362072df9e1b', 'pending-component/core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'pending-component/core/evaluation_epoch.adb': '76fa1977a41b3cdef9ee15972a1970db67771ec2f5bf0dab2cada0088679f363', 'core/worldline-resources.ads': '7fdf97a76f11aeeecfcde00c0e5e2587fde0f3155983765d006026aac70d4530', 'core/worldline-resources.adb': '8b9836dcb1eb091316a6dc08deb303aebdb664dcab5bb26e023c15e7a8ff8fb9', 'core/worldline-evaluation_v2.ads': '8e1f18244b924a7c9c05c67fdf785491a910c9f7c59966381b38962c2f68a72c', 'core/worldline-evaluation_v2.adb': '2fc57758a66ac2c7aa9ef6e108fdcbf93b1b286fd64b6620d8bca54ce32312eb', 'core/worldline-evaluation_wire.ads': '8b190a32f057a30a700e3331bd72aa2cfc18c5d6f3540b824756197f09077c7a', 'core/worldline-evaluation_wire.adb': '30696c9e2b4be84aad47d406864213a176f494e07dbed6f6907efe601d3be530', 'core/evaluation_raw_roster.ads': '1fcc5358aad66d61571552e80be7572fc47cb21fc8b4ab2dad2005812cd9664b', 'core/evaluation_raw_roster.adb': '51b238fc3489523bbc10acca6ee47dd274e391fb9491af8f65943b04396b4569', 'core/worldline-evaluation_report_facts.ads': 'f8bfee03303776b2825662bb1ce394fdf3c3e6acf3e7b1084500e50eba430f82', 'core/worldline-evaluation_report_facts.adb': 'ffdc1629f8eaef1ec4ab1bbc4fc988f2f1546dd8b5013ec4635888d77f8240fb', 'core/worldline-evaluation_report_wire.ads': 'a58347985c4242421c4114ecf61ddaf6f84229e62ab2114cd0947b7feee29b19', 'core/worldline-evaluation_report_wire.adb': '19ed101a83a9a9350a660cd7693a8be7ffee86557fa6d58e7959a0ae9973ff78', 'evaluation-wire-tests/evaluation_wire_tests.gpr': '8fde6733c882c9be99a7fbcdce0c6ba0a8eca138a4b68e65ec77efdc84160d89', 'worldline.gpr': 'edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021', 'core/worldline_core.gpr': 'f1a6492bceff785f35dec5f30d3d5470fe7f439b5a85c02ddcbb3b4b44a47436', 'core/worldline_core_sources.gpr': 'ed7f3006aec84e5059b9163b0aa525ed829a256f2e418bb400e0291bb1434077', 'core/attest_sha256.gpr': 'f75c901810d0227f9b1331929e06a4405eb83c82385e5cab2be4f4e86daf8822', 'tests/worldline_tests.gpr': '0cf4fdd19da37ad197a3ea063fdbb259a7400d4e3865e40088fd78ee6fb7560d', 'core/worldline.ads': '6fc501e7d5e4927784d415e25c84339efd42a96358216c69825882deea3603e3', 'core/attest/attest.ads': 'bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587', 'core/attest/attest-sha256.ads': 'b5b299d3559e8a083d1edbbaefc96f76f73a0c4e0e6d2dfdcfb6d3fc0c4d7bec', 'core/worldline-c_api.ads': '1da0afffd071cb78449216a359b362f9d31e6cae22e9d02c09cb19bfce097efe', 'core/worldline-collapse.ads': '94ef49a258a46363eea81d44e168ce4e7cc618fdf128e916e92e447f2ffe32e2', 'core/worldline-collapse_wire.ads': '48270be156ee3f1c7d7f6215917c9b8026ac5346c45064cf7803950c137ddd76', 'core/worldline-identities.ads': 'ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21', 'core/worldline-evaluation.ads': '06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e', 'core/worldline-transitions.ads': '5b9c8f89900d01eeb40818de6392e1f23f8e2606cba702dd06e72e4257406c27', 'core/worldline-c_api.adb': '64a839d076a4e52d8fb65c599a91f9eb0812adef30f8e48a4e80669f56557f52', 'core/worldline-receipts.ads': 'a354588d79bc6d01973afcf10b9b31a08d996e2056a1bad8db05e97fe7636dd6', 'core/worldline-receipts.adb': '8b30e5567ec7a86962f9cea3cd67b6d07194dc726e70b025bc2f97a406767829', 'core/worldline-causal_graph.ads': '4c1db06549310c2dd93c26b9e109dd832a0f43390fe7ece37dbab06934b78ae7', 'core/worldline-causal_graph.adb': 'e3239b7770a185f4eef90d838c803a64b128e84380e3af27513867632ff3c121', 'core/worldline-world.ads': '3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5', 'core/worldline-ancestry.ads': '718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db', 'core/resource_admission.adb': '0da682e7cd0aa85daea88a9f36926fa213240b9273cd7015108f95f4f48ee63c', 'core/resource_admission.ads': '2d93c087e980ec50ce77a21efdeb4c2d3a96e503493e55c0a9cbbb27e80381f2', 'core/resource_reservation_lifecycle.adb': '3cf6bbe8dfef85f485be16eb9185768ace28ddc6a3ea5bfe0cd0aa26dd8aef41', 'core/resource_reservation_lifecycle.ads': '8e3c85334abc8ff747e6f468bea29f04196c3c11cffa10a68207b96c8b3e0400', 'core/resource_reservation_transition.ads': '34d4b6d554999fc3366b78d0740be905c21e0d3c0c20b6fb96fa82691674a9d2', 'core/worldline-recovery.adb': '75763d6eb35c647df523a728c6939e21cda6c3d7b44ba54fb2a4a917f3149e24', 'core/worldline-recovery.ads': 'b2eff79e29cd18c5a69672e3c6063faa120345d19a3f4cc76cf8ae31a69df7fc', 'core/worldline-recovery_authorization.adb': 'd90b75ec516fbf8ddb0f0bf40ee39297e70eebc001d4edad6b0142c7da092e7d', 'core/worldline-recovery_authorization.ads': '3b95bc25da8343b9d0c4cd6e133614bb59cdce65740142d9c2d2ed072e62dec6', 'core/worldline-recovery_authorization_c_api.adb': 'c9ccade8b28286a2166130c0057ca3187a7465a8c1521c523fda3429b004282c', 'core/worldline-recovery_authorization_c_api.ads': '88a156f3749251a4cff6393739ce7b738e82fb9d625c71774489f99430914f34', 'core/worldline-recovery_authorization_wire.adb': 'e0c1054dd20e34bf1ddbcaefd9665c7588fc4683c8dad1a91351c89597928f62', 'core/worldline-recovery_authorization_wire.ads': 'a6b453f40b2eee2d860008ecb11b9720f6be2a5be5c1aca52a91f264c40d687c', 'core/worldline-resource_wire.adb': 'ec1ea00cf321f841aafcb874047c48d1ff28363d29ea042c6703a60a2be32f80', 'core/worldline-resource_wire.ads': 'b0af3ef936e727ba9113430ebc29c2843124f82e584b3bb294dc23af2667ad75', 'core/worldline-recovery_authorization_v3.adb': '21536d8595e0d6d14764b56309eb2f88d28bd88fc47b6fe9c16f915c98ed63dd', 'core/worldline-recovery_authorization_v3.ads': '8b3f3c7477c461dadceba33ab421cf54d4c77129e2875768346d93c91f3fdd51', 'core/worldline-recovery_authorization_v3_c_api.adb': '9a90152c2f15a615f61dbe3d96aa520f48ce541a0f8b9843dbb51553aef19ac4', 'core/worldline-recovery_authorization_v3_c_api.ads': '06832ec39eec8162227eadb2f158d7ca53ec6af0d796693d0701b32d430cf6c9', 'core/worldline-recovery_authorization_v3_wire.adb': '5df8bd9bcd6842aaf033bde67edd121e6d9e0bdfd6f29158f0f8b1a57fd36bc6', 'core/worldline-recovery_authorization_v3_wire.ads': '30a49ffee1fecf33fe798e524cda06f73a8a2164ffe92c2bce8a10155a45f90e', 'recovery-epoch-tests/recovery_epoch_tests.gpr': '600c9e1b3b3524f1419f2419a0e0925641a9dec1c822fb0b5ddb1e2afc9bc880', 'recovery-epoch-tests/test_epochs.adb': 'b134c380bb6990c55df7c21c590627585c57a8f0bbb99453a4d4c61913a68670', 'core/worldline-recovery_protocol.adb': '1188891c1663c1c0c3ec47d304af9aaf5b14b1f9a74cff6ad771d47d06f5f573', 'core/worldline-recovery_protocol.ads': '7ca9a947061fce2a3278ab064ede1f8c2edad77fb3ecbdb68ef3f1cc41131eec', 'core/worldline-recovery_protocol_c_api.adb': 'b8921fc27ccca361edcb7b6477e3804c16cff2aa154fe279bc368d65f51ddf77', 'core/worldline-recovery_protocol_c_api.ads': '659e9b509e0350d58039f67ce3741cb01eff6a266b970b00bf56f601b550d413', 'core/worldline-recovery_protocol_wire.adb': '4716e4c67604bc3ebb236994a30a1f98a2f2684e99fa8a3dde6c6529c2c49d2b', 'core/worldline-recovery_protocol_wire.ads': '389d2fd4ad5a625f1ac5274da214c9b8e953f261882b300fbbfa96d17b5c1cd4', 'recovery-protocol-tests/test_protocol.adb': '04a6b065ae31533e8dcb04b4661aedb467bc0c89a5613bb4fcec01b7734c0447', 'recovery-protocol-tests/recovery_protocol_tests.gpr': '2ab0cb616d8ff722655c92a6767e3c4bf8feb94707b5330f881601d8eb054d40', 'core/worldline-chain_authority.adb': 'ad10d252025b8d46dba16b99031b733f40d13d29d391a703bdf8b3b193c7166d', 'core/worldline-chain_authority.ads': '8aa61e6419fc3c2f8f76d5e0e279d1d338c1c6615b2ab7bc5ac8a8d408a8edff', 'core/worldline-chain_authority_c_api.adb': 'f3a7c76c681bf8e82960929a3c30659c1926dba38d71bd59f96abaa875c5326a', 'core/worldline-chain_authority_c_api.ads': 'c44a9c3ddd2dce171d5ff88c2da981b36afec678db7e830e24fa60699b1784b0', 'core/worldline-chain_authority_wire.adb': '9ff2355dbebbf8192b78e21adb225bb8405968612a1c8cc6e6778f27c42961e4', 'core/worldline-chain_authority_wire.ads': '7baf22c73d65bb6ba5dbe5386453da06a8b600f8a81e58931bf9c6377bada4f1', 'core/worldline-owner_transitions.adb': 'b3049b6773bed28e252c1faaa6926e6e71c3ca51a40701ad2293aa0474d8556f', 'core/worldline-owner_transitions.ads': '0d7692119a7eb400f06d1bc8b3792f9f6925f58096d23b059d8f6ea5a49000b3', 'core/worldline-owner_transitions_wire.adb': '4e340e98c08587cfdc891e7f46b44febc194b81bc5bebfdd265d751434884319', 'core/worldline-owner_transitions_wire.ads': '8867a739ddc2b22c3d73c8908a0be7bb8ecd1410bbe9232776499aa57837f814', 'core/resource_run_ledger.adb': 'c64d4369b0a58ac4290bbddb9390d2953406b8d44eade1ebc5de672635c560b1', 'core/resource_run_ledger.ads': '3a58b0c3721e0d7824f3ddd0674e3ef0bc0c485a5d313b33badc44be97c2fb5c', 'core/resource_run_ledger_c_api.adb': '71defbaa27c849a11e7628d1323ba0871b8e2b606c528dbf0d6e696caedb2892', 'core/resource_run_ledger_c_api.ads': 'e095a573d30b0c3aabe63a23fd13dca59e9a664c381c8e306863b9b152704e1d', 'core/resource_run_ledger_wire.adb': 'c2feb75a7b3616968802469e7df304afcc9af6ac113a02222796487d0a6df0b3', 'core/resource_run_ledger_wire.ads': 'b09d4e07df8652f8f87b2a6526f0fa26875253ea1dc8909bbec6b330d6d02eed', 'core/worldline-owner_retry_audit.ads': 'f10e8a5758de157d40ab487c2b5071232cc8ede3b0984b36e75e922dff5b49e0', 'core/worldline-owner_retry_audit.adb': 'd444de903bc184300bbfd6e95348f4307827b7ad3948e4fe77c091daec52b5bd', 'core/worldline-owner_retry_audit_wire.ads': '60772578c6f02b53ea7b4d5614dde93f4e6d02e073847932c4647853d205f979', 'core/worldline-owner_retry_audit_wire.adb': 'ffeb183989406733268c9d25cac7b2501f1fb28bcf36af622ca1391e0bc9bd70', 'core/worldline-owner_conjunction.ads': '62559ebaa5c94a88435d44333ac61aede278af67813f3ab7ac72d27bd86ec89d', 'core/worldline-owner_conjunction.adb': '9d6f3f09c955a8612747f088a14802c5004a9a656009389e11254d6d623f3c32', 'core/worldline-owner_conjunction_wire.ads': 'a078f33e659fcb0c0eac74e63777425181bd5e2865566abfb79f36fc34aa510d', 'core/worldline-owner_conjunction_wire.adb': '8aedcbc566fc59ca8a600a6410199ef8ec31b3fbffb655e856e679007f0fc7c7', 'core/worldline-owner_subject_projection.ads': '2aa7d9d7208c340ae46ac36a4bf74d0dfe1ce2f53fdae435f95fcdc39479b7f7', 'core/worldline-owner_subject_projection.adb': 'abcf67952cd84158f7a536c8315402ab6a7cb3a9f32ba13e7587ad1d0119df72', 'core/worldline-recovery_protocol_abi.ads': '7ca9a017eb112cde748227006cd5c6ffccda126cd7dd09fa7d4c36b1499ab62b', 'core/worldline-recovery_protocol_abi.adb': '362c5447a336cb8a1a87a81ce42e0c02deb8c2224bfe5330e4ca8e9a653c5247', 'protocol-adapter-tests/protocol_adapter_tests.gpr': '7e57d05ba13972588bc37cbe9b3b1a1d5c64b297a92e52349df6f08fcb5fbe47', 'protocol-adapter-tests/test_protocol_adapter.adb': '6055576865adf8a23c98ae8b7c9def207c8f253debbeb0d39548a94fdc310680', 'epoch-correspondence-tests/epoch_correspondence_core_tests.gpr': '5216f9a5a0d7f9430e4f8fe400181a6d111179bff4520d981ae3c37d18f2bc4e', 'epoch-correspondence-tests/epoch_correspondence_pending_tests.gpr': '1af95a0f4a5851f4aac0775bd8d2493fa26224639d312f097db87fb88da8ba28', 'epoch-correspondence-tests/test_epoch_correspondence.adb': 'a297bb45d5c87dd010997741f10beb7598310dd7662a255e50ad51160dd88c1a', 'core/evaluation_finalization-values.adb': 'c6dd5ea011677b3a8ae31f9d5b2ccddd51fc5549ed5f07eef27add39a3ead320', 'core/evaluation_finalization-values.ads': 'f3fe2b54ad04f1a43c5fdd181fc149fffc3441f2b744b9da6da6ef8bab8d13ce', 'finalization-value-controls/finalization_value_controls.gpr': '756918630a4b54abaff8e68e4ae84aac7a7de2b670ebea00bb86b0a6edc6e421', 'finalization-value-controls/test_finalization_parent_values.adb': '9e87197fa326dc73f582f05cc473beff73d0b08c82da4dee29951827e358de28', 'finalization-value-controls/test_finalization_projection.adb': '669b4aa0804d272585ab5fa3569a7db4435e14ea0d7224165ee8470370ebdefd', 'finalization-value-controls/test_finalization_values.adb': '3242b812f6c19ea65f5d523c6155964e6e41b7b06976718f6391761db7106b6d', 'resources-prefix-correspondence-tests/resources_prefix_correspondence_tests.gpr': 'd238363ed2e518627c36a4afe965398ac4cef15b4264f7b3d50f25b771460978', 'resources-prefix-correspondence-tests/test_resources_prefix_correspondence.adb': 'ac4c037ecddd23d710e57e3dfe92534f0f2ee67ef943daa6947904d1c165c91e', 'wire-initialization-tests/test_wire_initialization.adb': 'e779f4827c714b6329addd074cdefee94737bbada08f81a82875a6a4daba000c', 'wire-initialization-tests/wire_initialization_tests.gpr': 'bfe67074a1b0fa4193667beae58279c4746b50f8a05a6c0184354dcbe7570224', 'resource-ledger-correspondence-tests/resource_ledger_correspondence_tests.gpr': 'd1f489d22d3508c17e9c529836ec22db29d339db94f5ed70a6a0b3c365883ec8', 'resource-ledger-correspondence-tests/test_resource_ledger_correspondence.adb': 'fdbcf441d1dcb1ef0e0568f36910c03d727b58f9da634bf96dbfd75a24116d32', 'decision-correspondence-tests/decision_correspondence_tests.gpr': '52637b39b04f201af2c2088f748a3ab7c1b032e813457638b12f1d6c18661016', 'decision-correspondence-tests/test_completion_correspondence.adb': '6ad18e9ec3136d2bf14ca45cb711801fc125ac6e307598ce0c7e0b5c6e36e945', 'decision-correspondence-tests/test_history_correspondence.adb': 'd293c070a38372238ac0c546deb2b8cab3df6f83ba21428f720ebccb6ed597cf', 'decision-correspondence-tests/test_raw_roster_correspondence.adb': 'ba17660670e42559e2b38af0d71f1c08c7126fbc527096bfb988e1aa2a59956b', 'decision-correspondence-tests/test_run_metadata_correspondence.adb': '93b4b7b7f610aaf0c844738886c347589769363e94f26d77edd4ccf4bedecad9', 'decision-correspondence-tests/test_transition_correspondence.adb': 'ac2b451ac7e78e52fcf4ee89d164fdb006f5326748517aa3b52cd99a00fb9fb1', 'core/evaluation_pending_c.ads': '62c2992c04c7eccbc8e89a71d2b2fa09a3d98c418d56fddd3775ad1236582710', 'core/evaluation_pending_c.adb': 'fa443db56f8e69122b9a57ec93d66bf1d9856a1fc3718b00ad2515958b8297a5', 'core/evaluation_pending_v2_c.ads': '79362e75326c104583ebd0222f97a180f4fabf6832c3e2f36ed21424bfc9b509', 'core/evaluation_pending_v2_c.adb': '060ca872213a86e6c126879ce4773d6e05431865e2d0fd6ea7b89ffb56b5bbf2', 'core/spark-big_integers.ads': 'f96017313a6e785d5c4697d95e610ced1a3612d20b7310dddb5af230226dbf1a', 'core/worldline-evaluation_history_c_api.ads': 'ebdc5645651239c8b29ca208e2e2ea72413169e84964ae0ee91c9c3251948d50', 'core/worldline-evaluation_history_c_api.adb': 'b8986e965b42fb3125c9dbcb19434246aeaaafa2c3d0206193b83df97a9686d9', 'core/worldline-recovery_c_api.ads': '6567180361bb753618586362db27eaaf858d373bf18576eebfeda82e4896d41e', 'core/worldline-recovery_c_api.adb': '33a09d32f02dfd789818414d528d3646d23df54643a11fd345b946a861a098d4', 'core/worldline-reservation_lifecycle_c_api.ads': '98a204b4536082d3c9cdef075800a58d6d335c3bedcf647e9c0ec44c02cc2c70', 'core/worldline-reservation_lifecycle_c_api.adb': 'be91398f93040875e0eba00b0f2cd454e1a851af7720efbcaf494987ac1f4dba', 'core/worldline-resource_ledger_c_api.ads': '34cf925193fd48acd782a0295d786a6aaada67d11b12082504df1dfac5ee360f', 'core/worldline-resource_ledger_c_api.adb': '587e08311372b9455a06e341d52e8f51b790949eeeeabf696f9ff422e22ffed1', 'core/worldline-resource_policy_c_api.ads': '1a4a9838dd42e70d3386db77642d9d272b3371e5e19537a80d58ae57ebf565b6', 'core/worldline-resource_policy_c_api.adb': '356d6426e8fef668d52be40bf578374bb9356b4898474216738fe8dc631a66c1', 'core/worldline-resources_c_api.ads': '2d5dfca12e0e053616fbcccc262dba093b8ebc9cc64840c3e8e28975731d14f3', 'core/worldline-resources_c_api.adb': 'def7d0d21088f6121441faca99afc3a76de4aa32ed4aa657493be1c34203da81'})

# Finite installed-eligibility source repair; no proof or native-cost credit.
CONTRACT_PINS.update({'core/resource_quantities.ads': 'c39661155528ed7388b63277e034ac3bbbceba239119e4d7700218e905aeac65', 'core/evaluation_finalization_c.adb': 'e16932c56e25577c1782a927c60ad0cab68e3b503b11541a187cb5787bac5ac3'})

# SHA256 source-only warning repair; all original proof obligations remain.
CONTRACT_PINS.update({'core/attest/attest-sha256.adb': '60ac468bec5bc75013407700b2122faa52a8295c4c43c19359a2e4fea4dc3be2'})

# Whole common V4 composition normalized pins; every original obligation remains OPEN.
CONTRACT_PINS.update({'core/canonical_artifacts.ads': 'de5ecd7a705bd054497ac3594945b265d9ba3b34a332cd24f9849b2388b10f34', 'core/canonical_artifacts.adb': '349e185ee8e821142f58a293c91874cffe1cf55b1699dea5217c26478d4bc428', 'artifact-tests/canonical_artifact_tests.gpr': 'bce2824cc8181edb5f1e9d5b9c0a391d70d68302b9f717ae44f87a0cd4a1ea05', 'artifact-tests/test_canonical_artifacts.adb': '43137b6f14b3c71b87de8f09c957e95d29a7d44dab5c67fc92698be12c50b8f1', 'core/evaluation_finalization.ads': 'e0e85059342002b01291063b24c1a50ca2cfd94d0202e28e72806aefec332e5d', 'core/evaluation_finalization.adb': '3e18a007d6d6d49f7bd6713d246727d27b792a517934cbadba21b0b8db1c3a95', 'core/evaluation_finalization_c.ads': '28eb6e663262e471f71a97acf44c7683ba9c1f0979dcc88e1981a4395ea0f3c8', 'core/evaluation_finalization_c.adb': 'e16932c56e25577c1782a927c60ad0cab68e3b503b11541a187cb5787bac5ac3', 'core/evaluation_completion.ads': '0ced82cb877e8e9057b3b1ec796c72aee615bc4c67e95d6feecd168cda33a03b', 'core/evaluation_completion.adb': '0fdf0e0e700022ed9113d5a3efaee58316da12d1b77feec79d5779e9a43fcd42', 'core/evaluation_completion_roster.ads': '5af5ec8259073ad74444b5a4596b2a4b05e568c7d26739b9210e9b4616a2a2a3', 'core/evaluation_completion_roster.adb': 'f52e2b9d4a909b3c2b616e92aaf7b87ce4ddb8a6e8b34ea99068915dc9bb253a', 'core/evaluation_pending_v2.ads': '1e20de75c125ff20b5ad5750466430e959fb104b27f905403e38a35eb01f8321', 'core/evaluation_pending_v2.adb': 'd8864beff6356c688f3ed26c84d27e6d0e315c423e150ee257e45df71bad3a66', 'evaluation-authority-tests/test_evaluation_authority.adb': '071e0f859f92ac1576f95dc1c6e6f89df84c59edb304b36c3e15f0a887e98730', 'evaluation-authority-tests/evaluation_authority_tests.gpr': 'f9ba8e8e3b9593454c25f74a5678599ebdf09afbf8510b119ebfa6f8820a98f4', 'core/worldline-evaluation_authority.ads': 'ddf03fabb55ffcbf702dbaa066ad85a9f89a5b0e9600473b9b6824a2d1db767f', 'core/worldline-evaluation_authority.adb': '45a92dcf5d9950d333e5c6394370ef99c99bc53dadfd9dbdcf81aab50a1f3954', 'core/evaluation_completion_c.ads': '26a48384ae56b3590383c6ed9d408bad7dd55426cfa35402eb86d6921be34a73', 'core/evaluation_completion_c.adb': '4eb799e6d6de99df449c2b20f7368a9602ed015b47ebff9f584f4eee8119b900', 'core/resource_ledger.ads': '775e6daf668c1f3916b22d641a2c983d96bfa6dc9a7707709e1964a381ab950b', 'core/resource_ledger.adb': '8b4e8022b8e938de425b07389bc8e243ff974bcd6cdbb21baf5a668b7735bd7e', 'core/resource_reservation_transition.adb': 'f13ad8e1ef22ee22b3a6902b5c6945b0dcbb64d1385e28e8ad9d77fa083d0e86', 'core/resource_quantities.ads': 'c39661155528ed7388b63277e034ac3bbbceba239119e4d7700218e905aeac65', 'core/resource_quantities.adb': '155aa25399f30cb4837d589ae87c24ff8e2589dadbf27be06b9995bde3b6233b', 'pending-component/core/resource_quantities.ads': 'ff725d00a0be90fa2ca4632e9f48878f5f58199cbfacf2a82bfa554f4cdfe63a', 'pending-component/core/resource_quantities.adb': '48656286ffabeb9cac8436cafa2fe3bac2bb91a231ed17178966660c93f34206', 'core/evaluation_history.ads': 'e58eea740afa7f385a386ad97ad78380eb61ccac35d7669f14768dd4ac30cc3a', 'core/evaluation_history.adb': '74a24e09ac21e8900167db0f25b43cfd33d000eb52922653133a8e631a911c3f', 'core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'core/evaluation_epoch.adb': 'ee9b16847dfb3dedce58a9b6539e2568816b745d2bd0cb808a36362072df9e1b', 'pending-component/core/evaluation_epoch.ads': '91b6ffd9a92440ad93a4b871123459af54642a5483f6a037db4eeb78a88aeeb5', 'pending-component/core/evaluation_epoch.adb': '76fa1977a41b3cdef9ee15972a1970db67771ec2f5bf0dab2cada0088679f363', 'core/worldline-resources.ads': '7fdf97a76f11aeeecfcde00c0e5e2587fde0f3155983765d006026aac70d4530', 'core/worldline-resources.adb': '8b9836dcb1eb091316a6dc08deb303aebdb664dcab5bb26e023c15e7a8ff8fb9', 'core/worldline-evaluation_v2.ads': '8e1f18244b924a7c9c05c67fdf785491a910c9f7c59966381b38962c2f68a72c', 'core/worldline-evaluation_v2.adb': '2fc57758a66ac2c7aa9ef6e108fdcbf93b1b286fd64b6620d8bca54ce32312eb', 'core/worldline-evaluation_wire.ads': '8b190a32f057a30a700e3331bd72aa2cfc18c5d6f3540b824756197f09077c7a', 'core/worldline-evaluation_wire.adb': '30696c9e2b4be84aad47d406864213a176f494e07dbed6f6907efe601d3be530', 'core/evaluation_raw_roster.ads': '1fcc5358aad66d61571552e80be7572fc47cb21fc8b4ab2dad2005812cd9664b', 'core/evaluation_raw_roster.adb': '51b238fc3489523bbc10acca6ee47dd274e391fb9491af8f65943b04396b4569', 'core/worldline-evaluation_report_facts.ads': 'f8bfee03303776b2825662bb1ce394fdf3c3e6acf3e7b1084500e50eba430f82', 'core/worldline-evaluation_report_facts.adb': 'ffdc1629f8eaef1ec4ab1bbc4fc988f2f1546dd8b5013ec4635888d77f8240fb', 'core/worldline-evaluation_report_wire.ads': 'a58347985c4242421c4114ecf61ddaf6f84229e62ab2114cd0947b7feee29b19', 'core/worldline-evaluation_report_wire.adb': '19ed101a83a9a9350a660cd7693a8be7ffee86557fa6d58e7959a0ae9973ff78', 'evaluation-wire-tests/evaluation_wire_tests.gpr': '8fde6733c882c9be99a7fbcdce0c6ba0a8eca138a4b68e65ec77efdc84160d89', 'worldline.gpr': 'edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021', 'core/worldline_core.gpr': 'f1a6492bceff785f35dec5f30d3d5470fe7f439b5a85c02ddcbb3b4b44a47436', 'core/worldline_core_sources.gpr': 'ed7f3006aec84e5059b9163b0aa525ed829a256f2e418bb400e0291bb1434077', 'core/attest_sha256.gpr': 'f75c901810d0227f9b1331929e06a4405eb83c82385e5cab2be4f4e86daf8822', 'tests/worldline_tests.gpr': '0cf4fdd19da37ad197a3ea063fdbb259a7400d4e3865e40088fd78ee6fb7560d', 'core/worldline.ads': '6fc501e7d5e4927784d415e25c84339efd42a96358216c69825882deea3603e3', 'core/attest/attest.ads': 'bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587', 'core/attest/attest-sha256.ads': 'b5b299d3559e8a083d1edbbaefc96f76f73a0c4e0e6d2dfdcfb6d3fc0c4d7bec', 'core/worldline-c_api.ads': '1da0afffd071cb78449216a359b362f9d31e6cae22e9d02c09cb19bfce097efe', 'core/worldline-collapse.ads': '94ef49a258a46363eea81d44e168ce4e7cc618fdf128e916e92e447f2ffe32e2', 'core/worldline-collapse_wire.ads': '48270be156ee3f1c7d7f6215917c9b8026ac5346c45064cf7803950c137ddd76', 'core/worldline-identities.ads': 'ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21', 'core/worldline-evaluation.ads': '06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e', 'core/worldline-transitions.ads': '5b9c8f89900d01eeb40818de6392e1f23f8e2606cba702dd06e72e4257406c27', 'core/worldline-c_api.adb': '64a839d076a4e52d8fb65c599a91f9eb0812adef30f8e48a4e80669f56557f52', 'core/worldline-receipts.ads': 'a354588d79bc6d01973afcf10b9b31a08d996e2056a1bad8db05e97fe7636dd6', 'core/worldline-receipts.adb': '8b30e5567ec7a86962f9cea3cd67b6d07194dc726e70b025bc2f97a406767829', 'core/worldline-causal_graph.ads': '4c1db06549310c2dd93c26b9e109dd832a0f43390fe7ece37dbab06934b78ae7', 'core/worldline-causal_graph.adb': 'e3239b7770a185f4eef90d838c803a64b128e84380e3af27513867632ff3c121', 'core/worldline-world.ads': '3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5', 'core/worldline-ancestry.ads': '718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db', 'core/resource_admission.adb': '0da682e7cd0aa85daea88a9f36926fa213240b9273cd7015108f95f4f48ee63c', 'core/resource_admission.ads': '2d93c087e980ec50ce77a21efdeb4c2d3a96e503493e55c0a9cbbb27e80381f2', 'core/resource_reservation_lifecycle.adb': '3cf6bbe8dfef85f485be16eb9185768ace28ddc6a3ea5bfe0cd0aa26dd8aef41', 'core/resource_reservation_lifecycle.ads': '8e3c85334abc8ff747e6f468bea29f04196c3c11cffa10a68207b96c8b3e0400', 'core/resource_reservation_transition.ads': '34d4b6d554999fc3366b78d0740be905c21e0d3c0c20b6fb96fa82691674a9d2', 'core/worldline-recovery.adb': '75763d6eb35c647df523a728c6939e21cda6c3d7b44ba54fb2a4a917f3149e24', 'core/worldline-recovery.ads': 'b2eff79e29cd18c5a69672e3c6063faa120345d19a3f4cc76cf8ae31a69df7fc', 'core/worldline-recovery_authorization.adb': 'd90b75ec516fbf8ddb0f0bf40ee39297e70eebc001d4edad6b0142c7da092e7d', 'core/worldline-recovery_authorization.ads': '3b95bc25da8343b9d0c4cd6e133614bb59cdce65740142d9c2d2ed072e62dec6', 'core/worldline-recovery_authorization_c_api.adb': 'c9ccade8b28286a2166130c0057ca3187a7465a8c1521c523fda3429b004282c', 'core/worldline-recovery_authorization_c_api.ads': '88a156f3749251a4cff6393739ce7b738e82fb9d625c71774489f99430914f34', 'core/worldline-recovery_authorization_wire.adb': 'e0c1054dd20e34bf1ddbcaefd9665c7588fc4683c8dad1a91351c89597928f62', 'core/worldline-recovery_authorization_wire.ads': 'a6b453f40b2eee2d860008ecb11b9720f6be2a5be5c1aca52a91f264c40d687c', 'core/worldline-resource_wire.adb': 'ec1ea00cf321f841aafcb874047c48d1ff28363d29ea042c6703a60a2be32f80', 'core/worldline-resource_wire.ads': 'b0af3ef936e727ba9113430ebc29c2843124f82e584b3bb294dc23af2667ad75', 'core/worldline-recovery_authorization_v3.adb': '21536d8595e0d6d14764b56309eb2f88d28bd88fc47b6fe9c16f915c98ed63dd', 'core/worldline-recovery_authorization_v3.ads': '8b3f3c7477c461dadceba33ab421cf54d4c77129e2875768346d93c91f3fdd51', 'core/worldline-recovery_authorization_v3_c_api.adb': '9a90152c2f15a615f61dbe3d96aa520f48ce541a0f8b9843dbb51553aef19ac4', 'core/worldline-recovery_authorization_v3_c_api.ads': '06832ec39eec8162227eadb2f158d7ca53ec6af0d796693d0701b32d430cf6c9', 'core/worldline-recovery_authorization_v3_wire.adb': '5df8bd9bcd6842aaf033bde67edd121e6d9e0bdfd6f29158f0f8b1a57fd36bc6', 'core/worldline-recovery_authorization_v3_wire.ads': '30a49ffee1fecf33fe798e524cda06f73a8a2164ffe92c2bce8a10155a45f90e', 'recovery-epoch-tests/recovery_epoch_tests.gpr': '600c9e1b3b3524f1419f2419a0e0925641a9dec1c822fb0b5ddb1e2afc9bc880', 'recovery-epoch-tests/test_epochs.adb': 'b134c380bb6990c55df7c21c590627585c57a8f0bbb99453a4d4c61913a68670', 'core/worldline-recovery_protocol.adb': '1188891c1663c1c0c3ec47d304af9aaf5b14b1f9a74cff6ad771d47d06f5f573', 'core/worldline-recovery_protocol.ads': '7ca9a947061fce2a3278ab064ede1f8c2edad77fb3ecbdb68ef3f1cc41131eec', 'core/worldline-recovery_protocol_c_api.adb': 'b8921fc27ccca361edcb7b6477e3804c16cff2aa154fe279bc368d65f51ddf77', 'core/worldline-recovery_protocol_c_api.ads': '659e9b509e0350d58039f67ce3741cb01eff6a266b970b00bf56f601b550d413', 'core/worldline-recovery_protocol_wire.adb': '4716e4c67604bc3ebb236994a30a1f98a2f2684e99fa8a3dde6c6529c2c49d2b', 'core/worldline-recovery_protocol_wire.ads': '389d2fd4ad5a625f1ac5274da214c9b8e953f261882b300fbbfa96d17b5c1cd4', 'recovery-protocol-tests/test_protocol.adb': '04a6b065ae31533e8dcb04b4661aedb467bc0c89a5613bb4fcec01b7734c0447', 'recovery-protocol-tests/recovery_protocol_tests.gpr': '2ab0cb616d8ff722655c92a6767e3c4bf8feb94707b5330f881601d8eb054d40', 'core/worldline-chain_authority.adb': 'ad10d252025b8d46dba16b99031b733f40d13d29d391a703bdf8b3b193c7166d', 'core/worldline-chain_authority.ads': '8aa61e6419fc3c2f8f76d5e0e279d1d338c1c6615b2ab7bc5ac8a8d408a8edff', 'core/worldline-chain_authority_c_api.adb': 'f3a7c76c681bf8e82960929a3c30659c1926dba38d71bd59f96abaa875c5326a', 'core/worldline-chain_authority_c_api.ads': 'c44a9c3ddd2dce171d5ff88c2da981b36afec678db7e830e24fa60699b1784b0', 'core/worldline-chain_authority_wire.adb': '9ff2355dbebbf8192b78e21adb225bb8405968612a1c8cc6e6778f27c42961e4', 'core/worldline-chain_authority_wire.ads': '7baf22c73d65bb6ba5dbe5386453da06a8b600f8a81e58931bf9c6377bada4f1', 'core/worldline-owner_transitions.adb': 'b3049b6773bed28e252c1faaa6926e6e71c3ca51a40701ad2293aa0474d8556f', 'core/worldline-owner_transitions.ads': '0d7692119a7eb400f06d1bc8b3792f9f6925f58096d23b059d8f6ea5a49000b3', 'core/worldline-owner_transitions_wire.adb': '4e340e98c08587cfdc891e7f46b44febc194b81bc5bebfdd265d751434884319', 'core/worldline-owner_transitions_wire.ads': '8867a739ddc2b22c3d73c8908a0be7bb8ecd1410bbe9232776499aa57837f814', 'core/resource_run_ledger.adb': 'c64d4369b0a58ac4290bbddb9390d2953406b8d44eade1ebc5de672635c560b1', 'core/resource_run_ledger.ads': '3a58b0c3721e0d7824f3ddd0674e3ef0bc0c485a5d313b33badc44be97c2fb5c', 'core/resource_run_ledger_c_api.adb': '71defbaa27c849a11e7628d1323ba0871b8e2b606c528dbf0d6e696caedb2892', 'core/resource_run_ledger_c_api.ads': 'e095a573d30b0c3aabe63a23fd13dca59e9a664c381c8e306863b9b152704e1d', 'core/resource_run_ledger_wire.adb': 'c2feb75a7b3616968802469e7df304afcc9af6ac113a02222796487d0a6df0b3', 'core/resource_run_ledger_wire.ads': 'b09d4e07df8652f8f87b2a6526f0fa26875253ea1dc8909bbec6b330d6d02eed', 'core/worldline-owner_retry_audit.ads': 'f10e8a5758de157d40ab487c2b5071232cc8ede3b0984b36e75e922dff5b49e0', 'core/worldline-owner_retry_audit.adb': 'd444de903bc184300bbfd6e95348f4307827b7ad3948e4fe77c091daec52b5bd', 'core/worldline-owner_retry_audit_wire.ads': '60772578c6f02b53ea7b4d5614dde93f4e6d02e073847932c4647853d205f979', 'core/worldline-owner_retry_audit_wire.adb': 'ffeb183989406733268c9d25cac7b2501f1fb28bcf36af622ca1391e0bc9bd70', 'core/worldline-owner_conjunction.ads': '62559ebaa5c94a88435d44333ac61aede278af67813f3ab7ac72d27bd86ec89d', 'core/worldline-owner_conjunction.adb': '9d6f3f09c955a8612747f088a14802c5004a9a656009389e11254d6d623f3c32', 'core/worldline-owner_conjunction_wire.ads': 'a078f33e659fcb0c0eac74e63777425181bd5e2865566abfb79f36fc34aa510d', 'core/worldline-owner_conjunction_wire.adb': '8aedcbc566fc59ca8a600a6410199ef8ec31b3fbffb655e856e679007f0fc7c7', 'core/worldline-owner_subject_projection.ads': '2aa7d9d7208c340ae46ac36a4bf74d0dfe1ce2f53fdae435f95fcdc39479b7f7', 'core/worldline-owner_subject_projection.adb': 'abcf67952cd84158f7a536c8315402ab6a7cb3a9f32ba13e7587ad1d0119df72', 'core/worldline-recovery_protocol_abi.ads': '7ca9a017eb112cde748227006cd5c6ffccda126cd7dd09fa7d4c36b1499ab62b', 'core/worldline-recovery_protocol_abi.adb': '362c5447a336cb8a1a87a81ce42e0c02deb8c2224bfe5330e4ca8e9a653c5247', 'protocol-adapter-tests/protocol_adapter_tests.gpr': '7e57d05ba13972588bc37cbe9b3b1a1d5c64b297a92e52349df6f08fcb5fbe47', 'protocol-adapter-tests/test_protocol_adapter.adb': '6055576865adf8a23c98ae8b7c9def207c8f253debbeb0d39548a94fdc310680', 'epoch-correspondence-tests/epoch_correspondence_core_tests.gpr': '5216f9a5a0d7f9430e4f8fe400181a6d111179bff4520d981ae3c37d18f2bc4e', 'epoch-correspondence-tests/epoch_correspondence_pending_tests.gpr': '1af95a0f4a5851f4aac0775bd8d2493fa26224639d312f097db87fb88da8ba28', 'epoch-correspondence-tests/test_epoch_correspondence.adb': 'a297bb45d5c87dd010997741f10beb7598310dd7662a255e50ad51160dd88c1a', 'core/evaluation_finalization-values.adb': 'c6dd5ea011677b3a8ae31f9d5b2ccddd51fc5549ed5f07eef27add39a3ead320', 'core/evaluation_finalization-values.ads': 'f3fe2b54ad04f1a43c5fdd181fc149fffc3441f2b744b9da6da6ef8bab8d13ce', 'finalization-value-controls/finalization_value_controls.gpr': '756918630a4b54abaff8e68e4ae84aac7a7de2b670ebea00bb86b0a6edc6e421', 'finalization-value-controls/test_finalization_parent_values.adb': '9e87197fa326dc73f582f05cc473beff73d0b08c82da4dee29951827e358de28', 'finalization-value-controls/test_finalization_projection.adb': '669b4aa0804d272585ab5fa3569a7db4435e14ea0d7224165ee8470370ebdefd', 'finalization-value-controls/test_finalization_values.adb': '3242b812f6c19ea65f5d523c6155964e6e41b7b06976718f6391761db7106b6d', 'resources-prefix-correspondence-tests/resources_prefix_correspondence_tests.gpr': 'd238363ed2e518627c36a4afe965398ac4cef15b4264f7b3d50f25b771460978', 'resources-prefix-correspondence-tests/test_resources_prefix_correspondence.adb': 'ac4c037ecddd23d710e57e3dfe92534f0f2ee67ef943daa6947904d1c165c91e', 'wire-initialization-tests/test_wire_initialization.adb': 'e779f4827c714b6329addd074cdefee94737bbada08f81a82875a6a4daba000c', 'wire-initialization-tests/wire_initialization_tests.gpr': 'bfe67074a1b0fa4193667beae58279c4746b50f8a05a6c0184354dcbe7570224', 'resource-ledger-correspondence-tests/resource_ledger_correspondence_tests.gpr': 'd1f489d22d3508c17e9c529836ec22db29d339db94f5ed70a6a0b3c365883ec8', 'resource-ledger-correspondence-tests/test_resource_ledger_correspondence.adb': 'fdbcf441d1dcb1ef0e0568f36910c03d727b58f9da634bf96dbfd75a24116d32', 'decision-correspondence-tests/decision_correspondence_tests.gpr': '52637b39b04f201af2c2088f748a3ab7c1b032e813457638b12f1d6c18661016', 'decision-correspondence-tests/test_completion_correspondence.adb': '6ad18e9ec3136d2bf14ca45cb711801fc125ac6e307598ce0c7e0b5c6e36e945', 'decision-correspondence-tests/test_history_correspondence.adb': 'd293c070a38372238ac0c546deb2b8cab3df6f83ba21428f720ebccb6ed597cf', 'decision-correspondence-tests/test_raw_roster_correspondence.adb': 'ba17660670e42559e2b38af0d71f1c08c7126fbc527096bfb988e1aa2a59956b', 'decision-correspondence-tests/test_run_metadata_correspondence.adb': '93b4b7b7f610aaf0c844738886c347589769363e94f26d77edd4ccf4bedecad9', 'decision-correspondence-tests/test_transition_correspondence.adb': 'ac2b451ac7e78e52fcf4ee89d164fdb006f5326748517aa3b52cd99a00fb9fb1', 'core/evaluation_pending_c.ads': '62c2992c04c7eccbc8e89a71d2b2fa09a3d98c418d56fddd3775ad1236582710', 'core/evaluation_pending_c.adb': 'fa443db56f8e69122b9a57ec93d66bf1d9856a1fc3718b00ad2515958b8297a5', 'core/evaluation_pending_v2_c.ads': '79362e75326c104583ebd0222f97a180f4fabf6832c3e2f36ed21424bfc9b509', 'core/evaluation_pending_v2_c.adb': '060ca872213a86e6c126879ce4773d6e05431865e2d0fd6ea7b89ffb56b5bbf2', 'core/spark-big_integers.ads': 'f96017313a6e785d5c4697d95e610ced1a3612d20b7310dddb5af230226dbf1a', 'core/worldline-evaluation_history_c_api.ads': 'ebdc5645651239c8b29ca208e2e2ea72413169e84964ae0ee91c9c3251948d50', 'core/worldline-evaluation_history_c_api.adb': 'b8986e965b42fb3125c9dbcb19434246aeaaafa2c3d0206193b83df97a9686d9', 'core/worldline-recovery_c_api.ads': '6567180361bb753618586362db27eaaf858d373bf18576eebfeda82e4896d41e', 'core/worldline-recovery_c_api.adb': '33a09d32f02dfd789818414d528d3646d23df54643a11fd345b946a861a098d4', 'core/worldline-reservation_lifecycle_c_api.ads': '98a204b4536082d3c9cdef075800a58d6d335c3bedcf647e9c0ec44c02cc2c70', 'core/worldline-reservation_lifecycle_c_api.adb': 'be91398f93040875e0eba00b0f2cd454e1a851af7720efbcaf494987ac1f4dba', 'core/worldline-resource_ledger_c_api.ads': '34cf925193fd48acd782a0295d786a6aaada67d11b12082504df1dfac5ee360f', 'core/worldline-resource_ledger_c_api.adb': '587e08311372b9455a06e341d52e8f51b790949eeeeabf696f9ff422e22ffed1', 'core/worldline-resource_policy_c_api.ads': '1a4a9838dd42e70d3386db77642d9d272b3371e5e19537a80d58ae57ebf565b6', 'core/worldline-resource_policy_c_api.adb': '356d6426e8fef668d52be40bf578374bb9356b4898474216738fe8dc631a66c1', 'core/worldline-resources_c_api.ads': '2d5dfca12e0e053616fbcccc262dba093b8ebc9cc64840c3e8e28975731d14f3', 'core/worldline-resources_c_api.adb': 'def7d0d21088f6121441faca99afc3a76de4aa32ed4aa657493be1c34203da81', 'core/attest/attest-sha256.adb': '60ac468bec5bc75013407700b2122faa52a8295c4c43c19359a2e4fea4dc3be2'})

# Explicit complete marker values; original decision bodies and full domains stay required.
CONTRACT_PINS.update({'core/worldline-recovery.ads': 'b2eff79e29cd18c5a69672e3c6063faa120345d19a3f4cc76cf8ae31a69df7fc', 'explicit-recovery-marker-tests/test_explicit_recovery_markers.adb': '28b5ec869dfe195e56e2ebb0ced6fa999c5a1741723823a76a4ac13238eb4587', 'explicit-recovery-marker-tests/explicit_recovery_marker_tests.gpr': '384aebff4d2ab33af8d460dc1c3f74e7f6472db93333b637c3aed0076a05162c'})

# Explicit Phase One selected source composition. These names and units are
# obligations, not proof credit; the original 535 names remain the exact prefix
# and every full body, summary row and minimum check remains required.
REQUIRED_PROVED += ['Cosmogony.Capabilities.Well_Formed', 'Cosmogony.Capabilities.Rights_Within', 'Cosmogony.Capabilities.Scope_Within', 'Cosmogony.Capabilities.Attenuates', 'Cosmogony.Capabilities.Bound_To', 'Cosmogony.Capabilities.Role_Bounds_Grant', 'Cosmogony.Capabilities.Can_Derive', 'Cosmogony.Capabilities.Derive', 'Cosmogony.Capabilities.Scope_Allows', 'Cosmogony.Capabilities.Usage_Valid', 'Cosmogony.Capabilities.Has_Grant_Capacity', 'Cosmogony.Capabilities.Eligible', 'Cosmogony.Capabilities.Check_Request', 'Cosmogony.Genesis.Valid_Genesis', 'Cosmogony.Genesis.Role_Allows', 'Cosmogony.Genesis.Has_Capacity', 'Cosmogony.Genesis.Is_Forwardable', 'Cosmogony.Genesis.Is_Privileged', 'Cosmogony.Genesis.Bindings_Match', 'Cosmogony.Genesis.Eligible', 'Cosmogony.Genesis.Decide', 'Cosmogony.Governed_Capabilities.Gate_Open', 'Cosmogony.Governed_Capabilities.Can_Derive', 'Cosmogony.Governed_Capabilities.Derive', 'Cosmogony.Governed_Capabilities.Eligible', 'Cosmogony.Governed_Capabilities.Check_Request', 'Cosmogony.Revocable_Capabilities.Current_Link', 'Cosmogony.Revocable_Capabilities.Ancestry_Valid', 'Cosmogony.Revocable_Capabilities.Gate_Open', 'Cosmogony.Revocable_Capabilities.Can_Derive', 'Cosmogony.Revocable_Capabilities.Derive', 'Cosmogony.Revocable_Capabilities.Eligible', 'Cosmogony.Revocable_Capabilities.Check_Request', 'Cosmogony.Universes.Valid_Policy', 'Cosmogony.Universes.Quiet', 'Cosmogony.Universes.Snapshot_Ready', 'Cosmogony.Universes.Valid', 'Cosmogony.Universes.Can_Transition', 'Cosmogony.Universes.Same_Except_Life', 'Cosmogony.Universes.Transition', 'Cosmogony.Universes.Can_Revise', 'Cosmogony.Universes.Same_Except_Revision', 'Cosmogony.Universes.Revise', 'Cosmogony.Universes.Can_Capture_Snapshot', 'Cosmogony.Universes.Capture_Snapshot', 'Cosmogony.Universes.Can_Advance_Prime', 'Cosmogony.Universes.Advance_Prime', 'Cosmogony.Universes.Bind_Evidence', 'Cosmogony.Universes.Evidence_Current', 'Cosmogony.Universes.Genesis_Binds', 'Cosmogony.Universes.Governed_Decide', 'Decimal_Binary64.Magnitude', 'Decimal_Binary64.Finite', 'Decimal_Binary64.Valid', 'Decimal_Binary64.Numerator_Model', 'Decimal_Binary64.Denominator_Model', 'Decimal_Binary64.Value', 'Decimal_Binary64.Less', 'Decimal_Binary64.Equal', 'Decimal_Binary64.Midpoint', 'Decimal_Binary64.Rounds_To', 'Decimal_Binary64.Overflows', 'Decimal_Binary64.Round', 'Decimal_Binary64.Decimal_Denotation', 'Decimal_Binary64.Input_Finite', 'Decimal_Binary64.Input_Rounds_To', 'Decimal_Binary64.Convert', 'Decimal_Binary64.Expected_Repr', 'Decimal_Binary64.Repr', 'Decimal_Binary64.Spelling_Matches', 'Decimal_Binary64.Canonical', 'Exact_Decimal.Digit', 'Exact_Decimal.Digit_Fold', 'Exact_Decimal.Fraction_Digits', 'Exact_Decimal.Exponent_Value', 'Exact_Decimal.Digit_Count', 'Exact_Decimal.Parse', 'Exact_Decimal.Power_Model', 'Exact_Decimal.Power', 'Resource_Actor_Admission.Number', 'Resource_Actor_Admission.Eq', 'Resource_Actor_Admission.Is_Number', 'Resource_Actor_Admission.Complete', 'Resource_Actor_Admission.Requester_Holds', 'Resource_Actor_Admission.Source_Holds', 'Resource_Actor_Admission.Credential_Holds', 'Resource_Actor_Admission.Isolation_Reference', 'Resource_Actor_Admission.Isolation', 'Resource_Actor_Admission.Running_Holds', 'Resource_Actor_Admission.Reference', 'Resource_Actor_Admission.Check', 'Resource_Actor_Admission_Wire.Well_Formed', 'Resource_Actor_Admission_Wire.Decode', 'Resource_Actor_Admission_Wire.Decode_Capabilities', 'Resource_Actor_Admission_Wire.Decode_Groups', 'Resource_Observation_Classification.Text', 'Resource_Observation_Classification.Events', 'Resource_Observation_Classification.Zero', 'Resource_Observation_Classification.Current_Reference', 'Resource_Observation_Classification.Current', 'Resource_Observation_Classification.Genesis_Reference', 'Resource_Observation_Classification.Genesis_Current', 'Resource_Observation_Classification.Common', 'Resource_Observation_Classification.Custody', 'Resource_Observation_Classification.Never_Holds', 'Resource_Observation_Classification.Live_Holds', 'Resource_Observation_Classification.Reaped_Holds', 'Resource_Observation_Classification.Reference', 'Resource_Observation_Classification.Classify', 'Resource_Observation_Classification_Wire.Well_Formed', 'Resource_Observation_Classification_Wire.Decode', 'Resource_Observation_Classification_Wire.Current_Reference', 'Resource_Observation_Classification_Wire.Current', 'Resource_Observation_Classification_Wire.Genesis_Reference', 'Resource_Observation_Classification_Wire.Genesis_Current', 'Resource_Observation_Classification_Wire.Reference', 'Resource_Observation_Classification_Wire.Classify', 'Resource_Scoped_Run_Ledger.Frame_Valid', 'Resource_Scoped_Run_Ledger.Same_Frame', 'Resource_Scoped_Run_Ledger.History_Valid', 'Resource_Scoped_Run_Ledger.Origin', 'Resource_Scoped_Run_Ledger.Retained_Origin', 'Resource_Scoped_Run_Ledger.Shape', 'Resource_Scoped_Run_Ledger.Key_Valid', 'Resource_Scoped_Run_Ledger.Same_Key', 'Resource_Scoped_Run_Ledger.Projection_Valid', 'Resource_Scoped_Run_Ledger.Same_Projection_Origin', 'Resource_Scoped_Run_Ledger.Physical_Roster', 'Resource_Scoped_Run_Ledger.Charge_Reference', 'Resource_Scoped_Run_Ledger.Charge', 'Resource_Scoped_Run_Ledger.Bucket_Valid', 'Resource_Scoped_Run_Ledger.Physical_Reference', 'Resource_Scoped_Run_Ledger.Physical', 'Resource_Scoped_Run_Ledger.Contained_Reference', 'Resource_Scoped_Run_Ledger.Contained', 'Resource_Scoped_Run_Ledger.Current_Valid', 'Resource_Scoped_Run_Ledger.Classify_Reference', 'Resource_Scoped_Run_Ledger.Classify', 'Resource_Scoped_Run_Ledger.Native_Valid', 'Resource_Scoped_Run_Ledger.History_Prefix', 'Resource_Scoped_Run_Ledger.Projection_Prefix', 'Resource_Scoped_Run_Ledger.Bucket_Retained', 'Resource_Scoped_Run_Ledger.Buckets_Observed', 'Resource_Scoped_Run_Ledger.Within_Capacity', 'Resource_Scoped_Run_Ledger.No_Amplification', 'Resource_Scoped_Run_Ledger.Current_Facts', 'Resource_Scoped_Run_Ledger.Valid_Reference', 'Resource_Scoped_Run_Ledger.Valid', 'Resource_Scoped_Run_Ledger.Advance_Valid', 'Resource_Scoped_Run_Ledger.Ordinary_Reference', 'Resource_Scoped_Run_Ledger.Ordinary_Relation', 'Resource_Scoped_Run_Ledger.Decision_Reference', 'Resource_Scoped_Run_Ledger.Check', 'Resource_Scoped_Run_Ledger_Wire.Well_Formed', 'Resource_Scoped_Run_Ledger_Wire.Decode', 'Resource_Scoped_Run_Ledger_Wire.Decode_History', 'Resource_Scoped_Run_Ledger_Wire.Decode_Bucket', 'Resource_Scoped_Run_Ledger_Wire.Decode_Projection', 'Resource_Scoped_Run_Ledger_Wire.Decode_Facts', 'Resource_Scoped_Run_Ledger_Wire.Decide', 'Resource_Scoped_Run_Ledger_Wire.Validate', 'Resource_Scoped_Run_Ledger_Wire.Selected_Reference', 'Resource_Scoped_Run_Ledger_Wire.Classify_Selected', 'Worldline.Actor_Archive_Replay.Reestablish_Actor_Observation', 'Worldline.Actor_Archive_Replay.Operation_Boundary_Matches', 'Worldline.Archive_Envelope.Bytes_Valid', 'Worldline.Archive_Envelope.Materialize', 'Worldline.Archive_Envelope.Array_Element', 'Worldline.Archive_Envelope.Array_Length', 'Worldline.Archive_Envelope.Is_Array', 'Worldline.Archive_Envelope.Decode', 'Worldline.Archive_Envelope.Text_Is', 'Worldline.Confinement_Filter.Establishes', 'Worldline.Custody_V2_K4_Resource_Ack.Establish_History', 'Worldline.Custody_V2_K4_Resource_Ack.Current_Matches', 'Worldline.Custody_V2_K4_Resource_Ack.Source_Matches', 'Worldline.Custody_V2_K4_Resource_Ack.Authenticated', 'Worldline.Custody_V2_K4_Resource_Ack.Direct_Authenticated', 'Worldline.Custody_V2_K4_Resource_Ack.Current_Authenticated', 'Worldline.Custody_V2_Owner_Canonical.Extract_Replay_Capsules', 'Worldline.Custody_V2_Owner_Canonical.Establish_History', 'Worldline.Custody_V2_Owner_Canonical.Current_Matches', 'Worldline.Custody_V2_Owner_Canonical.Source_Matches', 'Worldline.Custody_V2_Owner_Canonical.Authenticated', 'Worldline.Custody_V2_Owner_Canonical.Current_History_Authenticated', 'Worldline.Custody_V2_Owner_Canonical.Reserved_Redecided', 'Worldline.Custody_V2_Owner_Canonical.Adopt_Settled_Redecided', 'Worldline.Evaluation_Agent_Native.Supervisor_Decide', 'Worldline.Evaluation_Agent_Native.Decide', 'Worldline.Evaluation_Policy.Required_Count', 'Worldline.Evaluation_Policy.Required', 'Worldline.Evaluation_Policy.Empty_Declared', 'Worldline.Evaluation_Policy.Declaration', 'Worldline.Evaluation_Policy.Declaration_Count', 'Worldline.Evaluation_Policy.Declaration_Name', 'Worldline.Evaluation_Policy.Project', 'Worldline.Evaluation_Policy.Policy_Same', 'Worldline.Evaluation_Policy.Verifiers_Modified', 'Worldline.Evaluation_Policy.Prefix', 'Worldline.Evaluation_Policy.Return_Row', 'Worldline.Evaluation_Policy.Capture_Plan', 'Worldline.Evaluation_Producer.Original_Projection', 'Worldline.Evaluation_Producer.Derive', 'Worldline.Evaluation_Role_Native.Valid', 'Worldline.Evaluation_Role_Native.Original_Observed', 'Worldline.Evaluation_Role_Native.Original_Workers_Separated', 'Worldline.Journal_Witness.Decide', 'Worldline.Lifetime_Values.Parse', 'Worldline.Lifetime_Values.Element', 'Worldline.Lifetime_Values.Text', 'Worldline.Lifetime_Values.Bytes', 'Worldline.Lifetime_Values.Equal', 'Worldline.Lifetime_Values.Compare', 'Worldline.Lifetime_Values.Matches', 'Worldline.Lifetime_Values.Nonnegative', 'Worldline.Lifetime_Values.Positive_Integer', 'Worldline.Lifetime_Values.Mod_256', 'Worldline.Lifetime_Values.Word', 'Worldline.Lifetime_Values.Complete', 'Worldline.Manager_Resource_Lifecycle.Unit_Valid', 'Worldline.Manager_Resource_Lifecycle.Identity_Valid', 'Worldline.Manager_Resource_Lifecycle.Events_State', 'Worldline.Manager_Resource_Lifecycle.Decide', 'Worldline.Native_Execution_Capture.Scoped_Check', 'Worldline.Native_Execution_Capture.Scoped_Validate', 'Worldline.Native_Execution_Capture.Scoped_Classify', 'Worldline.Native_Execution_Capture.Observation_Classify', 'Worldline.Native_Execution_Capture.Observation_Current', 'Worldline.Native_Execution_Capture.Observation_Genesis_Current', 'Worldline.Native_Execution_Capture.Actor_Check', 'Worldline.Native_Execution_Capture.Operation_Decide', 'Worldline.Native_Execution_Capture.Execution_Decide', 'Worldline.Native_Execution_Capture.Child_Decide', 'Worldline.Native_Execution_Views.Scoped_Check', 'Worldline.Native_Execution_Views.Scoped_Validate', 'Worldline.Native_Execution_Views.Scoped_Classify', 'Worldline.Native_Execution_Views.Observation_Classify', 'Worldline.Native_Execution_Views.Observation_Current', 'Worldline.Native_Execution_Views.Observation_Genesis_Current', 'Worldline.Native_Execution_Views.Actor_Expected', 'Worldline.Native_Execution_Views.Actor_Check', 'Worldline.Native_Execution_Views.Operation_Expected', 'Worldline.Native_Execution_Views.Operation_Decide', 'Worldline.Native_Execution_Views.Execution_Expected', 'Worldline.Native_Execution_Views.Execution_Decide', 'Worldline.Native_Execution_Views.Child_Expected', 'Worldline.Native_Execution_Views.Child_Decide', 'Worldline.Native_Lifetime_Observation.Clean', 'Worldline.Operation_Archive.Record_Fields', 'Worldline.Operation_Archive.Valid', 'Worldline.Operation_Archive.Field', 'Worldline.Operation_Archive.Same_Encoding', 'Worldline.Operation_Authority.Same', 'Worldline.Operation_Authority.Owner_Only', 'Worldline.Operation_Authority.Transaction_Operation', 'Worldline.Operation_Authority.Valid', 'Worldline.Operation_Authority.Grant_Valid', 'Worldline.Operation_Authority.Attenuates', 'Worldline.Operation_Authority.Roster_Valid', 'Worldline.Operation_Authority.Ancestor', 'Worldline.Operation_Authority.Count_Reference', 'Worldline.Operation_Authority.Count_Uses', 'Worldline.Operation_Authority.Eligible', 'Worldline.Operation_Authority.Reservation_Reference', 'Worldline.Operation_Authority.Reservation_Decision', 'Worldline.Operation_Authority.Chain_Effect', 'Worldline.Operation_Authority.Followup_Reference', 'Worldline.Operation_Authority.Execution_Reference', 'Worldline.Operation_Authority.Reference', 'Worldline.Operation_Authority.Decide', 'Worldline.Operation_Authority_Wire.Well_Formed', 'Worldline.Operation_Authority_Wire.Effect_Material_Well_Formed', 'Worldline.Operation_Authority_Wire.Decode', 'Worldline.Operation_Authority_Wire.Recovery_Well_Formed', 'Worldline.Operation_Result_Relations.Capture_Source_Reference', 'Worldline.Operation_Result_Relations.Result_Source_Reference', 'Worldline.Operation_Result_Relations.Capture_Reference', 'Worldline.Operation_Result_Relations.Result_Reference', 'Worldline.Operation_Result_Relations.Payloads_Reference', 'Worldline.Operation_Result_Relations.Assessment_Reference', 'Worldline.Operation_Result_Relations.Assess', 'Worldline.Operation_Result_Relations.Capture_Matches', 'Worldline.Operation_Result_Relations.Result_Matches', 'Worldline.Operation_Result_Relations.Payloads_Match', 'Worldline.Operation_Result_Relations.Matches', 'Worldline.Operation_Result_View.Expected', 'Worldline.Operation_Result_View.Check', 'Worldline.Ordinary_Receipt_Policy.Metadata_Truth', 'Worldline.Ordinary_Receipt_Policy.Schema_Status', 'Worldline.Ordinary_Receipt_Policy.Requester_Profile', 'Worldline.Ordinary_Receipt_Policy.Receipt_Predecessor_Status', 'Worldline.Ordinary_Receipt_Policy.Receipt_Name_Status', 'Worldline.Ordinary_Receipt_Policy.Effect_Table_Schema', 'Worldline.Ordinary_Receipt_Policy.Native_Write_Matches', 'Worldline.Ordinary_Receipt_Policy.Actual_Route', 'Worldline.Ordinary_Receipt_Policy.Column_Name', 'Worldline.Ordinary_Receipt_Policy.Verify_History', 'Worldline.Ordinary_Receipt_Policy.Schema_One', 'Worldline.Ordinary_Receipt_Policy.Reserved_Actor_Name', 'Worldline.Ordinary_Receipt_Policy.Reserved_Kind_Name', 'Worldline.Ordinary_Receipt_Policy.Receipt_Fields', 'Worldline.Ordinary_Receipt_Policy.History', 'Worldline.Ordinary_Receipt_Policy.Reference', 'Worldline.Ordinary_Receipt_Policy.Decide', 'Worldline.Ordinary_Reservation_Lifecycle.Plan', 'Worldline.Policy_Source.Observe', 'Worldline.Policy_Source.Current_Matches', 'Worldline.Policy_Syntax.Valid', 'Worldline.Producer_Bytes.Base64_Extent', 'Worldline.Producer_Bytes.Decode_Base64', 'Worldline.Producer_Bytes.Base64', 'Worldline.Producer_Bytes.Digest', 'Worldline.Producer_Render.Quote', 'Worldline.Producer_Render.Python_String', 'Worldline.Producer_Unicode.Printable', 'Worldline.Producer_Values.Parse', 'Worldline.Producer_Values.Member_Key', 'Worldline.Producer_Values.Standard_JSON', 'Worldline.Producer_Values.Duplicate_Free', 'Worldline.Producer_Values.Original_Exact_JSON', 'Worldline.Producer_Values.UTF8_Width', 'Worldline.Producer_Values.Number_Image', 'Worldline.Producer_Values.Field', 'Worldline.Producer_Values.Element', 'Worldline.Producer_Values.Count', 'Worldline.Producer_Values.Text', 'Worldline.Producer_Values.Is_Text', 'Worldline.Producer_Values.Is_True', 'Worldline.Producer_Values.Is_False', 'Worldline.Producer_Values.Is_Null', 'Worldline.Producer_Values.Present', 'Worldline.Producer_Values.Nonempty_Text', 'Worldline.Producer_Values.Equal', 'Worldline.Producer_Values.Truth', 'Worldline.Producer_Values.Decimal', 'Worldline.Producer_Values.Nonnegative', 'Worldline.Producer_Values.Slice', 'Worldline.Producer_Values.Member_Name', 'Worldline.Producer_Values.Kind', 'Worldline.Producer_Values.Quote', 'Worldline.Producer_Values.Python_String', 'Worldline.Protected_Paths.Matches', 'Worldline.Protected_Paths.Touched', 'Worldline.Raw_JSON.Decode_JSON', 'Worldline.Raw_JSON.Original_Exact_JSON', 'Worldline.Raw_JSON.Raw_JSON_Operation_Matches', 'Worldline.Raw_JSON.Ordinary_JSON_Operation_Matches', 'Worldline.Raw_JSON.Ordinary_JSON_Scoped_Matches', 'Worldline.Raw_JSON.JSON_Source_Value_Matches', 'Worldline.Raw_JSON.Ordinary_JSON_Finalization_Matches', 'Worldline.Raw_JSON.Raw_JSON_Scoped_Matches', 'Worldline.Raw_JSON.Raw_JSON_Operation_Equal', 'Worldline.Raw_JSON.Raw_JSON_Scoped_Equal', 'Worldline.Raw_JSON.Python_JSON_Equal', 'Worldline.Raw_JSON.Canonical_ASCII_Quote', 'Worldline.Raw_JSON.Canonical_ASCII_Valid', 'Worldline.Recovery_Archive.Record_Is', 'Worldline.Recovery_Archive.Valid', 'Worldline.Recovery_Archive.Field', 'Worldline.Recovery_Archive.Same_Encoding', 'Worldline.Recovery_Archive.Equal', 'Worldline.Recovery_Archive.Equal_Operation', 'Worldline.Recovery_Archive.Valid_Finalization_Record', 'Worldline.Recovery_Archive.Finalization_Record_Field', 'Worldline.Recovery_Archive.Equal_Finalization_Record', 'Worldline.Recovery_Archive.Source_Valid', 'Worldline.Recovery_Archive.Source_Value_Matches', 'Worldline.Recovery_Archive.Text_Is', 'Worldline.Recovery_Archive.Boolean_Is', 'Worldline.Recovery_Archive.Stored_Bytes_Valid', 'Worldline.Recovery_Archive.Stored_Bytes', 'Worldline.Recovery_Archive.Integer_Valid', 'Worldline.Recovery_Archive.Integer_Negative', 'Worldline.Recovery_Archive.Integer_Magnitude', 'Worldline.Recovery_Material_Replay.JSON', 'Worldline.Recovery_Material_Replay.JSON_Valid', 'Worldline.Recovery_Material_Replay.Syntax_Inputs', 'Worldline.Recovery_Material_Replay.Rebuild', 'Worldline.Recovery_Material_Replay.Bind', 'Worldline.Recovery_Material_Replay.Agent_Matches', 'Worldline.Recovery_Material_Replay.Agent_Admitted', 'Worldline.Recovery_Material_Replay.Row_Count', 'Worldline.Recovery_Material_Replay.Arena_Length', 'Worldline.Recovery_Material_Replay.Classify_All', 'Worldline.Recovery_Material_Replay.Owner_Selected', 'Worldline.Recovery_Material_Replay.Owner_Promotion', 'Worldline.Recovery_Owner_Replay.Matches', 'Worldline.Recovery_Owner_Replay.Decide', 'Worldline.Recovery_Owner_Replay.Decode_Request', 'Worldline.Recovery_Owner_Replay.Decode_Receipt', 'Worldline.Recovery_Owner_Replay.Decode_Identity', 'Worldline.Recovery_Owner_Replay.Decode_Epoch', 'Worldline.Recovery_Owner_Replay.Decode_Cursor', 'Worldline.Recovery_Owner_Replay.Decode_Scope', 'Worldline.Recovery_Owner_Replay.Decode_Hash', 'Worldline.Recovery_Packet.Decode', 'Worldline.Recovery_Packet.Inspect', 'Worldline.Recovery_Packet.Projection_Matches', 'Worldline.Recovery_Packet.Complete', 'Worldline.Recovery_Syntax.Valid', 'Worldline.Recovery_Syntax.Find', 'Worldline.Recovery_Syntax.Operand_Text', 'Worldline.Report_Custody_Native.Observe', 'Worldline.Report_Custody_Native.Captured', 'Worldline.Report_Parser.Parse', 'Worldline.Resource_Actor_Execution.Digest_Matches', 'Worldline.Resource_Actor_Execution.Epoch_Matches', 'Worldline.Resource_Actor_Execution.Crosswalk_Valid', 'Worldline.Resource_Actor_Execution.Same_Current', 'Worldline.Resource_Actor_Execution.Original_Holds', 'Worldline.Resource_Actor_Execution.Current_Holds', 'Worldline.Resource_Actor_Execution.Reference', 'Worldline.Resource_Actor_Execution.Decide', 'Worldline.Resource_Actor_Execution_Wire.Well_Formed', 'Worldline.Resource_Actor_Execution_Wire.Decode', 'Worldline.Resource_Child_Execution.Number_Valid', 'Worldline.Resource_Child_Execution.Number_Same', 'Worldline.Resource_Child_Execution.Process_Valid', 'Worldline.Resource_Child_Execution.Same_Process', 'Worldline.Resource_Child_Execution.Controller_Valid', 'Worldline.Resource_Child_Execution.Original_Root_Holds', 'Worldline.Resource_Child_Execution.Root_Controller_Holds', 'Worldline.Resource_Child_Execution.Task_Valid', 'Worldline.Resource_Child_Execution.Same_Task', 'Worldline.Resource_Child_Execution.Task_Roster_Valid', 'Worldline.Resource_Child_Execution.Child_Holds', 'Worldline.Resource_Child_Execution.Parent_Holds', 'Worldline.Resource_Child_Execution.Process_Ancestry', 'Worldline.Resource_Child_Execution.Namespace_Ancestry', 'Worldline.Resource_Child_Execution.Root_Admission_Reference', 'Worldline.Resource_Child_Execution.Root_Admission', 'Worldline.Resource_Child_Execution.Reference', 'Worldline.Resource_Child_Execution.Decide', 'Worldline.Resource_Child_Execution.Task_Request_Holds', 'Worldline.Resource_Child_Execution.Root_Refines_Original', 'Worldline.Resource_Child_Execution.Task_Admission_Reference', 'Worldline.Resource_Child_Execution.Task_Admission', 'Worldline.Resource_Child_Execution_Wire.Well_Formed', 'Worldline.Resource_Child_Execution_Wire.Decode', 'Worldline.Resource_Child_Execution_Wire.Decode_Process', 'Worldline.Resource_Child_Execution_Wire.Decode_Task', 'Worldline.Resource_Child_Execution_Wire.Decode_Namespace', 'Worldline.Retained_Evidence_Replay.Reestablish_Root_Observation', 'Worldline.Retained_Evidence_Replay.Reestablish_Scoped_Observation', 'Worldline.Retained_Evidence_Replay.Reestablish_Operation_Observation', 'Worldline.Retained_Evidence_Replay.Scoped_Identity_Matches', 'Worldline.Retained_Evidence_Replay.Root_Material_Matches', 'Worldline.Retained_Evidence_Replay.Scoped_Material_Matches', 'Worldline.Retained_Evidence_Replay.Operation_Material_Matches', 'Worldline.Retained_Evidence_Replay.Reestablish_Exchange_Observation', 'Worldline.Retained_Evidence_Replay.Exchange_Material_Matches', 'Worldline.Retained_Evidence_Replay.Root_Capture_Matches', 'Worldline.Retained_Evidence_Replay.Operation_Capture_Matches', 'Worldline.Retained_Evidence_Replay.Archive_Field', 'Worldline.Retained_Evidence_Replay.Decode_Collapse_Values', 'Worldline.Retained_Evidence_Replay.Reestablish_Reservation_Observation', 'Worldline.Retained_Evidence_Replay.Reservation_Material_Matches', 'Worldline.Retained_Evidence_Replay.Archive_Text_Is', 'Worldline.Retained_Evidence_Replay.Archive_Boolean_Is', 'Worldline.Retained_Evidence_Replay.Archive_Bytes_Valid', 'Worldline.Retained_Evidence_Replay.Archive_Bytes', 'Worldline.Retained_Evidence_Replay.Archive_Integer_Valid', 'Worldline.Retained_Evidence_Replay.Archive_Integer_Negative', 'Worldline.Retained_Evidence_Replay.Archive_Integer_Magnitude', 'Worldline.Retained_Evidence_Replay.Archive_Is_None', 'Worldline.Retained_Evidence_Replay.Archive_Length', 'Worldline.Retained_Evidence_Replay.Archive_Index', 'Worldline.Retained_Evidence_Replay.Archive_Record_Is', 'Worldline.Retained_Evidence_Replay.Archive_Is_Sequence', 'Worldline.Retained_Evidence_Replay.Archive_Equal', 'Worldline.Retained_Evidence_Replay.Archive_Image_Matches', 'Worldline.Retained_Evidence_Replay.Decode_Recovery_Collapse_Values', 'Worldline.Retained_Evidence_Replay.Actor_Material_Matches', 'Worldline.Retained_Evidence_Replay.Root_Scoped_Material_Matches', 'Worldline.Retained_Raw_Decode.Load', 'Worldline.Retained_Raw_Decode.Source_Padding_Valid', 'Worldline.Retained_Source_Layout.Start', 'Worldline.Retained_Source_Layout.Complete', 'Worldline.Retained_Source_Layout.Append', 'Worldline.Retained_Source_Layout.Unused_Row', 'Worldline.Runner_Acquisition_Bytes.Closed', 'Worldline.Runner_Lifecycle.Ended', 'Worldline.Runner_Lifecycle.Commands_Ended', 'Worldline.Runner_Lifecycle.Eof_Complete', 'Worldline.Runner_Lifecycle.Proxy_Ended', 'Worldline.Runner_Lifecycle.Quiescent', 'Worldline.Runner_Lifecycle.Finalization_Quiescent', 'Worldline.Runner_Lifecycle.Generation_Stable', 'Worldline.Runner_Lifecycle.Finished', 'Worldline.Runner_Lifecycle.Cancellation_Membership', 'Worldline.Runner_Lifecycle.Cancellation_Membership_Valid', 'Worldline.Runner_Lifecycle.Allowed', 'Worldline.Runner_Lifecycle_Bytes.Quiescent', 'Worldline.Runner_Lifecycle_Bytes.Finalization_Quiescent', 'Worldline.Runner_Lifecycle_Bytes.Field', 'Worldline.Runner_Lifecycle_Bytes.Text_Is', 'Worldline.Runner_Lifecycle_Bytes.Equal', 'Worldline.Runner_Lifecycle_Bytes.Truth', 'Worldline.Runner_Lifecycle_Bytes.Is_True', 'Worldline.Runner_Lifecycle_Bytes.Is_False', 'Worldline.Runner_Lifecycle_Bytes.Ended', 'Worldline.Runner_Lifecycle_Bytes.Commands_Ended', 'Worldline.Runner_Lifecycle_Bytes.Eof_Complete', 'Worldline.Runner_Lifecycle_Bytes.Proxy_Ended', 'Worldline.Runner_Lifecycle_Bytes.Finished', 'Worldline.Runner_Lifecycle_Bytes.Generation_Stable', 'Worldline.Runner_Lifecycle_Bytes.Cancellation_Membership_Valid', 'Worldline.Runner_Lifecycle_Bytes.Cancellation_Membership', 'Worldline.Runner_Lifecycle_Bytes.Allowed', 'Worldline.Runner_Lifecycle_Bytes.Text_Equal', 'Worldline.Runner_Outcome.Decide', 'Worldline.Runner_Outcome_Bytes.Decide', 'Worldline.Source_Audit_Native.Clean', 'Worldline.Source_Syntax.Valid', 'Worldline.Source_Syntax_Provider.Project', 'Worldline.Source_Syntax_Provider.Authentic', 'Worldline.Source_Syntax_Provider.Original_Joined', 'Worldline.Source_Syntax_Reference.Matches', 'Worldline.Startup_Admission.Observe', 'Worldline.Startup_Admission.Observe_Owner', 'Worldline.Startup_Admission.Decide', 'Worldline.Startup_Admission.Decide_Owner', 'Worldline.Startup_Admission.Operation_Source_Corresponds', 'Worldline.Startup_Admission.All_Required_Admissions_Consumed', 'Worldline.Startup_Admission.Transition_Matches', 'Worldline.Startup_Admission.Owner_Transition_Matches', 'Worldline.Startup_Admission_Owned.Runtime_Decide', 'Worldline.Startup_Admission_Owned.Owner_Decide', 'Worldline.Startup_Admission_Owned.Runtime_Transition', 'Worldline.Startup_Admission_Owned.Owner_Transition', 'Worldline.Startup_Installation.Path_Bytes_Equivalent', 'Worldline.Startup_Installation.Path_Equivalent', 'Worldline.Startup_Installation.Joined_Path', 'Worldline.Startup_Installation.Corresponds', 'Worldline.Startup_Installation.Stable', 'Worldline.Startup_Issuer_Source.Corresponds', 'Worldline.Startup_Source_Custody.Corresponds', 'Worldline.Startup_Source_Custody.File_Corresponds', 'Worldline.Startup_Source_Custody.Unselected_Path', 'Worldline.Transaction_Archive_JSON.Render', 'Worldline.Transaction_Relations.Freshness', 'Worldline.Transaction_Relations.Execution', 'Worldline.Transaction_Relations.Record_Matches', 'Worldline.Transaction_Relations.Manifests', 'Worldline.Transaction_Relations.Marker_State', 'Worldline.Transaction_Relations.Committed_Result_Matches', 'Worldline.Transaction_Relations.Decide']
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/cosmogony-capabilities.adb', 'core/cosmogony-capabilities.ads', 'core/cosmogony-genesis.adb', 'core/cosmogony-genesis.ads', 'core/cosmogony-governed_capabilities.adb', 'core/cosmogony-governed_capabilities.ads', 'core/cosmogony-revocable_capabilities.adb', 'core/cosmogony-revocable_capabilities.ads', 'core/cosmogony-universes.adb', 'core/cosmogony-universes.ads', 'core/cosmogony.ads', 'core/decimal_binary64.adb', 'core/decimal_binary64.ads', 'core/exact_decimal.adb', 'core/exact_decimal.ads', 'core/genesis_float_domain_controls.adb', 'core/resource_actor_admission.adb', 'core/resource_actor_admission.ads', 'core/resource_actor_admission_wire.adb', 'core/resource_actor_admission_wire.ads', 'core/resource_observation_classification.adb', 'core/resource_observation_classification.ads', 'core/resource_observation_classification_wire.adb', 'core/resource_observation_classification_wire.ads', 'core/resource_scoped_run_ledger.adb', 'core/resource_scoped_run_ledger.ads', 'core/resource_scoped_run_ledger_wire.adb', 'core/resource_scoped_run_ledger_wire.ads', 'core/worldline-actor_archive_replay.adb', 'core/worldline-actor_archive_replay.ads', 'core/worldline-archive_envelope.adb', 'core/worldline-archive_envelope.ads', 'core/worldline-confinement_filter.adb', 'core/worldline-confinement_filter.ads', 'core/worldline-custody_v2_k4_resource_ack.adb', 'core/worldline-custody_v2_k4_resource_ack.ads', 'core/worldline-custody_v2_owner_canonical.adb', 'core/worldline-custody_v2_owner_canonical.ads', 'core/worldline-evaluation_agent_native.adb', 'core/worldline-evaluation_agent_native.ads', 'core/worldline-evaluation_policy.adb', 'core/worldline-evaluation_policy.ads', 'core/worldline-evaluation_producer.adb', 'core/worldline-evaluation_producer.ads', 'core/worldline-evaluation_role_native.adb', 'core/worldline-evaluation_role_native.ads', 'core/worldline-journal_witness.adb', 'core/worldline-journal_witness.ads', 'core/worldline-lifetime_values.adb', 'core/worldline-lifetime_values.ads', 'core/worldline-manager_resource_lifecycle.adb', 'core/worldline-manager_resource_lifecycle.ads', 'core/worldline-native_execution_capture.adb', 'core/worldline-native_execution_capture.ads', 'core/worldline-native_execution_views.adb', 'core/worldline-native_execution_views.ads', 'core/worldline-native_lifetime_observation.adb', 'core/worldline-native_lifetime_observation.ads', 'core/worldline-operation_archive.adb', 'core/worldline-operation_archive.ads', 'core/worldline-operation_authority.adb', 'core/worldline-operation_authority.ads', 'core/worldline-operation_authority_wire.adb', 'core/worldline-operation_authority_wire.ads', 'core/worldline-operation_result_relations.adb', 'core/worldline-operation_result_relations.ads', 'core/worldline-operation_result_view.adb', 'core/worldline-operation_result_view.ads', 'core/worldline-ordinary_receipt_policy.adb', 'core/worldline-ordinary_receipt_policy.ads', 'core/worldline-ordinary_reservation_lifecycle.adb', 'core/worldline-ordinary_reservation_lifecycle.ads', 'core/worldline-policy_source.adb', 'core/worldline-policy_source.ads', 'core/worldline-policy_syntax.adb', 'core/worldline-policy_syntax.ads', 'core/worldline-producer_bytes.adb', 'core/worldline-producer_bytes.ads', 'core/worldline-producer_render.adb', 'core/worldline-producer_render.ads', 'core/worldline-producer_unicode.ads', 'core/worldline-producer_values.adb', 'core/worldline-producer_values.ads', 'core/worldline-protected_paths.adb', 'core/worldline-protected_paths.ads', 'core/worldline-raw_json.adb', 'core/worldline-raw_json.ads', 'core/worldline-recovery_archive.adb', 'core/worldline-recovery_archive.ads', 'core/worldline-recovery_material_replay.adb', 'core/worldline-recovery_material_replay.ads', 'core/worldline-recovery_owner_replay.adb', 'core/worldline-recovery_owner_replay.ads', 'core/worldline-recovery_packet.adb', 'core/worldline-recovery_packet.ads', 'core/worldline-recovery_syntax.adb', 'core/worldline-recovery_syntax.ads', 'core/worldline-report_custody_native.adb', 'core/worldline-report_custody_native.ads', 'core/worldline-report_parser.adb', 'core/worldline-report_parser.ads', 'core/worldline-resource_actor_execution.adb', 'core/worldline-resource_actor_execution.ads', 'core/worldline-resource_actor_execution_wire.adb', 'core/worldline-resource_actor_execution_wire.ads', 'core/worldline-resource_child_execution.adb', 'core/worldline-resource_child_execution.ads', 'core/worldline-resource_child_execution_wire.adb', 'core/worldline-resource_child_execution_wire.ads', 'core/worldline-retained_evidence_replay.adb', 'core/worldline-retained_evidence_replay.ads', 'core/worldline-retained_raw_decode.adb', 'core/worldline-retained_raw_decode.ads', 'core/worldline-retained_source_layout.adb', 'core/worldline-retained_source_layout.ads', 'core/worldline-runner_acquisition_bytes.adb', 'core/worldline-runner_acquisition_bytes.ads', 'core/worldline-runner_lifecycle.adb', 'core/worldline-runner_lifecycle.ads', 'core/worldline-runner_lifecycle_bytes.adb', 'core/worldline-runner_lifecycle_bytes.ads', 'core/worldline-runner_outcome.adb', 'core/worldline-runner_outcome.ads', 'core/worldline-runner_outcome_bytes.adb', 'core/worldline-runner_outcome_bytes.ads', 'core/worldline-source_audit_native.adb', 'core/worldline-source_audit_native.ads', 'core/worldline-source_syntax.adb', 'core/worldline-source_syntax.ads', 'core/worldline-source_syntax_provider.adb', 'core/worldline-source_syntax_provider.ads', 'core/worldline-source_syntax_reference.adb', 'core/worldline-source_syntax_reference.ads', 'core/worldline-startup_admission.adb', 'core/worldline-startup_admission.ads', 'core/worldline-startup_admission_owned.adb', 'core/worldline-startup_admission_owned.ads', 'core/worldline-startup_installation.adb', 'core/worldline-startup_installation.ads', 'core/worldline-startup_issuer_source.adb', 'core/worldline-startup_issuer_source.ads', 'core/worldline-startup_source_custody.adb', 'core/worldline-startup_source_custody.ads', 'core/worldline-transaction_archive_json.adb', 'core/worldline-transaction_archive_json.ads', 'core/worldline-transaction_relations.adb', 'core/worldline-transaction_relations.ads'])

# Additional already-integrated core composition: explicit source and public
# obligations, not admission by filesystem discovery or inherited proof credit.
# Overloads share one required name; the complete detailed report must still
# prove and count every overload, body, private helper, caller and termination.
REQUIRED_PROVED += [
    'Attest.Custody_SHA256.Bit_Length',
    'Attest.Custody_SHA256.Absorbed',
    'Attest.Custody_SHA256.Initial',
    'Attest.Custody_SHA256.Update',
    'Attest.Custody_SHA256.Final',
    'Attest.Custody_SHA256.Hash',
    'Native_Diagnostic_Trace.Contents',
    'Native_Diagnostic_Trace.Pending_Contents',
    'Native_Diagnostic_Trace.Appended',
    'Native_Diagnostic_Trace.Empty',
    'Native_Diagnostic_Trace.Push',
    'Native_Diagnostic_Trace.Take_All',
    'Native_Diagnostic_Trace.Release',
    'Native_Diagnostic_Trace.Stack_Contents',
    'Native_Diagnostic_Trace.Split_Contents',
    'Worldline.Archive_Base64.Span_Valid',
    'Worldline.Archive_Base64.Is_Digit',
    'Worldline.Archive_Base64.Digit',
    'Worldline.Archive_Base64.Padding',
    'Worldline.Archive_Base64.Canonical',
    'Worldline.Archive_Base64.Decoded_Length',
    'Worldline.Archive_Base64.Decoded_Byte',
    'Worldline.Archive_Base64.Decode',
    'Worldline.Archive_Text.Span_Valid',
    'Worldline.Archive_Text.Continuation',
    'Worldline.Archive_Text.Unit_Width',
    'Worldline.Archive_Text.Text_Valid',
    'Worldline.Archive_Text.Value_At',
    'Worldline.Archive_Text.Read',
    'Worldline.Canonical_Exchange.Same_Packet_Binding',
    'Worldline.Canonical_Exchange.Raw_Matches',
    'Worldline.Canonical_Exchange.Original_Packet',
    'Worldline.Canonical_Exchange.Joins',
    'Worldline.Canonical_Exchange.Worker_Chains',
    'Worldline.Canonical_Exchange.Retained_Use',
    'Worldline.Canonical_Exchange.Reference',
    'Worldline.Canonical_Exchange.Decide',
    'Worldline.Canonical_Exchange_Wire.Well_Formed',
    'Worldline.Canonical_Exchange_Wire.Decode',
    'Worldline.Canonical_Operation.Digest_Matches',
    'Worldline.Canonical_Operation.Reference',
    'Worldline.Canonical_Operation.Decide',
    'Worldline.Canonical_Operation_Wire.Well_Formed',
    'Worldline.Canonical_Owner_Completion.Grant_Lineage',
    'Worldline.Canonical_Owner_Completion.History_Extends',
    'Worldline.Canonical_Owner_Completion.Reference',
    'Worldline.Canonical_Owner_Completion.Decide',
    'Worldline.Canonical_Owner_Completion_Wire.Well_Formed',
    'Worldline.Custody_Hmac.Normalize',
    'Worldline.Custody_Hmac.Mac',
    'Worldline.Custody_V2_Archive_Chain.Base_Matches',
    'Worldline.Custody_V2_Archive_Chain.Verify',
    'Worldline.Custody_V2_Archive_Projection.Borrow_Valid',
    'Worldline.Custody_V2_Archive_Projection.Byte_Length',
    'Worldline.Custody_V2_Archive_Projection.Byte_At',
    'Worldline.Custody_V2_Archive_Projection.Bytes_Equal',
    'Worldline.Custody_V2_Archive_Projection.Scoped_Archive_Operation_Matches',
    'Worldline.Custody_V2_Closed_State.Original_Equal',
    'Worldline.Custody_V2_Closed_State.Event_Record_Matches',
    'Worldline.Custody_V2_Closed_State.Matches',
    'Worldline.Custody_V2_Closed_V1.Matches',
    'Worldline.Custody_V2_Delta_Encoding.Delta_Length',
    'Worldline.Custody_V2_Delta_Encoding.Encode_Delta',
    'Worldline.Custody_V2_Delta_Encoding.Dictionary_Length',
    'Worldline.Custody_V2_Delta_Encoding.Encode_Dictionary',
    'Worldline.Custody_V2_Delta_Encoding.Base_Length',
    'Worldline.Custody_V2_Delta_Encoding.Encode_Base',
    'Worldline.Custody_V2_Delta_Encoding.Head_Length',
    'Worldline.Custody_V2_Delta_Encoding.Encode_Event_Head',
    'Worldline.Custody_V2_Delta_Encoding.Base_In_Prefix',
    'Worldline.Custody_V2_Delta_Encoding.Head_In_Prefix',
    'Worldline.Custody_V2_Delta_Encoding.Append_Base',
    'Worldline.Custody_V2_Delta_Encoding.Append_Event_Head',
    'Worldline.Custody_V2_Delta_Encoding.Event_Digests',
    'Worldline.Custody_V2_Delta_Grammar.Bound',
    'Worldline.Custody_V2_Domain_Hmac.Mac',
    'Worldline.Custody_V2_Empty_Seed.Hash',
    'Worldline.Custody_V2_Empty_Seed.Mac',
    'Worldline.Custody_V2_Empty_Seed.Archives_Match',
    'Worldline.Custody_V2_Empty_Seed.Origin_Matches',
    'Worldline.Custody_V2_Empty_Seed.Construct',
    'Worldline.Custody_V2_Event_Joins.Has_Alternative',
    'Worldline.Custody_V2_Event_Joins.Set_Of',
    'Worldline.Custody_V2_Event_Joins.Row_Joined',
    'Worldline.Custody_V2_Event_Joins.Same_Key',
    'Worldline.Custody_V2_Event_Joins.Alternatives_Exact',
    'Worldline.Custody_V2_Event_Joins.Alternative_Free',
    'Worldline.Custody_V2_Event_Joins.Reference_Matches',
    'Worldline.Custody_V2_Event_Joins.Prior_Reference',
    'Worldline.Custody_V2_Fold_Engine.Archive_Authenticated',
    'Worldline.Custody_V2_Fold_Engine.Rows_Match',
    'Worldline.Custody_V2_Fold_Engine.Root_Index',
    'Worldline.Custody_V2_Fold_Engine.Subject_Index',
    'Worldline.Custody_V2_Fold_Engine.Fold_Prefix',
    'Worldline.Custody_V2_Fold_Engine.Fold',
    'Worldline.Custody_V2_Fold_Engine.Legal',
    'Worldline.Custody_V2_Fold_Engine.Next',
    'Worldline.Custody_V2_Fold_Engine.Apply_Legal',
    'Worldline.Custody_V2_Fold_Engine.Load_Decide',
    'Worldline.Custody_V2_Fold_Rows.Root_Key_Same',
    'Worldline.Custody_V2_Fold_Rows.Subject_Key_Same',
    'Worldline.Custody_V2_Fold_Rows.Roots_Valid',
    'Worldline.Custody_V2_Fold_Rows.Subjects_Valid',
    'Worldline.Custody_V2_Fold_Rows.Root_Rows_Equal',
    'Worldline.Custody_V2_Fold_Rows.Subject_Rows_Equal',
    'Worldline.Custody_V2_Fold_Rows.Compare',
    'Worldline.Custody_V2_History.Row_Matches',
    'Worldline.Custody_V2_History.Materialize',
    'Worldline.Custody_V2_Load_Input.Counts',
    'Worldline.Custody_V2_Load_Input.Parsed_Spans_Valid',
    'Worldline.Custody_V2_Load_Input.Decode',
    'Worldline.Custody_V2_Load_Input.Decode_Grown',
    'Worldline.Custody_V2_Load_Input.SQL_Byte_Count',
    'Worldline.Custody_V2_Load_Input.Append_SQL_Cell',
    'Worldline.Custody_V2_Load_Input.Event_Extra_Byte_Count',
    'Worldline.Custody_V2_Load_Input.Append_Event_Extras',
    'Worldline.Custody_V2_Machine_Evidence.Joined',
    'Worldline.Custody_V2_Mutation_Decision.Status_Code',
    'Worldline.Custody_V2_Mutation_Decision.Successor_LE',
    'Worldline.Custody_V2_Mutation_Decision.Context_View',
    'Worldline.Custody_V2_Mutation_Decision.Cleanup_Status_Code',
    'Worldline.Custody_V2_Mutation_Decision.Cleanup_Decide',
    'Worldline.Custody_V2_Mutation_Decision.Attempt_Matches',
    'Worldline.Custody_V2_Mutation_Decision.Serving_Decide',
    'Worldline.Custody_V2_Mutation_Decision.Closed_Decide',
    'Worldline.Custody_V2_Mutation_Decision.Decide',
    'Worldline.Custody_V2_Mutation_Decision.Retry_Decide',
    'Worldline.Custody_V2_Mutation_Decision.Output_Next',
    'Worldline.Custody_V2_Mutation_Decision.Output_Replay',
    'Worldline.Custody_V2_Mutation_Decision.Output_Written',
    'Worldline.Custody_V2_Mutation_Decision.Output_Prefix',
    'Worldline.Custody_V2_Operation_Journal.Transition_Allowed',
    'Worldline.Custody_V2_Operation_Journal.Envelope_Authenticated',
    'Worldline.Custody_V2_Operation_Journal.Establish',
    'Worldline.Custody_V2_Operation_Journal.Established',
    'Worldline.Custody_V2_Operation_Journal.Startup_Decide',
    'Worldline.Custody_V2_Operation_Journal.Authenticated',
    'Worldline.Custody_V2_Operation_Journal.Current_Authenticated',
    'Worldline.Custody_V2_Operation_Journal.Head_Action',
    'Worldline.Custody_V2_Operation_Journal.Preparations_Complete',
    'Worldline.Custody_V2_Operation_Journal.Recovery_Decide',
    'Worldline.Custody_V2_Operation_Journal.Append_Allowed',
    'Worldline.Custody_V2_Operation_Journal.Bootstrap_Decide',
    'Worldline.Custody_V2_Owner_Correspondence.Current_Capture_Matches',
    'Worldline.Custody_V2_Owner_Correspondence.Owner_Rows_Correspond',
    'Worldline.Custody_V2_Owner_Correspondence.Owner_Corresponds',
    'Worldline.Custody_V2_Owner_Correspondence.Startup_Native',
    'Worldline.Custody_V2_Owner_Correspondence.Startup_Contains_Unknown',
    'Worldline.Custody_V2_Owner_Correspondence.Context_Decide',
    'Worldline.Custody_V2_Prepared.Workload',
    'Worldline.Custody_V2_Prepared.Operation_Heads_Reestablished',
    'Worldline.Custody_V2_Prepared.Root_Event_Join',
    'Worldline.Custody_V2_Prepared.Try_Next',
    'Worldline.Custody_V2_Prepared_Wire.Try_Next',
    'Worldline.Custody_V2_Provision.Selected_Matches',
    'Worldline.Custody_V2_Provision.Prior_Matches',
    'Worldline.Custody_V2_Provision.Decide',
    'Worldline.Custody_V2_Raw_Next.Valid',
    'Worldline.Custody_V2_Raw_Next.Root_Phase_Image',
    'Worldline.Custody_V2_Raw_Next.Root_Image',
    'Worldline.Custody_V2_Raw_Next.End_Image',
    'Worldline.Custody_V2_Raw_Next.New_Generation',
    'Worldline.Custody_V2_Raw_Next.New_Subject',
    'Worldline.Custody_V2_Raw_Next.Subject_Image',
    'Worldline.Custody_V2_Raw_Next.Carried_Image',
    'Worldline.Custody_V2_Request_Step.Apply',
    'Worldline.Custody_V2_Requester_Join.Integer_Is',
    'Worldline.Custody_V2_Requester_Join.Unsigned_Is',
    'Worldline.Custody_V2_Requester_Join.Same',
    'Worldline.Custody_V2_Requester_Join.Same_Bytes',
    'Worldline.Custody_V2_Requester_Join.Digest_Matches',
    'Worldline.Custody_V2_Requester_Join.Frame_Mac_Matches',
    'Worldline.Custody_V2_Requester_Join.Ucred_Matches',
    'Worldline.Custody_V2_Requester_Join.Request_Archive_Matches',
    'Worldline.Custody_V2_Requester_Join.Socket_Matches',
    'Worldline.Custody_V2_Requester_Join.Fresh_Matches',
    'Worldline.Custody_V2_Root_Evidence.Number',
    'Worldline.Custody_V2_Root_Evidence.Cause_Class_Of',
    'Worldline.Custody_V2_Root_Evidence.Pidfd_Pid',
    'Worldline.Custody_V2_Root_Evidence.Stat_Field',
    'Worldline.Custody_V2_Root_Evidence.Native_Capture_Joined',
    'Worldline.Custody_V2_Root_Evidence.Worker_Gone',
    'Worldline.Custody_V2_Root_Evidence.Worker_Liveness_Of',
    'Worldline.Custody_V2_Root_Evidence.Join',
    'Worldline.Custody_V2_Root_Evidence.Closed_Proof_Reference',
    'Worldline.Custody_V2_Root_Values.Valid',
    'Worldline.Custody_V2_Root_Values.Type_Is',
    'Worldline.Custody_V2_Root_Values.Record_Field',
    'Worldline.Custody_V2_Root_Values.Bytes_Key_Field',
    'Worldline.Custody_V2_Root_Values.Valid_Text',
    'Worldline.Custody_V2_Root_Values.Valid_Bytes',
    'Worldline.Custody_V2_Root_Values.Is_Integer',
    'Worldline.Custody_V2_Root_Values.Is_Null',
    'Worldline.Custody_V2_Root_Values.Is_Sequence',
    'Worldline.Custody_V2_Root_Values.Text_Value',
    'Worldline.Custody_V2_Root_Values.Bytes_Value',
    'Worldline.Custody_V2_Root_Values.Magnitude_Value',
    'Worldline.Custody_V2_Root_Values.Negative',
    'Worldline.Custody_V2_Root_Values.Text_Is',
    'Worldline.Custody_V2_Root_Values.Text_Matches',
    'Worldline.Custody_V2_Root_Values.Valid_Hex_Field',
    'Worldline.Custody_V2_Root_Values.Hex_Value',
    'Worldline.Custody_V2_Root_Values.Count',
    'Worldline.Custody_V2_Root_Values.Element',
    'Worldline.Custody_V2_Root_Values.Nonnegative_Count',
    'Worldline.Custody_V2_S0_Abandon.Materialize_S0',
    'Worldline.Custody_V2_S0_Abandon.Step_Abandon',
    'Worldline.Custody_V2_Schema_Correspondence.Name',
    'Worldline.Custody_V2_Schema_Correspondence.DDL',
    'Worldline.Custody_V2_Schema_Correspondence.Width',
    'Worldline.Custody_V2_Schema_Correspondence.Table_Matches',
    'Worldline.Custody_V2_Schema_Correspondence.Database_Matches',
    'Worldline.Custody_V2_Subject_Evidence.Roles_Joined',
    'Worldline.Custody_V2_Subject_Evidence.Cleanup_Kind_Of',
    'Worldline.Custody_V2_Subject_Evidence.Serving_Reference',
    'Worldline.Custody_V2_Subject_Evidence.Serving_Join',
    'Worldline.Custody_V2_Subject_Evidence.Output_Reference',
    'Worldline.Custody_V2_Subject_Evidence.Output_Context_Reference',
    'Worldline.Custody_V2_Subject_Evidence.Primitive_Reference',
    'Worldline.Custody_V2_Subject_Evidence.Join',
    'Worldline.Custody_V2_Typed_Step.Kind_Name',
    'Worldline.Custody_V2_Typed_Step.Decode',
    'Worldline.Custody_V2_Typed_Step.Apply_Abandon',
    'Worldline.Custody_V2_Typed_Step.Apply_Request_Abandon',
    'Worldline.Custody_V2_Typed_Step.Fold_From_S0',
    'Worldline.Custody_V2_Values.Type_Is',
    'Worldline.Custody_V2_Values.Valid_Text_Field',
    'Worldline.Custody_V2_Values.Hex_Text',
    'Worldline.Custody_V2_Values.Hex_Domain',
    'Worldline.Custody_V2_Values.Valid_Hex_Field',
    'Worldline.Custody_V2_Values.Valid_Text',
    'Worldline.Custody_V2_Values.Valid_Bytes',
    'Worldline.Custody_V2_Values.Is_Integer',
    'Worldline.Custody_V2_Values.Is_Null',
    'Worldline.Custody_V2_Values.Is_Sequence',
    'Worldline.Custody_V2_Values.Text_Value',
    'Worldline.Custody_V2_Values.Hex_Value',
    'Worldline.Custody_V2_Values.Bytes_Value',
    'Worldline.Custody_V2_Values.Magnitude_Value',
    'Worldline.Custody_V2_Values.Negative',
    'Worldline.Custody_V2_Values.Count',
    'Worldline.Custody_V2_Values.Element',
    'Worldline.Custody_V2_Values.Record_Field',
    'Worldline.Custody_V2_Values.Nonnegative_Count',
    'Worldline.Emitter_Allocation_Capture.Capture',
    'Worldline.Emitter_Allocation_Capture.Replay_Capture',
    'Worldline.Emitter_Allocation_Capture.Written_Capture',
    'Worldline.Emitter_Allocation_Capture.Prefix_Capture',
    'Worldline.Emitter_Channel_Evidence.Prefix_Reference',
    'Worldline.Emitter_Channel_Evidence.Frame_Reference',
    'Worldline.Emitter_Channel_Evidence.Acknowledgement_Reference',
    'Worldline.Emitter_Ordinal.Unsigned_Span',
    'Worldline.Emitter_Ordinal.Canonical_Text',
    'Worldline.Emitter_Ordinal.Decimal_Prefix',
    'Worldline.Emitter_Ordinal.Minimal_Length',
    'Worldline.Emitter_Ordinal.Same_Value',
    'Worldline.Emitter_Ordinal.Successor',
    'Worldline.Emitter_Ordinal.Canonical_Decimal_Matches',
    'Worldline.Retained_Custody_Chain.Verify',
    'Worldline.Retained_V1_Migration.Literal',
    'Worldline.Retained_V1_Migration.Same',
    'Worldline.Retained_V1_Migration.Terminal',
    'Worldline.Retained_V1_Migration.Last_For_Operation',
    'Worldline.Retained_V1_Migration.Closed_Operations',
    'Worldline.Retained_V1_Migration.Context_Matches',
    'Worldline.Retained_V1_Migration.Decide',
    'Worldline.Root_Custody_Abandon.Ack_Kind',
    'Worldline.Root_Custody_Abandon.Same_Alternative',
    'Worldline.Root_Custody_Abandon.Row_Joined',
    'Worldline.Root_Custody_Abandon.Ack_Table_Corresponds',
    'Worldline.Root_Custody_Abandon.Alternative_Allowed',
    'Worldline.Root_Custody_Abandon.Bound',
    'Worldline.Root_Custody_Abandon.CAS_Matches',
    'Worldline.Root_Custody_Abandon.Fresh_Inputs_Valid',
    'Worldline.Root_Custody_Abandon.Event_Bound',
    'Worldline.Root_Custody_Abandon.Rows_Valid',
    'Worldline.Root_Custody_Abandon.Legal_Abandon',
    'Worldline.Root_Custody_Abandon.Decide',
    'Worldline.Root_Custody_Abandon.Next_Abandon',
    'Worldline.Root_Custody_Archive_Join.V1_Base_Matches',
    'Worldline.Root_Custody_Context.Generation_Valid',
    'Worldline.Root_Custody_Context.Root_Roster_Consistent',
    'Worldline.Root_Custody_Context.Root_Joined',
    'Worldline.Root_Custody_Context.Original_Owner_Equation',
    'Worldline.Root_Custody_Context.Current_Store_Owner',
    'Worldline.Root_Custody_Context.Physical_Actor',
    'Worldline.Root_Custody_Descriptor.Subject_Key_Joined',
    'Worldline.Root_Custody_Descriptor.Subject_Joined',
    'Worldline.Root_Custody_Descriptor.Project_Descriptor',
    'Worldline.Root_Custody_Model.Actor_Owner',
    'Worldline.Root_Custody_Model.Is_Worker_Phase',
    'Worldline.Root_Custody_Model.Same_Present_Digest',
    'Worldline.Root_Custody_Model.Failed_Append',
    'Worldline.Root_Custody_Mutation_Roles.M3_Store_Role',
    'Worldline.Root_Custody_Mutation_Roles.M6_Descriptor_Role',
    'Worldline.Root_Custody_Mutation_Roles.M10_Reset_Role_And_Witness',
    'Worldline.Root_Custody_Mutation_Roles.M11_Escrow_Role_And_Phase',
    'Worldline.Root_Custody_Phase_Values.Family',
    'Worldline.Root_Custody_Phase_Values.Is_Physical',
    'Worldline.Root_Custody_Phase_Values.Subject_Barrier',
    'Worldline.Root_Custody_Phase_Values.Root_From_Clause',
    'Worldline.Root_Custody_Phase_Values.Fixed_Root_Actor_Clause',
    'Worldline.Root_Custody_Phase_Values.Unknown_Actor_Clause',
    'Worldline.Root_Custody_Phase_Values.Physical_Flag_Clause',
    'Worldline.Root_Custody_Phase_Values.Transfer_Root_Clause',
    'Worldline.Root_Custody_Phase_Values.Request_From_Clause',
    'Worldline.Root_Custody_Phase_Values.Descriptor_From_Clause',
    'Worldline.Root_Custody_Phase_Values.Request_Fixed_Actor_Clause',
    'Worldline.Root_Custody_Phase_Values.Descriptor_Fixed_Actor_Clause',
    'Worldline.Root_Custody_Phase_Values.Original_Request_Target_Equation',
    'Worldline.Root_Custody_Phase_Values.Request_Target',
    'Worldline.Root_Custody_Phase_Values.Original_Descriptor_Target_Equation',
    'Worldline.Root_Custody_Phase_Values.Descriptor_Target',
    'Worldline.Root_Custody_Phase_Values.Original_Progress_Receiving_Window',
    'Worldline.Root_Custody_Phase_Values.Single_Root_Image_Event',
    'Worldline.Root_Custody_Phase_Values.Root_Target',
    'Worldline.Root_Custody_Phase_Values.Single_Root_Image',
    'Worldline.Root_Custody_Phase_Values.Unknown_Image',
    'Worldline.Root_Custody_Phase_Values.Reattached_Image',
    'Worldline.Root_Custody_Phase_Values.Reattach_Successor_Clause',
    'Worldline.Root_Custody_Phase_Values.Reconciled_Image',
    'Worldline.Root_Custody_Phase_Values.Abort_Phase_Image',
    'Worldline.Root_Custody_Phase_Values.Root_End_Image',
    'Worldline.Root_Custody_Phase_Values.Request_Phase_Image',
    'Worldline.Root_Custody_Phase_Values.Descriptor_Phase_Image',
    'Worldline.Root_Custody_Phase_Values.Replay_Matches',
    'Worldline.Root_Custody_Phase_Values.Request_Subgeneration_Clause',
    'Worldline.Root_Custody_Phase_Values.Request_Transfer_Image',
    'Worldline.Root_Custody_Phase_Values.Descriptor_Abandon_Image',
    'Worldline.Root_Custody_Phase_Values.Descriptor_Abandon_Successor_Clause',
    'Worldline.Root_Custody_Phase_Values.Descriptor_Freeze_Image',
    'Worldline.Root_Custody_Phase_Values.New_Generation_Successor_Clause',
    'Worldline.Root_Custody_Phase_Values.Carried_Request_Fields_Image',
    'Worldline.Root_Custody_Replay.Key',
    'Worldline.Root_Custody_Replay.Key_Valid',
    'Worldline.Root_Custody_Replay.Inputs_Valid',
    'Worldline.Root_Custody_Replay.Matches',
    'Worldline.Root_Custody_Replay.Any_Match',
    'Worldline.Root_Custody_Replay.Multiple_Matches',
    'Worldline.Root_Custody_Replay.Resolve',
    'Worldline.Root_Custody_Request_Abandon.Subject_Bound',
    'Worldline.Root_Custody_Request_Abandon.Subject_CAS',
    'Worldline.Root_Custody_Request_Abandon.Request_Kind',
    'Worldline.Root_Custody_Request_Abandon.Alternative_Joined',
    'Worldline.Root_Custody_Request_Abandon.Table_Corresponds',
    'Worldline.Root_Custody_Request_Abandon.Alternative_Allowed',
    'Worldline.Root_Custody_Request_Abandon.Subjects_Valid',
    'Worldline.Root_Custody_Request_Abandon.Event_Bound',
    'Worldline.Root_Custody_Request_Abandon.Transfer_Head_Joined',
    'Worldline.Root_Custody_Request_Abandon.Generation_Allowed',
    'Worldline.Root_Custody_Request_Abandon.Legal',
    'Worldline.Root_Custody_Request_Abandon.Decide',
    'Worldline.Root_Custody_Request_Abandon.Apply_Next',
    'Worldline.Root_Custody_Row_Schema.Span_Valid',
    'Worldline.Root_Custody_Row_Schema.Text_Is',
    'Worldline.Root_Custody_Row_Schema.Same_Span',
    'Worldline.Root_Custody_Row_Schema.Same_Cell',
    'Worldline.Root_Custody_Row_Schema.Magnitude_Blob',
    'Worldline.Root_Custody_Row_Schema.Nullable_Magnitude_Blob',
    'Worldline.Root_Custody_Row_Schema.Blob_Quantity',
    'Worldline.Root_Custody_Row_Schema.Bit_Cell',
    'Worldline.Root_Custody_Row_Schema.Bit_Value',
    'Worldline.Root_Custody_Row_Schema.Matches_Root_Phase',
    'Worldline.Root_Custody_Row_Schema.Read_Root_Phase_Name',
    'Worldline.Root_Custody_Row_Schema.Matches_Abort_Class',
    'Worldline.Root_Custody_Row_Schema.Read_Abort_Class_Name',
    'Worldline.Root_Custody_Row_Schema.Matches_Request_Phase',
    'Worldline.Root_Custody_Row_Schema.Read_Request_Phase_Name',
    'Worldline.Root_Custody_Row_Schema.Matches_Descriptor_Phase',
    'Worldline.Root_Custody_Row_Schema.Read_Descriptor_Phase_Name',
    'Worldline.Root_Custody_Row_Schema.Matches_Transfer_Mode',
    'Worldline.Root_Custody_Row_Schema.Read_Transfer_Mode_Name',
    'Worldline.Root_Custody_Row_Schema.Same_Root_Columns',
    'Worldline.Root_Custody_Row_Schema.Same_Subject_Columns',
    'Worldline.Root_Custody_Row_Schema.Read_Nullable_Root_Phase',
    'Worldline.Root_Custody_Row_Schema.Read_Nullable_Abort_Class',
    'Worldline.Root_Custody_Row_Schema.Text_Cell',
    'Worldline.Root_Custody_Row_Schema.Is_Hex_Character',
    'Worldline.Root_Custody_Row_Schema.Digest_Text',
    'Worldline.Root_Custody_Row_Schema.Before_Unknown_Columns',
    'Worldline.Root_Custody_Row_Schema.Root_Column_Shapes',
    'Worldline.Root_Custody_Row_Schema.Subject_Phase_Columns',
    'Worldline.Root_Custody_Row_Schema.Subject_Column_Shapes',
    'Worldline.Root_Custody_Row_Schema.Same_Optional_Root_Row',
    'Worldline.Root_Custody_Row_Schema.Same_Optional_Subject_Row',
    'Worldline.Root_Custody_Row_Schema.Read_Nullable_Quantity',
    'Worldline.Root_Custody_Row_Schema.Read_Subject_Phase',
    'Worldline.Root_Custody_Row_Views.Hex_Nibble',
    'Worldline.Root_Custody_Row_Views.Decode_Digest',
    'Worldline.Root_Custody_Row_Views.Optional_Digest',
    'Worldline.Root_Custody_Row_Views.Optional_Phase',
    'Worldline.Root_Custody_Row_Views.Optional_Abort',
    'Worldline.Root_Custody_Row_Views.Optional_Quantity',
    'Worldline.Root_Custody_Row_Views.Root_Corresponds',
    'Worldline.Root_Custody_Row_Views.Make_Root',
    'Worldline.Root_Custody_Row_Views.Make_Optional_Root',
    'Worldline.Root_Custody_Row_Views.Subject_Corresponds',
    'Worldline.Root_Custody_Row_Views.Make_Subject',
    'Worldline.Root_Custody_Row_Views.Make_Optional_Subject',
    'Worldline.Root_Output_Sequence.Evaluate',
    'Worldline.Root_Output_Sequence.Next_Output',
    'Worldline.Root_Output_Sequence.Replay_Output',
    'Worldline.Root_Output_Sequence.Written_Output',
    'Worldline.Root_Output_Sequence.Prefix_Output',
    'Worldline.Scoped_Archive.Valid',
    'Worldline.Scoped_Archive.Field',
    'Worldline.Scoped_Archive.Text_Is',
    'Worldline.Scoped_Archive.Text_Matches',
    'Worldline.Scoped_Archive.Member_Count',
    'Worldline.Scoped_Archive.Member_Name_Is',
    'Worldline.Scoped_Capture_Evolution_Projection.Closed_Roles_Match',
    'Worldline.Scoped_Capture_Evolution_Projection.Subject_Transport_Matches',
    'Worldline.Scoped_Capture_Evolution_Projection.Initial_Root_Transport_Matches',
    'Worldline.Scoped_Capture_Evolution_Projection.Subject_Roles_Match',
    'Worldline.Scoped_Capture_Evolution_Projection.Evolution_Matches',
    'Worldline.Scoped_Capture_History_Projection.Historical_Source_Matches',
    'Worldline.Scoped_Capture_History_Projection.Unavailable_Source_Matches',
    'Worldline.Scoped_Capture_History_Projection.Owned_Protocol_Matches',
    'Worldline.Scoped_Capture_Namespace_Projection.FD_Receipt_Matches',
    'Worldline.Scoped_Capture_Namespace_Projection.SCM_Credentials_Match',
    'Worldline.Scoped_Capture_Namespace_Projection.Reverse_Host_Matches',
    'Worldline.Scoped_Capture_Owner_Projection.Owner_Source_Matches',
    'Worldline.Scoped_Capture_Projection.Scoped_Capture_Matches',
    'Worldline.Scoped_Capture_Projection.Subject_Capture_Matches',
    'Worldline.Scoped_Capture_Projection.Value_Matches',
    'Worldline.Scoped_Capture_Projection.JSON_Value_Matches',
    'Worldline.Scoped_Capture_Projection.Current_Source_Matches',
    'Worldline.Scoped_Capture_Projection.Hash_Field',
    'Worldline.Scoped_Capture_Projection.Property',
    'Worldline.Scoped_Capture_Projection.Number',
    'Worldline.Scoped_Capture_Projection.Id_Hex',
    'Worldline.Scoped_Capture_Projection.Namespace_Matches',
    'Worldline.Scoped_Capture_Projection.Head_Source_Matches',
    'Worldline.Scoped_Capture_Projection.Role_Roster_Matches',
    'Worldline.Scoped_Capture_Projection.Member_Value',
    'Worldline.Scoped_Capture_Projection.Raw_Source_Field',
    'Worldline.Scoped_Capture_Projection.Process_Source_Matches',
    'Worldline.Scoped_Capture_Projection.Scoped_Descriptor_Alias_Matches',
    'Worldline.Scoped_Capture_Projection.JSON_Source_Value_Matches',
    'Worldline.Scoped_Capture_Projection.Scoped_Record_Matches',
    'Worldline.Scoped_Capture_Projection.Source_Record_Matches',
    'Worldline.Scoped_Capture_Projection.Line',
    'Worldline.Scoped_Capture_Projection.Word',
    'Worldline.Scoped_Capture_Projection.Decimal',
    'Worldline.Scoped_Capture_Projection.Stat_Number',
    'Worldline.Scoped_Capture_Projection.Process_Cgroup_Matches',
    'Worldline.Scoped_Capture_Projection.Maps_Match',
    'Worldline.Scoped_Capture_Projection.Archive_Image_Matches',
    'Worldline.Scoped_Record_Source.Scoped_Record_Value_Matches',
    'Worldline.Scoped_Record_Source.Source_Record_Value_Matches',
    'Worldline.SQLite_Parameter_Source.Truthy',
    'Worldline.SQLite_Parameter_Source.Text_Affinity_Matches',
    'Worldline.SQLite_Parameter_Source.Parameter_Equals_Text',
    'Canonical_Artifacts.JSON_Prefix',
    'Canonical_Artifacts.Canonical_JSON_Valid',
    'Canonical_Artifacts.Operation_Archive_JSON_Matches',
    'Canonical_Artifacts.Genesis_Archive_Matches',
    'Canonical_Artifacts.Scoped_Archive_JSON_Matches',
    'Canonical_Artifacts.Canonical_JSON_Field',
    'Resource_Ledger.Total_Model',
    'Resource_Ledger.Prefix_Total_Checked',
    'Resource_Reservation_Transition.Original_Final_Equation',
    'Resource_Run_Ledger.Original_Run_State_Equation',
    'Worldline.Recovery_Archive.Ordered_Source_Value_Matches',
    'Worldline.Recovery_Archive.Restored_Source_Value_Matches',
]
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset({
    'core/attest/attest-custody_sha256.adb',
    'core/attest/attest-custody_sha256.ads',
    'core/native_diagnostic_trace.adb',
    'core/native_diagnostic_trace.ads',
    'core/worldline-archive_base64.adb',
    'core/worldline-archive_base64.ads',
    'core/worldline-archive_text.adb',
    'core/worldline-archive_text.ads',
    'core/worldline-canonical_exchange.adb',
    'core/worldline-canonical_exchange.ads',
    'core/worldline-canonical_exchange_wire.ads',
    'core/worldline-canonical_operation.adb',
    'core/worldline-canonical_operation.ads',
    'core/worldline-canonical_operation_wire.ads',
    'core/worldline-canonical_owner_completion.adb',
    'core/worldline-canonical_owner_completion.ads',
    'core/worldline-canonical_owner_completion_wire.ads',
    'core/worldline-custody_hmac.adb',
    'core/worldline-custody_hmac.ads',
    'core/worldline-custody_v2_archive_chain.adb',
    'core/worldline-custody_v2_archive_chain.ads',
    'core/worldline-custody_v2_archive_projection.adb',
    'core/worldline-custody_v2_archive_projection.ads',
    'core/worldline-custody_v2_closed_state.adb',
    'core/worldline-custody_v2_closed_state.ads',
    'core/worldline-custody_v2_closed_v1.adb',
    'core/worldline-custody_v2_closed_v1.ads',
    'core/worldline-custody_v2_delta_encoding.adb',
    'core/worldline-custody_v2_delta_encoding.ads',
    'core/worldline-custody_v2_delta_grammar.adb',
    'core/worldline-custody_v2_delta_grammar.ads',
    'core/worldline-custody_v2_domain_hmac.adb',
    'core/worldline-custody_v2_domain_hmac.ads',
    'core/worldline-custody_v2_empty_seed.adb',
    'core/worldline-custody_v2_empty_seed.ads',
    'core/worldline-custody_v2_event_joins.adb',
    'core/worldline-custody_v2_event_joins.ads',
    'core/worldline-custody_v2_fold_engine.adb',
    'core/worldline-custody_v2_fold_engine.ads',
    'core/worldline-custody_v2_fold_rows.adb',
    'core/worldline-custody_v2_fold_rows.ads',
    'core/worldline-custody_v2_history.adb',
    'core/worldline-custody_v2_history.ads',
    'core/worldline-custody_v2_load_input.adb',
    'core/worldline-custody_v2_load_input.ads',
    'core/worldline-custody_v2_machine_evidence.adb',
    'core/worldline-custody_v2_machine_evidence.ads',
    'core/worldline-custody_v2_mutation_decision.adb',
    'core/worldline-custody_v2_mutation_decision.ads',
    'core/worldline-custody_v2_operation_journal.adb',
    'core/worldline-custody_v2_operation_journal.ads',
    'core/worldline-custody_v2_owner_correspondence.adb',
    'core/worldline-custody_v2_owner_correspondence.ads',
    'core/worldline-custody_v2_prepared.adb',
    'core/worldline-custody_v2_prepared.ads',
    'core/worldline-custody_v2_prepared_wire.adb',
    'core/worldline-custody_v2_prepared_wire.ads',
    'core/worldline-custody_v2_provision.adb',
    'core/worldline-custody_v2_provision.ads',
    'core/worldline-custody_v2_raw_next.adb',
    'core/worldline-custody_v2_raw_next.ads',
    'core/worldline-custody_v2_request_step.adb',
    'core/worldline-custody_v2_request_step.ads',
    'core/worldline-custody_v2_requester_join.adb',
    'core/worldline-custody_v2_requester_join.ads',
    'core/worldline-custody_v2_root_evidence.adb',
    'core/worldline-custody_v2_root_evidence.ads',
    'core/worldline-custody_v2_root_values.adb',
    'core/worldline-custody_v2_root_values.ads',
    'core/worldline-custody_v2_s0_abandon.adb',
    'core/worldline-custody_v2_s0_abandon.ads',
    'core/worldline-custody_v2_schema_correspondence.adb',
    'core/worldline-custody_v2_schema_correspondence.ads',
    'core/worldline-custody_v2_subject_evidence.adb',
    'core/worldline-custody_v2_subject_evidence.ads',
    'core/worldline-custody_v2_typed_step.adb',
    'core/worldline-custody_v2_typed_step.ads',
    'core/worldline-custody_v2_values.adb',
    'core/worldline-custody_v2_values.ads',
    'core/worldline-emitter_allocation_capture.adb',
    'core/worldline-emitter_allocation_capture.ads',
    'core/worldline-emitter_channel_evidence.adb',
    'core/worldline-emitter_channel_evidence.ads',
    'core/worldline-emitter_ordinal.adb',
    'core/worldline-emitter_ordinal.ads',
    'core/worldline-retained_custody_chain.adb',
    'core/worldline-retained_custody_chain.ads',
    'core/worldline-retained_v1_migration.adb',
    'core/worldline-retained_v1_migration.ads',
    'core/worldline-root_custody_abandon.adb',
    'core/worldline-root_custody_abandon.ads',
    'core/worldline-root_custody_archive_join.ads',
    'core/worldline-root_custody_context.adb',
    'core/worldline-root_custody_context.ads',
    'core/worldline-root_custody_descriptor.adb',
    'core/worldline-root_custody_descriptor.ads',
    'core/worldline-root_custody_model.adb',
    'core/worldline-root_custody_model.ads',
    'core/worldline-root_custody_mutation_roles.adb',
    'core/worldline-root_custody_mutation_roles.ads',
    'core/worldline-root_custody_phase_values.adb',
    'core/worldline-root_custody_phase_values.ads',
    'core/worldline-root_custody_raw_operands.ads',
    'core/worldline-root_custody_replay.adb',
    'core/worldline-root_custody_replay.ads',
    'core/worldline-root_custody_request_abandon.adb',
    'core/worldline-root_custody_request_abandon.ads',
    'core/worldline-root_custody_row_schema.adb',
    'core/worldline-root_custody_row_schema.ads',
    'core/worldline-root_custody_row_views.adb',
    'core/worldline-root_custody_row_views.ads',
    'core/worldline-root_output_sequence.adb',
    'core/worldline-root_output_sequence.ads',
    'core/worldline-scoped_archive.adb',
    'core/worldline-scoped_archive.ads',
    'core/worldline-scoped_capture_evolution_projection.adb',
    'core/worldline-scoped_capture_evolution_projection.ads',
    'core/worldline-scoped_capture_history_projection.adb',
    'core/worldline-scoped_capture_history_projection.ads',
    'core/worldline-scoped_capture_namespace_projection.adb',
    'core/worldline-scoped_capture_namespace_projection.ads',
    'core/worldline-scoped_capture_owner_projection.adb',
    'core/worldline-scoped_capture_owner_projection.ads',
    'core/worldline-scoped_capture_projection.adb',
    'core/worldline-scoped_capture_projection.ads',
    'core/worldline-scoped_record_source.adb',
    'core/worldline-scoped_record_source.ads',
    'core/worldline-sqlite_parameter_source.adb',
    'core/worldline-sqlite_parameter_source.ads',
})
CONTRACT_PINS.update({
    'core/attest/attest-custody_sha256.adb': '517483877673a14c64dbef546dba0c4de1f644b67fececeb404e5d0c0cd67636',
    'core/attest/attest-custody_sha256.ads': 'e8813485ce7f82ae71e219863a9aabd72f87f490b5af5ff7097460322b70a669',
    'core/native_diagnostic_trace.adb': 'c05e3e66db701d1228910da4d76f0678ecd1905b25d6a199f1bf52a607e39bc9',
    'core/native_diagnostic_trace.ads': '97e8ae16e92f5d2ef84949dca19051a6d7299ed72d9d227e1fe758d57b077946',
    'core/worldline-archive_base64.adb': '2eba767581bbbbc63b3f34a4084aa913a158c01818ae1bb29370f03a60cf7dc8',
    'core/worldline-archive_base64.ads': '50af2a70a5622c632f3b3408cee3e7f94edda8ca925aad5d2e853acc76488dde',
    'core/worldline-archive_text.adb': '7504da5ee5f87acf931b930e8551106c7f83425048d22c086f6d6fa1edf17753',
    'core/worldline-archive_text.ads': 'a8ff1343976637442f26056e64d92d17803452f91d5b4faca790f61c0223e008',
    'core/worldline-canonical_exchange.adb': 'abf9eae5025cdb4fb5c658bc9a34d8e38bfb25d9dc762ca50a92434d9bc65f21',
    'core/worldline-canonical_exchange.ads': 'dd06fede4281cf82ec86ede13fb986e7c4b777ecb786d417a06364a8c055fa84',
    'core/worldline-canonical_exchange_wire.ads': 'ca714e8950100dd375dbd3a1cdb57b34392b2bf12bb10e4562a076f566de2f46',
    'core/worldline-canonical_operation.adb': '46e68b00af2f0b1c4af8ece2cfa27cd750ed4493423fa368faf1cb239c40f244',
    'core/worldline-canonical_operation.ads': '77bc5760357cc2524b41897725bf9faeac33c4e32fba47a0cbe9a8d11bc81493',
    'core/worldline-canonical_operation_wire.ads': '7f7e75eed9a6264cf53f22b7ec3c9106ac3af59926bc2d72e83d9a2e670dd9df',
    'core/worldline-canonical_owner_completion.adb': '3abb4da29b08d9046e6bdd882991000eeb11166baba74d22bb830ae7e15d9062',
    'core/worldline-canonical_owner_completion.ads': '2bed90b3fe7db270940fec56025ceef0138b81fa2bc47ce7e426c08f56320e35',
    'core/worldline-canonical_owner_completion_wire.ads': '1775d328c16d359d49f254cc7bcdd8f5fdedaf972738784060ff7366a8c433f3',
    'core/worldline-custody_hmac.adb': 'b41cf2de9124af924541b03a567fc4e1cbca9df4dbf932f9f8647832b5086f11',
    'core/worldline-custody_hmac.ads': 'bc5d98e22855d017ab4858a822e2feb4fd01b6b883167d1d0bd486211c88f1c9',
    'core/worldline-custody_v2_archive_chain.adb': '336c2618913b802f5ffd8e74dc31e56cc663ac0ec80f62716fbacd19ab4b7cfc',
    'core/worldline-custody_v2_archive_chain.ads': '3c5d737184f0b50a4314c464a6a87567fb1636d8080c0c71a7a971b40bee5b57',
    'core/worldline-custody_v2_archive_projection.adb': '856b44e3b049c21b5f178f5b4ba85bb77498954b216aa58242e8719ba27b9768',
    'core/worldline-custody_v2_archive_projection.ads': 'ca6ebdf0628e502fd4078d9c968e35ddb640d6414d12026327a1ecfc500a856d',
    'core/worldline-custody_v2_closed_state.adb': 'cc105be47cc8cad052618d421ae2bd3fd8a780bfd64c6091fcf67f9f6b923a07',
    'core/worldline-custody_v2_closed_state.ads': '2f8f8ac54aff91083d0054718ed83d7df8aa97ab485b2b864339684f80a29cfc',
    'core/worldline-custody_v2_closed_v1.adb': 'b7462b00cf6181b614c96610a32e7cd682baa00a95556ffef1e274b125962793',
    'core/worldline-custody_v2_closed_v1.ads': '58ca2d0bf182da833fac25bbbe91d4c9d0b5d0a1a334a4c05ea63e9f17476157',
    'core/worldline-custody_v2_delta_encoding.adb': '553f57b8ae8ae9916d3ef38c710d79c28d960e8d52e96962c2446f22fd85f23e',
    'core/worldline-custody_v2_delta_encoding.ads': 'dbe5fd8b7a37ffecc128e35f30a8596422531ab05d683bf676837f636ab6d4ae',
    'core/worldline-custody_v2_delta_grammar.adb': '48b184ef302a54beac016b5f6563a18db7e6e30113cee7489a49c1bab6ec5995',
    'core/worldline-custody_v2_delta_grammar.ads': '3a0e65e25250615cd2711e0701cad851bbd546bfefb76f608cbc2d3653c112ef',
    'core/worldline-custody_v2_domain_hmac.adb': '129b11e3ee513d905bca721d6d903d3c9d4288786d41329b69deadb14b3593f8',
    'core/worldline-custody_v2_domain_hmac.ads': '8c0b42ef608bae567da4f1afcccd8dfc2e9a91a043bf431c90e92703c1eafd89',
    'core/worldline-custody_v2_empty_seed.adb': 'bb17d61bd944f62471354bfe904f11e6c2edecb3d5337c2dfcb381c6ba759436',
    'core/worldline-custody_v2_empty_seed.ads': 'd6f4ca39db85bd2dfeb29ae77c0bb30b806ca5022737eb3e4a8cc00086aa59d0',
    'core/worldline-custody_v2_event_joins.adb': '98533c6482b10d5a9024489340ba906d440ddcb30e7e2f1a92a4fa3fa979d511',
    'core/worldline-custody_v2_event_joins.ads': '825f8d3386c8e7c296fc6cf7e4d53572e48624da62d73e48203a70f43ffb1228',
    'core/worldline-custody_v2_fold_engine.adb': 'a47529d0cbf63936bd37f97907f25b888fdafe98098acb8fb7c67428932dfecf',
    'core/worldline-custody_v2_fold_engine.ads': 'cd9163a21912c30070a2d6d78e11dc2a7e9002f4b767d3b7aa2071133a874897',
    'core/worldline-custody_v2_fold_rows.adb': '66acc226ff8ccd798b3f1835d4c7a5ddc53c5cdfc3db4e88c99ad338383919c2',
    'core/worldline-custody_v2_fold_rows.ads': 'b32cd545940de4ec2ac53233ae3bc90b2dd57e1c2be38abf02a29cc442a55a74',
    'core/worldline-custody_v2_history.adb': '48fa3ac19e1dbf354eaa7fbe1a69f44d62c59a5dd1a454844c82b702ef37fa74',
    'core/worldline-custody_v2_history.ads': '24ef465b367b8a0ffd1d2c61b9e3838a096f0bea3056134dd93f440c9709ecac',
    'core/worldline-custody_v2_load_input.adb': '8f89472822bfe0ac18cf6d99a8959a219315c672b7bc46e4ee00680aba12bece',
    'core/worldline-custody_v2_load_input.ads': 'fda37eb7c3624c49b6689bd23ed236f7294c929d22f54d0cfcc587033c0d4915',
    'core/worldline-custody_v2_machine_evidence.adb': 'cdfcba9aee825bb6299ad2973dbb827ac50c4107f6317b4c2f78b624692ca773',
    'core/worldline-custody_v2_machine_evidence.ads': '4e9b0da0ee9c88cc89a2377dfba5e8a4b642f5cb29abd85596f5f6985c730ed0',
    'core/worldline-custody_v2_mutation_decision.adb': '9292a31a8bff797d9a071ff8eaa30eed4225cddb19628dbde6b389002417ecf0',
    'core/worldline-custody_v2_mutation_decision.ads': 'f8b79c2d9034e4b831b1b9fc4d9834a9568e5054333b0a3cc91a6f380c60eeb4',
    'core/worldline-custody_v2_operation_journal.adb': 'd109e4eb82e1819b9e25dc7c4bb0e451ce627daa072d0999b27d4002211a1f52',
    'core/worldline-custody_v2_operation_journal.ads': '3b442b54270c1b3de5e5addf30d8695a0d57d3634f339b10b4c1e344e1ad9043',
    'core/worldline-custody_v2_owner_correspondence.adb': '18d3e7ea6640650beed82e4def121b736fac86597f2518b1927f7c4a4d60f869',
    'core/worldline-custody_v2_owner_correspondence.ads': 'f96fc83d78e8293b99ff84e693bd80a3a72b20849a78de11b356bc70f1da82fa',
    'core/worldline-custody_v2_prepared.adb': '6003fb569f4a6bf19704a5036dc55074e2f9a36d67666c74efc302bfa9568a62',
    'core/worldline-custody_v2_prepared.ads': '9fd612c0ff0ecb1a93110ccceeb182a7227db8316294feeeb3b7857e0723c8b4',
    'core/worldline-custody_v2_prepared_wire.adb': '67b4b612451d51060e9364c0cef90f17e0f25897569b2a8607c1edd759f29752',
    'core/worldline-custody_v2_prepared_wire.ads': 'b58682076e7793592b60b0f4b1ecd4ee8c00741c515603b71491350e1ff260b0',
    'core/worldline-custody_v2_provision.adb': '8f5ee1beb9f517a3567cd51e44166ac21f6e175fc03b91e3f35fa8f1394f58d0',
    'core/worldline-custody_v2_provision.ads': 'b9f36c4be84c2dabf08824dc441123f55ea25d865238c5f673840aea3e8e97bf',
    'core/worldline-custody_v2_raw_next.adb': '10a86d422f1414f1d961b48c13e31ec1ecf43acd6d700bac765c4e2bc5584b21',
    'core/worldline-custody_v2_raw_next.ads': '7ac88aa21907fb8d9e4c23437d8c280efef31a593e3c0cbb245f4e3d421952b4',
    'core/worldline-custody_v2_request_step.adb': '8e8f983544936df6e36f859485f7fb20ba32f58e20025bc6d7b3d0e620dd7681',
    'core/worldline-custody_v2_request_step.ads': '5c4cf73874a4ef2f610d5e13f9f6fa0431ac485ff3dd7c84922def57d5b75a37',
    'core/worldline-custody_v2_requester_join.adb': 'c04cc5de8c3a81b3e59b8b825fa4a8beace7ad6c35217591cb0b3982516cd7eb',
    'core/worldline-custody_v2_requester_join.ads': 'f287886125cb12a0488466decbfcae8379462b1ebac7ef595c04e0c50a441c5f',
    'core/worldline-custody_v2_root_evidence.adb': '1c141dbf5648111fb2113f229a017a93628545d3328a518dd03f03bfed8cddc4',
    'core/worldline-custody_v2_root_evidence.ads': '3e0bcdc34c03060720d31c49f56982a93c0c1aeaf7f80f3ecf24637618138872',
    'core/worldline-custody_v2_root_values.adb': '3191d762940a96bf65586e4bc0e79a79ddc1af8ab629c7cca734149d2b536ddb',
    'core/worldline-custody_v2_root_values.ads': 'd9862eecb688cc7ccbb6cd705f395d4ce82e7768769ba0426d348a81f4b780ef',
    'core/worldline-custody_v2_s0_abandon.adb': '4ad477b5ceb0c19ec42ab09e39003cf66c18bc0e12d7ca52da3287f393caf325',
    'core/worldline-custody_v2_s0_abandon.ads': '976ac16c14d20eb4cfe59a5e02725f551252e39a6425d786c05227e3027a0d0e',
    'core/worldline-custody_v2_schema_correspondence.adb': '39d1cb445778a77b531d653cba79448587ba876b6dcf8c228bbe0067ac85b00f',
    'core/worldline-custody_v2_schema_correspondence.ads': 'ecae6be99b60057c6ddf5225852bf9308a9ccd17f9c940a8dac6d60b860002ed',
    'core/worldline-custody_v2_subject_evidence.adb': 'e6997467799645073efc6cd1e2c8e303af4cbf91ee5f4e8baec563c45b1ac25e',
    'core/worldline-custody_v2_subject_evidence.ads': 'dd4131b9c902f6f65d23336c691ca6417228ce7d903e3e86739996e526f1ae3b',
    'core/worldline-custody_v2_typed_step.adb': '28156aeebbd001b35703c288544d30131eaba0100f3eefddabf01920ed09d143',
    'core/worldline-custody_v2_typed_step.ads': '12a09d6d872ba07c219003b7effea05c0df6eeb4bf869e08a8d2d75e053bbfe5',
    'core/worldline-custody_v2_values.adb': 'df99d4075d1931c521da3e9d1ef1a9b7e80c9eb2f2481eb80bd3185e2bd42639',
    'core/worldline-custody_v2_values.ads': 'f09a4c9fd685f213899940863187424b25b2e8058fa0d1c9a0298175772fde4e',
    'core/worldline-emitter_allocation_capture.adb': '9c3ed60c60c30385b74e8c22c7544609aa1749977f7fa4dd6bad65566a7c860a',
    'core/worldline-emitter_allocation_capture.ads': '9e52ebd98354b2e931da12eed8db3d13c4047ab4008a38126ed5500698f1b096',
    'core/worldline-emitter_channel_evidence.adb': 'afb66e0f065091a22d32a7941fb722e7cf7925c1cf44ba271ce842601aead54f',
    'core/worldline-emitter_channel_evidence.ads': 'bb7dc00355b46bfa042571800cad04c3e6dde53fb764ff3fd88636a08d93d9e4',
    'core/worldline-emitter_ordinal.adb': '80fd43a1082ebd5da02e4d44ec9d2fb730dc67d3ae0b97b9aff49bd4f28ec097',
    'core/worldline-emitter_ordinal.ads': '783e6615582024a922da0e1a63463393223a31d8d674f10b20ffb9e92f1cdd0c',
    'core/worldline-retained_custody_chain.adb': 'ee0351ecec751433018f50a4617c0bf0add02c39951ca4e76672bac094d1677a',
    'core/worldline-retained_custody_chain.ads': '84bd9b932d81d5933d3b496a84e63353e151e86bbbff9750843131cc9420ba40',
    'core/worldline-retained_v1_migration.adb': 'f1dba236113a339ffc5c5e19e197a2c9c5e3f8e29b416fdb8e7f5328203610d3',
    'core/worldline-retained_v1_migration.ads': '1f89e4662347b4096e8ad67e21b51c3a9a8055f00f546bfe7459661a74222248',
    'core/worldline-root_custody_abandon.adb': '3cced12d5af1f65fd2310f67c88afc264e80f72e449e7bb2a511cd131668d0ba',
    'core/worldline-root_custody_abandon.ads': '7aff74a2e0d8915c1b6498135f851bd31d118666c3285aefba7c28917a21065f',
    'core/worldline-root_custody_archive_join.ads': 'a1bc9ec39dfc817677febba41a436b29103ccb7077ed0879382cd87fcbbe6b7c',
    'core/worldline-root_custody_context.adb': 'aedcbce8d6818aa9e95bdffde8ccbd35b866dc4a752c97c8e1dd16acf44f13dd',
    'core/worldline-root_custody_context.ads': '95b2b96d077ae7a692be58cd6a247cd1ff9029ca7954826cb60a7d40e7b61c6e',
    'core/worldline-root_custody_descriptor.adb': '9d2738df0cc85c83f2089fee740831838cfab8ee33ec6968d5d9660fb739fc32',
    'core/worldline-root_custody_descriptor.ads': '28a6700ae42d82c6e9f294ff54ba6b20bf328160a3e6c6cbc3e5f8cfafdb7b0c',
    'core/worldline-root_custody_model.adb': '7deff03133728dd0fd157a801db5fa0ff5bc400684d7f88b90aa1021ba8a9368',
    'core/worldline-root_custody_model.ads': '543d56735706430c664fad35c44cd990941ef465d3293a03f80a04ff8355065d',
    'core/worldline-root_custody_mutation_roles.adb': 'f25bc5831f8c5d31579175ee2750c108bfe33bad8ae4710a6d42f34c8eee768e',
    'core/worldline-root_custody_mutation_roles.ads': 'e75cee8592d01f0186ae7abc540ddcfe52316131b481be7980d219c1107b81b4',
    'core/worldline-root_custody_phase_values.adb': 'baaa1edd44a922739da06c036132a3bccf0a486522c382e26adf9ee29e703c6f',
    'core/worldline-root_custody_phase_values.ads': '9e84e683478f0685c49bf58cfc4fe199972619c93e68249fabb49fe9cd7be7c8',
    'core/worldline-root_custody_raw_operands.ads': '499e68753f324ca4f3aa0886c090e21ea315ca6c320e18e0de7d4361d8b80278',
    'core/worldline-root_custody_replay.adb': '3ab3f75d1fcf2764480e5319560a37cf23b93a197f497fb0d334d475146747fa',
    'core/worldline-root_custody_replay.ads': '605d5849c49da4c5f44e67a7e2e24632da2c1e1a56cbdabc87943d508e4940ff',
    'core/worldline-root_custody_request_abandon.adb': 'e3e4b6a6cd796d7d9016043a770ca384ecbd196e05e72d25fcc24ab01ebbc763',
    'core/worldline-root_custody_request_abandon.ads': 'ecf62ce68b8fe7221c80d2fa579682e1658b4f3dc9e98580bd963f9e76ee170a',
    'core/worldline-root_custody_row_schema.adb': 'a592a8062c61f9dc1d55af9e6cc155a117ac43f74d7e97d87df6216b2507d13f',
    'core/worldline-root_custody_row_schema.ads': 'fe1b6bc68f0fa5ae1818f30b7cf79c7fd38157986d925cc44324ac599ed231ba',
    'core/worldline-root_custody_row_views.adb': 'c2430737cd39e54473cc3e0a09e9ec461380c77b12fb0bdbb05564f0e1a54029',
    'core/worldline-root_custody_row_views.ads': 'd057ce7e2a3ea90ccb9d53d81c3eb66a1b845f72144a8028cfd110f2fa295dc9',
    'core/worldline-root_output_sequence.adb': '1f08806afe89bbc9be59ce7cc0b8bccc6b33aa75cd83f90172135f1dfaeae405',
    'core/worldline-root_output_sequence.ads': 'b69e90a3618709a5f51d73f9ff8ba75a405b9570868afb43771d64cddecaa9d0',
    'core/worldline-scoped_archive.adb': '4669f394542efcdfdc55a348e0e17069abb15fbaea3da563beb3bc3e6a003988',
    'core/worldline-scoped_archive.ads': '1b8336a07f3e615a15eaac9d26b09f50d45b3b1cc2d1b435ec882c6f3dd5de6a',
    'core/worldline-scoped_capture_evolution_projection.adb': 'b001b946705812560fd40cb943e9288e89b831598ea5ba46670e6ceea6a3aa3d',
    'core/worldline-scoped_capture_evolution_projection.ads': 'f91e2071281c95e8d8714864d77343aae996482cfaa8c3ba0bad6273040a09df',
    'core/worldline-scoped_capture_history_projection.adb': '19bf88acc3899664e22fbc98d31dec04c063eba7846d51c6b9c7770b15250b60',
    'core/worldline-scoped_capture_history_projection.ads': 'a608d04779d0bec99ddf56f211976aef1e2f9ea7b61f846662504ba9de612a6a',
    'core/worldline-scoped_capture_namespace_projection.adb': '794ceca684a7b25057e6ed9ec999f171274269d3b07c590977e531e6e7624562',
    'core/worldline-scoped_capture_namespace_projection.ads': '13897ec4d0a576bf0561870a459d9da9d9910b3b6c8d77f1773c008447ee052d',
    'core/worldline-scoped_capture_owner_projection.adb': '51201babec007a0b01e9eaaa03e05342e679e3808812c6f42e040127e5e0040b',
    'core/worldline-scoped_capture_owner_projection.ads': '29c1f87dce38b940f88edcc638d0f3940952c91abcd77383454b5442825a0bc1',
    'core/worldline-scoped_capture_projection.adb': '65a4acc31d9c361f4cb4e1d27a51324d625f6ee1ee9325bf8f5db5421d013c1a',
    'core/worldline-scoped_capture_projection.ads': '61400045960b92a7d5871ffe16bdeba6efaebcbe2897f0e363d84a8a18941118',
    'core/worldline-scoped_record_source.adb': 'e19bae82c81772c7fc8499f65927b3c3026fc4cdddfe4ec59483ef031c606f4b',
    'core/worldline-scoped_record_source.ads': '72cc4f39327b2f22a02af5e5490cb5a7276327f69a0d6a388e4e8f12fe3e865e',
    'core/worldline-sqlite_parameter_source.adb': 'ce3755acacba1cb3ae9f8bf56fa0ee4c83f2652b786eee6a3dcd80da6c332161',
    'core/worldline-sqlite_parameter_source.ads': '08226683331d9546533c474a0306eb7e3d7533e329606a81fa7260043f122b92',
})

# Every explicitly enrolled local specification and body is also normalized
# here, including earlier selected units. The excluded SPARK copies remain
# inventory inputs, not substitutes for imported-library implementation proof.
CONTRACT_PINS.update({
    'core/cosmogony-capabilities.adb': 'b293820b383aa3e43943d2a5a857b756c71a19df495108cc5298d4a79d4dfac5',
    'core/cosmogony-capabilities.ads': '1db286d4c8b877cdf57b638b87d922a4161311da00558e4bce8d9d6146824d3a',
    'core/cosmogony-genesis.adb': 'cfc62aaad23821de0b95eba5aa3788acd0e901e0a9b5e1a28c3935e8f4d3213e',
    'core/cosmogony-genesis.ads': 'ef96190014ba0e524ed145d2b2fc97a98d9a68cda843cadab8fa086df48d432d',
    'core/cosmogony-governed_capabilities.adb': '1f6947d9a19e4bd72060fc1f95a402e9f62cd3a8803c41709cc6f7d306ce8436',
    'core/cosmogony-governed_capabilities.ads': '4070ab0cc9323492829ba5eb5d195e19528c2adb06aee04965f9663f20958fa3',
    'core/cosmogony-revocable_capabilities.adb': '906968cf70fde93dd2cc8266192bae59c1a3e014431eaf998df3c27948c1a2fd',
    'core/cosmogony-revocable_capabilities.ads': '258f7c6cb266d46a113aca226ef0447f16f31f927e390698c9d2a5fb3af3194d',
    'core/cosmogony-universes.adb': 'ea29adc5df2a00febdaf0056fc1ae767d02b8528139395a6eba9095bb5b46b4d',
    'core/cosmogony-universes.ads': 'a1c16dc8015f34e19c8308d526e51c6ce32fd4524ff1a15fb2ecc2f2e3c16c5f',
    'core/cosmogony.ads': 'edfc847cde63fd64594c4e8d595478b7b7dab9591e31fdd65d53688734a5a686',
    'core/decimal_binary64.adb': '71ad35d134c8c299333350f81a7934dcdd899b4f9b7ae42bdae976de6045ed2e',
    'core/decimal_binary64.ads': 'a5ce3d74a7b2e41fc51828305c4f34824c9327c0947384e795e78d231bfc924a',
    'core/evaluation_pending.adb': 'fdf2e7587c096b46bd1358cda8700d8391c79e16b53741100c906364d1c1c54c',
    'core/evaluation_pending.ads': '59437a6fd41436d31c85f72bfe69757e31588c8c6c5916724b464f0329840b78',
    'core/exact_decimal.adb': 'f67b5394837223397b2b1bdc66549255f8c2c35390f176bc3a5c32bcfc36fff9',
    'core/exact_decimal.ads': 'b674a1d45718551fe0b617b8aecc607cc53af256e43e8cffe3993a241e65ab19',
    'core/genesis_float_domain_controls.adb': '5768f68f2db515d221370b1e49f6f2fd82d73667ff62655b0f0681af0cf3060c',
    'core/resource_actor_admission.adb': '534db2b45c1c7e37070c66a15fbf35d82c137ada624d6f076648a451f81e00e5',
    'core/resource_actor_admission.ads': 'b21d0adc001144b91794d2ddd2d8d3bb2efe6b9812c72eeb409cdb3a382776cb',
    'core/resource_actor_admission_wire.adb': '2dd761a9abb8c65c25f3794467c774938180ed4748efae654fa74e757cc8ca62',
    'core/resource_actor_admission_wire.ads': '56bb66885ae97b5f15a92bb4cbb46eaec0b3ce3a7a09acf5d4710d70263cf126',
    'core/resource_observation_classification.adb': '4824c90adef62eb7cc105dbc999cc9cac2988ce3f4ce259ef4f7ced761f45a35',
    'core/resource_observation_classification.ads': 'b7cef33a13b987e714526e9e00b6d4a5c3ca1798e746342c8a5a4d39b02be66f',
    'core/resource_observation_classification_wire.adb': 'f11e64bb6e3c7ff2295d497279c368decd4c1fe1ec725e315ae8b7f2d2cde0ba',
    'core/resource_observation_classification_wire.ads': 'be71fd0e0bb8940a947fcfe52596321e174d35a6b1beb6df69df73878a3f7558',
    'core/resource_scoped_run_ledger.adb': 'dcd7d85aa252a7edb3e814bab82bdc84f89a5512842ea9065e5cf75415f5d5bb',
    'core/resource_scoped_run_ledger.ads': 'bc6dd25ae4da125bd0aa21b09ca324166511a3adff4b3dfeff5495a3bbef1985',
    'core/resource_scoped_run_ledger_wire.adb': 'eaf1e59252e1eff73fc0f137a7fb81969e925d96373dd227018005bb29156105',
    'core/resource_scoped_run_ledger_wire.ads': 'fa91e06d913e1e4d5644084813156d48b9818e402c5e1d73d66cdb251764382c',
    'core/spark.ads': '5adcbdd7d040e27dec76c73fd847fa10642b54bed00b24970d79876a4b93a0ea',
    'core/worldline-actor_archive_replay.adb': 'e8182d161531cd337832ed7bec0131bc3f18159c19272737045e90ef51c92417',
    'core/worldline-actor_archive_replay.ads': 'dd76d12fe5ef3f1008a7b2a9b38546545cd31402edde81a33abe50744d78b481',
    'core/worldline-ancestry.adb': 'c757d66c1b959f8015f3c76ba809064ddf9b28dae382d4e3135bbbf5783e23a7',
    'core/worldline-archive_envelope.adb': '264c294952a00bb86f61b65a249fea5dc191dbc34f4b55988fed43e95cf1d669',
    'core/worldline-archive_envelope.ads': '8d682baa0b262aa56f2755d34507dd384cf102b4fb7448a516cbf273aabcf8f3',
    'core/worldline-collapse.adb': '6f54e8f4fae552c6a6041573d272c9ab8410b5ef0f5cae8a538eb9f4b279234a',
    'core/worldline-collapse_wire.adb': '4fd2489dc0433c4514fe1d5c78f631ba3fc1a8dd559219781d97bbd161ec8c54',
    'core/worldline-confinement_filter.adb': 'b8303641a05283f852ada7706c6b617112f549ae4066ad509cf5e22a39818713',
    'core/worldline-confinement_filter.ads': '4bd7cb37a3aaa6bf9c66c69d65418b22bf73776a520c583ae4ee886765987891',
    'core/worldline-custody_v2_k4_resource_ack.adb': '136a54a6d93c019b783cf40be2ba3ca0c87a4c438e64041ef85160dc433e2f8a',
    'core/worldline-custody_v2_k4_resource_ack.ads': 'd948bec7db8dcf7b4ad44d08674adc61569ce20f959a224a58e4c8d044ee3e33',
    'core/worldline-custody_v2_owner_canonical.adb': '702a7b26cc3c082ca0a53d5bd4a77d0e8f9ecd6869d678827a6951a4fa293062',
    'core/worldline-custody_v2_owner_canonical.ads': '0e39dc2a72fcf03374f30dcea0b05da7485e9f255967ef943723ed43ec52f4f5',
    'core/worldline-evaluation.adb': 'ca4cb14de7052b0b0b4a8e18b7fbdf859e949eb625a35377b8c68a85736285d3',
    'core/worldline-evaluation_agent_native.adb': '29ae7268a77977c1bb5fc1f5ff11104460b02735a16046ca4a307e36293f7b75',
    'core/worldline-evaluation_agent_native.ads': '14088300d81a83e26aad345de50e08df2d4b824a76cc46a5dc5587287d43607c',
    'core/worldline-evaluation_policy.adb': 'b4a38af50921511f74ec55b20f1d6f65e655a55facc2c3a8989e231ca764b86a',
    'core/worldline-evaluation_policy.ads': '374c4f2f38ebc7d0dcce470567c44f1964c25cd9c19a302ee638c01236b62f83',
    'core/worldline-evaluation_producer.adb': '8cd4b6c29d82588e95348a24c0a885144b8cc7d593d7a19998e4121047a09714',
    'core/worldline-evaluation_producer.ads': '1994cf62f1a0f060baffcdb24fbbdafedb13f1b358901d913867e5eaf0e1411f',
    'core/worldline-evaluation_role_native.adb': '7519c90117206ae779b09226ae8de6a80837343c79b99b0953f612e368910798',
    'core/worldline-evaluation_role_native.ads': '6b5d3f9b4fd6fe6f43f4aeb4298346fa1c7acf6d9ee92f1e18fa5f2c2f01609d',
    'core/worldline-journal_witness.adb': 'bc2568fecb751584dbcaf7e0be5d9a970a7e380915e06da22d588e6405b0ea1e',
    'core/worldline-journal_witness.ads': 'dbb41c6c199fff7c16576b235c1f1b5b01d1755bd541d984efa45dcb7221b2d2',
    'core/worldline-lifetime_values.adb': 'b80058f216100145b35db124350af4cf07fd5ce957a184e752de2876e862d598',
    'core/worldline-lifetime_values.ads': 'eaf31b375a636bb29b4786d8e877b51c6fee3354757d820847ba35c47fc2b92c',
    'core/worldline-manager_resource_lifecycle.adb': 'bdc3b9363224a7b00acab7b74ebd1a2fd6e8efe85fe57a1fc3452db205787f3a',
    'core/worldline-manager_resource_lifecycle.ads': 'd8caefed173dac8b4b5525d70f990bedea2bc493159a26da4228259afa80f55d',
    'core/worldline-native_execution_capture.adb': '7d4981360feb23a5cf6efc0492388a111c71477d01ac0b87ec132faea218bb1d',
    'core/worldline-native_execution_capture.ads': '59bc0a3772cd5b7b3484109d6d9e4c6b0ad5d33f2934e3bb9f8cc1b9f66c3838',
    'core/worldline-native_execution_views.adb': '7b9f03d5cb36810dad4db2e1949fac8f616f178eaf125e0ec62d1f3a6afd7d4d',
    'core/worldline-native_execution_views.ads': '8298358b1ef8c3777668169ef86c4bd9a209f542c7a3aa9e4ff4b27ad2e5657c',
    'core/worldline-native_lifetime_observation.adb': '6adf8804ea56ef167c9ae537755fefabc4e4f0962f4937e2b5f8221a8d9199ed',
    'core/worldline-native_lifetime_observation.ads': '1d1469879fb2df9b69fdcd0ecb4fe558ad0a1a8bfdbb8b6435f45d6f8b78ffc2',
    'core/worldline-operation_archive.adb': 'ee84cb8672c147b164f24d0157e13fd2da1461e60f2167f071c9609e352a1e2c',
    'core/worldline-operation_archive.ads': '166582bff87023be44b1c26e272664843803018c357e5b32e73d06e0b19deab7',
    'core/worldline-operation_authority.adb': '0030c894ac1f14f1b32d9454489ccb37c7099bfa45ccdab87eee9205a154b604',
    'core/worldline-operation_authority.ads': 'a644ec3c6fabd99b2c763d76114ace8a8dc7685a1979d4f94c1096825dd45b23',
    'core/worldline-operation_authority_wire.adb': 'a8d3b11e96034e9b641a00273ce68079a6ef90af38afef1677de8d8f168206f5',
    'core/worldline-operation_authority_wire.ads': 'ab8dcf9a8b0a77e92cf275f8cbf5f79536e2e26c21a126a454382be96768abb9',
    'core/worldline-operation_result_relations.adb': 'f551133b88a9a556475bddb1eb620e4c5fba6e62b6ddc0c9a5239c39ab8642d0',
    'core/worldline-operation_result_relations.ads': '85b5b66daf98ab8b4f008335d55fee825cd3f3da7c92f1e4eee39733f948c00a',
    'core/worldline-operation_result_view.adb': '481c3a03f9902e48d12d642ee268e10d74c3bcff63788bce0dec652125245a66',
    'core/worldline-operation_result_view.ads': 'bcf9395350c5f623c6a491a03380f2e0f7b30222d9aae53486f2e08ef3093c03',
    'core/worldline-ordinary_receipt_policy.adb': '8ee977b32b1989b53651d0ce6d2689444193ec0988b5da5df3e1dad03952fcb9',
    'core/worldline-ordinary_receipt_policy.ads': '577acb27604cdf0519c3d6e1160cb775cfd9edc69b81fe4b6338697065a8ecc7',
    'core/worldline-ordinary_reservation_lifecycle.adb': 'c11fcb64cd60a19c99a08afd71650d2c79f1c97f6e44dc699b32ef8b354a4192',
    'core/worldline-ordinary_reservation_lifecycle.ads': 'ff33ab4bc16774d4c1aa0d142f63dee131bcc2326b6457195a6aa4291d97f10a',
    'core/worldline-policy_source.adb': 'ef3b0abca40248ce26ef888487295cfd2c7c301044f1c7df980dc759e73cc45f',
    'core/worldline-policy_source.ads': 'e17a2c95c51e39db0e9fa737c4c977fc99337db658133dfa4305467a8845cd61',
    'core/worldline-policy_syntax.adb': 'ae0c83fa1bb8f2813d6c3b9f1c45783b3b3bf4d3f94de77e35713dceb7d44aea',
    'core/worldline-policy_syntax.ads': '64ab0b1044f3f7a6c7d8f067ea810aa2d53e1dce6eea7e66bd478c0dee626630',
    'core/worldline-producer_bytes.adb': '208216635f2a0554832fcf2d1e9bc987066c965dc8e4b487298b8d8205ebf591',
    'core/worldline-producer_bytes.ads': '865389ee91f1059ddda5f2468a64debfd4ece4c06cc930665e5b6ebb5cc5d07c',
    'core/worldline-producer_render.adb': 'd8ce4db60702adc9db3c91ad61515f6494137ad44ef83d2c9470a38ae5a7dc26',
    'core/worldline-producer_render.ads': 'ad62b58de1c7cb05f1cccb3a102bbdeb3ffa6230101a716df842939388e36cd1',
    'core/worldline-producer_unicode.ads': 'b968afb7b703c83843bc4a0728a4d50e068e78d1733863b57686af7e6a8acef3',
    'core/worldline-producer_values.adb': 'ded1864027fce9e70d2314127ad8e1f037ef8ed36037e0009cf1d7d1396388bf',
    'core/worldline-producer_values.ads': 'a4cbc022b7a28ad207e44cb46d16e33702905737aeb31f94cd66187e8e7c5a10',
    'core/worldline-protected_paths.adb': '0f6ee8ebf1245edec6e6080fc5f7559d4ee9255fda1209d6ecc1617b425312b2',
    'core/worldline-protected_paths.ads': 'd64f35cf78d6e8b9e2a1a6540735ee88cbe6e91833ef6614b5f415eabb24b356',
    'core/worldline-raw_json.adb': '77d187e97cf37ff98dbb3acb656bfa1e70e145669d69fbcac7584f07ef2b1ab6',
    'core/worldline-raw_json.ads': 'bc1d0a599946dce84aadec0465817a918a87bec252fdf84464d58aa3d8b4ffca',
    'core/worldline-recovery_archive.adb': 'a1d25ba35b74469d0b63cd10fdfef008914ff11d9935fd26259486ba59ed133f',
    'core/worldline-recovery_archive.ads': '275d02056637da182c9363ddb62baefdf5f86c11d5dd29f3b661272236ffe725',
    'core/worldline-recovery_material_replay.adb': '9d929d2cdf5afc6fb6f70e4ca5311ceecd1733c0b6ad1126026486c4b2738644',
    'core/worldline-recovery_material_replay.ads': '0abd28d5ab4c5561fe5e208fc92de015688dd5e3cfe2e0684224498559940e1d',
    'core/worldline-recovery_owner_replay.adb': '96188c7e14b714b724f17a4df1d4008e875b5e71dff4df0d6e9779f051b7240d',
    'core/worldline-recovery_owner_replay.ads': '707f0175b40ea4864e1329ce8b7885388a3cbbd40f795a08d938831d9d677c25',
    'core/worldline-recovery_packet.adb': '8634dba807f618db4262c61fd1eb269eff16189754c504e714da783b772c2a2c',
    'core/worldline-recovery_packet.ads': '95a15ac8a909f4e63f2ec9c057ebfe33d2fa6906e39f5473da41c56a5882cdd8',
    'core/worldline-recovery_syntax.adb': '105091a1d4fcb2cafea33891fc0b5b12702540d0a6da2b952deea261b6a3bd47',
    'core/worldline-recovery_syntax.ads': 'edaff9da4c39d030ef2c421d93f99acedb71ad8fa7aa234055b133d2b8014ab5',
    'core/worldline-report_custody_native.adb': 'c1d586a517217747690209812271dcffd32f165a60e27159ce3b2b30666904b4',
    'core/worldline-report_custody_native.ads': '34694dba57f97700f9de76816f70efc17c0a3cb52ee76ea6fba8488c3b7450c7',
    'core/worldline-report_parser.adb': 'd07ce60758153545bbb858497351f5e1a0bbdf55d241d1c7f1d05c7fd2757d80',
    'core/worldline-report_parser.ads': 'bc68b236e9186d2c1ec979e8aea802926d3e407964fb18862bba834e705ccd43',
    'core/worldline-resource_actor_execution.adb': 'e543cce8f7c59f8ee4954d994970c463041daaf0688f5b6e9eeb57b0bc273390',
    'core/worldline-resource_actor_execution.ads': '7dff63ecba10e61054bd7879aa0640f0296f80773d4b794ca49a33735b551ba1',
    'core/worldline-resource_actor_execution_wire.adb': '56b3c0a6b7b32385b87e15948fda2be7fd5be13712d3b90d925e5fdfba191e02',
    'core/worldline-resource_actor_execution_wire.ads': '37547489997336c8145bc41e752aa6f9eb6675f48581ad5199e877c13b7fbaa5',
    'core/worldline-resource_child_execution.adb': '09488580919f7ede93e7fcd44b19ef6cbd8646ec2edb6c1208d03cbe5dd3bbb0',
    'core/worldline-resource_child_execution.ads': '6c8592a7c9d397219551eb7b1fb5cbd8d2ee81c2de95fcb04bcad50376c87207',
    'core/worldline-resource_child_execution_wire.adb': '4cbc5cf9da21f026e25f37dc38748b999adf5c10f636a27672d70f1b2e16bd74',
    'core/worldline-resource_child_execution_wire.ads': '9faba6c3cb91f0e121852ee49537d627bc6047bbe381b749d3cfe2109fb67a7e',
    'core/worldline-retained_evidence_replay.adb': 'e683d832ac1ba364fc89b0f49bc2c9c2bc0d47db782075a29051c97ccd12aca7',
    'core/worldline-retained_evidence_replay.ads': '2028db7dc213a155603e137db1c60e9eee9429da0a397c1964dbc4531762b7b3',
    'core/worldline-retained_raw_decode.adb': '2ea718fb4ec91b46b0cea58e6995514feb9743f57e4553c6e31f6ad0aee05637',
    'core/worldline-retained_raw_decode.ads': '2f52421b9dd97ec7cfde57222b7a9c12ba404891420932991ccc23c10bd37bc3',
    'core/worldline-retained_source_layout.adb': '00c57169be7d9a1743721cf1524801354f0a858ea62b2f633681d29e0074ff0c',
    'core/worldline-retained_source_layout.ads': '3fe1bca37a124de9e20c79ea8cb150e7c3221ff3178d37409631f9af8710a88c',
    'core/worldline-runner_acquisition_bytes.adb': '656e39c93411b197c5a23b5e4f7961462e8bba4db94530a3befaa2fd38d8370b',
    'core/worldline-runner_acquisition_bytes.ads': 'a654e60c114e35d1952043610975477cc4d4283523d7526980c8038a3fd26593',
    'core/worldline-runner_lifecycle.adb': '47772f8d4605b0d6e93411db12758a9ecce5fdeda58c0f62807b27434226b832',
    'core/worldline-runner_lifecycle.ads': 'd8c0b5fefc603266b919ee8acf882e8de57f1f5622f678b51d2ac137fd4d8238',
    'core/worldline-runner_lifecycle_bytes.adb': 'b9787f2e463971c3f6181b6a091c4631562b81050bf89822e718a3eac3c420f8',
    'core/worldline-runner_lifecycle_bytes.ads': '2c192499aa1c30d07c855cdedc579f8f1225013c2ffd65b93b610b98fb3c8b76',
    'core/worldline-runner_outcome.adb': '996a0b0b40ad7a6f22e839a611b8227200572d616b1d8398559d4d9160ce02d9',
    'core/worldline-runner_outcome.ads': 'a136866c23a2df05706e15ce53dead30ae896e40cd5b9a470fbd7ce9711297fe',
    'core/worldline-runner_outcome_bytes.adb': 'c144eaf5f6cc349524ab5e909e0ad66b9bfe359ee0253d9d36e748f37e7bacab',
    'core/worldline-runner_outcome_bytes.ads': '60829d6aaf94a3b26876eb085443a26f087e91a20c645c43f65237581d4659c5',
    'core/worldline-source_audit_native.adb': '7c51e918fc9e9939a4ce93fe86b81f39ec1acc25713fd2881d41824dbbcee631',
    'core/worldline-source_audit_native.ads': '82df68fded3063af4fb787365b95698469ab866a4e6a5bf39201da2fd6694140',
    'core/worldline-source_syntax.adb': '1d18c82771503670ecb407ac540100d8f086f87561d34a82266621a95c23b860',
    'core/worldline-source_syntax.ads': '7e6b176c96eb61891c9f3daf11442ffe3a8ea4675d40fbbc258777d815bbb6c5',
    'core/worldline-source_syntax_provider.adb': '35aa02d1c4a87c1b7a272ab7adc4634422393823893460bde2a2a987d321cda4',
    'core/worldline-source_syntax_provider.ads': '168cce943010311dd4b38109a0c381394e495d3422c2dd370a812fb12ffe1858',
    'core/worldline-source_syntax_reference.adb': 'c3b52f4c8f31e44504376d874095028cb2448d7875d971a6416266ec0a6b8270',
    'core/worldline-source_syntax_reference.ads': '789c46006ca4ef20507b0872404a9aa0246e66fc56e16b9ee62ad3dc44300176',
    'core/worldline-startup_admission.adb': '9327056db04165c38952f483a7d873db424958d8221f6b553608945c4a4f2662',
    'core/worldline-startup_admission.ads': '3330351f545ce927d0b2b67511b7b7525ea761c35ad7e135c5cd13cb8c9f74b3',
    'core/worldline-startup_admission_owned.adb': '8f91b15f708383ab4173ed419c674850c3c3f85e5078c48b8abbdf822d2a0ad9',
    'core/worldline-startup_admission_owned.ads': 'a4e1a247fda4738206cf30b793a15feb877fefd804ea736e8f8e277756e783d3',
    'core/worldline-startup_installation.adb': 'c3900cd31300b8b8e72e24c7bb9d607d314fa67631311dd329a0fc5185f3be97',
    'core/worldline-startup_installation.ads': '9c1eb3d273934830ead7d0058cb4b336c575c21e6a265b438fad926e9f3d4974',
    'core/worldline-startup_issuer_source.adb': 'b5e6a1f6a9f10d95ef1ebd06b2be37fbf008fbe1355f5d252935d3ec20104e93',
    'core/worldline-startup_issuer_source.ads': '2a066aea1a117e28f4c4e70f66fa1889580eec6fc10151c250caf5dea7e6fb81',
    'core/worldline-startup_source_custody.adb': 'f346fcb24e726bcb756a31b1153e46e3c2f21fdddea99c7fb5db10e9b5dea442',
    'core/worldline-startup_source_custody.ads': '3994e41a79ba06991db72feed9b1ef00398864d5aec15824acbdaa25ff25f897',
    'core/worldline-transaction_archive_json.adb': 'f0bec12315d5fcc5ae0f7a70333a5c97059dd920c71a2aa5a4374b2719f4b809',
    'core/worldline-transaction_archive_json.ads': 'f7b9441fda9dbedaf96007201208dbff9466b5505642da5ec6ad4f6c2b9858d1',
    'core/worldline-transaction_relations.adb': 'ebcdd3d99cb425c0988591e73a7ffedd93340dd2edc99139d164fb50670b94b5',
    'core/worldline-transaction_relations.ads': '6fcb5ab25fc69455834a3aa7927ae15f5ec8521886a0387ec9d2c3988fd3043d',
    'core/worldline-transitions.adb': 'c3a57c5961ed121d350e36f61a9aa281195dff046f294e6ba032c545e4cf645c',
    'core/worldline-world.adb': '3fb26e1e982bac4b754dacd2b0b2fbb0c0de4be6a62e2bef191d5812ccfea459',
})

# Exact whole-owner observer helpers; retain the entire inherited ordered roster.
REQUIRED_PROVED += [
    'Worldline.Custody_V2_Owner_Canonical.Authenticated_From_Data',
    'Worldline.Custody_V2_K4_Resource_Ack.Establish_From_Data',
    'Worldline.Custody_V2_K4_Resource_Ack.Authenticated_From_Data',
]

# Original source-owner join; additive enrollment is not proof or installation.
REQUIRED_PROVED += [
    'Worldline.Excluded_Source_Owner.Launch_Reference',
    'Worldline.Excluded_Source_Owner.Acquisition_Reference',
    'Worldline.Excluded_Source_Owner.Completion_Reference',
    'Worldline.Excluded_Source_Owner.Decide',
    'Worldline.Startup_Source_Custody.Bootstrap_Corresponds',
    'Worldline.Startup_Source_Custody.Projection_Corresponds',
    'Worldline.Startup_Source_Custody.Image_Corresponds',
    'Worldline.Startup_Source_Custody.Role_Selected',
    'Worldline.Startup_Source_Custody.Readbacks_Correspond',
    'Worldline.Custody_V2_Requester_Join.SCM_Credentials_Match',
    'Worldline.Custody_V2_Requester_Join.Signed_32_Matches',
]
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset({
    'core/worldline-excluded_source_owner.ads',
    'core/worldline-excluded_source_owner.adb',
})
CONTRACT_PINS.update({
    'core/worldline-c_api.adb': '64a839d076a4e52d8fb65c599a91f9eb0812adef30f8e48a4e80669f56557f52',
    'core/worldline-c_api.adb#Excluded_Source_Owner_Decide_V1': 'c94165601c4ca87b91b25c18ff458ea8f87997f42ff0aefa306f7b619e405d88',
    'core/worldline-c_api.ads': '1da0afffd071cb78449216a359b362f9d31e6cae22e9d02c09cb19bfce097efe',
    'core/worldline-custody_v2_requester_join.adb': 'c04cc5de8c3a81b3e59b8b825fa4a8beace7ad6c35217591cb0b3982516cd7eb',
    'core/worldline-custody_v2_requester_join.ads': 'f287886125cb12a0488466decbfcae8379462b1ebac7ef595c04e0c50a441c5f',
    'core/worldline-excluded_source_owner.adb': '86873a7df4553b742fe345c55a5bbffa25ad6c53d935e264393912e07d1051d5',
    'core/worldline-excluded_source_owner.ads': 'd00bfcb4c3b7bff131507ea11ca8158e7d9355ae51e5acd3ba468b9e396b5e62',
    'core/worldline-startup_source_custody.adb': 'f346fcb24e726bcb756a31b1153e46e3c2f21fdddea99c7fb5db10e9b5dea442',
    'core/worldline-startup_source_custody.ads': '3994e41a79ba06991db72feed9b1ef00398864d5aec15824acbdaa25ff25f897',
    'core/worldline-startup_installation.adb': 'c3900cd31300b8b8e72e24c7bb9d607d314fa67631311dd329a0fc5185f3be97',
    'core/worldline_core.gpr': 'f1a6492bceff785f35dec5f30d3d5470fe7f439b5a85c02ddcbb3b4b44a47436',
})

# Complete fixed owner helper scope, not merely public decision postconditions.
# The inherited full required sequence and 251 check floor are unchanged.
# These are original strict all-source obligations; no source-only proof credit.
REQUIRED_PROVED += [
    'Worldline.Startup_Source_Custody.File_Identity_Corresponds',
    'Worldline.Excluded_Source_Owner.JSON_Matches',
    'Worldline.Excluded_Source_Owner.Hex_Matches',
    'Worldline.Excluded_Source_Owner.Bit',
    'Worldline.Excluded_Source_Owner.Sealed',
    'Worldline.Excluded_Source_Owner.Identity',
    'Worldline.Excluded_Source_Owner.FD_Number',
    'Worldline.Excluded_Source_Owner.Descriptor_Reference',
    'Worldline.Excluded_Source_Owner.Process_Reference',
    'Worldline.Excluded_Source_Owner.Projection_Reference',
    'Worldline.Excluded_Source_Owner.Root_Directory',
    'Worldline.Excluded_Source_Owner.Boolean_Is',
    'Worldline.Excluded_Source_Owner.Prefix_Events',
    'Worldline.Excluded_Source_Owner.Decimal',
    'Worldline.Excluded_Source_Owner.Status_Columns',
    'Worldline.Excluded_Source_Owner.Group_Multiset',
    'Worldline.Excluded_Source_Owner.Poll_Matches',
    'Worldline.Excluded_Source_Owner.Text_Number',
    'Worldline.Excluded_Source_Owner.Argv_Raw',
    'Worldline.Excluded_Source_Owner.Invocation_Reference',
    'Worldline.Excluded_Source_Owner.Hex_Number',
    'Worldline.Excluded_Source_Owner.Map_Line',
    'Worldline.Excluded_Source_Owner.Mapped_Reference',
    'Worldline.Excluded_Source_Owner.Owner_Reference',
    'Worldline.Excluded_Source_Owner.Creator_Reference',
    'Worldline.Excluded_Source_Owner.Receive_Reference',
    'Worldline.Excluded_Source_Owner.Close_Reference',
    'Worldline.Excluded_Source_Owner.Wrapped_Text',
    'Worldline.Excluded_Source_Owner.Peer_Name',
    'Worldline.Excluded_Source_Owner.Target_Reference',
    'Worldline.Excluded_Source_Owner.Receipt_Source',
    'Worldline.Excluded_Source_Owner.Pidfd_OFD_Reference',
    'Worldline.Excluded_Source_Owner.Dead_Pidfd_Info',
    'Worldline.Excluded_Source_Owner.Terminal_Reference',
    'Worldline.Excluded_Source_Owner.FD_Path',
    'Worldline.Excluded_Source_Owner.Word_32',
    'Worldline.Excluded_Source_Owner.Watch_Reference',
    'Worldline.Excluded_Source_Owner.Stream_Reference',
    'Worldline.Excluded_Source_Owner.Capabilities_Dropped',
    'Worldline.Excluded_Source_Owner.Traversal_Reference',
    'Worldline.Excluded_Source_Owner.Read_Allowed',
    'Worldline.Excluded_Source_Owner.Ancestor_Path',
    'Worldline.Excluded_Source_Owner.Private_Topology_Reference',
    'Worldline.Excluded_Source_Owner.Private_Source_Reference',
    'Worldline.Excluded_Source_Owner.Memory_Reference',
    'Worldline.Excluded_Source_Owner.Result_Reference',
]


# Original physical Actuation domain restored additively; no historical proof credit.
# Preserve the entire inherited ordered roster, exact floor and C_API boundary.
REQUIRED_PROVED += [
    'Worldline.Actuation.Same_Entry',
    'Worldline.Actuation.Decide',
    'Worldline.Actuation_Full_Wire.Well_Formed',
    'Worldline.Actuation_Full_Wire.Decode',
]
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset({
    'core/worldline-actuation.ads',
    'core/worldline-actuation.adb',
    'core/worldline-actuation_full_wire.ads',
})
CONTRACT_PINS.update({
    'core/worldline-actuation.ads': '5e7b3d6e8a8b899ef66fa51c6367f673f8db7be999331410866d77438714a365',
    'core/worldline-actuation.adb': 'ffb195061d07aa9520a8becfe1a69ccae38a757efb2a1f1ad7728c1d0ca1eabb',
    'core/worldline-actuation_full_wire.ads': 'ac1626dfbf05276ffedb10d629c7b80ca48dd132661ee2357b971e1e1432255f',
})


# Explicit local SHA compression contracts: retain every original proof obligation.
# Add separate private-helper proof names; no inherited or contextual proof credit.
REQUIRED_PROVED += [
    'Attest.SHA256.Compress',
    'Attest.Custody_SHA256.Compress',
]


# Additive content-erasure proof stages; every original equation/check remains required.
# No proof credit transfers across the private contracts or this source change.
REQUIRED_PROVED += ['Evaluation_Finalization.Lemma_Content_Rows', 'Evaluation_Finalization.Lemma_Content_Completion', 'Evaluation_Finalization.Lemma_Content_Failure', 'Evaluation_Finalization.Lemma_Content_Promotion']


# Distinct actual failed-handoff closure: preserve the whole original proof sequence.
REQUIRED_PROVED += [
    'Worldline.Custody_V2_Root_Evidence.Failed_Witness_State',
    'Worldline.Custody_V2_Root_Evidence.Closed_Witness_State',
    'Worldline.Custody_V2_Root_Evidence.Closed_Owner_Plan',
    'Worldline.Custody_V2_Root_Evidence.Witness_Terminal_Joined',
]

# Total original dependency equation and its real equivalence body remain mandatory.
# Preserve every inherited ordered obligation, full-source scope and check floor.
REQUIRED_PROVED += ['Worldline.Evaluation_Authority.Original_Dependencies', 'Worldline.Evaluation_Authority.Lemma_Dependencies_Equivalent']


# Shared String parser: additive source and complete helper/instance obligations.
DECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset(['core/worldline-json_syntax_types.ads', 'core/worldline-generic_json_syntax.ads', 'core/worldline-generic_json_syntax.adb'])
REQUIRED_PROVED += ['Worldline.Producer_Values', 'Worldline.Producer_Values.Byte_At', 'Worldline.Producer_Values.First_Key', 'Worldline.Producer_Values.Hex', 'Worldline.Producer_Values.Original_Form', 'Worldline.Producer_Values.Original_Node', 'Worldline.Producer_Values.Raw', 'Worldline.Producer_Values.Scan', 'Worldline.Producer_Values.Space', 'Worldline.Producer_Values.String_Grammar', 'Worldline.Producer_Values.String_Grammar.Advance', 'Worldline.Producer_Values.String_Grammar.Is_Hex', 'Worldline.Producer_Values.String_Grammar.Match_Token', 'Worldline.Producer_Values.String_Grammar.Parse', 'Worldline.Producer_Values.String_Grammar.Peek', 'Worldline.Producer_Values.String_Grammar.Read_Unit', 'Worldline.Producer_Values.String_Grammar.Scan', 'Worldline.Producer_Values.String_Grammar.Scan_String', 'Worldline.Producer_Values.String_Grammar.Source_Length', 'Worldline.Producer_Values.String_Grammar.Space', 'Worldline.Producer_Values.String_Length', 'Worldline.Producer_Values.String_Read', 'Worldline.Producer_Values.Text.Emit', 'Worldline.Producer_Values.Text.Unicode', 'Worldline.Producer_Values.Tree_Admitted', 'Worldline.Producer_Values.UTF8_Width.Tail', 'Worldline.JSON_Syntax_Types.Within']
CONTRACT_PINS.update({'core/worldline-json_syntax_types.ads': 'a20e5ad2862ebfbcbcaed2eac4572cf80afdaac22b0841acd67a4df0309dc80c', 'core/worldline-generic_json_syntax.ads': 'c18cb5434ab194664bdeb2b4e8fd42b41a4c9e4bc3a9106317fb84bd1b0b919c', 'core/worldline-generic_json_syntax.adb': '1e76d5a066816a2deda6a60ccfb46325145258b4058d69289c7cdd1e1ffdf7a4'})

# Scalar-record link digests, chain congruence, reservation split, and
# expression-function classification. Pins follow the source; not proof credit.
CONTRACT_PINS.update({
    'core/attest/attest-sha256.ads': 'b5b299d3559e8a083d1edbbaefc96f76f73a0c4e0e6d2dfdcfb6d3fc0c4d7bec',
    'core/attest/attest-sha256.adb': '60ac468bec5bc75013407700b2122faa52a8295c4c43c19359a2e4fea4dc3be2',
    'core/worldline-receipts.ads': 'a354588d79bc6d01973afcf10b9b31a08d996e2056a1bad8db05e97fe7636dd6',
    'core/worldline-receipts.adb': '8b30e5567ec7a86962f9cea3cd67b6d07194dc726e70b025bc2f97a406767829',
    'core/worldline-causal_graph.ads': '4c1db06549310c2dd93c26b9e109dd832a0f43390fe7ece37dbab06934b78ae7',
    'core/worldline-causal_graph.adb': 'e3239b7770a185f4eef90d838c803a64b128e84380e3af27513867632ff3c121',
    'core/worldline.ads': '6fc501e7d5e4927784d415e25c84339efd42a96358216c69825882deea3603e3',
    'core/worldline-chain_authority.adb': 'ad10d252025b8d46dba16b99031b733f40d13d29d391a703bdf8b3b193c7166d',
    'core/resource_reservation_transition.adb': 'f13ad8e1ef22ee22b3a6902b5c6945b0dcbb64d1385e28e8ad9d77fa083d0e86',
    'core/resource_observation_classification.ads': 'b7cef33a13b987e714526e9e00b6d4a5c3ca1798e746342c8a5a4d39b02be66f',
    'core/worldline-confinement_filter.adb': 'b8303641a05283f852ada7706c6b617112f549ae4066ad509cf5e22a39818713',
    'core/resource_observation_classification.adb': '4824c90adef62eb7cc105dbc999cc9cac2988ce3f4ce259ef4f7ced761f45a35',
    'core/worldline-resource_actor_execution.adb': 'e543cce8f7c59f8ee4954d994970c463041daaf0688f5b6e9eeb57b0bc273390',
    'core/worldline-policy_source.adb': 'ef3b0abca40248ce26ef888487295cfd2c7c301044f1c7df980dc759e73cc45f',
    'core/worldline-evaluation_policy.adb': 'b4a38af50921511f74ec55b20f1d6f65e655a55facc2c3a8989e231ca764b86a',
    'core/worldline-recovery_syntax.adb': '105091a1d4fcb2cafea33891fc0b5b12702540d0a6da2b952deea261b6a3bd47',
    'core/worldline-producer_render.adb': 'd8ce4db60702adc9db3c91ad61515f6494137ad44ef83d2c9470a38ae5a7dc26',
    'core/worldline-startup_source_custody.adb': 'f346fcb24e726bcb756a31b1153e46e3c2f21fdddea99c7fb5db10e9b5dea442',
})
