# D1: release-path native Big_Integer repair — DESIGN v4

Author: Claude Code lead claude-opus-5-5 (drafting subagent), 2026-10-04.

Status: **DRAFT v4 for independent actual GPT-6.1 (`gpt-6.1-sol`) review.**

- Nothing in this package was compiled, proved, built, tested, run, reviewed or accepted.
- Every Phase One obligation stays OPEN. `proof_acceptance=false`, `source_acceptance=false`,
  `phase_acceptance=false`, `native_acceptance=false`.
- No operator option is selected or recommended.
- No source tree, composition, review, packet or evidence file was modified. No SIA note was written.
- The package is five files in `W/work/claude-lead-isolation-v1/wt-1/designs/claude-native-bigint-d1-design-v4/`:
  - this `DESIGN.md`;
  - `decisions.json`;
  - `APPENDIX-A-python-conversion-surface.md`, the corrected census (sha256 cited in §2);
  - `jackal.json`, every JACKAL call used (sha256 cited in §2);
  - `AUTHOR-NOTES.md`.
- **Self-contained.** v3's Appendix B governed v3 where it differed. Its errata E-1..E-5 and its structural refinement
  B.2 are incorporated into the main text below, at the places listed in §1.4. v4 needs no separate errata file.
  v1, v2, v3 and their reviews remain unchanged history.

v4 answers the sealed actual gpt-6.1-sol review of v3 (verdict ENDORSED_WITH_REQUIRED_CHANGES):

- the three required changes V3-RC1, V3-RC2 and V3-RC3;
- the fact corrections V3-F1..V3-F7.

It carries forward unchanged everything that review closed or accepted:

- the closures of V2-RC1..V2-RC3 and RC4..RC6;
- rulings R-A, R-B, R-PREFIX, R-WORKSPACE, R-OD1, R-OD2, R-NOTICE and R-SCOPE;
- F10, F11 and F12, with F12 extended to staged locations;
- the Appendix B errata.

While answering V3-RC3 ("record actual checked failure points"), v4 found and repairs one checked-representation
regression that the v3 design itself introduced (F34, design rule DR-C5). It also records one D1-specific checked
hazard that remains OPEN (F35).

## 1. Closure and trace tables

Line numbers refer to this file. Section numbers are given with each entry.

### 1.1 Required changes of the v3 review

| Item | What the review requires | Where v4 answers it | Status |
|---|---|---|---|
| **V3-RC1** (a) | E2-b must preserve json's original-key sorting and failure behaviour, including the pre-coercion mixed-key `TypeError` | §11.4.2 serializer requirements S-1..S-10 and E2-b ({{L-1142}}); F30 in §3.4 ({{L-F30}}) | PACKAGE (no option selected) |
| V3-RC1 (b) | Include aliased and forwarded JSON calls, at least `scripts/decisive_evaluation_test.py:264`, using a semantic census stronger than direct-name AST matching; update inventory, totals and settings | §11.1 ({{L-1111}}); Appendix A.2 (method), A.3 (193 + 2 + 254 = 449 operations), A.5 row 193 | CORRECTED; census results OBSERVED |
| V3-RC1 (c) | Give the `native/build_guard.py` interpreter an E1 disposition or a reviewed bound | §11.3 class C12 ({{L-C12}}); Appendix A.5 rows 160-162 | PACKAGE plus a reviewed-bound proposal |
| V3-RC1 (d) | Formatting exclusions as absolute-magnitude bounds; parsing exclusions as lexical digit-count bounds | §11.4.3 ({{L-1143}}); §11.4.4 ({{L-1144}}); Appendix A.4 | CORRECTED |
| V3-RC1 (e) | Correct Appendix A's C4/C5 byte-identity statement for `proof_manifest.py` | Appendix A.1; F33 in §3.4 ({{L-F33}}) | CORRECTED |
| V3-RC1 (f) | Integer-key and mixed-key-failure codec controls | §12.5 PY-8 and PY-9; also PY-10..PY-14 ({{L-PY8}}) | DESIGNED (unrun) |
| V3-RC1 (g) | Synchronize `decisions.json`; keep E0/E1/E2 unselected | `decisions.json` `operator_items` OD-2; §11 | PACKAGE |
| **V3-RC2** (a) | Equal and lower usage variants with full arrays, totals and status walks | §12.2 RL-7d, RL-7d′, RL-7e, RL-7e′ ({{L-RL7}}) | DESIGNED (unrun) |
| V3-RC2 (b) | The remaining invalid-operand selector combinations | §12.3 RL-12V, RL-12I, RL-12IN, plus RL-12S and RL-12M; the selector matrix in §12.7 ({{L-RL12V}}) | DESIGNED (unrun) |
| V3-RC2 (c) | A true middle-cell IM mismatch | §12.4 IM-11 ({{L-IM11}}) | DESIGNED (unrun) |
| V3-RC2 (d) | Map X6 caller-Post and re-entry, and X7 pre-allocation exits, to admissible controls or to proved-unreachable obligations | §7.1 exit map X0..X7 ({{L-71}}); §12.6 W-7, W-8 ({{L-W7}}) | DESIGNED; probes OPEN |
| V3-RC2 (e) | Cover staged-only and Primary_And_Staged export and lifetime paths | §12.4 IM-10P, IM-10S, IM-10PS; §12.6 W-5 matrix; §9.4, §9.5 | DESIGNED (unrun) |
| V3-RC2 (f) | Specify RL-7c's row arrays | §12.2 RL-7c | DESIGNED |
| V3-RC2 (g) | Correct RL-7b's arithmetic: proposed held 8 minus selected sum 7+3 | §12.2 RL-7b, using K-102 | CORRECTED |
| V3-RC2 (h) | Mark RL-8 and RL-9 unused, or define them | §12.2: unused identifiers, no coverage credit | CORRECTED |
| V3-RC2 (i) | Review notes: IM-7's empty magnitude with positive 7 is an overflow, not a guard rejection; IM-10's positive case must rebuild bindings and its mismatch must isolate the magnitude | §12.4 IM-6, IM-7, IM-10 | CORRECTED |
| **V3-RC3** (a) | Rebuild §9.3/F29 from the self-referential `Prefix_Value`/`Radix_Power` Posts, `Magnitude`/`Value` body and Post, Compare's checked body and lemmas, every new helper, lemma and contract, and saved copies | §9.3.0-§9.3.5 ({{L-93}}); F29 corrected in §3.3 | CORRECTED (static source reasoning) |
| V3-RC3 (b) | Correct A-GHOST-0's inherited factor estimate | §5.4 and §9.3.3: per-term factor `(4/3)(c²+11c+12)`, not "about K" | CORRECTED |
| V3-RC3 (c) | Restrict B's "no recursion" statement to new declarations | §6.5 ({{L-65}}) | CORRECTED |
| V3-RC3 (d) | Qualify source-only stack-placement claims | F27 in §3.3; §7.4, §7.5, §9.3.5 | CORRECTED |
| V3-RC3 (e) | Record actual checked failure points | §9.6 ({{L-96}}); W-2. This led to F34/DR-C5 (repaired) and F35 (OPEN) | CORRECTED; OPEN where stated |
| V3-RC3 (f) | Expand mixed-call repetition and the readiness/context mapping to primary and staged, with dependency-qualified injection locations | §9.4 ({{L-94}}), §9.5 ({{L-95}}); §12.6 W-5 | CORRECTED |
| V3-RC3 (g) | Synchronize RL-1 wording, trace and index labels, and `decisions.json` | §12.1 RL-1 ({{L-RL1}}); this table; `decisions.json` | CORRECTED |
| V3-RC3 (h) | Keep D2, native and cost obligations OPEN | §9.3.0, §14 | OPEN |

### 1.2 Fact corrections of the v3 review

| Id | Finding | Where v4 answers it |
|---|---|---|
| V3-F1 | E2-b must preserve json's original-key sort and the pre-coercion mixed-key `TypeError` | §11.4.2 S-3/S-4 and E2-b; F30; PY-8, PY-9 |
| V3-F2 | 192 direct sites reproduce, but `decisive_evaluation_test.py:264` is an omitted alias; direct-name matching is not a census | Appendix A.2, A.3, A.5 row 193; §11.1 |
| V3-F3 | `proof_manifest.py` is not byte-identical between C4 and C5 | Appendix A.1; F33 |
| V3-F4 | F29/§9.3 omitted nested public Posts and Compare's body and lemma work; A-GHOST-0's factor was not established | §9.3; F29 corrected; §5.4 |
| V3-F5 | Primary_And_Staged permits both readiness and both context Decide calls | §9.4, §9.5; F12 extended in §3.1; W-5 |
| V3-F6 | No middle-cell mismatch; W did not supply X6/X7; the equal-usage variant was incomplete | IM-11; §7.1, W-7, W-8; RL-7d, RL-7e |
| V3-F7 | RL-7b's arithmetic; RL-7c's arrays; RL-8/9 undefined | §12.2 |

### 1.3 Rulings of the v3 review: how v4 honours them

| Ruling | v4 treatment |
|---|---|
| R-A | Algorithm A is unchanged in architecture (§5). Additions: the corrected cost (§9.3), the recorded cost-shaping alternative A-SEL-L (§5.10), and the OPEN horizon hazard F35 (§5.11). Nothing narrows the signed, invalid, duplicate or every-target domain |
| R-B | Algorithm B keeps the null-admitting shape, carry-out inequality, verbatim guard and ghost lockstep (§6). DR-C5 (§6.4, §6.5) reformulates D1's own ghost contracts only. No public Pre, size refusal or original statement changes |
| R-PREFIX | §6.3 and §6.7 are unchanged, plus the review's clarification that preserving PFX-3's variant text alone does not prove equivalent behaviour |
| R-WORKSPACE | CL-1 uses the B.2 inner-block shape in the main text (§6.6, §7.2). CL-2 and CL-3 are as before (§7.5). F-B2/F-B3 stay operator-owned |
| R-OD1 | §10 is unchanged; no option selected |
| R-OD2 | §11 is repaired as V3-RC1 requires; no E1/E2 choice is made. The 640-digit chunk guard is kept |
| R-NOTICE | §5.4 is unchanged in substance. A-GHOST-0's cost is corrected; O-NOTICE-R1 stays OPEN |
| R-SCOPE | §4 and §14: D1 alone closes no helper, checked-Ghost, Python, transport, physical-cost or acceptance obligation |

### 1.4 Carried forward unchanged (closed or accepted by the v3 review)

