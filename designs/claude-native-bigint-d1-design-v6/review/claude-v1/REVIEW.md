# WORLDLINE Phase One native Big_Integer D1 DESIGN v6: independent design review

**Verdict: ENDORSED**

- Reviewer: an independent Claude Code review subagent (claude-opus-5-5), fresh context. I am not a GPT model. I authored nothing under review and I am not the drafting agent.
- Author: Claude Code lead claude-opus-5-5, through a drafting subagent.
- This review grants no acceptance: proof_acceptance=false, phase_acceptance=false, source_acceptance=false, native_acceptance=false. It selects no operator option and adds or lowers no approval gate.
- ENDORSED is a **design** verdict: the re-presented Theorem H-A is, at the design level, complete and correct, the two v5 counterexamples are eliminated, and no required change remains. It is **not** closure of F35 and **not** acceptance of the candidate. F35 / O-GHOST-HORIZON-A stays **OPEN and BLOCKING** for D1-A pending proof (PO-A27..PO-A33, PO-A35) and checks-build observation (RL-24, RL-25, RL-25E, RL-26); this review is only the design-level re-review R-H-A asks for.

## 0. Inputs, identities, method

### Identities (all [OBS] via `sha256sum`)
| Item | sha256 | Match |
|---|---|---|
| Overrides `scratchpad/review-override-v2.txt` (read FIRST, 13 lines) | `bdb0…`—n/a; read in full | — |
| Brief `WT/briefs/d1-design-v6.md` (69 lines, read in full) | **`3fa7c6e35c14ec609dd92b1f6ec209e1f9d223eaf4c764d2ed3ad363736d79d7`** | computed and reported |
| D6 `DESIGN.md` (353396 bytes) | `fc3e3a61…94e95` | matches brief |
| D6 `APPENDIX-A-python-conversion-surface.md` | `c0acdc6d…e01268` | matches brief |
| D6 `APPENDIX-B-arow-horizon.md` | `902ac1a9…504db4` | matches brief |
| D6 `jackal.json` | `61883be3…82c8a14` | matches brief |
| D6 `decisions.json` | `b0b3eb63…2c6c2c92c` | matches brief |
| D6 `AUTHOR-NOTES.md` | `0cf1d246…16db21b` | matches brief |
| D5 review `REVIEW.md` / `review.json` (closure target, read in full) | `38cb267e…d3ee96` / `26213c66…dfad5` | match brief |
| D4 review `REVIEW.md` / `review.json` (closure target, read in full) | `a81c41f6…ac411` / `a5a26a90…2fb652` | match brief |

Roots: `W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow`; `WT = W/work/claude-lead-isolation-v1/wt-1`; `D6/D5/D4 = WT/designs/claude-native-bigint-d1-design-v6/-v5/-v4`; `C5 = W/work/claude-composition-v5-beta/source`. Bare `core/…` paths are C5. Bare `DESIGN.md`/`Appendix B` are D6.

### Method
- Passive reading and hashing only. No compiler, prover, build, test, WORLDLINE code, systemctl, project-vault, restic; no WORLDLINE import; no SIA consultation or note; nothing read under `~/.local/share/sia/.gbrain/`; `/home/sicarii`, `~/iPad`, `~/iPadBackup` never listed or stat'd. All eight Ada skills loaded with the Skill tool before any Ada reading. No file written anywhere. No stdin-reading command; no backgrounded command; `command ls`/`os.listdir` used (override item 6).
- I read in full: the overrides, the brief, D6 `AUTHOR-NOTES.md`, `decisions.json`, `jackal.json`, `APPENDIX-B`; the sealed D5 and D4 `REVIEW.md` + `review.json`. I read D6 `DESIGN.md` §1 (:42-156), §3.4 (:361-488), §4 (:489-557), §5.2-§5.16 (:592-1848), §7.8-§9.3.7 (:2396-2749), §12.3/§12.6/§12.7 (:3243-3398), §14 (:3421-3454), §16 (:3795-3818), plus the header grep. I did **not** re-diff every line of the carried §6/§7.1-7.7/§10/§11/Appendix A against D5; I rely on the D5 review's closure of those and verified the changed sections directly (limit disclosed). I did not read `R5/raw-final-message.txt`, `review-records/`, any `gpt61-*` directory, or any transcript (override item 3).
- C5 source read independently: `core/resource_run_ledger.adb:19-95`, `core/resource_run_ledger.ads:180-270`.
- 23 JACKAL (`jackal_exact`) calls, in groups of ≤4, literal exponents. Every call: `status=exact`, `formal=false`, `lane=rat`, evaluator `4c0ae28d…5d872`, no consequence ceiling (informational about code), no refusal. Verbatim non_claims on every call: "NOT formal-bounded: this lane carries no Lean-checked certificate"; "The epistemic class above is the STRONGEST claim this result supports"; "exact rational arithmetic (not yet checker-covered)". `exact` is outside the Lean certificate chain; it is **not** `formal-bounded`. Details in checks.json.

