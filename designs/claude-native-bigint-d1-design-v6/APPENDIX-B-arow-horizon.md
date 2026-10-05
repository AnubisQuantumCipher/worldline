# Appendix B to D1 DESIGN v6: Theorem H-A re-presented over A-ROW's final ghost text (R-H-A, V5-RC3)

Status: **[LEAD] design-level argument, unreviewed and unproved.** v5's version of this argument was found false by
the sealed v5 review (R-H-A): RL-25 and RL-25E were originally successful inputs on which v5's A-ROW checks build
formed `2**6432`. This version is re-presented over the **final** A-ROW text of DESIGN.md §5.12-§5.13, in which those
two causes are repaired (V5-RC1, V5-RC2), and it enumerates every construct of that text. It closes nothing by itself.
Closure of F35 for A-ROW needs an independent re-review of this argument, the proofs PO-A27..PO-A33 and PO-A35, the
DR-C6 review of the final source text (PO-A32), and observation of RL-24, RL-25 (z, n), RL-25E (z, n) and RL-26 in the
checks build. F35 stays OPEN for A-COL (B.11).

Arithmetic facts are JACKAL results, cited by their DESIGN.md §15 identifiers. Code references are to DESIGN.md
§5.3 (helpers), §5.4 (`Selected_Sum`), §5.5 (the shared Post), §5.6 (LA-10), §5.7 (`Pair_Sum_Order`), §5.8 (callers),
§5.12 (A-ROW executable and ghost text) and §5.13 (A-ROW lemmas). Bare `core/…` paths are the C5 source tree.

## B.0 Why a horizon argument is needed

GNAT 16.1.0 represents a Big_Integer only below `2**6432` (F1; `256**804 = 2**6432` [K-65], which needs 6433 bits
[K-05]). Under `-gnata` every ghost construct executes. So a checks-build evaluation fails whenever any Big_Integer
value it forms, final or intermediate, reaches `2**6432` in magnitude. A D1 construct must therefore never form such a
value on an input where the original's own checked evaluation forms none (no new checked failure, no domain
restriction, no refusal; `START-CLAUDE.txt:8`, `HANDOFF.md:29, 129`).

## B.1 Definitions

- **x.** Any input of the original domain of `Conserved`, `Contained` or `Check`: any `Data` (any bounds), any `Rows`
  (any bounds and length), any quantities, signed, invalid, duplicate-identity or padded, whether reached through the
  run-ledger C export or by a direct Ada call. No Pre exists, and none is added.
- **orig(f, x).** The checks-build evaluation of the original `f` on x: its body, every contract, loop invariant and
  assertion it executes, and every public ghost function those reach (recursively, each with its own Post).
- **D1(f, x).** The same for the D1 version of `f`, with A-ROW as `Selected_Sum_Order`'s body and the three-operand
  column engine as `Pair_Sum_Order`'s body.
- **Formed value.** Any Big_Integer value computed in an evaluation: a function result, an operand or result of
  `+`, `-`, `*`, unary `-`, `abs`, a conversion result, a saved `'Old` or `'Loop_Entry` value.
- **H.** The bound `2**6432`. A value is representable iff its magnitude is below H.
- **succeeds.** orig(f, x) succeeds iff it forms only representable values.
- For one `Selected_Sum_Order (Data, Rows, Parent, Mode, Target)` call: `E` is its extent (the maximum of
  `Effective_Length` over the target, every selected amount and the usage of every selected `Usage_Candidate` row;
  V4-RC1), `P = 256**E`, `S_K (k)` the original's partial sum `Sum_Reference (Data, Rows, k, Parent, K)` for kind `K`,
  `S` the selected total (`S_K (N)` for one kind; `S_H (N) + S_B (N)` for `Both_Kinds`), and `v_t` the target's value.
- **Span classes.** For a reached call, a quantity span of `Data` is:
  - **T**, the target (`State.Held_Total`, `State.Charged_Total` or `Rows (I).Amount`);
  - **A**, the amount of a row that is `Selected` for the call;
  - **U**, the usage of a `Selected` row with `Usage_Candidate` (Held and usage present);
  - **O**, an operand `Op = Operand (row)` of a selected row, which is its A or, only when `Usage_Selected`, its U;
  - **C**, one of `Check`'s three capacity operands (`Proposed.Held_Total`, `Charged_Total`, `Capacity`).
- **Value classes.** **W**: a member of the original's formed set (B.4). **L**: a local value of magnitude at most
  `2·P` (accumulator prefixes, `P(i)` for `i ≤ E`, the conditional low-part relations). **I**: integer only, no
  Big_Integer.

## B.2 Statement

**Theorem H-A.** For every `f` in {`Conserved`, `Contained`, `Check`} and every x: if orig(f, x) succeeds, then every
value formed by D1(f, x) is representable.

**Hypotheses on D1 itself (each an open proof obligation).** The argument uses the functional correctness of A-ROW and
of `Pair_Sum_Order` as designed: the loop invariants, assertions and Posts of DESIGN.md §5.12-§5.13 hold whenever
evaluated (PO-A27..PO-A31, PO-A35, PO-A17, PO-A21). It is a statement about the design that is to be proved. It also
uses DR-C6 as a property of the final text (PO-A32).

## B.3 H0: alignment of reached calls

**Claim.** D1(f, x) evaluates a `Selected_Sum_Order` call with arguments (Parent, Mode, Target) only if orig(f, x)
evaluates the corresponding original expression:

