# Appendix B to D1 DESIGN v5: Theorem H-A, the A-ROW horizon argument (R-F35)

Status: **[LEAD] design-level argument, unreviewed and unproved.** It is the "complete horizon argument" that ruling
R-F35 asks for. It closes nothing by itself. Closure of F35 for A-ROW still needs an independent review of this
argument, the proofs PO-A27..PO-A33, the DR-C6 review of the final source text (PO-A32), and observation of RL-24,
RL-25 and RL-26 in the checks build (DESIGN.md §12.3). For the column engine A-COL, F35 stays OPEN (B.9).

Arithmetic facts are JACKAL results, cited by their DESIGN.md §15 identifiers. Code references are to DESIGN.md
§5.12-§5.13 (A-ROW), §5.3 (helpers), §5.6 (shared lemmas), §5.7 (`Pair_Sum_Order`) and §5.8 (callers). Bare `core/…`
paths are the C5 source tree (DESIGN.md §2).

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
  `Effective_Length` over the target, every selected amount and the usage of every selected Held row with usage
  present; V4-RC1), `P = 256**E`, `S_K (k)` the original's partial sum `Sum_Reference (Data, Rows, k, Parent, K)` for
  kind `K`, `S` the selected total (`S_K (N)` for one kind; `S_H (N) + S_B (N)` for `Both_Kinds`), and `v_t` the
  target's value.

## B.2 Statement

**Theorem H-A.** For every `f` in {`Conserved`, `Contained`, `Check`} and every x: if orig(f, x) succeeds, then every
value formed by D1(f, x) is representable.

**Hypotheses on D1 itself (each an open proof obligation).** The argument uses the functional correctness of A-ROW and
of `Pair_Sum_Order` as designed: the loop invariants and Posts of DESIGN.md §5.12-§5.13 hold whenever evaluated
(PO-A27..PO-A31, PO-A17, PO-A21). It is therefore a statement about the design that is to be proved, not about a
partial implementation. It also uses DR-C6 as a property of the final text (PO-A32).

## B.3 H0: alignment of reached calls

**Claim.** D1(f, x) evaluates a `Selected_Sum_Order` call with arguments (Parent, Mode, Target) only if orig(f, x)
evaluates the corresponding original expression, and the corresponding pairs are:

| D1 call site (DESIGN.md §5.7-§5.8) | Original expression (C5) |
|---|---|
| `Conserved`: `Selected_Sum_Order (…, (Present => False), Held_Only, State.Held_Total) = Equal` | `Exact_Value (State.Held_Total) = Sum (…, Held_Capacity)` (`core/resource_run_ledger.adb`, `Conserved`) |
| `Conserved`: `… Budget_Only, State.Charged_Total) = Equal` | `Exact_Value (State.Charged_Total) = Sum (…, Irreversible_Budget)` |
| `Contained` loop 2, iteration I: `… Rows (I).Bound.Reservation, Both_Kinds, Rows (I).Amount) = Greater` | `Sum (…, Held) + Sum (…, Budget) > Exact_Value (Rows (I).Amount)` (`:85-86`) |
| `Check` capacity branch: `Pair_Sum_Order (Held_Total, Charged_Total, Capacity) = Greater` | the original capacity condition (`:173-174`) |

**Argument.** The D1 bodies keep the original control structure: the same short-circuit conjunctions in `Conserved`,
the same loop 1 and loop-2 invariant in `Contained`, and the same branch order in `Check` (DESIGN.md §4.1, §5.8). Each
replaced test returns the same Boolean as the original test (PO-A15, PO-A16, PO-A17, PO-A20). By induction over the
evaluation order, both evaluations reach the same sequence of call sites with the same arguments. In Ada both operands
of `=`, `+` and `>` are evaluated before the operator, so when orig(f, x) succeeds it has evaluated both sides of every
reached original expression.

Every other construct of D1(f, x) (loop 1, the loop-2 invariant, `Shape`, the public Posts, every other `Check`
branch) is byte-identical to the original and evaluated identically, so its formed values are formed by orig(f, x).

## B.4 H1: the original's formed set W

For one reached call, orig(f, x) forms at least the following, by source [OBS `core/resource_run_ledger.adb:19-90`,
`.ads:185-213`; F39]:

