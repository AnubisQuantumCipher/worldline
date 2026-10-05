# WORLDLINE Phase One C-API boundary consolidation DESIGN v6 — independent review

**Verdict: ENDORSED.** Required design changes: none.

**Reviewer:** actual model selection `gpt-6.1-sol`; different from the author; authored nothing under review. **Author:** Claude Code lead `claude-opus-5-5` through a drafting subagent. **Review date:** 2026-10-05.

This is a design verdict only. `CLOSED_AT_DESIGN_LEVEL` means that the specified invariant and enforcement sketch address the identified design defect. It gives no source, proof, phase, control-run, installed-legality, native-correspondence or production acceptance. `source_acceptance=false`, `proof_acceptance=false`, `phase_acceptance=false`. The fixed Phase One guarantee and every outstanding implementation/evidence obligation remain in force.

## Scope, method and identities

Path keys used in file:line evidence:

- **W:** /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow
- **WT:** /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1
- **D6:** /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v6
- **D5, D4, D3:** the corresponding `claude-capi-boundary-design-v5`, `-v4`, `-v3` directories under WT/designs.
- **S5:** W/work/claude-composition-v5-beta/source.
- **S4:** W/work/reviewed-common-proof-source-composition-v4/source.
- **H:** W/outputs/claude-phase1-handoff-20261004.
- **P:** /home/sicarii/Documents/complete-phase1-prompt.txt.
- **RW draft:** W/work/protected-original-root-worker-repair-v1/source.
- **Seam v2 sealed review:** WT/designs/claude-root-worker-seam-design-v2/review/gpt61-v1.

The review used passive file reads, hashes, inert Python AST parsing and literal extraction. Neither WORLDLINE nor the design check sketch was imported or executed. No compiler, prover, build, test, service, vault, restic, window or reservation action was performed. No process or tool was stopped, killed or interrupted. No SIA note was written. Neither the forbidden SIA store nor the in-progress seam v3 review was read or listed. No author/lead transcript was read. Only the requested review artifacts and item checkpoints were written, create-only, in this review directory.

The B8 reconstructions were text transformations followed by `ast.parse`. Source-manifest inspection interpreted only literal assignments, ordered list appends and dictionary updates; it invoked no WORLDLINE definition. The author simulation is not used as evidence. The exact audit observations, input hashes, quote comparisons, inert diff and JACKAL results are retained in checks.json.

| Input | Computed sha256 | Supplied identity |
|---|---|---|
| D6/DESIGN.md | `cfa0dca9e275e878b958f2f8da6b5cf54824534867773382965f2a887e98a417` | MATCH |
| D6/APPENDIX-BINDINGS.md | `9f9f3dfa897d0c320226df39c89bc5c156fc87ebc3e24959ab0c08bba5db1946` | MATCH |
| D6/decisions.json | `357bb2d429a7f6e039af53f95ad7a67c58a34587dac55fcdda6fcdacfc828d2b` | MATCH |
| D6/jackal.json | `34a7a3ab2c27552e94ce8a114119e4b14988bd03fafe3747b0bc3fec274a94de` | MATCH |
| D6/AUTHOR-NOTES.md | `414fd7363ed415ce5dd5c2f1c675780bb5917e9e9a08bc5ab0751ae48ba2aa08` | MATCH |
| D4/APPENDIX-COST-MAP.md, carried | `5592df3a6330da44e60957c8754e50972b6ac0ccfbdc1a53308365e9ccc5f1a4` | MATCH |

The v5 sealed REVIEW.md, review.json, checks.json and review-freeze.json match their supplied identities. The v3/v4/v5 freeze entries also match their declared hashes, bytes and modes. A final passive re-hash matches every previously observed input identity. Details are in checks.json `sealed_previous_review_files` and `final_input_rehash`.

## 1. V5-RC4-GATE-EXCEPTION

**CLOSED_AT_DESIGN_LEVEL.** The sole assignment exception is now checked against the independent, fixed `CAPI_WFX_PROTOCOL`, rather than inferred from mutual agreement of mutable tile/gate tables.

| Sub-clause | Ruling | Independent assessment | File:line evidence |
|---|---|---|---|
| E.1 | CLOSED_AT_DESIGN_LEVEL | Fixed PK-1 CAPI_WFX_PROTOCOL; no stage updates it; CR6 compares tables against it. | D6/DESIGN.md:26; D6/APPENDIX-BINDINGS.md:64-70,327-334,399-411 |
| E.2 | CLOSED_AT_DESIGN_LEVEL | Before Finalization_Decide is in CAPI_LAYOUT_EXPORTS, CR6 requires empty exclusive keys and empty wfx roster. | D6/DESIGN.md:27; D6/APPENDIX-BINDINGS.md:65,160-163,238,402-406,279 |
| E.3 | CLOSED_AT_DESIGN_LEVEL | After relocation only exclusive key G21c; not inferred from table mutual agreement. | D6/DESIGN.md:28; D6/APPENDIX-BINDINGS.md:66,239,404-406,279 |
| E.4 | CLOSED_AT_DESIGN_LEVEL | Only wfx triple (Finalization_Decide,G21c,O); CR5 also requires fixed row id/object. | D6/DESIGN.md:29; D6/APPENDIX-BINDINGS.md:396,403-406,279 |
| E.5 | CLOSED_AT_DESIGN_LEVEL | Fixed declaration/type/no initializer, exact region digest, assignments and test independently compared; BR7 binds source text to entry. | D6/DESIGN.md:30; D6/APPENDIX-BINDINGS.md:227-241,401-409,417-422; D5/APPENDIX-BINDINGS.md:463-541; D4/APPENDIX-BINDINGS.md:686 |
| E.6 | CLOSED_AT_DESIGN_LEVEL | MX9-MX12 specify coherent added, relabelled id/object and moved amendments; protocol check must refuse. Actual execution OPEN. | D6/DESIGN.md:31; D6/APPENDIX-BINDINGS.md:279 |
| E.7 | CLOSED_AT_DESIGN_LEVEL | Unchanged PK-1/PK-5 and PK-6b/PK-7 positive control specifications adequate; actual execution OPEN. | D6/DESIGN.md:32; D6/APPENDIX-BINDINGS.md:279 |
| E.8 | CLOSED_AT_DESIGN_LEVEL | No tile, branch, diagnostic, refusal, write or accepted runtime case is changed by the named deltas. | D6/DESIGN.md:33; D6/APPENDIX-BINDINGS.md:28,241,425; D5/APPENDIX-BINDINGS.md:591-790 |
| E.9 | CLOSED_AT_DESIGN_LEVEL | CR5 at row validation plus CR6 at function level after row loop closes the arbitrary-wfx-kind exception gap. | D6/DESIGN.md:34; D6/APPENDIX-BINDINGS.md:396,399-411 |

