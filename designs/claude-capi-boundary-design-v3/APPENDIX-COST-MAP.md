# C-API boundary consolidation v3: Appendix A-COST (native cost map, type- and call-site-resolved)

| | |
|---|---|
| Companion to | `DESIGN.md` in this directory (design v3). `§n` means a section of DESIGN.md. |
| Status | DRAFT_FOR_GPT61_REVIEW. **Every native cost, passing-mechanism, copy, allocation, assertion, failure and write-construction item here is OPEN.** |
| Base | S5 = `W/work/claude-composition-v5-beta/source`. Line citations are S5 lines (identical to S4 for the files cited). The installed tool tree is G = `/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1`. |
| Answers | RC6: it replaces v2's by-reference, no-copy and "all other evaluation deltas zero" statements with a map resolved by type and by call site, covering helper rechecks, new acceptance, marker and result copies, initialization, assertions, allocation, and exception and write effects. D-36 and the original native blockers stay OPEN (C19, C20). |

**Method and limits.**
- **Source reading only.** Every row comes from reading the S5 sources and the design. Nothing was compiled, executed, measured or disassembled, and no generated code was inspected.
- **What this map is.** It enumerates where the successor can differ natively from the original. It does not say how much the successor differs, and it does not establish that any difference is acceptable.
- **The obligation stays fixed.** A difference that makes an originally accepted computation fail, for example by exhausting storage at a smaller input, is a failure of the obligation. It is never an accepted refusal.

---

## C0. Legend

| Mark | Meaning |
|---|---|
| **E** | Elementary type: passed by copy (RM 6.2(3)). |
| **U** | Untagged, non-limited composite with no by-reference subcomponent: the passing mechanism is **unspecified** (RM 6.2(11)). GNAT's choice for the matching build is OPEN. By-copy passing of an array or large record adds a copy per call, and by-reference passing adds none. No row claims "no copy". |
| **R** | By-reference type (RM 6.2(4-9)): tagged, task, protected, explicitly limited, or containing one. **None was identified** (C2). |
| **Rd** | Definite function result: a constrained record, a record with defaulted discriminants, or a constrained array. It is returned through a return object, and whether the copy into the target is elided is OPEN. |
| **Ri** | Indefinite function result: an unconstrained array, `String`, or a record with discriminants and no defaults. It is returned on the secondary stack and copied into its target with a length or discriminant check. |
| rel / chk / comp | Builds: release (`-gnat2022 -gnatwa -gnatVa -gnatf -O2 -g -fPIC`, `core/worldline_core_sources.gpr:11-12`); checks = release plus `-gnata` (`:16-17`; the default build, `:9`); the pending component (`-gnat2022 -gnata -gnatVa -gnatwa -g -O0`, `pending-component/pending.gpr`). |
| RECHECK | A predicate evaluated again by a total value routine (V3, §3.2) or by an LD5 wrapper. It is dead on transport paths and costed in every build. |
| COPY | A new temporary, acceptance record, result object or copy that the original did not have. |
| INIT | A new initialization (D-28) or a moved one. |
| ASSERT | A new `-gnata` evaluation in chk or comp. An existing contract evaluated as often as before is marked `=`. |
| ALLOC | A change in heap, stack or secondary-stack allocation. Caller-count-sized allocations keep their position (§3.5). |
| EXC/WRITE | A change in exception or write behaviour. |
| `=` | Unchanged relative to the original, as far as source reading shows. |

**Cross-cutting deltas.** These apply to every new SPARK call and are not repeated in each row.

| Id | Delta | Basis |
|---|---|---|
| X1 | Every new value-routine call is a real call across compilation units: the builds have no `-gnatn` and no `Inline` aspect is added. There is a call and return, and argument passing per call. | `core/worldline_core_sources.gpr:11-12` |
| X2 | Under `-gnatVa`, validity checks may be generated at the new parameter, result and copy boundaries. Their placement is compiler-chosen and OPEN. | core switches |
| X3 | Each payload selection from an acceptance record (`D.Item`, `RA.Row`, and so on) carries a language-defined discriminant check in every build, since no checks are suppressed. Rule A1 makes it always pass, but it executes. | RM 4.1.3; A1 (§3.2 V4) |
| X4 | Each acceptance result is a definite discriminated record. Its temporary is sized either for the largest variant or for the actual variant, at the implementation's choice (OPEN), so per-row acceptance adds one such temporary per iteration. | RM 3.7, 3.8 |
| X5 | No new routine has a `Pre` or a functional `Post` (LD2), so `-gnata` evaluates no new contract of a new routine. Existing contracts of called relations are evaluated once per call wherever the relation is called. The rows list each such call and mark it `=` when the count is unchanged. The one exception is the new `History_Index` call (C15). | LD2 |

---

## C1. Withdrawn v2 statements

| v2 text (line) | Status in v3 |
|---|---|
| "**Arrays are not copied into SPARK.** They are passed by reference as `in` or `in out` formals." (v2:2510) | Withdrawn. Array mechanisms are unspecified (U), and each array actual is listed per site below. |
| "Every existing relation is called with the same arguments and as many times as on the original path, with the three constant-time exceptions in §10.3." (v2:2503) | Withdrawn. Re-evaluations are listed per site below; there are more than three. |
| "\| all other exports \| 0 \| n/a \| n/a \|" (v2:2537) | Withdrawn. Every export has at least the X1–X4 deltas, and most have site-specific ones. |
| "Both `Well_Formed` relations are bounded and constant-time" (v2:156) | Withdrawn as a cost claim. Source reading shows field and digest checks that do not depend on array lengths, but nothing was measured (C5, C6). |
| "Each per-element acceptance returns a small discriminated record by value, which adds one element-sized copy per row" (v2:2543) | Kept in substance and resolved per site. The temporary's size is OPEN (X4), and elements such as `F.Start_Row` and `T.Result_Record` are not small. |
| D-36 "That aligns with the documented no-write-on-refusal contract … The reviewer is to confirm it is equal-or-stronger behaviour." (v2:2648) | Withdrawn as a request for confirmation. D-36 is OPEN for every export in C19. |

