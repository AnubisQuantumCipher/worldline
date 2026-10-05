# WORLDLINE Phase One native Big_Integer D1 DESIGN v5: independent design review

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES**

- Reviewer: an independent Claude Code review subagent (claude-opus-5-5) with a fresh context. I am not a GPT model. I authored nothing under review and I am not the drafting agent.
- Author: Claude Code lead claude-opus-5-5, through a drafting subagent.
- This review grants no acceptance: proof_acceptance=false, phase_acceptance=false, source_acceptance=false, native_acceptance=false.
- It selects no operator option and adds or lowers no approval gate.

**Headline.** Theorem H-A, as v5 writes it, is **false**. The design's own control RL-25 is a counterexample, and so is a zero-extent variant of it (RL-25E). A-ROW's ghost text still evaluates `Q.Value` on a selected Budget row's usage span, which the original never evaluates. That is the F37/N1 class again, now in a lemma rather than in the extent.

The A-ROW architecture itself survives adversarial checking: per-kind row-order accumulation, the set W, Lemmas S/S′ and the B.7 sign table hold up. The defects are local and lead-owned, and they can be repaired without any Pre, cap, domain restriction or refusal.

As a result:
- F35 is **not** closed at design level for A-ROW in v5.
- O-GHOST-HORIZON-A stays OPEN and BLOCKING.
- V4-RC1 is NOT_CLOSED.

## 0. Inputs, identities, method and process disclosures

### Identities

| Item | sha256 |
|---|---|
| Overrides file (read first) | `bdb0815da741d72468c05087cb7a4136445cba26c533e69e24dee03935530b00` |
| Brief `WT/briefs/d1-design-v5.md` (62 lines, read in full) | **`92db0bef949a16b2a99a9ab5c0bea23c320a39c58adf3e126e34b622596cffd8`** |

Package hashes (all six match the brief) [OBS `sha256sum`]:

| File | sha256 |
|---|---|
| DESIGN.md | `5994b243…a11ebd` |
| APPENDIX-A | `11cad97d…f07d98` |
| APPENDIX-B | `b588941d…71fc4` |
| jackal.json | `edbdc9de…f99195` |
| decisions.json | `fd470295…c70396` |
| AUTHOR-NOTES.md | `be43d1b9…4ae12` |

Closure target `D4/review/claude-v1`: REVIEW.md `a81c41f6…c411` and review.json `a5a26a90…b652` match the brief. Both were read in full.

C5 source hashes I recomputed match DESIGN.md:158-167 for every file I read. These were:
- `core/resource_quantities.ad?`
- `core/resource_run_ledger.ad?`
- `core/resource_reservation_transition.ad?`
- `core/evaluation_finalization_c.adb`
- `native/build_guard.py`

### Roots