CR5 restricts the row identity and object even inside the `wfx` branch. CR6 runs at function level after the row loop and independently checks the entire `wfx` roster, the exclusive map's keyset, declared type/no initializer, region digest, then/else assignments and final test. BR7 still binds actual unit text to the exclusive entry. Thus coherent amendments to a tile and both mutable gate tables do not create another permitted assignment exception. Evidence: D6/APPENDIX-BINDINGS.md:396,399-422; D5/APPENDIX-BINDINGS.md:463-541.

The fixed region digest was independently recomputed from D4/APPENDIX-BINDINGS.md:686, B4.20 segment 6 excluding its final test: `34b1492a5b5a757dab0cd1c62fcc241155be318e42a728da6649387d62c5b4d0`. It equals the protocol tuple at D6/APPENDIX-BINDINGS.md:327-332.

The stage indicator remains a staged table, `CAPI_LAYOUT_EXPORTS`. Its membership is bound by R-LAYOUT/R-RES. More directly, a falsely absent scope with an exception still fails the required empty roster/map; a falsely present scope requires the same sole normative exception and cannot admit an added, relabelled or moved one. Editing the fixed PK-1 constant itself is outside the declared stage updates and requires a new reviewed check-text delta. Evidence: D6/APPENDIX-BINDINGS.md:64-70,160-163,402-410.

MX9–MX12 are adequate specifications of coherent added/relabelled/moved amendments. MX13–MX17 cover early staging, altered assignment, region, declared type and test. The named protocol check must refuse, independently of other checks. Unchanged PK-1/PK-5 empty tables and PK-6b/PK-7 sole-G21c tables are specified as positive controls. These are unrun obligations; the author's in-memory results supply no control credit. Evidence: D6/APPENDIX-BINDINGS.md:279; D6/DESIGN.md:298-300.

## 2. V5-RC4-QUAL-CAPTURE

**CLOSED_AT_DESIGN_LEVEL.** The text-only rule now examines the C_API specification, C_API body and parent specification, every potentially capturing mentioned prefix, routine-named library units, and separate body stubs.

| Sub-clause | Ruling | Independent assessment | File:line evidence |
|---|---|---|---|
| Q.1 | CLOSED_AT_DESIGN_LEVEL | Rule (d1)-(d4) explicitly covers SPEC, BODY, PARENT. | D6/DESIGN.md:40; D6/APPENDIX-BINDINGS.md:86,97-101,382-388 |
| Q.2 | CLOSED_AT_DESIGN_LEVEL | CR3 scans all noninitial with-clause components for roots and every component for listed simple names; CR4 calls it on each required unit. | D6/DESIGN.md:41; D6/APPENDIX-BINDINGS.md:338-388 |
| Q.3 | CLOSED_AT_DESIGN_LEVEL | Expanded-name argument now covers ancestors mentioned through descendants, parent declarations/context/use clauses, routine-named library units and subunits. | D6/DESIGN.md:42; D6/APPENDIX-BINDINGS.md:117,125,133,140-153 |
| Q.4 | CLOSED_AT_DESIGN_LEVEL | Promise rows 42 and 44, maps and DESIGN X-R2/X-R5 agree. | D6/DESIGN.md:43,165,189; D6/APPENDIX-BINDINGS.md:177,195-197,265-267 |
| Q.5 | CLOSED_AT_DESIGN_LEVEL | decisions.json qualified_v6 reproduces all units, rules, exceptions and controls. | D6/DESIGN.md:44; D6/decisions.json:158,237,270 (closure, gates_v6, qualified_v6) |
| Q.6 | CLOSED_AT_DESIGN_LEVEL | Every potentially capturing noninitial library-unit prefix is examined; limited/private modifiers do not evade the with-token scan. | D6/DESIGN.md:45; D6/APPENDIX-BINDINGS.md:99,146-147,273,349-354 |
| Q.7 | CLOSED_AT_DESIGN_LEVEL | Text-only refusal independent of unit existence; scoped exceptions and use-clause inventory unchanged. | D6/DESIGN.md:46; D6/APPENDIX-BINDINGS.md:102,425 |
| Q.8 | CLOSED_AT_DESIGN_LEVEL | MQ15-MQ24 specify descendant/parent/routine/stub/empty-text/nested controls; actual executions OPEN. | D6/DESIGN.md:47; D6/APPENDIX-BINDINGS.md:208-220,273,338-388 |
| Q.9 | CLOSED_AT_DESIGN_LEVEL | Unchanged contexts at PK-1/PK-5/PK-6b/PK-7 plus later context additions are adequate positive-control specifications. | D6/DESIGN.md:48; D6/APPENDIX-BINDINGS.md:208-220,273 |
| Q.10 | CLOSED_AT_DESIGN_LEVEL | D-38, installed integrated name/overload resolution, child-unit capture and RM readings explicitly OPEN. | D6/DESIGN.md:49,264,289-291; D6/APPENDIX-BINDINGS.md:103,153 |
| Q.11 | CLOSED_AT_DESIGN_LEVEL | Last-selector-only omission replaced by every-prefix check, with conclusion restricted to text-level argument. | D6/DESIGN.md:50; D6/APPENDIX-BINDINGS.md:97-109,349-354; D5/APPENDIX-BINDINGS.md:202-205,384-395 |

For a dotted with-clause name, CR3 checks every component after the initial component against the roots; this covers each noninitial terminal identifier of a mentioned ancestor, as well as that of the named descendant. It checks every component against the listed routine simple names. Searching from the `with` token also covers `limited`, `private` and their combined form. A root library unit used at the initial position is not itself a competing nested declaration; that exclusion is intentional. Refusal is by spelling, independent of whether a unit exists or that context would compile. Evidence: D6/APPENDIX-BINDINGS.md:97-109,338-363.

CR4 invokes the helper on both parts of the pair and on `core/worldline.ads`. The parent's own `Worldline` name is allowed only at its package head and final end; its whole text otherwise follows d1, has no use clause, and contains no listed routine simple name. The whole-text `separate` refusal prevents an unexamined subunit context. Missing/nonisolatable parent text is not accepted. These scans do not depend on nesting depth. Evidence: D6/APPENDIX-BINDINGS.md:97-101,343-363,382-388.