| Item | v3 review disposition | Where it lives in v4 |
|---|---|---|
| V2-RC1 (B shape, digit interface, no sentinel, no public Pre) | CLOSED | §6.2-§6.6 (unchanged except DR-C5 in D1's own ghost contracts) |
| V2-RC2 (Work lifetime, every exit, probes, B.2 placement) | CLOSED | §6.6 and §7 (B.2 now in the main text) |
| V2-RC3 (OD-1 option set) | CLOSED | §10 (unchanged) |
| RC4 (v1) (guard-inclusive lockstep reference) | CLOSED | §6.5, §6.8 |
| RC5 (v1) (legal workspace behind the Boolean profile) | CLOSED | §7 |
| RC6 (v1) (helpers and Ghost OPEN; OD-1) | CLOSED | §4.2, §10 |
| V2-RC4, V2-RC5, V2-RC6, RC7 (v1) | NOT_CLOSED in the v3 review | addressed by V3-RC1, V3-RC2 and V3-RC3 above |
| F10 | CONFIRMED_AND_DESIGN_REPAIRED | §5.3, §12.3 (RL-12, RL-12N) |
| F11 | CONFIRMED_WITH_SCOPE | §3.1, §4.3 |
| F12 | CONFIRMED_WITH_REQUIRED_EXTENSION | §3.1 (extended to staged), §9.4 |
| E-1 (input hashes) | INCORPORATED | §2 identity table (correct values in the cell) |
| E-2 (`resource_run_ledger.py:248`) | INCORPORATED | §9.2 |
| E-3 (LA-4 Pre with relational operators) | INCORPORATED | §5.6 LA-4 |
| E-4 (CL-2 start expression) | INCORPORATED | §7.5 CL-2 |
| E-5 (chapters read) | INCORPORATED as an author process statement, not legality evidence | §2 |
| B.2 (CL-1 handler on an inner block; RM 11.6) | INCORPORATED | §6.6, §7.1, §7.2 |

### 1.5 New in v4 (not requested; found while answering)

| Id | Finding | Section | Status |
|---|---|---|---|
| F30 | In CPython 3.14, `json.dumps` uses the C encoder even with `indent`. Sorting uses the original items before coercion. The C and Python encoders differ in their recursion guard | §3.4, §11.4.2 | OBSERVED |
| F31 | `tomllib` converts TOML integers with `int(…, 0)` and offers no integer hook (E2-T). `argparse` `type=int` needs `int()`'s full grammar. Source compilation converts literals | §3.4, §11.4.5 | OBSERVED; package OPEN |
| F32 | The original unexecuted control `test_additive_finalization_collapse_requires_full_context_and_metadata` expects AUTHORIZED for a request that lacks `resulting_requirement`. By `Worldline.Collapse.Decide` that request is not authorizable. Original controls stay byte-identical; v4's additive IM-10 requests are complete | §3.4, §12.4 | LEAD finding; OPEN for the lead |
| F33 | C4/C5 Python identity: 299 of 300 files identical; only `proof_manifest.py` differs (pin append) | §3.4, Appendix A.1 | OBSERVED |
| F34 | The v3 Algorithm B ghost formed `Power_Reference (n) = 256**n`. At `n = 804` that is `2**6432`, which the installed runtime cannot represent, on inputs the original computes successfully (IM-1-like). DR-C5 removes it | §3.4, §6.4, §6.5, §9.6 | DESIGNED repair; PO-B22 OPEN |
| F35 | Algorithm A's one-sided ghost sums can exceed every value the original checked path forms on direct-Ada signed inputs (RL-24) | §3.4, §5.11, §9.6 | OPEN (O-GHOST-HORIZON-A) |
| F36 | DR-C1 removed only the helpers' own Posts. `Usage_Selected` still reaches `Q.Compare`'s checked Post and body, which is the dominant D1-added checked cost when usage rows exist | §3.4, §5.3, §9.3.3, §5.10 | CORRECTED; alternative A-SEL-L recorded |

Status labels: **DESIGNED** (lead-owned design text, unproved and unreviewed); **PACKAGE** (operator decision package,
nothing selected); **CORRECTED** (a v3 statement replaced); **OPEN** (the obligation remains); **OBSERVED** (read
from a file or tool output in this session).

## 2. Conventions, roots, inputs and skills

Evidence labels:

- **[OBS]** observed: quoted from a file at `file:line`, from a read-only command or read-only AST scan run in this
  session, or from installed binary strings carried from v3.
- **[JKL K-nn]** / **[JKL PE-nn]** a JACKAL MCP result from this session, recorded in `jackal.json`.
  - `jackal_exact` results carry `status=exact`, `formal=false`, `lane=rat`.
  - `jackal_poly_eq` results carry `status=exact`, `formal=false`, `lane=poly-eq`, with a `jackal-exact-cert-v1`
    witness.
  - Both report evaluator_sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, carry the
    verbatim non_claims of §15, and declare no consequence ceiling, so every result is treated as informational
    about code.
  - The v3 identifiers K-01..K-78 were re-evaluated in this session, except K-53, K-71 and K-76; their values are
    unchanged.
- **[LEAD]** lead reasoning: an unverified argument that is itself a proof or evidence obligation, never acceptance.
  Every cost formula, call count and failure-point location in §9 is [LEAD] static source reasoning, even where its
  arithmetic is [JKL].
- **[DOC]** guide or documentation text: skill chapters, installed examples, the GNAT RM, Python documentation. Not
  legality or behaviour evidence for this candidate.
- Every Ada block is **UNCOMPILED / UNPROVED** design text.

Roots:

| Root | Path |
|---|---|
| `W` | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow` |
| `WT` | `W/work/claude-lead-isolation-v1/wt-1` |
| `C5` | `W/work/claude-composition-v5-beta/source` (QUALIFIED_SOURCE_COMPOSITION; no acceptance). Bare `core/…`, `runtime/…`, `tests/…` paths are C5 |
| `C4` | `W/work/reviewed-common-proof-source-composition-v4/source` |
| `D3` | `WT/designs/claude-native-bigint-d1-design-v3` |
| `R3` | `D3/review/gpt61-v1` (the closure target) |
| `D2` | `WT/designs/claude-d2-checked-ghost-inventory-v1` |
| `RT` | `/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude` |
| `GP` / `GN` | `/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1` / `/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1` |
| `PY` | `/usr/lib/python3.14` |
| `SK` | `/home/sicarii/.claude/skills` |

Input identities [OBS `sha256sum` in this session]:

| Input | sha256 |
|---|---|
| `D3/DESIGN.md` / `decisions.json` | `b20554c493e8406f0fa7191802294668bf3ae94ab8a65c6a75505b6e405f261f` / `186c28e150cc2d888f066d0bfffbff7b9b19dcf63df5c66a3e6ffb5161bd33fd` |
| `D3/APPENDIX-A…` / `D3/APPENDIX-B…` | `a8ba784ac4ff3d0797fb3c7b0b2cd67981ca0fa6a0649215b88890c8d71db70a` / `e485cfc77acd28f011aa7cb799ec1496c1b6816d1d553bdf1e16264387f17a4c` |
| `R3/REVIEW.md` / `review.json` / `checks.json` | `e82534cb680b70b92105c78906d9c2109c1122b367641ef78d88741d5754407f` / `cb1e3740ee9e0b31a77f254b6fb3a70b032e4535ff06c5b6eab9e21cfb95de45` / `0631a4ff6d0136421f9a06369779eef133447ab7294a500d1f3b4b2eafe53ea2` |
| v2 `DESIGN.md` | `f916123307c5132a1485d7c089af82c60204af8ccb0667494f2457aee1702cb4` |
| `D2/INVENTORY.md` / `D2/review/gpt61-v1/REVIEW.md` | `e5b9984d2beadf12f35e3018aff33c23a47d93adea7bd886abe8df2db46574b6` / `03fbf2461e857ddf9a3a0bdcf2515a14ccb6cd8498ade4e682a8a4bb60f02820` |
| `HANDOFF.md` / `START-CLAUDE.txt` / `complete-phase1-prompt.txt` (E-1 incorporated) | `2f3a0b4b3bb2a0996824859c2d9f8a59e7c58f624b2d81cb00e40e76bf588237` / `004c71a8da3cb4e917812af427a1701bde226a18da615bcdbf483414d75f187e` / `1b228f4b07209c91c8f8770851906a8ebbf90db12f0af605954aff392946b327` |
| `core/resource_quantities.ads` / `.adb` | `7bb5ebf110cfb6caec3c204e97be8bc4d7a93ebdb3b9e6251f48a456eeae1a28` / `5e87d8a0e874a0f2010070e31140ee1eb638ff866beea6f85da1f41599863b9b` |
| `core/resource_run_ledger.ads` / `.adb` | `9a761421da3799da2ecb3b8b1df3daa05b5d4c050f31bf32f2d12e50687d6c02` / `8e7c02c50954b9bb3ef2a7cf4a818931b6d0871c88c221e528eee81a964dbe42` |
| `core/canonical_artifacts.ads` / `.adb` | `bb62783aefa5b2b105dcec33d0273165d2cb5ba86c07006df11f101f5a057fee` / `979466c0c24fadb5ae5f4aac29a08cff680d367c4356ec69faa0596c7c5f2aa3` |
| `core/evaluation_finalization.ads` / `.adb` | `e20808c44b84e02485e10a3eb1e1e36a2f2f88defd75eb97c536cee6851c287a` / `c64f17246f0dfa3d88299a534e3e716ada35fd05120983a3d8f53a7c28d1a738` |
| `core/evaluation_finalization_c.adb` / `.ads` | `bdcf333878aebe4aca55333bc3b9a9a50007c187fc4b380dec1adb18127f83d3` / `2ca8602e87eb4605ddeda8e61c223ff39d765a81d3e22baec3e7d981bb74010b` |
| `core/worldline-evaluation_authority.ads` / `core/worldline-collapse.ads` / `.adb` / `core/worldline-collapse_wire.ads` | `29ea441b1bcc0212db70143c09b961b1f911827c8f30b40cc52f88080f4c222b` / `98b2661b6911332da1b460a78003ea5d3b692c8406c6c34c32b70ab9d6988a95` / `ba797079cf4316688eab9a7be2092e7c20db91c0881151e9df707cfa128937ef` / `987b3fa75865ae84fa1549424c947853c89a6f7a6762112975ace4d1918a00bd` |
| `core/evaluation_completion_c.adb` | `b799e93af37ca90104050473119aaca380b54244a491c2cc57226db8eaa77d69` |
| `core/resource_reservation_transition.ads` / `.adb` | `886bb13a69cdf029bc10703b39bce49eaeadb9be543d8449509badf6e6fd2aae` / `705f7102a64c06e4e03ab354fc3deac928129249fcb054146a486291ff1f04f3` |
| `core/resource_run_ledger_c_api.adb` / `core/resource_run_ledger_wire.adb` / `core/worldline_core_sources.gpr` | `fbc97b4c17ee0a0a17e74bae669fa11e674bb234ce5cd8f73d374b7d7e114581` / `d49ca335a1a3a353cdd0ce02ff2b51ea9b3eab359f557b5757fd09caad203a11` / `701931bc94f17aae8a14268cf7051f9a6d7b5bf8c7a1e0adccb9be0f5c0dff3c` |
| `runtime/worldline/canonical.py` / `core.py` / `finalization_kernel.py` / `evaluation_terminal.py` | `d80f79bcedace5364d2e9a238ab05b48250660d86cfb4c14aa5393f4b37952af` / `ee77fa7a39178b844972b3a3d704fb0732b93b73aead8c2b80137db66454786c` / `918fc2caef37d4bb5cdd4a5ff3f4b0ea072e156c3763d90afafa501c235a57a3` / `9f5e97446797f09633008c3d8c1f7d6759b674122681887e73a7a6e78db53033` |
| `tests/test_finalization_kernel.py` / `tests/test_raw_evaluation_default.py` / `tests/test_resource_run_ledger_v1.py` | `76141dfb2ddea1c9fb62e5ea09d27830432e96273f85e984da94f5ebbafb4a62` / `22b5b189f9686f456214666b5a4dc4b0e3c93ee5b48f983b18994f8119f1a4f0` / `eff3894460e2407afaeecaef78433f660b4c80a11c621f5a7ef67ac452ac0f63` |
| `APPENDIX-A-python-conversion-surface.md` (v4) / `jackal.json` (v4) | {{SHA-A}} / {{SHA-J}} |

Python standard-library, header and other C5 Python identities are in Appendix A.1. The pins in
`runtime/worldline/proof_manifest.py` are normalized hashes from the official generator and differ from raw file hashes
by design.

Skills: the `ada` hub, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`,
`ada-2005-amendment` and `ada-high-integrity` were loaded with the Skill tool in this session. v3 read ch05, ch06,
ch13, ch17, ch23, ch26, ch27, ch33 and ch36 of the SPARK guide and advanced-ada ch13 and ch16. E-5, now incorporated,
records that three of those chapters were completed after v3's sentence was written. That is an author process
statement, not legality evidence.

The SPARK User's Guide skill is release 28.0w, a development release. It is guidance, not legality evidence for the
installed GNATprove FSF 16.1.0. No compiler, prover, build, test, WORLDLINE code, systemctl, project-vault or restic
command was run. No WORLDLINE module was imported.

**Fixed requirements, verbatim and never weakened:**

- `START-CLAUDE.txt:8`: "Resolve native Big_Integer full-domain/runtime/checked-Ghost cost correspondence without
  adding caps, suppressing assertions or turning required successes into refusals."
- `HANDOFF.md:129`: "Do not add a domain cap, count native failure as an accepted refusal, substitute a proof-only
  light library or suppress checked Ghost code."
- `HANDOFF.md:131`: "Establish exact native runtime/body correspondence, implicit controlled Adjust/Finalize/copies,
  heap and primary/secondary stack lifetimes, checked contract/reference/Ghost recursion, time and physical resource
  costs, failure/termination semantics and actual assertion build selection."
- `HANDOFF.md:29`: "Do not narrow domains or accepted cases, lower contracts or floors, remove deterministic controls,
  skip bodies/callers, waive warnings, add assumptions, suppress checked assertions, restore Off exemptions or
  substitute a renamed Boolean for custody/confinement."
- `HANDOFF.md:161`: "… zero unproved, zero justified and zero pragma Assume, with complete reports and all strict
  warning obligations resolved. A renamed library or Off wrapper is not a new exception."
- `complete-phase1-prompt.txt:34`: "… A temporary refusal or documented limitation keeps the original obligation
  OPEN."

**Lead constraints for this design (unchanged from v3):**

- No domain cap.
- No Pre on any public subprogram.
- No accepted-refusal path.
- No light library.
- No suppressed or reduced checked assertion or Ghost code.
- No Assertion_Level or policy change.
- No new `SPARK_Mode => Off` boundary. The sole original boundary stays `core/worldline-c_api.adb:25`.
- No waived warning. No `pragma Assume`.
- Floor 251 and the 535-name ordered REQUIRED_PROVED prefix stay; additions are appended only.
- These texts stay byte-identical:
  - the public Posts of `Exact_Value`, `Amount`, `Sum`, `Conserved`, `Contained` and `Check`;
  - every `*_Reference`;
  - the profile of `Integer_Matches`;
  - every existing conjunct and variant of `Prefix`;
  - every original control.

## 3. Facts and corrections

### 3.1 Facts retained from v3, with their corrections

- **F1. Runtime limits and allocation [OBS].**
  - `RT/s-genbig.adb:1176` declares `Bignum_Limit : constant := 200`. `Normalize` (`:1178-1195`) raises
    `Storage_Error` when `X'Last - J > Bignum_Limit` (`:1190-1191`).
  - Normalized results therefore have at most 201 limbs of 32 bits: 6432 bits [K-01] or 804 bytes [K-02].
  - So `256**803 = 2**6424` (6425 bits) is representable [K-03, K-04, K-188]. `256**804 = 2**6432` [K-65] (6433 bits)
    is not [K-05, K-06].
  - Direct allocations bypass `Normalize`: in `To_Bignum` (`:1230-1285`) and in the `Amount = 0` shift cases (`:418`,
    `:451`).
  - `Big_Exp` has its own limit at `:332`.
  - `System.Shared_Bignums.Length` is `Natural range 0 .. 2**23 - 1` (`RT/s-shabig.ads:46`).
  - Every bignum is heap-allocated (`RT/a-nbnbin.adb:55-58`). `Big_Integer` is controlled: Adjust deep-copies
    (`:604-609`) and Finalize frees (`:615-620`). Comparisons allocate no result (`:106-145`); multiplication does
    (`:502-507`) (D2 review C-UNIT).
- **F2.** Check calls `Exact_Value` directly (`core/resource_run_ledger.adb:173-174`). D1 replaces that branch (§5.7).
- **F3.** Nonnegativity holds only under `Row_Valid` / `Shape` (`core/resource_run_ledger.ads:151-153, 226-228`).
  `Exact_Value`, `Amount`, `Sum` and `Contained` have no Pre. Negative zero and padding are admitted
  (`core/resource_reservation_transition.ads:132-138`).
- **F4. The decimal/binary interval.**
  - `10**1936 < 2**6432 < 10**1937` [K-07, K-08], so `2**6432` and `2**6432 - 1` have 1937 digits [K-09].
  - Every magnitude with at least 1938 digits [K-10] is at least `2**6432`.
  - Python's limit governs the decimal JSON conversions (`runtime/worldline/canonical.py:41-60`). It does not govern
    `int.to_bytes` / `int.from_bytes` (`runtime/worldline/evaluation_terminal.py:76-104`).
  - The Python failure length is whatever limit is configured: 4300 by default, any value of at least 640, or 0 for
    unlimited (F25).
- **F5.** Predecessor algorithms are patterns, not proofs (`HANDOFF.md:61`).
- **F6.** In C5, `Integer_Matches` is body-private with no contract (`core/canonical_artifacts.adb:431-463`).
  Packet 07 removed the initializations of `Product`/`Addend` (`:437`). No ghost decimal or binary reference exists.
- **F7.** Base64 is streamed (`:293-347`). Any work array is new storage.
- **F8.** Whole-operation costs:
  - `Contained` compares for every target after an O(N²) parent search (`core/resource_run_ledger.adb:70-90`).
  - `Check` calls each predicate at most twice, subject to short circuit (`:169-172`).
  - The transports **declare** whole-input local copies: `core/resource_run_ledger_c_api.adb:208-213` (a
    dynamically bounded `Q.Byte_Array` and row arrays), and `core/evaluation_finalization_c.adb:112-118, 160`
    (`Copy_Data` returns an unconstrained `P.Bytes` that initializes `A`).
  - Where these copies live (primary stack, secondary stack or an elided copy) is not established by source (F27).
- **F9.** The Python observations are of the authors' interpreters only (F25).
- **F10 (confirmed and repaired).**
  - The v1 selector `Compare (Usage, Amount) = Greater` returns Invalid when either span is invalid.
    `Amount_Reference` instead compares `Q.Value`, which is 0 for an invalid span (`core/resource_quantities.ads:85-117`;
    `core/resource_run_ledger.ads:187-192`).
  - v3 and v4 normalize invalid spans before comparing (§5.3).
  - RL-12 and RL-12N discriminate the whole `Contained` result. v4 completes the selector matrix (§12.3, §12.7).
- **F11 (confirmed with scope).** `core/worldline_core_sources.gpr:8-21` defaults `WORLDLINE_BUILD` to `checks` and adds
  `-gnata`. `install.sh:184` and `packaging/PKGBUILD:31` do not select `release`. This is not evidence of the inherited
  environment, the compiled scenario, the runtime closure or the loaded binary (O-BUILD-SELECTION).
- **F12 (confirmed; extended to staged locations, V3-F5).**
  - On `wl_finalization_decide_v1`, `Decide` maps any Ada exception to 255 (`core/evaluation_finalization_c.adb:253-256`).
  - On `wl_collapse_decide_finalization_v1`, `Decide_Mixed` (`:357-509`) calls the finalization `Decide` at up to four
    places. Each is reached only for an evidence slot of kind 2 (finalization):
    - **primary readiness**: `Read_Ready` → `Decide` (`:429-430` → `:386`), mark
      `finalization.mixed.primary-ready-rejected` (`:434`);
    - **staged readiness**: `:441-442` → `:386`, mark `finalization.mixed.staged-ready-rejected` (`:446`);
    - **primary context**: `Context_Joined` → `Final_Context_Matches` → `Decide` (`:474` → `:406` → `:273`), mark
      `finalization.mixed.primary-context-rejected` (`:476`);
    - **staged context**: `:479` → `:406` → `:273`, mark `finalization.mixed.staged-context-rejected` (`:481`).
  - `Decide`'s own handler converts any exception inside it to 255 and records the `finalization.decide` diagnostic
    (`:253-256`). An `Integer_Matches` failure therefore reaches the context stage as a 255 return. That gives
    `finalization.context.seal-rejected` (`:276`), not `Final_Context_Matches`'s own handler (`:351-354`).
  - `Decide_Mixed`'s own handler (`:505-508`) catches exceptions raised elsewhere.
  - Which places run is dependency- and readiness-qualified (§9.5): `Primary_And_Staged` can run all four
    (`core/worldline-evaluation_authority.ads:19-36`).
  - Hard process faults (for example SIGSEGV on a foreign thread) are not shown recoverable.
  - None of these outcomes is an accepted mathematical refusal.

### 3.2 Corrections of v2 statements (V2-F13..V2-F18; carried from v3)

- **V2-F13.** In the release build the pre-D1 `Exact_Value` body raises for a **valid** span of Length ≥ 804, whatever
  its value: `Place` reaches `256**804 = 2**6432` [K-65]. An invalid span returns 0 at `:24`. In the checks build every
  checked evaluation is a separate failure point (§9.6). Aggregates can reach the limit at shorter extents. D1's
  ghost `Low (S)` need not grow on padded zero inputs.
- **V2-F14.** "No other exit after allocation" is false (§7.1).
- **V2-F15.** OD-1 (ii) does not make "only allocation fail" (§10).
- **V2-F16.**
  - 4000-digit chunks exceed the minimum limit by 3360 digits [K-44].
  - The daemon request id, the client parse and the CLI output are not host-bounded.
  - E0's "native code accepts every length" is withdrawn.
- **V2-F17.** RL-1 now starts from the original genesis READY fixture. RL-12 and RL-14 are whole-result
  discriminators (§12).
- **V2-F18.** The no-fallback claim is withdrawn (§6.7). F-B1 (CL-2) is lead-owned (§4.4).

### 3.3 Lead-found facts carried from v3 (F19-F29), with F27 and F29 corrected

- **F19. Installed GNATprove shape rules [OBS strings of `GP/libexec/spark/bin/gnat2why`, sha256
  `375d0100954a66c78bace00d2229c9b96a30b6cf28845e00c4db220ba1efddb5`].**
  - Unsupported:
    - a loop invariant in a list of statements with an exception handler or with a finally section;
    - a non-scalar or address-claused object declared before the loop invariant;
    - a package or subprogram declaration in a loop before the invariant.
  - A warning text: "The initial value of constants declared before the loop invariant is not visible after the
    invariant".
  - Consequences: no declaration in loop bodies before invariants; no loop with an invariant in a handler- or
    `finally`-protected list.
  - Strings are not legality evidence (probe P-X3).
- **F20. Recursion notices attach to recursive functions only [OBS
  `W/work/claude-operator-decision-package-v1/evidence-recursive-notices.json`, 25 unique items].**
  - The tags are `[contracts-recursive]` and `[numeric-variant]`.
  - `Sum_Reference` carries both.
  - Recursive lemma procedures with `Subprogram_Variant` carry none.
  - D1 adds one recursive function (`Side_Sum`) under A-GHOST-1 and **no recursive declaration** in Algorithm B.
- **F21. Installed flow and dead-code warnings [OBS F10K ledger].** INEFFECTIVE initialization and VC_DEAD_CODE
  "unreachable code". The latter is the decisive gate on CL-1 (P-W3).
- **F22. Installed exception examples [OBS `GP/share/examples/spark/gnatprove_by_example`].**
  - `ug__exceptions_rte/test.out:1-4` reports "warning: unreachable branch" for a run-time-check exception.
  - `ug__storage_error/storage.adb:4-13` uses an Off body; that pattern is forbidden here.
  - `ug__access4` proves leak absence with a pool-specific `Free`.
- **F23. `finally` is experimental [OBS `GN/share/info/gnat_rm.info:25940-25944, 27013-27075`].**
- **F24. Refined_Post and the variant warning** [OBS `spark_book/Chapter-06/very_longs.adb:200-208`; gnat2why strings].
- **F25. Python limits [OBS, `/usr/bin/python3` 3.14.7; the v3 review observed the same].**
  - `default_max_str_digits=4300`, `str_digits_check_threshold=640`.
  - `set_int_max_str_digits(639)` is refused, and limits from 1 to 639 are fatal at startup.
  - `-X int_max_str_digits=640` is accepted.
  - `-I` ignores the environment variable.
  - The installed header states the threshold as `_PY_LONG_MAX_STR_DIGITS_THRESHOLD 640`, "a guaranteed minimum size
    limit for bignums" (`/usr/include/python3.14/internal/pycore_long.h:31-42`) [OBS].
  - No WORLDLINE process was observed.
- **F26 (superseded by §9.5 for the mixed export).** `Artifact_Binding` → `Bindings` → `Tagged_Matches` →
  `Integer_Matches` is reached from exactly four places [OBS grep]:
  - the `Seal` body (`core/evaluation_finalization.adb:270`);
  - `Seal`'s Post (`.ads:395`);
  - the `Seal_Reference` body (`.adb:129`);
  - `Seal_Equation` (`.ads:362`), through `Seal_Reference`'s Post.
  `Seal` is called only from the C export `Decide` (`core/evaluation_finalization_c.adb:219`). Repetition: §9.5.
- **F27 (corrected; V3-RC3 d).**
  - The transports declare whole-input local copies (F8).
  - The project switches contain no `-fstack-check` (`core/worldline_core_sources.gpr:11-12`).
  - **Source declarations establish neither primary versus secondary stack placement, nor copy elision, nor
    finalization order.** That holds for the transport copies, for `Copy_Data`'s unconstrained function result
    (`core/evaluation_finalization_c.adb:112-118, 160`), for D1's saved ghost copies (`Old_Work`, `Carry_In`,
    `'Old` values), for A-GHOST-0's ghost aggregates, and for CL-2's frame array.
  - Each placement is native evidence (PO-N2, PO-N7, O-NATIVE). Stack-size dependence and stack-clash exposure for
    input size are therefore OPEN for the transports independently of D1. D1 does not claim they are primary-stack
    copies.