| Member of W | Formed by |
|---|---|
| `S_K (k)` for every k in `0 .. N` and each kind `K` that the original sums at that site | `Sum`'s loop invariant `Result = Sum_Reference (Data, Rows, Count, Parent, Kind)` at every iteration (`:49-64`), and its recursive evaluation, which forms every shorter prefix |
| `Amount_Reference (row)` and `Q.Value` of each candidate span of every included row: the amount; and the usage of a Held row with usage present | `Amount`'s body (`Exact_Value` of the amount, and of the usage under `Item.Kind = Held_Capacity`, `:36-48`) and its Post `Amount_Reference` |
| `256**L` for every valid candidate span of Length L above | `Exact_Value`'s body: `Place := Place * 256` at every digit (`:19-34`), so `Place` reaches `256**L` |
| the selected total `S` | `Sum`'s Post (one kind), or `Sum (Held) + Sum (Budget)` in `Contained` (`:85-86`) |
| `v_t` and `256**L_t` when the target span is valid with Length `L_t` | `Exact_Value (target)` |
| for `Check`'s capacity branch: the values of the three totals and `Value (Held) + Value (Charged)` | the original capacity expression and the public Post's `Decision_Reference` |

**Lemma W1.** If orig(f, x) succeeds, then for every reached call: every valid candidate span of an included row and the
target have Length at most 803, so `E ≤ 803`, `P ≤ 256**803 = 2**6424` [K-188], `2·P < 2**6432` [K-226] and
`3·256**803 < 2**6432` [K-248].

*Proof.* A valid span of Length `L ≥ 804` makes `Exact_Value` form `256**L ≥ 256**804 = 2**6432` [K-65], which is not
representable. `Effective_Length` is `Length` for a valid span and 0 otherwise (DESIGN.md §5.3). Selected rows are
exactly the included rows of the summed kinds (`Selected`'s definition; for `Both_Kinds`, the two-valued `Charge_Kind`
partition). The usage contributes to `E` only for a selected Held row with usage present (V4-RC1), which is exactly
when the original evaluates its `Exact_Value`. ∎

Note what W does **not** contain: one-sided sums of magnitudes, truncated rows, and the mixed partial sums
`S_H (k) + S_B (k)` for `k < N`. The original forms none of them.

## B.5 The safe-form principle

**Lemma S (nonnegative sums).** If an expression is a left-associated sum `t_1 + … + t_m` of terms that are each
nonnegative, then every partial sum is at most the total. So if the total is representable, every intermediate of the
sum is representable, provided each term is.

**Lemma S′ (products).** For `Hi ≥ 0`, `0 ≤ LV < P` and `A = LV + Hi·P`: `0 ≤ Hi·P ≤ A`. For `Hi < 0` and
`A = LV + Hi·P`: `|A| = (P − LV) + (−Hi − 1)·P` with both terms nonnegative, `P − LV ≤ P` and `(−Hi − 1)·P ≤ |A|`.

**DR-C6 (the rule for D1-A text).** Every Big_Integer equation or inequality in D1-A's ghost text is written so that
each side is a nonnegative-term sum (Lemma S) whose total is either a member of W (in magnitude) or at most `2·P`;
each product is `Hi·P` with `Hi ≥ 0` bounded by Lemma S′, or a digit times a power `d·P(i)` with `i < E`; no
difference of two large values is formed (a comparison or a case split is used instead); and no one-sided, truncated
or mixed partial sum appears.

`Acc_Value`'s two branches (DESIGN.md §5.12) are exactly Lemma S′: for `Hi ≥ 0` it forms `LV`, `Hi·P` and `A`; for
`Hi < 0` it forms `P − LV`, `(−Hi − 1)·P`, `|A|` and `−|A|`.

## B.6 H2: every value A-ROW forms, by class

Throughout, the call's `E ≤ 803` (Lemma W1). "≤ W" means "at most the magnitude of a member of W".

