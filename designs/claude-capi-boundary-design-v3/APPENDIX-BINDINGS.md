# C-API boundary consolidation v3: Appendix A-BIND (binding tables and ordered tokens)

| | |
|---|---|
| Companion to | `DESIGN.md` in this directory (design v3). `§n` means a section of DESIGN.md. |
| Status | DRAFT_FOR_GPT61_REVIEW. **PROPOSAL ONLY.** No manifest code, table, source or control has been written, and none of the checks below has been run. Every obligation is OPEN. |
| Base | S5 = `W/work/claude-composition-v5-beta/source` (lineage L0, §9.1). Line citations are S5 lines; for the files cited they are identical to S4 (§0). |
| Normal form | Every literal below is in the manifest's own normal form, `normalized_ada` (`runtime/worldline/proof_manifest.py:420-433`). It removes `--` comments outside string literals and collapses all layout to single spaces. |
| Answers | RC4 (enforceable binding), RC5 (intermediate tables, append schedule, identity per stage), R2_NINE_CONDITIONS, and the binding half of RC1 (diagnostic confinement). |

Nothing in this appendix is evidence. A token match is a necessary guard, never proof of reachability, faithful actuals beyond the token text, or native behaviour (§8.9).

---

## B0. Rules shared by every table

- **R-ISO (§8.4 O1), isolation.**
  - Subprogram `N` in file `f`:
    - `end N;` must occur exactly once in the normalized text of `f`.
    - The isolated text runs from the nearest `function N ` or `procedure N ` before it, up to and including `end N;`.
    - Otherwise isolation fails and the check reports a problem.
    - This differs from `contract_text` (`proof_manifest.py:437-446`): it accepts a separate declaration earlier in the file, which the body-local transport packages need.
  - Body-local package `N`: the text from the unique `package body N is` to the following `end N;`.
- **R-ORD (§8.4 O2), order.**
  - The tokens of a unit must occur in the isolated text as an ordered subsequence. Each token is searched from the end of the previous token's match.
  - Repeated substrings therefore cannot satisfy the order by an earlier occurrence.
- **R-MUL (§8.4 O3), multiplicity.** Each `Counts` line gives exact occurrence counts within the isolated text.
- **R-W (§8.4 O4), result-to-write.**
  - Every write into foreign memory (`.all :=`, `Write_Data (`) is listed with its exact source expression.
  - The source is a SPARK result object declared `constant` from exactly the listed call, or `Finalization_Decide`'s `O`, which is assigned exactly twice, once on each exclusive path.
  - `Response` in the two completion exports is the `out` actual of exactly one listed call and is not otherwise assigned.
- **R-G (§8.4 O5), gating.**
  - Each acceptance declaration or assignment is followed by its discriminant test and the original refusal statement. Only `begin` may stand between them.
  - That test precedes every selection of a payload component (A1, §3.2 V4).
- **R-Q (§8.4 O6), qualification and renames.**
  - (a) Every call to a routine named in Appendix C is written with its full expanded name.
  - (b) The C_API body declares no package `renames` beyond:
    - the pre-existing ones of S5, with their occurrences unchanged (for example `core/worldline-c_api.adb:93`, `:672-674`, `:761-762`, `:836`, `:879-881`, `:1024-1027`);
    - inside each transport package or moved subprogram, exactly the renames that the original unit declares at the corresponding place. These are listed per unit below.
  - (c) The only non-`use type` use clause in an export body is one `use <Unit>_Transport;`.
  - (d) A transport package may declare subtypes that denote the original unit's types under their original simple names, for example `subtype Request is Evaluation_Pending_C.Request;`, so that copied helper text stays textual.
- **Spacing.** Tokens assume the GNAT layout these files already use: a space before each opening parenthesis of a call, aggregate or index, spaces around `=>` and `:=`, and no space before `;`. A successor that is laid out differently fails the check. That outcome is intended, and the remedy is reformatting, not a weaker table.
- **Name resolution.** Use-visibility conflicts inside the integrated C_API body cannot be checked until source exists, and they are OPEN. Resolving one, for example by qualifying a helper call, changes a literal token only through a reviewed table change in a new packet. A table is never edited silently to match the source.

---

## B1. Stage table (RC5)

Exactly one packet is applied per stage (§9.1). In the "C_API `External_Name`" column, 31 is observed and every later figure is JACKAL exact (Appendix A of DESIGN.md).

| Stage | Exports relocated in this stage | Cumulative movers / C_API `External_Name` | Predecessor edit (B5) | Tables changed | Units bound in B4 from this stage | `CONTRACT_PINS` regenerated |
|---|---|---|---|---|---|---|
| PK-0 | none | 0 / 31 | none | none (no manifest change) | none | none (controls bound through I5 only) |
| PK-1 | `wl_resources_can_reserve`, `wl_recovery_select` | 2 / 33 | none | Defines every table and the override (B8). `CAPI_CORE_HOME` lists all 91 closure symbols, 2 of them relocated. | B4.1, B4.2 | C_API pair, U1 pair, U2 pair |
| PK-2 | `wl_recovery_authorization_decide_v2`, `wl_recovery_authorization_decide_v3`, `wl_recovery_protocol_decide_v1` | 5 / 36 | E1, E2 | `.update` for the 3 symbols | B4.3, B4.4, B4.5 | C_API pair, U3, U4, U5 pairs |
| PK-2R | none | 5 / 36 | none | none | none | the U3, U4, U5 specs and recovery wire specs it repairs |
| PK-3 | `wl_reservation_lifecycle_plan`, `wl_resource_ledger_compute`, `wl_resource_ledger_headroom`, `wl_resource_policy_admit` | 9 / 40 | none | `.update` for the 4 symbols | B4.6, B4.7, B4.8, B4.9 | C_API pair, U6, U7, U8 pairs |
| PK-3R | none | 9 / 40 | none | none | none | U6, U7, U8 specs it repairs |
| PK-4 | `wl_evaluation_history_select` | 10 / 41 | none | `.update` for 1 symbol | B4.10 | C_API pair, U9 pair |
| PK-4R | none | 10 / 41 | none | none | none | U9 spec it repairs |
| PK-5 | `wl_resource_run_ledger_check_v1`, `wl_chain_authority_replay_v1` | 12 / 43 | E3 | `.update` for 2 symbols | B4.12, B4.13 | C_API pair, U12, U13 pairs |
| PK-5R | none | 12 / 43 | none | none | none | U12, U13 specs and wire specs it repairs |
| PK-6a | none (value routines only, §9.5) | 12 / 43 | none | REQUIRED_PROVED append (57 names) | none | completion pair, finalization pair |
| PK-6b | `wl_completion_decide_v1`, `wl_completion_raw_decide_v1`, `wl_completion_metadata_matches_v1`, `wl_native_diagnostic_control_v1`, `wl_finalization_decide_v1`, `wl_collapse_decide_finalization_v1` | 18 / 49 | E4 | `.update` for 6 symbols. `CAPI_DIAGNOSTIC_SITES` defined (B6); D1–D5 enabled. | B4.14–B4.24 | C_API pair, completion pair, finalization pair |
| PK-6R | none | 18 / 49 | none | none | none | U14, U15 specs and wire specs it repairs |
| PK-7 (after operator D-13) | `wl_pending_decide_v1`, `wl_pending_decide_v2` | 20 / 51 | none | `.update` for 2 core symbols; `CAPI_COMPONENT_HOME` and `CAPI_COMPONENT_INTERFACE` per D-13 (B2.3) | B4.11 | C_API pair, U10, U11 pairs; new component keys (I3, B7) |
| PK-7R | none | 20 / 51 | none | none | none | U10, U11 specs and component specs it repairs |
| PK-S | none | 20 / 51 | none | none (seal limits, §9.8) | none | none (records only that re-pin equals the stage pins) |

At every stage the effective tables are complete for the whole closure. A relocated symbol's home is `core/worldline-c_api.ads`, and every other symbol keeps its S5 home. The final override is never disabled, and an earlier table entry is never removed or reordered. A later packet only appends `.update({...})` lines.

---

## B2. Home tables

### B2.1 `CAPI_CORE_HOME` at L0 (91 symbols, observed)

Observed over the 137 core Ada files (`DECLARED_CORE_ADA_SOURCES`): 91 `Export` tokens, 91 `External_Name =>` tokens, 91 `"wl_…"` literals, 0 `Import` tokens.

| Home at L0 | Symbols that stay | Symbols that move to `core/worldline-c_api.ads` (stage) |
|---|---|---|
| `core/worldline-c_api.ads` | `wl_hash_file`, `wl_hash_bytes`, `wl_world_id`, `wl_causal_link`, `wl_receipt_link`, `wl_transition_allowed`, `wl_transaction_transition_allowed`, `wl_collapse_decide`, `wl_evaluation_classify`, `wl_evaluation_admissible`, `wl_evaluation_transition_allowed`, `wl_evaluation_advance`, `wl_evaluation_roster_complete`, `wl_abi_version`, `wl_layout_size`, `wl_layout_offset`, `wl_evaluation_wire_version`, `wl_evaluation_wire_layout`, `wl_evaluation_wire_classify`, `wl_evaluation_wire_admit`, `wl_evaluation_wire_report`, `wl_collapse_raw_dependencies_v1`, `wl_collapse_decide_raw_evaluation_v1`, `wl_collapse_decide_raw_evaluation_v2`, `wl_collapse_decide_raw_evaluation_v3`, `wl_owner_transition_version_v1`, `wl_owner_transition_layout_v1`, `wl_owner_transition_authorize_v1`, `wl_owner_audit_version_v1`, `wl_owner_audit_layout_v1`, `wl_owner_audit_decide_v1` | — |
| `core/worldline-resources_c_api.ads` | `wl_resources_abi_version` | `wl_resources_can_reserve` (PK-1) |
| `core/worldline-recovery_c_api.ads` | `wl_recovery_abi_version` | `wl_recovery_select` (PK-1) |
| `core/worldline-recovery_authorization_c_api.ads` | `wl_recovery_authorization_version_v2`, `wl_recovery_authorization_layout_v2` | `wl_recovery_authorization_decide_v2` (PK-2) |
| `core/worldline-recovery_authorization_v3_c_api.ads` | `wl_recovery_authorization_version_v3`, `wl_recovery_authorization_layout_v3` | `wl_recovery_authorization_decide_v3` (PK-2) |
| `core/worldline-recovery_protocol_c_api.ads` | `wl_recovery_protocol_version_v1`, `wl_recovery_protocol_layout_v1` | `wl_recovery_protocol_decide_v1` (PK-2) |
| `core/worldline-reservation_lifecycle_c_api.ads` | `wl_reservation_lifecycle_abi_version`, `wl_reservation_lifecycle_row_size`, `wl_reservation_lifecycle_row_offset` | `wl_reservation_lifecycle_plan` (PK-3) |
| `core/worldline-resource_ledger_c_api.ads` | `wl_resource_ledger_abi_version`, `wl_resource_ledger_layout_size`, `wl_resource_ledger_layout_offset` | `wl_resource_ledger_compute`, `wl_resource_ledger_headroom` (PK-3) |
| `core/worldline-resource_policy_c_api.ads` | `wl_resource_policy_abi_version`, `wl_resource_policy_layout_size`, `wl_resource_policy_layout_offset` | `wl_resource_policy_admit` (PK-3) |
| `core/worldline-evaluation_history_c_api.ads` | `wl_evaluation_history_abi_version`, `wl_evaluation_history_layout_size`, `wl_evaluation_history_layout_offset` | `wl_evaluation_history_select` (PK-4) |
| `core/resource_run_ledger_c_api.ads` | `wl_resource_run_ledger_version_v1`, `wl_resource_run_ledger_layout_v1` | `wl_resource_run_ledger_check_v1` (PK-5) |
| `core/worldline-chain_authority_c_api.ads` | `wl_chain_authority_version_v1`, `wl_chain_authority_layout_v1` | `wl_chain_authority_replay_v1` (PK-5) |
| `core/evaluation_completion_c.ads` | `wl_completion_abi_version_v1`, `wl_completion_layout_size_v1`, `wl_completion_layout_alignment_v1`, `wl_completion_layout_offset_v1`, `wl_completion_context_layout_v1`, `wl_completion_metadata_layout_v1` | `wl_native_diagnostic_control_v1`, `wl_completion_decide_v1`, `wl_completion_raw_decide_v1`, `wl_completion_metadata_matches_v1` (PK-6b) |
| `core/evaluation_finalization_c.ads` | `wl_finalization_version_v1`, `wl_finalization_layout_v1` | `wl_finalization_decide_v1`, `wl_collapse_decide_finalization_v1` (PK-6b) |
| `core/evaluation_pending_c.ads` | `wl_pending_abi_version_v1`, `wl_pending_layout_size_v1`, `wl_pending_layout_alignment_v1`, `wl_pending_layout_offset_v1` | `wl_pending_decide_v1` (PK-7) |
| `core/evaluation_pending_v2_c.ads` | `wl_pending_abi_version_v2`, `wl_pending_layout_size_v2`, `wl_pending_layout_alignment_v2`, `wl_pending_layout_offset_v2` | `wl_pending_decide_v2` (PK-7) |

### B2.2 Per-stage `.update` lines (literal form)