- **F28. C5 deltas relevant to D1 [OBS `diff C4 C5`].**
  - The `Prefix` digit-loop invariant `:229`.
  - The `Product`/`Addend` initializations removed (`:437`).
  - `Tagged_Matches`' `Parsed_Kind` selector.
  - Packet 05 parenthesization.
  - D1 packets write explicit left-association parentheses.
- **F29 (corrected; V3-F4).**
  - Every pinned reference and every public ghost function is evaluated by its body **and** its contracts under
    `-gnata`.
  - The public `Radix_Power` and `Prefix_Value` Posts call their own predecessors, so each public evaluation is a
    chain.
  - `Magnitude` and `Value` evaluate their subordinate function in body and Post.
  - `Compare`'s checked body adds padding lemmas, `Is_Negative`, assertions, per-column `Magnitude` invariants and
    `Prefix_Bounds` beyond its Post.
  - Exact source call counts are in §9.3.1-§9.3.2: for example one checked `Value` on a valid span of length `L`
    performs `4·PV(L)` Power_Reference invocations, with `PV(L) = L(L+1)(L²+11L+12)/6`.
  - v3's "~L⁴ per `Q.Value`" and its Post-only Compare estimate are withdrawn.

### 3.4 New facts found while answering the v3 review (F30-F36)

- **F30. CPython 3.14 json paths [OBS `PY/json/encoder.py`, `decoder.py`, `scanner.py`, `__init__.py`; headers].**
  - `json.dumps` → `encode` → `iterencode(o, _one_shot=True)`. That uses the **C encoder** whenever
    `_json.make_encoder` exists, **with or without `indent`** (`encoder.py:249-257`). The pure-Python
    `_make_iterencode` (`:265-454`) runs only for non-one-shot `iterencode`.
  - With `sort_keys`, the Python encoder sorts the **original** `(key, value)` items with `sorted(dct.items())`
    (`:357-358`) **before** coercing keys (`:361-382`). Integer keys therefore sort numerically. Incomparable mixed
    keys raise `TypeError` from the sort before any key is converted or emitted.
  - The coercion order is: `str`; `float` (through `floatstr`, which honours `allow_nan`); `True`/`False`/`None`;
    `int` (through `int.__repr__`, also for subclasses); `skipkeys`; else `TypeError("keys must be str, int, float,
    bool or None, not …")`.
  - Errors receive PEP 678 notes (`:330`, `:417`).
  - With a `parse_int` keyword, `json.loads` builds `cls(**kw)` (`__init__.py:349-365`), stores `parse_int or int`
    (`decoder.py:329`) and keeps `make_scanner = c_make_scanner or py_make_scanner` (`scanner.py:73`). The C scanner
    is retained.
  - C-level recursion protection is stack-address based (`pycore_ceval.h:238-245`). The Python frame limit is separate
    (`cpython/pystate.h:121-123`). C and Python encoders therefore have different depth thresholds. The C encoder's
    own source is not installed, so its exact sort and note behaviour is expected to match the Python encoder; PY-8,
    PY-9 and PY-11 confirm it against the real `json.dumps`.
- **F31. Other decimal conversions found by the extended census [OBS; Appendix A.8].**
  - `tomllib.loads` (`runtime/worldline/environment.py:217, 236`) converts TOML integers with `int(…, 0)`
    (`PY/tomllib/_re.py:110-113`) and has no integer hook.
  - Seven `argparse` `type=int` options parse operator text with `int()`'s full base-10 grammar: whitespace, sign,
    PEP 515 underscores and Unicode decimal digits.
  - `ast.parse`, `compile`, `exec` and `ast.literal_eval` convert source-code decimal literals.
  - `checks.py:888-889` formats a JSON-parsed number with `str()`.
- **F32. An original control's collapse expectation conflicts with `Worldline.Collapse.Decide` [LEAD on OBS source].**
  - `tests/test_finalization_kernel.py:245-263` builds its request from `RawDependencyControls.checkpoint()`
    (`tests/test_raw_evaluation_default.py:523-532`, where `resulting_requirement=None`) and changes `mode` to
    `CANDIDATE_EVALUATION` without supplying `resulting_requirement`. It then expects `AUTHORIZED`.
  - For Candidate_Evaluation, `Required_Present` requires `Resulting_Requirement.Present`
    (`core/worldline-collapse.ads:148-154`). `Decide`'s body returns `Identity_Absent` at `core/worldline-collapse.adb:24-25`
    before `Requirement_Changed`. `Decide_Mixed` returns any non-Authorized collapse decision unchanged
    (`core/evaluation_finalization_c.adb:487-490`). So the request cannot be AUTHORIZED.
  - The file states that its controls are unexecuted (`:1-4`).
  - D1 does not modify original controls. The conflict is recorded for the lead as OPEN (O-ORIGINAL-F32): if a run
    confirms it, repairing an original control is a separate reviewed change outside D1. v4's additive mixed fixtures
    (IM-10P/S/PS) state complete requests.
  - v3's IM-10 inherited the AUTHORIZED expectation; that is corrected in §12.4.
- **F33. C4/C5 Python identity (V3-F3) [OBS].** 299 of the 300 Python files are byte-identical. `runtime/worldline/proof_manifest.py`
  differs by an appended 6-line pin block (lines 1024-1029 [K-93]); lines 1-1023 are identical (Appendix A.1).
- **F34. v3's Algorithm B ghost exceeded the original's representation horizon [LEAD on OBS source].**
  - v3's `Multiply_Add` Post, LB-5 and the compare-phase invariant evaluated `Power_Reference (n)` (`256**n`) on
    every call, and `Finish_Binary`'s Post formed `(Value'Old + 1) * P(Upto)`.
  - For an `n = 804`-byte magnitude, `256**804 = 2**6432` [K-65] exceeds the installed limit (F1).
  - The original statements on a matching input never form a value ≥ `256**n`. IM-1, the decimal `10**1936` with an
    804-byte magnitude [K-07, K-150], succeeds pre-D1 in both builds but would fail in the post-D1 checks build.
  - v4's DR-C5 (§6.4, §6.5) reformulates these D1 ghost contracts so that they form `256**n` only when a carry out of
    the top cell exists. Then the decimal value itself is ≥ `256**n` and the original computation forms it too
    (PO-B22).
- **F35. Algorithm A's one-sided ghost sums can exceed the original's horizon on direct-Ada signed inputs [LEAD; K-183].**
  - `Side_Total` sums the magnitudes of all selected operands on one side. The original checked path forms partial
    sums in row order (`Sum_Reference`, `Sum`), which cancel.
  - Example RL-24: 514 children alternating `±(2**6424 - 1)` [K-184, K-188]. Every original partial sum is at most
    `2**6424 - 1` [K-186, K-187], but D1's L-side sum of 257 such magnitudes exceeds `2**6432` [K-183].
  - On the Check path, `Shape` makes every operand nonnegative, so one-sided sums equal the original's sums and the
    hazard is absent.
  - It is a D1-introduced checked-build failure class on the direct-Ada domain: OPEN (O-GHOST-HORIZON-A, §5.11).
- **F36. DR-C1's scope [LEAD on OBS source].**
  - `Usage_Selected` is Post-free, but its body calls `Q.Compare`, whose Post (`core/resource_quantities.ads:107-117`)
    and checked body (`.adb:340-402`) run on every call under `-gnata`.
  - D1 calls `Operand`/`Usage_Selected` per selected Held-usage row per column in executable code, and repeatedly in
    ghost row terms.
  - So DR-C1 removes only the helpers' own Posts. The resulting Compare work is the dominant D1-added checked cost
    when usage rows exist (§9.3.3).
  - A lead-owned contract-free alternative, A-SEL-L, is recorded (§5.10).

## 4. Scope (R-SCOPE)

### 4.1 What D1 v4 changes

| Unit | Executable change | Contract change |
|---|---|---|
| `core/resource_run_ledger.adb`: `Conserved` | two `Selected_Sum_Order (…) = Equal` tests replace `Exact_Value = Sum` | none; the Post is byte-identical |
| `core/resource_run_ledger.adb`: `Contained` | loop 2 tests `Selected_Sum_Order (…, Both_Kinds, Rows (I).Amount) = Greater`; loop 1 and the loop-2 invariant are byte-identical | none |
| `core/resource_run_ledger.adb`: `Check` | only the capacity condition (`:173-174`) becomes `Pair_Sum_Order (…) = Greater`; every other branch, its order and its status are byte-identical | none |
| `core/resource_run_ledger.adb`: new body-private entities | types, Post-free helpers, comparators, ghost model (§5.4), lemma procedures (§5.6) | new entities only |
| `core/canonical_artifacts.ads` | none | **adds** the public ghost `Integer_Token` and **one Post conjunct** on `Prefix` (D-B-PREFIX, §6.3). Profile, existing conjuncts and variant are byte-identical |
| `core/canonical_artifacts.adb`: `Prefix` | none | adds one loop invariant to the digit loop (`:228-232`) |
| `core/canonical_artifacts.adb`: `Binary_At` | none | **adds** `Post => Binary_At'Result <= 255` (body-private, no contract today) |
| `core/canonical_artifacts.adb`: `Integer_Matches` | body replaced: verbatim guard, allocation, inner handled block around one call (B.2), free (§6.6); profile byte-identical | **adds** `Global => null`; no functional Post (§6.5) |
| `core/canonical_artifacts.adb`: new body-private entities | `Work_Access`/`Free_Work`, `Multiply_Add`, `Decide_Work`, ghost procedures, lemmas, `Work_Value` (§6), with DR-C5 contract forms | new entities only |

Unchanged:

- `core/resource_run_ledger.ads` and `core/resource_quantities.*`;
- `core/evaluation_finalization*`;
- every C export, the wire layouts, all Python and every original control.

The run-ledger body uses only Resource_Quantities' public `Span_Valid`, `Digit`, `Compare`, `Prefix_Reference`,
`Power_Reference`, `Magnitude`, `Value` and `Prefix_Value`, together with lemma procedures copied per package, as in
`core/resource_quantities.adb:230-296` and the copies in `core/resource_reservation_transition.adb`.

### 4.2 What stays OPEN: unreachability satisfies nothing

- **O-HELPERS.**
  - `Exact_Value`, `Amount` and `Sum` keep their bodies and Posts (`core/resource_run_ledger.ads:185-213`). They stay
    in the Library_Interface (`core/worldline_core.gpr:69`) and in the required roster
    (`runtime/worldline/proof_manifest.py:967`).
  - After §4.1, the source-level release path of the three exports no longer calls them; the compiled closure is
    O-NATIVE.
  - That does not meet their own full-domain obligation. Routes are OD-1 (§10).
- **O-GHOST (D2).**
  - Under `-gnata`, every executed contract, invariant and ghost statement still evaluates Big_Integer.
  - D1 adds checked work (§9.3) and one OPEN horizon hazard of its own (F35).
  - DR-C5 removes the B-side horizon excess (F34).
  - D1 closes no part of D2.
- **O-PYTHON, O-PY-AUDIT, O-PY-COST.** OD-2 (§11).
- **O-TRANSPORT-MAPPING.** The export exception mappings (F12) are unchanged by D1. They must be classified so that a
  native failure is never counted as acceptance (§9.4).
- **Physical resources.** Transport copies (F8, F27), heap for the Work array (§7) and time (§9) remain native
  obligations.

### 4.3 Build scenarios