---

## C2. Type classification

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
| `Worldline.Recovery.Optional_Marker` | `worldline-recovery.ads:9-16` | discriminants `(Present : Boolean; Length : Byte_Count)` **without defaults** in S5 | U | **Indefinite**; results are Ri, copied with a discriminant check |
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
| Run-ledger wire `Raw_Packet`, `Raw_Result`, `Raw_Row`, `Raw_Native`, `Raw_Row_Array`, `Raw_Native_Array` | `resource_run_ledger_wire.ads:96`, `:102`, `:52`, `:74`, `:105`, `:106` | record and array | U | — |
| Chain `Raw_Row`, `Raw_Anchors`, `Raw_Result`; `Chain_Row`; `Retained_Rows` | `worldline-chain_authority_wire.ads:17`, `:20`, `:24`; `worldline-chain_authority.ads:16`, `:19` | record and array | U | — |
| Completion C records `Journal_Row`, `Required_Row`, `Check_Row`, `History_Row`, `Request`, `Result`, `Context_Row`, `Context_Input`, `Row_Metadata`, `Metadata_Context` | `evaluation_completion_c.ads:44`, `:78`, `:82`, `:96`, `:105`, `:130`, `:163`, `:167`, `:195`, `:199` | record | U | `Request`, `Result` and `Context_Input` are large records; their sizes are not computed here (OPEN) |
| `Evaluation_Completion.Result_Record`, `Result_Array`; roster `Measured_Result`, `Measured_Array`, `Required_Check`, `Check_Array`; raw roster `Measured_Result`, `Measured_Array` | `evaluation_completion.ads:73`, `:83`; `evaluation_completion_roster.ads:12`, `:19`, `:20`, `:24`; `evaluation_raw_roster.ads:19`, `:25` | record and array | U | — |
| `Worldline.Evaluation_Authority.Optional_Bytes`, `Context_Fields`, `Context_Row`, `Context_Rows`, `Row_Metadata`, `Row_Metadata_Array`; `Worldline.Evaluation_Wire.Raw_Record` | `worldline-evaluation_authority.ads:96` (defaulted discriminant), `:107` (constrained by its enumeration index, so definite), `:113`, `:118`, `:245`, `:249`; `worldline-evaluation_wire.ads:29` | record and array | U | — |
| Finalization C `Row`, `Request`, `Result`; `Evaluation_Finalization.Start_Row`, `Start_Rows`; `Worldline.Collapse_Wire.Raw_Request` | `evaluation_finalization_c.ads:32`, `:41`, `:57`; `evaluation_finalization.ads:60`, `:72`; `worldline-collapse_wire.ads:33` | record and array | U | `Start_Row` has enumeration and variant components |
| New acceptance records (every `*_Acceptance`, `Decide_Acceptance`, `Context_Fields_Acceptance`, `Context_Row_Acceptance`) | §5, §7 | defaulted `Boolean` or enumeration discriminant | U | Definite and mutable; temporary size OPEN (X4) |
| `Readiness_Result` (moved) | from `evaluation_finalization_c.adb:366-369` | record `(Valid : Boolean; Ready : U8)` | U | — |
| `String` | Standard | unconstrained array | U | Results are Ri |

---

## C3. U1 `wl_resources_can_reserve`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | `Negative_Flag_Valid (Available_Negative)` in the guard | `worldline-resources_c_api.adb:45` (inline `> 1`) | U8 E → Boolean E | An X1 call replaces an inline comparison. |
| 2 | `Valid (…)` ×4 | `:46-49` | E | `=` (verbatim transport) |
| 3 | `Decode (…)` ×4 | `:55-58` | E → `Byte_Array` Ri | `=`. The four secondary-stack results exist as before. |
| 4 | `Can_Reserve_Value (Available_Negative, 4 arrays)` | new, wrapping `:53-62` | U8 E; 4 × `Byte_Array` U → U8 E | RECHECK: one flag comparison (V3). COPY: each array is passed through two call levels, `Can_Reserve_Value` then `Resource_Wire.Can_Reserve`; mechanism U at each, so by-copy would copy each array once more (OPEN). The `Available_Negative = 1` actual is now computed inside SPARK. |
| 5 | `Worldline.Resource_Wire.Can_Reserve` | `:53-58` | as original | `=` (one call). Its Post (`worldline-resource_wire.ads:11`) is evaluated once in chk, `=`. |

ALLOC: `=` (the four `Decode` results; their lifetime is the return expression instead of the `if` condition). EXC/WRITE: no writes, and the handler at `:63-64` is `=`.

## C4. U2 `wl_recovery_select`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | `Presence_Valid` in the guard | `worldline-recovery_c_api.adb:61` (inline) | 2 × U8 E → Boolean E | X1 call |
| 2 | `Present (Live_Present)`, `Present (Prepared_Present)` in the guard | `:63-64` (inline `= 1`) | U8 E → Boolean E | X1 call per marker |
| 3 | `Copy (Expected, Expected_Length)` | `:69-70` | E → `Identity_Bytes` Ri | `=` |
| 4 | `Live_Value`, `Prepared_Value`: `(if Present (Flag) then Copy (…) else Empty)` | `:71-79`; the original copied inside `Marker` (`:37-51`) | U8 E → Boolean; `Identity_Bytes` Ri | COPY: each present marker's bytes now live as a transport constant (secondary stack) until `Select_Value` returns. RECHECK: one `Present` call per marker. |
| 5 | `Select_Value (Expected_Value, Live_Present, Live_Value, Prepared_Present, Prepared_Value)` | new, wrapping `:71-82` | 3 × `Identity_Bytes` U; 2 × U8 E → U8 E | RECHECK: `Presence_Valid` (dead), plus the two constraint expressions of the constrained marker constants. Mechanism U for three arrays. |
| 6 | `Marker_Of (Flag, Value)` ×2, inside `Select_Value` | new, replacing `Marker` | U8 E; `Identity_Bytes` U → `Optional_Marker` **Ri** | COPY: a **second full copy** of each present marker's bytes (`Result.Value := Value`), returned on the secondary stack and copied into a constrained constant with a discriminant check. RECHECK: one flag test each. Uses `Present_Flag /= 1` for totality; this is equivalent for the flags 0 and 1 that the transport admits. |
| 7 | `R.Select_Action (…)` | `:82` | as original | `=` (one call). Its Post (`worldline-recovery.ads:33`) is evaluated once in chk, `=`. |