```python
CAPI_CORE_HOME.update({'wl_resources_can_reserve': 'core/worldline-c_api.ads', 'wl_recovery_select': 'core/worldline-c_api.ads'})  # PK-1 (inside the definition)
CAPI_CORE_HOME.update({'wl_recovery_authorization_decide_v2': 'core/worldline-c_api.ads', 'wl_recovery_authorization_decide_v3': 'core/worldline-c_api.ads', 'wl_recovery_protocol_decide_v1': 'core/worldline-c_api.ads'})  # PK-2
CAPI_CORE_HOME.update({'wl_reservation_lifecycle_plan': 'core/worldline-c_api.ads', 'wl_resource_ledger_compute': 'core/worldline-c_api.ads', 'wl_resource_ledger_headroom': 'core/worldline-c_api.ads', 'wl_resource_policy_admit': 'core/worldline-c_api.ads'})  # PK-3
CAPI_CORE_HOME.update({'wl_evaluation_history_select': 'core/worldline-c_api.ads'})  # PK-4
CAPI_CORE_HOME.update({'wl_resource_run_ledger_check_v1': 'core/worldline-c_api.ads', 'wl_chain_authority_replay_v1': 'core/worldline-c_api.ads'})  # PK-5
CAPI_CORE_HOME.update({'wl_completion_decide_v1': 'core/worldline-c_api.ads', 'wl_completion_raw_decide_v1': 'core/worldline-c_api.ads', 'wl_completion_metadata_matches_v1': 'core/worldline-c_api.ads', 'wl_native_diagnostic_control_v1': 'core/worldline-c_api.ads', 'wl_finalization_decide_v1': 'core/worldline-c_api.ads', 'wl_collapse_decide_finalization_v1': 'core/worldline-c_api.ads'})  # PK-6b
CAPI_CORE_HOME.update({'wl_pending_decide_v1': 'core/worldline-c_api.ads', 'wl_pending_decide_v2': 'core/worldline-c_api.ads'})  # PK-7
```

Each stage's `CAPI_DECLARATIONS.update` adds the B3 successor declarations of exactly its symbols. Its `CAPI_ORDERED`/`CAPI_COUNTS` `.update` adds exactly its B4 units.

### B2.3 `CAPI_COMPONENT_HOME` and `CAPI_COMPONENT_INTERFACE`

Observed at L0:
- The component has 14 Ada files under `pending-component/core/`.
- 10 symbols, 5 in each C spec, each preceded by `External_Name => `.
- `pending-component/pending.gpr` has `Library_Interface` = `("evaluation_pending", "evaluation_pending_c", "evaluation_pending_v2", "evaluation_pending_v2_c", "evaluation_epoch", "resource_quantities", "spark", "spark.big_integers")`, with switches `-gnat2022 -gnata -gnatVa -gnatwa -g -O0`.

| Symbol | Home at L0 | Home after PK-7 under D-13 option (i) (§16.1; proposal) |
|---|---|---|
| `wl_pending_abi_version_v1`, `wl_pending_layout_size_v1`, `wl_pending_layout_alignment_v1`, `wl_pending_layout_offset_v1` | `pending-component/core/evaluation_pending_c.ads` | unchanged |
| `wl_pending_decide_v1` | `pending-component/core/evaluation_pending_c.ads` | `pending-component/core/evaluation_pending_transport.ads` |
| `wl_pending_abi_version_v2`, `wl_pending_layout_size_v2`, `wl_pending_layout_alignment_v2`, `wl_pending_layout_offset_v2` | `pending-component/core/evaluation_pending_v2_c.ads` | unchanged |
| `wl_pending_decide_v2` | `pending-component/core/evaluation_pending_v2_c.ads` | `pending-component/core/evaluation_pending_transport.ads` |

`CAPI_COMPONENT_INTERFACE` is the 8 L0 units above. Under option (i), PK-7 adds `"evaluation_pending_transport"`. No original entry is removed (K3). Options (ii) and (iii) are inadmissible (§16.1), so no table exists for them.

---

## B3. Relocated declarations (exact; P1)

The **Original** column gives the S5 normalized declaration from `function <old> ` to `External_Name => "<symbol>";`. That span was extracted by a read-only script that reimplemented `normalized_ada` without importing any WORLDLINE module. The **Successor** column is the same text with only the identifier replaced. `CAPI_DECLARATIONS[symbol]` is the successor text, which must occur exactly once in normalized `core/worldline-c_api.ads`, while the symbol must occur zero times in its old spec (G6).

| # | Symbol (stage) | Original file, identifier, sha256 of original text | Successor identifier, sha256 of successor text |
|---|---|---|---|
| 1 | `wl_resources_can_reserve` (PK-1) | `core/worldline-resources_c_api.ads`, `Can_Reserve`, `761a7c70159087f9228a14f843d8edc055d9e6ed5ed220397eab700cc490cdbb` | `Resources_Can_Reserve`, `65d9b861141b233af68fc167fe1497cf21568e437c27721e3675af4ee3675936` |
| 2 | `wl_recovery_select` (PK-1) | `core/worldline-recovery_c_api.ads`, `Select_Action`, `988c15a573320c11ab6e9a393a3da7bb02586e384b86702b81e1a82e59a12471` | `Recovery_Select`, `a1c63a2b04a28da4e920af7a2c11d82396a431a0660e0ca5b4c89112ac4a2ffc` |
| 3 | `wl_recovery_authorization_decide_v2` (PK-2) | `core/worldline-recovery_authorization_c_api.ads`, `Decide`, `704c77637a52b387cd75cd957a6b1b55d56019cb727534b94d6333df90d15af2` | `Recovery_Authorization_Decide_V2`, `8b2c82bbf3facccd9f7ee313858633f624592f81ecba073b86584731b94992fa` |
| 4 | `wl_recovery_authorization_decide_v3` (PK-2) | `core/worldline-recovery_authorization_v3_c_api.ads`, `Decide`, `03d0494051074ebaff9c4db2a5fd08118797dce90212d2dbdaba1dcdf06e244a` | `Recovery_Authorization_Decide_V3`, `4c32c093ce4611b2d81b3b58ce2e65c7882bd0b745a0ff04bfad86ba33348e3a` |
| 5 | `wl_recovery_protocol_decide_v1` (PK-2) | `core/worldline-recovery_protocol_c_api.ads`, `Decide`, `cfd44d57ff5aba0995503e73875fe4be0348ebf5c32b3295099980d5a0df0cb6` | `Recovery_Protocol_Decide_V1`, `32257ea85c221b59587bc114eab11b4ec816181d21932abd7608ccf3d6a95aec` |
| 6 | `wl_reservation_lifecycle_plan` (PK-3) | `core/worldline-reservation_lifecycle_c_api.ads`, `Plan`, `6497503f0494300417d7a1e2fc8afd634117a5dfdc36b6f71d4e1f2d91a916e4` | `Reservation_Lifecycle_Plan`, `0589d8b8f42d419ac400edf7a890804a7246863b758d5bf765f346a21bcbccd0` |
| 7 | `wl_resource_ledger_compute` (PK-3) | `core/worldline-resource_ledger_c_api.ads`, `Compute`, `6bb6d3a8b88d85d6442a0de425e055baca3b906cc1aee62844877685d789bd37` | `Resource_Ledger_Compute`, `eba57b58f9b90422a00c185aed7f3a1bf853da126182d43ae12f8a1a7c0729eb` |
| 8 | `wl_resource_ledger_headroom` (PK-3) | `core/worldline-resource_ledger_c_api.ads`, `Headroom`, `ffcc6dd9ba035d37f480411e799cde8255481bcb0acaf81f74473e26f1716619` | `Resource_Ledger_Headroom`, `7c066a1314d62cb59fe8b9f36e6f1555d2661ff1e706875ba1aeb4b75cc57470` |
| 9 | `wl_resource_policy_admit` (PK-3) | `core/worldline-resource_policy_c_api.ads`, `Admit`, `fa5dcd37d081f3dcd56f32edaec2f12cf6e47237547e12bdc7160f00c32b7699` | `Resource_Policy_Admit`, `2e6c8b4ec45b9e7a05ff5b3d89743c9765c4bdff0c7659fbb3df9ae2deadb314` |
| 10 | `wl_evaluation_history_select` (PK-4) | `core/worldline-evaluation_history_c_api.ads`, `Select_Evidence`, `f7b69dc152ed180aed8713064432a6a0f7cff2610dd1b4734a66bdd8b892c7b5` | `Evaluation_History_Select`, `7dd65cab5d4d8c46a22803771ca9796d41bd13a6887d0cd0eebbc62c7a61eb85` |
| 11 | `wl_resource_run_ledger_check_v1` (PK-5) | `core/resource_run_ledger_c_api.ads`, `Check`, `da2d307ccd3ce10c13683caa5a7a7bcdc6f93bfb973e7b209aab30d24736c746` | `Run_Ledger_Check`, `31a87eb960174130db8155f88687b357df5cf636c22de21f669de67d092836db` |
| 12 | `wl_chain_authority_replay_v1` (PK-5) | `core/worldline-chain_authority_c_api.ads`, `Replay`, `9f1d04c4681fe7d76148f32543b34fd8122926b87a53fdab8c8290168e2f6275` | `Chain_Replay`, `bb24be87f17871cc6946d1aff018875d218bb008ad4e71943fd054bb937c2047` |
| 13 | `wl_completion_decide_v1` (PK-6b) | `core/evaluation_completion_c.ads`, `Decide`, `20a88b0f1ca98f4c0d8ddf5df2b6f29bfd1b3f3221b989835e8ed9e1e600bebc` | `Completion_Decide`, `633b5e10cefa3a2730223dbed01081d9dc22ab8a7577920e19ae4da2bc923135` |
| 14 | `wl_completion_raw_decide_v1` (PK-6b) | `core/evaluation_completion_c.ads`, `Raw_Decide`, `15bfe93d566a2145164c221b0a6e491af2aa2b38acad02bc80f3d852055dfdc3` | `Completion_Raw_Decide`, `f953c68e4ca2b1dd31e5f4660d966a29702dc211245d770ccfb5b74d6255e594` |
| 15 | `wl_completion_metadata_matches_v1` (PK-6b) | `core/evaluation_completion_c.ads`, `Metadata_Matches`, `5d35ca057cd49546791e10c70de11a6d1b682a5c378ecfad78eaeff7a842ee93` | `Completion_Metadata_Matches`, `af3087fd991fb5b8664260497c732829beaa2b4c35371c06b98823e7020fac3f` |
| 16 | `wl_native_diagnostic_control_v1` (PK-6b) | `core/evaluation_completion_c.ads`, `Diagnostic_Control`, `38c8fec72ac32fed3bab9d9af0fcde544db5748bdd2a1c920564658bcbbbe511` | `Native_Diagnostic_Control`, `be2802255d649baba0a0956f3960bf9b022646d9db19feb97ba0725d40185524` |
| 17 | `wl_finalization_decide_v1` (PK-6b) | `core/evaluation_finalization_c.ads`, `Decide`, `ad24b6a8d75928c7e1fd08142c8acb30525630b7be13ba5bbc470f6ce40d8a0f` | `Finalization_Decide`, `926da24505ec1b14b63e2e01176ac36144242151cbc3d27f9075277cf525e97e` |
| 18 | `wl_collapse_decide_finalization_v1` (PK-6b) | `core/evaluation_finalization_c.ads`, `Decide_Mixed`, `fc1ea3df6ad5ca8ead51a9ddb6b173b5c41e8a167c994da89ef5cb7258f5f2e0` | `Finalization_Decide_Mixed`, `cd470941b2cda2ef68f74c3de6d3bdd8cd81c36794ed18f579d8be6c34814693` |
| 19 | `wl_pending_decide_v1` (PK-7) | `core/evaluation_pending_c.ads`, `Decide`, `1342b938e6ce1a9ef8b2f4c6364391681ef31c2ecc3a71a53f1dbf286f96b570` | `Pending_Decide_V1`, `deff63d3aab3015da305c8a53c2c8969e07f43e360d9b752ece03a1d8723bef1` |
| 20 | `wl_pending_decide_v2` (PK-7) | `core/evaluation_pending_v2_c.ads`, `Decide`, `dfe6ce06f81381cf5583f58c7812d16f7bc64623202e725433384e7cd8a67cd6` | `Pending_Decide_V2`, `32e00118ed4dab033466ebada78bf52e3f06c6a7b7f7ddab8c71e60e1cbf5a59` |

Successor texts. Each is the literal value of `CAPI_DECLARATIONS[symbol]`, and each original is identical except for the identifier shown in the table above.

