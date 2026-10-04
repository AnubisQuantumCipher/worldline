# D2 checked-build Ghost and contract evaluation inventory (draft v1)

- **Status:** DRAFT_FOR_GPT61_REVIEW. Nothing here is reviewed, accepted, measured or proved. It closes nothing. D2 stays OPEN.
- **Author:** Claude Code lead claude-opus-5-5 (analysis subagent), 2026-10-04.
- **Method:** static reading of source only. Nothing was compiled, proved, built, executed, imported or measured. No timings
  are claimed anywhere.
- **Evidence labels**
  - `[OBS]` text read from a file or a read-only tool output.
  - `[DER]` derived by reasoning (not machine-checked).
  - `[J..]` JACKAL result, listed in section 9: status=exact, formal=false, non_claims carried there verbatim.
- **Write location:** written to the lead's isolated worktree path given in the coordinator's correction. The originally
  named `work/claude-d2-checked-ghost-inventory-v1/` was never created.

W = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow`.

## 0. Subject and identities

**Candidate:** `W/work/claude-composition-v5-beta/source` [OBS].
- `author-freeze.json` sha256 `2db0d758d7bce87b72962628896e1f7cddb7aba161c690469fe284d12f9b11b2`.
- `composition.json` `a0e0bb5cbca667ad8e02eff9ea79c80459f4066544542178362257dbe347fa3e`.
- `source-inventory.json` `3407119bdf9e8497ed8259d76ea783f6d207f15fd155ee9c45534c3b0eaf937a`.
- The gpt-6.1-sol review disposition is `QUALIFIED_SOURCE_COMPOSITION`. That review keeps
  `EXACT_NATIVE_MODEL_CHECKED_GHOST_COST` OPEN (`review/gpt61-v1/review.json`) [OBS].
- The D1 v2 review (`claude-native-bigint-d1-design-v2/review/gpt61-v1/review.json`) keeps O-GHOST (D2) OPEN. Its F11
  says the default build is checks/-gnata [OBS].

**Base for comparison:** `W/work/reviewed-common-proof-source-composition-v4/source`. See section 7.

**Candidate file sha256 [OBS]:**

| File | sha256 |
|---|---|
| core/worldline-chain_authority.ads / .adb | 4b0874385a6f7e3acb7663a834f3ef168307af6786ba3cbbaad45bade5f78d02 / a72d60bd07d5d591b4232c1e3d7857ecd67b6613e1f3e0ea0bccf9e891abbbe4 |
| core/worldline-chain_authority_wire.ads / .adb | f8cdfc4e323bcc78afbb4a032198a5fc10627671b4f333088d4160d903a7eda6 / ab5fdba5291c115a5ffabc3538b443336b504e8484ba2096d573fa6ca4030ad1 |
| core/worldline-chain_authority_c_api.adb | dae2748bdb87c55b90ed73bd82fe882d5d4c64ca3af944f463dd4798ca66328a |
| core/resource_quantities.ads / .adb | 7bb5ebf110cfb6caec3c204e97be8bc4d7a93ebdb3b9e6251f48a456eeae1a28 / 5e87d8a0e874a0f2010070e31140ee1eb638ff866beea6f85da1f41599863b9b |
| core/resource_ledger.ads / .adb | f290ca5e5b39d351359227115081ab3fe09c9976a0e5de6a844a48b394742946 / 4a5fe307f79a8d6cf0afa7bec2f3fe2a6e58b6eeaf0c8d8790333c4dc6b24fe1 |
| core/resource_run_ledger.ads / .adb | 9a761421da3799da2ecb3b8b1df3daa05b5d4c050f31bf32f2d12e50687d6c02 / 8e7c02c50954b9bb3ef2a7cf4a818931b6d0871c88c221e528eee81a964dbe42 |
| core/worldline-resources.ads / .adb | 571e729f77c605d6589b18f753e635da2a324d6363860d08285551357c51b587 / 053d9c59ad1223939e98913af7b56cf860a4979444aea169dd16b876bfe7f3dc |
| core/canonical_artifacts.ads / .adb | bb62783aefa5b2b105dcec33d0273165d2cb5ba86c07006df11f101f5a057fee / 979466c0c24fadb5ae5f4aac29a08cff680d367c4356ec69faa0596c7c5f2aa3 |
| core/evaluation_epoch.ads / .adb | 7dca9f1ee1501e606f028577f9a6a145a4db1d2db768bcbe4faf7027f5b0fa64 / 61b009aca52b112a372501b119d687cfee8258b7788b7a0201bc4f932dddd7aa |
| core/resource_reservation_transition.ads / .adb | 886bb13a69cdf029bc10703b39bce49eaeadb9be543d8449509badf6e6fd2aae / 705f7102a64c06e4e03ab354fc3deac928129249fcb054146a486291ff1f04f3 |
| core/resource_admission.ads / .adb | 269a14b1f9e23a8ff35c2d76d8cdb4bd9e530721f4e17fd6e06a5b3f821a94d0 / 56561dc5fbe3a1cd62710b34678fe894ea55de200b0e3742bbdd31ea4dddf887 |
| core/worldline_core_sources.gpr / attest_sha256.gpr / worldline_core.gpr | 701931bc94f17aae8a14268cf7051f9a6d7b5bf8c7a1e0adccb9be0f5c0dff3c / 33c7a58b9d13c4dfa48f5a437d18bcd7eeb0ce90fe80d1ef692aeacbe5fef0d5 / 5497fabb698d53efc2bfb39104bdcd48b1c0f46e0c706c2643c8ce1af72fd5b0 |
| runtime/worldline/chain_authority.py / store.py / resource_ledger.py | 9f123d62282c8189a9b7b5f300b37d94d2544626820ca5d08ee9a72c81cab7f2 / 554b0a9dbe0b91f4fd9a6cd38d830e8b920d7e0d54e987f173865a0b33f68c9b / 97b921b7eb2f1440aedd801f3c4b78a9fd84c033d2e5ff32149773c753fc8a5f |

Hashes for the other cited files are in `inventory.json` (`source_files`).

**GNAT 16.1.0 install files read [OBS]** (`RT = ~/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude`):

| File | sha256 |
|---|---|
| RT/s-genbig.adb | 898241306e8d321750851a99cb7efc05064192f56b521de1fdbb2afb7b524991 |
| RT/s-shabig.ads | 344bcca75e082c901321e9a8e7a2b115c7c8fd08773f6047092b9a94e5139069 |
| RT/a-nbnbin.ads | be5a0604cbbde4b12d15ffd1ce665238b6581d8ec534dd6b3e8e8dfc4f40607a |
| RT/a-nbnbin.adb | 64872fd0039a97b22885320c559de9c4f13ac18c775d306b5690863ca6852d73 |
| share/info/gnat_ugn.info | 07f6d253c1a536946cdd0d5a26ddc4338d23c7c560a0f35bf918be51f576f17c |

## 1. What the checked build executes

### 1.1 Build selection [OBS]

- `core/worldline_core_sources.gpr:8-19`: `WORLDLINE_BUILD` defaults to `"checks"`, which appends `-gnata`.
  `core/attest_sha256.gpr:8-20` is identical.
- `core/worldline_core.gpr` aggregates both into the encapsulated `libworldline_core` (`:1-9`, `:81`). Every package in its
  `Library_Interface` (`:9-80`) is a callable Ada API.
- Core contains no `Assertion_Policy`, `Check_Policy`, `Suppress` or configuration-pragma file (grep). `spark.ads:8-12`
  only declares SPARKlib assertion levels, and no core Ghost entity uses them.
- Counts across the 134 core `.ads/.adb` files:
  - 155 `Loop_Invariant` lines;
  - 40 `Subprogram_Variant` lines;
  - 0 `Type_Invariant`, `Default_Initial_Condition`, `Contract_Cases` or `Initial_Condition` lines;
  - 0 predicate aspects;
  - 91 `External_Name` exports.

### 1.2 GNAT semantics

`gnat_ugn.info:9396-9436` [OBS] states:
- `-gnata` is equivalent to `pragma Assertion_Policy (Check)`.
- That covers `Assert, Dynamic_Predicate, Pre, Post, Ghost, Loop_Invariant, Loop_Variant, Subprogram_Variant` and the rest,
  all `=> Check`.
- "The pragmas Assert and Debug normally have no effect and are ignored" without the switch.

Consequences for the default build [DER]:
- Ghost subprograms, Ghost objects and Ghost statements execute.
- Every Pre and Post is evaluated, including those of expression functions and Ghost functions.
- Every `Loop_Invariant`, `Loop_Variant` and `pragma Assert` is evaluated each time control reaches it.
- `'Old` prefixes are copied at entry.
- `Subprogram_Variant` is checked at recursive calls.
- Dynamic predicates are checked at user-code subtype conversions.

A release build has no `-gnata`, so the default policy is Ignore and none of the above executes.

### 1.3 Counting rules [DER]

- An evaluated assertion executes every call in it. A function called from a Post runs its own body and its own Post.
  The inspected GNAT UG section describes no assertion-within-assertion disabling.
