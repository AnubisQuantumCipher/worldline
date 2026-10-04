# D1: release-path native Big_Integer repair — DESIGN v3

Author: Claude Code lead claude-opus-5-5 (drafting subagent), 2026-10-04.

Status: **DRAFT v3 for independent actual GPT-6.1 (`gpt-6.1-sol`) review.**

- Nothing in this package was compiled, proved, built, tested, run, reviewed or accepted.
- Every Phase One obligation stays OPEN. `proof_acceptance=false`, `source_acceptance=false`, `phase_acceptance=false`.
- No source tree, composition, review, packet or evidence file was modified. No SIA note was written.
- The package is three create-only files in
  `W/work/claude-lead-isolation-v1/wt-1/designs/claude-native-bigint-d1-design-v3/`:
  - this `DESIGN.md`;
  - `decisions.json`;
  - `APPENDIX-A-python-conversion-surface.md` (sha256
    `a8ba784ac4ff3d0797fb3c7b0b2cd67981ca0fa6a0649215b88890c8d71db70a`, 30912 bytes).
- v1, v2 and their GPT-6.1 reviews remain unchanged history.

This version answers the actual gpt-6.1-sol review of v2 (verdict NOT_ENDORSED): required changes V2-RC1..V2-RC6, the
still-NOT_CLOSED v1 items RC4..RC7, rulings R-A, R-B, R-PREFIX, R-WORKSPACE, R-OD1, R-OD2 and R-SCOPE, and fact
corrections F10-F12 and V2-F13..V2-F18. It keeps the parts ruled eligible in principle (Algorithm A, the Algorithm B
core, D-B-PREFIX and the pool-specific owner), completes them, and decides nothing for the operator.

## 1. Trace table

Status labels:

- **DESIGNED**: lead-owned design text in this document, unproved and unreviewed.
- **PACKAGE**: an operator decision package. No option is selected.
- **CORRECTED**: a v2 statement replaced by a qualified or corrected one.
- **OPEN**: the engineering or acceptance obligation remains.

v2 line numbers refer to `W/work/claude-native-bigint-d1-design-v2/DESIGN.md` (sha256 `f9161233…702cb4`).

| Item | What the review requires (short) | Answered in v3 | v2 text replaced | v3 status |
|---|---|---|---|---|
| **V2-RC1** | Complete B's internal shape contract and proof interface. Exclude a null Work before indexing its sentinel. Keep the public no-Pre domain. Correct the "no fallback" claim | §6.2: shape contract. There is no sentinel cell; a null Work is a legal shape and is never indexed. §6.3: digit interface. §6.4–§6.6: Multiply_Add, Decide_Work, Integer_Matches. §6.7: alternatives replace the claim | v2:851-893 (incl. "there is no fallback", :890-893); v2:959-996; v2:1010-1066; v2:1200-1223 | DESIGNED; O-B and O-PREFIX-PROOF OPEN |
| **V2-RC2** | SPARK-legal Work lifetime and reclamation on every normal and exceptional exit after allocation, with installed-pattern legality, flow, borrow and no-leak evidence | §7: exit inventory; CL-1 owner plus handler with re-raise, gated by probes P-W1..P-W8; lead-owned CL-2 (frame lifetime) and CL-3 (`finally`); operator-only F-B2/F-B3 | v2:904-947; v2:1085-1090 ("No other exit exists"); v2:1103-1140 | DESIGNED; O-LEGALITY-PROBE, O-EXCEPTION-CLEANUP, O-WORKSPACE OPEN |
| **V2-RC3** | Repair OD-1: (o) release-only while checked Posts stay open; (i-a) model binding and direct Ada users; (ii) layout, base/index/length, automatic vectors, full costs; (iii) retirement incompatible | §10 | v2:1337-1356, including the "(ii) only option" recommendation (withdrawn) | PACKAGE; O-HELPERS OPEN |
| **V2-RC4** | OD-2: E1 exact startup/import/child/exec/runpy/service coverage; E2 chunks valid under every admitted limit, complete data flow incl. PR and outside-runtime/non-JSON sites, unchanged canonical semantics; no cap as a cost repair | §11 and Appendix A | v2:1358-1462; v2:1643-1782 (Appendix A) | PACKAGE; O-PYTHON, O-PY-AUDIT, O-PY-COST OPEN |
| **V2-RC5** | Complete reference-evaluated fixtures (RL-1/2/3, RL-12, RL-14) and a source-to-control coverage map | §12 | v2:1464-1520 | DESIGNED (all unrun); O-CONTROLS OPEN |
| **V2-RC6** | Correct D2/native scope and costs; saved Work arrays, nested checked contracts and lemmas; qualify valid-span, padding, build and failure claims; two mixed-export failure stages; synchronized labels; preserve every original checked requirement | §3.2 (V2-F13..F18), §4, §9, this table, `decisions.json` | v2:91-103; 142-151; 172-184; 242-260; 284-301; 1235-1335; 1449-1457 | CORRECTED; O-GHOST, O-NATIVE OPEN |
| RC4 (v1) | Closed guard-inclusive references; complete obligation list | §6.5: the lockstep reference is the original statements; §6.8: v2's closed references kept as an alternative; §8.2 | v2 §6.2 as primary | DESIGNED; O-B OPEN |
| RC5 (v1) | Legal workspace behind the pure Boolean profile | §7 | v2 §6.4, §6.7 | DESIGNED; probes OPEN |
| RC6 (v1) | Helpers and Ghost stay OPEN; operator route package | §4.2, §10 | v2 §4.2, §9 | PACKAGE |
| RC7 (v1) | Python route or OPEN; extended controls | §11, §12 | v2 §10, §11 | PACKAGE; DESIGNED controls |
| R-A | Eligible in principle; supply omitted helper definitions, lemma contracts and bodies, legality, closure | §5: every helper defined; every lemma has a contract and proof sketch; installed-tool shape rules; one new recursive ghost function, disclosed | v2:446-503 abbreviations | DESIGNED; O-A, O-BOUNDS OPEN |
| R-B | Eligible as an inequality theorem, not a size refusal; private shape Pre, ownership and cost | §6, §7, §9.3 | v2 §6 | DESIGNED |
| R-PREFIX | Additive public Post plus `Integer_Token` eligible; the no-fallback claim rejected | §6.3 (primary, unchanged in substance), §6.7 | v2:851-893 | DESIGNED; O-PREFIX-PROOF OPEN |
| R-WORKSPACE | Pool-specific owner preferred, conditional on legality and all-exit reclamation. F-B1 lead-owned. F-B2/F-B3 operator-owned API/ABI | §7; ownership synchronized in §4.4 | v2:904-947, v2:1103-1140 | DESIGNED |
| R-OD1 | No OD-1 choice; corrected option set and evidence | §10 | v2 §9 | PACKAGE |
| R-OD2 | No E1/E2 choice; repaired packages | §11 | v2 §10 | PACKAGE |
| R-SCOPE | D1 cannot alone discharge the original native obligation | §4, §9.2, §14 | v2 §4.2–§4.3, §8.3, §10.4 | CORRECTED |
| F10 | v1 selector wrong on invalid spans; RL-12 is not a whole-result discriminator | §3.1 F10, §5.3, §12.3 (RL-12, RL-12N) | v2:232-240, v2:1496 | CORRECTED |
| F11 | Default build is `checks`; this is not evidence of the deployed scenario | §3.1 F11, §4.3 | v2:242-251 | CORRECTED (scope) |
| F12 | Two mixed-export failure stages; hard faults are unrecoverable | §3.1 F12, §9.4 | v2:253-260 | CORRECTED |
| V2-F13 | Padded failures need valid-span and build qualifiers; Low need not grow | §3.2, §9.2, §9.3 | v2:142-151, 1320-1325, 1342-1349 | CORRECTED |
| V2-F14 | "No other exit after allocation" is false | §3.2, §7.1 | v2:1085-1090 | CORRECTED |
| V2-F15 | (ii) does not make only allocation fail | §3.2, §10 | v2:1351-1355 | CORRECTED |
| V2-F16 | 4000-digit chunks unsafe; PR not host-bounded; E0 overbroad | §3.2, §11 | v2:1426-1428, 1455, 1664-1675 | CORRECTED |
| V2-F17 | RL-1, RL-12 and RL-14 expectations wrong or incomplete | §3.2, §12 | v2:1477-1498 | CORRECTED |
| V2-F18 | No-fallback claim; ownership labels | §3.2, §6.7, §4.4 | v2:91-103, 890-893, 1105-1139, 1348-1356 | CORRECTED |
| F19–F29 (new, lead-found) | Installed-tool, toolchain, Python and source facts that constrain v3 | §3.3 | — | OBSERVED, or [LEAD] where stated |

## 2. Conventions, roots, inputs and skills

Evidence labels:

- **[OBS]** observed: quoted from a file at `file:line`, from a read-only command run in this session, or from the
  installed tool binaries' strings.
- **[JKL K-nn]** a fresh `mcp__jackal__jackal_exact` result from this session. Every one has:
  - `status=exact`, `formal=false`, `lane=rat`;
  - evaluator_sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`;
  - the verbatim non_claims of §15.
  A JACKAL result is never presented as a proof of an Ada property.
- **[LEAD]** lead reasoning: an unverified argument that is itself a proof or evidence obligation. It is never
  acceptance.
- **[DOC]** guide or documentation text: skill chapters, installed examples, the installed GNAT RM. It is not
  installed-tool legality evidence for this candidate.
- Every Ada block is **UNCOMPILED / UNPROVED** design text.

Roots:

| Root | Path |
|---|---|
| `W` | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow` |
| `C5` | `W/work/claude-composition-v5-beta/source`, the current reviewed candidate (QUALIFIED_SOURCE_COMPOSITION; no acceptance) |
| `C4` | `W/work/reviewed-common-proof-source-composition-v4/source`, the base. Bare `core/…`, `runtime/…` paths are `C5` unless marked `C4` |
| `RT` | `/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude` |
| `GP` | `/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1` |
| `GN` | `/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1` |
| `SK` | `/home/sicarii/.claude/skills` |
| `v2` | the v2 DESIGN.md |
| `R2` | `W/work/claude-native-bigint-d1-design-v2/review/gpt61-v1` |

Input identities [OBS `sha256sum` in this session]:

| Input | sha256 |
|---|---|
| v2 `DESIGN.md` / `decisions.json` | `f916123307c5132a1485d7c089af82c60204af8ccb0667494f2457aee1702cb4` / `ee13763c0bbc3c0046c4b58bfb9b59f01e8b42585e6b84508364186de7cad0e4` |
| `R2/REVIEW.md` / `review.json` / `checks.json` | `04dbf7041148e0acd604b806f6ed4dd46a4b20a9e16874ad0f88056b1fa332bc` / `ed3780b6391b35f632b8c344a2c528675a7b2a4396d5d02f01950b434103a66d` / `1f672eba4f3efeea6421cde6772fb66b1e36e989fef933c8bc2c67b5bc04dc38` |
| `HANDOFF.md` / `START-CLAUDE.txt` / `complete-phase1-prompt.txt` | `2f3a0b4b…f588237` / `004c71a8…bf588237`-prefix differs: `004c71a8da3cb4e917812af427a1701bde226a18da615bcdbf483414d75f187e` / `1b228f4b07209c91c8f8770851906a8ebbf90db12f0af605954aff392946b327` |
| v5-beta review `REVIEW.md` / `source-inventory.json` | `a5cc89bbe21c80796f74a236f0c053da7ca94ec82efbf4a9924f8e489b798ebe` / `3407119bdf9e8497ed8259d76ea783f6d207f15fd155ee9c45534c3b0eaf937a` |
| `C5/core/resource_run_ledger.ads` / `.adb` (equal to C4) | `9a761421…6c02` / `8e7c02c5…be42` |
| `C5/core/resource_quantities.ads` / `.adb` (packet 05 parenthesization) | `7bb5ebf110cfb6caec3c204e97be8bc4d7a93ebdb3b9e6251f48a456eeae1a28` / `5e87d8a0e874a0f2010070e31140ee1eb638ff866beea6f85da1f41599863b9b` |
| `C5/core/canonical_artifacts.ads` (equal to C4) / `.adb` (packets 05, 07) | `bb62783a…7fee` / `979466c0c24fadb5ae5f4aac29a08cff680d367c4356ec69faa0596c7c5f2aa3` |
| `C5/core/evaluation_pending.ads` | `8750cacbebb849baba47f8319e179cab78dfefac7bee10760f96fa2e0dcf861e` |
| `C5/core/evaluation_finalization.ads` / `.adb` | `e20808c44b84e02485e10a3eb1e1e36a2f2f88defd75eb97c536cee6851c287a` / `c64f17246f0dfa3d88299a534e3e716ada35fd05120983a3d8f53a7c28d1a738` |
| `C5/core/evaluation_finalization_c.adb` (equal to C4) | `bdcf333878aebe4aca55333bc3b9a9a50007c187fc4b380dec1adb18127f83d3` |
| `C5/core/resource_run_ledger_c_api.adb` | `fbc97b4c17ee0a0a17e74bae669fa11e674bb234ce5cd8f73d374b7d7e114581` |
| `C5/core/worldline_core_sources.gpr` / `worldline_core.gpr` | `701931bc…dff3c` / `5497fabb698d53efc2bfb39104bdcd48b1c0f46e0c706c2643c8ce1af72fd5b0` |
| `C5/core/spark-big_integers.ads` / `worldline-resources.ads` | `fe80da029611497ba25aca43d5599a220f2be41f33010f6b04d42febc2bfec52` / `571e729f77c605d6589b18f753e635da2a324d6363860d08285551357c51b587` |
| `C5/runtime/worldline/canonical.py` / `trusted.py` / `daemon.py` / `client.py` / `cli_main.py` | `d80f79bc…52af` / `0e95e086…0890` / `2b302f89b6147d4aa72111e7f7f28e56cf517804e1db765f805381d681a12f92` / `a1fcdc67bdf484e0fa976d8d3e2b2200fe7fd6544c68d973c3671933a28255a4` / `adc4d1dd857c0da0ac20eaf3affeccc600eb3acbd72c313157dbe3f457d4aff5` |
| `C5/runtime/worldline/resource_run_ledger.py` / `simulation.py` / `linux/private_evaluator.py` | `14175c7da56f0c6b3425157e68bda7e19d9451cddac6dc9fc45ec3927a1588a9` / `aa5391fe990cfca43a79a2927548eb5518e6b9ece41bd3f116185727035b06fe` / `667d2dc6f9c06fea758d2b924fa067d3b45e366c6ef7cf286c41efb5024db2fc` |
| `C5/tests/test_resource_run_ledger_v1.py` / `tests/test_finalization_kernel.py` / `artifact-tests/test_canonical_artifacts.adb` | `eff3894460e2407afaeecaef78433f660b4c80a11c621f5a7ef67ac452ac0f63` / `76141dfb2ddea1c9fb62e5ea09d27830432e96273f85e984da94f5ebbafb4a62` / `2a8d127846ae5981d6021df9dc92a80c30a88b5e86b1040404a484dbe5df5fa1` |
| `RT/s-shabig.ads` / `s-genbig.adb` / `a-nbnbin.ads` / `a-nbnbin.adb` | `344bcca7…9069` / `89824130…4991` / `be5a0604…607a` / `64872fd0…2d73` |
| `GP/libexec/spark/bin/gnat2why` (equals the tool pin in the R-1 evidence file) | `375d0100954a66c78bace00d2229c9b96a30b6cf28845e00c4db220ba1efddb5` |
| `GN/share/info/gnat_rm.info` | `246bc8ac93f9e25c37e7835c8ff45e6e74e9ab564e3809cdf60dd11b48d8df64` |
| `W/work/claude-operator-decision-package-v1/evidence-recursive-notices.json` | `6b6ec3fb99ccfcd40aef8f99f3b7d82435e00e26255019eb9833c74eff9cd2b3` |

The `START-CLAUDE.txt` cell should read simply `004c71a8da3cb4e917812af427a1701bde226a18da615bcdbf483414d75f187e`.
The full `HANDOFF.md` hash is `2f3a0b4b3bb2a0996824859c2d9f8a59e7c58f624b2d81cb00e40e76bf588237`. These are raw file
hashes. The pins in `runtime/worldline/proof_manifest.py` are normalized hashes from the official generator and differ
by design.