```text
1  function Resources_Can_Reserve (Available_Negative : Interfaces.Unsigned_8; Available : System.Address; Available_Length : Interfaces.C.size_t; Withheld : System.Address; Withheld_Length : Interfaces.C.size_t; Floor : System.Address; Floor_Length : Interfaces.C.size_t; Requested : System.Address; Requested_Length : Interfaces.C.size_t) return Interfaces.Unsigned_8 with Export, Convention => C, External_Name => "wl_resources_can_reserve";
2  function Recovery_Select (Expected : System.Address; Expected_Length : Interfaces.C.size_t; Live_Present : Interfaces.Unsigned_8; Live : System.Address; Live_Length : Interfaces.C.size_t; Prepared_Present : Interfaces.Unsigned_8; Prepared : System.Address; Prepared_Length : Interfaces.C.size_t) return Interfaces.Unsigned_8 with Export, Convention => C, External_Name => "wl_recovery_select";
3  function Recovery_Authorization_Decide_V2 (Input : System.Address; Input_Length : Interfaces.C.size_t; Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_recovery_authorization_decide_v2";
4  function Recovery_Authorization_Decide_V3 (Input : System.Address; Input_Length : Interfaces.C.size_t; Arena : System.Address; Arena_Length : Interfaces.C.size_t; Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_recovery_authorization_decide_v3";
5  function Recovery_Protocol_Decide_V1 (Input : System.Address; Input_Length : Interfaces.C.size_t; Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_recovery_protocol_decide_v1";
6  function Reservation_Lifecycle_Plan (Data : System.Address; Data_Length : Size; Rows : System.Address; Row_Count : Size; Mode, Present : U8; Requested_First, Requested_Length : Size; Removed : System.Address; Removed_Length : Size) return U8 with Export, Convention => C, External_Name => "wl_reservation_lifecycle_plan";
7  function Resource_Ledger_Compute (Data : System.Address; Data_Length : Size; Rows : System.Address; Row_Count : Size; Detail_Data : System.Address; Detail_Length : Size; Total_Data : System.Address; Total_Length : Size; Details : System.Address; Result : System.Address) return U8 with Export, Convention => C, External_Name => "wl_resource_ledger_compute";
8  function Resource_Ledger_Headroom (Data : System.Address; Data_Length : Size; Available, Withheld, Floor : System.Address; Output : System.Address; Output_Length : Size; Result : System.Address) return U8 with Export, Convention => C, External_Name => "wl_resource_ledger_headroom";
9  function Resource_Policy_Admit (Data : System.Address; Data_Length : Size; Input : System.Address; Disks : System.Address; Disk_Count : Size; Result : System.Address) return U8 with Export, Convention => C, External_Name => "wl_resource_policy_admit";
10 function Evaluation_History_Select (Data : System.Address; Data_Length : Size; Rows : System.Address; Row_Count : Size; Final_Present : U8; Final_Row, Query, Output : System.Address) return U8 with Export, Convention => C, External_Name => "wl_evaluation_history_select";
11 function Run_Ledger_Check (Input : System.Address; Input_Length : Interfaces.C.size_t; Arena : System.Address; Arena_Length : Interfaces.C.size_t; Before_Rows : System.Address; Before_Count : Interfaces.C.size_t; Proposed_Rows : System.Address; Proposed_Count : Interfaces.C.size_t; Native : System.Address; Native_Count : Interfaces.C.size_t; Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_resource_run_ledger_check_v1";
12 function Chain_Replay (Anchors : System.Address; Anchors_Length : Interfaces.C.size_t; Rows : System.Address; Rows_Count, Rows_Length : Interfaces.C.size_t; Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_chain_authority_replay_v1";
13 function Completion_Decide (Input, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_completion_decide_v1";
14 function Completion_Raw_Decide (Input, Raw_Rows, Confinements, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_completion_raw_decide_v1";
15 function Completion_Metadata_Matches (Input, Context : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_completion_metadata_matches_v1";
16 function Native_Diagnostic_Control (Enable : U32) return U32 with Export, Convention => C, External_Name => "wl_native_diagnostic_control_v1";
17 function Finalization_Decide (Input, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_finalization_decide_v1";
18 function Finalization_Decide_Mixed (Collapse : System.Address; Primary_Kind : U32; Primary, Primary_Raw, Primary_Confinement, Primary_Context : System.Address; Staged_Kind : U32; Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address; Agent_Confinement : U8) return U8 with Export, Convention => C, External_Name => "wl_collapse_decide_finalization_v1";
19 function Pending_Decide_V1 (Input, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_pending_decide_v1";
20 function Pending_Decide_V2 (Input, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_pending_decide_v2";
```

**Subtype resolution (P2).**
- The originals of 6–10 use their unit's `Size`, `U8` and `U32`, and 16 and 18 use `U32` and `U8`.
- The successors resolve those names to the four `Worldline.C_API` subtypes (§3.6), which denote the same first subtypes: `Interfaces.C.size_t`, `Interfaces.Unsigned_8` and `Interfaces.Unsigned_32`.
- Observed today: `core/worldline-c_api.ads` declares no `U8`, `U32`, `I64` or `Size`. It does declare `subtype Byte is Interfaces.Unsigned_8;` (`:185`). The body uses `Size` only as the attribute `'Size` (`core/worldline-c_api.adb:550-555`) and refers to `K.U32` inside `Authority_Glue` (`:764`).
- Matching resolution in compiled code, and the native ABI, are OPEN (D-15, D-34).

---

## B4. Ordered tokens per isolated unit (`CAPI_ORDERED`, `CAPI_COUNTS`)

Isolated units are all in `core/worldline-c_api.adb` unless stated. Tokens are numbered in required order (R-ORD). "Renames" lists what the unit's transport package must replicate (R-Q b).

### B4.1 `Resources_Can_Reserve` (U1, PK-1)

Transport package `Resources_Transport`:
- holds `As_Byte`, `Valid` and `Decode`, copied from `core/worldline-resources_c_api.adb:13-35`;
- has no renames;
- needs `use System.Storage_Elements;` and `use type` clauses as in `:7-10`.

1. `use Resources_Transport;`
2. `if not Worldline.Resources_C_API.Negative_Flag_Valid (Available_Negative) or else not Valid (Available, Available_Length) or else not Valid (Withheld, Withheld_Length) or else not Valid (Floor, Floor_Length) or else not Valid (Requested, Requested_Length) then return 255; end if;`
3. `return Worldline.Resources_C_API.Can_Reserve_Value (Available_Negative, Decode (Available, Available_Length), Decode (Withheld, Withheld_Length), Decode (Floor, Floor_Length), Decode (Requested, Requested_Length));`
4. `exception when others => return 255; end Resources_Can_Reserve;`

Counts: `.all :=` 0; `Worldline.Resources_C_API.Can_Reserve_Value (` 1. Writes: none.

### B4.2 `Recovery_Select` (U2, PK-1)

Transport package `Recovery_Transport`:
- holds `As_Byte`, `Shape` and `Copy`, copied from `core/worldline-recovery_c_api.adb:14-35`, and the new constant `Empty : constant Worldline.Recovery.Identity_Bytes (1 .. 0) := (others => 0);`;
- renames `package R renames Worldline.Recovery;`.

The original `Marker` (`:37-51`) is not copied. Its decision logic is `Marker_Of` in SPARK.

1. `use Recovery_Transport;`
2. `if not Worldline.Recovery_C_API.Presence_Valid (Live_Present, Prepared_Present) or else not Shape (Expected, Expected_Length) or else (Worldline.Recovery_C_API.Present (Live_Present) and then not Shape (Live, Live_Length)) or else (Worldline.Recovery_C_API.Present (Prepared_Present) and then not Shape (Prepared, Prepared_Length)) then return 255; end if;`
3. `Expected_Value : constant Worldline.Recovery.Identity_Bytes := Copy (Expected, Expected_Length);`
4. `Live_Value : constant Worldline.Recovery.Identity_Bytes := (if Worldline.Recovery_C_API.Present (Live_Present) then Copy (Live, Live_Length) else Empty);`
5. `Prepared_Value : constant Worldline.Recovery.Identity_Bytes := (if Worldline.Recovery_C_API.Present (Prepared_Present) then Copy (Prepared, Prepared_Length) else Empty);`
6. `return Worldline.Recovery_C_API.Select_Value (Expected_Value, Live_Present, Live_Value, Prepared_Present, Prepared_Value);`
7. `exception when others => return 255; end Recovery_Select;`

Counts: `.all :=` 0; `Copy (` 3. Writes: none.

### B4.3 `Recovery_Authorization_Decide_V2` (U3, PK-2)

Transport package `Recovery_Authorization_Transport`:
- holds `Request_At`, `Result_At` and `Shape`, copied from `core/worldline-recovery_authorization_c_api.adb:14-121`;
- renames `package W renames Worldline.Recovery_Authorization_Wire;`.

1. `use Recovery_Authorization_Transport;`
2. `if Input_Length /= W.Raw_Request'Size / System.Storage_Unit or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit or else not Shape (Input, Input_Length) or else not Shape (Output, Output_Length) or else To_Integer (Input) mod W.Raw_Request'Alignment /= 0 or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;`. This is verbatim from `:129-137`.
3. `Raw : constant W.Raw_Request := Request_At (Input).all;` (`:139`)
4. `if not W.Well_Formed (Raw) then return -1; end if;` (`:141-143`)
5. `Owned : constant W.Raw_Result := Worldline.Recovery_Authorization_C_API.Decide_Total (Raw);`. It is declared in a nested block after token 4, so `Decide_Total` is never evaluated before the original check.
6. `Result_At (Output).all := Owned;`
7. `return 0;`
8. `exception when others => return -1; end Recovery_Authorization_Decide_V2;`

Counts: `.all :=` 1; `W.Well_Formed (Raw)` 1; `Decide_Total (` 1. Write: `Result_At (Output).all := Owned;`.

### B4.4 `Recovery_Authorization_Decide_V3` (U4, PK-2)

Transport package `Recovery_Authorization_V3_Transport`:
- holds `Byte_At`, `Request_At`, `Result_At` and `Shape`, copied from `core/worldline-recovery_authorization_v3_c_api.adb:16-130`;
- renames `package W renames Worldline.Recovery_Authorization_V3_Wire;` and `package Q renames Resource_Quantities;`.

1. `use Recovery_Authorization_V3_Transport;`
2. `if Input_Length /= W.Raw_Request'Size / System.Storage_Unit or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit or else not Shape (Input, Input_Length) or else not Shape (Output, Output_Length) or else Arena_Length > Interfaces.C.size_t (Q.Byte_Count'Last) or else (Arena_Length > 0 and then not Shape (Arena, Arena_Length)) or else To_Integer (Input) mod W.Raw_Request'Alignment /= 0 or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;`. This is verbatim from `:139-149`.
3. `Raw : constant W.Raw_Request := Request_At (Input).all;` (`:151`)
4. `Data : Q.Byte_Array (1 .. Q.Byte_Count (Arena_Length));` (`:152`)
5. `for Position in Data'Range loop Data (Position) := Byte_At (Arena + Storage_Offset (Position - 1)).all; end loop;` (`:154-157`)
6. `if not W.Well_Formed (Data, Raw) then return -1; end if;` (`:158-160`)
7. `Owned : constant W.Raw_Result := Worldline.Recovery_Authorization_V3_C_API.Decide_Total (Data, Raw);`, in a nested block after token 6.
8. `Result_At (Output).all := Owned;`
9. `return 0;`
10. `exception when others => return -1; end Recovery_Authorization_Decide_V3;`

Counts: `.all :=` 1; `W.Well_Formed (Data, Raw)` 1; `Decide_Total (` 1.

### B4.5 `Recovery_Protocol_Decide_V1` (U5, PK-2)

Transport package `Recovery_Protocol_Transport`:
- holds `Request_At`, `Result_At` and `Shape`, copied from `core/worldline-recovery_protocol_c_api.adb:14-43`;
- renames `package W renames Worldline.Recovery_Protocol_Wire;`.

1. `use Recovery_Protocol_Transport;`
2. `if Input_Length /= W.Raw_Request'Size / System.Storage_Unit or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit or else not Shape (Input, Input_Length) or else not Shape (Output, Output_Length) or else To_Integer (Input) mod W.Raw_Request'Alignment /= 0 or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;` (`:49-56`)
3. `Raw : constant W.Raw_Request := Request_At (Input).all;`
4. `Owned_Result : W.Raw_Result := (After => 0);`
5. `Worldline.Recovery_Protocol_ABI.Apply (Raw, Owned_Result, Status);`
6. `if Status /= Worldline.Recovery_Protocol_ABI.Success then return Status; end if;`
7. `Result_At (Output).all := Owned_Result;`
8. `return 0;`
9. `exception when others => return -1; end Recovery_Protocol_Decide_V1;`

Counts: `.all :=` 1; `Apply (` 1.

### B4.6 `Reservation_Lifecycle_Plan` (U6, PK-3)

Transport package `Lifecycle_Transport`:
- holds `As_Byte`, `As_Row`, `Extent_Valid` and `Copy_Data`, copied from `core/worldline-reservation_lifecycle_c_api.adb:14-52`;
- declares `subtype Row_C is Worldline.Reservation_Lifecycle_C_API.Row_C;`;
- renames `package L renames Resource_Reservation_Lifecycle;` and `package R renames Worldline.Resources;`.

1. `use Lifecycle_Transport;`
2. `Row_Size : constant Size := Worldline.Reservation_Lifecycle_C_API.Layout_Size;`
3. `if Data_Length > Size (R.Byte_Count'Last) or else Row_Count > Size (R.Byte_Count'Last) or else Removed_Length > Size (R.Byte_Count'Last) or else Row_Count > Size (Storage_Offset'Last) / Row_Size or else not Worldline.Reservation_Lifecycle_C_API.Request_Valid (Present, Requested_First, Requested_Length) or else not Extent_Valid (Data, Data_Length) or else not Extent_Valid (Rows, Row_Count * Row_Size, Row_C'Alignment) or else not Extent_Valid (Removed, Removed_Length) then return 255; end if;`
4. `Arena : constant R.Byte_Array := Copy_Data (Data, Data_Length);`
5. `Typed_Rows : L.Entry_Array (1 .. R.Byte_Count (Row_Count));`
6. `Mask : L.Removal_Array (1 .. R.Byte_Count (Removed_Length)) := (others => False);`
7. `Requested : constant L.Optional_Identity := Worldline.Reservation_Lifecycle_C_API.Requested_Of (Present, Requested_First, Requested_Length);`
8. `Selected_Mode : constant L.Operation := Worldline.Reservation_Lifecycle_C_API.Operation_Of (Mode);`
9. `Row : constant Row_C := As_Row (Rows + Storage_Offset (Size (I - 1) * Row_Size)).all;`
10. `D : constant Worldline.Reservation_Lifecycle_C_API.Row_Acceptance := Worldline.Reservation_Lifecycle_C_API.Accept_Row (Row);`
11. `if not D.Ok then return 255; end if;`
12. `Typed_Rows (I) := D.Item;`
13. `L.Plan (Arena, Typed_Rows, Requested, Selected_Mode, Mask, Status);`
14. `if Worldline.Reservation_Lifecycle_C_API.Publishes_Mask (Status) then for I in Mask'Range loop As_Byte (Removed + Storage_Offset (I - 1)).all := Worldline.Reservation_Lifecycle_C_API.Mask_Byte (Mask (I)); end loop; end if;`
15. `return Worldline.Reservation_Lifecycle_C_API.Status_Code (Status);`
16. `exception when others => return 255; end Reservation_Lifecycle_Plan;`