ALLOC: peak secondary-stack and stack use grows by up to one extra copy of each present marker. With caller lengths bounded only by `Byte_Count'Last`, this can lower the input size at which `Storage_Error` occurs. Such a case would turn an originally accepted call into the refusal 255, which is a **failure of the obligation**, not an accepted refusal (§3.5). OPEN, with evidence C21-a, C21-d. EXC/WRITE: no writes, and the handler is `=`.

## C5. U3 `wl_recovery_authorization_decide_v2`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | guards, `Raw` capture | `worldline-recovery_authorization_c_api.adb:129-139` | — | `=` |
| 2 | `W.Well_Formed (Raw)` in the transport | `:141-143` | `Raw_Request` U → Boolean | `=` (one call) |
| 3 | `Owned := Decide_Total (Raw)` | new, around `:146` | `Raw_Request` U → `Raw_Result` Rd | RECHECK: one extra `W.Well_Formed (Raw)` (`worldline-recovery_authorization_wire.ads:104-112`) per accepted call, in every build. COPY: the `Owned` local plus one copy into foreign memory. ASSERT: `W.Decide`'s Pre (`:166`) and Post (`:167`) are evaluated once each in chk, `=`. |
| 4 | `Result_At (Output).all := Owned` | `:146` (`Result_At (Output).all := W.Decide (Raw);`) | — | EXC/WRITE: the write construction changes (C19, D-36 OPEN). |

**`Well_Formed (Raw)` evaluations per accepted call:**

| Build | Original | Successor |
|---|---|---|
| rel | 1 | 2 (JACKAL `parsed=1+1` → `exact=2`) |
| chk | 2 (JACKAL `parsed=1+1` → `exact=2`) | 3 (JACKAL `parsed=1+1+1` → `exact=3`) |

A call refused by `Well_Formed` performs one evaluation in both versions. These counts are derived by reading the call sites. The JACKAL results are `status=exact` and `formal=false`; they are arithmetic facts about this reading and say nothing about the code's correctness.

## C6. U4 `wl_recovery_authorization_decide_v3`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | guards, `Raw` capture, `Data` allocation and unconditional copy | `worldline-recovery_authorization_v3_c_api.adb:139-157` | — | `=` |
| 2 | `W.Well_Formed (Data, Raw)` in the transport | `:158-160` | `Q.Byte_Array` U, `Raw_Request` U → Boolean | `=` |
| 3 | `Owned := Decide_Total (Data, Raw)` | new, around `:163` | `Q.Byte_Array` U; `Raw_Request` U → `Raw_Result` Rd | RECHECK: one extra `W.Well_Formed (Data, Raw)` (`worldline-recovery_authorization_v3_wire.ads:164-173`) per accepted call. It runs field, digest and span checks, uses `Q.Span_Valid` against `Data'Length`, and does not iterate over the arena contents, by source reading; nothing was measured. COPY: the array is passed through two call levels (mechanism U), plus the `Owned` local and one copy. ASSERT: `W.Decide`'s Pre (`:265`) and Post (`:266`) once each in chk, `=`. |
| 4 | `Result_At (Output).all := Owned` | `:163` | — | C19, D-36 |

Evaluation counts per accepted call are those of C5 (rel 1 → 2; chk 2 → 3; the same JACKAL results).

## C7. U5 `wl_recovery_protocol_decide_v1`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | guards, capture, `Owned_Result := (After => 0)` | `worldline-recovery_protocol_c_api.adb:49-59` | — | `=` |
| 2 | `Worldline.Recovery_Protocol_ABI.Apply (Raw, Owned_Result, Status)` | `:62` | `Raw_Request` U; `Raw_Result` U (`in out`); `C.int` E | `=`. It was already a call into another unit, and its Post (`worldline-recovery_protocol_abi.ads:20`) is evaluated once in chk. |
| 3 | `Result_At (Output).all := Owned_Result` | `:66` | — | `=` (a completed local written once) |

The only change is location. Native correspondence of the relocated code is still OPEN (D-15).

## C8. U6 `wl_reservation_lifecycle_plan`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | `Request_Valid (Present, Requested_First, Requested_Length)` in the guard | `worldline-reservation_lifecycle_c_api.adb:65-69` (inline) | U8, 2 × Size E → Boolean | X1 call |
| 2 | `Requested := Requested_Of (…)` | `:81-85` (aggregate) | E → `Optional_Identity` Rd | RECHECK: `Request_Valid` re-evaluated (V3; at most four comparisons). COPY: the result object. |
| 3 | `Selected_Mode := Operation_Of (Mode)` | `:86-90` | U8 E → `Operation` E | X1 call |
| 4 | per row `D := Accept_Row (Row)`; `Typed_Rows (I) := D.Item` | `:98-105` | `Row_C` U → acceptance (`Reservation_Entry`) Rd | Per row: X1, X3, X4, and one copy into `Typed_Rows (I)` (the original assigned an aggregate directly). |
| 5 | `L.Plan (…)` | `:108` | as original | `=`. Its Post (`resource_reservation_lifecycle.ads:103`) is evaluated once in chk. |
| 6 | `Publishes_Mask (Status)` | `:109` | E → Boolean | X1 call |
| 7 | per mask byte `Mask_Byte (Mask (I))` | `:111-112` (`Boolean'Pos (Mask (I))`) | Boolean E → U8 E | **One X1 call per byte** over a loop whose length the caller sets (`Removed_Length` ≤ `Byte_Count'Last`). This is linear extra call overhead (OPEN). |
| 8 | `Status_Code (Status)` | `:115` | E → U8 E | X1 call |

ALLOC: `=`. EXC/WRITE: `=`; mask bytes are written only for `No_Change` or `Removal_Planned`.