| Scenario | What D1 changes | What it does not change |
|---|---|---|
| `release` (selected only by `-XWORLDLINE_BUILD=release`; no in-tree path selects it, F11) | The repaired decision bodies contain no executable Big_Integer operation. This is a source-level statement; O-NATIVE must confirm the compiled closure | transport copies, the Work heap allocation, `Exact_Value`/`Amount`/`Sum` (OD-1), Python (OD-2), physical limits |
| `checks` (the default, F11) | executable bodies as in `release` | Every Pre, Post, invariant and ghost statement, including D1's new ones, still evaluates Big_Integer (§9.3). The representation limit applies (§9.6). Large inputs still fail (D2) |

Choosing `release` to make checked Ghost disappear would violate `HANDOFF.md:129-131`. It is not a repair.

### 4.4 Ownership (synchronized with `decisions.json`)

| Lead-owned (within the fixed guarantees) | Operator-owned (no choice made here) |
|---|---|
| Algorithm A and B implementations, including A-GHOST-1 versus A-GHOST-0 (§5.4), the recorded A-SEL-L (§5.10) and DR-C5 (§6.4) | OD-1 runtime/type/API architectures (i-a), (i-b), (ii) (§10) |
| Additive proved strengthenings (D-B-PREFIX) and the internal alternatives PFX-2, PFX-3, PFX-5 (§6.7) | OD-2 E0/E1/E2, the E2-T disposition, and the protected-custody flag or source changes E1 needs (§11) |
| Workspace CL-1 and the lead-owned alternatives CL-2 (F-B1) and CL-3 (§7) | F-B2 / F-B3 public API/ABI packages (§7.6), if ever needed |
| OD-1 option (o), a body-only release mitigation, never closure (§10) | R-1, the recursion-notice classification; D1 adds one site under A-GHOST-1 (§5.4) |
| Probes, controls and cost measurement under existing admission gates | campaign gates, deployment and installation |

## 5. Algorithm A: signed full-domain column comparison (run ledger)

### 5.1 Semantics matched exactly (unchanged references)

- `Q.Value (Data, X) = (if X.Negative then -Magnitude else Magnitude)`, with `Magnitude = 0` for an invalid span
  (`core/resource_quantities.ads:85-96`). An empty span is valid with value 0. Negative zero is 0. Leading-zero padding
  changes nothing.
- `Q.Digit (Data, X, K)` is the K-th little-endian byte when the span is valid and `K < X.Length`, else 0 (`:30-36`).
- `Amount_Reference`, `Included`, `Sum_Reference`, `Conserved_Reference`, `Contained_Reference` and the capacity
  conjunct of `Decision_Reference` are at `core/resource_run_ledger.ads:187-209, 236-263, 406-407`.
- **Signed identity [LEAD; PO-A8, PO-A13].**
  - Let L be the sum of the magnitudes of the selected operands whose sign flag is False, plus the target's magnitude
    when the target's flag is True.
  - Let R be the sum of the magnitudes of the selected operands whose flag is True, plus the target's magnitude when
    its flag is False.
  - Then `L - R = Σ Amount_Reference(selected) - Value(Target)`, so `Σ ≤ t ⟺ L ≤ R` and `Σ = t ⟺ L = R`.
  - Selection by sign flag needs no zero test. Negative zero and invalid spans contribute zero digits.

### 5.2 Representable types and conversions

```ada
--  UNCOMPILED / UNPROVED — core/resource_run_ledger.adb, body-private (packet D1-A)
   --  2**71 = 256 * ((2**63 - 1) + 1)                                   [K-12, K-54]
   type Column_Total is range 0 .. 2 ** 71;   --  needs a 128-bit base; an unsupporting target rejects the unit
   package Column_Big is new SPARK.Big_Integers.Signed_Conversions (Int => Column_Total)
     with Ghost;
   type Sum_Order is (Less, Equal, Greater);
   type Selection is (Held_Only, Budget_Only, Both_Kinds);
   type Side_Array is array (Boolean) of Column_Total;     --  index = sign flag of the side: False = L, True = R
   type Side_Low is array (Boolean) of Valid_Big_Integer with Ghost;
   type Term_Kind is (Prefix_Term, Digit_Term) with Ghost;
   Empty_Quantity : constant Q.Quantity := (Negative => False, First => 1, Length => 0);
```

Domain bounds:

- `Byte_Count'Last = 2**63 - 1` [K-11]. Rows are indexed by `Byte_Index` (`:49`), so `Rows'Length ≤ 2**63 - 1`.
- A side column holds at most `Carry + 255*(N+1) ≤ 256*(N+1) ≤ 2**71`; the bound is attained at the ceiling
  [K-52, K-54].
- 64 bits are insufficient [K-14]; a signed 128-bit base suffices [K-13].
- Every conversion is a PO-A0/A12 obligation:
  - `Column_Total (Q.Digit (…))`, range 0..255;
  - `Column_Total (J - Rows'First)`, at most `2**63 - 2`;
  - `Column_Total (Rows'Length) + 1`, at most `2**63`.
- `Rows'Length + 1` is never evaluated in `Byte_Count`. `Offset + 1` appears only in ghost text, where
  `Offset ≤ Columns - 1`.

### 5.3 Executable helpers: Post-free, with facts supplied by lemmas (DR-C1, scope corrected by F36)

The helpers are Post-free expression functions. Their bodies are visible to proof as implicit postconditions, and their
value-level facts are lemmas (LA-9, LA-10) called once per proof point (§5.6). This removes no original assertion.

**DR-C1's scope (F36).** DR-C1 removes only the helpers' **own** Posts. `Usage_Selected` calls `Q.Compare`, whose
original Post and checked body run on every call under `-gnata` (`core/resource_quantities.ads:107-117`,
`.adb:340-402`). §9.3.3 counts that work. §5.10 records a lead-owned alternative that avoids it.

```ada
--  UNCOMPILED / UNPROVED
   function Effective_Length (Data : Q.Byte_Array; Item : Q.Quantity) return Q.Byte_Count is
     (if Q.Span_Valid (Data, Item) then Item.Length else 0)
   with Global => null;

   function Normalized (Data : Q.Byte_Array; Item : Q.Quantity) return Q.Quantity is
     (if Q.Span_Valid (Data, Item) then Item else Empty_Quantity)
   with Global => null;

   function Usage_Selected (Data : Q.Byte_Array; Item : Row) return Boolean is
     (Item.Kind = Held_Capacity and then Item.Observed_Usage.Present
      and then Q.Compare (Data, Normalized (Data, Item.Observed_Usage.Value),
                                Normalized (Data, Item.Amount)) = Q.Greater)
   with Global => null;   --  reaches Q.Compare's checked Post and body (F36)

   function Operand (Data : Q.Byte_Array; Item : Row) return Q.Quantity is
     (if Usage_Selected (Data, Item) then Item.Observed_Usage.Value else Item.Amount)
   with Global => null;   --  the discriminant check is guarded by Usage_Selected's Present conjunct

   function Selected (Data : Q.Byte_Array; Item : Row; Parent : Identity;
                      Mode : Selection) return Boolean is
     (case Mode is
        when Held_Only   => Included (Data, Item, Parent, Held_Capacity),
        when Budget_Only => Included (Data, Item, Parent, Irreversible_Budget),
        when Both_Kinds  => Counted (Item)
          and then (if Parent.Present then Same (Data, Item.Parent, Parent)
                    else not Item.Parent.Present))
   with Global => null;
```

### 5.4 Ghost model: A-GHOST-1 (primary, one recursive function) and A-GHOST-0 (notice-free alternative)

```ada
--  UNCOMPILED / UNPROVED — ghost, body-private
   function Selected_Sum (Data : Q.Byte_Array; Rows : Row_Array; Count : Q.Byte_Count;
                          Parent : Identity; Mode : Selection) return Valid_Big_Integer is
     (case Mode is
        when Held_Only   => Sum_Reference (Data, Rows, Count, Parent, Held_Capacity),
        when Budget_Only => Sum_Reference (Data, Rows, Count, Parent, Irreversible_Budget),
        when Both_Kinds  => Sum_Reference (Data, Rows, Count, Parent, Held_Capacity)
                          + Sum_Reference (Data, Rows, Count, Parent, Irreversible_Budget))
   with Ghost, Global => null;                                   --  not recursive

   function Signed_Prefix_Value (Data : Q.Byte_Array; X : Q.Quantity) return Valid_Big_Integer is
     (if not Q.Span_Valid (Data, X) then To_Big_Integer (0)
      elsif X.Negative then -Q.Prefix_Reference (Data, X, X.Length)
      else Q.Prefix_Reference (Data, X, X.Length))
   with Ghost, Global => null;                                   --  not recursive; r(L) PRI (§9.3.1)

   function Row_Term (Data : Q.Byte_Array; Item : Row; Parent : Identity; Mode : Selection;
                      Side : Boolean; Term : Term_Kind; Column : Q.Byte_Count)
      return Valid_Big_Integer is
     (if Selected (Data, Item, Parent, Mode) and then Operand (Data, Item).Negative = Side then
        (case Term is
           when Prefix_Term => Q.Prefix_Reference (Data, Operand (Data, Item), Column),
           when Digit_Term  => To_Big_Integer (Q.Digit (Data, Operand (Data, Item), Column)))
      else To_Big_Integer (0))
   with Ghost, Global => null;                                   --  not recursive

   --  The ONLY new recursive function in D1 (A-GHOST-1). No Post. Expected installed notices
   --  [contracts-recursive] and [numeric-variant], by analogy with Sum_Reference (F20): an OPEN R-1-class obligation.
   function Side_Sum (Data : Q.Byte_Array; Rows : Row_Array; Count : Q.Byte_Count;
                      Parent : Identity; Mode : Selection; Side : Boolean;
                      Term : Term_Kind; Column : Q.Byte_Count) return Valid_Big_Integer is
     (if Count = 0 then To_Big_Integer (0)
      else Side_Sum (Data, Rows, Count - 1, Parent, Mode, Side, Term, Column)
           + (if Count <= Rows'Length
              then Row_Term (Data, Rows (Rows'First + (Count - 1)), Parent, Mode, Side, Term, Column)
              else To_Big_Integer (0)))
   with Ghost, Global => null, Subprogram_Variant => (Decreases => Count);

   function Target_Term (Data : Q.Byte_Array; Target : Q.Quantity; Side : Boolean;
                         Term : Term_Kind; Column : Q.Byte_Count) return Valid_Big_Integer is
     (if Target.Negative /= Side then
        (case Term is
           when Prefix_Term => Q.Prefix_Reference (Data, Target, Column),
           when Digit_Term  => To_Big_Integer (Q.Digit (Data, Target, Column)))
      else To_Big_Integer (0))
   with Ghost, Global => null;                                   --  not recursive

   function Side_Total (Data : Q.Byte_Array; Rows : Row_Array; Parent : Identity; Mode : Selection;
                        Target : Q.Quantity; Side : Boolean; Column : Q.Byte_Count)
      return Valid_Big_Integer is
     (Side_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode, Side, Prefix_Term, Column)
      + Target_Term (Data, Target, Side, Prefix_Term, Column))
   with Ghost, Global => null;                                   --  not recursive
```

`Side_Sum` with `Term => Digit_Term` replaces v2's `Side_Digits`.

**A-GHOST-0, the notice-free alternative (lead-owned switch, no API change).**

- Replace `Side_Sum` by the pinned `Sum_Reference` evaluated on ghost row arrays. Each array is built by a
  non-recursive iterated aggregate
  `[for J in Rows'Range => (Rows (J) with delta Amount => Truncated (Normalized (Data, Operand (Data, Rows (J))), C),
  Observed_Usage => (Present => False))]`.
- Track only the signed difference `L - R` in the invariants. `Truncated` keeps First and Negative and sets
  `Length => Byte_Count'Min (Length, C)`.
- No new notice site arises.
- **Cost, corrected (V3-RC3 b, V3-F4).** v3's "extra factor of about K" is withdrawn. Under A-GHOST-0 each selected
  row term at column extent `c` costs one `Amount_Reference` on the truncated row, that is one checked
  `Value` = `4·PV(c)` Power_Reference invocations (§9.3.1). Under A-GHOST-1 it costs one `Prefix_Reference` =
  `r(c)` invocations. The per-term ratio is `4·PV(c)/r(c) = (4/3)(c²+11c+12)` [PE-10]. For example: 32 at `c = 1`
  [K-163], 656/3 at `c = 8` [K-164], 2614616/3 at `c = 803` [K-165, K-173].
- A-GHOST-0 additionally builds an N-row ghost aggregate per evaluation (`N·ρ` bytes, `ρ = Row'Object_Size/8`;
  placement not established by source) and evaluates `Operand` (one checked `Compare` per Held usage row) per row per
  aggregate. These are static source counts (§9.3.3), not measurements.
- A-GHOST-0 replaces A-GHOST-1 if the operator's R-1 decision does not cover new D1 sites.

### 5.5 `Selected_Sum_Order` body (installed shape rules applied: F19, F21, F28)

```ada
--  UNCOMPILED / UNPROVED
   function Selected_Sum_Order
     (Data : Q.Byte_Array; Rows : Row_Array; Parent : Identity;
      Mode : Selection; Target : Q.Quantity) return Sum_Order
   with Global => null,
     Post => Selected_Sum_Order'Result =
       (if Selected_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode) < Q.Value (Data, Target)
        then Less
        elsif Selected_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode) = Q.Value (Data, Target)
        then Equal
        else Greater);

   function Selected_Sum_Order
     (Data : Q.Byte_Array; Rows : Row_Array; Parent : Identity;
      Mode : Selection; Target : Q.Quantity) return Sum_Order
   is
      Columns : Q.Byte_Count := Effective_Length (Data, Target);
      Carry   : Side_Array := [others => 0];
      Column  : Side_Array;                       --  hoisted (F19); assigned before every read
      Before  : Side_Array with Ghost;            --  hoisted (F19)
      Op      : Q.Quantity;                       --  hoisted (F19); no ineffective initialization (F21)
      State   : Sum_Order := Equal;
      Low     : Side_Low := [others => To_Big_Integer (0)] with Ghost;
   begin
      --  (1) Column extent over the target and both candidate operands of every selected row.
      for J in Rows'Range loop
         if Selected (Data, Rows (J), Parent, Mode) then
            Columns := Q.Byte_Count'Max (Columns, Effective_Length (Data, Rows (J).Amount));
            if Rows (J).Observed_Usage.Present then
               Columns := Q.Byte_Count'Max
                 (Columns, Effective_Length (Data, Rows (J).Observed_Usage.Value));
            end if;
         end if;
         pragma Loop_Invariant (Effective_Length (Data, Target) <= Columns);
         pragma Loop_Invariant
           (for all K in Rows'First .. J =>
              (if Selected (Data, Rows (K), Parent, Mode) then
                 Effective_Length (Data, Rows (K).Amount) <= Columns
                 and then (if Rows (K).Observed_Usage.Present then
                             Effective_Length (Data, Rows (K).Observed_Usage.Value) <= Columns)));
      end loop;

      if Columns = 0 then
         Lemma_Zero_Extent (Data, Rows, Parent, Mode, Target);          --  LA-11
         return Equal;
      end if;

      --  (2) Original columns 0 .. Columns - 1 only. No carry-draining column is formed.
      for Offset in 0 .. Columns - 1 loop
         Column := Carry;
         Before := Carry;                                                --  ghost
         Column (not Target.Negative) :=
           Column (not Target.Negative) + Column_Total (Q.Digit (Data, Target, Offset));
         for J in Rows'Range loop
            --  O(1) length test first: a row whose candidates both end at or before Offset adds digit 0.
            if (Offset < Effective_Length (Data, Rows (J).Amount)
                or else (Rows (J).Observed_Usage.Present
                         and then Offset < Effective_Length (Data, Rows (J).Observed_Usage.Value)))
              and then Selected (Data, Rows (J), Parent, Mode)
            then
               Op := Operand (Data, Rows (J));
               Column (Op.Negative) := Column (Op.Negative) + Column_Total (Q.Digit (Data, Op, Offset));
            end if;
            pragma Loop_Invariant
              (for all S in Boolean =>
                 Column (S) <= Before (S) + 255 * (Column_Total (J - Rows'First) + 2));
            pragma Loop_Invariant
              (for all S in Boolean =>
                 Column_Big.To_Big_Integer (Column (S))
                 = (Column_Big.To_Big_Integer (Before (S))
                    + Target_Term (Data, Target, S, Digit_Term, Offset))
                   + Side_Sum (Data, Rows, Q.Byte_Count (J - Rows'First) + 1,
                               Parent, Mode, S, Digit_Term, Offset));
         end loop;
         Lemma_Column_Step (Data, Rows, Parent, Mode, Target, Offset);   --  LA-1, LA-2 (both sides)
         Lemma_Column_Emit (Low (False), Q.Power_Reference (Offset), Column (False));   --  LA-3
         Lemma_Column_Emit (Low (True),  Q.Power_Reference (Offset), Column (True));
         if Column (False) mod 256 < Column (True) mod 256 then
            State := Less;
         elsif Column (False) mod 256 > Column (True) mod 256 then
            State := Greater;
         end if;                                                         --  equal digits keep State (LA-4)
         Low (False) := Low (False)
           + Column_Big.To_Big_Integer (Column (False) mod 256) * Q.Power_Reference (Offset);     --  ghost
         Low (True) := Low (True)
           + Column_Big.To_Big_Integer (Column (True) mod 256) * Q.Power_Reference (Offset);      --  ghost
         Carry (False) := Column (False) / 256;
         Carry (True)  := Column (True) / 256;
         pragma Loop_Invariant (for all S in Boolean => Carry (S) <= Column_Total (Rows'Length) + 1);
         pragma Loop_Invariant
           (for all S in Boolean => Low (S) >= 0 and then Low (S) < Q.Power_Reference (Offset + 1));
         pragma Loop_Invariant
           (for all S in Boolean =>
              Side_Total (Data, Rows, Parent, Mode, Target, S, Offset + 1)
              = Low (S) + Column_Big.To_Big_Integer (Carry (S)) * Q.Power_Reference (Offset + 1));
         pragma Loop_Invariant
           (State = (if Low (False) < Low (True) then Less
                     elsif Low (False) = Low (True) then Equal else Greater));
      end loop;

      --  (3) Closing theorem; completion; signed identity.
      Lemma_Close (Data, Rows, Parent, Mode, Target, Columns, Low, Carry, State);   --  LA-5, LA-7, LA-8
      if Carry (False) > Carry (True) then
         return Greater;
      elsif Carry (False) < Carry (True) then
         return Less;
      else
         return State;
      end if;
   end Selected_Sum_Order;
```