Counts: `.all :=` 1 (inside the mask loop); `L.Plan (` 1. Write: the mask byte from `Mask_Byte (Mask (I))` only, under `Publishes_Mask (Status)`.

### B4.7 `Resource_Ledger_Compute` (U7, PK-3)

Transport package `Ledger_Transport`:
- holds `As_Byte`, `As_Row`, `As_Quantity`, `As_Result`, `Extent_Valid`, `Copy_Data` and `Write_Data`, copied from `core/worldline-resource_ledger_c_api.adb:14-106`. The body-local `Shape`, `Decode` and `Encode` (`:74-88`) move to SPARK and are not copied.
- declares subtypes `Row_C`, `Quantity_C` and `Result_C` of `Worldline.Resource_Ledger_C_API`;
- renames `package Q renames Resource_Quantities;` and `package L renames Resource_Ledger;`.

1. `use Ledger_Transport;`
2. `Row_Size : constant Size := Row_C'Object_Size / System.Storage_Unit;`
3. `Quantity_Size : constant Size := Quantity_C'Object_Size / System.Storage_Unit;`
4. `then return 255; end if;`. This closes the guard, which is verbatim from `:118-134`.
5. `Arena : constant Q.Byte_Array := Copy_Data (Data, Data_Length);`
6. `Typed_Rows : L.Reservation_Array (1 .. Q.Byte_Count (Row_Count));`
7. `Slots : L.Span_Array (Typed_Rows'Range);`
8. `Detail_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Detail_Length));`
9. `Total_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Total_Length));`
10. `Typed_Details : L.Quantity_Array (Typed_Rows'Range);`
11. `Total : Q.Quantity;`
12. `V : constant Row_C := As_Row (Rows + Storage_Offset (Size (I - 1) * Row_Size)).all;`
13. `D : constant Worldline.Resource_Ledger_C_API.Row_Acceptance := Worldline.Resource_Ledger_C_API.Accept_Row (V);`
14. `if not D.Ok then return 255; end if;`
15. `Typed_Rows (I) := D.Row;`
16. `Slots (I) := D.Slot;`
17. `L.Compute (Arena, Typed_Rows, Slots, Detail_Arena, Total_Arena, Typed_Details, Total, Status);`
18. `Write_Data (Detail_Data, Detail_Arena);`
19. `Write_Data (Total_Data, Total_Arena);`
20. `As_Quantity (Details + Storage_Offset (Size (I - 1) * Quantity_Size)).all := Worldline.Resource_Ledger_C_API.Encode_Quantity (Typed_Details (I));`
21. `As_Result (Result).all := Worldline.Resource_Ledger_C_API.Result_Of (Status, Total);`
22. `return 0;`
23. `exception when others => return 255; end Resource_Ledger_Compute;`

Counts: `.all :=` 2; `Write_Data (` 2; `L.Compute (` 1. Writes run unconditionally after `L.Compute`, in this order (§7 U7).

### B4.8 `Resource_Ledger_Headroom` (U7, PK-3)

1. `use Ledger_Transport;`
2. `Quantity_Size : constant Size := Quantity_C'Object_Size / System.Storage_Unit;`
3. `then return 255; end if;`. This closes the guard, which is verbatim from `:186-197`.
4. `A : constant Quantity_C := As_Quantity (Available).all;`
5. `W : constant Quantity_C := As_Quantity (Withheld).all;`
6. `F : constant Quantity_C := As_Quantity (Floor).all;`
7. `HI : constant Worldline.Resource_Ledger_C_API.Headroom_Acceptance := Worldline.Resource_Ledger_C_API.Accept_Headroom_Inputs (A, W, F);`
8. `if not HI.Ok then return 255; end if;`
9. `Arena : constant Q.Byte_Array := Copy_Data (Data, Data_Length);`
10. `Output_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Output_Length));`
11. `L.Compute_Headroom (Arena, HI.Available, HI.Withheld, HI.Floor, Output_Arena, Typed_Result, Status);`
12. `Write_Data (Output, Output_Arena);`
13. `As_Result (Result).all := Worldline.Resource_Ledger_C_API.Result_Of (Status, Typed_Result);`
14. `return 0;`
15. `exception when others => return 255; end Resource_Ledger_Headroom;`

Counts: `.all :=` 1; `Write_Data (` 1.

### B4.9 `Resource_Policy_Admit` (U8, PK-3)

Transport package `Policy_Transport`:
- holds `As_Byte`, `As_Input`, `As_Disk`, `As_Result`, `Extent_Valid` and `Decode_Data`, copied from `core/worldline-resource_policy_c_api.adb:14-112`. `Shape` and `Decode` move to SPARK.
- declares subtypes `Input_C`, `Disk_C` and `Result_C`;
- renames `package Q renames Resource_Quantities;` and `package P renames Resource_Admission;`.

1. `use Policy_Transport;`
2. `Disk_Size : constant Size := Disk_C'Object_Size / System.Storage_Unit;`
3. `then return 255; end if;`. This closes the guard, which is verbatim from `:120-131`.
4. `V : constant Input_C := As_Input (Input).all;`
5. `IA : constant Worldline.Resource_Policy_C_API.Input_Acceptance := Worldline.Resource_Policy_C_API.Accept_Input (V);`
6. `if not IA.Ok then return 255; end if;`
7. `Rows : P.Disk_Array (1 .. Q.Byte_Count (Disk_Count));`
8. `Row : constant Disk_C := As_Disk (Disks + Storage_Offset (Size (I - 1) * Disk_Size)).all;`
9. `D : constant Worldline.Resource_Policy_C_API.Disk_Acceptance := Worldline.Resource_Policy_C_API.Accept_Disk (Row);`
10. `if not D.Ok then return 255; end if;`
11. `Rows (I) := D.Item;`
12. `Arena : constant Q.Byte_Array := Decode_Data (Data, Data_Length);`
13. `Decision : constant P.Decision := P.Admit (Arena, IA.State, Rows);`
14. `As_Result (Result).all := Worldline.Resource_Policy_C_API.Encode_Decision (Decision);`
15. `return 0;`
16. `exception when others => return 255; end Resource_Policy_Admit;`

Counts: `.all :=` 1; `P.Admit (` 1.

### B4.10 `Evaluation_History_Select` (U9, PK-4)

Transport package `History_Transport`:
- holds `As_Byte`, `As_Row`, `As_Query`, `As_Selection`, `Extent_Valid` and `Copy_Data`, copied from `core/worldline-evaluation_history_c_api.adb:14-89`. `Id_Valid`, `Cursor_Valid`, `Row_Valid`, the decoders and `Ref_Index` move to SPARK.
- declares subtypes `Row_C`, `Query_C` and `Selection_C`;
- renames `package H renames Evaluation_History;` and `package R renames Resource_Quantities;`.

1. `use History_Transport;`
2. `Stride : constant Size := Worldline.Evaluation_History_C_API.Layout_Size (4);`
3. `if Data_Length > Size (R.Byte_Count'Last) or else Row_Count > Size (R.Byte_Count'Last) or else Row_Count > Size (Storage_Offset'Last) / Stride or else not Worldline.Evaluation_History_C_API.Final_Flag_Valid (Final_Present) or else not Extent_Valid (Data, Data_Length) or else not Extent_Valid (Rows, Row_Count * Stride, Row_C'Alignment) or else (Worldline.Evaluation_History_C_API.Final_Row_Present (Final_Present) and then not Extent_Valid (Final_Row, Stride, Row_C'Alignment)) or else not Extent_Valid (Query, Worldline.Evaluation_History_C_API.Layout_Size (5), Query_C'Alignment) or else not Extent_Valid (Output, Worldline.Evaluation_History_C_API.Layout_Size (6), Selection_C'Alignment) then return 255; end if;`
4. `Raw_Q : constant Query_C := As_Query (Query).all;`
5. `A : constant R.Byte_Array := Copy_Data (Data, Data_Length);`
6. `History : H.History (1 .. R.Byte_Count (Row_Count));`
7. `F : H.Optional_Record;`
8. `QA : constant Worldline.Evaluation_History_C_API.Query_Acceptance := Worldline.Evaluation_History_C_API.Accept_Query (Raw_Q);`
9. `if not QA.Ok then return 255; end if;`
10. `if Worldline.Evaluation_History_C_API.Final_Row_Present (Final_Present) then`
11. `V : constant Row_C := As_Row (Final_Row).all;`
12. `FA : constant Worldline.Evaluation_History_C_API.Final_Acceptance := Worldline.Evaluation_History_C_API.Accept_Final_Row (V);`
13. `if not FA.Ok then return 255; end if;`
14. `F := FA.Item;`
15. `V : constant Row_C := As_Row (Rows + Storage_Offset (Size (I - 1) * Stride)).all;`
16. `D : constant Worldline.Evaluation_History_C_API.Row_Acceptance := Worldline.Evaluation_History_C_API.Accept_Row (V);`
17. `if not D.Ok then return 255; end if;`
18. `History (I) := D.Item;`
19. `Result : constant Selection_C := Worldline.Evaluation_History_C_API.Select_Result (A, History, F, QA.Item);`
20. `As_Selection (Output).all := Result;`
21. `return 0;`
22. `exception when others => return 255; end Evaluation_History_Select;`

Counts: `.all :=` 1; `Select_Result (` 1.

### B4.11 `Pending_Decide_V1` and `Pending_Decide_V2` (U10, U11, PK-7)

Transport packages `Pending_Transport` and `Pending_V2_Transport`:
- hold the pointer instances `Request_Pointers`, `Result_Pointers`, `Row_Pointers` and `Byte_Pointers`, with `Extent_Valid`, `Disjoint` and `Copy_Data`, copied from `core/evaluation_pending_c.adb:12-104` and `core/evaluation_pending_v2_c.adb:14-125`;
- declare subtypes `Request`, `Result` and `Row`;
- rename `package E renames Evaluation_Pending;`, and in v2 also `package V2 renames Evaluation_Pending_V2;`.

`Pending_Decide_V1`:
1. `use Pending_Transport;`
2. `Request_Size : constant I64 := Evaluation_Pending_C.Layout_Size (4);`
3. `Result_Size : constant I64 := Evaluation_Pending_C.Layout_Size (5);`
4. `Stride : constant I64 := Evaluation_Pending_C.Layout_Size (3);`
5. `if not Extent_Valid (Input, Request_Size, Request'Alignment) or else not Extent_Valid (Output, Result_Size, Result'Alignment) or else not Disjoint (Input, Request_Size, Output, Result_Size) then return 255; end if;`
6. `R : constant Request := Request_Pointers.To_Pointer (Input).all;`
7. `if not Evaluation_Pending_C.Header_Valid (R) or else R.Data_Length < 0 or else R.Row_Count < 0 or else Stride <= 0 or else R.Row_Count > I64 (Storage_Offset'Last) / Stride or else not Extent_Valid (R.Data, R.Data_Length, E.Byte'Alignment) or else not Extent_Valid (R.Rows, R.Row_Count * Stride, Row'Alignment) or else not Disjoint (Output, Result_Size, R.Data, R.Data_Length) or else not Disjoint (Output, Result_Size, R.Rows, R.Row_Count * Stride) or else not Evaluation_Pending_C.Request_Fields_Valid (R) then return 255; end if;`
8. `A : constant E.Bytes := Copy_Data (R.Data, R.Data_Length);`
9. `J : E.Journal (1 .. E.Count (R.Row_Count));`
10. `V : constant Row := Row_Pointers.To_Pointer (R.Rows + Storage_Offset (I64 (I - 1) * Stride)).all;`
11. `D : constant Evaluation_Pending_C.Row_Acceptance := Evaluation_Pending_C.Accept_Row (V);`
12. `if not D.Ok then return 255; end if;`
13. `J (I) := D.Item;`
14. `O : constant Evaluation_Pending_C.Decide_Acceptance := Evaluation_Pending_C.Decide_Value (A, J, R);`
15. `if not O.Ok then return 255; end if;`
16. `Result_Pointers.To_Pointer (Output).all := O.Value;`
17. `return 0;`
18. `exception when others => return 255; end Pending_Decide_V1;`