## C9. U7 `wl_resource_ledger_compute`, `wl_resource_ledger_headroom`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | per row `D := Accept_Row (V)`; `Typed_Rows (I) := D.Row`; `Slots (I) := D.Slot` | `worldline-resource_ledger_c_api.adb:150-159` | `Row_C` U → acceptance (`Reservation_Row`, `Output_Span`) Rd | Per row: X1, X4, two X3 selections, and two copies (the original assigned aggregates directly). The two `Decode` calls (`:157`) move inside, with an unchanged count. |
| 2 | `L.Compute (…)` | `:162-163` | as original | `=`. Its Post (`resource_ledger.ads:205`) is evaluated once in chk. |
| 3 | `Write_Data` ×2 | `:164-165` | — | `=` |
| 4 | per detail `Encode_Quantity (Typed_Details (I))` | `:166-170` (body-local `Encode`, `:86-88`) | `Q.Quantity` U → `Quantity_C` Rd | Per detail: **an X1 call into another unit replaces a body-local expression function**, which the original unit's own `-O2` could inline (OPEN). The result is copied into foreign memory, as before. |
| 5 | `As_Result (Result).all := Result_Of (Status, Total)` | `:171-172` (aggregate) | `Result_Status` E; `Q.Quantity` U → `Result_C` Rd | COPY: a result temporary, then a copy (C19). |
| 6 | headroom `HI := Accept_Headroom_Inputs (A, W, F)` | `:203-205`, decodes at `:213` | 3 × `Quantity_C` U → acceptance (3 × `Q.Quantity`) Rd | X4, and three X3 selections passed as actuals of `L.Compute_Headroom` (mechanism U). The original passed `Decode (…)` results directly. |
| 7 | `L.Compute_Headroom (…)` | `:212-214` | as original | `=`. Its Post (`resource_ledger.ads:263`) is evaluated once in chk. |
| 8 | `As_Result (Result).all := Result_Of (Status, Typed_Result)` | `:216-218` | as 5 | as 5 |

ALLOC: `=`. EXC/WRITE: the unconditional writeback keeps its original order. A partial write on an exception during writeback stays possible, as in the original. Result construction is a C19 item.

## C10. U8 `wl_resource_policy_admit`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | `IA := Accept_Input (V)` | `worldline-resource_policy_c_api.adb:135-151` | `Input_C` U → acceptance (`Policy_Input`) Rd | X4. Ten `Shape` tests and ten decodes move inside, with unchanged counts. `IA.State` is passed to `P.Admit` with an X3 check and mechanism U. |
| 2 | per row `D := Accept_Disk (Row)` | `:159-164` | `Disk_C` U → acceptance (`Disk_Row`) Rd | Per row: X1, X3, X4, and a copy. |
| 3 | `Decode_Data (Data, Data_Length)` | `:168` | — | `=` |
| 4 | `Decision := P.Admit (Arena, IA.State, Rows)` | `:169` | as original | `=`. Its Post (`resource_admission.ads:201`) is evaluated once in chk. |
| 5 | `As_Result (Result).all := Encode_Decision (Decision)` | `:171-176` (aggregate) | `Decision` U → `Result_C` Rd | C19 |

## C11. U9 `wl_evaluation_history_select`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | `Final_Flag_Valid`, `Final_Row_Present` ×2 | `worldline-evaluation_history_c_api.adb:136`, `:139`, `:157` | U8 E → Boolean | X1 calls |
| 2 | `QA := Accept_Query (Raw_Q)` | `:151-156`, with the decode moved from `:174-177` (M4) | `Query_C` U → acceptance (`H.Query`) Rd | X4. The decoded query lives across the row loop (stack). The decode itself is pure and its count is unchanged. |
| 3 | `FA := Accept_Final_Row (V)`; `F := FA.Item` | `:161-162` | `Row_C` U → acceptance (`H.Optional_Record`) Rd | X3, X4, one copy |
| 4 | per row `D := Accept_Row (V)`; `History (I) := D.Item` | `:170-171` | `Row_C` U → acceptance (`H.Evaluation_Record`) Rd | Per row: X1, X3, X4, one copy |
| 5 | `Result := Select_Result (A, History, F, QA.Item)` | `:179-183` | `R.Byte_Array` U, `H.History` U, `H.Optional_Record` U, `H.Query` U → `Selection_C` Rd | One extra call level around `H.Select_Evidence`, with mechanism U for the arrays. The aggregate of `:180-183` is built in SPARK. `H.Select_Evidence`'s Post (`evaluation_history.ads:321`) is evaluated once in chk, `=`. |
| 6 | `As_Selection (Output).all := Result` | `:185` | — | `=` (a completed object written once) |

## C12. U12 `wl_resource_run_ledger_check_v1`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | guards; capture; four allocations; four unconditional copy loops | `resource_run_ledger_c_api.adb:192-216` | — | `=` |
| 2 | `O := Check_Decision (Data, Raw, Before, Proposed, Observed)` | `:217-219` | `Q.Byte_Array` U, `Raw_Packet` U, 2 × `Raw_Row_Array` U, `Raw_Native_Array` U → acceptance (`Raw_Result`) Rd | `W.Well_Formed (…)` (`resource_run_ledger_wire.ads:342-350`, which iterates over the rows) is evaluated **once**, as in the original: this is the cost-neutral pattern. `W.Decide` is called once; its Pre (`:362`) and Post (`:363`) are evaluated once each in chk, `=`. COPY: five array actuals pass one extra call level (mechanism U), plus the acceptance temporary. The release-path `Big_Integer` code reached through `W.Decide` is unchanged (`=`; D1, D-35 OPEN). |
| 3 | `Result_At (Output).all := O.Value` | `:219` (`… := W.Decide (…)`) | — | C19 |