## 1. Closure of V5-RC1..V5-RC5 (and preservation of v4/v5 closures)

**V5-RC1 (guard LA-9N and LA-9 usage conjunct with Usage_Candidate; corrections; record F40): CLOSED (design text).**
- `Usage_Candidate (Item) = (Item.Kind = Held_Capacity and then Item.Observed_Usage.Present)` (DESIGN.md:669-671).
- LA-9N (`Lemma_Operand_Values`) usage conjunct is guarded `if Usage_Candidate (Item)` (DESIGN.md:1566-1568). A-COL's LA-9 (`Lemma_Operand`) likewise (DESIGN.md:977-979); its 4th conjunct's `Q.Value(usage)` is additionally short-circuited behind `Kind = Held_Capacity and then Present` (DESIGN.md:980-982, 1022-1025).
- Corrections present: §3.4 F37/F40 (:426-470), §5.14 (:1759-1806), §9.2 (:2558), §9.6 row, §12.7 "Budget usage ignored" (:3370), Appendix B.6 GT-08/GT-10/GT-11/GT-12, B.8, B.9; decisions.json `f35_outcome.exhibits.RL-25` and F37; K-236 recount (§9.3.7:2722-2723, K-252/K-253). F40 recorded (§3.4:460-470).

**V5-RC2 (A-ROW own iterative per-kind LA-11 body; move to PO set; RL-25E; keep F20/PO-X7): CLOSED (design text).**
- LA-11 (`Lemma_Zero_Extent`) has a v6 body (DESIGN.md:1590-1615): `Lemma_Zero_Length_Value` (LR-0, :1572-1576) on the target, each selected amount and each `Usage_Candidate` usage only; `Amount_Reference = 0` per selected row; `Lemma_Selected_Step` (LA-10) per kind (`Mode_Of_H`, and `Budget_Only` for `Both_Kinds`). **No `Side_Sum`, `Side_Total`, LA-7 or `Both_Kinds` LA-10** (:1603). v5's "LA-7 and LA-8 at Columns=0" plan is explicitly withdrawn (§5.6:1050-1051).
- Moved into A-ROW's PO set: PO-A35 (DESIGN.md:2481); PO-A11 no longer lists LA-11 (:2460). PO-X7 states A-ROW adds no recursive function including the E=0 path, LA-11 reaching no `Side_Sum` (:2440).
- RL-25E added (DESIGN.md:3282); W-10a observes XA0/no allocation (:2403, 3360). F20/PO-X7 preserved (:2440; Appendix B.10 U-3). F41 recorded (§3.4:471-479).

**V5-RC3 (re-present H-A: GT-01..GT-50, U-1..U-6, LR-3A/LR-4A derivation, independent re-review): CLOSED (design argument); re-review = this review.** §5.12-§5.13 write out the complete final A-ROW executable and ghost text; Appendix B.6 inventories every construct GT-01..GT-50; B.10 states U-1..U-6; B.7.1/B.7.2 give LR-4/LR-4A their own six-row derivations. Independent re-review requested at §5.14:1804-1806 / §14 O-GHOST-HORIZON-A — supplied here; F35 stays OPEN pending proof+observation.