| Root | Path |
|---|---|
| W | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow` |
| WT | `W/work/claude-lead-isolation-v1/wt-1` |
| D5 | `WT/designs/claude-native-bigint-d1-design-v5` |
| D4 | `WT/designs/claude-native-bigint-d1-design-v4` |
| C5 | `W/work/claude-composition-v5-beta/source` |
| RT | `…/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude` |

Bare `DESIGN.md` and `APPENDIX-B` mean the D5 files.

### Method

- Passive reading and hashing only.
- I ran no compiler, prover, build, test, WORLDLINE code, systemctl, project-vault or restic. I imported nothing from WORLDLINE.
- All eight Ada skills were loaded with the Skill tool before any Ada reading.
- I made 46 JACKAL calls (J1-J46 in checks.json), sequentially or in groups of at most four.
  - Every call returned `status=exact`, `formal=false`, `lane=rat`, evaluator `4c0ae28d…5d872`.
  - Verbatim non_claims: "NOT formal-bounded: this lane carries no Lean-checked certificate"; "The epistemic class above is the STRONGEST claim this result supports"; "exact rational arithmetic (not yet checker-covered)".
  - No consequence ceiling was declared, so every result is informational about code.
  - No refusal occurred.
  - `exact` is outside the Lean certificate chain; it is not `formal-bounded`.
- I re-ran all 38 relied-on and non-relied-on v5 values K-213..K-250 (J1-J38). **Every one reproduces** the `parsed=`/`exact=` of jackal.json:29-66 and DESIGN.md:3313-3350, including the leading and trailing digits of the large summaries.

### Process disclosures

- I wrote no file.
- I ran read-only Python, fed through a shell heredoc that terminates, to diff v4 and v5 sections and to read decisions.json keys. It did not wait on stdin.
- I did not consult SIA and wrote no SIA note.
- I did not read review-records/, D4/review/gpt61-*, any v5 review directory or any transcript.

### What I read in full

- DESIGN.md §0-§5 (:1-1474), §7.8-§9.7 (:2018-2438), §12-§14 (:2722-3038), §15.2-§16 (:3309-3377), §11.3 (:2531-2575) and R-OVR (:2636-2665).
- §6, §7.1-§7.7, §10 and §11 were compared section by section with v4. The only changes are editorial or the V4-RC2 (f)/(g) edits; R-DRC5's §6 is substantively unchanged.
- The full Appendix B, AUTHOR-NOTES and jackal.json.
- The relevant C5 and RT source.

## 1. Closure of V4-RC1 and V4-RC2

### V4-RC1 (R-EXTENT): NOT_CLOSED

| Part | Disposition | Evidence |
|---|---|---|
| (1) Held-only usage in pre-pass and length test | CLOSED (text) | A-COL DESIGN.md:728-739, 755-757; A-ROW :1212-1222 |
| (2) LA-7 Pre, LA-11, `Lemma_Close`, PO-A14 | CLOSED for the named sites, but **the restriction is incomplete** (F40, F41 below) | :899-905, 937-946, 2084 |
| (3) §5.5 and §5.11 horizon text | CORRECTED, but §5.11:1122-1123 ("every span that sets `Columns` is evaluated by the original") is still incomplete, because LA-9 evaluates Budget usage | :819-825, 1119-1139 |
| (4) §9.1, §9.2, §9.6 rows | rows present; **the v5 claims in them are false** | :2161, 2176, 2414 |
| (5) RL-25 (z, n), True in every build | control well-formed and expectation correct against the original; **the design as written fails it** in the post-D1 checks build (§3) | :2871 |
| (6) RL-25C | DESIGNED; one sizing error (V5-RC4 c) | :2872 |
| (7) F37 recorded; decisions.json | DESIGNED, but `f35_outcome.exhibits.RL-25 = "completes; usage never evaluated"` (decisions.json:76) is false | :409-422 |

R-EXTENT required the Held-only restriction so that D1 never evaluates a non-operand Budget usage span. v5 restricts the extent but still evaluates such a span in LA-9N and LA-9, and through LA-11's body. So V4-RC1 is not closed in substance.

### V4-RC2

| Item | Disposition | Evidence |
|---|---|---|
| (a) F32 restated | CLOSED | DESIGN.md:367-392. Spot-checked: `Decide_Mixed` returns `Decision` only from `CW.Decide_Wire`, else `Invalid_Request` (C5 `core/evaluation_finalization_c.adb:485-508`) |
| (b) O-GHOST-EXTENT-A | CLOSED (listed) | :3024; decisions.json:143. It cites **PO-A34**, which is never defined (V5-RC5) |
| (c) W-0 calibration; W-5/W-7 ordinals from W-0 | CLOSED | :2938, 2943, 2945, 2394-2399 |
| (d) IM-10 targeted, unique quartet | CLOSED | :2897 |
| (e) RL-12IN reworded | CLOSED | :2854. Checked: M-FALLBACK yields Σ = −raw ≤ −1 ≤ v_t = −1 (whole True); a compare-first raw reader keeps the amount (0) and is caught by RL-12I |
| (f) R-OVR pre-scan conditions | CLOSED | :2645-2659 (type-level `int` operations; no `default`/`cls`; PY-9/PY-13 extended :2923, 2927) |
| (g) C12 inventory | CLOSED | :2549. Checked against C5 `native/build_guard.py:1-55` and PY `subprocess.py:132-155, 1996-2003`: `abs returncode ≤ 255` (J28 745, J29 637); item 5 (J37 7852516352, J38 630) |
| (h) `/tmp` record | CLOSED | :174-177; AUTHOR-NOTES.md:36-38 |

### Rulings carried

These are preserved:
- R-DRC5: §6 unchanged (diff).
- R-F35: no Pre, cap or refusal is introduced (:1138, 3374-3375).
- R-F32: :390-392.
- R-OD2-DEPTH: :2636-2638; §11.6.
- R-CARRY: :82.

v4-review CLOSED items are not regressed.

## 2. Theorem H-A: what holds

I checked these parts adversarially against the source.

**F1, the representation limit.** RT `s-genbig.adb:1176, 1190-1191` (`Bignum_Limit = 200`) and RT `s-shabig.ads:52` (`SD is Unsigned_32`) give at most 201 32-bit limbs, so values must be below `2**6432`. J39 gives `256^804 − 2^6432 = 0`.

**Lemma W1 holds.**
- Every valid span the original passes to `Exact_Value` forms `Place = 256**L` regardless of its digits (C5 `core/resource_run_ledger.adb:19-34`, :31).
- `Amount` evaluates the amount, and the usage only when `Kind = Held_Capacity` (:36-48).
- `Sum` evaluates `Amount` for every `Included` row (:49-64).
- So a successful original implies E ≤ 803.

**H0, alignment, holds.** It covers `Conserved`'s short-circuit (:65-69), `Contained` loops 1 and 2 with their early returns (:70-90), and `Check`'s branch order (:148-210).

**Set W is formed by the original.** The `Sum` invariant `Result = Sum_Reference (k)` (:56), the recursive references (`.ads:200-209`), `Sum (Held) + Sum (Budget)` (:85-86) and `Decision_Reference`'s capacity sum (`.ads:406-407`).

**Lemmas S and S′, `Acc_Value`'s two branches (DESIGN.md:1180-1185), and the six B.7 rows** are correct identities. I checked each row as `|A_0| ± |v| = |A_1|` by sign case.

**G1c holds.** `Compare`'s checked body on spans of Length ≤ L forms at most `256**L`:
- `Prefix_Value_Worker`'s final `Place` (C5 `core/resource_quantities.adb:181`);
- `Prefix_Bounds`/`Column_Bounds` at `256·P(o−1)` with o ≤ L−1 (:230-257, 41-64);
- `Higher_Column_Order` below `P(o+1)` (:66-92).

**G8 holds.** Pair_Sum_Order is below `3·256**803` (J36), with carry ≤ 2.

**LA-10 per kind (DESIGN.md:1280-1285, 1371) is sound.**
- Selected rows of the H accumulator under `Both_Kinds` are exactly `Included (Held)`, through the two-valued `Charge_Kind` partition (C5 `.ads:36, 195-199`).
- The invariants (:1289-1295) then form only `S_H (k)` and `S_B (k)`, both in W at `Contained`.
- The cost coefficient `3·N·n_s + 6·n_s` (J34, J35) is a consistent upper bound of the stated terms (:2335-2346).

**Checks-path masking holds as v5 claims.** `Shape` evaluates `Value` of every row's amount and usage, whatever the kind (`Row_Valid`, C5 `.ads:151-153`; `Nonnegative_Valid` Post `Value (Data, Q) >= 0`, `core/resource_reservation_transition.ads:135-138`). On `Conserved`/`Check` a Budget usage of 804 or more bytes therefore already fails the original.

## 3. Finding F40 (new; proposed): A-ROW's LA-9N, and LA-9, still evaluate a selected Budget row's usage

### The defect

- `Decide_Rows` calls `Lemma_Operand_Values (Data, Rows (J))` (LA-9N) for **every selected row**, including Budget rows (DESIGN.md:1270-1272).
- LA-9N is defined as "for the amount and, **when present**, the usage of `Item` (LA-9's first three conjuncts …)" (:1364).
- LA-9's third conjunct is `(if Item.Observed_Usage.Present then Q.Value (Data, Normalized (Data, Item.Observed_Usage.Value)) = Q.Value (Data, Item.Observed_Usage.Value))` (:919-921). It is guarded by `Present` only, not by `Kind`.
- The checks build executes it.
- `Q.Value` on a valid span calls `Magnitude`, then `Prefix_Value (L)`, then `Prefix_Value_Worker`, whose `Place := 256 * Previous_Place` (C5 `core/resource_quantities.adb:181`; `.ads:92-96`; `.adb:210-226`) forms `256**804 = 2**6432` (J39) at L = 804. That value is not representable (F1).

### Counterexample: RL-25 itself (DESIGN.md:2871)

**Original, both builds: True.**
- Loop 1: P supports C.
- Target `p`: `1 − 5 = −4` (J1).
- Target `c`: `0 − 1 = −1` (J2).
- `Amount`/`Amount_Reference` never touch a Budget usage (C5 `.adb:36-48`, `.ads:187-192`).
- `Contained` has no `Shape` (`.adb:70-90`).

**v5 A-ROW, checks build:** target `p` gives E = 1 and C is selected (Budget, parent `p`). LA-9N's Post then evaluates `Q.Value` on C's valid 804-byte usage and raises `Storage_Error` at `resource_quantities.adb:181` (XA3), so `Contained` raises. This is a D1-introduced checked failure on an originally successful direct-Ada input. Both RL-25z and RL-25n fail, because `Place` grows regardless of digit values.

### What this falsifies

- APPENDIX-B:122-123: G1a lists LA-9N as evaluating only "spans the original also evaluates"; G1b claims a Budget usage is "never evaluated".
- APPENDIX-B:166 (B.8 RL-25 row).
- DESIGN.md:1415-1416, 1424-1426, 2176, 2414; decisions.json:76.
- A-COL inherits the same defect, because LA-7 uses LA-9 per row (DESIGN.md:986). So "REPAIRED in both engines" (:98; decisions.json:97) is false for A-COL too.
- §12.7 maps "Budget ignored: RL-25" to proof by "LA-9, LA-9N" (:2957). Those are the lemmas that break it.

### Repair (lead-owned, contract-preserving)

Guard the usage conjunct of LA-9N and LA-9 with `Usage_Candidate (Item)` (:612-614). LR-2 needs it only for Held usage rows; for a Budget row, `Operand` is the amount (:597-598).

## 4. Finding F41 (new; proposed): A-ROW's zero-extent path imports A-COL's LA-7

### The defect

- A-ROW calls LA-11 when E = 0 (DESIGN.md:1224-1226). The A-ROW lemma table says only "LA-11 | E = 0 (§5.6) | as before" (:1372).
- The only LA-11 body plan is "LA-7 and LA-8 at `Columns = 0`" (:996). §5.6 assigns LA-11 to A-COL (:851), and PO-A11 is A-COL-only (:2069, 2082).

LA-7's body (:986-990) does three things:
- it states its Post through `Side_Sum` (:906-908), A-COL's recursive function;
- it calls LA-10 with the caller's `Mode`, so `Both_Kinds` forms the mixed partial sums that DR-C6 excludes;
- it calls the unguarded LA-9.

### Consequences

These contradict:
- F20 and PO-X7 "A-ROW adds no recursive function" (:312, 2062, 3020);
- APPENDIX-B:183-184 (B.10 item 3);
- the claim that F38's mixed-sum hazard is avoided (:1445-1447).

### Counterexample RL-25E

- P: Budget, reservation `p`, parent absent, Amount (+, Length 0).
- C: Budget, reservation `c`, parent `p`, Amount (+, Length 0), usage a valid 804-byte span.

The original returns True: target `p` gives `(0 + 0) − 0 = 0 ≤ 0` (J46); target `c` gives 0 ≤ 0.

v5 A-ROW: target `p` has E = 0, because the usage is excluded from E. LA-11 then runs LA-7, LA-7 runs LA-9 on C, and `Q.Value` forms `2**6432`, which fails. The mixed partial sums are numerically 0 at E = 0, so they are a rule violation, not a horizon failure. The LA-9 path is a horizon failure.

## 5. Other findings

### F42 (new; cost statement)

§9.3.7 says A-ROW's "leading terms are of the same order, so its checked cost is within a constant factor of the original's own checked evaluation of the same call" (DESIGN.md:2348-2352). That is not true as a function of L.

- Each selected Held usage row costs one executable `Usage_Selected → Q.Compare` (:591-595), checked at `(8L + 42)·PV(L) + Q(L)` PRI (:2229).
- The original's per-row work is `20·PV(L)` (:2350, K-239 / J27).
- The ratio of the leading terms is `(8L + 42)/20`, which is `3233/10` at L = 803 (J44).
- The instance `454992179073696` (K-172) against `20·PV(803) = 1406689554160` (J40, J41) is `35413463502/109487045` (J42), and exceeds 300× (J43 = 32985312825696 > 0).

This is a D1-added checked cost, linear in L, that the original does not have. It must be stated and obligated (O-COST-MEASURE/D2). It is not a horizon issue. A-SEL-L remains an option and is not mandated.

**Release.** A-ROW's per-row cost is O(E) over the full low part (:1324-1327, 2159). When the target or one operand is long and the rest are short, that can exceed the original's per-row cost by a factor of up to E. On originally successful inputs E ≤ 803. §9.1 disclaims dominance (:2166) but does not state this case, and no control exercises it.

### V5-RC5 record items

- **PO-A34** is cited at DESIGN.md:2958, 3011, 3024 and decisions.json:55, 130, 143, but is not defined in §8.1 (:2071-2101).
- APPENDIX-B:187-188 says W-11a fails "at the location the original also fails". §9.6 gives different locations: the original at `resource_run_ledger.adb:31`, A-ROW at `resource_quantities.adb:181` (:2413, 2949). The text should say "on an input where the original also fails".
- B.7's derivation premise `Hi_1 − Hi_0 ∈ {−1,0,1}` (APPENDIX-B:142-143) does not hold for `Add_Accumulator`, where `Hi_H' = Hi_H + Hi_B + C` (:1339). The "same table" claim for LR-3A/LR-4A (APPENDIX-B:158-159) needs its own derivation. Its bounds still hold by Lemma S′.