## C13. U13 `wl_chain_authority_replay_v1`

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | guards; `H` capture; `Owned` allocation; `W.Well_Formed (H)` | `worldline-chain_authority_c_api.adb:70-88` | — | `=` |
| 2 | per row `D := Accept_Row (Raw)`; `Owned (I) := D.Item` | `:91-95` | `Raw_Row` U → acceptance (`Chain_Row`) Rd | Per row: `W.Well_Formed (Raw)` and `W.Decode (Raw)` are called once each, as before. Decode's Pre (`worldline-chain_authority_wire.ads:53`) and Post (`:54`) are evaluated once in chk, `=`. Also X1, X3, X4, and one copy (the original assigned the `Decode` result directly). |
| 3 | `RV := Replay_Value (Owned, H)` | `:99` | `Retained_Rows` U, `Raw_Anchors` U → acceptance (`Raw_Result`) Rd | RECHECK: one extra `W.Well_Formed (H)` (`worldline-chain_authority_wire.ads:37-42`) per accepted call, in every build. `W.Decide`'s Pre (`:60`) and Post (`:61`) are evaluated once in chk, `=`. COPY: the `Owned` array passes one call level (mechanism U), plus the acceptance temporary. |
| 4 | `Result_At (Output).all := RV.Value` | `:99` (`… := W.Decide (Owned, H);`) | — | C19 |

## C14. U10, U11 `wl_pending_decide_v1`, `wl_pending_decide_v2` (and the component under D-13)

| # | Successor site | Original (v1; v2) | Types | Delta |
|---|---|---|---|---|
| 1 | `Header_Valid (R)`, `Request_Fields_Valid (R)` in the guard | `evaluation_pending_c.adb:120`, `:128-131`; v2 `:141`, `:149-152` | `Request` U → Boolean | X1 calls; `R` is passed with mechanism U |
| 2 | per row `D := Accept_Row (V)`; `J (I) := D.Item` | `:146-158`; v2 `:167-181` | `Row` U → acceptance (`E.Intent`; `V2.Intent`) Rd | Per row: X1, X3, X4, one copy (the original assigned an aggregate directly) |
| 3 | `O := Decide_Value (A, J, R)` | `:161-168`; v2 `:184-192` | `E.Bytes` U, `E.Journal` / `V2.Journal` U, `Request` U → acceptance (`Result`) Rd | RECHECK: `Header_Valid (R)` and `Request_Fields_Valid (R)` are evaluated again (dead). The `Convert (R.…)` decodes are inside, with an unchanged count. `E.Decide` / `V2.Decide` is called once; its Post (`evaluation_pending.ads:163`; `evaluation_pending_v2.ads:86`) is evaluated once in chk, `=`. COPY: the result aggregate is built in SPARK inside an acceptance temporary. |
| 4 | `Result_Pointers.To_Pointer (Output).all := O.Value` | `:165-168`; v2 `:188-192` (aggregate) | — | C19 |

The component under D-13 option (i) (§16.1) has the same deltas in its own build (comp: `-gnata -gnatVa -O0`). At `-O0` no temporary is elided; the effect is OPEN. The original component carries Off copies that make no SPARK calls, so the mirror adds X1 to X4 in the component's Off text as well.

## C15. U14 completion

**`wl_completion_decide_v1` (original `evaluation_completion_c.adb:393-528`)**

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | `Decide_Header_Valid (R)`, `Decide_Fields_Valid (R)` in the chain | `:408`, `:416-420` | `Request` U (a large record) → Boolean | X1 calls; mechanism U for `R` |
| 2 | arrays `A`, `J`, `Measures`, `Captured`, `Retained_Results`, `History`, `Required` | `:423-429` | — | `=` (same declarations and order, A-BIND §B4.14) |
| 3 | per journal row `Accept_Journal_Row (X)` | `:446-453` | `Journal_Row` U → acceptance (`V.Intent`) Rd | Per row: X1, X3, X4, one copy |
| 4 | per captured row `Accept_Captured_Row (X)` | `:458-465` | `Check_Row` U → acceptance (`T.Result_Record`; `Roster.Measured_Result`) Rd | Per row: X1, X4, two X3 selections, two copies |
| 5 | per retained, history and required row `Accept_Result_Row`, `Accept_History_Row`, `Accept_Required_Row` | `:468-475`, `:477-484`, `:486-493` | `Check_Row`, `History_Row`, `Required_Row` U → acceptance (`T.Result_Record`, `H.Evaluation_Record`, `Roster.Required_Check`) Rd | Per row: X1, X3, X4, one copy |
| 6 | `Decide_Value (R, A, J, Captured, Measures, Retained_Results, History, Required, Response, Status)` | `:431-439`, `:495-520` | `Request` U, `P.Bytes` U, `V.Journal` U, 2 × `T.Result_Array` U, `Roster.Measured_Array` U, `H.History` U (**`in out`**), `Roster.Check_Array` U, `Result` U (`out`), `C.int` E (`out`) | RECHECK: `Decide_Header_Valid`, `Decide_Fields_Valid` (dead). **New call `T.History_Index (J, History, Selected)` (`evaluation_completion.ads:332-338`) on the summary path, with its Post (`:337`) evaluated in chk; this is the one new `-gnata` evaluation (X5, §5.4).** COPY: under by-copy passing, `in out History` would copy the whole history array in and out; `out Response` likewise (OPEN). INIT: `Response := Initial_Response` on every path (moved from the declaration at `:436-439`, same values). `T.Decide` (`:496`), `T.Apply` (`:499`), `T.Find_Run` (`:504`) and `Roster.Classify` (`:507`) keep their counts; their Posts (`evaluation_completion.ads:264`, `:420`, `:138`; `evaluation_completion_roster.ads:144`) are evaluated in chk as before, `=`. |
| 7 | `Outputs.To_Pointer (Output).all := Response` | `:522` | — | `=` (a completed local written once) |

