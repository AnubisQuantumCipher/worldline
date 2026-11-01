The 70-file cut closes the previously missing **source-level reference/context and AST-schema inputs**. It does not yet support an unmodified xgen build: the exact parent `Why` unit and GNATcoll development closure are missing locally.

Let `I` denote `records/phase1-direct/completion-20261026/old-retirement-interface-source-cut-v1/`; let `C` denote `old-retirement-fresh-owner-source-closure-fetch-v1/`, both under the carrier’s `completion-20261026`.

- **Typed references:** `I/src/why/why-gen-expr.ads:807` defines `Ref_Type = {Mutable, Name, Value}` and `Ref_Context` as a vector. `why-gen-expr.adb:354` folds that vector in reverse, emitting `New_Binding_Ref` for mutable entries and asserting `EW_Prog | EW_Pterm`. It supplies binding order and scope; it supplies no successful-initialization enrollment, ownership registry or cleanup.
- **Transformation context:** `I/src/why/gnat2why-util.ads:456` defines only `Phase`, `Gen_Marker`, `Ref_Allowed`, `Old_Policy`, and `Warn_On_Dead`. Ownership state cannot be inferred from this record.
- **Complete-value representation:** `I/src/why/why-gen-binders.ads:97` separates object values from optional initialization, move-tree and validity flags. `Mk_Tmp_Item_Of_Entity` at line 325 creates a `Regular` item with those flags absent. A temporary mutable binder alone therefore cannot establish borrow-permission or allocated-part ownership integration. `Reconstruct_Item` at `why-gen-binders.adb:1449` handles split records, arrays and pointers; treating every complete value as one scalar reference would discard representation obligations.
- **Constructors:** `I/src/why/xgen/xtree_sinfo.adb:489` specifies `W_Binding_Ref` fields `Name`, `Def`, `Context`, and `Typ`. Lines 571–576 specify `W_Try_Block` with `Prog`, a **nonempty** handler collection, and optional `Typ`; lines 200–205 specify handler name, optional exception argument and program body. `xtree_tables.adb:90` turns list fields into array parameters; `xtree_builders.adb:209` emits nonempty-list checks. There is no automatic `finally` node in this schema. Generated overload declarations/bodies remain UNRUN.
- **Pinned baseline discriminator:** `xtree_sinfo.adb:206` sets `W_Handler`’s domain to `EW_Prog`, then line 216 sets that same kind to `EW_Term`. `xtree_tables.adb:577` overwrites the stored domain. Preserve and observe this exact baseline behavior; do not silently “correct” it while qualifying O1.

The retirement design must still satisfy these contracts:

1. Enroll a distinct physical owner **only after successful initialization**, preserving native capture order and conditional evaluation. A later initializer failure must retire previously enrolled owners.
2. Keep that owner alive through all postcondition uses. `C/src/why/gnat2why-subprograms.adb:6492` performs existing local finalization **before** body postconditions and subsequent checks; `Declare_Old_Variables` wraps the assembled program at line 6868. Adding fresh-`Old` cleanup only to existing `Finalization_Actions` would be too early.
3. Cover normal completion, postcheck failure and exceptional exits. Existing named exception handlers re-raise after their work (`gnat2why-subprograms.adb:6549–6591`); a trailing cleanup statement cannot cover those paths.
4. Preserve real checked-call semantics. The retained exact `fsf-gnat2why-expr.adb:18370` private lowering routine requires an actual Ada call node and computes actual/formal arguments, stores, refinement, preconditions, invariants, variants, termination and exceptional propagation. `Why.Gen.Expr.New_Function_Call` at `I/src/why/why-gen-expr.adb:5004` is a lower-level builder; its `Check` branch supplies a precondition VC, not that complete call path.
5. Preserve independent ordinary assignment/Adjust semantics. Existing assignment leak checks remain at retained `fsf-gnat2why-expr.adb:16625`; the original allocating-assertion static leak failure remains at lines 24008–24029.
6. Keep physical enrollment independent of logical `Map_For_Old`: retained `Transform_Attribute_Old`, lines 16887–16892, bypasses the map for prefixes without proof variables. Logical-map membership cannot establish physical lifetime.

For xgen, `I/src/why/xgen/helpers.gpr:1` imports `gnatcoll_core`; `xtree_decls.adb:26` uses `GNATCOLL.Utils`, specifically `Starts_With` at lines 74 and 80. The exact source set is **62 files / 360,275 bytes**, including **39 Ada files and 21 templates**, plus `why-sinfo.ads` (**26,389 bytes**). The missing parent is:

`AdaCore/spark2014@b9410c6ed36d4e69a6c4d31e152fa8facaf0235c:src/why/why.ads`, blob `1853905acc5d03980a1047332a19618d707d6abc`, **2,499 bytes**.

No GNATcoll files were found under `/home/sicarii/opt/gnat`; the four checked system/user GPR directories are absent. A bounded Work search excluding overlays also found no `why.ads` or GNATcoll SDK units. This is bounded local absence, not a universal filesystem claim.

The exact next metadata task is **one** registered GET:

`https://api.github.com/repos/AdaCore/gnatcoll-core/git/trees/1d4374ae9187fd14d42ca99a3deb0ab2ff1ebc55?recursive=1`

Proposed limits: **1 request, 512 KiB response body, 10 seconds, no retry or redirect**. Persist the response durably immediately; require complete valid JSON and `truncated=false` before selecting sources. Record the prior eight-query history and failed persistence boundary; this is a separately registered recovery, not a reset.

Select all blobs under `core/` and `minimal/`, plus the three `gprproject` helpers, root Makefile and any explicitly selected root build/license files. Reuse the **10 retained exact GNATcoll payloads**; do not fetch them again. Prior complete observations give `core/ + minimal/` as **271 paths / 3,293,604 bytes**, with six reusable project/config/wrapper bodies totaling **28,619 bytes**. Thus the broad missing prerequisite body candidate is **265 GNATcoll files / 3,264,985 bytes**, plus `why.ads`: **266 files / 3,267,484 bytes**. These counts must be reconciled against the newly durable complete mapping before body authorization. Optional root glue/licenses increase that explicit selection.

Once prerequisites exist, a separately admitted isolated build can invoke `gprbuild -j2 -p -Phelpers xtree`, preserving `-gnata` and adding validity checks as recorded flags. Do not invoke the nested Makefile’s `-j0` or copy generated outputs into the evidence source packet. Xgen writes **21 outputs**, including the 20 Makefile-listed Ada outputs and `gnat_ast.ml`.

Known generator source bytes total **389,163** with schema and parent. Object, executable, generated-output, temporary and recovery peaks remain **UNMEASURED**; no qualified total build-space estimate exists. Admission must impose finite output limits and retain failure evidence.

First xgen acceptance requires exact input/tool/flag provenance, complete diagnostics, all 21 outputs, no unresolved template markers, repeat-generation byte equality and readback. Xgen success would establish neither translator build closure nor O1 semantics. The first future full translator baseline must still reproduce **unchanged D47 static-leak failures** before any semantic patch receives credit. Installed correspondence remains **UNKNOWN**. No writes, network, generation, builds or proofs occurred in this analysis.
