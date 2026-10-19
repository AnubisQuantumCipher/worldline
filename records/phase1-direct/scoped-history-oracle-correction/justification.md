# Scoped-history refusal oracle correction

The first capture regression run failed two unchanged tests. Preserve that run
in `../capture-runtime-v1` and the exact original test here as `original-test.py`.
`baseline-source.json` verifies that the decision specification, implementation,
Python transport and original test were unchanged from the published parent.

The normative `Decision_Reference` in `resource_scoped_run_ledger.ads` first checks
shape, then physical projection, then immutable projection prefix. The later
context-advance branch checks historical row equality. The public `Check`
postcondition requires exact equality with this reference, not just refusal.

The hidden-charge fixture has valid shape but an inconsistent physical total;
the reference requires `PHYSICAL_PROJECTION_INVALID`. The empty proposed rows
and projection fixture loses the original prefix; the reference requires
`IMMUTABLE_ORIGIN_CHANGED` before the later historical-row gate. Neither case
is allowed to return `READY`. The executable policy and its contract are not
changed to accommodate either test.

Only these two expected status literals change. The complete original packet
fixtures remain. The existing absent-frame-epoch test still demands
`INVALID_BEFORE`. An added context-advance case preserves the physical
projection but changes a retained row's launch state; it must reach the later
`HISTORICAL_ROW_CHANGED` gate. The original positive rollover and changed-origin
negative control remain in the same test roster.

Risk: editing an oracle can conceal a product regression. The mitigation is the
unchanged, explicit SPARK reference and postcondition, preserved original
failure, unchanged negative inputs, additional targeted refusal, and an actual
checked-library rerun. This correction is alignment with the existing contract,
not a policy exception or relaxation of a safety/acceptance guarantee. The final
runtime result records whether these controls actually pass; this rationale
alone is not that evidence.