- `if` expressions evaluate only the selected branch.
- `and then` / `or else` short-circuit.
- Actual parameters are evaluated before the call.
- Nothing is memoised.
- The defining packages are not declared Pure (for example `resource_quantities.ads:4`, `worldline-chain_authority.ads:9`),
  so the RM 10.2.1(18) permission to omit calls does not apply.
- Whether GCC `-O2` merges duplicate calls was not determined. The calls allocate, finalize controlled objects and can
  raise, which normally prevents elimination [DER, unverified].
- All counts below are source-semantic counts. They assume the success path (valid spans, anchors present, no early
  refusal) unless stated.

### 1.4 Big_Integer cost model [OBS runtime]

**Runtime facts:**
- `SPARK.Big_Integers` renames `Ada.Numerics.Big_Numbers.Big_Integers` (`core/spark-big_integers.ads:30`).
- `Big_Integer` is a controlled record over a heap Bignum (`a-nbnbin.ads:170-189`).
- Every operation allocates its result.
- Assignment deep-copies in `Adjust` (`a-nbnbin.adb:604-609`). `Finalize` frees (`:615-620`).
- Integer literals in Big_Integer context call `From_Universal_Image` (`a-nbnbin.ads:26-28`).
- Digits are 32-bit (`s-shabig.ads:46-50`).
- Multiplication is schoolbook, with an on-stack digit vector of `X.Len + Y.Len` words (`s-genbig.adb:579-613`).
- `Normalize` raises `Storage_Error "big integer limit exceeded"` when `X'Last - J > Bignum_Limit` (`:1176`, `:1190-1192`),
  with `Bignum_Limit = 200`.
- `Valid_Big_Integer` has `Dynamic_Predicate => Is_Valid (Intrinsic)` (`a-nbnbin.ads:30-37`).
- The `Big_Natural` and `Big_Positive` predicates compare with `To_Big_Integer (0)` (`:51-62`).
- Each predicate check is O(1) but may allocate one temporary.

**Unit used below.** One "PR invocation" is one call of `Resource_Quantities.Power_Reference`. It comprises:
- one multiply of the previous power by 256;
- one result allocation;
- one literal conversion for its Post;
- one variant check.

One PR invocation at exponent e costs Θ(e) limb work [DER]. "Limb work" means 32-bit digit operations.

### 1.5 Representation cliff [DER, with J49-J52, J72, J73]

- 256^804 = 2^6432 (804·8 = 6432 = 32·201, J49 J50) needs 6432/32 + 1 = 202 words (J72). The limit is 200 + 1 = 201 words
  (J52), so it raises.
- 256^803 = 2^6424 (803·8 = 6424, J51); 6424/32 = 803/4 (J73), so the top bit lies in word 201 and it fits.
- Hence, independently of the numerical value:
  - `Resource_Quantities.Power_Reference (e)` and `Radix_Power (e)` raise for e ≥ 804.
  - `Prefix_Value (c)`, `Magnitude` and `Value` raise for any valid span with Length ≥ 804. The worker forms
    `Place = 256^c` at `resource_quantities.adb:181`.
  - `Prefix_Reference (c)` raises for c ≥ 805, because it computes `Power_Reference (c - 1)`.
  - `Worldline.Resources.Radix_Power (Count)` raises for Count ≥ 804.
- A zero-padded 804-byte span holding the value 1 therefore fails in every checked contract that evaluates its Value.

## 2. Reference primitives: definition, per-level recursion, growth

The tables count call sites in the source [OBS] and give growth [DER] with the cited JACKAL checks.

### 2.1 Chain authority (no Big_Integer; the cost is calls and SHA-256 `Link`)

**E01 `Worldline.Chain_Authority.Prefix_Reference`**
- **Form:** spec `ads:74-86`, regular recursive body `adb:2-36`; Ghost; Pre (`:78`, O(1)); `Subprogram_Variant` (`:79`).
- **Recursion per level:** one recursive call in the body (`adb:11-12`) and one in its own Post (`ads:84-86`, the actual
  of `Prefix_Step`). Both are evaluated for every Count ≥ 1.
- **Hashing per invocation (valid chain):** up to one `Link` (SHA-256 over 84 bytes, `receipts.adb:71-78`) in the body
  (`adb:26-27`) and one in the Post's `Prefix_Step` (`ads:55-56`). That is 1+1 = 2 (J79).
- **Invocations:** T(0) = 1 and T(n) = 1 + 2·T(n-1), so **P(n) = 2^(n+1) - 1** [DER].
  - Step identity J01 with x = 2^n; base J07.
  - Count-0 invocations: 2^n. Nonzero invocations: 2^n - 1.
  - Link calls on a valid chain: 2^(n+1) - 2 (instance n = 2: J23 = J24 = 6).
- **Growth:** **Θ(2^n) time** in n = Count (at call sites, n = `Rows'Length`, the number of retained rows).
- **Stack:** O(n) nesting depth.
- **Release:** not executed.

**E02 `Replay_Reference`**
- **Form:** spec `ads:88-105`, body `adb:38-66`.
- **Evaluation:** once anchors are present and the genesis matches, the body evaluates `P(Rows'Length)` (`adb:54-55`) and
  its Post evaluates it again (`ads:102-105`). Cost: 2·P(n).

**E03 `Prefix_Step` (`ads:42-61`) and `Finish_Reference` (`ads:63-70`)**
- Ghost expression functions, O(1) (at most one `Link`).
- `Link` (`ads:29-33`) and `Present` (`ads:35-38`) are non-Ghost and O(1).

### 2.2 Resource_Quantities (pinned file; public Library_Interface)

All counts are PR invocations. p(e) = e + 1; r(c) = c(c+1)/2.

**E04 `Power_Reference` (`ads:40-45`)**
- **Form:** expression function, Ghost, variant. One body recursive call; Post `>= 1` is non-recursive.
- **Count:** p(e).
- **Growth:** Θ(e²) limbs, depth e.
- **Raises:** e ≥ 804.

**E05 `Prefix_Reference` (`ads:47-56`)**
- **Form:** expression function, Ghost. One body recursive call plus `Power_Reference (c - 1)`; Post `>= 0`.
- **Count:** r(c) PR invocations, c+1 self-invocations.
- **Growth:** Θ(c³) limbs.
- **Raises:** c ≥ 805.

**E06 `Radix_Power_Worker` (`adb:97-137`)**
- **Form:** iterative Ghost worker.
- **Evaluations:**
  - Invariants `:110` and `:112-113` evaluate `Power_Reference (Completed)` and `Power_Reference (Completed - 1)` on each
    iteration.
  - Two post-loop evaluations of `Power_Reference (e-1)` (`:127-131`).
  - Post `:100`.
- **Count:** w(e) = e² + 3e + 1 (J25; instance J59 = J60 = 11).
- **Growth:** Θ(e³) limbs.

**E07 `Radix_Power` (`ads:58-67`; body `adb:142-143` = worker)**
- **Form:** self-referential Post.
  - `Radix_Power (e-1)` at `:64`;
  - `Power_Reference (e)` at `:65`;
  - `Power_Reference (e-1)` at `:67`.
- **Recursion per level:** 0 calls in the body, 1 in the Post (linear chain).
- **Count:** RP(e) = RP(e-1) + e² + 5e + 2 (J26), RP(0) = 2, so **RP(e) = (e³ + 9e² + 14e + 6)/3**.
  - Telescoping J27; bases J32 and J63 = J64 = 10; canonical degree 3 (J76).
- **Growth:** Θ(e⁴) limbs, depth O(e).
- **Raises:** e ≥ 804.

**E08 `Prefix_Value_Worker` (`adb:147-203`)**
- **Evaluations:**
  - Invariants `:163-169` evaluate `Prefix_Reference (Completed)`, `Power_Reference (Completed)`,
    `Prefix_Reference (Completed - 1)` and `Power_Reference (Completed - 1)` on each iteration.
  - Post-loop `:186-196` evaluates `Prefix_Reference (c-1)` twice and `Power_Reference (c-1)` twice.
  - Post `:151` evaluates `Prefix_Reference (c)`.
- **Count:** PVW(c) = (c³ + 6c² + 5c)/3 (composition J29, using S(n) from J28; base J71; instance J61 = J62 = 14).
- **Growth:** Θ(c⁴) limbs.

**E09 `Prefix_Value` (`ads:69-83`; body `adb:205-208` = worker)**
- **Form:** self-referential Post. `Prefix_Value (c-1)` and `Radix_Power (c-1)` at `:76-78`; `Prefix_Reference (c)` at
  `:79`; `Prefix_Reference (c-1)` and `Power_Reference (c-1)` at `:81-83`.
- **Count:** PV(c) - PV(c-1) = (2c³ + 15c² + 7c)/3 (J30), so **PV(c) = c(c+1)(c² + 11c + 12)/6**.
  - Telescoping J31; base J69; canonical form degree 4, leading coefficient 1/6 (J75).
  - Instances: PV(1) = 8 (J33); PV(2) = 38 (J34); PV(8) = 1968 (J35); PV(32) = 244288 (J36); PV(128) = 48996608 (J37);
    PV(803) = 70334477708 (J38).