**`wl_completion_raw_decide_v1` (`:529-693`).** The same rows as decide, with these differences:
- the chain uses `Raw_Header_Valid` (`:545`) and `Raw_Fields_Valid` (`:557-561`);
- each captured row makes two acceptance calls: `Accept_Raw_Check_Row` (`:599-603`, X1, X3, X4) and `Accept_Raw_Measure` (`:605-614`), whose inside calls `W.Well_Formed (Wire)` (`:610`) once as before;
- `Raw_Decide_Value` re-checks `Decide_Header_Valid` and `Raw_Fields_Valid` (§5.5) and adds the same `History_Index` call;
- `Decide_Envelope` (`:646`; Post `worldline-evaluation_authority.ads:89`), `T.Apply` (`:650`), `T.Find_Run` (`:655`), `Raw_Roster.Row_Bound` (`:667`, once per measure as before) and `Raw_Roster.Classify` (`:672`; Post `evaluation_raw_roster.ads:143`) keep their counts, `=`;
- the post-decision 255 (`:657-671`) is unchanged.

**`Completion_Transport.Context_Matches` (`:733-869`)**

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | `Context_Header_Valid (R, X)`, `Context_Fields_Valid (R, X)`, `Context_Agent_Matches (X, Raw_Agent, Agent_Confinement)` in the chain | `:765`, `:767-774`, `:780` | `Request` U, `Context_Input` U (a large record), `W.Raw_Record` U, U8 E → Boolean | X1 calls; mechanism U for two large records per call |
| 2 | `FA := Accept_Context_Fields (X)` | `:795-804` | `Context_Input` U → acceptance (2 × `CA.Context_Fields`) Rd | INIT: two local arrays initialized `(others => (Present => False))` inside the routine, the same values as the original's default initialization at `:789`, then copied into the result (two array copies). `FA.Expected` and `FA.Observed` are later actuals of `Context_Join_Value`, with X3 and mechanism U. |
| 3 | per row pair `RA := Accept_Context_Row (Original, Owned)` | `:805-831` | `Check_Row` U, `Context_Row` U → acceptance (`T.Result_Record`; `CA.Context_Row`) Rd | Per row: INIT of `Joined`'s two field arrays inside (same values as `:791`), X1, X4, two X3 selections, two copies. |
| 4 | per required pair `QA := Accept_Required_Pair (Original, Owned)` | `:832-848` | 2 × `Required_Row` U → acceptance (2 × `Roster.Required_Check`) Rd | Per row: X1, X4, two X3 selections, two copies |
| 5 | `V := Context_Join_Value (R, X, Raw_Collapse, Data, Context_Data, FA.Expected, FA.Observed, Rows, Joined, Required, Expected_Required)` | `:850-857` | `Request` U, `Context_Input` U, `CW.Raw_Request` U, 2 × `P.Bytes` U, 2 × `CA.Context_Fields` U, `T.Result_Array` U, `CA.Context_Rows` U, 2 × `Roster.Check_Array` U → `Join_Verdict` E | RECHECK: `Context_Header_Valid` and `Context_Fields_Valid` (dead). `CA.Join_Context` is called once; its Post (`worldline-evaluation_authority.ads:236`) is evaluated in chk, `=`. Eleven actuals with mechanism U. |
| 6 | `Join_Code (…)` ×2 | `:859-861` | Boolean E → `C.int` E | X1 calls |

**`Completion_Metadata_Matches` (`:909-986`).**
- `Metadata_Header_Valid (R, X)` (`:932-933`): an X1 call with `Metadata_Context` U.
- Per row, `Accept_Metadata_Row (Original, Owned)` (`:953-968`) returns an acceptance carrying `T.Result_Record` and `CA.Row_Metadata`: X1, X4, two X3 selections, two copies.
- `CA.Join_Metadata` (`:974`; Post `:273`) is unchanged, `=`.
- `Join_Code`: an X1 call.

**`Completion_Transport.Metadata_Base` (`:893-907`).** `Metadata_Version_Valid (X)` (`:901`) is an X1 call with `Metadata_Context` U.

ALLOC for all completion units: `=` (every caller-count-sized array keeps its position, §3.5). EXC/WRITE: `=` (decide and raw write once; the others write nothing).

## C16. U15 finalization (including D-28)

**`wl_finalization_decide_v1` (`evaluation_finalization_c.adb:121-257`)**

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | `Request_Header_Valid (X)`, `Request_Fields_Valid (X)` in the chain | `:138`, `:145-153` | `Request` U → Boolean | X1 calls |
| 2 | per plan `PA := Accept_Plan (Q)` | `:170-178` | `Required_Row` U → acceptance (`Required_Check`) Rd | Per plan: X1, X3, X4, one copy |
| 3 | `Needs_Rows (X)` | `:183-188` (branch on `X.Operation`) | `Request` U → Boolean | X1 call |
| 4 | per row `RA := Accept_Row (Q)` (Operations 2 and 3 only) | `:189-199` | `Row` U → acceptance (`F.Start_Row`) Rd | Per row: X1, X3, X4 (`Start_Row` has variant components, so the temporary may be sized for its largest variant), one copy into `Captured (K)` |
| 5 | `O := Decide_Rows_Value (X, A, Required, Captured)` or `O := Decide_No_Rows_Value (X, A, Required)` | `:163-244` | `Request` U, `P.Bytes` U, `Raw_Roster.Check_Array` U, `F.Start_Rows` U → acceptance (`Result`) Rd | RECHECK: `Request_Header_Valid`, `Request_Fields_Valid` and the operation selector (dead). `S := Convert (X.Start)` (`:163`) and the `Response` initialization (`:164-166`) move inside, same work. `F.Classify_Capture` (`:204`; Post `evaluation_finalization.ads:265`) and `F.Seal` (`:219`; Post `:394`) keep their counts, `=`. `Seal`'s release-path `Canonical_Artifacts` `Big_Integer` code is unchanged (D1 OPEN). COPY: an acceptance temporary holding `Result`. |
| 6 | `Outputs.To_Pointer (Output).all := O.Value` | `:249` (`… := Response;`) | — | The same pattern (a completed object copied once) plus one temporary; C19. |

ALLOC: `Captured` is allocated for every operation, as the original does at `:162`, `=`. Operations 0 and 1 neither pass nor read it (§5.1).

