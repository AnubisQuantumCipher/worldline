# Erratum E1 to the D2 checked-Ghost inventory: pinned-file coverage

Author-side erratum by the Claude Code lead, 2026-10-04 ~21:10Z. It records an error found after the sealed review. It
does not edit the reviewed inventory (INVENTORY.md `e5b9984d2beadf12f35e3018aff33c23a47d93adea7bd886abe8df2db46574b6`)
or its review. It is not a review result, and it needs independent review wherever it is relied on.

## The error

INVENTORY.md:708-711 says that `CONTRACT_PINS` has "82 entries [OBS]" and that "worldline-chain_authority and
resource_run_ledger are not pinned there [OBS]".

That reading covered only the first dictionary literal, `proof_manifest.py:329`. The manifest adds pins in later
top-level `CONTRACT_PINS.update({...})` statements at lines 418, 925, 942, 955, 969, 974, 997, 1000, 1005, 1009,
1014, 1017, 1020, 1023, 1026 and 1029. All line numbers refer to
`work/claude-composition-v5-beta/source/runtime/worldline/proof_manifest.py`.

## Observed facts (read-only AST walk over every top-level `CONTRACT_PINS` assignment and `update` call)

- **169 effective pin keys.** This matches the "effective pin count observed is 169" in the sealed commonV5-beta
  composition review (`work/claude-composition-v5-beta/review/gpt61-v1/REVIEW.md:48`).
- **Chain-authority files.** `core/worldline-chain_authority.adb`, its `.ads`, `_c_api` and `_wire` files are first
  pinned at line 942. The `.adb` is pinned again in the update calls at lines 969, 997, 1014, 1023 and 1029. Line 1009
  re-pins the `.ads`.
- **Run-ledger files.** `core/resource_run_ledger{,_c_api,_wire}.ad[sb]` are added to `DECLARED_CORE_ADA_SOURCES` at
  line 968. They are pinned by the update calls at lines 969, 997, 1014, 1023 and 1029. Line 1000 pins
  `_c_api.adb` again.
- **No other form of pin change.** The walk found no subscript stores into `CONTRACT_PINS`.
- **Every packet touches pinned text.** Every file in every lead packet 01–14 is a pinned key. That covers both the
  workflow packets and the `wt-1` copies of 13 and 14:

  | Packet | Pinned files it changes |
  |---|---|
  | 01 | `worldline-recovery.ads` and the two marker-test files |
  | 02 | `evaluation_epoch.adb` (and its pending copy), `evaluation_finalization.ad[sb]` |
  | 03 | `worldline-c_api.ad[sb]`, `worldline-resources_c_api.ad[sb]` |
  | 04 | `resource_quantities.ads` (and its pending copy) |
  | 05 | `canonical_artifacts.adb`, `resource_ledger.adb`, `resource_quantities.adb`, `resource_reservation_transition.adb`, `worldline-owner_conjunction.ads`, `worldline-owner_subject_projection.adb`, `worldline-resources.ad[sb]` |
  | 06 | `worldline-resources.adb` |
  | 07 | `canonical_artifacts.adb` |
  | 08 | `resource_ledger.adb` |
  | 09 | `resource_reservation_transition.adb` |
  | 10 | `resource_ledger.adb` |
  | 11 | `resource_run_ledger_wire.adb` |
  | 12 | `evaluation_epoch.adb` (and its pending copy), `worldline-resources.adb` |
  | 13 | `resource_reservation_transition.adb` |
  | 14 | `worldline-chain_authority.adb` |

## Consequences

- **Approval labels.** The inventory labels some H1 (chain replay) and run-ledger directions "L" on the premise that
  those files are unpinned. They carry the same pinned-text approval requirement as the other pinned files.
- **The sealed D2 correction C-PINS** says: "a concrete change to enrolled pinned text must carry O-PINS operator
  approval as well as independent review and regenerated effective pins."
  - C-PINS applied the boundary that the lead's own brief stated in item 4 ("operator approval for pinned text or
    public contract").
  - Taken together with this erratum, the ruling covers every lead packet.
- **Already-qualified compositions.** The sealed commonV5-alpha and commonV5-beta reviews qualified packets 01, 02 and
  04–09, including their pin refreshes, without any operator pinned-text approval.
- **HANDOFF integration step 1** says: "Recompute all effective normalized pins and full ordered proof enrollment
  without changing the original policy prefix or replacing original accepted cases."
- This is carried to the operator as package item P-1. Nothing here decides it.