**V5-RC4 (cost statements; RL-25C=2E; RL-27): CLOSED (corrected/designed).** §9.3.7 (:2734-2745) replaces "within a constant factor" with the per-Held-usage-row checked `Compare` term `(8L+42)·PV(L)+Q(L)` vs the original's `20·PV(L)`, leading ratio `(8L+42)/20 = 3233/10` at L=803 [K-254], instance `454992179073696` [K-172] vs `1406689554160` [K-255], >300× [K-257]; obligated under O-COST-MEASURE/D2 (R-COST-5), no cap. §9.1 (:2540) states the release per-row E factor; RL-27 added (:3285). RL-25C workspace corrected to 2E (:3283; 1608/2000000/200000000 [K-262/K-261/K-260]).

**V5-RC5 (define PO-A34; reword W-11a; sync decisions.json): CLOSED.** PO-A34 defined (DESIGN.md:2480). W-11a reworded "on an input where the original also fails" (Appendix B.8 W-11a row; §12.6 W-11:3361; B.10 item 6). decisions.json synchronized.

**v4/v5 prior closures preserved.** R-DRC5, R-F32, R-OD2-DEPTH, R-A/R-B/R-PREFIX/R-WORKSPACE/R-OD1/R-OD2/R-NOTICE/R-SCOPE and V4-RC2(a)-(h), V3-RC1..RC3, V2-RC* carried (§1.5:93-97, §1.6:103-106; decisions.json `rulings_applied` R-CARRY-5). §6 (Algorithm B / DR-C5) carried unchanged (§4.1:500-504, §5.16:1849). No regression found in the sections I read. **Limit:** I did not re-diff the full carried text; I relied on the sealed D5 review's §6/§7/§10/§11 closure.

## 2. Theorem H-A as re-presented, and A-ROW: complete and correct on the complete domain

**The two v5 counterexamples are eliminated by the v6 text, confirmed against the final text and against C5 source.**

- **RL-25 (F40; Budget child C with valid 804-byte usage, amounts [05]/[01], E=1).** In `Decide_Rows` (DESIGN.md:1350-1365): `Op := Operand(Rows(J))` — `Operand` returns the usage only when `Usage_Selected`, whose first conjunct `Kind = Held_Capacity` is False for a Budget row, so `Op` is the amount (:653-655). `Lemma_Operand_Values` (LA-9N) usage conjunct is `Usage_Candidate`-guarded — False for Budget, so `Q.Value(usage)` is never formed (:1566-1568). `LR-2`/`Amount_Reference` read only the amount for a non-Held row. The pre-pass widens `E` with the usage only under `Usage_Candidate` (:1293-1294), so the 804-byte usage contributes nothing to E (E=1). **No construct evaluates C's usage.** Confirmed in C5: `Amount` evaluates `Exact_Value(Observed_Usage.Value)` only inside `if Item.Kind = Held_Capacity and then Item.Observed_Usage.Present` (`core/resource_run_ledger.adb:35-44`); `Amount_Reference` short-circuits `Q.Value(usage)` behind the same test (`core/resource_run_ledger.ads:187-191`). RL-25 reference walk True: `1-5=-4` [K-213=−4], `0-1=-1` [K-214=−1] (both re-run here). Matches DESIGN.md:3281, Appendix B.8, AP-1.
- **RL-25E (F41; as RL-25 with Length-0 amounts, E=0).** E=0 branch calls LA-11 and returns Equal (DESIGN.md:1305-1308). LA-11's v6 body applies LR-0 to the target and selected amounts, and to a usage only under `Usage_Candidate` (:1594-1599) — C is Budget, so its 804-byte usage is **not** touched; LA-11's Pre exempts a non-`Usage_Candidate` usage (:1585-1586), so the Pre is satisfiable with C's valid 804-byte usage present. No `Side_Sum`/LA-7/`Both_Kinds` LA-10 is reached (:1603). Reference walk True: `(0+0)-0=0` [K-251=0, re-run], `0-0=0` [K-27=0, re-run]. Matches DESIGN.md:3282, Appendix B.8, AP-2.