| D1 call site (DESIGN.md §5.7-§5.8) | Original expression (C5) |
|---|---|
| `Conserved`: `Selected_Sum_Order (…, (Present => False), Held_Only, State.Held_Total) = Equal` | `Exact_Value (State.Held_Total) = Sum (…, Held_Capacity)` (`core/resource_run_ledger.adb:65-69`) |
| `Conserved`: `… Budget_Only, State.Charged_Total) = Equal` | `Exact_Value (State.Charged_Total) = Sum (…, Irreversible_Budget)` |
| `Contained` loop 2, iteration I: `… Rows (I).Bound.Reservation, Both_Kinds, Rows (I).Amount) = Greater` | `Sum (…, Held) + Sum (…, Budget) > Exact_Value (Rows (I).Amount)` (`:85-86`) |
| `Check` capacity branch: `Pair_Sum_Order (Held_Total, Charged_Total, Capacity) = Greater` | the original capacity condition (`:173-174`) |

**Argument.** The D1 bodies keep the original control structure: the same short-circuit conjunctions in `Conserved`,
the same loop 1 and loop-2 invariant in `Contained`, and the same branch order in `Check` (DESIGN.md §4.1, §5.8). Each
replaced test returns the same Boolean as the original test (PO-A15, PO-A16, PO-A17, PO-A20). By induction over the
evaluation order, both evaluations reach the same sequence of call sites with the same arguments. In Ada both operands
of `=`, `+` and `>` are evaluated before the operator, so when orig(f, x) succeeds it has evaluated both sides of every
reached original expression. The v5 review found H0 sound.

Every other construct of D1(f, x) (loop 1, the loop-2 invariant, `Shape`, the public Posts, every other `Check`
branch) is byte-identical to the original and evaluated identically, so its formed values are formed by orig(f, x)
(GT-49).

## B.4 H1: the original's formed set W

For one reached call, orig(f, x) forms at least the following, by source [OBS `core/resource_run_ledger.adb:19-90`,
`.ads:185-213`; F39]:

| Member of W | Formed by |
|---|---|
| `S_K (k)` for every k in `0 .. N` and each kind `K` that the original sums at that site | `Sum`'s loop invariant `Result = Sum_Reference (Data, Rows, Count, Parent, Kind)` at every iteration (`:56`), its Post at `N`, and the recursive evaluation, which forms every shorter prefix |
| `Amount_Reference (row)` for every included row, and `Q.Value` of the amount and, for a Held row with usage present, of the usage | `Amount`'s body: `Exact_Value (Item.Amount)` first, then `Exact_Value (Item.Observed_Usage.Value)` under `Kind = Held_Capacity and then Present` (`:36-48`); each `Exact_Value`'s Post `Q.Value (…)`; `Amount`'s Post `Amount_Reference` |
| `256**L` for each valid span of Length L above (A and U spans of included rows) | `Exact_Value`'s body: `Place := Place * 256` at every digit (`:19-34`, `:31`) |
| `Magnitude` and `Prefix_Value (L)` of those spans | `Q.Value`'s body and Post (`core/resource_quantities.adb:210-226`) |
| the selected total `S` | `Sum`'s Post (one kind), or `Sum (Held) + Sum (Budget)` in `Contained` (`:85-86`) |
| `v_t`, `Magnitude (T)` and `256**L_t` when the target span is valid with Length `L_t` | `Exact_Value (target)` and its Post |
| for `Check`'s capacity branch: the values of the three capacity operands and `Value (Held) + Value (Charged)` | the original capacity expression and `Decision_Reference`'s capacity conjunct (`.ads:406-407`) |

Selected rows are exactly the included rows of the summed kinds (`Selected`'s definition; for `Both_Kinds`, the
two-valued `Charge_Kind` partition, `.ads:36, 195-199`). So the A spans are the amount spans the original evaluates,
and the U spans are exactly the usage spans the original evaluates.

**Lemma W1.** If orig(f, x) succeeds, then for every reached call every valid T, A and U span has Length at most 803,
so `E ≤ 803`, `P ≤ 256**803 = 2**6424` [K-188], `2·P < 2**6432` [K-226] and `3·256**803 < 2**6432` [K-248].

*Proof.* A valid span of Length `L ≥ 804` makes `Exact_Value` form `256**L ≥ 256**804 = 2**6432` [K-65], which is not
representable. `Effective_Length` is `Length` for a valid span and 0 otherwise. Every span that contributes to `E` is a
T, A or U span (the pre-pass reads a usage only under `Usage_Candidate`). ∎

W does **not** contain: one-sided sums of magnitudes, truncated rows, the mixed partial sums `S_H (k) + S_B (k)` for
`k < N`, or any value of a Budget row's usage (`Amount` and `Amount_Reference` never evaluate it).

## B.5 The safe-form principle

**Lemma S (nonnegative sums).** If an expression is a left-associated sum `t_1 + … + t_m` of nonnegative terms, then
every partial sum is at most the total. So if the total and each term are representable, every intermediate is.

**Lemma S′ (products).** For `Hi ≥ 0`, `0 ≤ LV < P` and `A = LV + Hi·P`: `0 ≤ Hi·P ≤ A`. For `Hi < 0`:
`abs A = (P − LV) + (−Hi − 1)·P`, both terms nonnegative, `P − LV ≤ P` and `(−Hi − 1)·P ≤ abs A`. In both cases
`Hi ≥ 0` iff `A ≥ 0`, so a case split on `A`'s sign is an integer case split on `Hi`.

**DR-C6 (as stated in DESIGN.md §5.14).** Every Big_Integer expression in D1-A's ghost text either evaluates a public
function on a T, A, U, O or C span; or is a W value, or a binary operation whose operands and result are W values; or
is a nonnegative-term sum whose total is a W value in magnitude, with products bounded by Lemma S′; or is an L value.

## B.6 H2: the complete construct inventory of the final A-ROW text