Skills: the `ada` hub, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`,
`ada-high-integrity` and `ada-2005-amendment` were loaded with the Skill tool. Chapters read:

- `SK/spark-users-guide`: ch05 (language restrictions, controlled types excluded), ch06 (Exceptional_Cases,
  Refined_Post), ch13 (ownership), ch17 and ch27 (`--proof-warnings`), ch33 (limitations: recursive contracts),
  ch36 (proof warnings as a smoke detector).
- `SK/ada-omarchy` (proof gate); `SK/gnat-toolchain` (gnatmem leak audit).
- `SK/advanced-ada` ch13 (exceptions, error ladder) and ch16 (access types, pool-specific deallocation).

The SPARK User's Guide skill is release **28.0w**, a development release. It is guidance, not legality evidence for the
installed GNATprove FSF 16.1.0. No compiler, prover, build, test or WORLDLINE code was run.

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

**Lead constraints for this design:**

- No domain cap.
- No Pre on any public subprogram.
- No accepted-refusal path.
- No light library.
- No suppressed or reduced checked assertion or Ghost code.
- No Assertion_Level or policy change.
- No new `SPARK_Mode => Off` boundary. The sole original boundary stays `core/worldline-c_api.adb:25`.
- No waived warning.
- These texts stay byte-identical: the public Posts of `Exact_Value`, `Amount`, `Sum`, `Conserved`, `Contained` and
  `Check`; every `*_Reference`; the profile of `Integer_Matches`; and every existing conjunct and variant of `Prefix`.

## 3. Facts and corrections

### 3.1 Facts retained from v2, with their corrections

- **F1. Runtime limits and allocation [OBS].**
  - `RT/s-genbig.adb:1176` declares `Bignum_Limit : constant := 200`. `Normalize` (`:1178-1195`) raises
    `Storage_Error` when `X'Last - J > Bignum_Limit` (`:1190-1191`). Normalized results therefore have at most 201
    limbs of 32 bits, that is 6432 bits [K-01] or 804 bytes [K-02].
  - Direct allocations bypass `Normalize`: in `To_Bignum` (`:1230-1285`) and in the `Amount = 0` shift cases
    (`:418`, `:451`).
  - `Big_Exp` has its own limit at `:332`.
  - `System.Shared_Bignums.Length` is `Natural range 0 .. 2**23 - 1` (`RT/s-shabig.ads:46`).
  - Every bignum is heap-allocated (`RT/a-nbnbin.adb:55-58`). `Big_Integer` is controlled; Adjust deep-copies
    (`:604-609`) and Finalize frees (`:615-620`).
- **F2.** Check calls `Exact_Value` directly (`core/resource_run_ledger.adb:173-174`). D1 replaces that branch (§5.7).
- **F3.** Nonnegativity holds only under `Row_Valid` / `Shape` (`core/resource_run_ledger.ads:151-153, 226-228`).
  `Exact_Value`, `Amount`, `Sum` and `Contained` have no Pre. Negative zero and padding are admitted
  (`core/resource_reservation_transition.ads:132-138`).
- **F4. The decimal/binary interval.**
  - `10**1936 < 2**6432 < 10**1937` [K-07, K-08]. So `2**6432` and `2**6432 - 1` have 1937 digits [K-09].
  - Every magnitude with at least 1938 digits [K-10] is at least `2**6432`.
  - Python's limit governs the decimal JSON conversions (`runtime/worldline/canonical.py:41-60`). It does not govern
    `int.to_bytes` / `int.from_bytes` (`runtime/worldline/evaluation_terminal.py:76-104`).
  - *Correction:* the Python failure length is whatever limit is actually configured: 4300 by default, any value of
    at least 640, or 0 for unlimited (F25). It is not a constant.
- **F5.** Predecessor algorithms are patterns, not proofs (`HANDOFF.md:61`).
- **F6.** In C5, `Integer_Matches` is body-private with no contract (`core/canonical_artifacts.adb:431-463`).
  Packet 07 removed the initializations of `Product`/`Addend` (`:437`). No ghost decimal or binary reference exists.
- **F7.** Base64 is streamed (`:293-347`). Any work array is new storage.
- **F8.** Whole-operation costs:
  - `Contained` compares for every target after an O(N²) parent search (`core/resource_run_ledger.adb:70-90`).
  - `Check` calls each predicate at most twice, subject to short circuit (`:169-172`).
  - The transports copy inputs onto the primary stack: `core/resource_run_ledger_c_api.adb:208-213` and
    `core/evaluation_finalization_c.adb:112-118`.
- **F9.** The v2 Python observations were of the author's interpreter only. The same holds for F25.
- **F10 (confirmed).**
  - The v1 selector `Compare (Usage, Amount) = Greater` returns Invalid when either span is invalid.
    `Amount_Reference` instead compares `Q.Value`, which is 0 for an invalid span (`core/resource_quantities.ads:85-117`;
    `core/resource_run_ledger.ads:187-192`).
  - v3 keeps v2's normalization (§5.3).
  - v2's RL-12 did not discriminate the whole `Contained` result. §12.3 replaces it with two whole-result
    discriminators, RL-12 and RL-12N.
- **F11 (confirmed with scope).** `core/worldline_core_sources.gpr:8-21` defaults `WORLDLINE_BUILD` to `checks` and adds
  `-gnata`. `install.sh:184` and `packaging/PKGBUILD:31` do not select `release`. This is not evidence of the inherited
  environment, the compiled scenario, the runtime closure or the loaded binary (O-BUILD-SELECTION).
- **F12 (confirmed with scope).**
  - On `wl_finalization_decide_v1`, `Decide` maps any Ada exception to 255 (`core/evaluation_finalization_c.adb:253-256`).
  - On `wl_collapse_decide_finalization_v1`, a failure can surface at two stages:
    - **Stage 1, readiness.** `Read_Ready` calls `Decide` (`:386-388`). A 255 makes readiness invalid, and
      `Decide_Mixed` returns `Invalid_Request` with the mark `finalization.mixed.primary-ready-rejected`
      (`:427-437`; staged `:439-449`).
    - **Stage 2, context.** `Final_Context_Matches` calls `Decide` again (`:273-278`), and its own handler maps any
      exception to False (`:351-354`). `Decide_Mixed` then returns `Invalid_Request` with
      `finalization.mixed.primary-context-rejected` (`:473-478`).
    - `Decide_Mixed`'s own handler also returns `Invalid_Request` (`:505-508`).
  - Hard process faults (for example SIGSEGV on a foreign thread) are not shown recoverable.
  - None of these outcomes is an accepted mathematical refusal.

### 3.2 Corrections of v2 statements (V2-F13..V2-F18)

- **V2-F13 (padded failures).** v2 said "any span of Length ≥ 804 makes `Exact_Value` raise" and "Low (S) grows to K
  bytes … the same place".
  - *Corrected.* In the release build the pre-D1 `Exact_Value` body raises for a **valid** span of Length ≥ 804
    whatever its value. `Place` reaches 256^804 = 2^6432 [K-65], whose 6433 bits need 202 limbs [K-05, K-06]. An
    invalid span returns 0 at `:24` without looping.
  - In the checks build every checked evaluation is a separate failure point: `Power_Reference (c)` at c ≥ 804,
    `Prefix_Value_Worker` in any `Q.Value` (`core/resource_quantities.adb:147-203`), and any `Sum_Reference` or
    `Side_Sum` aggregate whose value reaches 2^6432. Aggregates can reach the limit at much shorter column extents
    when many rows are summed.
  - D1's ghost `Low (S)` need not grow at all on padded zero inputs. The failure is not "the same place" as the
    original's.
- **V2-F14 ("no other exit after allocation").** False. After the Work allocation, a checks build evaluates assertions,
  invariants and ghost statements that allocate bignums and can raise `Storage_Error`. Saved-value copies can exhaust
  memory. A proof of absence of runtime errors does not exclude native resource exhaustion
  (`SK/spark-users-guide/chapters/ch26-applying-spark.md:54-56`). §7.1 inventories every exit.
- **V2-F15 (OD-1 (ii)).** Removing `Bignum_Limit` and widening `Length` does not make "only allocation fail". The record
  layout (`RT/s-shabig.ads:58-70`) and length arithmetic must change. Automatic digit vectors stay on the stack
  (`RT/s-genbig.adb:135, 177, 364, 388, 423, 456, 580, 778`). The checked costs remain. §10 lists the complete package.
- **V2-F16 (OD-2).**
  - A fixed 4000-digit chunk exceeds the legal minimum limit of 640 by 3360 digits [K-44]. Python admits any limit of
    at least 640, or 0 (F25).
  - The daemon's integer request id (`runtime/worldline/daemon.py:304-311`), client response parsing
    (`client.py:61`) and CLI output (`cli_main.py:105, 109`) are not host-bounded.
  - E0's "native code accepts every length" is withdrawn (§9.5).
- **V2-F17 (controls).**
  - RL-1 did not establish READY: with totals and capacity both 1, `1 + 1 - 1 = 1 > 0`.
  - RL-12 and RL-14 reasoned only about the parent. §12 gives complete fixtures evaluated against the whole
    `Decision_Reference` and `Contained_Reference`.
- **V2-F18 (labels).**
  - The claim that "no fallback" preserves the release-path repair is withdrawn. §6.7 lists the alternatives.
  - F-B1 is lead-owned. Only a concrete public API/ABI or runtime-identity change is operator-owned (§4.4).

### 3.3 New lead-found facts (F19–F29)

- **F19. Installed GNATprove: unsupported loop shapes and the constants warning [OBS strings of
  `GP/libexec/spark/bin/gnat2why`].**
  - The binary's list of unsupported constructs includes:
    - "a loop invariant in a list of statements with an exception handler";
    - "a loop invariant in a list of statements with a finally section";
    - "a non-scalar object or an object with an address clause declared before the loop-invariant";
    - "a package declaration occurring in a loop before the loop invariant";
    - "a subprogram declaration occurring in a loop before the loop invariant".
  - It also carries the warning text "The initial value of constants declared before the loop invariant is not visible
    after the invariant; it shall be restated in the invariant if necessary" (tag `constants-in-loop`).
  - *Consequences for v3 [LEAD]:*
    - v2's loop bodies are restructured. They declared non-scalar and constant objects in nested blocks before
      invariants (v2:552-555, 566-571, 978-983).
    - Every non-scalar or constant temporary is hoisted out of loop bodies.
    - No loop with an invariant may sit in a handler- or `finally`-protected statement list.
  - Binary strings are not legality evidence. Probe P-X3 (§8.0) must confirm each rule.
- **F20. Recursion notices attach to recursive functions only [OBS
  `W/work/claude-operator-decision-package-v1/evidence-recursive-notices.json`, 25 unique items].**
  - Every item is on a recursive **function**: 19 on spec-level pinned references, 2 on
    `resource_reservation_transition.adb:85`, and 4 on body-local witnesses. The tags are:
    - `[contracts-recursive]`: "function contract might not be available on recursive calls";
    - `[numeric-variant]`: "expression function body of subprograms with a numeric variant might not be available on
      recursive calls".
  - `Sum_Reference` (`core/resource_run_ledger.ads:200-209`) has no explicit Post and still carries both tags.
  - Recursive lemma **procedures** with `Subprogram_Variant` carry none. Examples:
    `core/resource_quantities.adb:230-296` (`Prefix_Bounds`, `Prefix_Monotone`, `Prefix_Padding`) and
    `core/resource_reservation_transition.adb` `Prefix_Padding`, `Power_Factor`, `Prefix_Decomposition`.
  - The HANDOFF.md:161 strict-warning criterion makes these notices open obligations. Operator package R-1
    (`W/work/claude-operator-decision-package-v1/DRAFT-v2.md`) has no approval.
  - *Consequence [LEAD]:* v2 would have added seven new recursive ghost functions (`Side_Prefix`, `Side_Digits`,
    `Side_Magnitude`, `Decimal_Reference`, `Binary_Horner`, `Binary_Prefix`, `Work_Prefix`), each a new notice site.
    v3 adds **one** (`Side_Sum`, §5.4) and **none** in Algorithm B.
- **F21. Installed flow and dead-code warnings [OBS, F10K ledger
  `W/work/claude-workflow-v1/ledger.json`].**
  - INEFFECTIVE: "initialization of … has no effect". C4 `canonical_artifacts.adb:434` had this for
    `Product`/`Addend`; packet 07 removed it in C5.
  - VC_DEAD_CODE: "unreachable code", for a provably unreachable case alternative at C4 `canonical_artifacts.adb:570`;
    packet 07 removed it.
  - *Consequences [LEAD]:*
    - v3 writes no ineffective initialization.
    - Any statement that GNATprove proves unreachable risks a strict dead-code warning. That includes a handler that
      catches only native, unmodeled exceptions. It is the decisive gate on CL-1 (§7).
- **F22. Installed exception examples [OBS `GP/share/examples/spark/gnatprove_by_example`].**
  - `ug__exceptions/exceptions.adb:36-44`: a SPARK handler for an exception declared in `Exceptional_Cases`.
  - `ug__exceptions_rte/test.out:1-4`: `Exceptional_Cases => (Constraint_Error => True)` is reported as "warning:
    unreachable branch". Run-time-check exceptions are not modeled as propagation.
  - `ug__storage_error/storage.adb:4-13`: the distribution's own `Storage_Error` handler is placed in a
    `SPARK_Mode (Off)` body. That pattern is forbidden here (no new Off).
  - `ug__access4/test.adb:3-13` with `test.out`: a pool-specific `Free` and "absence of resource or memory leak at end
    of scope proved".
- **F23. `finally` is experimental [OBS `GN/share/info/gnat_rm.info:25940-25944, 27013-27075`].** It is an experimental
  GNAT extension, activated by `-gnatX0` or `pragma Extensions_Allowed (All_Extensions)`. The finally part runs after
  normal and abnormal completion. Returns that transfer out of it are illegal.
- **F24. Refined_Post and the variant warning.**
  - `GP/share/examples/spark/spark_book/Chapter-06/very_longs.adb:200-208` puts a `Refined_Post` on a function body
    in a package without abstract state.
  - The gnat2why strings include "should be implied by its refined postcondition" and "no recursive call visible on
    subprogram with Subprogram_Variant".
- **F25. Python limits on the author's own interpreter [OBS, `/usr/bin/python3` = 3.14.7].**
  - `sys.int_info`: `default_max_str_digits=4300`, `str_digits_check_threshold=640`.
  - `sys.set_int_max_str_digits(639)` raises "maxdigits must be >= 640 or 0 for unlimited".
  - `PYTHONINTMAXSTRDIGITS=100` and `-X int_max_str_digits=100` are fatal at startup.
  - `-X int_max_str_digits=640` is accepted. Under limit 640, a 640-digit `int()` succeeds and a 641-digit one is
    refused.
  - `-I` ignores the environment variable (limit stays 4300). `-I -S -X int_max_str_digits=0` gives 0.
  - No WORLDLINE process was observed.
- **F26. Repeated evaluation in the checks build [OBS].** `Artifact_Binding`, and with it `Bindings` → `Tagged_Matches`
  → `Integer_Matches`, is reached from four places:
  - the `Seal` body (`core/evaluation_finalization.adb:270`);
  - `Seal`'s Post (`core/evaluation_finalization.ads:395`);
  - the `Seal_Reference` body (`.adb:129`);
  - `Seal_Equation` (`.ads:362`), through `Seal_Reference`'s Post.
  Under `-gnata` one `Seal` can evaluate `Integer_Matches` up to four times per integer node. The mixed export can run
  `Decide` twice (F12).
- **F27. Stack copies of inputs [OBS].**
  - The transports copy whole inputs onto the primary stack (F8).
  - The project switches contain no `-fstack-check` (`core/worldline_core_sources.gpr:11-12`).
  - So stack-size dependence and stack-clash exposure already exist for input size, independently of D1.
- **F28. C5 deltas relevant to D1 [OBS `diff C4 C5`].**
  - `core/canonical_artifacts.adb`:
    - the digit loop of `Prefix` gained `pragma Loop_Invariant (From < O and then O <= S.Length)` (`:229`);
    - the `Product`/`Addend` initializations were removed (`:437`);
    - `Tagged_Matches` gained the `Parsed_Kind` selector (`:476, :482`);
    - packet 05 inserted reassociation parentheses.
  - `core/resource_quantities.*`: parenthesization only. `core/resource_run_ledger.*` are unchanged.
  - D1 packets target C5 or its reviewed successor. They write explicit left-association parentheses for mixed
    additive chains: F10K observed 98 `[operator-reassociation]` items, and packet 05 repaired them.