**`Finalization_Transport.Final_Context_Matches` (`:259-355`)**

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | `Native : aliased Result := Initial_Result` | `:264` (`Native : aliased Result;`, uninitialized) | — | INIT (D-28): one full-record initialization per call |
| 2 | `Final_Seal_Ready (Seal_Status, Native)` | `:273-274` | `C.int` E, `Result` U → Boolean | X1 call. The address-based self-call `Finalization_Decide (Input, Native'Address)` is `=` (D-26). |
| 3 | `Final_Plans_Valid (X)` | `:282-286` | `Request` U → Boolean | X1 call |
| 4 | per row `Projected_Rows (I) := Final_Projected_Row (X, Original)` | `:300-313` | `Request` U, `Row` U → `K.Check_Row` Rd | Per row: X1, and **`X` is passed per row** (mechanism U; by-copy passing would copy the request once per row). The six-field `K.Binding` aggregate, built once in the original (`:294-295`), is **rebuilt per row** inside the routine. This adds linear per-row work (OPEN). A separately reviewed refinement could pass a once-computed binding, but it is not adopted here. |
| 5 | per plan, verbatim copy | `:314-318` | — | `=` |
| 6 | `Projection := Final_Projection (X, Native, Projected_Rows'Address, Projected_Plans'Address)` | `:294-331` | `Request` U, `Result` U, 2 × `System.Address` E → `K.Request` Rd | `Bound` and `Empty_Capture` are built inside, once. COPY: a result temporary, then a copy into `Projection` (the original assigned the aggregate directly). |
| 7 | `Completion_Transport.Context_Matches (…)`, `Completion_Transport.Metadata_Base (…)`, `Completion_Metadata_Matches (…)` | `:334-342` | — | Deltas as in C15 |

**`wl_collapse_decide_finalization_v1` (`:357-509`)**

| # | Successor site | Original | Types | Delta |
|---|---|---|---|---|
| 1 | `Read_Ready`: `Kind_Of (Kind)` | `:377-395` | U32 E → enumeration E | X1 call per invocation |
| 2 | `Ordinary : aliased Evaluation_Completion_C.Result := Initial_Response` (Kind 1 branch) | `:373` (uninitialized; declared for every kind) | — | INIT (D-28): one full-record initialization per Kind-1 call. The object is now declared only in its branch. |
| 3 | `Ordinary_Readiness (Status, Ordinary)` | `:379-384` | `C.int` E, `K.Result` U → `Readiness_Result` Rd | X1, result copy |
| 4 | `Finalized : aliased Result := Initial_Result` (Kind 2 branch) | `:374` (uninitialized) | — | INIT (D-28), as row 2 |
| 5 | `Finalized_Readiness (Status, Finalized)`; `Finalized_Operation_Readiness (X, Finalized)` | `:386-394` | `C.int` E, `Result` U, `Request` U → `Readiness_Result` Rd | RECHECK: `Promotion <= 1`, re-tested so that the `U8` conversion stays total (dead) |
| 6 | `Authority.Dependencies (Bound)`; `Authority.Needs_Primary/Needs_Staged/Needs_Agent (Needed)` | `:420`, `:427`, `:439`, `:453` | — | `=` |
| 7 | `Agent_Ready := Agent_Readiness (Owned_Agent, Agent_Confinement)` | `:463-469` | `W.Raw_Record` U, U8 E → U8 E | `W.Confined_Admit_Wire` is called once; its Post (`worldline-evaluation_wire.ads:164`) is evaluated in chk, `=`. X1. |
| 8 | `Context_Join_Needed (Agent_Ready, P_Ready)`, `Context_Join_Needed (Agent_Ready, S_Ready)` | `:473-484` | E → Boolean | X1 calls; `Agent_Ready = 1` is tested twice instead of once |
| 9 | `Decision := Mixed_Collapse_Decision (Bound, Agent_Ready, P_Ready, S_Ready)` | `:485-487` | `CW.Raw_Request` U, 3 × U8 E → U8 E | COPY: `(Bound with delta …)` creates **one full temporary copy of the collapse request** per call; the original mutated the transport variable in place. `CW.Decide_Wire` is called once; its Post (`worldline-collapse_wire.ads:257`) is evaluated in chk, `=`. |
| 10 | `Mixed_Authorized (Decision)`; `Mixed_Metadata_Needed (…)` ×2 | `:489`, `:491`, `:497` | E → Boolean | X1 calls. `Mixed_Metadata_Needed` calls `Needs_Primary` or `Needs_Staged` once each, as the original did at `:491` and `:497`. |

EXC/WRITE: `=`. The mixed entry writes nothing foreign. The double `Seal` on the Kind-2 path is kept (D-27).

## C17. `Authority_Glue` retargeting and effects across the C_API unit

| Site | Original | Successor | Delta |
|---|---|---|---|
| `K.Raw_Decide (…)` ×2 | `core/worldline-c_api.adb:784-785`, `:791-792` | `Completion_Raw_Decide (…)` | Profile unchanged. The callee now lives in the same unit; whether the compiler inlines it is OPEN. Per-call deltas are those of C15. |
| `K.Context_Matches (…)` ×2 | `:810-811`, `:813-814` | `Completion_Transport.Context_Matches (…)` | As above |
| `K.Metadata_Base (…)` ×2 | `:852`, `:855` | `Completion_Transport.Metadata_Base (…)` | As above |
| `K.Metadata_Matches (…)` ×2 | `:866-867`, `:869-870` | `Completion_Metadata_Matches (…)` | As above |

Across the unit:
- The C_API body gains `with Ada.Text_IO;` and `with Ada.Exceptions;` (§3.6). Their elaboration and runtime dependencies were already part of the library through `Evaluation_Completion_C`.
- Each transport package adds its own pointer-instance code. That code is the same as in the original units, which drop it (G7).

## C18. Diagnostics (RC1)