Every construct of DESIGN.md §5.12-§5.13 and of the shared text A-ROW reaches is listed, including integer-only ones,
so that nothing is omitted. "Spans" lists every quantity span of `Data` passed to a Big_Integer-forming function, by
class. "Bound" gives the magnitude bound of every Big_Integer value formed.

| GT | Construct (location) | Spans | Values formed | Bound |
|---|---|---|---|---|
| GT-01 | `Selected_Sum_Order` Post (§5.5) | T | `Selected_Sum (N, Mode)` (= `S_K (N)` or `S_H (N) + S_B (N) = S`), `Q.Value (Target)` | W |
| GT-02 | pre-pass loop invariants (2) (§5.12) | — | `Effective_Length` comparisons | I |
| GT-03 | pre-pass statements: `Selected`, `Usage_Candidate`, `Effective_Length`, `Q.Byte_Count'Max` | — | none | I |
| GT-04 | `E = 0` branch: the LA-11 call and `return Equal` | see GT-43..GT-45 | — | — |
| GT-05 | allocation, inner block, handler, `Free_Acc` | — | none | I |
| GT-06 | `Decide_Rows` Pre | — | `Effective_Length` and byte comparisons | I |
| GT-07 | `Decide_Rows` Post | T | `Selected_Sum (N, Mode)`, `Q.Value (Target)` | W |
| GT-08 | executable `Operand` → `Usage_Selected` → `Q.Compare` (per selected row) | U, A (normalized); reached only when `Kind = Held_Capacity and then Present` | `Compare`'s checked Post: `Q.Value` of both normalized spans; checked body: prefixes, `Prefix_Padding`, `Prefix_Bounds`, `Column_Bounds`, `Higher_Column_Order`, `Is_Negative` Posts (`core/resource_quantities.adb:340-402`) | W for the values; body intermediates at most `256**L ≤ 256**803` (G1c; the v5 review checked it) |
| GT-09 | LA-9N Post, conjunct 1 | A; `Normalized (A)` = A or `Empty_Quantity` | `Q.Value (Normalized (A))`, `Q.Value (A)` | W (or 0 for `Empty_Quantity`) |
| GT-10 | LA-9N Post, conjunct 2, **guarded by `Usage_Candidate (Item)`** (V5-RC1) | U only; never a Budget usage | `Q.Value (Normalized (U))`, `Q.Value (U)` | W (or 0) |
| GT-11 | LR-2 assertion `Q.Value (Data, Op) = Amount_Reference (Data, Rows (J))` | O; `Amount_Reference` reads A and, only under `Held and then Present`, U | `Q.Value (Op)`, `Amount_Reference (row)` | W |
| GT-12 | LA-10 Post, called with `Mode_Of_H (Mode)` and (for `Both_Kinds`) `Budget_Only` only | A, U through `Amount_Reference` of the selected row, and of included rows inside `Sum_Reference` | `Selected_Sum (k + 1, M)`, `Selected_Sum (k, M)` (per-kind `S_K`), `Amount_Reference (row)` when selected, and their sum, which is `S_K (k + 1)` | W |
| GT-13 | row-loop invariants 1-3 (`abs Hi_H`, `abs Hi_B`, `Hi_B = 0`) | — | integer comparisons | I |
| GT-14 | row-loop invariant 4 | via `Sum_Reference` (A, U of included rows) | `Acc_Value (H, Hi_H)`, `Sum_Reference (k, Kind_Of_H (Mode))` | `Acc_Value = S_K (k)` (W) with intermediates `max (abs A, P)` (Lemma S′); `S_K (k)` W |
| GT-15 | row-loop invariant 5 (`Both_Kinds`) | as GT-14 | `Acc_Value (B, Hi_B)`, `Sum_Reference (k, Irreversible_Budget)` | W, as GT-14 |
| GT-16 | AFTER assertion | — | `Acc_Value (H, Hi_H) = S`, `Selected_Sum (N, Mode)` | W |
| GT-17 | `Add_Operand` Pre | — | `Effective_Length`, `Hi` range | I |
| GT-18 | `Add_Operand` Post | O | `Acc_Value (Low, Hi)'Old` (= previous partial sum), `Q.Value (Op)`, their sum, `Acc_Value (Low, Hi)` (= next partial sum); `Hi` range | W |
| GT-19 | ghost constants `Old_Low`, `Old_Hi` | — | byte copy, integer | I |
| GT-20 | `Add_Operand` loop invariants 1-2 (carry bound, frame) | — | integer and byte comparisons | I |
| GT-21 | `Add_Operand` loop invariant LR-3 (DR-C5 conditional form) | O | `Low_Prefix (Low, I)`, `Low_Prefix (Old_Low, I)` (each `< P(I)`), `Q.Prefix_Reference (Data, Op, I)` (`≤ Magnitude (Op)`, `< P(I)`), `P(I)` only on the carry branch; each side at most `2·P(I)` | L |
| GT-22 | LR-3P `Lemma_Operand_Padding` (on Op in `Add_Operand`; on the target in `Compare_To_Target`) | O or T | Post `Q.Prefix_Reference (X, K) = Q.Magnitude (X)`; body assertions `Magnitude = Prefix_Value (L)` and `Prefix_Value (L) = Prefix_Reference (L)`; loop invariant `Prefix_Reference (X, M) = Prefix_Reference (X, L)` for `M ≤ K = E` | W (`Magnitude`, `Prefix_Value (L)` are formed by the original's `Q.Value`); prefixes `≤ Magnitude (X)`; powers inside `Prefix_Reference (X, M)` at most `P(E − 1)` |
| GT-23 | LR-4 `Lemma_Add_Step` Pre | O | `Prefix_Reference (Op, E) = Magnitude (Op)`; the low relation: `Low_Value (Low)`, `Low_Value (Old_Low)`, `Magnitude (Op)`, `P(E)`, sides at most `2·P` | W and L |
| GT-24 | LR-4 Post | O | `Acc_Value (Old_Low, Old_Hi)`, `Q.Value (Op)`, their sum, `Acc_Value (Low, Hi)` | W |
| GT-25 | LR-4 body (B.7.1): LR-6 on `Low`, `Old_Low` and `Op`; per sign row one (D) split and one (R) equation | O | (D): `To_Big (a)·P + To_Big (b)·P = To_Big (a + b)·P` with `a, b ≥ 0` and `(a + b)·P` a P-multiple term of a row side; (R): nonnegative-term sums whose side totals are `max (abs A_0, abs A_1, abs v)` | W (Lemma S, Lemma S′) |
| GT-26 | `Add_Accumulator` Pre | — | integer | I |
| GT-27 | `Add_Accumulator` Post | — | `Acc_Value (H, Hi_H)'Old = S_H (N)`, `Acc_Value (B, Hi_B) = S_B (N)`, their sum, `Acc_Value (H, Hi_H) = S` | W |
| GT-28 | `Add_Accumulator` loop invariants 1-2 | — | integer | I |
| GT-29 | `Add_Accumulator` loop invariant LR-3A | — | `Low_Prefix (H, I)`, `Low_Prefix (Old_H, I)`, `Low_Prefix (B, I)` (each `< P(I)`), `P(I)` on the carry branch; sides at most `2·P(I)` | L |
| GT-30 | LR-4A `Lemma_Accumulate_Step` Pre | — | the low relation at E (sides at most `2·P`); the integer identity `Hi_H = Old_Hi_H + Hi_B + C` | L, I |
| GT-31 | LR-4A Post | — | `Acc_Value (Old_H, Old_Hi_H)`, `Acc_Value (B, Hi_B)`, their sum, `Acc_Value (H, Hi_H)` | W |
| GT-32 | LR-4A body (B.7.2): LR-6 on `H`, `Old_H`, `B`; (D) and (R) per sign row | — | as GT-25, with side totals `max (abs S_H, abs S_B, abs S)` | W |
| GT-33 | `Compare_To_Target` Pre | — | integer | I |
| GT-34 | `Compare_To_Target` Post (LR-5) | T | `Acc_Value (Low, Hi)` (= S or `S_K (N)`), `Q.Value (Target)` | W |
| GT-35 | `Neg` (executable digit quantifier), the `Hi` case split | — | none | I |
| GT-36 | assertions `Hi·P ≥ P` (`Hi ≥ 1`) and `(−Hi − 1)·P ≥ P` (`Hi ≤ −2`) | — | `To_Big (Hi)·P` (`≤ A`), `To_Big (−Hi − 1)·P` (`≤ abs A`), `P` | W (Lemma S′) |
| GT-37 | MSB loop invariant (`Hi = 0` branch) | — | byte and digit comparisons | I |
| GT-38 | LR-5a `Lemma_First_Difference` (contract and body) | T | `Low_Value (Low)`, `Prefix_Reference (Target, E)`; body: LR-6 at `I − 1`, LA-4 at `P(I − 1)` (values `< P(I)`), loop invariant comparing `Low_Prefix (Low, K)` with `Prefix_Reference (Target, K)` (each `< P(K)`) | L; `Prefix_Reference (Target, E) = Magnitude (T)` W |
| GT-39 | LR-5b `Lemma_Equal_Prefixes` | T | `Low_Prefix (Low, M)`, `Prefix_Reference (Target, M)` for `M ≤ E` | L |
| GT-40 | `Hi = −1` loop invariants: `Nonzero` and the conditional sum | T | `Low_Prefix (Low, I) + Prefix_Reference (Target, I)` (`< 2·P(I)`), `Low_Prefix (Res, I)`, `P(I)` on the carry branch | L |
| GT-41 | LR-5c `Lemma_Zero_Prefix` on `Res` | — | `Low_Prefix (Res, M)`; LR-6 bound `< P(M)` | L |
| GT-42 | ghost writes to `Res` | — | bytes | I |
| GT-43 | LA-11 `Lemma_Zero_Extent` Pre and Post (v6 body, V5-RC2) | T | Pre: `Effective_Length` only; Post: `Selected_Sum (N, Mode)` (`= 0`), `Q.Value (Target)` (`= 0`) | W |
| GT-44 | LR-0 `Lemma_Zero_Length_Value` calls in LA-11 | T; A of each selected row; U only under `Usage_Candidate` | `Q.Value (X)` with `Effective_Length (X) = 0`: 0, forming only `Prefix_Value (·, 0) = 0` and `P(0) = 1`, or nothing for an invalid span | W (= 0) |
| GT-45 | LA-11 loop: assertion `Amount_Reference (row) = 0` for a selected row; LA-10 per kind (as GT-12); invariants `Selected_Sum (k + 1, Mode_Of_H (Mode)) = 0` and, for `Both_Kinds`, `Selected_Sum (k + 1, Budget_Only) = 0` | A, U (only under `Held and then Present`) through `Amount_Reference` | per-kind `S_K (k)` = 0; `Amount_Reference` = 0 | W (= 0). No `Side_Sum`, `Side_Total`, LA-7 or `Both_Kinds` LA-10 (V5-RC2) |
| GT-46 | LR-6 `Lemma_Prefix_Bound` (on `Low`, `Old_Low`, `H`, `Old_H`, `B`, `Res`, Op and the target) | O, T, or an accumulator array | Post `Prefix_Reference (X, K) < P(K)`; body: LA-3 calls forming `Low + d·P(M − 1)`, `Low + (d mod 256)·P(M − 1)`, `(d / 256)·(256·P(M − 1))` with `d ≤ 255`, `256·P(M − 1) = P(M) ≤ P(E)`; LA-3's own body (the `Column_Bounds` pattern: `Scale_Column` up to `255·P(M − 1)`, gaps `≤ P(M)`) | L |
| GT-47 | ghost definitions: `Low_Quantity` (no value), `Low_Prefix`/`Low_Value` (`< P`), `Acc_Value` (G3), `Kind_Of_H`/`Mode_Of_H` (no value) | accumulator arrays only | `LV`, `Hi·P` (`Hi ≥ 0`), `P − LV`, `(−Hi − 1)·P`, `abs A`, `A` | `Acc_Value` is evaluated only on consistent states (GT-14..GT-16, GT-18, GT-24, GT-27, GT-31, GT-34), where `A` is a W value: intermediates `max (abs A, P)` (Lemma S′) |
| GT-48 | `Pair_Sum_Order` (Check's capacity branch; G8) | C | Post: `Value (First) + Value (Second)`, `Value (Target)`; column ghost `Pair_Side_Total`, LA-3..LA-6, LA-8 padding facts | Post values W; ghost values below `3·256**803 < 2**6432` [K-248]; powers at most `256**803` (the v5 review checked G8) |
| GT-49 | the D1 bodies of `Conserved` and `Contained` (loop 1, loop-2 invariant) and `Check`'s other branches | as the original | the original's own text | W (formed by orig(f, x)) |
| GT-50 | the pre-existing public functions reached by GT-01..GT-48: `Value`, `Magnitude`, `Prefix_Value` (with `Prefix_Value_Worker`), `Prefix_Reference`, `Power_Reference`, `Radix_Power`, `Compare`'s body (with `Prefix_Padding`, `Prefix_Bounds`, `Column_Bounds`, `Higher_Column_Order`, `Is_Negative`, `Is_Zero`) | only the spans listed in GT-01..GT-48 | their internal values on a span of Length L | at most `256**L ≤ 256**803` (F1; G1a, G1c) |

`'Old` values (GT-18, GT-19, GT-27) are copies of values already classified.

**Conclusion.** Every class is bounded by a W value, by `2·P ≤ 2·256**803 < 2**6432` [K-226], or by
`3·256**803 < 2**6432` [K-248]. By Lemma W1 all W values are representable when orig(f, x) succeeds. Hence every value
formed by D1(f, x) is representable. ∎

## B.7 LR-4 and LR-4A: the sign cases in safe form, with their derivations

Each lemma body asserts, per sign case, its coefficient splits (D) (at most one for LR-4, at most two for LR-4A) and
the row equation (R). The integer case
split uses Lemma S′ (`sign A = sign Hi`). The low residual is the Pre's conditional relation (sides at most `2·P`).

### B.7.1 LR-4 (`Add_Operand`)

Notation: before the step `A_0 = LV_0 + h_0·P`; the operand `v = ±m`, `m = Magnitude (Op) < P` (LR-3P, LR-6); after
the step `A_1 = LV_1 + h_1·P`, with `h_1 = h_0 + C` (nonnegative operand) or `h_1 = h_0 − C` (negative operand),
`C ∈ {0, 1}` [K-224, K-225]. LR-3: `LV_1 + C·P = LV_0 + m` (nonnegative) or `LV_1 + m = LV_0 + C·P` (negative).

| Row | Signs | (R) row equation, all terms nonnegative | Side total | Coefficients and (D) | Residual |
|---|---|---|---|---|---|
| 1 | `v ≥ 0`, `h_0 ≥ 0` (so `h_1 ≥ 0`) | `LV_0 + h_0·P + m = LV_1 + h_1·P` | `A_1` | `h_1 = h_0 + C`; if `C = 1`, (D) `h_0·P + P = h_1·P` (total `h_1·P ≤ A_1`) | `LV_0 + m = LV_1 + C·P` (LR-3) |
| 2 | `v < 0`, `h_0 ≥ 0`, `h_1 ≥ 0` | `LV_1 + h_1·P + m = LV_0 + h_0·P` | `A_0` | `h_0 = h_1 + C`; if `C = 1`, (D) `h_1·P + P = h_0·P` (total `≤ A_0`) | `LV_1 + m = LV_0 + C·P` (LR-3) |
| 3 | `v < 0`, `h_0 ≥ 0`, `h_1 < 0` (so `h_0 = 0`, `C = 1`, `h_1 = −1`) | `LV_0 + h_0·P + (P − LV_1) + (−h_1 − 1)·P = m` | `m = abs v` | both coefficients are 0; no (D) | `LV_1 + m = LV_0 + P` (LR-3, `C = 1`) |
| 4 | `v ≥ 0`, `h_0 < 0`, `h_1 ≥ 0` (so `h_0 = −1`, `C = 1`, `h_1 = 0`) | `(P − LV_0) + (−h_0 − 1)·P + LV_1 + h_1·P = m` | `m = v` | both coefficients are 0; no (D) | `P + LV_1 = LV_0 + m` (LR-3, `C = 1`) |
| 5 | `v ≥ 0`, `h_0 < 0`, `h_1 < 0` | `(P − LV_1) + (−h_1 − 1)·P + m = (P − LV_0) + (−h_0 − 1)·P` | `abs A_0` | `−h_0 − 1 = (−h_1 − 1) + C`; if `C = 1`, (D) `(−h_1 − 1)·P + P = (−h_0 − 1)·P` (total `≤ abs A_0`) | `(P − LV_1) + m = (P − LV_0) + C·P`, i.e. LR-3 |
| 6 | `v < 0`, `h_0 < 0` (so `h_1 < 0`) | `(P − LV_0) + (−h_0 − 1)·P + m = (P − LV_1) + (−h_1 − 1)·P` | `abs A_1` | `−h_1 − 1 = (−h_0 − 1) + C`; if `C = 1`, (D) `(−h_0 − 1)·P + P = (−h_1 − 1)·P` (total `≤ abs A_1`) | `(P − LV_0) + m = (P − LV_1) + C·P`, i.e. LR-3 |

Each side total is the largest of `abs A_0`, `abs A_1`, `abs v`, all W values (`A_0`, `A_1` are per-kind partial sums;
`v` is an `Amount_Reference`). Each (D) total is a P-multiple term of a row side, so it is at most that side's total.
Each residual has sides at most `2·P`. The Post `A_0 + v = A_1` then follows from (R), `Acc_Value`'s definition and
`Value = ±Magnitude`; it forms only `A_0`, `v` and `A_1`.

### B.7.2 LR-4A (`Add_Accumulator`): its own derivation (V5-RC3)

Here the high-part step is `h' = h + b + C` with `C ∈ {0, 1}` and `b` the Budget accumulator's high part, which is not
in {−1, 0, 1}; v5's claim that B.7.1 applies "with v replaced" is withdrawn. Notation: `A_H = LV_H + h·P = S_H (N)`,
`A_B = LV_B + b·P = S_B (N)`, `A' = LV' + h'·P = S`. LR-3A: `LV' + C·P = LV_H + LV_B`. Impossible sign combinations:
`A_H, A_B ≥ 0` forces `A' ≥ 0`; `A_H, A_B < 0` forces `A' < 0`.

| Row | Signs | (R) row equation, all terms nonnegative | Side total | Coefficient identity and (D) | Residual |
|---|---|---|---|---|---|
| 1 | `A_H ≥ 0`, `A_B ≥ 0` | `LV_H + h·P + LV_B + b·P = LV' + h'·P` | `A'` | (D1) `h·P + b·P = (h + b)·P` (total `≤ A'`); `h' = (h + b) + C`; if `C = 1`, (D2) `(h + b)·P + P = h'·P` (total `≤ A'`) | `LV_H + LV_B = LV' + C·P` (LR-3A) |
| 2 | `A_H ≥ 0`, `A_B < 0`, `A' ≥ 0` | `(P − LV_B) + (−b − 1)·P + LV' + h'·P = LV_H + h·P` | `A_H` | `K_L = (−b − 1) + h'`, `h = K_L + 1 − C`; (D1) `(−b − 1)·P + h'·P = K_L·P` (total `≤ A_H`); if `C = 0`, (D2) `K_L·P + P = h·P` | `(P − LV_B) + LV' = LV_H + (1 − C)·P`, i.e. LR-3A |
| 3 | `A_H ≥ 0`, `A_B < 0`, `A' < 0` | `LV_H + h·P + (P − LV') + (−h' − 1)·P = (P − LV_B) + (−b − 1)·P` | `abs A_B` | `K_L = h + (−h' − 1)`, `−b − 1 = K_L + C`; (D1) `h·P + (−h' − 1)·P = K_L·P` (total `≤ abs A_B`); if `C = 1`, (D2) `K_L·P + P = (−b − 1)·P` | `LV_H + (P − LV') = (P − LV_B) + C·P`, i.e. LR-3A |
| 4 | `A_H < 0`, `A_B ≥ 0`, `A' ≥ 0` | `(P − LV_H) + (−h − 1)·P + LV' + h'·P = LV_B + b·P` | `A_B` | `K_L = (−h − 1) + h'`, `b = K_L + 1 − C`; (D1) as row 2 (total `≤ A_B`); if `C = 0`, (D2) `K_L·P + P = b·P` | `(P − LV_H) + LV' = LV_B + (1 − C)·P`, i.e. LR-3A |
| 5 | `A_H < 0`, `A_B ≥ 0`, `A' < 0` | `(P − LV') + (−h' − 1)·P + LV_B + b·P = (P − LV_H) + (−h − 1)·P` | `abs A_H` | `K_L = (−h' − 1) + b`, `−h − 1 = K_L + C`; (D1) (total `≤ abs A_H`); if `C = 1`, (D2) `K_L·P + P = (−h − 1)·P` | `(P − LV') + LV_B = (P − LV_H) + C·P`, i.e. LR-3A |
| 6 | `A_H < 0`, `A_B < 0` | `(P − LV_H) + (−h − 1)·P + (P − LV_B) + (−b − 1)·P = (P − LV') + (−h' − 1)·P` | `abs A'` | `K_L = (−h − 1) + (−b − 1)`, `−h' − 1 = K_L + 1 − C`; (D1) (total `≤ abs A'`); if `C = 0`, (D2) `K_L·P + P = (−h' − 1)·P` | `(P − LV_H) + (P − LV_B) = (P − LV') + (1 − C)·P`, i.e. LR-3A |

Derivation of each coefficient identity: substitute `h' = h + b + C` (integer arithmetic in `High_Count`, no
Big_Integer). For example row 2: `h = h' − b − C = ((−b − 1) + h') + 1 − C`. Every (D) step splits one P-multiple term of
a row side into nonnegative P-multiples (or joins them), so its total is at most that side's total (Lemma S); every
residual has sides at most `2·P`. The side totals are `max (abs S_H, abs S_B, abs S)`, all W values formed by the
original's `Contained` (`Sum (Held)`, `Sum (Budget)` and their sum). The v5 review found the bounds of this lemma sound
by Lemma S′; this table supplies the derivation it asked for.

## B.8 Coverage of the exhibits

| Exhibit | Original's values | A-ROW's values (v6 text) | Result |
|---|---|---|---|
| RL-24 (F35): 514 children `±X`, `X = 2**6424 − 1` [K-184, K-188] | per-kind partial sums alternate `X` and 0 [K-186, K-187]; every value at most `256**803` | `A` alternates `X` and 0; `E = 803`; GT-21/GT-25 sides at most `X` or `2·P` | no value reaches `2**6432`; False in every build |
| RL-25 (F37, F40): Budget child, 804-byte usage, `E = 1` | the usage is never evaluated (`Amount`'s kind test) | the usage is never evaluated: GT-03 (`Usage_Candidate`), GT-08 (kind short-circuit), GT-10 (guard), GT-11/GT-12 (`Amount_Reference`'s kind test) | True in every build; no checked failure |
| RL-25E (F41): as RL-25 with Length-0 amounts, `E = 0` | the usage is never evaluated | XA0: LA-11 (GT-43..GT-45) applies LR-0 to the target and the amounts only; no `Side_Sum`, LA-7 or LA-9 | True in every build; no checked failure |
| RL-26 (F38): 65537 pairs `+X, −Y` [K-215..K-223] | the partial sums run `X`, −1, `X − 1`, −2, … (each pair sums to −1 [K-216]); every magnitude is at most `X < 2**6424` [K-223] | `A` takes the same values; `E = 803`; no truncated sum is formed | no value reaches `2**6432`; False in every build (checks-build cost OPEN) |
| W-11a: a selected Held child with an 804-byte amount | orig fails at `core/resource_run_ledger.adb:31` (`Place` reaches `256**804`) | D1 fails at `core/resource_quantities.adb:181` (the first checked `Value` of that operand) | on an input where the original also fails; the hypothesis of H-A does not hold, so this is consistent with it (the locations differ) |

## B.9 What changed from v5's argument

- G1a/G1b of v5 claimed that LA-9N evaluates only spans the original evaluates and that a Budget usage is never
  evaluated. That was false for v5's text (F40). In v6 the claim holds by GT-10 and GT-08/GT-11/GT-12's kind tests.
- v5 listed LA-11 as "as before" for A-ROW, but its only body plan was A-COL's LA-7 + LA-8 (F41). v6's LA-11 has its own
  body (GT-43..GT-45).
- v5's B.6 classified constructs by class only; v6 enumerates each construct of the final text (GT-01..GT-50) and
  writes out the lemma bodies (§5.13) and `Compare_To_Target` (§5.12) so that the inventory is over text, not comments.
- v5's B.7 derived LR-4A by analogy; B.7.2 derives it.
- v5's B.10 item 6 said W-11a fails "at the location the original also fails"; it fails on an input where the original
  also fails, at a different location (B.8, DESIGN.md §9.6).

## B.10 The universal statements, and what review must check (PO-A32)

**U-1 (span discipline; V5-RC3).** Every quantity span of `Data` that D1-A passes to a Big_Integer-forming function is
the target, a selected amount, the usage of a selected `Usage_Candidate` row, or one of `Check`'s three capacity
operands, or `Normalized` of one of these. `Normalized (X)` is X when X is valid, else `Empty_Quantity` (Length 0),
on which `Q.Value` forms only 0 and `P(0) = 1`. The only other arrays on which D1-A forms Big_Integer values are its
own accumulator arrays (`Acc.H`, `Acc.B`, `Old_Low`, `Old_H`, `Res`) through `Low_Quantity`, whose values are below
`256**E`.

**U-2 (no usage of a non-`Usage_Candidate` row).** No D1-A construct evaluates a usage span unless `Usage_Candidate`
holds for its row (R-EXTENT-2): GT-03, GT-08, GT-10, GT-11, GT-12, GT-44, GT-45.

**U-3 (no recursion added).** A-ROW adds no recursive function; no A-ROW construct reaches `Side_Sum`, `Side_Total`,
`Row_Term`, LA-7 or LA-1/LA-2 (F20, PO-X7).

**U-4 (no mixed partial sum).** `Selected_Sum (·, Both_Kinds)` is evaluated only at `Count = Rows'Length` (GT-01,
GT-07, GT-16, GT-43); LA-10 is called only with `Held_Only` or `Budget_Only` (GT-12, GT-45).

**U-5 (no negative multiple).** No `Hi·P` with `Hi < 0` is formed (GT-47; Lemma S′).

**U-6 (bounded intermediates).** Every Big_Integer intermediate is a W value, a sum of nonnegative terms with a W
total, or an L value (GT-01..GT-50).

Review checklist:

1. H0 for the final `Conserved`, `Contained` and `Check` bodies (no new evaluation order).
2. GT-01..GT-50 against the final source text, one by one, including lemma bodies and every intermediate assertion,
   with the stated span classes and bounds; nothing in the final text left out of the inventory.
3. U-1..U-6.
4. G1c for the pinned `Compare` body (GT-08, GT-50).
5. The twelve rows of B.7.1 and B.7.2 as the only sign cases, each lemma body asserting its row, (D) and residual as
   written.
6. Observation in the checks build: RL-24, RL-25 (z, n), RL-25E (z, n) and RL-26 complete with their expected results;
   W-11a fails on an input where the original also fails, and its location is recorded.

## B.11 Why the same argument fails for A-COL (R-F38)

A-COL's state after columns `0..c−1` encodes the truncated sums `D(c)`. Any Big_Integer statement of its column
relation forms `D(c)` or a one-sided part of it (DESIGN.md §5.15, F38). Neither is in W, and Lemma S cannot bound them
by a W value: in RL-26 the truncated sum at `c = 802` is `65537·(256**802 − 1) > 2**6432` [K-219], and even the carry
difference times `256**802` equals `2**6432` [K-243, K-244, K-245]. In addition, A-COL's LA-7 uses LA-10 with
`Both_Kinds`, which forms the mixed partial sums excluded by U-4. So A-COL violates DR-C6, and F35 stays OPEN for it.
V5-RC1 is applied to A-COL's LA-9 anyway (PO-A34), so A-COL no longer evaluates a Budget usage.

## B.12 The adversarial pass (desk enumeration, this session)

For each family of originally successful direct-Ada inputs below, every construct GT-01..GT-50 was checked against the
spans it evaluates. "Original" lists the spans orig(f, x) evaluates with `Exact_Value` (and so `Q.Value`) at that call.

| AP | Input family (worst case) | E | Spans D1-A evaluates | Original evaluates them? | Result |
|---|---|---|---|---|---|
| AP-1 | RL-25: Budget child, valid 804-byte usage, amounts [05]/[01] | 1 | T, A of C; never C's usage (GT-03, GT-08, GT-10, GT-11, GT-12) | yes; neither evaluates the usage | no extra span |
| AP-2 | RL-25E: as AP-1 with Length-0 amounts | 0 | LA-11: T and A (Length 0) via LR-0; `Amount_Reference (C)` short-circuits on the kind | yes | no extra span |
| AP-3 | Budget selected row with an invalid usage of `Length = Byte_Count'Last` | ≥ 0 | never the usage | not evaluated by either | no extra span |
| AP-4 | Held selected row, usage absent | ≥ 0 | A only (`Present` short-circuits GT-08, GT-10, `Amount_Reference`) | yes | no extra span |
| AP-5 | Held selected row, valid usage of `L ≤ 803`, greater / equal / lower than the amount, signed (RL-7a, RL-7d, RL-7e, RL-12S, RL-12M) | ≥ 1 | A, U (GT-08, GT-10, GT-11, GT-12, GT-22..GT-24 when U is the operand) | yes: `Amount` evaluates both `Exact_Value`s for a counted Held row with usage present | no extra span |
| AP-6 | Held selected row, invalid usage (RL-12, RL-12N, RL-12V, RL-12I, RL-12IN) | ≥ 0 | U (value 0; `Normalized (U) = Empty_Quantity`) | yes: `Exact_Value (U)` returns 0 at `:24` and its Post evaluates `Q.Value (U)` | no extra span; `Empty_Quantity` forms only 0 |
| AP-7 | a Held row with a valid 804-byte usage that is not selected for this target (parent mismatch, or `Released`) | as the selected rows | never this row's spans (`Selected` false: pre-pass, `Decide_Rows`, LA-10's `if Selected`, `Sum_Reference`'s `Included`) | not evaluated at this call | no extra span; if the row is selected at a later target, the original evaluates and fails there, and so does D1 (H0) |
| AP-8 | a non-selected row with a valid 804-byte amount | as above | never at this call; as its own target, T, which the original also evaluates | as D1 | no extra span |
| AP-9 | Length-0 amounts and target; `Rows'Length = 0` (RL-13, RL-15, RL-23) | 0 | LA-11 with LR-0 on Length-0 or invalid spans | yes | values 0 only |
| AP-10 | signed cancellation with 803-byte operands (RL-24, RL-26) | 803 | T, A; values are per-kind partial sums | yes | bounded by W |
| AP-11 | `Both_Kinds` with Held and Budget rows whose mixed partial sums `S_H (k) + S_B (k)` would exceed `2**6432` while every `S_K (k)` and S do not | ≥ 1 | per-kind accumulators only; `Selected_Sum (Both_Kinds)` only at N (U-4) | yes (per-kind `S_K (k)`, and S) | no mixed partial sum formed |
| AP-12 | invalid target with a huge Length | from the operands | T (value 0) | yes (`Exact_Value` returns 0; Post `Q.Value` = 0) | no extra span |
| AP-13 | negative-zero target; negative operands driving `Hi = −1` and `Hi ≤ −2` | ≥ 1 | T, A; `Compare_To_Target` treats negative zero as nonnegative (`Neg` false) | yes | L values `≤ 2·P` |
| AP-14 | duplicate identities (RL-12N, RL-14P, RL-18) | ≥ 0 | selection uses `Same` on identities (no Big_Integer) | — | no extra span |
| AP-15 | `Data'First = 17`, `Rows'First = 5` | any | indices `Rows'First + Count`; accumulators 1-based | — | no extra span |
| AP-16 | `Check` path (capacity branch; `Conserved` after `Shape`) | ≤ 803 | C spans (GT-48); `Conserved` as above | yes (`Shape`, the capacity expression) | bounded by `3·256**803` |
| AP-17 | a selected Held row with a valid 804-byte amount or usage (W-11a) | 804 | the operand | the original evaluates it and fails | not originally successful; outside H-A's hypothesis |
| AP-18 | a selected Held row with a valid 803-byte usage not greater than its amount | 803 | U through GT-08, GT-10, GT-11 | yes | no extra span |

**Result.** On every originally successful input family enumerated, no D1-A construct passes to a Big_Integer-forming
function a `Data` span that the original does not evaluate at the same call. The only spans D1-A uses that the original
does not are `Empty_Quantity` (Length 0; it forms only 0 and `P(0) = 1`) and D1-A's own accumulator arrays (values
below `256**E`); both are bounded as stated in U-1. This is a desk enumeration over the design text by the author, not
an execution, not a proof, and not an independent review.

## B.13 Non-claims

- This argument is lead reasoning. It is not a proof, not an independent review and not an observation.
- It does not bound time, heap or stack (O-COST-MEASURE, O-WORKSPACE-A); the checked `Compare` term and the release
  per-row `E` factor (F42) are cost changes, not horizon issues.
- It assumes the functional-correctness obligations listed in B.2; if any of them fails, the argument must be redone.
- It makes no claim about A-COL beyond B.11.