- **Growth:** **Θ(c⁵) limb work**; Θ(c⁴) allocations; depth O(c).
- **Raises:** c ≥ 804.

**E10 `Magnitude` (`ads:85-90`, `adb:210-217`) and `Value` (`ads:92-96`, `adb:219-226`)**
- **Magnitude:** body and Post each evaluate `Prefix_Value (Q.Length)` on a valid span: 2 PV(L).
- **Value:** body and Post each evaluate `Magnitude`: 2·2 = 4 PV(L) (J81). Canonical form degree 4 (J78).
- **Value instances:** Value(8) = 7872 (J43); Value(32) = 977152 (J44); Value(803) = 281337910832 (J45).

**E11 Body lemmas (Ghost, `adb`)**

| Lemma | Lines | Behaviour | Growth |
|---|---|---|---|
| `Scale_Column` | 15-39 | Factor iterations, each with an invariant multiply | Θ(Factor·size) |
| `Column_Bounds` | 41-64 | two `Scale_Column` calls | 255 iterations total |
| `Higher_Column_Order` | 66-92 | one `Scale_Column` | — |
| `Prefix_Bounds` | 230-257 | recursive, depth c, `Prefix_Reference` / `Power_Reference` and `Column_Bounds` per level | Θ(c⁴) limbs |
| `Prefix_Monotone` | 259-276 | depth Larger - Smaller, two `Prefix_Reference` per level | Θ((Larger-Smaller)·Larger³) |
| `Prefix_Padding` | 278-296 | (Count - Length + 1) levels, each Post = `Prefix_Reference (Count_i)` + 2 PV(Length) | — |
| `Borrow_Column_Facts` | 298-314 | — | O(1) |

**E12 Ghost objects in `Capacity_Fits`**
- `Residue` / `Place` at `adb:413-414`; `Before_*` at `:444-445`; `Contribution` via `Scale_Column` at `:456-457`.
- Θ(k) per iteration. `Place` reaches 256^Count (`:474`), so the function raises for Count ≥ 804.

### 2.3 Resource_Ledger (pinned file)

**E13 `Total_Reference` (`ads:124-131`)**
- Expression function, one recursive call per level, no Post.
- Total_Reference(k) evaluates k `Row_Reference`.

**E14 `Withheld_Reference` and `Row_Reference`**
- `Withheld_Reference` (`ads:99-111`, `adb:470-489`): at most 2 `Value` in the body and 4 in the Post, 2 + 4 = 6 (J83).
- `Row_Reference` (`ads:113-120`, `adb:491-499`): `Withheld_Reference` in the body and again in the Post, 2·(2+4) = 12
  `Value` = 12·4 = 48 PV (J66, J67).

**E15 `Prefix_Total`**
- Spec `ads:133-142`; body `adb:832-838` = `Total_Worker_Recurrence` + `Prefix_Total_Worker`; worker `adb:501-530`;
  recurrence lemma `adb:534-564`.
- **Body:** non-recursive. The worker's invariant `:512-513` evaluates `Total_Reference (Offset)` and the assert
  `:515-516` evaluates `Total_Reference (Offset+1)` on each iteration.
- **Post:** recursive, `Prefix_Total (c-1)` plus `Total_Reference (c)`.
- **Growth:** Θ(c²) `Row_Reference` per worker call, so **Θ(c³) `Row_Reference` per `Prefix_Total (c)`**, that is Θ(c³·L⁵).

**E16 `Storage_Sufficient` (`ads:148-158`, `adb:840-870`)**
- **Loop invariant `:848-854`** evaluates, for every J < I:
  - `Withheld_Reference`;
  - `Radix_Power (slot_J)`;
  - `Prefix_Total (J+1)`;
  - `Radix_Power (Total_Capacity)`.
- **Body `:857-863`** evaluates the same terms once per I. The Post repeats them for all I.
- **Growth:** **Θ(N⁵·L⁵ + N²·T⁴ + N·S⁴)**, where N = rows, T = total arena length and S = slot length.
- **Raises:** T ≥ 804 or any slot ≥ 804.

**E17 Representation and frame references**
- `Canonical_In_Slot` (`ads:61-71`) is O(D) over the arena; `Arena_Frame_Zero` (`ads:75-80`) is O(D·N);
  `Output_Representation` (`ads:82-95`) is O(N·D + D·N).
- `Result_Conforms` (`ads:162-190`, `adb:872-929`) and `Processed_Conforms` (`adb:1390-1416`) combine them with
  `Storage_Sufficient` / `Prefix_Total` / `Value`.

**E18 Recursive body lemmas over a count**
- `Power_Factor :55`, `Power_Monotone :74`, `Prefix_Quotient :90`, `Equal_Prefix :304` (with an O(Count) Pre
  quantifier), `Padded_Prefix :324`, `Bounded_Prefix :342`, `Zero_Extension :386` (O(High-Low) Pre quantifier).
- When applied to `Whole (Output)` (`adb:7-9`), their count is the arena length, not the value length. Examples:
  `Output_Prefix_Value :403`, `Trimmed_Value :423`, and `Binary :1329-1331`.

### 2.4 Resource_Run_Ledger (not in CONTRACT_PINS)

**E19 `Sum_Reference` (`ads:200-209`)**
- Expression function, one recursive call per level, no Post.
- Per included row: `Amount_Reference` (`ads:187-192`), at most 3 `Value` = 3·4 = 12 PV (J57). `Included` is O(identity
  length).
- **Growth:** Θ(k·L⁵) for k included rows.

**E20 `Conserved_Reference` (`ads:236-243`), `Contained_Reference` (`ads:255-263`), `Decision_Reference` (`ads:376-444`)**
- Ghost expression functions. Their cost is section 3.3.

### 2.5 Worldline.Resources (pinned file; uses Ada Big_Integers directly)

**E21 `Radix_Power` (`ads:29-32`)**
- Expression function, no Post, Count + 1 invocations.
- Θ(Count²) limbs. One `Big_Positive` predicate per return.

**E22 `Prefix_Value` (`ads:34-42`)**
- The body calls `Prefix_Value (c-1)` and `Radix_Power (c-1)`. The Post calls `Radix_Power (c)` (non-recursive).
- **Count:** (c+1)² `Radix_Power` invocations (increment J65; base J70).
- **Growth:** Θ(c³) limbs.
- `Magnitude` (`ads:44-46`) = `Prefix_Value (length)`.

**E23 Body lemmas (`adb`)**

| Lemma | Lines | Behaviour | Growth |
|---|---|---|---|
| `Power_Quotient` | 9-31 | recursive | Θ((H-L)·H²) |
| `Prefix_Quotient` | 33-64 | recursive | Θ((H-L)·H³) |
| `Power_Order` | 178-196 | — | — |
| `Complete_Prefix` | 198-208 | depth Count - length, Post = `Prefix_Value (Count)` + `Magnitude` | — |
| `Prefix_Growth` | 210-224 | — | — |
| `Prefix_Modulus` | 239-262 | — | — |
| `Matching_Prefix` | 277-290 | depth Count; O(Count) Pre quantifier and 2 `Prefix_Value` per level | **Θ(Count⁴)** |
| `Prefix_Step` | 294-313 | — | Θ(c³) |
| column lemmas | 315-757 | Big_Integer arithmetic at operand size | — |

### 2.6 Lemma families in other units

**Evaluation_Epoch body lemmas**
- `Prefix_Step :67-97`: Θ(c⁵), because its asserts and Post evaluate `Prefix_Value (c)` and `Prefix_Value (c+1)`.
- `Prefix_Bounds :99-117`: recursive with `Prefix_Value (Count)` in each level's Post, Θ(c⁶).
- `Prefix_Padding :119-139`.
- `Power_Factor :141-160`: recursive, Θ((H-L)·H⁴).
- `Prefix_Tail :162-191`: recursive, Θ((H-L)·H⁵).
- `Prefix_Modulus :361`, `Magnitude_Modulus :387`, `Matching_Column :451`, `Mismatching_Column :498`.

**Resource_Reservation_Transition body lemmas**
- `Prefix_Step :8-33` (Θ(c⁵)), `Prefix_Padding :35-55`, `Power_Factor :57-80`.
- `Prefix_Tail :85-95`: expression-function recursion, Θ(m³).
- `Prefix_Decomposition :97-125`: Θ(m·S³).
- `Addition_Step :303-335`: Θ(o⁵).
- `Addition_Mismatch :384-449`.
- `Zero_Prefix :484-503`: recursive. Each level's Post evaluates `Prefix_Value (Zero_Quantity, k)`, which is Θ(k⁵) even
  though every digit is zero, so Zero_Prefix(c) is **Θ(c⁶)**.

**Recovery V3 wire lemmas**
- `Equal_Prefix :3-21`: Θ(c⁴).
- `Zero_Padding :23-45`: O(L) Pre quantifier plus `Magnitude` per level, so Θ((k+1)·L⁵) for k high zero bytes.
- `Positive_Prefix :47-62`.

