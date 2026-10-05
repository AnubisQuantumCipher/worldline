# C-API boundary consolidation v4: Appendix A-COST (source and native cost map, type- and call-site-resolved)

| | |
|---|---|
| Companion to | `DESIGN.md` in this directory (design v4). `§n` means a section of DESIGN.md; `A-BIND §x` means a section of `APPENDIX-BINDINGS.md`. |
| Supersedes | v3 `APPENDIX-COST-MAP.md` (sha256 `c2a320a266fdd088c203e0d61f4cd7c5ea94f7b3b731f5be400f6b2f3d5b114f`, 48792 bytes). |
| Status | DRAFT_FOR_GPT61_REVIEW. **PROPOSAL ONLY.** Every native item in this map is **OPEN**. The source items are readings of S5 and of the design text. They are not native facts, and none closes an obligation. |
| Base | S5 = `W/work/claude-composition-v5-beta/source`. Line citations are S5 lines (identical to S4 for the files cited). The installed tool trees are G = `/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1` and GN = `/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1`. |
| Answers | V3-RC6. It corrects the diagnostic `Fits` counts (C18) and the run-ledger actual classification (C12). It separates source evaluation and construction points from emitted native calls, checks, copies, storage, elision and lifetimes in every row (C0). It withdraws the categorical "it executes", mandatory Ri copy/storage and "-O0 no temporary is elided" statements (C1.2). It restricts every `ALLOC =` to the original allocations it names, and gives one construction account per write form (C19, aligned with A-BIND §B10). D-36 and every original native blocker stay OPEN (C19–C21). |

**Method and limits.**
- **Source reading only.** Every row comes from reading S5, the design text and the installed GNAT User's Guide. Nothing was compiled, executed, measured or disassembled, and no generated code was inspected.
- **Two layers, never merged.**
  - The **source layer** states what the source text and the language semantics fix: which calls are written, how many times a predicate is evaluated on a stated path, which objects and function results the source creates, which language-defined checks the source semantics requires, which allocations are declared, and the source order of reads and writes.
  - The **native layer** states what only matching generated code can settle: emitted calls or inlining, emitted or removed checks, passing mechanisms, temporaries, copies, elision, storage place, size and lifetime, validity checks and failure thresholds. **Every native item is OPEN** and is closed only by the C21 evidence.
- **Units (D2 review correction C-UNIT, applied).** A source count in this map counts source evaluation points on a stated path. It is not a count of allocations, machine instructions or emitted calls.
- **No improvement claims (D2 review correction C-COPY, applied).** No row claims that the successor uses fewer native copies, less storage or shorter lifetimes. Such an improvement cannot be established statically.
- **What this map is.** It enumerates where the successor can differ natively from the original. It does not say how much it differs, and it does not establish that any difference is acceptable.
- **The obligation stays fixed.** A difference that makes an originally accepted computation fail, for example by exhausting storage at a smaller input, is a failure of the obligation. It is never an accepted refusal (§3.5; H/HANDOFF.md:129-131).

---

## C0. Legend (REVISED in v4: source and native layers separated)

**Type categories of parameters (RM 6.2).** These are language rules. The choice the language leaves open is native.

| Mark | Meaning |
|---|---|
| **E** | Elementary type: passed by copy (RM 6.2(3)). |
| **U** | Untagged, non-limited composite with no by-reference subcomponent: the passing mechanism is **unspecified** (RM 6.2(11)). Which mechanism GNAT chooses for the matching build is native and OPEN (N-PASS). By-copy passing of an array or large record would add a copy per call; by-reference passing would not. No row claims "no copy". |
| **R** | By-reference type (RM 6.2(4-9)): tagged, task, protected, explicitly limited, or containing one. **None was identified** (C2). |

**Function results.**

| Mark | Source meaning | Native counterpart (OPEN) |
|---|---|---|
| **Rd** | Definite result: a constrained record, a record with defaulted discriminants, or a constrained array. The source creates one result per call. | Whether the result is built in place in its target, built in a temporary and copied, and where any temporary lives (N-OBJ, N-COPY). |
| **Ri** | Indefinite result: an unconstrained array, `String`, or a record with discriminants and no defaults. The function determines the bounds or discriminants. Initializing or assigning a **constrained** object from it includes the language-defined length or discriminant check of the subtype conversion. | The installed GNAT User's Guide states that the secondary stack "holds objects of unconstrained types that are returned by functions" (GN `share/info/gnat_ugn.info:11252-11260`). Whether a given result in the matching build uses it, whether it is copied into its target, and its lifetime are OPEN (N-OBJ, N-COPY, N-LIFE). v3's statement that every Ri result "is returned on the secondary stack and copied into its target" is withdrawn (C1.2). |

**Source-layer delta marks.**

| Mark | Meaning |
|---|---|
| **S-CALL** | A call written in the successor source that the original did not have (for example a value routine replacing an inline comparison). |
| **S-RECHECK** | A predicate the successor source evaluates again (V3 totality re-checks, the LD5 wrapper). It is dead on transport paths: the value is the one the chain just accepted. |
| **S-OBJ** | An object or function result the successor source creates that the original did not have (acceptance results and the constants they initialize, result constants, function results that replace aggregates). |
| **S-ASSIGN** | A source assignment the original did not have, or one that replaces a direct aggregate or function-result store. |
| **S-CHECK** | A language-defined check that the source semantics requires at a new place (X3; the subtype conversion of an Ri result into a constrained object). No check is suppressed in any build. |
| **S-INIT** | A new or moved initialization (D-28). |
| **S-ASSERT** | A new evaluation under `-gnata` in chk or comp. An existing contract evaluated as often as before is marked `=`. |
| **S-ALLOC** | The allocation statements written in source: object declarations sized by caller counts and the result arrays of copy functions. **`ALLOC =` means only that the original allocation statements named in the row are kept at the same source position, in the same order and with the same bounds.** It says nothing about S-OBJ objects, which are listed separately, or about native storage. |
| **EXC/WRITE** | The source-level exception mapping and write order. The defined effects, including handled internal exceptions, are classified in §9.6. |
| `=` | Unchanged in source, as far as reading shows. |

**Native-layer marks (all OPEN).** N-CALL (emitted call or inlining), N-CHECK (emitted test or its removal), N-PASS (mechanism for U actuals), N-OBJ (existence, size and place of storage for objects and results; build-in-place; elision), N-COPY (copies), N-LIFE (storage lifetimes), N-VALID (validity checks under `-gnatVa`), N-ASSERT (emitted assertion code), N-ALLOC (native storage use and failure thresholds within the originally accepted domain).

**Builds (observed switches).**
- rel: `-gnat2022 -gnatwa -gnatVa -gnatf -O2 -g -fPIC` (`core/worldline_core_sources.gpr:11-12`).
- chk: rel plus `-gnata` (`:16-17`); the default build (`:9`).
- comp: the pending component, `-gnat2022 -gnata -gnatVa -gnatwa -g -O0` (`pending-component/pending.gpr`).

### Cross-cutting deltas (REVISED in v4)

These apply to every new SPARK call and are not repeated in each row.