- **F29. Checked cost of the pinned references [LEAD, derived from source structure; unmeasured].**
  - Every pinned reference is evaluated by plain recursion under `-gnata`:
    - `Power_Reference (c)` is c recursive multiplications;
    - `Prefix_Reference (c)` re-evaluates `Power_Reference` at every level, about c³ limb operations;
    - `Prefix_Value_Worker` evaluates `Prefix_Reference` and `Power_Reference` in its loop invariants on every
      iteration, so one `Q.Value` costs about L⁴ limb operations (`core/resource_quantities.adb:160-176`).
  - Every executable function whose Post mentions `Q.Value` pays this cost in the default checks build:
    `Exact_Value`, `Nonnegative_Valid`, `Compare`, `Is_Zero`, `Is_Negative`, `Same_Epoch`, and others.
  - This is pre-existing D2 cost. §9.3 lists what D1 adds.

## 4. Scope (R-SCOPE)

### 4.1 What D1 v3 changes

| Unit | Executable change | Contract change |
|---|---|---|
| `core/resource_run_ledger.adb`: `Conserved` | two `Selected_Sum_Order (…) = Equal` tests replace `Exact_Value = Sum` | none; the Post is byte-identical |
| `core/resource_run_ledger.adb`: `Contained` | loop 2 tests `Selected_Sum_Order (…, Both_Kinds, Rows (I).Amount) = Greater`; loop 1 and the loop-2 invariant are byte-identical | none |
| `core/resource_run_ledger.adb`: `Check` | only the capacity condition (`:173-174`) becomes `Pair_Sum_Order (…) = Greater`; every other branch, its order and its status are byte-identical | none |
| `core/resource_run_ledger.adb`: new body-private entities | types, Post-free helpers, comparators, ghost model (§5.4) and lemma procedures (§5.6) | new entities only |
| `core/canonical_artifacts.ads` | none | **adds** the public ghost `Integer_Token` and **one Post conjunct** on `Prefix` (D-B-PREFIX, §6.3). Profile, existing conjuncts and variant are byte-identical |
| `core/canonical_artifacts.adb`: `Prefix` | none | adds one loop invariant to the digit loop (`:228-232`) |
| `core/canonical_artifacts.adb`: `Binary_At` | none | **adds** `Post => Binary_At'Result <= 255` (body-private, no contract today) |
| `core/canonical_artifacts.adb`: `Integer_Matches` | body replaced: verbatim guard, then work-array algorithm (§6.6); profile byte-identical | **adds** `Global => null`; no functional Post (§6.5) |
| `core/canonical_artifacts.adb`: new body-private entities | `Work_Access`/`Free_Work`, `Multiply_Add`, `Decide_Work`, ghost procedures, lemmas, `Work_Value` (§6) | new entities only |

Unchanged:

- `core/resource_run_ledger.ads` and `core/resource_quantities.*`;
- `core/evaluation_finalization*`;
- every C export, the wire layouts and all Python.

The run-ledger body uses only Resource_Quantities' public `Span_Valid`, `Digit`, `Compare`, `Prefix_Reference`,
`Power_Reference`, `Magnitude`, `Value` and `Prefix_Value`, together with lemma procedures copied per package. That
follows the established pattern (`core/resource_quantities.adb:230-296`, and the copies in
`core/resource_reservation_transition.adb`).

### 4.2 What stays OPEN: unreachability satisfies nothing

- **O-HELPERS.**
  - `Exact_Value`, `Amount` and `Sum` keep their bodies and Posts (`core/resource_run_ledger.ads:185-213`). They stay
    in the Library_Interface (`core/worldline_core.gpr:69`) and in the required roster
    (`runtime/worldline/proof_manifest.py:967`).
  - After §4.1 the source-level release path of the three exports no longer calls them. Compiled closure is O-NATIVE.
  - That does not meet their own full-domain obligation: results of 2^6432 or more are unrepresentable, and valid
    spans of 804 or more bytes raise in the release body (V2-F13).
  - The routes are OD-1 (§10).
- **O-GHOST (D2).** Under `-gnata`, every executed contract, invariant and ghost statement still evaluates
  Big_Integer. D1 adds checked work of its own (§9.3). D1 closes no part of D2.
- **O-PYTHON, O-PY-AUDIT, O-PY-COST.** OD-2 (§11).
- **O-TRANSPORT-MAPPING.** The export exception mappings (F12) are unchanged by D1. They must be classified so that a
  native failure is never counted as acceptance.
- **Physical resources.** Transport stack copies (F27), heap for the Work array (§7) and time (§9.1) remain native
  obligations.

### 4.3 Build scenarios

| Scenario | What D1 changes | What it does not change |
|---|---|---|
| `release` (selected only by `-XWORLDLINE_BUILD=release`; no in-tree path selects it, F11) | the repaired decision bodies contain no executable Big_Integer operation (source level; O-NATIVE must confirm the compiled closure) | transport copies, the Work heap allocation, `Exact_Value`/`Amount`/`Sum` (OD-1), Python (OD-2), physical limits |
| `checks` (the default, F11) | executable bodies as in `release` | every Pre/Post/invariant/ghost statement, including D1's new ones (§9.3), still evaluates Big_Integer: the representation limit and the costs of F29 remain. Large inputs still fail (D2) |

Choosing `release` to make checked Ghost disappear would violate `HANDOFF.md:129-131`. It is not a repair.

### 4.4 Ownership (synchronized with `decisions.json`)

| Lead-owned (within the fixed guarantees) | Operator-owned (no choice made here) |
|---|---|
| Algorithm A and B implementations, including the ghost-model choice A-GHOST-1 versus A-GHOST-0 (§5.4) | OD-1 runtime/type/API architectures (i-a), (i-b), (ii) (§10) |
| Additive proved strengthenings (D-B-PREFIX) and the internal alternatives PFX-2, PFX-3, PFX-5 (§6.7) | OD-2 E0/E1/E2 and the protected-custody flag or source changes E1 needs (§11) |
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
- **Signed identity [LEAD; PO-A8, PO-A13].** Let L be the sum of the magnitudes of the selected operands whose sign
  flag is False, plus the target's magnitude when the target's flag is True. Let R be the sum of the magnitudes of the
  selected operands whose flag is True, plus the target's magnitude when its flag is False.
  - Then `L - R = Σ Amount_Reference(selected) - Value(Target)`.
  - So `Σ ≤ t ⟺ L ≤ R` and `Σ = t ⟺ L = R`.
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
- A side column holds at most `Carry + 255*(N+1) ≤ 256*(N+1) ≤ 2**71`. The bound is attained at the ceiling
  [K-52, K-54].
- 64 bits are insufficient [K-14]; a signed 128-bit base suffices [K-13].
- Every conversion is a PO-A0/A12 obligation:
  - `Column_Total (Q.Digit (…))`: range 0..255;
  - `Column_Total (J - Rows'First)`: at most `2**63 - 2`;
  - `Column_Total (Rows'Length) + 1`: at most `2**63`.
- `Rows'Length + 1` is never evaluated in `Byte_Count`. `Offset + 1` appears only in ghost text, where
  `Offset ≤ Columns - 1`.

### 5.3 Executable helpers: Post-free, with facts supplied by lemmas (design rule DR-C1)

v2 gave `Normalized`, `Usage_Selected` and `Operand` Posts in terms of `Q.Value`. Under `-gnata` a Post is evaluated on
every call, and these helpers are called per row per column. Each call would then cost an L⁴-order `Q.Value`
evaluation (F29).

v3 writes them as Post-free expression functions. Their bodies are visible to proof as implicit postconditions. Their
value-level facts are lemmas (LA-9, LA-10) called once per proof point (§5.6). This removes no original assertion.

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
   with Global => null;

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

`Q.Compare` keeps its original Post (`core/resource_quantities.ads:106-117`). Its checked cost per call is pre-existing
(F29) and is listed in §9.3.

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

   --  Ghost image of a candidate operand's signed value; cubic, not quartic, under -gnata (DR-C2).
   function Signed_Prefix_Value (Data : Q.Byte_Array; X : Q.Quantity) return Valid_Big_Integer is
     (if not Q.Span_Valid (Data, X) then To_Big_Integer (0)
      elsif X.Negative then -Q.Prefix_Reference (Data, X, X.Length)
      else Q.Prefix_Reference (Data, X, X.Length))
   with Ghost, Global => null;                                   --  not recursive

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

`Side_Sum` with `Term => Digit_Term` replaces v2's `Side_Digits`. `Side_Magnitude` is no longer needed, because LA-7
links the prefix at full extent directly to `Selected_Sum`.

**A-GHOST-0, the notice-free alternative (lead-owned switch, no API change).**

- Replace `Side_Sum` by the pinned `Sum_Reference` evaluated on ghost row arrays. Each array is built by a
  non-recursive iterated aggregate
  `[for J in Rows'Range => (Rows (J) with delta Amount => Truncated (Normalized (Data, Operand (Data, Rows (J))), C),
  Observed_Usage => (Present => False))]`.
- Track only the signed difference `L - R` in the invariants. `Truncated` keeps First and Negative and sets
  `Length => Byte_Count'Min (Length, C)`.
- No new notice site arises.
- The cost is an extra factor of about K in checked evaluation, because `Sum_Reference` reaches `Q.Value` (F29), plus
  O(N) ghost row copies per evaluation (§9.3).
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

- No declaration appears in any loop body. Every invariant comes after statements only (F19).
- No initialization is ineffective (F21).
- Mixed additive chains are written left-associated with explicit parentheses (F28).
- Ghost assignments to `Low` and `Before` are ghost statements inside executable code.

Loop induction, in the guide's frame (`SK/spark-users-guide/chapters/ch23-loop-invariants.md`):

- **INIT.**
  - Inner loop: before row `Rows'First`, `Column = Before + target digit` and `Side_Sum (…, 0, …) = 0`.
  - Outer loop: before column 0, `Low = 0`, `Carry = 0`, `Power_Reference (0) = 1`, and `Side_Total (…, 0) = 0`,
    because every `Prefix_Reference (·, 0) = 0`.
- **INSIDE.** The row bound keeps every addition inside `Column_Total` (PO-A12, [K-52]). Indexing is within
  `Rows'Range`. `Operand`'s variant access is guarded.
- **PRESERVE.**
  - Inner: one row adds `Row_Term (…, Digit_Term, Offset)` to exactly one side. `Side_Sum` unfolds by one row.
  - Outer: LA-1 and LA-2 give
    `Side_Total (Offset + 1) = Side_Total (Offset) + (Column - Before) * P(Offset)`.
    With the previous invariant this becomes `Low + Column * P(Offset)`. LA-3 splits it into
    `Low' + Carry' * P(Offset + 1)` with `0 ≤ Low' < P(Offset + 1)`. LA-4 updates `State`.
- **AFTER.** At `Offset = Columns - 1`:
  - `Side_Total (S, Columns) = Low (S) + Carry (S) * P(Columns)`;
  - LA-7 and LA-8 give `Side_Total (False, Columns) - Side_Total (True, Columns) = Selected_Sum - Value (Target)`,
    because every selected operand and the target have effective length at most `Columns`;
  - LA-5 decides the sign from the carries, else from `State`.

### 5.6 Lemma procedures for Algorithm A: explicit contracts and proof plans

All of them are `Ghost`, `Global => null` and `Always_Terminates`, with full bodies. None is imported, assumed or
justified. Induction over an unbounded count (rows or columns) is **iterative**: a loop with invariants, never
recursion. That avoids checked-build recursion depth (design rule DR-C3). F20 shows that recursive procedures would
not draw notices.

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

   procedure Lemma_Order_Extension                                       --  LA-4
     (Low_L, Low_R, P : Valid_Big_Integer; D_L, D_R : Natural)
   with Pre  => P > 0 and then Low_L in 0 .. P - 1 and then Low_R in 0 .. P - 1   --  ghost Big_Integer ranges
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

- **LA-1/LA-2.** An iterative loop over `K in 0 .. Rows'Length - 1` with the invariant
  `Side_Sum (K + 1, Prefix, Offset + 1) = Side_Sum (K + 1, Prefix, Offset) + Side_Sum (K + 1, Digit, Offset) * P(Offset)`.
  Each step unfolds `Side_Sum` by one row and `Prefix_Reference (Op, Offset + 1)` by one level
  (`core/resource_quantities.ads:47-56`). The target term is one unfolding.
- **LA-3.** `T = T mod 256 + 256 * (T / 256)` for nonnegative T, then the `Column_Bounds` pattern
  (`core/resource_quantities.adb:41-64`). The pattern is copied, because body-private lemmas are not visible across
  packages.
- **LA-4.** The `Higher_Column_Order` pattern (`:66-92`), plus the equal-digit case.
- **LA-5.** If `C_L ≥ C_R + 1`, then `Low_L + C_L * P ≥ C_R * P + P > Low_R + C_R * P`. Symmetric for `<`. The integer
  bounds use `Scale_Column`-style accumulation (`:15-39`) to avoid nonlinear SMT steps.
- **LA-6.** Integer arithmetic: `(c + 255 * m) / 256 ≤ m` when `c ≤ m`.
- **LA-7.** An iterative loop over rows. Per row it uses LA-10, LA-9 and the padding fact
  `Prefix_Reference (X, Columns) = Magnitude (X)` for a valid X with `Length ≤ Columns`. That fact is a copy of
  `Prefix_Padding` (`:278-296`); an invalid span gives 0 on both sides through `Digit = 0`. LA-7 also uses the sign
  split `Value = ±Magnitude`.
- **LA-8.** The same padding fact for the target, and the sign case.
- **LA-9.** `Compare`'s Post on two valid spans (`:106-117`), `Normalized`'s body, `Magnitude`'s Post, and
  `Prefix_Value`'s Post `= Prefix_Reference` (`:69-83`).
- **LA-10.** One unfolding of the pinned `Sum_Reference` for each kind. Its expression body is available for
  non-recursive calls (F20). For `Both_Kinds`, the two-valued `Charge_Kind` partition makes exactly one `Included`
  hold for a selected row (`core/resource_run_ledger.ads:36, 195-199`).
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
(`core/resource_run_ledger.ads:406-407`). Branch order and statuses are unchanged (PO-A17, PO-A19). v2's alternative,
`Capacity_Fits`, stays rejected as primary: it is correct only under the `Shape` path condition.

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
- `= Greater` is the negation of `S_H + S_B ≤ Value (Rows (I).Amount)`. It covers every target row, and all signed,
  invalid and duplicate-identity inputs.
- Per-kind inequalities are not used. The aggregate is decided directly (PO-A15, PO-A16).

### 5.9 Termination and the terminal carry at the Byte_Count ceiling

- Every loop is a `for` loop over a finite range, so termination is structural.
- No column index at or beyond `Columns` is formed. The terminal carry is decided by LA-5 with
  `Low < 256**Columns` on both sides.
- `Side_Sum` has `Subprogram_Variant (Decreases => Count)`. It is the only new recursion. Every lemma is iterative and
  carries a `Loop_Variant` where it uses `while`.

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
- Tagged-binary padding is excluded by the guard's top-byte test. That is distinct from the leading-zero padding legal
  in `Resource_Quantities`.

### 6.2 Internal shape contract (V2-RC1)

The work representation changes from v2's 0-based `Work_Digits (0 .. B.Length)` with a sentinel cell to a 1-based
`P.Bytes (1 .. B.Length)`, with the carry out of the top cell returned as a scalar.

`P.Bytes` is `Resource_Quantities.Byte_Array` (`core/evaluation_pending.ads:9-11`). Its value is therefore given by
the **pinned** `Q.Prefix_Reference`, with no new recursive function (F20). No index `B.Length + 1` is ever formed.

| Shape fact | Statement | Established by | Used by |
|---|---|---|---|
| S1 | `Work'First = 1` | the allocator's bounds `1 .. B.Length` (§6.6), or CL-2's declaration | Pre of `Multiply_Add`, `Decide_Work` and `Work_Value` |
| S2 | `Count (Work'Length) = B.Length`. Null when `B.Length = 0` | the same | `Decide_Work` Pre; sizing |
| S3 | every cell is 0 initially | the aggregate `[1 .. B.Length => 0]` | `Decide_Work` Pre; INIT |
| S4 | no contract or assertion indexes Work outside `Work'Range` | each quantifier ranges over `Work'Range` or `Work'First .. I` with `I in Work'Range`. Unguarded uses are only `'First`, `'Last` and `'Length`, which are defined for null arrays | PO-B16 |
| S5 | bounds never change | `in out` actuals keep their bounds | — |
| S6 | there is no sentinel cell. Overflow is `Carry_Out /= 0` from `Multiply_Add` | §6.4 | PO-B8 |

