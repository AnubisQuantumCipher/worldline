# F32 investigation: original controls that assert AUTHORIZED without Resulting_Requirement

**Status: STATIC engineering investigation. Not a review, not acceptance, not run evidence.**

- **Investigator.** A Claude Code general-purpose subagent with a fresh context. It did not author D1 or PK-0. It
  finished ~17:10Z on 2026-10-05.
- **Its brief.** Read-only. It executed nothing and read no transcript.
- **How it reached this file.** The harness refused its write of this file ("Subagents should return findings as
  text"). It did not route around that, and returned its findings as text. The lead (claude-opus-5-5) wrote that text
  below verbatim; only this header is the lead's.
- **No JACKAL.** The investigator reports that every hash and count was read from tool output and none was derived, so
  it made no JACKAL calls.

---

Paths: W = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow`, S5 = `W/work/claude-composition-v5-beta/source`, B = `/home/sicarii/Work/ada-spark-readiness-20260927/codex-continuation-20260930`, ENG = `B/phase1-finalization-owned-acquisition-engineering-v1`.

**Verdict: the authors' claim is correct.** For these requests AUTHORIZED is unreachable. The answer is IDENTITY_ABSENT only when native roster and agent readiness both come back 1; otherwise it is EXECUTION_EVIDENCE_INCOMPLETE or INVALID_REQUEST. The defect was not introduced by the v5-beta composition. It entered at Codex's item1 V2 correction.

**1. What the tests build and assert**
- `RawDependencyControls.checkpoint()` (`test_raw_evaluation_default.py:522-533`) builds a checkpoint-mode request with `current_requirement=h(8)`, `resulting_requirement=None` (:530) and `roster_complete=False` (:526).
- `bound_request()` (:71-81) and `collapse_values()` (`test_finalization_kernel.py:245-255`) switch that request to `CANDIDATE_EVALUATION` and set the evaluated requirement, executed verifiers and checkpoints. Neither sets `resulting_requirement`, so it stays `None`.
- The AUTHORIZED assertions are at `test_raw_evaluation_default.py:88-89` and `test_finalization_kernel.py:262-263`.
- Python supplies no default. `CollapseInput` (`core.py:214-258`) has no defaults, and `_optional_hash(None)` returns "absent" with all-zero bytes (:596-598). The field order (:121) matches the Ada wire record (`collapse_wire.ads:56`).
- The bytes reach the kernel unchanged on both paths:
  - raw evaluation: `evaluation_wire.py:94-122` calls `wl_collapse_decide_raw_evaluation_v3`
  - finalization: `finalization_kernel.py:286-322` calls `wl_collapse_decide_finalization_v1`

**2. What the Ada decides**
- Both C entry points overwrite only the two roster bytes before calling the decision (`worldline-c_api.adb:817-819`, `evaluation_finalization_c.adb:485-487`).
- `Well_Formed` accepts an absent Resulting_Requirement in candidate mode (`collapse_wire.ads:89-137`), and `Decode` marks it not present (:237). The dependency function asks for the primary evaluation and the agent, because tested root equals staged root (`evaluation_authority.ads:23-29`).
- `Decide` (`worldline-collapse.adb`) clears every check through :18. Then:
  - :20-23 returns Execution_Evidence_Incomplete if roster readiness is 0
  - :24-25 returns Identity_Absent, because `Required_Present` requires `Resulting_Requirement.Present` in candidate mode (`.ads:151`)
- The contract says the same without relying on the body. `Post` makes Authorized equal to `All_Hold` (`.ads:217`), `Evidence_Holds` requires `Same(Current, Resulting)` (:188), and `Same` is false when either side is absent (`worldline-identities.ads:80-82`).
- The same helpers reach two more AUTHORIZED assertions:
  - `test_evaluation_row_projection.py:87-96`
  - `test_context_cast_lifetime.py:153-163`
- By contrast, `test_collapse_recomputes_carried_roster` (:471-490) and `test_revalidation_binding.py:303-325` set `resulting_requirement` explicitly and are not affected.

**3. Provenance (sha256 and diff)**
- In S5, both tests, the collapse unit, the wire, C API, glue and Python wrappers are byte-identical to the v5-beta preimage (v4). None appears in the composition's changed paths. The roster's working tree, `integrated-ordinary-v8/source`, holds the same bytes.
- `test_finalization_kernel.py` (`76141dfb…`) has never changed: it is the only version among 277 copies under W/work and matches the version in `ENG/source`.
- Lineage of `test_raw_evaluation_default.py` and the collapse unit:

| Tree | test_raw_evaluation_default.py | collapse.ads | Resulting_Requirement |
|---|---|---|---|
| `ENG/source`, pre-item1 original | `53db45a0…` | `ba6e2a53…` | not in the kernel; AUTHORIZED reachable (`ENG/source/core/worldline-collapse.ads:135-152`) |
| item1 V1 (`ENG/authority-item1-priority-v1`) | `979e4639…` | `98b2661b…` | added to the kernel for obligation OB-003 (`ALL-ORIGINAL-OBLIGATIONS.md:57`); fixture set to `h(8)` |
| item1 V2 (`authority-item1-priority-v2`, same as `W/work/item1-repair/source`) | `22b5b189…` | `98b2661b…` | checkpoint mode now requires it absent (`collapse_wire.ads:133`); fixture changed to `None` at :530 |

- The V2 HANDOFF says: "Valid checkpoint fixtures explicitly supply absence." The candidate-mode helpers that reuse that fixture were not updated, and `bound_request` is not in V1's `original-methods.json` list of changed methods.
- `integrated-collapse-composition` imported this delta, and every later composition kept it.

**4. Recorded execution evidence (files read as found; not authenticated)**
- Pre-item1 bytes only (`53db45a0…`):
  - `B/phase1-evaluation-checked-scan-ordinary-v1/evidence/default-tests-v1`: return code 0; `child.stderr` line 4 reads "test_complete_owned_join_and_padded_epoch … ok", then "Ran 41 tests … OK".
  - `B/phase1-finalization-ordinary-v2/evidence/default-tests-v1`: the same result.
  - `B/phase1-reviewed-resources-default-ordinary-v1/evidence/default-tests-v1`: terminated with return code -15.
  - `metadata-tests-v1` in the first two roots: "ok" for the row-projection test.
- The S5 bytes (`22b5b189…`) have no recorded run. No finalization-kernel run exists anywhere under B or W/work. The roster receipts `integrated-ordinary-v8/evidence/{default,metadata,finalization-kernel}-tests-v1` do not exist.
- The source's own checkpoint, `assurance/checkpoints/phase1-native-lifetime-2026-10-03.json`, lists `default-tests`, `metadata-tests` and `finalization-kernel-tests` under `remaining_required_actions`.
- A missing failure record is not a pass: at the S5 bytes these tests are unrun.

**5. Roster entries**
- `ORIGINAL-ORDINARY-ROSTER.json` `literal_g8_launches`, all with working directory `W/work/integrated-ordinary-v8/source`:
  - [35] mode `default-tests` runs `python3 -m unittest -v test_raw_evaluation_default`
  - [36] mode `metadata-tests` runs `test_evaluation_row_projection`
  - [43] mode `finalization-kernel-tests` runs `test_finalization_kernel`
- The roster also records `results_transferred: false` and `source_matching_rerun_required: true`.
- `REQUIRED-LIFETIME-CONTROLS.json` does not list the two F32 modules. It does list `test_context_cast_lifetime.py::test_discarded_full_prepared_graph_releases_without_cyclic_collection`, which is hit by the same defect, with status "UNRUN" and "ALL remain required".

**6. What this means for "keep every original control fixed"**
- (a) A marshalling default makes it Authorized: refuted.
- (b) The v5-beta composition changed behaviour: refuted for these files.
- (c) The tests already fail upstream: yes from item1 V2 onward, though never run at those bytes.
- (d) Codex item1 V2 made the fixture inconsistent: supported.

So the reading the evidence supports is (d), with (c) as its result. Run on matching source, four original controls will fail: the three AUTHORIZED assertions above plus the lifetime control. Two original requirements now conflict: the OB-003 rule that candidate mode requires Same(Current, Resulting), and the original controls that assert AUTHORIZED for a fixture with no Resulting_Requirement. That is an open obligation for you or the lead to route; under WORKSPACE-RULES.md:6 and HANDOFF.md:29 neither side may be weakened or skipped, and I propose no edit.

Only a run in an admitted frame can show the actual returned code (it depends on native readiness and context joins) and whether other assertions in these modules also fail. Whether the recorded pre-item1 runs are authentic is also not established here.