`Pending_Decide_V2` uses the same tokens with these substitutions: `Pending_V2_Transport`, `Evaluation_Pending_V2_C.`, token 9 `J : V2.Journal (1 .. E.Count (R.Row_Count));` and `end Pending_Decide_V2;`. Counts for each: `.all :=` 1; `Decide_Value (` 1. Under D-13 option (i), the component transport unit carries the same token lists with component-local names. That table is fixed in PK-7's review (§16.1).

### B4.12 `Run_Ledger_Check` (U12, PK-5)

Transport package `Run_Ledger_Transport`:
- holds `Packet_At`, `Result_At`, `Row_At`, `Native_At`, `Byte_At`, `Shape` and `Array_Shape`, copied from `core/resource_run_ledger_c_api.adb:14-184` up to the export. The `Layout` function stays in SPARK.
- renames `package Q renames Resource_Quantities;` and `package W renames Resource_Run_Ledger_Wire;`.

1. `use Run_Ledger_Transport;`
2. `Row_Size : constant Interfaces.C.size_t := W.Raw_Row'Size / System.Storage_Unit;`
3. `Native_Size : constant Interfaces.C.size_t := W.Raw_Native'Size / System.Storage_Unit;`
4. `then return -1; end if;`. This closes the guard, which is verbatim from `:195-205`.
5. `Raw : constant W.Raw_Packet := Packet_At (Input).all;`
6. `Data : Q.Byte_Array (1 .. Q.Byte_Count (Arena_Length));`
7. `Before : W.Raw_Row_Array (1 .. Q.Byte_Count (Before_Count));`
8. `Proposed : W.Raw_Row_Array (1 .. Q.Byte_Count (Proposed_Count));`
9. `Observed : W.Raw_Native_Array (1 .. Q.Byte_Count (Native_Count));`
10. `for I in Data'Range loop Data (I) := Byte_At (Arena + Storage_Offset (I - 1)).all; end loop;`
11. `for I in Before'Range loop Before (I) := Row_At (Before_Rows + Storage_Offset (Interfaces.C.size_t (I - 1) * Row_Size)).all; end loop;`
12. `for I in Proposed'Range loop Proposed (I) := Row_At (Proposed_Rows + Storage_Offset (Interfaces.C.size_t (I - 1) * Row_Size)).all; end loop;`
13. `for I in Observed'Range loop Observed (I) := Native_At (Native + Storage_Offset (Interfaces.C.size_t (I - 1) * Native_Size)).all; end loop;`
14. `O : constant Resource_Run_Ledger_C_API.Check_Acceptance := Resource_Run_Ledger_C_API.Check_Decision (Data, Raw, Before, Proposed, Observed);`
15. `if not O.Ok then return -1; end if;`
16. `Result_At (Output).all := O.Value;`
17. `return 0;`
18. `exception when others => return -1; end Run_Ledger_Check;`

Counts: `.all :=` 1; `W.Well_Formed (` 0 in this unit, because it is evaluated once inside `Check_Decision`, as the original evaluated it once.

### B4.13 `Chain_Replay` (U13, PK-5)

Transport package `Chain_Transport`:
- holds `Anchors_At`, `Row_At`, `Result_At` and `Shape`, copied from `core/worldline-chain_authority_c_api.adb:16-63`;
- renames `package W renames Worldline.Chain_Authority_Wire;` and `package A renames W.A;`.

1. `use Chain_Transport;`
2. `Stride : constant Interfaces.C.size_t := W.Raw_Row'Size / System.Storage_Unit;`
3. `then return -1; end if;`. This closes the guard, which is verbatim from `:72-83`.
4. `H : constant W.Raw_Anchors := Anchors_At (Anchors).all;`
5. `Owned : A.Retained_Rows (1 .. A.Q.Byte_Count (Rows_Count));`
6. `if not W.Well_Formed (H) then return -1; end if;`
7. `Raw : constant W.Raw_Row := Row_At (Rows + Storage_Offset (Interfaces.C.size_t (I - 1) * Stride)).all;`
8. `D : constant Worldline.Chain_Authority_C_API.Row_Acceptance := Worldline.Chain_Authority_C_API.Accept_Row (Raw);`
9. `if not D.Ok then return -1; end if;`
10. `Owned (I) := D.Item;`
11. `RV : constant Worldline.Chain_Authority_C_API.Replay_Acceptance := Worldline.Chain_Authority_C_API.Replay_Value (Owned, H);`
12. `if not RV.Ok then return -1; end if;`
13. `Result_At (Output).all := RV.Value;`
14. `return 0;`
15. `exception when others => return -1; end Chain_Replay;`

Counts: `.all :=` 1. `Replay_Value` is completed in `core/worldline-chain_authority_c_api.adb`, where `W` is declared (`:5`). It has a statement body ending `end Replay_Value;`, whose isolated text contains `return (Ok => True, Value => W.Decide (Owned, H));` exactly once (E3).

### B4.14 `Completion_Decide` (U14, PK-6b)

Transport package `Completion_Transport`:
- holds the pointer instances, `Copy_Data`, `Extent_Valid`, `Disjoint` and `Array_Valid`, copied from `core/evaluation_completion_c.adb:24-38` and the helper region before `Decide`;
- holds `Context_Matches` and `Metadata_Base` (B4.16, B4.18);
- declares subtypes for the unit's record types (`Request`, `Result`, `Journal_Row`, `Check_Row`, `History_Row`, `Required_Row`, `Context_Input`, `Context_Row`, `Metadata_Context`, `Row_Metadata`);
- renames `package P renames Evaluation_Pending;`, `package V renames Evaluation_Pending_V2;`, `package T renames Evaluation_Completion;`, `package H renames Evaluation_History;`, `package E renames Worldline.Evaluation;`, `package Roster renames Evaluation_Completion_Roster;`, `package Raw_Roster renames Evaluation_Raw_Roster;` and `package W renames Worldline.Evaluation_Wire;` (`:15-22`).

1. `use Completion_Transport;`
2. `not Evaluation_Completion_C.Decide_Header_Valid (R)`
3. `not Evaluation_Completion_C.Decide_Fields_Valid (R)`
4. `then return 255; end if;`
5. `A : constant P.Bytes := Copy_Data (R.Data, R.Data_Length);` (`:423`)
6. `J : V.Journal (1 .. P.Count (R.Journal_Count));` (`:424`)
7. `Measures : Roster.Measured_Array (1 .. P.Count (R.Captured_Count));` (`:425`)
8. `Captured : T.Result_Array (1 .. P.Count (R.Captured_Count));` (`:426`)
9. `Retained_Results : T.Result_Array (1 .. P.Count (R.Retained_Count));` (`:427`)
10. `History : H.History (1 .. H.Byte_Count (R.History_Count));` (`:428`)
11. `Required : Roster.Check_Array (1 .. P.Count (R.Required_Count));` (`:429`)
12. `:= Evaluation_Completion_C.Accept_Journal_Row (X);` then `if not JA.Ok then return 255; end if;` then `J (I) := JA.Item;`
13. `:= Evaluation_Completion_C.Accept_Captured_Row (X);` then `if not CR.Ok then return 255; end if;` then `Captured (I) := CR.Item;` then `Measures (I) := CR.Measure;`
14. `:= Evaluation_Completion_C.Accept_Result_Row (X);` then `if not RR.Ok then return 255; end if;` then `Retained_Results (I) := RR.Item;`
15. `:= Evaluation_Completion_C.Accept_History_Row (X);` then `if not HR.Ok then return 255; end if;` then `History (I) := HR.Item;`
16. `:= Evaluation_Completion_C.Accept_Required_Row (X);` then `if not QR.Ok then return 255; end if;` then `Required (I) := QR.Item;`
17. `Evaluation_Completion_C.Decide_Value (R, A, J, Captured, Measures, Retained_Results, History, Required, Response, Status);`
18. `if Status /= 0 then return Status; end if;`
19. `Outputs.To_Pointer (Output).all := Response;`
20. `return 0;`
21. `exception when others => return 255; end Completion_Decide;`

Counts: `.all :=` 1; `Decide_Value (` 1; `Response :=` 0.

Tokens 6–11 are the array declarations whose bounds give the invariants of §5.4. Changing any of them fails the check (D-18).

### B4.15 `Completion_Raw_Decide` (U14, PK-6b)

1. `use Completion_Transport;`
2. `not Evaluation_Completion_C.Raw_Header_Valid (R)`
3. `not Evaluation_Completion_C.Raw_Fields_Valid (R)`
4. `then return 255; end if;`
5. `A : constant P.Bytes := Copy_Data (R.Data, R.Data_Length);` (`:564`)
6. `J : V.Journal (1 .. P.Count (R.Journal_Count));` (`:565`)
7. `Measures : Raw_Roster.Measured_Array (1 .. P.Count (R.Captured_Count));` (`:566`)
8. `Captured : T.Result_Array (1 .. P.Count (R.Captured_Count));` (`:567`)
9. `Retained_Results : T.Result_Array (1 .. P.Count (R.Retained_Count));` (`:568`)
10. `History : H.History (1 .. H.Byte_Count (R.History_Count));` (`:569`)
11. `Required : Roster.Check_Array (1 .. P.Count (R.Required_Count));` (`:570`)
12. the journal tokens of B4.14 item 12
13. `:= Evaluation_Completion_C.Accept_Raw_Check_Row (X);` then `if not KA.Ok then return 255; end if;` then `Captured (I) := KA.Item;`
14. `:= Evaluation_Completion_C.Accept_Raw_Measure (KA.Item, KA.Declared, Wire, Confined);` then `if not MA.Ok then return 255; end if;` then `Measures (I) := MA.Item;`
15. the retained, history and required tokens of B4.14 items 14–16
16. `Evaluation_Completion_C.Raw_Decide_Value (R, A, J, Captured, Measures, Retained_Results, History, Required, Response, Status);`
17. `if Status /= 0 then return Status; end if;`
18. `Outputs.To_Pointer (Output).all := Response;`
19. `return 0;`
20. `exception when others => return 255; end Completion_Raw_Decide;`

Counts: `.all :=` 1; `Raw_Decide_Value (` 1. The wire row and the confinement row of row I are read only after token 13's test (§7 U14).

### B4.16 `Completion_Transport.Context_Matches` (U14, PK-6b; isolated by `end Context_Matches;`)

Local renames are as at `core/evaluation_completion_c.adb:736-737`: `package CA renames Worldline.Evaluation_Authority;` and `package CW renames Worldline.Collapse_Wire;`.

1. `Diagnostic_Transport.Mark ("completion.context.enter");`
2. `Diagnostic_Transport.Mark ("completion.context.input-extents-rejected");`
3. `not Evaluation_Completion_C.Context_Header_Valid (R, X)`
4. `not Evaluation_Completion_C.Context_Fields_Valid (R, X)`
5. `not Evaluation_Completion_C.Context_Agent_Matches (X, Raw_Agent, Agent_Confinement)`
6. `Diagnostic_Transport.Mark ("completion.context.transport-guard-rejected");`
7. `Diagnostic_Transport.Mark ("completion.context.copy-arenas");`
8. `Diagnostic_Transport.Mark ("completion.context.arenas-copied");`
9. `FA : constant Evaluation_Completion_C.Context_Fields_Acceptance := Evaluation_Completion_C.Accept_Context_Fields (X);`
10. `if not FA.Ok then Diagnostic_Transport.Value ("completion.context.field-rejected", FA.Rejected_Position); return 255; end if;`
11. `RA : constant Evaluation_Completion_C.Context_Row_Acceptance := Evaluation_Completion_C.Accept_Context_Row (Original, Owned);`
12. `case RA.Verdict is`
13. `when Evaluation_Completion_C.Row_Rejected => Diagnostic_Transport.Value ("completion.context.row-rejected", I64 (I)); return 255;`
14. `when Evaluation_Completion_C.Row_Field_Rejected => Diagnostic_Transport.Value ("completion.context.row-field-row", I64 (I)); Diagnostic_Transport.Value ("completion.context.row-field-rejected", RA.Rejected_Field_Position); return 255;`
15. `when Evaluation_Completion_C.Row_Accepted => Rows (I) := RA.Row; Joined (I) := RA.Joined;`
16. `:= Evaluation_Completion_C.Accept_Required_Pair (Original, Owned);`
17. `if not QA.Ok then Diagnostic_Transport.Value ("completion.context.required-rejected", I64 (I)); return 255; end if;`
18. `Required (I) := QA.Item;` then `Expected_Required (I) := QA.Expected;`
19. `Diagnostic_Transport.Mark ("completion.context.join");`
20. `V : constant Evaluation_Completion_C.Join_Verdict := Evaluation_Completion_C.Context_Join_Value (R, X, Raw_Collapse, Data, Context_Data, FA.Expected, FA.Observed, Rows, Joined, Required, Expected_Required);`
21. `if V = Evaluation_Completion_C.Join_Malformed then return 255; end if;`
22. `Diagnostic_Transport.Value ("completion.context.join-result", I64 (Evaluation_Completion_C.Join_Code (V = Evaluation_Completion_C.Join_Match)));`
23. `return Evaluation_Completion_C.Join_Code (V = Evaluation_Completion_C.Join_Match);`
24. `exception when Error : others => Diagnostic_Transport.Exception_Text ("completion.context", Error); return 255; end Context_Matches;`

Counts: `CA.Join_Context` 0 here, because `Join_Context` is called once inside `Context_Join_Value`; `.all :=` 0.

### B4.17 `Completion_Metadata_Matches` (U14, PK-6b)

The local rename is as at `core/evaluation_completion_c.adb:911`: `package CA renames Worldline.Evaluation_Authority;`.