Shape rules applied:

- No declaration appears in any loop body, and every invariant follows statements only (F19).
- No initialization is ineffective (F21).
- Mixed additive chains are left-associated with explicit parentheses (F28).
- Ghost assignments to `Low` and `Before` are ghost statements inside executable code.

The largest radix power this body's ghost forms is `Q.Power_Reference (Columns)`, where `Columns` is the largest
effective length among the target and the selected operands. That horizon is discussed in §5.11.

Loop induction, in the guide's frame (`SK/spark-users-guide/chapters/ch23-loop-invariants.md`):

- **INIT.**
  - Inner loop: before row `Rows'First`, `Column = Before + target digit` and `Side_Sum (…, 0, …) = 0`.
  - Outer loop: before column 0, `Low = 0`, `Carry = 0`, `Power_Reference (0) = 1`, and `Side_Total (…, 0) = 0`,
    because every `Prefix_Reference (·, 0) = 0`.
- **INSIDE.** The row bound keeps every addition inside `Column_Total` (PO-A12, [K-52]). Indexing is within
  `Rows'Range`. `Operand`'s variant access is guarded.
- **PRESERVE.**
  - Inner: one row adds `Row_Term (…, Digit_Term, Offset)` to exactly one side; `Side_Sum` unfolds by one row.
  - Outer: LA-1 and LA-2 give `Side_Total (Offset + 1) = Side_Total (Offset) + (Column - Before) * P(Offset)`. With
    the previous invariant this becomes `Low + Column * P(Offset)`. LA-3 splits it into
    `Low' + Carry' * P(Offset + 1)` with `0 ≤ Low' < P(Offset + 1)`. LA-4 updates `State`.
- **AFTER.** At `Offset = Columns - 1`:
  - `Side_Total (S, Columns) = Low (S) + Carry (S) * P(Columns)`;
  - LA-7 and LA-8 give `Side_Total (False, Columns) - Side_Total (True, Columns) = Selected_Sum - Value (Target)`;
  - LA-5 decides the sign from the carries, else from `State`.

### 5.6 Lemma procedures for Algorithm A: explicit contracts and proof plans

All of them are `Ghost`, `Global => null` and `Always_Terminates`, with full bodies. None is imported, assumed or
justified. Induction over an unbounded count (rows or columns) is **iterative**: a loop with invariants, never
recursion (DR-C3). Their checked costs are counted in §9.3.3.

```ada
--  UNCOMPILED / UNPROVED — contracts; bodies are described after the block
   procedure Lemma_Column_Step                                           --  LA-1 + LA-2
     (Data : Q.Byte_Array; Rows : Row_Array; Parent : Identity; Mode : Selection;
      Target : Q.Quantity; Offset : Q.Byte_Count)
   with Pre  => Offset < Q.Byte_Count'Last,
        Post => (for all S in Boolean =>
                   Side_Total (Data, Rows, Parent, Mode, Target, S, Offset + 1)
                   = Side_Total (Data, Rows, Parent, Mode, Target, S, Offset)
                     + (Side_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode, S, Digit_Term, Offset)
                        + Target_Term (Data, Target, S, Digit_Term, Offset))
                       * Q.Power_Reference (Offset));

   procedure Lemma_Column_Emit (Low, P : Valid_Big_Integer; Column : Column_Total)       --  LA-3
   with Pre  => P > 0 and then Low >= 0 and then Low < P,
        Post => Low + Column_Big.To_Big_Integer (Column) * P
                = (Low + Column_Big.To_Big_Integer (Column mod 256) * P)
                  + Column_Big.To_Big_Integer (Column / 256) * (To_Big_Integer (256) * P)
                and then Low + Column_Big.To_Big_Integer (Column mod 256) * P >= 0
                and then Low + Column_Big.To_Big_Integer (Column mod 256) * P < To_Big_Integer (256) * P;

   procedure Lemma_Order_Extension                                       --  LA-4 (E-3: relational Pre)
     (Low_L, Low_R, P : Valid_Big_Integer; D_L, D_R : Natural)
   with Pre  => P > 0 and then Low_L >= 0 and then Low_L < P and then Low_R >= 0 and then Low_R < P
                and then D_L <= 255 and then D_R <= 255,
        Post => (if D_L > D_R then Low_L + To_Big_Integer (D_L) * P > Low_R + To_Big_Integer (D_R) * P)
                and then (if D_L < D_R then Low_L + To_Big_Integer (D_L) * P < Low_R + To_Big_Integer (D_R) * P)
                and then (if D_L = D_R then
                            (Low_L + To_Big_Integer (D_L) * P < Low_R + To_Big_Integer (D_R) * P) = (Low_L < Low_R)
                            and then (Low_L + To_Big_Integer (D_L) * P = Low_R + To_Big_Integer (D_R) * P)
                                     = (Low_L = Low_R));

   procedure Lemma_Residual_Carry_Order                                  --  LA-5
     (Low_L, Low_R, P : Valid_Big_Integer; C_L, C_R : Column_Total)
   with Pre  => P > 0 and then Low_L >= 0 and then Low_L < P and then Low_R >= 0 and then Low_R < P,
        Post => (if C_L > C_R then Low_L + Column_Big.To_Big_Integer (C_L) * P
                                   > Low_R + Column_Big.To_Big_Integer (C_R) * P)
                and then (if C_L < C_R then Low_L + Column_Big.To_Big_Integer (C_L) * P
                                            < Low_R + Column_Big.To_Big_Integer (C_R) * P);

   procedure Lemma_Carry_Bound (Before_Carry, Column : Column_Total; Rows_Count : Q.Byte_Count)   --  LA-6
   with Pre  => Before_Carry <= Column_Total (Rows_Count) + 1
                and then Column <= Before_Carry + 255 * (Column_Total (Rows_Count) + 1),
        Post => Column / 256 <= Column_Total (Rows_Count) + 1;

   procedure Lemma_Signed_Completion                                     --  LA-7
     (Data : Q.Byte_Array; Rows : Row_Array; Parent : Identity; Mode : Selection; Columns : Q.Byte_Count)
   with Pre  => (for all K in Rows'Range =>
                   (if Selected (Data, Rows (K), Parent, Mode) then
                      Effective_Length (Data, Rows (K).Amount) <= Columns
                      and then (if Rows (K).Observed_Usage.Present then
                                  Effective_Length (Data, Rows (K).Observed_Usage.Value) <= Columns))),
        Post => Selected_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode)
                = Side_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode, False, Prefix_Term, Columns)
                  - Side_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode, True, Prefix_Term, Columns);

   procedure Lemma_Target_Completion (Data : Q.Byte_Array; Target : Q.Quantity; Columns : Q.Byte_Count)   --  LA-8
   with Pre  => Effective_Length (Data, Target) <= Columns,
        Post => Q.Value (Data, Target)
                = Target_Term (Data, Target, True, Prefix_Term, Columns)
                  - Target_Term (Data, Target, False, Prefix_Term, Columns);

   procedure Lemma_Operand (Data : Q.Byte_Array; Item : Row)                         --  LA-9
   with Post => Q.Span_Valid (Data, Normalized (Data, Item.Amount))
                and then Q.Value (Data, Normalized (Data, Item.Amount)) = Q.Value (Data, Item.Amount)
                and then (if Item.Observed_Usage.Present then
                            Q.Value (Data, Normalized (Data, Item.Observed_Usage.Value))
                            = Q.Value (Data, Item.Observed_Usage.Value))
                and then Usage_Selected (Data, Item)
                         = (Item.Kind = Held_Capacity and then Item.Observed_Usage.Present
                            and then Q.Value (Data, Item.Observed_Usage.Value) > Q.Value (Data, Item.Amount))
                and then (if Counted (Item) then
                            Q.Value (Data, Operand (Data, Item)) = Amount_Reference (Data, Item))
                and then Signed_Prefix_Value (Data, Operand (Data, Item)) = Q.Value (Data, Operand (Data, Item));

   procedure Lemma_Selected_Step                                         --  LA-10
     (Data : Q.Byte_Array; Rows : Row_Array; Count : Q.Byte_Count; Parent : Identity; Mode : Selection)
   with Pre  => Count < Rows'Length,
        Post => Selected_Sum (Data, Rows, Count + 1, Parent, Mode)
                = Selected_Sum (Data, Rows, Count, Parent, Mode)
                  + (if Selected (Data, Rows (Rows'First + Count), Parent, Mode)
                     then Amount_Reference (Data, Rows (Rows'First + Count)) else To_Big_Integer (0));

   procedure Lemma_Zero_Extent                                           --  LA-11
     (Data : Q.Byte_Array; Rows : Row_Array; Parent : Identity; Mode : Selection; Target : Q.Quantity)
   with Pre  => Effective_Length (Data, Target) = 0
                and then (for all K in Rows'Range =>
                            (if Selected (Data, Rows (K), Parent, Mode) then
                               Effective_Length (Data, Rows (K).Amount) = 0
                               and then (if Rows (K).Observed_Usage.Present then
                                           Effective_Length (Data, Rows (K).Observed_Usage.Value) = 0))),
        Post => Selected_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode) = 0
                and then Q.Value (Data, Target) = 0;

   procedure Lemma_Close (Data : Q.Byte_Array; Rows : Row_Array; Parent : Identity; Mode : Selection;
                          Target : Q.Quantity; Columns : Q.Byte_Count;
                          Low : Side_Low; Carry : Side_Array; State : Sum_Order)   --  LA-5, LA-7, LA-8 combined
   with Pre  => Columns > 0
                and then <the pre-pass coverage of LA-7 and LA-8 at Columns>
                and then (for all S in Boolean =>
                            Low (S) >= 0 and then Low (S) < Q.Power_Reference (Columns)
                            and then Side_Total (Data, Rows, Parent, Mode, Target, S, Columns)
                                     = Low (S) + Column_Big.To_Big_Integer (Carry (S)) * Q.Power_Reference (Columns))
                and then State = (if Low (False) < Low (True) then Less
                                  elsif Low (False) = Low (True) then Equal else Greater),
        Post => (if Carry (False) > Carry (True) then
                   Selected_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode) > Q.Value (Data, Target)
                 elsif Carry (False) < Carry (True) then
                   Selected_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode) < Q.Value (Data, Target)
                 else
                   (State = Less) = (Selected_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode)
                                     < Q.Value (Data, Target))
                   and then (State = Equal) = (Selected_Sum (Data, Rows, Q.Byte_Count (Rows'Length), Parent, Mode)
                                              = Q.Value (Data, Target)));
```

`<the pre-pass coverage …>` stands for LA-7's Pre at `Columns` together with
`Effective_Length (Data, Target) <= Columns`, written out in full in the packet. It is the pre-pass loop's exit fact.

Body plans [LEAD; each is a proof obligation]:

- **LA-1/LA-2.** An iterative loop over `K in 0 .. Rows'Length - 1` with, for both sides, the invariant
  `Side_Sum (K + 1, Prefix, Offset + 1) = Side_Sum (K + 1, Prefix, Offset) + Side_Sum (K + 1, Digit, Offset) * P(Offset)`.
  Each step unfolds `Side_Sum` by one row and `Prefix_Reference (Op, Offset + 1)` by one level
  (`core/resource_quantities.ads:47-56`). The target term is one unfolding.
- **LA-3.** `T = T mod 256 + 256 * (T / 256)` for nonnegative T, then the `Column_Bounds` pattern
  (`core/resource_quantities.adb:41-64`), copied because body-private lemmas are not visible across packages.
- **LA-4.** The `Higher_Column_Order` pattern (`:66-92`), plus the equal-digit case. E-3 is incorporated: the Pre uses
  relational operators, because a range membership on the private type `Big_Integer` is not legal Ada.
- **LA-5.** If `C_L ≥ C_R + 1`, then `Low_L + C_L * P ≥ C_R * P + P > Low_R + C_R * P`; symmetric for `<`. The bounds
  use `Scale_Column`-style accumulation (`:15-39`).
- **LA-6.** `(c + 255 * m) / 256 ≤ m` when `c ≤ m`.
- **LA-7.** An iterative loop over rows. Per row it uses LA-10, LA-9 and the padding fact
  `Prefix_Reference (X, Columns) = Magnitude (X)` for a valid X with `Length ≤ Columns`, which is a copy of
  `Prefix_Padding` (`:278-296`). An invalid span gives 0 on both sides through `Digit = 0`. It also uses the sign
  split `Value = ±Magnitude`.
- **LA-8.** The same padding fact for the target, and the sign case.
- **LA-9.** `Compare`'s Post on two valid spans (`:106-117`), `Normalized`'s body, `Magnitude`'s Post, and
  `Prefix_Value`'s Post `= Prefix_Reference` (`:69-83`).
- **LA-10.** One unfolding of the pinned `Sum_Reference` for each kind. For `Both_Kinds`, the two-valued
  `Charge_Kind` partition makes exactly one `Included` hold for a selected row (`core/resource_run_ledger.ads:36, 195-199`).
- **LA-11.** LA-7 and LA-8 at `Columns = 0`. Every `Prefix_Reference (·, 0) = 0`.

### 5.7 `Pair_Sum_Order` and Check's capacity branch

```ada
--  UNCOMPILED / UNPROVED
   function Pair_Sum_Order
     (Data : Q.Byte_Array; First_Addend, Second_Addend, Target : Q.Quantity) return Sum_Order
   with Global => null,
     Post => Pair_Sum_Order'Result =
       (if Q.Value (Data, First_Addend) + Q.Value (Data, Second_Addend) < Q.Value (Data, Target) then Less
        elsif Q.Value (Data, First_Addend) + Q.Value (Data, Second_Addend) = Q.Value (Data, Target) then Equal
        else Greater);
   --  Body: the §5.5 engine with three fixed operands and no row loop.
   --    Columns := maximum of the three Effective_Length values; Columns = 0 => Equal.
   --    Per column: Column (First.Negative)      += Digit (First, Offset);
   --                Column (Second.Negative)     += Digit (Second, Offset);
   --                Column (not Target.Negative) += Digit (Target, Offset).
   --    A side holds at most 3 digits: Column <= 3*255 + 2 = 2*256 + 255, so Carry <= 2   [K-17]
   --    Ghost model: Pair_Side_Total (S, C) = sum of the three Prefix terms on side S. Not recursive.
   --    Lemmas LA-3..LA-6 and the padding facts of LA-8.

   --  Check, capacity branch (core/resource_run_ledger.adb:173-174). Every other branch is byte-identical.
      elsif Pair_Sum_Order (Data, Proposed.Held_Total, Proposed.Charged_Total,
                            Proposed.Capacity) = Greater then Capacity_Exceeded
```