## 6. A-ROW decision preservation, F38 and A-COL, controls, and the guarantee check

**Decision preservation.** Once proved, A-ROW preserves the original decision on every input. The Post (:704-709) is the reference comparison on `Selected_Sum` and `Value (Target)`. `= Equal` and `= Greater` map to the original tests (:1063-1067), with PO-A15/A16/A20/A21.

**F38 / A-COL.** Correctly carried OPEN and correctly not selected.
- K-215..K-223 and K-243..K-245 reproduce (J3-J11, J31-J33).
- At c = 802 the truncated sum `65537·(256^802 − 1)` exceeds `2^6432` (J7), while `65536` rows stay below it (J8 = 65536).
- The carry difference `65536·256^802 = 2^6432` (J32).
- "No ghost-only repair known" is scoped correctly as a lead claim (:1448-1453).

**Controls.**
- RL-24, RL-26 and RL-25 are well formed, and their reference expectations are correct against C5: RL-24 False, RL-26 False (J10 = −65537), RL-25 True.
- RL-25C is well formed with a positive calibration. But the Held series at `10**8` bytes needs `2E = 200000000` bytes under `Both_Kinds` (J45; :1229), not the stated `10**8`.
- W-0 is well formed. IM-10, RL-12IN and RL-12I are correct.