### 2.7 Canonical_Artifacts

**E24 `Prefix` (`ads:32-39`, `adb:156-235`) and `Tagged_Matches` (`ads:61-63`, `adb:465-…`)**
- Executable, recursive.
- Checked overhead: Post O(1) (`P.Valid` is O(1), `evaluation_pending.ads:48-50`), variant O(1), loop invariants
  `adb:175-176`, `:195-196`, `:229` O(1).
- Constant factor over release.
- Recursion depth equals JSON nesting depth in both builds.
- `Integer_Matches` (`adb:431-463`) uses executable Big_Integer. That is D1 scope, not D2.

### 2.8 Remaining Ghost declarations

Appendix A lists every Ghost or recursive declaration the scan found, with its class.

## 3. Executable call sites per exported path (evaluations per call)

### 3.1 Chain replay: `wl_chain_authority_replay_v1`

**Path.** `worldline-chain_authority_c_api.adb:79-118` copies the rows (`:104-112`) and calls `Wire.Decide` (`:114`).
Its handler at `:117` turns any exception into `-1`.

| Site | Kind | Evaluations per call |
|---|---|---|
| `worldline-chain_authority.adb:90-92` (`Replay`) | Loop_Invariant | P(Count) at every iteration start, Count = 0..n-1: Σ P(c) = **2^(n+1) - 2 - n** (instance n = 5: J03 = J04 = 57) |
| `receipts.ads:21-28` / `causal_graph.ads:21-25` (`Append` Post) | Post | +1 `Link` per row |
| `worldline-chain_authority.ads:111-114` (`Replay` Post) | Post | 1 `Replay_Reference` = 2·P(n) |
| `worldline-chain_authority_wire.ads:59-72` (`Decide` Post) | Post | 3 `Replay_Reference` (`:62`, `:66`, `:70`) = 6·P(n) |

**Total `Prefix_Reference` invocations, success path** (anchors present, genesis matches, n rows accepted):
- (2^(n+1) - 2 - n) + 2·(1+3)·P(n) (J80), which gives **9·2^(n+1) - n - 10** [DER].
  - Instance n = 3: J05 = J08 = 131.
- Values:

| n | Invocations | JACKAL |
|---|---|---|
| 1 | 25 | J13 |
| 10 | 18412 | J14 |
| 20 | 18874338 | J15 |
| 30 | 19327352792 | J16 |
| 40 | 19791209299918 | J17 |
| 64 | 332041393326771929014 | J18 |

- On a valid chain, each nonzero-Count invocation also performs 2 SHA-256 `Link` calls.

**Ada API.** `Worldline.Chain_Authority.Replay` alone costs **3·2^(n+1) - n - 4** (instance n = 3: J09 = J10 = 41; n = 30:
6442450910, J22).

**Early returns.** These still pay the Posts. `Replay_Reference` recomputes P(n) regardless of where the loop stopped.

**Release.** The cost is n `Append` calls, i.e. n `Link` calls: Θ(n).