**Horizon argument structure (Appendix B).** H0 alignment (B.3) and the original formed-set W with Lemma W1 (B.4) are as in v5 (the v5 review found both sound); W1 gives E≤803. I re-ran the horizon constants: `256^804−2^6432 = 0` [K-65]; `256^803−2^6424 = 0` [K-188]; `2^6432−2·256^803 > 0` [K-226]; `2^6432−3·256^803 > 0` [K-248]. U-1 span discipline (B.10) holds: every `Data` span D1-A passes to a Big_Integer-forming function is T, A, U(`Usage_Candidate` only) or C, or `Normalized` of one; `Normalized(invalid)=Empty_Quantity` (Length 0, forms only 0 and P(0)=1); the only other arrays are D1-A's own accumulators (`Low_Quantity` over `Acc.H/Acc.B/Old_*/Res`, values < 256^E) — these are not `Data`. U-2 (no usage of a non-`Usage_Candidate` row), U-3 (no recursion added), U-4 (`Both_Kinds` only at Count=N; LA-10 per kind only), U-5 (no `Hi·P` with Hi<0, via `Acc_Value`'s safe form, DESIGN.md:1255-1260), U-6 (bounded intermediates) are each borne out by the constructs they cite.

**Construct inventory GT-01..GT-50 is faithful to the final text.** I mapped every construct of §5.12 (`Selected_Sum_Order`, `Decide_Rows`, `Add_Operand`, `Add_Accumulator`, `Compare_To_Target`, and the ghost helpers `Low_Quantity`/`Low_Prefix`/`Low_Value`/`Acc_Value`/`Kind_Of_H`/`Mode_Of_H`) and §5.13 (LA-9N, LR-0, LA-11, LR-3P, LR-6, LR-4, LR-4A, LR-5a/5b/5c) to GT-01..GT-50; nothing in that text is left out of the inventory. Span classes and bounds match: GT-08/GT-10/GT-11/GT-12/GT-44/GT-45 are exactly the usage-guarded sites; GT-09/GT-18/GT-34/GT-43 evaluate T/A spans the original also forms; GT-21/GT-29/GT-40/GT-46 are L values ≤ 2·P(I); GT-47's `Acc_Value` intermediates are bounded by Lemma S′ on W values. LR-4/LR-4A six-case tables (B.7.1/B.7.2): each row's side total is `max(|A_0|,|A_1|,|v|)` resp. `max(|S_H|,|S_B|,|S|)` (W values), each (D) total is a P-multiple term of a row side (≤ that side), each residual's sides ≤ 2·P. The LR-4A high-part step `h' = h+b+C` (b not in {−1,0,1}) is derived from the integer identity directly, not by analogy — the gap the v5 review flagged is answered.

**No ghost construct reads a Data span the original does not.** The only non-original spans are `Empty_Quantity` (Length 0, no Data bytes read) and the accumulator arrays (not `Data`). Every actual `Data` span (T, A, U-candidate, C) is one the original evaluates with `Exact_Value`/`Q.Value` when it reaches the call and succeeds (confirmed via `Amount`/`Sum`/`Sum_Reference`/`Contained` in C5). The author's 18-family adversarial desk pass (B.12, AP-1..AP-18) is consistent with my independent checks of the guards, including AP-3 (invalid usage with `Length=Byte_Count'Last`), AP-6 (invalid usage → `Empty_Quantity`), AP-7 (non-selected 804-byte-usage row), AP-11 (`Both_Kinds` mixed partial sums never formed), AP-17/W-11a (804-byte selected operand is not originally successful, outside H-A's hypothesis).

**F35 at design level for A-ROW.** The v5-level obstacle (a FALSE theorem) is repaired: the re-presented argument is sound as a design argument and this independent re-review finds no defect in it. The remaining R-H-A conditions — PO-A27..PO-A33, PO-A35 proved; the DR-C6/PO-A32 source review; RL-24/RL-25(z,n)/RL-25E(z,n)/RL-26 observed in the checks build — are proof and observation, not design. The design correctly keeps F35 / O-GHOST-HORIZON-A OPEN and BLOCKING (DESIGN.md:3437; §5.14:1804-1806; §16:3809-3811). This review closes none of them and grants no acceptance.