The primary Ada 2022 RM corroborates the design's underlying visibility argument: with-clause scope includes the declaration's children/subunits; a descendant mention also mentions its prefixes; children belong within their parent's declarative region; an inner homograph can hide an outer declaration. These are language readings, not installed candidate resolution. [RM 10.1.2(5,6/2,7)](https://www.adaic.org/resources/add_content/standards/22rm/html/RM-10-1-2.html), [RM 10.1.1(11)](https://www.adaic.org/resources/add_content/standards/22rm/html/RM-10-1-1.html), [RM 8.3(8)](https://www.adaic.org/resources/add_content/standards/22rm/html/RM-8-3.html).

Parent context use clauses have declaration-region scope. Plain `use type` and `use all type` have distinct visibility effects; the unchanged whitelist and the parent-wide refusal remain relevant. [RM 8.4(6–8.2/3)](https://www.adaic.org/resources/add_content/standards/22rm/html/RM-8-4.html). The enclosing Standard outline was also read; this review grants no installed-name-resolution closure from it. [RM A.1](https://www.adaic.org/resources/add_content/standards/22rm/html/RM-A-1.html).

MQ15–MQ24 and the unchanged-context/later-context positive controls are adequate specifications. MQ17 is additionally refused by whole-spec S-RES; MQ22 and MQ24 are additionally refused by fixed residual checks. Those extra guards do not discharge the separately named R-QUAL obligation. Actual controls and installed integrated names/overloads, child-unit capture and RM application remain **OPEN**, as v6 expressly states. Evidence: D6/APPENDIX-BINDINGS.md:208-220,273; D6/DESIGN.md:264,289-291,300. Checkpoint 2 recorded incomplete initial web retrieval; later primary RM retrieval did not change its design verdict or close any installed obligation.

## 3. Carried RC4 obligations, R2_NINE_CONDITIONS and PACKET_PLAN

| Item | Ruling | Basis and remaining evidence gap |
|---|---|---|
| V4-RC4-GATE | CLOSED_AT_DESIGN_LEVEL | The carried v5 Boolean/case branch and completeness repairs remain; the v6 fixed sole exception closes the remaining independent-invariant gap. D5/APPENDIX-BINDINGS.md:719-790,800-841; D6/APPENDIX-BINDINGS.md:227-241,396-411. Actual controls and relevant installed/proof/native evidence remain OPEN. |
| V4-RC4-ALIAS | CLOSED_AT_DESIGN_LEVEL | Full expanded-name, scoped exception, alias and use-clause rules remain; every-mentioned-prefix/parent/subunit rules close the remaining capture gap. D5/APPENDIX-BINDINGS.md:183-234,384-395; D6/APPENDIX-BINDINGS.md:97-109,338-388. Installed resolution and real controls remain OPEN. |
| V3-RC4 | CLOSED_AT_DESIGN_LEVEL | The sealed v5 review identified these as the remaining design defects; both are now closed at that level while the full binding/pin/coverage discipline is retained. D5/review/gpt61-v1/REVIEW.md:90-96; D6/DESIGN.md:254-279. Implementation and evidence remain OPEN. |
| R2_NINE_CONDITIONS | CLOSED_AT_DESIGN_LEVEL for the mapped design/binding specification | All mapped protections remain and condition (4) now includes the repaired independent invariants. Executable reachability, actuals, resolved profiles, native symbols, proof and custody require their original evidence. D6/DESIGN.md:278; D5/APPENDIX-BINDINGS.md:800-841; D6/APPENDIX-BINDINGS.md:265-267. |
| PACKET_PLAN | CLOSED_AT_DESIGN_LEVEL | Linear lineage, immediate PK-6a enrollment/pins, separately reviewed confirming representation packets, D-13 before PK-7 and identities-only PK-S remain. D3/DESIGN.md:1870-1993; D5/DESIGN.md:219-228; D6/DESIGN.md:279; D6/APPENDIX-BINDINGS.md:160-163. Actual packet execution/qualification remains OPEN. |

The original R2 review's nine protections were reread at W/work/claude-capi-boundary-design-v2/review/gpt61-v1/REVIEW.md:174-238. The v6 mapping preserves:

| Condition | Retained design protection | Evidence |
|---|---|---|
| (1) | Complete relocation map and designated homes | D6/DESIGN.md:278; carried §6 and A-BIND B2/B3 |
| (2) | Whole-core closure plus separate component closure, canonical bindings and alternate-binding exclusions | D6/DESIGN.md:278; carried G1–G10, K1–K6 |
| (3) | Original C profiles, named subtype resolution, spec residue | D6/DESIGN.md:278; carried P1–P3 and S-RES |
| (4) | Exact ordered tiles, writes, branch gates, full-name/alias rules, glue and diagnostics | D6/DESIGN.md:278; D6/APPENDIX-BINDINGS.md:64-70,97-109,265-267 |
| (5) | Unchanged predecessor chain and assertions | D6/DESIGN.md:278; carried PP1–PP3 |
| (6) | Original effective pin keys plus complete additive source/component/control identities and immediate re-pinning | D6/DESIGN.md:278; carried §8.7; H/HANDOFF.md:153 |
| (7) | Original ordered prefix and monotonic packet-aligned suffix | D6/DESIGN.md:278,383; D3/DESIGN.md:1918-1939,2478-2589 |
| (8) | Sole boundary and full relevant semantic body proof; no new Off exemption | D6/DESIGN.md:110-118,278; H/HANDOFF.md:161 |
| (9) | Original strict command/floor, no unproved/justified/Assume or warning waiver, matching complete identity | D6/DESIGN.md:278,293-295; H/HANDOFF.md:155-164 |

Text checks are necessary guards. They do not prove reachability, faithful actuals, whole-body semantics, custody or matching native behavior. That distinction is explicit in carried B11 row 40 and v6's OPEN list. Evidence: D5/APPENDIX-BINDINGS.md:839; D6/DESIGN.md:287-313.

## 4. Carry, quotes and declared changes

**Verified.** Every bound v6 slice matches its frozen v5 bytes. Inherited v5/v4 slices were also verified against their declared ranges. The slices use the specified line bytes with final newlines; the replacement audit separately distinguishes old quotation text from metadata line hashes. A-COST remains the v4 file under its unchanged hash.

| v6 carrier | Frozen source range | Computed slice sha256 | Result |
|---|---|---|---|
| DESIGN | D5/DESIGN.md:18-49 | `7fa68bed33a1c5fe54743eaeda01d1c8ab3c67c01ded1b16d2def11b0971b32c` | MATCH |
| DESIGN | D5/DESIGN.md:53-231 | `34e0da4296a4ae67c17c6f2168149b8a54957d62e1ce66a5e7ff1d1d6ab2a711` | MATCH |
| DESIGN | D5/DESIGN.md:235-265 | `f15a3160fc962d88a1a5e7725808808f55d7d77b2bf21dfae68ab6917cca042b` | MATCH |
| DESIGN | D5/DESIGN.md:332-339 | `68487dbac9c37ce7a51b3ea95fae6d8326e8aaa6cef7b97eb579ddd3dc2af9a8` | MATCH |
| DESIGN | D5/DESIGN.md:410-412 | `ff085fcce4b4423e88c00b313b8725fd894653759fadc9c035b20cfaa7ac5392` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:17-81 | `cc2e66b1123883484777c5ae344c3c9cbecc27c63284608bb50fd07cb577afca` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:85-112 | `c1997b91b05d2d4e94897d433780f8fa03927d3a217b7a6ca87cc9a839c1962b` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:114-177 | `3bbe54bb2fbca4c5af64619066c482f3cdd14c09703b57967af14cb54c8e4302` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:179-181 | `022663b6551574958e528e9dd7092babc22a83e85188ecc6e78ceef845aa5430` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:183-234 | `5a0488a3f44e16c865149e0dedc225891e665ff3f0b61eb677dba6da4324fc42` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:238-250 | `2e1886e3b7a045daa50a20e027f1d87e8f7f63ce530a97e2663016f71026555e` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:254-270 | `096ea57f1ecaf03b46de1cd9e4e5258940af16e069ec6d416f7ed4736e376458` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:272-557 | `206f07392321e24c330914cabe7028a884951f3cbc68e079a2fedeb5edb6e98d` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:559-575 | `7a1d60eb1d926b2f725bc09f74ffbf802f46056ee0f2857a592c74f250658d07` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:577-587 | `3c4bf4f47fd96907301a61f039b948098195c6641edb520ed8056362ef13c728` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:591-715 | `2ddae1af85bbdc2696effec550c12c21e5e8a7e63c49a3e9b0349cfdbdcbda90` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:719-790 | `9c269d9894c16bccdbcd8621c5a961f06873043fb1e3d00886529583b3c51f6a` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:794-841 | `0d7daa6243f99a1c477f13a80d69fa417b1ffb7e97d1e1c49bebd51b242bcc22` | MATCH |
| A-BIND | D5/APPENDIX-BINDINGS.md:845-868 | `b63258f1af0e4ab182b7fc9c34f15a4267540458f0707c351716ce39ac11604d` | MATCH |

All X-R1–X-R8 and W-A1–W-A20 old quotations or insertion anchors match. Their machine-twin old/new hashes match the corresponding rendered line bytes. BR1–BR8 quotations/anchors match the v4 code; CR1–CR6 match the effective v5 reconstruction. The inherited R1–R15, A-R1/A-R2 and V-R1–V-R9 quotations were independently compared too; V-R9 was compared against the effective R12 replacement, rather than the raw obsolete v3 line. Evidence: D6/DESIGN.md:127-146,152-214; D6/APPENDIX-BINDINGS.md:37-51,61-279,308-425; D4/DESIGN.md:166-265; D5/DESIGN.md:138-231; D5/APPENDIX-BINDINGS.md:61-80,272-557.

The changes are exact and justified as follows:

| Changes | Purpose and assessment | File:line evidence |
|---|---|---|
| X-R1, X-R3, X-R4 | Fixed protocol declaration and the sole normative assignment exception; consistent with E.1–E.9 | D6/DESIGN.md:152-181 |
| X-R2, X-R5 | Expanded-name checks over the pair, parent and mentioned prefixes; consistent with Q.1–Q.11 | D6/DESIGN.md:160-189 |
| X-R6 | Add the repaired-invariant amendment and positive controls | D6/DESIGN.md:192-197 |
| X-R7, X-R8 | Correct nested Child_Boundary wording only | D6/DESIGN.md:200-214 |
| W-A1, W-A2 | Normative fixed exception and constant text | D6/APPENDIX-BINDINGS.md:61-78 |
| W-A3, W-A4 | Extend the rule's checked units and define d1–d4 | D6/APPENDIX-BINDINGS.md:81-109 |
| W-A5, W-A6, W-A7, W-A8 | Amend the closure argument and state all considered capture vectors with evidence limits | D6/APPENDIX-BINDINGS.md:112-153 |
| W-A9 | Keep stage updates and fixed PK-1 constants distinct | D6/APPENDIX-BINDINGS.md:156-163 |
| W-A10 | Correctly describe the effective author sketch reconstruction as a self-check | D6/APPENDIX-BINDINGS.md:166-168 |
| W-A11, W-A12, W-A13 | Align the promise/check maps with the independent invariant repairs | D6/APPENDIX-BINDINGS.md:172-197 |
| W-A14 | Bind the parent/context observations and distinguish whole-spec binding from unbound body context | D6/APPENDIX-BINDINGS.md:200-220 |
| W-A15 | Preserve every gate while fixing the exclusive exception's roster and content | D6/APPENDIX-BINDINGS.md:224-241 |
| W-A16, W-A17, W-A18 | Restate affected B11 promises and add the independent protocol/capture rows | D6/APPENDIX-BINDINGS.md:244-267 |
| W-A19, W-A20 | Specify capture and sole-exception amendment controls plus staged positives | D6/APPENDIX-BINDINGS.md:270-279 |
| CR1 | Header/comment update only | D6/APPENDIX-BINDINGS.md:319-322 |
| CR2 | Fixed protocol tuple and parent-spec path | D6/APPENDIX-BINDINGS.md:327-334 |
| CR3 | Whole-unit capture helper, all-prefix/routine-name context checks and subunit refusal | D6/APPENDIX-BINDINGS.md:338-363 |
| CR4 | Apply helper to the pair/parent and enforce parent-specific exclusions | D6/APPENDIX-BINDINGS.md:382-388 |
| CR5 | Fixed wfx row/object identity | D6/APPENDIX-BINDINGS.md:396 |
| CR6 | Independent whole-roster, keyset and normative-content validation | D6/APPENDIX-BINDINGS.md:399-411 |

The effective v5-to-v6 sketch diff contains only the declared CR edits. The inert reconstructed v6 sketch has sha256 `e0360db00ee2c2316cb2bcfc56851816575267c101f3e938daffb3cb512fc081` and parses as AST. Parsing establishes syntax of this text, not enforcement correctness or execution success.

The canonical carried JSON payloads match their declared predecessor hashes. Every field of the v5 ruling objects, including owner and evidence_required, is carried exactly by the design; the prose carry was also compared. Historical NOT_CLOSED statements remain historical records, and this review explicitly supplies the new closures. The current rulings below change only the resulting RC4-linked adjudication where appropriate. Evidence: D6/DESIGN.md:67-108,139-146,254-279; D6/decisions.json carried payloads; checks.json `canonical_json_carry`, `carried_rulings`, `prose_rulings`, `historical_v5_rulings`.

L9–L12 remain **GENUINE; REPAIRED_AT_DESIGN_LEVEL** with the prior limits. L9 retains staged removed-routine inventory and restores the full roster at PK-6b. L10 retains Boolean/case branch confinement. L11 retains the whole-use-clause whitelist. L12 retains declaration/selection acceptance completeness, as a spelling convention rather than installed type resolution. No v6 delta retracts those repairs. The sole-exception/capture gaps left by v5 are separately closed above. Evidence: D6/DESIGN.md:258; verified v5 slice :18-49; D5/APPENDIX-BINDINGS.md:559-575,719-790,845-865; D6/decisions.json `latent_v4_defects`.

## 5. L13–L16 and nested-declaration coverage

| Item | Assessment | Repair and limit | File:line evidence |
|---|---|---|---|
| L13 | GENUINE; REPAIRED_AT_DESIGN_LEVEL | The former pair-only rule omitted parent declarations/context/use visibility. d1–d3 now inspect that specification. The S5 parent has no asserted current capture; the defect is the invariant's omission. | D6/DESIGN.md:56; D6/APPENDIX-BINDINGS.md:97-109,145-149,382-388; S5/core/worldline.ads:1-9 |
| L14 | GENUINE; REPAIRED_AT_DESIGN_LEVEL | A library unit named like a listed routine can supply a direct callable spelling through a with clause. d2 refuses such names throughout mentioned prefixes on all three units. Fixed tiles remain an additional guard, not a substitute for this invariant. | D6/DESIGN.md:57; D6/APPENDIX-BINDINGS.md:99,133,148,349-354,273 |
| L15 | GENUINE; REPAIRED_AT_DESIGN_LEVEL | A body stub introduces a separately contextualized subunit outside the scan. d4 closes that omitted source-form vector. R-RES already refuses the fixed-source mutation; the new independent invariant is still needed for coherent amendments. | D6/DESIGN.md:58; D6/APPENDIX-BINDINGS.md:101,150,273,347-348 |
| L16 | GENUINE_WORDING_DEFECT; CORRECTED_AT_DESIGN_LEVEL; WORDING_ONLY | The named renamings are inside package body Child_Boundary. X-R7/X-R8 correct the description. No new current same-scope collision or semantic repair is claimed. | D6/DESIGN.md:59,205-214,319-324; RW draft/core/worldline-c_api.adb:1198-1220,2251; seam v2 sealed review/review.json:472,505-508 |

MQ24 is an adequate **control specification** for nested-declaration coverage: the defining identifier in `package Evaluation_Pending renames Evaluation_Pending_V2;` is a root occurring alone, so d1's whole-text scan encounters it even inside the nested package body. The permitted renaming-target exception concerns the target after `renames`, not the defining identifier. R-INV(ii) assigns the nested clause to its innermost scope; an undesigned Child_Boundary falls into RESIDUAL, and R-RES is another refusal. No executed MQ24 result is claimed. Evidence: D6/APPENDIX-BINDINGS.md:98,144,273,356-361; D5/APPENDIX-BINDINGS.md:559-575; D6/DESIGN.md:59.

These changes exclude omitted capturing source forms without narrowing an original runtime domain, accepted case, diagnostic, gate, assignment or write. The specified unchanged and later-stage contexts remain positive controls. Evidence: D6/APPENDIX-BINDINGS.md:28,102,273,279,425.

## 6. Decision ownership and approval gates

**Correctly labelled; no new approval gate identified.**

- **D-13:** the operator decides a concrete material component transport/library architecture choice before PK-7; the lead prepares the artifacts. Only an ABI- and scope-preserving route is admissible. Both original Decide exports, every original interface unit, exact mirror correspondence and native/body evidence remain required. No option is chosen by this review. Evidence: D6/DESIGN.md:263; D3/DESIGN.md:2252-2260; W/work/integrated-proof-preparation/PLAN.md:104-107.
- **N-06:** the operator retains protected deployment custody of native_sha256. The changed installed/loaded library needs matching source/proof/control identity and mismatch-refusal evidence. An old-library hold gives no consolidated-candidate acceptance. Evidence: D6/DESIGN.md:276; D3/DESIGN.md:2262-2271; S5/protected-resource/run_service.py:117-120.
- **N-01:** lead-owned strict obligation. A confirming clause is not a material ABI decision and must satisfy C1–C8/E1–E6. A nonconfirming material change needs the original operator decision and cannot waive the original guarantee. Evidence: D6/DESIGN.md:271; D3/DESIGN.md:2012-2052,2273.

Pinning alone creates no approval gate. Reviewed explicit deltas plus recomputed effective pins are required by H/HANDOFF.md:153; routine authorized implementation is not reassigned to the operator. Existing material API/ABI/owner-policy, custody, architecture and publication/deployment boundaries remain. The existing draft-PR authorization in P:72 and H/HANDOFF.md:165 is not rewritten here; merge/release/install/sudo/production/PRIME actions retain their applicable original authorization at P:74 and H/HANDOFF.md:166.

## 7. Fixed guarantees and other defects

**No additional required design change identified.** The v6 delta strengthens independent text invariants and specifies matching controls. It neither changes the functional tiles nor removes a relevant proof/control obligation. The effective source baseline was inspected as inert literals:

- `MINIMUM_CHECKS=251` and `UNANALYZED_BOUNDARY={"worldline-c_api"}` are retained.
- The full ordered original REQUIRED_PROVED prefix and packet-aligned append are retained; arithmetic results are reported below under JACKAL's status.
- The S5 effective CONTRACT_PINS keyset is preserved. The explicit-recovery-marker test keys are pre-existing S5 lineage additions; no S4 key was removed. Future reviewed deltas require effective re-pinning and complete additive identity protection.
- Full relevant bodies/callers, strict warnings, initialized total interfaces, exact diagnostics/branches/write sets and original accepted native domains remain mandatory.

Evidence: S5/runtime/worldline/proof_manifest.py:22-25,312-329,418,924-1029; D6/DESIGN.md:110-118,278,293-313,383; D6/APPENDIX-BINDINGS.md:28,241,425; H/HANDOFF.md:153-167.

No runtime cap, new helper Pre, warning waiver, assumption, suppressed checked assertion/Ghost code, restored Off exemption or proof-only light library is introduced. Native failure remains a failure to meet the original accepted-domain obligation, not an accepted refusal. Confinement/custody are not replaced by syntax/hash/Boolean claims. Evidence: P:32-34,64-66; H/HANDOFF.md:129-131,137,161; D4/APPENDIX-COST-MAP.md:11-19,453-482; D6/DESIGN.md:281,294-308.

The author process records are model output, recorded as stated. The indirect transcript path to other-lane summaries and the sketch self-execution are disclosed. They provide no evidence for the closures here. L16 was independently checked against the named source draft and sealed seam v2 finding. Neither the seam v3 review nor integration order is adjudicated. Evidence: D6/DESIGN.md:222-246,319-324; D6/AUTHOR-NOTES.md:99-106; WT/deviations/capi-v6-author-process/NOTE.md:24-44.

## Current rulings

The original ruling identifiers, owners and evidence requirements are retained. The historical v5 ruling objects remain exact in checks.json. This table supplies the current v6 disposition, including the explicit RC4-linked closures. The inherited evidence requirements are not erased merely because a design finding is closed.

| ID | Current ruling | Owner | Evidence still required | File:line evidence |
|---|---|---|---|---|
| RC1 | CLOSED_AT_DESIGN_LEVEL preserved | lead | Installed legality, complete diagnostic state/control/value proof and matching behavior evidence | D3/DESIGN.md:356-400,599-642; D5/DESIGN.md:61 |
| RC2 | CLOSED_AT_DESIGN_LEVEL preserved | lead | Full initialized/total value-body proof and native evidence; allocation retained; no Captured read/pass on Operations 0/1 | D3/DESIGN.md:729-749; D5/DESIGN.md:62 |
| RC3 | CLOSED_AT_DESIGN_LEVEL for N-01 resolution discipline preserved | lead | Strict warning/proof and ABI-preserving repair evidence | D3/DESIGN.md:2012-2052; D5/DESIGN.md:63 |
| LD1 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL preserved | lead | Preserve original contracts, full body/caller/ABI/native accepted-domain and control obligations; no source/proof/phase acceptance | D3/DESIGN.md:113-125 |
| LD2 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL preserved | lead | Preserve original contracts, full body/caller/ABI/native accepted-domain and control obligations; no source/proof/phase acceptance | D3/DESIGN.md:127-138 |
| LD3 | CONDITIONALLY_ACCEPTABLE_PENDING_D-13 preserved | lead; operator for material component architecture | Preserve original contracts, full body/caller/ABI/native accepted-domain and control obligations; no source/proof/phase acceptance | D3/DESIGN.md:140-149 |
| LD4 | WITHDRAWN preserved | lead | Preserve original contracts, full body/caller/ABI/native accepted-domain and control obligations; no source/proof/phase acceptance | D3/DESIGN.md:151-168 |
| LD4-R | CLOSED_AT_DESIGN_LEVEL for RC1 preserved | lead | Preserve original contracts, full body/caller/ABI/native accepted-domain and control obligations; no source/proof/phase acceptance | D3/DESIGN.md:356-664 |
| LD5 | CONDITIONALLY_ACCEPTABLE preserved | lead | Preserve original contracts, full body/caller/ABI/native accepted-domain and control obligations; no source/proof/phase acceptance | D3/DESIGN.md:170-180 |
| LD6 | CONDITIONALLY_ACCEPTABLE; V3-RC5 design condition discharged preserved | lead | Preserve original contracts, full body/caller/ABI/native accepted-domain and control obligations; no source/proof/phase acceptance | D3/DESIGN.md:182-191; D4/DESIGN.md:534-629 |
| V3-RC5 | CLOSED_AT_DESIGN_LEVEL preserved | lead | Exact original behavior characterization and full matching native/behavioral controls | D4/DESIGN.md:534-629 |
| V3-RC6 | CLOSED_AT_DESIGN_LEVEL preserved | lead | Every native cost-map item and C21-a through C21-h on matching builds | D4/APPENDIX-COST-MAP.md:7-72,435-482 |
| L1-L8 | GENUINE and prior design repairs preserved; L3 installed warning UNVERIFIED; L5's separate RC4 gate specification is now CLOSED_AT_DESIGN_LEVEL | lead | Installed legality/warnings and real invariant controls without restoring earlier defects | D5/DESIGN.md:73; D4/review/gpt61-v1/REVIEW.md:105-114; D6/DESIGN.md:26-34,254-260; D6/APPENDIX-BINDINGS.md:327-334,391-411 |
| D-13 | OPERATOR_CHOICE_REQUIRED_BEFORE_PK-7; ONLY_ABI_AND_SCOPE_PRESERVING_ROUTE_ADMISSIBLE. Reservation concerns a concrete material component transport/library architecture choice, not editing pinned implementation files or recomputing effective pins. | operator for material architecture; lead prepares concrete artifacts | Both original Decide exports and profiles/layouts, every original interface unit, SPARK_Mode-only mirror correspondence, native positive/refusal controls, complete source/project/link/header/library identity, retained native body obligations and the actual operator decision. | D5/DESIGN.md:280-293; D5/decisions.json:operator_items; D3/DESIGN.md:2012-2052; D3/DESIGN.md:2248-2273; S5/protected-resource/run_service.py:117-120; H/HANDOFF.md:153-166; W/work/integrated-proof-preparation/PLAN.md:104-107; P:32-34; P:72-74 |
| N-06 | REPROVISION_UNDER_OPERATOR_CUSTODY_AT_DEPLOYMENT; mismatch refusal remains. An old-library hold supplies no consolidated-candidate acceptance. | operator | Installed/loaded matching reviewed library, protected native_sha256, operator-controlled provisioning record and mismatch refusal evidence. | D5/DESIGN.md:280-293; D5/decisions.json:operator_items; D3/DESIGN.md:2012-2052; D3/DESIGN.md:2248-2273; S5/protected-resource/run_service.py:117-120; H/HANDOFF.md:153-166; W/work/integrated-proof-preparation/PLAN.md:104-107; P:32-34; P:72-74 |
| N-01 | LEAD_OWNED_STRICT_OBLIGATION; confirming representation repairs preserve C1-C8 and satisfy E1-E6. Any nonconfirming material ABI change is separately operator-owned and grants no weakening of the original target. | lead; operator only for material ABI change | Exact representation output, installed legality, strict warning/proof evidence, matching baseline layout identity, independent ABI and actual GPT-6.1 different-author delta review. | D5/DESIGN.md:280-293; D5/decisions.json:operator_items; D3/DESIGN.md:2012-2052; D3/DESIGN.md:2248-2273; S5/protected-resource/run_service.py:117-120; H/HANDOFF.md:153-166; W/work/integrated-proof-preparation/PLAN.md:104-107; P:32-34; P:72-74 |
| D-05 | OPEN | lead; applicable original operator gates retained | Contextual proof at every original partial-decoder caller or separately reviewed non-narrowing total restructuring; no helper Pre approved | D3/DESIGN.md:247-252; D5/DESIGN.md:279 |
| D-18 | CLOSED_AT_DESIGN_LEVEL for index design; proof OPEN | lead; applicable original operator gates retained | Prove the index/caller correspondence without new length/bounds refusal; preserve mismatch typed outcome | D3/DESIGN.md:848-878 |
| D-19 | OPEN | lead; applicable original operator gates retained | Strict raw-value branch proof and no dead/unreachable-warning waiver or branch deletion | D3/DESIGN.md:880-893 |
| D-28 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL | lead; applicable original operator gates retained | Valid complete fixed local initialization and native costs | D3/DESIGN.md:895-902 |
| D-36 | OPEN for every write form | lead; applicable original operator gates retained | Matching native construction/copy/padding/exception/write-set evidence for every form | D4/APPENDIX-COST-MAP.md:435-482 |
| D-15/D-34/D-38 | OPEN | lead; applicable original operator gates retained | Matching symbol/mapping, ABI/layout and installed legality/name/overload resolution, transported-clause warnings and RM readings in context | D5/DESIGN.md:281,304-306; D6/DESIGN.md:264,289-291; D6/APPENDIX-BINDINGS.md:103,153 |
| N-03 | OPEN | lead; applicable original operator gates retained | Full strict matching-source callee/body proof; no PROVED_ROW transfer | D5/DESIGN.md:290 |
| N-04 | CLOSED_AT_DESIGN_LEVEL for Classify enrollment; implementation obligations OPEN | lead; applicable original operator gates retained | Full relevant unit/body and native evidence | D3/DESIGN.md:2556; D5/DESIGN.md:291 |
| N-05 | OPEN | lead; applicable original operator gates retained | Original exact-set static-audit assertion unchanged; no subset reinterpretation | D5/DESIGN.md:292 |
| N-07 | CLOSED_AT_DESIGN_LEVEL for pending Decide enrollments; implementation obligations OPEN | lead; applicable original operator gates retained | Full relevant unit/body/caller and native evidence | D3/DESIGN.md:2578-2587; D5/DESIGN.md:294 |
| APPENDIX_C | CLOSED_AT_DESIGN_LEVEL for exact append-only ordering/enrollment | lead; applicable original operator gates retained | Immediate packet enrollment and matching full unit/caller proof; original ordered prefix unchanged | D3/DESIGN.md:1918-1939,2478-2589 |
| R2_NINE_CONDITIONS | CLOSED_AT_DESIGN_LEVEL for the mapped design/binding specification; actual implementation, proof, native and control evidence OPEN | lead; applicable original operator gates retained | Resolve both v5 invariant findings and preserve all mapped conditions | D5/DESIGN.md:295; D5/APPENDIX-BINDINGS.md:800-841; D6/DESIGN.md:278; D6/APPENDIX-BINDINGS.md:64-70,97-109,265-267,391-411 |
| PACKET_PLAN | CLOSED_AT_DESIGN_LEVEL; linear lineage, immediate enrollment, separate representation repairs and identities-only seal preserved; execution and D-13 OPEN | lead; applicable original operator gates retained | Resolve both v5 invariant findings; retain linear lineage, immediate enrollment, separately reviewed repair packets and identities-only seal | D5/DESIGN.md:296; D3/DESIGN.md:1870-1993; D6/DESIGN.md:279; D3/DESIGN.md:1870-1993; D6/APPENDIX-BINDINGS.md:160-163 |
| ROOT_WORKER_INTEGRATION | OPEN; no ruling on the other lane or integration order | lead; applicable original operator gates retained | Re-observed reviewed residual/qualified/layout/binding tables, preserved On/ABI/API source and installed name resolution in the eventual composition | D5/DESIGN.md:332-339; RW/SEAM-DESIGN.md:1750-1830; D6/DESIGN.md:319-324 |
| OB-048 | OPEN for enlarged and pre-existing boundary | lead; applicable original operator gates retained | Actual custody, authentic producers, immutability, faithful callers and original full Phase One dependency evidence | D3/DESIGN.md:2192-2211; H/HANDOFF.md:25-29 |

## JACKAL arithmetic and consequence boundary

Every arithmetic derivation used for the reported tallies/range/matrix total was routed through JACKAL MCP sequentially. The following results carry `status=exact`, `formal=false`, lane `rat`, assurance `exact rational arithmetic (not yet checker-covered)`, evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`. They are informational about code correctness and establish no program proof.

| Quantity | Status | parsed= | Returned exact value |
|---|---|---|---|
| S5_required_proved | exact | `1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1` | 535 |
| S5_effective_contract_keys | exact | `1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1` | 169 |
| v5_rulings | exact | `1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1` | 31 |
| append_names | exact | `1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1` | 98 |
| append_final | exact | `535+98` | 633 |
| promise_matrix | exact | `42+2` | 44 |
| append_start | exact | `535+1` | 536 |

The original prefix tally is 535, the carried append tally is 98, and `parsed=535+98` returns 633. `parsed=535+1` returns the first appended index 536. The effective S5 key tally returns 169. The carried ruling tally returns 31. `parsed=42+2` returns the B11 matrix total 44. These are arithmetic facts under the declared status; equality of counts is not equality of scope.

**non_claims, verbatim for every call:**

- NOT formal-bounded: this lane carries no Lean-checked certificate
- The epistemic class above is the STRONGEST claim this result supports
- exact rational arithmetic (not yet checker-covered)

The complete MCP structured results are retained in checks.json. The JACKAL recall ledger is not cited as evidence.

## Remaining obligations

The original target is fixed. These obligations are carried rather than converted into required design edits or claimed closed:

- **IMPLEMENTATION_AND_STAGE_REVIEWS: OPEN.** Implement the successor and real manifest override on the exact reviewed lineage; regenerate effective pins and full inventories; qualify every stage and real negative and unchanged-stage positive control. B8 text/AST inspection supplies no control-run evidence. Evidence: D6/DESIGN.md:288,297-300,312-313; D3/DESIGN.md:1870-1993; H/HANDOFF.md:153-166.
- **D-38_AND_RM_APPLICATION: OPEN.** Installed legality, integrated names and overloads, child-unit capture, transported-clause warnings, External state and Image legality; application of the cited RM visibility rules to the complete installed candidate. Evidence: D6/DESIGN.md:264,289-291; D6/APPENDIX-BINDINGS.md:103,153.
- **FULL_STRICT_PROOF: OPEN.** The unchanged strict command, sole worldline-c_api boundary, protected floor, full ordered proof roster, zero unproved/justified/Assume and all intended contract/body/caller/flow/RTE/termination/native scope; no PROVED_ROW transfer. Evidence: D6/DESIGN.md:273-277,293-295; H/HANDOFF.md:155-161.
- **N-01: OPEN.** Resolve every applicable strict representation warning through confirming repairs preserving C1-C8 with all E1-E6 evidence; no relocation or operator waiver counts as resolution. Evidence: D3/DESIGN.md:2012-2052; D6/DESIGN.md:271,295.
- **D-05_D-18_D-19_D-28: OPEN.** Contextual proof for every partial decoder caller or reviewed non-narrowing total repair; index/caller proof; raw branch proof and warnings; complete local initialization and native cost evidence. Evidence: D6/DESIGN.md:262,266-269,293; D3/DESIGN.md:848-902.
- **D-15_D-34_D-36: OPEN.** Matching export/mapping/layout/calling convention and loaded-library identities; construction, copies, padding, exception and write effects for every form. Evidence: D6/DESIGN.md:264,270,302-303; D4/APPENDIX-COST-MAP.md:435-482.
- **NATIVE_FULL_DOMAIN_AND_COSTS: OPEN.** Every original native semantic/cost blocker and every A-COST C21-a through C21-h item on matching rel/chk/comp builds: runtime representability, allocation, controlled operations, primary/secondary stack and heap, actual assertions and checked Ghost code. No cap, light proof library or native failure counted as accepted refusal. Evidence: D4/APPENDIX-COST-MAP.md:453-482; H/HANDOFF.md:129-131; D6/DESIGN.md:304-305.
- **PK-0_CHARACTERIZATION: OPEN.** Original class-H failure location and copy atomicity of an in-progress write; foreign faults and violated premises receive no strengthened claim. Evidence: D6/DESIGN.md:306; D4/DESIGN.md:534-629.
- **FULL_CONTROLS: OPEN.** Complete original ordered ordinary roster, lifetime and additive controls, genuine provider/owner/root/task/child positives, and all applicable fault campaigns on the matching integrated candidate. Evidence: D6/DESIGN.md:307; H/HANDOFF.md:162-164.
- **N-03_N-04_N-07: OPEN.** Full matching-source callee, body and caller proof and native evidence behind the existing enrollment design closures. Evidence: D6/DESIGN.md:273-274,277,293.
- **N-05: OPEN.** Preserve and satisfy the original exact-set static-audit assertion; no removal or subset reinterpretation. Evidence: D6/DESIGN.md:275.
- **D-13: OPEN_OPERATOR.** Concrete ABI- and scope-preserving material component transport/library architecture choice before PK-7, with both original exports, complete interface roster, mirror correspondence and native-body evidence. Evidence: D6/DESIGN.md:263,310; D3/DESIGN.md:2252-2260.
- **N-06: OPEN_OPERATOR_AT_DEPLOYMENT.** Operator-controlled native_sha256 provisioning for the actual installed/loaded reviewed library, retained mismatch refusal and a custody record. An old-library hold supplies no consolidated-candidate acceptance. Evidence: D6/DESIGN.md:276,310; D3/DESIGN.md:2262-2271; S5/protected-resource/run_service.py:117-120.
- **ROOT_WORKER_INTEGRATION: OPEN.** Independently reviewed eventual composition with re-observed residual, qualified, layout and binding tables and parent-specification/context inputs; preserved On, API/ABI and nesting scopes. Neither lane nor integration order is resolved here. Evidence: D6/DESIGN.md:319-324.
- **OB-048_AND_PHASE_ONE_DEPENDENCIES: OPEN.** Authentic producers, current custody and mapping, immutability, faithful callers and measured confinement for the enlarged and original boundary; all original Phase One requirements and dependencies remain fixed. Evidence: D6/DESIGN.md:281,308; H/HANDOFF.md:25-29,137,167; P:32-34,46.
- **REMAINING_CARRIED_D_ITEMS: OPEN_WHERE_CARRIED_OPEN.** D-01 through D-04, D-06 through D-12, D-14, D-17, D-20 through D-27, D-29 through D-33, D-35 and D-37 retain their original obligations; D-16 remains withdrawn with LD4 and replaced by LD4-R. Evidence: D6/DESIGN.md:261,265,268.
- **ORIGINAL_OPERATOR_AND_FINAL_ACCEPTANCE: OPEN.** The original material API/ABI/owner-policy, custody, architecture and publication/deployment gates, final independent exact-candidate acceptance, hosted assurance and applicable production/release/installation authorization. This verdict creates no additional approval requirement for pinned implementation files. Evidence: D6/DESIGN.md:263,271,276,310; H/HANDOFF.md:153-167; P:72-74.

**Required changes:** none. **Final design verdict:** ENDORSED. **Source/proof/phase acceptance:** false.