A null `Work` is therefore a legal shape that no contract indexes. `Multiply_Add` on a null `Work` returns
`Carry_Out = Digit_Value`.

The minimal alternative to v2's layout, **B-SHAPE-S**, keeps the sentinel cell and adds
`Pre => Work'First = 0 and then Work'Last >= Work'First and then Work (Work'Last) = 0`, so that the array is nonempty
before its last cell is read. It is recorded but not selected: it needs the new recursive `Work_Prefix` (F20).

The public domain is unchanged:

- `Integer_Matches` is body-private.
- `Tagged_Matches` and the other public subprograms get no Pre.
- `Prefix` gets a Post conjunct only (§6.3).

### 6.3 Proof interface for digit bytes: D-B-PREFIX (primary, R-PREFIX)

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
- INIT:
  - for `[-]d`, the scanned bytes are an optional `'-'` at `From` and then `'1'..'9'` (`:217-226`);
  - `"0"` returns `After = O + 1` with the digit `'0'` (`:222-224`).
- PRESERVE: the loop condition at `:228` makes `Byte_At (A, S, O)` a digit, and `Byte_At` equals `A (S.First + O)`
  when `P.Valid` and `O < S.Length` (`:11-15`).
- Every non-integer path returns another `Form` or an invalid node, so the conjunct is vacuous there.
- `A (S.First + K)` is in range: `P.Valid (A, S)` and `K < S.Length` give `S.First + K ≤ A'Last`.
- The existing `[contracts-recursive]` notice on `Prefix` (F20) is unchanged. The new conjunct is used only at
  non-recursive call sites.

`Binary_At` (body-private, no contract today) gains `Post => Binary_At'Result <= 255` (PO-B3). The three cases give at
most 255 [K-49, K-50, K-51]. `B64_Digit ≤ 63` by its expression (`:287-292`); negative digits return 0 early
(`:338, :341, :344`).

Digits in `Decide_Work`:

- `N = Prefix (A, J, 0)` is valid with `First = 0` (Post), and the guard gives `N.After = J.Length`. The conjunct
  yields `Integer_Token (A, J, 0, N.After)`.
- If `Negative`, then `Start = 1` and only `K = 0` may be `'-'`, so every byte in `1 .. N.After - 1` is a digit.
- Otherwise byte 0 is not `'-'`, so all bytes are digits.
- Hence `Decide_Work`'s digit Pre holds (PO-B2).

### 6.4 `Multiply_Add`: one decimal digit, cell-wise carries, no array snapshot in the Post

```ada
--  UNCOMPILED / UNPROVED — core/canonical_artifacts.adb, body-private (packet D1-B)
   package RQ renames Resource_Quantities;   --  added "with Resource_Quantities;" (P already depends on it)

   function Work_Value (W : P.Bytes) return Valid_Big_Integer is
     (RQ.Prefix_Reference (W, (Negative => False, First => 1, Length => Count (W'Length)),
                           Count (W'Length)))
   with Ghost, Global => null, Pre => W'First = 1;                --  not recursive; pinned reference

   subtype Carry_Digit is Natural range 0 .. 9;
   type Carry_Vector is array (P.Index range <>) of Carry_Digit with Ghost;

   procedure Multiply_Add (Work : in out P.Bytes; Digit_Value : Natural; Carry_Out : out Natural)
   with Global => null, Always_Terminates,
     Pre  => Work'First = 1 and then Digit_Value <= 9,           --  shape only; null Work admitted; no indexing
     Post => Carry_Out <= 9
       and then Work_Value (Work)
                + To_Big_Integer (Carry_Out) * RQ.Power_Reference (Count (Work'Length))
              = To_Big_Integer (10) * Work_Value (Work)'Old + To_Big_Integer (Digit_Value);

   procedure Multiply_Add (Work : in out P.Bytes; Digit_Value : Natural; Carry_Out : out Natural) is
      Old_Work : constant P.Bytes := Work with Ghost;               --  checked builds only: Work'Length bytes (§9.3)
      Carry_In : Carry_Vector (Work'Range) := [others => 0] with Ghost;   --  checked builds only (§9.3)
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
```

Notes:

- The loop invariants are integer-only. Their checked cost is O(I) integer comparisons, not Big_Integer (§9.3).
- `Old_Work` is a ghost constant declared **outside** the loop, so the F19 rule about non-scalars before the invariant
  does not apply. Whether GNATprove keeps `Old_Work = Work'Old` across the loop is probe P-X3; restating it as an
  invariant is the fallback.
- The Post saves `Work_Value (Work)'Old`, a Big_Integer, instead of the array. The value is all the Post needs (V2-RC6).
- `K + 1` occurs only under `K < I ≤ Work'Last`.
- **LB-5, `Lemma_Multiply_Add_Value (Before, After, Carry_In, D, C_Out)`.**
  - Pre: equal bounds starting at 1; `D ≤ 9`; `C_Out ≤ 9`; `(if After'Length > 0 then Carry_In (1) = D else
    C_Out = D)`; and the per-cell relations of the last invariant at `I = After'Last`.
  - Post: `Work_Value (After) + C_Out * P(len) = 10 * Work_Value (Before) + D`.
  - Proof: an iterative loop over k with the invariant
    `Prefix (After, k) + c_k * P(k) = 10 * Prefix (Before, k) + D`, where c_k is `Carry_In (k + 1)`, or `C_Out` at the
    end. Each step uses one unfolding of `Prefix_Reference` on each array, `P(k+1) = 256 * P(k)`, and
    `(t mod 256) + 256 * (t / 256) = t`. No array is updated inside the lemma, so no frame lemma across an assignment
    is needed.

### 6.5 `Decide_Work`: the original statements as ghost lockstep (B-REF-L, primary)

v2 defined new closed recursive references (`Decimal_Reference`, `Binary_Horner`, `Binary_Prefix`, `Work_Prefix`). Each
would be a new R-1 notice site (F20) and a new checked recursion of depth m or n, a stack risk the v2 review accepted
as real.

v3 instead **executes the original function's own statements as ghost code in lockstep** with the new executable
algorithm. It proves inside the body that the returned Boolean equals the original statements' result:

- **The reference.** It is the original body itself: `core/canonical_artifacts.adb:446-462`, moved verbatim into ghost
  statements. Textual identity is a mechanical obligation (PO-B21).