1. `use Completion_Transport;`
2. `Diagnostic_Transport.Mark ("completion.metadata.enter");`
3. `Diagnostic_Transport.Mark ("completion.metadata.input-extents-rejected");`
4. `not Evaluation_Completion_C.Metadata_Header_Valid (R, X)`
5. `Diagnostic_Transport.Mark ("completion.metadata.transport-guard-rejected");`
6. `Diagnostic_Transport.Mark ("completion.metadata.copy-arenas");`
7. `Diagnostic_Transport.Mark ("completion.metadata.arenas-copied");`
8. `:= Evaluation_Completion_C.Accept_Metadata_Row (Original, Owned);`
9. `if not MA.Ok then Diagnostic_Transport.Value ("completion.metadata.row-rejected", I64 (I)); return 255; end if;`
10. `Rows (I) := MA.Row;` then `Projected (I) := MA.Projected;`
11. `Diagnostic_Transport.Mark ("completion.metadata.join");`
12. `CA.Join_Metadata (Data, Projected_Data, Rows, Projected);`
13. `Diagnostic_Transport.Value ("completion.metadata.join-result",`
14. `return Evaluation_Completion_C.Join_Code (Joined);`
15. `exception when Error : others => Diagnostic_Transport.Exception_Text ("completion.metadata", Error); return 255; end Completion_Metadata_Matches;`

### B4.18 `Completion_Transport.Metadata_Base` (U14, PK-6b)

1. `Evaluation_Completion_C.Metadata_Version_Valid (X)`
2. `return X.Base;`
3. `exception when others => return System.Null_Address; end Metadata_Base;`

Counts: `.all :=` 0.

### B4.19 `Native_Diagnostic_Control` (RC1, PK-6b)

1. `case Evaluation_Completion_C.Diagnostic_Control_Of (Enable) is`
2. `when Evaluation_Completion_C.Start_Trace => Evaluation_Completion_C.Diagnostic_Start (Code, Emit_Begin); if Emit_Begin then Diagnostic_Transport.Mark ("trace.begin"); end if; return Code;`
3. `when Evaluation_Completion_C.Stop_Trace => Diagnostic_Transport.Mark ("trace.end"); Evaluation_Completion_C.Diagnostic_Stop (Code); return Code;`
4. `when Evaluation_Completion_C.Invalid_Control => return Evaluation_Completion_C.Diagnostic_Invalid_Code;`
5. `end case; end Native_Diagnostic_Control;`

Counts: `exception` 0, so there is no handler, as in the original (`core/evaluation_completion_c.adb:73-88`). `Diagnostic_Active` and `Diagnostic_Failed` both 0.

### B4.20 `Finalization_Decide` (U15, PK-6b)

Transport package `Finalization_Transport`:
- holds the pointer instances `Requests`, `Outputs`, `Rows`, `Plans` and `Octets`, the extent, disjointness and copy helpers, and `Final_Context_Matches` (B4.21), copied from `core/evaluation_finalization_c.adb:28-120`;
- declares subtypes `Request`, `Result`, `Row` and `Required_Row`;
- renames `package F renames Evaluation_Finalization;`, `package T renames F.T;`, `package P renames F.P;`, `package R renames F.R;`, `package H renames F.H;`, `package W renames F.W;`, `package K renames Evaluation_Completion_C;`, `package CW renames Worldline.Collapse_Wire;` and `package Authority renames Worldline.Evaluation_Authority;` (`:9-17`).

1. `use Finalization_Transport;`
2. `Diagnostic_Transport.Mark ("finalization.decide.enter");`
3. `Diagnostic_Transport.Mark ("finalization.decide.input-extents-rejected");`
4. `not Evaluation_Finalization_C.Request_Header_Valid (X)`
5. `not Evaluation_Finalization_C.Request_Fields_Valid (X)`
6. `Diagnostic_Transport.Mark ("finalization.decide.transport-guard-rejected");`
7. `Diagnostic_Transport.Mark ("finalization.decide.copy-arena");`
8. `Captured : F.Start_Rows (1 .. P.Count (X.Row_Count));`
9. `:= Evaluation_Finalization_C.Accept_Plan (Q);`
10. `if not PA.Ok then Diagnostic_Transport.Value ("finalization.decide.required-rejected", I64 (K)); return 255; end if;`
11. `Required (K) := PA.Item;`
12. `if Evaluation_Finalization_C.Needs_Rows (X) then`
13. `RA : constant Evaluation_Finalization_C.Row_Acceptance := Evaluation_Finalization_C.Accept_Row (Q);`
14. `if not RA.Ok then Diagnostic_Transport.Value ("finalization.decide.row-rejected", I64 (K)); return 255; end if;`
15. `Captured (K) := RA.Item;`
16. `O := Evaluation_Finalization_C.Decide_Rows_Value (X, A, Required, Captured);`
17. `else O := Evaluation_Finalization_C.Decide_No_Rows_Value (X, A, Required); end if;`
18. `if not O.Ok then return 255; end if;`
19. `Diagnostic_Transport.Value ("finalization.decide.reason", I64 (O.Value.Reason));`
20. `Diagnostic_Transport.Value ("finalization.decide.promotion", I64 (O.Value.Promotion));`
21. `Outputs.To_Pointer (Output).all := O.Value;`
22. `return 0;`
23. `exception when Error : others => Diagnostic_Transport.Exception_Text ("finalization.decide", Error); return 255; end Finalization_Decide;`

Counts:
- `O :=` 2;
- `.all :=` 1;
- `Captured` as an actual parameter only in token 16, checked as `Captured)` 1;
- `Decide_No_Rows_Value (X, A, Required)` 1.

This is the only R-W exception (B0).

### B4.21 `Finalization_Transport.Final_Context_Matches` (U15, PK-6b; isolated by `end Final_Context_Matches;`)

1. `Native : aliased Evaluation_Finalization_C.Result := Evaluation_Finalization_C.Initial_Result;`
2. `Diagnostic_Transport.Mark ("finalization.context.enter");`
3. `Finalization_Decide (Input, Native'Address)`
4. `Evaluation_Finalization_C.Final_Seal_Ready (Seal_Status, Native)`
5. `Diagnostic_Transport.Mark ("finalization.context.seal-rejected");`
6. `X : constant Request := Requests.To_Pointer (Input).all;` (`:280`)
7. `Evaluation_Finalization_C.Final_Plans_Valid (X)`
8. `Diagnostic_Transport.Mark ("finalization.context.required-extent-rejected");`
9. `Projected_Rows : aliased Check_Array (1 .. P.Count (X.Row_Count));` (`:292`)
10. `Projected_Plans : aliased Plan_Array (1 .. P.Count (X.Start.Required.Length));` (`:293`)
11. `Projected_Rows (I) := Evaluation_Finalization_C.Final_Projected_Row (X, Original);`
12. `Projected_Plans (I) := Plans.To_Pointer (X.Required + Storage_Offset ((X.Start.Required.First - 1 + I64 (I - 1)) * Plan_Size)).all;` (`:315-317`)
13. `Projection := Evaluation_Finalization_C.Final_Projection (X, Native, Projected_Rows'Address, Projected_Plans'Address);`
14. `Diagnostic_Transport.Mark ("finalization.context.projected");`
15. `Completion_Transport.Context_Matches (Projection'Address, Completion_Transport.Metadata_Base (Metadata), Collapse, Agent, Agent_Confinement);`
16. `Diagnostic_Transport.Value ("finalization.context.context-result", I64 (Context_Result));`
17. `if Context_Result /= 1 then return False; end if;`
18. `Completion_Metadata_Matches (Projection'Address, Metadata);`
19. `Diagnostic_Transport.Value ("finalization.context.metadata-result", I64 (Metadata_Result));`
20. `return Metadata_Result = 1;`
21. `exception when Error : others => Diagnostic_Transport.Exception_Text ("finalization.context", Error); return False; end Final_Context_Matches;`

The local array types `Check_Array` and `Plan_Array` keep their declarations from `:267-270`, with `Convention => C`.

### B4.22 `Finalization_Decide_Mixed` (U15, PK-6b)

The local pointer instances are as at `:363-364`.

1. `use Finalization_Transport;`
2. `function Read_Ready (Kind : U32; Input, Raw, Confined : System.Address) return Evaluation_Finalization_C.Readiness_Result is`
3. `case Evaluation_Finalization_C.Kind_Of (Kind) is`
4. `when Evaluation_Finalization_C.Absent_Source => return (Valid => True, Ready => 0);`
5. `Ordinary : aliased Evaluation_Completion_C.Result := Evaluation_Completion_C.Initial_Response;`
6. `Completion_Raw_Decide (Input, Raw, Confined, Ordinary'Address)`
7. `return Evaluation_Finalization_C.Ordinary_Readiness (Status, Ordinary);`
8. `Finalized : aliased Evaluation_Finalization_C.Result := Evaluation_Finalization_C.Initial_Result;`
9. `Finalization_Decide (Input, Finalized'Address)`
10. `:= Evaluation_Finalization_C.Finalized_Readiness (Status, Finalized);`
11. `if not R1.Valid then return R1; end if;`
12. `X : constant Request := Requests.To_Pointer (Input).all;`
13. `return Evaluation_Finalization_C.Finalized_Operation_Readiness (X, Finalized);`
14. `when Evaluation_Finalization_C.Invalid_Source => return (Valid => False, Ready => 0);`
15. `end Read_Ready;`
16. `function Context_Joined (Kind : U32; Input, Metadata : System.Address) return Boolean is`
17. `when Evaluation_Finalization_C.Ordinary_Source => return Completion_Transport.Context_Matches (Input, Completion_Transport.Metadata_Base (Metadata), Collapse, Agent, Agent_Confinement) = 1;`
18. `when Evaluation_Finalization_C.Finalized_Source => return Final_Context_Matches (Input, Metadata, Collapse, Agent, Agent_Confinement);`
19. `end Context_Joined;`
20. `Diagnostic_Transport.Mark ("finalization.mixed.enter");`
21. `Diagnostic_Transport.Mark ("finalization.mixed.collapse-extent-rejected");`
22. `Bound : constant CW.Raw_Request := Collapse_Requests.To_Pointer (Collapse).all;`
23. `Needed : constant Authority.Raw_Dependency := Authority.Dependencies (Bound);`
24. `Diagnostic_Transport.Mark ("finalization.mixed.dependency-rejected");`
25. `if Authority.Needs_Primary (Needed) then`
26. `Read_Ready (Primary_Kind, Primary, Primary_Raw, Primary_Confinement)`
27. `Diagnostic_Transport.Mark ("finalization.mixed.primary-ready-rejected");`
28. `if Authority.Needs_Staged (Needed) then`
29. `Read_Ready (Staged_Kind, Staged, Staged_Raw, Staged_Confinement)`
30. `Diagnostic_Transport.Mark ("finalization.mixed.staged-ready-rejected");`
31. `Diagnostic_Transport.Value ("finalization.mixed.primary-ready", I64 (P_Ready));`
32. `Diagnostic_Transport.Value ("finalization.mixed.staged-ready", I64 (S_Ready));`
33. `if Authority.Needs_Agent (Needed) and then Agent /= System.Null_Address then`
34. `Diagnostic_Transport.Mark ("finalization.mixed.agent-extent-rejected");`
35. `Owned_Agent : constant W.Raw_Record := Raw_Records.To_Pointer (Agent).all;`
36. `Agent_Ready := Evaluation_Finalization_C.Agent_Readiness (Owned_Agent, Agent_Confinement);`
37. `if Agent_Ready = W.Invalid_Record then Diagnostic_Transport.Mark ("finalization.mixed.agent-record-rejected"); return CW.Invalid_Request; end if;`
38. `Diagnostic_Transport.Value ("finalization.mixed.agent-ready", I64 (Agent_Ready));`
39. `if Evaluation_Finalization_C.Context_Join_Needed (Agent_Ready, P_Ready) and then not Context_Joined (Primary_Kind, Primary, Primary_Context) then Diagnostic_Transport.Mark ("finalization.mixed.primary-context-rejected"); return CW.Invalid_Request; end if;`
40. `if Evaluation_Finalization_C.Context_Join_Needed (Agent_Ready, S_Ready) and then not Context_Joined (Staged_Kind, Staged, Staged_Context) then Diagnostic_Transport.Mark ("finalization.mixed.staged-context-rejected"); return CW.Invalid_Request; end if;`
41. `Decision := Evaluation_Finalization_C.Mixed_Collapse_Decision (Bound, Agent_Ready, P_Ready, S_Ready);`
42. `Diagnostic_Transport.Value ("finalization.mixed.collapse-decision", I64 (Decision));`
43. `if not Evaluation_Finalization_C.Mixed_Authorized (Decision) then return Decision; end if;`
44. `if Evaluation_Finalization_C.Mixed_Metadata_Needed (Needed, True, Primary_Kind) and then Completion_Metadata_Matches (Primary, Primary_Context) /= 1 then Diagnostic_Transport.Mark ("finalization.mixed.primary-metadata-rejected"); return CW.Invalid_Request; end if;`
45. `if Evaluation_Finalization_C.Mixed_Metadata_Needed (Needed, False, Staged_Kind) and then Completion_Metadata_Matches (Staged, Staged_Context) /= 1 then Diagnostic_Transport.Mark ("finalization.mixed.staged-metadata-rejected"); return CW.Invalid_Request; end if;`
46. `return Decision;`
47. `exception when Error : others => Diagnostic_Transport.Exception_Text ("finalization.mixed", Error); return CW.Invalid_Request; end Finalization_Decide_Mixed;`

