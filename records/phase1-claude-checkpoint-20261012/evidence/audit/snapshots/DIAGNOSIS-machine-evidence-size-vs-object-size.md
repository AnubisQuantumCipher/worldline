# Pre-existing Source20 defect: Custody_V2_Machine_Evidence.Joined can never accept a genuine frame

Reported by the machine-evidence unit owner (fresh-context Claude subagent) on 2026-10-12 while proving
core/worldline-custody_v2_machine_evidence.adb (its commit 259647f on campaign/machine-evidence; unit proves 188/188 at level 3).
Behavior was deliberately NOT changed by the owner (brief rule 6: intent must be unambiguous from code and tests, and no test
exercises Joined). Recorded here for the lead's decision and for the matrix (authority area 2, resource reservations).

Observation (owner's report; to be independently re-measured by the lead before any fix):
- Joined compares frame byte lengths and element strides against 'Size-derived values:
  Input_C'Size/8 = 249, Disk_C'Size/8 = 41, Quantity_C'Size/8 = 17, L.Result_C'Size/8 = 25
  (GNAT 'Size values 1992/328/136/200 bits; divisions via jackal_exact, status exact).
- The producers runtime/worldline/resource_machine_evidence.py (observe_policy / observe_ledger) emit bytes(ctypes struct);
  ctypes.sizeof: _Input 256, _Disk 48, _Quantity 24, L._Result 32 (Row 72 and policy Result 16 agree with 'Size/8).
- Consequence: `input` is 256 bytes, never 249, so Joined returns False at its length guard for every genuine frame; the disk and
  detail strides (41, 17) also differ from the real strides (48, 24). Joined is the last conjunct of Root_Evidence.Held
  (worldline-custody_v2_root_evidence.adb:1650), so Held can never hold for a genuine machine frame.
- Candidate fix (not applied): 'Size -> 'Object_Size at the six length/stride sites; the 17/25-byte single-value read guards in
  Quantity/Optional are correct as 'Size.

Lead's disposition: open defect in the frozen design, pre-existing (the sites are unchanged since Source20). The spec comment says the
unit "Replays BOTH original complete numeric machine frames from actual resource_machine_evidence.observe_ledger/observe_policy", so
accepting genuine producer frames is the stated intent. Decision deferred to the roster results: if a roster row or the matrix's
area-2 controls depend on Held, the fix is applied with a producer-derived regression test (genuine frame accepted, mutated frame
refused) and recorded as a demonstrated blocker; otherwise it stays an open obligation named in the matrix.