- **No new recursive function and no recursion.**
- **No functional Post on `Integer_Matches`.** The original had no contract (F6), and no caller's contract mentions
  integer semantics (§6.9). D-B-SPEC, v2's added functional Post, is withdrawn. The correspondence is a proved in-body
  assertion at every return of `Decide_Work`.

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
         pragma Loop_Invariant (Work_Value (Work) = Decimal_Value);
         pragma Loop_Variant (Decreases => Stop - O);
         Product := Decimal_Value * To_Big_Integer (10);                                    --  ghost, verbatim :449
         Addend := To_Big_Integer (Integer (Byte_At (A, J, O) - Character'Pos ('0')));     --  ghost, verbatim :450
         Decimal_Value := Product + Addend;                                                 --  ghost, verbatim :451
         Multiply_Add (Work, Byte_At (A, J, O) - Character'Pos ('0'), Carry);
         if Carry /= 0 then
            --  Decimal_Value = Work_Value (Work) + Carry * 256**n >= 256**n (PO-B8). Later digits never decrease
            --  it (PO-B9), and any n-byte binary value is below 256**n (PO-B10): an inequality theorem, not a cap.
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
         pragma Loop_Invariant
           (RQ.Prefix_Reference (Work, (False, 1, Count (Work'Length)), K)
            + RQ.Power_Reference (K) * Binary_Value = Work_Value (Work));   --  cells above K equal the bytes so far
         pragma Loop_Variant (Decreases => K);
         K := K - 1;                                                                        --  verbatim :457
         Product := Binary_Value * To_Big_Integer (256);                                    --  ghost, verbatim :458
         Addend := To_Big_Integer (Integer (Binary_At (A, T, B, K)));                       --  ghost, verbatim :459
         Binary_Value := Product + Addend;                                                  --  ghost, verbatim :460
         if Natural (Work (K + 1)) /= Binary_At (A, T, B, K) then
            --  First difference from the top: the two values lie in distinct blocks [x*256**K, (x+1)*256**K)
            --  (PO-B12, LB-3).
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

The original variable `O` of the decimal loop and the original binary loop variable are represented by `O` and `K`.
`K` plays the original's binary `O`, starting at `B.Length` and decremented before use, exactly as `:454-457`.

Ghost procedures: bodies are the original statements; Posts are bounds only.

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
     Post => Value >= Value'Old * RQ.Power_Reference (Upto)
             and then Value < (Value'Old + To_Big_Integer (1)) * RQ.Power_Reference (Upto);
   --  Body: O := Upto; then the loop :455-461 verbatim, with the invariant
   --  Value'Loop_Entry * P(Upto - O) <= Value < (Value'Loop_Entry + 1) * P(Upto - O), which uses Binary_At <= 255.
```

The overflow path calls `Finish_Binary` with `Upto = B.Length` and `Binary_Value = 0`, which yields
`0 ≤ Binary_Value < 256**n`.

Remaining B lemmas (procedures; iterative where induction is input-sized):

- **LB-1.** `0 ≤ Prefix_Reference (W, S, k) < Power_Reference (k)`. A copy of `Prefix_Bounds`
  (`core/resource_quantities.adb:230-257`), made iterative.
- **LB-2 (overflow).** `V ≥ 0` and `C ≥ 1` give `V + C * P ≥ P`.
- **LB-3 (distinct blocks).** Integers `x ≠ y` with `0 ≤ a, b < P` give `x * P + a ≠ y * P + b`.
- **LB-4 (split).** `Prefix (W, k + 1) = Prefix (W, k) + W (k + 1) * P(k)` and `P(k + 1) = 256 * P(k)`. Each is one
  unfolding.
- **LB-5.** §6.4.
- **LB-6.** The `Integer_Token` digit facts of §6.3.

### 6.6 `Integer_Matches`: owner, allocation and every exit (CL-1, §7)

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
      then return False; end if;                                              --  :439-445 verbatim; nothing allocated
      Work := new P.Bytes'[1 .. B.Length => 0];                               --  B.Length cells; null when 0
      Decide_Work (A, J, (if Negative then N.First + 1 else N.First), N.After, T, B, Work.all, Result);
      Free_Work (Work);
      return Result;
   exception
      when others =>
         Free_Work (Work);        --  no-op when Work is null (never allocated, or already freed)
         raise;                   --  the same occurrence propagates unchanged; it is never turned into a value
   end Integer_Matches;
```

- **Loop invariants.** There is no loop in `Integer_Matches`, so the unsupported construct "a loop invariant in a list
  of statements with an exception handler" (F19) cannot arise. All loops are in `Decide_Work`, `Multiply_Add` and
  the ghost procedures.
- **Start offset.** `N.First + 1` occurs only after the guard, where `N.First = 0` by `Prefix`'s Post.
- **Allocation size.** `B.Length ≤ 3 * (2**61 - 1) = 6917529027641081853` [K-18, K-19], from `Base64`'s
  `(Size / 4) * 3 - Padding` (`:305, :324`) with `Size ≤ Count'Last - 2`. The native size computation has
  `2305843009213693954` of headroom [K-20]. Physical fit is O-WORKSPACE.
- **Borrow.** `Work.all` is borrowed for the `Decide_Work` call (`SK/spark-users-guide/chapters/ch13-pointers-and-ownership.md`).
- **Normal exits.**
  - Every guard exit precedes allocation.
  - The single post-allocation normal exit frees before `return`.
  - `Free_Work` sets `Work` to null, which serves the end-of-scope leak check.

### 6.7 Correction of the "no fallback" claim: proof-interface alternatives (V2-RC1, V2-F18)

v2 said that refusing the `Prefix` strengthening left no fallback that preserves the repair. That is withdrawn. The
alternatives below are internal reformulations owned by the lead, unless one of them changes a public contract. None
is implemented or accepted. Each needs its own legality probe and proof.

| Id | Alternative | Public spec | Evidence it needs | Known risk |
|---|---|---|---|---|
| PFX-1 (primary) | D-B-PREFIX, §6.3 | adds one Post conjunct and the ghost `Integer_Token` (R-PREFIX: eligible in principle) | PO-B1; checked cost of one quantified token check per integer `Prefix` call (§9.3) | none known beyond proof |
| PFX-2 | `Refined_Post` on `Prefix`'s body carrying the integer-token conjunct, with `Integer_Token` body-private | byte-identical | installed probe P-PFX2: legality of `Refined_Post` on a visible, recursive function without abstract state (F24 shows one without recursion); its use at body-internal call sites; the "should be implied by its refined postcondition" check; no new warning ("refined postcondition does not check the outcome …") | unknown interaction with the existing `[contracts-recursive]` notice |
| PFX-3 | a private core `Prefix_Core` with the stronger Post, and `Prefix` completed in the body as `(Prefix_Core (A, S, From))` | byte-identical text | probe P-PFX3 | the unchanged `Subprogram_Variant` on a now non-recursive `Prefix` should draw "no recursive call visible on subprogram with Subprogram_Variant" (F24), a new strict warning. Removing the variant is a public contract-text change requiring review. The `[contracts-recursive]` site would move to `Prefix_Core`. Full equivalence of the parser recursion and of every caller must be re-proved |
| PFX-5 | general-addend arithmetic: the work array handles the original addend domain `-48 .. 207` with signed digit propagation, so no digit fact is needed | unchanged | a new proof of signed propagation | more complex, but internal |
| PFX-4 (rejected) | executable digit validation with an executable Big_Integer fallback on non-digits | — | — | rejected: executable Big_Integer would remain on a path the proof cannot exclude |

### 6.8 B-REF-R: v2's closed references, retained as an alternative

v2's `Decimal_Reference`, `Binary_Horner`, `Binary_Prefix`, `Work_Prefix` and `Integer_Matches_Reference` (v2:775-842)
would give `Integer_Matches` a functional Post (D-B-SPEC). They are retained as alternative B-REF-R, with two known
costs:

- four new recursive-function notice sites (F20);
- checked recursion of depth m and n (§9.3).

B-REF-L dominates on both counts and keeps the original statements as the reference.

### 6.9 Equivalence summary [LEAD; §8.2 obligations]

- Guard exits are byte-identical and precede allocation (PO-B14).
- On the guarded path, digits are `0..9` (PO-B2) and the lockstep invariant `Work_Value (Work) = Decimal_Value` holds
  (PO-B7).
- **Overflow path.**
  - `Decimal ≥ 256**n` (PO-B8) and stays so (PO-B9).
  - `Binary < 256**n` (PO-B10).
  - So the original returns False.
- **Mismatch path.** The first differing cell from the top separates the values (PO-B12).
- **Match path.** `Decimal_Value = Work_Value = Binary_Value` (PO-B11).
- **Result.** `Integer_Matches` returns exactly the Boolean that the original statements compute, on every input that
  passes the guard. In proof semantics Big_Integer is unbounded, so this covers values at and above 2^6432.
- **Callers.** `Tagged_Matches`, `Array_Payloads_Match`, `Bindings`, `Artifact_Binding` and `Seal` stay byte-identical.
  None of their contracts mentions integer semantics (`core/canonical_artifacts.ads:61-66, 77-81`;
  `core/evaluation_finalization.ads:332-339, 353-400`). Their existing proofs are re-run (PO-B19).
- **Release build.** It executes no Big_Integer operation in `Integer_Matches`, `Decide_Work` or `Multiply_Add`
  (O-NATIVE confirms the compiled closure).

## 7. Work lifetime and reclamation on every exit (V2-RC2, R-WORKSPACE)

### 7.1 Every exit after allocation (V2-F14 corrected)

Release-build ghost code is removed, because the default assertion policy is Ignore (inventory `SUMMARY.md` §(2), citing
`gnat_rm.info:14888-14889`).

| # | Exit after `new` | Builds | Mechanism | Reclaimed by |
|---|---|---|---|---|
| X1 | normal return of `Result` | both | `Free_Work` before `return` | normal path |
| X2 | `Storage_Error` from the allocator itself | both | raised before `Work` is assigned | nothing to reclaim; handler's `Free_Work` on null is a no-op |
| X3 | `Storage_Error` or `Assertion_Error` raised while evaluating `Decide_Work`'s or `Multiply_Add`'s Pre/Post, a loop invariant, a ghost lockstep statement, a lemma's Pre/Post or body, `Finish_Decimal`/`Finish_Binary`, `Work_Value`, `Prefix_Reference` or `Power_Reference` | checks | bignum limit (F1) or heap exhaustion inside checked evaluation; callee frames propagate to `Integer_Matches` | CL-1 handler |
| X4 | `Storage_Error` from saved-value copies: `Multiply_Add`'s ghost `Old_Work` (n bytes) and `Carry_In`, and `Work_Value (Work)'Old` (heap bignum) | checks | stack or heap exhaustion | CL-1 handler (when raised as `Storage_Error`) |
| X5 | primary-stack overflow without stack checking (F27) | both | SIGSEGV; GNAT may convert it to `Storage_Error` only where its signal handler and alternate stack exist; on a foreign thread the process may die | process death releases memory; a hard fault, recorded as a native failure (OPEN), never recovered or accepted |
| X6 | exceptions in the Post check of a caller of `Integer_Matches` (for example `Seal`'s Post, F26) | checks | raised after `Integer_Matches` returned, when its `Work` is already freed | nothing to reclaim |
| X7 | exceptions in `Integer_Matches`'s declarative part (`Base64`, `Byte_At`) | both | before allocation | nothing to reclaim |

Bignum temporaries are controlled. On every propagation they are finalized by Ada semantics (RM 7.6.1;
`RT/a-nbnbin.adb:615-620`). Whether GNAT actually finalizes every transient checked temporary on exception is native
evidence item P-W6.

### 7.2 CL-1 (primary): pool-specific owner plus function-level handler with re-raise

The code is §6.6. Requirements:

- the handler frees and re-raises the same occurrence, and never converts it to a value;
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
| P-W1 | Is a non-allocating `Global => null` Boolean function with a pool-specific allocator, a borrow of `Work.all` for an `in out` call, `Free_Work` before `return`, and `exception when others => Free_Work (Work); raise;` legal SPARK? | no SPARK legality or unsupported-construct error |
| P-W2 | Ownership and leak checks | "absence of resource or memory leak … proved" at each `Free_Work` and at end of scope, including in the handler; no move or borrow error |
| P-W3 | Proof warnings under `--proof-warnings=on` | **no** unreachable-code, unreachable-branch or other new warning on the handler or the bare `raise;` |
| P-W4 | Use in assertions | the function is called from another function's Post (as `Seal`'s Post reaches it, F26) without "allocating function inside an assertion" or a leak error |
| P-W5 | Flow | no flow error or warning (including INEFFECTIVE) |
| P-W6 | Native (§7.4) | handler coverage, finalization of temporaries and leak-freedom under induced failures |
| P-W7 | Alternative shapes | the same battery for CL-2 and CL-3 |
| P-W8 | Absence of new Off | probe units contain no `SPARK_Mode => Off`; the sole boundary stays `core/worldline-c_api.adb:25` |

### 7.4 Native evidence plan (O-EXCEPTION-CLEANUP, O-WORKSPACE; none run)

- **Expanded code.** Compile both scenarios on the exact toolchain. Inspect `-gnatG` for:
  - the allocator's in-place initialization, with no primary-stack temporary of n bytes;
  - the placement of `Old_Work`, `Carry_In` and `'Old` copies (primary stack, secondary stack or heap);
  - the postcondition wrapper `_wrapped_statements` relative to the handler, which shows that the handler covers
    exceptions from callee contracts;
  - transient-temporary finalization on exception.
- **Fault injection in a scratch harness.**
  - Allocation failure at the `new`: inject `malloc` failure at the k-th allocation.
  - Post-allocation checked failure: in the checks build, an integer of at least 2^6432 [K-07] raises inside ghost
    lockstep after allocation.
  - Saved-copy failure: a large n on a small thread stack, if the harness admits it.
  - For each, the expected observations:
    - the exception propagates unchanged;
    - the export maps it as F12 shows;
    - the diagnostic stream records `finalization.decide` with the exception;
    - the heap returns to its baseline.
- **Repeated calls.** Run N calls alternating success, mathematical False and injected failure, and record heap
  high-water and in-use bytes. A leak audit by `gnatmem` (link `-largs -lgmem`, `SK/gnat-toolchain`) or by allocator
  statistics: final water mark zero.
- **Stage separation on the mixed export.** Inject failure only at the first, then only at the second `Decide`
  invocation. Expect `primary-ready-rejected` and `primary-context-rejected` respectively (F12).
- Every injected failure is a resource failure: an OPEN native obligation, never an accepted refusal.

### 7.5 Lead-owned alternatives if a CL-1 gate fails

**CL-2: frame lifetime, the former F-B1 (lead-owned; no API change).** After the guard, in `Integer_Matches`:

```ada
--  UNCOMPILED / UNPROVED
      declare
         Work : P.Bytes (1 .. B.Length) := [others => 0];      --  primary stack; freed by unwinding on every exit
      begin
         Decide_Work (A, J, Start_Of (N, Negative), N.After, T, B, Work, Result);
      end;
      return Result;
```

- No handler and no ownership are needed. Every normal and exceptional exit reclaims the frame.
- Native obligations:
  - the exact stack placement and frame size from `-gnatG` and assembly;
  - measured stack headroom at the deepest export call depth, for every originally successful input;
  - recursion headroom, since `Tagged_Matches` is recursive;
  - stack-clash exposure without stack probes (F27; probes depend on `-fstack-check` or
    `-fstack-clash-protection`, absent from `core/worldline_core_sources.gpr:11-12`; adding one is a reviewed
    configuration change).
- Originally successful values are below 2^6432, so n ≤ 804 bytes [K-02]. Larger, newly successful inputs need about
  n more stack bytes on top of the transport's copy of at least 4n/3 input bytes (F27).
- Stack exhaustion is a native failure: OPEN, never accepted.

**CL-3: GNAT `finally` (lead-owned, experimental, last resort).** `Work := new …; Decide_Work (…);` followed by a
`finally` part containing `Free_Work (Work);`, with the return after the block.

- The finally part is reachable in the normal path, so no dead-code warning is expected.
- It requires the experimental extension (F23). That means `pragma Extensions_Allowed (All_Extensions)` in
  `canonical_artifacts.adb`, or isolating the owner in a small private child unit. That widens the unit's language
  mode.
- It needs probes P-W1..W8 for `finally`. F19 lists "a loop invariant in a list of statements with a finally section"
  as unsupported, so the loops stay in `Decide_Work`.
- It needs separate GPT-6.1 review of the experimental-mode use.

### 7.6 Operator-owned API/ABI packages: F-B2 and F-B3 (not selected; incomplete without the items listed)

| Package | What it is | Required before it could be eligible |
|---|---|---|
| F-B2: procedure migration | the workspace comes from a procedure caller; `Tagged_Matches`, `Array_Payloads_Match`, `Bindings`, `Artifact_Binding`, `Seal` and the C exports gain procedure successors | Every function version stays in contracts (`Seal`'s Post, `Seal_Equation`; `core/evaluation_finalization.ads:353-400`) and therefore still executes under `-gnata`. It needs an executable, non-allocating, equivalent body, which is the problem itself. The package must also supply: equivalent checked functions; every original capability and caller preserved; re-proof of every original contract; no new Off boundary; explicit operator approval of a concrete API, which is not proof (`HANDOFF.md:121`) |
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
| PO-X1 | Installed compile legality with `-gnat2022 -gnatwa -gnatVa -gnatf`: no new warnings and no `pragma Warnings (Off)`. GNATprove 16.1.0 legality of: the Ghost generic instance `Column_Big`; bracket and iterated aggregates; declare-free loop bodies; the pool-specific access type with its `Unchecked_Deallocation` instance; the handler and bare re-raise (P-W1); `Refined_Post` only if PFX-2 is used |
| PO-X2 | Flow: `Global => null` on every new subprogram; no uninitialized read; no INEFFECTIVE initialization (F21) |
| PO-X3 | No `Annotate` justification, no `Assume`, no imported or bodiless lemma |
| PO-X4 | Checked-build executability of all new ghost code; no Assertion_Level or policy change; cost recorded in §9.3 |
| PO-X5 | Pins refreshed only through the official generator (`runtime/worldline/proof_manifest.py:10`); roster additions append-only |
| PO-X6 (P-X3) | Installed shape rules of F19: no declaration in a loop body before an invariant; no loop with an invariant in a handler- or `finally`-protected list; whether `Old_Work = Work'Old` survives the `Multiply_Add` loop |
| PO-X7 (P-R1) | Recursion notices: confirm that `Side_Sum` draws `[contracts-recursive]`/`[numeric-variant]` and that iterative or recursive lemma procedures draw none. Resolution of the `Side_Sum` notice joins R-1. Otherwise switch to A-GHOST-0 |
| PO-X8 | Reassociation: every mixed additive chain explicitly left-associated (F28); no `[operator-reassociation]` item |

### 8.1 Algorithm A

| Id | Obligation |
|---|---|
| PO-A0 | `type Column_Total is range 0 .. 2**71` accepted with a 128-bit base on the pinned GNAT 16.1.0 aarch64; every §5.2 conversion is free of runtime errors |
| PO-A1 | LA-10 for `Held_Only`, `Budget_Only` and `Both_Kinds` (partition) |
| PO-A2/A3/A23 | LA-9: normalization keeps value; `Usage_Selected` equals the value comparison; `Operand`'s value equals `Amount_Reference` when counted |
| PO-A4/A5 | Invalid spans give zero prefixes; padding gives `Prefix_Reference (X, C) = Magnitude (X)` when `Length ≤ C` (copied `Prefix_Padding`) |
| PO-A6 | LA-1/LA-2 column step |
| PO-A7 | LA-7 signed completion at the extent |
| PO-A8/A13 | Sign split and target placement (LA-7, LA-8) |
| PO-A9 | LA-3 column emit |
| PO-A10 | LA-4 order extension |
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

### 8.2 Algorithm B

| Id | Obligation |
|---|---|
| PO-B1 | `Prefix`'s new conjunct, proved in its body; existing conjuncts and variant unchanged |
| PO-B2 | Digit range on `[Start, Stop)` from `Integer_Token` (LB-6) |
| PO-B3 | `Binary_At` Post `≤ 255` [K-49..K-51] |
| PO-B4 | `Multiply_Add` loop: unprocessed-cell frame against `Old_Work`; per-cell carry relations; `Old_Work = Work'Old` (PO-X6) |
| PO-B5 | Column arithmetic: `T ≤ 2559`, carry ≤ 9 [K-15, K-16]; LB-5 |
| PO-B6 | `Multiply_Add` Post, including the null-Work case (`Carry_Out = Digit_Value`, `P(0) = 1`) |
| PO-B7 | Decimal lockstep invariant preservation |
| PO-B8 | Overflow: `Carry ≥ 1 ⇒ Decimal_Value ≥ 256**n` (LB-2) |
| PO-B9 | `Finish_Decimal` monotonicity (digits nonnegative) |
| PO-B10 | `Finish_Binary` bounds; overflow path `Binary_Value < 256**n` |
| PO-B11 | Match path: compare-phase invariant; at `K = 0`, `Binary_Value = Work_Value` |
| PO-B12 | Mismatch path: first difference from the top (LB-3, LB-4, LB-1) |
| PO-B13 | The three in-body assertions `Result = (Decimal_Value = Binary_Value)` |
| PO-B14 | Guard identity: the guard text equals C5 `:439-445`; `Start` equals `:446`'s offset |
| PO-B15 | Ownership and memory: P-W1..P-W5 for CL-1; or the CL-2 or CL-3 equivalents |
| PO-B16 | Shape and sizing: S1..S6; no index outside `Work'Range`; no `B.Length + 1`; native size [K-19, K-20] |
| PO-B17 | Termination: loop variants; no recursion |
| PO-B19 | Callers byte-identical and their existing contracts re-proved |
| PO-B20 | Freedom from runtime errors of every new ghost expression on every input that reaches it |
| PO-B21 | Lockstep textual identity: the ghost statements in `Decide_Work`, `Finish_Decimal` and `Finish_Binary` are C5 `:436, :447-461` verbatim, modulo variable renaming (`O`/`K`, `Value`). A mechanical check, retained as evidence |

### 8.3 Native and resource obligations (evidence, not proof)

| Id | Obligation |
|---|---|
| PO-N1 | Compiled release call closure of the repaired bodies contains no Big_Integer operation (link map, objdump, `-gnatG`) |
| PO-N2 | The allocator is initialized in place, with no n-byte stack temporary; or CL-2's frame placement |
| PO-N3 | `Column_Total` arithmetic uses 128-bit operations; any `System.Arith_128` call allocates nothing |
| PO-N4 | Heap, stack and time measurements for §9 on the exact integrated library and runtime identity |
| PO-N5 | Export exception mapping classified (F12) without counting a native failure as acceptance |
| PO-N6 | P-W6: handler coverage, temporary finalization and leak-freedom under induced failures |
| PO-N7 | Checked-build saved-value placement and costs (§9.3) measured |

## 9. Native cost, failure semantics and the D2 delta (V2-RC6)

All formulas are **[LEAD] design estimates from source structure**. They are not measurements, and they are not proved
cost bounds (O-COST-MEASURE). Symbols:

- N rows; K = `Columns`, the maximum effective length;
- L an operand length (L ≤ K);
- m decimal digits; n magnitude bytes;
- `id` the identity length used by `Same`.

### 9.1 Release-build costs of the new executable code

| Operation | Time (operation counts) | Auxiliary memory | Allocation |
|---|---|---|---|
| `Selected_Sum_Order` | pre-pass `Σ_j (c + id_j)`; columns `O(N·K + Σ_j min(L_j, K)·(id_j + u_j·L_j))`, where `u_j = 1` for a Held row with usage present (its `Compare` costs O(L_j) per column visit) | O(1) scalars; no secondary stack | none |
| `Pair_Sum_Order` | O(K) | O(1) | none |
| `Conserved` / `Contained` / `Check` | existing `Shape` and O(N²) `Parent_Supports` plus the comparator calls above; worst case `O(N²·K + N·Σ_j L_j·(id_j + u_j·L_j))` per `Contained` | O(1) beyond inputs | none |
| `Integer_Matches` | guard as today; decimal phase at most `m·n` cell steps with early exit; compare phase at most n | n heap bytes plus allocator header (CL-1), or n primary-stack bytes (CL-2) | one allocate and one free per call (CL-1) |

There is no asymptotic dominance claim against the original. Where the original succeeded (values below 2^6432), it
allocated O(L) heap and automatic digit vectors per bignum operation (F1, V2-F15).

### 9.2 Failure semantics by scenario (corrected; "release" means `-XWORLDLINE_BUILD=release`)

| Path | Pre-D1 release | Post-D1 release | Checks build (default) |
|---|---|---|---|
| Run ledger, valid span with Length ≥ 804, or a value or sum ≥ 2^6432 | `Storage_Error` → `-1` (`core/resource_run_ledger_c_api.adb:222`) → Python `CoreUnavailable` (`runtime/worldline/resource_run_ledger.py:246`) | decision computed in the source-level design (O-NATIVE); time and stack-copy costs remain | still fails at the first checked evaluation reaching the limit. Example: `Nonnegative_Valid`'s Post inside `Shape` on a padded 804-byte span. D2 OPEN |
| Run ledger, invalid span of any Length | the value is 0, with no loop (`:24`) | the same, with zero columns | Post evaluation returns 0 |
| `Integer_Matches`, value ≥ 2^6432 | `Storage_Error` → 255 (plain); `Invalid_Request` (mixed, stage 1 or 2, F12) | Boolean computed (design); heap or stack n bytes; exhaustion is OPEN | ghost lockstep reaches the limit after allocation → X3 → CL-1 frees and re-raises → 255 / `Invalid_Request`. D2 OPEN |

E0's "native code accepts every length" (v2:1455) is withdrawn. D1 establishes no default-build success, no physical
fit and no loaded-identity behaviour.

### 9.3 Checked-build (`-gnata`) work: pre-existing, and added by D1

| Item | Pre-existing or D1 | Order per evaluation [LEAD] | Notes |
|---|---|---|---|
| `Q.Value` / `Magnitude` via `Prefix_Value_Worker` | pre-existing | ~L⁴ limb ops; recursion depth L | F29; reached from every `Q.Value`-based Post |
| `Power_Reference (c)`, `Prefix_Reference (c)` | pre-existing | ~c² and ~c³ limb ops; depth c | F29 |
| `Sum_Reference` over N rows | pre-existing | N·(row term); depth N | `Contained` loop-2 invariant and `Check`'s Post |
| `Selected_Sum_Order` Post | D1 | `Selected_Sum` → `Sum_Reference` → `Amount_Reference` → `Q.Value`: ~N·L⁴ | once per call |
| Outer column invariant | D1 | `Side_Total` → `Side_Sum (Prefix_Term)`: ~N·c³ per column, ~N·K⁴ per call; depth N + c | A-GHOST-0 multiplies this by about K |
| Inner row invariant | D1 | `Side_Sum (Digit_Term)` over J rows: ~J·(id + `Operand` cost) per row; `Operand` → `Compare`, whose Post is ~L⁴ (pre-existing Post, newly called here) | the dominant D1 term with usage rows: ~N²·K·L⁴ per call; DR-C1 keeps new helpers Post-free |
| `Lemma_Column_Step` per column | D1 | iterative over N rows, each step evaluating `Side_Sum` at two extents: ~N²·c³ | lemma bodies execute under `-gnata` |
| `Lemma_Signed_Completion`, `Lemma_Close` | D1 | ~N·(L⁴ + K³) once per call | |
| `Integer_Matches`: decimal invariant `Work_Value (Work) = Decimal_Value` | D1 | `Prefix_Reference (Work, n)`: ~n³ per digit, ~m·n³ total | ghost lockstep values are bignums of n bytes |
| `Multiply_Add` per call | D1 | integer invariants O(I) per cell, O(n²); LB-5 iterative ~n⁴; `Work_Value (Work)'Old` ~n³ | **saved values:** `Old_Work` n bytes (primary stack, placement PO-N7), `Carry_In` n elements, `'Old` bignum (heap) |
| Compare-phase invariant | D1 | `Prefix_Reference (Work, K)` plus `Power_Reference (K)` per cell: ~n⁴ total | |
| `Finish_Decimal` / `Finish_Binary` | D1 | the original computations, O(m² + n²) limb ops, plus invariant `Power_Reference` evaluations ~n³ | the original statements now run as ghost |
| `Prefix`'s new conjunct | D1 | O(token) quantified check per integer-node `Prefix` call | |
| Repetition | D1 × F26 | every `Integer_Matches` cost above occurs up to four times per `Seal` and twice per mixed request | |

Consequences:

- Under the current runtime, the representation limit (F1) stops checked evaluation at 2^6432. Below it, the orders
  above can make checks-build time for originally fast large inputs, and for padded run-ledger inputs, impractical.
  That is a cost-correspondence failure for the default build, recorded under O-GHOST and O-COST-MEASURE, not hidden.
- The pre-existing pinned references already have this character (F29).
- D2 must establish checked costs for original and D1 code together, without deleting or weakening any original
  checked assertion or Ghost requirement. Candidate D2 directions, recorded only, each needing separate review:
  - cost-correct executable definitions of the references;
  - logarithmic-depth reference forms with equivalence lemmas;
  - a runtime package (OD-1).
- D1's own new assertions follow lead-owned cost rules:
  - DR-C1: no `Q.Value`-based Post on per-iteration executable helpers;
  - DR-C2: ghost terms use `Prefix_Reference` forms rather than `Q.Value`;
  - DR-C3: iterative lemmas;
  - DR-C4: value snapshots rather than array snapshots in Posts.
  None of these rules removes an obligation; each still needs a complete proof.

### 9.4 The two mixed-export failure stages (F12)

| Stage | Call site | Outward result on native failure | Distinguishing evidence |
|---|---|---|---|
| plain export | `Decide` (`core/evaluation_finalization_c.adb:121-257`) | 255 (`:253-256`) | 255 against `0` with `Reason ≠ 0` for a mathematical False: distinct outwardly |
| mixed, stage 1 (readiness) | `Read_Ready` → `Decide` (`:386-388`) | `Invalid_Request` with mark `finalization.mixed.primary-ready-rejected` (`:433-436`) | the `finalization.decide` exception diagnostic, versus a reason value |
| mixed, stage 2 (context) | `Final_Context_Matches` → `Decide` (`:273-278`), or its handler (`:351-354`) | `Invalid_Request` with mark `finalization.mixed.primary-context-rejected` (`:474-477`) | the `finalization.context` or `finalization.decide` exception diagnostic |
| mixed, elsewhere | `Decide_Mixed` handler (`:505-508`) | `Invalid_Request` | the `finalization.mixed` exception diagnostic |

On the mixed export a mathematical False and a native failure are outwardly identical (`Invalid_Request`). Only the
diagnostics distinguish them. Controls must assert on the diagnostics (§12.6), and a native failure always remains OPEN.

### 9.5 Withdrawn or qualified v2 statements

- "exact decision; time cost only" (v2:1311) is qualified to "release scenario, source-level design; subject to
  O-NATIVE, transport stack copies and physical resources".
- "After D1, native code accepts every length" (v2:1455) is withdrawn.
- "the same place the original … failed" (v2:1322-1323) is withdrawn (V2-F13).
- "Fewer per-iteration invariants" as a D2 mitigation (v2:1333-1335) is withdrawn. Original checked assertions are
  never deleted merely because a static proof closes.
- "No other exit exists after allocation" (v2:1087-1089) is withdrawn (§7.1).

## 10. OPERATOR DECISION PACKAGE OD-1: public helpers `Exact_Value`, `Amount`, `Sum` (V2-RC3, R-OD1)

**Obligation.** These public functions return `Valid_Big_Integer`, and their Posts equal the full signed references
(`core/resource_run_ledger.ads:185-213`).

- With the GNAT 16.1.0 runtime they cannot represent results of 2^6432 or more [K-07, K-08].
- In the release body, `Exact_Value` raises on valid spans of 804 or more bytes (V2-F13).
- The checks build fails earlier, at any checked evaluation reaching the limit.
- Release-path unreachability satisfies none of this.
- **No option is selected. The lead makes no recommendation.**

| Option | Owner | What it is | Exact consequences | Evidence it requires | What stays OPEN |
|---|---|---|---|---|---|
| E (no decision) | — | nothing changes | O-HELPERS OPEN | — | everything |
| (o) MSB-first Horner with leading-zero skipping in the `Exact_Value` body | lead (body-only) | Find the highest nonzero digit, then `Value := Value * 256 + Digit` downward. Intermediate values never exceed the final magnitude | **Release-executable mitigation only.** Padded valid spans no longer raise in the release body when the value is below 2^6432. In the checks build, the unchanged Post `Exact_Value'Result = Q.Value (Data, Item)` (`:186`) still runs `Prefix_Value_Worker`. That advances `Place` and evaluates `Prefix_Reference` and `Power_Reference` through **every** column (`core/resource_quantities.adb:147-203`), so padded spans of at least 804 bytes still fail there. Values of at least 2^6432 fail in both builds | proof of the new body against the unchanged Post; the new body's own checked invariant costs; both-build controls at 803, 804 and 1000 padded bytes and at 2^6432 ± 1, each recorded with its build | O-HELPERS (representation), D2 |
| (i-a) WORLDLINE-owned `SPARK.Big_Integers` | operator | replace `core/spark-big_integers.ads:9-11`, today a rename of `Ada.Numerics.Big_Numbers.Big_Integers`, with an unbounded WORLDLINE implementation | **Model binding.** gnat2why's runtime-unit table names both `ADA_NUMERICS_BIG_NUMBERS_BIG_INTEGERS` and `SPARK_BIG_INTEGERS` [OBS strings]. If a replacement is bound to the mathematical model by name, its executable correspondence is *assumed*: a new trust exception, contrary to `HANDOFF.md:161`, unless independently verified. If it is not bound, every existing proof loses its model. **Direct users.** `Worldline.Resources` withs `Ada.Numerics.Big_Numbers.Big_Integers` directly (`core/worldline-resources.ads:2-6`), as does the pending-component copy (`pending-component/core/spark-big_integers.ads`). A SPARK-rename replacement does not reach them; they must migrate, with re-proof. The light library stays forbidden (`HANDOFF.md:129`) | determination of GNATprove 16.1.0's model binding; an independent full verification of the implementation, with no assumed axioms; migration and re-proof of every direct user; identical public API; full original roster and controls | costs, heap and stack, D2 |
| (i-b) separate WORLDLINE-proved bignum type | operator (API) | an owning digit vector with full SPARK proof against a ghost model | The helpers' result types change, so this is a concrete public API/caller migration. It must preserve every original executable capability, caller and accepted case. It is not the frozen profile | concrete API; caller enumeration (compiler-resolved); ABI and roster consequences; full proofs; equivalent checked functions where contracts call the helpers | costs, D2 |
| (ii) rebuilt GNAT runtime | operator (toolchain identity) | patch `System.Generic_Bignums` and `System.Shared_Bignums`, rebuild the runtime from the GCC 16.1.0 sources, relink the encapsulated `libworldline_core` (`core/worldline_core.gpr:81`) | **Not "only allocation can fail" as v2 claimed.** Required: (1) the record layout `Bignum_Data (Len : Length)` with representation clause `Len at 0 range 0 .. 23; Neg at 3 range 0 .. 7` (`RT/s-shabig.ads:58-70`), plus the `Length` subtype (`:46`) and the `Digit_Vector` index (`:55`); (2) every base, index and length expression, for example `X.Len + Y.Len` (`RT/s-genbig.adb:580`), shift lengths (`:423, :456`), `Normalize` (`:1178-1195`), `Big_Exp`'s limit (`:303-332`), `To_Bignum`; (3) automatic digit vectors on the primary stack proportional to operand size: `Sum` (`:135`), `Diff` (`:177`), `Result` (`:364, :388, :423, :456, :580, :778`). Removing the limit turns them into stack-exhaustion failures unless they are rewritten; (4) quadratic `Big_Mul` and `Div_Rem` time; (5) the full checked costs of F29 and §9.3, now unbounded by representation; (6) any compiler-front-end dependence on the bignum layout (for example overflow mode ELIMINATED) audited | patch specification and diff; a GPT-6.1 review; a proof-model refinement argument for the patched operations; reproducible rebuild recipe, runtime, relink and loaded identities; both-build boundary controls on `Exact_Value`, `Amount` and `Sum`; the complete original roster on the new identity; cost measurements without caps; explicit operator approval of the identity change, which is not acceptance. The header records GPL with the Runtime Library Exception (`RT/s-genbig.adb:11-25`); no legal determination is made here | heap and stack exhaustion, time, D2 cost |
| (iii) Ghost-only retirement or removal of the helpers | — | — | **Incompatible.** It removes the original executable value-returning capability. It is a requirement change, not an eligible closure, even with operator approval (R-OD1) | — | — |
| (iii') executable successor API added alongside | operator (API) | new executable digit-wise functions; the originals remain executable | Closes nothing by itself. The originals keep O-HELPERS | every original capability and accepted case preserved; separate review | O-HELPERS |

## 11. OPERATOR DECISION PACKAGE OD-2: Python decimal-integer correspondence (V2-RC4, R-OD2)

No setting or code was changed. No WORLDLINE module was imported. **No option is selected.**

### 11.1 Facts

- The conversion surface is in Appendix A:
  - 192 JSON sites (122 PROD-RUNTIME, 2 INLINE-CHILD, 10 PROD-PROTECTED, 25 ORIGINAL-CONTROL, 3 BUILD-TOOL,
    30 INSTALL-RELEASE-SCRIPT) [K-57];
  - the AST candidate universe of non-JSON decimal conversions.
- Python's admitted configurations are limit 0 or any limit of at least 640. Values from 1 to 639 are refused at
  runtime and fatal at startup (F25). The default is 4300.
- `parse_canonical` decodes with `json.loads(data.decode("utf-8", "strict"))` (`runtime/worldline/canonical.py:54`). It
  catches only `UnicodeDecodeError`/`JSONDecodeError` (`:55`). A too-long integer raises an uncaught `ValueError`.
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
- Every such outcome is an OPEN failure, never an accepted refusal. A finite higher limit, catch-and-refuse, or a native
  size cap would not close the obligation.

### 11.3 E1: interpreter-wide unlimited (`int_max_str_digits = 0`) with exact process-class coverage

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
| C10 install/release scripts | `scripts/*.py` run by `install.sh` (for example `preflight.py`, which parses prepared transactions at `:125`) | re-executed | for each script that parses WORLDLINE data: `sys.set_int_max_str_digits(0)` at start, or a reviewed demonstration that its integers are bounded | — |
| C11 native embedding | `native/examiner_guard.c` is a CPython extension; it reads configuration (`:1958`) and starts no interpreter (no `Py_Initialize` found) | inherits from its host | none | — |

E1 consequences:

- The guard is removed for all conversions in covered processes, including untrusted local requests, peers and
  examiner reports.
- CPython 3.14 converts large values superlinearly (`/usr/lib/python3.14/_pylong.py:1-13`).
- Cost evidence must meet the original target without a new cap or refusal (O-PY-COST).
- Every touched pinned file needs pin regeneration.

E1 evidence:

- a per-class startup observation that `sys.get_int_max_str_digits() == 0` before the first relevant conversion, for
  C1, each C4 helper kind, C8 and C10;
- a C6 observation that the examiner sees the original default;
- the PY controls (§12.5).

### 11.4 E2: scoped codec, with the interpreter limit kept

**11.4.1 Parse.** At each site, add `parse_int=decimal_int` and preserve every existing keyword (Appendix A.2).

- For `canonical.py:54` the exact expression becomes
  `json.loads(data.decode("utf-8", "strict"), parse_int=decimal_int)`.
- `decimal_int (s)` receives the scanner-validated literal `-?(0|[1-9][0-9]*)`. The C scanner passes the whole digit
  string when `parse_int` is not `int` (F9).
- It splits the digits into chunks of **at most 640**. 640 is the minimum admitted limit, so each `int(chunk)` is legal
  under every admitted configuration (0 or ≥ 640; F25). This replaces v2's 4000-digit premise [K-44].
- Example: a 4301-digit literal [K-43] gives six 640-digit chunks and one 461-digit chunk [K-45].
- It recombines by divide-and-conquer, `value = high * 10**len(low) + low`, using only integer arithmetic, which has no
  limit.
- It restores the sign. `"-0"` gives 0, exactly as `int` does, so canonical re-encoding still refuses `"-0"`
  (`canonical.py:58`).
- Requirement: `decimal_int (s) == int (s)` for every s where `int` succeeds. That is proved by construction and
  review, then controlled by differential tests.

**11.4.2 Serialize.** Replace `json.dumps(value, **settings)` with `codec_dumps(value, **settings)`.

- Each distinct settings combination of Appendix A.2 must be reproduced byte-for-byte. The combinations include
  `indent=2`, `ensure_ascii=True/False`, `sort_keys`, `separators` and `allow_nan`.
- Integers, including integer dict keys, are formatted by divide-and-conquer `divmod` by `10**(640·2^j)`. Each chunk
  is converted with `str()` on at most 640 digits and zero-padded.
- Every other value class is serialized exactly as `json` does. Two sub-options:
  - **E2-a:** reuse CPython's pure-Python `json.encoder._make_iterencode` with its `_intstr` hook. It is a private API,
    pinned to CPython 3.14.7, and the C-encoder and Python-encoder outputs must be shown identical.
  - **E2-b:** a complete WORLDLINE encoder covering string escaping for both `ensure_ascii` modes, separators, indent,
    `sort_keys` by code point, `allow_nan` and recursion behaviour.
- Existing failure classes are preserved: `_validate` still runs first in `canonical_bytes`; `RecursionError`,
  `TypeError` and circular-reference behaviour stay as they are.
- Finite byte-differential tests inside the old limit are controls. They do not prove an unbounded encoder. The
  correspondence argument is by construction plus review.

**11.4.3 Sites.**

- Every PROD-RUNTIME, PROD-PROTECTED, BUILD-TOOL and INSTALL-RELEASE-SCRIPT site moves to the codec, or carries a
  reviewed data-flow demonstration that its integers stay below 10**640.
- The demonstration is an audit result about where a value comes from: for example `time.monotonic_ns()` durations
  in `simulation.py:30`'s child source. It is never a cap.
- INLINE-CHILD sources must inline the codec text, because trusted helpers import the standard library only
  (`trusted.py:31-33`), or carry such a demonstration.
- ORIGINAL-CONTROL files stay byte-identical.
- PR sites are not excluded. The daemon request parse, the client response parse and CLI output are covered.
- Protected sites under C8 custody need operator re-provisioning of approved sources.

**11.4.4 Non-JSON conversions (O-PY-AUDIT).** The universe is Appendix A.3.

- Criterion: each candidate whose operand can be a workload-derived `int` either routes through `decimal_str` /
  `decimal_int`, or carries a demonstrated bound below 10**640.
- Categories include `int(str)`, `str(int)`, f-string fields, `%`-format, `repr`, `format`, lazy logging and
  `str.format`.
- The classification is OPEN. No site is excluded by module role.

E2 consequences:

- The interpreter's guard remains for unrouted conversions, so DoS protection is retained there.
- Correctness depends on audit completeness.
- More pinned code needs review.
- The protected-custody changes are operator-owned.

E2 evidence:

- codec correctness by construction and review;
- differential tests for every settings combination, at the lowest legal limit 640, at the default 4300 and at 0;
- the audit report;
- PY controls;
- cost measurements without caps.

### 11.5 Rejected

| Rejected item | Reason |
|---|---|
| Per-call toggling of the limit | a race: the setting is per interpreter and the daemon is multithreaded (`runtime/worldline/evaluation_terminal.py:19`) |
| A finite higher limit | not closure |
| A new size cap or "size admission" presented as a cost repair (v2:1408-1410) | withdrawn |
| Catching `ValueError` as a refusal | turns a required success into a refusal |

## 12. Controls: complete fixtures and source-to-control coverage map (V2-RC5)

### 12.0 Rules for every control

- Every control is new and additive. Original controls stay byte-identical: `tests/test_resource_run_ledger_v1.py`,
  `tests/test_finalization_kernel.py`, `artifact-tests/test_canonical_artifacts.adb` and the 52-action ordinary roster.
- **All controls are unrun.**
- Each control runs in both builds.
- Expected values are **reference-evaluated**: each status is derived by walking the whole `Decision_Reference` or
  `Contained_Reference` in priority order. Arithmetic is JACKAL (§15).
- "Pre-D1" columns are source deductions, not observations.
- A checks-build failure is recorded as OPEN (D2), never as a pass.

The C-export fixtures use the original test helpers `row`, `state`, `observation` and `request`
(`tests/test_resource_run_ledger_v1.py:22-49`). Defaults:

- scope `SCOPE`;
- `capacity=20`, `held=0`, `charged=0`;
- `ledger_head=b'head-<epoch>'`, `universe_head=b'universe-head'`;
- row identities derived from the row name;
- `planned_unit` present unless the state is `RESERVED`;
- `observed_usage=None`.

### 12.1 RL-1, RL-2, RL-3: padded READY at 803, 804 and 1000 bytes (V2-F17)

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
`Nonnegative_Valid` (`core/resource_reservation_transition.ads:16-19`), `Compare` (its Post), `Same_Epoch`,
`Is_Successor`, `Same_Row` and the reference sums. Padding inside the arena preserves both, so the status equals the
base fixture's status [LEAD; PO-C1]. In priority order (`core/resource_run_ledger.ads:381-443`):

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
| RL-1 (P = 803) | READY. `Place` reaches 256^803 = 2^6424, which fits: 6425 bits ≤ 6432 [K-03, K-04] | READY | READY expected. Time is impractical by F29 (~L⁴ per `Q.Value`); recorded as O-COST-MEASURE, not as a pass on time |
| RL-2 (P = 804) | code `-1` → Python `CoreUnavailable("full-ledger native transport refused")`. `Exact_Value (Before.Held_Total)` reaches 256^804 = 2^6432 [K-65], which needs 202 limbs [K-05, K-06] | READY | fails at the first checked `Q.Value` of a padded span, for example `Nonnegative_Valid`'s Post in `Shape` → `-1`: **OPEN (D2)** |
| RL-3 (P = 1000) | `-1` / `CoreUnavailable` | READY | **OPEN (D2)** |

### 12.2 RL-4 to RL-7: large and selection fixtures through the C export

| Id | Complete inputs (helpers of §12.0) | Reference walk (first deciding branch) | Expected |
|---|---|---|---|
| RL-4a | budget = `row(b'budget', amount=1, kind='IRREVERSIBLE_BUDGET', state='CHARGED', effect=True)`; hold = `row(b'hold', epoch=1, amount=2**6432-1)`; before = `state(1, charged=1, capacity=2**6432)`; after = `state(2, held=2**6432-1, charged=1, capacity=2**6432)`; before rows (budget,); proposed (budget, hold); observed (`observation(budget, 1, 'REAPED')`,); `request(before, hold)`. This is the original `:173-177` shape with new values | Shape, native roster, request, epoch (`1 → 2`) and heads pass. Conserved: before charged `1 = 1`; proposed held 2^6432−1 and charged 1. Contained: no parents; every target `0 ≤ amount`. Capacity: `(2^6432-1) + 1 - 2^6432 = 0` [K-33], not exceeded. Reserve checks pass | **READY** post-D1 release; pre-D1 `-1` (sum ≥ 2^6432); checks OPEN |
| RL-4b | as RL-4a, with the budget amount and both charged totals equal to 2 | Capacity: `(2^6432-1) + 2 - 2^6432 = 1 > 0` [K-34] | **CAPACITY_EXCEEDED** post-D1; pre-D1 `-1`; checks OPEN |
| RL-5a | parent = `row(b'parent', amount=255)`; one = `row(b'one', amount=255, parent=b'parent')`; two = `row(b'two', epoch=1, amount=1, parent=b'parent')`; before = `state(1, held=255, capacity=300)`; after = `state(2, held=255, capacity=300)`; before rows (parent, one); proposed (parent, one, two); observed (`observation(parent,1)`, `observation(one,1)`); `request(before, two)` | Conserved: only root Held rows count (`Included` with absent parent), so `255 = 255`. Contained(before) holds. Contained(proposed): target `b'parent'` has children `255 + 1 - 255 = 1 > 0` [K-36]. At column 0 the L side holds 256: digit 0, carry 1; the target digit is 255. The residual carry decides (LA-5) | **PARENT_INVALID** in every build (values are small) |
| RL-5b | as RL-5a, with parent amount 256 and both held totals 256 | Contained: `255 + 1 - 256 = 0` [K-37] (equal carries; State Equal). Capacity: `256 + 0 - 300 = -44` [K-62]. Reserve checks pass | **READY** |
| RL-6 | r1 = `row(b'r1', amount=2**6432-1)`; r2 = `row(b'r2', amount=2**6432-1)`; r3 = `row(b'r3', epoch=1, amount=2**6432-1)`; before = `state(1, held=2*(2**6432-1), capacity=3*2**6432-3)`; after = `state(2, held=3*2**6432-3, capacity=3*2**6432-3)`; before rows (r1, r2); proposed (r1, r2, r3); observed (`observation(r1,1)`, `observation(r2,1)`); `request(before, r3)` | Conserved: `2(2^6432-1) - (2^6432-1) - (2^6432-1) = 0` [K-68] and `3(2^6432-1) - (3·2^6432-3) = 0` [K-35]. Capacity: total equals capacity, not exceeded | **READY** post-D1; pre-D1 `-1`; checks OPEN |
| RL-7a | h1 = `replace(row(b'h1', amount=5, state='RUNNING', effect=True), observed_usage=7)`; r1 = `row(b'r1', amount=9, state='RELEASED')`; n1 = `row(b'n1', epoch=1, amount=3)`; before = `state(1, held=7)`; after = `state(2, held=10)`; before rows (h1, r1); proposed (h1, r1, n1); observed (`observation(h1,1,'LIVE')`, `observation(r1,1,'REAPED')`); `request(before, n1)` | h1 contributes usage: `7 - 5 = 2 > 0` [K-69]. r1 is released, so not counted. Before held `7`; proposed `7 + 3 - 10 = 0` [K-70]. Capacity `10 - 20 < 0` [K-21] | **READY** |
| RL-7b | as RL-7a, with proposed held 8 (the amount-based sum) | proposed Σ = 10, and `5 + 3 - 10 = -2 ≠ 0` [K-71] | **CONSERVATION_MISMATCH** |
| RL-7c | b1 = `replace(row(b'b1', amount=5, kind='IRREVERSIBLE_BUDGET', state='CHARGED', effect=True), observed_usage=7)`; n1 as RL-7a; before = `state(1, charged=5)`; after = `state(2, held=3, charged=5)`; observed (`observation(b1,1,'REAPED')`,); `request(before, n1)`; variant: both charged totals 7 | Budget rows never use usage (`Amount_Reference`'s Held test), so charged `5 = 5`. Capacity `3 + 5 - 20 = -12` [K-73]. Variant: `7 - 5 = 2 ≠ 0` [K-69] | **READY**; variant **CONSERVATION_MISMATCH** |

### 12.3 Direct Ada controls for `Contained` (public; signed, invalid and duplicate domains unreachable through the C export)

These are new Ada test programs. `Data` is a `Q.Byte_Array` with the non-default lower bound 17, as in the original
builder `artifact-tests/test_canonical_artifacts.adb:11-17`. `Rows` uses a non-default first index (5) where marked.

Fields `Contained` does not read are absent or default: Scope, the Binding fields other than `Reservation`, the units
and the epochs. Quantities are written as (sign, bytes). **INVALID** means a span with `First = Data'Last` and
`Length = 2`, which is invalid because `2 > Data'Last - First + 1`. Identities are byte strings in `Data`.

| Id | Rows, in order | Reference walk (`Contained_Reference`, every target) | Expected (reference) | Discriminates |
|---|---|---|---|---|
| RL-11 | R1: Held, Reserved, reservation `r`, parent absent, Amount (−,[01]) | loop 1 vacuous. Target `r`: Σ = 0, and `0 - (0-1) = 1 > 0` [K-28] | **False** | the reviewer's counter-example (unsigned-only comparator) |
| **RL-12** | R1 parent P: Held, Reserved, reservation `p`, parent absent, Amount (+,[03]). R2 child C: Held, Reserved, reservation `c`, parent `p`, Amount **INVALID**, usage present (+,[05]) | loop 1: `Parent_Supports (R1, R2)` holds (same id, same kind, both counted, R1 not Charged, no effect). Target `p`: C is counted Held and `Value(usage) = 5 > Value(INVALID) = 0`, so the reference selects usage; `5 - 3 = 2 > 0` [K-25] fails. Target `c`: no children, `0 - 0 = 0` [K-27] | **False** | **v1 selector:** `Compare (valid, invalid) = Invalid`, so it selects Amount (value 0); target `p` gives `0 - 3 = -3 ≤ 0` [K-26]; target `c` holds; the whole result is **True**. Reference False against v1 True |
| **RL-12N** | R1: Held, Reserved, reservation `p`, parent absent, Amount (−,[01]). R2: Held, Reserved, reservation `p` (**duplicate identity**, admitted by `Contained`), parent `p`, Amount (−,[03]), usage present **INVALID** | loop 1: R1 supports R2. Target `p` (from R1 or R2; the same sum): R2 contributes `max(0, −3) = 0` (usage, value 0, is greater), so `0 - (0-1) = 1 > 0` [K-28] fails | **False** | **v1:** selects Amount −3. Target from R1: `-3 - (0-1) = -2 ≤ 0` [K-29]. Target from R2: `-3 - (0-3) = 0 ≤ 0` [K-30]. Whole result **True**. This is the negative-operand selector case, kept separately |
| RL-13 | R1: target, reservation `z`, Amount (−, Length 0). R2: as R1 but Amount (−,[00,00]). R3: Held child of `z`, Amount (+, Length 0) | every target's Σ is 0 and every value is 0 | **True** | negative zero, padding, empty |
| **RL-14** | R1: Held, reservation `p`, parent absent, Amount (−,[05]). R2: Held, reservation `c` (distinct), parent `p`, Amount (−,[05]) | Target `p`: `(0-5) - (0-5) = 0` [K-32] holds. Target `c`: no children, `0 - (0-5) = 5 > 0` [K-31] fails | **False** (v2 said True: corrected) | the child target matters |
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
| RL-10 | `Exact_Value`, `Amount`, `Sum` called directly on valid 804-byte padded spans and on values of 2^6432 | — | records the **OPEN** O-HELPERS failure. **Not** a passing control until OD-1 is decided | O-HELPERS |

The `Parent_Supports` effect/cgroup conjunct and the earlier-parent order are covered by the original control
`test_parent_must_exist_earlier_and_actual_cgroup_must_be_contained` (`tests/test_resource_run_ledger_v1.py:153-164`).

### 12.4 `Integer_Matches` controls

Direct Ada through the public `Tagged_Matches (A, JSON_Span, Tagged_Span)`, with A built at lower bound 17. Tagged
text is `["int",<sign>,"<base64 LE magnitude>"]`, as produced by `value_bytes` (`runtime/worldline/evaluation_terminal.py:81-83`).

| Id | JSON text / tagged magnitude | Path exercised | Expected |
|---|---|---|---|
| IM-1 | `"1"` followed by 1936 zeros, with its minimal magnitude | match; `10**1936 < 2**6432` [K-07] | True (pre and post) |
| IM-2 | decimal of 2^6432 (1937 digits [K-09]) and its 805-byte magnitude; also `10**1937 - 1` | match beyond the old limit | True post-D1; pre-D1 `Storage_Error` → 255 / `Invalid_Request` |
| IM-3 | `"1"` followed by 1937 zeros (1938 digits [K-10]) | match | True post-D1 |
| IM-4 | `"1"` followed by 5000 zeros (5001 digits, 701 beyond the Python default [K-74]; the text is a literal, not converted from `int`); also with the magnitude of `10**5000 + 1` | match; bottom-cell mismatch (difference 1 [K-75]) | True / False (direct Ada only; the export form needs OD-2) |
| IM-5 | decimal 2^6432 against the magnitude of `2**6432 - 1` (n = 804) | **overflow**: `256**804 = 2**6432` [K-65], so the decimal reaches `256**n`; difference 1 [K-66] | False |
| IM-6 | `"256"` vs `[FF]`; `"255"` vs `[FF]`; `"65535"` vs `[FF,FF]`; `"65536"` vs `[00,00,01]`; `"65536"` vs `[FF,FF]`; `"256"` vs `[00,01]`; `"257"` vs `[00,01]`; `"65535"` vs `[FE,FF]`; `"65535"` vs `[FF,FE]` | suffix overflow [K-38]; match; match [K-39]; match [K-40]; suffix overflow [K-46]; match [K-63]; bottom mismatch [K-64]; bottom mismatch [K-77]; top mismatch [K-78] | False; True; True; True; False; True; False; False; False |
| IM-7 | guards: `"-5"` with tag `false`; `"5"` with tag `true`; `"0"` with `[int,true,""]`; `"1"` as `"AQA="` (`[01,00]`, high zero byte); `"0"` with `"AA=="`; `"7"` with an empty magnitude; base64 errors: a length not divisible by 4, a non-alphabet byte, a misplaced `=`, nonzero pad bits (`:302-323`); sign node a string (`["int","true","AQ=="]`); a wrong tag or element count | each guard conjunct reachable through `Tagged_Matches` (`:439-445`, `:494-497`, `:302-323`) | all False |
| IM-8 | `"-"` followed by the decimal of 2^6432, with tag `true` and its magnitude | large negative match | True post-D1 |
| IM-9 | `"0"` with `[int,false,""]` | empty magnitude, zero | True |
| IM-10 | exports: the original `test_artifact_payload_integer_and_object_order_correspondence` (`tests/test_finalization_kernel.py:179-187`, plain export via `kernel.seal`) and `test_additive_finalization_collapse_requires_full_context_and_metadata` (`:257-266`, mixed export), with the payload integer replaced by ±(the decimal of 2^6432 + 7); a mismatch variant made by a raw edit of the tagged magnitude's lowest byte | producer to native | promotion True / `AUTHORIZED` post-D1 release; mismatch refused; pre-D1 255 / `INVALID_REQUEST`; checks build OPEN |

The guard conjuncts `N.Valid`, `N = Prefix (A, J, 0)`, `N.Form` and `N.After = J.Length` are always satisfied through
`Tagged_Matches` (`:478-482, :494-497`). Proof covers them (PO-B14); no public control can reach them.

### 12.5 Python controls (run only after OD-2 selects E1 or E2; under E0 they record OPEN)

| Id | Content | E1 / E2 expectation |
|---|---|---|
| PY-1 | `canonical_bytes(10**4300) == b"1" + b"0"*4300` (4301 digits [K-43]); parse round trip; a negative value; `2**20000`; `"01"`, `"-0"` and whitespace still refused; nested lists and dicts with big ints; `value_bytes` round trip | pass |
| PY-2 | E2 only: the same at limits 640 (minimum), 4300 (default) and 0; chunk boundaries at 640 and 641 digits | pass |
| PY-3 | E1 only: startup observation per process class C1, C4 (each helper kind), C8 and C10 = 0, before the first relevant conversion; C6 examiner = default | pass |
| PY-4 | E2 only: byte-differential `codec_dumps` against `json.dumps` for every Appendix A.2 settings combination, including Unicode, escapes, key order and duplicates, on values inside the old limit | identical bytes |
| PY-5 | daemon request id with 5000 digits; response echoes the id; client parse; CLI print | pass |
| PY-6 | producer-to-native finalization: positive and mismatch controls beyond 4300 digits, through both exports | promotion / `AUTHORIZED`; mismatch refused |
| PY-7 | under E0: the same inputs | recorded **OPEN** (`ValueError`), never a pass |

### 12.6 Workspace-lifetime controls (W)

| Id | Content | Expectation |
|---|---|---|
| W-1 | allocation failure injected at the Work allocation | the exception propagates; 255 (plain) / `Invalid_Request` with `finalization.decide` diagnostics; heap back to baseline. **Native failure: OPEN** |
| W-2 | checks build: an integer of at least 2^6432 raises inside ghost lockstep after allocation | CL-1 frees and re-raises; same mapping; no leak |
| W-3 | checks build: saved-copy failure (`Old_Work` on a small stack), if the harness admits it | `Storage_Error` handled as W-2, or a hard fault recorded |
| W-4 | repeated calls mixing success, mathematical False and injected failure | stable heap high-water; final water mark zero |
| W-5 | mixed export: failure injected only in the stage-1 `Decide`, then only in stage 2 | `primary-ready-rejected` against `primary-context-rejected` |
| W-6 | mathematical False (IM-5 through exports) against a native failure (W-1) | plain export: `Reason ≠ 0` against 255. Mixed export: same `Invalid_Request`, distinguished by diagnostics only |

### 12.7 Source-to-control coverage map

| Source construct (C5) | Controls | Proof |
|---|---|---|
| `Normalized` invalid → empty (§5.3) | RL-12 (invalid amount), RL-12N (invalid usage), RL-15 (invalid target) | LA-9 |
| `Usage_Selected` usage > amount / equal / Budget ignored | RL-7a, RL-12; RL-7c; an equal case `observed_usage = amount` added to RL-7a's variants | LA-9 |
| Signed operands, negative zero, padding | RL-11, RL-12N, RL-13, RL-14, RL-14P, RL-18; RL-1..3 | LA-7, LA-8 |
| Carry propagation and both-side carries | RL-5a, RL-6, RL-17a, RL-18 | LA-3, LA-6 |
| Equal carries with a different low digit; residual carry overriding State | RL-17b; RL-17a, RL-5a | LA-4, LA-5 |
| `Both_Kinds` partition | RL-22 | LA-10 |
| `Parent_Supports` conjuncts | RL-19, RL-20, RL-21, original `:153-164`, RL-12 | unchanged loop 1 |
| Null arrays and non-default bounds | RL-23, RL-18, the `Data'First = 17` builder | PO-A22 |
| Check status priority | RL-1..RL-7 walks; the original 52-action roster | PO-A19 |
| `Pair_Sum_Order` boundary | RL-4a/4b | PO-A17 |
| Column extent and zero columns | RL-15, RL-13 | LA-11, PO-A14 |
| `Prefix` integer path (`:216-234`) | original `test_canonical_artifacts.adb:36-64`; IM-7 | PO-B1 |
| `Integer_Matches` guard (`:439-445`) | IM-7, IM-9 | PO-B14 |
| `Base64` guards (`:302-323`) | IM-7 | existing |
| Decimal overflow, first and suffix digit | IM-5, IM-6 | PO-B8..B10 |
| Mismatch, top, middle and bottom | IM-6, IM-4 | PO-B12 |
| Match, large positive and negative, empty | IM-1..3, IM-8, IM-9 | PO-B11 |
| Every exit X1..X7 | W-1..W-6 | P-W1..P-W6 |
| Export stages | W-5, W-6, IM-10 | PO-N5 |
| Python classes and codec | PY-1..PY-7 | O-PY-* |
| Helpers (OD-1) | RL-10 | O-HELPERS |

## 13. Packet plan (nothing written)

| Packet | Files (exact) | Gate before writing |
|---|---|---|
| D1-A | `core/resource_run_ledger.adb` only (§5). The spec and `resource_quantities.*` stay byte-identical | GPT-6.1 review of this design; probes P-X3 and P-R1 |
| D1-B | `core/canonical_artifacts.ads` (`Integer_Token`; the `Prefix` Post conjunct) and `core/canonical_artifacts.adb` (context `with Ada.Unchecked_Deallocation; with Resource_Quantities;`; the `Prefix` invariant; the `Binary_At` Post; §6 entities; `Integer_Matches`) | design review, then probes P-W1..P-W5 and P-X3 in the reviewed scratch frame |
| D1-M | `runtime/worldline/proof_manifest.py`: **append** `REQUIRED_PROVED` names, never reorder or remove; `CONTRACT_PINS` only through the official generator; raw pins in `resource-run-ledger-source-controls-v1.json`; `proof-manifest.json` untouched (historical) | after D1-A and D1-B source review |
| D1-C | new files only: Ada programs for RL-10..RL-23 and IM-1..IM-9; `tests/test_resource_run_ledger_bigint_v3.py` (RL-1..RL-7); `tests/test_canonical_integer_bigint_v3.py` (IM-10); W controls in a scratch harness; additive enrollment with the original roster unchanged | after D1-A and D1-B |
| OD-1 | option-specific | operator decision |
| OD-2 | the E1 class table (§11.3) or the E2 site and audit set (§11.4, Appendix A), plus PY controls | operator decision |

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
| O-A | Full Algorithm A equivalence (PO-A0..A24) on the original signed and invalid domain, every target |
| O-CHECK | Capacity-branch equivalence and unchanged status priority (PO-A17, PO-A19) |
| O-BOUNDS | Installed 128-bit acceptance; every RTE and termination obligation |
| O-B | Lockstep correspondence, overflow theorem, frames, sizing (PO-B1..B21) |
| O-PREFIX-PROOF | D-B-PREFIX proof and checked cost; or PFX-2/3/5 with their probes |
| O-LEGALITY-PROBE | P-W1..P-W5, P-X3, P-R1, P-PFX* on GNATprove 16.1.0 |
| O-EXCEPTION-CLEANUP | Reclamation on X2..X4 under native fault injection (P-W6) |
| O-WORKSPACE | Heap (CL-1) or stack (CL-2) fit for every originally successful input; resource failures never accepted |
| O-NOTICE-R1 | A-GHOST-1's `Side_Sum` notices join R-1; otherwise A-GHOST-0 |
| O-HELPERS | OD-1 |
| O-GHOST (D2) | Checked contracts, Ghost code and invariants, original and D1-added: representation limit, recursion, saved values, heap, stack, time (§9.3) |
| O-BUILD-SELECTION | Actual assertion scenario and runtime/library identity loaded |
| O-PYTHON / O-PY-AUDIT / O-PY-COST | OD-2; audit of Appendix A.3; conversion costs without caps |
| O-TRANSPORT-MAPPING | Stage-aware classification of export failures (§9.4) |
| O-COST-MEASURE | Native time, heap and stack measurements on exact identities |
| O-PROOF | Complete strict matching-source proof with floor 251, the sole boundary and the ordered roster; zero unproved, justified or assumed; every strict warning resolved |
| O-NATIVE | Compiled call closure, `-gnatG` and assembly evidence (PO-N1..N7), loaded identity |
| O-CONTROLS | Every original and additive control in both builds under existing admission; all unrun |
| O-PINS | Official pin regeneration; append-only roster |
| O-JACKAL-SYMBOLIC | Universal facts are SPARK obligations; JACKAL supplied exact instances only |
| O-FINAL | Independent source, proof, native and integrated Phase One acceptance; none granted here |

## 15. JACKAL evidence (verbatim `parsed=` and `exact=`)

All results come from `mcp__jackal__jackal_exact`, called in this drafting session. Every result carries:

- `status=exact`, `formal=false`, `lane=rat`;
- assurance "exact rational arithmetic (not yet checker-covered)";
- evaluator_sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`.

No `consequence_ceiling` field was returned. This design draws no conclusion stronger than informational: exact
arithmetic is informational about code. No refusal occurred. The JSONL ledger is recall, not evidence, and is not
cited.

| Id | parsed= | exact= | Use |
|---|---|---|---|
| K-01 | `32*(200+1)` | `6432` | bits in 201 limbs |
| K-02 | `32*(200+1)/8` | `804` | bytes in 201 limbs |
| K-03 | `8*803+1-32*200` | `25` | 6425 bits exceed 200 limbs |
| K-04 | `32*201-(8*803+1)` | `7` | 6425 bits fit 201 limbs |
| K-05 | `8*804+1-32*201` | `1` | 6433 bits exceed 201 limbs |
| K-06 | `32*202-(8*804+1)` | `31` | 6433 bits fit 202 limbs |
| K-07 | `2^6432-10^1936` | positive integer (begins `67854160659933622185`, ends `7041591296`) | `10**1936 < 2**6432` |
| K-08 | `10^1937-2^6432` | positive integer (begins `83214583934006637781`, ends `2958408704`) | `2**6432 < 10**1937` |
| K-09 | `1936+1` | `1937` | digits of 2^6432 |
| K-10 | `1937+1` | `1938` | first all-failing digit count |
| K-11 | `2^63-1` | `9223372036854775807` | `Byte_Count'Last` |
| K-12 | `256*(2^63-1+1)-2^71` | `0` | column bound equals 2^71 |
| K-13 | `2^127-1-2^71` | `170141183460469229370504062281061498879` | 128-bit margin |
| K-14 | `2^71-(2^63-1)` | `2351959869397967831041` | 64 bits insufficient |
| K-15 | `10*255+9-(9*256+255)` | `0` | Multiply_Add carry ≤ 9 |
| K-16 | `10*255+9` | `2559` | Multiply_Add column maximum |
| K-17 | `3*255+2-(2*256+255)` | `0` | Pair carry ≤ 2 |
| K-18 | `2^63-3-(4*(2^61-1)+1)` | `0` | `floor((2^63-3)/4) = 2^61-1` |
| K-19 | `3*(2^61-1)` | `6917529027641081853` | maximum `B.Length` |
| K-20 | `2^63-1-3*(2^61-1)` | `2305843009213693954` | allocation-size headroom |
| K-21 | `10+0-20` | `-10` | RL-1 capacity; RL-7a capacity |
| K-22 | `10-10` | `0` | RL-1 Conserved |
| K-23 | `0+0-10` | `-10` | RL-1 Contained |
| K-24 | `1-(0+1)` | `0` | RL-1 epoch successor |
| K-25 | `5-3` | `2` | RL-12 reference |
| K-26 | `0-3` | `-3` | RL-12 v1 |
| K-27 | `0-0` | `0` | RL-12 child target |
| K-28 | `0-(0-1)` | `1` | RL-11; RL-12N reference |
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
| K-39 | `255+255*256-65535` | `0` | IM-6 |
| K-40 | `0+0*256+1*256^2-65536` | `0` | IM-6 |
| K-41 | `122+2` | `124` | runtime JSON sites with inline sources (observed counts) |
| K-42 | `124+22+11+2+3+30` | `192` | all JSON sites (observed counts) |
| K-43 | `4300+1` | `4301` | first digit count beyond the default limit |
| K-44 | `4000-640` | `3360` | a 4000-digit chunk exceeds the minimum legal limit |
| K-45 | `6*640+461-4301` | `0` | 4301 digits in chunks of at most 640 |
| K-46 | `65536-256^2` | `0` | IM-6 suffix overflow at n = 2 |
| K-47 | `22+11+2+3+30` | `68` | JSON sites outside `runtime/` |
| K-48 | `10*(256-1)+9-(256*10-1)` | `0` | instance of `10(P-1)+9 = 10P-1` at P = 256 (the universal form is a proof obligation) |
| K-49 | `63*4+(63-15)/16` | `255` | `Binary_At` case 0 maximum |
| K-50 | `15*16+(63-3)/4` | `255` | `Binary_At` case 1 maximum |
| K-51 | `3*64+63` | `255` | `Binary_At` case 2 maximum |
| K-52 | `2^63+255*2^63-256*2^63` | `0` | column bound attained at the ceiling |
| K-53 | `256-(10*0+9)` | `247` | historical: v2's sentinel absorption; not relied on in v3 |
| K-54 | `256*2^63-2^71` | `0` | 2^71 bound |
| K-55 | `5+2+2+1` | `10` | PROD-PROTECTED sites (observed counts) |
| K-56 | `6+9+1+5+2+2` | `25` | ORIGINAL-CONTROL sites (observed counts) |
| K-57 | `122+2+10+25+3+30` | `192` | scope partition total |
| K-58 | `255+255-(1*256+254)` | `0` | RL-17a and RL-18 column split |
| K-59 | `255+255-255` | `255` | RL-17a |
| K-60 | `255+255-255-255-0` | `0` | RL-18 |
| K-61 | `3+3-5` | `1` | RL-22 |
| K-62 | `256-300` | `-44` | RL-5b capacity |
| K-63 | `0+1*256-256` | `0` | IM-6 `"256"` vs `[00,01]` |
| K-64 | `257-(0+1*256)` | `1` | IM-6 `"257"` vs `[00,01]` |
| K-65 | `256^804-2^6432` | `0` | `256**804 = 2**6432` |
| K-66 | `2^6432-(2^6432-1)` | `1` | IM-5 |
| K-67 | `255+0-300` | `-45` | RL-5a capacity |
| K-68 | `2*(2^6432-1)-(2^6432-1)-(2^6432-1)` | `0` | RL-6 before |
| K-69 | `7-5` | `2` | RL-7a; RL-7c variant |
| K-70 | `7+3-10` | `0` | RL-7a proposed |
| K-71 | `5+3-10` | `-2` | RL-7b |
| K-72 | `1-2` | `-1` | RL-17b |
| K-73 | `3+5-20` | `-12` | RL-7c capacity |
| K-74 | `5000+1-4300` | `701` | IM-4 digits beyond the default limit |
| K-75 | `10^5000+1-10^5000` | `1` | IM-4 mismatch |
| K-76 | `65535-(254+255*256)-(65535-(255+254*256))` | `-255` | computed, not relied on |
| K-77 | `65535-(254+255*256)` | `1` | IM-6 bottom mismatch |
| K-78 | `65535-(255+254*256)` | `256` | IM-6 top mismatch |

Verbatim non_claims returned with every result:

- "NOT formal-bounded: this lane carries no Lean-checked certificate"
- "The epistemic class above is the STRONGEST claim this result supports"
- "exact rational arithmetic (not yet checker-covered)"

Universal statements about all n, all rows and all carries are SPARK proof obligations (§8). JACKAL supplied exact
instances and constants only. Counts read from files or scans are observations; only their sums went to JACKAL.

## 16. Non-claims

- No source, proof, native, test, review or Phase One acceptance is claimed. `proof_acceptance`, `source_acceptance`
  and `phase_acceptance` are false.
- No compiler, prover, build, test, WORLDLINE code, systemctl, project-vault or restic command was run. No WORLDLINE
  module was imported.
- Installed binary strings, examples and guide text are not legality evidence for this candidate. Every legality
  question is a named probe.
- The Python observations are of this agent's interpreter only.
- The cost orders are lead estimates, not measurements or bounds.
- No operator option is selected or recommended. Operator approval would not be acceptance evidence.
- Resource failures of any kind (heap, stack, time) are never accepted refusals. They remain OPEN native obligations.

_End of DESIGN v3._