| Id | Source layer | Native layer (OPEN) | Basis |
|---|---|---|---|
| X1 | Each new value-routine call is a source call from `Worldline.C_API` into another compilation unit (the unit's SPARK specification). | Whether each such call is emitted as a call or inlined is OPEN. The installed User's Guide gives the ordinary conditions for inlining calls into `with`ed units: at least `-O1`, `pragma Inline` on the subprogram, and `-gnatn` (GN `gnat_ugn.info:14798-14835`). The core builds use `-O2` without `-gnatn`, the design adds no `Inline` aspect, and the component build uses `-O0`. Some value routines are completed as expression functions in the visible part of the unit specification (§3.2 V2); the same Guide lists expression functions among the conditions for inlining calls **within the current unit**. That documentation describes ordinary behaviour. It is not object-code evidence for any call site (C21-a, C21-h). v3's "every new value-routine call is a real call" is withdrawn (C1.2). | §3.2 V2; GN `gnat_ugn.info:14798-14835` |
| X2 | The core builds use `-gnatVa`. | Validity checks may be generated at new parameter, result and copy boundaries. Their placement is compiler-chosen and OPEN (N-VALID). | core switches |
| X3 | Each selection of a component in the variant part of an acceptance record (`D.Item`, `RA.Row`, and so on) is subject to the language-defined discriminant check of component selection (RM 4.1.3). No check is suppressed in any build. R-GATE (A-BIND §B0.7, §B10.3) makes the discriminant test precede every such selection, so the check's condition holds on every transport path. | Whether the matching code emits a test for that check, or removes it as redundant after the dominating `if not D.Ok` test, is OPEN (N-CHECK). v3's "but it executes" is withdrawn (C1.2). | RM 4.1.3; A1 (§3.2 V4); R-GATE |
| X4 | Each acceptance call creates one function result of a definite discriminated record type, which initializes a declared constant (`D : constant … := Accept_…(…)`). Per-row acceptance therefore adds one such object per iteration in source. | Whether the result is built in place in the constant or in a temporary, the size of any storage (largest variant or actual variant; RM 3.7 and 3.8 do not fix it) and its place and lifetime are OPEN (N-OBJ, N-LIFE). | RM 3.7, 3.8 |
| X5 | No new routine has a `Pre` or a functional `Post` (LD2), so `-gnata` evaluates no new contract of a new routine. Existing contracts of called relations are evaluated once per call wherever the relation is called; the rows list each such call and mark it `=` when the count is unchanged. The one new evaluation is the `History_Index` Post (C15). | Emitted assertion code and its cost are OPEN (N-ASSERT, C21-f). | LD2 |

---

## C1. Withdrawn statements

### C1.1 Withdrawn v2 statements (carried from v3, unchanged)

| v2 text (line) | Status |
|---|---|
| "**Arrays are not copied into SPARK.** They are passed by reference as `in` or `in out` formals." (v2:2510) | Withdrawn. Array mechanisms are unspecified (U), and each array actual is listed per site below. |
| "Every existing relation is called with the same arguments and as many times as on the original path, with the three constant-time exceptions in §10.3." (v2:2503) | Withdrawn. Re-evaluations are listed per site below; there are more than three. |
| "\| all other exports \| 0 \| n/a \| n/a \|" (v2:2537) | Withdrawn. Every export has at least the X1–X4 deltas, and most have site-specific ones. |
| "Both `Well_Formed` relations are bounded and constant-time" (v2:156) | Withdrawn as a cost claim. Source reading shows field and digest checks that do not depend on array lengths, but nothing was measured (C5, C6). |
| "Each per-element acceptance returns a small discriminated record by value, which adds one element-sized copy per row" (v2:2543) | Kept in substance as a source fact (X4) and resolved per site. Storage and copies are native and OPEN. Elements such as `F.Start_Row` and `T.Result_Record` are not small. |
| D-36 "That aligns with the documented no-write-on-refusal contract … The reviewer is to confirm it is equal-or-stronger behaviour." (v2:2648) | Withdrawn as a request for confirmation. D-36 is OPEN for every export in C19. |

### C1.2 Withdrawn or restated v3 statements (new in v4; V3-RC6)

Each quotation is the exact v3 text. "A-COST v3:n" is line n of the v3 `APPENDIX-COST-MAP.md`; "DESIGN v3:n" is line n of the v3 `DESIGN.md`.

| v3 text (line) | Status in v4 |
|---|---|
| "It is returned on the secondary stack and copied into its target with a length or discriminant check." (A-COST v3:25, Ri) | Withdrawn as a native claim. Restated in C0: the source fact is the subtype-conversion check into a constrained object; storage and copy are OPEN. |
| "Every new value-routine call is a real call across compilation units: the builds have no `-gnatn` and no `Inline` aspect is added. There is a call and return, and argument passing per call." (A-COST v3:39, X1) | Withdrawn. Restated in X1: a source call, with the documented ordinary inlining conditions cited and the emitted code OPEN. |
| "Rule A1 makes it always pass, but it executes." (A-COST v3:41, X3) | Withdrawn ("it executes"). Restated in X3: the source semantics requires the check; whether a test is emitted is OPEN. |
| "Its temporary is sized either for the largest variant or for the actual variant, at the implementation's choice (OPEN), so per-row acceptance adds one such temporary per iteration." (A-COST v3:42, X4) | Restated in X4: one source object per iteration; any temporary is native and OPEN. |
| "`=`. The four secondary-stack results exist as before." (A-COST v3:104, C3 row 3) and "their lifetime is the return expression instead of the `if` condition" (A-COST v3:108) | Restated in C3: the same four source results; storage place and lifetime OPEN. |
| "COPY: each present marker's bytes now live as a transport constant (secondary stack) until `Select_Value` returns." (A-COST v3:117) and "returned on the secondary stack and copied into a constrained constant with a discriminant check" (A-COST v3:119) and "peak secondary-stack and stack use grows by up to one extra copy of each present marker" (A-COST v3:122) | Restated in C4: the source objects and their block lifetime are stated; the storage place and any peak growth are OPEN. |
| "which the original unit's own `-O2` could inline (OPEN). The result is copied into foreign memory, as before." (A-COST v3:185, C9 row 4) | Restated in C9: the documented ordinary inlining conditions differ for the same-unit and cross-unit calls; neither is object-code evidence. The store is a WF-F direct store (A-BIND §B10). |
| "COPY: a result temporary, then a copy (C19)." (A-COST v3:186, C9 row 5) | Withdrawn. The successor stores the `Result_Of` function result directly through the access value (WF-F), as the original stored an aggregate directly. Construction is native and OPEN (C19). |
| "ALLOC: `=`." (A-COST v3:191, C9) | Restricted. In C9 `ALLOC =` covers only the named original allocations (`Arena`, `Typed_Rows`, `Slots`, `Detail_Arena`, `Total_Arena`, `Typed_Details`; `Arena`, `Output_Arena`). The acceptance objects and the WF-F function results are listed separately, with native storage OPEN. Every other `ALLOC` line is restricted the same way. |
| "The decoded query lives across the row loop (stack)." (A-COST v3:208) | Restated in C11 without "(stack)": the source lifetime is the block; storage is OPEN. |
| "COPY: five array actuals pass one extra call level (mechanism U), plus the acceptance temporary." (A-COST v3:219, C12) | Corrected in C12. `Check_Decision` has four array actuals (`Data`, `Before`, `Proposed`, `Observed`; JACKAL J10 `parsed=1+2+1` → `exact=4`) and one record actual (`Raw`), five actuals in all (JACKAL J11 `parsed=4+1` → `exact=5`). |
| "At `-O0` no temporary is elided; the effect is OPEN." (A-COST v3:240, C14) | Withdrawn. Nothing is claimed about elision at any optimization level (C14). |
| "`=` (a completed local written once)" (A-COST v3:254, C15 row 7) and "The same pattern (a completed object copied once) plus one temporary; C19." (A-COST v3:295, C16 row 6) | Restated per write form (WF-R, WF-X) as source assignments; copy counts OPEN (C19). |
| "ALLOC for all completion units: `=` (every caller-count-sized array keeps its position, §3.5)." (A-COST v3:282) | Restricted to the named original arrays (C15). |
| "One length test, one call, a secondary-stack result (the original's catenation was also a temporary)" (A-COST v3:348); "**+1 `'Image` per active value site**, plus a length test." (A-COST v3:349); "One length test, one call" (A-COST v3:350) | Corrected in C18. Each reached fitting pair is two source predicate evaluations, one in the `Begin_*` procedure and one in the guarded composer (JACKAL J06 `parsed=1+1` → `exact=2`). The nested `Mark` has its own active gate and its own `Line_Fits` pair. The `'Image` delta (+1; JACKAL J09 `parsed=2-1` → `exact=1`) is kept. Storage of the `String` results is OPEN. |
| "the successor completes a SPARK result first and copies it once" for "policy, ledger details/result" (DESIGN v3:267) | Corrected (§3.4, C19). Policy and ledger details/result are WF-F: the SPARK function result is stored directly through the access value. |
| "Text is composed through SPARK functions returning `String` on the secondary stack; the original catenations also used it." and "Cross-unit calls are not inlined under the core switches" (DESIGN v3:668-669) | Restated in §4.9 v4 per C18 and X1. |
| "Indefinite results (`String`, unconstrained arrays, `Optional_Marker` in S5) are returned on the secondary stack and copied into constrained targets with a discriminant or length check." and "Cross-unit calls are therefore real calls." (DESIGN v3:2074, :2077) | Restated in §11.2 v4 per C0 and X1. |

---

## C2. Type classification (carried from v3; two cells reworded)

**Observations by grep over the involved specs:**
- No type declaration contains `tagged`, `limited`, `task`, `protected` or `Controlled`.
- `Big_Integer` occurs only as the result or parameter type of specification and ghost functions, never as a record component. Examples: `resource_quantities.ads:40-93`, `resource_ledger.ads:100-221`, `resource_admission.ads:77`.
- No type carries `Volatile`, `Atomic` or `Independent`. The two `Atomic` objects are `Boolean` (`core/evaluation_completion_c.adb:39-40`).
- So no by-reference (R) type was identified. That is a reading of the declarations, not a whole-closure proof. The deepest component traced is `Worldline.Hash`, a subtype of `Attest.SHA256.Digest`, itself a constrained subtype of `Byte_Array` (`core/attest/attest-sha256.ads:16`).

| Type | Declared at | Kind | Category | Note |
|---|---|---|---|---|
| `Interfaces.Unsigned_8`, `Unsigned_32`, `Integer_64`, `Interfaces.C.size_t`, `Interfaces.C.int`, `Boolean` | predefined | scalar | E | — |
| `System.Address` | `G/…/adainclude/system.ads:67` (private), `:117` (full type `mod Memory_Size`) | private type with a modular full type | E | — |
| Enumerations: `Recovery_Action`; `Resource_Reservation_Lifecycle.Operation`, `Liveness`, `Result_Status`; `Resource_Ledger.Result_Status`; `Worldline.Evaluation_Authority.Raw_Dependency`; `Context_Field`; `Row_Field`. New: `Diagnostic_Control_Kind`, `Context_Row_Verdict`, `Join_Verdict`, `Evaluation_Finalization_C.Source_Kind` | `worldline-recovery.ads:24`; `resource_reservation_lifecycle.ads:26`, `:19`, `:27`; `resource_ledger.ads:160`; `worldline-evaluation_authority.ads:19`, `:102`, `:108`; new types per §4.2, §5.2, §7 | enumeration | E | — |
| `Worldline.Resources.Byte_Array` | `worldline-resources.ads:15` | unconstrained array of `Unsigned_8` | U | Results are Ri |
| `Worldline.Recovery.Identity_Bytes` | `worldline-recovery.ads:8` | unconstrained array | U | Results are Ri |
| `Worldline.Recovery.Optional_Marker` | `worldline-recovery.ads:9-16` | discriminants `(Present : Boolean; Length : Byte_Count)` **without defaults** in S5 | U | **Indefinite**; results are Ri. Initializing a constrained object from one includes the language-defined discriminant check (v4 wording). |
| `Resource_Quantities.Byte_Array` (= `Evaluation_Pending.Bytes`; `Q.Byte_Array`) | `resource_quantities.ads:9`; `evaluation_pending.ads:11` | unconstrained array | U | — |
| `Resource_Quantities.Quantity` | `resource_quantities.ads:13-17` | record `(Negative : Boolean; First : Byte_Index; Length : Byte_Count)` | U | No `Big_Integer` component |
| `Resource_Quantities.Optional_Quantity` | `resource_quantities.ads:18` | defaulted discriminant | U | Definite |
| Wire records `Raw_Request` / `Raw_Result` (v2, v3, protocol) | `worldline-recovery_authorization_wire.ads:52`, `:57`; `…_v3_wire.ads:64`, `:70`; `worldline-recovery_protocol_wire.ads:6`, `:9` | record | U | — |
| `Worldline.Reservation_Lifecycle_C_API.Row_C`; `Reservation_Entry`; `Optional_Identity`; `Entry_Array`; `Removal_Array` | `worldline-reservation_lifecycle_c_api.ads:12`; `resource_reservation_lifecycle.ads:20`, `:13` (defaulted discriminant), `:24`, `:25` | record and array | U | — |
| Ledger and policy C records `Row_C`, `Result_C`, `Quantity_C`, `Optional_C`, `Input_C`, `Disk_C`, `Result_C` | `worldline-resource_ledger_c_api.ads:15`, `:21`; `worldline-resource_policy_c_api.ads:12`, `:17`, `:21`, `:33`, `:37` | record | U | — |
| `Resource_Ledger.Reservation_Row`, `Output_Span`, `Reservation_Array`, `Quantity_Array`, `Span_Array` | `resource_ledger.ads:9`, `:15`, `:13`, `:14`, `:19` | record and array | U | — |
| `Resource_Admission.Disk_Row`, `Disk_Array`, `Policy_Input`, `Decision` | `resource_admission.ads:8`, `:12`, `:20`, `:50` | record and array | U | — |
| History C records `Row_C`, `Query_C`, `Selection_C`; `Evaluation_History.Evaluation_Record`, `Optional_Record`, `History`, `Query`, `Selection` | `worldline-evaluation_history_c_api.ads:24`, `:29`, `:33`; `evaluation_history.ads:114`, `:123` (defaulted discriminant), `:129`, `:131`, `:156` | record and array | U | — |
| Pending C `Row`, `Request`, `Result`; `Evaluation_Pending.Intent`, `Journal`, `Plan`; v2 equivalents | `evaluation_pending_c.ads:15`, `:21`, `:30`; `evaluation_pending.ads:26`, `:32`, `:39`; `evaluation_pending_v2_c.ads:19`, `:26`, `:36`; `evaluation_pending_v2.ads:21`, `:25`, `:49` | record and array | U | — |
| Run-ledger wire `Raw_Packet`, `Raw_Result`, `Raw_Row`, `Raw_Native`, `Raw_Row_Array`, `Raw_Native_Array` | `resource_run_ledger_wire.ads:96`, `:102`, `:52`, `:74`, `:105`, `:106` | record and array | U | `Raw_Packet` and `Raw_Result` are records; the two `…_Array` types are arrays (C12) |
| Chain `Raw_Row`, `Raw_Anchors`, `Raw_Result`; `Chain_Row`; `Retained_Rows` | `worldline-chain_authority_wire.ads:17`, `:20`, `:24`; `worldline-chain_authority.ads:16`, `:19` | record and array | U | — |
| Completion C records `Journal_Row`, `Required_Row`, `Check_Row`, `History_Row`, `Request`, `Result`, `Context_Row`, `Context_Input`, `Row_Metadata`, `Metadata_Context` | `evaluation_completion_c.ads:44`, `:78`, `:82`, `:96`, `:105`, `:130`, `:163`, `:167`, `:195`, `:199` | record | U | `Request`, `Result` and `Context_Input` are large records; their sizes are not computed here (OPEN) |
| `Evaluation_Completion.Result_Record`, `Result_Array`; roster `Measured_Result`, `Measured_Array`, `Required_Check`, `Check_Array`; raw roster `Measured_Result`, `Measured_Array` | `evaluation_completion.ads:73`, `:83`; `evaluation_completion_roster.ads:12`, `:19`, `:20`, `:24`; `evaluation_raw_roster.ads:19`, `:25` | record and array | U | — |
| `Worldline.Evaluation_Authority.Optional_Bytes`, `Context_Fields`, `Context_Row`, `Context_Rows`, `Row_Metadata`, `Row_Metadata_Array`; `Worldline.Evaluation_Wire.Raw_Record` | `worldline-evaluation_authority.ads:96` (defaulted discriminant), `:107` (constrained by its enumeration index, so definite), `:113`, `:118`, `:245`, `:249`; `worldline-evaluation_wire.ads:29` | record and array | U | — |
| Finalization C `Row`, `Request`, `Result`; `Evaluation_Finalization.Start_Row`, `Start_Rows`; `Worldline.Collapse_Wire.Raw_Request` | `evaluation_finalization_c.ads:32`, `:41`, `:57`; `evaluation_finalization.ads:60`, `:72`; `worldline-collapse_wire.ads:33` | record and array | U | `Start_Row` has enumeration and variant components |
| New acceptance records (every `*_Acceptance`, `Decide_Acceptance`, `Context_Fields_Acceptance`, `Context_Row_Acceptance`) | §5, §7 | defaulted `Boolean` or enumeration discriminant | U | Definite and mutable; storage OPEN (X4) |
| `Readiness_Result` (moved) | from `evaluation_finalization_c.adb:366-369` | record `(Valid : Boolean; Ready : U8)` | U | — |
| `String` | Standard | unconstrained array | U | Results are Ri |

---

## C3. U1 `wl_resources_can_reserve`

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `Negative_Flag_Valid (Available_Negative)` in the guard | `worldline-resources_c_api.adb:45` (inline `> 1`) | U8 E → Boolean E | S-CALL replacing an inline comparison | N-CALL (X1) |
| 2 | `Valid (…)` ×4 | `:46-49` | E | `=` (verbatim transport text, hash-bound, A-BIND §B9.3) | code identity of the relocated helper (D-15) |
| 3 | `Decode (…)` ×4 | `:55-58` | E → `Byte_Array` Ri | `=`: the same four source calls and four Ri results. They are now actuals of `Can_Reserve_Value` inside a return expression instead of actuals of `Resource_Wire.Can_Reserve` inside an `if` condition; their mutual evaluation order is unspecified in both. | N-OBJ, N-LIFE for the four results |
| 4 | `Can_Reserve_Value (Available_Negative, 4 arrays)` | new, wrapping `:53-62` | U8 E; 4 × `Byte_Array` U → U8 E | S-CALL; S-RECHECK of the flag (V3). Each array is an actual at two call levels in source (`Can_Reserve_Value`, then `Resource_Wire.Can_Reserve`). The `Available_Negative = 1` actual is computed inside SPARK. | N-PASS at each level (a by-copy choice would copy each array once more); N-CALL |
| 5 | `Worldline.Resource_Wire.Can_Reserve` | `:53-58` | as original | `=` (one call). Its Post (`worldline-resource_wire.ads:11`) is evaluated once in chk, `=`. | — |

ALLOC (restricted): the original allocates only the four `Decode` results; the successor's source creates the same four, `=`. EXC/WRITE: no writes; the handler `:63-64` is `=`.

## C4. U2 `wl_recovery_select`

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `Presence_Valid` in the guard | `worldline-recovery_c_api.adb:61` (inline) | 2 × U8 E → Boolean E | S-CALL | N-CALL |
| 2 | `Present (Live_Present)`, `Present (Prepared_Present)` in the guard | `:63-64` (inline `= 1`) | U8 E → Boolean E | S-CALL per marker | N-CALL |
| 3 | `Copy (Expected, Expected_Length)` | `:69-70` | E → `Identity_Bytes` Ri | `=` | — |
| 4 | `Live_Value`, `Prepared_Value`: `(if Present (Flag) then Copy (…) else Empty)` | `:71-79`; the original copied inside `Marker` (`:37-51`) | U8 E → Boolean; `Identity_Bytes` Ri | S-OBJ: each present marker's bytes are held in a transport constant whose source lifetime is the declare block, until `Select_Value` returns. S-RECHECK: one `Present` call per marker. | N-OBJ, N-LIFE (storage place and size of the constants) |
| 5 | `Select_Value (Expected_Value, Live_Present, Live_Value, Prepared_Present, Prepared_Value)` | new, wrapping `:71-82` | 3 × `Identity_Bytes` U; 2 × U8 E → U8 E | S-CALL; S-RECHECK: `Presence_Valid` (dead) and the two constraint expressions of the constrained marker constants | N-PASS for the three arrays |
| 6 | `Marker_Of (Flag, Value)` ×2, inside `Select_Value` | new, replacing `Marker` | U8 E; `Identity_Bytes` U → `Optional_Marker` **Ri** | S-OBJ: each call creates an `Optional_Marker` result whose `Value` component is assigned from `Value` (one source assignment of the marker bytes). It initializes a constrained constant, which includes the discriminant check (S-CHECK). S-RECHECK: one flag test each. `Present_Flag /= 1` is used for totality; it is equivalent for the flags 0 and 1 that the transport admits. | N-OBJ, N-COPY, N-CHECK |
| 7 | `R.Select_Action (…)` | `:82` | as original | `=` (one call). Its Post (`worldline-recovery.ads:33`) is evaluated once in chk, `=`. | — |

ALLOC (restricted): the `Copy` result for Expected (`:69-70`) is kept, `=`. The two constrained marker objects of `:71-79` are not `=`: they move into `Select_Value`, with the same constraints, and are initialized by `Marker_Of`. Not covered by `=` either: for each present marker the successor's source holds both the transport constant and the `Optional_Marker` built from it, where the original built only the marker from foreign memory. Whether this raises peak storage, and on which stack or heap, is OPEN (N-ALLOC). If it lowered the input size at which `Storage_Error` occurs, an originally accepted call would become 255, which is a **failure of the obligation** and not an accepted refusal (§3.5; C21-c, C21-d). EXC/WRITE: no writes; the handler is `=`.

## C5. U3 `wl_recovery_authorization_decide_v2`

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | guards, `Raw` capture | `worldline-recovery_authorization_c_api.adb:129-139` | — | `=` | — |
| 2 | `W.Well_Formed (Raw)` in the transport | `:141-143` | `Raw_Request` U → Boolean | `=` (one call) | — |
| 3 | `Owned : constant … := Decide_Total (Raw)` | new, around `:146` | `Raw_Request` U → `Raw_Result` Rd | S-CALL; S-RECHECK: one extra `W.Well_Formed (Raw)` (`worldline-recovery_authorization_wire.ads:104-112`) per accepted call, in every build. S-OBJ: the constant `Owned`. `W.Decide`'s Pre (`:166`) and Post (`:167`) are evaluated once each in chk, `=`. | N-CALL; N-OBJ (whether `Owned` has its own storage) |
| 4 | `Result_At (Output).all := Owned` | `:146` (`Result_At (Output).all := W.Decide (Raw);`) | — | WF-C (A-BIND §B10): one source assignment of a completed constant through the access value, where the original assigned the `W.Decide` function result directly. | N-COPY; construction and exception-path write behaviour (C19, D-36) |

**`Well_Formed (Raw)` source evaluations per accepted call** (each `Pre` evaluation counted under chk's assertion policy):

| Build | Original | Successor |
|---|---|---|
| rel | 1 | 2 (JACKAL J06 `parsed=1+1` → `exact=2`) |
| chk | 2 (JACKAL J06 `parsed=1+1` → `exact=2`) | 3 (JACKAL J07 `parsed=1+1+1` → `exact=3`) |

A call refused by `Well_Formed` performs one evaluation in both versions. These are source evaluations read from the call sites, not emitted instructions (C-UNIT). The JACKAL results are `status=exact`, `formal=false`.

## C6. U4 `wl_recovery_authorization_decide_v3`

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | guards, `Raw` capture, `Data` allocation and unconditional copy | `worldline-recovery_authorization_v3_c_api.adb:139-157` | — | `=` | — |
| 2 | `W.Well_Formed (Data, Raw)` in the transport | `:158-160` | `Q.Byte_Array` U, `Raw_Request` U → Boolean | `=` | — |
| 3 | `Owned : constant … := Decide_Total (Data, Raw)` | new, around `:163` | `Q.Byte_Array` U; `Raw_Request` U → `Raw_Result` Rd | S-CALL; S-RECHECK: one extra `W.Well_Formed (Data, Raw)` (`worldline-recovery_authorization_v3_wire.ads:164-173`) per accepted call. By source reading it runs field, digest and span checks, uses `Q.Span_Valid` against `Data'Length`, and does not iterate over the arena contents; nothing was measured. The array is an actual at two call levels in source. S-OBJ: `Owned`. `W.Decide`'s Pre (`:265`) and Post (`:266`) once each in chk, `=`. | N-PASS, N-CALL, N-OBJ |
| 4 | `Result_At (Output).all := Owned` | `:163` | — | WF-C, as C5 row 4 | C19, D-36 |

ALLOC (restricted): `Data` (`:152`) `=`. Evaluation counts per accepted call are those of C5 (rel 1 → 2; chk 2 → 3; the same JACKAL results).

## C7. U5 `wl_recovery_protocol_decide_v1`

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | guards, capture, `Owned_Result := (After => 0)` | `worldline-recovery_protocol_c_api.adb:49-59` | — | `=` | — |
| 2 | `Worldline.Recovery_Protocol_ABI.Apply (Raw, Owned_Result, Status)` | `:62` | `Raw_Request` U; `Raw_Result` U (`in out`); `C.int` E | `=`. It was already a call into another unit, and its Post (`worldline-recovery_protocol_abi.ads:20`) is evaluated once in chk. | — |
| 3 | `Result_At (Output).all := Owned_Result` | `:66` | — | `=`: WF-P, one source assignment of the local through the access value, as before | copy count OPEN, as it was for the original |

The only source change is location. Native correspondence of the relocated code is OPEN (D-15).

## C8. U6 `wl_reservation_lifecycle_plan`

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `Request_Valid (Present, Requested_First, Requested_Length)` in the guard | `worldline-reservation_lifecycle_c_api.adb:65-69` (inline) | U8, 2 × Size E → Boolean | S-CALL | N-CALL |
| 2 | `Requested := Requested_Of (…)` | `:81-85` (aggregate) | E → `Optional_Identity` Rd | S-CALL; S-RECHECK: `Request_Valid` again (V3; at most four comparisons). S-OBJ: a function result initializes the constant where the original used an aggregate. | N-OBJ |
| 3 | `Selected_Mode := Operation_Of (Mode)` | `:86-90` (case expression) | U8 E → `Operation` E | S-CALL | N-CALL |
| 4 | per row `D := Accept_Row (Row)`; `Typed_Rows (I) := D.Item` | `:98-105` | `Row_C` U → acceptance (`Reservation_Entry`) Rd | Per row: S-CALL, X3, X4, and one S-ASSIGN of `D.Item` (the original assigned an aggregate directly) | N-CALL, N-CHECK, N-OBJ, N-COPY |
| 5 | `L.Plan (…)` | `:108` | as original | `=`. `Mask` (WF-O) and `Status` are its `in out` and `out` actuals as before. Its Post (`resource_reservation_lifecycle.ads:103`) is evaluated once in chk. | — |
| 6 | `Publishes_Mask (Status)` | `:109` | E → Boolean | S-CALL | N-CALL |
| 7 | per mask byte `Mask_Byte (Mask (I))` | `:111-112` (`Boolean'Pos (Mask (I))`) | Boolean E → U8 E | **One S-CALL per mask byte** over a loop whose length the caller sets (`Removed_Length` ≤ `Byte_Count'Last`). WF-F: the function result is stored directly through the access value, as the original stored the attribute result directly. | N-CALL per byte (linear in the caller's length unless inlined) |
| 8 | `Status_Code (Status)` | `:115` | E → U8 E | S-CALL | N-CALL |

ALLOC (restricted): `Arena` (the `Copy_Data` result, `:77`), `Typed_Rows` (`:78`) and `Mask` with its initialization (`:79-80`) `=`. Not covered: the `Requested` function result and the per-row acceptance objects (X4), native storage OPEN. EXC/WRITE: mask bytes only for `No_Change` or `Removal_Planned`, ascending; handler 255 (§9.6).

## C9. U7 `wl_resource_ledger_compute`, `wl_resource_ledger_headroom`

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | per row `D := Accept_Row (V)`; `Typed_Rows (I) := D.Row`; `Slots (I) := D.Slot` | `worldline-resource_ledger_c_api.adb:150-159` | `Row_C` U → acceptance (`Reservation_Row`, `Output_Span`) Rd | Per row: S-CALL, X4, two X3 selections, two S-ASSIGN (the original assigned aggregates directly). The two `Decode` calls (`:157`) move inside, with an unchanged count. | N-CALL, N-CHECK, N-OBJ, N-COPY |
| 2 | `L.Compute (…)` | `:162-163` | as original | `=`. `Detail_Arena`, `Total_Arena`, `Typed_Details`, `Total` and `Status` are its `out` actuals (WF-O). Its Post (`resource_ledger.ads:205`) is evaluated once in chk. | — |
| 3 | `Write_Data` ×2 | `:164-165` | — | `=` (WF-B; the helper is hash-bound, A-BIND §B9.3) | — |
| 4 | per detail `As_Quantity (…).all := Worldline.Resource_Ledger_C_API.Encode_Quantity (Typed_Details (I))` | `:166-170` (body-local expression function `Encode`, `:86-88`) | `Q.Quantity` U → `Quantity_C` Rd | Per detail: S-CALL into another unit replaces the call of a body-local expression function. WF-F: the function result is stored directly through the access value, as the original stored the `Encode` result. | N-CALL: the installed User's Guide lists expression functions among the conditions for inlining calls within the current unit, and requires `pragma Inline` and `-gnatn` for calls into `with`ed units (GN `gnat_ugn.info:14798-14835`). So the documented ordinary behaviour differs between the original and the successor, but neither is object-code evidence (C21-a). N-OBJ for the result; construction (C19). |
| 5 | `As_Result (Result).all := Result_Of (Status, Total)` | `:171-172` (aggregate stored directly) | `Result_Status` E; `Q.Quantity` U → `Result_C` Rd | S-CALL. WF-F: the function result is stored directly, as the original stored the aggregate directly. | N-OBJ: in place or temporary; construction (C19) |
| 6 | headroom `HI := Accept_Headroom_Inputs (A, W, F)` | `:203-205`, decodes at `:213` | 3 × `Quantity_C` U → acceptance (3 × `Q.Quantity`) Rd | S-CALL; X4. Three X3 selections are actuals of `L.Compute_Headroom`; the original passed three `Decode (…)` function results directly. The three decodes move into the acceptor (M4), count unchanged. | N-PASS, N-CHECK, N-OBJ |
| 7 | `L.Compute_Headroom (…)` | `:212-214` | as original | `=`. `Output_Arena`, `Typed_Result` and `Status` are its `out` actuals (WF-O). Its Post (`resource_ledger.ads:263`) is evaluated once in chk. | — |
| 8 | `As_Result (Result).all := Result_Of (Status, Typed_Result)` | `:216-218` | as 5 | as 5 | as 5 |

ALLOC (restricted): Compute's `Arena` (`:136`), `Typed_Rows`, `Slots`, `Detail_Arena`, `Total_Arena` and `Typed_Details` (`:137-141`) and Headroom's `Arena` and `Output_Arena` (`:207-208`) keep their source positions, order and bounds, `=`. Not covered: the per-row acceptance objects, `HI`, and the `Encode_Quantity`/`Result_Of` function results; their native storage is OPEN. EXC/WRITE: the unconditional writeback keeps its source order. A handled internal exception raised after the first write returns 255, and the writes completed before it may persist (§9.6). Which writes complete, and whether one in progress completes partially, is OPEN (C19, D-36).

## C10. U8 `wl_resource_policy_admit`

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `IA := Accept_Input (V)` | `worldline-resource_policy_c_api.adb:135-151` | `Input_C` U → acceptance (`Policy_Input`) Rd | S-CALL; X4. Ten `Shape` tests and ten decodes move inside, with unchanged counts. `IA.State` is an actual of `P.Admit` (X3 selection). The original's `State` constant (`:145-150`) becomes `IA`'s payload. | N-PASS, N-CHECK, N-OBJ |
| 2 | per row `D := Accept_Disk (Row)`; `Rows (I) := D.Item` | `:159-164` | `Disk_C` U → acceptance (`Disk_Row`) Rd | Per row: S-CALL, X3, X4, one S-ASSIGN (the original assigned an aggregate) | N-CALL, N-CHECK, N-OBJ, N-COPY |
| 3 | `Decode_Data (Data, Data_Length)` | `:168` | — | `=` | — |
| 4 | `Decision : constant P.Decision := P.Admit (Arena, IA.State, Rows)` | `:169` | as original | `=` (WF-C provenance of `Decision`). Its Post (`resource_admission.ads:201`) is evaluated once in chk. | — |
| 5 | `As_Result (Result).all := Worldline.Resource_Policy_C_API.Encode_Decision (Decision)` | `:171-176` (aggregate stored directly) | `Decision` U → `Result_C` Rd | S-CALL. WF-F: the aggregate is built inside SPARK as the function result, which is stored directly through the access value, as the original stored the aggregate directly. | N-CALL, N-OBJ; construction (C19) |

ALLOC (restricted): `Rows` (`:152`) and `Arena` (`Decode_Data`, `:168`) `=`. Not covered: `IA`, the per-row acceptance objects and the `Encode_Decision` result (native OPEN).

## C11. U9 `wl_evaluation_history_select`

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `Final_Flag_Valid`, `Final_Row_Present` ×2 | `worldline-evaluation_history_c_api.adb:136`, `:139`, `:157` | U8 E → Boolean | S-CALL | N-CALL |
| 2 | `QA := Accept_Query (Raw_Q)` | `:151-156`, with the decode moved from `:174-177` (M4) | `Query_C` U → acceptance (`H.Query`) Rd | S-CALL; X4. The decoded query's source lifetime is the enclosing block, across the row loop. The decode is pure and its count unchanged. | N-OBJ, N-LIFE |
| 3 | `FA := Accept_Final_Row (V)`; `F := FA.Item` | `:161-162` | `Row_C` U → acceptance (`H.Optional_Record`) Rd | S-CALL, X3, X4, one S-ASSIGN | N-CHECK, N-OBJ, N-COPY |
| 4 | per row `D := Accept_Row (V)`; `History (I) := D.Item` | `:170-171` | `Row_C` U → acceptance (`H.Evaluation_Record`) Rd | Per row: S-CALL, X3, X4, one S-ASSIGN | N-CALL, N-CHECK, N-OBJ, N-COPY |
| 5 | `Result : constant … := Select_Result (A, History, F, QA.Item)` | `:179-183` | `R.Byte_Array` U, `H.History` U, `H.Optional_Record` U, `H.Query` U → `Selection_C` Rd | S-CALL: one extra call level around `H.Select_Evidence`. The aggregate of `:180-183` is built in SPARK. `H.Select_Evidence`'s Post (`evaluation_history.ads:321`) is evaluated once in chk, `=`. | N-PASS for the arrays; N-OBJ |
| 6 | `As_Selection (Output).all := Result` | `:185` | — | `=`: WF-C, one source assignment of a completed constant, as before; the constant now comes from a SPARK function result | copy count OPEN |

ALLOC (restricted): `A` (`Copy_Data`, `:147`), `History` (`:148`) and `F` (`:149`) `=`. Not covered: `QA`, `FA`, the per-row acceptance objects and the `Select_Result` result.

## C12. U12 `wl_resource_run_ledger_check_v1` (CORRECTED in v4)

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | guards; capture; four allocations; four unconditional copy loops | `resource_run_ledger_c_api.adb:195-216` | — | `=` | — |
| 2 | `O := Check_Decision (Data, Raw, Before, Proposed, Observed)` | `:217-219` | `Data`: `Q.Byte_Array` U (array); `Raw`: `Raw_Packet` U (record); `Before`, `Proposed`: 2 × `Raw_Row_Array` U (arrays); `Observed`: `Raw_Native_Array` U (array) → acceptance (`Raw_Result`) Rd | S-CALL. `W.Well_Formed (…)` (`resource_run_ledger_wire.ads:342-350`, which iterates over the rows) is evaluated **once**, as in the original: this is the cost-neutral pattern. `W.Decide` is called once; its Pre (`:362`) and Post (`:363`) are evaluated once each in chk, `=`. One extra call level in source for **four array actuals** (JACKAL J10 `parsed=1+2+1` → `exact=4`) and **one record actual** (`Raw`), five actuals in all (JACKAL J11 `parsed=4+1` → `exact=5`). X4 for the acceptance result. The release-path `Big_Integer` code reached through `W.Decide` is unchanged (`=`; D1, D-35 OPEN). | N-PASS for each of the five U actuals; N-OBJ |
| 3 | `Result_At (Output).all := O.Value` | `:219` (`… := W.Decide (…)`) | — | WF-A: one source assignment of the payload of a completed acceptance constant, where the original assigned the `W.Decide` function result directly | C19, D-36 |

ALLOC (restricted): `Data`, `Before`, `Proposed` and `Observed` (`:208-211`) `=`. Not covered: `O` (X4).

## C13. U13 `wl_chain_authority_replay_v1`

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | guards; `H` capture; `Owned` allocation; `W.Well_Formed (H)` | `worldline-chain_authority_c_api.adb:70-88` | — | `=` | — |
| 2 | per row `D := Accept_Row (Raw)`; `Owned (I) := D.Item` | `:91-95` | `Raw_Row` U → acceptance (`Chain_Row`) Rd | Per row: `W.Well_Formed (Raw)` and `W.Decode (Raw)` are called once each, as before; Decode's Pre (`worldline-chain_authority_wire.ads:53`) and Post (`:54`) are evaluated once in chk, `=`. Also S-CALL, X3, X4 and one S-ASSIGN (the original assigned the `Decode` result directly). | N-CALL, N-CHECK, N-OBJ, N-COPY |
| 3 | `RV := Replay_Value (Owned, H)` | `:99` | `Retained_Rows` U, `Raw_Anchors` U → acceptance (`Raw_Result`) Rd | S-CALL; S-RECHECK: one extra `W.Well_Formed (H)` (`worldline-chain_authority_wire.ads:37-42`) per accepted call, in every build. `W.Decide`'s Pre (`:60`) and Post (`:61`) are evaluated once in chk, `=`. One extra call level for `Owned` and `H`; X4. | N-PASS, N-OBJ |
| 4 | `Result_At (Output).all := RV.Value` | `:99` (`… := W.Decide (Owned, H);`) | — | WF-A | C19, D-36 |

ALLOC (restricted): `Owned` (`:86`) `=`. Not covered: the per-row acceptance objects and `RV`.

## C14. U10, U11 `wl_pending_decide_v1`, `wl_pending_decide_v2` (and the component under D-13)

| # | Successor site | Original (v1; v2) | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `Header_Valid (R)`, `Request_Fields_Valid (R)` in the guard | `evaluation_pending_c.adb:120`, `:128-131`; v2 `:141`, `:149-152` | `Request` U → Boolean | S-CALL; `R` is an actual | N-CALL, N-PASS |
| 2 | per row `D := Accept_Row (V)`; `J (I) := D.Item` | `:146-158`; v2 `:167-181` | `Row` U → acceptance (`E.Intent`; `V2.Intent`) Rd | Per row: S-CALL, X3, X4, one S-ASSIGN (the original assigned an aggregate directly) | N-CALL, N-CHECK, N-OBJ, N-COPY |
| 3 | `O := Decide_Value (A, J, R)` | `:161-168`; v2 `:184-192` | `E.Bytes` U, `E.Journal` / `V2.Journal` U, `Request` U → acceptance (`Result`) Rd | S-CALL; S-RECHECK: `Header_Valid (R)` and `Request_Fields_Valid (R)` again (dead). The `Convert (R.…)` decodes are inside, with an unchanged count. `E.Decide` / `V2.Decide` is called once; its Post (`evaluation_pending.ads:163`; `evaluation_pending_v2.ads:86`) is evaluated once in chk, `=`. The result aggregate is built in SPARK as the acceptance payload. | N-PASS, N-OBJ |
| 4 | `Result_Pointers.To_Pointer (Output).all := O.Value` | `:165-168`; v2 `:188-192` (aggregate stored directly) | — | WF-A | C19, D-36 |

ALLOC (restricted): `A` and `J` (`:136-137`; v2 `:157-158`) `=`. The plan variable `P` (`:138`; v2 `:159`) moves into `Decide_Value`.

**Component under D-13 option (i) (§16.1).** The mirrored component units and the component transport unit have the same source deltas in the component's own build (comp: `-gnata -gnatVa -O0`); the component transport adds X1, X3 and X4 in its own Off text. Native effects in that build (calls, temporaries, copies, checks) are OPEN like every other native item. **Nothing is claimed about elision at `-O0` or at any other level** (v3 A-COST:240 withdrawn).

## C15. U14 completion

**`wl_completion_decide_v1` (original `evaluation_completion_c.adb:393-528`)**

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `Decide_Header_Valid (R)`, `Decide_Fields_Valid (R)` in the chain | `:408`, `:416-420` | `Request` U (a large record) → Boolean | S-CALL | N-CALL, N-PASS for `R` |
| 2 | arrays `A`, `J`, `Measures`, `Captured`, `Retained_Results`, `History`, `Required` | `:423-429` | — | `=` (same declarations and order; A-BIND §B4.14 tile) | — |
| 3 | per journal row `Accept_Journal_Row (X)` | `:446-453` | `Journal_Row` U → acceptance (`V.Intent`) Rd | Per row: S-CALL, X3, X4, one S-ASSIGN | N-CALL, N-CHECK, N-OBJ, N-COPY |
| 4 | per captured row `Accept_Captured_Row (X)` | `:458-465` | `Check_Row` U → acceptance (`T.Result_Record`; `Roster.Measured_Result`) Rd | Per row: S-CALL, X4, two X3 selections, two S-ASSIGN | as 3 |
| 5 | per retained, history and required row `Accept_Result_Row`, `Accept_History_Row`, `Accept_Required_Row` | `:468-475`, `:477-484`, `:486-493` | `Check_Row`, `History_Row`, `Required_Row` U → acceptance (`T.Result_Record`, `H.Evaluation_Record`, `Roster.Required_Check`) Rd | Per row: S-CALL, X3, X4, one S-ASSIGN | as 3 |
| 6 | `Decide_Value (R, A, J, Captured, Measures, Retained_Results, History, Required, Response, Status)` | `:431-439`, `:495-520` | `Request` U, `P.Bytes` U, `V.Journal` U, 2 × `T.Result_Array` U, `Roster.Measured_Array` U, `H.History` U (**`in out`**), `Roster.Check_Array` U, `Result` U (`out`), `C.int` E (`out`) | S-CALL; S-RECHECK: `Decide_Header_Valid`, `Decide_Fields_Valid` (dead). **New source call `T.History_Index (J, History, Selected)` (`evaluation_completion.ads:332-338`) on the summary path, with its Post (`:337`) evaluated in chk: the one new `-gnata` evaluation (S-ASSERT; X5; §5.4).** S-INIT: `Response := Initial_Response` on every path (moved from the declaration at `:436-439`, same values). `T.Decide` (`:496`), `T.Apply` (`:499`), `T.Find_Run` (`:504`) and `Roster.Classify` (`:507`) keep their counts; their Posts (`evaluation_completion.ads:264`, `:420`, `:138`; `evaluation_completion_roster.ads:144`) are evaluated in chk as before, `=`. | N-PASS: a by-copy choice for `in out History` would copy the whole history array in and out, and `out Response` likewise; N-ASSERT |
| 7 | `Outputs.To_Pointer (Output).all := Response` | `:522` | — | WF-R: one source assignment of the local `Response`, as before; `Response` is now the `out` actual of `Decide_Value` | copy count OPEN |

**`wl_completion_raw_decide_v1` (`:529-693`).** The same rows as decide, with these differences:
- the chain uses `Raw_Header_Valid` (`:545`) and `Raw_Fields_Valid` (`:557-561`);
- each captured row makes two acceptance calls: `Accept_Raw_Check_Row` (`:599-603`; S-CALL, X3, X4) and `Accept_Raw_Measure` (`:605-614`), whose body calls `W.Well_Formed (Wire)` (`:610`) once as before;
- `Raw_Decide_Value` re-checks `Decide_Header_Valid` and `Raw_Fields_Valid` (§5.5) and adds the same `History_Index` call;
- `Decide_Envelope` (`:646`; Post `worldline-evaluation_authority.ads:89`), `T.Apply` (`:650`), `T.Find_Run` (`:655`), `Raw_Roster.Row_Bound` (`:667`, once per measure as before) and `Raw_Roster.Classify` (`:672`; Post `evaluation_raw_roster.ads:143`) keep their counts, `=`;
- the post-decision 255 (`:657-671`) is unchanged.

**`Completion_Transport.Context_Matches` (`:733-869`)**

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `Context_Header_Valid (R, X)`, `Context_Fields_Valid (R, X)`, `Context_Agent_Matches (X, Raw_Agent, Agent_Confinement)` in the chain | `:765`, `:767-774`, `:780` | `Request` U, `Context_Input` U (a large record), `W.Raw_Record` U, U8 E → Boolean | S-CALL | N-CALL; N-PASS for two large records per call |
| 2 | `FA := Accept_Context_Fields (X)` | `:795-804` | `Context_Input` U → acceptance (2 × `CA.Context_Fields`) Rd | S-CALL; X4. S-INIT: two local arrays inside the routine initialized `(others => (Present => False))`, the same values as the original's default initialization at `:789`; they become components of the result aggregate. `FA.Expected` and `FA.Observed` are later actuals of `Context_Join_Value` (X3 selections). | N-OBJ, N-COPY, N-PASS |
| 3 | per row pair `RA := Accept_Context_Row (Original, Owned)` | `:805-831` | `Check_Row` U, `Context_Row` U → acceptance (`T.Result_Record`; `CA.Context_Row`) Rd | Per row: S-INIT of `Joined`'s two field arrays inside (same values as `:791`), S-CALL, X4, two X3 selections, two S-ASSIGN | N-CALL, N-CHECK, N-OBJ, N-COPY |
| 4 | per required pair `QA := Accept_Required_Pair (Original, Owned)` | `:832-848` | 2 × `Required_Row` U → acceptance (2 × `Roster.Required_Check`) Rd | Per row: S-CALL, X4, two X3 selections, two S-ASSIGN | as 3 |
| 5 | `V := Context_Join_Value (R, X, Raw_Collapse, Data, Context_Data, FA.Expected, FA.Observed, Rows, Joined, Required, Expected_Required)` | `:850-857` | `Request` U, `Context_Input` U, `CW.Raw_Request` U, 2 × `P.Bytes` U, 2 × `CA.Context_Fields` U, `T.Result_Array` U, `CA.Context_Rows` U, 2 × `Roster.Check_Array` U → `Join_Verdict` E | S-CALL; S-RECHECK: `Context_Header_Valid` and `Context_Fields_Valid` (dead). `CA.Join_Context` is called once; its Post (`worldline-evaluation_authority.ads:236`) is evaluated in chk, `=`. Every actual is a U composite. | N-PASS for every actual |
| 6 | `Join_Code (…)` ×2 | `:859-861` | Boolean E → `C.int` E | S-CALL | N-CALL |

**`Completion_Metadata_Matches` (`:909-986`).**
- `Metadata_Header_Valid (R, X)` (`:932-933`): S-CALL with `Metadata_Context` U.
- Per row, `Accept_Metadata_Row (Original, Owned)` (`:953-968`) returns an acceptance carrying `T.Result_Record` and `CA.Row_Metadata`: S-CALL, X4, two X3 selections, two S-ASSIGN.
- `CA.Join_Metadata` (`:974`; Post `:273`) is unchanged, `=`.
- `Join_Code`: S-CALL.

**`Completion_Transport.Metadata_Base` (`:893-907`).** `Metadata_Version_Valid (X)` (`:901`) is an S-CALL with `Metadata_Context` U.

ALLOC (restricted): the original arrays keep their source positions, order and bounds (A-BIND §B4.14–§B4.17 tiles), `=`: in decide and raw, `A`, `J`, `Measures`, `Captured`, `Retained_Results`, `History` and `Required`; in context, `Data`, `Context_Data`, `Rows`, `Joined`, `Required` and `Expected_Required`; in metadata, `Data`, `Projected_Data`, `Rows` and `Projected`. Not covered: the acceptance objects (X4) and the arrays inside acceptance results (`Accept_Context_Fields`' `Expected`/`Observed`, `Accept_Context_Row`'s `Joined`), whose native storage is OPEN. EXC/WRITE: decide and raw write once (WF-R); context and metadata write nothing foreign.

## C16. U15 finalization (including D-28)

**`wl_finalization_decide_v1` (`evaluation_finalization_c.adb:121-257`)**

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `Request_Header_Valid (X)`, `Request_Fields_Valid (X)` in the chain | `:138`, `:145-153` | `Request` U → Boolean | S-CALL | N-CALL, N-PASS |
| 2 | per plan `PA := Accept_Plan (Q)` | `:170-178` | `Required_Row` U → acceptance (`Required_Check`) Rd | Per plan: S-CALL, X3, X4, one S-ASSIGN | N-CALL, N-CHECK, N-OBJ, N-COPY |
| 3 | `Needs_Rows (X)` | `:183-188` (branch on `X.Operation`) | `Request` U → Boolean | S-CALL | N-CALL |
| 4 | per row `RA := Accept_Row (Q)` (Operations 2 and 3 only) | `:189-199` | `Row` U → acceptance (`F.Start_Row`) Rd | Per row: S-CALL, X3, X4 (`Start_Row` has variant components), one S-ASSIGN into `Captured (K)` | as 2 |
| 5 | `O := Decide_Rows_Value (X, A, Required, Captured)` or `O := Decide_No_Rows_Value (X, A, Required)` | `:163-244` | `Request` U, `P.Bytes` U, `Raw_Roster.Check_Array` U, `F.Start_Rows` U → acceptance (`Result`) Rd | S-CALL; S-RECHECK: `Request_Header_Valid`, `Request_Fields_Valid` and the operation selector (dead). `S := Convert (X.Start)` (`:163`) and the `Response` initialization (`:164-166`) move inside, same source work. `F.Classify_Capture` (`:204`; Post `evaluation_finalization.ads:265`) and `F.Seal` (`:219`; Post `:394`) keep their counts, `=`. `Seal`'s release-path `Canonical_Artifacts` `Big_Integer` code is unchanged (D1 OPEN). X4 for `O`'s value. | N-PASS, N-OBJ |
| 6 | `Outputs.To_Pointer (Output).all := O.Value` | `:249` (`… := Response;`) | — | WF-X: one source assignment of the payload of `O`, which is assigned on exactly one of two exclusive paths (§5.1); the original assigned the local `Response` | C19 |

ALLOC (restricted): `A` (`:160`), `Required` (`:161`) and `Captured` for every operation (`:162`) `=`. Operations 0 and 1 neither pass nor read `Captured` (§5.1).

**`Finalization_Transport.Final_Context_Matches` (`:259-355`)**

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `Native : aliased Result := Initial_Result` | `:264` (`Native : aliased Result;`, uninitialized) | — | S-INIT (D-28): one full-record initialization per call | N-OBJ |
| 2 | `Final_Seal_Ready (Seal_Status, Native)` | `:273-274` | `C.int` E, `Result` U → Boolean | S-CALL. The address-based self-call `Finalization_Decide (Input, Native'Address)` is `=` (D-26). | N-CALL, N-PASS |
| 3 | `Final_Plans_Valid (X)` | `:282-286` | `Request` U → Boolean | S-CALL | N-CALL, N-PASS |
| 4 | per row `Projected_Rows (I) := Final_Projected_Row (X, Original)` | `:300-313` | `Request` U, `Row` U → `K.Check_Row` Rd | Per row: S-CALL with `X` as an actual. The six-field `K.Binding` aggregate, evaluated once in the original (`:294-295`), is **evaluated per row** inside the routine: linear extra source work in the row count. A separately reviewed refinement could pass a once-computed binding; it is not adopted here. | N-PASS (a by-copy choice would copy the request once per row); N-OBJ |
| 5 | per plan, verbatim copy | `:314-318` | — | `=` | — |
| 6 | `Projection := Final_Projection (X, Native, Projected_Rows'Address, Projected_Plans'Address)` | `:294-331` | `Request` U, `Result` U, 2 × `System.Address` E → `K.Request` Rd | S-CALL. `Bound` and `Empty_Capture` are built inside, once. `Projection` is assigned from a function result; the original assigned an aggregate directly. | N-OBJ, N-COPY |
| 7 | `Completion_Transport.Context_Matches (…)`, `Completion_Transport.Metadata_Base (…)`, `Completion_Metadata_Matches (…)` | `:334-342` | — | as in C15 | as in C15 |

**`wl_collapse_decide_finalization_v1` (`:357-509`)**

| # | Successor site | Original | Types | Source delta | Native (OPEN) |
|---|---|---|---|---|---|
| 1 | `Read_Ready`: `Kind_Of (Kind)` | `:377-395` | U32 E → enumeration E | S-CALL per invocation | N-CALL |
| 2 | `Ordinary : aliased Evaluation_Completion_C.Result := Initial_Response` (Kind 1 branch) | `:373` (uninitialized; declared for every kind) | — | S-INIT (D-28): one full-record initialization per Kind-1 call; the object is now declared only in its branch | N-OBJ |
| 3 | `Ordinary_Readiness (Status, Ordinary)` | `:379-384` | `C.int` E, `K.Result` U → `Readiness_Result` Rd | S-CALL; S-OBJ (result) | N-PASS, N-OBJ |
| 4 | `Finalized : aliased Result := Initial_Result` (Kind 2 branch) | `:374` (uninitialized) | — | S-INIT (D-28), as row 2 | N-OBJ |
| 5 | `Finalized_Readiness (Status, Finalized)`; `Finalized_Operation_Readiness (X, Finalized)` | `:386-394` | `C.int` E, `Result` U, `Request` U → `Readiness_Result` Rd | S-RECHECK: `Promotion <= 1`, re-tested so that the `U8` conversion stays total (dead) | N-PASS, N-OBJ |
| 6 | `Authority.Dependencies (Bound)`; `Authority.Needs_Primary/Needs_Staged/Needs_Agent (Needed)` | `:420`, `:427`, `:439`, `:453` | — | `=` | — |
| 7 | `Agent_Ready := Agent_Readiness (Owned_Agent, Agent_Confinement)` | `:463-469` | `W.Raw_Record` U, U8 E → U8 E | S-CALL. `W.Confined_Admit_Wire` is called once; its Post (`worldline-evaluation_wire.ads:164`) is evaluated in chk, `=`. | N-CALL, N-PASS |
| 8 | `Context_Join_Needed (Agent_Ready, P_Ready)`, `Context_Join_Needed (Agent_Ready, S_Ready)` | `:473-484` | E → Boolean | S-CALL; `Agent_Ready = 1` is tested twice in source instead of once | N-CALL |
| 9 | `Decision := Mixed_Collapse_Decision (Bound, Agent_Ready, P_Ready, S_Ready)` | `:485-487` | `CW.Raw_Request` U, 3 × U8 E → U8 E | S-CALL. S-OBJ: the delta aggregate `(Bound with delta …)` denotes a new record value built from `Bound` (RM 4.3.4), passed to `CW.Decide_Wire`; the original assigned two components of the transport variable and passed it. `CW.Decide_Wire` is called once; its Post (`worldline-collapse_wire.ads:257`) is evaluated in chk, `=`. | N-OBJ, N-COPY (whether a full copy of the collapse request is made) |
| 10 | `Mixed_Authorized (Decision)`; `Mixed_Metadata_Needed (…)` ×2 | `:489`, `:491`, `:497` | E → Boolean | S-CALL. `Mixed_Metadata_Needed` calls `Needs_Primary` or `Needs_Staged` once each, as the original did at `:491` and `:497`. | N-CALL |

EXC/WRITE: `=`. The mixed entry writes nothing foreign. The double `Seal` on the Kind-2 path is kept (D-27).

## C17. `Authority_Glue` edits and effects across the C_API unit

| Site | Original | Successor | Source delta | Native (OPEN) |
|---|---|---|---|---|
| `K.Raw_Decide (…)` ×2 (GE1, GE2) | `core/worldline-c_api.adb:784-785`, `:791-792` | `Completion_Raw_Decide (…)` | Same profile and actuals; the callee is now in the same unit | N-CALL (whether a same-unit call is inlined) |
| `K.Context_Matches (…)` ×2 (GE3, GE4) | `:810-811`, `:813-814` | `Completion_Transport.Context_Matches (…)` | as above | as above |
| `K.Metadata_Base (…)` ×2 (GE5, GE6) | `:852`, `:855` | `Completion_Transport.Metadata_Base (…)` | as above | as above |
| `K.Metadata_Matches (…)` ×2 (GE7, GE8) | `:866-867`, `:869-870` | `Completion_Metadata_Matches (…)` | as above | as above |
| `package K renames Evaluation_Completion_C;` (GE9, R-DEL-1) | `:836` | deleted | A renaming with no remaining reference is removed; no source evaluation changes | none |

Per-call source deltas of the callees are those of C15.

Across the unit:
- The C_API body gains `with Ada.Text_IO;` and `with Ada.Exceptions;` (§3.6). Their elaboration and runtime dependencies were already part of the library through `Evaluation_Completion_C`.
- Each transport package carries its own copy of its unit's pointer instances and helpers (hash-bound, A-BIND §B9.3). The original units drop that text (G7). Native code identity of the relocated text is OPEN (D-15).

## C18. Diagnostics (RC1) (CORRECTED in v4)

Source counts are per reached call on the stated path. "Active" means that the read in the path's `Begin_*` or `Observe` call returns True. "Fitting" means that the length predicate holds, which is the case for every actual call site (literal sites, `I64` values, exception information); the overlong case is kept exact but is unreachable there (§4.6). A **fit pair** is the two source evaluations of one `*_Fits` predicate on a fitting path: one in the `Begin_*` procedure (§4.3, DESIGN v3:450, :461, :472) and one in the guarded composer (DESIGN v3:429, :432, :434). JACKAL J06 `parsed=1+1` → `exact=2` per pair.

| Path | Original (source) | Successor (source) | Source delta | Native (OPEN) |
|---|---|---|---|---|
| Inactive `Mark` site | One call to `Diagnostic_Mark`, then one atomic read (`evaluation_completion_c.adb:44`); no length test | The transport `Mark` (a C_API-local call), then `Diagnostic_Begin_Line`, which performs one atomic read; `Active and then …` short-circuits, so `Line_Fits` is **not** evaluated | One more call level; the same single atomic read (§4.6) | N-CALL |
| Inactive `Value` site | `Diagnostic_Value`, one atomic read (`:55`); `I64'Image` not evaluated | `Value` → `Diagnostic_Begin_Value`, one atomic read; the short circuit skips both `I64'Image` and `Value_Fits` | One more call level | N-CALL |
| Inactive `Exception` site | `Diagnostic_Exception`, one atomic read (`:65`); `Exception_Information` not called | `Exception_Text` → `Diagnostic_Observe`, one atomic read; `Exception_Information` not called | One more call level | N-CALL |
| Active `Mark`, fitting | One atomic read; catenation inline in the `Put_Line` actual; `Put_Line`; `Flush` (`:46-47`) | `Begin_Line`: one atomic read and `Line_Fits` once; then `Diagnostic_Line`: `Line_Fits` again and the catenation, returning a `String` (Ri); then `Put_Line`; `Flush` | **One fit pair: two `Line_Fits` evaluations** (J06); two SPARK calls; a `String` function result in place of the original's catenation result | N-CALL; N-OBJ, N-LIFE for the `String` result and for the original's catenation result (the installed User's Guide's secondary-stack statement covers results of unconstrained types returned by functions, GN `gnat_ugn.info:11252-11260`; its application to these two objects is OPEN) |
| Active `Mark`, overlong (unreachable at actual sites) | Catenation raises `Constraint_Error`; the handler latches | `Begin_Line` evaluates `Line_Fits` once, latches, and writes no line | One length test replaces the exception path, with the same effect | — |
| Active `Value`, fitting | One atomic read; one `I64'Image`; catenation; nested `Diagnostic_Mark` with its own atomic read, catenation, `Put_Line` and `Flush` (`:56`) | `Begin_Value`: one atomic read, `I64'Image` once and `Value_Fits` once; `Diagnostic_Value_Site`: `I64'Image` again, `Value_Fits` again, catenation; nested transport `Mark`: its own atomic read in `Begin_Line` and, if that read is True, its own fit pair (`Line_Fits` in `Begin_Line` and in `Diagnostic_Line`) | `Value_Fits`: one fit pair (J06). `I64'Image`: 2 against 1, +1 (J09 `parsed=2-1` → `exact=1`). The nested `Mark` adds its own `Line_Fits` pair when its read is True, so the path has four `*_Fits` evaluations (JACKAL J08 `parsed=2+2` → `exact=4`). Atomic reads: 2 in both (J06). | N-CALL, N-OBJ |
| Active `Exception`, fitting | One atomic read; `Exception_Information`; catenation; nested `Mark` (`:67`) | `Diagnostic_Observe` (one atomic read); `Exception_Information` (transport, T4); `Begin_Exception`: `Exception_Fits` once (no atomic read); `Diagnostic_Exception_Site`: `Exception_Fits` again, catenation; nested `Mark` as above | `Exception_Fits`: one fit pair (J06); the nested `Mark`'s `Line_Fits` pair when its read is True, four `*_Fits` evaluations in all (J08). Atomic reads: 2 in both (J06). | N-CALL, N-OBJ |
| `Native_Diagnostic_Control` | Inline check-then-act (`:73-88`) | `Diagnostic_Control_Of`, then `Diagnostic_Start` or `Diagnostic_Stop`, and the transport `Mark` | Calls only, with the same atomic reads and writes in the same order (§4.6). On Start with `Emit_Begin`, and on Stop, the transport `Mark` performs its own read and, when that read is True, one `Line_Fits` pair, where the original `Diagnostic_Mark` performed its read and catenation. | N-CALL |

The nested `Mark` has its own active gate. If its read returns False (the check-then-act is not atomic, as the original documents), it evaluates no `Line_Fits` and writes nothing, exactly as the original's nested `Diagnostic_Mark` would.

ASSERT: none, unless a reviewer requires the optional small Posts (§4.7), which would each add a chk evaluation. EXC: the latch semantics are unchanged.

## C19. D-36: write construction per write form (REVISED in v4; aligned with A-BIND §B10)

One account per export, in the form of A-BIND §B10.1. Every native column is OPEN.

| Export | Form | Original construction (S5, source) | Successor construction (source) | Native (OPEN) |
|---|---|---|---|---|
| v2 | WF-C | `Result_At (Output).all := W.Decide (Raw);` (`worldline-recovery_authorization_c_api.adb:146`): a function result assigned through an access value | `Owned : constant W.Raw_Result := Worldline.Recovery_Authorization_C_API.Decide_Total (Raw);` then `Result_At (Output).all := Owned;` | Whether the original's result was built in place in `Output`, so that an exception inside `W.Decide` could leave `Output` partly written; whether `Owned` is a separate object and the assignment a copy; padding |
| v3 | WF-C | `… := W.Decide (Data, Raw);` (`…_v3_c_api.adb:163`) | `Owned` from `Decide_Total (Data, Raw)`, then one assignment | as v2 |
| protocol | WF-P | `Result_At (Output).all := Owned_Result;` (`worldline-recovery_protocol_c_api.adb:66`) | unchanged | copy count, as for the original |
| lifecycle mask | WF-F (with WF-O `Mask`) | `As_Byte (…).all := Boolean'Pos (Mask (I));` per byte (`worldline-reservation_lifecycle_c_api.adb:111-112`) | `As_Byte (…).all := Worldline.Reservation_Lifecycle_C_API.Mask_Byte (Mask (I));` per byte | call or inlining per byte |
| ledger compute | WF-B ×2, WF-F ×2 (with WF-O buffers) | `Write_Data` ×2 (`:164-165`); `As_Quantity (…).all := Encode (Typed_Details (I));` (`:166-170`); `As_Result (Result).all := (Status => …, Total => Encode (Total));` (`:171-172`) | `Write_Data` ×2 unchanged; `… := Worldline.Resource_Ledger_C_API.Encode_Quantity (Typed_Details (I));`; `As_Result (Result).all := Worldline.Resource_Ledger_C_API.Result_Of (Status, Total);` | For each WF-F store: built in place in the foreign object or in a temporary; partial-write behaviour on an exception during construction |
| ledger headroom | WF-B, WF-F | `Write_Data (Output, Output_Arena);` (`:215`); aggregate stored directly (`:216-218`) | `Write_Data` unchanged; `Result_Of (Status, Typed_Result)` stored directly | as compute |
| policy | WF-F (with WF-C `Decision`) | an aggregate of `D` fields stored directly (`worldline-resource_policy_c_api.adb:171-176`) | `As_Result (Result).all := Worldline.Resource_Policy_C_API.Encode_Decision (Decision);` | as compute |
| history | WF-C | `As_Selection (Output).all := Result;` (`worldline-evaluation_history_c_api.adb:185`), `Result` a constant initialized by an aggregate | the same statement; `Result` initialized by `Select_Result (…)` | copy count |
| pending v1, v2 | WF-A | an aggregate of `P` fields stored directly (`evaluation_pending_c.adb:165-168`; `evaluation_pending_v2_c.adb:188-192`) | `Result_Pointers.To_Pointer (Output).all := O.Value;` | construction of the aggregate in the original; copy of `O.Value` |
| run ledger | WF-A | `Result_At (Output).all := W.Decide (…);` (`resource_run_ledger_c_api.adb:219`) | `Result_At (Output).all := O.Value;` | as v2 |
| chain | WF-A | `Result_At (Output).all := W.Decide (Owned, H);` (`worldline-chain_authority_c_api.adb:99`) | `Result_At (Output).all := RV.Value;` | as v2 |
| completion decide, raw | WF-R | the local `Response`, declared with an initializing aggregate and assigned piecewise, assigned once (`evaluation_completion_c.adb:522`, `:687`) | `Response` declared without an initializer, the `out` actual of `Decide_Value`/`Raw_Decide_Value`, assigned once | copy counts; `out` passing (N-PASS) |
| finalization decide | WF-X | the local `Response` assigned once (`evaluation_finalization_c.adb:249`) | `O.Value` assigned once; `O` is assigned on exactly one of two exclusive paths | copy counts |

For every row, the matching builds must establish the order in which the stored value is constructed, its copy and padding effects, and its exception and no-write semantics (C21-e, C21-h). The malformed-input fixture `tests/test_recovery_witness_relation.py:174-179` establishes none of them. No global transactional-write claim is made.

**C-14 scope (proposed behaviour only).** C-14 asks whether the successor writes nothing on an internal exception for the WF-C and WF-A exports, where the successor completes the stored value before the write: v2, v3, run ledger, chain, pending v1 and v2. It is review evidence for D-36 only, never a baseline assertion (§9.6). WF-F exports (lifecycle mask, ledger, policy) store a function result directly, as their originals stored a function result or aggregate directly; no stronger behaviour is proposed for them. v3's C-14 scope, which listed policy and ledger as local-then-write exports, is corrected (§15).

## C20. Original native blockers (carried from v3, unchanged, OPEN)

- `H/native-cost-gap/REVIEW.md` full-acceptance blockers:
  - `Big_Integer` `Normalize` with `Bignum_Limit` 200 raising `Storage_Error`;
  - runtime selection;
  - representability;
  - allocation failures.
- D1: release-path `Big_Integer` correspondence (`Resource_Run_Ledger` executables reached through `Resource_Run_Ledger_Wire.Decide`; `Canonical_Artifacts` reached through `Evaluation_Finalization.Seal`).
- D2: checks-build Ghost and contract `Big_Integer` evaluation.
- D-35: run-ledger native cost.
- Implicit controlled `Adjust` and `Finalize` in the runtime's `Big_Integer` implementation.
- Primary-stack, secondary-stack and heap lifetimes.
- Checked Ghost code.
- Actual assertion-build selection.
- Full native accepted-domain correspondence.

None is closed or narrowed by this design, and the successor reaches each of them through unchanged source call counts (C5–C16).

## C21. Evidence that would close this map (all OPEN; none exists)

| Id | Evidence | Closes |
|---|---|---|
| C21-a | Generated code for the matching builds (rel, chk, comp) of the successor and of S5, compared per call site: passing mechanism for every U actual, result-copy elision, temporaries, inlining | U, Rd and Ri native entries; X1–X4; C19 copy counts |
| C21-b | `-fstack-usage` per new routine and per changed export, compared with the original | stack growth (X4, C4, C15, C16) |
| C21-c | Secondary-stack high-water marks for `String`, `Byte_Array`, `Identity_Bytes` and `Optional_Marker` results at the original accepted maxima | C4, C18 |
| C21-d | Allocation-failure behaviour at the original's accepted input sizes: no new `Storage_Error` inside the originally accepted domain | §3.5; C4, C15, C16 |
| C21-e | Exception-path write behaviour of every export in C19, original and successor, on the matching library | D-36 |
| C21-f | Strict-build assertion evaluation counts (chk, comp), including the new `History_Index` Post | X5, C15 |
| C21-g | Independent actual gpt-6.1-sol review of the evidence above | all |
| C21-h (new) | Source-to-native correspondence: for each source count and construction in this map (S-CALL, S-RECHECK, S-OBJ, S-ASSIGN, S-CHECK, S-INIT, the C18 fit pairs and `'Image` evaluations), the matching generated code shows the emitted calls, tests and objects or their removal | every N-mark; the separation required by V3-RC6 |

Timing and constant-time behaviour are not claimed anywhere in this map.

## C22. Derived numbers in this map

Every derived number is a JACKAL `jackal_exact` result with `status=exact`, `formal=false`, assurance "exact rational arithmetic (not yet checker-covered)" and the three non_claims recorded in `jackal.json`. Each is arithmetic over source counts read from the text. None is a native, proof or acceptance fact.

| Use | JACKAL |
|---|---|
| One fit pair; atomic reads on an active value or exception path; `Well_Formed (Raw)` original chk and successor rel | J06 `parsed=1+1` → `exact=2` |
| `Well_Formed (Raw)` successor chk | J07 `parsed=1+1+1` → `exact=3` |
| `*_Fits` evaluations on an active fitting value or exception path, with the nested `Mark` active | J08 `parsed=2+2` → `exact=4` |
| `I64'Image` delta per active fitting value site | J09 `parsed=2-1` → `exact=1` |
| Array actuals of `Check_Decision` | J10 `parsed=1+2+1` → `exact=4` |
| All actuals of `Check_Decision` | J11 `parsed=4+1` → `exact=5` |