By its Post and on every input, `Pair_Sum_Order (…) = Greater` equals `Decision_Reference`'s capacity conjunct
(`core/resource_run_ledger.ads:406-407`). Branch order and statuses are unchanged (PO-A17, PO-A19). `Capacity_Fits`
stays rejected as primary: it is correct only under the `Shape` path condition.

### 5.8 `Conserved` and `Contained`

```ada
--  UNCOMPILED / UNPROVED — specs and Posts unchanged (core/resource_run_ledger.ads:244-246, 264-265)
   function Conserved (Data : Q.Byte_Array; State : Ledger_State; Rows : Row_Array)
      return Boolean is
     (Shape (Data, State, Rows)
      and then Selected_Sum_Order (Data, Rows, (Present => False), Held_Only,
                                   State.Held_Total) = Equal
      and then Selected_Sum_Order (Data, Rows, (Present => False), Budget_Only,
                                   State.Charged_Total) = Equal);

   function Contained (Data : Q.Byte_Array; Rows : Row_Array) return Boolean is
   begin
      for I in Rows'Range loop                     --  loop 1: byte-identical to :72-79
         pragma Loop_Invariant (for all K in Rows'Range => (if K < I then
           (if Rows (K).Parent.Present then (for some J in Rows'Range => J < K
             and then Parent_Supports (Data, Rows (J), Rows (K))))));
         if Rows (I).Parent.Present and then not
           (for some J in Rows'Range => J < I and then Parent_Supports (Data, Rows (J), Rows (I)))
         then return False; end if;
      end loop;
      for I in Rows'Range loop                     --  loop 2: invariant byte-identical to :81-84
         pragma Loop_Invariant (for all K in Rows'Range => (if K < I then
           Sum_Reference (Data, Rows, Rows'Length, Rows (K).Bound.Reservation, Held_Capacity)
           + Sum_Reference (Data, Rows, Rows'Length, Rows (K).Bound.Reservation, Irreversible_Budget)
           <= Q.Value (Data, Rows (K).Amount)));
         if Selected_Sum_Order (Data, Rows, Rows (I).Bound.Reservation, Both_Kinds,
                                Rows (I).Amount) = Greater
         then return False; end if;
      end loop;
      return True;
   end Contained;
```

- `= Equal` is `Value (Total) = Sum_Reference (…)` by the Post and the symmetry of `=`. That is
  `Conserved_Reference`, including Shape's False branch.
- `= Greater` is the negation of `S_H + S_B ≤ Value (Rows (I).Amount)`. It covers every target row and all signed,
  invalid and duplicate-identity inputs.
- Per-kind inequalities are not used; the aggregate is decided directly (PO-A15, PO-A16).

### 5.9 Termination and the terminal carry at the Byte_Count ceiling

- Every loop is a `for` loop over a finite range, so termination is structural.
- No column index at or beyond `Columns` is formed. The terminal carry is decided by LA-5 with `Low < 256**Columns` on
  both sides.
- `Side_Sum` has `Subprogram_Variant (Decreases => Count)`. It is the only new recursion. Every lemma is iterative and
  carries a `Loop_Variant` where it uses `while`.

### 5.10 A-SEL-L: recorded lead-owned cost-shaping alternative (not selected)

**Purpose.** To remove the dominant D1-added checked term of §9.3.3, which is `Q.Compare` evaluated through
`Usage_Selected`/`Operand` in executable code and ghost row terms (F36), without changing any public contract,
reference or domain.

**Shape (UNCOMPILED / UNPROVED).**

```ada
   --  Contract-free executable comparison of the normalized usage and amount spans.
   function Usage_Exceeds (Data : Q.Byte_Array; Item : Row) return Boolean
   with Global => null;
   --  Body: U := Normalized (Data, Item.Observed_Usage.Value); M := Normalized (Data, Item.Amount);
   --  zero-aware signs (a span is zero iff all its digits are 0: a contract-free loop over Q.Digit),
   --  then an MSB-first digit comparison over Count := max (Effective_Length (U), Effective_Length (M)),
   --  with integer-only loop invariants. No Post.

   --  Usage_Selected then reads:
   --    Item.Kind = Held_Capacity and then Item.Observed_Usage.Present and then Usage_Exceeds (Data, Item)

   procedure Lemma_Usage_Exceeds (Data : Q.Byte_Array; Item : Row)          --  LA-9L
   with Ghost, Global => null, Always_Terminates,
     Pre  => Item.Kind = Held_Capacity and then Item.Observed_Usage.Present,
     Post => Usage_Exceeds (Data, Item)
             = (Q.Value (Data, Item.Observed_Usage.Value) > Q.Value (Data, Item.Amount));
   --  Body: the Compare-body pattern (padding facts, Prefix_Bounds, Higher_Column_Order) written as an iterative
   --  ghost proof with Prefix_Reference-based invariants (DR-C2); called once per row inside LA-7's row loop.
```

**Effect (static).**

- `Q.Compare` disappears from D1's executable path and ghost row terms.
- The `12uNK` Compare term of §9.3.3 is replaced by `N` calls of LA-9L per `Selected_Sum_Order` call, each with an
  O(L) loop over Prefix_Reference invariants (about `L·r(L)` invocations).
- Release cost per call stays O(L), the same order as `Compare`'s body.
- `Q.Compare` is unchanged and still used by `Shape`, `Same_Row` and `Changed_Row_Allowed`.

**Obligations if selected.**

- PO-A25: LA-9L, proved.
- PO-A2 restated with LA-9L.
- The probes of §7.3 for the new function.
- A separate GPT-6.1 review of the swap.

The lead may select it after the probes. Nothing is selected in v4.

### 5.11 F35: representation-horizon hazard of the one-sided ghost sums (OPEN)

- **Statement [LEAD].**
  - The ghost terms of §5.4 and §5.5 form one-sided sums: `Side_Total (S, c)` sums the magnitudes of every selected
    operand on side `S`.
  - The original checked path forms signed partial sums in row order (`Sum_Reference`, `Sum`), and each operand's
    value.
  - On the Check path, `Shape` makes every operand nonnegative (negative zero has magnitude 0). One-sided sums then
    equal the original sums, so D1's ghost horizon equals the original's.
  - On direct-Ada calls of `Contained` with signed operands, the one-sided sums can exceed every value the original
    path forms.
- **Exhibit (RL-24, §12.3).**
  - A parent with amount 0 and 514 Held children [K-184] alternating `+X, -X`, where `X = 2**6424 - 1`: 803 bytes, all
    FF [K-188].
  - The original partial sums alternate between `X` and 0 [K-186, K-187], and each `Q.Value (X)` forms at most
    `256**803` (F1). The original therefore completes, returning False because the negative children fail their own
    targets.
  - D1's L-side ghost sum of 257 magnitudes exceeds `2**6432` [K-183, K-185]. It raises in the checks build.
  - The release build is unaffected: carries are `Column_Total`.
- **Status.** This is a D1-introduced checked-build failure class on admitted inputs. It is an OPEN D1-specific O-GHOST
  item (O-GHOST-HORIZON-A).
- **Candidate directions (recorded, not selected).**
  - A-GHOST-2: a signed-net ghost model that never states one-sided totals, tracking `L - R` per column with bounded
    low parts. The horizon of its truncated signed partial sums still needs an argument; none is claimed.
  - OD-1 (ii), where the limit disappears and the hazard becomes cost only.
  - Any route must preserve every original contract and the full domain.
- **Not eligible.** Restricting the domain, a Pre, or treating the failure as a refusal.

## 6. Algorithm B: `Integer_Matches` (canonical artifacts)

### 6.1 The original guard is preserved byte-identically

C5 `core/canonical_artifacts.adb:439-445`, unchanged:

```ada
      if not N.Valid or else N /= Prefix (A, J, 0) or else N.Form /= Integer_Value
        or else N.After /= J.Length or else not B.Valid
        or else not Sign.Valid or else Sign.Form /= Boolean_Value
        or else (Negative /= Match (A, T, Sign.First, "true"))
        or else (B.Length > 0 and then Binary_At (A, T, B, B.Length - 1) = 0)
        or else (Negative and then B.Length = 0)
      then return False; end if;
```

- `B` and `Negative` keep their declarations (`:433-434`). Every False the guard returns is the original False.
- No storage is allocated before the guard.
- Tagged-binary padding is excluded by the guard's top-byte test, which is distinct from the leading-zero padding legal
  in `Resource_Quantities`.
- An empty magnitude with a positive decimal (for example `"7"` with `""`) **passes** the guard and reaches the
  overflow decision with a null Work (§12.4 IM-6; review note).

### 6.2 Internal shape contract (V2-RC1; unchanged)

The work representation is a 1-based `P.Bytes (1 .. B.Length)`, with the carry out of the top cell returned as a
scalar. `P.Bytes` is `Resource_Quantities.Byte_Array` (`core/evaluation_pending.ads:9-11`), so its value is given by
the pinned `Q.Prefix_Reference`. No index `B.Length + 1` is ever formed.

| Shape fact | Statement | Established by | Used by |
|---|---|---|---|
| S1 | `Work'First = 1` | the allocator's bounds `1 .. B.Length` (§6.6), or CL-2's declaration | Pre of `Multiply_Add`, `Decide_Work` and `Work_Value` |
| S2 | `Count (Work'Length) = B.Length`. Null when `B.Length = 0` | the same | `Decide_Work` Pre; sizing |
| S3 | every cell is 0 initially | the aggregate `[1 .. B.Length => 0]` | `Decide_Work` Pre; INIT |
| S4 | no contract or assertion indexes Work outside `Work'Range` | each quantifier ranges over `Work'Range` or `Work'First .. I` with `I in Work'Range`; unguarded uses are only `'First`, `'Last` and `'Length` | PO-B16 |
| S5 | bounds never change | `in out` actuals keep their bounds | — |
| S6 | there is no sentinel cell. Overflow is `Carry_Out /= 0` from `Multiply_Add` | §6.4 | PO-B8 |