**Callers [OBS]:**
- `runtime/worldline/chain_authority.py:80-110` `replay_chain`, called from `store.py:1104-1140`
  `replay_native_chains`. That method replays *every* row of `receipts` and of `causal_events` ("Legacy verify_chains
  remains unchanged pending full caller integration", `:1111`).
- grep found no in-tree caller of `replay_native_chains`.
- `chain-bounds-tests/test_bounds.adb` uses only 1- and 2-row chains (`:24`, `:34`). Its project builds with
  `-gnata -O0`.

### 3.2 Resource_Quantities executable functions (used by most quantity exports)

**`Is_Zero` (`adb:316-333`)**
- Invariant `:322-323` evaluates `Prefix_Reference (Offset)` on each scanned byte, until the first nonzero byte.
- On exit: `Prefix_Monotone :325` and asserts `:326-327` (2 PV).
- Post `ads:98-100` is `Magnitude`, 2 PV.
- Growth: Θ(L⁵).

**`Is_Negative` (`adb:335-338`)**
- Post `ads:102-104` is `Value`, 4 PV, plus `Is_Zero` when the sign flag is set.

**`Compare` (`adb:340-402`)**
- **PV evaluations, equal nonnegative operands of length L:**
  - `Prefix_Padding` ×2 (`:350-351`): 3 + 3;
  - `Is_Negative` ×2 (`:352-353`): 8;
  - asserts `:357-364`: 12;
  - loop: 8 per iteration (invariant `:369-372` plus assert `:396-399`, 2·2 + 2·2 = 8, J58), over L iterations;
  - Post `ads:110-117` (`Equal`): 16.
  - Total: **8L + 42** (J42).
- When the operands differ in the top byte: 50 (`Greater`, J55) or 42 (`Less`, J56).
- `Prefix_Bounds` ×2 per iteration (`:373-374`) adds Θ(o⁴) per iteration.
- PR invocations from the PV terms alone: (8L + 42)·PV(L), canonical degree 5 (J77).
  - L = 8: **208608** (J46).
  - L = 32: **72797824** (J47).
  - L = 803: **454782732859928** (J48).
- Growth: **Θ(L⁶)**.

**`Capacity_Fits` (`adb:404-486`)**
- `Prefix_Padding` ×4 (`:423-426`).
- Per iteration: invariants `:431-438` (`Power_Reference` and 4× `Prefix_Reference`), `Scale_Column` (`:456-457`), asserts
  `:459-482`. The loop total is Θ(L⁴).
- Post `ads:125-130`: 4 `Magnitude` = 8 PV.
- Growth: Θ(L⁵) plus padding terms.

**Release.** `Compare`, `Is_Zero` and `Capacity_Fits` are Θ(L) digit scans with no Big_Integer.

### 3.3 Run ledger: `wl_resource_run_ledger_check_v1`

**Path.** `resource_run_ledger_c_api.adb:185-222` (any exception becomes `-1` at `:221`) → `resource_run_ledger_wire.adb:24-30`
→ `Check`.

**`Exact_Value` (`adb:19-35`)**
- Invariants `:27-28` evaluate `Prefix_Reference (Count)` and `Power_Reference (Count)` on each iteration, S(L) PR
  invocations with S(L) = (L³ - L)/6 + (L² + L)/2 (J28, base J68).
- Post `ads:185-186`: `Value`, 4 PV.
- The executable Big_Integer arithmetic is D1 scope.

**`Amount` (`adb:36-48`)**
- 2 `Exact_Value` plus Post `Amount_Reference` (at most 3 `Value`): 2·4 + 3·4 = 20 PV (J54), plus 2·S(L).

**`Sum` (`adb:49-64`)**
- Invariant `:56` evaluates `Sum_Reference (Count)` on every iteration.
- One `Amount` per included row.
- Post `ads:213`: `Sum_Reference (N)`.

**`Conserved` (`adb:65-69`)**
- Executable: `Shape`, 2 `Exact_Value`, 2 `Sum`.
- Post `ads:244-246`: `Conserved_Reference` = `Shape` again, 2 `Value`, 2 `Sum_Reference (N)`.

**`Contained` (`adb:70-90`)**
- Invariant `:73-75`: Θ(I²) `Parent_Supports` per iteration, Θ(N³) in total.
- Invariant `:81-84`: Σ over K < I of 2 `Sum_Reference (N)` + `Value`, on every iteration.
- Body `:85-87`: 2 `Sum` + `Exact_Value`.
- Post `ads:264-265`: `Contained_Reference`.
- On the `Check` path, `Shape` has already established distinct reservation identities, so each row belongs to at most
  one parent sum. That bounds this function at **Θ(N²) `Value` evaluations plus Θ(N³) identity comparisons** [DER].
- A direct Ada call (`Resource_Run_Ledger` is in the Library_Interface) with duplicate reservation identities can reach
  **Θ(N³) `Value` evaluations** [DER].

**`Shape` (`ads:223-235`, executable)**
- Per row: `Row_Valid`, with 4 `Nonnegative_Valid`/`Epoch_Valid` calls of about 8 PV each.
- `Same_Context` → `Same_Epoch` (`adb:2-4`): `Compare` plus Post `ads:95-99` (2 `Epoch_Valid` + 2 `Value`).
- One more `Compare` (`:231-232`).
- Pairwise identity quantifier, executable in both builds.
- Growth: Θ(N·L⁶ + N²·id).

**`Check` (`adb:144-210`)**
- `Shape` ×2, `Native_Valid`, `Same_Epoch`, `Same_Context`, `Compare`.
- `T.Is_Successor` (`:166`) is **Θ(L_e⁷)**: Zero_Prefix(o) and Zero_Prefix(o+1) are called on every iteration
  (`resource_reservation_transition.adb:609`, `:615`), plus `Addition_Step` per column.
- `Conserved` ×2, `Contained` ×2, `Exact_Value` ×3, and for Reserve `Same_Row` ×N.
- Post `ads:450-457`: `Decision_Reference` re-evaluates all of this through the references, including a second
  `T.Is_Successor` (`ads:399`). When Ready, it adds `Conserved_Reference`, `Contained_Reference` and 2 `Value`.
- **Class: Θ(N²·L⁵ + N·L⁶ + L_e⁷ + N³·id)** [DER].
- **Release:** Θ(N²·id) identity work plus D1-scope `Exact_Value` Big_Integer.

**Wire decoding (`resource_run_ledger_wire.adb:2-23`)**
- Invariants `:6-7` and `:17-18` (`'Initialized` plus `Result (J) = Decode`) make decoding Θ(N²·row size). This is
  checked-only.

### 3.4 Resource ledger: `wl_resource_ledger_compute` and `wl_resource_ledger_headroom`

**Path.** `worldline-resource_ledger_c_api.adb:108-177` and `:178-224`; any exception becomes `255` at `:175-176` and
`:222-223`.

**Arena sizing by the Python caller [OBS]**
- `runtime/worldline/resource_ledger.py:159-172` gives every row `capacity = max(len r, len u) + 1` and sets
  **T = D = Σ capacities**.
- Headroom uses `capacity = max length + 2` (`:237-239`).
- A transport failure raises `CoreUnavailable` (`:179-180`).

**`Binary` (`adb:1114-1346`), with Output'Length = O**

Per loop iteration (column `Count` = max operand length):
- invariants `:1173-1200`, including `Binary_Reference` (2 `Value`) and `Power_Reference (Offset)`;
- `Combined_Remainder` with 2 `Magnitude` actuals (`:1247-1257`);
- asserts `:1259-1264`;
- `Before_Output := Output` (`:1203`), an O(O) Ghost array copy.

Loop growth: Θ(Count·L⁵).

After the loop, O-scale evaluations:
- `Output_Prefix_Value`, `Bounded_Prefix`, `Padded_Prefix` over `Whole (Output)` (`:1329-1331`);
- `Magnitude (Output, Whole (Output))` (`:1332-1335`);
- `Radix_Power (Output'Length)` (`:1336-1339`, and Post `:1121-1122`);
- `Canonicalize` (`:1001-1038`), whose `Trimmed_Value` / `Padded_Prefix` / Post evaluate `Magnitude (Whole)` again.

Post-loop growth: **Θ(O⁵)** from several `Prefix_Value (O)` evaluations.

**`Compute` (`adb:1418-1516`)**

Per row:
- `Compute_Row` → `Compare` (Θ(L⁶)) and `Binary` with slot output S (Θ(L⁶ + S⁵));
- `Binary` with the total workspace, Output'Length = T (`:1484-1485`): **Θ(T⁵)**;
- `Processed_Conforms` in the invariant (`:1444-1447`) and in the assert (`:1505-1508`): `Prefix_Total` for every
  processed row and `Radix_Power (T)`;
- `Before_Detail_Data := Detail_Data` (`:1456`), an O(D) Ghost copy;
- `Retained_Detail_Frame` and `Checked_Detail_Step` over the detail arena.

**Class: Θ(N·T⁵ + N·L⁶ + N⁵·L⁵ + N²·T⁴ + N²·D)** [DER]. With the Python sizing T ≥ N, so it is **Θ(N⁶) for bounded value
lengths**.
- Instances of PR invocations per `Prefix_Value (T)` evaluation with 1-byte values (T = 2N, capacity 1 + 1 = 2, J79):
  - N = 10, T = 20: **44240** (J39);
  - N = 50, T = 100: **18705200** (J40);
  - N = 100, T = 200: **282820400** (J41).
- **Failure:** `Storage_Error` whenever T ≥ 804, any slot ≥ 804, or any quantity span ≥ 804. With 1-byte values this
  happens for **N ≥ 402 rows** (804/2, J53). It surfaces as 255 and then `CoreUnavailable`.

**`Compute_Headroom` (`adb:1517-1543`)**
- 2 `Binary` with O = L + 2, so Θ(L⁶).
- Fails for L ≥ 802 (804 - 2, J74).

**Release.** Θ(N·T) byte-column arithmetic, no Big_Integer.

### 3.5 `wl_resources_can_reserve` and the Ada `Try_Reserve`

**Path.** `worldline-resources_c_api.adb:36-65` (any exception becomes `255`) → `Resource_Wire.Can_Reserve`
(`worldline-resource_wire.adb:2-10`; Post `ads:11-16` = `Fits_By_Addition` + `Fits_Mathematically`) →
`Resources.Can_Reserve`.

**`Can_Reserve` (`adb:853-921`)**
- Per column: 4× `Prefix_Step`, `Extended_Digit_Bound`, `Subtraction_Column` with 4× `Prefix_Value` actuals,
  invariants `:906-913`.
- Then 4× `Complete_Prefix`.
- Post `ads:87-90`: `Fits_By_Addition` (`adb:787-851`, another Θ(L⁴) loop) + `Fits_Mathematically` (4× `Magnitude`).
- **Growth:** Θ(L⁴), L = max operand length.

**`Sum_Equals` (`adb:923-965`)** is also Θ(L⁴).

**`Try_Reserve` (`adb:967-1041`, Ada API)**
- `Matching_Prefix (Before_Step, Outstanding, Offset)` on every iteration (`:1023`) gives **Θ(Cap⁵)**.
- `Original` (`:973`) is a Ghost copy of Cap bytes. `Before_Step := ...` (`:1001`) is O(Cap) per iteration.
- `State'Old` (Post `ads:153-155`) copies 3·Cap bytes.
- `Radix_Power (State.Capacity)` (`:980-982`) raises for Cap ≥ 804.

**Failure.** Any operand ≥ 804 bytes raises (`Radix_Power (Offset+1)` at the last column).

**Release.** Θ(L) column scan.

### 3.6 `wl_resource_policy_admit`

**Path.** `worldline-resource_policy_c_api.adb:113-183` (any exception becomes `255`) → `Resource_Admission.Admit`
(`adb:208-276`).

Per disk:
- 2 `Check_Binary` (`Compare` plus assert `:163-169` with 2 `Value`; Post = `Binary_Reference`, 2+2 `Value`);
- asserts `:245`, `:252`;
- invariant `:237-241`, for all J < I: 2 references, each evaluating `Binary_Reference` in its body and Post;
- assert `:260-264`, the same for J ≤ I.

Then `Check_Capacity` (4× `Is_Negative` + `Capacity_Fits`). The Post (`ads:201`) is `Decision_Conforms` over all disks.

**Class:** **Θ(D²·L⁵ + D·L⁶)** for D disks [DER].

### 3.7 Epoch consumers (fixed or per-row multiples of Θ(L_e⁶))

**Basic costs**
- `Evaluation_Epoch.Same_Value` (`adb:551-558`; Post `ads:7-12`, 4 `Value` = 4·4 = 16 PV, J82): `Compare` plus 2×
  `Nonnegative_Valid`. **Θ(L⁶)**.
- `Evaluation_Epoch.Is_Successor` (`adb:560-604`): invariant `:578-582` (2 `Prefix_Value` + `Radix_Power` per column)
  and `Matching_Column` per column (`:589`; Θ(o⁵)). **Θ(L⁶)**.
- `Evaluation_History.Same_Epoch` (`adb:7-10`) is `Compare`. `Next_Epoch` and `Epoch_One` (`:15-24`) are
  `Evaluation_Epoch.Is_Successor`.
- `Evaluation_History.Epoch_Valid` (`ads:40-41`) is O(1).

**Consumers verified by reading**

| Unit | Path | Class |
|---|---|---|
| `Evaluation_Pending.Decide` (`adb:14-55`) | `Journal_Valid` (`ads:81-102`, executable), with `Successor` and `Same_Cursor` per row; Post `Reference`; `Run_Index` invariant `adb:8-9` | **Θ(J·L⁶ + J²·id)** |
| `Evaluation_Pending_V2.Decide` | through v1, plus `Base_Of` invariant `adb:11-12` (Θ(J²)) | same as v1 |
| `Evaluation_Completion.Results_Valid` (`adb:2-21`) and `Same_Results` (`:23-37`) | invariants `:15-18` / `:32-34` evaluate `Same_Binding` → `P.Epoch_Same` (`ads:117`) for every earlier row | **Θ(R²·L⁶)** checked, against Θ(R·L) release |
| `Evaluation_Completion.Apply` | `History'Old` copy (`ads:422`, `:432-433`) | O(H) |
| `Evaluation_History.Select_Evidence` (`adb:42-77`; via `wl_evaluation_history_select`, `worldline-evaluation_history_c_api.adb:179`) | `History_Valid` (`ads:203-217`, executable) with `Next_Epoch` per row; `Find_Completed_Failure` invariant `adb:36-37`; Post `Result_Conforms` + `History_Valid` again | **Θ(H·L⁶ + H²·id)** |
| Owner transitions / retry audit | `E.Same_Epoch` with `E = Evaluation_History` (`worldline-owner_transitions.ads:8`, `:65`; `owner_transitions.adb:100`; `owner_retry_audit.ads:81`) | fixed multiples of Θ(L⁶) |
| Recovery V3 `Same` (`adb:2-7`; Post `Same_Epoch_Reference`, `ads:33-41`) | `Compare` + 2 `T.Epoch_Valid` | — |
| `Recovery_Authorization_V3_Wire.Decide` | Post `wire.ads:262-267` evaluates `Selected_Action` twice more (each with Post `Action_Reference`) | fixed multiples of Θ(L⁶) |

**Not traced to completion:** `wl_completion_raw_decide_v1`, `wl_completion_metadata_matches_v1`, `wl_finalization_*`.
- `Raw_Roster.Row_Bound` → `Same_Binding` → `Epoch_Same` is reached from `evaluation_completion_c.adb:667`.
- `Evaluation_Finalization` uses `P.Epoch_Same` (`ads:112`).

### 3.8 Checked-only quadratic or cubic loop invariants (no Big_Integer)

Each turns a linear release loop into a sum over the processed prefix [OBS sites; DER class]:

| Site | Growth |
|---|---|
| `evaluation_pending.adb:8-9` | Θ(J²·id) |
| `evaluation_pending_v2.adb:11-12` | Θ(J²) |
| `evaluation_completion.adb:46-48` | Θ(J²·id) |
| `evaluation_history.adb:36-37` | Θ(H²·id) |
| `evaluation_completion_roster.adb:57` | `for some K ≤ I`: `Failure_For_Check_Reference`, itself O(R), so **Θ(Q²·R)** |
| `evaluation_completion_roster.adb:59` | Θ(Q²·R) |
| `evaluation_raw_roster.adb:56` | Θ(Q²·R) |
| `evaluation_raw_roster.adb:71` | Θ(H²·Q·R) |
| `evaluation_finalization.adb:33-35`, `:108-110` | Θ(n²) |
| `evaluation_finalization.adb:241` | Θ(Q²·M) |
| `resource_reservation_lifecycle.adb:18`, `:23` | Θ(n²) |
| `resource_run_ledger_wire.adb:6-7`, `:17-18` | Θ(N²) |
| `worldline-evaluation.adb:122`, `worldline-evaluation_v2.adb:150`, `worldline-evaluation_wire.adb:97`, `:109` | Θ(n²) |
| `worldline-evaluation_authority.adb:47` | Θ(n²) |
| `worldline-owner_transitions_wire.adb:73-74` | Θ(H²) |
| `worldline-recovery_authorization_v3_wire.adb:77-80` | Θ(L²) |

### 3.9 Copies, stack and heap (no measurement)

**Checked-only Ghost arrays**
- `resource_ledger.adb:1144`: `Before_Output`, O bytes, copied per column.
- `resource_ledger.adb:1424`: `Before_Detail_Data`, D bytes, copied per row.
- `worldline-resources.adb:973` and `:989`: Cap bytes each.

**`'Old` copies**
- `History'Old` (`evaluation_completion.ads:422`);
- `Removed'Old` (`resource_reservation_lifecycle.ads:104`);
- `State'Old` in `worldline-resources.ads:153-155` and `resource_reservation_transition.ads:397-401`;
- `C'Old` in Attest `Update` (`attest-sha256.ads:34`, O(1)).

**Recursion depth**
- `Prefix_Reference` (chain): O(n).
- The Resource_Quantities `Power_Reference` / `Prefix_Reference` / `Radix_Power` / `Prefix_Value` chains: O(L).
- Each frame holds controlled temporaries plus `Big_Mul` digit vectors of up to 201+201 words.

**Heap:** Θ(L⁴) allocate/free pairs per `Value`; live heap O(L²) bytes [DER].

None of these was measured.

### 3.10 Failure mapping (classification hazard)

The C wrappers turn every exception into a generic failure code:
- chain authority `-1` (`c_api.adb:117`);
- run ledger `-1` (`:221`);
- ledger `255`;
- resources `255`;
- policy `255`.

`Final_Context_Matches` turns exceptions into `False` (D1 review F12).

So checked-build `Storage_Error` from the representation cliff, `Storage_Error` from heap or stack exhaustion, and
`Assertion_Error` all become refusal-shaped outcomes for inputs the release build accepts. Under the native rule these
must never be counted as accepted refusals. Whether a stack overflow is caught at all was not determined: no
`-fstack-check` appears in the switches.

## 4. Ranked hazards

| Rank | Hazard | Class (checked) | Exported entry / Ada API | Release avoids? |
|---|---|---|---|---|
| H1 | Chain `Prefix_Reference`: body recursion plus a self-referential Post | **exponential**: 9·2^(n+1) - n - 10 invocations per C call; Θ(2^n) SHA-256 | `wl_chain_authority_replay_v1`; `Worldline.Chain_Authority.Replay`; `Chain_Authority_Wire.Decide`; Python `replay_chain` ← `store.replay_native_chains` (replays every stored receipt and event; no in-tree caller observed) | Yes (Θ(n)), but no in-tree path selects release (F11) |
| H2 | Resource ledger: `Whole (Output)`-scale Ghost evaluation with Python arena T = Σ(L_i+1) | **Θ(N⁶)** for bounded values; generally Θ(N·T⁵ + N⁵·L⁵ + N²·T⁴); `Storage_Error` at T ≥ 804 (N ≥ 402 with 1-byte values) | `wl_resource_ledger_compute`, `wl_resource_ledger_headroom`; `Resource_Ledger.Compute` / `Compute_Headroom` | Yes (Θ(N·T)) |
| H3 | Quantity references: `Value` Θ(L⁵) through the self-referential `Prefix_Value` / `Radix_Power` Posts and worker invariants; representation cliff at 804 bytes regardless of value | `Compare` Θ(L⁶); `T.Is_Successor` **Θ(L⁷)**; `Evaluation_Epoch.Is_Successor` / `Same_Value` Θ(L⁶); `Capacity_Fits`, `Is_Zero`, `Is_Negative`, `Nonnegative_Valid` Θ(L⁵) | every quantity or epoch export (H4-H7); Ada APIs `Resource_Quantities.*`, `Resource_Reservation_Transition.*` | Yes (Θ(L) scans) |
| H4 | Run ledger `Check` | Θ(N²·L⁵ + N·L⁶ + L_e⁷ + N³·id); direct `Contained`/`Sum` Θ(N³·L⁵) worst case | `wl_resource_run_ledger_check_v1`; `Resource_Run_Ledger.*` | Mostly (Θ(N²·id) plus D1-scope Big_Integer remain) |
| H5 | Worldline.Resources | `Can_Reserve` Θ(L⁴); `Try_Reserve` **Θ(Cap⁵)**; cliff at 804 | `wl_resources_can_reserve`; Ada `Worldline.Resources.Try_Reserve` | Yes |
| H6 | Resource admission | Θ(D²·L⁵ + D·L⁶) | `wl_resource_policy_admit` | Yes |
| H7 | Epoch consumers | Θ(J·L⁶ + J²·id) pending; Θ(R²·L⁶) completion; Θ(H·L⁶ + H²·id) history; fixed Θ(L⁶) owner / recovery V3 | `wl_pending_decide_v1/_v2`, `wl_completion_decide_v1`, `wl_evaluation_history_select`, `wl_owner_transition_authorize_v1`, `wl_owner_audit_decide_v1`, `wl_recovery_authorization_decide_v3` (others in 3.7 not traced) | Yes |
| H8 | Checked-only quadratic or cubic invariants (3.8) | Θ(n²) to Θ(H²·Q·R) | completion, raw roster, finalization, pending, history, run-ledger decode, lifecycle | Yes |
| H9 | Checked-only copies and recursion depth (3.9) | O(arena) per step; O(n) or O(L) depth | ledger, resources, completion | Yes |
| H10 | Failure-to-refusal mapping (3.10) | classification | all of the above | Not applicable |
| H11 | Canonical_Artifacts `Prefix` / `Tagged_Matches` | constant factor | finalization / collapse paths | Yes |

**Release caveat.** "Release avoids" means only that `-gnata` code is absent there. Selecting release was never
established (O-BUILD-SELECTION), and using it to discharge D2 would be suppression (section 5).

## 5. Candidate repair directions (none adopted; approvals needed)

**Approval classes**
- **L:** lead-only body change. Files in `CONTRACT_PINS` (`runtime/worldline/proof_manifest.py`, 82 entries [OBS],
  whole-file pins for resource_quantities, resource_ledger, worldline-resources, evaluation_epoch,
  resource_reservation_transition and canonical_artifacts) also need reviewed pin regeneration (O-PINS).
  worldline-chain_authority and resource_run_ledger are not pinned there [OBS].
- **R:** reviewer ruling, needed whenever an existing checked assertion or invariant is replaced or removed. The ruling
  must establish that no checked obligation is weakened.
- **O:** operator approval, needed whenever public spec or reference text, a public contract, the API/ABI, runtime or
  toolchain identity, or build selection changes.

**H1**
- **(a) L + R + proof evidence.** Make the `Prefix_Reference` body iterative and leave the spec and Post byte-identical.
  The Post still recurses, so T(n) = Θ(n) + T(n-1), i.e. Θ(n²) per evaluation and Θ(n³) per replay. Proof feasibility
  is undetermined: the recursive-contract limitation of SPARK UG ch33 applies.
- **(b) O.** A non-self-referential or divide-and-conquer reference definition with equivalence lemmas. That is a public
  spec change.
- **(c) R.** Any change to the `Replay` invariant (`:90-92`) or to the Wire `Decide` Post that removes reference
  evaluations is assertion replacement and needs a ruling. Deleting them is forbidden.

**H2**
- **(a) L + R.** In `Binary` / `Canonicalize`, state the final value facts on the canonical result span instead of
  `Whole (Output)` (`adb:1329-1340`). This replaces assertions.
- **(b) R and possibly O.** Have Python provision T from the largest ordered partial sum, not Σ(L_i+1). This is storage
  provisioning, not a cap. It must never produce `Insufficient_Storage` for an accepted input, and it must not make
  Python an accounting authority.
- **(c) O.** Restate `Storage_Sufficient` / `Processed_Conforms` without `Radix_Power (T)` (public Ghost spec).

**H3**
- **(a) L + R.** Cheaper worker invariants (`adb:108-116`, `:161-175`) through Ghost accumulators. This can remove at
  most one power: the self-referential spec Posts keep about a Θ(L⁴) floor.
- **(b) O.** Redesign the reference hierarchy (non-recursive `Prefix_Value` / `Radix_Power` Posts, logarithmic-depth
  references) in the pinned public spec.
- **(c) O.** D1 OD-1 (ii), a rebuilt runtime without `Bignum_Limit`. It removes only the 804-byte cliff, not the costs.
  Per the D1 review it is operator-owned and needs a repaired evidence package.

**H4**
- **(a) L + R.** Restructure `Contained` / `Sum` so the reference sums are evaluated once per parent rather than per
  iteration. Assertion replacement.
- **(b)** D1's release-path redesign adds checked work of its own (D1 v2 §8.4) and closes no D2.

**H5 to H8**
- The same L+R and O pattern applies: replace per-iteration whole-reference invariants with incremental Ghost state,
  each replacement under a ruling.

**H9**
- **L.** Narrow the Ghost copies to the slot that changes. Constant-factor only.

**H10**
- **L + R.** Distinguish native or Ghost resource failure from a semantic refusal in the transport codes. That needs
  ABI review, possibly O.

**Forbidden under the native rule** ("Do not add a domain cap, count native failure as an accepted refusal, substitute
a proof-only light library or suppress checked Ghost code", HANDOFF.md):
- caps or Pre on Count / Length / rows / arena;
- treating `-1` / `255` / `False` / `CoreUnavailable` from these failures as accepted refusals;
- the light `SPARK.Big_Integers` unit;
- Assertion_Policy `Ignore` for Ghost / Post / Loop_Invariant, an `Assertion_Level` disabled at run time, or
  `pragma Suppress`;
- deploying `release` as the D2 closure;
- weakening or removing invariants, Posts or references;
- Off wrappers or renamed libraries.

## 6. Packet deltas (candidates, untested, not in the candidate composition)

All three stack exactly on the candidate files [OBS]: their `stacks_on` hashes equal the candidate hashes in section 0.

**P14 `14-chain-replay-reference-lemmas`**
- Result `worldline-chain_authority.adb` `d003cd49ca418ab5b721bb241edf932aeab5e43f7394df1e1018804f93351a56`.
- Each successful iteration adds an assert of P(Count+1) and a `Link` assert.
- The success path becomes **11·2^(n+1) - 2n - 14**, against 9·2^(n+1) - n - 10.
  - n = 3: J11 = J12 = 156.
  - n = 10, 20, 30: 22494, 23068618, 23622320054 (J19-J21).
- An early return at Count = c adds (2(n-c)+1)·P(c+1) + Σ_{To=c+1}^{n} P(To) through the assert and the new recursive
  `Prefix_Settled`, depth n - c (instance n = 3, c = 0: J84 = J85 = 46).
- Class unchanged (exponential), constant increased.

**P13 `13-iterative-prefix-tail`**
- Result `resource_reservation_transition.adb` `5f106d5e711d14c5a7a0ac7ddc2f00136b4b5b180d63a6d0ad1868f53f5b9208`.
- `Prefix_Tail`: recursive Θ(m³) becomes an iterative loop whose invariants and asserts evaluate `Prefix_Reference` at
  absolute positions and `Power_Factor (First, Reached)`. Result Θ(m·S³ + m²·S²), where m = Stop - First and S = Stop.
- `Prefix_Decomposition`: Θ(m·S³) becomes Θ(m²·S³), because each level adds evaluations of `Prefix_Tail` and the
  `Positive_Factor_Cancellation` actuals.
- Reached only through `Magnitude_Columns` / `Addition_Mismatch`, once per `Magnitude_Sum_Equals` / `Is_Successor` call
  on the mismatch path. The callers' class is unchanged (at most Θ(L⁵) there, beside Θ(L⁶) or Θ(L⁷) loops).
- `Prefix_Tail` recursion depth m disappears. `Prefix_Reference` chains of depth up to S remain.

**P12 `12-iterative-body-local-witnesses`**
- Results: `evaluation_epoch.adb` (both copies) `3131f36c77e458ecbe2adc71d648ed15adf7418cd5cf1d9a961ac1b81fd0fcaa`;
  `worldline-resources.adb` `c16618a47dfcf7330d0846ff0f6e3ef032071551abf4d5c1cd5ca901efb86f44`.
- Recursion becomes loops. Same classes:

| Lemma | Class (before and after) |
|---|---|
| epoch `Power_Factor` | Θ((H-L)·H⁴) |
| epoch `Prefix_Tail` | Θ((H-L)·H⁵) |
| resources `Power_Quotient` | Θ((H-L)·H²) |
| resources `Prefix_Quotient` | Θ((H-L)·H³), with one extra `Prefix_Step` per step (constant factor) |

- A per-step Post evaluation is replaced by a per-step invariant evaluation.
- The witness recursion depth disappears.
- Reached only on mismatch lemmas, once per call.

## 7. Base (commonV4) against the candidate

Byte-identical in base and candidate [OBS]:
- worldline-chain_authority.ads/.adb;
- resource_run_ledger.ads/.adb;
- resource_ledger.ads;
- canonical_artifacts.ads;
- worldline_core_sources.gpr.

The diffs in resource_quantities.ads/.adb, resource_ledger.adb, worldline-resources.ads/.adb, evaluation_epoch.adb,
resource_reservation_transition.adb and canonical_artifacts.adb consist of:
- parenthesisation;
- added non-recursive contradiction lemmas (O(1) Big_Integer operations at operand size);
- in canonical_artifacts.adb, one O(1) loop invariant and a case-selector subtype.

No growth class above differs between base and candidate [DER from the diffs].

## 8. Could not be determined statically

- Actual time, heap, primary or secondary stack, allocator behaviour, and whether stack or heap exhaustion surfaces as a
  catchable `Storage_Error` or kills the process. Nothing was run.
- Whether GCC `-O2` merges or elides any duplicate evaluation.
- Which build is actually deployed or loaded (O-BUILD-SELECTION), and the exact linked or loaded runtime.
- Production input sizes: retained receipt/event counts, run-ledger rows, ledger arenas, epoch and sequence byte
  lengths, journal and history lengths. Only the Python ledger and headroom sizing was read.
- Complete tracing of every export listed in 3.7, and of the Attest SHA-256 checked costs. These were inspected as
  constant per block, not analysed in depth.
- Whether the iterative or reformulated repairs in section 5 are provable with GNATprove 16.1.0. The recursive-contract
  limitation applies.
- Exact closed forms for the composite functions beyond the derived primitives. Only classes or lower bounds are given.

## 9. JACKAL calls

All calls used evaluator `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`. Every result is
status=exact, formal=false.

**non_claims, verbatim**
- exact lane: `["NOT formal-bounded: this lane carries no Lean-checked certificate", "The epistemic class above is the
  STRONGEST claim this result supports", "exact rational arithmetic (not yet checker-covered)"]`.
- poly-eq lane: last entry `"decidable polynomial identity over Q[x]"`.
- poly-canon lane: last entry `"dense Q[x] canonical form (degree <= 64)"`.

**Refusals**
- **J02** `2^(0+1) - 1` and **J06** `9*2^(3+1) - 3 - 10` were **refused**: `evaluator-refused`, "rat: ^ requires an
  integer exponent in exact mode; fail closed".
- The same questions were re-posed with literal exponents (J07, J08). No weaker lane was used.

The full list, with inputs, parsed forms and results, is in `inventory.json` `jackal`.

**Key results**

| Group | IDs | Results |
|---|---|---|
| Chain recurrence and step identity | J01 | identity holds |
| Chain sums (instance checks) | J03-J05, J07-J12 | 57; 131; 41; 156 |
| Chain totals | J13-J22 | as in sections 3.1 and 6 |
| Chain Link counts | J23-J24 | 6 |
| RPW, RP, S, PVW, PV identities | J25-J31, J65 | all hold |
| Bases | J32, J68-J71 | — |
| PV instances | J33-J41 | as in sections 2.2 and 3.4 |
| Compare multiplicities | J42, J55, J56, J58 | 42; 50; 42; 8 |
| Value and Compare products | J43-J48 | as in sections 2.2 and 3.2 |
| Thresholds | J49-J53, J72-J74 | as in sections 1.5 and 3.4 |
| Small multiplicities | J54, J57, J66, J67, J79-J83 | — |
| Packet 14 early-return instance | J84-J85 | 46 |
| Canonical degrees | J75-J78 | PV degree 4, RP degree 3, Compare×PV degree 5, Value degree 4 |

Exact mathematics stays informational about code correctness. These identities count source evaluations under the
stated model. They are not proofs of GNAT behaviour.

## 10. Non-claims

- No measurement or timing, and no proof, build or test, was performed.
- No growth statement is a measured cost.
- No review, acceptance, clearance or approval is claimed or granted.
- D2, O-GHOST and EXACT_NATIVE_MODEL_CHECKED_GHOST_COST stay OPEN.
- Release-build avoidance is not proposed as a closure.
- No cap, Pre, accepted-refusal path, light library or suppression is proposed.
- Counts assume RM evaluation semantics and the cited GNAT documentation, not observed compiler output.
- Packet deltas are analyses of drafted, untested packets.
- Source identities establish byte observations, not provenance or custody.

## Appendix A: Ghost and recursive declarations found by the scan

A read-only regex scan of `core/*.ads` and `core/*.adb` printed 171 declaration rows [OBS]. Spec and body declarations
are counted separately. Classes are [DER]. "O(1)" means fixed-size records, hashes or identities, independent of row
count and quantity length.

| Unit | Declarations (line) and class |
|---|---|
| worldline-chain_authority.ads | `Prefix_Step` 42 O(1)+Link; `Finish_Reference` 62 O(1); **`Prefix_Reference` 74 exponential**; **`Replay_Reference` 87 2·P(n)** |
| resource_quantities.ads | `Power_Reference` 40 Θ(e²); `Prefix_Reference` 46 Θ(c³); **`Radix_Power` 57 Θ(e⁴)**; **`Prefix_Value` 68 Θ(c⁵)**; `Magnitude` 84 and `Value` 91 Θ(L⁵) |
| resource_quantities.adb | `Scale_Column` 15, `Column_Bounds` 40, `Higher_Column_Order` 65 Θ(255·size); `Radix_Power_Worker` 97 Θ(e³); `Prefix_Value_Worker` 147 Θ(c⁴); `Prefix_Bounds` 230 Θ(c⁴); `Prefix_Monotone` 258; `Prefix_Padding` 277; `Borrow_Column_Facts` 297 O(1) |
| resource_ledger.ads | `Contains` 52 O(1); `Canonical_In_Slot` 61 O(arena); `Arena_Frame_Zero` 75 O(D·N); `Output_Representation` 81; `Withheld_Reference` 99 Θ(L⁵); `Row_Reference` 112 Θ(L⁵); `Total_Reference` 124 Θ(k·L⁵); **`Prefix_Total` 132 Θ(c³·L⁵)**; **`Storage_Sufficient` 148**; `Result_Conforms` 162; `Headroom_Reference` 215, `Headroom_Storage_Sufficient` 226 (`Radix_Power` of capacity), `Headroom_Conforms` 235 |
| resource_ledger.adb | `Whole` 7 O(1); `Column_Product` 13 Θ(Factor·size); `Column_Bounds` 35; `Power_Factor` 54, `Power_Monotone` 73, `Prefix_Quotient` 89 recursive; `Positive_Multiple` 131, `Witness_Below_Contradiction` 151 / `Witness_Above_Contradiction` 174, `Remainder_Witness` 196 O(1) at operand size; `Advance_Column` 214, `Combined_Remainder` 260 (Magnitude actuals at callers); `Equal_Prefix` 303, `Padded_Prefix` 323, `Bounded_Prefix` 341, `Zero_Extension` 385 recursive; `Magnitude_Remainder` 367; `Output_Prefix_Value` 402 and `Trimmed_Value` 421 **Θ(O⁵)**; `Lift_Slice` 439; `Prefix_Total_Worker` 500 Θ(c²·L⁵); `Total_Worker_Recurrence` 534; `Ordered_Magnitude_Columns` 568; `Written_Prefix_Step` 625; `Quantity_Slot_Frame` 658; `Checked_Detail_Step` 692; `Retained_Detail_Frame` 755; `Binary_Reference` 1039 (2 Value); `Binary_Signs` 1047; `Processed_Conforms` 1388 |
| resource_run_ledger.ads | `Amount_Reference` 187 ≤ 3 Value; `Sum_Reference` 200 Θ(k·L⁵); `Conserved_Reference` 236; `Contained_Reference` 255 Θ(N²·L⁵); `Changed_Row_Composition_Equality` 332; `Decision_Reference` 376 |
| resource_reservation_transition.ads | `Counted_Amount` 175, `Conserved_Reference` 181, `Same_Reservation_Reference` 189, `Proposed_Row_Reference` 201, `Change_Reference` 221, `Operation_Row_Reference` 260, `Final_Transition_Reference` 285, `Decision_Reference` 304, `Decision_Composition_Equality` 333: fixed numbers of Value, so Θ(L⁵) |
| resource_reservation_transition.adb | `Prefix_Step` 7 Θ(c⁵); `Prefix_Padding` 34; `Power_Factor` 56; `Prefix_Tail` 85 Θ(m³); `Prefix_Decomposition` 96 Θ(m·S³); `Magnitude_Columns` 126; column and contradiction lemmas 145-364 O(1) at operand size; `Addition_Mismatch` 383; `Addition_Finish` 450; **`Zero_Prefix` 483 Θ(c⁶)**; `Nonnegative_Magnitude` 504 |
| worldline-resources.ads | `Radix_Power` 29 Θ(c²); `Prefix_Value` 33 Θ(c³); `Magnitude` 43; `Fits_Mathematically` 47; `Reserve_Mathematically_Conforms` 109 |
| worldline-resources.adb | `Power_Quotient` 9; `Prefix_Quotient` 32; scalar witnesses 71-147 O(1) at operand size; `Power_Order` 177; `Complete_Prefix` 197; `Prefix_Growth` 209; `Low_Prefix_Exact` 225; `Prefix_Modulus` 238; `Value_Modulus` 263; **`Matching_Prefix` 276 Θ(c⁴)**; `Prefix_Step` 294 Θ(c³); column lemmas 314-599; `Mismatching_Sum_Column` 679 |
| evaluation_epoch.adb | `Scale_Column` 14; `Column_Bounds` 35; `Prefix_Step` 66 Θ(c⁵); **`Prefix_Bounds` 98 Θ(c⁶)**; `Prefix_Padding` 118; `Power_Factor` 140; `Prefix_Tail` 161; scalar witnesses 196-330; `Prefix_Modulus` 360; `Magnitude_Modulus` 386; `Unsigned_Value` 410; `Carry_Input` 425 Θ(c⁵); `Column_Division` 434; `Matching_Column` 450; `Increment_Modulus` 483; `Mismatching_Column` 497 |
| resource_admission.ads | `Numeric_Rejection` 76 O(size); `Binary_Reference` 88 (2+2 Value); `Concurrency_Reference` 101, `Pressure_Reference` 110, `Disk_Bytes_Reference` 118, `Disk_Inodes_Reference` 124 (each 2× `Binary_Reference`); `Capacity_Reference` 130; `Decision_Conforms` 155 Θ(D·L⁵) |
| worldline-recovery_authorization_v3.ads | `Same_Epoch_Reference` 33 (2 Epoch_Valid + 2 Value); `Same_Binding_Reference` 76; `Action_Reference` 175 |
| worldline-recovery_authorization_v3_wire.adb | `Equal_Prefix` 3 Θ(c⁴); `Zero_Padding` 22 Θ((k+1)·L⁵); `Positive_Prefix` 46 Θ(c³) |
| evaluation_completion.ads | `Update_Composition_Equality` 387 |
| evaluation_finalization.ads / .adb | `Seal_Classification_Equation` 343, `Seal_Equation` 353; `Lemma_Selected_Same` 154, `Lemma_Content_Erasure` 175 (rows and roster: polynomial, no quantity arithmetic seen) |
| resource_reservation_lifecycle.ads | `Plan_Conforms` 76 O(n) |
| worldline-owner_transitions.ads | `Query_Equation` 118, `Retry_Equation` 131 O(H·id) |
| canonical_artifacts.ads (recursive, non-Ghost) | `Prefix` 32, `Tagged_Matches` 61: constant-factor checked overhead |

Ghost objects: `resource_quantities.adb:413-414`, `:444-457`; `resource_ledger.adb:947`, `:1017`, `:1143-1149`,
`:1273`, `:1424`; `resource_reservation_transition.adb:6`; `worldline-resources.adb:796`, `:860`, `:873-875`, `:973`,
`:989`, `:1004` [OBS].
