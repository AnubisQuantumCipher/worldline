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
| **V3-RC1** (a) | E2-b must preserve json's original-key sorting and failure behaviour, including the pre-coercion mixed-key `TypeError` | §11.4.2 serializer requirements S-1..S-10 and E2-b (line 2262); F30 in §3.4 (line 399) | PACKAGE (no option selected) |
| V3-RC1 (b) | Include aliased and forwarded JSON calls, at least `scripts/decisive_evaluation_test.py:264`, using a semantic census stronger than direct-name AST matching; update inventory, totals and settings | §11.1 (line 2132); Appendix A.2 (method), A.3 (193 + 2 + 254 = 449 operations), A.5 row 193 | CORRECTED; census results OBSERVED |
| V3-RC1 (c) | Give the `native/build_guard.py` interpreter an E1 disposition or a reviewed bound | §11.3 class C12 (line 2208); Appendix A.5 rows 160-162 | PACKAGE plus a reviewed-bound proposal |
| V3-RC1 (d) | Formatting exclusions as absolute-magnitude bounds; parsing exclusions as lexical digit-count bounds | §11.4.3 (line 2308); §11.4.4 (line 2331); Appendix A.4 | CORRECTED |
| V3-RC1 (e) | Correct Appendix A's C4/C5 byte-identity statement for `proof_manifest.py` | Appendix A.1; F33 in §3.4 (line 437) | CORRECTED |
| V3-RC1 (f) | Integer-key and mixed-key-failure codec controls | §12.5 PY-8 and PY-9; also PY-10..PY-14 (line 2554) | DESIGNED (unrun) |
| V3-RC1 (g) | Synchronize `decisions.json`; keep E0/E1/E2 unselected | `decisions.json` `operator_items` OD-2; §11 | PACKAGE |
| **V3-RC2** (a) | Equal and lower usage variants with full arrays, totals and status walks | §12.2 RL-7d, RL-7d′, RL-7e, RL-7e′ (line 2462) | DESIGNED (unrun) |
| V3-RC2 (b) | The remaining invalid-operand selector combinations | §12.3 RL-12V, RL-12I, RL-12IN, plus RL-12S and RL-12M; the selector matrix in §12.7 (line 2487) | DESIGNED (unrun) |
| V3-RC2 (c) | A true middle-cell IM mismatch | §12.4 IM-11 (line 2528) | DESIGNED (unrun) |
| V3-RC2 (d) | Map X6 caller-Post and re-entry, and X7 pre-allocation exits, to admissible controls or to proved-unreachable obligations | §7.1 exit map X0..X7 (line 1559); §12.6 W-7, W-8 (line 2576) | DESIGNED; probes OPEN |
| V3-RC2 (e) | Cover staged-only and Primary_And_Staged export and lifetime paths | §12.4 IM-10P, IM-10S, IM-10PS; §12.6 W-5 matrix; §9.4, §9.5 | DESIGNED (unrun) |
| V3-RC2 (f) | Specify RL-7c's row arrays | §12.2 RL-7c | DESIGNED |
| V3-RC2 (g) | Correct RL-7b's arithmetic: proposed held 8 minus selected sum 7+3 | §12.2 RL-7b, using K-102 | CORRECTED |
| V3-RC2 (h) | Mark RL-8 and RL-9 unused, or define them | §12.2: unused identifiers, no coverage credit | CORRECTED |
| V3-RC2 (i) | Review notes: IM-7's empty magnitude with positive 7 is an overflow, not a guard rejection; IM-10's positive case must rebuild bindings and its mismatch must isolate the magnitude | §12.4 IM-6, IM-7, IM-10 | CORRECTED |
| **V3-RC3** (a) | Rebuild §9.3/F29 from the self-referential `Prefix_Value`/`Radix_Power` Posts, `Magnitude`/`Value` body and Post, Compare's checked body and lemmas, every new helper, lemma and contract, and saved copies | §9.3.0-§9.3.6 (line 1817); F29 corrected in §3.3 | CORRECTED (static source reasoning) |
| V3-RC3 (b) | Correct A-GHOST-0's inherited factor estimate | §5.4 and §9.3.3: per-term factor `(4/3)(c²+11c+12)`, not "about K" | CORRECTED |
| V3-RC3 (c) | Restrict B's "no recursion" statement to new declarations | §6.5 (line 1330) | CORRECTED |
| V3-RC3 (d) | Qualify source-only stack-placement claims | F27 in §3.3; §7.4, §7.5, §9.3.5 | CORRECTED |
| V3-RC3 (e) | Record actual checked failure points | §9.6 (line 2071); W-2. This led to F34/DR-C5 (repaired) and F35 (OPEN) | CORRECTED; OPEN where stated |
| V3-RC3 (f) | Expand mixed-call repetition and the readiness/context mapping to primary and staged, with dependency-qualified injection locations | §9.4 (line 2019), §9.5 (line 2034); §12.6 W-5 | CORRECTED |
| V3-RC3 (g) | Synchronize RL-1 wording, trace and index labels, and `decisions.json` | §12.1 RL-1 (line 2446); this table; `decisions.json` | CORRECTED |
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
| `APPENDIX-A-python-conversion-surface.md` (v4) / `jackal.json` (v4) | `8c8772d0bae606c45d06428cf6ee69da8afa94231477eb2152e5857accc5e996` / `c3de17e765f8d67f3ac01e65295a28bca199426a0b61d1cba7d3e557c8962bd3` |

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
- The checked `Compare` evaluations of §9.3.3, at most `(12N + 13)·u·K + 3·u·N + 10·u` per `Selected_Sum_Order` call,
  are replaced by `u` calls of LA-9L, one per selected usage row inside LA-7's row loop. Each costs its Post's two
  `Q.Value` evaluations, `8·PV(L)` invocations [K-202], plus an O(L) loop of Prefix_Reference invariants (about
  `L·r(L)` invocations).
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
   --  Step I-1 -> I: Prefix (X, I) = Prefix (X, I-1) + X (I) * P(I-1) (one unfolding of the expression function,
   --  the fact LB-4 states; no Prefix-level step assertion, §9.3.4) and
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
| X2 | `Storage_Error` from the allocator | both | raised by `new`, which is outside the inner handled block (B.2), before `Work` is assigned; propagates to the caller | nothing owned | W-1 injection at the Work allocation; W-7b for a re-entrant invocation; P-W6 |
| X3 | `Storage_Error` from the representation limit or heap exhaustion inside checked evaluation after allocation: `Decide_Work`/`Multiply_Add` Pre/Post, invariants, ghost lockstep, lemmas, `Work_Value`, `Prefix_Reference`, `Power_Reference`. (`Assertion_Error` is excluded by proof, PO-B13 and PO-B20) | checks | propagates into the inner block | inner handler: `Free_Work`, bare `raise` | W-2, which records the actual failing location (§9.6); W-7c for re-entrant invocations; P-W1..P-W6 |
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

## 8. Proof-obligation list (all OPEN; none attempted)

"Proof" means:

- the exact strict command of `HANDOFF.md:158`;
- zero unproved, zero justified and zero `pragma Assume`;
- every strict warning obligation resolved (`HANDOFF.md:161`);
- protected floor 251, the sole `worldline-c_api` boundary, and the full ordered roster (535 names observed in common
  source) preserved, with new names appended only.

### 8.0 Cross-cutting

| Id | Obligation |
|---|---|
| PO-X1 | Installed compile legality with `-gnat2022 -gnatwa -gnatVa -gnatf`: no new warnings and no `pragma Warnings (Off)`. GNATprove 16.1.0 legality of: the Ghost generic instance `Column_Big`; bracket and iterated aggregates; declare-free loop bodies; the pool-specific access type with its `Unchecked_Deallocation` instance; the inner-block handler and bare re-raise (B.2, P-W1); `Refined_Post` only if PFX-2 is used; **`Multiply_Add`'s `'Old` prefix placed in the first operand of `and then`, outside the conditional expression (RM 6.1.1 rules for a potentially unevaluated `'Old`; §6.4)** |
| PO-X2 | Flow: `Global => null` on every new subprogram; no uninitialized read; no INEFFECTIVE initialization (F21) |
| PO-X3 | No `Annotate` justification, no `Assume`, no imported or bodiless lemma |
| PO-X4 | Checked-build executability of all new ghost code; no Assertion_Level or policy change; cost recorded in §9.3 |
| PO-X5 | Pins refreshed only through the official generator (`runtime/worldline/proof_manifest.py:10`); roster additions append-only |
| PO-X6 (P-X3) | Installed shape rules of F19: no declaration in a loop body before an invariant; no loop with an invariant in a handler- or `finally`-protected list; whether `Old_Work = Work'Old` survives the `Multiply_Add` loop |
| PO-X7 (P-R1) | Recursion notices: confirm that `Side_Sum` draws `[contracts-recursive]`/`[numeric-variant]` and that iterative lemma procedures draw none. Resolution of the `Side_Sum` notice joins R-1. Otherwise switch to A-GHOST-0 |
| PO-X8 | Reassociation: every mixed additive chain explicitly left-associated (F28); no `[operator-reassociation]` item |
| PO-X9 (new) | Representation horizon of D1's checked ghost: PO-B22 for Algorithm B; the OPEN item O-GHOST-HORIZON-A for Algorithm A (F35). Neither is closed by a cap, a Pre or a refusal |

### 8.1 Algorithm A

| Id | Obligation |
|---|---|
| PO-A0 | `type Column_Total is range 0 .. 2**71` accepted with a 128-bit base on the pinned GNAT 16.1.0 aarch64; every §5.2 conversion is free of runtime errors |
| PO-A1 | LA-10 for `Held_Only`, `Budget_Only` and `Both_Kinds` (partition) |
| PO-A2/A3/A23 | LA-9: normalization keeps value; `Usage_Selected` equals the value comparison; `Operand`'s value equals `Amount_Reference` when counted |
| PO-A4/A5 | Invalid spans give zero prefixes; padding gives `Prefix_Reference (X, C) = Magnitude (X)` when `Length ≤ C` (an iterative copy of `Prefix_Padding`, DR-C3) |
| PO-A6 | LA-1/LA-2 column step |
| PO-A7 | LA-7 signed completion at the extent |
| PO-A8/A13 | Sign split and target placement (LA-7, LA-8) |
| PO-A9 | LA-3 column emit |
| PO-A10 | LA-4 order extension (E-3: relational Pre) |
| PO-A11 | LA-5 residual carry; LA-11 zero extent; `Lemma_Close` |
| PO-A12 | LA-6 and all range checks: `Column ≤ Before + 255 * (count + 2)`, `Carry ≤ N + 1 ≤ 2**63`, `Column ≤ 2**71` [K-52, K-54] |
| PO-A14 | Pre-pass invariant: coverage of the target and of both candidates of every selected row |
| PO-A15/A16 | `Contained` loop 2: the unchanged invariant is preserved; early False equals `¬(S_H + S_B ≤ Value (Amount))` |
| PO-A17 | `Pair_Sum_Order` Post; carry at most 2 [K-17] |
| PO-A18 | Termination: `for` loops; the `Side_Sum` variant; lemma loop variants |
| PO-A19 | `Check'Result = Decision_Reference` and the Ready conjuncts: every other branch structurally identical, status order unchanged |
| PO-A20 | `Conserved` Post |
| PO-A21 | `Selected_Sum_Order` Post, including `Columns = 0` |
| PO-A22 | INIT/INSIDE/PRESERVE/AFTER for both loop levels, with frames on the untouched side |
| PO-A24 | If A-GHOST-0 is used: the `Truncated`-rows lemmas (row-wise `Sum_Reference` difference equals digit times power) and the completion `Truncated (X, C) = X` |
| PO-A25 (new) | If A-SEL-L is selected (§5.10): LA-9L proved; PO-A2 restated through LA-9L; probes of §7.3 for `Usage_Exceeds`; separate GPT-6.1 review |
| PO-A26 (new) | F35 (§5.11): a design that removes the one-sided ghost horizon excess on the direct-Ada signed domain without a Pre, cap, refusal or contract change. **OPEN; no candidate selected** (O-GHOST-HORIZON-A) |

### 8.2 Algorithm B

| Id | Obligation |
|---|---|
| PO-B1 | `Prefix`'s new conjunct, proved in its body; existing conjuncts and variant unchanged |
| PO-B2 | Digit range on `[Start, Stop)` from `Integer_Token` (LB-6) |
| PO-B3 | `Binary_At` Post `≤ 255` [K-49..K-51] |
| PO-B4 | `Multiply_Add` loop: unprocessed-cell frame against `Old_Work`; per-cell carry relations; `Old_Work = Work'Old` (PO-X6) |
| PO-B5 | Column arithmetic: `T ≤ 2559`, carry ≤ 9 [K-15, K-16]; LB-5 in its DR-C5 form |
| PO-B6 | `Multiply_Add` Post in its DR-C5 form, including the null-Work case (`Carry_Out = Digit_Value`, `P(0) = 1`) |
| PO-B7 | Decimal lockstep invariant preservation |
| PO-B8 | Overflow: `Carry ≥ 1 ⇒ Decimal_Value ≥ 256**n` (LB-2) |
| PO-B9 | `Finish_Decimal` monotonicity (digits nonnegative) |
| PO-B10 | `Finish_Binary` Post in its DR-C5 form; overflow path `0 ≤ Binary_Value < 256**n` |
| PO-B11 | Match path: the DR-C5 compare-phase invariant (both branches); at `K = 0`, `Binary_Value = Work_Value` |
| PO-B12 | Mismatch path: first difference from the top (LB-3, LB-4, LB-1) |
| PO-B13 | The three in-body assertions `Result = (Decimal_Value = Binary_Value)` |
| PO-B14 | Guard identity: the guard text equals C5 `:439-445`; `Start` equals `:446`'s offset |
| PO-B15 | Ownership and memory: P-W1..P-W5 for CL-1 in the B.2 shape; or the CL-2 or CL-3 equivalents |
| PO-B16 | Shape and sizing: S1..S6; no index outside `Work'Range`; no `B.Length + 1`; native size [K-19, K-20] |
| PO-B17 | Termination: loop variants. No new recursive declaration; the existing recursive `Prefix_Reference`/`Power_Reference` are evaluated with their existing variants (§6.5) |
| PO-B19 | Callers byte-identical and their existing contracts re-proved |
| PO-B20 | Freedom from runtime errors of every new ghost expression on every input that reaches it |
| PO-B21 | Lockstep textual identity: the ghost statements in `Decide_Work`, `Finish_Decimal` and `Finish_Binary` are C5 `:436, :447-461` verbatim, modulo variable renaming (`O`/`K`, `Value`). A mechanical check, retained as evidence |
| PO-B22 (new; F34) | **Radix horizon (DR-C5).** On every guard-passing input, the magnitude of every Big_Integer value formed by D1-B's checked evaluation (contracts, invariants, ghost statements, lemma bodies, including intermediate results of `+`, `-`, `*`) is at most the largest magnitude formed by the original statements `:446-461` on that input. In particular `Power_Reference (n)` is evaluated only after a carry out of cell `n`. Consequence with the installed runtime: D1-B's checked ghost fails only on inputs on which the original statements fail. This is a design obligation discharged by review of every D1-B contract and assertion text, then observed by IM-1 and IM-5 in the checks build (§9.6, W-2). It is not a GNATprove property |
| PO-B23 (new) | `'Old` placement of §6.4 (PO-X1) and the conditional forms of §6.4-§6.5 prove with no new warning, including the INIT case `Binary_Value = 0` of the compare-phase invariant |

### 8.3 Native and resource obligations (evidence, not proof)

| Id | Obligation |
|---|---|
| PO-N1 | Compiled release call closure of the repaired bodies contains no Big_Integer operation (link map, objdump, `-gnatG`) |
| PO-N2 | The allocator is initialized in place, with no n-byte stack temporary; or CL-2's frame placement |
| PO-N3 | `Column_Total` arithmetic uses 128-bit operations; any `System.Arith_128` call allocates nothing |
| PO-N4 | Heap, stack and time measurements for §9 on the exact integrated library and runtime identity |
| PO-N5 | Export exception mapping classified (F12, §9.4) without counting a native failure as acceptance |
| PO-N6 | P-W6: handler coverage, generated owner store and landing pad, temporary finalization and leak-freedom under induced failures |
| PO-N7 | Checked-build saved-value placement and costs (§9.3.5) measured; source does not establish placement (F27) |
| PO-N8 (new) | The checked failure points of §9.6 observed on the exact identity, by location, never presupposed |

## 9. Native cost, failure semantics and the D2 delta (V2-RC6, V3-RC3)

All formulas are **[LEAD] static source counts**. They are not measurements and not proved cost bounds
(O-COST-MEASURE). Their arithmetic and polynomial identities are [JKL]. Symbols:

- N rows; `n_s` selected rows; `u` selected Held rows with observed usage present (`u ≤ n_s ≤ N`);
- K = `Columns`, the maximum effective length; L, `L_j` operand lengths (each at most K); `L_t` the target length;
- m decimal digits; n magnitude bytes;
- `id` the identity length used by `Same`.

### 9.1 Release-build costs of the new executable code

| Operation | Time (operation counts) | Auxiliary memory | Allocation |
|---|---|---|---|
| `Selected_Sum_Order` | pre-pass `Σ_j (c + id_j)`; columns `O(N·K + Σ_j min(L_j, K)·(id_j + u_j·L_j))`, where `u_j = 1` for a selected Held row with usage present (its executable `Compare` costs O(L_j) per column visit; with A-SEL-L, `Usage_Exceeds` costs the same order) | O(1) scalars; no secondary stack | none |
| `Pair_Sum_Order` | O(K) | O(1) | none |
| `Conserved` / `Contained` / `Check` | existing `Shape` and O(N²) `Parent_Supports` plus the comparator calls above; worst case `O(N²·K + N·Σ_j L_j·(id_j + u_j·L_j))` per `Contained` | O(1) beyond inputs | none |
| `Integer_Matches` | guard as today; decimal phase at most `m·n` cell steps with early exit; compare phase at most n | n heap bytes plus allocator header (CL-1), or n bytes of frame storage whose placement is not established by source (CL-2, F27) | one allocate and one free per call (CL-1) |

There is no asymptotic dominance claim against the original. Where the original succeeded (values below `2**6432`), it
allocated O(L) heap and automatic digit vectors per bignum operation (F1, V2-F15).

### 9.2 Failure semantics by scenario ("release" means `-XWORLDLINE_BUILD=release`; E-2 incorporated)

| Path | Pre-D1 release | Post-D1 release | Checks build (default) |
|---|---|---|---|
| Run ledger: a valid span with Length ≥ 804, or a value or sum ≥ `2**6432` | `Storage_Error` → `-1` (`core/resource_run_ledger_c_api.adb:222`) → Python `CoreUnavailable('full-ledger native transport refused')` (`runtime/worldline/resource_run_ledger.py:248`) | decision computed in the source-level design (O-NATIVE); time and transport-copy costs remain | fails at the first checked evaluation that reaches the limit; for padded inputs that is located in §9.6 (pre-existing, before any D1 code). D2 OPEN |
| Run ledger: an invalid span of any Length | the value is 0, with no loop (`:24`) | the same, with zero columns | Post evaluation returns 0 |
| Run ledger: direct-Ada `Contained` on signed operands whose one-sided magnitude sums reach `2**6432` (RL-24) | completes (False) | completes (False) | **post-D1 only:** a D1-introduced checked failure (F35, §9.6). OPEN |
| `Integer_Matches`, a value ≥ `2**6432` (magnitude n ≥ 805) | `Storage_Error` → 255 (plain); `Invalid_Request` (mixed, at the stage of §9.4) | Boolean computed (design); heap n bytes; exhaustion OPEN | pre-D1: the original decimal or binary accumulation. Post-D1: the first decimal-loop invariant (§9.6) → X3 → CL-1 frees and re-raises → same mapping. D2 OPEN |
| `Integer_Matches`, n ≤ 804 and decimal < `2**6432` (IM-1, IM-6; with or without a carry out) | value computed | value computed | value computed: DR-C5 keeps D1-B within the original's horizon (PO-B22). Cost OPEN |
| `Integer_Matches`, n ≤ 804 and decimal ≥ `2**6432` (IM-5) | `Storage_Error` → 255 / `Invalid_Request` | False (carry out) | the original decimal statement, now ghost, at the first prefix ≥ `2**6432`, in both pre-D1 and post-D1 checks builds (§9.6) |

E0's "native code accepts every length" (v2:1455) stays withdrawn. D1 establishes no default-build success, no
physical fit and no loaded-identity behaviour.

### 9.3 Checked-build (`-gnata`) work, rebuilt from source (V3-RC3 a, V3-F4)