| Class | Constructs | Values formed | Bound |
|---|---|---|---|
| **G1a** spans the original also evaluates | LA-9N, LR-2's `Q.Value (Data, Op)`, `Usage_Selected`'s `Q.Compare` Post, LA-11's `Q.Value (Target)` | `Q.Value`, `Magnitude`, `Prefix_Value` of a candidate span of a selected row, or of the target | the same public functions on the same spans as orig: ≤ W, with internal powers at most `256**L ≤ 256**803` (`Prefix_Value_Worker`, `core/resource_quantities.adb:147-203`) |
| **G1b** never evaluated | a Budget row's usage; a Held row's usage when absent | nothing | V4-RC1: neither the extent, nor the length test, nor `Operand` reads it (`Usage_Selected` short-circuits on the kind and on `Present`, DESIGN.md §5.3) |
| **G1c** `Q.Compare`'s own checked body | the body of `Compare` on the normalized amount and usage of a selected Held row with usage present (`core/resource_quantities.adb:340-402`) | prefixes and powers up to the longer Length L; `Column_Bounds` and `Higher_Column_Order` values (`:41-92`) | at most `256**L ≤ 256**803` [LEAD on that source; the same bound is the reason §9.6 records no failure for RL-1's 803-byte `Compare`]. An invalid span is normalized to the empty quantity (value 0) |
| **G2** references | `Sum_Reference` per kind (row-loop invariants; LA-10 called with `Held_Only` or `Budget_Only` only), `Amount_Reference` (LR-2, LA-10), `Selected_Sum (N)` (Posts of `Decide_Rows`, `Selected_Sum_Order`, LA-11) | `S_K (k)`, `S`, `Amount_Reference` | members of W. `Selected_Sum (N)` for `Both_Kinds` is `S_H (N) + S_B (N)`: its operands and its result `S` are all members of W, and it is the only `+` in it |
| **G3** `Acc_Value` | invariants, `Add_Operand`/`Add_Accumulator` Posts, LR-4, LR-5 | `LV`, `Hi·P`, `P − LV`, `(−Hi − 1)·P`, `A`, `−abs A` | by the invariants `A` is `S_K (k)` (or `S` after `Add_Accumulator`), a member of W; intermediates ≤ `max (abs A, P)` (Lemma S′) |
| **G4** `Add_Operand`, `Add_Accumulator` | Posts; LR-3 (DR-C5 conditional form); LR-3P; LR-4 / LR-3A / LR-4A case proofs (B.7); loop prefix invariants | `LV (Low)`, `LV (Old_Low)`, `Pfx (Op, I)`, `P(I)` only when the carry or borrow out of cell I is 1, `A_before`, `A_after`, `v` | LR-3 sides total at most `2·P` [K-226 with W1]; LR-4 sides total `max (abs A_before, abs A_after, abs v)`, all members of W (B.7) |
| **G5** comparison with the target | `Compare_To_Target` (executable, no Big_Integer), LR-5 | `A = S`, `v_t`, `Hi·P` (`Hi ≥ 1`), `P + (P − LV)` (`Hi ≤ −2`), `LV + abs v_t` (`Hi = −1`), `LV` and `abs v_t` (`Hi = 0`) | `S, v_t` in W; the others at most `2·P` |
| **G6** prefixes and powers | `Low_Value` (`Prefix_Reference (Low, E)`), `Pfx (Op, I)` for `I ≤ E`, `P(I)` for `I ≤ E`, `Column_Bounds`-style lemma steps `256·P(I)` for `I < E` | — | at most `256**E ≤ 256**803` |
| **G7** integer conversions | `High_Big.To_Big_Integer (Hi)`, `(−Hi − 1)` | — | `abs Hi ≤ 2**64 − 1` [K-233] |
| **G8** `Pair_Sum_Order` (Check's capacity branch) | three-operand column engine (DESIGN.md §5.7), its Post `Value (First) + Value (Second)` against `Value (Target)` | per side at most three truncated magnitudes, carries at most 2 [K-17], powers at most `256**K` with `K ≤ 803` | the Post's values are the original's (W); the column ghost's values are below `3·256**803 < 2**6432` [K-248]. A side of three operands cannot carry a truncated sum beyond three terms, which is why the RL-26 mechanism (B.9) does not arise here |

`'Old` values (`Acc_Value (…)'Old`, `Old_Low`, `Old_Hi`) are copies of values already classified (G3, G4). The
row-loop's range invariants and the pre-pass are integer-only.

**Conclusion.** Every class is bounded by a member of W or by `2·P ≤ 2·256**803 < 2**6432` [K-226], or by
`3·256**803 < 2**6432` [K-248]. By Lemma W1 all members of W are representable when orig(f, x) succeeds. Hence every
value formed by D1(f, x) is representable. ∎

## B.7 LR-4: the sign cases in safe form

Notation: before the step `A_0 = LV_0 + Hi_0·P`, the operand `v` (`|v| < P`, LR-3P), after the step
`A_1 = LV_1 + Hi_1·P = A_0 + v`, with `Hi_1 − Hi_0 = c ∈ {−1, 0, 1}` (K-224, K-225). Each row states the equation
the lemma body asserts. Every side is a nonnegative-term sum (Lemma S) whose total is the largest of `|A_0|`, `|A_1|`,
`|v|`, all members of W (`A_0`, `A_1` are per-kind partial sums or `S`; `v` is an `Amount_Reference`).

| Signs | Asserted equation (all terms nonnegative) | Side total |
|---|---|---|
| `A_0 ≥ 0`, `v ≥ 0` (then `A_1 ≥ 0`) | `LV_0 + Hi_0·P + v = LV_1 + Hi_1·P` | `A_1` |
| `A_0 ≥ 0`, `v < 0`, `A_1 ≥ 0` | `LV_1 + Hi_1·P + abs v = LV_0 + Hi_0·P` | `A_0` |
| `A_0 ≥ 0`, `v < 0`, `A_1 < 0` | `LV_0 + Hi_0·P + (P − LV_1) + (−Hi_1 − 1)·P = abs v` | `abs v` |
| `A_0 < 0`, `v ≥ 0`, `A_1 ≥ 0` | `(P − LV_0) + (−Hi_0 − 1)·P + LV_1 + Hi_1·P = v` | `v` |
| `A_0 < 0`, `v ≥ 0`, `A_1 < 0` | `(P − LV_1) + (−Hi_1 − 1)·P + v = (P − LV_0) + (−Hi_0 − 1)·P` | `abs A_0` |
| `A_0 < 0`, `v < 0` (then `A_1 < 0`) | `(P − LV_0) + (−Hi_0 − 1)·P + abs v = (P − LV_1) + (−Hi_1 − 1)·P` | `abs A_1` |

Each row follows from LR-3 (low parts, sides at most `2·P`) by adding the same nonnegative multiple of `P` to both
sides; the multiple is `Hi_0·P`, `Hi_1·P` or `(−Hi − 1)·P`, each at most a side total by Lemma S′. The sign of `A`
equals the sign of `Hi` (`Hi ≥ 0` iff `A ≥ 0`, because `0 ≤ LV < P`), so the case split is on integers only. LR-3A and
LR-4A (`Add_Accumulator`) are the same table with `v` replaced by `A_B = S_B (N)` and `A_1 = S`.

## B.8 Coverage of the exhibits

| Exhibit | Original's values | A-ROW's values | Result |
|---|---|---|---|
| RL-24 (F35): 514 children `±X`, `X = 2**6424 − 1` [K-184, K-188] | per-kind partial sums alternate `X` and 0 [K-186, K-187]; every value at most `256**803` | `A` alternates `X` and 0; `E = 803`; G4 sides at most `X` or `2·P` | no value reaches `2**6432`; expected False in every build |
| RL-25 (F37/N1): Budget child, 804-byte usage | the usage is never evaluated (`Amount`'s kind test) | the usage is never evaluated (G1b); `E = 1` | expected True in every build; no checked failure |
| RL-26 (F38): 65537 pairs `+X, −Y` [K-215..K-223] | the partial sums run `X`, −1, `X − 1`, −2, … (each pair sums to −1 [K-216]); every magnitude is at most `X < 2**6424` [K-223] | `A` takes the same values; `E = 803`; no truncated sum is formed | no value reaches `2**6432`; expected False in every build (checks-build cost OPEN) |
| Direct-Ada operand of 804 bytes | orig fails (`Exact_Value`, `Place` reaches `256**804`) | D1 may fail too (G1a at `core/resource_quantities.adb:181`) | consistent with H-A: the hypothesis does not hold |

## B.9 Why the same argument fails for A-COL

A-COL's state after columns `0..c−1` encodes the truncated sums `D(c)`. Any Big_Integer statement of its column
relation forms `D(c)` or a one-sided part of it (DESIGN.md §5.15, F38). Neither is in W, and Lemma S cannot bound them
by a member of W: in RL-26 the truncated sum at `c = 802` is `65537·(256**802 − 1) > 2**6432` [K-219], and even the
carry difference times `256**802` equals `2**6432` [K-243, K-244, K-245]. In addition, A-COL's LA-7 uses LA-10 with
`Both_Kinds`, which forms the mixed partial sums excluded in B.4. So A-COL violates DR-C6, and F35 stays OPEN for it.

## B.10 What review must check (PO-A32)

1. That B.3's alignment holds for the final `Conserved`, `Contained` and `Check` bodies (no new evaluation order).
2. That every Big_Integer expression in the final D1-A text, including lemma bodies and every intermediate assertion,
   falls in one of G1a..G8 with the stated bound, and is written in DR-C6 form.
3. That LA-10 is never called with `Both_Kinds` by A-ROW, and that no A-ROW text names `Side_Total`, `Side_Sum`,
   `Truncated` or a mixed partial sum.
4. That G1c holds for the pinned `Compare` body.
5. That the six rows of B.7 are the only sign cases and each lemma body asserts its row as written.
6. Observation in the checks build: RL-24, RL-25 (both variants) and RL-26 complete with their expected results, and
   W-11a records its failure at the location the original also fails.

## B.11 Non-claims

- This argument is lead reasoning. It is not a proof, not an independent review and not an observation.
- It does not bound time, heap or stack (O-COST-MEASURE, O-WORKSPACE-A); RL-26 is expensive in the checks build for
  the original and D1 alike.
- It assumes the functional correctness obligations listed in B.2; if any of them fails, the argument must be redone.
- It makes no claim about A-COL beyond B.9.