Counts:
- `.all :=` 0;
- `Bound.` assignments 0, because the original mutated `Bound` at `:485-486` and the successor builds the delta inside SPARK (A-COST §C16);
- `exception` 1, belonging to the main body. `Read_Ready` and `Context_Joined` have no handlers, as in the original.

### B4.23 `Authority_Glue` retargeting (PK-6b; isolated by `end Decide_Raw_Context;` and `end Decide_Raw_Metadata;`)

`Decide_Raw_Context` (original `core/worldline-c_api.adb:758-822`):
1. `if Completion_Raw_Decide (Primary, Primary_Raw, Primary_Confinement, P_Result'Address) /= 0`
2. `if Completion_Raw_Decide (Staged, Staged_Raw, Staged_Confinement, S_Result'Address) /= 0`
3. `if P_Ready = 1 and then Completion_Transport.Context_Matches (Primary, Primary_Context, Request, Agent, Agent_Confinement) /= 1`
4. `if S_Ready = 1 and then Completion_Transport.Context_Matches (Staged, Staged_Context, Request, Agent, Agent_Confinement) /= 1`

Counts: `K.Raw_Decide` 0 and `K.Context_Matches` 0. Every other statement of the function is unchanged; the C_API pin and the full-body review bind it.

`Decide_Raw_Metadata` (original `:832-876`):
1. `P_Context := Completion_Transport.Metadata_Base (Primary_Context);`
2. `S_Context := Completion_Transport.Metadata_Base (Staged_Context);`
3. `if A.Needs_Primary (Needed) and then Completion_Metadata_Matches (Primary, Primary_Context) /= 1`
4. `if A.Needs_Staged (Needed) and then Completion_Metadata_Matches (Staged, Staged_Context) /= 1`

Counts: `K.Metadata_Base` 0 and `K.Metadata_Matches` 0. The pre-existing `package K renames Evaluation_Completion_C;` (`:761`, `:836`) stays and names types only.

### B4.24 `Diagnostic_Transport` (RC1, PK-6b; isolated as a package body)

1. `procedure Mark (Site : String) is`
2. `Evaluation_Completion_C.Diagnostic_Begin_Line (Site, Write);`
3. `if Write then Ada.Text_IO.Put_Line (Ada.Text_IO.Standard_Error, Evaluation_Completion_C.Diagnostic_Line (Site)); Ada.Text_IO.Flush (Ada.Text_IO.Standard_Error); end if;`
4. `exception when others => Evaluation_Completion_C.Diagnostic_Latch_Failure; end Mark;`
5. `procedure Value (Site : String; Number : Interfaces.Integer_64) is`
6. `Evaluation_Completion_C.Diagnostic_Begin_Value (Site, Number, Compose);`
7. `if Compose then Mark (Evaluation_Completion_C.Diagnostic_Value_Site (Site, Number)); end if;`
8. `exception when others => Evaluation_Completion_C.Diagnostic_Latch_Failure; end Value;`
9. `procedure Exception_Text (Site : String; Error : Ada.Exceptions.Exception_Occurrence) is`
10. `Evaluation_Completion_C.Diagnostic_Observe (Active);`
11. `if Active then declare Information : constant String := Ada.Exceptions.Exception_Information (Error);`
12. `Evaluation_Completion_C.Diagnostic_Begin_Exception (Site, Information, Compose);`
13. `if Compose then Mark (Evaluation_Completion_C.Diagnostic_Exception_Site (Site, Information)); end if;`
14. `exception when others => Evaluation_Completion_C.Diagnostic_Latch_Failure; end Exception_Text;`
15. `end Diagnostic_Transport;`

Counts within the package body:
- `Ada.Text_IO.Put_Line` 1, `Ada.Text_IO.Flush` 1, `Standard_Error` 2;
- `Ada.Exceptions.Exception_Information` 1;
- `when others =>` 3;
- `with Atomic` 0, `Diagnostic_Active` 0 and `Diagnostic_Failed` 0.

D2 compares the counts of the first five tokens in the whole C_API body with the counts inside `Mark` and `Exception_Text` respectively.

---

## B5. Predecessor edits E1–E4 (PP1; exact text)

Each edit is one entry of compose's single-occurrence `manifest-edits.json`. The old text is the exact S5 text and occurs once in the manifest. Indentation is shown exactly. Each edit keeps the problem message text, and no other line of the predecessor function changes (PP2).

### E1 (PK-2): `proof_manifest.py:500-504`, base `export_problems`

Old:
```python
    v3 = normalized_ada((root / 'core/worldline-recovery_authorization_v3_c_api.ads').read_text(encoding='utf-8'))
    for symbol in ('wl_recovery_authorization_version_v3', 'wl_recovery_authorization_layout_v3',
                   'wl_recovery_authorization_decide_v3'):
        if v3.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'full-domain recovery export binding differs: {symbol}')
```
New:
```python
    v3 = normalized_ada((root / 'core/worldline-recovery_authorization_v3_c_api.ads').read_text(encoding='utf-8'))
    v3_capi = normalized_ada((root / 'core/worldline-c_api.ads').read_text(encoding='utf-8'))
    for symbol, home in (('wl_recovery_authorization_version_v3', v3), ('wl_recovery_authorization_layout_v3', v3),
                         ('wl_recovery_authorization_decide_v3', v3_capi)):
        if home.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'full-domain recovery export binding differs: {symbol}')
```

### E2 (PK-2): `proof_manifest.py:932-936`, protocol override

Old:
```python
    text = normalized_ada((root / 'core/worldline-recovery_protocol_c_api.ads').read_text(encoding='utf-8'))
    for symbol in ('wl_recovery_protocol_version_v1', 'wl_recovery_protocol_layout_v1',
                   'wl_recovery_protocol_decide_v1'):
        if text.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'protected recovery protocol export binding differs: {symbol}')
```
New:
```python
    text = normalized_ada((root / 'core/worldline-recovery_protocol_c_api.ads').read_text(encoding='utf-8'))
    capi = normalized_ada((root / 'core/worldline-c_api.ads').read_text(encoding='utf-8'))
    for symbol, home in (('wl_recovery_protocol_version_v1', text), ('wl_recovery_protocol_layout_v1', text),
                         ('wl_recovery_protocol_decide_v1', capi)):
        if home.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'protected recovery protocol export binding differs: {symbol}')
```

### E3 (PK-5): `proof_manifest.py:946-949`, chain override

Old:
```python
    spec = (root / 'core/worldline-chain_authority_c_api.ads').read_text()
    body = (root / 'core/worldline-chain_authority_c_api.adb').read_text()
    if spec.count('External_Name => "wl_chain_authority_replay_v1"') != 1 or 'Result_At (Output).all := W.Decide (Owned, H);' not in body:
        problems.append('complete-chain native export is not bound to the selected full-row wire decision')
```
New:
```python
    spec = normalized_ada((root / 'core/worldline-c_api.ads').read_text(encoding='utf-8'))
    body = normalized_ada((root / 'core/worldline-chain_authority_c_api.adb').read_text(encoding='utf-8'))
    capi = normalized_ada((root / 'core/worldline-c_api.adb').read_text(encoding='utf-8'))
    if (spec.count('External_Name => "wl_chain_authority_replay_v1"') != 1
            or _capi_isolate(body, 'Replay_Value').count('return (Ok => True, Value => W.Decide (Owned, H));') != 1
            or _capi_isolate(capi, 'Chain_Replay').count('Result_At (Output).all := RV.Value;') != 1):
        problems.append('complete-chain native export is not bound to the selected full-row wire decision')
```
`_capi_isolate` is defined by the PK-1 tail (B8) and resolved at call time. It returns `''` on any isolation failure and never raises. The decision-to-output protection the predecessor gave is kept and strengthened with exact, isolated tokens. The B4.13 ordered list adds the rest.

### E4 (PK-6b): `proof_manifest.py:488-491`, base `export_problems`

Old:
```python
    finalization = normalized_ada((root / 'core/evaluation_finalization_c.ads').read_text(encoding='utf-8'))
    final_entry = ('function Decide (Input, Output : System.Address) return Interfaces.C.int '
        'with Export, Convention => C, External_Name => "wl_finalization_decide_v1";')
    mixed_entry = ('function Decide_Mixed (Collapse : System.Address; Primary_Kind : U32; '
```
New:
```python
    finalization = normalized_ada((root / 'core/worldline-c_api.ads').read_text(encoding='utf-8'))
    final_entry = ('function Finalization_Decide (Input, Output : System.Address) return Interfaces.C.int '
        'with Export, Convention => C, External_Name => "wl_finalization_decide_v1";')
    mixed_entry = ('function Finalization_Decide_Mixed (Collapse : System.Address; Primary_Kind : U32; '
```
Lines 492–499, which hold the rest of `mixed_entry`, the two count checks and the two messages, are unchanged. The resulting strings equal B3 items 17 and 18.

**No other predecessor changes.** The owner override (`:956-964`) counts the owner symbols in raw `core/worldline-c_api.ads`, and the owner audit override (`:975-994`) checks an exact declaration there. Neither touches a relocated symbol. Both stay byte-identical, as do `:453-487`. PP2's reconstruction check undoes E1–E4, deletes the appended tails, and must reproduce the S5 manifest exactly.

---

## B6. Diagnostic site sequences (`CAPI_DIAGNOSTIC_SITES`; observed in S5, enforced from PK-6b)

The observed sequences were extracted read-only from `core/evaluation_completion_c.adb` and `core/evaluation_finalization_c.adb`. Each is an ordered tuple of (kind, literal); in the successor, kind `Mark` maps to `Diagnostic_Transport.Mark`, `Value` to `.Value`, and `Exception` to `.Exception_Text`. D3 extracts `Diagnostic_Transport\.(Mark|Value|Exception_Text) \("([^"]*)"` from each isolated successor unit and requires the identical tuple.

| Successor unit | S5 origin | Sequence (S5 line of each call) |
|---|---|---|
| `Native_Diagnostic_Control` | `Diagnostic_Control` (`:73-88`) | Mark `trace.begin` (79); Mark `trace.end` (82) |
| `Completion_Transport.Context_Matches` | `Context_Matches` (`:733-869`) | Mark `completion.context.enter` (750); Mark `completion.context.input-extents-rejected` (756); Mark `completion.context.transport-guard-rejected` (782); Mark `completion.context.copy-arenas` (785); Mark `completion.context.arenas-copied` (794); Value `completion.context.field-rejected` (798); Value `completion.context.row-rejected` (813); Value `completion.context.row-field-row` (822); Value `completion.context.row-field-rejected` (823); Value `completion.context.required-rejected` (842); Mark `completion.context.join` (849); Value `completion.context.join-result` (859); Exception `completion.context` (867) |
| `Completion_Transport.Metadata_Base` | `Metadata_Base` (`:893-907`) | none |
| `Completion_Metadata_Matches` | `Metadata_Matches` (`:909-986`) | Mark `completion.metadata.enter` (921); Mark `completion.metadata.input-extents-rejected` (925); Mark `completion.metadata.transport-guard-rejected` (940); Mark `completion.metadata.copy-arenas` (943); Mark `completion.metadata.arenas-copied` (950); Value `completion.metadata.row-rejected` (962); Mark `completion.metadata.join` (971); Value `completion.metadata.join-result` (976); Exception `completion.metadata` (984) |
| `Finalization_Decide` | `Decide` (`core/evaluation_finalization_c.adb:121-257`) | Mark `finalization.decide.enter` (127); Mark `finalization.decide.input-extents-rejected` (132); Mark `finalization.decide.transport-guard-rejected` (155); Mark `finalization.decide.copy-arena` (158); Value `finalization.decide.required-rejected` (175); Value `finalization.decide.row-rejected` (195); Value `finalization.decide.reason` (247); Value `finalization.decide.promotion` (248); Exception `finalization.decide` (255) |
| `Finalization_Transport.Final_Context_Matches` | `Final_Context_Matches` (`:259-355`) | Mark `finalization.context.enter` (272); Mark `finalization.context.seal-rejected` (276); Mark `finalization.context.required-extent-rejected` (288); Mark `finalization.context.projected` (332); Value `finalization.context.context-result` (338); Value `finalization.context.metadata-result` (344); Exception `finalization.context` (353) |
| `Finalization_Decide_Mixed` | `Decide_Mixed` (`:357-509`) | Mark `finalization.mixed.enter` (411); Mark `finalization.mixed.collapse-extent-rejected` (415); Mark `finalization.mixed.dependency-rejected` (424); Mark `finalization.mixed.primary-ready-rejected` (434); Mark `finalization.mixed.staged-ready-rejected` (446); Value `finalization.mixed.primary-ready` (451); Value `finalization.mixed.staged-ready` (452); Mark `finalization.mixed.agent-extent-rejected` (457); Mark `finalization.mixed.agent-record-rejected` (465); Value `finalization.mixed.agent-ready` (472); Mark `finalization.mixed.primary-context-rejected` (476); Mark `finalization.mixed.staged-context-rejected` (481); Value `finalization.mixed.collapse-decision` (488); Mark `finalization.mixed.primary-metadata-rejected` (494); Mark `finalization.mixed.staged-metadata-rejected` (500); Exception `finalization.mixed` (507) |

Observed sequence lengths: 2, 13, 0, 9, 9, 7, 16. Textual sequence equality does not establish the runtime line sequence. C-06 checks that on the integrated library.

