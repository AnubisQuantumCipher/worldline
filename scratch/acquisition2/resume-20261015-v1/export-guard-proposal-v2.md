# D49 export guard correction — fresh unapplied v2

**UNVERIFIED proposal; no application, candidate import or test execution.** Observed source commit: `9522e894a7ea995103c26ee0ce20ed18a7caaa37`. Target `runtime/worldline/proof_manifest.py` still had SHA256 `b534fa1cb27db5c2c3601a04c7c2693ed012fdc4f940ab4e897cd9ebf852979c` during formation. All v1 source, proposal, review and failure evidence remains retained unchanged.

The v1 complete-normalized-unit claim was too strong: existing `normalized_ada` collapses whitespace inside Ada string literals. Normalized hashes identify that projection only. V2 preserves the normalizer and every original CONTRACT_PINS value, and adds a separate `_TYPED_EXPORT_RAW_UNIT_PINS` map for the same ten selected transport specs/bodies. The formation script reads actual bytes using `read_bytes()` and SHA256. The proposed guard likewise hashes raw bytes directly, before UTF-8 decoding for the existing declaration/literal inventory.

These are deliberately stricter, additive source guards. Comment, layout and literal-whitespace changes all change the raw identity. Every new raw pin needs review of its associated complete source unit; a matching hash is source correspondence, not proof of that unit. No original check, accepted runtime input, proof obligation, contract pin or complete original audit is removed or repinned.

Use these fresh artifacts instead of applying v1:

- `proof_manifest-export-guard-v2.patch` — SHA256 `f13411b880aed9fc91a1a1813fe0aa8eb8778bce72bf6521a859139d23db0bff`.
- `proof_manifest-export-guard-candidate-v2.py` — SHA256 `9d9ac3fc8ad726da3818aa3db09eaa6491f34d04dbd40fae16254e6f8ad78811`.
- `test_typed_export_correspondence_proposal_v2.py` — SHA256 `af7b53695f7b7983fef6b5490d7ad3835e6f22d191d2c3f02865af52d278c150`; proposed destination remains `tests/test_typed_export_correspondence.py`, with the original full audit untouched.
- `form_export_guard_proposal_v2.py` — SHA256 `41c269e62d57698f19d04249aa5449ed7343e998dc57f5be92cb47ff21588bf9`.
- `export-guard-preparation-receipt-v2.json` — SHA256 `f41ab1c9bfc444a759a756eeb1081555e70bf81f4662848adea968690d9d44b0`; contains every raw and normalized pin and its source path.
- `export-guard-static-readback-v2.json` — mechanical AST and actual-byte readback only.

Formation command:

```sh
python3 -B scratch/acquisition2/resume-20261015-v1/form_export_guard_proposal_v2.py
```

The proposed comment control now requires no fake-binding inventory error but requires the raw-spec identity refusal. It then restores the exact original spec bytes and verifies an empty baseline before introducing the separate status-branch body mutation. That body mutation must independently refuse for the raw body, without inheriting the comment refusal.

The new literal control changes the real existing Ada runtime diagnostic literal `"wl_excluded_source_owner_decide_v1: "` in `core/worldline-c_api.adb` to `"wl_excluded_source_owner_decide_v1:  "`. It requires the old normalizer to return equal projections, and then requires exactly the raw-body refusal, with no normalized-projection refusal. This is a proposed source-identity mutation test, not native execution or proof of diagnostic behavior.

**MEASURED source preparation:** AST parsing of the candidate and proposed tests succeeded. AST comparison preserved all existing non-function policy statements and every existing non-export function, including `normalized_ada`. Readback matched each proposed raw pin against the current actual bytes. The existing diagnostic literal was observed once in that source. These operations did not import or execute candidate code.

**UNVERIFIED:** baseline guard success, proposed mutation outcomes, historical legacy positive compatibility, actual linker/ABI behavior, complete typed semantic closures, runtime paths and proof. V2 does not inherit v1's `git apply --check` result; no v2 application/check/test was run. Direct literal inventory still is not an Ada constant-expression or ELF alias resolver. The unchanged whole-source inventory/contract/frame/build/proof gates and original ABI/runtime controls remain required. Independent acceptance remains NOT PERFORMED.