A null `Work` is therefore a legal shape that no contract indexes. `Multiply_Add` on a null `Work` returns
`Carry_Out = Digit_Value`. B-SHAPE-S (v2's sentinel with a nonempty Pre) stays recorded and not selected. The public
domain is unchanged: `Integer_Matches` is body-private; `Tagged_Matches` and the other public subprograms get no Pre;
`Prefix` gets a Post conjunct only (§6.3).

### 6.3 Proof interface for digit bytes: D-B-PREFIX (primary, R-PREFIX; unchanged)

```ada
--  UNCOMPILED / UNPROVED — core/canonical_artifacts.ads (ADDITIVE)
   function Integer_Token (A : Bytes; S : Span; From, After : Count) return Boolean is
     (P.Valid (A, S) and then From < After and then After <= S.Length
      and then (for all K in From .. After - 1 =>
                  (K = From and then A (S.First + K) = Character'Pos ('-'))
                  or else A (S.First + K) in Character'Pos ('0') .. Character'Pos ('9')))
   with Ghost, Global => null;

   function Prefix (A : Bytes; S : Span; From : Count) return Node
     with Global => null,
       Post => (if Prefix'Result.Valid then
         P.Valid (A, S) and then Prefix'Result.First = From
         and then From < Prefix'Result.After
         and then Prefix'Result.After <= S.Length
         and then Prefix'Result.Form /= Invalid_Value)
         and then (if Prefix'Result.Valid and then Prefix'Result.Form = Integer_Value
                   then Integer_Token (A, S, From, Prefix'Result.After)),           --  ADDED conjunct
       Subprogram_Variant => (Decreases => S.Length - Count'Min (From, S.Length));
```

Body obligations on the integer path (C5 `core/canonical_artifacts.adb:216-234`; PO-B1):

- Add `pragma Loop_Invariant (Integer_Token (A, S, From, O));` to the digit loop at `:228-232`, after the existing
  invariant at `:229`.
- INIT: `[-]d` scans an optional `'-'` at `From`, then `'1'..'9'` (`:217-226`); `"0"` returns `After = O + 1`
  (`:222-224`).
- PRESERVE: the loop condition at `:228` makes `Byte_At (A, S, O)` a digit, and `Byte_At` equals `A (S.First + O)`
  when `P.Valid` and `O < S.Length` (`:11-15`).
- Non-integer paths return another `Form` or an invalid node, so the conjunct is vacuous there.
- `A (S.First + K)` is in range: `P.Valid (A, S)` and `K < S.Length` give `S.First + K ≤ A'Last`.
- The existing `[contracts-recursive]` notice on `Prefix` (F20) is unchanged; the new conjunct is used only at
  non-recursive call sites.

`Binary_At` (body-private, no contract today) gains `Post => Binary_At'Result <= 255` (PO-B3). The three cases give at
most 255 [K-49, K-50, K-51]. `B64_Digit ≤ 63` by its expression (`:287-292`); negative digits return 0 early.

Digits in `Decide_Work`: `N = Prefix (A, J, 0)` is valid with `First = 0` (Post), and the guard gives
`N.After = J.Length`. The conjunct yields `Integer_Token (A, J, 0, N.After)`. If `Negative`, then `Start = 1` and only
`K = 0` may be `'-'`; otherwise all bytes are digits. Hence `Decide_Work`'s digit Pre holds (PO-B2).

### 6.4 `Multiply_Add`: one decimal digit, cell-wise carries; DR-C5 radix horizon

**DR-C5 (new in v4; F34).**

- On every path on which the original statements form no value ≥ `256**n` (`n = B.Length`), no D1-B ghost
  expression may evaluate `Power_Reference (n)`, nor form any value ≥ `256**n`.
- Concretely, every D1 contract or assertion that mentions `P(n)` or `(V+1)·P(k)` is written so that `256**n` is formed
  only when a carry out of cell `n` exists.
- When it does, the ghost decimal value, which is the original statement's value, is already ≥ `256**n`.
- DR-C5 changes no original statement, guard, profile or public contract.
- It is checked by PO-B22. Its effect on cost is a reduction: §9.3.4 counts remain upper bounds.

The Post below also places `'Old` in the **first** operand of `and then` and outside the conditional expression.
`Work_Value (Work)` does not statically name an entity, so an `'Old` in a potentially unevaluated position (a
short-circuit right operand or a conditional dependent) would fall under the RM 6.1.1 rule for potentially unevaluated
`'Old`. v3's form had `'Old` in the right operand of `and then`; v4 reorders it. Installed legality is probe PO-X1.

```ada
--  UNCOMPILED / UNPROVED — core/canonical_artifacts.adb, body-private (packet D1-B)
   package RQ renames Resource_Quantities;   --  added "with Resource_Quantities;" (P already depends on it)

   function Work_Value (W : P.Bytes) return Valid_Big_Integer is
     (RQ.Prefix_Reference (W, (Negative => False, First => 1, Length => Count (W'Length)),
                           Count (W'Length)))
   with Ghost, Global => null, Pre => W'First = 1;                --  not recursive itself; forms at most P(n-1)

   subtype Carry_Digit is Natural range 0 .. 9;
   type Carry_Vector is array (P.Index range <>) of Carry_Digit with Ghost;

   procedure Multiply_Add (Work : in out P.Bytes; Digit_Value : Natural; Carry_Out : out Natural)
   with Global => null, Always_Terminates,
     Pre  => Work'First = 1 and then Digit_Value <= 9,           --  shape only; null Work admitted; no indexing
     Post => To_Big_Integer (10) * Work_Value (Work)'Old + To_Big_Integer (Digit_Value)
               = (if Carry_Out = 0 then Work_Value (Work)             --  DR-C5: no P(n) without a carry
                  else Work_Value (Work)
                       + To_Big_Integer (Carry_Out) * RQ.Power_Reference (Count (Work'Length)))
             and then Carry_Out <= 9;

   procedure Multiply_Add (Work : in out P.Bytes; Digit_Value : Natural; Carry_Out : out Natural) is
      Old_Work : constant P.Bytes := Work with Ghost;               --  checks builds only: n bytes (§9.3.5)
      Carry_In : Carry_Vector (Work'Range) := [others => 0] with Ghost;   --  checks builds only (§9.3.5)
      Carry    : Carry_Digit := Digit_Value;
      Column   : Natural;
   begin
      for I in Work'Range loop
         Carry_In (I) := Carry;                                     --  ghost
         Column := 10 * Natural (Work (I)) + Carry;                 --  <= 10*255 + 9 = 2559          [K-16]
         Work (I) := P.Byte (Column mod 256);
         Carry := Column / 256;                                     --  2559 = 9*256 + 255 => <= 9    [K-15]
         pragma Loop_Invariant (for all K in Work'Range => (if K > I then Work (K) = Old_Work (K)));
         pragma Loop_Invariant (Carry_In (Work'First) = Digit_Value);
         pragma Loop_Invariant
           (for all K in Work'First .. I =>
              Natural (Work (K)) = (10 * Natural (Old_Work (K)) + Carry_In (K)) mod 256
              and then (if K < I
                        then Carry_In (K + 1) = (10 * Natural (Old_Work (K)) + Carry_In (K)) / 256
                        else Carry = (10 * Natural (Old_Work (K)) + Carry_In (K)) / 256));
      end loop;
      Lemma_Multiply_Add_Value (Old_Work, Work, Carry_In, Digit_Value, Carry);   --  LB-5
      Carry_Out := Carry;
   end Multiply_Add;

   function Next_Carry (Carry_In : Carry_Vector; C_Out : Natural; I : P.Index) return Natural is
     (if I < Carry_In'Last then Carry_In (I + 1) else C_Out)
   with Ghost, Global => null, Pre => I in Carry_In'Range;

   procedure Lemma_Multiply_Add_Value                                     --  LB-5 (DR-C5 form)
     (Before, After : P.Bytes; Carry_In : Carry_Vector; D, C_Out : Natural)
   with Ghost, Global => null, Always_Terminates,
     Pre  => Before'First = 1 and then After'First = 1 and then Before'Last = After'Last
             and then Carry_In'First = 1 and then Carry_In'Last = After'Last
             and then D <= 9 and then C_Out <= 9
             and then (if After'Length > 0 then Carry_In (1) = D else C_Out = D)
             and then (for all K in After'Range =>
                         Natural (After (K)) = (10 * Natural (Before (K)) + Carry_In (K)) mod 256
                         and then Next_Carry (Carry_In, C_Out, K)
                                  = (10 * Natural (Before (K)) + Carry_In (K)) / 256),
     Post => To_Big_Integer (10) * Work_Value (Before) + To_Big_Integer (D)
             = (if C_Out = 0 then Work_Value (After)
                else Work_Value (After) + To_Big_Integer (C_Out) * RQ.Power_Reference (Count (After'Length)));
   --  Body: for I in After'Range, with Prefix (X, I) := RQ.Prefix_Reference (X, (False, 1, Count (X'Length)), Count (I)):
   --    pragma Loop_Invariant
   --      (To_Big_Integer (10) * Prefix (Before, I) + To_Big_Integer (D)
   --       = (if Next_Carry (Carry_In, C_Out, I) = 0 then Prefix (After, I)
   --          else Prefix (After, I) + To_Big_Integer (Next_Carry (Carry_In, C_Out, I)) * RQ.Power_Reference (Count (I))));
   --  Step I-1 -> I: Prefix (X, I) = Prefix (X, I-1) + X (I) * P(I-1) (one unfolding; LB-4) and
   --  After (I) + 256 * c_I = 10 * Before (I) + c_(I-1); (t mod 256) + 256 * (t / 256) = t.
   --  Assertions in the body follow the same conditional discipline: P(I) is formed only for c_I /= 0, and at I = n
   --  only for C_Out /= 0 (DR-C5). No array is updated inside the lemma.
```

Notes:

- The `Multiply_Add` loop invariants are integer-only. Their checked cost is O(I) integer comparisons per cell
  (§9.3.4).
- `Old_Work` is a ghost constant declared **outside** the loop, so the F19 rule about non-scalars before the invariant
  does not apply. Whether GNATprove keeps `Old_Work = Work'Old` across the loop is probe P-X3; restating it as an
  invariant is the fallback.
- The Post saves `Work_Value (Work)'Old`, a Big_Integer, not the array (DR-C4). `'Old` forms at most `P(n-1)`.
- `K + 1` occurs only under `K < I ≤ Work'Last`; `Next_Carry` indexes `I + 1` only under `I < Carry_In'Last`.

### 6.5 `Decide_Work`: the original statements as ghost lockstep (B-REF-L, primary)

- **The reference** is the original body itself, `core/canonical_artifacts.adb:446-462`, moved verbatim into ghost
  statements. Textual identity is a mechanical obligation (PO-B21).
- **No new recursive declaration (corrected; V3-RC3 c).** Algorithm B declares no recursive function and no recursive
  procedure, so it adds no notice site (F20). It is **not** recursion-free in execution: its ghost assertions
  evaluate the existing pinned recursive references `Prefix_Reference` and `Power_Reference`
  (`core/resource_quantities.ads:40-56`). Under `-gnata`, each such evaluation recurses to a depth of about `n + 1`
  frames, each holding controlled Big_Integer temporaries (§9.3.4). The kind is pre-existing; the call sites are new.
- **No functional Post on `Integer_Matches`.** The original had no contract (F6), and no caller's contract mentions
  integer semantics (§6.9). The correspondence is a proved in-body assertion at every return of `Decide_Work`.

```ada
--  UNCOMPILED / UNPROVED — core/canonical_artifacts.adb, body-private
   procedure Decide_Work
     (A : Bytes; J : Span; Start, Stop : Count; T : Span; B : Binary_String;
      Work : in out P.Bytes; Result : out Boolean)
   with Global => null, Always_Terminates,
     Pre => P.Valid (A, J) and then Start <= Stop and then Stop <= J.Length
       and then (for all O in Start .. Stop - 1 =>
                   A (J.First + O) in Character'Pos ('0') .. Character'Pos ('9'))
       and then B.Valid
       and then Work'First = 1 and then Count (Work'Length) = B.Length
       and then (for all I in Work'Range => Work (I) = 0);

   procedure Decide_Work
     (A : Bytes; J : Span; Start, Stop : Count; T : Span; B : Binary_String;
      Work : in out P.Bytes; Result : out Boolean)
   is
      O     : Count := Start;
      K     : Count;
      Carry : Natural;
      Decimal_Value, Binary_Value, Product, Addend : Big_Integer with Ghost;   --  the original locals (:436-437)
   begin
      Decimal_Value := To_Big_Integer (0);                          --  ghost; the original initial values (:436)
      Binary_Value  := To_Big_Integer (0);                          --  ghost; the original initial values (:436)
      --  Decimal phase: the original loop :447-453, lockstep with the work array.
      while O < Stop loop
         pragma Loop_Invariant (Start <= O and then O <= Stop);
         pragma Loop_Invariant (Decimal_Value >= 0);
         pragma Loop_Invariant (Work_Value (Work) = Decimal_Value);   --  forms at most P(n-1) (§9.6)
         pragma Loop_Variant (Decreases => Stop - O);
         Product := Decimal_Value * To_Big_Integer (10);                                    --  ghost, verbatim :449
         Addend := To_Big_Integer (Integer (Byte_At (A, J, O) - Character'Pos ('0')));     --  ghost, verbatim :450
         Decimal_Value := Product + Addend;                                                 --  ghost, verbatim :451
         Multiply_Add (Work, Byte_At (A, J, O) - Character'Pos ('0'), Carry);
         if Carry /= 0 then
            --  Decimal_Value = Work_Value (Work) + Carry * 256**n >= 256**n (PO-B8). The ghost statement above has
            --  already formed this value (DR-C5). Later digits never decrease it (PO-B9); any n-byte binary value
            --  is below 256**n (PO-B10): an inequality theorem, not a cap.
            Finish_Decimal (A, J, O + 1, Stop, Decimal_Value);     --  ghost: the remaining original statements
            Finish_Binary (A, T, B, B.Length, Binary_Value);       --  ghost: the whole original binary loop
            Result := False;
            pragma Assert (Result = (Decimal_Value = Binary_Value));           --  PO-B13 (overflow path)
            return;
         end if;
         O := O + 1;                                                                        --  as :452
      end loop;
      --  Compare phase: most significant cell first, lockstep with the original binary loop :454-461.
      K := B.Length;
      while K > 0 loop
         pragma Loop_Invariant (K <= B.Length);
         pragma Loop_Invariant (Binary_Value >= 0);
         pragma Loop_Invariant (Work_Value (Work) = Decimal_Value);
         pragma Loop_Invariant                                              --  DR-C5 form: no P(n) at entry
           (if Binary_Value = 0
            then RQ.Prefix_Reference (Work, (False, 1, Count (Work'Length)), K) = Work_Value (Work)
            else RQ.Prefix_Reference (Work, (False, 1, Count (Work'Length)), K)
                 + RQ.Power_Reference (K) * Binary_Value = Work_Value (Work));
         pragma Loop_Variant (Decreases => K);
         K := K - 1;                                                                        --  verbatim :457
         Product := Binary_Value * To_Big_Integer (256);                                    --  ghost, verbatim :458
         Addend := To_Big_Integer (Integer (Binary_At (A, T, B, K)));                       --  ghost, verbatim :459
         Binary_Value := Product + Addend;                                                  --  ghost, verbatim :460
         if Natural (Work (K + 1)) /= Binary_At (A, T, B, K) then
            --  First difference from the top: the two values lie in distinct blocks [x*256**K, (x+1)*256**K)
            --  (PO-B12, LB-3), with K <= n - 1.
            Finish_Binary (A, T, B, K, Binary_Value);              --  ghost: the original statements for K-1 .. 0
            Result := False;
            pragma Assert (Result = (Decimal_Value = Binary_Value));           --  PO-B13 (mismatch path)
            return;
         end if;
      end loop;
      Result := True;                 --  K = 0: Prefix (·, 0) = 0 and 256**0 = 1, so Binary_Value = Work_Value
      pragma Assert (Result = (Decimal_Value = Binary_Value));                 --  PO-B13 (match path)
   end Decide_Work;
```

The original decimal loop variable `O` and the original binary loop variable are represented by `O` and `K`. `K` plays
the original's binary `O`, starting at `B.Length` and decremented before use, exactly as `:454-457`. At loop entry
`Binary_Value = 0` selects the first branch of the DR-C5 invariant, which is definitionally true. After the first
iteration, `Binary_Value` is at least the guard-nonzero top byte, and `K ≤ n - 1`.

Ghost procedures: bodies are the original statements; Posts are bounds only, written in DR-C5 form.

```ada
--  UNCOMPILED / UNPROVED
   procedure Finish_Decimal (A : Bytes; J : Span; From, Stop : Count; Value : in out Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Pre  => P.Valid (A, J) and then From <= Stop and then Stop <= J.Length
             and then (for all O in From .. Stop - 1 =>
                         A (J.First + O) in Character'Pos ('0') .. Character'Pos ('9'))
             and then Value >= 0,
     Post => Value >= Value'Old;
   --  Body: O := From; then the loop :447-453 verbatim (Product := Value * 10; Addend := …; Value := Product + Addend;
   --  O := O + 1) with Loop_Invariant (From <= O and then O <= Stop and then Value >= Value'Loop_Entry)
   --  and Loop_Variant (Decreases => Stop - O).

   procedure Finish_Binary (A : Bytes; T : Span; B : Binary_String; Upto : Count; Value : in out Big_Integer)
   with Ghost, Global => null, Always_Terminates,
     Pre  => Upto <= B.Length and then Value >= 0,
     Post => Value >= Value'Old * RQ.Power_Reference (Upto)                   --  DR-C5 form: never (Value'Old + 1) * P
             and then Value - Value'Old * RQ.Power_Reference (Upto) < RQ.Power_Reference (Upto);
   --  Body: O := Upto; then the loop :455-461 verbatim, with the invariant
   --    Value >= Value'Loop_Entry * P(Upto - O) and then Value - Value'Loop_Entry * P(Upto - O) < P(Upto - O),
   --  which uses Binary_At <= 255. On the mismatch path Upto <= n - 1 and Value'Old * P(Upto) <= 256**n - 256**Upto.
```

The overflow path calls `Finish_Binary` with `Upto = B.Length` and `Binary_Value = 0`, which yields
`0 ≤ Binary_Value < 256**n`. There `P(n)` is formed, but only after the decimal ghost value has reached `256**n`
(DR-C5).

Remaining B lemmas (procedures; iterative where induction is input-sized):

- **LB-1.** `0 ≤ Prefix_Reference (W, S, k) < Power_Reference (k)`. A copy of `Prefix_Bounds`
  (`core/resource_quantities.adb:230-257`), made iterative. It is instantiated only at `k ≤ n - 1` on non-overflow paths
  (DR-C5).
- **LB-2 (overflow).** `V ≥ 0` and `C ≥ 1` give `V + C * P ≥ P` (overflow path only).
- **LB-3 (distinct blocks).** Integers `x ≠ y` with `0 ≤ a, b < P` give `x * P + a ≠ y * P + b`.
- **LB-4 (split).** `Prefix (W, k + 1) = Prefix (W, k) + W (k + 1) * P(k)` and `P(k + 1) = 256 * P(k)`; each is one
  unfolding. On non-overflow paths it is used only for `k + 1 ≤ n - 1` when it mentions `P(k + 1)`.
- **LB-5.** §6.4.
- **LB-6.** The `Integer_Token` digit facts of §6.3.

### 6.6 `Integer_Matches`: owner, allocation and every exit (CL-1 in the B.2 shape)

Appendix B.2 of v3 is incorporated here. It supersedes v3's function-level handler.

**Reason [LEAD; DOC `SK/advanced-ada/chapters/ch13-exceptions.md`; Ada 2022 RM 11.6].**

- When an exception results from a failed language-defined check, assignments in the handled sequence may be
  disrupted.
- The owner assignment `Work := new …` therefore sits **before and outside** the inner handled sequence, which
  contains only the `Decide_Work` call.

```ada
--  UNCOMPILED / UNPROVED — core/canonical_artifacts.adb
with Ada.Unchecked_Deallocation;                       --  ADDED context clause
   type Work_Access is access P.Bytes;                 --  pool-specific; never "access all"
   procedure Free_Work is new Ada.Unchecked_Deallocation (P.Bytes, Work_Access);

   function Integer_Matches
     (A : Bytes; J : Span; N : Node; T : Span; Sign, Magnitude : Node) return Boolean
   with Global => null                                                       --  ADDED; profile byte-identical
   is
      B        : constant Binary_String := Base64 (A, T, Magnitude);          --  as :433
      Negative : constant Boolean := Byte_At (A, J, N.First) = Character'Pos ('-');   --  as :434
      Work     : Work_Access;                                                 --  owner; null by default
      Result   : Boolean;
   begin
      if not N.Valid or else N /= Prefix (A, J, 0) or else N.Form /= Integer_Value
        or else N.After /= J.Length or else not B.Valid
        or else not Sign.Valid or else Sign.Form /= Boolean_Value
        or else (Negative /= Match (A, T, Sign.First, "true"))
        or else (B.Length > 0 and then Binary_At (A, T, B, B.Length - 1) = 0)
        or else (Negative and then B.Length = 0)
      then return False; end if;                     --  :439-445 verbatim; nothing allocated (X0)
      Work := new P.Bytes'[1 .. B.Length => 0];      --  X2 (allocation failure) propagates here: nothing owned yet
      begin                                          --  the handled sequence contains only the call
         Decide_Work (A, J, (if Negative then N.First + 1 else N.First), N.After, T, B, Work.all, Result);
      exception
         when others =>
            Free_Work (Work);                        --  Work was assigned before this sequence began
            raise;                                   --  the same occurrence; never converted to a value
      end;
      Free_Work (Work);
      return Result;
   end Integer_Matches;
```

- **Loop invariants.** `Integer_Matches` contains no loop, so "a loop invariant in a list of statements with an
  exception handler" (F19) cannot arise. All loops are in `Decide_Work`, `Multiply_Add` and the ghost procedures.
- **Start offset.** `N.First + 1` occurs only after the guard, where `N.First = 0` by `Prefix`'s Post.
- **Allocation size.** `B.Length ≤ 3 * (2**61 - 1) = 6917529027641081853` [K-18, K-19], from `Base64`'s
  `(Size / 4) * 3 - Padding` (`:305, :324`) with `Size ≤ Count'Last - 2`. The native size computation has
  `2305843009213693954` of headroom [K-20]. Physical fit is O-WORKSPACE.
- **Borrow.** `Work.all` is borrowed for the `Decide_Work` call (`SK/spark-users-guide/chapters/ch13-pointers-and-ownership.md`).
- **Normal exits.** Every guard exit precedes allocation. The single post-allocation normal exit frees before
  `return`. `Free_Work` sets `Work` to null, which serves the end-of-scope leak check.

### 6.7 Proof-interface alternatives (V2-RC1, V2-F18; unchanged, with the R-PREFIX clarification)

| Id | Alternative | Public spec | Evidence it needs | Known risk |
|---|---|---|---|---|
| PFX-1 (primary) | D-B-PREFIX, §6.3 | adds one Post conjunct and the ghost `Integer_Token` (R-PREFIX: eligible in principle) | PO-B1; checked cost of one quantified token check per integer `Prefix` call (§9.3.4) | none known beyond proof |
| PFX-2 | `Refined_Post` on `Prefix`'s body carrying the integer-token conjunct, with `Integer_Token` body-private | byte-identical | probe P-PFX2: legality of `Refined_Post` on a visible recursive function without abstract state; use at internal call sites; the "should be implied by its refined postcondition" check; no new warning | unknown interaction with the existing `[contracts-recursive]` notice |
| PFX-3 | a private core `Prefix_Core` with the stronger Post, and `Prefix` completed in the body as `(Prefix_Core (A, S, From))` | byte-identical text | probe P-PFX3 | The unchanged variant on a now non-recursive `Prefix` should draw "no recursive call visible on subprogram with Subprogram_Variant" (F24), a new strict warning. Removing or relocating the variant is a reviewed public contract and termination change. **Preserving the variant's text alone does not prove equivalent behaviour** (R-PREFIX). Full equivalence must be re-proved |
| PFX-5 | general-addend arithmetic: the work array handles the original addend domain `-48 .. 207` with signed digit propagation | unchanged | a new proof of signed propagation | more complex, but internal |
| PFX-4 (rejected) | executable digit validation with an executable Big_Integer fallback | — | — | rejected: executable Big_Integer would remain on a path the proof cannot exclude |

### 6.8 B-REF-R: v2's closed references, retained as an alternative

v2's `Decimal_Reference`, `Binary_Horner`, `Binary_Prefix`, `Work_Prefix` and `Integer_Matches_Reference` would give
`Integer_Matches` a functional Post (D-B-SPEC). They are retained as alternative B-REF-R, with two costs: four new
recursive-function notice sites (F20), and checked recursion of depth m and n. B-REF-L dominates on both counts.

### 6.9 Equivalence summary [LEAD; §8.2 obligations]

- Guard exits are byte-identical and precede allocation (PO-B14).
- On the guarded path, digits are `0..9` (PO-B2) and the lockstep invariant `Work_Value (Work) = Decimal_Value` holds
  (PO-B7).
- **Overflow path.** `Decimal ≥ 256**n` (PO-B8) and stays so (PO-B9); `Binary < 256**n` (PO-B10); so the original
  returns False.
- **Mismatch path.** The first differing cell from the top separates the values (PO-B12).
- **Match path.** `Decimal_Value = Work_Value = Binary_Value` (PO-B11).
- **Result.** `Integer_Matches` returns exactly the Boolean the original statements compute, on every input that
  passes the guard. In proof semantics Big_Integer is unbounded, so this covers values at and above `2**6432`.
- **Callers.** `Tagged_Matches`, `Array_Payloads_Match`, `Bindings`, `Artifact_Binding` and `Seal` stay
  byte-identical, and none of their contracts mentions integer semantics. Their existing proofs are re-run (PO-B19).
- **Release build.** No Big_Integer operation executes in `Integer_Matches`, `Decide_Work` or `Multiply_Add`
  (O-NATIVE confirms the compiled closure).
- **Checks build, horizon (DR-C5, PO-B22).** D1-B's ghost forms a value ≥ `256**n` only on a path where the original
  decimal statement has already formed one. With the installed runtime, the guard-passing inputs on which D1-B's
  checked ghost exceeds the representation limit are therefore contained in those on which the original statements
  already exceed it. That is a static claim to be proved and observed (§9.6). D1-B still adds checked **cost**
  (§9.3.4).

## 7. Work lifetime and reclamation on every exit (V2-RC2, R-WORKSPACE)

### 7.1 Exit map X0..X7 (V2-F14 corrected; X6 and X7 mapped, V3-RC2 d)

Release-build ghost code is removed, because the default assertion policy is Ignore (inventory `SUMMARY.md` §(2),
citing `gnat_rm.info:14888-14889`). "Control" means an additive control of §12.6, run in a scratch harness under the
existing admission gates. "Proof" means an obligation of §8. No control manufactures a new accepted exception.
Injected failures are native failures, recorded OPEN.

| # | Exit | Builds | Mechanism | Reclaimed by | Control or proof |
|---|---|---|---|---|---|
| X0 | guard `return False` and Tagged_Matches pre-checks (normal, pre-allocation) | both | before `new` | nothing allocated | W-8a: the allocation counter for Work-call-site allocations stays 0 on every IM-7 case; PO-B14 |
| X1 | normal return of `Result` | both | `Free_Work` before `return` | normal path | W-4 heap baseline; IM-*; P-W2 |
| X2 | `Storage_Error` from the allocator | both | raised by `new`, which is outside the inner handled block (B.2), before `Work` is assigned; propagates to the caller | nothing owned | W-1 injection at the Work allocation; W-7c for a re-entrant invocation; P-W6 |
| X3 | `Storage_Error` from the representation limit or heap exhaustion inside checked evaluation after allocation: `Decide_Work`/`Multiply_Add` Pre/Post, invariants, ghost lockstep, lemmas, `Work_Value`, `Prefix_Reference`, `Power_Reference`. (`Assertion_Error` is excluded by proof, PO-B13 and PO-B20) | checks | propagates into the inner block | inner handler: `Free_Work`, bare `raise` | W-2, which records the actual failing location (§9.6); W-7b for re-entrant invocations; P-W1..P-W6 |
| X4 | `Storage_Error` from saved-value copies (`Old_Work`, `Carry_In`, `Work_Value (Work)'Old`) | checks | when represented as an Ada exception; placement unknown from source (F27) | inner handler | W-3 if the harness admits it; PO-N7 |
| X5 | primary-stack overflow without stack checking (F27) | both | SIGSEGV; GNAT may convert it to `Storage_Error` only where its handler and alternate stack exist; on a foreign thread the process may die | process death releases memory; a hard fault | W-3 and W-8b record it as a native failure (OPEN), never a recovery or acceptance |
| X6 | **caller Post and re-entry** (F26) | checks | **X6a:** a failure in `Seal`'s Post, `Seal_Reference` or `Seal_Equation` evaluation outside any `Integer_Matches` invocation: the earlier invocation's Work was already freed at its X1. **X6b:** those contracts **re-invoke** `Integer_Matches` through `Artifact_Binding` (`.ads:395`, `.adb:129`, `.ads:362`). Each re-invocation is a fresh call with its own X0..X5; its failure propagates out of the caller's contract evaluation to `Decide`'s handler | X6a nothing to reclaim; X6b per invocation | W-7a (X6a), W-7b and W-7c (X6b). P-W2 holds per invocation (`Global => null`, local owner). P-W4: the call is made from another function's Post |
| X7 | **pre-allocation exceptional exits**: the declarative part (`Base64`, `Byte_At`) and the guard (`Prefix` with its new conjunct, `Match`, `Binary_At` with its new Post) | both | **X7-L:** a failed language-defined check. **X7-A:** a failed checked contract evaluated before allocation. **X7-R:** native resource exhaustion before allocation | nothing allocated | X7-L: **proved unreachable** (existing AoRTE proofs of these units re-run, PO-B19, PO-B20). X7-A: **proved unreachable** (PO-B1, PO-B3, existing contract proofs). X7-R: X5-class native failure, W-8b if admissible; no Work outstanding |

Bignum temporaries are controlled. On every propagation they are finalized by Ada semantics (RM 7.6.1;
`RT/a-nbnbin.adb:615-620`). Whether GNAT actually finalizes every transient checked temporary on exception is native
evidence item P-W6.

### 7.2 CL-1 (primary): pool-specific owner plus inner-block handler with re-raise

The code is §6.6. Requirements:

- the handler frees and re-raises the same occurrence, and never converts it to a value;
- the allocation is completed **before** the handled sequence (B.2);
- no loop sits in the handler-protected list (F19);
- the access type is pool-specific;
- the initialized allocator is required by installed E0019 (`GP/share/spark/explain_codes/E0019.md:8-19`).

**CL-1 is selected only if every gate below passes on the exact installed tool in a reviewed scratch frame.** F21 and
F22 make gate P-W3 a real risk. GNATprove does not model run-time-check or native exceptions as propagation, so it may
prove the handler unreachable and report "unreachable code". That is a strict warning, and waiving it is forbidden.

### 7.3 Installed-tool probe battery (O-LEGALITY-PROBE; none run)

All probes run in the reviewed scratch frame, never as a raw prover launch outside it (`HANDOFF.md:80`). The command is
the strict command of `HANDOFF.md:158`, applied to probe units that copy the §6.6 pattern exactly.

| Probe | Question | Pass criterion |
|---|---|---|
| P-W1 | Is a `Global => null` Boolean function legal SPARK with this shape: a pool-specific allocator before an inner block, a borrow of `Work.all` for an `in out` call inside that block, a block handler `when others => Free_Work (Work); raise;`, and `Free_Work` before `return`? SPARK's non-allocating-function classification is not a claim that the body executes no allocator | no SPARK legality or unsupported-construct error |
| P-W2 | Ownership and leak checks | "absence of resource or memory leak … proved" at each `Free_Work` and at end of scope, including the handler; no move or borrow error |
| P-W3 | Proof warnings under `--proof-warnings=on` | **no** unreachable-code, unreachable-branch or other new warning on the handler or the bare `raise;` |
| P-W4 | Use in assertions | the function is called from another function's Post (as `Seal`'s Post reaches it, X6) without "allocating function inside an assertion" or a leak error |
| P-W5 | Flow | no flow error or warning (including INEFFECTIVE) |
| P-W6 | Native (§7.4) | handler coverage, generated owner store and landing pad, saved-value placement, temporary finalization and leak-freedom under induced failures |
| P-W7 | Alternative shapes | the same battery for CL-2 and CL-3 |
| P-W8 | Absence of new Off | probe units contain no `SPARK_Mode => Off`; the sole boundary stays `core/worldline-c_api.adb:25` |

### 7.4 Native evidence plan (O-EXCEPTION-CLEANUP, O-WORKSPACE; none run)

- **Expanded code.** Compile both scenarios on the exact toolchain. Inspect `-gnatG` and assembly for:
  - the allocator's in-place initialization (no n-byte stack temporary);
  - the **placement** of `Old_Work`, `Carry_In`, `'Old` copies, A-GHOST-0 aggregates (if used), the transport copies
    (F8) and CL-2's array: primary stack, secondary stack, heap, or elided. Source does not establish it (F27);
  - the postcondition wrapper relative to the inner handler;
  - the owner store and the handler's landing pad (B.2);
  - transient-temporary finalization on exception.
- **Fault injection in a scratch harness.** An interposed allocator fails exactly the selected allocation. The Work
  allocation is identified by its call site and ordinal; bignum allocations by their call sites. Cases:
  - allocation failure at the Work `new` (X2);
  - a post-allocation checked failure: an n ≥ 805 magnitude reaches the representation limit at the first decimal
    invariant (X3, §9.6);
  - a saved-copy failure: a large n on a small thread stack, if the harness admits it (X4/X5);
  - caller-Post failures and re-entries (X6).
- For each injected case, the expected observations are:
  - the exception propagates unchanged;
  - the export maps it as §9.4 shows;
  - the diagnostic stream records `finalization.decide` with the exception;
  - the heap returns to its baseline.
- **Repeated calls.** N calls alternating success, mathematical False and injected failure. Record heap high-water and
  in-use bytes. Audit leaks with `gnatmem` (`-largs -lgmem`) or allocator statistics: the final water mark is zero.
- **Stage separation on the mixed export, by dependency (§9.5).** Inject only at the k-th `Decide` invocation of the
  fixed dependency and kind combination. The expected marks are those of §9.4: primary/staged readiness,
  primary/staged context. W-5 lists every case.
- Every injected failure is a resource failure: an OPEN native obligation, never an accepted refusal.

### 7.5 Lead-owned alternatives if a CL-1 gate fails

**CL-2: frame lifetime, the former F-B1 (lead-owned; no API change).** After the guard, in `Integer_Matches` (E-4
incorporated: the start offset is the explicit expression of §6.6):

```ada
--  UNCOMPILED / UNPROVED
      declare
         Work : P.Bytes (1 .. B.Length) := [others => 0];      --  a local object of dynamic size; freed by unwinding
      begin
         Decide_Work (A, J, (if Negative then N.First + 1 else N.First), N.After, T, B, Work, Result);
      end;
      return Result;
```

- No handler and no ownership are needed. Every normal and exceptional exit reclaims the frame.
- **Placement is not established by source.** GNAT usually places dynamically sized locals in the primary stack
  frame; that is PO-N2 evidence for this candidate (F27).
- Native obligations:
  - the exact placement and frame size from `-gnatG` and assembly;
  - measured stack headroom at the deepest export call depth, for every originally successful input;
  - recursion headroom (`Tagged_Matches` is recursive);
  - stack-clash exposure without stack probes (`-fstack-check` and `-fstack-clash-protection` are absent from
    `core/worldline_core_sources.gpr:11-12`; adding one is a reviewed configuration change).
- Originally successful values are below `2**6432`, so `n ≤ 804` bytes [K-02].
- Stack exhaustion is a native failure: OPEN, never accepted.

**CL-3: GNAT `finally` (lead-owned, experimental, last resort).**

- `Work := new …` stays outside the protected block. The block contains `Decide_Work (…)`, and its `finally` part
  contains `Free_Work (Work)`. The return follows the block.
- It requires the experimental extension (F23): `pragma Extensions_Allowed (All_Extensions)` in
  `canonical_artifacts.adb`, or a small private child unit.
- It needs the probe battery P-W1..W8 for `finally`. Loops stay in `Decide_Work` (F19).
- It needs a separate GPT-6.1 review of the experimental-mode use.

### 7.6 Operator-owned API/ABI packages: F-B2 and F-B3 (not selected; incomplete without the items listed)

| Package | What it is | Required before it could be eligible |
|---|---|---|
| F-B2: procedure migration | the workspace comes from a procedure caller; `Tagged_Matches`, `Array_Payloads_Match`, `Bindings`, `Artifact_Binding`, `Seal` and the C exports gain procedure successors | Every function version stays in contracts (`Seal`'s Post, `Seal_Equation`) and still executes under `-gnata`. The package needs an executable, non-allocating, equivalent body, which is the problem itself. It must also supply: equivalent checked functions; every original capability and caller preserved; re-proof of every original contract; no new Off boundary; explicit operator approval of a concrete API, which is not proof (`HANDOFF.md:121`) |
| F-B3: caller-supplied scratch | the C ABI gains a scratch address and length (new export versions) | everything in F-B2, plus: size derivation before parsing; size, alignment, extent and overlap checks; custody and lifetime of the scratch; versioned layouts and ABI tests; the Python caller's obligations; migration of every caller; `proof_manifest` export bindings |

### 7.7 What stays OPEN

- Legality probes: O-LEGALITY-PROBE.
- Exceptional reclamation evidence: O-EXCEPTION-CLEANUP.
- Heap or stack fit for every originally successful input, and costs for new inputs: O-WORKSPACE, O-COST-MEASURE.
- Hard-fault classification: O-NATIVE.
- Export mapping: O-TRANSPORT-MAPPING.

<!-- PART-4 -->