---

## B7. Identity binding per stage (RC4, RC5; §8.7)

| Stage | I1: core Ada pins regenerated by compose re-pin | I3/I4: new `CONTRACT_PINS` keys | I5: controls bound by `source-inventory.json` and execution frames | Manifest changes recorded in `composition.json` |
|---|---|---|---|---|
| PK-0 | none | none | `tests/test_capi_characterization.py`, `tests/test_capi_layout_identity.py`, `tests/test_capi_diagnostics.py`, `tests/capi_guard_pages.py`, `tests/capi_characterization.json`, `tests/capi_layout_baseline.json` | none |
| PK-1 | `core/worldline-c_api.ad[sb]`, `core/worldline-resources_c_api.ad[sb]`, `core/worldline-recovery_c_api.ad[sb]` | none | `tests/test_capi_symbol_binding.py` (C-08), `tests/test_capi_manifest_mutations.py` (C-09) | tail append (B8 tables, override, 6 REQUIRED_PROVED names, pins) |
| PK-2 | C_API pair; U3, U4, U5 pairs | none | C-09 data updated in the same files under the stage's own inventory hash | tail append; E1, E2 |
| PK-xR | the repaired specs (and wire specs) only | none | `tests/test_capi_layout_identity.py` data (C-13) | tail append (pins) |
| PK-3, PK-4 | C_API pair and the stage's unit pairs | none | C-09 data | tail append |
| PK-5 | C_API pair; U12, U13 pairs | none | C-09 data | tail append; E3 |
| PK-6a | `core/evaluation_completion_c.ad[sb]`, `core/evaluation_finalization_c.ad[sb]` | none | optional Ada value-level control projects (I4 keys if added) | tail append (57 names, pins) |
| PK-6b | C_API pair; completion pair; finalization pair | none | C-06 and C-09 data | tail append; E4 |
| PK-7 | C_API pair; U10, U11 pairs | `pending-component/core/evaluation_pending_c.ads`, `…_c.adb`, `evaluation_pending_v2_c.ads`, `…_v2_c.adb`, `evaluation_pending_transport.ads`, `…_transport.adb`, `pending-component/pending.gpr` (169 → 176 keys, JACKAL exact); optionally `core/evaluation_pending.ads`/`.adb` (→ 178) | C-10 | tail append |
| PK-S | none | none | none | identities only |

In every stage, every file outside the touched list has the same raw sha256 as in the base stage's `source-inventory.json` (I7, "untouched means identical"). This covers the provider files (`runtime/worldline/*.py`, `core/*.h`, `pending-component/core/*.h`), which this design does not touch (I6). Adding a key changes `proof_source_files` (`proof_manifest.py:662-667`). That change is reviewed in the stage that makes it, and it is never a side effect.

---

## B8. The `export_problems` override (PK-1 tail; PROPOSAL sketch)

The text is not executed and not reviewed, and it imports nothing beyond what the manifest already imports (`hashlib`, `json`, `Path`, `re`, `typing`). It is appended after the last S5 line (`:1029`). Later stages only append `.update` lines.

```python
# C-API raw-pointer boundary consolidation (design v3, stage PK-1). Whole-closure binding,
# exact relocated declarations and ordered decision paths. Every predecessor check runs first.
CAPI_ALTERNATE_BINDINGS = ('Link_Name', 'pragma Export', 'pragma Import', 'pragma Linker_Section',
    'Export_Function', 'Export_Procedure', 'Export_Object', 'Import_Function', 'Import_Procedure',
    'Import_Object', 'Import_Valued_Procedure')
CAPI_PROJECT_FORBIDDEN = ('Linker_Options', '--defsym', '--wrap', '-Wl,', 'version-script')
CAPI_CORE_HOME = {...}            # B2.1 literal: all 91 symbols at their L0 homes, then the PK-1 .update
CAPI_DECLARATIONS = {...}         # B3 successor texts of the relocated symbols
CAPI_ORDERED = {...}              # (file, kind, name) -> ordered tokens (B4)
CAPI_COUNTS = {...}               # (file, kind, name) -> {token: exact count} (B4)
CAPI_DIAGNOSTIC_SITES = {}        # (file, kind, name) -> ((kind, literal), ...) (B6), filled at PK-6b
CAPI_COMPONENT_HOME = {...}       # B2.3 literal, L0 homes
CAPI_COMPONENT_INTERFACE = ('evaluation_pending', 'evaluation_pending_c', 'evaluation_pending_v2',
    'evaluation_pending_v2_c', 'evaluation_epoch', 'resource_quantities', 'spark', 'spark.big_integers')
CAPI_MOVED_UNITS = ('core/worldline-resources_c_api.ads', 'core/worldline-resources_c_api.adb',
    'core/worldline-recovery_c_api.ads', 'core/worldline-recovery_c_api.adb')   # extended per stage (G7)
CAPI_C_API_SUBTYPES = ('subtype U8 is Interfaces.Unsigned_8;', 'subtype U32 is Interfaces.Unsigned_32;',
    'subtype I64 is Interfaces.Integer_64;', 'subtype Size is Interfaces.C.size_t;')
CAPI_DIAGNOSTIC_CALL = re.compile(r'Diagnostic_Transport\.(Mark|Value|Exception_Text) \("([^"]*)"')


def _capi_text(root: Path, relative: str) -> str:
    return normalized_ada((root / relative).read_text(encoding='utf-8'))


def _capi_isolate(text: str, name: str, kind: str = 'subprogram') -> str:
    end_token = f'end {name};'
    if kind == 'package':
        head = f'package body {name} is'
        if text.count(head) != 1:
            return ''
        start = text.find(head)
        end = text.find(end_token, start)
        return '' if end < 0 else text[start:end + len(end_token)]
    if text.count(end_token) != 1:
        return ''
    end = text.find(end_token)
    start = max(text.rfind(f'function {name} ', 0, end), text.rfind(f'procedure {name} ', 0, end))
    return '' if start < 0 else text[start:end + len(end_token)]


def _capi_ordered(text: str, tokens) -> bool:
    position = 0
    for token in tokens:
        found = text.find(token, position)
        if found < 0:
            return False
        position = found + len(token)
    return True


def _capi_symbols(root: Path, files, home_table, label: str) -> list[str]:
    problems, seen, counts = [], {}, {'Export': 0, 'External_Name': 0, 'literal': 0}
    for relative in files:
        text = _capi_text(root, relative)
        for word in CAPI_ALTERNATE_BINDINGS:
            if word in text:
                problems.append(f'{relative}: alternate binding construct {word}')
        if re.search(r'\bImport\b', text):
            problems.append(f'{relative}: Import aspect or pragma')
        counts['Export'] += len(re.findall(r'\bExport\b', text))
        counts['External_Name'] += text.count('External_Name =>')
        for match in re.finditer(r'"(wl_[a-z0-9_]+)"', text):
            counts['literal'] += 1
            seen.setdefault(match.group(1), []).append(relative)
            if not text[:match.start()].endswith('External_Name => '):
                problems.append(f'{relative}: {match.group(1)} is not an External_Name literal')
    if set(seen) != set(home_table):
        problems.append(f'{label} C symbol set differs from the binding table')
    for symbol, homes in seen.items():
        if homes != [home_table.get(symbol)]:
            problems.append(f'{symbol} is bound in {homes}, expected exactly once in {home_table.get(symbol)}')
    if len(set(counts.values())) != 1:
        problems.append(f'{label} Export/External_Name/literal counts differ: {counts}')
    return problems


def _capi_closure_problems(root: Path) -> list[str]:
    core = sorted(name for name in DECLARED_CORE_ADA_SOURCES if name.endswith(('.ads', '.adb')))
    problems = _capi_symbols(root, core, CAPI_CORE_HOME, 'core closure')                  # G1, G2, G3, G4
    for relative in ('core/worldline_core.gpr', 'core/worldline_core_sources.gpr', 'core/attest_sha256.gpr'):
        project = (root / relative).read_text(encoding='utf-8')
        problems += [f'{relative}: linker option {word}' for word in CAPI_PROJECT_FORBIDDEN if word in project]  # G5
    for unit in CAPI_MOVED_UNITS:                                                          # G7
        text = _capi_text(root, unit)
        for word in ('Address_To_Access_Conversions', 'Unchecked_Conversion', "'Address"):
            if word in text:
                problems.append(f'{unit}: {word} remains after relocation')
    return problems


def _capi_component_problems(root: Path) -> list[str]:
    files = sorted(path.relative_to(root).as_posix()
                   for path in (root / 'pending-component/core').glob('*.ad[sb]'))
    problems = _capi_symbols(root, files, CAPI_COMPONENT_HOME, 'component')               # K1, K2
    project = (root / 'pending-component/pending.gpr').read_text(encoding='utf-8')
    problems += [f'pending.gpr misses interface unit {unit}' for unit in CAPI_COMPONENT_INTERFACE
                 if f'"{unit}"' not in project]                                            # K3
    problems += [f'pending.gpr: linker option {word}' for word in CAPI_PROJECT_FORBIDDEN if word in project]
    return problems                                                                        # K4 is C-10 plus pins (I3)


def _capi_profile_problems(root: Path) -> list[str]:
    spec = _capi_text(root, 'core/worldline-c_api.ads')
    body = _capi_text(root, 'core/worldline-c_api.adb')
    problems = [f'{symbol}: relocated declaration differs' for symbol, declaration in CAPI_DECLARATIONS.items()
                if spec.count(declaration) != 1]                                           # P1, G2
    problems += [f'C_API subtype differs: {line}' for line in CAPI_C_API_SUBTYPES if spec.count(line) != 1]
    for name in ('U8', 'U32', 'I64', 'Size'):                                              # P2
        declared = len(re.findall(rf'\b(?:sub)?type {name} is\b', spec + ' ' + body))
        objects = len(re.findall(rf"(?<![\w.']){name}\s*:", spec + ' ' + body))
        if declared != 1 or objects:
            problems.append(f'C_API declares {name} more than once')
    return problems


def _capi_order_problems(root: Path) -> list[str]:
    problems = []
    for (relative, kind, name), tokens in CAPI_ORDERED.items():                           # O1, O2, O4, O5
        unit = _capi_isolate(_capi_text(root, relative), name, kind)
        if not unit or not _capi_ordered(unit, tokens):
            problems.append(f'{relative}:{name}: ordered decision path differs')
            continue
        for token, expected in CAPI_COUNTS.get((relative, kind, name), {}).items():       # O3
            if unit.count(token) != expected:
                problems.append(f'{relative}:{name}: {token!r} occurs {unit.count(token)} times, not {expected}')
    return problems


def _capi_diagnostic_problems(root: Path) -> list[str]:
    if not CAPI_DIAGNOSTIC_SITES:
        return []
    body = _capi_text(root, 'core/worldline-c_api.adb')
    unit_spec = _capi_text(root, 'core/evaluation_completion_c.ads')
    unit_body = _capi_text(root, 'core/evaluation_completion_c.adb')
    problems = []
    for (relative, kind, name), sites in CAPI_DIAGNOSTIC_SITES.items():                   # D3
        unit = _capi_isolate(_capi_text(root, relative), name, kind)
        if tuple(CAPI_DIAGNOSTIC_CALL.findall(unit)) != sites:
            problems.append(f'{name}: diagnostic site sequence differs')
    transport = _capi_isolate(body, 'Diagnostic_Transport', 'package')
    mark, text = _capi_isolate(transport, 'Mark'), _capi_isolate(transport, 'Exception_Text')
    for token, home in (('Ada.Text_IO.Put_Line', mark), ('Ada.Text_IO.Flush', mark),
                        ('Standard_Error', mark), ('Ada.Exceptions.Exception_Information', text)):  # D2
        if not home.count(token) or body.count(token) != home.count(token):
            problems.append(f'{token} occurs outside its diagnostic transport procedure')
    if 'with Atomic' in body or re.search(r'Diagnostic_(?:Active|Failed)\b', body):        # D1
        problems.append('diagnostic state appears in the boundary')
    if (unit_body.count('Diagnostic_Active : Boolean := False with Atomic;') != 1
            or unit_body.count('Diagnostic_Failed : Boolean := False with Atomic;') != 1
            or 'Abstract_State => (Diagnostic_State with External)' not in unit_spec):     # D5
        problems.append('SPARK diagnostic state declarations differ')
    for word in ('Ada.Text_IO', 'Ada.Exceptions'):                                          # G8
        if word in unit_spec or word in unit_body:
            problems.append(f'{word} remains in Evaluation_Completion_C')
    return problems


_capi_predecessor_export_problems = export_problems


def export_problems(root: Path) -> list[str]:
    problems = _capi_predecessor_export_problems(root)                                     # PP3
    for check in (_capi_closure_problems, _capi_component_problems, _capi_profile_problems,
                  _capi_order_problems, _capi_diagnostic_problems):
        problems += check(root)
    return problems
```

Notes on the sketch:
- **G6 (old-spec absence)** follows from the closure check. Each symbol must occur exactly once, at its `CAPI_CORE_HOME` entry, so any occurrence in the old spec fails.
- **Isolation failure is a problem, never a skip.** An empty isolation fails `_capi_ordered`. The one exception is a unit whose token list is empty, and no unit has one.
- **Mutation controls (§8.8, C-09).** These run each mutation in a temporary copy of the stage tree and expect at least one problem. They read text only and never build or run WORLDLINE code.
- **Limits.** What these checks do not establish is listed in §8.9.