**Guarantee check.** I found no Pre, cap, domain restriction, refusal, suppressed Ghost, `Assume`, Off boundary, policy change, added gate or lowered floor.
- The original controls and public Posts stay byte-identical (:185-212, 2731).
- The A-ROW workspace's XA2 heap failure is a native obligation (O-WORKSPACE-A), never a refusal (:2027, 3019).
- The only guarantee breach is a defect: F40/F41 are a required success turned into a checked failure. They must be repaired, not accepted.

## 7. Required changes

### V5-RC1 (blocking; F40; completes V4-RC1/R-EXTENT)

- Guard the usage conjunct of LA-9N (:1364) and LA-9 (:919-921) with `Usage_Candidate (Item)`, in both engines.
- Correct DESIGN.md:98, 1415-1416, 1424-1426, 2176, 2414, 2957 and APPENDIX-B:122-123, 166.
- Correct decisions.json:76 and :97, and recount K-236's LA-9N term.
- Record F40.

### V5-RC2 (blocking; F41)

- Give A-ROW its own LA-11 body: iterative, per kind (LA-10 with `Held_Only`/`Budget_Only` only), using the guarded LA-9N and zero-extent padding facts, with no `Side_Sum`, `Side_Total`, LA-7 or `Both_Kinds` LA-10.
- Move LA-11 into A-ROW's PO set.
- Add the direct-Ada control RL-25E: expected True in every build, with E = 0 / XA0.
- Keep F20/PO-X7 "A-ROW adds no recursive function" true.