| Path | Original | Successor | Delta |
|---|---|---|---|
| Inactive `Mark` site | One cross-unit or intra-unit call to `Diagnostic_Mark`, then one atomic read (`evaluation_completion_c.adb:44`) | The transport `Mark` (a C_API-local call), then `Diagnostic_Begin_Line`, then one atomic read | One more call level. The atomic accesses are the same (§4.6). |
| Inactive `Value` site | `Diagnostic_Value`, one atomic read (`:55`) | `Value` → `Diagnostic_Begin_Value`, one atomic read. `Value_Fits` and `I64'Image` are short-circuited away when inactive. | One more call level |
| Inactive `Exception` site | `Diagnostic_Exception`, one atomic read (`:65`); `Exception_Information` is not called | `Exception_Text` → `Diagnostic_Observe`, one atomic read; `Exception_Information` is not called | One more call level |
| Active `Mark` | Catenation inline in the `Put_Line` actual; `Put_Line`; `Flush` (`:46-47`) | `Line_Fits`, then `Diagnostic_Line` (a `String` result, Ri, on the secondary stack), then `Put_Line`, then `Flush` | One length test, one call, a secondary-stack result (the original's catenation was also a temporary) |
| Active `Value` | `I64'Image` once, catenation, nested `Mark` (`:56`) | `I64'Image` in `Value_Fits` and again in `Diagnostic_Value_Site`, catenation, nested `Mark` | **+1 `'Image` per active value site**, plus a length test. The nested `Mark` performs its own atomic read, as the original's nested call did. |
| Active `Exception` | `Exception_Information`, catenation, nested `Mark` (`:67`) | `Exception_Information` (transport), `Exception_Fits`, `Diagnostic_Exception_Site`, nested `Mark` | One length test, one call |
| `Native_Diagnostic_Control` | Inline check-then-act (`:73-88`) | `Diagnostic_Control_Of`, `Diagnostic_Start` or `Diagnostic_Stop`, transport `Mark` | Calls only; the same atomic reads and writes in the same order (§4.6) |

ASSERT: none, unless a reviewer requires the optional small Posts (§4.7), which would each add a chk evaluation. EXC: the latch semantics are unchanged. An overlong catenation latches through an exact SPARK length test instead of `Constraint_Error`, with the same effect.

## C19. D-36: write construction, every export (OPEN)

| Export | Original construction (S5) | Successor construction | Status |
|---|---|---|---|
| v2 | `Result_At (Output).all := W.Decide (Raw);` (`worldline-recovery_authorization_c_api.adb:146`), a function result assigned through an access value, possibly built in place | `Owned : constant W.Raw_Result := …Decide_Total (Raw);` then one copy | OPEN |
| v3 | `… := W.Decide (Data, Raw);` (`…_v3_c_api.adb:163`) | `Owned` then one copy | OPEN |
| chain | `Result_At (Output).all := W.Decide (Owned, H);` (`worldline-chain_authority_c_api.adb:99`) | `RV := Replay_Value (…)`, then a copy of `RV.Value` | OPEN |
| run ledger | `Result_At (Output).all := W.Decide (…);` (`resource_run_ledger_c_api.adb:219`) | `O := Check_Decision (…)`, then a copy of `O.Value` | OPEN |
| pending v1, v2 | An aggregate of `P` fields assigned through an access value (`evaluation_pending_c.adb:165-168`; `evaluation_pending_v2_c.adb:188-192`) | `O := Decide_Value (…)`, then a copy of `O.Value` | OPEN |
| policy | An aggregate of `D` fields assigned through an access value (`worldline-resource_policy_c_api.adb:171-176`) | The `Encode_Decision (Decision)` result assigned | OPEN |
| ledger | `Encode (…)` results and an aggregate assigned through access values (`worldline-resource_ledger_c_api.adb:166-172`, `:216-218`) | `Encode_Quantity` and `Result_Of` results assigned | OPEN |
| lifecycle mask | `Boolean'Pos (Mask (I))` per byte (`worldline-reservation_lifecycle_c_api.adb:111-112`) | `Mask_Byte (Mask (I))` per byte | OPEN (cost only) |
| protocol | A completed local written once (`worldline-recovery_protocol_c_api.adb:66`) | Unchanged | Copy counts OPEN |
| history | A completed constant written once (`worldline-evaluation_history_c_api.adb:185`) | Unchanged; the constant now comes from SPARK | Copy counts OPEN |
| completion decide, raw | A completed local `Response` written once (`evaluation_completion_c.adb:522`, `:687`) | Unchanged; `Response` is an `out` actual | Copy counts OPEN |
| finalization decide | A completed local `Response` written once (`evaluation_finalization_c.adb:249`) | `O.Value` written once, plus one acceptance temporary | Copy counts OPEN |

For every row, three things must be established on the matching builds: the order in which the completed result is constructed, its copy and padding effects, and its exception and no-write semantics. The malformed-input fixture `tests/test_recovery_witness_relation.py:174-179` establishes none of them. No global transactional-write claim is made. C-14 tests the successor's local-then-write behaviour as a proposed behaviour only, never as baseline.

## C20. Original native blockers (unchanged, OPEN)

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

None is closed or narrowed by this design, and the successor reaches each of them through unchanged call counts (C5–C16).

## C21. Evidence that would close this map (all OPEN; none exists)

| Id | Evidence | Closes |
|---|---|---|
| C21-a | Generated code for the matching builds (rel, chk, comp) of the successor and of S5, compared per call site: parameter-passing mechanism for every U actual, result-copy elision, temporaries, inlining | the U, Rd and Ri entries; X1–X4; C19 copy counts |
| C21-b | `-fstack-usage` per new routine and per changed export, compared with the original | stack growth (X4, C4, C15, C16) |
| C21-c | Secondary-stack high-water marks for `String`, `Byte_Array`, `Identity_Bytes` and `Optional_Marker` results at the original accepted maxima | C4, C18 |
| C21-d | Allocation-failure behaviour at the original's accepted input sizes: no new `Storage_Error` inside the originally accepted domain | §3.5; C4, C15, C16 |
| C21-e | Exception-path write behaviour of every export in C19, original and successor, on the matching library | D-36 |
| C21-f | Strict-build assertion evaluation counts (chk, comp), including the new `History_Index` Post | X5, C15 |
| C21-g | Independent actual gpt-6.1-sol review of the evidence above | all |

Timing and constant-time behaviour are not claimed anywhere in this map.