#### 9.3.0 Scope and unit

- **Unit.** One **PRI** is one invocation of `Power_Reference`'s body (D2 review C-UNIT). Each PRI multiplies a
  bignum of up to `e` bytes by 256 and allocates its result (F1). Time per PRI grows with `e`, so PRI counts are
  operation counts, not time.
- **What is counted.** Under `-gnata`, every executed body, Pre, Post, loop invariant, assertion, ghost statement and
  lemma call. A public function evaluated anywhere is charged its body **and** its own Post, recursively.
- **What is listed but not converted into PRI.** Big_Integer additions, comparisons and multiplications outside
  `Power_Reference`, for example the 255 `Scale_Column` iterations of every `Column_Bounds` call
  (`core/resource_quantities.adb:15-39, 41-64`); controlled Adjust/Finalize; saved copies (§9.3.5); allocator and
  stack behaviour.
- **Exactness.** A count is exact where the path is stated. Otherwise it is an upper bound that assumes every
  conditional term is evaluated.
- **Status.** Every count is static source reasoning [LEAD]. None is a measurement. D2 and every native and cost
  obligation stay OPEN (V3-RC3 h).

#### 9.3.1 Primitives (pinned references and public ghost functions; C5 `core/resource_quantities.*`)

| Symbol | Construct | Checked PRI per evaluation | Source recurrence | JACKAL |
|---|---|---|---|---|
| `p(e)` | `Power_Reference (e)` (`.ads:40-45`) | `e + 1` | body recursion e → 0; the Post `>= 1` calls nothing | PE-01, K-174 |
| `r(c)` | `Prefix_Reference (·, ·, c)` (`.ads:47-56`) | `c(c+1)/2` | `r(c) = r(c−1) + p(c−1)`; the Post `>= 0` calls nothing | PE-02, PE-07 |
| `T(c)` | `Σ_{k=1..c} r(k)` | `c(c+1)(c+2)/6` | | PE-21, PE-06 |
| `w(e)` | `Radix_Power_Worker (e)` (`.adb:97-137`) | `e² + 3e + 1` | invariants at each iteration `k < e`: `p(k)`, plus `p(k−1)` when `k > 0`; Post `p(e)`; final block when `e > 0`: `2·p(e−1)` | PE-03 |
| `RP(e)` | public `Radix_Power (e)` (`.ads:58-67`; body `.adb:142-143`) | `(e³ + 9e² + 14e + 6)/3` | `RP(e) = w(e) + RP(e−1) + p(e) + p(e−1)`: its Post calls `Radix_Power (e−1)`, `Power_Reference (e)` and `Power_Reference (e−1)`; `RP(0) = w(0) + p(0)` | PE-04, PE-05, K-153 |
| `PVW(c)` | `Prefix_Value_Worker (c)` (`.adb:147-203`) | `(c³ + 6c² + 5c)/3` | invariants at each iteration `k < c`: `r(k) + p(k)`, plus `r(k−1) + p(k−1)` when `k > 0`; Post `r(c)`; final block when `c > 0`: `2·r(c−1) + 2·p(c−1)` | PE-08 |
| `PV(c)` | public `Prefix_Value (c)` (`.ads:69-83`; body `.adb:205-208`) | `c(c+1)(c² + 11c + 12)/6` | `PV(c) = PVW(c) + PV(c−1) + RP(c−1) + r(c) + r(c−1) + p(c−1)`: its Post calls `Prefix_Value (c−1)`, `Radix_Power (c−1)`, `Prefix_Reference (c)`, `Prefix_Reference (c−1)` and `Power_Reference (c−1)`; `PV(0) = 0` | PE-09, K-154 |
| — | `Magnitude` on a valid span of Length L (`.ads:85-89`; body `.adb:210-217`) | `2·PV(L)` | body `Prefix_Value (L)`; Post `Prefix_Value (L)`. An invalid span: 0 | — |
| — | `Value` on a valid span of Length L (`.ads:91-94`; body `.adb:219-226`) | `4·PV(L)` | body `Magnitude`; Post `Magnitude` | K-162 |
| `PB(o)` | `Prefix_Bounds (·, ·, o)` (`.adb:230-257`) | `o³ + 5o² + 7o + 1` | level `k ≥ 1`: `3k² + 7k + 3` (Post `2r(k) + p(k)`; the three assertions and the `Column_Bounds` actuals); level 0: Post `p(0)`. Plus 255 `Scale_Column` iterations per level (not PRI) | PE-15, PE-16, K-156 |
| `ΣPB(L)` | `Σ_{o<L} PB(o)` | `(3L⁴ + 14L³ + 15L² − 20L)/12` | | PE-17, K-157 |

Instances: `PV(803) = 70334477708` [K-159]; one checked `Value` on a valid 803-byte span: `281337910832` PRI [K-162].
v3's "~L⁴ per `Q.Value`" is replaced by `4·PV(L)`; the self-referential public Posts (`Radix_Power`, `Prefix_Value`)
are what v3 omitted.

#### 9.3.2 Composites reached from D1 and from the original

| Construct | Checked PRI per evaluation | Notes |
|---|---|---|
| `Is_Zero` on a valid L-byte span (`.ads:98-100`; body `.adb:316-333`) | Post `2·PV(L)`; body, all digits zero: `T(L−1) + T(L)` (loop invariant `r(k)` and end assertion `r(k+1)`) | a nonzero span exits early through `Prefix_Monotone` (`.adb:259-276`) and assertions with `Magnitude` |
| `Is_Negative` (`.ads:102-104`; body `.adb:335-338`) | Post `4·PV(L)`; body calls `Is_Zero` only when the sign flag is True | |
| `T.Nonnegative_Valid` (`core/resource_reservation_transition.ads:135-138`; body `.adb:520-523`) | Post `4·PV(L)`; body: `Is_Negative`, so `4·PV(L)` more | reached from `Shape` (`core/resource_run_ledger.ads:223-235`) |
| `Compare`, both spans valid, sign flags False, both of Length L, all digits equal (the full equal path; exact) (`.ads:107-117`; body `.adb:340-402`) | `(8L + 42)·PV(L) + Q(L)`, with `Q(L) = (L⁴ + 6L³ + 11L² − 2L)/2` | `42 = 16 + 6 + 8 + 12` [K-147]: Post (up to four `Value`), `Prefix_Padding` (Post `Magnitude` and base assertion `Prefix_Value`, per operand), the two `Is_Negative` Posts, the two `Value`/`Magnitude` assertions. `8 = 4 + 4` per iteration [K-148]: the loop invariant and the end assertion, each with two `Magnitude`. `Q(L)`: padding prefixes `4r(L)`, per-iteration prefixes `2(T(L) + T(L−1))`, two `Prefix_Bounds` per iteration `2·ΣPB(L)` [PE-18, PE-19, PE-22, K-158] |
| `Compare`, lengths `a ≤ b`, full equal path | PV terms `(2(b−a) + 21 + 4b)·PV(a) + (21 + 4b)·PV(b)`, plus prefix and `Prefix_Bounds` terms of order `b⁴` | `21 = 8 + 3 + 4 + 6` per operand [K-210]: Post, padding base, `Is_Negative`, assertions; the shorter operand's padding recursion adds `2(b−a)` levels of `Magnitude`; the loop runs `b` iterations. At `a = b = L` this is `(8L + 42)·PV(L)` [PE-19]. A sign flag True adds `Is_Zero` |
| `Compare` on an early-exit path | the fixed `42` terms (lengths permitting) plus the iterations executed, plus `Higher_Column_Order` and two assertions with `Magnitude` | upper bound: the full equal path |
| `Amount_Reference` (`core/resource_run_ledger.ads:187-192`) | at most three `Value`: `≤ 12·PV(L)` [K-181] | the Held usage comparison evaluates two `Value`, then the selected one |
| `Sum_Reference` over N rows (`.ads:200-209`) | `≤ N·12·PV(L)` | recursion depth N |
| `Exact_Value`, checked (`core/resource_run_ledger.adb:19-34`) | invariants `r(k) + p(k)` at each `k < L`, that is `T(L−1) + r(L)`; Post `4·PV(L)` | pre-existing; OD-1 |

Instances for two valid, nonnegative, equal 803-byte spans [K-159..K-161, K-172]:

| Term | PRI |
|---|---|
| `(8·803 + 42)·PV(803)` | `454782732859928` [K-160] |
| `Q(803)` | `209446213768` [K-161] |
| one checked `Compare`, full equal path | **`454992179073696`** [K-172] |

This is the `Context_Changed` comparison of RL-1's padded capacities (`core/resource_run_ledger.adb:165`), a
pre-existing cost on an originally successful input. v3's Post-only Compare estimate is withdrawn.

#### 9.3.3 D1-A (`Selected_Sum_Order`, `Pair_Sum_Order`, their lemmas), per call, A-GHOST-1

`Operand` → `Usage_Selected` → checked `Q.Compare` is reached only for a Held row with usage present (F36). One
both-sides evaluation of a `Side_Sum` or `Side_Total` calls `Operand` three times per such row: once per side in the
sign test, once more for the term on the matching side [K-191].

| D1-A construct | Evaluated | `Compare` evaluations | Other checked work |
|---|---|---|---|
| pre-pass | executable | 0 | none |
| executable `Operand` in the column loop | per column, per row passing the length test | `≤ u` per column | none |
| inner row invariant (`Digit_Term`) | per column, at each of N row iterations, over rows `1..J` | `≤ 3·u·N` per column [K-191] | digits only; no PRI |
| `Lemma_Column_Step` (LA-1/LA-2) Post | once per column | `9·u` per column (three both-sides `Side_Sum` kinds) [K-192] | prefix terms at `o + 1` and `o` per selected row; `P(o)` twice |
| `Lemma_Column_Step` loop invariant | per column, N iterations | `≤ 9·u·N` per column [K-192] | prefix terms at `o + 1` and `o`, up to N per selected row; `P(o)` twice per iteration |
| outer invariants | once per column | `3·u` per column [K-191] | prefix terms at `o + 1` per selected row; `P(o + 1)` four times [K-212] |
| ghost `Low` updates and LA-3 actuals | once per column | 0 | `P(o)` four times; LA-3 bodies run the `Column_Bounds` pattern (255 `Scale_Column` iterations each, two per column) |
| `Lemma_Close` Pre | once | `3·u` [K-191] | prefix terms at K per selected row and target; `P(K)` four times [K-212] |
| LA-7 Post | once | `3·u` [K-191] | `Selected_Sum` (`n_s` `Amount_Reference`); prefix terms at K |
| LA-7 loop invariant | N iterations | `≤ 3·u·N` [K-191] | `Selected_Sum (k)` and prefix terms at K for the first k rows |
| LA-10 Posts | N calls | 0 | `Selected_Sum (k + 1)`, `Selected_Sum (k)`, one `Amount_Reference`: `≤ 2·n_s + 1` `Amount_Reference` per call |
| LA-9 Posts | one per selected row | `4` per selected usage row (`1 + 1 + 2`) [K-193] | at most 11 `Value` including one `Amount_Reference`: `≤ 44·PV(L_j)` [K-179, K-180]; `Signed_Prefix_Value`: `r(L_j)` |
| padding facts (LA-7, LA-8; iterative `Prefix_Padding` copies) | one per selected operand and one for the target | 0 | `≤ (K − L_j + 2)` `Magnitude`, `2·PV(L_j)` each [K-199]; prefix terms |
| `Lemma_Close` Post; `Selected_Sum_Order` Post | once each | 0 | each `≤ 2` `Selected_Sum` and `≤ 2` `Value (Target)` |
| LA-8 Post | once | 0 | one `Value (Target)`; target prefix at K |

Totals per `Selected_Sum_Order` call (upper bounds):

- **Checked `Compare` evaluations through `Usage_Selected`:** `≤ (12N + 13)·u·K + 3·u·N + 10·u`.
  - Per column: `3N + 9N = 12N` from the row-sized loops [K-176] and `1 + 9 + 3 = 13` from the executable `Operand`,
    LA-1's Post and the outer invariant [K-177].
  - Once per call: `3N` from LA-7's loop; `3 + 3 = 6` from `Lemma_Close`'s Pre and LA-7's Post [K-178]; `4` from
    LA-9 [K-193]; `6 + 4 = 10` [K-194].
  - Each evaluation costs a checked `Compare` of the normalized usage and amount spans (§9.3.2).
- **Prefix-term PRI:** `≤ (n_s·(N + 2) + 2)·K(K+1)(2K+1)/6` over the columns, plus `(n_s·(N + 2) + 2)·r(K)` at the
  close. A selected row's prefix term costs `r(c)` whatever its own length, because `Prefix_Reference` recurses to
  `c`. Per column a selected row contributes `N + 2` prefix terms at `o + 1` (outer invariant, LA-1 Post, LA-1 loop)
  and at most `N + 1` at `o`; the target contributes 2 [K-199]. The column sum is `T(K) + T(K−1)` [PE-22].
- **Radix-power PRI:** per column `(2N + 6)·p(o) + 4·p(o + 1)` [K-211, K-212], plus `4·p(K)` at the close: order
  `N·K²`.
- **`Amount_Reference` evaluations:** `≤ 5·n_s + 3·N·n_s + N`, each `≤ 12·PV(L_j)` [K-181].
  - `5 = 2 + 2 + 1` from the `Selected_Sum_Order` Post, the `Lemma_Close` Post and LA-7's Post [K-200].
  - `3 = 1 + 2` per row and selected row from LA-7's loop and LA-10 [K-201]; LA-10 adds N single terms.
- **Target `Value` evaluations:** `≤ 5` (`2 + 2 + 1` [K-200]: the two Posts and LA-8), each `4·PV(L_t)`.
- **LA-9:** `≤ 44·PV(L_j)` per selected row [K-180].
- **Padding facts:** `≤ 2·(K − L_j + 2)·PV(L_j)` per selected operand and for the target.

Instance [K-195..K-198]: N = 1, one selected Held row with usage present (`u = 1`), usage and amount valid,
nonnegative, equal 803-byte spans, and an 803-byte target (K = 803):

| Term | Value |
|---|---|
| per-column `Compare` evaluations, `(12·1 + 13)·1·803` | `20075` [K-195] |
| once-per-call `Compare` evaluations, `3·1·1 + 10·1` | `13` [K-196] |
| all `Compare` evaluations | `20088` [K-197] |
| their PRI, each on the full equal path at 803 bytes (`454992179073696`, K-172) | **`9139882893232405248`** [K-198] |

This term alone exceeds every other D1-A term in the instance. It is the dominant D1-added checked cost whenever
usage rows exist (F36). A-SEL-L (§5.10) would replace those evaluations by `u` calls of LA-9L, each with its Post's two
`Value` evaluations, `8·PV(L)` [K-202], plus an O(L) loop of prefix invariants (about `L·r(L)`).

Without usage rows, the leading terms are the `Amount_Reference` evaluations of LA-7 and LA-10 (`3·N·n_s·12·PV(L)`)
and the prefix terms (`n_s·(N + 2)·K(K+1)(2K+1)/6`).