**JACKAL values H-A relies on — re-run.** All 15 new values K-251..K-265 reproduce exactly (parsed=, exact=, and the leading/trailing digits of the large summaries K-258/K-259/K-263 match jackal.json). Carried horizon/cost constants re-run and confirmed: 256^804=2^6432, 256^803=2^6424, 2·256^803<2^6432, 3·256^803<2^6432, PV(803)=70334477708 [K-159], 20·PV(803)=1406689554160 [K-255]. Per JACKAL rules these are `exact` (exact rational arithmetic, **not** formal-bounded); they establish the stated arithmetic instances only — the recurrences, counts, failure locations and the horizon argument they feed are [LEAD] reasoning and SPARK/review obligations (O-JACKAL-SYMBOLIC).

## 3. Independent adversarial pass: decision preservation, cost, per-kind LA-10

- **Decision preservation.** `Conserved`/`Contained`/`Check` bodies keep the original control structure (DESIGN.md:1087-1116; §4.1:495-497); the shared `Selected_Sum_Order` Post is the reference comparison (:761-766) and the D6 specs' Posts equal `Conserved_Reference`/`Contained_Reference` verbatim in C5 (`core/resource_run_ledger.ads`). Once proved (PO-A15/A16/A17/A19/A20/A21), A-ROW preserves the original decision on every input.
- **Release cost class.** No executable Big_Integer on the release path (source-level; O-NATIVE must confirm the compiled closure, PO-N1). The per-row O(E) factor (F42) is a **stated** cost change, obligated, no cap (§9.1:2540, §9.3.7, R-COST-5). RL-27(a/b/baseline) references re-run: `10000−256^802<0` [K-258], `256^802+9999−2·256^802<0` [K-259], `10000−65535=−55535` [K-265], `10001` rows [K-264]. RL-25C Held-series: `256^803−5>0` [K-263], workspace 2E [K-260/261/262].
- **Per-kind LA-10 (DESIGN.md:987-993, 1362-1365, 1751) is sound.** A-ROW calls `Lemma_Selected_Step` only with `Held_Only`/`Budget_Only`; `Both_Kinds`'s `Selected_Sum` is formed only at Count=N (U-4). `Selected_Sum` is non-recursive (:678-685); for `Both_Kinds` it is `Sum_Reference(Held)+Sum_Reference(Budget)`. Confirmed in C5 that `Included`/`Sum_Reference` partition selected rows by the two-valued `Charge_Kind`.

## 4. F38 / A-COL

Correctly carried OPEN and correctly not selected (DESIGN.md:5.15:1808-1829, §5.16:1833-1842, decisions.json `a_col`, R-F38). A-COL's column state encodes truncated multi-row sums `D(c)`, not in W and not boundable by Lemma S (RL-26 at c=802: `65537·(256^802−1) > 2^6432` [K-219]); and its LA-7 forms `Both_Kinds` mixed partial sums excluded by U-4 (Appendix B.11). V4-RC1/V5-RC1 are applied to A-COL anyway via PO-A34 (:2480), removing the Budget-usage evaluation but not the horizon hazard; A-COL remains ineligible while PO-A26 is OPEN.

## 5. Controls and expectations against C5

RL-24, RL-25(z,n), RL-25E(z,n), RL-26, W-0 calibration, IM-10, RL-12IN/RL-12I are well-formed; their reference expectations are correct against C5 to the extent I checked: the Budget-usage-never-read basis of RL-25/RL-25E is confirmed at `core/resource_run_ledger.adb:35-44` and `.ads:187-191`; `Sum`'s loop invariant `Result = Sum_Reference(…,Count,…)` at `.adb:49-64`; `Contained` has no `Shape` (`.adb:70-90`); `Exact_Value`'s `Place := Place*256` (`.adb:31`) forms 256^L (so an 804-byte span reaches 2^6432, the W-11a / original failure). RL-12I/RL-12IN pin the invalid/invalid contribution at 0 in both sign directions. **Limit:** I did not independently re-walk every RL/IM/PY/W fixture; I checked the controls central to H-A and the Budget-usage discipline.

