# Capacity_Fits: reuse the existing column-bound lemma

UNAPPLIED proposal. The core candidate addresses the actual D53 failure; the separately hash-bound pending candidate has not been executed or reported as failing.

Add only this call inside the existing ghost column block, immediately after the existing assertion about `Before_Residue` and `Before_Place`:

```ada
               Column_Bounds
                 (Before_Residue, Before_Place, Column_Value);
```

The D53 `resource_quantities.spark` row reports `resource_quantities.adb:587:50`, `VC_ASSERT`, medium, “assertion might fail, cannot prove Residue < Place”; its unproved status is a time limit. The complete report records `Column_Bounds` proved, while `Capacity_Fits` is not proved. The result's exact command, tool identities, source hashes and diagnostic row are retained in `proposal.json`. Build and runtime exited 0; proof exited 1. Those are finite candidate outcomes, not full WORLDLINE acceptance.

The current core body is byte-identical to the actual D53 dependency snapshot. The original loop invariant already states strict residue/place bounds. Saved ghost constants retain those values while only the borrow state changes. The existing `Borrow_Column_Facts` postcondition and `Column_Value` assertion supply the other premise. `Column_Bounds` already has the exact lower/upper postcondition needed after the unchanged residue and place assignments. Reusing that local, analyzed body avoids asking the solver to rediscover its nonlinear argument inside the larger function.

No lemma body, invariant, existing assertion, public contract, admitted span/magnitude domain, debit/credit calculation, branch or return changes. The assertion-enabled path may execute additional ghost arithmetic: `Column_Bounds` calls the existing `Scale_Column` with `Column` and `255 - Column`. Those factors use the existing byte-column condition; there is no new quantity bound. Do not claim zero checked-runtime cost or proof success before the original full-closure rerun.

`core.patch` and `pending.patch` are separate call-only diffs against their own recorded hashes. The pending body differs elsewhere and must never be replaced by the core body. Its local invariant, constants, assertions and helper signature match this proposed use, but the pending profile requires its own complete dependency proof; core proof does not transfer.

All original source/contract pins remain untouched. The inspected manifest's existing Resource_Quantities pin literals already differ from the current bodies/specs. A later pin migration needs its own reviewed source/proof epoch; this local change does not authorize refreshing stale pins to manufacture a pass.

Coordinator validation: record the reviewed decision, preserve D53 v1, use fresh outputs, and rerun the unchanged complete candidate build/all-unit proof/runtime under the original resource and solver bounds. Retain every failed result. If reverted, delete only the added call and require each preimage hash. No product file or original evidence was changed by this preparation.