**`Pair_Sum_Order`** (Check's capacity branch): its Post evaluates at most `3·2 = 6` `Value` [K-205], that is
`24·PV(L)` [K-206]; its column loop has three prefix terms per side and no `Compare`.

**Per caller.**

- `Conserved`: two `Selected_Sum_Order` calls (`Held_Only`, `Budget_Only`).
- `Contained`: at most one call per row in loop 2.
- `Check`: at most two `Conserved` and two `Contained` calls, subject to short circuit (F8), plus one
  `Pair_Sum_Order`.
- `Check`'s own Post (`Decision_Reference`), `Conserved`'s and `Contained`'s Posts (the references) are pre-existing and
  unchanged.

**A-GHOST-0 instead of A-GHOST-1 (V3-RC3 b).**

- Each prefix row term at extent `c` costs one `Amount_Reference` on a truncated row: one or more checked `Value`,
  `4·PV(c)` each, instead of `r(c)`.
- The per-term ratio is `4·PV(c)/r(c) = (4/3)(c² + 11c + 12)` [PE-10]: 32 at `c = 1` [K-163], 656/3 at `c = 8`
  [K-164] and 2614616/3 at `c = 803` [K-165, K-173].
- Each evaluation also builds an N-row ghost aggregate and evaluates `Operand` (a checked `Compare` for every Held usage
  row) per row per aggregate.

#### 9.3.4 D1-B (`Integer_Matches` and its callees), per call

| D1-B construct | Evaluations | Checked PRI | Other checked work |
|---|---|---|---|
| decimal-loop invariants | one per decimal digit processed (at most m) | `r(n)` each (`Work_Value`) | integer invariants; the original decimal statements as ghost (multiply by 10, add) |
| `Multiply_Add` | at most m calls | `≤ MA(n) = (2n³ + 21n² + 37n + 12)/6` per call [PE-12]: `'Old` `r(n)`; Post `r(n)` (+ `p(n)` with a carry); LB-5 Post `2r(n)` (+ `p(n)` with a carry); LB-5 loop invariant `2r(I)` (+ `p(I)` with a carry) for `I = 1..n` | integer loop invariants, O(I) per cell; saved copies (§9.3.5) |
| decimal phase, per digit | — | `D(n) = r(n) + MA(n) = (n³ + 12n² + 20n + 6)/3` [PE-13, K-175] | |
| compare phase | at most n iterations | `≤ C(n) = (7n³ + 12n² + 11n)/6` [PE-14]: per iteration at K, two `Work_Value` `2r(n)`, `Prefix_Reference (Work, K)` `r(K)`, and `p(K)` once `Binary_Value ≠ 0` | the original binary statements as ghost (multiply by 256, add) |
| `Finish_Binary` (overflow `Upto = n`; mismatch `Upto = K ≤ n − 1`) | at most one | `≤ 3·r(Upto + 1)`: Post `3·p(Upto)` (`2 + 1` [K-191]); loop invariant `3·p(i)` for `i < Upto` [PE-23] | the original binary statements as ghost |
| `Finish_Decimal` (overflow only) | at most one | 0 | the remaining original decimal statements as ghost |
| PO-B13 assertions | one per return | 0 | one bignum equality |
| `Prefix`'s new conjunct | at every `Prefix` return of an integer node, in every caller | 0 | a quantified scan of the token |
| `Binary_At` Post | per call | 0 | integer |

The LB-5 body relies on the expression-function definitions of `Prefix_Reference` and `Power_Reference` for its one-level
unfoldings. An explicit step assertion that mentions only `P(I−1)` and `P(I)` adds O(n²) PRI per call. A
`Prefix_Reference`-level step assertion would add O(n³) per call and must then be counted in the packet.

Per `Integer_Matches` call on the match path: `m·D(n) + C(n)` PRI. Instances: `D(803) = 175178467` per digit
[K-166]; `C(803) = 605369655` [K-167]; `D(3) = 67` [K-168]; `C(3) = 55` [K-169]. Under `-gnata` every Seal evaluates
up to four bindings (§9.5), so each integer node can incur these costs four times per Seal.

#### 9.3.5 Saved copies and placement (F27 corrected)

| Copy | Where | Size | Placement |
|---|---|---|---|
| `Old_Work` | `Multiply_Add`, ghost constant | n bytes per call | not established by source (PO-N7) |
| `Carry_In` | `Multiply_Add`, ghost variable | n `Carry_Digit` elements | not established by source |
| `Work_Value (Work)'Old` | `Multiply_Add` Post | one bignum of at most n bytes (heap) plus its controlled wrapper | wrapper placement not established |
| `Value'Old`, `Value'Loop_Entry` | `Finish_Binary`, `Finish_Decimal` | one bignum each | as above |
| `Before`, `Low` | `Selected_Sum_Order` | two `Column_Total` scalars; two bignums below `256**K` | as above |
| A-GHOST-0 aggregates (only if selected) | per evaluation of a truncated-row `Sum_Reference` | `N·ρ` bytes, `ρ = Row'Object_Size/8` | not established |
| Work (CL-1) | heap | n bytes plus allocator header | heap |
| CL-2's array (only if selected) | `Integer_Matches` frame | n bytes | not established; usually the primary stack frame (PO-N2) |
| transport copies (pre-existing, F8) | C exports | whole input | not established |

#### 9.3.6 Consequences

- Under the current runtime the representation limit (F1) stops checked evaluation at `2**6432`. Below it, counts such
  as `454992179073696` PRI for one pre-existing `Compare` at 803 bytes [K-172] and `9139882893232405248` PRI for the
  D1-A instance above [K-198] make the default build a cost-correspondence failure candidate for such inputs. That is
  recorded under O-GHOST and O-COST-MEASURE, not hidden. No time was measured.
- The pre-existing pinned references and public ghost functions already have this character (F29).
- D2 must establish checked costs for original and D1 code together, without deleting or weakening any original
  checked assertion or Ghost requirement. Candidate D2 directions, recorded only, each needing separate review:
  - cost-correct executable definitions of the references;
  - logarithmic-depth reference forms with equivalence lemmas;
  - a runtime package (OD-1).
- D1's own new assertions follow lead-owned rules. None of them removes an obligation; each still needs a complete
  proof:
  - DR-C1: no `Q.Value`-based Post on per-iteration executable helpers (scope corrected by F36);
  - DR-C2: ghost terms use `Prefix_Reference` forms rather than `Q.Value`;
  - DR-C3: iterative lemmas;
  - DR-C4: value snapshots rather than array snapshots in Posts;
  - DR-C5 (new): no D1-B ghost value beyond the original's horizon (PO-B22).

### 9.4 Export failure stages, primary and staged (F12 extended; V3-F5)

| Stage | Call chain | Reached when | Outward result of a native failure in `Integer_Matches` | Distinguishing evidence |
|---|---|---|---|---|
| plain export | `Decide` (`core/evaluation_finalization_c.adb:121-257`), operation 3 → `F.Seal` (`:219`) | every operation-3 request | 255 (`:253-256`) | 255 against `0` with `Reason ≠ 0` for a mathematical False; the `finalization.decide` exception diagnostic (`:255`) |
| mixed, primary readiness | `Read_Ready` (`:429-430`) → `Decide` (`:386`) | `Needs_Primary` and `Primary_Kind = 2` | `Valid => False` → mark `finalization.mixed.primary-ready-rejected` (`:434`) → `Invalid_Request` | `finalization.decide` exception, then that mark |
| mixed, staged readiness | `Read_Ready` (`:441-442`) → `Decide` (`:386`) | `Needs_Staged` and `Staged_Kind = 2` | mark `finalization.mixed.staged-ready-rejected` (`:446`) → `Invalid_Request` | `finalization.decide` exception, then that mark |
| mixed, primary context | `Context_Joined` (`:474`) → `Final_Context_Matches` (`:406`) → `Decide` (`:273`) | `Agent_Ready = 1`, `P_Ready = 1`, `Primary_Kind = 2` | 255 → mark `finalization.context.seal-rejected` (`:276`) → False → mark `finalization.mixed.primary-context-rejected` (`:476`) → `Invalid_Request` | `finalization.decide` exception, then both marks |
| mixed, staged context | `Context_Joined` (`:479`) → `:406` → `:273` | `Agent_Ready = 1`, `S_Ready = 1`, `Staged_Kind = 2` | `seal-rejected`, then `finalization.mixed.staged-context-rejected` (`:481`) → `Invalid_Request` | `finalization.decide` exception, then both marks |
| mixed, elsewhere | `Decide_Mixed` handler (`:505-508`) | an exception outside `Decide` | `Invalid_Request` | the `finalization.mixed` exception diagnostic (`:507`) |

On the mixed export a mathematical False and a native failure are outwardly identical (`Invalid_Request`). Only the
diagnostic sequence distinguishes them: a mathematical False shows the stage mark without a preceding
`finalization.decide` exception. Controls assert on the diagnostics (§12.6). A native failure always remains OPEN.

### 9.5 Dependency-qualified Decide sequence and repetition (V3-RC3 f)

`Authority.Dependencies` and `Needs_*` (`core/worldline-evaluation_authority.ads:19-38`) fix which stages can run. With both
evidence slots of kind 2, the `Decide` invocations of one mixed request are, in order, each reached only if the
previous one returned normally:

| Dependency | Request shape | Decide invocations, in order |
|---|---|---|
| `Invalid_Collapse` | malformed request | none (`finalization.mixed.dependency-rejected`, `:424`) |
| `No_Raw_Evidence` | `Checkpoint_Return`, primary covers | none |
| `Primary_Only` | `Candidate_Evaluation`, primary covers | 1 primary readiness; 2 primary context (if `Agent_Ready = 1` and `P_Ready = 1`) |
| `Staged_Only` | `Checkpoint_Return`, primary does not cover | 1 staged readiness; 2 staged context (if `Agent_Ready = 1` and `S_Ready = 1`) |
| `Primary_And_Staged` | `Candidate_Evaluation`, primary does not cover | 1 primary readiness; 2 staged readiness; 3 primary context; 4 staged context (3 and 4 under the same conditions) |

Repetition (static source counts):

- At most `2 + 2 = 4` `Decide` invocations per mixed request [K-138].
- Each operation-3 `Decide` calls `Seal` once. Under `-gnata` one Seal reaches `Artifact_Binding` at up to four sites,
  in this order: the `Seal` body (`core/evaluation_finalization.adb:270`), `Seal`'s Post (`.ads:395`), the
  `Seal_Reference` body (`.adb:129`) reached from that Post, and `Seal_Equation` (`.ads:362`) reached from
  `Seal_Reference`'s Post. The release build evaluates the body only.
- An unobserved Seal evaluates three of these sites and makes `Read_Ready` or `Final_Context_Matches` reject, so the
  mixed request stops at that stage.
- With one integer node in each finalized bundle and every Seal observed: at most `4·(2 + 2) = 16` `Integer_Matches`
  evaluations per mixed request in the checks build [K-139], and `1·2 + 1·2 = 4` in the release build [K-140].

Fault-injection ordinals for the Work allocation (counted by call site), with one integer node per bundle and every
Seal observed:

| Build | Work-allocation ordinal of the first evaluation in Decide k | Within Decide k |
|---|---|---|
| checks | `4(k − 1) + 1`: 1, 5, 9, 13 for k = 1..4 [K-141..K-144] | `+0` Seal body; `+1` Seal Post; `+2` `Seal_Reference` body; `+3` `Seal_Equation` |
| release | `k` [PE-20] | the Seal body only |

Which stage Decide k is depends on the dependency (table above). For `Primary_And_Staged`, Decide 2 is the staged
readiness stage, not primary context (V3-RC3 f). §12.6 W-5 enumerates every injection by dependency and ordinal.

### 9.6 Checked failure points, recorded from source (V3-RC3 e)

These are the first checked evaluations that reach the representation limit, read from source [LEAD]. W-2 and the
named controls must record the actual locations on the exact identity (PO-N8); generated and native locations stay OPEN.

| Input | Pre-D1 checks build | Post-D1 checks build | Status |
|---|---|---|---|
| IM-1: decimal `10**1936`, magnitude n = 804 [K-07, K-150] | none: every value is below `2**6432` | none under DR-C5: `Work_Value` forms at most `P(803)` [K-204], and `P(804)` is never formed without a carry. **The v3 form failed here**: `Multiply_Add`'s Post and LB-5 formed `P(804) = 2**6432` [K-65] on every call (F34) | must succeed; cost OPEN |
| IM-2, IM-3, IM-4, IM-8, IM-10: magnitudes of n ≥ 805 bytes [K-151, K-137, K-149, K-131] | the first original decimal statement (`:449` or `:451`) whose result reaches `2**6432` | the first evaluation of the decimal-loop invariant `Work_Value (Work) = Decimal_Value`, at `O = Start`: `Prefix_Reference (Work, n)` evaluates `Power_Reference (n − 1)` with `n − 1 ≥ 804` [K-203, K-65]. X3: CL-1 frees and re-raises. The original would also fail on these inputs, because its binary accumulation reaches at least `256**(n−1)` (guard: top byte nonzero) | OPEN (D2) |
| IM-5: decimal `2**6432`, magnitude `2**6432 − 1`, n = 804 [K-152] | the original decimal accumulation (`:451`) at the last digit | the same statement, now the ghost copy in `Decide_Work`, at the last digit, before `Multiply_Add` is called | OPEN (D2) |
| RL-1: 803-byte padding | none | none (D1 adds cost only) | READY expected; cost OPEN: at least `454992179073696` PRI for `Context_Changed`'s `Compare` alone [K-172] |
| RL-2, RL-3 (804 and 1000 bytes); RL-4a, RL-4b, RL-6 (quantities of 805 bytes) | `Shape (Before, …)` → `T.Nonnegative_Valid (Data, State.Capacity)` (`core/resource_run_ledger.ads:226`) → `Is_Negative`'s Post → `Value` → `Magnitude` → `Prefix_Value` → `Prefix_Value_Worker`, at `core/resource_quantities.adb:181` (`Place := To_Big_Integer (256) * Previous_Place`) in the iteration `Completed = 803` [K-204]: `256 * 2**6424 = 2**6432` [K-185] | the same; D1 changes nothing before `Shape` | OPEN (D2) |
| RL-24 (direct Ada, F35) | none: completes with False | `Lemma_Column_Step`'s loop invariant at `Offset = 802` [K-207], when the L-side prefix `Side_Sum` first includes the 257th positive operand, row 513 [K-208]. 256 operands sum to `2**6432 − 256`, which is representable [K-209]; 257 exceed `2**6432` [K-183]. Under the §5.6 LA-1 body plan | **D1-introduced; OPEN** (O-GHOST-HORIZON-A) |

Release-build counterparts: IM-1 True; IM-2/3/4/8/10 computed post-D1 (pre-D1 255 / `Invalid_Request`); IM-5 False
post-D1; RL-1..RL-6 decided post-D1 (pre-D1 `-1` for RL-2..RL-6); RL-24 False in both.

### 9.7 Withdrawn or qualified statements

- v2: "exact decision; time cost only" (v2:1311) is qualified to "release scenario, source-level design; subject to
  O-NATIVE, transport copies and physical resources".
- v2: "After D1, native code accepts every length" (v2:1455) is withdrawn.
- v2: "the same place the original … failed" (v2:1322-1323) is withdrawn (V2-F13); §9.6 records the places.
- v2: "Fewer per-iteration invariants" as a D2 mitigation (v2:1333-1335) is withdrawn. Original checked assertions are
  never deleted merely because a static proof closes.
- v2: "No other exit exists after allocation" (v2:1087-1089) is withdrawn (§7.1).
- v3: "~L⁴ limb ops per `Q.Value`", the Post-only `Compare` estimate, "A-GHOST-0 multiplies this by about K" and the
  "~N²·K·L⁴" dominant term are withdrawn and replaced by §9.3.1-§9.3.3.
- v3: "twice per mixed request" and the primary-only stage table are withdrawn and replaced by §9.4-§9.5.
- v3: "No new recursive function and no recursion" for Algorithm B is restricted to new declarations (§6.5).
- v3: "`Old_Work` n bytes (primary stack …)" is withdrawn: placement is not established by source (§9.3.5).

## 10. OPERATOR DECISION PACKAGE OD-1: public helpers `Exact_Value`, `Amount`, `Sum` (V2-RC3, R-OD1; unchanged)

The v3 review closed this package (R-OD1). v4 changes only two cross-references: the checks-build failure location
of option (o) is now recorded in §9.6, and option (ii)'s item (5) points at the rebuilt §9.3.

**Obligation.** These public functions return `Valid_Big_Integer`, and their Posts equal the full signed references
(`core/resource_run_ledger.ads:185-213`).

- With the GNAT 16.1.0 runtime they cannot represent results of `2**6432` or more [K-07, K-08].
- In the release body, `Exact_Value` raises on valid spans of 804 or more bytes (V2-F13).
- The checks build fails earlier, at any checked evaluation reaching the limit.
- Release-path unreachability satisfies none of this.
- **No option is selected. The lead makes no recommendation.**

| Option | Owner | What it is | Exact consequences | Evidence it requires | What stays OPEN |
|---|---|---|---|---|---|
| E (no decision) | — | nothing changes | O-HELPERS OPEN | — | everything |
| (o) MSB-first Horner with leading-zero skipping in the `Exact_Value` body | lead (body-only) | Find the highest nonzero digit, then `Value := Value * 256 + Digit` downward. Intermediate values never exceed the final magnitude | **Release-executable mitigation only.** Padded valid spans no longer raise in the release body when the value is below `2**6432`. In the checks build, the unchanged Post `Exact_Value'Result = Q.Value (Data, Item)` (`:186`) still runs `Prefix_Value_Worker`. That advances `Place` and evaluates `Prefix_Reference` and `Power_Reference` through **every** column (`core/resource_quantities.adb:147-203`), so padded spans of at least 804 bytes still fail there (`:181` in the iteration `Completed = 803`, §9.6). Values of at least `2**6432` fail in both builds | proof of the new body against the unchanged Post; the new body's own checked invariant costs; both-build controls at 803, 804 and 1000 padded bytes and at `2**6432 ± 1`, each recorded with its build | O-HELPERS (representation), D2 |
| (i-a) WORLDLINE-owned `SPARK.Big_Integers` | operator | replace `core/spark-big_integers.ads:9-11`, today a rename of `Ada.Numerics.Big_Numbers.Big_Integers`, with an unbounded WORLDLINE implementation | **Model binding.** gnat2why's runtime-unit table names both `ADA_NUMERICS_BIG_NUMBERS_BIG_INTEGERS` and `SPARK_BIG_INTEGERS` [OBS strings]. If a replacement is bound to the mathematical model by name, its executable correspondence is *assumed*: a new trust exception, contrary to `HANDOFF.md:161`, unless independently verified. If it is not bound, every existing proof loses its model. **Direct users.** `Worldline.Resources` withs `Ada.Numerics.Big_Numbers.Big_Integers` directly (`core/worldline-resources.ads:2-6`), as does the pending-component copy (`pending-component/core/spark-big_integers.ads`). A SPARK-rename replacement does not reach them; they must migrate, with re-proof. The light library stays forbidden (`HANDOFF.md:129`) | determination of GNATprove 16.1.0's model binding; an independent full verification of the implementation, with no assumed axioms; migration and re-proof of every direct user; identical public API; full original roster and controls | costs, heap and stack, D2 |
| (i-b) separate WORLDLINE-proved bignum type | operator (API) | an owning digit vector with full SPARK proof against a ghost model | The helpers' result types change, so this is a concrete public API/caller migration. It must preserve every original executable capability, caller and accepted case. It is not the frozen profile | concrete API; caller enumeration (compiler-resolved); ABI and roster consequences; full proofs; equivalent checked functions where contracts call the helpers | costs, D2 |
| (ii) rebuilt GNAT runtime | operator (toolchain identity) | patch `System.Generic_Bignums` and `System.Shared_Bignums`, rebuild the runtime from the GCC 16.1.0 sources, relink the encapsulated `libworldline_core` (`core/worldline_core.gpr:81`) | **Not "only allocation can fail" as v2 claimed.** Required: (1) the record layout `Bignum_Data (Len : Length)` with representation clause `Len at 0 range 0 .. 23; Neg at 3 range 0 .. 7` (`RT/s-shabig.ads:58-70`), plus the `Length` subtype (`:46`) and the `Digit_Vector` index (`:55`); (2) every base, index and length expression, for example `X.Len + Y.Len` (`RT/s-genbig.adb:580`), shift lengths (`:423, :456`), `Normalize` (`:1178-1195`), `Big_Exp`'s limit (`:303-332`), `To_Bignum`; (3) automatic digit vectors on the primary stack proportional to operand size: `Sum` (`:135`), `Diff` (`:177`), `Result` (`:364, :388, :423, :456, :580, :778`). Removing the limit turns them into stack-exhaustion failures unless they are rewritten; (4) quadratic `Big_Mul` and `Div_Rem` time; (5) the full checked costs of F29 and §9.3 (rebuilt in v4), now unbounded by representation; (6) any compiler-front-end dependence on the bignum layout (for example overflow mode ELIMINATED) audited | patch specification and diff; a GPT-6.1 review; a proof-model refinement argument for the patched operations; reproducible rebuild recipe, runtime, relink and loaded identities; both-build boundary controls on `Exact_Value`, `Amount` and `Sum`; the complete original roster on the new identity; cost measurements without caps; explicit operator approval of the identity change, which is not acceptance. The header records GPL with the Runtime Library Exception (`RT/s-genbig.adb:11-25`); no legal determination is made here | heap and stack exhaustion, time, D2 cost |
| (iii) Ghost-only retirement or removal of the helpers | — | — | **Incompatible.** It removes the original executable value-returning capability. It is a requirement change, not an eligible closure, even with operator approval (R-OD1) | — | — |
| (iii') executable successor API added alongside | operator (API) | new executable digit-wise functions; the originals remain executable | Closes nothing by itself. The originals keep O-HELPERS | every original capability and accepted case preserved; separate review | O-HELPERS |

## 11. OPERATOR DECISION PACKAGE OD-2: Python decimal-integer correspondence (V2-RC4, R-OD2, V3-RC1)

No setting or code was changed. No WORLDLINE module was imported. **No option is selected.** The 640-digit chunk
guard that the v3 review accepted is kept.

### 11.1 Facts (census corrected; V3-F2, V3-F3)

- **JSON operations** (Appendix A.2-A.5, A.7):
  - v3 universe: 193 operations, that is the 192 direct sites plus the alias `scripts/decisive_evaluation_test.py:264`
    (`_json.dumps`, `import json as _json` at `:260`) [K-79].
  - Scope partition: 122 PROD-RUNTIME, 2 INLINE-CHILD, 10 PROD-PROTECTED, 25 ORIGINAL-CONTROL, 3 BUILD-TOOL and
    31 INSTALL-RELEASE-SCRIPT [K-80, K-81].
  - Extended to all 300 Python files of C5 [K-84]: 2 ROOT-TOOL operations and 254 ORIGINAL-TEST operations, 449 in
    all [K-88, K-89]. 170 are in routed or bounded scopes [K-86]; 279 are in unchanged originals [K-87].
  - The census is scope-aware: aliases, from-imports, assigned names, partials, encoder and decoder classes and
    instances, forwarded references, dynamic `getattr` and other JSON libraries. It is still static (Appendix A.2
    lists its limits), so it is a stronger minimum census, not a data-flow proof. PY-13 re-runs it.
  - Every routed operation is a `json.dumps` or `json.loads` call; no routed scope calls `json.dump` or `json.load`
    [OBS grep].
  - Settings: the alias uses `indent=2`, an existing combination. The distinct combinations are in Appendix A.5.
- **Non-JSON conversions** (Appendix A.8, extended): the v3 categories; stdlib text parsers with an internal decimal
  conversion (11 sites [K-90]); Python-source compilation of decimal literals (14 calls [K-190]); and
  `runtime/worldline/checks.py:888-889`.
- **C4/C5** (F33): 299 of the 300 files are byte-identical; `runtime/worldline/proof_manifest.py` differs by a pin-only
  append (Appendix A.1).
- **Interpreter** (F25): admitted configurations are limit 0 or any limit of at least 640; 1 to 639 are refused at
  runtime and fatal at startup; the default is 4300.
- **Interpreter paths** (F30): `json.dumps` uses the C encoder, with or without `indent`; `sort_keys` sorts the original
  items before key coercion; `parse_int` keeps the C scanner; the C and Python encoders have different recursion
  guards.
- **Messages** [OBS strings of `/usr/lib/libpython3.14.so.1.0`, sha256
  `7e88cb35da4d8fc0fd4c3f595483f98765ee59e23ef43d9eb3ebd1e1c5432c65`, linked by `/usr/bin/python3`]: "Exceeds the
  limit (%d digits) for integer string conversion: value has %zd digits; use sys.set_int_max_str_digits() to increase
  the limit"; the formatting variant without the digit count; "invalid literal for int() with base %d: %.200R"; and the
  compiler's "%S - Consider hexadecimal for huge integer literals to avoid decimal conversion limits." Strings are not
  behaviour evidence.
- `parse_canonical` decodes with `json.loads(data.decode("utf-8", "strict"))` (`runtime/worldline/canonical.py:54`) and
  catches only `UnicodeDecodeError`/`JSONDecodeError` (`:55`). A too-long integer raises an uncaught `ValueError`.
  `canonical_bytes` runs the recursive `_validate` first (`:14-38, :41-49`), which also admits only `str` keys.
- **Not host-bounded:**
  - the daemon parses requests with default `json.loads` (`daemon.py:304`) and admits any non-Boolean `int` id
    (`:309-311`);
  - responses go through `canonical_bytes` (`:379`);
  - `client.py:61` parses responses with default `json.loads`;
  - `cli_main.py:105, 109` print results with `json.dumps(…, indent=2, sort_keys=True, ensure_ascii=False)`.

### 11.2 E0: no decision

O-PYTHON stays OPEN. Current behaviour, from source:

- A decimal integer longer than the configured limit raises `ValueError`, at parse or at serialize.
- In `_dispatch_line`, a too-long request id escapes the inner `except` and reaches the generic handler, which answers
  `INTERNAL_ERROR` (`daemon.py:353-357`).
- A result containing such an integer fails inside `_send` → `canonical_bytes` (`:379`). The same handler then answers
  `INTERNAL_ERROR`, and that answer can itself fail when the id is too long.
- `tomllib.loads` lets the `ValueError` of `int(…, 0)` (`/usr/lib/python3.14/tomllib/_re.py:110-113`) escape: the call
  at `_parser.py:730` is not wrapped [OBS]. One long decimal integer anywhere in a captured `Cargo.toml` or
  `pyproject.toml` fails the whole parse (`runtime/worldline/environment.py:217, 236`).
- An `argparse` option with `type=int` reports "invalid int value" and exits with a usage error, because `argparse`
  converts the `ValueError` (`/usr/lib/python3.14/argparse.py:2664-2668`).
- Every such outcome is an OPEN failure, never an accepted refusal. A finite higher limit, catch-and-refuse, or a native
  size cap would not close the obligation.

### 11.3 E1: interpreter-wide unlimited (`int_max_str_digits = 0`) with exact process-class coverage

Every interpreter that executes a routed-scope operation belongs to exactly one class (Appendix A.9). Classes C12-C14
are new in v4; C1-C11 are unchanged from v3.

| Class | Processes | Interpreter start | Exact change | Guarantee |
|---|---|---|---|---|
| C1 launcher-started | `cli/worldline`, `cli/worldline-relocate`, `daemon/worldlined` (`#!/usr/bin/env python3`, not isolated) | re-executed interpreter | insert `sys.set_int_max_str_digits(0)` right after `import sys` (`cli/worldline:3`, `daemon/worldlined:3`) and before `from worldline… import` (`:18`) | set before any WORLDLINE import; `pathlib` alone is imported earlier and does no workload conversion |
| C2 service | `daemon/worldlined.service` (`ExecStart=%h/.local/bin/worldlined`) | via C1 | none beyond C1 | covered by C1. An `Environment=` setting alone would not reach isolated children |
| C3 direct module `__main__` | `runtime/worldline/daemon_main.py:106`, `cli_main.py:658`, `relocate.py:1146`, `linux/namespace_lifetime.py:712`, `linux/private_evaluator.py:2755` | re-executed only if run as `python -m` or as a script | if any is a production entry, launch with `-X int_max_str_digits=0`. A first-statement call in `__main__` is weaker: module imports (`daemon_main.py:3-11`) run before it, and an import-time conversion such as `simulation.py:30`'s source would precede it | the production entry inventory must state which of these run; each needs `-X` |
| C4 trusted helpers | `trusted_inline` (`revalidate.py:461`, `finalize.py:505`, `simulation.py:183`); `trusted_script` (`linux/kernel_role_observer.py:624, 732, 1528`; `linux/systemd.py:276`; `linux/namespaces.py:346`; `linux/private_evaluator.py:1781, 2020`) | re-executed with `-I -S`; the environment is ignored (F25) | `ISOLATION_FLAGS = ("-I", "-S", "-X", "int_max_str_digits=0")` (`runtime/worldline/trusted.py:41`) | the startup setting precedes all code. Consistent changes are required to `checkRunnerInterpreter` / `trustedStartupFlags` (`runtime/worldline/validation.py:240-245`) and to any test asserting the tuple |
| C5 in-process `runpy` | `linux/private_evaluator.py:53-56, 2008` | inherited | none | inherits from the C4 host interpreter |
| C6 examiner role | runs in-process in the private evaluator (`linux/private_evaluator.py:2742-2752`; argv policy `:1026-1028`) | inherited | **to preserve the examiner-isolation policy exactly**, the examiner role path restores the pre-E1 value (`sys.int_info.default_max_str_digits`) before entry code. The alternative, examiner inherits unlimited, is an explicit operator choice | WORLDLINE parses examiner reports in C1/C4 interpreters, which are covered |
| C7 re-executed payloads | `os.execv` for worker and candidate roles (`linux/private_evaluator.py:2750`) | candidate programs | none | candidate interpreters are not WORLDLINE parse paths and are not changed |
| C8 protected services | `protected-startup/launcher.py`, `owner_provision_bootstrap.py`, `protected-resource/run_service.py`, `gate_bridge.py`, `protected-runtime/approved_source_loader.py` | the operator's interpreter under `-I -S -B`; the flags are bound in the early envelope (`protected-startup/OPERATOR.md:70-90`) | either add `-X int_max_str_digits=0` to the operator-bound flag set (operator custody and re-provisioning), or set the limit in approved source before the first parse (for example before `launcher.py:26`), which changes approved-source pins | operator custody required in both forms |
| C9 control campaigns | `protected-*/controls/run_campaign.py` (argv `-I -S -B` at `:156` / `:176`) | re-executed | none: original controls stay byte-identical; C8's source-level form covers the helpers they start | additive PY controls observe the setting |
| C10 install/release scripts | `scripts/*.py` run by `install.sh` (for example `preflight.py`, which parses prepared transactions at `:125`), and `scripts/decisive_evaluation_test.py` (the alias site, row 193) | re-executed | for each script that parses or formats WORLDLINE data: `sys.set_int_max_str_digits(0)` at start, or a reviewed demonstration under §11.4.3's criteria | — |
| C11 native embedding | `native/examiner_guard.c` is a CPython extension; it reads configuration (`:1958`) and starts no interpreter (no `Py_Initialize` found) | inherits from its host | none | — |
| **C12 build tool (new; V3-RC1 c)** | `native/build_guard.py`, run by the Root native-build action as `/usr/bin/python3 -B …/native/build_guard.py <fresh output dir>` [OBS argv form, `W/outputs/phase1-status.json:249-254`, recorded for the `integrated-ordinary-v8` tree, whose `build_guard.py` has the same sha256 as C5's, `949f917d…07d7`] | a direct interpreter without `-I` | **none needed, by a reviewed absolute-magnitude bound** (Appendix A.5 rows 160-162): its only integer operands are `st_size` values, bounded by `2**63 − 1 < 10**19` [K-94] (at most 19 digits [K-95], 621 digits inside the minimum limit [K-96]), and a return code of 0. It performs no decimal parse | holds under every admitted configuration. If review does not accept the bound, the alternative is `-X int_max_str_digits=0` in the Root action's argv, an operator-owned Root-action change |
| **C13 root tools (new)** | `refresh_contract_pins.py`, `verify_proof_manifest.py` (developer, CI and release tools) | direct interpreter | `sys.set_int_max_str_digits(0)` immediately after `import sys`, before the first parse or source compilation | row 195 has no lexical bound and must be configured (E1) or routed (E2); row 194 has no integer operand |
| **C14 original test runners (new)** | the interpreters running `tests/` and the original campaigns | as the operator runs them | none: original tests stay byte-identical and unconfigured; WORLDLINE processes they start are covered through C1, C4 and C8 | additive PY controls run in configured interpreters and observe the setting (PY-3) |

E1 consequences:

- The guard is removed for all conversions in covered processes, including untrusted local requests, peers and
  examiner reports.
- CPython 3.14 converts large values superlinearly (`/usr/lib/python3.14/_pylong.py:1-13`).
- Cost evidence must meet the original target without a new cap or refusal (O-PY-COST).
- Every touched pinned file needs pin regeneration.
- The stdlib parsers (§11.4.5) and source compilation are covered in configured classes, because the setting is
  interpreter-wide.

E1 evidence:

- a per-class startup observation that `sys.get_int_max_str_digits() == 0` before the first relevant conversion, for
  C1, each C4 helper kind, C8, C10 and C13;
- a C6 observation that the examiner sees the original default;
- for C12, either review acceptance of the bound or the argv observation;
- the PY controls (§12.5).

### 11.4 E2: scoped codec, with the interpreter limit kept

**Reference semantics R∞.** For each routed call, the target behaviour is that of the same call in the same pinned
CPython 3.14.7 with the limit set to 0. The codec must return byte-identical text wherever R∞ returns, and raise the
same exception class, with the same message and notes, wherever R∞ raises. Where today's limited interpreter succeeds,
R∞ and today agree, so the codec agrees with today.

#### 11.4.1 Parse

- At each `json.loads` site, add `parse_int=decimal_int` and preserve every existing keyword (Appendix A.5). For
  `canonical.py:54` the exact expression becomes `json.loads(data.decode("utf-8", "strict"), parse_int=decimal_int)`.
- `json.loads` with a keyword builds `JSONDecoder(**kw)` (`json/__init__.py:349-365`), which stores
  `parse_int or int` (`decoder.py:329`) and keeps the C scanner (`scanner.py:73`). The scanner passes the whole
  validated literal `-?(0|[1-9][0-9]*)` to `parse_int`.
- `decimal_int (s)` splits the digits into chunks of **at most 640**. 640 is the minimum admitted limit, so every
  `int(chunk)` is legal under every admitted configuration (0 or ≥ 640; F25). Example: a 4301-digit literal [K-43] gives
  six 640-digit chunks and one 461-digit chunk [K-45].
- It recombines by divide-and-conquer, `value = high * 10**len(low) + low`, using only integer arithmetic, which has no
  limit. It restores the sign. `"-0"` gives 0, exactly as `int` does, so canonical re-encoding still refuses `"-0"`
  (`canonical.py:58`).
- Requirement: `decimal_int (s) == int (s)` under R∞ for every scanner literal s. That is shown by construction and
  review, then controlled by differential tests (PY-2).
- **Non-JSON parse sites** (`int(x)` on decimal text, `argparse` `type=int`) need a different helper,
  `decimal_text_to_int`, because they receive arbitrary text. It must reproduce `int(s)` with base 10 under R∞ exactly:
  - surrounding Unicode whitespace, an optional sign, PEP 515 underscores (single, between digits only) and Unicode
    decimal digits are accepted exactly as `int` accepts them;
  - every other text raises `ValueError` with the message `invalid literal for int() with base 10: %.200R` of the
    original string, as `int` does [OBS strings above];
  - as an `argparse` type its `__name__` must be `'int'`, so that the message `invalid int value: '…'`
    (`argparse.py:2664-2668`) is unchanged;
  - PY-14 controls the grammar differentially against `int` inside the limit.

#### 11.4.2 Serialize (V3-RC1 a, V3-F1)

Replace `json.dumps(value, **settings)` with `codec_dumps(value, **settings)`. Requirements, each checked against
R∞:

| Id | Requirement |
|---|---|
| S-1 | Byte-identical output for every settings combination of Appendix A.5: `indent` (int or str), `separators`, `sort_keys`, `ensure_ascii`, `allow_nan`. An unsupported keyword raises the same `TypeError` as `json.dumps` |
| S-2 | Integers and `int` subclasses (not `bool`) are formatted as `int.__repr__ (v)`, ignoring any subclass `__repr__`, as both encoders do. The codec computes the same text by divide-and-conquer `divmod` by `10**(640·2^j)`, converting each chunk of at most 640 digits with `str()` and zero-padding inner chunks. `True`, `False`, `None` and floats are formatted exactly as `json` does (`floatstr`, honouring `allow_nan`, with its `ValueError` text) |
| S-3 | **Key order.** With `sort_keys`, the item order is the result of `sorted(dct.items())` on the **original** dict items, evaluated exactly as `json/encoder.py:357-358` does, before any key is coerced. Integer keys therefore sort numerically, never by their decimal text. v3's "sort_keys by code point" is withdrawn |
| S-4 | **Mixed-key failure.** When that sort raises (for example `TypeError` for incomparable `int` and `str` keys), the same exception propagates unchanged, before any key is coerced and before any output is returned. `codec_dumps` returns a whole string or raises; it never yields partial output |
| S-5 | **Key coercion**, in this order, as `encoder.py:361-382`: `str`; `float` through `floatstr`; `True`/`False`/`None`; `int` through `int.__repr__` (chunked as S-2); then `skipkeys`; else `TypeError("keys must be str, int, float, bool or None, not …")` with the same text |
| S-6 | **Strings** are escaped by `json.encoder.encode_basestring_ascii` or `encode_basestring`, selected by `ensure_ascii` exactly as `encoder.py:221-224`, so escaping is the reference's own code |
| S-7 | **Circular references** raise `ValueError("Circular reference detected")` at the same traversal point as R∞ when `check_circular` is in effect |
| S-8 | **Unsupported objects** raise the same `TypeError` (`Object of type … is not JSON serializable`), with the same PEP 678 notes that the reference attaches while unwinding (`encoder.py:330, 417, 457` in the Python encoder; the C encoder's notes are checked by PY-9) |
| S-9 | **Depth.** The codec raises no `RecursionError` where R∞ succeeds, and at a depth where R∞ raises `RecursionError` the codec's behaviour is recorded (E2-a/E2-b below) |
| S-10 | **Traversal order.** Where several failures exist in one value, the codec raises the one R∞ raises first, because it traverses in R∞'s order (list order; dict insertion order, or S-3's order with `sort_keys`) |

Sub-options (none selected):

- **E2-a: reuse CPython's pure-Python encoder.** `json.encoder._make_iterencode` with its `_intstr` hook, a private API
  pinned to CPython 3.14.7. Additional evidence:
  - the C encoder (the reference for `json.dumps`) and the Python encoder must be shown to agree on S-1..S-8. The C
    encoder's source is not installed, so this is differential evidence (PY-4, PY-8, PY-9) plus a review of the
    CPython 3.14.7 `Modules/_json.c` source obtained separately;
  - **depth:** the Python encoder recurses through generator frames, roughly two per nesting level, under the Python
    frame limit, while the C encoder uses the C-stack guard (F30). E2-a can therefore raise `RecursionError` at depths
    where R∞ succeeds. At `canonical_bytes` sites the recursive `_validate` runs first under the same Python limit,
    which narrows but does not remove the gap, because `_validate` uses one frame per level. E2-a is eligible only
    with evidence that no admitted value reaches the gap at any routed site (PY-11), or with an iterative depth
    strategy, which is E2-b.
- **E2-b: a complete WORLDLINE encoder (corrected).** It implements S-1..S-10 directly with an explicit iterative stack,
  so it has no recursion limit of its own. Consequence: where R∞ raises `RecursionError` from the C-stack guard, E2-b
  succeeds. That is a failure-to-success difference; it is recorded, not hidden, and needs operator acceptance as a
  behaviour change. No original control is known to assert that failure (Appendix A.7).
- **R-OVR routing (an option for either).** `codec_dumps` calls the original `json.dumps` unchanged unless an iterative
  pre-scan finds, among the values or keys that `json.dumps` would format, an `int` (not `bool`) with `|v| ≥ 10**L`,
  where `L = sys.get_int_max_str_digits()` and `L > 0`. Only then does the codec path run. For every value without
  such an integer, behaviour, including depth and every failure, is the original's exactly. The pre-scan tracks
  visited containers so that a cycle cannot loop, and it never raises: unsupported objects are left for the chosen
  path to report. The codec path must still meet S-1..S-10 for the values it handles.

Existing failure classes outside the codec are preserved: `_validate` still runs first in `canonical_bytes`. Finite
byte-differential tests inside the old limit are controls. They do not prove an unbounded encoder; the correspondence
argument is by construction plus review.

#### 11.4.3 Sites and exclusion precision (V3-RC1 d)

- Every PROD-RUNTIME, PROD-PROTECTED, INSTALL-RELEASE-SCRIPT and ROOT-TOOL operation moves to the codec, or carries a
  reviewed demonstration of one of the two forms below. "Below 10**640" alone no longer suffices.
  - **Formatting** (`int` to decimal text: JSON values and keys, `str`, `repr`, `format`, f-string fields, `%`-format,
    lazy `logging` arguments): an **absolute-magnitude bound**. Every integer that reaches the conversion satisfies
    `−10**640 < v < 10**640`, that is, `|v|` has at most 640 digits. A one-sided `v < 10**640` is insufficient.
  - **Parsing** (decimal text to `int`): a **lexical digit-count bound**. Every admitted input text has at most 640
    decimal-digit characters in the converted literal, counting leading zeros and excluding sign, whitespace and
    underscores. A bound on the parsed value is insufficient: `'0'*640 + '1'` has value 1 and 641 digit characters
    [K-98]. For JSON the bound must hold for every admitted byte string, including peer, candidate and tampered
    inputs.
- Such a demonstration is an audit result about where a value or text comes from. It is never a cap, and it never
  filters inputs.
- BUILD-TOOL: the reviewed bound of C12 (Appendix A.5 rows 160-162).
- INLINE-CHILD sources must inline the codec text, because trusted helpers import the standard library only
  (`runtime/worldline/trusted.py:31-33`), or carry such a demonstration.
- ORIGINAL-CONTROL and ORIGINAL-TEST files stay byte-identical.
- PR sites are not excluded: the daemon request parse, the client response parse and CLI output are covered.
- Protected sites under C8 custody need operator re-provisioning of approved sources.
- The alias site (row 193) formats only the literal `1` and Booleans in its JSON; its f-string `detail` fields are
  non-JSON formatting candidates (§11.4.4).

#### 11.4.4 Non-JSON conversions (O-PY-AUDIT)

- The universe is Appendix A.8 (extended in v4).
- Each candidate whose operand can be a workload-derived `int` or decimal text either routes through `decimal_str` /
  `decimal_text_to_int`, or carries a demonstration of the matching §11.4.3 form.
- The classification is OPEN. No site is excluded by module role.

#### 11.4.5 E2-T: stdlib parsers and source compilation (new; F31)

| Category | Sites | E2 disposition options (none selected) |
|---|---|---|
| `tomllib.loads` | `runtime/worldline/environment.py:217, 236`, on captured workspace `Cargo.toml` and `pyproject.toml` | **T1** unrouted: eligible only with a lexical digit-count bound over every admitted workspace file; none is available, because the files are workspace content. **T4** hybrid: the process classes that run the environment capture are configured as under E1, while E2 covers the rest; per-call toggling stays rejected (§11.5). **T5** a WORLDLINE-owned TOML parser, or a pinned copy of `tomllib` whose decimal conversion calls `decimal_text_to_int`, with byte-identical results and identical `TOMLDecodeError` behaviour, under separate review. Catch-and-refuse and a pre-filter are rejected |
| `argparse` `type=int` | `runtime/worldline/cli_main.py:371, 380, 414, 415`; `scripts/prune_backups.py:47`; `scripts/release_gate.py:226, 227` | `type=decimal_text_to_int` (§11.4.1), with `__name__ == 'int'`, or the C1/C10 configuration of E1 for those processes |
| `ast.literal_eval` | `refresh_contract_pins.py:30`; `runtime/worldline/examiner_audit.py:403` | literal evaluation compiles the text; route by a lexical bound on the evaluated source, or configure the class (C13, and the class running `examiner_audit.py`) |
| source compilation (`ast.parse`, `compile`, `exec`) | `refresh_contract_pins.py:23, 55`; `scripts/engine_codes.py:47`; `runtime/worldline/examiner_audit.py:382, 459`; `runtime/worldline/executed.py:369`; `runtime/worldline/linux/private_evaluator.py:342, 367, 383, 814, 849` | the compiler converts decimal literals under the limit; no hook exists. Options: a lexical bound on the compiled source, or configuring the class. The two `exec` calls in the original campaigns stay byte-identical |
| `decimal` | `runtime/worldline/checks.py:888-889` (`Decimal(str(…))`) | format with `decimal_str`, or demonstrate an absolute-magnitude bound |

### 11.5 Rejected

| Rejected item | Reason |
|---|---|
| Per-call toggling of the limit | a race: the setting is per interpreter and the daemon is multithreaded (`runtime/worldline/evaluation_terminal.py:19`) |
| A finite higher limit | not closure |
| A new size cap or "size admission" presented as a cost repair (v2:1408-1410) | withdrawn |
| Catching `ValueError` as a refusal, including around `tomllib` | turns a required success into a refusal |
| v3's E2-b "sort_keys by code point" | changes integer-key order and mixed-key failures (V3-F1) |

### 11.6 What stays OPEN

O-PYTHON (no option selected), O-PY-AUDIT (the A.8 classification), O-PY-COST (conversion costs without caps),
O-PY-T (the E2-T disposition), O-PY-DEPTH (E2-a depth evidence, or acceptance of E2-b's failure-to-success
difference) and O-CENSUS (the static census limits; PY-13).

## 12. Controls: complete fixtures and source-to-control coverage map (V2-RC5, V3-RC2)

### 12.0 Rules for every control

- Every control is new and additive. Original controls stay byte-identical: `tests/test_resource_run_ledger_v1.py`,
  `tests/test_finalization_kernel.py`, `artifact-tests/test_canonical_artifacts.adb` and the 52-action ordinary roster.
- **All controls are unrun.**
- Each control runs in both builds.
- Expected values are **reference-evaluated**: each status is derived by walking the whole `Decision_Reference` or
  `Contained_Reference` in priority order. Arithmetic is JACKAL (§15).
- "Pre-D1" columns are source deductions, not observations.
- A checks-build failure is recorded as OPEN (D2, or O-GHOST-HORIZON-A for RL-24), never as a pass, and its location is
  recorded (PO-N8).
- Every fixture states its complete row arrays and totals. Identifiers that are not defined here carry no coverage
  credit; **RL-8 and RL-9 are unused identifiers** (V3-RC2 h).

The C-export fixtures use the original test helpers `row`, `state`, `observation` and `request`
(`tests/test_resource_run_ledger_v1.py:25-49`). Defaults:

- scope `SCOPE`;
- `capacity=20`, `held=0`, `charged=0`;
- `ledger_head=b'head-<epoch>'`, `universe_head=b'universe-head'`;
- row identities derived from the row name;
- `planned_unit` present unless the state is `RESERVED`;
- `observed_usage=None`.

### 12.1 RL-1, RL-2, RL-3: padded READY at 803, 804 and 1000 bytes (V2-F17; RL-1 wording corrected, V3-RC3 g)

**Base fixture.** This is the original control `test_present_genesis_zero_reserves_before_launch`
(`tests/test_resource_run_ledger_v1.py:59-61`):

- `before = state(0)`;
- `first = row()`, which is Held, Reserved, amount 10, resource epoch 0, parent absent;
- `after = state(1, held=10)`;
- `Before_Rows = ()`, `Proposed_Rows = (first,)`, `Observed = ()`;
- request `request(before, first)` (`RESERVE`).

**Padding edit.** This follows the original raw-edit pattern of `:201-219`:

1. Call `owned = kernel.prepare(…)`.
2. For each quantity below, append to the arena the value's minimal little-endian bytes followed by zero bytes up to
   length P (P = 803, 804 or 1000). A zero value becomes P zero bytes.
3. Point the descriptor's `first` (1-based, as `_span` at `runtime/worldline/resource_run_ledger.py:149-157`) and
   `length` at that encoding.
4. Call `kernel.call` with the extended arena.

The quantities padded are:

- `packet.before_state.capacity` (20), `.held_total` (0), `.charged_total` (0);
- `packet.proposed_state.capacity` (20), `.held_total` (10), `.charged_total` (0);
- `proposed_rows[0].amount` (10);
- `packet.intent.new_row.amount` (10).

Epochs and identities are unchanged.

**Reference walk.** The value-dependent predicates see quantities only through `Span_Valid` and `Value`. That covers
`Nonnegative_Valid` (`core/resource_reservation_transition.ads:135-138`), `Compare` (its Post), `Same_Epoch`,
`Is_Successor`, `Same_Row` and the reference sums. Padding inside the arena preserves both, so the status equals the
base fixture's status [LEAD; PO-C1]. In priority order (`core/resource_run_ledger.ads:377-443`):

| Branch | Result | Why |
|---|---|---|
| `Unknown_Kind` | no | `R.Kind = Reserve` |
| `Invalid_Before` | no | `Shape (before, ())`: context and epoch valid; totals and capacity nonnegative and valid; no rows |
| `Invalid_Proposed` | no | `first` satisfies `Row_Valid`: Reserved, no planned, actual, cgroup or invocation; amount nonnegative and valid. Same context. Row epoch 0 compares `Less` than state epoch 1. A single reservation |
| `Native_Roster_Invalid` | no | lengths 0 = 0 |
| `Request_Invalid` | no | all ids valid; binding valid; reservation, operation and owner agree |
| `Stale_Epoch` | no | `Same_Epoch (0, 0)` |
| `Ledger_Head_Mismatch` | no | `head-0 = head-0` |
| `Context_Changed` | no | same scopes; same universe head; `Compare (20, 20) = Equal` |
| `Epoch_Not_Successor` | no | `1 - (0 + 1) = 0` [K-24] |
| `Ledger_Head_Mismatch` (heads equal) | no | `head-0 ≠ head-1` |
| `Conservation_Mismatch` | no | before: `0 = Σ() = 0`, both kinds. Proposed: held `10 - 10 = 0` [K-22] (root Held `first`), charged 0 |
| `Parent_Invalid` | no | no parents. Target `first`: children of `b'row'` sum to 0, and `0 + 0 - 10 = -10 ≤ 0` [K-23] |
| `Capacity_Exceeded` | no | `10 + 0 - 20 = -10 ≤ 0` [K-21] |
| Reserve checks | pass | lengths `0 → 1`; no historical rows; `Same_Row (new_row, Proposed_Rows (Last))`; binding, state `Reserved`, reservation, operation, epoch (0 = 0) and universe head agree; requester equals owner |
| Result | **READY** | |

**Expected outcomes by build:**

| Fixture | Pre-D1 release | Post-D1 release | Checks build (pre and post D1) |
|---|---|---|---|
| RL-1 (P = 803) | READY. `Exact_Value`'s `Place` reaches `256**803 = 2**6424`, which fits: 6425 bits ≤ 6432 [K-03, K-04, K-188] | READY | **READY is the semantic expectation only.** No evaluation reaches the representation limit (§9.6), but the checked cost is OPEN: at least `454992179073696` PRI for `Context_Changed`'s `Compare` of the padded capacities alone [K-172], plus every other checked evaluation of §9.3. Recorded under O-COST-MEASURE; never a pass on time |
| RL-2 (P = 804) | code `-1` → `CoreUnavailable('full-ledger native transport refused')` (`runtime/worldline/resource_run_ledger.py:248`). `Exact_Value (Before.Held_Total)` in `Conserved` reaches `256**804 = 2**6432` [K-65], which needs 202 limbs [K-05, K-06] | READY | fails at `core/resource_quantities.adb:181` in the iteration `Completed = 803`, reached from `Shape (Before, …)` → `Nonnegative_Valid (Capacity)` → `Is_Negative`'s Post (§9.6) → `-1`: **OPEN (D2)** |
| RL-3 (P = 1000) | `-1` / `CoreUnavailable` | READY | the same location as RL-2: **OPEN (D2)** |

### 12.2 RL-4 to RL-7: large and selection fixtures through the C export

| Id | Complete inputs (helpers of §12.0) | Reference walk (first deciding branch) | Expected |
|---|---|---|---|
| RL-4a | budget = `row(b'budget', amount=1, kind='IRREVERSIBLE_BUDGET', state='CHARGED', effect=True)`; hold = `row(b'hold', epoch=1, amount=2**6432-1)`; before = `state(1, charged=1, capacity=2**6432)`; after = `state(2, held=2**6432-1, charged=1, capacity=2**6432)`; before rows (budget,); proposed (budget, hold); observed (`observation(budget, 1, 'REAPED')`,); `request(before, hold)`. This is the original `:173-177` shape with new values | Shape, native roster, request, epoch (`1 → 2`) and heads pass. Conserved: before charged `1 = 1`; proposed held `2**6432 − 1` and charged 1. Contained: no parents; every target `0 ≤ amount`. Capacity: `(2**6432 - 1) + 1 - 2**6432 = 0` [K-33], not exceeded. Reserve checks pass | **READY** post-D1 release; pre-D1 `-1` (sum ≥ `2**6432`); checks OPEN (§9.6) |
| RL-4b | as RL-4a, with the budget amount and both charged totals equal to 2 | Capacity: `(2**6432 - 1) + 2 - 2**6432 = 1 > 0` [K-34] | **CAPACITY_EXCEEDED** post-D1; pre-D1 `-1`; checks OPEN |
| RL-5a | parent = `row(b'parent', amount=255)`; one = `row(b'one', amount=255, parent=b'parent')`; two = `row(b'two', epoch=1, amount=1, parent=b'parent')`; before = `state(1, held=255, capacity=300)`; after = `state(2, held=255, capacity=300)`; before rows (parent, one); proposed (parent, one, two); observed (`observation(parent,1)`, `observation(one,1)`); `request(before, two)` | Conserved: only root Held rows count (`Included` with absent parent), so `255 = 255`. Contained(before) holds. Contained(proposed): target `b'parent'` has children `255 + 1 - 255 = 1 > 0` [K-36]. At column 0 the L side holds 256: digit 0, carry 1; the target digit is 255. The residual carry decides (LA-5) | **PARENT_INVALID** in every build (values are small) |
| RL-5b | as RL-5a, with parent amount 256 and both held totals 256 | Contained: `255 + 1 - 256 = 0` [K-37] (equal carries; State Equal). Capacity: `256 + 0 - 300 = -44` [K-62]. Reserve checks pass | **READY** |
| RL-6 | r1 = `row(b'r1', amount=2**6432-1)`; r2 = `row(b'r2', amount=2**6432-1)`; r3 = `row(b'r3', epoch=1, amount=2**6432-1)`; before = `state(1, held=2*(2**6432-1), capacity=3*2**6432-3)`; after = `state(2, held=3*2**6432-3, capacity=3*2**6432-3)`; before rows (r1, r2); proposed (r1, r2, r3); observed (`observation(r1,1)`, `observation(r2,1)`); `request(before, r3)` | Conserved: `2(2**6432-1) - (2**6432-1) - (2**6432-1) = 0` [K-68] and `3(2**6432-1) - (3·2**6432-3) = 0` [K-35]. Capacity: total equals capacity, not exceeded | **READY** post-D1; pre-D1 `-1`; checks OPEN |
| RL-7a | h1 = `replace(row(b'h1', amount=5, state='RUNNING', effect=True), observed_usage=7)`; r1 = `row(b'r1', amount=9, state='RELEASED')`; n1 = `row(b'n1', epoch=1, amount=3)`; before = `state(1, held=7)`; after = `state(2, held=10)`; before rows (h1, r1); proposed (h1, r1, n1); observed (`observation(h1,1,'LIVE')`, `observation(r1,1,'REAPED')`); `request(before, n1)` | h1 contributes usage: `7 - 5 = 2 > 0` [K-69]. r1 is released, so not counted. Before held `7`; proposed `7 + 3 - 10 = 0` [K-70]. Epoch `2 - (1 + 1) = 0` [K-105]. Capacity `10 - 20 < 0` [K-21] | **READY** |
| RL-7b | as RL-7a, with proposed held 8 (the amount-based total) | **corrected (V3-RC2 g):** the proposed state's held total 8 minus the selected sum `7 + 3`: `8 - (7 + 3) = -2 ≠ 0` [K-102]. Before is unchanged (`7 = 7`) | **CONSERVATION_MISMATCH** |
| RL-7c | b1 = `replace(row(b'b1', amount=5, kind='IRREVERSIBLE_BUDGET', state='CHARGED', effect=True), observed_usage=7)`; n1 = `row(b'n1', epoch=1, amount=3)`; before = `state(1, charged=5)`; after = `state(2, held=3, charged=5)`; **Before_Rows = (b1,)**; **Proposed_Rows = (b1, n1)**; **Observed = (`observation(b1, 1, 'REAPED')`,)**; `request(before, n1)`. Variant: both charged totals 7 | Shape: b1 is Charged, a budget, with effect and planned unit; n1 Reserved; epochs 0 and 1 are at most the state epochs. Native roster: one observation for one before row. Epoch `2 - (1 + 1) = 0` [K-105]. Budget rows never use usage (`Amount_Reference`'s Held test), so charged `5 - 5 = 0` [K-103] before and after; proposed held `3 - 3 = 0` [K-104]. Contained: no parents. Capacity `3 + 5 - 20 = -12` [K-73]. Reserve checks: `Same_Row (b1, b1)` including equal usage; n1 binding, state, epoch `1 = 1`. Variant: before charged `7 - 5 = 2 ≠ 0` [K-69] | **READY**; variant **CONSERVATION_MISMATCH** |
| **RL-7d** (equal usage) | as RL-7a, with h1's `observed_usage=5`, before = `state(1, held=5)`, after = `state(2, held=8)`; rows, observations and request as RL-7a | `Usage_Selected`: `Compare (5, 5) = Equal`, not Greater (`5 - 5 = 0` [K-103]), so the amount 5 is used. Before held `5 - 5 = 0` [K-103]; proposed `8 - (5 + 3) = 0` [K-106]. Contained: no parents. Capacity `8 + 0 - 20 = -12` [K-107]. Epoch [K-105]. Reserve checks as RL-7a | **READY** |
| **RL-7d′** | as RL-7d, but with RL-7a's totals: before = `state(1, held=7)`, after = `state(2, held=10)` | Before held `7` against the selected sum 5: `7 - 5 = 2 ≠ 0` [K-69]; the `Conserved (Before)` conjunct decides first | **CONSERVATION_MISMATCH** |
| **RL-7e** (lower usage) | as RL-7a, with h1's `observed_usage=2`, before = `state(1, held=5)`, after = `state(2, held=8)` | `Compare (2, 5) = Less` (`2 - 5 = -3` [K-108]), so the amount 5 is used. Before `5 - 5 = 0` [K-103]; proposed `8 - (5 + 3) = 0` [K-106]; capacity `-12` [K-107] | **READY** |
| **RL-7e′** | as RL-7e, with the usage-based totals: before = `state(1, held=2)`, after = `state(2, held=5)` | Before held 2 against the selected sum 5: `2 - 5 = -3 ≠ 0` [K-108] | **CONSERVATION_MISMATCH** |

RL-8 and RL-9: unused identifiers; no fixture and no coverage credit.

### 12.3 Direct Ada controls for `Contained` (public; signed, invalid and duplicate domains unreachable through the C export)

These are new Ada test programs. `Data` is a `Q.Byte_Array` with the non-default lower bound 17, as in the original
builder `artifact-tests/test_canonical_artifacts.adb:11-17`. `Rows` uses a non-default first index (5) where marked.

Fields `Contained` does not read are absent or default: Scope, the Binding fields other than `Reservation`, the units
and the epochs. Quantities are written as (sign, bytes). Identities are byte strings in `Data`.

- **INVALID** is a span with `First = Data'Last` and `Length = 2`, which is invalid because `2 > Data'Last - First + 1`.
- **INVALID-H** (new) is a span with `First = Data'Last - 1` and `Length = 3` over two `16#FF#` bytes. It is invalid
  because its Length exceeds the bytes that remain after `First`. A selector or column engine that read an invalid
  span's raw bytes would see a nonzero value; the reference sees 0.

| Id | Rows, in order | Reference walk (`Contained_Reference`, every target) | Expected (reference) | Discriminates |
|---|---|---|---|---|
| RL-11 | R1: Held, Reserved, reservation `r`, parent absent, Amount (−,[01]) | loop 1 vacuous. Target `r`: Σ = 0, and `0 - (0-1) = 1 > 0` [K-28] | **False** | the reviewer's counter-example (unsigned-only comparator) |
| **RL-12** | R1 parent P: Held, Reserved, reservation `p`, parent absent, Amount (+,[03]). R2 child C: Held, Reserved, reservation `c`, parent `p`, Amount **INVALID**, usage present (+,[05]) | loop 1: `Parent_Supports (R1, R2)` holds. Target `p`: C is counted Held and `Value(usage) = 5 > Value(INVALID) = 0`, so the reference selects usage; `5 - 3 = 2 > 0` [K-25] fails. Target `c`: no children, `0 - 0 = 0` [K-27] | **False** | **v1 selector:** `Compare (valid, invalid) = Invalid`, so it selects Amount (value 0); target `p` gives `0 - 3 = -3 ≤ 0` [K-26]; the whole result is **True** |
| **RL-12N** | R1: Held, Reserved, reservation `p`, parent absent, Amount (−,[01]). R2: Held, Reserved, reservation `p` (**duplicate identity**), parent `p`, Amount (−,[03]), usage present **INVALID** | loop 1: R1 supports R2. Target `p`: R2 contributes usage, value 0 (`0 > −3`), so `0 - (0-1) = 1 > 0` [K-28] fails | **False** | **v1:** selects Amount −3. Target from R1: `-3 - (0-1) = -2 ≤ 0` [K-29]. Target from R2: `-3 - (0-3) = 0 ≤ 0` [K-30]. Whole result **True** |
| **RL-12V** (new; invalid usage, nonnegative amount) | R1: Held, Reserved, reservation `p`, parent absent, Amount (+,[02]). R2: Held, Reserved, reservation `c`, parent `p`, Amount (+,[03]), usage present **INVALID**. R3: Held, Reserved, reservation `c0`, parent `p`, Amount (+, Length 0), usage present **INVALID-H** | loop 1: R1 supports R2 and R3. Target `p`: R2 keeps its amount (`0 - 3 = -3`, not Greater [K-26]), R3 keeps its amount (`0 - 0 = 0` [K-27]), so Σ = 3 and `3 + 0 - 2 = 1 > 0` [K-109] fails. Targets `c`, `c0`: no children (`0 ≤ 3`, `0 ≤ 0`) | **False** | a selector that treats an `Invalid` comparison as Greater selects both usages (value 0): `0 + 0 - 2 = -2 ≤ 0` [K-110], whole **True**. A raw-byte reader on R3 changes Σ |
| **RL-12I** (new; invalid/invalid) | R1: Held, reservation `p`, parent absent, Amount (+, Length 0). R2: Held, reservation `c`, parent `p`, Amount **INVALID**, usage present (+, **INVALID-H**) | Target `p`: R2 keeps its amount (`0 > 0` is false), value 0; `0 - 0 = 0 ≤ 0` [K-27] holds. Target `c`: `0 ≤ 0` | **True** | a raw-byte reader of the usage contributes a positive term: whole **False** |
| **RL-12IN** (new; invalid/invalid, negative target) | as RL-12I, but R1's Amount is (−,[01]) and R2's usage is (−, **INVALID-H**) | Target `p`: Σ = 0, and `0 - (0-1) = 1 > 0` [K-28] fails. Target `c`: `0 ≤ 0` | **False** | a raw-byte reader that selects the negative usage contributes `−(raw) ≤ −1`, so `p` holds and the whole result is **True**. With RL-12I this pins the invalid/invalid contribution at exactly 0 in both directions |
| **RL-12S** (new; signed selector) | R1: Held, reservation `p`, parent absent, Amount (+,[01]). R2: Held, reservation `p` (duplicate), parent `p`, Amount (−,[01]), usage present (+,[02]) | loop 1: R1 supports R2. Selection: `2 - (0-1) = 3 > 0` [K-111], so usage 2. Target from R1: `2 - 1 = 1 > 0` [K-112] fails. Target from R2: `2 - (0-1) = 3 > 0` [K-111] fails | **False** | a selector that keeps the amount when the usage is positive and the amount negative (for example `Compare` with swapped operands): target R1 `0-1-1 = -2 ≤ 0` [K-113], target R2 `0-1-(0-1) = 0 ≤ 0` [K-114]; whole **True** |
| **RL-12M** (new; magnitude selector) | R1: Held, reservation `p`, parent absent, Amount (−,[02]). R2: Held, reservation `p` (duplicate), parent `p`, Amount (−,[01]), usage present (−,[05]) | Selection: `0-5-(0-1) = -4 < 0` [K-115], so the amount −1. Target from R1: `0-1-(0-2) = 1 > 0` [K-116] fails. Target from R2: `0-1-(0-1) = 0` [K-114] holds | **False** | a magnitude-only selector picks usage −5: target R1 `0-5-(0-2) = -3 ≤ 0` [K-117], target R2 `0-5-(0-1) = -4 ≤ 0` [K-115]; whole **True** |
| RL-13 | R1: target, reservation `z`, Amount (−, Length 0). R2: as R1 but Amount (−,[00,00]). R3: Held child of `z`, Amount (+, Length 0) | every target's Σ is 0 and every value is 0 | **True** | negative zero, padding, empty |
| **RL-14** | R1: Held, reservation `p`, parent absent, Amount (−,[05]). R2: Held, reservation `c` (distinct), parent `p`, Amount (−,[05]) | Target `p`: `(0-5) - (0-5) = 0` [K-32] holds. Target `c`: no children, `0 - (0-5) = 5 > 0` [K-31] fails | **False** | the child target matters |
| RL-14P | R1: Held, reservation `p`, parent absent, Amount (−,[05]). R2: Held, reservation `p` (duplicate), parent `p`, Amount (−,[05]) | Target `p` (both rows): Σ over parent `p` = R2's −5, and `(0-5) - (0-5) = 0 ≤ 0` [K-32] for both targets. Loop 1: R1 supports R2 | **True** | an unrestricted topology in which every negative target holds |
| RL-15 | R1: target, reservation `t`, Amount span with `First = Data'First` and `Length = Byte_Count'Last` (invalid) | value 0; Σ 0; **zero columns visited** (`Effective_Length = 0`) | **True** | resource edge; LA-11 |
| RL-16 | `Conserved` with `Shape` False (for example R1 with an invalid identity) | `Shape` is False | **False** | unchanged branch |
| RL-17a | R1 parent: reservation `p`, Amount (+,[FF]). R2, R3: Held children of `p` with Amount (+,[FF]) each | Target `p`: column 0 L = 510 = `1*256 + 254` [K-58], so digit 254 and carry 1. R digit 255, so State = Less, but carries 1 > 0 decide Greater; `255 + 255 - 255 = 255 > 0` [K-59]. Children's targets: 0 ≤ 255 | **False** | the residual carry overrides State |
| RL-17b | R1 parent Amount (+,[02]). R2 child (+,[01]) | `1 - 2 = -1 ≤ 0` [K-72]: equal carries, the low digit decides | **True** | equal carries, different low digit |
| RL-18 | P: reservation `p`, Amount (+, Length 0). C1, C2: children of `p`, reservations `c1`, `c2`, Amount (+,[FF]). C3: child of `p`, reservation `q`, Amount (−,[FF]). C4: child of `p`, reservation `q2`, Amount (−,[FF]). G3: reservation `q` (duplicate of C3), parent `q`, Amount (−,[FF]). G4: reservation `q2`, parent `q2`, Amount (−,[FF]). `Rows'First = 5` | Target `p`: L = 510 (digit 254, carry 1) and R = 510 (digit 254, carry 1) plus target 0, so Equal; `255 + 255 - 255 - 255 - 0 = 0` [K-60]. Targets `c1`, `c2`: 0 ≤ 255. Targets `q` (C3 and G3): Σ over parent `q` = −255 ≤ −255. Targets `q2` likewise. Loop 1: P supports C1..C4; C3 supports G3; C4 supports G4 | **True** | signed cancellation; carries on both sides; non-default bounds |
| RL-19 | P: **Budget**, reservation `p`. C: **Held**, parent `p` | loop 1: no earlier supporter of the same kind | **False** | `Parent_Supports` kind conjunct |
| RL-20 | P: Held, **Released**, reservation `p`. C: Held, Reserved, parent `p` | `Counted (C) ⇒ Counted (P)` fails | **False** | counted conjunct |
| RL-21 | P: Budget, **Charged**, reservation `p`. C: Budget, **Terminal**, parent `p` | P Charged and C counted require C Charged | **False** | charged conjunct |
| RL-22 | PH: Held, reservation `p`, Amount (+,[05]). PB: Budget, reservation `p` (duplicate), Amount (+,[05]). CH: Held, parent `p`, Amount (+,[03]). CB: Budget, parent `p`, Amount (+,[03]) | loop 1: PH supports CH and PB supports CB. Target `p`: `S_H + S_B = 3 + 3`, and `3 + 3 - 5 = 1 > 0` [K-61] | **False** | a genuine mixed-kind aggregate. A per-kind comparator would return True (3 ≤ 5 each) |
| RL-23 | `Rows'Length = 0` | vacuous | **True** (`Contained`) | null arrays |
| **RL-24** (new; F35) | P: Held, Reserved, reservation `p`, parent absent, Amount (+, Length 0). Then 514 children [K-184] `C_1 .. C_514`: Held, Reserved, distinct reservations, parent `p`, Amounts alternating (+, X), (−, X), starting with +, where X is one 803-byte run of `16#FF#` in `Data`, the value `2**6424 − 1` [K-188] | loop 1: P supports every child. Target `p`: the signed sum cancels pair by pair [K-187]; every original partial sum is X or 0 [K-186], so `0 ≤ 0` holds. Targets of positive children hold (`0 ≤ X`). The first negative child's target fails (`0 > −X`) | **False** | pre-D1, both builds: False (the original forms no value above `256**803`). Post-D1 release: False. **Post-D1 checks: the D1 ghost fails at the location of §9.6** (257 one-sided magnitudes exceed `2**6432` [K-183]); recorded **OPEN** (O-GHOST-HORIZON-A), never a pass |
| RL-10 | `Exact_Value`, `Amount`, `Sum` called directly on valid 804-byte padded spans and on values of `2**6432` | — | records the **OPEN** O-HELPERS failure. **Not** a passing control until OD-1 is decided | O-HELPERS |

The `Parent_Supports` effect/cgroup conjunct and the earlier-parent order are covered by the original control
`test_parent_must_exist_earlier_and_actual_cgroup_must_be_contained` (`tests/test_resource_run_ledger_v1.py:153-164`).

### 12.4 `Integer_Matches` controls

Direct Ada through the public `Tagged_Matches (A, JSON_Span, Tagged_Span)`, with A built at lower bound 17. Tagged
text is `["int",<sign>,"<base64 LE magnitude>"]`, as produced by `value_bytes`
(`runtime/worldline/evaluation_terminal.py:76-83`).

| Id | JSON text / tagged magnitude | Path exercised | Expected |
|---|---|---|---|
| IM-1 | `"1"` followed by 1936 zeros, with its minimal magnitude (n = 804 [K-150]) | match; `10**1936 < 2**6432` [K-07] | True (pre and post, both builds). **Post-D1 checks must not fail here** (DR-C5, PO-B22; v3's form did, F34) |
| IM-2 | decimal of `2**6432` (1937 digits [K-09]) and its 805-byte magnitude; also `10**1937 - 1` | match beyond the old limit | True post-D1 release; pre-D1 `Storage_Error` → 255 / `Invalid_Request`; checks OPEN at the location of §9.6 |
| IM-3 | `"1"` followed by 1937 zeros (1938 digits [K-10]) | match | True post-D1 release; checks OPEN |
| IM-4 | `"1"` followed by 5000 zeros (5001 digits, 701 beyond the Python default [K-74]; the text is a literal, not converted from `int`); also with the magnitude of `10**5000 + 1` | match; bottom-cell mismatch (difference 1 [K-75]) | True / False (direct Ada only; the export form needs OD-2); checks OPEN |
| IM-5 | decimal `2**6432` against the magnitude of `2**6432 - 1` (n = 804 [K-152]) | **overflow**: `256**804 = 2**6432` [K-65], so the decimal reaches `256**n`; difference 1 [K-66] | False post-D1 release; checks OPEN at the original statement (§9.6) |
| IM-6 | `"256"` vs `[FF]`; `"255"` vs `[FF]`; `"65535"` vs `[FF,FF]`; `"65536"` vs `[00,00,01]`; `"65536"` vs `[FF,FF]`; `"256"` vs `[00,01]`; `"257"` vs `[00,01]`; `"65535"` vs `[FE,FF]`; `"65535"` vs `[FF,FE]`; **`"7"` vs the empty magnitude `""`** | suffix overflow [K-38]; match; match [K-39]; match [K-40]; suffix overflow [K-46]; match [K-63]; bottom mismatch [K-64]; bottom mismatch [K-77]; top mismatch [K-78]; **the guard passes, Work is null, and `Multiply_Add` returns the digit as `Carry_Out` at once: overflow at n = 0** (V3-RC2 i) | False; True; True; True; False; True; False; False; False; **False** |
| IM-7 | guards: `"-5"` with tag `false`; `"5"` with tag `true`; `"0"` with `[int,true,""]`; `"1"` as `"AQA="` (`[01,00]`, high zero byte); `"0"` with `"AA=="`; base64 errors: a length not divisible by 4, a non-alphabet byte, a misplaced `=`, nonzero pad bits (`:302-323`); sign node a string (`["int","true","AQ=="]`); a wrong tag or element count | each guard conjunct reachable through `Tagged_Matches` (`:439-445`, `:494-497`, `:302-323`). The Work-allocation counter stays 0 (W-8a) | all False |
| IM-8 | `"-"` followed by the decimal of `2**6432`, with tag `true` and its magnitude | large negative match | True post-D1 release; checks OPEN |
| IM-9 | `"0"` with `[int,false,""]` | empty magnitude, zero | True |
| **IM-11** (new; middle cell) | `16777215` (8 digits [K-129, K-130]) vs `["int",false,"//7/"]`, the magnitude `[FF,FE,FF]` | the decimal is `255 + 255·256 + 255·256²` [K-118] and below `256³` [K-121], so no carry ever occurs. The magnitude is `16776959` [K-119]: base64 group `16776959` [K-122] with sextets 63, 63, 59, 63 [K-123], where 59 is `'7'` [K-124]; `Binary_At` gives cells FF [K-125], FE [K-126, K-127, K-128] and FF [K-51]. The compare phase from the top: cell 3 agrees, cell 2 differs (difference −256 [K-120]) | **False**, decided at the middle cell |
| IM-10 (plain export) | the original `test_artifact_payload_integer_and_object_order_correspondence` (`tests/test_finalization_kernel.py:179-187`) with `'z'` set to `+(2**6432 + 7)`, and separately `−(2**6432 + 7)` (1937 digits [K-149, K-07]; magnitude 805 bytes, 268 full base64 groups plus one byte [K-131]) | **positive:** the capture is rebuilt through the normal producer path (`replace (row, payload = value_bytes (payload))`, then `self.sealed (capture)`), so every artifact, metadata and identity binding is rebuilt. **Mismatch:** `evidence, environment = self.artifacts (positive_capture)`; the edited capture replaces the payload's first base64 quartet `BwAA` (bytes 07 00 00 [K-132, K-133]) by `BgAA` (06 00 00 [K-134, K-135]), a value that differs only in the bottom cell [K-136]; then `self.kernel.seal (self.with_artifacts (edited, evidence, environment))`, exactly the pattern of the original `test_checks_order_and_validation_context_are_not_hash_only` (`:189-201`). Only the artifact's decimal against the payload's tagged magnitude differs | post-D1 release: promotion True; mismatch `KernelRefused`. Pre-D1: 255 at `seal` / preparation. Post-D1 checks: OPEN at the location of §9.6 |
| **IM-10P** (mixed, `Primary_Only`) | request **REQ-P** = `RawDependencyControls.checkpoint()` (`tests/test_raw_evaluation_default.py:523-532`) with `mode='CANDIDATE_EVALUATION'`, `evaluated_requirement = resulting_requirement = h(8)`, `executed_verifiers = h(9)` and both checkpoints `None`; `tested_root = h(7)` covers the staged content. The bundle is IM-10's positive capture, prepared with `prepare_finalization` and joined with `joined (prepared, REQ-P, agent)` (`tests/test_finalization_kernel.py:224-243`); `agent` as `collapse_values` (`:245-255`). Call `collapse_decide_with_evaluation (REQ-P, primary = prepared, staged = None, agent = agent)` | Decide 1 primary readiness, Decide 2 primary context (§9.5). **F32:** unlike the original `:257-266`, REQ-P supplies `resulting_requirement`, so `Required_Present` holds (`core/worldline-collapse.ads:148-154`) | post-D1 release `AUTHORIZED`. **Mismatch:** after preparation, a raw edit of the prepared native request's arena replaces the one occurrence of `BwAA` by `BgAA`, as the original `:268-280` edits `inputs.config`: `INVALID_REQUEST` with the mark `primary-ready-rejected` and no `finalization.decide` exception. Pre-D1 and post-D1 checks: preparation fails (255); OPEN |
| **IM-10S** (mixed, `Staged_Only`) | request **REQ-S** = `checkpoint()` with `tested_root = None`, `staged_evaluated_requirement = h(8)`, `staged_executed_verifiers = h(9)`, `staged_examined_root = h(7)`; mode `CHECKPOINT_RETURN`, so the mode-1 wire rules hold (`core/worldline-collapse_wire.ads:128-136`). Call with `primary = None, staged = prepared` | Decide 1 staged readiness, Decide 2 staged context. `Staged_Covers` holds once `Decide_Mixed` sets `Staged_Roster_Complete := S_Ready` (`core/evaluation_finalization_c.adb:486`) | post-D1 release `AUTHORIZED`; the raw-edit mismatch gives `INVALID_REQUEST` with `staged-ready-rejected`; pre-D1 and checks as IM-10P |
| **IM-10PS** (mixed, `Primary_And_Staged`) | request **REQ-PS** = REQ-P with `tested_root = h(11)` (primary does not cover) and the staged fields of REQ-S. Two prepared bundles from two IM-10 positive captures, each joined with REQ-PS | Decides 1-4 in the order of §9.5 | post-D1 release `AUTHORIZED`; a raw-edit mismatch in the primary bundle gives `primary-ready-rejected`, in the staged bundle `staged-ready-rejected` (after primary readiness passed); pre-D1 and checks as IM-10P |

In all IM-10 requests, `h(v) = bytes([v]) * 32` (`tests/test_raw_evaluation_default.py:524`). Release-build semantic
expectations are never checked-build success credit.

The guard conjuncts `N.Valid`, `N = Prefix (A, J, 0)`, `N.Form` and `N.After = J.Length` are always satisfied through
`Tagged_Matches` (`:478-482, :494-497`). Proof covers them (PO-B14); no public control can reach them.

### 12.5 Python controls (run only after OD-2 selects E1 or E2; under E0 they record OPEN)

Reference runs of R∞ use a separate interpreter started with `-X int_max_str_digits=0`; the codec under test runs at
limits 640, 4300 and 0.

| Id | Content | E1 / E2 expectation |
|---|---|---|
| PY-1 | `canonical_bytes(10**4300) == b"1" + b"0"*4300` (4301 digits [K-43]); parse round trip; a negative value; `2**20000`; `"01"`, `"-0"` and whitespace still refused; nested lists and dicts with big ints; `value_bytes` round trip | pass |
| PY-2 | E2 only: the same at limits 640 (minimum), 4300 (default) and 0; chunk boundaries at 640 and 641 digits [K-98] | pass |
| PY-3 | E1 only: startup observation per process class C1, C4 (each helper kind), C8, C10 and C13 = 0, before the first relevant conversion; C6 examiner = default; C12 argv recorded or bound accepted | pass |
| PY-4 | E2 only: byte-differential `codec_dumps` against R∞ and against `json.dumps` for every Appendix A.5 settings combination, including Unicode, escapes, key order and duplicates, on values inside the old limit | identical bytes |
| PY-5 | daemon request id with 5000 digits (seven 640-digit chunks and one 520-digit chunk [K-97]); response echoes the id; client parse; CLI print | pass |
| PY-6 | producer-to-native finalization: positive and mismatch controls beyond 4300 digits, through both exports | promotion / `AUTHORIZED`; mismatch refused |
| PY-7 | under E0: the same inputs | recorded **OPEN** (`ValueError`), never a pass |
| **PY-8** (new; integer keys) | for every Appendix A.5 combination with `sort_keys=True`: `{10: 'a', 2: 'b'}` must give `{"2": …, "10": …}` (numeric order: `10 - 2 = 8 > 0` [K-99]; a code-point order would put `"10"` first, since `'2'` exceeds `'1'` [K-100]); `{-1: …, -10: …}` gives `-10` first (`-1 - (0-10) = 9 > 0` [K-101]); `{True: …, 2: …}`; `{1.5: …, 1: …}`; a key `10**5000` with another `int` key; `sort_keys=False` keeps insertion order | identical to R∞ |
| **PY-9** (new; mixed keys) | `{1: 'a', 'b': 2}` and `{10**5000: 'x', 'b': 1}` with `sort_keys=True`, at top level and nested in a list and a dict | the same `TypeError` class, message and `__notes__` as R∞; nothing returned; no limit `ValueError` for the large key, because the sort fails first |
| **PY-10** (new; exclusion probes) | for every site excluded by a demonstration: formatting probes at the edge of its absolute-magnitude bound under limit 640 (for C12, `str(±(2**63 - 1))`); parsing probes with `'0'*640 + '1'` (641 digit characters, value 1 [K-98]) through the site's actual input path, showing that the site is routed or that the text cannot reach it | pass, or the exclusion is withdrawn |
| **PY-11** (new; depth) | nested lists and dicts from depth 1 up to the largest depth at which R∞ succeeds, found by the control, at a `canonical_bytes` site and at an `indent=2` site; at R∞'s first failing depth, the codec's behaviour is recorded | E2-a: identical below the gap, and the gap is shown unreachable, or E2-a is ineligible. E2-b: identical where R∞ succeeds; the failure-to-success difference is recorded. R-OVR: identical everywhere for values without large integers |
| **PY-12** (new; E2-T) | `tomllib.loads` of a `pyproject.toml` whose dependency table contains a 5001-digit integer literal; `ast.parse` of source containing one; `argparse` options with a 5001-digit value and with invalid text | E0: OPEN (escaping `ValueError`, compiler error, usage error). E1-configured classes: parse. E2: per the selected E2-T option; `argparse` messages for invalid text unchanged |
| **PY-13** (new; census) | re-run the Appendix A.2 census on the exact source identity, recording every scanned file's sha256 | totals 193, 2 and 254 (449 [K-88, K-89]) and the alias list reproduce; any new site is OPEN |
| **PY-14** (new; non-JSON helper) | `decimal_text_to_int (s)` against `int (s)` inside the limit and against R∞ beyond it: ASCII and Unicode whitespace; signs; valid and invalid underscores; Unicode decimal digits; empty and invalid text, including invalid text longer than 200 characters (the `%.200R` truncation); 5000-digit text | identical values, exception classes and messages; `argparse` error text unchanged |

### 12.6 Workspace-lifetime controls (W)

Fault injection uses an interposed allocator that fails exactly one selected allocation, identified by call site and
ordinal (§7.4). W-1 to W-9 use the **original small payload integer** (`tests/test_finalization_kernel.py:184`) unless
stated, so that only the injected failure occurs.

| Id | Content | Expectation |
|---|---|---|
| W-1 | X2: allocation failure injected at the Work allocation, plain export | the exception propagates; 255 with `finalization.decide` diagnostics; heap back to baseline. **Native failure: OPEN** |
| W-2 | X3, checks build: an IM-2 magnitude (n = 805) reaches the limit after allocation | CL-1 frees and re-raises; same mapping; no leak; **the actual failing location is recorded** (expected by source: the first decimal-loop invariant, §9.6) |
| W-3 | X4/X5, checks build: saved-copy failure (`Old_Work` on a small thread stack), if the harness admits it | `Storage_Error` handled as W-2, or a hard fault recorded OPEN |
| W-4 | repeated calls mixing success, mathematical False and injected failure | stable heap high-water; final water mark zero |
| **W-5** (rewritten; V3-RC2 e, V3-RC3 f) | mixed export, one injection per run at the Work-allocation ordinal of Decide k (checks `4(k − 1) + 1` [K-141..K-144]; release `k` [PE-20]), by dependency: **P1** `Primary_Only`, k = 1; **P2** `Primary_Only`, k = 2; **S1** `Staged_Only`, k = 1; **S2** `Staged_Only`, k = 2; **PS1..PS4** `Primary_And_Staged`, k = 1..4. Requests REQ-P, REQ-S, REQ-PS of §12.4. Also mixed kinds: an ordinary kind-1 primary with a kind-2 staged bundle, and the converse, where only kind-2 slots reach `Decide` and the ordinals renumber | P1, PS1: `finalization.decide` exception then `primary-ready-rejected`. S1: then `staged-ready-rejected`. **PS2: `staged-ready-rejected`, not a context mark.** P2, PS3: `finalization.decide` exception, `context.seal-rejected`, then `primary-context-rejected`. S2, PS4: `context.seal-rejected`, then `staged-context-rejected`. Every case: `Invalid_Request`; heap at baseline. Native failure: OPEN |
| W-6 | mathematical False (IM-5 through the exports) against a native failure (W-1) | plain export: `Reason ≠ 0` against 255. Mixed export: the same `Invalid_Request`, distinguished by the diagnostic sequence only |
| **W-7** (new; X6) | **W-7a (X6a):** a failure injected at a non-Work allocation inside `Seal`'s Post evaluation, after the body's `Integer_Matches` returned. **W-7b (X6b, X2 of a re-entry):** a failure at the Work allocation of occurrence j ∈ {2, 3, 4} within one Seal (Seal Post `:395`, `Seal_Reference` body `:129`, `Seal_Equation` `:362`), checks build only. **W-7c (X6b, X3 of a re-entry):** a failure at a bignum allocation inside occurrence j's `Decide_Work`, by call site and ordinal | W-7a: no Work outstanding; heap at baseline; 255. W-7b: nothing owned by that invocation; 255. W-7c: CL-1 frees in that invocation and re-raises through the caller's Post evaluation to `Decide`'s handler; 255; heap at baseline. All native failures: OPEN |
| **W-8** (new; X7) | **W-8a:** on every IM-7 guard case and on every X0 path, the Work-allocation counter stays 0. **W-8b (X7-R):** native exhaustion before allocation (for example the `Base64` frame on a tiny thread stack), if the harness admits it. X7-L and X7-A are not manufactured: they are proved unreachable (PO-B19, PO-B20, PO-B1, PO-B3) | W-8a: counter 0, heap unchanged. W-8b: a hard fault or `Storage_Error` with no Work outstanding, recorded OPEN |
| **W-9** (new; lifetime on all mixed paths) | allocation and free counters and heap water marks over the positive and mismatch runs of IM-10, IM-10P, IM-10S and IM-10PS, in both builds | allocations equal frees; final water mark zero. A checks-build failure of those runs is OPEN (§9.6) |

### 12.7 Source-to-control coverage map

| Source construct (C5) | Controls | Proof |
|---|---|---|
| `Normalized` invalid → empty (§5.3) | RL-12 (invalid amount), RL-12N, RL-12V (invalid usage), RL-12I, RL-12IN (both invalid), RL-15 (invalid target) | LA-9 |
| `Usage_Selected` selector matrix | usage greater: RL-7a, RL-12, RL-12S; equal: RL-7d, RL-7d′; lower: RL-7e, RL-7e′, RL-12M; Budget ignored: RL-7c; invalid combinations: RL-12, RL-12N, RL-12V, RL-12I, RL-12IN | LA-9 |
| Signed operands, negative zero, padding | RL-11, RL-12N, RL-12S, RL-12M, RL-13, RL-14, RL-14P, RL-18; RL-1..3 | LA-7, LA-8 |
| Carry propagation and both-side carries | RL-5a, RL-6, RL-17a, RL-18 | LA-3, LA-6 |
| Equal carries with a different low digit; residual carry overriding State | RL-17b; RL-17a, RL-5a | LA-4, LA-5 |
| `Both_Kinds` partition | RL-22 | LA-10 |
| `Parent_Supports` conjuncts | RL-19, RL-20, RL-21, original `:153-164`, RL-12 | unchanged loop 1 |
| Null arrays and non-default bounds | RL-23, RL-18, the `Data'First = 17` builder | PO-A22 |
| Check status priority | RL-1..RL-7e′ walks; the original 52-action roster | PO-A19 |
| `Pair_Sum_Order` boundary | RL-4a/4b | PO-A17 |
| Column extent and zero columns | RL-15, RL-13 | LA-11, PO-A14 |
| One-sided ghost horizon (F35) | RL-24 | O-GHOST-HORIZON-A (OPEN) |
| `Prefix` integer path (`:216-234`) | original `test_canonical_artifacts.adb:36-64`; IM-7 | PO-B1 |
| `Integer_Matches` guard (`:439-445`) | IM-7, IM-9 | PO-B14 |
| `Base64` guards (`:302-323`) | IM-7 | existing |
| Decimal overflow: first digit, suffix digit, null Work | IM-5, IM-6 (including `"7"` with an empty magnitude) | PO-B8..B10 |
| Mismatch at the top, middle and bottom cells | IM-6 (top, bottom), **IM-11 (middle)**, IM-4 (bottom) | PO-B12 |
| Match: large positive and negative, empty | IM-1..3, IM-8, IM-9 | PO-B11 |
| Radix horizon of D1-B (F34) | IM-1 and IM-5 in the checks build | PO-B22 |
| Exits X0..X7 (§7.1) | X0: W-8a, IM-7. X1: W-4, IM-*. X2: W-1, W-7b. X3: W-2, W-7c. X4/X5: W-3. X6: W-7a, W-7b, W-7c. X7-R: W-8b | P-W1..P-W6; X7-L/X7-A: PO-B19, PO-B20, PO-B1, PO-B3 |
| Export stages, primary and staged, by dependency | W-5 (P1, P2, S1, S2, PS1..PS4, mixed kinds), W-6, IM-10, IM-10P, IM-10S, IM-10PS, W-9 | PO-N5 |
| Python classes, codec, keys, depth, parsers, census | PY-1..PY-14 | O-PY-* |
| Helpers (OD-1) | RL-10 | O-HELPERS |

Finite controls never replace the full proof floor (`HANDOFF.md:161`).

## 13. Packet plan (nothing written)

| Packet | Files (exact) | Gate before writing |
|---|---|---|
| D1-A | `core/resource_run_ledger.adb` only (§5). The spec and `resource_quantities.*` stay byte-identical | GPT-6.1 review of this design; probes P-X3 and P-R1 |
| D1-B | `core/canonical_artifacts.ads` (`Integer_Token`; the `Prefix` Post conjunct) and `core/canonical_artifacts.adb` (context `with Ada.Unchecked_Deallocation; with Resource_Quantities;`; the `Prefix` invariant; the `Binary_At` Post; §6 entities in their DR-C5 forms; `Integer_Matches` in the B.2 shape) | design review, then probes P-W1..P-W8, P-X3 and the `'Old` placement of PO-X1 in the reviewed scratch frame |
| D1-M | `runtime/worldline/proof_manifest.py`: **append** `REQUIRED_PROVED` names, never reorder or remove; `CONTRACT_PINS` only through the official generator; raw pins in `resource-run-ledger-source-controls-v1.json`; `proof-manifest.json` untouched (historical) | after D1-A and D1-B source review |
| D1-C | new files only: Ada programs for RL-10..RL-24 (including RL-12V, RL-12I, RL-12IN, RL-12S, RL-12M) and IM-1..IM-11; `tests/test_resource_run_ledger_bigint_v4.py` (RL-1..RL-7e′); `tests/test_canonical_integer_bigint_v4.py` (IM-10, IM-10P, IM-10S, IM-10PS); W controls in a scratch harness; additive enrollment with the original roster unchanged | after D1-A and D1-B |
| OD-1 | option-specific | operator decision |
| OD-2 | the E1 class table (§11.3) or the E2 site, codec, E2-T and audit set (§11.4, Appendix A), plus PY controls | operator decision |

Each packet goes through, in order:

1. scratch engineering in the reviewed frame;
2. an actual GPT-6.1 source review by a different author;
3. the exact strict command with floor 251 and the full ordered roster;
4. the original 52-action ordinary roster plus the additive controls, in both builds;
5. native and fault campaigns under the existing admission and operator gates.

This document authorizes and runs none of these steps.

## 14. OPEN list

| Id | Item |
|---|---|
| O-A | Full Algorithm A equivalence (PO-A0..A26) on the original signed and invalid domain, every target |
| O-CHECK | Capacity-branch equivalence and unchanged status priority (PO-A17, PO-A19) |
| O-BOUNDS | Installed 128-bit acceptance; every RTE and termination obligation |
| O-B | Lockstep correspondence, overflow theorem, frames, sizing, DR-C5 forms and radix horizon (PO-B1..B23) |
| O-PREFIX-PROOF | D-B-PREFIX proof and checked cost; or PFX-2/3/5 with their probes |
| O-LEGALITY-PROBE | P-W1..P-W8, P-X3, P-R1, P-PFX* and the `'Old` placement (PO-X1) on GNATprove 16.1.0 |
| O-EXCEPTION-CLEANUP | Reclamation on X2..X7 under native fault injection (P-W6; W-1..W-3, W-7, W-8) |
| O-WORKSPACE | Heap (CL-1) or frame (CL-2) fit for every originally successful input; resource failures never accepted |
| O-NOTICE-R1 | A-GHOST-1's `Side_Sum` notices join R-1; otherwise A-GHOST-0 |
| O-HELPERS | OD-1 |
| O-GHOST (D2) | Checked contracts, Ghost code and invariants, original and D1-added: representation limit, recursion, saved values, heap, stack, time (§9.3, §9.6) |
| **O-GHOST-HORIZON-A** (new) | F35: D1-A's one-sided ghost sums exceed the original's checked horizon on direct-Ada signed inputs (RL-24, PO-A26). No candidate selected |
| O-BUILD-SELECTION | Actual assertion scenario and runtime/library identity loaded |
| O-PYTHON / O-PY-AUDIT / O-PY-COST | OD-2; audit of Appendix A.8; conversion costs without caps |
| **O-PY-T** (new) | E2-T disposition for `tomllib`, `argparse`, `ast.literal_eval`, source compilation and `decimal` (§11.4.5) |
| **O-PY-DEPTH** (new) | E2-a depth evidence, or acceptance of E2-b's failure-to-success difference, or R-OVR (S-9, PY-11) |
| **O-CENSUS** (new) | The static census limits (Appendix A.2); PY-13 on the exact identity |
| **O-ORIGINAL-F32** (new; lead) | The original unexecuted control at `tests/test_finalization_kernel.py:257-266` expects AUTHORIZED for a request that `Worldline.Collapse.Decide` answers `Identity_Absent`. Run it; if confirmed, a separate reviewed change outside D1 |
| O-TRANSPORT-MAPPING | Stage-aware classification of export failures, primary and staged (§9.4, §9.5) |
| O-COST-MEASURE | Native time, heap and stack measurements on exact identities; the §9.3 counts are static |
| O-PROOF | Complete strict matching-source proof with floor 251, the sole boundary and the ordered roster; zero unproved, justified or assumed; every strict warning resolved |
| O-NATIVE | Compiled call closure, `-gnatG` and assembly evidence, loaded identity, and the observed checked failure points (PO-N1..N8) |
| O-CONTROLS | Every original and additive control in both builds under existing admission; all unrun |
| O-PINS | Official pin regeneration; append-only roster |
| O-JACKAL-SYMBOLIC | Universal facts are SPARK obligations; JACKAL supplied exact instances and polynomial identities only |
| O-FINAL | Independent source, proof, native and integrated Phase One acceptance; none granted here |

## 15. JACKAL evidence (verbatim `parsed=` and `exact=`)

Every derived number in this package came from `mcp__jackal__jackal_exact` or `mcp__jackal__jackal_poly_eq`, called in
this drafting session. The full records, including witnesses and per-call provenance, are in `jackal.json` (sha256 in
§2): 232 calls, 209 `jackal_exact` and 23 `jackal_poly_eq`.

- `jackal_exact`: `status=exact`, `formal=false`, `lane=rat`, assurance "exact rational arithmetic (not yet
  checker-covered)".
- `jackal_poly_eq`: `status=exact`, `equal=true`, `formal=false`, `lane=poly-eq`, assurance "decidable polynomial
  identity over Q[x]", with a `jackal-exact-cert-v1` certificate.
- Both report evaluator_sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`.
- `exact` here is exact rational arithmetic outside the Lean certificate chain; it is not `formal-bounded`.
- No `consequence_ceiling` field was returned, so every result is treated as informational about code. No refusal
  occurred. The JSONL ledger is recall, not evidence, and is not cited.
- K-01..K-78 are v3's identifiers, re-evaluated with identical results, except K-53, K-71 and K-76, which were not
  re-evaluated: K-53 was historical, K-71 is withdrawn by V3-F7 (replaced by K-102), and K-76 was not relied on.
  K-145 and K-182 were computed and are not relied on.

Verbatim non_claims returned with every result:

- "NOT formal-bounded: this lane carries no Lean-checked certificate"
- "The epistemic class above is the STRONGEST claim this result supports"
- "exact rational arithmetic (not yet checker-covered)" (`jackal_exact`), or "decidable polynomial identity over
  Q[x]" (`jackal_poly_eq`)

| Id | parsed= | exact= | Use |
|---|---|---|---|
| K-01 | `32*(200+1)` | `6432` | bits in 201 limbs (F1) |
| K-02 | `32*(200+1)/8` | `804` | bytes in 201 limbs (F1) |
| K-03 | `8*803+1-32*200` | `25` | 6425 bits exceed 200 limbs |
| K-04 | `32*201-(8*803+1)` | `7` | 6425 bits fit 201 limbs (256^803 representable) |
| K-05 | `8*804+1-32*201` | `1` | 6433 bits exceed 201 limbs (256^804 not representable) |
| K-06 | `32*202-(8*804+1)` | `31` | 6433 bits fit 202 limbs |
| K-07 | `2^6432-10^1936` | positive integer; leading digits 67854160659933622185; trailing digits 7041591296 | 10^1936 < 2^6432 |
| K-08 | `10^1937-2^6432` | positive integer; leading digits 83214583934006637781; trailing digits 2958408704 | 2^6432 < 10^1937 |
| K-09 | `1936+1` | `1937` | digits of 2^6432 |
| K-10 | `1937+1` | `1938` | first all-failing digit count |
| K-11 | `2^63-1` | `9223372036854775807` | Byte_Count'Last; build_guard st_size bound |
| K-12 | `256*(2^63-1+1)-2^71` | `0` | column bound equals 2^71 |
| K-13 | `2^127-1-2^71` | `170141183460469229370504062281061498879` | 128-bit margin |
| K-14 | `2^71-(2^63-1)` | `2351959869397967831041` | 64 bits insufficient |
| K-15 | `10*255+9-(9*256+255)` | `0` | Multiply_Add carry <= 9 |
| K-16 | `10*255+9` | `2559` | Multiply_Add column maximum |
| K-17 | `3*255+2-(2*256+255)` | `0` | Pair_Sum_Order carry <= 2 |
| K-18 | `2^63-3-(4*(2^61-1)+1)` | `0` | floor((2^63-3)/4) = 2^61-1 |
| K-19 | `3*(2^61-1)` | `6917529027641081853` | maximum B.Length |
| K-20 | `2^63-1-3*(2^61-1)` | `2305843009213693954` | allocation-size headroom |
| K-21 | `10+0-20` | `-10` | RL-1 capacity |
| K-22 | `10-10` | `0` | RL-1 Conserved |
| K-23 | `0+0-10` | `-10` | RL-1 Contained |
| K-24 | `1-(0+1)` | `0` | RL-1 epoch successor |
| K-25 | `5-3` | `2` | RL-12 reference |
| K-26 | `0-3` | `-3` | RL-12 v1; RL-12V usage-vs-amount and target c |
| K-27 | `0-0` | `0` | RL-12 child target; RL-12V zero-amount row; RL-12I targets |
| K-28 | `0-(0-1)` | `1` | RL-11; RL-12N reference; RL-12IN target p |
| K-29 | `0-3-(0-1)` | `-2` | RL-12N v1 parent |
| K-30 | `0-3-(0-3)` | `0` | RL-12N v1 duplicate child |
| K-31 | `0-(0-5)` | `5` | RL-14 child target fails |
| K-32 | `0-5-(0-5)` | `0` | RL-14 parent; RL-14P |
| K-33 | `2^6432-1+1-2^6432` | `0` | RL-4a |
| K-34 | `2^6432-1+2-2^6432` | `1` | RL-4b |
| K-35 | `3*(2^6432-1)-(3*2^6432-3)` | `0` | RL-6 |
| K-36 | `255+1-255` | `1` | RL-5a |
| K-37 | `255+1-256` | `0` | RL-5b |
| K-38 | `256-256^1` | `0` | IM-6 suffix overflow at n = 1 |
| K-39 | `255+255*256-65535` | `0` | IM-6 65535 match |
| K-40 | `0+0*256+1*256^2-65536` | `0` | IM-6 65536 match |
| K-41 | `122+2` | `124` | runtime/ JSON operations incl. the two inline-child sites (counts observed) |
| K-42 | `124+22+11+2+3+30` | `192` | direct-name JSON calls in the v3 universe (counts observed); reproduced by the v4 census |
| K-43 | `4300+1` | `4301` | first digit count beyond the default limit |
| K-44 | `4000-640` | `3360` | a 4000-digit chunk exceeds the minimum admitted limit |
| K-45 | `6*640+461-4301` | `0` | 4301 digits in chunks of at most 640 |
| K-46 | `65536-256^2` | `0` | IM-6 suffix overflow at n = 2 |
| K-47 | `22+11+2+3+30` | `68` | direct-name JSON calls outside runtime/ in the v3 universe |
| K-48 | `10*(256-1)+9-(256*10-1)` | `0` | instance 10(P-1)+9 = 10P-1 at P = 256 |
| K-49 | `63*4+(63-15)/16` | `255` | Binary_At case 0 maximum |
| K-50 | `15*16+(63-3)/4` | `255` | Binary_At case 1 maximum |
| K-51 | `3*64+63` | `255` | Binary_At case 2 maximum; IM-11 cell 2 decode |
| K-52 | `2^63+255*2^63-256*2^63` | `0` | column bound attained at the ceiling |
| K-54 | `256*2^63-2^71` | `0` | 2^71 bound |
| K-55 | `5+2+2+1` | `10` | PROD-PROTECTED operations (counts observed) |
| K-56 | `6+9+1+5+2+2` | `25` | ORIGINAL-CONTROL operations (counts observed) |
| K-57 | `122+2+10+25+3+30` | `192` | v3 direct-name scope partition; superseded by K-81 with the alias |
| K-58 | `255+255-(1*256+254)` | `0` | RL-17a and RL-18 column split |
| K-59 | `255+255-255` | `255` | RL-17a |
| K-60 | `255+255-255-255-0` | `0` | RL-18 |
| K-61 | `3+3-5` | `1` | RL-22 |
| K-62 | `256-300` | `-44` | RL-5b capacity |
| K-63 | `0+1*256-256` | `0` | IM-6 256 vs [00,01] |
| K-64 | `257-(0+1*256)` | `1` | IM-6 257 vs [00,01] |
| K-65 | `256^804-2^6432` | `0` | 256^804 = 2^6432 |
| K-66 | `2^6432-(2^6432-1)` | `1` | IM-5 |
| K-67 | `255+0-300` | `-45` | RL-5a capacity |
| K-68 | `2*(2^6432-1)-(2^6432-1)-(2^6432-1)` | `0` | RL-6 before |
| K-69 | `7-5` | `2` | RL-7a usage over amount; RL-7c' and RL-7d' held/charged total minus selected sum |
| K-70 | `7+3-10` | `0` | RL-7a proposed |
| K-72 | `1-2` | `-1` | RL-17b |
| K-73 | `3+5-20` | `-12` | RL-7c capacity |
| K-74 | `5000+1-4300` | `701` | IM-4 digits beyond the default limit |
| K-75 | `10^5000+1-10^5000` | `1` | IM-4 mismatch |
| K-77 | `65535-(254+255*256)` | `1` | IM-6 bottom-cell mismatch |
| K-78 | `65535-(255+254*256)` | `256` | IM-6 top-cell mismatch |
| K-79 | `192+1` | `193` | v3-universe JSON operations: 192 direct + 1 alias (V3-F2) |
| K-80 | `30+1` | `31` | INSTALL-RELEASE-SCRIPT operations incl. the alias |
| K-81 | `122+2+10+25+3+31` | `193` | v3-universe scope partition with the alias |
| K-82 | `68+1` | `69` | v3-universe operations outside runtime/ incl. the alias |
| K-83 | `121+2+1+1+4+2+5+14` | `150` | files in the v3 universe (per-directory counts observed) |
| K-84 | `150+2+2+146` | `300` | all Python files in C5 (v3 universe, root, protected-lab, tests) |
| K-85 | `250+1+3` | `254` | tests/ JSON operations: direct calls, encoder instantiation, instance method calls |
| K-86 | `122+2+10+3+31+2` | `170` | routed scopes (production, inline child, protected, build tool, scripts, root tools) |
| K-87 | `25+254` | `279` | original-control operations (protected controls and tests), unchanged |
| K-88 | `170+279` | `449` | all JSON operations in the 300-file universe |
| K-89 | `193+2+254` | `449` | cross-check of the total by directory group |
| K-90 | `2+2+7` | `11` | stdlib text-parser decimal sites: tomllib 2, ast.literal_eval 2, argparse type=int 7 |
| K-91 | `299+1` | `300` | C4/C5 Python identity: 299 identical + 1 differing (V3-F3) |
| K-92 | `125+1` | `126` | files with JSON operations: 125 identical + proof_manifest.py |
| K-93 | `1029-1023` | `6` | proof_manifest.py lines appended by C5 (V3-F3) |
| K-94 | `10^19-(2^63-1)` | `776627963145224193` | 2^63-1 < 10^19 (build_guard st_size bound) |
| K-95 | `2^63-1-10^18` | `8223372036854775807` | 2^63-1 has exactly 19 digits |
| K-96 | `640-19` | `621` | digit margin of the build_guard bound under the minimum limit |
| K-97 | `7*640+520-5000` | `0` | PY-5: a 5000-digit id splits into seven 640-digit chunks and one 520-digit chunk |
| K-98 | `640+1` | `641` | first digit count above the minimum admitted limit (PY-2, PY-10) |
| K-99 | `10-2` | `8` | PY-8: integer keys sort numerically (2 before 10) |
| K-100 | `50-49` | `1` | PY-8: code point of '2' exceeds '1', so text order puts "10" first (the withdrawn E2-b order) |
| K-101 | `-1-(0-10)` | `9` | PY-8: -10 sorts before -1 numerically |
| K-102 | `8-(7+3)` | `-2` | RL-7b corrected: proposed held 8 minus selected sum 7+3 (V3-F7) |
| K-103 | `5-5` | `0` | RL-7d selector (usage equals amount); RL-7c/7d/7e before totals |
| K-104 | `3-3` | `0` | RL-7c proposed held |
| K-105 | `2-(1+1)` | `0` | RL-7 epoch successor 1 to 2 |
| K-106 | `8-(5+3)` | `0` | RL-7d and RL-7e proposed held |
| K-107 | `8+0-20` | `-12` | RL-7d and RL-7e capacity |
| K-108 | `2-5` | `-3` | RL-7e selector (usage below amount); RL-7e' before mismatch |
| K-109 | `3+0-2` | `1` | RL-12V target p fails |
| K-110 | `0+0-2` | `-2` | RL-12V wrong selector would hold |
| K-111 | `2-(0-1)` | `3` | RL-12S selector (usage 2 over amount -1) and duplicate target |
| K-112 | `2-1` | `1` | RL-12S target R1 fails |
| K-113 | `0-1-1` | `-2` | RL-12S wrong selector target R1 holds |
| K-114 | `0-1-(0-1)` | `0` | RL-12S wrong selector target R2; RL-12M reference target R2 |
| K-115 | `0-5-(0-1)` | `-4` | RL-12M selector (usage -5 not over amount -1); wrong selector target R2 |
| K-116 | `0-1-(0-2)` | `1` | RL-12M reference target R1 fails |
| K-117 | `0-5-(0-2)` | `-3` | RL-12M wrong selector target R1 holds |
| K-118 | `255+255*256+255*256^2` | `16777215` | IM-11 decimal value (cells FF FF FF) |
| K-119 | `255+254*256+255*256^2` | `16776959` | IM-11 tagged magnitude [FF,FE,FF] |
| K-120 | `255+254*256+255*256^2-(255+255*256+255*256^2)` | `-256` | IM-11 middle-cell difference |
| K-121 | `256^3-16777215` | `1` | IM-11 decimal below 256^3: no carry-out at any digit |
| K-122 | `255*2^16+254*2^8+255` | `16776959` | IM-11 base64 24-bit group of bytes FF FE FF |
| K-123 | `63*2^18+63*2^12+59*2^6+63` | `16776959` | IM-11 sextets 63,63,59,63 give the text //7/ |
| K-124 | `52+7` | `59` | base64 index of '7' |
| K-125 | `63*4+3` | `255` | IM-11 Binary_At cell 0 = FF |
| K-126 | `3*16+15` | `63` | 63 = 3*16 + 15 (quotient and remainder used by Binary_At) |
| K-127 | `15*16+14` | `254` | IM-11 Binary_At cell 1 = FE |
| K-128 | `14*4+3` | `59` | 59 = 14*4 + 3 (quotient and remainder used by Binary_At) |
| K-129 | `16777215-10^7` | `6777215` | IM-11 decimal has at least 8 digits |
| K-130 | `10^8-16777215` | `83222785` | IM-11 decimal has at most 8 digits |
| K-131 | `3*268+1` | `805` | IM-10: 805 magnitude bytes = 268 full base64 groups + 1 byte (== padding) |
| K-132 | `7*2^16-(1*2^18+48*2^12)` | `0` | IM-10 first quartet BwAA (bytes 07 00 00) |
| K-133 | `26+22` | `48` | base64 index of 'w' |
| K-134 | `6*2^16-(1*2^18+32*2^12)` | `0` | IM-10 mismatch edit BgAA (bytes 06 00 00) |
| K-135 | `26+6` | `32` | base64 index of 'g' |
| K-136 | `2^6432+7-(2^6432+6)` | `1` | IM-10 mismatch differs only in the bottom cell |
| K-137 | `5000-1937` | `3063` | IM-4: 10^5000 exceeds 10^1937 > 2^6432, so its magnitude has at least 805 bytes |
| K-138 | `2+2` | `4` | maximum Decide calls per Primary_And_Staged mixed request (V3-F5) |
| K-139 | `4*(2+2)` | `16` | checks build: Integer_Matches evaluations per mixed request, one integer node per bundle, every Seal observed |
| K-140 | `1*2+1*2` | `4` | release build: Integer_Matches evaluations per mixed request, one node per bundle |
| K-141 | `4*(1-1)+1` | `1` | checks-build Work-allocation ordinal of Decide 1 |
| K-142 | `4*(2-1)+1` | `5` | checks-build Work-allocation ordinal of Decide 2 |
| K-143 | `4*(3-1)+1` | `9` | checks-build Work-allocation ordinal of Decide 3 |
| K-144 | `4*(4-1)+1` | `13` | checks-build Work-allocation ordinal of Decide 4 |
| K-145 | `3*(2+2)` | `12` | computed, not relied on: an unobserved Seal evaluates three bindings but makes Read_Ready or Final_Context_Matches reject, so the mixed request stops at that stage and 12 is not reached (DESIGN.md 9.5) |
| K-146 | `256-10` | `246` | DR-C5: 10*256^(n-1) is below 256^n |
| K-147 | `16+6+8+12` | `42` | Compare fixed PV-term multiplicity (Post 16, padding 6, Is_Negative 8, assertions 12) |
| K-148 | `4+4` | `8` | Compare per-iteration PV-term multiplicity |
| K-149 | `10^1937-(2^6432+7)` | positive integer; leading digits 83214583934006637781; trailing digits 2958408697 | IM-10 decimal 2^6432+7 has 1937 digits (with K-07) |
| K-150 | `10^1936-2^6424` | positive integer; leading digits 99344319684922134288; trailing digits 3488118784 | IM-1: 10^1936 >= 256^803, so its magnitude has exactly 804 bytes (with K-07) |
| K-151 | `2^6440-10^1937` | positive integer; leading digits 41970665128943007279; trailing digits 2647371776 | IM-2/IM-3: 10^1937 < 256^805, so magnitudes of 2^6432 .. 10^1937 have 805 bytes |
| K-152 | `2^6432-1-2^6424` | positive integer; leading digits 16719848034485575647; trailing digits 0529710079 | IM-5: 2^6432-1 >= 256^803, so its magnitude has exactly 804 bytes |
| K-153 | `(0^3+9*0^2+14*0+6)/3-(1+1)` | `0` | RP(0) closed form equals w(0)+p(0) |
| K-154 | `0*(0+1)*(0^2+11*0+12)/6` | `0` | PV(0) = 0 |
| K-155 | `(2*0^3+21*0^2+37*0+12)/6-(4*0+2*(0+1)+0+0)` | `0` | MA(0) base case |
| K-156 | `1^3+5*1^2+7*1+1-(4*1+2*0+3*2+3*1+1)` | `0` | PB(1) closed form equals the direct level count |
| K-157 | `(3*2^4+14*2^3+15*2^2-20*2)/12-(1+14)` | `0` | sum of PB(0), PB(1) equals the closed form at 2 |
| K-158 | `(1^4+6*1^3+11*1^2-2*1)/2-(4*1+2*1+2*1+2*0)` | `0` | Compare residual Q(1) equals the direct count |
| K-159 | `803*(803+1)*(803^2+11*803+12)/6` | `70334477708` | PV(803) Power_Reference invocations |
| K-160 | `(8*803+42)*70334477708` | `454782732859928` | Compare PV terms, equal 803-byte operands |
| K-161 | `(803^4+6*803^3+11*803^2-2*803)/2` | `209446213768` | Compare residual reference terms Q(803) |
| K-162 | `4*70334477708` | `281337910832` | one checked Value on a valid 803-byte span |
| K-163 | `4*(1^2+11*1+12)/3` | `32` | A-GHOST-0 per-term factor at c = 1 |
| K-164 | `4*(8^2+11*8+12)/3` | `656/3` | A-GHOST-0 per-term factor at c = 8 |
| K-165 | `4*(803^2+11*803+12)/3` | `2614616/3` | A-GHOST-0 per-term factor at c = 803 |
| K-166 | `(803^3+12*803^2+20*803+6)/3` | `175178467` | D(803): decimal-phase PRI per digit, n = 803 |
| K-167 | `(7*803^3+12*803^2+11*803)/6` | `605369655` | C(803): compare-phase PRI, n = 803 |
| K-168 | `(3^3+12*3^2+20*3+6)/3` | `67` | D(3) |
| K-169 | `(7*3^3+12*3^2+11*3)/6` | `55` | C(3) |
| K-170 | `(803^3+6*803^2+5*803)/3` | `173884832` | PVW(803) |
| K-171 | `803*(803+1)/2` | `322806` | r(803) |
| K-172 | `454782732859928+209446213768` | `454992179073696` | Compare total PRI, equal 803-byte operands (RL-1 lower bound) |
| K-173 | `281337910832/322806` | `2614616/3` | consistency: 4PV(803)/r(803) equals the factor K-165 |
| K-174 | `0+1` | `1` | p(0) = 1 |
| K-175 | `(1^3+12*1^2+20*1+6)/3-(1*(1+1)/2+(2*1^3+21*1^2+37*1+12)/6)` | `0` | D(1) = r(1) + MA(1) |
| K-176 | `3+9` | `12` | Compare calls per selected usage row per column from row-sized invariant and lemma loops |
| K-177 | `1+9+3` | `13` | Compare calls per selected usage row per column from executable Operand, LA-1 Post, outer invariant |
| K-178 | `3+3` | `6` | Compare calls per selected usage row from Lemma_Close Pre and LA-7 Post |
| K-179 | `2+2+2+1+3+1` | `11` | Value evaluations in LA-9's Post (upper bound) |
| K-180 | `4*11` | `44` | LA-9 Post PV-term bound 44 PV(L) |
| K-181 | `3*4` | `12` | Amount_Reference worst case 12 PV(L) (three Values) |
| K-182 | `2*(2*12)+12` | `60` | computed, not relied on |
| K-183 | `257*(2^6424-1)-2^6432` | positive integer; leading digits 65568031507786571166; trailing digits 6511880959 | RL-24: one-sided ghost sum of 257 operands 2^6424-1 exceeds 2^6432 |
| K-184 | `2*257` | `514` | RL-24 child-row count |
| K-185 | `256*2^6424-2^6432` | `0` | 256 * 2^6424 = 2^6432 |
| K-186 | `2^6424-1-(2^6424-1)` | `0` | RL-24 alternating partial sums return to 0 |
| K-187 | `0-(0-(2^6424-1))-(2^6424-1)` | `0` | RL-24 one +X/-X pair cancels exactly |
| K-188 | `256^803-2^6424` | `0` | 256^803 = 2^6424 (X = 2^6424-1 has 803 bytes, all FF) |
| K-189 | `255*2^6424-1-(2^6432-1-2^6424)` | `0` | closed form of K-152 |
| K-190 | `6+3+5` | `14` | Python-source compilation sites: ast.parse 6, compile 3, exec 5 |
| K-191 | `2+1` | `3` | (a) Compare evaluations per selected usage row per both-sides Side_Sum or Side_Total evaluation: two sign tests plus one term on the matching side; (b) Finish_Binary Post: two Value'Old * P(Upto) products plus one P(Upto) bound |
| K-192 | `3*3` | `9` | Compare evaluations per selected usage row in LA-1's Post or in one LA-1 loop iteration (three both-sides Side_Sum kinds) |
| K-193 | `1+1+2` | `4` | Compare evaluations per selected usage row in LA-9's Post (Usage_Selected conjunct, Counted conjunct, two Operand in the Signed_Prefix_Value conjunct) |
| K-194 | `6+4` | `10` | once-per-call Compare coefficient on u: Lemma_Close Pre and LA-7 Post 6 (K-178) plus LA-9 4 (K-193) |
| K-195 | `(12*1+13)*1*803` | `20075` | instance N = u = 1, K = 803: per-column Compare evaluations over all columns |
| K-196 | `3*1*1+10*1` | `13` | instance N = u = 1: once-per-call Compare evaluations |
| K-197 | `20075+13` | `20088` | instance: all Compare evaluations per Selected_Sum_Order call |
| K-198 | `20088*454992179073696` | `9139882893232405248` | instance: Compare-term PRI with every Compare on equal nonnegative 803-byte spans (K-172 each) |
| K-199 | `1+1` | `2` | the 2 in N + 2 (outer invariant 1 plus LA-1 Post 1; Lemma_Close Pre 1 plus LA-7 Post 1), the target's 2 prefix terms per column, and the 2 in K - L + 2 (invariant evaluations K - L + 1 plus the Post) of the padding facts |
| K-200 | `2+2+1` | `5` | Amount_Reference coefficient on n_s (Selected_Sum_Order Post 2, Lemma_Close Post 2, LA-7 Post 1); target Value evaluations (the two Posts 2 + 2, LA-8 1) |
| K-201 | `1+2` | `3` | Amount_Reference coefficient on N * n_s (LA-7 loop 1, LA-10 2) |
| K-202 | `2*4` | `8` | LA-9L Post PV terms (two Value, 4 PV each) |
| K-203 | `805-1` | `804` | n >= 805: Work_Value evaluates Power_Reference (n - 1) with n - 1 >= 804 |
| K-204 | `804-1` | `803` | n = 804: Work_Value forms at most P(803); RL-2's failing iteration Completed = Count - 1 = 803 |
| K-205 | `3*2` | `6` | Pair_Sum_Order Post Value evaluations (three operands, two conditions) |
| K-206 | `6*4` | `24` | Pair_Sum_Order Post PV terms |
| K-207 | `803-1` | `802` | RL-24: Offset of the failing LA-1 evaluation (Offset + 1 = 803) |
| K-208 | `2*257-1` | `513` | RL-24: row position of the 257th positive child |
| K-209 | `256*(2^6424-1)-(2^6432-256)` | `0` | RL-24: 256 operands X sum to 2^6432 - 256, which is representable |
| K-210 | `8+3+4+6` | `21` | Compare PV coefficient per operand outside the loop (Post 8, padding base 3, Is_Negative 4, assertions 6) |
| K-211 | `2+4` | `6` | radix-power evaluations at P(Offset) per column outside LA-1's loop (LA-1 Post 2, LA-3 actuals and Low updates 4) |
| K-212 | `2+2` | `4` | radix-power evaluations at P(Offset + 1) per column in the outer invariants (Low bound 2, Carry product 2); also Lemma_Close Pre at P(K) |
| PE-01 | `(x+1)-((x-1)+1)` = `1` | equal=true | p(e) = e+1 step |
| PE-02 | `x*(x+1)/2 - (x-1)*x/2` = `x` | equal=true | r(c) = c(c+1)/2 step (r(c) - r(c-1) = p(c-1)) |
| PE-03 | `x*(x+1)/2 + x*(x-1)/2 + 2*x + (x+1)` = `x^2+3*x+1` | equal=true | Radix_Power_Worker count w(e) |
| PE-04 | `(x^3+9*x^2+14*x+6)/3 - ((x-1)^3+9*(x-1)^2+14*(x-1)+6)/3` = `x^2+5*x+2` | equal=true | RP(e) closed form step |
| PE-05 | `x^2+3*x+1 + (x+1) + x` = `x^2+5*x+2` | equal=true | RP increment w(e)+p(e)+p(e-1) |
| PE-06 | `x*(x+1)*(x+2)/6 - (x-1)*x*(x+1)/6` = `(x-1)*x/2 + x` | equal=true | S(c) = sum over k<c of r(k)+p(k): closed form step |
| PE-07 | `(x-1)*x/2 + x` = `x*(x+1)/2` | equal=true | r(c-1)+p(c-1) = r(c), so S(c) = T(c) |
| PE-08 | `x*(x+1)*(x+2)/6 + (x-1)*x*(x+1)/6 + (x-1)*x + 2*x + x*(x+1)/2` = `(x^3+6*x^2+5*x)/3` | equal=true | Prefix_Value_Worker count PVW(c) |
| PE-09 | `x*(x+1)*(x^2+11*x+12)/6 - (x-1)*x*((x-1)^2+11*(x-1)+12)/6` = `(x^3+6*x^2+5*x)/3 + ((x-1)^3+9*(x-1)^2+14*(x-1)+6)/3 + x*(x+1)/2 + (x-1)*x/2 + x` | equal=true | public Prefix_Value PV(c) closed form step (self-referential Post) |
| PE-10 | `4*x*(x+1)*(x^2+11*x+12)/6` = `(x*(x+1)/2)*(4*(x^2+11*x+12)/3)` | equal=true | A-GHOST-0 per-term factor: 4PV(c) = r(c) * (4/3)(c^2+11c+12) |
| PE-11 | `x*(x+3)/2 - (x-1)*(x+2)/2` = `x+1` | equal=true | sum of p(k), k = 1..n, = n(n+3)/2 step |
| PE-12 | `4*x*(x+1)/2 + 2*(x+1) + 2*x*(x+1)*(x+2)/6 + x*(x+3)/2` = `(2*x^3+21*x^2+37*x+12)/6` | equal=true | Multiply_Add per-call count MA(n) |
| PE-13 | `x*(x+1)/2 + (2*x^3+21*x^2+37*x+12)/6` = `(x^3+12*x^2+20*x+6)/3` | equal=true | decimal-phase per-digit count D(n) = r(n) + MA(n) |
| PE-14 | `2*x*(x*(x+1)/2) + x*(x+1)*(x+2)/6 + x*(x+3)/2` = `(7*x^3+12*x^2+11*x)/6` | equal=true | compare-phase count C(n) |
| PE-15 | `4*x*(x+1)/2 + 2*(x-1)*x/2 + 3*(x+1) + 3*x` = `3*x^2+7*x+3` | equal=true | Prefix_Bounds per-level count |
| PE-16 | `(x^3+5*x^2+7*x+1) - ((x-1)^3+5*(x-1)^2+7*(x-1)+1)` = `3*x^2+7*x+3` | equal=true | PB(o) = o^3+5o^2+7o+1 step |
| PE-17 | `(3*x^4+14*x^3+15*x^2-20*x)/12 - (3*(x-1)^4+14*(x-1)^3+15*(x-1)^2-20*(x-1))/12` = `(x-1)^3+5*(x-1)^2+7*(x-1)+1` | equal=true | sum of PB(o), o < L, closed form step |
| PE-18 | `4*x*(x+1)/2 + 2*(x*(x+1)*(x+2)/6 + (x-1)*x*(x+1)/6) + 2*(3*x^4+14*x^3+15*x^2-20*x)/12` = `(x^4+6*x^3+11*x^2-2*x)/2` | equal=true | Compare residual reference count Q(L), equal-length operands |
| PE-19 | `(2*(x-x)+21+4*x) + (21+4*x)` = `42+8*x` | equal=true | general padded Compare PV formula specialises to (8L+42) at equal lengths |
| PE-20 | `(x-1)*1+1` = `x` | equal=true | release-build Work-allocation ordinal of Decide k with one node per bundle equals k |
| PE-21 | `x*(x+1)*(x+2)/6 - (x-1)*x*(x+1)/6` = `x*(x+1)/2` | equal=true | T(c) = c(c+1)(c+2)/6 step (T(c) - T(c-1) = r(c)) |
| PE-22 | `x*(x+1)*(x+2)/6 + (x-1)*x*(x+1)/6` = `x*(x+1)*(2*x+1)/6` | equal=true | T(K)+T(K-1) = K(K+1)(2K+1)/6 (Compare residual; Selected_Sum_Order Prefix-term total) |
| PE-23 | `3*x*(x+1)/2 + 3*(x+1)` = `3*(x+1)*(x+2)/2` | equal=true | Finish_Binary PRI: 3 r(Upto) + 3 p(Upto) = 3 r(Upto + 1) |

Universal statements about all n, all rows and all carries are SPARK proof obligations (§8). Each recurrence above is
lead reading of the source; JACKAL establishes only that the stated polynomial identities and instances hold, not that
GNAT executes those recurrences. Counts read from files or scans are observations; only their arithmetic went to
JACKAL.

## 16. Non-claims

- No source, proof, native, test, review or Phase One acceptance is claimed. `proof_acceptance`, `source_acceptance`,
  `phase_acceptance` and `native_acceptance` are false.
- No compiler, prover, build, test, WORLDLINE code, systemctl, project-vault or restic command was run. No WORLDLINE
  module was imported.
- Installed binary strings, examples and guide text are not legality evidence for this candidate. Every legality
  question is a named probe.
- The Python observations are of this agent's interpreter and installed files only.
- The cost counts of §9 are static source counts, not measurements and not proved bounds. No time was measured.
- The checked failure points of §9.6 are read from source; they are to be observed (PO-N8), not presupposed.
- No operator option is selected or recommended. Operator approval would not be acceptance evidence.
- Resource failures of any kind (heap, stack, time) are never accepted refusals. They remain OPEN native obligations.
- F35 is a D1-introduced checked-build hazard that this design does not repair; it stays OPEN.

_End of DESIGN v4._