## 6. Guarantee check (weakening / gates)

I found **no** Pre, cap, domain restriction, refusal, suppressed Ghost, `Assume`, new `Off` boundary, Assertion_Level change, added gate or lowered floor. The public `Selected_Sum_Order`/`Conserved`/`Contained`/`Check` carry no Pre; `Add_Operand`/`Add_Accumulator`/`Compare_To_Target`/`Decide_Rows` Pres are internal helper obligations established by callers (DESIGN.md:1327-1336, 1399-1403, 1448-1451, 1478-1479), not domain restrictions. `E` is unbounded (`Byte_Count`); larger E is a native heap/stack obligation (O-WORKSPACE-A), never a refusal (§7.8:2403-2418, §16:3808). F42 cost is stated and obligated, never accepted (R-COST-5). Resource failures are OPEN native obligations throughout (§4.2:536-537, §9.2, §16:3808). "Unreachability satisfies nothing": O-HELPERS stays OPEN and does not meet its full-domain obligation (§4.2:522-526). F35, F37/F40/F41 lemma extent, F38 all stay OPEN (§14:3437-3439). F32 restated, owned outside D1 (§3.4:383-408, O-ORIGINAL-F32). The only guarantee-relevant items are defects already repaired (RL-25, RL-25E) and stated cost changes — neither is accepted.

## 7. Required changes

None. All of V5-RC1..RC5 are addressed, both counterexamples are eliminated, the horizon argument is sound as a design argument, and the design correctly keeps F35 OPEN and BLOCKING.

## 8. Rulings (carried / affirmed)

- **R-H-A (affirmed).** v5's Theorem H-A was false; v6's re-presentation repairs the two causes and is sound at the design level. This review is the independent design-level re-review R-H-A requires; it clears the FALSE-theorem obstacle but closes nothing else. F35 / O-GHOST-HORIZON-A stays OPEN and BLOCKING for D1-A. No Pre/cap/domain restriction/refusal eligible. Owner: lead. Evidence still required: PO-A27..PO-A33, PO-A35 proved; the DR-C6/PO-A32 source review; RL-24, RL-25(z,n), RL-25E(z,n), RL-26 completing in the checks build.
- **R-EXTENT-2 (satisfied in design).** The Held-only (`Usage_Candidate`) restriction covers every D1-A construct that forms a Big_Integer from a usage span (pre-pass, length test, LA-9N, LA-9, LA-11, LA-7 Pre, `Lemma_Close`, and by construction `Usage_Selected`/`Amount_Reference`). U-1 states it universally; RL-25/RL-25E observe it. Owner: lead; evidence: PO-A30/A34/A35/A32, RL-25(z,n)/RL-25E(z,n) both builds.
- **R-F38 (carried).** A-COL OPEN and not selected; V5-RC1 applied to its LA-9 (PO-A34). A revival needs a different reviewed horizon argument.
- **R-COST-5 (carried).** Checked `Compare` term and release per-row E factor are stated cost changes under O-COST-MEASURE/D2; never acceptance; no cap. Evidence: measurements (PO-N4), RL-25C, RL-27.
- **R-CARRY-5 (carried).** R-DRC5, R-F32, R-OD2-DEPTH, R-A, R-B, R-PREFIX, R-WORKSPACE, R-OD1, R-OD2, R-NOTICE, R-SCOPE stand unchanged.

## 9. OPEN obligations

Every item of DESIGN.md:3421-3453 stays OPEN, including O-GHOST-HORIZON-A (BLOCKING), O-GHOST-EXTENT-A, O-GHOST-EXTENT-A-LEMMA, O-COST-MEASURE, O-WORKSPACE-A, O-PROOF, O-NATIVE, O-ORIGINAL-F32 and O-FINAL. The full strict proof floor (251), the sole `worldline-c_api` boundary, the ordered roster, and all original and additive controls in both builds remain required. No finite control, JACKAL instance, the author's desk adversarial pass, or this verdict substitutes for them. This review grants no source, proof, native or Phase One acceptance.