### V5-RC3 (blocking; H-A re-presentation)

- Re-state Appendix B.6 with a complete per-construct enumeration of A-ROW's final ghost text, including each conjunct of LA-9N and the new LA-11 body.
- Add to B.10: "every quantity span passed to a Big_Integer-forming function in D1-A is the target, a selected amount, or a `Usage_Candidate` usage".
- Give LR-3A/LR-4A their own derivation.
- Submit H-A for independent re-review. F35 stays OPEN until then.

### V5-RC4 (cost statements)

- **(a)** Replace §9.3.7's "within a constant factor" with the per-Held-usage-row checked `Compare` term `(8L+42)·PV(L) + Q(L)` against the original's `20·PV(L)`, obligated under O-COST-MEASURE/D2.
- **(b)** State in §9.1 the release case where A-ROW does O(E) work per short row, up to a factor E ≤ 803 over the original on originally successful inputs, and add a release timing control for it: many short rows with a long target or one long operand.
- **(c)** Fix RL-25C's workspace size to 2E.

### V5-RC5 (records)

- Define PO-A34 or remove every citation of it.
- Reword APPENDIX-B:187-188.
- Synchronize decisions.json.

## 8. Rulings

### R-H-A

Theorem H-A as written in v5 is false (RL-25 and RL-25E).
- F35/O-GHOST-HORIZON-A is NOT closed at design level for A-ROW, and remains BLOCKING for D1-A.
- The A-ROW architecture is endorsed as the candidate direction.
- No Pre, cap, domain restriction or refusal is eligible.
- Owner: lead.
- Evidence required: V5-RC1..RC3 text; independent re-review of the revised H-A; PO-A27..PO-A33 proved; RL-24, RL-25 (z, n), RL-25E and RL-26 completing in the checks build.

### R-EXTENT-2

The Held-only restriction applies to every D1-A construct that forms a Big_Integer value from a usage span, not only to the extent and the length test.
- Owner: lead.
- Evidence required: V5-RC1/RC2 text; RL-25 and RL-25E in both builds.

### R-F38

A-COL is correctly OPEN and correctly not selected. If it is ever revived, V5-RC1 applies to its LA-9.
- Owner: lead.
- Evidence required: a different reviewed horizon argument.

### R-COST-5

The `Compare` term and the release per-row E factor are stated cost changes, obligated under O-COST-MEASURE/D2. They are never acceptance, and no cap is permitted.
- Owner: lead.
- Evidence required: V5-RC4 text; measurements.

### R-CARRY-5

R-DRC5, R-F32, R-OD2-DEPTH, R-A, R-B, R-PREFIX, R-WORKSPACE, R-OD1, R-OD2, R-NOTICE and R-SCOPE stand unchanged.
- Owner: as in the v4 review.
- Evidence required: as in the v4 review.

## 9. OPEN obligations

- Every item of DESIGN.md:3011-3038 stays OPEN, including O-GHOST-HORIZON-A and O-GHOST-EXTENT-A.
- This review adds O-GHOST-EXTENT-A-LEMMA (F40/F41), open until V5-RC1/RC2 are implemented, proved and observed.
- The full strict proof floor (251), the ordered roster, the sole Off boundary, and all original and additive controls in both builds remain required.
- No finite control, JACKAL instance or this verdict substitutes for them.
